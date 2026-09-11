# EVAL_FREEZE_R1 — NBPOLAR-PHASE3-R1-CONSTRUCTION-RECOVERY

Frozen after TRAIN/DEV, before any fresh EVAL read. The R1 EVAL has not
run; seed 2026091213 is unconsumed and `eval_r1_fresh/` does not exist.

## 1. Selected candidate (PLAN_R1 §6 applied to the DEV table in §2)

- option O3 analytic (exact BEC erasure order, zero TRAIN sampling)
- channel q=32 erasure side information, q=32, N=256, epsilon=0.05
- K=45 (first 45 of the full 256-permutation below, worst first):
  [0, 1, 2, 4, 8, 3, 16, 5, 32, 6, 9, 10, 64, 17, 12, 128, 18, 33, 7,
  20, 34, 24, 11, 65, 36, 66, 40, 13, 129, 68, 19, 14, 48, 130, 72,
  21, 132, 80, 22, 35, 136, 96, 25, 144, 26]
- field GF32 poly37, alpha=2, natural U order (eval_r1 pins)
- TRAIN: none consumed by O3 (analytic_construction n_used=0,
  train_seed=-1); paired genie calibration is the O2 eps=0.05/0.10
  TRAIN below (R1_TRAIN_SEED=2026091211 sequential)
- DEV: R1_DEV_SEED=2026091212 sequential, 100 blocks/candidate

Selection proof: retained = DEV exact ≥ 98/100 → O1 {(0.05,53,100),
(0.05,61,100), (0.05,69,99)}, O2 {(0.05,45,99), (0.05,53,100),
(0.05,61,99), (0.05,69,99)}, O3 {(0.05,45,100), (0.05,53,99),
(0.05,61,100), (0.05,69,100)}. Smallest retained K is 45 (O2, O3;
O1 K=45 scores 97 and is out). Same eps 0.05; higher DEV exact wins:
O3 100/100 imposs 0 over O2 99/100 imposs 1. No out-of-grid tuning;
predecessor seed 2026091203 and its output never entered.

## 2. Full DEV table (100 blocks/candidate, denominator = all attempts)

| opt | eps | K | exact | init | imposs | other | nan | fails[:5] |
|-----|------|---|-------|------|--------|-------|-----|-----------|
| O1 | 0.05 | 45 | 97 | 100 | 1 | 0 | 0 | 2,65,84 |
| O1 | 0.05 | 53 | 100 | 100 | 0 | 0 | 0 | - |
| O1 | 0.05 | 61 | 100 | 100 | 0 | 0 | 0 | - |
| O1 | 0.05 | 69 | 99 | 100 | 1 | 0 | 0 | 60 |
| O1 | 0.10 | 58 | 95 | 100 | 5 | 0 | 0 | 4,44,64,78,84 |
| O2 | 0.05 | 45 | 99 | 100 | 1 | 0 | 0 | 24 |
| O2 | 0.05 | 53 | 100 | 100 | 0 | 0 | 0 | - |
| O2 | 0.05 | 61 | 99 | 100 | 1 | 0 | 0 | 50 |
| O2 | 0.05 | 69 | 99 | 100 | 0 | 0 | 0 | 55 |
| O2 | 0.10 | 58 | 96 | 100 | 4 | 0 | 0 | 58,73,75,84 |
| O3 | 0.05 | 45 | 100 | 100 | 0 | 0 | 0 | - |
| O3 | 0.05 | 53 | 99 | 100 | 1 | 0 | 0 | 17 |
| O3 | 0.05 | 61 | 100 | 100 | 0 | 0 | 0 | - |
| O3 | 0.05 | 69 | 100 | 100 | 0 | 0 | 0 | - |
| O3 | 0.10 | 58 | 94 | 100 | 6 | 0 | 0 | 30,36,55,66,91 |

Harder sanity (0.10,58) retains nothing (94–96 < 98): the gate still
discriminates. Impossible events sit inside the denominator everywhere
(R1-D2 prereg); no zero-tolerance substitution was made.

## 3. Construction evidence (q=32 N=256 eps=0.10 TRAIN, R1 stream)

- O1/512: full-vector 0.7802 (187-way zero tie, reported only),
  resolvable 0.9954/n=69 ≥ 0.90, top-50 overlap 1.000 ≥ 0.80 → GATE PASS
