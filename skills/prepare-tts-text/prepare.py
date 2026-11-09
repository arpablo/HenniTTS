#!/usr/bin/env python3
"""Turn a Markdown note into the wording a speech model should read, and check
the reading version that was made from it. Standard library only.

A speech model reads characters, not meaning. `50.000` ends a sentence for it
because there is a full stop, `1907/08` becomes a fraction or a date, and
`Wilhelm II.` has neither article nor case. No amount of listening afterwards
helps, because the model says exactly what is written and what is written is
wrong. So the text is prepared before it is spoken.

Two steps belong to this program and one does not:

    wording   strips what a listener cannot hear and lays the text down
    (rewrite) the assistant writes out what has one reading — not this program
    check     names what is still unspoken and what the rewriting lost

Which reading an expression has needs context. Whether `1.234` is a quantity
or a file reference, whether `1907/08` means a span, a season or two years,
whether `Wilhelm II.` stands in the dative — a replacement rule cannot read
that, so this program never rewrites. It prepares and it checks.
"""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

# --- What a listener cannot hear -----------------------------------------
FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---[ \t]*\r?\n", re.S)
TITLE = re.compile(r"^title:[ \t]*(.+?)[ \t]*$", re.M)
EMBED = re.compile(r"!\[\[[^\]\n]*\]\]|!\[[^\]\n]*\]\([^)\n]*\)")
WIKILINK = re.compile(r"\[\[([^\]\n|]+)(?:\\?\|([^\]\n]*))?\]\]")
MARKDOWN_LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\([^)\n]*\)")
COMMENT = re.compile(r"%%.*?%%|<!--.*?-->", re.S)
FOOTNOTE = re.compile(r"\[\^[^\]\n]+\](?::[^\n]*)?")
HEADING = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", re.M)
CLOSES_SENTENCE = (".", "!", "?", "…", ":", ";")

# Markdown markup is not language. An asterisk, a backtick, a quote mark and a
# rule stand for something a reader sees and a listener does not hear. The
# model reads them along with the text.
BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
ITALIC = re.compile(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])")
UNDERSCORED = re.compile(r"(?<![\w_])_{1,2}(?!\s)([^_\n]+?)(?<!\s)_{1,2}(?![\w_])")
HIGHLIGHTED = re.compile(r"==(.+?)==", re.S)
STRICKEN = re.compile(r"~~(.+?)~~", re.S)
INLINE_CODE = re.compile(r"`+([^`\n]+?)`+")
QUOTE_MARK = re.compile(r"^[ \t]*>[ \t]?", re.M)
CALLOUT_MARK = re.compile(r"^\[![^\]\n]+\][-+]?[ \t]*", re.M)
RULE_LINE = re.compile(r"^[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*$", re.M)
BULLET = re.compile(r"^[ \t]*[-*+][ \t]+(.*?)[ \t]*$", re.M)
# A number at the start of a line is two things: a list marker, or an ordinal
# that a line break put there. `25.\nNovember` is no list item, and taking it
# for one swallows the date. A number counts only where a second one stands
# beside it, because a list has more than one item and a wrapped year has no
# neighbour.
NUMBERED = re.compile(r"^[ \t]*\d+[.)][ \t]+(.*?)[ \t]*$")
# A table and a code block are what a reader sees as a block. Read
# mechanically they are a row of dashes. What is to be said of them is
# sentences, and only someone who reads them can write those.
TABLE_ROW = re.compile(r"^[ \t]*\|.*\|[ \t]*$", re.M)
FENCE = re.compile(r"^[ \t]*(?:```|~~~)", re.M)


def sentence(line):
    """A heading or a list item spoken as a sentence, so it does not run into
    the next one."""
    line = line.strip()
    return line if not line or line.endswith(CLOSES_SENTENCE) else line + "."


def item(match):
    """A list item as its own sentence. A listener hears no bullet, and without
    a full stop the items of a list run together. A comma or semicolon at the
    end of an item is the punctuation of the list and not of the sentence, so
    it falls away."""
    return sentence(match.group(1).strip().rstrip(",;"))


