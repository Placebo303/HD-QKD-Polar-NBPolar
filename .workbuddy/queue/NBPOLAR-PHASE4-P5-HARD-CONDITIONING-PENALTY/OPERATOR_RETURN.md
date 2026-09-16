# Operator return — NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY

Rev 1 (2026-09-13). Phase 4-P5 hard-L1 conditioning penalty gate. Candidate only:
no acceptance is claimed here; acceptance is owned by the main thread. No commit,
no push, no code or immutable-gate-artifact change.

## 1. Mission

Test, at one frozen dependent-L2 operating point, whether a correct-L1 oracle arm
and a hard-candidate operational arm over the same blocks and disclosures show a
material operational penalty (oracle-only events), while operational-only events
stay structurally zero. Synthetic injected tables only; not real-data FER,
efficiency, loss, key rate, qualification or promotion evidence.

## 2. Frozen point, model, sets, seeds, masters, command, root

- Point: GF32 polynomial basis (poly 37, alpha 2, natural order), `q=32`,
  `N=256`, `epsilon1=0.05`; strong dependent-L2 profile
  `epsilon2(u1) = 0.02 + 0.36*u1/31` (mean exactly 0.20); `K1=45`, `K2=140`.
- Model: dependent injected `[Alice,Bob]` table
  `P(B|A) = Ph(B_high|high) * Pl(B_low|low, high)` with the q=32 marked-erasure
  kernels; `[Alice,Bob]` column-normalized with max deviation
  `3.774758283725532e-15 <= 1e-12` (asserted, never renormalized).
- Pre-decoder guard: `p2_maxdiff = 0.34875000000000267` (floor 0.30; closed form
  `0.36 * 31/32`), bit-identical to the X02 persisted value.
- D sets: `D1 = sorted(analytic_order(0.05,256)[:45])` (45 coords);
  `D2 = sorted(analytic_order(0.20,256)[:140])` (140 coords).
- Streams: `2026091470, 2026091471, 2026091472`, 128 paired blocks each
  (384 pairs in one attempt); public tag masters `stream_seed + 10000` =
  `2026101470, 2026101471, 2026101472` (public control).
- Output root: `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`
  (absent before execution; exactly five files after).
- Frozen command (executed once as written):

  ```bash
  cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
  ulimit -v 2097152
  timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.penalty_gate --n 256 --epsilon1 0.05 --profile strong --k1 45 --k2 140 --seeds 2026091470 2026091471 2026091472 --blocks-per-seed 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate
  ```

## 3. Run result

Single gate execution, exit 0. Persisted outcome label
`HARD_L1_CONDITIONING_PENALTY_CANDIDATE`.

Four-cell paired table (disjoint/exhaustive over 384):

| cell | count |
|---|---|
| `both_exact` | 233 |
| `oracle_only` | 144 |
| `operational_only` | 0 |
| `neither` | 7 |

Per-stream cell split (both / oracle_only / operational_only / neither):

- `2026091470`: 83 / 43 / 0 / 2
- `2026091471`: 72 / 55 / 0 / 1
- `2026091472`: 78 / 46 / 0 / 4

Marginals (all non-exact arms are `verify_failed`; `undetected`,
`decode_failed`, `resource_abort` are all 0 on both arms):

- operational: exact 233 (`verify_failed` 151), exact rate 0.606770833;
- oracle: exact 377 (`verify_failed` 7), exact rate 0.981770833;
- paired exact gap `X = oracle_only = 144`.

Exact lower bound: `L = 0.3338842736427746` for the one-sided 95% oracle-only
event, root of `sum_{j=X}^{384} C(384,j) L^j (1-L)^(384-j) = 0.05` by monotone
bisection; independent recompute `0.33388427364277450`, residual `4.3e-16`;
the first X with `L > 0.30` is X=131. No binomial interval is applied to the
difference of the two marginal rates.

Integrity gates: all ten persisted booleans true (pairing coverage complete;
`p2_maxdiff >= 0.30`; provenance candidate/oracle complete; operational truth
leak zero; undetected zero; nonfinite zero; resource abort zero; cells
disjoint/exhaustive; disclosures exact and transcript recount zero mismatch;
attempt accounting at frozen point). `integrity_all_pass = true`,
`failing_integrity_gates = []`.

Cost: wall `41.187262 s`; peak RSS `211537920 B` (within the 3600 s / 2 GiB
envelope). Exactly one generation of the five files.

## 4. Discriminator definition and rule mapping

Frozen discriminator (all three required):

1. `oracle_exact >= 365` (out of 384) — observed 377, met;
2. `operational_only == 0` — observed 0, met;
3. one-sided 95% exact lower bound `L > 0.30` — observed 0.3338842736427746,
   met.

