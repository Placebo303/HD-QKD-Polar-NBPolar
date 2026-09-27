"""Non-protocol timing smoke (Tier-X pre-launch check; not a result).

Measures wall time for one scl_joint_decode L1 call and one L2 call at
N=32768, GF32, for list_width_L in {4,8,16}, using seed=1 (explicitly a
non-protocol seed, never used by the frozen grid). Purpose: inform process
layout / feasibility only -- no parameter tuning of the frozen grid follows
from this, per AGENTS.md Tier-X rules. Writes only under this probe root.
"""
import sys, time
import numpy as np

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
sys.path.insert(0, ROOT + "/comparison_bench/src")

from comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.formal_ir.nbpolar import scl_joint
from comparison_bench.formal_ir.nbpolar.prior import (
    build_p1_metrics, gather_p2_metrics, probs_to_symbol_metric, Provenance,
    apply_explicit_floor,
)
from comparison_bench.formal_ir.nbpolar.algebra import make_gf32

Q = 1024
N = 32768
ALPHA = 2

def matched_pmf_raw(q):
    p = np.zeros(q)
    p[0] = 0.7562
    p[1 % q] = 0.0018
    p[(q - 1) % q] = 0.2419
    return p

def main():
    field = make_gf32()
    pmf_floor = apply_explicit_floor(matched_pmf_raw(Q), 1e-15, reason="timing smoke (non-protocol)")
    table = pmf_floor[(np.arange(Q)[None, :] - np.arange(Q)[:, None]) % Q]
    p1, p2 = tl.layer_metric_tables(table)

    rng = np.random.default_rng(1)  # non-protocol seed
    x = rng.integers(0, Q, size=N)
    dd = rng.choice(Q, size=N, p=matched_pmf_raw(Q) / matched_pmf_raw(Q).sum())
    y = (x + dd) % Q
    high = (x >> 5).astype(np.int64)
    low = (x & 31).astype(np.int64)
    bob = y.astype(np.int64)

    k1, k2 = 301, 6120
    d1 = np.sort(rng.choice(N, size=k1, replace=False)).astype(np.int64)
    d2 = np.sort(rng.choice(N, size=k2, replace=False)).astype(np.int64)
    from comparison_bench.formal_ir.nbpolar.transform import polar_transform
    u1_true = polar_transform(high, field=field, alpha=ALPHA)
    u2_true = polar_transform(low, field=field, alpha=ALPHA)
    val1 = u1_true[d1]
    val2 = u2_true[d2]
    labels_true = (low + tl.LABEL_SCALE * high).astype(np.int64)
    crc_true = scl_joint.labels_crc16(labels_true)

    for L in (4, 8, 16):
        t0 = time.perf_counter()
        got = scl_joint.scl_joint_decode(
            bob, crc_true, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
            list_width_L=L, top_m=4,
        )
        dt = time.perf_counter() - t0
        print(f"L={L} top_m={got.top_m_used} candidates={got.candidates_considered} "
              f"wall_s={dt:.3f} label_exact={got.label_hat.tolist()==labels_true.tolist()} "
              f"crc_pass={got.crc_pass}", flush=True)

if __name__ == "__main__":
    main()
