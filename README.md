# HD-QKD Polar Comparison — NB-Polar worktree

## Repository identity and sibling boundary

This checkout (`HD-QKD_Polar_Comparison-nbpolar`) is the independent
NB-Polar planning and future implementation worktree. It must not inherit
NB-LDPC graph, Cascade, or binary Polar baseline logic silently.

- Canonical plan: `docs/nbpolar/` and candidate change
  `openspec/changes/formal-ir-nbpolar-mvp/` (status `PLAN_CANDIDATE`;
  implementation and execution not authorized).
- Sibling `../HD-QKD_Polar_Comparison`: formal-IR / NB-LDPC history and
  decision owner (read-only reference, separate project).
- Sibling `../HD-QKD_Polar_Comparison-worktree-cascade-single`: isolated
  binary Cascade study (read-only reference).
- Sibling `../HD-QKD_Polar_Release`: frozen binary Polar baseline and
  protocol reference (read-only reference).

## NB-Polar worktree status (2026-09-11)

This checkout is now the independent NB-Polar planning and future
implementation worktree. The canonical documents are:

- [NB-Polar track](docs/nbpolar/README.md)
- [asset map](docs/nbpolar/ASSET_MAP.md)
- [architecture](docs/nbpolar/ARCHITECTURE.md)
- [implementation roadmap](docs/nbpolar/ROADMAP.md)
- [critical path](docs/nbpolar/CRITICAL_PATH.md)
- [validation gates](docs/nbpolar/VALIDATION_GATES.md)
- [NBPOLAR-PHASE0 review packet](docs/research_cycles/NBPOLAR-PHASE0/REVIEW_ENTRYPOINT.md)
- [NB-Polar MVP proposal](openspec/changes/formal-ir-nbpolar-mvp/proposal.md)
  ([design](openspec/changes/formal-ir-nbpolar-mvp/design.md),
  [tasks](openspec/changes/formal-ir-nbpolar-mvp/tasks.md))

The current lifecycle is `PLAN_CANDIDATE`: there is no NB-Polar production
decoder, Model-F run, real-data run, qualification, or promotion in this
checkout. The inherited Comparison documents below remain historical context;
the new track is owned by this worktree and must not modify the binary Polar
Release checkout.

## Project First Principle

This is a performance-first research-code repository. Its strict first
principle is to find, implement, and validate scientifically reasonable
high-performance information-reconciliation algorithms for the actual HD-QKD
data. Primary measures are correction success/FER, leakage efficiency,
throughput and resource cost, and accepted-frame net secret-key yield.

Benchmarking and reproducibility support algorithm discovery. Package maturity,
general frameworks, defensive hardening, exhaustive audit machinery, and
verifier sophistication are secondary and must not displace algorithm work
unless a concrete issue would make the scientific result wrong, irreproducible,
unauthorized, or destructive to existing data.

This repository contains the current HD-QKD Polar comparison workspace, including:
- the frozen Polar baseline (`src/`, `experiments/`, `tools/` — do not modify;
  `comparison_bench/` is an outer wrapper that only reads existing Polar
  outputs and adds separate comparison capabilities)
- the non-invasive `comparison_bench/` comparison layer (formal IR methods, CLIs, parameter sweeps, and tests)
- workflow and result documentation

## Output policy

- Do not overwrite anything under `results/` or
  `comparison_bench/outputs_comparison/` unless explicitly asked.
- New comparison outputs stay under `comparison_bench/outputs_comparison/`
  with additive naming.
- Test fixtures and temp pytest artifacts under
  `comparison_bench/outputs_comparison/` are not production outputs.

## Inherited Comparison context

As of 2026-08-24, the active research mainline is performance-first formal IR:

- V34 is closed as an ER1-accepted bounded failure for the tested matched
  empirical-P V31 QC packet/decoder (`0/60` exact, useful residual reduction).
- V35R1 is a bounded negative for one hand-designed mixed-degree NB-LDPC
  configuration; it does not close empirical-P irregular or MET designs.
- V36 produced an exploratory paired residual signal, but its DE selection and
  finite-graph structural gates do not satisfy the frozen OpenSpec. It is not
  an accepted candidate and remains `NO_FINITE_GRAPH_ADVANCE`.
- The next algorithm decision is a small corrected DE/finite-graph experiment,
  not automatic MET promotion or more verifier infrastructure.

The older Polar reporting line below remains frozen baseline context, not the
active algorithm-development objective.

