# Phase 4-P1 task packet — PRIOR ADAPTER (PREPARED ONLY, NOT AUTHORIZED)

## State

`PLAN_READY_AWAITING_EXPLICIT_AUTHORIZATION`. This packet authorizes
NOTHING. Do not read CAL/private data, run Model-F/decoder/benchmark/EVAL,
modify Phase 1–3 code or frozen artifacts, or commit/push under this packet
until a verbatim user authorization flips `STATUS.yaml`.

Frozen contract: `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md` +
`openspec/changes/formal-ir-nbpolar-phase4-p0/` (proposal/design/tasks/
specs). P0 independent review must PASS before P1 authorization.

## Mission

Implement the pure prior adapter and its synthetic qualification. This slice
stops before CAL, Model-F, DEV/EVAL selection, or any decoder call:

1. `comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py`
   (new): `SymbolMetric`, `Conditioning`, `Provenance`, and pure helpers
   `smooth_joint_to_conditional`, `derive_p1`, `derive_p2`,
   `build_p1_metrics`, `gather_p2_metrics`, `probs_to_symbol_metric`,
   `apply_explicit_floor` — NumPy+stdlib only, error prefixes
   `axis/smoothing/metric/provenance/lifecycle contract:`.
2. `comparison_bench/tests/test_nbpolar_prior.py` (new): synthetic
   fixtures + independent literal-formula oracle (no shared helper);
   gates V-P0-01–07 green on synthetic data BEFORE any CAL artifact.
3. Produce a reviewed Phase 4-P2 CAL/DEV packet, still all-false and
   unauthorized. It will later freeze concrete data identities and any floor
   before a CAL artifact is read.

## Hard boundaries

- Allow-list imports for `prior.py`: `numpy`, stdlib, local range checks
  only. NEVER import: `v72p2d5_gf32_rate_mother.build_f_model` /
  `prepare_model_f_prior`, any `get_l1_app_prior_l2`, any decoder/BP
  belief, benchmark/protocol/result machinery, pandas/parquet (P1 tests
  are synthetic; CAL loading is a separately reviewed step).
- Oracle gather helper lives in the TEST FILE ONLY; never exported from
  `nbpolar/__init__.py`. Operational builders take no Alice input.
- `VAL1726-1729` and any held-out sample never enter construction,
  smoothing, floor, or thresholds. No `7.162347` reuse as NB-Polar input.
- Run V-P0-01–07 only. V-P0-08–12 remain closed for later packets. Add one
  decoder-free resource smoke for N=256 dense metric creation (≤60 s wall,
  <2 GiB RSS on ≤1024 synthetic frames) without treating it as V-P0-12.

## Return

After explicit authorization only: `P1_IMPLEMENTATION_CANDIDATE` (V-P0-01–07
green, independent formula comparison, inactive P2 packet) or `BLOCKED(<single earliest
gate>)` with raw evidence and one needed decision. No Phase 5/reconciliation
transition follows automatically.
