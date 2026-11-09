---
name: prepare-tts-text
description: "Turn a Markdown note into the plain text file a speech model should read: markup removed, numbers, units, dates, Roman numerals and abbreviations written out, tables dissolved into sentences. Produces a .txt for tts-qwen or tts-phonon and checks it against the note. Use before voicing a note that contains numbers, lists, tables or regnal names."
---

# Prepare a note for speech

**A speech model reads characters, not meaning.** `50.000` ends a sentence for
it because there is a full stop. `1907/08` becomes a fraction or a date,
whichever it guesses. `Wilhelm II.` has neither article nor case, and `m²` is
a letter followed by a sign it has to invent a sound for. Listening afterwards
does not help, because the model says exactly what is written and what is
written is wrong.

So the text is prepared first. The result is a plain UTF-8 text file beside
the note, and that file is what `tts-qwen` or `tts-phonon` reads.

This skill is self-contained. It needs nothing but Python 3 and the files in
this directory.

## Three steps

### 1. Lay down the wording

```bash
python3 skills/prepare-tts-text/prepare.py wording NOTE.md
```

That writes `NOTE.txt`: the note without what a listener cannot hear. Gone are
the frontmatter, comments, embeds, footnotes, bold and italic markers, inline
code, quote marks, callout headings and rules. A wikilink becomes its alias, a
Markdown link its text, a heading a sentence of its own. Each list item
becomes its own sentence, because a listener hears no bullet and without a
full stop the items run together.

The command also prints an inventory of the places that still have to be
decided: digits, Roman numerals, signs and units, and whether a table or a
code block is in the way.

### 2. Rewrite it into a reading version

This step is yours. Read the rules for the language of the note and rewrite
`NOTE.txt` in place:

- `skills/prepare-tts-text/reading-de.md` and `dictionary-de.json` for German
- `skills/prepare-tts-text/reading-en.md` and `dictionary-en.json` for English

The rules cover numbers and identifiers, money, years and spans, Roman
numerals, units, signs and formulas, abbreviations, tables and code blocks,
and what never happens. The dictionaries hold the cases that have already
been decided, and a new decision belongs in them.

**Add nothing and drop nothing.** Write out what has one reading. Leave
standing what is an identifier: `Version 1.2.0` is not a quantity, and an ISBN
is not a sum. Grammar is adjusted only as far as writing out forces it.

**Ask rather than guess.** `1.234`, `1907/08`, a bare `$`, `03/04/2026`,
`5 nm` and `Heinrich VIII` in a German sentence each have more than one
reading. Where the text does not decide, collect the open questions and ask
them in one go.

### 3. Check it

```bash
python3 skills/prepare-tts-text/prepare.py check NOTE.md NOTE.txt
```

The check compares the reading version with the note and reports:

- **Words of the note that are missing.** Writing out replaces, it does not
  delete. Two or more words gone in one place is an error and the reading
  version is not ready. Exactly one word is a hint, because two rewritings
  the rules themselves prescribe move a single word: `23:05 Uhr` becomes
  `dreiundzwanzig Uhr fünf`, and `mc²` becomes `m mal c Quadrat`.
- **A table or a code block still in the text.** Read mechanically that is a
  row of dashes.
- **Digits, Roman numerals, signs and units still standing.** These are
  hints. An identifier may stay, a forgotten year may not.

Numbers are left out of the comparison, because rewriting them is the point.
A placeholder stands in their place, and that is how the check tells a
replacement from a disappearance.

**What the check does not do.** Measured against seven faults injected into a
reading version it found five. It missed a dropped sentence tail whose words
occur elsewhere in the text, and a dropped number word, which it does not
compare at all. A clean run is no proof that the reading version says the same
thing. It shows that the coarse losses are not in it. Read what you wrote.

## Then speak it

```bash
# Fast, with a fixed voice
tts-phonon --lang de NOTE.txt

# With a saved voice of your own
tts-qwen --lang de NOTE.txt
```

Neither launcher prepares text, which is why this skill exists.

## What stays out of the reading version

A phonetic respelling. Whether a model says `NASA` as a word or `ADAC` letter
by letter is a property of the model and not of the text. Where a model
audibly gets a word wrong, write the phonetic spelling in by hand and record
the case in the dictionary, so the decision is not lost. That holds for that
one model and says nothing about the text.
