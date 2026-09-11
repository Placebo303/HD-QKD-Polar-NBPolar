# Current Mainline

## NB-Polar worktree boundary — 2026-09-11

This checkout is the independent NB-Polar track. Its canonical plan is
[docs/nbpolar/README.md](nbpolar/README.md) and its source-of-truth change is
`openspec/changes/formal-ir-nbpolar-mvp/`.

The selected MVP is native GF(32), polynomial 37, `alpha=2`, an explicitly
ordered 2x2 kernel, and a reference log-domain q-ary SC source decoder.
Phase 0 is `FREEZE_ACCEPT`. Phase 1 GF4/GF32 algebra, natural-order transform,
dense reference, and coordinate selection are `IMPLEMENTATION_ACCEPTED` after
an independent pytest 17/17 run. Phase 2 reference SC and its independent
enumeration oracle are `IMPLEMENTATION_ACCEPTED` on reviewer-go's 33/33 suite.
Phase 3 is `BLOCKED(PHASE3_GATE_INVALID)`: full-vector Spearman missed its
frozen gate, the required independent pre-EVAL review was unavailable, and the
procedure-invalid one-shot EVAL is retained only as a 299/300 diagnostic. The
Phase 3-R1 is accepted only as a fresh synthetic development diagnostic:
O3 analytic, epsilon=0.05, K=45, seed 2026091213, 299/300 exact with one
impossible failure at block 219 and zero other/NaN failures. Its seed and root
are frozen. Phase 4-P0 prior contract is `FREEZE_ACCEPT`; Phase 4-P1 pure
adapter/synthetic qualification is `IMPLEMENTATION_ACCEPTED_SYNTHETIC_ONLY`
after the P3-T1-09 sentinel-scope ruling, 66/66 focused regression, independent
11/11 decoder-free check and reviewer-go ACCEPT. Phase 4-P2-R1 CAL prior-table
validation is accepted after 88 tests, one artifact read and independent
Pre-RESULT review; its entropy values are CAL-resubstitution descriptions only.
P2 attempt 1 is retained as `BLOCKED(P2_DIAG_INDEX_ERROR)` after the accepted
artifact loader passed and a new entropy diagnostic mis-indexed `[U1,B,U2]`.
P2-R1's read is consumed. A heavy P3 empirical-prior SC interface packet is
prepared but remains all-false; no P3 action is authorized. Real-data execution,
benchmark/result roots, SCL and promotion remain false. The inherited D5-D7
ledger below is historical Comparison context and does not authorize a new
NB-Polar data run.

The Comparison checkout owns the NB-LDPC history and durable route log. The
Release checkout remains the frozen binary Polar mainline and is read-only for
this track.

## Inherited Comparison route ledger — historical context (through D7-D)

This document is **status, not authorization**. The active gate and accepted
cycle documents outrank aggregate checkbox counts; stale historical checkboxes
are bookkeeping, not execution authorization.

The strict first principle is high-performance error correction for actual
HD-QKD data. The frozen Polar line below is a comparison baseline; active
algorithm work lives under `comparison_bench/`, OpenSpec, and the NB-LDPC
research cycle documents.

Current route ledger (each item is a bounded conclusion already accepted in its
own cycle document; no new claim is added here):

1. **D5 — fixed rate-mother path stopped within tested scope.** The two-layer
   rate-mother BP path is accepted as stopped for the tested configuration.
2. **D6 — graph/mother successor structurally blocked.** The graph/mother A2
   path is structurally blocked; R1d Option C is frozen but optional/paused
   (`PAUSED_OPTIONAL_LOCAL_CONFIRMATION_NOT_MAINLINE_GATE`) and is not a
   mainline gate.
3. **D7-A — decoder certification PASS.**
4. **D7-B — hard-decision easy region observed**, with RSS/belief limitations
   recorded; no belief-calibration claim.
5. **D7-C — bounded bidirectional dependence accepted** as a diagnostic; it
   does not prove that alternating/joint BP can bootstrap.
6. **D7-D — schedule effect inconclusive** (`D7_D_SCHEDULE_EFFECT_INCONCLUSIVE`,
   accepted as `D7_D_RESULT_ACCEPTED_SCHEDULE_EFFECT_INCONCLUSIVE`); no
   schedule-superiority claim.
7. **Active gate — BP provenance implementation.** The next mainline action is
   Alternative A of the accepted layer-interface proposal: explicit belief
   provenance plus fail-closed cross-layer consumers.
8. **After BP**, freeze a provenance-safe cross-layer mechanism discriminator
   before any further cross-layer APP work.
9. **Only then** consider dimension/bandwidth expansion. For more than two
   layers, a separate mathematical/leakage contract is required.

Earlier bounded V-series states superseded by the ledger above: V34 matched
empirical-P fixed-packet bounded failure (ER1 accepted); V35R1 closed only the
tested hand-designed NB configuration
(`NO_NB_CANDIDATE_FOR_TESTED_HAND_DESIGNED_CONFIGURATION`,
`PROTOCOL_PARTIAL_A4_NOT_EXECUTED`); V36 showed a real exploratory residual
decrease with no exact recovery and no accepted finite-graph advance.

Use `docs/research-cycle-sop.md` for the next plan -> ChatGPT review -> OpenCode
implementation -> result-review loop. No successor or formal run is currently
authorized by this status document.

## Reporting Rule

The default reporting line is Route A actual-IR finite-key:

- `PIE_main`
- `SKR_main_bps`
- `main_result_source=actual_ir_finite_key`

`PIE_practical`, `SKR_measured_bps`, shadow-only outputs, and estimate-only outputs are diagnostics.

## Recommended Entrypoints

Front half:

```powershell
python experiments/run_e2e_pipeline.py --ttbin <head.ttbin> --skip-polar --force-align --out-root <e2e_out>
python experiments/run_real_polar_max_pie.py --grid-table <e2e_out>\_tmp_grid_table.csv --in-csv <e2e_out>\_tmp_src_table.csv --out-csv <polar_out>\polar_e2e_results.csv --prefer-sidecar-map-ser
```

ASENoise Type0:

```powershell
python tools/asenoise/run_asenoise_type0_corrected_subset.py --timestamp <stamp>
python tools/asenoise/run_asenoise_routeA_replay.py replay --mode full --timestamp <stamp>
python tools/asenoise/run_asenoise_routeA_replay.py finalize-main --input-csv <full_master.csv> --backup
```

Security reports / Route A:

```powershell
python tools/security_reports/round2_build_finite_key_audit_table.py --input-dirs <candidate_dir> <actual_ir_dir> --output-dir <stage2_security> --overwrite
python tools/security_reports/round2_build_actual_ir_finite_key_shadow.py --output-dir <stage2_security> --overwrite
python tools/security_reports/round2_build_security_round2_summary.py --actual-ir-dir <stage2_security> --beta-baseline-dir <stage2_security> --output-dir <stage2_security> --overwrite
```

Current pipelines live in `pipelines/current/`. Historical batch scripts live in `pipelines/archive/` and are not maintained as default commands.

## Archived Studies

Route B-lite is an archived side study. It tested whether richer binary channel / LLR modeling should enter the mainline. The result was mixed and locally useful but not stable enough to replace Route A or to pollute the mainline. Its value is as evidence for future Route C / q-ary Polar discussions.

## Old Entrypoints

Old root-level `tools/routeB_*`, root `tools/round2_*`, and root `tools/run_asenoise_*` paths are intentionally not preserved as wrappers. Use the paths above.
