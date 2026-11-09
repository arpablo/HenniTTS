# Lesefassung, deutsch

Was hier steht, gilt für das Umschreiben eines Wortlaufs in eine
Lesefassung. Es sind Leseregeln und keine Schreibregeln: Die Notiz bleibt,
wie sie ist.

## Der Grundsatz

Ein Sprechmodell liest Zeichen. `50.000` enthält einen Punkt, und Ollama
nimmt ihn für ein Satzende. Ausgeschrieben verschwindet das Problem, und
zugleich wird die gesprochene Form prüfbar: Ein Erkenner normalisiert jede
Zahl zu Ziffern, ein Wort aber schreibt er als Wort.

Ausgeschrieben wird nur, was eine Lesart hat. Wo zwei Lesarten möglich sind
und der Zusammenhang nicht entscheidet, wird gefragt und nicht geraten.

## Zahlen und Kennungen

- Deutsche Konvention: Punkt trennt Tausender, Komma trennt Dezimalstellen.
  Erst am Text bestätigen. Eine aus dem Englischen übernommene Zahl kann es
  anders halten.
- `50.000 Menschen` → `fünfzigtausend Menschen`.
- `1.234,50` → `eintausendzweihundertvierunddreißig Komma fünf null`.
  Nachkommastellen ziffernweise, bedeutungstragende Nullen bleiben.
- `−3,05` → `minus drei Komma null fünf`.
- Größenordnung und Genauigkeit bleiben. `1,5 Mio.` → `eine Komma fünf
  Millionen`. Kasus und Numerus anpassen, nie runden.
- **Eine Kennung wird nicht zur Menge.** Versionsnummern, Postleitzahlen,
  Telefonnummern, Aktenzeichen, Kontonummern behalten ihre Gestalt.
  `Version 1.2.0` → `Version eins Punkt zwei Punkt null`, und eine
  Telefonnummer wird nie zu einer großen Zahl zusammengezogen.
- Eine Ziffer, die in der Lesefassung stehen bleibt, ist eine Entscheidung
  und kein Rest. Die Prüfung nennt jede solche Stelle als Hinweis.

## Römische Zahlen

Eine römische Zahl trägt keine Ziffer. Der Ziffernhinweis findet sie darum
nicht, und die Prüfung nennt sie eigens. Gelesen wird sie auf zwei Arten, und
welche gilt, entscheidet, ob eine Person gezählt wird oder eine Sache.

- **Ein Herrschername bekommt Ordnungszahl, Artikel und Kasus aus dem Satz.**
  `Wilhelm II.` → `Wilhelm der Zweite`, `unter Wilhelm II.` → `unter Wilhelm
  dem Zweiten`, `die Flotte Wilhelms II.` → `die Flotte Wilhelms des
  Zweiten`. Ebenso `Ludwig XIV.` → `Ludwig der Vierzehnte`, `Pius XII.` →
  `Pius der Zwölfte`.
- **Eine Zählung ohne Person bekommt die Grundzahl und keinen Artikel.**
  `Kapitel IV` → `Kapitel vier`, `Teil II` → `Teil zwei`, `Band III` →
  `Band drei`, `Anforderungsbereich II` → `Anforderungsbereich zwei`.
- Der Punkt hinter der Zahl ist das Ordnungszeichen und kein Satzende.
  Ausgeschrieben verschwindet er, und mit ihm der falsche Satzschluss, den
  das Sprechmodell sonst dort hört.
- Ein Jahrhundert in römischen Zahlen, wie es aus fremdsprachigen Quellen
  kommt: `XIX. Jahrhundert` → `neunzehnten Jahrhundert`, Kasus aus dem Satz.
- Was wie eine römische Zahl aussieht und keine ist, bleibt: `CD`, `CIA`,
  `MI6`, `LLM`. Die Prüfung hält eine kurze Liste solcher Wörter zurück.
  Was sie dennoch meldet, wird geprüft und nicht blind umgeschrieben.

## Geld

- `12,50 €` → `zwölf Euro und fünfzig Cent`, `0,05 €` → `fünf Cent`.
- Die Währung der Quelle bleibt. Ein alleinstehendes `$` wird ohne
  Zusammenhang nicht zu US-Dollar, `£` nicht zu Pfund Sterling.
