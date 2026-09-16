"""Focused Phase 4-P3 Stage A/A2 tests: synthetic empirical channel + tiny oracle.

Synthetic fixtures only: every table is hand-built or drawn from a frozen
P3 seed inside this file. No CAL artifact, parquet, TTBin, real frame,
DEV/EVAL, sibling read, benchmark, or file output outside temporary
directories. Written without a pytest dependency so it runs under plain
``python`` and is still collected by pytest: every ``test_*`` takes no
arguments and uses plain asserts plus a local ``assert_raises_match``.

Stage A gates P3-A01--A12 plus autonomous exploration P3-A13--A20 per
``.workbuddy/queue/NBPOLAR-PHASE4-P3-EMPIRICAL-PRIOR-SC/TASK_PACKET.md``.
Tolerances are absolute maxima (probability 1e-12, finite log 1e-9,
normalization 1e-12). Full 5-rep N=2..1024 medians live in
``EXPLORATION_NOTES.md`` (profiling run); the pytest A18 entry below is
a bounded no-crash/shape smoke so the suite stays fast.
"""

from __future__ import annotations

import inspect
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    construction as construction_mod,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    empirical_channel as ech,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    empirical_diagnostic as ediag,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    empirical_oracle as eor,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    oracle as phase2_oracle,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    prior as prior_mod,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    sc as sc_mod,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
    make_gf2m,
    make_gf32,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    probs_to_symbol_metric,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc import sc_decode
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
    polar_transform,
    polar_transform_reference,
)

PROB_TOL = 1e-12
LOG_TOL = 1e-9
NORM_TOL = 1e-12

# Preregistered absolute tolerances for the A02 unit sanity (fixed large
# sample; generator sanity only, never evidence).
A02_N = 40000
A02_BOB_TOL = 0.01
A02_COND_TOL = 0.02

EVIDENCE = {"a18_times": {}, "a19_times": {}}


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def hand_p1():
    """Asymmetric hand table (q=4, n_b=3): dense, sparse, exact-zero mix."""
    p1 = np.array([
        [0.50, 0.25, 1.00],
        [0.25, 0.25, 0.00],
        [0.125, 0.50, 0.00],
        [0.125, 0.00, 0.00],
    ])
    assert abs(p1.sum(axis=0) - 1).max() <= 1e-15
    return p1


def hand_p_b():
    return np.array([0.5, 0.3, 0.2])


# --- P3-A01: asymmetric hand table, Bob-axis gather + normalization --------

def test_a01_asymmetric_gather_and_normalization():
    p1 = hand_p1()
    bob = np.array([0, 1, 2, 0, 2, 1])
    got = ech.build_p1_metrics(bob, p1)
    assert got.shape == (6, 4)
    for j, b in enumerate(bob.tolist()):
        assert float(np.abs(got[j] - p1[:, b]).max()) == 0.0
    assert float(np.abs(got.sum(axis=1) - 1).max()) <= NORM_TOL
    batch = np.array([[0, 2], [1, 1]])
    got2 = ech.build_p1_metrics(batch, p1)
    assert got2.shape == (2, 2, 4)
    assert float(np.abs(got2[0, 1] - p1[:, 2]).max()) == 0.0
    assert float(np.abs(got2.sum(axis=2) - 1).max()) <= NORM_TOL


# --- P3-A02: generator frequency convergence (unit sanity) -----------------

def test_a02_generator_frequency_convergence():
    p_b = hand_p_b()
    p1 = hand_p1()
    rng = ech.make_rng(ech.P3_UNIT_SEED)
    bob = ech.sample_bob(rng, p_b, A02_N)
    freq = np.bincount(bob, minlength=3) / A02_N
    assert float(np.abs(freq - p_b).max()) <= A02_BOB_TOL, (freq, p_b)
    rng2 = ech.make_rng(ech.P3_UNIT_SEED + 1000)
    fixed = np.zeros(20000, dtype=np.int64)
    draws = ech.sample_high_given_bob(rng2, fixed, p1)
    cond = np.bincount(draws, minlength=4) / draws.shape[0]
    assert float(np.abs(cond - p1[:, 0]).max()) <= A02_COND_TOL, (cond, p1[:, 0])


# --- P3-A03: seed reproducibility ------------------------------------------

def test_a03_seed_reproducibility():
    p_b = hand_p_b()
    p1 = hand_p1()
    r1 = ech.make_rng(ech.P3_TRAIN_SEED)
    r2 = ech.make_rng(ech.P3_TRAIN_SEED)
    b1, a1, h1, l1 = ech.sample_full_block(r1, p_b, _full_from_p1(p1), 4, 1, 16)
    b2, a2, h2, l2 = ech.sample_full_block(r2, p_b, _full_from_p1(p1), 4, 1, 16)
    assert np.array_equal(b1, b2) and np.array_equal(a1, a2)
    assert np.array_equal(h1, h2) and np.array_equal(l1, l2)
    r3 = ech.make_rng(ech.P3_DIAG_SEED)
    b3, _, _, _ = ech.sample_full_block(r3, p_b, _full_from_p1(p1), 4, 1, 16)
    assert not np.array_equal(b1, b3), "distinct frozen seeds must differ"
    assert_raises_match(ValueError, "seed contract", ech.make_rng, 2026091200)
    assert_raises_match(ValueError, "seed contract", ech.make_rng, 2026091213)


def _full_from_p1(p1):
    """Embed a high-level table as full ``f_full`` with ``q_low=1``."""
    return np.asarray(p1, dtype=np.float64).copy()


def _to_log(probs):
    """Generic prob-row to log-row conversion: ``0 -> -inf``, rows renormed.

    Same semantics as ``prior.probs_to_symbol_metric`` but for any ``q``
    (the accepted converter pins ``q=32``); A14 proves bitwise parity at
    ``q=32`` so production always converts through the accepted helper.
    """
    mat = np.asarray(probs, dtype=np.float64)
    with np.errstate(divide="ignore"):
        logp = np.log(mat, out=np.full_like(mat, -np.inf), where=mat > 0)
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(logp, axis=1, keepdims=True)
    return logp - lse


