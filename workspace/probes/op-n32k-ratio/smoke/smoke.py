# NON-RESULT timing smoke for op-n32k-ratio: 1 design MC sample + 1 block at 1 point, seed 1.
# Used only to size B and DESIGN_MC. Not a measurement.
import sys, time, json
import numpy as np, resource
sys.path.insert(0, "/mnt/d/Code/qkd-reconciliation-lab/src")
from comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.formal_ir.nbpolar.prior import build_p1_metrics, gather_p2_metrics, probs_to_symbol_metric, Provenance
from comparison_bench.formal_ir.nbpolar.sc import sc_decode
from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.formal_ir.nbpolar.transform import polar_transform
Q = 1024; N = 32768; ALPHA = 2
T0 = time.perf_counter()
p = np.zeros(Q); p[0] = .75; p[1] = .24; p[Q-1] = .005
rest = [d for d in range(Q) if d not in (0, 1, Q-1)]; p[rest] = .005/(Q-3)
table = p[(np.arange(Q)[:, None] - np.arange(Q)[None, :]) % Q]
p1, p2 = tl.layer_metric_tables(table)
field = make_gf32()
rng = np.random.default_rng(1)
allpos = np.arange(N)
t = time.perf_counter()
x = rng.integers(0, Q, size=N); dd = rng.choice(Q, size=N, p=p); y = (x + dd) % Q
high = x >> 5; low = x & 31; bob = y
m1 = probs_to_symbol_metric(build_p1_metrics(bob[None, :], p1)[0], provenance=Provenance.PRIOR_ONLY)
r1 = sc_decode(m1.logp, field=field, alpha=ALPHA, known_positions=allpos, known_values=polar_transform(high, field=field, alpha=ALPHA))
pr = np.exp(r1.decision_metrics)
H1 = -(np.where(pr > 0, pr*np.log2(np.where(pr > 0, pr, 1)), 0)).sum(axis=1)
m2 = probs_to_symbol_metric(gather_p2_metrics(bob[None, :], high[None, :], p2)[0], provenance=Provenance.ORACLE_CONDITIONED)
r2 = sc_decode(m2.logp, field=field, alpha=ALPHA, known_positions=allpos, known_values=polar_transform(low, field=field, alpha=ALPHA))
pr = np.exp(r2.decision_metrics)
H2 = -(np.where(pr > 0, pr*np.log2(np.where(pr > 0, pr, 1)), 0)).sum(axis=1)
t_design = time.perf_counter() - t
k1, k2 = 715, 7224
d1 = np.sort(np.argsort(-H1, kind="stable")[:k1]); d2 = np.sort(np.argsort(-H2, kind="stable")[:k2])
t = time.perf_counter()
rb = np.random.default_rng([1, 0])
x = rb.integers(0, Q, size=N); dd = rb.choice(Q, size=N, p=p); y = (x + dd) % Q
res = tl.run_two_layer_block(0, x >> 5, x & 31, y, field=field, p1_table=p1, p2_table=p2, d1=d1, d2=d2, n=N, k1=k1, k2=k2, toeplitz_master=tl.FROZEN_TOEPLITZ_MASTER)
t_block = time.perf_counter() - t
out = {"label": "NON-RESULT timing smoke (seed 1, 1 design sample, 1 block, k1=715,k2=7224; d1/d2 from 1-sample H)",
       "design_sample_s": t_design, "block_s": t_block,
       "block_op_outcome": res.operational.outcome, "block_oracle_outcome": res.oracle.outcome,
       "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
       "total_s": time.perf_counter() - T0}
print(json.dumps(out, indent=2))
with open("/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-n32k-ratio/smoke/smoke_timing.json", "w") as fh:
    json.dump(out, fh, indent=2)
