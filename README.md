# HenniTTS

Local text-to-speech on an Apple Silicon Mac. This repository holds:

- `bin/tts-qwen`, which speaks with Qwen3-TTS voices through MLX-Audio. The
  voices are designed once and kept in `voices`.
- `bin/tts-phonon`, which speaks with the fixed Phonon voices through Ollama.
- `skills/prepare-tts-text`, which turns a Markdown note into the plain text
  file either launcher reads.
- `tests/`, the behaviour tests, and this guide.

Both launchers take the same options. English and German are supported, with
English as the default.

## Which launcher to use

| | `tts-qwen` | `tts-phonon` |
| --- | --- | --- |
| Voices | designed by you and saved in `voices` | fixed, shipped with the model |
| Runtime | `mlx-env`, created by `--setup` | a running Ollama server |
| Model size | about 2.3 GB per model | about 0.1 GB per model |
| Reading tempo | `--speed 0.85` by default | unchanged tempo by default |
| Design or clone a voice | yes | no |

Phonon is the smaller and faster of the two. In a measurement on an M-series
Mac it produced 285 seconds of audio in 3.8 seconds. Qwen's speed on your own
machine is not measured here.

There is no automatic language detection and no translation. In `tts-qwen`,
English uses the saved `voice-en` profile and `--lang de` the saved `voice-de`
profile. In `tts-phonon`, the language sits in the model, so `--lang` selects
`phonon:40m-en` or `phonon:40m-de`.

Each section below states which launcher it applies to wherever they differ.
Sections about designing, creating or cloning a voice are `tts-qwen` only,
because Phonon has nothing of the kind.

## Project layout

```text
HenniTTS/
├── bin/
│   ├── tts-qwen           Shell launcher
│   ├── tts-qwen.py        Text input and voice profiles
│   ├── tts-qwen-engine.py Bounded synthesis and tempo adjustment
│   ├── tts-phonon         Shell launcher
│   └── tts-phonon.py      Phonon voices through Ollama, standard library only
├── mlx-env/               tts-qwen runtime, created by --setup
├── voices/                tts-qwen voice profiles
│   ├── voice-en/
│   │   ├── reference.wav  Generated English reference recording
│   │   ├── reference.txt  Exact transcript of the reference recording
│   │   └── voice.json     Language, design description and provenance
│   └── voice-de/
│       ├── reference.wav  Generated German reference recording
│       ├── reference.txt  Exact transcript of the reference recording
│       └── voice.json
├── skills/
│   └── prepare-tts-text/  Turns a Markdown note into the text to be spoken
├── tests/                 Behaviour tests for tts-qwen
├── AGENTS.md              For an agent working in this repository
├── Install.md             How to install the skill into a harness, on request
└── README.md
```

The project can live anywhere. `tts-qwen` finds `mlx-env` and `voices` relative to its own location. `tts-phonon` needs neither and runs from any directory. All repository paths in this guide are relative to the project directory.

## Setup and updates

Each launcher brings its own runtime, and neither needs the other's. Set up
only the one you intend to use.

Both need macOS on an Apple Silicon Mac, in a native terminal session without
Rosetta, and internet access for the initial model downloads.

Both use `ffmpeg` for pitch-preserving tempo adjustment (`brew install ffmpeg`
if you use Homebrew), but they need it differently: `tts-qwen` reads at
`--speed 0.85` by default and therefore needs it in normal use, while
`tts-phonon` leaves the tempo alone and needs it only when you ask for a
tempo other than `1`.

### tts-qwen

Additionally required: `uv` on your command search path or in `~/.local/bin`.
Check with `uv --version`. If that fails, install it:

