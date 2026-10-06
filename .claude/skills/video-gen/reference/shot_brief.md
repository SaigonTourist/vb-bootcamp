# How to ask Claude for a shot

You do not write prompts for the video models. Claude does. What decides the quality is what you
give Claude: a vague wish gets a generic stock shot; a brief with the right details gets a shot you
can use. These are the details that matter, in the order Claude needs them.

## The shot card

| # | Tell Claude | Example | Why it matters |
|---|---|---|---|
| 1 | **What the viewer should take away** from this shot, in one sentence | "That the advisor prepares for the client, before they arrive." | Claude turns it into something a camera can see. A feeling alone ("trust") gets a stock handshake. |
| 2 | **The one thing that happens**, start to end | "She places two cups and turns one handle toward the empty chair." | One shot holds one action. A whole story in one shot comes back as the model's own edit. |
| 3 | **Who is in it** (a description, or a photo of the real person), and whether it is the same person as in another shot | "Our trainer, photo trainer.jpg. Same presenter as slot s3." | Same person across shots needs a start frame. Nothing gets carried over by itself. |
| 4 | **How close the camera is** | "Wide, we see the whole room." / "Medium, waist up." | Close-ups of emotional faces turn into grimaces. Medium or wider for people. |
| 5 | **Where** it happens, with two or three real details | "Our advisory room: round oak table, tall plant, window on the left." | Concrete things beat adjectives. "Modern office" gets a stock office. |
| 6 | **The light and the time of day** | "Grey morning, light from the window, a lamp on." | "Bright and cinematic" comes back glossy and fake. A light source with a direction looks filmed. |
| 7 | **The sound**: who speaks, the exact words, in which language, or only room sound | "Only her, in German: 'Ein gutes Gespräch beginnt mit einer Frage.'" | Without words the model invents dialogue, often in English, sometimes in the wrong mouth. |
| 8 | **Any words that must appear on screen** | "The module title: Das gute Gespräch." | They go in the edit, where they are spelled right and can be changed. Models misspell. |
| 9 | **Length and format** | "6 seconds, 16:9." | Each model has fixed lengths; Claude picks the nearest. |

You do not have to fill everything. Give 1, 2 and 7 at least; Claude fills the rest with sensible
defaults and shows you what it assumed. Change any of it in plain words.

**Leave out:** brand and product names (they get drawn as logos), dates, prices and deadlines in the
voice (they expire; they go on screen), "no X" lists
(say what is there instead).

## A brief, before and after

> Make a video of a happy customer at our bank, cinematic, modern.

> Slot s2 of template A. The viewer should feel the advisor got ready for the client. Hands only:
> two cups placed on a round oak table, one handle turned toward the empty chair. Close, from slightly
> above. Morning light from a window on the left. Room sound and the knock of the cups, no voice.
> 5 seconds.

Same model, same cost. The second one is usable.

## When a take comes back wrong

Say **what** is wrong in one word, **where** (the second), and **what to keep**. Claude changes one
thing and tells you which.

| Word | What you saw | You say, for example |
|---|---|---|
| Framing | Too close, too far, wrong angle | "At 2 s it cuts her head off. Keep the action, a bit wider." |
| Action | It did something else, or too much | "She should only nod, not stand up." |
| Physics | Hands, objects or bodies behave wrong | "The cup passes through her hand at 3 s." |
| Person | Different face, or looks into the lens | "She looks into the camera; she should look at her colleague." |
| Text | Letters or numbers on things | "The paper has fake writing; keep it blank." |
| Sound | Wrong words, wrong voice, wrong language | "The woman says his line; only he speaks." |
| Look | Glossy, too bright, looks fake | "Too shiny. Make it greyer and more natural." |

Avoid "make it better" or "try again": a blind retry costs the same and teaches nothing.
