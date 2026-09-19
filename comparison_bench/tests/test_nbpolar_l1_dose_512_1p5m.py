"""Focused Phase 4-P20K N=32768 L1-dose-512 +512 single-factor tests.

Injected tables/arrays and temporary roots only. The V25 channel-counts
NPZ and every registered pairs parquet (1M, 1.5M, reserved 2M) are NEVER
content-opened (real-mode tests use a throwaway temporary prior stub with
a patched DEV loader, plus synthetic in-memory priors); the real P16
construction root, the real split manifest, the real Stage-A calibration
product, every real evidence root, the 1M same-file pools (TRAIN
0..1199 / VAL 1200..1599 / HOLD 1600..1999, incl. consumed P20C DEV
0..383, P20E DEV 384..767 and P20F DEV 768..1151), the consumed P20H DEV
prefix (1.5M TRAIN 0..383), the consumed P20I DEV segment (1.5M TRAIN
384..767), the consumed P20J DEV segment (1.5M TRAIN 768..1151) and the
reserved 2M file are never touched.
Focused tests use their own fresh seeds ``2026092251..2026092257`` and
never the frozen P20K tag master 2026092250 (nor the P20J master
2026092240, the P20I master 2026092230, the P20H master 2026092220, the
P20G master 2026092210, the P20F master 2026092200, the P20E master
2026092100, the P20C master 2026092090, the P20B master 2026092080, the
P19 master 2026092060, the P18 master 2026092050, the P16/P17 streams,
nor any prior/probe seed) for real scoring.

The frozen N=32768 makes real SC calls too slow for runner tests, so
runner tests patch the documented ``run_operational_block`` and
``run_oracle_control_block`` seams with scripted deterministic fakes;
tables, formation, transform, NLL scoring, gates, accounting and
checkpointing all run for real. Carried-over inputs (same base K/caps/
prior-reuse rule, pinned against the P20J module read-only) plus the
single deliberate delta (the frozen +512 L1 order-prefix step,
K1 319 -> 831 on the SAME frozen P16 L1 order) are asserted literally,
the single +512 L1 step is asserted as a single-step disclosure
differential (E1 k1=831 on the SAME frozen L1 order object as E0,
key-bit delta exactly +2560), and the fail-closed sextuple gate
(cross-file source-tag+digest gate against the 1M full pool and the
reserved 2M file first, then the intra-file DEV-vs-VAL/HOLD overlap
gate, then the consumed-P20H-DEV exclusion gate, then the
consumed-P20I-DEV exclusion gate, then the consumed-P20J-DEV
exclusion gate, then the calibration-identity digest gate) is asserted
to refuse before any SC call, with zero protected opens and the 2M
file never touched. Every ``test_*`` takes no arguments, uses plain
asserts and restores any monkeypatched module attribute in a
``finally``.
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
    l1_dose_512_1p5m as pe,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l1_dose_escalation_1p5m as p20j,  # read-only prior-reuse/population carry-over reference
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
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    per_session_calibration as psc,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never any frozen master/stream/probe seed.
TEST_SEEDS = (2026092251, 2026092252, 2026092253, 2026092254)
TEST_MASTER = 2026092255
TEST_SPARES = (2026092256, 2026092257)

FROZEN_BASE_LEAKAGE = 34119  # 5 * 6811 + 64 (E0 base operational)
FROZEN_E1_LEAKAGE = 36679  # 5 * 7323 + 64 (E1, +512 L1)
FROZEN_CONTROL_LEAKAGE = 32524  # 5 * 6492 + 64 (oracle arm)
FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63
TOTAL_KEY_BITS = 3 * FROZEN_BASE_LEAKAGE + 3 * FROZEN_E1_LEAKAGE + 3 * FROZEN_CONTROL_LEAKAGE  # 309966
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
    prior, dev = pe._PRIOR_CONTENT_LOADED, pe._DEV_PARQUET_CONTENT_OPENED
    try:
        yield
    finally:
        pe._PRIOR_CONTENT_LOADED = prior
        pe._DEV_PARQUET_CONTENT_OPENED = dev


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def injected_counts(seed: int = TEST_SEEDS[0]) -> np.ndarray:
    """Sparse V25-like 1024x1024 count matrix feeding synthetic priors."""
    rng = np.random.default_rng(seed)
    counts = np.zeros((1024, 1024), dtype=np.float64)
    cols = np.repeat(np.arange(1024), 2)
    rows = rng.integers(0, 1024, size=2048)
    counts[rows, cols] = rng.integers(1, 500, size=2048)
    extra = rng.choice(1024, size=497, replace=False)
    counts[extra, extra] += rng.integers(1, 500, size=extra.size)
    counts = counts * 4.0
    return counts / counts.sum() * 262144.0


def make_prior(counts: np.ndarray) -> dict:
    """Synthetic Stage-A-style prior dict via the frozen §3 program."""
    arrays = psc.build_prior_arrays(counts)
    digest = psc.canonical_prior_digest(arrays)
    return {
        "arrays": dict(arrays),
        "digest": digest,
        "h1": float(arrays["h1"]),
        "h2": float(arrays["h2"]),
        "h_total": float(arrays["h_total"]),
    }


def prior_kwargs(seed: int = TEST_SEEDS[0]) -> dict:
    """Injected-prior call kwargs (arrays + matching expected literals).

    Tests reaching prior verification must additionally patch
    ``pe.FROZEN_PRIOR_DIGEST`` to the synthetic digest (see full_run).
    """
    prior = make_prior(injected_counts(seed))
    return {
        "prior": prior["arrays"],
        "expected_literals": (prior["h1"], prior["h2"], prior["h_total"]),
    }


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
    if tamper == "train-frames":
        per[source]["frames"]["train"] = 1659
    elif tamper == "train-pairs":
        per[source]["pairs"]["train"] = 424959
    elif tamper == "val-frames":
        per[source]["frames"]["val"] = 552
    elif tamper == "hold-frames":
        per[source]["frames"]["hold"] = 553
    elif tamper == "schema":
        schema = "nbldpc_v25_split_manifest_v2"
    elif tamper == "missing-source":
        per = {"type2_1M_20260121_184040": per[source]}
    path = Path(directory) / name
    path.write_text(json.dumps({"schema": schema, "per_source": per}), encoding="utf-8")
    return path


def injected_dev_table(*, frames=384, first_frame=1152, per_frame=256,
                       seed=TEST_SEEDS[1], extras=True):
    """Deterministic TRAIN-like pairs frame; shuffled rows, extra non-DEV rows.

    Carries the DEV pool (1152..1535) plus the declared never-used remainder
    (1536..1659, counted but never decoded); ``extras=True`` adds one frame
    per intra-file forbidden pool (1.5M VAL 1660, 1.5M HOLD 2213) plus one
    frame of the consumed P20H DEV prefix (frame 0), one frame of the
    consumed P20I DEV segment (frame 384) and one frame of the consumed
    P20J DEV segment (frame 768), present in the file but never selected.
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
    rem_frames = np.repeat(np.arange(1536, 1660), per_frame)
    rem = pd.DataFrame({
        "frame_id": rem_frames,
        "pair_idx": np.tile(np.arange(per_frame), 124),
        "alice_symbol": rng.integers(0, 1024, size=rem_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=rem_frames.size),
    })
    df = pd.concat([df, rem], ignore_index=True)
    if extras:
        # Frames outside the DEV pool, one per forbidden pool (1.5M VAL,
        # 1.5M HOLD, consumed P20H/P20I/P20J DEV): present in the file but
        # never selected.
        extra = pd.DataFrame({
            "frame_id": np.repeat([1660, 2213, 0, 384, 768], per_frame),
            "pair_idx": np.tile(np.arange(per_frame), 5),
            "alice_symbol": rng.integers(0, 1024, size=5 * per_frame),
            "bob_symbol": rng.integers(0, 1024, size=5 * per_frame),
        })
        df = pd.concat([df, extra], ignore_index=True)
    return df.sample(frac=1.0, random_state=int(seed)).reset_index(drop=True)


