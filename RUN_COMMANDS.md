# RUN_COMMANDS.md

Curated commands for this repository. Prefer smoke commands first.

> Project venv required: `source .venv/bin/activate` or run via `.venv/bin/python -m ...`.
> Bare `python` / `python3` is disabled (system interpreter lacks `numpy`/`pytest`).
> Validate once: `.venv/bin/python -c "import numpy,pytest"`.
> Windows native (PowerShell/CMD) variant: `.venv\Scripts\python -m ...` (same args).

## Smoke

```bash
.venv/bin/python -m comparison_bench.src.comparison_bench.cli.smoke_test --config comparison_bench/configs/benchmark_synth.yaml
```

## Benchmark

```bash
.venv/bin/python -m comparison_bench.src.comparison_bench.cli.build_dataset
.venv/bin/python -m comparison_bench.src.comparison_bench.cli.run_benchmark --config comparison_bench/configs/benchmark_realdata.yaml
.venv/bin/python -m comparison_bench.src.comparison_bench.cli.compare_methods --input <input> --output <output>
```

## V3 sweeps

```bash
.venv/bin/python -m comparison_bench.src.comparison_bench.cli.run_cascade_param_sweep --config comparison_bench/configs/cascade_param_sweep.yaml
.venv/bin/python -m comparison_bench.src.comparison_bench.cli.run_layered_ldpc_param_sweep --config comparison_bench/configs/layered_ldpc_param_sweep.yaml
.venv/bin/python -m comparison_bench.src.comparison_bench.cli.run_qldpc_param_sweep --config comparison_bench/configs/qldpc_param_sweep.yaml
.venv/bin/python -m comparison_bench.src.comparison_bench.cli.run_ir_v3_master --config comparison_bench/configs/ir_methods_v3_master.yaml
```

## Do not run by default

- `experiments/run_e2e_pipeline.py` on raw data
- any `tools/longrun_*.py`
- any `tools/minrerun_*.py`
- any `tools/routeA_*.py`
