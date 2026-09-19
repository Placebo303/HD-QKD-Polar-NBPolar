"""Focused Phase 4-P20M N=32768 raw-prior + session-budget tests.

Injected tables/arrays and fresh additive ``workspace/p20m/<uuid>/`` temp
roots only. The V25 channel-counts NPZ and every registered pairs parquet
(1M, 1.5M, reserved 2M) are NEVER content-opened, statted, or listed (the
real P16 construction root, the real split manifest, the real P20H
calibration product, every real evidence root, the 1M pools, the consumed
1.5M TRAIN DEV ranges, the 1.5M VAL remainder/HOLD pools and the reserved
2M file are never touched; the single read-only worktree-npz open happens
only in the authorized Stage-A derivation, never in tests).
Focused tests use their own fresh seeds ``2026092281..2026092287`` and
never the frozen P20M tag master 2026092280, the frozen derivation seeds
``2026092291..2026092294``, nor any prior/probe seed for real scoring.

The frozen N=32768 makes real SC calls too slow for runner tests, so
runner tests patch the documented ``run_operational_block`` and
``run_oracle_control_block`` seams with scripted deterministic fakes;
tables, formation, transform, NLL scoring, gates, accounting and
checkpointing all run for real. The Stage-A derivation path runs for
real at tiny n on synthetic 1024x1024 count matrices. Every ``test_*``
takes no arguments, uses plain asserts and restores any monkeypatched
module attribute in a ``finally`` (via ExitStack).
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    raw_prior_val_1p5m as pm,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l1_order_1p5m as p20l,  # read-only import target / carry-over reference
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    holdout_microcheck as hm,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13 as opf,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    holdout_backoff_diagnostic as hbd,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    per_session_calibration as psc,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    empirical_genie_scaling as egs,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_n_scaling import (
    budget_k_total,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_DIR = REPO_ROOT / ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M"

# Fresh test-local seeds; never any frozen master/stream/probe/derivation seed.
TEST_SEEDS = (2026092281, 2026092282, 2026092283, 2026092284)
TEST_MASTER = 2026092285
TEST_SPARES = (2026092286, 2026092287)

FROZEN_G0_LEAKAGE = 34119  # 5 * 6811 + 64 (G0 operational control)
FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63


@contextlib.contextmanager
def patched(obj, name, value):
    original = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, original)


@contextlib.contextmanager
def restored_guards():
    """Derivation/run tests consume one-open guards; restore them afterwards."""
    state = (
        pm._WORKTREE_CONTENT_OPENED, pm._WORKTREE_CONTENT_OPENS,
        pm._RAW_PRIOR_CONTENT_LOADED, pm._LAMBDA_PRIOR_CONTENT_LOADED,
        pm._DEV_PARQUET_CONTENT_OPENED,
    )
    try:
        yield
    finally:
        (pm._WORKTREE_CONTENT_OPENED, pm._WORKTREE_CONTENT_OPENS,
         pm._RAW_PRIOR_CONTENT_LOADED, pm._LAMBDA_PRIOR_CONTENT_LOADED,
         pm._DEV_PARQUET_CONTENT_OPENED) = state


@contextlib.contextmanager
def p20m_root():
    """Fresh additive workspace/p20m/<uuid>/ temp root, cleaned up afterwards."""
    root = REPO_ROOT / "workspace" / "p20m" / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    assert "workspace" in root.parts and "p20m" in root.parts
    try:
        yield root
    finally:
        shutil.rmtree(root, ignore_errors=True)


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def injected_counts(seed: int = TEST_SEEDS[0], total: float = 262144.0) -> np.ndarray:
    """Sparse 1024x1024 count matrix feeding synthetic priors."""
    rng = np.random.default_rng(seed)
    counts = np.zeros((1024, 1024), dtype=np.float64)
    cols = np.repeat(np.arange(1024), 2)
    rows = rng.integers(0, 1024, size=2048)
    counts[rows, cols] = rng.integers(1, 500, size=2048)
    extra = rng.choice(1024, size=497, replace=False)
    counts[extra, extra] += rng.integers(1, 500, size=extra.size)
    counts = counts * 4.0
    return counts / counts.sum() * total


def make_raw_prior(counts: np.ndarray) -> dict:
    """Synthetic corrected prior via the frozen §3 raw rule (no lambda)."""
    arrays = pm.build_raw_prior_arrays(counts)
    digest = psc.canonical_prior_digest(arrays)
    return {
        "arrays": dict(arrays),
        "digest": digest,
        "h1": float(arrays["h1"]),
        "h2": float(arrays["h2"]),
        "h_total": float(arrays["h_total"]),
    }


def make_lambda_prior(counts: np.ndarray) -> dict:
    """Synthetic lambda-prior control via the accepted calibration program."""
    arrays = psc.build_prior_arrays(counts)
    digest = psc.canonical_prior_digest(arrays)
    return {
        "arrays": dict(arrays),
        "digest": digest,
        "h1": float(arrays["h1"]),
        "h2": float(arrays["h2"]),
        "h_total": float(arrays["h_total"]),
    }


def make_worktree_npz(directory, counts: np.ndarray, name="calibrated_prior_stub.npz"):
    """Fabricate a P20H-shaped worktree npz (never the real calibration product)."""
    arrays = psc.build_prior_arrays(counts)
    path = Path(directory) / name
    with open(path, "wb") as fh:
        np.savez(fh, **{k: arrays[k] for k in psc.PRIOR_NPZ_KEYS})
    return path, psc.canonical_prior_digest(arrays)


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
    stored_hex = clean_hex
    if tamper == "digest":
        stored_hex = ("0" if clean_hex[0] != "0" else "1") + clean_hex[1:]
    cell["freeze_sha256"] = stored_hex
    doc = {
        "protocol": "nbpolar-p20h-tampered" if tamper == "protocol"
        else "nbpolar-p16-operational-f13-gate",
        "frozen_before_first_dev": True,
        "cell": cell,
    }
    path = directory / "construction_and_allocation.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path, clean_hex


def make_manifest(directory, *, tamper=None, name="split_manifest.json"):
    frames = {"train": 1660, "val": 553, "hold": 554}
    pairs = {"train": 424960, "val": 141568, "hold": 141824}
    schema = hm.FROZEN_MANIFEST_SCHEMA
    source = "type2_1p5M_20260121_183806"
    per = {source: {"frames": dict(frames), "pairs": dict(pairs)}}
    if tamper == "train-pairs":
        per[source]["pairs"]["train"] = 424959
    elif tamper == "schema":
        schema = "nbldpc_v25_split_manifest_v2"
    elif tamper == "missing-source":
        per = {"type2_1M_20260121_184040": per[source]}
    path = Path(directory) / name
    path.write_text(json.dumps({"schema": schema, "per_source": per}), encoding="utf-8")
    return path


def make_order_file_p20m(directory, *, prior_digest, k1, k2, k_total,
                         floor_hits=1046140, floor_hit_rate=0.997,
                         tamper=None, name="raw_prior_orders_stub.json"):
    """Fabricate a canonical-shape P20M order-file copy (never the Stage-A file)."""
    n = 32768
    rng = np.random.default_rng(TEST_MASTER)
    l1 = rng.permutation(n).astype(np.int64).tolist()
    l2 = rng.permutation(n).astype(np.int64).tolist()
    if tamper == "order-dup":
        l1[0] = l1[1]
    derivation = {
        "program": pm.FROZEN_ORDER_PROGRAM_PIN,
        "prior_path": "stub",
        "prior_digest": str(prior_digest),
        "train_seeds": [int(s) for s in pm.FROZEN_DERIVATION_SEEDS],
        "train_blocks_per_seed": 4,
        "train_blocks_attempted": 16,
        "train_blocks_used": 16,
        "train_impossible": 0,
        "train_genie_calls": 32,
        "provenance_violations": 0,
        "budget_literal": "stub",
        "counts_total": 424960,
        "floor_hits": int(floor_hits),
        "floor_hit_rate": float(floor_hit_rate),
        "zero_columns": 0,
        "train_residual": 0.0,
    }
    doc = {
        "protocol": "nbpolar-p20m-raw-prior-val-1p5m",
        "kind": "raw-prior-orders-file",
        "n": n,
        "k_total": int(k_total),
        "k1": int(k1),
        "k2": int(k2),
        "l1_order": l1,
        "l2_order": l2,
        "derivation": derivation,
    }
    if tamper == "protocol":
        doc["protocol"] = "nbpolar-p20m-tampered"
    elif tamper == "kind":
        doc["kind"] = "l1-order-file"
    elif tamper == "prior-digest":
        derivation["prior_digest"] = "0" * 64
    elif tamper == "program":
        derivation["program"] = "tampered"
    elif tamper == "train-seeds":
        derivation["train_seeds"] = [1, 2, 3, 4]
    elif tamper == "blocks-used":
        derivation["train_blocks_used"] = 15
    elif tamper == "k1":
        doc["k1"] = int(k1) + 1
    path = Path(directory) / name
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def injected_dev_table(*, frames=384, first_frame=1660, per_frame=256,
                       seed=TEST_SEEDS[1], extras=True):
    """Deterministic VAL-like pairs frame; shuffled rows, extra non-DEV rows."""
    rng = np.random.default_rng(seed)
    total = frames * per_frame
    frame_id = np.repeat(np.arange(first_frame, first_frame + frames), per_frame)
    pair_idx = np.tile(np.arange(per_frame), frames)
    df = pd.DataFrame({
        "frame_id": frame_id,
        "pair_idx": pair_idx,
        "alice_symbol": rng.integers(0, 1024, size=total),
        "bob_symbol": rng.integers(0, 1024, size=total),
    })
    rem_frames = np.repeat(np.arange(2044, 2213), per_frame)
    rem = pd.DataFrame({
        "frame_id": rem_frames,
        "pair_idx": np.tile(np.arange(per_frame), 169),
        "alice_symbol": rng.integers(0, 1024, size=rem_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=rem_frames.size),
    })
    df = pd.concat([df, rem], ignore_index=True)
    if extras:
        extra = pd.DataFrame({
            "frame_id": np.repeat([2213, 0, 384, 768, 1152, 1536], per_frame),
            "pair_idx": np.tile(np.arange(per_frame), 6),
            "alice_symbol": rng.integers(0, 1024, size=6 * per_frame),
            "bob_symbol": rng.integers(0, 1024, size=6 * per_frame),
        })
        df = pd.concat([df, extra], ignore_index=True)
    return df.sample(frac=1.0, random_state=int(seed)).reset_index(drop=True)


class FakeOperationalArmG:
    """Scripted fake for the accepted ``run_operational_block`` seam (G0 + G1).

    Records the frozen order object identities to pin the operating-point
    swap (G1 runs DIFFERENT L1+L2 order objects than G0 at DIFFERENT K).
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
            "l1_order_id": id(kwargs["l1_order"]),
            "l2_order_id": id(kwargs["l2_order"]),
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


