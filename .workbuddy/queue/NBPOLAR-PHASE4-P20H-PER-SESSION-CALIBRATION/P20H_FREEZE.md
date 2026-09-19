# P20H freeze — per-session-calibration +1024 confirmation on type2_1p5M_20260121_183806 (Stage A implementation)

Packet: `NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION` (`TASK_PACKET.md`, 416
lines, frozen). Predecessor: P20G terminal
`BLOCKED_TARGET_POPULATION_CONTRACT_ACCEPTED_TERMINAL_DESCRIPTIVE` (1M
literals H1 0.02428054681872374 / H2 0.7767572780789994 / TOTAL
0.8010378248977232 mismatch the 1.5M counts array; NPZ open 1/1 +
attempt 1/1 SPENT; DEV 0 opens) + P20A `IMPLEMENTATION_ACCEPTED`
(resource passthrough + endpoint instrumentation). Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 (reproducible
reliability: confirm the frozen candidate on new blocks/sessions;
development blocks never become the confirmation sample). Tier-Y
decision-gate packet: Stage A (this document + implementation + tests +
calibration product) is authorized separately from Stage B (single
authorized execution).

This document authorizes nothing. No box in `tasks.md` is checked by the
implementing session. Stage B additionally needs an independent Pre-EXECUTE
PASS (explicitly adjudicating the §3 calibration-vs-tuning gate (i)–(iv))
plus a separate pasted Stage-B authorization.

## 1. Mission (one frozen per-session-calibration question, zero further tuning)

> With ONE preregistered change against P20G — the prior is per-session
> calibrated on 1.5M TRAIN counts by the frozen §3 program (Stage A,
> DEV-zero-contact, read-only in Stage B) — and everything else carried
> over byte-identical from P20C/P20E/P20F/P20G (K1=319, K2 base 6492 / B1
> 7516 via frozen order-prefix extension, floor 1e-15, N=32768, new P20H
> tag domains only), zero further tuning, does +1024 maintain exact on
> three 1.5M TRAIN-first-384-frame blocks — and does a P20C-style
> restoration event (B0 fail → B1 exact) appear on
> per-session-calibrated data, or not?

P20G DEV 0..383 is UNCONSUMED (0 records, DEV never content-opened) and
is therefore the legitimate P20H DEV range. All branches after this
packet are deferred to §16 of the packet and must not be prejudged here.

## 2. Calibration freeze (normative — the single deliberate delta vs P20G)

FROZEN program = the accepted P0/P2 Model-F concentration fitting
program, isomorphic (same formula / smoothing / flow), new-session input
only, executed ONCE in Stage A (counts-calibration open 0→1 consumed):

- Formula: `p_global[a] = sum_b counts[a,b]/sum counts`;
  `n_b[b] = sum_a counts[a,b]`;
  `f[a,b] = (counts[a,b] + lambda*p_global[a])/(n_b[b]+lambda)`.
  Column meaning `P(A|B)` shape (1024,1024) `[Alice,Bob]`; unseen-Bob
  column falls back to `p_global` exactly. Banned per-cell twin
  (`build_f_model` `counts+lam`) never called, never imported.
- Adapter chain: accepted `derive_p1`/`derive_p2` under packing
  `A = 32*U1 + U2`, joint-Bob conditioning `FULL_BOB_ONLY`, fixed
  `1e-15` floor + column renormalization before SC, `SymbolMetric`
  log-domain contract.
- Lambda (frozen literal + provenance): `137.3823795883264` — the
  accepted fitting-program constant procedure output (D4R2 nested-CV
  refit, carried via `prior_artifact.LAMBDA_STAR`; verified equal in
  Stage A). No hand-fill, no DEV influence, no per-session search, no
  floor search.
- Input (sole allowed): 1.5M TRAIN counts ONLY (`--source 1p5M`):
  NPZ `/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/
  outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/
  channel_counts.npz`, size 25166822 B, counts shape (1024,1024) float64,
  counts total 424960 == split-manifest TRAIN pairs 424960
  (cross-check passed, fail-closed), counts sha256
  `e5e99cc89a09ec913b82af7d061cc462af7bf57404c6d97c06537de9c3a2d59c`.
  FORBIDDEN inputs (untouched): 1.5M DEV/VAL/HOLD, any 1M split,
  reserved 2M, Model-F CAL artifact.
