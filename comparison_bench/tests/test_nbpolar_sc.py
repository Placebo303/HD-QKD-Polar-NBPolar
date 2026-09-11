"""Focused Phase 2 tests: reference q-ary SC vs independent exhaustive oracle.

Synthetic tiny/deterministic metrics only. No Model-F, no real data, no
file output, no performance claim. Written without a pytest dependency
so it runs under plain ``python`` and is still collected by pytest
elsewhere: every ``test_*`` function takes no arguments and uses plain
asserts plus a local ``assert_raises`` helper.

Tolerances are absolute maxima: probabilities within 1e-12, finite log
scores within 1e-9, exact-zero support matched exactly, no NaN.
"""

from __future__ import annotations

import itertools
import re
import sys
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    SCResult,
    make_gf2m,
    make_gf32,
    oracle_block_log_score,
    oracle_sc_metric,
    polar_transform,
    sc_decode,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import oracle as oracle_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import sc as sc_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import transform as tmod

RNG_SEED = 20260911
PROB_TOL = 1e-12
LOG_TOL = 1e-9

EVIDENCE = {
    "oracle_max_prob_err": 0.0,
    "oracle_max_log_err": 0.0,
    "oracle_support_mismatches": 0,
    "oracle_comparisons": 0,
    "loopback_exact": 0,
    "loopback_total": 0,
    "n64_times": {},
}


def assert_raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__} from {fn.__name__}{args}")


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def normalize_rows(mat):
    """Logsumexp normalization (packet input contract); keeps -inf support."""
    mat = np.asarray(mat, dtype=np.float64)
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(mat, axis=1, keepdims=True)
    return mat - lse


def check_oracle_row(prod_row, logp, prefix, field, alpha=2):
    ora = oracle_sc_metric(logp, prefix, field=field, alpha=alpha)
    prob_err, log_err, support = oracle_mod.compare_sc_vectors(
        prod_row, ora, n=np.asarray(logp).shape[0],
        coordinate=len(prefix), prefix=list(prefix),
        prob_tol=PROB_TOL, log_tol=LOG_TOL,
    )
    EVIDENCE["oracle_max_prob_err"] = max(EVIDENCE["oracle_max_prob_err"], prob_err)
    EVIDENCE["oracle_max_log_err"] = max(EVIDENCE["oracle_max_log_err"], log_err)
    EVIDENCE["oracle_support_mismatches"] += support
    EVIDENCE["oracle_comparisons"] += 1
    return ora


def gf4_metrics():
    rng = np.random.default_rng(RNG_SEED)
    asym = normalize_rows(rng.normal(0, 1.5, size=(4, 4)))
    uni = normalize_rows(np.zeros((4, 4)))
    one = np.full((4, 4), -np.inf)
    one[(0, 1, 2, 3), (2, 0, 3, 1)] = 0.0
    zero = rng.normal(0, 1.0, size=(4, 4))
    zero[zero < zero.max(axis=1, keepdims=True) - 1.0] = -np.inf
    zero = normalize_rows(zero)
    for j in range(4):
        if not np.isfinite(zero[j]).any():
            fix = np.full(4, -np.inf)
            fix[j % 4] = 0.0
            zero[j] = fix
    skew = normalize_rows(np.array([[-0.1, -3.0, -3.0, -3.0]] * 4))
    return {"asymmetric": asym, "uniform": uni, "one_hot": one, "zero_support": zero, "skewed": skew}


# --- P2-T0-01: surface and side-effect discipline ------------------------------

