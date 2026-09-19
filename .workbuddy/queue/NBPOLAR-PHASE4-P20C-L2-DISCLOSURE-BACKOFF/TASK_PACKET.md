# Phase 4-P20C — L2 disclosure backoff (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: implementation Stage A + single authorized execution Stage B).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read,
  decoder execution, or commit/push is authorized by this file.
- Predecessors: `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (P19) + P20A `IMPLEMENTATION_ACCEPTED` (resource passthrough + endpoint instrumentation)
  + `TARGET_EMPIRICAL_N32768_DEV_BOUNDED_SEARCH_COMPLETE_ACCEPTED_DESCRIPTIVE` (P20B).
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` ("Next scientific question",
  options 1-3; closed-blocks rule; SCL entry gate; stop rules) and `docs/nbpolar/ROADMAP.md`
  current-priority section.
- Gate discipline: the user's standing long-horizon authorization ("proceed at least five
  rounds") does NOT collapse Tier-Y gates. Stage A and Stage B each need their own explicit
  pasted authorization text; this packet authorizes neither.

## 1. Mission

Answer one frozen development question on independent real development data, changing exactly
one factor:

> With P16 order fixed and prior / construction-order / floor / kernel / representation /
> SC decoder all frozen, does ONE preregistered, practically meaningful L2 disclosure step
> recover complete low layers on independent real development data — or does the bounded
> negative hold?

This is strategy option 1. Option 2 (alternative L2 construction) is deferred to §16 and
must not enter this packet. Option 3 (bounded search) is answered descriptively by P20B
and must not be re-run or extended here.

## 2. Background (frozen inputs, not re-argued here)

- P19 (descriptive-accepted): 15/15 `verify_failed` on the three closed HOLD blocks; +128 L1
  repaired the two L1 errors but recovered 0/3 complete blocks; the registered +512 L2 step
  recovered 0/3; true-L1-conditioned L2 recovered 0/3. The old +512 disclosure point is a
  closed-block observation and SHALL NOT be reused as a success basis.
- P20A (implementation-accepted): `MemoryError` inside L1/L2 SC re-raised to the frozen
  resource-stop path at 3 internal sites; scalar endpoints `l1_exact` / `hard_l2_exact` /
  `oracle_l2_exact` / `pair_exact` (`pair_exact` tag-independent; `exact` tag-verified);
  113 focused tests green; zero protected reads / attempts / claims.
- P20B (descriptive-accepted): bounded negative holds within M=8 / `P20B-NBHD-1`. S1 selected
  the greedy candidate on all three DEV blocks (`selected_source` greedy, dNLL 0.0,
  `search_better_count` 0/3); per-arm exact S0 0/3, S1 0/3, S2 0/3; S0 L1 F/T/T. Within the
  preregistered bound, search-miss is NOT the explanation; information insufficiency remains
  the primary hypothesis. P20B consumed the full VAL pool (frames 1200..1599 declared).
- Closed data: the three P18/P19 HOLD blocks (frames 1600..1983) are CLOSED diagnostic data.
  The P20B VAL range (frames 1200..1599) is a CONSUMED development pool (same-block tuning
  across packets is forbidden, §4).

## 3. Single-factor freeze (normative)

FROZEN (identical for every arm; any deviation is a packet violation, not a tuning choice):

- Prior: frozen Model-F concentration prior path + fixed `1e-15` floor applied before SC.
  Diagnose raw zero-count hits, floor hits + log loss; never retune the floor.
- Construction order: frozen P16 order (permutation fixed by the accepted construction file;
  digest pinned in the Stage-A freeze). K1=319 base L1 set unchanged on every arm.
- Kernel / representation / transform / SC arithmetic: unchanged; greedy SC is the baseline;
  no SCL, no new kernel/model/schema.
- Verification: one final Toeplitz tag per block/record under NEW P20C tag domains;
  verification never selects a candidate.

VARIED (the single factor): L2 disclosure ladder, preregistered in `P20C_FREEZE.md` before
Pre-EXECUTE and never changed afterwards:

- Exactly ONE operational step: `B1` discloses ΔK2 = +1024 L2 symbols beyond the frozen base
  (K2 6492 → 7516; K_total 6811 → 7835) by FROZEN-ORDER-PREFIX EXTENSION — the disclosed L2
  set is the first 7516 positions of the frozen P16 L2 order. Positions are fixed by the
  construction file, never selected on closed blocks, the consumed VAL pool, or DEV data.
