# P5 freeze — NB-Polar Phase 5 static protocol development gate

Rev 1 (2026-09-13). Rev note R1/R2 below resolves packet wording defects per the
two main-thread rulings of 2026-09-13; no other semantics changed.

Status: **FROZEN, awaiting independent Pre-EXECUTE PASS; authorizes nothing.**

No 300-block development attempt has been executed. The single attempt is
**0 consumed** at freeze; it is consumed at the first scientific `sc_decode`
call of the frozen command below. `attempts_used` stays 0 until then.

## 0. R1/R2 main-thread rulings (supersede packet wording)

- **R1 (disclosure orientation).** The static DISCLOSED set is
  `construction.analytic_order(0.05, 256)[:45]` — the 45 *highest-risk*
  coordinates. This matches the accepted Phase 3 point (`evaluate_blocks(...,
  k=45)`) and `docs/nbpolar/ARCHITECTURE.md` ("Alice sends the actual values
  `U[D]`"). The TASK_PACKET phrase "information set ... disclose its
  complement" and the design.md sentence "disclose the complement" are
  superseded wording; the implementation discloses the order's first 45
  coordinates and SC-reconstructs the remaining 211.
- **R2 (label domain).** The physical label vector is the 10-bit single-layer
  embedding `label_j = 32 * x_hat_j` with `x_hat = U_hat G`, low half constant
  zero. The verification message domain is `10*N = 2560` bits; the Toeplitz
  seed per verification is `message_bits + 63 = 2623` public control bits.

## 1. Scope

One static, synthetic-only reconciliation protocol at the accepted Phase 3
point plus a thin `IRMethod` adapter, focused tests, a budget profile, and one
preregistered 300-block development gate after this freeze receives an
independent Pre-EXECUTE PASS. Not real-data FER, leakage efficiency, key rate,
qualification or promotion. No adaptive disclosure, retry, SCL/CRC, rate scan,
benchmark comparison, Phase 6, sibling write, commit or push.

## 2. Frozen implementation identity

| item | value |
|---|---|
| core | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/protocol.py` |
| adapter | `comparison_bench/src/comparison_bench/methods/nbpolar_static.py` |
| tests | `comparison_bench/tests/test_nbpolar_protocol.py` |
| re-exports | `comparison_bench/src/comparison_bench/formal_ir/nbpolar/__init__.py` (explicit names only) |
| interpreter | `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python` (3.12.3, numpy 2.5.3) |
| accepted predecessors reused unchanged | `algebra.make_gf32`, `transform.polar_transform`, `sc.sc_decode`, `synthetic.generate_erasure_block`, `construction.analytic_order`, `shared.toeplitz_tag/canonical_event/transcript_summary` |
| untouched | frozen `src/`, `experiments/`, `tools/`, `results/`, `comparison_bench/outputs_comparison/`, sibling checkouts, accepted nbpolar modules |

## 3. Frozen point and per-block protocol

- GF32 polynomial basis, primitive polynomial 37, alpha 2, natural index order.
- q-ary erasure channel, `N=256`, `epsilon=0.05`, `K=45`.
- `D = sorted(analytic_order(0.05, 256)[:45])`, computed at runtime from the
  accepted analytic order; the set (not the query order) is frozen. The 45
  coordinates passed to SC are:

```text
worst-first slice: [0, 1, 2, 4, 8, 3, 16, 5, 32, 6, 9, 10, 64, 17, 12, 128, 18, 33, 7, 20,
                    34, 24, 11, 65, 36, 66, 40, 13, 129, 68, 19, 14, 48, 130, 72, 21, 132, 80,
                    22, 35, 136, 96, 25, 144, 26]
ascending (SC known_positions):
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22,
                     24, 25, 26, 32, 33, 34, 35, 36, 40, 48, 64, 65, 66, 68, 72, 80, 96, 128,
                     129, 130, 132, 136, 144]
