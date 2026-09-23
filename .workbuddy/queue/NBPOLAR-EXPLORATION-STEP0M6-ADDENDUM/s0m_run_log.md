# RUN LOG — NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM (s0m_runs=1, reruns=0, rebuilds=1)

## P0 draft check (PASS, before any write)

- branch: `.git/HEAD` = `ref: refs/heads/codex/nbpolar-phase0`;
  `git branch --show-current` = `codex/nbpolar-phase0`. No switch.
- packet dir: exactly 4 files (TASK_PACKET.md, STATUS.yaml,
  AUTHORIZATION_PROMPT.md, prereg_frozen.md).
- M6 exists: `comparison_bench/outputs_comparison/real_frame_batch.parquet`
  (12597 bytes; PAR1 magic confirmed read-only).
- protected root `workspace/exploration/nbpolar-native-highdim/step0/`:
  exactly 3 files, sizes prereg.md=3900 / results.json=29953 / notes.md=1987
  bytes; NOT modified (re-checked at end — same sizes).
- output root `.../step0-m6-addendum/`: ABSENT before P1.

## Interpreter probes (ordered policy, nothing installed, read-only)

- (1) `/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python`
  (3.12.3): pandas 3.0.2 + numpy present; pyarrow/fastparquet/duckdb/polars
  absent. Functional probe `pandas.read_parquet(M6)` =>
  `ImportError: Unable to find a usable engine; tried using: 'pyarrow',
  'fastparquet'` (recorded verbatim in results.json).
- (2) import-only probes: hd-qkd-polar-release (pandas, no pyarrow),
  paper2slides (pandas, no pyarrow), time-tagger-tools (pandas, no pyarrow);
  jti-extract-clean / jti-extract-cn / timetagger (neither pandas nor
  pyarrow); /usr/bin/python3 (neither). No system interpreter imports
  pyarrow or fastparquet. Repo `.venv/` does not exist.
- (3) => reader check FAILS; UNMEASURABLE terminal per packet (not a stop).

## P1

- `mkdir` output root; `cp prereg_frozen.md -> prereg.md`; `cmp` =>
  BYTE-IDENTICAL.

## P2 runs

- Run 1 (zero-output crash): `s0m6_check.py` called
  `os.makedirs(out_root, exist_ok=False)` on the P1-created root =>
  `FileExistsError: [Errno 17] File exists`. No artifact written by the
  script (prereg.md from P1 untouched). Corrective rebuild #1 (allowed:
  exactly one after a zero-output crash): replaced `makedirs` with a
  guard requiring the pre-existing out-root + prereg.md.
- Run 2 (the counted run): exit 0, elapsed 0.432 s, wrote results.json +
  notes.md in one end-of-run pass. Outcome: `failing_check=reader`,
  `occupancy.status=UNMEASURABLE_FROM_FROZEN_ARTIFACTS`;
  column/alphabet/provenance `not_run` (in-order stop). Manifest context
  (stdlib json, read-only): dataset_ids=['synthetic_d8_ser005'],
  dimensions=[8] — context only, not a check verdict.
- Counter fix: `counters.rebuilds` 0 -> 1 in results.json + notes.md
  budget line (this log is the record of the rebuild).

## P3 verification (end of run)

- output root holds exactly 3 files: prereg.md / results.json / notes.md.
- protected step0 root re-checked: 3 files, sizes 3900 / 29953 / 1987 bytes
  (unchanged).
- `git status --short`: no new entries under `comparison_bench/`,
  `results/`, protected root, or other `workspace/` paths from this task
  (pre-existing dirty/untracked worktree files preserved untouched).
- No installs, no network, no decoder, no claim language.

## Exact command (run 2)

`/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python .workbuddy/queue/NBPOLAR-EXPLORATION-STEP0M6-ADDENDUM/s0m6_check.py --out-root workspace/exploration/nbpolar-native-highdim/step0-m6-addendum/`