- Step semantics (why this is not brainless disclosure): each ladder step asks exactly one
  question — "does THIS step restore the complete low layer". A restoring step STOPS the
  ladder (no chasing higher disclosure inside this packet); a non-restoring step records a
  bounded negative that licenses P20D construction work, never a further disclosure hike.
- Why +1024 and why only one step: +1024 doubles P19's probed +512 increment, so it is a
  genuinely new information point, not a repeat of a failed closed-block point; it stays a
  moderate, practically meaningful increment (§5 ratio). A second operational step (`B1b`)
  is DELIBERATELY ABSENT: two steps would double disclosure spend and invite post-hoc
  step-picking after the fact, and the strategy stop rule forbids adding factors after an
  inconclusive result — fewer steps, cleaner attribution. (No `B1b` may be added without a
  new packet and a written necessity argument.)

## 4. Population and closed/consumed-data rule (normative)

- The three P18/P19 HOLD blocks (frames 1600..1983) SHALL NOT select K, floor, order,
  decoder, disclosure step, or any successful point. No tuning on them, no third factor
  after an inconclusive result.
- The P20B VAL pool (frames 1200..1599, INCLUDING the declared-unused remainder 1584..1599)
  is CONSUMED and SHALL NOT supply P20C blocks. Cross-packet same-pool tuning is forbidden.
- Stage B runs on a DECLARED independent real development population: exact source-file
  identity (digest), frame ranges, N, block count, and tag domains frozen in `P20C_FREEZE.md`
  and approved at Pre-EXECUTE. Confirmation on new blocks/sessions is a later packet, never
  this one.
- Recommended development pool (Stage A freeze to confirm or replace with a written
  equivalent + justification): the same-file TRAIN range frames 0..1199 (inferred from the
  P20B-verified 2000-frame inventory — 1200 TRAIN + 400 VAL + 400 HOLD with VAL 1200..1599
  and HOLD 1600..1999; Stage A re-verifies via JSON-manifest provenance reads ONLY, never a
  content open), using blocks `0..127`, `128..255`, `256..383` at N=32768 (3 x 128 frames,
  mirroring the P18/P19/P20B cost class); remainder frames 384..1199 recorded never used.
- Evidence-reuse isolation argument for the TRAIN-pool recommendation (Stage A restates it in
  the freeze; Pre-EXECUTE adjudicates): the Model-F prior is a FROZEN aggregate concentration
  model, identical across arms, never refit or reselected on DEV; the comparison is an
  INTER-ARM differential (base vs +1024 vs oracle) on DEV-specific frames, not a prior
  effect; no K/floor/order/step selection touches DEV or closed/consumed ranges. If
  Pre-EXECUTE rejects the isolation, Stage A must substitute a declared independent session
  (or other registered split) with the same 3-block cost class — same packet, new freeze
  values, re-review.
- Fail-closed overlap gate (frozen in the runner, checked first): DEV ranges must overlap
  NEITHER 1600..1983 NOR 1200..1599, else the run refuses before any protected content open.

## 5. Preregistered disclosure cap (normative)

- Cap rule: the cap INCREASES by design here (this is a disclosure-backoff packet), so the
  zero-growth debate is inapplicable — instead the cap is preregistered per arm, frozen
  before Pre-EXECUTE, and each step must sit FAR below raw input bits with its ratio shown.

| arm | K1 | K2 | key-dependent bits/block | public bits/tag |
|---|---|---|---|---|
| B0_sc_base (operational) | 319 | 6492 | 34119 = 5*6811+64 | 327743 = 10*32768+63 |
| B1_L2plus (operational) | 319 | 7516 | 39239 = 5*7835+64 | 327743 |
| B2_true_l1_diagnostic (oracle) | 0 | 6492 | 32524 = 5*6492+64 | 327743 |

- Planned totals if all invoked: key 317646 = 3*34119 + 3*39239 + 3*32524
  (operational 220074 + oracle 97572); public 2949687 = 9*327743.
- Meaningfulness bar: base 34119/327680 ≈ 10.41% and B1 39239/327680 ≈ 11.98% of raw input
  bits (10*N per block at N=32768) — both far below raw. Sample-CE-normalized ratios are
  reported descriptively and are NOT qualification efficiency.
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate BLOCKS.

## 6. Arms (frozen; differ ONLY in L2 disclosure)

- `B0_sc_base`: frozen greedy SC at base disclosure/construction (operational; 2 SC + 1
  P20C-domain tag per block).
- `B1_L2plus`: frozen greedy SC at base + the ONE preregistered +1024 L2 step via §3
  order-prefix extension, all else identical (operational; the single-factor delta; 2 SC +
  1 P20C-domain tag per block).