```

Per attempted block, with an explicit `numpy.random.Generator` created once
from the frozen run seed and consumed sequentially:

1. `x, _, logp = generate_erasure_block(rng, 32, 256, 0.05)`.
2. `U = polar_transform(x, field, alpha=2)`.
3. Alice publishes the actual `U[D]` values including zeros; zeros are values,
   never sentinels. SC receives only `known_positions=D`, `known_values=U[D]`.
4. Exactly ONE `sc_decode(logp, field, alpha=2, known_positions=D,
   known_values=U[D])`.
5. `labels_true = 32*x`; `labels_hat = 32*res.x_hat`.
   `exact = (u_hat == U) and (labels_hat == labels_true)`.
6. At most ONE verification AFTER decode: 64-bit Toeplitz tag over the
   MSB-first 10-bit expansion of the label vector (2560 message bits), with the
   per-block seed of §4. Tag pass & exact -> `exact`; tag pass & not exact ->
   `undetected`; tag mismatch -> `verify_failed`. SC exception or nonfinite
   marginals -> `decode_failed` with no tag invocation. A block not executed
   because the preregistered budget stop fired -> `resource_abort`.
7. The tag never selects, retries or modifies a decoder path. There is exactly
   one decoder invocation per attempted block, including on tag mismatch.

Outcome precedence: `resource_abort` > `decode_failed` > `verify_failed` >
`exact` > `undetected` (first matching rule wins; the buckets are disjoint and
exhaustive over the planned blocks).

## 4. Frozen seeds and verification accounting

- Run seed **2026091317**. Unused by Phase 1-4: `git grep 2026091317 HEAD`
  returns zero matches (recorded 2026-09-13 before implementation). It is used
  only by the frozen 300-block command. Tests never use it.
- Banned/consumed run seeds refused by `validate_run_seed`:
  `2026091200..2026091213` (Phase 1-3 unit/TRAIN/DEV/EVAL/protocol seeds) and
  `2026091314/2026091315/2026091316` (P3 units/TRAIN/Stage B).
- Toeplitz master seed **2026091318** (also absent from `HEAD`). Per-block seed
  rule (public, documented, deterministic, never persisted raw): concatenate
  `SHA-256("nbpolar-p5-toeplitz-seed:2026091318:<block_index>:<counter>")` for
  `counter = 0,1,...` (ASCII decimal), unpack each digest MSB-first, truncate
  to `2623` bits. Seed bits are public control.
- Per attempted block: `key_dependent_bits = 5*45 + (64 if verification
  invoked else 0)`; a `decode_failed` block discloses only `225` bits and
  invokes no verification. `public_control_bits = 2623` per verification
  invocation, reported separately.
- Independent literal event recount (`recount_transcript`) walks the in-memory
  event list and must equal the incremental totals exactly; any mismatch is a
  hard-gate failure. Per verification invocation the key-dependent total is
  `225 + 64 = 289` bits.
- Truth isolation: the metric is built only from the channel observation; SC
  receives only the disclosed subset; an adversarial post-decision mutation of
  the truth buffers must leave Bob's metric and decisions bitwise unchanged
  (violations counted, must be 0).

## 5. Budget and resource ceilings (synthetic profile evidence)

Profile: `protocol.execute_blocks` in memory, profile seed 2026091330,
non-frozen seed, no output files (command: `.venv/bin/python /tmp/opencode/p5_profile.py`).

| workload | blocks | median wall | max wall | median metric | median decode | outcomes |
|---|---|---|---|---|---|---|
| N=64, K=45 | 64 | 4.24 ms | 14.79 ms | 0.06 ms | 4.18 ms | 64 exact |
| N=256, K=45 (frozen point) | 64 | 15.61 ms | 19.90 ms | 0.13 ms | 15.48 ms | 64 exact |
| N=1024, K=45 probe | 8 | 11.69 ms | 16.66 ms | 0.39 ms | 11.31 ms | 8 decode_failed (early SC exception) |
| N=1024, K=160 scaling probe | 14 | 70.74 ms | 74.24 ms | 0.42 ms | 70.08 ms | 14 exact |
| N=1024, K=320 scaling probe | 14 | 69.69 ms | 77.35 ms | 0.39 ms | 69.31 ms | 14 exact |

Peak RSS across the whole profile process (includes the N=1024 probes):
**120000512 bytes ≈ 114.4 MiB**.

Frozen ceilings:

- total wall budget: **300 s** (`DEV_GATE_TOTAL_WALL_S`; ≈ 64× the expected
  `300 × 15.6 ms ≈ 4.7 s`). On expiry, remaining planned blocks are
  `resource_abort` and the five files are still written.
- per-block soft cap: **5.0 s** (`DEV_GATE_PER_BLOCK_SOFT_CAP_S`; ≈ 250× the
  observed N=256 maximum of 19.9 ms). On expiry after a completed block,
  remaining planned blocks are `resource_abort`.
- external command timeout: **T = 600 s** (`timeout 600`), 2× the internal
  total budget so the internal stop fires first and the evidence is written.
- memory envelope: `ulimit -v 2097152` (2 GiB virtual); the plan records
  `rss_bytes_max = 2147483648`, and the actual peak RSS is measured and
  persisted in `aggregate_summary.json` (`rss_bytes_peak`), measured profile
  peak 114.4 MiB.

## 6. Frozen output root and schema

Root (relative to repo):
`.workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate/`

Confirmed **ABSENT** at freeze. The CLI refuses an existing root before any
decoder call. Exactly five compact files are written; no symbol vectors,
decoded keys, per-block disclosed value lists, per-block Toeplitz seed
contents, or transcript raw events are persisted:

1. `frozen_plan.json` — `protocol, mode, created_utc, repository, run_seed,
   planned_blocks, q, n, k, epsilon, field{}, channel, disclosure_rule,
   disclosure_coordinates[45], label_domain{}, toeplitz{}, outcome_precedence[],
   budget{}, attempt_consumption_point`.
2. `per_block_outcomes.json` — `n_blocks` and one scalar record per block:
   `block_index, outcome, exact, verification_invoked, key_dependent_bits,
   public_control_bits, nonfinite, truth_leak_violation, error_type,
   metric_wall_s, decode_wall_s`.
3. `transcript_accounting.json` — `event_count, incremental{key_dependent_bits,
   public_control_bits, verification_invocations}, recount{...},
   mismatch_count, transcript_sha256`.
4. `aggregate_summary.json` — output totals for the five buckets, `attempted`,
   `coverage`, `verified` (explicit `exact + undetected` union), 
   `verification_invocations` (`exact + undetected + verify_failed`),
   `undetected`, key-dependent/public totals, average key-dependent bits per
   attempted block, transcript block with recount and mismatch count,
   `truth_leak_count`, `nonfinite_count`, `decode_error_types`, `wilson{}`,
   `hard_gates{}`, `candidate`, bounded `claim_scope`, `wall_s`,
   `rss_bytes_peak`, `resource_stop_fired`.
5. `report.md` — bounded human-readable summary.

## 7. Wilson calculation and hard gates

One-sided 95% Wilson lower bound for exact recovery, successes `s = exact`,
denominator `n = attempted` (executed blocks; `resource_abort` blocks are not
attempted and not in the denominator):

```text
p = s/n;  z = 1.6448536269514722
lower = (p + z^2/(2n) - z*sqrt(p(1-p)/n + z^2/(4n^2))) / (1 + z^2/n)
n = 0 -> lower = 0
```

Hard gates (all must be true for the candidate label; each is persisted as a
boolean in `hard_gates`):

1. `outcome_accounting_disjoint_exhaustive` — the five bucket counts sum to the
   planned 300;
2. `coverage_complete` — attempted == planned;
3. `resource_stop_preregistered` — any `resource_abort` came from the frozen
   budget stop;
4. `per_block_disclosure_consistent` — per-block key-dependent/public bits obey
   the §4 formula;
5. `verification_universe_consistent` — verification invocations equal
   `exact + undetected + verify_failed` and equal the transcript recount;
6. `recount_zero_mismatch` — recount totals equal incremental totals;
7. `undetected_zero`;
8. `truth_leak_zero`;
9. `nonfinite_zero`;
10. `wilson_lower_ge_0_90`;
11. `avg_key_dependent_below_input_bits` — average key-dependent bits per
    attempted block < `10*N = 2560`.

Only if all eleven gates pass is the label
`STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE` emitted; otherwise `candidate` is null.
The label is a synthetic development signal only.

## 8. Exact frozen command (recorded, NOT executed in this session)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.protocol --mode dev-gate --run-seed 2026091317 --blocks 300 --out .workbuddy/queue/NBPOLAR-PHASE5-STATIC-PROTOCOL/static_protocol_dev_gate
```