- Output (Stage-A frozen, Stage-B read-only):
  `per_session_calibration/` (five files): `calibration_plan.json`
  (pre-open pins), `calibration_input_identity.json` (post-open
  identity), `calibrated_prior.npz` (keys exactly `counts_ab`,
  `f_prior`, `p1`, `p2`, `p_b`, `lambda_star`, `floor_value`, `h1`,
  `h2`, `h_total`; 25438654 B), `recalibrated_literals.json`,
  `calibration_report.md`.
- Recalibrated literals (replacing the 1M literals for the
  `target_population_contract` gate): H1 `2.006647056368773` / H2
  `1.9017235959286112` / TOTAL `3.908370652297384` (floor-table entropy
  functionals on the calibrated prior; unfloored-smoothed total differs
  by floor_change 4.440892098500626e-16; column_dev 7.327471962526033e-15).
- Prior canonical digest (Stage-B calibration-identity pin):
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
  (sorted-key `key + shape + dtype + C-order bytes` sha256; independent
  of NPZ zip timestamps).
- §3 (i)–(iv) evidence for Pre-EXECUTE: (i) input = 1.5M TRAIN counts
  only (source pin + manifest cross-check 424960/424960 in
  `calibration_input_identity.json`); (ii) DEV zero contact before
  freeze (calibration module has no pairs/parquet code path; module
  guards `_COUNTS_CONTENT_OPENED` audit; DEV opens 0 at Stage-A close);
  (iii) program isomorphic (focused test recomputes the full pipeline
  against an independent literal formula ≤1e-12 / ≤1e-9; banned twin
  absent by source test); (iv) frozen before execution, read-only in
  Stage B (digest gate refuses on mismatch; no refit path exists in the
  runner — no counts loader, no smoothing import).

## 3. Fixed identities (verified in this session; JSON provenance only + the single counts open)

