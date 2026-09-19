# P20B freeze — N=32768 VAL bounded-search diagnostic (Stage A implementation)

Packet: `NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC` (`TASK_PACKET.md`, 225
lines, frozen). Predecessors: P19
`TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE_ACCEPTED_DESCRIPTIVE`
+ P20A `IMPLEMENTATION_ACCEPTED` (resource passthrough + endpoint
instrumentation). Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` (next scientific question,
options 1-3; closed-blocks rule; SCL entry gate; stop rules). Tier-Y
decision-gate packet: Stage A (this document + implementation + tests) is
authorized separately from Stage B (single authorized execution).

This document authorizes nothing. No box in `tasks.md` is checked by the
implementing session. Stage B additionally needs an independent Pre-EXECUTE
PASS plus a separate pasted Stage-B authorization.

## 1. Mission (one frozen diagnostic question, one factor)

> With true L1 fixed for diagnosis and prior / construction / disclosure /
> floor / order / kernel / representation / SC decoder all frozen, does a
> preregistered bounded search find a present complete-block candidate that
> greedy SC misses — or does the bounded negative hold?

Strategy option 3. Options 1 (L2 disclosure backoff, P20C candidate) and 2
(alternative L2 construction, P20D candidate) are deferred and must not
enter this packet. Found-count 0 and found-count >0 are both descriptive
COMPLETE when integrity holds; neither promotes any block, session, or
route.

## 2. Single-factor freeze (normative)

FROZEN identical for every arm (any deviation is a packet violation):

- Prior: frozen Model-F concentration prior path (`target_preconditions`
  + `derive_p1`/`derive_p2`, accepted P7 rule) with fixed `1e-15` floor
  applied before SC. Raw zero-count hits, floor hits and their log loss
  are diagnosed per selected candidate, never retuned.
- Construction: accepted P16 order, K1=319 / K2=6492 (base), N=32768.
- Disclosure: frozen base K sets (no +128 L1, no +512 L2, no incremental
  schedule).
- Kernel / representation / transform / SC arithmetic: unchanged; greedy
  SC is the baseline arm; no SCL, no new kernel/model/schema.
- Verification: one final 64-bit Toeplitz tag per block/record under new
  P20B tag domains; verification never selects a candidate.

VARIED (the single factor), frozen here and never changed afterwards:

- Search bound M=8 (max candidates rescored, greedy included).
- Neighborhood `P20B-NBHD-1`: greedy hard path plus single-symbol U-domain
  divergent alternates at undisclosed coordinates only (frozen/disclosed
  positions never varied), ranked by ascending SC margin gap (best minus
  runner-up, ln units), deterministic tie-break (layer L1 < L2, coordinate
  ascending); each alternate re-encoded with the frozen transform;
  rescore-only (no extra SC calls, L2 never re-decoded under L1
  alternates).
- Scoring: ONE coherent probability model — argmin total NLL bits under
  the same floored p1/p2 tables as SC (greedy wins ties); no tag-guided
  candidate selection, no evidence reuse, no truth in selection.
- True-L1-fixed diagnosis (S2) is recorded for attribution only
  (provenance ORACLE, deployable=false); it changes no operational
  disclosure or construction.

## 3. Fixed identities (verified in this session before any protected open)

P16 accepted file
`.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json`
(JSON read only; P16 immutable, never modified):

| item | verified value |
|---|---|
| protocol | `nbpolar-p16-operational-f13-gate`, frozen before first DEV |
| N / K_total / K1 / K2 | 32768 / 6811 / 319 / 6492 |
| L1/L2 orders | valid permutations of length 32768 |
| canonical digest (recomputed here) | `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` |
| stored digest / frozen flag | identical (match) |
| K replay | `floor((1.3*32768*H-64)/5) = 6811`, `319+6492 = 6811` |
| leakage / f | `5*6811+64 = 34119`, `f = 1.2998502888 <= 1.3` |

Split manifest
`comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`
(JSON read only):

| item | verified value |
|---|---|
| schema | `nbldpc_v25_split_manifest_v1` |
| 1M source tag | `type2_1M_20260121_184040` |
| HOLD frames / pairs | 400 / 102400 (frozen requirement, unchanged) |
| VAL frames / pairs | 400 / 102400 (development pool host) |
| TRAIN frames / pairs | 1200 / 307200 (prior counts source, unchanged) |

Any mismatch stops before any root exists and before either protected
content open, consuming no read and no attempt.

## 4. Development population and closed-data rule (normative)

The three P18/P19 HOLD blocks (frames 1600..1983) SHALL NOT select K,
floor, order, decoder, search bound/neighborhood, or any successful
point. No tuning on them, no third factor after an inconclusive result.

Stage B runs on the DECLARED independent real development population:

| item | frozen value |
|---|---|
| source file identity | same registered paths as P18/P19 (same NPZ + same pairs parquet + same manifest + same P16 construction; no new file, no new digest) |
| DEV frame range | 1200..1599 (VAL split of the same 1M source) |
| DEV blocks (N=32768) | `1200..1327`, `1328..1455`, `1456..1583` (3 x 128 frames) |
| unused remainder | frames `1584..1599`, 4096 pairs, recorded never used |
| closed range | 1600..1983 — disjoint by fail-closed gate (`dev_block_range_identity` checks overlap first, then literals) |
| block count | 3 at N=32768 (mirrors P18/P19 cost class) |
| tag domains | new P20B domain below |

Rationale (replacement with equivalent, packet §4): only 16 HOLD frames
(1984..1999, 4096 pairs) remain outside the closed range in the same
file — arithmetically insufficient for even one N=32768 block — so the
packet-recommended "later HOLD frames" pool cannot supply the mirrored
cost class. The VAL pool (400 frames / 102400 pairs per the verified
manifest; the file holds all 2000 frames per the 512000-row inventory:
1200 TRAIN + 400 VAL + 400 HOLD) keeps the source, channel, file
identity, block geometry (3x128 + 16-frame remainder) and cost class
fixed while changing only disjoint frames. Confirmation on new
blocks/sessions is a later packet, never this one.

## 5. Preregistered disclosure cap (normative)

Cap rule: NO increase over the frozen base construction at the same N.

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| S0_sc_base (operational) | 319 | 6492 | 34119 = 5*6811+64 | 327743 = 10*32768+63 |
| S1_bounded_search (operational) | 319 | 6492 | 34119 (identical; rescore-only adds no disclosure) | 327743 |
| S2_true_l1_diagnostic (oracle) | 0 | 6492 | 32524 = 5*6492+64 | 327743 |

Planned totals if all invoked: 302286 key-dependent bits
(6x34119 + 3x32524) and 2949687 public-control bits (9x327743).

Meaningfulness bar: cap per operational block 34119 sits at
34119/327680 = 0.10412292 (~10.41%) of raw input bits (10*N per block at
N=32768) — well below raw. Sample-CE-normalized ratios
(`disclosure_ce_ratio`) are reported descriptively and are NOT
qualification efficiency.

Recount rule: independent key/public/tag recount from canonical
transcript events; mismatch 0, or the gate BLOCKS.

## 6. Arms (frozen; differ ONLY in search)

Run block-major (S0, S1, S2) per DEV block; checkpoint after every
(arm, block) record; 9 records total.

- `S0_sc_base`: frozen greedy SC at base disclosure/construction
  (operational; accepted `run_operational_block` called directly; 2 SC +
  1 P20B-domain tag per block).
- `S1_bounded_search`: §2 bounded search at identical
  disclosure/construction/prior (operational; frozen greedy prefix + ≤M
  NLL rescores + exactly one final P20B-domain tag; 2 SC + 1 tag per
  block; the single-factor delta).
- `S2_true_l1_diagnostic`: true-L1-conditioned L2 (accepted
  `run_oracle_control_block` called directly with a P20B-domain tag
  closure; provenance ORACLE, deployable=false, 1 SC + 1 tag per block;
  excluded from every operational aggregate; never described as a
  correction result).

No other arms. Tag domain: master 2026092080, prefix
`nbpolar-p20b-bounded-search-diagnostic-seed`, seed string
`<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256,
MSB-first, truncated to `10*N+63 = 327743` bits). Prefix and arm tokens
differ from the P16, P17, P18 and P19 domains; raw seed bits are never
persisted.