- `B2_true_l1_diagnostic`: true-L1-conditioned diagnostic at BASE disclosure (provenance
  ORACLE, deployable=false, excluded from every operational aggregate; never described as
  a correction result; 1 SC + 1 P20C-domain tag per block).
- No other arms. Run block-major (B0, B1, B2) per DEV block; checkpoint after every
  (arm, block) record; 9 records total. Five-file + per-arm checkpointing pattern reused
  from P18/P19/P20B.

## 7. Thresholds and labels (descriptive only)

- Outcome label `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE` iff ALL
  integrity gates (§9) hold — regardless of exact-count. Any exact count (including 0/9
  and any partial restoration) is COMPLETE when integrity holds.
- This packet makes NO recovery / FER / Wilson / superiority / qualification / promotion
  claim. A restoring step is a development signal directing disclosure work; a bounded
  negative (0 restored at +1024) licenses P20D construction work. Neither promotes any
  block, session, or route.
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`, with `undetected`
  isolated (never merged into success/FER), plus `decode_failed` / `nonfinite` /
  `resource_abort` via the P20A path. P20A four-endpoint separation
  (`l1_exact` / `hard_l2_exact` / `oracle_l2_exact` / `pair_exact`) recorded per record.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized execution; no
  rerun, no seed change, no disclosure-step tuning after preregistration. An execution
  error rerun is allowed only as a recorded repeat of the identical freeze, never as tuning.
- SC/tag budget: 15 SC calls (3 blocks x (2+2+1)) and 9 tags; derived per-record
  recomputation must equal the counters, else BLOCKED.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence + call/disclosure
  accounting; abort is a BLOCKED result, never success.
- Wall/RSS ceilings frozen in `P20C_FREEZE.md` (P20B class reference: ~111 s wall, ~541 MB
  RSS peak for 15 SC calls / 9 tags at N=32768; P20C plans the identical 15 SC / 9-tag
  budget, strictly inside the same class; external timeout + virtual/RSS caps + single
  thread frozen as in P20B §10).
- Strategy stop rules restated as binding: no tuning on closed blocks; no reuse of the
  consumed VAL pool; no third factor after an inconclusive single-factor result; no
  near-raw disclosure feasibility claim; no oracle-as-operational; no
  population-reliability inference before an independent-session gate; if the frozen +1024
  step cannot restore independent development blocks, record the bounded negative and
  revisit L2 model/representation (P20D) before raising N or list width.
- SCL entry gate UNCHANGED (all five strategy conditions must still be shown; this
  backoff informs the information axis but unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage B, all frozen in P20C_FREEZE.md)

- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF/l2_disclosure_backoff/`
  (exactly five files, created pre-open; per-(arm, block) checkpointing; one content open
  per protected input; no reopen/rerun). Root must be ABSENT at Pre-EXECUTE.
- Five files: `frozen_plan.json`, `input_and_predecessor_identity.json`,
  `per_block_arm_outcomes.jsonl` (9 records at completion), `aggregate_summary.json`,
  `report.md`. Scalar-only: never counts, sampled symbols, truth vectors, decoded
  labels/keys, metric planes, raw rows, per-arm orders, tag seeds or RNG state.
- Per-record separation (P20A endpoints): `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`,
  `pair_exact`, `exact`, first error coordinate + layer, raw zero-count hits, `1e-15` floor
  hits + log loss, true-H-conditioned vs candidate-H-conditioned L2 NLL, outcome taxonomy,
  plus B1 disclosure fields (ΔK2=1024 applied, order-prefix positions fixed, key-bit delta
  +5120 vs base).
- Accounting: key/public/tag disclosure + independent recount (mismatch 0); SC-call counts
  (L1/L2 split) and tag-invocation counts exact; block SER/NLL; wall/RSS.
- Integrity gates (all true or BLOCKED; frozen order in the freeze): predecessor
  construction identity; split manifest identity; dev block range identity (disjoint from
  BOTH 1600..1983 and 1200..1599, overlap pre-check first); target population contract
  (7/7 preconditions or frozen equivalent); dev population exact; blocks exact with
  declared remainder; nine records exact; SC calls exact (derived 15); tags exact
  (derived 9); order-prefix disclosure positions fixed within registered arms; oracle
  isolation; buckets disjoint exhaustive; undetected zero; nonfinite zero; truth isolation;
  disclosure recount exact; one open per protected input; input stat unchanged;
  no unregistered access; resource limits met and no abort.

