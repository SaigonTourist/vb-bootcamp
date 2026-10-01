#!/usr/bin/env python3
"""
Pre-generate the reserve clip for every generated slot of the templates (facilitators only, paid).
A reserve is what assemble.py uses when the participant has not generated that slot, so the day
survives an API outage. Start frames are made first, because H3 slots depend on them.

  python3 scripts/make_reserves.py                     plan and total, nothing sent
  python3 scripts/make_reserves.py --go                submit everything (then: vg.py wait)
  python3 scripts/make_reserves.py --go --only A_teaser

Slots whose prompt still has [brackets] to fill in are skipped (template C waits for the real footage).
Runs on the 'reserves' ledger, so it never counts against a participant.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VG = REPO / ".claude/skills/video-gen/scripts/vg.py"
sys.path.insert(0, str(VG.parent))
os.environ.setdefault("VG_USER", "reserves")
os.environ["VG_BUDGET_EUR"] = os.environ.get("VG_BUDGET_EUR", "200")
import vg  # noqa: E402


def plan(only=None):
    steps = []
    for f in sorted(REPO.glob("templates/*/shotlist.json")):
        sl = json.loads(f.read_text())
        if only and sl["id"] not in only:
            continue
        m = f.parent
        for fr in sl.get("frames", []):
            if not (REPO / fr["out"]).exists():
                steps.append(("image", sl["id"], fr["id"], ["image", "--prompt-file", str(m / fr["prompt"]), "--out", fr["out"]],
                              vg.load_model("image")["pricing"]["usd_per_image"]))
        for s in sl["slots"]:
            if not s.get("model"):
                continue
            prompt = (m / s["prompt"]).read_text()
            if "[" in prompt:
                print(f"  · skip {sl['id']}/{s['id']}: prompt still has [brackets] to fill in")
                continue
            if (m / "reserves" / f"{s['id']}.mp4").exists():
                continue
            dur = int(s.get("gen_dur", s["dur"]))
            args = ["submit", s["model"], "--prompt-file", str(m / s["prompt"]), "--dur", str(dur),
                    "--slot", str((m / "reserves" / f"{s['id']}.mp4").relative_to(REPO)), "--label", f"{sl['id']}_{s['id']}", "--yes"]
            if s.get("seed") is not None:
                args += ["--seed", str(s["seed"])]
            if s.get("first_frame"):
                args += ["--first-frame", s["first_frame"]]
            steps.append(("video", sl["id"], s["id"], args, vg.estimate_usd(vg.load_model(s["model"]), dur)))
    return steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    steps = plan(a.only)
    for kind, mq, sid, args, usd in steps:
        print(f"  {mq:16} {sid:12} {args[1] if kind == 'video' else 'image':9} {vg.fmt_money(usd)}")
    total = sum(x[-1] for x in steps)
    print(f"  total {vg.fmt_money(total)} for {len(steps)} generations")
    if not a.go:
        print("  nothing sent. Repeat with --go to submit.")
        return
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(REPO))
    for kind, mq, sid, args, usd in sorted(steps, key=lambda x: x[0] != "image"):
        print(f"\n  ▶ {mq}/{sid}")
        r = subprocess.run([sys.executable, str(VG), *args], cwd=REPO, env=env)
        if r.returncode:
            print(f"  ✗ {mq}/{sid} returned {r.returncode}; continuing")
    print("\n  submitted. Collect with: VG_USER=reserves python3 .claude/skills/video-gen/scripts/vg.py wait")


if __name__ == "__main__":
    main()