# --- P3-A04: operational signature carries no truth -------------------------

def test_a04_operational_signature_truth_free():
    params = list(inspect.signature(ech.build_p1_metrics).parameters)
    assert params == ["bob", "p1_table"], params
    joined = " ".join(params).lower()
    for banned in ("alice", "truth", "u_true", "a_full", "high", "known"):
        assert banned not in joined, (banned, params)
    # the operational builder takes Bob + table only (signature gate above);
    # behavioral isolation under adversarial truth mutation is proved by A05
    assert callable(ech.build_p1_metrics)


# --- P3-A05: truth mutation changes neither Bob nor metric ------------------

def test_a05_truth_mutation_isolation():
    p_b = hand_p_b()
    p1 = hand_p1()
    rng = ech.make_rng(ech.P3_UNIT_SEED + 7)
    bob, a_full, high, _ = ech.sample_full_block(
        rng, p_b, _full_from_p1(p1), 4, 1, 8)
    bob_frozen = bob.copy()
    m_before = ech.build_p1_metrics(bob, p1)
    a_full[:] = (a_full + 1) % 4  # adversarial post-hoc truth mutation
    high[:] = (high + 2) % 4
    assert np.array_equal(bob, bob_frozen), "Bob must not alias mutated truth"
    m_after = ech.build_p1_metrics(bob, p1)
    assert np.array_equal(m_before, m_after), "metric must be bitwise stable"
    assert np.array_equal(m_before, ech.build_p1_metrics(bob_frozen, p1))


# --- P3-A06: empirical oracle vs direct enumeration (GF4 N=2/4) --------------

def _gf4_logp_cases():
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 21)
    cases = {}
    raw = rng.normal(0, 1.2, size=(2, 4))
    cases["n2_asym"] = raw - np.logaddexp.reduce(raw, axis=1, keepdims=True)
    one = np.full((2, 4), -np.inf)
    one[(0, 1), (1, 3)] = 0.0
    cases["n2_onehot"] = one
    raw4 = rng.normal(0, 1.0, size=(4, 4))
    raw4[raw4 < raw4.max(axis=1, keepdims=True) - 1.2] = -np.inf
    lse = np.logaddexp.reduce(np.where(np.isfinite(raw4), raw4, -np.inf),
                              axis=1, keepdims=True)
    cases["n4_zero"] = np.where(np.isfinite(raw4), raw4 - lse, -np.inf)
    rawb = rng.normal(0.5, 1.5, size=(4, 4))
    cases["n4_asym"] = rawb - np.logaddexp.reduce(rawb, axis=1, keepdims=True)
    return cases


def test_a06_oracle_agrees_direct_enumeration_gf4():
    f4 = make_gf2m(2, 7)
    for name, logp in sorted(_gf4_logp_cases().items()):
        n = logp.shape[0]
        prefixes = [[]] if n == 2 else [[], [0], [1, 2]]
        for prefix in prefixes:
            got = eor.empirical_oracle_sc_metric(logp, prefix, field=f4, alpha=2)
            ref = phase2_oracle.oracle_sc_metric(logp, prefix, field=f4, alpha=2)
            assert got.shape == ref.shape == (4,)
            assert np.array_equal(np.isfinite(got), np.isfinite(ref)), name
            assert float(np.abs(np.exp(got) - np.exp(ref)).max()) <= PROB_TOL, name
            both = np.isfinite(got) & np.isfinite(ref)
            if np.any(both):
                assert float(np.abs(got[both] - ref[both]).max()) <= LOG_TOL, name


# --- P3-A07: SC vs empirical oracle, every coordinate (GF4 N=2/4) -----------

def test_a07_sc_agrees_empirical_oracle_gf4():
    f4 = make_gf2m(2, 7)
    for name, logp in sorted(_gf4_logp_cases().items()):
        res = sc_decode(logp, field=f4, alpha=2)
        for i in range(logp.shape[0]):
            ora = eor.empirical_oracle_sc_metric(
                logp, res.u_hat[:i].tolist(), field=f4, alpha=2)
            prod = res.decision_metrics[i]
            assert np.array_equal(np.isfinite(prod), np.isfinite(ora)), (name, i)
            assert float(np.abs(np.exp(prod) - np.exp(ora)).max()) <= PROB_TOL, (name, i)
            both = np.isfinite(prod) & np.isfinite(ora)
            if np.any(both):
                assert float(np.abs(prod[both] - ora[both]).max()) <= LOG_TOL, (name, i)


# --- P3-A08: GF32 N=2 one-hot / uniform / asymmetric ------------------------

def test_a08_gf32_n2_oracle_shapes():
    f32 = make_gf32()
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 33)
    raw = rng.normal(0, 1.4, size=(2, 32))
    asym = raw - np.logaddexp.reduce(raw, axis=1, keepdims=True)
    uni = np.zeros((2, 32))
    one = np.full((2, 32), -np.inf)
    one[(0, 1), (7, 19)] = 0.0
    for name, logp in (("asymmetric", asym), ("uniform", uni), ("one_hot", one)):
        res = sc_decode(logp, field=f32, alpha=2)
        for i in range(2):
            ora = eor.empirical_oracle_sc_metric(
                logp, res.u_hat[:i].tolist(), field=f32, alpha=2)
            prod = res.decision_metrics[i]
            assert np.array_equal(np.isfinite(prod), np.isfinite(ora)), name
            assert float(np.abs(np.exp(prod) - np.exp(ora)).max()) <= PROB_TOL, name
            both = np.isfinite(prod) & np.isfinite(ora)
            if np.any(both):
                assert float(np.abs(prod[both] - ora[both]).max()) <= LOG_TOL, name


# --- P3-A09: frozen values incl. zero stay distinguishable ------------------

