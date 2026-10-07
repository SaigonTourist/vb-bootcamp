#!/usr/bin/env python3
"""
vg: video generation through OpenRouter for Claude Code on the web.

Standard library only, so nothing has to be installed in the cloud environment.

  vg.py models [--live]                    model call templates on disk, or checked against OpenRouter
  vg.py show h3                            call template, limits and gotchas for one model
  vg.py estimate h3 --dur 8 [--refs 2]     cost before spending
  vg.py lint h3 --prompt-file p.md         prompt check, never blocks
  vg.py submit h3 --prompt-file p.md --dur 8 [--first-frame img] [--slot templates/A_teaser/s3] [--yes]
  vg.py wait [--max-minutes 9]             poll every pending job, download, place, publish
  vg.py status | spend                     the ledger
  vg.py image --prompt "..." --out input/refs/presenter.png [--in ref.jpg]
  vg.py publish out/clip.mp4               signed link that plays in the browser
  vg.py gallery                            one page with every clip, signed link
  vg.py wall [--label s2 | --job ID]       package the latest landed clip for the Bootcamp wall (wall/outbox/)
  vg.py doctor                             environment check, prints status only, never secrets

Environment: OPENROUTER_API_KEY (or a managed credential for openrouter.ai in the cloud), VG_USER, VG_CONFIRM_EUR (3), VG_BUDGET_EUR (60), VG_USD_EUR (0.90),
VG_MOCK=1 (no network, no cost), VG_S3_ENDPOINT / VG_S3_BUCKET / VG_S3_REGION / VG_S3_ACCESS_KEY /
VG_S3_SECRET_KEY / VG_S3_PREFIX for the bucket, VG_LINK_DAYS (7).
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import hmac
import html
import json
import mimetypes
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
MODELS = SKILL / "models"
ASSETS = SKILL / "assets"
BASE = "https://openrouter.ai/api/v1"


def repo_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    for p in [SKILL, *SKILL.parents]:
        if (p / ".git").exists():
            return p
    return SKILL.parents[2]


REPO = repo_root()
OUT = REPO / "out"


def env_float(name, default):
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return float(default)


USD_EUR = env_float("VG_USD_EUR", 0.90)
CONFIRM_EUR = env_float("VG_CONFIRM_EUR", 3)
BUDGET_EUR = env_float("VG_BUDGET_EUR", 60)
MOCK = os.environ.get("VG_MOCK") == "1"
USER = re.sub(r"[^A-Za-z0-9_-]", "_", os.environ.get("VG_USER") or os.environ.get("USER") or "designer")
# one ledger per participant, so a rehearsal or the reserve renders never count against anyone
LEDGER = Path(os.environ["VG_LEDGER"]) if os.environ.get("VG_LEDGER") else REPO / "jobs" / f"{USER}.jsonl"


def die(msg, code=1):
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------- models

def load_model(name: str) -> dict:
    for f in sorted(MODELS.glob("*.json")):
        m = json.loads(f.read_text())
        if name in (m["key"], m["id"]):
            return m
    keys = ", ".join(json.loads(f.read_text())["key"] for f in sorted(MODELS.glob("*.json")))
    die(f"unknown model '{name}'. Available: {keys}")


def all_models():
    return [json.loads(f.read_text()) for f in sorted(MODELS.glob("*.json"))]


# ---------------------------------------------------------------- cost

def estimate_usd(m: dict, dur=None, resolution=None, audio=True, nrefs=0, ratio=None) -> float:
    p = m["pricing"]
    if m["key"] == "image":
        return p["usd_per_image"]
    dur = dur or m["defaults"]["duration"]
    if "usd_per_token" in p:
        res = resolution or m["defaults"].get("resolution", "720p")
        ratio = ratio or m["defaults"]["aspect_ratio"]
        w, h = m["sizes"][res][ratio]
        return w * h * 24 * dur / 1024 * p["usd_per_token"]
    per = p["usd_per_second"]
    if isinstance(per, dict):
        res = resolution or m["defaults"].get("resolution")
        base = "audio" if audio else "no_audio"
        per = per.get(f"{base}_{res}", per[base])
    usd = per * dur
    usd += nrefs * p.get("usd_per_reference_image", 0)
    return usd


def eur(usd: float) -> float:
    return usd * USD_EUR


def fmt_money(usd: float) -> str:
    return f"{eur(usd):.2f} € (≈ {usd:.2f} $)"


# ---------------------------------------------------------------- lint

NEG = re.compile(r"\b(no|not|never|don't|do not|without|avoid|nothing|none|nobody|kein\w*|nicht|nie)\b", re.I)
BRANDS = re.compile(
    r"\b(sony|canon|nikon|arri|red komodo|blackmagic|leica|apple|iphone|ipad|macbook|samsung|google|"
    r"microsoft|nike|adidas|puma|ralph lauren|lacoste|hugo boss|zara|h&m|coca[- ]cola|starbucks|"
    r"volksbank|raiffeisen|sparkasse|vr[- ]bank|deutsche bank|commerzbank|visa|mastercard|paypal)\b", re.I)
TEXT_SURFACES = re.compile(
    r"\b(screens?|monitors?|displays?|laptop screen|phone screen|smartphone|tablet|notebook|whiteboard|"
    r"flip ?chart|calculator|posters?|signs?|signage|documents?|contracts?|forms?|letters?|book covers?|"
    r"labels?|newspapers?|presentation slides?|presentation|charts?|graphs?|spreadsheets?|bildschirm\w*|tafel|vertrag|"
    r"formular|dokument\w*|plakat\w*|schild\w*)\b", re.I)
VAGUE = re.compile(r"\b(cinematic|beautiful|stunning|epic|amazing|bright|vibrant|high quality|masterpiece|8k|4k)\b", re.I)
ABSTRACT = re.compile(r"\b(trust|trustworthy|confidence|success|successful|innovation|innovative|quality|security|"
                      r"safety|growth|future|values|professionalism|empathy|reliability|excellence|vertrauen|"
                      r"sicherheit|erfolg|zukunft|kompetenz|qualität|innovation|wertschätzung|zuverlässigkeit)\b", re.I)
LAUGH = re.compile(r"\blaugh\w*|lach\w*", re.I)
EDIT_VERBS = re.compile(r"\b(add|adds|remove|removes|replace|replaces|modify|extend|extends|continue|continues)\b", re.I)
CONTINUITY = re.compile(r"\b(same as before|as before|previous shot|last shot|like before|wie vorher|again)\b", re.I)
CLOSE = re.compile(r"\b(extreme close[- ]?up|close[- ]?up|closeup|macro)\b", re.I)
FACE = re.compile(r"\b(face|faces|eyes|smile|presenter|woman|man|person|speaker|gesicht)\b", re.I)
MONTHS = (r"januar|februar|märz|maerz|april|mai|juni|juli|august|september|oktober|november|dezember|"
          r"january|february|march|may|june|july|october|december")
# A bare weekday ("ab Montag") is true every week and stays allowed; "bis Freitag" is a deadline.
PERISHABLE = re.compile(r"(\d|%|€|\beuro\b|\bprozent\b|\bheute\b|\bmorgen\b|\bdiese woche\b|\bbis (?:\w+tag|mittwoch|ende|zum)\b|\buntil \w+day\b|\b(" + MONTHS + r")\b)", re.I)


def dialogue_of(prompt: str) -> str:
    m = re.search(r"(?i:dialogue)\s*:\s*(.+?)(?:\n\s*\n|\n\s*[A-Z][A-Z ]+:|\Z)", prompt, re.S)
    if m:
        section = m.group(1).strip()
        said = re.findall(r'[„"“](.+?)["“”]', section)
        # 'The man says in German: "..."' -> only the quoted words are spoken
        return " ".join(said) if said else section
    quoted = re.findall(r"[„\"“](.+?)[\"“”]", prompt)
    return " ".join(quoted)


def lint(m: dict, prompt: str, dur=None) -> list:
    """List of (level, code, message). Levels: warn, info. Never blocks a submit."""
    out = []
    words = prompt.split()
    n = len(words)
    key = m["key"]
    if n > 180:
        out.append(("warn", "LONG", f"{n} words. Long prompts bury the action; keep it under ~150 and lead with what happens."))
    a = re.search(r"\baction\s*:", prompt, re.I)
    if a and len(prompt[:a.start()].split()) > 60:
        out.append(("warn", "ACTION_LATE", f"ACTION starts at word {len(prompt[:a.start()].split())}. Move it into the first two sentences."))
    negs = NEG.findall(prompt)
    if len(negs) > 3:
        out.append(("warn", "NEGATIONS", f"{len(negs)} negations. The model draws what you name, including what you forbid. Say what IS there."))
    for b in sorted({x.lower() for x in BRANDS.findall(prompt)}):
        out.append(("warn", "BRAND", f"'{b}' named. It will be drawn, logos included. Describe it without the name; put real logos in the edit."))
    spoken = dialogue_of(prompt)
    visual = prompt.replace(spoken, " ") if spoken else prompt  # spoken words are not drawn
    surf = sorted({x.lower() for x in TEXT_SURFACES.findall(visual)})
    if surf:
        out.append(("warn", "TEXT_SURFACE", f"{', '.join(surf)}: models invent letters on anything readable. Turn it away, keep it blurred, add real text in the edit."))
    abstract = sorted({x.lower() for x in ABSTRACT.findall(visual)})
    if abstract:
        out.append(("info", "ABSTRACT", f"{', '.join(abstract)}: an idea, not something a camera sees. Name the small physical "
                                        "action that makes a viewer feel it (see reference/idea_to_prompt.md)."))
    vague = sorted({x.lower() for x in VAGUE.findall(prompt)})
    if vague:
        out.append(("info", "VAGUE", f"{', '.join(vague)}: says nothing executable. Name the lens, the distance, one light source and its direction."))
    if LAUGH.search(prompt):
        out.append(("warn", "LAUGH", "Acted laughter looks uncomfortable. Direct a smile or a short smirk."))
    if key in ("veo", "veo-fast"):
        if not re.search(r"^\s*shot\s*:", prompt, re.I | re.M):
            out.append(("warn", "NO_SHOT", "No SHOT: line. Veo picks the framing itself and tends to push in on faces."))
        if CLOSE.search(prompt) and FACE.search(prompt):
            out.append(("warn", "FACE_CLOSEUP", "Close-up on a face. Energetic close-ups drift into grimaces; medium shot or wider."))
    if key == "seedance":
        if EDIT_VERBS.search(prompt):
            out.append(("warn", "TASK_TYPE", f"'{EDIT_VERBS.search(prompt).group(0)}' makes Seedance treat this as an edit job (TaskTypeConstraint). Rephrase."))
        if FACE.search(prompt) and CLOSE.search(prompt):
            out.append(("info", "FACE", "Seedance is the b-roll model here. Faces in close-up belong on H3."))
    if CONTINUITY.search(prompt):
        out.append(("warn", "CONTINUITY", "No model remembers another shot. Restate the full blocking instead of 'as before'."))
    if spoken:
        hits = sorted({h if isinstance(h, str) else h[0] for h in PERISHABLE.findall(spoken)})
        if hits:
            out.append(("warn", "PERISHABLE", f"Spoken {', '.join(hits)}. Dates, prices, numbers and deadlines go on screen as text; spoken, they force a re-render every time they change."))
        if dur and key in ("h3", "veo", "veo-fast"):
            sw = len(spoken.split())
            if sw > 2.3 * max(dur - 0.8, 1):
                out.append(("warn", "TOO_MANY_WORDS", f"{sw} spoken words in {dur} s. German at a natural pace is about 2 words per second; cut or lengthen."))
            elif sw < 1.0 * dur and key == "h3":
                out.append(("info", "FEW_WORDS", f"{sw} words in {dur} s. H3 fills silence by repeating words; end with a short filler line you cut later."))
    return out


def print_lint(items):
    if not items:
        print("  lint: clean")
    for level, code, msg in items:
        mark = "⚠" if level == "warn" else "·"
        print(f"  {mark} {code}: {msg}")


# ---------------------------------------------------------------- http

def api_key() -> str:
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def http(method, url, body=None, headers=None, timeout=120, raw=False):
    data = None
    h = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode()
        h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = r.read()
            return payload if raw else json.loads(payload or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        raise RuntimeError(f"HTTP {e.code} from {urllib.parse.urlparse(url).netloc}: {detail}") from None


def or_headers():
    """With OPENROUTER_API_KEY in the environment, send it. Without it, send nothing: in Claude Code on
    the web a managed credential for openrouter.ai makes the proxy add the header, and the key never
    enters the container. A 401 then means no credential is configured."""
    k = api_key()
    return {"Authorization": f"Bearer {k}"} if k else {}


def sniff_mime(raw: bytes, name: str) -> str:
    """The bytes decide, not the extension: image models may return JPEG for a file we named .png."""
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if raw[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    if raw[4:8] == b"ftyp":
        return "video/mp4"
    return mimetypes.guess_type(name)[0] or "application/octet-stream"


def data_url(p: Path) -> str:
    p = Path(p)
    if not p.exists():
        die(f"file not found: {p}")
    raw = p.read_bytes()
    return f"data:{sniff_mime(raw, str(p))};base64," + base64.b64encode(raw).decode()


def download(url, dest: Path, auth=True):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=or_headers() if auth else {})
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    return dest


# ---------------------------------------------------------------- body

def build_body(m, prompt, dur=None, ratio=None, resolution=None, audio=None, seed=None,
               first_frame=None, last_frame=None, refs=(), ref_videos=(), negative=None) -> dict:
    lim, d = m["limits"], m["defaults"]
    dur = int(dur or d["duration"])
    ratio = ratio or d["aspect_ratio"]
    if dur not in lim["durations"]:
        die(f"{m['name']} accepts durations {lim['durations']}, not {dur}.")
    if ratio not in lim["ratios"]:
        die(f"{m['name']} accepts ratios {lim['ratios']}, not {ratio}.")
    body = {"model": m["id"], "prompt": prompt, "duration": dur, "aspect_ratio": ratio,
            "generate_audio": d.get("generate_audio", True) if audio is None else bool(audio)}
    res = resolution or d.get("resolution")
    if res:
        if res not in lim["resolutions"]:
            die(f"{m['name']} accepts resolutions {lim['resolutions']}, not {res}.")
        if lim["resolutions"] != ["2K"]:
            body["resolution"] = res
    if seed is not None:
        if lim.get("seed"):
            body["seed"] = int(seed)
        else:
            print(f"  · {m['name']} has no seed; ignoring --seed")
    refs, ref_videos = list(refs), list(ref_videos)
    if (refs or ref_videos) and lim["refs"] == "none":
        die(f"{m['name']} takes no reference images through OpenRouter. Use --first-frame instead.")
    if ref_videos and "video" not in lim["refs"]:
        die(f"{m['name']} ignores reference videos.")
    if len(refs) + len(ref_videos) > lim.get("max_refs", 0) and lim["refs"] != "none":
        die(f"{m['name']} takes at most {lim['max_refs']} references.")
    inputs = [{"type": "image_url", "image_url": {"url": data_url(r)}} for r in refs]
    inputs += [{"type": "video_url", "video_url": {"url": data_url(r)}} for r in ref_videos]
    frames = []
    if first_frame:
        frames.append({"type": "image_url", "frame_type": "first_frame", "image_url": {"url": data_url(first_frame)}})
    if last_frame:
        frames.append({"type": "image_url", "frame_type": "last_frame", "image_url": {"url": data_url(last_frame)}})
    if frames:
        body["frame_images"] = frames
        if inputs:
            print("  ⚠ frame_images wins over references: the references will be ignored by the provider.")
    if inputs:
        body["input_references"] = inputs
    if negative and "negativePrompt" in m.get("passthrough", []):
        body["negativePrompt"] = negative
    return body


def redacted(body: dict) -> dict:
    s = json.dumps(body)
    s = re.sub(r"data:([\w/+.-]+);base64,[A-Za-z0-9+/=]+", lambda x: f"data:{x.group(1)};base64,<{len(x.group(0)) // 1024} KB>", s)
    return json.loads(s)


# ---------------------------------------------------------------- ledger

def ledger_append(rec: dict):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    rec = {"t": dt.datetime.now().isoformat(timespec="seconds"), **rec}
    with open(LEDGER, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def jobs() -> dict:
    state = {}
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                state.setdefault(r["id"], {}).update(r)
    return state


def spent_usd(state=None) -> float:
    total = 0.0
    for j in (state or jobs()).values():
        if j.get("status") == "failed":
            continue
        cost = j.get("cost_usd")
        total += float(cost) if cost is not None else float(j.get("estimate_usd", 0))
    return total


# ---------------------------------------------------------------- slots

def slot_target(slot: str | None) -> Path | None:
    """templates/A_teaser/s3 -> templates/A_teaser/slots/s3.mp4"""
    if not slot:
        return None
    p = Path(slot)
    if p.suffix == ".mp4":
        return REPO / p
    return REPO / p.parent / "slots" / f"{p.name}.mp4"


def mock_clip() -> Path:
    clip = ASSETS / "mock.mp4"
    if not clip.exists():
        die(f"mock clip missing at {clip}")
    return clip


# ---------------------------------------------------------------- commands

def read_prompt(a) -> str:
    if getattr(a, "prompt_file", None):
        return Path(a.prompt_file).read_text().strip()
    if getattr(a, "prompt", None):
        return a.prompt.strip()
    die("give --prompt or --prompt-file")


def cmd_models(a):
    for m in all_models():
        lim = m["limits"]
        durs = lim.get("durations")
        span = f"{durs[0]}-{durs[-1]} s" if durs else "image"
        print(f"  {m['key']:9} {m['id']:36} {span:9} {','.join(lim['ratios'][:3]):18} {m['role']}")
    if a.live:
        live = {x["id"]: x for x in http("GET", f"{BASE}/videos/models", headers=or_headers())["data"]}
        print()
        for m in all_models():
            if m["key"] == "image":
                continue
            x = live.get(m["id"])
            if not x:
                print(f"  ✗ {m['id']} is no longer listed by OpenRouter")
                continue
            issues = []
            if sorted(x.get("supported_durations") or []) != sorted(m["limits"]["durations"]):
                issues.append(f"durations now {x.get('supported_durations')}")
            if sorted(x.get("supported_aspect_ratios") or []) != sorted(m["limits"]["ratios"]):
                issues.append(f"ratios now {x.get('supported_aspect_ratios')}")
            print(f"  {'✓' if not issues else '⚠'} {m['id']} {'; '.join(issues) or 'matches models/' + m['key'] + '.json'} · pricing {x.get('pricing_skus')}")


def cmd_show(a):
    m = load_model(a.model)
    print(json.dumps({k: m[k] for k in ("id", "role", "limits", "defaults", "pricing", "example_call", "gotchas") if k in m},
                     indent=2, ensure_ascii=False))
    for t in m.get("prompt_templates", []):
        print(f"\n  prompt template: {SKILL / 'prompts' / t}")


def cmd_estimate(a):
    m = load_model(a.model)
    usd = estimate_usd(m, a.dur, a.resolution, not a.no_audio, a.refs, a.ratio)
    lo, hi = m.get("render_minutes", [0, 0])
    print(f"  {m['name']} · {a.dur or m['defaults'].get('duration', '')} s · {fmt_money(usd)} · renders in {lo}-{hi} min")


def cmd_lint(a):
    m = load_model(a.model)
    print_lint(lint(m, read_prompt(a), a.dur))


def budget_check(usd, force=False):
    spent = spent_usd()
    if eur(spent + usd) > BUDGET_EUR and not force:
        die(f"this would take the session to {eur(spent + usd):.2f} € of a {BUDGET_EUR:.0f} € budget. Ask the facilitator.")
    return spent


ENGINE_FAMILY = {"veo-fast": "veo"}  # drafting a Veo slot on Veo Fast is part of the method


def slot_engine(slot: str | None):
    """(template slot id, engine the shotlist fixes for it), or (None, None) when not a template slot."""
    target = slot_target(slot)
    if not target or target.parent.name != "slots":
        return None, None
    shotlist = target.parent.parent / "shotlist.json"
    if not shotlist.exists():
        return None, None
    for s in json.loads(shotlist.read_text())["slots"]:
        if s["id"] == target.stem:
            return s["id"], s.get("model")
    return None, None


def cmd_submit(a):
    m = load_model(a.model)
    if m["key"] == "image":
        die("use 'vg.py image' for start frames")
    sid, fixed = slot_engine(a.slot)
    if fixed and ENGINE_FAMILY.get(m["key"], m["key"]) != fixed and not a.change_engine:
        die(f"slot {sid} is a {load_model(fixed)['name']} slot in its shotlist, not {m['name']}. The engines are fixed "
            f"so the takes can be compared. Use {fixed}"
            + (" (or veo-fast for a draft)" if fixed == "veo" else "")
            + ". Only if the designer explicitly asks for another engine: add --change-engine and say so.")
    prompt = read_prompt(a)
    body = build_body(m, prompt, a.dur, a.ratio, a.resolution, None if not a.no_audio else False, a.seed,
                      a.first_frame, a.last_frame, a.ref, a.ref_video, a.negative)
    nrefs = len(a.ref) if not (a.first_frame or a.last_frame) else 0
    usd = estimate_usd(m, body["duration"], body.get("resolution"), body["generate_audio"], nrefs, body["aspect_ratio"])
    print(f"  {m['name']} · {body['duration']} s · {body['aspect_ratio']} · estimate {fmt_money(usd)}")
    findings = lint(m, prompt, body["duration"])
    if a.raw:
        print("  raw mode: sent exactly as typed, no rewrite. Findings are kept for after the clip lands.")
    else:
        print_lint(findings)
    spent = budget_check(usd, a.over_budget)
    if a.dry_run:
        print(json.dumps(redacted(body), indent=2, ensure_ascii=False))
        print(f"  dry run: nothing sent. Session spend so far {eur(spent):.2f} €.")
        return
    if eur(usd) > CONFIRM_EUR and not a.yes:
        print(f"  ✋ {eur(usd):.2f} € is above the {CONFIRM_EUR:.0f} € confirmation line. Ask the designer, then repeat with --yes.")
        sys.exit(3)
    target = slot_target(a.slot)
    label = a.label or (Path(a.slot).name if a.slot else m["key"])
    if MOCK:
        jid = f"mock-{int(time.time() * 1000)}"
        status = "pending"
    else:
        r = http("POST", f"{BASE}/videos", body=body, headers=or_headers())
        jid, status = r["id"], r.get("status", "pending")
    ledger_append({"id": jid, "kind": "video", "user": USER, "model": m["id"], "key": m["key"], "label": label,
                   "slot": str(target.relative_to(REPO)) if target else None, "duration": body["duration"],
                   "ratio": body["aspect_ratio"], "prompt": prompt, "estimate_usd": round(usd, 4),
                   "status": status, "mock": MOCK, "submitted": time.time(), "mode": "raw" if a.raw else "assisted",
                   "lint": [[lvl, code, msg] for lvl, code, msg in findings]})
    lo, hi = m.get("render_minutes", [0, 0])
    print(f"  → job {jid} queued ({lo}-{hi} min). Run 'vg.py wait' to collect it; keep working meanwhile.")


def finish(j: dict, src: Path | None = None, url: str | None = None, cost=None):
    name = f"{j['label']}_{j['id'][-8:]}.mp4"
    dest = OUT / name
    if src:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    else:
        download(url, dest)
    placed, take = None, None
    if j.get("slot"):
        placed = REPO / j["slot"]
        placed.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(dest, placed)
        if placed.parent.name == "slots":
            # every render of a template slot is kept as a take, so the designer can compare and choose
            takes = placed.parent.parent / "takes"
            takes.mkdir(exist_ok=True)
            n = len(list(takes.glob(f"{placed.stem}_t*.mp4"))) + 1
            take = takes / f"{placed.stem}_t{n}.mp4"
            shutil.copyfile(dest, take)
            take.with_suffix(".txt").write_text(j.get("prompt", ""))
            placed.with_suffix(".take").write_text(f"t{n}")
    link = publish(dest) if s3_ready() else None
    took = time.time() - j.get("submitted", time.time())
    upd = {"id": j["id"], "status": "completed", "file": str(dest.relative_to(REPO)), "link": link,
           "seconds": round(took)}
    if cost is not None:
        upd["cost_usd"] = float(cost)
    ledger_append(upd)
    cost_txt = fmt_money(float(cost)) if cost is not None else "cost pending"
    print(f"  ✓ {j['label']} · {dest.relative_to(REPO)} · {took / 60:.1f} min · {cost_txt}")
    if placed:
        print(f"    placed in {placed.relative_to(REPO)}" + (f" (take {take.stem.rsplit('_t', 1)[1]}, kept in takes/)" if take else ""))
    if link:
        print(f"    watch: {link}")
    if wall_url():
        print(f"    wall: run 'vg.py wall --label {j['label']}' and post it (SKILL.md, Bootcamp wall)")


def cmd_wait(a):
    deadline = time.time() + a.max_minutes * 60
    while True:
        pending = [j for j in jobs().values() if j.get("kind") == "video" and j.get("status") not in ("completed", "failed")
                   and (not a.job or j["id"] == a.job)]
        if not pending:
            print("  nothing pending.")
            return
        for j in pending:
            if j.get("mock"):
                finish(j, src=mock_clip(), cost=0.0)
                continue
            try:
                s = http("GET", f"{BASE}/videos/{j['id']}", headers=or_headers(), timeout=60)
            except RuntimeError as e:
                print(f"  · {j['label']}: poll error, retrying ({e})")
                continue
            st = s.get("status")
            if st == "completed":
                urls = s.get("unsigned_urls") or []
                if not urls:
                    print(f"  · {j['label']}: completed without a download url yet")
                    continue
                finish(j, url=urls[0], cost=(s.get("usage") or {}).get("cost"))
            elif st == "failed":
                err = json.dumps(s.get("error") or s)[:400]
                ledger_append({"id": j["id"], "status": "failed", "error": err})
                print(f"  ✗ {j['label']} failed: {err}")
            elif st != j.get("status"):
                ledger_append({"id": j["id"], "status": st})
        left = [j for j in jobs().values() if j.get("kind") == "video" and j.get("status") not in ("completed", "failed")
                and (not a.job or j["id"] == a.job)]
        if not left:
            return
        if time.time() > deadline:
            names = ", ".join(f"{j['label']} ({(time.time() - j.get('submitted', time.time())) / 60:.0f} min)" for j in left)
            print(f"  … still rendering: {names}. Run 'vg.py wait' again.")
            return
        time.sleep(a.every)


def cmd_status(a):
    state = jobs()
    if not state:
        print("  ledger is empty.")
        return
    for j in state.values():
        cost = j.get("cost_usd", j.get("estimate_usd", 0))
        tag = "" if "cost_usd" in j else " est."
        print(f"  {j.get('status', '?'):11} {j.get('key', ''):9} {j.get('label', ''):18} {eur(float(cost)):6.2f} €{tag:5} "
              f"{j.get('file') or j['id']}")
    print(f"  session total {eur(spent_usd(state)):.2f} € of {BUDGET_EUR:.0f} €")


def cmd_sent(a):
    """What was really sent for a clip: shown after every delivery so the designer sees the final format."""
    vids = [j for j in jobs().values() if j.get("kind") == "video"]
    if a.job:
        vids = [j for j in vids if j["id"] == a.job]
    elif a.label:
        vids = [j for j in vids if j.get("label") == a.label]
    if not vids:
        die("no matching generation in this session's ledger")
    j = sorted(vids, key=lambda x: x.get("submitted", 0))[-1]
    print(f"  {j.get('label')} · {j.get('model')} · {j.get('duration')} s · mode {j.get('mode', 'assisted')} · {j.get('status')}")
    print("  --- prompt sent ---")
    print("\n".join("  " + line for line in j.get("prompt", "").splitlines()))
    findings = j.get("lint") or []
    print("  --- what the method would flag ---" if findings else "  --- lint: clean ---")
    for lvl, code, msg in findings:
        print(f"  {'⚠' if lvl == 'warn' else '·'} {code}: {msg}")


# ---------------------------------------------------------------- bootcamp wall

WALL_CFG = SKILL / "wall.json"
WALL_DIR = REPO / "wall"
WALL_MAX_BYTES = 19 * 1024 * 1024  # the wall's asset store takes 20 MiB per file


def wall_url() -> str | None:
    url = os.environ.get("VG_WALL_URL")
    if not url and WALL_CFG.exists():
        url = json.loads(WALL_CFG.read_text()).get("url")
    return url or None


def ffmpeg_exe() -> str | None:
    ff = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if not ff and (Path.home() / ".local" / "bin" / "ffmpeg").exists():
        ff = str(Path.home() / ".local" / "bin" / "ffmpeg")
    return ff


def wall_package(j: dict, note: str = "") -> dict:
    """A small mp4, a poster and the post row for one landed clip, in wall/outbox/. Never touches the network."""
    import subprocess
    src = REPO / j["file"]
    if not src.exists():
        die(f"{j['file']} is not in this session any more")
    stem = f"{USER}_{j.get('label', 'clip')}_{j['id'][-8:]}"
    box = WALL_DIR / "outbox"
    box.mkdir(parents=True, exist_ok=True)
    clip, poster = box / f"{stem}.mp4", box / f"{stem}.jpg"
    ff = ffmpeg_exe()
    if ff:
        # long side 1280, h264 + aac, faststart: plays at once in every browser and stays far below the cap
        scale = "scale='if(gt(iw,ih),min(1280,iw),-2)':'if(gt(iw,ih),-2,min(1280,ih))'"
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(src), "-vf", scale, "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                        str(clip)], check=True)
        subprocess.run([ff, "-y", "-loglevel", "error", "-ss", "1", "-i", str(src), "-frames:v", "1", "-vf", "scale=640:-2",
                        "-q:v", "4", str(poster)], check=False)
    else:
        shutil.copyfile(src, clip)
    if clip.stat().st_size > WALL_MAX_BYTES:
        die(f"{clip.name} is {clip.stat().st_size / 1e6:.1f} MB, above the wall's 20 MB per clip")
    slot = j.get("slot") or ""
    parts = Path(slot).parts
    template = parts[1] if len(parts) > 1 and parts[0] == "templates" else ""
    cost = j.get("cost_usd", j.get("estimate_usd"))
    row = {
        "author": USER, "label": j.get("label", ""), "template": template, "slot": Path(slot).stem if slot else "",
        "engine": j.get("key", ""), "model": j.get("model", ""), "mode": j.get("mode", "assisted"),
        "duration": j.get("duration"), "ratio": j.get("ratio", ""),
        "cost_eur": round(eur(float(cost)), 2) if cost is not None else None,
        "render_s": j.get("seconds"), "prompt": j.get("prompt", ""),
        "lint": [{"level": lvl, "code": code, "msg": msg} for lvl, code, msg in (j.get("lint") or [])],
        "note": note, "job": j["id"], "created": int(time.time() * 1000), "source": "session",
        "asset": None, "poster": None,
    }
    (box / f"{stem}.json").write_text(json.dumps(row, ensure_ascii=False, indent=2))
    return {"stem": stem, "clip": clip, "poster": poster if poster.exists() else None, "row": box / f"{stem}.json"}


def cmd_wall(a):
    """Package a landed clip for the wall and print the two steps that post it from this session."""
    vids = [j for j in jobs().values() if j.get("kind") == "video" and j.get("status") == "completed" and j.get("file")]
    if a.job:
        vids = [j for j in vids if j["id"] == a.job]
    elif a.label:
        vids = [j for j in vids if j.get("label") == a.label]
    if not vids:
        die("no landed clip matches in this session's ledger")
    j = sorted(vids, key=lambda x: x.get("submitted", 0))[-1]
    pk = wall_package(j, a.note or "")
    url = wall_url()
    rel = lambda p: str(p.relative_to(REPO))  # noqa: E731
    print(f"  wall package ready: {rel(pk['clip'])} ({pk['clip'].stat().st_size / 1e6:.1f} MB)"
          + (f", poster {rel(pk['poster'])}" if pk["poster"] else ""))
    print(f"  post row: {rel(pk['row'])}")
    if not url:
        print("  · no wall configured (wall.json or VG_WALL_URL); the package stays in wall/outbox/.")
        return
    print(f"  wall: {url}")
    print("  to post: upload the mp4 (and the poster) to the wall's assets, put the returned ids into the row's")
    print("  'asset' and 'poster' fields, write the row to the wall's 'posts' collection with doc id = "
          f"{pk['stem']}, then run: vg.py wall --done {pk['stem']}")


def cmd_wall_done(stem: str):
    box = WALL_DIR / "outbox"
    sent = WALL_DIR / "posted"
    sent.mkdir(parents=True, exist_ok=True)
    moved = 0
    for f in box.glob(f"{stem}.*"):
        f.replace(sent / f.name)
        moved += 1
    print(f"  {stem}: marked as posted ({moved} files moved to wall/posted/)" if moved else f"  nothing in the outbox named {stem}")


def cmd_spend(a):
    state = jobs()
    by = {}
    for j in state.values():
        if j.get("status") == "failed":
            continue
        k = j.get("key", "?")
        by[k] = by.get(k, 0) + float(j.get("cost_usd", j.get("estimate_usd", 0)))
    for k, v in sorted(by.items()):
        print(f"  {k:9} {fmt_money(v)}")
    print(f"  total     {fmt_money(spent_usd(state))} · budget {BUDGET_EUR:.0f} €")


def cmd_image(a):
    m = load_model("image")
    prompt = read_prompt(a)
    usd = m["pricing"]["usd_per_image"]
    budget_check(usd, a.over_budget)
    out = REPO / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    jid = f"img-{int(time.time() * 1000)}"
    if MOCK:
        shutil.copyfile(ASSETS / "mock_frame.png", out)
        cost = 0.0
    else:
        content = [{"type": "text", "text": prompt}] + [{"type": "image_url", "image_url": {"url": data_url(p)}} for p in a.inp]
        body = {"model": m["id"], "messages": [{"role": "user", "content": content}],
                "modalities": ["image", "text"], "image_config": {"aspect_ratio": a.ratio}}
        r = http("POST", f"{BASE}/chat/completions", body=body, headers=or_headers(), timeout=300)
        msg = r["choices"][0]["message"]
        imgs = msg.get("images") or []
        if not imgs:
            die("no image came back: " + (msg.get("content") or "")[:300])
        url = imgs[0]["image_url"]["url"]
        mm = re.match(r"data:(image/\w+);base64,(.*)", url, re.S)
        if not mm:
            die("unexpected image response")
        # keep the name that was asked for: start frames are referenced by it (data_url sniffs the real type)
        out.write_bytes(base64.b64decode(mm.group(2)))
        cost = (r.get("usage") or {}).get("cost", usd)
    ledger_append({"id": jid, "kind": "image", "user": USER, "model": m["id"], "key": "image", "label": out.stem,
                   "prompt": prompt, "estimate_usd": usd, "cost_usd": float(cost), "status": "completed",
                   "file": str(out.relative_to(REPO)), "mock": MOCK})
    print(f"  ✓ {out.relative_to(REPO)} · {fmt_money(float(cost))}")


# ---------------------------------------------------------------- bucket (S3 / R2, SigV4, stdlib)

def s3_ready() -> bool:
    return all(os.environ.get(k) for k in ("VG_S3_ENDPOINT", "VG_S3_BUCKET", "VG_S3_ACCESS_KEY", "VG_S3_SECRET_KEY"))


def _hmac(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def _signing_key(secret, date, region, service="s3"):
    k = _hmac(("AWS4" + secret).encode(), date)
    k = _hmac(k, region)
    k = _hmac(k, service)
    return _hmac(k, "aws4_request")


def _q(s, safe="-_.~"):
    return urllib.parse.quote(s, safe=safe)


def presign(host, uri, access, secret, region, expires, now: dt.datetime, method="GET") -> str:
    """Query-string SigV4 for S3. `uri` is already the canonical path (/bucket/key or /key)."""
    amz = now.strftime("%Y%m%dT%H%M%SZ")
    date = now.strftime("%Y%m%d")
    scope = f"{date}/{region}/s3/aws4_request"
    params = {"X-Amz-Algorithm": "AWS4-HMAC-SHA256", "X-Amz-Credential": f"{access}/{scope}", "X-Amz-Date": amz,
              "X-Amz-Expires": str(expires), "X-Amz-SignedHeaders": "host"}
    qs = "&".join(f"{_q(k)}={_q(v)}" for k, v in sorted(params.items()))
    canonical = f"{method}\n{uri}\n{qs}\nhost:{host}\n\nhost\nUNSIGNED-PAYLOAD"
    sts = f"AWS4-HMAC-SHA256\n{amz}\n{scope}\n{hashlib.sha256(canonical.encode()).hexdigest()}"
    sig = hmac.new(_signing_key(secret, date, region), sts.encode(), hashlib.sha256).hexdigest()
    return f"{qs}&X-Amz-Signature={sig}"


def _s3():
    ep = os.environ["VG_S3_ENDPOINT"].rstrip("/")
    if "://" not in ep:
        ep = "https://" + ep
    host = urllib.parse.urlparse(ep).netloc
    return ep, host, os.environ["VG_S3_BUCKET"], os.environ.get("VG_S3_REGION", "auto"), \
        os.environ["VG_S3_ACCESS_KEY"], os.environ["VG_S3_SECRET_KEY"], os.environ.get("VG_S3_PREFIX", "volksbank")


def s3_put(path: Path, key: str, content_type=None):
    ep, host, bucket, region, access, secret, _ = _s3()
    data = Path(path).read_bytes()
    ctype = content_type or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    now = dt.datetime.now(dt.timezone.utc)
    amz, date = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y%m%d")
    uri = f"/{bucket}/{_q(key, '/-_.~')}"
    phash = hashlib.sha256(data).hexdigest()
    headers = {"content-type": ctype, "host": host, "x-amz-content-sha256": phash, "x-amz-date": amz}
    signed = ";".join(sorted(headers))
    canonical = f"PUT\n{uri}\n\n" + "".join(f"{k}:{headers[k]}\n" for k in sorted(headers)) + f"\n{signed}\n{phash}"
    scope = f"{date}/{region}/s3/aws4_request"
    sts = f"AWS4-HMAC-SHA256\n{amz}\n{scope}\n{hashlib.sha256(canonical.encode()).hexdigest()}"
    sig = hmac.new(_signing_key(secret, date, region), sts.encode(), hashlib.sha256).hexdigest()
    auth = f"AWS4-HMAC-SHA256 Credential={access}/{scope}, SignedHeaders={signed}, Signature={sig}"
    req = urllib.request.Request(ep + uri, data=data, method="PUT",
                                 headers={"Content-Type": ctype, "x-amz-content-sha256": phash, "x-amz-date": amz,
                                          "Authorization": auth})
    try:
        urllib.request.urlopen(req, timeout=300).read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"bucket upload failed: HTTP {e.code} {e.read().decode(errors='replace')[:300]}") from None
    return s3_link(key)


def s3_link(key: str) -> str:
    ep, host, bucket, region, access, secret, _ = _s3()
    days = min(int(env_float("VG_LINK_DAYS", 7)), 7)
    uri = f"/{bucket}/{_q(key, '/-_.~')}"
    qs = presign(host, uri, access, secret, region, days * 86400, dt.datetime.now(dt.timezone.utc))
    return f"{ep}{uri}?{qs}"


def publish(path: Path) -> str:
    *_, prefix = _s3()
    return s3_put(path, f"{prefix}/{USER}/{Path(path).name}")


def cmd_publish(a):
    if not s3_ready():
        die("bucket is not configured (VG_S3_* variables). See DRY_RUN.md.")
    print(f"  {publish(REPO / a.file if not Path(a.file).is_absolute() else Path(a.file))}")


def cmd_gallery(a):
    if not s3_ready():
        die("bucket is not configured (VG_S3_* variables).")
    items = []
    for j in jobs().values():
        if j.get("status") != "completed" or j.get("kind") != "video" or not j.get("file"):
            continue
        f = REPO / j["file"]
        if not f.exists():
            continue
        link = publish(f)
        cost = float(j.get("cost_usd", j.get("estimate_usd", 0)))
        items.append(f"<figure><video controls preload=metadata src=\"{html.escape(link)}\"></video>"
                     f"<figcaption><b>{html.escape(j['label'])}</b> · {html.escape(j.get('key', ''))} · "
                     f"{j.get('duration', '')} s · {eur(cost):.2f} €<details><summary>prompt</summary>"
                     f"<pre>{html.escape(j.get('prompt', ''))}</pre></details></figcaption></figure>")
    page = OUT / f"gallery_{USER}.html"
    page.write_text(GALLERY.replace("{{user}}", html.escape(USER)).replace("{{items}}", "\n".join(items) or "<p>No clips yet.</p>")
                    .replace("{{total}}", f"{eur(spent_usd()):.2f} €"))
    *_, prefix = _s3()
    print(f"  {s3_put(page, f'{prefix}/{USER}/gallery.html', 'text/html; charset=utf-8')}")


GALLERY = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Video lab · {{user}}</title><style>
:root{--bg:#f6f5f2;--fg:#1d1d1b;--mute:#6b6a66;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--fg:#eceae4;--mute:#9a988f;--card:#1f1f1d}}
body{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{max-width:1100px;margin:auto}h1{font-size:20px;margin:0 0 4px}p.m{color:var(--mute);margin:0 0 20px}
.g{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}
figure{margin:0;background:var(--card);border-radius:10px;overflow:hidden}video{width:100%;display:block;background:#000}
figcaption{padding:10px 12px;font-size:13px}pre{white-space:pre-wrap;font-size:12px;color:var(--mute)}
</style><main><h1>{{user}}</h1><p class=m>Session spend {{total}} · links expire after 7 days</p><div class=g>
{{items}}
</div></main></html>"""


