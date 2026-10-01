# Model guide

One page: which model for which job. Prices are OpenRouter list prices on 1 October 2026, in US
dollars as billed; `vg.py estimate` converts to euros. Check `vg.py models --live` before relying on
them.

| | MiniMax H3 | Google Veo 3.1 | Veo 3.1 Fast | ByteDance Seedance 2.5 | Nano Banana Pro |
|---|---|---|---|---|---|
| Key | `h3` | `veo` | `veo-fast` | `seedance` | `image` |
| Best at | People speaking to camera, lip sync in German and other languages; objects true to a photo | Cinematic realism, light, native sound | Drafts of a Veo shot | B-roll, multi-reference scenes, long takes | Start frames |
| Length | 5-15 s | 4, 6, 8 s | 4, 6, 8 s | 4-30 s | still image |
| Output | 2K, all ratios | 720p / 1080p / 4K, 16:9 or 9:16 | same | 480p / 720p, all ratios | any ratio |
| Sound | voice + lip sync + ambience | yes | yes | yes | no |
| Price | 0.13 $/s (+0.04 $ per reference image) | 0.40 $/s with sound | 0.10-0.12 $/s | about 0.23 $/s at 720p | 0.14 $/image |
| 8 s costs | ~1.04 $ | ~3.20 $ | ~0.96 $ | ~1.85 $ | |
| Render time | 4-13 min | 2-8 min | 1-4 min | 3-12 min | <1 min |
| Holds a person across shots | Yes, from one start frame | No | No | No (and rejects photos of people) | Yes, edits keep the face |
| Weak at | Lettering on surfaces; no seed | Brand names get drawn; faces in close-up | same | Text, numbers, faces | |

## Choosing in one question each

- **Does someone speak to camera?** H3, from a start frame made with Nano Banana Pro.
- **Is it the first or last image people see?** Veo, drafted on Veo Fast.
- **Is it hands, a room, a process, a crowd from behind?** Seedance.
- **Does an object have to look exactly like the real one?** H3 with the photo as reference.

## Things every model shares

- No model remembers another shot. Continuity comes from repeating the same words, the same start
  frame, the same light and lens.
- No model writes reliably. Text, numbers, screens and forms go on in the edit.
- What the prompt names, the model draws. Forbidding something names it.
- Render time is real time. Launch early, work on the next shot while it renders.
