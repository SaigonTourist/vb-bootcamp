#!/usr/bin/env python3
"""
Check the German H3 probes: transcribe each take with local whisper and compare it with the line
it was asked to say. Facilitator machine only (needs the whisper package and ffmpeg).

  <venv with whisper>/bin/python probes/check_de.py [--model small]

A take passes at >= 0.90 word match. Listen to each one as well: whisper hears words, not accent,
lip sync or pacing.
"""
import argparse
import difflib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def words(t):
    t = re.sub(r"also,? ja\.?\s*$", "", t.strip(), flags=re.I)
    return re.findall(r"[a-zäöüß]+", t.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="small")
    a = ap.parse_args()
    import whisper
    model = whisper.load_model(a.model)
    ledger = REPO / "jobs" / "probes.jsonl"
    state = {}
    for line in ledger.read_text().splitlines():
        r = json.loads(line)
        state.setdefault(r["id"], {}).update(r)
    for j in state.values():
        if not str(j.get("label", "")).startswith("de_") or j.get("status") != "completed":
            continue
        asked = re.search(r'DIALOGUE:\s*"(.+?)"', j["prompt"], re.S).group(1)
        heard = model.transcribe(str(REPO / j["file"]), language="de")["text"]
        ratio = difflib.SequenceMatcher(None, words(asked), words(heard)).ratio()
        print(f"\n{j['label']} · {'PASS' if ratio >= 0.9 else 'CHECK'} · word match {ratio:.2f} · {j.get('seconds', '?')} s render")
        print(f"  asked: {asked}")
        print(f"  heard: {heard.strip()}")


if __name__ == "__main__":
    main()