# ---------------------------------------------------------------- doctor

def cmd_doctor(a):
    ok = True

    def line(good, what, hint=""):
        nonlocal ok
        ok &= bool(good)
        print(f"  {'✓' if good else '✗'} {what}{'' if good else '  → ' + hint}")

    line(sys.version_info >= (3, 8), f"python {sys.version.split()[0]}", "needs 3.8+")
    ff = ffmpeg_exe()
    line(ff, f"ffmpeg {'at ' + ff if ff else 'missing'}", "run: bash scripts/setup_cloud.sh")
    if MOCK:
        print("  · mock mode: no network, no cost")
    elif api_key():
        print("  · OpenRouter key: from the environment variable")
    else:
        print("  · OpenRouter key: none in the container; expecting a managed credential for openrouter.ai")
    print(f"  · VG_USER={USER} · confirm above {CONFIRM_EUR:.0f} € · budget {BUDGET_EUR:.0f} € · spent {eur(spent_usd()):.2f} €")
    if not MOCK:
        try:
            n = len(http("GET", f"{BASE}/videos/models", headers=or_headers(), timeout=30)["data"])
            line(True, f"openrouter.ai reachable ({n} video models)")
        except Exception as e:  # noqa: BLE001
            line(False, "openrouter.ai reachable", f"add openrouter.ai to the environment's allowed domains ({str(e)[:120]})")
        try:
            k = http("GET", f"{BASE}/key", headers=or_headers(), timeout=30).get("data", {})
            lim, used = k.get("limit"), k.get("usage")
            line(True, "OpenRouter accepts the key")
            print(f"  · key credit (shared by everyone on this key): used {used} $ of {lim if lim is not None else 'no limit'} $")
        except RuntimeError as e:
            line(False, "OpenRouter accepts the key",
                 "add a managed credential for openrouter.ai (Bearer, header Authorization), then start a NEW session: "
                 "a running session never picks up a credential added after it started"
                 if "HTTP 401" in str(e) else str(e)[:160])
    if s3_ready():
        try:
            probe = OUT / ".doctor.txt"
            probe.parent.mkdir(parents=True, exist_ok=True)
            probe.write_text(f"vg doctor {dt.datetime.now().isoformat()}")
            *_, prefix = _s3()
            link = s3_put(probe, f"{prefix}/{USER}/doctor.txt", "text/plain")
            got = urllib.request.urlopen(link, timeout=30).read().decode()
            line(got.startswith("vg doctor"), "bucket upload + signed link")
            print(f"  · open this from the office browser to test the proxy: {link}")
        except Exception as e:  # noqa: BLE001
            line(False, "bucket upload + signed link", str(e)[:200])
    else:
        print("  · no bucket configured (VG_S3_*): clips stay in out/; publish and gallery are off")
    print(f"  · Bootcamp wall: {wall_url() or 'not configured'}")
    print("  ready." if ok else "  fix the ✗ lines before the session.")
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------- cli

