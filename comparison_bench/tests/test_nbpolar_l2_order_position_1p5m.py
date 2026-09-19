"""Focused Phase 4-P20R 1.5M VAL-remainder order-position tests.

Injected/synthetic counts, priors, artifacts and fresh additive
``workspace/p20r/<uuid>/`` temp roots only. The V25 channel-counts NPZ, every
registered pairs parquet (1M, 1.5M VAL/HOLD/TRAIN, 2M VAL/HOLD), the real P16
construction root, the real split manifest, the accepted P20M/P20N worktree
products and every accepted evidence root are NEVER content-opened, statted,
or listed here: the Stage-A reuse verification and the frozen derivation run
only in the authorized ``--verify-reuse`` / ``--derive-new-order`` commands,
never in tests. The frozen derivation is deterministic (no sampler, no RNG):
genie 0+0. Focused tests use their own fresh seeds
``2026092341..2026092347`` and never the frozen P20R tag master
``2026092340`` (except through the frozen module constant).
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
    l2_order_position_1p5m as l2r,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_alt_hold_ir_2m as p20q,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_alt_hold_1p5m as p20n,
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
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    l2_alt_maintain_2m as p20o,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never the frozen P20R tag master 2026092340.
TEST_SEEDS = (2026092341, 2026092342, 2026092343, 2026092344,
              2026092345, 2026092346, 2026092347)

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
        l2r._SESSION_PRIOR_CONTENT_LOADED, l2r._ALT_CONTENT_LOADED,
        l2r._DEV_PARQUET_CONTENT_OPENED,
    )
    try:
        yield
    finally:
        (l2r._SESSION_PRIOR_CONTENT_LOADED, l2r._ALT_CONTENT_LOADED,
         l2r._DEV_PARQUET_CONTENT_OPENED) = state


@contextlib.contextmanager
def p20r_root():
    """Fresh additive workspace/p20r/<uuid>/ temp root, cleaned afterwards."""
    root = REPO_ROOT / "workspace" / "p20r" / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    assert "workspace" in root.parts and "p20r" in root.parts
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


def exact_total_counts(seed: int, total: int = 424960) -> np.ndarray:
    """Synthetic counts with an exact integer total (self-consistent fixture)."""
    counts = sparse_counts(seed)
    counts[0, 0] += float(total) - float(counts.sum())
    assert int(round(float(counts.sum()))) == total
    return np.ascontiguousarray(counts)


def synthetic_prior_arrays(seed: int = TEST_SEEDS[0]) -> dict:
    """Self-consistent synthetic 1.5M-shaped prior arrays (no protected data)."""
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


def val_remainder_table(*, seed: int = TEST_SEEDS[2]) -> pd.DataFrame:
    """VAL-remainder-like pairs frame: 128 DEV frames 2044..2171 + 41-frame stub."""
    rng = np.random.default_rng(int(seed))
    frames = np.repeat(np.arange(2044, 2172), 256)
    pair_idx = np.tile(np.arange(256), 128)
    dev = pd.DataFrame({
        "frame_id": frames,
        "pair_idx": pair_idx,
        "alice_symbol": rng.integers(0, 1024, size=frames.size),
        "bob_symbol": rng.integers(0, 1024, size=frames.size),
    })
    rem_frames = np.repeat(np.arange(2172, 2213), 256)
    rem = pd.DataFrame({
        "frame_id": rem_frames,
        "pair_idx": np.tile(np.arange(256), 41),
        "alice_symbol": rng.integers(0, 1024, size=rem_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=rem_frames.size),
    })
    # Extra rows outside the DEV/stub spans must not influence slicing.
    extra = pd.DataFrame({
        "frame_id": np.repeat([0, 1659, 1660, 2043, 2213, 2766], 256),
        "pair_idx": np.tile(np.arange(256), 6),
        "alice_symbol": rng.integers(0, 1024, size=6 * 256),
        "bob_symbol": rng.integers(0, 1024, size=6 * 256),
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
        hazards = p20n._hazard_bits(
            p2, np.asarray(view.get("u1_cond", view["high"])),
            np.asarray(view["bob"]), np.asarray(view["low"]))
        prefix_mean = float(np.mean(hazards[mask]))
    with patched(l2r, "FROZEN_K2", k2):
        return l2r._ir_hazard_diagnostics(
            view=view, p2_arm=p2, l2_order=order, k2=k2,
            first_error=first_error, prefix_mean=prefix_mean)


def reuse_fixture(root, *, seed: int = TEST_SEEDS[0]):
    """Self-consistent synthetic prior/alt/frozen-A-order/new-B fixtures + pins."""
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
        "protocol": p20m.PROTOCOL_NAME,
        "kind": "raw-prior-orders-file",
        "n": n,
        "k_total": 7020,
        "k1": 331,
        "k2": 6689,
        "l1_order": [int(v) for v in rng.permutation(n).tolist()],
        "l2_order": [int(v) for v in rng.permutation(n).tolist()],
        "derivation": {
            "program": "test-frozen-A-program-pin",
            "prior_digest": prior_digest,
            "train_seeds": [2026092291 + i for i in range(4)],
            "train_blocks_used": 16,
        },
    }
    order_path = root / "orders.json"
    order_path.write_text(json.dumps(doc, sort_keys=True) + "\n", encoding="utf-8")
    new_order_path = root / "new_orders.json"
    with patched(l2r, "FROZEN_SESSION_PRIOR_DIGEST", prior_digest):
        written = l2r.write_new_order_file(
            new_order_path, prior_arrays=prior_arrays,
            l1_order=np.asarray(doc["l1_order"], dtype=np.int64),
            prior_digest=prior_digest)
    d1 = p20n.feasibility_literals(
        np.asarray(prior_arrays["counts_ab"], dtype=np.float64),
        p2_incumbent=np.asarray(prior_arrays["p2"]),
        p2_alt=np.asarray(alt_arrays["p2_alt"]))
    pins = {
        "prior_digest": prior_digest,
        "alt_digest": hashlib.sha256(alt_path.read_bytes()).hexdigest(),
        "order_digest": hashlib.sha256(order_path.read_bytes()).hexdigest(),
        "new_order_digest": written["new_order_digest"],
        "h1": float(np.asarray(prior_arrays["h1"])),
        "h2": float(np.asarray(prior_arrays["h2"])),
        "h_total": float(np.asarray(prior_arrays["h_total"])),
        "ce_alt": float(d1["ce_alt_insample_bits_per_symbol"]),
        "ce_incumbent": float(d1["ce_incumbent_insample_bits_per_symbol"]),
        "alt_ideal_length_bits": float(d1["alt_ideal_length_bits"]),
    }
    return prior_path, alt_path, order_path, new_order_path, pins


def _git_grep_hits(literal: str):
    proc = subprocess.run(
        ["git", "grep", "-l", "--untracked", literal, "--",
         "comparison_bench", "openspec", ".workbuddy", "docs"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1), proc.stderr
    return [line for line in proc.stdout.splitlines() if line.strip()]


# ---- frozen literals, arms, population, delta d1-d8 ----

def test_frozen_literals_arms_population_and_delta():
    assert l2r.FROZEN_SOURCE == "1p5M"
    assert l2r.FROZEN_SOURCE_TAG == "type2_1p5M_20260121_183806"
    assert l2r.FROZEN_N == 32768
    assert l2r.FROZEN_FLOOR == 1e-15
    assert l2r.FROZEN_ALPHA == 1.0
    # (d3) K literals replay the P20M derivation, never recarried from 2M.
    assert (l2r.FROZEN_K_TOTAL, l2r.FROZEN_K1,
            l2r.FROZEN_K2) == (7020, 331, 6689)
    assert (l2r.FROZEN_K1, l2r.FROZEN_K2) == (p20n.FROZEN_K1, p20n.FROZEN_K2)
    # (d2) reuse pins are byte-identical to the accepted 1.5M products.
    assert l2r.FROZEN_SESSION_PRIOR_DIGEST == p20m.FROZEN_PRIOR_DIGEST
    assert l2r.FROZEN_ORDER_DIGEST_A == p20m.FROZEN_ORDER_DIGEST
    assert l2r.FROZEN_ALT_DIGEST == p20n.FROZEN_ALT_DIGEST
    assert (l2r.FROZEN_H1, l2r.FROZEN_H2,
            l2r.FROZEN_H_TOTAL) == (p20m.FROZEN_H1, p20m.FROZEN_H2,
                                    p20m.FROZEN_H_TOTAL)
    # (d1/d8) VAL-remainder population: FIRST 128 remainder frames, one block.
    assert tuple(l2r.FROZEN_DEV_FRAME_RANGE) == (2044, 2171)
    assert l2r.FROZEN_DEV_FRAMES == 128
    assert l2r.FROZEN_DEV_PAIRS == 32768
    assert tuple(tuple(r) for r in l2r.FROZEN_BLOCK_RANGES) == ((2044, 2171),)
    assert tuple(l2r.FROZEN_REMAINDER_FRAME_RANGE) == (2172, 2212)
    assert l2r.FROZEN_REMAINDER_FRAMES == 41
    assert l2r.FROZEN_REMAINDER_SYMBOLS == 41 * 256
    assert tuple(l2r.FROZEN_2M_HOLD_REMAINDER_FRAME_RANGE) == (3556, 3644)
    assert tuple(l2r.FROZEN_BUILD_FRAME_RANGE) == (0, 1659)
    # (d6) new P20R tag domain, disjoint from every predecessor by master+prefix.
    assert l2r.FROZEN_TAG_MASTER == 2026092340
    assert l2r.FROZEN_TAG_MASTER not in (
        p20m.FROZEN_TAG_MASTER, p20l.FROZEN_TAG_MASTER,
        p20o.FROZEN_TAG_MASTER if hasattr(p20o, "FROZEN_TAG_MASTER") else None,
        p20q.FROZEN_TAG_MASTER)
    assert l2r.SEED_PREFIX == "nbpolar-p20r-order-position-1p5m-seed"
    assert l2r.SEED_PREFIX != p20q.SEED_PREFIX
    # (d5) arms: same K, same alpha1 tables, zero disclosure delta by design.
    arms = l2r.frozen_arm_table()
    assert tuple(s.name for s in arms) == l2r.FROZEN_ARM_NAMES
    assert l2r.check_frozen_arm_table()["planned_key_dependent_bits"] == 137346
    totals = l2r.planned_totals(331, 6689)
    assert totals["operational_key_dependent_bits"] == 35164
    assert totals["oracle_key_dependent_bits"] == 33509
    assert totals["planned_key_dependent_bits"] == 137346
    assert totals["planned_public_control_bits"] == 1310972
    assert totals["planned_sc_calls"] == 6
    assert totals["planned_tag_invocations"] == 4
    assert totals["planned_records"] == 4
    # (d7) IR pins frozen PRESENT, same caps/formulas as P20Q section 7.
    assert l2r.IR1_BINS == 64
    assert (l2r.IR3_LO_MULT, l2r.IR3_HI_MULT) == (1.0, 2.0)
    assert l2r.IR4_TOPK == 16
    assert l2r.IR5_CAP == 4096
    assert l2r.IR_FIELDS == p20q.IR_FIELDS
    # the delta list d1-d8 is evidenced in the module docstring and the
    # import target plus the carried-over callsite pattern are referenced.
    source = Path(l2r.__file__).read_text(encoding="utf-8")
    assert "from . import l2_alt_hold_ir_2m as p20q" in source
    assert "_l2_hazard_diagnostics" in source
    assert "_ir_hazard_diagnostics" in source
    assert "no lambda" in source.lower() or "NO lambda" in source or \
        "lambda anywhere" in source


def test_frozen_command_pinned():
    assert l2r.pins_are_frozen() is True
    assert l2r.FROZEN_COMMAND is not None
    assert "--verify-reuse" not in l2r.FROZEN_COMMAND
    assert "--derive-new-order" not in l2r.FROZEN_COMMAND
    assert "--source 1p5M" in l2r.FROZEN_COMMAND
    assert "--dev-frames 2044 2171" in l2r.FROZEN_COMMAND
    assert "--remainder-frames 2172 2212" in l2r.FROZEN_COMMAND
    assert "--tag-master 2026092340" in l2r.FROZEN_COMMAND
    assert "--k1 331 --k2 6689" in l2r.FROZEN_COMMAND
    assert "l2_order_position_1p5m" in l2r.FROZEN_COMMAND
    assert l2r.FROZEN_COMMAND.count(
        "372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac") == 1
    assert l2r.FROZEN_COMMAND.count(
        "6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78") == 1
    assert l2r.FROZEN_COMMAND.count(
        "a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638") == 1
    assert l2r.FROZEN_COMMAND.count(str(l2r.FROZEN_NEW_ORDER_DIGEST_B)) == 1
    # the Stage-B out root is the frozen P20R evidence root.
    assert l2r.FROZEN_OUT_ROOT.endswith(
        "NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/l2_order_position_1p5m")


# ---- Stage-A new-order derivation (section 3 contract + B-1 functional) ----

def test_derive_new_order_deterministic_permutation():
    prior_arrays = synthetic_prior_arrays()
    first = l2r.derive_new_l2_order(prior_arrays)
    second = l2r.derive_new_l2_order(prior_arrays)
    order = first["new_l2_order"]
    assert order.shape == (32768,)
    assert set(order.tolist()) == set(range(32768))
    assert np.array_equal(order, second["new_l2_order"])
    assert first["sampling_calls"] == 0 and first["genie_calls"] == 0
    assert first["k2"] == 6689
    assert first["program"] == l2r.NEW_ORDER_PROGRAM_PIN
    # the first-K2 prefix is arm B's disclosed set at identical size.
    assert len(set(order[:6689].tolist())) == 6689


def test_derive_new_order_ranking_and_tiebreak():
    prior_arrays = synthetic_prior_arrays(seed=TEST_SEEDS[1])
    derived = l2r.derive_new_l2_order(prior_arrays)
    order = derived["new_l2_order"]
    hazards = derived["cell_hazards"]
    # descending hazard along the order; ties broken by ascending coordinate.
    ordered_haz = hazards[order]
    assert bool(np.all(ordered_haz[:-1] >= ordered_haz[1:]))
    ties = np.where(ordered_haz[:-1] == ordered_haz[1:])[0]
    for t in ties[:64]:
        assert int(order[t]) < int(order[t + 1])
    # worst-first: the head cell carries the maximum hazard.
    assert int(order[0]) == int(np.argmax(hazards))
    # degenerate flat hazards collapse to the natural coordinate order.
    flat = dict(prior_arrays)
    flat_counts = np.ones((1024, 1024), dtype=np.float64)
    flat["counts_ab"] = np.ascontiguousarray(flat_counts)
    flat["p1"] = np.ascontiguousarray(
        np.full((32, 1024), 1.0 / 32.0, dtype=np.float64))
    deg = l2r.derive_new_l2_order(flat)
    assert np.array_equal(deg["new_l2_order"],
                          np.arange(32768, dtype=np.int64))


def test_derive_new_order_refusals():
    prior_arrays = synthetic_prior_arrays()
    bad = dict(prior_arrays)
    del bad["p1"]
    assert_raises_match(ValueError, "exactly", l2r.derive_new_l2_order, bad)
    bad = dict(prior_arrays)
    bad["counts_ab"] = np.zeros((16, 16))
    assert_raises_match(ValueError, "(1024,1024)", l2r.derive_new_l2_order, bad)
    bad = dict(prior_arrays)
    bad["p1"] = np.zeros((4, 4))
    assert_raises_match(ValueError, "(32,1024)", l2r.derive_new_l2_order, bad)


def test_write_and_verify_new_order_file():
    with p20r_root() as root:
        prior_path, _, order_path, new_order_path, pins = reuse_fixture(root)
        doc = json.loads(new_order_path.read_text(encoding="utf-8"))
        assert doc["protocol"] == l2r.NEW_ORDER_PROTOCOL
        assert doc["kind"] == l2r.NEW_ORDER_KIND
        assert doc["n"] == 32768
        assert (doc["k_total"], doc["k1"], doc["k2"]) == (7020, 331, 6689)
        assert len(doc["l1_order"]) == 32768 and len(doc["l2_order"]) == 32768
        assert doc["derivation"]["zero_sampling_attestation"] is True
        assert doc["derivation"]["program"] == l2r.NEW_ORDER_PROGRAM_PIN
        # fail-if-present: the derivation never overwrites.
        with patched(l2r, "FROZEN_SESSION_PRIOR_DIGEST", pins["prior_digest"]):
            assert_raises_match(FileExistsError, "refusing to overwrite",
                                l2r.write_new_order_file, new_order_path,
                                prior_arrays=synthetic_prior_arrays(),
                                l1_order=np.arange(32768, dtype=np.int64),
                                prior_digest=pins["prior_digest"])
        # the verifier replays the file behind the digest + L1 + program pins.
        frozen_doc = json.loads(order_path.read_text(encoding="utf-8"))
        frozen_l1 = np.asarray(frozen_doc["l1_order"], dtype=np.int64)
        with patched(l2r, "FROZEN_NEW_ORDER_DIGEST_B", pins["new_order_digest"]):
            pin = l2r.verify_new_order_file(
                new_order_path, expected_digest=pins["new_order_digest"],
                expected_prior_digest=pins["prior_digest"],
                frozen_l1_order=frozen_l1, expected_k1=331,
                expected_k2=6689, expected_k_total=7020)
            assert pin["verified"] is True
            assert pin["new_order_digest"] == pins["new_order_digest"]
            assert_raises_match(ValueError, "digest flag",
                                l2r.verify_new_order_file, new_order_path,
                                expected_digest="0" * 64,
                                expected_prior_digest=pins["prior_digest"],
                                frozen_l1_order=frozen_l1, expected_k1=331,
                                expected_k2=6689, expected_k_total=7020)
            assert_raises_match(ValueError, "L1 order",
                                l2r.verify_new_order_file, new_order_path,
                                expected_digest=pins["new_order_digest"],
                                expected_prior_digest=pins["prior_digest"],
                                frozen_l1_order=np.arange(32768 - 1, -1, -1,
                                                          dtype=np.int64),
                                expected_k1=331, expected_k2=6689,
                                expected_k_total=7020)


def test_order_set_delta_exact():
    rng = np.random.default_rng(TEST_SEEDS[4])
    n = 32768
    frozen = rng.permutation(n).astype(np.int64)
    new = rng.permutation(n).astype(np.int64)
    delta = l2r.order_set_delta(frozen, new, 6689)
    assert delta["a_disclosed_size"] == 6689
    assert delta["b_disclosed_size"] == 6689
    assert delta["size_delta_b_minus_a"] == 0
    assert (delta["intersection_size"] + delta["a_minus_b_count"]) == 6689
    assert delta["a_minus_b_count"] == delta["b_minus_a_count"]
    assert sorted(delta["a_minus_b"]) == delta["a_minus_b"]
    assert sorted(delta["b_minus_a"]) == delta["b_minus_a"]
    assert not (set(delta["a_minus_b"]) & set(new[:6689].tolist()))
    assert not (set(delta["b_minus_a"]) & set(frozen[:6689].tolist()))
    # identical orders give an empty delta (still size-delta 0).
    same = l2r.order_set_delta(frozen, frozen, 6689)
    assert same["a_minus_b"] == [] and same["b_minus_a"] == []
    assert same["intersection_size"] == 6689


# ---- Stage-A verify-reuse (injected fixtures only) ----

def test_verify_reuse_positive_and_refusals():
    with p20r_root() as root:
        prior_path, alt_path, order_path, new_order_path, pins = reuse_fixture(root)
        kws = dict(prior=prior_path, alt_prior=alt_path,
                   order_file=order_path, new_order_file=new_order_path,
                   prior_digest=pins["prior_digest"],
                   alt_digest=pins["alt_digest"],
                   order_digest=pins["order_digest"],
                   new_order_digest=pins["new_order_digest"],
                   h1=pins["h1"], h2=pins["h2"], h_total=pins["h_total"],
                   k1=331, k2=6689, ce_alt=pins["ce_alt"],
                   ce_incumbent=pins["ce_incumbent"],
                   alt_ideal_length_bits=pins["alt_ideal_length_bits"],
                   d2_feasible=True)
        result = None
        with patched(p20m, "FROZEN_ORDER_DIGEST", pins["order_digest"]), \
                patched(p20m, "FROZEN_ORDER_PROGRAM_PIN", "test-frozen-A-program-pin"), \
                patched(p20m, "FROZEN_DERIVATION_SEEDS",
                        tuple(2026092291 + i for i in range(4))), \
                patched(p20n, "FROZEN_ALT_DIGEST", pins["alt_digest"]), \
                patched(p20n, "FROZEN_H1_INC", pins["h1"]), \
                patched(l2r, "FROZEN_SESSION_PRIOR_DIGEST", pins["prior_digest"]), \
                patched(l2r, "FROZEN_ORDER_DIGEST_A", pins["order_digest"]), \
                patched(l2r, "FROZEN_ALT_DIGEST", pins["alt_digest"]), \
                patched(l2r, "FROZEN_NEW_ORDER_DIGEST_B",
                        pins["new_order_digest"]):
            result = l2r.verify_reuse(**kws)
            assert result["verified"] is True
            assert result["dev_contact"] == 0
            assert result["prior_digest"] == pins["prior_digest"]
            assert result["alt_file_digest"] == pins["alt_digest"]
            assert result["order_digest_A"] == pins["order_digest"]
            assert result["new_order_digest_B"] == pins["new_order_digest"]
            assert result["new_order_program"] == l2r.NEW_ORDER_PROGRAM_PIN
            assert result["d2_feasible"] is True
            assert result["k_literals"]["k_total"] == 7020
            assert result["set_delta"]["size_delta_b_minus_a"] == 0
            # every replay pin refuses on mismatch with DEV untouched.
            bad = dict(kws)
            bad["prior_digest"] = "0" * 64
            assert_raises_match(ValueError, "reuse_prior_identity",
                                l2r.verify_reuse, **bad)
            bad = dict(kws)
            bad["alt_digest"] = "0" * 64
            assert_raises_match(ValueError, "reuse_alt_identity",
                                l2r.verify_reuse, **bad)
            bad = dict(kws)
            bad["order_digest"] = "0" * 64
            assert_raises_match(ValueError, "reuse_order_freeze_A",
                                l2r.verify_reuse, **bad)
            bad = dict(kws)
            bad["new_order_digest"] = "0" * 64
            assert_raises_match(ValueError, "new_order_identity_B",
                                l2r.verify_reuse, **bad)
            bad = dict(kws)
            bad["k1"] = 332
            assert_raises_match(ValueError, "k_literal_exact",
                                l2r.verify_reuse, **bad)
            bad = dict(kws)
            bad["ce_alt"] = float(pins["ce_alt"]) + 1.0
            assert_raises_match(ValueError,
                                "alt_construction_budget_feasibility",
                                l2r.verify_reuse, **bad)
            bad = dict(kws)
            bad["d2_feasible"] = False
            assert_raises_match(ValueError,
                                "alt_construction_budget_feasibility",
                                l2r.verify_reuse, **bad)
            bad = dict(kws)
            bad["h_total"] = float(pins["h_total"]) + 1e-6
            assert_raises_match(ValueError, "reuse_prior_identity",
                                l2r.verify_reuse, **bad)
        assert result is not None


def test_cli_mode_refusals(capsys):
    assert l2r.main(["--verify-reuse", "--prior", "x"]) == 2
    _, err = capsys.readouterr()
    assert "missing required --verify-reuse flags" in err
    assert l2r.main(["--derive-new-order", "--prior", "x"]) == 2
    _, err = capsys.readouterr()
    assert "missing required --derive-new-order flags" in err
    assert l2r.main([]) == 2
    _, err = capsys.readouterr()
    assert "ambiguous invocation refused" in err
    assert l2r.main(["--verify-reuse", "--derive-new-order",
                     "--prior", "p"]) == 2
    _, err = capsys.readouterr()
    assert "never combine" in err
    with p20r_root() as root:
        _, _, _, _, pins = reuse_fixture(root)
        rc = l2r.main([
            "--verify-reuse",
            "--prior", "p", "--prior-digest", pins["prior_digest"],
            "--alt-prior", "a", "--alt-digest", pins["alt_digest"],
            "--order-file", "o", "--order-digest", pins["order_digest"],
            "--new-order-file", "n", "--new-order-digest",
            pins["new_order_digest"],
            "--k1", "331", "--k2", "6689", "--tag-master", "2026092340",
        ])
        assert rc == 2
        _, err = capsys.readouterr()
        assert "takes no Stage-B-only flags" in err
        rc = l2r.main([
            "--derive-new-order",
            "--prior", "p", "--prior-digest", pins["prior_digest"],
            "--order-file", "o", "--out", "n",
            "--k1", "331",
        ])
        assert rc == 2
        _, err = capsys.readouterr()
        assert "takes no Stage-B-only flags" in err


# ---- 1.5M VAL-remainder population + gate family (b)-(e) ----

def test_val_remainder_population_and_gate_family():
    table = val_remainder_table()
    formation = l2r.form_val_remainder_blocks(table)
    assert formation["dev_frame_range"] == [2044, 2171]
    assert formation["dev_frames"] == 128
    assert formation["dev_pairs"] == 32768
    assert [tuple(r) for r in formation["block_ranges"]] == [(2044, 2171)]
    assert len(formation["blocks"]) == 1
    for block in formation["blocks"]:
        assert block["labels"].size == 32768
        assert int(block["high"].max()) < 32 and int(block["low"].max()) < 32
    assert formation["remainder"] == {
        "frame_start": 2172, "frame_end": 2212, "frames": 41,
        "symbols": 10496, "used": False}
    assert l2r.verify_val_remainder_containment()["verified"] is True
    assert l2r.verify_consumed_exclusions_val_remainder()["verified"] is True
    assert l2r.verify_consumed_exclusions_val_remainder()["build_frames"] == [0, 1659]
    # declared-range refusals refuse before any content open.
    assert_raises_match(ValueError, "dev-frames",
                        l2r.form_val_remainder_blocks, table,
                        dev_frames=(2044, 2170))
    assert_raises_match(ValueError, "remainder-frames",
                        l2r.form_val_remainder_blocks, table,
                        remainder_frames=(2172, 2213))
    assert_raises_match(ValueError, "BLOCKED(dev_block_range_identity)",
                        l2r.verify_val_remainder_containment, (2044, 2170))
    # consumed 1.5M VAL DEV / TRAIN / HOLD refuse in the remainder.
    assert_raises_match(ValueError, "consumed 1.5M VAL DEV",
                        l2r.verify_val_remainder_containment, (1660, 2043))
    assert_raises_match(ValueError, "outside 1.5M VAL",
                        l2r.verify_val_remainder_containment, (2213, 2724))
    assert_raises_match(ValueError, "consumed 1.5M TRAIN",
                        l2r.verify_consumed_exclusions_val_remainder, (0, 1659))
    assert_raises_match(ValueError, "consumed 1.5M HOLD",
                        l2r.verify_consumed_exclusions_val_remainder,
                        (2044, 2171), (2213, 2766))
    # cross-file gate: the 1M pool and the 2M session refuse by path.
    assert_raises_match(ValueError, "1M full-pool",
                        l2r.verify_dev_source_identity_1p5m,
                        l2r.REFUSED_1M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "reserved 2M",
                        l2r.verify_dev_source_identity_1p5m,
                        l2r.REFUSED_2M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "dev-pairs",
                        l2r.verify_dev_source_identity_1p5m, "elsewhere.parquet")
    # malformed population refuses inside the formation.
    bad = table.copy()
    bad.loc[bad.index[0], "bob_symbol"] = 1024
    assert_raises_match(ValueError, "dev_population_exact",
                        l2r.form_val_remainder_blocks, bad)
    bad2 = table.copy()
    bad2 = bad2[bad2["frame_id"] != 2044]
    assert_raises_match(ValueError, "dev_population_exact",
                        l2r.form_val_remainder_blocks, bad2)


# ---- IR-1..IR-5 recorder formulas, caps, nullability ----

def test_ir_recorder_formulas_caps_and_nullability():
    _, p2, view, order = tiny_ir_fixture()
    n = int(view["bob"].size)
    k2 = TEST_K2
    prefix = order[:k2]
    ir = ir_recorder(view, p2, order,
                     {"first_error_layer": "L1", "first_error_coord": 9})
    assert set(ir) == set(l2r.IR_FIELDS)
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
    pm = float(np.mean(p20n._hazard_bits(
        p2, view["high"][prefix], view["bob"][prefix], view["low"][prefix])))
    assert abs(ir["ir3_thresh_lo_bits"] - pm) <= 1e-12
    assert abs(ir["ir3_thresh_hi_bits"] - 2.0 * pm) <= 1e-12
    prefix_haz = p20n._hazard_bits(
        p2, view["high"][prefix], view["bob"][prefix], view["low"][prefix])
    assert ir["ir3_prefix_above_lo_count"] == int(np.sum(prefix_haz > pm))
    assert ir["ir3_prefix_above_lo_frac"] == int(np.sum(prefix_haz > pm)) / k2
    assert ir["ir3_prefix_above_hi_count"] == int(np.sum(prefix_haz > 2.0 * pm))
    assert ir["ir3_prefix_above_hi_frac"] == int(
        np.sum(prefix_haz > 2.0 * pm)) / k2
    # IR-4: top-16 hazards with 1-based ranks.
    hazards = p20n._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
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
    with patched(l2r, "FROZEN_K2", k2):
        assert_raises_match(ValueError, "gated prefix length",
                            l2r._ir_hazard_diagnostics, view=view, p2_arm=p2,
                            l2_order=order, k2=k2 - 1,
                            first_error={"first_error_layer": None,
                                         "first_error_coord": None},
                            prefix_mean=pm)
        # an L2 failure without a valid coordinate refuses (never a silent null).
        assert_raises_match(ValueError, "valid natural block symbol index",
                            l2r._ir_hazard_diagnostics, view=view, p2_arm=p2,
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
    k2 = int(l2r.FROZEN_K2)
    prefix = order[:k2]
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    hazards = p20n._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
    pm = float(np.mean(hazards[mask]))
    base = l2r._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": None, "first_error_coord": None},
        prefix_mean=pm)
    assert l2r.ir_payload_complete([]) is False
    assert l2r.ir_payload_complete([dict(base, outcome="exact",
                                        first_error_layer=None)]) is True
    pos = int(prefix[3])
    l2rec = dict(l2r._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": "L2", "first_error_coord": pos},
        prefix_mean=pm),
        outcome="verify_failed", first_error_layer="L2")
    assert l2r.ir_payload_complete([l2rec]) is True
    # IR-5 truncation flag is frozen true at N=32768.
    assert l2rec["ir5_series_truncated"] is True
    assert len(l2rec["ir5_series_hazard_bits"]) == 4096
    # every refusal mode fails the gate.
    assert l2r.ir_payload_complete(
        [dict(l2rec, ir4_topk_coords=l2rec["ir4_topk_coords"][:15])]) is False
    assert l2r.ir_payload_complete(
        [dict(l2rec,
              ir2_first_error_hazard_rank_pct=None)]) is False
    assert l2r.ir_payload_complete(
        [dict(base, outcome="exact", first_error_layer=None,
              ir2_first_error_hazard_rank_pct=0.5)]) is False
    assert l2r.ir_payload_complete(
        [dict(l2rec, ir5_series_truncated=False)]) is False
    dropped = dict(l2rec)
    del dropped["ir3_thresh_hi_bits"]
    assert l2r.ir_payload_complete([dropped]) is False
    # resource_abort records are skipped, never passed.
    abort = dict(l2rec, outcome="resource_abort")
    assert l2r.ir_payload_complete([abort]) is True


def test_ir_payload_tables_descriptive():
    _, p2, view, _ = tiny_ir_fixture(n=32768, seed=TEST_SEEDS[5])
    n = 32768
    rng = np.random.default_rng(TEST_SEEDS[5])
    order = rng.permutation(n).astype(np.int64)
    k2 = int(l2r.FROZEN_K2)
    prefix = order[:k2]
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    hazards = p20n._hazard_bits(p2, view["u1_cond"], view["bob"], view["low"])
    pm = float(np.mean(hazards[mask]))
    rec_a = dict(l2r._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": None, "first_error_coord": None},
        prefix_mean=pm),
        outcome="exact", arm="A_frozen-order_operational", block_index=0)
    pos = int(prefix[11])
    rec_b = dict(l2r._ir_hazard_diagnostics(
        view=view, p2_arm=p2, l2_order=order, k2=k2,
        first_error={"first_error_layer": "L2", "first_error_coord": pos},
        prefix_mean=pm),
        outcome="verify_failed", arm="B_new-order_operational", block_index=0,
        first_error_layer="L2")
    tables = l2r.ir_payload_tables([rec_a, rec_b])
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


def test_nine_scalars_arm_specific_digest():
    counts = sparse_counts(TEST_SEEDS[6])
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.asarray(arrays["p2"], dtype=np.float64)
    rng = np.random.default_rng(TEST_SEEDS[6])
    n = 256
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    block = {"block_index": 0, "frame_start": 2044, "frame_end": 2171,
             "high": high, "low": low, "bob": bob}
    view = {"bob": bob, "high": high, "low": low, "u1_cond": high}
    order = rng.permutation(n).astype(np.int64)
    first_error = {"first_error_layer": None, "first_error_coord": None}
    nine_a = l2r._nine_scalars_for_arm(
        arm_name="A_frozen-order_operational", block=block, view=view,
        p2_arm=p2, counts_arr=np.asarray(arrays["counts_ab"]),
        l2_order=order, k2=6689, first_error=first_error, field=None,
        low_hat=low)
    nine_b = l2r._nine_scalars_for_arm(
        arm_name="B_new-order_operational", block=block, view=view,
        p2_arm=p2, counts_arr=np.asarray(arrays["counts_ab"]),
        l2_order=order, k2=6689, first_error=first_error, field=None,
        low_hat=low)
    # the computation is the accepted recorder's; only the digest label is
    # arm-specific (frozen-A on A/C, new-B on B/D).
    assert nine_a["l2_order_digest"] == l2r.FROZEN_ORDER_DIGEST_A
    assert nine_b["l2_order_digest"] == l2r.FROZEN_NEW_ORDER_DIGEST_B
    assert nine_a["l2_order_digest"] != nine_b["l2_order_digest"]
    assert nine_a["l2_prefix_len"] == 6689
    assert set(nine_a) == set(p20o.HAZARD_FIELDS)
    assert l2r._arm_order_digest("C_frozen-order_oracle") == l2r.FROZEN_ORDER_DIGEST_A
    assert l2r._arm_order_digest("D_new-order_oracle") == l2r.FROZEN_NEW_ORDER_DIGEST_B
    assert_raises_match(ValueError, "unknown frozen arm",
                        l2r._arm_order_digest, "Z_unknown")
    # the arm-specific gate accepts per-arm digests with frozen nullability.
    rec_a = dict(nine_a, outcome="exact", arm="A_frozen-order_operational",
                 first_error_layer=None)
    rec_b = dict(nine_b, outcome="exact", arm="B_new-order_operational",
                 first_error_layer=None)
    assert l2r.hazard_instrumentation_complete([rec_a, rec_b]) is True
    assert l2r.hazard_instrumentation_complete(
        [dict(rec_a, l2_order_digest=nine_b["l2_order_digest"])]) is False
    assert l2r.hazard_instrumentation_complete([]) is False


# ---- truth isolation (recording-only, post-decode) ----

def test_truth_isolation_ir_recording_only(monkeypatch):
    counts = sparse_counts(TEST_SEEDS[6])
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.asarray(arrays["p2"], dtype=np.float64)
    p1 = np.asarray(arrays["p1"], dtype=np.float64)
    rng = np.random.default_rng(TEST_SEEDS[6])
    n = 64
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    block = {"block_index": 0, "frame_start": 2044, "frame_end": 2171,
             "high": high, "low": low, "bob": bob}
    view = {"bob": bob, "high": high, "low": low,
            "u2": np.zeros(n, dtype=np.int64)}
    result = opf.OperationalBlockResult(
        stream_seed=2044, block_index=0, outcome="exact", exact=True,
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
        return {field: "sentinel" for field in l2r.IR_FIELDS}

    monkeypatch.setattr(l2r, "_ir_hazard_diagnostics", hostile_ir_recorder)
    record = l2r._operational_record(
        result, spec=l2r.ArmSpec(
            "A_frozen-order_operational", "operational", 331, 6689,
            5 * 7020 + 64, l2r.OPERATIONAL_PROVENANCE, "alt"),
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
    assert record["arm"] == "A_frozen-order_operational"
    assert record["l2_construction"] == "alt-α1"
    assert record["key_bit_delta_vs_control"] == 0
    assert record["protocol"] == l2r.PROTOCOL_NAME


def test_ir_truth_mutation_changes_recording_only():
    # a denser synthetic prior so the truth mutation moves prefix hazards
    # (sparse-count fixtures can be last-axis-degenerate).
    rng = np.random.default_rng(TEST_SEEDS[6])
    counts = sparse_counts(TEST_SEEDS[6], cells=16384, hi=200)
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.ascontiguousarray(np.asarray(arrays["p2"], dtype=np.float64))
    n = 512
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    order = rng.permutation(n).astype(np.int64)
    view = {"bob": bob, "high": high, "low": low, "u1_cond": high}
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
    assert n == 512
    assert "ir" not in l2r.run_l2_order_position_1p5m.__code__.co_varnames


# ---- no Stage-B root + zero protected opens + zero Stage-B sampling ----

def test_no_stage_b_root_and_no_protected_opens_in_stage_a():
    assert not Path(l2r.FROZEN_OUT_ROOT).exists()
    assert Path(l2r.FROZEN_OUT_ROOT).name == "l2_order_position_1p5m"
    assert l2r._DEV_PARQUET_CONTENT_OPENED is False
    assert l2r._ALT_CONTENT_LOADED is False
    assert l2r._SESSION_PRIOR_CONTENT_LOADED is False
    source = Path(l2r.__file__).read_text(encoding="utf-8")
    for token in ("load_v25_channel_counts", "smooth_joint_to_conditional",
                  "LAMBDA_STAR", "137.3823795883264"):
        assert token not in source, token
    for token in ("_ir_hazard_diagnostics", "reuse_prior_identity",
                  "reuse_alt_identity", "reuse_order_freeze_A",
                  "new_order_identity_B", "order_derivation_program_identity",
                  "verify_val_remainder_containment",
                  "verify_consumed_exclusions_val_remainder",
                  "ir_payload_complete", "derive_new_l2_order",
                  "nbpolar-p20r-order-position-1p5m-seed",
                  "from . import l2_alt_hold_ir_2m",
                  "verify_reuse", "run_l2_order_position_1p5m",
                  "k_literal_exact",
                  "alt_construction_budget_feasibility_replayed",
                  "TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE"):
        assert token in source, token
    assert "2026092340" in source
    # the four frozen arms carry the single-factor order delta (same K, same
    # alpha1 tables, frozen-A prefixes on A/C, new-B prefixes on B/D).
    assert l2r.FROZEN_ARM_NAMES == (
        "A_frozen-order_operational", "B_new-order_operational",
        "C_frozen-order_oracle", "D_new-order_oracle")
    # the nine carried scalars (incl. the ninth U-domain scalar) ride the
    # accepted 1.5M recorder, called at the carried-over code point.
    assert "_l2_hazard_diagnostics" in source
    assert "l2_fail_in_prefix_u_domain" in source


def test_zero_stage_b_sampling_pin():
    parser = l2r.build_parser()
    options = set()
    for action in parser._actions:
        options.update(action.option_strings)
    for forbidden in ("--train-seeds", "--seed", "--sample", "--rng", "--genie",
                      "--deriv-seeds-stage-b", "--derive"):
        assert forbidden not in options, forbidden
    for name in l2r.STAGE_B_FLAGS:
        assert "seed" not in name and "sample" not in name
    assert "--verify-reuse" in options
    assert "--derive-new-order" in options
    assert "seeds" not in l2r.run_l2_order_position_1p5m.__code__.co_varnames
    assert "genie" not in l2r.run_l2_order_position_1p5m.__code__.co_varnames
    assert "seeds" not in l2r.derive_new_l2_order.__code__.co_varnames
    source = Path(l2r.__file__).read_text(encoding="utf-8")
    assert "default_rng" not in source
    assert "sample_full_block" not in source


def test_one_open_guards_refuse_reload(monkeypatch):
    monkeypatch.setattr(
        l2r, "verify_predecessor_construction", lambda *a, **k: {"record": {}})
    monkeypatch.setattr(
        l2r, "verify_dev_manifest_1p5m",
        lambda *a, **k: {"train_pairs": 424960, "val_pairs": 141568,
                         "hold_pairs": 141824})
    monkeypatch.setattr(
        l2r, "verify_stage_b_order_file_p20m",
        lambda *a, **k: {"verified": True, "order_digest": "x",
                         "l1_order": np.zeros(32768, dtype=np.int64),
                         "l2_order": np.zeros(32768, dtype=np.int64),
                         "k1": 331, "k2": 6689})
    monkeypatch.setattr(
        l2r, "verify_new_order_file",
        lambda *a, **k: {"verified": True, "new_order_digest": "y",
                         "program": l2r.NEW_ORDER_PROGRAM_PIN,
                         "l1_order": np.zeros(32768, dtype=np.int64),
                         "l2_order": np.zeros(32768, dtype=np.int64),
                         "k1": 331, "k2": 6689})
    base = dict(prior_path="p", prior_digest=l2r.FROZEN_SESSION_PRIOR_DIGEST,
                alt_prior_path="a", alt_digest=l2r.FROZEN_ALT_DIGEST,
                source="1p5M", floor=1e-15, n=32768, k1=331, k2=6689,
                construction="c",
                construction_digest=l2r.FROZEN_CONSTRUCTION_DIGEST,
                manifest_path="m", dev_pairs=l2r.FROZEN_DEV_PAIRS_PATH,
                order_file="o", order_digest=l2r.FROZEN_ORDER_DIGEST_A,
                new_order_file="n", new_order_digest=l2r.FROZEN_NEW_ORDER_DIGEST_B,
                tag_master=2026092340)
    with p20r_root() as root, restored_guards():
        out = str(root / "out")
        l2r._SESSION_PRIOR_CONTENT_LOADED = True
        assert_raises_match(ValueError, "reload refused",
                            l2r.run_l2_order_position_1p5m, out_dir=out, **base)
        assert not Path(out).exists()
        l2r._SESSION_PRIOR_CONTENT_LOADED = False
        l2r._ALT_CONTENT_LOADED = True
        assert_raises_match(ValueError, "reload refused",
                            l2r.run_l2_order_position_1p5m, out_dir=out,
                            prior={}, **base)
        assert not Path(out).exists()
        l2r._ALT_CONTENT_LOADED = False
        l2r._DEV_PARQUET_CONTENT_OPENED = True
        assert_raises_match(ValueError, "reopen refused",
                            l2r.run_l2_order_position_1p5m, out_dir=out,
                            prior={}, alt_prior={}, **base)
        assert not Path(out).exists()


# ---- injected end-to-end single-block dual-order run (no protected data) ----

def test_injected_end_to_end_single_block_dual_order(monkeypatch):
    with p20r_root() as root:
        prior_path, alt_path, order_path, new_order_path, pins = reuse_fixture(root)
        with open(prior_path, "rb") as fh:
            data = np.load(fh, allow_pickle=False)
            with data:
                prior_arrays = {k: np.asarray(data[k]) for k in data.files}
        with open(alt_path, "rb") as fh:
            data = np.load(fh, allow_pickle=False)
            with data:
                alt_arrays = {k: np.asarray(data[k]) for k in data.files}
        table = val_remainder_table(seed=TEST_SEEDS[1])
        monkeypatch.setattr(
            l2r, "verify_predecessor_construction",
            lambda *a, **k: {"record": {"n": 32768}})
        monkeypatch.setattr(
            l2r, "verify_dev_manifest_1p5m",
            lambda *a, **k: {"train_pairs": 424960, "val_pairs": 141568,
                             "hold_pairs": 141824})
        out = str(root / "l2_order_position_1p5m")
        with patched(l2r, "FROZEN_H1", pins["h1"]), \
                patched(l2r, "FROZEN_H2", pins["h2"]), \
                patched(l2r, "FROZEN_H_TOTAL", pins["h_total"]), \
                patched(p20m, "FROZEN_ORDER_DIGEST", pins["order_digest"]), \
                patched(p20m, "FROZEN_ORDER_PROGRAM_PIN",
                        "test-frozen-A-program-pin"), \
                patched(p20m, "FROZEN_DERIVATION_SEEDS",
                        tuple(2026092291 + i for i in range(4))), \
                patched(p20n, "FROZEN_ALT_DIGEST", pins["alt_digest"]), \
                patched(p20n, "FROZEN_H1_INC", pins["h1"]), \
                patched(l2r, "FROZEN_SESSION_PRIOR_DIGEST",
                        pins["prior_digest"]), \
                patched(l2r, "FROZEN_ORDER_DIGEST_A", pins["order_digest"]), \
                patched(l2r, "FROZEN_ALT_DIGEST", pins["alt_digest"]), \
                patched(l2r, "FROZEN_NEW_ORDER_DIGEST_B",
                        pins["new_order_digest"]), \
                restored_guards():
            run = l2r.run_l2_order_position_1p5m(
                prior=dict(prior_arrays), alt_prior=dict(alt_arrays),
                prior_digest=pins["prior_digest"],
                alt_digest=pins["alt_digest"], source="1p5M", floor=1e-15,
                n=32768, k1=331, k2=6689, construction="c",
                construction_digest=l2r.FROZEN_CONSTRUCTION_DIGEST,
                manifest_path="m", dev_table=table,
                dev_pairs=l2r.FROZEN_DEV_PAIRS_PATH,
                dev_frames=(2044, 2171), block_frames=128,
                remainder_frames=(2172, 2212), tag_master=2026092340,
                chunk_rows=512, tag_bits=64, order_file=str(order_path),
                order_digest=pins["order_digest"],
                new_order_file=str(new_order_path),
                new_order_digest=pins["new_order_digest"], out_dir=out)
            summary = run.summary
            records = list(run.records)
            assert summary["records_completed"] == 4
            assert {r["arm"] for r in records} == set(l2r.FROZEN_ARM_NAMES)
            assert summary["stage_b_sampling_calls"] == 0
            # arm-specific order digests: frozen-A on A/C, new-B on B/D.
            by_arm = {r["arm"]: r for r in records}
            assert by_arm["A_frozen-order_operational"]["l2_order_digest"] == \
                pins["order_digest"]
            assert by_arm["C_frozen-order_oracle"]["l2_order_digest"] == \
                pins["order_digest"]
            assert by_arm["B_new-order_operational"]["l2_order_digest"] == \
                pins["new_order_digest"]
            assert by_arm["D_new-order_oracle"]["l2_order_digest"] == \
                pins["new_order_digest"]
            # the order factor moves the prefix hazard means between A and B.
            assert by_arm["A_frozen-order_operational"][
                "l2_prefix_hazard_mean_bits"] != by_arm["B_new-order_operational"][
                "l2_prefix_hazard_mean_bits"]
            # IR-1..IR-5 all PRESENT on every completed record.
            assert l2r.ir_payload_complete(records) is True
            assert l2r.hazard_instrumentation_complete(records) is True
            # the byte-exact set-delta rides the summary with size-delta 0.
            assert summary["order_set_delta"]["size_delta_b_minus_a"] == 0
            assert summary["aggregates"]["maintenance"]["a_to_b_transition_table"]
            # five files land under the injected out root only.
            for name in l2r.OUTPUT_FILES:
                assert (Path(out) / name).exists(), name


# ---- seed-domain grep rule ----

def test_grep_rule_seed_placement():
    master = "2026092340"
    test_seeds = [str(seed) for seed in TEST_SEEDS]
    module_source = Path(l2r.__file__).read_text(encoding="utf-8")
    test_source = Path(__file__).read_text(encoding="utf-8")
    assert master in module_source
    for seed in test_seeds:
        assert seed in test_source, seed
        assert seed not in module_source, seed
    assert l2r.FROZEN_TAG_MASTER == 2026092340
    assert l2r.FROZEN_TAG_MASTER not in (
        p20m.FROZEN_TAG_MASTER, p20l.FROZEN_TAG_MASTER,
        p20q.FROZEN_TAG_MASTER)
    allowed_prefixes = (
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_order_position_1p5m.py",
        "comparison_bench/tests/test_nbpolar_l2_order_position_1p5m.py",
        ".workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20r/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md",
    )
    for literal in [master] + test_seeds:
        for hit in _git_grep_hits(literal):
            assert hit.startswith(allowed_prefixes), (literal, hit)