def test_a09_frozen_values_including_zero():
    f4 = make_gf2m(2, 7)
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 44)
    logp = rng.normal(0, 1.0, size=(4, 4))
    logp -= np.logaddexp.reduce(logp, axis=1, keepdims=True)
    res = sc_decode(logp, field=f4, alpha=2, known_positions=[1, 3],
                    known_values=[0, 0])
    assert res.u_hat[1] == 0 and res.u_hat[3] == 0
    assert res.known_count == 2
    assert res.known_mask.tolist() == [False, True, False, True]
    res2 = sc_decode(logp, field=f4, alpha=2, known_positions=[0, 2],
                     known_values=[3, 1])
    assert res2.u_hat[0] == 3 and res2.u_hat[2] == 1
    assert res2.known_mask.tolist() == [True, False, True, False]


# --- P3-A10: impossible disclosure failure category -------------------------

def test_a10_impossible_disclosure_category():
    f4 = make_gf2m(2, 7)
    one = np.full((2, 4), -np.inf)
    one[np.arange(2), [0, 0]] = 0.0
    assert_raises_match(sc_mod.ImpossibleDisclosedValueError,
                        "impossible disclosed value", sc_decode, one, field=f4,
                        known_positions=[0], known_values=[1])
    # same trigger through a sampled one-hot metric: still impossible, never silent
    assert_raises_match(sc_mod.ImpossibleDisclosedValueError,
                        "impossible disclosed value", sc_decode, one, field=f4,
                        known_positions=[0, 1], known_values=[1, 1])


# --- P3-A11: oracle isolation from package surface and operators ------------

def test_a11_oracle_not_exported_or_imported():
    import comparison_bench.src.comparison_bench.formal_ir.nbpolar as pkg

    assert "empirical_oracle" not in pkg.__all__
    assert "empirical_block_score" not in pkg.__all__
    assert "empirical_oracle_sc_metric" not in pkg.__all__
    assert not hasattr(pkg, "empirical_oracle_sc_metric")
    ch_src = Path(ech.__file__).read_text(encoding="utf-8")
    assert "empirical_oracle" not in ch_src
    assert "oracle_sc_metric" not in ch_src
    sc_src = Path(sc_mod.__file__).read_text(encoding="utf-8")
    assert "empirical_oracle" not in sc_src
    or_src = Path(eor.__file__).read_text(encoding="utf-8")
    assert "from .sc import" not in or_src
    assert "from .oracle import" not in or_src
    assert "_minus_block" not in or_src and "_plus_block" not in or_src


# --- P3-A12: no sibling-content markers in new modules/tests ----------------

def test_a12_no_sibling_access_markers():
    # Access indicators (paths, raw-format suffixes, pickle loaders), not
    # prose: docstrings may name the forbidden classes, but no file may
    # open, load, or path-reference sibling content. Markers are built
    # from parts so this self-scan cannot match its own literals.
    _AC = "workspace" + chr(47)
    _DR = "D:" + chr(47)
    _DB = "D:" + chr(92)
    _PQ = ".par" + "quet"
    _TB = ".tt" + "bin"
    _PK = "allow" + "_pickle"
    _NL = "np" + ".lo" + "ad"
    _ART = "v72p2" + "d5"
    markers = (_AC, _DR, _DB, _PQ, _TB, _PK, _NL, _ART)
    import comparison_bench.src.comparison_bench.formal_ir.nbpolar as pkg

    paths = [ech.__file__, eor.__file__,
             str(Path(pkg.__file__).parent / "empirical_diagnostic.py"), __file__]
    for path in paths:
        src = Path(path).read_text(encoding="utf-8")
        for mark in markers:
            assert mark not in src, (path, mark)


# --- P3-A13: dual-path likelihood over >=100 asymmetric cases ----------------

def _dual_path_case_tables(rng):
    kinds = []
    for _ in range(28):  # dense asymmetric
        raw = rng.random((4, 5)) + 0.05
        kinds.append(("dense", raw / raw.sum(axis=0, keepdims=True)))
    for _ in range(24):  # sparse with exact zeros
        raw = rng.random((4, 5)) + 0.05
        mask = rng.random((4, 5)) < 0.35
        raw[mask] = 0.0
        raw[0, :] = np.where(raw[:, :].sum(axis=0) == 0, 1.0, raw[0, :])
        col = raw.sum(axis=0, keepdims=True)
        col[col == 0] = 1.0
        kinds.append(("sparse", raw / col))
    for _ in range(24):  # one-hot columns
        mat = np.zeros((4, 5))
        mat[rng.integers(0, 4, size=5), np.arange(5)] = 1.0
        kinds.append(("one_hot", mat))
    for _ in range(24):  # single surviving symbol per row-block + uniform col
        raw = rng.random((4, 5)) + 0.1
        raw[1:, 0] = 0.0
        raw[:, 1] = 0.25
        col = raw.sum(axis=0, keepdims=True)
        kinds.append(("mixed", raw / col))
    return kinds  # 100 cases


def test_a13_dual_path_likelihood_100_cases():
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 55)
    cases = _dual_path_case_tables(rng)
    assert len(cases) >= 100
    worst = 0.0
    mism = 0
    kinds_seen = set()
    for kind, p1 in cases:
        kinds_seen.add(kind)
        for shape in ((7,), (3, 7)):
            bob = rng.integers(0, 5, size=shape)
            vec = ech.build_p1_metrics(bob, p1)
            lit = ech.build_p1_metrics_literal(bob, p1)
            assert vec.shape == lit.shape, (kind, shape)
            worst = max(worst, float(np.abs(vec - lit).max()))
            mism += int(np.sum(np.isfinite(vec) != np.isfinite(lit)))
    assert kinds_seen == {"dense", "sparse", "one_hot", "mixed"}, kinds_seen
    assert worst <= PROB_TOL, worst
    assert mism == 0, mism


# --- P3-A14: probability vs log representation ------------------------------