As of 2026-03-27, the current reporting line is:
- `PRIMARY_REPORTING_MODE = actual_ir_finite_key`
- `BETA_BASELINE_ROLE = comparison_only`
- `NIU_2016_STATUS = not_supported_by_current_observables`

The authoritative latest results are **not** the older `_tmp_longrun_stage*` directories.
Use these instead:
- frozen baseline outputs: `results/`
- comparison outputs: `comparison_bench/outputs_comparison/`

Route A correctness-side verification is formalized with per-block universal hashing. This is not a strict Zhong 2015 or full Niu 2016 proof instantiation.

Route B-lite is a completed archived study. Its LLR-only gains were local and unstable, so it is not part of the mainline.

## Main Documents

- GitHub/ChatGPT/OpenCode research-cycle SOP:
  - [docs/research-cycle-sop.md](docs/research-cycle-sop.md)
  - [ChatGPT review prompt](docs/prompts/chatgpt-research-review.md)
  - [OpenCode execution prompt](docs/prompts/opencode-research-execution.md)
- active formal-IR state:
  - [AGENT_HANDOFF.md](AGENT_HANDOFF.md)
  - [docs/nbldpc-v36-empirical-graph-development.md](docs/nbldpc-v36-empirical-graph-development.md)

- latest workflow and run method:
  - [docs/POLAR_CODE_MAINFLOW_20260327.md](docs/POLAR_CODE_MAINFLOW_20260327.md)
- latest results and authoritative output paths:
  - [docs/LATEST_RESULTS_20260327.md](docs/LATEST_RESULTS_20260327.md)
- current mainline and maintained commands:
  - [docs/CURRENT_MAINLINE.md](docs/CURRENT_MAINLINE.md)
- Route A correctness formalization:
  - [docs/ROUTE_A_FORMAL_VERIFICATION_20260410.md](docs/ROUTE_A_FORMAL_VERIFICATION_20260410.md)
  - [docs/ROUTE_A_BIT_PLANE_INTERFACE_20260414.md](docs/ROUTE_A_BIT_PLANE_INTERFACE_20260414.md)

## Repository type and installation

