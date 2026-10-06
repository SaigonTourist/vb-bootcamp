# From an idea to a prompt

Designers arrive with an idea, not a prompt: "something that shows trust in the advisory
conversation", "our trainer explaining the new module". Claude's job is to turn that into one prompt
per shot, each written for its engine, and to show the designer what changed and why. That last
part is how the team learns the craft.

## The procedure

**1. Find the filmable action.** Models film actions, not ideas. "Trust", "security" and
"Vertrauen" cannot be filmed; "she slides the cup toward him by its handle" can. For every abstract
word in the idea, ask: what would a camera see that makes a viewer feel this? Pick one concrete,
physical, everyday action. Small and specific beats big and symbolic (no handshakes in front of
sunsets, no lightbulbs, no puzzles).

**2. Split into shots and pick the engine for each.** In templates A, B and C the engine of each slot is already fixed by its shotlist: keep it, so the engines can be compared. One shot is one action in one place, 4 to 15 s.

| The shot shows | Engine |
|---|---|
| Someone speaking to camera | `h3`, with a start frame from `vg.py image` |
| Two people talking to each other, one short line | `veo` (one 8 s shot), or two `h3` takes cut together |
| The first or last image of the piece, a place, a mood | `veo` (draft on `veo-fast`) |
| Hands, objects, rooms, people from behind, a process | `seedance` |
| A specific object that must look real | `h3` with the photo as reference |

**3. Fill the gaps with defaults instead of questions.** The idea rarely says framing, lens, light,
sound or length. Use these unless the designer said otherwise, and list them so they can change any:

- 16:9; medium shot for people, close shot from slightly above for hands and objects
- 35mm lens for people, 50mm for objects; camera on a tripod or a slow move of centimetres
- one soft window light from the left, about 4:1, a warm lamp in the background
- quiet room tone plus one specific sound that belongs to the action
- 6 s for b-roll, 8 s for a spoken line, 15 s maximum per take

Ask a question only when the answer changes the engine or the cost: "Does someone speak on camera?"
or "Is this the opening shot?"

**4. Write the prompt from the engine's template** in `.claude/skills/video-gen/prompts/`, then run
`vg.py lint`. Fix every warning before showing it.

**5. Show the designer three things, briefly:**
- the engine and why, in one line
- the prompt
- what you changed from their idea, one line per change, with the reason

Then the estimate, then wait for a go. When they edit the prompt, keep their edit and only re-lint.

**6. After the render, diagnose before retrying.** Name what is wrong in one word (framing,
physics, identity, lettering, audio, timing), change the one sentence responsible, say which.

## Worked examples

### 1. "Something that shows trust in the advisory conversation"

Abstract idea, no person speaking, so this is b-roll. Trust becomes an action: someone prepares the
table for the other person before they arrive.

- Engine: `seedance`, hands and objects, no faces.

```
ACTION: two hands place two white ceramic cups of coffee on a round oak table, one on each side,
then one hand turns a cup so its handle points toward the empty chair opposite.
SHOT: close shot from slightly above, 50mm lens, very slow push of a few centimetres.
PLACE: a quiet advisory room, pale oak table, a tall olive tree out of focus in the background,
morning light through tall windows.
LIGHT: one soft key from tall windows camera-left, about 4:1, warm pendant lamp above the table.
SOUND: quiet room tone, the soft knock of ceramic on wood.
```

What changed: "trust" became the cup turned toward the guest (filmable, small, human); no faces, so
Seedance; no handshake (cliché, and hands meeting is hard physics); light and sound defaults added.

### 2. "Our trainer explains the new compliance module, in German, short"

Someone speaks to camera: H3, from a fictional start frame. The idea had a date in it ("starting
15 October"); that goes on a card, not in the voice.

Step one, the start frame (`prompts/image_start_frame.md`), then:

```
SHOT: medium shot, eye level, camera locked off on a tripod, 35mm lens, as in the start frame.
ACTION: the man looks straight into the lens and speaks in German, warm and direct, at a natural
pace, a small open-hand gesture on the word in capitals.
DIALOGUE: "Das neue Compliance-Modul dauert eine Viertelstunde und spart Ihnen später viel ÄRGER. Also, ja."
SCENE: he stands leaning lightly against a tall table in a training room, light blue shirt with
sleeves rolled once. One soft window light from camera right, warm lamp in the background.
RULES: German pronunciation, native speaker from Austria. Mouth matches every word. Steady camera,
same framing for the whole take. Speech ends on the last word, then a short friendly nod.
```

What changed: the start date moved to the end card (spoken, it expires); 14 words for 8 s (German
runs at about 2 words per second); "Also, ja." added as a filler the edit cuts, because H3 talks to
the end of the clip; one word in capitals for emphasis.

### 3. "Show the warning signs of money laundering"

The idea invites screens with transactions on them, which no model can render legibly. Keep the
human moment, put the information in text on top.

- Engine: `veo`, a single attentive moment at final quality.

```
SHOT: medium shot, eye level, 50mm at T2, static, 25 fps.
SUBJECT AND ACTION: a woman in her forties in a dark green cardigan sits at a desk, reading; she
stops, leans back slightly, takes off her glasses and looks thoughtfully toward a closed office door.
PLACE: a quiet back office, a desk lamp, a window with blinds half closed.
LIGHT: one warm desk lamp camera-right as key, cool daylight through the blinds behind her, about 5:1.
COLOUR: muted greens and warm skin, deep shadows kept.
SOUND: office room tone, a clock ticking softly, the click of the glasses folding.
```

What changed: the screen is gone (it would come out as scribbles); the warning sign is shown as her
reaction, and the actual red flags go on screen as captions in the edit; no "suspicious" or "money"
in the prompt, which would invite clichés (stacks of cash, shady figures).

### 4. "A busy branch in the morning"

"Busy" is a mood; turn it into countable activity. Many small people, no faces in close-up: Seedance.

```
ACTION: in an open branch hall, six or seven people move calmly in different directions: a
man in a coat walks in through the glass door, two colleagues cross with folders under their arms,
a woman waits by a tall plant and checks her watch.
SHOT: wide, slightly high angle, 28mm lens, very slow lateral move of about half a metre.
PLACE: pale stone floor, tall glass facade, round wooden tables with two chairs each, potted trees.
LIGHT: low morning sun from camera-left through the glass, about 4:1, long soft shadows on the floor.
SOUND: hall room tone, footsteps on stone, the soft swish of the automatic door.
```

What changed: "busy" became a counted set of actions; wide and high so no face is close; no logos
or signage named (the bank's real branding goes on in the edit if needed).

### 5. "Two colleagues discuss a difficult client case"

Two people, one exchange. Veo can hold two speakers in one 8 s shot if the lines are short and each
speaker is described so the model knows who says what.

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

What changed: the "difficult case" stays unnamed (no client data, and a generic line is reusable);
two short lines, 11 words in total for 8 s; each speaker described by clothing and position so the
voices land on the right person. For a longer exchange, use two H3 takes (one start frame per
person) and cut between them.

## A retry, done properly

Example 1 came back with the cup lifted and put down twice. Diagnosis: **physics**, the action
was read as a loop. One change: "then one hand turns a cup" becomes "then one hand turns one cup a
quarter turn and rests beside it". Nothing else changes, so the next take tells us whether that
sentence was the cause.