`operational_only` is structurally impossible when the L1 candidate is correct
(a correct candidate makes the operational `P2_hat` bitwise identical to the
oracle `P2_true`, so both fresh L2 SC calls receive identical arguments and
produce identical labels/tags); observed 0 matches the structural argument.

Rule mapping: integrity all pass AND discriminator pass AND 384-pair shape ->
`HARD_L1_CONDITIONING_PENALTY_CANDIDATE` (persisted exactly). The runner never
claims FER, efficiency, qualification or promotion.

## 5. Accounting and recount

- Fully invoked arm: `5*(K1+K2) + 64 = 5*(45+140) + 64 = 989` key-dependent bits
  (L1 disclosure 225 + L2 disclosure 700 + tag 64).
- Key-dependent bits total `759552` (768 arm-tag invocations x 989); per arm
  `379776` (operational 384, oracle 384).
- Public control `2014464` bits (768 tags x `seed_bits_for(256) = 2623`); per arm
  `1007232`.
- Transcript: 2304 events (L1 disclosure 768, L2 disclosure 768, verification
  tag 768); independent literal recount equals the incremental totals with
  `mismatch_count = 0`, `mismatches = []`.

## 6. Attempt and seed accounting

- `attempts_allowed: 1`; the single attempt is consumed at the first gate L1 SC
  call (stream 0, block 0). Persisted `attempts_consumed_before = 0`,
  `attempts_consumed_by_this_run = 1`, `retries = 0`.
- Streams consumed: `2026091470..2026091472` (128 paired blocks each). Public tag
  masters `2026101470..2026101472` are public control only.
- No rerun, no seed change, no model/K/threshold/set change. A non-frozen-seed
  CLI smoke (temp root) was used earlier for development only and is not part of
  the gate.
- `STATUS.yaml` now records `attempts_used: 1` (this closeout owned the ledger
  update; the runner deliberately does not touch it).

## 7. Review verdicts

- Independent Pre-EXECUTE R0 = `NEEDS_CHANGES` with one docs-only blocker B-1:
  `P5_FREEZE.md`/`P5_IMPLEMENTATION_NOTES.md` enumerated the masters as
  `2026092470..2026092472` (seed+1000) while the frozen definition, packet,
  authorization and module constant (`PUBLIC_TAG_MASTER_OFFSET = 10000`) are
  `seed+10000` = `2026101470..2026101472`. Repaired docs-only; executable
  contract, seeds, sets, command and root unchanged.
- Independent Pre-EXECUTE R1 = `PASS`: B-1 closed with corrected values; no
  collateral change; all frozen items and premises re-verified.
- Independent Pre-RESULT = `PASS_WITH_COMMENTS`: no blocking issue; every
  number, gate and the discriminator root independently recomputed from the
  five persisted files; result may be solidified as-is.

## 8. Output files

`.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`
(exactly five; sizes in bytes):

| file | bytes |
|---|---|
| `frozen_plan.json` | 6722 |
| `per_block_paired_outcomes.json` | 535730 |
| `transcript_accounting.json` | 1240 |
| `aggregate_summary.json` | 4040 |
| `report.md` | 1479 |

## 9. Bounded scope

Synthetic single-point N=256 hard-conditioning penalty signal only; not
real-data FER, efficiency, qualification or promotion. The operational-arm
numbers are interface diagnostics. No artifact/real data, no empirical
construction, no N>256, no FWHT/SCL, no APP/soft path, no cross-layer soft
transfer, no adaptive K, no scalable/list decoder, no old evidence root
modification, no sibling-checkout content access, no commit/push.

## 10. Carried non-blocking notes

1. Per-block `oracle_candidate_divergence` is in-memory only; the structural
   argument for `operational_only == 0` rests on the code + the contingency
   table + the tiny-n focused test, not on a persisted per-block bitwise
   divergence field. Optional future observability; not required by the freeze.
2. Gate 10 (`attempt_accounting_at_frozen_point`) is a frozen-record
   self-consistency check (module constants + coverage), not an external ledger
   read; the main thread / this return own the ledger.
3. The task prompt cited 13 `test_nbpolar_*.py` files; the actual glob is 14
   (totals unchanged).
4. Test totals: focused `test_nbpolar_penalty_gate.py` 9 passed; full NB-Polar
   predecessor suite plus the new file 201 passed (9 new + 192 predecessors, 14
   files).
5. Frozen-point single operating point (X02-screened); the gate is not a sweep
   and does not estimate a rate region.

## 11. Unrun stages and status

Unrun stages: none. The only remaining lifecycle step is main-thread acceptance
adjudication. No OpenSpec box was checked. No commit or push was performed.
