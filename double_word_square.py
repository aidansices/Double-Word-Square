#!/usr/bin/env python3
"""
double_word_square.py -- find *playable* 5x5 Double Word Squares for Scrabble.

======================================================================
WHAT THIS PROGRAM LOOKS FOR
======================================================================
A 5x5 grid of letters where

    * each of the 5 rows is a valid 5-letter word,
    * each of the 5 columns is a valid 5-letter word,
    * no word is used both as a row and as a column
      (that is what makes it a *double* word square rather than an
      ordinary one, where row i and column i are the same word),

and -- the part that makes it actually buildable over a Scrabble board --
the grid can be laid down tile by tile in the "waffle" order

        1. Row 3     (the centre row)
        2. Column 1
        3. Column 3
        4. Column 5
        5. Row 1
        6. Row 5
        7. Row 2, then Row 4      <- "top-down finish"   (Condition A)
           or Row 4, then Row 2   <- "bottom-up finish"  (Condition B)

without ever putting a non-word on the board.

======================================================================
WHY THE WHOLE BUILD ORDER REDUCES TO TWO 3-LETTER CHECKS
======================================================================
Write the grid with 1-based (row, column) coordinates.  Steps 1-4 lay a
"#"-shaped skeleton: the centre row plus the three odd columns.  That
leaves exactly four empty squares -- (2,2), (2,4), (4,2) and (4,4) --
which is why the finished shape looks like a waffle.

Walk the moves and ask what words each one forms:

  Step 1  Row 3          : one 5-letter word.                       OK
  Steps   Col 1, 3, 5    : each column play runs through the single
   2-4                     letter already on it from Row 3, and forms
                           one 5-letter word.  The new tiles in rows
                           1, 2, 4, 5 are horizontally isolated
                           (their neighbours in columns 2 and 4 are
                           still empty), so no cross-words appear.     OK
  Step 5  Row 1          : adds only (1,2) and (1,4), completing the
                           Row 1 word.  Vertically each of those tiles
                           sits directly above an empty square -- (2,2)
                           and (2,4) -- so it forms no column word.     OK
  Step 6  Row 5          : adds only (5,2) and (5,4), completing the
                           Row 5 word.  Below them is nothing and above
                           them are the empty squares (4,2) and (4,4),
                           so again no column word forms.               OK
  Step 7  Row 2          : adds (2,2) and (2,4), completing the Row 2
                           word.  NOW column 2 has a contiguous run of
                           three tiles, rows 1-2-3, and so does column
                           4.  Those two 3-letter strings hit the board
                           as real words, so they MUST be valid.
                           ==> CONDITION A
  Step 8  Row 4          : adds (4,2) and (4,4), completing the Row 4
                           word and extending columns 2 and 4 to their
                           full 5 letters.                              OK

Play Row 4 before Row 2 instead and the same argument puts the
contiguous 3-letter runs in rows 3-4-5 of columns 2 and 4:

    CONDITION A (top-down) : col2[1:3] and col4[1:3] are both valid
                             3-letter words.
    CONDITION B (bottom-up): col2[3:5] and col4[3:5] are both valid
                             3-letter words.

A grid is playable if it satisfies A or B (either finishing order works;
satisfying both just gives the player a choice).  Note that no 2-letter
or 4-letter fragment is ever exposed by this sequence -- the empty
squares are placed so that columns 2 and 4 jump straight from "3 tiles"
to "5 tiles".  That is the whole point of the waffle.

======================================================================
ALGORITHM
======================================================================
Brute force over 26^25 grids is obviously hopeless, and even the
"iterate over triples of 5-letter words for rows 1/3/5" idea costs
|W5|^3 ~ 10^12 with a real Scrabble lexicon.  Instead this is a plain
CSP / backtracking search over the 25 cells in row-major order, with two
tries doing all the pruning work:

  * a trie of the 5-letter words used for the ROW currently being filled;
  * the same trie used to track, for every column, the node reached by
    the column's prefix so far.

At cell (r, c) the only legal letters are
      children(row_node)  INTERSECT  children(column_node_c)
which is usually a handful of letters and frequently empty -- a dead
prefix like "SQ_" in a column is killed after one letter rather than
after a whole word.  Two extra filters finish the job: on the last
column the row node must be terminal, and on the last row every column
node must be terminal.

The waffle constraint is folded into the same pruning, on the two
"spine" columns 2 and 4, using a 3-letter trie flattened into lookup
tables:

      row 1, col 2/4 : letter must start some 3-letter word
      row 2, col 2/4 : letter must extend that into a 3-letter prefix
      row 3, col 2/4 : letter must complete a valid 3-letter word

That enforces Condition A.  Condition B is the same constraint on rows
3-4-5, i.e. it only bites at the very end of the search, which prunes
far less.  So instead of writing a second search, Condition B is
obtained by running the *identical* Condition-A engine on a vertically
mirrored problem: mirror the grid top-to-bottom, and

      rows  : still 5-letter words (just in the opposite order)
      cols  : each column is read bottom-up, so validate against a trie
              of REVERSED 5-letter words
      cols 2/4, rows 1-2-3 of the mirrored grid, read bottom-up
            = rows 3-4-5 of the real grid  -> validate against REVERSED
              3-letter words

Mirroring the answer back at the end yields exactly the Condition-B
grids, found with Condition-A-strength pruning.  (`--condition either`
runs both and drops the duplicates, i.e. grids that satisfy both.)

Every grid is re-checked from scratch by `verify()` before it is
printed, so a bug in the fast path cannot leak a bad square into the
output.

======================================================================
PLUGGING IN A SCRABBLE DICTIONARY
======================================================================
Supply any plain-text word list: one word per line (anything after the
first whitespace on a line -- a definition, a score -- is ignored),
case-insensitive.  Words that are not pure A-Z are skipped.

    python3 double_word_square.py --dict /path/to/twl06.txt

You can pass --dict more than once (e.g. a 5-letter file and a
3-letter file), or point --dict3 at a separate list if you want the
intermediate 3-letter words judged by a different lexicon.

Where to get one:
    * TWL06 / TWL2014 (North American club+tournament word list)
    * SOWPODS / Collins ("sowpods.txt")
    * ENABLE1 ("enable1.txt") -- public domain, widely mirrored
Any of the many "scrabble dictionary txt" repositories on GitHub work;
the file is ~2 MB.  With no --dict the script looks for a few common
filenames in the working directory (see DEFAULT_DICT_PATHS) and falls
back to /usr/share/dict/words, which is NOT Scrabble-legal -- it is only
there so the script runs at all.

======================================================================
EXAMPLES
======================================================================
    # first 10 playable squares
    python3 double_word_square.py --dict twl06.txt

    # 25 random ones (different every run), 60-second budget
    python3 double_word_square.py -d twl06.txt -n 25 --shuffle --time-limit 60

    # only bottom-up-finishable grids, built around a given centre row
    python3 double_word_square.py -d twl06.txt --condition b --row 3=ROBOT

    # how many Condition-A squares exist at all? (long!)
    python3 double_word_square.py -d twl06.txt --count-only --condition a
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

# --------------------------------------------------------------------------
# Board geometry.  Everything below is written for a 5x5 board; the spine
# columns and the four holes are the waffle shape described in the header.
# --------------------------------------------------------------------------
N = 5                       # grid size
SPINE = (1, 3)              # 0-based columns 2 and 4: the ones that get the
                            # 3-letter intermediate test.  The four holes the
                            # waffle leaves are (1,1) (1,3) (3,1) (3,3).

DEFAULT_DICT_PATHS = (
    "scrabble.txt", "dictionary.txt", "words.txt", "wordlist.txt",
    "twl06.txt", "twl.txt", "sowpods.txt", "collins.txt", "enable1.txt",
    "/usr/share/dict/scrabble", "/usr/share/dict/words",
)

EMPTY: FrozenSet[str] = frozenset()


# ==========================================================================
# 1.  LEXICON
# ==========================================================================
def load_words(paths: Sequence[str], lengths: Iterable[int] = (3, 5),
               drop_capitalised: bool = False) -> Dict[int, Set[str]]:
    """Read one or more word-list files and bucket the words by length.

    * one word per line; text after the first whitespace is discarded so
      "AA  a type of lava" style files work too
    * words are upper-cased; non-ASCII / non-alphabetic words are dropped
    * `drop_capitalised` throws away entries that were not already all
      lower-case, which is how proper nouns get filtered out of
      /usr/share/dict/words.  Real Scrabble lists are usually ALL CAPS,
      so this is off unless we fall back to the system dictionary.
    """
    wanted = set(lengths)
    buckets: Dict[int, Set[str]] = {n: set() for n in wanted}
    for path in paths:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                parts = line.split()
                if not parts:
                    continue
                raw = parts[0]
                if len(raw) not in wanted:
                    continue
                if drop_capitalised and not raw.islower():
                    continue
                if not (raw.isascii() and raw.isalpha()):
                    continue
                buckets[len(raw)].add(raw.upper())
    return buckets


def load_common(path: str, top: Optional[int] = None) -> Set[str]:
    """Read a familiarity list -- words an ordinary player would recognise.

    Frequency lists are ordered commonest-first, so `top` simply takes the
    first N entries of the file.  Entries are counted before the A-Z filter,
    so "top 20000" means the file's first 20,000 lines whatever is in them.
    A "word 12345" count column is fine; only the first token is read.
    """
    keep: Set[str] = set()
    seen = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            parts = line.split()
            if not parts:
                continue
            seen += 1
            if top is not None and seen > top:
                break
            word = parts[0]
            if word.isascii() and word.isalpha():
                keep.add(word.upper())
    return keep


def resolve_dictionaries(explicit: Sequence[str]) -> Tuple[List[str], bool]:
    """Return (paths, drop_capitalised).  Falls back to system dictionaries."""
    if explicit:
        missing = [p for p in explicit if not os.path.exists(p)]
        if missing:
            raise SystemExit("dictionary file(s) not found: " + ", ".join(missing))
        return list(explicit), False
    for cand in DEFAULT_DICT_PATHS:
        if os.path.exists(cand):
            system = cand.startswith("/usr/share/dict/")
            if system:
                print("WARNING: no --dict given; falling back to %s, which is NOT a\n"
                      "         Scrabble word list.  Results will contain illegal words."
                      % cand, file=sys.stderr)
            return [cand], system
    raise SystemExit(
        "No dictionary found.  Pass one with --dict /path/to/scrabble_words.txt\n"
        "(see the module docstring for where to get a TWL/SOWPODS/ENABLE list)."
    )


# ==========================================================================
# 2.  TRIE
# ==========================================================================
class Node:
    """Trie node.  `kids` maps a letter to the next node; `word` marks a
    complete word.  __slots__ keeps 100k+ nodes cheap and attribute access
    fast -- this is the hot data structure of the search."""
    __slots__ = ("kids", "word")

    def __init__(self) -> None:
        self.kids: Dict[str, "Node"] = {}
        self.word = False


def build_trie(words: Iterable[str], reverse: bool = False) -> Node:
    """Build a trie.  `reverse=True` inserts every word backwards, which is
    what the mirrored (Condition B) search validates its columns against."""
    root = Node()
    for w in words:
        if reverse:
            w = w[::-1]
        node = root
        for ch in w:
            nxt = node.kids.get(ch)
            if nxt is None:
                nxt = Node()
                node.kids[ch] = nxt
            node = nxt
        node.word = True
    return root


def three_letter_tables(words3: Iterable[str]):
    """Flatten the 3-letter lexicon into three lookup tables used by the
    spine-column pruning:

        firsts          : letters that can start a 3-letter word
        seconds['A']    : letters b such that "Ab?" is a live prefix
        thirds['AB']    : letters c such that "ABc" is a word
    """
    firsts: Set[str] = set()
    seconds: Dict[str, Set[str]] = {}
    thirds: Dict[str, Set[str]] = {}
    for w in words3:
        firsts.add(w[0])
        seconds.setdefault(w[0], set()).add(w[1])
        thirds.setdefault(w[:2], set()).add(w[2])
    return frozenset(firsts), seconds, thirds


# ==========================================================================
# 3.  SEARCH ENGINE
# ==========================================================================
class Halt(Exception):
    """Raised to unwind the recursion when we hit the result limit or the
    time budget."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class WaffleEngine:
    """Cell-by-cell backtracking search for 5x5 double word squares whose
    spine columns carry a valid 3-letter word in their TOP three cells
    (Condition A *in this engine's own coordinates* -- the caller may be
    feeding it a vertically mirrored problem to get Condition B).

    Parameters
    ----------
    row_root   : trie the rows are validated against
    col_roots  : one trie per column (reversed words when `mirrored` is set).
                 They are usually the same object, but a pinned row lets the
                 caller hand each column a trie restricted to the words with
                 the right letter in that position, which prunes column
                 prefixes long before the pinned row is reached.
    words3     : 3-letter lexicon for the spine test (reversed words when
                 `mirrored` is set)
    mirrored   : if True, the grid being built is the top-to-bottom mirror
                 of the real grid; `_emit` un-mirrors before reporting
    forced     : {engine_row_index: word} rows pinned by the user
    allow_repeats : permit the same word to appear twice among the rows
    rng        : if given, letter choices are shuffled -> different squares
                 on each run instead of always the alphabetically-first ones
    deadline   : time.monotonic() value at which to abort
    """

    def __init__(self, row_root: Node, col_roots: Sequence[Node],
                 words3: Iterable[str], *,
                 mirrored: bool = False,
                 forced: Optional[Dict[int, str]] = None,
                 allow_repeats: bool = False,
                 rng: Optional[random.Random] = None,
                 deadline: Optional[float] = None) -> None:
        self.row_root = row_root
        self.col_roots = list(col_roots)
        self.firsts, self.seconds, self.thirds = three_letter_tables(words3)
        self.mirrored = mirrored
        self.forced = dict(forced or {})
        self.allow_repeats = allow_repeats
        self.rng = rng
        self.deadline = deadline

        # mutable search state
        self.grid: List[List[Optional[str]]] = [[None] * N for _ in range(N)]
        self.col_nodes: List[Node] = list(self.col_roots)  # per-column position
        self.row_set: Set[str] = set()                # rows placed so far
        self.nodes = 0                                # cells visited (stats)
        self.on_solution: Callable[[List[str], List[str]], None] = lambda r, c: None

    # ---- driver ---------------------------------------------------------
    def run(self, on_solution: Callable[[List[str], List[str]], None]) -> None:
        self.on_solution = on_solution
        self.col_nodes = list(self.col_roots)
        self.row_set.clear()
        self._fill(0, 0, self.row_root)

    # ---- the hot recursion ----------------------------------------------
    def _fill(self, r: int, c: int, row_node: Node) -> None:
        """Place a letter in cell (r, c).  `row_node` is the trie node for
        the current row's prefix; self.col_nodes[c] is the node for column
        c's prefix (rows 0..r-1)."""
        if c == N:                       # row finished
            self._row_complete(r)
            return

        self.nodes += 1
        # Check the clock rarely: time.monotonic() is cheap but not free and
        # this line runs millions of times.
        if self.deadline is not None and not (self.nodes & 0x3FFFF):
            if time.monotonic() > self.deadline:
                raise Halt("time limit")

        col_node = self.col_nodes[c]
        row_kids = row_node.kids
        col_kids = col_node.kids
        if not row_kids or not col_kids:
            return

        # --- core CSP step: letters allowed by BOTH the row and the column.
        # Iterate the smaller dict for the membership test.
        if len(row_kids) <= len(col_kids):
            cands = [ch for ch in row_kids if ch in col_kids]
        else:
            cands = [ch for ch in col_kids if ch in row_kids]
        if not cands:
            return

        # --- last cell of the row: the row word has to END here.
        if c == N - 1:
            cands = [ch for ch in cands if row_kids[ch].word]
            if not cands:
                return
        # --- last row: every column word has to END here, and (this is the
        #     "double" in double word square) a column may not repeat a word
        #     already used across.  Rows 1-4 are known by now, so most of the
        #     across/down clashes die here instead of at the finished grid.
        if r == N - 1:
            keep = []
            for ch in cands:
                if not col_kids[ch].word:
                    continue
                col_word = "".join(self.grid[i][c] for i in range(N - 1)) + ch
                if self.mirrored:
                    col_word = col_word[::-1]
                if col_word in self.row_set:
                    continue
                keep.append(ch)
            cands = keep
            if not cands:
                return

        # --- waffle constraint, applied on the two spine columns as the
        #     first three rows are laid down.
        if c in SPINE:
            if r == 0:
                allowed: Optional[FrozenSet[str]] = self.firsts
            elif r == 1:
                allowed = self.seconds.get(self.grid[0][c], EMPTY)
            elif r == 2:
                allowed = self.thirds.get(self.grid[0][c] + self.grid[1][c], EMPTY)
            else:
                allowed = None          # rows 4-5 are unconstrained here
            if allowed is not None:
                cands = [ch for ch in cands if ch in allowed]
                if not cands:
                    return

        # --- user-pinned row (--row 3=ROBOT).
        forced_word = self.forced.get(r)
        if forced_word is not None:
            want = forced_word[c]
            cands = [want] if want in cands else []
            if not cands:
                return

        if self.rng is not None and len(cands) > 1:
            self.rng.shuffle(cands)

        row = self.grid[r]
        for ch in cands:
            row[c] = ch
            self.col_nodes[c] = col_kids[ch]
            self._fill(r, c + 1, row_kids[ch])
        # Restore this column's trie position for the caller.  Deeper columns
        # restore themselves in their own frames.
        self.col_nodes[c] = col_node
        row[c] = None

    def _row_complete(self, r: int) -> None:
        """Row r is a valid word (the trie guaranteed that).  Recurse to the
        next row, or emit the finished grid."""
        word = "".join(self.grid[r])
        if not self.allow_repeats and word in self.row_set:
            return                       # duplicate row word
        if r == N - 1:
            self._emit()
            return
        self.row_set.add(word)
        try:
            self._fill(r + 1, 0, self.row_root)
        finally:
            self.row_set.discard(word)

    def _emit(self) -> None:
        """Hand the finished grid to the caller, un-mirroring it first if we
        were searching the mirrored problem."""
        rows = ["".join(row) for row in self.grid]
        cols = ["".join(self.grid[i][j] for i in range(N)) for j in range(N)]
        if self.mirrored:
            rows.reverse()                       # undo the top-to-bottom flip
            cols = [col[::-1] for col in cols]   # columns were read bottom-up
        # No word may be used both across and down -- that is the definition of
        # a *double* word square, and it is what rules out the symmetric
        # squares where column i simply repeats row i.  (Row 5 was not in
        # row_set during the pruning above, so the check is repeated here in
        # full.)  Duplicate columns are rejected unless --allow-repeats.
        col_set = set(cols)
        if col_set & set(rows):
            return
        if not self.allow_repeats and len(col_set) != N:
            return
        self.on_solution(rows, cols)


