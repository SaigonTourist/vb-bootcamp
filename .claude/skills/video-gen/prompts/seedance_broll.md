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
5. **Faces belong on H3.** Seedance rejects reference images that may show a real person, and close
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
