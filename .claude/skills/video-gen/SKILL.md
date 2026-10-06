---
name: video-gen
description: Generate video clips with Google Veo 3.1, ByteDance Seedance 2.5 and MiniMax H3 (and start frames with Nano Banana Pro) through OpenRouter, and assemble them into the templates in templates/. Use whenever someone wants a video, a shot, b-roll, a presenter speaking German, a start frame, to fill a slot of a template, to check what a generation costs, to see what is rendering, or to build a preview.
---

# video-gen

Everything runs inside this cloud session. The designer only has a browser. Never ask them to
install or run anything on their laptop.

Tools, all standard-library Python, run from the repo root:

```bash
python3 .claude/skills/video-gen/scripts/vg.py --help
python3 .claude/skills/video-gen/scripts/assemble.py --help
```

## Which model

| Need | Model key | Why |
|---|---|---|
| A person speaking to camera (German or any language) | `h3` | Voice and lip sync in one pass; holds a face from a start frame; 5-15 s |
| An object that must match a photo | `h3` | Most faithful to reference images |
| Opener, establishing shot, mood, final quality 16:9 | `veo` | 1080p, native sound; 4, 6 or 8 s |
| Drafting a Veo shot | `veo-fast` | About a quarter of the price; same prompt and seed, then `veo` for the keeper |
| B-roll without faces, scenes from several references, long takes | `seedance` | Up to 30 s and many references; rejects images of real people |
| A start frame (fictional presenter, room, object pose) | `vg.py image` | Nano Banana Pro, about 0.13 € |

`vg.py show <key>` prints the exact call template, limits, prices and known failure modes.

## The designer briefs, Claude prompts

Designers do not write model prompts; they brief you, and the day's goal is that they learn to brief
well. `reference/shot_brief.md` is the shot card they use: what the viewer should take away, the one
action, who (and whether it is the same person as another shot), camera distance, place, light,
sound with exact words, on-screen text, length.

1. **Read their brief against the card.** Turn it into a prompt following
   `reference/idea_to_prompt.md` (filmable action behind every abstract word, one shot per action,
   the engine per shot, defaults for what is missing).
2. **Show the brief back before anything else**, in their words, as the filled card: each field,
   and for every field they did not give, your default marked *(assumed)*. Then the engine with its
   reason and the estimate. Show the model prompt itself only if they ask, or after the render.
3. **Coach, briefly.** If a field that decides quality is missing or vague (no action, a feeling
   instead of something visible, no exact words for speech, "close-up" on an emotional face,
   a brand name, a date in the voice), say in one line what it would cost them and offer the fix.
   Ask only what changes the engine, the cost or the result; assume the rest.
4. **They correct the card, not the prompt.** "Wider", "only he speaks", "morning not evening":
   apply it, re-show the changed fields, launch on their go.
5. **After the render, ask for feedback the card's way:** what is wrong in one word, where, what to
   keep (the table at the end of `reference/shot_brief.md`). Change one thing and say which.

Prompt templates per engine, in `.claude/skills/video-gen/prompts/`:

| File | For |
|---|---|
| `h3_talking.md` | A person speaking to camera, series with one presenter |
| `h3_object.md` | An object that must match a photo |
| `veo_cinematic.md` | Cinematic shots, and short dialogue inside a scene |
| `seedance_broll.md` | B-roll, and scenes built from several reference images |
| `image_start_frame.md` | Start frames and variants of the same fictional presenter |

## Template C: the designer's own material

Template C is built from what the designer brings, in `input/own/` (uploaded on github.com, then
`git pull`; pasted images you save there yourself). `templates/C_own_material/shotlist.json` is only
a starter: rewrite its slots, purposes and prompts from their material.

- **Module text** (script, storyboard, slides): pull out two or three key messages, show them back
  as a list, and turn each into one shot via the shot card. Spoken lines come from their text,
  shortened to about 2 words per second.
- **Photos of their places and objects**: use them as Seedance references or start frames so the
  generated shots look like their world. Check each one first: if a person is recognisable, do not
  use it as a reference and say why.
- **A clip they own**: ask once whether everyone visible agreed to be filmed for this use. Yes: cut it
  in untouched as `type: real` slots (`trim_start` and `dur` pick the part). Unsure: leave it out.
- **Logo and colours**: title and end cards in the edit, never inside a generated shot.
- Nothing from their material leaves the session except what a generation needs, and nothing with
  client data or real people's faces goes to a model.

## The flow for one shot

