"""Focused Phase 4-P7 target-population empirical construction gate tests.

Injected tiny/synthetic tables and temporary roots only.  No V25 NPZ, no
Model-F/raw/held-out artifact, no production gate invocation and no output
outside a temporary directory.  Focused tests use their own fresh seeds
>= 2026091680 and never the frozen TRAIN/DEV streams 2026091650..2026091652 /
2026091660..2026091664.

Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments, uses plain
asserts and restores any monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import target_construction as tc
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    derive_p1,
    derive_p2,
    gather_p2_metrics,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import labels_to_bits

REPO_ROOT = Path(__file__).resolve().parents[2]
FIELD = make_gf32()
# Fresh test-local seeds (>= 2026091680); the frozen gate streams are only read
# from the module constants and are never used as inputs here.
TEST_SEED_A = 2026091680
TEST_SEED_B = 2026091681
TEST_SEED_C = 2026091682
TEST_SEED_D = 2026091683
TEST_SEED_E = 2026091684
TEST_SEED_F = 2026091685
TEST_SEED_G = 2026091686
TEST_SEEDS = (TEST_SEED_A, TEST_SEED_B, TEST_SEED_C, TEST_SEED_D, TEST_SEED_E, TEST_SEED_F, TEST_SEED_G)

FORBIDDEN_MODULE_MARKERS = (
    "model_f",
    "v72p2d5",
    "parquet",
    "ttbin",
    "pandas",
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


def expectations(counts: np.ndarray) -> tuple:
    report = tc.target_entropies(counts)
    return report.h1, report.h2, report.total


def run_kwargs(counts, train_seed=TEST_SEED_A, dev_seed=TEST_SEED_B, train_blocks=1, dev_blocks=2):
    return {
        "counts": counts,
        "train_seeds": (train_seed,),
        "train_blocks": train_blocks,
        "dev_seeds": (dev_seed,),
        "dev_blocks": dev_blocks,
        "expected_entropies": expectations(counts),
    }


def tiny_tables():
    """Tiny p_b plus a P(A|B) table with q_high=2, q_low=2 (A=4, B=3)."""
    p_b = np.array([0.5, 0.3, 0.2], dtype=np.float64)
    f = np.array(
        [
            [0.70, 0.10, 0.25],
            [0.10, 0.60, 0.25],
            [0.15, 0.20, 0.25],
            [0.05, 0.10, 0.25],
        ],
        dtype=np.float64,
    )
    return p_b, f


class FakeSC:
    """Minimal accepted-SC-shaped result for seam tests (never production)."""

    def __init__(self, x_hat, metrics=None):
        self.x_hat = np.asarray(x_hat, dtype=np.int64)
        self.u_hat = self.x_hat.copy()
        if metrics is None:
            metrics = np.zeros((self.x_hat.shape[0], 32), dtype=np.float64)
        self.decision_metrics = np.asarray(metrics, dtype=np.float64)


def gate_p1_p2(counts):
    table = tc.build_target_conditional(counts)
    return derive_p1(table.f), derive_p2(table.f)


def ent_literal(probs, axis=None):
    """Independent literal entropy: skip exact zeros, no shared module helper."""
    arr = np.asarray(probs, dtype=np.float64)
    out = np.zeros_like(arr)
    mask = arr > 0.0
    out[mask] = -arr[mask] * np.log2(arr[mask])
    return out.sum(axis=axis)


def test_p7_support_rule_floor_renormalization_and_refusals():
    counts = np.array(
        [[4.0, 0.0, 1.0], [0.0, 2.0, 1.0], [1.0, 1.0, 0.0], [3.0, 1.0, 0.0]]
    )
    table = tc.build_target_conditional(counts, floor=1e-15)
    col = counts.sum(axis=0)
    assert np.allclose(table.p_b, col / col.sum(), atol=1e-15, rtol=0)
    ref = counts / col
    ref = np.maximum(ref, 1e-15)
    ref = ref / ref.sum(axis=0, keepdims=True)
    assert np.array_equal(table.f, ref)
    assert table.column_dev <= tc.COLUMN_TOL
    # floor-then-renormalize: pre-division cells are >= 1e-15, post stays within
    # one float rounding of the floor
    assert float(table.f.min()) >= 1e-15 * (1.0 - 1e-12)
    assert table.total_count == float(counts.sum())
    assert table.floor == 1e-15

    zero_col = np.array([[1.0, 0.0], [1.0, 0.0]])
    assert_raises_match(
        tc.TargetPopulationContractError, "zero Bob column", tc.build_target_conditional, zero_col
    )
    assert_raises_match(
        TypeError, "boolean", tc.build_target_conditional, np.ones((2, 2), dtype=bool)
    )
    assert_raises_match(ValueError, "2-D", tc.build_target_conditional, np.ones(4))
    assert_raises_match(
        ValueError, "finite", tc.build_target_conditional, np.array([[1.0, np.inf], [1.0, 1.0]])
    )
    assert_raises_match(
        ValueError, "non-negative", tc.build_target_conditional, np.array([[1.0, -1.0], [1.0, 1.0]])
    )
    assert_raises_match(ValueError, "floor", tc.build_target_conditional, np.ones((2, 2)), floor=0.0)
    assert_raises_match(ValueError, "floor", tc.build_target_conditional, np.ones((2, 2)), floor=1.0)

    assert float(tc.entropy_bits(np.array([0.0, 0.0, 0.0, 0.0]))) == 0.0
    assert abs(float(tc.entropy_bits(np.full(32, 1.0 / 32.0))) - 5.0) < 1e-12
    assert_raises_match(ValueError, "finite", tc.entropy_bits, np.array([np.nan]))


def test_p7_population_and_floored_entropy_reconstruction():
    counts = injected_counts(TEST_SEED_C)
    report = tc.target_entropies(counts)
    col = counts.sum(axis=0)
    p_b = col / col.sum()
    raw_f = counts / col
    joint = raw_f.reshape(32, 32, 1024)
    p1_raw = joint.sum(axis=1)
    mass = joint.sum(axis=1)
    p2_raw = np.empty((32, 1024, 32), dtype=np.float64)
    for u1 in range(32):
        for b in range(1024):
            if mass[u1, b] > 0:
                p2_raw[u1, b] = joint[u1, :, b] / mass[u1, b]
            else:
                p2_raw[u1, b] = 1.0 / 32.0
    h1 = float(np.sum(p_b[None, :] * ent_literal(p1_raw, axis=0)))
    h2 = float(np.sum(p_b[None, :] * p1_raw * ent_literal(p2_raw, axis=2)))
    assert abs(report.h1 - h1) < 1e-12
    assert abs(report.h2 - h2) < 1e-12
    assert abs(report.total - (h1 + h2)) < 1e-12

    floored = np.maximum(raw_f, 1e-15)
    floored = floored / floored.sum(axis=0, keepdims=True)
    fjoint = floored.reshape(32, 32, 1024)
    fp1 = fjoint.sum(axis=1)
    fmass = fjoint.sum(axis=1)
    fp2 = np.empty((32, 1024, 32), dtype=np.float64)
    for u1 in range(32):
        for b in range(1024):
            fp2[u1, b] = fjoint[u1, :, b] / fmass[u1, b]
    fh1 = float(np.sum(p_b[None, :] * ent_literal(fp1, axis=0)))
    fh2 = float(np.sum(p_b[None, :] * fp1 * ent_literal(fp2, axis=2)))
    assert abs(report.floor_h1 - fh1) < 1e-12
    assert abs(report.floor_h2 - fh2) < 1e-12
    assert abs(report.floor_total - (fh1 + fh2)) < 1e-12
    # The sparse-counts floor guard is meaningful: a real (but bounded) shift.
    assert 0.0 < report.floor_change <= tc.FLOOR_ENTROPY_TOL


def test_p7_preconditions_zero_column_literal_mismatch_and_floor_change():
    counts = injected_counts(TEST_SEED_D)
    h1, h2, total = expectations(counts)
    report = tc.target_preconditions(counts, expected_h1=h1, expected_h2=h2, expected_total=total)
    assert set(report.checks) == set(tc.PRECONDITION_ORDER)
    assert report.passed is True and report.failing == ()
    assert all(report.checks.values())
    assert report.column_dev <= tc.COLUMN_TOL

    bad = tc.target_preconditions(
        counts, expected_h1=h1 + 1e-6, expected_h2=h2, expected_total=total
    )
    assert bad.passed is False and "h1_matches_literal" in bad.failing
    bad_total = tc.target_preconditions(
        counts, expected_h1=h1, expected_h2=h2, expected_total=total + 1e-6
    )
    assert "total_matches_literal" in bad_total.failing

    zero = np.zeros((1024, 1024), dtype=np.float64)
    zero[0, :] = 1.0
    zero[:, 0] = 0.0
    zero_report = tc.target_preconditions(zero)
    assert zero_report.passed is False
    assert zero_report.failing == tc.PRECONDITION_ORDER
    assert "zero Bob column" in zero_report.message

    extreme = tc.target_preconditions(
        counts, floor=0.5, expected_h1=h1, expected_h2=h2, expected_total=total
    )
    assert "floor_entropy_change_at_most_1e-9" in extreme.failing


def test_p7_sampler_frequencies_packing_and_determinism():
    p_b, f = tiny_tables()
    n = 20000
    rng = np.random.default_rng(TEST_SEED_E)
    bob, a_full, high, low = tc.sample_target_block(rng, p_b=p_b, f_full=f, n=n, q_high=2, q_low=2)
    assert bob.shape == (n,) and a_full.shape == (n,)
    assert np.array_equal(low + 2 * high, a_full)
    assert np.array_equal(high, a_full // 2) and np.array_equal(low, a_full % 2)
    freq_b = np.bincount(bob, minlength=3) / n
    assert np.allclose(freq_b, p_b, atol=0.02, rtol=0)
    for b in range(3):
        idx = bob == b
        freq_a = np.bincount(a_full[idx], minlength=4) / idx.sum()
        assert np.allclose(freq_a, f[:, b], atol=0.03, rtol=0)
    bob2, a2, _h2, _l2 = tc.sample_target_block(
        np.random.default_rng(TEST_SEED_E), p_b=p_b, f_full=f, n=n, q_high=2, q_low=2
    )
    assert np.array_equal(bob, bob2) and np.array_equal(a_full, a2)
    _b, a_other, _h, _l = tc.sample_target_block(
        np.random.default_rng(TEST_SEED_F), p_b=p_b, f_full=f, n=n, q_high=2, q_low=2
    )
    assert not np.array_equal(a_full, a_other)
    assert_raises_match(
        TypeError, "Generator", tc.sample_target_block, np.random, p_b=p_b, f_full=f, n=4
    )


def test_p7_orders_per_stream_pooled_and_freeze():
    counts = injected_counts(TEST_SEED_F)
    root = Path(tempfile.mkdtemp()) / "orders"
    run = tc.run_target_construction(
        counts=counts,
        train_seeds=(TEST_SEED_A, TEST_SEED_B),
        train_blocks=1,
        dev_seeds=(TEST_SEED_C,),
        dev_blocks=2,
        out_dir=str(root),
        expected_entropies=expectations(counts),
    )
    orders = json.loads((root / "construction_orders.json").read_text(encoding="utf-8"))
    assert orders["frozen_before_dev"] is True
    assert orders["orders_unchanged_after_dev"] is True
    assert orders["train_seeds"] == [TEST_SEED_A, TEST_SEED_B]
    assert orders["orders_sha256"] == tc._canonical_sha(orders["layers"])
    for layer in ("l1", "l2"):
        rec = orders["layers"][layer]
        assert set(rec["per_stream"]) == {str(TEST_SEED_A), str(TEST_SEED_B)}
        for seed in (TEST_SEED_A, TEST_SEED_B):
            order = np.asarray(rec["per_stream"][str(seed)]["order"])
            assert order.shape == (256,)
            assert sorted(order.tolist()) == list(range(256))
        pooled = np.asarray(rec["pooled"]["order"])
        assert sorted(pooled.tolist()) == list(range(256))
        assert rec["permutation"] is True
        assert rec["provenance_consistent"] is True
        assert rec["bec"]["report_only"] is True
        eps = rec["bec"]["epsilon"]
        assert np.array_equal(np.asarray(rec["bec"]["order"]), tc.analytic_order(eps, 256))
        assert rec["pooled"]["n_used"] == sum(
            rec["per_stream"][str(s)]["n_used"] for s in (TEST_SEED_A, TEST_SEED_B)
        )
        assert rec["pooled"]["n_impossible"] == 0
    assert run.summary["orders_sha256"] == orders["orders_sha256"]
    assert run.summary["integrity"]["orders_frozen_permutations_provenance"] is True
    # No orders-unchanged failure path slipped through: the digest is the same
    # object hashed before and after the DEV phase.
    assert run.summary["orders_unchanged_after_dev"] is True


def test_p7_arm_separation_and_candidate_conditioned_l2():
    counts = injected_counts(TEST_SEED_G)
    p1, p2 = gate_p1_p2(counts)
    n, k1, k2 = 8, 3, 4
    high = np.arange(n, dtype=np.int64)
    low = np.array([7, 6, 5, 4, 3, 2, 1, 0], dtype=np.int64)
    u1 = polar_transform(high, field=FIELD, alpha=2)
    u2 = polar_transform(low, field=FIELD, alpha=2)
    labels = (low + 32 * high).astype(np.int64)
    bits = labels_to_bits(labels)
    bob = (np.arange(n, dtype=np.int64) * 127) % 1024
    l1_order = np.arange(n, dtype=np.int64)
    l2_order = l1_order[::-1].copy()
    candidate = (high + 1) % 32

    sc_calls = []

    def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        sc_calls.append(
            {
                "logp": np.array(logp, copy=True),
                "pos": np.array(known_positions, dtype=np.int64),
                "val": np.array(known_values, dtype=np.int64),
            }
        )
        if len(sc_calls) == 1:
            return FakeSC(candidate)
        return FakeSC(np.zeros(n, dtype=np.int64))

    gathered = []

    def spy_gather(bob_arg, u1_arg, table):
        gathered.append((np.array(bob_arg, copy=True), np.array(u1_arg, copy=True)))
        return gather_p2_metrics(bob_arg, u1_arg, table)

    with patched(tc, "sc_decode", fake_sc), patched(tc, "gather_p2_metrics", spy_gather):
        result = tc.run_dev_arm(
            arm="empirical",
            block_index=0,
            bob=bob,
            high_true=high,
            low_true=low,
            u1_true=u1,
            u2_true=u2,
            labels_true=labels,
            labels_true_bits=bits,
            field=FIELD,
            p1_table=p1,
            p2_table=p2,
            l1_order=l1_order,
            l2_order=l2_order,
            k1=k1,
            k2=k2,
            n=n,
            master=TEST_SEED_D,
        )
    assert len(sc_calls) == 2  # fresh L1 then fresh candidate-conditioned L2
    assert np.array_equal(sc_calls[0]["pos"], l1_order[:k1])
    assert np.array_equal(sc_calls[0]["val"], u1[l1_order[:k1]])
    assert np.array_equal(sc_calls[1]["pos"], l2_order[:k2])
    assert np.array_equal(sc_calls[1]["val"], u2[l2_order[:k2]])
    assert len(gathered) == 1
    assert np.array_equal(gathered[0][1][0], candidate)
    assert not np.array_equal(gathered[0][1][0], high)
    assert result.l1_provenance == "PRIOR_ONLY"
    assert result.l2_provenance == "CANDIDATE_CONDITIONED"
    assert np.array_equal(result.high_hat, candidate)
    assert np.array_equal(result.low_hat, np.zeros(n, dtype=np.int64))
    assert np.array_equal(result.label_hat, np.zeros(n, dtype=np.int64) + 32 * candidate)

    # Paired block: both arms compute their own candidate from their own L1
    # call; every fresh metric object is distinct (no L1 state transfer).
    call_state = {"i": 0}
    logp_ids = []

    def fake_sc_block(logp, *, field, alpha=2, known_positions=None, known_values=None):
        call_state["i"] += 1
        logp_ids.append(id(np.asarray(logp)))
        x = np.zeros(n, dtype=np.int64)
        x[0] = call_state["i"]
        return FakeSC(x)

    with patched(tc, "sc_decode", fake_sc_block):
        block = tc.run_dev_block(
            0,
            bob,
            high,
            low,
            u1,
            u2,
            labels,
            bits,
            field=FIELD,
            p1_table=p1,
            p2_table=p2,
            l1_orders={"empirical": l1_order, "bec": l2_order},
            l2_orders={"empirical": l1_order, "bec": l2_order},
            k1=k1,
            k2=k2,
            n=n,
            master=TEST_SEED_D,
        )
    assert call_state["i"] == 4
    assert block.empirical.high_hat[0] == 1
    assert block.bec.high_hat[0] == 3
    assert len(set(logp_ids)) == 4
    assert block.cell in tc.CELLS


def test_p7_outcome_buckets_and_paired_cells():
    assert tc.OUTCOMES == (
        "exact",
        "undetected",
        "verify_failed",
        "decode_failed",
        "resource_abort",
    )
    assert (
        tc.classify_outcome(l1_failed=False, l2_failed=False, tag_pass=True, label_match=True)
        == "exact"
    )
    assert (
        tc.classify_outcome(l1_failed=False, l2_failed=False, tag_pass=True, label_match=False)
        == "undetected"
    )
    assert (
        tc.classify_outcome(l1_failed=False, l2_failed=False, tag_pass=False, label_match=True)
        == "verify_failed"
    )
    assert (
        tc.classify_outcome(l1_failed=True, l2_failed=False, tag_pass=True, label_match=True)
        == "decode_failed"
    )
    assert (
        tc.classify_outcome(l1_failed=False, l2_failed=True, tag_pass=True, label_match=False)
        == "decode_failed"
    )
    assert tc.classify_pair(True, True) == "both_exact"
    assert tc.classify_pair(True, False) == "empirical_only"
    assert tc.classify_pair(False, True) == "bec_only"
    assert tc.classify_pair(False, False) == "neither"
    abort = tc._abort_arm("empirical")
    assert tc._arm_record_consistent(abort, k1=45, k2=140, n=256) is True
    inconsistent = tc.DevArmResult(
        arm="empirical",
        outcome="undetected",
        exact=False,
        label_match=True,  # undetected must NOT match the truth label
        tag_pass=True,
        l1_provenance="PRIOR_ONLY",
        l2_provenance="CANDIDATE_CONDITIONED",
        l1_executed=True,
        l1_decode_failed=False,
        l2_invoked=True,
        l2_skipped_by_l1_failure=False,
        l2_decode_failed=False,
        tag_invoked=True,
        key_dependent_bits=989,
        public_control_bits=2623,
        nonfinite=False,
        truth_leak_violation=False,
        l1_error_type=None,
        l2_error_type=None,
        wall_s=0.0,
    )
    assert tc._arm_record_consistent(inconsistent, k1=45, k2=140, n=256) is False
    no_tag = tc.DevArmResult(
        arm="bec",
        outcome="verify_failed",
        exact=False,
        label_match=False,
        tag_pass=False,
        l1_provenance="PRIOR_ONLY",
        l2_provenance="CANDIDATE_CONDITIONED",
        l1_executed=True,
        l1_decode_failed=False,
        l2_invoked=True,
        l2_skipped_by_l1_failure=False,
        l2_decode_failed=False,
        tag_invoked=False,  # verify_failed without a tag is inconsistent
        key_dependent_bits=925,
        public_control_bits=0,
        nonfinite=False,
        truth_leak_violation=False,
        l1_error_type=None,
        l2_error_type=None,
        wall_s=0.0,
    )
    assert tc._arm_record_consistent(no_tag, k1=45, k2=140, n=256) is False


def test_p7_disclosure_tag_accounting_and_recount():
    counts = injected_counts(TEST_SEED_A)
    root = Path(tempfile.mkdtemp()) / "acc"
    run = tc.run_target_construction(
        counts=counts,
        train_seeds=(TEST_SEED_B,),
        train_blocks=1,
        dev_seeds=(TEST_SEED_C, TEST_SEED_D),
        dev_blocks=2,
        out_dir=str(root),
        expected_entropies=expectations(counts),
    )
    per = json.loads((root / "per_block_paired_outcomes.json").read_text(encoding="utf-8"))
    assert per["n_blocks"] == 4
    kdb = tags = public = 0
    for record in per["blocks"]:
        for arm in ("empirical", "bec"):
            entry = record[arm]
            expected_kdb = (
                5 * 45
                + (5 * 140 if entry["l2_invoked"] else 0)
                + (64 if entry["tag_invoked"] else 0)
            )
            assert entry["key_dependent_bits"] == expected_kdb
            assert entry["public_control_bits"] == (2623 if entry["tag_invoked"] else 0)
            kdb += entry["key_dependent_bits"]
            tags += int(entry["tag_invoked"])
            public += entry["public_control_bits"]
    summary = json.loads((root / "aggregate_summary.json").read_text(encoding="utf-8"))
    acc = summary["disclosure_accounting"]
    assert acc["key_dependent_bits_total"] == kdb
    assert acc["tag_invocations"] == tags
    assert acc["public_control_bits_total"] == public
    assert acc["recount"]["key_dependent_bits"] == kdb
    assert acc["recount"]["public_control_bits"] == public
    assert acc["recount"]["tag_invocations"] == tags
    assert acc["mismatch_count"] == 0 and acc["mismatches"] == []
    assert acc["fully_invoked_arm_bits"] == 989
    assert acc["public_control_bits_per_tag"] == 2623
    assert acc["l1_bits_per_arm"] == 225 and acc["l2_bits_per_arm"] == 700
    assert acc["recount"]["event_types"]["l1_disclosure"] == 8
    assert acc["recount"]["event_types"]["verification_tag"] == tags
    assert len(run.events) == (
        acc["recount"]["event_types"]["l1_disclosure"]
        + acc["recount"]["event_types"]["l2_disclosure"]
        + tags
    )
    assert summary["integrity"]["disclosure_and_recount_exact"] is True

    tampered = [dict(event) for event in run.events]
    tampered[0]["key_dependent_bits"] += 5
    recount = tc.recount_events(tampered)
    assert recount["key_dependent_bits"] == kdb + 5
    wrong = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    wrong_by_arm = {arm: dict(wrong) for arm in tc.ARMS}
    assert tc._transcript_mismatches(wrong, wrong_by_arm, recount)


def test_p7_cli_refusals_and_frozen_constants():
    assert tc.FROZEN_TRAIN_SEEDS == (2026091650, 2026091651, 2026091652)
    assert tc.FROZEN_DEV_SEEDS == (2026091660, 2026091661, 2026091662, 2026091663, 2026091664)
    assert tc.FROZEN_TRAIN_BLOCKS == 256 and tc.FROZEN_DEV_BLOCKS == 128
    assert tc.FROZEN_PAIRS == 640
    assert tc.FROZEN_N == 256 and tc.FROZEN_SOURCE == "1M" and tc.FROZEN_FLOOR == 1e-15
    assert tc.FROZEN_K1 == 45 and tc.FROZEN_K2 == 140
    assert tc.EXPECTED_NPZ_BYTES == 25166822
    assert tc.EXPECTED_H1 == 0.02428054681872374
    assert tc.EXPECTED_H2 == 0.7767572780789994
    assert tc.EXPECTED_TOTAL == 0.8010378248977232
    assert tc.ENTROPY_TOL == 1e-12 and tc.FLOOR_ENTROPY_TOL == 1e-9
    assert tc.SPEARMAN_MIN == 0.95 and tc.EXACT_MIN == 620 and tc.WILSON_MIN == 0.95
    assert tc.FULLY_INVOKED_ARM_BITS == 989
    assert tc.L1_DISCLOSURE_BITS == 225 and tc.L2_DISCLOSURE_BITS == 700
    assert tc.PUBLIC_CONTROL_BITS_PER_TAG == 2623
    assert tc.PUBLIC_TAG_MASTER_OFFSET == 10000
    assert tc.ATTEMPT_CONSUMPTION_POINT == "first NPZ content open (load_v25_channel_counts)"
    assert tc.ARTIFACT_READ_ACCOUNTING["artifact_content_reads_allowed"] == 1
    assert tc.ARTIFACT_READ_ACCOUNTING["attempts_allowed"] == 1
    assert tc.ARTIFACT_READ_ACCOUNTING["retries"] == 0
    assert tc.INTEGRITY_GATE_ORDER[0] == "target_population_contract"
    assert tc.INTEGRITY_GATE_ORDER[-1] == "resource_limits_met"
    assert tc.SCIENTIFIC_GATE_ORDER == (
        "train_spearman_min_at_least_0p95",
        "empirical_exact_at_least_620_of_640",
        "empirical_wilson_lower_bound_at_least_0p95",
    )
    assert tc.OUTPUT_FILES == (
        "frozen_plan.json",
        "construction_orders.json",
        "per_block_paired_outcomes.json",
        "aggregate_summary.json",
        "report.md",
    )
    assert "--counts" in tc.FROZEN_COMMAND and "--floor 1e-15" in tc.FROZEN_COMMAND
    assert ("channel_counts" + ".npz") in tc.FROZEN_COMMAND
    assert ("target_construction" + "_gate") in tc.FROZEN_COMMAND
    for seed in TEST_SEEDS:
        assert seed not in tc.FROZEN_TRAIN_SEEDS and seed not in tc.FROZEN_DEV_SEEDS
    assert_raises_match(tc.SeedPrefixError, "arm", tc.arm_seed_bits, "operational", 0, master=1)
    bits_a = tc.arm_seed_bits("empirical", 0, master=TEST_SEED_E)
    bits_b = tc.arm_seed_bits("empirical", 0, master=TEST_SEED_E)
    assert bits_a.shape == (2623,) and np.array_equal(bits_a, bits_b)
    assert not np.array_equal(bits_a, tc.arm_seed_bits("bec", 0, master=TEST_SEED_E))
    assert not np.array_equal(bits_a, tc.arm_seed_bits("empirical", 1, master=TEST_SEED_E))

    parser = tc.build_parser()
    option_pairs = [
        ("--counts", "x.npz"),
        ("--source", "1M"),
        ("--n", "256"),
        ("--floor", "1e-15"),
        ("--train-seeds", "2026091650"),
        ("--train-blocks", "256"),
        ("--dev-seeds", "2026091660"),
        ("--dev-blocks", "128"),
        ("--k1", "45"),
        ("--k2", "140"),
        ("--out-dir", "example_root"),
    ]
    frozen_argv = []
    for flag, value in option_pairs:
        frozen_argv.extend([flag, value])
    args = parser.parse_args(frozen_argv)
    assert args.n == 256 and args.floor == 1e-15
    assert args.train_blocks == 256 and args.dev_blocks == 128
    assert args.k1 == 45 and args.k2 == 140
    for drop in range(len(option_pairs)):
        reduced = []
        for index, (flag, value) in enumerate(option_pairs):
            if index != drop:
                reduced.extend([flag, value])
        assert_raises_match(SystemExit, "", parser.parse_args, reduced)

    def forbidden_loader(*args, **kwargs):
        raise AssertionError("loader must not run before the refusals")

    sandbox = Path(tempfile.mkdtemp())
    existing = sandbox / "exists"
    existing.mkdir()
    never = sandbox / "never"
    with patched(tc, "load_v25_channel_counts", forbidden_loader):
        assert_raises_match(
            FileExistsError,
            "refusing to overwrite",
            tc.run_target_construction,
            counts_path=str(sandbox / "fake.npz"),
            out_dir=str(existing),
        )
        assert tc.main(
            [
                "--counts", str(sandbox / "fake.npz"),
                "--source", "1M", "--n", "256", "--floor", "1e-15",
                "--train-seeds", "2026091650", "2026091651", "2026091652",
                "--train-blocks", "256",
                "--dev-seeds", "2026091660", "2026091661", "2026091662",
                "2026091663", "2026091664",
                "--dev-blocks", "128", "--k1", "45", "--k2", "140",
                "--out-dir", str(existing),
            ]
        ) == 2
        small = sandbox / "small.npz"
        small.write_bytes(b"0" * 10)
        assert_raises_match(
            ValueError,
            "size mismatch",
            tc.run_target_construction,
            counts_path=str(small),
            out_dir=str(never),
        )
        assert_raises_match(
            FileNotFoundError,
            "not found",
            tc.run_target_construction,
            counts_path=str(sandbox / "absent.npz"),
            out_dir=str(never),
        )
        good = injected_counts(TEST_SEED_A)
        exp = expectations(good)
        base = {
            "counts": good,
            "train_seeds": (TEST_SEED_A,),
            "train_blocks": 1,
            "dev_seeds": (TEST_SEED_B,),
            "dev_blocks": 1,
            "out_dir": str(never),
            "expected_entropies": exp,
        }
        for override in (
            {"n": 128},
            {"floor": 1e-6},
            {"source": "1p5M"},
            {"k1": 46},
            {"k2": 139},
        ):
            kwargs = dict(base)
            kwargs.update(override)
            assert_raises_match(ValueError, "", tc.run_target_construction, **kwargs)
        dup = dict(base)
        dup["train_seeds"] = (TEST_SEED_A, TEST_SEED_A)
        assert_raises_match(ValueError, "distinct", tc.run_target_construction, **dup)
        overlap = dict(base)
        overlap["dev_seeds"] = (TEST_SEED_A,)
        assert_raises_match(ValueError, "disjoint", tc.run_target_construction, **overlap)
        # injected counts never touch the loader, and the five files are exactly
        injected_root = Path(tempfile.mkdtemp()) / "injected"
        injected = tc.run_target_construction(
            counts=good,
            train_seeds=(TEST_SEED_A,),
            train_blocks=1,
            dev_seeds=(TEST_SEED_B,),
            dev_blocks=1,
            out_dir=str(injected_root),
            expected_entropies=exp,
        )
        assert injected.summary["input_mode"] == "injected_counts"
        assert injected.summary["integrity"]["attempt_read_accounting_exact"] is True
        assert injected.summary["attempt_read_accounting"]["open_count"] == 0
        assert sorted(p.name for p in injected_root.iterdir()) == sorted(tc.OUTPUT_FILES)
    assert not never.exists()


def test_p7_sentinel_and_resource_abort_paths():
    counts = injected_counts(TEST_SEED_B)
    exp = expectations(counts)
    root = Path(tempfile.mkdtemp()) / "leak"
    with patched(tc, "_truth_isolation_sentinel", lambda *args, **kwargs: False):
        run = tc.run_target_construction(
            counts=counts,
            train_seeds=(TEST_SEED_C,),
            train_blocks=1,
            dev_seeds=(TEST_SEED_D,),
            dev_blocks=1,
            out_dir=str(root),
            expected_entropies=exp,
        )
    assert run.summary["integrity"]["truth_leak_zero"] is False
    assert run.summary["integrity_all_pass"] is False
    assert run.summary["outcome_label"] == "BLOCKED"
    assert run.summary["blocked_detail"] == "BLOCKED(truth_leak_zero)"

    root2 = Path(tempfile.mkdtemp()) / "abort"
    state = {"n": 0}

    def fake_budget(start, cap):
        state["n"] += 1
        return None if state["n"] <= 2 else "wall_s"

    with patched(tc, "_budget_exceeded", fake_budget):
        run2 = tc.run_target_construction(
            counts=counts,
            train_seeds=(TEST_SEED_E,),
            train_blocks=1,
            dev_seeds=(TEST_SEED_F,),
            dev_blocks=3,
            out_dir=str(root2),
            expected_entropies=exp,
        )
    assert run2.summary["resource_stop_fired"] is True
    assert run2.summary["integrity"]["resource_abort_zero"] is False
    assert run2.summary["integrity"]["coverage_complete_and_disjoint"] is True
    assert run2.summary["integrity"]["pairing_and_buckets"] is True
    # Aborted arms are exempt from executed-arm accounting: the disclosure and
    # recount gate stays true while the resource gate alone blocks the label.
    assert run2.summary["integrity"]["disclosure_and_recount_exact"] is True
    assert run2.summary["outcome_label"] == "BLOCKED"
    assert "resource_abort_zero" in run2.summary["failing_integrity_gates"]
    per = json.loads((root2 / "per_block_paired_outcomes.json").read_text(encoding="utf-8"))
    assert per["n_blocks"] == 3
    aborted = [r for r in per["blocks"] if r["empirical"]["outcome"] == "resource_abort"]
    assert len(aborted) == 2
    for record in aborted:
        assert record["bec"]["outcome"] == "resource_abort"
        assert record["empirical"]["key_dependent_bits"] == 0
        assert record["empirical"]["public_control_bits"] == 0
    assert all(
        record["empirical"]["outcome"] != "resource_abort"
        for record in per["blocks"][:1]
    )
    # Aborted arms emit no transcript events.
    assert run2.summary["disclosure_accounting"]["recount"]["event_types"]["l1_disclosure"] == 2


def test_p7_no_forbidden_markers_or_production_invocation():
    import re

    source = Path(tc.__file__).read_text(encoding="utf-8")
    lowered = source.lower()
    for marker in FORBIDDEN_MODULE_MARKERS:
        assert marker not in lowered, f"forbidden marker {marker!r} in target_construction.py"
    for match in re.finditer(r"np\.random\.([A-Za-z_]+)\s*\(", source):
        assert match.group(1) == "default_rng", f"global RNG use: {match.group(0)}"
    assert "open(" not in source
    own = Path(__file__).read_text(encoding="utf-8")
    assert ("channel_counts" + ".npz") not in own
    assert ("target_construction" + "_gate") not in own
    for seed in tc.FROZEN_TRAIN_SEEDS + tc.FROZEN_DEV_SEEDS:
        assert f"default_rng({seed})" not in own
        assert f"train_seeds=({seed}" not in own
        assert f"dev_seeds=({seed}" not in own

    empty = Path(tempfile.mkdtemp())
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    code = (
        "import comparison_bench.src.comparison_bench.formal_ir.nbpolar."
        "target_construction as t; "
        "assert t.FROZEN_PAIRS == 640 and t.OUTPUT_FILES[0] == 'frozen_plan.json' "
        "and t.FULLY_INVOKED_ARM_BITS == 989"
    )
    proc = subprocess.run(
        [sys.executable, "-B", "-c", code],
        cwd=str(empty),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert list(empty.iterdir()) == []


if __name__ == "__main__":
    names = sorted(
        n for n, v in sorted(globals().items()) if n.startswith("test_") and callable(v)
    )
    failed = 0
    for name in names:
        started = time.perf_counter()
        try:
            globals()[name]()
        except Exception as err:  # noqa: BLE001 -- minimal runner reports only
            failed += 1
            print(f"FAIL {name}: {type(err).__name__}: {err}")
        else:
            print(f"ok {name} ({time.perf_counter() - started:.3f}s)")
    print(f"{len(names) - failed}/{len(names)} passed")
    sys.exit(1 if failed else 0)