P16 accepted file
`.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
(JSON read only; P16 immutable, never modified):

| item | verified value |
|---|---|
| protocol | `nbpolar-p16-operational-f13-gate`, frozen before first DEV |
| canonical digest (recomputed here via the accepted `verify_predecessor_construction`) | `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` |
| stored digest / frozen flag | identical (match) |
| n / k1 / k2 / k_total | 32768 / 319 / 6492 / 6811 |

Split manifest
`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`
(JSON read only; verified inside the calibration run):

| item | verified value |
|---|---|
| schema | `nbldpc_v25_split_manifest_v1` |
| 1.5M source tag | `type2_1p5M_20260121_183806` |
| TRAIN frames / pairs | 1660 / 424960 (calibration input host; counts total 424960 match) |
| VAL frames / pairs | 553 / 141568 (intra-file gate, never selected) |
| HOLD frames / pairs | 554 / 141824 (intra-file gate, never selected) |

TRAIN base provenance (Stage-A written equivalent with justification;
the manifest gives counts only, never frame numbering): carried over
from P20G §3 unchanged (time-ordered first-60% split code +
same-pipeline parity with the accepted 1M 0-based layout at 256
rows/frame; total 2767 frames). THEREFORE the frozen TRAIN base is 0:
DEV 0..383 (first 384 TRAIN frames), remainder 384..1659 (1276 frames /
326656 pairs), VAL 1660..2212, HOLD 2213..2766. The runner fail-closes
on any layout drift (`dev_population_exact` requires exactly frames
0..383 with 256 rows each; the triple gate §4 refuses first), so a
wrong base BLOCKS before any SC call instead of misattributing.
Pre-EXECUTE owns the cross-session isolation adjudication (§4).

Build-manifest file pins (carried over from P20G §3; same 1.5M file):
pairs size 1869178 B / sha
`ca351e5205e76600530121066af4e0e1e5278061745c0797368a49443570a06b`.

Any mismatch stops before any root exists and before the DEV content
open, consuming no DEV read and no attempt.

## 4. Development population and closed/consumed-data rule (normative)

The three P18/P19 HOLD blocks (1M frames 1600..1983), the P20B VAL pool
(1M frames 1200..1599), the P20C DEV blocks (1M 0..383), the P20E DEV
blocks (1M 384..767) and the P20F DEV blocks (1M 768..1151, remainder
1152..1199 never used) are CONSUMED/CLOSED and SHALL NOT supply P20H
blocks. The ENTIRE 1M pool is fail-closed against P20H DEV selection by
the cross-file gate. Cross-packet same-block tuning is forbidden.

The 2M session file is RESERVED and was NOT opened, statted, listed, or
read under Stage A. It is not consumed.

Stage B runs on the DECLARED population (P20G-UNCONSUMED, reused
legitimately):

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin; mismatch blocks) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 |
| DEV frame rule | FIRST 384 TRAIN frames of the 1.5M file in (frame_id, pair_idx) order → frozen TRAIN base 0: `0..383` |
| DEV blocks (N=32768) | `0..127`, `128..255`, `256..383` (3 × 128 frames) |
| unused remainder | frames `384..1659` (1276 frames / 326656 pairs) recorded never used — counted, never decoded |
| intra-file VAL / HOLD | 1660..2212 / 2213..2766 — disjoint by fail-closed gate (VAL first) |
| 1M full pool + reserved 2M | excluded by the cross-file gate (checked FIRST); never touched |
| block count | 3 at N=32768 (same cost class as P18/P19/P20B/P20C/P20E/P20F/P20G) |
| tag domains | new P20H domain (§6) |

Fail-closed triple gate (frozen in the runner, order (a)→(b)→(c), VAL
before HOLD): (a) CROSS-FILE — DEV content-open path + stat-size/sha
pin must equal the 1.5M identity; any 1M or 2M path or digest mismatch
refuses before any SC call (frame integers alone are never identity);
(b) INTRA-FILE — DEV ranges must overlap NONE of 1.5M VAL/HOLD, else
refuse before any protected content open; (c) CALIBRATION-IDENTITY —
Stage-B prior/table/literal digest must equal the Stage-A frozen
calibration digest `e8dd078a…e43b` before any SC call, else refuse (this
replaces P20G's failed 1M-literal gate).

## 5. Preregistered disclosure cap (normative, carried over)

Cap rule: caps are CARRIED OVER unchanged from P20C/P20E/P20F/P20G (no
growth, no tuning) — preregistered per arm, frozen before Pre-EXECUTE,
each FAR below raw input bits with its ratio shown.

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| B0_sc_base (operational) | 319 | 6492 | 34119 = 5*6811+64 | 327743 = 10*32768+63 |
| B1_L2plus (operational) | 319 | 7516 | 39239 = 5*7835+64 | 327743 |
| B2_true_l1_diagnostic (oracle) | 0 | 6492 | 32524 = 5*6492+64 | 327743 |

Planned totals if all invoked: key 317646 = 3*34119 + 3*39239 + 3*32524
(operational 220074 + oracle 97572); public 2949687 = 9*327743. B1
key-bit delta vs base exactly +5120 = 5*1024.

Meaningfulness bar: base 34119/327680 = 0.10412292 (~10.41%) and B1
39239/327680 = 0.11974792 (~11.97%) of raw input bits (10*N per block at
N=32768) — both far below raw. Sample-CE-normalized ratios
(`disclosure_ce_ratio`) are reported descriptively and are NOT
qualification efficiency.

Recount rule: independent key/public/tag recount from canonical
transcript events; mismatch 0, or the gate BLOCKS.

## 6. Arms (frozen; +1024 step carried over identical, prior swapped per §2)

Run block-major (B0, B1, B2) per DEV block; checkpoint after every
(arm, block) record; 9 records total.

- `B0_sc_base`: frozen greedy SC at base disclosure/construction
  (operational; accepted `run_operational_block` called directly with
  k1=319/k2=6492; 2 SC + 1 P20H-domain tag per block).
- `B1_L2plus`: frozen greedy SC at base + the carried-over +1024 L2
  step via §2 order-prefix extension, all else identical (operational;
  the confirmation candidate; accepted `run_operational_block` called
  directly with k1=319/k2=7516 on the SAME frozen L2 order object; 2 SC +
  1 tag per block).
- `B2_true_l1_diagnostic`: true-L1-conditioned L2 at BASE disclosure
  (accepted `run_oracle_control_block` called directly with k2=6492 and a
  P20H-domain tag closure; provenance ORACLE, deployable=false, 1 SC +
  1 tag per block; excluded from every operational aggregate; never
  described as a correction result).

No other arms. Tag domain: master 2026092220, prefix
`nbpolar-p20h-per-session-calibration-seed`, seed string
`<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256,
MSB-first, truncated to `10*N+63 = 327743` bits). Prefix, master and arm
tokens differ from the P16, P17, P18, P19, P20B, P20C, P20E, P20F and
P20G domains; raw seed bits are never persisted.