def test_a14_probability_log_representation():
    p1 = hand_p1()
    bob = np.array([0, 1, 2, 0])
    probs = ech.build_p1_metrics(bob, p1)
    assert float(np.abs(probs.sum(axis=1) - 1).max()) <= NORM_TOL
    logp = _to_log(probs)
    assert float(np.abs(np.logaddexp.reduce(logp, axis=1)).max()) <= 1e-9
    back = np.exp(logp)
    pos = probs > 0
    assert float(np.abs(back[pos] - probs[pos]).max()) <= PROB_TOL
    zero = probs == 0
    assert zero.any() and bool((logp[zero] == -np.inf).all())
    # production parity: generic conversion equals the accepted q=32
    # converter, so operational code always converts through it
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 58)
    raw = rng.random((5, 32))
    raw[rng.random((5, 32)) < 0.2] = 0.0
    raw /= raw.sum(axis=1, keepdims=True)
    mine = _to_log(raw)
    theirs = probs_to_symbol_metric(raw).logp
    assert np.array_equal(np.isfinite(mine), np.isfinite(theirs))
    both = np.isfinite(mine) & np.isfinite(theirs)
    assert float(np.abs(mine[both] - theirs[both]).max()) <= 1e-15
    # canonical ownership: SC consumes log rows; adapter owns conversion
    sig = inspect.signature(sc_decode)
    assert "logp_x" in sig.parameters
    assert logp.dtype == np.float64


# --- P3-A15: numerical stress ------------------------------------------------

def test_a15_numerical_stress():
    floor_row = np.full(32, 1e-300)
    floor_row[0] = 1.0
    floor_row /= floor_row.sum()
    concentrated = np.full(32, 1e-12)
    concentrated[5] = 1.0
    concentrated /= concentrated.sum()
    uniform = np.full(32, 1.0 / 32)
    one = np.zeros(32)
    one[17] = 1.0
    half = np.zeros(32)
    half[::2] = 1.0 / 16
    probs = np.stack([floor_row, concentrated, uniform, one, half, floor_row])
    metric = probs_to_symbol_metric(probs)
    assert not np.isnan(metric.logp).any()
    assert not np.isposinf(metric.logp).any()
    assert bool(((metric.logp == -np.inf) == (probs == 0)).all())
    f32 = make_gf32()
    res = sc_decode(metric.logp[:2], field=f32, alpha=2)
    assert res.decision_metrics.shape == (2, 32)
    # scaling any likelihood row by a positive constant keeps the decision
    logp = metric.logp[:2].copy()
    scaled = logp + np.array([[3.0], [-7.5]])
    res2 = sc_decode(scaled, field=f32, alpha=2)
    assert res.u_hat.tolist() == res2.u_hat.tolist()
    scaled_probs = probs[:2] * np.array([[2.5], [0.01]])
    scaled_probs /= scaled_probs.sum(axis=1, keepdims=True)
    res3 = sc_decode(probs_to_symbol_metric(scaled_probs).logp,
                     field=f32, alpha=2)
    assert res.u_hat.tolist() == res3.u_hat.tolist()


# --- P3-A16: transform/interface metamorphism --------------------------------

def test_a16_transform_interface_metamorphism():
    f4 = make_gf2m(2, 7)
    f32 = make_gf32()
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 66)
    for field, ns in ((f4, (2, 4, 8)), (f32, (2,))):
        for n in ns:
            vec = rng.integers(0, field.q, size=n)
            assert np.array_equal(
                polar_transform(vec, field=field, alpha=2),
                polar_transform_reference(vec, field=field, alpha=2))
    # gather permutation equivariance (Bob-axis interface morphism)
    p1 = rng.random((4, 6)) + 0.1
    p1 /= p1.sum(axis=0, keepdims=True)
    bob = rng.integers(0, 6, size=(3, 8))
    perm_f = [2, 0, 1]
    perm_p = [7, 3, 0, 5, 1, 6, 2, 4]
    m = ech.build_p1_metrics(bob, p1)
    assert np.array_equal(m[perm_f][:, perm_p],
                          ech.build_p1_metrics(bob[perm_f][:, perm_p], p1))
    # disclosed-coordinate input order is irrelevant
    logp = rng.normal(0, 1.0, size=(4, 4))
    logp -= np.logaddexp.reduce(logp, axis=1, keepdims=True)
    dec = sc_decode(logp, field=f4, alpha=2).u_hat.tolist()
    r1 = sc_decode(logp, field=f4, alpha=2, known_positions=[3, 0],
                   known_values=[dec[3], dec[0]])
    r2 = sc_decode(logp, field=f4, alpha=2, known_positions=[0, 3],
                   known_values=[dec[0], dec[3]])
    assert r1.u_hat.tolist() == r2.u_hat.tolist() == dec


# --- P3-A17: failure taxonomy -------------------------------------------------

def test_a17_failure_taxonomy():
    f4 = make_gf2m(2, 7)
    p1 = hand_p1()
    good = ech.build_p1_metrics(np.array([0, 1]), p1)
    # impossible disclosure -> its own stable category
    one = np.full((2, 4), -np.inf)
    one[np.arange(2), [0, 0]] = 0.0
    assert_raises_match(sc_mod.ImpossibleDisclosedValueError,
                        "impossible disclosed value", sc_decode, one, field=f4,
                        known_positions=[1], known_values=[2])
    # malformed table normalization -> channel contract, never a decode count
    bad = p1.copy()
    bad[:, 0] *= 2.0
    assert_raises_match(ValueError, "channel contract",
                        ech.build_p1_metrics, np.array([0]), bad)
    # invalid symbol / wrong shape / nonfinite input -> fail-loud contracts
    assert_raises_match(ValueError, "channel contract",
                        ech.build_p1_metrics, np.array([99]), p1)
    assert_raises_match(ValueError, "channel contract",
                        ech.build_p1_metrics, np.zeros((2, 2, 2)), p1)
    nan_p1 = p1.copy()
    nan_p1[0, 0] = np.nan
    assert_raises_match(ValueError, "channel contract",
                        ech.build_p1_metrics, np.array([0]), nan_p1)
    nan_log = _to_log(good).copy()
    nan_log[0, 0] = np.nan
    assert_raises_match(ValueError, "metric contract",
                        sc_decode, nan_log, field=f4)
    assert_raises_match(ValueError, "known-coordinate contract",
                        sc_decode, good, field=f4,
                        known_positions=[0, 0], known_values=[0, 1])
    # sampling guards
    assert_raises_match(TypeError, "channel contract",
                        ech.sample_bob, "not-a-generator", hand_p_b(), 4)


