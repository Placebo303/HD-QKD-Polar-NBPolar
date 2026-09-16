"""Focused Phase 6 fixed incremental protocol tests (P6-A01..A12 + refusals).

Synthetic/injected fixtures only. No Model-F artifact, parquet, TTBin, real
frame, DEV/EVAL, sibling read, or output file outside a temporary directory.
The reserved scientific seeds 2026091340/2026091341 are never used here;
tests use 2026091342/2026091343/2026091344 only.

Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments, uses plain
asserts, and restores any monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import dataclasses
import importlib.util
import inspect
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

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    incremental as inc,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    protocol as proto,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
    make_gf32,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.construction import (
    analytic_order,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.synthetic import (
    generate_erasure_block,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
    polar_transform,
)
from comparison_bench.src.comparison_bench.formal_ir.shared import (
    toeplitz_tag,
    verification_union_bound,
)

FIELD = make_gf32()
REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_SEED_A = 2026091342
TEST_SEED_B = 2026091343
TEST_SEED_C = 2026091344
EVIDENCE = {"predecessor_seconds": None, "predecessor_count": 0}


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:  # noqa: BLE001 -- exact class is the assertion
        assert substr in str(err), f"expected {substr!r} in {err!r}"
    else:
        raise AssertionError(f"expected {exc.__name__} containing {substr!r}")


@contextlib.contextmanager
def patched(module, name, replacement):
    original = getattr(module, name)
    setattr(module, name, replacement)
    try:
        yield
    finally:
        setattr(module, name, original)


def noiseless_logp(x, q: int = 32):
    x = np.asarray(x, dtype=np.int64)
    logp = np.full((x.size, q), -np.inf)
    logp[np.arange(x.size), x] = 0.0
    return logp


def seeded_block(seed, n: int = 256, eps: float = 0.05):
    rng = np.random.default_rng(seed)
    return generate_erasure_block(rng, 32, n, eps)


def scripted_tag(match_level: int, calls: dict):
    """Tag function: mismatch levels < ``match_level``, honest at ``match_level``.

    Two calls per level (Alice tag, Bob tag); a mismatch returns a different
    constant per parity so the two tag values never agree.
    """

    def tag(bits, seed, tag_bits=64):
        calls["n"] += 1
        level, parity = divmod(calls["n"] - 1, 2)
        if level < match_level:
            return b"\x01" * 8 if parity == 0 else b"\x02" * 8
        return toeplitz_tag(bits, seed, tag_bits)

    return tag


def colliding_tag(bits, seed, tag_bits=64):
    return b"\x2a" * 8


def temp_root(name: str) -> Path:
    return Path(tempfile.mkdtemp()) / name


def test_a01_nested_sets_equal_analytic_prefixes_and_strict_nesting():
    nested = inc.build_nested_schedule()
    assert nested.sizes == inc.FROZEN_K == (29, 33, 37, 41, 45)
    assert nested.n == 256 and nested.epsilon == 0.05
    order = analytic_order(0.05, 256)
    for k, positions in zip(nested.sizes, nested.sets):
        assert positions.shape == (k,)
        assert np.array_equal(positions, np.sort(order[:k]))
        assert len(set(positions.tolist())) == k
    assert nested.order_prefix_matches is True
    assert nested.strict_nesting is True
    assert nested.new_coordinates_disjoint is True
    for i in range(len(nested.sets) - 1):
        assert len(nested.sets[i]) < len(nested.sets[i + 1])
        assert bool(np.isin(nested.sets[i], nested.sets[i + 1]).all())
        assert len(nested.new_positions[i + 1]) == nested.sizes[i + 1] - nested.sizes[i]
    flat = [int(v) for arr in nested.new_positions for v in arr.tolist()]
    assert sorted(flat) == nested.sets[-1].tolist()
    assert len(flat) == len(set(flat)) == 45
    # D_4 is exactly the accepted Phase 5 static K=45 set.
    assert np.array_equal(nested.sets[-1], proto.static_disclosure_coordinates(256, 45))

    tiny = inc.build_nested_schedule(n=8, sizes=(2, 3, 4))
    assert tiny.strict_nesting and tiny.order_prefix_matches and tiny.new_coordinates_disjoint
    assert [len(arr) for arr in tiny.new_positions] == [2, 1, 1]
    assert_raises_match(ValueError, "strictly increasing", inc.build_nested_schedule, sizes=(3, 3))
    assert_raises_match(ValueError, "strictly increasing", inc.build_nested_schedule, sizes=(4, 2))
    assert_raises_match(ValueError, "power of two", inc.build_nested_schedule, n=6, sizes=(2,))


def test_a02_incremental_only_transmission_zeros_round_trip_counted_once():
    nested = inc.build_nested_schedule()
    x = np.zeros(256, dtype=np.int64)
    logp = noiseless_logp(x)
    captured = {"positions": [], "values": []}
    real_decode = inc.sc_decode

    def spy_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        captured["positions"].append(np.array(known_positions, dtype=np.int64))
        captured["values"].append(np.array(known_values, dtype=np.int64))
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    tag_calls = {"n": 0}
    with patched(inc, "sc_decode", spy_decode), patched(
        inc, "toeplitz_tag", scripted_tag(99, tag_calls)
    ):
        result = inc.run_incremental_block(0, x, logp, field=FIELD)
    assert result.outcome == "verify_failed"  # every level forced to mismatch
    assert len(captured["positions"]) == 5
    u_true = polar_transform(x, field=FIELD)
    for level, positions in enumerate(captured["positions"]):
        assert np.array_equal(positions, nested.sets[level])
        assert np.array_equal(captured["values"][level], u_true[positions])
        assert int(np.count_nonzero(captured["values"][level] == 0)) == len(positions)
    # Only newly added coordinates are transmitted per level; counted once.
    events = inc.incremental_block_events(result, nested)
    disclosure_bits = [
        event["key_dependent_bits"] for event in events if event["event_type"] == "incremental_disclosure"
    ]
    assert disclosure_bits == [5 * len(arr) for arr in nested.new_positions]
    assert sum(disclosure_bits) == 5 * 45
    assert result.key_dependent_bits == 5 * 45 + 64 * 5
    assert inc.incremental_record_consistent(result, nested)

    # Mixed zero/non-zero disclosed values are actual U values, never sentinels.
    found = None
    for candidate in (3, 7, 11, 5, 1):
        x_mixed = np.zeros(8, dtype=np.int64)
        x_mixed[2] = candidate
        u_mixed = polar_transform(x_mixed, field=FIELD)
        tiny = inc.build_nested_schedule(n=8, sizes=(2, 3, 4))
        values = u_mixed[tiny.sets[-1]]
        if int(np.count_nonzero(values == 0)) > 0 and int(np.count_nonzero(values != 0)) > 0:
            found = (x_mixed, tiny, u_mixed)
            break
    assert found is not None, "expected a tiny U vector mixing zero and non-zero values"
    x_mixed, tiny, u_mixed = found
    tiny_capture = {"positions": [], "values": []}

    def spy_tiny(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        tiny_capture["positions"].append(np.array(known_positions, dtype=np.int64))
        tiny_capture["values"].append(np.array(known_values, dtype=np.int64))
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(inc, "sc_decode", spy_tiny):
        tiny_result = inc.run_incremental_block(
            0, x_mixed, noiseless_logp(x_mixed), field=FIELD, n=8, sizes=(2, 3, 4)
        )
    assert tiny_result.outcome == "exact" and tiny_result.accepted_level == 0
    assert np.array_equal(tiny_capture["positions"][0], tiny.sets[0])
    assert np.array_equal(tiny_capture["values"][0], u_mixed[tiny.sets[0]])


def test_a03_every_invoked_level_restarts_from_original_metric():
    x, _y, _logp = seeded_block(TEST_SEED_A)
    logp = noiseless_logp(x)
    logp_snapshot = logp.copy()
    nested = inc.build_nested_schedule()
    u_true = polar_transform(x, field=FIELD)
    seen = {"metrics": [], "positions": [], "values": [], "kwargs": []}
    real_decode = inc.sc_decode

    def spy_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        seen["metrics"].append(np.array(logp_x, copy=True))
        seen["positions"].append(np.array(known_positions, dtype=np.int64))
        seen["values"].append(np.array(known_values, dtype=np.int64))
        seen["kwargs"].append({"alpha": alpha, "field": field})
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    tag_calls = {"n": 0}
    with patched(inc, "sc_decode", spy_decode), patched(
        inc, "toeplitz_tag", scripted_tag(4, tag_calls)
    ):
        result = inc.run_incremental_block(0, x, logp, field=FIELD)

    assert result.outcome == "exact" and result.accepted_level == 4
    assert result.levels_invoked == 5 and result.tag_invocations == 5
    assert result.feedback_control_invocations == 4
    assert result.key_dependent_bits == 5 * 45 + 64 * 5
    assert len(seen["metrics"]) == 5
    for level, metric in enumerate(seen["metrics"]):
        assert np.array_equal(metric, logp_snapshot), f"level {level} did not receive the original metric"
        assert np.array_equal(seen["positions"][level], nested.sets[level])
        assert np.array_equal(seen["values"][level], u_true[nested.sets[level]])
        assert seen["kwargs"][level]["alpha"] == 2
        assert seen["kwargs"][level]["field"] is FIELD
    # The caller's Bob metric is untouched by either the decoder or the sentinel.
    assert np.array_equal(logp, logp_snapshot)
    assert inc.incremental_record_consistent(result, nested)

    # A second identical run sees the same fresh sequence (no hidden state).
    again = {"metrics": [], "positions": []}

    def spy_again(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        again["metrics"].append(np.array(logp_x, copy=True))
        again["positions"].append(np.array(known_positions, dtype=np.int64))
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    tag_calls2 = {"n": 0}
    with patched(inc, "sc_decode", spy_again), patched(
        inc, "toeplitz_tag", scripted_tag(4, tag_calls2)
    ):
        result2 = inc.run_incremental_block(0, x, logp, field=FIELD)
    assert result2.accepted_level == 4
    assert len(again["metrics"]) == 5
    for metric in again["metrics"]:
        assert np.array_equal(metric, logp_snapshot)


def test_a04_tag_mismatch_advances_exactly_one_level_no_selection():
    x, _y, _logp = seeded_block(TEST_SEED_B)
    logp = noiseless_logp(x)
    nested = inc.build_nested_schedule()
    for match_level in range(5):
        calls = {"n": 0}
        decode_calls = []
        real_decode = inc.sc_decode

        def spy_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
            decode_calls.append(np.array(known_positions, dtype=np.int64))
            return real_decode(
                logp_x, field=field, alpha=alpha,
                known_positions=known_positions, known_values=known_values,
            )

        with patched(inc, "sc_decode", spy_decode), patched(
            inc, "toeplitz_tag", scripted_tag(match_level, calls)
        ):
            result = inc.run_incremental_block(0, x, logp, field=FIELD)
        assert result.outcome == "exact"
        assert result.accepted_level == match_level
        assert len(decode_calls) == match_level + 1  # one decode per invoked level, no retry
        for level, positions in enumerate(decode_calls):
            assert np.array_equal(positions, nested.sets[level])  # no skip, no reorder
        assert result.tag_invocations == match_level + 1
        assert result.feedback_control_invocations == match_level
        assert result.key_dependent_bits == 5 * nested.sizes[match_level] + 64 * (match_level + 1)
        assert inc.incremental_record_consistent(result, nested)


def test_a05_injected_equal_tag_forces_undetected_never_success():
    x, _y, logp = seeded_block(TEST_SEED_C)
    nested = inc.build_nested_schedule()
    real_decode = inc.sc_decode

    def wrong_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        real = real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )
        wrong_u = real.u_hat.copy()
        wrong_u[0] = (int(wrong_u[0]) + 1) % 32
        return dataclasses.replace(
            real, u_hat=wrong_u, x_hat=polar_transform(wrong_u, field=FIELD)
        )

    with patched(inc, "sc_decode", wrong_decode), patched(inc, "toeplitz_tag", colliding_tag):
        result = inc.run_incremental_block(0, x, logp, field=FIELD)
    assert result.outcome == "undetected"
    assert result.exact is False and result.outcome != "exact"
    assert result.accepted_level == 0 and result.tag_invocations == 1
    assert inc.incremental_record_consistent(result, nested)

    root = temp_root("paired_incremental_dev_gate")
    with patched(inc, "sc_decode", wrong_decode), patched(inc, "toeplitz_tag", colliding_tag):
        run = inc.run_paired_dev_gate(run_seed=TEST_SEED_C, blocks=2, out_root=str(root))
    aggregate = run["aggregate"]
    assert aggregate["incremental"]["outcome_totals"]["undetected"] == 2
    assert aggregate["incremental"]["outcome_totals"]["exact"] == 0
    assert aggregate["hard_gates"]["incremental_undetected_zero"] is False
    assert aggregate["candidate"] is None


def test_a06_decode_failure_stop_fail_closed_and_final_mismatch():
    x, _y, logp = seeded_block(TEST_SEED_A)
    nested = inc.build_nested_schedule()
    real_decode = inc.sc_decode
    for fail_level in range(5):
        decode_state = {"n": 0}
        tag_state = {"n": 0}

        def failing_decode(*args, **kwargs):
            index = decode_state["n"]
            decode_state["n"] += 1
            if index == fail_level:
                raise inc.NumericNonfiniteError("numeric nonfinite failure: injected")
            return real_decode(*args, **kwargs)

        # Earlier levels must advance on mismatching tags to reach the failing level.
        with patched(inc, "sc_decode", failing_decode), patched(
            inc, "toeplitz_tag", scripted_tag(99, tag_state)
        ):
            result = inc.run_incremental_block(0, x, logp, field=FIELD)
        assert result.outcome == "decode_failed"
        assert result.decode_failed_level == fail_level
        assert result.levels_invoked == fail_level + 1
        assert decode_state["n"] == fail_level + 1  # no further level was invoked
        assert tag_state["n"] == fail_level * 2  # no tag at the failing level or after it
        assert result.tag_invocations == fail_level
        assert result.feedback_control_invocations == fail_level
        assert result.key_dependent_bits == 5 * inc.FROZEN_K[fail_level] + 64 * fail_level
        assert result.nonfinite is True
        assert inc.incremental_record_consistent(result, nested)

    # Nonfinite decision marginals (not an exception) also fail closed.
    nan_decode_state = {"n": 0}

    def nan_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        nan_decode_state["n"] += 1
        real = real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )
        bad = np.array(real.decision_metrics, copy=True)
        bad[0, 0] = np.nan
        return dataclasses.replace(real, decision_metrics=bad)

    with patched(inc, "sc_decode", nan_decode):
        nan_result = inc.run_incremental_block(0, x, logp, field=FIELD)
    assert nan_result.outcome == "decode_failed" and nan_result.nonfinite is True
    assert nan_decode_state["n"] == 1  # stop fail-closed after the first level
    assert nan_result.key_dependent_bits == 5 * inc.FROZEN_K[0]

    # Forced all-level mismatch: verify_failed after exactly 5 tag invocations.
    tag_calls = {"n": 0}
    decode_count = {"n": 0}

    def counting_decode(*args, **kwargs):
        decode_count["n"] += 1
        return real_decode(*args, **kwargs)

    with patched(inc, "sc_decode", counting_decode), patched(
        inc, "toeplitz_tag", scripted_tag(99, tag_calls)
    ):
        failed = inc.run_incremental_block(0, x, logp, field=FIELD)
    assert failed.outcome == "verify_failed"
    assert failed.levels_invoked == 5
    assert failed.tag_invocations == 5
    assert failed.feedback_control_invocations == 4
    assert failed.key_dependent_bits == 5 * 45 + 64 * 5
    assert decode_count["n"] == 5
    assert tag_calls["n"] == 10  # 5 levels, 2 tag computations each, then stop
    assert inc.incremental_record_consistent(failed, nested)


def test_a07_cumulative_accounting_literal_recount_and_tamper():
    root = temp_root("paired_incremental_dev_gate")
    run = inc.run_paired_dev_gate(run_seed=TEST_SEED_B, blocks=4, out_root=str(root))
    nested = run["nested"]
    for result in run["incremental_results"]:
        assert inc.incremental_record_consistent(result, nested)
    for result in run["static_results"]:
        assert inc.static_record_consistent(result, 256, 45)

    # Independent literal recount (does not call inc.recount_transcript).
    key = sum(int(event["key_dependent_bits"]) for event in run["incremental_events"])
    public = sum(int(event["public_control_bits"]) for event in run["incremental_events"])
    tags = sum(1 for event in run["incremental_events"] if event["event_type"] == "verification_tag")
    controls = sum(1 for event in run["incremental_events"] if event["event_type"] == "control")
    assert key == run["incremental_totals"]["key_dependent_bits"]
    assert public == run["incremental_totals"]["public_control_bits"]
    assert tags == run["incremental_totals"]["verification_invocations"]
    assert controls == run["incremental_totals"]["feedback_control_invocations"]
    assert run["accounting"]["incremental"]["mismatch_count"] == 0
    assert run["accounting"]["incremental"]["recount"]["key_dependent_bits"] == key
    assert run["accounting"]["static"]["mismatch_count"] == 0
    static_key = sum(int(event["key_dependent_bits"]) for event in run["static_events"])
    static_public = sum(int(event["public_control_bits"]) for event in run["static_events"])
    assert static_key == run["static_totals"]["key_dependent_bits"]
    assert static_public == run["static_totals"]["public_control_bits"]

    # Transcript tampering must be detected by the recount.
    tampered = [dict(event) for event in run["incremental_events"]]
    tampered[0]["key_dependent_bits"] += 5
    assert inc.recount_transcript(tampered)["key_dependent_bits"] != key
    # Control-event tampering is proven on a forced multi-level block.
    x_forced, _y, _logp = seeded_block(TEST_SEED_C)
    forced = inc.run_incremental_block(
        0, x_forced, noiseless_logp(x_forced), field=FIELD, tag_fn=scripted_tag(2, {"n": 0})
    )
    forced_events = inc.incremental_block_events(forced, nested)
    forced_controls = sum(1 for event in forced_events if event["event_type"] == "control")
    assert forced.accepted_level == 2 and forced_controls == 2
    tampered2 = [dict(event) for event in forced_events]
    for event in tampered2:
        if event["event_type"] == "control":
            event["event_type"] = "incremental_disclosure"
            break
    assert inc.recount_transcript(tampered2)["feedback_control_invocations"] != forced_controls
    tampered3 = [dict(event) for event in run["static_events"]]
    for event in tampered3:
        if event["event_type"] == "verification_tag":
            event["public_control_bits"] -= 1
            break
    assert inc.recount_transcript(tampered3)["public_control_bits"] != static_public

    # Record tampering must be detected by the per-block consistency proof.
    first = run["incremental_results"][0]
    assert inc.incremental_record_consistent(first, nested) is True
    mutations = {
        "key_dependent_bits": first.key_dependent_bits + 64,
        "tag_invocations": first.tag_invocations + 1,
        "feedback_control_invocations": first.feedback_control_invocations + 1,
        "levels_invoked": first.levels_invoked + 1,
    }
    if first.outcome == "decode_failed":
        mutations["decode_failed_level"] = first.decode_failed_level + 1
    else:
        mutations["accepted_level"] = first.accepted_level + 1
    for field_name, bad_value in mutations.items():
        tampered_record = dataclasses.replace(first, **{field_name: bad_value})
        assert (
            inc.incremental_record_consistent(tampered_record, nested) is False
        ), f"tampered {field_name} was not detected"


def test_a08_seed_feedback_control_counting_and_union_bound():
    base = inc.block_toeplitz_seed_bits("static", 0, 0)
    assert base.shape == (2623,) and base.dtype == np.uint8
    assert set(np.unique(base).tolist()).issubset({0, 1})
    assert np.array_equal(base, inc.block_toeplitz_seed_bits("static", 0, 0))
    pairs = [
        ("static", 0, 0),
        ("incremental", 0, 0),
        ("incremental", 0, 1),
        ("incremental", 1, 0),
        ("incremental", 2, 3),
    ]
    seeds = [inc.block_toeplitz_seed_bits(*pair) for pair in pairs]
    for i in range(len(seeds)):
        for j in range(i + 1, len(seeds)):
            assert not np.array_equal(seeds[i], seeds[j])
    assert len(inc.block_toeplitz_seed_bits("incremental", 3, 2, 80)) == 80
    assert_raises_match(ValueError, "arm", inc.block_toeplitz_seed_bits, "other", 0, 0)
    assert_raises_match(ValueError, "block_index", inc.block_toeplitz_seed_bits, "static", -1, 0)
    assert_raises_match(ValueError, "level", inc.block_toeplitz_seed_bits, "static", 0, -1)

    # Forced 5-level block: every seed bit, control call and tag invocation is counted.
    x, _y, _logp = seeded_block(TEST_SEED_C)
    logp = noiseless_logp(x)
    tag_calls = {"n": 0}
    with patched(inc, "toeplitz_tag", scripted_tag(99, tag_calls)):
        result = inc.run_incremental_block(0, x, logp, field=FIELD)
    assert result.public_seed_bits == 5 * 2623
    assert result.feedback_control_invocations == 4
    assert result.feedback_control_bits == 4
    assert result.public_control_bits == 5 * 2623 + 4
    events = inc.incremental_block_events(result, inc.build_nested_schedule())
    assert inc.recount_transcript(events)["feedback_control_invocations"] == 4

    root = temp_root("paired_incremental_dev_gate")
    run = inc.run_paired_dev_gate(run_seed=TEST_SEED_A, blocks=3, out_root=str(root))
    bound = run["aggregate"]["union_bound"]
    assert bound["static"] == verification_union_bound(bound["static_tag_invocations"])
    assert bound["incremental"] == verification_union_bound(bound["incremental_tag_invocations"])
    assert bound["total"] == verification_union_bound(bound["total_tag_invocations"])
    assert bound["total"] == min(1.0, bound["total_tag_invocations"] * 2.0**-64)
    assert bound["recount_total_tag_invocations"] == bound["total_tag_invocations"]
    assert run["aggregate"]["hard_gates"]["union_bound_consistent"] is True
    assert run["aggregate"]["hard_gates"]["feedback_control_counted"] is True
    assert run["aggregate"]["hard_gates"]["public_control_counted"] is True
    assert (
        run["aggregate"]["public_control"]["total_public_control_bits"]
        == run["static_totals"]["public_control_bits"] + run["incremental_totals"]["public_control_bits"]
    )
    assert (
        run["aggregate"]["public_control"]["incremental_feedback_control_bits"]
        == run["incremental_totals"]["feedback_control_invocations"]
    )

    # Tampered invocation count breaks union-bound/recount consistency.
    fake = inc.recount_transcript(run["incremental_events"])
    fake["verification_invocations"] += 1
    assert verification_union_bound(fake["verification_invocations"]) != bound["incremental"]


def test_a09_buckets_disjoint_exhaustive_truth_leak_nonfinite_zero():
    x, _y, logp = seeded_block(TEST_SEED_B)
    nested = inc.build_nested_schedule()
    outcomes = {}

    outcomes["exact"] = inc.run_incremental_block(0, x, noiseless_logp(x), field=FIELD)
    tag_calls = {"n": 0}
    with patched(inc, "toeplitz_tag", scripted_tag(99, tag_calls)):
        outcomes["verify_failed"] = inc.run_incremental_block(0, x, noiseless_logp(x), field=FIELD)
    real_decode = inc.sc_decode

    def failing_decode(*args, **kwargs):
        raise inc.NumericNonfiniteError("numeric nonfinite failure: injected")

    with patched(inc, "sc_decode", failing_decode):
        outcomes["decode_failed"] = inc.run_incremental_block(0, x, noiseless_logp(x), field=FIELD)

    def wrong_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        real = real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )
        wrong_u = real.u_hat.copy()
        wrong_u[1] = (int(wrong_u[1]) + 1) % 32
        return dataclasses.replace(
            real, u_hat=wrong_u, x_hat=polar_transform(wrong_u, field=FIELD)
        )

    with patched(inc, "sc_decode", wrong_decode), patched(inc, "toeplitz_tag", colliding_tag):
        outcomes["undetected"] = inc.run_incremental_block(0, x, noiseless_logp(x), field=FIELD)
    outcomes["resource_abort"] = inc._abort_result(0, "incremental")
    assert {result.outcome for result in outcomes.values()} == set(inc.OUTCOMES)
    assert len(outcomes) == len(inc.OUTCOMES)
    for result in outcomes.values():
        assert inc.incremental_record_consistent(result, nested)

    # Disjoint/exhaustive totals across both arms and truth-leak/nonfinite zero.
    root = temp_root("paired_incremental_dev_gate")
    run = inc.run_paired_dev_gate(run_seed=TEST_SEED_B, blocks=5, out_root=str(root))
    aggregate = run["aggregate"]
    assert sum(aggregate["static"]["outcome_totals"].values()) == 5
    assert sum(aggregate["incremental"]["outcome_totals"].values()) == 5
    assert aggregate["hard_gates"]["outcome_buckets_disjoint_exhaustive_both_arms"] is True
    assert aggregate["hard_gates"]["truth_leak_zero"] is True
    assert aggregate["hard_gates"]["nonfinite_zero"] is True

    # The sentinel detects a decision that aliases a truth buffer.
    metric = np.zeros((3, 32), dtype=np.float64)
    decision = np.array([1, 2, 3], dtype=np.int64)
    assert inc.truth_isolation_sentinel(metric, [decision], [np.array([4, 5, 6])]) is True
    aliased = np.array([1, 2, 3], dtype=np.int64)
    assert inc.truth_isolation_sentinel(metric, [aliased], [aliased]) is False

    # Injected truth-leak and nonfinite violations must flip their gates.
    leak_root = temp_root("paired_incremental_dev_gate")
    with patched(inc, "truth_isolation_sentinel", lambda *a, **k: False):
        leak_run = inc.run_paired_dev_gate(run_seed=TEST_SEED_C, blocks=2, out_root=str(leak_root))
    assert leak_run["aggregate"]["hard_gates"]["truth_leak_zero"] is False
    assert leak_run["aggregate"]["candidate"] is None

    nan_state = {"n": 0}

    def nan_first_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        nan_state["n"] += 1
        real = real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )
        if nan_state["n"] == 1:
            bad = np.array(real.decision_metrics, copy=True)
            bad[0, 0] = np.nan
            return dataclasses.replace(real, decision_metrics=bad)
        return real

    nan_root = temp_root("paired_incremental_dev_gate")
    with patched(inc, "sc_decode", nan_first_decode):
        nan_run = inc.run_paired_dev_gate(run_seed=TEST_SEED_A, blocks=2, out_root=str(nan_root))
    assert nan_run["aggregate"]["hard_gates"]["nonfinite_zero"] is False
    assert nan_run["aggregate"]["nonfinite_count"]["static"] == 1
    assert nan_run["aggregate"]["candidate"] is None


def test_a10_paired_identity_identical_blocks_identical_metric():
    sequence = []
    real_generate = inc.generate_erasure_block
    real_decode = inc.sc_decode

    def generate_spy(rng, q, n, epsilon):
        x, y, logp = real_generate(rng, q, n, epsilon)
        sequence.append(("generate", x.copy(), logp.copy()))
        return x, y, logp

    def decode_spy(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        sequence.append(
            ("decode", np.array(known_positions, dtype=np.int64), np.array(logp_x, copy=True))
        )
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    root = temp_root("paired_incremental_dev_gate")
    with patched(inc, "generate_erasure_block", generate_spy), patched(
        inc, "sc_decode", decode_spy
    ):
        run = inc.run_paired_dev_gate(run_seed=TEST_SEED_A, blocks=3, out_root=str(root))

    groups = []
    current = None
    for item in sequence:
        if item[0] == "generate":
            current = {"x": item[1], "logp": item[2], "decodes": []}
            groups.append(current)
        else:
            assert current is not None
            current["decodes"].append((item[1], item[2]))
    assert len(groups) == 3  # exactly one generator draw per paired block
    rng_reference = np.random.default_rng(TEST_SEED_A)
    for block_index, group in enumerate(groups):
        x_ref, _y, logp_ref = generate_erasure_block(rng_reference, 32, 256, 0.05)
        assert np.array_equal(group["x"], x_ref)
        assert np.array_equal(group["logp"], logp_ref)
        assert group["decodes"], "each block must run at least the static comparator"
        assert group["decodes"][0][0].shape == (45,)
        assert np.array_equal(group["decodes"][0][0], proto.static_disclosure_coordinates(256, 45))
        for positions, metric in group["decodes"]:
            assert np.array_equal(metric, logp_ref), "an arm did not see the original metric"
    assert all(record["paired_match"] for record in run["paired_records"])
    assert run["aggregate"]["hard_gates"]["paired_identical_blocks"] is True

    # A mutating arm must be detected and must fail the pairing gate.
    original_static = inc.run_static_comparator_block

    def mutating_static(block_index, x, logp, **kwargs):
        logp[0, 0] = 12345.0
        return original_static(block_index, x, logp, **kwargs)

    mutant_root = temp_root("paired_incremental_dev_gate")
    with patched(inc, "run_static_comparator_block", mutating_static):
        mutant = inc.run_paired_dev_gate(run_seed=TEST_SEED_B, blocks=2, out_root=str(mutant_root))
    assert any(record["paired_match"] is False for record in mutant["paired_records"])
    assert mutant["aggregate"]["hard_gates"]["paired_identical_blocks"] is False
    assert mutant["aggregate"]["candidate"] is None


def test_a11_signatures_comparator_equivalence_and_predecessor_suite():
    from comparison_bench.src.comparison_bench.methods import nbpolar_incremental as adapter_mod
    from comparison_bench.src.comparison_bench.methods.base import IRMethod
    from comparison_bench.src.comparison_bench.types import FrameBatch, IRRunConfig, IRRunResult

    assert [f.name for f in dataclasses.fields(FrameBatch)] == [
        "dataset_id", "alice_symbols", "bob_symbols", "dimension", "frame_len_symbols", "metadata"
    ]
    assert [f.name for f in dataclasses.fields(IRRunConfig)] == [
        "method", "method_variant", "dimension", "frame_len_symbols", "max_iter",
        "qber_estimate", "ser_estimate", "verify_mode", "notes"
    ]
    assert [f.name for f in dataclasses.fields(IRRunResult)] == [
        "dataset_id", "method", "method_variant", "frame_len_symbols", "frame_len_bits",
        "n_frames_total", "n_frames_attempted", "n_frames_success", "n_frames_failed_decode",
        "n_frames_failed_verify", "raw_ser", "raw_ber", "post_ir_ser", "post_ir_ber",
        "leak_EC_actual_bits", "leak_EC_per_frame", "leak_EC_per_input_bit",
        "beta_eff_empirical", "runtime_s", "throughput_input_bits_per_s",
        "throughput_output_bits_per_s", "metadata"
    ]
    assert issubclass(adapter_mod.NBPolarIncrementalMethod, IRMethod)
    assert list(inspect.signature(adapter_mod.NBPolarIncrementalMethod.run).parameters) == [
        "self", "batch", "cfg"
    ]
    assert list(inspect.signature(inc.run_static_comparator_block).parameters) == [
        "block_index", "x", "logp", "field", "n", "k", "tag_fn"
    ]
    assert list(inspect.signature(inc.run_incremental_block).parameters) == [
        "block_index", "x", "logp", "field", "n", "sizes", "nested", "tag_fn"
    ]
    assert list(inspect.signature(inc.run_paired_dev_gate).parameters) == [
        "run_seed", "blocks", "out_root", "total_wall_s", "per_paired_block_soft_cap_s"
    ]

    # Static comparator semantics equivalence with the accepted Phase 5 block.
    for block_index, seed in enumerate((TEST_SEED_A, TEST_SEED_B, TEST_SEED_C)):
        x, _y, logp = seeded_block(seed)
        comparator = inc.run_static_comparator_block(block_index, x, logp, field=FIELD)
        reference = proto.run_static_block(block_index, x, logp, field=FIELD)
        assert comparator.outcome == reference.outcome
        assert comparator.exact == reference.exact
        assert comparator.pre_symbol_errors == reference.pre_symbol_errors
        assert comparator.pre_bit_errors == reference.pre_bit_errors
        assert comparator.symbol_errors == reference.symbol_errors
        assert comparator.bit_errors == reference.bit_errors
        assert comparator.key_dependent_bits == reference.key_dependent_bits
        assert comparator.public_control_bits == reference.public_control_bits
        assert comparator.public_control_bits == 2623

    # Tags differ only by seed: same message bits, P6 vs P5 seed derivation.
    x, _y, logp = seeded_block(TEST_SEED_A)
    seen = {"p6": [], "p5": []}
    original_p6_tag = inc.toeplitz_tag
    original_p5_tag = proto.toeplitz_tag

    def tag6(bits, seed, tag_bits=64):
        seen["p6"].append((np.array(bits, copy=True), np.array(seed, copy=True)))
        return original_p6_tag(bits, seed, tag_bits)

    def tag5(bits, seed, tag_bits=64):
        seen["p5"].append((np.array(bits, copy=True), np.array(seed, copy=True)))
        return original_p5_tag(bits, seed, tag_bits)

    with patched(inc, "toeplitz_tag", tag6), patched(proto, "toeplitz_tag", tag5):
        comparator = inc.run_static_comparator_block(0, x, logp, field=FIELD)
        reference = proto.run_static_block(0, x, logp, field=FIELD)
    assert comparator.outcome == reference.outcome == "exact"
    assert len(seen["p6"]) == 2 and len(seen["p5"]) == 2
    for i in range(2):
        assert np.array_equal(seen["p6"][i][0], seen["p5"][i][0])
        assert seen["p6"][i][1].shape == (2623,) and seen["p5"][i][1].shape == (2623,)
        assert not np.array_equal(seen["p6"][i][1], seen["p5"][i][1])
    assert np.array_equal(seen["p6"][0][1], inc.block_toeplitz_seed_bits("static", 0, 0))
    assert np.array_equal(seen["p5"][0][1], proto.block_toeplitz_seed_bits(0))
    assert orig_p6_seed_tag(seen, original_p6_tag) == orig_p5_seed_tag(seen, original_p5_tag)

    # Decode failure semantics match on an impossible disclosed value.
    x1 = np.random.default_rng(TEST_SEED_C).integers(0, 32, size=256).astype(np.int64)
    x2 = x1.copy()
    x2[0] = (int(x2[0]) + 1) % 32
    impossible_metric = noiseless_logp(x1)
    p6_fail = inc.run_static_comparator_block(0, x2, impossible_metric, field=FIELD)
    p5_fail = proto.run_static_block(0, x2, impossible_metric, field=FIELD)
    assert p6_fail.outcome == p5_fail.outcome == "decode_failed"
    assert p6_fail.error_type == p5_fail.error_type
    assert p6_fail.key_dependent_bits == p5_fail.key_dependent_bits == 225
    assert p6_fail.tag_invocations == 0 and p5_fail.verification_invoked is False

    # All predecessor Phase 5 tests still pass.
    start = time.perf_counter()
    predecessor_module = _load_predecessor_tests()
    names = sorted(
        name
        for name in dir(predecessor_module)
        if name.startswith("test_") and callable(getattr(predecessor_module, name))
    )
    assert len(names) >= 16
    for name in names:
        try:
            getattr(predecessor_module, name)()
        except Exception as err:  # noqa: BLE001 -- re-raise with the test name
            raise AssertionError(f"predecessor {name} failed: {type(err).__name__}: {err}") from err
    EVIDENCE["predecessor_seconds"] = time.perf_counter() - start
    EVIDENCE["predecessor_count"] = len(names)


def orig_p6_seed_tag(seen, original_p6_tag):
    return original_p6_tag(seen["p6"][0][0], seen["p6"][0][1])


def orig_p5_seed_tag(seen, original_p5_tag):
    return original_p5_tag(seen["p6"][0][0], seen["p6"][0][1])


def _load_predecessor_tests():
    path = Path(__file__).resolve().parent / "test_nbpolar_protocol.py"
    spec = importlib.util.spec_from_file_location("_p5_predecessor_tests", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a12_tiny_exhaustive_scheduler_mutation_and_frozen_constants():
    assert inc.FROZEN_K == (29, 33, 37, 41, 45)
    assert inc.DEFAULT_N == 256 and inc.EPSILON == 0.05 and inc.ALPHA == 2
    assert inc.SEED_BITS == 2623 and inc.MESSAGE_BITS == 2560 and inc.TAG_BITS == 64
    assert inc.FROZEN_RUN_SEED == 2026091340
    assert inc.TOEPLITZ_MASTER_SEED == 2026091341
    assert inc.FROZEN_BLOCKS == 300 and inc.MIN_EXACT == 285 and inc.WILSON_LB_MIN == 0.90
    parser = inc.build_parser()
    dests = {action.dest for action in parser._actions}
    assert not any(
        name in dests for name in ("k", "n", "sizes", "schedule", "toeplitz", "master_seed")
    )

    # Tiny exhaustive scheduler: acceptance at every level, all-mismatch, decode failures.
    n = 8
    sizes = (2, 3, 4)
    nested = inc.build_nested_schedule(n=n, sizes=sizes)
    rng = np.random.default_rng(TEST_SEED_A)
    x = rng.integers(0, 32, size=n).astype(np.int64)
    logp = noiseless_logp(x)
    for match_level in range(3):
        calls = {"n": 0}
        with patched(inc, "toeplitz_tag", scripted_tag(match_level, calls)):
            result = inc.run_incremental_block(0, x, logp, field=FIELD, n=n, sizes=sizes)
        assert result.outcome == "exact" and result.accepted_level == match_level
        assert result.key_dependent_bits == 5 * sizes[match_level] + 64 * (match_level + 1)
        assert result.public_seed_bits == inc.seed_bits_for(n) * (match_level + 1)
    # seed bits for n=8 are 10*8 + 63 = 143
    assert inc.seed_bits_for(8) == 143
    calls = {"n": 0}
    with patched(inc, "toeplitz_tag", scripted_tag(99, calls)):
        all_mismatch = inc.run_incremental_block(0, x, logp, field=FIELD, n=n, sizes=sizes)
    assert all_mismatch.outcome == "verify_failed"
    assert all_mismatch.key_dependent_bits == 5 * 4 + 64 * 3
    assert all_mismatch.feedback_control_invocations == 2
    assert inc.incremental_record_consistent(all_mismatch, nested)
    for fail_level in range(3):
        state = {"n": 0}
        tag_state = {"n": 0}
        real_decode = inc.sc_decode

        def failing(*args, **kwargs):
            index = state["n"]
            state["n"] += 1
            if index == fail_level:
                raise inc.NumericNonfiniteError("numeric nonfinite failure: tiny")
            return real_decode(*args, **kwargs)

        with patched(inc, "sc_decode", failing), patched(
            inc, "toeplitz_tag", scripted_tag(99, tag_state)
        ):
            failed = inc.run_incremental_block(0, x, logp, field=FIELD, n=n, sizes=sizes)
        assert failed.outcome == "decode_failed"
        assert failed.key_dependent_bits == 5 * sizes[fail_level] + 64 * fail_level
        assert failed.levels_invoked == fail_level + 1
        assert inc.incremental_record_consistent(failed, nested)

    # A 1-block frozen-point paired run uses the frozen schedule and never searches it.
    root = temp_root("paired_incremental_dev_gate")
    run = inc.run_paired_dev_gate(run_seed=TEST_SEED_C, blocks=1, out_root=str(root))
    assert run["plan"]["schedule"]["K"] == list(inc.FROZEN_K)
    assert run["nested"].sizes == inc.FROZEN_K
    assert set(run["aggregate"]["schedule_sizes"]) == set(inc.FROZEN_K)


def test_refusals_existing_root_banned_seeds_and_cli_arguments():
    listed = (
        list(range(2026091200, 2026091214))
        + [2026091314, 2026091315, 2026091316, 2026091317, 2026091318, 2026091319, 2026091320, 2026091330]
    )
    assert inc.BANNED_RUN_SEEDS == frozenset(listed)
    for banned in listed:
        assert_raises_match(ValueError, "banned", inc.validate_run_seed, banned)
    assert inc.validate_run_seed(2026091340) == 2026091340  # frozen seed stays CLI-usable
    assert inc.validate_run_seed(TEST_SEED_A) == TEST_SEED_A

    existing = Path(tempfile.mkdtemp())
    assert_raises_match(
        FileExistsError, "refusing to overwrite",
        inc.run_paired_dev_gate, run_seed=TEST_SEED_A, blocks=1, out_root=str(existing),
    )
    never = existing / "never"
    assert_raises_match(
        ValueError, "banned",
        inc.run_paired_dev_gate, run_seed=2026091319, blocks=1, out_root=str(never),
    )
    assert not never.exists()  # refused before any decoder call or directory creation

    assert_raises_match(SystemExit, "", inc.build_parser().parse_args, [])
    assert_raises_match(
        SystemExit, "", inc.build_parser().parse_args,
        ["--mode", "paired-dev-gate", "--run-seed", "1", "--out", "/tmp/x"],
    )
    assert_raises_match(
        SystemExit, "", inc.build_parser().parse_args,
        ["--mode", "dev-gate", "--run-seed", "1", "--blocks", "1", "--out", "/tmp/x"],
    )
    args = inc.build_parser().parse_args(
        ["--mode", "paired-dev-gate", "--run-seed", "1", "--blocks", "2", "--out", "/tmp/x"]
    )
    assert args.run_seed == 1 and args.blocks == 2 and args.out == "/tmp/x"


def test_five_file_scalar_only_schema():
    root = Path(tempfile.mkdtemp()) / "paired_incremental_dev_gate"
    run = inc.run_paired_dev_gate(run_seed=TEST_SEED_B, blocks=3, out_root=str(root))
    assert sorted(path.name for path in root.iterdir()) == [
        "aggregate_comparison.json",
        "frozen_plan.json",
        "per_block_paired_outcomes.json",
        "report.md",
        "transcript_accounting.json",
    ]

    def check_scalar(node, where):
        if isinstance(node, dict):
            for key, value in node.items():
                assert isinstance(key, str), where
                check_scalar(value, f"{where}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                check_scalar(value, f"{where}[{index}]")
        else:
            assert node is None or isinstance(node, (bool, int, float, str)), f"{where}: {type(node)}"

    raw = {}
    for name in (
        "frozen_plan.json",
        "per_block_paired_outcomes.json",
        "transcript_accounting.json",
        "aggregate_comparison.json",
    ):
        raw[name] = (root / name).read_text()
        check_scalar(json.loads(raw[name]), name)
    for token in ("seed_hex", "u_hat", "x_hat", "known_values", "labels_hat", "decoded"):
        assert all(token not in text for text in raw.values()), f"persisted private token {token!r}"

    plan = json.loads(raw["frozen_plan.json"])
    assert plan["run_seed"] == TEST_SEED_B and plan["planned_blocks"] == 3
    assert plan["schedule"]["K"] == list(inc.FROZEN_K)
    assert plan["schedule"]["strict_nesting"] is True
    assert [len(v) for v in plan["schedule"]["new_coordinates"]] == [29, 4, 4, 4, 4]
    assert plan["static_comparator"]["K"] == 45
    assert plan["toeplitz"]["master_seed"] == inc.TOEPLITZ_MASTER_SEED
    assert plan["toeplitz"]["seed_bits"] == 2623
    assert set(plan["refused_run_seeds"]) == set(inc.BANNED_RUN_SEEDS)
    assert "first scientific sc_decode call" in plan["attempt_consumption_point"]

    per_block = json.loads(raw["per_block_paired_outcomes.json"])
    assert per_block["n_blocks"] == 3
    record = per_block["blocks"][0]
    assert set(record) == {
        "block_index", "paired_match", "metric_wall_s", "static_wall_s",
        "incremental_wall_s", "paired_wall_s", "static", "incremental",
    }
    account = json.loads(raw["transcript_accounting.json"])
    assert account["static"]["mismatch_count"] == 0
    assert account["incremental"]["mismatch_count"] == 0
    static_totals = account["static"]["incremental"]
    static_recount = account["static"]["recount"]
    assert static_totals["key_dependent_bits"] == static_recount["key_dependent_bits"]
    assert static_totals["public_control_bits"] == static_recount["public_control_bits"]
    assert static_totals["public_seed_bits"] == static_recount["public_control_bits"]
    assert static_totals["verification_invocations"] == static_recount["verification_invocations"]
    assert static_totals["feedback_control_bits"] == 0
    aggregate = json.loads(raw["aggregate_comparison.json"])
    assert aggregate["run_seed"] == TEST_SEED_B
    assert aggregate["candidate"] == run["aggregate"]["candidate"]
    assert "not real-data" in aggregate["claim_scope"]
    assert "Wilson" in (root / "report.md").read_text()


def test_resource_abort_paired_bookkeeping():
    root = temp_root("paired_incremental_dev_gate")
    run = inc.run_paired_dev_gate(
        run_seed=TEST_SEED_A, blocks=4, out_root=str(root), total_wall_s=-1.0
    )
    aggregate = run["aggregate"]
    assert aggregate["static"]["outcome_totals"]["resource_abort"] == 4
    assert aggregate["incremental"]["outcome_totals"]["resource_abort"] == 4
    assert aggregate["resource_stop_fired"] is True
    assert aggregate["hard_gates"]["paired_coverage_complete"] is False
    assert aggregate["candidate"] is None
    for record in run["paired_records"]:
        assert record["static"]["key_dependent_bits"] == 0
        assert record["incremental"]["key_dependent_bits"] == 0
        assert record["incremental"]["levels_invoked"] == 0

    root2 = temp_root("paired_incremental_dev_gate")
    run2 = inc.run_paired_dev_gate(
        run_seed=TEST_SEED_B, blocks=3, out_root=str(root2), per_paired_block_soft_cap_s=-1.0
    )
    aggregate2 = run2["aggregate"]
    assert aggregate2["static"]["outcome_totals"]["resource_abort"] == 2
    assert aggregate2["incremental"]["outcome_totals"]["resource_abort"] == 2
    assert aggregate2["resource_stop_fired"] is True
    assert aggregate2["hard_gates"]["resource_stop_preregistered"] is True
    assert aggregate2["hard_gates"]["paired_coverage_complete"] is False
    assert len(run2["paired_records"]) == 3


def test_adapter_round_trip_and_refusals():
    from comparison_bench.src.comparison_bench.methods import nbpolar_incremental as adapter_mod
    from comparison_bench.src.comparison_bench.metrics.leakage import compute_beta_eff_empirical
    from comparison_bench.src.comparison_bench.types import FrameBatch, IRRunConfig

    rng = np.random.default_rng(TEST_SEED_C)
    frames, n = 2, inc.DEFAULT_N
    x = rng.integers(0, 32, size=(frames, n))
    alice = inc.LABEL_SCALE * x
    bob = alice.copy()
    bob[rng.random((frames, n)) < 0.05] = -1
    batch = FrameBatch("synthetic-ds", alice, bob, 1024, n, {})
    cfg = IRRunConfig(
        method="nbpolar_incremental", method_variant="dev", dimension=1024,
        frame_len_symbols=n, max_iter=1, verify_mode="toeplitz64",
    )
    result = adapter_mod.NBPolarIncrementalMethod().run(batch, cfg)
    totals = result.metadata["outcome_totals"]
    assert result.n_frames_total == frames
    assert result.n_frames_attempted == frames - totals["resource_abort"]
    assert sum(totals.values()) == frames
    assert result.n_frames_success == totals["exact"]
    assert result.n_frames_failed_decode == totals["decode_failed"]
    assert result.n_frames_failed_verify == totals["verify_failed"]
    assert result.metadata["verified_union"] == totals["exact"] + totals["undetected"]
    assert result.metadata["key_dependent_bits_total"] == result.leak_EC_actual_bits
    assert result.metadata["schedule_sizes"] == list(inc.FROZEN_K)
    assert (
        result.metadata["public_control_bits_total"]
        == result.metadata["public_seed_bits_total"] + result.metadata["feedback_control_bits"]
    )
    assert result.metadata["verification_invocations"] >= totals["exact"] + totals["undetected"]
    assert result.beta_eff_empirical == compute_beta_eff_empirical(
        result.leak_EC_actual_bits, frames * n * inc.LABEL_BITS, result.raw_ber
    )
    assert result.frame_len_bits == n * inc.LABEL_BITS
    assert 0.0 <= result.raw_ser <= 1.0 and 0.0 <= result.post_ir_ser <= 1.0

    assert_raises_match(
        ValueError, "toeplitz64", adapter_mod.NBPolarIncrementalMethod().run, batch,
        dataclasses.replace(cfg, verify_mode="crc32"),
    )
    bad_batch = FrameBatch("synthetic-ds", alice, bob, 32, n, {})
    assert_raises_match(
        ValueError, "dimension", adapter_mod.NBPolarIncrementalMethod().run, bad_batch, cfg,
    )
    wrong_n = FrameBatch("synthetic-ds", alice[:, :64], bob[:, :64], 1024, 64, {})
    assert_raises_match(
        ValueError, f"N={inc.DEFAULT_N}", adapter_mod.NBPolarIncrementalMethod().run, wrong_n, cfg,
    )


def test_no_forbidden_markers_or_import_time_side_effects():
    import re

    from comparison_bench.src.comparison_bench.methods import nbpolar_incremental as adapter_mod

    core_source = Path(inc.__file__).read_text()
    adapter_source = Path(adapter_mod.__file__).read_text()
    sources = core_source.lower() + adapter_source.lower()
    for token in (
        "outputs_comparison", "model_f", "v72p2d5", "parquet", "ttbin",
        "dev_seed", "eval_seed", "benchmark", "sibling", "artifact", "results/",
    ):
        assert token not in sources, f"forbidden marker {token!r} in Phase 6 sources"
    assert inc.main is not None and adapter_mod.NBPolarIncrementalMethod is not None

    # No global RNG: every numpy random use is an explicit default_rng(...) call.
    for source in (core_source, adapter_source):
        for match in re.finditer(r"np\.random\.([A-Za-z_]+)", source):
            assert match.group(1) == "default_rng", f"global RNG use: {match.group(0)}"

    # Importing both modules in a fresh interpreter performs no file I/O.
    empty = Path(tempfile.mkdtemp())
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import comparison_bench.src.comparison_bench.formal_ir.nbpolar.incremental as i; "
            "import comparison_bench.src.comparison_bench.methods.nbpolar_incremental as a; "
            "assert i.main is not None and a.NBPolarIncrementalMethod is not None",
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
    print(
        f"{len(names) - failed}/{len(names)} passed; predecessor "
        f"{EVIDENCE['predecessor_count']} in {EVIDENCE['predecessor_seconds']}s"
    )
    sys.exit(1 if failed else 0)
