#!/usr/bin/env python3
"""
Everything Claude needs to greet a participant, in one call: environment checks, the three templates,
the participant's jobs and spend, the material they brought, and a suggested next step.

  python3 .claude/skills/video-gen/scripts/welcome.py
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vg  # noqa: E402
import assemble  # noqa: E402

REPO = vg.REPO


def section(title):
    print(f"\n## {title}")


def doctor() -> list:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            vg.cmd_doctor(None)
        except SystemExit:
            pass
    out = buf.getvalue()
    print(out.rstrip())
    return [line.strip() for line in out.splitlines() if line.strip().startswith("✗")]


def templates() -> dict:
    """slot counts per template: generated / total generated slots"""
    state = {}
    for f in sorted(REPO.glob("templates/*/shotlist.json")):
        sl = json.loads(f.read_text())
        gen = [s for s in sl["slots"] if s.get("model")]
        done = [s for s in gen if (f.parent / "slots" / f"{s['id']}.mp4").exists()]
        state[sl["id"]] = (len(done), len(gen), sl["title"])
        print(f"  {sl['title']}: {len(done)} of {len(gen)} generated slots filled")
    return state


def jobs():
    state = vg.jobs()
    videos = [j for j in state.values() if j.get("kind") == "video"]
    pending = [j for j in videos if j.get("status") not in ("completed", "failed")]
    failed = [j for j in videos if j.get("status") == "failed"]
    print(f"  {len(videos)} videos ({len(pending)} rendering, {len(failed)} failed), "
          f"spend {vg.eur(vg.spent_usd(state)):.2f} € of {vg.BUDGET_EUR:.0f} €")
    for j in pending:
        print(f"  · rendering: {j.get('label')} ({j.get('key')})")
    return videos, pending


def material():
    own = [p for p in (REPO / "input" / "own").glob("*") if p.is_file() and p.name != "README.md"]
    if own:
        for p in own:
            print(f"  · {p.name} ({p.stat().st_size / 1e6:.1f} MB)")
    else:
        print("  · nothing yet (template C uses it; see input/own/README.md)")
    return own


def main():
    print(f"# Video lab · participant {vg.USER}")
    section("Checks")
    problems = doctor()
    section("Templates")
    tpl = templates()
    section("Your generations")
    videos, pending = jobs()
    section("Your material (input/own)")
    own = material()

    section("Suggested next step")
    a_done, a_total, _ = tpl.get("A_teaser", (0, 0, ""))
    b_done, b_total, _ = tpl.get("B_series", (0, 0, ""))
    if any("accepts the key" in p for p in problems):
        print("  Fix the key first: managed credential for openrouter.ai, then a NEW session (SETUP.md step 2).")
    elif problems:
        print("  Fix the ✗ lines above first; raise your hand if unsure.")
    elif pending:
        print("  Collect what is rendering: \"Check my renders.\" Meanwhile brief the next slot.")
    elif not videos:
        print("  First render, unassisted: \"Raw mode, slot s2: <describe the advisor getting ready for a client>\"")
    elif a_done < a_total:
        print("  Continue template A: \"Show me the shot card for the next empty slot of template A.\"")
    elif b_done < b_total:
        print("  Template A is filled: \"Build the preview of template A.\" Then move to template B.")
    elif own:
        print("  Build template C from your material: \"My material is in input/own, build template C from it.\"")
    else:
        print("  Bring your material into input/own for template C, or refine a shot with one change.")


if __name__ == "__main__":
    main()