def test_package_surface_and_result_shape():
    import comparison_bench.src.comparison_bench.formal_ir.nbpolar as pkg

    # Phase 3 expands the surface; Phase 2 names must remain present.
    # ponytail: subset check keeps Phase 2 regression green across phases.
    assert {
        "make_gf2m", "make_gf32", "validate_symbols", "kernel_pair",
        "polar_transform", "polar_transform_reference", "transform_and_select",
        "sc_decode", "SCResult", "oracle_sc_metric", "oracle_block_log_score",
    } <= set(pkg.__all__)
    f4 = make_gf2m(2, 7)
    res = sc_decode(np.zeros((2, 4)), field=f4)
    assert isinstance(res, SCResult) and res.status == "ok"
    assert res.u_hat.shape == (2,) and res.x_hat.shape == (2,)
    assert res.decision_metrics.shape == (2, 4) and res.decision_log_scores.shape == (2,)
    assert res.known_count == 0 and res.known_mask.tolist() == [False, False]
    assert not hasattr(res, "final_beliefs") and not hasattr(res, "APP")
    assert res.metric_provenance["log_base"] == "natural"
    assert "prior" in res.metric_provenance["input_role"]
    assert "suffix marginalized" in res.metric_provenance["row_role"]


# --- P2-T0-02: metric validation and normalization -----------------------------

def test_metric_validation_and_normalization():
    f4 = make_gf2m(2, 7)
    f32 = make_gf32()
    good = normalize_rows(np.array([[-1.0, -2.0, -3.0, -4.0]] * 4))
    res = sc_decode(good, field=f4)
    assert np.max(np.abs(np.logaddexp.reduce(res.decision_metrics, axis=1))) <= 1e-12
    # unnormalized finite rows are explicitly normalized, not rejected
    res2 = sc_decode(np.array([[-1.0, -2.0, -3.0, -4.0]] * 4), field=f4)
    assert np.array_equal(res2.u_hat, res.u_hat)
    # exact-zero support preserved, never uniform-filled
    one = np.full((4, 4), -np.inf)
    one[:, 1] = 0.0
    res3 = sc_decode(one, field=f4)
    assert res3.x_hat.tolist() == [1, 1, 1, 1]
    assert res3.u_hat.tolist() == polar_transform([1, 1, 1, 1], field=f4).tolist()
    # integer dtype is convertible
    res4 = sc_decode(np.zeros((2, 4), dtype=np.int64), field=f4)
    assert res4.u_hat.shape == (2,)
    # invalid rows fail clearly
    bad_nan = good.copy()
    bad_nan[0, 0] = np.nan
    assert_raises_match(ValueError, "metric contract", sc_decode, bad_nan, field=f4)
    bad_inf = good.copy()
    bad_inf[1, 1] = np.inf
    assert_raises_match(ValueError, "metric contract", sc_decode, bad_inf, field=f4)
    bad_empty = np.full((4, 4), -np.inf)
    assert_raises_match(ValueError, "metric contract", sc_decode, bad_empty, field=f4)
    assert_raises_match(TypeError, "metric contract", sc_decode, np.zeros((4, 4), dtype=bool), field=f4)
    assert_raises_match(ValueError, "metric contract", sc_decode, np.zeros((4, 4, 1)), field=f4)
    assert_raises_match(ValueError, "metric contract", sc_decode, np.zeros(4), field=f4)
    # q/N consistency and field/shape contract
    assert_raises_match(ValueError, "field/shape contract", sc_decode, np.zeros((4, 32)), field=f4)
    assert_raises_match(ValueError, "field/shape contract", sc_decode, np.zeros((3, 4)), field=f4)
    assert_raises_match(ValueError, "field/shape contract", sc_decode, np.zeros((2, 4)), field=f32)
    assert_raises_match(ValueError, "field/shape contract", sc_decode, np.zeros((2, 4)), field=f4, alpha=99)


# --- P2-T1-01: local minus/plus vs direct double-loop definition ---------------

def direct_minus(l0, l1, field, alpha, q):
    a = field.add(alpha, 0)
    out = np.empty(q)
    for u in range(q):
        acc = -np.inf
        for v in range(q):
            acc = np.logaddexp(acc, l0[field.add(u, field.mul(a, v))] + l1[v])
        out[u] = acc
    top = out[np.isfinite(out)].max(initial=-np.inf)
    return out if top == -np.inf else out - np.logaddexp.reduce(out)


