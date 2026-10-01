# Veo · a cinematic shot

Use for: openers, establishing shots, a mood, a short spoken line by someone who appears once.
16:9 at 1080p, native sound, 4, 6 or 8 seconds.

**Draft on `veo-fast` with a fixed `--seed`, then render the keeper on `veo` with the same seed.**
Fast costs about a quarter.

## Five rules learned the expensive way

1. **What you name, Veo draws.** `negativePrompt` does not stop it. "Shot on a [camera brand]"
   printed the brand in the corner; "polo shirt" came back with an embroidered logo. Describe the
   thing without its name: "cotton piqué shirt with a small folded collar".
2. **A SHOT: line on every prompt, medium shot or wider for people.** Without it Veo pushes into
   faces, and energetic close-ups turn into grimaces.
3. **Light is a source, a direction and a ratio.** "Bright, white walls, big windows" comes back
   washed out. "One soft key from a tall window camera-left an hour before sunset, about 4:1, warm
   practicals in the background, expose to protect the highlights" comes back like film.
4. **Technical spec, not defects.** Sensor size, focal length, aperture, frame rate and support
   give realism. Asking for grain, aberration or wobble gives dirt on the image.
5. **No face continuity between calls.** If several people speak across shots, each shot
   describes its own person in full. Continuity comes from the room, the light and the lens.

## Skeleton

```
SHOT: {wide / medium / medium-wide}, {eye level / slightly low}, {lens}mm at T{2}, {static / slow
dolly in / slow lateral track}, 25 fps, shoulder-free.
SUBJECT AND ACTION: {who or what, doing one concrete physical thing, from start to end of the shot}.
PLACE: {one location, three concrete elements}.
LIGHT: one {soft / hard} key from {direction} {time of day}, about {4}:1, {practicals}, expose to
protect the highlights.
COLOUR: {restrained palette in words}, natural skin, no glow.
SOUND: {room tone and two specific sounds}. {Dialogue in quotes, if any.}
```

## Example (template A, slot s1)

```
SHOT: medium-wide, eye level, 35mm at T2, slow dolly in of about half a metre, 25 fps.
SUBJECT AND ACTION: a man in his fifties in a grey wool jacket opens a glass door, steps into a
quiet modern advisory room, and pauses with one hand still on the door handle, looking toward a
round table where two cups are already waiting.
PLACE: pale oak floor, a round table with two chairs, a tall olive tree in a ceramic pot.
LIGHT: one soft key from tall windows camera-left in the early morning, about 4:1, a warm pendant
lamp above the table, expose to protect the highlights.
COLOUR: muted warm neutrals, deep green of the plant, natural skin, no glow.
SOUND: quiet room tone, the soft click of the door, distant street sounds through the glass.
```

Command (draft, then final):

```bash
python3 .claude/skills/video-gen/scripts/vg.py submit veo-fast --prompt-file templates/A_teaser/prompts/s1.md --dur 6 --seed 11 --label A_s1_draft
python3 .claude/skills/video-gen/scripts/vg.py submit veo --prompt-file templates/A_teaser/prompts/s1.md --dur 6 --seed 11 --slot templates/A_teaser/s1
```
