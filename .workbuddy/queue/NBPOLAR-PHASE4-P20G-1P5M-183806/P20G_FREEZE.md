# P20G freeze — N=32768 +1024 independent-session confirmation on type2_1p5M_20260121_183806 (Stage A implementation)

Packet: `NBPOLAR-PHASE4-P20G-1P5M-183806` (`TASK_PACKET.md`, 411
lines, frozen). Predecessor: P20F
`TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE_ACCEPTED_DESCRIPTIVE`
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

## 1. Mission (one frozen independent-session question, zero tuning)

> With construction / disclosure / order / prior / floor / kernel /
> representation / SC all carried over byte-identical from P20C/P20E/P20F
> (K1=319, K2 base 6492 / B1 7516 via frozen order-prefix extension,
> floor 1e-15, N=32768, new P20G tag domains only), zero tuning, does
> +1024 maintain exact on three new independent-session blocks — and
> does a P20C-style restoration event (B0 fail → B1 exact) replicate on
> genuinely new data, or not?

Same-file TRAIN is geometrically exhausted (P20C 0..383 + P20E 384..767
+ P20F 768..1151 = all 1152 usable TRAIN frames of the 1M file;
remainder 1152..1199 is 48 frames < one 128-frame N=32768 block). P20E
and P20F both held maintain-exact with the restoration-event
denominator at 0 — neither replicated nor falsified. This packet asks
only whether the maintain pattern holds on an independent session, and
whether any restoration opportunity appears. The positive
(efficiency-optimization) / negative (P20D candidate) / maintain
(reserved-2M vs minimality-probe) branch decision belongs to
main-thread planning AFTER acceptance, never to this packet's label.

## 2. Zero-tuning freeze (normative)

FROZEN identical for every arm (any deviation is a packet violation):

- Prior: frozen Model-F concentration prior path (`target_preconditions`
  + `derive_p1`/`derive_p2`, accepted P7 rule) with fixed `1e-15` floor
  applied before SC. Raw zero-count hits, floor hits and their log loss
  are diagnosed per selected candidate, never retuned, never refit on
  the new session. Cross-session applicability is a STATED
  TO-BE-VERIFIED ASSUMPTION adjudicated at Pre-EXECUTE — never a
  finding of this packet; per-session refit is NOT a fallback (it would
  be tuning).
- Construction order: accepted P16 order, K1=319 base L1 set unchanged on
  every arm (permutation fixed by the accepted construction file; digest
  pinned in §3).
- Carried-over +1024 step: `B1` discloses ΔK2 = +1024 L2 symbols beyond
  the frozen base (K2 6492 → 7516; K_total 6811 → 7835) by
  FROZEN-ORDER-PREFIX EXTENSION — the disclosed L2 set is the first 7516
  positions of the frozen P16 L2 order. Positions are fixed by the
  construction file, never selected on closed blocks, the consumed 1M
  pool, the reserved 2M file, or the new DEV data. No second step
  (`B1b`) without a new packet and a written necessity argument.
- Disclosure base: K2=6492 (B0, B2); kernel / representation / transform /
  SC arithmetic: unchanged; greedy SC is the baseline; no SCL, no new
  kernel/model/schema.
- Verification: one final 64-bit Toeplitz tag per block/record under new
  P20G tag domains (§6); verification never selects a candidate.

VARIED: NOTHING. The only deliberate differences from P20C/P20E/P20F are
the new-session population (§4) and the new tag domain (§6) — both
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
| 1.5M source tag | `type2_1p5M_20260121_183806` |
| TRAIN frames / pairs | 1660 / 424960 (new-session DEV host) |
| VAL frames / pairs | 553 / 141568 (intra-file gate, never selected) |
| HOLD frames / pairs | 554 / 141824 (intra-file gate, never selected) |

Build manifest
`comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/build_manifest.json`
(JSON read only): 1.5M pairs size 1869178 B, sha
`ca351e5205e76600530121066af4e0e1e5278061745c0797368a49443570a06b`
(same v13r3fresh pipeline as 1M: point 1024,200; factor 1; nearest
pairing; legacy_v1; 256 rows/frame throughout — 1660×256=424960,
553×256=141568, 554×256=141824, all exact).

