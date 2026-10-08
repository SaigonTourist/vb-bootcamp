#!/usr/bin/env python3
"""YouTube Short "Ein Tag als Legionär" (9:16, ~60 s): the whole plan in one file.

  short.py prompts     write every image and animation prompt to prompts/
  short.py vo          narrate every VO segment (ElevenLabs via OpenRouter) into audio/
  short.py music       generate the music bed (Lyria via OpenRouter) into audio/
  short.py timeline    print scene timings computed from the VO
  short.py build       cut clips + VO + music + SFX + captions + overlays into out/D_legionaer_short.mp4
  short.py package     write PAKET.md (prompts, VO script, SRT, overlays, sound list, cut plan, titles)
"""
import base64, json, os, subprocess, sys, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = REPO / "out"
W, H, FPS = 1080, 1920, 25

STYLE = (
    "STYLE: humorous 2D history-explainer cartoon style: characters with large perfectly round pure-white heads "
    "and white hands, very thick dark brown-black outlines on everything, minimal faces made of short thick black "
    "brush strokes: narrow half-lidded eyes, heavy angled eyebrows, small wavy frowning mouths, deadpan, grumpy and "
    "unimpressed expressions as the default, simple rounded bodies with flat colours and soft cel shading, hair as "
    "one solid shape with a few inner lines, detailed painted backgrounds in warm muted tones (ochre, terracotta red, "
    "mustard yellow, warm brown wood) with clear perspective and architectural detail, subtle texture, gentle "
    "vignette, comedic timing through held poses and slow eyebrow movements. No speech bubbles, no written text, "
    "no letters or numbers inside the image."
)

GAIUS = (
    "GAIUS: a young Roman legionary around 110 AD, slim, round pure-white head, short dark-brown hair as one solid "
    "shape with a small fringe, narrow half-lidded eyes, heavy angled dark eyebrows, a small wavy frown. Full kit: "
    "knee-length red wool tunic, grey segmented iron plate armour over chest and shoulders, plain iron helmet with "
    "cheek guards and a neck guard, short sword in a scabbard on his right hip, large curved rectangular red shield "
    "with a plain yellow rim, brown leather hobnailed sandal-boots. In the tent and at meals he wears only the red "
    "tunic, no armour and no helmet."
)
MAXIMUS = (
    "MAXIMUS: the centurion, a head taller and much broader than Gaius, round pure-white head, thick black eyebrows "
    "angled sharply down, a short black stubble beard drawn as a few short strokes, polished silver-grey helmet with "
    "a transverse red horsehair crest that runs across the helmet from his left ear over the top to his right "
    "ear, so seen from the front it is a wide red half-circle fan, silver-grey mail shirt, red cloak over one shoulder, greaves on his shins, and "
    "always a knotted brown vine-wood staff in his right hand."
)
SQUAD = (
    "THE SQUAD: seven other legionaries who share Gaius' tent, same round pure-white heads and the same red "
    "tunics, each with a different simple hair shape (bald, curly black, ginger, grey, spiky), all deadpan; one of "
    "them is big and round and always asleep with his mouth open."
)

LIGHT = {
    "morning": "LIGHT: early morning, low orange sunrise light from the left, long soft shadows, warm orange sky.",
    "day": "LIGHT: grey rainy day, flat cool grey overcast light, light rain, wet ground, muted colours.",
    "evening": "LIGHT: warm evening, golden-orange light from an oil lamp or a campfire, cosy warm shadows.",
    "night": "LIGHT: night, deep blue moonlight, one flickering orange torch as the only warm light.",
}

COMPOSE = ("COMPOSITION: one single full-bleed illustration that fills the whole tall vertical 9:16 frame from edge "
           "to edge: the painted scene continues upward into sky, tent roof or wooden beams and downward into ground "
           "or floor; the characters sit in the middle third.")

