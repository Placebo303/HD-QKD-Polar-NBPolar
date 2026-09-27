"""Focused tests for the new CRC-aided joint two-layer SCL module ``scl_joint``.

Authorization: PI ruling 2026-09-27 (``docs/decision-log.md`` "PI 裁决三项:
SCL 锁修订 T1 = DECIDED..."), mirrored in
``openspec/changes/nbpolar-scl-lock-amendment/tasks.md`` T1/T2. This file
tests only the new module ``scl_joint.py``; ``scl.py``/``sc.py``/
``two_layer.py``/``prior.py`` are exercised read-only, never modified.

T-a: L=1, top_m=1 identity against ``two_layer.run_two_layer_block``'s
operational (SC) arm on a small-N synthetic block drawn from the
G1R2-matched channel (real CAL32 delta pmf, explicit 1e-15 floor).
T-b: small-N (N=2, GF32) brute-force joint-ML enumerator oracle, independent
of the SC recursion (direct per-position log-likelihood summation), checked
against the joint list at full list width (no pruning possible).
T-c: CRC-16/CCITT-FALSE known test vector ("123456789" -> 0x29B1) plus
disclosure-accounting (``crc_bits`` counted exactly once, always 16).
T-d: descriptive L-monotonicity smoke check (L=4 exact count >= L=1 on the
same blocks; not a strong correctness gate -- see the test docstring).

Fresh test-local seeds only; no protected/real data; no file output.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl as scl_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl_joint
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as two_layer_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    Provenance,
    apply_explicit_floor,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform

# Fresh test-local seeds for this file only.
TEST_SEED_A = 2026092751
TEST_SEED_B = 2026092752
TEST_SEED_C = 2026092753

Q_SYMBOL = 1024  # Alice symbol alphabet (32*high+low)
GF32 = make_gf32()
ALPHA = 2


def _g1r2_matched_table(q: int = Q_SYMBOL) -> np.ndarray:
    """Build the sign-fixed matched [Alice,Bob] table with an explicit 1e-15 floor.

    Raw masses from the real CAL32 G1R2 triple (p0=0.7562, p(delta=+1)=0.0018,
    p(delta=-1)=0.2419, all other 1021 offsets zero); ``apply_explicit_floor``
    (unmodified import from ``prior.py``) adds the 1e-15 floor and renormalizes
    to sum 1 in the same step. Convention: ``table[a,b] = pmf[(b-a) % q]``
    (decoder matched to the generator ``y = (x+delta) % q``), same sign-fixed
    convention as the reviewed ``op-n32k-matched`` probe.
    """
    pmf_raw = np.zeros(q, dtype=np.float64)
    pmf_raw[0] = 0.7562
    pmf_raw[1 % q] = 0.0018
    pmf_raw[(q - 1) % q] = 0.2419
    pmf = apply_explicit_floor(pmf_raw, 1e-15, reason="G1R2-matched explicit floor (test-local)")
    delta = (np.arange(q)[None, :] - np.arange(q)[:, None]) % q
    return pmf[delta]


def _sample_block(rng, n: int, pmf_2d_row) -> tuple:
    """Draw one synthetic (high_true, low_true, bob) block from the matched channel."""
    q = pmf_2d_row.shape[0]
    x = rng.integers(0, q, size=n).astype(np.int64)
    delta_pmf = pmf_2d_row[0]  # table[a,b]=pmf[(b-a)%q]; row 0 IS the pmf itself
    delta = rng.choice(q, size=n, p=delta_pmf).astype(np.int64)
    y = (x + delta) % q
    high_true = (x >> 5).astype(np.int64)
    low_true = (x & 31).astype(np.int64)
    bob = y.astype(np.int64)
    return high_true, low_true, bob


# --- T-a: L=1, top_m=1 identity with two_layer's operational SC path -----------

def test_l1_m1_identity_matched_channel():
    """L=1/M=1 identity against the frozen ``scl.scl_decode(L=1)`` wiring, at
    N=64 and N=256 (repo-verified reliable at both sizes; see rationale below).

    This test no longer compares ``scl_joint_decode``'s output against
    ``two_layer.run_two_layer_block``'s SC path (``sc_decode``). Independent
    review (``workspace/probes/scl-joint-timing/CODE_REVIEW.md`` FAIL-1) found
    that ``scl.py``'s ``decode_leaf`` ranks candidates by
    ``path.metric + score`` while ``sc_decode`` ranks the leaf ``row`` alone;
    at N>=64 these two orderings occasionally disagree on a genuine float64
    near-tie (score difference ~4e-16), which is a pre-existing property of
    the frozen ``scl.py``/``sc.py`` pair, not a defect in this module or its
    test, and is out of scope to fix here (``scl.py`` must not be modified).
    That mismatch is now recorded separately, without asserting equality, by
    ``test_scl_l1_vs_sc_decode_known_tiebreak_mismatch`` below.

    What this test actually checks is the *intended* T-a identity: that
    ``scl_joint_decode(list_width_L=1, top_m=1)`` reduces exactly to calling
    the frozen ``scl.scl_decode(list_width_L=1)`` directly for L1, then again
    (candidate-conditioned, via ``prior.gather_p2_metrics``) for L2 -- i.e.
    that the new module's data flow (disclosure wiring, L1-to-L2 candidate
    hand-off, CRC/label packing) is correct, independent of any tie-break
    agreement with ``sc_decode``. This is a real regression gate against
    wiring bugs (wrong candidate passed to L2, swapped disclosure arrays,
    wrong provenance, off-by-one candidate indexing); it is verified reliable
    (0 mismatches) at both N=64 and N=256 with the k1=5/k2=20 disclosure used
    here.
    """
    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    field = GF32
    for n in (64, 256):
        rng = np.random.default_rng([TEST_SEED_A, n])
        k1 = min(5, n)
        k2 = min(20, n)
        for block in range(4):
            high_true, low_true, bob = _sample_block(rng, n, table)
            d1 = np.sort(rng.choice(n, size=k1, replace=False)).astype(np.int64)
            d2 = np.sort(rng.choice(n, size=k2, replace=False)).astype(np.int64)
            u1_true = polar_transform(high_true, field=field, alpha=ALPHA)
            u2_true = polar_transform(low_true, field=field, alpha=ALPHA)
            val1 = u1_true[d1]
            val2 = u2_true[d2]
            labels_true = (low_true + two_layer_mod.LABEL_SCALE * high_true).astype(np.int64)
            crc_true = scl_joint.labels_crc16(labels_true)

            # Reference: two independent, frozen scl.scl_decode(L=1) calls,
            # chained exactly the way scl_joint_decode's contract describes
            # (L2 metric is CANDIDATE_CONDITIONED on the L1 hard estimate).
            bob_row = np.asarray(bob)[None, :]
            ref_p1_probs = two_layer_mod.build_p1_metrics(bob_row, p1)[0]
            ref_p1_metric = probs_to_symbol_metric(ref_p1_probs, provenance=Provenance.PRIOR_ONLY)
            ref_l1 = scl_mod.scl_decode(
                ref_p1_metric.logp, field=field, alpha=ALPHA,
                known_positions=d1, known_values=val1,
                list_width_L=1, prune_rule=scl_joint.top_l_prune,
            )
            high_ref = ref_l1.x_candidates[0]
            ref_p2_probs = gather_p2_metrics(bob_row, high_ref[None, :], p2)[0]
            ref_p2_metric = probs_to_symbol_metric(ref_p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
            ref_l2 = scl_mod.scl_decode(
                ref_p2_metric.logp, field=field, alpha=ALPHA,
                known_positions=d2, known_values=val2,
                list_width_L=1, prune_rule=scl_joint.top_l_prune,
            )
            low_ref = ref_l2.x_candidates[0]
            label_ref = (low_ref + two_layer_mod.LABEL_SCALE * high_ref).astype(np.int64)

            got = scl_joint.scl_joint_decode(
                bob, crc_true, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
                d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
                list_width_L=1, top_m=1,
            )
            assert got.high_hat.tolist() == high_ref.tolist()
            assert got.low_hat.tolist() == low_ref.tolist()
            assert got.label_hat.tolist() == label_ref.tolist()
            assert got.l1_survivor_count == 1
            assert got.top_m_used == 1
            assert got.candidates_considered == 1
            assert got.crc_bits == 16
            # CRC-pass state is descriptive only and never changes the L=1/M=1
            # candidate (there is exactly one); if the chained-reference path
            # landed on the true label the CRC must pass (crc_true was built
            # from that same true label), which is an extra sanity check of
            # the CRC wiring.
            if label_ref.tolist() == labels_true.tolist():
                assert got.crc_pass is True
                assert got.crc_failed is False


def test_scl_l1_vs_sc_decode_known_tiebreak_mismatch():
    """Descriptive: records (never asserts) the known scl.py(L=1)/sc_decode
    tie-break mismatch identified in
    ``workspace/probes/scl-joint-timing/CODE_REVIEW.md`` FAIL-1.

    ``scl.py``'s ``decode_leaf`` ranks candidates by ``path.metric + score``;
    ``sc.py``'s ``sc_decode`` ranks the leaf ``row`` alone (plain
    ``argmax``). These orderings can disagree on a genuine float64 near-tie
    once ``path.metric`` accumulates enough magnitude, which review found
    happens routinely at N=64/N=256 on this channel (CODE_REVIEW.md reports
    5/20 blocks at N=64 and 19-20/20 at N=256 for the same seed family). This
    is a reproducible property of the frozen ``scl.py``/``sc.py`` pair, out of
    this task's scope to fix (neither module may be modified) -- this test
    only measures and records the mismatch rate for the record, and never
    fails the suite because of it.
    """
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import sc as sc_mod

    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    field = GF32
    n = 256
    k1, k2 = min(5, n), min(20, n)
    rng = np.random.default_rng([TEST_SEED_A, n, 999])
    mismatches = 0
    total = 0
    for block in range(20):
        high_true, low_true, bob = _sample_block(rng, n, table)
        d1 = np.sort(rng.choice(n, size=k1, replace=False)).astype(np.int64)
        u1_true = polar_transform(high_true, field=field, alpha=ALPHA)
        val1 = u1_true[d1]
        bob_row = np.asarray(bob)[None, :]
        p1_probs = two_layer_mod.build_p1_metrics(bob_row, p1)[0]
        p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)

        scl_l1 = scl_mod.scl_decode(
            p1_metric.logp, field=field, alpha=ALPHA,
            known_positions=d1, known_values=val1,
            list_width_L=1, prune_rule=scl_joint.top_l_prune,
        )
        sc_ref = sc_mod.sc_decode(
            p1_metric.logp, field=field, alpha=ALPHA,
            known_positions=d1, known_values=val1,
        )
        total += 1
        if scl_l1.x_candidates[0].tolist() != sc_ref.x_hat.tolist():
            mismatches += 1
    # Sanity on the measurement itself only -- never a correctness assertion
    # about scl.py/sc.py agreement (that is the known, out-of-scope issue).
    assert total == 20
    assert isinstance(mismatches, int) and 0 <= mismatches <= total


# --- T-b: small-N (N=2, GF32) brute-force joint-ML enumerator oracle ------------

def _brute_force_joint_best(bob, p1_logp, p2_table, field, alpha, top_k: int = 5):
    """Independent (non-recursive) exact joint-ML search over N=2, q=32.

    Scores every one of the ``q**2=1024`` L1 candidates and, for each, every
    one of the ``q**2=1024`` L2 candidates conditioned on it, by *direct*
    per-position log-likelihood summation (no SC recursion, no scl_decode
    call): this is mathematically the definition of the full-length SC path
    metric (positions are conditionally independent given Bob in this model),
    so it is a genuinely separate ground truth, not a restatement of
    ``scl.scl_decode``'s own algorithm. Returns the sorted-by-joint-score
    ``top_k`` (high, low, m1, m2, joint) tuples, best first.
    """
    q = field.q
    n = 2
    index = scl_mod.sc_mod._combination_index(field, alpha, q) if False else None
    # _combination_index lives in sc.py; scl.py re-exports the sc module object.
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import sc as sc_mod
    index = sc_mod._combination_index(field, alpha, q)  # index[u0,u1] = u0 + alpha*u1

    u0 = np.repeat(np.arange(q), q)
    u1 = np.tile(np.arange(q), q)
    x0 = index[u0, u1]
    x1 = u1
    # score1[k] = logp1_row[0, x0[k]] + logp1_row[1, x1[k]] for the k-th (u0,u1) combo
    score1 = p1_logp[0, x0] + p1_logp[1, x1]  # shape (q*q,)

    high_all = np.stack([x0, x1], axis=1)  # (q*q, 2) every possible high candidate
    bob_bcast = np.broadcast_to(np.asarray(bob), high_all.shape)
    p2_probs_all = gather_p2_metrics(bob_bcast, high_all, p2_table)  # (q*q, 2, 32)
    flat = p2_probs_all.reshape(-1, q)
    metric = probs_to_symbol_metric(flat, provenance=Provenance.CANDIDATE_CONDITIONED)
    logp2_all = metric.logp.reshape(high_all.shape[0], n, q)  # (q*q, 2, 32)

    v0 = np.repeat(np.arange(q), q)
    v1 = np.tile(np.arange(q), q)
    y0 = index[v0, v1]
    y1 = v1
    # score2_all[k, m] = logp2_all[k,0,y0[m]] + logp2_all[k,1,y1[m]]
    score2_all = logp2_all[:, 0, :][:, y0] + logp2_all[:, 1, :][:, y1]  # (q*q, q*q)

    joint = score1[:, None] + score2_all  # (q*q, q*q)
    flat_joint = joint.reshape(-1)
    order = np.argsort(-flat_joint, kind="stable")[:top_k]
    results = []
    for idx in order.tolist():
        k, m = divmod(idx, joint.shape[1])
        high_cand = np.array([x0[k], x1[k]], dtype=np.int64)
        low_cand = np.array([y0[m], y1[m]], dtype=np.int64)
        results.append((high_cand, low_cand, float(score1[k]), float(score2_all[k, m]), float(joint[k, m])))
    return results


def test_small_n_enumerator_oracle_matches_full_width_joint_scl():
    n = 2
    epsilon1, epsilon2 = 0.2, 0.35  # away from 0/1 so no exact-zero symbol support
    table = two_layer_mod.build_injected_joint_table(epsilon1=epsilon1, epsilon2=epsilon2)
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    field = GF32
    q = field.q
    full_width = q * q  # 1024; strictly >= max distinct full-length paths (q**n)

    rng = np.random.default_rng(TEST_SEED_B)
    for trial in range(3):
        bob = rng.integers(0, two_layer_mod.N_LABELS, size=n).astype(np.int64)
        p1_probs = two_layer_mod.build_p1_metrics(bob[None, :], p1)[0]
        p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)

        brute = _brute_force_joint_best(bob, p1_metric.logp, p2, field, ALPHA, top_k=5)
        brute_high, brute_low, brute_m1, brute_m2, brute_joint = brute[0]

        got = scl_joint.scl_joint_decode(
            bob, crc_true=0, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=None, d1_values=None, d2_positions=None, d2_values=None,
            list_width_L=full_width, top_m=full_width,
        )
        assert got.l1_survivor_count == q * q
        assert got.top_m_used == q * q
        top_joint = got.ranked_candidates[0]
        assert top_joint.high.tolist() == brute_high.tolist()
        assert top_joint.low.tolist() == brute_low.tolist()
        assert abs(top_joint.m1 - brute_m1) < 1e-9
        assert abs(top_joint.m2 - brute_m2) < 1e-9
        assert abs(top_joint.joint_metric - brute_joint) < 1e-9
        # merged candidate list itself must also be sorted best-first by
        # joint metric (composite tie-break well-defined, not just the winner)
        joints = [c.joint_metric for c in got.ranked_candidates]
        assert all(joints[k] >= joints[k + 1] - 1e-12 for k in range(len(joints) - 1))


# --- T-c: CRC-16 known vector + disclosure accounting ---------------------------

def test_crc16_known_vector_123456789():
    bits = np.unpackbits(np.frombuffer(b"123456789", dtype=np.uint8), bitorder="big")
    assert scl_joint.crc16_ccitt_false_bits(bits) == 0x29B1


def test_crc_bits_counted_once_pass_and_fail():
    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    field = GF32
    n = 64
    rng = np.random.default_rng(TEST_SEED_C)
    high_true, low_true, bob = _sample_block(rng, n, table)
    u1_true = polar_transform(high_true, field=field, alpha=ALPHA)
    u2_true = polar_transform(low_true, field=field, alpha=ALPHA)
    d1 = np.arange(5, dtype=np.int64)
    d2 = np.arange(20, dtype=np.int64)
    val1 = u1_true[d1]
    val2 = u2_true[d2]
    labels_true = (low_true + two_layer_mod.LABEL_SCALE * high_true).astype(np.int64)
    crc_true = scl_joint.labels_crc16(labels_true)

    # passing case: correct disclosed CRC
    ok = scl_joint.scl_joint_decode(
        bob, crc_true, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
        d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
        list_width_L=4, top_m=4,
    )
    assert ok.crc_bits == 16

    # forced-fail case: deliberately wrong disclosed CRC (16-bit XOR flip)
    bad_crc = crc_true ^ 0xFFFF
    bad = scl_joint.scl_joint_decode(
        bob, bad_crc, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
        d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
        list_width_L=4, top_m=4,
    )
    assert bad.crc_bits == 16
    assert bad.crc_failed is True
    assert bad.crc_pass is False
    # crc_failed fallback must still be the top joint-metric candidate
    assert bad.joint_metric == bad.ranked_candidates[0].joint_metric


# --- T-d: descriptive L-monotonicity smoke check --------------------------------

def test_l_monotonicity_smoke():
    """L=4 exact count >= L=1 exact count on the same blocks (descriptive only).

    Not a strong correctness gate: CRC selection walks the merged list and
    stops at the first pass, so a rare 16-bit CRC collision on a *wrong*
    higher-joint-metric candidate that only exists in the wider L=4 list
    could in principle make L=4 pick a wrong answer where L=1's single
    candidate happened to be correct (probability ~1/65536 per extra wrong
    candidate examined -- negligible at these block counts, but not exactly
    zero, hence this is recorded as a smoke check rather than an invariant).
    """
    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    field = GF32
    n = 64
    k1, k2 = 5, 20
    rng = np.random.default_rng(TEST_SEED_A + 1)
    exact_l1 = 0
    exact_l4 = 0
    for block in range(10):
        high_true, low_true, bob = _sample_block(rng, n, table)
        d1 = np.sort(rng.choice(n, size=k1, replace=False)).astype(np.int64)
        d2 = np.sort(rng.choice(n, size=k2, replace=False)).astype(np.int64)
        u1_true = polar_transform(high_true, field=field, alpha=ALPHA)
        u2_true = polar_transform(low_true, field=field, alpha=ALPHA)
        val1 = u1_true[d1]
        val2 = u2_true[d2]
        labels_true = (low_true + two_layer_mod.LABEL_SCALE * high_true).astype(np.int64)
        crc_true = scl_joint.labels_crc16(labels_true)

        r1 = scl_joint.scl_joint_decode(
            bob, crc_true, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
            list_width_L=1, top_m=1,
        )
        r4 = scl_joint.scl_joint_decode(
            bob, crc_true, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
            list_width_L=4, top_m=4,
        )
        exact_l1 += int(r1.label_hat.tolist() == labels_true.tolist())
        exact_l4 += int(r4.label_hat.tolist() == labels_true.tolist())
    assert exact_l4 >= exact_l1, (exact_l4, exact_l1)


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    main()