This is a script repository, not an installable Python package. Run commands from the repository root. Prefer WSL/POSIX paths; legacy Windows paths (where referenced in history/docs) are provenance only. `wsl-env.sh` sets `PROJECT_DATA_ROOT`, `PROJECT_RESULTS_ROOT`, etc. for WSL environments.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r comparison_bench/requirements-comparison.txt  # optional: pyyaml, pyarrow, pytest
```

Core deps: `numpy`, `pandas`, `numba`, `tqdm`, `matplotlib` (`requirements.txt`).
Comparison deps: `pyyaml`, `pyarrow`, `pytest`
(`comparison_bench/requirements-comparison.txt`).

Windows (provenance) equivalent:

- `.ttbin` ingestion requires the Swabian Instruments Time Tagger software and its `TimeTagger` Python module.
- The CA-SCL decoder uses the included Windows DLL when compatible. If the platform-specific library is absent, the wrapper builds it from C++17 source and requires `g++`.
- `results/` and raw `.ttbin` data are not included in a fresh clone.

Verify the optional TimeTagger binding:

```bash
python -c "import TimeTagger; print('TimeTagger available')"
```

## Main Entry Points

Do not run by default (require explicit request/authorization):
`tools/longrun_*`, `tools/minrerun_*`, `tools/routeA_*`,
`experiments/run_e2e_pipeline.py` on raw data, full real-data benchmark or
v3 master sweep in a fresh environment. The same heavy-run restriction applies to
`pipelines/current/longrun_*`, `pipelines/current/routeA_*`, and `pipelines/archive/longrun_*` / `minrerun_*` reruns.

Front half (frozen baseline; heavy — do not run on raw data casually):
- [experiments/run_e2e_pipeline.py](experiments/run_e2e_pipeline.py)
- [experiments/run_real_polar_max_pie.py](experiments/run_real_polar_max_pie.py)

Replay / security (maintained, post-restructure):
- [pipelines/current/round1a_build_replay_index.py](pipelines/current/round1a_build_replay_index.py)
- [pipelines/current/round1b_run_actual_ir_replay.py](pipelines/current/round1b_run_actual_ir_replay.py)
- [tools/security_reports/round2_build_finite_key_audit_table.py](tools/security_reports/round2_build_finite_key_audit_table.py)
- [tools/security_reports/longrun_build_security_master_table.py](tools/security_reports/longrun_build_security_master_table.py)

Refined frame-accounting pass (archived):
- [pipelines/archive/minrerun_audit_frame_accounting_inputs.py](pipelines/archive/minrerun_audit_frame_accounting_inputs.py)
- [pipelines/archive/minrerun_run_frame_audit.py](pipelines/archive/minrerun_run_frame_audit.py)
- [pipelines/archive/minrerun_rebuild_security_master_20dB.py](pipelines/archive/minrerun_rebuild_security_master_20dB.py)
- [pipelines/archive/minrerun_build_cross_loss_refined_summary.py](pipelines/archive/minrerun_build_cross_loss_refined_summary.py)

Comparison benchmark entrypoints:

```bash
python -m comparison_bench.src.comparison_bench.cli.build_dataset
python -m comparison_bench.src.comparison_bench.cli.run_benchmark
python -m comparison_bench.src.comparison_bench.cli.compare_methods
```

V3 parameter sweeps (all under
`python -m comparison_bench.src.comparison_bench.cli.<entrypoint> --config <config>`):
`run_cascade_param_sweep.py`, `run_layered_ldpc_param_sweep.py`,
`run_qldpc_param_sweep.py`, `run_ir_v3_master.py`.

## Recommended Usage

For a new research cycle, begin with
[docs/research-cycle-sop.md](docs/research-cycle-sop.md). Freeze an OpenSpec
plan, push a Git candidate, obtain a copy-pasteable ChatGPT review, then give
OpenCode the accepted SHA and frozen execution packet. Commit compact result
data or the standard result summary before the next review.

If you only need the current best result package, read the existing outputs and do not rerun the physics front half.

If you need to reproduce the current workflow from raw data, use the split boundary flow described in [docs/POLAR_CODE_MAINFLOW_20260327.md](docs/POLAR_CODE_MAINFLOW_20260327.md):
1. extraction/materialization with `--skip-polar`
2. Polar evaluation from cached `_tmp_grid_table.csv` and `_tmp_src_table.csv`
3. actual-IR replay and security aggregation
4. refined frame-accounting rebuild

## Result packs and checksum verification

`results/` is local artifact storage (ignored by Git); authority is defined by [docs/RESULTS_MANIFEST_20260427.md](docs/RESULTS_MANIFEST_20260427.md). Validate a transferred set with `python tools/verify_authoritative_results.py --verify docs/AUTHORITATIVE_RESULTS_CHECKSUMS.json`.

## Layout (main directories)

- `experiments/`: E2E and Polar entrypoints
- `src/`: timing, mapping, decoder, and verification code
- `comparison_bench/`: non-invasive IR comparison layer (methods, formal IR implementations, CLIs, sweeps, tests, outputs)
- `openspec/`: OpenSpec change proposals, specs, and archives
- `pipelines/current/`: maintained replay pipelines
- `pipelines/archive/`: historical batch reruns
- `tools/security_reports/`: finite-key and reporting builders
- `tools/asenoise/`: ASENoise and cross-correlation tools
- `tools/diagnostics/`: non-authoritative diagnostics
- `tools/archive/routeB_lite/`: archived Route B-lite study
- `docs/`: result semantics, workflow, and scientific boundaries
- `tests/`: raw-data-free smoke tests
- Output/auxiliary directories (not entrypoints): `analysis/`, `workspace/`, `scripts/` (development/diagnostic scripts), `comparison_bench/outputs_comparison/`; `results/` is local artifact storage when present (absent in a fresh clone).

## Safe checks

Safe smoke (primary):

```bash
python -m comparison_bench.src.comparison_bench.cli.smoke_test --config comparison_bench/configs/benchmark_synth.yaml
```

Other safe checks:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src experiments pipelines tools analysis tests
```

These checks do not replace a raw-data E2E or full replay run.

## Key documents

- [Current mainline](docs/CURRENT_MAINLINE.md)
- [Project classification](docs/PROJECT_CLASSIFICATION_20260427.md)
- [Results manifest](docs/RESULTS_MANIFEST_20260427.md)
- [Results interpretation](docs/RESULTS_INTERPRETATION.md)
- [Security model](docs/SECURITY_MODEL.md)
- [Route A formal verification](docs/ROUTE_A_FORMAL_VERIFICATION_20260410.md)
- [Route A bit-plane interface](docs/ROUTE_A_BIT_PLANE_INTERFACE_20260414.md)
- [Archived Route B-lite summary](docs/archived_studies/routeB_lite/ROUTE_B_LITE_FINAL_SUMMARY_20260415.md)

## License

MIT
