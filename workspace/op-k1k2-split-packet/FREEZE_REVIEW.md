# op-k1k2-split-560 freeze review — 2026-09-27 (independent, read-only)

Reviewer: independent read-only subagent (no files modified). Reviewed against the parent
`workspace/probes/op-k1ramp-k550-base/run.py` and the preregistration.

## Verdict: MAY_PROCEED (after one RETURN_TO_AUTHORING round)

A first derivative was returned for authoring on three findings; all three were fixed and
re-reviewed. A static AST check of the final file confirms **zero** `%`-format placeholders
vs argument mismatches (6 formatting sites, all consistent).

| # | Item | Verdict |
|---|---|---|
| 1 | Target-output absence (`results.json` absent) | PASS (confirmed twice) |
| 2 | Diff vs parent within the six declared change classes | PASS |
| 3 | Frozen invariants (seeds, design seed/MC, toeplitz, channel, prior, call args, stop rules, one-shot) | PASS |
| 4 | Arithmetic (`k1+k2=560`, disclosed 2800 at every point, cells 16, blocks 256) | PASS |
| 5 | Prereg C/P vs run.py consistency | PASS |
| 6 | Non-claim wording compliance | PASS |

## Declared change classes relative to the parent

1. output / Numba cache paths; 2. probe identifiers; 3. `TOTAL_K=560` + `K1_GRID=(10,40,80,160,240,320,400,480)`
   + `K1_POINTS` (8 entries, each `disclosed=2800`, `f_book=2.9344139789`);
4. `k2 = TOTAL_K - k1` (total disclosure held constant);
5. `d2 = worst_k(H2, c["k2"])` **per point** (parent used a shared `worst_k(H2,550)`) — required
   because `k2` now varies; declared as DP-S3 in `STATUS.yaml`; `d2_len` follows the per-point value;
6. derived descriptive numbers (8 splits / 256 blocks) and the string/comment sync needed to keep
   `frozen_params` self-consistent.

## Blocking findings from the first round, and their resolution

- **F1 (fatal)**: `single_factor` string had no `%s` placeholder but received two arguments →
  would raise `TypeError` during `results` construction and write `execution_error`, voiding the
  measurement. Fixed by restoring one `%s` and one argument; re-verified by AST check (line 387).
- **F2 (contradictory self-description)**: `a3_split_rule` still claimed `k2=550 fixed` and a shared
  `d2`, contradicting the per-point behaviour. Fixed (line 397) to state `k2=560-k1`, constant 2800 bits,
  and per-point `d1`/`d2`.
- **F3 (description range)**: deviations row read "disclosed 2800..5000 bits". Fixed to
  "disclosed 2800 bits at every split".

## Non-blocking carry-overs

- Header comment (lines 22–23) still names the parent runner; cosmetic.
- `frozen_params.k2_single = 550` remains as an inherited literal; it no longer carries run semantics
  under the split grid (the per-point `k2` is `560 - k1`). Recorded so no future reading treats it as
  the operating k2.
- `d2_base = None` is a dead assignment kept for structural parity with the parent.

## Why this probe is in scope

It tests **allocation at fixed total disclosure**, not dose magnitude: every point spends the same
2800 bits (`f_book` identical), so any change in the operational counts is attributable to the
k1/k2 split rather than to a larger budget. It remains a bookkeeping-only dose-allocation diagnostic
and may never be described as an efficiency or operating point.
