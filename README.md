# Video lab

AI video for learning design, driven from Claude Code on the web. You describe the shot; Claude
writes the call, sends it to the model, collects the clip and drops it into a mock-up.

## Start

Open this repository in Claude Code on the web and say:

> Run the doctor, then show me the three templates.

Pick one and work slot by slot. Every slot already has a working prompt to start from. To ask for
your own shots, brief Claude with the shot card in `.claude/skills/video-gen/reference/shot_brief.md`:
you describe the shot, Claude writes the prompt.

| Template | What you build | What you learn |
|---|---|---|
| **A · Teaser** | 20 s attention piece for a learning module | Which model for which shot, prompting, drafting cheap |
| **B · Series** | One presenter, three short questions | Keeping a person and a room consistent across takes |
| **C · Your material** | A piece built from what you bring: a module script, photos of your spaces, a clip you own | Turning your own content into shots, combining real material with generated ones |

## The models

Veo 3.1 (cinematic shots), Seedance 2.5 (b-roll and long takes), MiniMax H3 (people speaking German
with lip sync) and Nano Banana Pro (start frames), all through one OpenRouter key.
See `.claude/skills/video-gen/reference/model_guide.md`.

## For facilitators

`DRY_RUN.md` (setup, probes, reserves, rehearsal) · `python3 -m unittest discover -s tests`.
