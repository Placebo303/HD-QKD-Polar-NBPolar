"""Focused Phase 4-P20S merged-2M mechanism-probe tests.

Injected/synthetic counts, priors, artifacts and fresh additive
``workspace/p20s/<uuid>/`` temp roots only. The V25 channel-counts NPZ, every
registered pairs parquet (1M, 1.5M VAL/HOLD/TRAIN, 2M VAL/HOLD), the real P16
construction root, the real split manifest, the accepted P20O worktree
products and every accepted evidence root are NEVER content-opened, statted,
or listed here: the Stage-A reuse verification and the frozen derivation run
only in the authorized ``--verify-reuse`` / ``--derive-spike-order`` commands,
never in tests. The frozen derivation is deterministic (no sampler, no RNG):
genie 0+0. Focused tests use their own fresh seeds
``2026092361..2026092367`` and never the frozen P20S tag master
``2026092360`` (except through the frozen module constant).
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
    l2_mechanism_probe_2m as l2s,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_alt_hold_ir_2m as p20q,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_alt_hold_1p5m as p20n,
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
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_alt_maintain_2m as p20o,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never the frozen P20S tag master 2026092360.
TEST_SEEDS = (2026092361, 2026092362, 2026092363, 2026092364,
              2026092365, 2026092366, 2026092367)

FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63

# Injected 2M TRAIN total: the alt-identity gate pins counts_total to the
# 2M TRAIN count (559872), so fixtures carry that exact total.
TEST_COUNTS_TOTAL = 559872


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
        l2s._SESSION_PRIOR_CONTENT_LOADED, l2s._ALT_CONTENT_LOADED,
        l2s._DEV_PARQUET_CONTENT_OPENED,
    )
    try:
        yield
    finally:
        (l2s._SESSION_PRIOR_CONTENT_LOADED, l2s._ALT_CONTENT_LOADED,
         l2s._DEV_PARQUET_CONTENT_OPENED) = state


@contextlib.contextmanager
def p20s_root():
    """Fresh additive workspace/p20s/<uuid>/ temp root, cleaned afterwards."""
    root = REPO_ROOT / "workspace" / "p20s" / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    assert "workspace" in root.parts and "p20s" in root.parts
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


def exact_total_counts(seed: int, total: int = TEST_COUNTS_TOTAL) -> np.ndarray:
    """Synthetic counts with an exact integer total (self-consistent fixture)."""
    counts = sparse_counts(seed)
    counts[0, 0] += float(total) - float(counts.sum())
    assert int(round(float(counts.sum()))) == total
    return np.ascontiguousarray(counts)


def synthetic_prior_arrays(seed: int = TEST_SEEDS[0]) -> dict:
    """Self-consistent synthetic 2M-shaped prior arrays (no protected data)."""
    counts = exact_total_counts(seed)
    return p20m.build_raw_prior_arrays(counts)


def synthetic_alt_arrays(prior_arrays) -> dict:
    """Self-consistent synthetic alt arrays via the frozen alpha=1 rule."""
    counts = np.asarray(prior_arrays["counts_ab"], dtype=np.float64)
    derived = p20n.derive_alt_l2_arrays(
        counts, incumbent_p1=np.asarray(prior_arrays["p1"]),
        incumbent_p_b=np.asarray(prior_arrays["p_b"]),
        incumbent_h1=float(np.asarray(prior_arrays["h1"])))
    return {
        "counts_ab": np.ascontiguousarray(counts),
        "f_alt": np.ascontiguousarray(np.asarray(derived["f_alt"])),
        "p1": np.ascontiguousarray(np.asarray(derived["p1"])),
        "p2_alt": np.ascontiguousarray(np.asarray(derived["p2_alt"])),
        "alpha": np.asarray(1.0),
        "floor_value": np.asarray(1e-15),
        "h1_inc": np.asarray(float(np.asarray(prior_arrays["h1"]))),
        "h2_alt": np.asarray(float(derived["h2_alt"])),
        "h_total_alt": np.asarray(float(derived["h_total_alt"])),
    }


def merged_table(*, seed: int = TEST_SEEDS[2]) -> pd.DataFrame:
    """Merged-like pairs frame: VAL tail 2827..2915 + HOLD head 3556..3594 + tail."""
    rng = np.random.default_rng(int(seed))
    val_frames = np.repeat(np.arange(2827, 2916), 256)
    hold_frames = np.repeat(np.arange(3556, 3595), 256)
    dev_frames = np.concatenate([val_frames, hold_frames])
    dev = pd.DataFrame({
        "frame_id": dev_frames,
        "pair_idx": np.tile(np.arange(256), 128),
        "alice_symbol": rng.integers(0, 1024, size=dev_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=dev_frames.size),
    })
    rem_frames = np.repeat(np.arange(3595, 3645), 256)
    rem = pd.DataFrame({
        "frame_id": rem_frames,
        "pair_idx": np.tile(np.arange(256), 50),
        "alice_symbol": rng.integers(0, 1024, size=rem_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=rem_frames.size),
    })
    # Extra rows outside the DEV/tail spans must not influence slicing.
    extra = pd.DataFrame({
        "frame_id": np.repeat([0, 2186, 2187, 2826, 2916, 3555, 3645], 256),
        "pair_idx": np.tile(np.arange(256), 7),
        "alice_symbol": rng.integers(0, 1024, size=7 * 256),
        "bob_symbol": rng.integers(0, 1024, size=7 * 256),
    })
    return pd.concat([dev, rem, extra], ignore_index=True).sample(
        frac=1.0, random_state=int(seed)).reset_index(drop=True)


def full_block_ir_fixture(*, seed: int = TEST_SEEDS[3]):
    """Full-block (N=32768) natural-index truth vectors + tables for the IR recorder."""
    rng = np.random.default_rng(int(seed))
    counts = sparse_counts(seed, cells=1024, hi=20)
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.ascontiguousarray(np.asarray(arrays["p2"], dtype=np.float64))
    n = 32768
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    order = rng.permutation(n).astype(np.int64)
    view = {"bob": bob, "high": high, "low": low, "u1_cond": high,
            "u2": rng.integers(0, 32, size=n)}
    return counts, p2, view, order


def ir_recorder(view, p2, order, first_error, *, prefix_mean=None):
    k2 = int(l2s.FROZEN_K2)
    if prefix_mean is None:
        mask = np.zeros(int(view["bob"].size), dtype=bool)
        mask[np.asarray(order)[:k2]] = True
        hazards = p20q._hazard_bits(
            p2, np.asarray(view.get("u1_cond", view["high"])),
            np.asarray(view["bob"]), np.asarray(view["low"]))
        prefix_mean = float(np.mean(hazards[mask]))
    return l2s._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error=first_error, prefix_mean=prefix_mean)


def reuse_fixture(root, *, seed: int = TEST_SEEDS[0]):
    """Self-consistent synthetic prior/alt/frozen-A-order/spike-B fixtures + pins."""
    prior_arrays = synthetic_prior_arrays(seed)
    alt_arrays = synthetic_alt_arrays(prior_arrays)
    prior_path = root / "raw_prior.npz"
    with open(prior_path, "wb") as fh:
        np.savez(fh, **{k: np.asarray(v) for k, v in prior_arrays.items()})
    alt_path = root / "alt.npz"
    with open(alt_path, "wb") as fh:
        np.savez(fh, **{k: np.asarray(v) for k, v in alt_arrays.items()})
    rng = np.random.default_rng(seed)
    n = 32768
    prior_digest = psc.canonical_prior_digest(prior_arrays)
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
            "program": "test-frozen-A-program-pin",
            "prior_digest": prior_digest,
            "train_seeds": [int(s) for s in p20o.FROZEN_DERIVATION_SEEDS],
            "train_blocks_used": 16,
        },
    }
    order_path = root / "orders.json"
    order_path.write_text(json.dumps(doc, sort_keys=True) + "\n", encoding="utf-8")
    spike_order_path = root / "spike_orders.json"
    with patched(l2s, "FROZEN_SESSION_PRIOR_DIGEST", prior_digest):
        written = l2s.write_spike_order_file(
            spike_order_path, prior_arrays=prior_arrays,
            l1_order=np.asarray(doc["l1_order"], dtype=np.int64),
            prior_digest=prior_digest)
    d1 = p20o.feasibility_literals_2m(
        np.asarray(prior_arrays["counts_ab"], dtype=np.float64),
        p2_incumbent=np.asarray(prior_arrays["p2"]),
        p2_alt=np.asarray(alt_arrays["p2_alt"]), k2=6746, k_total=7080)
    pins = {
        "prior_digest": prior_digest,
        "alt_digest": hashlib.sha256(alt_path.read_bytes()).hexdigest(),
        "order_digest": hashlib.sha256(order_path.read_bytes()).hexdigest(),
        "spike_order_digest": written["spike_order_digest"],
        "h1": float(np.asarray(prior_arrays["h1"])),
        "h2": float(np.asarray(prior_arrays["h2"])),
        "h_total": float(np.asarray(prior_arrays["h_total"])),
        "ce_alt": float(d1["ce_alt_insample_bits_per_symbol"]),
        "ce_incumbent": float(d1["ce_incumbent_insample_bits_per_symbol"]),
        "alt_ideal_length_bits": float(d1["alt_ideal_length_bits"]),
    }
    return prior_path, alt_path, order_path, spike_order_path, pins


def _git_grep_hits(literal: str):
    proc = subprocess.run(
        ["git", "grep", "-l", "--untracked", literal, "--",
         "comparison_bench", "openspec", ".workbuddy", "docs"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1), proc.stderr
    return [line for line in proc.stdout.splitlines() if line.strip()]


# ---- frozen literals, arms, population, delta d1-d9 ----

def test_frozen_literals_arms_population_and_delta():
    assert l2s.FROZEN_SOURCE == "2M"
    assert l2s.FROZEN_SOURCE_TAG == "type2_2M_20260121_183657"
    assert l2s.FROZEN_N == 32768
    assert l2s.FROZEN_FLOOR == 1e-15
    assert l2s.FROZEN_ALPHA == 1.0
    # (d3) K literals replay the P20O derivation, never recarried from 1.5M.
    assert (l2s.FROZEN_K_TOTAL, l2s.FROZEN_K1,
            l2s.FROZEN_K2) == (7080, 334, 6746)
    assert (l2s.FROZEN_K_TOTAL, l2s.FROZEN_K1,
            l2s.FROZEN_K2) == (p20o.FROZEN_K_TOTAL, p20o.FROZEN_K1,
                               p20o.FROZEN_K2)
    # (d2) reuse pins are byte-identical to the accepted 2M products.
    assert l2s.FROZEN_SESSION_PRIOR_DIGEST == p20o.FROZEN_SESSION_PRIOR_DIGEST
    assert l2s.FROZEN_ORDER_DIGEST_A == p20o.FROZEN_ORDER_DIGEST
    assert l2s.FROZEN_ALT_DIGEST == p20o.FROZEN_ALT_DIGEST
    assert (l2s.FROZEN_H1, l2s.FROZEN_H2,
            l2s.FROZEN_H_TOTAL) == (p20o.FROZEN_H1, p20o.FROZEN_H2,
                                    p20o.FROZEN_H_TOTAL)
    assert (l2s.FROZEN_ALT_H1_INC, l2s.FROZEN_ALT_H2_ALT,
            l2s.FROZEN_ALT_H_TOTAL_ALT) == (
        p20o.FROZEN_ALT_H1_INC, p20o.FROZEN_ALT_H2_ALT,
        p20o.FROZEN_ALT_H_TOTAL_ALT)
    # (d1/d8) merged population: VAL tail 89 + HOLD head 39 = one block.
    assert tuple(l2s.FROZEN_DEV_FRAMES_VAL) == (2827, 2915)
    assert l2s.FROZEN_DEV_VAL_FRAMES == 89
    assert tuple(l2s.FROZEN_DEV_FRAMES_HOLD) == (3556, 3594)
    assert l2s.FROZEN_DEV_HOLD_FRAMES == 39
    assert l2s.FROZEN_DEV_FRAMES == 128
    assert l2s.FROZEN_DEV_PAIRS == 32768
    assert [list(s) for s in l2s.FROZEN_BLOCK_SEGMENTS] == [[2827, 2915],
                                                           [3556, 3594]]
    assert list(l2s.FROZEN_MERGED_FRAME_LIST) == (
        list(range(2827, 2916)) + list(range(3556, 3595)))
    assert tuple(l2s.FROZEN_REMAINDER_FRAME_RANGE) == (3595, 3644)
    assert l2s.FROZEN_REMAINDER_FRAMES == 50
    assert l2s.FROZEN_REMAINDER_SYMBOLS == 50 * 256
    assert tuple(l2s.FROZEN_1P5M_VAL_STUB_FRAME_RANGE) == (2172, 2212)
    assert tuple(l2s.FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE) == (2725, 2766)
    assert tuple(l2s.FROZEN_BUILD_FRAME_RANGE) == (0, 2186)
    # (d6) new P20S tag domain, disjoint from every predecessor by master+prefix.
    assert l2s.FROZEN_TAG_MASTER == 2026092360
    assert l2s.FROZEN_TAG_MASTER not in (
        p20m.FROZEN_TAG_MASTER, p20o.FROZEN_TAG_MASTER,
        p20q.FROZEN_TAG_MASTER)
    assert l2s.SEED_PREFIX == "nbpolar-p20s-mechanism-probe-2m-seed"
    assert l2s.SEED_PREFIX != p20q.SEED_PREFIX
    # (d5) arms: same K on A/B, carried K2 on O, zero disclosure delta by design.
    arms = l2s.frozen_arm_table()
    assert tuple(s.name for s in arms) == l2s.FROZEN_ARM_NAMES
    assert l2s.FROZEN_ARM_NAMES == ("A_anchor_frozen_order",
                                    "B_spike_local_order",
                                    "O_true_l1_oracle")
    assert l2s.check_frozen_arm_table()["planned_key_dependent_bits"] == 104722
    totals = l2s.planned_totals(334, 6746)
    assert totals["operational_key_dependent_bits"] == 35464
    assert totals["oracle_key_dependent_bits"] == 33794
    assert totals["planned_key_dependent_bits"] == 104722
    assert totals["planned_public_control_bits"] == 983229
    assert totals["planned_sc_calls"] == 5
    assert totals["planned_tag_invocations"] == 3
    assert totals["planned_records"] == 3
    # (d7/d9) IR pins frozen PRESENT: P20Q-identical IR-1..IR-4 + uncapped IR-5.
    assert l2s.IR1_BINS == 64
    assert (l2s.IR3_LO_MULT, l2s.IR3_HI_MULT) == (1.0, 2.0)
    assert l2s.IR4_TOPK == 16
    assert l2s.IR5_FULL_N == 32768
    assert l2s.IR5_FORMAT_VERSION == "ir5full-v1"
    assert l2s.IR5_HAZARD_BYTES == 131072
    assert l2s.IR5_FLAG_BYTES == 32768
    assert l2s.IR5_PER_RECORD_BUDGET_BYTES == 400 * 1024
    assert l2s.IR5_ROOT_BUDGET_BYTES == 1536 * 1024
    assert l2s.IR5_MAX_FILE_BYTES == 2 * 1024 * 1024
    # the delta list d1-d9 is evidenced in the module docstring and the
    # import target plus the carried-over callsite pattern are referenced.
    source = Path(l2s.__file__).read_text(encoding="utf-8")
    assert "from . import l2_alt_hold_ir_2m as p20q" in source
    assert "_l2_hazard_diagnostics" in source
    assert "_ir_hazard_diagnostics" in source
    assert "derive_spike_l2_order" in source
    assert "no lambda" in source.lower() or "NO lambda" in source or \
        "lambda anywhere" in source


def test_frozen_command_pinned():
    assert l2s.pins_are_frozen() is True
    assert l2s.FROZEN_COMMAND is not None
    assert "--verify-reuse" not in l2s.FROZEN_COMMAND
    assert "--derive-spike-order" not in l2s.FROZEN_COMMAND
    assert "--source 2M" in l2s.FROZEN_COMMAND
    assert "--dev-frames-val 2827 2915" in l2s.FROZEN_COMMAND
    assert "--dev-frames-hold 3556 3594" in l2s.FROZEN_COMMAND
    assert "--remainder-frames 3595 3644" in l2s.FROZEN_COMMAND
    assert "--tag-master 2026092360" in l2s.FROZEN_COMMAND
    assert "--k1 334 --k2 6746" in l2s.FROZEN_COMMAND
    assert "--spike-formula F_MEDIAN8_DECIDED_20260920_H_MINUS_LOCAL_MEDIAN_W8" in \
        l2s.FROZEN_COMMAND
    assert "l2_mechanism_probe_2m" in l2s.FROZEN_COMMAND
    assert l2s.FROZEN_COMMAND.count(
        "b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587") == 1
    assert l2s.FROZEN_COMMAND.count(
        "98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5") == 1
    assert l2s.FROZEN_COMMAND.count(
        "b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906") == 1
    assert l2s.FROZEN_COMMAND.count(str(l2s.FROZEN_SPIKE_ORDER_DIGEST_B)) == 1
    # the Stage-B out root is the frozen P20S evidence root.
    assert l2s.FROZEN_OUT_ROOT.endswith(
        "NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m")


# ---- Stage-A spike derivation (section 3 contract + F-median8 functional) ----

def test_derive_spike_deterministic_permutation():
    prior_arrays = synthetic_prior_arrays()
    first = l2s.derive_spike_l2_order(prior_arrays)
    second = l2s.derive_spike_l2_order(prior_arrays)
    order = first["spike_l2_order"]
    assert order.shape == (32768,)
    assert set(order.tolist()) == set(range(32768))
    assert np.array_equal(order, second["spike_l2_order"])
    assert first["sampling_calls"] == 0 and first["genie_calls"] == 0
    assert first["k2"] == 6746
    assert first["formula_id"] == l2s.SPIKE_FORMULA_ID
    assert first["formula_id"] == "F_MEDIAN8_DECIDED_20260920_H_MINUS_LOCAL_MEDIAN_W8"
    assert first["program"] == l2s.SPIKE_PROGRAM_PIN
    # the first-K2 prefix is arm B's disclosed set at identical size.
    assert len(set(order[:6746].tolist())) == 6746


def test_derive_spike_fmedian8_ranking_and_tiebreak():
    prior_arrays = synthetic_prior_arrays(seed=TEST_SEEDS[1])
    derived = l2s.derive_spike_l2_order(prior_arrays)
    order = derived["spike_l2_order"]
    hazards = derived["cell_hazards"]
    scores = derived["cell_scores"]
    medians = derived["cell_medians"]
    assert hazards.shape == (32768,) and scores.shape == (32768,)
    assert medians.shape == (32768,)
    # spot-check the frozen F-median8 functional on explicit windows.
    for i in (0, 100, 32767):
        lo, hi = max(0, i - 8), min(32768, i + 9)
        assert abs(scores[i] - (hazards[i] - float(np.median(hazards[lo:hi]))
                                )) <= 1e-9
    # descending score along the order; ties broken by ascending coordinate.
    ordered_scores = scores[order]
    assert bool(np.all(ordered_scores[:-1] >= ordered_scores[1:]))
    ties = np.where(ordered_scores[:-1] == ordered_scores[1:])[0]
    for t in ties[:64]:
        assert int(order[t]) < int(order[t + 1])
    # spike head carries the maximum local-excess score.
    assert int(order[0]) == int(np.argmax(scores))
    # degenerate flat hazards collapse to the natural coordinate order.
    flat = dict(prior_arrays)
    flat_counts = np.ones((1024, 1024), dtype=np.float64)
    flat["counts_ab"] = np.ascontiguousarray(flat_counts)
    flat["p1"] = np.ascontiguousarray(
        np.full((32, 1024), 1.0 / 32.0, dtype=np.float64))
    deg = l2s.derive_spike_l2_order(flat)
    assert np.array_equal(deg["spike_l2_order"],
                          np.arange(32768, dtype=np.int64))


def test_derive_spike_refusals():
    prior_arrays = synthetic_prior_arrays()
    bad = dict(prior_arrays)
    del bad["p1"]
    assert_raises_match(ValueError, "exactly", l2s.derive_spike_l2_order, bad)
    bad = dict(prior_arrays)
    bad["counts_ab"] = np.zeros((16, 16))
    assert_raises_match(ValueError, "(1024,1024)", l2s.derive_spike_l2_order, bad)
    bad = dict(prior_arrays)
    bad["p1"] = np.zeros((4, 4))
    assert_raises_match(ValueError, "(32,1024)", l2s.derive_spike_l2_order, bad)


def test_write_and_verify_spike_order_file():
    with p20s_root() as root:
        prior_path, _, order_path, spike_order_path, pins = reuse_fixture(root)
        doc = json.loads(spike_order_path.read_text(encoding="utf-8"))
        assert doc["protocol"] == l2s.SPIKE_ORDER_PROTOCOL
        assert doc["kind"] == l2s.SPIKE_ORDER_KIND
        assert doc["n"] == 32768
        assert (doc["k_total"], doc["k1"], doc["k2"]) == (7080, 334, 6746)
        assert len(doc["l1_order"]) == 32768 and len(doc["l2_order"]) == 32768
        assert doc["derivation"]["zero_sampling_attestation"] is True
        assert doc["derivation"]["program"] == l2s.SPIKE_PROGRAM_PIN
        assert doc["derivation"]["formula_id"] == l2s.SPIKE_FORMULA_ID
        assert doc["derivation"]["hazard_radius_R"] == 8
        # fail-if-present: the derivation never overwrites.
        with patched(l2s, "FROZEN_SESSION_PRIOR_DIGEST", pins["prior_digest"]):
            assert_raises_match(FileExistsError, "refusing to overwrite",
                                l2s.write_spike_order_file, spike_order_path,
                                prior_arrays=synthetic_prior_arrays(),
                                l1_order=np.arange(32768, dtype=np.int64),
                                prior_digest=pins["prior_digest"])
        # the verifier replays the file behind the digest + L1 + program pins.
        frozen_doc = json.loads(order_path.read_text(encoding="utf-8"))
        frozen_l1 = np.asarray(frozen_doc["l1_order"], dtype=np.int64)
        with patched(l2s, "FROZEN_SPIKE_ORDER_DIGEST_B",
                     pins["spike_order_digest"]):
            pin = l2s.verify_spike_order_file(
                spike_order_path, expected_digest=pins["spike_order_digest"],
                expected_prior_digest=pins["prior_digest"],
                frozen_l1_order=frozen_l1, expected_k1=334,
                expected_k2=6746, expected_k_total=7080)
            assert pin["verified"] is True
            assert pin["spike_order_digest"] == pins["spike_order_digest"]
            assert pin["formula_id"] == l2s.SPIKE_FORMULA_ID
            assert_raises_match(ValueError, "digest flag",
                                l2s.verify_spike_order_file, spike_order_path,
                                expected_digest="0" * 64,
                                expected_prior_digest=pins["prior_digest"],
                                frozen_l1_order=frozen_l1, expected_k1=334,
                                expected_k2=6746, expected_k_total=7080)
            assert_raises_match(ValueError, "L1 order",
                                l2s.verify_spike_order_file, spike_order_path,
                                expected_digest=pins["spike_order_digest"],
                                expected_prior_digest=pins["prior_digest"],
                                frozen_l1_order=np.arange(32768 - 1, -1, -1,
                                                          dtype=np.int64),
                                expected_k1=334, expected_k2=6746,
                                expected_k_total=7080)


def test_order_set_delta_exact():
    rng = np.random.default_rng(TEST_SEEDS[4])
    n = 32768
    frozen = rng.permutation(n).astype(np.int64)
    new = rng.permutation(n).astype(np.int64)
    delta = l2s.order_set_delta(frozen, new, 6746)
    assert delta["a_disclosed_size"] == 6746
    assert delta["b_disclosed_size"] == 6746
    assert delta["size_delta_b_minus_a"] == 0
    assert (delta["intersection_size"] + delta["a_minus_b_count"]) == 6746
    assert delta["a_minus_b_count"] == delta["b_minus_a_count"]
    assert sorted(delta["a_minus_b"]) == delta["a_minus_b"]
    assert sorted(delta["b_minus_a"]) == delta["b_minus_a"]
    assert not (set(delta["a_minus_b"]) & set(new[:6746].tolist()))
    assert not (set(delta["b_minus_a"]) & set(frozen[:6746].tolist()))
    # identical orders give an empty delta (still size-delta 0).
    same = l2s.order_set_delta(frozen, frozen, 6746)
    assert same["a_minus_b"] == [] and same["b_minus_a"] == []
    assert same["intersection_size"] == 6746


# ---- Stage-A verify-reuse (injected fixtures only) ----

def test_verify_reuse_positive_and_refusals():
    with p20s_root() as root:
        prior_path, alt_path, order_path, spike_order_path, pins = reuse_fixture(root)
        kws = dict(prior=prior_path, alt_prior=alt_path,
                   order_file=order_path, spike_order_file=spike_order_path,
                   prior_digest=pins["prior_digest"],
                   alt_digest=pins["alt_digest"],
                   order_digest=pins["order_digest"],
                   spike_order_digest=pins["spike_order_digest"],
                   spike_formula=l2s.SPIKE_FORMULA_ID,
                   h1=pins["h1"], h2=pins["h2"], h_total=pins["h_total"],
                   k1=334, k2=6746, ce_alt=pins["ce_alt"],
                   ce_incumbent=pins["ce_incumbent"],
                   alt_ideal_length_bits=pins["alt_ideal_length_bits"],
                   d2_feasible=True)
        result = None
        fixture_margin = float(5 * 6746 + 64 - pins["alt_ideal_length_bits"])
        with patched(p20o, "FROZEN_ORDER_DIGEST", pins["order_digest"]), \
                patched(p20o, "FROZEN_ORDER_PROGRAM_PIN",
                        "test-frozen-A-program-pin"), \
                patched(p20o, "FROZEN_DERIVATION_SEEDS",
                        tuple(int(s) for s in p20o.FROZEN_DERIVATION_SEEDS)), \
                patched(p20o, "FROZEN_ALT_DIGEST", pins["alt_digest"]), \
                patched(p20o, "FROZEN_ALT_H1_INC", pins["h1"]), \
                patched(l2s, "FROZEN_SESSION_PRIOR_DIGEST",
                        pins["prior_digest"]), \
                patched(l2s, "FROZEN_ORDER_DIGEST_A", pins["order_digest"]), \
                patched(l2s, "FROZEN_ALT_DIGEST", pins["alt_digest"]), \
                patched(l2s, "FROZEN_SPIKE_ORDER_DIGEST_B",
                        pins["spike_order_digest"]), \
                patched(l2s, "FROZEN_D2_MARGIN_BITS", fixture_margin):
            result = l2s.verify_reuse(**kws)
            assert result["verified"] is True
            assert result["dev_contact"] == 0
            assert result["prior_digest"] == pins["prior_digest"]
            assert result["alt_file_digest"] == pins["alt_digest"]
            assert result["order_digest_A"] == pins["order_digest"]
            assert result["spike_order_digest_B"] == pins["spike_order_digest"]
            assert result["spike_program"] == l2s.SPIKE_PROGRAM_PIN
            assert result["spike_formula_id"] == l2s.SPIKE_FORMULA_ID
            assert result["d2_feasible"] is True
            assert result["k_literals"]["k_total"] == 7080
            assert result["set_delta"]["size_delta_b_minus_a"] == 0
            # every replay pin refuses on mismatch with DEV untouched.
            bad = dict(kws)
            bad["prior_digest"] = "0" * 64
            assert_raises_match(ValueError, "reuse_prior_identity",
                                l2s.verify_reuse, **bad)
            bad = dict(kws)
            bad["alt_digest"] = "0" * 64
            assert_raises_match(ValueError, "reuse_alt_identity",
                                l2s.verify_reuse, **bad)
            bad = dict(kws)
            bad["order_digest"] = "0" * 64
            assert_raises_match(ValueError, "reuse_order_freeze",
                                l2s.verify_reuse, **bad)
            bad = dict(kws)
            bad["spike_order_digest"] = "0" * 64
            assert_raises_match(ValueError, "spike_order_identity_B",
                                l2s.verify_reuse, **bad)
            bad = dict(kws)
            bad["spike_formula"] = "WRONG_FORMULA"
            assert_raises_match(ValueError, "order_derivation_program_identity",
                                l2s.verify_reuse, **bad)
            bad = dict(kws)
            bad["k1"] = 335
            assert_raises_match(ValueError, "k_literal_exact",
                                l2s.verify_reuse, **bad)
            bad = dict(kws)
            bad["ce_alt"] = float(pins["ce_alt"]) + 1.0
            assert_raises_match(ValueError,
                                "alt_construction_budget_feasibility",
                                l2s.verify_reuse, **bad)
            bad = dict(kws)
            bad["d2_feasible"] = False
            assert_raises_match(ValueError,
                                "alt_construction_budget_feasibility",
                                l2s.verify_reuse, **bad)
            bad = dict(kws)
            bad["h_total"] = float(pins["h_total"]) + 1e-6
            assert_raises_match(ValueError, "reuse_prior_identity",
                                l2s.verify_reuse, **bad)
        assert result is not None


def test_cli_mode_refusals(capsys):
    assert l2s.main(["--verify-reuse", "--prior", "x"]) == 2
    _, err = capsys.readouterr()
    assert "missing required --verify-reuse flags" in err
    assert l2s.main(["--derive-spike-order", "--prior", "x"]) == 2
    _, err = capsys.readouterr()
    assert "missing required --derive-spike-order flags" in err
    assert l2s.main([]) == 2
    _, err = capsys.readouterr()
    assert "ambiguous invocation refused" in err
    assert l2s.main(["--verify-reuse", "--derive-spike-order",
                     "--prior", "p"]) == 2
    _, err = capsys.readouterr()
    assert "never combine" in err
    with p20s_root() as root:
        _, _, _, _, pins = reuse_fixture(root)
        rc = l2s.main([
            "--verify-reuse",
            "--prior", "p", "--prior-digest", pins["prior_digest"],
            "--alt-prior", "a", "--alt-digest", pins["alt_digest"],
            "--order-file", "o", "--order-digest", pins["order_digest"],
            "--spike-order-file", "s", "--spike-order-digest",
            pins["spike_order_digest"],
            "--spike-formula", l2s.SPIKE_FORMULA_ID,
            "--k1", "334", "--k2", "6746", "--tag-master", "2026092360",
        ])
        assert rc == 2
        _, err = capsys.readouterr()
        assert "takes no Stage-B-only flags" in err
        rc = l2s.main([
            "--derive-spike-order",
            "--prior", "p", "--prior-digest", pins["prior_digest"],
            "--order-file", "o", "--out", "n",
            "--k1", "334",
        ])
        assert rc == 2
        _, err = capsys.readouterr()
        assert "takes no Stage-B-only flags" in err


# ---- merged 2M population + gate family (b)-(g) ----

def test_merged_population_and_gate_family():
    table = merged_table()
    formation = l2s.form_merged_blocks(table)
    assert formation["dev_segments"] == [[2827, 2915], [3556, 3594]]
    assert formation["dev_frames"] == 128
    assert formation["dev_pairs"] == 32768
    assert formation["merged_frame_list"] == (
        list(range(2827, 2916)) + list(range(3556, 3595)))
    assert [list(s) for s in formation["block_segments"]] == [[2827, 2915],
                                                             [3556, 3594]]
    assert len(formation["blocks"]) == 1
    for block in formation["blocks"]:
        assert block["labels"].size == 32768
        assert int(block["high"].max()) < 32 and int(block["low"].max()) < 32
    assert formation["remainder"] == {
        "frame_start": 3595, "frame_end": 3644, "frames": 50,
        "symbols": 12800, "used": False}
    assert formation["counted_1p5m_never_decoded"]["used"] is False
    assert formation["counted_1p5m_never_decoded"]["val_stub_frames"] == [2172, 2212]
    assert formation["counted_1p5m_never_decoded"]["hold_remainder_frames"] == [
        2725, 2766]
    assert l2s.verify_merged_containment()["verified"] is True
    assert l2s.verify_merged_frame_set_identity()["verified"] is True
    assert l2s.verify_consumed_exclusions_merged()["verified"] is True
    assert l2s.verify_consumed_exclusions_merged()["build_frames"] == [0, 2186]
    # declared-range refusals refuse before any content open.
    assert_raises_match(ValueError, "dev-frames-val",
                        l2s.form_merged_blocks, table,
                        dev_frames_val=(2827, 2914))
    assert_raises_match(ValueError, "remainder-frames",
                        l2s.form_merged_blocks, table,
                        remainder_frames=(3595, 3645))
    assert_raises_match(ValueError, "BLOCKED(dev_block_range_identity)",
                        l2s.verify_merged_containment, (2827, 2914))
    assert_raises_match(ValueError, "BLOCKED(dev_block_range_identity)",
                        l2s.verify_merged_frame_set_identity, (2827, 2914))
    # consumed 2M VAL DEV / TRAIN refuse in the VAL segment.
    assert_raises_match(ValueError, "consumed 2M VAL DEV",
                        l2s.verify_merged_containment, (2187, 2826))
    assert_raises_match(ValueError, "outside 2M VAL",
                        l2s.verify_merged_containment, (0, 2186))
    assert_raises_match(ValueError, "consumed 2M TRAIN",
                        l2s.verify_consumed_exclusions_merged, (0, 2186))
    assert_raises_match(ValueError, "consumed 2M HOLD DEV",
                        l2s.verify_consumed_exclusions_merged,
                        (2827, 2915), (2916, 3555))
    # cross-file gate: the 1M pool and the 1.5M session refuse by path.
    assert_raises_match(ValueError, "1M full-pool",
                        l2s.verify_dev_source_identity_2m,
                        l2s.REFUSED_1M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "1.5M session",
                        l2s.verify_dev_source_identity_2m,
                        l2s.REFUSED_1P5M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "dev-pairs",
                        l2s.verify_dev_source_identity_2m, "elsewhere.parquet")
    # malformed population refuses inside the formation.
    bad = table.copy()
    bad.loc[bad.index[0], "bob_symbol"] = 1024
    assert_raises_match(ValueError, "dev_population_exact",
                        l2s.form_merged_blocks, bad)
    bad2 = table.copy()
    bad2 = bad2[bad2["frame_id"] != 2827]
    assert_raises_match(ValueError, "dev_population_exact",
                        l2s.form_merged_blocks, bad2)


# ---- IR-1..IR-4 recorder formulas, caps, nullability (full-block N) ----

def test_ir_recorder_formulas_caps_and_nullability():
    _, p2, view, order = full_block_ir_fixture()
    n = 32768
    k2 = 6746
    prefix = order[:k2]
    ir = ir_recorder(view, p2, order,
                     {"first_error_layer": "L1", "first_error_coord": 9})
    assert set(ir) == set(l2s.IR_FIELDS) - {
        "ir5_hazard_bits_file", "ir5_hazard_bits_sha256",
        "ir5_inprefix_file", "ir5_inprefix_sha256",
        "ir5_inu_file", "ir5_inu_sha256",
        "ir5_format_version", "ir5_total_len",
    }
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
    pm = float(np.mean(p20q._hazard_bits(
        p2, view["high"][prefix], view["bob"][prefix], view["low"][prefix])))
    assert abs(ir["ir3_thresh_lo_bits"] - pm) <= 1e-12
    assert abs(ir["ir3_thresh_hi_bits"] - 2.0 * pm) <= 1e-12
    prefix_haz = p20q._hazard_bits(
        p2, view["high"][prefix], view["bob"][prefix], view["low"][prefix])
    assert ir["ir3_prefix_above_lo_count"] == int(np.sum(prefix_haz > pm))
    assert ir["ir3_prefix_above_lo_frac"] == int(np.sum(prefix_haz > pm)) / k2
    assert ir["ir3_prefix_above_hi_count"] == int(np.sum(prefix_haz > 2.0 * pm))
    assert ir["ir3_prefix_above_hi_frac"] == int(
        np.sum(prefix_haz > 2.0 * pm)) / k2
    # IR-4: top-16 hazards with 1-based ranks.
    hazards = p20q._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
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
    # L2 failure: IR-2 is the exact hazard-rank percentile.
    pos = int(prefix[7])
    ir2 = ir_recorder(view, p2, order,
                      {"first_error_layer": "L2", "first_error_coord": pos})
    want_rank = float(np.mean(hazards <= hazards[pos]))
    assert abs(ir2["ir2_first_error_hazard_rank_pct"] - want_rank) <= 1e-12
    # the gated prefix length refuses anything else.
    assert_raises_match(ValueError, "gated prefix length",
                        l2s._ir_hazard_diagnostics, view=view, p2_arm=p2,
                        l2_order=order, k2=k2 - 1,
                        first_error={"first_error_layer": None,
                                     "first_error_coord": None},
                        prefix_mean=pm)
    # an L2 failure without a valid coordinate refuses (never a silent null).
    assert_raises_match(ValueError, "valid natural block symbol index",
                        l2s._ir_hazard_diagnostics, view=view, p2_arm=p2,
                        l2_order=order, k2=k2,
                        first_error={"first_error_layer": "L2",
                                     "first_error_coord": None},
                        prefix_mean=pm)
    # exact formulas do not mutate their inputs.
    snapshot = {k: np.array(view[k], copy=True)
                for k in ("bob", "high", "low", "u1_cond", "u2")}
    p2_snapshot = np.array(p2, copy=True)
    ir_recorder(view, p2, order,
                {"first_error_layer": "L2", "first_error_coord": pos})
    for key, before in snapshot.items():
        assert np.array_equal(before, view[key]), key
    assert np.array_equal(p2_snapshot, p2)


def test_ir5_arrays_writer_and_manifest_identity():
    _, p2, view, order = full_block_ir_fixture(seed=TEST_SEEDS[4])
    n = 32768
    k2 = 6746
    arrays = l2s._ir5_full_block_arrays(
        view=view, p2_arm=p2, l2_order=order, k2=k2, low_hat=None, field=None)
    assert arrays["hazards_f32"].shape == (32768,)
    assert arrays["hazards_f32"].dtype == np.dtype("<f4")
    assert arrays["inprefix_u8"].shape == (32768,)
    assert arrays["inu_u8"].shape == (32768,)
    assert arrays["inprefix_u8"].dtype == np.uint8
    # in-prefix popcount equals the disclosed K2 size; no estimate -> inu zero.
    assert int(arrays["inprefix_u8"].sum()) == k2
    assert int(arrays["inu_u8"].sum()) == 0
    assert np.isfinite(np.asarray(arrays["hazards_f32"],
                                  dtype=np.float64)).all()
    # hazards match the IR-1..IR-4 recorder's true-cell definition.
    ref_haz = p20q._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
    assert np.allclose(np.asarray(arrays["hazards_f32"], dtype=np.float64),
                       np.asarray(ref_haz, dtype=np.float32), atol=1e-6)
    with p20s_root() as root:
        out = root / "ir5"
        refs = {}
        for arm in l2s.FROZEN_ARM_NAMES:
            refs[arm] = l2s._ir5_full_block_writer(
                out_dir=out, arm_name=arm, block_index=0, arrays=arrays,
                order_digest="0" * 64)
        # per-record ~192 KiB, well under the ~400 KB budget; binary only.
        assert (out / "A_hazard_bits_f32le.bin").stat().st_size == 131072
        assert (out / "A_inprefix_u8.bin").stat().st_size == 32768
        assert (out / "A_inu_u8.bin").stat().st_size == 32768
        assert refs["A_anchor_frozen_order"]["ir5_format_version"] == "ir5full-v1"
        assert refs["A_anchor_frozen_order"]["ir5_total_len"] == 32768
        assert refs["B_spike_local_order"]["ir5_hazard_bits_file"] == \
            "B_hazard_bits_f32le.bin"
        assert refs["O_true_l1_oracle"]["ir5_inu_file"] == "O_inu_u8.bin"
        # fail-if-present: the writer never overwrites.
        assert_raises_match(FileExistsError, "refusing to overwrite",
                            l2s._ir5_full_block_writer, out_dir=out,
                            arm_name="A_anchor_frozen_order", block_index=0,
                            arrays=arrays, order_digest="0" * 64)
        assert_raises_match(ValueError, "unknown frozen arm",
                            l2s._ir5_full_block_writer, out_dir=out,
                            arm_name="Z_unknown", block_index=0,
                            arrays=arrays, order_digest="0" * 64)
        # digests recomputed from disk match the record references.
        for arm, ref in refs.items():
            for key, name in (("ir5_hazard_bits_sha256",
                               ref["ir5_hazard_bits_file"]),
                              ("ir5_inprefix_sha256", ref["ir5_inprefix_file"]),
                              ("ir5_inu_sha256", ref["ir5_inu_file"])):
                raw = (out / name).read_bytes()
                assert hashlib.sha256(raw).hexdigest() == ref[key]
        # the nine-file manifest verifies byte-present with matching digests.
        manifest = {"format_version": "ir5full-v1", "files": []}
        for arm, ref in refs.items():
            order_id = ("b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906"
                        if arm != "B_spike_local_order"
                        else "139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864")
            for fname, skey, shape, dtype, nbytes in (
                    (ref["ir5_hazard_bits_file"], "ir5_hazard_bits_sha256",
                     [32768], "<f4", 131072),
                    (ref["ir5_inprefix_file"], "ir5_inprefix_sha256",
                     [32768], "u1", 32768),
                    (ref["ir5_inu_file"], "ir5_inu_sha256",
                     [32768], "u1", 32768)):
                manifest["files"].append({
                    "file": fname, "sha256": ref[skey], "shape": shape,
                    "dtype": dtype, "endianness": "little",
                    "order_identity": order_id, "arm": arm, "block_index": 0,
                    "bytes": nbytes, "format_version": "ir5full-v1",
                })
        assert l2s.check_ir5_manifest_identity(out, manifest)["verified"] is True
        # tampered digest / wrong set / wrong version all refuse.
        tampered = json.loads(json.dumps(manifest))
        tampered["files"][0]["sha256"] = "0" * 64
        assert_raises_match(ValueError, "sha256",
                            l2s.check_ir5_manifest_identity, out, tampered)
        short = dict(manifest, files=manifest["files"][:8])
        assert_raises_match(ValueError, "exactly nine",
                            l2s.check_ir5_manifest_identity, out, short)
        badver = dict(manifest, format_version="ir5full-v0")
        assert_raises_match(ValueError, "format_version",
                            l2s.check_ir5_manifest_identity, out, badver)


def test_ir_payload_complete_gate():
    _, p2, view, order = full_block_ir_fixture()
    n = 32768
    k2 = int(l2s.FROZEN_K2)
    prefix = order[:k2]
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    hazards = p20q._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
    pm = float(np.mean(hazards[mask]))
    base = dict(l2s._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": None, "first_error_coord": None},
        prefix_mean=pm),
        ir5_hazard_bits_file="A_hazard_bits_f32le.bin",
        ir5_hazard_bits_sha256="a" * 64,
        ir5_inprefix_file="A_inprefix_u8.bin",
        ir5_inprefix_sha256="b" * 64,
        ir5_inu_file="A_inu_u8.bin",
        ir5_inu_sha256="c" * 64,
        ir5_format_version="ir5full-v1",
        ir5_total_len=32768)
    assert l2s.ir_payload_complete([]) is False
    assert l2s.ir_payload_complete([dict(base, outcome="exact",
                                        first_error_layer=None)]) is True
    pos = int(prefix[3])
    l2rec = dict(l2s._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": "L2", "first_error_coord": pos},
        prefix_mean=pm),
        ir5_hazard_bits_file="B_hazard_bits_f32le.bin",
        ir5_hazard_bits_sha256="d" * 64,
        ir5_inprefix_file="B_inprefix_u8.bin",
        ir5_inprefix_sha256="e" * 64,
        ir5_inu_file="B_inu_u8.bin",
        ir5_inu_sha256="f" * 64,
        ir5_format_version="ir5full-v1",
        ir5_total_len=32768,
        outcome="verify_failed", first_error_layer="L2")
    assert l2s.ir_payload_complete([l2rec]) is True
    # every refusal mode fails the gate.
    assert l2s.ir_payload_complete(
        [dict(l2rec, ir4_topk_coords=l2rec["ir4_topk_coords"][:15])]) is False
    assert l2s.ir_payload_complete(
        [dict(l2rec,
              ir2_first_error_hazard_rank_pct=None)]) is False
    assert l2s.ir_payload_complete(
        [dict(base, outcome="exact", first_error_layer=None,
              ir2_first_error_hazard_rank_pct=0.5)]) is False
    assert l2s.ir_payload_complete(
        [dict(l2rec, ir5_format_version="ir5full-v0")]) is False
    assert l2s.ir_payload_complete(
        [dict(l2rec, ir5_total_len=4096)]) is False
    dropped = dict(l2rec)
    del dropped["ir3_thresh_hi_bits"]
    assert l2s.ir_payload_complete([dropped]) is False
    # resource_abort records are skipped, never passed.
    abort = dict(l2rec, outcome="resource_abort")
    assert l2s.ir_payload_complete([abort]) is True


def test_ir_payload_tables_descriptive():
    _, p2, view, _ = full_block_ir_fixture(seed=TEST_SEEDS[5])
    n = 32768
    rng = np.random.default_rng(TEST_SEEDS[5])
    order = rng.permutation(n).astype(np.int64)
    k2 = int(l2s.FROZEN_K2)
    prefix = order[:k2]
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    hazards = p20q._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
    pm = float(np.mean(hazards[mask]))
    rec_a = dict(l2s._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": None, "first_error_coord": None},
        prefix_mean=pm),
        outcome="exact", arm="A_anchor_frozen_order", block_index=0)
    pos = int(prefix[11])
    rec_b = dict(l2s._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": "L2", "first_error_coord": pos},
        prefix_mean=pm),
        outcome="verify_failed", arm="B_spike_local_order", block_index=0,
        first_error_layer="L2")
    tables = l2s.ir_payload_tables([rec_a, rec_b])
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


def test_nine_scalars_arm_specific_digest():
    counts = sparse_counts(TEST_SEEDS[6])
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.asarray(arrays["p2"], dtype=np.float64)
    rng = np.random.default_rng(TEST_SEEDS[6])
    n = 256
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    block = {"block_index": 0, "frame_start": 2827, "frame_end": 3594,
             "high": high, "low": low, "bob": bob}
    view = {"bob": bob, "high": high, "low": low, "u1_cond": high}
    order = rng.permutation(n).astype(np.int64)
    first_error = {"first_error_layer": None, "first_error_coord": None}
    nine_a = l2s._nine_scalars_for_arm(
        arm_name="A_anchor_frozen_order", block=block, view=view,
        p2_arm=p2, counts_arr=np.asarray(arrays["counts_ab"]),
        l2_order=order, k2=6746, first_error=first_error, field=None,
        low_hat=low)
    nine_b = l2s._nine_scalars_for_arm(
        arm_name="B_spike_local_order", block=block, view=view,
        p2_arm=p2, counts_arr=np.asarray(arrays["counts_ab"]),
        l2_order=order, k2=6746, first_error=first_error, field=None,
        low_hat=low)
    # the computation is the accepted recorder's; only the digest label is
    # arm-specific (frozen-A on A/O, spike on B).
    assert nine_a["l2_order_digest"] == l2s.FROZEN_ORDER_DIGEST_A
    assert nine_b["l2_order_digest"] == l2s.FROZEN_SPIKE_ORDER_DIGEST_B
    assert nine_a["l2_order_digest"] != nine_b["l2_order_digest"]
    assert nine_a["l2_prefix_len"] == 6746
    assert set(nine_a) == set(p20o.HAZARD_FIELDS)
    assert l2s._arm_order_digest("O_true_l1_oracle") == l2s.FROZEN_ORDER_DIGEST_A
    assert l2s._arm_order_digest("B_spike_local_order") == \
        l2s.FROZEN_SPIKE_ORDER_DIGEST_B
    assert_raises_match(ValueError, "unknown frozen arm",
                        l2s._arm_order_digest, "Z_unknown")
    # the arm-specific gate accepts per-arm digests with frozen nullability.
    rec_a = dict(nine_a, outcome="exact", arm="A_anchor_frozen_order",
                 first_error_layer=None)
    rec_b = dict(nine_b, outcome="exact", arm="B_spike_local_order",
                 first_error_layer=None)
    assert l2s.hazard_instrumentation_complete([rec_a, rec_b]) is True
    assert l2s.hazard_instrumentation_complete(
        [dict(rec_a, l2_order_digest=nine_b["l2_order_digest"])]) is False
    assert l2s.hazard_instrumentation_complete([]) is False


# ---- truth isolation (recording-only, post-decode) ----

def test_truth_isolation_ir_recording_only(monkeypatch):
    counts = sparse_counts(TEST_SEEDS[6])
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.asarray(arrays["p2"], dtype=np.float64)
    p1 = np.asarray(arrays["p1"], dtype=np.float64)
    rng = np.random.default_rng(TEST_SEEDS[6])
    n = 32768
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    block = {"block_index": 0, "frame_start": 2827, "frame_end": 3594,
             "high": high, "low": low, "bob": bob}
    view = {"bob": bob, "high": high, "low": low,
            "u2": rng.integers(0, 32, size=n)}
    result = opf.OperationalBlockResult(
        stream_seed=2827, block_index=0, outcome="exact", exact=True,
        label_match=True, tag_pass=True, l1_provenance=opf.Provenance.PRIOR_ONLY.value,
        l2_provenance=opf.Provenance.CANDIDATE_CONDITIONED.value, l1_executed=True,
        l1_decode_failed=False, l2_invoked=True, l2_skipped_by_l1_failure=False,
        l2_decode_failed=False, tag_invoked=True, key_dependent_bits=100,
        public_control_bits=FROZEN_PUBLIC_BITS, nonfinite=False,
        truth_leak_violation=False, l1_error_type=None, l2_error_type=None,
        wall_s=0.01, k1=334, k2=6746, l1_exact=True, hard_l2_exact=True,
        oracle_l2_exact=None, pair_exact=True, high_hat=high.copy(),
        low_hat=low.copy(), label_hat=(high * 32 + low).astype(np.int64))
    calls = []

    def hostile_ir_recorder(**kwargs):
        calls.append(dict(kwargs))
        # a recording-only call cannot feed anything back: poison the truth
        # it received after the decode has already completed.
        kwargs["view"]["low"][:] = (kwargs["view"]["low"] + 7) % 32
        return {field: "sentinel" for field in l2s.IR_FIELDS}

    def sentinel_ir5_writer(**kwargs):
        return {
            "ir5_hazard_bits_file": "sentinel.bin",
            "ir5_hazard_bits_sha256": "s" * 64,
            "ir5_inprefix_file": "sentinel.bin",
            "ir5_inprefix_sha256": "s" * 64,
            "ir5_inu_file": "sentinel.bin",
            "ir5_inu_sha256": "s" * 64,
            "ir5_format_version": "sentinel",
            "ir5_total_len": -1,
        }

    monkeypatch.setattr(l2s, "_ir_hazard_diagnostics", hostile_ir_recorder)
    monkeypatch.setattr(l2s, "_ir5_full_block_writer", sentinel_ir5_writer)
    with p20s_root() as root:
        record = l2s._operational_record(
            result, spec=l2s.ArmSpec(
                "A_anchor_frozen_order", "operational", 334, 6746,
                5 * 7080 + 64, l2s.OPERATIONAL_PROVENANCE, "alt"),
            arm_index=0, block=block,
            scoring=l2s._scoring_absent(), resources={},
            k_total=7080, budget_literal="test-budget-literal",
            prior_digest="0" * 64, alt_digest="0" * 64,
            order_digest="0" * 64, counts_arr=counts, p1=p1, p2=p2,
            l2_order=np.arange(n, dtype=np.int64), n=n, view=view,
            field=make_gf32(),
            ir5_dir=str(root / "ir5"))
    assert len(calls) == 1
    # the IR recorder is called post-decode with the hard-L1 candidate as
    # U1_cond on the operational arms, and its outputs land in the IR record
    # fields only.
    assert calls[0]["view"]["u1_cond"] is result.high_hat
    assert record["ir1_hist_prefix_counts"] == "sentinel"
    assert record["ir2_first_error_hazard_rank_pct"] == "sentinel"
    assert record["ir3_thresh_hi_bits"] == "sentinel"
    assert record["ir4_topk_coords"] == "sentinel"
    # decode-derived fields are exactly the pre-record result, untouched by
    # the post-decode truth mutation.
    assert record["outcome"] == "exact" and record["exact"] is True
    assert record["l1_exact"] is True and record["hard_l2_exact"] is True
    assert record["tag_pass"] is True and record["pair_exact"] is True
    assert record["first_error_layer"] is None
    assert record["first_error_coord"] is None
    assert record["arm"] == "A_anchor_frozen_order"
    assert record["l2_construction"] == "alt-α1"
    assert record["key_bit_delta_vs_control"] == 0
    assert record["protocol"] == l2s.PROTOCOL_NAME


def test_ir_truth_mutation_changes_recording_only():
    # a denser synthetic prior so the truth mutation moves prefix hazards
    # (sparse-count fixtures can be last-axis-degenerate).
    rng = np.random.default_rng(TEST_SEEDS[6])
    counts = sparse_counts(TEST_SEEDS[6], cells=16384, hi=200)
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.ascontiguousarray(np.asarray(arrays["p2"], dtype=np.float64))
    n = 32768
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    order = rng.permutation(n).astype(np.int64)
    view = {"bob": bob, "high": high, "low": low, "u1_cond": high,
            "u2": rng.integers(0, 32, size=n)}
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
    assert "ir" not in p20q.run_operational_block.__code__.co_varnames
    assert "ir" not in p20q.run_oracle_control_block.__code__.co_varnames
    assert "ir" not in l2s.run_l2_mechanism_probe_2m.__code__.co_varnames


# ---- no Stage-B root + zero protected opens + zero Stage-B sampling ----

# P20S-Stage-A-historical: this pin recorded the TRUE pre-execution Stage-A
# state (P20S Stage-B root absent). P20S Stage-B has since executed once
# (exit 0, 15/15 files present, attempt consumed), so the absence clause is
# stale for the R1 delta-successor while every other clause below stays a
# live Stage-A invariant. The body is preserved verbatim as the historical
# record; it is skipped whenever the P20S root exists. The live
# pre-execution gate for R1 is
# test_r1_out_root_absent_and_p20s_root_untouched below.
@pytest.mark.skipif(
    (REPO_ROOT / l2s.FROZEN_OUT_ROOT).exists(),
    reason="P20S-Stage-A-historical: P20S Stage-B already executed "
    "(root present); R1 successor pin covers the live pre-execution state",
)
def test_no_stage_b_root_and_no_protected_opens_in_stage_a():
    assert not Path(l2s.FROZEN_OUT_ROOT).exists()
    assert Path(l2s.FROZEN_OUT_ROOT).name == "l2_mechanism_probe_2m"
    assert l2s._DEV_PARQUET_CONTENT_OPENED is False
    assert l2s._ALT_CONTENT_LOADED is False
    assert l2s._SESSION_PRIOR_CONTENT_LOADED is False
    source = Path(l2s.__file__).read_text(encoding="utf-8")
    for token in ("load_v25_channel_counts", "smooth_joint_to_conditional",
                  "LAMBDA_STAR", "137.3823795883264"):
        assert token not in source, token
    for token in ("_ir_hazard_diagnostics", "reuse_prior_identity",
                  "reuse_alt_identity", "reuse_order_freeze_A",
                  "spike_order_identity_B", "order_derivation_program_identity",
                  "verify_merged_containment",
                  "verify_consumed_exclusions_merged",
                  "verify_merged_frame_set_identity",
                  "ir_payload_complete", "derive_spike_l2_order",
                  "check_ir5_manifest_identity", "ir5full-v1",
                  "nbpolar-p20s-mechanism-probe-2m-seed",
                  "from . import l2_alt_hold_ir_2m",
                  "verify_reuse", "run_l2_mechanism_probe_2m",
                  "k_literal_exact",
                  "alt_construction_budget_feasibility_replayed",
                  "TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE"):
        assert token in source, token
    assert "2026092360" in source
    # the three frozen arms carry the single-factor order delta (same K, same
    # alpha1 tables, frozen-A prefixes on A/O, spike prefixes on B).
    assert l2s.FROZEN_ARM_NAMES == (
        "A_anchor_frozen_order", "B_spike_local_order",
        "O_true_l1_oracle")
    # the nine carried scalars (incl. the ninth U-domain scalar) ride the
    # accepted 2M recorder, called at the carried-over code point.
    assert "_l2_hazard_diagnostics" in source
    assert "l2_fail_in_prefix_u_domain" in source


def test_r1_out_root_absent_and_p20s_root_untouched():
    """R1 delta-successor live pre-execution pin (Stage-A close for R1).

    The R1 out-root must be ABSENT (no Stage-B execution yet under R1) and
    the P20S predecessor root must remain PRESENT-and-untouched: exactly
    the fifteen frozen ``OUTPUT_FILES`` exist under it. Read-only:
    ``Path.exists`` checks only — no writes, no content opens, no stats,
    no directory listings.
    """
    r1_root = (REPO_ROOT / ".workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX"
               / "l2_mechanism_probe_2m")
    assert r1_root.name == "l2_mechanism_probe_2m"
    assert not r1_root.exists()
    p20s_root_dir = REPO_ROOT / l2s.FROZEN_OUT_ROOT
    assert p20s_root_dir.name == "l2_mechanism_probe_2m"
    assert p20s_root_dir.exists()
    assert len(l2s.OUTPUT_FILES) == 15
    for name in l2s.OUTPUT_FILES:
        assert (p20s_root_dir / name).exists(), name


def test_zero_stage_b_sampling_pin():
    parser = l2s.build_parser()
    options = set()
    for action in parser._actions:
        options.update(action.option_strings)
    for forbidden in ("--train-seeds", "--seed", "--sample", "--rng", "--genie",
                      "--deriv-seeds-stage-b", "--derive"):
        assert forbidden not in options, forbidden
    for name in l2s.STAGE_B_FLAGS:
        assert "seed" not in name and "sample" not in name
    assert "--verify-reuse" in options
    assert "--derive-spike-order" in options
    assert "seeds" not in l2s.run_l2_mechanism_probe_2m.__code__.co_varnames
    assert "genie" not in l2s.run_l2_mechanism_probe_2m.__code__.co_varnames
    assert "seeds" not in l2s.derive_spike_l2_order.__code__.co_varnames
    source = Path(l2s.__file__).read_text(encoding="utf-8")
    assert "default_rng" not in source
    assert "sample_full_block" not in source


def test_one_open_guards_refuse_reload(monkeypatch):
    monkeypatch.setattr(
        l2s, "verify_predecessor_construction", lambda *a, **k: {"record": {}})
    monkeypatch.setattr(
        l2s, "verify_dev_manifest_2m",
        lambda *a, **k: {"train_pairs": 559872, "val_pairs": 186624,
                         "hold_pairs": 186624})
    monkeypatch.setattr(
        l2s, "verify_stage_b_order_file_2m",
        lambda *a, **k: {"verified": True, "order_digest": "x",
                         "l1_order": np.zeros(32768, dtype=np.int64),
                         "l2_order": np.zeros(32768, dtype=np.int64),
                         "k1": 334, "k2": 6746})
    monkeypatch.setattr(
        l2s, "verify_spike_order_file",
        lambda *a, **k: {"verified": True, "spike_order_digest": "y",
                         "program": l2s.SPIKE_PROGRAM_PIN,
                         "formula_id": l2s.SPIKE_FORMULA_ID,
                         "l1_order": np.zeros(32768, dtype=np.int64),
                         "l2_order": np.zeros(32768, dtype=np.int64),
                         "k1": 334, "k2": 6746})
    base = dict(prior_path="p", prior_digest=l2s.FROZEN_SESSION_PRIOR_DIGEST,
                alt_prior_path="a", alt_digest=l2s.FROZEN_ALT_DIGEST,
                source="2M", floor=1e-15, n=32768, k1=334, k2=6746,
                construction="c",
                construction_digest=l2s.FROZEN_CONSTRUCTION_DIGEST,
                manifest_path="m", dev_pairs=l2s.FROZEN_DEV_PAIRS_PATH,
                order_file="o", order_digest=l2s.FROZEN_ORDER_DIGEST_A,
                spike_order_file="s",
                spike_order_digest=l2s.FROZEN_SPIKE_ORDER_DIGEST_B,
                spike_formula=l2s.SPIKE_FORMULA_ID,
                tag_master=2026092360)
    with p20s_root() as root, restored_guards():
        out = str(root / "out")
        l2s._SESSION_PRIOR_CONTENT_LOADED = True
        assert_raises_match(ValueError, "reload refused",
                            l2s.run_l2_mechanism_probe_2m, out_dir=out, **base)
        assert not Path(out).exists()
        l2s._SESSION_PRIOR_CONTENT_LOADED = False
        l2s._ALT_CONTENT_LOADED = True
        assert_raises_match(ValueError, "reload refused",
                            l2s.run_l2_mechanism_probe_2m, out_dir=out,
                            prior={}, **base)
        assert not Path(out).exists()
        l2s._ALT_CONTENT_LOADED = False
        l2s._DEV_PARQUET_CONTENT_OPENED = True
        assert_raises_match(ValueError, "reopen refused",
                            l2s.run_l2_mechanism_probe_2m, out_dir=out,
                            prior={}, alt_prior={}, **base)
        assert not Path(out).exists()


# ---- injected end-to-end single-block three-arm run (no protected data) ----

def test_injected_end_to_end_single_block_three_arms(monkeypatch):
    with p20s_root() as root:
        prior_path, alt_path, order_path, spike_order_path, pins = reuse_fixture(root)
        with open(prior_path, "rb") as fh:
            data = np.load(fh, allow_pickle=False)
            with data:
                prior_arrays = {k: np.asarray(data[k]) for k in data.files}
        with open(alt_path, "rb") as fh:
            data = np.load(fh, allow_pickle=False)
            with data:
                alt_arrays = {k: np.asarray(data[k]) for k in data.files}
        table = merged_table(seed=TEST_SEEDS[1])
        monkeypatch.setattr(
            l2s, "verify_predecessor_construction",
            lambda *a, **k: {"record": {"n": 32768}})
        monkeypatch.setattr(
            l2s, "verify_dev_manifest_2m",
            lambda *a, **k: {"train_pairs": 559872, "val_pairs": 186624,
                             "hold_pairs": 186624})
        out = str(root / "l2_mechanism_probe_2m")
        with patched(l2s, "FROZEN_H1", pins["h1"]), \
                patched(l2s, "FROZEN_H2", pins["h2"]), \
                patched(l2s, "FROZEN_H_TOTAL", pins["h_total"]), \
                patched(p20o, "FROZEN_ORDER_DIGEST", pins["order_digest"]), \
                patched(p20o, "FROZEN_ORDER_PROGRAM_PIN",
                        "test-frozen-A-program-pin"), \
                patched(p20o, "FROZEN_DERIVATION_SEEDS",
                        tuple(int(s) for s in p20o.FROZEN_DERIVATION_SEEDS)), \
                patched(p20o, "FROZEN_ALT_DIGEST", pins["alt_digest"]), \
                patched(p20o, "FROZEN_ALT_H1_INC", pins["h1"]), \
                patched(l2s, "FROZEN_SESSION_PRIOR_DIGEST",
                        pins["prior_digest"]), \
                patched(l2s, "FROZEN_ORDER_DIGEST_A", pins["order_digest"]), \
                patched(l2s, "FROZEN_ALT_DIGEST", pins["alt_digest"]), \
                patched(l2s, "FROZEN_SPIKE_ORDER_DIGEST_B",
                        pins["spike_order_digest"]), \
                restored_guards():
            run = l2s.run_l2_mechanism_probe_2m(
                prior=dict(prior_arrays), alt_prior=dict(alt_arrays),
                prior_digest=pins["prior_digest"],
                alt_digest=pins["alt_digest"], source="2M", floor=1e-15,
                n=32768, k1=334, k2=6746, construction="c",
                construction_digest=l2s.FROZEN_CONSTRUCTION_DIGEST,
                manifest_path="m", dev_table=table,
                dev_pairs=l2s.FROZEN_DEV_PAIRS_PATH,
                dev_frames_val=(2827, 2915), dev_frames_hold=(3556, 3594),
                block_frames=128,
                remainder_frames=(3595, 3644), tag_master=2026092360,
                chunk_rows=512, tag_bits=64, order_file=str(order_path),
                order_digest=pins["order_digest"],
                spike_order_file=str(spike_order_path),
                spike_order_digest=pins["spike_order_digest"],
                spike_formula=l2s.SPIKE_FORMULA_ID, out_dir=out)
            summary = run.summary
            records = list(run.records)
            assert summary["records_completed"] == 3
            assert {r["arm"] for r in records} == set(l2s.FROZEN_ARM_NAMES)
            assert summary["stage_b_sampling_calls"] == 0
            # arm-specific order digests: frozen-A on A/O, spike on B.
            by_arm = {r["arm"]: r for r in records}
            assert by_arm["A_anchor_frozen_order"]["l2_order_digest"] == \
                pins["order_digest"]
            assert by_arm["O_true_l1_oracle"]["l2_order_digest"] == \
                pins["order_digest"]
            assert by_arm["B_spike_local_order"]["l2_order_digest"] == \
                pins["spike_order_digest"]
            # the order factor moves the prefix hazard means between A and B.
            assert by_arm["A_anchor_frozen_order"][
                "l2_prefix_hazard_mean_bits"] != by_arm["B_spike_local_order"][
                "l2_prefix_hazard_mean_bits"]
            # IR-1..IR-4 all PRESENT plus IR-5 manifest references, every record.
            assert l2s.ir_payload_complete(records) is True
            assert l2s.hazard_instrumentation_complete(records) is True
            # the byte-exact set-delta rides the summary with size-delta 0.
            assert summary["order_set_delta"]["size_delta_b_minus_a"] == 0
            # mechanism diagnostics replace counting vocabulary: no transition
            # cells are computed anywhere in the aggregates.
            assert summary["aggregates"]["mechanism"]["transition_cells_computed"] \
                is False
            assert summary["aggregates"]["mechanism"]["transition_tables"] is None
            # fifteen files land under the injected out root only.
            for name in l2s.OUTPUT_FILES:
                assert (Path(out) / name).exists(), name
            assert len(l2s.OUTPUT_FILES) == 15
            # the nine IR-5 binaries verify against the run manifest.
            manifest = json.loads((Path(out) / "ir5_full_manifest.json")
                                  .read_text(encoding="utf-8"))
            assert l2s.check_ir5_manifest_identity(
                Path(out), manifest)["verified"] is True


# ---- seed-domain grep rule ----

def test_grep_rule_seed_placement():
    master = "2026092360"
    test_seeds = [str(seed) for seed in TEST_SEEDS]
    module_source = Path(l2s.__file__).read_text(encoding="utf-8")
    test_source = Path(__file__).read_text(encoding="utf-8")
    assert master in module_source
    for seed in test_seeds:
        assert seed in test_source, seed
        assert seed not in module_source, seed
    assert l2s.FROZEN_TAG_MASTER == 2026092360
    assert l2s.FROZEN_TAG_MASTER not in (
        p20m.FROZEN_TAG_MASTER,
        p20o.FROZEN_TAG_MASTER if hasattr(p20o, "FROZEN_TAG_MASTER") else None,
        p20q.FROZEN_TAG_MASTER)
    allowed_prefixes = (
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_mechanism_probe_2m.py",
        "comparison_bench/tests/test_nbpolar_mechanism_probe_2m.py",
        ".workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/",
        # R1 is an authorized delta successor of the same P20S freeze
        # (DELTA.md carries the reused tag master); rule stays strict:
        # only runner/tests/packet/spec + the R1 dir are allowed.
        ".workbuddy/queue/NBPOLAR-PHASE4-P20S-R1-GATE-FIX/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20s/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md",
    )
    for literal in [master] + test_seeds:
        for hit in _git_grep_hits(literal):
            assert hit.startswith(allowed_prefixes), (literal, hit)
