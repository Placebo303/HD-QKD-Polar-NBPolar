"""Reviewer scratch (read-only): per-block mismatch report for T-a claim.

Same sampling order as test_nbpolar_scl_joint.test_l1_m1_identity_matched_channel
(TEST_SEED_A=2026092751), but reports which block indices mismatch instead of
only a total count, to check whether the actual pytest-covered blocks (0..3)
are among the failures.
"""
import sys

sys.path.insert(0, r"D:\Code\HD-QKD_Polar_Comparison-nbpolar")

import numpy as np

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl_joint
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as two_layer_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import apply_explicit_floor
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform

GF32 = make_gf32()
ALPHA = 2
Q = 1024
TEST_SEED_A = 2026092751


def g1r2_matched_table(q=Q):
    pmf_raw = np.zeros(q, dtype=np.float64)
    pmf_raw[0] = 0.7562
    pmf_raw[1 % q] = 0.0018
    pmf_raw[(q - 1) % q] = 0.2419
    pmf = apply_explicit_floor(pmf_raw, 1e-15, reason="reviewer repro (scratch, read-only)")
    delta = (np.arange(q)[None, :] - np.arange(q)[:, None]) % q
    return pmf[delta]


def sample_block(rng, n, table):
    q = table.shape[0]
    x = rng.integers(0, q, size=n).astype(np.int64)
    delta_pmf = table[0]
    delta = rng.choice(q, size=n, p=delta_pmf).astype(np.int64)
    y = (x + delta) % q
    high_true = (x >> 5).astype(np.int64)
    low_true = (x & 31).astype(np.int64)
    return high_true, low_true, y.astype(np.int64)


def check_n(n, k1, k2, n_blocks):
    table = g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    field = GF32
    rng = np.random.default_rng([TEST_SEED_A, n])
    results = []
    for block in range(n_blocks):
        high_true, low_true, bob = sample_block(rng, n, table)
        d1 = np.sort(rng.choice(n, size=min(k1, n), replace=False)).astype(np.int64)
        d2 = np.sort(rng.choice(n, size=min(k2, n), replace=False)).astype(np.int64)
        u1_true = polar_transform(high_true, field=field, alpha=ALPHA)
        u2_true = polar_transform(low_true, field=field, alpha=ALPHA)
        val1 = u1_true[d1]
        val2 = u2_true[d2]
        labels_true = (low_true + two_layer_mod.LABEL_SCALE * high_true).astype(np.int64)
        crc_true = scl_joint.labels_crc16(labels_true)

        ref = two_layer_mod.run_two_layer_block(
            block, high_true, low_true, bob, field=field,
            p1_table=p1, p2_table=p2, d1=d1, d2=d2, n=n, k1=len(d1), k2=len(d2),
        )
        got = scl_joint.scl_joint_decode(
            bob, crc_true, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
            list_width_L=1, top_m=1,
        )
        ok = (
            got.high_hat.tolist() == ref.operational.high_hat.tolist()
            and got.low_hat.tolist() == ref.operational.low_hat.tolist()
        )
        results.append(ok)
    return results


if __name__ == "__main__":
    for (n, k1, k2, blocks) in [(64, 5, 20, 20), (256, 5, 20, 20)]:
        res = check_n(n, k1, k2, blocks)
        first4 = res[:4]
        print(f"N={n} k1={k1} k2={k2}: first4_blocks_ok={all(first4)} detail_first4={first4}")
        print(f"  full {blocks}-block detail: {res}")
