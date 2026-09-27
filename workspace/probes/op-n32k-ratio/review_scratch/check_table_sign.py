import sys, time
import numpy as np

sys.path.insert(0, "/mnt/d/Code/qkd-reconciliation-lab/src")
sys.path.insert(0, "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src")
from comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.formal_ir.nbpolar.prior import (build_p1_metrics, gather_p2_metrics,
    probs_to_symbol_metric, Provenance)
from comparison_bench.formal_ir.nbpolar.sc import sc_decode
from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.formal_ir.nbpolar.transform import polar_transform

Q = 1024; R = 10; ALPHA = 2
P_F4 = {"p0": 0.75, "p1": 0.24, "pm1": 0.005, "prest": 0.005}

def f4_pmf(q):
    p = np.zeros(q)
    p[0] = P_F4["p0"]
    p[1 % q] = P_F4["p1"]
    p[(q - 1) % q] = P_F4["pm1"]
    rest = [d for d in range(q) if d not in (0, 1 % q, (q - 1) % q)]
    for d in rest:
        p[d] = P_F4["prest"] / (q - 3)
    assert abs(p.sum() - 1.0) < 1e-12
    return p

pmf = f4_pmf(Q)
H_true = float(-(pmf[pmf > 0] * np.log2(pmf[pmf > 0])).sum())
print("H_F4 (exact, entropy of true delta pmf) =", H_true)

# Cross-entropy of true delta under the MIRRORED delta model (pmf(-delta)):
mirror = pmf[(-np.arange(Q)) % Q]
with np.errstate(divide="ignore"):
    ce_mirror = float(-(pmf * np.where(mirror > 0, np.log2(mirror, out=np.full(Q, -np.inf), where=mirror > 0), -np.inf)).sum())
print("cross-entropy H(true_delta || mirrored_model_delta) =", ce_mirror)
print("KL(true || mirror) = ce - H =", ce_mirror - H_true)

def run_design(N, NLOG, mc, seed, use_bug):
    field = make_gf32()
    if use_bug:
        table = pmf[(np.arange(Q)[:, None] - np.arange(Q)[None, :]) % Q]  # code as-is (a-b)
    else:
        table = pmf[(np.arange(Q)[None, :] - np.arange(Q)[:, None]) % Q]  # corrected (b-a) -> table[a,b]=pmf[(b-a)%Q]
    colsum = table.sum(axis=0)
    rowsum = table.sum(axis=1)
    p1, p2 = tl.layer_metric_tables(table)

    def natural_EJB(i):
        E = 1 << i
        L = 1 << (R - 1 - i)
        e = np.arange(E)[:, None, None]
        b = np.array([0, 1])[None, :, None]
        l = np.arange(L)[None, None, :]
        return (e | (b << i) | (l << (i + 1))).astype(np.int64)

    rng = np.random.default_rng(seed)
    H1 = np.zeros(N)
    H2 = np.zeros(N)
    allpos = np.arange(N)
    for m in range(mc):
        x = rng.integers(0, Q, size=N)
        dd = rng.choice(Q, size=N, p=pmf)
        y = (x + dd) % Q
        high = (x >> 5).astype(np.int64)
        low = (x & 31).astype(np.int64)
        bob = y.astype(np.int64)
        mtr1 = probs_to_symbol_metric(build_p1_metrics(bob[None, :], p1)[0],
                                      provenance=Provenance.PRIOR_ONLY)
        r1 = sc_decode(mtr1.logp, field=field, alpha=ALPHA, known_positions=allpos,
                       known_values=polar_transform(high, field=field, alpha=ALPHA))
        pr = np.exp(r1.decision_metrics)
        with np.errstate(divide="ignore"):
            lg = np.log2(pr, out=np.zeros_like(pr), where=pr > 0)
        H1 += -(np.where(pr > 0, pr * lg, 0.0)).sum(axis=1)
        mtr2 = probs_to_symbol_metric(gather_p2_metrics(bob[None, :], high[None, :], p2)[0],
                                      provenance=Provenance.ORACLE_CONDITIONED)
        r2 = sc_decode(mtr2.logp, field=field, alpha=ALPHA, known_positions=allpos,
                       known_values=polar_transform(low, field=field, alpha=ALPHA))
        pr = np.exp(r2.decision_metrics)
        with np.errstate(divide="ignore"):
            lg = np.log2(pr, out=np.zeros_like(pr), where=pr > 0)
        H2 += -(np.where(pr > 0, pr * lg, 0.0)).sum(axis=1)
    H1 /= mc
    H2 /= mc
    return float(H1.mean()), float(H2.mean()), float(np.abs(colsum - 1).max()), float(np.abs(rowsum - 1).max())

for N, NLOG in ((256, 8), (1024, 10)):
    for use_bug, label in ((True, "AS-CODED(a-b)"), (False, "CORRECTED(b-a)")):
        t0 = time.perf_counter()
        h1, h2, cdev, rdev = run_design(N, NLOG, mc=48, seed=99001, use_bug=use_bug)
        dt = time.perf_counter() - t0
        print("N=%d %s H1=%.4f H2=%.4f sum=%.4f coldev=%.2e rowdev=%.2e wall=%.1fs"
              % (N, label, h1, h2, h1 + h2, cdev, rdev, dt))
