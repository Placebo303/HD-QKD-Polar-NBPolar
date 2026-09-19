# P20E freeze — N=32768 +1024 confirmation on new blocks (Stage A implementation)

Packet: `NBPOLAR-PHASE4-P20E-PLUS1024-CONFIRMATION` (`TASK_PACKET.md`, 334
lines, frozen). Predecessor: P20C
`TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE_ACCEPTED_DESCRIPTIVE`
+ P20A `IMPLEMENTATION_ACCEPTED` (resource passthrough + endpoint
instrumentation). Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 (reproducible
reliability: confirm the frozen candidate on new blocks/sessions;
development blocks never become the confirmation sample). Tier-Y
decision-gate packet: Stage A (this document + implementation + tests) is
authorized separately from Stage B (single authorized execution).

This document authorizes nothing. No box in `tasks.md` is checked by the
implementing session. Stage B additionally needs an independent Pre-EXECUTE
PASS plus a separate pasted Stage-B authorization.

## 1. Mission (one frozen confirmation question, zero tuning)

> With construction / disclosure / order / prior / floor / kernel /
> representation / SC all carried over byte-identical from P20C (K1=319,
> K2 base 6492 / B1 7516 via frozen order-prefix extension, floor 1e-15,
> N=32768, new P20E tag domains only), zero tuning, does +1024 repeat its
> P20C recovery and maintain exact on independent new blocks — or does
> it not?

P20C's TRAIN 0..383 signal was descriptive development evidence, not
proof. This packet asks only whether that signal repeats on blocks the
candidate has never seen. Positive (repeat recovery / maintained exact)
directs a later efficiency-optimization round; negative (no repeat)
returns to the P20D alternative-construction candidate. Both branches
are deferred and must not be prejudged here.

## 2. Zero-tuning freeze (normative)

FROZEN identical for every arm (any deviation is a packet violation):

- Prior: frozen Model-F concentration prior path (`target_preconditions`
  + `derive_p1`/`derive_p2`, accepted P7 rule) with fixed `1e-15` floor
  applied before SC. Raw zero-count hits, floor hits and their log loss
  are diagnosed per selected candidate, never retuned.
- Construction order: accepted P16 order, K1=319 base L1 set unchanged on
  every arm (permutation fixed by the accepted construction file; digest
  pinned in §3).
- Carried-over +1024 step: `B1` discloses ΔK2 = +1024 L2 symbols beyond
  the frozen base (K2 6492 → 7516; K_total 6811 → 7835) by
  FROZEN-ORDER-PREFIX EXTENSION — the disclosed L2 set is the first 7516
  positions of the frozen P16 L2 order. Positions are fixed by the
  construction file, never selected on closed blocks, the consumed VAL
  pool, the consumed P20C DEV blocks, or the new DEV data. No second
  step (`B1b`) without a new packet and a written necessity argument.
- Disclosure base: K2=6492 (B0, B2); kernel / representation / transform /
  SC arithmetic: unchanged; greedy SC is the baseline; no SCL, no new
  kernel/model/schema.
- Verification: one final 64-bit Toeplitz tag per block/record under new
  P20E tag domains (§6); verification never selects a candidate.

VARIED: NOTHING. The only deliberate differences from P20C are the
new-block population (§4) and the new tag domain (§6) — both
provenance/identity changes, never algorithm changes.

## 3. Fixed identities (verified in this session before any protected open)

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
(JSON read only):

| item | verified value |
|---|---|
| schema | `nbldpc_v25_split_manifest_v1` |
| 1M source tag | `type2_1M_20260121_184040` |
| TRAIN frames / pairs | 1200 / 307200 (development pool host) |
| VAL frames / pairs | 400 / 102400 (P20B-consumed, never re-entered) |
| HOLD frames / pairs | 400 / 102400 (frozen requirement, unchanged) |

