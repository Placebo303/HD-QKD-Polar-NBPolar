# P20I freeze — L1-disclosure +128 single-factor on type2_1p5M_20260121_183806 (Stage A implementation)

Packet: `NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M` (`TASK_PACKET.md`, 466
lines, frozen). Predecessor: P20H terminal
`TARGET_EMPIRICAL_N32768_DEV_PLUS1024_PER_SESSION_CALIBRATION_COMPLETE_ACCEPTED_DESCRIPTIVE`
(Stage-B single attempt SPENT 1/1; DEV 1/1 SPENT on 1.5M TRAIN 0..383;
9/9 records; 21/21 gates PASS; B0 0/3 verify_failed + B1 0/3
verify_failed + b1_restored 0/3, first errors 16/L1 + 6/L1 + 8/L1 at
raw SER 0.2563/0.2541/0.2551; B2 oracle 3/3 exact isolated; undetected
0; SC 15/15; tags 9/9; recount 0; 2M pristine by non-access) + P20A
`IMPLEMENTATION_ACCEPTED` (resource passthrough + endpoint
instrumentation). P19 precedent: `l1_plus` +128 L1 (K1 319→447,
leakage 34759) repaired the two L1 errors on the same three HOLD
blocks (base L1 true/false/false → l1_plus true/true/true). Strategy
parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2
(reproducible reliability: confirmation on new blocks/sessions; stop
rules). Tier-Y decision-gate packet: Stage A (this document +
implementation + tests + OpenSpec delta) is authorized separately from
Stage B (single authorized execution).

This document authorizes nothing. No box in `tasks.md` is checked by
the implementing session. Stage B additionally needs an independent
Pre-EXECUTE PASS (explicitly adjudicating the §3 prior-reuse pins and
the §4 quadruple gate) plus a separate pasted Stage-B authorization.

## 1. Mission (one frozen L1-disclosure question, zero further tuning)

> With ONE preregistered change against P20H — L1 disclosure +ΔK1=128
> via the frozen order-prefix rule (Stage-A frozen, Stage-B
> read-only) — and everything else carried over from P20H
> (per-session prior digest-pinned read-only, K2 base 6492, floor
> 1e-15, N=32768, greedy SC only, new P20I tag domains only), zero
> further tuning, does +128 L1 restore any complete operational block
> on three NEW 1.5M TRAIN blocks (384..767) — and where does the first
> error move when L1 disclosure grows while L2 disclosure stays at
> base?

P20H DEV 0..383 is CONSUMED (9 records, DEV 1/1 + attempt 1/1 SPENT)
and SHALL NOT supply P20I blocks. All branches after this packet are
deferred to §16 of the packet and must not be prejudged here.

## 2. Prior-reuse freeze (normative — zero new calibration)

FROZEN prior = the P20H Stage-A product read-only (no refit, no
resmoothing, no relambda, no floor change):
`.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz`
(keys exactly `counts_ab`, `f_prior`, `p1`, `p2`, `p_b`,
`lambda_star`, `floor_value`, `h1`, `h2`, `h_total`):

- canonical digest (recomputed in this session via the frozen
  `canonical_prior_digest`, worktree-file read only; never a counts
  open):
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
  (match);
- lambda pin `137.3823795883264` (equals the calibration-module pin;
  accepted fitting-program constant procedure output) (match);
- floor pin `1e-15` (match);
- recalibrated literals H1 `2.006647056368773` / H2
  `1.9017235959286112` / TOTAL `3.908370652297384` (match; sum within
  1e-12).

Stage B loads the frozen file read-only behind the
calibration-identity digest gate (digest equality + lambda/floor pins
+ exact key set + recomputed H1/H2/TOTAL within 1e-12 of the
literals, or BLOCKED before any SC call). The V25 counts NPZ is NEVER
opened in this packet (counts opens 0; no NPZ loader inside the
Stage-B runner — asserted absent by source test). FORBIDDEN inputs
for any fitting: 1.5M DEV (384..767 and remainder), 1.5M VAL/HOLD,
P20H DEV 0..383, ANY 1M split, reserved 2M, Model-F CAL artifact. No
calibration fallback inside Stage B. This packet performs zero
calibration opens (split-counted counts 0/0).