# Each scene: frame (image prompt), anim (Veo prompt), sfx, vo segments [(text, punch, [highlight words])],
# overlay text, gen duration of the clip, who appears.
SCENES = [
    dict(id="s1", light="morning", who=["gaius", "squad"], dur=6,
         frame="Inside a cramped brown leather army tent at dawn. Gaius, only in his red tunic, lies on his back on a "
               "straw mat, seen from slightly above, eyes wide open, staring straight up, deadpan. Right next to his "
               "face, in the left edge of the frame, sticks the bare dusty foot of a sleeping comrade. Morning light "
               "falls through the open tent flap.",
         camera="medium shot from slightly above, very slow push-in toward Gaius' face",
         action="A distant brass horn call sounds. Gaius' eyes snap open, then his heavy eyebrows slowly sink into "
                "a grumpy frown. The foot next to his face wiggles its toes once. Gentle parallax on the tent folds.",
         sfx="a long low brass horn call from outside the tent, then one loud snore",
         vo=[("Du wolltest Ruhm.", False, ["Ruhm."]), ("Du bekommst: einen Fuß im Gesicht.", True, ["Fuß"])],
         overlay=""),
    dict(id="s2", light="morning", who=["gaius", "squad"], dur=6,
         frame="Wide view of the inside of the sloping brown leather tent: eight legionaries in red tunics lie "
               "squeezed shoulder to shoulder on straw mats, cloaks and helmets hanging from the tent poles. Gaius "
               "lies squeezed in the middle with his arms crossed, grumpy. The big round comrade next to him sleeps "
               "with his mouth wide open.",
         camera="wide shot, eye level, slow pull back that reveals the whole crowded tent",
         action="The big comrade's belly rises and falls with each snore, the tent wall flutters with it. Gaius "
                "blinks once, very slowly, and does not move.",
         sfx="loud rhythmic snoring, creaking leather, a rope straining",
         vo=[("Acht Männer. Ein Zelt.", False, ["Acht", "Ein"]), ("Einer schnarcht immer.", True, ["immer."])],
         overlay="8 Männer · 1 Zelt"),
    dict(id="s3", light="morning", who=["gaius"], dur=6,
         frame="Outside the tent in the camp at sunrise. Gaius, only in his red tunic, sits on a wooden stool next to "
               "a small round stone hand mill full of grain, holding a plain clay cup in one hand. Rows of leather "
               "tents and campfire smoke behind him.",
         camera="medium shot, eye level, static, slight parallax in the background smoke",
         action="Gaius lifts the clay cup and takes one sip. He freezes. His mouth slowly curls into a sour wavy line "
                "and his eyebrows slowly rise, then he lowers the cup and stares into the camera.",
         sfx="a stone mill grinding, a single sip, a small reluctant swallow",
         vo=[("Frühstück: Getreide. Dazu Posca.", False, ["Posca."]), ("Wasser mit Essig. Prost.", True, ["Essig."])],
         overlay="Posca = Wasser + Essig"),
    dict(id="s4", light="morning", who=["gaius", "maximus"], dur=6,
         frame="A muddy parade ground in the camp at sunrise. Maximus the centurion stands in the foreground on the "
               "right, slowly tapping his knotted vine-wood staff into his open left palm. Behind him on the left, "
               "Gaius stands stiffly in full armour in the front row of a line of legionaries, eyes nervously turned "
               "sideways toward the staff.",
         camera="medium-wide shot, slightly low angle on Maximus, static",
         action="Maximus taps the vine-wood staff into his palm twice, slowly. On the second tap Gaius straightens "
                "up even more and his eyebrows jump. The legionaries in the line behind stand still, shields steady, every iron helmet stays on every head for the whole shot.",
         sfx="two dry wooden taps on a leather glove, wind over the parade ground",
         vo=[("Centurio Maximus. Sein Rebstock: Rangabzeichen.", False, ["Rebstock:"]), ("Und ein Argument.", True, ["Argument."])],
         overlay=""),
    dict(id="s5", light="day", who=["gaius"], dur=6,
         frame="On a muddy road out of the camp on a grey rainy day. Gaius in full armour carries a long wooden "
               "carrying pole over his left shoulder, heavily loaded: a bronze cooking pot, a leather bag, a rolled "
               "cloak, a small shovel and a net bag, all dangling. He leans forward under the weight, knees slightly "
               "bent, deadpan.",
         camera="medium-wide shot, eye level, side view, slow lateral track with him",
         action="Gaius takes two heavy steps forward, the pot and the shovel swing and clank, he lets out a long sigh "
                "and his shoulders sink a little lower.",
         sfx="metal clanking, heavy squelching footsteps in mud, one long sigh",
         vo=[("Dein Gepäck trägst du selbst. Spitzname:", False, ["selbst."]), ("Marius' Maultiere.", True, ["Maultiere."])],
         overlay="ca. 30 kg"),
    dict(id="s6", light="day", who=["gaius", "squad"], dur=6,
         frame="A long column of legionaries in full armour marches toward the camera on a straight paved road "
               "through green hills in grey rain. Gaius marches in the front row in the middle, soaked, water "
               "dripping from his helmet rim, deadpan.",
         camera="medium-wide shot, eye level, the camera moves backward at walking pace in front of the column",
         action="The column marches steadily in step, the hills slide past in slow parallax, rain streaks down. "
                "Gaius keeps marching and slowly lifts his eyebrows at the sky.",
         sfx="steady rain, rhythmic hobnailed footsteps on stone, armour jingling",
         vo=[("20 römische Meilen. In 5 Stunden.", False, ["20", "5"]), ("Im Regen.", True, ["Regen."])],
         overlay="bis zu 30 km"),
    dict(id="s7", light="evening", who=["gaius", "squad"], dur=6,
         frame="At sunset at the edge of a field, legionaries in red tunics dig a deep ditch and pile the earth into "
               "a wall, a row of sharpened wooden stakes half built on top. Gaius stands waist-deep in the ditch "
               "with a shovel, dirt on his face, staring at the camera, deadpan.",
         camera="medium shot, eye level, static",
         action="Gaius throws a shovel of earth over his shoulder without looking, then stares into the camera. "
                "Behind him others keep digging. Gaius keeps his iron helmet on and his face stays exactly the same character for the whole shot.",
         sfx="shovels biting into earth, clods of earth thudding",
         vo=[("Am Ziel: ein befestigtes Lager bauen.", False, ["Lager"]), ("Jeden. Einzelnen. Abend.", True, ["Jeden.", "Einzelnen.", "Abend."])],
         overlay="JEDEN Abend"),
    dict(id="s8", light="day", who=["gaius", "maximus"], dur=6,
         frame="A training field on a grey day. Gaius in full armour holds a thick clumsy wooden practice sword and a "
               "heavy woven wicker shield in front of a tall wooden post. Maximus stands to the side with his arms "
               "crossed and his vine-wood staff under his arm, unimpressed.",
         camera="medium-wide shot, eye level, static",
         action="Gaius heaves the heavy wooden sword up, swings slowly at the post, the sword drags him half a step "
                "sideways. Maximus slowly raises one eyebrow.",
         sfx="a heavy dull wooden thud, a strained grunt without words",
         vo=[("Übungswaffen? Absichtlich schwerer als echte.", False, ["schwerer"]), ("Danke, Maximus.", True, ["Maximus."])],
         overlay=""),
    dict(id="s9", light="evening", who=["gaius", "maximus"], dur=6,
         frame="Inside a wooden camp office lit by an oil lamp. Across a plain wooden table, Maximus pushes a small "
               "pile of plain round silver coins toward Gaius, who sits in his red tunic, looking hopeful for once. "
               "No marks or symbols on the coins.",
         camera="medium shot, eye level, static",
         action="With the tip of his vine-wood staff, Maximus slowly slides one coin back to his side, then a second, "
                "then a third. With each coin Gaius' eyebrows sink lower.",
         sfx="coins clinking on wood, three slow sliding scrapes",
         vo=[("Zahltag! Minus Essen. Minus Ausrüstung. Minus Begräbniskasse.", False, ["Zahltag!", "Essen.", "Ausrüstung.", "Begräbniskasse."]), ("Beruhigend.", True, ["Beruhigend."])],
         overlay="Sold − Abzüge"),
    dict(id="s10", light="evening", who=["gaius", "squad"], dur=6,
         frame="Inside the leather tent in the evening, lit by one small oil lamp. The eight tent mates in red tunics "
               "sit in a circle around a big pot of grey grain porridge, each with a wooden bowl. Gaius in the middle "
               "holds his spoon up and stares at the porridge on it, deadpan.",
         camera="medium shot, eye level, slow push-in on Gaius",
         action="A thick glob of porridge slowly slides off Gaius' spoon and drops back into the bowl. He blinks "
                "once, slowly.",
         sfx="a thick wet plop, an oil lamp crackling, quiet spoon scrapes",
         vo=[("Gaius denkt an Rom.", False, ["Rom."]), ("Rom denkt nicht an Gaius.", True, ["nicht"])],
         overlay=""),
    dict(id="s11", light="night", who=["gaius"], dur=6,
         frame="Night on the wooden walkway behind the camp's stake wall. Gaius in full armour stands guard holding "
               "a tall spear, a burning torch beside him, starry deep-blue sky behind. His eyes are forced extremely "
               "wide open.",
         camera="medium shot, eye level, very slow push-in",
         action="Gaius' eyelids slowly droop halfway, his head dips, then his eyes snap wide open again and he "
                "stands rigidly straight. The torch flame flickers gently and keeps the same small size.",
         sfx="crickets, a crackling torch, a slow heavy heartbeat",
         vo=[("Nachtwache. Wer einschläft, wird von Kameraden erschlagen.", False, ["einschläft,", "erschlagen."]), ("Gaius ist sehr wach.", True, ["wach."])],
         overlay=""),
    dict(id="s12", light="morning", who=["gaius", "squad"], dur=6,
         frame="Inside the cramped brown leather army tent at dawn, the same place as before. Gaius, only in his red "
               "tunic, lies on his straw mat and turns his head to stare straight into the camera with total deadpan "
               "resignation. The bare dusty foot of a sleeping comrade sticks in from the left edge right next to "
               "his face.",
         camera="medium shot from slightly above, static",
         action="Gaius holds his stare into the camera, motionless, only one slow blink. At the very end a brass horn "
                "call sounds from outside and his eyebrows twitch.",
         sfx="silence, one snore, then at the very end a long low brass horn call",
         vo=[("Und das Ganze?", False, []), ("25 Jahre lang.", True, ["25", "Jahre"])],
         overlay="25 Jahre Dienstzeit"),
]