- Historische Währungen so, wie der Text sie führt: `1 Schilling und 4 Pence`
  bleibt, `15 Rupien` wird `fünfzehn Rupien`.

## Einheiten, Zeichen und Formeln

Ein Einheitenkürzel ist eine Abkürzung ohne Ziffer, und ein Zeichen hat gar
keine Aussprache. Die Prüfung nennt beides, weil ein Kürzel oft mehr als eine
Lesart hat.

- **Die Einheit wird ausgeschrieben und richtet sich in Zahl und Kasus nach
  ihrem Wert.** `3,5 km` → `drei Komma fünf Kilometer`, `1 km` → `ein
  Kilometer`, `250 ml` → `zweihundertfünfzig Milliliter`, `7 kg` → `sieben
  Kilogramm`, `15 min` → `fünfzehn Minuten`, `100 kWh` → `hundert
  Kilowattstunden`.
- **Eine Hochzahl an einer Einheit wird Teil des Wortes, an einer Größe wird
  sie gesprochen.** `m²` → `Quadratmeter`, `m³` → `Kubikmeter`, `cm³` →
  `Kubikzentimeter`, dagegen `c²` → `c Quadrat`, `x³` → `x hoch drei`,
  `10⁶` → `zehn hoch sechs`.
- **Der Schrägstrich heißt in einer Einheit `pro`, in einer Rechnung
  `geteilt durch`.** `km/h` → `Kilometer pro Stunde`, `mg/l` → `Milligramm
  pro Liter`, `m/s` → `Meter pro Sekunde`. Welches von beidem gemeint ist,
  sagt der Zusammenhang.
- `20 °C` → `zwanzig Grad Celsius`, ein Winkel `20°` → `zwanzig Grad`,
  `12,5 %` → `zwölf Komma fünf Prozent`, `3 ‰` → `drei Promille`, `§ 5` →
  `Paragraf fünf`.
- Rechenzeichen werden Wörter: `=` `ist gleich`, `+` `plus`, `−` `minus`,
  `×` und `·` `mal`, `<` `kleiner als`, `>` `größer als`, `≈` `etwa`,
  `±` `plus minus`. Ein `→` wird nach seinem Sinn gelesen, `ergibt` oder
  `führt zu`, und nicht als Pfeil beschrieben.
- **Eine Formel wird ein Satz,** und das unsichtbare Malzeichen zwischen
  zwei Größen wird gesprochen. `E = mc²` → `E ist gleich m mal c Quadrat`,
  `a² + b² = c²` → `a Quadrat plus b Quadrat ist gleich c Quadrat`.
- Ein Kürzel mit zwei Bedeutungen wird nicht geraten: `m` Meter oder Minute,
  `t` Tonne oder Zeit, `a` Jahr oder Ar, `s` Sekunde oder Seite, `h` Stunde
  oder Höhe. Hier wird gefragt.
- Historische und nichtmetrische Einheiten so, wie der Text sie führt:
  `3 Fuß`, `2 Zoll`, `10 Meilen` bleiben, was sie sind.
- Dosierungen und technische Angaben werden nie umgerechnet.

## Jahre, Daten, Zeiträume

- `1890` → `achtzehnhundertneunzig`, `1907` → `neunzehnhundertsieben`,
  `2026` → `zweitausendsechsundzwanzig`.
- `am 03.04.2026` bei bestätigtem deutschem Datum → `am dritten April
  zweitausendsechsundzwanzig`. Der Kasus kommt aus dem Satz.
- ISO `2026-04-03` ist eindeutig. Ein Datum mit Schrägstrich wird nicht
  allein wegen der Ausgabesprache als Tag/Monat gelesen.
- **`1907/08` hat drei Lesarten** und wird nur bei belegtem Zusammenhang
  aufgelöst: Zeitraum → `neunzehnhundertsieben bis neunzehnhundertacht`,
  Saison oder Rechnungsjahr → `neunzehnhundertsieben null acht`, zwei
  Jahresangaben → beide ausschreiben. `im Rechnungsjahr 1911/12` ist ein
  Rechnungsjahr, `der Winter 1907/08` ein Zeitraum.
