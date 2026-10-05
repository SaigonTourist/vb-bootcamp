#!/usr/bin/env python3
"""
The ten before/after pairs for the prompting block (facilitators only, paid, about 14 $).
Each pair changes one thing, so the difference on screen is the strategy and nothing else.

  python3 scripts/make_pairs.py                    plan and cost, nothing sent
  python3 scripts/make_pairs.py --go               start frames and images, then submit every video at once
  python3 scripts/make_pairs.py --wait             collect what has rendered (repeat until nothing is pending)
  python3 scripts/make_pairs.py --compose          one side-by-side pair.mp4 per pair, for the beamer
  python3 scripts/make_pairs.py --go --only 03_brands 04_closeup

Pairs live in teaching/pairs/pairs.json; prompts next to each pair. Runs on the 'pairs' ledger.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAIRS = REPO / "teaching" / "pairs"
SCRIPTS = REPO / ".claude/skills/video-gen/scripts"
VG = SCRIPTS / "vg.py"
sys.path.insert(0, str(SCRIPTS))
os.environ.setdefault("VG_USER", "pairs")
os.environ.setdefault("VG_BUDGET_EUR", "40")
import vg  # noqa: E402
import assemble  # noqa: E402

FRAME = "input/refs/presenter_A.png"
FRAME_PROMPT = "templates/A_teaser/prompts/frame_presenter_A.md"


def load(only=None):
    pairs = json.loads((PAIRS / "pairs.json").read_text())
    return [p for p in pairs if not only or p["id"] in only]


def shots(p):
    """(side, index, shot, output path relative to the repo)"""
    for side in ("before", "after"):
        many = len(p[side]) > 1
        for i, s in enumerate(p[side], 1):
            name = f"{side}_{i}.mp4" if many else f"{side}.mp4"
            if s.get("reuse"):
                name = s["reuse"]
            yield side, i, s, (PAIRS / p["id"] / name).relative_to(REPO)


def opt(args, flag, default=None):
    return args[args.index(flag) + 1] if flag in args else default


def run_vg(*args):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO))
    return subprocess.run([sys.executable, str(VG), *args], cwd=REPO, env=env).returncode


def plan(pairs):
    steps, image_usd = [], vg.load_model("image")["pricing"]["usd_per_image"]
    if any(p.get("needs_frame") for p in pairs) and not (REPO / FRAME).exists():
        steps.append(("image", "presenter_A", ["image", "--prompt-file", FRAME_PROMPT, "--out", FRAME], image_usd))
    for p in pairs:
        for im in p.get("images", []):
            if not (REPO / im["out"]).exists():
                steps.append(("image", p["id"], ["image", "--prompt-file", str((PAIRS / p["id"] / im["prompt"]).relative_to(REPO)),
                                                 "--out", im["out"]], image_usd))
        for side, i, s, out in shots(p):
            if s.get("reuse") or (REPO / out).exists():
                continue
            m = vg.load_model(s["model"])
            nrefs = s["args"].count("--ref")
            usd = vg.estimate_usd(m, s["dur"], opt(s["args"], "--resolution"), True, nrefs)
            args = ["submit", s["model"], "--prompt-file", str((PAIRS / p["id"] / s["prompt"]).relative_to(REPO)),
                    "--dur", str(s["dur"]), *s["args"], "--slot", str(out), "--label", f"{p['id']}_{out.stem}", "--yes"]
            steps.append(("video", f"{p['id']} {out.stem}", args, usd))
    return steps


def compose(p):
    rows = {"before": [], "after": []}
    for side, i, s, out in shots(p):
        rows[side].append(REPO / out)
    missing = [str(f.relative_to(REPO)) for f in rows["before"] + rows["after"] if not f.exists()]
    if missing:
        print(f"  · {p['id']}: waiting for {', '.join(missing)}")
        return
    ff = assemble.ffmpeg()
    files = rows["before"] + rows["after"]
    longest = max(assemble.probe(f)[0] for f in files)
    cols = len(rows["before"])
    w, h = (960, 540)
    labels = [p["labels"][0]] * cols + [p["labels"][1]] * cols
    out = PAIRS / p["id"] / "pair.mp4"
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        chains = []
        for k, (f, lab) in enumerate(zip(files, labels)):
            tf = tmp / f"l{k}.txt"
            tf.write_text(lab)
            d = assemble.probe(f)[0]
            # in the 2x2 grid the title sits on the seam, so the lower row labels its clips at the bottom
            y = "h-text_h-16" if cols > 1 and k >= cols else "16"
            chains.append(f"[{k}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
                          f"setsar=1,fps=25,tpad=stop_mode=clone:stop_duration={longest - d + 0.5:.2f},"
                          f"drawtext={assemble.font_opt()}:textfile='{assemble.esc_path(tf)}':fontcolor=white:fontsize=26:"
                          f"box=1:boxcolor=black@0.6:boxborderw=10:x=16:y={y}[v{k}]")
        title = tmp / "title.txt"
        title.write_text(f"{p['n']:02d} · {p['title']}")
        n = len(files)
        if cols == 1:
            grid = f"[v0][v1]hstack=inputs=2[g];[g]pad=1920:1080:0:270:color=0x14213d,"
        else:
            # before row on top, after row below; title band is drawn over the seam
            grid = f"{''.join(f'[v{k}]' for k in range(n))}xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[g];[g]"
        draw_title = (f"drawtext={assemble.font_opt()}:textfile='{assemble.esc_path(title)}':fontcolor=white:fontsize=40:"
                      f"box=1:boxcolor=0x14213d@0.9:boxborderw=14:x=(w-text_w)/2:y={'90' if cols == 1 else '(h-text_h)/2'}[o]")
        fc = ";".join(chains) + ";" + grid + draw_title
        cmd = [ff, "-y"]
        for f in files:
            cmd += ["-i", str(f)]
        cmd += ["-filter_complex", fc, "-map", "[o]", "-t", f"{longest + 0.5:.2f}", "-an",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
        assemble.run(cmd)
    note = " (muted; play the originals for sound)" if p.get("audio") else ""
    print(f"  ✓ {out.relative_to(REPO)}{note}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--compose", action="store_true")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    pairs = load(a.only)

    if a.wait:
        sys.exit(run_vg("wait"))
    if a.compose:
        for p in pairs:
            compose(p)
        return

    steps = plan(pairs)
    for kind, name, args, usd in steps:
        model = "image" if kind == "image" else args[1]
        print(f"  {name:28} {model:9} {vg.fmt_money(usd)}")
    total = sum(s[-1] for s in steps)
    print(f"  total {vg.fmt_money(total)} for {len(steps)} generations")
    if not a.go:
        print("  nothing sent. Repeat with --go to submit.")
        return
    for kind, name, args, usd in [s for s in steps if s[0] == "image"]:
        print(f"\n  ▶ {name} (start frame / reference)")
        if run_vg(*args):
            sys.exit(f"  ✗ image for {name} failed; videos that need it were not sent")
    for kind, name, args, usd in [s for s in steps if s[0] == "video"]:
        print(f"\n  ▶ {name}")
        if run_vg(*args):
            print(f"  ✗ {name} was not submitted; continuing")
    print("\n  all submitted. Collect with: python3 scripts/make_pairs.py --wait   then   --compose")


if __name__ == "__main__":
    main()