## 7. Thresholds and labels (descriptive only)

Outcome label `TARGET_EMPIRICAL_N32768_DEV_BOUNDED_SEARCH_COMPLETE` iff
ALL 20 integrity gates hold — regardless of found-count. This packet
makes NO recovery / FER / Wilson / superiority / qualification /
promotion claim. Status taxonomy frozen: `exact` (tag-verified) vs
`verify_failed`, with `undetected` isolated (never success), plus
`decode_failed` / `nonfinite` / `resource_abort` via the P20A path.

Per-record separation (P20A endpoints): `l1_exact`, `hard_l2_exact`,
`oracle_l2_exact`, `pair_exact`, `exact`, first error coordinate +
layer, raw zero-count hits, `1e-15` floor hits + log loss,
candidate-H-conditioned vs true-H-conditioned L2 NLL, outcome taxonomy,
plus S1 search fields (`rescores_used` 1..8, `selected_source`,
`search_found_better`, NLL improvement).

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until
  authorized execution; no rerun, no seed change, no bound/neighborhood
  tuning after preregistration. An execution-error rerun is allowed only
  as a recorded repeat of the identical freeze, never as tuning.
- SC/tag budget: 15 SC calls (3 blocks x (2+2+1)) and 9 tags; derived
  per-record recomputation (`1+l2_invoked` operational, `l2_invoked`
  control) must equal the counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative (`MemoryError` re-raised
  at both S1 SC sites; accepted helpers unchanged); abort preserves
  evidence + call/disclosure accounting; abort is BLOCKED, never success.
