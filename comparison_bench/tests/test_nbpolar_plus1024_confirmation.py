"""Focused Phase 4-P20E N=32768 +1024 confirmation tests.

Injected tables/arrays and temporary roots only. The V25 1M TRAIN NPZ and
the registered pairs parquet are NEVER content-opened (real-mode tests use
throwaway temporary stubs with patched loaders); the real P16
construction root, the real split manifest, every real evidence root, the
closed HOLD blocks 1600..1983, the consumed P20B VAL pool 1200..1599 and
the consumed P20C DEV blocks 0..383 are never touched. Focused tests use
their own fresh seeds ``2026092101..2026092107`` and never the frozen P20E
tag master 2026092100 (nor the P20C master 2026092090, the P20B master
2026092080, the P19 master 2026092060, the P18 master 2026092050, the
P16/P17 streams, nor any prior/probe seed) for real scoring.

The frozen N=32768 makes real SC calls too slow for runner tests, so
runner tests patch the documented ``run_operational_block`` and
``run_oracle_control_block`` seams with scripted deterministic fakes;
tables, formation, transform, NLL scoring, gates, accounting and
checkpointing all run for real. Zero tuning carry-over from P20C is
asserted literally (same K/floor/caps/order-prefix rule, pinned against
the P20C module read-only), the single +1024 L2 step is asserted as a
single-step disclosure differential (B1 k2=7516 on the SAME frozen L2
order object as B0, key-bit delta exactly +5120), and the triple overlap
gate (consumed P20C DEV first, then consumed VAL, then closed HOLD) is
asserted to refuse before any root exists. Every ``test_*`` takes
no arguments, uses plain asserts and restores any monkeypatched module
attribute in a ``finally``.
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
    plus1024_confirmation as pc,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_disclosure_backoff as lb,  # read-only zero-tuning carry-over reference
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    holdout_microcheck as hm,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13 as opf,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    holdout_backoff_diagnostic as hb,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never any frozen master/stream/probe seed.
TEST_SEEDS = (2026092101, 2026092102, 2026092103, 2026092104)
TEST_MASTER = 2026092105
TEST_SPARES = (2026092106, 2026092107)

FROZEN_BASE_LEAKAGE = 34119  # 5 * 6811 + 64 (B0 base operational)
FROZEN_B1_LEAKAGE = 39239  # 5 * 7835 + 64 (B1, +1024 L2)
FROZEN_CONTROL_LEAKAGE = 32524  # 5 * 6492 + 64 (oracle arm)
FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63
TOTAL_KEY_BITS = 3 * FROZEN_BASE_LEAKAGE + 3 * FROZEN_B1_LEAKAGE + 3 * FROZEN_CONTROL_LEAKAGE  # 317646
TOTAL_PUBLIC_BITS = 9 * FROZEN_PUBLIC_BITS  # 2949687


@contextlib.contextmanager
def patched(obj, name, value):
    original = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, original)


@contextlib.contextmanager
def restored_open_guards():
    """Real-mode tests consume the one-open guards; restore them afterwards."""
    npz, dev = pc._NPZ_CONTENT_OPENED, pc._DEV_PARQUET_CONTENT_OPENED
    try:
        yield
    finally:
        pc._NPZ_CONTENT_OPENED = npz
        pc._DEV_PARQUET_CONTENT_OPENED = dev


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
        "protocol": "nbpolar-p20c-tampered" if tamper == "protocol"
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
    if tamper == "train-frames":
        per[source]["frames"]["train"] = 1199
    elif tamper == "train-pairs":
        per[source]["pairs"]["train"] = 307199
    elif tamper == "hold-frames":
        per[source]["frames"]["hold"] = 399
    elif tamper == "schema":
        schema = "nbldpc_v25_split_manifest_v2"
    elif tamper == "missing-source":
        per = {"type2_2M_20260121_183657": per[source]}
    path = Path(directory) / name
    path.write_text(json.dumps({"schema": schema, "per_source": per}), encoding="utf-8")
    return path


def injected_dev_table(*, frames=384, first_frame=384, per_frame=256,
                       seed=TEST_SEEDS[1], extras=True):
    """Deterministic TRAIN-like pairs frame; shuffled rows, extra non-DEV rows.

    Carries the DEV pool (384..767) plus the declared never-used remainder
    (768..1199, counted but never decoded); ``extras=True`` adds one frame
    per forbidden pool (consumed P20C DEV 0, consumed VAL 1200, closed
    HOLD 1600), present in the file but never selected.
    """
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
    # Declared never-used remainder: present and counted, never decoded.
    rem_frames = np.repeat(np.arange(768, 1200), per_frame)
    rem = pd.DataFrame({
        "frame_id": rem_frames,
        "pair_idx": np.tile(np.arange(per_frame), 432),
        "alice_symbol": rng.integers(0, 1024, size=rem_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=rem_frames.size),
    })
    df = pd.concat([df, rem], ignore_index=True)
    if extras:
        # Frames outside the DEV pool, one per forbidden pool (consumed
        # P20C DEV, consumed VAL, closed HOLD): present in the file but
        # never selected.
        extra = pd.DataFrame({
            "frame_id": np.repeat([0, 1200, 1600], per_frame),
            "pair_idx": np.tile(np.arange(per_frame), 3),
            "alice_symbol": rng.integers(0, 1024, size=3 * per_frame),
            "bob_symbol": rng.integers(0, 1024, size=3 * per_frame),
        })
        df = pd.concat([df, extra], ignore_index=True)
    return df.sample(frac=1.0, random_state=int(seed)).reset_index(drop=True)


def mutate_dev(df, how):
    out = df.copy()
    if how == "drop-frame":
        out = out[out["frame_id"] != 400]
    elif how == "pair-gap":
        row = out[(out["frame_id"] == 384) & (out["pair_idx"] == 255)].index[0]
        out.loc[row, "pair_idx"] = 254
    elif how == "symbol-range":
        row = out[out["frame_id"] == 384].index[0]
        out.loc[row, "bob_symbol"] = 1024
    elif how == "no-dev":
        out = out[out["frame_id"].isin([0, 1200, 1600])]
    elif how == "drop-remainder-frame":
        out = out[out["frame_id"] != 800]
    elif how == "shrink-remainder":
        out = out[~((out["frame_id"] == 1199) & (out["pair_idx"] == 255))]
    else:
        raise AssertionError(f"unknown mutation {how}")
    return out


def tiny_tables(n, *, seed=TEST_SEEDS[2]):
    """Full-shape floored-positive P1/P2 tables plus a tiny DEV block view."""
    rng = np.random.default_rng(seed)
    p1 = rng.random((32, 1024)) + 0.5
    p1 = p1 / p1.sum(axis=0, keepdims=True)
    p2 = rng.random((32, 1024, 32)) + 0.5
    p2 = p2 / p2.sum(axis=2, keepdims=True)
    field = opf_provenance_field()
    bob = rng.integers(0, 1024, size=n).astype(np.int64)
    high = rng.integers(0, 32, size=n).astype(np.int64)
    low = rng.integers(0, 32, size=n).astype(np.int64)
    labels = (low + 32 * high).astype(np.int64)
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        labels_to_bits,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
        polar_transform,
    )

    return {
        "p1": p1,
        "p2": p2,
        "field": field,
        "bob": bob,
        "high": high,
        "low": low,
        "labels": labels,
        "u1": polar_transform(high, field=field, alpha=2),
        "u2": polar_transform(low, field=field, alpha=2),
        "labels_bits": labels_to_bits(labels),
        "l1_order": rng.permutation(n).astype(np.int64),
        "l2_order": rng.permutation(n).astype(np.int64),
    }


def opf_provenance_field():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
        make_gf32,
    )

    return make_gf32()


class FakeOperationalArm:
    """Scripted fake for the accepted ``run_operational_block`` seam (B0 + B1).

    One shared seam serves both operational arms; the arm is identified by
    the disclosed ``k2`` (6492 base vs 7516 +1024 step) and the frozen L2
    order object identity is recorded to pin the order-prefix extension.
    """

    def __init__(self, scripts=None):
        self.scripts = list(scripts or ["exact"] * 6)
        self.seen = []
        self.consumed = 0

    def __call__(self, **kwargs):
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
            seed_bits_for,
        )

        outcome = self.scripts[self.consumed % len(self.scripts)]
        self.consumed += 1
        if outcome == "memory_error":
            raise MemoryError("injected L2 SC memory pressure")
        if outcome == "runtime_error":
            raise RuntimeError("injected ordinary SC failure")
        l1_failed = outcome in ("decode_failed", "nonfinite")
        sc_delta = 1 if l1_failed else 2
        calls = kwargs.get("calls")
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + sc_delta
        n = int(kwargs["n"])
        k1, k2 = int(kwargs["k1"]), int(kwargs["k2"])
        tag = outcome in ("exact", "undetected", "verify_failed")
        self.seen.append({
            "k1": k1, "k2": k2, "outcome": outcome,
            "block_index": int(kwargs["block_index"]),
            "l2_order_id": id(kwargs["l2_order"]),
            "l1_order_id": id(kwargs["l1_order"]),
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
            l1_exact=bool(outcome == "exact"),
            hard_l2_exact=bool(outcome == "exact"),
            oracle_l2_exact=None,
            pair_exact=bool(outcome == "exact"),
            high_hat=None if l1_failed else np.array(kwargs["high_true"], copy=True),
            low_hat=None if l1_failed else np.array(kwargs["low_true"], copy=True),
            label_hat=None,
        )


class FakeControl:
    """Scripted fake for the ``run_oracle_control_block`` (B2) seam."""

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
            "arm": "B2_true_l1_diagnostic", "outcome": outcome,
            "block_index": int(kwargs["block_index"]), "tag_fn": kwargs.get("tag_fn"),
        })
        return pc.OracleControlResult(
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
            provenance=pc.ORACLE_PROVENANCE,
            oracle_truth_use=True,
            low_hat=None,
        )


def full_run(out, *, s0_scripts=None, s2_scripts=None,
             counts=None, dev=None, **over):
    tmp = Path(out).parent
    fab_dir = tmp / "fab"
    fab_dir.mkdir(parents=True, exist_ok=True)
    fab_path, fab_hex = make_construction_file(fab_dir)
    man_path = make_manifest(tmp)
    if counts is None:
        counts = injected_counts()
    if dev is None:
        dev = injected_dev_table()
    s0 = FakeOperationalArm(s0_scripts)
    s2 = FakeControl(s2_scripts)
    kw = dict(
        counts=counts,
        dev_table=dev,
        expected_entropies=expected_seam(counts),
        construction=str(fab_path),
        construction_digest=fab_hex,
        manifest_path=str(man_path),
        out_dir=Path(out),
    )
    kw.update(over)
    with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
        with patched(pc, "run_operational_block", s0):
            with patched(pc, "run_oracle_control_block", s2):
                run = pc.run_plus1024_confirmation(**kw)
    return run, s0, s2


# ---- frozen constants, arm table and fresh seeds ----

def test_frozen_constants_and_arm_table_pinned():
    assert pc.FROZEN_N == 32768
    assert (pc.FROZEN_K1, pc.FROZEN_K2, pc.FROZEN_K_TOTAL) == (319, 6492, 6811)
    assert pc.FROZEN_FLOOR == 1e-15
    assert pc.FROZEN_L2_DELTA_K2 == 1024
    assert pc.FROZEN_K2_B1 == 7516
    assert pc.FROZEN_K_TOTAL_B1 == 7835
    assert pc.FROZEN_B1_KEY_BIT_DELTA == 5120
    assert pc.FROZEN_DEV_FRAME_RANGE == (384, 767)
    assert pc.FROZEN_DEV_FRAMES == 384
    assert pc.FROZEN_DEV_PAIRS == 98304
    assert pc.FROZEN_BLOCK_RANGES == ((384, 511), (512, 639), (640, 767))
    assert pc.FROZEN_REMAINDER_FRAME_RANGE == (768, 1199)
    assert pc.FROZEN_REMAINDER_FRAMES == 432
    assert pc.FROZEN_REMAINDER_SYMBOLS == 110592
    assert pc.FROZEN_MANIFEST_TRAIN_FRAMES == 1200
    assert pc.FROZEN_MANIFEST_TRAIN_PAIRS == 307200
    assert pc.CLOSED_HOLD_FRAME_RANGE == (1600, 1983)
    assert pc.CONSUMED_VAL_FRAME_RANGE == (1200, 1599)
    assert pc.CONSUMED_P20C_DEV_FRAME_RANGE == (0, 383)
    assert pc.FROZEN_TAG_MASTER == 2026092100
    assert pc.PLANNED_SC_CALLS == 15
    assert pc.PLANNED_TAG_INVOCATIONS == 9
    assert pc.PLANNED_RECORDS == 9
    assert pc.FROZEN_LEAKAGE_BITS == FROZEN_BASE_LEAKAGE
    assert pc.FROZEN_B1_LEAKAGE_BITS == FROZEN_B1_LEAKAGE
    assert pc.FROZEN_CONTROL_LEAKAGE_BITS == FROZEN_CONTROL_LEAKAGE
    assert pc.FROZEN_TOTAL_KEY_DEPENDENT_BITS == TOTAL_KEY_BITS
    assert pc.FROZEN_TOTAL_PUBLIC_CONTROL_BITS == TOTAL_PUBLIC_BITS
    assert abs(pc.FROZEN_LEAKAGE_BITS / pc.FROZEN_RAW_INPUT_BITS - 0.1041229248046875) < 1e-12
    assert abs(pc.FROZEN_B1_LEAKAGE_BITS / pc.FROZEN_RAW_INPUT_BITS - 0.1197479248046875) < 1e-12
    pin = pc.check_frozen_arm_table()
    assert pin["l2_delta_k2"] == 1024
    assert pin["b1_k2"] == 7516
    assert pin["b1_key_bit_delta_vs_base"] == 5120
    assert pin["cap_vs_raw_ratio"] < 0.5
    assert pin["b1_cap_vs_raw_ratio"] < 0.5
    assert "--dev-frames 384 767" in pc.FROZEN_COMMAND
    assert "--remainder-frames 768 1199" in pc.FROZEN_COMMAND
    assert "--tag-master 2026092100" in pc.FROZEN_COMMAND
    assert "plus1024_confirmation" in pc.FROZEN_COMMAND
    assert "1200 1599" not in pc.FROZEN_COMMAND
    with patched(pc, "FROZEN_K2_B1", 7515):
        assert_raises_match(ValueError, "1024", pc.check_frozen_arm_table)
    with patched(pc, "FROZEN_B1_LEAKAGE_BITS", 39238):
        assert_raises_match(ValueError, "drifted", pc.check_frozen_arm_table)


def test_zero_tuning_carry_over_from_p20c():
    # Every algorithm input is carried over byte-identical from the P20C
    # module (read-only reference): prior path, floor, construction K
    # values, the +1024 order-prefix step, per-arm caps, N, tag shape,
    # budgets and arm/provenance identity. Only the new-block population
    # and the new tag domain may differ.
    assert pc.FROZEN_N == lb.FROZEN_N == 32768
    assert pc.FROZEN_FLOOR == lb.FROZEN_FLOOR == 1e-15
    assert (pc.FROZEN_K1, pc.FROZEN_K2, pc.FROZEN_K_TOTAL) == (
        lb.FROZEN_K1, lb.FROZEN_K2, lb.FROZEN_K_TOTAL) == (319, 6492, 6811)
    assert pc.FROZEN_L2_DELTA_K2 == lb.FROZEN_L2_DELTA_K2 == 1024
    assert pc.FROZEN_K2_B1 == lb.FROZEN_K2_B1 == 7516
    assert pc.FROZEN_K_TOTAL_B1 == lb.FROZEN_K_TOTAL_B1 == 7835
    assert pc.FROZEN_B1_KEY_BIT_DELTA == lb.FROZEN_B1_KEY_BIT_DELTA == 5120
    assert pc.FROZEN_LEAKAGE_BITS == lb.FROZEN_LEAKAGE_BITS == 34119
    assert pc.FROZEN_B1_LEAKAGE_BITS == lb.FROZEN_B1_LEAKAGE_BITS == 39239
    assert pc.FROZEN_CONTROL_LEAKAGE_BITS == lb.FROZEN_CONTROL_LEAKAGE_BITS == 32524
    assert pc.FROZEN_PUBLIC_CONTROL_BITS == lb.FROZEN_PUBLIC_CONTROL_BITS == 327743
    assert pc.FROZEN_RAW_INPUT_BITS == lb.FROZEN_RAW_INPUT_BITS == 327680
    assert pc.FROZEN_TOTAL_KEY_DEPENDENT_BITS == lb.FROZEN_TOTAL_KEY_DEPENDENT_BITS
    assert pc.FROZEN_TOTAL_PUBLIC_CONTROL_BITS == lb.FROZEN_TOTAL_PUBLIC_CONTROL_BITS
    assert pc.PLANNED_SC_CALLS == lb.PLANNED_SC_CALLS == 15
    assert pc.PLANNED_TAG_INVOCATIONS == lb.PLANNED_TAG_INVOCATIONS == 9
    assert pc.PLANNED_RECORDS == lb.PLANNED_RECORDS == 9
    assert pc.FROZEN_ARM_NAMES == lb.FROZEN_ARM_NAMES
    assert pc.OPERATIONAL_PROVENANCE == lb.OPERATIONAL_PROVENANCE
    assert pc.ORACLE_PROVENANCE == lb.ORACLE_PROVENANCE
    assert pc.DISCLOSURE_RULE == lb.DISCLOSURE_RULE
    assert pc.OUTCOMES == lb.OUTCOMES
    assert pc.INTEGRITY_GATE_ORDER == lb.INTEGRITY_GATE_ORDER
    # The deliberate deltas: new-block population + new tag domain only.
    assert pc.FROZEN_DEV_FRAME_RANGE != lb.FROZEN_DEV_FRAME_RANGE
    assert pc.FROZEN_BLOCK_RANGES != lb.FROZEN_BLOCK_RANGES
    assert pc.FROZEN_TAG_MASTER != lb.FROZEN_TAG_MASTER
    assert pc.SEED_PREFIX != lb.SEED_PREFIX
    assert pc.PROTOCOL_NAME != lb.PROTOCOL_NAME
    assert pc.COMPLETE_LABEL != lb.COMPLETE_LABEL


def test_fresh_test_seeds_disjoint_from_all_frozen_seeds():
    frozen = (
        set(opf.FROZEN_DEV_SEEDS) | set(opf.FROZEN_TRAIN_SEEDS)
        | {hm.FROZEN_TAG_MASTER, hb.FROZEN_TAG_MASTER, lb.FROZEN_TAG_MASTER,
           pc.FROZEN_TAG_MASTER}
    )
    for seed in (2026092050, 2026092060,
                 2026092070, 2026092071, 2026092072, 2026092073,
                 2026092074, 2026092075, 2026092076,
                 2026092080, 2026092081, 2026092082, 2026092083,
                 2026092084, 2026092085, 2026092086, 2026092087,
                 2026092090, 2026092091, 2026092092, 2026092093,
                 2026092094, 2026092095, 2026092096, 2026092097):
        frozen.add(seed)
    for prior in (2026091650, 2026091680, 2026091710, 2026091820, 2026091860,
                  2026091930, 2026091940, 2026091960, 2026091970, 2026091980,
                  2026091990, 2026091800, 2026091811, 2026091753, 2026091760):
        frozen.add(prior)
    assert set(TEST_SEEDS).isdisjoint(frozen)
    assert set(TEST_SPARES).isdisjoint(frozen)
    assert TEST_MASTER not in TEST_SEEDS + TEST_SPARES
    assert pc.FROZEN_TAG_MASTER not in TEST_SEEDS + TEST_SPARES + (TEST_MASTER,)
    assert pc.FROZEN_TAG_MASTER != hm.FROZEN_TAG_MASTER
    assert pc.FROZEN_TAG_MASTER != hb.FROZEN_TAG_MASTER
    assert pc.FROZEN_TAG_MASTER != lb.FROZEN_TAG_MASTER


def test_accepted_helpers_shared_not_reimplemented():
    assert pc.run_operational_block is opf.run_operational_block
    assert pc.run_oracle_control_block is hb.run_oracle_control_block
    assert pc.OracleControlResult is hb.OracleControlResult
    assert pc._decode_layer is opf._decode_layer
    assert pc.classify_operational_outcome is opf.classify_operational_outcome
    assert pc.verify_predecessor_construction.__module__.endswith(
        "operational_f13_replication")
    assert pc.verify_split_manifest is hm.verify_split_manifest
    assert pc.holdout_nll_bits is hm.holdout_nll_bits
    assert pc.raw_symbol_error_rate is hm.raw_symbol_error_rate
    assert pc.polar_transform_fn.__module__.endswith("transform")
    assert pc.make_gf32_fn.__module__.endswith("algebra")
    assert pc.toeplitz_tag_fn.__module__.endswith("shared")
    assert pc.build_p1_metrics_fn.__module__.endswith("prior")
    assert pc.gather_p2_metrics_fn.__module__.endswith("prior")
    assert pc.probs_to_symbol_metric_fn.__module__.endswith("prior")
    assert pc.target_preconditions.__module__.endswith("target_construction")
    assert pc.load_v25_channel_counts.__module__.endswith("v35_algorithm_development")
    assert pc.load_pairs_table.__module__.endswith("pairs_loader")
    for banned in ("sample_full_block", "block_genie_risks", "select_empirical_split",
                   "budget_k_total", "analytic_order", "wilson_lower_bound",
                   "recovery_gates", "select_label", "backoff_seed_bits",
                   "holdout_seed_bits", "operational_seed_bits", "list_decode",
                   "fwht", "belief_provenance", "smooth_joint_to_conditional",
                   "run_search_block", "build_search_candidates",
                   "FROZEN_SEARCH_BOUND_M", "NEIGHBORHOOD_ID", "SEARCH_RULE",
                   "rescores_used", "search_found_better", "selected_source"):
        assert not hasattr(pc, banned), banned
    # The accepted HOLD formation is range-pinned: DEV ranges are refused,
    # which justifies the local P20E formation with identical semantics.
    assert_raises_match(ValueError, "hold-frames",
                         hm.form_holdout_blocks, injected_dev_table(),
                         hold_frames=(384, 767), block_frames=128,
                         remainder_frames=(768, 1199))


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
            with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pc, "load_v25_channel_counts", forbidden_loader):
                    with patched(pc, "load_pairs_table", forbidden_loader):
                        with patched(pc, "run_operational_block", forbidden_arm):
                            with patched(pc, "run_oracle_control_block", forbidden_control):
                                assert_raises_match(
                                    ValueError, "predecessor construction identity",
                                    pc.run_plus1024_confirmation,
                                    counts=injected_counts(), dev_table=injected_dev_table(),
                                    construction=str(fab_path), construction_digest=fab_hex,
                                    manifest_path=str(man), out_dir=root,
                                )
            assert not root.exists()
        fab_path, fab_hex = make_construction_file(tmp_path)
        bad_flag = ("0" if fab_hex[0] != "0" else "1") + fab_hex[1:]
        assert_raises_match(
            ValueError, "digest flag != frozen digest",
            pc.run_plus1024_confirmation,
            counts=injected_counts(), dev_table=injected_dev_table(),
            construction=str(fab_path), construction_digest=bad_flag,
            manifest_path=str(man), out_dir=tmp_path / "outflag",
        )
        assert not (tmp_path / "outflag").exists()


def test_manifest_and_dev_pin_refusals_zero_reads_zero_root():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        good = make_manifest(tmp_path, name="good.json")
        assert_raises_match(FileNotFoundError, "not found", pc.verify_dev_manifest,
                            str(tmp_path / "absent.json"))
        for idx, tamper in enumerate(("train-frames", "train-pairs", "hold-frames",
                                      "schema", "missing-source")):
            man = make_manifest(tmp_path, tamper=tamper, name=f"bad{idx}.json")
            assert_raises_match(ValueError, "manifest identity",
                                pc.verify_dev_manifest, man, source="1M")
            root = tmp_path / f"out{idx}"
            with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pc, "load_v25_channel_counts", forbidden_loader):
                    with patched(pc, "load_pairs_table", forbidden_loader):
                        assert_raises_match(
                            ValueError, "manifest identity",
                            pc.run_plus1024_confirmation,
                            counts=injected_counts(), dev_table=injected_dev_table(),
                            construction=str(fab_path), construction_digest=fab_hex,
                            manifest_path=str(man), out_dir=root,
                        )
            assert not root.exists()
        # The DEV range pin refuses before the opens too. Only
        # CLI-uncovered constants reach the pin at run level (CLI-covered
        # drift trips the earlier frozen-flag refusal); CLI-covered drift is
        # pinned by direct pin calls below.
        root = tmp_path / "outpin"
        for field, value in (
            ("FROZEN_BLOCK_RANGES", ((384, 510), (511, 638), (639, 766))),
        ):
            with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pc, field, value):
                    with patched(pc, "load_v25_channel_counts", forbidden_loader):
                        with patched(pc, "load_pairs_table", forbidden_loader):
                            assert_raises_match(
                                ValueError, "DEV block-range identity",
                                pc.run_plus1024_confirmation,
                                counts=injected_counts(), dev_table=injected_dev_table(),
                                construction=str(fab_path), construction_digest=fab_hex,
                                manifest_path=str(good), out_dir=root,
                            )
        assert not root.exists()
        for field, value, substr in (
            ("FROZEN_REMAINDER_FRAME_RANGE", (769, 1199), "remainder_frame_range"),
            ("FROZEN_DEV_FRAME_RANGE", (384, 768), "dev_frame_range"),
        ):
            with patched(pc, field, value):
                assert_raises_match(ValueError, substr, pc.verify_dev_block_identity)


def test_triple_overlap_gate_p20c_consumed_first_then_val_then_hold():
    pin = pc.verify_dev_block_identity()
    assert pin["verified"] is True
    assert pin["consumed_p20c_disjoint"] is True
    assert pin["closed_disjoint"] is True
    assert pin["consumed_disjoint"] is True
    assert pin["consumed_p20c_dev_frame_range"] == [0, 383]
    assert pin["consumed_val_frame_range"] == [1200, 1599]
    # Any DEV block touching the consumed P20C DEV range refuses FIRST.
    with patched(pc, "FROZEN_BLOCK_RANGES", ((0, 127), (512, 639), (640, 767))):
        assert_raises_match(ValueError, "overlaps consumed P20C DEV",
                            pc.verify_dev_block_identity)
    with patched(pc, "FROZEN_REMAINDER_FRAME_RANGE", (0, 767)):
        assert_raises_match(ValueError, "remainder overlaps consumed P20C",
                            pc.verify_dev_block_identity)
    # A remainder overlapping all three pools reports the P20C pool first.
    with patched(pc, "FROZEN_REMAINDER_FRAME_RANGE", (0, 1600)):
        assert_raises_match(ValueError, "consumed P20C",
                            pc.verify_dev_block_identity)
    # Any DEV block touching the consumed VAL pool refuses second.
    with patched(pc, "FROZEN_BLOCK_RANGES", ((384, 511), (512, 639), (640, 1200))):
        assert_raises_match(ValueError, "overlaps consumed VAL",
                            pc.verify_dev_block_identity)
    with patched(pc, "FROZEN_REMAINDER_FRAME_RANGE", (768, 1200)):
        assert_raises_match(ValueError, "remainder overlaps consumed VAL",
                            pc.verify_dev_block_identity)
    # Any DEV block touching the closed HOLD range refuses third.
    with patched(pc, "FROZEN_BLOCK_RANGES", ((384, 511), (512, 639), (1600, 1727))):
        assert_raises_match(ValueError, "overlaps closed HOLD",
                            pc.verify_dev_block_identity)
    with patched(pc, "FROZEN_REMAINDER_FRAME_RANGE", (1600, 1727)):
        assert_raises_match(ValueError, "remainder overlaps closed HOLD",
                            pc.verify_dev_block_identity)
    # Run level: CLI-covered range drift trips the frozen-flag refusal
    # before any root exists.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for over, substr in (
            ({"dev_frames": (0, 383)}, "dev-frames"),
            ({"dev_frames": (1200, 1599)}, "dev-frames"),
            ({"remainder_frames": (1584, 1599)}, "remainder-frames"),
        ):
            root = tmp_path / f"gate{abs(hash(substr + str(over))) % 100000}"
            with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, substr, pc.run_plus1024_confirmation,
                    counts=injected_counts(), dev_table=injected_dev_table(),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=root, **over,
                )
            assert not root.exists()


# ---- deterministic slicing ----

def test_dev_slicing_blocks_and_remainder_exact():
    formation = pc.form_dev_blocks(injected_dev_table())
    assert formation["dev_frames"] == 384
    assert formation["dev_pairs"] == 98304
    assert formation["block_ranges"] == [[384, 511], [512, 639], [640, 767]]
    assert [b["frame_start"] for b in formation["blocks"]] == [384, 512, 640]
    assert all(len(b["bob"]) == 32768 for b in formation["blocks"])
    assert formation["remainder"]["frames"] == 432
    assert formation["remainder"]["symbols"] == 110592
    assert formation["remainder"]["used"] is False
    closed_first, closed_last = pc.CLOSED_HOLD_FRAME_RANGE
    consumed_first, consumed_last = pc.CONSUMED_VAL_FRAME_RANGE
    p20c_first, p20c_last = pc.CONSUMED_P20C_DEV_FRAME_RANGE
    for start, end in formation["block_ranges"]:
        assert end < closed_first or start > closed_last
        assert end < consumed_first or start > consumed_last
        assert end < p20c_first or start > p20c_last


def test_malformed_dev_population_run_level_blocked_five_files():
    counts = injected_counts()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for idx, how in enumerate(("drop-frame", "pair-gap", "symbol-range", "no-dev")):
            root = tmp_path / f"bad{idx}"
            with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, "BLOCKED(dev_population_exact)",
                    pc.run_plus1024_confirmation,
                    counts=counts, dev_table=mutate_dev(injected_dev_table(), how),
                    expected_entropies=expected_seam(counts),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=root,
                )


def test_declared_remainder_measured_and_fail_closed():
    # The never-used remainder is counted from the pool (never decoded):
    # a damaged remainder blocks with the remainder gate, never success.
    counts = injected_counts()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for idx, how in enumerate(("drop-remainder-frame", "shrink-remainder")):
            root = tmp_path / f"rem{idx}"
            with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, "BLOCKED(blocks_exact_with_declared_remainder)",
                    pc.run_plus1024_confirmation,
                    counts=counts, dev_table=mutate_dev(injected_dev_table(), how),
                    expected_entropies=expected_seam(counts),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=root,
                )


def test_one_open_guards_refuse_reopen_with_zero_execution():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(pc, "_NPZ_CONTENT_OPENED", True):
                with patched(pc, "load_v25_channel_counts", forbidden_loader):
                    assert_raises_match(
                        ValueError, "reopen refused",
                        pc.run_plus1024_confirmation,
                        counts=None, dev_table=injected_dev_table(),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=tmp_path / "o1",
                    )
            with patched(pc, "_DEV_PARQUET_CONTENT_OPENED", True):
                with patched(pc, "load_pairs_table", forbidden_loader):
                    assert_raises_match(
                        ValueError, "reopen refused",
                        pc.run_plus1024_confirmation,
                        counts=injected_counts(), dev_table=None,
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=tmp_path / "o2",
                    )
        assert not (tmp_path / "o1").exists()
        assert not (tmp_path / "o2").exists()
    assert pc._NPZ_CONTENT_OPENED is False
    assert pc._DEV_PARQUET_CONTENT_OPENED is False


def test_no_fitting_or_sampling_tokens_and_exact_call_counts():
    source = Path(pc.__file__).read_text(encoding="utf-8")
    for token in ("np.random.default_rng", "random_state", "sample_full_block",
                  "block_genie_risks", "list_decode", "fwht(", "posterior_APP",
                  "smooth_joint", "wilson_lower_bound", "results/",
                  "outputs_comparison", "git commit", "git push"):
        assert token not in source, token
    assert re.search(r"\bSCL\b", source) is None, "SCL"
    for token in ("plus1024_seed_bits", "form_dev_blocks", "l2_prefix_positions",
                  "candidate_nll_bits", "raw_floor_diagnostics",
                  "frozen-order-prefix-extension", "MemoryError",
                  "resource_abort", "oracle_isolation_ok"):
        assert token in source, token
    assert source.count("except MemoryError") >= 2
    assert source.count("raise  # resource stop owns MemoryError") >= 2
    assert pc.PLANNED_SC_CALLS == 15
    assert pc.PLANNED_TAG_INVOCATIONS == 9


# ---- arms, disclosure differential, accounting ----

def test_three_arm_semantics_k_leakage_labels_and_call_counts():
    with tempfile.TemporaryDirectory() as tmp:
        run, s0, s2 = full_run(Path(tmp) / "out")
        assert len(run.records) == 9
        assert run.summary["records_completed"] == 9
        assert run.summary["sc_calls"] == 15
        assert run.summary["tag_invocations"] == 9
        assert run.summary["aggregates"]["arms"]["B0_sc_base"]["key_dependent_bits"] == 3 * 34119
        assert run.summary["aggregates"]["arms"]["B1_L2plus"]["key_dependent_bits"] == 3 * 39239
        assert run.summary["aggregates"]["arms"]["B2_true_l1_diagnostic"]["key_dependent_bits"] == 3 * 32524
        assert run.summary["aggregates"]["operational"]["key_dependent_bits"] == 3 * 34119 + 3 * 39239
        assert run.summary["aggregates"]["operational"]["public_control_bits"] == 6 * 327743
        assert run.summary["outcome_label"] == pc.COMPLETE_LABEL
        assert run.summary["integrity_all_pass"] is True
        assert len(s0.seen) == 6 and len(s2.seen) == 3
        # Slot order is block-major B0/B1/B2; every arm ran on every block.
        assert sorted(r["block_index"] for r in run.records
                      if r["arm"] == "B1_L2plus") == [0, 1, 2]
        # The single-factor differential: B1 discloses exactly +1024 L2
        # symbols on the SAME frozen L2 order object as B0.
        b0_calls = [c for c in s0.seen if c["k2"] == 6492]
        b1_calls = [c for c in s0.seen if c["k2"] == 7516]
        assert len(b0_calls) == 3 and len(b1_calls) == 3
        assert {c["k1"] for c in s0.seen} == {319}
        assert {c["l2_order_id"] for c in s0.seen} == {s0.seen[0]["l2_order_id"]}
        assert {c["l1_order_id"] for c in s0.seen} == {s0.seen[0]["l1_order_id"]}
        for record in run.records:
            if record["arm"] == "B1_L2plus":
                assert record["l2_prefix_len"] == 7516
                assert record["l2_delta_k2_applied"] == 1024
                assert record["l2_disclosure_rule"] == "frozen-order-prefix-extension"
                assert record["key_bit_delta_vs_base"] == 5120
            elif record["arm_kind"] == "operational":
                assert record["l2_prefix_len"] == 6492
                assert record["l2_delta_k2_applied"] == 0
                assert record["l2_disclosure_rule"] == "base"
                assert record["key_bit_delta_vs_base"] == 0


def test_b1_restored_differential_is_descriptive_and_complete():
    # B0 fails block 0 while B1 restores it: the differential is recorded
    # descriptively and the label stays COMPLETE (no threshold).
    scripts = ["verify_failed", "exact"] + ["exact"] * 4
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out", s0_scripts=scripts)
        recovery = run.summary["aggregates"]["recovery"]
        assert recovery["b1_restored_count"] == 1
        assert recovery["disclosure_blocks"][0]["b1_restored_given_b0_failed"] is True
        assert recovery["disclosure_blocks"][1]["b1_restored_given_b0_failed"] is False
        assert run.summary["outcome_label"] == pc.COMPLETE_LABEL
        assert run.summary["integrity_all_pass"] is True


def test_incremental_k_arithmetic_exact():
    assert 5 * (319 + 6492) + 64 == 34119
    assert 5 * (319 + 7516) + 64 == 39239
    assert 39239 - 34119 == 5120
    assert 5 * 6492 + 64 == 32524
    assert 10 * 32768 + 63 == 327743
    assert 3 * 34119 + 3 * 39239 + 3 * 32524 == TOTAL_KEY_BITS
    assert 9 * 327743 == TOTAL_PUBLIC_BITS


def test_p20e_seed_domain_arm_block_separation():
    seeds = {}
    for arm in pc.FROZEN_ARM_NAMES:
        for block in range(3):
            seed = pc.plus1024_seed_bits(TEST_MASTER, 32768, arm, block)
            assert seed.shape == (327743,)
            seeds[(arm, block)] = seed.tobytes()
    assert len(set(seeds.values())) == 9
    for prefix in ("nbpolar-p16-operational-f13-seed",
                    "nbpolar-p17-operational-replication-seed",
                    "nbpolar-p18-holdout-microcheck-seed",
                    "nbpolar-p19-holdout-backoff-diagnostic-seed",
                    "nbpolar-p20b-bounded-search-diagnostic-seed",
                    "nbpolar-p20c-l2-disclosure-backoff-seed"):
        assert prefix != pc.SEED_PREFIX
    assert pc.SEED_PREFIX == "nbpolar-p20e-plus1024-confirmation-seed"
    assert pc.FROZEN_TAG_MASTER not in (hm.FROZEN_TAG_MASTER, hb.FROZEN_TAG_MASTER,
                                        lb.FROZEN_TAG_MASTER)
    assert_raises_match(ValueError, "unknown frozen arm",
                         pc.plus1024_seed_bits, TEST_MASTER, 32768, "B0", 0)


def test_oracle_isolation_control_excluded_from_operational_aggregates():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        assert pc.oracle_isolation_ok(run.records, final=True) is True
        operational = [r for r in run.records if r["arm_kind"] == "operational"]
        control = [r for r in run.records if r["arm_kind"] == "oracle_control"]
        assert len(operational) == 6 and len(control) == 3
        assert all(r["deployable"] is True for r in operational)
        assert all(r["deployable"] is False for r in control)
        assert all(r["oracle_l2_exact"] is None for r in operational)
        assert all(isinstance(r["oracle_l2_exact"], bool) for r in control)
        assert all(r["l1_exact"] is None and r["hard_l2_exact"] is None
                   for r in control)
        assert run.summary["aggregates"]["operational"]["records"] == 6
        assert run.summary["aggregates"]["oracle_control"]["records"] == 3


def test_disclosure_diagnostics_present_and_descriptive():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        for record in run.records:
            if record["outcome"] == "resource_abort":
                continue
            for key in ("raw_zero_count_hits", "floor_hits_1e15",
                        "floor_hit_log_loss_bits", "l2_nll_candidate_H_bits",
                        "l2_nll_true_H_bits", "selected_total_nll_bits"):
                assert key in record, key
            if record["arm_kind"] == "operational":
                # The scripted fakes return full hats, so operational
                # diagnostics populate; the oracle fake returns no hats
                # (same convention as the P20B control fake).
                assert record["raw_zero_count_hits"] is not None
                assert record["floor_hits_1e15"] is not None
                assert record["floor_hit_log_loss_bits"] is not None
                assert record["l2_nll_candidate_H_bits"] is not None
                assert record["l2_nll_true_H_bits"] is not None
                assert record["selected_total_nll_bits"] is not None
        recovery = run.summary["aggregates"]["recovery"]
        assert set(recovery) == {"per_arm", "b1_restored_count", "disclosure_blocks"}
        assert set(recovery["per_arm"]) == set(pc.FROZEN_ARM_NAMES)


def test_counts_buckets_and_recount_exact_and_tamper():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        events = []
        for record in run.records:
            spec = pc.ARM_BY_NAME[record["arm"]]
            events.extend(pc.plus1024_block_events(
                32768, spec, record["block_index"], record["frame_start"], record))
        recount = pc.plus1024_recount_events(events)
        assert recount["key_dependent_bits"] == TOTAL_KEY_BITS
        assert recount["public_control_bits"] == TOTAL_PUBLIC_BITS
        assert recount["tag_invocations"] == 9
        assert recount["event_types"] == {
            "l1_disclosure": 6, "l2_disclosure": 9, "verification_tag": 9}
        tampered = [dict(event) for event in events]
        tampered[0] = dict(tampered[0], key_dependent_bits=int(tampered[0]["key_dependent_bits"]) + 1)
        assert pc.plus1024_recount_events(tampered)["key_dependent_bits"] != TOTAL_KEY_BITS
        bad_arm = [dict(event) for event in events]
        bad_arm[0] = dict(bad_arm[0], event_id="block-32768-0-nope-l1-disclosure")
        assert_raises_match(ValueError, "N/arm-tagged",
                            pc.plus1024_recount_events, bad_arm)
        bad_type = [dict(event) for event in events]
        bad_type[0] = dict(bad_type[0], event_type="l3_disclosure")
        assert_raises_match(ValueError, "not frozen",
                            pc.plus1024_recount_events, bad_type)


def test_outcome_classifier_every_bucket_and_precedence():
    classify = opf.classify_operational_outcome
    assert classify(l1_failed=False, l2_failed=False, nonfinite=False,
                    tag_pass=True, label_match=True) == "exact"
    assert classify(l1_failed=False, l2_failed=False, nonfinite=False,
                    tag_pass=True, label_match=False) == "undetected"
    assert classify(l1_failed=False, l2_failed=False, nonfinite=False,
                    tag_pass=False, label_match=False) == "verify_failed"
    assert classify(l1_failed=True, l2_failed=False, nonfinite=False,
                    tag_pass=False, label_match=False) == "decode_failed"
    assert classify(l1_failed=False, l2_failed=True, nonfinite=False,
                    tag_pass=False, label_match=False) == "decode_failed"
    # Nonfinite outranks decode_failed; undetected is never success.
    assert classify(l1_failed=True, l2_failed=False, nonfinite=True,
                    tag_pass=False, label_match=False) == "nonfinite"
    assert pc.OUTCOMES == ("exact", "undetected", "verify_failed",
                           "decode_failed", "nonfinite", "resource_abort")


def test_no_threshold_labels_all_recovery_patterns():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        assert run.summary["outcome_label"] == pc.COMPLETE_LABEL
        assert pc.plus1024_confirmation_label(
            {name: True for name in pc.INTEGRITY_GATE_ORDER}) == pc.COMPLETE_LABEL
        gates = {name: True for name in pc.INTEGRITY_GATE_ORDER}
        gates["undetected_zero"] = False
        assert pc.plus1024_confirmation_label(gates) == "BLOCKED(undetected_zero)"


def test_undetected_record_blocks_with_earliest_gate():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(
            Path(tmp) / "out", s0_scripts=["undetected"] + ["exact"] * 5)
        assert run.summary["records_completed"] == 9
        assert run.summary["outcome_label"] == "BLOCKED(undetected_zero)"
        assert run.summary["integrity"]["undetected_zero"] is False


def test_budget_stop_abort_fill_and_precedence():
    counts = injected_counts()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_dir = tmp_path / "fab"
        fab_dir.mkdir(parents=True, exist_ok=True)
        fab_path, fab_hex = make_construction_file(fab_dir)
        man_path = make_manifest(tmp_path)
        s0 = FakeOperationalArm()
        s2 = FakeControl()
        with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(pc, "run_operational_block", s0):
                with patched(pc, "run_oracle_control_block", s2):
                    run = pc.run_plus1024_confirmation(
                        counts=counts, dev_table=injected_dev_table(),
                        expected_entropies=expected_seam(counts),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man_path), out_dir=tmp_path / "out",
                        total_wall_s=1e-9,
                    )
        assert len(run.records) == 9
        assert all(r["outcome"] == "resource_abort" for r in run.records)
        assert run.summary["outcome_label"].startswith("BLOCKED(")
        assert run.summary["resource_stop_fired"] is True
        assert s0.seen == [] and s2.seen == []


def test_operational_memory_error_escapes_to_resource_path():
    counts = injected_counts()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_dir = tmp_path / "fab"
        fab_dir.mkdir(parents=True, exist_ok=True)
        fab_path, fab_hex = make_construction_file(fab_dir)
        man_path = make_manifest(tmp_path)
        s0 = FakeOperationalArm(["exact", "memory_error"] + ["exact"] * 4)
        s2 = FakeControl()
        with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(pc, "run_operational_block", s0):
                with patched(pc, "run_oracle_control_block", s2):
                    try:
                        pc.run_plus1024_confirmation(
                            counts=counts, dev_table=injected_dev_table(),
                            expected_entropies=expected_seam(counts),
                            construction=str(fab_path), construction_digest=fab_hex,
                            manifest_path=str(man_path), out_dir=tmp_path / "out",
                        )
                    except pc.Plus1024ConfirmationResourceError as err:
                        assert "MemoryError" in str(err)
                    else:
                        raise AssertionError("expected a resource stop")
        summary = json.loads((tmp_path / "out" / "aggregate_summary.json").read_text(
            encoding="utf-8"))
        assert summary["outcome_label"].startswith("BLOCKED(")
        records = (tmp_path / "out" / "per_block_arm_outcomes.jsonl").read_text(
            encoding="utf-8").splitlines()
        assert len(records) == 1  # checkpoint before the stop preserved


def test_operational_ordinary_failure_keeps_decode_bucket():
    with tempfile.TemporaryDirectory() as tmp:
        run, s0, _ = full_run(
            Path(tmp) / "out", s0_scripts=["runtime_error"] + ["exact"] * 5)
        assert run.summary["records_completed"] == 9
        failed = [r for r in run.records if r.get("error") is not None]
        assert len(failed) == 1
        assert failed[0]["outcome"] == "decode_failed"
        assert failed[0]["nonfinite"] is False
        assert run.summary["outcome_label"].startswith("BLOCKED(")


def test_precondition_failure_blocked_no_sc_call():
    counts = injected_counts()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_dir = tmp_path / "fab"
        fab_dir.mkdir(parents=True, exist_ok=True)
        fab_path, fab_hex = make_construction_file(fab_dir)
        man_path = make_manifest(tmp_path)
        s0 = FakeOperationalArm()
        s2 = FakeControl()
        with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(pc, "run_operational_block", s0):
                with patched(pc, "run_oracle_control_block", s2):
                    assert_raises_match(
                        ValueError, "target_population_contract",
                        pc.run_plus1024_confirmation,
                        counts=counts, dev_table=injected_dev_table(),
                        expected_entropies=(0.1, 0.1, 0.2),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man_path), out_dir=tmp_path / "out",
                    )
        assert s0.seen == [] and s2.seen == []


def test_five_file_scalar_only_inventory_and_resources():
    banned_keys = {"high_hat", "low_hat", "label_hat", "u_hat", "u1_hat", "u2_hat",
                   "logp", "seed_bits", "seed", "l1_order", "l2_order", "counts",
                   "counts_arr", "metrics", "metric", "bob", "alice_symbol",
                   "bob_symbol", "labels", "labels_bits", "p1_table", "p2_table",
                   "high", "low", "u1", "u2"}

    def walk_keys(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in banned_keys, key
                walk_keys(value)
        elif isinstance(obj, list):
            for value in obj:
                walk_keys(value)

    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        out = Path(tmp) / "out"
        assert sorted(p.name for p in out.iterdir()) == sorted(pc.OUTPUT_FILES)
        for name in ("frozen_plan.json", "input_and_predecessor_identity.json",
                     "aggregate_summary.json"):
            walk_keys(json.loads((out / name).read_text(encoding="utf-8")))
        records = [json.loads(line) for line in
                   (out / "per_block_arm_outcomes.jsonl").read_text().splitlines()]
        assert len(records) == 9
        for record in records:
            walk_keys(record)
            assert pc.record_dict_consistent(record, n=32768)
            assert isinstance(record["resources"], dict)
        report = (out / "report.md").read_text(encoding="utf-8")
        for token in ("high_hat", "low_hat", "label_hat", "logp", "seed_bits",
                      "l1_order", "array("):
            assert token not in report, token
        summary = json.loads((out / "aggregate_summary.json").read_text(encoding="utf-8"))
        assert summary["records_completed"] == 9
        assert summary["attempt_read_accounting"]["attempts_consumed_by_this_run"] == 0
        assert summary["attempt_read_accounting"]["counts_content_opens"] == 0
        assert summary["attempt_read_accounting"]["dev_content_opens"] == 0


def test_real_mode_accounting_with_patched_loaders():
    with restored_open_guards():
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fab_path, fab_hex = make_construction_file(tmp_path)
            man = make_manifest(tmp_path)
            stub_npz = tmp_path / "counts.npz"
            stub_npz.write_bytes(b"stub")
            stub_parquet = tmp_path / "pairs.parquet"
            stub_parquet.write_bytes(b"stub")
            counts = injected_counts()
            dev = injected_dev_table()

            def fake_counts(path):
                assert str(path).endswith("counts.npz")
                return {"1M": counts}

            def fake_pairs(path):
                assert str(path).endswith("pairs.parquet")
                return dev

            with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pc, "EXPECTED_NPZ_BYTES", 4):
                    with patched(pc, "load_v25_channel_counts", fake_counts):
                        with patched(pc, "load_pairs_table", fake_pairs):
                            with patched(pc, "run_operational_block", FakeOperationalArm()):
                                with patched(pc, "run_oracle_control_block", FakeControl()):
                                    run = pc.run_plus1024_confirmation(
                                        counts_path=str(stub_npz),
                                        dev_pairs=str(stub_parquet),
                                        expected_entropies=expected_seam(counts),
                                        construction=str(fab_path),
                                        construction_digest=fab_hex,
                                        manifest_path=str(man),
                                        out_dir=tmp_path / "out",
                                    )
            accounting = run.summary["attempt_read_accounting"]
            assert accounting["counts_content_opens"] == 1
            assert accounting["dev_content_opens"] == 1
            assert accounting["attempts_consumed_by_this_run"] == 1
            assert len(accounting["opened_content_paths"]) == 2


def test_real_mode_stat_change_blocks_with_earliest_gate():
    with restored_open_guards():
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fab_path, fab_hex = make_construction_file(tmp_path)
            man = make_manifest(tmp_path)
            stub_npz = tmp_path / "counts.npz"
            stub_npz.write_bytes(b"stub")
            stub_parquet = tmp_path / "pairs.parquet"
            stub_parquet.write_bytes(b"stub")
            counts = injected_counts()
            dev = injected_dev_table()

            def fake_counts(path):
                return {"1M": counts}

            def fake_pairs(path):
                return dev

            state = {"calls": 0}

            def drifting_stat(path):
                # Every stat call observes a new mtime: before != after.
                state["calls"] += 1
                if path is None:
                    return {"path": None, "size_bytes": None, "mtime_ns": None}
                return {"path": str(path), "size_bytes": 4,
                        "mtime_ns": 1000 + state["calls"]}

            with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pc, "EXPECTED_NPZ_BYTES", 4):
                    with patched(pc, "_stat_record", drifting_stat):
                        with patched(pc, "load_v25_channel_counts", fake_counts):
                            with patched(pc, "load_pairs_table", fake_pairs):
                                with patched(pc, "run_operational_block", FakeOperationalArm()):
                                    with patched(pc, "run_oracle_control_block",
                                                  FakeControl()):
                                        run = pc.run_plus1024_confirmation(
                                            counts_path=str(stub_npz),
                                            dev_pairs=str(stub_parquet),
                                            expected_entropies=expected_seam(counts),
                                            construction=str(fab_path),
                                            construction_digest=fab_hex,
                                            manifest_path=str(man),
                                            out_dir=tmp_path / "out",
                                        )
            # Changed inputs between stat calls fail the earliest stat gate;
            # records still complete but the label is BLOCKED, never success.
            assert run.summary["records_completed"] == 9
            assert run.summary["outcome_label"] == "BLOCKED(input_stat_unchanged)"
            assert run.summary["integrity"]["input_stat_unchanged"] is False


def test_cli_parser_and_run_contract_refusals_before_open():
    parser = pc.build_parser()
    args = parser.parse_args([
        "--counts", "c", "--source", "1M", "--floor", "1e-15",
        "--n", "32768", "--k1", "319", "--k2", "6492",
        "--construction", "f", "--construction-digest", "d",
        "--dev-pairs", "p", "--dev-frames", "384", "767",
        "--block-frames", "128", "--remainder-frames", "768", "1199",
        "--tag-master", "2026092100", "--chunk-rows", "512",
        "--tag-bits", "64", "--out-dir", "o",
    ])
    assert args.dev_frames == [384, 767]
    assert args.tag_master == 2026092100
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for over, substr in (
            ({"k1": 320}, "k1=319"),
            ({"k2": 6493}, "k2=6492"),
            ({"floor": 1e-14}, "floor=1e-15"),
            ({"dev_frames": (384, 768)}, "dev-frames"),
            ({"tag_master": 2026092090}, "tag-master"),
        ):
            root = tmp_path / f"cli{abs(hash(substr)) % 100000}"
            with patched(pc, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, substr, pc.run_plus1024_confirmation,
                    counts=injected_counts(), dev_table=injected_dev_table(),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=root, **over,
                )
            assert not root.exists()


def test_existing_root_refusal_zero_execution():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        root.mkdir()
        with patched(pc, "load_v25_channel_counts", forbidden_loader):
            assert_raises_match(FileExistsError, "refusing to overwrite",
                                 pc.run_plus1024_confirmation,
                                 counts=injected_counts(), dev_table=injected_dev_table(),
                                 construction="f", construction_digest="d",
                                 manifest_path="m", out_dir=root)


def test_module_required_tokens_and_no_forbidden_paths():
    source = Path(pc.__file__).read_text(encoding="utf-8")
    for token in ("FROZEN_DEV_FRAME_RANGE = (384, 767)",
                  "FROZEN_REMAINDER_FRAME_RANGE = (768, 1199)",
                  "CLOSED_HOLD_FRAME_RANGE = (1600, 1983)",
                  "CONSUMED_VAL_FRAME_RANGE = (1200, 1599)",
                  "CONSUMED_P20C_DEV_FRAME_RANGE = (0, 383)",
                  "B1_L2plus", "B2_true_l1_diagnostic", "B0_sc_base",
                  "deployable", "b1_restored_count", "disclosure_blocks",
                  "l2_delta_k2_applied", "frozen-order-prefix-extension",
                  "key_bit_delta_vs_base", "FROZEN_B1_LEAKAGE_BITS = 39239",
                  "FROZEN_TAG_MASTER = 2026092100",
                  "nbpolar-p20e-plus1024-confirmation-seed"):
        assert token in source, token
    for token in ("l2_disclosure_backoff", "L2DisclosureBackoff",
                  "second disclosure step", "S1_bounded_search",
                  "S2_true_l1_diagnostic", "S0_sc_base", "bounded_search",
                  "BoundedSearch", "NEIGHBORHOOD", "rescore", "argmin total NLL"):
        assert token not in source, token
    # Exactly one forbidding mention of a second step; no implementation.
    assert source.count("B1b") == 1


def test_l2_prefix_positions_pin_order_prefix_extension():
    rng = np.random.default_rng(TEST_SEEDS[3])
    order = rng.permutation(32768).astype(np.int64)
    base = pc.l2_prefix_positions(order, 6492)
    plus = pc.l2_prefix_positions(order, 7516)
    assert base.shape == (6492,) and plus.shape == (7516,)
    assert np.array_equal(plus[:6492], base)  # prefix extension, no reselection
    assert np.array_equal(plus, order[:7516])
    assert_raises_match(ValueError, "exceeds", pc.l2_prefix_positions, order, 32769)


def test_tiny_real_operational_and_oracle_via_p20e_closure():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        seed_bits_for,
        labels_to_bits,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        holdout_backoff_diagnostic as hbd,
    )

    n = 64
    tiny = tiny_tables(n)
    calls: dict = {}

    def tag_fn(bits, _seed, tag_bits, _fixed=None):
        seed = pc.plus1024_seed_bits(TEST_MASTER, n, "B0_sc_base", 0,
                                       bit_length=seed_bits_for(n))
        return pc.toeplitz_tag_fn(bits, seed, tag_bits)

    result = opf.run_operational_block(
        n=n, stream_seed=0, block_index=0, bob=tiny["bob"],
        high_true=tiny["high"], low_true=tiny["low"], u1_true=tiny["u1"],
        u2_true=tiny["u2"], labels_true=tiny["labels"],
        labels_true_bits=tiny["labels_bits"], field=tiny["field"],
        p1_table=tiny["p1"], p2_table=tiny["p2"], l1_order=tiny["l1_order"],
        l2_order=tiny["l2_order"], k1=n, k2=n, master=TEST_MASTER,
        tag_fn=tag_fn, calls=calls,
    )
    assert result.outcome == "exact"
    assert result.l1_exact and result.hard_l2_exact and result.pair_exact
    assert result.oracle_l2_exact is None
    assert calls["sc"] == 2
    control = hbd.run_oracle_control_block(
        n=n, block_index=0, frame_start=0, bob=tiny["bob"],
        high_true=tiny["high"], low_true=tiny["low"], u1_true=tiny["u1"],
        u2_true=tiny["u2"], labels_true=tiny["labels"],
        labels_true_bits=tiny["labels_bits"], field=tiny["field"],
        p2_table=tiny["p2"], l2_order=tiny["l2_order"], k2=n,
        master=TEST_MASTER, tag_fn=tag_fn, calls=calls,
    )
    assert control.oracle_l2_exact is True
    assert control.outcome == "exact"


def test_layer_endpoints_and_diagnostics_tiny_real():
    tiny = tiny_tables(32)
    nll = hm.holdout_nll_bits(tiny["bob"], tiny["high"], tiny["low"],
                              tiny["p1"], tiny["p2"])
    assert nll["total_nll_bits"] > 0
    cand = pc.candidate_nll_bits(tiny["bob"], tiny["high"], tiny["low"],
                                 tiny["p1"], tiny["p2"])
    assert abs(cand["total_nll_bits"] - nll["total_nll_bits"]) < 1e-9
    first = pc.first_error_coordinate(tiny["high"], tiny["low"],
                                      tiny["high"], tiny["low"])
    assert first == {"first_error_layer": None, "first_error_coord": None}
    wrong = (tiny["low"] + 1) % 32
    first = pc.first_error_coordinate(tiny["high"], wrong, tiny["high"], tiny["low"])
    assert first["first_error_layer"] == "L2"
    assert first["first_error_coord"] == 0


def test_zero_protected_opens_audit():
    assert pc._NPZ_CONTENT_OPENED is False
    assert pc._DEV_PARQUET_CONTENT_OPENED is False
