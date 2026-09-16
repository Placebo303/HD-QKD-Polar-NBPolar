# Tasks: Phase 4-P0 prior-contract freeze (plan-only; P1 unauthorized)

## P0 freeze work (this change; docs only, no `.py`)

- [x] P0-1: source inventory + provenance map — accepted concentration
  formula, banned per-cell callable/path, `[Alice,Bob]` vs `[Bob,Alice]`
  at every boundary (`design.md` §§1–2).
- [x] P0-2: symbol contract — 5+5 packing, ranges, joint-Bob
  conditioning, P1/P2_true/P2_hat tensors (`design.md` §3).
- [x] P0-3: `SymbolMetric` API — value object + separate helpers,
  log conversion, `-inf`, floor policy, no-APP rule (`design.md` §4).
- [x] P0-4: CAL/DEV/EVAL separation + D1/D2/D3 diagnostics, paired
  identities, failure precedence, truth isolation (`design.md` §5).
- [x] P0-5: 12-gate validation matrix with oracle/ground truth, failure
  category, first diagnostic, blocking scope (`specs/` + contract doc).
- [x] P0-6: architecture handoff — exact module/test names, signatures,
  enums, imports, error semantics, exports (`design.md` §7).
- [x] Alternatives A/B/C with MVP selection + floor/conditioning/
  hard-candidate decisions (`design.md` §6).
- [x] Unauthorized P1 packet prepared at
  `.workbuddy/queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/` (`STATUS.yaml`
  all-false, `phase4_p1_authorized: false`).
- [x] Independent `INDEPENDENT_PHASE4_P0_FREEZE_REVIEW`:
  re-check every cited callable/axis against source, recalculate the
  smoothing formula, trace truth provenance, verify CAL/DEV/EVAL
  isolation, confirm P1 still unauthorized. Self-review is diagnostic
  only. **Do not self-accept.**

## P1 implementation tasks (FROZEN, NOT AUTHORIZED — do not start)

- [ ] P1-1: implement `formal_ir/nbpolar/prior.py` pure adapters per
  `design.md` §7 + P1 packet acceptance IDs.
- [ ] P1-2: implement `tests/test_nbpolar_prior.py` synthetic fixtures +
  independent formula oracle; gates V-P0-01–07 green on synthetic data.
- [ ] P1-3: run the decoder-free synthetic resource smoke and all accepted
  Phase 1-3 regressions without reading CAL or calling SC from the new tests.
- [ ] P1-4: prepare an all-false Phase 4-P2 CAL/DEV packet; do not freeze data
  identities or select a floor in P1.
- [ ] P1-5: independent implementation review + memory triage; return candidate
  or the single earliest blocker.

## Acceptance (P0)

- [x] Every §1–§2 citation resolves to the stated file/callable/line
  and the banned twin is unimportable from the P1 allow-list.
- [x] Asymmetric-counts sentinel is frozen to distinguish `[Alice,Bob]` from its
  transpose; packing round-trips exhaustively over `0..31`.
- [x] Truth-leak sentinels are frozen: mutating Alice truth changes neither
  P1 nor P2_hat; operational surface never imports the oracle helper.
- [x] P1 packet exists but carries no authorization flag; no `.py`,
  data, result, or Phase 1–3 artifact changed; no commit/push.
- [x] Independent review verdict recorded; comments resolved without widening
  scope.

## P3 implementation tasks (Phase 4-P3; frozen packet `NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [x] P3-1: vectorized exhaustive oracle backend in
  `formal_ir/nbpolar/empirical_oracle.py` (mixed-radix enumeration, dense
  batch transform validated against `polar_transform_reference`, contiguous
  slice conditionals) with the literal default path and its 4096 cap
  unchanged; GF32 N=4 supported under a separate vector cap
  (`specs/nbpolar-phase4-p3/spec.md` "interface gates").
- [x] P3-2: `--mode stageb` runner plus `_run_stageb_from_tables` test seam
  in `formal_ir/nbpolar/empirical_diagnostic.py`: single artifact load, B1–B5
  in frozen order, per-case 120 s soft stop and 3600 s total guard, masks
  M1–M5, `resource_abort` bookkeeping, refusal paths, exactly five compact
  output files written at the end, no other writes.
- [x] P3-3: truth-leak sentinel and earliest-layer attribution classifier
  with disjoint per-case accounting (`exact + failed + resource_abort ==
  planned`), impossible/other/nonfinite never merged into exact.
- [x] P3-4: focused `tests/test_nbpolar_empirical_sc.py` additions plus the
  full accepted predecessor suite green; ordinary tests use injected tables
  and temporary roots only and never touch the sibling artifact.
- [x] P3-5: freeze v2 (`P3_STAGEB_FREEZE.md` in the P3 queue dir), the
  SUPERSEDED banner on the stale MVP draft, and this P3 spec/tasks delta;
  this doc authorizes nothing.
- [x] P3-6: independent Pre-EXECUTE review of the frozen command, thresholds,
  seeds, masks, counts, budget and absent root (main thread + reviewer).
- [x] P3-7: exactly one authorized Stage B artifact run with the frozen
  command; the artifact-content attempt is consumed at first content open.
- [x] P3-8: independent Pre-RESULT review, then main-thread adjudication to
  `EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE` or rejection; no FER/leakage/
  key-rate/reconciliation/performance claim either way.

Evidence: `.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/OPERATOR_RETURN.md`
and output root
`.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/empirical_prior_sc_diagnostic/`
(accepted `EMPIRICAL_PRIOR_SC_INTERFACE_ACCEPTED`; interface evidence only).

## P4 implementation tasks (Phase 4-P4; frozen packet `NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [ ] P4-1: implement the single two-layer core module
  `formal_ir/nbpolar/two_layer.py`: explicit injected `[Alice,Bob]` table,
  `derive_p1`/`derive_p2` metric tables, frozen `D1`/`D2`, explicit-RNG block
  sampler, per-arm/per-block Toeplitz seed, causal operational arm and isolated
  oracle arm with no state/APP transfer.
- [ ] P4-2: outcome taxonomy, per-layer sub-buckets, canonical transcript
  events, independent literal recount, truth-isolation sentinel and the
  report-only wrong-L1 `oracle_candidate_divergence` hook.
- [ ] P4-3: frozen CLI gate runner (all nine required flags, absent-root and
  banned-seed refusals, `n <= 256`, budget stop, exactly five compact
  scalar-only files, 13 hard gates persisted as booleans).
- [ ] P4-4: focused `tests/test_nbpolar_two_layer.py` (P4-A01..A09, A11) plus
  the full accepted predecessor suite green; tests use injected/tiny inputs,
  temporary roots and fresh seeds only.
- [ ] P4-5: `P4_FREEZE.md` + `P4_IMPLEMENTATION_NOTES.md` in the packet queue
  directory and this P4 spec/tasks delta; this doc authorizes nothing.
- [ ] P4-6: independent Pre-EXECUTE review of the frozen command, model, sets,
  seeds (including the P6-R1 test-local seed-overlap adjudication), gates,
  budget and absent root (`P4-A12`, main thread + reviewer).
- [ ] P4-7: at most one authorized gate run with the frozen command; the single
  attempt is consumed at the first gate SC call (block 0 operational L1).
- [ ] P4-8: independent Pre-RESULT review, then main-thread adjudication to
  `TWO_LAYER_OPERATIONAL_SC_CANDIDATE` or rejection; no FER/leakage/key-rate/
  reconciliation/performance claim either way.

Evidence (candidate only, gate not yet run):
`.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/P4_FREEZE.md`,
`P4_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/`
is absent and must remain absent until an authorized execution.

Candidate execution evidence (supersedes the absent-root note above): `.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/OPERATOR_RETURN.md`, gate root `.workbuddy/queue/NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC/two_layer_operational_sc_gate/` (exit 0; 13/13 hard gates true; attempt 1/1 consumed; candidate only, no OpenSpec box checked).

## P5 implementation tasks (Phase 4-P5; frozen packet `NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [x] P5-1: implement the single statistic/runner wrapper
  `formal_ir/nbpolar/penalty_gate.py`: dependent injected `[Alice,Bob]` table
  with the per-high-value profile kernel, pre-decoder `p2_maxdiff` guard,
  explicit-RNG dependent sampler, paired four-cell classification on the
  accepted `run_two_layer_block`, exact-binomial lower bound and the frozen
  two registered outcome labels.