def direct_plus(l0, l1, beta, field, alpha, q):
    a = field.add(alpha, 0)
    out = np.array([l0[field.add(beta, field.mul(a, v))] + l1[v] for v in range(q)])
    return out if not np.isfinite(out).any() else out - np.logaddexp.reduce(out)


def check_pair_against_direct(l0, l1, field, alpha, q, betas):
    index = sc_mod._combination_index(field, alpha, q)
    m0 = sc_mod._minus_block(l0[None, :], l1[None, :], index)[0]
    ref = direct_minus(l0, l1, field, alpha, q)
    assert m0.shape == (q,) and ref.shape == (q,)
    assert not np.isnan(m0).any() and not np.isnan(ref).any()
    assert np.array_equal(np.isfinite(m0), np.isfinite(ref))
    assert np.max(np.abs(np.exp(m0) - np.exp(ref))) <= PROB_TOL
    both = np.isfinite(m0) & np.isfinite(ref)
    if np.any(both):
        assert np.max(np.abs(m0[both] - ref[both])) <= LOG_TOL
    for beta in betas:
        p0 = sc_mod._plus_block(l0[None, :], l1[None, :], np.array([beta]), index)[0]
        pr = direct_plus(l0, l1, beta, field, alpha, q)
        assert not np.isnan(p0).any() and np.array_equal(np.isfinite(p0), np.isfinite(pr))
        assert np.max(np.abs(np.exp(p0) - np.exp(pr))) <= PROB_TOL
        both = np.isfinite(p0) & np.isfinite(pr)
        if np.any(both):
            assert np.max(np.abs(p0[both] - pr[both])) <= LOG_TOL


def test_minus_plus_against_direct_definition():
    f4 = make_gf2m(2, 7)
    grid = [0.0, -1.0, -2.0]
    vecs = [np.array(v, dtype=np.float64) for v in itertools.product(grid, repeat=4)]
    count = 0
    for l0, l1 in itertools.product(vecs, repeat=2):
        check_pair_against_direct(l0, l1, f4, 2, 4, range(4))
        count += 1
    assert count == 81 * 81
    # exact-zero support variants (deterministic masks)
    masks = [(0,), (1,), (0, 2), (3,), (0, 1, 2)]
    for mask in masks:
        l0 = np.array([0.0, -0.5, -1.0, -1.5])
        l1 = np.array([-0.25, -1.25, -0.75, -2.0])
        l0[list(mask)] = -np.inf
        l1[list(mask)] = -np.inf
        if not np.isfinite(l0).any() or not np.isfinite(l1).any():
            continue
        check_pair_against_direct(l0, l1, f4, 2, 4, range(4))
    # GF32 deterministic representative pairs including -inf
    f32 = make_gf32()
    rng = np.random.default_rng(RNG_SEED)
    pairs = [
        (rng.normal(0, 1.0, size=32), np.zeros(32)),
        (np.full(32, -np.inf), rng.normal(0, 1.0, size=32)),
        (rng.normal(0, 2.0, size=32), rng.normal(0, 2.0, size=32)),
        (np.full(32, -1.0), np.full(32, -2.0)),
    ]
    pairs[1][0][5] = 0.0
    pairs[2][0][pairs[2][0] < -0.5] = -np.inf
    pairs[2][1][pairs[2][1] < -0.5] = -np.inf
    assert np.isfinite(pairs[1][0]).any() and np.isfinite(pairs[2][0]).any()
    for l0, l1 in pairs:
        check_pair_against_direct(np.asarray(l0), np.asarray(l1), f32, 2, 32, (0, 1, 17, 31))


# --- P2-T1-02: exhaustive SC conditional comparison ----------------------------

