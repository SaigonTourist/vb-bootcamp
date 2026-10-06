# Seedance · b-roll and scenes from references

Use for: illustrative b-roll without recognisable faces (hands, rooms, objects, people from behind
or far away), scenes assembled from several reference images, long takes up to 30 s.

## Rules

1. **Action first.** The first sentence is what physically happens. Rules at the end, few, positive.
2. **Every shot is a fresh start.** There is no "as before". Restate place, light and blocking in
   full in every prompt.
3. **No edit verbs.** add, remove, replace, extend, continue make Seedance treat the job as a video
   edit and the call fails (TaskTypeConstraint).
4. **No readable surfaces in close-up.** Screens, forms, notebooks and calculators come out as
   scribbles. Keep them turned away, far, or out of focus; put the real text on top in the edit.
5. **Faces belong on H3.** Seedance may reject reference images that show a person, and close
   faces are not its strength here.
6. **Smiles, not laughs.** Acted laughter looks uncomfortable.

## Skeleton

```
ACTION: {one concrete physical action from start to finish, with the final state}.
SHOT: {framing}, {lens}, {camera movement in centimetres or a slow speed}.
PLACE: {location with three concrete elements, the same words in every shot of the series}.
LIGHT: one soft key from {direction}, about 4:1, {practicals}.
SOUND: {room tone, one or two specific sounds}.
```

## Example (template A, slot s2)

```
ACTION: two hands place two white ceramic cups of coffee on a round oak table, one on each side,
then one hand turns a cup so its handle points toward the empty chair opposite.
SHOT: close shot from slightly above, 50mm lens, very slow push of a few centimetres.
PLACE: a quiet advisory room, pale oak table, a tall olive tree out of focus in the background,
morning light through tall windows.
LIGHT: one soft key from tall windows camera-left, about 4:1, warm pendant lamp above the table.
SOUND: quiet room tone, the soft knock of ceramic on wood.
```

Command:

```bash
python3 .claude/skills/video-gen/scripts/vg.py submit seedance --prompt-file templates/A_teaser/prompts/s2.md --dur 5 --slot templates/A_teaser/s2
```

## Several reference images

Seedance can build a scene from several images: a room, an object, a material. Through OpenRouter
the references arrive in the order given to `--ref`, and the prompt refers to them by that order.

- **Give each image one role, positively, by number:** "the room from image 1, the leather folder
  from image 2 lying closed on the table". Never leave the model to guess which image is what.
- **Only include an image when its content is in the shot.** An unused reference still leaks into
  the picture.
- **The image decides the pose.** If the folder must lie flat, image 2 shows it lying flat.
- **No people in reference images.** Seedance rejects them; people come from the prompt (from
  behind, at a distance) or the shot moves to H3.
- Each image at least 300 px per side, aspect between 0.4 and 2.5 (pad logos onto a square canvas).
- `--first-frame` overrides references: use one or the other.

```bash
python3 .claude/skills/video-gen/scripts/vg.py submit seedance --prompt-file shot.md --dur 6 \
  --ref input/refs/room.jpg input/refs/folder.jpg
```

```
ACTION: a hand sets the leather folder from image 2 down closed and flat on the round table in the
room from image 1, then slides it a few centimetres toward the empty chair.
SHOT: close shot from slightly above, 50mm lens, camera locked off.
PLACE: the room from image 1, morning light through its tall windows.
LIGHT: one soft key from the windows camera-left, about 4:1.
SOUND: quiet room tone, the soft slide of leather on wood.
```
