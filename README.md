# Video lab

AI video for learning design, driven from Claude Code on the web. You describe the shot; Claude
writes the call, sends it to the model, collects the clip and drops it into a mock-up.

## Start

First time? Follow `SETUP.md` (ten minutes, browser only).

Open this repository in Claude Code on the web and say:

> Run the doctor, then show me the three templates.

Pick one and work slot by slot. Each slot is a task: you decide what we see, brief Claude with the
shot card (`.claude/skills/video-gen/reference/shot_brief.md`), compare takes and choose. Claude writes
the prompts; the edit is yours.

| Template | What you build | What you learn |
|---|---|---|
| **A · The joke** | A joke in three shots (setup, twist, punchline) plus your own end card | Briefing, comparing takes, choosing, designing the card |
| **B · Series** | Your presenter asking your three questions | Designing a person once and keeping them consistent across takes |
| **C · Your material** | A piece built from what you bring: a module script, photos of your spaces, a clip you own | Turning your own content into shots, combining real material with generated ones |

## The models

Veo 3.1 (cinematic shots), Seedance 2.5 (b-roll and long takes), MiniMax H3 (people speaking German
with lip sync) and Nano Banana Pro (start frames), all through one OpenRouter key.
See `.claude/skills/video-gen/reference/model_guide.md`.

## For facilitators

`DRY_RUN.md` (setup, probes, reserves, rehearsal) · `python3 -m unittest discover -s tests`.
