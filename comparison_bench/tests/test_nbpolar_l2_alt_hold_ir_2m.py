"""Focused Phase 4-P20Q 2M HOLD-IR confirmation tests.

Injected/synthetic counts, priors, artifacts and fresh additive
``workspace/p20q/<uuid>/`` temp roots only. The V25 channel-counts NPZ, every
registered pairs parquet (1M, 1.5M VAL/HOLD/TRAIN, 2M VAL/HOLD), the real P16
construction root, the real split manifest, the accepted P20O worktree
products and every accepted evidence root are NEVER content-opened, statted,
or listed here: the Stage-A reuse verification runs only in the authorized
``--verify-reuse`` command, never in tests. There is no derivation sampler
in P20Q (reuse needs zero sampling; genie 0+0). Focused tests use their own
fresh seeds ``2026092331..2026092337`` and never the frozen P20Q tag master
``2026092330`` (except through the frozen module constant).
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

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_alt_hold_ir_2m as l2q,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_alt_maintain_2m as p20o,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l1_order_1p5m as p20l,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13 as opf,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    per_session_calibration as psc,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    raw_prior_val_1p5m as p20m,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never the frozen P20Q tag master 2026092330.
TEST_SEEDS = (2026092331, 2026092332, 2026092333, 2026092334,
              2026092335, 2026092336, 2026092337)

FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63

# Test-local gated prefix length for the recorder seam.
TEST_K2 = 256


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
        l2q._SESSION_PRIOR_CONTENT_LOADED, l2q._ALT_CONTENT_LOADED,
        l2q._DEV_PARQUET_CONTENT_OPENED,
    )
    try:
        yield
    finally:
        (l2q._SESSION_PRIOR_CONTENT_LOADED, l2q._ALT_CONTENT_LOADED,
         l2q._DEV_PARQUET_CONTENT_OPENED) = state


@contextlib.contextmanager
def p20q_root():
    """Fresh additive workspace/p20q/<uuid>/ temp root, cleaned afterwards."""
    root = REPO_ROOT / "workspace" / "p20q" / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    assert "workspace" in root.parts and "p20q" in root.parts
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


def exact_total_counts(seed: int, total: int = 559872) -> np.ndarray:
    """Synthetic counts with an exact integer total (self-consistent fixture)."""
    counts = sparse_counts(seed)
    counts[0, 0] += float(total) - float(counts.sum())
    assert int(round(float(counts.sum()))) == total
    return np.ascontiguousarray(counts)


def hold_table(*, seed: int = TEST_SEEDS[2]) -> pd.DataFrame:
    """HOLD-like pairs frame: 640 DEV frames 2916..3555 + 89-frame remainder."""
    rng = np.random.default_rng(int(seed))
    frames = np.repeat(np.arange(2916, 3556), 256)
    pair_idx = np.tile(np.arange(256), 640)
    dev = pd.DataFrame({
        "frame_id": frames,
        "pair_idx": pair_idx,
        "alice_symbol": rng.integers(0, 1024, size=frames.size),
        "bob_symbol": rng.integers(0, 1024, size=frames.size),
    })
    rem_frames = np.repeat(np.arange(3556, 3645), 256)
    rem = pd.DataFrame({
        "frame_id": rem_frames,
        "pair_idx": np.tile(np.arange(256), 89),
        "alice_symbol": rng.integers(0, 1024, size=rem_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=rem_frames.size),
    })
    # Extra rows outside the DEV/remainder spans must not influence slicing.
    extra = pd.DataFrame({
        "frame_id": np.repeat([0, 2186, 2187, 2826, 2915], 256),
        "pair_idx": np.tile(np.arange(256), 5),
        "alice_symbol": rng.integers(0, 1024, size=5 * 256),
        "bob_symbol": rng.integers(0, 1024, size=5 * 256),
    })
    return pd.concat([dev, rem, extra], ignore_index=True).sample(
        frac=1.0, random_state=int(seed)).reset_index(drop=True)


def tiny_ir_fixture(*, seed: int = TEST_SEEDS[3], n: int = 512):
    """Length-n natural-index truth vectors + tables for the IR recorder."""
    rng = np.random.default_rng(int(seed))
    counts = sparse_counts(seed, cells=1024, hi=20)
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.ascontiguousarray(np.asarray(arrays["p2"], dtype=np.float64))
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    order = rng.permutation(n).astype(np.int64)
    view = {"bob": bob, "high": high, "low": low, "u1_cond": high}
    return counts, p2, view, order


def ir_recorder(view, p2, order, first_error, *, k2=TEST_K2,
                prefix_mean=None):
    if prefix_mean is None:
        mask = np.zeros(int(view["bob"].size), dtype=bool)
        mask[np.asarray(order)[:k2]] = True
        hazards = p20o._hazard_bits(
            p2, np.asarray(view.get("u1_cond", view["high"])),
            np.asarray(view["bob"]), np.asarray(view["low"]))
        prefix_mean = float(np.mean(hazards[mask]))
    with patched(l2q, "FROZEN_K2", k2):
        return l2q._ir_hazard_diagnostics(
            view=view, p2_arm=p2, l2_order=order, k2=k2,
            first_error=first_error, prefix_mean=prefix_mean)


def reuse_fixture(root, *, seed: int = TEST_SEEDS[0]):
    """Self-consistent synthetic prior/alt/order fixtures + their pins."""
    counts = exact_total_counts(seed)
    prior_arrays = p20o.raw_prior_arrays(counts)
    alt = p20o.alt_tables_2m(counts, incumbent_arrays=prior_arrays)
    alt_arrays = alt["arrays"]
    prior_path = root / "raw_prior.npz"
    with open(prior_path, "wb") as fh:
        np.savez(fh, **{k: np.asarray(v) for k, v in prior_arrays.items()})
    alt_path = root / "alt.npz"
    with open(alt_path, "wb") as fh:
        np.savez(fh, **{k: np.asarray(v) for k, v in alt_arrays.items()})
    rng = np.random.default_rng(seed)
    n = 32768
    doc = {
        "protocol": p20o.PROTOCOL_NAME,
        "kind": "raw-prior-orders-file",
        "n": n,
        "k_total": 7080,
        "k1": 334,
        "k2": 6746,
        "l1_order": [int(v) for v in rng.permutation(n).tolist()],
        "l2_order": [int(v) for v in rng.permutation(n).tolist()],
        "derivation": {
            "program": p20o.FROZEN_ORDER_PROGRAM_PIN,
            "prior_digest": psc.canonical_prior_digest(prior_arrays),
            "train_seeds": [int(s) for s in p20o.FROZEN_DERIVATION_SEEDS],
            "train_blocks_used": 16,
        },
    }
    order_path = root / "orders.json"
    order_path.write_text(json.dumps(doc, sort_keys=True) + "\n", encoding="utf-8")
    d1 = p20o.feasibility_literals_2m(
        np.asarray(counts, dtype=np.float64),
        p2_incumbent=np.asarray(prior_arrays["p2"]),
        p2_alt=np.asarray(alt_arrays["p2_alt"]), k2=6746, k_total=7080)
    pins = {
        "prior_digest": psc.canonical_prior_digest(prior_arrays),
        "alt_digest": hashlib.sha256(alt_path.read_bytes()).hexdigest(),
        "order_digest": hashlib.sha256(order_path.read_bytes()).hexdigest(),
        "h1": float(np.asarray(prior_arrays["h1"])),
        "h2": float(np.asarray(prior_arrays["h2"])),
        "h_total": float(np.asarray(prior_arrays["h_total"])),
        "ce_alt": float(d1["ce_alt_insample_bits_per_symbol"]),
        "ce_incumbent": float(d1["ce_incumbent_insample_bits_per_symbol"]),
        "alt_ideal_length_bits": float(d1["alt_ideal_length_bits"]),
    }
    return prior_path, alt_path, order_path, pins


def _git_grep_hits(literal: str):
    proc = subprocess.run(
        ["git", "grep", "-l", "--untracked", literal, "--",
         "comparison_bench", "openspec", ".workbuddy", "docs"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1), proc.stderr
    return [line for line in proc.stdout.splitlines() if line.strip()]


# ---- frozen literals, arms, population, delta d1-d8 ----

def test_frozen_literals_arms_population_and_delta():
    assert l2q.FROZEN_SOURCE == "2M"
    assert l2q.FROZEN_SOURCE_TAG == "type2_2M_20260121_183657"
    assert l2q.FROZEN_N == 32768
    assert l2q.FROZEN_FLOOR == 1e-15
    assert l2q.FROZEN_ALPHA == 1.0
    # (d3) K literals replay the P20O derivation, never recarried.
    assert (l2q.FROZEN_K_TOTAL, l2q.FROZEN_K1,
            l2q.FROZEN_K2) == (7080, 334, 6746)
    assert (l2q.FROZEN_K_TOTAL, l2q.FROZEN_K1,
            l2q.FROZEN_K2) == (p20o.FROZEN_K_TOTAL, p20o.FROZEN_K1,
                               p20o.FROZEN_K2)
    # (d2) reuse pins are byte-identical to the accepted import target.
    assert l2q.FROZEN_SESSION_PRIOR_DIGEST == p20o.FROZEN_SESSION_PRIOR_DIGEST
    assert l2q.FROZEN_ORDER_DIGEST == p20o.FROZEN_ORDER_DIGEST
    assert l2q.FROZEN_ALT_DIGEST == p20o.FROZEN_ALT_DIGEST
    assert (l2q.FROZEN_H1, l2q.FROZEN_H2,
            l2q.FROZEN_H_TOTAL) == (p20o.FROZEN_H1, p20o.FROZEN_H2,
                                    p20o.FROZEN_H_TOTAL)
    # (d1/d8) HOLD population: FIRST 640 HOLD frames, five blocks, remainder.
    assert tuple(l2q.FROZEN_DEV_FRAME_RANGE) == (2916, 3555)
    assert l2q.FROZEN_DEV_FRAMES == 640
    assert l2q.FROZEN_DEV_PAIRS == 163840
    assert tuple(tuple(r) for r in l2q.FROZEN_BLOCK_RANGES) == (
        (2916, 3043), (3044, 3171), (3172, 3299), (3300, 3427), (3428, 3555))
    assert tuple(l2q.FROZEN_REMAINDER_FRAME_RANGE) == (3556, 3644)
    assert l2q.FROZEN_REMAINDER_FRAMES == 89
    assert l2q.FROZEN_REMAINDER_SYMBOLS == 89 * 256
    assert tuple(l2q.CONSUMED_2M_VAL_FRAME_RANGE) == (2187, 2915)
    assert tuple(l2q.FROZEN_BUILD_FRAME_RANGE) == (0, 2186)
    # (d6) new P20Q tag domain, disjoint from P20O by master and prefix.
    assert l2q.FROZEN_TAG_MASTER == 2026092330
    assert l2q.FROZEN_TAG_MASTER != p20o.FROZEN_TAG_MASTER
    assert l2q.SEED_PREFIX == "nbpolar-p20q-hold-ir-2m-seed"
    assert l2q.SEED_PREFIX != p20o.SEED_PREFIX
    # (d5) arms: same K, same prefixes, zero disclosure delta by design.
    arms = l2q.frozen_arm_table()
    assert tuple(s.name for s in arms) == l2q.FROZEN_ARM_NAMES
    assert l2q.check_frozen_arm_table()["planned_key_dependent_bits"] == 692580
    totals = l2q.planned_totals(334, 6746)
    assert totals["operational_key_dependent_bits"] == 35464
    assert totals["oracle_key_dependent_bits"] == 33794
    assert totals["planned_key_dependent_bits"] == 692580
    assert totals["planned_public_control_bits"] == 6554860
    assert totals["planned_sc_calls"] == 30
    assert totals["planned_tag_invocations"] == 20
    assert totals["planned_records"] == 20
    # (d7) IR pins frozen PRESENT.
    assert l2q.IR1_BINS == 64
    assert (l2q.IR3_LO_MULT, l2q.IR3_HI_MULT) == (1.0, 2.0)
    assert l2q.IR4_TOPK == 16
    assert l2q.IR5_CAP == 4096
    # the delta list d1-d8 is evidenced in the module docstring and the
    # import target plus the carried-over callsite pattern are referenced.
    source = Path(l2q.__file__).read_text(encoding="utf-8")
    assert "from . import l2_alt_maintain_2m as p20o" in source
    assert "_l2_hazard_diagnostics" in source
    assert "_ir_hazard_diagnostics" in source
    assert "no lambda" in source.lower() or "NO lambda" in source or \
        "lambda anywhere" in source


def test_frozen_command_byte_identical_when_pins_applied():
    assert l2q.pins_are_frozen() is True
    assert l2q.FROZEN_COMMAND is not None
    assert "--verify-reuse" not in l2q.FROZEN_COMMAND
    assert "--source 2M" in l2q.FROZEN_COMMAND
    assert "--dev-frames 2916 3555" in l2q.FROZEN_COMMAND
    assert "--remainder-frames 3556 3644" in l2q.FROZEN_COMMAND
    assert "--tag-master 2026092330" in l2q.FROZEN_COMMAND
    assert "l2_alt_hold_ir_2m" in l2q.FROZEN_COMMAND
    assert l2q.FROZEN_COMMAND.count(
        "b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587") == 1
    assert l2q.FROZEN_COMMAND.count(
        "98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5") == 1
    assert l2q.FROZEN_COMMAND.count(
        "b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906") == 1
    # the Stage-B out root is the frozen P20Q evidence root.
    assert l2q.FROZEN_OUT_ROOT.endswith(
        "NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/l2_alt_hold_ir_2m")


# ---- Stage-A verify-reuse (injected fixtures only) ----

def test_verify_reuse_positive_and_refusals():
    with p20q_root() as root:
        prior_path, alt_path, order_path, pins = reuse_fixture(root)
        kws = dict(prior=prior_path, alt_prior=alt_path,
                   order_file=order_path, prior_digest=pins["prior_digest"],
                   alt_digest=pins["alt_digest"],
                   order_digest=pins["order_digest"], h1=pins["h1"],
                   h2=pins["h2"], h_total=pins["h_total"], k1=334, k2=6746,
                   ce_alt=pins["ce_alt"], ce_incumbent=pins["ce_incumbent"],
                   alt_ideal_length_bits=pins["alt_ideal_length_bits"],
                   d2_feasible=True)
        result = None
        with patched(p20o, "FROZEN_SESSION_PRIOR_DIGEST", pins["prior_digest"]), \
                patched(p20o, "FROZEN_ALT_DIGEST", pins["alt_digest"]), \
                patched(p20o, "FROZEN_ORDER_DIGEST", pins["order_digest"]), \
                patched(p20o, "FROZEN_ALT_H1_INC", pins["h1"]):
            result = l2q.verify_reuse(**kws)
            assert result["verified"] is True
            assert result["hold_contact"] == 0
            assert result["prior_digest"] == pins["prior_digest"]
            assert result["alt_file_digest"] == pins["alt_digest"]
            assert result["order_digest"] == pins["order_digest"]
            assert result["d2_feasible"] is True
            assert result["k_literals"]["k_total"] == 7080
            # every replay pin refuses on mismatch with HOLD untouched.
            bad = dict(kws)
            bad["prior_digest"] = "0" * 64
            assert_raises_match(ValueError, "reuse_prior_identity",
                                l2q.verify_reuse, **bad)
            bad = dict(kws)
            bad["alt_digest"] = "0" * 64
            assert_raises_match(ValueError, "reuse_alt_identity",
                                l2q.verify_reuse, **bad)
            bad = dict(kws)
            bad["order_digest"] = "0" * 64
            assert_raises_match(ValueError, "reuse_order_freeze",
                                l2q.verify_reuse, **bad)
            bad = dict(kws)
            bad["k1"] = 335
            assert_raises_match(ValueError, "k_literal_exact",
                                l2q.verify_reuse, **bad)
            bad = dict(kws)
            bad["ce_alt"] = float(pins["ce_alt"]) + 1.0
            assert_raises_match(ValueError,
                                "alt_construction_budget_feasibility",
                                l2q.verify_reuse, **bad)
            bad = dict(kws)
            bad["d2_feasible"] = False
            assert_raises_match(ValueError,
                                "alt_construction_budget_feasibility",
                                l2q.verify_reuse, **bad)
            bad = dict(kws)
            bad["h_total"] = float(pins["h_total"]) + 1e-6
            assert_raises_match(ValueError, "reuse_prior_identity",
                                l2q.verify_reuse, **bad)
        assert result is not None


def test_cli_mode_refusals(capsys):
    assert l2q.main(["--verify-reuse", "--prior", "x"]) == 2
    _, err = capsys.readouterr()
    assert "missing required --verify-reuse flags" in err
    assert l2q.main([]) == 2
    _, err = capsys.readouterr()
    assert "ambiguous invocation refused" in err
    with p20q_root() as root:
        _, _, _, pins = reuse_fixture(root)
        rc = l2q.main([
            "--verify-reuse",
            "--prior", "p", "--prior-digest", pins["prior_digest"],
            "--alt-prior", "a", "--alt-digest", pins["alt_digest"],
            "--order-file", "o", "--order-digest", pins["order_digest"],
            "--k1", "334", "--k2", "6746", "--tag-master", "2026092330",
        ])
        assert rc == 2
        _, err = capsys.readouterr()
        assert "takes no Stage-B-only flags" in err


# ---- 2M HOLD population + gate family (b)-(e) ----

def test_hold_population_and_gate_family():
    table = hold_table()
    formation = l2q.form_hold_blocks(table)
    assert formation["dev_frame_range"] == [2916, 3555]
    assert formation["dev_frames"] == 640
    assert formation["dev_pairs"] == 163840
    assert [tuple(r) for r in formation["block_ranges"]] == list(
        l2q.FROZEN_BLOCK_RANGES)
    assert len(formation["blocks"]) == 5
    for block in formation["blocks"]:
        assert block["labels"].size == 32768
        assert int(block["high"].max()) < 32 and int(block["low"].max()) < 32
    assert formation["remainder"] == {
        "frame_start": 3556, "frame_end": 3644, "frames": 89,
        "symbols": 22784, "used": False}
    assert l2q.verify_hold_containment()["verified"] is True
    assert l2q.verify_consumed_exclusions_hold()["verified"] is True
    assert l2q.verify_consumed_exclusions_hold()["build_frames"] == [0, 2186]
    # declared-range refusals refuse before any content open.
    assert_raises_match(ValueError, "dev-frames",
                        l2q.form_hold_blocks, table, dev_frames=(2916, 3554))
    assert_raises_match(ValueError, "remainder-frames",
                        l2q.form_hold_blocks, table,
                        remainder_frames=(3556, 3645))
    assert_raises_match(ValueError, "BLOCKED(dev_block_range_identity)",
                        l2q.verify_hold_containment, (2916, 3554))
    # consumed 2M VAL (DEV + remainder) and 2M TRAIN-as-DEV refuse in HOLD.
    assert_raises_match(ValueError, "lies outside 2M HOLD",
                        l2q.verify_hold_containment, (2187, 2826))
    assert_raises_match(ValueError, "lies outside 2M HOLD",
                        l2q.verify_hold_containment, (0, 1000))
    assert_raises_match(ValueError, "consumed 2M TRAIN",
                        l2q.verify_consumed_exclusions_hold, (0, 1000))
    assert_raises_match(ValueError, "consumed 2M VAL",
                        l2q.verify_consumed_exclusions_hold,
                        (2916, 3555), (2827, 2915))
    # cross-file gate: the 1M pool and the 1.5M session refuse by path.
    assert_raises_match(ValueError, "1M full-pool",
                        l2q.verify_dev_source_identity_2m,
                        l2q.REFUSED_1M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "1.5M session",
                        l2q.verify_dev_source_identity_2m,
                        l2q.REFUSED_1P5M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "dev-pairs",
                        l2q.verify_dev_source_identity_2m, "elsewhere.parquet")
    # malformed population refuses inside the formation.
    bad = table.copy()
    bad.loc[bad.index[0], "bob_symbol"] = 1024
    assert_raises_match(ValueError, "dev_population_exact",
                        l2q.form_hold_blocks, bad)
    bad2 = table.copy()
    bad2 = bad2[bad2["frame_id"] != 2916]
    assert_raises_match(ValueError, "dev_population_exact",
                        l2q.form_hold_blocks, bad2)


# ---- IR-1..IR-5 recorder formulas, caps, nullability ----

def test_ir_recorder_formulas_caps_and_nullability():
    _, p2, view, order = tiny_ir_fixture()
    n = int(view["bob"].size)
    k2 = TEST_K2
    prefix = order[:k2]
    ir = ir_recorder(view, p2, order,
                     {"first_error_layer": "L1", "first_error_coord": 9})
    assert set(ir) == set(l2q.IR_FIELDS)
    # IR-1: frozen 65 log-spaced edges; prefix/outside counts tile the block.
    edges = np.asarray(ir["ir1_hist_edges_bits"], dtype=np.float64)
    assert edges.shape == (65,)
    assert edges[0] == 0.0
    assert abs(edges[1] - 1e-3) / 1e-3 <= 1e-12
    assert abs(edges[-1] - 32.0) <= 1e-9
    assert len(ir["ir1_hist_prefix_counts"]) == 64
    assert len(ir["ir1_hist_outside_counts"]) == 64
    assert sum(ir["ir1_hist_prefix_counts"]) == k2
    assert sum(ir["ir1_hist_outside_counts"]) == n - k2
    # IR-2: null unless the first error is L2-layer.
    assert ir["ir2_first_error_hazard_rank_pct"] is None
    # IR-3: EXACTLY two frozen thresholds at 1.0x/2.0x record prefix-mean.
    pm = float(np.mean(p20o._hazard_bits(
        p2, view["high"][prefix], view["bob"][prefix], view["low"][prefix])))
    assert abs(ir["ir3_thresh_lo_bits"] - pm) <= 1e-12
    assert abs(ir["ir3_thresh_hi_bits"] - 2.0 * pm) <= 1e-12
    prefix_haz = p20o._hazard_bits(
        p2, view["high"][prefix], view["bob"][prefix], view["low"][prefix])
    assert ir["ir3_prefix_above_lo_count"] == int(np.sum(prefix_haz > pm))
    assert ir["ir3_prefix_above_lo_frac"] == int(np.sum(prefix_haz > pm)) / k2
    assert ir["ir3_prefix_above_hi_count"] == int(np.sum(prefix_haz > 2.0 * pm))
    assert ir["ir3_prefix_above_hi_frac"] == int(
        np.sum(prefix_haz > 2.0 * pm)) / k2
    # IR-4: top-16 hazards with 1-based ranks.
    hazards = p20o._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
    serial = np.arange(n)
    full_order = np.lexsort((serial, -hazards))
    assert ir["ir4_topk_coords"] == [int(v) for v in full_order[:16]]
    assert ir["ir4_topk_hazard_bits"] == [float(hazards[v])
                                         for v in full_order[:16]]
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    assert ir["ir4_topk_in_prefix"] == [bool(mask[v])
                                       for v in full_order[:16]]
    assert ir["ir4_topk_ranks"] == list(range(1, 17))
    # IR-5: capped series (n < cap here: full length, truncation False).
    assert len(ir["ir5_series_hazard_bits"]) == n
    assert len(ir["ir5_series_in_prefix"]) == n
    assert ir["ir5_series_truncated"] is False
    assert ir["ir5_series_total_len"] == n
    assert ir["ir5_series_hazard_bits"] == [
        float(v) for v in np.asarray(hazards[:n], dtype=np.float32)]
    # L2 failure: IR-2 is the exact hazard-rank percentile.
    pos = int(prefix[7])
    ir2 = ir_recorder(view, p2, order,
                      {"first_error_layer": "L2", "first_error_coord": pos})
    want_rank = float(np.mean(hazards <= hazards[pos]))
    assert abs(ir2["ir2_first_error_hazard_rank_pct"] - want_rank) <= 1e-12
    # the gated prefix length refuses anything else.
    with patched(l2q, "FROZEN_K2", k2):
        assert_raises_match(ValueError, "gated prefix length",
                            l2q._ir_hazard_diagnostics, view=view, p2_arm=p2,
                            l2_order=order, k2=k2 - 1,
                            first_error={"first_error_layer": None,
                                         "first_error_coord": None},
                            prefix_mean=pm)
        # an L2 failure without a valid coordinate refuses (never a silent null).
        assert_raises_match(ValueError, "valid natural block symbol index",
                            l2q._ir_hazard_diagnostics, view=view, p2_arm=p2,
                            l2_order=order, k2=k2,
                            first_error={"first_error_layer": "L2",
                                         "first_error_coord": None},
                            prefix_mean=pm)
    # exact formulas do not mutate their inputs.
    snapshot = {k: np.array(view[k], copy=True)
                for k in ("bob", "high", "low", "u1_cond")}
    p2_snapshot = np.array(p2, copy=True)
    ir_recorder(view, p2, order,
                {"first_error_layer": "L2", "first_error_coord": pos})
    for key, before in snapshot.items():
        assert np.array_equal(before, view[key]), key
    assert np.array_equal(p2_snapshot, p2)


def test_ir_payload_complete_gate():
    _, p2, view, _ = tiny_ir_fixture(n=32768)
    n = 32768
    rng = np.random.default_rng(TEST_SEEDS[4])
    order = rng.permutation(n).astype(np.int64)
    k2 = int(l2q.FROZEN_K2)
    prefix = order[:k2]
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    hazards = p20o._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
    pm = float(np.mean(hazards[mask]))
    base = l2q._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": None, "first_error_coord": None},
        prefix_mean=pm)
    assert l2q.ir_payload_complete([]) is False
    assert l2q.ir_payload_complete([dict(base, outcome="exact",
                                        first_error_layer=None)]) is True
    pos = int(prefix[3])
    l2rec = dict(l2q._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": "L2", "first_error_coord": pos},
        prefix_mean=pm),
        outcome="verify_failed", first_error_layer="L2")
    assert l2q.ir_payload_complete([l2rec]) is True
    # IR-5 truncation flag is frozen true at N=32768.
    assert l2rec["ir5_series_truncated"] is True
    assert len(l2rec["ir5_series_hazard_bits"]) == 4096
    # every refusal mode fails the gate.
    assert l2q.ir_payload_complete(
        [dict(l2rec, ir4_topk_coords=l2rec["ir4_topk_coords"][:15])]) is False
    assert l2q.ir_payload_complete(
        [dict(l2rec,
              ir2_first_error_hazard_rank_pct=None)]) is False
    assert l2q.ir_payload_complete(
        [dict(base, outcome="exact", first_error_layer=None,
              ir2_first_error_hazard_rank_pct=0.5)]) is False
    assert l2q.ir_payload_complete(
        [dict(l2rec, ir5_series_truncated=False)]) is False
    dropped = dict(l2rec)
    del dropped["ir3_thresh_hi_bits"]
    assert l2q.ir_payload_complete([dropped]) is False
    # resource_abort records are skipped, never passed.
    abort = dict(l2rec, outcome="resource_abort")
    assert l2q.ir_payload_complete([abort]) is True


def test_ir_payload_tables_descriptive():
    _, p2, view, _ = tiny_ir_fixture(n=32768, seed=TEST_SEEDS[5])
    n = 32768
    rng = np.random.default_rng(TEST_SEEDS[5])
    order = rng.permutation(n).astype(np.int64)
    k2 = int(l2q.FROZEN_K2)
    prefix = order[:k2]
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    hazards = p20o._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
    pm = float(np.mean(hazards[mask]))
    rec_a = dict(l2q._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": None, "first_error_coord": None},
        prefix_mean=pm),
        outcome="exact", arm="A_incumbent_L2_operational", block_index=0)
    pos = int(prefix[11])
    rec_b = dict(l2q._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": "L2", "first_error_coord": pos},
        prefix_mean=pm),
        outcome="verify_failed", arm="B_alt_L2_operational", block_index=0,
        first_error_layer="L2")
    tables = l2q.ir_payload_tables([rec_a, rec_b])
    assert tables["records_completed"] == 2
    assert tables["ir2_rank_pct_all"]["count"] == 1
    assert tables["ir2_rank_pct_b_operational"]["count"] == 1
    assert tables["ir2_rank_pct_a_operational"]["count"] == 0
    assert len(tables["ir1_histogram_rows"]) == 2
    assert tables["ir1_histogram_rows"][0]["prefix_mass"] == k2
    assert tables["ir1_histogram_rows"][0]["outside_mass"] == n - k2
    assert len(tables["ir3_threshold_rows"]) == 2
    assert tables["ir3_threshold_rows"][0]["thresh_hi_bits"] == 2.0 * pm
    assert len(tables["ir4_topk_rows"]) == 2
    assert tables["ir5_truncated_all"] is True
    assert tables["ir5_cap"] == 4096


# ---- truth isolation (recording-only, post-decode) ----

def test_truth_isolation_ir_recording_only(monkeypatch):
    counts = sparse_counts(TEST_SEEDS[6])
    arrays = p20o.raw_prior_arrays(counts)
    p2 = np.asarray(arrays["p2"], dtype=np.float64)
    p1 = np.asarray(arrays["p1"], dtype=np.float64)
    rng = np.random.default_rng(TEST_SEEDS[6])
    n = 64
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    block = {"block_index": 0, "frame_start": 2916, "frame_end": 2916,
             "high": high, "low": low, "bob": bob}
    view = {"bob": bob, "high": high, "low": low,
            "u2": np.zeros(n, dtype=np.int64)}
    result = opf.OperationalBlockResult(
        stream_seed=2916, block_index=0, outcome="exact", exact=True,
        label_match=True, tag_pass=True, l1_provenance=opf.Provenance.PRIOR_ONLY.value,
        l2_provenance=opf.Provenance.CANDIDATE_CONDITIONED.value, l1_executed=True,
        l1_decode_failed=False, l2_invoked=True, l2_skipped_by_l1_failure=False,
        l2_decode_failed=False, tag_invoked=True, key_dependent_bits=100,
        public_control_bits=FROZEN_PUBLIC_BITS, nonfinite=False,
        truth_leak_violation=False, l1_error_type=None, l2_error_type=None,
        wall_s=0.01, k1=331, k2=6689, l1_exact=True, hard_l2_exact=True,
        oracle_l2_exact=None, pair_exact=True, high_hat=high.copy(),
        low_hat=low.copy(), label_hat=(high * 32 + low).astype(np.int64))
    calls = []

    def hostile_ir_recorder(**kwargs):
        calls.append(dict(kwargs))
        # a recording-only call cannot feed anything back: poison the truth
        # it received after the decode has already completed.
        kwargs["view"]["low"][:] = (kwargs["view"]["low"] + 7) % 32
        return {field: "sentinel" for field in l2q.IR_FIELDS}

    monkeypatch.setattr(l2q, "_ir_hazard_diagnostics", hostile_ir_recorder)
    record = l2q._operational_record(
        result, spec=l2q.ArmSpec(
            "A_incumbent_L2_operational", "operational", 331, 6689,
            5 * 7020 + 64, l2q.OPERATIONAL_PROVENANCE, "incumbent"),
        arm_index=0, block=block,
        scoring=p20m._scoring_absent(), resources={},
        k_total=7020, budget_literal="test-budget-literal",
        prior_digest="0" * 64, alt_digest="0" * 64,
        order_digest="0" * 64, counts_arr=counts, p1=p1, p2=p2,
        l2_order=np.arange(n, dtype=np.int64), n=n, view=view, field=None)
    assert len(calls) == 1
    # the IR recorder is called post-decode with the hard-L1 candidate as
    # U1_cond on the operational arms, and its outputs land in the IR record
    # fields only.
    assert calls[0]["view"]["u1_cond"] is result.high_hat
    assert record["ir1_hist_prefix_counts"] == "sentinel"
    assert record["ir2_first_error_hazard_rank_pct"] == "sentinel"
    assert record["ir3_thresh_hi_bits"] == "sentinel"
    assert record["ir4_topk_coords"] == "sentinel"
    assert record["ir5_series_truncated"] == "sentinel"
    # decode-derived fields are exactly the pre-record result, untouched by
    # the post-decode truth mutation.
    assert record["outcome"] == "exact" and record["exact"] is True
    assert record["l1_exact"] is True and record["hard_l2_exact"] is True
    assert record["tag_pass"] is True and record["pair_exact"] is True
    assert record["first_error_layer"] is None
    assert record["first_error_coord"] is None
    assert record["arm"] == "A_incumbent_L2_operational"
    assert record["l2_construction"] == "incumbent"
    assert record["key_bit_delta_vs_control"] == 0
    assert record["protocol"] == l2q.PROTOCOL_NAME


def test_ir_truth_mutation_changes_recording_only():
    _, p2, view, order = tiny_ir_fixture()
    n = int(view["bob"].size)
    before = ir_recorder(view, p2, order,
                         {"first_error_layer": None,
                          "first_error_coord": None})
    mutated = {k: (np.array(v, copy=True) if isinstance(v, np.ndarray) else v)
               for k, v in view.items()}
    mutated["low"] = (np.asarray(view["low"]) + 7) % 32
    mutated["u1_cond"] = np.asarray(view["u1_cond"])
    after = ir_recorder(mutated, p2, order,
                        {"first_error_layer": None,
                         "first_error_coord": None})
    # truth enters the recording: mutating it changes the recorded payload.
    assert before["ir1_hist_prefix_counts"] != after["ir1_hist_prefix_counts"]
    # the recorder exposes no decoder input: its outputs are a plain dict of
    # record fields, and the decoder entry points take no IR argument.
    assert "ir" not in p20o.run_operational_block.__code__.co_varnames
    assert "ir" not in p20o.run_oracle_control_block.__code__.co_varnames
    assert n == 512


# ---- no Stage-B root + zero protected opens + zero Stage-B sampling ----

def test_no_stage_b_root_and_no_protected_opens_in_stage_a():
    assert not Path(l2q.FROZEN_OUT_ROOT).exists()
    assert Path(l2q.FROZEN_OUT_ROOT).name == "l2_alt_hold_ir_2m"
    assert l2q._DEV_PARQUET_CONTENT_OPENED is False
    assert l2q._ALT_CONTENT_LOADED is False
    assert l2q._SESSION_PRIOR_CONTENT_LOADED is False
    source = Path(l2q.__file__).read_text(encoding="utf-8")
    for token in ("load_v25_channel_counts", "smooth_joint_to_conditional",
                  "LAMBDA_STAR", "137.3823795883264", "--derive"):
        assert token not in source, token
    for token in ("_ir_hazard_diagnostics", "reuse_prior_identity",
                  "reuse_alt_identity", "reuse_order_freeze",
                  "verify_hold_containment", "verify_consumed_exclusions_hold",
                  "ir_payload_complete",                   "hold-confirmation-identity",
                  "HAZARD_FIELDS",
                  "nbpolar-p20q-hold-ir-2m-seed",
                  "from . import l2_alt_maintain_2m",
                  "verify_reuse", "run_l2_alt_hold_ir_2m",
                  "k_literal_exact",
                  "alt_construction_budget_feasibility_replayed",
                  "TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE"):
        assert token in source, token
    assert "2026092330" in source
    # the four frozen arms ride the accepted import target (same K, same
    # prefixes, zero disclosure delta by design).
    assert l2q.FROZEN_ARM_NAMES == p20o.FROZEN_ARM_NAMES == (
        "A_incumbent_L2_operational", "B_alt_L2_operational",
        "C_incumbent_L2_oracle", "D_alt_L2_oracle")
    # the nine carried scalars (incl. the ninth U-domain scalar) ride the
    # accepted import target's recorder, called at the carried-over code point.
    assert "l2_fail_in_prefix_u_domain" in p20o.HAZARD_FIELDS


def test_zero_stage_b_sampling_pin():
    parser = l2q.build_parser()
    options = set()
    for action in parser._actions:
        options.update(action.option_strings)
    for forbidden in ("--train-seeds", "--seed", "--sample", "--rng", "--genie",
                      "--deriv-seeds-stage-b", "--derive"):
        assert forbidden not in options, forbidden
    for name in l2q.STAGE_B_FLAGS:
        assert "seed" not in name and "sample" not in name
    assert "--verify-reuse" in options
    assert "seeds" not in l2q.run_l2_alt_hold_ir_2m.__code__.co_varnames
    assert "genie" not in l2q.run_l2_alt_hold_ir_2m.__code__.co_varnames
    source = Path(l2q.__file__).read_text(encoding="utf-8")
    assert "default_rng" not in source
    assert "sample_full_block" not in source


def test_one_open_guards_refuse_reload(monkeypatch):
    monkeypatch.setattr(
        l2q, "verify_predecessor_construction", lambda *a, **k: {"record": {}})
    monkeypatch.setattr(
        l2q, "verify_dev_manifest_2m",
        lambda *a, **k: {"train_pairs": 559872, "val_pairs": 186624,
                         "hold_pairs": 186624})
    monkeypatch.setattr(
        l2q, "verify_stage_b_order_file_2m",
        lambda *a, **k: {"verified": True, "order_digest": "x",
                         "l1_order": np.zeros(32768, dtype=np.int64),
                         "l2_order": np.zeros(32768, dtype=np.int64),
                         "k1": 334, "k2": 6746})
    base = dict(prior_path="p", prior_digest=l2q.FROZEN_SESSION_PRIOR_DIGEST,
                alt_prior_path="a", alt_digest=l2q.FROZEN_ALT_DIGEST,
                source="2M", floor=1e-15, n=32768, k1=334, k2=6746,
                construction="c",
                construction_digest=l2q.FROZEN_CONSTRUCTION_DIGEST,
                manifest_path="m", dev_pairs=l2q.FROZEN_DEV_PAIRS_PATH,
                order_file="o", order_digest=l2q.FROZEN_ORDER_DIGEST,
                tag_master=2026092330)
    with p20q_root() as root, restored_guards():
        out = str(root / "out")
        l2q._SESSION_PRIOR_CONTENT_LOADED = True
        assert_raises_match(ValueError, "reload refused",
                            l2q.run_l2_alt_hold_ir_2m, out_dir=out, **base)
        assert not Path(out).exists()
        l2q._SESSION_PRIOR_CONTENT_LOADED = False
        l2q._ALT_CONTENT_LOADED = True
        assert_raises_match(ValueError, "reload refused",
                            l2q.run_l2_alt_hold_ir_2m, out_dir=out,
                            prior={}, **base)
        assert not Path(out).exists()
        l2q._ALT_CONTENT_LOADED = False
        l2q._DEV_PARQUET_CONTENT_OPENED = True
        assert_raises_match(ValueError, "reopen refused",
                            l2q.run_l2_alt_hold_ir_2m, out_dir=out,
                            prior={}, alt_prior={}, **base)
        assert not Path(out).exists()


# ---- seed-domain grep rule ----

def test_grep_rule_seed_placement():
    master = "2026092330"
    test_seeds = [str(seed) for seed in TEST_SEEDS]
    module_source = Path(l2q.__file__).read_text(encoding="utf-8")
    test_source = Path(__file__).read_text(encoding="utf-8")
    assert master in module_source
    for seed in test_seeds:
        assert seed in test_source, seed
        assert seed not in module_source, seed
    assert l2q.FROZEN_TAG_MASTER == 2026092330
    assert l2q.FROZEN_TAG_MASTER not in (
        p20m.FROZEN_TAG_MASTER, p20l.FROZEN_TAG_MASTER,
        p20o.FROZEN_TAG_MASTER)
    allowed_prefixes = (
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_ir_2m.py",
        "comparison_bench/tests/test_nbpolar_l2_alt_hold_ir_2m.py",
        ".workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20q/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md",
    )
    for literal in [master] + test_seeds:
        for hit in _git_grep_hits(literal):
            assert hit.startswith(allowed_prefixes), (literal, hit)