TRAIN base provenance (Stage-A written equivalent with justification;
the manifest gives counts only, never frame numbering): the frozen
split code assigns TRAIN as the first 60% of time-ordered unique
frame_ids (`np.unique` sorted, `split_by_frame` in the accepted
`nonbinary_v25_gate.py`); the accepted 1M layout is 0-based contiguous
(TRAIN 0..1199 by elimination with accepted VAL 1200..1599 and HOLD
1600..1999); the 1.5M file uses the identical pipeline at 256
rows/frame with total 2767 frames (1660+553+554; parquet_rows 708352 =
2767×256 per the accepted data inventory). THEREFORE the frozen TRAIN
base is 0: DEV 0..383 (first 384 TRAIN frames), remainder 384..1659
(1276 frames / 326656 pairs), VAL 1660..2212, HOLD 2213..2766. The
runner fail-closes on any layout drift (`dev_population_exact` requires
exactly frames 0..383 with 256 rows each; the double gate §4 refuses
first), so a wrong base BLOCKS before any SC call instead of
misattributing. Pre-EXECUTE owns the cross-session isolation
adjudication (§4).

Any mismatch stops before any root exists and before either protected
content open, consuming no read and no attempt.

## 4. Development population and closed/consumed-data rule (normative)

The three P18/P19 HOLD blocks (1M frames 1600..1983) SHALL NOT select K,
floor, order, decoder, disclosure step, or any successful point. No
tuning on them, no third factor after an inconclusive result.

The P20B VAL pool (1M frames 1200..1599), the P20C DEV blocks (1M
0..383), the P20E DEV blocks (1M 384..767) and the P20F DEV blocks (1M
768..1151, remainder 1152..1199 never used) are CONSUMED and SHALL NOT
supply P20G blocks. The ENTIRE 1M pool (TRAIN 0..1199 / VAL 1200..1599 /
HOLD 1600..1999) is fail-closed against P20G DEV selection by the
cross-file gate below. Cross-packet same-block tuning is forbidden.

The 2M session file (`type2_2M_20260121_183657/pairs.parquet`) is
RESERVED and SHALL NOT be opened, statted, or read under this packet.
It is not consumed.

Stage B runs on the DECLARED new-session population:

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin from the build manifest; any mismatch blocks) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 |
| DEV frame rule | FIRST 384 TRAIN frames of the 1.5M file in (frame_id, pair_idx) order → frozen TRAIN base 0: `0..383` |
| DEV blocks (N=32768) | `0..127`, `128..255`, `256..383` (3 x 128 frames) |
| unused remainder | frames `384..1659`, 1276 frames / 326656 pairs, recorded never used (counted, never decoded) |
| intra-file VAL | 1660..2212 — disjoint by fail-closed gate (checked second, VAL first) |
| intra-file HOLD | 2213..2766 — disjoint by fail-closed gate (checked second, HOLD second) |
| 1M full pool | excluded by the cross-file gate (checked FIRST) |
| reserved 2M file | excluded by the cross-file gate (checked FIRST); never touched |
| block count | 3 at N=32768 (mirrors P18/P19/P20B/P20C/P20E/P20F cost class) |
| tag domains | new P20G domain below |

Evidence-reuse isolation (packet §4, restated for Pre-EXECUTE
adjudication): the Model-F prior is a FROZEN aggregate concentration
model, identical across arms, never refit or reselected on the new
session; the comparison is an INTER-ARM differential (base vs +1024 vs
oracle) on new-session frames, not a prior effect; no
K/floor/order/step selection touches the new DEV, the 1M
consumed/closed ranges, or the reserved 2M file. If Pre-EXECUTE rejects
the cross-session isolation, Stage B is BLOCKED and the packet returns
to the planner — per-session refit is NOT a fallback (it would be
tuning).

Fail-closed double gate (frozen in the runner, checked first, in this
order): (a) CROSS-FILE gate — the DEV content-open path must equal the
frozen 1.5M pairs path and its stat size must equal 1869178 B (sha
`ca351e52…a06b` recorded as the frozen provenance pin in the plan and
identity docs); the 1M full-pool path and the reserved 2M path refuse
with their own messages, any other path refuses as well — bare frame
integers collide across files, so source-tag + digest pin is the
identity, never frame numbers alone; (b) INTRA-FILE gate — DEV ranges
must overlap NONE of the 1.5M VAL/HOLD frame sets, else the run refuses
before any protected content open. Gate order (a)→(b) is frozen; within
(b), VAL is checked before HOLD.

