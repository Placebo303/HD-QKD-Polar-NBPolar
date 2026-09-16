"""Focused Phase 5 static protocol tests (P5-A01..A11 + refusals).

Synthetic/injected fixtures only. No Model-F artifact, parquet, TTBin, real
frame, DEV/EVAL, sibling read, benchmark, or output file outside a temporary
directory. The reserved scientific seed 2026091317 is never used here; tests
use 2026091319/2026091320/2026091330 only.

Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments, uses plain
asserts, and restores any monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import dataclasses
import inspect
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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

FIELD = make_gf32()
TEST_SEED = 2026091319
TEST_SEED_B = 2026091320
TEST_SEED_C = 2026091330
EVIDENCE = {"a11_seconds": None}


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


def noiseless_logp(x):
    x = np.asarray(x, dtype=np.int64)
    logp = np.full((x.size, 32), -np.inf)
    logp[np.arange(x.size), x] = 0.0
    return logp


def seeded_block(seed, n=256, eps=0.05):
    rng = np.random.default_rng(seed)
    return generate_erasure_block(rng, 32, n, eps)


def literal_gf32_mul(a, b):
    """Textbook carry-less multiply with explicit x^5+x^2+1 reduction."""
    a, b, acc = int(a), int(b), 0
    while b:
        if b & 1:
            acc ^= a
        a <<= 1
        b >>= 1
    while acc.bit_length() > 5:
        acc ^= 37 << (acc.bit_length() - 6)
    return acc & 31


def literal_transform(symbols):
    """Slow dense G_N = F_alpha tensor-power for tiny N (2 or 4)."""
    symbols = [int(v) for v in symbols]
    n = len(symbols)
    if n not in (2, 4):
        raise ValueError("literal_transform is a tiny-case oracle only")
    gen = [[1, 0], [2, 1]]
    while len(gen) < n:
        k = len(gen)
        big = [[0] * (2 * k) for _ in range(2 * k)]
        for i in range(k):
            for j in range(k):
                big[i][j] = gen[i][j]
                big[k + i][j] = literal_gf32_mul(2, gen[i][j])
                big[k + i][k + j] = gen[i][j]
        gen = big
    return [
        _xor_all(literal_gf32_mul(symbols[row], gen[row][col]) for row in range(n))
        for col in range(n)
    ]


def _xor_all(values):
    acc = 0
    for value in values:
        acc ^= int(value)
    return acc


def literal_label_bits(labels):
    bits = []
    for value in labels:
        bits.extend(int(ch) for ch in format(int(value), "010b"))
    return np.array(bits, dtype=np.uint8)


def literal_toeplitz_tag_bits(x_bits, seed_bits, tag_bits=64):
    x_bits = [int(v) for v in x_bits]
    seed_bits = [int(v) for v in seed_bits]
    out = []
    for k in range(tag_bits):
        parity = 0
        for j, bit in enumerate(x_bits):
            if bit:
                parity ^= seed_bits[j - k + tag_bits - 1]
        out.append(parity & 1)
    return np.array(out, dtype=np.uint8)


def test_a01_zero_and_nonzero_disclosed_values_round_trip():
    # Zero-only disclosure: an all-zero source discloses 45 zeros.
    n, k = 16, 4
    x_zero = np.zeros(n, dtype=np.int64)
    res_zero = proto.run_static_block(0, x_zero, noiseless_logp(x_zero), field=FIELD, n=n, k=k)
    assert res_zero.outcome == "exact" and res_zero.exact
    positions = proto.static_disclosure_coordinates(n, k)
    assert int(np.count_nonzero(res_zero.u_true[positions] == 0)) == k
    assert int(np.count_nonzero(res_zero.labels_true)) == 0

    # Mixed zero/non-zero disclosure values are actual U values, never sentinels.
    x = np.zeros(n, dtype=np.int64)
    x[3] = 7
    u_true = polar_transform(x, field=FIELD)
    disclosed_true = u_true[positions]
    assert int(np.count_nonzero(disclosed_true == 0)) > 0
    assert int(np.count_nonzero(disclosed_true != 0)) > 0

    captured = {}
    original_decode = proto.sc_decode

    def spy(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        captured["positions"] = np.array(known_positions, dtype=np.int64)
        captured["values"] = np.array(known_values, dtype=np.int64)
        return original_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(proto, "sc_decode", spy):
        res = proto.run_static_block(0, x, noiseless_logp(x), field=FIELD, n=n, k=k)
    assert res.outcome == "exact" and res.exact
    assert np.array_equal(captured["positions"], positions)
    assert np.array_equal(captured["values"], disclosed_true)
    assert int(np.count_nonzero(captured["values"] == 0)) > 0
    assert int(np.count_nonzero(captured["values"] != 0)) > 0
    assert np.array_equal(res.u_hat, u_true)


def test_a02_static_set_invariant_and_equals_transform():
    positions = proto.static_disclosure_coordinates(256, 45)
    assert positions.shape == (45,)
    assert len(set(positions.tolist())) == 45
    assert int(positions.min()) >= 0 and int(positions.max()) < 256
    reference = np.sort(analytic_order(0.05, 256)[:45])
    assert np.array_equal(positions, reference)
    # Invariant across calls and independent of the block RNG stream.
    assert np.array_equal(proto.static_disclosure_coordinates(256, 45), positions)

    x, _y, logp = seeded_block(TEST_SEED)
    u_true = polar_transform(x, field=FIELD)
    captured = {}
    original_decode = proto.sc_decode

    def spy(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        captured["positions"] = np.array(known_positions, dtype=np.int64)
        captured["values"] = np.array(known_values, dtype=np.int64)
        return original_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(proto, "sc_decode", spy):
        res = proto.run_static_block(0, x, logp, field=FIELD)
    assert res.outcome == "exact" and res.exact
    assert np.array_equal(captured["positions"], positions)
    assert np.array_equal(captured["values"], u_true[positions])


def test_a03_full_reencode_complete_label_vector():
    x, _y, logp = seeded_block(TEST_SEED)
    res = proto.run_static_block(0, x, logp, field=FIELD)
    assert res.outcome == "exact" and res.exact
    assert res.u_hat.shape == (256,)
    assert res.labels_hat.shape == (256,)
    assert int(res.labels_hat.min()) >= 0 and int(res.labels_hat.max()) < 1024
    assert np.array_equal(res.labels_hat, proto.LABEL_SCALE * res.x_hat)
    assert np.array_equal(res.labels_hat, res.labels_true)
    assert np.array_equal(res.labels_true, proto.LABEL_SCALE * x)

    bits = proto.labels_to_bits(res.labels_hat)
    assert bits.shape == (proto.LABEL_BITS * 256,)
    assert np.array_equal(bits, literal_label_bits(res.labels_hat))
    # MSB-first spot check.
    spot = proto.labels_to_bits(np.array([1, 1023], dtype=np.int64)).tolist()
    assert spot == [0, 0, 0, 0, 0, 0, 0, 0, 0, 1] + [1] * 10
    assert_raises_match(ValueError, "0..1023", proto.labels_to_bits, np.array([1024]))
    assert_raises_match(ValueError, "0..31", proto.labels_from_symbols, np.array([32]))


def test_a04_truth_isolation_sentinel_and_spy():
    x, _y, logp = seeded_block(TEST_SEED_B)
    x_before = x.copy()
    logp_before = logp.copy()
    seen = {}
    original_decode = proto.sc_decode

    def spy(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        seen["metric"] = np.array(logp_x, copy=True)
        seen["known"] = np.array(known_values, dtype=np.int64)
        return original_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(proto, "sc_decode", spy):
        res = proto.run_static_block(0, x, logp, field=FIELD)
    assert res.outcome == "exact"
    # The decoder saw the channel metric only and exactly the disclosed subset.
    assert np.array_equal(seen["metric"], logp_before)
    assert seen["known"].shape == (proto.DEFAULT_K,)
    assert res.truth_leak_violation is False
    # The caller's truth/metric buffers are never mutated.
    assert np.array_equal(x, x_before)
    assert np.array_equal(logp, logp_before)

    # The sentinel actually detects a decision that aliases a truth buffer.
    metric = np.zeros((3, 32), dtype=np.float64)
    decision = np.array([1, 2, 3], dtype=np.int64)
    assert proto._truth_isolation_sentinel(metric, [decision], [np.array([4, 5, 6])]) is True
    aliased = np.array([1, 2, 3], dtype=np.int64)
    assert proto._truth_isolation_sentinel(metric, [aliased], [aliased]) is False


def test_a05_decoder_once_verification_at_most_once():
    x, _y, logp = seeded_block(TEST_SEED)
    counts = {"decode": 0, "tag": 0}
    original_decode = proto.sc_decode
    original_tag = proto.toeplitz_tag

    def spy_decode(*args, **kwargs):
        counts["decode"] += 1
        return original_decode(*args, **kwargs)

    def spy_tag(*args, **kwargs):
        counts["tag"] += 1
        return original_tag(*args, **kwargs)

    with patched(proto, "sc_decode", spy_decode), patched(proto, "toeplitz_tag", spy_tag):
        res = proto.run_static_block(0, x, logp, field=FIELD)
    assert res.outcome == "exact"
    assert counts["decode"] == 1
    assert counts["tag"] == 2  # one verification = Alice tag + Bob tag
    assert res.verification_invoked is True
    assert bool(np.array_equal(res.u_hat, polar_transform(x, field=FIELD)))

    counts.update(decode=0, tag=0)

    def failing_decode(*args, **kwargs):
        counts["decode"] += 1
        raise proto.NumericNonfiniteError("numeric nonfinite failure: injected")

    with patched(proto, "sc_decode", failing_decode), patched(proto, "toeplitz_tag", spy_tag):
        failed = proto.run_static_block(0, x, logp, field=FIELD)
    assert failed.outcome == "decode_failed"
    assert failed.verification_invoked is False
    assert counts["decode"] == 1 and counts["tag"] == 0


def test_a06_tag_never_selects_retries_or_mutates_decoder():
    x, _y, logp = seeded_block(TEST_SEED_B)
    reference = proto.run_static_block(0, x, logp, field=FIELD)
    assert reference.outcome == "exact"
    counts = {"decode": 0}
    original_decode = proto.sc_decode
    tag_state = {"n": 0}

    def spy_decode(*args, **kwargs):
        counts["decode"] += 1
        return original_decode(*args, **kwargs)

    def alternating_tag(bits, seed, tag_bits=64):
        tag_state["n"] += 1
        return b"\x00" * 8 if tag_state["n"] == 1 else b"\xff" * 8

    with patched(proto, "sc_decode", spy_decode), patched(proto, "toeplitz_tag", alternating_tag):
        res = proto.run_static_block(0, x, logp, field=FIELD)
    assert res.outcome == "verify_failed"
    assert res.exact is True  # decoding was exact; the tag rejected only the candidate
    assert counts["decode"] == 1  # no retry, no path reselection
    assert np.array_equal(res.u_hat, reference.u_hat)
    assert np.array_equal(res.labels_hat, reference.labels_hat)


def test_a07_forced_collision_is_undetected_never_success():
    x, _y, logp = seeded_block(TEST_SEED_C)
    counts = {"decode": 0}
    original_decode = proto.sc_decode

    def wrong_decode(*args, **kwargs):
        counts["decode"] += 1
        real = original_decode(*args, **kwargs)
        wrong_u = real.u_hat.copy()
        wrong_u[0] ^= 1
        return dataclasses.replace(
            real, u_hat=wrong_u, x_hat=polar_transform(wrong_u, field=FIELD)
        )

    def colliding_tag(bits, seed, tag_bits=64):
        return b"\x2a" * 8

    with patched(proto, "sc_decode", wrong_decode), patched(proto, "toeplitz_tag", colliding_tag):
        res = proto.run_static_block(0, x, logp, field=FIELD)
    assert res.outcome == "undetected"
    assert res.exact is False
    assert res.verification_invoked is True
    assert counts["decode"] == 1

    run = proto.execute_blocks(run_seed=TEST_SEED_C, blocks=2)
    assert run.summary["outcome_totals"]["undetected"] == 0

    with patched(proto, "sc_decode", wrong_decode), patched(proto, "toeplitz_tag", colliding_tag):
        run_bad = proto.execute_blocks(run_seed=TEST_SEED_C, blocks=2)
    totals = run_bad.summary["outcome_totals"]
    assert totals["undetected"] == 2 and totals["exact"] == 0
    assert run_bad.summary["verified"] == 2  # listed union, still not success
    assert run_bad.summary["hard_gates"]["undetected_zero"] is False
    assert run_bad.summary["candidate"] is None


def test_a08_disjoint_exhaustive_accounting():
    state = {"n": 0}
    counts = {"decode": 0, "tag": 0}
    original_decode = proto.sc_decode
    original_tag = proto.toeplitz_tag

    def scripted_decode(*args, **kwargs):
        index = state["n"]
        state["n"] += 1
        counts["decode"] += 1
        if index == 1:
            raise proto.NumericNonfiniteError("numeric nonfinite failure: scripted")
        real = original_decode(*args, **kwargs)
        if index == 2:
            wrong_u = real.u_hat.copy()
            wrong_u[0] ^= 1
            return dataclasses.replace(
                real, u_hat=wrong_u, x_hat=polar_transform(wrong_u, field=FIELD)
            )
        return real

    def spy_tag(*args, **kwargs):
        counts["tag"] += 1
        # Block 0 (calls 1-2) verifies honestly; block 2 (calls 3-4) is a
        # forced collision so the scripted non-exact decode lands in
        # ``undetected`` rather than ``verify_failed``.
        if counts["tag"] > 2:
            return b"\x11" * 8
        return original_tag(*args, **kwargs)

    with patched(proto, "sc_decode", scripted_decode), patched(proto, "toeplitz_tag", spy_tag):
        run = proto.execute_blocks(run_seed=TEST_SEED_B, blocks=3)

    totals = run.summary["outcome_totals"]
    assert totals == {
        "exact": 1, "undetected": 1, "verify_failed": 0, "decode_failed": 1, "resource_abort": 0
    }
    assert sum(totals.values()) == run.summary["planned_blocks"] == 3
    assert run.summary["attempted"] == 3 and run.summary["coverage"] == 1.0
    assert run.summary["verified"] == 2
    assert run.summary["verification_invocations"] == 2
    assert counts["decode"] == 3 and counts["tag"] == 4
    assert run.summary["hard_gates"]["outcome_accounting_disjoint_exhaustive"] is True
    assert run.summary["hard_gates"]["per_block_disclosure_consistent"] is True
    key_dependent = run.summary["key_dependent_bits_total"]
    assert key_dependent == 289 * 2 + 225  # two verifications + one decode failure


def test_a09_transcript_recount_and_tamper():
    run = proto.execute_blocks(run_seed=TEST_SEED, blocks=3)
    assert run.mismatch_count == 0
    assert run.recount == run.incremental
    assert run.incremental["key_dependent_bits"] == 3 * 289
    assert run.incremental["public_control_bits"] == 3 * proto.SEED_BITS
    assert run.incremental["verification_invocations"] == 3
    assert run.summary["transcript"]["mismatch_count"] == 0
    assert len(run.summary["transcript"]["transcript_sha256"]) == 64

    by_block = {}
    for event in run.events:
        by_block.setdefault(event["block_id"], []).append(event)
    for events in by_block.values():
        types = sorted(e["event_type"] for e in events)
        assert types == ["static_disclosure", "verification_tag"]
        assert events[0]["key_dependent_bits"] == 225
        assert events[1]["key_dependent_bits"] == 64
        assert events[1]["public_control_bits"] == proto.SEED_BITS

    tampered = [dict(event) for event in run.events]
    tampered[0]["key_dependent_bits"] += 1
    assert proto.recount_transcript(tampered)["key_dependent_bits"] != run.incremental["key_dependent_bits"]
    tampered2 = [dict(event) for event in run.events]
    tampered2[1]["event_type"] = "static_disclosure"
    assert proto.recount_transcript(tampered2)["verification_invocations"] != run.incremental[
        "verification_invocations"
    ]


def test_a10_signatures_and_adapter_round_trip():
    from comparison_bench.src.comparison_bench.methods import nbpolar_static as adapter_mod
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
    assert issubclass(adapter_mod.NBPolarStaticMethod, IRMethod)
    assert list(inspect.signature(adapter_mod.NBPolarStaticMethod.run).parameters) == [
        "self", "batch", "cfg"
    ]

    rng = np.random.default_rng(TEST_SEED_C)
    frames, n = 2, proto.DEFAULT_N
    x = rng.integers(0, 32, size=(frames, n))
    alice = proto.LABEL_SCALE * x
    bob = alice.copy()
    bob[rng.random((frames, n)) < 0.05] = -1
    batch = FrameBatch("synthetic-ds", alice, bob, 1024, n, {})
    cfg = IRRunConfig(
        method="nbpolar_static", method_variant="dev", dimension=1024,
        frame_len_symbols=n, max_iter=1, verify_mode="toeplitz64",
    )
    result = adapter_mod.NBPolarStaticMethod().run(batch, cfg)
    totals = result.metadata["outcome_totals"]
    assert result.n_frames_total == frames
    assert result.n_frames_attempted == frames - totals["resource_abort"]
    assert result.n_frames_success == totals["exact"]
    assert result.n_frames_failed_decode == totals["decode_failed"]
    assert result.n_frames_failed_verify == totals["verify_failed"]
    assert result.metadata["verified_union"] == totals["exact"] + totals["undetected"]
    expected_leak = (
        289 * (totals["exact"] + totals["undetected"] + totals["verify_failed"])
        + 225 * totals["decode_failed"]
    )
    assert result.leak_EC_actual_bits == expected_leak
    assert result.leak_EC_per_input_bit == expected_leak / (frames * n * proto.LABEL_BITS)
    from comparison_bench.src.comparison_bench.metrics.leakage import (
        compute_beta_eff_empirical,
    )

    assert result.beta_eff_empirical == compute_beta_eff_empirical(
        result.leak_EC_actual_bits, frames * n * proto.LABEL_BITS, result.raw_ber
    )
    assert 0.0 <= result.raw_ser <= 1.0 and 0.0 <= result.post_ir_ser <= 1.0
    assert result.frame_len_bits == n * proto.LABEL_BITS

    assert_raises_match(
        ValueError, "toeplitz64",
        adapter_mod.NBPolarStaticMethod().run, batch,
        dataclasses.replace(cfg, verify_mode="crc32"),
    )
    bad_batch = FrameBatch("synthetic-ds", alice, bob, 32, n, {})
    assert_raises_match(
        ValueError, "dimension",
        adapter_mod.NBPolarStaticMethod().run, bad_batch, cfg,
    )
    wrong_n = FrameBatch("synthetic-ds", alice[:, :64], bob[:, :64], 1024, 64, {})
    assert_raises_match(
        ValueError, f"N={proto.DEFAULT_N}",
        adapter_mod.NBPolarStaticMethod().run, wrong_n, cfg,
    )


def test_a11_exhaustive_tiny_independent_oracle():
    start = time.perf_counter()
    for a in range(32):
        for b in range(32):
            assert literal_gf32_mul(a, b) == FIELD.mul(a, b)

    n_small = 2
    for first in range(32):
        for second in range(32):
            x = np.array([first, second], dtype=np.int64)
            u = polar_transform(x, field=FIELD)
            assert u.tolist() == literal_transform(x)
            res = proto.run_static_block(
                0, x, noiseless_logp(x), field=FIELD, n=n_small, k=n_small
            )
            assert res.outcome == "exact" and res.exact
            assert np.array_equal(res.u_true, literal_transform(x))
            assert np.array_equal(res.labels_true, proto.LABEL_SCALE * x)
            assert np.array_equal(
                proto.labels_to_bits(res.labels_hat), literal_label_bits(res.labels_hat)
            )

    rng = np.random.default_rng(TEST_SEED)
    for _ in range(64):
        x = rng.integers(0, 32, size=4)
        assert polar_transform(x, field=FIELD).tolist() == literal_transform(x)
    x4 = rng.integers(0, 32, size=4)
    res4 = proto.run_static_block(1, x4, noiseless_logp(x4), field=FIELD, n=4, k=4)
    assert res4.outcome == "exact" and res4.exact

    bits = rng.integers(0, 2, size=40).astype(np.uint8)
    seed = rng.integers(0, 2, size=40 + proto.TAG_BITS - 1).astype(np.uint8)
    from comparison_bench.src.comparison_bench.formal_ir.shared import toeplitz_tag

    packed = toeplitz_tag(bits, seed, proto.TAG_BITS)
    assert np.array_equal(
        np.unpackbits(np.frombuffer(packed, dtype=np.uint8), bitorder="big"),
        literal_toeplitz_tag_bits(bits, seed, proto.TAG_BITS),
    )
    assert np.array_equal(
        proto.block_toeplitz_seed_bits(7), proto.block_toeplitz_seed_bits(7)
    )
    assert not np.array_equal(
        proto.block_toeplitz_seed_bits(7), proto.block_toeplitz_seed_bits(8)
    )
    EVIDENCE["a11_seconds"] = time.perf_counter() - start


def test_refusals_existing_root_and_banned_seeds():
    for banned in (2026091200, 2026091207, 2026091213, 2026091314, 2026091315, 2026091316):
        assert_raises_match(ValueError, "banned", proto.validate_run_seed, banned)
    assert proto.validate_run_seed(2026091317) == 2026091317  # frozen seed is CLI-usable
    assert proto.validate_run_seed(TEST_SEED) == TEST_SEED

    existing = Path(tempfile.mkdtemp())
    assert_raises_match(
        FileExistsError, "refusing to overwrite",
        proto.run_dev_gate, run_seed=TEST_SEED, blocks=1, out_root=str(existing),
    )
    assert_raises_match(ValueError, "banned", proto.run_dev_gate,
                        run_seed=2026091316, blocks=1,
                        out_root=str(existing / "never"))
    assert_raises_match(SystemExit, "", proto.build_parser().parse_args, [])
    assert_raises_match(
        SystemExit, "", proto.build_parser().parse_args,
        ["--mode", "dev-gate", "--run-seed", "1", "--out", "/tmp/x"],
    )


def test_dev_gate_five_file_schema():
    root = Path(tempfile.mkdtemp()) / "static_protocol_dev_gate"
    run = proto.run_dev_gate(run_seed=TEST_SEED_B, blocks=5, out_root=str(root))
    assert sorted(p.name for p in root.iterdir()) == [
        "aggregate_summary.json", "frozen_plan.json", "per_block_outcomes.json",
        "report.md", "transcript_accounting.json",
    ]
    import json

    plan = json.loads((root / "frozen_plan.json").read_text())
    assert plan["disclosure_coordinates"] == proto.static_disclosure_coordinates().tolist()
    assert plan["run_seed"] == TEST_SEED_B and plan["planned_blocks"] == 5
    assert plan["toeplitz"]["seed_bits"] == proto.SEED_BITS
    assert plan["label_domain"]["message_bits"] == 2560
    per_block = json.loads((root / "per_block_outcomes.json").read_text())
    allowed = {
        "block_index", "outcome", "exact", "verification_invoked", "key_dependent_bits",
        "public_control_bits", "nonfinite", "truth_leak_violation", "error_type",
        "metric_wall_s", "decode_wall_s",
    }
    assert per_block["n_blocks"] == 5
    assert all(set(record) == allowed for record in per_block["blocks"])
    account = json.loads((root / "transcript_accounting.json").read_text())
    assert account["mismatch_count"] == 0
    assert account["incremental"] == account["recount"]
    summary = json.loads((root / "aggregate_summary.json").read_text())
    assert sum(summary["outcome_totals"].values()) == 5
    assert summary["candidate"] == run.summary["candidate"]
    assert "not real-data" in summary["claim_scope"]
    assert "Wilson" in (root / "report.md").read_text()


def test_resource_abort_bookkeeping():
    run = proto.execute_blocks(run_seed=TEST_SEED, blocks=4, total_wall_s=-1.0)
    assert run.summary["outcome_totals"]["resource_abort"] == 4
    assert run.summary["attempted"] == 0 and run.summary["coverage"] == 0.0
    assert all(record["key_dependent_bits"] == 0 for record in run.records)
    assert run.summary["hard_gates"]["coverage_complete"] is False
    assert run.summary["hard_gates"]["per_block_disclosure_consistent"] is True
    assert run.summary["candidate"] is None

    counts = {"decode": 0}
    original_decode = proto.sc_decode

    def counting_decode(*args, **kwargs):
        counts["decode"] += 1
        return original_decode(*args, **kwargs)

    with patched(proto, "sc_decode", counting_decode):
        run2 = proto.execute_blocks(run_seed=TEST_SEED, blocks=3, per_block_soft_cap_s=-1.0)
    assert counts["decode"] == 1
    assert run2.summary["outcome_totals"]["resource_abort"] == 2
    assert run2.summary["resource_stop_fired"] is True
    assert run2.summary["hard_gates"]["per_block_disclosure_consistent"] is True
    assert sum(run2.summary["outcome_totals"].values()) == 3


def test_wilson_known_values():
    assert abs(proto.wilson_lower_bound(290, 300) - 0.945020093768338) < 1e-12
    assert abs(proto.wilson_lower_bound(300, 300) - 0.9910621278248719) < 1e-12
    assert abs(proto.wilson_lower_bound(270, 300) - 0.8678383125985952) < 1e-12
    assert abs(proto.wilson_lower_bound(45, 50) - 0.8084624858484291) < 1e-12
    assert proto.wilson_lower_bound(0, 300) == 0.0
    assert proto.wilson_lower_bound(0, 0) == 0.0
    assert_raises_match(ValueError, "exceed", proto.wilson_lower_bound, 301, 300)


def test_no_forbidden_markers_or_import_time_side_effects():
    from comparison_bench.src.comparison_bench.methods import nbpolar_static as adapter_mod

    sources = Path(proto.__file__).read_text() + Path(adapter_mod.__file__).read_text()
    for token in (
        "outputs_comparison", "model_f", "v72p2d5", "parquet", "ttbin",
        "results/", "HD-QKD_Polar_Comparison/", "DEV_SEED", "EVAL_SEED",
    ):
        assert token not in sources, f"forbidden marker {token!r} in protocol sources"
    assert proto.main is not None


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
    print(f"{len(names) - failed}/{len(names)} passed; a11 {EVIDENCE['a11_seconds']}")
    sys.exit(1 if failed else 0)
