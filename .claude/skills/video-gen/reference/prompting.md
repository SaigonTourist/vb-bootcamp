# The prompt contract

Learned over several hundred paid generations across Veo, Seedance and H3. The same failures showed
up in different models for the same reason: the prompt, not the model.

## 1. Action first

The first sentence says what physically happens, from start to end. Framing comes with it. Rules
come last, few and positive.

A prompt that was 80 % rules, with the action starting at word 300, failed the same way on two
different models. Put back in order, the same scenes passed.

## 2. Say what is there, not what is not

| Instead of | Write |
|---|---|
| "The card must not stand up, never upright" | "sets the card down flat on its back" |
| "No text on the screen, no logo" | "the laptop faces away from the camera" |
| "Gregor is NOT in this shot" | Do not mention Gregor at all |
| "Don't laugh too much" | "a short, warm smile" |

## 3. Technical specification, not mood

| Instead of | Write |
|---|---|
| "cinematic, beautiful lighting" | "one soft key from a tall window camera-left, about 4:1, warm lamp in the background" |
| "bright modern office" | "pale oak floor, tall glass facade, morning sun from the left, long soft shadows" |
| "shot on a [camera brand]" | "full-frame sensor, 35mm at T2, 25 fps, tripod" |
| "close-up, high energy" | "medium shot, eye level, she leans forward slightly on the key word" |

## 4. No names of brands, products or people

The model draws every name it reads, logos included, and negative prompts do not stop it. Describe
the object by shape, material and colour. Real logos and product names go on in the edit.

## 5. Every shot stands alone

Restate the place, the light, the clothing and the position in every prompt. "As before" has no
meaning to a model that never saw "before". For a recurring presenter, reuse the same start frame
and copy the same SHOT, SCENE and RULES text word for word.

## 6. Spoken text is permanent, on-screen text is free

Anything that changes (a date, a rate, a price, a deadline, a count of places) goes on a card or a
caption. Spoken, it ties the clip to one week. Write the line so it is true any week: "ab Montag"
instead of a date, "jetzt im Lernportal" instead of "bis Freitag".

## 7. One change per retry

When a take fails, name the failure (framing, physics, identity, lettering, audio), change the one
sentence responsible, and say what you changed. Two changes at once teach nothing.

`vg.py lint` checks most of this automatically.
