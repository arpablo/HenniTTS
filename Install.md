# Installing the skill

Read this file only when the user has asked for the skill to be installed.
Without that request, use it from `skills/` as `AGENTS.md` describes. Nothing
here is needed to prepare a note.

Installing copies `skills/prepare-tts-text` into a directory the harness
searches, so the skill is offered in every session without anyone pointing at
it. The copy is a copy. **This repository stays the source.** Never edit an
installed copy. Change the files under `skills/` and install again.

## 1. Ask where it goes

Never decide this alone, because one of the two answers writes outside this
repository.

> Install `prepare-tts-text` locally for this project, or globally for your
> harness, so every project can use it?

### Claude Code

| Choice | Directory |
| --- | --- |
| Local, this project only | `.claude/skills/prepare-tts-text/` |
| Global, every project | `~/.claude/skills/prepare-tts-text/` |

### Codex

| Choice | Directory |
| --- | --- |
| Local, this project only | `.agents/skills/prepare-tts-text/` |
| Global, every project | `~/.agents/skills/prepare-tts-text/` |

These are the repository and user locations in the Codex documentation on
skills. Codex finds a new skill without a restart. If it does not appear,
restart Codex.

### Another harness

Use the skill directory that harness documents, and follow its own layout for
a local and a global skill. Do not invent a path. If its convention is not
clear from its documentation, say so and ask rather than guess.

## 2. See which version is installed

Ask git which version this repository holds, and compare it with the version
that was installed.

```bash
# The version here: the git tree of the skill directory. It changes when a
# file of the skill changes and not when some unrelated commit is made.
git rev-parse "HEAD:skills/prepare-tts-text"

# The version installed, recorded at install time:
sed -n 's/^tree: //p' <skill directory>/.installed-from
```

- Both the same: that version is installed already. Say so and stop.
- Different: an older version is installed. Install again and say which
  version replaces which.
- No `.installed-from` and no directory: not installed. Install it.
- No `.installed-from` but a directory: something else put it there. Report
  that and ask before overwriting it.

If `git status --porcelain -- skills/prepare-tts-text` is not empty, the
working copy differs from every commit and no tree id describes what is on
disk. Install from the working copy, record `tree: uncommitted`, and say so.
A version recorded that way is reinstalled on every check.

## 3. Install

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

## 4. Say what happened

Name the directory, the version, and that an installed copy is not the source.
A local install is already in `.gitignore`, under `.claude/skills/` for
Claude Code and `.agents/skills/` for Codex. Ask before committing one.

## Removing it

Delete the directory. Nothing else was changed, and the skill keeps working
from `skills/`.
