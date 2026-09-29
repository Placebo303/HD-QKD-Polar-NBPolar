#!/bin/bash
# usage: ./r.sh script args   (from git bash)
MSYS_NO_PATHCONV=1 wsl.exe -e bash /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/r2c-layer-diag/w.sh "$@" 2>&1 | tr -d '\000' | grep -av "^wsl:"