- Wall/RSS ceilings: 600 s external timeout, 2 GiB virtual limit
  (`ulimit -v 2097152`), 2 GiB RSS cap, single-thread BLAS/OpenMP +
  `MALLOC_ARENA_MAX=2` — the P19 class (P19 reference: ~186 s wall,
  ~616 MB RSS peak for 27 SC / 15 tags at N=32768; P20B plans 15 SC /
  9 tags plus ≤7 cheap NLL rescores per S1 block, strictly inside the
  class).
- Strategy stop rules restated as binding: no tuning on closed blocks; no
  third factor after an inconclusive single-factor result; no near-raw
  disclosure feasibility claim; no oracle-as-operational; no
  population-reliability inference before an independent-session gate; if
  the frozen cap cannot recover independent development blocks, record
  the bounded negative and revisit L2 model/representation before raising
  N or list width.
- SCL entry gate UNCHANGED (all five strategy conditions must still be
  shown; this diagnostic informs conditions 1-3 but unlocks nothing by
  itself).

## 9. Evidence matrix and accounting (Stage B, frozen here)

- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/bounded_search_diagnostic/`
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
  0); SC-call counts (L1/L2 split; search rescores are NLL evaluations,
  not SC calls) and tag-invocation counts exact; block SER/NLL; wall/RSS.
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`; `dev_split_manifest_identity`;
  `dev_block_range_identity`; `target_population_contract` (7/7
  preconditions); `dev_population_exact` (400 frames / 102400 pairs / 256
  rows per frame / pair indices / symbol range);
  `blocks_exact_with_declared_remainder` (three exact DEV ranges per arm
  in block-major slot order + unused remainder 4096 pairs);
  `nine_records_exact`; `sc_calls_exact` (derived 15);
  `tags_exact` (derived 9);
  `orders_valid_k_prefixes_within_registered_arms`;
  `oracle_isolation`; `buckets_disjoint_exhaustive` (unique arm/block +
  schema); `undetected_zero`; `nonfinite_zero`; `truth_isolation`;
  `disclosure_recount_exact`; `one_open_per_protected_input`;
  `input_stat_unchanged`; `no_unregistered_access`;
  `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen here)

Stage A (injected only; the authorized command for this stage):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_bounded_search_diagnostic.py \
  -q -p no:cacheprovider --basetemp=/tmp/p20b-<uuid>
```
using injected/synthetic inputs and a fresh additive temp root. Zero
protected opens (audit §12). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4
stays valid.