# --- P3-A18: bounded complexity smoke (full medians in EXPLORATION_NOTES) -----

def _median_of(fn, reps: int) -> float:
    fn()
    spans = []
    for _ in range(reps):
        start = time.perf_counter()
        fn()
        spans.append(time.perf_counter() - start)
    return float(np.median(np.asarray(spans)))


def test_a18_complexity_smoke_metric_sc_separated():
    f32 = make_gf32()
    rng = np.random.default_rng(ech.P3_DIAG_SEED)
    raw = rng.random((32, 64)) + 0.1
    p1 = raw / raw.sum(axis=0, keepdims=True)
    for n in (2, 4, 8, 16, 64, 256, 1024):
        bob = rng.integers(0, 64, size=n)
        probs = ech.build_p1_metrics(bob, p1)
        assert probs.shape == (n, 32)
        reps = 5 if n <= 64 else 2  # bounded smoke; full 5-rep medians profiled aside
        tm = _median_of(lambda: ech.build_p1_metrics(bob, p1), reps)
        logp = probs_to_symbol_metric(probs).logp
        td = _median_of(lambda: sc_decode(logp, field=f32, alpha=2), reps)
        EVIDENCE["a18_times"][n] = (tm, td)
        res = sc_decode(logp, field=f32, alpha=2)
        assert res.decision_metrics.shape == (n, 32)
        assert not np.isnan(res.decision_metrics).any()


# --- P3-A19: vectorized vs literal selection ----------------------------------

def test_a19_implementation_comparison_record():
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 77)
    raw = rng.random((32, 16)) + 0.1
    p1 = raw / raw.sum(axis=0, keepdims=True)
    bob = rng.integers(0, 16, size=256)
    vec = ech.build_p1_metrics(bob, p1)
    lit = ech.build_p1_metrics_literal(bob, p1)
    assert float(np.abs(vec - lit).max()) <= PROB_TOL
    tv = _median_of(lambda: ech.build_p1_metrics(bob, p1), 5)
    tl = _median_of(lambda: ech.build_p1_metrics_literal(bob, p1), 5)
    EVIDENCE["a19_times"] = {"vectorized": tv, "literal": tl}
    src = inspect.getsource(ech.build_p1_metrics)
    assert "for a in range" not in src, "operational path must stay vectorized"
    lit_src = inspect.getsource(ech.build_p1_metrics_literal)
    assert "for a in range" in lit_src and "for j, b in enumerate" in lit_src


# --- P3-A20: regression isolation via temp-dir diagnostic ---------------------

def test_a20_temp_dir_diagnostic_isolation():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        empirical_diagnostic as ediag,
    )

    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "synth_diag")
        payload = ediag.run_synthetic_diagnostic(
            q=4, n=4, n_b=6, seed=ech.P3_DIAG_SEED, n_blocks=4, out=out)
        assert payload["support_mismatches"] == 0
        assert payload["max_prob_err"] <= PROB_TOL
        assert (Path(out) / "synthetic_summary.json").is_file()
        assert (Path(out) / "report.md").is_file()
        # guards: banned seed and existing root refuse without side effects
        assert_raises_match(ValueError, "seed contract",
                            ediag.run_synthetic_diagnostic,
                            q=4, n=4, n_b=6, seed=2026091201, n_blocks=1,
                            out=str(Path(tmp) / "refused_seed"))
        assert_raises_match(FileExistsError, "refuse to overwrite",
                            ediag.run_synthetic_diagnostic,
                            q=4, n=4, n_b=6, seed=ech.P3_DIAG_SEED, n_blocks=1,
                            out=out)
        # artifact mode refuses a missing temp root with the artifact
        # contract prefix -- never touching the sibling root
        assert_raises_match(ValueError, "artifact contract",
                            ediag.run_artifact_diagnostic,
                            npz_path=str(Path(tmp) / "model_f_input.npz"),
                            summary_path=str(Path(tmp) / "model_f_input_summary.json"),
                            seed=ech.P3_DIAG_SEED, n=2, n_blocks=1,
                            out=str(Path(tmp) / "refused_artifact"))


# --- packing: miniature split/combine + production parity ---------------------

def test_packing_miniature_and_production_parity():
    for q_low, trials in ((2, 4), (32, 1024)):
        rng = np.random.default_rng(ech.P3_UNIT_SEED + 88)
        full = rng.integers(0, trials, size=64)
        low, high = ech.split_labels(full, q_low)
        assert np.array_equal(ech.combine_labels(low, high, q_low), full)
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 89)
    for s in rng.integers(0, 1024, size=32).tolist():
        low, high = ech.split_labels(np.int64(s), 32)
        plow, phigh = prior_mod.split_symbol(int(s))
        assert (int(low), int(high)) == (plow, phigh), s
        assert int(ech.combine_labels(
            np.array([plow]), np.array([phigh]), 32)[0]) == int(s)


def test_derive_p1_from_full_matches_literal():
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 93)
    raw = rng.random((6, 5)) + 0.1
    f_full = raw / raw.sum(axis=0, keepdims=True)
    got = ech.derive_p1_from_full(f_full, 3, 2)
    assert got.shape == (3, 5)
    for hi in range(3):
        for b in range(5):
            want = f_full[hi * 2, b] + f_full[hi * 2 + 1, b]
            assert abs(float(got[hi, b]) - want) <= 1e-15, (hi, b)
    assert float(np.abs(got.sum(axis=0) - 1).max()) <= NORM_TOL


