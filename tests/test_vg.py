"""python3 -m unittest discover -s tests   (standard library only, no network, no cost)"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / ".claude/skills/video-gen/scripts"
sys.path.insert(0, str(SCRIPTS))
import vg  # noqa: E402


def codes(model, prompt, dur=None):
    return {c for _, c, _ in vg.lint(vg.load_model(model), prompt, dur)}


class Cost(unittest.TestCase):
    def test_h3_per_second_and_refs(self):
        self.assertAlmostEqual(vg.estimate_usd(vg.load_model("h3"), 8), 1.04)
        self.assertAlmostEqual(vg.estimate_usd(vg.load_model("h3"), 8, nrefs=2), 1.12)

    def test_veo_audio_and_resolution(self):
        self.assertAlmostEqual(vg.estimate_usd(vg.load_model("veo"), 6), 2.40)
        self.assertAlmostEqual(vg.estimate_usd(vg.load_model("veo"), 8, audio=False), 1.60)
        self.assertAlmostEqual(vg.estimate_usd(vg.load_model("veo-fast"), 8, "720p"), 0.80)

    def test_seedance_tokens(self):
        usd = vg.estimate_usd(vg.load_model("seedance"), 8, "720p", ratio="16:9")
        self.assertAlmostEqual(usd, 1280 * 720 * 24 * 8 / 1024 * 0.0000107)


class Lint(unittest.TestCase):
    def test_clean_template_prompts(self):
        for f in REPO.glob("templates/*/shotlist.json"):
            sl = json.loads(f.read_text())
            for s in sl["slots"]:
                if s.get("model"):
                    warn = [c for lvl, c, _ in vg.lint(vg.load_model(s["model"]), (f.parent / s["prompt"]).read_text(),
                                                       s.get("gen_dur", int(s["dur"]))) if lvl == "warn"]
                    self.assertEqual(warn, [], f"{sl['id']}/{s['id']}")

    def test_brand_negation_surface(self):
        c = codes("veo", "SHOT: wide.\nA man in a Ralph Lauren polo, no logo, not smiling, never moving, nothing else, looks at a monitor.")
        self.assertTrue({"BRAND", "NEGATIONS", "TEXT_SURFACE"} <= c)

    def test_spoken_words_are_not_surfaces(self):
        p = 'SHOT: medium.\nACTION: she speaks.\nDIALOGUE: "Dokumentieren Sie alles. Also, ja."\nSCENE: a quiet room.'
        self.assertNotIn("TEXT_SURFACE", codes("h3", p, 5))

    def test_perishable_only_in_dialogue(self):
        p = 'SHOT: medium, 35mm.\nACTION: she speaks.\nDIALOGUE: "Nur bis Freitag, 3 Prozent. Also, ja."\nSCENE: room 4.'
        self.assertIn("PERISHABLE", codes("h3", p, 6))
        self.assertNotIn("PERISHABLE", codes("h3", 'SHOT: 35mm lens.\nACTION: she nods.\nDIALOGUE: "Ab Montag im Lernportal."', 5))
        self.assertIn("PERISHABLE", codes("h3", 'SHOT: 35mm lens.\nACTION: she nods.\nDIALOGUE: "Nur bis Mittwoch."', 5))

    def test_too_many_words(self):
        p = 'SHOT: medium.\nACTION: speaks.\nDIALOGUE: "' + " ".join(["Wort"] * 30) + '"'
        self.assertIn("TOO_MANY_WORDS", codes("h3", p, 8))

    def test_model_specific(self):
        self.assertIn("NO_SHOT", codes("veo", "A woman walks into a room."))
        self.assertIn("TASK_TYPE", codes("seedance", "ACTION: add a cup to the table."))
        self.assertIn("LAUGH", codes("seedance", "ACTION: two people laugh."))


class GuideExamples(unittest.TestCase):
    """Every prompt the guides teach must pass the lint it teaches."""

    @staticmethod
    def blocks(path):
        import re
        return [b for lang, b in re.findall(r"```(\w*)\n(.*?)```", path.read_text(), re.S)
                if not lang and re.search(r"^(SHOT|ACTION):", b, re.M)]

    def test_idea_to_prompt_examples(self):
        ref = SCRIPTS.parent / "reference/idea_to_prompt.md"
        engines = [("seedance", 6), ("h3", 8), ("veo", 8), ("seedance", 6), ("veo", 8)]
        examples = self.blocks(ref)
        self.assertEqual(len(examples), len(engines))
        for (m, d), b in zip(engines, examples):
            self.assertEqual(vg.lint(vg.load_model(m), b, d), [], b.splitlines()[0])

    def test_prompt_template_examples(self):
        for name, m, d in (("veo_cinematic.md", "veo", 8), ("seedance_broll.md", "seedance", 6),
                           ("h3_talking.md", "h3", 8), ("h3_object.md", "h3", 8)):
            for b in self.blocks(SCRIPTS.parent / "prompts" / name):
                if "{" in b:
                    continue  # skeletons with {placeholders}
                warn = [c for lvl, c, _ in vg.lint(vg.load_model(m), b, d) if lvl == "warn"]
                self.assertEqual(warn, [], f"{name}: {b.splitlines()[0]}")

    def test_abstract_idea_is_flagged(self):
        self.assertIn("ABSTRACT", codes("seedance", "ACTION: a scene that shows trust and security."))
        self.assertNotIn("ABSTRACT", codes("h3", 'SHOT: medium, 35mm.\nACTION: she speaks.\nDIALOGUE: "Vertrauen ist alles."', 5))


class Body(unittest.TestCase):
    def test_limits(self):
        with self.assertRaises(SystemExit):
            vg.build_body(vg.load_model("veo"), "x", dur=5)
        with self.assertRaises(SystemExit):
            vg.build_body(vg.load_model("h3"), "x", dur=20)
        with self.assertRaises(SystemExit):
            vg.build_body(vg.load_model("veo"), "x", ratio="1:1")

    def test_veo_takes_no_refs(self):
        frame = SCRIPTS.parent / "assets/mock_frame.png"
        with self.assertRaises(SystemExit):
            vg.build_body(vg.load_model("veo"), "x", refs=[frame])

    def test_h3_shapes(self):
        frame = SCRIPTS.parent / "assets/mock_frame.png"
        b = vg.build_body(vg.load_model("h3"), "x", dur=8, first_frame=frame)
        self.assertEqual(b["frame_images"][0]["type"], "image_url")
        self.assertEqual(b["frame_images"][0]["frame_type"], "first_frame")
        self.assertNotIn("resolution", b)  # H3 is 2K only, the field is not sent
        b = vg.build_body(vg.load_model("h3"), "x", refs=[frame])
        self.assertEqual(b["input_references"][0]["type"], "image_url")
        self.assertTrue(b["input_references"][0]["image_url"]["url"].startswith("data:image/png;base64,"))

    def test_seed_dropped_where_unsupported(self):
        self.assertNotIn("seed", vg.build_body(vg.load_model("h3"), "x", seed=3))
        self.assertEqual(vg.build_body(vg.load_model("veo"), "x", seed=3)["seed"], 3)


class Takes(unittest.TestCase):
    def test_takes_compare_and_use(self):
        if not shutil.which("ffmpeg"):
            self.skipTest("ffmpeg missing")
        with tempfile.TemporaryDirectory() as t:
            root = Path(t) / "lab"
            shutil.copytree(REPO, root, ignore=shutil.ignore_patterns("out", "jobs", ".git", "slots", "takes", "teaching"))
            env = dict(os.environ, VG_MOCK="1", VG_USER="takes", CLAUDE_PROJECT_DIR=str(root))
            vgp = root / ".claude/skills/video-gen/scripts/vg.py"
            asm = root / ".claude/skills/video-gen/scripts/assemble.py"

            def run(script, *args):
                return subprocess.run([sys.executable, str(script), *args], cwd=root, env=env, capture_output=True, text=True)

            for _ in range(2):
                self.assertEqual(run(vgp, "submit", "seedance", "--prompt", "ACTION: a cup.", "--dur", "5",
                                     "--slot", "templates/A_teaser/s2").returncode, 0)
                self.assertEqual(run(vgp, "wait").returncode, 0)
            self.assertIn("t1, t2 (in use)", run(asm, "templates/A_teaser", "--takes").stdout)
            self.assertEqual(run(asm, "templates/A_teaser", "--compare", "s2").returncode, 0)
            self.assertTrue((root / "out/A_teaser_s2_takes.mp4").exists())
            run(asm, "templates/A_teaser", "--use", "s2", "t1")
            self.assertIn("t1 (in use), t2", run(asm, "templates/A_teaser", "--takes").stdout)


class Welcome(unittest.TestCase):
    def test_greeting_report_in_mock_mode(self):
        env = dict(os.environ, VG_MOCK="1", VG_USER="welcometest", CLAUDE_PROJECT_DIR=str(REPO))
        r = subprocess.run([sys.executable, str(SCRIPTS / "welcome.py")], cwd=REPO, env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for part in ("## Checks", "## Templates", "## Your generations", "## Suggested next step"):
            self.assertIn(part, r.stdout)
        (REPO / "jobs" / "welcometest.jsonl").unlink(missing_ok=True)


class Presign(unittest.TestCase):
    def test_aws_documented_vector(self):
        # AWS SigV4 docs, "GET object" presigned URL example
        qs = vg.presign("examplebucket.s3.amazonaws.com", "/test.txt", "AKIAIOSFODNN7EXAMPLE",
                        "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "us-east-1", 86400,
                        dt.datetime(2013, 5, 24, 0, 0, 0))
        self.assertTrue(qs.endswith("X-Amz-Signature=aeeed9bbccd4d02ee5c0109b86d86835f995330da4c265957d157751f604d404"))


class MockFlow(unittest.TestCase):
    def test_submit_wait_assemble(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t) / "lab"
            shutil.copytree(REPO, root, ignore=shutil.ignore_patterns("out", "jobs", ".git", "slots"))
            env = dict(os.environ, VG_MOCK="1", VG_USER="test", CLAUDE_PROJECT_DIR=str(root))
            env.pop("VG_LEDGER", None)
            vgp = root / ".claude/skills/video-gen/scripts/vg.py"

            def run(*args):
                return subprocess.run([sys.executable, str(vgp), *args], cwd=root, env=env, capture_output=True, text=True)

            r = run("submit", "seedance", "--prompt-file", "templates/A_teaser/prompts/s2.md", "--dur", "5",
                    "--slot", "templates/A_teaser/s2")
            self.assertEqual(r.returncode, 0, r.stderr)
            env["VG_CONFIRM_EUR"] = "1"
            r = run("submit", "veo", "--prompt-file", "templates/A_teaser/prompts/s1.md", "--dur", "8")
            self.assertEqual(r.returncode, 3, "above the confirmation line it must ask first")
            env.pop("VG_CONFIRM_EUR")
            r = run("wait")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((root / "templates/A_teaser/slots/s2.mp4").exists())
            ledger = [json.loads(x) for x in (root / "jobs/test.jsonl").read_text().splitlines()]
            self.assertEqual(ledger[-1]["status"], "completed")
            r = run("submit", "h3", "--prompt", "x", "--dur", "8", "--over-budget")
            self.assertEqual(r.returncode, 0, r.stderr)
            env["VG_BUDGET_EUR"] = "0.5"
            r = run("submit", "h3", "--prompt", "x", "--dur", "8")
            self.assertEqual(r.returncode, 1, "budget must stop the call")
            if shutil.which("ffmpeg"):
                r = subprocess.run([sys.executable, str(root / ".claude/skills/video-gen/scripts/assemble.py"),
                                    "templates/A_teaser"], cwd=root, env=env, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn("20.4 s", r.stdout)


if __name__ == "__main__":
    unittest.main()