TRAIN range provenance (Stage-A confirmation of the packet-recommended
subrange): 1200 + 400 + 400 = 2000 frames per the manifest; VAL
1200..1599 (P20B-accepted) + HOLD 1600..1999 (P18-accepted, blocks
1600..1983 + remainder 1984..1999) pin TRAIN to frames 0..1199 by
elimination. The P20E DEV subrange 384..767 sits inside TRAIN; the
runner additionally fail-closes (`dev_population_exact` requires
exactly frames 384..767 with 256 rows each; the triple overlap gate §4
refuses first), so any layout drift blocks before any SC call. Declared
never-used remainder frames 768..1199 (432 frames, 110592 pairs) are
counted from the pool but never decoded.

Any mismatch stops before any root exists and before either protected
content open, consuming no read and no attempt.

## 4. Development population and closed/consumed-data rule (normative)

The three P18/P19 HOLD blocks (frames 1600..1983) SHALL NOT select K,
floor, order, decoder, disclosure step, or any successful point. No
tuning on them, no third factor after an inconclusive result.

The P20B VAL pool (frames 1200..1599, INCLUDING the declared-unused
remainder 1584..1599) is CONSUMED and SHALL NOT supply P20E blocks.
Cross-packet same-pool tuning is forbidden.

The P20C DEV blocks (frames 0..383) are CONSUMED and SHALL NOT supply
P20E blocks. Cross-packet same-block tuning is forbidden.