# English version: same pictures, new narration and overlays.  SHORT_LANG=en short.py …
EN = {
    "s1": ([("You wanted glory.", False, ["glory."]), ("You got: a foot in the face.", True, ["foot"])], ""),
    "s2": ([("Eight men. One tent.", False, ["Eight", "One"]), ("One always snores.", True, ["snores."])],
           "8 men · 1 tent"),
    "s3": ([("Breakfast: grain. Plus posca.", False, ["posca."]), ("Water with vinegar. Cheers.", True, ["vinegar."])],
           "Posca = water + vinegar"),
    "s4": ([("Centurion Maximus. His vine staff: a badge of rank.", False, ["vine", "staff:"]),
            ("And an argument.", True, ["argument."])], ""),
    "s5": ([("You carry your own pack. Nickname:", False, ["own"]), ("Marius' mules.", True, ["mules."])],
           "approx. 30 kg"),
    "s6": ([("20 Roman miles. In 5 hours.", False, ["20", "5"]), ("In the rain.", True, ["rain."])], "up to 30 km"),
    "s7": ([("After the march: build a fortified camp.", False, ["camp."]),
            ("Every... single... evening.", True, ["Every...", "single...", "evening."])], "EVERY evening"),
    "s8": ([("Training weapons? Deliberately heavier than real ones.", False, ["heavier"]),
            ("Thanks, Maximus.", True, ["Maximus."])], ""),
    "s9": ([("Payday! Minus food. Minus gear. Minus burial fund.", False,
             ["Payday!", "food.", "gear.", "burial", "fund."]), ("Reassuring.", True, ["Reassuring."])],
           "Pay − deductions"),
    "s10": ([("Gaius thinks of Rome.", False, ["Rome."]), ("Rome does not think of Gaius.", True, ["not"])], ""),
    "s11": ([("Night watch. Fall asleep, and your comrades beat you to death.", False, ["asleep,", "death."]),
             ("Gaius is very awake.", True, ["awake."])], ""),
    "s12": ([("And all of this?", False, []), ("For 25 years.", True, ["25", "years."])], "25 years of service"),
}
LANG = os.environ.get("SHORT_LANG", "de")
SUF = "" if LANG == "de" else f"_{LANG}"
if LANG == "en":
    for _s in SCENES:
        _s["vo"], _s["overlay"] = EN[_s["id"]]
