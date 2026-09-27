import sys, ast, time
import numpy as np

sys.path.insert(0, "/mnt/d/Code/qkd-reconciliation-lab/src")
sys.path.insert(0, "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/comparison_bench/src")
from comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.formal_ir.nbpolar.prior import (build_p1_metrics, gather_p2_metrics,
    probs_to_symbol_metric, Provenance)
from comparison_bench.formal_ir.nbpolar.sc import sc_decode
from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.formal_ir.nbpolar.transform import polar_transform

Q = 1024; R = 10; N = 1024; ALPHA = 2
P_F4 = {"p0": 0.75, "p1": 0.24, "pm1": 0.005, "prest": 0.005}
DESIGN_SEED = 2026092600
DESIGN_MC = 128

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
H = float(-(pmf[pmf > 0] * np.log2(pmf[pmf > 0])).sum())
print("(a) H (true channel entropy) =", H)

# corrected table: table[a,b] = pmf[(b-a)%Q]
table = pmf[(np.arange(Q)[None, :] - np.arange(Q)[:, None]) % Q]
p1, p2 = tl.layer_metric_tables(table)
field = make_gf32()

t0 = time.perf_counter()
rng = np.random.default_rng(DESIGN_SEED)
H1 = np.zeros(N)
H2 = np.zeros(N)
allpos = np.arange(N)
for m in range(DESIGN_MC):
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
H1 /= DESIGN_MC
H2 /= DESIGN_MC
h1m, h2m = float(H1.mean()), float(H2.mean())
dt = time.perf_counter() - t0
print("(a) N=1024 DESIGN_MC=128 design_seed=2026092600 (sign-corrected table): H1=%.4f H2=%.4f sum=%.4f |sum-H|=%.4f wall=%.1fs"
      % (h1m, h2m, h1m + h2m, abs(h1m + h2m - H), dt))
print("(a) PASS" if abs(h1m + h2m - H) < 0.05 else "(a) FAIL")

# (b) AST %-format placeholder/argument-count check on run.py
import re
src_path = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-fix-n1024-alloc/run.py"
src = open(src_path).read()
tree = ast.parse(src)
mismatches = []
checked = 0
for node in ast.walk(tree):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
        fmt = node.left.value
        placeholders = re.findall(r"%(?:\([a-zA-Z_]+\)?)?[-+ #0]*[0-9*]*\.?[0-9*]*[sdifr%]", fmt)
        n_ph = len([p for p in placeholders if not p.endswith("%%") and p != "%%"])
        n_pct_literal = fmt.count("%%")
        checked += 1
        rhs = node.right
        if isinstance(rhs, ast.Tuple):
            n_args = len(rhs.elts)
        else:
            n_args = 1
        if n_ph != n_args:
            mismatches.append((fmt[:80], n_ph, n_args))
print("(b) checked %d %%-format expressions, mismatches=%d" % (checked, len(mismatches)))
for m in mismatches:
    print("   MISMATCH:", m)
print("(b) PASS" if not mismatches else "(b) FAIL")
