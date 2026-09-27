#!/usr/bin/env bash
# scl-gate-t3 launcher: pre-launch checks, then design -> smoke -> 7 parallel
# workers (SC + 6x SCL/oracle) -> aggregate. Frozen one-shot launch; no
# parameter tuning. All writes stay under workspace/probes/scl-gate-t3/.
set -euo pipefail

ROOT=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
PROBE=$ROOT/workspace/probes/scl-gate-t3
PY=/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python
export PYTHONDONTWRITEBYTECODE=1
export NUMBA_CACHE_DIR=$PROBE/.numba_cache
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMBA_NUM_THREADS=1

echo "=== pre-launch check: results.json absent ==="
if [ -f "$PROBE/results.json" ]; then
  echo "ABORT: results.json already exists"; exit 2
fi

echo "=== pre-launch check: current time (Get-Date-equivalent via date) ==="
date

echo "=== step: design ==="
"$PY" "$PROBE/run.py" design

echo "=== pre-launch check: 1-block L=4 smoke (non-protocol seed=1, not counted) ==="
"$PY" "$PROBE/run.py" smoke

echo "=== launching 7 parallel workers ==="
"$PY" "$PROBE/run.py" sc            > "$PROBE/log_sc.txt"          2>&1 &
"$PY" "$PROBE/run.py" scl --point A --L 4  > "$PROBE/log_scl_A_L4.txt"  2>&1 &
"$PY" "$PROBE/run.py" scl --point B --L 4  > "$PROBE/log_scl_B_L4.txt"  2>&1 &
"$PY" "$PROBE/run.py" scl --point A --L 8  > "$PROBE/log_scl_A_L8.txt"  2>&1 &
"$PY" "$PROBE/run.py" scl --point B --L 8  > "$PROBE/log_scl_B_L8.txt"  2>&1 &
"$PY" "$PROBE/run.py" scl --point A --L 16 > "$PROBE/log_scl_A_L16.txt" 2>&1 &
"$PY" "$PROBE/run.py" scl --point B --L 16 > "$PROBE/log_scl_B_L16.txt" 2>&1 &
wait
echo "=== all 7 workers finished (or errored; see logs) ==="

echo "=== step: aggregate ==="
"$PY" "$PROBE/aggregate.py"
echo "=== DONE ==="