- [x] P5-2: integrity gates, frozen CLI (eight required flags, absent-root and
  consumed-seed refusals) and exactly five compact scalar-only output files at
  the frozen root.
- [x] P5-3: focused `tests/test_nbpolar_penalty_gate.py` plus the full accepted
  NB-Polar predecessor suite green; tests use injected/tiny inputs, temporary
  roots and fresh seeds only and never the gate seeds.
- [x] P5-4: `P5_FREEZE.md` + `P5_IMPLEMENTATION_NOTES.md` in the packet queue
  directory and this P5 spec/tasks delta; this doc authorizes nothing.
- [x] P5-5: independent Pre-EXECUTE review of the frozen point, table,
  D1/D2, seeds/masters, gates, discriminator, budgets and absent root.
- [x] P5-6: exactly one authorized 384-pair attempt with the frozen command;
  the single attempt is consumed at the first gate L1 SC call (stream 0,
  block 0), with no rerun/seed/model/K/threshold change.
- [x] P5-7: independent Pre-RESULT review of thresholds, cell accounting,
  `undetected` isolation, per-source breakdown and disclosure accounting.
- [x] P5-8: main-thread adjudication to
  `HARD_L1_CONDITIONING_PENALTY_CANDIDATE` /
  `HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED` / `BLOCKED(<earliest gate>)`;
  no FER/leakage/key-rate/reconciliation/performance claim either way.

Evidence (candidate only, gate not run):
`.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/P5_FREEZE.md`,
`P5_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`
is absent and must remain absent until an authorized execution.

Accepted execution evidence: `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/OPERATOR_RETURN.md`, gate root `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/` (exit 0; 384/384; 10/10 hard gates true; cells 233/144/0/7; X=144; L=0.3338842736427746>0.30; attempt 1/1 consumed; main-thread bounded acceptance recorded).

## P6 implementation tasks (Phase 4-P6; frozen packet `NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [x] P6-1: implement the single adaptive/static core+CLI module
  `formal_ir/nbpolar/adaptive_l1.py`: reused strong-profile dependent table and
  sampler, nested `D1` ladder `[45,60,72,112]`, fixed `K2=140` `D2`, level
  domain-separated Toeplitz seeds, the static `K1=112` endpoint arm, the
  adaptive restart ladder with tag/feedback/impossible semantics, executed
  disclosure accounting, independent literal recount and the union bound.
- [x] P6-2: integrity + scientific gates, frozen CLI (eight required flags,
  absent-root and consumed-seed refusals, 640-pair shape) and exactly five
  compact scalar-only output files at the frozen root.
- [x] P6-3: focused `tests/test_nbpolar_adaptive_l1.py` covering nested sets,
  restart/no-state-reuse, tag accept/advance, nonterminal/terminal impossible
  semantics, label assembly, truth-isolation sentinels, accounting at every
  termination class, transcript recount/tamper, paired block identity and the
  no-production-invocation rule; plus the full accepted NB-Polar predecessor
  suite green with injected/tiny inputs, temporary roots and fresh seeds only.
- [x] P6-4: `P6_FREEZE.md` + `P6_IMPLEMENTATION_NOTES.md` in the packet queue
  directory and this P6 spec/tasks delta; this doc authorizes nothing.
- [x] P6-5: independent Pre-EXECUTE review of the frozen point, schedule,
  table, D1/D2, seeds/masters, restart/tag/feedback semantics, accounting,
  gates, budgets, command and absent root.
- [x] P6-6: exactly one authorized 640-pair attempt with the frozen command;
  the single attempt is consumed at the first scientific SC call (stream 0,
  block 0), with no rerun/seed/model/K/threshold change.
- [x] P6-7: independent Pre-RESULT review of thresholds, paired cells,
  `undetected` isolation, per-arm/per-source accounting, union bound and the
  exact integer leakage comparison against the five artifacts.
- [x] P6-8: main-thread adjudication to
  `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE` /
  `ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED` / `BLOCKED(<earliest gate>)`;
  no FER/leakage/key-rate/reconciliation/performance claim either way.

Evidence (candidate only, gate not run):
`.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/P6_FREEZE.md`,
`P6_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate/`
is absent and must remain absent until an authorized execution.

Execution evidence: the original gate ran once and retained label
`BLOCKED(d1_exactly_nested_and_d2_disclosed_once)` with attempt 1/1 consumed.
P6-R1 then read-only revalidated the unchanged root after the compound-identity
repair: 12/12 integrity and 4/4 scientific gates true, independent review
PASS_WITH_COMMENTS, and main-thread bounded acceptance recorded as
`ADAPTIVE_HARD_L1_DISCLOSURE_ACCEPTED`. The original label/root remain intact.

### P6-R1 rev note (2026-09-13)

Rev note for the Δ successor `NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX`. Sole
correction: every future transcript event carries the public scalar
`stream_seed` identity and the `d1_exactly_nested_and_d2_disclosed_once` gate
groups L2 disclosures by the compound `(stream_seed, block_index, arm)` identity
instead of the previous per-stream `(block_index, arm)`. The pre-R1 checker key
collided across the five frozen streams (they share block indices 0..127), so
the executed D2 behaviour — one L2 disclosure per arm/block, 1280/1280 — was
scored false; the independent `PRE_RESULT_REVIEW.md` §4 diagnosed this as a
gate-check implementation defect, not a contract violation.

No scientific constant, threshold, disclosure formula, decoder path, outcome
taxonomy, seed/master, K1/K2 level, accounting rule or artifact schema changes.
The original P6 evidence root and its persisted `BLOCKED` field remain
immutable. A read-only revalidation helper recomputes the 12 integrity and 4
scientific gates from the stored five files; if every corrected gate is true it
returns the successor candidate label `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`
without consuming a new attempt, sample, seed or decoder call.

Candidate evidence (no box checked): `.workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/revalidation.json`, `INDEPENDENT_REVALIDATION_REVIEW.md` (PASS_WITH_COMMENTS) and `OPERATOR_RETURN_R1.md`; candidate label `ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`, main-thread acceptance pending.

