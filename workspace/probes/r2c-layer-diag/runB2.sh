#!/bin/bash
cd /d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/r2c-layer-diag
run4() { for l in "$@"; do ./r.sh partB2.py $l > logB2_$l.txt 2>&1; done; }
run4 9 0 4 & run4 8 1 5 & run4 7 2 6 & run4 3 & wait
