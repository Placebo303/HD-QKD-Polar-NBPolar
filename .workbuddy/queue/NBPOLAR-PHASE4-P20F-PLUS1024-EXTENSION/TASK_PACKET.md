# Phase 4-P20F — +1024 extension confirmation on last same-file TRAIN tranche (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: implementation Stage A + single authorized execution Stage B).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read,
  decoder execution, or commit/push is authorized by this file.
- Predecessor: `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (P20E) + P20A `IMPLEMENTATION_ACCEPTED` (resource passthrough + endpoint instrumentation).
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` (three stages:
  feasibility → reproducible reliability → efficiency optimization; confirmation on new
  blocks/sessions; stop rules) and `docs/nbpolar/ROADMAP.md` current-priority section.
- Gate discipline: any standing long-horizon authorization ("proceed at least five rounds")
  does NOT collapse Tier-Y gates. Stage A and Stage B each need their own explicit pasted
  authorization text; this packet authorizes neither.

## 1. Mission

Confirm the frozen +1024 candidate on the LAST same-file TRAIN tranche, changing nothing:

> With construction / disclosure / order / prior / floor / kernel / representation / SC
> all carried over byte-identical from P20C/P20E (K1=319, K2 base 6492 / B1 7516 via frozen
> order-prefix extension, floor 1e-15, N=32768, new P20F tag domains only), zero tuning,
> does +1024 maintain exact on the remaining new blocks — and does a P20C-style
> restoration event (B0 fail → B1 exact) get a second opportunity to replicate, or not?

This is strategy stage 2 (reproducible reliability), second confirmation round on new
blocks. P20C's TRAIN 0..383 signal was descriptive development evidence; P20E's TRAIN
384..767 confirmation held maintain-exact (B0 3/3, B1 3/3, B2 3/3; operational 6/6) with
the restoration-event denominator at 0 — neither replicated nor falsified. This packet
asks only whether the maintain pattern holds on blocks the candidate has still never
seen, and whether any restoration opportunity appears. Positive (restoration replicates
/ maintain holds) directs a later independent-session round; genuine negative (B0 fails
unrestored by B1 despite opportunities) returns to the P20D alternative-construction
candidate. All branches are deferred to §16 and must not be prejudged here.

## 2. Background (frozen inputs, not re-argued here)

- P20C (descriptive-accepted,
  `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE_ACCEPTED_DESCRIPTIVE`):
  B0 2/3 exact (blk1 `verify_failed` at L2@723 with L1 exact); B1 3/3 exact (ΔK2=+1024,
  K2 6492→7516 order-prefix, key Δ+5120); B2 oracle 2/3 exact (excluded from aggregates).
  Operational exact 5/6, `b1_restored_count` 1 (block1 B0 fail→B1 exact). Overall exact 7 /
  verify_failed 2 / undetected 0 / decode_failed 0 / nonfinite 0 / abort 0. Caps 34119 /
  39239 / 32524 + 327743 public (~10.41% / ~11.97% of raw). First positive DEV signal for
  the information-insufficiency hypothesis; SCL still unlocked.
