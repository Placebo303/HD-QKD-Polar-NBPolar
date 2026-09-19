# Phase 4-P20E — +1024 candidate confirmation on new blocks (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: implementation Stage A + single authorized execution Stage B).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read,
  decoder execution, or commit/push is authorized by this file.
- Predecessor: `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (P20C) + P20A `IMPLEMENTATION_ACCEPTED` (resource passthrough + endpoint instrumentation).
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` (three stages:
  feasibility → reproducible reliability → efficiency optimization; confirmation on new
  blocks/sessions; stop rules) and `docs/nbpolar/ROADMAP.md` current-priority section.
- Gate discipline: any standing long-horizon authorization ("proceed at least five rounds")
  does NOT collapse Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.

## 1. Mission

Confirm the frozen +1024 candidate on NEW real development blocks, changing nothing:

> With construction / disclosure / order / prior / floor / kernel / representation / SC
> all carried over byte-identical from P20C (K1=319, K2 base 6492 / B1 7516 via frozen
> order-prefix extension, floor 1e-15, N=32768, new P20E tag domains only), zero tuning,
> does +1024 repeat its P20C recovery and maintain exact on independent new blocks — or
> does it not?

This is strategy stage 2 (reproducible reliability), first confirmation round. P20C's
TRAIN 0..383 signal was descriptive development evidence, not proof. This packet asks
only whether that signal repeats on blocks the candidate has never seen. Positive
(repeat recovery / maintained exact) directs a later efficiency-optimization round;
negative (no repeat) returns to the P20D alternative-construction candidate. Both
branches are deferred to §16 and must not be prejudged here.

## 2. Background (frozen inputs, not re-argued here)

- P20C (descriptive-accepted,
  `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE_ACCEPTED_DESCRIPTIVE`):
  9 records, 20/20 integrity gates PASS, exit 0, wall ~92.9 s. B0 2/3 exact
  (blk1 `verify_failed` at L2@723 with L1 exact); B1 3/3 exact (ΔK2=+1024,
  K2 6492→7516 order-prefix, key Δ+5120); B2 oracle 2/3 exact (blk1 also fail;
  ORACLE / deployable=false, excluded from aggregates). Operational exact 5/6,
  `b1_restored_count` 1 (block1 B0 fail→B1 exact). Overall exact 7 /
  verify_failed 2 / undetected 0 / decode_failed 0 / nonfinite 0 / abort 0.
  15 SC + 9 tags recalculated consistent. Caps 34119 / 39239 / 32524 + 327743
  public (~10.41% / ~11.97% of raw). First positive DEV signal for the
  information-insufficiency hypothesis; SCL still unlocked.
- Closed data: the three P18/P19 HOLD blocks (frames 1600..1983) are CLOSED and
  SHALL NOT select anything. The P20B VAL pool (frames 1200..1599, including
  remainder 1584..1599) is CONSUMED and SHALL NOT supply blocks.
- P20C DEV blocks (frames 0..383: 0..127 / 128..255 / 256..383) are now CONSUMED
  development data. They SHALL NOT supply P20E blocks and SHALL NOT be re-tuned.
  P20C's declared-never-used remainder 384..1199 is preregistered for enablement
  ONLY as §4 states (384..767); 768..1199 stays never-used.
- P20A (implementation-accepted): `MemoryError` re-raised at 3 internal SC sites;
  endpoints `l1_exact` / `hard_l2_exact` / `oracle_l2_exact` / `pair_exact`
  (`pair_exact` tag-independent; `exact` tag-verified); zero protected reads at
  implementation time.

## 3. Freeze (normative — carried over, zero tuning)

FROZEN identical for every arm (any deviation is a packet violation, not a choice):

- Prior: frozen Model-F concentration prior path + fixed `1e-15` floor before SC.
  Diagnose only; never retune.
