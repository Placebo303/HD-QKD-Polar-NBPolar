#!/bin/bash
export NUMBA_CACHE_DIR=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2c_strong_binary_msd_shg_64/_stage/numba_cache
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/r2c-layer-diag
exec /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python -u "$@"