Stage B runs on the DECLARED new-block population (preregistered
enablement of P20C's never-used remainder):

| item | frozen value |
|---|---|
| source file identity | same registered paths as P18/P19/P20B/P20C (same NPZ + same pairs parquet + same manifest + same P16 construction; no new file, no new digest) |
| DEV frame range (enabled subrange) | 384..767 (same-file TRAIN range of the same 1M source) |
| DEV blocks (N=32768) | `384..511`, `512..639`, `640..767` (3 x 128 frames) |
| unused remainder | frames `768..1199`, 432 frames / 110592 pairs, recorded never used (counted, never decoded) |
| P20C-consumed range | 0..383 — disjoint by fail-closed gate (checked FIRST) |
| consumed range | 1200..1599 — disjoint by fail-closed gate (checked second) |
| closed range | 1600..1983 — disjoint by fail-closed gate (checked third) |
| block count | 3 at N=32768 (mirrors P18/P19/P20B/P20C cost class) |
| tag domains | new P20E domain below |

Evidence-reuse isolation (packet §4, restated for Pre-EXECUTE
adjudication): the Model-F prior is a FROZEN aggregate concentration
model, identical across arms, never refit or reselected on DEV; the
comparison is an INTER-ARM differential (base vs +1024 vs oracle) on
DEV-specific frames, not a prior effect; no K/floor/order/step selection
touches DEV, P20C-consumed, closed, or consumed ranges. If Pre-EXECUTE
rejects the isolation, Stage A substitutes a declared independent session
(or other registered split) with the same 3-block cost class — same
packet, new freeze values, re-review.

## 5. Preregistered disclosure cap (normative, carried over)

Cap rule: caps are CARRIED OVER unchanged from P20C (no growth, no
tuning) — preregistered per arm, frozen before Pre-EXECUTE, each FAR
below raw input bits with its ratio shown.

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

## 6. Arms (frozen; identical to P20C for comparability)

Run block-major (B0, B1, B2) per DEV block; checkpoint after every
(arm, block) record; 9 records total.

- `B0_sc_base`: frozen greedy SC at base disclosure/construction
  (operational; accepted `run_operational_block` called directly with
  k1=319/k2=6492; 2 SC + 1 P20E-domain tag per block).
- `B1_L2plus`: frozen greedy SC at base + the carried-over +1024 L2
  step via §2 order-prefix extension, all else identical (operational;
  the confirmation candidate; accepted `run_operational_block` called
  directly with k1=319/k2=7516 on the SAME frozen L2 order object; 2 SC +
  1 tag per block).
- `B2_true_l1_diagnostic`: true-L1-conditioned L2 at BASE disclosure
  (accepted `run_oracle_control_block` called directly with k2=6492 and a
  P20E-domain tag closure; provenance ORACLE, deployable=false, 1 SC +
  1 tag per block; excluded from every operational aggregate; never
  described as a correction result).

No other arms. Tag domain: master 2026092100, prefix
`nbpolar-p20e-plus1024-confirmation-seed`, seed string
`<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256,
MSB-first, truncated to `10*N+63 = 327743` bits). Prefix, master and arm
tokens differ from the P16, P17, P18, P19, P20B and P20C domains; raw
seed bits are never persisted.

## 7. Thresholds and labels (descriptive only)

Outcome label `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE`
iff ALL 20 integrity gates hold — regardless of exact-count. Any exact
count (including 0/9 and any partial outcome) is COMPLETE when integrity
holds. This packet makes NO recovery / FER / Wilson / superiority /
qualification / promotion claim. Confirmation reading is descriptive
only: "repeat recovery" = blocks where B0 fails and B1 is exact on the
NEW blocks (P20C analogue `b1_restored_count`), reported as a count with
per-block endpoint rows; "maintain" = B1 exact where B0 exact, reported
the same way. Either pattern (or its absence) counts as COMPLETE; the
positive/negative branch decision belongs to main-thread planning AFTER
acceptance, never to this packet's label. Status taxonomy frozen:
`exact` (tag-verified) vs `verify_failed`, with `undetected` isolated
(never success), plus `decode_failed` / `nonfinite` / `resource_abort`
via the P20A path.

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
  disclosure/construction tuning after preregistration. An execution
  error rerun is allowed only as a recorded repeat of the identical
  freeze, never as tuning.
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
  P20E plans the identical budget, strictly inside the same class).
- Strategy stop rules restated as binding: no tuning on closed blocks; no
  reuse of the consumed VAL pool or the consumed P20C DEV blocks; no
  third factor after an inconclusive single-factor result; no near-raw
  disclosure feasibility claim; no oracle-as-operational; no
  population-reliability inference before an independent-session gate; no
  efficiency tuning inside this confirmation packet.
- SCL entry gate UNCHANGED (all five strategy conditions must still be
  shown; this confirmation unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage B, frozen here)

- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P20E-PLUS1024-CONFIRMATION/plus1024_confirmation/`
  (exactly five files, created pre-open; per-(arm, block) checkpointing;
  one content open per protected input; no reopen/rerun). Root is ABSENT
  at Stage A close and must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`,
  `input_and_predecessor_identity.json`, `per_block_arm_outcomes.jsonl`
  (9 records at completion), `aggregate_summary.json`, `report.md`.
  Scalar-only: never counts, sampled symbols, truth vectors, decoded
  labels/keys, metric planes, raw rows, per-arm orders, tag seeds or RNG
  state.
- Accounting: key/public/tag disclosure + independent recount (mismatch
  0); SC-call counts (L1/L2 split) and tag-invocation counts exact;
  block SER/NLL; wall/RSS; `b1_restored_count` analogue recomputed
  descriptively (B0 fail→B1 exact on new blocks).
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `dev_split_manifest_identity`;
  `dev_block_range_identity` (TRIPLE overlap pre-check: consumed P20C DEV
  0..383 first, then consumed VAL 1200..1599, then closed HOLD
  1600..1983); `target_population_contract` (7/7 preconditions);
  `dev_population_exact` (384 frames / 98304 pairs / 256 rows per frame /
  pair indices / symbol range);
  `blocks_exact_with_declared_remainder` (three exact DEV ranges per arm
  in block-major slot order + never-used remainder 432 frames / 110592
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

Stage A (injected only; the authorized command for this stage):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_plus1024_confirmation.py \
  -q -p no:cacheprovider --basetemp=$PWD/workspace/p20e/<uuid>
```
using injected/synthetic inputs and a fresh additive temp root. Zero
protected opens (audit §11). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4
stays valid. (This checkout carries no `.venv`; the neighboring
`.venv` interpreter from the frozen Stage-B command family was used —
no install, no network, no repo write beyond the fresh temp root.)

Stage B execution command (NOT AUTHORIZED until independent Pre-EXECUTE
PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_confirmation --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --dev-frames 384 767 --block-frames 128 --remainder-frames 768 1199 --tag-master 2026092100 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20E-PLUS1024-CONFIRMATION/plus1024_confirmation
```
Sixteen flags, all required, no production default; three hardcoded arms
with the +1024 prefix-extension pinned (never CLI-tunable). byte-identical
to the module `FROZEN_COMMAND` (verified by import in this session).
Forbidden by default: `longrun_*`, `minrerun_*`, `routeA_*`,
`experiments/run_e2e_pipeline.py` on raw data, full sweeps.

Read-only verify: reviewer recomputes §9 identities from artifacts; never
`git show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Stage-A verification evidence (implementation time)

- Output root absent: the queue dir holds only `TASK_PACKET.md`,
  `STATUS.yaml`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `P20E_FREEZE.md`,
  `P20E_IMPLEMENTATION_NOTES.md`. `plus1024_confirmation/` does not
  exist.
- Zero protected content opens: module one-open guards
  `_NPZ_CONTENT_OPENED` / `_DEV_PARQUET_CONTENT_OPENED` are False at
  close; no NPZ/parquet stat or open was performed in this stage (only
  JSON provenance reads: P16 construction file + split manifest, per
  P18/P19/P20B/P20C Stage-A precedent).
- P16 digest recomputed in this session: `055c90...c3faea1b`, equal to
  the stored freeze digest and the frozen flag; P16 root untouched.
- Manifest verified in this session: schema + 1M TRAIN 1200/307200 +
  VAL 400/102400 + HOLD 400/102400 (see §3); TRAIN 0..1199 by
  elimination with accepted VAL/HOLD ranges; the P20E DEV subrange
  384..767 sits inside TRAIN, fail-closed in the runner.
- Fresh focused-test seeds 2026092101..2107 and frozen tag master
  2026092100 appear in NO tracked file (`git grep` empty — same bar as
  P20C); untracked hits are exactly the new P20E runner, tests, spec
  delta, packet docs and this freeze (plus git-ignored `__pycache__`
  bytecode from the test runs).
- Focused suite `test_nbpolar_plus1024_confirmation.py`: 36/36 green
  (fresh temp basetemp, pinned interpreter, `-p no:cacheprovider`).
- Packet-scoped predecessor suites: `test_nbpolar_l2_disclosure_backoff.py`
  (34) + `test_nbpolar_bounded_search_diagnostic.py` (34) +
  `test_nbpolar_operational_f13.py` (29) +
  `test_nbpolar_operational_f13_replication.py` (25) +
  `test_nbpolar_holdout_microcheck.py` (26) +
  `test_nbpolar_holdout_backoff_diagnostic.py` (33): 181/181 green (same
  settings, fresh basetemp). No shared predecessor code was changed, so
  the full NB-Polar suite was not run (recorded in the notes).
- No commit (no commit/push authorized in Stage A).

## 12. Forbidden paths and scope boundary (Stage A observed)

Forbidden and not done: Model-F artifact reads, protected
TRAIN/HOLD/VAL/EVAL/raw reads/stats/opens, other N in the frozen run,
any added/changed arm, any construction path, BEC, transform/belief/list
decoders, a second tag outside the registered arms, fitting/sampling on
DEV, any use of the remainder/closed/consumed frames, a second
disclosure step (`B1b`), an alternative-construction second factor,
production benchmark, `results/` or `comparison_bench/outputs_comparison/`
writes, P12-P20C code or old-root modification, official prior/probe seed
reuse, commit/push. Scope is implementation + frozen planning artifacts
for a descriptive zero-tuning confirmation diagnostic on new blocks; it is
not real-frame FER, reconciliation efficiency, leakage, key rate, scaling,
qualification or promotion evidence, and B2 is never operational.
