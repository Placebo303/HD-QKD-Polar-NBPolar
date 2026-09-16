# Tier-Y packet — hard-L1 conditioning penalty

## Frozen point

- GF32, N=256, epsilon1=0.05;
- `epsilon2(u1)=0.02+0.36*u1/31` (mean 0.20), normalized injected joint table;
- analytic worst-first K1=45, K2=140;
- streams 2026091470, 2026091471, 2026091472, 128 paired blocks each;
- public tag master=`stream_seed+10000`;
- one attempt containing all 384 pairs;
- output root `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`, absent before execution, exactly five files afterward:
  `frozen_plan.json`, `per_block_paired_outcomes.json`,
  `transcript_accounting.json`, `aggregate_summary.json`, `report.md`;
- 2 GiB address-space and 3600-second wall limit.

Exact WSL command:

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
ulimit -v 2097152
timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m comparison_bench.src.comparison_bench.formal_ir.nbpolar.penalty_gate --n 256 --epsilon1 0.05 --profile strong --k1 45 --k2 140 --seeds 2026091470 2026091471 2026091472 --blocks-per-seed 128 --out-dir .workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate
```

The implementation may add only the smallest statistic/runner wrapper and
focused tests around accepted `two_layer.py`. Do not change the decoder,
construction, prior or protocol.

## Hard integrity gates

384/384 pairing and coverage; P2 cross-u1 max difference >=0.30; provenance
correct; operational truth leak, undetected, nonfinite and resource abort all
zero; four paired cells disjoint/exhaustive; disclosure/tag/control and
transcript recount exact; all focused and predecessor tests pass.

## Scientific discriminator

- oracle exact >=365/384;
- operational-only = 0;
- compute oracle-only count X and the one-sided 95% exact lower bound L solving
  `sum_{j=X}^{384} C(384,j)L^j(1-L)^(384-j)=0.05` by monotone bisection;
- confirm material penalty iff L>0.30.

If integrity gates pass and the discriminator passes, return
`HARD_L1_CONDITIONING_PENALTY_CANDIDATE`. If integrity gates pass but any
scientific discriminator fails, return
`HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED`. An integrity failure returns
`BLOCKED(<earliest gate>)`. Report all four paired cells and marginal outcomes.

Obtain independent Pre-EXECUTE and Pre-RESULT reviews. Attempt is consumed at
the first gate L1 SC call; no rerun/seed/model/K/threshold change.

Forbidden: artifact/real data, empirical construction, N>256, FWHT/SCL,
APP/soft implementation, efficiency/FER/qualification/promotion claim, old
root modification, commit/push.