- O2/2048: full-vector 0.8079 (179-way zero tie, reported only),
  resolvable 0.9966/n=77 ≥ 0.90, top-50 overlap 1.000 ≥ 0.80 → GATE PASS
- O3: exact by construction (order IS the BEC oracle); calibration =
  O2 row above (genie agrees with analytic where samples resolve)
- analytic checks: mean preserved within 1e-12, endpoints exact,
  extreme fraction 0.816 ≥ 0.20 (predecessor unit evidence, code unchanged)
- TRAIN wall 80.7 s (5120 blocks, 0 impossible in TRAIN), DEV wall
  23.7 s; tests 55/55 green (17+16+12+10, plain-python runners)

Why O3 measures construction quality best here: the disclosure head it
uses is the exact worst-first ranking of the tested channel family, and
the paired genie calibration shows sampled estimates converge to it
(resolvable ≈ 0.997, overlap 1.000) rather than somewhere else; DEV then
confirms disclosure performance separately (100/100 at the smallest K).

## 4. EVAL identity and exact command (one-shot, not yet executed)

- R1_EVAL_SEED=2026091213, exactly 300 erasure blocks, eps=0.05, K=45,
  first-45 list in §1, field/alpha/order as §1
- prereg criteria (PLAN_R1 §7): 300 attempted; exact (U and X) ≥ 285/300
  with impossible/other/nan inside the denominator; impossible reported
  as its own decode-failure class with indices (no zero-tolerance gate);
  initial-error blocks ≥ 240/300; NaN 0 and other-failure 0 hard;
  failures listed, no rerun/replacement. Development gate only.
- exact command (from repo root; no placeholder — full 256-permutation
  literal, 913 chars):

```text
PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.eval_r1 --q 32 --n 256 --channel erasure --param 0.05 --k 45 --seed 2026091213 --order 0,1,2,4,8,3,16,5,32,6,9,10,64,17,12,128,18,33,7,20,34,24,11,65,36,66,40,13,129,68,19,14,48,130,72,21,132,80,22,35,136,96,25,144,26,37,160,28,38,67,192,41,42,69,15,49,44,70,50,131,73,52,74,56,133,81,76,134,23,82,137,97,84,138,98,88,145,140,100,27,146,104,161,148,112,29,39,162,152,30,193,164,194,168,196,176,43,200,208,45,224,46,71,51,53,54,75,57,58,77,60,78,135,83,85,86,139,99,89,90,141,101,92,142,102,147,105,106,149,113,108,150,114,163,153,116,154,31,120,165,156,166,195,169,170,197,177,172,198,178,201,180,202,184,209,204,210,225,212,226,216,47,228,232,240,55,59,61,79,62,87,91,93,143,94,103,107,109,151,110,115,117,155,118,121,157,122,158,124,167,171,173,174,199,179,181,182,203,185,186,205,188,206,211,213,214,227,217,218,229,220,230,233,234,241,236,242,244,248,63,95,111,119,123,159,125,126,175,183,187,189,190,207,215,219,221,222,231,235,237,238,243,245,246,249,250,252,127,191,223,239,247,251,253,254,255 --n-blocks 300 --out .workbuddy/queue/NBPOLAR-PHASE3-R1-CONSTRUCTION-RECOVERY/eval_r1_fresh
```

- entry guards (tested): banned predecessor seeds refused; existing
  `--out` refused; order must be a full permutation; module form
  `python -m ...eval_r1` runs `main` via the package path above
  (resolves to `eval_r1.py` in `formal_ir/nbpolar/`)
- stop rules: ~5 s expected, stop at 600 s or first NaN/resource abort;
  peak < 2 GiB. Total R1 task so far ≈ 5 min.

## 5. Stream separation and scope

R1 unit 2026091210 / TRAIN 2026091211 / DEV 2026091212 / EVAL 2026091213:
all mutually distinct and all differ from predecessor 2026091200–1203
(test-pinned). No EVAL sample entered construction or selection. Scope:
`construction.py` (+3 helpers), `__init__.py` (+exports), new
`eval_r1.py`, new `test_nbpolar_r1.py`; predecessor tests untouched;
no Phase 2 production change (oracle suite green); no Model-F, real
data, adapters, SCL, rate work, production roots, commit/push/Phase 4.

Statement: the R1 EVAL has not run as of this freeze; target
`eval_r1_fresh/` is absent (verified OUT_ABSENT before writing this
file). One fresh EVAL is authorized only after a real independent
reviewer-go PASS on this contract. Self-authorization is refused.