## 3. Fixed identities (verified in this session; JSON provenance only + the prior worktree-file digest check)

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
(JSON read only, population part):

| item | verified value |
|---|---|
| schema | `nbldpc_v25_split_manifest_v1` |
| 1.5M source tag | `type2_1p5M_20260121_183806` |
| TRAIN frames / pairs | 1660 / 424960 |
| VAL frames / pairs | 553 / 141568 (intra-file gate, never selected) |
| HOLD frames / pairs | 554 / 141824 (intra-file gate, never selected) |

TRAIN base provenance (Stage-A written equivalent with justification;
the manifest gives counts only, never frame numbering): carried over
from P20H §3 unchanged (time-ordered first-60% split code +
same-pipeline parity with the accepted 1M 0-based layout at 256
rows/frame; total 2767 frames). THEREFORE the frozen TRAIN base is 0:
P20H consumed 0..383; P20I DEV is the NEXT 384 frames 384..767;
remainder 768..1659 (892 frames / 228352 pairs); VAL 1660..2212, HOLD
2213..2766. The runner fail-closes on any layout drift
(`dev_population_exact` requires exactly frames 384..767 with 256
rows each; the quadruple gate §4 refuses first), so a wrong base
BLOCKS before any SC call instead of misattributing. Pre-EXECUTE owns
the cross-session isolation adjudication (§4).

Build-manifest file pins (carried over from P20H §3; same 1.5M file):
pairs size 1869178 B / sha
`ca351e5205e76600530121066af4e0e1e5278061745c0797368a49443570a06b`
(provenance pins; enforced at run level by path-string + stat-size
checks pre-open, never recomputed from content).

Any mismatch stops before any root exists and before the DEV content
open, consuming no DEV read and no attempt.

## 4. Development population and closed/consumed-data rule (normative)

The three P18/P19 HOLD blocks (1M frames 1600..1983), the P20B VAL
pool (1M frames 1200..1599), the P20C DEV blocks (1M 0..383), the P20E
DEV blocks (1M 384..767) and the P20F DEV blocks (1M 768..1151,
remainder 1152..1199 never used) plus the P20H DEV blocks (1.5M TRAIN
0..383) are CONSUMED/CLOSED and SHALL NOT supply P20I blocks. The
ENTIRE 1M pool is fail-closed against P20I DEV selection by the
cross-file gate. Cross-packet same-block tuning is forbidden.

The 2M session file is RESERVED and was NOT opened, statted, listed,
or read under Stage A in any form. It is not consumed.

Stage B runs on the DECLARED population (P20H-UNCONSUMED next
segment):

