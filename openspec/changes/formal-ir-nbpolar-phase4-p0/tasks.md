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

Gate evidence (no box checked): `P19_FREEZE.md`, `P19_IMPLEMENTATION_NOTES.md`, `PRE_EXECUTE_REVIEW.md` (PASS WITH COMMENTS), `PRE_RESULT_REVIEW.md` (PASS_WITH_COMMENTS, 20/20 gates recomputed; downgrade solely for the external-commit provenance anomaly), `OPERATOR_RETURN.md`; output root `.workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/holdout_backoff_diagnostic/` (five files; reads 1/1 + 1/1 and attempt 1/1 consumed; 15/15 records `verify_failed`, descriptive only — no FER/recovery/winner/monotonicity/superiority threshold); result label `TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`, main-thread acceptance pending, and acceptance must read the finalized worktree files only (a concurrent external commit captured a mid-run 11/15 snapshot).

Main-thread disposition (2026-09-17): accepted descriptively as
`TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`. The finalized
worktree artifacts are authoritative. +128 L1 made L1 correct on all three
blocks, but +128 L1, +512 L2, both and the true-L1 control all had 0/3 complete
recovery. This does not estimate FER or reject the route; it makes hard-L1
propagation insufficient as the sole explanation and closes these three blocks
to tuning.

## P20A implementation/accounting tasks

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20A-RESOURCE-ENDPOINT-INSTRUMENTATION/`.
It awaits explicit authorization and permits no protected read or scientific
attempt.

- [ ] Audit shared inner L1/L2 SC exception seams used by the P16-P19 route.
- [ ] Re-raise `MemoryError` to the resource-stop handler without changing the
  accepted decode/nonfinite taxonomy.
- [ ] Add injected inner-L1 and inner-L2 OOM tests with call/disclosure recount.
- [ ] Make L1, hard-L2, oracle-L2 and pair exact endpoint semantics explicit.
- [ ] Run focused predecessor tests using injected inputs and temporary roots.
- [ ] Obtain independent acceptance before freezing any L2 real-data
  feasibility execution.

## P20B bounded-search diagnostic tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/`
(`TASK_PACKET.md`, 225 lines, frozen; Tier-Y decision-gate packet).
Predecessors: P19
`TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE_ACCEPTED_DESCRIPTIVE`
+ P20A `IMPLEMENTATION_ACCEPTED`. Stage A authorized separately; it permits
no protected read (not even stat), no real-data decoder execution, no
Stage-B output root, no disclosure/construction change, no closed-block
tuning, no SCL/new kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and no commit/push. Stage B needs
an independent Pre-EXECUTE PASS plus a separate pasted authorization.

- [ ] P20B-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py` plus the
  `construction.py` / `prior.py` / `sc.py` contracts as called); change no
  shared logic.
- [ ] P20B-2: implement the thin runner
  `formal_ir/nbpolar/bounded_search_diagnostic.py` reusing P18 loading and
  the P16 operational helpers read-only: hardcoded three arms
  (`S0_sc_base` via accepted `run_operational_block`; `S1_bounded_search`
  frozen greedy prefix plus rescore-only `P20B-NBHD-1` search over at most
  M=8 candidates with one coherent NLL model, no tag-guided selection, no
  evidence reuse, 2 SC + 1 tag per block; `S2_true_l1_diagnostic` via
  accepted `run_oracle_control_block`, oracle-isolated); new P20B tag
  domains; VAL DEV formation (1200..1327 / 1328..1455 / 1456..1583,
  remainder 1584..1599 unused, closed 1600..1983 disjoint by fail-closed
  gate); five files with per-(arm, block) checkpointing; P20A resource
  passthrough and endpoint separation.
- [ ] P20B-3: freeze ONE search bound (M=8), ONE neighborhood
  (`P20B-NBHD-1` Hamming-1 U-domain margin-ranked), and ONE coherent
  probability-model score; freeze the independent development population,
  the base disclosure cap (34119 operational / 32524 control key bits per
  block, 327743 public bits per tag, ~10.41% of raw), the exact Stage-B
  command, and the SC/tag/wall/RSS budgets in `P20B_FREEZE.md`.
- [ ] P20B-4: focused `tests/test_nbpolar_bounded_search_diagnostic.py`
  (synthetic/injected small arrays plus scripted seams and tiny-n real SC;
  fresh seeds; temporary roots; `pytest -p no:cacheprovider`) asserting
  search-vs-SC behavior, accounting, endpoint separation, no-tag-selection,
  resource path, and the no-production-invocation rule; plus the four
  packet-scoped predecessor suites green with zero protected opens.
- [ ] P20B-5: `P20B_FREEZE.md` + `P20B_IMPLEMENTATION_NOTES.md` in the packet
  queue directory and this P20B spec/tasks delta; this doc authorizes
  nothing (no Stage-B execution, no self-acceptance).
- [ ] P20B-6: independent Pre-EXECUTE review of the frozen command,
  population, cap, search freeze, budgets, tag/domain separation,
  truth/accounting gates, tests and target absence (main thread +
  reviewer; separate gate, not this task).
- [ ] P20B-7: exactly one authorized nine-record three-arm attempt with the
  frozen command; the single attempt is consumed at the first protected
  content open with no rerun/reopen/seed/parameter/arm change (separate
  Stage-B authorization required; not authorized here).
- [ ] P20B-8: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, search-vs-SC diagnostics,
  NLL/disclosure accounting, oracle isolation, gates, input stats,
  resources and the five-file inventory from the artifacts (separate gate,
  not this task).
- [ ] P20B-9: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_DEV_BOUNDED_SEARCH_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive single-factor
  development diagnostic, not real-frame FER, efficiency, key-rate,
  scaling, qualification or promotion evidence either way, and the oracle
  S2 arm is never an operational or deployable result.

Evidence (Stage A only; Stage B not run): `P20B_FREEZE.md`,
`P20B_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20B-BOUNDED-SEARCH-DIAGNOSTIC/bounded_search_diagnostic/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20C L2 disclosure backoff tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF/`
(`TASK_PACKET.md`, 289 lines, frozen; Tier-Y decision-gate packet).
Predecessors: P19
`TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE_ACCEPTED_DESCRIPTIVE`
+ P20A `IMPLEMENTATION_ACCEPTED` + P20B
`TARGET_EMPIRICAL_N32768_DEV_BOUNDED_SEARCH_COMPLETE_ACCEPTED_DESCRIPTIVE`.
Stage A authorized separately; it permits no protected read (not even
stat), no real-data decoder execution, no Stage-B output root, no
disclosure step beyond the single frozen +1024, no construction change,
no closed-block or consumed-VAL-pool tuning, no SCL/new
kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and no commit/push. Stage B needs
an independent Pre-EXECUTE PASS plus a separate pasted authorization.

- [ ] P20C-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py` plus the
  `construction.py` / `prior.py` / `sc.py` contracts as called); change no
  shared logic.
- [ ] P20C-2: implement the thin runner
  `formal_ir/nbpolar/l2_disclosure_backoff.py` reusing P18 loading and
  the P16 operational helpers read-only: hardcoded three arms
  (`B0_sc_base` base K1=319/K2=6492 via accepted
  `run_operational_block`; `B1_L2plus` base + the ONE preregistered +1024
  L2 step via frozen-order-prefix extension on the same frozen L2 order,
  all else identical, 2 SC + 1 tag per block; `B2_true_l1_diagnostic`
  base K2 via accepted `run_oracle_control_block`, oracle-isolated); new
  P20C tag domains; same-file TRAIN DEV formation (0..127 / 128..255 /
  256..383, remainder 384..1199 never used, closed 1600..1983 AND
  consumed VAL 1200..1599 disjoint by dual fail-closed gate); five files
  with per-(arm, block) checkpointing; P20A resource passthrough and
  endpoint separation.
- [ ] P20C-3: freeze ONE disclosure step (ΔK2=+1024, K2 6492→7516,
  K_total 6811→7835, order-prefix rule), the independent development
  population, the per-arm disclosure caps (34119 / 39239 / 32524 key bits
  per block + 327743 public bits per tag, ~10.41% / ~11.97% of raw, B1
  delta +5120), the exact Stage-B command, and the SC/tag/wall/RSS
  budgets in `P20C_FREEZE.md`.
- [ ] P20C-4: focused `tests/test_nbpolar_l2_disclosure_backoff.py`
  (synthetic/injected small arrays plus scripted seams and tiny-n real SC;
  fresh seeds; temporary roots; `pytest -p no:cacheprovider`) asserting
  the single-step disclosure differential, accounting, endpoint
  separation, the dual overlap gate, resource path, and the
  no-production-invocation rule; plus the packet-scoped predecessor
  suites green with zero protected opens.
- [ ] P20C-5: `P20C_FREEZE.md` + `P20C_IMPLEMENTATION_NOTES.md` in the packet
  queue directory and this P20C spec/tasks delta; this doc authorizes
  nothing (no Stage-B execution, no self-acceptance).
- [ ] P20C-6: independent Pre-EXECUTE review of the frozen command,
  population, cap, disclosure-step freeze, budgets, tag/domain
  separation, truth/accounting gates, tests and target absence (main
  thread + reviewer; separate gate, not this task).
- [ ] P20C-7: exactly one authorized nine-record three-arm attempt with the
  frozen command; the single attempt is consumed at the first protected
  content open with no rerun/reopen/seed/parameter/arm change (separate
  Stage-B authorization required; not authorized here).
- [ ] P20C-8: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, B1-vs-B0 disclosure
  comparison, NLL/disclosure accounting, oracle isolation, gates, input
  stats, resources and the five-file inventory from the artifacts
  (separate gate, not this task).
- [ ] P20C-9: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive single-factor
  development diagnostic, not real-frame FER, efficiency, key-rate,
  scaling, qualification or promotion evidence either way, and the oracle
  B2 arm is never an operational or deployable result.

Evidence (Stage A only; Stage B not run): `P20C_FREEZE.md`,
`P20C_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20C-L2-DISCLOSURE-BACKOFF/l2_disclosure_backoff/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20E +1024 confirmation tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20E-PLUS1024-CONFIRMATION/`
(`TASK_PACKET.md`, 334 lines, frozen; Tier-Y decision-gate packet).
Predecessor: P20C
`TARGET_EMPIRICAL_N32768_DEV_L2_DISCLOSURE_BACKOFF_COMPLETE_ACCEPTED_DESCRIPTIVE`
+ P20A `IMPLEMENTATION_ACCEPTED`. Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 (reproducible
reliability: confirm the frozen candidate on new blocks/sessions).
Stage A authorized separately; it permits no protected read (not even
stat), no real-data decoder execution, no Stage-B output root, no
disclosure or construction change of any kind, no closed-block /
consumed-VAL-pool / consumed-P20C-block tuning or peeking, no second
disclosure step, no alternative-construction second factor, no
efficiency tuning, no SCL/new kernel/model/schema, no overwrite under
`results/` or `comparison_bench/outputs_comparison/`, and no
commit/push. Stage B needs an independent Pre-EXECUTE PASS plus a
separate pasted authorization.

