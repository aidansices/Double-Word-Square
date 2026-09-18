# Playable 5x5 Double Word Squares for Scrabble

`double_word_square.py` searches a Scrabble lexicon for 5x5 grids where

* all five **rows** are valid 5-letter words,
* all five **columns** are valid 5-letter words,
* **no word is used both across and down** (a *double* word square, as opposed
  to the symmetric kind where column *i* repeats row *i*), and
* the grid can actually be **built over the board**, tile by tile, without ever
  exposing a non-word.

That last constraint is the interesting one.

## The waffle build order

The grid is assembled as

```
1. Row 3          2-4. Col 1, Col 3, Col 5      5-6. Row 1, Row 5
```

which leaves four empty squares — (2,2), (2,4), (4,2), (4,4) — hence "waffle":

```
      c1 c2 c3 c4 c5
 r1    #  #  #  #  #
 r2    #  .  #  .  #
 r3    #  #  #  #  #
 r4    #  .  #  .  #
 r5    #  #  #  #  #
```

Every move up to this point forms exactly one new word: the column plays run
through the single letter Row 3 already put on them, and the tiles Row 1 and
Row 5 add at columns 2 and 4 sit next to *empty* squares vertically, so they
form no cross-word.

The grid is then finished in one of two orders, and only that last pair of
moves can expose a fragment:

* **Top-down** — play Row 2, which gives columns 2 and 4 a contiguous run of
  three tiles (rows 1–2–3), then Row 4 completes them to five.
  → **Condition A**: `col2[1:3]` and `col4[1:3]` must both be valid 3-letter words.
* **Bottom-up** — play Row 4 first, exposing rows 3–4–5 instead.
  → **Condition B**: `col2[3:5]` and `col4[3:5]` must both be valid 3-letter words.

A grid is playable if it satisfies A **or** B. Note that no 2-letter or
4-letter fragment is ever created: the holes are positioned so columns 2 and 4
jump straight from three tiles to five.

## Plugging in a dictionary

Any plain-text word list works — one word per line, case-insensitive; anything
after the first whitespace on a line (a definition, a score) is ignored, and
entries that aren't pure A–Z are dropped.

```bash
python3 double_word_square.py --dict /path/to/twl06.txt
```

Word lists to use:

| List | What it is | Typical filename |
|---|---|---|
| **TWL06 / TWL2014 / NWL** | North American club & tournament list | `twl06.txt` |
| **SOWPODS / Collins** | International list (larger) | `sowpods.txt`, `collins.txt` |
| **ENABLE1** | Public domain, the basis of several of the above | `enable1.txt` |

Search GitHub for "scrabble dictionary txt" — the file is about 2 MB and
several mirrors exist. With no `--dict`, the script looks for common filenames
(`dictionary.txt`, `words.txt`, `twl06.txt`, `sowpods.txt`, …) in the working
directory and finally falls back to `/usr/share/dict/words`, which is **not**
Scrabble-legal and only exists so the script runs at all — it warns when it
does this.

`--dict` is repeatable, and `--dict3` takes a separate list for the
intermediate 3-letter words if you want those judged differently.

## Usage

```bash
# first 10 playable squares (5 top-down, 5 bottom-up)
python3 double_word_square.py -d twl06.txt

# 25 random ones, different every run, with a time budget
python3 double_word_square.py -d twl06.txt -n 25 --shuffle --time-limit 60

# only bottom-up-finishable grids, built around a chosen centre row
python3 double_word_square.py -d twl06.txt --condition b --row 3=ROBOT

# how many Condition-A squares exist in total?
python3 double_word_square.py -d twl06.txt --count-only --condition a
```