AI_NOTE = {"de": "Einige Szenen wurden mit KI erstellt.",
           "en": "Some scenes were created with AI.\\NEinige Szenen wurden mit KI erstellt."}[LANG]

CHAR = {"gaius": GAIUS, "maximus": MAXIMUS, "squad": SQUAD}


def chars(s):
    return "\n".join(CHAR[c] for c in s["who"])


def image_prompt(s):
    return f"{STYLE}\n\n{chars(s)}\n\nSCENE: {s['frame']}\n{LIGHT[s['light']]}\n{COMPOSE}\n"


def anim_prompt(s):
    # The start frame carries the full STYLE and the characters; the animation prompt leads with the action
    # (vg.py lint: long style blocks bury the action and Veo then improvises the motion).
    return (f"ACTION: {s['action']}\n"
            f"SHOT: {s['camera']}, vertical 9:16, 25 fps.\n"
            f"LOOK: the drawing of the first frame stays exactly as it is: flat 2D cartoon, thick dark outlines, "
            f"round pure-white heads, soft cel shading, painted warm background, held poses and slow eyebrow "
            f"movements for comic timing.\n{LIGHT[s['light']]}\n"
            f"SOUND: only {s['sfx']}; the rest is quiet room tone.\n")


REF_PROMPTS = {
    "ref_gaius": f"{STYLE}\n\n{GAIUS}\n\nSCENE: a character model sheet on a plain warm ochre background: Gaius twice, "
                 "standing full body in full kit on the left and in only his red tunic on the right, both front view, "
                 "arms at his sides, deadpan.\n" + LIGHT["morning"] + "\n",
    "ref_maximus": f"{STYLE}\n\n{MAXIMUS}\n\nSCENE: a character model sheet on a plain warm ochre background: Maximus "
                   "standing full body, front view, the vine-wood staff in his right hand, unimpressed.\n"
                   + LIGHT["morning"] + "\n",
    "ref_squad": f"{STYLE}\n\n{GAIUS}\n{SQUAD}\n\nSCENE: a group character sheet on a plain warm ochre background: "
                 "the eight tent mates standing side by side in red tunics, Gaius second from the left, the big round "
                 "one sleeping standing up, all front view.\n" + LIGHT["morning"] + "\n",
}

THUMB = (f"{STYLE}\n\n{GAIUS}\n\nSCENE: a close-up of Gaius in his red tunic lying on a straw mat in the leather tent, "
         "extremely annoyed: eyebrows pressed down hard, eyes narrowed to slits, mouth a tight wavy line, staring into "
         "the camera. The bare dusty foot of a comrade pokes into the frame from the left edge, right next to his "
         "cheek.\n" + LIGHT["morning"] + "\nCOMPOSITION: vertical 9:16, face fills the middle of the frame.\n")


# ---------- prompts

def cmd_prompts():
    p = HERE / "prompts"
    for k, v in REF_PROMPTS.items():
        (p / f"{k}.md").write_text(v)
    (p / "thumbnail.md").write_text(THUMB)
    for s in SCENES:
        (p / f"{s['id']}_frame.md").write_text(image_prompt(s))
        (p / f"{s['id']}_anim.md").write_text(anim_prompt(s))
    print(f"prompts written to {p.relative_to(REPO)}")


# ---------- OpenRouter audio

def _post(url, body, timeout=300):
    k = os.environ.get("OPENROUTER_API_KEY", "").strip()
    hdr = {"Content-Type": "application/json"}
    if k:
        hdr["Authorization"] = f"Bearer {k}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=hdr)
    return urllib.request.urlopen(req, timeout=timeout)