def decode_and_check_all_rows(logp, known_pos, known_val, field, alpha=2):
    res = sc_decode(logp, field=field, alpha=alpha,
                    known_positions=known_pos, known_values=known_val)
    n = np.asarray(logp).shape[0]
    assert res.decision_metrics.shape == (n, field.q)
    for i in range(n):
        check_oracle_row(res.decision_metrics[i], logp, res.u_hat[:i], field, alpha)
    assert np.array_equal(res.x_hat, polar_transform(res.u_hat, field=field, alpha=alpha))
    return res


def test_sc_matches_oracle_gf4_n2():
    f4 = make_gf2m(2, 7)
    patterns = [
        np.array([[0.0, -1.0, -2.0, -3.0], [-0.5, -0.5, -2.0, -2.0]]),
        np.zeros((2, 4)),
        np.array([[0.0, -np.inf, -np.inf, -np.inf], [-1.0, -0.5, -2.0, -1.5]]),
        np.array([[-0.25, -1.0, -0.5, -2.0], [-2.0, 0.0, -1.0, -1.0]]),
    ]
    for logp in patterns:
        finite = bool(np.isfinite(logp).all())
        res = decode_and_check_all_rows(logp, None, None, f4)
        decode_and_check_all_rows(logp, [1], [int(res.u_hat[1])], f4)
        decode_and_check_all_rows(logp, [0, 1], [int(v) for v in res.u_hat], f4)
        if finite:
            flipped = (int(res.u_hat[0]) + 1) % 4
            r2 = decode_and_check_all_rows(logp, [0], [flipped], f4)
            assert r2.u_hat[0] == flipped
            zero_forced = decode_and_check_all_rows(logp, [0], [0], f4)
            assert zero_forced.u_hat[0] == 0


def test_sc_matches_oracle_gf4_n4():
    f4 = make_gf2m(2, 7)
    metrics = gf4_metrics()
    rng = np.random.default_rng(RNG_SEED + 1)
    metrics["rng_a"] = normalize_rows(rng.normal(0, 1.2, size=(4, 4)))
    metrics["rng_b"] = normalize_rows(rng.normal(1.0, 2.0, size=(4, 4)))
    for name, logp in sorted(metrics.items()):
        finite = bool(np.isfinite(logp).all())
        res = decode_and_check_all_rows(logp, None, None, f4)
        dec = [int(v) for v in res.u_hat]
        decode_and_check_all_rows(logp, [0, 2], [dec[0], dec[2]], f4)
        decode_and_check_all_rows(logp, [1, 3, 0], [dec[1], dec[3], dec[0]], f4)
        decode_and_check_all_rows(logp, [0, 1, 2, 3], dec, f4)
        if finite:
            flipped = (dec[0] + 2) % 4
            r2 = decode_and_check_all_rows(logp, [0], [flipped], f4)
            assert r2.u_hat[0] == flipped
            decode_and_check_all_rows(logp, [2], [0], f4)


def test_sc_matches_oracle_gf32_n2():
    f32 = make_gf32()
    rng = np.random.default_rng(RNG_SEED + 2)
    raw_zero = rng.normal(0, 1.0, size=(2, 32))
    raw_zero[raw_zero < raw_zero.max(axis=1, keepdims=True) - 1.5] = -np.inf
    metrics = {
        "asymmetric": normalize_rows(rng.normal(0, 1.5, size=(2, 32))),
        "uniform": np.zeros((2, 32)),
        "one_hot": np.where(np.arange(64).reshape(2, 32) % 32 == np.array([[7], [19]]), 0.0, -np.inf),
        "zero_support": normalize_rows(raw_zero),
    }
    for name, logp in sorted(metrics.items()):
        finite = bool(np.isfinite(logp).all())
        res = decode_and_check_all_rows(logp, None, None, f32)
        dec = [int(v) for v in res.u_hat]
        decode_and_check_all_rows(logp, [1], [dec[1]], f32)
        decode_and_check_all_rows(logp, [0, 1], dec, f32)
        if finite:
            flipped = (dec[0] + 5) % 32
            r2 = decode_and_check_all_rows(logp, [0], [flipped], f32)
            assert r2.u_hat[0] == flipped


