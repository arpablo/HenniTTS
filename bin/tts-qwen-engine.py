"""Bounded Qwen synthesis. Load the model once, generate short chunks, then join."""

import argparse
import contextlib
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys


ABBREVIATIONS = {"dr", "prof", "mr", "mrs", "ms", "st", "bzw", "vgl", "nr", "abs",
                 "ggf", "mio", "mrd", "usw", "etc", "vs", "ff", "ca"}


def sentence_boundaries(paragraph):
    boundaries = []
    for match in re.finditer(r'[.!?]+["”»\')\]]*\s+', paragraph):
        prefix = paragraph[:match.start()]
        last = re.search(r"([\w]+)$", prefix)
        token = last.group(1) if last else ""
        if match.group().startswith(".") and (token.lower() in ABBREVIATIONS or
                len(token) == 1 or token.isdigit() or re.fullmatch(r"[IVXLCDM]+", token)):
            continue
        boundaries.append(match.end())
    return boundaries


def split_text(text, limit=280):
    """Keep numbers intact, join wrapped lines, prefer sentence/word boundaries."""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    chunks = []
    for paragraph in paragraphs:
        paragraph = " ".join(paragraph.split())
        # Pure separators and empty markup have no speakable words.
        if not re.search(r"\w", paragraph):
            continue
        boundaries = sentence_boundaries(paragraph)
        while len(paragraph) > limit:
            candidates = [boundary for boundary in boundaries if boundary <= limit]
            end = max(candidates) if candidates else paragraph.rfind(" ", 0, limit + 1)
            if end <= 0:
                # Do not split an unbroken identifier in the middle.
                end = paragraph.find(" ", limit)
                if end < 0:
                    end = len(paragraph)
            chunk = paragraph[:end].strip()
            if len(chunk) > 1200:
                raise ValueError("A single unbroken text item is too long to synthesize safely.")
            if chunk:
                chunks.append(chunk)
            paragraph = paragraph[end:].lstrip()
            boundaries = sentence_boundaries(paragraph)
        if paragraph:
            chunks.append(paragraph)
    if not chunks:
        raise ValueError("No speakable text was found.")
    return chunks


def token_limit(text):
    return min(768, max(128, len(text.split()) * 12 + 80))


def check_token_limit(results, maximum):
    if not results:
        raise ValueError("The model returned no audio.")
    if sum(result.token_count for result in results) >= maximum:
        raise ValueError("Generation reached the token limit without a normal end; refusing potentially corrupted audio.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--lang_code", required=True)
    parser.add_argument("--instruct")
    parser.add_argument("--ref_audio")
    parser.add_argument("--ref_text")
    parser.add_argument("--output_path", required=True)
    parser.add_argument("--file_prefix", default="speech")
    parser.add_argument("--join_audio", action="store_true")
    parser.add_argument("--play", action="store_true")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--pause", type=float, default=0.3)
    args = parser.parse_args()
    if not math.isfinite(args.speed) or not 0.5 <= args.speed <= 2.0:
        parser.error("Speed must be between 0.5 and 2.0.")
    if not math.isfinite(args.pause) or not 0 <= args.pause <= 3:
        parser.error("Pause must be between 0 and 3 seconds.")
    ffmpeg = shutil.which("ffmpeg")
    if args.speed != 1.0 and not ffmpeg:
        parser.error("Install ffmpeg for pitch-preserving tempo control, or use --speed 1.")

    chunks = split_text(sys.stdin.read())
    # MLX and its model code are imported only inside the synthesis worker.
    import mlx.core as mx
    import numpy as np
    from mlx_audio.tts.utils import load_model
    from mlx_audio.audio_io import write as audio_write
    from mlx_audio.utils import load_audio

    with contextlib.redirect_stdout(sys.stderr):
        model = load_model(args.model)
        reference = load_audio(args.ref_audio, sample_rate=model.sample_rate) if args.ref_audio else None
        audio_parts = []
        for index, chunk in enumerate(chunks):
            maximum = token_limit(chunk)
            print(f"Synthesizing section {index + 1}/{len(chunks)} ({len(chunk)} characters).", file=sys.stderr, flush=True)
            for attempt, temperature in enumerate((0.7, 0.35)):
                mx.random.seed(42 + index)
                kwargs = dict(text=chunk, lang_code=args.lang_code, max_tokens=maximum,
                              temperature=temperature, verbose=False)
                if args.instruct is not None:
                    kwargs["instruct"] = args.instruct
                else:
                    kwargs.update(ref_audio=reference, ref_text=args.ref_text)
                results = list(model.generate(**kwargs))
                try:
                    check_token_limit(results, maximum)
                    samples = np.concatenate([np.asarray(result.audio) for result in results])
                    if samples.size == 0 or not np.isfinite(samples).all():
                        raise ValueError("Invalid or empty audio samples.")
                    if float(np.sqrt(np.mean(samples.astype(np.float64) ** 2))) < 0.0001:
                        raise ValueError("The model returned near-silent audio.")
                    break
                except ValueError:
                    if attempt:
                        raise
                    print("Retrying this section once with lower sampling temperature.", file=sys.stderr, flush=True)
            audio_parts.append(samples)
            if index < len(chunks) - 1 and args.pause:
                # Account for the later atempo filter so the final pause matches --pause.
                audio_parts.append(np.zeros(round(model.sample_rate * args.pause * args.speed), dtype=np.float32))
        combined = np.concatenate(audio_parts)
        folder = Path(args.output_path)
        folder.mkdir(parents=True, exist_ok=True)
        output = folder / (args.file_prefix + ".wav")
        if args.speed == 1.0:
            audio_write(str(output), combined, model.sample_rate)
        else:
            raw = folder / (args.file_prefix + "-unadjusted.wav")
            audio_write(str(raw), combined, model.sample_rate)
            subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                            "-i", str(raw), "-filter:a", f"atempo={args.speed}",
                            "-c:a", "pcm_s16le", str(output)], check=True)
            raw.unlink()
        if args.play:
            subprocess.run(["afplay", str(output)], check=True)


if __name__ == "__main__":
    main()
