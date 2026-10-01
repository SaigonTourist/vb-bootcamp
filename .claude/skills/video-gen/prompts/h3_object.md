# H3 · an object that has to look like the real thing

Use for: a product, a device, a branded item, a prop that must match a reference photo. H3 is more
faithful to reference images than Seedance.

## Rules that decide the result

- **The photo decides the pose.** If the object must lie flat, the reference shows it lying flat.
  The sentence will not overrule the photo.
- **A hand gives the scale.** An object alone in frame comes back at random size. A hand holding or
  placing it fixes the size.
- **Say where it ends up, positively.** "sets it down flat on its back on the table" works; "it
  does not stand up" invites it to stand up.
- **Exactly one.** Say "exactly one {object}" when the scene could tempt a duplicate.
- **References vs first frame:** with `--first-frame` the references are ignored. Use references
  when the object must appear inside a scene the model invents; use a first frame when you already
  have the exact opening image.

## Skeleton

```
SHOT: {framing}, {lens}, camera {locked off / slow push of a few centimetres}.
SCENE: {surface, room, two concrete objects}. One soft light from camera {side}, gentle shadow.
ACTION: a hand {enters from the right, holds / turns / sets down} exactly one {object, as in the
reference image}, {final position stated positively}.
OBJECT: the {object} matches the reference image in shape, colour and proportions; the hand shows
its real size.
RULES: steady camera, real-world physics, the {object} stays in frame to the end.
```

## Example

```
SHOT: close shot from slightly above, 50mm lens, camera locked off.
SCENE: a light oak desk by a window, a ceramic mug and a closed leather folder at the edge of the
frame. One soft window light from camera left, gentle shadow to the right.
ACTION: a hand enters from the right and sets exactly one bank card, as in the reference image,
flat on its back in the centre of the desk, then slides it a few centimetres toward the camera
and withdraws.
OBJECT: the card matches the reference image in shape, colour and proportions; the hand shows its
real size.
RULES: steady camera, real-world physics, the card stays in frame to the end.
```

Card numbers and names will come out as scribbles. Use a reference with a plain front, or keep the
card face-down.