# --- P2-T1-03: partial-sum discriminator ---------------------------------------

DISC_METRIC = [
    [-1.0, -2.0, -3.0, -3.0],
    [-2.0, 0.0, -1.0, -1.0],
    [-2.0, -2.0, -3.0, -2.0],
    [-1.0, 0.0, -2.0, -2.0],
]


def test_partial_sum_discriminator():
    f4 = make_gf2m(2, 7)
    res = sc_decode(DISC_METRIC, field=f4)
    assert res.u_hat.tolist() == [0, 3, 1, 1]
    assert res.x_hat.tolist() == polar_transform([0, 3, 1, 1], field=f4).tolist()
    u_left = res.u_hat[:2]
    beta = polar_transform(u_left, field=f4)
    assert beta.tolist() == [1, 3] and u_left.tolist() == [0, 3]  # transform differs from raw
    assert not np.array_equal(beta, u_left)
    ora_u2 = check_oracle_row(res.decision_metrics[2], DISC_METRIC, u_left, f4)
    assert int(np.argmax(ora_u2)) == 1  # oracle-correct MAP symbol at U_2
    # wrong implementation: raw left-U decisions as plus conditioning
    index = sc_mod._combination_index(f4, 2, 4)
    logp = sc_mod._normalize_rows(np.asarray(DISC_METRIC, dtype=np.float64))
    wrong_in = sc_mod._plus_block(logp[:2], logp[2:], u_left, index)
    gathered = wrong_in[0][index] + wrong_in[1][None, :]
    w = np.logaddexp.reduce(gathered, axis=1)
    wrong_u2 = w - np.logaddexp.reduce(w)
    prob_err = float(np.max(np.abs(np.exp(wrong_u2) - np.exp(ora_u2))))
    assert prob_err > 1e-6, prob_err
    assert int(np.argmax(wrong_u2)) != int(np.argmax(ora_u2))
    assert_raises(AssertionError, oracle_mod.compare_sc_vectors,
                  wrong_u2, ora_u2, n=4, coordinate=2, prefix=[0, 3])


# --- P2-T1-04: known-symbol semantics ------------------------------------------

