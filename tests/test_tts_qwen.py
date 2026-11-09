"""Behavior checks without model downloads, GPU use or audio playback."""

import json
import importlib.util
from types import SimpleNamespace
import os
from pathlib import Path
import pty
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave


class VoiceWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hennitts-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "bin").mkdir()
        source = Path(__file__).resolve().parent.parent / "bin" / "tts-qwen.py"
        self.script = self.root / "bin" / "tts-qwen.py"
        shutil.copyfile(source, self.script)
        engine = self.root / "fake-env" / "bin" / "python"
        engine.parent.mkdir(parents=True)
        engine.write_text("#!" + sys.executable + "\n" + '''
import json, os, pathlib, sys, wave
args = sys.argv[1:]
out = pathlib.Path(args[args.index('--output_path') + 1])
pathlib.Path(os.environ['TTS_TEST_LOG']).write_text(json.dumps({'args': args, 'text': sys.stdin.read(), 'temp': str(out)}))
print('backend status on stdout')
print('backend status on stderr', file=sys.stderr)
if os.environ.get('TTS_TEST_FAIL'):
    raise SystemExit(7)
with wave.open(str(out / 'speech.wav'), 'wb') as result:
    result.setnchannels(1)
    result.setsampwidth(2)
    result.setframerate(24000)
    result.writeframes(b'\\0\\0' * 240)
''')
        engine.chmod(0o755)
        self.env = dict(os.environ, MLX_TTS_ENV=str(engine.parent.parent),
                        TTS_TEST_LOG=str(self.root / "request.json"))
        for name, language in (("voice-en", "en"), ("voice-de", "de")):
            profile = self.root / "voices" / name
            profile.mkdir(parents=True)
            (profile / "reference.txt").write_text("Exact reference transcript.\n")
            (profile / "voice.json").write_text(json.dumps({"schema_version": 1, "language": language}))
            with wave.open(str(profile / "reference.wav"), "wb") as recording:
                recording.setnchannels(1)
                recording.setsampwidth(2)
                recording.setframerate(24000)
                recording.writeframes(b"\0\0" * 240)

    def run_cli(self, *args, text=None, stdout=subprocess.PIPE):
        return subprocess.run([sys.executable, str(self.script), *args], env=self.env,
                              input=text.encode() if text is not None else None,
                              stdout=stdout, stderr=subprocess.PIPE, cwd=self.root)

    def request(self):
        return json.loads((self.root / "request.json").read_text())

    def test_language_defaults_clone_the_matching_saved_reference(self):
        for flags, name, language in (([], "voice-en", "English"), (["--lang", "de"], "voice-de", "German")):
            result = self.run_cli(*flags, "--text", "A new sentence.")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout[:4], b"RIFF")
            self.assertNotIn(b"backend status", result.stdout)
            request = self.request()
            args = request["args"]
            self.assertIn("1.7B-Base-4bit", args[args.index("--model") + 1])
            self.assertEqual(Path(args[args.index("--ref_audio") + 1]).parent.name, name)
            self.assertEqual(args[args.index("--ref_text") + 1], "Exact reference transcript.")
            self.assertEqual(args[args.index("--lang_code") + 1], language)
            self.assertNotIn("--instruct", args)
            self.assertEqual(args[args.index("--speed") + 1], "0.85")
            self.assertFalse(Path(request["temp"]).exists())

    def test_named_voice_and_language_mismatch(self):
        self.assertEqual(self.run_cli("--voice", "voice-en", "--text", "Hello.").returncode, 0)
        result = self.run_cli("--voice", "voice-de", "--text", "Hello.")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"does not match", result.stderr)

    def test_new_voice_saves_exact_text_and_metadata_without_stdout_audio(self):
        text = 'Grüße. Literal text: $HOME and "quotes".'
        result = self.run_cli("--lang", "de", "--create-voice", "custom-de", "--text", text)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, b"")
        profile = self.root / "voices" / "custom-de"
        self.assertEqual((profile / "reference.txt").read_text(), text + "\n")
        metadata = json.loads((profile / "voice.json").read_text())
        self.assertEqual(metadata["language"], "de")
        self.assertEqual(metadata["schema_version"], 1)
        self.assertIn("VoiceDesign", self.request()["args"][self.request()["args"].index("--model") + 1])
        self.assertEqual(list((self.root / "voices").glob(".creating-*")), [])
        self.assertEqual(self.request()["args"][self.request()["args"].index("--speed") + 1], "1.0")
        audio = (profile / "reference.wav").read_bytes()
        self.assertNotEqual(self.run_cli("--create-voice", "custom-de").returncode, 0)
        self.assertEqual((profile / "reference.wav").read_bytes(), audio)

    def test_builtin_creation_passage_does_not_consume_piped_text(self):
        result = self.run_cli("--create-voice", "custom-en", text="Unrelated pipeline input.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Good morning.", (self.root / "voices/custom-en/reference.txt").read_text())

    def test_file_output_and_failure_preserve_existing_file(self):
        output = self.root / "speech with spaces.wav"
        result = self.run_cli("--text", "Hello.", "-o", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(output.read_bytes()[:4], b"RIFF")
        original = output.read_bytes()
        self.env["TTS_TEST_FAIL"] = "1"
        self.assertNotEqual(self.run_cli("--text", "Hello.", "-o", str(output)).returncode, 0)
        self.assertEqual(output.read_bytes(), original)
        self.assertFalse(Path(self.request()["temp"]).exists())

    def test_terminal_playback_keeps_no_recording(self):
        master, slave = pty.openpty()
        try:
            result = self.run_cli("--text", "Hello.", stdout=slave)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("--play", self.request()["args"])
            self.assertFalse(Path(self.request()["temp"]).exists())
        finally:
            os.close(master)
            os.close(slave)

    def test_missing_profile_does_not_fall_back_to_random_design(self):
        shutil.rmtree(self.root / "voices/voice-en")
        result = self.run_cli("--text", "Hello.")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Cannot load voice", result.stderr)
        self.assertFalse((self.root / "request.json").exists())

    def test_failed_creation_leaves_no_partial_profile(self):
        self.env["TTS_TEST_FAIL"] = "1"
        result = self.run_cli("--create-voice", "failed-en")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "voices/failed-en").exists())
        self.assertEqual(list((self.root / "voices").glob(".creating-*")), [])

    def test_one_off_design_stdin_and_invalid_arguments(self):
        result = self.run_cli("--description", "A quiet British narrator.", "-", text="Hello from stdin.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.request()["text"], "Hello from stdin.")
        self.assertIn("--instruct", self.request()["args"])
        for flags in (("--voice", "../escape"), ("--voice", ""), ("--create-voice", ""),
                      ("--lang", "fr"), ("--voice", "voice-en", "--description", "new voice"),
                      ("--create-voice", "new", "-o", "out.wav"), ("--speed", "0"),
                      ("--speed", "nan"), ("--pause", "-1")):
            self.assertNotEqual(self.run_cli(*flags).returncode, 0, flags)


class LongTextRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parent.parent / "bin/tts-qwen-engine.py"
        spec = importlib.util.spec_from_file_location("tts_engine_checks", path)
        cls.engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.engine)

    def test_wrapped_prose_is_bounded_without_losing_words_or_splitting_numbers(self):
        paragraph = ("Dr. Meyer zahlte 50.000 Euro. Der Wert betrug 1.234,50 Euro. "
                     "Das war im Jahr 1978/79. This sentence includes e.g. a number. ") * 80
        chunks = self.engine.split_text(paragraph.replace("Euro. ", "Euro.\n"))
        self.assertGreater(len(chunks), 10)
        self.assertTrue(all(len(chunk) <= 280 for chunk in chunks))
        self.assertEqual(" ".join(chunks), " ".join(paragraph.split()))
        self.assertTrue(all("1.234,50" in chunk or "1.234" not in chunk for chunk in chunks))

    def test_token_limit_exhaustion_is_not_success(self):
        with self.assertRaisesRegex(ValueError, "token limit"):
            self.engine.check_token_limit([SimpleNamespace(token_count=256)], 256)
        with self.assertRaises(ValueError):
            self.engine.check_token_limit([], 256)
        self.engine.check_token_limit([SimpleNamespace(token_count=255)], 256)

    def test_punctuation_only_and_oversized_identifiers(self):
        with self.assertRaises(ValueError):
            self.engine.split_text("---\n\n...")
        with self.assertRaises(ValueError):
            self.engine.split_text("x" * 1201)
        self.assertEqual(self.engine.split_text("---\n\nHello world."), ["Hello world."])


if __name__ == "__main__":
    unittest.main()