## 10. Commands (exact argv frozen in Stage A / P20C_FREEZE.md)

- Stage A (injected only, authorized separately): `.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_<l2_backoff outreach files> -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20c/<uuid>/` temp root.
  Zero protected opens (audit required). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage B execution command: named in Stage A design and frozen verbatim in `P20C_FREEZE.md`
  (thin runner reusing P18 loading/block formation + P16 operational helpers read-only; new
  P20C tag domains; three hardcoded arms with the +1024 prefix-extension pinned, not
  CLI-tunable). NOT AUTHORIZED until independent Pre-EXECUTE PASS + pasted Stage-B
  authorization. Forbidden by default: `longrun_*`, `minrerun_*`, `routeA_*`,
  `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git show HEAD:`
  blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: thin runner + focused injected tests + `P20C_FREEZE.md` +
  `P20C_IMPLEMENTATION_NOTES.md` (exact files, diffs, test commands/results, frozen
  step/population/cap/command/budget). No protected reads, no output root.
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md` (+ freeze,
  `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md` at their gates).
- OpenSpec P20C delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20c/spec.md`
  + `tasks.md` P20C section (same umbrella change as P18/P19/P20A/P20B; no new top-level change).

## 12. Allowed work

- New thin L2-disclosure-backoff runner + focused injected tests (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py` (+ `construction.py`, `prior.py`, `sc.py` contracts as called).
- P20C OpenSpec delta + packet docs + freeze/return/review files + Stage-B evidence root
  (root only after Stage-B authorization).

## 13. Forbidden work

- Any protected TRAIN/HOLD/VAL/EVAL/raw read, stat, or open before Stage-B authorization;
  any decoder execution before Pre-EXECUTE PASS + pasted authorization.
- Any change to GF32/transform/SC arithmetic, prior/floor, construction order (except the
  frozen §3 prefix-extension rule itself), tag scheme semantics, outcome precedence,
  accepted evidence roots, or `src/` + `experiments/` + `tools/` frozen baseline.
- No K/floor/order/decoder/step/success-point selection on the closed three blocks or the
  consumed VAL pool; no second factor (alternative construction) inside this packet; no
  second disclosure step (`B1b`) without a new packet.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push;
  no self-acceptance; no P20D scope creep.

## 14. Acceptance IDs

- `P20C-R1`: prior/construction-order/floor/kernel/representation/SC frozen identical across
  arms; only the preregistered +1024 L2 prefix-extension step varies.
- `P20C-R2`: closed three blocks select nothing; consumed VAL pool untouched; development
  population independently declared, digest-pinned, isolation-argued, Pre-EXECUTE-approved;
  confirmation deferred to a later packet.
- `P20C-R3`: disclosure caps preregistered per arm (34119 / 39239 / 32524 + 327743 public),
  ratios-vs-raw shown (~10.41% / ~11.98%), recount mismatch 0; CE ratios never called efficiency.
- `P20C-R4`: single +1024 step + order-prefix rule frozen before execution, unchanged after;
  no tag-guided selection, no evidence reuse, no post-hoc step-picking.
- `P20C-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9; `undetected`
  isolated; oracle arm never operational.
- `P20C-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning; resource aborts
  via P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20C-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded; main-thread acceptance
  owns the label; descriptive-only, no FER/qualification/promotion language.
- `P20C-R8`: Stage-A suites green on injected data with zero protected opens; no
  commit/push; frozen dirs byte-untouched except the §12 manifest.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs `P20C-R1..R8`
(stage-appropriately) complete with changed files + exact commands/results + artifact
inventory; or (b) a concrete blocker with failing command, exact error/traceback, attempted
remedies, and the ONE decision needed from the main thread. "Still incomplete" is not a
completion report. The operator never marks its own work accepted and never authorizes
Stage B.

## 16. Deferred options (not in this packet)

- P20D candidate — strategy option 2: fixed disclosure + ONE preregistered alternative L2
  construction on independent development data. Needs P20C's backoff answer first (if a
  moderate disclosure step restores blocks, construction redesign is moot; if the bounded
  negative holds at +1024, construction work is then constrained tuning, not open-ended).
- Rationale for option 1 now: P20B's bounded negative (M=8/NBHD-1, greedy selected 3/3,
  dNLL 0.0) removed search-miss as the in-bound explanation, leaving information lack as
  the primary hypothesis — the cheapest next single-factor test is one fixed moderate
  disclosure step, not a construction redesign with extra degrees of freedom.