- [ ] P20E-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py` plus the `construction.py` / `prior.py` /
  `sc.py` contracts as called); change no shared logic.
- [ ] P20E-2: implement the thin runner
  `formal_ir/nbpolar/plus1024_confirmation.py` reusing P18 loading and
  the P16 operational helpers read-only: hardcoded three arms
  (`B0_sc_base` base K1=319/K2=6492 via accepted
  `run_operational_block`; `B1_L2plus` base + the carried-over +1024 L2
  step via frozen-order-prefix extension on the same frozen L2 order,
  all else identical, 2 SC + 1 tag per block; `B2_true_l1_diagnostic`
  base K2 via accepted   `run_oracle_control_block`, oracle-isolated); new
  P20E tag domains (new master, new seed prefix); NEW-block TRAIN formation
  (384..511 / 512..639 / 640..767, remainder 768..1199 never used,
  counted but never decoded) disjoint from consumed P20C DEV 0..383 AND
  consumed VAL 1200..1599 AND closed HOLD 1600..1983 by a triple
  fail-closed gate (P20C-consumed first); five files with per-(arm,
  block) checkpointing; P20A resource passthrough and endpoint
  separation.
- [ ] P20E-3: freeze the zero-tuning carry-over (ΔK2=+1024, K2 6492→7516,
  K_total 6811→7835, order-prefix rule, all algorithm inputs
  byte-identical to P20C), the new-block population, the carried-over
  per-arm disclosure caps (34119 / 39239 / 32524 key bits per block +
  327743 public bits per tag, ~10.41% / ~11.97% of raw, B1 delta +5120),
  the exact Stage-B command (new P20E tag master, 15-SC / 9-tag budget,
  600-s / 2-GiB / single-thread envelope), and the SC/tag/wall/RSS
  budgets in `P20E_FREEZE.md`.
- [ ] P20E-4: focused `tests/test_nbpolar_plus1024_confirmation.py`
  (synthetic/injected small arrays plus scripted seams and tiny-n real
  SC; fresh test-local seeds (seven, disjoint from all frozen
  masters/streams/probes); temporary roots;
  `pytest -p no:cacheprovider`) asserting the zero-tuning carry-over
  against the P20C module, the single-step disclosure differential,
  accounting, endpoint separation, the triple overlap gate (P20C
  first), the declared-remainder measurement, resource path, and the
  no-production-invocation rule; plus the packet-scoped predecessor
  suites green with zero protected opens.
- [ ] P20E-5: `P20E_FREEZE.md` + `P20E_IMPLEMENTATION_NOTES.md` in the
  packet queue directory and this P20E spec/tasks delta; this doc
  authorizes nothing (no Stage-B execution, no self-acceptance).
- [ ] P20E-6: independent Pre-EXECUTE review of the frozen command,
  population, cap, carry-over freeze, budgets, tag/domain separation,
  truth/accounting gates, tests and target absence (main thread +
  reviewer; separate gate, not this task).
- [ ] P20E-7: exactly one authorized nine-record three-arm attempt with
  the frozen command; the single attempt is consumed at the first
  protected content open with no rerun/reopen/seed/parameter/arm change
  (separate Stage-B authorization required; not authorized here).
- [ ] P20E-8: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, B1-vs-B0 confirmation
  comparison, NLL/disclosure accounting, oracle isolation, gates, input
  stats, resources and the five-file inventory from the artifacts
  (separate gate, not this task).
- [ ] P20E-9: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive zero-tuning
  confirmation diagnostic, not real-frame FER, efficiency, key-rate,
  scaling, qualification or promotion evidence either way, and the
  oracle B2 arm is never an operational or deployable result. The
  positive (efficiency-optimization) / negative (P20D candidate) branch
  decision belongs to later planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `P20E_FREEZE.md`,
`P20E_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20E-PLUS1024-CONFIRMATION/plus1024_confirmation/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20F +1024 extension tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION/`
(`TASK_PACKET.md`, 357 lines, frozen; Tier-Y decision-gate packet).
Predecessor: P20E
`TARGET_EMPIRICAL_N32768_DEV_PLUS1024_CONFIRMATION_COMPLETE_ACCEPTED_DESCRIPTIVE`
+ P20A `IMPLEMENTATION_ACCEPTED`. Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 (reproducible
reliability: confirm the frozen candidate on new blocks/sessions).
Stage A authorized separately; it permits no protected read (not even
stat), no real-data decoder execution, no Stage-B output root, no
disclosure or construction change of any kind, no closed-block /
consumed-VAL-pool / consumed-P20C-block / consumed-P20E-block tuning or
peeking, no second disclosure step, no alternative-construction second
factor, no efficiency tuning, no SCL/new kernel/model/schema, no
overwrite under `results/` or `comparison_bench/outputs_comparison/`,
and no commit/push. Stage B needs an independent Pre-EXECUTE PASS plus a
separate pasted authorization.

- [ ] P20F-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py` plus the
  `construction.py` / `prior.py` / `sc.py` contracts as called); change
  no shared logic.
- [ ] P20F-2: implement the thin runner
  `formal_ir/nbpolar/plus1024_extension.py` reusing P18 loading and
  the P16 operational helpers read-only: hardcoded three arms
  (`B0_sc_base` base K1=319/K2=6492 via accepted
  `run_operational_block`; `B1_L2plus` base + the carried-over +1024 L2
  step via frozen-order-prefix extension on the same frozen L2 order,
  all else identical, 2 SC + 1 tag per block; `B2_true_l1_diagnostic`
  base K2 via accepted `run_oracle_control_block`, oracle-isolated); new
  P20F tag domains (new master, new seed prefix); NEW-block TRAIN
  formation (768..895 / 896..1023 / 1024..1151, remainder 1152..1199
  never used, counted but never decoded) disjoint from consumed P20C DEV
  0..383 AND consumed P20E DEV 384..767 AND consumed VAL 1200..1599 AND
  closed HOLD 1600..1983 by a quadruple fail-closed gate (P20C-consumed
  first); five files with per-(arm, block) checkpointing; P20A resource
  passthrough and endpoint separation.
- [ ] P20F-3: freeze the zero-tuning carry-over (ΔK2=+1024, K2 6492→7516,
  K_total 6811→7835, order-prefix rule, all algorithm inputs
  byte-identical to P20C/P20E), the new-block population, the carried-over
  per-arm disclosure caps (34119 / 39239 / 32524 key bits per block +
  327743 public bits per tag, ~10.41% / ~11.97% of raw, B1 delta +5120),
  the exact Stage-B command (new P20F tag master, 15-SC / 9-tag budget,
  600-s / 2-GiB / single-thread envelope), and the SC/tag/wall/RSS
  budgets in `P20F_FREEZE.md`.
- [ ] P20F-4: focused `tests/test_nbpolar_plus1024_extension.py`
  (synthetic/injected small arrays plus scripted seams and tiny-n real
  SC; fresh test-local seeds (seven, disjoint from all frozen
  masters/streams/probes); temporary roots;
  `pytest -p no:cacheprovider`) asserting the zero-tuning carry-over
  against the P20E module, the single-step disclosure differential,
  accounting, endpoint separation, the quadruple overlap gate (P20C
  first), the declared-remainder measurement, resource path, and the
  no-production-invocation rule; plus the packet-scoped predecessor
  suites green with zero protected opens.
- [ ] P20F-5: `P20F_FREEZE.md` + `P20F_IMPLEMENTATION_NOTES.md` in the
  packet queue directory and this P20F spec/tasks delta; this doc
  authorizes nothing (no Stage-B execution, no self-acceptance).
- [ ] P20F-6: independent Pre-EXECUTE review of the frozen command,
  population, cap, carry-over freeze, budgets, tag/domain separation,
  truth/accounting gates, tests and target absence (main thread +
  reviewer; separate gate, not this task).
- [ ] P20F-7: exactly one authorized nine-record three-arm attempt with
  the frozen command; the single attempt is consumed at the first
  protected content open with no rerun/reopen/seed/parameter/arm change
  (separate Stage-B authorization required; not authorized here).
- [ ] P20F-8: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, B1-vs-B0 extension
  comparison, NLL/disclosure accounting, oracle isolation, gates, input
  stats, resources and the five-file inventory from the artifacts
  (separate gate, not this task).
- [ ] P20F-9: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive zero-tuning
  extension diagnostic, not real-frame FER, efficiency, key-rate,
  scaling, qualification or promotion evidence either way, and the
  oracle B2 arm is never an operational or deployable result. The
  positive (independent-session / efficiency-optimization) / negative
  (P20D candidate / minimality-probe) branch decision belongs to later
  planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `P20F_FREEZE.md`,
`P20F_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION/plus1024_extension/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20G +1024 independent-session tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/`
(`TASK_PACKET.md`, frozen; Tier-Y decision-gate packet).
Predecessor: P20F
`TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE_ACCEPTED_DESCRIPTIVE`
+ P20A `IMPLEMENTATION_ACCEPTED`. Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 (reproducible
reliability: confirm the frozen candidate on new blocks/sessions).
Stage A authorized separately; it permits no protected read (not even
stat — including the 1.5M DEV file and the reserved 2M file), no
real-data decoder execution, no Stage-B output root, no disclosure or
construction change of any kind, no per-session prior refit, no
closed-block / consumed-1M-pool / reserved-2M tuning or peeking, no
second disclosure step, no alternative-construction second factor, no
efficiency tuning, no SCL/new kernel/model/schema, no overwrite under
`results/` or `comparison_bench/outputs_comparison/`, and no
commit/push. Stage B needs an independent Pre-EXECUTE PASS plus a
separate pasted authorization.

- [ ] P20G-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py` plus the `construction.py` / `prior.py` /
  `sc.py` contracts as called); change no shared logic.
- [ ] P20G-2: implement the thin runner
  `formal_ir/nbpolar/plus1024_independent_session.py` reusing P18 loading
  and the P16 operational helpers read-only: hardcoded three arms
  (`B0_sc_base` base K1=319/K2=6492 via accepted
  `run_operational_block`; `B1_L2plus` base + the carried-over +1024 L2
  step via frozen-order-prefix extension on the same frozen L2 order,
  all else identical, 2 SC + 1 tag per block; `B2_true_l1_diagnostic`
  base K2 via accepted `run_oracle_control_block`, oracle-isolated); new
  P20G tag domains (new master, new seed prefix); NEW-session TRAIN
  formation (first 384 TRAIN frames of the 1.5M file → blocks 0..127 /
  128..255 / 256..383, remainder 384..1659 never used, counted but never
  decoded) under a fail-closed double gate (cross-file source-tag+digest
  gate against the 1M full pool and the reserved 2M file first, then the
  intra-file DEV-vs-VAL/HOLD overlap gate); five files with per-(arm,
  block) checkpointing; P20A resource passthrough and endpoint
  separation.
- [ ] P20G-3: freeze the zero-tuning carry-over (ΔK2=+1024, K2 6492→7516,
  K_total 6811→7835, order-prefix rule, all algorithm inputs
  byte-identical to P20C/P20E/P20F; Model-F cross-session use recorded
  as a to-be-verified assumption for Pre-EXECUTE, no refit fallback),
  the new-session population, the carried-over per-arm disclosure caps
  (34119 / 39239 / 32524 key bits per block + 327743 public bits per
  tag, ~10.41% / ~11.97% of raw, B1 delta +5120), the exact Stage-B
  command (new P20G tag master, `--source 1p5M` vocabulary, 15-SC /
  9-tag budget, 600-s / 2-GiB / single-thread envelope), and the SC/tag/
  wall/RSS budgets in `P20G_FREEZE.md`.
- [ ] P20G-4: focused `tests/test_nbpolar_plus1024_independent_session.py`
  (synthetic/injected small arrays plus scripted seams and tiny-n real
  SC; fresh test-local seeds (seven, disjoint from all frozen
  masters/streams/probes); temporary roots;
  `pytest -p no:cacheprovider`) asserting the zero-tuning carry-over
  against the P20F module, the single-step disclosure differential,
  accounting, endpoint separation, the double gate (source-first, with
  2M zero-contact), the declared-remainder measurement, the size-pinned
  source identity, resource path, and the no-production-invocation
  rule; plus the packet-scoped predecessor suites green with zero
  protected opens.
- [ ] P20G-5: `P20G_FREEZE.md` + `P20G_IMPLEMENTATION_NOTES.md` in the
  packet queue directory and this P20G spec/tasks delta; this doc
  authorizes nothing (no Stage-B execution, no self-acceptance).
- [ ] P20G-6: independent Pre-EXECUTE review of the frozen command,
  population, cap, carry-over freeze, cross-session prior assumption,
  budgets, tag/domain separation, truth/accounting gates, tests and
  target absence (main thread + reviewer; separate gate, not this task).
- [ ] P20G-7: exactly one authorized nine-record three-arm attempt with
  the frozen command; the single attempt is consumed at the first
  protected content open with no rerun/reopen/seed/parameter/arm change
  (separate Stage-B authorization required; not authorized here).
- [ ] P20G-8: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, B1-vs-B0 extension
  comparison, NLL/disclosure accounting, oracle isolation, gates, input
  stats, resources and the five-file inventory from the artifacts
  (separate gate, not this task).
- [ ] P20G-9: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_INDEPENDENT_SESSION_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive zero-tuning
  independent-session diagnostic, not real-frame FER, efficiency,
  key-rate, scaling, qualification or promotion evidence either way,
  and the oracle B2 arm is never an operational or deployable result.
  The positive (efficiency-optimization) / negative (P20D candidate) /
  maintain (reserved-2M vs minimality-probe) branch decision belongs to
  later planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `P20G_FREEZE.md`,
`P20G_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20G-1P5M-183806/independent_session/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20H per-session-calibration +1024 tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/`
(`TASK_PACKET.md`, frozen; Tier-Y decision-gate packet).
Predecessor: P20G
`BLOCKED_TARGET_POPULATION_CONTRACT_ACCEPTED_TERMINAL_DESCRIPTIVE`
(1M literals H1 0.02428054681872374 / H2 0.7767572780789994 / TOTAL
0.8010378248977232 mismatch the 1.5M counts array; NPZ open 1/1 and
attempt 1/1 SPENT; DEV 0 opens) + P20A `IMPLEMENTATION_ACCEPTED`.
Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 (reproducible
reliability: confirm the frozen candidate on new blocks/sessions).
Stage A authorized separately; it permits exactly ONE protected content
open (the 1.5M TRAIN counts-calibration open, digest-recorded) and no
1.5M DEV/VAL/HOLD content open or stat, no 1M-pool or reserved-2M
open/stat/listing/read in any form, no real-data decoder execution, no
Stage-B output root, no disclosure/construction/calibration change
beyond the frozen §3 program, no calibration on DEV and no refit after
any DEV contact, no closed-block / consumed-1M-pool / reserved-2M
tuning or peeking, no efficiency tuning, no SCL/new kernel/model/schema,
no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and no commit/push. Stage B
needs an independent Pre-EXECUTE PASS (explicitly adjudicating the §3
calibration-vs-tuning gate (i)–(iv)) plus a separate pasted
authorization.

- [ ] P20H-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py` plus the
  `construction.py` / `prior.py` / `sc.py` contracts as called); change
  no shared logic.