```bash
# With Homebrew
brew install uv

# Without Homebrew, using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The installer places `uv` in `~/.local/bin`. Open a new terminal afterwards so
your shell picks it up. The launcher looks in that directory as well, even
without a `PATH` entry. To update it later, use `brew upgrade uv` or
`uv self update`.

Open a terminal in the project directory and run:

```bash
./bin/tts-qwen --setup
```

Setup creates a Python 3.11 environment in `mlx-env` and installs MLX-Audio. Running `--setup` again updates MLX-Audio and its dependencies. The launcher uses this environment directly. No manual activation is needed.

Two models serve different purposes:

| Model | Used for |
| --- | --- |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit` | Creating a reference voice from a description |
| `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-4bit` | Speaking new text using a saved reference voice |

Each model is about 2.3 GB plus supporting files and downloads only when first needed. Weights are reused from the Hugging Face cache, normally `~/.cache/huggingface/hub`, separately from `mlx-env`. Text synthesis runs locally. Keep the `voices` profiles when sharing the repository. `mlx-env` is local runtime data and is ignored by Git.

### tts-phonon

Additionally required: Ollama, installed separately. There is no `uv`, no
`mlx-env` and no `voices` directory. The launcher uses only the Python
standard library and speaks through the Ollama server over HTTP, so it runs
from any directory.

```bash
./bin/tts-phonon --setup
```

That pulls `phonon:40m-de` and `phonon:40m-en`, about 0.1 GB each. The voices
ship with the models, so nothing else is created or downloaded later. Running
`--setup` again updates both models. Without Ollama on your `PATH`, pull them
from its own interface instead. The launcher only needs the server.

`OLLAMA_HOST` selects another server. Without it, `http://localhost:11434` is
used, and a missing scheme is filled in.

### Your command search path

This applies to either launcher:

```bash
export PATH="$PWD/bin:$PATH"
```

The `PATH` command applies to this terminal session. Alternatively, use `./bin/tts-qwen` or `./bin/tts-phonon` from the project directory. For permanent access, add the project's `bin` directory to your shell configuration using your chosen installation location. Do not copy the session's `$PWD` expression unchanged into your shell startup file.

## Speak with the default voice

### tts-qwen

The two bundled references are synthetic voices generated with VoiceDesign. Both are warm, calm male narrators. `voice-en` was designed for British English and `voice-de` for standard German.

```bash
# English: voice-en is selected automatically
tts-qwen --text "Good morning. This is the saved English narrator."

# German: voice-de is selected automatically
tts-qwen --lang de --text "Guten Morgen. Dies ist die gespeicherte deutsche Erzählerstimme."
```

These calls use the Base model, `reference.wav` and the exact `reference.txt` transcript. They do not create a fresh VoiceDesign speaker each time. Keeping the same reference anchors the voice identity, but pronunciation, intonation, speed and timbre can still vary between generations.

### tts-phonon

Each Phonon model serves a voice named `default`, which is used unless `--voice` names another one. Nothing has to be designed first.

```bash
# English: the default voice of phonon:40m-en
tts-phonon --text "Good morning. This is the default Phonon voice."

# German: the default voice of phonon:40m-de
tts-phonon --lang de --text "Guten Morgen. Dies ist die voreingestellte Phonon-Stimme."
```

The voice is fixed by the model, so its identity cannot drift. The delivery still varies: the same sentence spoken three times gave three recordings of the same length and of different content each time.

### Text sources

Either launcher takes its text the same way. Read a plain UTF-8 text file:

```bash
# English
tts-qwen "english.txt"
tts-phonon "english.txt"

# German
tts-qwen --lang de "deutsch.txt"
tts-phonon --lang de "deutsch.txt"
```

Read the macOS clipboard:

```bash
# English
tts-qwen --clipboard
tts-phonon --clipboard

# German
tts-qwen --lang de --clipboard
tts-phonon --lang de --clipboard
```

With no source specified, an interactive terminal uses the clipboard, and piped input is read from stdin. Explicit stdin examples:

```bash
# English
printf '%s\n' 'The cost was fifty thousand euros.' | tts-qwen -

# German
printf '%s\n' 'Die Kosten betrugen fünfzigtausend Euro.' | tts-phonon --lang de -
```

