# The complete catalogue of playable double word squares in common English

All 15 of them.

These are the 5x5 double word squares — five words across, five different
words down — that can be built over a Scrabble board in the waffle order
without ever exposing a non-word, using only words an ordinary player would
recognise. "Recognise" here means the word appears in **both** a TWL Scrabble
list and the 20,000 commonest English words.

This is an exhaustive result, not a sample: the search explores the whole
space and finishes in about five seconds.

## Reproducing it

```bash
curl -o dictionary.txt https://raw.githubusercontent.com/redbo/scrabble/master/dictionary.txt
curl -O https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt
python3 double_word_square.py --common 20k.txt -n 0        # all of them
python3 double_word_square.py --common 20k.txt --count-only # just the count
```

The TWL file used here has 8,938 five-letter and 1,015 three-letter words;
intersected with the frequency list that falls to 1,973 and 599.

## The cliff

Tightening `--common-top` shrinks the lexicon, and the population collapses
far faster than the lexicon does. Every count below is exhaustive:

| `--common-top` | 5-letter words | playable squares |
|---:|---:|---:|
| 11,000 | 1,302 | 0 |
| 12,000 | 1,392 | 0 |
| 13,000 | 1,473 | 0 |
| 14,000 | 1,556 | 0 |
| 15,000 | 1,640 | 1 |
| 16,000 | 1,701 | 1 |
| 17,000 | 1,781 | 7 |
| 18,000 | 1,840 | 8 |
| 19,000 | 1,909 | 13 |
| 20,000 | 1,973 | 15 |

The lexicon grows 27% between 14,000 and 20,000; the population goes from
**none at all** to fifteen. At 15,000 words there is exactly one — grid 4
below, the unique minimal playable double word square in common English.

For contrast, the unrestricted TWL list passes 40,000 squares in the first
20 seconds of counting. Almost all of them lean on words like `ASKOS`.

## The squares

### 1. AWARD, THREE, LOOSE, ARMED, SEATS — either finish

```
   A  W  A  R  D
   T  H  R  E  E
   L  O  O  S  E
   A  R  M  E  D
   S  E  A  T  S

   across : AWARD, THREE, LOOSE, ARMED, SEATS
   down   : ATLAS, WHORE, AROMA, RESET, DEEDS
   Row 2 first, exposing WHO and RES
   Row 4 first, exposing ORE and SET
```

### 2. SAVES, OLIVE, LADEN, AMEND, ROOTS — top-down finish (Row 2, then Row 4)

```
   S  A  V  E  S
   O  L  I  V  E
   L  A  D  E  N
   A  M  E  N  D
   R  O  O  T  S

   across : SAVES, OLIVE, LADEN, AMEND, ROOTS
   down   : SOLAR, ALAMO, VIDEO, EVENT, SENDS
   Row 2 first, exposing ALA and EVE
```

### 3. SCARF, PAGER, ERASE, CRIES, SYNTH — top-down finish (Row 2, then Row 4)

```
   S  C  A  R  F
   P  A  G  E  R
   E  R  A  S  E
   C  R  I  E  S
   S  Y  N  T  H

   across : SCARF, PAGER, ERASE, CRIES, SYNTH
   down   : SPECS, CARRY, AGAIN, RESET, FRESH
   Row 2 first, exposing CAR and RES
```

### 4. SCARF, POLAR, ALONE, ROUGE, ENDED — top-down finish (Row 2, then Row 4)

```
   S  C  A  R  F
   P  O  L  A  R
   A  L  O  N  E
   R  O  U  G  E
   E  N  D  E  D

   across : SCARF, POLAR, ALONE, ROUGE, ENDED
   down   : SPARE, COLON, ALOUD, RANGE, FREED
   Row 2 first, exposing COL and RAN
```

### 5. SCRAP, THESE, RINSE, ALTER, PESTS — top-down finish (Row 2, then Row 4)

```
   S  C  R  A  P
   T  H  E  S  E
   R  I  N  S  E
   A  L  T  E  R
   P  E  S  T  S

   across : SCRAP, THESE, RINSE, ALTER, PESTS
   down   : STRAP, CHILE, RENTS, ASSET, PEERS
   Row 2 first, exposing CHI and ASS
```

### 6. SEALS, ORBIT, FAUNA, ASSET, SEEDS — top-down finish (Row 2, then Row 4)

```
   S  E  A  L  S
   O  R  B  I  T
   F  A  U  N  A
   A  S  S  E  T
   S  E  E  D  S

   across : SEALS, ORBIT, FAUNA, ASSET, SEEDS
   down   : SOFAS, ERASE, ABUSE, LINED, STATS
   Row 2 first, exposing ERA and LIN
```

### 7. SOFAS, ERASE, ABUSE, LINED, STATS — either finish