# ==========================================================================
# 4.  RESULTS + INDEPENDENT VERIFICATION
# ==========================================================================
@dataclass(frozen=True)
class Square:
    rows: Tuple[str, ...]
    cols: Tuple[str, ...]
    cond_a: bool          # top-down finish legal (Row 2 before Row 4)
    cond_b: bool          # bottom-up finish legal (Row 4 before Row 2)

    def stems(self, top: bool) -> Tuple[str, str]:
        """The two intermediate 3-letter words exposed by the finish."""
        sl = slice(0, 3) if top else slice(2, 5)
        return (self.cols[SPINE[0]][sl], self.cols[SPINE[1]][sl])


def verify(rows: Sequence[str], words5: FrozenSet[str], words3: FrozenSet[str],
           allow_repeats: bool = False) -> Tuple[List[str], Square]:
    """Re-derive everything from the row words alone and check every rule.

    This deliberately shares no code with the search: it is the safety net
    that catches any mistake in the trie logic or in the mirroring trick.
    Returns (list_of_problems, Square).  Empty list == valid.
    """
    problems: List[str] = []
    if len(rows) != N or any(len(w) != N for w in rows):
        return ["grid is not %dx%d" % (N, N)], Square(tuple(rows), (), False, False)

    cols = tuple("".join(rows[i][j] for i in range(N)) for j in range(N))
    rows = tuple(rows)

    for i, w in enumerate(rows, 1):
        if w not in words5:
            problems.append("row %d (%s) is not a 5-letter word" % (i, w))
    for j, w in enumerate(cols, 1):
        if w not in words5:
            problems.append("column %d (%s) is not a 5-letter word" % (j, w))

    overlap = set(rows) & set(cols)
    if overlap:
        problems.append("word(s) used both across and down: " + ", ".join(sorted(overlap)))
    if not allow_repeats:
        if len(set(rows)) != N:
            problems.append("repeated row word")
        if len(set(cols)) != N:
            problems.append("repeated column word")

    # The waffle test, straight from the definition.
    cond_a = all(cols[c][0:3] in words3 for c in SPINE)
    cond_b = all(cols[c][2:5] in words3 for c in SPINE)
    if not (cond_a or cond_b):
        problems.append("neither waffle finish is legal (no valid 3-letter stems)")

    return problems, Square(rows, cols, cond_a, cond_b)