No flags may be added or changed. The output root must still be absent at
execution time. The attempt is consumed at the first scientific `sc_decode`
call; on any failure it stays consumed — no rerun, no parameter tuning, no seed
change. There is no partial-credit path.

## 9. Forbidden-path proof

- `protocol.py` imports only stdlib (`argparse, hashlib, json, math, sys, time,
  dataclasses, numbers, pathlib`), numpy, and the accepted nbpolar modules plus
  `formal_ir/shared.py`. No artifact, parquet, TTBin, DEV/EVAL, benchmark,
  Model-F, sibling-checkout, SCL/CRC or rate-adaptation code path exists in the
  module; no import-time I/O; no global RNG; the only write target is the
  explicitly passed output root (created after the run, refused if present).
- The adapter builds its metric from the passed observation only; Alice truth
  never enters the metric or the decoder arguments.
- `test_no_forbidden_markers_or_import_time_side_effects` scans both source
  files for `outputs_comparison`, `model_f`, `v72p2d5`, `parquet`, `ttbin`,
  `results/`, `HD-QKD_Polar_Comparison/`, `DEV_SEED`, `EVAL_SEED` and requires
  zero occurrences.
- Tests use only temporary directories and synthetic generators; no real data,
  artifact, or `comparison_bench/outputs_comparison/` path is touched.
- The sibling checkout is used read-only as the pinned interpreter only
  (`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`).

## 10. Pre-EXECUTE checklist for the independent reviewer

1. Confirm this freeze doc is the authoritative Rev 1 and matches the
   implemented constants (`FROZEN_RUN_SEED`, `TOEPLITZ_MASTER_SEED`, `SEED_BITS`,
   `DEFAULT_N/K`, budgets, `D` set).
2. Recompute `D = analytic_order(0.05,256)[:45]` and compare the set.
3. Re-run the focused suite and all nbpolar predecessor tests.
4. Confirm the 300-block command and output root above; confirm the root is
   absent and `STATUS.yaml` grants only the authorized flags with
   `attempts_used: 0`.
5. Confirm `git grep 2026091317 HEAD` and `git grep 2026091318 HEAD` are empty.
6. FAIL blocks execution; issues return to the operator for scoped repair and
   re-review.