## 7. Thresholds and labels (descriptive only)

Outcome label
`TARGET_EMPIRICAL_N32768_DEV_PLUS1024_PER_SESSION_CALIBRATION_COMPLETE`
iff ALL 21 integrity gates hold — regardless of exact-count. Any exact
count (including 0/9 and any partial outcome) is COMPLETE when integrity
holds. This packet makes NO recovery / FER / Wilson / superiority /
qualification / promotion claim. Confirmation reading is descriptive
only: "repeat recovery" = blocks where B0 fails and B1 is exact on the
calibrated new-session blocks, reported as a count with per-block
endpoint rows; "maintain" = B1 exact where B0 exact, reported the same
way. Either pattern (or its absence) counts as COMPLETE; the
calibration-positive / confirmation-negative / calibration-blocked
branch decision belongs to main-thread planning AFTER acceptance, never
to this packet's label. Status taxonomy frozen: `exact`
(tag-verified) vs `verify_failed`, with `undetected` isolated (never
success), plus `decode_failed` / `nonfinite` / `resource_abort` via the
P20A path.

Per-record separation (P20A endpoints): `l1_exact`, `hard_l2_exact`,
`oracle_l2_exact`, `pair_exact`, `exact`, first error coordinate +
layer, raw zero-count hits, `1e-15` floor hits + log loss,
candidate-H-conditioned vs true-H-conditioned L2 NLL, outcome taxonomy,
plus B1 disclosure fields (`l2_delta_k2_applied` 1024/0,
`l2_disclosure_rule` frozen-order-prefix-extension/base,
`key_bit_delta_vs_base` 5120/0).

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until
  authorized execution; no rerun, no seed change, no
  disclosure/construction/calibration tuning after preregistration. An
  execution error rerun is allowed only as a recorded repeat of the
  identical freeze, never as tuning. P20G's spent attempt does NOT
  transfer (independent packet).
- Reads (split-counted): counts-calibration open 1/1 SPENT in Stage A
  (NPZ 1p5M array, consumed at the single calibration content open) +
  DEV open 1/1 reserved for Stage B (parquet, consumed at first DEV
  content open). HOLD reads 0/1 untouched. Any reopen, second
  calibration, or DEV refit is forbidden.
- SC/tag budget: 15 SC calls (3 blocks x (2+2+1)) and 9 tags; derived
  per-record recomputation (`1+l2_invoked` operational, `l2_invoked`
  control) must equal the counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative (`MemoryError` re-raised
  at both operational SC sites and the oracle site; accepted helpers
  unchanged); abort preserves evidence + call/disclosure accounting;
  abort is BLOCKED, never success.
- Wall/RSS ceilings: 600 s external timeout, 2 GiB virtual limit
  (`ulimit -v 2097152`), 2 GiB RSS cap, single-thread BLAS/OpenMP +
  `MALLOC_ARENA_MAX=2` — the P20C class (P20C reference at the identical
  15 SC / 9-tag budget at N=32768: ~92.9 s wall, ~579 MB RSS peak;
  P20E observed ~100.1 s / ~554 MB; P20F observed ~93.0 s / ~553 MB;
  P20H plans the identical 15 SC / 9-tag decoder budget, strictly
  inside the same class). Calibration cost is separately recorded:
  0.420163 s wall for the single calibration open + frozen-program
  application (array footprint order tens of MB; far below the 2 GiB
  cap; no second calibration will be run).
