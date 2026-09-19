# Freeze design — N=8192 persistence probe (SCOPING ONLY, no freeze executed)

- Status: `SCOPING_ONLY_NO_EXECUTION_AUTHORIZED`. Supporting design note
  for `spec.md` in this directory. It designs the future freeze; it does
  NOT execute it. No derivation, execution, data contact, commit, or push
  is authorized by this file.
- Parent analysis:
  `.workbuddy/queue/NBPOLAR-REDUCED-N-FEASIBILITY.md` (§2 rows C1–C10;
  §3 comparability; §4 gate class). Read that file for the full
  evidence-backed cost inventory before freezing anything.

## 1. What must be rebuilt at N=8192 (new derivation)

| # | item | N=8192 consequence |
|---|---|---|
| R1 | `construction_and_allocation.json` rebuild | Full re-derivation per P16 pattern (`TASK_PACKET.md` P16-02): new counts-train sampling at N=8192, new pooled `(e,h,index)` worst-first orders, new (K1,K2) exhaustive selection by TRAIN residual (NOT carried from 334/6746) |
| R2 | Runner frozen point | New module (or thin-importer + new frozen constants) with `FROZEN_N = 8192` + focused injected tests; `target_construction.py:1559` hard-gates `n == FROZEN_N`, so no frozen-point runner accepts `--n 8192` |
| R3 | K allocation | `floor((1.3·N·H−64)/5)` derived in-packet from recomputed 2M H within 1e-12 — estimate ≈1760 only, never hand-filled (AGENTS.md §5.5) |
| R4 | L1/L2 orders | Fresh length-8192 worst-first empirical permutations (new counts opens + sampling budget under frozen derivation seeds); the 32768-length files are length- and geometry-incompatible |
| R5 | Spike order | F-median8 formula-id carried, but R=8 window convention vs 8192-geometry re-frozen as a NEW freeze decision; new length-8192 spike permutation + digest |
| R6 | Tag value + domain | Value `10·N+63` = **81983** bits/tag (frozen arithmetic in packet); NEW tag domain (fresh master + prefix, grep disjointness proof) |
| R7 | SC sizing | Stage count log2(8192) = **13**; `chunk_rows` geometry re-sizing (P11 precedent); code paths reused, all sizing constants new |
| R8 | IR lengths | IR-5 series 8192 f32-LE (32 KiB) + 8192 u8 + 8192 u8 = 48 KiB/record (≈144 KiB for 3 records, `ir5full-v1` manifest linkage unchanged); IR-1/IR-2/IR-3/IR-4 shapes and formulas unchanged |
| R9 | Disclosure values | `5·(K1+K2)+64` per operational block (≈8864 at the ≈1760 estimate), `5·K2+64` oracle, planned key/public totals, recount gates — all re-derived from the in-packet K |
| R10 | Population gates | Gate pattern reused; frame sets new: DEV 3595..3626, remainder 3627..3644, 1.5M stubs excluded, S2-ii build-frames (2M TRAIN 0..2186) disjointness declared |
| R11 | Reviews + authorizations | Fresh freeze review, independent Pre-EXECUTE, Pre-RESULT, main-thread acceptance (all future, all separately authorized) |

Effort class: P16-scale (new spec delta + new/tested runner +
full-suite green + two independent reviews + one Tier-Y execution with
fresh TRAIN sampling) — explicitly NOT P20S-scale thin reuse. At N=8192
nothing is thin-reusable except session-H inputs, formula shapes, and
code paths.

## 2. What is reusable read-only

- Session-H inputs: 2M H literals (recomputed within 1e-12) + worktree
  `raw_prior_2m.npz` arrays as off-protected-data derivation inputs
  (never the V25 counts NPZ; counts-calibration opens 0/0).
- Formula shapes: budget, tag-length, K-split selection, F-median8
  ranking, IR-1..IR-4, nine-scalar semantics, D1/D2 feasibility shape.
- Code paths: `sc.py`, `sc_chunked_gate.py`, `transform.py`, causal
  two-layer wiring, Toeplitz accounting, P20A resource/endpoint paths.
- Machinery: recount/gate machinery, S2-ii disjointness declaration,
  truth-isolation boundary, `undetected`/oracle isolation, checkpoint
  + refusal-ordering patterns, 2 GiB / single-thread envelope shape.

## 3. N-dependent value table (shapes frozen, literals in-packet)

| quantity | N=32768 pin (NOT transferred) | N=8192 shape |
|---|---|---|
| tag bits | 327743 | **81983** (= 10·8192+63) |
| SC stages | 15 | **13** |
| K_total | 7080 (334/6746) | ≈1760 estimate; (K1,K2) derived in-packet |
| key/block (operational) | 35464 | ≈8864 at estimate |
| IR-5 /record | 192 KiB (32768 f32 + 2×32768 u8) | 48 KiB (8192 f32 + 2×8192 u8) |
| DEV block | 128 frames | 32 frames (3595..3626) |
| remainder | 50-frame tail | 18 frames (3627..3644, 4608 pairs) |

## 4. Comparability boundary (load-bearing — repeated from spec ADDED-7)

Per-N results are NOT comparable across N: do not transfer the
1/4→2/5→4/5 chain, the H2 verdicts, the IR-5 32768 geometry, or any
leakage literal. Pooling across N is forbidden by the same logic that
forbids truncated/full-block and cross-session pooling. The probe's only
valid comparisons are WITHIN N=8192 (A vs B paired on the same block;
tail-mass contrasts under each record's own order).

## 5. Future gate sequence (ALL future — none authorized by this scoping)

1. OpenSpec delta freeze review (main thread) of spec + design + tasks.
2. Stage-A implementation authorization (explicit pasted text; new
   runner/tests/derivation-program pin).
3. Independent reviewer-go Pre-EXECUTE PASS (AGENTS.md §10.3).
4. Stage-B single-execution authorization (explicit pasted text,
   separate from 2).
5. Independent reviewer-go Pre-RESULT review on actual artifacts.
6. Main-thread acceptance before any analysis use.
   FAIL at any gate blocks execution/solidification.

(End of file)