def mutate_dev(df, how):
    out = df.copy()
    if how == "drop-frame":
        out = out[out["frame_id"] != 1200]
    elif how == "pair-gap":
        row = out[(out["frame_id"] == 1152) & (out["pair_idx"] == 255)].index[0]
        out.loc[row, "pair_idx"] = 254
    elif how == "symbol-range":
        row = out[out["frame_id"] == 1152].index[0]
        out.loc[row, "bob_symbol"] = 1024
    elif how == "no-dev":
        out = out[out["frame_id"].isin([1660, 2213])]
    elif how == "drop-remainder-frame":
        out = out[out["frame_id"] != 1600]
    elif how == "shrink-remainder":
        out = out[~((out["frame_id"] == 1659) & (out["pair_idx"] == 255))]
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
    """Scripted fake for the accepted ``run_operational_block`` seam (E0 + E1).

    One shared seam serves both operational arms; the arm is identified by
    the disclosed ``k1`` (319 base vs 831 +512 step) and the frozen L1
    order object identity is recorded to pin the order-prefix extension
    (isomorphic with the K2 rule); the frozen L2 order identity is
    recorded too (K2 stays base on every arm).
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
    """Scripted fake for the ``run_oracle_control_block`` (E2) seam."""

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
            "arm": "E2_true_l1_diagnostic", "outcome": outcome,
            "block_index": int(kwargs["block_index"]), "tag_fn": kwargs.get("tag_fn"),
        })
        return pe.OracleControlResult(
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
            provenance=pe.ORACLE_PROVENANCE,
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
    prior = make_prior(counts)
    if dev is None:
        dev = injected_dev_table()
    s0 = FakeOperationalArm(s0_scripts)
    s2 = FakeControl(s2_scripts)
    kw = dict(
        prior=prior["arrays"],
        dev_table=dev,
        expected_literals=(prior["h1"], prior["h2"], prior["h_total"]),
        construction=str(fab_path),
        construction_digest=fab_hex,
        manifest_path=str(man_path),
        out_dir=Path(out),
    )
    kw.update(over)
    with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
        with patched(pe, "FROZEN_PRIOR_DIGEST", prior["digest"]):
            with patched(pe, "run_operational_block", s0):
                with patched(pe, "run_oracle_control_block", s2):
                    run = pe.run_l1_dose_512_1p5m(**kw)
    return run, s0, s2


# ---- frozen constants, arm table and fresh seeds ----

def test_frozen_constants_and_arm_table_pinned():
    assert pe.FROZEN_N == 32768
    assert (pe.FROZEN_K1, pe.FROZEN_K2, pe.FROZEN_K_TOTAL) == (319, 6492, 6811)
    assert pe.FROZEN_FLOOR == 1e-15
    assert pe.FROZEN_L1_DELTA_K1 == 512
    assert pe.FROZEN_K1_E1 == 831
    assert pe.FROZEN_K_TOTAL_E1 == 7323
    assert pe.FROZEN_E1_KEY_BIT_DELTA == 2560
    assert pe.FROZEN_DEV_FRAME_RANGE == (1152, 1535)
    assert pe.FROZEN_DEV_FRAMES == 384
    assert pe.FROZEN_DEV_PAIRS == 98304
    assert pe.FROZEN_BLOCK_RANGES == ((1152, 1279), (1280, 1407), (1408, 1535))
    assert pe.FROZEN_REMAINDER_FRAME_RANGE == (1536, 1659)
    assert pe.FROZEN_REMAINDER_FRAMES == 124
    assert pe.FROZEN_REMAINDER_SYMBOLS == 31744
    assert pe.FROZEN_MANIFEST_TRAIN_FRAMES == 1660
    assert pe.FROZEN_MANIFEST_TRAIN_PAIRS == 424960
    assert pe.FROZEN_MANIFEST_VAL_FRAMES == 553
    assert pe.FROZEN_MANIFEST_VAL_PAIRS == 141568
    assert pe.FROZEN_MANIFEST_HOLD_FRAMES == 554
    assert pe.FROZEN_MANIFEST_HOLD_PAIRS == 141824
    assert pe.INTRA_FILE_VAL_FRAME_RANGE == (1660, 2212)
    assert pe.INTRA_FILE_HOLD_FRAME_RANGE == (2213, 2766)
    assert pe.P20H_DEV_FRAME_RANGE == (0, 383)
    assert pe.P20I_DEV_FRAME_RANGE == (384, 767)
    assert pe.P20J_DEV_FRAME_RANGE == (768, 1151)
    assert pe.FROZEN_SOURCE == "1p5M"
    assert pe.FROZEN_SOURCE_TAG == "type2_1p5M_20260121_183806"
    assert pe.FROZEN_DEV_PAIRS_PATH == (
        "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
        "v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet")
    assert pe.FROZEN_DEV_PAIRS_SIZE == 1869178
    assert pe.FROZEN_DEV_PAIRS_SHA256 == (
        "ca351e5205e76600530121066af4e0e1e5278061745c0797368a49443570a06b")
    assert pe.REFUSED_2M_DEV_PAIRS_PATH.endswith(
        "type2_2M_20260121_183657/pairs.parquet")
    assert pe.REFUSED_1M_DEV_PAIRS_PATH == hm.FROZEN_HOLD_PAIRS_PATH
    assert pe.FROZEN_TAG_MASTER == 2026092250
    assert pe.SEED_PREFIX == "nbpolar-p20k-l1-dose-512-1p5m-seed"
    assert pe.FROZEN_LAMBDA == 137.3823795883264
    assert pe.FROZEN_PRIOR_DIGEST == (
        "e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b")
    assert pe.FROZEN_CAL_H1 == 2.006647056368773
    assert pe.FROZEN_CAL_H2 == 1.9017235959286112
    assert pe.FROZEN_CAL_H_TOTAL == 3.908370652297384
    assert pe.FROZEN_PRIOR_PATH == (
        ".workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/"
        "per_session_calibration/calibrated_prior.npz")
    assert pe.PLANNED_SC_CALLS == 15
    assert pe.PLANNED_TAG_INVOCATIONS == 9
    assert pe.PLANNED_RECORDS == 9
    assert pe.FROZEN_LEAKAGE_BITS == FROZEN_BASE_LEAKAGE
    assert pe.FROZEN_E1_LEAKAGE_BITS == FROZEN_E1_LEAKAGE
    assert pe.FROZEN_CONTROL_LEAKAGE_BITS == FROZEN_CONTROL_LEAKAGE
    assert pe.FROZEN_TOTAL_KEY_DEPENDENT_BITS == TOTAL_KEY_BITS
    assert pe.FROZEN_TOTAL_PUBLIC_CONTROL_BITS == TOTAL_PUBLIC_BITS
    assert abs(pe.FROZEN_LEAKAGE_BITS / pe.FROZEN_RAW_INPUT_BITS - 0.1041229248046875) < 1e-12
    assert abs(pe.FROZEN_E1_LEAKAGE_BITS / pe.FROZEN_RAW_INPUT_BITS - 0.1119354248046875) < 1e-12
    pin = pe.check_frozen_arm_table()
    assert pin["l1_delta_k1"] == 512
    assert pin["e1_k1"] == 831
    assert pin["e1_key_bit_delta_vs_base"] == 2560
    assert pin["cap_vs_raw_ratio"] < 0.5
    assert pin["e1_cap_vs_raw_ratio"] < 0.5
    cal_pin = pe.check_frozen_calibration_pins()
    assert cal_pin["lambda"] == 137.3823795883264
    assert cal_pin["prior_digest"] == pe.FROZEN_PRIOR_DIGEST
    assert cal_pin["h_total"] == pe.FROZEN_CAL_H_TOTAL
    assert "--dev-frames 1152 1535" in pe.FROZEN_COMMAND
    assert "--remainder-frames 1536 1659" in pe.FROZEN_COMMAND
    assert "--tag-master 2026092250" in pe.FROZEN_COMMAND
    assert "--source 1p5M" in pe.FROZEN_COMMAND
    assert "--prior" in pe.FROZEN_COMMAND
    assert "--counts" not in pe.FROZEN_COMMAND
    assert "type2_1p5M_20260121_183806/pairs.parquet" in pe.FROZEN_COMMAND
    assert "calibrated_prior.npz" in pe.FROZEN_COMMAND
    assert "l1_dose_512_1p5m" in pe.FROZEN_COMMAND
    assert "--dev-frames 384 767" not in pe.FROZEN_COMMAND
    assert "--dev-frames 768 1151" not in pe.FROZEN_COMMAND
    assert "--remainder-frames 1152 1659" not in pe.FROZEN_COMMAND
    assert "--tag-master 2026092240" not in pe.FROZEN_COMMAND
    with patched(pe, "FROZEN_K1_E1", 830):
        assert_raises_match(ValueError, "512", pe.check_frozen_arm_table)
    with patched(pe, "FROZEN_E1_LEAKAGE_BITS", 36678):
        assert_raises_match(ValueError, "drifted", pe.check_frozen_arm_table)


def test_zero_tuning_carry_over_from_p20j():
    # Every carried-over input is byte-identical with the P20J module
    # (read-only reference): base K values, base/oracle caps, N, floor,
    # the digest-pinned prior reuse (path/digest/lambda/literals), tag
    # shape, budgets, gate order, provenance and outcome identity. Only
    # the single-factor L1 step, the new-segment population and the new
    # tag domain may differ.
    assert pe.FROZEN_N == p20j.FROZEN_N == 32768
    assert pe.FROZEN_FLOOR == p20j.FROZEN_FLOOR == 1e-15
    assert (pe.FROZEN_K1, pe.FROZEN_K2, pe.FROZEN_K_TOTAL) == (
        p20j.FROZEN_K1, p20j.FROZEN_K2, p20j.FROZEN_K_TOTAL) == (319, 6492, 6811)
    assert pe.FROZEN_LEAKAGE_BITS == p20j.FROZEN_LEAKAGE_BITS == 34119
    assert pe.FROZEN_CONTROL_LEAKAGE_BITS == p20j.FROZEN_CONTROL_LEAKAGE_BITS == 32524
    assert pe.FROZEN_PUBLIC_CONTROL_BITS == p20j.FROZEN_PUBLIC_CONTROL_BITS == 327743
    assert pe.FROZEN_RAW_INPUT_BITS == p20j.FROZEN_RAW_INPUT_BITS == 327680
    assert pe.PLANNED_SC_CALLS == p20j.PLANNED_SC_CALLS == 15
    assert pe.PLANNED_TAG_INVOCATIONS == p20j.PLANNED_TAG_INVOCATIONS == 9
    assert pe.PLANNED_RECORDS == p20j.PLANNED_RECORDS == 9
    assert pe.OPERATIONAL_PROVENANCE == p20j.OPERATIONAL_PROVENANCE
    assert pe.ORACLE_PROVENANCE == p20j.ORACLE_PROVENANCE
    assert pe.OUTCOMES == p20j.OUTCOMES
    # The prior-reuse freeze is carried over byte-identical (R1): the
    # same Stage-A product, digest, lambda/floor pins and literals, and
    # the same gate order including the calibration-identity gate.
    assert pe.FROZEN_PRIOR_PATH == p20j.FROZEN_PRIOR_PATH
    assert pe.FROZEN_PRIOR_DIGEST == p20j.FROZEN_PRIOR_DIGEST == (
        "e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b")
    assert pe.FROZEN_LAMBDA == p20j.FROZEN_LAMBDA == 137.3823795883264
    assert (pe.FROZEN_CAL_H1, pe.FROZEN_CAL_H2, pe.FROZEN_CAL_H_TOTAL) == (
        p20j.FROZEN_CAL_H1, p20j.FROZEN_CAL_H2, p20j.FROZEN_CAL_H_TOTAL)
    assert pe.SUPPORT_RULE == p20j.SUPPORT_RULE
    assert pe.INTEGRITY_GATE_ORDER == p20j.INTEGRITY_GATE_ORDER
    assert "calibration_identity" in pe.INTEGRITY_GATE_ORDER
    # The factor swap: P20K discloses +512 L1 (E1 K1=831, K2 stays base)
    # where P20J disclosed +256 L1 (D1 K1=575, K2 stayed base).
    assert pe.FROZEN_L1_DELTA_K1 == 512
    assert pe.FROZEN_K1_E1 == 831
    assert pe.FROZEN_K_TOTAL_E1 == 7323
    assert pe.FROZEN_E1_KEY_BIT_DELTA == 2560
    assert pe.FROZEN_E1_LEAKAGE_BITS == 36679
    assert p20j.FROZEN_L1_DELTA_K1 == 256
    assert p20j.FROZEN_K1_D1 == 575
    assert p20j.FROZEN_K_TOTAL_D1 == 7067
    assert p20j.FROZEN_D1_KEY_BIT_DELTA == 1280
    assert p20j.FROZEN_D1_LEAKAGE_BITS == 35399
    assert not hasattr(pe, "FROZEN_K1_D1")
    assert not hasattr(p20j, "FROZEN_K1_E1")
    assert pe.FROZEN_TOTAL_KEY_DEPENDENT_BITS == TOTAL_KEY_BITS == 309966
    assert p20j.FROZEN_TOTAL_KEY_DEPENDENT_BITS == 306126
    assert pe.FROZEN_TOTAL_KEY_DEPENDENT_BITS != p20j.FROZEN_TOTAL_KEY_DEPENDENT_BITS
    assert pe.FROZEN_TOTAL_PUBLIC_CONTROL_BITS == p20j.FROZEN_TOTAL_PUBLIC_CONTROL_BITS
    assert pe.FROZEN_ARM_NAMES != p20j.FROZEN_ARM_NAMES
    assert pe.FROZEN_ARM_NAMES == ("E0_sc_base", "E1_L1plus512", "E2_true_l1_diagnostic")
    assert p20j.FROZEN_ARM_NAMES == ("D0_sc_base", "D1_L1plus", "D2_true_l1_diagnostic")
    assert pe.DISCLOSURE_RULE != p20j.DISCLOSURE_RULE
    assert "831" in pe.DISCLOSURE_RULE
    # The deliberate deltas: new-segment population + new tag domain only.
    assert pe.FROZEN_SOURCE == p20j.FROZEN_SOURCE == "1p5M"
    assert pe.FROZEN_DEV_FRAME_RANGE != p20j.FROZEN_DEV_FRAME_RANGE
    assert pe.FROZEN_BLOCK_RANGES != p20j.FROZEN_BLOCK_RANGES
    assert pe.FROZEN_REMAINDER_FRAME_RANGE != p20j.FROZEN_REMAINDER_FRAME_RANGE
    assert pe.P20H_DEV_FRAME_RANGE == p20j.P20H_DEV_FRAME_RANGE == (0, 383)
    assert pe.P20I_DEV_FRAME_RANGE == p20j.P20I_DEV_FRAME_RANGE == (384, 767)
    assert not hasattr(p20j, "P20J_DEV_FRAME_RANGE")
    assert pe.P20J_DEV_FRAME_RANGE == (768, 1151)
    assert pe.FROZEN_TAG_MASTER != p20j.FROZEN_TAG_MASTER
    assert pe.SEED_PREFIX != p20j.SEED_PREFIX
    assert pe.PROTOCOL_NAME != p20j.PROTOCOL_NAME
    assert pe.COMPLETE_LABEL != p20j.COMPLETE_LABEL


def test_fresh_test_seeds_disjoint_from_all_frozen_seeds():
    frozen = (
        set(opf.FROZEN_DEV_SEEDS) | set(opf.FROZEN_TRAIN_SEEDS)
        | {hm.FROZEN_TAG_MASTER, hb.FROZEN_TAG_MASTER, p20j.FROZEN_TAG_MASTER,
           pe.FROZEN_TAG_MASTER}
    )
    for seed in (2026092050, 2026092060,
                 2026092070, 2026092071, 2026092072, 2026092073,
                 2026092074, 2026092075, 2026092076,
                 2026092080, 2026092081, 2026092082, 2026092083,
                 2026092084, 2026092085, 2026092086, 2026092087,
                  2026092090, 2026092091, 2026092092, 2026092093,
                  2026092094, 2026092095, 2026092096, 2026092097,
                  2026092100, 2026092101, 2026092102, 2026092103,
                  2026092104, 2026092105, 2026092106, 2026092107,
                  2026092200, 2026092201, 2026092202, 2026092203,
                  2026092204, 2026092205, 2026092206, 2026092207,
                  2026092210, 2026092211, 2026092212, 2026092213,
                  2026092214, 2026092215, 2026092216, 2026092217,
                  2026092220, 2026092221, 2026092222, 2026092223,
                  2026092224, 2026092225, 2026092226, 2026092227,
                  2026092230, 2026092231, 2026092232, 2026092233,
                  2026092234, 2026092235, 2026092236, 2026092237,
                  2026092240, 2026092241, 2026092242, 2026092243,
                  2026092244, 2026092245, 2026092246, 2026092247):
        frozen.add(seed)
    for prior in (2026091650, 2026091680, 2026091710, 2026091820, 2026091860,
                  2026091930, 2026091940, 2026091960, 2026091970, 2026091980,
                  2026091990, 2026091800, 2026091811, 2026091753, 2026091760):
        frozen.add(prior)
    assert set(TEST_SEEDS).isdisjoint(frozen)
    assert set(TEST_SPARES).isdisjoint(frozen)
    assert TEST_MASTER not in TEST_SEEDS + TEST_SPARES
    assert pe.FROZEN_TAG_MASTER not in TEST_SEEDS + TEST_SPARES + (TEST_MASTER,)
    assert pe.FROZEN_TAG_MASTER not in (2026092050, 2026092060, 2026092080,
                                        2026092090, 2026092210, 2026092220,
                                        2026092230, 2026092240, p20j.FROZEN_TAG_MASTER)
    assert pe.FROZEN_TAG_MASTER != hm.FROZEN_TAG_MASTER
    assert pe.FROZEN_TAG_MASTER != hb.FROZEN_TAG_MASTER
    assert pe.FROZEN_TAG_MASTER != p20j.FROZEN_TAG_MASTER


def test_accepted_helpers_shared_not_reimplemented():
    assert pe.run_operational_block is opf.run_operational_block
    assert pe.run_oracle_control_block is hb.run_oracle_control_block
    assert pe.OracleControlResult is hb.OracleControlResult
    assert pe._decode_layer is opf._decode_layer
    assert pe.classify_operational_outcome is opf.classify_operational_outcome
    assert pe.verify_predecessor_construction.__module__.endswith(
        "operational_f13_replication")
    assert pe.verify_split_manifest is hm.verify_split_manifest
    assert pe.holdout_nll_bits is hm.holdout_nll_bits
    assert pe.raw_symbol_error_rate is hm.raw_symbol_error_rate
    assert pe.polar_transform_fn.__module__.endswith("transform")
    assert pe.make_gf32_fn.__module__.endswith("algebra")
    assert pe.toeplitz_tag_fn.__module__.endswith("shared")
    assert pe.build_p1_metrics_fn.__module__.endswith("prior")
    assert pe.gather_p2_metrics_fn.__module__.endswith("prior")
    assert pe.probs_to_symbol_metric_fn.__module__.endswith("prior")
    assert pe.load_calibrated_prior.__module__.endswith("per_session_calibration")
    assert pe.load_pairs_table.__module__.endswith("pairs_loader")
    assert not hasattr(pe, "load_v25_channel_counts"), "no NPZ loader in Stage B"
    for banned in ("sample_full_block", "block_genie_risks", "select_empirical_split",
                   "budget_k_total", "analytic_order", "wilson_lower_bound",
                   "recovery_gates", "select_label", "backoff_seed_bits",
                   "holdout_seed_bits", "operational_seed_bits", "list_decode",
                   "fwht", "belief_provenance", "smooth_joint_to_conditional",
                   "run_search_block", "build_search_candidates",
                   "FROZEN_SEARCH_BOUND_M", "NEIGHBORHOOD_ID", "SEARCH_RULE",
                   "rescores_used", "search_found_better", "selected_source",
                   "channel_counts", "counts_path", "_NPZ_CONTENT_OPENED",
                   "v25_npz", "EXPECTED_H1", "EXPECTED_H2"):
        assert not hasattr(pe, banned), banned
    # The accepted HOLD formation is range-pinned: DEV ranges are refused,
    # which justifies the local P20K formation with identical semantics.
    assert_raises_match(ValueError, "hold-frames",
                         hm.form_holdout_blocks, injected_dev_table(),
                         hold_frames=(1152, 1535), block_frames=128,
                         remainder_frames=(1536, 1659))
    # The accepted split-manifest helper is source-pinned to 1M: the 1p5M
    # source is refused, which justifies the local P20K manifest check
    # with identical semantics.
    with tempfile.TemporaryDirectory() as tmp:
        man = make_manifest(tmp)
        assert_raises_match(ValueError, "source=",
                            hm.verify_split_manifest, man, source="1p5M")


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
            with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pe, "load_calibrated_prior", forbidden_loader):
                    with patched(pe, "load_pairs_table", forbidden_loader):
                        with patched(pe, "run_operational_block", forbidden_arm):
                            with patched(pe, "run_oracle_control_block", forbidden_control):
                                assert_raises_match(
                                    ValueError, "predecessor construction identity",
                                    pe.run_l1_dose_512_1p5m,
                                    dev_table=injected_dev_table(), **prior_kwargs(),
                                    construction=str(fab_path), construction_digest=fab_hex,
                                    manifest_path=str(man), out_dir=root,
                                )
            assert not root.exists()
        fab_path, fab_hex = make_construction_file(tmp_path)
        bad_flag = ("0" if fab_hex[0] != "0" else "1") + fab_hex[1:]
        assert_raises_match(
            ValueError, "digest flag != frozen digest",
            pe.run_l1_dose_512_1p5m,
            dev_table=injected_dev_table(), **prior_kwargs(),
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
        assert_raises_match(FileNotFoundError, "not found", pe.verify_dev_manifest,
                            str(tmp_path / "absent.json"))
        for idx, tamper in enumerate(("train-frames", "train-pairs", "val-frames",
                                      "hold-frames", "schema", "missing-source")):
            man = make_manifest(tmp_path, tamper=tamper, name=f"bad{idx}.json")
            assert_raises_match(ValueError, "manifest identity",
                                pe.verify_dev_manifest, man, source="1p5M")
            root = tmp_path / f"out{idx}"
            with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pe, "load_calibrated_prior", forbidden_loader):
                    with patched(pe, "load_pairs_table", forbidden_loader):
                        assert_raises_match(
                            ValueError, "manifest identity",
                            pe.run_l1_dose_512_1p5m,
                            dev_table=injected_dev_table(), **prior_kwargs(),
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
            ("FROZEN_BLOCK_RANGES", ((1152, 1278), (1279, 1406), (1407, 1534))),
        ):
            with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pe, field, value):
                    with patched(pe, "load_calibrated_prior", forbidden_loader):
                        with patched(pe, "load_pairs_table", forbidden_loader):
                            assert_raises_match(
                                ValueError, "DEV block-range identity",
                                pe.run_l1_dose_512_1p5m,
                                dev_table=injected_dev_table(), **prior_kwargs(),
                                construction=str(fab_path), construction_digest=fab_hex,
                                manifest_path=str(good), out_dir=root,
                            )
        assert not root.exists()
        for field, value, substr in (
            ("FROZEN_REMAINDER_FRAME_RANGE", (1537, 1659), "remainder_frame_range"),
            ("FROZEN_DEV_FRAME_RANGE", (1152, 1536), "dev_frame_range"),
            ("P20H_DEV_FRAME_RANGE", (0, 382), "p20h_dev_range"),
            ("P20I_DEV_FRAME_RANGE", (384, 766), "p20i_dev_range"),
            ("P20J_DEV_FRAME_RANGE", (768, 1150), "p20j_dev_range"),
        ):
            with patched(pe, field, value):
                assert_raises_match(ValueError, substr, pe.verify_dev_block_identity)


def test_sextuple_gate_source_first_then_val_then_hold_then_p20h_dev_then_p20i_dev_then_p20j_dev():
    # Cross-file source gate first: the 1M full-pool path, the reserved
    # 2M path and any foreign path refuse before any root exists, with
    # zero protected opens. The 2M path is a refusal string only: the
    # reserved file is never opened, statted, or read here.
    source_pin = pe.verify_dev_source_identity()
    assert source_pin["verified"] is True
    assert source_pin["source"] == "1p5M"
    assert source_pin["source_tag"] == "type2_1p5M_20260121_183806"
    assert source_pin["dev_pairs_size_bytes"] == 1869178
    assert source_pin["dev_pairs_sha256"] == (
        "ca351e5205e76600530121066af4e0e1e5278061745c0797368a49443570a06b")
    assert_raises_match(ValueError, "1M full-pool path refused",
                        pe.verify_dev_source_identity,
                        pe.REFUSED_1M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "reserved 2M path refused",
                        pe.verify_dev_source_identity,
                        pe.REFUSED_2M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "dev-pairs=",
                        pe.verify_dev_source_identity, "other/dir/pairs.parquet")
    assert pe._PRIOR_CONTENT_LOADED is False
    assert pe._DEV_PARQUET_CONTENT_OPENED is False
    # Intra-file gate second: DEV ranges must overlap NONE of the 1.5M
    # VAL/HOLD frame sets (VAL checked first, then HOLD).
    pin = pe.verify_dev_block_identity()
    assert pin["verified"] is True
    assert pin["intra_val_disjoint"] is True
    assert pin["intra_hold_disjoint"] is True
    assert pin["p20h_dev_disjoint"] is True
    assert pin["p20i_dev_disjoint"] is True
    assert pin["p20j_dev_disjoint"] is True
    assert pin["intra_file_val_frame_range"] == [1660, 2212]
    assert pin["intra_file_hold_frame_range"] == [2213, 2766]
    assert pin["p20h_dev_frame_range"] == [0, 383]
    assert pin["p20i_dev_frame_range"] == [384, 767]
    assert pin["p20j_dev_frame_range"] == [768, 1151]
    # Any DEV block touching the 1.5M VAL set refuses first.
    with patched(pe, "FROZEN_BLOCK_RANGES", ((1152, 1279), (1280, 1407), (1660, 1787))):
        assert_raises_match(ValueError, "overlaps 1.5M VAL",
                            pe.verify_dev_block_identity)
    with patched(pe, "FROZEN_REMAINDER_FRAME_RANGE", (1536, 1660)):
        assert_raises_match(ValueError, "remainder overlaps 1.5M VAL",
                            pe.verify_dev_block_identity)
    # A remainder overlapping VAL and HOLD reports the VAL set first.
    with patched(pe, "FROZEN_REMAINDER_FRAME_RANGE", (1536, 2213)):
        assert_raises_match(ValueError, "1.5M VAL",
                            pe.verify_dev_block_identity)
    # Any DEV block touching the 1.5M HOLD set refuses second.
    with patched(pe, "FROZEN_BLOCK_RANGES", ((1152, 1279), (1280, 1407), (2213, 2340))):
        assert_raises_match(ValueError, "overlaps 1.5M HOLD",
                            pe.verify_dev_block_identity)
    with patched(pe, "FROZEN_REMAINDER_FRAME_RANGE", (2213, 2340)):
        assert_raises_match(ValueError, "remainder overlaps 1.5M HOLD",
                            pe.verify_dev_block_identity)
    # P20H-DEV exclusion gate third: DEV ranges must overlap NONE of the
    # consumed P20H DEV prefix 0..383.
    with patched(pe, "FROZEN_BLOCK_RANGES", ((0, 127), (1152, 1279), (1280, 1407))):
        assert_raises_match(ValueError, "consumed P20H DEV",
                            pe.verify_dev_block_identity)
    with patched(pe, "FROZEN_REMAINDER_FRAME_RANGE", (0, 383)):
        assert_raises_match(ValueError, "remainder overlaps consumed P20H DEV",
                            pe.verify_dev_block_identity)
    # P20I-DEV exclusion gate fourth: DEV ranges must overlap NONE of the
    # consumed P20I DEV segment 384..767.
    with patched(pe, "FROZEN_BLOCK_RANGES", ((384, 511), (1152, 1279), (1280, 1407))):
        assert_raises_match(ValueError, "consumed P20I DEV",
                            pe.verify_dev_block_identity)
    with patched(pe, "FROZEN_REMAINDER_FRAME_RANGE", (384, 767)):
        assert_raises_match(ValueError, "remainder overlaps consumed P20I DEV",
                            pe.verify_dev_block_identity)
    # P20J-DEV exclusion gate fifth: DEV ranges must overlap NONE of the
    # consumed P20J DEV segment 768..1151.
    with patched(pe, "FROZEN_BLOCK_RANGES", ((768, 895), (1152, 1279), (1280, 1407))):
        assert_raises_match(ValueError, "consumed P20J DEV",
                            pe.verify_dev_block_identity)
    with patched(pe, "FROZEN_REMAINDER_FRAME_RANGE", (768, 1151)):
        assert_raises_match(ValueError, "remainder overlaps consumed P20J DEV",
                            pe.verify_dev_block_identity)
    # A block touching both P20H DEV and VAL reports the VAL set first
    # (intra-file gate runs before the P20H-DEV exclusion gate).
    with patched(pe, "FROZEN_BLOCK_RANGES", ((0, 127), (1280, 1407), (1660, 1787))):
        assert_raises_match(ValueError, "overlaps 1.5M VAL",
                            pe.verify_dev_block_identity)
    # A block touching both P20I DEV and VAL reports the VAL set first
    # (intra-file gate runs before the P20I-DEV exclusion gate).
    with patched(pe, "FROZEN_BLOCK_RANGES", ((384, 511), (1280, 1407), (1660, 1787))):
        assert_raises_match(ValueError, "overlaps 1.5M VAL",
                            pe.verify_dev_block_identity)
    # A block touching both P20J DEV and VAL reports the VAL set first
    # (intra-file gate runs before the P20J-DEV exclusion gate).
    with patched(pe, "FROZEN_BLOCK_RANGES", ((768, 895), (1280, 1407), (1660, 1787))):
        assert_raises_match(ValueError, "overlaps 1.5M VAL",
                            pe.verify_dev_block_identity)
    # A block touching both P20J DEV and P20I DEV reports the P20I set
    # first (P20I-DEV exclusion runs before the P20J-DEV exclusion gate).
    with patched(pe, "FROZEN_BLOCK_RANGES", ((384, 511), (768, 895), (1280, 1407))):
        assert_raises_match(ValueError, "consumed P20I DEV",
                            pe.verify_dev_block_identity)
    # Run level: CLI-covered range drift trips the frozen-flag refusal
    # before any root exists.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for over, substr in (
            ({"dev_frames": (1153, 1536)}, "dev-frames"),
            ({"dev_frames": (1152, 1536)}, "dev-frames"),
            ({"dev_frames": (768, 1151)}, "dev-frames"),
            ({"remainder_frames": (1537, 1659)}, "remainder-frames"),
            ({"source": "1M"}, "source="),
            ({"source": "2M"}, "source="),
            ({"dev_pairs": pe.REFUSED_1M_DEV_PAIRS_PATH}, "1M full-pool"),
            ({"dev_pairs": pe.REFUSED_2M_DEV_PAIRS_PATH}, "reserved 2M"),
            ({"dev_pairs": "other/dir/pairs.parquet"}, "dev-pairs="),
        ):
            root = tmp_path / f"gate{abs(hash(substr + str(over))) % 100000}"
            with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, substr, pe.run_l1_dose_512_1p5m,
                    dev_table=injected_dev_table(), **prior_kwargs(),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=root, **over,
                )
            assert not root.exists()


# ---- deterministic slicing ----

def test_dev_slicing_blocks_and_remainder_exact():
    formation = pe.form_dev_blocks(injected_dev_table())
    assert formation["dev_frame_range"] == [1152, 1535]
    assert formation["dev_frames"] == 384
    assert formation["dev_pairs"] == 98304
    assert formation["block_ranges"] == [[1152, 1279], [1280, 1407], [1408, 1535]]
    assert [b["frame_start"] for b in formation["blocks"]] == [1152, 1280, 1408]
    assert all(len(b["bob"]) == 32768 for b in formation["blocks"])
    assert formation["remainder"]["frames"] == 124
    assert formation["remainder"]["symbols"] == 31744
    assert formation["remainder"]["used"] is False
    val_first, val_last = pe.INTRA_FILE_VAL_FRAME_RANGE
    hold_first, hold_last = pe.INTRA_FILE_HOLD_FRAME_RANGE
    p20h_first, p20h_last = pe.P20H_DEV_FRAME_RANGE
    p20i_first, p20i_last = pe.P20I_DEV_FRAME_RANGE
    p20j_first, p20j_last = pe.P20J_DEV_FRAME_RANGE
    for start, end in formation["block_ranges"]:
        assert end < val_first or start > val_last
        assert end < hold_first or start > hold_last
        assert end < p20h_first or start > p20h_last
        assert end < p20i_first or start > p20i_last
        assert end < p20j_first or start > p20j_last


def test_malformed_dev_population_run_level_blocked_five_files():
    prior = make_prior(injected_counts())
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for idx, how in enumerate(("drop-frame", "pair-gap", "symbol-range", "no-dev")):
            root = tmp_path / f"bad{idx}"
            with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pe, "FROZEN_PRIOR_DIGEST", prior["digest"]):
                    assert_raises_match(
                        ValueError, "BLOCKED(dev_population_exact)",
                        pe.run_l1_dose_512_1p5m,
                        prior=prior["arrays"],
                        dev_table=mutate_dev(injected_dev_table(), how),
                        expected_literals=(prior["h1"], prior["h2"], prior["h_total"]),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=root,
                    )


def test_declared_remainder_measured_and_fail_closed():
    # The never-used remainder is counted from the pool (never decoded):
    # a damaged remainder blocks with the remainder gate, never success.
    prior = make_prior(injected_counts())
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for idx, how in enumerate(("drop-remainder-frame", "shrink-remainder")):
            root = tmp_path / f"rem{idx}"
            with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pe, "FROZEN_PRIOR_DIGEST", prior["digest"]):
                    assert_raises_match(
                        ValueError, "BLOCKED(blocks_exact_with_declared_remainder)",
                        pe.run_l1_dose_512_1p5m,
                        prior=prior["arrays"],
                        dev_table=mutate_dev(injected_dev_table(), how),
                        expected_literals=(prior["h1"], prior["h2"], prior["h_total"]),
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
        with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(pe, "_PRIOR_CONTENT_LOADED", True):
                with patched(pe, "load_calibrated_prior", forbidden_loader):
                    assert_raises_match(
                        ValueError, "reload refused",
                        pe.run_l1_dose_512_1p5m,
                        prior=None, dev_table=injected_dev_table(),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=tmp_path / "o1",
                    )
            with patched(pe, "_DEV_PARQUET_CONTENT_OPENED", True):
                with patched(pe, "load_pairs_table", forbidden_loader):
                    assert_raises_match(
                        ValueError, "reopen refused",
                        pe.run_l1_dose_512_1p5m,
                        **prior_kwargs(), dev_table=None,
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=tmp_path / "o2",
                    )
        assert not (tmp_path / "o1").exists()
        assert not (tmp_path / "o2").exists()
    assert pe._PRIOR_CONTENT_LOADED is False
    assert pe._DEV_PARQUET_CONTENT_OPENED is False


def test_no_fitting_or_sampling_tokens_and_exact_call_counts():
    source = Path(pe.__file__).read_text(encoding="utf-8")
    for token in ("np.random.default_rng", "random_state", "sample_full_block",
                  "block_genie_risks", "list_decode", "fwht(", "posterior_APP",
                  "smooth_joint", "wilson_lower_bound", "results/",
                  "outputs_comparison", "git commit", "git push"):
        assert token not in source, token
    assert re.search(r"\bSCL\b", source) is None, "SCL"
    for token in ("l1_dose_512_seed_bits", "form_dev_blocks", "l1_prefix_positions",
                  "l2_prefix_positions",
                  "candidate_nll_bits", "raw_floor_diagnostics",
                  "frozen-order-prefix-extension", "MemoryError",
                  "resource_abort", "oracle_isolation_ok"):
        assert token in source, token
    assert source.count("except MemoryError") >= 2
    assert source.count("raise  # resource stop owns MemoryError") >= 2
    assert pe.PLANNED_SC_CALLS == 15
    assert pe.PLANNED_TAG_INVOCATIONS == 9


# ---- arms, disclosure differential, accounting ----

def test_three_arm_semantics_k_leakage_labels_and_call_counts():
    with tempfile.TemporaryDirectory() as tmp:
        run, s0, s2 = full_run(Path(tmp) / "out")
        assert len(run.records) == 9
        assert run.summary["records_completed"] == 9
        assert run.summary["sc_calls"] == 15
        assert run.summary["tag_invocations"] == 9
        assert run.summary["aggregates"]["arms"]["E0_sc_base"]["key_dependent_bits"] == 3 * 34119
        assert run.summary["aggregates"]["arms"]["E1_L1plus512"]["key_dependent_bits"] == 3 * 36679
        assert run.summary["aggregates"]["arms"]["E2_true_l1_diagnostic"]["key_dependent_bits"] == 3 * 32524
        assert run.summary["aggregates"]["operational"]["key_dependent_bits"] == 3 * 34119 + 3 * 36679
        assert run.summary["aggregates"]["operational"]["public_control_bits"] == 6 * 327743
        assert run.summary["outcome_label"] == pe.COMPLETE_LABEL
        assert run.summary["integrity_all_pass"] is True
        assert len(s0.seen) == 6 and len(s2.seen) == 3
        # Slot order is block-major E0/E1/E2; every arm ran on every block.
        assert sorted(r["block_index"] for r in run.records
                      if r["arm"] == "E1_L1plus512") == [0, 1, 2]
        # The single-factor differential: E1 discloses exactly +512 L1
        # symbols on the SAME frozen L1 order object as E0, with K2 at
        # base on every arm.
        e0_calls = [c for c in s0.seen if c["k1"] == 319]
        e1_calls = [c for c in s0.seen if c["k1"] == 831]
        assert len(e0_calls) == 3 and len(e1_calls) == 3
        assert {c["k2"] for c in s0.seen} == {6492}
        assert {c["l1_order_id"] for c in s0.seen} == {s0.seen[0]["l1_order_id"]}
        assert {c["l2_order_id"] for c in s0.seen} == {s0.seen[0]["l2_order_id"]}
        for record in run.records:
            if record["arm"] == "E1_L1plus512":
                assert record["l1_prefix_len"] == 831
                assert record["l2_prefix_len"] == 6492
                assert record["l1_delta_k1_applied"] == 512
                assert record["l1_disclosure_rule"] == "frozen-order-prefix-extension"
                assert record["key_bit_delta_vs_base"] == 2560
            elif record["arm_kind"] == "operational":
                assert record["l1_prefix_len"] == 319
                assert record["l2_prefix_len"] == 6492
                assert record["l1_delta_k1_applied"] == 0
                assert record["l1_disclosure_rule"] == "base"
                assert record["key_bit_delta_vs_base"] == 0


def test_e1_restored_differential_is_descriptive_and_complete():
    # E0 fails block 0 while E1 restores it: the differential is recorded
    # descriptively and the label stays COMPLETE (no threshold).
    scripts = ["verify_failed", "exact"] + ["exact"] * 4
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out", s0_scripts=scripts)
        recovery = run.summary["aggregates"]["recovery"]
        assert recovery["e1_restored_count"] == 1
        assert recovery["disclosure_blocks"][0]["e1_restored_given_e0_failed"] is True
        assert recovery["disclosure_blocks"][1]["e1_restored_given_e0_failed"] is False
        assert run.summary["outcome_label"] == pe.COMPLETE_LABEL
        assert run.summary["integrity_all_pass"] is True


def test_incremental_k_arithmetic_exact():
    assert 5 * (319 + 6492) + 64 == 34119
    assert 5 * (831 + 6492) + 64 == 36679
    assert 36679 - 34119 == 2560
    assert 2560 == 5 * 512
    assert 5 * 6492 + 64 == 32524
    assert 10 * 32768 + 63 == 327743
    assert 3 * 34119 + 3 * 36679 + 3 * 32524 == TOTAL_KEY_BITS == 309966
    assert 3 * 34119 + 3 * 36679 == 212394  # operational
    assert 3 * 32524 == 97572  # oracle
    assert 9 * 327743 == TOTAL_PUBLIC_BITS


def test_p20k_seed_domain_arm_block_separation():
    seeds = {}
    for arm in pe.FROZEN_ARM_NAMES:
        for block in range(3):
            seed = pe.l1_dose_512_seed_bits(TEST_MASTER, 32768, arm, block)
            assert seed.shape == (327743,)
            seeds[(arm, block)] = seed.tobytes()
    assert len(set(seeds.values())) == 9
    for prefix in ("nbpolar-p16-operational-f13-seed",
                    "nbpolar-p17-operational-replication-seed",
                    "nbpolar-p18-holdout-microcheck-seed",
                    "nbpolar-p19-holdout-backoff-diagnostic-seed",
                    "nbpolar-p20b-bounded-search-diagnostic-seed",
                    "nbpolar-p20c-l2-disclosure-backoff-seed",
                     "nbpolar-p20e-plus1024-confirmation-seed",
                     "nbpolar-p20f-plus1024-extension-seed",
                     "nbpolar-p20g-independent-session-seed",
                     "nbpolar-p20h-per-session-calibration-seed",
                     "nbpolar-p20i-l1-disclosure-1p5m-seed",
                     "nbpolar-p20j-l1-dose-escalation-1p5m-seed"):
        assert prefix != pe.SEED_PREFIX
    assert pe.SEED_PREFIX == "nbpolar-p20k-l1-dose-512-1p5m-seed"
    assert p20j.SEED_PREFIX == "nbpolar-p20j-l1-dose-escalation-1p5m-seed"
    assert pe.FROZEN_TAG_MASTER not in (hm.FROZEN_TAG_MASTER, hb.FROZEN_TAG_MASTER,
                                        p20j.FROZEN_TAG_MASTER, 2026092210, 2026092220,
                                        2026092230, 2026092240)
    assert_raises_match(ValueError, "unknown frozen arm",
                         pe.l1_dose_512_seed_bits, TEST_MASTER, 32768, "E0", 0)


def test_oracle_isolation_control_excluded_from_operational_aggregates():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        assert pe.oracle_isolation_ok(run.records, final=True) is True
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
        assert set(recovery) == {"per_arm", "e1_restored_count", "disclosure_blocks"}
        assert set(recovery["per_arm"]) == set(pe.FROZEN_ARM_NAMES)


def test_counts_buckets_and_recount_exact_and_tamper():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        events = []
        for record in run.records:
            spec = pe.ARM_BY_NAME[record["arm"]]
            events.extend(pe.l1_dose_512_block_events(
                32768, spec, record["block_index"], record["frame_start"], record))
        recount = pe.l1_dose_512_recount_events(events)
        assert recount["key_dependent_bits"] == TOTAL_KEY_BITS
        assert recount["public_control_bits"] == TOTAL_PUBLIC_BITS
        assert recount["tag_invocations"] == 9
        assert recount["event_types"] == {
            "l1_disclosure": 6, "l2_disclosure": 9, "verification_tag": 9}
        tampered = [dict(event) for event in events]
        tampered[0] = dict(tampered[0], key_dependent_bits=int(tampered[0]["key_dependent_bits"]) + 1)
        assert pe.l1_dose_512_recount_events(tampered)["key_dependent_bits"] != TOTAL_KEY_BITS
        bad_arm = [dict(event) for event in events]
        bad_arm[0] = dict(bad_arm[0], event_id="block-32768-0-nope-l1-disclosure")
        assert_raises_match(ValueError, "N/arm-tagged",
                            pe.l1_dose_512_recount_events, bad_arm)
        bad_type = [dict(event) for event in events]
        bad_type[0] = dict(bad_type[0], event_type="l3_disclosure")
        assert_raises_match(ValueError, "not frozen",
                            pe.l1_dose_512_recount_events, bad_type)


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
    assert pe.OUTCOMES == ("exact", "undetected", "verify_failed",
                           "decode_failed", "nonfinite", "resource_abort")


def test_no_threshold_labels_all_recovery_patterns():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(Path(tmp) / "out")
        assert run.summary["outcome_label"] == pe.COMPLETE_LABEL
        assert pe.l1_dose_512_1p5m_label(
            {name: True for name in pe.INTEGRITY_GATE_ORDER}) == pe.COMPLETE_LABEL
        gates = {name: True for name in pe.INTEGRITY_GATE_ORDER}
        gates["undetected_zero"] = False
        assert pe.l1_dose_512_1p5m_label(gates) == "BLOCKED(undetected_zero)"


def test_undetected_record_blocks_with_earliest_gate():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _ = full_run(
            Path(tmp) / "out", s0_scripts=["undetected"] + ["exact"] * 5)
        assert run.summary["records_completed"] == 9
        assert run.summary["outcome_label"] == "BLOCKED(undetected_zero)"
        assert run.summary["integrity"]["undetected_zero"] is False


def test_budget_stop_abort_fill_and_precedence():
    prior = make_prior(injected_counts())
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_dir = tmp_path / "fab"
        fab_dir.mkdir(parents=True, exist_ok=True)
        fab_path, fab_hex = make_construction_file(fab_dir)
        man_path = make_manifest(tmp_path)
        s0 = FakeOperationalArm()
        s2 = FakeControl()
        with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(pe, "FROZEN_PRIOR_DIGEST", prior["digest"]):
                with patched(pe, "run_operational_block", s0):
                    with patched(pe, "run_oracle_control_block", s2):
                        run = pe.run_l1_dose_512_1p5m(
                            prior=prior["arrays"], dev_table=injected_dev_table(),
                            expected_literals=(prior["h1"], prior["h2"], prior["h_total"]),
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
    prior = make_prior(injected_counts())
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_dir = tmp_path / "fab"
        fab_dir.mkdir(parents=True, exist_ok=True)
        fab_path, fab_hex = make_construction_file(fab_dir)
        man_path = make_manifest(tmp_path)
        s0 = FakeOperationalArm(["exact", "memory_error"] + ["exact"] * 4)
        s2 = FakeControl()
        with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(pe, "FROZEN_PRIOR_DIGEST", prior["digest"]):
                with patched(pe, "run_operational_block", s0):
                    with patched(pe, "run_oracle_control_block", s2):
                        try:
                            pe.run_l1_dose_512_1p5m(
                                prior=prior["arrays"], dev_table=injected_dev_table(),
                                expected_literals=(prior["h1"], prior["h2"],
                                                   prior["h_total"]),
                                construction=str(fab_path), construction_digest=fab_hex,
                                manifest_path=str(man_path), out_dir=tmp_path / "out",
                            )
                        except pe.L1Dose512_1p5mResourceError as err:
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


def test_calibration_identity_failure_blocked_no_sc_call():
    # A prior whose digest differs from the Stage-A pin refuses before any
    # SC call (calibration identity); wrong expected literals refuse the
    # same way (target population contract on the calibrated population).
    prior = make_prior(injected_counts())
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_dir = tmp_path / "fab"
        fab_dir.mkdir(parents=True, exist_ok=True)
        fab_path, fab_hex = make_construction_file(fab_dir)
        man_path = make_manifest(tmp_path)
        s0 = FakeOperationalArm()
        s2 = FakeControl()
        with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(pe, "run_operational_block", s0):
                with patched(pe, "run_oracle_control_block", s2):
                    assert_raises_match(
                        ValueError, "prior_digest_mismatch",
                        pe.run_l1_dose_512_1p5m,
                        prior=prior["arrays"], dev_table=injected_dev_table(),
                        expected_literals=(prior["h1"], prior["h2"], prior["h_total"]),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man_path), out_dir=tmp_path / "out",
                    )
        assert s0.seen == [] and s2.seen == []
        with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(pe, "FROZEN_PRIOR_DIGEST", prior["digest"]):
                with patched(pe, "run_operational_block", s0):
                    with patched(pe, "run_oracle_control_block", s2):
                        assert_raises_match(
                            ValueError, "h1_matches_literal",
                            pe.run_l1_dose_512_1p5m,
                            prior=prior["arrays"], dev_table=injected_dev_table(),
                            expected_literals=(0.1, 0.1, 0.2),
                            construction=str(fab_path), construction_digest=fab_hex,
                            manifest_path=str(man_path), out_dir=tmp_path / "out2",
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
        assert sorted(p.name for p in out.iterdir()) == sorted(pe.OUTPUT_FILES)
        for name in ("frozen_plan.json", "input_and_predecessor_identity.json",
                     "aggregate_summary.json"):
            walk_keys(json.loads((out / name).read_text(encoding="utf-8")))
        records = [json.loads(line) for line in
                   (out / "per_block_arm_outcomes.jsonl").read_text().splitlines()]
        assert len(records) == 9
        for record in records:
            walk_keys(record)
            assert pe.record_dict_consistent(record, n=32768)
            assert isinstance(record["resources"], dict)
        report = (out / "report.md").read_text(encoding="utf-8")
        for token in ("high_hat", "low_hat", "label_hat", "logp", "seed_bits",
                      "l1_order", "array("):
            assert token not in report, token
        summary = json.loads((out / "aggregate_summary.json").read_text(encoding="utf-8"))
        assert summary["records_completed"] == 9
        assert summary["attempt_read_accounting"]["attempts_consumed_by_this_run"] == 0
        assert summary["attempt_read_accounting"]["counts_content_opens"] == 0
        assert summary["attempt_read_accounting"]["prior_content_loads"] == 0
        assert summary["attempt_read_accounting"]["dev_content_opens"] == 0


def test_real_mode_accounting_with_patched_loaders():
    with restored_open_guards():
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fab_path, fab_hex = make_construction_file(tmp_path)
            man = make_manifest(tmp_path)
            prior = make_prior(injected_counts())
            stub_prior = tmp_path / "calibrated_prior.npz"
            with open(stub_prior, "wb") as fh:
                np.savez(fh, **prior["arrays"])
            stub_parquet = tmp_path / "pairs.parquet"
            stub_parquet.write_bytes(b"stub")
            dev = injected_dev_table()

            def fake_pairs(path):
                assert str(path).endswith("pairs.parquet")
                return dev

            with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pe, "FROZEN_PRIOR_DIGEST", prior["digest"]):
                    with patched(pe, "FROZEN_DEV_PAIRS_PATH", str(stub_parquet)):
                        with patched(pe, "FROZEN_DEV_PAIRS_SIZE", 4):
                            with patched(pe, "load_pairs_table", fake_pairs):
                                with patched(pe, "run_operational_block", FakeOperationalArm()):
                                    with patched(pe, "run_oracle_control_block", FakeControl()):
                                        run = pe.run_l1_dose_512_1p5m(
                                            prior_path=str(stub_prior),
                                            dev_pairs=str(stub_parquet),
                                            expected_literals=(prior["h1"], prior["h2"],
                                                               prior["h_total"]),
                                            construction=str(fab_path),
                                            construction_digest=fab_hex,
                                            manifest_path=str(man),
                                            out_dir=tmp_path / "out",
                                        )
            accounting = run.summary["attempt_read_accounting"]
            assert accounting["counts_content_opens"] == 0
            assert accounting["prior_content_loads"] == 1
            assert accounting["dev_content_opens"] == 1
            assert accounting["attempts_consumed_by_this_run"] == 1
            assert len(accounting["opened_content_paths"]) == 2
            assert run.summary["outcome_label"] == pe.COMPLETE_LABEL


def test_real_mode_stat_change_blocks_with_earliest_gate():
    with restored_open_guards():
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fab_path, fab_hex = make_construction_file(tmp_path)
            man = make_manifest(tmp_path)
            prior = make_prior(injected_counts())
            stub_prior = tmp_path / "calibrated_prior.npz"
            with open(stub_prior, "wb") as fh:
                np.savez(fh, **prior["arrays"])
            stub_parquet = tmp_path / "pairs.parquet"
            stub_parquet.write_bytes(b"stub")
            dev = injected_dev_table()

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

            with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(pe, "FROZEN_PRIOR_DIGEST", prior["digest"]):
                    with patched(pe, "FROZEN_DEV_PAIRS_PATH", str(stub_parquet)):
                        with patched(pe, "FROZEN_DEV_PAIRS_SIZE", 4):
                            with patched(pe, "_stat_record", drifting_stat):
                                with patched(pe, "load_pairs_table", fake_pairs):
                                    with patched(pe, "run_operational_block", FakeOperationalArm()):
                                        with patched(pe, "run_oracle_control_block",
                                                  FakeControl()):
                                            run = pe.run_l1_dose_512_1p5m(
                                                prior_path=str(stub_prior),
                                                dev_pairs=str(stub_parquet),
                                                expected_literals=(prior["h1"], prior["h2"],
                                                                   prior["h_total"]),
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
    parser = pe.build_parser()
    args = parser.parse_args([
        "--prior", "p", "--source", "1p5M", "--floor", "1e-15",
        "--n", "32768", "--k1", "319", "--k2", "6492",
        "--construction", "f", "--construction-digest", "d",
        "--dev-pairs", "p", "--dev-frames", "1152", "1535",
        "--block-frames", "128", "--remainder-frames", "1536", "1659",
        "--tag-master", "2026092250", "--chunk-rows", "512",
        "--tag-bits", "64", "--out-dir", "o",
    ])
    assert args.dev_frames == [1152, 1535]
    assert args.tag_master == 2026092250
    assert args.prior == "p"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for over, substr in (
            ({"k1": 320}, "k1=319"),
            ({"k2": 6493}, "k2=6492"),
            ({"floor": 1e-14}, "floor=1e-15"),
            ({"dev_frames": (1152, 1536)}, "dev-frames"),
            ({"dev_frames": (768, 1151)}, "dev-frames"),
            ({"tag_master": 2026092240}, "tag-master"),
        ):
            root = tmp_path / f"cli{abs(hash(substr)) % 100000}"
            with patched(pe, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, substr, pe.run_l1_dose_512_1p5m,
                    dev_table=injected_dev_table(), **prior_kwargs(),
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
        with patched(pe, "load_calibrated_prior", forbidden_loader):
            assert_raises_match(FileExistsError, "refusing to overwrite",
                                 pe.run_l1_dose_512_1p5m,
                                 dev_table=injected_dev_table(), **prior_kwargs(),
                                 construction="f", construction_digest="d",
                                 manifest_path="m", out_dir=root)


def test_module_required_tokens_and_no_forbidden_paths():
    source = Path(pe.__file__).read_text(encoding="utf-8")
    for token in ("FROZEN_DEV_FRAME_RANGE = (1152, 1535)",
                   "FROZEN_BLOCK_RANGES = ((1152, 1279), (1280, 1407), (1408, 1535))",
                   "FROZEN_REMAINDER_FRAME_RANGE = (1536, 1659)",
                   "P20H_DEV_FRAME_RANGE = (0, 383)",
                   "P20I_DEV_FRAME_RANGE = (384, 767)",
                   "INTRA_FILE_VAL_FRAME_RANGE = (1660, 2212)",
                   "INTRA_FILE_HOLD_FRAME_RANGE = (2213, 2766)",
                   "FROZEN_MANIFEST_TRAIN_FRAMES = 1660",
                   "FROZEN_DEV_PAIRS_SIZE = 1869178",
                   "E1_L1plus512", "E2_true_l1_diagnostic", "E0_sc_base",
                   "deployable", "e1_restored_count", "disclosure_blocks",
                   "l1_delta_k1_applied", "frozen-order-prefix-extension",
                    "key_bit_delta_vs_base", "FROZEN_E1_LEAKAGE_BITS = 36679",
                    "FROZEN_K1_E1 = 831",
                    "P20J_DEV_FRAME_RANGE = (768, 1151)",
                    "FROZEN_TAG_MASTER = 2026092250",
                    "FROZEN_LAMBDA = 137.3823795883264",
                    "FROZEN_PRIOR_DIGEST = \"e8dd078a",
                    "calibration_identity",
                    "nbpolar-p20k-l1-dose-512-1p5m-seed"):
        assert token in source, token
    for token in ("plus1024_per_session_confirmation", "Plus1024PerSessionConfirmation",
                   "plus1024_extension", "Plus1024Extension",
                   "B1_L2plus", "B0_sc_base", "B2_true_l1_diagnostic",
                   "l1_disclosure_1p5m", "L1Disclosure1p5m",
                   "C1_L1plus", "C0_sc_base", "C2_true_l1_diagnostic",
                   "c1_restored", "FROZEN_K1_C1", "FROZEN_C1_", "C1b",
                   "l1_dose_escalation_1p5m", "L1DoseEscalation1p5m",
                   "D1_L1plus", "D0_sc_base", "D2_true_l1_diagnostic",
                   "d1_restored", "FROZEN_K1_D1", "FROZEN_D1_", "D1b",
                   "second L2 step", "S1_bounded_search",
                   "S2_true_l1_diagnostic", "S0_sc_base", "bounded_search",
                   "BoundedSearch", "NEIGHBORHOOD", "rescore", "argmin total NLL",
                   "load_v25_channel_counts", "counts_path", "channel_counts",
                   "_NPZ_CONTENT_OPENED", "v25_npz"):
        assert token not in source, token
    # Exactly one forbidding mention of a second L1 tier; no implementation.
    assert source.count("E1b") == 1


def test_l1_prefix_positions_pin_order_prefix_extension():
    rng = np.random.default_rng(TEST_SEEDS[3])
    order = rng.permutation(32768).astype(np.int64)
    base = pe.l1_prefix_positions(order, 319)
    plus = pe.l1_prefix_positions(order, 831)
    assert base.shape == (319,) and plus.shape == (831,)
    assert np.array_equal(plus[:319], base)  # prefix extension, no reselection
    assert np.array_equal(plus, order[:831])
    assert_raises_match(ValueError, "exceeds", pe.l1_prefix_positions, order, 32769)
    # K2 stays at base on every P20K arm: the L2 prefix helper pins the
    # carried-over base length on the same frozen order.
    assert np.array_equal(pe.l2_prefix_positions(order, 6492), order[:6492])


def test_tiny_real_operational_and_oracle_via_p20k_closure():
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
        seed = pe.l1_dose_512_seed_bits(TEST_MASTER, n, "E0_sc_base", 0,
                                           bit_length=seed_bits_for(n))
        return pe.toeplitz_tag_fn(bits, seed, tag_bits)

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
    cand = pe.candidate_nll_bits(tiny["bob"], tiny["high"], tiny["low"],
                                 tiny["p1"], tiny["p2"])
    assert abs(cand["total_nll_bits"] - nll["total_nll_bits"]) < 1e-9
    first = pe.first_error_coordinate(tiny["high"], tiny["low"],
                                      tiny["high"], tiny["low"])
    assert first == {"first_error_layer": None, "first_error_coord": None}
    wrong = (tiny["low"] + 1) % 32
    first = pe.first_error_coordinate(tiny["high"], wrong, tiny["high"], tiny["low"])
    assert first["first_error_layer"] == "L2"
    assert first["first_error_coord"] == 0


def test_zero_protected_opens_audit():
    assert pe._PRIOR_CONTENT_LOADED is False
    assert pe._DEV_PARQUET_CONTENT_OPENED is False