def without_items(body):
    lines = body.split("\n")
    numbered = [bool(NUMBERED.match(line)) for line in lines]
    kept = []
    for index, line in enumerate(lines):
        match = NUMBERED.match(line)
        neighbour = (index and numbered[index - 1]) or (
            index + 1 < len(lines) and numbered[index + 1])
        kept.append(item(match) if match and neighbour else line)
    return BULLET.sub(item, "\n".join(kept))


def without_markup(body):
    """Markup out, text in: bold, italic, highlighted, struck, inline code, the
    quote mark, a callout heading, a rule."""
    body = RULE_LINE.sub("", body)
    body = QUOTE_MARK.sub("", body)
    body = CALLOUT_MARK.sub("", body)
    body = INLINE_CODE.sub(r"\1", body)
    body = BOLD.sub(r"\1", body)
    body = HIGHLIGHTED.sub(r"\1", body)
    body = STRICKEN.sub(r"\1", body)
    body = ITALIC.sub(r"\1", body)
    return UNDERSCORED.sub(r"\1", body)


def resolve_links(body):
    """A wikilink becomes its alias, because that is what a listener hears."""
    return WIKILINK.sub(lambda m: (m.group(2) or m.group(1).split("/")[-1]).strip(), body)


def flattened(part):
    """A paragraph as one line, unless it carries a block structure. Pulling a
    table into one line makes it unreadable, and read it must whoever dissolves
    it into sentences."""
    lines = [" ".join(line.split()) for line in part.split("\n") if line.strip()]
    broken = any(TABLE_ROW.match(line) or FENCE.match(line) for line in lines)
    return ("\n" if broken else " ").join(lines)


def wording(note):
    """What a listener hears of one note, as plain paragraphs."""
    text = note.read_text(encoding="utf-8-sig")
    head = FRONTMATTER.match(text)
    title = ""
    if head:
        named = TITLE.search(head.group(0))
        title = named.group(1).strip().strip('"\'') if named else ""
        text = text[head.end():]
    text = COMMENT.sub("", text)
    text = EMBED.sub("", text)
    text = resolve_links(text)
    text = MARKDOWN_LINK.sub(r"\1", text)
    text = FOOTNOTE.sub("", text)
    text = without_markup(text)
    text = without_items(text)
    text = HEADING.sub(lambda match: sentence(match.group(1)), text)
    paragraphs = [flattened(part) for part in re.split(r"\n\s*\n", text)]
    parts = [part for part in paragraphs if part]
    if title:
        parts.insert(0, sentence(title))
    return "\n\n".join(parts)


# --- What is still unspoken ----------------------------------------------
AROUND = ".,;:!?()[]„“»«\"'–—"
AROUND_NUMBER = AROUND.replace(".", "")
WITH_DIGIT = re.compile(r"\S*\d\S*")
# A Roman numeral carries no digit, so the digit check never finds it. Read it
# must be all the same, and not uniformly: `Wilhelm II.` is `Wilhelm der
# Zweite`, `Kapitel IV` is `Kapitel vier`. Searching takes two steps, because
# the grammar of a Roman numeral also fits the empty string.
NUMERAL_RUN = re.compile(r"\b[IVXLCDM]{2,}\b")
NUMERAL = re.compile(r"M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")
# Capitalised words that are also valid Roman numerals. They stand here so the
# hint does not fire on every CD. There is no ruler numbered forty or nine
# hundred.
NOT_NUMERALS = frozenset({"CD", "CM", "MM", "MIX", "MIL", "XL"})
# Signs a reader sees and a speech model has to guess: superscripts, currency
# and arithmetic, the slash as `per`.
WITH_SIGN = re.compile(r"\S*[²³¹⁴-⁹½¼¾€£$¥%‰°=+×·÷±<>≈≠→/§&]\S*")
# Unit abbreviations that stand without a sign and without a digit. The list is
# a hint and not a standard. Single letters are not in it, because they almost
# always hang on a number and the digit hint shows them already.
UNITS = frozenset("mm cm dm km ml cl dl mg kg min Hz kHz MHz kW kWh MW kJ"
                  " Pa bar ha nm mol kcal PS mph ccm".split())