- [ ] P20H-2: freeze the §3 calibration program isomorphic to the
  accepted P0/P2 Model-F concentration procedure (same
  formula/smoothing/flow, banned per-cell twin excluded,
  lambda-procedure literal 137.3823795883264 + floor 1e-15 + packing
  `A = 32*U1 + U2` + `FULL_BOB_ONLY` pinned) with input = 1.5M TRAIN
  counts ONLY; execute the single declared counts-calibration open and
  write `per_session_calibration/` (plan + input identity +
  digest-pinned `calibrated_prior.npz` + recalibrated H1/H2/TOTAL
  literals + report) with DEV-zero-contact evidenced by the one-open
  guards.
- [ ] P20H-3: implement the thin runner
  `formal_ir/nbpolar/plus1024_per_session_confirmation.py` reusing P18
  loading and the P16 operational helpers read-only: hardcoded three
  arms (`B0_sc_base` base K1=319/K2=6492 via accepted
  `run_operational_block`; `B1_L2plus` base + the carried-over +1024 L2
  step via frozen-order-prefix extension on the same frozen L2 order,
  all else identical, 2 SC + 1 tag per block; `B2_true_l1_diagnostic`
  base K2 via accepted `run_oracle_control_block`, oracle-isolated);
  the Stage-A frozen prior loaded read-only behind a
  calibration-identity digest gate (no counts NPZ open in Stage B); new
  P20H tag domains (master 2026092220, seed prefix
  `nbpolar-p20h-per-session-calibration-seed`); P20G-unconsumed 1.5M
  TRAIN formation (first 384 TRAIN frames → blocks 0..127 / 128..255 /
  256..383, remainder 384..1659 never used, counted but never decoded)
  under a fail-closed triple gate (cross-file source-tag+digest gate
  against the 1M full pool and the reserved 2M file first, then the
  intra-file DEV-vs-VAL/HOLD overlap gate, then the
  calibration-identity gate); five files with per-(arm, block)
  checkpointing; P20A resource passthrough and endpoint separation.
- [ ] P20H-4: freeze the carried-over +1024 step (ΔK2=+1024, K2
  6492→7516, K_total 6811→7835, order-prefix rule), the P16
  construction/order/K migration (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`),
  the population, the carried-over per-arm disclosure caps (34119 /
  39239 / 32524 key bits per block + 327743 public bits per tag,
  ~10.41% / ~11.97% of raw, B1 delta +5120), the exact Stage-B command
  (new P20H tag master, `--prior` frozen digest path, `--source 1p5M`
  vocabulary, 15-SC / 9-tag budget, 600-s / 2-GiB / single-thread
  envelope), and the SC/tag/wall/RSS budgets in `P20H_FREEZE.md`.
- [ ] P20H-5: focused `tests/test_nbpolar_per_session_calibration.py`
  (synthetic counts + stub loader; fresh test-local seeds 2026092221..
  2026092227; temporary roots; `pytest -p no:cacheprovider`) asserting
  calibration-program isomorphism against an independent literal
  formula, the lambda provenance pin, the single-open audit, zero
  tuning (lambda/floor pin refusals), the manifest cross-check and the
  five-file inventory; plus focused
  `tests/test_nbpolar_plus1024_per_session_confirmation.py` (36 tests:
  synthetic priors + scripted seams and tiny-n real SC; same seeds and
  settings) asserting the P20F carry-over, the single-step disclosure
  differential, accounting, endpoint separation, the triple gate
  (source-first, calibration-identity last, with 2M zero-contact), the
  declared-remainder measurement, the digest-pinned prior identity, the
  resource path and the no-production-invocation rule; plus the
  packet-scoped predecessor suites green with the declared single
  counts-calibration open audit.
- [ ] P20H-6: `P20H_FREEZE.md` + `P20H_IMPLEMENTATION_NOTES.md` in the
  packet queue directory and this P20H spec/tasks delta; this doc
  authorizes nothing (no Stage-B execution, no self-acceptance).
- [ ] P20H-7: independent Pre-EXECUTE review of the frozen command,
  population, cap, calibration freeze (§3 gate (i)–(iv) adjudication),
  budgets, tag/domain separation, truth/accounting gates, tests and
  target absence (main thread + reviewer; separate gate, not this task).
- [ ] P20H-8: exactly one authorized nine-record three-arm attempt with
  the frozen command; the single DEV attempt is consumed at the first
  DEV content open with no rerun/reopen/seed/parameter/arm change
  (separate Stage-B authorization required; not authorized here).
- [ ] P20H-9: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, B1-vs-B0 extension
  comparison, NLL/disclosure accounting, oracle isolation, gates, input
  stats, resources and the five-file inventory from the artifacts
  (separate gate, not this task).
- [ ] P20H-10: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_DEV_PLUS1024_PER_SESSION_CALIBRATION_COMPLETE`
  or `BLOCKED(<earliest gate>)`; this is a descriptive
  per-session-calibration diagnostic, not real-frame FER, efficiency,
  key-rate, scaling, qualification or promotion evidence either way,
  and the oracle B2 arm is never an operational or deployable result.
  The calibration-positive (efficiency round) / confirmation-negative
  (P20D candidate) / calibration-blocked (P20H-R1 rework) branch
  decision belongs to later planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `per_session_calibration/`
(five files), `P20H_FREEZE.md`, `P20H_IMPLEMENTATION_NOTES.md`; output
root
`.workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_confirmation/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20I L1-disclosure +128 tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/`
(`TASK_PACKET.md`, frozen; Tier-Y decision-gate packet).
Predecessor: P20H
`TARGET_EMPIRICAL_N32768_DEV_PLUS1024_PER_SESSION_CALIBRATION_COMPLETE_ACCEPTED_DESCRIPTIVE`
(Stage-B single attempt SPENT 1/1; DEV 1/1 SPENT on 1.5M TRAIN 0..383;
9/9 records; 21/21 gates PASS; B0 0/3 verify_failed + B1 0/3
verify_failed + b1_restored 0/3, first errors 16/L1 + 6/L1 + 8/L1; B2
oracle 3/3 exact isolated; undetected 0; SC 15/15; tags 9/9; recount 0;
2M pristine by non-access) + P20A `IMPLEMENTATION_ACCEPTED`. P19
precedent: `l1_plus` +128 L1 (K1 319→447, leakage 34759) repaired the
two L1 errors on the same three HOLD blocks. Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 (reproducible
reliability: confirm the frozen candidate on new blocks/sessions).
Stage A authorized separately; it permits ZERO protected content opens
(counts 0/0 with no NPZ open, the §3 digest check is a worktree-file
read only; no 1.5M DEV/VAL/HOLD content open or stat, DEV 0/1, HOLD
0/1) and no 1M-pool or reserved-2M open/stat/listing/read in any form
(2M pristine by non-access), no real-data decoder execution, no
Stage-B output root, no disclosure/construction/prior change beyond
the frozen §§2-3/§§5-6 pins, no prior refit/resmoothing/relambda and
no calibration on DEV, no closed-block / consumed-1M-pool / P20H-DEV /
reserved-2M tuning or peeking, no second L1 tier or L2 step, no
efficiency tuning, no SCL/new kernel/model/schema, no overwrite under
`results/` or `comparison_bench/outputs_comparison/`, and no
commit/push. Stage B needs an independent Pre-EXECUTE PASS
(explicitly adjudicating the §3 reuse pins and the §4 quadruple gate)
plus a separate pasted authorization.

- [ ] P20I-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest function + formula pins only),
  `plus1024_per_session_confirmation.py` (gate/population pattern
  reference) plus the `construction.py` / `prior.py` / `sc.py`
  contracts as called; change no shared logic.
- [ ] P20I-2: freeze the §3 prior-reuse pins (P20H `calibrated_prior.npz`
  canonical digest
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
  + lambda 137.3823795883264 + floor 1e-15 + recalibrated H1/H2/TOTAL
  literals, verified by a worktree-file digest recomputation ONLY —
  zero NPZ/parquet content opens; V25 counts NPZ never opened, no
  refit path in the runner).
- [ ] P20I-3: implement the thin runner
  `formal_ir/nbpolar/l1_disclosure_1p5m.py` reusing P18 loading and the
  P16 operational helpers read-only: hardcoded three arms
  (`C0_sc_base` base K1=319/K2=6492 via accepted
  `run_operational_block`; `C1_L1plus` base + the frozen +128 L1 step
  via frozen-order-prefix extension K1=447/K2=6492 on the same frozen
  L1 order, all else identical, 2 SC + 1 tag per block;
  `C2_true_l1_diagnostic` base K2 via accepted
  `run_oracle_control_block`, oracle-isolated, deployable=false); the
  §3 frozen prior loaded read-only behind a calibration-identity
  digest gate (no counts NPZ open in Stage B); new P20I tag domains
  (master 2026092230, seed prefix
  `nbpolar-p20i-l1-disclosure-1p5m-seed`); next-segment 1.5M TRAIN
  formation (384 TRAIN frames 384..767 → blocks 384..511 / 512..639 /
  640..767, remainder 768..1659 never used, counted but never decoded)
  under a fail-closed quadruple gate (cross-file source-tag+digest
  gate against the 1M full pool and the reserved 2M file first, then
  the intra-file DEV-vs-VAL/HOLD overlap gate with VAL first, then
  the consumed-P20H-DEV 0..383 exclusion gate, then the
  calibration-identity gate); five files with per-(arm, block)
  checkpointing; P20A resource passthrough and endpoint separation.
