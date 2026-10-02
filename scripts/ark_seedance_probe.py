#!/usr/bin/env python3
"""
One Seedance 2.5 generation straight through BytePlus ModelArk (not OpenRouter).
Standard library only, so it runs unchanged in a Claude Code on the web session or locally.

  python3 scripts/ark_seedance_probe.py --check      free: key accepted + host reachable, nothing generated
  python3 scripts/ark_seedance_probe.py --dry-run    print the request body, send nothing
  python3 scripts/ark_seedance_probe.py              one 5 s clip, 16:9, with sound (paid)
  python3 scripts/ark_seedance_probe.py --prompt-file templates/A_teaser/prompts/s1.md --dur 6

Environment: ARK_API_KEY (optional in Claude Code on the web when a managed credential for the Ark
host injects the Authorization header), ARK_BASE (default the ap-southeast endpoint),
ARK_MODEL (default dreamina-seedance-2-5-260628).

Seedance 2.5 on Ark takes only: model, content[], generate_audio, ratio, duration (4-30),
output_format. No resolution, negative prompt, watermark or --flags: a 2.0-style body is accepted
at create and then fails later with a generic InvalidParameter.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE = os.environ.get("ARK_BASE", "https://ark.ap-southeast.bytepluses.com/api/v3").rstrip("/")
MODEL = os.environ.get("ARK_MODEL", "dreamina-seedance-2-5-260628")
DEFAULT_PROMPT = REPO / "templates/A_teaser/prompts/s2.md"
RATIOS = ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16", "adaptive")


def die(msg):
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(1)


def auth_headers():
    """With ARK_API_KEY in the environment, send it. Without it, send no Authorization header: in Claude
    Code on the web a managed credential for this host makes the proxy add it, and the key never
    enters the container."""
    k = os.environ.get("ARK_API_KEY", "").strip()
    return {"Authorization": f"Bearer {k}"} if k else {}


def call(method, url, body=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={**auth_headers(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"raw": raw[:400]}
    except urllib.error.URLError as e:
        host = urllib.parse.urlparse(url).netloc
        die(f"cannot reach {host} ({e.reason}). In the cloud, add {host} to the environment's allowed domains.")


def find_video_url(o):
    if isinstance(o, str) and o.startswith("http") and ".mp4" in o:
        return o
    if isinstance(o, dict):
        if isinstance(o.get("video_url"), str):
            return o["video_url"]
        o = list(o.values())
    if isinstance(o, list):
        for v in o:
            f = find_video_url(v)
            if f:
                return f
    return None


def check():
    """GET a task id that cannot exist: 401/403 means the key is wrong, 404/400 means key and network are fine."""
    host = urllib.parse.urlparse(BASE).netloc
    code, j = call("GET", f"{BASE}/contents/generations/tasks/cgt-00000000000000-probe", timeout=30)
    err = (j.get("error") or {}) if isinstance(j, dict) else {}
    print(f"  {host} answered HTTP {code} {err.get('code', '')}")
    if code in (401, 403):
        if auth_headers():
            die("the key was rejected. Check ARK_API_KEY and that it belongs to the ap-southeast region.")
        die(f"no key reached {host}. Add a managed credential for {host} (type Bearer, header Authorization, "
            "path prefix /api/v3/) or set ARK_API_KEY.")
    print("  ✓ key accepted and host reachable. Nothing was generated, nothing was charged.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prompt")
    ap.add_argument("--prompt-file", default=str(DEFAULT_PROMPT))
    ap.add_argument("--dur", type=int, default=5)
    ap.add_argument("--ratio", default="16:9", choices=RATIOS)
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out")
    ap.add_argument("--max-minutes", type=float, default=20)
    a = ap.parse_args()

    if a.check:
        check()
        return
    if not 4 <= a.dur <= 30:
        die("Seedance 2.5 takes 4 to 30 seconds.")
    prompt = a.prompt or Path(a.prompt_file).read_text().strip()
    body = {"model": MODEL, "content": [{"type": "text", "text": prompt}],
            "generate_audio": not a.no_audio, "ratio": a.ratio, "duration": a.dur}
    if a.seed is not None:
        body["seed"] = a.seed
    tokens = {"16:9": 1280 * 720, "9:16": 1280 * 720}.get(a.ratio, 960 * 960) * 24 * a.dur / 1024
    print(f"  {MODEL} · {a.dur} s · {a.ratio} · audio {'on' if body['generate_audio'] else 'off'} · "
          f"about {tokens / 1000:.0f}k video tokens")
    if a.dry_run:
        print(json.dumps(body, indent=2, ensure_ascii=False))
        print("  dry run: nothing sent.")
        return

    t0 = time.time()
    code, j = call("POST", f"{BASE}/contents/generations/tasks", body)
    if code not in (200, 201, 202):
        die(f"create failed: HTTP {code} {json.dumps(j)[:400]}")
    tid = j.get("id") or j.get("task_id") or (j.get("data") or {}).get("task_id")
    print(f"  → task {tid} created")

    status = None
    while time.time() - t0 < a.max_minutes * 60:
        time.sleep(10)
        code, j = call("GET", f"{BASE}/contents/generations/tasks/{tid}", timeout=60)
        st = str(j.get("status") or (j.get("data") or {}).get("status") or "?").lower()
        if st != status:
            print(f"  · {time.time() - t0:5.0f} s  {st}")
            status = st
        if st in ("succeeded", "completed", "success"):
            break
        if st in ("failed", "error", "cancelled", "expired"):
            die(f"task {st}: {json.dumps(j.get('error') or j)[:400]}")
    else:
        die(f"still {status} after {a.max_minutes:.0f} min; task {tid}. Re-run later with the same id is not supported here; check the Ark console.")

    url = find_video_url(j.get("content") or j)
    if not url:
        die(f"succeeded but no video url in the response: {json.dumps(j)[:400]}")
    dl_host = urllib.parse.urlparse(url).netloc
    out = Path(a.out) if a.out else REPO / "out" / f"ark_seedance_{tid}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=600) as r, open(out, "wb") as f:
            shutil.copyfileobj(r, f, 1 << 20)
    except urllib.error.URLError as e:
        die(f"render finished but the download from {dl_host} failed ({getattr(e, 'reason', e)}). "
            f"In the cloud, add {dl_host} (or *.bytepluses.com) to the allowed domains.")

    took = time.time() - t0
    usage = j.get("usage") or {}
    print(f"  ✓ {out.relative_to(REPO) if out.is_relative_to(REPO) else out} · {out.stat().st_size / 1e6:.1f} MB · {took / 60:.1f} min")
    print(f"    download host: {dl_host}")
    if usage:
        print(f"    usage: {json.dumps(usage)}")
    ff = shutil.which("ffmpeg")
    if ff:
        info = subprocess.run([ff, "-hide_banner", "-i", str(out)], capture_output=True, text=True).stderr
        dur = re.search(r"Duration: ([\d:.]+)", info)
        vid = re.search(r"Video: .*?, (\d{3,5}x\d{3,5})", info)
        print(f"    {dur.group(1) if dur else '?'} · {vid.group(1) if vid else '?'} · audio {'yes' if ' Audio:' in info else 'no'}")


if __name__ == "__main__":
    main()