```
   S  O  F  A  S
   E  R  A  S  E
   A  B  U  S  E
   L  I  N  E  D
   S  T  A  T  S

   across : SOFAS, ERASE, ABUSE, LINED, STATS
   down   : SEALS, ORBIT, FAUNA, ASSET, SEEDS
   Row 2 first, exposing ORB and ASS
   Row 4 first, exposing BIT and SET
```

### 8. STAMP, THREE, ROOTS, ASSET, PEERS — top-down finish (Row 2, then Row 4)

```
   S  T  A  M  P
   T  H  R  E  E
   R  O  O  T  S
   A  S  S  E  T
   P  E  E  R  S

   across : STAMP, THREE, ROOTS, ASSET, PEERS
   down   : STRAP, THOSE, AROSE, METER, PESTS
   Row 2 first, exposing THO and MET
```

### 9. STRAP, CHILE, RENTS, ASSET, PEERS — top-down finish (Row 2, then Row 4)

```
   S  T  R  A  P
   C  H  I  L  E
   R  E  N  T  S
   A  S  S  E  T
   P  E  E  R  S

   across : STRAP, CHILE, RENTS, ASSET, PEERS
   down   : SCRAP, THESE, RINSE, ALTER, PESTS
   Row 2 first, exposing THE and ALT
```

### 10. SWAMP, THREE, ROOTS, ASSET, PEERS — top-down finish (Row 2, then Row 4)

```
   S  W  A  M  P
   T  H  R  E  E
   R  O  O  T  S
   A  S  S  E  T
   P  E  E  R  S

   across : SWAMP, THREE, ROOTS, ASSET, PEERS
   down   : STRAP, WHOSE, AROSE, METER, PESTS
   Row 2 first, exposing WHO and MET
```

### 11. TALES, OLIVE, RAVEN, AMEND, HOSTS — top-down finish (Row 2, then Row 4)

```
   T  A  L  E  S
   O  L  I  V  E
   R  A  V  E  N
   A  M  E  N  D
   H  O  S  T  S

   across : TALES, OLIVE, RAVEN, AMEND, HOSTS
   down   : TORAH, ALAMO, LIVES, EVENT, SENDS
   Row 2 first, exposing ALA and EVE
```

### 12. THUMB, RURAL, AMINO, CONGO, TREAD — top-down finish (Row 2, then Row 4)

```
   T  H  U  M  B
   R  U  R  A  L
   A  M  I  N  O
   C  O  N  G  O
   T  R  E  A  D

   across : THUMB, RURAL, AMINO, CONGO, TREAD
   down   : TRACT, HUMOR, URINE, MANGA, BLOOD
   Row 2 first, exposing HUM and MAN
```

### 13. THUMB, RURAL, AMINO, PANIC, SNEAK — top-down finish (Row 2, then Row 4)

```
   T  H  U  M  B
   R  U  R  A  L
   A  M  I  N  O
   P  A  N  I  C
   S  N  E  A  K

   across : THUMB, RURAL, AMINO, PANIC, SNEAK
   down   : TRAPS, HUMAN, URINE, MANIA, BLOCK
   Row 2 first, exposing HUM and MAN
```

### 14. GRASS, HELLO, OPTIC, SLACK, TYRES — bottom-up finish (Row 4, then Row 2)

```
   G  R  A  S  S
   H  E  L  L  O
   O  P  T  I  C
   S  L  A  C  K
   T  Y  R  E  S

   across : GRASS, HELLO, OPTIC, SLACK, TYRES
   down   : GHOST, REPLY, ALTAR, SLICE, SOCKS
   Row 4 first, exposing PLY and ICE
```

### 15. COSTA, APART, METAL, ERICA, LANES — bottom-up finish (Row 4, then Row 2)

```
   C  O  S  T  A
   A  P  A  R  T
   M  E  T  A  L
   E  R  I  C  A
   L  A  N  E  S

   across : COSTA, APART, METAL, ERICA, LANES
   down   : CAMEL, OPERA, SATIN, TRACE, ATLAS
   Row 4 first, exposing ERA and ACE
```

## Notes

Some grids are transposes of one another (5 and 9, 6 and 7). Transposing a
double word square gives another one — across and down simply swap — but the
waffle test is not symmetric under transposition, so a square and its
transpose can differ in which finishing orders are legal: grid 6 can only be
finished top-down, while its transpose, grid 7, can be finished either way.
They are listed separately because they are different grids to play, not the
same square written twice.

"Common" is a judgement call baked into the frequency list. A different list
moves the threshold and changes which grids survive — the shape of the curve
is robust, the number 15 is not. `TYRES` in grid 14 is the British spelling;
`COSTA` and `ERICA` in grid 15 are the weakest entries here, and `WHORE` in
grid 1 is recognisable but not what you want to put on the board at a family
occasion.