class FakeControlG:
    """Scripted fake for the ``run_oracle_control_block`` (G2) seam."""

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
            "arm": "G2_true_l1_diagnostic", "outcome": outcome,
            "block_index": int(kwargs["block_index"]),
            "l2_order_id": id(kwargs["l2_order"]),
            "tag_fn": kwargs.get("tag_fn"),
        })
        return pm.OracleControlResult(
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
            provenance=pm.ORACLE_PROVENANCE,
            oracle_truth_use=True,
            oracle_l2_exact=bool(outcome == "exact"),
            low_hat=None if l2_failed else np.array(kwargs["low_true"], copy=True),
        )


def consistent_k_point(h_total: float):
    """Budget-consistent (K_total, K1, K2) triple for the injected H."""
    k_total = int(budget_k_total(32768, float(h_total), 1.3))
    k1 = min(k_total // 2, 32768)
    k2 = k_total - k1
    if k2 > 32768:
        k1 = k_total - 32768
        k2 = 32768
    assert 0 <= k1 <= 32768 and 0 <= k2 <= 32768 and k1 + k2 == k_total
    return k_total, k1, k2


def full_run_p20m(out, *, s0_scripts=None, s2_scripts=None,
                  counts=None, lam_counts=None, dev=None, order_tamper=None, **over):
    tmp = Path(out).parent
    fab_dir = tmp / "fab"
    fab_dir.mkdir(parents=True, exist_ok=True)
    fab_path, fab_hex = make_construction_file(fab_dir)
    man_path = make_manifest(tmp)
    raw = make_raw_prior(injected_counts() if counts is None else counts)
    lam = make_lambda_prior(
        injected_counts(TEST_SEEDS[2]) if lam_counts is None else lam_counts)
    k_total, k1, k2 = consistent_k_point(raw["h_total"])
    order_path, order_hex = make_order_file_p20m(
        tmp, prior_digest=raw["digest"], k1=k1, k2=k2, k_total=k_total,
        tamper=order_tamper)
    if dev is None:
        dev = injected_dev_table()
    s0 = FakeOperationalArmG(s0_scripts)
    s2 = FakeControlG(s2_scripts)
    kw = dict(
        prior=raw["arrays"],
        lambda_prior=lam["arrays"],
        dev_table=dev,
        expected_raw=(raw["digest"], raw["h1"], raw["h2"], raw["h_total"]),
        expected_lambda=(lam["h1"], lam["h2"], lam["h_total"]),
        construction=str(fab_path),
        construction_digest=fab_hex,
        manifest_path=str(man_path),
        order_file=str(order_path),
        order_digest=order_hex,
        k1=k1,
        k2=k2,
        out_dir=Path(out),
    )
    kw.update(over)
    stack = contextlib.ExitStack()
    with stack:
        stack.enter_context(patched(pm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex))
        stack.enter_context(patched(pm, "FROZEN_PRIOR_DIGEST", raw["digest"]))
        stack.enter_context(patched(pm, "FROZEN_H1", raw["h1"]))
        stack.enter_context(patched(pm, "FROZEN_H2", raw["h2"]))
        stack.enter_context(patched(pm, "FROZEN_H_TOTAL", raw["h_total"]))
        stack.enter_context(patched(pm, "FROZEN_K_TOTAL", k_total))
        stack.enter_context(patched(pm, "FROZEN_K1_G1", k1))
        stack.enter_context(patched(pm, "FROZEN_K2_G1", k2))
        stack.enter_context(patched(pm, "FROZEN_ORDER_DIGEST", order_hex))
        stack.enter_context(
            patched(pm, "FROZEN_CONSTRUCTION_FLOOR_HITS", 1046140))
        stack.enter_context(
            patched(pm, "FROZEN_CONSTRUCTION_FLOOR_HIT_RATE", 0.997))
        stack.enter_context(patched(p20l, "FROZEN_PRIOR_DIGEST", lam["digest"]))
        stack.enter_context(patched(pm, "run_operational_block", s0))
        stack.enter_context(patched(pm, "run_oracle_control_block", s2))
        run = pm.run_raw_prior_val_1p5m(**kw)
    return run, s0, s2


# ---- frozen literals, arms, carry-over ----

def test_frozen_literals_arms_and_carry_over():
    assert pm.FROZEN_N == 32768
    assert pm.FROZEN_SOURCE == "1p5M"
    assert pm.FROZEN_SOURCE_TAG == "type2_1p5M_20260121_183806"
    assert pm.FROZEN_FLOOR == 1e-15
    assert pm.FROZEN_TARGET_F == 1.3
    assert (pm.FROZEN_K1_G0, pm.FROZEN_K2_G0) == (319, 6492)
    assert pm.FROZEN_LEAKAGE_G0 == 34119 == 5 * 6811 + 64
    assert pm.FROZEN_PUBLIC_CONTROL_BITS == 327743 == 10 * 32768 + 63
    assert pm.FROZEN_TAG_MASTER == 2026092280
    assert pm.SEED_PREFIX == "nbpolar-p20m-raw-prior-val-1p5m-seed"
    assert pm.FROZEN_ARM_NAMES == ("G0_old_point_base", "G1_raw_prior_session_budget",
                                   "G2_true_l1_diagnostic")
    assert pm.ORACLE_ARM_NAME == "G2_true_l1_diagnostic"
    assert pm.PLANNED_SC_CALLS == 15
    assert pm.PLANNED_TAG_INVOCATIONS == 9
    assert pm.PLANNED_RECORDS == 9
    # Carry-over: G0 control + population + construction identical to accepted P20L.
    assert pm.FROZEN_LEAKAGE_G0 == p20l.FROZEN_LEAKAGE_BITS
    assert (pm.FROZEN_K1_G0, pm.FROZEN_K2_G0) == (p20l.FROZEN_K1, p20l.FROZEN_K2)
    assert pm.FROZEN_DEV_FRAME_RANGE == p20l.FROZEN_DEV_FRAME_RANGE == (1660, 2043)
    assert pm.FROZEN_BLOCK_RANGES == p20l.FROZEN_BLOCK_RANGES
    assert pm.FROZEN_REMAINDER_FRAME_RANGE == p20l.FROZEN_REMAINDER_FRAME_RANGE
    assert pm.FROZEN_MANIFEST_TRAIN_PAIRS == psc.FROZEN_MANIFEST_TRAIN_PAIRS == 424960
    assert pm.FROZEN_CONSTRUCTION_DIGEST == p20l.FROZEN_CONSTRUCTION_DIGEST
    assert pm.FROZEN_OLD_L1_ORDER_DIGEST == p20l.FROZEN_OLD_L1_ORDER_DIGEST
    assert pm.FROZEN_WORKTREE_PRIOR_DIGEST == p20l.FROZEN_PRIOR_DIGEST
    assert pm.FROZEN_LAMBDA_PRIOR_DIGEST == p20l.FROZEN_PRIOR_DIGEST
    assert tuple(pm.FROZEN_DERIVATION_SEEDS) == (2026092291, 2026092292,
                                                2026092293, 2026092294)
    assert pm.FROZEN_TRAIN_BLOCKS_PER_SEED == 4
    assert pm.FROZEN_TRAIN_BLOCKS_TOTAL == 16
    assert pm.FROZEN_TRAIN_GENIE_CALLS == 32
    assert "select_empirical_split" in pm.FROZEN_ORDER_PROGRAM_PIN
    assert "block_genie_risks" in pm.FROZEN_ORDER_PROGRAM_PIN
    assert "sample_full_block" in pm.FROZEN_ORDER_PROGRAM_PIN
    # S2-ii build-frames declaration.
    disjoint = pm.verify_build_dev_disjointness()
    assert disjoint == {"build_frames": [0, 1659], "dev_frames": [1660, 2043],
                        "disjoint": True}
    # G0/G1/G2 arm table from an injected derived point (5K+64 rule).
    arms = pm.build_arm_table(k1_g1=700, k2_g1=6320)
    assert [s.name for s in arms] == list(pm.FROZEN_ARM_NAMES)
    assert (arms[0].k1, arms[0].k2, arms[0].leakage_bits) == (319, 6492, 34119)
    assert arms[0].prior_source == "lambda"
    assert (arms[1].k1, arms[1].k2) == (700, 6320)
    assert arms[1].leakage_bits == 5 * 7020 + 64
    assert arms[1].prior_source == "raw"
    assert (arms[2].k1, arms[2].k2) == (0, 6320)
    assert arms[2].leakage_bits == 5 * 6320 + 64
    assert arms[2].kind == "oracle_control"


def test_pin_state_pre_or_post_fill():
    if not pm.pins_are_frozen():
        assert_raises_match(ValueError, "Stage-A freeze not yet applied",
                            pm.pins_frozen)
        assert_raises_match(ValueError, "Stage-A freeze not yet applied",
                            pm.check_frozen_arm_table)
        assert_raises_match(ValueError, "Stage-A freeze not yet applied",
                            pm.frozen_arm_table)
        return
    pins = pm.pins_frozen()
    assert isinstance(pins["prior_digest"], str) and len(pins["prior_digest"]) == 64
    assert isinstance(pins["order_digest"], str) and len(pins["order_digest"]) == 64
    assert pins["k1_g1"] + pins["k2_g1"] == pins["k_total"]
    checked = pm.check_frozen_arm_table()
    assert checked["g0"] == {"k1": 319, "k2": 6492, "leakage_bits": 34119}
    assert checked["g1"]["leakage_bits"] == 5 * pins["k_total"] + 64
    # Module pins match the Stage-A freeze document.
    freeze = (QUEUE_DIR / "P20M_FREEZE.md").read_text(encoding="utf-8")
    assert pins["prior_digest"] in freeze
    assert pins["order_digest"] in freeze
    assert str(pins["k1_g1"]) in freeze and str(pins["k2_g1"]) in freeze


# ---- derivation math, artifact, digest, p_b ----

def independent_raw_rule(counts):
    """Independently written literal of the §3 raw rule (explicit column loop)."""
    mat = np.asarray(counts, dtype=np.float64)
    n_b = mat.sum(axis=0)
    total = float(mat.sum())
    p_global = mat.sum(axis=1) / total
    out = np.empty_like(mat)
    for b in range(mat.shape[1]):
        if n_b[b] == 0:
            out[:, b] = p_global
        else:
            out[:, b] = mat[:, b] / n_b[b]
    floor = 1e-15
    out = np.maximum(out, floor)
    out = out / out.sum(axis=0, keepdims=True)
    return out, n_b / total


def test_raw_prior_math_vs_independent_literal():
    counts = injected_counts()
    cal = pm.derive_raw_prior_arrays(counts)
    f_ref, p_b_ref = independent_raw_rule(counts)
    assert np.array_equal(cal["f_raw"], f_ref)
    assert np.array_equal(cal["p_b"], p_b_ref)
    assert abs(float(cal["p_b"].sum()) - 1.0) < 1e-12
    assert float(np.abs(cal["f_raw"].sum(axis=0) - 1.0).max()) < 1e-12
    assert float(np.abs(cal["p1"].sum(axis=0) - 1.0).max()) < 1e-12
    assert float(np.abs(cal["p2"].sum(axis=2) - 1.0).max()) < 1e-12
    # Floor hits are exactly the zero-count cells (integer counts, 1/max_n_b >> 1e-15).
    zero_cells = int(np.sum(counts == 0))
    assert cal["floor_hits"] == zero_cells
    assert cal["floor_hit_rate"] == zero_cells / counts.size
    assert cal["zero_columns"] == 0
    assert cal["column_dev"] < 1e-12
    assert cal["counts_total"] == int(round(float(counts.sum())))
    assert abs((cal["h1"] + cal["h2"]) - cal["h_total"]) < 1e-12
    # Zero-column fallback goes to p_global exactly.
    mat = counts.copy()
    mat[:, 7] = 0.0
    cal2 = pm.derive_raw_prior_arrays(mat)
    assert cal2["zero_columns"] == 1
    p_global = mat.sum(axis=1) / mat.sum()
    pre = pm.raw_prefloor_table(mat)
    assert np.array_equal(pre[:, 7], p_global)
    # No lambda anywhere: identical output regardless of any smoothing scale.
    assert "lambda" not in pm.derive_raw_prior_arrays.__code__.co_varnames


def test_canonical_digest_determinism():
    counts = injected_counts()
    first = make_raw_prior(counts)
    second = make_raw_prior(counts.copy())
    assert first["digest"] == second["digest"]
    reordered = {k: first["arrays"][k] for k in reversed(list(first["arrays"]))}
    assert psc.canonical_prior_digest(reordered) == first["digest"]
    mutated = dict(first["arrays"])
    flat = np.asarray(mutated["p_b"]).copy()
    flat[0] += 1e-9
    mutated["p_b"] = flat
    assert psc.canonical_prior_digest(mutated) != first["digest"]


def test_pb_cross_check_and_corrected_prior_tamper():
    raw = make_raw_prior(injected_counts())
    good = dict(raw["arrays"])
    verified = pm.verify_corrected_prior(
        good, expected_digest=raw["digest"], expected_h1=raw["h1"],
        expected_h2=raw["h2"], expected_total=raw["h_total"])
    assert verified["passed"] is True
    assert verified["counts_total"] == int(round(float(injected_counts().sum())))
    assert verified["zero_columns"] == 0
    bad = dict(good)
    bad["p_b"] = np.asarray(bad["p_b"]) + 1e-9
    assert_raises_match(ValueError, "p_b_cross_check", pm.verify_corrected_prior, bad,
                        expected_digest=raw["digest"], expected_h1=raw["h1"],
                        expected_h2=raw["h2"], expected_total=raw["h_total"])
    bad = dict(good)
    bad["lambda_star"] = np.asarray(0.5)
    assert_raises_match(ValueError, "lambda_nonzero", pm.verify_corrected_prior, bad,
                        expected_digest=raw["digest"], expected_h1=raw["h1"],
                        expected_h2=raw["h2"], expected_total=raw["h_total"])
    bad = dict(good)
    bad["f_extra"] = np.zeros((4, 4))
    assert_raises_match(ValueError, "exactly", pm.verify_corrected_prior, bad,
                        expected_digest=raw["digest"], expected_h1=raw["h1"],
                        expected_h2=raw["h2"], expected_total=raw["h_total"])
    assert_raises_match(ValueError, "prior_digest_mismatch", pm.verify_corrected_prior,
                        good, expected_digest="0" * 64, expected_h1=raw["h1"],
                        expected_h2=raw["h2"], expected_total=raw["h_total"])
    assert_raises_match(ValueError, "h1_matches_literal", pm.verify_corrected_prior,
                        good, expected_digest=raw["digest"],
                        expected_h1=raw["h1"] + 1e-6,
                        expected_h2=raw["h2"], expected_total=raw["h_total"])


def test_derive_end_to_end_tiny_n_and_artifact_keys():
    counts = injected_counts()
    with p20m_root() as root:
        stub_path, stub_digest = make_worktree_npz(root, counts)
        out_prior = root / "raw_prior_1p5m.npz"
        out_orders = root / "raw_prior_orders_1p5m.json"
        with restored_guards():
            assert pm._WORKTREE_CONTENT_OPENS == 0
            result = pm.run_derive_stage_a(
                worktree_prior_path=stub_path, expected_worktree_digest=stub_digest,
                out_prior_path=out_prior, out_orders_path=out_orders,
                expected_counts_total=int(round(float(counts.sum()))), n=64)
            assert pm._WORKTREE_CONTENT_OPENS == 1
            # Reopen in the same process refuses.
            assert_raises_match(pm.RawPriorVal1p5mContractError, "reopen refused",
                                pm.load_worktree_counts_arrays, stub_path,
                                expected_digest=stub_digest)
        assert result["train_blocks_used"] == 16
        assert result["train_genie_calls"] == 32
        assert result["k1"] + result["k2"] == result["k_total"]
        assert result["worktree_content_opens"] == 1
        assert result["derivation_seeds"] == [2026092291, 2026092292,
                                              2026092293, 2026092294]
        # Artifact: exact 10-key set, dtypes, pins, normalization.
        with open(out_prior, "rb") as fh:
            data = np.load(fh, allow_pickle=False)
            with data:
                assert set(str(k) for k in data.files) == set(pm.RAW_PRIOR_NPZ_KEYS)
                arrays = {k: np.asarray(data[k]) for k in data.files}
        assert float(arrays["lambda_star"]) == 0.0
        assert float(arrays["floor_value"]) == 1e-15
        assert arrays["counts_ab"].shape == (1024, 1024)
        assert arrays["f_raw"].shape == (1024, 1024)
        assert arrays["p1"].shape == (32, 1024)
        assert arrays["p2"].shape == (32, 1024, 32)
        assert arrays["p_b"].shape == (1024,)
        assert psc.canonical_prior_digest(arrays) == result["prior_digest"]
        # Order file: P20M kind, L1+L2 permutations at tiny n, digest-gated use.
        doc = json.loads(out_orders.read_text(encoding="utf-8"))
        assert doc["protocol"] == pm.PROTOCOL_NAME
        assert doc["kind"] == "raw-prior-orders-file"
        assert doc["n"] == 64
        assert set(doc["l1_order"]) == set(range(64))
        assert set(doc["l2_order"]) == set(range(64))
        assert doc["derivation"]["train_blocks_used"] == 16
        assert doc["derivation"]["prior_digest"] == result["prior_digest"]
        assert hashlib.sha256(out_orders.read_bytes()).hexdigest() == result[
            "order_digest"]
        with restored_guards():
            assert pm._WORKTREE_CONTENT_OPENS == 0
        # Existing products refuse overwrite.
        assert_raises_match(FileExistsError, "refusing to overwrite",
                            pm.run_derive_stage_a,
                            worktree_prior_path=stub_path,
                            expected_worktree_digest=stub_digest,
                            out_prior_path=out_prior, out_orders_path=out_orders,
                            expected_counts_total=int(round(float(counts.sum()))), n=64)


def test_select_empirical_split_semantics_tiny():
    rng = np.random.default_rng(TEST_SEEDS[3])
    n = 64
    e1 = rng.random(n)
    h1 = rng.random(n)
    e2 = rng.random(n)
    h2 = rng.random(n)
    k_total = 20
    split = egs.select_empirical_split(n, e1, h1, e2, h2, k_total)
    assert split["k1"] + split["k2"] == k_total
    assert set(np.asarray(split["l1_order"]).tolist()) == set(range(n))
    assert set(np.asarray(split["l2_order"]).tolist()) == set(range(n))
    # Lexicographic minimum over every feasible K1, ties toward smaller K1.
    best = None
    for cand_k1 in range(0, min(n, k_total) + 1):
        cand_k2 = k_total - cand_k1
        residual = egs.residual_for_orders(
            e1, e2, split["l1_order"], split["l2_order"], cand_k1, cand_k2)
        key = (residual, cand_k1, cand_k2)
        if best is None or key < best[0]:
            best = (key, cand_k1, cand_k2)
    assert (split["k1"], split["k2"]) == (best[1], best[2])
    # Budget literal recomputation matches the accepted frozen budget.
    assert budget_k_total(n, 1.5, 1.3) == max(0, min(2 * n, int(__import__("math").floor(
        (1.3 * n * 1.5 - 64.0) / 5.0))))
    literal = pm.budget_literal_display(0.825566051673296)
    assert "1.3*32768*" in literal and "floored" in literal
    verified = pm.verify_budget_literal(0.825566051673296, 7020)
    assert verified["k_total"] == 7020
    assert_raises_match(ValueError, "BLOCKED(budget_literal_recomputed)",
                        pm.verify_budget_literal, 0.825566051673296, 7021)


# ---- grep rule: seed placement ----

def _git_grep_hits(literal: str):
    proc = subprocess.run(
        ["git", "grep", "-l", literal, "--", "."],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1), proc.stderr
    return [line for line in proc.stdout.splitlines() if line.strip()]


def test_grep_rule_seed_placement():
    master = "2026092280"
    test_seeds = ["2026092281", "2026092282", "2026092283", "2026092284",
                  "2026092285", "2026092286", "2026092287"]
    deriv_seeds = ["2026092291", "2026092292", "2026092293", "2026092294"]
    module_source = Path(pm.__file__).read_text(encoding="utf-8")
    test_source = Path(__file__).read_text(encoding="utf-8")
    assert master in module_source
    for seed in deriv_seeds:
        assert seed in module_source
    for seed in test_seeds:
        assert seed in test_source
        assert seed not in module_source
    # The frozen master/derivation seeds are disjoint from every frozen seed
    # of the predecessor packets.
    assert pm.FROZEN_TAG_MASTER not in (p20l.FROZEN_TAG_MASTER,)
    for seed in pm.FROZEN_DERIVATION_SEEDS:
        assert seed not in tuple(p20l.FROZEN_TRAIN_SEEDS)
    # Repo-wide: hits live only in the P20M runner/tests/packet/spec documents.
    allowed_prefixes = (
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/raw_prior_val_1p5m.py",
        "comparison_bench/tests/test_nbpolar_raw_prior_val_1p5m.py",
        ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20m/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md",
    )
    for literal in [master] + test_seeds + deriv_seeds:
        for hit in _git_grep_hits(literal):
            assert hit.startswith(allowed_prefixes), (literal, hit)


# ---- gate refusals, modes, guards ----

def test_order_file_digest_gated_use():
    raw = make_raw_prior(injected_counts())
    k_total, k1, k2 = consistent_k_point(raw["h_total"])
    with p20m_root() as root:
        order_path, order_hex = make_order_file_p20m(
            root, prior_digest=raw["digest"], k1=k1, k2=k2, k_total=k_total)
        with patched(pm, "FROZEN_ORDER_DIGEST", order_hex):
            pin = pm.verify_stage_b_order_file_p20m(
                order_path, expected_digest=order_hex,
                expected_prior_digest=raw["digest"], expected_k1=k1,
                expected_k2=k2, expected_k_total=k_total)
            assert pin["verified"] is True
            assert pin["k1"] == k1 and pin["k2"] == k2
        # Wrong --order-digest flag value refuses (bytes mismatch path).
        with patched(pm, "FROZEN_ORDER_DIGEST", "f" * 64):
            assert_raises_match(ValueError, "order-file digest flag",
                                pm.verify_stage_b_order_file_p20m, order_path,
                                expected_digest=order_hex,
                                expected_prior_digest=raw["digest"],
                                expected_k1=k1, expected_k2=k2,
                                expected_k_total=k_total)
        # Tampered bytes refuse against the previously good digest.
        tampered = root / "tampered.json"
        tampered.write_bytes(order_path.read_bytes() + b" ")
        with patched(pm, "FROZEN_ORDER_DIGEST", order_hex):
            assert_raises_match(ValueError, "bytes sha256",
                                pm.verify_stage_b_order_file_p20m, tampered,
                                expected_digest=order_hex,
                                expected_prior_digest=raw["digest"],
                                expected_k1=k1, expected_k2=k2,
                                expected_k_total=k_total)
        # Provenance mismatches refuse.
        for tamper, substr in (("prior-digest", "prior digest"),
                              ("program", "program pin"),
                              ("train-seeds", "TRAIN seeds"),
                              ("blocks-used", "block count"),
                              ("k1", "k1 !="),
                              ("protocol", "protocol"),
                              ("kind", "kind")):
            bad_path, _ = make_order_file_p20m(
                root, prior_digest=raw["digest"], k1=k1, k2=k2, k_total=k_total,
                tamper=tamper, name=f"bad_{tamper}.json")
            bad_hex = hashlib.sha256(bad_path.read_bytes()).hexdigest()
            with patched(pm, "FROZEN_ORDER_DIGEST", bad_hex):
                assert_raises_match(ValueError, substr,
                                    pm.verify_stage_b_order_file_p20m, bad_path,
                                    expected_digest=bad_hex,
                                    expected_prior_digest=raw["digest"],
                                    expected_k1=k1, expected_k2=k2,
                                    expected_k_total=k_total)


def test_cli_modes_refuse_before_read_write():
    assert pm.main([]) == 2
    assert pm.main(["--derive", "--n", "32768"]) == 2
    assert pm.main(["--derive", "--out-dir", "o"]) == 2
    # Missing-flag Stage-B invocation refuses.
    assert pm.main(["--prior", "p", "--source", "1p5M"]) == 2
    # Stage-B root stays absent: Stage A creates no Stage-B root.
    assert not Path(pm.FROZEN_OUT_ROOT).exists()
    parser = pm.build_parser()
    args = parser.parse_args([
        "--prior", "p", "--source", "1p5M", "--floor", "1e-15",
        "--n", "32768", "--k1", "700", "--k2", "6320",
        "--construction", "c", "--construction-digest", "d",
        "--dev-pairs", "p", "--dev-frames", "1660", "2043",
        "--block-frames", "128", "--remainder-frames", "2044", "2212",
        "--tag-master", "2026092280", "--chunk-rows", "512",
        "--tag-bits", "64", "--order-file", "o", "--order-digest", "g",
        "--out-dir", "r",
    ])
    assert args.tag_master == 2026092280
    assert tuple(args.dev_frames) == (1660, 2043)
    assert pm.STAGE_B_FLAGS[0] == "prior" and "out_dir" in pm.STAGE_B_FLAGS


def test_no_stage_b_root_and_no_protected_opens_in_stage_a():
    counts = injected_counts()
    with p20m_root() as root:
        stub_path, stub_digest = make_worktree_npz(root, counts)
        with restored_guards():
            pm.run_derive_stage_a(
                worktree_prior_path=stub_path, expected_worktree_digest=stub_digest,
                out_prior_path=root / "a.npz", out_orders_path=root / "a.json",
                expected_counts_total=int(round(float(counts.sum()))), n=64)
        assert not Path(pm.FROZEN_OUT_ROOT).exists()
    assert pm._DEV_PARQUET_CONTENT_OPENED is False
    assert pm._RAW_PRIOR_CONTENT_LOADED is False
    assert pm._LAMBDA_PRIOR_CONTENT_LOADED is False
    assert "load_v25_channel_counts" not in dir(pm)
    source = Path(pm.__file__).read_text(encoding="utf-8")
    for token in ("load_v25_channel_counts", "FROZEN_COUNTS_PATH", "channel_counts",
                  "smooth_joint_to_conditional", "LAMBDA_STAR", "137.3823795883264",
                  "v25_npz", "F1_new_l1_order_base", "F2_true_l1_diagnostic"):
        assert token not in source, token
    for token in ("corrected_prior_identity", "budget_literal", "raw-prior-orders-file",
                  "G0_old_point_base", "G1_raw_prior_session_budget",
                  "G2_true_l1_diagnostic", "g1_restored_count", "deployable",
                  "from . import l1_order_1p5m", "select_empirical_split",
                  "sample_full_block", "derive_raw_prior_arrays",
                  "nbpolar-p20m-raw-prior-val-1p5m-seed"):
        assert token in source, token


def test_seed_domain_separation_and_format():
    got = pm.raw_prior_val_1p5m_seed_bits(2026092280, 32768, "G0_old_point_base", 0)
    assert got.shape == (327743,)
    again = pm.raw_prior_val_1p5m_seed_bits(2026092280, 32768, "G0_old_point_base", 0)
    assert np.array_equal(got, again)
    other_arm = pm.raw_prior_val_1p5m_seed_bits(
        2026092280, 32768, "G1_raw_prior_session_budget", 0)
    assert not np.array_equal(got, other_arm)
    other_block = pm.raw_prior_val_1p5m_seed_bits(2026092280, 32768, "G0_old_point_base", 1)
    assert not np.array_equal(got, other_block)
    # The P20M domain differs from the P20L domain by construction.
    legacy = p20l.l1_order_1p5m_seed_bits(
        p20l.FROZEN_TAG_MASTER, 32768, "F0_old_order_base", 0)
    assert legacy.shape == got.shape
    assert not np.array_equal(got, legacy)
    assert_raises_match(ValueError, "unknown frozen arm",
                        pm.raw_prior_val_1p5m_seed_bits, 2026092280, 32768, "F0", 0)


def test_one_open_guards_refuse_reload():
    with restored_guards():
        pm._WORKTREE_CONTENT_OPENED = True
        assert_raises_match(pm.RawPriorVal1p5mContractError, "reopen refused",
                            pm.load_worktree_counts_arrays, "stub",
                            expected_digest="0" * 64)
    with p20m_root() as root:
        out = root / "guard_out"
        out.mkdir()
        assert_raises_match(FileExistsError, "refusing to overwrite",
                            pm.run_raw_prior_val_1p5m,
                            prior={}, lambda_prior={}, dev_table=None,
                            k1=1, k2=2, order_digest="d", out_dir=out)


# ---- full Stage-B runs with scripted SC fakes ----

def test_full_run_all_exact_complete_five_files():
    with p20m_root() as root:
        out = root / "run_out"
        with restored_guards():
            run, s0, s2 = full_run_p20m(out)
        summary = run.summary
        assert summary["records_completed"] == 9
        assert summary["sc_calls"] == 15
        assert summary["tag_invocations"] == 9
        assert summary["stage_b_sampling_calls"] == 0
        assert summary["integrity_all_pass"] is True
        assert summary["failing_integrity_gates"] == []
        assert summary["outcome_label"] == pm.COMPLETE_LABEL
        assert summary["recount_mismatch"] == 0
        assert summary["aggregates"]["operational"]["exact_count"] == 6
        assert summary["aggregates"]["oracle"]["exact_count"] == 3
        assert summary["aggregates"]["recovery"]["g1_restored_count"] == 0
        assert summary["aggregates"]["recovery"]["g1_maintain_count"] == 3
        assert summary["aggregates"]["undetected_count"] == 0
        for name in pm.OUTPUT_FILES:
            assert (out / name).is_file(), name
        records = list(run.records)
        assert {(r["arm"], r["block_index"]) for r in records} == {
            (name, block) for name in pm.FROZEN_ARM_NAMES for block in range(3)}
        for record in records:
            assert record["floor_hit_rate"] is not None
            assert record["k_total"] == record["k1"] + record["k2"]
            assert "1.3*32768*" in record["budget_literal"]
            if record["arm"] == "G0_old_point_base":
                assert record["prior_source"] == "lambda"
                assert record["l1_order_digest"] == pm.FROZEN_OLD_L1_ORDER_DIGEST
                assert record["key_bit_delta_vs_G0"] == 0
            elif record["arm"] == "G1_raw_prior_session_budget":
                assert record["prior_source"] == "raw"
                assert record["l1_exact"] is True
            else:
                assert record["deployable"] is False
                assert record["oracle_l2_exact"] is True
        # Operating-point swap: G1 runs different L1+L2 order objects than G0
        # at different K; G2 shares G1's derived L2 object.
        g0_seen = [s for s in s0.seen if s["k1"] == 319 and s["k2"] == 6492]
        g1_seen = [s for s in s0.seen if not (s["k1"] == 319 and s["k2"] == 6492)]
        assert len(g0_seen) == 3 and len(g1_seen) == 3
        assert {s["l1_order_id"] for s in g0_seen}.isdisjoint(
            {s["l1_order_id"] for s in g1_seen})
        assert {s["l2_order_id"] for s in g0_seen}.isdisjoint(
            {s["l2_order_id"] for s in g1_seen})
        assert {s["l2_order_id"] for s in s2.seen} == {
            s["l2_order_id"] for s in g1_seen}
        assert len(s2.seen) == 3


def test_full_run_restoration_is_descriptive_and_complete():
    with p20m_root() as root:
        out = root / "run_restore"
        with restored_guards():
            run, _, _ = full_run_p20m(
                out,
                s0_scripts=["verify_failed", "exact", "exact",
                            "exact", "exact", "exact"],
                s2_scripts=["exact"] * 3)
        summary = run.summary
        assert summary["integrity_all_pass"] is True
        assert summary["outcome_label"] == pm.COMPLETE_LABEL
        assert summary["aggregates"]["recovery"]["g1_restored_count"] == 1
        assert summary["aggregates"]["operational"]["exact_count"] == 5


def test_full_run_undetected_blocks_with_earliest_gate():
    with p20m_root() as root:
        out = root / "run_undet"
        with restored_guards():
            run, _, _ = full_run_p20m(
                out, s0_scripts=["undetected"] + ["exact"] * 5,
                s2_scripts=["exact"] * 3)
        assert run.summary["integrity_all_pass"] is False
        assert run.summary["outcome_label"] == "BLOCKED(undetected_zero)"
        assert len(run.records) == 9


def test_full_run_stage_b_zero_sampling_pin():
    with p20m_root() as root:
        out = root / "run_nosample"
        with restored_guards():
            with patched(pm, "sample_full_block", _forbidden_sampler):
                with patched(pm, "block_genie_risks", _forbidden_sampler):
                    run, _, _ = full_run_p20m(out)
        assert run.summary["stage_b_sampling_calls"] == 0
        assert run.gates["genie_calls_exact"] is True


def _forbidden_sampler(*args, **kwargs):
    raise AssertionError("Stage B must perform zero sampling of any kind")


def test_tiny_real_sc_via_accepted_path():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        seed_bits_for,
        labels_to_bits,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
        polar_transform,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
        make_gf32,
    )

    n = 64
    rng = np.random.default_rng(TEST_SEEDS[3])
    p1 = rng.random((32, 1024)) + 0.5
    p1 = p1 / p1.sum(axis=0, keepdims=True)
    p2 = rng.random((32, 1024, 32)) + 0.5
    p2 = p2 / p2.sum(axis=2, keepdims=True)
    field = make_gf32()
    bob = rng.integers(0, 1024, size=n).astype(np.int64)
    high = rng.integers(0, 32, size=n).astype(np.int64)
    low = rng.integers(0, 32, size=n).astype(np.int64)
    labels = (low + 32 * high).astype(np.int64)
    calls: dict = {}

    def tag_fn(bits, _seed, tag_bits, _fixed=None):
        seed = pm.raw_prior_val_1p5m_seed_bits(
            TEST_MASTER, n, "G0_old_point_base", 0, bit_length=seed_bits_for(n))
        return pm.toeplitz_tag_fn(bits, seed, tag_bits)

    result = pm.run_operational_block(
        n=n, stream_seed=0, block_index=0, bob=bob,
        high_true=high, low_true=low,
        u1_true=polar_transform(high, field=field, alpha=2),
        u2_true=polar_transform(low, field=field, alpha=2),
        labels_true=labels, labels_true_bits=labels_to_bits(labels), field=field,
        p1_table=p1, p2_table=p2, l1_order=rng.permutation(n).astype(np.int64),
        l2_order=rng.permutation(n).astype(np.int64), k1=n, k2=n, master=TEST_MASTER,
        tag_fn=tag_fn, calls=calls,
    )
    assert result.outcome == "exact"
    assert calls["sc"] == 2
    control = pm.run_oracle_control_block(
        n=n, block_index=0, frame_start=0, bob=bob,
        high_true=high, low_true=low,
        u1_true=polar_transform(high, field=field, alpha=2),
        u2_true=polar_transform(low, field=field, alpha=2),
        labels_true=labels, labels_true_bits=labels_to_bits(labels), field=field,
        p2_table=p2, l2_order=rng.permutation(n).astype(np.int64), k2=n,
        master=TEST_MASTER, tag_fn=tag_fn, calls=calls,
    )
    assert control.oracle_l2_exact is True
    nll = pm.holdout_nll_bits(bob, high, low, p1, p2)
    assert nll["total_nll_bits"] > 0
    first = pm.first_error_coordinate(high, low, high, low)
    assert first == {"first_error_layer": None, "first_error_coord": None}


def test_zero_protected_opens_audit():
    assert pm._WORKTREE_CONTENT_OPENED is False
    assert pm._RAW_PRIOR_CONTENT_LOADED is False
    assert pm._LAMBDA_PRIOR_CONTENT_LOADED is False
    assert pm._DEV_PARQUET_CONTENT_OPENED is False