VOICE = os.environ.get("SHORT_VOICE", "Daniel")


def seg_files():
    for s in SCENES:
        for i, (text, punch, hl) in enumerate(s["vo"]):
            yield s, i, text, punch, hl, HERE / "audio" / f"vo{SUF}_{s['id']}_{i}.mp3"


def vo_fast(s, i):
    return HERE / "audio" / f"vo{SUF}_{s['id']}_{i}_fast.wav"


def cmd_vo(force=False):
    for s, i, text, punch, hl, f in seg_files():
        if f.exists() and not force:
            continue
        r = _post("https://openrouter.ai/api/v1/audio/speech",
                  {"model": "elevenlabs/eleven-multilingual-v2", "input": text, "voice": VOICE,
                   "response_format": "mp3"})
        f.write_bytes(r.read())
        print(f"  {f.name}: {dur(f):.2f} s  {text}")
    for s, i, *_ , f in seg_files():
        fast = vo_fast(s, i)
        if force or not fast.exists() or fast.stat().st_mtime < f.stat().st_mtime:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(f), "-af",
                            f"atempo={TEMPO},silenceremove=start_periods=1:start_threshold=-45dB,"
                            "areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                            "-ar", "48000", str(fast)], check=True)


def cmd_music():
    f = HERE / "audio" / "music.mp3"
    prompt = ("Instrumental only, no vocals. Light, playful comedic underscore for a dry humorous history cartoon: "
              "pizzicato strings, a plucked harp and a soft frame drum with a gentle ancient Mediterranean flavour, "
              "about 100 bpm, steady and loopable, sparse and quiet so a narrator sits clearly on top, about 70 seconds.")
    r = _post("https://openrouter.ai/api/v1/chat/completions",
              {"model": "google/lyria-3-pro-preview", "messages": [{"role": "user", "content": prompt}],
               "modalities": ["audio", "text"], "audio": {"format": "mp3"}, "stream": True}, timeout=600)
    chunks, sample = [], []
    for line in r:
        line = line.decode().strip()
        if not line.startswith("data:") or line == "data: [DONE]":
            continue
        try:
            ev = json.loads(line[5:])
        except ValueError:
            continue
        for ch in ev.get("choices", []):
            au = (ch.get("delta") or {}).get("audio") or {}
            if au.get("data"):
                chunks.append(au["data"])
            elif len(sample) < 3:
                sample.append(line[:300])
    if not chunks:
        print("\n".join(sample))
        sys.exit("no audio in the stream")
    data = "".join(chunks)
    f.write_bytes(base64.b64decode(data))
    print(f"  music: {dur(f):.1f} s")


# ---------- timing

PAUSE_PUNCH = 0.5   # pause before each punchline
LEAD, TAIL = 0.25, 0.5
TEMPO = 1.05        # ElevenLabs reads ~130 wpm; the brief asks for ~150


def dur(f):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True).stdout.strip()
    return float(o)


def timeline():
    """Scene start/len, and every VO segment's absolute start/len."""
    t, rows = 0.0, []
    for s in SCENES:
        lead = 0.6 if s["id"] == "s1" else LEAD   # s1: let the horn hit first
        segs, x = [], lead
        for i, (text, punch, hl) in enumerate(s["vo"]):
            f = vo_fast(s, i)
            if punch:
                x += PAUSE_PUNCH
            d = dur(f)
            segs.append(dict(text=text, punch=punch, hl=hl, file=f, start=t + x, len=d))
            x += d
        length = max(x + TAIL, 3.5)
        if s["id"] == "s12":
            length = x + 2.1         # room for the closing horn, the loop back to s1
        s["gen"] = 6 if length <= 6 else 8
        rows.append(dict(scene=s, start=t, len=length, segs=segs))
        t += length
        continue
        rows.append(dict(scene=s, start=t, len=length, segs=segs))
        t += length
    return rows, t


def cmd_timeline():
    rows, total = timeline()
    for r in rows:
        print(f"{r['scene']['id']:4} {r['start']:6.2f}  {r['len']:.2f} s  " +
              " | ".join(f"{g['text']} ({g['len']:.1f})" for g in r["segs"]))
    print(f"total {total:.2f} s")


# ---------- captions (ASS)

RED = "&H002222B2"   # #B22222 in ASS BGR


def ts(t):
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02}:{s:05.2f}"


def srt_ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def word_times(g):
    """Spread the segment's words over its audio by character length (a usable karaoke approximation)."""
    words = g["text"].split()
    weights = [len(w) + 2 for w in words]
    tot = sum(weights)
    t, out = g["start"] + 0.05, []
    span = g["len"] - 0.15
    for w, k in zip(words, weights):
        d = span * k / tot
        out.append((w, t, t + d))
        t += d
    return out


def chunks(wt, n=3):
    cur = []
    for item in wt:
        cur.append(item)
        if len(cur) == n or item[0][-1] in ".?!:,":
            yield cur
            cur = []
    if cur:
        yield cur


def ass_file(rows, total, path):
    font = "Inter Display"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,11,4,2,80,80,480,1
