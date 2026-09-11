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
