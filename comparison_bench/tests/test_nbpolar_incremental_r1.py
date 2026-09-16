"""Focused Phase 6-R1 decode-reject-advance tests (R1-A01..A12 + refusals).

Synthetic/injected fixtures only. No Model-F artifact, parquet, TTBin, real
frame, DEV/EVAL, sibling read, or output file outside a temporary directory.
The frozen R1 seeds 2026091350/2026091351 are never used as inputs here;
tests use 2026091360..2026091363 and larger offsets only.

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
# R1 tests use their own fresh seeds (>= 2026091360); the frozen R1 seeds
# 2026091350/2026091351 are never used as inputs.
TEST_SEED_A = 2026091360
TEST_SEED_B = 2026091361
TEST_SEED_C = 2026091362
TEST_SEED_D = 2026091363
TEST_SEEDS = (TEST_SEED_A, TEST_SEED_B, TEST_SEED_C, TEST_SEED_D)
EVIDENCE = {
    "predecessor_p5_count": 0,
    "predecessor_p6_count": 0,
    "predecessor_seconds": None,
}


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


def scripted_tag(match_level: int, calls: dict, seeds: list | None = None):
    """Tag seam: mismatch pairs before ``match_level``, honest afterwards.

    Two calls per tagged level (Alice tag, Bob tag); a mismatch returns a
    different constant per parity so the two tag values never agree.
    """

    def tag(bits, seed, tag_bits=64):
        calls["n"] += 1
        if seeds is not None:
            seeds.append(np.array(seed, copy=True))
        level, parity = divmod(calls["n"] - 1, 2)
        if level < match_level:
            return b"\x01" * 8 if parity == 0 else b"\x02" * 8
        return toeplitz_tag(bits, seed, tag_bits)

    return tag


def colliding_tag(bits, seed, tag_bits=64):
    return b"\x2a" * 8


def raising_decode(fail_calls: dict, *, real_decode=None):
    """Decode seam: raise ``fail_calls[index]()`` at the listed call indices."""
    if real_decode is None:
        real_decode = inc.sc_decode
    state = {"n": 0}

    def decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        index = state["n"]
        state["n"] += 1
        if index in fail_calls:
            raise fail_calls[index]()
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    return decode, state


def impossible_error():
    return inc.ImpossibleDisclosedValueError("injected impossible disclosed value")


def temp_root(name: str) -> Path:
    return Path(tempfile.mkdtemp()) / name


def seed_of(block_index: int, level: int) -> np.ndarray:
    return inc.block_toeplitz_seed_bits("incremental", block_index, level)


def test_r1_a01_non_final_impossible_continues_at_every_next_level():
    """Rejection at level r in 0..3 resets to a fresh SC and accepts at r+1."""
    x, _y, _logp = seeded_block(TEST_SEED_A)
    logp = noiseless_logp(x)
    nested = inc.build_nested_schedule()
    u_true = polar_transform(x, field=FIELD)
    for reject_level in range(len(inc.FROZEN_K) - 1):
        tag_calls = {"n": 0}
        seeds: list = []
        positions_seen: list = []
        values_seen: list = []
        real_decode = inc.sc_decode

        def spy_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
            positions_seen.append(np.array(known_positions, dtype=np.int64))
            values_seen.append(np.array(known_values, dtype=np.int64))
            if len(positions_seen) - 1 == reject_level:
                raise impossible_error()
            return real_decode(
                logp_x, field=field, alpha=alpha,
                known_positions=known_positions, known_values=known_values,
            )

        with patched(inc, "sc_decode", spy_decode), patched(
            inc, "toeplitz_tag", scripted_tag(reject_level, tag_calls, seeds)
        ):
            result = inc.run_incremental_r1_block(0, x, logp, field=FIELD)

        assert result.outcome == "exact", f"reject_level={reject_level}"
        assert result.accepted_level == reject_level + 1
        assert result.rejected_levels == (reject_level,)
        assert result.decode_rejected_continue_count == 1
        assert result.levels_invoked == reject_level + 2
        assert result.tag_invocations == reject_level + 1
        assert result.feedback_control_invocations == reject_level + 1
        assert result.nonfinite is False and result.error_type is None
        assert result.key_dependent_bits == 5 * inc.FROZEN_K[reject_level + 1] + 64 * (
            reject_level + 1
        )
        assert inc.incremental_record_consistent(result, nested, advance_on_reject=True)
        # The strict checker refuses an R1 record (rejection pinning).
        assert inc.incremental_record_consistent(result, nested) is False
        # Cumulative disclosure: level j sees D_j with the actual U values,
        # including the rejected level (disclosure happened, only the tag did not).
        assert len(positions_seen) == reject_level + 2
        for level, positions in enumerate(positions_seen):
            assert np.array_equal(positions, nested.sets[level])
            assert np.array_equal(values_seen[level], u_true[positions])
        # One feedback per advance: mismatch levels plus the rejection.
        assert reject_level + 1 == result.levels_invoked - 1
        # No tag used the rejected level's seed; tags sit on the other levels.
        tried = [np.array_equal(seed, seed_of(0, reject_level)) for seed in seeds]
        assert not any(tried), f"tag invoked at rejected level {reject_level}"
        tagged_levels = []
        for level in range(result.levels_invoked):
            if level == reject_level:
                continue
            tagged_levels.append(level)
        assert len(seeds) == 2 * len(tagged_levels)
        for index, level in enumerate(tagged_levels):
            assert np.array_equal(seeds[2 * index], seed_of(0, level))
            assert np.array_equal(seeds[2 * index + 1], seed_of(0, level))


def test_r1_a02_rejected_level_creates_no_candidate_and_no_tag():
    """A rejected level converts no candidate and calls no tag."""
    x, _y, _logp = seeded_block(TEST_SEED_B)
    logp = noiseless_logp(x)
    nested = inc.build_nested_schedule()
    real_decode = inc.sc_decode
    real_labels = inc.labels_from_symbols
    labels_calls = {"n": 0}
    decode_calls: list = []
    seeds: list = []
    tag_calls = {"n": 0}

    def spy_labels(symbols):
        labels_calls["n"] += 1
        return real_labels(symbols)

    def spy_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        decode_calls.append(np.array(known_positions, dtype=np.int64))
        if len(decode_calls) - 1 == 0:
            raise impossible_error()
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(inc, "sc_decode", spy_decode), patched(
        inc, "labels_from_symbols", spy_labels
    ), patched(inc, "toeplitz_tag", scripted_tag(1, tag_calls, seeds)):
        result = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert result.outcome == "exact" and result.accepted_level == 2
    assert result.rejected_levels == (0,)
    assert result.levels_invoked == 3 and result.tag_invocations == 2
    assert result.feedback_control_invocations == 2
    # labels_from_symbols: truth + pre-observation + one candidate per decoded
    # level (levels 1 and 2 only; the rejected level produced no candidate).
    assert labels_calls["n"] == 2 + 2
    assert len(seeds) == 4
    assert not any(np.array_equal(seed, seed_of(0, 0)) for seed in seeds)
    assert np.array_equal(seeds[0], seed_of(0, 1)) and np.array_equal(seeds[2], seed_of(0, 2))
    # No candidate vectors exist on the result for a rejected level.
    assert result.u_hat is not None and result.x_hat is not None  # accepted at level 2
    assert inc.incremental_record_consistent(result, nested, advance_on_reject=True)

    # R1 events place no verification tag at the rejected level.
    events = inc.incremental_block_events(result, nested, advance_on_reject=True)
    tags_by_level = []
    controls_by_level = []
    for event in events:
        if event["event_type"] == "verification_tag":
            tags_by_level.append(event["event_id"])
        if event["event_type"] == "control":
            controls_by_level.append((event["event_id"], event["payload"]["reason"]))
    assert not any("lvl-0-verification" in event_id for event_id in tags_by_level)
    assert ("block-0-lvl-0-control", "decode_rejected_advance_next_level") in controls_by_level
    assert ("block-0-lvl-1-control", "tag_mismatch_advance_next_level") in controls_by_level
    assert inc.recount_transcript(events)["feedback_control_invocations"] == 2


def test_r1_a03_exactly_one_feedback_and_next_increment_per_rejection():
    x, _y, _logp = seeded_block(TEST_SEED_C)
    logp = noiseless_logp(x)
    nested = inc.build_nested_schedule()
    u_true = polar_transform(x, field=FIELD)
    capture = {"positions": [], "values": []}
    real_decode = inc.sc_decode
    tag_calls = {"n": 0}

    def spy_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        capture["positions"].append(np.array(known_positions, dtype=np.int64))
        capture["values"].append(np.array(known_values, dtype=np.int64))
        if len(capture["positions"]) - 1 in (0, 2):
            raise impossible_error()
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(inc, "sc_decode", spy_decode), patched(
        inc, "toeplitz_tag", scripted_tag(2, tag_calls)
    ):
        result = inc.run_incremental_r1_block(0, x, logp, field=FIELD)

    # Rejections at levels 0 and 2; tag mismatch at 1 and 3; accept at 4.
    assert result.outcome == "exact" and result.accepted_level == 4
    assert result.rejected_levels == (0, 2)
    assert result.decode_rejected_continue_count == 2
    assert result.levels_invoked == 5
    assert result.tag_invocations == 3
    assert result.feedback_control_invocations == 4
    assert result.feedback_control_bits == 4
    assert result.key_dependent_bits == 5 * 45 + 64 * 3
    # Each invoked level disclosed its cumulative set exactly once.
    assert len(capture["positions"]) == 5
    for level, positions in enumerate(capture["positions"]):
        assert np.array_equal(positions, nested.sets[level])
        assert np.array_equal(capture["values"][level], u_true[positions])
    assert inc.incremental_record_consistent(result, nested, advance_on_reject=True)
    events = inc.incremental_block_events(result, nested, advance_on_reject=True)
    key = sum(int(e["key_dependent_bits"]) for e in events)
    tags = sum(1 for e in events if e["event_type"] == "verification_tag")
    controls = sum(1 for e in events if e["event_type"] == "control")
    assert key == result.key_dependent_bits
    assert tags == result.tag_invocations == 3
    assert controls == result.feedback_control_invocations == 4
    assert result.public_seed_bits == 3 * inc.SEED_BITS
    assert result.public_control_bits == 3 * inc.SEED_BITS + 4


def test_r1_a04_restart_from_original_metric_no_state():
    x, _y, _logp = seeded_block(TEST_SEED_D)
    logp = noiseless_logp(x)
    logp_snapshot = logp.copy()
    nested = inc.build_nested_schedule()
    real_decode = inc.sc_decode
    seen = {"metrics": [], "positions": []}
    tag_calls = {"n": 0}

    def spy_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        seen["metrics"].append(np.array(logp_x, copy=True))
        seen["positions"].append(np.array(known_positions, dtype=np.int64))
        if len(seen["metrics"]) - 1 == 1:
            raise impossible_error()
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(inc, "sc_decode", spy_decode), patched(
        inc, "toeplitz_tag", scripted_tag(1, tag_calls)
    ):
        result = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert result.outcome == "exact" and result.accepted_level == 2
    assert result.rejected_levels == (1,)
    assert len(seen["metrics"]) == 3
    for level, metric in enumerate(seen["metrics"]):
        assert np.array_equal(metric, logp_snapshot), f"level {level} metric differed"
        assert np.array_equal(seen["positions"][level], nested.sets[level])
    assert np.array_equal(logp, logp_snapshot)  # caller metric untouched

    # Re-running reproduces the identical fresh sequence (no hidden state).
    again = {"metrics": [], "positions": []}

    def spy_again(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        again["metrics"].append(np.array(logp_x, copy=True))
        again["positions"].append(np.array(known_positions, dtype=np.int64))
        if len(again["metrics"]) - 1 == 1:
            raise impossible_error()
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    tag_calls2 = {"n": 0}
    with patched(inc, "sc_decode", spy_again), patched(
        inc, "toeplitz_tag", scripted_tag(1, tag_calls2)
    ):
        result2 = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert result2.accepted_level == result.accepted_level == 2
    assert result2.key_dependent_bits == result.key_dependent_bits
    for first, second in zip(seen["metrics"], again["metrics"]):
        assert np.array_equal(first, second)
    for first, second in zip(seen["positions"], again["positions"]):
        assert np.array_equal(first, second)


def test_r1_a05_final_k45_and_other_exceptions_remain_terminal():
    x, _y, _logp = seeded_block(TEST_SEED_A)
    logp = noiseless_logp(x)
    nested = inc.build_nested_schedule()

    # Persistent impossible disclosed value through K45: no tag anywhere.
    decode_fn, state = raising_decode(
        {level: impossible_error for level in range(5)}
    )
    tag_calls = {"n": 0}
    with patched(inc, "sc_decode", decode_fn), patched(
        inc, "toeplitz_tag", scripted_tag(99, tag_calls)
    ):
        persistent = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert state["n"] == 5
    assert tag_calls["n"] == 0
    assert persistent.outcome == "decode_failed"
    assert persistent.decode_failed_level == 4
    assert persistent.rejected_levels == (0, 1, 2, 3)
    assert persistent.decode_rejected_continue_count == 4
    assert persistent.levels_invoked == 5
    assert persistent.tag_invocations == 0
    assert persistent.feedback_control_invocations == 4
    assert persistent.key_dependent_bits == 5 * 45
    assert persistent.error_type == "ImpossibleDisclosedValueError"
    assert persistent.nonfinite is False
    assert inc.incremental_record_consistent(persistent, nested, advance_on_reject=True)

    # Final-level failure after mismatches is terminal and keeps prior tags.
    tag_calls2 = {"n": 0}
    decode_fn2, state2 = raising_decode({4: impossible_error})
    with patched(inc, "sc_decode", decode_fn2), patched(
        inc, "toeplitz_tag", scripted_tag(99, tag_calls2)
    ):
        final_only = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert state2["n"] == 5 and tag_calls2["n"] == 8
    assert final_only.outcome == "decode_failed" and final_only.decode_failed_level == 4
    assert final_only.rejected_levels == ()
    assert final_only.tag_invocations == 4
    assert final_only.feedback_control_invocations == 4
    assert final_only.key_dependent_bits == 5 * 45 + 64 * 4
    assert inc.incremental_record_consistent(final_only, nested, advance_on_reject=True)

    # Other exceptions fail closed at non-final levels too.
    others = {
        0: lambda: inc.NumericNonfiniteError("numeric nonfinite failure: injected"),
        1: lambda: ValueError("injected other value error"),
        2: lambda: TypeError("injected other type error"),
        3: lambda: RuntimeError("injected other runtime error"),
    }
    for level, factory in others.items():
        decode_fn3, state3 = raising_decode({level: factory})
        tag_calls3 = {"n": 0}
        with patched(inc, "sc_decode", decode_fn3), patched(
            inc, "toeplitz_tag", scripted_tag(99, tag_calls3)
        ):
            failed = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
        assert failed.outcome == "decode_failed", f"level={level}"
        assert failed.decode_failed_level == level
        assert failed.rejected_levels == ()
        assert failed.decode_rejected_continue_count == 0
        assert failed.levels_invoked == level + 1
        assert failed.tag_invocations == level
        assert failed.feedback_control_invocations == level
        assert failed.key_dependent_bits == 5 * inc.FROZEN_K[level] + 64 * level
        assert inc.incremental_record_consistent(failed, nested, advance_on_reject=True)

    # Nonfinite marginals (not an exception) stay terminal.
    real_decode = inc.sc_decode

    def nan_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        real = real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )
        bad = np.array(real.decision_metrics, copy=True)
        bad[0, 0] = np.nan
        return dataclasses.replace(real, decision_metrics=bad)

    with patched(inc, "sc_decode", nan_decode):
        nan_result = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert nan_result.outcome == "decode_failed" and nan_result.nonfinite is True
    assert nan_result.rejected_levels == ()
    assert nan_result.key_dependent_bits == 5 * inc.FROZEN_K[0]

    # Strict-stop mode still terminates at level 0 on the same injected error.
    decode_fn4, state4 = raising_decode({0: impossible_error})
    with patched(inc, "sc_decode", decode_fn4):
        strict = inc.run_incremental_block(0, x, logp, field=FIELD)
    assert state4["n"] == 1
    assert strict.outcome == "decode_failed" and strict.decode_failed_level == 0
    assert strict.decode_rejected_continue_count == 0
    assert inc.incremental_record_consistent(strict, nested)


def test_r1_a06_recount_and_tamper_detection():
    x, _y, _logp = seeded_block(TEST_SEED_B)
    logp = noiseless_logp(x)
    nested = inc.build_nested_schedule()
    real_decode = inc.sc_decode
    tag_calls = {"n": 0}

    def spy_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        if len(seen) == 0:
            seen.append(len(seen))
            raise impossible_error()
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    seen: list = []
    with patched(inc, "sc_decode", spy_decode), patched(
        inc, "toeplitz_tag", scripted_tag(0, tag_calls)
    ):
        result = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert result.outcome == "exact" and result.accepted_level == 1
    assert result.rejected_levels == (0,)
    assert result.levels_invoked == 2 and result.tag_invocations == 1
    assert result.feedback_control_invocations == 1
    assert result.key_dependent_bits == 5 * 33 + 64
    assert inc.incremental_record_consistent(result, nested, advance_on_reject=True)

    events = inc.incremental_block_events(result, nested, advance_on_reject=True)
    # Independent literal walk, not inc.recount_transcript.
    key = sum(int(e["key_dependent_bits"]) for e in events)
    public = sum(int(e["public_control_bits"]) for e in events)
    tags = sum(1 for e in events if e["event_type"] == "verification_tag")
    controls = sum(1 for e in events if e["event_type"] == "control")
    assert key == result.key_dependent_bits == 229
    assert public == result.public_control_bits == inc.SEED_BITS + 1
    assert tags == result.tag_invocations == 1
    assert controls == result.feedback_control_invocations == 1
    recount = inc.recount_transcript(events)
    assert recount["key_dependent_bits"] == key
    assert recount["public_control_bits"] == public
    assert recount["verification_invocations"] == tags
    assert recount["feedback_control_invocations"] == controls

    tampered = [dict(e) for e in events]
    tampered[0]["key_dependent_bits"] += 5
    assert inc.recount_transcript(tampered)["key_dependent_bits"] != key
    tampered2 = [dict(e) for e in events]
    for event in tampered2:
        if event["event_type"] == "control":
            event["event_type"] = "incremental_disclosure"
            break
    assert inc.recount_transcript(tampered2)["feedback_control_invocations"] != controls

    # Record tampering is detected by the mode-aware checker.
    for replacement in (
        {"tag_invocations": result.tag_invocations + 1},
        {"feedback_control_invocations": result.feedback_control_invocations + 1},
        {"levels_invoked": result.levels_invoked + 1},
        {"rejected_levels": ()},
        {"decode_rejected_continue_count": 0},
        {"key_dependent_bits": result.key_dependent_bits + 1},
    ):
        bad = dataclasses.replace(result, **replacement)
        assert (
            inc.incremental_record_consistent(bad, nested, advance_on_reject=True) is False
        ), f"tampered {next(iter(replacement))} was not detected"
    # A rejection at the final level can never be recorded.
    bad_final = dataclasses.replace(
        result, rejected_levels=(4,), decode_rejected_continue_count=1
    )
    assert inc.incremental_record_consistent(bad_final, nested, advance_on_reject=True) is False
    # Scalar-only record: JSON round-trips and carries the frozen facts.
    record = inc._r1_arm_record(result, nested)
    assert json.loads(json.dumps(record)) == record
    assert record["rejected_levels"] == [0]
    assert record["decode_rejected_continue_count"] == 1
    assert record["terminating_level"] == 1 and record["terminating_k"] == 33


def test_r1_a07_buckets_disjoint_exhaustive():
    x, _y, logp = seeded_block(TEST_SEED_C)
    nested = inc.build_nested_schedule()
    real_decode = inc.sc_decode
    outcomes = {}
    outcomes["exact"] = inc.run_incremental_r1_block(0, x, noiseless_logp(x), field=FIELD)
    tag_calls = {"n": 0}
    with patched(inc, "toeplitz_tag", scripted_tag(99, tag_calls)):
        outcomes["verify_failed"] = inc.run_incremental_r1_block(
            0, x, noiseless_logp(x), field=FIELD
        )

    def failing_decode(*args, **kwargs):
        raise inc.NumericNonfiniteError("numeric nonfinite failure: injected")

    with patched(inc, "sc_decode", failing_decode):
        outcomes["decode_failed"] = inc.run_incremental_r1_block(
            0, x, noiseless_logp(x), field=FIELD
        )

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
        outcomes["undetected"] = inc.run_incremental_r1_block(
            0, x, noiseless_logp(x), field=FIELD
        )
    outcomes["resource_abort"] = inc._abort_result(0, inc.R1_RESULT_ARM)
    assert {result.outcome for result in outcomes.values()} == set(inc.OUTCOMES)
    for result in outcomes.values():
        assert inc.incremental_record_consistent(result, nested, advance_on_reject=True)
    assert inc.rescue_comparison(list(outcomes.values()), list(outcomes.values()))["persisted"] == 5

    root = temp_root("three_arm_paired_dev_gate")
    run = inc.run_three_arm_paired_dev_gate(run_seed=TEST_SEED_C, blocks=4, out_root=str(root))
    aggregate = run["aggregate"]
    for arm in ("static", "strict_stop", "r1"):
        assert sum(aggregate[arm]["outcome_totals"].values()) == 4
    assert aggregate["hard_gates"]["outcome_buckets_disjoint_exhaustive_all_arms"] is True
    assert aggregate["hard_gates"]["coverage_complete_all_arms"] is True


def test_r1_a08_three_arms_identical_blocks_and_metric():
    sequence = []
    real_generate = inc.generate_erasure_block
    real_decode = inc.sc_decode

    def generate_spy(rng, q, n, epsilon):
        x, y, logp = real_generate(rng, q, n, epsilon)
        sequence.append(("generate", x.copy(), logp.copy()))
        return x, y, logp

    def decode_spy(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        sequence.append(("decode", np.array(logp_x, copy=True)))
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    root = temp_root("three_arm_paired_dev_gate")
    with patched(inc, "generate_erasure_block", generate_spy), patched(
        inc, "sc_decode", decode_spy
    ):
        run = inc.run_three_arm_paired_dev_gate(
            run_seed=TEST_SEED_A, blocks=3, out_root=str(root)
        )

    groups = []
    current = None
    for item in sequence:
        if item[0] == "generate":
            current = {"x": item[1], "logp": item[2], "decodes": []}
            groups.append(current)
        else:
            assert current is not None
            current["decodes"].append(item[1])
    assert len(groups) == 3  # exactly one generator draw per three-arm block
    rng_reference = np.random.default_rng(TEST_SEED_A)
    for group in groups:
        x_ref, _y, logp_ref = generate_erasure_block(rng_reference, 32, 256, 0.05)
        assert np.array_equal(group["x"], x_ref)
        assert np.array_equal(group["logp"], logp_ref)
        assert len(group["decodes"]) >= 3  # static + strict-stop + R1 at minimum
        for metric in group["decodes"]:
            assert np.array_equal(metric, logp_ref)
    assert all(record["paired_match"] for record in run["paired_records"])
    assert run["aggregate"]["hard_gates"]["three_arm_identical_blocks"] is True

    # A mutating R1 arm must fail the pairing gate.
    original_r1 = inc.run_incremental_r1_block

    def mutating_r1(block_index, x, logp, **kwargs):
        logp[0, 0] = 12345.0
        return original_r1(block_index, x, logp, **kwargs)

    mutant_root = temp_root("three_arm_paired_dev_gate")
    with patched(inc, "run_incremental_r1_block", mutating_r1):
        mutant = inc.run_three_arm_paired_dev_gate(
            run_seed=TEST_SEED_B, blocks=2, out_root=str(mutant_root)
        )
    assert any(record["paired_match"] is False for record in mutant["paired_records"])
    assert mutant["aggregate"]["hard_gates"]["three_arm_identical_blocks"] is False
    assert mutant["aggregate"]["candidate"] is None


def test_r1_a09_rescue_persisted_regressed_identities():
    x, _y, _logp = seeded_block(TEST_SEED_D)
    logp = noiseless_logp(x)
    nested = inc.build_nested_schedule()
    base = inc.run_incremental_r1_block(0, x, logp, field=FIELD)  # exact

    def variants(*outcomes):
        pairs = []
        for index, (strict_outcome, r1_outcome) in enumerate(outcomes):
            strict = dataclasses.replace(
                base,
                block_index=index,
                outcome=strict_outcome,
                exact=strict_outcome == "exact",
                decode_failed_level=0 if strict_outcome == "decode_failed" else -1,
                accepted_level=0 if strict_outcome in ("exact", "undetected", "verify_failed") else -1,
            )
            r1 = dataclasses.replace(
                base,
                block_index=index,
                outcome=r1_outcome,
                exact=r1_outcome == "exact",
                decode_failed_level=0 if r1_outcome == "decode_failed" else -1,
                accepted_level=0 if r1_outcome in ("exact", "undetected", "verify_failed") else -1,
            )
            pairs.append((strict, r1))
        return pairs

    pairs = variants(
        ("decode_failed", "exact"),      # rescued
        ("exact", "exact"),              # persisted
        ("exact", "verify_failed"),      # regressed
        ("verify_failed", "decode_failed"),  # other
        ("verify_failed", "verify_failed"),  # persisted
    )
    result = inc.rescue_comparison([p[0] for p in pairs], [p[1] for p in pairs])
    assert result["rescued"] == 1 and result["rescued_block_indices"] == [0]
    assert result["persisted"] == 2 and result["persisted_block_indices"] == [1, 4]
    assert result["regressed"] == 1 and result["regressed_block_indices"] == [2]
    assert result["other"] == 1 and result["other_block_indices"] == [3]
    assert result["partition_exhaustive"] is True
    assert (
        result["rescued"] + result["persisted"] + result["regressed"] + result["other"] == 5
    )
    assert_raises_match(
        ValueError, "paired", inc.rescue_comparison, [pairs[0][0]], []
    )

    # The three-arm gate reports the same identities.
    root = temp_root("three_arm_paired_dev_gate")
    run = inc.run_three_arm_paired_dev_gate(run_seed=TEST_SEED_D, blocks=5, out_root=str(root))
    reported = run["aggregate"]["rescue_comparison_against_strict"]
    recomputed = inc.rescue_comparison(run["strict_results"], run["r1_results"])
    assert reported == recomputed
    assert reported["partition_exhaustive"] is True
    assert (
        reported["rescued"] + reported["persisted"] + reported["regressed"] + reported["other"]
        == 5
    )


def test_r1_a10_strict_stop_behavior_pinned():
    nested = inc.build_nested_schedule()
    # The strict-stop public signatures are unchanged.
    assert list(inspect.signature(inc.run_incremental_block).parameters) == [
        "block_index", "x", "logp", "field", "n", "sizes", "nested", "tag_fn"
    ]
    assert list(inspect.signature(inc.run_three_arm_paired_dev_gate).parameters) == [
        "run_seed", "blocks", "out_root", "total_wall_s", "per_paired_block_soft_cap_s"
    ]
    for seed in TEST_SEEDS:
        x, _y, logp = seeded_block(seed)
        direct = inc.run_incremental_block(0, x, logp, field=FIELD)
        three = inc.run_three_arm_block(0, x, logp, field=FIELD)
        strict = three["strict_result"]
        assert strict.outcome == direct.outcome
        assert strict.accepted_level == direct.accepted_level
        assert strict.decode_failed_level == direct.decode_failed_level
        assert strict.levels_invoked == direct.levels_invoked
        assert strict.tag_invocations == direct.tag_invocations
        assert strict.feedback_control_invocations == direct.feedback_control_invocations
        assert strict.key_dependent_bits == direct.key_dependent_bits
        assert strict.public_control_bits == direct.public_control_bits
        assert strict.decode_rejected_continue_count == 0
        assert strict.rejected_levels == ()
        assert inc.incremental_record_consistent(strict, nested)

    # A block that never rejects is bit-identical between strict and R1
    # because both incremental arms share the seed namespace.
    x, _y, logp = seeded_block(TEST_SEED_A)
    logp = noiseless_logp(x)
    tag_calls = {"n": 0}
    strict_seeds: list = []
    r1_seeds: list = []
    with patched(inc, "toeplitz_tag", scripted_tag(0, tag_calls, strict_seeds)):
        strict = inc.run_incremental_block(0, x, logp, field=FIELD)
    tag_calls2 = {"n": 0}
    with patched(inc, "toeplitz_tag", scripted_tag(0, tag_calls2, r1_seeds)):
        r1 = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert strict.outcome == r1.outcome == "exact"
    assert strict.key_dependent_bits == r1.key_dependent_bits
    assert len(strict_seeds) == len(r1_seeds) == 2
    for first, second in zip(strict_seeds, r1_seeds):
        assert np.array_equal(first, second)

    # Injected level-0 impossible error: strict terminates, R1 continues.
    decode_fn, state = raising_decode({0: impossible_error})
    with patched(inc, "sc_decode", decode_fn):
        strict_fail = inc.run_incremental_block(0, x, logp, field=FIELD)
    decode_fn2, state2 = raising_decode({0: impossible_error})
    with patched(inc, "sc_decode", decode_fn2):
        r1_continue = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert strict_fail.outcome == "decode_failed" and state["n"] == 1
    assert r1_continue.outcome == "exact" and state2["n"] == 2
    assert strict_fail.decode_rejected_continue_count == 0
    assert r1_continue.decode_rejected_continue_count == 1


def test_r1_a11_truth_leak_nonfinite_undetected_unchanged():
    x, _y, logp = seeded_block(TEST_SEED_B)
    nested = inc.build_nested_schedule()
    real_decode = inc.sc_decode

    def rejecting_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        if not hasattr(rejecting_decode, "done"):
            rejecting_decode.done = True
            raise impossible_error()
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(inc, "sc_decode", rejecting_decode):
        result = inc.run_incremental_r1_block(0, x, logp, field=FIELD)
    assert result.outcome == "exact"
    assert result.truth_leak_violation is False
    assert result.nonfinite is False

    # Injected truth leak flips the gate and blocks the candidate.
    leak_root = temp_root("three_arm_paired_dev_gate")
    with patched(inc, "truth_isolation_sentinel", lambda *a, **k: False):
        leak_run = inc.run_three_arm_paired_dev_gate(
            run_seed=TEST_SEED_A, blocks=2, out_root=str(leak_root)
        )
    assert leak_run["aggregate"]["hard_gates"]["truth_leak_zero"] is False
    assert leak_run["aggregate"]["candidate"] is None
    assert leak_run["aggregate"]["truth_leak_count"]["r1"] == 2

    # Injected nonfinite marginals flip the gate and stay terminal.
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

    nan_root = temp_root("three_arm_paired_dev_gate")
    with patched(inc, "sc_decode", nan_first_decode):
        nan_run = inc.run_three_arm_paired_dev_gate(
            run_seed=TEST_SEED_C, blocks=2, out_root=str(nan_root)
        )
    assert nan_run["aggregate"]["hard_gates"]["nonfinite_zero"] is False
    assert sum(nan_run["aggregate"]["nonfinite_count"].values()) >= 1
    assert nan_run["aggregate"]["candidate"] is None

    # An injected equal tag is undetected, never success, in R1 mode too.
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
        undetected = inc.run_incremental_r1_block(0, x, noiseless_logp(x), field=FIELD)
    assert undetected.outcome == "undetected" and undetected.exact is False
    assert inc.incremental_record_consistent(undetected, nested, advance_on_reject=True)

    # A rejection followed by a terminal failure is never success.
    decode_fn, _state = raising_decode({0: impossible_error, 4: impossible_error})
    tag_calls = {"n": 0}
    with patched(inc, "sc_decode", decode_fn), patched(
        inc, "toeplitz_tag", scripted_tag(99, tag_calls)
    ):
        failed = inc.run_incremental_r1_block(0, x, noiseless_logp(x), field=FIELD)
    assert failed.outcome == "decode_failed" and failed.exact is False
    assert failed.rejected_levels == (0,)


def test_r1_a12_frozen_constants_and_predecessor_suites():
    assert inc.THREE_ARM_MODE == "three-arm-paired-dev-gate"
    assert inc.R1_PROTOCOL_NAME == "nbpolar-decode-reject-advance-protocol"
    assert inc.R1_FROZEN_BLOCKS == 300
    assert inc.R1_RUN_SEED == 2026091350
    assert inc.R1_TOEPLITZ_MASTER_SEED == 2026091351
    assert inc.FROZEN_K == (29, 33, 37, 41, 45)
    assert inc.DEFAULT_N == 256 and inc.EPSILON == 0.05
    assert inc.MIN_EXACT == 285 and inc.WILSON_LB_MIN == 0.90
    assert inc.SEED_BITS == 2623 and inc.MESSAGE_BITS == 2560 and inc.TAG_BITS == 64
    required_refusals = (
        set(range(2026091200, 2026091214))
        | set(range(2026091314, 2026091322))
        | {2026091330, 2026091340, 2026091341}
    )
    assert required_refusals.issubset(inc.R1_BANNED_RUN_SEEDS)
    for banned in sorted(required_refusals):
        assert_raises_match(ValueError, "banned", inc.validate_r1_run_seed, banned)
    assert inc.validate_r1_run_seed(2026091350) == 2026091350
    for seed in TEST_SEEDS:
        assert seed >= 2026091360
        assert inc.validate_r1_run_seed(seed) == seed
    # Phase 6 pinning: the old validator and constant set are unchanged.
    assert inc.validate_run_seed(2026091340) == 2026091340
    assert inc.BANNED_RUN_SEEDS == (
        frozenset(range(2026091200, 2026091214))
        | frozenset(range(2026091314, 2026091321))
        | {2026091330}
    )
    assert inc.R1_RUN_SEED not in TEST_SEEDS and inc.R1_TOEPLITZ_MASTER_SEED not in TEST_SEEDS

    parser = inc.build_parser()
    dests = {action.dest for action in parser._actions}
    assert not any(
        name in dests for name in ("k", "n", "sizes", "schedule", "toeplitz", "master_seed")
    )
    args = parser.parse_args(
        ["--mode", "three-arm-paired-dev-gate", "--run-seed", "1", "--blocks", "2", "--out", "/tmp/x"]
    )
    assert args.mode == "three-arm-paired-dev-gate" and args.blocks == 2
    assert_raises_match(
        SystemExit, "", parser.parse_args,
        ["--mode", "three-arm-paired-dev-gate", "--run-seed", "1", "--out", "/tmp/x"],
    )

    # Predecessor suites: Phase 5 (16) and Phase 6 (17) run unchanged.
    start = time.perf_counter()
    p5_module = _load_test_module("test_nbpolar_protocol.py", "_p5_for_r1")
    p6_module = _load_test_module("test_nbpolar_incremental.py", "_p6_for_r1")
    for label, module in (("p5", p5_module), ("p6", p6_module)):
        names = sorted(
            name
            for name in dir(module)
            if name.startswith("test_") and callable(getattr(module, name))
        )
        for name in names:
            try:
                getattr(module, name)()
            except Exception as err:  # noqa: BLE001 -- re-raise with the test name
                raise AssertionError(f"predecessor {label}:{name} failed: {type(err).__name__}: {err}") from err
        EVIDENCE[f"predecessor_{label}_count"] = len(names)
    EVIDENCE["predecessor_seconds"] = time.perf_counter() - start


def _load_test_module(filename: str, module_name: str):
    path = Path(__file__).resolve().parent / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_refusals_existing_root_banned_seeds_cli():
    listed = sorted(
        set(range(2026091200, 2026091214))
        | set(range(2026091314, 2026091322))
        | {2026091330, 2026091340, 2026091341}
    )
    assert inc.R1_BANNED_RUN_SEEDS == frozenset(listed)
    for banned in (2026091321, 2026091340, 2026091341):
        assert_raises_match(ValueError, "banned", inc.validate_r1_run_seed, banned)

    existing = Path(tempfile.mkdtemp())
    assert_raises_match(
        FileExistsError, "refusing to overwrite",
        inc.run_three_arm_paired_dev_gate,
        run_seed=TEST_SEED_A, blocks=1, out_root=str(existing),
    )
    never = existing / "never"
    assert_raises_match(
        ValueError, "banned",
        inc.run_three_arm_paired_dev_gate,
        run_seed=2026091340, blocks=1, out_root=str(never),
    )
    assert not never.exists()  # refused before any decoder call or directory creation

    assert inc.main(
        [
            "--mode", "three-arm-paired-dev-gate",
            "--run-seed", "2026091341",
            "--blocks", "1",
            "--out", str(never),
        ]
    ) == 2
    assert not never.exists()
    assert inc.main(
        [
            "--mode", "paired-dev-gate",
            "--run-seed", "2026091340",
            "--blocks", "1",
            "--out", str(existing),
        ]
    ) == 2


def test_three_arm_five_file_scalar_only_schema():
    root = Path(tempfile.mkdtemp()) / "three_arm_paired_dev_gate"
    run = inc.run_three_arm_paired_dev_gate(run_seed=TEST_SEED_B, blocks=3, out_root=str(root))
    assert sorted(path.name for path in root.iterdir()) == [
        "aggregate_comparison.json",
        "frozen_plan.json",
        "per_block_three_arm_outcomes.json",
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
        "per_block_three_arm_outcomes.json",
        "transcript_accounting.json",
        "aggregate_comparison.json",
    ):
        raw[name] = (root / name).read_text()
        check_scalar(json.loads(raw[name]), name)
    for token in ("seed_hex", "u_hat", "x_hat", "known_values", "labels_hat", "decoded"):
        assert all(token not in text for text in raw.values()), f"persisted private token {token!r}"

    plan = json.loads(raw["frozen_plan.json"])
    assert plan["mode"] == "three-arm-paired-dev-gate"
    assert plan["run_seed"] == TEST_SEED_B and plan["planned_blocks"] == 3
    assert plan["schedule"]["K"] == list(inc.FROZEN_K)
    assert plan["arms"] == ["static", "strict_stop", "r1"]
    assert plan["toeplitz"]["master_seed"] == inc.R1_TOEPLITZ_MASTER_SEED
    assert plan["seed_derivation"]["master_seed"] == inc.R1_TOEPLITZ_MASTER_SEED
    assert "non_final_levels" in json.dumps(plan["rejection_rule"])
    assert set(plan["refused_run_seeds"]) == set(inc.R1_BANNED_RUN_SEEDS)
    assert "first scientific sc_decode call" in plan["attempt_consumption_point"]

    per_block = json.loads(raw["per_block_three_arm_outcomes.json"])
    assert per_block["n_blocks"] == 3
    record = per_block["blocks"][0]
    assert set(record) == {
        "block_index", "paired_match", "metric_wall_s", "static_wall_s", "strict_wall_s",
        "r1_wall_s", "three_arm_wall_s", "static", "strict_stop", "r1",
    }
    for arm in ("static", "strict_stop", "r1"):
        assert "rejected_levels" in record[arm]
        assert "decode_rejected_continue_count" in record[arm]
        assert "terminating_level" in record[arm] and "terminating_k" in record[arm]
        assert record[arm]["arm"] in ("static", "incremental", inc.R1_RESULT_ARM)
    account = json.loads(raw["transcript_accounting.json"])
    for arm in ("static", "strict_stop", "r1"):
        assert account[arm]["mismatch_count"] == 0
    aggregate = json.loads(raw["aggregate_comparison.json"])
    assert aggregate["run_seed"] == TEST_SEED_B
    assert aggregate["candidate"] == run["aggregate"]["candidate"]
    assert "rescue_comparison_against_strict" in aggregate
    assert "Wilson" in (root / "report.md").read_text()


def test_resource_abort_three_arm_bookkeeping():
    root = temp_root("three_arm_paired_dev_gate")
    run = inc.run_three_arm_paired_dev_gate(
        run_seed=TEST_SEED_A, blocks=4, out_root=str(root), total_wall_s=-1.0
    )
    aggregate = run["aggregate"]
    for arm in ("static", "strict_stop", "r1"):
        assert aggregate[arm]["outcome_totals"]["resource_abort"] == 4
        assert aggregate[arm]["attempted"] == 0
    assert aggregate["resource_stop_fired"] is True
    assert aggregate["hard_gates"]["coverage_complete_all_arms"] is False
    assert aggregate["hard_gates"]["resource_stop_preregistered"] is True
    assert aggregate["candidate"] is None
    for record in run["paired_records"]:
        for arm in ("static", "strict_stop", "r1"):
            assert record[arm]["key_dependent_bits"] == 0
            assert record[arm]["levels_invoked"] == 0
    assert aggregate["rescue_comparison_against_strict"]["persisted"] == 4


def test_adapter_r1_round_trip_and_strict_output_unchanged():
    from comparison_bench.src.comparison_bench.methods import nbpolar_incremental as adapter_mod
    from comparison_bench.src.comparison_bench.metrics.leakage import compute_beta_eff_empirical
    from comparison_bench.src.comparison_bench.types import FrameBatch, IRRunConfig

    assert issubclass(adapter_mod.NBPolarIncrementalR1Method, adapter_mod.NBPolarIncrementalMethod)
    assert adapter_mod.NBPolarIncrementalMethod.METHOD_NAME == "nbpolar_incremental"
    assert list(inspect.signature(adapter_mod.NBPolarIncrementalMethod.run).parameters) == [
        "self", "batch", "cfg"
    ]
    assert list(inspect.signature(adapter_mod.NBPolarIncrementalR1Method.run).parameters) == [
        "self", "batch", "cfg"
    ]

    rng = np.random.default_rng(TEST_SEED_C)
    frames, n = 2, inc.DEFAULT_N
    x = rng.integers(0, 32, size=(frames, n))
    alice = inc.LABEL_SCALE * x
    bob = alice.copy()
    bob[rng.random((frames, n)) < 0.05] = -1
    batch = FrameBatch("synthetic-ds", alice, bob, 1024, n, {})
    cfg = IRRunConfig(
        method="nbpolar_incremental_r1", method_variant="dev", dimension=1024,
        frame_len_symbols=n, max_iter=1, verify_mode="toeplitz64",
    )
    result = adapter_mod.NBPolarIncrementalR1Method().run(batch, cfg)
    totals = result.metadata["outcome_totals"]
    assert result.method == "nbpolar_incremental_r1"
    assert result.n_frames_total == frames
    assert result.n_frames_success == totals["exact"]
    assert sum(totals.values()) == frames
    assert result.metadata["schedule_sizes"] == list(inc.FROZEN_K)
    assert result.metadata["decode_rejected_continue_count"] >= 0
    assert set(result.metadata["rejected_level_histogram"]) == {"0", "1", "2", "3"}
    assert set(result.metadata["terminating_level_histogram"]) == {
        "-1", "0", "1", "2", "3", "4"
    }
    assert result.metadata["key_dependent_bits_total"] == result.leak_EC_actual_bits
    assert result.beta_eff_empirical == compute_beta_eff_empirical(
        result.leak_EC_actual_bits, frames * n * inc.LABEL_BITS, result.raw_ber
    )

    # Strict adapter output has no R1-only metadata key.
    strict_cfg = dataclasses.replace(cfg, method="nbpolar_incremental")
    strict_result = adapter_mod.NBPolarIncrementalMethod().run(batch, strict_cfg)
    assert strict_result.method == "nbpolar_incremental"
    assert "decode_rejected_continue_count" not in strict_result.metadata
    assert strict_result.metadata["backend_status"] == "nbpolar_incremental_protocol_synthetic"

    assert_raises_match(
        ValueError, "toeplitz64", adapter_mod.NBPolarIncrementalR1Method().run, batch,
        dataclasses.replace(cfg, verify_mode="crc32"),
    )


def test_no_forbidden_markers_or_import_time_side_effects():
    import re

    from comparison_bench.src.comparison_bench.methods import nbpolar_incremental as adapter_mod

    core_source = Path(inc.__file__).read_text()
    adapter_source = Path(adapter_mod.__file__).read_text()
    test_source = Path(__file__).read_text()
    sources = core_source.lower() + adapter_source.lower()
    for token in (
        "outputs_comparison", "model_f", "v72p2d5", "parquet", "ttbin",
        "dev_seed", "eval_seed", "benchmark", "sibling", "artifact", "results/",
    ):
        assert token not in sources, f"forbidden marker {token!r} in Phase 6-R1 sources"
    # The real queue root and the frozen seeds never appear as inputs here.
    assert ("." + "workbuddy") not in test_source
    assert ("NBPOLAR" + "-PHASE6-R1") not in test_source
    assert ("default_rng(" + str(2026091350)) not in test_source
    assert ("default_rng(" + str(2026091351)) not in test_source

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
            "assert i.run_incremental_r1_block is not None and "
            "a.NBPolarIncrementalR1Method is not None",
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
        f"P5 {EVIDENCE['predecessor_p5_count']} + P6 {EVIDENCE['predecessor_p6_count']} "
        f"in {EVIDENCE['predecessor_seconds']}s"
    )
    sys.exit(1 if failed else 0)
