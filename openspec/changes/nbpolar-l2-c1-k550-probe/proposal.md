# Proposal: bounded L2 C1 synthetic probe at k2=550

## Why

The prior `l2-singlefactor-k550` Tier-X run stopped before decoder measurement because its BASE and C3 information sets were identical (550/550 overlap). The main thread selected the next bounded candidate, C1, to compare the same frozen single-factor BASE against the reverse-Shannon information set.

## Scope

Prepare one new synthetic-only Tier-X probe at `N=1024`, `k1=10`, and `k2=550`. BASE remains `worst_k(H2,550)`. CAND is `best_k(H2,550)`, formed by ascending H2 with stable ordering so equal H2 values break ties by ascending index. Both arms use the same design MC rows and paired `(x,y)` per `(seed,block)`.

The packet reports descriptive counts only. A design-stage gate stops before measurement when the sets are identical or overlap is at least 495/550. One result record, one-shot execution, and no automatic successor are specified.

## Boundaries

- No real/protected data or artifact access. The inherited runner's only external code dependency is the read-only `qkd_recon.polar_core` import from `/mnt/d/Code/qkd-reconciliation-lab/src`; no writes are made there. No original Polar baseline, `results/`, or `comparison_bench/outputs_comparison/` writes.
- No FER, efficiency, security, R2-sizing, construction-superiority, prior-attribution, or qualification claim.
- No fallback k2, extra samples, retuning, rerun, or follow-on candidate in this change.
- This change prepares OpenSpec, preregistration, runner, and packet only. The user has granted broad synthetic-work authorization; execution still awaits main-thread freeze review.