- P20E (descriptive-accepted,
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE_ACCEPTED_DESCRIPTIVE`):
  three NEW blocks 384..511 / 512..639 / 640..767, all three arms 3/3 exact (overall 9 /
  verify_failed 0 / undetected 0 / decode_failed 0 / nonfinite 0 / abort 0; operational
  6/6). `b1_restored_count` analogue 0/3: B0 never failed, so no restoration event
  occurred ("maintain" mode, descriptive only). Cumulative descriptive: B1 +1024
  operational 6/6 exact (P20C 3/3 + P20E 3/3), B0 5/6. Pre-RESULT honesty assessment:
  maintain-exact holds; restoration denominator 0.
- Closed data: the three P18/P19 HOLD blocks (frames 1600..1983) are CLOSED and
  SHALL NOT select anything. The P20B VAL pool (frames 1200..1599, including
  remainder 1584..1599) is CONSUMED and SHALL NOT supply blocks.
- Consumed DEV: P20C blocks (frames 0..383) and P20E blocks (frames 384..767) are CONSUMED
  development data. They SHALL NOT supply P20F blocks and SHALL NOT be re-tuned.
  P20E's declared-never-used remainder 768..1199 is preregistered for enablement ONLY as
  §4 states (768..1151); 1152..1199 stays never-used.
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
- Verification: one final 64-bit Toeplitz tag per block/record under NEW P20F tag
  domains (§6, master 2026092200); verification never selects a candidate.

VARIED: NOTHING. This packet varies no factor. The only deliberate differences from
P20C/P20E are the new-block population (§4) and the new tag domain (§6) — both
provenance/identity changes, never algorithm changes.

## 4. Population and closed/consumed-data rule (normative)

- The three P18/P19 HOLD blocks (frames 1600..1983) SHALL NOT select K, floor,
  order, decoder, disclosure, or any successful point.
- The P20B VAL pool (frames 1200..1599, INCLUDING remainder 1584..1599) is
  CONSUMED and SHALL NOT supply P20F blocks.
- The P20C DEV blocks (frames 0..383) and the P20E DEV blocks (frames 384..767) are
  CONSUMED and SHALL NOT supply P20F blocks. Cross-packet same-block tuning is forbidden.
- Stage B runs on the DECLARED new-block population (preregistered enablement of
  P20E's never-used remainder):

| item | frozen value |
|---|---|
| source file identity | same registered paths as P18/P19/P20B/P20C/P20E (same NPZ + same pairs parquet + same manifest + same P16 construction; no new file, no new digest) |
| DEV frame range (enabled subrange) | 768..1151 (same-file TRAIN range of the same 1M source) |
| DEV blocks (N=32768) | `768..895`, `896..1023`, `1024..1151` (3 x 128 frames) |
| unused remainder | frames `1152..1199`, 48 frames / 12288 pairs, recorded never used |
| P20C-consumed range | 0..383 — disjoint by fail-closed gate |
| P20E-consumed range | 384..767 — disjoint by fail-closed gate |
| consumed range | 1200..1599 — disjoint by fail-closed gate |
| closed range | 1600..1983 — disjoint by fail-closed gate |
| block count | 3 at N=32768 (mirrors P18/P19/P20B/P20C/P20E cost class) |
| tag domains | new P20F domain below |

- Stage A confirms (or replaces with a written equivalent + justification) via
  JSON-manifest provenance reads ONLY, never a content open: manifest
  TRAIN 1200 / VAL 400 / HOLD 400 geometry pins TRAIN to 0..1199 by elimination
  with accepted VAL/HOLD ranges; the runner additionally fail-closes
  (`dev_population_exact` requires exactly the §4 ranges; the quadruple overlap
  gate §9 refuses first), so any layout drift blocks before any SC call.
- Evidence-reuse isolation (Pre-EXECUTE adjudicates): Model-F prior is a FROZEN
  aggregate concentration model, identical across arms, never refit on DEV; the
  comparison is an INTER-ARM differential (base vs +1024 vs oracle) on
  DEV-specific frames, not a prior effect; no K/floor/order/step selection
  touches DEV, consumed, closed, or consumed ranges. If Pre-EXECUTE rejects
  the isolation, Stage A substitutes a declared independent session (or other
  registered split) with the same 3-block cost class — same packet, new freeze
  values, re-review.
- Fail-closed overlap gate (frozen in the runner, checked first, in this order): DEV
  ranges must overlap NONE of 0..383, 384..767, 1200..1599, 1600..1983, else the run
  refuses before any protected content open.

## 5. Preregistered disclosure cap (normative, carried over)

- Cap rule: caps are CARRIED OVER unchanged from P20C/P20E (no growth, no tuning) —
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

## 6. Arms (frozen; identical to P20C/P20E for comparability)

- `B0_sc_base`: frozen greedy SC at base disclosure/construction (operational; 2 SC +
  1 P20F-domain tag per block).
- `B1_L2plus`: frozen greedy SC with the SAME +1024 L2 order-prefix step as P20C/P20E,
  all else identical (operational; the confirmation candidate; 2 SC + 1 P20F-domain
  tag per block).
- `B2_true_l1_diagnostic`: true-L1-conditioned diagnostic at BASE disclosure
  (provenance ORACLE, deployable=false, excluded from every operational aggregate;
  never described as a correction result; 1 SC + 1 P20F-domain tag per block).
- No other arms. Run block-major (B0, B1, B2) per DEV block; checkpoint after every
  (arm, block) record; 9 records total. Five-file + per-arm checkpointing pattern
  reused from P18/P19/P20B/P20C/P20E.
- Tag domain: master 2026092200, prefix
  `nbpolar-p20f-plus1024-extension-seed`, seed string
  `<prefix>:<master>:<n>:<arm>:<block_index>:<counter>` (SHA-256, MSB-first,
  truncated to `10*N+63 = 327743` bits). Prefix, master and arm tokens differ from
  the P16, P17, P18, P19, P20B, P20C and P20E domains; raw seed bits are never persisted.
  Stage A verifies by repo grep that master 2026092200 and focused-test seeds
  2026092201..2207 appear in no tracked file outside the P20F runner/tests/packet/
  spec/queue documents.

## 7. Thresholds and labels (descriptive only)

- Outcome label `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE` iff ALL
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
- Wall/RSS ceilings frozen in `P20F_FREEZE.md` (P20C class reference: ~92.9 s wall,
  ~579 MB RSS peak; P20E observed ~100.1 s / ~554 MB at the identical 15 SC / 9-tag
  budget at N=32768; P20F plans the identical budget, strictly inside the same class;
  external timeout 600 s + virtual/RSS caps 2 GiB + single thread frozen as in P20E §8).
- Strategy stop rules restated as binding: no tuning on closed blocks; no reuse of
  the consumed VAL pool or the consumed P20C/P20E DEV blocks; no third factor after an
  inconclusive single-factor result; no near-raw disclosure feasibility claim; no
  oracle-as-operational; no population-reliability inference before an
  independent-session gate; no efficiency tuning inside this confirmation packet.
- SCL entry gate UNCHANGED (all five strategy conditions must still be shown; this
  confirmation unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage B, all frozen in P20F_FREEZE.md)

- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION/plus1024_extension/`
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
  construction identity; split manifest identity; dev block range identity (QUADRUPLE
  overlap pre-check in §4 order: P20C-consumed 0..383 first, then P20E-consumed 384..767,
  then consumed 1200..1599, then closed 1600..1983); target population contract (7/7
  preconditions or frozen equivalent); dev population exact; blocks exact with declared
  remainder (three exact DEV ranges per arm in block-major slot order + never-used
  remainder 48 frames / 12288 pairs, frames 1152..1199, counted never decoded); nine
  records exact; SC calls exact (derived 15); tags exact (derived 9); order-prefix
  disclosure positions fixed within registered arms; oracle isolation; buckets disjoint
  exhaustive; undetected zero; nonfinite zero; truth isolation; disclosure recount exact;
  one open per protected input; input stat unchanged; no unregistered access; resource
  limits met and no abort.

## 10. Commands (exact argv frozen in Stage A / P20F_FREEZE.md)

- Stage A (injected only, authorized separately): `.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_<plus1024_extension files> -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20f/<uuid>/` temp root.
  Zero protected opens (audit required). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage B execution command (RECOMMENDED here, frozen verbatim in `P20F_FREEZE.md`;
  NOT AUTHORIZED until independent Pre-EXECUTE PASS + pasted Stage-B authorization):
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
ulimit -v 2097152
timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_extension --counts /mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz --source 1M --floor 1e-15 --n 32768 --k1 319 --k2 6492 --construction .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json --construction-digest 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b --dev-pairs comparison_bench/outputs_comparison/nonbinary_diagnostics/v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet --dev-frames 768 1151 --block-frames 128 --remainder-frames 1152 1199 --tag-master 2026092200 --chunk-rows 512 --tag-bits 64 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION/plus1024_extension
```
  Sixteen flags, all required, no production default; three hardcoded arms with the
  +1024 prefix-extension carried over pinned (never CLI-tunable). Stage A confirms the
  module path (`plus1024_extension` thin runner reusing P18 loading/block formation
  + P16 operational helpers read-only; new P20F tag domains) or freezes a written
  equivalent with justification. Forbidden by default: `longrun_*`, `minrerun_*`,
  `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git show
  HEAD:` blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: thin runner + focused injected tests + `P20F_FREEZE.md` +
  `P20F_IMPLEMENTATION_NOTES.md` (exact files, diffs, test commands/results, frozen
  population/cap/command/budget). No protected reads, no output root.
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md` (+ freeze,
  `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md` at their gates).
- OpenSpec P20F delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20f/spec.md`
  + `tasks.md` P20F section (same umbrella change as P18/P19/P20A/P20B/P20C/P20E; no new top-level change).

## 12. Allowed work

- New thin plus1024-extension runner + focused injected tests (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py`, `l2_disclosure_backoff.py`,
  `plus1024_confirmation.py` (+ `construction.py`,
  `prior.py`, `sc.py` contracts as called).
- P20F OpenSpec delta + packet docs + freeze/return/review files + Stage-B evidence root
  (root only after Stage-B authorization).

## 13. Forbidden work

- Any protected TRAIN/HOLD/VAL/EVAL/raw read, stat, or open before Stage-B authorization;
  any decoder execution before Pre-EXECUTE PASS + pasted authorization.
- Any change to GF32/transform/SC arithmetic, prior/floor, construction order (including
  the carried-over prefix-extension rule itself), tag scheme semantics, outcome
  precedence, accepted evidence roots, or `src/` + `experiments/` + `tools/` frozen baseline.
- No K/floor/order/decoder/step/success-point selection on the closed three blocks, the
  consumed VAL pool, or the consumed P20C/P20E DEV blocks; no second factor (alternative
  construction) inside this packet; no second disclosure step (`B1b`); no efficiency
  tuning; no new-block peeking before the authorized attempt.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push;
  no self-acceptance; no P20D scope creep.

## 14. Acceptance IDs

- `P20F-R1`: prior/construction-order/floor/kernel/representation/SC carried over
  identical across arms; the +1024 prefix-extension step unchanged from P20C/P20E; only the
  new-block population and new tag domain differ.
- `P20F-R2`: closed three blocks select nothing; consumed VAL pool untouched; consumed
  P20C DEV blocks (0..383) and consumed P20E DEV blocks (384..767) untouched; new population
  (768..895 / 896..1023 / 1024..1151, remainder 1152..1199 never used) independently
  declared, digest-pinned, quadruple-gated, Pre-EXECUTE-approved.
- `P20F-R3`: disclosure caps carried over per arm (34119 / 39239 / 32524 + 327743
  public), ratios-vs-raw shown (~10.41% / ~11.97%), recount mismatch 0; CE ratios never
  called efficiency.
- `P20F-R4`: carried-over +1024 step + order-prefix rule frozen before execution,
  unchanged after; no tag-guided selection, no evidence reuse, no post-hoc re-picking.
- `P20F-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9; `undetected`
  isolated; oracle arm never operational.
- `P20F-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning; resource aborts
  via P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20F-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded; main-thread acceptance
  owns the label; descriptive-only, no FER/qualification/promotion language; branch
  reading (§16) stays planning input, never an in-packet verdict.
- `P20F-R8`: Stage-A suites green on injected data with zero protected opens; no
  commit/push; frozen dirs byte-untouched except the §12 manifest.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs `P20F-R1..R8`
(stage-appropriately) complete with changed files + exact commands/results + artifact
inventory; or (b) a concrete blocker with failing command, exact error/traceback,
attempted remedies, and the ONE decision needed from the main thread. "Still incomplete"
is not a completion report. The operator never marks its own work accepted and never
authorizes Stage B.

## 16. Deferred options (not in this packet)

- Independent-session confirmation (deferred, strategy stage-2 second half): the 1.5M
  (`type2_1p5M_20260121_183806`) and 2M (`type2_2M_20260121_183657`) acquisition sessions
  exist as registered files (pairs parquet present; TRAIN/VAL/HOLD geometry in the same
  split manifest) but have NEVER been frozen as an NB-Polar Tier-Y DEV population — no
  prior-transfer check, no geometry pin, no tag domain, no NB-Polar execution. A future
  packet may freeze one of them as DEV with the same 3-block cost class and carried-over
  +1024 point, but only AFTER this same-file extension answers. This packet performs no
  cross-session work and licenses no cross-session claim.
- Disclosure-minimality probe (deferred): +512 vs +1024 at frozen order. Trigger: at least
  one restoration event (B0 fail → B1 exact) replicated, so the smaller-step comparison
  discriminates. With the restoration denominator at 0 after P20E, the probe cannot yet
  discriminate; it stays deferred.
- P20D candidate (deferred): strategy option 2, fixed disclosure + ONE preregistered
  alternative L2 construction on independent development data. Trigger: genuine negative —
  B0 failures occur on new blocks but B1 does not restore them. P20E was maintain-mode
  (no B0 failures), not a negative; P20D stays deferred until a negative exists.
- Efficiency optimization (deferred): reduce disclosure / wall / memory under a new
  preregistered cap. Trigger: restoration replicates AND maintain holds. This packet
  performs no efficiency tuning and licenses no efficiency claim.
- Rationale for extension now: P20E left the restoration signal unreplicated (denominator
  0) on the second TRAIN tranche; the last preregistered same-file tranche (768..1151)
  is the cheapest single-factor continuation — same 3-block cost class, same caps, same
  arms, only new frames — enlarging the descriptive sample (B1 +1024 toward 9/9
  operational blocks if maintain holds) and giving restoration one more chance before
  paying cross-session generalization or redesign cost. Fewer blocks, cleaner attribution.
