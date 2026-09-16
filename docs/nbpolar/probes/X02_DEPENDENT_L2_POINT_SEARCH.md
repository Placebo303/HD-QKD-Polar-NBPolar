# X02 — dependent-L2 operating-point search (Tier X)

Question: find whether any N=256 injected dependent-L2 point combines high
oracle recovery with a measurable operational-vs-oracle gap, so a later Tier-Y
gate is informative rather than trivially weak.

Freeze before execution:

- dependence profiles with mean epsilon2=0.20: weak
  `0.14+0.12*u1/31`, medium `0.08+0.24*u1/31`, strong
  `0.02+0.36*u1/31`; epsilon1=0.05;
- K1 in `{45,64,96,128}`, K2 in `{110,140,170,200,230}`;
- seeds `2026091450..2026091452`, 32 paired blocks/configuration, N=256;
- public master=`seed+10000`; analytic worst-first sets; accepted P4 runner;
- output root `workspace/probes/nbpolar_x02_dependent_l2_point_search/` with
  exactly `prereg.md` and `results.json`.

For all 60 configurations report per-seed operational/oracle exact and failures,
paired exact gap, disclosure, P2 cross-u1 maximum difference, mean/std/range.
Rank descriptively by: oracle mean exact rate descending, operational/oracle
gap magnitude descending, total disclosed bits ascending, then profile/K1/K2.
Also list configurations satisfying the descriptive region
`oracle mean >= 0.90` and `paired gap mean >= 0.05`; these are screening labels,
not pass/fail gates. If none exist, report none without expanding the grid.

No code or workflow edits, thresholds, candidate/accepted token, attempt,
artifact/real data, old-root write, ledger/memory update, commit or push.
Execution errors may be rerun and must be recorded; frozen parameters may not
change. Return one compact summary and one focused arithmetic review.