def number(token):
    """A reported number without the punctuation around it, but with its full
    stop. On a number the full stop is the question: `25.` is an ordinal or the
    end of a sentence, and both look the same."""
    bare = token.strip(AROUND)
    dotted = (bare and bare[-1].isdigit()
              and token.rstrip(AROUND_NUMBER).endswith("."))
    return bare + "." if dotted else bare


def digits(text):
    found = {number(token) for token in WITH_DIGIT.findall(text)}
    found.discard("")
    return sorted(found)


def numerals(text):
    return sorted({run for run in NUMERAL_RUN.findall(text)
                   if run not in NOT_NUMERALS and NUMERAL.fullmatch(run)})


def signs(text):
    """A unit abbreviation inside a place already reported is not named twice:
    `km/h` is one place and not three."""
    found = {token.strip(AROUND) for token in WITH_SIGN.findall(text)}
    found.discard("")
    shown = " ".join(found)
    found.update(word for word in re.findall(r"\b[A-Za-z]{2,4}\b", text)
                 if word in UNITS and word not in shown)
    return sorted(found)


def unreadable(text):
    return [name for name, pattern in (("table", TABLE_ROW), ("code block", FENCE))
            if pattern.search(text)]


# --- What the rewriting lost ---------------------------------------------
# A comparison between wording and reading version must not hold on to
# numbers, because rewriting them is the purpose. Every digit sequence, every
# number word and every Roman numeral becomes a placeholder. Standing in the
# place is its whole job, because that is how the comparison tells a
# replacement from a disappearance. Placeholders are never counted.
#
# Measured against seven faults injected into a reading version, this form
# found five. A form that brackets only digits and leaves number words
# standing found four.
PLACEHOLDER = "#"
DIGITS = re.compile(r"\d")
NUMBER_WORD = frozenset("""
null ein eine einer eines einem einen eins zwei drei vier fünf sechs sieben
acht neun zehn elf zwölf dreizehn vierzehn fünfzehn sechzehn siebzehn achtzehn
neunzehn zwanzig dreißig vierzig fünfzig sechzig siebzig achtzig neunzig
hundert tausend million millionen milliarde milliarden
one two three four five six seven eight nine ten eleven twelve hundred
thousand million millions billion billions
""".split())
NUMBER_PART = re.compile(
    r"hundert|tausend|million|milliard|zwanzig|dreißig|vierzig|fünfzig"
    r"|sechzig|siebzig|achtzig|neunzig|teen|hundred")
# Number words that are also articles or pronouns. They stay words, or their
# loss would pass unseen. `ein Kilometer` out of `1 km` is no loss to the
# comparison anyway, but a replaced placeholder.
AMBIGUOUS = frozenset("ein eine einer eines einem einen one".split())


def numeric(word):
    return word in NUMBER_WORD or bool(NUMBER_PART.search(word))


def compared(text):
    """The words a comparison may hold on to."""
    words = []
    for raw in re.findall(r"\w+", text):
        word = raw.lower()
        number_like = (DIGITS.search(raw) or NUMERAL.fullmatch(raw)
                       or (word not in AMBIGUOUS and numeric(word)))
        words.append(PLACEHOLDER if number_like else word)
    return words


def without_blocks(text):
    """The wording without its block structures. A table and a code block are
    dissolved into sentences, and where they stood nothing of the same wording
    has to stand again."""
    kept, inside = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            inside = not inside
            continue
        if inside or TABLE_ROW.match(line):
            continue
        kept.append(line)
    return "\n".join(kept)


