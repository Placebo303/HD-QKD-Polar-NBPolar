# Focused review — op-fix-n32k-alloc (Tier-X, reviewer-go)

## Verdict: PASS

1. **Diff vs op-n32k-ratio/run.py**: authorized deltas only — (i) sign fix
   `table[a,b]=pmf[(np.arange(Q)[None,:]-np.arange(Q)[:,None])%Q]` = `pmf[(b-a)%Q]` applied
   identically to `table` and `Wmat` (predecessor used `pmf[(a-b)%Q]`); (ii) grid changed to
   f_book {1.15,1.30} (8 points) replacing {1.30,1.60}; (iii) new seeds (2026092903/04); (iv)
   new output root/PROBE_ID. `DESIGN_MC=64`, `BLOCKS=8`, `DESIGN_SEED=2026092800`,
   `WALL_LIMIT_S=5400`, `RSS_LIMIT=4GiB` all held identical to the predecessor, as claimed —
   confirmed by direct comparison of the two files. No frozen M2/two-layer/toeplitz/worst_k/
   undetected-isolation/rng logic touched.
2. **Sign-fix correctness**: same fix as op-fix-n1024-alloc, same generative model
   `y=(x+delta)%Q` → `P(Bob=b|Alice=a)=pmf[(b-a)%Q]`; the fixed line computes this correctly.
   Consistent with `prior.py`'s `[Alice,Bob]` table contract.
3. **Prereg vs run**: prereg.md's 8-point grid (T7023/T7939 x shares
   319/6811,0.09,0.14,0.20), seeds 2026092903/04, `design_seed=2026092800`, `DESIGN_MC=64`,
   `wall<=5400s`, `RSS<=4GiB`, and the launch-gate note ("launched only after
   op-fix-n1024-alloc finished") all match `run.py` and `STATUS.yaml`'s `launch_gate` field
   verbatim.
4. **results.json arithmetic** (independently recomputed): `H=0.9318300074841255`,
   `HN=30534.205685239824`. Totals `round(f*HN/5)`: f1.15->7023, f1.30->7939 — match. All 8
   `k1=round(share*total)` values match the grid exactly (T7939 row numerically identical to
   op-n32k-ratio's own T7939 row, as noted in prereg, since both derive from the same H·N
   rounding rule). `disclosed=5*total` (35115/39695) and `kdb=disclosed+64`=[35179,39759],
   matching `a3_key_dependent_bits_observed` exactly. `cells={expected:16,completed:16}`
   (2 seeds x 8 points).
5. **Design H1+H2**: `a3_H1_mean=0.0942625685`, `a3_H2_mean=0.8373663084`,
   sum=0.9316288769 ≈ reported 0.931629, close to `H=0.9318300075` (|diff|=0.0002). This is a
   genuine full N=32768 design pass (not merely inherited from the N=1024 pre-launch check),
   and it independently corroborates the sign-fix diagnosis at the target scale.
6. **Truth isolation**: global and every per-point `operational_totals`/`oracle_totals` show
   `undetected:0, decode_failed:0, resource_abort:0` throughout — isolated, not merged.
7. **Headline reproduction**: recomputed per-point op/oracle exact counts from results.json
   match the reported headline exactly — op f1.15: 0,0,0,0; f1.30: 0,0,13,2; oracle f1.15:
   12,2,0,0; f1.30: 16,16,13,2.
8. **Sanity (h) operational ≤ oracle exact**: checked all 8 points — every point satisfies
   op_exact ≤ oracle_exact (13≤13 and 2≤2 tie at two points; no violation). Expected for the
   same reason as the N=1024 probe: oracle conditions L2 decode on the true L1 symbol,
   operational on the decoded one.
9. **Budgets/reruns/write-scope**: `reruns=0`, `probe_runs=1`, `status=ok`,
   `within_budget=true`, `wall_s=3481.066≤5400`, `peak_rss_bytes=1,208,664,064 (~1.13 GiB)≤4GiB`.
   `git status` shows no writes under `results/`, `comparison_bench/outputs_comparison/`, or
   any unrelated path — only the probe's own `workspace/probes/op-fix-n32k-alloc/` and this
   packet directory were touched (pre-existing dirty files at session start are unrelated).

No FAIL-level issues found.
