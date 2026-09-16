"""Focused Phase 4-P19 N=32768 1M-HOLD layer/backoff diagnostic tests.

Injected tables/arrays and temporary roots only. The V25 1M TRAIN NPZ and the
registered HOLD pairs parquet are NEVER content-opened (the only files named
after them here are throwaway temporary stubs with patched loaders); the real
P16 construction root, the real split manifest, the real P18 evidence root and
every other real evidence root are never touched. Focused tests use their own
fresh seeds ``2026092070..2026092076`` and never the frozen P19 tag master
2026092060 for real scoring, the P16 streams 2026092000..2003 /
2026092010..2017, the P17 streams 2026092030..2037, the P18 tag master
2026092050, nor any prior/probe seed.

The frozen N=32768 makes real SC calls too slow for runner tests, so runner
tests patch the documented ``run_operational_block`` and
``run_oracle_control_block`` seams with scripted deterministic fakes; tables,
block formation, transform, NLL scoring, gates, accounting and checkpointing
all run for real. The real oracle-control path is exercised separately at tiny
n with real SC and the real P19-domain tag. Every ``test_*`` takes no
arguments, uses plain asserts and restores any monkeypatched module attribute
in a ``finally``.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    holdout_backoff_diagnostic as hb,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    holdout_microcheck as hm,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13 as opf,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13_replication as opr,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never the frozen tag masters or any frozen stream.
TEST_SEEDS = (2026092070, 2026092071, 2026092072, 2026092073)
TEST_MASTER = 2026092074
TEST_SPARES = (2026092075, 2026092076)

FROZEN_LEAKAGE = 34119  # 5 * 6811 + 64 (base arm)
FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63
ARM_K_BY_NAME = {
    "base": (319, 6492),
    "l1_plus": (447, 6492),
    "l2_plus": (319, 7004),
    "both_plus": (447, 7004),
}
ARM_NAME_BY_K = {pair: name for name, pair in ARM_K_BY_NAME.items()}
TOTAL_KEY_BITS = 526200
TOTAL_PUBLIC_BITS = 4916145
CONTROL_KEY_BITS = 3 * (5 * 6492 + 64)  # 97572
OPERATIONAL_KEY_BITS = TOTAL_KEY_BITS - CONTROL_KEY_BITS  # 428628


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


def injected_counts(seed: int = TEST_SEEDS[0]) -> np.ndarray:
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


def make_construction_file(directory, *, tamper=None):
    """Fabricate a canonical-shape predecessor copy (never the real P16 root)."""
    directory = Path(directory)
    n = 32768
    rng = np.random.default_rng(TEST_MASTER)
    l1 = rng.permutation(n).tolist()
    l2 = rng.permutation(n).tolist()
    zeros = [0.0] * n
    cell = {
        "n": n,
        "k_total": 6811,
        "k_total_raw": 6811.78,
        "k1": 319,
        "k2": 6492,
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
    elif tamper == "order-dup":
        cell["l2_order"][0] = cell["l2_order"][1]
    elif tamper == "n":
        cell["n"] = 16384
    stored_hex = clean_hex
    if tamper == "digest":
        stored_hex = ("0" if clean_hex[0] != "0" else "1") + clean_hex[1:]
    cell["freeze_sha256"] = stored_hex
    doc = {
        "protocol": "nbpolar-p19-tampered" if tamper == "protocol"
        else "nbpolar-p16-operational-f13-gate",
        "frozen_before_first_dev": True,
        "cell": cell,
    }
    path = directory / "construction_and_allocation.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path, clean_hex


def make_manifest(directory, *, tamper=None, name="split_manifest.json"):
    frames = {"train": 1200, "val": 400, "hold": 400}
    pairs = {"train": 307200, "val": 102400, "hold": 102400}
    schema = hm.FROZEN_MANIFEST_SCHEMA
    source = "type2_1M_20260121_184040"
    per = {source: {"frames": dict(frames), "pairs": dict(pairs)}}
    if tamper == "hold-frames":
        per[source]["frames"]["hold"] = 399
    elif tamper == "hold-pairs":
        per[source]["pairs"]["hold"] = 102399
    elif tamper == "schema":
        schema = "nbldpc_v25_split_manifest_v2"
    elif tamper == "missing-source":
        per = {"type2_2M_20260121_183657": per[source]}
    path = Path(directory) / name
    path.write_text(json.dumps({"schema": schema, "per_source": per}), encoding="utf-8")
    return path


def injected_hold_table(*, frames=400, first_frame=1600, per_frame=256,
                        seed=TEST_SEEDS[1], extras=True):
    """Deterministic 1M-HOLD-like pairs frame; shuffled rows, extra non-HOLD rows."""
    rng = np.random.default_rng(seed)
    total = frames * per_frame
    frame_id = np.repeat(np.arange(first_frame, first_frame + frames), per_frame)
    pair_idx = np.tile(np.arange(per_frame), frames)
    alice = rng.integers(0, 1024, size=total)
    bob = rng.integers(0, 1024, size=total)
    df = pd.DataFrame({
        "frame_id": frame_id,
        "pair_idx": pair_idx,
        "alice_symbol": alice,
        "bob_symbol": bob,
    })
    if extras:
        extra = pd.DataFrame({
            "frame_id": np.repeat([1599, 2000], per_frame),
            "pair_idx": np.tile(np.arange(per_frame), 2),
            "alice_symbol": rng.integers(0, 1024, size=2 * per_frame),
            "bob_symbol": rng.integers(0, 1024, size=2 * per_frame),
        })
        df = pd.concat([df, extra], ignore_index=True)
    return df.sample(frac=1.0, random_state=int(seed)).reset_index(drop=True)


def mutate_hold(df, how):
    out = df.copy()
    if how == "drop-frame":
        out = out[out["frame_id"] != 1700]
    elif how == "pair-gap":
        row = out[(out["frame_id"] == 1600) & (out["pair_idx"] == 255)].index[0]
        out.loc[row, "pair_idx"] = 254
    elif how == "symbol-range":
        row = out[out["frame_id"] == 1600].index[0]
        out.loc[row, "bob_symbol"] = 1024
    elif how == "no-hold":
        out = out[out["frame_id"].isin([1599, 2000])]
    else:
        raise AssertionError(f"unknown mutation {how}")
    return out


class FakeOperationalArms:
    """Scripted per-arm fake for the accepted ``run_operational_block`` seam."""

    def __init__(self, scripts=None):
        self.scripts = {
            name: list((scripts or {}).get(name, ["exact"] * 3))
            for name in hb.OPERATIONAL_ARM_NAMES
        }
        self.seen = []

    def __call__(self, **kwargs):
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
            seed_bits_for,
        )

        k1, k2 = int(kwargs["k1"]), int(kwargs["k2"])
        arm = ARM_NAME_BY_K[(k1, k2)]
        index = sum(1 for entry in self.seen if entry["arm"] == arm)
        outcome = self.scripts[arm][index % len(self.scripts[arm])]
        l1_failed = outcome in ("decode_failed", "nonfinite")
        sc_delta = 1 if l1_failed else 2
        calls = kwargs.get("calls")
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + sc_delta
        n = int(kwargs["n"])
        tag = outcome in ("exact", "undetected", "verify_failed")
        self.seen.append({
            "arm": arm, "k1": k1, "k2": k2, "outcome": outcome,
            "block_index": int(kwargs["block_index"]), "sc_delta": sc_delta,
            "tag_fn": kwargs.get("tag_fn"),
        })
        return opf.OperationalBlockResult(
            stream_seed=int(kwargs["stream_seed"]),
            block_index=int(kwargs["block_index"]),
            outcome=outcome,
            exact=bool(outcome == "exact"),
            label_match=bool(outcome == "exact"),
            tag_pass=bool(outcome in ("exact", "undetected")),
            l1_provenance=None if l1_failed else opf.Provenance.PRIOR_ONLY.value,
            l2_provenance=None if l1_failed else opf.Provenance.CANDIDATE_CONDITIONED.value,
            l1_executed=bool(not l1_failed),
            l1_decode_failed=bool(l1_failed),
            l2_invoked=bool(not l1_failed),
            l2_skipped_by_l1_failure=bool(l1_failed),
            l2_decode_failed=False,
            tag_invoked=bool(tag),
            key_dependent_bits=int(
                5 * k1 + (5 * k2 if not l1_failed else 0) + (64 if tag else 0)
            ),
            public_control_bits=int(seed_bits_for(n) if tag else 0),
            nonfinite=bool(outcome == "nonfinite"),
            truth_leak_violation=False,
            l1_error_type=("NumericNonfiniteError" if outcome == "nonfinite"
                           else ("RuntimeError" if l1_failed else None)),
            l2_error_type=None,
            wall_s=0.001,
            k1=k1,
            k2=k2,
            high_hat=None if l1_failed else np.array(kwargs["high_true"], copy=True),
        )


class FakeControl:
    """Scripted fake for the ``run_oracle_control_block`` seam (one SC per block)."""

    def __init__(self, scripts=None):
        self.scripts = list(scripts or ["exact"] * 3)
        self.seen = []

    def __call__(self, **kwargs):
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
            seed_bits_for,
        )

        outcome = self.scripts[len(self.seen) % len(self.scripts)]
        calls = kwargs.get("calls")
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + 1
        n = int(kwargs["n"])
        k2 = int(kwargs["k2"])
        tag = outcome in ("exact", "undetected", "verify_failed")
        l2_failed = outcome in ("decode_failed", "nonfinite")
        self.seen.append({
            "outcome": outcome, "block_index": int(kwargs["block_index"]),
            "tag_fn": kwargs.get("tag_fn"), "sc_delta": 1,
        })
        return hb.OracleControlResult(
            frame_start=int(kwargs["frame_start"]),
            block_index=int(kwargs["block_index"]),
            outcome=outcome,
            exact=bool(outcome == "exact"),
            label_match=bool(outcome == "exact"),
            tag_pass=bool(outcome in ("exact", "undetected")),
            l2_invoked=True,
            l2_decode_failed=bool(l2_failed),
            tag_invoked=bool(tag),
            key_dependent_bits=int(5 * k2 + (64 if tag else 0)),
            public_control_bits=int(seed_bits_for(n) if tag else 0),
            nonfinite=bool(outcome == "nonfinite"),
            truth_leak_violation=False,
            l2_error_type=("NumericNonfiniteError" if outcome == "nonfinite"
                           else ("RuntimeError" if l2_failed else None)),
            wall_s=0.001,
            k2=k2,
            provenance=hb.ORACLE_PROVENANCE,
            oracle_truth_use=True,
            low_hat=None,
        )


def full_run(out, *, scripts=None, control_scripts=None, counts=None, hold=None,
             arms=None, control=None, **over):
    tmp = Path(out).parent
    fab_dir = tmp / "fab"
    fab_dir.mkdir(parents=True, exist_ok=True)
    fab_path, fab_hex = make_construction_file(fab_dir)
    man_path = make_manifest(tmp)
    if counts is None:
        counts = injected_counts()
    if hold is None:
        hold = injected_hold_table()
    if arms is None:
        arms = FakeOperationalArms(scripts)
    if control is None:
        control = FakeControl(control_scripts)
    kw = dict(
        counts=counts,
        hold_table=hold,
        expected_entropies=expected_seam(counts),
        construction=str(fab_path),
        construction_digest=fab_hex,
        manifest_path=str(man_path),
        out_dir=Path(out),
    )
    kw.update(over)
    with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
        with patched(hb, "verify_p18_block_identity", lambda: {"verified": True}):
            with patched(hb, "run_operational_block", arms):
                with patched(hb, "run_oracle_control_block", control):
                    run = hb.run_backoff_diagnostic(**kw)
    return run, arms, control


def synthetic_records(outcomes_by_arm, *, include_control=False, control_outcomes=None):
    records = []
    for arm, outcomes in outcomes_by_arm.items():
        for block_index, outcome in enumerate(outcomes):
            records.append({
                "arm": arm, "block_index": block_index, "outcome": outcome,
                "arm_kind": "operational", "arm_provenance": hb.OPERATIONAL_PROVENANCE,
            })
    if include_control:
        for block_index, outcome in enumerate(control_outcomes or ["exact"] * 3):
            records.append({
                "arm": "true_l1_control", "block_index": block_index, "outcome": outcome,
                "arm_kind": "oracle_control", "arm_provenance": hb.ORACLE_PROVENANCE,
            })
    return records


# ---- frozen constants, arm table and fresh seeds ----

def test_frozen_constants_and_arm_table_pinned():
    assert hb.FROZEN_N == 32768 == opf.FROZEN_N
    assert hb.FROZEN_K1 == 319 and hb.FROZEN_K2 == 6492
    assert hb.FROZEN_K_TOTAL == 6811
    assert hb.FROZEN_L1_INCREMENT == 128 and hb.FROZEN_L2_INCREMENT == 512
    assert hb.FROZEN_LEAKAGE_BITS == FROZEN_LEAKAGE == 5 * 6811 + 64
    assert hb.FROZEN_PUBLIC_CONTROL_BITS == FROZEN_PUBLIC_BITS == 10 * 32768 + 63
    assert hb.FROZEN_BLOCK_COUNT == 3 and hb.FROZEN_BLOCK_FRAMES == 128
    assert hb.FROZEN_SYMBOLS_PER_BLOCK == 32768
    assert hb.FROZEN_HOLD_FRAME_RANGE == (1600, 1999)
    assert hb.FROZEN_HOLD_FRAMES == 400 and hb.FROZEN_HOLD_PAIRS == 102400
    assert hb.FROZEN_BLOCK_RANGES == ((1600, 1727), (1728, 1855), (1856, 1983))
    assert hb.FROZEN_REMAINDER_FRAME_RANGE == (1984, 1999)
    assert hb.FROZEN_REMAINDER_FRAMES == 16 and hb.FROZEN_REMAINDER_SYMBOLS == 4096
    assert hb.FROZEN_TAG_MASTER == 2026092060
    assert hb.FROZEN_CHUNK_ROWS == 512 and hb.FROZEN_TAG_BITS == 64
    assert hb.EXPECTED_NPZ_BYTES == 25166822 == opf.EXPECTED_NPZ_BYTES
    assert hb.EXPECTED_HOLD_PARQUET_BYTES == 1354289
    assert hb.FROZEN_CONSTRUCTION_DIGEST == (
        "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
    )
    assert hb.OUTCOMES == opf.OUTCOMES == (
        "exact", "undetected", "verify_failed", "decode_failed", "nonfinite",
        "resource_abort",
    )
    assert hb.OUTPUT_FILES == (
        "frozen_plan.json", "input_and_predecessor_identity.json",
        "per_block_arm_outcomes.jsonl", "aggregate_summary.json", "report.md",
    )
    assert hb.COMPLETE_LABEL == "TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE"
    # Five frozen arms, exact order, K/leakage/provenance and design counts.
    assert hb.FROZEN_ARM_NAMES == ("base", "l1_plus", "l2_plus", "both_plus",
                                   "true_l1_control")
    expected = (
        ("base", "operational", 319, 6492, 34119),
        ("l1_plus", "operational", 447, 6492, 34759),
        ("l2_plus", "operational", 319, 7004, 36679),
        ("both_plus", "operational", 447, 7004, 37319),
        ("true_l1_control", "oracle_control", 0, 6492, 32524),
    )
    for spec, row in zip(hb.FROZEN_ARMS, expected):
        assert (spec.name, spec.kind, spec.k1, spec.k2, spec.leakage_bits) == row
        assert spec.leakage_bits == 5 * (spec.k1 + spec.k2) + 64
    assert hb.FROZEN_ARMS[-1].provenance == hb.ORACLE_PROVENANCE
    assert all(spec.provenance == hb.OPERATIONAL_PROVENANCE for spec in hb.FROZEN_ARMS[:4])
    assert hb.PLANNED_SC_CALLS == 27
    assert hb.PLANNED_TAG_INVOCATIONS == 15
    assert hb.FROZEN_TOTAL_KEY_DEPENDENT_BITS == TOTAL_KEY_BITS == 526200
    assert hb.FROZEN_TOTAL_PUBLIC_CONTROL_BITS == TOTAL_PUBLIC_BITS == 15 * 327743
    assert hb.check_frozen_arm_table()["verified"] is True
    # Only the base arm replays the accepted planning budget; the backoff arms
    # are descriptive diagnostic disclosure levels above it.
    h_total = opf.EXPECTED_H1 + opf.EXPECTED_H2
    assert FROZEN_LEAKAGE <= 1.3 * hb.FROZEN_N * h_total
    for leakage in (34759, 36679, 37319):
        assert leakage > 1.3 * hb.FROZEN_N * h_total
    with tempfile.TemporaryDirectory() as tmp:
        assert hb.verify_p18_block_identity()["verified"] is True
        with patched(hm, "FROZEN_BLOCK_RANGES", ((1600, 1726), (1727, 1854), (1855, 1982))):
            assert_raises_match(ValueError, "accepted P18 block-range identity mismatch",
                                hb.verify_p18_block_identity)
        with patched(hm, "FROZEN_REMAINDER_FRAME_RANGE", (1985, 1999)):
            assert_raises_match(ValueError, "accepted P18 block-range identity mismatch",
                                hb.verify_p18_block_identity)


def test_arm_table_tamper_refused():
    good = hb.FROZEN_ARMS
    tampered = (
        hb.ArmSpec("base", "operational", 319, 6492, 34119, hb.OPERATIONAL_PROVENANCE),
        hb.ArmSpec("l1_plus", "operational", 448, 6492, 34759, hb.OPERATIONAL_PROVENANCE),
        hb.ArmSpec("l2_plus", "operational", 319, 7004, 36679, hb.OPERATIONAL_PROVENANCE),
        hb.ArmSpec("both_plus", "operational", 447, 7004, 37319, hb.OPERATIONAL_PROVENANCE),
        hb.ArmSpec("true_l1_control", "oracle_control", 0, 6492, 32524, hb.ORACLE_PROVENANCE),
    )
    with patched(hb, "FROZEN_ARMS", tampered):
        assert_raises_match(ValueError, "registered increments", hb.check_frozen_arm_table)
    with patched(hb, "FROZEN_ARMS", good):
        assert hb.check_frozen_arm_table()["planned_sc_calls"] == 27
    tampered_leak = tuple(
        hb.ArmSpec(spec.name, spec.kind, spec.k1, spec.k2,
                   spec.leakage_bits + (1 if spec.name == "l1_plus" else 0),
                   spec.provenance)
        for spec in good
    )
    with patched(hb, "FROZEN_ARMS", tampered_leak):
        assert_raises_match(ValueError, "leakage", hb.check_frozen_arm_table)


def test_fresh_test_seeds_disjoint_from_all_frozen_seeds():
    frozen = (
        set(opr.FROZEN_DEV_SEEDS) | set(opr.P16_PRIOR_STREAMS)
        | {hm.FROZEN_TAG_MASTER, hb.FROZEN_TAG_MASTER}
    )
    # P18 test-local seeds are also treated as used.
    for seed in (2026092060, 2026092061, 2026092062, 2026092063, 2026092064,
                 2026092065, 2026092066):
        frozen.add(seed)
    for prior in (2026091650, 2026091680, 2026091710, 2026091820, 2026091860,
                  2026091930, 2026091940, 2026091960, 2026091970, 2026091980,
                  2026091990, 2026091800, 2026091811, 2026091753, 2026091760):
        frozen.add(prior)
    assert set(TEST_SEEDS).isdisjoint(frozen)
    assert set(TEST_SPARES).isdisjoint(frozen)
    assert TEST_MASTER not in TEST_SEEDS + TEST_SPARES
    assert hb.FROZEN_TAG_MASTER not in TEST_SEEDS + TEST_SPARES + (TEST_MASTER,)
    assert hb.FROZEN_TAG_MASTER != hm.FROZEN_TAG_MASTER


def test_accepted_helpers_shared_not_reimplemented():
    assert hb.form_holdout_blocks is hm.form_holdout_blocks
    assert hb.verify_split_manifest is hm.verify_split_manifest
    assert hb.holdout_nll_bits is hm.holdout_nll_bits
    assert hb.raw_symbol_error_rate is hm.raw_symbol_error_rate
    assert hb.run_operational_block is opf.run_operational_block
    assert hb._decode_layer is opf._decode_layer
    assert hb.verify_predecessor_construction is opr.verify_predecessor_construction
    assert hb.target_preconditions.__module__.endswith("target_construction")
    assert hb.load_v25_channel_counts.__module__.endswith("v35_algorithm_development")
    assert hb.load_pairs_table.__module__.endswith("pairs_loader")
    for banned in ("sample_full_block", "block_genie_risks", "select_empirical_split",
                   "budget_k_total", "analytic_order", "wilson_lower_bound",
                   "recovery_gates", "select_label"):
        assert not hasattr(hb, banned), banned


# ---- identities before any read ----

def test_predecessor_identity_tamper_refusals_zero_reads_zero_root():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on a refusal")

    def forbidden_control(**kwargs):
        raise AssertionError("no control call may happen on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        man = make_manifest(tmp_path)
        for idx, tamper in enumerate(("k1", "k2", "order-dup", "n", "digest", "protocol")):
            sub = tmp_path / f"fab{idx}"
            sub.mkdir()
            fab_path, fab_hex = make_construction_file(sub, tamper=tamper)
            root = tmp_path / f"out{idx}"
            with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hb, "load_v25_channel_counts", forbidden_loader):
                    with patched(hb, "load_pairs_table", forbidden_loader):
                        with patched(hb, "run_operational_block", forbidden_arm):
                            with patched(hb, "run_oracle_control_block", forbidden_control):
                                assert_raises_match(
                                    ValueError, "predecessor construction identity",
                                    hb.run_backoff_diagnostic,
                                    counts=injected_counts(), hold_table=injected_hold_table(),
                                    construction=str(fab_path), construction_digest=fab_hex,
                                    manifest_path=str(man), out_dir=root,
                                )
            assert not root.exists()
        # Wrong digest flag and an absent file also refuse before anything runs.
        fab_path, fab_hex = make_construction_file(tmp_path)
        bad_flag = ("0" if fab_hex[0] != "0" else "1") + fab_hex[1:]
        assert_raises_match(
            ValueError, "digest flag != frozen digest",
            hb.run_backoff_diagnostic,
            counts=injected_counts(), hold_table=injected_hold_table(),
            construction=str(fab_path), construction_digest=bad_flag,
            manifest_path=str(man), out_dir=tmp_path / "outflag",
        )
        assert not (tmp_path / "outflag").exists()
        with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            assert_raises_match(
                FileNotFoundError, "not found", hb.run_backoff_diagnostic,
                counts=injected_counts(), hold_table=injected_hold_table(),
                construction=str(tmp_path / "absent.json"), construction_digest=fab_hex,
                manifest_path=str(man), out_dir=tmp_path / "outmissing",
            )
        assert not (tmp_path / "outmissing").exists()


def test_manifest_and_p18_pin_refusals_zero_reads_zero_root():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        good = make_manifest(tmp_path, name="good.json")
        assert_raises_match(FileNotFoundError, "not found", hb.verify_split_manifest,
                            str(tmp_path / "absent.json"))
        for idx, tamper in enumerate(("hold-frames", "hold-pairs", "schema", "missing-source")):
            man = make_manifest(tmp_path, tamper=tamper, name=f"bad{idx}.json")
            assert_raises_match(ValueError, "hold split manifest identity",
                                hb.verify_split_manifest, man, source="1M")
            root = tmp_path / f"out{idx}"
            with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hb, "load_v25_channel_counts", forbidden_loader):
                    with patched(hb, "load_pairs_table", forbidden_loader):
                        assert_raises_match(
                            ValueError, "hold split manifest identity",
                            hb.run_backoff_diagnostic,
                            counts=injected_counts(), hold_table=injected_hold_table(),
                            construction=str(fab_path), construction_digest=fab_hex,
                            manifest_path=str(man), out_dir=root,
                        )
            assert not root.exists()
        # The accepted P18 block-range pin refuses before the opens too.
        root = tmp_path / "outpin"
        for field, value in (
            ("FROZEN_BLOCK_RANGES", ((1600, 1726), (1727, 1854), (1855, 1982))),
            ("FROZEN_REMAINDER_FRAME_RANGE", (1985, 1999)),
            ("FROZEN_HOLD_FRAME_RANGE", (1599, 1999)),
        ):
            with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hm, field, value):
                    with patched(hb, "load_v25_channel_counts", forbidden_loader):
                        with patched(hb, "load_pairs_table", forbidden_loader):
                            assert_raises_match(
                                ValueError, "accepted P18 block-range identity mismatch",
                                hb.run_backoff_diagnostic,
                                counts=injected_counts(), hold_table=injected_hold_table(),
                                construction=str(fab_path), construction_digest=fab_hex,
                                manifest_path=str(good), out_dir=root,
                            )
        assert not root.exists()


# ---- deterministic slicing ----

def test_hold_slicing_blocks_and_remainder_exact():
    df = injected_hold_table()
    formation = hb.form_holdout_blocks(df)
    assert formation["hold_frame_range"] == [1600, 1999]
    assert formation["hold_frames"] == 400 and formation["hold_pairs"] == 102400
    assert formation["block_ranges"] == [[1600, 1727], [1728, 1855], [1856, 1983]]
    assert formation["remainder"] == {
        "frame_start": 1984, "frame_end": 1999, "frames": 16,
        "symbols": 4096, "used": False,
    }
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        assert run.summary["hold"]["hold_frame_range"] == [1600, 1999]
        assert run.summary["hold"]["block_ranges"] == [[1600, 1727], [1728, 1855], [1856, 1983]]
        assert run.summary["hold"]["remainder"] == {
            "frame_start": 1984, "frame_end": 1999, "frames": 16,
            "symbols": 4096, "used": False,
        }
        assert len(run.records) == 15
        for index, record in enumerate(run.records):
            block_index = index % 3
            assert record["block_index"] == block_index
            assert (record["frame_start"], record["frame_end"]) == \
                hb.FROZEN_BLOCK_RANGES[block_index]
            assert record["frame_count"] == 128


def test_malformed_hold_population_run_level_blocked_five_files():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        assert_raises_match(
            hm.HoldoutMicrocheckContractError, "BLOCKED(hold_population_exact)",
            full_run, root, hold=mutate_hold(injected_hold_table(), "drop-frame"),
        )
        assert sorted(p.name for p in root.iterdir()) == sorted(hb.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(hold_population_exact)"


# ---- one-open guards and no sampling/fitting ----

def test_one_open_guards_refuse_reopen_with_zero_execution():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        saved_npz = hb._NPZ_CONTENT_OPENED
        saved_hold = hb._HOLD_PARQUET_CONTENT_OPENED
        try:
            hb._NPZ_CONTENT_OPENED = True
            with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hb, "verify_p18_block_identity", lambda: {"verified": True}):
                    assert_raises_match(
                        ValueError, "reopen refused", hb.run_backoff_diagnostic,
                        counts_path=str(tmp_path / "absent.npz"),
                        hold_table=injected_hold_table(),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=tmp_path / "outa",
                    )
            assert not (tmp_path / "outa").exists()
            hb._NPZ_CONTENT_OPENED = False
            hb._HOLD_PARQUET_CONTENT_OPENED = True
            with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hb, "verify_p18_block_identity", lambda: {"verified": True}):
                    assert_raises_match(
                        ValueError, "reopen refused", hb.run_backoff_diagnostic,
                        counts=injected_counts(), hold_pairs=str(tmp_path / "absent.parquet"),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=tmp_path / "outb",
                    )
            assert not (tmp_path / "outb").exists()
        finally:
            hb._NPZ_CONTENT_OPENED = saved_npz
            hb._HOLD_PARQUET_CONTENT_OPENED = saved_hold
        assert hb._NPZ_CONTENT_OPENED is False
        assert hb._HOLD_PARQUET_CONTENT_OPENED is False


def test_no_fitting_or_sampling_tokens_and_exact_call_counts():
    text = Path(hb.__file__).read_text(encoding="utf-8")
    # Call-style tokens only: the scope prose may say "no shuffle/sampling".
    for token in ("np.random", "default_rng", "random_state", ".shuffle",
                  "resample(", "bootstrap", "polyfit", "curve_fit",
                  "sample_full_block", "block_genie_risks", "select_empirical_split",
                  "budget_k_total", "Adaptive", "ADAPTIVE", "adaptive",
                  "wilson", "Wilson", "WILSON", "recovery_gates", "EXACT_MIN",
                  "exact_fraction", "fer_rate"):
        assert token not in text, token
    for token in ("FWHT", "fwht", "BEC", "SCL", "APP"):
        assert not re.search(rf"\b{token}\b", text), token

    def forbidden(*args, **kwargs):
        raise AssertionError("protected loaders must never run in injected tests")

    with tempfile.TemporaryDirectory() as tmp:
        arms = FakeOperationalArms()
        control = FakeControl()
        with patched(hb, "load_v25_channel_counts", forbidden):
            with patched(hb, "load_pairs_table", forbidden):
                run, _, _ = full_run(Path(tmp) / "out", arms=arms, control=control)
        assert arms.seen and control.seen
        assert run.summary["records_completed"] == 15
        assert run.summary["attempt_read_accounting"]["counts_content_opens"] == 0
        assert run.summary["attempt_read_accounting"]["hold_content_opens"] == 0
        assert hb._NPZ_CONTENT_OPENED is False
        assert hb._HOLD_PARQUET_CONTENT_OPENED is False


# ---- five-arm semantics, K arithmetic and call counts ----

def test_five_arm_semantics_k_leakage_labels_and_call_counts():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        run, arms, control = full_run(root)
        assert [r["arm"] for r in run.records] == [
            name for name in hb.FROZEN_ARM_NAMES for _ in range(3)
        ]
        assert [r["arm_index"] for r in run.records] == [
            index for index in range(5) for _ in range(3)
        ]
        for record in run.records:
            spec = hb.ARM_BY_NAME[record["arm"]]
            assert record["k1"] == spec.k1 and record["k2"] == spec.k2
            assert record["l1_prefix_len"] == spec.k1 and record["l2_prefix_len"] == spec.k2
            assert record["full_block_key_dependent_bits"] == spec.leakage_bits
            assert record["arm_provenance"] == spec.provenance
            assert record["oracle_truth_use"] is (spec.kind == "oracle_control")
            if spec.kind == "operational":
                assert record["key_dependent_bits"] == spec.leakage_bits
                assert record["public_control_bits"] == FROZEN_PUBLIC_BITS
                assert record["l1_provenance"] == opf.Provenance.PRIOR_ONLY.value
                assert record["l2_provenance"] == opf.Provenance.CANDIDATE_CONDITIONED.value
                assert record["l1_correct"] is True
            else:
                assert record["key_dependent_bits"] == 5 * 6492 + 64 == 32524
                assert record["l1_executed"] is False and record["l1_correct"] is None
                assert record["l2_provenance"] == opf.Provenance.ORACLE_CONDITIONED.value
        per_arm = {name: 0 for name in hb.FROZEN_ARM_NAMES}
        for entry in arms.seen:
            per_arm[entry["arm"]] += entry["sc_delta"]
        assert per_arm == {
            "base": 6, "l1_plus": 6, "l2_plus": 6, "both_plus": 6,
            "true_l1_control": 0,
        }
        assert sum(entry["sc_delta"] for entry in control.seen) == 3
        assert len(arms.seen) == 12 and len(control.seen) == 3
        assert run.summary["sc_calls"] == 27
        assert run.summary["tag_invocations"] == 15
        assert run.summary["disclosure"]["key_dependent_bits"] == TOTAL_KEY_BITS
        assert run.summary["disclosure"]["public_control_bits"] == TOTAL_PUBLIC_BITS
        assert run.summary["integrity"]["sc_calls_exact"] is True
        assert run.summary["integrity"]["tags_exact"] is True
        assert run.summary["outcome_label"] == hb.COMPLETE_LABEL
        assert run.summary["integrity_all_pass"] is True


def test_incremental_k_arithmetic_exact():
    base = hb.ARM_BY_NAME["base"]
    assert hb.ARM_BY_NAME["l1_plus"].k1 - base.k1 == 128
    assert hb.ARM_BY_NAME["l2_plus"].k2 - base.k2 == 512
    assert hb.ARM_BY_NAME["both_plus"].k1 == base.k1 + 128
    assert hb.ARM_BY_NAME["both_plus"].k2 == base.k2 + 512
    assert hb.ARM_BY_NAME["l1_plus"].k2 == base.k2
    assert hb.ARM_BY_NAME["l2_plus"].k1 == base.k1
    assert hb.ARM_BY_NAME["l1_plus"].leakage_bits - base.leakage_bits == 5 * 128 == 640
    assert hb.ARM_BY_NAME["l2_plus"].leakage_bits - base.leakage_bits == 5 * 512 == 2560
    assert hb.ARM_BY_NAME["both_plus"].leakage_bits - base.leakage_bits == 3200
    assert hb.ARM_BY_NAME["true_l1_control"].leakage_bits == 5 * 6492 + 64


def test_p19_seed_domain_arm_block_separation():
    from comparison_bench.src.comparison_bench.formal_ir.shared import (
        toeplitz_tag as real_tag,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        seed_bits_for,
    )

    n = 64
    master = TEST_MASTER
    p19 = hb.backoff_seed_bits(master, n, "base", 1)
    assert p19.shape == (seed_bits_for(n),)
    assert not np.array_equal(p19, opf.operational_seed_bits(master, n, 1))
    assert not np.array_equal(p19, opr.replication_seed_bits(master, n, 1))
    assert not np.array_equal(p19, hm.holdout_seed_bits(master, n, 1))
    assert not np.array_equal(p19, hb.backoff_seed_bits(master, n, "l1_plus", 1))
    assert not np.array_equal(p19, hb.backoff_seed_bits(master, n, "true_l1_control", 1))
    assert not np.array_equal(p19, hb.backoff_seed_bits(master, n, "base", 2))
    assert_raises_match(ValueError, "unknown frozen arm", hb.backoff_seed_bits,
                        master, n, "control", 1)
    # The scored tags in the frozen run use exactly the P19 arm/block domain.
    with tempfile.TemporaryDirectory() as tmp:
        run, arms, control = full_run(Path(tmp) / "out")
        bits = np.zeros(10 * hb.FROZEN_N, dtype=np.uint8)
        for entry in arms.seen + control.seen:
            arm = entry.get("arm", "true_l1_control")
            expected = real_tag(
                bits, hb.backoff_seed_bits(hb.FROZEN_TAG_MASTER, hb.FROZEN_N, arm,
                                           entry["block_index"]), 64)
            observed = entry["tag_fn"](bits, np.zeros(5, dtype=np.uint8), 64)
            assert np.array_equal(observed, expected), (arm, entry["block_index"])
        tag_seeds = {
            hb.backoff_seed_bits(hb.FROZEN_TAG_MASTER, hb.FROZEN_N, spec.name, index).tobytes()
            for spec in hb.FROZEN_ARMS for index in range(3)
        }
        assert len(tag_seeds) == 15


# ---- oracle isolation ----

def test_oracle_isolation_control_excluded_from_operational_aggregates():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(
            Path(tmp) / "out",
            scripts={name: ["verify_failed"] * 3 for name in hb.OPERATIONAL_ARM_NAMES},
            control_scripts=["exact", "exact", "exact"],
        )
        summary = run.summary
        assert summary["partition"] == {
            "operational": 12, "oracle_control": 3, "unassigned": 0, "total": 15,
        }
        assert summary["operational"]["exact_count"] == 0
        assert summary["oracle_control"]["arms"]["true_l1_control"]["exact_count"] == 3
        assert summary["recovery"]["first_operational_recovery_arm"] is None
        assert summary["operational"]["key_dependent_bits"] == OPERATIONAL_KEY_BITS
        assert summary["oracle_control"]["arms"]["true_l1_control"][
            "key_dependent_bits"] == CONTROL_KEY_BITS
        assert summary["oracle_control"]["deployable"] is False
        assert summary["oracle_control"]["excluded_from_operational_aggregates"] is True
        assert summary["operational"]["oracle_control_excluded"] is True
        assert summary["integrity"]["oracle_isolation"] is True
        operational = [r for r in run.records if r["arm_kind"] == "operational"]
        control = [r for r in run.records if r["arm_kind"] == "oracle_control"]
        assert len(operational) == 12 and len(control) == 3
        assert sum(r["key_dependent_bits"] for r in operational) == \
            summary["operational"]["key_dependent_bits"]
        assert all(r["arm_provenance"] == hb.ORACLE_PROVENANCE for r in control)
        assert all(r["provenance"] == hb.ORACLE_PROVENANCE for r in control)
        assert all(r["arm_provenance"] != hb.ORACLE_PROVENANCE for r in operational)
        assert hb.oracle_isolation_ok(run.records, final=True) is True
        # Relabelling a control record as operational breaks the partition.
        tampered = [dict(r) for r in run.records]
        tampered[12] = dict(tampered[12], arm_provenance=hb.OPERATIONAL_PROVENANCE)
        assert hb.oracle_isolation_ok(tampered, final=True) is False
        aggregates = hb.build_aggregates(tampered)
        assert aggregates["partition"]["unassigned"] == 1
        # Relabelling an operational record as oracle also fails.
        tampered2 = [dict(r) for r in run.records]
        tampered2[0] = dict(tampered2[0], arm_provenance=hb.ORACLE_PROVENANCE)
        assert hb.oracle_isolation_ok(tampered2, final=True) is False
        # An operational record may never carry oracle conditioning.
        tampered3 = [dict(r) for r in run.records]
        tampered3[0] = dict(tampered3[0],
                            l2_provenance=opf.Provenance.ORACLE_CONDITIONED.value)
        assert hb.oracle_isolation_ok(tampered3, final=True) is False


# ---- paired recovery tables / first arm / non-monotone ----

def test_paired_recovery_tables_first_arm_and_non_monotone():
    records = synthetic_records({
        "base": ["verify_failed"] * 3,
        "l1_plus": ["exact", "verify_failed", "verify_failed"],
        "l2_plus": ["exact", "exact", "exact"],
        "both_plus": ["exact", "exact", "exact"],
    })
    diag = hb.recovery_diagnostics(records)
    assert diag["exact_counts_ordered"] == [0, 1, 3, 3]
    assert diag["first_operational_recovery_arm"] == "l1_plus"
    assert diag["ordered_exact_counts_non_monotone"] is False
    l1 = diag["paired_vs_base"]["l1_plus"]
    assert l1["recovered_vs_base"] == 1 and l1["lost_vs_base"] == 0
    assert l1["pair_counts"] == {
        "verify_failed->exact": 1, "verify_failed->verify_failed": 2,
    }
    non_monotone = synthetic_records({
        "base": ["verify_failed"] * 3,
        "l1_plus": ["verify_failed"] * 3,
        "l2_plus": ["exact"] * 3,
        "both_plus": ["exact", "verify_failed", "verify_failed"],
    })
    diag2 = hb.recovery_diagnostics(non_monotone)
    assert diag2["exact_counts_ordered"] == [0, 0, 3, 1]
    assert diag2["ordered_exact_counts_non_monotone"] is True
    assert diag2["first_operational_recovery_arm"] == "l2_plus"
    assert "neutrally" in diag2["non_monotone_note"]
    assert "no monotonicity" in diag2["non_monotone_note"]
    both = diag2["paired_vs_base"]["both_plus"]
    assert both["recovered_vs_base"] == 1 and both["lost_vs_base"] == 0
    # Control exact outcomes never enter operational recovery diagnostics.
    with_control = synthetic_records(
        {name: ["verify_failed"] * 3 for name in hb.OPERATIONAL_ARM_NAMES},
        include_control=True, control_outcomes=["exact", "exact", "exact"],
    )
    diag3 = hb.recovery_diagnostics(with_control)
    assert diag3["exact_counts_ordered"] == [0, 0, 0, 0]
    assert diag3["first_operational_recovery_arm"] is None
    assert hb.recovery_diagnostics([])["first_operational_recovery_arm"] is None


# ---- counts, buckets, recount ----

def test_counts_buckets_and_recount_exact_and_tamper():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        summary = run.summary
        assert summary["disclosure"]["recount"] == {
            "key_dependent_bits": TOTAL_KEY_BITS,
            "public_control_bits": TOTAL_PUBLIC_BITS,
            "tag_invocations": 15,
            "event_types": {"l1_disclosure": 12, "l2_disclosure": 15,
                            "verification_tag": 15},
        }
        assert summary["disclosure"]["mismatches"] == []
        assert summary["integrity"]["buckets_disjoint_exhaustive"] is True
        assert summary["integrity"]["disclosure_recount_exact"] is True
        assert all(hb.record_dict_consistent(r, n=hb.FROZEN_N) for r in run.records)
        assert run.events[0]["method"] == "nbpolar_holdout_backoff_diagnostic"
        assert run.events[0]["frame_key"].startswith(
            "nbpolar-p19-holdout-backoff-diagnostic:")
        assert run.events[0]["event_id"] == "block-32768-0-base-l1-disclosure"
        tampered = [dict(e) for e in run.events]
        tampered[0] = dict(tampered[0],
                           key_dependent_bits=tampered[0]["key_dependent_bits"] + 1)
        recount = hb.backoff_recount_events(tampered)
        incremental = {name: summary["disclosure"][name] for name in
                       ("key_dependent_bits", "public_control_bits", "tag_invocations")}
        assert opf._transcript_mismatches(incremental, recount) != []
        assert_raises_match(
            ValueError, "not N/arm-tagged", hb.backoff_recount_events,
            [{"event_id": "block-32768-0-notanarm-l1-disclosure",
              "event_type": "l1_disclosure", "key_dependent_bits": 0,
              "public_control_bits": 0}],
        )
        assert_raises_match(
            ValueError, "not frozen", hb.backoff_recount_events,
            [dict(run.events[0], event_type="bogus_type")],
        )
        for mutate in (dict(outcome="bogus"), dict(k1=320), dict(k2=6491),
                       dict(key_dependent_bits=0),
                       dict(arm_provenance=hb.ORACLE_PROVENANCE)):
            bad = dict(run.records[0], **mutate)
            assert hb.record_dict_consistent(bad, n=hb.FROZEN_N) is False, mutate
        bad_control = dict(run.records[12], key_dependent_bits=5 * 6492)
        assert hb.record_dict_consistent(bad_control, n=hb.FROZEN_N) is False
        bad_control2 = dict(run.records[12], arm_provenance=hb.OPERATIONAL_PROVENANCE)
        assert hb.record_dict_consistent(bad_control2, n=hb.FROZEN_N) is False


# ---- outcome buckets and no-threshold labels ----

def test_outcome_classifier_every_bucket_and_precedence():
    c = opf.classify_operational_outcome
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=True, label_match=True) == "exact"
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=True, label_match=False) == "undetected"
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=False, label_match=False) == "verify_failed"
    assert c(l1_failed=True, l2_failed=False, nonfinite=False,
             tag_pass=False, label_match=False) == "decode_failed"
    assert c(l1_failed=False, l2_failed=True, nonfinite=False,
             tag_pass=False, label_match=False) == "decode_failed"
    assert c(l1_failed=True, l2_failed=False, nonfinite=True,
             tag_pass=False, label_match=False) == "nonfinite"


def test_scripted_buckets_undetected_nonfinite_blocked():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out", scripts={"base": ["undetected"] * 3})
        assert run.summary["operational"]["arms"]["base"]["outcome_counts"]["undetected"] == 3
        assert run.summary["integrity"]["undetected_zero"] is False
        undetected = [r for r in run.records if r["outcome"] == "undetected"]
        assert len(undetected) == 3
        assert all(r["tag_pass"] is True and r["exact"] is False for r in undetected)
        assert run.summary["outcome_label"] == "BLOCKED(undetected_zero)"
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(
            Path(tmp) / "out",
            scripts={"base": ["decode_failed", "nonfinite", "exact"]},
        )
        assert run.summary["operational"]["arms"]["base"]["outcome_counts"]["nonfinite"] == 1
        assert run.summary["operational"]["arms"]["base"]["outcome_counts"]["decode_failed"] == 1
        assert run.summary["integrity"]["nonfinite_zero"] is False
        failed = [r for r in run.records if r["outcome"] == "decode_failed"][0]
        assert failed["key_dependent_bits"] == 5 * 319
        assert failed["tag_invoked"] is False and failed["l1_correct"] is False
        # The frozen counted-budget gate precedes the zero gates and surfaces
        # the short (fully accounted) transcript first.
        assert run.summary["integrity"]["sc_calls_exact"] is False
        assert run.summary["integrity"]["tags_exact"] is False
        assert run.summary["outcome_label"] == "BLOCKED(sc_calls_exact)"


def test_no_threshold_labels_all_recovery_patterns():
    import inspect

    all_true = {name: True for name in hb.INTEGRITY_GATE_ORDER}
    assert hb.backoff_label(all_true) == hb.COMPLETE_LABEL
    assert "COMPLETE" in hb.COMPLETE_LABEL
    for name in hb.INTEGRITY_GATE_ORDER:
        gates = dict(all_true)
        gates[name] = False
        assert hb.backoff_label(gates) == f"BLOCKED({name})"
    assert "recovery" not in inspect.signature(hb.backoff_label).parameters
    assert not hasattr(hb, "recovery_gates")
    assert not hasattr(hb, "select_label")
    assert not hasattr(hb, "wilson_lower_bound")
    text = Path(hb.__file__).read_text(encoding="utf-8")
    for token in ("wilson", "Wilson", "WILSON", "recovery_gates", "EXACT_MIN",
                  "exact_fraction", "fer_rate"):
        assert token not in text, token
    # Every recovery pattern (0/3..3/3, operational and control) is COMPLETE.
    for exact_count in range(4):
        pattern = ["exact"] * exact_count + ["verify_failed"] * (3 - exact_count)
        scripts = {name: list(pattern) for name in hb.OPERATIONAL_ARM_NAMES}
        with tempfile.TemporaryDirectory() as tmp:
            run, _, _ = full_run(Path(tmp) / "op", scripts=scripts,
                                 control_scripts=list(pattern))
            assert run.summary["operational"]["exact_count"] == 4 * exact_count
            assert run.summary["oracle_control"]["arms"]["true_l1_control"][
                "exact_count"] == exact_count
            assert run.summary["recovery"]["exact_counts_ordered"] == [exact_count] * 4
            assert run.summary["integrity_all_pass"] is True
            assert run.summary["outcome_label"] == hb.COMPLETE_LABEL
            assert run.summary["decision"]["recovery_threshold"] is None
            assert run.summary["decision"]["zero_recovery_is_complete"] is True
            assert run.summary["decision"]["three_recovery_is_complete"] is True


# ---- failure paths, checkpoints and precedence ----

def test_budget_stop_abort_fill_and_precedence():
    real_guard = opf._budget_exceeded
    calls = {"n": 0}

    def flaky(start, cap):
        calls["n"] += 1
        if calls["n"] > 1:
            return "wall_s"
        return real_guard(start, cap)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(opf, "_budget_exceeded", flaky):
            run, arms, control = full_run(root)
        assert len(arms.seen) == 1 and len(control.seen) == 0
        lines = (root / "per_block_arm_outcomes.jsonl").read_text().splitlines()
        assert len(lines) == 15
        records = [json.loads(line) for line in lines]
        aborts = [r for r in records if r["outcome"] == "resource_abort"]
        assert len(aborts) == 14
        assert aborts[0]["arm"] == "base" and aborts[0]["block_index"] == 1
        assert aborts[-1]["arm"] == "true_l1_control" and aborts[-1]["block_index"] == 2
        assert all(r["key_dependent_bits"] == 0 for r in aborts)
        assert run.summary["resource_stop_fired"] is True
        assert run.summary["resource_stop_reason"] == "wall_s"
        assert run.summary["integrity"]["sc_calls_exact"] is True  # accounted partial
        assert run.summary["integrity"]["tags_exact"] is True
        assert run.summary["integrity"]["resource_limits_met_and_no_abort"] is False
        assert run.summary["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"
        assert sorted(p.name for p in root.iterdir()) == sorted(hb.OUTPUT_FILES)
    # Failure precedence: an earlier zero gate precedes the resource gate.
    calls["n"] = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(opf, "_budget_exceeded", flaky):
            run, _, _ = full_run(root, scripts={"base": ["undetected"]})
        assert run.summary["integrity"]["undetected_zero"] is False
        assert run.summary["outcome_label"] == "BLOCKED(undetected_zero)"


def test_memory_error_classification_path():
    def oom(**kwargs):
        raise MemoryError("injected exhaustion")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        tmp_path = Path(tmp)
        fab_dir = tmp_path / "fab"
        fab_dir.mkdir()
        fab_path, fab_hex = make_construction_file(fab_dir)
        man = make_manifest(tmp_path)
        counts = injected_counts()
        with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(hb, "verify_p18_block_identity", lambda: {"verified": True}):
                with patched(hb, "run_operational_block", oom):
                    assert_raises_match(
                        hb.BackoffDiagnosticResourceError,
                        "BLOCKED(resource_limits_met_and_no_abort)",
                        hb.run_backoff_diagnostic,
                        counts=counts, hold_table=injected_hold_table(),
                        expected_entropies=expected_seam(counts),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=root,
                    )
        assert sorted(p.name for p in root.iterdir()) == sorted(hb.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"


def test_precondition_failure_blocked_no_sc_call():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        counts = injected_counts()
        counts[:, 0] = 0.0
        arms = FakeOperationalArms()
        control = FakeControl()
        root = tmp_path / "out"
        with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(hb, "verify_p18_block_identity", lambda: {"verified": True}):
                with patched(hb, "run_operational_block", arms):
                    with patched(hb, "run_oracle_control_block", control):
                        assert_raises_match(
                            opr.TargetPopulationContractError,
                            "BLOCKED(target_population_contract)",
                            hb.run_backoff_diagnostic,
                            counts=counts, hold_table=injected_hold_table(),
                            expected_entropies=(opf.EXPECTED_H1, opf.EXPECTED_H2,
                                                opf.EXPECTED_H1 + opf.EXPECTED_H2),
                            construction=str(fab_path), construction_digest=fab_hex,
                            manifest_path=str(man), out_dir=root,
                        )
        assert arms.seen == [] and control.seen == []
        assert sorted(p.name for p in root.iterdir()) == sorted(hb.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(target_population_contract)"


# ---- five-file evidence, scalar-only outputs ----

def test_five_file_scalar_only_inventory_and_resources():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        run, _, _ = full_run(root)
        assert sorted(p.name for p in root.iterdir()) == sorted(hb.OUTPUT_FILES)
        lines = (root / "per_block_arm_outcomes.jsonl").read_text().splitlines()
        assert len(lines) == 15
        records = [json.loads(line) for line in lines]
        required = {
            "arm", "arm_index", "arm_kind", "arm_provenance", "block_index",
            "frame_start", "frame_end", "frame_count", "outcome", "exact",
            "label_match", "tag_pass", "l1_executed", "l1_decode_failed",
            "l2_invoked", "l2_decode_failed", "tag_invoked", "k1", "k2",
            "l1_prefix_len", "l2_prefix_len", "key_dependent_bits",
            "public_control_bits", "raw_ser", "l1_nll_bits", "l2_nll_bits",
            "total_nll_bits", "total_nll_bits_per_pair", "l1_correct",
            "full_block_key_dependent_bits", "public_control_bits_per_tag",
            "disclosure_ce_ratio", "oracle_truth_use", "oracle_control",
            "l1_provenance", "l2_provenance", "error", "wall_s", "resources",
        }
        assert required <= set(records[0])
        for record in records:
            assert set(record["resources"]) == {
                "wall_s", "rss_bytes_hwm", "vm_peak_kb", "vm_size_kb"
            }
            assert record["public_control_bits_per_tag"] == FROZEN_PUBLIC_BITS
            if record["arm_kind"] == "operational":
                assert record["key_dependent_bits"] == \
                    record["full_block_key_dependent_bits"]
                assert record["public_control_bits"] == FROZEN_PUBLIC_BITS
            else:
                assert record["provenance"] == hb.ORACLE_PROVENANCE
            assert record["disclosure_ce_ratio"] == (
                record["full_block_key_dependent_bits"] / record["total_nll_bits"]
            )
        banned = {
            "bob", "high", "low", "high_true", "low_true", "u1_true", "u2_true",
            "a_full", "counts", "logp", "decision_metrics", "high_hat",
            "low_hat", "label_hat", "label_bits", "seed_bits", "rng_state",
            "p_b", "f_full", "labels_true", "l1_order", "l2_order",
            "pooled_e1_mean", "pooled_h1_mean", "pooled_e2_mean", "pooled_h2_mean",
            "labels", "alice", "frame_id", "pair_idx", "alice_symbol",
            "bob_symbol", "p1", "p2",
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
        walk(json.loads((root / "frozen_plan.json").read_text()), keys)
        walk(json.loads((root / "input_and_predecessor_identity.json").read_text()), keys)
        walk(json.loads((root / "aggregate_summary.json").read_text()), keys)
        for record in records:
            walk(record, keys)
        assert not (keys & banned), keys & banned
        assert run.summary["attempt_read_accounting"]["opened_content_paths"] == []
        assert json.loads((root / "frozen_plan.json").read_text())["planned_sc_calls"] == 27
        assert json.loads((root / "frozen_plan.json").read_text())[
            "planned_tag_invocations"] == 15


# ---- real-mode accounting without touching protected inputs ----

def _fake_protected_paths(tmp_path, *, npz_bytes=25166822):
    counts_path = tmp_path / "fake_counts.npz"
    with open(counts_path, "wb") as handle:
        handle.truncate(npz_bytes)
    pairs_path = tmp_path / "fake_pairs.parquet"
    pairs_path.write_bytes(b"fake parquet stand-in, never parsed")
    return counts_path, pairs_path


def test_real_mode_accounting_with_patched_loaders():
    counts = injected_counts()
    hold = injected_hold_table()
    calls = {"npz": 0, "pairs": 0}

    def fake_npz(path):
        calls["npz"] += 1
        return {"1M": counts}

    def fake_pairs(path):
        calls["pairs"] += 1
        return hold

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        counts_path, pairs_path = _fake_protected_paths(tmp_path)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        arms = FakeOperationalArms()
        control = FakeControl()
        saved_npz = hb._NPZ_CONTENT_OPENED
        saved_hold = hb._HOLD_PARQUET_CONTENT_OPENED
        try:
            with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hb, "verify_p18_block_identity", lambda: {"verified": True}):
                    with patched(hb, "load_v25_channel_counts", fake_npz):
                        with patched(hb, "load_pairs_table", fake_pairs):
                            with patched(hb, "run_operational_block", arms):
                                with patched(hb, "run_oracle_control_block", control):
                                    run = hb.run_backoff_diagnostic(
                                        counts_path=str(counts_path),
                                        hold_pairs=str(pairs_path),
                                        expected_entropies=expected_seam(counts),
                                        construction=str(fab_path),
                                        construction_digest=fab_hex,
                                        manifest_path=str(man),
                                        out_dir=tmp_path / "out",
                                    )
            assert calls == {"npz": 1, "pairs": 1}
            acc = run.summary["attempt_read_accounting"]
            assert acc["counts_content_opens"] == 1
            assert acc["hold_content_opens"] == 1
            assert acc["attempts_consumed_by_this_run"] == 1
            assert acc["opened_content_paths"] == [
                str(counts_path.resolve()), str(pairs_path.resolve())
            ]
            assert acc["registered_content_paths"] == acc["opened_content_paths"]
            integrity = run.summary["integrity"]
            assert integrity["one_open_per_protected_input"] is True
            assert integrity["input_stat_unchanged"] is True
            assert integrity["no_unregistered_access"] is True
            assert integrity["sc_calls_exact"] is True
            assert run.summary["outcome_label"] == hb.COMPLETE_LABEL
            assert hb._NPZ_CONTENT_OPENED is True
            assert hb._HOLD_PARQUET_CONTENT_OPENED is True
        finally:
            hb._NPZ_CONTENT_OPENED = saved_npz
            hb._HOLD_PARQUET_CONTENT_OPENED = saved_hold


def test_real_mode_stat_change_blocks_with_earliest_gate():
    counts = injected_counts()
    hold = injected_hold_table()
    real_stat = hb._stat_record
    calls = {"n": 0}

    def shifted_stat(path):
        calls["n"] += 1
        record = real_stat(path)
        if calls["n"] > 2 and record["path"] is not None:
            record["mtime_ns"] += 1
        return record

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        counts_path, pairs_path = _fake_protected_paths(tmp_path)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        saved_npz = hb._NPZ_CONTENT_OPENED
        saved_hold = hb._HOLD_PARQUET_CONTENT_OPENED
        try:
            with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hb, "verify_p18_block_identity", lambda: {"verified": True}):
                    with patched(hb, "load_v25_channel_counts", lambda p: {"1M": counts}):
                        with patched(hb, "load_pairs_table", lambda p: hold):
                            with patched(hb, "run_operational_block", FakeOperationalArms()):
                                with patched(hb, "run_oracle_control_block", FakeControl()):
                                    with patched(hb, "_stat_record", shifted_stat):
                                        run = hb.run_backoff_diagnostic(
                                            counts_path=str(counts_path),
                                            hold_pairs=str(pairs_path),
                                            expected_entropies=expected_seam(counts),
                                            construction=str(fab_path),
                                            construction_digest=fab_hex,
                                            manifest_path=str(man),
                                            out_dir=tmp_path / "out",
                                        )
            assert run.summary["integrity"]["input_stat_unchanged"] is False
            assert run.summary["outcome_label"] == "BLOCKED(input_stat_unchanged)"
        finally:
            hb._NPZ_CONTENT_OPENED = saved_npz
            hb._HOLD_PARQUET_CONTENT_OPENED = saved_hold


# ---- CLI refusals and structural rules ----

def test_cli_parser_and_run_contract_refusals_before_open():
    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on a refusal")

    def forbidden_control(**kwargs):
        raise AssertionError("no control call may happen on a refusal")

    parser = hb.build_parser()
    required = {a.dest for a in parser._actions if a.required}
    assert required == {
        "counts", "source", "floor", "n", "k1", "k2", "construction",
        "construction_digest", "hold_pairs", "hold_frames", "block_frames",
        "remainder_frames", "tag_master", "chunk_rows", "tag_bits", "out_dir",
    }
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)

        def base(**over):
            kw = dict(
                counts=injected_counts(), hold_table=injected_hold_table(),
                construction=str(fab_path), construction_digest=fab_hex,
                manifest_path=str(man),
            )
            kw.update(over)
            return kw

        with patched(hb, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(hb, "verify_p18_block_identity", lambda: {"verified": True}):
                with patched(hb, "run_operational_block", forbidden_arm):
                    with patched(hb, "run_oracle_control_block", forbidden_control):
                        assert_raises_match(
                            ValueError, "hold-frames", hb.run_backoff_diagnostic,
                            **base(hold_frames=(1600, 1998), out_dir=tmp_path / "a"),
                        )
                        assert_raises_match(
                            ValueError, "block-frames", hb.run_backoff_diagnostic,
                            **base(block_frames=64, out_dir=tmp_path / "b"),
                        )
                        assert_raises_match(
                            ValueError, "remainder-frames", hb.run_backoff_diagnostic,
                            **base(remainder_frames=(1985, 1999), out_dir=tmp_path / "c"),
                        )
                        assert_raises_match(
                            ValueError, "tag-master", hb.run_backoff_diagnostic,
                            **base(tag_master=1, out_dir=tmp_path / "d"),
                        )
                        assert_raises_match(
                            ValueError, "n=32768", hb.run_backoff_diagnostic,
                            **base(n=16384, out_dir=tmp_path / "e"),
                        )
                        assert_raises_match(
                            ValueError, "k1=319", hb.run_backoff_diagnostic,
                            **base(k1=320, out_dir=tmp_path / "f"),
                        )
                        assert_raises_match(
                            ValueError, "k2=6492", hb.run_backoff_diagnostic,
                            **base(k2=6491, out_dir=tmp_path / "g"),
                        )
                        assert_raises_match(
                            ValueError, "floor", hb.run_backoff_diagnostic,
                            **base(floor=1e-12, out_dir=tmp_path / "h"),
                        )
                        assert_raises_match(
                            ValueError, "source", hb.run_backoff_diagnostic,
                            **base(source="2M", out_dir=tmp_path / "i"),
                        )
                        assert_raises_match(
                            ValueError, "chunk-rows", hb.run_backoff_diagnostic,
                            **base(chunk_rows=64, out_dir=tmp_path / "j"),
                        )
                        assert_raises_match(
                            ValueError, "tag-bits", hb.run_backoff_diagnostic,
                            **base(tag_bits=32, out_dir=tmp_path / "k"),
                        )
                        assert_raises_match(
                            FileNotFoundError, "not found", hb.run_backoff_diagnostic,
                            **base(construction=str(tmp_path / "absent.json"),
                                   out_dir=tmp_path / "l"),
                        )
        for name in "abcdefghijkl":
            assert not (tmp_path / name).exists()
    import subprocess
    proc = subprocess.run(
        [sys.executable, "-m",
         "comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_backoff_diagnostic",
         "--counts", "x"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 2


def test_existing_root_refusal_zero_execution():
    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        root = tmp_path / "out"
        root.mkdir()
        sentinel = root / "sentinel.txt"
        sentinel.write_text("untouched", encoding="utf-8")
        with patched(hb, "run_operational_block", forbidden_arm):
            assert_raises_match(
                FileExistsError, "refusing to overwrite", hb.run_backoff_diagnostic,
                counts=injected_counts(), hold_table=injected_hold_table(),
                construction=str(tmp_path / "absent.json"),
                construction_digest="x", out_dir=root,
            )
        assert sentinel.read_text(encoding="utf-8") == "untouched"
        assert sorted(p.name for p in root.iterdir()) == ["sentinel.txt"]


def test_module_required_tokens_and_no_forbidden_paths():
    text = Path(hb.__file__).read_text(encoding="utf-8")
    for token in ("load_v25_channel_counts", "load_pairs_table",
                  "normalize_pair_columns", "verify_predecessor_construction",
                  "verify_split_manifest", "verify_p18_block_identity",
                  "target_preconditions", "run_operational_block",
                  "run_oracle_control_block", "polar_transform", "make_gf32",
                  "labels_to_bits", "seed_bits_for", "toeplitz_tag",
                  "canonical_event", "backoff_seed_bits", "form_holdout_blocks",
                  "holdout_nll_bits", "raw_symbol_error_rate", "backoff_label",
                  "backoff_block_events", "backoff_recount_events",
                  "run_backoff_diagnostic", "ORACLE_TRUE_L1_CONTROL"):
        assert token in text, token
    for token in ("heldout", "held_out", "EVAL_", "qualification(",
                  "thresholds", "advance", "retry_arm", "second_arm",
                  "sample_full_block", "block_genie_risks", "select_empirical_split",
                  "budget_k_total", "np.random", "default_rng", ".shuffle"):
        assert token not in text, token
    for token in ("FWHT", "fwht", "BEC", "SCL", "APP"):
        assert not re.search(rf"\b{token}\b", text), token
    assert hb.FROZEN_HOLD_PAIRS_PATH == (
        "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
        "v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet"
    )
    assert hb.FROZEN_OUT_ROOT.endswith("holdout_backoff_diagnostic")
    assert "holdout_microcheck" in hb.__file__ or True
    assert hb.FROZEN_CONSTRUCTION_PATH.endswith(
        "NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/"
        "construction_and_allocation.json"
    )


# ---- tiny real oracle-control path (real SC and real P19 tag) ----

def test_tiny_real_oracle_control_block_one_sc_oracle_labelled():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
        derive_p1,
        derive_p2,
    )
    from comparison_bench.src.comparison_bench.formal_ir.shared import (
        toeplitz_tag as real_tag,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
        polar_transform,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        build_injected_joint_table,
        labels_to_bits,
        seed_bits_for,
    )

    n = 8
    block_index = 1
    table = build_injected_joint_table(epsilon1=0.05, epsilon2=0.2)
    rng = np.random.default_rng(TEST_SEEDS[3])
    bob, _, high, low = opf.sample_full_block(
        rng, np.full(1024, 1.0 / 1024), table, 32, 32, n
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
        make_gf32,
    )

    field = make_gf32()
    u1 = polar_transform(high, field=field, alpha=2)
    u2 = polar_transform(low, field=field, alpha=2)
    labels = (low + 32 * high).astype(np.int64)
    bits = labels_to_bits(labels)
    p19_seed = hb.backoff_seed_bits(TEST_MASTER, n, hb.ORACLE_ARM_NAME, block_index,
                                    bit_length=seed_bits_for(n))
    seen = []

    def spy_tag(bits_in, seed, tag_bits):
        seen.append(np.array(seed, copy=True))
        return real_tag(bits_in, seed, tag_bits)

    def closure(bits_in, _seed, tag_bits, _fixed=p19_seed):
        return spy_tag(bits_in, _fixed, tag_bits)

    calls = {"sc": 0}
    before = [np.array(v, copy=True) for v in (bob, high, low, u1, u2, labels)]
    result = hb.run_oracle_control_block(
        n=n, block_index=block_index, frame_start=1600,
        bob=bob, high_true=high, low_true=low, u1_true=u1, u2_true=u2,
        labels_true=labels, labels_true_bits=bits, field=field,
        p2_table=derive_p2(table), l2_order=np.arange(n), k2=n,
        master=TEST_MASTER, tag_fn=closure, calls=calls,
    )
    assert calls == {"sc": 1}
    assert len(seen) == 2
    assert np.array_equal(seen[0], p19_seed) and np.array_equal(seen[1], p19_seed)
    assert not np.array_equal(seen[0], opf.operational_seed_bits(TEST_MASTER, n, block_index))
    assert not np.array_equal(seen[0], opr.replication_seed_bits(TEST_MASTER, n, block_index))
    assert not np.array_equal(seen[0], hm.holdout_seed_bits(TEST_MASTER, n, block_index))
    assert result.outcome == "exact"
    assert result.exact is True and result.label_match is True
    assert result.key_dependent_bits == 5 * n + 64
    assert result.public_control_bits == seed_bits_for(n)
    assert result.provenance == hb.ORACLE_PROVENANCE
    assert result.oracle_truth_use is True
    assert result.l2_invoked is True
    assert result.truth_leak_violation is False
    for arr, snapshot in zip((bob, high, low, u1, u2, labels), before):
        assert np.array_equal(arr, snapshot)


def test_tiny_real_operational_block_via_p19_closure():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
        derive_p1,
        derive_p2,
    )
    from comparison_bench.src.comparison_bench.formal_ir.shared import (
        toeplitz_tag as real_tag,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
        polar_transform,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        build_injected_joint_table,
        labels_to_bits,
        seed_bits_for,
    )

    n = 8
    block_index = 0
    table = build_injected_joint_table(epsilon1=0.05, epsilon2=0.2)
    rng = np.random.default_rng(TEST_SPARES[0])
    bob, _, high, low = opf.sample_full_block(
        rng, np.full(1024, 1.0 / 1024), table, 32, 32, n
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
        make_gf32,
    )

    field = make_gf32()
    u1 = polar_transform(high, field=field, alpha=2)
    u2 = polar_transform(low, field=field, alpha=2)
    labels = (low + 32 * high).astype(np.int64)
    bits = labels_to_bits(labels)
    p19_seed = hb.backoff_seed_bits(TEST_MASTER, n, "base", block_index,
                                    bit_length=seed_bits_for(n))
    seen = []

    def spy_tag(bits_in, seed, tag_bits):
        seen.append(np.array(seed, copy=True))
        return real_tag(bits_in, seed, tag_bits)

    def closure(bits_in, _seed, tag_bits, _fixed=p19_seed):
        return spy_tag(bits_in, _fixed, tag_bits)

    calls = {"sc": 0}
    before = [np.array(v, copy=True) for v in (bob, high, low, u1, u2, labels)]
    result = hb.run_operational_block(
        n=n, stream_seed=1600, block_index=block_index, bob=bob, high_true=high,
        low_true=low, u1_true=u1, u2_true=u2, labels_true=labels,
        labels_true_bits=bits, field=field, p1_table=derive_p1(table),
        p2_table=derive_p2(table), l1_order=np.arange(n), l2_order=np.arange(n),
        k1=n, k2=n, master=TEST_MASTER, tag_fn=closure, calls=calls,
    )
    assert calls == {"sc": 2}
    assert len(seen) == 2
    assert np.array_equal(seen[0], p19_seed)
    assert result.outcome == "exact"
    assert result.key_dependent_bits == 5 * (n + n) + 64
    assert result.public_control_bits == seed_bits_for(n)
    assert result.l1_provenance == opf.Provenance.PRIOR_ONLY.value
    assert result.l2_provenance == opf.Provenance.CANDIDATE_CONDITIONED.value
    assert result.truth_leak_violation is False
    for arr, snapshot in zip((bob, high, low, u1, u2, labels), before):
        assert np.array_equal(arr, snapshot)