def test_known_symbol_semantics():
    f4 = make_gf2m(2, 7)
    rng = np.random.default_rng(RNG_SEED + 3)
    logp = normalize_rows(rng.normal(0, 1.5, size=(4, 4)))
    plain = sc_decode(logp, field=f4)
    # empty, sparse, interleaved, all-known
    assert sc_decode(logp, field=f4, known_positions=[], known_values=[]).u_hat.tolist() == plain.u_hat.tolist()
    dec = [int(v) for v in plain.u_hat]
    sparse = sc_decode(logp, field=f4, known_positions=[2], known_values=[dec[2]])
    assert sparse.u_hat.tolist() == dec and sparse.known_count == 1
    assert sparse.known_mask.tolist() == [False, False, True, False]
    inter = sc_decode(logp, field=f4, known_positions=[3, 0], known_values=[dec[3], dec[0]])
    assert inter.u_hat.tolist() == dec and inter.known_count == 2
    full = sc_decode(logp, field=f4, known_positions=[0, 1, 2, 3], known_values=dec)
    assert full.u_hat.tolist() == dec and full.known_count == 4
    assert full.known_mask.tolist() == [True, True, True, True]
    # input coordinate order is irrelevant (explicit position mapping)
    shuf = sc_decode(logp, field=f4, known_positions=[2, 0], known_values=[dec[2], dec[0]])
    assert shuf.u_hat.tolist() == dec
    # known zero is selected as zero even when it is not MAP
    forced_zero = sc_decode(logp, field=f4, known_positions=[1], known_values=[0])
    assert forced_zero.u_hat[1] == 0
    assert forced_zero.decision_log_scores[1] == float(forced_zero.decision_metrics[1, 0])
    # known non-MAP value is forced and its conditional still matches the oracle
    nonmap = (dec[1] + 1) % 4
    assert nonmap != dec[1]
    rnm = sc_decode(logp, field=f4, known_positions=[1], known_values=[nonmap])
    assert rnm.u_hat[1] == nonmap
    check_oracle_row(rnm.decision_metrics[2], logp, rnm.u_hat[:2], f4)
    # a later known coordinate does not alter earlier classic-SC conditionals
    late = sc_decode(logp, field=f4, known_positions=[2, 3], known_values=[dec[2], dec[3]])
    assert np.array_equal(late.decision_metrics[:2], plain.decision_metrics[:2])
    # malformed known inputs fail clearly
    assert_raises_match(ValueError, "known-coordinate contract", sc_decode, logp, field=f4,
                        known_positions=[1, 1], known_values=[0, 1])
    assert_raises_match(ValueError, "known-coordinate contract", sc_decode, logp, field=f4,
                        known_positions=[4], known_values=[0])
    assert_raises_match(ValueError, "known-coordinate contract", sc_decode, logp, field=f4,
                        known_positions=[-1], known_values=[0])
    assert_raises_match(ValueError, "known-coordinate contract", sc_decode, logp, field=f4,
                        known_positions=[0], known_values=[4])
    assert_raises_match(ValueError, "known-coordinate contract", sc_decode, logp, field=f4,
                        known_positions=[0], known_values=[-1])
    assert_raises_match(ValueError, "known-coordinate contract", sc_decode, logp, field=f4,
                        known_positions=[0, 1], known_values=[0])
    assert_raises_match(ValueError, "known-coordinate contract", sc_decode, logp, field=f4,
                        known_positions=[0], known_values=None)
    assert_raises_match(TypeError, "known-coordinate contract", sc_decode, logp, field=f4,
                        known_positions=[0.0], known_values=[0])
    assert_raises_match(TypeError, "known-coordinate contract", sc_decode, logp, field=f4,
                        known_positions=[True], known_values=[0])


# --- P2-T1-05: noiseless loopback ----------------------------------------------

def check_loopback(u_true, field, patterns):
    x_true = polar_transform(np.asarray(u_true), field=field)
    n, q = len(u_true), field.q
    one = np.full((n, q), -np.inf)
    one[np.arange(n), np.asarray(x_true)] = 0.0
    for name, (pos, val) in patterns(x_true, u_true).items():
        res = sc_decode(one, field=field, known_positions=pos, known_values=val)
        assert res.u_hat.tolist() == list(u_true), (name, res.u_hat.tolist(), list(u_true))
        assert res.x_hat.tolist() == list(x_true), name
        EVIDENCE["loopback_exact"] += 1
        EVIDENCE["loopback_total"] += 1


def std_patterns(x_true, u_true):
    n = len(u_true)
    even = [i for i in range(n) if i % 2 == 0]
    return {
        "none": ([], []),
        "partial": (even, [int(u_true[i]) for i in even]),
        "all": (list(range(n)), [int(v) for v in u_true]),
    }


def test_noiseless_loopback_gf4_n4_exhaustive():
    f4 = make_gf2m(2, 7)
    for tup in itertools.product(range(4), repeat=4):
        check_loopback(list(tup), f4, std_patterns)
    assert EVIDENCE["loopback_total"] >= 256 * 3


def test_noiseless_loopback_gf32():
    f32 = make_gf32()
    rng = np.random.default_rng(RNG_SEED + 4)
    for n, trials in ((2, 8), (4, 6), (8, 4), (64, 3)):
        for _ in range(trials):
            check_loopback(rng.integers(0, 32, size=n).tolist(), f32, std_patterns)


def test_n1_identity():
    for field in (make_gf2m(2, 7), make_gf32()):
        q = field.q
        row = normalize_rows(np.arange(q, dtype=np.float64)[None, :])
        res = sc_decode(row, field=field)
        assert res.u_hat.tolist() == [q - 1] and res.x_hat.tolist() == [q - 1]
        check_oracle_row(res.decision_metrics[0], row, [], field)
        forced = sc_decode(row, field=field, known_positions=[0], known_values=[0])
        assert forced.u_hat.tolist() == [0]


