# PREREG_DRAFT.md — NBPOLAR-X14-SCL-LIST-SURVIVAL (3-line Tier-X preregistration draft)

The frozen `workspace/probes/nbpolar_x14_scl_list_survival/prereg.md` shall contain exactly these
three lines (plus the packet pointer header used by X08/X09/X10 convention — line count applies
to the registration body). Written BEFORE any synthetic generation; the operator copies this
verbatim at freeze after re-verifying seed freshness by repo grep.

1. Question: with the frozen empirical channel structure reproduced synthetically (96/1024 ≈ 9.375% planted floor-mass cells vs recorded 3063/32768 ≈ 9.3475%), does the true (b,u1,u2) cell rank within the top-L (L=4,8) per-position arm-table likelihood at frozen-hazard spike positions (excess ≥ 2.0 bits over prefix mean, strata [2,4)/[4,8)/[8,∞)), with symmetric L1-column ranking (Q1b) and a local-spike (R=8) vs mean-hazard top-52 coverage comparison on greedy-SC mismatches (Q2) — descriptive survival/coverage fractions only, no thresholds, no verdicts, SCL stays locked.
2. Parameters: N=256, q=32, alpha=2, GF(32) poly 37, chunk_rows=512, floor 1e-15, p_b uniform over 1024 labels, s=96 deterministic rare symbols per column + Dirichlet(1.0) remainder, K2_synth=52, table-master seed 2026092350, block seeds 2026092351..2026092357 × 4 blocks (28 blocks, 7168 L2 positions), read-only reuse of empirical_channel/prior/algebra/transform/sc (greedy L=1 only), zero protected opens, zero tag calls.
3. Command: `cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && timeout 300 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python workspace/probes/nbpolar_x14_scl_list_survival/body.py` (interpreter fallback recorded if numpy missing; bare python/python3 never used).
