#!/usr/bin/env bash
# Relaunch of the 6 SCL/oracle workers only (SC arm already completed OK in
# attempt1: part_SC.json present). Rerun justification (AGENTS Tier-X rerun
# exception): attempt1's single combined `&&`/`&` one-liner had a shell
# precedence bug -- `A && B && C && CMD1 & CMD2 & CMD3 & ...` backgrounds the
# WHOLE `A&&B&&C&&CMD1` chain as job1 (so cd/PROBE/PY/export only applied
# inside job1's own subshell), while CMD2..CMD7 forked as separate jobs from
# the ORIGINAL shell that never ran cd/PROBE=/PY=/export -- all 6 SCL workers
# died instantly on the redirection (PROBE empty -> tried to write
# "/log_scl_*.txt" at filesystem root -> Permission denied), before drawing
# any block (0 measurement). This is exactly the "implementation-defect
# death before any measurement" exception in prereg.md's rerun_policy: kept
# as evidence in log_relaunch_attempt1_combined.txt (the earlier captured
# transcript output), fixed here by putting cd/var-assignment/export on
# their own lines (no `&&` chain ending in `&`) before backgrounding, and
# relaunched once. No parameter/seed/L change.
set -u

ROOT=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
PROBE=$ROOT/workspace/probes/scl-gate-t3
PY=/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
export NUMBA_CACHE_DIR="$PROBE/.numba_cache"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMBA_NUM_THREADS=1

date

"$PY" "$PROBE/run.py" scl --point A --L 4  > "$PROBE/log_scl_A_L4.txt"  2>&1 &
"$PY" "$PROBE/run.py" scl --point B --L 4  > "$PROBE/log_scl_B_L4.txt"  2>&1 &
"$PY" "$PROBE/run.py" scl --point A --L 8  > "$PROBE/log_scl_A_L8.txt"  2>&1 &
"$PY" "$PROBE/run.py" scl --point B --L 8  > "$PROBE/log_scl_B_L8.txt"  2>&1 &
"$PY" "$PROBE/run.py" scl --point A --L 16 > "$PROBE/log_scl_A_L16.txt" 2>&1 &
"$PY" "$PROBE/run.py" scl --point B --L 16 > "$PROBE/log_scl_B_L16.txt" 2>&1 &
wait

echo ALL_6_SCL_WORKERS_DONE
date