## Speaking rate and long texts

Both launchers accept `--speed` between `0.5` and `2.0` and `--pause` between
`0` and `3` seconds, and both adjust tempo with ffmpeg's `atempo` filter,
which preserves pitch. What differs is the default and what a pause separates.

### tts-qwen

The reading default is **`--speed 0.85`**, which slows the generated audio to 85 percent of its original tempo without lowering the voice pitch. Reference voice creation defaults to the original tempo (`1.0`), so the reference is not slowed twice. Tempo adjustment uses ffmpeg's `atempo` filter, rather than Qwen's ineffective model-level speed parameter.

```bash
# English: slower reading
tts-qwen --speed 0.75 english.txt

# German: slower reading
tts-qwen --lang de --speed 0.75 deutsch.txt
```

Use `--speed 1` for the unadjusted tempo. Accepted values range from `0.5` to `2.0`. If ffmpeg is unavailable, install it or use `--speed 1`. Tempo settings are never silently ignored. Add `--pause` to adjust the silence between generated sections (default `0.3` seconds, range `0`–`3`):

```bash
# English
tts-qwen --speed 0.85 --pause 0.5 english.txt

# German
tts-qwen --lang de --speed 0.85 --pause 0.5 deutsch.txt
```

The launcher joins wrapped lines within paragraphs and divides prose into short sections, preferring sentence boundaries. It loads the model once, generates each section independently and joins the audio with the requested pauses. Pure punctuation separators are skipped. Numbers and abbreviations are not automatically rewritten. Prepare complex Markdown and numbers as a spoken text separately.

Each section has a bounded generation budget. Reaching that limit without a normal end is treated as an error, followed by one retry at a lower sampling temperature. If it still fails, the command stops and does not publish a partial recording. This prevents a long runaway generation from being accepted merely because it produced a valid WAV header. Progress messages identify the current section on stderr.

Short sections and these checks reduce a known long-text failure mode. They are not an automatic proof of correct pronunciation. Listen to representative passages before using long recordings.

### tts-phonon

**The tempo is left alone by default.** Phonon is not hasty, and slowing it unasked would assert something about its delivery that has not been measured. `--speed 1` therefore needs no ffmpeg at all. Any other value does.

```bash
# English: slower reading
tts-phonon --speed 0.85 english.txt

# German: slower reading
tts-phonon --lang de --speed 0.85 deutsch.txt
```

`--pause` separates paragraphs only, not sentences. A paragraph longer than the request limit is cut at sentence boundaries, and those pieces join without a seam, because the endpoint returns raw samples rather than finished files. There is no generation budget and no retry: the server either answers with samples or with an error.

Output is 24 kHz, mono, 16-bit WAV. One paragraph of 4,959 characters produced 285 seconds of audio in 3.8 seconds.

## Save output only when requested

Everything in this section applies to both launchers. The examples use `tts-qwen`, and `tts-phonon` behaves identically.

At a terminal, normal reading plays audio without keeping a recording. Generation uses a temporary WAV file that is removed on completion or a handled interruption. The deliberately saved reference profiles in `voices` are kept.

Use `-o` or `--output` to save a WAV file without playback:

```bash
# English
tts-qwen -o speech.wav english.txt

# German
tts-qwen --lang de -o sprache.wav deutsch.txt
```

Or use Unix redirection:

```bash
# English
tts-qwen english.txt > speech.wav

# German
tts-qwen --lang de deutsch.txt > sprache.wav
```

Explicit stdout also works:

```bash
# English
tts-qwen --text "Good morning." -o - > speech.wav

# German
tts-qwen --lang de --text "Guten Morgen." -o - > sprache.wav
```

Redirected stdout contains WAV audio only. All status and error messages go to stderr. Output is written after generation, rather than streamed live. File output disables playback. `-o` takes a filename, not a directory, and its parent must already exist. Existing output files are overwritten. Relative paths refer to the current working directory. Output is always WAV regardless of filename extension.

