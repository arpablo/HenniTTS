# Reading version, English

What stands here governs rewriting a wording into a reading version. These
are reading rules, not writing rules: the note stays as it is.

## The principle

A speech model reads characters. `50,000` holds a comma, `1907/08` looks
like a fraction. Written out, the problem disappears, and the spoken form
becomes checkable: a recogniser normalises every number back to digits, but
a word it writes as a word.

Only what has one reading is written out. Where two readings are possible
and the context does not decide, ask rather than guess.

## Numbers and identifiers

- English convention: comma separates thousands, full stop separates
  decimals. Confirm it from the text.
- `50,000 people` → `fifty thousand people`.
- `1,234.50` → `one thousand two hundred thirty-four point five zero`.
  Decimals digit by digit, and meaningful zeros stay.
- `−3.05` → `minus three point zero five`, `12.5 %` → `twelve point five
  percent`.
- Magnitude and precision stay. `1.5 m` → `one point five million` only
  where `m` means million, otherwise metres. Never round.
- **An identifier does not become a quantity.** Version numbers, postcodes,
  phone numbers, case numbers and account numbers keep their shape.
  `Version 1.2.0` → `version one point two point zero`, and a phone number
  is never pulled together into one large number.
- A digit left standing in a reading version is a decision, not a leftover.
  The check names every such place as a hint.

## Roman numerals

A Roman numeral carries no digit, so the digit hint never finds it and the
the check names it separately. It has two readings, and which one holds depends on
whether a person is being counted or a thing.

- **A regnal name takes an ordinal with its article.** `Henry VIII` →
  `Henry the Eighth`, `under Henry VIII` → `under Henry the Eighth`, `Louis
  XIV` → `Louis the Fourteenth`, `Pius XII` → `Pius the Twelfth`.
- **A count without a person takes a cardinal and no article.**
  `Chapter IV` → `Chapter four`, `Part II` → `Part two`, `Volume III` →
  `Volume three`.
- A full stop after the numeral, as German sources carry it, is the ordinal
  mark and not the end of a sentence. Writing the numeral out removes it,
  and with it the false sentence break the speech model would hear there.
- A century in Roman numerals, as it comes from other languages: `XIX
  century` → `nineteenth century`.
- What looks like a numeral and is none stays: `CD`, `CIA`, `MI6`, `LLM`.
  The check holds back a short list of such words. Whatever it still
  reports is examined, not rewritten blindly.

## Money

- `£12.50` → `twelve pounds fifty`, `$0.05` → `five cents`.
- The source's currency stays. A bare `$` does not become US dollars
  without context.
- Historical currency as the text carries it: `1 shilling and 4 pence`
  stays, `15 rupees` becomes `fifteen rupees`.

## Units, signs, formulas

A unit abbreviation carries no digit, and a sign has no pronunciation at all.
The check names both, because an abbreviation often has more than one reading.

- **The unit is written out and agrees with its value.** `3.5 km` → `three
  point five kilometres`, `1 km` → `one kilometre`, `250 ml` → `two hundred
  and fifty millilitres`, `7 kg` → `seven kilograms`, `15 min` → `fifteen
  minutes`, `100 kWh` → `one hundred kilowatt hours`.
- **A superscript on a unit becomes part of the word, on a quantity it is
  spoken.** `m²` → `square metres`, `m³` → `cubic metres`, but `c²` →
  `c squared`, `x³` → `x cubed`, `10⁶` → `ten to the sixth`.
- **A slash is `per` in a unit and `divided by` in a calculation.** `km/h` →
  `kilometres per hour`, `mg/l` → `milligrams per litre`, `m/s` → `metres
  per second`. Which one it is, the context says.
- `20 °C` → `twenty degrees Celsius`, an angle `20°` → `twenty degrees`,
  `12.5 %` → `twelve point five per cent`, `3 ‰` → `three per mille`,
  `§ 5` → `section five`.
- Operators become words: `=` `equals`, `+` `plus`, `−` `minus`, `×` and
  `·` `times`, `<` `less than`, `>` `greater than`, `≈` `about`, `±` `plus
  or minus`. An `→` is read for its sense, `gives` or `leads to`, and not
  described as an arrow.
- **A formula becomes a sentence,** and the invisible multiplication between
  two quantities is spoken. `E = mc²` → `E equals m times c squared`,
  `a² + b² = c²` → `a squared plus b squared equals c squared`.
- An abbreviation with two meanings is not guessed: `m` metre or minute,
  `t` ton or time, `s` second or page, `h` hour or height. Here one asks.
- Historical and non-metric units as the text carries them: `3 feet`,
  `2 inches`, `10 miles` stay what they are.
- Dosages and technical figures are never converted.

## Years, dates, spans

- `1890` → `eighteen ninety`, `1907` → `nineteen oh seven`, `2026` → `twenty
  twenty-six`.
- `on 3 April 2026` → `on the third of April twenty twenty-six`. A date
  written `03/04/2026` is ambiguous between British and American order and
  is not resolved from the output language alone.
- ISO `2026-04-03` is unambiguous.
- **`1907/08` has three readings** and is resolved only from the context:
  span → `nineteen oh seven to nineteen oh eight`, season or financial year
  → `nineteen oh seven oh eight`, two separate years → write both out.
- `23:05` → `eleven oh five at night` or `twenty-three oh five`, following
  the register of the text.
- `5–7 kg` → `five to seven kilograms`. A minus sign is not a range by
  itself.
- `19th century` → `nineteenth century`.

## Abbreviations and names

- `e.g.` → `for example`, `i.e.` → `that is`, `cf.` → `compare`, `No. 5` →
  `number five`, `p. 12` → `page twelve`, `Dr.` → `Doctor` where a title is
  meant.
- **An abbreviation is either expanded or left standing.** It is expanded
  where the text gives its meaning: with `the West African Currency Board,
  the WACB` in the text, every later mention reads `West African Currency
  Board`. Otherwise it stays as it stands. That decision belongs to the
  text, and the cases already decided are in `dictionary-en.json`.
- **Whether a model says `NASA` as a word and `BBC` letter by letter is not
  a question of the text.** It is a question of the model. A reading version
  does not rewrite `BBC` into `B B C` to make it sound spelled, it leaves
  `BBC` standing. Where a model audibly says it wrong, write the phonetic
  spelling into the reading version by hand and record the case in the
  dictionary, so the decision is not lost. That holds for that one model and
  says nothing about the text.
- Proper names stay. A phonetic respelling serves the model and not the
  text, and it is written in only where a model audibly says the name
  wrong.
- Foreign phrases stay in their language and are not translated.

## Tables and blocks

The check does not let a table through. It refuses the text and asks for the
table in sentences. Dissolved into sentences means: what the table shows, in the order
a reader reads it, without repeating the header row. Depending on the table
that is one sentence per row or one paragraph for the whole. Nothing is left
out and nothing is added. A table that merely lists becomes a list in
sentences.

The same holds for a code block. It may not vanish in silence: what is to be
heard of it stands as a sentence in the reading version.

## What the tool has already done

List markers, asterisks, backticks, quote marks and rules are out of the
wording before it is laid down, and each list item stands as its own
sentence. `prepare.py wording` did that, and nothing is left to do there. What still stands in the wording
stands there because someone has to read it.

## What does not happen

Nothing is summarised, explained, smoothed or added. No transition, no
comment, no preamble. Negations, qualifications, quotations and order stay.
Grammar is adjusted only as far as writing out forces it.