| item | frozen value |
|---|---|
| source file identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet` ONLY (size 1869178 B / sha `ca351e52…a06b` provenance pin; mismatch blocks) |
| split manifest identity | `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/split_manifest.json`, schema `nbldpc_v25_split_manifest_v1`, 1.5M TRAIN 1660/424960 + VAL 553/141568 + HOLD 554/141824 |
| DEV frame rule | NEXT 384 TRAIN frames after P20H in (frame_id, pair_idx) order → frozen TRAIN base 0: `384..767` |
| DEV blocks (N=32768) | `384..511`, `512..639`, `640..767` (3 × 128 frames) |
| unused remainder | frames `768..1659` (892 frames / 228352 pairs) recorded never used — counted, never decoded |
| intra-file VAL / HOLD | 1660..2212 / 2213..2766 — disjoint by fail-closed gate (VAL first) |
| P20H DEV exclusion | 1.5M TRAIN `0..383` — overlap refuses before any protected content open |
| 1M full pool + reserved 2M | excluded by the cross-file gate (checked FIRST); never touched |
| block count | 3 at N=32768 (same cost class as P18/P19/P20B/P20C/P20E/P20F/P20G/P20H) |
| tag domains | new P20I domain (§6) |

Fail-closed quadruple gate (frozen in the runner, order (a)→(b)→(c)→(d),
VAL before HOLD): (a) CROSS-FILE — DEV content-open path +
stat-size/sha pin must equal the 1.5M identity; any 1M or 2M path or
digest mismatch refuses before any SC call (frame integers alone are
never identity); (b) INTRA-FILE — DEV ranges must overlap NONE of
1.5M VAL/HOLD, else refuse before any protected content open; (c)
P20H-DEV EXCLUSION — DEV ranges must overlap NONE of P20H DEV 0..383,
else refuse before any protected content open; (d)
CALIBRATION-IDENTITY — Stage-B prior/table/literal digest must equal
the §2 frozen digest before any SC call, else refuse.

## 5. Preregistered disclosure cap (normative, single frozen tier)

Cap rule: caps are PREREGISTERED per arm, frozen before Pre-EXECUTE,
each FAR below raw input bits with its ratio shown. Key increment
rule: keyΔ = 5·ΔK1 = 5·128 = 640.

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| C0_sc_base (operational) | 319 | 6492 | 34119 = 5*6811+64 | 327743 = 10*32768+63 |
| C1_L1plus (operational) | 447 | 6492 | 34759 = 5*6939+64 (base +640) | 327743 |
| C2_true_l1_diagnostic (oracle) | 0 | 6492 | 32524 = 5*6492+64 | 327743 |

Planned totals if all invoked: key 304206 = 3*34119 (102357) +
3*34759 (104277) + 3*32524 (97572) (operational 206634 + oracle
97572); public 2949687 = 9*327743. C1 key-bit delta vs base exactly
+640 = 5*128.

Meaningfulness bar: base 34119/327680 = 0.10412292 (~10.41%) and C1
34759/327680 = 0.10607605 (~10.61%) of raw input bits (10*N per block
at N=32768) — both far below raw. Sample-CE-normalized ratios
(`disclosure_ce_ratio`) are reported descriptively and are NOT
qualification efficiency.

Recount rule: independent key/public/tag recount from canonical
transcript events; mismatch 0, or the gate BLOCKS.

## 6. Arms (frozen; prior + L1 step swapped per packet §§2-3, all else P20H-identical)

Run block-major (C0, C1, C2) per DEV block; checkpoint after every
(arm, block) record; 9 records total.

- `C0_sc_base`: frozen greedy SC at base disclosure/construction
  (operational; accepted `run_operational_block` called directly with
  k1=319/k2=6492; 2 SC + 1 P20I-domain tag per block).
- `C1_L1plus`: frozen greedy SC at base + the frozen +128 L1 step via
  §2 order-prefix extension, all else identical (operational; the
  single-factor candidate; accepted `run_operational_block` called
  directly with k1=447/k2=6492 as the first-447 prefix of the SAME
  frozen P16 L1 order object — no reselection, on ANY data; 2 SC + 1
  tag per block).
- `C2_true_l1_diagnostic`: true-L1-conditioned L2 at BASE disclosure
  (accepted `run_oracle_control_block` called directly with k2=6492
  and a P20I-domain tag closure; provenance ORACLE, deployable=false,
  1 SC + 1 tag per block; excluded from every operational aggregate;
  never described as a correction result).

No other arms. Tag domain: master 2026092230, prefix
`nbpolar-p20i-l1-disclosure-1p5m-seed`, seed string
`<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256,
MSB-first, truncated to `10*N+63 = 327743` bits). Prefix, master and
arm tokens differ from the P16, P17, P18, P19, P20B, P20C, P20E, P20F,
P20G and P20H domains; raw seed bits are never persisted.

## 7. Thresholds and labels (descriptive only)