- Strategy stop rules restated as binding: no tuning on closed blocks; no
  reuse of the consumed 1M pool (any split, any subrange) or the
  reserved 2M file; no third factor after an inconclusive single-factor
  result; no near-raw disclosure feasibility claim; no
  oracle-as-operational; no population-reliability inference from this
  single gate alone (one per-session-calibrated session is necessary but
  not sufficient for a reliability claim); no efficiency tuning inside
  this confirmation packet.
- SCL entry gate UNCHANGED (all five strategy conditions must still be
  shown; this confirmation unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage-A calibration product + Stage-B five files)

- Calibration product (Stage A, frozen):
  `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/`
  (exactly five files): `calibration_plan.json`,
  `calibration_input_identity.json`, `calibrated_prior.npz` (keys
  exactly `counts_ab`, `f_prior`, `p1`, `p2`, `p_b`, `lambda_star`,
  `floor_value`, `h1`, `h2`, `h_total` — the ONLY prior Stage B may
  load, digest-pinned), `recalibrated_literals.json`,
  `calibration_report.md`. Scalar-only elsewhere: never sampled
  symbols, truth vectors, decoded labels/keys, metric planes, raw rows,
  per-arm orders, tag seeds or RNG state beyond the pinned
  tables/digests.
- Stage-B root: `.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_confirmation/`
  (exactly five files, created pre-open; per-(arm, block) checkpointing;
  one DEV content open; no reopen/rerun). Root is ABSENT at Stage-A
  close and must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`,
  `input_and_predecessor_identity.json`, `per_block_arm_outcomes.jsonl`
  (9 records at completion), `aggregate_summary.json`, `report.md`.
  Scalar-only: never counts, sampled symbols, truth vectors, decoded
  labels/keys, metric planes, raw rows, per-arm orders, tag seeds or RNG
  state.
- Accounting: key/public/tag disclosure + independent recount (mismatch
  0); SC-call counts (L1/L2 split) and tag-invocation counts exact;
  block SER/NLL; wall/RSS (decoder + calibration reported separately);
  `b1_restored_count` analogue recomputed descriptively (B0 fail→B1
  exact on calibrated blocks).
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `dev_split_manifest_identity`;
  `dev_block_range_identity` (TRIPLE gate: cross-file source-tag+digest
  pin first, then intra-file DEV-vs-VAL/HOLD overlap with VAL first,
  then calibration-identity digest pin);
  `calibration_identity` (prior digest + lambda/floor pins + key-set
  exactness); `target_population_contract` (recalibrated literals,
  recomputed H1/H2 within 1e-12 + column normalization);
  `dev_population_exact` (384 frames / 98304 pairs / 256 rows per frame /
  pair indices / symbol range);
  `blocks_exact_with_declared_remainder` (three exact DEV ranges per arm
  in block-major slot order + never-used remainder 1276 frames / 326656
  pairs, counted from the pool but never decoded); `nine_records_exact`;
  `sc_calls_exact` (derived 15); `tags_exact` (derived 9);
  `orders_valid_k_prefixes_within_registered_arms` (per-arm K1/K2 pins +
  B1 disclosure triple); `oracle_isolation`;
  `buckets_disjoint_exhaustive` (unique arm/block + schema);
  `undetected_zero`; `nonfinite_zero`; `truth_isolation`;
  `disclosure_recount_exact`; `one_open_per_protected_input`;
  `input_stat_unchanged`; `no_unregistered_access`;
  `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen here)

Stage A (calibration-freeze; the authorized command for this stage,
executed ONCE — counts 0→1 consumed here):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.per_session_calibration --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1p5M --lambda 137.3823795883264 --floor 1e-15 --manifest comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration
```
Six flags, all required, no production default; refuses on any
non-`1p5M` source, non-frozen lambda/floor, manifest mismatch, counts
total mismatch, existing root or reopen. Result: `counts_content_opens
1`, `counts_total 424960`, H1/H2/TOTAL
`2.006647056368773/1.9017235959286112/3.908370652297384`, prior digest
`e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`,
wall 0.420163 s.

Stage-A test commands (injected only, fresh additive temp roots, zero
protected opens):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_per_session_calibration.py \
  comparison_bench/tests/test_nbpolar_plus1024_per_session_confirmation.py \
  -q -p no:cacheprovider --basetemp=$PWD/workspace/p20h/new-suites
```
→ 53/53 green. Packet-scoped predecessors (same settings, fresh
basetemp `workspace/p20h/pred-suites`): plus1024_independent_session 36
+ plus1024_extension 36 + plus1024_confirmation 36 + l2_backoff 34 +
bounded_search 34 + opf 29 + replication 25 + microcheck 26 + backoff 33
= 289/289 green. No shared predecessor code was changed.

