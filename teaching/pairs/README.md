# Before/after pairs

Seven pairs for the prompting block. The "before" is how most people write a prompt the first time:
one long sentence, mood adjectives, famous brands as shorthand, text they want on screen, "the same
woman from the previous video". The "after" is the same intent written with our method. Point at the
strategy the pair is named after, then let the room find the other differences.

Every pair here was watched before it was kept: the failure in each "before" is visible on screen.

| # | Pair | Engine | What the room sees | Say this |
|---|---|---|---|---|
| 1 | `01_light` | Veo Fast, 4 s, seed 21 | "Bright, cinematic, 8k, masterpiece" comes back as stock footage with a "BANK" sign and invented subtitles ("Tine gotwle too hout cany basimer.?") | Adjectives give nothing to execute; one light source with a direction does. |
| 2 | `02_brands` | Veo Fast, 4 s, seed 31 | "Apple commercial style" prints the Apple logo in the corner; "Ralph Lauren" embroiders the polo player | Name a brand and its logo gets drawn. Describe the look instead. |
| 3 | `03_closeup` | Veo Fast, 4 s, seed 41 | The same good news: a grimace in extreme close-up, joy in a medium shot | Big emotion in close-up turns into a grimace; tell it with distance. |
| 4 | `04_text` | Seedance 480p, 5 s | "Kreditvertrag" comes back as "Kredittract", the table mixes German and English, the numbers are invented; the "after" carries the real word as a title added in the edit | It reads right at a glance and wrong when you read it. A bank cannot ship a typo or fix one letter without a re-render. Text goes in the edit. |
| 5 | `05_consistency` | H3, 5 s, 2 takes per side | "The same woman from the previous video" gives two different women; one start frame gives the same woman twice | No shot remembers another. One frame, the same scene words, only the dialogue changes. **Play the sequence: the German is word for word.** |
| 6 | `06_idea` | Seedance 720p, 5 s | "Trust and security" gives a stock handshake; the cup turned toward the guest gives a moment | You cannot film an idea; you can film the small action that makes people feel it. |
| 7 | `07_draft` | Veo Fast vs Veo, 6 s, seed 11 | Draft 0.60 $ vs final 2.40 $, same prompt and seed | Find the shot on the cheap model, render it once on the good one. |

Pair 3 is controlled (only the shot distance changes); the others compare a real first attempt with
the method. The "after" of pair 6 is the clip rendered through ModelArk on 2 October.

## Talking points without a pair

These were tried and dropped: in our October 2026 tests the models handled the naive version well
enough that the "before" taught nothing. They stay in the talk, with the story of where they did bite.

- **Say what is there, not what is not.** A short list of prohibitions was obeyed. It bites in long,
  rule-heavy prompts: a COME prompt that was 70 to 83 % rules failed the same way on two engines.
- **One action per shot.** Veo turned a whole story in 6 s into a clean mini-ad with its own cuts:
  it looks fine, but the edit is the model's, not yours, and it cannot be cut apart.
- **The reference image decides the pose.** Here Seedance followed the sentence; with COME, the
  reference won five times in a row. Give the photo of the final pose and the question disappears.
- **A filler line for H3.** At 6 s H3 said the line and stopped; on longer takes it repeated the last
  word. A harmless "Also, ja." at the end costs nothing and gives the edit a clean cut.

The discarded material is in `_discarded/`.

## Making them

```bash
python3 scripts/make_pairs.py                plan and cost
python3 scripts/make_pairs.py --go           start frame first, then every video at once
python3 scripts/make_pairs.py --wait         collect; repeat until nothing is pending
python3 scripts/make_pairs.py --go --redo before after --only 03_closeup   after rewriting a prompt
python3 scripts/make_pairs.py --compose      pair.mp4 (side by side, muted) and sequence.mp4 (with sound)
```

Use `pair.mp4` to compare the picture and `sequence.mp4` (before, then after, full screen with
sound) whenever the audio matters. If a "before" ever comes out fine, regenerate it or drop the pair:
a lucky take teaches nothing.
