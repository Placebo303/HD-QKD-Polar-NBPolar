"""Focused Phase 4-P6 adaptive hard-L1 gate tests.

Synthetic/injected fixtures only.  No stored data product, no real frame, no
DEV/EVAL stream, no sibling read, no method adapter and no output outside a
temporary directory.  Focused tests use their own fresh seeds >= 2026091560 and
never the frozen gate streams 2026091550..2026091554 (read from the module
constants only).

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

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import adaptive_l1 as al
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import penalty_gate as pg
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    Provenance,
    build_p1_metrics,
    probs_to_symbol_metric,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc import (
    ImpossibleDisclosedValueError,
    NumericNonfiniteError,
)
from comparison_bench.src.comparison_bench.formal_ir.shared import toeplitz_tag, verification_union_bound

FIELD = make_gf32()
REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_SEED_A = 2026091560
TEST_SEED_B = 2026091561
TEST_SEED_C = 2026091562
TEST_SEED_D = 2026091563
TEST_SEED_E = 2026091564
TEST_SEED_F = 2026091565
TEST_SEED_G = 2026091566
TEST_MASTER_BASE = 2026101560
TEST_SEEDS = (TEST_SEED_A, TEST_SEED_B, TEST_SEED_C, TEST_SEED_D, TEST_SEED_E, TEST_SEED_F, TEST_SEED_G)
TINY_N = 8
TINY_LEVELS = (2, 4, 8)
TINY_K2 = 3

FORBIDDEN_MARKERS = (
    "outputs_comparison",
    "model_f",
    "v72p2d5",
    "parquet",
    "ttbin",
    "dev_seed",
    "eval_seed",
    "benchmark",
    "sibling",
    "artifact",
    "results/",
    "fwht",
    "scl/crc",
    "scl_crc",
    "app_fed",
    "app_prior",
    "get_l1_app",
    "pandas",
    "pyarrow",
    "scipy",
)

_TABLE_CACHE: dict = {}


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


@contextlib.contextmanager
def patched(obj, name, value):
    original = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, original)


def strong_tables():
    if "p2" not in _TABLE_CACHE:
        table = pg.build_dependent_joint_table(profile="strong", epsilon1=0.05)
        p1_table, p2_table = tl.layer_metric_tables(table)
        _TABLE_CACHE.update(table=table, p1=p1_table, p2=p2_table)
    return _TABLE_CACHE["p1"], _TABLE_CACHE["p2"]


def tiny_fixture(seed=TEST_SEED_A, levels=TINY_LEVELS, k2=TINY_K2, n=TINY_N):
    """Deterministic tiny injected block plus metrics and disclosure sets."""
    p1_table, p2_table = strong_tables()
    order = tl.analytic_order(0.05, n)
    d1_sets = tuple(np.sort(order[:k]).astype(np.int64) for k in levels)
    d2 = tl.disclosure_coordinates(n=n, k=k2, epsilon=0.20)
    sample = pg.sample_dependent_block(
        np.random.default_rng(seed), n=n, epsilon1=0.05, profile="strong"
    )
    p1_metric = probs_to_symbol_metric(
        build_p1_metrics(sample.bob[None, :], p1_table)[0],
        provenance=Provenance.PRIOR_ONLY,
    )
    u1_true = tl.polar_transform(sample.high, field=FIELD, alpha=al.ALPHA)
    u2_true = tl.polar_transform(sample.low, field=FIELD, alpha=al.ALPHA)
    labels_true = (sample.low + 32 * sample.high).astype(np.int64)
    return {
        "sample": sample,
        "tables": (p1_table, p2_table),
        "p1_logp": p1_metric.logp,
        "d1_sets": d1_sets,
        "d2": d2,
        "u1_true": u1_true,
        "u2_true": u2_true,
        "labels_true": labels_true,
        "labels_true_bits": tl.labels_to_bits(labels_true),
    }


def arm_kwargs(fixture, master=TEST_MASTER_BASE, levels=TINY_LEVELS, n=TINY_N):
    _, p2_table = fixture["tables"]
    order = tl.analytic_order(0.05, n)
    d1_sets = tuple(np.sort(order[:k]).astype(np.int64) for k in levels)
    return {
        "field": FIELD,
        "p1_logp": fixture["p1_logp"],
        "p2_table": p2_table,
        "d1_sets": d1_sets,
        "d2": fixture["d2"],
        "bob": fixture["sample"].bob,
        "u1_true": fixture["u1_true"],
        "u2_true": fixture["u2_true"],
        "labels_true": fixture["labels_true"],
        "labels_true_bits": fixture["labels_true_bits"],
        "levels": levels,
        "n": n,
        "master": master,
    }


def scripted_tag(match_level: int, calls: dict):
    """Mismatch levels < ``match_level``, honest at ``match_level``."""

    def tag(bits, seed, tag_bits=64):
        calls["n"] += 1
        level, parity = divmod(calls["n"] - 1, 2)
        if level < match_level:
            return b"\x01" * 8 if parity == 0 else b"\x02" * 8
        return toeplitz_tag(bits, seed, tag_bits)

    return tag


def always_mismatch_tag():
    """Every pair of (Alice, Bob) tag calls returns two different constants."""
    state = {"n": 0}

    def tag(bits, seed, tag_bits=64):
        state["n"] += 1
        return b"\x01" * 8 if state["n"] % 2 == 1 else b"\x02" * 8

    return tag


def colliding_tag(bits, seed, tag_bits=64):
    return b"\x2a" * 8


def test_p6_nested_schedule_and_frozen_sets():
    nested = al.inc.build_nested_schedule(n=256, epsilon=0.05, sizes=al.FROZEN_K1_LEVELS)
    assert tuple(int(v) for v in nested.sizes) == al.FROZEN_K1_LEVELS
    assert nested.strict_nesting and nested.order_prefix_matches and nested.new_coordinates_disjoint
    sizes = [int(len(s)) for s in nested.sets]
    assert sizes == [45, 60, 72, 112]
    for i in range(len(nested.sets) - 1):
        assert len(nested.sets[i]) < len(nested.sets[i + 1])
        assert bool(np.isin(nested.sets[i], nested.sets[i + 1]).all())
    flat = [int(v) for arr in nested.new_positions for v in arr.tolist()]
    assert sorted(flat) == sorted(int(v) for v in nested.sets[-1].tolist())
    assert len(flat) == len(set(flat)) == 112
    accepted_d1_45 = tl.frozen_disclosure_sets(
        n=256, k1=45, k2=140, epsilon1=0.05, epsilon2=0.20
    )[0]
    assert np.array_equal(nested.sets[0], accepted_d1_45)
    d2 = tl.disclosure_coordinates(n=256, k=140, epsilon=0.20)
    assert d2.shape == (140,) and len(set(int(v) for v in d2.tolist())) == 140
    assert al.STATIC_K1 == 112
    assert al.STATIC_FULLY_INVOKED_BITS == 1324 == 5 * (112 + 140) + 64
    assert al.FROZEN_K2 == 140 and al.FROZEN_PAIRS == 640
    assert al.STATIC_EXACT_MIN == 620


def test_p6_level_restart_and_no_state_reuse():
    fixture = tiny_fixture(seed=TEST_SEED_A)
    real_decode_layer = tl._decode_layer
    sc_calls: list = []
    tag_seeds: list = []

    def recording_decode_layer(logp, **kwargs):
        sc_calls.append((logp, tuple(int(v) for v in kwargs["positions"].tolist())))
        return real_decode_layer(logp, **kwargs)

    def recording_tag(bits, seed, tag_bits=64):
        tag_seeds.append(bytes(seed))
        return toeplitz_tag(bits, seed, tag_bits)

    calls = {"n": 0}
    scripted = scripted_tag(2, calls)

    def recording_tag(bits, seed, tag_bits=64):
        tag_seeds.append(bytes(seed))
        return scripted(bits, seed, tag_bits)

    with patched(tl, "_decode_layer", recording_decode_layer):
        result = al.run_adaptive_arm(0, **arm_kwargs(fixture), tag_fn=recording_tag)
    assert result.outcome == "exact" and result.termination_stage == 3
    assert result.termination_k1 == 8 and result.tag_invocations == 3
    assert result.feedback_invocations == 2
    # Three stages x (L1 + L2); every L1 call receives the ORIGINAL metric
    # object, every L2 call a freshly gathered distinct object.
    assert len(sc_calls) == 6
    l1_calls = [c for i, c in enumerate(sc_calls) if i % 2 == 0]
    l2_calls = [c for i, c in enumerate(sc_calls) if i % 2 == 1]
    assert all(c[0] is fixture["p1_logp"] for c in l1_calls)
    assert [c[1] for c in l1_calls] == [
        tuple(int(v) for v in fixture["d1_sets"][i]) for i in range(3)
    ]
    assert all(c[0] is not fixture["p1_logp"] for c in l2_calls)
    assert len({id(c[0]) for c in l2_calls}) == 3
    # One L1 + L2 pair per stage, no stage reuses a decoder result.
    assert [c[1] for c in l2_calls] == [tuple(int(v) for v in fixture["d2"])] * 3
    # Tag seeds are domain-separated per level and match the frozen derivation.
    assert len(tag_seeds) == 6 and len(set(tag_seeds)) == 3
    for level in (1, 2, 3):
        expected = al.block_toeplitz_seed_bits(
            "adaptive", 0, level, master=TEST_MASTER_BASE, bit_length=tl.seed_bits_for(TINY_N)
        )
        assert expected.tobytes() in tag_seeds


def test_p6_tag_accept_advance_and_terminal_verify():
    fixture = tiny_fixture(seed=TEST_SEED_A)
    kwargs = arm_kwargs(fixture)
    # Forced mismatch for every call: the terminal stage is verify_failed.
    terminal = al.run_adaptive_arm(
        0, **arm_kwargs(fixture, levels=(4, 8)), tag_fn=always_mismatch_tag()
    )
    assert terminal.outcome == "verify_failed"
    assert terminal.termination_stage == 2 and terminal.termination_k1 == 8
    assert terminal.tag_invocations == 2 and terminal.feedback_invocations == 1
    assert terminal.tag_pass is False and terminal.exact is False
    # Forced mismatch on the first level only: advances exactly one level and
    # accepts at the next level with an honest tag.
    calls = {"n": 0}
    advanced = al.run_adaptive_arm(
        0, **arm_kwargs(fixture, levels=(4, 8)), tag_fn=scripted_tag(1, calls)
    )
    assert advanced.outcome == "exact" and advanced.exact is True
    assert advanced.termination_stage == 2 and advanced.termination_k1 == 8
    assert advanced.tag_invocations == 2 and advanced.feedback_invocations == 1
    assert advanced.feedback_stages == (0,)
    # Forced tag collision on a wrong label is undetected, never exact.
    undetected = al.run_adaptive_arm(0, **kwargs, tag_fn=colliding_tag)
    assert undetected.outcome == "undetected" and undetected.exact is False
    assert undetected.label_match is False and undetected.tag_pass is True
    assert undetected.termination_stage == 1 and undetected.tag_invocations == 1
    # Honest tag with a fully disclosed level stops immediately.
    calls = {"n": 0}
    exact_first = al.run_adaptive_arm(
        0, **arm_kwargs(fixture, levels=(8,)), tag_fn=scripted_tag(0, calls)
    )
    assert exact_first.outcome == "exact" and exact_first.termination_stage == 1
    assert exact_first.tag_invocations == 1 and exact_first.feedback_invocations == 0


def test_p6_impossible_disclosure_nonterminal_terminal_and_failclosed():
    fixture = tiny_fixture(seed=TEST_SEED_A)
    real_decode_layer = tl._decode_layer

    def raise_first(n_raises, exc_type):
        state = {"n": 0}

        def wrapper(logp, **kwargs):
            state["n"] += 1
            if state["n"] <= n_raises:
                raise exc_type("forced test failure")
            return real_decode_layer(logp, **kwargs)

        return wrapper

    # Nonterminal impossible: one feedback bit, no tag, then advance and accept.
    with patched(tl, "_decode_layer", raise_first(1, ImpossibleDisclosedValueError)):
        advanced = al.run_adaptive_arm(
            0, **arm_kwargs(fixture, levels=(2, 4)), tag_fn=toeplitz_tag
        )
    assert advanced.outcome == "exact"
    assert advanced.rejected_stages == (0,) and advanced.feedback_stages == (0,)
    assert advanced.feedback_invocations == 1 and advanced.tag_invocations == 1
    assert advanced.termination_stage == 2 and advanced.key_dependent_bits == 5 * (4 + 3) + 64
    # Terminal impossible: decode_failed, no candidate, no tag, one feedback.
    with patched(tl, "_decode_layer", raise_first(2, ImpossibleDisclosedValueError)):
        failed = al.run_adaptive_arm(
            0, **arm_kwargs(fixture, levels=(2, 4)), tag_fn=toeplitz_tag
        )
    assert failed.outcome == "decode_failed"
    assert failed.l1_decode_failed is True and failed.l2_invoked is False
    assert failed.tag_invocations == 0 and failed.feedback_invocations == 1
    assert failed.termination_stage == 2
    assert failed.key_dependent_bits == 5 * 4
    assert failed.public_seed_bits == 0 and failed.public_control_bits == 1
    # All other exceptions fail closed immediately: no feedback, no tag.
    with patched(tl, "_decode_layer", raise_first(1, NumericNonfiniteError)):
        nonfinite = al.run_adaptive_arm(
            0, **arm_kwargs(fixture, levels=(2, 4, 8)), tag_fn=toeplitz_tag
        )
    assert nonfinite.outcome == "decode_failed"
    assert nonfinite.termination_stage == 1 and nonfinite.nonfinite is True
    assert nonfinite.feedback_invocations == 0 and nonfinite.tag_invocations == 0
    assert nonfinite.key_dependent_bits == 5 * 2
    assert nonfinite.l1_error_type == "NumericNonfiniteError"


def test_p6_label_assembly_and_static_endpoint():
    fixture = tiny_fixture(seed=TEST_SEED_A)
    kwargs = arm_kwargs(fixture)
    calls = {"n": 0}
    adaptive = al.run_adaptive_arm(
        0, **arm_kwargs(fixture, levels=(8,)), tag_fn=scripted_tag(0, calls)
    )
    assert adaptive.outcome == "exact" and adaptive.label_match is True
    assert np.array_equal(
        adaptive.label_hat, (adaptive.low_hat + 32 * adaptive.high_hat).astype(np.int64)
    )
    assert np.array_equal(adaptive.label_hat, fixture["labels_true"])
    static = al.run_static_arm(
        0,
        field=FIELD,
        p1_logp=fixture["p1_logp"],
        p2_table=fixture["tables"][1],
        d1=fixture["d1_sets"][-1],
        d2=fixture["d2"],
        bob=fixture["sample"].bob,
        u1_true=fixture["u1_true"],
        u2_true=fixture["u2_true"],
        labels_true=fixture["labels_true"],
        labels_true_bits=fixture["labels_true_bits"],
        n=TINY_N,
        master=TEST_MASTER_BASE,
    )
    assert static.arm == "static" and static.termination_stage == 1
    assert static.termination_k1 == 8 and static.levels_invoked == 1
    assert static.feedback_invocations == 0
    assert static.outcome == "exact" and static.label_match is True
    assert np.array_equal(
        static.label_hat, (static.low_hat + 32 * static.high_hat).astype(np.int64)
    )
    assert np.array_equal(static.label_hat, fixture["labels_true"])
    assert static.key_dependent_bits == 5 * (8 + 3) + 64


def test_p6_truth_isolation_sentinel_and_input_invariance():
    fixture = tiny_fixture(seed=TEST_SEED_B)
    _, p2_table = fixture["tables"]
    high = np.array(fixture["sample"].high, copy=True)
    low = np.array(fixture["sample"].low, copy=True)
    bob = np.array(fixture["sample"].bob, copy=True)
    paired = al.run_paired_block(
        0,
        high,
        low,
        bob,
        field=FIELD,
        p1_table=fixture["tables"][0],
        p2_table=p2_table,
        d1_sets=fixture["d1_sets"],
        d2=fixture["d2"],
        levels=TINY_LEVELS,
        n=TINY_N,
        master=TEST_MASTER_BASE,
    )
    assert paired.static.truth_leak_violation is False
    assert paired.adaptive.truth_leak_violation is False
    # The caller's arrays are not mutated by the mutation sentinel.
    assert np.array_equal(high, fixture["sample"].high)
    assert np.array_equal(low, fixture["sample"].low)
    assert np.array_equal(bob, fixture["sample"].bob)
    # A failing sentinel marks both arms and never hides the violation.
    with patched(tl, "_truth_isolation_sentinel", lambda *a, **k: False):
        compromised = al.run_paired_block(
            0,
            high,
            low,
            bob,
            field=FIELD,
            p1_table=fixture["tables"][0],
            p2_table=p2_table,
            d1_sets=fixture["d1_sets"],
            d2=fixture["d2"],
            levels=TINY_LEVELS,
            n=TINY_N,
            master=TEST_MASTER_BASE,
        )
    assert compromised.static.truth_leak_violation is True
    assert compromised.adaptive.truth_leak_violation is True


def test_p6_accounting_at_every_termination_class():
    fixture = tiny_fixture(seed=TEST_SEED_A)
    kwargs = arm_kwargs(fixture)
    seed_bits = tl.seed_bits_for(TINY_N)
    real_decode_layer = tl._decode_layer

    def raise_first(n_raises, exc_type):
        state = {"n": 0}

        def wrapper(logp, **inner):
            state["n"] += 1
            if state["n"] <= n_raises:
                raise exc_type("forced test failure")
            return real_decode_layer(logp, **inner)

        return wrapper

    calls = {"n": 0}
    accepted_stage3 = al.run_adaptive_arm(
        0, **arm_kwargs(fixture, levels=(2, 4, 8)), tag_fn=scripted_tag(2, calls)
    )
    assert accepted_stage3.outcome == "exact"
    assert accepted_stage3.termination_stage == 3
    assert accepted_stage3.key_dependent_bits == 5 * (8 + TINY_K2) + 64 * 3
    assert accepted_stage3.public_seed_bits == seed_bits * 3
    assert accepted_stage3.feedback_bits == 2
    assert accepted_stage3.public_control_bits == seed_bits * 3 + 2

    calls = {"n": 0}
    accepted_stage2 = al.run_adaptive_arm(
        0, **arm_kwargs(fixture, levels=(4, 8)), tag_fn=scripted_tag(1, calls)
    )
    assert accepted_stage2.outcome == "exact"
    assert accepted_stage2.termination_stage == 2
    assert accepted_stage2.key_dependent_bits == 5 * (8 + TINY_K2) + 64 * 2
    assert accepted_stage2.public_seed_bits == seed_bits * 2
    assert accepted_stage2.feedback_bits == 1
    assert accepted_stage2.public_control_bits == seed_bits * 2 + 1

    verify_failed = al.run_adaptive_arm(
        0, **arm_kwargs(fixture, levels=(4, 8)), tag_fn=always_mismatch_tag()
    )
    assert verify_failed.outcome == "verify_failed"
    assert verify_failed.termination_stage == 2
    assert verify_failed.key_dependent_bits == 5 * (8 + TINY_K2) + 64 * 2
    assert verify_failed.public_control_bits == seed_bits * 2 + 1

    undetected = al.run_adaptive_arm(0, **kwargs, tag_fn=colliding_tag)
    assert undetected.outcome == "undetected"
    assert undetected.termination_stage == 1
    assert undetected.key_dependent_bits == 5 * (2 + TINY_K2) + 64
    assert undetected.public_seed_bits == seed_bits
    assert undetected.feedback_bits == 0
    assert undetected.public_control_bits == seed_bits

    with patched(tl, "_decode_layer", raise_first(1, ImpossibleDisclosedValueError)):
        rejection_then_accept = al.run_adaptive_arm(
            0, **arm_kwargs(fixture, levels=(2, 4)), tag_fn=toeplitz_tag
        )
    assert rejection_then_accept.outcome == "exact"
    assert rejection_then_accept.key_dependent_bits == 5 * (4 + TINY_K2) + 64
    assert rejection_then_accept.public_control_bits == seed_bits + 1
    assert rejection_then_accept.feedback_bits == 1

    with patched(tl, "_decode_layer", raise_first(2, ImpossibleDisclosedValueError)):
        terminal_rejection = al.run_adaptive_arm(
            0, **arm_kwargs(fixture, levels=(2, 4)), tag_fn=toeplitz_tag
        )
    assert terminal_rejection.outcome == "decode_failed"
    assert terminal_rejection.termination_stage == 2
    assert terminal_rejection.key_dependent_bits == 5 * 4
    assert terminal_rejection.public_seed_bits == 0
    assert terminal_rejection.feedback_bits == 1
    assert terminal_rejection.public_control_bits == 1

    with patched(tl, "_decode_layer", raise_first(1, NumericNonfiniteError)):
        other_exception = al.run_adaptive_arm(
            0, **arm_kwargs(fixture, levels=(2, 4, 8)), tag_fn=toeplitz_tag
        )
    assert other_exception.outcome == "decode_failed"
    assert other_exception.key_dependent_bits == 5 * 2
    assert other_exception.public_seed_bits == 0 and other_exception.public_control_bits == 0
    assert other_exception.feedback_invocations == 0


def test_p6_transcript_recount_and_tamper():
    root = Path(tempfile.mkdtemp()) / "recount"
    run = al.run_adaptive_gate(
        n=256,
        epsilon1=0.05,
        profile="strong",
        k1_levels=list(al.FROZEN_K1_LEVELS),
        k2=140,
        seeds=[TEST_SEED_C],
        blocks_per_seed=2,
        out_dir=str(root),
    )
    assert run.summary["transcript"]["mismatch_count"] == 0
    assert run.summary["transcript"]["mismatches"] == []
    recount = al.recount_transcript(run.events)
    assert recount["key_dependent_bits"] == run.transcript["incremental"]["key_dependent_bits"]
    assert recount["tag_invocations"] == run.transcript["incremental"]["tag_invocations"]
    assert recount["feedback_invocations"] == run.transcript["incremental"]["feedback_invocations"]
    assert recount["public_control_bits"] == run.transcript["incremental"]["public_control_bits"]
    for arm in ("static", "adaptive"):
        for field_name in ("key_dependent_bits", "public_control_bits", "tag_invocations"):
            assert recount["by_arm"][arm][field_name] == (
                run.transcript["incremental_by_arm"][arm][field_name]
            )
    l2_events = [e for e in run.events if e["event_type"] == "l2_disclosure"]
    assert len(l2_events) == 2 * 2
    assert all(int(e["key_dependent_bits"]) == 5 * 140 for e in l2_events)

    # Tamper with a disclosure count: the recount mismatch is detected.
    tampered = [dict(e) for e in run.events]
    target = next(e for e in tampered if e["event_type"] == "l1_disclosure")
    target["key_dependent_bits"] = int(target["key_dependent_bits"]) + 5
    tamper_recount = al.recount_transcript(tampered)
    mismatches = al._transcript_mismatches(
        run.transcript["incremental"],
        run.transcript["incremental_by_arm"],
        tamper_recount,
    )
    assert mismatches
    assert any("key_dependent_bits" in m for m in mismatches)

    # Tamper with a tag's public control bits: mismatch is detected too.
    tampered = [dict(e) for e in run.events]
    target = next(e for e in tampered if e["event_type"] == "verification_tag")
    target["public_control_bits"] = int(target["public_control_bits"]) + 1
    tamper_recount = al.recount_transcript(tampered)
    assert al._transcript_mismatches(
        run.transcript["incremental"],
        run.transcript["incremental_by_arm"],
        tamper_recount,
    )

    # Malformed events fail closed.
    bad_type = [dict(e) for e in run.events]
    bad_type[0]["event_type"] = "symbols"
    assert_raises_match(ValueError, "not frozen", al.recount_transcript, bad_type)
    bad_arm = [dict(e) for e in run.events]
    bad_arm[0]["event_id"] = "block-0-unknown-l1"
    assert_raises_match(ValueError, "arm-tagged", al.recount_transcript, bad_arm)


def test_p6_paired_block_identity_and_same_sample():
    fixture = tiny_fixture(seed=TEST_SEED_D)
    _, p2_table = fixture["tables"]
    real_decode_layer = tl._decode_layer
    seen: list = []

    def recording_decode_layer(logp, **kwargs):
        seen.append(logp)
        return real_decode_layer(logp, **kwargs)

    with patched(tl, "_decode_layer", recording_decode_layer):
        paired = al.run_paired_block(
            3,
            fixture["sample"].high,
            fixture["sample"].low,
            fixture["sample"].bob,
            field=FIELD,
            p1_table=fixture["tables"][0],
            p2_table=p2_table,
            d1_sets=fixture["d1_sets"],
            d2=fixture["d2"],
            levels=TINY_LEVELS,
            n=TINY_N,
            master=TEST_MASTER_BASE,
        )
    assert paired.block_index == 3
    assert paired.static.block_index == 3 and paired.adaptive.block_index == 3
    # The static L1 and every adaptive L1 call share the one original P1 metric
    # produced for this paired block; L2 metrics are freshly gathered.
    assert seen and paired.p1_logp is not None
    assert np.allclose(paired.p1_logp, fixture["p1_logp"])
    assert sum(1 for logp in seen if logp is paired.p1_logp) == 1 + paired.adaptive.levels_invoked
    assert np.array_equal(paired.labels_true, fixture["labels_true"])

    root = Path(tempfile.mkdtemp()) / "identity"
    run = al.run_adaptive_gate(
        n=256,
        epsilon1=0.05,
        profile="strong",
        k1_levels=list(al.FROZEN_K1_LEVELS),
        k2=140,
        seeds=[TEST_SEED_E],
        blocks_per_seed=3,
        out_dir=str(root),
    )
    identity = {(int(r.stream_seed), int(r.block_index)) for r in run.results}
    assert identity == {(TEST_SEED_E, i) for i in range(3)}
    for record in run.records:
        assert record["stream_seed"] == TEST_SEED_E
        assert record["paired_cell"] in al.CELLS
        assert record["static"]["outcome"] in tl.OUTCOMES
        assert record["adaptive"]["outcome"] in tl.OUTCOMES


def test_p6_r1_multistream_compound_d2_identity_gate():
    """Two streams sharing block indices: D2-once gates on compound identity.

    Pure record/checker logic with TEST-ONLY fabricated scalar arms (no SC,
    RNG, sampling or tag call): production ``paired_block_events`` and
    ``_integrity_gates`` are exercised directly.  Under the pre-R1
    ``(block_id, arm)`` grouping the shared block indices collapse into
    multiplicity-2 keys, so this fixture fails the old check; under the
    compound ``(stream_seed, block_index, arm)`` identity each arm-block has
    exactly one L2 disclosure and the gate passes.  Dropping or duplicating a
    single compound D2 disclosure must fail the gate.
    """
    levels = al.FROZEN_K1_LEVELS
    k2 = al.FROZEN_K2
    n = al.FROZEN_N
    seeds = (TEST_SEED_A, TEST_SEED_B)
    blocks_per_seed = 2
    nested = al.inc.build_nested_schedule(n=n, epsilon=al.FROZEN_EPSILON1, sizes=levels)
    d2 = np.arange(k2, dtype=np.int64)  # only len(d2) enters the L2 event bits
    seed_bits = tl.seed_bits_for(n)

    def fake_arm(arm, block_index, termination_stage, termination_k1):
        tag_invocations = termination_stage
        public_seed_bits = seed_bits * tag_invocations
        return al.AdaptiveArmResult(
            block_index=block_index,
            arm=arm,
            outcome="exact",
            exact=True,
            label_match=True,
            tag_pass=True,
            l1_provenance=Provenance.PRIOR_ONLY.value,
            l2_provenance=Provenance.CANDIDATE_CONDITIONED.value,
            l1_executed=True,
            l1_decode_failed=False,
            l2_invoked=True,
            l2_decode_failed=False,
            tag_invoked=True,
            levels_invoked=termination_stage,
            tag_invocations=tag_invocations,
            feedback_invocations=0,
            termination_stage=termination_stage,
            termination_k1=termination_k1,
            key_dependent_bits=5 * (termination_k1 + k2) + al.TAG_BITS * tag_invocations,
            public_seed_bits=public_seed_bits,
            feedback_bits=0,
            public_control_bits=public_seed_bits,
            nonfinite=False,
            truth_leak_violation=False,
            l1_error_type=None,
            l2_error_type=None,
            wall_s=0.0,
            tagged_stages=tuple(range(termination_stage)),
            feedback_stages=(),
            rejected_stages=(),
            l2_stage=0,
        )

    results = []
    events = []
    for stream_seed in seeds:
        for block_index in range(blocks_per_seed):
            static = fake_arm("static", block_index, 1, al.STATIC_K1)
            adaptive = fake_arm("adaptive", block_index, 1, levels[0])
            results.append(
                al.ResultRow(
                    stream_seed=stream_seed,
                    block_index=block_index,
                    static=static,
                    adaptive=adaptive,
                )
            )
            events.extend(
                al.paired_block_events(
                    al.PairedBlockResult(
                        block_index=block_index,
                        static=static,
                        adaptive=adaptive,
                        block_wall_s=0.0,
                    ),
                    stream_seed=stream_seed,
                    nested=nested,
                    d2=d2,
                    n=n,
                )
            )

    fields = (
        "key_dependent_bits",
        "public_seed_bits",
        "feedback_bits",
        "public_control_bits",
        "tag_invocations",
        "feedback_invocations",
    )
    incremental = {
        name: sum(getattr(a, name) for r in results for a in (r.static, r.adaptive))
        for name in fields
    }
    incremental_by_arm = {
        arm: {
            name: sum(
                getattr(a, name)
                for r in results
                for a in (r.static, r.adaptive)
                if a.arm == arm
            )
            for name in fields
        }
        for arm in al.ARMS
    }
    recount = al.recount_transcript(events)
    mismatches = al._transcript_mismatches(incremental, incremental_by_arm, recount)
    assert mismatches == []
    union_bound = verification_union_bound(recount["tag_invocations"])

    def gates_for(event_list):
        return al._integrity_gates(
            planned=len(results),
            results=results,
            stream_seeds=list(seeds),
            blocks_per_seed=blocks_per_seed,
            events=event_list,
            nested=nested,
            levels=levels,
            k2=k2,
            n=n,
            incremental=incremental,
            incremental_by_arm=incremental_by_arm,
            recount=recount,
            mismatches=mismatches,
            union_bound=union_bound,
            wall_s=0.0,
            total_wall_s=al.TOTAL_WALL_S,
            rss_bytes=None,
        )

    gates = gates_for(events)
    assert gates["d1_exactly_nested_and_d2_disclosed_once"] is True
    assert all(gates.values())  # every other frozen integrity gate passes too

    l2_events = [e for e in events if e["event_type"] == "l2_disclosure"]
    assert len(l2_events) == 2 * blocks_per_seed * len(al.ARMS)
    assert len({(e["stream_seed"], e["block_id"]) for e in events}) == 4
    assert all(e["stream_seed"] in seeds for e in events)
    assert all(
        e["frame_key"] == f"nbpolar-p4p6-synthetic:{e['stream_seed']}:{e['block_id']}"
        for e in events
    )

    # (i) The pre-R1 (block_id, arm) key collides across the two streams, so
    # the old `count == 1` D2 check would fail on exactly this fixture.
    old_counts = {}
    for event in l2_events:
        old_key = (int(event["block_id"]), str(event["event_id"]).split("-")[2])
        old_counts[old_key] = old_counts.get(old_key, 0) + 1
    assert sorted(old_counts.values()) == [2, 2, 2, 2]

    # The compound identity is complete and one-to-one for this fixture.
    compound = {
        (int(e["stream_seed"]), int(e["block_id"]), str(e["event_id"]).split("-")[2])
        for e in l2_events
    }
    assert len(compound) == len(l2_events) == 8

    # (ii) A missing or duplicated compound D2 disclosure fails the gate while
    # every other frozen gate stays unchanged (recount/mismatches held fixed).
    others = [name for name in al.INTEGRITY_GATE_ORDER if name != "d1_exactly_nested_and_d2_disclosed_once"]
    missing = list(events)
    missing.remove(
        next(
            e
            for e in l2_events
            if e["stream_seed"] == TEST_SEED_A
            and e["block_id"] == 0
            and e["event_id"].endswith("static-l2-disclosure")
        )
    )
    missing_gates = gates_for(missing)
    assert missing_gates["d1_exactly_nested_and_d2_disclosed_once"] is False
    assert all(missing_gates[name] is True for name in others)

    duplicated = list(events) + [l2_events[0]]
    duplicated_gates = gates_for(duplicated)
    assert duplicated_gates["d1_exactly_nested_and_d2_disclosed_once"] is False
    assert all(duplicated_gates[name] is True for name in others)


def test_p6_runner_tiny_schema_gates_and_five_files():
    root = Path(tempfile.mkdtemp()) / "smoke"
    started = time.perf_counter()
    run = al.run_adaptive_gate(
        n=256,
        epsilon1=0.05,
        profile="strong",
        k1_levels=list(al.FROZEN_K1_LEVELS),
        k2=140,
        seeds=[TEST_SEED_F],
        blocks_per_seed=2,
        out_dir=str(root),
    )
    elapsed = time.perf_counter() - started
    assert sorted(path.name for path in root.iterdir()) == sorted(al.OUTPUT_FILES)

    plan = json.loads((root / "frozen_plan.json").read_text(encoding="utf-8"))
    assert plan["seeds"] == [TEST_SEED_F]
    assert plan["toeplitz_masters"] == [TEST_SEED_F + al.PUBLIC_TAG_MASTER_OFFSET]
    assert plan["blocks_per_seed"] == 2 and plan["planned_pairs"] == 2
    assert plan["k1_levels"] == list(al.FROZEN_K1_LEVELS)
    assert plan["static_k1"] == 112 and plan["k2"] == 140
    assert len(plan["disclosure_coordinates"]["D1_by_level"]["112"]) == 112
    assert len(plan["disclosure_coordinates"]["D2"]) == 140
    assert plan["nested_assertions"]["strict_nesting"] is True
    assert plan["dependent_table"]["p2_maxdiff_floor"] == 0.30
    assert abs(plan["dependent_table"]["p2_maxdiff"] - 0.34875) < 1e-12
    assert plan["attempt_consumption_point"] == al.ATTEMPT_CONSUMPTION_POINT
    assert plan["attempts_allowed"] == 1 and plan["attempts_consumed_before"] == 0
    assert plan["attempts_consumed_by_this_run"] == 1 and plan["retries"] == 0
    assert plan["budget"] == {
        "total_wall_s": 3600.0,
        "external_timeout_s": 3600,
        "ulimit_virtual_kib": 2097152,
        "rss_bytes_max": 2147483648,
    }
    assert plan["frozen_command"] == al.FROZEN_COMMAND
    assert plan["claim_scope"] == al.CLAIM_SCOPE

    per_raw = (root / "per_block_paired_outcomes.json").read_text(encoding="utf-8")
    for banned in (
        "high_hat",
        "low_hat",
        "label_hat",
        "labels_true",
        "u1_disclosed",
        "u2_disclosed",
        "b_high",
        "b_low",
        '"seed_bits"',
        "seed_hex",
    ):
        assert banned not in per_raw, banned
    per = json.loads(per_raw)
    assert per["n_blocks"] == 2 and len(per["blocks"]) == 2
    for record in per["blocks"]:
        assert record["paired_cell"] in al.CELLS
        for arm_name in ("static", "adaptive"):
            arm_record = record[arm_name]
            assert set(arm_record) == {
                "outcome",
                "exact",
                "label_match",
                "tag_pass",
                "l1_provenance",
                "l2_provenance",
                "l1_executed",
                "l1_decode_failed",
                "l2_invoked",
                "l2_decode_failed",
                "tag_invoked",
                "levels_invoked",
                "tag_invocations",
                "feedback_invocations",
                "termination_stage",
                "termination_k1",
                "key_dependent_bits",
                "public_seed_bits",
                "feedback_bits",
                "public_control_bits",
                "nonfinite",
                "truth_leak_violation",
                "l1_error_type",
                "l2_error_type",
                "wall_s",
            }
            assert arm_record["outcome"] in tl.OUTCOMES

    transcript = json.loads((root / "transcript_accounting.json").read_text(encoding="utf-8"))
    assert transcript["mismatch_count"] == 0 and transcript["mismatches"] == []
    assert transcript["public_control_bits_per_tag"] == 2623
    assert transcript["fully_invoked_static_arm_bits"] == 1324
    assert transcript["fully_invoked_adaptive_arm_bits_by_level"]["112"] == 1324
    assert transcript["recount"]["tag_invocations"] == transcript["incremental"]["tag_invocations"]
    expected_kd = sum(
        record[arm_name]["key_dependent_bits"]
        for record in per["blocks"]
        for arm_name in ("static", "adaptive")
    )
    assert transcript["incremental"]["key_dependent_bits"] == expected_kd

    summary = json.loads((root / "aggregate_summary.json").read_text(encoding="utf-8"))
    assert summary == run.summary
    assert set(summary["integrity"]) == set(al.INTEGRITY_GATE_ORDER)
    assert set(summary["scientific"]) == set(al.SCIENTIFIC_GATE_ORDER)
    assert summary["integrity_all_pass"] is True
    assert summary["outcome_label"] == "ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED"
    assert summary["shape_is_frozen_640"] is False
    assert summary["cells"]["adaptive_only"] == 0 and summary["cells"]["static_only"] == 0
    assert summary["planning_only_f"]["denominator_reference_bits"] == al.PLANNING_DENOMINATOR_BITS
    assert summary["wall_s"] >= 0.0
    assert summary["rss_bytes_peak"] is None or summary["rss_bytes_peak"] > 0
    assert summary["claim_scope"] == al.CLAIM_SCOPE

    report = (root / "report.md").read_text(encoding="utf-8")
    assert "synthetic N=256 development evidence only" in report
    assert "not real-channel FER" in report
    assert "ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED" in report
    assert elapsed < 600.0


def test_p6_runner_refusals_without_decoder_calls():
    def forbidden_decode(*args, **kwargs):
        raise AssertionError("decoder must not run before refusals")

    sandbox = Path(tempfile.mkdtemp())
    existing = sandbox / "exists"
    existing.mkdir()
    never = sandbox / "never"
    base = {
        "n": 256,
        "epsilon1": 0.05,
        "profile": "strong",
        "k1_levels": list(al.FROZEN_K1_LEVELS),
        "k2": 140,
        "seeds": [TEST_SEED_A],
        "blocks_per_seed": 1,
    }
    with patched(tl, "sc_decode", forbidden_decode):
        assert_raises_match(
            FileExistsError,
            "refusing to overwrite",
            al.run_adaptive_gate,
            out_dir=str(existing),
            **base,
        )
        for banned in (2026091213, 2026091351, 2026091360, 2026091510):
            with_kwargs = dict(base)
            with_kwargs["seeds"] = [banned]
            assert_raises_match(
                ValueError,
                "banned",
                al.run_adaptive_gate,
                out_dir=str(never),
                **with_kwargs,
            )
        for override in (
            {"profile": "weak"},
            {"profile": "bogus"},
            {"k1_levels": [45, 60, 72]},
            {"k1_levels": [45, 60, 72, 113]},
            {"k2": 141},
            {"n": 128},
            {"epsilon1": 0.10},
            {"seeds": [TEST_SEED_A, TEST_SEED_A]},
        ):
            with_kwargs = dict(base)
            with_kwargs.update(override)
            assert_raises_match(
                ValueError, "", al.run_adaptive_gate, out_dir=str(never), **with_kwargs
            )
        # The p2_maxdiff floor refuses before any decoder call; no root created.
        floor_root = sandbox / "floor"
        with patched(pg, "p2_cross_u1_maxdiff", lambda p2: 0.1):
            assert_raises_match(
                ValueError,
                "p2_maxdiff",
                al.run_adaptive_gate,
                out_dir=str(floor_root),
                **base,
            )
    assert not never.exists() and not floor_root.exists()

    parser = al.build_parser()
    frozen_argv = [
        "--n", "256", "--epsilon1", "0.05", "--profile", "strong",
        "--k1-levels", "45", "60", "72", "112", "--k2", "140",
        "--seeds", str(TEST_SEED_A), "--blocks-per-seed", "1",
        "--out-dir", "example_root",
    ]
    args = parser.parse_args(frozen_argv)
    assert args.n == 256 and args.epsilon1 == 0.05 and args.profile == "strong"
    assert args.k1_levels == [45, 60, 72, 112] and args.k2 == 140
    assert args.blocks_per_seed == 1 and args.seeds == [TEST_SEED_A]
    option_pairs = [
        ("--n", "256"), ("--epsilon1", "0.05"), ("--profile", "strong"),
        ("--k1-levels", "45 60 72 112"), ("--k2", "140"), ("--seeds", str(TEST_SEED_A)),
        ("--blocks-per-seed", "1"), ("--out-dir", "example_root"),
    ]
    for drop in range(len(option_pairs)):
        reduced = []
        for index, (flag, value) in enumerate(option_pairs):
            if index != drop:
                reduced.extend([flag, *value.split()])
        assert_raises_match(SystemExit, "", parser.parse_args, reduced)
    assert al.main(
        [
            "--n", "256", "--epsilon1", "0.05", "--profile", "strong",
            "--k1-levels", "45", "60", "72", "112", "--k2", "140",
            "--seeds", "2026091510", "--blocks-per-seed", "1",
            "--out-dir", str(never),
        ]
    ) == 2
    assert not never.exists()


def test_p6_resource_abort_and_truth_leak_gate_paths():
    root = Path(tempfile.mkdtemp()) / "abort"
    run = al.run_adaptive_gate(
        n=256,
        epsilon1=0.05,
        profile="strong",
        k1_levels=list(al.FROZEN_K1_LEVELS),
        k2=140,
        seeds=[TEST_SEED_G],
        blocks_per_seed=2,
        out_dir=str(root),
        total_wall_s=1e-6,
    )
    assert run.summary["resource_stop_fired"] is True
    assert run.summary["integrity"]["resource_abort_zero"] is False
    assert run.summary["integrity"]["pairing_coverage_complete"] is True
    assert run.summary["outcome_label"] == "BLOCKED"
    assert "resource_abort_zero" in run.summary["failing_integrity_gates"]
    assert sorted(path.name for path in root.iterdir()) == sorted(al.OUTPUT_FILES)

    root2 = Path(tempfile.mkdtemp()) / "leak"
    with patched(tl, "_truth_isolation_sentinel", lambda *a, **k: False):
        run2 = al.run_adaptive_gate(
            n=256,
            epsilon1=0.05,
            profile="strong",
            k1_levels=list(al.FROZEN_K1_LEVELS),
            k2=140,
            seeds=[TEST_SEED_G],
            blocks_per_seed=1,
            out_dir=str(root2),
        )
    assert run2.summary["integrity"]["provenance_and_truth_isolation_complete"] is False
    assert run2.summary["integrity_all_pass"] is False
    assert run2.summary["outcome_label"] == "BLOCKED"
    assert "provenance_and_truth_isolation_complete" in run2.summary["failing_integrity_gates"]


def test_p6_frozen_constants_and_fresh_test_seeds():
    assert al.FROZEN_SEEDS == (2026091550, 2026091551, 2026091552, 2026091553, 2026091554)
    assert al.FROZEN_BLOCKS_PER_SEED == 128 and al.FROZEN_PAIRS == 640
    assert al.PUBLIC_TAG_MASTER_OFFSET == 10000
    assert al.FROZEN_N == 256 and al.FROZEN_EPSILON1 == 0.05 and al.FROZEN_PROFILE == "strong"
    assert al.FROZEN_K1_LEVELS == (45, 60, 72, 112) and al.FROZEN_K2 == 140
    assert al.PROFILE_MEAN_EPSILON2 == 0.20
    assert al.TAG_BITS == 64 and al.DISCLOSED_BITS_PER_COORDINATE == 5
    assert al.FEEDBACK_CONTROL_BITS == 1
    assert tl.seed_bits_for(256) == 2623
    assert al.ATTEMPT_ACCOUNTING == {
        "attempts_allowed": 1,
        "attempts_consumed_before": 0,
        "attempts_consumed_by_this_run": 1,
        "retries": 0,
    }
    required_refusals = (
        set(range(2026091200, 2026091214))
        | set(range(2026091314, 2026091322))
        | {2026091330, 2026091340, 2026091341, 2026091350, 2026091351}
        | {2026091360, 2026091361}
        | set(range(2026091400, 2026091405))
        | set(range(2026091410, 2026091415))
        | set(range(2026091420, 2026091425))
        | set(range(2026091430, 2026091435))
        | set(range(2026091450, 2026091453))
        | set(range(2026091470, 2026091473))
        | set(range(2026091490, 2026091495))
        | set(range(2026091510, 2026091515))
    )
    assert al.BANNED_SEEDS == frozenset(required_refusals)
    for banned in sorted(required_refusals):
        assert banned in al.BANNED_SEEDS
    for seed in al.FROZEN_SEEDS:
        assert seed not in al.BANNED_SEEDS
        assert seed + al.PUBLIC_TAG_MASTER_OFFSET not in al.BANNED_SEEDS
    for seed in TEST_SEEDS:
        assert seed >= 2026091560
        assert seed not in al.BANNED_SEEDS and seed not in al.FROZEN_SEEDS
    command_lines = al.FROZEN_COMMAND.splitlines()
    assert len(command_lines) == 3
    assert command_lines[0] == "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
    assert command_lines[1] == "ulimit -v 2097152"
    assert command_lines[2].startswith(
        "timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
        "comparison_bench.src.comparison_bench.formal_ir.nbpolar.adaptive_l1 "
    )
    assert "--n 256 --epsilon1 0.05 --profile strong" in command_lines[2]
    assert "--k1-levels 45 60 72 112" in command_lines[2]
    assert "--k2 140" in command_lines[2]
    assert "--seeds 2026091550 2026091551 2026091552 2026091553 2026091554" in command_lines[2]
    assert "--blocks-per-seed 128" in command_lines[2]
    assert command_lines[2].endswith(
        "--out-dir ." + "workbuddy/queue/"
        "NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive" + "_gate"
    )
    own = Path(__file__).read_text(encoding="utf-8")
    assert ("." + "workbuddy") not in own
    assert ("paired_adaptive" + "_gate") not in own
    for seed in al.FROZEN_SEEDS:
        assert f"default_rng({seed})" not in own


def test_p6_entropy_and_p2_maxdiff_conventions():
    table = pg.build_dependent_joint_table(profile="strong", epsilon1=0.05)
    _, p2_table = tl.layer_metric_tables(table)
    assert abs(pg.p2_cross_u1_maxdiff(p2_table) - 0.34875) < 1e-12
    entropy = al.h_a_given_b_from_table(table)
    assert abs(entropy["h_a_given_b_bits"] - al.H_A_GIVEN_B_REFERENCE_BITS) < 1e-12
    assert abs(entropy["chain_vs_direct_abs_diff"]) < 1e-12
    assert abs(256 * entropy["h_a_given_b_bits"] - al.PLANNING_DENOMINATOR_BITS) < 1e-9
    assert abs(1324 / al.PLANNING_DENOMINATOR_BITS - 2.423509842447853) < 1e-12


def test_p6_no_forbidden_markers_or_import_time_effects():
    import re

    source = Path(al.__file__).read_text(encoding="utf-8")
    lowered = source.lower()
    for marker in FORBIDDEN_MARKERS:
        assert marker not in lowered, f"forbidden marker {marker!r} in adaptive_l1.py"
    for match in re.finditer(r"np\.random\.([A-Za-z_]+)\s*\(", source):
        assert match.group(1) == "default_rng", f"global RNG use: {match.group(0)}"
    assert "open(" not in source

    empty = Path(tempfile.mkdtemp())
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import comparison_bench.src.comparison_bench.formal_ir.nbpolar.adaptive_l1 as a; "
            "assert a.FROZEN_PAIRS == 640 and a.OUTPUT_FILES[0] == 'frozen_plan.json'",
        ],
        cwd=str(empty),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert list(empty.iterdir()) == []


if __name__ == "__main__":
    names = sorted(n for n, v in sorted(globals().items())
                   if n.startswith("test_") and callable(v))
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
