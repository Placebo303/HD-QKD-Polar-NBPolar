"""Focused Phase 4-P1 tests: prior adapter vs independent formula oracle.

Synthetic fixtures only. No CAL/TTBin/real data, no Model-F, no SC
decoder call, no benchmark, no file output, no floor from data, no
performance claim. Written without a pytest dependency so it runs under
plain ``python`` and is still collected by pytest elsewhere: every
``test_*`` function takes no arguments and uses plain asserts plus a
local ``assert_raises_match`` helper.

Gates V-P0-01--07 per ``docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`` section 6.
V-P0-08--12 remain closed for later packets. Tolerances are absolute
maxima (1e-12 unless noted).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    Conditioning,
    Provenance,
    SymbolMetric,
    build_p1_metrics,
    derive_p1,
    derive_p2,
    gather_p2_metrics,
    probs_to_symbol_metric,
    smooth_joint_to_conditional,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import prior as prior_mod

SEED = 20260930
PROB_TOL = 1e-12
NORM_TOL = 1e-12

BANNED_IDENTIFIERS = (
    "build_f_model",
    "prepare_model_f_prior",
    "get_l1_app_prior_l2",
    "app_fed_l2_prior",
)


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def oracle_smooth(counts, lam):
    """Independent literal-formula oracle (D7-A pattern: loops, no shared helper).

    Plain-Python per-cell evaluation of the frozen concentration formula;
    unseen-Bob columns fall back to ``p_global``.
    """
    grid = [[float(v) for v in row] for row in counts.tolist()]
    n_a = len(grid)
    n_b = len(grid[0])
    total = 0.0
    for a in range(n_a):
        for b in range(n_b):
            total += grid[a][b]
    p_global = [0.0] * n_a
    for a in range(n_a):
        s = 0.0
        for b in range(n_b):
            s += grid[a][b]
        p_global[a] = s / total
    n_bcol = [0.0] * n_b
    for b in range(n_b):
        s = 0.0
        for a in range(n_a):
            s += grid[a][b]
        n_bcol[b] = s
    out = [[0.0] * n_b for _ in range(n_a)]
    for a in range(n_a):
        for b in range(n_b):
            denom = n_bcol[b] + lam
            if denom == 0 or n_bcol[b] == 0:
                out[a][b] = p_global[a]
            else:
                out[a][b] = (grid[a][b] + lam * p_global[a]) / denom
    return np.array(out, dtype=np.float64)


def oracle_gather_p2_true(alice_true, bob, p2_table):
    """TEST-LOCAL oracle helper (never exported from ``nbpolar/``).

    Splits true Alice labels into true U1 and gathers oracle L2 rows.
    Operational code must never import this.
    """
    alice_true = np.asarray(alice_true, dtype=np.int64)
    bob = np.asarray(bob, dtype=np.int64)
    assert alice_true.shape == bob.shape
    u1_true = (alice_true >> 5) & 31
    return p2_table[u1_true, bob, :]


def hand_counts():
    """Asymmetric hand-built counts: total 7, transpose-sensitive cells."""
    counts = np.zeros((1024, 1024), dtype=np.int64)
    counts[33, 7] = 4
    counts[7, 33] = 1
    counts[0, 0] = 2
    return counts


def test_v01_axis_transpose_sentinel():
    counts = hand_counts()
    f = smooth_joint_to_conditional(counts, 7.0)
    # Hand-computed: total=7, p_global[33]=4/7, p_global[7]=1/7, p_global[0]=2/7.
    assert abs(f[33, 7] - 8.0 / 11.0) < 1e-15, f[33, 7]
    assert abs(f[0, 7] - 2.0 / 11.0) < 1e-15, f[0, 7]
    assert abs(f[7, 7] - 1.0 / 11.0) < 1e-15, f[7, 7]
    assert abs(f[7, 33] - 1.0 / 4.0) < 1e-15, f[7, 33]
    assert abs(f[33, 33] - 1.0 / 2.0) < 1e-15, f[33, 33]
    assert abs(f[0, 33] - 1.0 / 4.0) < 1e-15, f[0, 33]
    assert abs(f[0, 0] - 4.0 / 9.0) < 1e-15, f[0, 0]
    assert abs(f[33, 0] - 4.0 / 9.0) < 1e-15, f[0, 0]
    assert abs(f[7, 0] - 1.0 / 9.0) < 1e-15, f[7, 0]
    # Unseen column falls back to p_global.
    assert abs(f[33, 5] - 4.0 / 7.0) < 1e-15, f[33, 5]
    assert abs(f[7, 5] - 1.0 / 7.0) < 1e-15, f[7, 5]
    assert abs(f[0, 5] - 2.0 / 7.0) < 1e-15, f[0, 5]
    assert f[1, 5] == 0.0, f[1, 5]
    # Transpose sentinel: [Alice,Bob] must differ from [Bob,Alice].
    assert f[33, 7] != f[7, 33], (f[33, 7], f[7, 33])
    assert f.shape == (1024, 1024)


def test_v02_column_sums_and_fallbacks():
    rng = np.random.RandomState(SEED)
    counts = rng.randint(0, 6, size=(1024, 1024)).astype(np.float64)
    counts[:, 100:111] = 0.0  # guaranteed unseen Bob columns
    for lam in (7.0, 0.0):
        f = smooth_joint_to_conditional(counts, lam)
        dev = float(np.abs(f.sum(axis=0) - 1).max())
        assert dev <= NORM_TOL, (lam, dev)
        p_global = counts.sum(axis=1) / counts.sum()
        got = float(np.abs(f[:, 100:111] - p_global[:, None]).max())
        assert got == 0.0 or got <= 1e-15, (lam, got)


def test_v03_adapter_vs_independent_oracle():
    rng = np.random.RandomState(SEED + 1)
    counts = rng.randint(0, 4, size=(1024, 1024)).astype(np.float64)
    counts[:, 500:505] = 0.0
    lam = 7.0
    prod = smooth_joint_to_conditional(counts, lam)
    ref = oracle_smooth(counts, lam)
    diff = np.abs(prod - ref)
    cell = int(np.argmax(diff.max(axis=1)))
    assert diff.max() <= PROB_TOL, (diff.max(), cell)
    # derive parity against the oracle table through the same pure path.
    p1 = derive_p1(ref)
    assert p1.shape == (32, 1024)
    assert float(np.abs(derive_p1(prod) - p1).max()) <= PROB_TOL


def test_v04_prob_log_round_trip():
    rng = np.random.RandomState(SEED + 2)
    counts = rng.randint(0, 6, size=(1024, 1024)).astype(np.float64)
    p1 = derive_p1(smooth_joint_to_conditional(counts, 3.0))
    bob = rng.randint(0, 1024, size=(2, 4))
    probs = build_p1_metrics(bob, p1)
    for frame in range(probs.shape[0]):
        metric = probs_to_symbol_metric(probs[frame], provenance=Provenance.PRIOR_ONLY)
        assert isinstance(metric, SymbolMetric)
        assert metric.conditioning is Conditioning.FULL_BOB_ONLY
        assert metric.symbol_order == tuple(range(32))
        assert metric.normalization == "LOGSUMEXP_ZERO"
        back = np.exp(metric.logp)
        pos = probs[frame] > 0
        assert pos.all()
        assert float(np.abs(back[pos] - probs[frame][pos]).max()) <= PROB_TOL


def test_v05_exact_zero_stays_neginf():
    counts = np.zeros((1024, 1024), dtype=np.float64)
    counts[0, 0] = 5
    counts[1, 3] = 2
    counts[0, 900] = 1
    f = smooth_joint_to_conditional(counts, 7.0)
    p1 = derive_p1(f)
    assert (p1[1:, :] == 0).all()  # only Alice {0,1} observed -> U1>=1 empty
    bob = np.array([[0, 3, 900, 7]])
    probs = build_p1_metrics(bob, p1)
    metric = probs_to_symbol_metric(probs[0])
    zero = probs[0] == 0
    assert zero.any()
    assert (metric.logp[zero] == -np.inf).all()
    assert np.isfinite(metric.logp[~zero]).all()


def test_v06_packing_round_trip():
    for u1 in range(32):
        for u2 in range(32):
            s = prior_mod.combine_symbol(u2, u1)
            assert s == u2 + 32 * u1, (u1, u2, s)
            low, high = prior_mod.split_symbol(s)
            assert (low, high) == (u2, u1), (s, low, high)
    for s in (0, 1, 31, 32, 33, 63, 64, 511, 512, 1000, 1022, 1023):
        low, high = prior_mod.split_symbol(s)
        assert prior_mod.combine_symbol(low, high) == s, s
    assert_raises_match(ValueError, "axis contract:", prior_mod.split_symbol, 1024)
    assert_raises_match(ValueError, "axis contract:", prior_mod.combine_symbol, 0, 32)


def test_v07_batch_position_permutation_equivariance():
    rng = np.random.RandomState(SEED + 3)
    counts = rng.randint(0, 6, size=(1024, 1024)).astype(np.float64)
    f = smooth_joint_to_conditional(counts, 5.0)
    p1, p2 = derive_p1(f), derive_p2(f)
    bob = rng.randint(0, 1024, size=(3, 8))
    u1 = rng.randint(0, 32, size=(3, 8))
    frame_perm = [2, 0, 1]
    pos_perm = [7, 3, 0, 5, 1, 6, 2, 4]
    m1 = build_p1_metrics(bob, p1)
    m2 = gather_p2_metrics(bob, u1, p2)
    assert float(np.abs(m1[frame_perm][:, pos_perm] - build_p1_metrics(
        bob[frame_perm][:, pos_perm], p1)).max()) == 0.0
    assert float(np.abs(m2[frame_perm][:, pos_perm] - gather_p2_metrics(
        bob[frame_perm][:, pos_perm], u1[frame_perm][:, pos_perm], p2)).max()) == 0.0
    # Oracle helper agrees with the operational gather on true U1 (test-local only).
    alice_true = (u1 << 5) | rng.randint(0, 32, size=(3, 8))
    ref = oracle_gather_p2_true(alice_true, bob, p2)
    assert float(np.abs(ref - gather_p2_metrics(bob, u1, p2)).max()) <= 1e-15
    assert not hasattr(prior_mod, "oracle_gather_p2_true"), "oracle helper must stay test-local"


def test_error_prefix_taxonomy():
    counts = hand_counts()
    assert_raises_match(ValueError, "smoothing contract:",
                        smooth_joint_to_conditional, -counts, 1.0)
    assert_raises_match(ValueError, "smoothing contract:",
                        smooth_joint_to_conditional, np.zeros((4, 4)), 1.0)
    assert_raises_match(ValueError, "smoothing contract:",
                        smooth_joint_to_conditional, counts, -1.0)
    assert_raises_match(ValueError, "axis contract:",
                        smooth_joint_to_conditional, np.zeros((4, 4, 4)), 1.0)
    f = smooth_joint_to_conditional(counts, 7.0)
    assert_raises_match(ValueError, "axis contract:", derive_p1, f.T.reshape(1024, 1024)[:33, :])
    assert_raises_match(ValueError, "axis contract:",
                        build_p1_metrics, np.array([[1024]]), derive_p1(f))
    assert_raises_match(ValueError, "metric contract:",
                        probs_to_symbol_metric, np.full((4, 32), -0.1))
    assert_raises_match(ValueError, "metric contract:",
                        probs_to_symbol_metric, np.zeros((4, 32)))
    assert_raises_match(ValueError, "provenance contract:",
                        probs_to_symbol_metric, np.full((4, 32), 1 / 32),
                        provenance="PRIOR_ONLY")
    assert_raises_match(ValueError, "provenance contract:",
                        prior_mod.apply_explicit_floor,
                        np.full((4, 32), 1 / 32), 1e-6, reason="  ")
    assert_raises_match(ValueError, "metric contract:",
                        prior_mod.apply_explicit_floor,
                        np.full((4, 32), 1 / 32), 0.0, reason="x")
    assert_raises_match(ValueError, "lifecycle contract:",
                        prior_mod.check_frame_ids_disjoint, [1, 2], [2, 3])
    prior_mod.check_frame_ids_disjoint([1, 2], [3, 4], range(10, 13))


def test_floor_opt_in_only():
    probs = np.zeros((2, 32))
    probs[:, 0] = 1.0
    floored = prior_mod.apply_explicit_floor(probs, 1e-6, reason="synthetic P1 check")
    # Floor-then-renormalize lifts exact zeros to strict positivity (the
    # D5 diagnostic pattern); the floor value itself is not preserved
    # through renormalization, so positivity -- not the raw floor -- is asserted.
    assert (floored > 0).all()
    assert (probs[:, 1:] == 0).all(), "floor must not mutate its input"
    assert float(np.abs(floored.sum(axis=1) - 1).max()) <= 1e-12


def test_banned_twin_unimportable():
    src = Path(prior_mod.__file__).read_text(encoding="utf-8")
    for name in BANNED_IDENTIFIERS:
        assert name not in src, name
    assert "pandas" not in src and "parquet" not in src


def test_resource_smoke_decoder_free():
    rng = np.random.RandomState(SEED + 4)
    counts = rng.randint(0, 6, size=(1024, 1024)).astype(np.float64)
    start = time.time()
    f = smooth_joint_to_conditional(counts, 7.0)
    p1, p2 = derive_p1(f), derive_p2(f)
    frames, npos = 256, 256
    bob = rng.randint(0, 1024, size=(frames, npos))
    u1 = rng.randint(0, 32, size=(frames, npos))
    m1 = build_p1_metrics(bob, p1)
    m2 = gather_p2_metrics(bob, u1, p2)
    assert m1.shape == (frames, npos, 32) and m2.shape == (frames, npos, 32)
    metric = probs_to_symbol_metric(m1[0])
    assert metric.logp.shape == (npos, 32)
    wall = time.time() - start
    assert wall <= 60, wall
    try:
        import resource

        rss_gib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 ** 3)
        assert rss_gib < 2, rss_gib
    except ImportError:
        pass


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
    sys.exit(1 if failed else 0)
