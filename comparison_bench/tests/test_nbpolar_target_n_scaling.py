"""Focused Phase 4-P12 target-population f=1.3 N-scaling profile tests.

Injected tiny/synthetic tables and arrays plus temporary roots only.  No V25
NPZ, no Model-F/raw/held-out/real/EVAL artifact, no production invocation
and no output outside a temporary directory.  Focused tests use their own
fresh seeds >= 2026091900 and never the frozen profile streams
2026091820..2026091825.

Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments, uses plain
asserts and restores any monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import target_n_scaling as tns
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.construction import analytic_order
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.synthetic import analytic_erasure_probs
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
    TAG_BITS,
    seed_bits_for,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIELD = make_gf32()
# Fresh test-local seeds; the frozen P12 streams are only read from the
# module constants and are never used as inputs here.
TEST_SEED_A = 2026091900
TEST_SEED_B = 2026091901
TEST_SEED_C = 2026091902
TEST_SEED_D = 2026091903
TEST_SEED_E = 2026091904
TEST_SEED_F = 2026091905
TEST_SEED_G = 2026091906
TEST_SEED_H = 2026091907

H1 = tns.EXPECTED_H1
H2 = tns.EXPECTED_H2
HTOTAL = tns.EXPECTED_TOTAL

# Frozen six-N allocation pinned by the packet arithmetic (Kt, K1, K2, leakage).
FROZEN_ALLOCATIONS = (
    (256, 40, 1, 39, 264),
    (4096, 840, 37, 803, 4264),
    (16384, 3399, 166, 3233, 17059),
    (65536, 13636, 678, 12958, 68244),
    (131072, 27285, 1381, 25904, 136489),
    (262144, 54583, 2776, 51807, 272979),
)


@contextlib.contextmanager
def patched(obj, name, value):
    original = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, original)


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def injected_counts(seed: int = TEST_SEED_A) -> np.ndarray:
    """Sparse V25-like 1024x1024 count matrix: no zero Bob column."""
    rng = np.random.default_rng(seed)
    counts = np.zeros((1024, 1024), dtype=np.float64)
    cols = np.repeat(np.arange(1024), 2)
    rows = rng.integers(0, 1024, size=2048)
    counts[rows, cols] = rng.integers(1, 500, size=2048)
    extra = rng.choice(1024, size=497, replace=False)
    counts[extra, extra] += rng.integers(1, 500, size=extra.size)
    counts = counts * 4.0
    return counts / counts.sum() * 262144.0


def expected_seam(counts: np.ndarray) -> tuple:
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_construction as tc,
    )

    report = tc.target_entropies(counts)
    return report.h1, report.h2, report.total


def uniform_p1_p2():
    p1 = np.full((32, 1024), 1.0 / 32.0, dtype=np.float64)
    p2 = np.full((32, 1024, 32), 1.0 / 32.0, dtype=np.float64)
    return p1, p2


def tiny_truth(n=8, seed=TEST_SEED_C):
    rng = np.random.default_rng(seed)
    high = rng.integers(0, 32, size=n).astype(np.int64)
    low = rng.integers(0, 32, size=n).astype(np.int64)
    bob = rng.integers(0, 4, size=n).astype(np.int64)
    u1 = polar_transform(high, field=FIELD, alpha=2)
    u2 = polar_transform(low, field=FIELD, alpha=2)
    labels = (low + 32 * high).astype(np.int64)
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        labels_to_bits as _l2b,
    )

    return {
        "bob": bob,
        "high": high,
        "low": low,
        "u1": u1,
        "u2": u2,
        "labels": labels,
        "label_bits": _l2b(labels),
    }


class FakeSC:
    """Minimal accepted-SC-shaped result for seam tests (never production)."""

    def __init__(self, x_hat, metrics=None):
        self.x_hat = np.asarray(x_hat, dtype=np.int64)
        self.u_hat = self.x_hat.copy()
        if metrics is None:
            metrics = np.zeros((self.x_hat.shape[0], 32), dtype=np.float64)
        self.decision_metrics = np.asarray(metrics, dtype=np.float64)


def constant_tag(bits, seed, nbits):
    assert int(nbits) == 64
    return b"\x00" * 8


# ---- budget floors ----

def test_budget_formula_and_clip():
    assert tns.budget_k_total(256, HTOTAL) == 40
    assert tns.budget_k_total(8, 0.0) == 0  # floor negative -> clip to 0
    assert tns.budget_k_total(8, 100.0) == 16  # huge budget -> clip to 2N
    assert tns.budget_k_total(8, 0.5) == max(0, min(16, int(math.floor((1.3 * 8 * 0.5 - 64.0) / 5.0))))
    assert_raises_match(ValueError, "power of two", tns.budget_k_total, 7, HTOTAL)
    assert_raises_match(ValueError, "target_f", tns.budget_k_total, 8, HTOTAL, -1.0)


def test_budget_full_use_inequality_frozen_points():
    for n, kt, _k1, _k2, leak in FROZEN_ALLOCATIONS:
        assert tns.budget_k_total(n, H1 + H2) == kt
        assert leak == 5 * kt + 64
        assert leak <= 1.3 * n * (H1 + H2)
        assert leak / (n * (H1 + H2)) <= 1.3


def test_frozen_six_allocations_pinned():
    for n, kt, k1, k2, leak in FROZEN_ALLOCATIONS:
        alloc = tns.allocate_layer_ks(n, H1, H2, kt)
        assert (alloc["k1"], alloc["k2"]) == (k1, k2), f"N={n}"
        assert alloc["k_total"] == kt
        assert 5 * kt + 64 == leak


# ---- K feasibility and ties ----

def test_k_feasibility_window():
    alloc = tns.allocate_layer_ks(8, 0.4, 0.9, 10)
    assert alloc["k1"] + alloc["k2"] == 10
    assert 2 <= alloc["k1"] <= 8  # feasible window [max(0,10-8), min(8,10)]
    alloc = tns.allocate_layer_ks(8, 0.4, 0.9, 0)
    assert (alloc["k1"], alloc["k2"]) == (0, 0)
    alloc = tns.allocate_layer_ks(8, 0.4, 0.9, 16)
    assert alloc["k1"] + alloc["k2"] == 16
    assert_raises_match(ValueError, "k_total", tns.allocate_layer_ks, 8, 0.4, 0.9, 17)


def test_k_tie_break_to_smallest_k1():
    # All-zero reliabilities: every feasible K1 ties at residual 0.
    alloc = tns.allocate_layer_ks(8, 0.0, 0.0, 10)
    assert alloc["residual"] == 0.0
    assert (alloc["k1"], alloc["k2"]) == (2, 8)
    alloc = tns.allocate_layer_ks(8, 0.0, 0.0, 5)
    assert (alloc["k1"], alloc["k2"]) == (0, 5)


def test_k_enumeration_matches_brute_force():
    rng = np.random.default_rng(TEST_SEED_B)
    for trial in range(5):
        n = 8
        h1, h2 = float(rng.uniform(0.05, 0.9)), float(rng.uniform(0.05, 0.9))
        kt = int(rng.integers(0, 2 * n + 1))
        alloc = tns.allocate_layer_ks(n, h1, h2, kt)
        z1 = np.asarray(analytic_erasure_probs(min(1.0, max(0.0, h1 / 5.0)), n))
        z2 = np.asarray(analytic_erasure_probs(min(1.0, max(0.0, h2 / 5.0)), n))
        o1 = np.asarray(analytic_order(min(1.0, max(0.0, h1 / 5.0)), n))
        o2 = np.asarray(analytic_order(min(1.0, max(0.0, h2 / 5.0)), n))
        cands = []
        for k1 in range(max(0, kt - n), min(n, kt) + 1):
            k2 = kt - k1
            residual = float(z1[np.setdiff1d(np.arange(n), o1[:k1])].sum() + z2[np.setdiff1d(np.arange(n), o2[:k2])].sum())
            cands.append((residual, k1, k2))
        want = min(cands)
        assert (alloc["k1"], alloc["k2"]) == (want[1], want[2])
        assert abs(alloc["residual"] - want[0]) < 1e-9


# ---- literal BEC recurrence and order ----

def test_bec_recurrence_tiny_hand_values():
    z = analytic_erasure_probs(0.5, 2)
    assert list(z) == [0.75, 0.25]
    z = analytic_erasure_probs(0.5, 4)
    assert list(z) == [0.9375, 0.5625, 0.4375, 0.0625]
    z = analytic_erasure_probs(0.0, 8)
    assert bool((z == 0.0).all())
    z = analytic_erasure_probs(1.0, 8)
    assert bool((z == 1.0).all())


def test_bec_order_index_tie_break():
    assert list(analytic_order(0.0, 8)) == list(range(8))
    assert list(analytic_order(1.0, 8)) == list(range(8))
    assert list(analytic_order(0.5, 4)) == [0, 1, 2, 3]
    alloc = tns.allocate_layer_ks(4, H1, H2, 3)
    assert sorted(alloc["l1_order"].tolist()) == [0, 1, 2, 3]
    assert sorted(alloc["l2_order"].tolist()) == [0, 1, 2, 3]


# ---- Clopper-Pearson ----

def binom_tail_ge(x, n, p):
    return math.fsum(math.comb(n, k) * (p ** k) * ((1.0 - p) ** (n - k)) for k in range(x, n + 1))


def binom_tail_le(x, n, p):
    return math.fsum(math.comb(n, k) * (p ** k) * ((1.0 - p) ** (n - k)) for k in range(0, x + 1))


def test_clopper_pearson_edges():
    alpha = 0.05
    for n in (1, 4, 16, 64):
        lo, hi = tns.clopper_pearson_interval(0, n)
        assert lo == 0.0
        assert abs(hi - (1.0 - (alpha / 2.0) ** (1.0 / n))) < 1e-9
        lo, hi = tns.clopper_pearson_interval(n, n)
        assert hi == 1.0
        assert abs(lo - ((alpha / 2.0) ** (1.0 / n))) < 1e-9
    assert tns.clopper_pearson_interval(0, 0) == (0.0, 1.0)
    assert_raises_match(ValueError, "must not exceed", tns.clopper_pearson_interval, 3, 2)


def test_clopper_pearson_small_n_against_binomial_identity():
    alpha = 0.05
    for n, x in ((8, 1), (8, 4), (8, 7), (16, 3), (16, 13), (5, 2)):
        lo, hi = tns.clopper_pearson_interval(x, n, alpha)
        assert 0.0 <= lo <= x / n <= hi <= 1.0
        assert abs(binom_tail_ge(x, n, lo) - alpha / 2.0) < 1e-6
        assert abs(binom_tail_le(x, n, hi) - alpha / 2.0) < 1e-6


# ---- f/accounting, axes/packing, tag seeds ----

def test_f_and_tag_free_f():
    for n, kt, _k1, _k2, leak in FROZEN_ALLOCATIONS:
        f = leak / (n * (H1 + H2))
        f_no_tag = (5 * kt) / (n * (H1 + H2))
        assert f <= 1.3
        assert f_no_tag < f


def test_axes_packing_round_trip():
    counts = injected_counts()
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_construction as tc,
    )

    table = tc.build_target_conditional(counts)
    rng = np.random.default_rng(TEST_SEED_D)
    bob, a_full, high, low = tc.sample_target_block(rng, p_b=table.p_b, f_full=table.f, n=8)
    assert bob.shape == high.shape == low.shape == (8,)
    assert bool(((a_full == 32 * high + low)).all())
    assert bool((((high == a_full // 32) & (low == a_full % 32))).all())


def test_profile_seed_domain_separation():
    s1 = tns.profile_seed_bits(100, 8, 0)
    assert s1.shape == (seed_bits_for(8),) and s1.dtype == np.uint8
    assert np.array_equal(s1, tns.profile_seed_bits(100, 8, 0))
    assert not np.array_equal(s1, tns.profile_seed_bits(100, 8, 1))
    assert not np.array_equal(s1, tns.profile_seed_bits(101, 8, 0))
    assert tns.profile_seed_bits(100, 16, 0).shape == (seed_bits_for(16),)


# ---- causal two-layer wiring, buckets, truth isolation ----

def test_l2_metric_uses_hard_candidate_not_truth():
    truth = tiny_truth()
    p1, _p2 = uniform_p1_p2()
    # L2 table where the metric visibly depends on the L1 candidate.
    p2 = np.full((32, 1024, 32), 1.0 / 32.0 / 31.0, dtype=np.float64)
    p2[3, :, 3] = 0.9
    p2[:, :, :] /= p2.sum(axis=2, keepdims=True)
    seen = {}

    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import prior as prior_mod

    real_gather = prior_mod.gather_p2_metrics
    def spy_gather(bob, u1, table):
        seen["u1"] = np.array(u1, copy=True)
        return real_gather(bob, u1, table)

    forced = np.full(8, 3, dtype=np.int64)
    calls = {"n": 0}

    def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return FakeSC(forced)
        return FakeSC(truth["low"])

    with patched(tns, "sc_decode", fake_sc):
        with patched(tns, "gather_p2_metrics", spy_gather):
            arm = tns.run_scale_arm(
                n=8, stream_seed=TEST_SEED_E, block_index=0, bob=truth["bob"],
                high_true=truth["high"], low_true=truth["low"], u1_true=truth["u1"],
                u2_true=truth["u2"], labels_true=truth["labels"],
                labels_true_bits=truth["label_bits"], field=FIELD,
                p1_table=p1, p2_table=p2,
                l1_order=np.arange(8, dtype=np.int64), l2_order=np.arange(8, dtype=np.int64),
                k1=2, k2=2, master=TEST_SEED_E + 10000, tag_fn=constant_tag,
            )
    assert np.array_equal(seen["u1"][0], forced)
    assert arm.l2_provenance == "CANDIDATE_CONDITIONED"
    assert arm.l1_provenance == "PRIOR_ONLY"


def test_outcome_buckets_forced():
    truth = tiny_truth()
    p1, p2 = uniform_p1_p2()
    order = np.arange(8, dtype=np.int64)
    kw = dict(
        n=8, stream_seed=TEST_SEED_F, block_index=0, bob=truth["bob"],
        high_true=truth["high"], low_true=truth["low"], u1_true=truth["u1"],
        u2_true=truth["u2"], labels_true=truth["labels"],
        labels_true_bits=truth["label_bits"], field=FIELD,
        p1_table=p1, p2_table=p2, l1_order=order, l2_order=order,
        k1=2, k2=2, master=TEST_SEED_F + 10000,
    )
    # exact: true candidates, matching tags.
    calls = {"n": 0}

    def true_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        calls["n"] += 1
        return FakeSC(truth["high"] if calls["n"] == 1 else truth["low"])

    with patched(tns, "sc_decode", true_sc):
        arm = tns.run_scale_arm(tag_fn=constant_tag, **kw)
    assert arm.outcome == "exact" and arm.exact and arm.tag_invoked
    assert arm.key_dependent_bits == 5 * 2 + 5 * 2 + TAG_BITS
    assert arm.public_control_bits == seed_bits_for(8)
    assert not arm.truth_leak_violation

    # verify_failed: true candidates, mismatched tags.
    def split_tag(bits, seed, nbits):
        split_tag.n += 1
        return b"\x00" * 8 if split_tag.n == 1 else b"\xff" * 8

    split_tag.n = 0
    calls["n"] = 0
    with patched(tns, "sc_decode", true_sc):
        arm = tns.run_scale_arm(tag_fn=split_tag, **kw)
    assert arm.outcome == "verify_failed" and not arm.exact

    # undetected: wrong L2 candidate, tags forced equal (never success).
    def wrong_l2_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        wrong_l2_sc.n += 1
        if wrong_l2_sc.n == 1:
            return FakeSC(truth["high"])
        return FakeSC((truth["low"] + 1) % 32)

    wrong_l2_sc.n = 0
    with patched(tns, "sc_decode", wrong_l2_sc):
        arm = tns.run_scale_arm(tag_fn=constant_tag, **kw)
    assert arm.outcome == "undetected" and not arm.exact and arm.tag_pass

    # decode_failed: SC raises, no tag.
    def boom(logp, *, field, alpha=2, known_positions=None, known_values=None):
        raise ValueError("injected SC failure")

    with patched(tns, "sc_decode", boom):
        arm = tns.run_scale_arm(tag_fn=constant_tag, **kw)
    assert arm.outcome == "decode_failed" and not arm.tag_invoked
    assert arm.key_dependent_bits == 5 * 2  # only actually disclosed L1 bits
    assert arm.public_control_bits == 0


def test_truth_inputs_never_aliased():
    truth = tiny_truth()
    before = {k: np.array(v, copy=True) for k, v in truth.items() if k != "label_bits"}
    p1, p2 = uniform_p1_p2()
    order = np.arange(8, dtype=np.int64)
    tns.run_scale_arm(
        n=8, stream_seed=TEST_SEED_G, block_index=0, bob=truth["bob"],
        high_true=truth["high"], low_true=truth["low"], u1_true=truth["u1"],
        u2_true=truth["u2"], labels_true=truth["labels"],
        labels_true_bits=truth["label_bits"], field=FIELD,
        p1_table=p1, p2_table=p2, l1_order=order, l2_order=order,
        k1=2, k2=2, master=TEST_SEED_G + 10000, tag_fn=constant_tag,
    )
    for k, snapshot in before.items():
        assert np.array_equal(truth[k], snapshot), k


def test_transcript_recount_literal():
    truth = tiny_truth()
    p1, p2 = uniform_p1_p2()
    order = np.arange(8, dtype=np.int64)
    arm = tns.run_scale_arm(
        n=8, stream_seed=TEST_SEED_H, block_index=3, bob=truth["bob"],
        high_true=truth["high"], low_true=truth["low"], u1_true=truth["u1"],
        u2_true=truth["u2"], labels_true=truth["labels"],
        labels_true_bits=truth["label_bits"], field=FIELD,
        p1_table=p1, p2_table=p2, l1_order=order, l2_order=order,
        k1=2, k2=2, master=TEST_SEED_H + 10000, tag_fn=constant_tag,
    )
    events = tns.block_events(8, TEST_SEED_H, arm)
    recount = tns.recount_events(events)
    assert recount["key_dependent_bits"] == arm.key_dependent_bits
    assert recount["public_control_bits"] == arm.public_control_bits
    assert recount["tag_invocations"] == int(arm.tag_invoked)
    assert recount["by_n"]["8"]["key_dependent_bits"] == arm.key_dependent_bits
    assert_raises_match(ValueError, "event id", tns.recount_events, [{"event_id": "bogus"}])


# ---- refusals, loader isolation, end-to-end tiny run ----

def test_absent_root_refusal_creates_nothing():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        root.mkdir()
        with patched(tns, "load_v25_channel_counts", forbidden_loader):
            assert_raises_match(
                FileExistsError, "refusing to overwrite", tns.run_target_n_scaling,
                counts=injected_counts(), out_dir=root,
            )
            assert_raises_match(ValueError, "chunk-rows", tns.run_target_n_scaling,
                                counts=injected_counts(), chunk_rows=64, out_dir=Path(tmp) / "nope")
        assert not (Path(tmp) / "nope").exists()


def test_precondition_failure_zero_sc_and_no_root():
    def boom_sc(*args, **kwargs):
        raise AssertionError("no SC call may happen before the contract passes")

    counts = injected_counts()
    counts[:, 0] = 0.0  # zero Bob column breaks the target contract
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(tns, "sc_decode", boom_sc):
            assert_raises_match(
                tns.TargetPopulationContractError, "BLOCKED(target_population_contract)",
                tns.run_target_n_scaling, counts=counts,
                expected_entropies=(H1, H2, H1 + H2), out_dir=root,
                n_values=[8], stream_seeds=[TEST_SEED_A], blocks=[1],
            )
        assert not root.exists()


def test_no_production_loader_on_injected_path():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    counts = injected_counts()
    with tempfile.TemporaryDirectory() as tmp:
        with patched(tns, "load_v25_channel_counts", forbidden_loader):
            run = tns.run_target_n_scaling(
                counts=counts, expected_entropies=expected_seam(counts),
                out_dir=Path(tmp) / "out", n_values=[64, 128],
                stream_seeds=[TEST_SEED_A, TEST_SEED_B], blocks=[2, 1],
            )
        assert run.summary["input_mode"] == "injected_counts"
        assert run.summary["outcome_label"] == "BLOCKED(six_n_rows_and_128_blocks)"
        files = sorted(p.name for p in Path(run.plan["out_root"]).iterdir())
        assert files == sorted(tns.OUTPUT_FILES)


def test_tiny_end_to_end_files_buckets_and_recount():
    counts = injected_counts()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run = tns.run_target_n_scaling(
            counts=counts, expected_entropies=expected_seam(counts),
            out_dir=out, n_values=[64], stream_seeds=[TEST_SEED_C], blocks=[3],
        )
        assert sorted(p.name for p in out.iterdir()) == sorted(tns.OUTPUT_FILES)
        summary = json.loads((out / "aggregate_summary.json").read_text())
        per = summary["per_n"]["64"]
        buckets = per["buckets"]
        assert sum(buckets.values()) == 3
        assert per["exact"] + buckets["verify_failed"] + buckets["decode_failed"] + buckets["undetected"] == 3
        lo, hi = per["clopper_pearson_95"]["lower"], per["clopper_pearson_95"]["upper"]
        assert 0.0 <= lo <= per["exact_fraction"] <= hi <= 1.0
        assert per["f"] <= 1.3
        acc = summary["disclosure_accounting"]
        assert acc["mismatch_count"] == 0 and not acc["mismatches"]
        assert acc["key_dependent_bits_total"] == acc["recount"]["key_dependent_bits"]
        blocks_doc = json.loads((out / "per_block_outcomes.json").read_text())
        assert blocks_doc["n_blocks"] == 3
        alloc_doc = json.loads((out / "allocation_and_orders.json").read_text())
        assert alloc_doc["frozen_before_first_sc"] is True
        assert alloc_doc["allocation_unchanged_after_execution"] is True
        # Scalar-only: no symbol/key/metric arrays persisted anywhere.
        for name in tns.OUTPUT_FILES:
            if name.endswith(".json"):
                text = (out / name).read_text()
                assert "high_hat" not in text and "decision_metrics" not in text


def test_resource_stop_path_is_blocked():
    counts = injected_counts()
    with tempfile.TemporaryDirectory() as tmp:
        with patched(tns, "_budget_exceeded", lambda *a, **k: "wall_s"):
            run = tns.run_target_n_scaling(
                counts=counts, expected_entropies=expected_seam(counts),
                out_dir=Path(tmp) / "out", n_values=[64], stream_seeds=[TEST_SEED_D],
                blocks=[2],
            )
    assert run.summary["resource_stop_fired"] is True
    assert run.summary["outcome_label"] == "BLOCKED(six_n_rows_and_128_blocks)"
    assert all(r["outcome"] == "resource_abort" for r in run.records)


def test_chunk_contract_and_cli_parse_refusals():
    import subprocess

    assert tns.FROZEN_CHUNK_ROWS == 512
    # CLI parse failure refuses before any NPZ access (exit code 2 from argparse).
    proc = subprocess.run(
        [sys.executable, "-m",
         "comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_n_scaling",
         "--counts", "x"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 2
