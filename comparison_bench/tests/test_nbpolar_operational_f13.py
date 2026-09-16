"""Focused Phase 4-P16 N=32768 empirical-construction operational f=1.3 tests.

Injected tiny/synthetic tables and arrays plus temporary roots only. No V25
NPZ content open, no Model-F/raw/held-out/real/EVAL artifact, no production
invocation and no output outside a temporary directory. Focused tests use
their own fresh seeds 2026091753..2026091759 and 2026091761..2026091765
(2026091760 skipped: X11 probe seed) and never the frozen P16 streams
2026092000..2026092003 / 2026092010..2026092017 (nor any official prior or
probe seed).

The frozen N=32768 makes real sampling/genie/SC calls too slow for runner
tests, so runner tests patch the three documented seams (``sample_full_block``,
the P13-shared ``block_genie_risks`` and the P16 ``run_operational_block``)
with deterministic fakes; metrics, transform, orders, splits, Wilson,
gates, accounting and checkpointing all run for real. The real operational
arm is exercised separately at tiny n with real SC and the real tag.
Every ``test_*`` takes no arguments, uses plain asserts and restores any
monkeypatched module attribute in a ``finally``.
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

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import operational_f13 as opf

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds (2026091760 skipped: X11 probe seed); the frozen P16
# streams are only read from the module constants and never used as inputs.
TEST_TRAINS = (2026091753, 2026091754, 2026091755, 2026091756)
TEST_DEVS = (
    2026091757, 2026091758, 2026091759, 2026091761,
    2026091762, 2026091763, 2026091764, 2026091765,
)

FROZEN_K_TOTAL = 6811  # floor((1.3*32768*H-64)/5), H from the ratified literals
FROZEN_PUBLIC_BITS = 327743  # 10*32768 + 63


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


def injected_counts(seed: int = 2026091753) -> np.ndarray:
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


def train_formula(k: int, n: int):
    idx = np.arange(n, dtype=np.float64)
    base = float(k + 1)
    return (
        0.005 * base + 1e-7 * idx,
        0.05 * base + 1e-6 * idx,
        0.003 * base + 1e-7 * idx,
        0.03 * base + 1e-6 * idx,
    )


class FakeGenie:
    """Deterministic TRAIN risk fake with the exact calls-counter contract."""

    def __init__(self):
        self.blocks = 0

    def __call__(self, l1_logp, u1, l2_logp, u2, *, field, calls=None):
        if calls is not None:
            calls["genie"] = int(calls.get("genie", 0)) + 2
        k = self.blocks
        self.blocks += 1
        n = int(np.asarray(u1).shape[0])
        e1, h1, e2, h2 = train_formula(k, n)
        return {"e1": e1, "h1": h1, "e2": e2, "h2": h2}


def fake_sample(rng, p_b, f_full, q_high, q_low, n):
    zeros = np.zeros(int(n), dtype=np.int64)
    return zeros, zeros, zeros, zeros


class FakeArm:
    """Scripted operational-DEV fake following the runner's arm contract.

    Cycles ``script`` outcomes; increments ``calls["sc"]`` twice per executed
    block (one L1 plus one L2 attempt) and captures the tag master per stream.
    """

    def __init__(self, script=None):
        self.calls = 0
        self.script = list(script) if script else ["exact"] * 64
        self.masters = {}

    def __call__(self, **kwargs):
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
            seed_bits_for,
        )

        calls = kwargs.get("calls")
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + 2
        n = int(kwargs["n"])
        seed = int(kwargs["stream_seed"])
        self.masters.setdefault(seed, int(kwargs["master"]))
        outcome = self.script[self.calls % len(self.script)]
        self.calls += 1
        k1, k2 = int(kwargs["k1"]), int(kwargs["k2"])
        invoked = outcome in ("exact", "undetected", "verify_failed")
        tag = outcome in ("exact", "undetected", "verify_failed")
        failed_l1 = outcome in ("decode_failed", "nonfinite")
        return opf.OperationalBlockResult(
            stream_seed=seed,
            block_index=int(kwargs["block_index"]),
            outcome=outcome,
            exact=bool(outcome == "exact"),
            label_match=bool(outcome == "exact"),
            tag_pass=bool(outcome in ("exact", "undetected")),
            l1_provenance=None if failed_l1 else opf.Provenance.PRIOR_ONLY.value,
            l2_provenance=None if failed_l1 else opf.Provenance.CANDIDATE_CONDITIONED.value,
            l1_executed=bool(not failed_l1),
            l1_decode_failed=bool(failed_l1),
            l2_invoked=bool(invoked),
            l2_skipped_by_l1_failure=bool(failed_l1),
            l2_decode_failed=False,
            tag_invoked=bool(tag),
            key_dependent_bits=int(
                5 * k1 + (5 * k2 if invoked else 0) + (64 if tag else 0)
            ),
            public_control_bits=int(seed_bits_for(n) if tag else 0),
            nonfinite=bool(outcome == "nonfinite"),
            truth_leak_violation=False,
            l1_error_type=("NumericNonfiniteError" if outcome == "nonfinite"
                           else ("RuntimeError" if failed_l1 else None)),
            l2_error_type=None,
            wall_s=0.001,
            k1=k1,
            k2=k2,
        )


def full_run(out, **over):
    kw = dict(
        train_seeds=list(TEST_TRAINS),
        dev_seeds=list(TEST_DEVS),
        out_dir=out,
    )
    kw.update(over)
    counts = kw.pop("counts", None)
    if counts is None:
        counts = injected_counts()
    seam = kw.pop("expected_entropies", None)
    if seam is None:
        seam = expected_seam(counts)
    return opf.run_operational_f13(
        counts=counts, expected_entropies=seam, **kw
    )


def run_with_fakes(out, script=None, **over):
    genie = FakeGenie()
    arm = FakeArm(script)
    with patched(opf, "sample_full_block", fake_sample):
        with patched(opf, "block_genie_risks", genie):
            with patched(opf, "run_operational_block", arm):
                run = full_run(out, **over)
    return run, genie, arm


# ---- frozen arithmetic and matrix ----

def test_frozen_k_total_pinned():
    # floor((1.3*N*H-64)/5), H from the ratified literals; far from any
    # integer boundary under either float64 spelling of H1+H2.
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_n_scaling as tns,
    )

    for h in (opf.EXPECTED_H1 + opf.EXPECTED_H2, opf.EXPECTED_TOTAL):
        raw = (1.3 * opf.FROZEN_N * h - 64.0) / 5.0
        assert math.floor(raw) == FROZEN_K_TOTAL, (repr(h), repr(raw))
        assert tns.budget_k_total(opf.FROZEN_N, h, 1.3) == FROZEN_K_TOTAL
    assert 5 * FROZEN_K_TOTAL + 64 == 34119
    assert 5 * FROZEN_K_TOTAL + 64 <= 1.3 * opf.FROZEN_N * (opf.EXPECTED_H1 + opf.EXPECTED_H2)
    f = (5 * FROZEN_K_TOTAL + 64) / (opf.FROZEN_N * (opf.EXPECTED_H1 + opf.EXPECTED_H2))
    assert f <= 1.3 and abs(f - 1.2998502888172847) < 1e-12


def test_frozen_matrix_constants_pinned():
    assert opf.FROZEN_N == 32768
    assert opf.FROZEN_TRAIN_SEEDS == (2026092000, 2026092001, 2026092002, 2026092003)
    assert opf.FROZEN_DEV_SEEDS == tuple(2026092010 + i for i in range(8))
    assert opf.FROZEN_TRAIN_BLOCKS_PER_STREAM == 4
    assert opf.FROZEN_DEV_BLOCKS_PER_STREAM == 8
    assert opf.FROZEN_TRAIN_TOTAL == 16
    assert opf.FROZEN_DEV_TOTAL == 64
    assert opf.PLANNED_GENIE_CALLS == 32
    assert opf.PLANNED_SC_CALLS_MAX == 128
    assert opf.FROZEN_CHUNK_ROWS == 512
    assert opf.FROZEN_TAG_BITS == 64
    assert opf.PUBLIC_TAG_MASTER_OFFSET == 10000
    assert opf.PUBLIC_CONTROL_BITS_PER_TAG == FROZEN_PUBLIC_BITS
    assert opf.OUTCOMES == ("exact", "undetected", "verify_failed",
                            "decode_failed", "nonfinite", "resource_abort")
    assert set(opf.FROZEN_TRAIN_SEEDS).isdisjoint(opf.FROZEN_DEV_SEEDS)
    # Fresh test seeds never touch the frozen streams, the X11 probe seed,
    # or known official priors.
    assert set(TEST_TRAINS).isdisjoint(opf.FROZEN_TRAIN_SEEDS + opf.FROZEN_DEV_SEEDS)
    assert set(TEST_DEVS).isdisjoint(opf.FROZEN_TRAIN_SEEDS + opf.FROZEN_DEV_SEEDS)
    assert set(TEST_TRAINS).isdisjoint(TEST_DEVS)
    assert 2026091760 not in TEST_TRAINS + TEST_DEVS
    for prior in (2026091650, 2026091680, 2026091710, 2026091820, 2026091860,
                  2026091930, 2026091960, 2026091800, 2026091811):
        assert prior not in TEST_TRAINS + TEST_DEVS


def test_p13_p12_helpers_shared_not_reimplemented():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        empirical_genie_scaling as egs,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_n_scaling as tns,
    )

    assert opf.block_genie_risks is egs.block_genie_risks
    assert opf.select_empirical_split is egs.select_empirical_split
    assert opf.budget_k_total is tns.budget_k_total


# ---- outcome buckets and precedence ----

def test_outcome_classifier_every_bucket_and_precedence():
    c = opf.classify_operational_outcome
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=True, label_match=True) == "exact"
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=True, label_match=False) == "undetected"
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=False, label_match=False) == "verify_failed"
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=False, label_match=True) == "verify_failed"
    assert c(l1_failed=True, l2_failed=False, nonfinite=False,
             tag_pass=False, label_match=False) == "decode_failed"
    assert c(l1_failed=False, l2_failed=True, nonfinite=False,
             tag_pass=False, label_match=False) == "decode_failed"
    # Nonfinite outranks generic decode failure on either layer.
    assert c(l1_failed=True, l2_failed=False, nonfinite=True,
             tag_pass=False, label_match=False) == "nonfinite"
    assert c(l1_failed=False, l2_failed=True, nonfinite=True,
             tag_pass=False, label_match=False) == "nonfinite"
    assert c(l1_failed=True, l2_failed=True, nonfinite=True,
             tag_pass=False, label_match=False) == "nonfinite"
    # The resource_abort bucket is runner-level (budget stop), never from SC.
    abort = opf._abort_block(2026091757, 3, k1=4, k2=5)
    assert abort.outcome == "resource_abort"
    assert abort.exact is False
    assert abort.key_dependent_bits == 0 and abort.public_control_bits == 0


# ---- Wilson boundary and labels ----

def test_wilson_boundary_literals_and_recovery_gates():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.protocol import (
        WILSON_Z,
        wilson_lower_bound,
    )

    lb62 = wilson_lower_bound(62, 64, z=WILSON_Z)
    lb61 = wilson_lower_bound(61, 64, z=WILSON_Z)
    assert round(lb62, 10) == opf.WILSON_LB_62_OF_64 == 0.9098711859
    assert round(lb61, 10) == opf.WILSON_LB_61_OF_64 == 0.8883797144
    assert lb62 >= 0.90 and lb61 < 0.90
    assert opf.check_wilson_boundary() == {"lb_62_of_64": lb62, "lb_61_of_64": lb61}
    good = opf.recovery_gates(62)
    assert good["pass"] is True
    assert good["exact_at_least_62_of_64"] is True
    assert good["wilson_lower_bound_at_least_0p90"] is True
    assert opf.recovery_gates(64)["pass"] is True
    bad61 = opf.recovery_gates(61)
    assert bad61["pass"] is False
    assert bad61["exact_at_least_62_of_64"] is False
    assert bad61["wilson_lower_bound_at_least_0p90"] is False
    assert_raises_match(ValueError, "must not exceed", opf.recovery_gates, 65)


def test_select_label_three_branches():
    good = {g: True for g in opf.INTEGRITY_GATE_ORDER}
    assert opf.select_label(good, True) == opf.CANDIDATE_LABEL
    assert opf.select_label(good, False) == opf.NOT_CONFIRMED_LABEL
    bad = dict(good)
    bad["undetected_zero"] = False
    assert opf.select_label(bad, True) == "BLOCKED(undetected_zero)"
    bad2 = dict(good)
    bad2["target_population_contract"] = False
    bad2["undetected_zero"] = False
    assert opf.select_label(bad2, True) == "BLOCKED(target_population_contract)"


# ---- tag domain separation ----

def test_tag_seed_domain_separation_and_lengths():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        seed_bits_for,
    )

    assert opf.SEED_PREFIX == "nbpolar-p16-operational-f13-seed"
    a = opf.operational_seed_bits(2026091757 + 10000, 8, 3)
    assert len(a) == seed_bits_for(8) == 143
    assert np.array_equal(a, opf.operational_seed_bits(2026091757 + 10000, 8, 3))
    assert not np.array_equal(a, opf.operational_seed_bits(2026091757 + 10000, 8, 4))
    assert not np.array_equal(a, opf.operational_seed_bits(2026091758 + 10000, 8, 3))
    assert not np.array_equal(a, opf.operational_seed_bits(2026091757 + 10000, 16, 3))
    assert len(opf.operational_seed_bits(1, 32768, 0)) == FROZEN_PUBLIC_BITS


# ---- real arm at tiny n ----

def tiny_inputs(n=8, seed=2026091753):
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        two_layer as tl2,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
        make_gf32,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
        derive_p1,
        derive_p2,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
        polar_transform,
    )

    table = tl2.build_injected_joint_table(epsilon1=0.05, epsilon2=0.2)
    p_b = np.full(1024, 1.0 / 1024)
    rng = np.random.default_rng(seed)
    bob, _, high, low = opf.sample_full_block(rng, p_b, table, 32, 32, n)
    field = make_gf32()
    u1 = polar_transform(high, field=field, alpha=2)
    u2 = polar_transform(low, field=field, alpha=2)
    labels = (low + 32 * high).astype(np.int64)
    return {
        "bob": bob, "high": high, "low": low, "u1": u1, "u2": u2,
        "labels": labels, "bits": tl2.labels_to_bits(labels),
        "field": field, "p1": derive_p1(table), "p2": derive_p2(table),
    }


def test_real_arm_full_disclosure_exact_and_accounting():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        seed_bits_for,
    )

    n = 8
    data = tiny_inputs(n)
    before = {k: np.array(data[k], copy=True) for k in ("bob", "high", "low", "u1", "u2")}
    calls = {"sc": 0}
    result = opf.run_operational_block(
        n=n, stream_seed=2026091753, block_index=0,
        bob=data["bob"], high_true=data["high"], low_true=data["low"],
        u1_true=data["u1"], u2_true=data["u2"],
        labels_true=data["labels"], labels_true_bits=data["bits"],
        field=data["field"], p1_table=data["p1"], p2_table=data["p2"],
        l1_order=np.arange(n), l2_order=np.arange(n)[::-1],
        k1=n, k2=n, master=2026091753 + 10000, calls=calls,
    )
    # Full disclosure forces exact recovery with the real tag.
    assert result.outcome == "exact"
    assert result.exact is True and result.tag_pass is True and result.label_match is True
    assert result.key_dependent_bits == 5 * (n + n) + 64
    assert result.public_control_bits == seed_bits_for(n)
    assert result.l1_provenance == "PRIOR_ONLY"
    assert result.l2_provenance == "CANDIDATE_CONDITIONED"
    assert result.nonfinite is False and result.truth_leak_violation is False
    assert calls == {"sc": 2}
    for key, snapshot in before.items():
        assert np.array_equal(data[key], snapshot), key


def test_causal_l1_candidate_l2_wiring_sentinel():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
        gather_p2_metrics as real_gather,
    )

    n = 8
    data = tiny_inputs(n)
    captured = {}
    wrong = ((data["high"] + 1) % 32).astype(np.int64)
    assert not np.array_equal(wrong, data["high"])

    def spy(bob, high, table):
        captured["high"] = np.array(high)
        return real_gather(bob, high, table)

    with patched(opf, "gather_p2_metrics", spy):
        result = opf.run_operational_block(
            n=n, stream_seed=2026091753, block_index=1,
            bob=data["bob"], high_true=data["high"], low_true=data["low"],
            u1_true=data["u1"], u2_true=data["u2"],
            labels_true=data["labels"], labels_true_bits=data["bits"],
            field=data["field"], p1_table=data["p1"], p2_table=data["p2"],
            l1_order=np.arange(n), l2_order=np.arange(n),
            k1=2, k2=3, master=2026091753 + 10000,
            l1_candidate_override=wrong,
        )
    # The L2 metric saw exactly the hard L1 candidate (here the forced-wrong
    # override), never the true high layer.
    assert np.array_equal(captured["high"][0], wrong)
    assert not np.array_equal(captured["high"][0], data["high"])
    assert result.l2_provenance == "CANDIDATE_CONDITIONED"
    assert result.truth_leak_violation is False


def test_real_arm_tag_master_domain_reaches_seed():
    seen = {}

    def spy_tag(bits, seed, tag_bits):
        seen.setdefault("seeds", []).append(np.array(seed, copy=True))
        seen["tag_bits"] = tag_bits
        from comparison_bench.src.comparison_bench.formal_ir.shared import (
            toeplitz_tag as real_tag,
        )

        return real_tag(bits, seed, tag_bits)

    n = 8
    data = tiny_inputs(n)
    kw = dict(
        n=n, stream_seed=2026091753, block_index=2,
        bob=data["bob"], high_true=data["high"], low_true=data["low"],
        u1_true=data["u1"], u2_true=data["u2"],
        labels_true=data["labels"], labels_true_bits=data["bits"],
        field=data["field"], p1_table=data["p1"], p2_table=data["p2"],
        l1_order=np.arange(n), l2_order=np.arange(n),
        k1=n, k2=n, tag_fn=spy_tag,
    )
    opf.run_operational_block(master=2026091753 + 10000, **kw)
    assert len(seen["seeds"]) == 2  # true tag + hat tag share one seed
    first = seen["seeds"][0]
    assert seen["tag_bits"] == 64 and len(first) == 143
    opf.run_operational_block(master=2026091754 + 10000, **kw)
    assert len(seen["seeds"]) == 4
    assert np.array_equal(seen["seeds"][1], first)
    assert not np.array_equal(seen["seeds"][2], first)


# ---- full runner with fakes ----

def test_full_run_construction_gates_and_accounting():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, genie, arm = run_with_fakes(out)
        assert sorted(p.name for p in out.iterdir()) == sorted(opf.OUTPUT_FILES)
        cell = run.construction["cell"]
        assert cell["n"] == 32768
        assert cell["train_seeds"] == list(TEST_TRAINS)
        assert cell["dev_seeds"] == list(TEST_DEVS)
        assert cell["train_used_l1"] == 16 and cell["train_used_l2"] == 16
        assert cell["train_impossible"] == 0
        # Exact call accounting: 16 TRAIN blocks x 2 genie layers, and the
        # fake arm's two SC attempts per executed DEV block.
        assert genie.blocks == 16
        assert run.summary["genie_calls"] == 32 == opf.PLANNED_GENIE_CALLS
        assert run.summary["sc_calls"] == 128
        assert run.summary["integrity"]["no_unregistered_calls"] is True
        # Injected path: zero reads/attempts, exact accounting.
        assert run.summary["input_mode"] == "injected_counts"
        acc = run.summary["attempt_read_accounting"]
        assert acc["artifact_content_reads_consumed_by_this_run"] == 0
        assert acc["attempts_consumed_by_this_run"] == 0
        assert acc["open_count"] == 0
        assert opf._NPZ_CONTENT_OPENED is False
        # Frozen K replay from the injected entropies (formula arm holds on
        # injected data; the literal replay cannot).
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
            target_n_scaling as tns,
        )

        injected_h = run.summary["entropy"]["total"]
        assert cell["k_total"] == tns.budget_k_total(32768, injected_h, 1.3)
        assert 5 * cell["k_total"] + 64 <= 1.3 * 32768 * injected_h
        replay = opf.select_empirical_split(
            32768,
            np.asarray(cell["pooled_e1_mean"]),
            np.asarray(cell["pooled_h1_mean"]),
            np.asarray(cell["pooled_e2_mean"]),
            np.asarray(cell["pooled_h2_mean"]),
            cell["k_total"],
        )
        assert (replay["k1"], replay["k2"]) == (cell["k1"], cell["k2"])
        assert abs(replay["residual"] - cell["train_residual"]) < 1e-9
        assert replay["l1_order"].tolist() == cell["l1_order"]
        assert replay["l2_order"].tolist() == cell["l2_order"]
        # Pooled means equal the closed form over the 16 TRAIN fake blocks.
        for key, pos in (("pooled_e1_mean", 0), ("pooled_h1_mean", 1),
                         ("pooled_e2_mean", 2), ("pooled_h2_mean", 3)):
            total = np.zeros(32768)
            for k in range(16):
                total += train_formula(k, 32768)[pos]
            assert np.allclose(np.asarray(cell[key]), total / 16, rtol=0, atol=1e-12)
        # Orders are permutations with a matching freeze digest.
        for key in ("l1_order", "l2_order"):
            assert sorted(cell[key]) == list(range(32768))
        # DEV: 64 exact records with full-disclosure accounting.
        lines = (out / "per_block_outcomes.jsonl").read_text().splitlines()
        assert len(lines) == 64
        records = [json.loads(line) for line in lines]
        assert {r["outcome"] for r in records} == {"exact"}
        first = records[0]
        assert set(first) == {"stream_seed", "block_index", "outcome", "exact",
                              "label_match", "tag_pass", "l1_provenance",
                              "l2_provenance", "l1_executed", "l1_decode_failed",
                              "l2_invoked", "l2_skipped_by_l1_failure",
                              "l2_decode_failed", "tag_invoked",
                              "key_dependent_bits", "public_control_bits",
                              "nonfinite", "truth_leak_violation",
                              "l1_error_type", "l2_error_type", "error",
                              "k1", "k2", "wall_s", "resources"}
        assert set(first["resources"]) == {"wall_s", "rss_bytes_hwm",
                                           "vm_peak_kb", "vm_size_kb"}
        for record in records:
            assert record["key_dependent_bits"] == 5 * (cell["k1"] + cell["k2"]) + 64
            assert record["public_control_bits"] == FROZEN_PUBLIC_BITS
            assert record["error"] is None
        assert run.summary["outcome_counts"] == {
            "exact": 64, "undetected": 0, "verify_failed": 0,
            "decode_failed": 0, "nonfinite": 0, "resource_abort": 0,
        }
        assert run.summary["exact_count"] == 64
        assert run.summary["recovery"]["pass"] is True
        # Tag masters are exactly DEV seed + 10000 per stream.
        assert arm.masters == {s: s + 10000 for s in TEST_DEVS}
        # Transcript recount is exact over all disclosure/tag/public events.
        disclosure = run.summary["disclosure"]
        assert disclosure["mismatches"] == []
        assert disclosure["key_dependent_bits"] == 64 * (5 * (cell["k1"] + cell["k2"]) + 64)
        assert disclosure["public_control_bits"] == 64 * FROZEN_PUBLIC_BITS
        assert disclosure["tag_invocations"] == 64
        assert disclosure["recount"] == {
            "key_dependent_bits": disclosure["key_dependent_bits"],
            "public_control_bits": disclosure["public_control_bits"],
            "tag_invocations": 64,
            "event_types": {"l1_disclosure": 64, "l2_disclosure": 64,
                            "verification_tag": 64},
        }
        # Test-local seeds are not the frozen matrix: the shape gates fail
        # while every other mechanical gate holds.
        integrity = run.summary["integrity"]
        assert integrity["target_population_contract"] is True
        assert integrity["construction_frozen_before_dev"] is True
        assert integrity["train_dev_coverage_complete"] is False
        assert integrity["streams_disjoint_frozen"] is False
        assert integrity["buckets_disjoint_exhaustive"] is True
        assert integrity["truth_isolation"] is True
        assert integrity["undetected_zero"] is True
        assert integrity["nonfinite_zero"] is True
        assert integrity["disclosure_recount_exact"] is True
        assert integrity["attempt_read_accounting_exact"] is True
        assert integrity["resource_limits_met_and_no_abort"] is True
        assert run.summary["outcome_label"] == "BLOCKED(train_dev_coverage_complete)"


def test_undetected_and_nonfinite_buckets_block_gates():
    script = ["exact"] * 62 + ["undetected", "nonfinite"]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _, _ = run_with_fakes(out, script)
        assert run.summary["outcome_counts"]["undetected"] == 1
        assert run.summary["outcome_counts"]["nonfinite"] == 1
        assert run.summary["outcome_counts"]["exact"] == 62
        assert run.summary["integrity"]["undetected_zero"] is False
        assert run.summary["integrity"]["nonfinite_zero"] is False
        assert run.summary["outcome_label"] == "BLOCKED(train_dev_coverage_complete)"
        lines = (out / "per_block_outcomes.jsonl").read_text().splitlines()
        by_outcome = {}
        for line in lines:
            record = json.loads(line)
            by_outcome.setdefault(record["outcome"], []).append(record)
        # Undetected is never success: exact is False on that record.
        assert by_outcome["undetected"][0]["exact"] is False
        assert by_outcome["undetected"][0]["tag_pass"] is True
        assert by_outcome["nonfinite"][0]["nonfinite"] is True
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _, _ = run_with_fakes(out, ["exact"] * 63 + ["nonfinite"])
        assert run.summary["integrity"]["undetected_zero"] is True
        assert run.summary["integrity"]["nonfinite_zero"] is False


def test_partial_decode_failure_counts_disclosed_bits_only():
    script = ["exact"] * 60 + ["decode_failed"] * 4
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _, _ = run_with_fakes(out, script)
        cell = run.construction["cell"]
        lines = (out / "per_block_outcomes.jsonl").read_text().splitlines()
        records = [json.loads(line) for line in lines]
        failed = [r for r in records if r["outcome"] == "decode_failed"]
        assert len(failed) == 4
        for record in failed:
            assert record["key_dependent_bits"] == 5 * cell["k1"]
            assert record["public_control_bits"] == 0
            assert record["tag_invoked"] is False
        disclosure = run.summary["disclosure"]
        assert disclosure["mismatches"] == []
        assert disclosure["tag_invocations"] == 60
        assert disclosure["recount"]["event_types"] == {
            "l1_disclosure": 64, "l2_disclosure": 60, "verification_tag": 60,
        }
        assert run.summary["integrity"]["disclosure_recount_exact"] is True


def test_recount_tamper_detected():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _, _ = run_with_fakes(out)
        events = run.events
        assert len(events) == 64 * 3
        recount = opf.recount_events(events)
        tampered = [dict(e) for e in events]
        tampered[0] = dict(tampered[0])
        tampered[0]["key_dependent_bits"] += 1
        recount2 = opf.recount_events(tampered)
        assert recount2["key_dependent_bits"] != recount["key_dependent_bits"]
        incremental = {"key_dependent_bits": recount["key_dependent_bits"],
                       "public_control_bits": recount["public_control_bits"],
                       "tag_invocations": recount["tag_invocations"]}
        assert opf._transcript_mismatches(incremental, recount) == []
        assert opf._transcript_mismatches(incremental, recount2) != []
        assert_raises_match(ValueError, "not N/arm-tagged", opf.recount_events,
                            [{"event_id": "bogus", "event_type": "l1_disclosure",
                              "key_dependent_bits": 0, "public_control_bits": 0}])
        assert_raises_match(ValueError, "not frozen", opf.recount_events,
                            [dict(events[0], event_type="bogus_type")])


# ---- refusals, accounting, failure paths ----

def test_grouping_and_contract_refusals_before_open():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    def forbidden_genie(*args, **kwargs):
        raise AssertionError("no genie call may happen on refusal")

    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on refusal")

    with tempfile.TemporaryDirectory() as tmp:
        with patched(opf, "load_v25_channel_counts", forbidden_loader):
            with patched(opf, "block_genie_risks", forbidden_genie):
                with patched(opf, "run_operational_block", forbidden_arm):
                    assert_raises_match(
                        ValueError, "exactly 4 streams", full_run, Path(tmp) / "a",
                        train_seeds=list(TEST_TRAINS)[:3],
                    )
                    assert_raises_match(
                        ValueError, "exactly 8 streams", full_run, Path(tmp) / "b",
                        dev_seeds=list(TEST_DEVS)[:7],
                    )
                    assert_raises_match(
                        ValueError, "disjoint", full_run, Path(tmp) / "c",
                        dev_seeds=list(TEST_TRAINS) + list(TEST_DEVS)[:4],
                    )
                    assert_raises_match(
                        ValueError, "train-blocks-per-stream", full_run,
                        Path(tmp) / "d", train_blocks_per_stream=8,
                    )
                    assert_raises_match(
                        ValueError, "dev-blocks-per-stream", full_run,
                        Path(tmp) / "e", dev_blocks_per_stream=4,
                    )
                    assert_raises_match(
                        ValueError, "chunk-rows", full_run, Path(tmp) / "f",
                        chunk_rows=64,
                    )
                    assert_raises_match(
                        ValueError, "tag-bits", full_run, Path(tmp) / "g",
                        tag_bits=32,
                    )
                    assert_raises_match(
                        ValueError, "n=32768", full_run, Path(tmp) / "h",
                        n=16384,
                    )
                    assert_raises_match(
                        ValueError, "floor", full_run, Path(tmp) / "i",
                        floor=1e-12,
                    )
                    assert_raises_match(
                        FileNotFoundError, "not found", opf.run_operational_f13,
                        counts_path=str(Path(tmp) / "missing.npz"),
                        train_seeds=list(TEST_TRAINS), dev_seeds=list(TEST_DEVS),
                        out_dir=Path(tmp) / "j",
                    )
        for name in ("a", "b", "c", "d", "e", "f", "g", "h", "i"):
            assert not (Path(tmp) / name).exists()


def test_checkpoint_resume_refusal_zero_execution():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on refusal")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        root.mkdir()
        sentinel = root / "sentinel.txt"
        sentinel.write_text("untouched", encoding="utf-8")
        with patched(opf, "load_v25_channel_counts", forbidden_loader):
            with patched(opf, "run_operational_block", forbidden_arm):
                assert_raises_match(
                    FileExistsError, "refusing to overwrite",
                    full_run, root,
                )
        assert sentinel.read_text(encoding="utf-8") == "untouched"
        assert sorted(p.name for p in root.iterdir()) == ["sentinel.txt"]


def test_single_open_guard_refuses_reopen():
    saved = opf._NPZ_CONTENT_OPENED
    opf._NPZ_CONTENT_OPENED = True
    try:
        with tempfile.TemporaryDirectory() as tmp:
            # NPZ-mode call while the single open is consumed: reopen
            # refused without touching the filesystem counts path.
            assert_raises_match(
                ValueError, "reopen refused",
                opf.run_operational_f13,
                counts_path="/nonexistent/channel_counts.npz",
                train_seeds=list(TEST_TRAINS), dev_seeds=list(TEST_DEVS),
                out_dir=Path(tmp) / "out",
            )
    finally:
        opf._NPZ_CONTENT_OPENED = saved
    assert opf._NPZ_CONTENT_OPENED is False


def test_precondition_failure_zero_calls_and_blocked_stubs():
    seen = {"genie": 0, "sc": 0}

    def boom_genie(*args, **kwargs):
        seen["genie"] += 1
        raise AssertionError("no genie call may happen before the contract passes")

    def boom_arm(**kwargs):
        seen["sc"] += 1
        raise AssertionError("no SC call may happen before the contract passes")

    counts = injected_counts()
    counts[:, 0] = 0.0  # zero Bob column breaks the target contract
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(opf, "sample_full_block", fake_sample):
            with patched(opf, "block_genie_risks", boom_genie):
                with patched(opf, "run_operational_block", boom_arm):
                    assert_raises_match(
                        opf.TargetPopulationContractError,
                        "BLOCKED(target_population_contract)",
                        opf.run_operational_f13, counts=counts,
                        expected_entropies=(opf.EXPECTED_H1, opf.EXPECTED_H2,
                                            opf.EXPECTED_H1 + opf.EXPECTED_H2),
                        train_seeds=list(TEST_TRAINS), dev_seeds=list(TEST_DEVS),
                        out_dir=root,
                    )
        assert seen == {"genie": 0, "sc": 0}
        assert sorted(p.name for p in root.iterdir()) == sorted(opf.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(target_population_contract)"
        assert blocked["attempt_read_accounting"]["attempts_consumed_by_this_run"] == 0


def test_memory_error_classification_path():
    genie = FakeGenie()

    def oom(**kwargs):
        raise MemoryError("injected exhaustion")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(opf, "sample_full_block", fake_sample):
            with patched(opf, "block_genie_risks", genie):
                with patched(opf, "run_operational_block", oom):
                    assert_raises_match(
                        opf.OperationalF13ResourceError,
                        "BLOCKED(resource_limits_met_and_no_abort)",
                        full_run, root,
                    )
        assert sorted(p.name for p in root.iterdir()) == sorted(opf.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"
        assert opf._NPZ_CONTENT_OPENED is False


def test_budget_stop_abort_fill_preserves_checkpoints():
    genie = FakeGenie()
    arm = FakeArm()
    calls = {"n": 0}
    real_guard = opf._budget_exceeded

    def flaky(start, cap):
        calls["n"] += 1
        if calls["n"] > 16 + 2:  # 16 TRAIN blocks + 2 DEV blocks, then stop
            return "wall_s"
        return real_guard(start, cap)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(opf, "sample_full_block", fake_sample):
            with patched(opf, "block_genie_risks", genie):
                with patched(opf, "run_operational_block", arm):
                    with patched(opf, "_budget_exceeded", flaky):
                        run = full_run(root)
        assert sorted(p.name for p in root.iterdir()) == sorted(opf.OUTPUT_FILES)
        lines = (root / "per_block_outcomes.jsonl").read_text().splitlines()
        assert len(lines) == 64
        records = [json.loads(line) for line in lines]
        aborts = [r for r in records if r["outcome"] == "resource_abort"]
        assert len(aborts) == 62
        assert run.summary["outcome_counts"]["exact"] == 2
        assert run.summary["resource_stop_fired"] is True
        assert run.summary["resource_stop_reason"] == "wall_s"
        assert run.summary["integrity"]["resource_limits_met_and_no_abort"] is False
        assert run.summary["outcome_label"].startswith("BLOCKED(")


def test_chunk_contract_and_cli_parse_refusals():
    import subprocess

    assert opf.FROZEN_CHUNK_ROWS == 512
    assert_raises_match(ValueError, "chunk-rows", opf._check_chunk_contract, 64)
    assert opf._check_chunk_contract(512) == 512
    assert_raises_match(ValueError, "tag-bits", opf._check_tag_bits, 32)
    assert opf._check_tag_bits(64) == 64
    parser = opf.build_parser()
    required = {a.dest for a in parser._actions if a.required}
    assert required == {"counts", "source", "floor", "target_f", "n",
                        "train_seeds", "dev_seeds", "train_blocks_per_stream",
                        "dev_blocks_per_stream", "chunk_rows", "tag_bits",
                        "out_dir"}
    proc = subprocess.run(
        [sys.executable, "-m",
         "comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13",
         "--counts", "x"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 2


def test_scalar_only_outputs_carry_no_secret_material():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run_with_fakes(out)
        banned = {
            "bob", "high", "low", "high_true", "low_true", "u1_true", "u2_true",
            "a_full", "counts", "logp", "decision_metrics", "high_hat",
            "low_hat", "label_hat", "label_bits", "seed_bits", "rng_state",
            "p_b", "f_full", "labels_true",
        }

        def walk(node, keys):
            if isinstance(node, dict):
                for key, value in node.items():
                    keys.add(key)
                    walk(value, keys)
            elif isinstance(node, list):
                for value in node:
                    walk(value, keys)

        keys: set = set()
        walk(json.loads((out / "frozen_plan.json").read_text()), keys)
        walk(json.loads((out / "construction_and_allocation.json").read_text()), keys)
        walk(json.loads((out / "aggregate_summary.json").read_text()), keys)
        for line in (out / "per_block_outcomes.jsonl").read_text().splitlines():
            walk(json.loads(line), keys)
        assert not (keys & banned), keys & banned


def test_no_forbidden_access_rule():
    text = Path(opf.__file__).read_text(encoding="utf-8")
    # Functional-use tokens: the scope prose may name forbidden paths, but
    # the module must never call or import them. There is exactly one
    # operational arm here: no second decision arm, no retry arm, no
    # surrogate-order construction anywhere in this gate.
    for token in ("analytic_order", "allocate_layer_ks", "adaptive", "Adaptive",
                  "fwht", "FWHT", "rescue", "Rescue", "load_v31",
                  "parquet", "TTBin", "ttbin", "HOLD_", "EVAL_",
                  "bec", "BEC", "Bec"):
        assert token not in text, token
    assert not hasattr(opf, "analytic_order")
    assert not hasattr(opf, "allocate_layer_ks")
    # The accepted seams this gate is built on.
    for token in ("load_v25_channel_counts", "block_genie_risks",
                  "select_empirical_split", "budget_k_total",
                  "target_preconditions", "sc_decode", "toeplitz_tag",
                  "wilson_lower_bound", "seed_bits_for",
                  "run_operational_block", "classify_operational_outcome",
                  "operational_seed_bits"):
        assert token in text, token