def test_gather_matches_accepted_prior_at_production_shape():
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 94)
    raw = rng.random((32, 1024)) + 0.1
    p1 = raw / raw.sum(axis=0, keepdims=True)
    bob = rng.integers(0, 1024, size=(3, 16))
    mine = ech.build_p1_metrics(bob, p1)
    theirs = prior_mod.build_p1_metrics(bob, p1)
    assert mine.shape == theirs.shape == (3, 16, 32)
    assert float(np.abs(mine - theirs).max()) == 0.0


# --- Stage B: vectorized oracle backend + frozen runner ---------------------

def test_sb_masks_m1_m5_positions_and_values():
    for n in (16, 64, 256):
        masks = ediag.stageb_masks(n)
        assert list(masks) == list(ediag.STAGEB_MASK_NAMES)
        assert masks["M1_all_but_one"].tolist() == list(range(n - 1))
        assert masks["M2_prefix"].tolist() == list(range(n // 2))
        assert masks["M3_suffix"].tolist() == list(range(n // 2, n))
        assert masks["M4_alternating"].tolist() == list(range(0, n, 2))
        assert np.array_equal(
            masks["M5_construction_order"],
            construction_mod.analytic_order(0.05, n)[: n // 2])
        assert masks["M1_all_but_one"].size == n - 1
        assert masks["M2_prefix"].size == n // 2
        assert masks["M3_suffix"].size == n // 2
        assert masks["M4_alternating"].size == n // 2
        for name, pos in masks.items():
            assert pos.dtype == np.int64, name
            assert len(set(pos.tolist())) == pos.size, name
            assert int(pos.min()) >= 0 and int(pos.max()) < n, name
    # disclosed values are the true U at the mask positions and are kept
    f32 = make_gf32()
    n = 16
    rng = ech.make_rng(ech.P3_UNIT_SEED + 201)
    raw = rng.random((32, 6)) + 0.05
    p1 = raw / raw.sum(axis=0, keepdims=True)
    p_b = np.full(6, 1.0 / 6)
    bob = ech.sample_bob(rng, p_b, n)
    high = ech.sample_high_given_bob(rng, bob, p1)
    u_true = polar_transform(high, field=f32, alpha=2)
    logp = probs_to_symbol_metric(ech.build_p1_metrics(bob, p1)).logp
    for name, pos in ediag.stageb_masks(n).items():
        res = sc_decode(logp, field=f32, alpha=2,
                        known_positions=pos, known_values=u_true[pos])
        assert res.known_count == pos.size, name
        assert np.array_equal(res.u_hat[pos], u_true[pos]), name


def _gf32_logp_cases():
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 202)
    cases = {}
    raw = rng.normal(0, 1.4, size=(2, 32))
    cases["n2_asym"] = raw - np.logaddexp.reduce(raw, axis=1, keepdims=True)
    cases["n2_uniform"] = np.zeros((2, 32))
    one = np.full((2, 32), -np.inf)
    one[(0, 1), (7, 19)] = 0.0
    cases["n2_one_hot"] = one
    raw4 = rng.normal(0, 1.0, size=(4, 32))
    raw4[raw4 < raw4.max(axis=1, keepdims=True) - 1.5] = -np.inf
    lse = np.logaddexp.reduce(np.where(np.isfinite(raw4), raw4, -np.inf),
                              axis=1, keepdims=True)
    cases["n4_zero"] = np.where(np.isfinite(raw4), raw4 - lse, -np.inf)
    return cases


def _assert_oracle_parity(got, ref, label):
    assert got.shape == ref.shape, label
    assert np.array_equal(np.isfinite(got), np.isfinite(ref)), label
    assert float(np.abs(np.exp(got) - np.exp(ref)).max()) <= PROB_TOL, label
    both = np.isfinite(got) & np.isfinite(ref)
    if both.any():
        assert float(np.abs(got[both] - ref[both]).max()) <= LOG_TOL, label


def test_sb_oracle_vectorized_matches_literal():
    f4 = make_gf2m(2, 7)
    f32 = make_gf32()
    # GF4 N=2/4: every prefix length is cheap in the literal backend
    for name, logp in sorted(_gf4_logp_cases().items()):
        n = logp.shape[0]
        prefixes = ([[], [0], [1], [3]] if n == 2
                    else [[], [2], [1, 3], [0, 2, 1]])
        for prefix in prefixes:
            ref = eor.empirical_oracle_sc_metric(logp, prefix, field=f4)
            got = eor.empirical_oracle_sc_metric_vectorized(logp, prefix, field=f4)
            _assert_oracle_parity(got, ref, (name, prefix))
    # GF32 N=2: one-hot / uniform / asymmetric
    for name, logp in sorted(_gf32_logp_cases().items()):
        if logp.shape[0] != 2:
            continue
        for prefix in ([], [7], [19]):
            ref = eor.empirical_oracle_sc_metric(logp, prefix, field=f32)
            got = eor.empirical_oracle_sc_metric_vectorized(logp, prefix, field=f32)
            _assert_oracle_parity(got, ref, (name, prefix))
    # GF32 N=4: literal parity at prefixes of length >= 2 (the literal path
    # needs the explicit vector cap opt-in outside its 4096 default domain)
    logp4 = _gf32_logp_cases()["n4_zero"]
    for prefix in ([5, 9], [31, 0, 17]):
        ref = eor.empirical_oracle_sc_metric(
            logp4, prefix, field=f32,
            max_candidates=eor.MAX_VECTOR_ORACLE_CANDIDATES)
        got = eor.empirical_oracle_sc_metric_vectorized(logp4, prefix, field=f32)
        _assert_oracle_parity(got, ref, ("gf32_n4", prefix))
    # batch API equals the single-prefix wrapper on shared nested prefixes
    chain_prefixes = [[], [3], [3, 12], [3, 12, 1]]
    chain = eor.empirical_oracle_conditionals_vectorized(
        logp4, chain_prefixes, field=f32)
    for row, prefix in enumerate(chain_prefixes):
        single = eor.empirical_oracle_sc_metric_vectorized(logp4, prefix, field=f32)
        assert np.array_equal(chain[row], single), prefix


def test_sb_oracle_exact_zero_and_all_inf_handling():
    f4 = make_gf2m(2, 7)
    f32 = make_gf32()
    # exact-zero support stays distinguishable from finite support
    logp = _gf32_logp_cases()["n4_zero"]
    ref = eor.empirical_oracle_sc_metric(
        logp, [2, 5], field=f32,
        max_candidates=eor.MAX_VECTOR_ORACLE_CANDIDATES)
    got = eor.empirical_oracle_sc_metric_vectorized(logp, [2, 5], field=f32)
    assert np.array_equal(np.isneginf(ref), np.isneginf(got))
    # an all--inf input row is rejected by both backends
    bad = np.zeros((2, 32))
    bad[0] = -np.inf
    assert_raises_match(ValueError, "every logp_x row needs finite support",
                        eor.empirical_oracle_sc_metric, bad, [], field=f32)
    assert_raises_match(ValueError, "every logp_x row needs finite support",
                        eor.empirical_oracle_conditionals_vectorized, bad, [[]],
                        field=f32)
    # an impossible prefix yields the same all--inf aggregate in both backends
    one = np.full((2, 4), -np.inf)
    one[0, 0] = 0.0
    one[1, 0] = 0.0
    ref = eor.empirical_oracle_sc_metric(one, [2], field=f4)
    got = eor.empirical_oracle_sc_metric_vectorized(one, [2], field=f4)
    assert bool((ref == -np.inf).all()) and np.array_equal(ref, got)
    # uniform rows: analytic 1/q conditionals at N=2 and N=4
    uni2 = eor.empirical_oracle_sc_metric_vectorized(
        np.zeros((2, 32)), [], field=f32)
    assert float(np.abs(np.exp(uni2) - 1.0 / 32).max()) <= PROB_TOL
    uni4 = eor.empirical_oracle_sc_metric_vectorized(
        np.zeros((4, 32)), [], field=f32)
    assert float(np.abs(np.exp(uni4) - 1.0 / 32).max()) <= PROB_TOL


def test_sb_batch_transform_matches_reference():
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 203)
    for field in (make_gf2m(2, 7), make_gf32()):
        for n in (2, 4, 8):
            vecs = rng.integers(0, field.q, size=(6, n))
            got = eor.batch_polar_transform_reference(vecs, field=field)
            assert got.shape == (6, n)
            for row in range(vecs.shape[0]):
                ref = polar_transform_reference(vecs[row], field=field, alpha=2)
                assert np.array_equal(got[row], ref), (field.q, n, row)
    # the default literal oracle cap is unchanged for existing callers
    assert eor.MAX_ORACLE_CANDIDATES == 4096
    assert eor.MAX_VECTOR_ORACLE_CANDIDATES == 1 << 20


def test_sb_stageb_refusal_paths():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        npz = root / "model_f_input.npz"
        summary = root / "model_f_input_summary.json"
        existing = root / "existing"
        existing.mkdir()
        assert_raises_match(
            FileExistsError, "refuse to overwrite",
            ediag.run_stageb_diagnostic, npz_path=str(npz),
            summary_path=str(summary), seed=ediag.STAGEB_SEED,
            out=str(existing))
        banned_out = root / "banned_seed_out"
        assert_raises_match(
            ValueError, "seed contract", ediag.run_stageb_diagnostic,
            npz_path=str(npz), summary_path=str(summary), seed=2026091200,
            out=str(banned_out))
        assert not banned_out.exists(), "banned seed must not create the root"
        missing_out = root / "missing_artifact_out"
        assert_raises_match(
            ValueError, "artifact contract", ediag.run_stageb_diagnostic,
            npz_path=str(npz), summary_path=str(summary),
            seed=ediag.STAGEB_SEED, out=str(missing_out))
        assert not missing_out.exists(), "failed load must not create the root"


def _stageb_injected_tables(n_b=8):
    rng = np.random.default_rng(ech.P3_UNIT_SEED + 204)
    raw = rng.random((32, n_b)) + 0.05
    p1 = raw / raw.sum(axis=0, keepdims=True)
    p_b = rng.random(n_b) + 0.2
    return p_b / p_b.sum(), p1


def _stageb_scored_cases(summary):
    return summary["b1"] + summary["b2"]["cases"] + summary["b3"]["cases"]


def test_sb_injected_full_matrix_smoke():
    import json

    p_b, p1 = _stageb_injected_tables()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "stageb"
        summary = ediag._run_stageb_from_tables(
            rng=ech.make_rng(ech.P3_DIAG_SEED), p_b=p_b, p1=p1,
            seed=ech.P3_DIAG_SEED, out=str(out))
        assert sorted(p.name for p in out.iterdir()) == sorted(ediag.STAGEB_OUT_FILES)
        plan = json.loads((out / "frozen_plan.json").read_text())
        assert plan["entry"] == "empirical_stageb_diagnostic"
        assert plan["artifact"]["source"] == "caller-injected tables (test seam)"
        assert plan["attempt_accounting"]["consumed_at_write"] == 0
        assert plan["out_files"] == list(ediag.STAGEB_OUT_FILES)
        assert plan["b2"]["blocks_per_mask"] == 16
        assert plan["b3"]["blocks_per_mask"] == 8
        oracle = json.loads((out / "oracle_records.json").read_text())
        assert oracle["backend"] == "empirical_oracle_conditionals_vectorized"
        assert len(oracle["b1"]) == 2
        profile = json.loads((out / "stress_and_profile.json").read_text())
        assert [rec["n"] for rec in profile["b4"]["profiles"]] == [64, 256, 1024]
        for rec in profile["b4"]["profiles"]:
            assert rec["metric_batch_shape"] == [4, rec["n"], 32]
            assert rec["metric_shape"] == [rec["n"], 32]
            assert rec["decision_shape"] == [rec["n"], 32]
        payload = json.loads((out / "diagnostic_summary.json").read_text())
        assert payload["hard_gates_pass"] is True, payload["hard_gates"]
        assert payload["truth_leak_violations"] == 0
        assert payload["resource_abort_blocks"] == 0
        assert payload["candidate_conclusion"] == "EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE"
        assert len(payload["b2"]["cases"]) == 10
        assert all(rec["n_blocks_planned"] == 16 for rec in payload["b2"]["cases"])
        assert len(payload["b3"]["cases"]) == 5
        assert all(rec["n_blocks_planned"] == 8 for rec in payload["b3"]["cases"])
        assert all(rec["n_disclosed"] == rec["n"] - 1
                   for rec in payload["b3"]["cases"]
                   if rec["mask"] == "M1_all_but_one")
        for rec in payload["b1"]:
            assert all(rec["gates"].values()), (rec["case"], rec["gates"])
            assert rec["max_prob_err"] <= PROB_TOL
            assert rec["max_log_err"] <= LOG_TOL
            assert rec["support_mismatches"] == 0
        # disjoint accounting: exact+failed==attempted per case
        for rec in _stageb_scored_cases(payload):
            assert rec["n_executed"] + rec["n_resource_abort"] == rec["n_blocks_planned"]
            assert (rec["n_exact"] + rec["n_impossible"] + rec["n_other"]
                    + rec["n_nonfinite"]) == rec["n_executed"]
            assert sum(rec["attribution"].values()) == rec["n_executed"] - rec["n_exact"]
        report = (out / "report.md").read_text()
        assert report.startswith("# P3 Stage B empirical-prior SC interface diagnostic")


def test_sb_truth_leak_sentinel_direct():
    f32 = make_gf32()
    rng = ech.make_rng(ech.P3_DIAG_SEED + 1)
    raw = rng.random((32, 5)) + 0.1
    p1 = raw / raw.sum(axis=0, keepdims=True)
    p_b = np.full(5, 0.2)
    bob = ech.sample_bob(rng, p_b, 4)
    high = ech.sample_high_given_bob(rng, bob, p1)
    probs = ech.build_p1_metrics(bob, p1)
    logp = probs_to_symbol_metric(probs).logp
    res = sc_decode(logp, field=f32, alpha=2)
    assert ediag._truth_leak_violation(
        bob=bob, high=high, p1=p1, probs=probs, res=res, field=f32) == 0
    assert ediag._truth_leak_violation(
        bob=bob, high=high, p1=p1, probs=probs * 2.0, res=res, field=f32) == 1
    tampered = sc_decode(logp, field=f32, alpha=2)
    tampered.u_hat[0] = int((tampered.u_hat[0] + 1) % 32)
    assert ediag._truth_leak_violation(
        bob=bob, high=high, p1=p1, probs=probs, res=tampered, field=f32) == 1


def test_sb_attribution_classifier_forced_categories():
    classify = ediag.classify_stageb_failure
    assert classify(outcome="other", support_failure=True) == "artifact_adapter_support"
    assert classify(outcome="other", normalization_failure=True) == "normalization"
    assert classify(outcome="impossible") == "disclosure_contradiction"
    assert classify(outcome="nonfinite") == "SC_numeric"
    assert classify(outcome="other", under_disclosure_ambiguous=True) == \
        "expected_under_disclosure"
    assert classify(outcome="other") == "SC_decision"
    assert classify(outcome="other", unclassified_error=True) == "unattributed"
    # precedence: support beats every later layer
    assert classify(outcome="impossible", support_failure=True) == \
        "artifact_adapter_support"
    assert classify(outcome="nonfinite", normalization_failure=True) == "normalization"
    for not_a_failure in ("exact", "resource_abort"):
        assert_raises_match(ValueError, "attribution contract", classify,
                            outcome=not_a_failure)


def test_sb_soft_stop_bookkeeping_never_counts_exact():
    p_b, p1 = _stageb_injected_tables()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "stageb_stop"
        summary = ediag._run_stageb_from_tables(
            rng=ech.make_rng(ech.P3_DIAG_SEED + 2), p_b=p_b, p1=p1,
            seed=ech.P3_DIAG_SEED + 2, out=str(out), soft_cap_s=0.0)
        for rec in summary["b1"]:
            assert rec["n_resource_abort"] == rec["n_blocks_planned"]
            assert rec["n_executed"] == 0 and rec["n_exact"] == 0
            assert rec["oracle_rows"] == 0
            assert rec["gates"]["coverage_complete"] is False
        for rec in summary["b2"]["cases"] + summary["b3"]["cases"]:
            assert rec["n_resource_abort"] == rec["n_blocks_planned"]
            assert rec["n_executed"] == 0 and rec["n_exact"] == 0
            assert sum(rec["attribution"].values()) == 0
        planned = (
            len(ediag.STAGEB_B1_N) * ediag.STAGEB_B1_BLOCKS
            + len(ediag.STAGEB_B2_N) * len(ediag.STAGEB_MASK_NAMES)
            * ediag.STAGEB_B2_BLOCKS
            + len(ediag.STAGEB_MASK_NAMES) * ediag.STAGEB_B3_BLOCKS
        )
        assert summary["resource_abort_blocks"] == planned
        assert summary["hard_gates_pass"] is False
        assert sorted(p.name for p in out.iterdir()) == sorted(ediag.STAGEB_OUT_FILES)


if __name__ == "__main__":
    names = sorted(n for n, v in sorted(globals().items())
                   if n.startswith("test_") and callable(v))
    failed = 0
    for name in names:
        try:
            globals()[name]()
        except Exception as err:  # noqa: BLE001 -- minimal runner reports only
            failed += 1
            print(f"FAIL {name}: {type(err).__name__}: {err}")
        else:
            print(f"ok {name}")
    print(f"{len(names) - failed}/{len(names)} passed")
    print(f"a18 times (metric, decode): {EVIDENCE['a18_times']}")
    print(f"a19 times: {EVIDENCE['a19_times']}")
    sys.exit(1 if failed else 0)
