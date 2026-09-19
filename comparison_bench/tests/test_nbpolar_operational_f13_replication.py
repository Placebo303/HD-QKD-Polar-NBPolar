"""Focused Phase 4-P17 N=32768 operational-replication tests.

Injected tiny/synthetic tables and arrays plus temporary roots only. No V25
NPZ content open, no Model-F/raw/held-out/real/EVAL artifact, no production
invocation and no output outside a temporary directory. Focused tests use
their own fresh seeds 2026091790..2026091799 and never the frozen P17
streams 2026092030..2026092037, never the P16 streams 2026092000..2003 /
2026092010..2017, nor any official prior or probe seed.

The accepted P16 construction file is never touched here (not even read):
predecessor-identity tests fabricate construction files with the same
canonical digest recipe plus tamper variants. The frozen N=32768 makes real
sampling/SC calls too slow for runner tests, so runner tests patch the two
documented seams (``sample_full_block`` and the accepted P16
``run_operational_block``) with deterministic fakes; tables, transform,
orders, Wilson, gates, accounting and checkpointing all run for real. The
real operational arm is exercised separately at tiny n with real SC and the
real P17-domain tag. Every ``test_*`` takes no arguments, uses plain
asserts and restores any monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13 as opf,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13_replication as opr,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; the frozen P17 streams (2030..2037) and every P16,
# prior and probe seed below are never used as inputs.
TEST_DEVS = (
    2026091790, 2026091791, 2026091792, 2026091793,
    2026091794, 2026091795, 2026091796, 2026091797,
)
TEST_SPARES = (2026091798, 2026091799)

FROZEN_K_TOTAL = 6811
FROZEN_LEAKAGE = 34119  # 5 * 6811 + 64
FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63


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


def injected_counts(seed: int = 2026091790) -> np.ndarray:
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


def fab_digest(cell: dict) -> str:
    payload = {
        "n": int(cell["n"]),
        "k_total": int(cell["k_total"]),
        "k1": int(cell["k1"]),
        "k2": int(cell["k2"]),
        "l1_order": [int(v) for v in cell["l1_order"]],
        "l2_order": [int(v) for v in cell["l2_order"]],
        "pooled_e1_mean": [float(v) for v in cell["pooled_e1_mean"]],
        "pooled_h1_mean": [float(v) for v in cell["pooled_h1_mean"]],
        "pooled_e2_mean": [float(v) for v in cell["pooled_e2_mean"]],
        "pooled_h2_mean": [float(v) for v in cell["pooled_h2_mean"]],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def make_construction_file(directory, *, k1=319, k2=6492, tamper=None):
    """Fabricate a canonical-shape predecessor file (never the real P16 root)."""
    directory = Path(directory)
    n = 32768
    rng = np.random.default_rng(2026091799)
    l1 = rng.permutation(n).tolist()
    l2 = rng.permutation(n).tolist()
    zeros = [0.0] * n
    cell = {
        "n": n,
        "k_total": 6811,
        "k_total_raw": 6811.78,
        "k1": k1,
        "k2": k2,
        "l1_order": l1,
        "l2_order": l2,
        "pooled_e1_mean": list(zeros),
        "pooled_h1_mean": list(zeros),
        "pooled_e2_mean": list(zeros),
        "pooled_h2_mean": list(zeros),
        "train_seeds": [2026092000, 2026092001, 2026092002, 2026092003],
        "dev_seeds": [2026092010 + i for i in range(8)],
    }
    clean_hex = fab_digest(cell)
    if tamper == "k1":
        cell["k1"] = 320
    elif tamper == "k2":
        cell["k2"] = 6491
    elif tamper == "order-swap":
        # Still a permutation, but the stored digest no longer matches.
        cell["l1_order"][0], cell["l1_order"][1] = cell["l1_order"][1], cell["l1_order"][0]
    elif tamper == "order-dup":
        cell["l2_order"][0] = cell["l2_order"][1]
    elif tamper == "n":
        cell["n"] = 16384
    # NOTE: the stored digest below always describes the untampered cell, so
    # every tamper above breaks the stored-vs-recomputed identity check.
    stored_hex = clean_hex
    if tamper == "digest":
        stored_hex = ("0" if clean_hex[0] != "0" else "1") + clean_hex[1:]
    cell["freeze_sha256"] = stored_hex
    doc = {
        "protocol": "nbpolar-p17-tampered" if tamper == "protocol"
        else "nbpolar-p16-operational-f13-gate",
        "frozen_before_first_dev": True,
        "cell": cell,
    }
    if tamper == "stored-digest":
        doc["cell"]["freeze_sha256"] = (
            ("0" if clean_hex[0] != "0" else "1") + clean_hex[1:]
        )
    path = directory / "construction_and_allocation.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path, clean_hex


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
        self.script = list(script) if script else ["exact"] * 128
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


def full_run(out, script=None, **over):
    fab_dir = Path(out).parent / "fab"
    fab_dir.mkdir(parents=True, exist_ok=True)
    fab_path, fab_hex = make_construction_file(fab_dir)
    kw = dict(
        dev_seeds=list(TEST_DEVS),
        dev_blocks_per_stream=16,
        construction=str(fab_path),
        construction_digest=fab_hex,
        out_dir=out,
    )
    kw.update(over)
    counts = kw.pop("counts", None)
    if counts is None:
        counts = injected_counts()
    seam = kw.pop("expected_entropies", None)
    if seam is None:
        seam = expected_seam(counts)
    arm = FakeArm(script)
    with patched(opr, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
        with patched(opr, "sample_full_block", fake_sample):
            with patched(opr, "run_operational_block", arm):
                run = opr.run_operational_replication(
                    counts=counts, expected_entropies=seam, **kw
                )
    return run, arm


# ---- frozen constants and fresh streams ----

def test_frozen_constants_pinned():
    assert opr.FROZEN_N == 32768 == opf.FROZEN_N
    assert opr.FROZEN_K1 == 319
    assert opr.FROZEN_K2 == 6492
    assert opr.FROZEN_K_TOTAL == FROZEN_K_TOTAL == 6811
    assert opr.FROZEN_K1 + opr.FROZEN_K2 == FROZEN_K_TOTAL
    assert opr.FROZEN_LEAKAGE_BITS == FROZEN_LEAKAGE == 5 * FROZEN_K_TOTAL + 64
    assert opr.FROZEN_DEV_SEEDS == tuple(2026092030 + i for i in range(8))
    assert opr.FROZEN_DEV_BLOCKS_PER_STREAM == 16
    assert opr.FROZEN_DEV_TOTAL == 128
    assert opr.PLANNED_SC_CALLS_MAX == 256
    assert opr.PLANNED_TAG_INVOCATIONS == 128
    assert opr.FROZEN_CHUNK_ROWS == 512
    assert opr.FROZEN_TAG_BITS == 64
    assert opr.PUBLIC_TAG_MASTER_OFFSET == 10000
    assert opr.PUBLIC_CONTROL_BITS_PER_TAG == FROZEN_PUBLIC_BITS
    assert opr.EXPECTED_NPZ_BYTES == 25166822 == opf.EXPECTED_NPZ_BYTES
    assert opr.OUTCOMES == opf.OUTCOMES == ("exact", "undetected", "verify_failed",
                                           "decode_failed", "nonfinite", "resource_abort")
    # The frozen construction digest is pinned to the accepted P16 value.
    assert opr.FROZEN_CONSTRUCTION_DIGEST == (
        "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
    )
    # K arithmetic from the ratified literals, far from any integer boundary.
    for h in (opf.EXPECTED_H1 + opf.EXPECTED_H2, opf.EXPECTED_TOTAL):
        raw = (1.3 * opr.FROZEN_N * h - 64.0) / 5.0
        assert math.floor(raw) == FROZEN_K_TOTAL, (repr(h), repr(raw))
    assert FROZEN_LEAKAGE <= 1.3 * opr.FROZEN_N * (opf.EXPECTED_H1 + opf.EXPECTED_H2)


def test_fresh_streams_disjoint_from_p16_and_priors():
    assert set(opr.FROZEN_DEV_SEEDS).isdisjoint(opf.FROZEN_TRAIN_SEEDS + opf.FROZEN_DEV_SEEDS)
    assert set(opr.FROZEN_DEV_SEEDS).isdisjoint(opr.P16_PRIOR_STREAMS)
    assert set(opr.P16_PRIOR_STREAMS) == set(opf.FROZEN_TRAIN_SEEDS + opf.FROZEN_DEV_SEEDS)
    assert set(TEST_DEVS).isdisjoint(opr.FROZEN_DEV_SEEDS)
    assert set(TEST_DEVS).isdisjoint(opr.P16_PRIOR_STREAMS)
    assert set(TEST_DEVS).isdisjoint(TEST_SPARES)
    assert 2026091760 not in TEST_DEVS + TEST_SPARES  # X11 probe seed
    for prior in (2026091650, 2026091680, 2026091710, 2026091820, 2026091860,
                  2026091930, 2026091940, 2026091960, 2026091970, 2026091980,
                  2026091990, 2026091800, 2026091811, 2026091753):
        assert prior not in TEST_DEVS + TEST_SPARES
        assert prior not in opr.FROZEN_DEV_SEEDS


def test_p16_helpers_shared_not_reimplemented():
    assert opr.run_operational_block is opf.run_operational_block
    assert opr.classify_operational_outcome is opf.classify_operational_outcome
    assert not hasattr(opr, "block_genie_risks")
    assert not hasattr(opr, "select_empirical_split")
    assert not hasattr(opr, "budget_k_total")


# ---- predecessor identity ----

def test_predecessor_identity_accepts_valid_fabricated_file():
    with tempfile.TemporaryDirectory() as tmp:
        fab_path, fab_hex = make_construction_file(tmp)
        verified = opr.verify_predecessor_construction(fab_path, expected_digest=fab_hex)
        record = verified["record"]
        assert record["digest_match"] is True
        assert record["digest_recomputed"] == fab_hex
        assert (record["n"], record["k_total"], record["k1"], record["k2"]) == (32768, 6811, 319, 6492)
        assert record["leakage_bits"] == FROZEN_LEAKAGE
        assert record["f"] <= 1.3
        assert len(verified["l1_order"]) == 32768
        assert len(verified["l2_order"]) == 32768
        assert sorted(verified["l1_order"]) == list(range(32768))
        assert sorted(verified["l2_order"]) == list(range(32768))


def test_predecessor_identity_tamper_refusals_zero_execution():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on refusal")

    cases = ("k1", "k2", "order-swap", "order-dup", "n", "digest",
             "stored-digest", "protocol")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for idx, tamper in enumerate(cases):
            sub = tmp_path / f"fab{idx}"
            sub.mkdir()
            fab_path, fab_hex = make_construction_file(sub, tamper=tamper)
            assert_raises_match(
                ValueError, "predecessor construction identity",
                opr.verify_predecessor_construction, fab_path, expected_digest=fab_hex,
            )
            root = tmp_path / f"out{idx}"
            with patched(opr, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(opr, "load_v25_channel_counts", forbidden_loader):
                    with patched(opr, "run_operational_block", forbidden_arm):
                        assert_raises_match(
                            ValueError, "predecessor construction identity",
                            opr.run_operational_replication,
                            counts=injected_counts(), dev_seeds=list(TEST_DEVS),
                            construction=str(fab_path), construction_digest=fab_hex,
                            out_dir=root,
                        )
            assert not root.exists()
        # Wrong digest flag against a valid file also refuses.
        sub = tmp_path / "fabflag"
        sub.mkdir()
        fab_path, fab_hex = make_construction_file(sub)
        bad_flag = ("0" if fab_hex[0] != "0" else "1") + fab_hex[1:]
        assert_raises_match(
            ValueError, "predecessor construction identity",
            opr.verify_predecessor_construction, fab_path, expected_digest=bad_flag,
        )
        # Missing file refuses before any attempt.
        assert_raises_match(
            FileNotFoundError, "not found",
            opr.verify_predecessor_construction,
            str(tmp_path / "absent.json"), expected_digest=fab_hex,
        )


# ---- tag domain separation ----

def test_frozen_digest_flag_pin_at_run_level():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        # Internally consistent file, but the flag is not the frozen digest:
        # run refuses before any root exists (no constant patch here).
        assert_raises_match(
            ValueError, "digest flag != frozen digest",
            opr.run_operational_replication,
            counts=injected_counts(), dev_seeds=list(TEST_DEVS),
            construction=str(fab_path), construction_digest=fab_hex,
            out_dir=tmp_path / "out",
        )
        assert not (tmp_path / "out").exists()


def test_seed_prefix_differs_from_p16():
    assert opr.SEED_PREFIX == "nbpolar-p17-operational-replication-seed"
    assert opr.SEED_PREFIX != opf.SEED_PREFIX
    a = opr.replication_seed_bits(2026091790 + 10000, 8, 3)
    assert len(a) == 143
    assert np.array_equal(a, opr.replication_seed_bits(2026091790 + 10000, 8, 3))
    assert not np.array_equal(a, opr.replication_seed_bits(2026091790 + 10000, 8, 4))
    # Same master/n/block under the P16 domain yields different bits.
    b = opf.operational_seed_bits(2026091790 + 10000, 8, 3)
    assert len(b) == len(a)
    assert not np.array_equal(a, b)


def tiny_inputs(n=8, seed=2026091790):
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


def test_p16_operational_parity_and_p17_tag_domain():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        seed_bits_for,
    )
    from comparison_bench.src.comparison_bench.formal_ir.shared import (
        toeplitz_tag as real_tag,
    )

    n = 8
    data = tiny_inputs(n)
    master = 2026091790 + 10000
    gidx = 5
    p17_seed = opr.replication_seed_bits(master, n, gidx, bit_length=seed_bits_for(n))
    seen = []

    def spy_tag(bits, seed, tag_bits):
        seen.append(np.array(seed, copy=True))
        return real_tag(bits, seed, tag_bits)

    def p17_closure(bits, _seed, tag_bits, _fixed=p17_seed):
        return spy_tag(bits, _fixed, tag_bits)

    kw = dict(
        n=n, stream_seed=2026091790, block_index=1,
        bob=data["bob"], high_true=data["high"], low_true=data["low"],
        u1_true=data["u1"], u2_true=data["u2"],
        labels_true=data["labels"], labels_true_bits=data["bits"],
        field=data["field"], p1_table=data["p1"], p2_table=data["p2"],
        l1_order=np.arange(n), l2_order=np.arange(n),
        k1=n, k2=n, master=master,
    )
    with patched(opr, "toeplitz_tag", spy_tag):
        result_p17 = opr.run_operational_block(tag_fn=p17_closure, **kw)
    # The scored tag used exactly the P17-domain seed (true tag + hat tag).
    assert len(seen) == 2
    assert np.array_equal(seen[0], p17_seed)
    assert np.array_equal(seen[1], p17_seed)
    assert not np.array_equal(seen[0], opf.operational_seed_bits(master, n, gidx))
    assert result_p17.outcome == "exact"
    assert result_p17.key_dependent_bits == 5 * (n + n) + 64
    assert result_p17.public_control_bits == seed_bits_for(n)
    assert result_p17.truth_leak_violation is False
    # Same injected block through the default P16-domain tag: same outcome.
    result_default = opf.run_operational_block(**kw)
    assert result_default.outcome == result_p17.outcome == "exact"


# ---- outcome buckets and precedence ----

def test_outcome_classifier_every_bucket_and_precedence():
    c = opr.classify_operational_outcome
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
    assert c(l1_failed=True, l2_failed=False, nonfinite=True,
             tag_pass=False, label_match=False) == "nonfinite"
    assert c(l1_failed=False, l2_failed=True, nonfinite=True,
             tag_pass=False, label_match=False) == "nonfinite"
    abort = opf._abort_block(2026091790, 3, k1=319, k2=6492)
    assert abort.outcome == "resource_abort"
    assert abort.exact is False
    assert abort.key_dependent_bits == 0 and abort.public_control_bits == 0


# ---- Wilson boundary and labels ----

def test_wilson_121_120_boundary_literals_and_recovery_gates():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.protocol import (
        WILSON_Z,
        wilson_lower_bound,
    )

    lb121 = wilson_lower_bound(121, 128, z=WILSON_Z)
    lb120 = wilson_lower_bound(120, 128, z=WILSON_Z)
    assert round(lb121, 10) == opr.WILSON_LB_121_OF_128 == 0.9021084760
    assert round(lb120, 10) == opr.WILSON_LB_120_OF_128 == 0.8924595822
    assert lb121 >= 0.90 and lb120 < 0.90
    assert opr.check_wilson_boundary() == {"lb_121_of_128": lb121, "lb_120_of_128": lb120}
    good = opr.recovery_gates(121)
    assert good["pass"] is True
    assert good["exact_at_least_121_of_128"] is True
    assert good["wilson_lower_bound_at_least_0p90"] is True
    assert opr.recovery_gates(128)["pass"] is True
    bad120 = opr.recovery_gates(120)
    assert bad120["pass"] is False
    assert bad120["exact_at_least_121_of_128"] is False
    assert bad120["wilson_lower_bound_at_least_0p90"] is False
    # Structural non-pooling: the P16 62/64 context can never satisfy the
    # P17 count gate, whatever its Wilson value.
    p16_shaped = opr.recovery_gates(62, 64)
    assert p16_shaped["exact_at_least_121_of_128"] is False
    assert p16_shaped["pass"] is False
    assert_raises_match(ValueError, "must not exceed", opr.recovery_gates, 129)


def test_select_label_three_branches():
    good = {g: True for g in opr.INTEGRITY_GATE_ORDER}
    assert opr.select_label(good, True) == opr.CANDIDATE_LABEL
    assert opr.select_label(good, False) == opr.NOT_CONFIRMED_LABEL
    bad = dict(good)
    bad["undetected_zero"] = False
    assert opr.select_label(bad, True) == "BLOCKED(undetected_zero)"
    bad2 = dict(good)
    bad2["predecessor_construction_identity"] = False
    bad2["undetected_zero"] = False
    assert opr.select_label(bad2, True) == "BLOCKED(predecessor_construction_identity)"


# ---- full runner with fakes ----

def test_full_run_128_exact_gates_and_accounting():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, arm = full_run(out)
        assert sorted(p.name for p in out.iterdir()) == sorted(opr.OUTPUT_FILES)
        identity = run.construction["identity"]
        assert identity["digest_match"] is True
        assert (identity["k1"], identity["k2"]) == (319, 6492)
        # Exact call accounting: the fake arm's two SC attempts per block.
        assert run.summary["sc_calls"] == 256 == opr.PLANNED_SC_CALLS_MAX
        assert run.summary["tag_invocations"] == 128
        assert run.summary["integrity"]["no_unregistered_calls"] is True
        # Injected path: zero reads/attempts, exact accounting.
        assert run.summary["input_mode"] == "injected_counts"
        acc = run.summary["attempt_read_accounting"]
        assert acc["artifact_content_reads_consumed_by_this_run"] == 0
        assert acc["attempts_consumed_by_this_run"] == 0
        assert acc["open_count"] == 0
        assert opr._NPZ_CONTENT_OPENED is False
        # DEV: 128 exact records with full-disclosure accounting.
        lines = (out / "per_block_outcomes.jsonl").read_text().splitlines()
        assert len(lines) == 128
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
                              "k1", "k2", "l1_exact", "hard_l2_exact",
                              "oracle_l2_exact", "pair_exact",
                              "wall_s", "resources"}
        assert set(first["resources"]) == {"wall_s", "rss_bytes_hwm",
                                           "vm_peak_kb", "vm_size_kb"}
        for record in records:
            assert record["key_dependent_bits"] == FROZEN_LEAKAGE
            assert record["public_control_bits"] == FROZEN_PUBLIC_BITS
            assert record["error"] is None
        assert run.summary["outcome_counts"] == {
            "exact": 128, "undetected": 0, "verify_failed": 0,
            "decode_failed": 0, "nonfinite": 0, "resource_abort": 0,
        }
        assert run.summary["exact_count"] == 128
        assert run.summary["recovery"]["total"] == 128
        assert run.summary["recovery"]["pass"] is True
        # Tag masters are exactly DEV seed + 10000 per stream.
        assert arm.masters == {s: s + 10000 for s in TEST_DEVS}
        # Transcript recount is exact over all disclosure/tag/public events.
        disclosure = run.summary["disclosure"]
        assert disclosure["mismatches"] == []
        assert disclosure["key_dependent_bits"] == 128 * FROZEN_LEAKAGE
        assert disclosure["public_control_bits"] == 128 * FROZEN_PUBLIC_BITS
        assert disclosure["tag_invocations"] == 128
        assert disclosure["recount"] == {
            "key_dependent_bits": disclosure["key_dependent_bits"],
            "public_control_bits": disclosure["public_control_bits"],
            "tag_invocations": 128,
            "event_types": {"l1_disclosure": 128, "l2_disclosure": 128,
                            "verification_tag": 128},
        }
        # P17 transcript events carry the replication domain, never P16's.
        assert run.events[0]["method"] == "nbpolar_operational_f13_replication"
        assert run.events[0]["frame_key"].startswith("nbpolar-p17-operational-replication:")
        assert "-replication-" in run.events[0]["event_id"]
        # Test-local seeds are not the frozen matrix: the shape gates fail
        # while every other mechanical gate holds.
        integrity = run.summary["integrity"]
        assert integrity["predecessor_construction_identity"] is True
        assert integrity["target_population_contract"] is True
        assert integrity["construction_frozen_before_dev"] is True
        assert integrity["dev_coverage_complete"] is False
        assert integrity["streams_disjoint_frozen"] is False
        assert integrity["orders_valid_k_replay_f_within_budget"] is True
        assert integrity["buckets_disjoint_exhaustive"] is True
        assert integrity["truth_isolation"] is True
        assert integrity["undetected_zero"] is True
        assert integrity["nonfinite_zero"] is True
        assert integrity["disclosure_recount_exact"] is True
        assert integrity["attempt_read_accounting_exact"] is True
        assert integrity["resource_limits_met_and_no_abort"] is True
        assert run.summary["outcome_label"] == "BLOCKED(dev_coverage_complete)"


def test_p16_numbers_never_enter_decision():
    script = ["exact"] * 121 + ["verify_failed"] * 7
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _ = full_run(out, script)
        assert run.summary["exact_count"] == 121
        assert run.summary["dev_block_count"] == 128
        recovery = run.summary["recovery"]
        assert recovery["total"] == 128
        assert recovery["exact_count"] == 121
        assert recovery["pass"] is True
        report_only = run.summary["predecessor_report_only"]
        assert report_only == {"p16_exact": 62, "p16_total": 64,
                               "p16_wilson_lb": 0.9098711859,
                               "pooled_into_decision": False}
        # The 62/64 context appears in the report discussion only, never in
        # any gate input: every integrity/recovery scalar derives from 128.
        text = (out / "report.md").read_text()
        assert "62/64" in text
        assert "never pooled" in text or "zero weight" in text


def test_undetected_and_nonfinite_buckets_block_gates():
    script = ["exact"] * 126 + ["undetected", "nonfinite"]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _ = full_run(out, script)
        assert run.summary["outcome_counts"]["undetected"] == 1
        assert run.summary["outcome_counts"]["nonfinite"] == 1
        assert run.summary["outcome_counts"]["exact"] == 126
        assert run.summary["integrity"]["undetected_zero"] is False
        assert run.summary["integrity"]["nonfinite_zero"] is False
        lines = (out / "per_block_outcomes.jsonl").read_text().splitlines()
        by_outcome = {}
        for line in lines:
            record = json.loads(line)
            by_outcome.setdefault(record["outcome"], []).append(record)
        # Undetected is never success: exact is False on that record.
        assert by_outcome["undetected"][0]["exact"] is False
        assert by_outcome["undetected"][0]["tag_pass"] is True
        assert by_outcome["nonfinite"][0]["nonfinite"] is True


def test_partial_decode_failure_counts_disclosed_bits_only():
    script = ["exact"] * 124 + ["decode_failed"] * 4
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _ = full_run(out, script)
        lines = (out / "per_block_outcomes.jsonl").read_text().splitlines()
        records = [json.loads(line) for line in lines]
        failed = [r for r in records if r["outcome"] == "decode_failed"]
        assert len(failed) == 4
        for record in failed:
            assert record["key_dependent_bits"] == 5 * 319
            assert record["public_control_bits"] == 0
            assert record["tag_invoked"] is False
        disclosure = run.summary["disclosure"]
        assert disclosure["mismatches"] == []
        assert disclosure["tag_invocations"] == 124
        assert disclosure["recount"]["event_types"] == {
            "l1_disclosure": 128, "l2_disclosure": 124, "verification_tag": 124,
        }
        assert run.summary["integrity"]["disclosure_recount_exact"] is True


def test_recount_tamper_detected():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _ = full_run(out)
        events = run.events
        assert len(events) == 128 * 3
        recount = opr.replication_recount_events(events)
        tampered = [dict(e) for e in events]
        tampered[0] = dict(tampered[0])
        tampered[0]["key_dependent_bits"] += 1
        recount2 = opr.replication_recount_events(tampered)
        assert recount2["key_dependent_bits"] != recount["key_dependent_bits"]
        incremental = {"key_dependent_bits": recount["key_dependent_bits"],
                       "public_control_bits": recount["public_control_bits"],
                       "tag_invocations": recount["tag_invocations"]}
        assert opf._transcript_mismatches(incremental, recount) == []
        assert opf._transcript_mismatches(incremental, recount2) != []
        assert_raises_match(ValueError, "not N/arm-tagged", opr.replication_recount_events,
                            [{"event_id": "bogus", "event_type": "l1_disclosure",
                              "key_dependent_bits": 0, "public_control_bits": 0}])
        assert_raises_match(ValueError, "not frozen", opr.replication_recount_events,
                            [dict(events[0], event_type="bogus_type")])


# ---- refusals, accounting, failure paths ----

def _refusal_run_kwargs(tmp_path):
    fab_dir = tmp_path / "fab"
    fab_dir.mkdir(parents=True, exist_ok=True)
    fab_path, fab_hex = make_construction_file(fab_dir)
    return fab_path, fab_hex


def test_grouping_and_contract_refusals_before_open():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = _refusal_run_kwargs(tmp_path)

        def base_kwargs(**over):
            kw = dict(
                counts=injected_counts(),
                dev_seeds=list(TEST_DEVS),
                construction=str(fab_path),
                construction_digest=fab_hex,
            )
            kw.update(over)
            return kw

        with patched(opr, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(opr, "load_v25_channel_counts", forbidden_loader):
                with patched(opr, "run_operational_block", forbidden_arm):
                    assert_raises_match(
                        ValueError, "exactly 8 streams",
                        opr.run_operational_replication,
                        **base_kwargs(dev_seeds=list(TEST_DEVS)[:7],
                                     out_dir=tmp_path / "a"),
                    )
                    assert_raises_match(
                        ValueError, "must avoid every P16 stream",
                        opr.run_operational_replication,
                        **base_kwargs(dev_seeds=[2026092010] + list(TEST_DEVS)[:7],
                                     out_dir=tmp_path / "b"),
                    )
                    assert_raises_match(
                        ValueError, "distinct",
                        opr.run_operational_replication,
                        **base_kwargs(dev_seeds=[TEST_DEVS[0]] * 8,
                                     out_dir=tmp_path / "c"),
                    )
                    assert_raises_match(
                        ValueError, "dev-blocks-per-stream",
                        opr.run_operational_replication,
                        **base_kwargs(dev_blocks_per_stream=8, out_dir=tmp_path / "d"),
                    )
                    assert_raises_match(
                        ValueError, "chunk-rows",
                        opr.run_operational_replication,
                        **base_kwargs(chunk_rows=64, out_dir=tmp_path / "e"),
                    )
                    assert_raises_match(
                        ValueError, "tag-bits",
                        opr.run_operational_replication,
                        **base_kwargs(tag_bits=32, out_dir=tmp_path / "f"),
                    )
                    assert_raises_match(
                        ValueError, "n=32768",
                        opr.run_operational_replication,
                        **base_kwargs(n=16384, out_dir=tmp_path / "g"),
                    )
                    assert_raises_match(
                        ValueError, "k1=319",
                        opr.run_operational_replication,
                        **base_kwargs(k1=320, out_dir=tmp_path / "h"),
                    )
                    assert_raises_match(
                        ValueError, "k2=6492",
                        opr.run_operational_replication,
                        **base_kwargs(k2=6491, out_dir=tmp_path / "i"),
                    )
                    assert_raises_match(
                        ValueError, "floor",
                        opr.run_operational_replication,
                        **base_kwargs(floor=1e-12, out_dir=tmp_path / "j"),
                    )
                    assert_raises_match(
                        ValueError, "source",
                        opr.run_operational_replication,
                        **base_kwargs(source="2M", out_dir=tmp_path / "k"),
                    )
                    assert_raises_match(
                        FileNotFoundError, "not found",
                        opr.run_operational_replication,
                        **base_kwargs(construction=str(tmp_path / "absent.json"),
                                     out_dir=tmp_path / "l"),
                    )
        for name in ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"):
            assert not (tmp_path / name).exists()


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
        with patched(opr, "load_v25_channel_counts", forbidden_loader):
            with patched(opr, "run_operational_block", forbidden_arm):
                assert_raises_match(
                    FileExistsError, "refusing to overwrite",
                    opr.run_operational_replication,
                    counts=injected_counts(), dev_seeds=list(TEST_DEVS),
                    construction=str(Path(tmp) / "absent.json"),
                    construction_digest="x", out_dir=root,
                )
        assert sentinel.read_text(encoding="utf-8") == "untouched"
        assert sorted(p.name for p in root.iterdir()) == ["sentinel.txt"]


def test_single_open_guard_refuses_reopen():
    with tempfile.TemporaryDirectory() as tmp:
        fab_path, fab_hex = make_construction_file(Path(tmp))
        saved = opr._NPZ_CONTENT_OPENED
        opr._NPZ_CONTENT_OPENED = True
        try:
            with patched(opr, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                # NPZ-mode call while the single open is consumed: reopen
                # refused without touching the filesystem counts path.
                assert_raises_match(
                    ValueError, "reopen refused",
                    opr.run_operational_replication,
                    counts_path="/nonexistent/channel_counts.npz",
                    dev_seeds=list(TEST_DEVS),
                    construction=str(fab_path), construction_digest=fab_hex,
                    out_dir=Path(tmp) / "out",
                )
        finally:
            opr._NPZ_CONTENT_OPENED = saved
        assert opr._NPZ_CONTENT_OPENED is False


def test_precondition_failure_zero_calls_and_blocked_stubs():
    seen = {"sc": 0}

    def boom_arm(**kwargs):
        seen["sc"] += 1
        raise AssertionError("no SC call may happen before the contract passes")

    counts = injected_counts()
    counts[:, 0] = 0.0  # zero Bob column breaks the target contract
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        fab_path, fab_hex = make_construction_file(Path(tmp))
        with patched(opr, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(opr, "sample_full_block", fake_sample):
                with patched(opr, "run_operational_block", boom_arm):
                    assert_raises_match(
                        opr.TargetPopulationContractError,
                        "BLOCKED(target_population_contract)",
                        opr.run_operational_replication, counts=counts,
                        expected_entropies=(opf.EXPECTED_H1, opf.EXPECTED_H2,
                                            opf.EXPECTED_H1 + opf.EXPECTED_H2),
                        dev_seeds=list(TEST_DEVS),
                        construction=str(fab_path), construction_digest=fab_hex,
                        out_dir=root,
                    )
        assert seen == {"sc": 0}
        assert sorted(p.name for p in root.iterdir()) == sorted(opr.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(target_population_contract)"
        assert blocked["attempt_read_accounting"]["attempts_consumed_by_this_run"] == 0


def test_memory_error_classification_path():
    def oom(**kwargs):
        raise MemoryError("injected exhaustion")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        fab_path, fab_hex = make_construction_file(Path(tmp))
        with patched(opr, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(opr, "sample_full_block", fake_sample):
                with patched(opr, "run_operational_block", oom):
                    assert_raises_match(
                        opr.ReplicationResourceError,
                        "BLOCKED(resource_limits_met_and_no_abort)",
                        opr.run_operational_replication,
                        counts=injected_counts(),
                        expected_entropies=expected_seam(injected_counts()),
                        dev_seeds=list(TEST_DEVS),
                        construction=str(fab_path), construction_digest=fab_hex,
                        out_dir=root,
                    )
        assert sorted(p.name for p in root.iterdir()) == sorted(opr.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"
        assert opr._NPZ_CONTENT_OPENED is False


def test_budget_stop_abort_fill_preserves_checkpoints():
    arm = FakeArm()
    calls = {"n": 0}
    real_guard = opf._budget_exceeded

    def flaky(start, cap):
        calls["n"] += 1
        if calls["n"] > 2:  # two DEV blocks, then stop
            return "wall_s"
        return real_guard(start, cap)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        fab_path, fab_hex = make_construction_file(Path(tmp))
        with patched(opr, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(opr, "sample_full_block", fake_sample):
                with patched(opr, "run_operational_block", arm):
                    with patched(opf, "_budget_exceeded", flaky):
                        counts = injected_counts()
                        run = opr.run_operational_replication(
                            counts=counts, expected_entropies=expected_seam(counts),
                            dev_seeds=list(TEST_DEVS),
                            construction=str(fab_path), construction_digest=fab_hex,
                            out_dir=root,
                        )
        assert sorted(p.name for p in root.iterdir()) == sorted(opr.OUTPUT_FILES)
        lines = (root / "per_block_outcomes.jsonl").read_text().splitlines()
        assert len(lines) == 128
        records = [json.loads(line) for line in lines]
        aborts = [r for r in records if r["outcome"] == "resource_abort"]
        assert len(aborts) == 126
        assert run.summary["outcome_counts"]["exact"] == 2
        assert run.summary["resource_stop_fired"] is True
        assert run.summary["resource_stop_reason"] == "wall_s"
        assert run.summary["integrity"]["resource_limits_met_and_no_abort"] is False
        assert run.summary["outcome_label"].startswith("BLOCKED(")


def test_chunk_contract_and_cli_parse_refusals():
    import subprocess

    assert opr.FROZEN_CHUNK_ROWS == 512
    assert_raises_match(ValueError, "chunk-rows", opf._check_chunk_contract, 64)
    assert opf._check_chunk_contract(512) == 512
    assert_raises_match(ValueError, "tag-bits", opr._check_tag_bits, 32)
    assert opr._check_tag_bits(64) == 64
    parser = opr.build_parser()
    required = {a.dest for a in parser._actions if a.required}
    assert required == {"counts", "source", "floor", "n", "k1", "k2",
                        "construction", "construction_digest",
                        "dev_seeds", "dev_blocks_per_stream",
                        "chunk_rows", "tag_bits", "out_dir"}
    proc = subprocess.run(
        [sys.executable, "-m",
         "comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13_replication",
         "--counts", "x"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 2


def test_scalar_only_outputs_carry_no_secret_material():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        full_run(out)
        banned = {
            "bob", "high", "low", "high_true", "low_true", "u1_true", "u2_true",
            "a_full", "counts", "logp", "decision_metrics", "high_hat",
            "low_hat", "label_hat", "label_bits", "seed_bits", "rng_state",
            "p_b", "f_full", "labels_true", "l1_order", "l2_order",
            "pooled_e1_mean", "pooled_h1_mean", "pooled_e2_mean", "pooled_h2_mean",
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
        walk(json.loads((out / "predecessor_construction_identity.json").read_text()), keys)
        walk(json.loads((out / "aggregate_summary.json").read_text()), keys)
        for line in (out / "per_block_outcomes.jsonl").read_text().splitlines():
            walk(json.loads(line), keys)
        assert not (keys & banned), keys & banned


def test_no_forbidden_access_rule():
    text = Path(opr.__file__).read_text(encoding="utf-8")
    # Functional-use tokens: the scope prose may name frozen inputs, but the
    # module must never call or import them. This runner holds no
    # construction path of any kind: no second decision arm, no retry arm,
    # no surrogate-order path anywhere in this gate.
    for token in ("block_genie_risks", "select_empirical_split", "budget_k_total",
                  "genie", "Genie", "GENIE", "train", "Train", "TRAIN",
                  "adaptive", "Adaptive", "ADAPTIVE", "fwht", "FWHT",
                  "rescue", "Rescue", "analytic_order", "allocate_layer_ks",
                  "load_v31", "parquet", "TTBin", "ttbin", "HOLD_", "EVAL_",
                  "oracle", "Oracle", "ORACLE", "bec", "BEC", "Bec"):
        assert token not in text, token
    assert not hasattr(opr, "block_genie_risks")
    assert not hasattr(opr, "select_empirical_split")
    # The accepted seams this replication is built on.
    for token in ("load_v25_channel_counts", "target_preconditions",
                  "sample_full_block", "run_operational_block",
                  "classify_operational_outcome", "wilson_lower_bound",
                  "seed_bits_for", "toeplitz_tag", "canonical_event",
                  "polar_transform", "make_gf32", "labels_to_bits",
                  "replication_seed_bits", "verify_predecessor_construction",
                  "replication_block_events", "replication_recount_events",
                  "recovery_gates", "select_label"):
        assert token in text, token
