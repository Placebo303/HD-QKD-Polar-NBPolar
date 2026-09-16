"""Focused Phase 4-P4 two-layer operational SC tests (P4-A01..A09, A11).

Synthetic/injected fixtures only.  No Model-F stored file, no columnar or
TT-binary reader, no real frame, no DEV/EVAL stream, no sibling read, no
method adapter and no output outside a temporary directory.  Focused tests use
their own fresh seeds >= 2026091364 and never the frozen gate seeds
2026091360/2026091361.

Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments, uses plain
asserts and restores any monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import importlib.util
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
    empirical_oracle as empirical_oracle_mod,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import oracle as oracle_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    combine_symbol,
    derive_p1,
    derive_p2,
    gather_p2_metrics,
    build_p1_metrics,
    probs_to_symbol_metric,
    split_symbol,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc import (
    ImpossibleDisclosedValueError,
    NumericNonfiniteError,
    sc_decode,
)
from comparison_bench.src.comparison_bench.formal_ir.shared import toeplitz_tag

FIELD = make_gf32()
REPO_ROOT = Path(__file__).resolve().parents[2]
# Fresh test-local seeds (>= 2026091364); the frozen gate seeds are only read
# from the module constants and are never used as inputs here.
TEST_SEED_A = 2026091364
TEST_SEED_B = 2026091365
TEST_SEED_C = 2026091366
TEST_SEED_D = 2026091367
TEST_SEED_E = 2026091368
TEST_SEED_F = 2026091369
TEST_SEEDS = (TEST_SEED_A, TEST_SEED_B, TEST_SEED_C, TEST_SEED_D, TEST_SEED_E, TEST_SEED_F)
PROB_TOL = 1e-12
LOG_TOL = 1e-9

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


def fixture(n, seed, k1, k2, *, epsilon1=0.05, epsilon2=0.20):
    """Injected joint table + metric tables + frozen sets + one sampled block."""
    table = tl.build_injected_joint_table(epsilon1=epsilon1, epsilon2=epsilon2)
    p1, p2 = tl.layer_metric_tables(table)
    d1 = tl.disclosure_coordinates(n=n, k=k1, epsilon=epsilon1)
    d2 = tl.disclosure_coordinates(n=n, k=k2, epsilon=epsilon2)
    sample = tl.sample_two_layer_block(
        np.random.default_rng(seed), n=n, epsilon1=epsilon1, epsilon2=epsilon2
    )
    return table, p1, p2, d1, d2, sample


def run_block(sample, p1, p2, d1, d2, n, k1, k2, *, master=TEST_SEED_F, **kwargs):
    return tl.run_two_layer_block(
        0,
        sample.high,
        sample.low,
        sample.bob,
        field=FIELD,
        p1_table=p1,
        p2_table=p2,
        d1=d1,
        d2=d2,
        n=n,
        k1=k1,
        k2=k2,
        toeplitz_master=master,
        **kwargs,
    )


def oracle_gather_p2(bob, u1, p2_table):
    """Literal test-local gather (no shared helper)."""
    bob = np.asarray(bob).ravel()
    u1 = np.asarray(u1).ravel()
    out = np.empty((bob.size, 32), dtype=np.float64)
    for j in range(bob.size):
        for a in range(32):
            out[j, a] = p2_table[int(u1[j]), int(bob[j]), a]
    return out


def oracle_labels_to_bits(labels):
    """Literal MSB-first 10-bit expansion (no shared helper)."""
    bits = []
    for symbol in np.asarray(labels).ravel().tolist():
        for shift in range(9, -1, -1):
            bits.append((int(symbol) >> shift) & 1)
    return np.array(bits, dtype=np.uint8)


def oracle_seed_bits(master, arm, block_index, bit_length):
    """Literal independent Toeplitz seed derivation (no shared helper)."""
    prefix = f"nbpolar-p4-toeplitz-seed:{int(master)}:{arm}:{int(block_index)}"
    buf = b""
    counter = 0
    while len(buf) * 8 < bit_length:
        buf += hashlib.sha256(f"{prefix}:{counter}".encode("ascii")).digest()
        counter += 1
    return np.unpackbits(np.frombuffer(buf, dtype=np.uint8), bitorder="big")[:bit_length].astype(np.uint8)


def oracle_tag_for(arm, block_index, master, n, labels):
    seed = oracle_seed_bits(master, arm, block_index, tl.seed_bits_for(n))
    return toeplitz_tag(oracle_labels_to_bits(labels), seed, tl.TAG_BITS)


def injected_dependent_table():
    """Hand-injected layer-dependent table (literal construction)."""
    table = np.full((1024, 1024), 1.0 / 1024.0, dtype=np.float64)
    table[:, 0] = 0.0
    table[0, 0] = 0.2
    table[1, 0] = 0.3
    table[32, 0] = 0.5
    return table


def high_zero_support_table():
    """Columns carry mass only on A_high == 0: L1 metric has exact-zero support."""
    table = np.zeros((1024, 1024), dtype=np.float64)
    table[:32, :] = 1.0 / 32.0
    return table


def low_zero_support_table():
    """Every column is concentrated on A = 0: L2 metric has exact-zero support."""
    table = np.zeros((1024, 1024), dtype=np.float64)
    table[0, :] = 1.0
    return table


def test_p4_a01_p1_bob_only_and_source_domain_candidate():
    n, k1, k2 = 4, 4, 2
    table, p1, p2, d1, d2, sample = fixture(n, TEST_SEED_A, k1, k2)
    assert d1.tolist() == [0, 1, 2, 3]  # full disclosure of the permutation
    res = run_block(sample, p1, p2, d1, d2, n, k1, k2)
    # Full disclosure forces U1 exactly; x_hat is the source-domain high layer.
    assert res.operational.l1_executed and not res.operational.l1_decode_failed
    assert np.array_equal(res.operational.high_hat, sample.high)
    # P1 metric is Bob-only: the same Bob with different truth gives the same table.
    other = dataclasses.replace(
        sample, high=(sample.high + 1) % 32, low=(sample.low + 2) % 32
    )
    res_other = run_block(other, p1, p2, d1, d2, n, k1, k2)
    assert np.array_equal(res.p1_probs, res_other.p1_probs)
    assert np.array_equal(res.p1_probs, build_p1_metrics(sample.bob[None, :], p1)[0])
    # Literal formula oracle for the P1 gather (no shared helper).
    literal_p1 = np.empty((n, 32), dtype=np.float64)
    for j in range(n):
        for a in range(32):
            literal_p1[j, a] = p1[a, int(sample.bob[j])]
    assert np.array_equal(res.p1_probs, literal_p1)
    assert res.operational.l1_provenance == "PRIOR_ONLY"


def test_p4_a02_operational_p2_bob_plus_candidate_and_literal_gather():
    n, k1, k2 = 4, 1, 2
    table, p1, p2, d1, d2, sample = fixture(n, TEST_SEED_A, k1, k2)
    res = run_block(sample, p1, p2, d1, d2, n, k1, k2)
    assert res.operational.l2_invoked
    # Literal formula oracle for the P2 gather on Bob + the candidate.
    ref = oracle_gather_p2(sample.bob, res.operational.high_hat, p2)
    assert np.array_equal(res.p2_hat_probs, ref)
    assert np.array_equal(
        res.p2_hat_probs,
        gather_p2_metrics(sample.bob[None, :], res.operational.high_hat[None, :], p2)[0],
    )
    assert res.operational.l2_provenance == "CANDIDATE_CONDITIONED"
    # A forced different candidate changes the gathered rows on a dependent table.
    table_dep = injected_dependent_table()
    p1_dep, p2_dep = derive_p1(table_dep), derive_p2(table_dep)
    bob = np.array([0, 0], dtype=np.int64)
    high = np.array([1, 0], dtype=np.int64)
    low = np.array([0, 0], dtype=np.int64)
    dep = tl.run_two_layer_block(
        0, high, low, bob, field=FIELD, p1_table=p1_dep, p2_table=p2_dep,
        d1=np.array([0]), d2=np.array([0]), n=2, k1=1, k2=1,
        toeplitz_master=TEST_SEED_F, l1_candidate_override=np.array([0, 0]),
    )
    assert np.array_equal(dep.p2_hat_probs, oracle_gather_p2(bob, np.array([0, 0]), p2_dep))
    assert not np.array_equal(dep.p2_hat_probs, dep.p2_true_probs)
    # Axis/packing round trip is exact over the whole alphabet.
    for high_symbol in range(32):
        for low_symbol in range(32):
            symbol = combine_symbol(low_symbol, high_symbol)
            assert symbol == low_symbol + 32 * high_symbol
            assert split_symbol(symbol) == (low_symbol, high_symbol)


def test_p4_a03_oracle_arm_isolated_true_l1():
    table_dep = injected_dependent_table()
    p1, p2 = derive_p1(table_dep), derive_p2(table_dep)
    bob = np.array([0, 0], dtype=np.int64)
    high = np.array([1, 0], dtype=np.int64)
    low = np.array([0, 0], dtype=np.int64)
    d1, d2 = np.array([0]), np.array([0])
    base = tl.run_two_layer_block(
        0, high, low, bob, field=FIELD, p1_table=p1, p2_table=p2, d1=d1, d2=d2,
        n=2, k1=1, k2=1, toeplitz_master=TEST_SEED_F,
    )
    forced = tl.run_two_layer_block(
        0, high, low, bob, field=FIELD, p1_table=p1, p2_table=p2, d1=d1, d2=d2,
        n=2, k1=1, k2=1, toeplitz_master=TEST_SEED_F,
        l1_candidate_override=np.array([0, 0]),
    )
    # Oracle metric is the true-L1 gather and never the candidate gather.
    assert np.array_equal(forced.p2_true_probs, oracle_gather_p2(bob, high, p2))
    assert forced.oracle.l2_provenance == "ORACLE_CONDITIONED"
    assert base.operational.l2_provenance == "CANDIDATE_CONDITIONED"
    assert np.array_equal(base.oracle.label_hat, base.low_hat_oracle + 32 * high)
    assert not np.array_equal(forced.p2_hat_probs, forced.p2_true_probs)
    # Changing only the operational candidate leaves the oracle arm bitwise fixed.
    assert np.array_equal(base.p2_true_probs, forced.p2_true_probs)
    assert np.array_equal(base.oracle.label_hat, forced.oracle.label_hat)


def test_p4_a04_fresh_sc_calls_no_state_transfer():
    n, k1, k2 = 4, 1, 2
    table, p1, p2, d1, d2, sample = fixture(n, TEST_SEED_B, k1, k2)
    calls = []
    real_decode = tl.sc_decode

    def spy_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        calls.append(
            {
                "logp": np.array(logp_x, copy=True),
                "positions": None if known_positions is None else np.array(known_positions, copy=True),
                "values": None if known_values is None else np.array(known_values, copy=True),
            }
        )
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(tl, "sc_decode", spy_decode):
        res = run_block(sample, p1, p2, d1, d2, n, k1, k2)
    # One L1 call, one fresh operational L2 call and one fresh oracle L2 call.
    assert len(calls) == 3
    assert all(not np.shares_memory(calls[i]["logp"], calls[j]["logp"])
               for i in range(3) for j in range(i + 1, 3))
    assert calls[0]["positions"].tolist() == d1.tolist()
    assert calls[1]["positions"].tolist() == d2.tolist()
    assert calls[2]["positions"].tolist() == d2.tolist()
    assert np.array_equal(calls[0]["values"], res.u1_disclosed)
    assert np.array_equal(calls[1]["values"], res.u2_disclosed)
    # The L2 metrics are new log metrics gathered from scratch, not L1 state.
    assert np.array_equal(calls[1]["logp"], probs_to_symbol_metric(res.p2_hat_probs).logp)
    assert np.array_equal(calls[2]["logp"], probs_to_symbol_metric(res.p2_true_probs).logp)
    assert not np.shares_memory(res.p2_hat_probs, res.p1_probs)
    assert not np.shares_memory(res.p2_true_probs, res.p1_probs)


def test_p4_a05_full_label_single_final_tag_and_injection_seams():
    n, k1, k2 = 4, 1, 1
    table, p1, p2, d1, d2, sample = fixture(n, TEST_SEED_C, k1, k2)
    res = run_block(sample, p1, p2, d1, d2, n, k1, k2)
    assert res.operational.tag_invoked
    assert np.array_equal(
        res.operational.label_hat, res.operational.low_hat + 32 * res.operational.high_hat
    )
    # Literal bit expansion and independent tag arithmetic.
    assert np.array_equal(tl.labels_to_bits(res.labels_true), oracle_labels_to_bits(res.labels_true))
    seed = tl.block_toeplitz_seed_bits(
        "operational", 0, master=TEST_SEED_F, bit_length=tl.seed_bits_for(n)
    )
    assert np.array_equal(seed, oracle_seed_bits(TEST_SEED_F, "operational", 0, tl.seed_bits_for(n)))
    tag_true = oracle_tag_for("operational", 0, TEST_SEED_F, n, res.labels_true)
    tag_hat = oracle_tag_for("operational", 0, TEST_SEED_F, n, res.operational.label_hat)
    assert res.operational.tag_pass == (tag_true == tag_hat)
    events = tl.block_events(res, k1=k1, k2=k2, n=n)
    for arm in ("operational", "oracle"):
        tags = [e for e in events if e["event_id"] == f"block-0-{arm}-verification"]
        assert len(tags) <= 1
    # Wrong-tag injection: tag mismatch is verify_failed, never success.
    wrong = bytes([tag_true[0] ^ 0xFF]) + tag_true[1:]
    assert wrong != tag_true
    mismatch = run_block(sample, p1, p2, d1, d2, n, k1, k2, tag_override=wrong)
    assert mismatch.operational.outcome == "verify_failed"
    assert mismatch.operational.exact is False
    # Forced tag collision on a wrong label is undetected, never success.
    table_dep = injected_dependent_table()
    p1_dep, p2_dep = derive_p1(table_dep), derive_p2(table_dep)
    bob = np.array([0, 0], dtype=np.int64)
    high = np.array([1, 0], dtype=np.int64)
    low = np.array([0, 0], dtype=np.int64)
    true_tag = oracle_tag_for("operational", 0, TEST_SEED_F, 2, low + 32 * high)
    collision = tl.run_two_layer_block(
        0, high, low, bob, field=FIELD, p1_table=p1_dep, p2_table=p2_dep,
        d1=np.array([0]), d2=np.array([0]), n=2, k1=1, k2=1,
        toeplitz_master=TEST_SEED_F, l1_candidate_override=np.array([0, 0]),
        tag_override=true_tag,
    )
    assert collision.operational.label_match is False
    assert collision.operational.tag_pass is True
    assert collision.operational.outcome == "undetected"
    assert collision.operational.exact is False


def test_p4_a06_truth_mutation_invariance_and_sentinel():
    protected = [np.array([1, 2, 3], dtype=np.int64)]
    truth = np.array([4, 5, 6], dtype=np.int64)
    assert tl._truth_isolation_sentinel(protected, [(truth, 32)]) is True
    assert protected[0].tolist() == [1, 2, 3]
    assert truth.tolist() == [5, 6, 7]
    aliased = [truth]
    assert tl._truth_isolation_sentinel(aliased, [(truth, 32)]) is False
    assert truth.tolist() == [6, 7, 8]
    n, k1, k2 = 4, 1, 2
    table, p1, p2, d1, d2, sample = fixture(n, TEST_SEED_D, k1, k2)
    res = run_block(sample, p1, p2, d1, d2, n, k1, k2)
    assert res.operational.truth_leak_violation is False
    assert res.oracle.truth_leak_violation is False
    assert not np.shares_memory(res.p2_hat_probs, res.labels_true)
    assert not np.shares_memory(res.operational.label_hat, res.labels_true)
    assert not np.shares_memory(res.p1_probs, res.u1_disclosed)
    # Same inputs -> bitwise identical operational results (no hidden state).
    res2 = run_block(sample, p1, p2, d1, d2, n, k1, k2)
    assert np.array_equal(res.p2_hat_probs, res2.p2_hat_probs)
    assert np.array_equal(res.operational.label_hat, res2.operational.label_hat)
    # Mutating the caller's own arrays after the call cannot alter captured results.
    snapshot = res.p2_hat_probs.copy()
    sample.bob[0] = (sample.bob[0] + 7) % 1024
    sample.high[0] = (sample.high[0] + 1) % 32
    sample.low[0] = (sample.low[0] + 1) % 32
    assert np.array_equal(res.p2_hat_probs, snapshot)


def test_p4_a07_tiny_exhaustive_probability_and_decode_oracles():
    for n, use_vector in ((2, False), (4, True)):
        table, p1, p2, d1, d2, sample = fixture(n, TEST_SEED_E + n, 1, 1)
        res = run_block(sample, p1, p2, d1, d2, n, 1, 1)
        for metric_probs, positions, disclosed in (
            (res.p1_probs, d1, res.u1_disclosed),
            (res.p2_hat_probs, d2, res.u2_disclosed),
            (res.p2_true_probs, d2, res.u2_disclosed),
        ):
            metric = probs_to_symbol_metric(metric_probs)
            decoded = sc_decode(
                metric.logp, field=FIELD, alpha=2,
                known_positions=positions, known_values=disclosed,
            )
            for i in range(n):
                prefix = decoded.u_hat[:i]
                if use_vector:
                    ora = empirical_oracle_mod.empirical_oracle_sc_metric_vectorized(
                        metric.logp, prefix, field=FIELD
                    )
                else:
                    ora = oracle_mod.oracle_sc_metric(metric.logp, prefix, field=FIELD)
                oracle_mod.compare_sc_vectors(
                    decoded.decision_metrics[i], ora,
                    n=n, coordinate=i, prefix=prefix,
                    prob_tol=PROB_TOL, log_tol=LOG_TOL,
                )
        assert res.operational.l2_invoked and res.oracle.l2_invoked


def test_p4_a08_forced_wrong_l1_propagation():
    pre = tl.injected_wrong_l1_propagation_check()
    assert pre["passed"] is True and pre["decoder_calls"] == 0
    assert pre["metric_divergent"] is True and pre["label_divergent"] is True
    table = injected_dependent_table()
    p1, p2 = derive_p1(table), derive_p2(table)
    bob = np.array([0, 0], dtype=np.int64)
    high = np.array([1, 0], dtype=np.int64)
    low = np.array([0, 0], dtype=np.int64)
    wrong = np.array([0, 0], dtype=np.int64)
    res = tl.run_two_layer_block(
        0, high, low, bob, field=FIELD, p1_table=p1, p2_table=p2,
        d1=np.array([0]), d2=np.array([0]), n=2, k1=1, k2=1,
        toeplitz_master=TEST_SEED_F, l1_candidate_override=wrong,
    )
    assert res.oracle_candidate_divergence is True
    assert not np.array_equal(res.p2_hat_probs, res.p2_true_probs)
    assert float(np.abs(res.p2_hat_probs - res.p2_true_probs).max()) > 0.25
    record = tl._block_record(res)
    assert record["oracle_candidate_divergence"] is True
    # The same block without the override keeps the true candidate field true.
    assert np.array_equal(res.p2_true_probs, oracle_gather_p2(bob, high, p2))


def test_p4_a09_buckets_recount_tamper_and_five_file_schema():
    root = Path(tempfile.mkdtemp()) / "gate_root"
    run = tl.run_two_layer_dev_gate(
        run_seed=TEST_SEED_A, toeplitz_master=TEST_SEED_B, blocks=4,
        out_root=str(root), n=4, k1=1, k2=2,
    )
    assert all(run.summary["hard_gates"].values())
    for arm_name in ("operational", "oracle"):
        totals = run.summary["outcome_totals"][arm_name]
        assert sum(totals.values()) == 4
        assert totals["resource_abort"] == 0
    for result in run.results:
        for arm in (result.operational, result.oracle):
            assert tl._arm_record_consistent(arm, k1=1, k2=2, n=4)
    for key in ("key_dependent_bits", "public_control_bits", "tag_invocations"):
        assert run.incremental[key] == run.recount[key]
    assert run.mismatches == []
    # Event-order invariant: L1 disclosure precedes L2 disclosure precedes the tag.
    order = {}
    for event in run.events:
        block_id, arm = event["event_id"].split("-")[1], event["event_id"].split("-")[2]
        order.setdefault((block_id, arm), []).append(event["event_type"])
    for types in order.values():
        assert types == sorted(types, key=("l1_disclosure", "l2_disclosure", "verification_tag").index)
    # Tamper detection: a changed event value or an unknown arm is caught.
    tampered = [dict(e) for e in run.events]
    tampered[0]["key_dependent_bits"] += 5
    assert tl.recount_transcript(tampered)["key_dependent_bits"] != run.incremental["key_dependent_bits"]
    bad_arm = [dict(e) for e in run.events]
    bad_arm[0]["event_id"] = "block-0-unknown-l1-disclosure"
    assert_raises_match(ValueError, "arm-tagged", tl.recount_transcript, bad_arm)
    # Record tampering is caught by the structural proof.
    arm0 = run.results[0].operational
    for replacement in (
        {"key_dependent_bits": arm0.key_dependent_bits + 1},
        {"public_control_bits": arm0.public_control_bits + 1},
        {"l2_skipped_by_l1_failure": not arm0.l2_skipped_by_l1_failure},
        {"outcome": "exact"},
        {"tag_invoked": not arm0.tag_invoked},
    ):
        bad = dataclasses.replace(arm0, **replacement)
        assert tl._arm_record_consistent(bad, k1=1, k2=2, n=4) is False, replacement
    # Exactly five compact files; per-block records carry no symbols or labels.
    assert sorted(path.name for path in root.iterdir()) == [
        "aggregate_summary.json",
        "frozen_plan.json",
        "per_block_two_layer_outcomes.json",
        "report.md",
        "transcript_accounting.json",
    ]
    raw = (root / "per_block_two_layer_outcomes.json").read_text(encoding="utf-8")
    for banned in ("high_hat", "low_hat", "label_hat", "labels", "u1_disclosed", "u2_disclosed"):
        assert banned not in raw, banned
    plan = json.loads((root / "frozen_plan.json").read_text(encoding="utf-8"))
    assert plan["run_seed"] == TEST_SEED_A and plan["toeplitz_master"] == TEST_SEED_B
    assert len(plan["disclosure_coordinates"]["D1"]) == 1
    assert len(plan["disclosure_coordinates"]["D2"]) == 2
    assert "seed_hex" not in json.dumps(plan)


def test_failure_taxonomy_l1_l2_impossible_nonfinite():
    n, k1, k2 = 4, 1, 1
    table, p1, p2, d1, d2, sample = fixture(n, TEST_SEED_F, k1, k2)
    real_decode = tl.sc_decode
    calls = {"n": 0}

    def fail_first(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("injected L1 failure")
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(tl, "sc_decode", fail_first):
        res = run_block(sample, p1, p2, d1, d2, n, k1, k2)
    op = res.operational
    assert op.outcome == "decode_failed"
    assert op.l1_decode_failed and not op.l1_executed and not op.tag_invoked
    assert op.l2_skipped_by_l1_failure and not op.l2_invoked
    assert op.key_dependent_bits == 5 * k1 and op.public_control_bits == 0
    assert op.l1_error_type == "RuntimeError" and op.nonfinite is False
    # The oracle arm still runs because true L1 is available.
    assert res.oracle.l2_invoked and res.oracle.tag_invoked
    assert res.oracle_candidate_divergence is None

    calls["n"] = 0

    def fail_second(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        calls["n"] += 1
        if calls["n"] == 2:
            raise NumericNonfiniteError("numeric nonfinite failure: injected L2")
        return real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )

    with patched(tl, "sc_decode", fail_second):
        res2 = run_block(sample, p1, p2, d1, d2, n, k1, k2)
    op2 = res2.operational
    assert op2.outcome == "decode_failed" and op2.l2_decode_failed and not op2.tag_invoked
    assert op2.l1_executed and op2.l2_invoked
    assert op2.key_dependent_bits == 5 * (k1 + k2)
    assert op2.nonfinite is True and op2.l2_error_type == "NumericNonfiniteError"
    assert res2.oracle.tag_invoked

    # Impossible L1 disclosure: the P1 metric has exact-zero support.
    impossible = high_zero_support_table()
    p1_bad, p2_bad = derive_p1(impossible), derive_p2(impossible)
    high = np.array([1, 0, 0, 0], dtype=np.int64)
    low = np.array([0, 0, 0, 0], dtype=np.int64)
    bob = np.array([0, 0, 0, 0], dtype=np.int64)
    res3 = tl.run_two_layer_block(
        0, high, low, bob, field=FIELD, p1_table=p1_bad, p2_table=p2_bad,
        d1=np.array([0]), d2=np.array([0]), n=4, k1=1, k2=1,
        toeplitz_master=TEST_SEED_F,
    )
    assert res3.operational.outcome == "decode_failed"
    assert res3.operational.l1_error_type == "ImpossibleDisclosedValueError"
    assert res3.operational.nonfinite is False
    assert res3.oracle.l2_invoked

    # Impossible L2 disclosure: L1 succeeds, the L2 metric has exact-zero support.
    sparse = low_zero_support_table()
    p1_sp, p2_sp = derive_p1(sparse), derive_p2(sparse)
    res4 = tl.run_two_layer_block(
        0, np.zeros(4, dtype=np.int64), np.array([1, 0, 0, 0], dtype=np.int64),
        np.zeros(4, dtype=np.int64), field=FIELD, p1_table=p1_sp, p2_table=p2_sp,
        d1=np.array([0]), d2=np.array([0]), n=4, k1=1, k2=1,
        toeplitz_master=TEST_SEED_F,
    )
    assert res4.operational.l1_executed is True
    assert res4.operational.outcome == "decode_failed"
    assert res4.operational.l2_error_type == "ImpossibleDisclosedValueError"

    # Nonfinite decision marginals (not an exception) stay fail-closed.
    def nan_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None):
        real = real_decode(
            logp_x, field=field, alpha=alpha,
            known_positions=known_positions, known_values=known_values,
        )
        bad = np.array(real.decision_metrics, copy=True)
        bad[0, 0] = np.nan
        return dataclasses.replace(real, decision_metrics=bad)

    with patched(tl, "sc_decode", nan_decode):
        res5 = run_block(sample, p1, p2, d1, d2, n, k1, k2)
    assert res5.operational.outcome == "decode_failed"
    assert res5.operational.nonfinite is True
    assert res5.operational.l1_error_type == "NumericNonfiniteError"
    assert res5.operational.l1_decode_failed and res5.operational.tag_invoked is False


def test_p4_a11_constants_cli_refusals_and_predecessor_suites():
    assert tl.FROZEN_RUN_SEED == tl.validate_run_seed(tl.FROZEN_RUN_SEED)
    assert tl.FROZEN_TOEPLITZ_MASTER == tl.validate_toeplitz_master(tl.FROZEN_TOEPLITZ_MASTER)
    assert tl.FROZEN_BLOCKS == 96
    assert tl.DEFAULT_N == 256 and tl.DEFAULT_Q == 32
    assert tl.DEFAULT_EPSILON1 == 0.05 and tl.DEFAULT_EPSILON2 == 0.20
    assert tl.DEFAULT_K1 == 45 and tl.DEFAULT_K2 == 110
    assert tl.TAG_BITS == 64 and tl.SEED_BITS == 2623 and tl.MESSAGE_BITS == 2560
    assert tl.DISCLOSED_BITS_PER_COORDINATE == 5
    assert tl.DISCLOSED_BITS_PER_COORDINATE * (45 + 110) + 64 == 839
    assert tl.ARMS == ("operational", "oracle")
    assert tl.OUTCOMES == ("exact", "undetected", "verify_failed", "decode_failed", "resource_abort")

    required_refusals = (
        set(range(2026091200, 2026091214))
        | set(range(2026091314, 2026091322))
        | {2026091330, 2026091340, 2026091341, 2026091350, 2026091351}
    )
    assert tl.BANNED_RUN_SEEDS == frozenset(required_refusals)
    for banned in sorted(required_refusals):
        assert_raises_match(ValueError, "banned", tl.validate_run_seed, banned)
        assert_raises_match(ValueError, "banned", tl.validate_toeplitz_master, banned)
    for seed in TEST_SEEDS:
        assert seed >= 2026091362
        assert seed not in required_refusals
    assert tl.FROZEN_RUN_SEED not in TEST_SEEDS and tl.FROZEN_TOEPLITZ_MASTER not in TEST_SEEDS

    # CLI: exactly the frozen flags, every one required, no production default.
    frozen_argv = [
        "--n", "256", "--epsilon1", "0.05", "--epsilon2", "0.20",
        "--k1", "45", "--k2", "110", "--blocks", "96",
        "--seed", str(tl.FROZEN_RUN_SEED), "--toeplitz-master", str(tl.FROZEN_TOEPLITZ_MASTER),
        "--out-dir", "example_gate_root",
    ]
    parser = tl.build_parser()
    args = parser.parse_args(frozen_argv)
    assert args.n == 256 and args.epsilon1 == 0.05 and args.epsilon2 == 0.20
    assert args.k1 == 45 and args.k2 == 110 and args.blocks == 96
    assert args.toeplitz_master == tl.FROZEN_TOEPLITZ_MASTER
    for index in range(0, len(frozen_argv), 2):
        reduced = frozen_argv[:index] + frozen_argv[index + 2:]
        assert_raises_match(SystemExit, "", parser.parse_args, reduced)

    # Refusals happen before any decoder call or directory creation.
    def forbidden_decode(*args_, **kwargs_):
        raise AssertionError("decoder must not run before refusals")

    existing = Path(tempfile.mkdtemp())
    never = existing / "never"
    with patched(tl, "sc_decode", forbidden_decode):
        assert_raises_match(
            FileExistsError, "refusing to overwrite", tl.run_two_layer_dev_gate,
            run_seed=TEST_SEED_A, toeplitz_master=TEST_SEED_B, blocks=1,
            out_root=str(existing), n=4, k1=1, k2=1,
        )
        assert_raises_match(
            ValueError, "banned", tl.run_two_layer_dev_gate,
            run_seed=2026091351, toeplitz_master=TEST_SEED_B, blocks=1,
            out_root=str(never), n=4, k1=1, k2=1,
        )
        assert_raises_match(
            ValueError, "exceed", tl.run_two_layer_dev_gate,
            run_seed=TEST_SEED_A, toeplitz_master=TEST_SEED_B, blocks=1,
            out_root=str(never), n=512, k1=1, k2=1,
        )
    assert not never.exists()
    assert tl.main(
        [
            "--n", "256", "--epsilon1", "0.05", "--epsilon2", "0.20",
            "--k1", "45", "--k2", "110", "--blocks", "96",
            "--seed", "2026091351", "--toeplitz-master", "2026091361",
            "--out-dir", str(never),
        ]
    ) == 2
    assert not never.exists()

    # Predecessor suites: the accepted Phase 1/4-P1 and Phase 6-R2 suites run.
    start = time.perf_counter()
    counts = {}
    for filename, name in (
        ("test_nbpolar_prior.py", "pre_prior"),
        ("test_nbpolar_transform.py", "pre_transform"),
        ("test_nbpolar_two_layer_rate.py", "pre_two_layer_rate"),
    ):
        module = _load_test_module(filename, name)
        names = sorted(
            item for item in dir(module)
            if item.startswith("test_") and callable(getattr(module, item))
        )
        for item in names:
            try:
                getattr(module, item)()
            except Exception as err:  # noqa: BLE001 -- re-raise with the test name
                raise AssertionError(
                    f"predecessor {filename}:{item} failed: {type(err).__name__}: {err}"
                ) from err
        counts[filename] = len(names)
    assert counts["test_nbpolar_prior.py"] >= 9
    assert sum(counts.values()) >= 15
    EVIDENCE["predecessor_seconds"] = time.perf_counter() - start


def test_no_forbidden_markers_or_import_time_side_effects():
    import re

    source = Path(tl.__file__).read_text(encoding="utf-8")
    lowered = source.lower()
    for marker in FORBIDDEN_MARKERS:
        assert marker not in lowered, f"forbidden marker {marker!r} in two_layer.py"
    for match in re.finditer(r"np\.random\.([A-Za-z_]+)\s*\(", source):
        assert match.group(1) == "default_rng", f"global RNG use: {match.group(0)}"
    assert "open(" not in source
    own = Path(__file__).read_text(encoding="utf-8")
    assert ("." + "workbuddy") not in own
    assert ("two_layer" + "_operational_sc_gate") not in own
    for seed in (tl.FROZEN_RUN_SEED, tl.FROZEN_TOEPLITZ_MASTER):
        assert f"default_rng({seed})" not in own

    empty = Path(tempfile.mkdtemp())
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer as t; "
            "assert t.run_two_layer_dev_gate is not None and t.FROZEN_BLOCKS == 96",
        ],
        cwd=str(empty),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert list(empty.iterdir()) == []


EVIDENCE: dict = {}


def _load_test_module(filename: str, module_name: str):
    path = Path(__file__).resolve().parent / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