# --- P2-T1-06: nontrivial correction evidence -----------------------------------

CORR_METRIC = [
    [-1.5, -1.5, -1.5, 0.5],
    [-1.5, -1.5, 0.5, -1.5],
    [-1.5, -1.5, 0.5, -1.5],
    [-1.0, -1.0, -1.0, 0.5],
]
CORR_U_TRUE = [0, 0, 0, 1]
CORR_X_TRUE = [3, 2, 2, 1]


def test_nontrivial_correction():
    f4 = make_gf2m(2, 7)
    assert polar_transform(CORR_U_TRUE, field=f4).tolist() == CORR_X_TRUE
    x_map = [int(np.argmax(np.asarray(CORR_METRIC)[j])) for j in range(4)]
    assert x_map == [3, 2, 2, 3] and x_map != CORR_X_TRUE  # independent X MAP errs at row 3
    plain = sc_decode(CORR_METRIC, field=f4)
    assert plain.u_hat.tolist() == [1, 3, 3, 3]  # undisclosed SC echoes the wrong MAP
    assert plain.u_hat.tolist() != CORR_U_TRUE
    fixed = sc_decode(CORR_METRIC, field=f4, known_positions=[0], known_values=[0])
    assert fixed.u_hat.tolist() == CORR_U_TRUE  # one disclosed U coordinate recovers the block
    assert fixed.x_hat.tolist() == CORR_X_TRUE
    check_oracle_row(fixed.decision_metrics[1], CORR_METRIC, fixed.u_hat[:1], f4)


# --- P2-T1-07: surprisal-chain identity ----------------------------------------

def test_surprisal_chain_identity():
    f4 = make_gf2m(2, 7)
    f32 = make_gf32()
    rng = np.random.default_rng(RNG_SEED + 5)
    cases = [
        (f4, [1, 0, 3, 2], normalize_rows(rng.normal(0, 1.0, size=(4, 4)))),
        (f4, [3, 3, 3, 3], normalize_rows(rng.normal(-0.5, 1.5, size=(4, 4)))),
        (f32, [7, 19], normalize_rows(rng.normal(0, 1.0, size=(2, 32)))),
    ]
    for field, u_true, logp in cases:
        chain = 0.0
        for i in range(len(u_true)):
            row = oracle_sc_metric(logp, u_true[:i], field=field)
            assert np.isfinite(row[u_true[i]])
            chain += float(row[u_true[i]])
        block = oracle_block_log_score(logp, u_true, field=field)
        assert abs(chain - block) <= 1e-9, (chain, block)
    # exact-zero impossible case: one-hot metric contradicted by the forced prefix
    one = np.full((4, 4), -np.inf)
    one[np.arange(4), [0, 0, 0, 0]] = 0.0
    bad_prefix = [1, 1]
    rows = [oracle_sc_metric(one, bad_prefix[:i], field=f4) for i in range(3)]
    assert not np.isfinite(rows[2]).any()
    assert_raises(sc_mod.ImpossibleDisclosedValueError, sc_decode, one, field=f4,
                  known_positions=[0, 1, 2, 3], known_values=[1, 1, 0, 0])


# --- P2-T1-08: deterministic failure attribution --------------------------------

