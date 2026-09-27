# op-k1ramp-k550-base freeze review — 2026-09-27 (independent, read-only)

Reviewer: independent read-only subagent (no files modified).
Scope: `prereg.md`, `run.py` (new vs the C1 predecessor), `openspec/changes/nbpolar-op-k1-ramp-k550/{proposal,design,tasks}.md`,
`docs/nbpolar/OVERNIGHT_PLAN_20260927.md` §1–§2. The probe was **not** re-run by the reviewer.

## Verdict: MAY_PROCEED (7/7 items PASS, zero blocking)

| # | Item | Verdict |
|---|---|---|
| 1 | Target-output absence (`results.json` absent before launch) | PASS |
| 2 | Preregistered C command identical across prereg / design / run.py | PASS |
| 3 | Derivation discipline vs C1 predecessor | PASS |
| 4 | Arithmetic (disclosed, f, cells, blocks) | PASS |
| 5 | Stop rules complete (undetected isolation, budget, one-shot) | PASS |
| 6 | Write scope confined to the probe root | PASS |
| 7 | Non-claim wording compliance | PASS |

## Evidence summary

1. Before launch the probe root contained only `prereg.md`, `run.py`, and an scoped
   `.numba_cache/`; `results.json` was absent (one-shot idempotence).
2. `OUT` (`run.py:9`), `NUMBA_CACHE_DIR` (`run.py:47`), `PYTHONPATH` (`run.py:49`), and the
   interpreter (`run.py:46`) match the preregistered C command character-for-character
   (including the single-thread environment variables).
3. Relative to `l2-singlefactor-c1-k550/run.py`: channel `f4_pmf`/`P_F4`, dimensions
   (`Q/R/N/NLOG/ALPHA`), prior construction (`PRIOR_ONLY` for H1, `ORACLE_CONDITIONED` for H2),
   `toeplitz_master=tl.FROZEN_TOEPLITZ_MASTER`, the `tl.run_two_layer_block` positional and
   keyword arguments, `sc_decode` usage, `worst_k`/`best_k`, and the paired sampling rule
   (`default_rng([seed, block])`, x then delta) are unchanged. The only changes are the
   declared ones: `K1_FROZEN -> K1_GRID`, per-point `d1=worst_k(H1,k1)`, single arm
   `ARMS=("BASE",)`, seeds, output/cache paths, `WALL_LIMIT_S=600`, and identifiers.
   Removal of the CAND arm and the d2-overlap gate follows from the single-arm design.
4. `disclosed = 5*(k1+550)` gives 2800/3150/3550/4350/5000 for k1 = 10/80/160/320/450,
   matching `K1_POINTS` and the plan table; expected cells = 1 x 2 x 5 = 10; blocks = 5 x 2 x 16 = 160.
   The k1=160 point's 3550 bits cross-checks the `k2-dose-ramp` 3550-bit point.
5. `undetected` triggers immediate stop and is counted in isolation (never merged into
   success/FER); budget is checked every block and every 32 design samples with an
   immediate `incomplete` stop and no tuning; any exception writes one
   `execution_error` record with traceback and never retries; `reruns=0`.
6. The only writes are `workspace/probes/op-k1ramp-k550-base/results.json` and a Numba cache
   inside the same probe root. `qkd_recon.polar_core` is imported read-only from
   `/mnt/d/Code/qkd-reconciliation-lab/src` and receives no writes.
7. Every occurrence of efficiency/operating-point language is inside an explicit negation;
   each k1 point is labelled a bookkeeping-only dose diagnostic in `run.py`, `prereg.md`,
   and `design.md`.

## Non-blocking notes carried into the execution record

- **N1 (HN rounding)**: the plan table wrote `HN ≈ 954.18`; the in-run value is
  `954.1939276637445`. The difference is < 0.002% and only affects the bookkeeping
  reference column; in-run arithmetic uses `f_actual = 5*(k1+k2)/HN`, so no count changes.
- **N2 (Toeplitz stream per k1 point)**: `bidx` includes the k1 index, so each point draws
  its own Toeplitz stream. The pairing claim (same `(x,y)` per `(seed, block)`) is
  unaffected; this is recorded so future cross-probe comparisons do not over-read it.

Neither note changes arith. Both are carried into `EXECUTION_TRANSCRIPT.md`.