Outcome label
`TARGET_EMPIRICAL_N32768_DEV_L1_DISCLOSURE_1P5M_COMPLETE` iff ALL 21
integrity gates hold — regardless of exact-count. Any exact count
(including 0/9 and any partial outcome) is COMPLETE when integrity
holds. This packet makes NO recovery / FER / Wilson / superiority /
qualification / promotion claim. Disclosure reading is descriptive
only: "L1-restoration" = blocks where C0 fails and C1 is exact on the
new-segment blocks (`c1_restored_count` analogue, count + per-block
endpoint rows); "maintain" = C1 exact where C0 exact, reported the
same way. Either pattern (or its absence) counts as COMPLETE; the
C1-restoration / C1-zero-restoration / maintain-only branch decision
belongs to main-thread planning AFTER acceptance, never to this
packet's label. Status taxonomy frozen: `exact` (tag-verified) vs
`verify_failed`, with `undetected` isolated (never success), plus
`decode_failed` / `nonfinite` / `resource_abort` via the P20A path.

Per-record separation (P20A endpoints): `l1_exact`, `hard_l2_exact`,
`oracle_l2_exact`, `pair_exact`, `exact`, first error coordinate +
layer, raw zero-count hits, `1e-15` floor hits + log loss,
candidate-H-conditioned vs true-H-conditioned L2 NLL, outcome
taxonomy, plus C1 disclosure fields (`l1_delta_k1_applied` 128/0,
`l1_disclosure_rule` frozen-order-prefix-extension/base,
`key_bit_delta_vs_base` 640/0).

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until
  authorized execution; no rerun, no seed change, no
  disclosure/construction/calibration tuning after preregistration.
  An execution error rerun is allowed only as a recorded repeat of
  the identical freeze, never as tuning. P20H's spent attempt does
  NOT transfer (independent packet).
- Reads (split-counted, continuing P20H mode): counts-calibration
  opens 0/0 (no NPZ open in this packet; prior reuse only via a
  worktree-file digest check, never a counts open) + DEV open 1/1
  reserved for Stage B (parquet, consumed at first DEV content open).
  HOLD reads 0/1 untouched. Any reopen, new calibration, or DEV refit
  is forbidden. Prior file load is a worktree-file read, not a
  protected open.
- SC/tag budget: 15 SC calls (3 blocks x (2+2+1)) and 9 tags; derived
  per-record recomputation (`1+l2_invoked` operational, `l2_invoked`
  control) must equal the counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative (`MemoryError`
  re-raised at both operational SC sites and the oracle site;
  accepted helpers unchanged); abort preserves evidence + call/
  disclosure accounting; abort is BLOCKED, never success.
- Wall/RSS ceilings: 600 s external timeout, 2 GiB virtual limit
  (`ulimit -v 2097152`), 2 GiB RSS cap, single-thread BLAS/OpenMP +
  `MALLOC_ARENA_MAX=2` — the P20C class (P20C reference at the
  identical 15 SC / 9-tag budget at N=32768: ~92.9 s wall, ~579 MB
  RSS peak; P20E observed ~100.1 s / ~554 MB; P20F observed ~93.0 s /
  ~553 MB; P20H observed ~114.27 s / ~533 MB; P20I plans the identical
  15 SC / 9-tag decoder budget, strictly inside the same class).
- Strategy stop rules restated as binding: no tuning on closed blocks;
  no reuse of the consumed 1M pool (any split, any subrange), P20H
  DEV 0..383, or the reserved 2M file; no third factor after an
  inconclusive single-factor result; no near-raw disclosure
  feasibility claim; no oracle-as-operational; no
  population-reliability inference from this single gate alone (one
  new-segment session is necessary but not sufficient for a
  reliability claim); no efficiency tuning inside this packet.
- SCL entry gate UNCHANGED (all five strategy conditions must still
  be shown; this diagnostic unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage-A freeze + Stage-B five files)

- Stage-A freeze pins (no protected opens): exact module path +
  16-flag Stage-B command verbatim (§10) + population integers + caps
  + budgets + tag domain + prior digest/literals + construction
  digest; recorded in this document.
- Stage-B root: `.workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/l1_disclosure_1p5m/`
  (exactly five files, created pre-open; per-(arm, block)
  checkpointing; one DEV content open; no reopen/rerun). Root is
  ABSENT at Stage-A close and must be ABSENT at Pre-EXECUTE
  (verified absent in this session).