The shell opens or truncates the destination before a command with `>` starts. Never redirect onto the input text file.

## Choose a voice

### tts-qwen

List the available profiles:

```bash
tts-qwen --list-voices
```

The listing identifies the default profiles. To select a voice explicitly:

```bash
# English
tts-qwen --voice voice-en english.txt

# German
tts-qwen --lang de --voice voice-de deutsch.txt
```

`--voice` takes a profile name from `voices`, not a WAV path or a built-in Qwen speaker name. A voice must match the selected language. Selecting `voice-de` without `--lang de` is rejected rather than silently changing the language.

### tts-phonon

The voices belong to the model, so the listing depends on `--lang`:

| `--lang` | Model | Voices |
| --- | --- | --- |
| `en`, `en-GB`, `en-US` | `phonon:40m-en` | 38, including `default` |
| `de` | `phonon:40m-de` | 14, including `default` |

```bash
# English
tts-phonon --list-voices
tts-phonon --voice Harper english.txt

# German
tts-phonon --lang de --list-voices
tts-phonon --lang de --voice Anton deutsch.txt
```

A voice name may contain spaces, as several English ones do, and it is matched against the model's own list without regard to case. An unknown name is rejected with the available names, rather than silently replaced. There is nothing to create: a voice that the model does not serve cannot be added.

## Create additional reusable voices

**`tts-qwen` only.** Phonon serves the voices that ship with its models and has no `--create-voice`, no `--description` and no reference recording.

### 1. Describe the new speaker

Choose a new name and call `--create-voice`. With no text source, the command uses a short built-in reference passage in the selected language:

```bash
# English
tts-qwen --create-voice narrator-en \
  --description "A warm female narrator speaking clear British English at a relaxed, natural pace."

# German
tts-qwen --lang de --create-voice narrator-de \
  --description "A warm female narrator speaking clear standard German at a relaxed, natural pace."
```

VoiceDesign generates the reference. The command saves a complete profile in `voices/narrator-en` or `voices/narrator-de` and exits without playback. Voice creation is an explicit save operation, so do not combine it with `-o`, `>` or `--no-play`. Status messages remain on stderr. Redirecting stdout during creation does not export audio.

Names may contain letters A–Z, digits, underscores and hyphens, with a maximum of 64 characters, starting with a letter or digit. Existing names are never overwritten. To try a different take, create a new name, such as `narrator-en-v2` or `narrator-de-v2`.

### 2. Optionally supply your own reference text

You can use `--text`, a UTF-8 text file, stdin (`-`) or `--clipboard` instead of the built-in passage. The supplied words must be in the selected language. For example:

```bash
# English
tts-qwen --create-voice storyteller-en \
  --description "A calm British male storyteller with clear articulation." \
  --text "Welcome to our story. Take a moment to settle in, and let us discover what happens next."

# German
tts-qwen --lang de --create-voice storyteller-de \
  --description "A calm male storyteller speaking clear standard German." \
  --text "Willkommen zu unserer Geschichte. Mach es dir einen Moment bequem, und lass uns gemeinsam entdecken, wie es weitergeht."
```

Use a clean, natural passage of roughly 8–15 seconds as a starting point. Avoid music, reaction tags, difficult numbers, abbreviations and deliberate character changes. Reference text is limited to 1,200 characters, and much shorter passages are generally more convenient. If `--description` is omitted, creation uses the built-in narrator description for the selected language.

### 3. Listen and check the transcript

From the project directory, play each candidate:

```bash
# English
afplay voices/narrator-en/reference.wav
cat voices/narrator-en/reference.txt

# German
afplay voices/narrator-de/reference.wav
cat voices/narrator-de/reference.txt
```