# ==========================================================================
# 5.  TOP-LEVEL FINDER (runs the engine once per condition)
# ==========================================================================
@dataclass
class SearchStats:
    found: int = 0
    nodes: int = 0
    seconds: float = 0.0
    halted: str = ""          # "" | "limit" | "time limit"
    rejected: int = 0         # solutions that failed verify() -- must stay 0


class DoubleWordSquareFinder:
    def __init__(self, words5: Iterable[str], words3: Iterable[str], *,
                 allow_repeats: bool = False, seed: Optional[int] = None,
                 shuffle: bool = False) -> None:
        self.words5: FrozenSet[str] = frozenset(words5)
        self.words3: FrozenSet[str] = frozenset(words3)
        self.allow_repeats = allow_repeats
        self.rng = random.Random(seed) if (shuffle or seed is not None) else None

        # Two tries over the 5-letter lexicon: forwards for the normal
        # search, backwards for the mirrored (Condition B) search.
        # Sort before inserting: set iteration order is randomised per process,
        # and the trie's child order decides the order squares come out in.
        # Sorting makes a run without --shuffle reproducible.
        self._ordered5 = sorted(self.words5)
        # `_stored[mirrored]` is the list of strings the column trie actually
        # holds: plain words normally, reversed words in the mirrored pass.
        self._stored = {False: self._ordered5,
                        True: [w[::-1] for w in self._ordered5]}
        self.trie_fwd = build_trie(self._stored[False])
        self.trie_rev = build_trie(self._stored[True])
        self.words3_rev = frozenset(w[::-1] for w in self.words3)

    def _column_tries(self, mirrored: bool, forced: Dict[int, str]) -> List[Node]:
        """One trie per column.  With no pinned rows every column shares the
        general trie.  A row pinned at engine index r fixes one letter of every
        column word, so each column gets a trie of just the words that carry
        that letter in that position -- the pruning then starts at row 1 rather
        than waiting until row r is reached.  (This matters most in the
        mirrored pass, where a pin on real row 1 lands on the *last* row.)"""
        shared = self.trie_rev if mirrored else self.trie_fwd
        if not forced:
            return [shared] * N
        stored = self._stored[mirrored]
        roots: List[Node] = []
        for j in range(N):
            # (engine row, required letter of the stored column word)
            pins = [(r, w[j]) for r, w in forced.items()]
            roots.append(build_trie([w for w in stored
                                     if all(w[r] == ch for r, ch in pins)]))
        return roots

    def search(self, *, condition: str = "either", limit: int = 10,
               time_limit: Optional[float] = None,
               forced_rows: Optional[Dict[int, str]] = None,
               on_found: Optional[Callable[[Square, int], None]] = None,
               keep: bool = True) -> Tuple[List[Square], SearchStats]:
        """Find playable squares.

        condition : 'a' (top-down finish), 'b' (bottom-up), or 'either'
        limit     : stop after this many squares; 0 = unlimited
        on_found  : called with (square, index) as each square is found, so
                    results stream instead of arriving in one lump
        keep      : accumulate the squares in the returned list.  Pass False
                    when only counting -- an exhaustive run finds far too many
                    to hold in memory.
        """
        forced_rows = forced_rows or {}
        for idx, word in forced_rows.items():
            if word not in self.words5:
                raise SystemExit("--row %d=%s: not a 5-letter word in the lexicon"
                                 % (idx + 1, word))

        results: List[Square] = []
        stats = SearchStats()
        count = 0
        deadline = time.monotonic() + time_limit if time_limit else None
        started = time.monotonic()

        # For 'either' we run both engines.  Give the first pass only half the
        # quota so the output is a mix rather than 10 Condition-A grids;
        # whatever it does not use rolls over to the second pass.
        if condition == "either":
            passes = [("a", (limit + 1) // 2 if limit else 0), ("b", 0)]
        else:
            passes = [(condition, 0)]

        for cond, quota in passes:
            remaining = (limit - count) if limit else 0
            if limit and remaining <= 0:
                break
            # stop_at: the running total at which THIS pass gives up (0 = never)
            stop_at = count + (min(quota, remaining) if quota else remaining)
            # In an 'either' run the Condition-B pass re-finds every grid that
            # satisfies both conditions, and pass A has already reported those.
            # Skipping them is an exact de-duplication -- pass B then yields
            # "B and not A" -- and costs no memory.
            drop_a = (cond == "b" and condition == "either")

            def collect(rows: List[str], _cols: List[str], _stop_at=stop_at,
                        _drop_a=drop_a) -> None:
                nonlocal count
                problems, square = verify(rows, self.words5, self.words3,
                                          self.allow_repeats)
                if problems:
                    # Unreachable unless the fast path has a bug: the engine
                    # already enforces every rule verify() re-checks.  Shout,
                    # drop the grid, keep searching.
                    stats.rejected += 1
                    print("INTERNAL ERROR: rejected %s -- %s"
                          % (rows, "; ".join(problems)), file=sys.stderr)
                    return
                if _drop_a and square.cond_a:
                    return
                count += 1
                if keep:
                    results.append(square)
                if on_found:
                    on_found(square, count)
                if limit and count >= _stop_at:
                    raise Halt("limit")

            mirrored = (cond == "b")
            # A mirrored grid has real row i at engine row N-1-i.
            engine_forced = {(N - 1 - i if mirrored else i): w
                             for i, w in forced_rows.items()}
            engine = WaffleEngine(
                row_root=self.trie_fwd,
                col_roots=self._column_tries(mirrored, engine_forced),
                words3=self.words3_rev if mirrored else self.words3,
                mirrored=mirrored,
                forced=engine_forced,
                allow_repeats=self.allow_repeats,
                rng=self.rng,
                deadline=deadline,
            )
            try:
                engine.run(collect)
            except Halt as stop:
                stats.nodes += engine.nodes
                if stop.reason == "time limit":
                    stats.halted = stop.reason
                    break
                # This pass hit its share of the quota; the next one (if any)
                # still gets to run.
                continue
            stats.nodes += engine.nodes

        if limit and count >= limit:
            stats.halted = stats.halted or "limit"
        stats.found = count
        stats.seconds = time.monotonic() - started
        return results, stats


# ==========================================================================
# 6.  OUTPUT
# ==========================================================================
BUILD_ORDER = "Row 3 -> Col 1 -> Col 3 -> Col 5 -> Row 1 -> Row 5"


def format_square(sq: Square, index: int) -> str:
    """Pretty-print one grid, its words, and how to build it over the board."""
    out: List[str] = []
    if sq.cond_a and sq.cond_b:
        finish = "either finish works (Row 2 first or Row 4 first)"
    elif sq.cond_a:
        finish = "top-down finish only (Row 2, then Row 4)"
    else:
        finish = "bottom-up finish only (Row 4, then Row 2)"

    out.append("=" * 64)
    out.append("Grid #%d   --   %s" % (index, finish))
    out.append("=" * 64)
    out.append("       c1 c2 c3 c4 c5")
    for i, word in enumerate(sq.rows):
        out.append("   r%d   %s" % (i + 1, "  ".join(word)))
    out.append("")
    out.append("   Across : %s" % ", ".join(sq.rows))
    out.append("   Down   : %s" % ", ".join(sq.cols))
    out.append("")
    out.append("   Build  : %s" % BUILD_ORDER)
    if sq.cond_a:
        s2, s4 = sq.stems(top=True)
        out.append("            -> Row 2   (exposes %s in col 2 and %s in col 4)"
                   % (s2, s4))
        out.append("            -> Row 4   (completes the square)")
    if sq.cond_b:
        if sq.cond_a:
            out.append("            or")
        s2, s4 = sq.stems(top=False)
        out.append("            -> Row 4   (exposes %s in col 2 and %s in col 4)"
                   % (s2, s4))
        out.append("            -> Row 2   (completes the square)")
    out.append("")
    return "\n".join(out)


def print_squares(squares: Sequence[Square]) -> None:
    """Dump a list of grids to the console (kept separate from the search so
    it can be reused on stored results)."""
    for i, sq in enumerate(squares, 1):
        print(format_square(sq, i))


# ==========================================================================
# 7.  CLI
# ==========================================================================
def parse_row_spec(spec: str) -> Tuple[int, str]:
    """--row 3=ROBOT  ->  (2, 'ROBOT')  (0-based index)."""
    if "=" not in spec:
        raise SystemExit("--row expects N=WORD, e.g. --row 3=ROBOT (got %r)" % spec)
    num, word = spec.split("=", 1)
    try:
        idx = int(num)
    except ValueError:
        raise SystemExit("--row: %r is not a row number" % num)
    if not 1 <= idx <= N:
        raise SystemExit("--row: row number must be 1..%d" % N)
    word = word.strip().upper()
    if len(word) != N or not word.isalpha():
        raise SystemExit("--row: %r must be a %d-letter word" % (word, N))
    return idx - 1, word


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Find playable 5x5 double word squares for Scrabble.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Dictionary: pass --dict /path/to/twl06.txt (one word per line,\n"
               "case-insensitive).  See the top of this file for details and\n"
               "for where to download TWL / SOWPODS / ENABLE word lists.",
    )
    ap.add_argument("-d", "--dict", action="append", default=[], metavar="FILE",
                    help="Scrabble word list; repeatable.")
    ap.add_argument("--dict3", metavar="FILE",
                    help="separate word list for the intermediate 3-letter words "
                         "(default: same as --dict).")
    ap.add_argument("--common", metavar="FILE",
                    help="familiarity list: every word in the square, and both "
                         "3-letter intermediates, must appear here as well as in "
                         "the Scrabble lexicon.  Trades yield for squares you "
                         "could defend at the kitchen table.")
    ap.add_argument("--common-top", type=int, default=None, metavar="N",
                    help="use only the first N entries of --common (frequency "
                         "lists are ordered commonest-first).")
    ap.add_argument("-n", "--limit", type=int, default=None, metavar="N",
                    help="stop after N squares (0 = no limit; default 10, or "
                         "no limit with --count-only).")
    ap.add_argument("--condition", choices=("a", "b", "either"), default="either",
                    help="a = top-down finish, b = bottom-up finish, "
                         "either = both (default).")
    ap.add_argument("--row", action="append", default=[], metavar="N=WORD",
                    help="pin a row, e.g. --row 3=ROBOT; repeatable.")
    ap.add_argument("--time-limit", type=float, default=None, metavar="SEC",
                    help="give up after SEC seconds.")
    ap.add_argument("--shuffle", action="store_true",
                    help="randomise letter order so each run finds different "
                         "squares instead of the alphabetically first ones.")
    ap.add_argument("--seed", type=int, default=None,
                    help="RNG seed (implies --shuffle; makes runs reproducible).")
    ap.add_argument("--allow-repeats", action="store_true",
                    help="allow a word to appear twice among the rows or twice "
                         "among the columns (across/down overlap is always "
                         "forbidden -- that is what 'double' means).")
    ap.add_argument("--count-only", action="store_true",
                    help="count squares without printing them.")
    args = ap.parse_args(argv)

    # ---- lexicon ----
    paths, system_fallback = resolve_dictionaries(args.dict)
    buckets = load_words(paths, (3, 5), drop_capitalised=system_fallback)
    words5, words3 = buckets[5], buckets[3]
    if args.dict3:
        words3 = load_words([args.dict3], (3,))[3]
    if not words5 or not words3:
        raise SystemExit("lexicon is missing 5-letter or 3-letter words "
                         "(%d five-letter, %d three-letter found)"
                         % (len(words5), len(words3)))
    print("Lexicon: %s  ->  %d five-letter words, %d three-letter words"
          % (", ".join(paths), len(words5), len(words3)), file=sys.stderr)

    if args.common:
        if not os.path.exists(args.common):
            raise SystemExit("--common: file not found: " + args.common)
        familiar = load_common(args.common, args.common_top)
        words5 = {w for w in words5 if w in familiar}
        words3 = {w for w in words3 if w in familiar}
        print("Common-word filter (%s%s): %d five-letter words, "
              "%d three-letter words remain"
              % (args.common,
                 ", top %d" % args.common_top if args.common_top else "",
                 len(words5), len(words3)), file=sys.stderr)
        if not words5 or not words3:
            raise SystemExit("nothing left after the common-word filter -- "
                             "raise --common-top or use a longer list.")
        if len(words5) < 1500:
            print("NOTE: below roughly 1500 five-letter words the squares run "
                  "out entirely.\n      If this finds nothing, that is the "
                  "lexicon, not the search.", file=sys.stderr)

    forced = dict(parse_row_spec(s) for s in args.row)
    # --count-only means "how many are there", so it counts them all unless the
    # user asked for a cap.
    limit = args.limit if args.limit is not None else (0 if args.count_only else 10)

    finder = DoubleWordSquareFinder(words5, words3,
                                    allow_repeats=args.allow_repeats,
                                    seed=args.seed, shuffle=args.shuffle)

    # Stream results as they are found rather than waiting for the whole run.
    stream = None if args.count_only else (lambda sq, i: print(format_square(sq, i)))
    squares, stats = finder.search(condition=args.condition,
                                   limit=max(0, limit),
                                   time_limit=args.time_limit,
                                   forced_rows=forced,
                                   on_found=stream,
                                   keep=not args.count_only)

    if args.count_only:
        print("%d square(s)" % stats.found)
    if not stats.found:
        print("No playable square found%s."
              % (" within the limits given" if stats.halted else ""), file=sys.stderr)
    print("%d square(s), %.2fs, %d cells explored%s%s"
          % (stats.found, stats.seconds, stats.nodes,
             ", stopped: " + stats.halted if stats.halted else "",
             ", %d REJECTED BY VERIFIER" % stats.rejected if stats.rejected else ""),
          file=sys.stderr)
    return 0 if stats.found else 1


if __name__ == "__main__":
    sys.exit(main())
