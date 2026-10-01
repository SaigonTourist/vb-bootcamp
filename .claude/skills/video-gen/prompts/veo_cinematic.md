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

## Dialogue in Veo

Veo speaks German too, with one or two short lines per shot. H3 is the better choice for a
presenter to camera; Veo is for a line spoken inside a scene, or a short exchange between two people.

- **Attribute every line** to a person described by clothing and position:
  `The woman in the grey blazer says in German: "..."`. Without that, voices land on the wrong face.
- **Short.** 8 s holds about 12 to 15 German words in total. One line per speaker.
- **Medium or medium-wide two-shot**, both faces visible, camera static.
- **No continuity of faces between calls**, so a conversation longer than one shot is two H3 takes
  (one start frame per person) cut together, not several Veo calls.
- If burned-in subtitles appear, add them to the safety net: `--negative "subtitles, captions, on-screen text"`.

```
SHOT: medium two-shot, eye level, 35mm at T2.8, static, 25 fps.
SUBJECT AND ACTION: at a tall table, a younger man in a white shirt turns to an older woman in a
grey blazer and asks his question; she answers calmly, with a small reassuring nod.
DIALOGUE: The man says in German: "Wie würden Sie das ansprechen?" The woman answers in German:
"Ehrlich. Und mit einer guten Frage."
PLACE: a small meeting corner, frosted glass wall behind them, a plant at the edge of frame.
LIGHT: one soft key from a window camera-left, about 4:1, warm practical lamp in the background.
SOUND: quiet office room tone, their voices close and natural.
```