- [ ] P20I-4: freeze the +128 step (ΔK1=+128, K1 319→447, K_total
  6811→6939, order-prefix rule isomorphic with the K2 rule), the P16
  construction/order/K migration (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`),
  the population (DEV 384..767, remainder 768..1659), the
  preregistered per-arm disclosure caps (34119 / 34759 / 32524 key
  bits per block + 327743 public bits per tag, ~10.41% / ~10.61% of
  raw, C1 delta +640 = 5·128; planned totals 304206 key (operational
  206634 + oracle 97572) / 2949687 public), the exact Stage-B command
  (new P20I tag master, `--prior` frozen digest path, `--source 1p5M`
  vocabulary, `--dev-frames 384 767`, `--remainder-frames 768 1659`,
  15-SC / 9-tag budget, 600-s / 2-GiB / single-thread envelope), and
  the SC/tag/wall/RSS budgets in `P20I_FREEZE.md`.
- [ ] P20I-5: focused `tests/test_nbpolar_l1_disclosure_1p5m.py` (36
  tests: synthetic priors + scripted seams and tiny-n real SC; fresh
  test-local seeds 2026092231..2026092237; temporary roots; `pytest -p
  no:cacheprovider`) asserting the P20H carry-over (N/floor/base
  K/caps/prior-reuse/budgets/gates/provenance), the single-step L1
  disclosure differential (C1 k1=447 on the same frozen L1 order
  object as C0, key-bit delta exactly +640, order-prefix landing),
  accounting, endpoint separation, the quadruple gate (source-first,
  VAL-before-HOLD, P20H-DEV exclusion, calibration-identity last,
  with 2M zero-contact), the declared-remainder measurement, the
  digest-pinned prior identity, the resource path and the
  no-production-invocation rule; plus the packet-scoped predecessor
  suites green with the zero-protected-open audit.
- [ ] P20I-6: `P20I_FREEZE.md` + `P20I_IMPLEMENTATION_NOTES.md` in the
  packet queue directory and this P20I spec/tasks delta; this doc
  authorizes nothing (no Stage-B execution, no self-acceptance).
- [ ] P20I-7: independent Pre-EXECUTE review of the frozen command,
  population, cap, prior-reuse freeze (§3 pins) and quadruple gate
  (§4), budgets, tag/domain separation, truth/accounting gates, tests
  and target absence (main thread + reviewer; separate gate, not this
  task).
- [ ] P20I-8: exactly one authorized nine-record three-arm attempt with
  the frozen command; the single DEV attempt is consumed at the first
  DEV content open with no rerun/reopen/seed/parameter/arm change
  (separate Stage-B authorization required; not authorized here).
- [ ] P20I-9: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, C1-vs-C0 disclosure
  comparison, NLL/disclosure accounting, oracle isolation, gates,
  input stats, resources and the five-file inventory from the
  artifacts (separate gate, not this task).
- [ ] P20I-10: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_DEV_L1_DISCLOSURE_1P5M_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive +128
  L1-disclosure diagnostic, not real-frame FER, efficiency, key-rate,
  scaling, qualification or promotion evidence either way, and the
  oracle C2 arm is never an operational or deployable result. The
  C1-restoration (maintain-confirmation) / C1-zero-restoration (P20D
  candidate) / maintain-only branch decision belongs to later
  planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `P20I_FREEZE.md`,
`P20I_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/l1_disclosure_1p5m/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20J L1-dose-escalation +256 tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M/`
(`TASK_PACKET.md`, frozen; Tier-Y decision-gate packet).
Predecessor: P20I
`TARGET_EMPIRICAL_N32768_DEV_L1_DISCLOSURE_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
(Stage-B single attempt SPENT 1/1; counts-calibration opens 0/0; DEV
open 1/1 SPENT on 1.5M TRAIN 384..767; 9/9 records; 21/21 gates PASS;
C0 base-K1 0/3 verify_failed + C1 L1+128 0/3 verify_failed +
c1_restored 0/3; all six operational first errors L1-layer — blk0 2/L1
→ 2/L1 unchanged, blk1 17/L1 → 1/L1 moved earlier, blk2 13/L1 → 16/L1
moved later; raw SER ~0.2520/0.2526/0.2535; C2 oracle 3/3 exact
isolated; undetected 0; SC 15/15; tags 9/9; recount 0; key 304206 /
public 2949687; 2M pristine by non-access) + P20H precedent
(calibrated-prior +1024 confirmation on 1.5M TRAIN 0..383) + P20A
`IMPLEMENTATION_ACCEPTED`. Dose decision (frozen, not re-argued):
+128 (P20I) moved first-error coordinates but restored nothing — the
+128 minimal dose is falsified as a fix while proving L1 sensitivity;
+256 doubles the P20I dose (K1 319→575, keyΔ +1280) before any larger
jump, preserving single-step dose-response resolution. Strategy
parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2
(reproducible reliability: confirm the frozen candidate on new
blocks/sessions). Stage A authorized separately; it permits ZERO
protected content opens (counts 0/0 with no NPZ open, the §3 digest
check is a worktree-file read only; no 1.5M DEV/VAL/HOLD content open
or stat, DEV 0/1, HOLD 0/1) and no 1M-pool or reserved-2M
open/stat/listing/read in any form (2M pristine by non-access), no
real-data decoder execution, no Stage-B output root, no
disclosure/construction/prior change beyond the frozen §§2-3/§§5-6
pins, no prior refit/resmoothing/relambda and no calibration on DEV,
no closed-block / consumed-1M-pool / P20H-DEV / P20I-DEV /
reserved-2M tuning or peeking, no second L1 tier or L2 step, no
efficiency tuning, no SCL/new kernel/model/schema, no overwrite under
`results/` or `comparison_bench/outputs_comparison/`, and no
commit/push. Stage B needs an independent Pre-EXECUTE PASS
(explicitly adjudicating the §3 reuse pins and the §4 quintuple gate)
plus a separate pasted authorization.

- [ ] P20J-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest function + formula pins only),
  `plus1024_per_session_confirmation.py` (gate/population pattern
  reference), `l1_disclosure_1p5m.py` (gate/population/cap pattern
  reference) plus the `construction.py` / `prior.py` / `sc.py`
  contracts as called; change no shared logic.
- [ ] P20J-2: freeze the §3 prior-reuse pins (P20H `calibrated_prior.npz`
  canonical digest
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
  + lambda 137.3823795883264 + floor 1e-15 + recalibrated H1/H2/TOTAL
  literals, verified by a worktree-file digest recomputation ONLY —
  zero NPZ/parquet content opens; V25 counts NPZ never opened, no
  refit path in the runner).
- [ ] P20J-3: implement the thin runner
  `formal_ir/nbpolar/l1_dose_escalation_1p5m.py` reusing P18 loading
  and the P16 operational helpers read-only: hardcoded three arms
  (`D0_sc_base` base K1=319/K2=6492 via accepted
  `run_operational_block`; `D1_L1plus` base + the frozen +256 L1 step
  via frozen-order-prefix extension K1=575/K2=6492 on the same frozen
  L1 order, all else identical, 2 SC + 1 tag per block;
  `D2_true_l1_diagnostic` base K2 via accepted
  `run_oracle_control_block`, oracle-isolated, deployable=false); the
  §3 frozen prior loaded read-only behind a calibration-identity
  digest gate (no counts NPZ open in Stage B); new P20J tag domains
  (master 2026092240, seed prefix
  `nbpolar-p20j-l1-dose-escalation-1p5m-seed`); next-segment 1.5M
  TRAIN formation (384 TRAIN frames 768..1151 → blocks 768..895 /
  896..1023 / 1024..1151, remainder 1152..1659 never used, counted
  but never decoded) under a fail-closed quintuple gate (cross-file
  source-tag+digest gate against the 1M full pool and the reserved 2M
  file first, then the intra-file DEV-vs-VAL/HOLD overlap gate with
  VAL first, then the consumed-P20H-DEV 0..383 exclusion gate, then
  the consumed-P20I-DEV 384..767 exclusion gate, then the
  calibration-identity gate); five files with per-(arm, block)
  checkpointing; P20A resource passthrough and endpoint separation.
- [ ] P20J-4: freeze the +256 step (ΔK1=+256, K1 319→575, K_total
  6811→7067, order-prefix rule isomorphic with the K2 rule), the P16
  construction/order/K migration (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`),
  the population (DEV 768..1151, remainder 1152..1659), the
  preregistered per-arm disclosure caps (34119 / 35399 / 32524 key
  bits per block + 327743 public bits per tag, ~10.41% / ~10.80% of
  raw, D1 delta +1280 = 5·256; planned totals 306126 key (operational
  208554 + oracle 97572) / 2949687 public), the exact Stage-B command
  (new P20J tag master, `--prior` frozen digest path, `--source 1p5M`
  vocabulary, `--dev-frames 768 1151`, `--remainder-frames 1152 1659`,
  15-SC / 9-tag budget, 600-s / 2-GiB / single-thread envelope), and
  the SC/tag/wall/RSS budgets in `P20J_FREEZE.md`.
- [ ] P20J-5: focused `tests/test_nbpolar_l1_dose_escalation_1p5m.py` (36
  tests: synthetic priors + scripted seams and tiny-n real SC; fresh
  test-local seeds 2026092241..2026092247; temporary roots; `pytest -p
  no:cacheprovider`) asserting the P20I carry-over (N/floor/base
  K/caps/prior-reuse/budgets/gates/provenance), the single-step L1
  disclosure differential (D1 k1=575 on the same frozen L1 order
  object as D0, key-bit delta exactly +1280, order-prefix landing),
  accounting, endpoint separation, the quintuple gate (source-first,
  VAL-before-HOLD, P20H-DEV exclusion, P20I-DEV exclusion,
  calibration-identity last, with 2M zero-contact), the
  declared-remainder measurement, the digest-pinned prior identity,
  the resource path and the no-production-invocation rule; plus the
  packet-scoped predecessor suites green with the zero-protected-open
  audit.
- [ ] P20J-6: `P20J_FREEZE.md` + `P20J_IMPLEMENTATION_NOTES.md` in the
  packet queue directory and this P20J spec/tasks delta; this doc
  authorizes nothing (no Stage-B execution, no self-acceptance).
- [ ] P20J-7: independent Pre-EXECUTE review of the frozen command,
  population, cap, prior-reuse freeze (§3 pins) and quintuple gate
  (§4), budgets, tag/domain separation, truth/accounting gates, tests
  and target absence (main thread + reviewer; separate gate, not this
  task).
- [ ] P20J-8: exactly one authorized nine-record three-arm attempt with
  the frozen command; the single DEV attempt is consumed at the first
  DEV content open with no rerun/reopen/seed/parameter/arm change
  (separate Stage-B authorization required; not authorized here).
- [ ] P20J-9: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, D1-vs-D0 disclosure
  comparison, NLL/disclosure accounting, oracle isolation, gates,
  input stats, resources and the five-file inventory from the
  artifacts (separate gate, not this task).
- [ ] P20J-10: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_ESCALATION_1P5M_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive +256
  L1-dose-escalation diagnostic, not real-frame FER, efficiency,
  key-rate, scaling, qualification or promotion evidence either way,
  and the oracle D2 arm is never an operational or deployable result.
  The D1-restoration (maintain-confirmation) / D1-zero-restoration
  (P20D candidate) / maintain-only branch decision belongs to later
  planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `P20J_FREEZE.md`,
`P20J_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M/l1_dose_escalation_1p5m/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20K L1-dose-512 +512 tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/`
(`TASK_PACKET.md`, frozen; Tier-Y decision-gate packet).
Predecessor: P20J
`TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_ESCALATION_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
(Stage-B single attempt SPENT 1/1; counts-calibration opens 0/0; DEV
open 1/1 SPENT on 1.5M TRAIN 768..1151; 9/9 records; 21/21 gates PASS;
D0 base-K1 0/3 verify_failed + D1 L1+256 (K1 575, keyΔ +1280) 0/3
verify_failed + d1_restored 0/3; all six operational first errors
L1-layer with D1 coordinates all later — blk0 14/L1→23/L1, blk1
6/L1→25/L1, blk2 1/L1→21/L1; D2 oracle 3/3 exact isolated; undetected
0; SC 15/15; tags 9/9; recount 0; key 306126 / public 2949687; 2M
pristine by non-access) + P20I precedent (+128 L1 single-factor on
1.5M TRAIN 384..767, C0/C1 0/3, mixed first-error move) + P20H
precedent (calibrated-prior +1024 L2 confirmation on 1.5M TRAIN 0..383)
+ P20A `IMPLEMENTATION_ACCEPTED`. Dose decision (frozen, not
re-argued): +256 (P20J) delayed every first error but restored nothing
— the second dose is falsified as a fix while showing strictly
stronger causal activity than +128 (full deferral vs mixed move); +512
doubles the P20J dose (K1 319→831, keyΔ +2560 = 5·512) to COMPLETE the
+128/+256/+512 doubling chain before any larger jump or factor switch
(P20D deferred to the §16 zero-restoration branch), preserving
single-step dose-response resolution and giving the disclosure route a
clean closure condition. Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2
(reproducible reliability: confirm the frozen candidate on new
blocks/sessions). Stage A authorized separately; it permits ZERO
protected content opens (counts 0/0 with no NPZ open, the §3 digest
check is a worktree-file read only; no 1.5M DEV/VAL/HOLD content open
or stat, DEV 0/1, HOLD 0/1) and no 1M-pool or reserved-2M
open/stat/listing/read in any form (2M pristine by non-access), no
real-data decoder execution, no Stage-B output root, no
disclosure/construction/prior change beyond the frozen §§2-3/§§5-6
pins, no prior refit/resmoothing/relambda and no calibration on DEV,
no closed-block / consumed-1M-pool / P20H-DEV / P20I-DEV / P20J-DEV /
reserved-2M tuning or peeking, no second L1 tier or L2 step, no
efficiency tuning, no SCL/new kernel/model/schema, no overwrite under
`results/` or `comparison_bench/outputs_comparison/`, and no
commit/push. Stage B needs an independent Pre-EXECUTE PASS
(explicitly adjudicating the §3 reuse pins and the §4 sextuple gate)
plus a separate pasted authorization.

- [ ] P20K-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest function + formula pins only),
  `plus1024_per_session_confirmation.py` (gate/population pattern
  reference), `l1_disclosure_1p5m.py` (gate/population/cap pattern
  reference), `l1_dose_escalation_1p5m.py` (gate/population/cap pattern
  reference) plus the `construction.py` / `prior.py` / `sc.py`
  contracts as called; change no shared logic.
- [ ] P20K-2: freeze the §3 prior-reuse pins (P20H `calibrated_prior.npz`
  canonical digest
  `e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b`
  + lambda 137.3823795883264 + floor 1e-15 + recalibrated H1/H2/TOTAL
  literals, verified by a worktree-file digest recomputation ONLY —
  zero NPZ/parquet content opens; V25 counts NPZ never opened, no
  refit path in the runner).
