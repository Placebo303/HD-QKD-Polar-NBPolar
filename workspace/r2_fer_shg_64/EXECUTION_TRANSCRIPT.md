# EXECUTION_TRANSCRIPT — r2-fer-shg-64

Operator run. Execution-only; no judgment rendered here (per AGENTS.md
§10.3 Pre-RESULT review requirement — adjudication is a separate,
not-yet-performed main-thread act).

## Command (verbatim, from prereg.md §C)

```
MSYS_NO_PATHCONV=1 wsl.exe -e bash -c "PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar /home/karel_303/.venvs/timetagger/bin/python /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2_fer_shg_64/run.py"
```

stdout -> `execution_stdout.log`, stderr -> `execution_stderr.log` (both
this directory). `EXIT_CODE=$?` appended to `execution_stdout.log` after
the process exited.

## Timing

- Started (UTC): 2026-09-28T12:14:26Z (recorded in STATUS.yaml
  `execution_started` before launch)
- Finished (UTC): 2026-09-28T13:29:48Z (results.json / execution_stdout.log
  mtime, host local 2026-09-28 21:29:48 +0800)
- External wall (launch to file-write): ~75m22s
- Script-internal `timing.wall_s_total` (results.json): 4493.36 s
  (= 74m53s), launch_start to aggregate-write, consistent with the
  external wall above
- Budget: per-block wall <=1200s, per-block RSS <=2GiB, total wall <=3h
  (10800s), 8-way parallel — well inside all three caps; no
  `resource_abort` of any kind occurred (0 blocks)

## Exit code

`EXIT_CODE=0`

## Per-block status summary (64/64 `part_<SESSION>_<idx>.json` written)

- `status == "ok"`: 64 / 64 (no `STOPPED_FIDELITY_MISMATCH`, no
  `resource_abort_*`, no `error:*`)
- SCL-arm taxonomy (from `results.json.taxonomy_pooled`): `exact`=62,
  `verify_failed`=2, `decode_failed`=0, `undetected`=0, `resource_abort`=0,
  `fidelity_mismatch`=0 — sums to 64
- The 2 `verify_failed` blocks: `part_G2_23.json` (session G2,
  global_block_index 23, stratum_task `previously_decoded_eval`,
  stratum_official `EVAL_already_decoded`) and `part_G3_38.json` (session
  G3, global_block_index 38, stratum_task `never_decoded`, stratum_official
  `A1_CAL_characterization`)

## Per-block wall / RSS ranges (from each part file's `resources` block, n=64)

- `wall_total_s` (SC descriptive call + SCL decode call, per block):
  min 534.2 s, max 574.4 s, mean 550.9 s
- `wall_sc_s` (SC arm only): min 20.2 s, max 21.9 s
- `wall_scl_s` (SCL arm only): min 513.9 s, max 554.2 s
- `rss_gib_peak_advisory`: min 0.520 GiB, max 0.577 GiB, mean 0.567 GiB
  (well under the 2 GiB/block cap)

## stderr anomalies

`execution_stderr.log` is 6 lines total: 1 garbled UTF-16 `wsl:` locale
banner line (benign, WSL startup noise, not from run.py) + 4 `[setup]`
progress lines (G2/G3 alignment-reproduction + CAL fit, both `H_total`
values reported, matching `results.json.per_session`). No
`Error`/`Exception`/`Traceback`/`abort`/`killed`/`fail` text anywhere in
stderr beyond the benign matches already accounted for above (own
`[setup]` lines and the frozen `resource_abort*` field names inside JSON
output, which do not indicate any triggered abort — the abort counters are
all 0). No other deviation observed.

## Artifacts produced

- `results.json` (154077 bytes)
- `part_G2_00.json` .. `part_G2_31.json`, `part_G3_32.json` ..
  `part_G3_63.json` (64 files total)
- `execution_stdout.log`, `execution_stderr.log` (this run's raw output)
- This file (`EXECUTION_TRANSCRIPT.md`)

No writes outside `workspace/r2_fer_shg_64/`. No git operations performed
by this operator.