## P7 implementation tasks (Phase 4-P7; frozen packet `NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [x] P7-1: add the P7 spec delta
  (`specs/nbpolar-phase4-p7/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [x] P7-2: implement the single core+CLI module
  `formal_ir/nbpolar/target_construction.py`: accepted
  `load_v25_channel_counts` source-`1M` load with a stat-only size check and
  absent-root refusal before the content open, the floor-only support rule,
  the frozen entropy/column preconditions, pooled empirical L1/oracle-L2
  `genie_conditionals` orders with BEC `epsilon_l=H_l/5` controls, the two
  paired candidate-conditioned DEV arms, the accepted outcome buckets, the
  Toeplitz accounting/recount and the frozen labels.
- [x] P7-3: integrity + scientific gates, the frozen eleven-flag CLI with no
  production default, and exactly five compact scalar-only output files at the
  frozen root.
- [x] P7-4: focused `tests/test_nbpolar_target_construction.py` covering
  floor/renormalization and exact entropy reconstruction, axes/packing,
  zero-column refusal, injected tiny sampler frequencies, per-stream/pooled
  construction, order freeze before DEV, empirical/BEC arm separation,
  candidate-conditioned L2 truth isolation, buckets, disclosure/tag accounting
  and recount, and the no-artifact/no-production-invocation rule; plus the
  full accepted 217-test NB-Polar predecessor suite green with injected/tiny
  inputs, temporary roots and fresh test seeds only.
- [x] P7-5: `P7_FREEZE.md` + `P7_IMPLEMENTATION_NOTES.md` in the packet queue
  directory with the frozen point, constants, verbatim command, absent root,
  five-file schema, gates, accounting, attempt/read consumption point,
  no-rerun rule, budgets and forbidden-path proof.
- [x] P7-6: independent Pre-EXECUTE review of source identity, support formula,
  entropy literals, streams, thresholds, truth boundary, tests, resource
  limits, accounting and target absence.
- [x] P7-7: exactly one authorized 640-pair attempt with the frozen command;
  the single artifact read and scientific attempt are consumed at the first
  NPZ content open, with no rerun/seed/order/K/floor/threshold change.
- [x] P7-8: independent Pre-RESULT review of input entropies, construction
  statistics, outcomes, Wilson bound, accounting and every gate recomputed from
  the five artifacts.
- [x] P7-9: main-thread adjudication to
  `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE` /
  `TARGET_EMPIRICAL_CONSTRUCTION_NOT_CONFIRMED` / `BLOCKED(<earliest gate>)`;
  no held-out/real FER, efficiency, key-rate, scaling, qualification or
  promotion claim either way.

Evidence (implementation only; gate not run): `P7_FREEZE.md`,
`P7_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Candidate evidence (no box checked): `P8_FREEZE.md`, `P8_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS; seed-coincidence ratified FRESH), `PRE_RESULT_REVIEW.md` (PASS_WITH_COMMENTS), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/rate_screen_confirm/` (five files; read 1/1 + attempt 1/1 consumed); candidate label `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE`, main-thread acceptance pending.

Candidate evidence (no box checked): `P7_FREEZE.md`, `P7_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS; review item #1 entropy-functional semantics ratified), `PRE_RESULT_REVIEW.md` (PASS), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/target_construction_gate/` (five files; read 1/1 + attempt 1/1 consumed); candidate label `TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE`, main-thread acceptance pending.

## P8 implementation tasks (Phase 4-P8; frozen packet `NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [x] P8-1: add the P8 spec delta
  (`specs/nbpolar-phase4-p8/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [x] P8-2: implement the single core+CLI module
  `formal_ir/nbpolar/target_rate.py`: accepted P7 pooled empirical
  L1/L2 orders with the frozen order-identity digest and BEC-surrogate
  check before the content open, the accepted `load_v25_channel_counts`
  source-`1M` load with a stat-only size check and absent-root refusal,
  the exact P7 floor-only support rule and entropy/column preconditions,
  the frozen 35-point shared-block SCREEN with deterministic
  lexicographic selection, the disjoint CONFIRM with paired BEC control
  at the selected point only, the accepted outcome buckets, the Toeplitz
  accounting/recount and the frozen labels.
- [x] P8-3: integrity + scientific gates, the frozen twelve-flag CLI with
  no production default, and exactly five compact scalar-only output
  files at the frozen root.
- [x] P8-4: focused `tests/test_nbpolar_target_rate.py` covering grid
  completeness/shared-block identity, Wilson 187/192-vs-188/192 boundary
  with the independently verified equivalence, deterministic selection
  including ties/no eligible point, SCREEN/CONFIRM isolation,
  selected-only confirmation, empirical/BEC same-K pairing, truth
  isolation, buckets, partial/full accounting and recount, and the
  no-artifact/no-production-invocation rule; plus the full accepted
  228-test NB-Polar predecessor suite green with injected/tiny inputs,
  temporary roots and fresh test seeds only.
- [x] P8-5: `P8_FREEZE.md` + `P8_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the frozen point, constants, verbatim command,
  absent root, five-file schema, gates, accounting, attempt/read
  consumption point, no-rerun rule, budgets and forbidden-path proof.
- [x] P8-6: independent Pre-EXECUTE review of the complete selection
  rule, streams, support/order identity, thresholds, truth boundary,
  tests, resource limits, accounting, attempt point and target absence.
- [x] P8-7: exactly one authorized SCREEN+CONFIRM attempt with the frozen
  command; the single artifact read and scientific attempt are consumed
  at the first NPZ content open, with no rerun/seed/grid/order/floor/
  threshold change.
- [x] P8-8: independent Pre-RESULT review of the 35-point SCREEN, Wilson
  eligibility, deterministic selection, independent CONFIRM, paired
  cells, accounting and every gate recomputed from the five artifacts.
- [x] P8-9: main-thread adjudication to
  `TARGET_EMPIRICAL_RATE_POINT_CANDIDATE` /
  `TARGET_EMPIRICAL_RATE_POINT_NOT_CONFIRMED` /
  `TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT` / `BLOCKED(<earliest gate>)`;
  no held-out/real FER, efficiency, key-rate, scaling, qualification or
  promotion claim either way.

Evidence (implementation only; gate not run): `P8_FREEZE.md`,
`P8_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/rate_screen_confirm/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

## P9 implementation tasks (Phase 4-P9; frozen packet `NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [x] P9-1: add the P9 spec delta
  (`specs/nbpolar-phase4-p9/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [x] P9-2: implement the delta-only successor in
  `formal_ir/nbpolar/target_rate.py`: required closed-choice CLI field
  `--gate-id p9-lower-rate-boundary` selecting only the P9 protocol name,
  tag-domain prefix and result labels, the frozen P9 56-point grid and
  output root; preserve the existing P8 behavior byte-for-byte with no
  SC/prior/construction/tag/outcome/support/truth/accounting change and
  no modification of accepted P7/P8 evidence roots.
- [x] P9-3: integrity + scientific gates, the frozen thirteen-flag CLI
  with no production default, and exactly five compact scalar-only output
  files at the frozen root.
- [x] P9-4: focused `tests/test_nbpolar_target_rate.py` additions covering
  56-point grid completeness with `(0,0)` and the `(8,80)` anchor, zero-K
  behavior, shared-block identity across all 56, eligibility boundary
  187/192-vs-188/192, deterministic selection including ties/no eligible
  point, SCREEN/CONFIRM isolation with prior-stream disjointness,
  selected-only same-K confirmation, empirical/BEC pairing, buckets/truth
  isolation, partial/full accounting and recount, P9 domain separation,
  absent root, gate-id closed-choice with P8 preservation, and the
  no-artifact/no-production-invocation rule; plus the full accepted
  240-test NB-Polar predecessor suite green with injected/tiny inputs,
  temporary roots and fresh test seeds only.
- [x] P9-5: `P9_FREEZE.md` + `P9_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the frozen point, constants, verbatim command,
  absent root, five-file schema, gates, accounting, attempt/read
  consumption point, no-rerun rule, budgets and forbidden-path proof.
- [x] P9-6: independent Pre-EXECUTE review of the complete selection
  rule, streams, support/order identity, thresholds, truth boundary,
  tests, resource limits, accounting, attempt point and target absence.
- [x] P9-7: exactly one authorized SCREEN+CONFIRM attempt with the frozen
  command; the single artifact read and scientific attempt are consumed
  at the first NPZ content open, with no rerun/seed/grid/order/floor/
  threshold change.
- [x] P9-8: independent Pre-RESULT review of the 56-point SCREEN, Wilson
  eligibility, deterministic selection, independent CONFIRM, paired
  cells, accounting and every gate recomputed from the five artifacts.
- [x] P9-9: main-thread adjudication to
  `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE` /
  `TARGET_EMPIRICAL_LOWER_RATE_POINT_NOT_CONFIRMED` /
  `TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT` / `BLOCKED(<earliest gate>)`;
  no held-out/real FER, efficiency, key-rate, scaling, qualification or
  promotion claim either way.

Evidence (implementation only; gate not run): `P9_FREEZE.md`,
`P9_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Candidate evidence (no box checked): `P9_FREEZE.md`, `P9_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS, zero comments), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/lower_rate_screen_confirm/` (five files; read 1/1 + attempt 1/1 consumed); candidate label `TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE`, main-thread acceptance pending.

## P11 implementation tasks (Phase 4-P11; frozen packet `NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [x] P11-1: add the P11 spec delta
  (`specs/nbpolar-phase4-p11/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [x] P11-2: implement the allocation-only delta in
  `formal_ir/nbpolar/sc.py`: keyword-only `chunk_rows` with production
  default exactly `512` on `_minus_block`, contiguous row slices in
  original order each running the exact accepted
  `first_slice[:, index] + second_slice[:, None, :]` +
  `np.logaddexp.reduce(..., axis=2)` with the accepted `_normalize_rows`
  once over the full matrix, `chunk_rows=None` as the unchunked golden
  comparator, bool/non-integral/nonpositive rejection before allocation;
  no FWHT/clipping/caching/reordered-summation/dynamic-range/
  approximation/env-config and no new public `sc_decode` argument.
- [x] P11-3: implement the thin injected-data gate runner
  `formal_ir/nbpolar/sc_chunked_gate.py` with no production default
  (required `--seed`/`--chunk-rows`/`--out-dir`, absent-root refusal
  before the first `sc_decode`) performing exactly the P11-04 steps 1-3
  with the four-file outputs and the registered labels.
- [x] P11-4: focused `tests/test_nbpolar_sc_chunked.py` covering chunk
  sizes 32/128/512/2048, row boundaries
  1/31/32/33/127/128/129/511/512/513/2048, finite moderate/wide and exact
  `-inf` support, exact equality vs `chunk_rows=None`, N=64/256 full-SC
  equality (moderate, wide, mixed support, known coordinates, X11-C3
  pattern, impossible disclosure, near/exact ties, invalid/nonfinite
  inputs with identical exception type/message), default-is-512, public
  signature unchanged, invalid chunk sizes rejected and the
  no-production-invocation rule; plus the full accepted 252-test NB-Polar
  predecessor suite green with injected arrays, temporary roots and fresh
  test seeds only.
- [x] P11-5: `P11_FREEZE.md` + `P11_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the frozen contract, seed/env, verbatim command,
  absent root, four-file schema, gates/labels, attempt consumption at the
  first formal `sc_decode` (with the test-vs-gate distinction), no-rerun
  rule, budgets (600 s timeout, 1.5 GiB hard RSS, 120 s/1 GiB
  report-only) and forbidden-path proof; this doc authorizes nothing.
- [x] P11-6: independent Pre-EXECUTE review of the frozen implementation,
  tests, command, output schema, target absence, budgets and attempt
  point (main thread + reviewer).
- [x] P11-7: exactly one authorized gate execution with the frozen
  command; the single attempt is consumed at the first formal `sc_decode`
  call, with no rerun/seed/chunk/threshold change; no artifact read.
- [x] P11-8: independent Pre-RESULT review recomputing the recorded
  equivalence/resource facts from the four artifacts.
- [x] P11-9: main-thread adjudication to
  `EXACT_CHUNKED_SC_CANDIDATE` / `BLOCKED(<earliest gate>)`; no
  FER/efficiency/key-rate/scaling/throughput/qualification/promotion
  claim either way.

Evidence (implementation only; gate not run): `P11_FREEZE.md`,
`P11_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Candidate evidence (no box checked): `P11_FREEZE.md`, `P11_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS; partial-evidence fallback ratified), `PRE_RESULT_REVIEW.md` (PASS_WITH_COMMENTS, non-blocking only), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate/` (four files: frozen_plan 2152 / equivalence_records 23808 / scaling_record 580 / report 8018 B; attempt 1/1 consumed; 0 artifact reads); candidate label `EXACT_CHUNKED_SC_CANDIDATE`, main-thread acceptance pending.

## P12 implementation tasks (Phase 4-P12; frozen packet `NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [x] P12-1: add the P12 spec delta
  (`specs/nbpolar-phase4-p12/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [x] P12-2: implement the single thin core+CLI module
  `formal_ir/nbpolar/target_n_scaling.py`: accepted
  `load_v25_channel_counts` source-`1M` load with a stat-only size check,
  absent-root refusal and CLI-parse/chunk-contract refusals before the
  content open, the exact P7 floor-only support rule and entropy/column
  preconditions with zero-SC fail-closed contract, the frozen f-budget
  `K_total` with full use, N-specific analytic BEC reliabilities/orders
  with exhaustive `K1` enumeration and pre-SC freeze, the six-N/128-block
  single-arm candidate-conditioned two-layer execution with one tag per
  block, the accepted outcome buckets, the Clopper-Pearson intervals, the
  Toeplitz accounting/recount and the frozen labels; reuse the accepted P7
  floor/support/precondition pattern, the accepted P11 chunked SC
  (`chunk_rows=512`, call it, do not change it) and the P8 two-layer
  hard-candidate/Toeplitz/accounting pattern without changing those files.
- [x] P12-3: integrity-only gates (no recovery threshold), the frozen
  nine-flag CLI with no production default, and exactly five compact
  scalar-only output files at the frozen root.
- [x] P12-4: focused `tests/test_nbpolar_target_n_scaling.py` covering
  budget floors (formula, clip, full use, leakage inequality), `K`
  feasibility/ties (enumeration plus lexicographic selection including tie
  cases), literal BEC recurrence/order (tiny-N hand-checkable values plus
  index tie-break), f/accounting (5K+64, public/tag bits, partial failure,
  recount), axes/packing, causal two-layer wiring (candidate-conditioned
  L2), buckets/truth isolation, tag/recount, Clopper-Pearson edges (0/n,
  n/n, small-n two-sided values against an independent beta computation),
  absent-root refusal and the no-artifact/no-production-invocation rule;
  plus the full accepted 262-test NB-Polar predecessor suite green with
  injected arrays/tables, temporary roots and fresh test seeds only (never
  the NPZ, never the frozen streams, never production paths).
- [x] P12-5: `P12_FREEZE.md` + `P12_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the frozen point, constants, six frozen
  allocations, verbatim command, absent root, five-file schema, gates,
  accounting, attempt/read consumption point with refusal ordering,
  no-rerun rule, budgets and forbidden-path proof; this doc authorizes
  nothing.
- [x] P12-6: independent Pre-EXECUTE review of the frozen command,
  thresholds, seeds, budget, construction, allocation, truth boundary,
  tests, resource limits, accounting, attempt point and target absence.
- [x] P12-7: exactly one authorized six-N/128-block attempt with the frozen
  command; the single artifact read and scientific attempt are consumed
  at the first NPZ content open, with no rerun/seed/N/K/floor/order/
  threshold change.
- [x] P12-8: independent Pre-RESULT review recomputing all allocations,
  outcomes, intervals, accounting and gates from the five artifacts.
- [x] P12-9: main-thread adjudication to
  `TARGET_F13_N_SCALING_PROFILE_CANDIDATE` / `BLOCKED(<earliest gate>)`;
  recovery trend and first success are report-only; no held-out/real FER,
  efficiency, key-rate, scaling, qualification or promotion claim either
  way.

Evidence (implementation only; gate not run): `P12_FREEZE.md`,
`P12_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/target_f13_n_scaling/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Terminal evidence (no box checked): `PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (CONFIRMED_SINGLE_RESOURCE_ABORT), `OPERATOR_RETURN.md` (verbatim stderr); single run executed once 20:53:45→21:12:37, exit 1, stdout empty, resource-aborted on the N=262144 64 MiB metric alloc; no output root, no label persisted; read 1/1 + attempt 1/1 spent; closeout `BLOCKED(resource_limits_met_and_no_abort)`; no rerun; successor needs new authorization.

## P13 implementation tasks (Phase 4-P13; frozen packet `NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [ ] P13-1: add the P13 spec delta
  (`specs/nbpolar-phase4-p13/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [ ] P13-2: implement the single thin core+CLI module
  `formal_ir/nbpolar/empirical_genie_scaling.py`: accepted
  `load_v25_channel_counts` source-`1M` load with a stat-only size check,
  absent-root refusal and CLI-parse/chunk-contract/seed-grouping refusals
  before the content open, the exact P7 floor-only support rule and
  entropy/column preconditions with zero-genie fail-closed contract, the
  frozen TRAIN/DEV stream matrix with per-stream RNG restarts and
  oracle-conditioned L1/L2 genie rows, pooled per-layer risks with
  worst-first `(e,h,index)` orders, the frozen f-budget `K_total` with
  exhaustive `(K1,K2)` lexicographic selection frozen before DEV, scalar
  DEV residuals plus report-only P12 same-entropy BEC residuals from the
  same rows with no extra SC calls, the Student-t UCB aggregates and the
  frozen candidate/not-confirmed/BLOCKED labels; reuse the accepted P7
  floor/support/precondition pattern, the accepted P11 chunked SC
  (`chunk_rows=512` via the accepted `genie_conditionals`, call it, do
  not change it) and the P12 f-budget/BEC-allocation helpers without
  changing those files; no tag/Toeplitz master anywhere in this gate.
- [ ] P13-3: integrity gates plus the empirical-arm-only 0.01 UCB decision
  rule, the frozen eleven-flag CLI with no production default, and exactly
  five scalar-only files at the frozen root created as stubs before the
  content open and checkpointed after every completed block/N with per-cell
  wall/RSS-HWM/VmPeak/VmSize records.
- [ ] P13-4: focused `tests/test_nbpolar_empirical_genie_scaling.py`
  covering literal tiny genie oracle, empirical order/ties, K budget and
  exhaustive split selection, TRAIN/DEV separation, scalar DEV residual,
  t-UCB literal, BEC report-only reconstruction with zero extra SC calls,
  checkpoint-resume refusal, one-open/one-attempt accounting, MemoryError
  classification, seed grouping and the no-artifact/no-production-invocation
  rule; plus the full accepted NB-Polar predecessor suite green with
  injected arrays/tables, temporary roots and fresh test seeds only (never
  the NPZ, never the frozen streams, never production paths).
- [ ] P13-5: `P13_FREEZE.md` + `P13_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the frozen point, constants, three frozen K_total
  values, verbatim command, absent root, five-file schema, gates, UCB rule,
  accounting, attempt/read consumption point with refusal ordering,
  no-rerun rule, budgets and forbidden-path proof; this doc authorizes
  nothing.
- [ ] P13-6: independent Pre-EXECUTE review of the frozen command,
  thresholds, seeds, budget, construction, allocation, truth boundary,
  tests, resource limits, accounting, attempt point and target absence.
- [ ] P13-7: exactly one authorized three-N/120-block attempt with the
  frozen command; the single artifact read and scientific attempt are
  consumed at the first NPZ content open, with no rerun/seed/N/K/floor/
  order/threshold change.
- [ ] P13-8: independent Pre-RESULT review recomputing the three
  allocations, per-block residual aggregates/UCBs, classification,
  resource/accounting records and the five-file inventory from the five
  artifacts.
- [ ] P13-9: main-thread adjudication to
  `TARGET_EMPIRICAL_GENIE_F13_SCALING_CANDIDATE` /
  `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED` /
  `BLOCKED(<earliest gate>)`; residual is a genie union-bound construction
  proxy, not operational FER; no held-out/real FER, efficiency, key-rate,
  scaling, qualification or promotion claim either way.

Evidence (implementation only; gate not run): `P13_FREEZE.md`,
`P13_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Gate evidence (no box checked): `P13_FREEZE.md`, `P13_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS_WITH_COMMENTS, non-blocking only), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P13-EMPIRICAL-GENIE-SCALING/empirical_genie_scaling_gate/` (five files; read 1/1 + attempt 1/1 consumed); result label `TARGET_EMPIRICAL_GENIE_F13_SCALING_NOT_CONFIRMED`, main-thread acceptance pending.

## P14 implementation tasks (Phase 4-P14; frozen packet `NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [ ] P14-1: add the P14 spec delta
  (`specs/nbpolar-phase4-p14/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [ ] P14-2: implement the single thin core+CLI module
  `formal_ir/nbpolar/empirical_genie_learning_curve.py`: accepted
  `load_v25_channel_counts` source-`1M` load with a stat-only size check,
  absent-root refusal and CLI-parse/chunk/n/prefix/seed-shape refusals
  before the content open, the exact P7 floor-only support rule and
  entropy/column preconditions with zero-genie fail-closed contract, the
  frozen single-N=16384 matrix (TRAIN eight streams x 16 blocks in
  stream-major order, DEV four disjoint streams x 8 blocks) with nested
  prefixes 8/16/32/64/128 from the one TRAIN sequence, shared P13
  sampling/oracle-genie helpers (each TRAIN/DEV block decoded once per
  layer, 320 planned calls), pooled running-sum risks with worst-first
  `(e,h,index)` orders per prefix, the frozen f-budget `K_total`=3399
  with exhaustive `(K1,K2)` lexicographic selection per prefix frozen
  before DEV, five-way scalar DEV residuals from the one decode per
  block, the Student-t UCB aggregates plus paired `R_B-R_8` and adjacent
  differences, report-only Spearman/top-K/allocation-movement/count
  diagnostics, and the frozen candidate/not-confirmed/BLOCKED labels;
  reuse the accepted P7 floor/support/precondition pattern, the accepted
  P11 chunked SC (`chunk_rows=512` via the accepted P13 genie helpers,
  call them, do not change them) and the P12/P13 f-budget helper without
  changing those files; no tag/Toeplitz master anywhere in this gate.
- [ ] P14-3: integrity gates plus the B=128-only 0.01 UCB decision rule,
  the frozen twelve-flag CLI with no production default, and exactly
  five scalar-only files at the frozen root created as stubs before the
  content open and checkpointed after every completed TRAIN/DEV block
  with wall/RSS-HWM/VmPeak/VmSize records.
- [ ] P14-4: focused `tests/test_nbpolar_empirical_genie_learning_curve.py`
  covering frozen K_total pin, nested accumulation with no repeated
  calls (exact 320-call budget), order/K replay per prefix, five-way DEV
  scoring from one decode, paired UCB diffs with the t factor, stream
  separation and stream-major order, checkpoint-resume refusal,
  one-open/one-attempt accounting, MemoryError classification, and the
  no-artifact/no-production-invocation rule; plus the full accepted
  NB-Polar predecessor suite green with injected arrays/tables, temporary
  roots and fresh test seeds only (never the NPZ, never the frozen
  streams 1930..1943, never production paths).
- [ ] P14-5: `P14_FREEZE.md` + `P14_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the frozen point, constants, K_total=3399
  verification, five prefixes, verbatim command, absent root, five-file
  schema with per-block checkpointing, gates, B=128 UCB rule, accounting,
  attempt/read consumption point with refusal ordering, no-rerun rule,
  budgets and forbidden-path proof; this doc authorizes nothing.
- [ ] P14-6: independent Pre-EXECUTE review of the frozen command,
  thresholds, seeds, budget, construction, allocation, truth boundary,
  tests, resource limits, accounting, attempt point and target absence.
- [ ] P14-7: exactly one authorized 160-block attempt with the frozen
  command; the single artifact read and scientific attempt are consumed
  at the first NPZ content open, with no rerun/seed/prefix/N/K/floor/
  order/threshold change.
- [ ] P14-8: independent Pre-RESULT review recomputing the prefixes,
  constructions, per-block residual aggregates/UCBs, classification,
  resource/accounting records and the five-file inventory from the five
  artifacts.
- [ ] P14-9: main-thread adjudication to
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_CANDIDATE` /
  `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED` /
  `BLOCKED(<earliest gate>)`; residual is a genie union-bound construction
  proxy, not operational FER; no held-out/real FER, efficiency, key-rate,
  scaling, qualification or promotion claim either way.

Evidence (implementation only; gate not run): `P14_FREEZE.md`,
`P14_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Gate evidence (no box checked): `P14_FREEZE.md`, `P14_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS_WITH_COMMENTS, non-blocking only), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/empirical_genie_learning_curve_gate/` (five files; read 1/1 + attempt 1/1 consumed); result label `TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED`, main-thread acceptance pending.

## P15 implementation tasks (Phase 4-P15; frozen packet `NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [ ] P15-1: add the P15 spec delta
  (`specs/nbpolar-phase4-p15/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [ ] P15-2: implement the single thin core+CLI module
  `formal_ir/nbpolar/empirical_genie_mid_n.py`: accepted
  `load_v25_channel_counts` source-`1M` load with a stat-only size check,
  absent-root refusal and CLI-parse/chunk-contract/N-to-seed-grouping
  refusals before the content open, the exact P7 floor-only support rule
  and entropy/column preconditions with zero-genie fail-closed contract,
  the frozen two-cell matrix (N=32768 TRAIN 2026091960..1963 x 4 blocks
  + DEV 2026091970..1973 x 4 blocks; N=65536 TRAIN 2026091980..1983 x 4
  blocks + DEV 2026091990..1993 x 4 blocks) with per-stream RNG restarts
  and oracle-conditioned L1/L2 genie rows, pooled per-layer risks with
  worst-first `(e,h,index)` orders, the frozen f-budget `K_total` (6811
  at N=32768, 13636 at N=65536) with exhaustive `(K1,K2)` lexicographic
  selection frozen before each N's DEV, scalar DEV residuals only with
  the df=15 Student-t UCB aggregates and the frozen candidate/
  not-confirmed/BLOCKED labels; reuse the accepted P7 floor/support/
  precondition pattern, the accepted P11 chunked SC (`chunk_rows=512`
  via the accepted P13 genie helpers, call them, do not change them)
  and the P12/P13 f-budget helper without changing those files; no
  decision arm, tag or Toeplitz master anywhere in this gate.
- [ ] P15-3: integrity gates plus the any-UCB `<= 0.01` decision rule with
  smallest qualifying N, the frozen eleven-flag CLI with no production
  default, and exactly five scalar-only files at the frozen root created
  as stubs before the content open and checkpointed after every completed
  block with per-cell and per-record wall/RSS-HWM/VmPeak/VmSize records.
- [ ] P15-4: focused `tests/test_nbpolar_empirical_genie_mid_n.py`
  covering frozen K_total pins (6811/13636), both-N grouping with
  mis-grouping refusal, stream separation per N and across N,
  order/allocation replay per N, scalar DEV residuals with df=15 UCB
  (hand value vs the 1.753050356 factor, df=31 factor absent),
  checkpoint-resume refusal, partial-failure preservation,
  one-open/one-attempt accounting with the reopen guard, MemoryError
  classification, and the no-artifact/no-decision-arm/no-production-
  invocation rule; plus the full accepted NB-Polar predecessor suite
  green with injected arrays/tables, temporary roots and fresh test seeds
  only (never the NPZ, never the frozen streams 1960..1993, never
  production paths).
- [ ] P15-5: `P15_FREEZE.md` + `P15_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the frozen point, constants, both frozen K_total
  values with arithmetic, verbatim command, absent root, five-file schema
  with per-block checkpointing, gates, any-UCB rule with the df=15
  factor, accounting, attempt/read consumption point with refusal
  ordering, no-rerun rule, budgets and forbidden-path proof; this doc
  authorizes nothing.
- [ ] P15-6: independent Pre-EXECUTE review of the frozen command,
  thresholds, seeds, budget, construction, allocation, truth boundary,
  tests, resource limits, accounting, attempt point and target absence.
- [ ] P15-7: exactly one authorized two-N/64-block attempt with the frozen
  command; the single artifact read and scientific attempt are consumed
  at the first NPZ content open, with no rerun/seed/N/K/floor/order/
  threshold change.
- [ ] P15-8: independent Pre-RESULT review recomputing the two
  allocations, per-block residual aggregates/UCBs, classification,
  resource/accounting records and the five-file inventory from the five
  artifacts.
- [ ] P15-9: main-thread adjudication to
  `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_CANDIDATE` /
  `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED` /
  `BLOCKED(<earliest gate>)`; the UCB is a genie union-bound
  construction proxy, not operational FER and not proof of any minimum
  N; no held-out/real FER, efficiency, key-rate, scaling, qualification
  or promotion claim either way.

Evidence (implementation only; gate not run): `P15_FREEZE.md`,
`P15_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Gate evidence (no box checked): `P15_FREEZE.md`, `P15_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS, numbers bit-exact, two non-blocking notes), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/empirical_genie_mid_n_gate/` (five files; read 1/1 + attempt 1/1 consumed); result label `TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED`, main-thread acceptance pending.

## P16 implementation tasks (Phase 4-P16; frozen packet `NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [ ] P16-1: add the P16 spec delta
  (`specs/nbpolar-phase4-p16/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [ ] P16-2: implement the single thin core+CLI module
  `formal_ir/nbpolar/operational_f13.py`: accepted
  `load_v25_channel_counts` source-`1M` load with a stat-only size check,
  absent-root refusal and CLI-parse/chunk-contract/tag-bits/N/seed-grouping
  refusals before the content open, the exact P7 floor-only support rule
  and entropy/column preconditions with zero-call fail-closed contract,
  the frozen matrix (N=32768; TRAIN 2026092000..2003 x 4 blocks; DEV
  2026092010..2017 x 8 blocks) with per-stream RNG restarts and
  P13-shared true-prefix/oracle-conditioned TRAIN genie rows, pooled
  per-layer risks with worst-first `(e,h,index)` orders, the frozen
  f-budget `K_total=6811` with exhaustive `(K1,K2)` lexicographic
  selection frozen before DEV, single-arm operational DEV (disclose U1,
  candidate-conditioned L2 metrics, disclose U2, restarted L2 SC, one
  64-bit Toeplitz tag with master DEV seed+10000 in the P16/N/block
  domain), the six-bucket outcome precedence with undetected never
  success and nonfinite outranking decode failure, `5*(K1+K2)+64`
  disclosure with the f-inequality assert, `327743` public bits per tag
  and the independent literal recount; reuse the accepted P7
  floor/support/precondition pattern, the P13 genie/construction helpers,
  the P12 f-budget helper, the accepted P11 chunked SC (`chunk_rows=512`
  contract check) and the P8 causal/tag/accounting pattern without
  changing those files; no second arm, no retry, no surrogate orders
  anywhere in this gate.
- [ ] P16-3: integrity gates in frozen order plus the exact-62/64 and
  Wilson-LB-0.90 recovery rule with the frozen 62/61 boundary values
  verified in code, the frozen twelve-flag CLI with no production
  default, and exactly five scalar-only files at the frozen root created
  as stubs before the content open and checkpointed after the
  construction freeze and every TRAIN/DEV block with per-record
  wall/RSS-HWM/VmPeak/VmSize records.
- [ ] P16-4: focused `tests/test_nbpolar_operational_f13.py`
  covering the frozen K_total pin (6811 with arithmetic), matrix
  constants, shared-helper identity, every outcome bucket and precedence
  (incl. nonfinite outranking and undetected never success), the Wilson
  62/61 boundary literals with all three label branches, tag/domain
  separation, real-arm exact recovery/accounting/truth isolation at tiny
  n, the causal L1-candidate-L2 wiring sentinel, construction replay and
  full-disclosure accounting on fakes, partial-failure bit counting,
  recount tamper detection, grouping/contract refusals, checkpoint-resume
  refusal, precondition failure with zero calls, one-open/one-attempt
  accounting with the reopen guard, MemoryError classification, budget
  abort-fill, scalar-only outputs, CLI refusals and the
  no-forbidden-access rule; plus the full accepted NB-Polar predecessor
  suite green with injected arrays/tables, temporary roots and fresh test
  seeds only (never the NPZ, never the frozen streams 2000..2003 /
  2010..2017, never production paths).
- [ ] P16-5: `P16_FREEZE.md` + `P16_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the frozen point, constants, frozen K_total with
  arithmetic, verbatim command, absent root, five-file schema with freeze
  plus per-block checkpointing, gates, 62/64 + Wilson-0.90 rule with both
  boundary values, disclosure/public accounting, attempt/read consumption
  point with refusal ordering, no-rerun rule, budgets and forbidden-path
  proof; this doc authorizes nothing.
- [ ] P16-6: independent Pre-EXECUTE review of the frozen command,
  thresholds, seeds, budget, construction, allocation, causal wiring,
  truth boundary, tag/domain separation, tests, resource limits,
  accounting, attempt point and target absence.
- [ ] P16-7: exactly one authorized 16+64-block attempt with the frozen
  command; the single artifact read and scientific attempt are consumed
  together at the first NPZ content open, with no rerun/seed/N/K/floor/
  order/threshold change.
- [ ] P16-8: independent Pre-RESULT review recomputing the allocation,
  64 operational outcomes, Wilson, disclosure/public accounting, gates,
  resources and the five-file inventory from the five artifacts.
- [ ] P16-9: main-thread adjudication to
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` /
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_NOT_CONFIRMED` /
  `BLOCKED(<earliest gate>)`; this is a model-sampled operational
  development signal, not real-data qualification; no held-out/real FER,
  efficiency, key-rate, scaling, qualification or promotion claim either
  way.

Evidence (implementation only; gate not run): `P16_FREEZE.md`,
`P16_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Gate evidence (no box checked): `P16_FREEZE.md`, `P16_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS_WITH_COMMENTS, 62/64 recount + Wilson recomputed, zero-count margin), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/` (five files; read 1/1 + attempt 1/1 consumed); result label `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE`, main-thread acceptance pending.

## P17 implementation tasks (Phase 4-P17; frozen packet `NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [ ] P17-1: add the P17 spec delta
  (`specs/nbpolar-phase4-p17/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [ ] P17-2: implement the single thin replication runner
  `formal_ir/nbpolar/operational_f13_replication.py`: verified-P16-file
  predecessor identity (N/K1/K2/orders/canonical digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  recomputed with the exact P16 recipe) before any root or content open,
  the accepted `load_v25_channel_counts` source-`1M` load with a
  stat-only size check, the exact P7 floor-only support rule and
  entropy/column preconditions with zero-SC fail-closed contract, the
  frozen 128-block matrix (DEV `2026092030..2037` x 16 blocks, per-stream
  RNG restarts, fresh relative to P16) with the verified orders and
  K1=319/K2=6492, single-arm operational DEV (disclose U1,
  candidate-conditioned L2 metrics, disclose U2, restarted L2 SC, one
  64-bit Toeplitz tag in the P17/N/block seed domain with master DEV
  seed+10000), the six-bucket outcome precedence with undetected never
  success and nonfinite outranking decode failure, `34119` key-dependent
  bits per fully invoked block with the f-inequality assert, `327743`
  public bits per tag and the independent literal recount; reuse the
  accepted P16 operational helpers (`run_operational_block`,
  `classify_operational_outcome`, record/event/recount/accounting
  helpers), the accepted P7 floor/support/precondition pattern and the
  accepted P11 chunked SC (`chunk_rows=512` contract check, call it, do
  not change it) without changing those files; no construction path, no
  second arm, no retry, no P16-domain tag reuse, no P16-block pooling
  anywhere in this gate.
- [ ] P17-3: predecessor-identity plus integrity gates in frozen order
  with the exact-121/128 and Wilson-LB-0.90 recovery rule over the 128
  P17 blocks only (P16's 62/64 report-only, structurally excluded by the
  pinned total), the frozen 121/120 boundary values verified in code, the
  frozen thirteen-flag CLI with no production default, and exactly five
  scalar-only files at the frozen root created as stubs before the
  content open and checkpointed after every DEV block with per-record
  wall/RSS-HWM/VmPeak/VmSize records.
- [ ] P17-4: focused `tests/test_nbpolar_operational_f13_replication.py`
  covering predecessor identity with fabricated files plus tamper
  refusals (mutated K/orders/digest/protocol, zero execution), the
  frozen-digest flag pin, zero construction-path calls, P16 operational
  parity with P17 tag-domain proof, every outcome bucket and precedence
  (incl. nonfinite outranking and undetected never success), the Wilson
  121/120 boundary literals with all three label branches, the pinned
  128 total that structurally excludes P16-shaped inputs, fresh-stream
  disjointness, P16-non-pooling (decision inputs exactly the 128 P17
  blocks), full-disclosure accounting (34119/327743) with recount tamper
  detection, grouping/contract refusals, checkpoint-resume refusal,
  precondition failure with zero calls, one-open/one-attempt accounting
  with the reopen guard, MemoryError classification, budget abort-fill,
  scalar-only outputs, CLI refusals and the no-forbidden-access rule;
  plus the full accepted NB-Polar predecessor suite green with injected
  arrays/tables, temporary roots and fresh test seeds only (never the
  NPZ, never the frozen streams 2030..2037, never production paths, never
  the real P16 root).
- [ ] P17-5: `P17_FREEZE.md` + `P17_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the predecessor identity record incl. digest,
  frozen matrix, verbatim command, absent root, five-file schema with
  per-block checkpointing, gates, 121/128 + Wilson-0.90 rule with both
  boundary values, P16-report-only rule, disclosure/public accounting,
  attempt/read consumption point with refusal ordering, no-rerun rule,
  budgets and forbidden-path proof; this doc authorizes nothing.
- [ ] P17-6: independent Pre-EXECUTE review of the frozen command,
  predecessor identity, thresholds, seeds, budget, orders, causal wiring,
  truth boundary, tag/domain separation, tests, resource limits,
  accounting, attempt point and target absence.
- [ ] P17-7: exactly one authorized 128-block attempt with the frozen
  command; the single artifact read and scientific attempt are consumed
  together at the first NPZ content open, with no rerun/seed/N/K/floor/
  order/threshold change.
- [ ] P17-8: independent Pre-RESULT review recomputing the predecessor
  identity, 128 operational outcomes, Wilson, disclosure/public
  accounting, gates, resources and the five-file inventory from the five
  artifacts.
- [ ] P17-9: main-thread adjudication to
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE` /
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_NOT_CONFIRMED` /
  `BLOCKED(<earliest gate>)`; this is a model-sampled operational
  replication development signal resolving P16's zero-count margin, not
  real-data qualification; no held-out/real FER, efficiency, key-rate,
  scaling, qualification or promotion claim either way.

Evidence (implementation only; gate not run): `P17_FREEZE.md`,
`P17_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Gate evidence (no box checked): `P17_FREEZE.md`, `P17_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS_WITH_COMMENTS, 123/128 recount + Wilson recomputed, count margin exactly 2, item-8 resolved), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/operational_replication_gate/` (five files; read 1/1 + attempt 1/1 consumed); result label `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE`, main-thread acceptance pending.

## P18 implementation tasks (Phase 4-P18; frozen packet `NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [ ] P18-1: add the P18 spec delta
  (`specs/nbpolar-phase4-p18/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [ ] P18-2: implement the single thin HOLD microcheck runner
  `formal_ir/nbpolar/holdout_microcheck.py`: P16 construction identity
  (N=32768, K1=319, K2=6492, K_total=6811, leakage=34119, canonical digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  recomputed with the exact P16 recipe) plus the V25 run_04 split-manifest
  identity (400 HOLD frames / 102400 HOLD pairs) before any root or
  protected content open; the two protected inputs each content-opened
  exactly once (accepted `load_v25_channel_counts` with the stat-only
  `25,166,822`-byte check; accepted `load_pairs_table` /
  `normalize_pair_columns` for the 1M HOLD frames), with the single
  scientific attempt consumed at the first content open and module-level
  reopen guards; the exact P7 floor-1e-15 support rule and
  entropy/column preconditions with zero-SC fail-closed contract;
  deterministic HOLD block formation (sort by `(frame_id,pair_idx)`,
  exactly 400 frames `1600..1999`, 256 rows/frame, `pair_idx 0..255`,
  symbols `0..1023`, blocks `1600..1727`/`1728..1855`/`1856..1983`,
  unused remainder `1984..1999`) with no shuffle/resampling/overlap/pad/
  pool/fit; one L1 SC plus one candidate-conditioned L2 SC per block
  through the accepted `run_operational_block` with the verified orders,
  K1=319/K2=6492 and `chunk_rows=512`; one 64-bit Toeplitz tag per block
  in the P18/N/block domain (public master 2026092050); scalar-only
  frame-range/SER/per-layer-NLL/outcome/L1/tag/34119/327743/resource
  records and the sample `34119 / observed_block_NLL_bits` CE-normalized
  disclosure ratio (explicitly not qualification efficiency); zero
  recovery threshold with the COMPLETE label for all 0..3 exact outcomes
  and `BLOCKED(<earliest gate>)` otherwise; reuse the accepted P16
  operational helpers, the accepted P17 predecessor verifier, the
  accepted P7 floor/support/precondition pattern and the accepted P11
  chunked SC (`chunk_rows=512` contract check, call it, do not change it)
  without changing those files.
- [ ] P18-3: integrity gates in frozen order (predecessor identity,
  manifest identity, target population contract, exact HOLD population,
  exact blocks with declared remainder, orders/K/f replay, SC-call and
  tag accounting recomputed from records, exhaustive disjoint buckets,
  truth isolation, undetected zero, nonfinite zero, disclosure plus
  literal recount, one open per protected input, unchanged input
  size/mtime, no unregistered access, no resource abort), the frozen
  sixteen-flag CLI with no production default and the exact-command
  refusals before the opens, and exactly five scalar-only files at the
  frozen root created as stubs before the opens and checkpointed after
  every block with per-record wall/RSS-HWM/VmPeak/VmSize and the
  2 GiB/600 s budgets.
- [ ] P18-4: focused
  `tests/test_nbpolar_holdout_microcheck.py` covering identity refusal
  before reads (mutated K/digest/manifest, zero reads, zero root), exact
  HOLD slicing and remainder with malformed frame/row/pair/symbol
  rejections, both one-open guards, no fitting/sampling/shuffling
  (structural plus exact call counts), fixed construction and P16 orders
  with the P18 tag-domain proof, truth isolation (sentinel plus
  array-immutability), all six outcome buckets and precedence, NLL/SER
  and 34119/327743/CE-ratio arithmetic with recount tamper detection,
  checkpoint recovery, budget abort-fill, MemoryError classification,
  failure precedence `BLOCKED(<earliest>)`, no-threshold labels for 0/3
  and 3/3 exact with no Wilson/FER/recovery code path, scalar-only
  outputs, real-mode accounting/stat gates through patched loaders on
  throwaway files and CLI refusals; plus the complete accepted NB-Polar
  suite green with injected arrays/tables, temporary roots and fresh test
  seeds only (never the NPZ, never the pairs parquet, never the frozen
  tag master for real scoring, never production paths or old roots).
- [ ] P18-5: `P18_FREEZE.md` + `P18_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the P16 identity record incl. digest, the manifest
  400/102400 record, both protected input absolute paths with stat-only
  sizes and the one-open/consumption point, block/remainder ranges, the
  verbatim frozen command incl. exports, absent root and five-file schema
  with per-block checkpointing, integrity gates with the explicit
  no-threshold statement, no-rerun rule, 2 GiB/600 s budgets,
  forbidden-path proof and the real-input-microcheck-not-FER boundary;
  this doc authorizes nothing.
- [ ] P18-6: independent Pre-EXECUTE review of the frozen command,
  predecessor/manifest identities, protected-input resolution and stat
  values, one-open rules, block/remainder ranges, K/orders, budgets,
  tag/domain separation, truth boundary, accounting, tests and target
  absence.
- [ ] P18-7: exactly one authorized three-block HOLD attempt with the
  frozen command; the single attempt is consumed at the first protected
  content open with no rerun/reopen/seed/parameter change.
- [ ] P18-8: independent Pre-RESULT review recomputing the identities,
  population, three block outcomes, NLL/disclosure accounting, gates,
  input stats, resources and the five-file inventory from the artifacts.
- [ ] P18-9: main-thread adjudication to
  `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a real-input operational microcheck
  of the frozen V25 1M HOLD split, not real-frame FER, efficiency,
  key-rate, scaling, qualification or promotion evidence either way.

Evidence (implementation only; gate not run): `P18_FREEZE.md`,
`P18_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.

Gate evidence (no box checked): `P18_FREEZE.md`, `P18_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS_WITH_COMMENTS, 17/17 gates recomputed, resumed from an interrupted prior attempt's transcript), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/holdout_microcheck/` (five files; reads 1/1 + 1/1 and attempt 1/1 consumed; 0/3 exact, descriptive only — no FER/recovery threshold); result label `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE`, main-thread acceptance pending.

## P19 implementation tasks (Phase 4-P19; frozen packet `NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC`)

Status/acceptance of every item below is owned by the main thread; the
implementing session reports evidence only and never checks its own boxes.

- [ ] P19-1: add the P19 spec delta
  (`specs/nbpolar-phase4-p19/spec.md`) and this task section; no production
  behavior is authorized by this doc.
- [ ] P19-2: implement the single thin layer/backoff diagnostic runner
  `formal_ir/nbpolar/holdout_backoff_diagnostic.py`: P16 construction
  identity (N=32768, K1=319, K2=6492, K_total=6811, leakage=34119, canonical
  digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`
  recomputed with the exact P16 recipe), the V25 run_04 split-manifest
  identity (400 HOLD frames / 102400 HOLD pairs) and the accepted P18
  block-range pin before any root or protected content open; the two
  protected inputs each content-opened exactly once (accepted
  `load_v25_channel_counts` with the stat-only `25,166,822`-byte check;
  accepted `load_pairs_table`/`normalize_pair_columns` for the 1M HOLD
  frames), with the single scientific attempt consumed at the first content
  open and module-level reopen guards; the exact P7 floor-1e-15 support rule
  and entropy/column preconditions with zero-SC fail-closed contract; the
  accepted P18 `form_holdout_blocks` slicing (blocks `1600..1727`/
  `1728..1855`/`1856..1983`, unused remainder `1984..1999`) with no
  shuffle/resampling/overlap/pad/pool/fit; exactly five frozen arms in order
  `base(319,6492)`/`l1_plus(447,6492)`/`l2_plus(319,7004)`/
  `both_plus(447,7004)`/`true_l1_control(oracle, K1=0, K2=6492)` with the
  fixed +128 L1 / +512 L2 increments, `chunk_rows=512`, the P16 empirical
  orders and the P19/N/arm/block tag domain (public master 2026092060); one
  operational L1 plus one candidate-conditioned L2 SC per operational block
  and one oracle-conditioned L2 SC for the control (27 SC calls / 15 tags);
  scalar-only per-(arm, block) outcomes with raw SER, per-layer/total NLL,
  disclosure bits, the arm-leakage CE-normalized ratio (explicitly not
  qualification efficiency) and resources; paired recovery tables versus
  base, the first-operational-recovery-arm pointer and the neutral
  non-monotone flag; zero recovery threshold with the COMPLETE label for all
  0/3..3/3 patterns and `BLOCKED(<earliest gate>)` otherwise; the
  oracle-labelled control is provenance-isolated from every operational
  aggregate; reuse the accepted P16 operational helpers, the accepted P17
  predecessor verifier, the accepted P18 loading/block formation, the
  accepted P7 floor/support/precondition pattern and the accepted P11
  chunked SC (`chunk_rows=512` contract check, call it, do not change it)
  without changing those files.
- [ ] P19-3: integrity gates in frozen order (predecessor identity, manifest
  identity, P18 block pin, target population contract, exact HOLD
  population, exact blocks per arm with declared remainder, 15 records, 27
  SC calls, 15 tags, valid orders with per-arm K/prefix arithmetic, oracle
  isolation, exhaustive disjoint buckets, undetected zero, nonfinite zero,
  truth isolation, disclosure plus literal recount, one open per protected
  input, unchanged input size/mtime, no unregistered access, no resource
  abort), the frozen sixteen-flag CLI with no production default and the
  exact-command refusals before the opens, and exactly five scalar-only
  files at the frozen root created as stubs before the opens and
  checkpointed after every (arm, block) record with per-record
  wall/RSS-HWM/VmPeak/VmSize and the 2 GiB/600 s budgets.
- [ ] P19-4: focused
  `tests/test_nbpolar_holdout_backoff_diagnostic.py` covering identity
  refusal before reads (mutated construction K/digest, mutated manifest,
  mutated P18 pin, zero reads, zero root), P18 slicing and remainder with
  malformed frame/row/pair/symbol rejections, both one-open guards, no
  fitting/sampling/shuffling (structural plus exact call counts), five-arm
  semantics (K values, leakages, labels, 2 SC per operational block and 1
  for the control, 27 SC/15 tags), the exact +128/+512 K and leakage
  arithmetic, the P19 tag-domain proof against the P16/P17/P18 domains,
  oracle isolation (control excluded from operational aggregates, provenance
  enforced, partition tamper), counts/buckets/recount with tamper detection,
  paired recovery tables with first-arm and non-monotone reporting, all
  four 0/3..3/3 operational and control recovery patterns COMPLETE with no
  Wilson/FER/recovery code path, checkpoint STOP, budget abort-fill,
  MemoryError classification, failure precedence `BLOCKED(<earliest>)`,
  scalar-only five-file outputs, real-mode accounting/stat gates through
  patched loaders on throwaway files and CLI refusals; plus the
  packet-scoped predecessor suites green with injected arrays/tables,
  temporary roots and fresh test seeds only (never the NPZ, never the pairs
  parquet, never a frozen tag master for real scoring, never production
  paths or old roots).
- [ ] P19-5: `P19_FREEZE.md` + `P19_IMPLEMENTATION_NOTES.md` in the packet
  queue directory with the five-arm K/leakage table, the P16 identity
  record incl. digest, the manifest 400/102400 record, the accepted P18
  block pin, both protected input absolute paths with stat-only sizes and
  the one-open/consumption point, block/remainder ranges, the verbatim
  frozen command incl. exports, absent root and five-file schema with
  per-(arm, block) checkpointing, integrity gates with the explicit
  no-threshold statement and the oracle-control boundary, no-rerun rule,
  2 GiB/600 s budgets, forbidden-path proof and the descriptive-diagnostic-
  not-FER boundary; this doc authorizes nothing.
- [ ] P19-6: independent Pre-EXECUTE review of the frozen command, the
  predecessor/manifest/P18-pin identities, protected-input resolution and
  stat values, one-open rules, block/remainder ranges, the five-arm K/order/
  leakage table, the oracle boundary, budgets, tag/domain separation,
  truth/accounting gates, tests and target absence.
- [ ] P19-7: exactly one authorized fifteen-record five-arm attempt with the
  frozen command; the single attempt is consumed at the first protected
  content open with no rerun/reopen/seed/parameter/arm change.
- [ ] P19-8: independent Pre-RESULT review recomputing the identities,
  population, 15 records, per-arm outcomes, paired/first-recovery
  diagnostics, NLL/disclosure accounting, oracle isolation, gates, input
  stats, resources and the five-file inventory from the artifacts.
- [ ] P19-9: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive real-input layer/backoff
  diagnostic of the frozen V25 1M HOLD split, not real-frame FER,
  efficiency, key-rate, scaling, qualification or promotion evidence either
  way, and the oracle true-L1 arm is never an operational or deployable
  result.

Evidence (implementation only; gate not run): `P19_FREEZE.md`,
`P19_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/`
is absent and must remain absent until an authorized execution. No box above is
checked by the implementing session.