def losses(source, reading, around=5):
    """The places where the reading version loses words of the note, each with
    the number of words lost.

    Writing out replaces, it does not delete. Where `50.000` becomes
    `fünfzigtausend` and `m²` becomes `Quadratmeter`, something stands in that
    place again. Where a word disappears, the recording says something other
    than the note, and nobody hears that. Inserted words are no loss: a sign
    written out needs them, and `12,5 %` becomes `zwölf Komma fünf Prozent`.

    A comparison of word sequences cannot tell a move from a deletion, and the
    reading rules themselves prescribe two moves: `23:05 Uhr` becomes
    `dreiundzwanzig Uhr fünf`, and `mc²` becomes `m mal c Quadrat`. Both move
    or split a single word. So this check counts how many words are missing in
    one place. One can be a prescribed rewriting. Two in a row cannot.
    """
    want, got = compared(without_blocks(source)), compared(reading)
    places = []
    for tag, i1, i2, _, _ in difflib.SequenceMatcher(
            None, want, got, autojunk=False).get_opcodes():
        if tag != "delete":
            continue
        lost = [word for word in want[i1:i2] if word != PLACEHOLDER]
        if lost:
            before = " ".join(want[max(0, i1 - around):i1])
            places.append((len(lost), f"…{before} «{' '.join(lost)}»"))
    return places


# --- The two commands ----------------------------------------------------
def report(label, found, limit=10):
    if not found:
        return
    shown = ", ".join(found[:limit])
    more = f" and {len(found) - limit} more" if len(found) > limit else ""
    print(f"{label}: {shown}{more}")


def command_wording(args):
    text = wording(args.note)
    target = Path(args.output) if args.output else args.note.with_suffix(".txt")
    if target.exists() and not args.force:
        sys.exit(f"{target} exists already. Pass --force to overwrite it.")
    target.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {target} ({len(text.split())} words).")
    print("Rewrite it into a reading version, then run: prepare.py check "
          f"{args.note} {target}")
    blocks = unreadable(text)
    if blocks:
        print(f"Dissolve into sentences: {' and '.join(blocks)}.")
    report("Digits", digits(text))
    report("Roman numerals", numerals(text))
    report("Signs and units", signs(text))
    return 0


def command_check(args):
    source = wording(args.note)
    reading = args.reading.read_text(encoding="utf-8-sig").strip()
    problems = 0
    blocks = unreadable(reading)
    if blocks:
        print(f"ERROR {' and '.join(blocks)} still in {args.reading}."
              " Read mechanically that is a row of dashes. Dissolve it into"
              " sentences.")
        problems += 1
    lost = losses(source, reading)
    gone = [place for count, place in lost if count > 1]
    single = [place for count, place in lost if count == 1]
    for place in gone:
        print(f"ERROR words of the note are missing: {place}")
    if gone:
        print("      Writing out replaces and does not delete. A recording"
              " that says something other than the note is worse than none.")
        problems += 1
    for place in single:
        print(f"HINT  one word is missing: {place}")
    if single:
        print("      A prescribed rewriting looks like this. So does a"
              " deletion.")
    report("HINT  digits left", digits(reading))
    report("HINT  Roman numerals left", numerals(reading))
    report("HINT  signs and units left", signs(reading))
    if problems:
        print(f"\n{problems} error(s). The reading version is not ready to be"
              " spoken.")
        return 1
    print("\nNo errors. The hints above are places to look at, not verdicts.")
    print("Of seven faults injected into a reading version this comparison"
          " found five, so a clean run is no proof that the text still says"
          " the same thing.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="prepare.py",
        description="Lay down the wording of a Markdown note, and check the"
                    " reading version made from it.")
    commands = parser.add_subparsers(dest="command", required=True)
    lay = commands.add_parser("wording", help="write the note's wording as a text file")
    lay.add_argument("note", type=Path, help="the Markdown note")
    lay.add_argument("-o", "--output", help="target file, NOTE.txt by default")
    lay.add_argument("--force", action="store_true", help="overwrite an existing target")
    lay.set_defaults(run=command_wording)
    look = commands.add_parser("check", help="check a reading version against its note")
    look.add_argument("note", type=Path, help="the Markdown note")
    look.add_argument("reading", type=Path, help="the reading version")
    look.set_defaults(run=command_check)
    args = parser.parse_args()
    try:
        return args.run(args)
    except OSError as error:
        sys.exit(f"Error: {error}")


if __name__ == "__main__":
    sys.exit(main())
