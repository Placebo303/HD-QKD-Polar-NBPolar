"""Focused Phase 4-P20T N=8192 persistence-probe tests.

Injected/synthetic counts, priors, artifacts and fresh additive
``workspace/p20t/<uuid>/`` temp roots only. The V25 channel-counts NPZ, every
registered pairs parquet (1M, 1.5M VAL/HOLD/TRAIN, 2M VAL/HOLD), the real P16
construction root, the real split manifest, the accepted P20O worktree
products and every accepted evidence root are NEVER content-opened, statted,
or listed here: the Stage-A reuse verification and the frozen derivation run
only in the authorized ``--verify-derivation`` / ``--derive`` commands,
never in tests. The frozen post-derivation pins (K + digests) are read from
the module (filled at Stage-A close); fixture-level tests patch them to
self-consistent fixture values and never the reverse. Focused tests use
their own fresh seeds ``2026092401..2026092407`` and never the frozen P20T
tag master ``2026092400`` (except through the frozen module constant) nor
the frozen derivation seeds ``2026092410..2026092413`` (except through the
frozen module constant and the allowed grep-rule paths).
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    n8192_persistence_probe_2m as p20t,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_mechanism_probe_2m as p20s,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    per_session_calibration as psc,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    raw_prior_val_1p5m as p20m,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_alt_maintain_2m as p20o,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    empirical_genie_scaling as egs,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never the frozen P20T tag master 2026092400 nor
# the frozen derivation seeds 2026092410..2026092413.
TEST_SEEDS = (2026092401, 2026092402, 2026092403, 2026092404,
              2026092405, 2026092406, 2026092407)

FROZEN_PUBLIC_BITS = 81983  # 10 * 8192 + 63
N = 8192


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
    """One-open guard tests flip flags; restore them afterwards."""
    state = (
        p20t._SESSION_PRIOR_CONTENT_LOADED,
        p20t._DEV_PARQUET_CONTENT_OPENED,
    )
    try:
        yield
    finally:
        (p20t._SESSION_PRIOR_CONTENT_LOADED,
         p20t._DEV_PARQUET_CONTENT_OPENED) = state


@contextlib.contextmanager
def p20t_root():
    """Fresh additive workspace/p20t/<uuid>/ temp root, cleaned afterwards."""
    root = REPO_ROOT / "workspace" / "p20t" / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    assert "workspace" in root.parts and "p20t" in root.parts
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


def sparse_counts(seed: int, cells: int = 2048, hi: int = 50) -> np.ndarray:
    """Sparse 1024x1024 synthetic count matrix (fast; deterministic)."""
    rng = np.random.default_rng(int(seed))
    counts = np.zeros((1024, 1024), dtype=np.float64)
    cols = np.repeat(np.arange(1024), cells // 1024)
    rows = rng.integers(0, 1024, size=cols.size)
    counts[rows, cols] = rng.integers(1, hi, size=cols.size)
    extra = rng.choice(1024, size=197, replace=False)
    counts[extra, extra] += rng.integers(1, hi, size=extra.size)
    return np.ascontiguousarray(counts)


def synthetic_prior_arrays(seed: int = TEST_SEEDS[0]) -> dict:
    """Self-consistent synthetic 2M-shaped prior arrays (no protected data)."""
    counts = sparse_counts(seed)
    counts[0, 0] += 1000.0
    return p20m.build_raw_prior_arrays(counts)


def synthetic_risks(seed: int = TEST_SEEDS[1]):
    """Synthetic length-8192 pooled-risk vectors for the split selection."""
    rng = np.random.default_rng(int(seed))
    return (
        rng.random(N).astype(np.float64),
        (0.5 + rng.random(N)).astype(np.float64),
        rng.random(N).astype(np.float64),
        (0.5 + rng.random(N)).astype(np.float64),
    )


def fixture_k_and_orders(seed: int = TEST_SEEDS[1]):
    """Self-consistent fixture (K1,K2,residual,orders) from the frozen K rule."""
    arrays = synthetic_prior_arrays(seed)
    h_total = float(np.asarray(arrays["h_total"]))
    k_total = int(p20t.budget_k_total(N, h_total, 1.3))
    assert 0 < k_total <= 2 * N
    e1, h1, e2, h2 = synthetic_risks(seed)
    split = egs.select_empirical_split(N, e1, h1, e2, h2, k_total)
    assert int(split["k1"]) + int(split["k2"]) == k_total
    return arrays, h_total, k_total, split


def single_segment_table(*, seed: int = TEST_SEEDS[2]) -> pd.DataFrame:
    """Single-segment HOLD-tail pairs frame: DEV 3595..3626 + remainder + extras."""
    rng = np.random.default_rng(int(seed))
    dev_frames = np.repeat(np.arange(3595, 3627), 256)
    dev = pd.DataFrame({
        "frame_id": dev_frames,
        "pair_idx": np.tile(np.arange(256), 32),
        "alice_symbol": rng.integers(0, 1024, size=dev_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=dev_frames.size),
    })
    rem_frames = np.repeat(np.arange(3627, 3645), 256)
    rem = pd.DataFrame({
        "frame_id": rem_frames,
        "pair_idx": np.tile(np.arange(256), 18),
        "alice_symbol": rng.integers(0, 1024, size=rem_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=rem_frames.size),
    })
    # Extra rows outside the DEV/remainder spans must not influence slicing.
    extra = pd.DataFrame({
        "frame_id": np.repeat([0, 2186, 2187, 2826, 2916, 3555, 3645], 256),
        "pair_idx": np.tile(np.arange(256), 7),
        "alice_symbol": rng.integers(0, 1024, size=7 * 256),
        "bob_symbol": rng.integers(0, 1024, size=7 * 256),
    })
    return pd.concat([dev, rem, extra], ignore_index=True).sample(
        frac=1.0, random_state=int(seed)).reset_index(drop=True)


def full_block_ir_fixture(*, seed: int = TEST_SEEDS[3]):
    """Full-block (N=8192) natural-index truth vectors + tables for the IR recorder."""
    rng = np.random.default_rng(int(seed))
    counts = sparse_counts(seed, cells=1024, hi=20)
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.ascontiguousarray(np.asarray(arrays["p2"], dtype=np.float64))
    n = N
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    order = rng.permutation(n).astype(np.int64)
    view = {"bob": bob, "high": high, "low": low, "u1_cond": high,
            "u2": rng.integers(0, 32, size=n)}
    return counts, p2, view, order


def ir_recorder(view, p2, order, first_error, *, k2, prefix_mean=None):
    k2 = int(k2)
    if prefix_mean is None:
        mask = np.zeros(int(view["bob"].size), dtype=bool)
        mask[np.asarray(order)[:k2]] = True
        hazards = p20o._hazard_bits(
            p2, np.asarray(view.get("u1_cond", view["high"])),
            np.asarray(view["bob"]), np.asarray(view["low"]))
        prefix_mean = float(np.mean(hazards[mask]))
    return p20t._ir_hazard_diagnostics_8192(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error=first_error, prefix_mean=prefix_mean)


def stage_a_fixture(root, *, seed: int = TEST_SEEDS[0]):
    """Self-consistent synthetic construction/orders/spike fixtures + pins.

    Mirrors the frozen derivation shape (K rule -> TRAIN-residual-style
    split -> F-median8 spike -> three JSON docs) with test-local seeds and
    the frozen 16-block/32-genie budget shape in the provenance. Patches
    the module pins to these fixture values (never the reverse).
    """
    arrays, h_total, k_total, split = fixture_k_and_orders(seed)
    k1, k2 = int(split["k1"]), int(split["k2"])
    residual = float(split["residual"])
    l1_order = np.asarray(split["l1_order"], dtype=np.int64)
    l2_order = np.asarray(split["l2_order"], dtype=np.int64)
    rng = np.random.default_rng(seed)
    h2_vec = (0.5 + rng.random(N)).astype(np.float64)
    spike = p20t.derive_spike_order_8192(h2_vec)
    spike_l2 = np.asarray(spike["spike_l2_order"], dtype=np.int64)
    prior_digest = psc.canonical_prior_digest(
        {k: np.asarray(arrays[k]) for k in p20o.RAW_PRIOR_NPZ_KEYS})
    budget_literal = p20m.budget_literal_display(
        h_total, n=N, target_f=1.3)
    derivation = {
        "program": p20t.DERIVATION_PROGRAM_PIN,
        "prior_path": "test-prior",
        "prior_digest": prior_digest,
        "h1": float(np.asarray(arrays["h1"])),
        "h2": float(np.asarray(arrays["h2"])),
        "h_total": h_total,
        "budget_literal": budget_literal,
        "train_seeds": [int(s) for s in p20t.FROZEN_DERIVATION_SEEDS],
        "train_blocks_per_seed": 4,
        "train_blocks_attempted": 16,
        "train_blocks_used": 16,
        "train_impossible": 0,
        "train_genie_calls": 32,
        "provenance_violations": 0,
        "spike_sampling_calls": 0,
        "spike_genie_calls": 0,
        "floor_value": 1e-15,
        "alpha": 1.0,
        "hazard_radius_R": 8,
        "hazard_radius_R_refrozen_for_8192_geometry": True,
        "counts_content_opens": 0,
        "dev_contact": 0,
    }
    construction_doc = {
        "protocol": p20t.CONSTRUCTION_PROTOCOL,
        "kind": p20t.CONSTRUCTION_KIND,
        "n": N,
        "k_total": k_total,
        "k1": k1,
        "k2": k2,
        "train_residual": residual,
        "frozen_before_first_dev": True,
        "derivation": dict(derivation),
    }
    orders_doc = {
        "protocol": p20t.ORDER_PROTOCOL,
        "kind": p20t.ORDER_KIND,
        "n": N,
        "k_total": k_total,
        "k1": k1,
        "k2": k2,
        "l1_order": [int(v) for v in l1_order.tolist()],
        "l2_order": [int(v) for v in l2_order.tolist()],
        "derivation": dict(derivation),
    }
    spike_doc = {
        "protocol": p20t.SPIKE_ORDER_PROTOCOL,
        "kind": p20t.SPIKE_ORDER_KIND,
        "n": N,
        "k_total": k_total,
        "k1": k1,
        "k2": k2,
        "l1_order": [int(v) for v in l1_order.tolist()],
        "l2_order": [int(v) for v in spike_l2.tolist()],
        "derivation": dict(
            derivation,
            reused_prior_digest=prior_digest,
            formula_id=str(p20t.SPIKE_FORMULA_ID),
            formula_text=str(p20t.SPIKE_FORMULA_TEXT),
            cell_convention="TRAIN-pooled mean L2 hazard per 8192-coordinate",
            zero_sampling_attestation=True,
        ),
    }
    construction_path = root / "construction_and_allocation_8192.json"
    construction_path.write_text(
        json.dumps(construction_doc, sort_keys=True) + "\n", encoding="utf-8")
    order_path = root / "fresh_orders_8192.json"
    order_path.write_text(
        json.dumps(orders_doc, sort_keys=True) + "\n", encoding="utf-8")
    spike_path = root / "new_spike_order_8192.json"
    spike_path.write_text(
        json.dumps(spike_doc, sort_keys=True) + "\n", encoding="utf-8")
    pins = {
        "prior_digest": prior_digest,
        "construction_digest": hashlib.sha256(
            construction_path.read_bytes()).hexdigest(),
        "order_digest": hashlib.sha256(order_path.read_bytes()).hexdigest(),
        "spike_order_digest": hashlib.sha256(
            spike_path.read_bytes()).hexdigest(),
        "h1": float(np.asarray(arrays["h1"])),
        "h2": float(np.asarray(arrays["h2"])),
        "h_total": h_total,
        "budget_literal": budget_literal,
        "k_total": k_total,
        "k1": k1,
        "k2": k2,
        "train_residual": residual,
    }
    return arrays, construction_path, order_path, spike_path, pins


def _git_grep_hits(literal: str):
    proc = subprocess.run(
        ["git", "grep", "-l", "--untracked", literal, "--",
         "comparison_bench", "openspec", ".workbuddy", "docs"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1), proc.stderr
    return [line for line in proc.stdout.splitlines() if line.strip()]


# ---- frozen static pins, arms, population (no Stage-A literals) ----

def test_frozen_static_pins_arms_population_and_delta():
    assert p20t.FROZEN_SOURCE == "2M"
    assert p20t.FROZEN_SOURCE_TAG == "type2_2M_20260121_183657"
    assert p20t.FROZEN_N == 8192
    assert p20t.FROZEN_SC_STAGES == 13
    assert p20t.FROZEN_FLOOR == 1e-15
    assert p20t.FROZEN_ALPHA == 1.0
    assert p20t.FROZEN_TARGET_F == 1.3
    assert p20t.FROZEN_HAZARD_R == 8
    # (d2) reuse pins replay the accepted 2M session-H inputs.
    assert p20t.FROZEN_SESSION_PRIOR_DIGEST == p20o.FROZEN_SESSION_PRIOR_DIGEST
    assert (p20t.FROZEN_H1, p20t.FROZEN_H2,
            p20t.FROZEN_H_TOTAL) == (p20o.FROZEN_H1, p20o.FROZEN_H2,
                                     p20o.FROZEN_H_TOTAL)
    # no N=32768 K/order/tag/leakage literal is carried (comparability boundary).
    for literal in (334, 6746, 7080, 327743, 32768):
        assert literal not in (p20t.FROZEN_N, p20t.FROZEN_PUBLIC_CONTROL_BITS)
    assert p20t.FROZEN_PUBLIC_CONTROL_BITS == 81983
    assert p20t.seed_bits_for(8192) == 81983
    # (d1) single-segment population: HOLD tail 3595..3626 -> ONE block.
    assert tuple(p20t.FROZEN_DEV_FRAMES_HOLD) == (3595, 3626)
    assert p20t.FROZEN_DEV_FRAMES == 32
    assert p20t.FROZEN_DEV_PAIRS == 8192
    assert p20t.FROZEN_BLOCK_COUNT == 1
    assert p20t.FROZEN_BLOCK_FRAMES == 32
    assert list(p20t.FROZEN_DEV_FRAME_LIST) == list(range(3595, 3627))
    assert tuple(p20t.FROZEN_REMAINDER_FRAME_RANGE) == (3627, 3644)
    assert p20t.FROZEN_REMAINDER_FRAMES == 18
    assert p20t.FROZEN_REMAINDER_SYMBOLS == 18 * 256
    assert tuple(p20t.FROZEN_1P5M_VAL_STUB_FRAME_RANGE) == (2172, 2212)
    assert tuple(p20t.FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE) == (2725, 2766)
    assert tuple(p20t.FROZEN_BUILD_FRAME_RANGE) == (0, 2186)
    # (d6) new P20T tag domain, disjoint from every predecessor by master+prefix.
    assert p20t.FROZEN_TAG_MASTER == 2026092400
    assert p20t.FROZEN_TAG_MASTER not in (
        p20m.FROZEN_TAG_MASTER, p20o.FROZEN_TAG_MASTER,
        p20s.FROZEN_TAG_MASTER)
    assert not (2026092390 <= p20t.FROZEN_TAG_MASTER <= 2026092399)
    assert p20t.SEED_PREFIX == "nbpolar-p20t-n8192-persistence-2m-seed"
    assert p20t.SEED_PREFIX != p20s.SEED_PREFIX
    # (d5) arms: same K on A/B, carried K2 on O (K checked post-freeze).
    assert p20t.FROZEN_ARM_NAMES == ("A_anchor_frozen_order_equivalent",
                                     "B_spike_local_order",
                                     "O_true_l1_oracle")
    # (d7) derivation seeds follow the P16 4x4 pattern, disjoint from X17/P20S.
    assert tuple(p20t.FROZEN_DERIVATION_SEEDS) == (
        2026092410, 2026092411, 2026092412, 2026092413)
    assert p20t.FROZEN_TRAIN_BLOCKS_PER_SEED == 4
    assert p20t.FROZEN_TRAIN_BLOCKS_TOTAL == 16
    assert p20t.FROZEN_TRAIN_GENIE_CALLS == 32
    for seed in p20t.FROZEN_DERIVATION_SEEDS:
        assert seed not in TEST_SEEDS
        assert not (2026092390 <= seed <= 2026092399)
        assert not (2026092360 <= seed <= 2026092367)
    # (d7/d9) IR pins frozen PRESENT: P20Q-identical IR-1..IR-4 + N=8192 IR-5.
    assert p20t.IR1_BINS == 64
    assert (p20t.IR3_LO_MULT, p20t.IR3_HI_MULT) == (1.0, 2.0)
    assert p20t.IR4_TOPK == 16
    assert p20t.IR5_FULL_N == 8192
    assert p20t.IR5_FORMAT_VERSION == "ir5full-v1"
    assert p20t.IR5_HAZARD_BYTES == 32768
    assert p20t.IR5_FLAG_BYTES == 8192
    assert p20t.IR5_PER_RECORD_BYTES == 49152
    assert p20t.IR5_PER_RECORD_BUDGET_BYTES == 64 * 1024
    assert p20t.IR5_ROOT_BUDGET_BYTES == 1536 * 1024
    assert p20t.IR5_MAX_FILE_BYTES == 2 * 1024 * 1024
    # chunk_rows resized per the P11 precedent (512/4, 64 chunks preserved).
    assert p20t.FROZEN_CHUNK_ROWS == 128
    assert (p20t.FROZEN_N // p20t.FROZEN_CHUNK_ROWS) == 64
    # the delta list is evidenced in the module docstring and the import
    # targets plus the carried-over callsite pattern are referenced.
    source = Path(p20t.__file__).read_text(encoding="utf-8")
    assert "sample_synthetic_train_blocks" in source
    assert "_l2_hazard_diagnostics_8192" in source
    assert "_ir_hazard_diagnostics_8192" in source
    assert "derive_spike_order_8192" in source
    assert "run_derive_stage_a" in source
    assert "no lambda" in source.lower() or "lambda anywhere" in source


def test_stage_a_pins_frozen_k_rule_and_command():
    """Post-freeze pins (K + budget + residual + digests + command)."""
    assert p20t.pins_are_frozen() is True
    pins = p20t._require_stage_a_pins()
    k_total, k1, k2 = pins["k_total"], pins["k1"], pins["k2"]
    assert k1 + k2 == k_total
    assert 0 < k_total <= 2 * N
    # K derived in-packet from recomputed H via the frozen budget rule.
    expect = p20t.budget_k_total(N, float(p20t.FROZEN_H_TOTAL), 1.3)
    assert k_total == expect
    replay = p20m.verify_budget_literal(
        float(p20t.FROZEN_H_TOTAL), k_total, n=N, target_f=1.3)
    assert replay["k_total"] == k_total
    assert pins["budget_literal"].startswith("1.3*8192*")
    assert pins["budget_literal"].endswith(f"= {k_total}")
    assert str(replay["literal"]).rsplit("=", 1)[1].strip() == str(k_total)
    # never from (334,6746): the totals differ by construction.
    assert (k1, k2) != (334, 6746)
    assert k_total != 7080
    assert np.isfinite(pins["train_residual"])
    totals = p20t.planned_totals(k1, k2)
    assert totals["operational_key_dependent_bits"] == 5 * k_total + 64
    assert totals["oracle_key_dependent_bits"] == 5 * k2 + 64
    assert totals["planned_key_dependent_bits"] == (
        2 * (5 * k_total + 64) + (5 * k2 + 64))
    assert totals["planned_public_control_bits"] == 3 * 81983
    arms = p20t.frozen_arm_table()
    assert tuple(s.name for s in arms) == p20t.FROZEN_ARM_NAMES
    assert p20t.check_frozen_arm_table()["verified"] is True
    # the frozen Stage-B command renders the packet section 10 template.
    assert p20t.FROZEN_COMMAND is not None
    assert "--derive" not in p20t.FROZEN_COMMAND
    assert "--verify-derivation" not in p20t.FROZEN_COMMAND
    assert "--source 2M" in p20t.FROZEN_COMMAND
    assert "--n 8192" in p20t.FROZEN_COMMAND
    assert "--dev-frames-hold 3595 3626" in p20t.FROZEN_COMMAND
    assert "--block-frames 32" in p20t.FROZEN_COMMAND
    assert "--remainder-frames 3627 3644" in p20t.FROZEN_COMMAND
    assert "--tag-master 2026092400" in p20t.FROZEN_COMMAND
    assert "--chunk-rows 128" in p20t.FROZEN_COMMAND
    assert f"--k1 {k1} --k2 {k2}" in p20t.FROZEN_COMMAND
    assert ("--spike-formula " + p20t.SPIKE_FORMULA_ID) in p20t.FROZEN_COMMAND
    assert p20t.SPIKE_FORMULA_ID == (
        "F_MEDIAN8_CARRIED_20260920_H_MINUS_LOCAL_MEDIAN_W8_R8_REFROZEN_8192")
    assert "n8192_persistence_probe_2m" in p20t.FROZEN_COMMAND
    assert p20t.FROZEN_COMMAND.count(p20t.FROZEN_SESSION_PRIOR_DIGEST) == 1
    assert p20t.FROZEN_COMMAND.count(pins["construction_digest"]) == 1
    assert p20t.FROZEN_COMMAND.count(pins["order_digest"]) == 1
    assert p20t.FROZEN_COMMAND.count(pins["spike_order_digest"]) == 1
    assert p20t.FROZEN_OUT_ROOT.endswith(
        "NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/n8192_persistence_probe_2m")


# ---- Stage-A spike derivation (section 3 contract + F-median8 functional) ----

def test_derive_spike_deterministic_permutation():
    rng = np.random.default_rng(TEST_SEEDS[4])
    h = (0.5 + rng.random(N)).astype(np.float64)
    first = p20t.derive_spike_order_8192(h)
    second = p20t.derive_spike_order_8192(h)
    order = first["spike_l2_order"]
    assert order.shape == (N,)
    assert set(order.tolist()) == set(range(N))
    assert np.array_equal(order, second["spike_l2_order"])
    assert first["sampling_calls"] == 0 and first["genie_calls"] == 0
    assert first["hazard_radius_R"] == 8
    assert first["formula_id"] == p20t.SPIKE_FORMULA_ID
    assert first["program"] == p20t.DERIVATION_PROGRAM_PIN
    # any first-K prefix is arm B's disclosed set at identical size.
    assert len(set(order[:1500].tolist())) == 1500


def test_derive_spike_fmedian8_ranking_and_tiebreak():
    # a single hazard spike above its R=8 neighborhood ranks first.
    h = np.full(N, 1.0, dtype=np.float64)
    h[4000] = 10.0
    order = p20t.derive_spike_order_8192(h)["spike_l2_order"]
    assert int(order[0]) == 4000
    scores = p20t.derive_spike_order_8192(h)["spike_scores"]
    assert float(scores[4000]) == pytest.approx(9.0)
    # a flat hazard vector scores all-zero -> ascending tie-break (identity).
    flat = np.full(N, 2.5, dtype=np.float64)
    order_flat = p20t.derive_spike_order_8192(flat)["spike_l2_order"]
    assert np.array_equal(order_flat, np.arange(N, dtype=np.int64))
    # clipped neighborhoods at the block edges stay finite.
    edge = np.full(N, 1.0, dtype=np.float64)
    edge[0] = 5.0
    edge[N - 1] = 5.0
    derived = p20t.derive_spike_order_8192(edge)
    assert set(derived["spike_l2_order"][:2].tolist()) == {0, N - 1}
    assert np.isfinite(derived["spike_medians"]).all()


def test_derive_spike_refusals():
    assert_raises_match(ValueError, "length 8192",
                        p20t.derive_spike_order_8192, np.ones(100))
    bad = np.full(N, 1.0)
    bad[7] = np.inf
    assert_raises_match(ValueError, "finite",
                        p20t.derive_spike_order_8192, bad)


def test_run_derive_stage_a_refusals():
    with p20t_root() as root:
        base = dict(
            prior_path=str(root / "missing.npz"),
            expected_prior_digest=p20t.FROZEN_SESSION_PRIOR_DIGEST,
            out_construction_path=str(root / "c.json"),
            out_orders_path=str(root / "o.json"),
            out_spike_path=str(root / "s.json"))
        assert_raises_match(ValueError, "frozen seeds",
                            p20t.run_derive_stage_a, seeds=(1, 2, 3, 4), **base)
        assert_raises_match(ValueError, "blocks_per_seed",
                            p20t.run_derive_stage_a, blocks_per_seed=3, **base)
        assert_raises_match(ValueError, "n=8192",
                            p20t.run_derive_stage_a, n=32768, **base)
        (root / "c.json").write_text("{}", encoding="utf-8")
        assert_raises_match(FileExistsError, "refusing to overwrite",
                            p20t.run_derive_stage_a, **base)


def test_write_and_verify_stage_a_files():
    with p20t_root() as root:
        arrays, construction_path, order_path, spike_path, pins = \
            stage_a_fixture(root)
        with patched(p20t, "FROZEN_K_TOTAL", pins["k_total"]), \
                patched(p20t, "FROZEN_K1", pins["k1"]), \
                patched(p20t, "FROZEN_K2", pins["k2"]), \
                patched(p20t, "FROZEN_BUDGET_LITERAL", pins["budget_literal"]), \
                patched(p20t, "FROZEN_TRAIN_RESIDUAL", pins["train_residual"]), \
                patched(p20t, "FROZEN_CONSTRUCTION_DIGEST_8192",
                        pins["construction_digest"]), \
                patched(p20t, "FROZEN_ORDER_DIGEST_A_8192",
                        pins["order_digest"]), \
                patched(p20t, "FROZEN_SPIKE_ORDER_DIGEST_B_8192",
                        pins["spike_order_digest"]):
            construction_pin = p20t.verify_construction_file_8192(
                construction_path, expected_digest=pins["construction_digest"],
                expected_prior_digest=pins["prior_digest"],
                expected_k1=pins["k1"], expected_k2=pins["k2"],
                expected_k_total=pins["k_total"])
            assert construction_pin["verified"] is True
            assert construction_pin["train_residual"] == pins["train_residual"]
            order_pin = p20t.verify_fresh_order_file_8192(
                order_path, expected_digest=pins["order_digest"],
                expected_prior_digest=pins["prior_digest"],
                expected_k1=pins["k1"], expected_k2=pins["k2"],
                expected_k_total=pins["k_total"])
            assert order_pin["verified"] is True
            spike_pin = p20t.verify_spike_order_file(
                spike_path, expected_digest=pins["spike_order_digest"],
                expected_prior_digest=pins["prior_digest"],
                frozen_l1_order=np.asarray(order_pin["l1_order"]),
                expected_k1=pins["k1"], expected_k2=pins["k2"],
                expected_k_total=pins["k_total"])
            assert spike_pin["verified"] is True
            assert spike_pin["formula_id"] == p20t.SPIKE_FORMULA_ID
            # refusals: digest/seed/formula/K drift.
            assert_raises_match(ValueError, "frozen Stage-A digest",
                                p20t.verify_construction_file_8192,
                                construction_path, expected_digest="0" * 64,
                                expected_prior_digest=pins["prior_digest"],
                                expected_k1=pins["k1"], expected_k2=pins["k2"],
                                expected_k_total=pins["k_total"])
            assert_raises_match(ValueError, "k1 != replayed K1",
                                p20t.verify_construction_file_8192,
                                construction_path,
                                expected_digest=pins["construction_digest"],
                                expected_prior_digest=pins["prior_digest"],
                                expected_k1=pins["k1"] + 1,
                                expected_k2=pins["k2"] - 1,
                                expected_k_total=pins["k_total"])
            assert_raises_match(ValueError, "carried fresh L1",
                                p20t.verify_spike_order_file,
                                spike_path,
                                expected_digest=pins["spike_order_digest"],
                                expected_prior_digest=pins["prior_digest"],
                                frozen_l1_order=np.asarray(
                                    order_pin["l1_order"]) + 1,
                                expected_k1=pins["k1"], expected_k2=pins["k2"],
                                expected_k_total=pins["k_total"])


def test_order_set_delta_exact():
    with p20t_root() as root:
        _, _, order_path, spike_path, pins = stage_a_fixture(root)
        fresh = np.asarray(json.loads(
            order_path.read_text(encoding="utf-8"))["l2_order"], dtype=np.int64)
        spike = np.asarray(json.loads(
            spike_path.read_text(encoding="utf-8"))["l2_order"], dtype=np.int64)
        delta = p20t.order_set_delta_8192(fresh, spike, pins["k2"])
        assert delta["a_disclosed_size"] == pins["k2"]
        assert delta["b_disclosed_size"] == pins["k2"]
        assert delta["size_delta_b_minus_a"] == 0
        assert (delta["a_minus_b_count"] == delta["b_minus_a_count"]
                == pins["k2"] - delta["intersection_size"])
        assert len(delta["a_minus_b_ranks_in_new_order"]) == delta["a_minus_b_count"]
        assert len(delta["b_minus_a_ranks_in_fresh_order"]) == delta["b_minus_a_count"]
        assert_raises_match(ValueError, "length-8192",
                            p20t.order_set_delta_8192, fresh[:100], spike,
                            pins["k2"])


def test_verify_derivation_positive_and_refusals():
    with p20t_root() as root:
        arrays, construction_path, order_path, spike_path, pins = \
            stage_a_fixture(root)
        with patched(p20t, "FROZEN_K_TOTAL", pins["k_total"]), \
                patched(p20t, "FROZEN_K1", pins["k1"]), \
                patched(p20t, "FROZEN_K2", pins["k2"]), \
                patched(p20t, "FROZEN_BUDGET_LITERAL", pins["budget_literal"]), \
                patched(p20t, "FROZEN_TRAIN_RESIDUAL", pins["train_residual"]), \
                patched(p20t, "FROZEN_CONSTRUCTION_DIGEST_8192",
                        pins["construction_digest"]), \
                patched(p20t, "FROZEN_ORDER_DIGEST_A_8192",
                        pins["order_digest"]), \
                patched(p20t, "FROZEN_SPIKE_ORDER_DIGEST_B_8192",
                        pins["spike_order_digest"]):
            result = p20t.verify_derivation(
                prior=dict(arrays), construction_file=str(construction_path),
                order_file=str(order_path), spike_order_file=str(spike_path),
                prior_digest=pins["prior_digest"],
                construction_digest=pins["construction_digest"],
                order_digest=pins["order_digest"],
                spike_order_digest=pins["spike_order_digest"],
                spike_formula=p20t.SPIKE_FORMULA_ID,
                h1=pins["h1"], h2=pins["h2"], h_total=pins["h_total"],
                k1=pins["k1"], k2=pins["k2"])
            assert result["verified"] is True
            assert result["dev_contact"] == 0
            assert result["set_delta"]["size_delta_b_minus_a"] == 0
            assert result["k_total"] == pins["k_total"]
            assert_raises_match(
                p20t.N8192PersistenceProbeContractError, "formula-id",
                p20t.verify_derivation, prior=dict(arrays),
                construction_file=str(construction_path),
                order_file=str(order_path), spike_order_file=str(spike_path),
                prior_digest=pins["prior_digest"],
                construction_digest=pins["construction_digest"],
                order_digest=pins["order_digest"],
                spike_order_digest=pins["spike_order_digest"],
                spike_formula="WRONG_FORMULA",
                h1=pins["h1"], h2=pins["h2"], h_total=pins["h_total"],
                k1=pins["k1"], k2=pins["k2"])
            assert_raises_match(
                p20t.N8192PersistenceProbeContractError, "k_rule_derived",
                p20t.verify_derivation, prior=dict(arrays),
                construction_file=str(construction_path),
                order_file=str(order_path), spike_order_file=str(spike_path),
                prior_digest=pins["prior_digest"],
                construction_digest=pins["construction_digest"],
                order_digest=pins["order_digest"],
                spike_order_digest=pins["spike_order_digest"],
                spike_formula=p20t.SPIKE_FORMULA_ID,
                h1=pins["h1"], h2=pins["h2"], h_total=pins["h_total"],
                k1=pins["k1"] + 1, k2=pins["k2"] - 1)


def test_cli_mode_refusals(capsys):
    assert p20t.main([]) == 2
    out, err = capsys.readouterr()
    assert "ambiguous invocation refused" in err
    assert p20t.main(["--derive", "--verify-derivation"]) == 2
    out, err = capsys.readouterr()
    assert "never combine" in err
    assert p20t.main(["--derive"]) == 2
    out, err = capsys.readouterr()
    assert "missing required --derive flags" in err
    assert p20t.main(["--derive", "--prior", "p", "--prior-digest", "d",
                      "--out-construction", "c", "--out-orders", "o",
                      "--out-spike", "s", "--k1", "1"]) == 2
    out, err = capsys.readouterr()
    assert "no Stage-B-only flags" in err
    assert p20t.main(["--verify-derivation"]) == 2
    out, err = capsys.readouterr()
    assert "missing required --verify-derivation flags" in err
    assert p20t.main(["--prior", "p", "--source", "2M"]) == 2
    out, err = capsys.readouterr()
    assert "missing required Stage-B flags" in err


def test_single_segment_population_and_gate_family():
    table = single_segment_table()
    formation = p20t.form_single_segment_block(table)
    assert formation["dev_frames"] == 32
    assert formation["dev_pairs"] == 8192
    assert formation["dev_frame_list"] == list(range(3595, 3627))
    assert len(formation["blocks"]) == 1
    block = formation["blocks"][0]
    assert int(block["labels"].size) == 8192
    assert int(block["frame_start"]) == 3595
    assert int(block["frame_end"]) == 3626
    assert formation["remainder"]["frames"] == 18
    assert formation["remainder"]["symbols"] == 4608
    assert formation["remainder"]["used"] is False
    counted = formation["counted_1p5m_never_decoded"]
    assert counted["val_stub_symbols"] == 10496
    assert counted["hold_remainder_symbols"] == 10752
    assert counted["used"] is False
    # gate (a): cross-file identity refuses 1M/1.5M paths by name.
    assert_raises_match(ValueError, "1M full-pool path refused",
                        p20t.verify_dev_source_identity_2m,
                        p20t.REFUSED_1M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "1.5M session path refused",
                        p20t.verify_dev_source_identity_2m,
                        p20t.REFUSED_1P5M_DEV_PAIRS_PATH)
    assert p20t.verify_dev_source_identity_2m()["verified"] is True
    # gate (b): containment refuses TRAIN/VAL-DEV/HOLD-DEV overlap.
    assert p20t.verify_single_segment_containment()["verified"] is True
    assert_raises_match(ValueError, "dev-frames-hold",
                        p20t.verify_single_segment_containment,
                        (3595, 3627), (3627, 3644))
    # gate (g, frame part): the exact 32-frame list rule.
    assert p20t.verify_single_segment_frame_set_identity()["verified"] is True
    # gates (c)-(e): consumed exclusions + S2-ii disjointness.
    exclusions = p20t.verify_consumed_exclusions_single_segment()
    assert exclusions["verified"] is True
    assert exclusions["disjoint"] is True
    assert exclusions["build_frames"] == [0, 2186]
    # formation refusals: wrong frames, malformed columns, bad symbols.
    assert_raises_match(
        p20t.N8192PersistenceProbeContractError, "dev-frames-hold",
        p20t.form_single_segment_block, table,
        dev_frames_hold=(3595, 3625))
    bad = table.copy()
    bad.loc[bad["frame_id"] == 3595, "pair_idx"] = 0
    assert_raises_match(
        p20t.N8192PersistenceProbeContractError, "pair_idx",
        p20t.form_single_segment_block, bad)
    bad_sym = table.copy()
    bad_sym.loc[bad_sym["frame_id"] == 3595, "bob_symbol"] = 1024
    assert_raises_match(
        p20t.N8192PersistenceProbeContractError, "outside",
        p20t.form_single_segment_block, bad_sym)


def test_ir_recorder_formulas_caps_and_nullability():
    with p20t_root() as root:
        _, _, _, _, pins = stage_a_fixture(root)
        k2 = pins["k2"]
        counts, p2, view, order = full_block_ir_fixture()
        with patched(p20t, "FROZEN_K_TOTAL", pins["k_total"]), \
                patched(p20t, "FROZEN_K1", pins["k1"]), \
                patched(p20t, "FROZEN_K2", pins["k2"]), \
                patched(p20t, "FROZEN_BUDGET_LITERAL", pins["budget_literal"]), \
                patched(p20t, "FROZEN_TRAIN_RESIDUAL", pins["train_residual"]), \
                patched(p20t, "FROZEN_CONSTRUCTION_DIGEST_8192",
                        pins["construction_digest"]), \
                patched(p20t, "FROZEN_ORDER_DIGEST_A_8192",
                        pins["order_digest"]), \
                patched(p20t, "FROZEN_SPIKE_ORDER_DIGEST_B_8192",
                        pins["spike_order_digest"]):
            no_fail = {"first_error_layer": None, "first_error_coord": None}
            payload = ir_recorder(view, p2, order, no_fail, k2=k2)
            assert len(payload["ir1_hist_edges_bits"]) == 65
            assert len(payload["ir1_hist_prefix_counts"]) == 64
            assert len(payload["ir1_hist_outside_counts"]) == 64
            assert (sum(payload["ir1_hist_prefix_counts"])
                    + sum(payload["ir1_hist_outside_counts"]) == N)
            assert payload["ir2_first_error_hazard_rank_pct"] is None
            assert payload["ir3_thresh_hi_bits"] == pytest.approx(
                2.0 * payload["ir3_thresh_lo_bits"])
            assert payload["ir3_prefix_above_lo_frac"] == pytest.approx(
                payload["ir3_prefix_above_lo_count"] / k2)
            assert len(payload["ir4_topk_coords"]) == 16
            assert len(payload["ir4_topk_hazard_bits"]) == 16
            assert len(payload["ir4_topk_in_prefix"]) == 16
            assert len(payload["ir4_topk_ranks"]) == 16
            # IR-2 under an L2 failure: rank percentile in [0,1], 1.0 = worst.
            fail = {"first_error_layer": "L2",
                    "first_error_coord": int(order[k2 + 5])}
            payload_fail = ir_recorder(view, p2, order, fail, k2=k2)
            pct = payload_fail["ir2_first_error_hazard_rank_pct"]
            assert pct is not None and 0.0 <= pct <= 1.0
            assert_raises_match(ValueError, "valid natural block symbol index",
                                ir_recorder, view, p2, order,
                                {"first_error_layer": "L2",
                                 "first_error_coord": N + 10}, k2=k2)
            # the gated prefix length is enforced (never 6746).
            assert_raises_match(ValueError, "gated prefix length",
                                ir_recorder, view, p2, order, no_fail, k2=6746)


def test_ir5_arrays_writer_and_manifest_identity():
    with p20t_root() as root:
        _, _, _, _, pins = stage_a_fixture(root)
        k2 = pins["k2"]
        counts, p2, view, order = full_block_ir_fixture()
        field = make_gf32()
        with patched(p20t, "FROZEN_K_TOTAL", pins["k_total"]), \
                patched(p20t, "FROZEN_K1", pins["k1"]), \
                patched(p20t, "FROZEN_K2", pins["k2"]), \
                patched(p20t, "FROZEN_BUDGET_LITERAL", pins["budget_literal"]), \
                patched(p20t, "FROZEN_TRAIN_RESIDUAL", pins["train_residual"]), \
                patched(p20t, "FROZEN_CONSTRUCTION_DIGEST_8192",
                        pins["construction_digest"]), \
                patched(p20t, "FROZEN_ORDER_DIGEST_A_8192",
                        pins["order_digest"]), \
                patched(p20t, "FROZEN_SPIKE_ORDER_DIGEST_B_8192",
                        pins["spike_order_digest"]):
            arrays = p20t._ir5_full_block_arrays_8192(
                view=view, p2_arm=p2, l2_order=order, k2=k2, low_hat=None,
                field=field)
            assert arrays["hazards_f32"].shape == (N,)
            assert arrays["hazards_f32"].dtype == np.dtype("<f4")
            assert arrays["inprefix_u8"].shape == (N,)
            assert arrays["inu_u8"].shape == (N,)
            assert int(arrays["inprefix_u8"].sum()) == k2
            assert int(arrays["inu_u8"].sum()) == 0
            refs = p20t._ir5_full_block_writer_8192(
                out_dir=root, arm_name="A_anchor_frozen_order_equivalent",
                block_index=0, arrays=arrays, order_digest=pins["order_digest"])
            assert refs["ir5_format_version"] == "ir5full-v1"
            assert refs["ir5_total_len"] == 8192
            assert (root / "A_hazard_bits_f32le.bin").stat().st_size == 32768
            assert (root / "A_inprefix_u8.bin").stat().st_size == 8192
            assert (root / "A_inu_u8.bin").stat().st_size == 8192
            assert_raises_match(FileExistsError, "refusing to overwrite",
                                p20t._ir5_full_block_writer_8192,
                                out_dir=root,
                                arm_name="A_anchor_frozen_order_equivalent",
                                block_index=0, arrays=arrays,
                                order_digest=pins["order_digest"])
            assert_raises_match(ValueError, "unknown frozen arm",
                                p20t._ir5_full_block_writer_8192,
                                out_dir=root, arm_name="Z", block_index=0,
                                arrays=arrays, order_digest="x")
            # nine-file manifest identity + tamper refusals need the Stage-A pins.
            manifest = {"format_version": "ir5full-v1", "files": [{
                "file": "A_hazard_bits_f32le.bin",
                "sha256": refs["ir5_hazard_bits_sha256"],
                "shape": [8192], "dtype": "<f4", "endianness": "little",
                "order_identity": pins["order_digest"],
                "arm": "A_anchor_frozen_order_equivalent", "block_index": 0,
                "bytes": 32768, "format_version": "ir5full-v1",
            }]}
            assert_raises_match(ValueError, "exactly nine files",
                                p20t.check_ir5_manifest_identity, root, manifest)


def test_ir_payload_complete_gate():
    with p20t_root() as root:
        arrays, _, _, _, pins = stage_a_fixture(root)
        k2 = pins["k2"]
        counts, p2, view, order = full_block_ir_fixture()
        field = make_gf32()
        no_fail = {"first_error_layer": None, "first_error_coord": None}
        with patched(p20t, "FROZEN_K_TOTAL", pins["k_total"]), \
                patched(p20t, "FROZEN_K1", pins["k1"]), \
                patched(p20t, "FROZEN_K2", pins["k2"]), \
                patched(p20t, "FROZEN_BUDGET_LITERAL", pins["budget_literal"]), \
                patched(p20t, "FROZEN_TRAIN_RESIDUAL", pins["train_residual"]), \
                patched(p20t, "FROZEN_CONSTRUCTION_DIGEST_8192",
                        pins["construction_digest"]), \
                patched(p20t, "FROZEN_ORDER_DIGEST_A_8192",
                        pins["order_digest"]), \
                patched(p20t, "FROZEN_SPIKE_ORDER_DIGEST_B_8192",
                        pins["spike_order_digest"]):
            nine = p20t._nine_scalars_for_arm(
                arm_name="A_anchor_frozen_order_equivalent", block=None,
                view=view, p2_arm=p2, counts_arr=counts, l2_order=order,
                k2=k2, first_error=no_fail, field=field, low_hat=None)
            payload = ir_recorder(view, p2, order, no_fail, k2=k2,
                                  prefix_mean=nine["l2_prefix_hazard_mean_bits"])
            record = dict(nine)
            record.update(payload)
            record.update({
                "outcome": "exact", "arm": "A_anchor_frozen_order_equivalent",
                "first_error_layer": None,
                "ir5_hazard_bits_file": "A_hazard_bits_f32le.bin",
                "ir5_hazard_bits_sha256": "x",
                "ir5_inprefix_file": "A_inprefix_u8.bin",
                "ir5_inprefix_sha256": "x",
                "ir5_inu_file": "A_inu_u8.bin",
                "ir5_inu_sha256": "x",
                "ir5_format_version": "ir5full-v1",
                "ir5_total_len": 8192,
            })
            assert p20t.ir_payload_complete([record]) is True
            assert p20t.hazard_instrumentation_complete([record]) is True
            bad = dict(record)
            bad["ir4_topk_coords"] = bad["ir4_topk_coords"][:15]
            assert p20t.ir_payload_complete([bad]) is False
            tables = p20t.ir_payload_tables([record])
            assert tables["within_n_only"] is True
            assert tables["cross_n_inference"] is False
            assert tables["ir5_full_n"] == 8192
            assert tables["records_completed"] == 1


def test_nine_scalars_arm_specific_digest():
    with p20t_root() as root:
        _, _, _, _, pins = stage_a_fixture(root)
        k2 = pins["k2"]
        counts, p2, view, order = full_block_ir_fixture()
        field = make_gf32()
        no_fail = {"first_error_layer": None, "first_error_coord": None}
        with patched(p20t, "FROZEN_K_TOTAL", pins["k_total"]), \
                patched(p20t, "FROZEN_K1", pins["k1"]), \
                patched(p20t, "FROZEN_K2", pins["k2"]), \
                patched(p20t, "FROZEN_BUDGET_LITERAL", pins["budget_literal"]), \
                patched(p20t, "FROZEN_TRAIN_RESIDUAL", pins["train_residual"]), \
                patched(p20t, "FROZEN_CONSTRUCTION_DIGEST_8192",
                        pins["construction_digest"]), \
                patched(p20t, "FROZEN_ORDER_DIGEST_A_8192",
                        pins["order_digest"]), \
                patched(p20t, "FROZEN_SPIKE_ORDER_DIGEST_B_8192",
                        pins["spike_order_digest"]):
            nine_a = p20t._nine_scalars_for_arm(
                arm_name="A_anchor_frozen_order_equivalent", block=None,
                view=view, p2_arm=p2, counts_arr=counts, l2_order=order,
                k2=k2, first_error=no_fail, field=field, low_hat=None)
            nine_b = p20t._nine_scalars_for_arm(
                arm_name="B_spike_local_order", block=None,
                view=view, p2_arm=p2, counts_arr=counts, l2_order=order,
                k2=k2, first_error=no_fail, field=field, low_hat=None)
            assert nine_a["l2_order_digest"] == pins["order_digest"]
            assert nine_b["l2_order_digest"] == pins["spike_order_digest"]
            assert nine_a["l2_prefix_len"] == k2
            assert nine_a["l2_prefix_hazard_mean_bits"] is not None
            assert nine_a["l2_prefix_floor_frac"] is not None
            for field_name in ("l2_fail_in_prefix", "l2_fail_hazard_bits",
                               "l2_fail_nbhd_mean_bits",
                               "l2_fail_nbhd_floor_frac",
                               "l2_fail_in_prefix_u_domain"):
                assert nine_a[field_name] is None
            assert_raises_match(ValueError, "unknown frozen arm",
                                p20t._nine_scalars_for_arm, arm_name="Z",
                                block=None, view=view, p2_arm=p2,
                                counts_arr=counts, l2_order=order, k2=k2,
                                first_error=no_fail, field=field, low_hat=None)


def test_truth_isolation_ir_recording_only():
    with p20t_root() as root:
        _, _, _, _, pins = stage_a_fixture(root)
        k2 = pins["k2"]
        counts, p2, view, order = full_block_ir_fixture()
        with patched(p20t, "FROZEN_K_TOTAL", pins["k_total"]), \
                patched(p20t, "FROZEN_K1", pins["k1"]), \
                patched(p20t, "FROZEN_K2", pins["k2"]), \
                patched(p20t, "FROZEN_BUDGET_LITERAL", pins["budget_literal"]), \
                patched(p20t, "FROZEN_TRAIN_RESIDUAL", pins["train_residual"]), \
                patched(p20t, "FROZEN_CONSTRUCTION_DIGEST_8192",
                        pins["construction_digest"]), \
                patched(p20t, "FROZEN_ORDER_DIGEST_A_8192",
                        pins["order_digest"]), \
                patched(p20t, "FROZEN_SPIKE_ORDER_DIGEST_B_8192",
                        pins["spike_order_digest"]):
            no_fail = {"first_error_layer": None, "first_error_coord": None}
            before_keys = set(view.keys())
            before_bob = np.asarray(view["bob"]).copy()
            ir_recorder(view, p2, order, no_fail, k2=k2)
            # the recorder never mutates its truth inputs.
            assert set(view.keys()) == before_keys
            assert np.array_equal(np.asarray(view["bob"]), before_bob)
            # recording responds to truth (it records truth) while the
            # disclosed-prefix structure stays order-determined.
            view2 = dict(view)
            view2["bob"] = (np.asarray(view["bob"]) + 1) % 1024
            out1 = ir_recorder(view, p2, order, no_fail, k2=k2)
            out2 = ir_recorder(view2, p2, order, no_fail, k2=k2)
            assert out1["ir1_hist_prefix_counts"] != out2["ir1_hist_prefix_counts"]
            assert out1["ir1_hist_edges_bits"] == out2["ir1_hist_edges_bits"]


def test_derivation_sampling_chain_smoke():
    """The frozen sampling -> split -> spike chain runs at N=8192 (test seeds)."""
    arrays = synthetic_prior_arrays(TEST_SEEDS[5])
    sampled = p20m.sample_synthetic_train_blocks(
        np.asarray(arrays["p_b"]), np.asarray(arrays["f_raw"]),
        np.asarray(arrays["p1"]), np.asarray(arrays["p2"]),
        seeds=(TEST_SEEDS[5], TEST_SEEDS[6]), blocks_per_seed=2, n=N)
    assert int(sampled["blocks_attempted"]) == 4
    assert int(sampled["blocks_used"]) == 4
    assert int(sampled["calls"].get("genie", 0)) == 8
    assert int(sampled["provenance_violations"]) == 0
    for key in ("e1_mean", "h1_mean", "e2_mean", "h2_mean"):
        assert np.asarray(sampled[key]).shape == (N,)
    h_total = float(np.asarray(arrays["h_total"]))
    k_total = int(p20t.budget_k_total(N, h_total, 1.3))
    split = egs.select_empirical_split(
        N, sampled["e1_mean"], sampled["h1_mean"],
        sampled["e2_mean"], sampled["h2_mean"], k_total)
    assert int(split["k1"]) + int(split["k2"]) == k_total
    assert set(np.asarray(split["l1_order"]).tolist()) == set(range(N))
    assert set(np.asarray(split["l2_order"]).tolist()) == set(range(N))
    spike = p20t.derive_spike_order_8192(sampled["h2_mean"])
    assert set(spike["spike_l2_order"].tolist()) == set(range(N))
    delta = p20t.order_set_delta_8192(
        np.asarray(split["l2_order"]), np.asarray(spike["spike_l2_order"]),
        int(split["k2"]))
    assert delta["size_delta_b_minus_a"] == 0


def test_no_stage_b_root_and_no_protected_opens_in_stage_a():
    assert not Path(p20t.FROZEN_OUT_ROOT).exists()
    assert Path(p20t.FROZEN_OUT_ROOT).name == "n8192_persistence_probe_2m"
    assert p20t._DEV_PARQUET_CONTENT_OPENED is False
    assert p20t._SESSION_PRIOR_CONTENT_LOADED is False
    source = Path(p20t.__file__).read_text(encoding="utf-8")
    for token in ("load_v25_channel_counts", "smooth_joint_to_conditional",
                  "LAMBDA_STAR", "137.3823795883264"):
        assert token not in source, token
    for token in ("reuse_prior_arrays_identity",
                  "new_construction_identity_8192",
                  "fresh_order_identity_A_8192",
                  "spike_order_identity_B_8192",
                  "order_derivation_identity", "k_rule_derived",
                  "sampling_calls_exact",
                  "verify_single_segment_containment",
                  "verify_consumed_exclusions_single_segment",
                  "verify_single_segment_frame_set_identity",
                  "ir_payload_complete", "derive_spike_order_8192",
                  "run_derive_stage_a", "verify_derivation",
                  "check_ir5_manifest_identity", "ir5full-v1",
                  "nbpolar-p20t-n8192-persistence-2m-seed",
                  "run_n8192_persistence_probe_2m",
                  "TARGET_EMPIRICAL_N8192_TAIL_PERSISTENCE_PROBE_COMPLETE"):
        assert token in source, token
    assert "2026092400" in source
    assert p20t.FROZEN_ARM_NAMES == (
        "A_anchor_frozen_order_equivalent", "B_spike_local_order",
        "O_true_l1_oracle")
    assert "_l2_hazard_diagnostics_8192" in source
    assert "l2_fail_in_prefix_u_domain" in source


def test_p20t_out_root_absent_and_p20s_root_untouched():
    """Stage-A close pin: the P20T out-root is ABSENT; the P20S root is untouched.

    Read-only: ``Path.exists`` checks only — no writes, no content opens,
    no stats, no directory listings.
    """
    p20t_root_dir = REPO_ROOT / p20t.FROZEN_OUT_ROOT
    assert p20t_root_dir.name == "n8192_persistence_probe_2m"
    assert not p20t_root_dir.exists()
    p20s_root_dir = REPO_ROOT / p20s.FROZEN_OUT_ROOT
    assert p20s_root_dir.name == "l2_mechanism_probe_2m"
    assert p20s_root_dir.exists()
    assert len(p20s.OUTPUT_FILES) == 15
    for name in p20s.OUTPUT_FILES:
        assert (p20s_root_dir / name).exists(), name
    assert len(p20t.OUTPUT_FILES) == 15


def test_zero_stage_b_sampling_pin():
    parser = p20t.build_parser()
    options = set()
    for action in parser._actions:
        options.update(action.option_strings)
    for forbidden in ("--train-seeds", "--seed", "--sample", "--rng", "--genie",
                      "--deriv-seeds-stage-b"):
        assert forbidden not in options, forbidden
    for name in p20t.STAGE_B_FLAGS:
        assert "seed" not in name and "sample" not in name
    assert "--derive" in options
    assert "--verify-derivation" in options
    assert "seeds" not in p20t.run_n8192_persistence_probe_2m.__code__.co_varnames
    assert "genie" not in p20t.run_n8192_persistence_probe_2m.__code__.co_varnames
    source = Path(p20t.__file__).read_text(encoding="utf-8")
    assert "default_rng" not in source
    assert "sample_full_block" not in source


def test_one_open_guards_refuse_reload(monkeypatch):
    with p20t_root() as root:
        _, construction_path, order_path, spike_path, pins = \
            stage_a_fixture(root)
        monkeypatch.setattr(
            p20t, "verify_dev_manifest_2m",
            lambda *a, **k: {"train_pairs": 559872, "val_pairs": 186624,
                             "hold_pairs": 186624})
        base = dict(prior_path="p", prior_digest=pins["prior_digest"],
                    source="2M", floor=1e-15, n=N,
                    k1=pins["k1"], k2=pins["k2"],
                    construction=str(construction_path),
                    construction_digest=pins["construction_digest"],
                    manifest_path="m", dev_pairs=p20t.FROZEN_DEV_PAIRS_PATH,
                    order_file=str(order_path), order_digest=pins["order_digest"],
                    spike_order_file=str(spike_path),
                    spike_order_digest=pins["spike_order_digest"],
                    spike_formula=p20t.SPIKE_FORMULA_ID,
                    tag_master=2026092400)
        with patched(p20t, "FROZEN_K_TOTAL", pins["k_total"]), \
                patched(p20t, "FROZEN_K1", pins["k1"]), \
                patched(p20t, "FROZEN_K2", pins["k2"]), \
                patched(p20t, "FROZEN_BUDGET_LITERAL", pins["budget_literal"]), \
                patched(p20t, "FROZEN_TRAIN_RESIDUAL", pins["train_residual"]), \
                patched(p20t, "FROZEN_CONSTRUCTION_DIGEST_8192",
                        pins["construction_digest"]), \
                patched(p20t, "FROZEN_ORDER_DIGEST_A_8192",
                        pins["order_digest"]), \
                patched(p20t, "FROZEN_SPIKE_ORDER_DIGEST_B_8192",
                        pins["spike_order_digest"]), \
                patched(p20t, "FROZEN_H1", pins["h1"]), \
                patched(p20t, "FROZEN_H2", pins["h2"]), \
                patched(p20t, "FROZEN_H_TOTAL", pins["h_total"]), \
                patched(p20t, "FROZEN_SESSION_PRIOR_DIGEST",
                        pins["prior_digest"]), \
                restored_guards():
            out = str(root / "out")
            p20t._SESSION_PRIOR_CONTENT_LOADED = True
            assert_raises_match(ValueError, "reload refused",
                                p20t.run_n8192_persistence_probe_2m,
                                out_dir=out, **base)
            assert not Path(out).exists()
            p20t._SESSION_PRIOR_CONTENT_LOADED = False
            p20t._DEV_PARQUET_CONTENT_OPENED = True
            assert_raises_match(ValueError, "reopen refused",
                                p20t.run_n8192_persistence_probe_2m,
                                out_dir=out, prior={}, **base)
            assert not Path(out).exists()


# ---- injected end-to-end single-block three-arm run (no protected data) ----

def test_injected_end_to_end_single_block_three_arms(monkeypatch):
    with p20t_root() as root:
        arrays, construction_path, order_path, spike_path, pins = \
            stage_a_fixture(root)
        table = single_segment_table(seed=TEST_SEEDS[1])
        monkeypatch.setattr(
            p20t, "verify_dev_manifest_2m",
            lambda *a, **k: {"train_pairs": 559872, "val_pairs": 186624,
                             "hold_pairs": 186624})
        out = str(root / "n8192_persistence_probe_2m")
        with patched(p20t, "FROZEN_H1", pins["h1"]), \
                patched(p20t, "FROZEN_H2", pins["h2"]), \
                patched(p20t, "FROZEN_H_TOTAL", pins["h_total"]), \
                patched(p20t, "FROZEN_SESSION_PRIOR_DIGEST",
                        pins["prior_digest"]), \
                patched(p20t, "FROZEN_K_TOTAL", pins["k_total"]), \
                patched(p20t, "FROZEN_K1", pins["k1"]), \
                patched(p20t, "FROZEN_K2", pins["k2"]), \
                patched(p20t, "FROZEN_BUDGET_LITERAL", pins["budget_literal"]), \
                patched(p20t, "FROZEN_TRAIN_RESIDUAL", pins["train_residual"]), \
                patched(p20t, "FROZEN_CONSTRUCTION_DIGEST_8192",
                        pins["construction_digest"]), \
                patched(p20t, "FROZEN_ORDER_DIGEST_A_8192",
                        pins["order_digest"]), \
                patched(p20t, "FROZEN_SPIKE_ORDER_DIGEST_B_8192",
                        pins["spike_order_digest"]), \
                restored_guards():
            run = p20t.run_n8192_persistence_probe_2m(
                prior=dict(arrays),
                prior_digest=pins["prior_digest"],
                source="2M", floor=1e-15,
                n=N, k1=pins["k1"], k2=pins["k2"],
                construction=str(construction_path),
                construction_digest=pins["construction_digest"],
                manifest_path="m", dev_table=table,
                dev_pairs=p20t.FROZEN_DEV_PAIRS_PATH,
                dev_frames_hold=(3595, 3626),
                block_frames=32,
                remainder_frames=(3627, 3644), tag_master=2026092400,
                chunk_rows=128, tag_bits=64, order_file=str(order_path),
                order_digest=pins["order_digest"],
                spike_order_file=str(spike_path),
                spike_order_digest=pins["spike_order_digest"],
                spike_formula=p20t.SPIKE_FORMULA_ID, out_dir=out)
            summary = run.summary
            records = list(run.records)
            assert summary["records_completed"] == 3
            assert {r["arm"] for r in records} == set(p20t.FROZEN_ARM_NAMES)
            assert summary["stage_b_sampling_calls"] == 0
            # arm-specific order digests: fresh-A on A/O, spike on B.
            by_arm = {r["arm"]: r for r in records}
            assert by_arm["A_anchor_frozen_order_equivalent"][
                "l2_order_digest"] == pins["order_digest"]
            assert by_arm["O_true_l1_oracle"][
                "l2_order_digest"] == pins["order_digest"]
            assert by_arm["B_spike_local_order"][
                "l2_order_digest"] == pins["spike_order_digest"]
            # the order factor moves the prefix hazard means between A and B.
            assert by_arm["A_anchor_frozen_order_equivalent"][
                "l2_prefix_hazard_mean_bits"] != by_arm["B_spike_local_order"][
                "l2_prefix_hazard_mean_bits"]
            # IR-1..IR-4 all PRESENT plus IR-5 manifest references, every record.
            assert p20t.ir_payload_complete(records) is True
            assert p20t.hazard_instrumentation_complete(records) is True
            # the byte-exact set-delta rides the summary with size-delta 0.
            assert summary["order_set_delta"]["size_delta_b_minus_a"] == 0
            # mechanism diagnostics replace counting vocabulary: no transition
            # cells are computed anywhere in the aggregates.
            assert summary["aggregates"]["mechanism"]["transition_cells_computed"] \
                is False
            assert summary["aggregates"]["mechanism"]["transition_tables"] is None
            # within-N quantities only; never a recovery-rate reading.
            assert summary["aggregates"]["ir_payload"]["within_n_only"] is True
            assert summary["aggregates"]["ir_payload"]["cross_n_inference"] is False
            # fifteen files land under the injected out root only.
            for name in p20t.OUTPUT_FILES:
                assert (Path(out) / name).exists(), name
            assert len(p20t.OUTPUT_FILES) == 15
            # the nine IR-5 binaries verify against the run manifest.
            manifest = json.loads((Path(out) / "ir5_full_manifest.json")
                                  .read_text(encoding="utf-8"))
            assert p20t.check_ir5_manifest_identity(
                Path(out), manifest)["verified"] is True


# ---- seed-domain grep rule ----

def test_grep_rule_seed_placement():
    master = "2026092400"
    deriv_seeds = ["2026092410", "2026092411", "2026092412", "2026092413"]
    test_seeds = [str(seed) for seed in TEST_SEEDS]
    module_source = Path(p20t.__file__).read_text(encoding="utf-8")
    test_source = Path(__file__).read_text(encoding="utf-8")
    assert master in module_source
    for seed in test_seeds:
        assert seed in test_source, seed
        assert seed not in module_source, seed
    assert p20t.FROZEN_TAG_MASTER == 2026092400
    assert p20t.FROZEN_TAG_MASTER not in (
        p20m.FROZEN_TAG_MASTER,
        p20o.FROZEN_TAG_MASTER if hasattr(p20o, "FROZEN_TAG_MASTER") else None,
        p20s.FROZEN_TAG_MASTER)
    assert tuple(p20t.FROZEN_DERIVATION_SEEDS) == (
        2026092410, 2026092411, 2026092412, 2026092413)
    allowed_prefixes = (
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/n8192_persistence_probe_2m.py",
        "comparison_bench/tests/test_nbpolar_n8192_persistence_probe_2m.py",
        ".workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-reduced-n-persistence/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md",
    )
    for literal in [master] + test_seeds + deriv_seeds + ["nbpolar-p20t"]:
        for hit in _git_grep_hits(literal):
            assert hit.startswith(allowed_prefixes), (literal, hit)
