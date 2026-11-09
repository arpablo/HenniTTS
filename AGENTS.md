# Working in HenniTTS

This repository holds two launchers that speak text aloud on an Apple Silicon
Mac, `bin/tts-qwen` and `bin/tts-phonon`, and one skill that prepares a
Markdown note for them, `skills/prepare-tts-text`. `README.md` is the guide
for a person. This file is for an agent working here.

**This repository is the source of the skill.** The copy a harness loads is
installed from here. Never edit an installed copy. Change the files under
`skills/` and install again.

## Before preparing a note, see whether the skill is installed

The skill only takes effect once it sits where the harness looks for it. Ask
git which version this repository holds, and compare it with the version that
was installed.

```bash
# The version here: the git tree of the skill directory. It changes when a
# file in the skill changes and not when some unrelated commit is made.
git rev-parse "HEAD:skills/prepare-tts-text"

# The version installed, recorded at install time:
sed -n 's/^tree: //p' <skill directory>/.installed-from
```

- Both the same: the skill is installed and current. Nothing to do.
- Different: an older version is installed. Install again and say which
  version replaces which.
- No `.installed-from` and no directory: not installed. Install it.
- No `.installed-from` but a directory: something else put it there. Report
  that and ask before overwriting it.

If `git status --porcelain -- skills/prepare-tts-text` is not empty, the
working copy differs from every commit and no tree id describes what is on
disk. Install from the working copy, record `tree: uncommitted`, and say so.
A version recorded that way is reinstalled on every check.

## Installing it

**First ask where.** Never decide this alone, because one answer changes a
directory outside this repository.

> Install `prepare-tts-text` locally for this project, or globally for your
> harness, so every project can use it?

Then install into the directory the harness uses for that choice.

### Claude Code

| Choice | Directory |
| --- | --- |
| Local, this project only | `.claude/skills/prepare-tts-text/` |
| Global, every project | `~/.claude/skills/prepare-tts-text/` |

### Another harness

Use the skill directory that harness documents, and follow its own layout for
a local and a global skill. Do not invent a path. If its convention is not
clear from its documentation, say so and ask rather than guess.

### The steps

```bash
target=".claude/skills/prepare-tts-text"      # or the global directory
mkdir -p "$target"
cp skills/prepare-tts-text/* "$target/"

{
  echo "repo: https://github.com/arpablo/HenniTTS"
  echo "skill: prepare-tts-text"
  echo "tree: $(git rev-parse "HEAD:skills/prepare-tts-text")"
  echo "commit: $(git rev-parse HEAD)"
  echo "installed: $(date -u +%Y-%m-%d)"
} > "$target/.installed-from"
```

A local install belongs in this repository's `.gitignore` unless the user
wants it committed. Ask before committing an installed copy.

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