- [ ] P20K-3: implement the thin runner
  `formal_ir/nbpolar/l1_dose_512_1p5m.py` reusing P18 loading
  and the P16 operational helpers read-only: hardcoded three arms
  (`E0_sc_base` base K1=319/K2=6492 via accepted
  `run_operational_block`; `E1_L1plus512` base + the frozen +512 L1
  step via frozen-order-prefix extension K1=831/K2=6492 on the same
  frozen L1 order, all else identical, 2 SC + 1 tag per block;
  `E2_true_l1_diagnostic` base K2 via accepted
  `run_oracle_control_block`, oracle-isolated, deployable=false); the
  §3 frozen prior loaded read-only behind a calibration-identity
  digest gate (no counts NPZ open in Stage B); new P20K tag domains
  (master 2026092250, seed prefix
  `nbpolar-p20k-l1-dose-512-1p5m-seed`); next-segment 1.5M
  TRAIN formation (384 TRAIN frames 1152..1535 → blocks 1152..1279 /
  1280..1407 / 1408..1535, remainder 1536..1659 never used, counted
  but never decoded) under a fail-closed sextuple gate (cross-file
  source-tag+digest gate against the 1M full pool and the reserved 2M
  file first, then the intra-file DEV-vs-VAL/HOLD overlap gate with
  VAL first, then the consumed-P20H-DEV 0..383 exclusion gate, then
  the consumed-P20I-DEV 384..767 exclusion gate, then the
  consumed-P20J-DEV 768..1151 exclusion gate, then the
  calibration-identity gate); five files with per-(arm, block)
  checkpointing; P20A resource passthrough and endpoint separation.