- `23:05 Uhr` → `dreiundzwanzig Uhr fünf`.
- `5–7 kg` → `fünf bis sieben Kilogramm`. Ein Minuszeichen ist nicht von
  selbst ein Bereich.
- Ein Jahrhundert: `19. Jahrhundert` → `neunzehnten Jahrhundert`, Kasus aus
  dem Satz.

## Abkürzungen und Namen

- `z. B.` → `zum Beispiel`, `bzw.` → `beziehungsweise`, `u. a.` nur bei
  klarem Sinn, und `Dr.` → `Doktor`, wenn ein Titel gemeint ist.
- `Nr. 5` → `Nummer fünf`, `S. 12` → `Seite zwölf`, `vgl.` → `vergleiche`.
- **Ein Kürzel wird aufgelöst oder es bleibt stehen.** Aufgelöst wird es,
  wo der Text seine Bedeutung nennt: Steht `das West African Currency
  Board, kurz WACB` im Text, heißt es danach `West African Currency Board`.
  Sonst bleibt es, wie es dasteht. Diese Entscheidung gehört dem Text, und
  entschiedene Fälle stehen im Wörterbuch `dictionary-de.json`.
- **Ob ein Modell `NASA` als Wort und `ADAC` als Buchstabenfolge sagt, ist
  keine Frage des Textes.** Es ist eine Frage des Modells. Eine Lesefassung
  schreibt `DIN` nicht zu `Din` um, damit es wie ein Wort klingt, sondern
  lässt `DIN` stehen. Sagt ein Modell es hörbar falsch, wird die lautnahe
  Schreibung von Hand in die Lesefassung geschrieben und der Fall im
  Wörterbuch vermerkt, damit die Entscheidung nicht verloren geht. Das gilt
  dann für dieses eine Modell und ist keine Aussage über den Text.
- Was nur aussieht wie ein Kürzel, ist keines. Ein Sprachkürzel in einem
  Titel, ein Namenszusatz, eine Spaltenbeschriftung bleiben, wie sie sind:
  `Probe DE` wird nicht `Probe D E`.
- Keine erfundene Langform.
- Eigennamen bleiben. Eine lautnahe Ersatzschreibung gilt dem Modell und
  nicht dem Text, und sie wird nur dort nachgetragen, wo ein Modell den
  Namen hörbar falsch sagt.
- Fremdsprachige Wendungen bleiben in ihrer Sprache und werden nicht
  übersetzt. `Council Bill` bleibt `Council Bill`.

## Tabellen und Blöcke

Eine Tabelle lässt die Prüfung nicht durch. Sie verweigert den Text und
verlangt, dass die Tabelle in Sätzen steht. Zu Sätzen aufgelöst heißt: was die Tabelle zeigt, in der
Reihenfolge, in der ein Leser sie liest, ohne die Kopfzeile zu wiederholen.
Je nach Tabelle wird daraus ein Satz pro Zeile oder ein Absatz für das Ganze.
Nichts wird weggelassen und nichts hinzugefügt. Eine Tabelle, die nur
aufzählt, wird eine Aufzählung in Sätzen.

Für einen Codeblock gilt dasselbe. Stillschweigend verschwinden darf er
nicht: Was von ihm zu hören ist, steht als Satz in der Lesefassung.

## Was das Werkzeug schon getan hat

Listenzeichen, Sternchen, Backticks, Zitatpfeile und Trennlinien sind aus dem
Wortlaut heraus, bevor er abgelegt wird, und jeder Listenpunkt steht als
eigener Satz. `prepare.py wording` hat das getan, und daran ist nichts
mehr zu tun. Was im Wortlaut noch steht, steht
dort, weil es jemand lesen muss.

## Was nicht geschieht

Nichts wird zusammengefasst, erklärt, geglättet oder ergänzt. Keine
Überleitung, kein Kommentar, keine Einleitung. Negationen, Einschränkungen,
Zitate und die Reihenfolge bleiben. Grammatik wird nur so weit angepasst,
wie das Ausschreiben sie erzwingt.
