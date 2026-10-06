# Nano Banana Pro · start frames

Use for: the opening image of an H3 take (a presenter), a room or an object in exactly
the pose a video must start from. About 0.14 $ per image, back in under a minute.

```bash
python3 .claude/skills/video-gen/scripts/vg.py image --prompt-file <file> --out input/refs/<name>.png --ratio 16:9
```

## What makes a start frame work for video

1. **Frame it exactly as the video shot.** Same ratio (16:9), same shot size (mid-chest up for a
   medium shot), the subject in the centre third, some headroom. The video starts from this image;
   whatever is cropped out here does not exist.
2. **Mouth closed, neutral and friendly.** H3 animates speech from this face. An open mouth or a
   big smile in the frame becomes the first syllable.
3. **Real, not stock.** Describe a phone-camera photo: real skin with pores and a few freckles, no
   retouching, ordinary clothes described by material and colour. Stock-perfect faces read as fake
   once they move.
4. **A clip-on microphone** on the collar makes a talking-head take read as a recorded statement.
5. **The same light as the video prompt.** If the video prompt says "window light from camera
   left", so does the image. A mismatch makes the first second jump.
6. **No readable text anywhere** in the scene: plain folders, a blank wall, a turned-away screen.
7. **A real person works too.** A photo from the designer's material can be the start frame as it is,
   or the input to restage it (same face, new room or framing). Public figures are refused.

## Skeleton

```
A candid photo taken on a phone at eye level, 16:9: a fictional {woman/man} in {her/his} {age},
{hair}, {clothing by material and colour}, a tiny black clip-on microphone on the collar.
{She/He} {sits/stands} {where}, looking straight into the lens with a calm, friendly expression,
mouth closed. Behind {her/him}, softly out of focus: {two plain background elements}. One soft
window light from camera {left/right}, {practical} in the background, gentle shadow on the far
side of the face. Real skin texture with visible pores, no retouching. Framed from {mid-chest /
the waist} up, in the centre third of the frame.
```

## Variants of the same person

To put the same presenter in another scene or outfit, give the chosen image back as input and
describe only the change:

```bash
python3 .claude/skills/video-gen/scripts/vg.py image --in input/refs/presenter_B.png --out input/refs/presenter_B_window.png \
  --prompt "The same man, same face and hair, same shirt, now standing by a tall window in the same training room, same framing, mouth closed."
```

Make two or three candidates of a new presenter (a few cents each) and let the designer pick before
any video is generated on top of it.