Style: Ovl,{font},104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,10,3,8,70,70,330,1
Style: Lab,{font},44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,1,2,60,60,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev, srt, ovl = [], [], []
    n = 0
    for r in rows:
        for g in r["segs"]:
            hl = set(g["hl"])
            wt = word_times(g)
            chs = list(chunks(wt))
            for ci, ch in enumerate(chs):
                end = ch[-1][2] + 0.12
                if ci + 1 < len(chs):
                    end = min(end, chs[ci + 1][0][1])   # never two captions on screen at once
                n += 1
                srt.append(f"{n}\n{srt_ts(ch[0][1])} --> {srt_ts(end)}\n{' '.join(w for w, *_ in ch)}\n")
                for k, (w, a, b) in enumerate(ch):
                    shown = []
                    for w2, *_ in ch[:k + 1]:
                        shown.append(f"{{\\c{RED}}}{w2}{{\\c&H00FFFFFF&}}" if w2 in hl or w2.strip('.,!?:') in hl
                                     else w2)
                    e = ch[k + 1][1] if k + 1 < len(ch) else end
                    pop = "{\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}" if k == 0 else ""
                    ev.append(f"Dialogue: 1,{ts(a)},{ts(e)},Cap,,0,0,0,,{pop}{' '.join(shown)}")
        o = r["scene"]["overlay"]
        if o:
            a, b = r["start"] + 0.25, r["start"] + r["len"] - 0.1
            ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Ovl,,0,0,0,,{{\\fad(120,80)}}{o}")
            ovl.append((r["scene"]["id"], a, b, o))
    # AI disclosure, small, last 3 s
    ev.append(f"Dialogue: 3,{ts(total - 3.2)},{ts(total)},Lab,,0,0,0,,{{\\fad(150,0)}}{AI_NOTE}")
    path.write_text(head + "\n".join(ev) + "\n")
    return "\n".join(srt), ovl


# ---------- build

SFX_VOL = {"s11": 0.3, "s12": 0.25}   # s11 carries a heartbeat instead; s12 gets the s1 horn for the loop


def extras(rows, total, tmp):
    """Heartbeat under s11 and the horn from s1 at the very end, so the Short loops back to its start."""
    s11 = next(r for r in rows if r["scene"]["id"] == "s11")
    hb = tmp / "heartbeat.wav"
    beat = ("0.9*sin(2*PI*48*t)*exp(-28*mod(t,0.9))+0.6*sin(2*PI*42*t)*exp(-28*(mod(t,0.9)-0.22))"
            "*gte(mod(t,0.9),0.22)")
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "aevalsrc=" + beat.replace(",", "\\,") + f":s=48000:d={s11['len']:.2f}",
         "-af", "afade=t=in:d=0.3,afade=t=out:st=" + f"{s11['len'] - 0.4:.2f}:d=0.4", "-ac", "2", str(hb)])
    horn = tmp / "horn.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(latest_clip("s1")), "-t", "2.0", "-vn", "-af",
         "volume=2.0,afade=t=out:st=1.7:d=0.3", "-ar", "48000", "-ac", "2", str(horn)])
    a, b = int(s11["start"] * 1000), int((total - 2.0) * 1000)
    return (["-i", str(hb), "-i", str(horn)],
            f"[HB]adelay={a}|{a},apad[hb];[HN]adelay={b}|{b},apad[hn];")


def latest_clip(sid):
    c = sorted(OUT.glob(f"short_{sid}_*.mp4"), key=lambda p: p.stat().st_mtime)
    return c[-1] if c else None


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        print(p.stderr[-3000:])
        sys.exit(f"ffmpeg failed: {' '.join(cmd[:6])} …")


