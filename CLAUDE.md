# Video lab

Training repository for the AI video bootcamp. Learning designers work here through Claude Code on
the web. Their laptops are locked-down corporate machines: **everything runs in this cloud session,
nothing is installed or run locally**, and the designer only ever needs the browser.

## What is here

| Path | What |
|---|---|
| `.claude/skills/video-gen/` | The skill: model call templates, prompt templates, `vg.py`, `assemble.py`, reference pages |
| `templates/A_teaser/` | Template A: 20 s teaser for a learning module (Veo opener, Seedance b-roll, H3 presenter, card) |
| `templates/B_series/` | Template B: one fictional presenter, three short questions, b-roll between them |
| `templates/C_own_material/` | Template C: built from the designer's own material (module text, photos of their spaces, a clip they own) |
| `input/refs/` | Start frames and reference images (fictional people only) |
| `input/own/` | The designer's own material for template C (see its README) |
| `out/` | Every generated clip and every preview |
| `jobs/<participant>.jsonl` | Ledger of every generation: prompt, model, cost, result |

Each template has `shotlist.json` (slots, models, durations), `prompts/` (a ready prompt per slot),
`placeholders/` (grey cards), `reserves/` (pre-generated clips, used if an API is down) and `slots/`
(what the participant generated).

## How to work with the designer

Use the `video-gen` skill for anything video. Start a session by running
`python3 .claude/skills/video-gen/scripts/vg.py doctor` and, if the designer has not picked one yet,
show the three templates with `assemble.py templates/<template> --status`.

- Talk to the designer in the language they write in (English or German).
- The designer briefs, you prompt. Show their brief back as the shot card (`reference/shot_brief.md`)
  with your assumptions marked, then the engine and the estimate; the model prompt only on request.
- Before every generation, show the estimate in euros and the lint result in one or two lines.
- Launch, then keep working on the next slot. Never sit and wait for a render.
- After each landed clip, rebuild the preview and give the link (or the file path).
- Keep answers short and concrete. The designer is learning the craft; explain the reason behind a
  prompt change in one sentence.

## Rules

- No real person as identity input (start frame or reference). Presenters are fictional.
- Nothing perishable spoken (dates, prices, rates, deadlines): on screen only.
- No brand names in prompts.
- Never print secrets. Never pass `--over-budget`.
- Every finished piece with generated people or realistic scenes carries a visible
  "Einige Szenen wurden mit KI erstellt." note.
