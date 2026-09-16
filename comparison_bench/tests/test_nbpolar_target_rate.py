"""Focused Phase 4-P8 target rate SCREEN -> CONFIRM gate tests.

Injected tiny/synthetic tables and orders plus temporary roots only.  No V25
NPZ, no P7 orders file, no Model-F/raw/held-out artifact, no production gate
invocation and no output outside a temporary directory.  Focused tests use
their own fresh seeds >= 2026091700 and never the frozen SCREEN streams
2026091680..2026091682 or CONFIRM streams 2026091690..2026091694.

Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments, uses plain
asserts and restores any monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import target_rate as tr
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.construction import analytic_order
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform

REPO_ROOT = Path(__file__).resolve().parents[2]
FIELD = make_gf32()
# Fresh test-local seeds (>= 2026091700); the frozen SCREEN/CONFIRM streams
# are only read from the module constants and are never used as inputs here.
TEST_SEED_A = 2026091700
TEST_SEED_B = 2026091701
TEST_SEED_C = 2026091702
TEST_SEED_D = 2026091703
TEST_SEED_E = 2026091704
TEST_SEED_F = 2026091705
TEST_SEED_G = 2026091706
TEST_SEED_H = 2026091707
TEST_SEEDS = (
    TEST_SEED_A,
    TEST_SEED_B,
    TEST_SEED_C,
    TEST_SEED_D,
    TEST_SEED_E,
    TEST_SEED_F,
    TEST_SEED_G,
    TEST_SEED_H,
)

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


def expected_seam(counts: np.ndarray) -> tuple:
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_construction as tc,
    )

    report = tc.target_entropies(counts)
    return report.h1, report.h2, report.total


def injected_orders(seed: int = TEST_SEED_B) -> dict:
    """Four valid 256-permutations in the injected loaded-orders form."""
    rng = np.random.default_rng(seed)
    return {
        "l1_empirical": rng.permutation(256).astype(np.int64),
        "l2_empirical": rng.permutation(256).astype(np.int64),
        "l1_bec": analytic_order(0.05, 256),
        "l2_bec": analytic_order(0.155, 256),
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


def tiny_p1_p2():
    """Full-axis metric tables with uniform rows (shape per the accepted contract)."""
    p1 = np.full((32, 1024), 1.0 / 32.0, dtype=np.float64)
    p2 = np.full((32, 1024, 32), 1.0 / 32.0, dtype=np.float64)
    return p1, p2


def tiny_block(n=8, seed=TEST_SEED_C):
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

    return tr.SharedBlock(
        stream_seed=seed,
        block_index=0,
        bob=bob,
        high=high,
        low=low,
        u1=u1,
        u2=u2,
        labels=labels,
        label_bits=_l2b(labels),
    )


def literal_wilson(successes: int, total: int, z: float = 1.6448536269514722) -> float:
    """Independent literal one-sided Wilson lower bound (no shared helper)."""
    if total == 0:
        return 0.0
    p = successes / total
    denom = 1.0 + z * z / total
    center = p + z * z / (2.0 * total)
    margin = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total))
    return max(0.0, (center - margin) / denom)


def test_p8_grid_complete_35_configs():
    assert tr.FROZEN_K1_GRID == (8, 10, 12, 16, 24, 32, 45)
    assert tr.FROZEN_K2_GRID == (80, 94, 110, 125, 140)
    grid = tr.screen_grid()
    assert len(grid) == 35 == tr.FROZEN_NCONFIGS
    assert len(set(grid)) == 35
    assert {k1 for k1, _ in grid} == set(tr.FROZEN_K1_GRID)
    assert {k2 for _, k2 in grid} == set(tr.FROZEN_K2_GRID)
    assert grid[0] == (8, 80) and grid[1] == (8, 94) and grid[-1] == (45, 140)
    for k1 in tr.FROZEN_K1_GRID:
        for k2 in tr.FROZEN_K2_GRID:
            assert (k1, k2) in grid


def test_p8_wilson_screen_boundary_and_equivalence():
    assert tr.WILSON_MIN == 0.95
    assert abs(tr.WILSON_Z - 1.6448536269514722) == 0.0
    assert tr.SCREEN_EXACT_MIN == 188 and tr.FROZEN_SCREEN_TOTAL == 192
    assert tr.CONFIRM_EXACT_MIN == 618 and tr.FROZEN_CONFIRM_TOTAL == 640
    low = tr.screen_eligibility(187, 192)
    high = tr.screen_eligibility(188, 192)
    assert low["eligible"] is False and low["count_rule_188_of_192"] is False
    assert high["eligible"] is True and high["count_rule_188_of_192"] is True
    assert abs(low["wilson_lower_bound"] - literal_wilson(187, 192)) < 1e-12
    assert abs(high["wilson_lower_bound"] - literal_wilson(188, 192)) < 1e-12
    assert low["wilson_lower_bound"] < 0.95 <= high["wilson_lower_bound"]
    # Independently verify the frozen equivalence over the full 0..192 range.
    for exact in range(193):
        elig = tr.screen_eligibility(exact, 192)
        assert elig["eligible"] == (exact >= 188), f"screen equivalence breaks at {exact}"
        assert elig["wilson_count_agree"] is True
        assert abs(elig["wilson_lower_bound"] - literal_wilson(exact, 192)) < 1e-12
    # Same check for the CONFIRM shape used by the confirm gates.
    for exact in range(641):
        lb = tr.wilson_lower_bound(exact, 640, z=tr.WILSON_Z)
        assert (lb >= 0.95) == (exact >= 618), f"confirm equivalence breaks at {exact}"
        assert abs(lb - literal_wilson(exact, 640)) < 1e-12
    assert_raises_match(ValueError, "must not exceed", tr.screen_eligibility, 193, 192)


def test_p8_selection_deterministic_ties_and_empty():
    def cfg(k1, k2, eligible=True):
        return {"k1": k1, "k2": k2, "eligible": eligible}

    # Real grid ties on K1+K2: (10,94)=104 vs (24,80)=104 -> smaller K1 wins.
    tie = [cfg(24, 80), cfg(10, 94), cfg(45, 140)]
    assert (tr.select_point(tie)["k1"], tr.select_point(tie)["k2"]) == (10, 94)
    # (16,110)=126 vs (32,94)=126 -> smaller K1 wins.
    tie2 = [cfg(32, 94), cfg(8, 140), cfg(16, 110)]
    assert (tr.select_point(tie2)["k1"], tr.select_point(tie2)["k2"]) == (16, 110)
    # Global minimum over the full eligible grid is (8,80).
    full = [cfg(k1, k2) for k1, k2 in tr.screen_grid()]
    assert (tr.select_point(full)["k1"], tr.select_point(full)["k2"]) == (8, 80)
    # Ineligible points never compete, even at the minimum disclosure.
    assert tr.select_point([cfg(8, 80, eligible=False), cfg(45, 140)])["k1"] == 45
    # No eligible point -> None (the valid negative path, not BLOCKED).
    assert tr.select_point([cfg(8, 80, eligible=False)]) is None
    assert tr.select_point([]) is None


def test_p8_stream_isolation_and_disjointness():
    assert tr.FROZEN_SCREEN_SEEDS == (2026091680, 2026091681, 2026091682)
    assert tr.FROZEN_CONFIRM_SEEDS == (
        2026091690,
        2026091691,
        2026091692,
        2026091693,
        2026091694,
    )
    assert set(tr.FROZEN_SCREEN_SEEDS).isdisjoint(tr.FROZEN_CONFIRM_SEEDS)
    assert tr.FROZEN_SCREEN_BLOCKS == 64 and tr.FROZEN_CONFIRM_BLOCKS == 128
    assert tr.PUBLIC_TAG_MASTER_OFFSET == 10000
    assert_raises_match(
        ValueError, "disjoint", tr._check_seed_lists, (TEST_SEED_A,), (TEST_SEED_A,)
    )
    assert_raises_match(
        ValueError, "distinct", tr._check_seed_lists, (TEST_SEED_A, TEST_SEED_A), (TEST_SEED_B,)
    )
    tr._check_seed_lists((TEST_SEED_A,), (TEST_SEED_B,))
    # Phase domain separation: identical master/arm/block, different phase.
    screen_bits = tr.arm_seed_bits("screen", "empirical", 0, master=TEST_SEED_C)
    confirm_bits = tr.arm_seed_bits("confirm", "empirical", 0, master=TEST_SEED_C)
    assert screen_bits.shape == (2623,) and not np.array_equal(screen_bits, confirm_bits)
    assert not np.array_equal(
        screen_bits, tr.arm_seed_bits("screen", "bec", 0, master=TEST_SEED_C)
    )
    assert not np.array_equal(
        screen_bits, tr.arm_seed_bits("screen", "empirical", 1, master=TEST_SEED_C)
    )
    assert_raises_match(
        tr.SeedPrefixError, "phase", tr.arm_seed_bits, "dev", "empirical", 0, master=1
    )
    assert_raises_match(
        tr.SeedPrefixError, "arm", tr.arm_seed_bits, "screen", "operational", 0, master=1
    )


def canned_exact_arm(phase, arm, k1, k2):
    return tr.RateArmResult(
        phase=phase,
        arm=arm,
        outcome="exact",
        exact=True,
        label_match=True,
        tag_pass=True,
        l1_provenance="PRIOR_ONLY",
        l2_provenance="CANDIDATE_CONDITIONED",
        l1_executed=True,
        l1_decode_failed=False,
        l2_invoked=True,
        l2_skipped_by_l1_failure=False,
        l2_decode_failed=False,
        tag_invoked=True,
        key_dependent_bits=5 * (k1 + k2) + 64,
        public_control_bits=2623,
        nonfinite=False,
        truth_leak_violation=False,
        l1_error_type=None,
        l2_error_type=None,
        wall_s=0.0,
        k1=k1,
        k2=k2,
    )


def test_p8_shared_block_identity_selected_only_and_pairing():
    counts = injected_counts(TEST_SEED_D)
    exp = expected_seam(counts)
    orders = injected_orders(TEST_SEED_E)
    seen = []

    def spy_run_rate_arm(**kwargs):
        seen.append(kwargs)
        return canned_exact_arm(
            kwargs["phase"], kwargs["arm"], kwargs["k1"], kwargs["k2"]
        )

    root = Path(tempfile.mkdtemp()) / "shared"
    with patched(tr, "run_rate_arm", spy_run_rate_arm):
        run = tr.run_target_rate(
            counts=counts,
            orders=orders,
            screen_seeds=(TEST_SEED_F,),
            screen_blocks=52,
            confirm_seeds=(TEST_SEED_G,),
            confirm_blocks=2,
            out_dir=str(root),
            expected_entropies=exp,
        )
    assert len(run.screen_configs) == 35
    # Shared-block identity: every grid point saw the identical block objects.
    by_position = {}
    for call in seen:
        if call["phase"] != "screen":
            continue
        key = (call["block"].stream_seed, call["block"].block_index)
        by_position.setdefault(key, set()).add(id(call["block"]))
    assert len(by_position) == 52
    assert all(len(ids) == 1 for ids in by_position.values())
    screen_calls = [c for c in seen if c["phase"] == "screen"]
    assert len(screen_calls) == 35 * 52
    # All-exact test shape selects the lexicographic minimum (8,80).
    assert run.selection is not None
    assert (run.selection["k1"], run.selection["k2"]) == (8, 80)
    assert run.summary["selected"] == {"k1": 8, "k2": 80}
    # Selected-only confirmation: only (8,80) confirmed, both arms, same K.
    confirm_calls = [c for c in seen if c["phase"] == "confirm"]
    assert len(confirm_calls) == 2 * 2
    assert all((c["k1"], c["k2"]) == (8, 80) for c in confirm_calls)
    assert {c["arm"] for c in confirm_calls} == {"empirical", "bec"}
    assert all(c["master"] == TEST_SEED_G + 10000 for c in confirm_calls)
    emp_orders = [c for c in confirm_calls if c["arm"] == "empirical"]
    bec_orders = [c for c in confirm_calls if c["arm"] == "bec"]
    assert all(np.array_equal(c["l1_order"], orders["l1_empirical"]) for c in emp_orders)
    assert all(np.array_equal(c["l2_order"], orders["l2_empirical"]) for c in emp_orders)
    assert all(np.array_equal(c["l1_order"], orders["l1_bec"]) for c in bec_orders)
    assert all(np.array_equal(c["l2_order"], orders["l2_bec"]) for c in bec_orders)
    # Empirical/BEC same-K pairing is persisted per confirm block.
    selection_file = json.loads(
        (root / "selection_and_confirmation_records.json").read_text(encoding="utf-8")
    )
    assert selection_file["selected"] == {"k1": 8, "k2": 80}
    assert selection_file["confirm"]["k1"] == 8 and selection_file["confirm"]["k2"] == 80
    assert len(selection_file["confirm"]["blocks"]) == 2
    for record in selection_file["confirm"]["blocks"]:
        assert record["empirical"]["k1"] == record["bec"]["k1"] == 8
        assert record["empirical"]["k2"] == record["bec"]["k2"] == 80
        assert record["cell"] in tr.CELLS
    # SCREEN/CONFIRM stream isolation holds end to end.
    screen_streams = {
        r["stream_seed"] for c in run.screen_configs for r in c["blocks"]
    }
    confirm_streams = {r["stream_seed"] for r in run.confirm_records}
    assert screen_streams == {TEST_SEED_F} and confirm_streams == {TEST_SEED_G}
    assert screen_streams.isdisjoint(confirm_streams)
    # Test shape cannot claim: integrity passes but the label stays non-candidate.
    assert run.summary["shape_is_frozen"] is False
    assert run.summary["integrity_all_pass"] is True
    assert run.summary["outcome_label"] == "TARGET_EMPIRICAL_RATE_POINT_NOT_CONFIRMED"
    assert sorted(p.name for p in root.iterdir()) == sorted(tr.OUTPUT_FILES)


def test_p8_screen_no_eligible_point_path():
    counts = injected_counts(TEST_SEED_F)
    exp = expected_seam(counts)
    orders = injected_orders(TEST_SEED_G)
    n = 256

    def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        return FakeSC(np.zeros(n, dtype=np.int64))

    root = Path(tempfile.mkdtemp()) / "negative"
    with patched(tr, "sc_decode", fake_sc):
        run = tr.run_target_rate(
            counts=counts,
            orders=orders,
            screen_seeds=(TEST_SEED_A,),
            screen_blocks=2,
            confirm_seeds=(TEST_SEED_B,),
            confirm_blocks=2,
            out_dir=str(root),
            expected_entropies=exp,
        )
    assert run.selection is None
    assert run.confirm_results == [] and run.confirm_records == []
    assert run.summary["outcome_label"] == "TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT"
    assert run.summary["integrity_all_pass"] is True
    assert run.summary["eligible_points"] == []
    screen_file = json.loads((root / "screen_records.json").read_text(encoding="utf-8"))
    assert screen_file["n_configs"] == 35
    assert all(len(c["blocks"]) == 2 for c in screen_file["configs"])
    assert all(c["eligible"] is False for c in screen_file["configs"])
    selection_file = json.loads(
        (root / "selection_and_confirmation_records.json").read_text(encoding="utf-8")
    )
    assert selection_file["selected"] is None
    assert selection_file["confirm"] == {"executed": False}
    assert sorted(p.name for p in root.iterdir()) == sorted(tr.OUTPUT_FILES)


def test_p8_truth_isolation():
    p1, p2 = tiny_p1_p2()
    block = tiny_block()
    before = {name: np.array(getattr(block, name), copy=True) for name in ("bob", "high", "low")}

    def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        return FakeSC(np.zeros(8, dtype=np.int64))

    with patched(tr, "sc_decode", fake_sc):
        arm = tr.run_rate_arm(
            phase="screen",
            arm="empirical",
            block=block,
            field=FIELD,
            p1_table=p1,
            p2_table=p2,
            l1_order=np.arange(8, dtype=np.int64),
            l2_order=np.arange(8, dtype=np.int64)[::-1],
            k1=3,
            k2=4,
            n=8,
            master=TEST_SEED_D,
            tag_fn=constant_tag,
        )
    # The caller's block arrays are never mutated; truth only travelled via copies.
    for name, snapshot in before.items():
        assert np.array_equal(np.asarray(getattr(block, name)), snapshot)
    assert arm.truth_leak_violation is False
    # A broken sentinel is caught by the integrity gate, not hidden.
    counts = injected_counts(TEST_SEED_G)
    exp = expected_seam(counts)
    root = Path(tempfile.mkdtemp()) / "leak"
    with patched(tr, "_truth_isolation_sentinel", lambda *args, **kwargs: False):
        with patched(tr, "sc_decode", fake_sc_small()):
            run = tr.run_target_rate(
                counts=counts,
                orders=injected_orders(TEST_SEED_H),
                screen_seeds=(TEST_SEED_A,),
                screen_blocks=1,
                confirm_seeds=(TEST_SEED_B,),
                confirm_blocks=1,
                out_dir=str(root),
                expected_entropies=exp,
            )
    assert run.summary["integrity"]["truth_leak_zero"] is False
    assert run.summary["integrity_all_pass"] is False
    assert run.summary["outcome_label"] == "BLOCKED"
    assert run.summary["blocked_detail"] == "BLOCKED(truth_leak_zero)"


def fake_sc_small():
    def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        n = int(np.asarray(logp).shape[0])
        return FakeSC(np.zeros(n, dtype=np.int64))

    return fake_sc


def test_p8_buckets_mutually_exclusive():
    assert tr.OUTCOMES == (
        "exact",
        "undetected",
        "verify_failed",
        "decode_failed",
        "resource_abort",
    )
    assert (
        tr.classify_outcome(l1_failed=False, l2_failed=False, tag_pass=True, label_match=True)
        == "exact"
    )
    assert (
        tr.classify_outcome(l1_failed=False, l2_failed=False, tag_pass=True, label_match=False)
        == "undetected"
    )
    assert (
        tr.classify_outcome(l1_failed=False, l2_failed=False, tag_pass=False, label_match=True)
        == "verify_failed"
    )
    assert (
        tr.classify_outcome(l1_failed=True, l2_failed=False, tag_pass=True, label_match=True)
        == "decode_failed"
    )
    assert (
        tr.classify_outcome(l1_failed=False, l2_failed=True, tag_pass=True, label_match=False)
        == "decode_failed"
    )
    assert tr.classify_pair(True, True) == "both_exact"
    assert tr.classify_pair(True, False) == "empirical_only"
    assert tr.classify_pair(False, True) == "bec_only"
    assert tr.classify_pair(False, False) == "neither"
    abort = tr._abort_arm("screen", "empirical", k1=8, k2=80)
    assert tr._arm_record_consistent(abort, n=256) is True
    # undetected must never carry a matching label; verify_failed needs its tag.
    bad_undetected = tr.RateArmResult(
        phase="screen",
        arm="empirical",
        outcome="undetected",
        exact=False,
        label_match=True,
        tag_pass=True,
        l1_provenance="PRIOR_ONLY",
        l2_provenance="CANDIDATE_CONDITIONED",
        l1_executed=True,
        l1_decode_failed=False,
        l2_invoked=True,
        l2_skipped_by_l1_failure=False,
        l2_decode_failed=False,
        tag_invoked=True,
        key_dependent_bits=5 * (8 + 80) + 64,
        public_control_bits=2623,
        nonfinite=False,
        truth_leak_violation=False,
        l1_error_type=None,
        l2_error_type=None,
        wall_s=0.0,
        k1=8,
        k2=80,
    )
    assert tr._arm_record_consistent(bad_undetected, n=256) is False
    full = canned_exact_arm("confirm", "bec", 8, 80)
    assert tr._arm_record_consistent(full, n=256) is True


def test_p8_accounting_partial_full_and_recount():
    p1, p2 = tiny_p1_p2()
    block = tiny_block(n=8, seed=TEST_SEED_E)
    order = np.arange(8, dtype=np.int64)
    k1, k2 = 3, 4

    def run_with(mode):
        calls = {"n": 0}

        def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
            calls["n"] += 1
            if mode == "l1-fail" or (mode == "l2-fail" and calls["n"] == 2):
                raise RuntimeError("injected SC failure")
            return FakeSC(np.zeros(8, dtype=np.int64))

        with patched(tr, "sc_decode", fake_sc):
            arm = tr.run_rate_arm(
                phase="screen",
                arm="empirical",
                block=block,
                field=FIELD,
                p1_table=p1,
                p2_table=p2,
                l1_order=order,
                l2_order=order,
                k1=k1,
                k2=k2,
                n=8,
                master=TEST_SEED_F,
                tag_fn=constant_tag,
            )
        return arm

    l1_fail = run_with("l1-fail")
    assert l1_fail.outcome == "decode_failed" and l1_fail.tag_invoked is False
    assert l1_fail.l2_invoked is False and l1_fail.l2_skipped_by_l1_failure is True
    assert l1_fail.key_dependent_bits == 5 * k1 and l1_fail.public_control_bits == 0
    l2_fail = run_with("l2-fail")
    assert l2_fail.outcome == "decode_failed" and l2_fail.tag_invoked is False
    assert l2_fail.l2_invoked is True
    assert l2_fail.key_dependent_bits == 5 * (k1 + k2) and l2_fail.public_control_bits == 0
    full = run_with("ok")
    assert full.tag_invoked is True
    assert full.key_dependent_bits == 5 * (k1 + k2) + 64
    assert full.public_control_bits == 10 * 8 + 63
    # Independent literal recount over the emitted events matches exactly.
    events = (
        tr.block_events("screen", 7, 0, l1_fail, n=8)
        + tr.block_events("screen", 7, 1, l2_fail, n=8)
        + tr.block_events("screen", 7, 2, full, n=8)
    )
    recount = tr.recount_events(events)
    assert recount["key_dependent_bits"] == (
        l1_fail.key_dependent_bits + l2_fail.key_dependent_bits + full.key_dependent_bits
    )
    assert recount["public_control_bits"] == full.public_control_bits
    assert recount["tag_invocations"] == 1
    assert recount["by_phase"]["screen"]["tag_invocations"] == 1
    assert recount["by_arm"]["empirical"]["tag_invocations"] == 1
    assert recount["event_types"] == {"l1_disclosure": 3, "l2_disclosure": 2, "verification_tag": 1}
    tampered = [dict(event) for event in events]
    tampered[0]["key_dependent_bits"] += 5
    assert tr.recount_events(tampered)["key_dependent_bits"] == recount["key_dependent_bits"] + 5
    wrong = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    wrong_phase = {phase: dict(wrong) for phase in tr.PHASES}
    wrong_arm = {arm: dict(wrong) for arm in tr.ARMS}
    assert tr._transcript_mismatches(wrong, wrong_phase, wrong_arm, recount)
    assert_raises_match(
        ValueError, "phase/arm-tagged", tr.recount_events, [{"event_id": "block-0-x"}]
    )


def test_p8_orders_identity_refusals_before_any_npz_access():
    import copy

    rng = np.random.default_rng(TEST_SEED_G)

    def make_layers():
        return {
            "l1": {
                "pooled": {"order": rng.permutation(256).tolist()},
                "bec": {"epsilon": 0.05, "order": analytic_order(0.05, 256).tolist()},
            },
            "l2": {
                "pooled": {"order": rng.permutation(256).tolist()},
                "bec": {"epsilon": 0.155, "order": analytic_order(0.155, 256).tolist()},
            },
        }

    layers = make_layers()
    test_sha = tr._canonical_sha(layers)
    good = {"orders_sha256": test_sha, "layers": layers}
    # The documented test seam validates the full rule set: identity,
    # payload digest, permutations and BEC surrogates.
    loaded = tr.validate_orders_doc(good, expected_sha=test_sha)
    assert loaded["sha256"] == test_sha
    for key in ("l1_empirical", "l2_empirical", "l1_bec", "l2_bec"):
        assert loaded[key].shape == (256,)
    assert np.array_equal(loaded["l1_bec"], analytic_order(0.05, 256))
    assert loaded["eps_l1"] == 0.05 and loaded["eps_l2"] == 0.155

    assert tr.is_valid_permutation(layers["l1"]["pooled"]["order"]) is True
    assert tr.is_valid_permutation([0] * 256) is False
    assert tr.is_valid_permutation([0, 1, 2]) is False
    assert tr.is_valid_permutation("not-an-order") is False

    tampered_sha = copy.deepcopy(good)
    tampered_sha["orders_sha256"] = "0" * 64
    assert_raises_match(
        tr.OrdersIdentityError,
        "identity mismatch",
        tr.validate_orders_doc,
        tampered_sha,
        expected_sha=test_sha,
    )
    mutated = copy.deepcopy(good)
    mutated["layers"]["l1"]["pooled"]["order"] = list(
        reversed(mutated["layers"]["l1"]["pooled"]["order"])
    )
    assert_raises_match(
        tr.OrdersIdentityError,
        "digest mismatch",
        tr.validate_orders_doc,
        mutated,
        expected_sha=test_sha,
    )
    dup = copy.deepcopy(good)
    dup["layers"]["l1"]["pooled"]["order"] = [0] * 256
    dup["orders_sha256"] = tr._canonical_sha(dup["layers"])
    assert_raises_match(
        tr.OrdersIdentityError,
        "256-permutation",
        tr.validate_orders_doc,
        dup,
        expected_sha=dup["orders_sha256"],
    )
    bad_bec = copy.deepcopy(good)
    bad_bec["layers"]["l2"]["bec"]["order"] = analytic_order(0.05, 256).tolist()
    bad_bec["orders_sha256"] = tr._canonical_sha(bad_bec["layers"])
    assert_raises_match(
        tr.OrdersIdentityError,
        "surrogate",
        tr.validate_orders_doc,
        bad_bec,
        expected_sha=bad_bec["orders_sha256"],
    )
    assert_raises_match(
        tr.OrdersIdentityError, "JSON object", tr.validate_orders_doc, [1, 2, 3]
    )

    # File level: production enforces the frozen digest, so a self-consistent
    # synthetic file is still refused; a wrong recorded digest is refused too.
    sandbox = Path(tempfile.mkdtemp())
    synthetic_path = sandbox / "synthetic.json"
    synthetic_path.write_text(json.dumps(good), encoding="utf-8")
    assert_raises_match(
        tr.OrdersIdentityError,
        "identity mismatch",
        tr.load_construction_orders,
        synthetic_path,
    )
    tampered_path = sandbox / "tampered.json"
    tampered_path.write_text(json.dumps(tampered_sha), encoding="utf-8")
    assert_raises_match(
        tr.OrdersIdentityError, "identity mismatch", tr.load_construction_orders, tampered_path
    )
    assert_raises_match(
        tr.OrdersIdentityError, "not found", tr.load_construction_orders, sandbox / "absent.json"
    )

    def forbidden_loader(*args, **kwargs):
        raise AssertionError("NPZ loader must not run for orders refusals")

    with patched(tr, "load_v25_channel_counts", forbidden_loader):
        assert_raises_match(
            tr.OrdersIdentityError,
            "identity mismatch",
            tr.load_construction_orders,
            tampered_path,
        )
        # The runner refuses orders-identity before the NPZ content open too.
        assert_raises_match(
            tr.OrdersIdentityError,
            "identity mismatch",
            tr.run_target_rate,
            counts_path=str(sandbox / "fake.npz"),
            orders_path=str(tampered_path),
            out_dir=str(sandbox / "never"),
        )


def test_p8_cli_frozen_flags_and_refusals():
    assert tr.FROZEN_SCREEN_SEEDS == (2026091680, 2026091681, 2026091682)
    assert tr.FROZEN_CONFIRM_SEEDS == (
        2026091690,
        2026091691,
        2026091692,
        2026091693,
        2026091694,
    )
    assert tr.EXPECTED_ORDERS_SHA == "8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104"
    assert tr.EXPECTED_NPZ_BYTES == 25166822
    assert tr.EXPECTED_H1 == 0.02428054681872374
    assert tr.EXPECTED_H2 == 0.7767572780789994
    assert tr.EXPECTED_TOTAL == 0.8010378248977232
    assert tr.SCREEN_EXACT_MIN == 188 and tr.CONFIRM_EXACT_MIN == 618
    assert tr.OUTPUT_FILES == (
        "frozen_plan.json",
        "screen_records.json",
        "selection_and_confirmation_records.json",
        "transcript_accounting.json",
        "report.md",
    )
    assert "--orders" in tr.FROZEN_COMMAND and "--k1-grid" in tr.FROZEN_COMMAND
    assert "--screen-seeds" in tr.FROZEN_COMMAND and "--confirm-seeds" in tr.FROZEN_COMMAND
    for seed in TEST_SEEDS:
        assert seed not in tr.FROZEN_SCREEN_SEEDS and seed not in tr.FROZEN_CONFIRM_SEEDS

    parser = tr.build_parser()
    by_flag = {
        "--counts": ["x.npz"],
        "--source": ["1M"],
        "--orders": ["o.json"],
        "--n": ["256"],
        "--floor": ["1e-15"],
        "--screen-seeds": ["2026091680", "2026091681", "2026091682"],
        "--screen-blocks": ["64"],
        "--k1-grid": ["8", "10", "12", "16", "24", "32", "45"],
        "--k2-grid": ["80", "94", "110", "125", "140"],
        "--confirm-seeds": ["2026091690", "2026091691", "2026091692", "2026091693", "2026091694"],
        "--confirm-blocks": ["128"],
        "--out-dir": ["example_root"],
    }
    assert list(by_flag) == [
        "--counts", "--source", "--orders", "--n", "--floor", "--screen-seeds",
        "--screen-blocks", "--k1-grid", "--k2-grid", "--confirm-seeds",
        "--confirm-blocks", "--out-dir",
    ]
    frozen_argv = []
    for flag, values in by_flag.items():
        frozen_argv.append(flag)
        frozen_argv.extend(values)
    args = parser.parse_args(frozen_argv)
    assert args.n == 256 and args.floor == 1e-15 and args.source == "1M"
    assert tuple(args.screen_seeds) == tr.FROZEN_SCREEN_SEEDS
    assert tuple(args.confirm_seeds) == tr.FROZEN_CONFIRM_SEEDS
    assert tuple(args.k1_grid) == tr.FROZEN_K1_GRID and tuple(args.k2_grid) == tr.FROZEN_K2_GRID
    for drop in by_flag:
        reduced = []
        for flag, values in by_flag.items():
            if flag != drop:
                reduced.append(flag)
                reduced.extend(values)
        assert_raises_match(SystemExit, "", parser.parse_args, reduced)

    def forbidden_loader(*args, **kwargs):
        raise AssertionError("loader must not run before the refusals")

    sandbox = Path(tempfile.mkdtemp())
    existing = sandbox / "exists"
    existing.mkdir()
    never = sandbox / "never"
    with patched(tr, "load_v25_channel_counts", forbidden_loader):
        assert_raises_match(
            FileExistsError,
            "refusing to overwrite",
            tr.run_target_rate,
            counts_path=str(sandbox / "fake.npz"),
            orders_path=str(sandbox / "o.json"),
            out_dir=str(existing),
        )
        assert tr.main(
            [
                "--counts", str(sandbox / "fake.npz"),
                "--source", "1M",
                "--orders", str(sandbox / "o.json"),
                "--n", "256", "--floor", "1e-15",
                "--screen-seeds", "2026091680", "2026091681", "2026091682",
                "--screen-blocks", "64",
                "--k1-grid", "8", "10", "12", "16", "24", "32", "45",
                "--k2-grid", "80", "94", "110", "125", "140",
                "--confirm-seeds", "2026091690", "2026091691", "2026091692",
                "2026091693", "2026091694",
                "--confirm-blocks", "128",
                "--out-dir", str(existing),
            ]
        ) == 2
        # Wrong grid and overlapping streams are refused before any content open.
        assert tr.main(
            [
                "--counts", str(sandbox / "fake.npz"),
                "--source", "1M",
                "--orders", str(sandbox / "o.json"),
                "--n", "256", "--floor", "1e-15",
                "--screen-seeds", "2026091680", "2026091681", "2026091682",
                "--screen-blocks", "64",
                "--k1-grid", "8", "10",
                "--k2-grid", "80", "94", "110", "125", "140",
                "--confirm-seeds", "2026091690", "2026091691", "2026091692",
                "2026091693", "2026091694",
                "--confirm-blocks", "128",
                "--out-dir", str(never),
            ]
        ) == 2
        assert tr.main(
            [
                "--counts", str(sandbox / "fake.npz"),
                "--source", "1M",
                "--orders", str(sandbox / "o.json"),
                "--n", "256", "--floor", "1e-15",
                "--screen-seeds", "2026091690",
                "--screen-blocks", "64",
                "--k1-grid", "8", "10", "12", "16", "24", "32", "45",
                "--k2-grid", "80", "94", "110", "125", "140",
                "--confirm-seeds", "2026091690",
                "--confirm-blocks", "128",
                "--out-dir", str(never),
            ]
        ) == 2
    assert not never.exists()


def test_p8_no_forbidden_markers_or_production_invocation():
    import re

    source = Path(tr.__file__).read_text(encoding="utf-8")
    lowered = source.lower()
    for marker in FORBIDDEN_MODULE_MARKERS:
        assert marker not in lowered, f"forbidden marker {marker!r} in target_rate.py"
    for match in re.finditer(r"np\.random\.([A-Za-z_]+)\s*\(", source):
        assert match.group(1) == "default_rng", f"global RNG use: {match.group(0)}"
    assert "open(" not in source
    own = Path(__file__).read_text(encoding="utf-8")
    assert ("channel_counts" + ".npz") not in own
    assert ("rate_screen" + "_confirm") not in own
    for seed in tr.FROZEN_SCREEN_SEEDS + tr.FROZEN_CONFIRM_SEEDS:
        assert f"default_rng({seed})" not in own
        assert f"screen_seeds=({seed}" not in own
        assert f"confirm_seeds=({seed}" not in own

    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not run from injected tests")

    counts = injected_counts(TEST_SEED_A)
    exp = expected_seam(counts)
    injected_root = Path(tempfile.mkdtemp()) / "injected"
    with patched(tr, "load_v25_channel_counts", forbidden_loader):
        injected = tr.run_target_rate(
            counts=counts,
            orders=injected_orders(TEST_SEED_B),
            screen_seeds=(TEST_SEED_C,),
            screen_blocks=1,
            confirm_seeds=(TEST_SEED_D,),
            confirm_blocks=1,
            out_dir=str(injected_root),
            expected_entropies=exp,
            tag_fn=constant_tag,
        )
    assert injected.summary["input_mode"] == "injected_counts"
    assert injected.summary["integrity"]["attempt_read_accounting_exact"] is True
    assert injected.summary["attempt_read_accounting"]["open_count"] == 0
    assert sorted(p.name for p in injected_root.iterdir()) == sorted(tr.OUTPUT_FILES)

    empty = Path(tempfile.mkdtemp())
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    code = (
        "import comparison_bench.src.comparison_bench.formal_ir.nbpolar."
        "target_rate as t; "
        "assert t.FROZEN_NCONFIGS == 35 and t.OUTPUT_FILES[0] == 'frozen_plan.json' "
        "and t.EXPECTED_ORDERS_SHA.startswith('8ec69034')"
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


# ---- Phase 4-P9 lower-rate boundary delta tests.
#
# Fresh test-local seeds >= 2026091730 only; the frozen P9 SCREEN/CONFIRM
# streams are read from the module constants and are never sampled here.
P9_TEST_SEED_A = 2026091730
P9_TEST_SEED_B = 2026091731
P9_TEST_SEED_C = 2026091732
P9_TEST_SEED_D = 2026091733
P9_TEST_SEED_E = 2026091734
P9_TEST_SEED_F = 2026091735
P9_TEST_SEED_G = 2026091736
P9_TEST_SEED_H = 2026091737
P9_TEST_SEED_I = 2026091738
P9_TEST_SEED_J = 2026091739
P9_TEST_SEEDS = (
    P9_TEST_SEED_A,
    P9_TEST_SEED_B,
    P9_TEST_SEED_C,
    P9_TEST_SEED_D,
    P9_TEST_SEED_E,
    P9_TEST_SEED_F,
    P9_TEST_SEED_G,
    P9_TEST_SEED_H,
    P9_TEST_SEED_I,
    P9_TEST_SEED_J,
)


def test_p9_grid_complete_56_configs():
    assert tr.P9_FROZEN_K1_GRID == (0, 2, 4, 6, 8, 12, 24, 45)
    assert tr.P9_FROZEN_K2_GRID == (0, 20, 40, 50, 60, 70, 80)
    assert tr.P9_FROZEN_NCONFIGS == 56
    assert tr.FROZEN_K1_GRID == (8, 10, 12, 16, 24, 32, 45)
    assert tr.FROZEN_NCONFIGS == 35
    grid = tr.screen_grid(tr.P9_FROZEN_K1_GRID, tr.P9_FROZEN_K2_GRID)
    assert len(grid) == 56
    assert len(set(grid)) == 56
    assert (0, 0) in grid
    assert (8, 80) in grid
    assert grid[0] == (0, 0) and grid[1] == (0, 20) and grid[-1] == (45, 80)
    assert {k1 for k1, _ in grid} == set(tr.P9_FROZEN_K1_GRID)
    assert {k2 for _, k2 in grid} == set(tr.P9_FROZEN_K2_GRID)
    for k1 in tr.P9_FROZEN_K1_GRID:
        for k2 in tr.P9_FROZEN_K2_GRID:
            assert (k1, k2) in grid


def test_p9_zero_k_behavior():
    p1, p2 = tiny_p1_p2()
    block = tiny_block(n=8, seed=P9_TEST_SEED_C)

    def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        return FakeSC(np.zeros(8, dtype=np.int64))

    with patched(tr, "sc_decode", fake_sc):
        zero = tr.run_rate_arm(
            phase="screen",
            arm="empirical",
            block=block,
            field=FIELD,
            p1_table=p1,
            p2_table=p2,
            l1_order=np.arange(8, dtype=np.int64),
            l2_order=np.arange(8, dtype=np.int64),
            k1=0,
            k2=0,
            n=8,
            master=P9_TEST_SEED_D,
            tag_fn=constant_tag,
            gate_id=tr.P9_GATE_ID,
        )
    assert zero.tag_invoked is True and zero.l2_invoked is True
    assert zero.key_dependent_bits == 64
    assert zero.public_control_bits == 10 * 8 + 63
    assert tr._arm_record_consistent(zero, n=8) is True
    events = tr.block_events("screen", 7, 0, zero, n=8, gate_id=tr.P9_GATE_ID)
    assert [e["event_type"] for e in events] == [
        "l1_disclosure",
        "l2_disclosure",
        "verification_tag",
    ]
    assert events[0]["key_dependent_bits"] == 0
    assert events[1]["key_dependent_bits"] == 0
    assert events[2]["key_dependent_bits"] == 64
    with patched(tr, "sc_decode", fake_sc):
        k1only = tr.run_rate_arm(
            phase="screen",
            arm="empirical",
            block=block,
            field=FIELD,
            p1_table=p1,
            p2_table=p2,
            l1_order=np.arange(8, dtype=np.int64),
            l2_order=np.arange(8, dtype=np.int64),
            k1=0,
            k2=4,
            n=8,
            master=P9_TEST_SEED_D,
            tag_fn=constant_tag,
            gate_id=tr.P9_GATE_ID,
        )
        k2only = tr.run_rate_arm(
            phase="screen",
            arm="empirical",
            block=block,
            field=FIELD,
            p1_table=p1,
            p2_table=p2,
            l1_order=np.arange(8, dtype=np.int64),
            l2_order=np.arange(8, dtype=np.int64),
            k1=3,
            k2=0,
            n=8,
            master=P9_TEST_SEED_D,
            tag_fn=constant_tag,
            gate_id=tr.P9_GATE_ID,
        )
    assert k1only.key_dependent_bits == 5 * 4 + 64
    assert k2only.key_dependent_bits == 5 * 3 + 64
    ev1 = tr.block_events("screen", 7, 1, k1only, n=8, gate_id=tr.P9_GATE_ID)
    assert ev1[0]["key_dependent_bits"] == 0 and ev1[1]["key_dependent_bits"] == 5 * 4


def test_p9_wilson_screen_boundary_and_equivalence():
    assert tr.WILSON_MIN == 0.95
    assert tr.SCREEN_EXACT_MIN == 188 and tr.FROZEN_SCREEN_TOTAL == 192
    assert tr.CONFIRM_EXACT_MIN == 618 and tr.FROZEN_CONFIRM_TOTAL == 640
    low = tr.screen_eligibility(187, 192)
    high = tr.screen_eligibility(188, 192)
    assert low["eligible"] is False and high["eligible"] is True
    assert low["wilson_lower_bound"] < 0.95 <= high["wilson_lower_bound"]
    for exact in range(193):
        elig = tr.screen_eligibility(exact, 192)
        assert elig["eligible"] == (exact >= 188)
        assert abs(elig["wilson_lower_bound"] - literal_wilson(exact, 192)) < 1e-12
    for exact in range(641):
        lb = tr.wilson_lower_bound(exact, 640, z=tr.WILSON_Z)
        assert (lb >= 0.95) == (exact >= 618)


def test_p9_selection_deterministic_ties_and_empty():
    def cfg(k1, k2, eligible=True):
        return {"k1": k1, "k2": k2, "eligible": eligible}

    tie = [cfg(24, 20), cfg(4, 40), cfg(45, 80)]
    assert (tr.select_point(tie)["k1"], tr.select_point(tie)["k2"]) == (4, 40)
    tie2 = [cfg(12, 40), cfg(2, 50), cfg(45, 80)]
    assert (tr.select_point(tie2)["k1"], tr.select_point(tie2)["k2"]) == (2, 50)
    full = [cfg(k1, k2) for k1, k2 in tr.screen_grid(tr.P9_FROZEN_K1_GRID, tr.P9_FROZEN_K2_GRID)]
    assert (tr.select_point(full)["k1"], tr.select_point(full)["k2"]) == (0, 0)
    assert tr.select_point([cfg(0, 0, eligible=False), cfg(45, 80)])["k1"] == 45
    assert tr.select_point([cfg(0, 0, eligible=False)]) is None
    assert tr.select_point([]) is None


def test_p9_stream_isolation_and_prior_disjointness():
    assert tr.P9_FROZEN_SCREEN_SEEDS == (2026091710, 2026091711, 2026091712)
    assert tr.P9_FROZEN_CONFIRM_SEEDS == (
        2026091720,
        2026091721,
        2026091722,
        2026091723,
        2026091724,
    )
    assert set(tr.P9_FROZEN_SCREEN_SEEDS).isdisjoint(tr.P9_FROZEN_CONFIRM_SEEDS)
    assert set(tr.P9_FROZEN_SCREEN_SEEDS).isdisjoint(tr.P9_PRIOR_OFFICIAL_STREAMS)
    assert set(tr.P9_FROZEN_CONFIRM_SEEDS).isdisjoint(tr.P9_PRIOR_OFFICIAL_STREAMS)
    for seed in P9_TEST_SEEDS:
        assert seed not in tr.P9_FROZEN_SCREEN_SEEDS
        assert seed not in tr.P9_FROZEN_CONFIRM_SEEDS
        assert seed not in tr.FROZEN_SCREEN_SEEDS
        assert seed not in tr.FROZEN_CONFIRM_SEEDS
    assert_raises_match(
        ValueError, "disjoint", tr._check_seed_lists,
        (P9_TEST_SEED_A,), (P9_TEST_SEED_A,), tr.P9_GATE_ID,
    )
    assert_raises_match(
        ValueError, "prior official", tr._check_seed_lists,
        (2026091680,), (P9_TEST_SEED_B,), tr.P9_GATE_ID,
    )
    assert_raises_match(
        ValueError, "prior official", tr._check_seed_lists,
        (P9_TEST_SEED_A,), (2026091690,), tr.P9_GATE_ID,
    )
    tr._check_seed_lists((P9_TEST_SEED_A,), (P9_TEST_SEED_B,), tr.P9_GATE_ID)
    tr._check_seed_lists((P9_TEST_SEED_A,), (P9_TEST_SEED_B,))
    p9_bits = tr.arm_seed_bits("screen", "empirical", 0, master=P9_TEST_SEED_C, gate_id=tr.P9_GATE_ID)
    p8_bits = tr.arm_seed_bits("screen", "empirical", 0, master=P9_TEST_SEED_C, gate_id=tr.P8_GATE_ID)
    assert p9_bits.shape == (2623,) and not np.array_equal(p9_bits, p8_bits)
    assert not np.array_equal(
        p9_bits, tr.arm_seed_bits("confirm", "empirical", 0, master=P9_TEST_SEED_C, gate_id=tr.P9_GATE_ID)
    )
    assert not np.array_equal(
        p9_bits, tr.arm_seed_bits("screen", "bec", 0, master=P9_TEST_SEED_C, gate_id=tr.P9_GATE_ID)
    )


def test_p9_shared_block_identity_selected_only_and_pairing():
    counts = injected_counts(P9_TEST_SEED_D)
    exp = expected_seam(counts)
    orders = injected_orders(P9_TEST_SEED_E)
    seen = []

    def spy_run_rate_arm(**kwargs):
        seen.append(kwargs)
        return canned_exact_arm(kwargs["phase"], kwargs["arm"], kwargs["k1"], kwargs["k2"])

    root = Path(tempfile.mkdtemp()) / "shared9"
    with patched(tr, "run_rate_arm", spy_run_rate_arm):
        run = tr.run_target_rate(
            counts=counts,
            orders=orders,
            screen_seeds=(P9_TEST_SEED_F,),
            screen_blocks=52,
            k1_grid=list(tr.P9_FROZEN_K1_GRID),
            k2_grid=list(tr.P9_FROZEN_K2_GRID),
            confirm_seeds=(P9_TEST_SEED_G,),
            confirm_blocks=2,
            out_dir=str(root),
            expected_entropies=exp,
            gate_id=tr.P9_GATE_ID,
        )
    assert len(run.screen_configs) == 56
    by_position = {}
    for call in seen:
        if call["phase"] != "screen":
            continue
        key = (call["block"].stream_seed, call["block"].block_index)
        by_position.setdefault(key, set()).add(id(call["block"]))
        assert call["gate_id"] == tr.P9_GATE_ID
    assert len(by_position) == 52
    assert all(len(ids) == 1 for ids in by_position.values())
    assert len([c for c in seen if c["phase"] == "screen"]) == 56 * 52
    assert run.selection is not None
    assert (run.selection["k1"], run.selection["k2"]) == (0, 0)
    confirm_calls = [c for c in seen if c["phase"] == "confirm"]
    assert len(confirm_calls) == 2 * 2
    assert all((c["k1"], c["k2"]) == (0, 0) for c in confirm_calls)
    assert {c["arm"] for c in confirm_calls} == {"empirical", "bec"}
    assert run.summary["gate_id"] == tr.P9_GATE_ID
    assert run.summary["analysis"] == tr.P9_PROTOCOL_NAME
    assert run.plan["protocol"] == tr.P9_PROTOCOL_NAME
    selection_file = json.loads(
        (root / "selection_and_confirmation_records.json").read_text(encoding="utf-8")
    )
    assert selection_file["protocol"] == tr.P9_PROTOCOL_NAME
    assert selection_file["gate_id"] == tr.P9_GATE_ID
    assert selection_file["selected"] == {"k1": 0, "k2": 0}
    assert len(selection_file["confirm"]["blocks"]) == 2
    for record in selection_file["confirm"]["blocks"]:
        assert record["empirical"]["k1"] == record["bec"]["k1"] == 0
        assert record["empirical"]["k2"] == record["bec"]["k2"] == 0
        assert record["cell"] in tr.CELLS
    assert run.summary["shape_is_frozen"] is False
    assert run.summary["outcome_label"] == tr.P9_NOT_CONFIRMED_LABEL
    assert sorted(p.name for p in root.iterdir()) == sorted(tr.OUTPUT_FILES)


def test_p9_screen_no_eligible_point_path():
    counts = injected_counts(P9_TEST_SEED_F)
    exp = expected_seam(counts)
    orders = injected_orders(P9_TEST_SEED_G)
    n = 256

    def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        return FakeSC(np.zeros(n, dtype=np.int64))

    root = Path(tempfile.mkdtemp()) / "negative9"
    with patched(tr, "sc_decode", fake_sc):
        run = tr.run_target_rate(
            counts=counts,
            orders=orders,
            screen_seeds=(P9_TEST_SEED_A,),
            screen_blocks=2,
            k1_grid=list(tr.P9_FROZEN_K1_GRID),
            k2_grid=list(tr.P9_FROZEN_K2_GRID),
            confirm_seeds=(P9_TEST_SEED_B,),
            confirm_blocks=2,
            out_dir=str(root),
            expected_entropies=exp,
            gate_id=tr.P9_GATE_ID,
        )
    assert run.selection is None
    assert run.confirm_results == [] and run.confirm_records == []
    assert run.summary["outcome_label"] == tr.P9_NO_ELIGIBLE_LABEL
    assert run.summary["integrity_all_pass"] is True
    screen_file = json.loads((root / "screen_records.json").read_text(encoding="utf-8"))
    assert screen_file["n_configs"] == 56
    assert screen_file["protocol"] == tr.P9_PROTOCOL_NAME
    assert all(c["eligible"] is False for c in screen_file["configs"])
    selection_file = json.loads(
        (root / "selection_and_confirmation_records.json").read_text(encoding="utf-8")
    )
    assert selection_file["selected"] is None
    assert selection_file["confirm"] == {"executed": False}
    assert sorted(p.name for p in root.iterdir()) == sorted(tr.OUTPUT_FILES)


def test_p9_accounting_partial_full_and_recount_with_zero_k():
    p1, p2 = tiny_p1_p2()
    block = tiny_block(n=8, seed=P9_TEST_SEED_E)
    order = np.arange(8, dtype=np.int64)

    def run_with(mode, k1=3, k2=4):
        calls = {"n": 0}

        def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
            calls["n"] += 1
            if mode == "l1-fail" or (mode == "l2-fail" and calls["n"] == 2):
                raise RuntimeError("injected SC failure")
            return FakeSC(np.zeros(8, dtype=np.int64))

        with patched(tr, "sc_decode", fake_sc):
            arm = tr.run_rate_arm(
                phase="screen",
                arm="empirical",
                block=block,
                field=FIELD,
                p1_table=p1,
                p2_table=p2,
                l1_order=order,
                l2_order=order,
                k1=k1,
                k2=k2,
                n=8,
                master=P9_TEST_SEED_F,
                tag_fn=constant_tag,
                gate_id=tr.P9_GATE_ID,
            )
        return arm

    l1_fail = run_with("l1-fail")
    assert l1_fail.key_dependent_bits == 5 * 3 and l1_fail.public_control_bits == 0
    full = run_with("ok")
    assert full.key_dependent_bits == 5 * (3 + 4) + 64
    zero_full = run_with("ok", k1=0, k2=0)
    assert zero_full.key_dependent_bits == 64
    assert zero_full.public_control_bits == 10 * 8 + 63
    events = (
        tr.block_events("screen", 7, 0, l1_fail, n=8, gate_id=tr.P9_GATE_ID)
        + tr.block_events("screen", 7, 1, full, n=8, gate_id=tr.P9_GATE_ID)
        + tr.block_events("screen", 7, 2, zero_full, n=8, gate_id=tr.P9_GATE_ID)
    )
    recount = tr.recount_events(events)
    assert recount["key_dependent_bits"] == (
        l1_fail.key_dependent_bits + full.key_dependent_bits + zero_full.key_dependent_bits
    )
    assert recount["tag_invocations"] == 2
    assert all(e["frame_key"].startswith(tr.P9_FRAME_PREFIX) for e in events)
    tampered = [dict(event) for event in events]
    tampered[0]["key_dependent_bits"] += 5
    assert tr.recount_events(tampered)["key_dependent_bits"] == recount["key_dependent_bits"] + 5


def test_p9_domain_separation_protocol_prefix_labels():
    assert tr.P9_PROTOCOL_NAME != tr.PROTOCOL_NAME
    assert tr.P9_SEED_PREFIX != tr.SEED_PREFIX
    assert tr.P9_FRAME_PREFIX != tr.P8_FRAME_PREFIX
    assert tr.P9_MODE != tr.MODE
    assert tr.P9_CANDIDATE_LABEL != tr.P8_CANDIDATE_LABEL
    assert tr.P9_NO_ELIGIBLE_LABEL != tr.P8_NO_ELIGIBLE_LABEL
    assert tr.P9_NOT_CONFIRMED_LABEL != tr.P8_NOT_CONFIRMED_LABEL
    assert tr._gate_protocol(tr.P9_GATE_ID) == tr.P9_PROTOCOL_NAME
    assert tr._gate_protocol(tr.P8_GATE_ID) == tr.PROTOCOL_NAME
    assert tr._gate_seed_prefix(tr.P9_GATE_ID) == tr.P9_SEED_PREFIX
    assert tr._gate_labels(tr.P9_GATE_ID)["candidate"] == tr.P9_CANDIDATE_LABEL
    assert tr._gate_labels(tr.P9_GATE_ID)["no_eligible_point"] == tr.P9_NO_ELIGIBLE_LABEL
    assert tr._gate_labels(tr.P8_GATE_ID)["candidate"] == tr.P8_CANDIDATE_LABEL
    assert_raises_match(ValueError, "gate-id", tr._normalize_gate_id, "p9-typo")
    counts = injected_counts(P9_TEST_SEED_A)
    exp = expected_seam(counts)
    orders = injected_orders(P9_TEST_SEED_B)
    sandbox = Path(tempfile.mkdtemp())
    assert_raises_match(
        ValueError, "k1-grid", tr.run_target_rate,
        counts=counts, orders=orders,
        screen_seeds=(P9_TEST_SEED_C,), screen_blocks=1,
        k1_grid=list(tr.FROZEN_K1_GRID), k2_grid=list(tr.FROZEN_K2_GRID),
        confirm_seeds=(P9_TEST_SEED_D,), confirm_blocks=1,
        out_dir=str(sandbox / "mismatch1"), expected_entropies=exp,
        gate_id=tr.P9_GATE_ID,
    )
    assert_raises_match(
        ValueError, "k1-grid", tr.run_target_rate,
        counts=counts, orders=orders,
        screen_seeds=(P9_TEST_SEED_C,), screen_blocks=1,
        k1_grid=list(tr.P9_FROZEN_K1_GRID), k2_grid=list(tr.P9_FROZEN_K2_GRID),
        confirm_seeds=(P9_TEST_SEED_D,), confirm_blocks=1,
        out_dir=str(sandbox / "mismatch2"), expected_entropies=exp,
        gate_id=tr.P8_GATE_ID,
    )


def test_p9_cli_gate_id_closed_choice_and_refusals():
    assert tr.P9_GATE_ID == "p9-lower-rate-boundary"
    assert tr.GATE_IDS == (tr.P8_GATE_ID, tr.P9_GATE_ID)
    assert "--gate-id" in tr.P9_FROZEN_COMMAND
    assert tr.P9_FROZEN_COMMAND.count("--gate-id p9-lower-rate-boundary") == 1
    assert tr.P9_FROZEN_OUT_ROOT.endswith("lower_rate_screen" + "_confirm")
    parser = tr.build_parser()
    p9_argv = [
        "--gate-id", "p9-lower-rate-boundary",
        "--counts", "x.npz",
        "--source", "1M",
        "--orders", "o.json",
        "--n", "256", "--floor", "1e-15",
        "--screen-seeds", "2026091710", "2026091711", "2026091712",
        "--screen-blocks", "64",
        "--k1-grid", "0", "2", "4", "6", "8", "12", "24", "45",
        "--k2-grid", "0", "20", "40", "50", "60", "70", "80",
        "--confirm-seeds", "2026091720", "2026091721", "2026091722",
        "2026091723", "2026091724",
        "--confirm-blocks", "128",
        "--out-dir", "example_root",
    ]
    args = parser.parse_args(p9_argv)
    assert args.gate_id == tr.P9_GATE_ID
    assert tuple(args.k1_grid) == tr.P9_FROZEN_K1_GRID
    assert tuple(args.k2_grid) == tr.P9_FROZEN_K2_GRID
    assert tuple(args.screen_seeds) == tr.P9_FROZEN_SCREEN_SEEDS
    assert tuple(args.confirm_seeds) == tr.P9_FROZEN_CONFIRM_SEEDS
    assert_raises_match(SystemExit, "", parser.parse_args, p9_argv[:-2] + ["--gate-id", "bad"])
    nogate = [v for v in p9_argv if v != "--gate-id" and v != "p9-lower-rate-boundary"]
    parsed = parser.parse_args(nogate)
    assert parsed.gate_id is None

    def forbidden_loader(*args, **kwargs):
        raise AssertionError("loader must not run before the refusals")

    sandbox = Path(tempfile.mkdtemp())
    existing = sandbox / "exists9"
    existing.mkdir()
    never = sandbox / "never9"
    with patched(tr, "load_v25_channel_counts", forbidden_loader):
        assert tr.main(nogate[:-1] + [str(never)]) == 2
        assert tr.main(
            [
                "--gate-id", "p9-lower-rate-boundary",
                "--counts", str(sandbox / "fake.npz"),
                "--source", "1M",
                "--orders", str(sandbox / "o.json"),
                "--n", "256", "--floor", "1e-15",
                "--screen-seeds", "2026091710", "2026091711", "2026091712",
                "--screen-blocks", "64",
                "--k1-grid", "0", "2", "4", "6", "8", "12", "24", "45",
                "--k2-grid", "0", "20", "40", "50", "60", "70", "80",
                "--confirm-seeds", "2026091720", "2026091721", "2026091722",
                "2026091723", "2026091724",
                "--confirm-blocks", "128",
                "--out-dir", str(existing),
            ]
        ) == 2
        assert tr.main(
            [
                "--gate-id", "p9-lower-rate-boundary",
                "--counts", str(sandbox / "fake.npz"),
                "--source", "1M",
                "--orders", str(sandbox / "o.json"),
                "--n", "256", "--floor", "1e-15",
                "--screen-seeds", "2026091680",
                "--screen-blocks", "64",
                "--k1-grid", "0", "2", "4", "6", "8", "12", "24", "45",
                "--k2-grid", "0", "20", "40", "50", "60", "70", "80",
                "--confirm-seeds", "2026091721",
                "--confirm-blocks", "128",
                "--out-dir", str(never),
            ]
        ) == 2
    assert not never.exists()
    p8_args = parser.parse_args(
        [
            "--gate-id", "p8-target-rate-screen-confirm",
            "--counts", "x.npz",
            "--source", "1M",
            "--orders", "o.json",
            "--n", "256", "--floor", "1e-15",
            "--screen-seeds", "2026091680", "2026091681", "2026091682",
            "--screen-blocks", "64",
            "--k1-grid", "8", "10", "12", "16", "24", "32", "45",
            "--k2-grid", "80", "94", "110", "125", "140",
            "--confirm-seeds", "2026091690", "2026091691", "2026091692",
            "2026091693", "2026091694",
            "--confirm-blocks", "128",
            "--out-dir", "example_root",
        ]
    )
    assert p8_args.gate_id == tr.P8_GATE_ID


def test_p9_truth_isolation_and_buckets():
    p1, p2 = tiny_p1_p2()
    block = tiny_block(n=8, seed=P9_TEST_SEED_G)
    before = {name: np.array(getattr(block, name), copy=True) for name in ("bob", "high", "low")}

    def fake_sc(logp, *, field, alpha=2, known_positions=None, known_values=None):
        return FakeSC(np.zeros(8, dtype=np.int64))

    with patched(tr, "sc_decode", fake_sc):
        arm = tr.run_rate_arm(
            phase="screen",
            arm="empirical",
            block=block,
            field=FIELD,
            p1_table=p1,
            p2_table=p2,
            l1_order=np.arange(8, dtype=np.int64),
            l2_order=np.arange(8, dtype=np.int64),
            k1=0,
            k2=0,
            n=8,
            master=P9_TEST_SEED_H,
            tag_fn=constant_tag,
            gate_id=tr.P9_GATE_ID,
        )
    for name, snapshot in before.items():
        assert np.array_equal(np.asarray(getattr(block, name)), snapshot)
    assert arm.truth_leak_violation is False
    assert tr.classify_pair(True, True) == "both_exact"
    assert tr.classify_pair(True, False) == "empirical_only"
    zero_exact = canned_exact_arm("screen", "empirical", 0, 0)
    assert zero_exact.key_dependent_bits == 64
    assert tr._arm_record_consistent(zero_exact, n=256) is True
    counts = injected_counts(P9_TEST_SEED_I)
    exp = expected_seam(counts)
    root = Path(tempfile.mkdtemp()) / "leak9"
    with patched(tr, "_truth_isolation_sentinel", lambda *args, **kwargs: False):
        with patched(tr, "sc_decode", fake_sc_small()):
            run = tr.run_target_rate(
                counts=counts,
                orders=injected_orders(P9_TEST_SEED_J),
                screen_seeds=(P9_TEST_SEED_A,),
                screen_blocks=1,
                k1_grid=list(tr.P9_FROZEN_K1_GRID),
                k2_grid=list(tr.P9_FROZEN_K2_GRID),
                confirm_seeds=(P9_TEST_SEED_B,),
                confirm_blocks=1,
                out_dir=str(root),
                expected_entropies=exp,
                gate_id=tr.P9_GATE_ID,
            )
    assert run.summary["integrity"]["truth_leak_zero"] is False
    assert run.summary["outcome_label"] == "BLOCKED"


def test_p9_no_forbidden_markers_or_production_invocation():
    import re

    source = Path(tr.__file__).read_text(encoding="utf-8")
    lowered = source.lower()
    for marker in FORBIDDEN_MODULE_MARKERS:
        assert marker not in lowered, f"forbidden marker {marker!r} in target_rate.py"
    for match in re.finditer(r"np\.random\.([A-Za-z_]+)\s*\(", source):
        assert match.group(1) == "default_rng", f"global RNG use: {match.group(0)}"
    assert "open(" not in source
    own = Path(__file__).read_text(encoding="utf-8")
    assert ("channel_counts" + ".npz") not in own
    assert ("lower_rate_screen" + "_confirm") not in own
    for seed in tr.P9_FROZEN_SCREEN_SEEDS + tr.P9_FROZEN_CONFIRM_SEEDS:
        assert f"default_rng({seed})" not in own
        assert f"screen_seeds=({seed}" not in own
        assert f"confirm_seeds=({seed}" not in own

    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not run from injected tests")

    counts = injected_counts(P9_TEST_SEED_A)
    exp = expected_seam(counts)
    injected_root = Path(tempfile.mkdtemp()) / "injected9"
    with patched(tr, "load_v25_channel_counts", forbidden_loader):
        injected = tr.run_target_rate(
            counts=counts,
            orders=injected_orders(P9_TEST_SEED_B),
            screen_seeds=(P9_TEST_SEED_C,),
            screen_blocks=1,
            k1_grid=list(tr.P9_FROZEN_K1_GRID),
            k2_grid=list(tr.P9_FROZEN_K2_GRID),
            confirm_seeds=(P9_TEST_SEED_D,),
            confirm_blocks=1,
            out_dir=str(injected_root),
            expected_entropies=exp,
            tag_fn=constant_tag,
            gate_id=tr.P9_GATE_ID,
        )
    assert injected.summary["input_mode"] == "injected_counts"
    assert injected.summary["gate_id"] == tr.P9_GATE_ID
    assert injected.summary["analysis"] == tr.P9_PROTOCOL_NAME
    assert injected.summary["attempt_read_accounting"]["open_count"] == 0
    assert sorted(p.name for p in injected_root.iterdir()) == sorted(tr.OUTPUT_FILES)

    empty = Path(tempfile.mkdtemp())
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    code = (
        "import comparison_bench.src.comparison_bench.formal_ir.nbpolar."
        "target_rate as t; "
        "assert t.P9_FROZEN_NCONFIGS == 56 and t.FROZEN_NCONFIGS == 35 "
        "and t.P9_GATE_ID == 'p9-lower-rate-boundary'"
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