- Construction order: accepted P16 order (digest pinned in the Stage-A freeze),
  K1=319 base L1 set unchanged on every arm. B1's +1024 set is the SAME first-7516
  prefix of the SAME frozen P16 L2 order — no reselection, no re-derivation.
- Disclosure: K2=6492 (B0, B2) / 7516 (B1); K_total 6811 / 7835. Caps per §5.
- Kernel / representation / transform / SC arithmetic: unchanged; greedy SC only;
  no SCL, no new kernel/model/schema.
- Verification: one final 64-bit Toeplitz tag per block/record under NEW P20E tag
  domains (§6, master 2026092100); verification never selects a candidate.

VARIED: NOTHING. This packet varies no factor. The only deliberate differences from
P20C are the new-block population (§4) and the new tag domain (§6) — both
provenance/identity changes, never algorithm changes.

## 4. Population and closed/consumed-data rule (normative)

- The three P18/P19 HOLD blocks (frames 1600..1983) SHALL NOT select K, floor,
  order, decoder, disclosure, or any successful point.
- The P20B VAL pool (frames 1200..1599, INCLUDING remainder 1584..1599) is
  CONSUMED and SHALL NOT supply P20E blocks.
- The P20C DEV blocks (frames 0..383) are CONSUMED and SHALL NOT supply P20E
  blocks. Cross-packet same-block tuning is forbidden.