def cmd_build():
    rows, total = timeline()
    tmp = HERE / "build"
    tmp.mkdir(exist_ok=True)
    # 1. video track: each clip trimmed to its scene length, normalised to 1080x1920 @25, with its own SFX audio
    parts = []
    for r in rows:
        sid = r["scene"]["id"]
        clip = latest_clip(sid)
        part = tmp / f"{sid}.mp4"
        if clip:
            run(["ffmpeg", "-y", "-v", "error", "-i", str(clip), "-t", f"{r['len']:.3f}",
                 "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},"
                        "tpad=stop_mode=clone:stop_duration=3",   # a clip shorter than its scene holds its last frame
                 "-af", f"aresample=48000,aformat=channel_layouts=stereo,volume={SFX_VOL.get(sid, 1.0)},apad",
                 "-ar", "48000",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac",
                 "-shortest", str(part)])
        else:   # placeholder: the start frame held, or grey
            fr = HERE / "frames" / f"{sid}.png"
            src = ["-loop", "1", "-i", str(fr)] if fr.exists() else ["-f", "lavfi", "-i", f"color=c=gray:s={W}x{H}"]
            run(["ffmpeg", "-y", "-v", "error", *src, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                 "-t", f"{r['len']:.3f}", "-vf",
                 f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}",
                 "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(part)])
        parts.append(part)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    cut = tmp / "cut.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cut)])

    # 2. audio: VO segments at their times, SFX under, music with holes at punchlines and in s11
    vo_in, vo_f = [], []
    for k, g in enumerate(gg for r in rows for gg in r["segs"]):
        vo_in += ["-i", str(g["file"])]
        ms = int(g["start"] * 1000)
        vo_f.append(f"[{k + 2}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{k}]")
    nv = len(vo_f)
    holes = []
    for r in rows:
        if r["scene"]["id"] == "s11":
            holes.append((r["start"], r["start"] + r["len"]))
        for g in r["segs"]:
            if g["punch"]:
                holes.append((g["start"] - PAUSE_PUNCH - 0.05, g["start"] + g["len"] + 0.25))
    mute = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in holes) or "0"
    music = HERE / "audio" / "music.mp3"
    ass = tmp / "captions.ass"
    srt, ovl = ass_file(rows, total, ass)
    (HERE / f"captions{SUF}.srt").write_text(srt)
    m_in = ["-stream_loop", "-1", "-i", str(music)] if music.exists() else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    # music: ramps to 0 in holes (short fades via smoothing the gate)
    fc = ";".join(vo_f) + ";" + \
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f}," \
        f"volume='0.16*(1-min(1,{mute}))':eval=frame,afade=t=out:st={total - 1.2:.2f}:d=1.2[mu];" \
        f"[0:a]volume=0.55[sfx];" + \
        "".join(f"[v{k}]" for k in range(nv)) + f"amix=inputs={nv}:normalize=0,volume=1.0[vo];" \
        f"[sfx][mu]amix=inputs=2:normalize=0[bed];" \
        f"[bed][vo]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[duck];" \
        f"[duck]" + "".join(f"[v{k}]" for k in range(0)) + "anull[duck2];" \
        f"[duck2][vo]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout];" \
        f"[0:v]ass={ass}:fontsdir=/usr/share/fonts/opentype/inter[vout]"
    # sidechaincompress needs the vo twice; split it
    fc = fc.replace(f"amix=inputs={nv}:normalize=0,volume=1.0[vo];",
                    f"amix=inputs={nv}:normalize=0,volume=1.0,apad,asplit=2[vo][vo2];")
    fc = fc.replace("[duck2][vo]amix", "[duck2][vo2]amix")
    ex_in, ex_f = extras(rows, total, tmp)
    hb_i, hn_i = nv + 2, nv + 3
    fc = ex_f.replace("[HB]", f"[{hb_i}:a]").replace("[HN]", f"[{hn_i}:a]") + fc
    fc = fc.replace("[0:a]volume=0.55[sfx];", "[0:a]volume=0.45[sfx0];[sfx0][hb][hn]amix=inputs=3:normalize=0:duration=first[sfx];")
    final = OUT / f"D_legionaer_short{SUF}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(cut), *m_in, *vo_in, *ex_in, "-filter_complex", fc,
         "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium",
         "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)])
    print(f"built {final.relative_to(REPO)} · {total:.1f} s")


# ---------- package (section 12 of the brief)

def tr(de, en):
    return en if LANG == "en" else de


TITLES = tr(["Ein Tag als römischer Legionär", "Legionär sein? Lieber nicht.", "Rom, 110 n. Chr.: Dein Albtraum-Job"],
            ["A Day as a Roman Legionary", "Join the Roman Army? Maybe Not.", "Rome, 110 AD: Your Nightmare Job"])
DESC = tr("Acht Männer, ein Zelt, Essig zum Frühstück und 25 Jahre Dienstzeit: so sah der Alltag eines römischen "
          "Legionärs um 110 n. Chr. aus. Einige Szenen wurden mit KI erstellt.",
          "Eight men, one tent, vinegar for breakfast and 25 years of service: daily life of a Roman legionary "
          "around 110 AD. Some scenes were created with AI.")
TAGS = tr("#Geschichte #AltesRom #Legionär #Shorts #History", "#History #AncientRome #RomanLegion #Shorts #RomanEmpire")


