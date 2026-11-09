#!/usr/bin/env python3
"""CLI and saved voice profiles for the tts-qwen launcher (standard library only)."""

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import wave

ROOT = Path(__file__).resolve().parent.parent
VOICES = ROOT / "voices"
PYTHON = Path(os.environ.get("MLX_TTS_ENV", str(ROOT / "mlx-env"))) / "bin/python"
DESIGN_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit"
BASE_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-4bit"
DEFAULTS = {
    "en": {
        "name": "voice-en",
        "language": "English",
        "description": "A warm male narrator speaking clear British English at a calm natural pace with restrained expression.",
        "text": "Good morning. Let us take a moment to explore something new. I will guide you through the details in a clear and natural way.",
    },
    "de": {
        "name": "voice-de",
        "language": "German",
        "description": "A warm male narrator with clear standard German pronunciation, a calm natural pace and restrained expression.",
        "text": "Guten Morgen. Nehmen wir uns einen Moment Zeit, um etwas Neues zu entdecken. Ich begleite dich klar und verständlich durch die einzelnen Schritte.",
    },
}


def fail(message):
    raise ValueError(message)


def voice_name(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value):
        fail("Voice names must contain 1–64 letters, digits, underscores or hyphens, starting with a letter or digit.")
    return value


def wav_details(path):
    with wave.open(str(path), "rb") as recording:
        frames = recording.getnframes()
        rate = recording.getframerate()
        if frames <= 0 or rate <= 0:
            fail("The generated WAV is empty.")
        return {"duration_seconds": round(frames / rate, 3), "sample_rate": rate, "channels": recording.getnchannels()}


def load_voice(name, language):
    profile = VOICES / voice_name(name)
    try:
        metadata = json.loads((profile / "voice.json").read_text(encoding="utf-8"))
        transcript = (profile / "reference.txt").read_text(encoding="utf-8-sig").strip()
    except (OSError, json.JSONDecodeError) as error:
        fail(f"Cannot load voice '{name}': {error}. Use --list-voices or create it with --create-voice.")
    if not isinstance(metadata, dict) or metadata.get("schema_version") != 1:
        fail(f"Unsupported voice metadata for '{name}'.")
    if metadata.get("language") != language:
        fail(f"Voice '{name}' does not match --lang. Select a voice for {language}.")
    if not transcript:
        fail(f"Voice '{name}' has an empty reference transcript.")
    reference = profile / "reference.wav"
    wav_details(reference)
    return reference, transcript


def read_text(args, creating=False):
    if args.text is not None:
        text = args.text
    elif args.clipboard:
        text = subprocess.check_output(["pbpaste"]).decode("utf-8")
    elif args.file and args.file != "-":
        text = Path(args.file).read_text(encoding="utf-8-sig")
    elif args.file == "-":
        text = sys.stdin.read()
    elif creating:
        # Creating a voice without a source always uses a known reference text.
        # Do not accidentally consume clipboard contents or a redirected stdin.
        text = DEFAULTS[args.language_group]["text"]
    elif sys.stdin.isatty():
        text = subprocess.check_output(["pbpaste"]).decode("utf-8")
    else:
        text = sys.stdin.read()
    if not text.strip():
        fail("The text source is empty.")
    return text


def synthesize(text, folder, language, description=None, reference=None, transcript=None, play=False, speed=1.0, pause=0.3):
    command = [str(PYTHON), str(ROOT / "bin/tts-qwen-engine.py"), "--model",
               DESIGN_MODEL if description is not None else BASE_MODEL,
               "--lang_code", DEFAULTS[language]["language"],
               "--output_path", str(folder), "--file_prefix", "speech", "--join_audio",
               "--speed", str(speed), "--pause", str(pause)]
    if description is not None:
        command.extend(["--instruct", description])
    else:
        command.extend(["--ref_audio", str(reference), "--ref_text", transcript])
    if play:
        command.append("--play")
    # All library output must stay off binary stdout. Never execute text as code.
    subprocess.run(command, input=text.encode("utf-8"), stdout=sys.stderr, stderr=sys.stderr, check=True)
    result = folder / "speech.wav"
    wav_details(result)
    return result


