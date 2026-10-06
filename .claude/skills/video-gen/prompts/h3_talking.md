# H3 · a person speaking to camera

Use for: a presenter, a trainer, a colleague-type character saying one or two sentences in German
(or English, French, Italian...). H3 generates the voice and the lip sync together.

## How it holds a person across takes

1. Make the person once as a start frame with `vg.py image`, or use a photo of the real person from the designer's material.
2. Every take uses that image as `--first-frame` and the **same SHOT, SCENE and RULES text, word for word**.
3. Only the DIALOGUE changes between takes.

That is the whole trick. Change the scene text and you get a different room and, often, a different face.

## Skeleton

Order matters: what happens comes first. The start frame already carries the face and the room, so
the SCENE block is a short reminder at the end, not the opening.

```
SHOT: medium shot, eye level, camera locked off on a tripod, 35mm lens, as in the start frame.
ACTION: {the woman / the man} looks straight into the lens and speaks in German, {calm and warm /
direct}, at a natural pace, {one small gesture} on the word in capitals, keeps eye contact to the end.
DIALOGUE: "{line 1} {line 2} Also, ja."
SCENE: {two lines: where they are, clothing in plain words, one light source and its side}.
RULES: German pronunciation, native speaker from {region}. Mouth matches every word. Steady camera,
same framing for the whole take. Speech ends on the last word, then a relaxed half smile.
```

- **Filler at the end ("Also, ja.")**: H3 overshoots by about 0.6 s and keeps talking to fill the
  clip. The filler gives it something harmless to say; the slot's `dur` in the shotlist cuts before it.
- **About 2 words per second.** 8 s holds 13 to 16 words including the filler. `vg.py lint` counts.
- **CAPITALS on one word** give it vocal emphasis. One per line, not more.
- **Nothing perishable in the dialogue.** No dates, prices, percentages or deadlines spoken; those
  go on screen as text, where changing them is free.

## Example (template A, slot s3)

```
SHOT: medium shot, eye level, camera locked off on a tripod, 35mm lens, as in the start frame.
ACTION: the woman looks straight into the lens and speaks in German, calm and warm, at a natural
pace, opens one hand toward the camera on the word FRAGE, keeps eye contact to the end.
DIALOGUE: "Ein gutes Gespräch beginnt nicht mit dem Produkt. Es beginnt mit einer FRAGE. Also, ja."
SCENE: she sits at a round oak table in a quiet meeting room, navy knitted top, dark blond hair tied
back loosely. One soft window light from camera left, warm lamp in the background.
RULES: German pronunciation, native speaker from southern Germany. Mouth matches every word. Steady
camera, same framing for the whole take. Speech ends on the last word, then a relaxed half smile.
```

Command:

```bash
python3 .claude/skills/video-gen/scripts/vg.py submit h3 --prompt-file templates/A_teaser/prompts/s3.md --dur 8 \
  --first-frame input/refs/presenter_A.png --slot templates/A_teaser/s3
```