## 5. Preregistered disclosure cap (normative, carried over)

Cap rule: caps are CARRIED OVER unchanged from P20C/P20E/P20F (no
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

## 6. Arms (frozen; identical to P20C/P20E/P20F for comparability)

Run block-major (B0, B1, B2) per DEV block; checkpoint after every
(arm, block) record; 9 records total.

- `B0_sc_base`: frozen greedy SC at base disclosure/construction
  (operational; accepted `run_operational_block` called directly with
  k1=319/k2=6492; 2 SC + 1 P20G-domain tag per block).
- `B1_L2plus`: frozen greedy SC at base + the carried-over +1024 L2
  step via §2 order-prefix extension, all else identical (operational;
  the confirmation candidate; accepted `run_operational_block` called
  directly with k1=319/k2=7516 on the SAME frozen L2 order object; 2 SC +
  1 tag per block).
- `B2_true_l1_diagnostic`: true-L1-conditioned L2 at BASE disclosure
  (accepted `run_oracle_control_block` called directly with k2=6492 and a
  P20G-domain tag closure; provenance ORACLE, deployable=false, 1 SC +
  1 tag per block; excluded from every operational aggregate; never
  described as a correction result).

No other arms. Tag domain: master 2026092210, prefix
`nbpolar-p20g-independent-session-seed`, seed string
`<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256,
MSB-first, truncated to `10*N+63 = 327743` bits). Prefix, master and arm
tokens differ from the P16, P17, P18, P19, P20B, P20C, P20E and P20F
domains; raw seed bits are never persisted.

## 7. Thresholds and labels (descriptive only)

Outcome label
`TARGET_EMPIRICAL_N32768_DEV_PLUS1024_INDEPENDENT_SESSION_COMPLETE`
iff ALL 20 integrity gates hold — regardless of exact-count. Any exact
count (including 0/9 and any partial outcome) is COMPLETE when integrity
holds. This packet makes NO recovery / FER / Wilson / superiority /
qualification / promotion claim. Confirmation reading is descriptive
only: "repeat recovery" = blocks where B0 fails and B1 is exact on the
NEW-session blocks (P20C analogue `b1_restored_count`), reported as a
count with per-block endpoint rows; "maintain" = B1 exact where B0
exact, reported the same way. Either pattern (or its absence) counts as
COMPLETE; the positive/negative branch decision belongs to main-thread
planning AFTER acceptance, never to this packet's label. Status
taxonomy frozen: `exact` (tag-verified) vs `verify_failed`, with
`undetected` isolated (never success), plus `decode_failed` /
`nonfinite` / `resource_abort` via the P20A path.

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
  P20E observed ~100.1 s / ~554 MB; P20F observed ~93.0 s / ~553 MB at
  the identical budget; P20G plans the identical 15 SC / 9-tag budget,
  strictly inside the same class).
- Strategy stop rules restated as binding: no tuning on closed blocks; no
  reuse of the consumed 1M pool (any split, any subrange) or the
  reserved 2M file; no third factor after an inconclusive single-factor
  result; no near-raw disclosure feasibility claim; no
  oracle-as-operational; no population-reliability inference from this
  single gate alone (one independent session is necessary but not
  sufficient for a reliability claim); no efficiency tuning inside this
  confirmation packet.
- SCL entry gate UNCHANGED (all five strategy conditions must still be
  shown; this confirmation unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage B, frozen here)

- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/independent_session/`
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
  `dev_block_range_identity` (DOUBLE gate: cross-file source-tag+digest
  pin first, then intra-file DEV-vs-VAL/HOLD overlap with VAL first);
  `target_population_contract` (7/7 preconditions);
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

Stage A (injected only; the authorized command for this stage):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_plus1024_independent_session.py \
  -q -p no:cacheprovider --basetemp=$PWD/workspace/p20g/<uuid>
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
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_independent_session --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 0 383 --block-frames 128 --remainder-frames 384 1659 --tag-master 2026092210 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/independent_session
```
Sixteen flags, all required, no production default; three hardcoded arms
with the +1024 prefix-extension pinned (never CLI-tunable). Verbatim
the packet §10 recommended command with the Stage-A-frozen
`--dev-frames 0 383` / `--remainder-frames 384 1659` integers; the
`--source 1p5M` vocabulary admits only `1p5M`. Forbidden by default:
`longrun_*`, `minrerun_*`, `routeA_*`,
`experiments/run_e2e_pipeline.py` on raw data, full sweeps.

Read-only verify: reviewer recomputes §9 identities from artifacts; never
`git show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Stage-A verification evidence (implementation time)

- Output root absent: the queue dir holds only `TASK_PACKET.md`,
  `STATUS.yaml`, `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `P20G_FREEZE.md`,
  `P20G_IMPLEMENTATION_NOTES.md`. `independent_session/` does not
  exist.
- Zero protected content opens: module one-open guards
  `_NPZ_CONTENT_OPENED` / `_DEV_PARQUET_CONTENT_OPENED` are False at
  close; no NPZ/parquet stat or open was performed in this stage (only
  JSON provenance reads: P16 construction file + split manifest + build
  manifest, per P18/P19/P20B/P20C/P20E/P20F Stage-A precedent). The 2M
  file was never opened, statted, or read — not even a directory
  listing of its folder; the 2M refusal path in the runner is a string
  literal only.
- P16 digest recomputed in this session: `055c90...c3faea1b`, equal to
  the stored freeze digest and the frozen flag; P16 root untouched.
- Manifest verified in this session: schema + 1.5M TRAIN 1660/424960 +
  VAL 553/141568 + HOLD 554/141824 (see §3); 256 rows/frame exact
  throughout; TRAIN base 0 by the §3 written equivalent; the P20G DEV
  prefix 0..383 sits inside TRAIN, fail-closed in the runner.
- Build-manifest file pins verified in this session: 1.5M pairs size
  1869178 B / sha `ca351e52…a06b` (see §3); the runner enforces the
  path string + stat size pre-open and records the sha as the frozen
  provenance pin.
- Fresh focused-test seeds 2026092211..2217 and frozen tag master
  2026092210 appear in NO tracked file (`git grep` empty — same bar as
  P20C/P20E/P20F); untracked hits are exactly the new P20G runner,
  tests, spec delta, packet docs and this freeze (plus git-ignored
  `__pycache__` bytecode from the test runs).
- Focused suite `test_nbpolar_plus1024_independent_session.py`: 36/36
  green (fresh temp basetemp, pinned interpreter, `-p
  no:cacheprovider`).
- Packet-scoped predecessor suites: `test_nbpolar_plus1024_extension.py`
  (36) + `test_nbpolar_plus1024_confirmation.py` (36) +
  `test_nbpolar_l2_disclosure_backoff.py` (34) +
  `test_nbpolar_bounded_search_diagnostic.py` (34) +
  `test_nbpolar_operational_f13.py` (29) +
  `test_nbpolar_operational_f13_replication.py` (25) +
  `test_nbpolar_holdout_microcheck.py` (26) +
  `test_nbpolar_holdout_backoff_diagnostic.py` (33): green (same
  settings, fresh basetemp; real counts reported in the notes).
  No shared predecessor code was changed, so the full NB-Polar suite was
  not run (recorded in the notes).
- No commit (no commit/push authorized in Stage A).

## 12. Forbidden paths and scope boundary (Stage A observed)

Forbidden and not done: Model-F artifact reads, protected
TRAIN/HOLD/VAL/EVAL/raw reads/stats/opens, the 2M file in any form,
other N in the frozen run, any added/changed arm, any construction
path, BEC, transform/belief/list decoders, a second tag outside the
registered arms, fitting/sampling on DEV, any use of the remainder/1M
consumed/closed frames or the reserved 2M file, a second disclosure
step (`B1b`), an alternative-construction second factor, per-session
prior refit, production benchmark, `results/` or
`comparison_bench/outputs_comparison/` writes, P12-P20F code or
old-root modification, official prior/probe seed reuse, commit/push.
Scope is implementation + frozen planning artifacts for a descriptive
zero-tuning independent-session diagnostic on new blocks; it is not
real-frame FER, reconciliation efficiency, leakage, key rate, scaling,
qualification or promotion evidence, and B2 is never operational.
