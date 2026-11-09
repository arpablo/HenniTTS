# Working in HenniTTS

This repository holds two launchers that speak text aloud on an Apple Silicon
Mac, `bin/tts-qwen` and `bin/tts-phonon`, and one skill that prepares a
Markdown note for them, `skills/prepare-tts-text`. `README.md` is the guide
for a person. This file is for an agent working here.

**This repository is the source of the skill.** The copy a harness loads is
installed from here. Never edit an installed copy. Change the files under
`skills/` and install again.

## Use the skill from this repository

The skill needs no installation to be used. Read its contract and run it from
where it lies:

```bash
cat skills/prepare-tts-text/SKILL.md
python3 skills/prepare-tts-text/prepare.py wording NOTE.md
```

That works whenever the work happens in this repository, and it is the normal
way. What it does not do is make the harness find the skill by itself. Here it
has to be used deliberately, which is no loss while you are working in this
directory and reading this file.

## Installing it is the user's decision

Installing copies the skill into a directory of the harness, so that it is
offered in every session without anyone pointing at it. That directory lies
outside this repository, and in the global case outside the project
altogether.

**Do not install anything unless the user asks for it.** You may say once that
installation is possible and what it would change. If the user wants it, read
`Install.md` and follow it. It carries the question of local or global, the
directories per harness, the steps, and the check that tells with git whether
a version is installed already.

Without that request, use the skill from `skills/` as above.

## Preparing a note

The skill carries its own contract in `skills/prepare-tts-text/SKILL.md`.
Read that before preparing a note. In short:

```bash
python3 skills/prepare-tts-text/prepare.py wording NOTE.md
# rewrite NOTE.txt into a reading version, by hand, after the reading rules
python3 skills/prepare-tts-text/prepare.py check NOTE.md NOTE.txt
tts-phonon --lang de NOTE.txt
```

The middle step is never automated. Whether `1.234` is a quantity or a file
reference, whether `1907/08` means a span or a financial year, whether
`Wilhelm II.` stands in the dative — that needs context, and a replacement
rule cannot read it. Where the text does not decide, ask instead of guessing.

## House rules for this repository

- **No semicolons in prose.** Two main clauses become two sentences. Where
  they belong together, a comma with `and`, `but` or `because` carries them.
  In code a semicolon is syntax and stays what it is.
- Files are written in English. Say what was measured, not what is expected.
  A number in this repository comes from a run, not from an estimate.
- Audio in `samples` is not committed. The sample texts are, the recordings
  made from them are not.
- `mlx-env` and `voices/.creating-*` are local runtime data and stay out of
  git.
- Run the tests before committing a change to `bin`:

```bash
python3 -m unittest discover -s tests
```

  They cover `tts-qwen` only. `tts-phonon` and the skill have no tests yet,
  so check a change to either by hand against a running Ollama server and say
  that you did.