def create_voice(args):
    name = voice_name(args.create_voice)
    destination = VOICES / name
    if destination.exists():
        fail(f"Voice '{name}' already exists. Use another name; existing voices are never overwritten.")
    text = read_text(args, creating=True).strip()
    description = args.description or DEFAULTS[args.language_group]["description"]
    if args.lang == "en-US" and not args.description:
        description = description.replace("British English", "American English")
    # No multi-paragraph or very long reference: short, exact speech is better for cloning.
    if len(text) > 1200:
        fail("Please use a short reference passage (at most 1,200 characters).")
    VOICES.mkdir(exist_ok=True)
    # Stage in the same filesystem and publish only after synthesis succeeds.
    with tempfile.TemporaryDirectory(prefix=".creating-", dir=VOICES) as temporary:
        staging = Path(temporary)
        audio = synthesize(text, staging, args.language_group, description=description,
                           speed=1.0 if args.speed is None else args.speed, pause=args.pause)
        metadata = {
            "schema_version": 1, "name": name, "language": args.language_group,
            "source_locale": "en-GB" if args.lang == "en" else args.lang,
            "description": description, "source_model": DESIGN_MODEL,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **wav_details(audio),
        }
        audio.rename(staging / "reference.wav")
        (staging / "reference.txt").write_text(text + "\n", encoding="utf-8")
        (staging / "voice.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # A concurrent creator must not replace an already published profile.
        if destination.exists():
            fail(f"Voice '{name}' was created by another process. Choose another name.")
        staging.rename(destination)
    print(f"Created voice: {name} ({metadata['duration_seconds']:.1f} seconds).", file=sys.stderr)
    print("Listen to reference.wav and verify reference.txt before reusing this voice.", file=sys.stderr)


def list_voices():
    for folder in sorted(VOICES.glob("*")) if VOICES.is_dir() else []:
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        try:
            metadata = json.loads((folder / "voice.json").read_text(encoding="utf-8"))
            if not isinstance(metadata, dict):
                raise ValueError("Invalid metadata")
            language = metadata.get("language", "unknown")
            default = " (default)" if language in DEFAULTS and DEFAULTS[language]["name"] == folder.name else ""
            print(f"{folder.name}\t{language}{default}")
        except (OSError, ValueError):
            print(f"{folder.name}\tinvalid profile")


def parser():
    result = argparse.ArgumentParser(
        prog="tts-qwen",
        description="Local speech with saved voices. Only English and German are supported; English is the default.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  tts-qwen --text "Good morning."
  tts-qwen --lang de --text "Guten Morgen."
  tts-qwen -o speech.wav english.txt
  tts-qwen --lang de deutsch.txt > sprache.wav
  tts-qwen --create-voice narrator-en --description "A calm British female narrator."
  tts-qwen --lang de --create-voice narrator-de --description "A calm female narrator speaking standard German."
  tts-qwen --voice narrator-en english.txt
  tts-qwen --lang de --voice narrator-de deutsch.txt

English defaults to voice-en; German defaults to voice-de.
No output option at a terminal: playback only. -o FILE or > FILE: save WAV without playback.
--description alone uses fresh VoiceDesign for one invocation (no saved identity).
--create-voice saves reference.wav, reference.txt and voice.json in voices/NAME.
--speed 0.85 is the reading default; --speed 1 uses the original tempo.
Text is synthesized in short sections; token-limit failures are rejected.
--setup installs/updates the runtime; creating and cloning download their models as needed.''')
    source = result.add_mutually_exclusive_group()
    source.add_argument("--text", help="Text to read")
    source.add_argument("--clipboard", action="store_true", help="Read the macOS clipboard")
    source.add_argument("file", nargs="?", help="UTF-8 text file, or - for stdin")
    result.add_argument("--lang", default="en", choices=["en", "en-GB", "en-US", "de"], help="Only English and German; default en")
    mode = result.add_mutually_exclusive_group()
    mode.add_argument("--voice", help="Saved voice name; defaults to voice-en or voice-de")
    mode.add_argument("--create-voice", metavar="NAME", help="Generate and save a new reference voice")
    mode.add_argument("--list-voices", action="store_true", help="List saved voice profiles")
    result.add_argument("--description", help="VoiceDesign description (new voice or one-off design)")
    result.add_argument("-o", "--output", help="WAV output filename, or - for stdout")
    result.add_argument("--speed", type=float, help="Pitch-preserving tempo, 0.5–2.0; reading default 0.85, reference creation 1.0; requires ffmpeg unless 1.0")
    result.add_argument("--pause", type=float, default=0.3, help="Pause between short sections in seconds (0–3; default 0.3)")
    result.add_argument("--no-play", action="store_true", help="Disable playback; requires an output destination")
    return result


def main():
    options = parser()
    args = options.parse_args()
    args.language_group = "de" if args.lang == "de" else "en"
    if args.speed is not None and (not math.isfinite(args.speed) or not 0.5 <= args.speed <= 2.0):
        options.error("Speed must be between 0.5 and 2.0.")
    if not math.isfinite(args.pause) or not 0 <= args.pause <= 3:
        options.error("Pause must be between 0 and 3 seconds.")
    if args.description is not None and not args.description.strip():
        options.error("The voice description is empty.")
    if args.voice is not None:
        voice_name(args.voice)
    if args.create_voice is not None:
        voice_name(args.create_voice)
    if args.voice is not None and args.description:
        options.error("A saved voice cannot be combined with --description. Use --create-voice for a new design.")
    if args.list_voices:
        if args.file or args.text is not None or args.clipboard or args.description or args.output is not None or args.no_play:
            options.error("Use --list-voices without text or generation options.")
        list_voices()
        return
    if args.create_voice is not None:
        if args.output is not None or args.no_play:
            options.error("--create-voice saves its own profile; do not combine it with -o or --no-play.")
        create_voice(args)
        return

    if args.output == "":
        options.error("The output filename is empty.")
    output = args.output if args.output is not None else (None if sys.stdout.isatty() else "-")
    if output and output != "-":
        target = Path(output)
        if target.is_dir() or not target.parent.is_dir():
            fail("Output must be a filename in an existing directory.")
    if args.no_play and output is None:
        fail("Without playback, select an output using -o or >.")

    reference = transcript = None
    if args.description is None:
        reference, transcript = load_voice(args.voice or DEFAULTS[args.language_group]["name"], args.language_group)
    text = read_text(args)
    # SIGINT/SIGTERM unwinds this context and removes temporary recordings.
    with tempfile.TemporaryDirectory(prefix="mlx-tts-") as temporary:
        audio = synthesize(text, Path(temporary), args.language_group,
                           description=args.description, reference=reference, transcript=transcript,
                           play=output is None, speed=0.85 if args.speed is None else args.speed, pause=args.pause)
        if output == "-":
            with audio.open("rb") as handle:
                shutil.copyfileobj(handle, sys.stdout.buffer)
            sys.stdout.buffer.flush()
        elif output:
            shutil.copyfile(audio, output)
            print(f"Saved: {output}", file=sys.stderr)


if __name__ == "__main__":
    def interrupted(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGHUP, interrupted)
    try:
        main()
    except BrokenPipeError:
        # Avoid another flush error when the consumer closes a pipe early.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(141)
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        sys.exit(130)
    except (OSError, ValueError, wave.Error, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