Stage B execution command (NOT AUTHORIZED until independent Pre-EXECUTE
PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.bounded_search_diagnostic --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --dev-frames 1200 1599 --block-frames 128 --remainder-frames 1584 1599 --tag-master 2026092080 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/bounded_search_diagnostic
```
Sixteen flags, all required, no production default; three hardcoded arms,
not CLI-tunable (`bound` is pinned to M=8 by fail-closed refusal).
Forbidden by default: `longrun_*`, `minrerun_*`, `routeA_*`,
`experiments/run_e2e_pipeline.py` on raw data, full sweeps.

Read-only verify: reviewer recomputes §9 identities from artifacts; never
`git show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Stage-A verification evidence (implementation time)

- Output root absent: the queue dir holds only `TASK_PACKET.md`,
  `STATUS.yaml`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `P20B_FREEZE.md`,
  `P20B_IMPLEMENTATION_NOTES.md`. `bounded_search_diagnostic/` does not
  exist.
- Zero protected content opens: module one-open guards
  `_NPZ_CONTENT_OPENED` / `_DEV_PARQUET_CONTENT_OPENED` are False at
  close; no NPZ/parquet stat or open was performed in this stage (only
  JSON provenance reads: P16 construction file + split manifest, per
  P18/P19 Stage-A precedent).
- P16 digest recomputed in this session: `055c90...c3faea1b`, equal to
  the stored freeze digest and the frozen flag; P16 root untouched.
- Manifest verified in this session: schema + 1M HOLD 400/102400 +
  VAL 400/102400 (see §3).
- Fresh focused-test seeds 2026092081..087 appear in no tracked file
  outside the P20B test file; frozen tag master 2026092080 appears in no
  tracked `.py`/test outside the P20B runner, tests, packet, spec and
  queue documents.
- Focused suite `test_nbpolar_bounded_search_diagnostic.py`: 34/34 green
  (fresh temp basetemp, pinned interpreter, `-p no:cacheprovider`).
- Packet-scoped predecessor suites: `test_nbpolar_operational_f13.py` +
  `test_nbpolar_operational_f13_replication.py` +
  `test_nbpolar_holdout_microcheck.py` +
  `test_nbpolar_holdout_backoff_diagnostic.py`: 113/113 green (same
  settings). No shared predecessor code was changed, so the full
  NB-Polar suite was not run (recorded in the notes).
- No commit (no commit/push authorized in Stage A).

## 12. Forbidden paths and scope boundary (Stage A observed)

Forbidden and not done: Model-F artifact reads, protected
TRAIN/HOLD/VAL/EVAL/raw reads/stats/opens, other N in the frozen run,
any added/changed arm, any construction path, BEC, transform/belief/list
decoders, a second tag outside the registered arms, fitting/sampling on
DEV, any use of the remainder or closed frames, production benchmark,
`results/` or `comparison_bench/outputs_comparison/` writes, P12-P20A
code or old-root modification, official prior/probe seed reuse,
commit/push. Scope is implementation + frozen planning artifacts for a
descriptive single-factor development diagnostic; it is not real-frame
FER, reconciliation efficiency, leakage, key rate, scaling,
qualification or promotion evidence, and S2 is never operational.