def test_failure_attribution():
    f4 = make_gf2m(2, 7)
    good = normalize_rows(rng_matrix())
    # metric contract
    assert_raises_match(ValueError, "metric contract", sc_decode, good + np.nan, field=f4)
    # field/shape contract
    assert_raises_match(ValueError, "field/shape contract", sc_decode, good, field="not-a-field")
    assert_raises_match(ValueError, "field/shape contract", sc_decode, good, field=f4, alpha=True)
    # known-coordinate contract
    assert_raises_match(ValueError, "known-coordinate contract", sc_decode, good, field=f4,
                        known_positions=[[0]], known_values=[0])
    # impossible disclosed value is stable and distinct
    one = np.full((2, 4), -np.inf)
    one[np.arange(2), [0, 0]] = 0.0
    assert_raises_match(sc_mod.ImpossibleDisclosedValueError, "impossible disclosed value",
                        sc_decode, one, field=f4, known_positions=[0], known_values=[1])
    # numeric nonfinite failure is raised by internal normalization, never masked
    assert_raises_match(sc_mod.NumericNonfiniteError, "numeric nonfinite failure",
                        sc_mod._normalize_rows, np.full((2, 3), np.nan))
    untouched = sc_mod._normalize_rows(np.full((1, 3), -np.inf))
    assert np.array_equal(untouched, np.full((1, 3), -np.inf))  # all--inf kept for leaf attribution


def rng_matrix():
    return np.random.default_rng(RNG_SEED + 6).normal(0, 1.0, size=(4, 4))


# --- P2-T1-09: forbidden coupling audit ----------------------------------------

def test_forbidden_coupling_audit():
    pkg = Path(tmod.__file__).parent
    pattern = re.compile(
        r"LDPC|PEG|QC|BP|Cascade|\bPW\b|BSC|LLR|CRC|SCL|Model-F|TTBin|polar_existing|IRRunResult"
    )
    hits = []
    for name in ("__init__.py", "sc.py", "oracle.py"):
        for lineno, line in enumerate((pkg / name).read_text().splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{name}:{lineno}:{line}")
    assert hits == [], hits
    assert "final_beliefs" not in (pkg / "sc.py").read_text()
    assert "APP" not in (pkg / "sc.py").read_text()
    assert "APP" not in (pkg / "oracle.py").read_text()
    # oracle is independent of production SC internals
    source = (pkg / "oracle.py").read_text()
    assert "from .sc import" not in source and "from comparison_bench" not in source
    assert "_minus_block" not in source and "_plus_block" not in source


# --- P2-T1-10: bounded resource sanity -----------------------------------------

def test_bounded_resource_sanity():
    f32 = make_gf32()
    rng = np.random.default_rng(RNG_SEED + 7)
    n = 64
    u = rng.integers(0, 32, size=n)
    x = polar_transform(u, field=f32)
    one = np.full((n, 32), -np.inf)
    one[np.arange(n), x] = 0.0
    start = time.perf_counter()
    res = sc_decode(one, field=f32)
    EVIDENCE["n64_times"]["noiseless"] = time.perf_counter() - start
    assert res.u_hat.tolist() == u.tolist() and res.x_hat.tolist() == x.tolist()
    assert res.decision_metrics.shape == (n, 32)
    soft = normalize_rows(rng.normal(0, 1.0, size=(n, 32)))
    start = time.perf_counter()
    res2 = sc_decode(soft, field=f32)
    EVIDENCE["n64_times"]["asymmetric"] = time.perf_counter() - start
    assert res2.decision_metrics.shape == (n, 32)
    assert np.max(np.abs(np.logaddexp.reduce(res2.decision_metrics, axis=1))) <= 1e-12
    for name, spent in EVIDENCE["n64_times"].items():
        assert spent < 30.0, (name, spent)


# --- plain-python runner -------------------------------------------------------

def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        start = time.perf_counter()
        fn()
        print(f"PASS {fn.__name__} ({time.perf_counter() - start:.2f}s)")
    print(f"{len(tests)} passed")
    print(f"oracle comparisons: {EVIDENCE['oracle_comparisons']}, "
          f"max_prob_err={EVIDENCE['oracle_max_prob_err']:.3e}, "
          f"max_log_err={EVIDENCE['oracle_max_log_err']:.3e}, "
          f"support_mismatches={EVIDENCE['oracle_support_mismatches']}")
    print(f"loopback exact: {EVIDENCE['loopback_exact']}/{EVIDENCE['loopback_total']}")
    print(f"n64 times: {EVIDENCE['n64_times']}")


if __name__ == "__main__":
    main()