Stage B execution command (NOT AUTHORIZED until independent Pre-EXECUTE
PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_per_session_confirmation --prior .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 0 383 --block-frames 128 --remainder-frames 384 1659 --tag-master 2026092220 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_confirmation
```
Sixteen flags, all required, no production default (`--prior` replaces
P20G's `--counts`; the V25 counts NPZ is never opened in Stage B);
three hardcoded arms with the +1024 prefix-extension pinned (never
CLI-tunable). Byte-identical to the module `FROZEN_COMMAND` (verified
by import in this session). Forbidden by default: `longrun_*`,
`minrerun_*`, `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data,
full sweeps.

Read-only verify: reviewer recomputes §9 identities from artifacts; never
`git show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Stage-A verification evidence (implementation time)

- Output root absent: the Stage-B root `per_session_confirmation/` does
  not exist. The queue dir holds only `TASK_PACKET.md`, `STATUS.yaml`,
  `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `per_session_calibration/`
  (five files), `P20H_FREEZE.md`, `P20H_IMPLEMENTATION_NOTES.md`.
- Single declared counts-calibration open: the §10 calibration command
  ran exactly once (result `counts_content_opens 1`, wall 0.420163 s);
  the counts total (424960) matched the manifest TRAIN pairs; the
  calibration input identity pins the NPZ path + size 25166822 B +
  counts sha + shape (1024,1024). No second calibration, no reopen.
- DEV-zero-contact: the calibration module has no pairs/parquet code
  path (asserted by source test); no 1.5M DEV/VAL/HOLD content open or
  stat in this stage (DEV opens 0 at close). Only JSON provenance
  reads: P16 construction file (digest recomputed, §3), the split
  manifest (verified inside the calibration run), the build-manifest
  pins carried over from P20G §3.
- The 1M pool was never opened (only the 1p5M key of the loaded counts
  dict was accessed); the 2M session file was never opened, statted,
  listed, or read in any form (the runner's 2M refusal path is a string
  literal only; one inadvertent parent-directory listing during early
  inventory is recorded in the notes for main-thread adjudication).
- P16 digest recomputed in this session: `055c90...c3faea1b`, equal to
  the stored freeze digest and the frozen flag; P16 root untouched.
- Fresh focused-test seeds 2026092221..2026092227 and frozen tag master
  2026092220 appear in NO tracked file outside the P20H runner/tests/
  packet/spec documents (`git grep` verified — same bar as P20G).
- Focused suites: calibration 17/17 + per-session-confirmation 36/36 =
  53/53 green (fresh temp basetemp, pinned interpreter, `-p
  no:cacheprovider`).
- Packet-scoped predecessor suites 289/289 green (same settings, fresh
  basetemp). No shared predecessor code was changed, so the full
  NB-Polar suite was not run (recorded in the notes).
- No commit (no commit/push authorized in Stage A).

## 12. Forbidden paths and scope boundary (Stage A observed)

Forbidden and not done: second counts-calibration open, any
DEV/VAL/HOLD/EVAL/raw content open or stat, the 2M file in any form
(see the one parent-listing note in §11), 1M-pool tuning or peeking,
other N in the frozen run, any added/changed arm, any construction
path, BEC, transform/belief/list decoders, a second tag outside the
registered arms, fitting/sampling on DEV, any use of the remainder/1M
consumed/closed frames or the reserved 2M file, a second disclosure
step (`B1b`), an alternative-construction second factor, per-DEV prior
refit, production benchmark, `results/` or
`comparison_bench/outputs_comparison/` writes, P12-P20G code or
old-root modification, official prior/probe seed reuse, commit/push.
Scope is the frozen calibration program + implementation + frozen
planning artifacts for a descriptive per-session-calibration diagnostic
on new blocks; it is not real-frame FER, reconciliation efficiency,
leakage, key rate, scaling, qualification or promotion evidence, and B2
is never operational.