- Five files: `frozen_plan.json`,
  `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl` (9 records at completion),
  `aggregate_summary.json`, `report.md`. Per-record §7 endpoints +
  first error coordinate/layer, zero-count hits, floor hits + log
  loss, true-H vs candidate-H L2 NLL, taxonomy, C1 disclosure triple
  (ΔK1=128, order-prefix, +640 vs base).
- Accounting: key/public/tag disclosure + independent recount
  (mismatch 0); SC-call counts (L1/L2 split) and tag-invocation
  counts exact; block SER/NLL; wall/RSS;
  `c1_restored_count` analogue recomputed descriptively (C0 fail→C1
  exact on new-segment blocks).
- Integrity gates in frozen order (all true or BLOCKED):
  `predecessor_construction_identity`;
  `dev_split_manifest_identity`;
  `dev_block_range_identity` (QUADRUPLE gate: cross-file
  source-tag+digest pin first, then intra-file DEV-vs-VAL/HOLD
  overlap with VAL first, then P20H-DEV exclusion, then
  calibration-identity digest pin);
  `calibration_identity` (prior digest + lambda/floor pins + key-set
  exactness, reuse-only);
  `target_population_contract` (recalibrated literals, recomputed
  H1/H2 within 1e-12 + column normalization);
  `dev_population_exact` (384 frames / 98304 pairs / 256 rows per
  frame / pair indices / symbol range);
  `blocks_exact_with_declared_remainder` (three exact DEV ranges per
  arm in block-major slot order + never-used remainder 892 frames /
  228352 pairs, counted from the pool but never decoded);
  `nine_records_exact`; `sc_calls_exact` (derived 15);
  `tags_exact` (derived 9);
  `orders_valid_k_prefixes_within_registered_arms` (per-arm K1/K2 pins
  + C1 disclosure triple); `oracle_isolation`;
  `buckets_disjoint_exhaustive` (unique arm/block + schema);
  `undetected_zero`; `nonfinite_zero`; `truth_isolation`;
  `disclosure_recount_exact`; `one_open_per_protected_input`;
  `input_stat_unchanged`; `no_unregistered_access`;
  `resource_limits_met_and_no_abort`.

## 10. Commands (exact argv frozen here)

Stage A (injected tests + implementation-freeze; the authorized
command family for this stage, zero protected opens):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m pytest \
  comparison_bench/tests/test_nbpolar_l1_disclosure_1p5m.py \
  -q -p no:cacheprovider --basetemp=$PWD/workspace/p20i/<uuid>/new-suites
```
→ 36/36 green (injected/synthetic inputs + stub loaders, fresh
additive temp root). Packet-scoped predecessors (same settings,
fresh basetemps `workspace/p20i/<uuid>/pred-A|pred-B|pred-C`):
plus1024_per_session_confirmation 36 + per_session_calibration 17 +
plus1024_independent_session 36 + plus1024_extension 36 +
plus1024_confirmation 36 + l2_disclosure_backoff 34 +
bounded_search_diagnostic 34 + operational_f13 29 +
operational_f13_replication 25 + holdout_microcheck 26 +
holdout_backoff_diagnostic 33 = 342/342 green. No shared predecessor
code was changed. Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays
valid.

Stage-A prior check (read-only, zero protected opens): the P20H
`calibrated_prior.npz` canonical digest recomputed in this session
equals `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
via the frozen `canonical_prior_digest` function (worktree-file read
only; never a counts open).