def main(argv=None):
    ap = argparse.ArgumentParser(prog="vg", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("models"); p.add_argument("--live", action="store_true"); p.set_defaults(f=cmd_models)
    p = sub.add_parser("show"); p.add_argument("model"); p.set_defaults(f=cmd_show)

    p = sub.add_parser("estimate"); p.add_argument("model"); p.add_argument("--dur", type=int)
    p.add_argument("--refs", type=int, default=0); p.add_argument("--resolution"); p.add_argument("--ratio")
    p.add_argument("--no-audio", action="store_true"); p.set_defaults(f=cmd_estimate)

    p = sub.add_parser("lint"); p.add_argument("model"); p.add_argument("--prompt"); p.add_argument("--prompt-file")
    p.add_argument("--dur", type=int); p.set_defaults(f=cmd_lint)

    p = sub.add_parser("submit"); p.add_argument("model"); p.add_argument("--prompt"); p.add_argument("--prompt-file")
    p.add_argument("--dur", type=int); p.add_argument("--ratio"); p.add_argument("--resolution"); p.add_argument("--seed", type=int)
    p.add_argument("--no-audio", action="store_true"); p.add_argument("--first-frame"); p.add_argument("--last-frame")
    p.add_argument("--ref", nargs="*", default=[]); p.add_argument("--ref-video", nargs="*", default=[])
    p.add_argument("--negative"); p.add_argument("--slot", help="templates/<template>/<slot id>")
    p.add_argument("--label"); p.add_argument("--yes", action="store_true"); p.add_argument("--dry-run", action="store_true")
    p.add_argument("--over-budget", action="store_true", help="facilitator only")
    p.add_argument("--change-engine", action="store_true", help="only when the designer explicitly asks for another engine on a template slot")
    p.add_argument("--raw", action="store_true", help="hands-on I part 1: the designer's words exactly as typed, no rewrite")
    p.set_defaults(f=cmd_submit)

    p = sub.add_parser("wait"); p.add_argument("--job"); p.add_argument("--max-minutes", type=float, default=9)
    p.add_argument("--every", type=float, default=15); p.set_defaults(f=cmd_wait)

    sub.add_parser("status").set_defaults(f=cmd_status)
    p = sub.add_parser("sent", help="the exact prompt a clip was made from, its mode and the lint findings")
    p.add_argument("--job"); p.add_argument("--label"); p.set_defaults(f=cmd_sent)
    sub.add_parser("spend").set_defaults(f=cmd_spend)
    p = sub.add_parser("wall", help="package a landed clip for the Bootcamp wall")
    p.add_argument("--job"); p.add_argument("--label"); p.add_argument("--note")
    p.add_argument("--done", metavar="STEM", help="mark a package as posted")
    p.set_defaults(f=lambda a: cmd_wall_done(a.done) if a.done else cmd_wall(a))

    p = sub.add_parser("image"); p.add_argument("--prompt"); p.add_argument("--prompt-file"); p.add_argument("--out", required=True)
    p.add_argument("--in", dest="inp", nargs="*", default=[]); p.add_argument("--ratio", default="16:9")
    p.add_argument("--over-budget", action="store_true"); p.set_defaults(f=cmd_image)

    p = sub.add_parser("publish"); p.add_argument("file"); p.set_defaults(f=cmd_publish)
    sub.add_parser("gallery").set_defaults(f=cmd_gallery)
    sub.add_parser("doctor").set_defaults(f=cmd_doctor)

    a = ap.parse_args(argv)
    try:
        a.f(a)
    except RuntimeError as e:
        die(str(e))


if __name__ == "__main__":
    main()
