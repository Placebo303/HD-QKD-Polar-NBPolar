"""Reviewer scratch (read-only): isolate whether the T-a block-2 mismatch is
caused by scl_joint.py's own logic, or purely by sc_decode vs scl_decode(L=1)
disagreeing on the identical L2 metric array (the claimed pre-existing scl.py
float64 tie-break property). Feeds the SAME p2 logp array + SAME disclosures
into both decoders directly and diffs the leaf position where they choose
differently, printing the raw row scores at that position.
"""
import sys

sys.path.insert(0, r"D:\Code\HD-QKD_Polar_Comparison-nbpolar")

import numpy as np

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl as scl_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import sc as sc_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl_joint
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as two_layer_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    Provenance, apply_explicit_floor, build_p1_metrics, gather_p2_metrics, probs_to_symbol_metric,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform

GF32 = make_gf32()
ALPHA = 2
Q = 1024
TEST_SEED_A = 2026092751
N = 64


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


def main():
    table = g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    field = GF32
    rng = np.random.default_rng([TEST_SEED_A, N])
    k1, k2 = 5, 20
    for block in range(4):
        high_true, low_true, bob = sample_block(rng, N, table)
        d1 = np.sort(rng.choice(N, size=k1, replace=False)).astype(np.int64)
        d2 = np.sort(rng.choice(N, size=k2, replace=False)).astype(np.int64)
        u1_true = polar_transform(high_true, field=field, alpha=ALPHA)
        u2_true = polar_transform(low_true, field=field, alpha=ALPHA)
        val1 = u1_true[d1]
        val2 = u2_true[d2]
        if block != 2:
            continue  # the block reported to mismatch by pytest

        # Reproduce ref's L1 (sc_decode) to get its high_hat.
        bob_row = bob[None, :]
        p1_probs = build_p1_metrics(bob_row, p1)[0]
        p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)
        sc1 = sc_mod.sc_decode(p1_metric.logp, field=field, alpha=ALPHA, known_positions=d1, known_values=val1)
        high_hat = sc1.x_hat

        scl1 = scl_mod.scl_decode(
            p1_metric.logp, field=field, alpha=ALPHA, known_positions=d1, known_values=val1,
            list_width_L=1, prune_rule=scl_joint.top_l_prune,
        )
        print("block", block, "L1 high_hat match:", high_hat.tolist() == scl1.x_candidates[0].tolist())

        # Now build the SAME L2 metric from the SAME high_hat candidate and feed
        # it to both sc_decode and scl_decode(L=1) directly.
        p2_probs = gather_p2_metrics(bob_row, high_hat[None, :], p2)[0]
        p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)

        sc2 = sc_mod.sc_decode(p2_metric.logp, field=field, alpha=ALPHA, known_positions=d2, known_values=val2)
        scl2 = scl_mod.scl_decode(
            p2_metric.logp, field=field, alpha=ALPHA, known_positions=d2, known_values=val2,
            list_width_L=1, prune_rule=scl_joint.top_l_prune,
        )
        u_sc = sc2.u_hat
        u_scl = scl2.u_candidates[0]
        print("low u_hat identical between sc_decode and scl_decode(L=1)?", u_sc.tolist() == u_scl.tolist())
        diverge_positions = np.where(u_sc != u_scl)[0]
        print("diverging U positions:", diverge_positions.tolist())
        for pos in diverge_positions.tolist():
            row = sc2.decision_metrics[pos]
            top2 = np.argsort(-row)[:2]
            print(
                f"  U[{pos}] sc_decode chose {u_sc[pos]} (row score {row[u_sc[pos]]!r}); "
                f"scl_decode(L=1) chose {u_scl[pos]} (row score {row[u_scl[pos]]!r}); "
                f"top-2 raw row symbols/scores: {[(int(s), row[s]) for s in top2]}; "
                f"raw score diff = {row[u_sc[pos]] - row[u_scl[pos]]!r}"
            )
        print()


if __name__ == "__main__":
    main()