Check that every word in `reference.txt` is actually spoken, with no omitted or extra words, long silence or distortion. The transcript is saved from the requested text, not produced by speech recognition. If a take misreads the passage, create a new candidate with simpler wording. Keep only a candidate you have listened to and approved.

### 4. Use the saved speaker for new text

```bash
# English
tts-qwen --voice narrator-en --text "This is a completely new sentence in my saved voice."

# German
tts-qwen --lang de --voice narrator-de \
  --text "Dies ist ein völlig neuer Satz mit meiner gespeicherten Stimme."
```

The Base model reads the new text using the saved reference and transcript. It does not retrain model weights. `--description` cannot be combined with `--voice`. A description defines a new VoiceDesign speaker, not an instruction to modify an existing profile.

Keep the three profile files together when moving or sharing a voice. `voice.json` stores language and provenance without machine-specific paths. Do not edit `reference.txt` to contain your next text. It must always describe `reference.wav` exactly. Supply new text through the normal command options instead.

## Defaults, language and accents

**Only English and German are currently supported by either launcher**, although the models support additional languages.

| Setting | Output language | `tts-qwen` default voice | `tts-phonon` model |
| --- | --- | --- | --- |
| No `--lang` option | English | `voice-en` | `phonon:40m-en` |
| `--lang en` or `--lang en-GB` | English | `voice-en` | `phonon:40m-en` |
| `--lang en-US` | English | `voice-en` | `phonon:40m-en` |
| `--lang de` | German | `voice-de` | `phonon:40m-de` |

In `tts-phonon` the three English settings select the same model, so they do not switch the accent. The accent is whatever the chosen voice has. The rest of this section is about `tts-qwen`.

With saved voices, the reference recording determines the speaker and accent. `--lang en-US` does **not** turn the British `voice-en` reference into an American speaker. To create an American English reference, use `en-US` during voice creation, then select that profile explicitly:

```bash
# English: create and use an American narrator
tts-qwen --lang en-US --create-voice narrator-us
tts-qwen --lang en-US --voice narrator-us english.txt

# German: create and use another standard German narrator
tts-qwen --lang de --create-voice narrator-standard-de
tts-qwen --lang de --voice narrator-standard-de deutsch.txt
```

The default names are fixed to `voice-en` and `voice-de`. Additional voices are selected with `--voice`, and creating one does not change the defaults. If a default profile is missing, the launcher reports an error. It never silently replaces it with a new random speaker. A missing default can be recreated with `--create-voice voice-en` or `--lang de --create-voice voice-de`, provided the respective name does not already exist.

## One-off VoiceDesign without a saved profile

**`tts-qwen` only.**

The earlier `--description` workflow is still available. Without `--create-voice`, it uses VoiceDesign for that invocation and bypasses the saved default:

```bash
# English
tts-qwen --description "A quiet British female narrator." --text "A new voice for this sentence."

# German
tts-qwen --lang de --description "A quiet female narrator speaking standard German." \
  --text "Eine neue Stimme für diesen Satz."
```

At a terminal these calls play without saving. Use `-o` if you want to keep the resulting audio. Unlike saved profiles, repeated descriptions may generate different speaker identities.

## Prepare numbers and pronunciation

Prepare difficult numbers and abbreviations as spoken text before synthesis:

| Language | Source | Spoken text |
| --- | --- | --- |
| English | `50,000 euros` | `fifty thousand euros` |
| German | `50.000 Euro` | `fünfzigtausend Euro` |
| English | `e.g.` | `for example` |
| German | `z. B.` | `zum Beispiel` |

In both languages, the reading of `1978/79` depends on whether it means a season, academic year or time range.

**`skills/prepare-tts-text` does this work.** It lays down the wording of a Markdown note, carries the reading rules and dictionaries for German and English, and checks the finished text against the note for places that are still unspoken and for words that went missing. Neither launcher invokes it, so run it first and hand the resulting `.txt` to `tts-qwen` or `tts-phonon`:

```bash
python3 skills/prepare-tts-text/prepare.py wording NOTE.md
# rewrite NOTE.txt into a reading version, then
python3 skills/prepare-tts-text/prepare.py check NOTE.md NOTE.txt
tts-phonon --lang de NOTE.txt
```

The skill needs no installation to be used this way. `Install.md` describes
how to copy it into a directory your harness searches, so it is offered
without being pointed at. That is optional and nothing here depends on it.

Neither launcher loads a dictionary of its own. VoiceStudio profiles and dictionaries are not imported. Convert PDF documents to plain UTF-8 text first.

Neither launcher rewrites anything, and that applies to both the same way.

```bash
# English
tts-qwen prepared-english.txt
tts-phonon prepared-english.txt

# German
tts-qwen --lang de lesefassung-deutsch.txt
tts-phonon --lang de lesefassung-deutsch.txt
```

## Use the environment directly

**`tts-qwen` only.** `tts-phonon` has no environment of its own and talks to Ollama over HTTP.

From the project directory:

```bash
source mlx-env/bin/activate
python -m mlx_audio.tts.generate --help
deactivate
```

Or call the interpreter directly:

```bash
./mlx-env/bin/python -m mlx_audio.tts.generate --help
```

`MLX_TTS_ENV` can select another environment for testing. It does not change the project's `voices` directory.

## Option reference

Both launchers accept the same options. Where an option behaves differently,
the section above says so.

| Option | `tts-qwen` | `tts-phonon` |
| --- | --- | --- |
| `--text`, `--clipboard`, `FILE`, `-` | yes | yes |
| `--lang {en,en-GB,en-US,de}` | selects the saved default voice | selects the model |
| `--voice NAME` | a profile in `voices` | a voice of the model |
| `--list-voices` | saved profiles | the model's voices |
| `-o`, `--output`, `>` | yes | yes |
| `--speed 0.5`–`2.0` | default `0.85` | default `1` |
| `--pause 0`–`3` | between sections | between paragraphs |
| `--no-play` | yes | yes |
| `--setup` | creates `mlx-env`, installs MLX-Audio | pulls both Phonon models |
| `--description`, `--create-voice` | yes | not available |

Playback, redirection, stdout and the exit codes are identical in both, so
anything this guide says about those applies to either launcher.

## Help and troubleshooting

```bash
tts-qwen --help
tts-qwen --list-voices
tts-phonon --help
tts-phonon --lang de --list-voices
```

- Missing runtime: run `tts-qwen --setup`, or `tts-phonon --setup` for the Phonon models.
- Synthesis failure: check stderr. No WAV output is published if generation fails.
- `tts-qwen` missing profile: check `voices/NAME` contains all three files, or create a new named voice.
- `tts-qwen` language mismatch: use `--lang de` with a German profile, or an English setting with an English profile.
- `tts-qwen` poor cloning: listen to the reference and check its exact transcript, then try a clearer reference passage.
- `tts-qwen` moved project: recreate `mlx-env` at the new location and update any PATH entries or symlinks.
- `tts-phonon` cannot reach Ollama: start the server, check `OLLAMA_HOST`, or run `tts-phonon --setup`.
- `tts-phonon` rejects a voice: run `--list-voices` for the chosen `--lang`, because the voices differ per model.

Temporary recordings are removed after completion or handled interruptions. A forced process kill or power loss may leave temporary files. Incomplete voice creation folders start with `.creating-` and are excluded from Git. Existing profiles are never overwritten by `--create-voice`.

## Development checks

Run the behavior tests without downloading models or using the GPU:

```bash
python3 -m unittest discover -s tests -v
```

The tests use a simulated synthesis backend. They cover default and named voices, English and German routing, profile creation, failure cleanup, playback selection, clean WAV output, bounded long-text splitting, tempo routing and rejection of generation-limit exhaustion.

They cover `tts-qwen` only. `tts-phonon` has no tests yet. What it does was checked by hand against a running Ollama server.
