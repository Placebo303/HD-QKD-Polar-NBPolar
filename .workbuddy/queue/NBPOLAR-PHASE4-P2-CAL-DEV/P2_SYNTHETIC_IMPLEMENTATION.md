# P2 synthetic-phase return — PRIOR-ARTIFACT ADAPTER (operator evidence, NOT acceptance)

State: synthetic implementation COMPLETE; no artifact content read
(`artifact_content_attempts: 0`). No self-acceptance; independent
Pre-EXECUTE (P2-G0) PASS is still required before the single authorized
read, then an independent Pre-RESULT review before any candidate return.
Next gate per STATUS: `P2_IMPLEMENT_SYNTHETIC_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW`.

## 1. Pre-EXECUTE self-check (synthetic scope, all PASS)

- Branch `codex/nbpolar-phase0`; unrelated dirty files preserved, no tracked file touched.
- Allow-list: `prior_artifact.py` imports NumPy + stdlib (`json`,
  `dataclasses`, `pathlib`) + local P1 enums (`Conditioning`,
  `Provenance` from `.prior`, itself NumPy+stdlib only). No sibling
  import, no pandas/parquet/decoder/benchmark, no default production path.
- Frozen contract read: `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`
  (FREEZE_ACCEPT) + P2 `TASK_PACKET.md`; summary schema pinned from the
  locally documented producer contract (`test_v72p2d5_model_f_input.py`
  M11: schema/cycle/session/source/CAL702..1725/1024x256/axis/dims/
  mapping/field{q32,poly37}/lambda_star/selection/flags/counters/formal/
  status/artifact_files). `status` frozen as `MODEL_F_INPUT_CANDIDATE`:
  acceptance was recorded at cycle level, the protected root was never
  rewritten (decision-log + AGENT_PROJECT_MEMORY 2026-09-07).
- Authorization: STATUS `AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P2_CAL_PRIOR_VALIDATION`.
- Target absence: `.workbuddy/queue/NBPOLAR-PHASE4-P2-CAL-DEV/cal_prior_validation/` absent.
- Sibling untouched: only its `.venv/bin/python` used as a runtime binary
  (P1 precedent); no read/stat of `workspace/v72p2d5_model_f_input/20260907_r1/`.

## 2. Files (additive only)

- `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior_artifact.py`
  (new, ~230 lines): `PriorArtifact` frozen record (`counts_ab` int64
  read-only, `p_b` float64 read-only, summary copy, `FULL_BOB_ONLY` /
  `PRIOR_ONLY`) + `load_prior_artifact(npz_path, summary_path)` — explicit
  paths, exact basenames, `np.load(allow_pickle=False)`, exact two keys,
  object/bool rejection, counts `(1024,1024)` int / non-negative / sum
  exactly 262144, `p_b` shape/finite/non-negative/sum-1 ≤1e-12/axis-0
  marginal ≤1e-12, full frozen summary identity + dims/sum cross-checks.
  Read-only (never writes); all failures `artifact contract:`-prefixed.
- `comparison_bench/tests/test_nbpolar_prior_artifact.py` (new, 13
  tests): synthetic temp fixtures + loop-based literal-formula oracle;
  covers P2-T0-01 + P2-T1-01--T1-12. P2-T0-02/P2-T2-02 stay closed
  (need entrypoint + sole authorized read after G0 PASS).
- No `__init__.py` edit (loader is not public API this phase); no
  diagnostic entrypoint yet (created only with the execution-phase packet
  after G0 PASS). No commit/push. P3 not opened.

## 3. Evidence

- New tests, plain python: **13/13 passed**.
- Full regression (pytest, same interpreter):
  transform+sc+construction+r1+prior (66, baseline green before change) +
  prior_artifact (13) → **79 passed, 0 failed**.
- Decisions needing no adjudication: strict integer-dtype counts (producer
  writes int64); exact `lambda_star ==` on JSON doubles (repr round-trip
  exact); status frozen `MODEL_F_INPUT_CANDIDATE` (multiply attested
  locally). Any real-artifact schema surprise stops safely with
  loader/schema attribution per packet (no rerun without new disposition).
