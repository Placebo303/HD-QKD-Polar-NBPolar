# Focused review — op-fix-n1024-alloc (Tier-X, reviewer-go)

## Verdict: PASS

1. **Diff vs op-peak-refine/run.py**: every changed line is an authorized delta —
   (i) sign fix `table[a,b]=pmf[(np.arange(Q)[None,:]-np.arange(Q)[:,None])%Q]` = `pmf[(b-a)%Q]`
   applied identically to both `table` and `Wmat`; (ii) new 3-total x 5-share (15-point)
   `POINTS` grid replacing the 3-point `K1_GRID`; (iii) new seeds (2026092901/02), new
   `WALL_LIMIT_S=1200` (matches prereg's `wall<=1200s`); (iv) new output root/PROBE_ID.
   Additions beyond that are benign: three `assert` grid-consistency checks re-deriving
   total/k1/disclosed/f_book from the frozen rule, progress `print(flush=True)` lines,
   `block_wall_s` field (real attribute of `TwoLayerBlockResult`), and aggregation keyed by
   `f_label` (total,k1,k2) rather than `k1` alone. No frozen M2/two-layer/toeplitz/worst_k/
   undetected-isolation/rng logic touched.
2. **Sign-fix correctness**: generative model is `y=(x+delta)%Q` (confirmed in run.py and
   `frozen_params.channel.model`), so `P(Bob=b|Alice=a)=pmf[(b-a)%Q]`. The fixed line computes
   exactly this. `prior.py`'s contract (`smooth_joint_to_conditional`, `_checked_joint_table`)
   stores tables `[Alice,Bob]` with columns (fixed Bob) summing to 1 — `coldev` in results.json
   is consistent with this (checked in code path, not separately re-verified here since it is
   unchanged plumbing). Matches the `[Alice,Bob]=P(A|B)`-adjacent contract cited in the task and
   the predecessor review's diagnosis.
3. **Prereg vs run**: prereg.md's 15-point grid (T248/T305/T382 x shares
   0.047/0.09/0.14/0.20/0.30), seeds, DESIGN_SEED=2026092600, DESIGN_MC=128, wall<=1200s,
   RSS<=1GiB all match `run.py`'s `POINTS`/`SEEDS`/`DESIGN_SEED`/`DESIGN_MC`/`WALL_LIMIT_S`/
   `RSS_LIMIT` verbatim.
4. **results.json arithmetic** (independently recomputed): `H=0.9318300074841255`,
   `HN=954.1939276637445`. Totals `round(f*HN/5)`: f1.30->248, f1.60->305, f2.00->382 — match.
   All 15 `k1=round(share*total)` values match the grid exactly. `disclosed=5*total`
   (1240/1525/1910) and `kdb=disclosed+64` = [1304,1589,1974], matching
   `a3_key_dependent_bits_observed` exactly. `cells={expected:30,completed:30}`
   (2 seeds x 15 points).
5. **Design H1+H2**: `a3_H1_mean=0.0939724719`, `a3_H2_mean=0.8377065469`,
   sum=0.9316790188 ≈ reported 0.931679, close to `H=0.9318300075` (|diff|=0.00015),
   consistent with STATUS.yaml's prelaunch sanity (0.9317 vs 0.93183, diff 0.0002<0.05).
6. **Truth isolation**: global and every per-point `operational_totals`/`oracle_totals` show
   `undetected:0, decode_failed:0, resource_abort:0` throughout — isolated, not merged.
7. **Headline reproduction**: recomputed per-point op/oracle exact counts from results.json
   match the reported headline exactly — op f1.30: 0,8,7,1,0; f1.60: 0,12,26,29,12; f2.00:
   3,19,30,32,32; oracle f1.30: 27,22,12,2,0; f1.60: 32,32,32,29,12; f2.00: 32×5.
8. **Sanity (h) operational ≤ oracle exact**: checked all 15 points — every point satisfies
   op_exact ≤ oracle_exact (e.g. 29≤29 and 12≤12 at two points where they tie; no violation).
   This is expected: the operational arm decodes from `p2` conditioned on the *decoded* L1
   symbol while the oracle arm conditions on the *true* L1 symbol, so oracle strictly
   dominates or ties.
9. **Budgets/reruns/write-scope**: `reruns=0`, `probe_runs=1`, `status=ok`,
   `within_budget=true`, `wall_s=261.503≤1200`, `peak_rss_bytes=216,842,240 (~0.20 GiB)≤1GiB`.
   `git status` shows no writes under `results/`, `comparison_bench/outputs_comparison/`, or
   any unrelated path — only the probe's own `workspace/probes/op-fix-n1024-alloc/` and this
   packet directory were touched (pre-existing dirty files at session start are unrelated).

No FAIL-level issues found.
