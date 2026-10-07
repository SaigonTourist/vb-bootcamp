# Video lab

Training repository for the AI video bootcamp. Learning designers work here through Claude Code on
the web. Their laptops are locked-down corporate machines: **everything runs in this cloud session,
nothing is installed or run locally**, and the designer only ever needs the browser.

## What is here

| Path | What |
|---|---|
| `.claude/skills/video-gen/` | The skill: model call templates, prompt templates, `vg.py`, `assemble.py`, reference pages |
| `templates/A_teaser/` | Template A: 20 s teaser (Veo opener, Seedance b-roll, H3 presenter telling the designer's joke) and a designed end card |
| `templates/B_series/` | Template B: one fictional presenter, three short questions, b-roll between them |
| `templates/C_own_material/` | Template C: built from the designer's own material (module text, photos of their spaces, a clip they own) |
| `input/refs/` | Start frames and reference images |
| `input/own/` | The designer's own material for template C (see its README) |
| `out/` | Every generated clip and every preview |
| `jobs/<participant>.jsonl` | Ledger of every generation: prompt, model, cost, result |

Each template has `shotlist.json` (slots, models, durations), `prompts/` (a ready prompt per slot),
`placeholders/` (grey cards), `reserves/` (pre-generated clips, used if an API is down) and `slots/`
(what the participant generated).

## When the session opens with a greeting

If the first message is a greeting or has no specific request ("Hello!", "Hi", "Hallo", "Let's go"),
run `python3 .claude/skills/video-gen/scripts/welcome.py` once and answer in the language of the
greeting, in this order and briefly:

1. **Welcome**: one or two sentences. This is the AI Video Bootcamp: they describe shots, you write
   the prompts, call Veo, Seedance and MiniMax H3, and assemble the clips into a finished piece.
2. **Checks**: one line if everything is ✓. Otherwise name each ✗ with its fix in plain words; a key
   that is not accepted means adding the credential and starting a **new** session (this one will
   never see it).
3. **Where you are**: the three templates in one line each (A teaser, B series, C your material)
   with how many slots are filled, anything still rendering, spend so far, and any material found
   in `input/own/`.
4. **Next step**: the suggested step from the script, with the exact sentence they can type.

No tables of commands, no file paths unless they need one. End with the sentence to type.

## How to work with the designer

Use the `video-gen` skill for anything video. Start a session by running
`python3 .claude/skills/video-gen/scripts/vg.py doctor` and, if the designer has not picked one yet,
show the three templates with `assemble.py templates/<template> --status`.

- Talk to the designer in the language they write in (English or German).
- "Raw mode" means part 1: send their words exactly as typed with `--raw`, no help; after it lands, show
  what was sent, what went wrong and the next step (SKILL.md).
- Otherwise the designer briefs, you prompt. Show their brief back as the shot card (`reference/shot_brief.md`)
  with your assumptions marked, then the engine and the estimate.
- After every landed clip, show the exact prompt that was sent (`vg.py sent`) and, for assisted takes,
  what you added to their brief.
- Before every generation, show the estimate in euros and the lint result in one or two lines.
- Launch, then keep working on the next slot. Never sit and wait for a render.
- After each landed clip, rebuild the preview and show the clip and the preview in the chat, where the designer watches and can download them.
- Keep answers short and concrete. The designer is learning the craft; explain the reason behind a
  prompt change in one sentence.

## Rules

- **No git during the session.** Do not commit, push or open pull requests, and do not ask whether
  to. Generated clips, takes and edits stay in the session. Only when the designer explicitly asks
  ("save my work", "push it", "I want to see it on GitHub") commit and push once.

- The engine of a template slot is fixed by its shotlist (Veo, Seedance or H3; Veo slots may be drafted on veo-fast). Never switch it on your own; the day compares the engines.

- Real faces from the designer's material may be used as start frames or references; no consent question. No minors.
- Nothing perishable spoken (dates, prices, rates, deadlines): on screen only.
- No brand names in prompts.
- Never print secrets. Never pass `--over-budget`.
- Every finished piece with generated people or realistic scenes carries a visible
  "Einige Szenen wurden mit KI erstellt." note.
