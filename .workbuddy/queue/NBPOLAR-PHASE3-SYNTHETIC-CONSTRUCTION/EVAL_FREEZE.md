# EVAL_FREEZE — NBPOLAR-PHASE3-SYNTHETIC-CONSTRUCTION

Frozen after TRAIN/DEV, before any EVAL read. EVAL has not yet run.

## 1. Selected candidate (deterministic per packet §6)

- channel: q=32 erasure side information
- q=32, N=256, epsilon=0.05, K_margin=32, K=ceil(12.8)+32=45
- TRAIN samples: 512 blocks, TRAIN_SEED=2026091201 (sequential stream,
  eps=0.05 built first; 512/512 used, 0 impossible)
- disclosure order (first 45 of 256, worst first, U coordinates):
  [0, 2, 1, 4, 8, 3, 16, 5, 32, 6, 9, 10, 64, 17, 12, 18, 128, 33, 7, 20,
   34, 24, 65, 36, 11, 66, 40, 13, 48, 14, 19, 129, 130, 72, 68, 22, 80,
   132, 21, 136, 35, 26, 96, 25, 67]
- full 256-permutation held in the TRAIN construction result;
  above are entries 0..44. Order rule: descending (e,h), ties by index.

## 2. DEV table (DEV_SEED=2026091202 sequential, 100 blocks/candidate)

| eps | margin | K | exact/100 | init_err/100 | imposs | other | nan | fails[:5] |
|-----|--------|---|-----------|--------------|--------|-------|-----|-----------|
| 0.05 | 16 | 29 | 84 | 100 | 6 | 0 | 0 | 21,23,25,28,31 |
| 0.05 | 24 | 37 | 97 | 100 | 1 | 0 | 0 | 48,50,97 |
| 0.05 | 32 | 45 | 99 | 100 | 0 | 0 | 0 | 76 |
| 0.10 | 16 | 42 | 71 | 100 | 22 | 0 | 0 | 1,4,6,7,9 |
| 0.10 | 24 | 50 | 86 | 100 | 12 | 0 | 0 | 0,5,6,12,20 |
| 0.10 | 32 | 58 | 96 | 100 | 3 | 0 | 0 | 0,80,81,86 |
| 0.15 | 16 | 55 | 47 | 100 | 43 | 0 | 0 | 1,2,6,9,10 |
| 0.15 | 24 | 63 | 68 | 100 | 29 | 0 | 0 | 0,3,10,12,13 |
| 0.15 | 32 | 71 | 90 | 100 | 10 | 0 | 0 | 2,13,17,22,51 |
| 0.20 | 16 | 68 | 44 | 100 | 46 | 0 | 0 | 0,1,2,3,4 |
| 0.20 | 24 | 76 | 72 | 100 | 27 | 0 | 0 | 0,3,7,21,23 |
| 0.20 | 32 | 84 | 83 | 100 | 15 | 0 | 0 | 4,5,22,34,36 |

Selection proof: retained = exact>=98/100 → only (0.05,45,99).
Smallest K among retained =45 (sole). No tie-break needed. If none
had passed, terminal would be BLOCKED(NO_EASY_SYNTHETIC_POINT) with
this table; tuning outside the grid is forbidden and was not done.
QSC was not searched as a replacement (packet §6).

## 3. Polarization evidence for eps=0.10 (unit + official TRAIN)

- analytic mean 0.10 within 1e-12; extreme (<=0.01 or >=0.99) 0.816>=0.20
- official TRAIN eps=0.10: full average-tie Spearman 0.7665
  (diagnostic, 187-way zero tie); resolvable (e>0, n=66) Spearman
  0.9959>=0.90; top-50 overlap 0.98>=0.80; Pearson raw 0.9998

## 4. EVAL identity (one-shot, not yet executed)

- EVAL_SEED=2026091203, exactly 300 erasure blocks, eps=0.05, K=45,
  disclosure list above, field GF32 poly37 alpha=2 natural order
- pass criteria (P3-T1-08 + P3-T1-07): 300 attempted; exact (U and X)
  >=285/300; initial-error blocks >=240/300; zero NaN/invalid-metric/
  impossible-disclosure/resource-abort; failures listed by index, no
  rerun/replacement. Development gate only, not FER qualification.
- exact command (from repo root):
  PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
  /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python
  <eval_script>  # single call evaluating the frozen candidate above
  Time/resource stop: 300 decodes (~5 s expected, stop at 600 s or on
  first NaN/resource abort); peak <2 GiB (observed N=256 block ~tens
  of KiB). Total task <30 min (TRAIN 35 s + DEV 19 s + tests 37 s so
  far).

## 5. Stream separation and scope

TRAIN/DEV/EVAL use distinct RNG instances seeded 2026091201/02/03;
unit tests use 2026091200 only. No EVAL sample entered construction
or selection. Production scope is synthetic.py/construction.py plus
`__init__` surface and the Phase 2 `__all__` subset-fix; no Model-F,
real data, adapters, SCL, rate adaptation, benchmark roots, commits,
or Phase 4. Frozen dirs clean (see OPERATOR_RETURN audit).

Statement: EVAL has not yet run as of this freeze.

## 6. Cure addendum B2 (doc-only, 2026-09-11, no rerun)

Replaces the `<eval_script>` placeholder in §4 with the exact frozen
call. The single one-shot EVAL was one direct call (no dedicated eval
script file exists under `scripts/`/`tools/`; there is no script path
to record — the call point is the function below, invoked inline with
the repo root on `PYTHONPATH` in the packet §10 Miniforge python
environment):

```text
from numpy.random import default_rng
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    EVAL_SEED, evaluate_blocks, make_gf32)
rng = default_rng(EVAL_SEED)  # 2026091203, fresh sequential instance
out = evaluate_blocks(rng, field=make_gf32(), alpha=2, q=32, n=256,
                      channel="erasure", param=0.05,
                      disclosure_order=<frozen full 256-permutation
                        whose entries 0..44 are listed in §1>,
                      k=45, n_blocks=300)
```

Field identity: `make_gf32()` = `make_gf2m(5, 37)` (GF32, polynomial
basis, pinned poly 37; `algebra.py`), `alpha=2`, natural U order —
same field/alpha/order as TRAIN/DEV (§5, OPERATOR_RETURN §11).
TRAIN consumed only 2026091201 (`build_construction`, 512/epsilon
sequential); DEV consumed only 2026091202 (100 blocks/candidate
sequential); the EVAL stream 2026091203 was consumed exactly once by
the call above (300 blocks sequential). Unit-seed diagnostic checks
(`genie 298/1`, analytic `297/2` per 300) used the 2026091200 stream
only and never touched 2026091203. No other EVAL-stream call exists.
This addendum is reconstructed from frozen code and packet records;
no TRAIN/DEV/EVAL was rerun for it.