- Stage B runs on the DECLARED new-block population (preregistered enablement of
  P20C's never-used remainder):

| item | frozen value |
|---|---|
| source file identity | same registered paths as P18/P19/P20B/P20C (same NPZ + same pairs parquet + same manifest + same P16 construction; no new file, no new digest) |
| DEV frame range (enabled subrange) | 384..767 (same-file TRAIN range of the same 1M source) |
| DEV blocks (N=32768) | `384..511`, `512..639`, `640..767` (3 x 128 frames) |
| unused remainder | frames `768..1199`, 432 frames / 110592 pairs, recorded never used |
| P20C-consumed range | 0..383 — disjoint by fail-closed gate |
| closed range | 1600..1983 — disjoint by fail-closed gate |
| consumed range | 1200..1599 — disjoint by fail-closed gate |
| block count | 3 at N=32768 (mirrors P18/P19/P20B/P20C cost class) |
| tag domains | new P20E domain below |

- Stage A confirms (or replaces with a written equivalent + justification) via
  JSON-manifest provenance reads ONLY, never a content open: manifest
  TRAIN 1200 / VAL 400 / HOLD 400 geometry pins TRAIN to 0..1199 by elimination
  with accepted VAL/HOLD ranges; the runner additionally fail-closes
  (`dev_population_exact` requires exactly the §4 ranges; the triple overlap
  gate §9 refuses first), so any layout drift blocks before any SC call.
- Evidence-reuse isolation (Pre-EXECUTE adjudicates): Model-F prior is a FROZEN
  aggregate concentration model, identical across arms, never refit on DEV; the
  comparison is an INTER-ARM differential (base vs +1024 vs oracle) on
  DEV-specific frames, not a prior effect; no K/floor/order/step selection
  touches DEV, P20C-consumed, closed, or consumed ranges. If Pre-EXECUTE rejects
  the isolation, Stage A substitutes a declared independent session (or other
  registered split) with the same 3-block cost class — same packet, new freeze
  values, re-review.
- Fail-closed overlap gate (frozen in the runner, checked first): DEV ranges must
  overlap NONE of 0..383, 1200..1599, 1600..1983, else the run refuses before any
  protected content open.

## 5. Preregistered disclosure cap (normative, carried over)

- Cap rule: caps are CARRIED OVER unchanged from P20C (no growth, no tuning) —
  preregistered per arm, frozen before Pre-EXECUTE, each FAR below raw input bits
  with its ratio shown.

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| B0_sc_base (operational) | 319 | 6492 | 34119 = 5*6811+64 | 327743 = 10*32768+63 |
| B1_L2plus (operational) | 319 | 7516 | 39239 = 5*7835+64 | 327743 |
| B2_true_l1_diagnostic (oracle) | 0 | 6492 | 32524 = 5*6492+64 | 327743 |

- Planned totals if all invoked: key 317646 = 3*34119 + 3*39239 + 3*32524
  (operational 220074 + oracle 97572); public 2949687 = 9*327743. B1 key-bit
  delta vs base exactly +5120 = 5*1024.
- Meaningfulness bar (unchanged): base 34119/327680 ≈ 10.41% and B1
  39239/327680 ≈ 11.97% of raw input bits (10*N per block at N=32768) — both far
  below raw. Sample-CE-normalized ratios are reported descriptively and are NOT
  qualification efficiency.
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate BLOCKS.

## 6. Arms (frozen; identical to P20C for comparability)

- `B0_sc_base`: frozen greedy SC at base disclosure/construction (operational; 2 SC +
  1 P20E-domain tag per block).
- `B1_L2plus`: frozen greedy SC with the SAME +1024 L2 order-prefix step as P20C,
  all else identical (operational; the confirmation candidate; 2 SC + 1 P20E-domain
  tag per block).
- `B2_true_l1_diagnostic`: true-L1-conditioned diagnostic at BASE disclosure
  (provenance ORACLE, deployable=false, excluded from every operational aggregate;
  never described as a correction result; 1 SC + 1 P20E-domain tag per block).
- No other arms. Run block-major (B0, B1, B2) per DEV block; checkpoint after every
  (arm, block) record; 9 records total. Five-file + per-arm checkpointing pattern
  reused from P18/P19/P20B/P20C.
- Tag domain: master 2026092100, prefix
  `nbpolar-p20e-plus1024-confirmation-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix, master and arm tokens differ from
  the P16, P17, P18, P19, P20B and P20C domains; raw seed bits are never persisted.
  Stage A verifies by repo grep that master 2026092100 and focused-test seeds
  2026092101..2107 appear in no tracked file outside the P20E runner/tests/packet/
  spec/queue documents.

## 7. Thresholds and labels (descriptive only)

- Outcome label `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE` iff ALL
  integrity gates (§9) hold — regardless of exact-count. Any exact count (including
  0/9 and any partial outcome) is COMPLETE when integrity holds.
- This packet makes NO recovery / FER / Wilson / superiority / qualification /
  promotion claim. Confirmation reading is descriptive only:
  - "repeat recovery" = blocks where B0 fails and B1 is exact on the NEW blocks
    (P20C analogue `b1_restored_count`), reported as a count with per-block
    endpoint rows — a development signal, never a pass/fail verdict;
  - "maintain" = B1 exact where B0 exact, reported the same way.
  Either pattern (or its absence) counts as COMPLETE; the positive/negative branch
  decision belongs to main-thread planning AFTER acceptance (§16), never to this
  packet's label.
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`, with
  `undetected` isolated (never merged into success/FER), plus `decode_failed` /
  `nonfinite` / `resource_abort` via the P20A path. P20A four-endpoint separation
  (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` / `pair_exact`) recorded per record.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized execution;
  no rerun, no seed change, no disclosure/construction tuning after preregistration.
  An execution-error rerun is allowed only as a recorded repeat of the identical
  freeze, never as tuning.
- SC/tag budget: 15 SC calls (3 blocks x (2+2+1)) and 9 tags; derived per-record
  recomputation must equal the counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence +
  call/disclosure accounting; abort is a BLOCKED result, never success.
- Wall/RSS ceilings frozen in `P20E_FREEZE.md` (P20C class reference: ~92.9 s wall,
  ~579 MB RSS peak for 15 SC calls / 9 tags at N=32768; P20E plans the identical
  15 SC / 9-tag budget, strictly inside the same class; external timeout 600 s +
  virtual/RSS caps 2 GiB + single thread frozen as in P20C §8).
- Strategy stop rules restated as binding: no tuning on closed blocks; no reuse of
  the consumed VAL pool or the consumed P20C DEV blocks; no third factor after an
  inconclusive single-factor result; no near-raw disclosure feasibility claim; no
  oracle-as-operational; no population-reliability inference before an
  independent-session gate; no efficiency tuning inside this confirmation packet.
- SCL entry gate UNCHANGED (all five strategy conditions must still be shown; this
  confirmation unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage B, all frozen in P20E_FREEZE.md)

- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P20E-PLUS1024-CONFIRMATION/plus1024_confirmation/`
  (exactly five files, created pre-open; per-(arm, block) checkpointing; one content
  open per protected input; no reopen/rerun). Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl` (9 records at completion), `aggregate_summary.json`,
  `report.md`. Scalar-only: never counts, sampled symbols, truth vectors, decoded
  labels/keys, metric planes, raw rows, per-arm orders, tag seeds or RNG state.
- Per-record separation (P20A endpoints): `l1_exact`, `hard_l2_exact`,
  `oracle_l2_exact`, `pair_exact`, `exact`, first error coordinate + layer, raw
  zero-count hits, `1e-15` floor hits + log loss, true-H-conditioned vs
  candidate-H-conditioned L2 NLL, outcome taxonomy, plus B1 disclosure fields
  (ΔK2=1024 applied, order-prefix positions fixed, key-bit delta +5120 vs base).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0); SC-call
  counts (L1/L2 split) and tag-invocation counts exact; block SER/NLL; wall/RSS;
  `b1_restored_count` analogue recomputed descriptively (B0 fail→B1 exact on new blocks).
- Integrity gates (all true or BLOCKED; frozen order in the freeze): predecessor
  construction identity; split manifest identity; dev block range identity (TRIPLE
  overlap pre-check: P20C-consumed 0..383 first, then consumed 1200..1599, then
  closed 1600..1983); target population contract (7/7 preconditions or frozen
  equivalent); dev population exact; blocks exact with declared remainder (three
  exact DEV ranges per arm in block-major slot order + never-used remainder 432
  frames / 110592 pairs); nine records exact; SC calls exact (derived 15); tags
  exact (derived 9); order-prefix disclosure positions fixed within registered arms;
  oracle isolation; buckets disjoint exhaustive; undetected zero; nonfinite zero;
  truth isolation; disclosure recount exact; one open per protected input; input
  stat unchanged; no unregistered access; resource limits met and no abort.

## 10. Commands (exact argv frozen in Stage A / P20E_FREEZE.md)

- Stage A (injected only, authorized separately): `.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_<plus1024_confirmation files> -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20e/<uuid>/` temp root.
  Zero protected opens (audit required). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage B execution command (RECOMMENDED here, frozen verbatim in `P20E_FREEZE.md`;
  NOT AUTHORIZED until independent Pre-EXECUTE PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_confirmation --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --dev-frames 384 767 --block-frames 128 --remainder-frames 768 1199 --tag-master 2026092100 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20E-PLUS1024-CONFIRMATION/plus1024_confirmation
```
  Sixteen flags, all required, no production default; three hardcoded arms with the
  +1024 prefix-extension carried over pinned (never CLI-tunable). Stage A confirms the
  module path (`plus1024_confirmation` thin runner reusing P18 loading/block formation
  + P16 operational helpers read-only; new P20E tag domains) or freezes a written
  equivalent with justification. Forbidden by default: `longrun_*`, `minrerun_*`,
  `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git show
  HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: thin runner + focused injected tests + `P20E_FREEZE.md` +
  `P20E_IMPLEMENTATION_NOTES.md` (exact files, diffs, test commands/results, frozen
  population/cap/command/budget). No protected reads, no output root.
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md` (+ freeze,
  `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md` at their gates).
- OpenSpec P20E delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20e/spec.md`
  + `tasks.md` P20E section (same umbrella change as P18/P19/P20A/P20B/P20C; no new top-level change).

## 12. Allowed work

- New thin plus1024-confirmation runner + focused injected tests (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py`, `l2_disclosure_backoff.py` (+ `construction.py`,
  `prior.py`, `sc.py` contracts as called).
- P20E OpenSpec delta + packet docs + freeze/return/review files + Stage-B evidence root
  (root only after Stage-B authorization).

## 13. Forbidden work

- Any protected TRAIN/HOLD/VAL/EVAL/raw read, stat, or open before Stage-B authorization;
  any decoder execution before Pre-EXECUTE PASS + pasted authorization.
- Any change to GF32/transform/SC arithmetic, prior/floor, construction order (including
  the carried-over prefix-extension rule itself), tag scheme semantics, outcome
  precedence, accepted evidence roots, or `src/` + `experiments/` + `tools/` frozen baseline.
- No K/floor/order/decoder/step/success-point selection on the closed three blocks, the
  consumed VAL pool, or the consumed P20C DEV blocks; no second factor (alternative
  construction) inside this packet; no second disclosure step (`B1b`); no efficiency
  tuning; no new-block peeking before the authorized attempt.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push;
  no self-acceptance; no P20D scope creep.

## 14. Acceptance IDs

- `P20E-R1`: prior/construction-order/floor/kernel/representation/SC carried over
  identical across arms; the +1024 prefix-extension step unchanged from P20C; only the
  new-block population and new tag domain differ.
- `P20E-R2`: closed three blocks select nothing; consumed VAL pool untouched; consumed
  P20C DEV blocks untouched; new population (384..511 / 512..639 / 640..767, remainder
  768..1199 never used) independently declared, digest-pinned, triple-gated,
  Pre-EXECUTE-approved.
- `P20E-R3`: disclosure caps carried over per arm (34119 / 39239 / 32524 + 327743
  public), ratios-vs-raw shown (~10.41% / ~11.97%), recount mismatch 0; CE ratios never
  called efficiency.
- `P20E-R4`: carried-over +1024 step + order-prefix rule frozen before execution,
  unchanged after; no tag-guided selection, no evidence reuse, no post-hoc re-picking.
- `P20E-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9; `undetected`
  isolated; oracle arm never operational.
- `P20E-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning; resource aborts
  via P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20E-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded; main-thread acceptance
  owns the label; descriptive-only, no FER/qualification/promotion language; branch
  reading (§16) stays planning input, never an in-packet verdict.
- `P20E-R8`: Stage-A suites green on injected data with zero protected opens; no
  commit/push; frozen dirs byte-untouched except the §12 manifest.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs `P20E-R1..R8`
(stage-appropriately) complete with changed files + exact commands/results + artifact
inventory; or (b) a concrete blocker with failing command, exact error/traceback,
attempted remedies, and the ONE decision needed from the main thread. "Still incomplete"
is not a completion report. The operator never marks its own work accepted and never
authorizes Stage B.

## 16. Deferred options (not in this packet)

- Positive branch (deferred, not prejudged): if +1024 repeats recovery / maintains exact
  on the new blocks (descriptive reading of the §7 counts), the NEXT packet plans the
  strategy stage-3 efficiency-optimization round (reduce disclosure / wall / memory under
  a new preregistered cap). This packet performs no efficiency tuning and licenses no
  efficiency claim.
- Negative branch (deferred, not prejudged): if +1024 does not repeat on the new blocks,
  the NEXT packet returns to the P20D candidate — strategy option 2, fixed disclosure +
  ONE preregistered alternative L2 construction on independent development data. P20D
  stays deferred until P20E's confirmation answer exists.
- Rationale for confirmation now: P20C's +1024 signal came from TRAIN 0..383 development
  blocks; per the strategy's second stage, a frozen candidate must be confirmed on new
  blocks before any efficiency work or construction redesign. Fewer blocks, cleaner
  attribution: same 3-block cost class, same caps, same arms — only new frames.