def fmt(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def cmd_package():
    rows, total = timeline()
    _, ovl = ass_file(rows, total, HERE / "build" / "captions.ass")
    srt = (HERE / f"captions{SUF}.srt").read_text() if (HERE / f"captions{SUF}.srt").exists() else ""
    L = [tr(f"# Ein Tag als Legionär · YouTube Short (9:16, {total:.0f} s)\n",
            f"# A Day as a Roman Legionary · YouTube Short (9:16, {total:.0f} s)\n"),
         tr("Alles, was Abschnitt 12 des Briefings verlangt. Die Prompts stehen auch einzeln in `prompts/`.\n",
            "Everything section 12 of the brief asks for. The prompts are also in `prompts/`, one file each.\n"),
         tr("## 1. Charakter-Referenzen\n", "## 1. Character references\n")]
    for k, v in REF_PROMPTS.items():
        L += [f"### {k.replace('ref_', '').capitalize()}\n", "```", v.strip(), "```\n"]
    L.append(tr("## 2. Szenen\n", "## 2. Scenes\n"))
    for r in rows:
        s = r["scene"]
        L += [f"### {s['id'].upper()} · {fmt(r['start'])}–{fmt(r['start'] + r['len'])} · {r['len']:.1f} s "
              f"(Clip {s['gen']} s, Veo 3.1 Fast)\n",
              tr("**Bild-Prompt**", "**Image prompt**"), "```", image_prompt(s).strip(), "```",
              tr("**Animations-Prompt**", "**Animation prompt**"), "```", anim_prompt(s).strip(), "```\n"]
    L += [tr("## 3. Voiceover-Skript\n", "## 3. Voiceover script\n"),
          tr("Männlich, ruhig, trocken; ElevenLabs Multilingual v2, Tempo +5 %, 0,5 s Pause vor jeder Pointe.\n",
             "Male, calm, dry; ElevenLabs Multilingual v2, tempo +5 %, a 0.5 s pause before every punchline.\n"),
          tr("| Zeit | Szene | Text |", "| Time | Scene | Text |"), "|---|---|---|"]
    for r in rows:
        for g in r["segs"]:
            L.append(f"| {fmt(g['start'])} | {r['scene']['id'].upper()} | {'**' + g['text'] + '**' if g['punch'] else g['text']} |")
    L += [tr("\nAls Fließtext:\n", "\nAs running text:\n"), "> " + " ".join(g["text"] for r in rows for g in r["segs"]) + "\n",
          tr("## 4. Untertitel (SRT)\n", "## 4. Subtitles (SRT)\n"),
          tr(f"Auch als `captions{SUF}.srt`. Im Video wortweise eingeblendet, Schlüsselwörter in #B22222.\n",
             f"Also as `captions{SUF}.srt`. In the video they appear word by word, key words in #B22222.\n"),
          "```", srt.strip(), "```\n", "## 5. Overlays\n",
          tr("| von | bis | Szene | Text |", "| from | to | Scene | Text |"), "|---|---|---|---|"]
    L += [f"| {fmt(a)} | {fmt(b)} | {sid.upper()} | {o} |" for sid, a, b, o in ovl]
    L.append(f"| {fmt(total - 3.2)} | {fmt(total)} | {tr('Ende', 'End')} | {AI_NOTE.replace(chr(92) + 'N', ' / ')} "
             f"{tr('(klein, unten)', '(small, bottom)')} |\n")
    L += [tr("## 6. Sound und Musik\n", "## 6. Sound and music\n"), tr("| Zeit | Was |", "| Time | What |"), "|---|---|",
          f"| 0:00–{fmt(total)} | " + tr("Musik: Pizzicato-Streicher, Harfe, Rahmentrommel (KI-generiert, instrumental), leise unter dem VO",
                                        "Music: pizzicato strings, harp, frame drum (AI-generated, instrumental), low under the VO") + " |"]
    for r in rows:
        s = r["scene"]
        L.append(f"| {fmt(r['start'])} | {s['id'].upper()} SFX: {s['sfx']} |")
        for g in r["segs"]:
            if g["punch"]:
                L.append(f"| {fmt(g['start'] - PAUSE_PUNCH)} | " +
                         tr(f"Musik aus für die Pointe „{g['text']}“", f"Music off for the punchline “{g['text']}”") + " |")
        if s["id"] == "s11":
            L.append(f"| {fmt(r['start'])}–{fmt(r['start'] + r['len'])} | " +
                     tr("Musik aus, nur Atmo und Herzschlag", "Music off, only ambience and a heartbeat") + " |")
    L.append(f"| {fmt(total - 2.0)} | " + tr("Signalhorn als Abschluss, derselbe Ruf wie in S1 → Loop",
                                             "Closing horn call, the same call as in S1 → loop") + " |\n")
    L += [tr("## 7. Schnittplan\n", "## 7. Cut plan\n"),
          tr("| Zeit | Szene | Bild | VO | Overlay | SFX |", "| Time | Scene | Picture | VO | Overlay | SFX |"),
          "|---|---|---|---|---|---|"]
    for r in rows:
        s = r["scene"]
        L.append(f"| {fmt(r['start'])} | {s['id'].upper()} | {s['action'].split('.')[0]}. | "
                 f"{' '.join(g['text'] for g in r['segs'])} | {s['overlay'] or '–'} | {s['sfx']} |")
    L += [tr("\n## 8. Thumbnail-Prompt\n", "\n## 8. Thumbnail prompt\n"), "```", THUMB.strip(), "```\n",
          "## 9. YouTube\n", tr("**Titel**\n", "**Titles**\n")] + \
         [f"- {x} ({len(x)} {tr('Zeichen', 'characters')})" for x in TITLES] + \
         ["", f"**{tr('Beschreibung', 'Description')}:** {DESC}\n", f"**Hashtags:** {TAGS}\n",
          tr("Beim Hochladen in YouTube Studio „Veränderte oder synthetische Inhalte“ auf *Ja* setzen.\n",
             "When uploading, set “Altered or synthetic content” to *Yes* in YouTube Studio.\n")]
    (HERE / f"PAKET{SUF}.md").write_text("\n".join(L))
    print(f"PAKET{SUF}.md written")

if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    {"prompts": cmd_prompts, "vo": lambda: cmd_vo("--force" in sys.argv), "music": cmd_music,
     "timeline": cmd_timeline, "build": cmd_build, "package": cmd_package}.get(c, lambda: print(__doc__))()