| Flag | Meaning |
|---|---|
| `-d, --dict FILE` | word list (repeatable) |
| `--dict3 FILE` | separate list for the 3-letter intermediates |
| `-n, --limit N` | stop after N squares (`0` = unlimited, default 10) |
| `--condition {a,b,either}` | which finishing order to require (default `either`) |
| `--row N=WORD` | pin a row, e.g. `--row 3=ROBOT` (repeatable) |
| `--time-limit SEC` | give up after SEC seconds |
| `--shuffle` / `--seed N` | randomise letter order so runs differ / are reproducible |
| `--allow-repeats` | allow a word twice among the rows or twice among the columns (across/down overlap is always forbidden) |
| `--count-only` | count without printing |

Sample output:

```
================================================================
Grid #3   --   either finish works (Row 2 first or Row 4 first)
================================================================
       c1 c2 c3 c4 c5
   r1   S  T  O  M  P
   r2   L  O  B  A  R
   r3   A  R  O  S  E
   r4   T  A  L  E  S
   r5   S  H  I  R  E

   Across : STOMP, LOBAR, AROSE, TALES, SHIRE
   Down   : SLATS, TORAH, OBOLI, MASER, PRESE

   Build  : Row 3 -> Col 1 -> Col 3 -> Col 5 -> Row 1 -> Row 5
            -> Row 2   (exposes TOR in col 2 and MAS in col 4)
            -> Row 4   (completes the square)
            or
            -> Row 4   (exposes RAH in col 2 and SER in col 4)
            -> Row 2   (completes the square)
```

Without `--shuffle` the output is deterministic for a given lexicon.

## How it works

Brute force over 26^25 grids is hopeless, and even "iterate over triples of
5-letter words for rows 1/3/5" costs |W5|^3 ≈ 10^12 with a real lexicon.
Instead the search is a CSP/backtracking walk over the 25 cells in row-major
order, driven by tries:

* one trie for the row being filled, and the same trie tracking, per column,
  the node reached by that column's prefix;
* at cell *(r, c)* the legal letters are
  `children(row_node) ∩ children(col_node[c])` — usually a handful, often
  none, so a dead column prefix like `SQ_` dies after one letter rather than
  after a whole word;
* on the last column the row node must be terminal; on the last row every
  column node must be terminal (and must not repeat a word already used
  across).

The waffle constraint folds into the same pruning on columns 2 and 4, using
the 3-letter lexicon flattened into three lookup tables (valid first letters /
valid second letters given the first / valid completions given the first two).
That enforces **Condition A** at rows 1–3, i.e. early.

**Condition B** constrains rows 3–5, so enforcing it directly would prune far
too late. Rather than write a second search, the same engine is run on the
vertically mirrored problem: rows are still 5-letter words (in the opposite
order), columns are read bottom-up and so are validated against a trie of
*reversed* 5-letter words, and the spine test becomes Condition A against
*reversed* 3-letter words. Mirroring the answers back yields exactly the
Condition-B grids, with Condition-A-strength pruning. `--condition either`
runs both passes and drops the overlap.

A pinned row (`--row`) fixes one letter of *every* column word, so each column
is given a trie holding only the words with that letter in that position. The
pruning then starts at row 1 instead of waiting until the pinned row is
reached — which matters in the mirrored pass, where `--row 1=…` lands on the
last row searched.

Every grid is re-derived and re-checked from scratch by `verify()` — which
shares no code with the search — before it is printed, so a bug in the fast
path cannot leak an invalid square into the output. The search was also
cross-checked grid-for-grid against a brute-force reference (whole-word
iteration, flat prefix set, no trie and no mirroring) over 18 exhaustive runs
with two rows pinned: identical result sets in every case.

Performance with a TWL list (8,938 five-letter words, 1,015 three-letter
words): the first ten squares come back in about 10 ms. The space is rich —
an exhaustive Condition-A count passes 40,000 squares in the first 20 seconds.

## Two caveats for actual play

The model covers the words the grid itself creates. Two things it can't know:

1. The first move (Row 3) has to hook into letters already on the board, and
   the whole figure has to fit the premium squares you're aiming at.
2. A 25-square figure is roughly 25 tiles across eight turns, so your opponent
   is also playing — anything they put adjacent to the waffle creates
   cross-words this program never saw.
