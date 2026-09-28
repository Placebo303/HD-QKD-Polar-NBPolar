# EXECUTION TRANSCRIPT — m2-scl-check-g2g3-success

Attempt 1 (the only attempt; no rerun needed).

## Authorization / gates satisfied before launch

- PI authorization on file: "授权，19 块也跑 SCL L=16" (`AUTHORIZATION_PROMPT.md`).
- Independent Pre-EXECUTE review: **PASS** (`PRE_EXECUTE_REVIEW.md`, reviewer-go).
- Main-thread rulings D_NEW1/D_NEW2: **ACCEPTED** (`STATUS.yaml`
  `main_thread_rulings_successor_2026_09_28`).
- One-shot readiness re-confirmed immediately before launch: `results.json`
  and all 19 `part_*.json` absent.
- Environment check immediately before launch:
  `wsl.exe -e bash -c "echo wsl_ok; whoami; ls -la /home/karel_303/.venvs/timetagger/bin/python; ls -ld /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"`
  → `wsl_ok`, `karel_303`, venv `python -> python3` symlink present, repo
  mount present.

## Launch

- Mechanism: Bash tool `run_in_background: true` wrapping a single
  **foreground** `wsl.exe -e bash -c "..."` call (no `nohup`, no trailing
  `&`, no `cd` — absolute paths only), running `prereg.md`'s C-line command
  verbatim:

  ```
  PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar /home/karel_303/.venvs/timetagger/bin/python /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/m2_scl_check_g2g3_success/run.py
  ```

- Background task id: `btaap3hf3`.
- Started (UTC): `2026-09-28T05:53:42Z`.
- Completed: exit code **0**. Total notified wall time ≈ 30 minutes
  (matches `results.json["timing"]["wall_s_total"] = 1643.53s` ≈ 27.4 min
  compute + setup, consistent with the ≈35 min estimate in
  `TASK_PACKET.md` §6 / `prereg.md`).

## stdout/stderr (verbatim, minus the WSL launcher's own UTF-16 startup
banner noise, which is a `wsl.exe` console-encoding artifact unrelated to
the Python process)

```
[setup] reproducing G2 session context (raw read + align + CAL fit)...
[setup] G2 ready: H_total=0.816814 bits, f_book_no_crc=1.274745, f_book_with_crc=1.275343
[setup] reproducing G3 session context (raw read + align + CAL fit)...
[setup] G3 ready: H_total=0.821478 bits, f_book_no_crc=1.267507, f_book_with_crc=1.268101
DONE fidelity_ok=19/19 fidelity_mismatch=0 preserved_exact=19 broken=0 undetected=0 errors_or_aborts=0 wall_s=1643.5

[exited with code 0]
```

## Artifacts produced (all additive; none pre-existed)

- `results.json`
- `part_G2_00.json`, `part_G2_02.json`, `part_G2_03.json`, `part_G2_04.json`,
  `part_G2_06.json`, `part_G2_07.json`, `part_G2_08.json`, `part_G2_09.json`,
  `part_G2_10.json`, `part_G2_11.json`, `part_G2_13.json` (11 G2 blocks)
- `part_G3_03.json`, `part_G3_05.json`, `part_G3_06.json`, `part_G3_07.json`,
  `part_G3_08.json`, `part_G3_09.json`, `part_G3_12.json`, `part_G3_13.json`
  (8 G3 blocks)

No `session_setup_execution_error_attemptN.json` was created — no
pre-measurement execution defect occurred (unlike the predecessor packet's
attempt 1). This is attempt 1 and the only attempt; `reruns=0`.

## Result headline (descriptive; no verdict rendered by this operator)

`fidelity_compromised = False`. `summary = {n_targets: 19, n_fidelity_ok:
19, n_fidelity_mismatch: 0, n_preserved_exact: 19, n_broken: 0,
n_undetected: 0, n_errors_or_aborts: 0}`.

Full per-block breakdown (all 5 fidelity fields, all 7 SCL outcome fields,
per-block wall times) is reported separately to the main thread; see also
`results.json["blocks"]` for the machine-readable record.

## Next gate

Independent Pre-RESULT review of `results.json` / this transcript is
required (per AGENTS.md §3/§10.3) before any citation in an
adjudication/decision-log entry. Not performed by this operator.