- [ ] P20K-4: freeze the +512 step (ΔK1=+512, K1 319→831, K_total
  6811→7323, order-prefix rule isomorphic with the K2 rule), the P16
  construction/order/K migration (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`),
  the population (DEV 1152..1535, remainder 1536..1659), the
  preregistered per-arm disclosure caps (34119 / 36679 / 32524 key
  bits per block + 327743 public bits per tag, ~10.41% / ~11.19% of
  raw, E1 delta +2560 = 5·512; planned totals 309966 key (operational
  212394 + oracle 97572) / 2949687 public), the exact Stage-B command
  (new P20K tag master, `--prior` frozen digest path, `--source 1p5M`
  vocabulary, `--dev-frames 1152 1535`, `--remainder-frames 1536 1659`,
  15-SC / 9-tag budget, 600-s / 2-GiB / single-thread envelope), and
  the SC/tag/wall/RSS budgets in `P20K_FREEZE.md`.
- [ ] P20K-5: focused `tests/test_nbpolar_l1_dose_512_1p5m.py` (36
  tests: synthetic priors + scripted seams and tiny-n real SC; fresh
  test-local seeds 2026092251..2026092257; temporary roots; `pytest -p
  no:cacheprovider`) asserting the P20J carry-over (N/floor/base
  K/caps/prior-reuse/budgets/gates/provenance), the single-step L1
  disclosure differential (E1 k1=831 on the same frozen L1 order
  object as E0, key-bit delta exactly +2560, order-prefix landing),
  accounting, endpoint separation, the sextuple gate (source-first,
  VAL-before-HOLD, P20H-DEV exclusion, P20I-DEV exclusion,
  P20J-DEV exclusion, calibration-identity last, with 2M
  zero-contact), the declared-remainder measurement, the digest-pinned
  prior identity, the resource path and the no-production-invocation
  rule; plus the packet-scoped predecessor suites green with the
  zero-protected-open audit.
- [ ] P20K-6: `P20K_FREEZE.md` + `P20K_IMPLEMENTATION_NOTES.md` in the
  packet queue directory and this P20K spec/tasks delta; this doc
  authorizes nothing (no Stage-B execution, no self-acceptance).
- [ ] P20K-7: independent Pre-EXECUTE review of the frozen command,
  population, cap, prior-reuse freeze (§3 pins) and sextuple gate
  (§4), budgets, tag/domain separation, truth/accounting gates, tests
  and target absence (main thread + reviewer; separate gate, not this
  task).
- [ ] P20K-8: exactly one authorized nine-record three-arm attempt with
  the frozen command; the single DEV attempt is consumed at the first
  DEV content open with no rerun/reopen/seed/parameter/arm change
  (separate Stage-B authorization required; not authorized here).
- [ ] P20K-9: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, E1-vs-E0 disclosure
  comparison, NLL/disclosure accounting, oracle isolation, gates,
  input stats, resources and the five-file inventory from the
  artifacts (separate gate, not this task).
- [ ] P20K-10: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_512_1P5M_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive +512
  L1-dose-512 diagnostic, not real-frame FER, efficiency,
  key-rate, scaling, qualification or promotion evidence either way,
  and the oracle E2 arm is never an operational or deployable result.
  The E1-restoration (maintain-confirmation) / E1-zero-restoration
  (close-the-disclosure-route) / maintain-only branch decision belongs
  to later planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `P20K_FREEZE.md`,
`P20K_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/l1_dose_512_1p5m/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20M raw-prior + session-budget tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/`
(`TASK_PACKET.md`, frozen; Tier-Y decision-gate packet).
Predecessor: P20K
`TARGET_EMPIRICAL_N32768_DEV_L1_DOSE_512_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
(Stage-B single attempt SPENT 1/1; counts-calibration opens 0/0; DEV open 1/1
SPENT on 1.5M TRAIN 1152..1535; 9/9 records; 21/21 gates PASS; E0 0/3 +
E1 L1+512 0/3 + e1_restored 0/3, all six operational first errors L1-layer; E2
oracle 3/3 exact isolated; undetected 0; SC 15/15; tags 9/9; recount 0; 2M
pristine by non-access) + X08 Tier-X probe
(`workspace/probes/nbpolar_x08_per_session_prior_entropy_audit/results.json`,
reviewer-go focused review all-PASS: λ=137.3823795883264 reproduces stored
H1/H2/TOTAL exactly; raw-MLE + 1e-15 floor + column-renorm variant gives
H1 0.025199496923753 / H2 0.800366554749543 / TOTAL 0.825566051673296 with
1,046,140/1,048,576 cells floor-hit and 0 zero columns; implied K_total 33285
vs 7020) + P20A `IMPLEMENTATION_ACCEPTED`. P20L
(`NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M`) is SUPERSEDED-BY-P20M per the 2026-09-19
user decision (Stage B never executed, zero consumption; files preserved);
its declared VAL DEV 1660..2043 is released to this successor. Factor decision
(frozen, not re-argued): the corrected raw-count prior + its session-derived
budget is ONE operating-point factor (prior and its same-run-H budget cannot
vary independently under S2-i). Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2 (reproducible
reliability: confirm the frozen candidate on new blocks/sessions). Stage A
authorized separately; it permits ZERO protected content opens (counts 0/0:
§3 derivation reads the digest-pinned worktree npz only, never the V25 counts
NPZ; no 1.5M DEV/VAL/HOLD content open or stat, DEV 0/1, HOLD 0/1) and no
1M-pool or reserved-2M open/stat/listing/read in any form (2M pristine by
non-access), no lambda anywhere, no K carried as an absolute from another
session (S2-i), no derivation on real frames, no real-data decoder execution,
no Stage-B output root, no second factor, no efficiency tuning, no SCL/new
kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and no commit/push. Stage B needs an
independent Pre-EXECUTE PASS (explicitly adjudicating the §3 derivation, the
§5 budget literal, the §4 gate family, and the §2 runner-delta design) plus a
separate pasted authorization.

- [ ] P20M-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`
  (import target; gate/population/order-file pattern references) plus the
  P13/P16 budget/split callsites (`target_n_scaling.budget_k_total`,
  `empirical_genie_scaling.select_empirical_split`,
  `target_n_scaling.allocate_layer_ks` as same-family reference only) and the
  `construction.py` / `prior.py` / `sc.py` contracts as called; change no
  shared logic.
- [ ] P20M-2: derive the §3 corrected prior (read `counts_ab` from the
  digest-reverified P20H worktree npz ONLY — worktree-file read, never a
  protected counts open; raw-count MLE + 1e-15 floor + column renormalize, no
  lambda anywhere, `derive_p1`/`derive_p2` under A=32*U1+U2 FULL_BOB_ONLY,
  `p_b` cross-check against column totals/total) and write the frozen
  artifact `raw_prior_1p5m.npz` (exact 10-key set with `f_raw` and
  `lambda_star` 0.0) with its canonical digest + session H1/H2/TOTAL literals
  + floor-hit count/rate pinned for the freeze.
- [ ] P20M-3: implement the thin runner
  `formal_ir/nbpolar/raw_prior_val_1p5m.py` importing accepted `l1_order_1p5m`
  read-only with ONLY the §2 delta list d1–d7: hardcoded three arms
  (`G0_old_point_base` λ-prior/P16-order control at 319/6492 via the carried
  seams; `G1_raw_prior_session_budget` corrected-prior + derived (K1,K2) +
  derived worst-first orders; `G2_true_l1_diagnostic` oracle at candidate K2,
  oracle-isolated, deployable=false); the §3 frozen artifact loaded read-only
  behind the `corrected_prior_identity` gate; session-derived point frozen
  from the same-run session H (K_total via the literal f=1.3 recomputation
  displayed — S2-i; (K1,K2) via `select_empirical_split` semantics on 16
  synthetic TRAIN blocks model-sampled from the corrected prior under the
  frozen derivation seeds, never a real frame, never DEV; worst-first L1+L2
  orders into the frozen `raw_prior_orders_1p5m.json` with Stage-B read-only
  `--order-file` + `--order-digest` gated use and zero sampling); new P20M tag
  domains (master 2026092280, seed prefix
  `nbpolar-p20m-raw-prior-val-1p5m-seed`); FIRST-384-VAL-frame 1.5M formation
  (1660..2043 → blocks 1660..1787 / 1788..1915 / 1916..2043, remainder
  2044..2212 never used, counted but never decoded) under the §4 gate family
  (a)→(g) (cross-file source-tag+digest first, then intra-file
  VAL-containment + VAL-exterior/HOLD with VAL first, then consumed-TRAIN +
  remainder exclusions incl. the DEV∩build-frames disjointness declaration
  with frame sets — S2-ii, then corrected-prior-identity + order-freeze +
  budget-literal); five files with per-(arm, block) checkpointing; per-record
  floor-hit fields (S2); P20A resource passthrough and endpoint separation.
- [ ] P20M-4: freeze the corrected-prior artifact (digest + H literals + `p_b`
  cross-check + floor-hit rate), the session-derived point (K_total literal
  recomputation display + (K1,K2) integers + worst-first orders + order-file
  digest), the P16 construction migration (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), the
  population (DEV 1660..2043, remainder 2044..2212), the preregistered per-arm
  caps from the derived integers (G0 34119 + 327743 public; G1/G2 via the 5K+64
  rule; ratios-vs-raw shown), the derivation seeds
  (2026092291..2026092294), the exact Stage-B command (new P20M tag master,
  `--prior` frozen-artifact path, `--source 1p5M` vocabulary, `--k1/--k2` +
  `--order-file` + `--order-digest` frozen pins, `--dev-frames 1660 2043`,
  `--remainder-frames 2044 2212`, 15-SC / 9-tag pure-DEV budget, 600-s / 2-GiB
  / single-thread envelope), and the SC/tag/genie/wall/RSS budgets in
  `P20M_FREEZE.md`.
- [ ] P20M-5: focused `tests/test_nbpolar_raw_prior_val_1p5m.py`
  (synthetic counts/priors + scripted seams and tiny-n real SC; fresh
  test-local seeds 2026092281..2026092287; temporary roots; `pytest -p
  no:cacheprovider`) asserting the raw-rule derivation against an independent
  literal (no-lambda pin, floor/renorm/`p_b` cross-check), the zero-protected-
  open audit, the budget-literal recomputation (S2-i), the split/order freeze
  (derivation-seed pins, zero Stage-B sampling), the operating-point
  differential (G0 control pins vs G1 candidate pins), accounting, endpoint
  separation, the §4 gate family (source-first, VAL-before-HOLD,
  consumed-TRAIN exclusions, prior/order/budget pins last, with 2M
  zero-contact), the DEV∩build-frames declaration (S2-ii), the floor-hit
  reporting (S2), the declared-remainder measurement, the resource path and
  the no-production-invocation rule; plus the packet-scoped predecessor
  suites green with the zero-protected-open audit.
- [ ] P20M-6: `P20M_FREEZE.md` + `P20M_IMPLEMENTATION_NOTES.md` in the packet
  queue directory and this P20M spec/tasks delta; this doc authorizes nothing
  (no Stage-B execution, no self-acceptance).
- [ ] P20M-7: independent Pre-EXECUTE review of the frozen command,
  population, caps, corrected-prior derivation (§3), budget literal (§5),
  gate family (§4) and runner-delta design (§2), budgets, tag/domain
  separation, truth/accounting gates, tests and target absence (main thread +
  reviewer; separate gate, not this task).
- [ ] P20M-8: exactly one authorized nine-record three-arm attempt with the
  frozen command; the single DEV attempt is consumed at the first DEV content
  open with no rerun/reopen/seed/parameter/arm change (separate Stage-B
  authorization required; not authorized here).
- [ ] P20M-9: independent Pre-RESULT review recomputing the identities,
  population, 9 records, per-arm outcomes, G1-vs-G0 comparison,
  NLL/disclosure/floor-hit accounting, oracle isolation, gates, input stats,
  resources and the five-file inventory from the artifacts (separate gate,
  not this task).
- [ ] P20M-10: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive raw-prior +
  session-budget diagnostic on the first genuinely out-of-sample 1.5M segment,
  not real-frame FER, efficiency, key-rate, scaling, qualification or promotion
  evidence either way, and the oracle G2 arm is never an operational or
  deployable result. It does not establish NB-Polar real-block recovery in
  general and does not close the 1M-HOLD thread. The G1-restoration
  (maintain-confirmation) / G1-zero-restoration (next upstream single factor) /
  L2-implication (P20D) / maintain-only branch decision belongs to later
  planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `raw_prior_1p5m.npz`,
`raw_prior_orders_1p5m.json`, `P20M_FREEZE.md`,
`P20M_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

Gate evidence (no box checked): `P20M_FREEZE.md`, `P20M_IMPLEMENTATION_NOTES.md`,
`PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS),
`OPERATOR_RETURN.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/`
(five files; counts 0/0 + DEV 1/1 + HOLD 0/1, attempt 1/1 consumed; G0 0/3 L1
first errors + G1 0/3 with 2/3 hard-L1-exact + G2 oracle 0/3, undetected 0);
result label `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`,
main-thread acceptance recorded in `MAIN_THREAD_ACCEPTANCE.md` (both §16
L2-implication triggers fired: oracle non-exact + bottleneck-layer move).

## P20N alt-L2-construction tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/`
(`TASK_PACKET.md`, frozen; Tier-Y decision-gate packet).
Predecessor: P20M
`TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
(Stage-B single attempt SPENT 1/1; counts-calibration opens 0/0; DEV open 1/1
SPENT on 1.5M VAL 1660..2043; 9/9 records; 25/25 gates PASS; G0 0/3 L1 first
errors + G1 0/3 with L1 breakthrough (2/3 hard-L1-exact; L2/26, L1/848, L2/31)
+ G2 oracle 0/3 (L2/26, L2/3646, L2/31); undetected 0; SC 15/15; tags 9/9;
recount 0; 2M pristine by non-access) + X09/X09-R1 Tier-X probe
(`workspace/probes/nbpolar_x09_l2_attribution_r1/results.json`, reviewed PASS:
H1 NOT SUPPORTED with positive ideal-length margins on every L2-failing block;
H3 NOT SUPPORTED with failing-block floor hits 43/43/30/25/25 vs in-sample max
3,262; H2 NOT DECIDABLE with the two decode-time instrumentation requirements;
`first_error_coord` settled as a natural block symbol index) + P20A
`IMPLEMENTATION_ACCEPTED`. Historic P20D definition (P20C §16, P20L §16):
"fixed disclosure + ONE preregistered alternative L2 construction on
independent development data", "constrained tuning, not open-ended"; P20L's
oracle-exoneration objection is flipped by P20M's out-of-sample oracle failure.
Factor decision (frozen, not re-argued): ALT-L2-LAPLACE-α1 —
`f_alt[a,b] = (counts_ab[a,b]+1)/(n_b[b]+1024)` with the 1e-15 floor step
retained formally, `p2_alt = derive_p2(f_alt)`, L1 `p1` byte-identical, K1/K2
carried 331/6689 with zero disclosure delta, shared frozen P20M order prefixes
on all arms. User decision (2026-09-19): HOLD 2213..2766 first use (4 blocks +
42-frame remainder); VAL remainder 2044..2212 and 2M untouched. Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2. Stage A authorized
separately; it permits ZERO protected content opens (counts 0/0: §3 derivation
reads the digest-pinned P20M worktree npz only, never the V25 counts NPZ; no
1.5M HOLD/DEV/VAL-remainder content open or stat, HOLD 0/1, VAL-remainder 0)
and no 1M-pool or reserved-2M open/stat/listing/read in any form (2M pristine
by non-access), no lambda anywhere, no K other than the §5 literals (alt-H
descriptive only, never a budget input), no derivation on real frames, no
real-data decoder execution, no Stage-B output root, no second construction,
no construction sweep, no order re-derivation, no disclosure change, no
efficiency tuning, no SCL/new kernel/model/schema, no overwrite under
`results/` or `comparison_bench/outputs_comparison/`, and no commit/push.
Stage B needs an independent Pre-EXECUTE PASS (explicitly adjudicating the §3
derivation, the §5 K-literal, the §4 gate family, the §2 runner-delta design,
and the §7 instrumentation boundary) plus a separate pasted authorization.

- [ ] P20N-1: read-only callsite inventory of the packet-§12 predecessor
  helpers (`operational_f13.py`, `operational_f13_replication.py`,
  `holdout_microcheck.py`, `holdout_backoff_diagnostic.py`,
  `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`,
  `raw_prior_val_1p5m.py` (import target; gate/population/record-writer
  pattern references) plus the P13/P16 budget callsite
  (`target_n_scaling.budget_k_total` as carried-literal reference only) and
  the `construction.py` / `prior.py` / `sc.py` contracts as called, with the
  P20M `_selected_diagnostics` code point cited as the carried-over callsite
  pattern for the §7 recorder; change no shared logic.
- [ ] P20N-2: derive the §3 alt-L2 table (read `counts_ab` from the
  digest-reverified P20M worktree npz ONLY — worktree-file read, never a
  protected counts open; frozen α=1 rule with the 1e-15 floor step retained +
  column renormalize, `derive_p2` under A=32*U1+U2 FULL_BOB_ONLY,
  `p1`-equality within 1e-12 against the P20M artifact, descriptive alt-H via
  `entropy_bits` never a budget input; closed form with zero sampling, zero
  genie calls, zero derivation seeds) and write the frozen artifact
  `alt_l2_tables_1p5m.npz` (exact 9-key set with `alpha` 1.0) with its
  file-bytes sha256 digest + floor-hit count/rate + zero-column count +
  `f_alt` min/max + descriptive alt-H literals pinned for the freeze, plus the
  D1 feasibility literals (`ce_alt`/`ce_incumbent` TRAIN-only estimator,
  ceilings 33509/35164, `alt_ideal_length_bits`) with the D2
  `alt_construction_budget_feasibility` gate evaluated BEFORE any HOLD contact
  (INFEASIBLE → report the literals, HOLD untouched, no Stage-B request).
- [ ] P20N-3: implement the thin runner
  `formal_ir/nbpolar/l2_alt_hold_1p5m.py` importing accepted
  `raw_prior_val_1p5m` read-only with ONLY the §2 delta list d1–d7: hardcoded
  four arms (`A_incumbent_L2_operational` P20M-G1 construction at 331/6689 via
  the carried seams; `B_alt_L2_operational` incumbent-p1 + p2_alt at 331/6689
  with the SAME P20M order prefixes; `C_incumbent_L2_oracle` /
  `D_alt_L2_oracle` at K2 6689, oracle-isolated, deployable=false); the §3
  frozen artifact loaded read-only behind the `alt_l2_identity` gate with the
  carried K-literal gate (331/6689/7020 replayed, never recomputed); the shared
  frozen P20M order file via the reused `--order-file` + `--order-digest`
  gated use with zero sampling; the §7 mandatory instrumentation recorder
  `_l2_hazard_diagnostics` (eight exact scalar fields, post-decode
  recording-only, truth-isolation boundary pinned); new P20N tag domains
  (master 2026092300, seed prefix
  `nbpolar-p20n-l2-alt-hold-1p5m-seed`); FIRST-512-HOLD-frame 1.5M formation
  (2213..2724 → blocks 2213..2340 / 2341..2468 / 2469..2596 / 2597..2724,
  remainder 2725..2766 never used, counted but never decoded) under the §4
  gate family (a)→(g) (cross-file source-tag+digest first, then intra-file
  HOLD-containment, then consumed-TRAIN / consumed-VAL-DEV / VAL-remainder
  exclusions incl. the DEV∩build-frames disjointness declaration with frame
  sets — S2-ii, then alt-identity + order-freeze + K-literal); five files with
  per-(arm, block) checkpointing; per-record floor-hit fields (S2); P20A
  resource passthrough and endpoint separation.
- [ ] P20N-4: freeze the alt-table artifact (file-bytes digest + alpha/floor/
  key-set + `p1`-equality max-abs-diff + floor-hit rate + zero-columns +
  `f_alt` range + descriptive alt-H), the carried point (K1/K2/K_total
  literals + order-file digest + P16 construction digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), the
  population (HOLD DEV 2213..2724, remainder 2725..2766), the preregistered
  per-arm caps from the carried integers (A/B 35164 with Δ exactly 0; C/D
  33509 with Δ exactly 0; 327743 public; totals 549384 + 5243888), the exact
  Stage-A derive command (frozen `--alpha 1` vocabulary, zero sampling / zero
  genie calls) and Stage-B command (new P20N tag master, `--alt-digest` pin,
  `--source 1p5M` vocabulary, `--dev-frames 2213 2724`,
  `--remainder-frames 2725 2766`, 24-SC / 16-tag pure-HOLD budget, 900-s /
  2-GiB / single-thread envelope), and the SC/tag/genie/wall/RSS budgets in
  `P20N_FREEZE.md`, plus the D1 literals and the D2 gate outcome (FEASIBLE
  required before any Pre-EXECUTE request).
- [ ] P20N-5: focused `tests/test_nbpolar_l2_alt_hold_1p5m.py`
  (synthetic counts/priors + scripted seams and tiny-n real SC; fresh
  test-local seeds 2026092301..2026092307; temporary roots; `pytest -p
  no:cacheprovider`) asserting the α=1 derivation against an independent
  literal (alpha/floor pin, `p1`-equality, key-set, zero-protected-open audit,
  zero-sampling/zero-genie pins), the K-literal replay (never recomputed from
  alt-H), the construction differential (A-vs-B / C-vs-D table pins with
  shared-prefix rule), accounting, endpoint separation, the §4 gate family
  (source-first, HOLD-containment, consumed-TRAIN / consumed-VAL-DEV /
  VAL-remainder exclusions, alt/order/K pins last, with 2M zero-contact), the
  DEV∩build-frames declaration (S2-ii), the floor-hit reporting (S2), the
  D1 estimator + D2 gate logic on synthetic counts (both branches), the
  eight §7 instrumentation scalars incl. nullability + the truth-isolation
  sentinel, the declared-remainder measurement, the resource path and the
  no-production-invocation rule; plus the packet-scoped predecessor suites
  green with the zero-protected-open audit.
- [ ] P20N-6: `P20N_FREEZE.md` + `P20N_IMPLEMENTATION_NOTES.md` in the packet
  queue directory and this P20N spec/tasks delta; this doc authorizes nothing
  (no Stage-B execution, no self-acceptance).
- [ ] P20N-7: independent Pre-EXECUTE review of the frozen command,
  population, caps, alt-L2 derivation (§3), D2 feasibility-gate outcome (§3),
  K-literal (§5), gate family (§4),
  runner-delta design (§2) and instrumentation boundary (§7), budgets,
  tag/domain separation, truth/accounting gates, tests and target absence
  (main thread + reviewer; separate gate, not this task).
- [ ] P20N-8: exactly one authorized sixteen-record four-arm attempt with the
  frozen command (only if the D2 gate outcome is FEASIBLE; INFEASIBLE ends the
  packet at Stage A with HOLD untouched); the single HOLD attempt is consumed at the first HOLD
  content open with no rerun/reopen/seed/parameter/arm change (separate
  Stage-B authorization required; not authorized here).
- [ ] P20N-9: independent Pre-RESULT review recomputing the identities,
  population, 16 records, per-arm outcomes, B-vs-A / D-vs-C comparisons,
  NLL/disclosure/floor-hit/hazard accounting, oracle isolation, gates, input
  stats, resources and the five-file inventory from the artifacts (separate
  gate, not this task).
- [ ] P20N-10: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive fixed-disclosure
  alt-L2 diagnostic on the first HOLD-segment use, not real-frame FER,
  efficiency, key-rate, scaling, qualification or promotion evidence either
  way, and the oracle C/D arms are never operational or deployable results.
  It can restore L2 or falsify this construction; it licenses no
  reliability/recovery claim; 2M and VAL remainder remain untouched; the
  1M-HOLD thread stays open. The B-restoration (maintain-confirmation) /
  B-zero-restoration (next upstream single factor) / maintain-only branch
  decision belongs to later planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `alt_l2_tables_1p5m.npz`,
`P20N_FREEZE.md`, `P20N_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

Gate evidence (no box checked): `P20N_FREEZE.md`, `P20N_IMPLEMENTATION_NOTES.md`,
`PRE_EXECUTE_REVIEW.md` (PASS), `PRE_RESULT_REVIEW.md` (PASS),
`OPERATOR_RETURN.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/`
(five files; counts 0/0 + HOLD 1/1 + VAL-remainder 0 + 2M pristine, attempt 1/1
consumed; A 0/4 / B 1/4 (b3 2597..2724 exact) / C 0/4 / D 1/4, b_restored 1,
d_restored 1, all 14 failures L2-layer, undetected 0); result label
`TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`,
main-thread acceptance recorded in `MAIN_THREAD_ACCEPTANCE.md` (the deferred
`b_restoration_branch_maintain_confirmation_round` is the live next branch; no
reliability claim).

## P20O maintain-confirmation tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/`
(`TASK_PACKET.md`, frozen; Tier-Y decision-gate packet).
Predecessor: P20N
`TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE_ACCEPTED_DESCRIPTIVE`
(Stage-B single attempt SPENT 1/1; counts 0/0 + HOLD 1/1 SPENT on 1.5M HOLD
2213..2724; 16/16 records; A 0/4 / B 1/4 (b3 exact) / C 0/4 / D 1/4; b_restored 1,
d_restored 1; all 14 failures L2-layer; undetected 0; SC 24/24; tags 16/16; recount 0;
2M pristine by non-access) + P20M operating-point precedent (raw prior + session budget
on VAL 1660..2043) + X09/X09-R1 attribution (eight scalars; `l2_fail_in_prefix`
domain artifact adjudicated; U-domain cross-check as the successor item) + P20A
`IMPLEMENTATION_ACCEPTED`. Factor decision (frozen, not re-argued):
maintain-confirmation of ALT-L2-LAPLACE-α1 at fixed per-session disclosure on the
independent 2M session — the alt RULE is the confirmed single factor (α=1 frozen); the
raw prior + budget + split + orders are ALL 2M-TRAIN-derived under S2-i (never carried
across sessions). User decision (2026-09-19): reserved 2M session
`type2_2M_20260121_183657` first use (VAL DEV 2187..2826, 5 blocks + 89-frame
remainder); 1.5M HOLD consumed; 1.5M VAL remainder 2044..2212 and all 1M data untouched;
2M never opened/statted/listed by the planner. Strategy parent:
`docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2. Stage A authorized
separately; it permits EXACTLY ONE protected counts open (the 2M `--source 2M` TRAIN
array, counts 0/1→1/1; every other array 0; zero DEV contact, VAL-DEV 0/1) and no
1M-pool or any-1.5M-split open/stat/listing/read in any form, no lambda anywhere, no K
carried as an absolute from 1.5M (S2-i; alt-H descriptive only), no derivation on real
frames, no real-data decoder execution, no Stage-B output root, no second construction,
no construction sweep, no order re-derivation, no disclosure change, no efficiency
tuning, no SCL/new kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and no commit/push. Stage B needs an independent
Pre-EXECUTE PASS (explicitly adjudicating the §3 prior/alt derivation, the D2 outcome,
the §5 budget/K-literal, the §4 gate family, the §2 runner-delta design, and the §7
instrumentation boundary incl. the U-domain scalar) plus a separate pasted authorization.

- [ ] P20O-1: read-only callsite inventory of the packet-§12 predecessor helpers
  (`operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py`, `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`,
  `raw_prior_val_1p5m.py` (import target; gate/population/record-writer pattern
  references), `l2_alt_hold_1p5m.py` (construction-swap + instrumentation pattern
  reference) plus the P13/P16 budget/split callsites
  (`target_n_scaling.budget_k_total` + `empirical_genie_scaling.select_empirical_split`
  as the derivation rules) and the `construction.py` / `prior.py` / `sc.py` contracts
  as called, with the P20M `_selected_diagnostics` code point cited as the carried-over
  callsite pattern for the §7 recorder; change no shared logic.
- [ ] P20O-2: perform the single authorized 2M counts open and derive the §3 2M raw
  prior (raw-count MLE + 1e-15 floor + column renormalize, no lambda anywhere,
  `derive_p1`/`derive_p2` under A=32*U1+U2 FULL_BOB_ONLY, `p_b` cross-check, canonical
  digest, session H via `entropy_bits`) writing `raw_prior_2m.npz` (exact 10-key set,
  `lambda_star` 0.0) with digest + H literals + floor-hit rate pinned; model-sample 16
  synthetic TRAIN blocks under frozen derivation seeds 2026092321..2026092324 → L1+L2
  genie risks (32 calls, Stage A only) → pooled means → `select_empirical_split` →
  freeze K_total via the literal f=1.3 recomputation (S2-i) + (K1,K2) + worst-first
  orders into `raw_prior_orders_2m.json` (file-bytes digest pinned); derive the §3 2M
  alt-L2 table from the SAME counts (frozen α=1 rule with the 1e-15 floor step retained
  + column renormalize, `derive_p2`, `p1`-equality within 1e-12, descriptive alt-H never
  a budget input) writing `alt_l2_tables_2m.npz` (exact 9-key set, `alpha` 1.0) with
  file-bytes digest + floor-rate + `p1`-equality + alt-H pinned, plus the D1 feasibility
  literals (`ce_alt`/`ce_incumbent` 2M-TRAIN-only estimator, L2 ceiling `5*K2+64`,
  `alt_ideal_length_bits`) with the D2 `alt_construction_budget_feasibility` gate
  evaluated BEFORE any VAL contact (INFEASIBLE → report the literals, VAL untouched,
  no Stage-B request).
- [ ] P20O-3: implement the thin runner
  `formal_ir/nbpolar/l2_alt_maintain_2m.py` importing accepted `raw_prior_val_1p5m`
  read-only with ONLY the §2 delta list d1–d8: hardcoded four arms
  (`A_incumbent_L2_operational` 2M-incumbent at session K via the carried seams;
  `B_alt_L2_operational` 2M-incumbent-p1 + p2_alt at session K with the SAME 2M order
  prefixes; `C_incumbent_L2_oracle` / `D_alt_L2_oracle` at session K2,
  oracle-isolated, deployable=false); the §3 frozen artifacts loaded read-only behind
  the `session_prior_identity` + `alt_l2_identity` gates with the session K-literal gate
  (replayed, never recarried); the 2M-derived order file via the reused `--order-file` +
  `--order-digest` gated use with zero sampling; the §7 mandatory instrumentation
  recorder `_l2_hazard_diagnostics` (eight exact scalar fields + the optional ninth
  U-domain scalar `l2_fail_in_prefix_u_domain` frozen present-or-absent before execution,
  post-decode recording-only, truth-isolation boundary pinned); new P20O tag domains
  (master 2026092310, seed prefix `nbpolar-p20o-maintain-2m-seed`); FIRST-640-VAL-frame
  2M formation (2187..2826 → blocks 2187..2314 / 2315..2442 / 2443..2570 / 2571..2698 /
  2699..2826, remainder 2827..2915 never used, counted but never decoded) under the §4
  gate family (a)→(g) (cross-file source-tag+digest first, then intra-file
  VAL-containment, then consumed-1M / consumed-1.5M exclusions incl. the DEV∩build-frames
  disjointness declaration with frame sets — S2-ii, then session-prior + alt-identity +
  order-freeze + K-literal + maintain-confirmation-identity); five files with
  per-(arm, block) checkpointing; per-record floor-hit fields (S2); P20A resource
  passthrough and endpoint separation.
- [ ] P20O-4: freeze the 2M raw-prior artifact (canonical digest + H literals + `p_b`
  cross-check + floor-hit rate), the session-derived point (K_total literal recomputation
  display + (K1,K2) integers + derivation seeds 2026092321..2026092324 + worst-first
  orders + order-file digest), the alt-table artifact (file-bytes digest + alpha/floor/
  key-set + `p1`-equality max-abs-diff + floor-hit rate + zero-columns + `f_alt` range +
  descriptive alt-H), the P16 construction migration (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), the population
  (VAL DEV 2187..2826, remainder 2827..2915), the preregistered per-arm caps from the
  derived integers (A/B `5*(K1+K2)+64` with Δ exactly 0; C/D `5*K2+64` with Δ exactly 0;
  327743 public; totals frozen at Stage A), the exact Stage-A derive command (frozen
  `--source 2M` + `--alpha 1` vocabularies, single counts open, 32 genie calls) and
  Stage-B command (new P20O tag master, `--prior-digest` / `--alt-digest` / `--k1/--k2`
  / `--order-digest` pins, `--dev-frames 2187 2826`, `--remainder-frames 2827 2915`,
  30-SC / 20-tag pure-VAL budget, 1200-s / 2-GiB / single-thread envelope), and the
  SC/tag/genie/wall/RSS budgets in `P20O_FREEZE.md`, plus the D1 literals and the D2 gate
  outcome (FEASIBLE required before any Pre-EXECUTE request).
- [ ] P20O-5: focused `tests/test_nbpolar_l2_alt_maintain_2m.py`
  (synthetic counts/priors + scripted seams and tiny-n real SC; fresh test-local seeds
  2026092311..2026092317; temporary roots; `pytest -p no:cacheprovider`) asserting the
  2M raw-rule derivation against an independent literal (no-lambda pin, floor/renorm/`p_b`
  cross-check, single-counts-open audit), the budget-literal recomputation (S2-i), the
  split/order freeze (derivation-seed pins, zero Stage-B sampling), the α=1 alt derivation
  (alpha/floor pin, `p1`-equality, key-set, zero-DEV-read audit), the K-literal replay
  (never recarried from 1.5M, alt-H never a budget input), the construction differential
  (A-vs-B / C-vs-D table pins with shared-prefix rule), accounting, endpoint separation,
  the §4 gate family (source-first, VAL-containment, consumed-1M / consumed-1.5M
  exclusions, session-prior/alt/order/K pins last, with 2M-HOLD zero-contact), the
  DEV∩build-frames declaration (S2-ii), the D1 estimator + D2 gate logic on synthetic
  counts (both branches), the eight §7 instrumentation scalars incl. nullability + the
  ninth U-domain scalar (present-or-absent per freeze) + the truth-isolation sentinel, the
  declared-remainder measurement, the resource path and the no-production-invocation rule;
  plus the packet-scoped predecessor suites green with the declared-open audit.
- [ ] P20O-6: `P20O_FREEZE.md` + `P20O_IMPLEMENTATION_NOTES.md` in the packet queue
  directory and this P20O spec/tasks delta; this doc authorizes nothing (no Stage-B
  execution, no self-acceptance).
- [ ] P20O-7: independent Pre-EXECUTE review of the frozen command, population, caps,
  2M prior/alt derivation (§3), D2 feasibility-gate outcome (§3), budget/K-literal (§5),
  gate family (§4), runner-delta design (§2) and instrumentation boundary (§7 incl. the
  U-domain scalar), budgets, tag/domain separation, truth/accounting gates, tests and
  target absence (main thread + reviewer; separate gate, not this task).
- [ ] P20O-8: exactly one authorized twenty-record four-arm attempt with the frozen
  command (only if the D2 gate outcome is FEASIBLE; INFEASIBLE ends the packet at Stage A
  with VAL untouched); the single VAL attempt is consumed at the first VAL content open
  with no rerun/reopen/seed/parameter/arm change (separate Stage-B authorization required;
  not authorized here).
- [ ] P20O-9: independent Pre-RESULT review recomputing the identities, population, 20
  records, per-arm outcomes, B-vs-A maintain/restore table + D-vs-C diagnostic,
  NLL/disclosure/floor-hit/hazard accounting, oracle isolation, gates, input stats,
  resources and the five-file inventory from the artifacts (separate gate, not this task).
- [ ] P20O-10: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive fixed-per-session-disclosure
  maintain-confirmation diagnostic on the first 2M-segment use, not real-frame FER,
  efficiency, key-rate, scaling, qualification or promotion evidence either way, and the
  oracle C/D arms are never operational or deployable results. It can maintain/restore or
  falsify this construction on the independent session; it licenses no reliability claim;
  1.5M VAL remainder stays untouched; the 1M-HOLD thread stays open. The B-maintained /
  B-zero-maintain branch decision belongs to later planning, never to this packet's label.

Evidence (Stage A only; Stage B not run): `raw_prior_2m.npz`,
`raw_prior_orders_2m.json`, `alt_l2_tables_2m.npz`, `P20O_FREEZE.md`,
`P20O_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.

## P20Q instrumented HOLD confirmation tasks (Stage A implementation only)

Frozen packet:
`.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/`
(`TASK_PACKET.md`, frozen; Tier-Y decision-gate packet).
Predecessor: P20O
`TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE_ACCEPTED_DESCRIPTIVE`
(Stage-B single attempt SPENT 1/1; counts 1/1 for the 2M array ONLY; VAL-DEV open 1/1
SPENT on 2M VAL 2187..2826; 20/20 records; A 0/5 / B 2/5 (b1, b2 exact) / C 0/5 / D 3/5;
b_restored 2, d_restored 3; 11 L2-fail records all natural-in-prefix but U-domain-out;
undetected 0; SC 30/30; tags 20/20; recount 0; key 692580 / public 6554860) + X10 Tier-X
probe (`workspace/probes/nbpolar_x10_h2_scalar_adjudication/results.json`, reviewed PASS:
H2a REFUTED; H2b fail-position hazard elevated median ratio 2.246 n=25; H2c X-prefix
concentration with P20O 11/11 out-of-U; H2d floor flat; H2e static geometry NOT-DECIDABLE →
IR-1..IR-5 mandatory) + P20A `IMPLEMENTATION_ACCEPTED`. Factor decision (frozen, not
re-argued): instrumented α1 confirmation on the third 2M segment (HOLD) — same
construction/prior/orders/K and same arms A/B/C/D as P20O; ALL P20O frozen artifacts reused
read-only (no new derivation, NO new counts read); IR-1..IR-5 mandatory with IR-5 PRESENT
capped. User decision (2026-09-19): next packet is `NBPOLAR-PHASE4-P20Q-...` on 2M HOLD
(HOLD base 2916 by TRAIN 2187 + VAL 729 manifest-count arithmetic; DEV FIRST 640 HOLD
frames 2916..3555, remainder 3556..3644); 1.5M VAL remainder stays untouched. Strategy
parent: `docs/nbpolar/REAL_DATA_FEASIBILITY_STRATEGY.md` stage 2. Stage A authorized
separately; it permits ZERO protected opens (counts 0/0 at every stage — the V25 counts NPZ
never opened/statted/listed; HOLD-DEV 0/1; VAL-DEV 0; VAL-remainder 0) and no 1M-pool or
any-1.5M-split or any-2M-VAL open/stat/listing/read in any form, zero sampling/genie calls
at every stage, no lambda anywhere, no K carried as an absolute from 1.5M or recomputed
from alt-H (S2-i; replay only), no derivation or sampling on real frames, no real-data
decoder execution, no Stage-B output root, no second construction, no construction sweep, no
order re-derivation, no disclosure change, no H2 verdict, no efficiency tuning, no SCL/new
kernel/model/schema, no overwrite under `results/` or
`comparison_bench/outputs_comparison/`, and no commit/push. Stage B needs an independent
Pre-EXECUTE PASS (explicitly adjudicating the §3 reuse/alt replay, the D2 replay outcome,
the §5 budget/K-literal replay, the §4 gate family, the §2 runner-delta design, and the §7
nine-scalar + IR-1..IR-5 boundary incl. IR-3 thresholds and IR-5 cap) plus a separate pasted
authorization.

- [ ] P20Q-1: read-only callsite inventory of the packet-§12 predecessor helpers
  (`operational_f13.py`, `operational_f13_replication.py`, `holdout_microcheck.py`,
  `holdout_backoff_diagnostic.py`, `l2_disclosure_backoff.py`, `plus1024_confirmation.py`,
  `plus1024_extension.py`, `plus1024_independent_session.py`,
  `per_session_calibration.py` (digest recipe pin only),
  `plus1024_per_session_confirmation.py`, `l1_disclosure_1p5m.py`,
  `l1_dose_escalation_1p5m.py`, `l1_dose_512_1p5m.py`, `l1_order_1p5m.py`,
  `raw_prior_val_1p5m.py` (gate/population/record-writer pattern references),
  `l2_alt_hold_1p5m.py` (construction-swap + instrumentation pattern reference),
  `l2_alt_maintain_2m.py` (import target; gate/population/record-writer/nine-scalar
  pattern references) plus the P13/P16 budget/split callsites
  (`target_n_scaling.budget_k_total` as carried-literal reference only) and the
  `construction.py` / `prior.py` / `sc.py` contracts as called, with the P20O
  `_l2_hazard_diagnostics` code point cited as the carried-over callsite pattern for the
  §7 IR recorder extension; change no shared logic.
- [ ] P20Q-2: verify the §3 P20O reuse pins by worktree-file digest recomputation ONLY
  (zero protected opens at every stage): prior canonical digest
  `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587` + H literals
  `0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477` within 1e-12 + `p_b`
  cross-check + floor pins; orders file-bytes digest
  `b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906`; alt file-bytes
  digest `98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5` +
  alpha-1.0/floor pins + exact key sets + `p1`-equality within 1e-12 + descriptive alt-H
  replay; K literals `(7080,334,6746)` replayed never recomputed with the S2-i
  budget-literal replay display; D1 literals replayed (`ce_alt` 0.8850983725781965,
  `ce_incumbent` 0.8069006731253678, ceilings 33794/35464, `alt_ideal_length_bits`
  29002.90347264234) with the D2 `alt_construction_budget_feasibility_replayed` gate
  evaluated BEFORE any HOLD contact (MISMATCH → HOLD untouched, no Stage-B request).
- [ ] P20Q-3: implement the thin runner
  `formal_ir/nbpolar/l2_alt_hold_ir_2m.py` importing accepted `l2_alt_maintain_2m`
  read-only with ONLY the §2 delta list d1–d8: hardcoded four arms
  (`A_incumbent_L2_operational` 2M-incumbent at carried K via the carried seams;
  `B_alt_L2_operational` 2M-incumbent-p1 + p2_alt at carried K with the SAME 2M order
  prefixes; `C_incumbent_L2_oracle` / `D_alt_L2_oracle` at carried K2, oracle-isolated,
  deployable=false); the §3 reuse artifacts loaded read-only behind the
  `reuse_prior_identity` + `reuse_alt_identity` + `reuse_order_freeze` gates with the
  K-literal replay gate (never recomputed); the P20O order file via the reused
  `--order-file` + `--order-digest` gated use with zero sampling; the §7 carried nine
  scalars PLUS the mandatory IR-1..IR-5 recorder `_ir_hazard_diagnostics` (IR-1 64-bin
  histograms {prefix, outside} + IR-2 first-error hazard-rank percentile + IR-3
  above-threshold prefix counts at EXACTLY two frozen thresholds 1.0×/2.0× record
  prefix-mean hazard + IR-4 top-16 hazardous positions with ranks + IR-5 capped 4096×2
  float32 series with truncation flag, all PRESENT bounded recording-only post-decode with
  the truth-isolation boundary pinned); new P20Q tag domains (master 2026092330, seed
  prefix `nbpolar-p20q-hold-ir-2m-seed`); FIRST-640-HOLD-frame 2M formation (2916..3555 →
  blocks 2916..3043 / 3044..3171 / 3172..3299 / 3300..3427 / 3428..3555, remainder
  3556..3644 never used, counted but never decoded) under the §4 gate family (a)→(g)
  (cross-file source-tag+digest first, then intra-file HOLD-containment, then consumed-1M
  / consumed-1.5M / consumed-2M (TRAIN-as-DEV + VAL DEV + VAL remainder) exclusions incl.
  the DEV∩build-frames disjointness declaration with frame sets — S2-ii, then reuse-prior
  + reuse-alt + order-freeze + K-literal + hold-confirmation-identity); five files with
  per-(arm, block) checkpointing; per-record floor-hit fields (S2); P20A resource
  passthrough and endpoint separation.
- [ ] P20Q-4: freeze the §3 reuse pins (all three digest replays + H literals + `p_b` +
  `p1`-equality + floor/alpha pins), the replayed point (K_total literal replay display +
  (K1,K2) integers + order-file digest replay; NO derivation seeds — reuse needs zero
  sampling), the P16 construction migration (digest
  `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b`), the population
  (HOLD DEV 2916..3555, remainder 3556..3644), the replayed per-arm caps from the carried
  integers (A/B `5*(K1+K2)+64 = 35464` with Δ exactly 0; C/D `5*K2+64 = 33794` with Δ
  exactly 0; 327743 public; totals 692580/6554860), the IR-3 multipliers (1.0×/2.0× with
  the X10 median-2.246 justification) + IR caps (64-bin / 1-float / 2-threshold / top-16 /
  4096×2+flag), the exact Stage-A verify command (zero-open reuse check, `--source 2M`
  vocabulary) and Stage-B command (new P20Q tag master, `--prior-digest` / `--alt-digest`
  / `--k1/--k2` / `--order-digest` replay pins, `--dev-frames 2916 3555`,
  `--remainder-frames 3556 3644`, 30-SC / 20-tag pure-HOLD budget, 1200-s / 2-GiB /
  single-thread envelope), and the SC/tag/genie (0+0)/wall/RSS budgets in `P20Q_FREEZE.md`,
  plus the D1/D2 replay literals and outcome (FEASIBLE-replay required before any
  Pre-EXECUTE request).
- [ ] P20Q-5: focused `tests/test_nbpolar_l2_alt_hold_ir_2m.py`
  (synthetic counts/priors + scripted seams and tiny-n real SC; fresh test-local seeds
  2026092331..2026092337; temporary roots; `pytest -p no:cacheprovider`) asserting the
  zero-protected-open audit, the reuse-identity replay (digests/H/`p_b`/`p1`-equality/
  key-set pins), the budget/K-literal replay (S2-i; alt-H never a budget input; zero
  sampling/genie pins), the construction differential (A-vs-B / C-vs-D table pins with
  shared-prefix rule), accounting, endpoint separation, the §4 gate family (source-first,
  HOLD-containment, consumed-1M / consumed-1.5M / consumed-2M exclusions, reuse/order/K
  pins last, with VAL zero-contact), the DEV∩build-frames declaration (S2-ii), the D1
  estimator + D2 replay-gate logic on synthetic counts (both branches), the nine carried
  scalars incl. nullability + IR-1..IR-5 (all PRESENT: 64-bin histogram shapes/caps,
  rank-percentile formula + nullability, IR-3 two-threshold 1.0×/2.0× counts on synthetic
  hazards, top-16 shapes/ranks, capped-series truncation flag) + the truth-isolation
  sentinel, the declared-remainder measurement, the resource path and the
  no-production-invocation rule; plus the packet-scoped predecessor suites green with the
  zero-protected-open audit.
- [ ] P20Q-6: `P20Q_FREEZE.md` + `P20Q_IMPLEMENTATION_NOTES.md` in the packet queue
  directory and this P20Q spec/tasks delta; this doc authorizes nothing (no Stage-B
  execution, no self-acceptance).
- [ ] P20Q-7: independent Pre-EXECUTE review of the frozen command, population, caps,
  reuse derivation (§3), D2 replay-gate outcome (§3), budget/K-literal replay (§5), gate
  family (§4), runner-delta design (§2) and nine-scalar + IR-1..IR-5 boundary (§7 incl.
  IR-3 thresholds and IR-5 cap), budgets, tag/domain separation, truth/accounting gates,
  tests and target absence (main thread + reviewer; separate gate, not this task).
- [ ] P20Q-8: exactly one authorized twenty-record four-arm attempt with the frozen
  command (only if the D2 replay outcome is FEASIBLE; MISMATCH ends the packet at Stage A
  with HOLD untouched); the single HOLD attempt is consumed at the first HOLD content open
  with no rerun/reopen/seed/parameter/arm change (separate Stage-B authorization required;
  not authorized here).
- [ ] P20Q-9: independent Pre-RESULT review recomputing the identities, population, 20
  records, per-arm outcomes, B-vs-A maintain/restore table + D-vs-C diagnostic,
  NLL/disclosure/floor-hit/hazard/IR accounting (rank-percentile distribution + histogram
  summaries + above-threshold mass + top-k concentration + truncation flags), oracle
  isolation, gates, input stats, resources and the five-file inventory from the artifacts
  (separate gate, not this task; H2 quantities checked present, never decided).
- [ ] P20Q-10: main-thread adjudication to
  `TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE` or
  `BLOCKED(<earliest gate>)`; this is a descriptive frozen-disclosure instrumented
  confirmation on the third 2M segment, not real-frame FER, efficiency, key-rate, scaling,
  qualification or promotion evidence either way, and the oracle C/D arms are never
  operational or deployable results. It can maintain/restore or falsify this construction
  on HOLD with the H2 quantities recorded; it licenses no reliability claim and no H2
  verdict; 1.5M VAL remainder stays untouched; the 1M-HOLD thread stays open. The
  B-maintained / B-zero-maintain branch decision and the H2a–H2e decision belong to later
  main-thread analysis, never to this packet's label.

Evidence (Stage A only; Stage B not run): NO new artifacts (reuse paths point at the P20O
queue dir); `P20Q_FREEZE.md`, `P20Q_IMPLEMENTATION_NOTES.md`; output root
`.workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m/`
is absent and must remain absent until an authorized Stage-B execution. No
box above is checked by the implementing session.
