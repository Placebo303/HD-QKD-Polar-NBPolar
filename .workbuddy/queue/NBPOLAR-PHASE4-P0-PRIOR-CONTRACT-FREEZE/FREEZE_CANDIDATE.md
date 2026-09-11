# Phase 4-P0 return — FREEZE_CANDIDATE (elements, NOT self-accepted)

- Disposition: `FREEZE_CANDIDATE` elements per
  `TASK_PACKET.md` return contract (§§180-188). Independent review
  (`INDEPENDENT_PHASE4_P0_FREEZE_REVIEW`) is the next gate and has NOT run;
  nothing here is accepted until that verdict.
- Authorization respected: `STATUS.yaml`
  (`AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P0_FREEZE`, documentation-only).
  No `.py` added/modified; no CAL/TTBin read; no Model-F/decoder/data/
  benchmark/EVAL run; no Phase 1–3 or frozen-artifact change; no P1 start;
  no commit/push.

## Changed-file list (this turn, docs only)

1. `openspec/changes/formal-ir-nbpolar-phase4-p0/proposal.md` (new)
2. `openspec/changes/formal-ir-nbpolar-phase4-p0/design.md` (new, §§1–7)
3. `openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md` (new)
4. `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p0/spec.md` (new)
5. `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md` (new, §§1–8 + V-P0-01–12)
6. `.workbuddy/queue/NBPOLAR-PHASE4-P0-PRIOR-CONTRACT-FREEZE/FREEZE_CANDIDATE.md` (this file)
7. `.workbuddy/queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/TASK_PACKET.md` (new, unauthorized)
8. `.workbuddy/queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/PROMPT.md` (new, unauthorized)
9. `.workbuddy/queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/STATUS.yaml` (new, all-false)

## Source citations (exact)

Accepted formula: `comparison_bench/src/comparison_bench/formal_ir/v72p2d4r2_cal_gf32_model_rate_audit.py`
`build_canonical_counts` :246-261, `symbols_to_layers` :236-243, `build_f` :329-375,
`FLOOR/NORM_TOL/CHAIN_TOL` :43-45, CAL consts :21-28.
D5 twins: `.../v72p2d5_gf32_rate_mother.py` `build_f_model` :246-271 (BANNED),
`build_f_model_concentration` :274-305 (ACCEPTED), `marginalize/conditionalize`
:308-342, `app_fed_l2_prior` :353-375 (EXCLUDED), `oracle_l2_prior` :378-397
(pattern), packing :400-416, consts :39-51, `prepare_model_f_prior` :2330-2358
(BANNED) vs `_candidate` :2361-2388 (ACCEPTED).
Input: `.../v72p2d5_model_f_input.py` contract :1-15, consts :33-51,
`build_model_f_input` :78-125, marginal check :147-149, summary :164-167.
Scope rejects: `.../v72p2d3_gf32_contrast.py` header :1-10, canonical comment
:97-102, `_smooth_counts` :460-482, stage builders :485-550, packing :377-411.
Consumer: `formal_ir/nbpolar/sc.py` contract :1-32, normalize/validate :88-121,
`sc_decode` :188-257; `algebra.py:make_gf32` :40-42; `nonbinary_field.py`
`_POLYNOMIALS` :14-18, `get_field_spec` :38-52; `oracle.py` independence :1-15,
compare :116-150; `construction.py:failure_summary` :335-359;
`eval_r1.py` seeds :35-41. Provenance: `v35_algorithm_development.py`
`factorize_f03` :421-429, oracle posterior :432-447, tokens :523-551;
`v72p2d7_gf32_bidirectional_oracle.py` doc :1-22, consts :53-79, tokens
:119-121, estimator :158-159; `...schedule_discriminator.py` :114-116;
`v72p2d7_gf32_decoder_certification.py` :22-52. Decisions: `docs/decision-log.md`
:3506 (H03), :3512 (D7-C), :3528 (D7-D). Docs: `docs/nbpolar/ARCHITECTURE.md`
prior :99-124; `ROADMAP.md` Phase 4 :79-90; `VALIDATION_GATES.md` :3-36;
`ASSET_MAP.md` reuse :3-14, no-reuse :35-45; `README.md` :3-34, :61-71.
Packets: P0 `TASK_PACKET.md` formula :40-48, tensors :60-65, API :75-88,
lifecycle :92-106, matrix :110-129, handoff :134-146, alternatives :150-160,
allowed files :162-170, review :172-178; Phase 3-R1 `EVAL_FREEZE_R1.md`,
`MAIN_THREAD_ACCEPTANCE_R1.md` (299/300, block 219, seed 2026091213).

## API / alternatives / matrix

Selected API: `SymbolMetric` + six pure helpers + explicit floor helper
(`design.md` §§4,7). Alternative A (dense) SELECTED; B/C DEFERRED
(`design.md` §6). Matrix V-P0-01–12 (`PHASE4_P0_PRIOR_CONTRACT.md` §6).

## Independent review verdict

PENDING — next gate `INDEPENDENT_PHASE4_P0_FREEZE_REVIEW`. Required checks:
every cited callable/axis vs source; smoothing recalculation; truth trace;
CAL/DEV/EVAL isolation; P1 still unauthorized.

## Memory triage

PENDING — after independent review, file under `AGENT_PROJECT_MEMORY.md`
+ `docs/decision-log.md` (additive only).

## Risks

See contract doc §8. Earliest-known non-blocker: DEV/EVAL concrete IDs
deferred to P1 authorization by design (CAL read forbidden in P0).

## Inactive P1 packet

`.workbuddy/queue/NBPOLAR-PHASE4-P1-PRIOR-ADAPTER/` — `phase4_p1_authorized:
false`; execution/reads all false. Do not start.
