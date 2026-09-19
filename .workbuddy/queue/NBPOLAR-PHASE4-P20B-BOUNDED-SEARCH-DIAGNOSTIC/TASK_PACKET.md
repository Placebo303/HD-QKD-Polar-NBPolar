# Phase 4-P20B — bounded search diagnostic (FROZEN, awaiting explicit authorization)

- Tier: Y (decision-gate packet: implementation Stage A + single authorized execution Stage B).
- State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. No implementation, protected read,
  decoder execution, or commit/push is authorized by this file.
- Predecessor: `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE_ACCEPTED_DESCRIPTIVE`
  (P19) + P20A `IMPLEMENTATION_ACCEPTED` (resource passthrough + endpoint instrumentation).
- Strategy parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` ("Next scientific question",
  options 1-3; closed-blocks rule; SCL entry gate; stop rules) and `docs/nbpolar/ROADMAP.md`
  current-priority section.

## 1. Mission

Answer one frozen diagnostic question on independent real development data, changing exactly
one factor:

> With true L1 fixed for diagnosis and prior / construction / disclosure / floor / order /
> kernel / representation / SC decoder all frozen, does a preregistered bounded search find a
> present complete-block candidate that greedy SC misses — or does the bounded negative hold?

This is strategy option 3. Options 1 (L2 disclosure backoff) and 2 (alternative L2
construction) are deferred to §16 and must not enter this packet.

## 2. Background (frozen inputs, not re-argued here)

- P19 (descriptive-accepted): 15/15 `verify_failed` on the same three HOLD blocks; +128 L1
  repaired the two L1 errors (L1 true/true/true) but recovered 0/3 complete blocks; +512 L2
  recovered 0/3; true-L1-conditioned L2 recovered 0/3. Hard-L1 propagation is not a sufficient
  explanation; L1 SCL is not the default next step.
- P20A (implementation-accepted): `MemoryError` inside L1/L2 SC re-raised to the frozen
  resource-stop path at 3 internal sites; scalar endpoints `l1_exact` / `hard_l2_exact` /
  `oracle_l2_exact` / `pair_exact` (`pair_exact` tag-independent; `exact` tag-verified);
  113 focused tests green; zero protected reads / attempts / claims.
- P18/P19 three blocks (frames 1600..1983 of the registered 1M HOLD split, N=32768) are
  CLOSED diagnostic data.

## 3. Single-factor freeze (normative)

FROZEN (identical for every arm; any deviation is a packet violation, not a tuning choice):

- Prior: frozen Model-F concentration prior path + fixed `1e-15` floor applied before SC.
  Diagnose raw zero-count hits, floor hits + log loss; never retune the floor.
- Construction: frozen P16 order, K1=319 / K2=6492 (base), same N=32768 block formation as
  P18/P19 (loading/block-formation helpers reused read-only).
- Disclosure: frozen base K sets (no +128 L1, no +512 L2, no incremental schedule).
  Per-block leakage identical across arms except preregistered tag-count differences.
- Kernel / representation / transform / SC arithmetic: unchanged; greedy SC (`L=1`
  equivalent) is the baseline arm; no SCL, no new kernel/model/schema.
- Verification: one final Toeplitz tag per block/record under new P20B tag domains;
  verification never selects a candidate.

VARIED (the single factor): bounded search around the frozen SC path, preregistered in
`P20B_FREEZE.md` before Pre-EXECUTE and never changed afterwards:

- Search bound M (max candidates rescored), neighborhood definition (e.g. first-error-layer
  ball / top-M divergent-prefix set — exact definition frozen in Stage A design, one choice
  only), candidate scoring under ONE coherent probability model (same priors/floor as SC,
  no evidence reuse), no tag-guided candidate selection (tags verify once, after search).
- True-L1-fixed diagnosis is recorded for attribution only (oracle arm, deployable=false);
  it does not change the operational disclosure or construction.

## 4. Population and closed-data rule (normative)

- The three P18/P19 HOLD blocks (frames 1600..1983) SHALL NOT select K, floor, order,
  decoder, search bound/neighborhood, or any successful point. No tuning on them, no
  third factor after an inconclusive result.
- Stage B runs on a DECLARED independent real development population: exact source-file
  identity (digest), frame ranges, N, block count, and tag domains frozen in `P20B_FREEZE.md`
  and approved at Pre-EXECUTE. Confirmation on new blocks/sessions is a later packet, never
  this one.
- Recommended development pool (Stage A freeze to confirm or replace with equivalent):
  later HOLD frames outside 1600..1983 from the same registered 1M split, or a declared
  independent session; block count small and fixed (3 blocks at N=32768 mirrors P18/P19
  cost class; more blocks need explicit budget justification in the freeze).

## 5. Preregistered disclosure cap (normative)

- Cap rule: NO increase over the frozen base construction at the same N. Per-block
  key-dependent disclosure equals the P19 `base` class (K1=319/K2=6492 + tags); the freeze
  writes the exact numeric cap (bits) plus public/tag accounting.
- Meaningfulness bar: the cap must sit well below raw input bits (`10*N` per block at N=32768)
  and the freeze must show the ratio. Sample-CE-normalized ratios are reported descriptively
  and are NOT qualification efficiency.
- Recount rule: independent key/public/tag recount, mismatch 0, or the gate BLOCKS.

## 6. Arms (frozen; differ ONLY in search)

- `S0_sc_base`: frozen greedy SC at base disclosure/construction (operational).
- `S1_bounded_search`: §3 bounded search at identical disclosure/construction/prior
  (operational; the single-factor delta).
- `S2_true_l1_diagnostic`: true-L1-conditioned diagnostic (provenance ORACLE, deployable=false,
  excluded from every operational aggregate; never described as a correction result).
- No other arms. Five-file + per-arm checkpointing pattern reused from P18/P19.

## 7. Thresholds and labels (descriptive only)

- Outcome label `TARGET_EMPIRICAL_N32768_DEV_BOUNDED_SEARCH_COMPLETE` iff ALL integrity gates
  (§9) hold — regardless of found-count. Found-count 0 and found-count >0 are both COMPLETE.
- This packet makes NO recovery / FER / Wilson / superiority / qualification / promotion claim.
  A positive (candidate found within bound) is a development signal directing search work; a
  bounded negative licenses disclosure/construction work in a later packet. Neither promotes
  any block, session, or route.
- Status taxonomy frozen: `exact` (tag-verified) vs `verify_failed`, with `undetected`
  isolated (never merged into success/FER), plus `decode_failed` / `nonfinite` /
  `resource_abort` via the P20A path.

## 8. Budget, stop rules, SCL gate

- Single attempt: `attempts_allowed: 1`, `attempts_used: 0` until authorized execution; no
  rerun, no seed change, no bound/neighborhood tuning after preregistration. An execution
  error rerun is allowed only as a recorded repeat of the identical freeze, never as tuning.
- Resource-stop: P20A passthrough authoritative; abort preserves evidence + call/disclosure
  accounting; abort is a BLOCKED result, never success.
- Wall/RSS ceilings frozen in `P20B_FREEZE.md` (P19 class reference: ~186 s wall, ~616 MB RSS
  peak for 27 SC calls / 15 tags at N=32768; P20B freeze scales the ceiling to its declared
  block×arm SC-call/tag budget).
- Strategy stop rules restated as binding: no tuning on closed blocks; no third factor after
  an inconclusive single-factor result; no near-raw disclosure feasibility claim; no
  oracle-as-operational; no population-reliability inference before an independent-session gate;
  if the frozen cap cannot recover independent development blocks, record the bounded negative
  and revisit L2 model/representation before raising N or list width.
- SCL entry gate UNCHANGED (all five conditions in the strategy doc must still be shown;
  this diagnostic informs conditions 1-3 but unlocks nothing by itself).

## 9. Evidence matrix and accounting (Stage B, all frozen in P20B_FREEZE.md)

- Root: `.workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/bounded_search_diagnostic/`
  (exactly five files, created pre-open; per-arm checkpointing; one content open per
  protected input; no reopen/rerun). Root must be ABSENT at Pre-EXECUTE.
- Per-record separation (P20A endpoints): `l1_exact`, `hard_l2_exact`, `oracle_l2_exact`,
  `pair_exact`, `exact`, first error coordinate + layer, raw zero-count hits, `1e-15` floor
  hits + log loss, true-H-conditioned vs candidate-H-conditioned L2 NLL, outcome taxonomy.
- Accounting: key/public/tag disclosure + independent recount (mismatch 0); SC-call counts
  (L1/L2/search-rescore split) and tag-invocation counts exact; block SER/NLL; wall/RSS.
- Integrity gates (all true or BLOCKED): predecessor digest match; manifest counts;
  preconditions 7/7 (or frozen equivalent); consumption reads 1/1 + attempt 1/1 at first
  protected open; SC/tag count identities; recount 0; endpoint-schema check; oracle
  isolation; five-file inventory; resource accounting on abort path.

## 10. Commands (exact argv frozen in Stage A / P20B_FREEZE.md)

- Stage A (injected only, authorized separately): `.venv/bin/python -m pytest
  comparison_bench/tests/test_nbpolar_<bounded_search outreach files> -p no:cacheprovider`
  using injected/synthetic inputs and a fresh additive `workspace/p20b/<uuid>/` temp root.
  Zero protected opens (audit required). Safe smoke per `AGENT_PROJECT_MEMORY.md` §4 stays valid.
- Stage B execution command: named in Stage A design and frozen verbatim in `P20B_FREEZE.md`
  (thin runner reusing P18 loading/block formation + P16 operational helpers read-only; new
  tag domains; hardcoded arms, not CLI-tunable). NOT AUTHORIZED until independent Pre-EXECUTE
  PASS + pasted Stage-B authorization. Forbidden by default: `longrun_*`, `minrerun_*`,
  `routeA_*`, `experiments/run_e2e_pipeline.py` on raw data, full sweeps.
- Read-only verify: reviewer recomputes §9 identities from artifacts; never `git show HEAD:`
  blobs for evidence paths (P19 lesson).

## 11. Products

- Stage A: thin runner + focused injected tests + `P20B_FREEZE.md` + `P20B_IMPLEMENTATION_NOTES.md`
  (exact files, diffs, test commands/results, frozen bound/neighborhood/model/population/cap/
  command/budget). No protected reads, no output root.
- Stage B (only after authorization): evidence root (§9) + `OPERATOR_RETURN.md` (+ freeze,
  `PRE_EXECUTE_REVIEW.md`, `PRE_RESULT_REVIEW.md`, `MAIN_THREAD_ACCEPTANCE.md` at their gates).
- OpenSpec P20B delta: `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20b/spec.md`
  + `tasks.md` P20B section (same umbrella change as P18/P19/P20A; see §15).

## 12. Allowed work

- New thin bounded-search diagnostic runner + focused injected tests (temporary roots only).
- Read-only reuse (no logic change) of predecessor helpers by filename:
  `operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py` (+ `construction.py`, `prior.py`, `sc.py` contracts as called).
- P20B OpenSpec delta + packet docs + freeze/return/review files + Stage-B evidence root
  (root only after Stage-B authorization).

## 13. Forbidden work

- Any protected TRAIN/HOLD/VAL/EVAL/raw read, stat, or open before Stage-B authorization;
  any decoder execution before Pre-EXECUTE PASS + pasted authorization.
- Any change to GF32/transform/SC arithmetic, prior/floor, construction/order/K, disclosure
  sets, tag scheme semantics, outcome precedence, accepted evidence roots, or
  `src/` + `experiments/` + `tools/` frozen baseline.
- No SCL / new kernel / new model / new schema; no K/floor/order/decoder/success-point
  selection on the closed three blocks; no second factor (disclosure backoff or alternative
  construction) inside this packet.
- No overwrite under `results/` or `comparison_bench/outputs_comparison/`; no commit/push;
  no self-acceptance; no P20C scope creep.

## 14. Acceptance IDs

- `P20B-R1`: prior/construction/disclosure/floor/order/kernel/representation/SC frozen
  identical across arms; only the preregistered bounded search varies.
- `P20B-R2`: closed three blocks select nothing; development population independently
  declared, digest-pinned, Pre-EXECUTE-approved; confirmation deferred to a later packet.
- `P20B-R3`: disclosure cap preregistered at frozen base (no increase), ratio-vs-raw shown,
  recount mismatch 0; CE ratios never called efficiency.
- `P20B-R4`: search bound M + neighborhood + coherent single-model scoring frozen before
  execution, unchanged after; no tag-guided selection, no evidence reuse.
- `P20B-R5`: L1 / hard-L2 / oracle-L2 / pair endpoints separated per §9; `undetected`
  isolated; oracle arm never operational.
- `P20B-R6`: one-shot Tier-Y semantics — single attempt, no rerun/tuning; resource aborts
  via P20A path with accounting preserved; stop rules + SCL gate intact.
- `P20B-R7`: independent Pre-EXECUTE + Pre-RESULT reviews recorded; main-thread acceptance
  owns the label; descriptive-only, no FER/qualification/promotion language.
- `P20B-R8`: Stage-A suites green on injected data with zero protected opens; no
  commit/push; frozen dirs byte-untouched except the §12 manifest.

## 15. Return conditions

Per `AGENTS.md` §10.1 exactly two operator return conditions: (a) ALL IDs `P20B-R1..R8`
(stage-appropriately) complete with changed files + exact commands/results + artifact
inventory; or (b) a concrete blocker with failing command, exact error/traceback, attempted
remedies, and the ONE decision needed from the main thread. "Still incomplete" is not a
completion report. The operator never marks its own work accepted and never authorizes
Stage B.

## 16. Deferred options (not in this packet)

- P20C candidate — strategy option 1: fixed order + preregistered L2 disclosure backoff on
  independent development data. Needs P20B's search answer first (if SC misses present
  candidates, extra disclosure burns budget without diagnosing search).
- P20D candidate — strategy option 2: fixed disclosure + ONE preregistered alternative L2
  construction. Needs P20B's bounded negative first (otherwise construction redesign is
  unconstrained tuning with extra degrees of freedom).
- Rationale for option 3 first: strictest isolation (zero disclosure/construction change, so
  the cap-meaningfulness debate is moot), cheapest discriminator (compute-bounded, no leakage
  expansion), and directly resolves P19's open ambiguity (true-L1-fixed L2 still failed:
  search miss vs information lack) before spending the disclosure budget or redesigning order.