1. **Find the slot.** `assemble.py templates/<template> --status` lists slots, models and what is
   filled. Each slot has a ready prompt in `templates/<template>/prompts/<slot>.md`.
2. **Write or adapt the prompt** from the model's prompt template in `.claude/skills/video-gen/prompts/`.
   Save it as a file; the file is the record of what was asked.
3. **Lint and estimate, and show both to the designer:**
   `vg.py lint <key> --prompt-file <file> --dur <s>` and `vg.py estimate <key> --dur <s>`.
   Lint warnings are advice; explain them in one line each and offer the rewrite.
4. **Submit** (returns at once):
   `vg.py submit <key> --prompt-file <file> --dur <s> [--first-frame img] [--seed n] --slot templates/<template>/<slot>`.
   Exit code 3 means the cost is above the confirmation line: ask the designer, then repeat with `--yes`.
5. **Keep working** on the next slot while it renders (2 to 13 minutes). Launch `vg.py wait` in the
   background (it returns after 9 minutes at most; run it again if something is still rendering).
6. **When it lands**, `wait` downloads it to `out/`, copies it into the slot and, if a bucket is
   configured, prints a link that plays in the browser. Rebuild the preview:
   `assemble.py templates/<template> [--publish]`.

## Iteration discipline

- **Change one thing per retry** and say which. A blind relaunch of the same prompt is a coin toss
  at full price.
- **Diagnose before you spend.** Look at what came back (extract a frame with ffmpeg and read it)
  and name the failure: framing, physics, identity, text on surfaces, audio. Then fix the prompt
  for that failure.
- **Write what you want, not what you fear.** Every forbidden thing you name gets drawn. Rewrite a
  "no X" as the positive state ("the card lies flat on its back").
- **Draft Veo on `veo-fast`** with a fixed `--seed`; render the keeper on `veo`.
- **H3 series:** one start frame, the same SHOT/SCENE/RULES text, only the DIALOGUE changes.

## Hard rules

- **No real person as identity input.** Never use a photo of a colleague, a client or a public
  figure as a start frame or reference for a person. Presenters are fictional, made with
  `vg.py image`. No images of minors at all. Real people appear only as real footage they consented to.
- **Nothing perishable is spoken.** Dates, prices, rates, percentages, deadlines and counters go on
  screen as text (a card or a caption), never in the dialogue. Spoken, they force a re-render.
- **No brand names in prompts**, including our own: models draw them badly. Real logos go in the edit.
- **Money:** never pass `--over-budget`; that is for the facilitators. If a call returns 402 or the
  budget check stops you, tell the designer to call a facilitator.
- **Secrets:** never print, echo or write the API key or bucket credentials. `vg.py doctor` reports
  status only.
- **Labelling:** every finished piece that shows AI-generated people or realistic scenes carries a
  visible "KI-generiert" note somewhere (card or caption). See `reference/compliance.md`.

## When something fails

| Message | Meaning | Do |
|---|---|---|
| `400 ... No matching discriminator` | A reference lacks `"type": "image_url"` | Bug in a hand-built call; use `vg.py submit` |
| `402` / insufficient credits | The participant key hit its cap | Stop, call a facilitator |
| `InputImageSensitiveContentDetected` | Seedance saw a person in an input image | Move the shot to `h3` or use an image without people |
| `TaskTypeConstraint` | Seedance read the prompt as an edit | Remove add / remove / replace / extend / continue |
| Status `failed` with `Invalid media input` | Provider-side flake fetching the media | Resubmit once as a new job |
| Still rendering after 15 min | Queue is slow | `vg.py wait` again; meanwhile work on another slot |
| Person repeats the last word, or the clip overruns | H3 fills to the end | Expected; the slot `dur` cuts before the filler |

## Watching the results

If `vg.py doctor` shows a bucket, every finished clip and `assemble.py --publish` print a signed
link that plays in the browser for 7 days, and `vg.py gallery` builds one page with everything the
participant made. Without a bucket, the clips stay in `out/`: commit them on the session branch and
push, and the designer opens them from the repository in the browser.

## Reference

- `reference/shot_brief.md`: the shot card designers brief you with, and the feedback words after a render.
- `reference/idea_to_prompt.md`: from a designer's idea to one prompt per engine, with worked examples.
- `reference/model_guide.md`: the one-page model guide the team keeps.
- `reference/prompting.md`: the prompt contract, with before and after examples.
- `reference/compliance.md`: consent, GDPR, EU AI Act transparency, where the data goes.
