#!/usr/bin/env python3
"""Local speech with the Phonon voices served by Ollama (standard library only).

The interface follows tts-qwen, so the two can be compared on the same text.
What Phonon does not have is left out: it serves fixed voices, so there is no
VoiceDesign description and nothing to create or clone. The voices come with
the model, and the language comes with it too — Phonon ships one model per
language, and `--lang` selects the model rather than a setting inside it.

Speech arrives as raw 16-bit PCM at 24 kHz, mono. Pieces of one paragraph
join without a seam; between paragraphs a pause is inserted, because that is
where a reader breathes.
"""

import argparse
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
import urllib.error
import urllib.request
import wave

MODELS = {"en": "phonon:40m-en", "de": "phonon:40m-de"}
DEFAULT_HOST = "http://localhost:11434"
# The endpoint takes at most 4096 characters; the margin leaves room for the
# sentence that would have crossed the line.
LIMIT = 3800
RATE = 24000
TIMEOUT = 600
SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")


def fail(message):
    raise ValueError(message)


def host():
    """Where Ollama listens: the environment, else the default."""
    url = os.environ.get("OLLAMA_HOST", "").strip() or DEFAULT_HOST
    return (url if "://" in url else f"http://{url}").rstrip("/")


def ask(path, payload, decode=True):
    data = json.dumps(payload).encode("utf-8")
    call = urllib.request.Request(f"{host()}{path}", data=data,
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(call, timeout=TIMEOUT) as answer:
            body = answer.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace").strip()
        fail(f"Ollama answered HTTP {error.code}: {detail[:300]}")
    except urllib.error.URLError as error:
        fail(f"Ollama is not reachable at {host()}: {error.reason}."
             " Start it, or run tts-phonon --setup.")
    return json.loads(body) if decode else body


def voices(model):
    """The voices the model serves, as it spells them."""
    shown = ask("/api/show", {"model": model})
    if "speech" not in (shown.get("capabilities") or []):
        fail(f"{model} cannot speak. Run tts-phonon --setup.")
    listed = shown.get("voices") or []
    if not listed:
        fail(f"{model} names no voices.")
    return listed


def chosen_voice(model, wanted):
    """The voice as the model spells it. A name may hold spaces, so it is
    matched against the model's own list and not against a pattern."""
    listed = voices(model)
    for name in listed:
        if name.lower() == wanted.lower():
            return name
    fail(f"{model} does not serve the voice '{wanted}'. Available: "
         + ", ".join(listed))


def pieces(paragraph):
    """One paragraph cut into requests at sentence, then word boundaries."""
    if len(paragraph) <= LIMIT:
        return [paragraph]
    result, current = [], ""
    for part in SENTENCE_END.split(paragraph):
        while len(part) > LIMIT:
            cut = part.rfind(" ", 0, LIMIT)
            cut = cut if cut > 0 else LIMIT
            if current:
                result.append(current)
                current = ""
            result.append(part[:cut].strip())
            part = part[cut:].strip()
        joined = f"{current} {part}" if current else part
        if len(joined) <= LIMIT:
            current = joined
        else:
            result.append(current)
            current = part
    if current:
        result.append(current)
    return result


def spoken(model, voice, text, pause):
    """Every paragraph spoken, joined, with a pause between paragraphs."""
    paragraphs = [" ".join(part.split()) for part in re.split(r"\n\s*\n", text)]
    paragraphs = [part for part in paragraphs if part]
    quiet = b"\0\0" * int(RATE * pause)
    samples = bytearray()
    for index, paragraph in enumerate(paragraphs):
        if index:
            samples += quiet
        for piece in pieces(paragraph):
            samples += ask("/v1/audio/speech",
                           {"model": model, "voice": voice, "input": piece,
                            "response_format": "pcm"}, decode=False)
    if not samples:
        fail("The model returned no audio.")
    return bytes(samples)


def write_wav(samples, target):
    with wave.open(str(target), "wb") as recording:
        recording.setnchannels(1)
        recording.setsampwidth(2)
        recording.setframerate(RATE)
        recording.writeframes(samples)


def retimed(source, target, speed):
    """Tempo without pitch, which is what ffmpeg's atempo does."""
    tool = shutil.which("ffmpeg")
    if tool is None:
        fail("--speed other than 1 needs ffmpeg. Install it, or leave the tempo alone.")
    subprocess.run([tool, "-nostdin", "-loglevel", "error", "-y", "-i", str(source),
                    "-filter:a", f"atempo={speed:g}", str(target)],
                   stdout=sys.stderr, stderr=sys.stderr, check=True)


def play(path):
    tool = shutil.which("afplay")
    if tool is None:
        fail("afplay is missing; select an output with -o instead.")
    subprocess.run([tool, str(path)], stdout=sys.stderr, stderr=sys.stderr, check=True)


def read_text(args):
    if args.text is not None:
        text = args.text
    elif args.clipboard:
        text = subprocess.check_output(["pbpaste"]).decode("utf-8")
    elif args.file and args.file != "-":
        text = Path(args.file).read_text(encoding="utf-8-sig")
    elif args.file == "-":
        text = sys.stdin.read()
    elif sys.stdin.isatty():
        text = subprocess.check_output(["pbpaste"]).decode("utf-8")
    else:
        text = sys.stdin.read()
    if not text.strip():
        fail("The text source is empty.")
    return text


def setup():
    tool = shutil.which("ollama")
    if tool is None:
        fail("Install Ollama first; tts-phonon speaks through its server.")
    for model in MODELS.values():
        print(f"Pulling {model} …", file=sys.stderr)
        subprocess.run([tool, "pull", model], stdout=sys.stderr, stderr=sys.stderr,
                       check=True)
    print('Phonon is ready. English: tts-phonon --text "Good morning."'
          ' German: tts-phonon --lang de --text "Guten Morgen."', file=sys.stderr)


def parser():
    result = argparse.ArgumentParser(
        prog="tts-phonon",
        description="Local speech with the Phonon voices served by Ollama. Only"
                    " English and German are supported; English is the default.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  tts-phonon --text "Good morning."
  tts-phonon --lang de --text "Guten Morgen."
  tts-phonon --lang de --voice Anton deutsch.txt
  tts-phonon -o speech.wav english.txt
  tts-phonon --lang de deutsch.txt > sprache.wav
  tts-phonon --lang de --list-voices

The voices belong to the model, so --lang selects the model: phonon:40m-de or
phonon:40m-en. Each serves a voice named default, which is used unless --voice
names another one; --list-voices prints them.
No output option at a terminal: playback only. -o FILE or > FILE: save WAV
without playback.
--speed leaves the tempo alone by default. Unlike tts-qwen, Phonon is not
hasty, and a tempo other than 1 needs ffmpeg.
Text is spoken paragraph by paragraph; a long paragraph is cut at sentence
boundaries and joins without a seam. --pause only separates paragraphs.
There is nothing to create or clone: Phonon serves fixed voices, so it has no
VoiceDesign description, no --create-voice and no reference recording.
--setup pulls both models through the Ollama command.''')
    source = result.add_mutually_exclusive_group()
    source.add_argument("--text", help="Text to read")
    source.add_argument("--clipboard", action="store_true", help="Read the macOS clipboard")
    source.add_argument("file", nargs="?", help="UTF-8 text file, or - for stdin")
    result.add_argument("--lang", default="en", choices=["en", "en-GB", "en-US", "de"],
                        help="Only English and German; default en")
    mode = result.add_mutually_exclusive_group()
    mode.add_argument("--voice", help="Voice of the model; default is its voice named default")
    mode.add_argument("--list-voices", action="store_true", help="List the voices of the model")
    result.add_argument("-o", "--output", help="WAV output filename, or - for stdout")
    result.add_argument("--speed", type=float,
                        help="Pitch-preserving tempo, 0.5–2.0; default 1, which needs no ffmpeg")
    result.add_argument("--pause", type=float, default=0.3,
                        help="Pause between paragraphs in seconds (0–3; default 0.3)")
    result.add_argument("--no-play", action="store_true",
                        help="Disable playback; requires an output destination")
    result.add_argument("--setup", action="store_true", help="Pull both Phonon models")
    return result


def main():
    options = parser()
    args = options.parse_args()
    if args.setup:
        if len(sys.argv) != 2:
            options.error("Use --setup on its own.")
        setup()
        return
    model = MODELS["de" if args.lang == "de" else "en"]
    if args.speed is not None and (not math.isfinite(args.speed)
                                   or not 0.5 <= args.speed <= 2.0):
        options.error("Speed must be between 0.5 and 2.0.")
    if not math.isfinite(args.pause) or not 0 <= args.pause <= 3:
        options.error("Pause must be between 0 and 3 seconds.")
    if args.list_voices:
        if (args.file or args.text is not None or args.clipboard
                or args.output is not None or args.no_play):
            options.error("Use --list-voices without text or generation options.")
        for name in voices(model):
            print(f"{name}\t{model}")
        return
    if args.voice is not None and not args.voice.strip():
        options.error("The voice name is empty.")

    if args.output == "":
        options.error("The output filename is empty.")
    output = args.output if args.output is not None else (None if sys.stdout.isatty() else "-")
    if output and output != "-":
        target = Path(output)
        if target.is_dir() or not target.parent.is_dir():
            fail("Output must be a filename in an existing directory.")
    if args.no_play and output is None:
        fail("Without playback, select an output using -o or >.")

    voice = chosen_voice(model, args.voice) if args.voice else "default"
    text = read_text(args)
    speed = 1.0 if args.speed is None else args.speed
    # SIGINT/SIGTERM unwinds this context and removes temporary recordings.
    with tempfile.TemporaryDirectory(prefix="phonon-tts-") as temporary:
        folder = Path(temporary)
        audio = folder / "speech.wav"
        write_wav(spoken(model, voice, text, args.pause), audio)
        if speed != 1.0:
            retimed(audio, folder / "retimed.wav", speed)
            audio = folder / "retimed.wav"
        if output is None:
            play(audio)
        elif output == "-":
            with audio.open("rb") as handle:
                shutil.copyfileobj(handle, sys.stdout.buffer)
            sys.stdout.buffer.flush()
        else:
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