Stage B execution command (FROZEN verbatim here; byte-identical to
the module `FROZEN_COMMAND`, verified by import in this session; NOT
AUTHORIZED until independent Pre-EXECUTE PASS + pasted Stage-B
authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.l1_disclosure_1p5m --prior .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz --source 1p5M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet --dev-frames 384 767 --block-frames 128 --remainder-frames 768 1659 --tag-master 2026092230 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/l1_disclosure_1p5m
```
Sixteen flags, all required, no production default (`--prior`
replaces P20G's `--counts`; the V25 counts NPZ is never opened in
Stage B); three hardcoded arms with the +128 L1 prefix-extension
pinned (never CLI-tunable); `--source` vocabulary frozen to `1p5M`
only; `--dev-frames 384 767` / `--remainder-frames 768 1659` frozen
(expected values confirmed, not assumed). Forbidden by default:
`longrun_*`, `minrerun_*`, `routeA_*`,
`experiments/run_e2e_pipeline.py` on raw data, full sweeps.

Read-only verify: reviewer recomputes §9 identities from artifacts;
never `git show HEAD:` blobs for evidence paths (P19 lesson).

## 11. Stage-A verification evidence (implementation time)

- Output root absent: the Stage-B root `l1_disclosure_1p5m/` does not
  exist. The queue dir holds only `TASK_PACKET.md`, `STATUS.yaml`,
  `PROMPT.md`, `AUTHORIZATION_PROMPT.md`, `P20I_FREEZE.md` (this
  file), `P20I_IMPLEMENTATION_NOTES.md`.
- Zero protected opens: no counts-NPZ open (counts 0/0), no 1.5M
  DEV/VAL/HOLD content open or stat (DEV 0/1, HOLD 0/1), no 1M-pool
  or reserved-2M open/stat/listing/read in any form at close. Only
  JSON provenance reads (P16 construction file with digest recompute
  §3; split manifest population part §3; build-manifest size/sha
  provenance pins) plus the single §2 prior worktree-file digest
  recomputation (never a counts open).
- The 1M pool was never opened; the 2M session file was never opened,
  statted, listed, or read in any form (the runner's 2M refusal path
  is a string literal only; refusal-tested with guards False). No
  parent-directory listing of the pairs root was performed in this
  stage.
- P16 digest recomputed in this session: `055c90...c3faea1b`, equal
  to the stored freeze digest and the frozen flag; P16 root
  untouched.
- Fresh P20I tag master 2026092230 and focused-test seeds
  2026092231..2026092237 appear in NO tracked file outside the P20I
  runner/tests/packet/spec documents (`git grep` verified) and in NO
  untracked file outside the P20I runner/tests/packet/spec documents
  (worktree grep verified) — same bar as P20H.
- Focused suite: `test_nbpolar_l1_disclosure_1p5m.py` 36/36 green
  (fresh temp basetemp, pinned interpreter, `-p
  no:cacheprovider`).
- Packet-scoped predecessor suites 342/342 green (same settings,
  fresh basetemps). No shared predecessor code was changed, so the
  full NB-Polar suite was not run (recorded in the notes).
- This checkout carries no `.venv`; Stage-A pytest and the digest
  checks used the neighboring frozen-command-family interpreter
  (`/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`, the same
  path the frozen Stage-B command names) — no install, no network,
  no repo write outside the fresh temp roots and the frozen packet/
  spec paths.
- No commit (no commit/push authorized in Stage A).

## 12. Forbidden paths and scope boundary (Stage A observed)

Forbidden and not done: any counts-NPZ open, any DEV/VAL/HOLD/EVAL/
raw content open or stat, the 2M file in any form, 1M-pool tuning or
peeking, other N in the frozen run, any added/changed arm, any
construction path, BEC, transform/belief/list decoders, a second tag
outside the registered arms, fitting/sampling on DEV, any use of the
remainder/1M consumed/closed frames/P20H DEV 0..383 or the reserved
2M file, a second L1 tier (`C1b`), a second L2 step, an
alternative-construction second factor, per-DEV prior refit,
production benchmark, `results/` or
`comparison_bench/outputs_comparison/` writes, P12-P20H code or
old-root modification, official prior/probe seed reuse, commit/push.
Scope is the frozen +128 L1 order-prefix step + implementation +
frozen planning artifacts for a descriptive L1-disclosure diagnostic
on new blocks; it is not real-frame FER, reconciliation efficiency,
leakage, key rate, scaling, qualification or promotion evidence, and
C2 is never operational.
