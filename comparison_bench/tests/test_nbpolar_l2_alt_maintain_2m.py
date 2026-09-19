"""Focused Phase 4-P20O 2M maintain-confirmation tests.

Injected/synthetic counts, priors, artifacts and fresh additive
``workspace/p20o/<uuid>/`` temp roots only. The V25 channel-counts NPZ, every
registered pairs parquet (1M, 1.5M VAL/HOLD/TRAIN, 2M), the real P16
construction root, the real split manifest, the accepted P20M/P20N worktree
products and every accepted evidence root are NEVER content-opened, statted,
or listed here: the single protected counts open happens only in the
authorized Stage-A derivation command, never in tests. The 2M derivation
sampler is replaced by a deterministic stub in tests (the real 16-block
L1+L2 genie sampling runs only in the authorized Stage-A derivation).
Focused tests use their own fresh seeds ``2026092311..2026092317`` and never
the frozen P20O tag master ``2026092310`` or the derivation seeds
``2026092321..2026092324`` (except through the frozen module constants).
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
    l2_alt_maintain_2m as l2m,
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
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_construction import (
    entropy_bits,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
    polar_transform,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never the frozen P20O tag master 2026092310 or the
# derivation seeds 2026092321..2026092324.
TEST_SEEDS = (2026092311, 2026092312, 2026092313, 2026092314,
              2026092315, 2026092316, 2026092317)

FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63

# Test-local gated prefix length / order digest for the recorder seam.
TEST_K2 = 1000
TEST_ORDER_DIGEST = "test-order-digest"


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
    """Derivation tests consume one-open guards; restore them afterwards."""
    state = (
        l2m._COUNTS_CONTENT_OPENED, l2m._COUNTS_CONTENT_OPENS,
        l2m._SESSION_PRIOR_CONTENT_LOADED, l2m._ALT_CONTENT_LOADED,
        l2m._DEV_PARQUET_CONTENT_OPENED,
    )
    try:
        yield
    finally:
        (l2m._COUNTS_CONTENT_OPENED, l2m._COUNTS_CONTENT_OPENS,
         l2m._SESSION_PRIOR_CONTENT_LOADED, l2m._ALT_CONTENT_LOADED,
         l2m._DEV_PARQUET_CONTENT_OPENED) = state


@contextlib.contextmanager
def p20o_root():
    """Fresh additive workspace/p20o/<uuid>/ temp root, cleaned afterwards."""
    root = REPO_ROOT / "workspace" / "p20o" / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    assert "workspace" in root.parts and "p20o" in root.parts
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


def counts_npz(directory, counts: np.ndarray, name: str = "counts.npz") -> Path:
    """Fabricate a V25-shaped counts npz holding ONLY the 2M key (fixture)."""
    path = Path(directory) / name
    with open(path, "wb") as fh:
        np.savez(fh, **{l2m.FROZEN_COUNTS_KEY: counts})
    return path


def fake_sampler(p_b, f_raw, p1, p2, *, seeds, blocks_per_seed, n):
    """Deterministic cheap stand-in for the Stage-A 16-block genie sampling.

    Returns pooled risk vectors with the frozen shapes and the frozen
    32-genie-call accounting; used ONLY by the injected derive tests (the
    real sampler runs once in the authorized Stage-A derivation).
    """
    rng = np.random.default_rng(int(seeds[0]))
    e1 = 0.10 + 0.05 * rng.random(n)
    h1 = 0.05 + 0.05 * rng.random(n)
    e2 = 0.20 + 0.10 * rng.random(n)
    h2 = 0.10 + 0.10 * rng.random(n)
    return {
        "e1_mean": e1,
        "h1_mean": h1,
        "e2_mean": e2,
        "h2_mean": h2,
        "blocks_attempted": int(len(seeds)) * int(blocks_per_seed),
        "blocks_used": int(len(seeds)) * int(blocks_per_seed),
        "blocks_impossible": 0,
        "calls": {"genie": 2 * int(len(seeds)) * int(blocks_per_seed)},
        "provenance_violations": 0,
    }


@contextlib.contextmanager
def stubbed_sampler():
    original = p20m.sample_synthetic_train_blocks
    p20m.sample_synthetic_train_blocks = fake_sampler
    try:
        yield
    finally:
        p20m.sample_synthetic_train_blocks = original


def derive_stub(root, *, seed: int = TEST_SEEDS[4], counts: np.ndarray | None = None):
    """Run the Stage-A derivation on a synthetic counts fixture."""
    if counts is None:
        counts = sparse_counts(seed)
    fixture = counts_npz(root, counts)
    with restored_guards(), stubbed_sampler(), \
            patched(l2m, "FROZEN_COUNTS_PATH", str(fixture)):
        return l2m.run_derive_stage_a(
            counts_path=fixture, source="2M", alpha=1, floor=1e-15, n=32768,
            target_f=1.3, seeds=l2m.FROZEN_DERIVATION_SEEDS,
            out_prior_path=root / "raw_prior.npz",
            out_orders_path=root / "orders.json",
            out_alt_path=root / "alt.npz",
            expected_counts_total=int(round(float(counts.sum()))),
        )


def val_table(*, seed: int = TEST_SEEDS[2]) -> pd.DataFrame:
    """VAL-like pairs frame: 640 DEV frames 2187..2826 + 89-frame remainder."""
    rng = np.random.default_rng(int(seed))
    frames = np.repeat(np.arange(2187, 2827), 256)
    pair_idx = np.tile(np.arange(256), 640)
    dev = pd.DataFrame({
        "frame_id": frames,
        "pair_idx": pair_idx,
        "alice_symbol": rng.integers(0, 1024, size=frames.size),
        "bob_symbol": rng.integers(0, 1024, size=frames.size),
    })
    rem_frames = np.repeat(np.arange(2827, 2916), 256)
    rem = pd.DataFrame({
        "frame_id": rem_frames,
        "pair_idx": np.tile(np.arange(256), 89),
        "alice_symbol": rng.integers(0, 1024, size=rem_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=rem_frames.size),
    })
    # Extra rows outside the DEV/remainder spans must not influence slicing.
    extra = pd.DataFrame({
        "frame_id": np.repeat([0, 2186, 2916, 3644], 256),
        "pair_idx": np.tile(np.arange(256), 4),
        "alice_symbol": rng.integers(0, 1024, size=4 * 256),
        "bob_symbol": rng.integers(0, 1024, size=4 * 256),
    })
    return pd.concat([dev, rem, extra], ignore_index=True).sample(
        frac=1.0, random_state=int(seed)).reset_index(drop=True)


def tiny_hazard_fixture(*, seed: int = TEST_SEEDS[3], n: int = 4096):
    """Length-n natural-index truth vectors + tables for the §7 recorder."""
    rng = np.random.default_rng(int(seed))
    counts = sparse_counts(seed, cells=1024, hi=20)
    arrays = p20m.build_raw_prior_arrays(counts)
    p2 = np.ascontiguousarray(
        p20n.derive_alt_l2_arrays(
            counts, incumbent_p1=np.asarray(arrays["p1"]),
            incumbent_p_b=np.asarray(arrays["p_b"]),
            incumbent_h1=float(np.asarray(arrays["h1"])),
        )["p2_alt"])
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    order = rng.permutation(n).astype(np.int64)
    field = make_gf32()
    u2 = polar_transform(low, field=field, alpha=2)
    view = {"bob": bob, "high": high, "low": low, "u2": u2, "u1_cond": high}
    return counts, p2, view, order, field


def recorder(view, p2, counts, order, first_error, *, k2=TEST_K2,
             order_digest=TEST_ORDER_DIGEST, field=None, low_hat=None):
    with patched(l2m, "FROZEN_K2", k2), patched(l2m, "FROZEN_ORDER_DIGEST",
                                                order_digest):
        return l2m._l2_hazard_diagnostics(
            block={}, view=view, p2_arm=p2, counts_arr=counts, l2_order=order,
            k2=k2, first_error=first_error, field=field, low_hat=low_hat)


def _git_grep_hits(literal: str):
    proc = subprocess.run(
        ["git", "grep", "-l", "--untracked", literal, "--",
         "comparison_bench", "openspec", ".workbuddy", "docs"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1), proc.stderr
    return [line for line in proc.stdout.splitlines() if line.strip()]


# ---- frozen literals, arms, command ----

def test_frozen_literals_arms_and_population():
    assert l2m.FROZEN_SOURCE == "2M"
    assert l2m.FROZEN_SOURCE_TAG == "type2_2M_20260121_183657"
    assert l2m.FROZEN_N == 32768 and l2m.FROZEN_FLOOR == 1e-15
    assert l2m.FROZEN_ALPHA == 1.0 and l2m.FROZEN_TARGET_F == 1.3
    assert l2m.FROZEN_HAZARD_R == 8
    assert l2m.FROZEN_DEV_FRAME_RANGE == (2187, 2826)
    assert l2m.FROZEN_DEV_FRAMES == 640 and l2m.FROZEN_DEV_PAIRS == 163840
    assert l2m.FROZEN_BLOCK_COUNT == 5 and l2m.FROZEN_BLOCK_FRAMES == 128
    assert l2m.FROZEN_BLOCK_RANGES == (
        (2187, 2314), (2315, 2442), (2443, 2570), (2571, 2698), (2699, 2826))
    assert l2m.FROZEN_REMAINDER_FRAME_RANGE == (2827, 2915)
    assert l2m.FROZEN_REMAINDER_FRAMES == 89
    assert l2m.FROZEN_REMAINDER_SYMBOLS == 22784
    assert l2m.INTRA_FILE_VAL_FRAME_RANGE == (2187, 2915)
    assert l2m.INTRA_FILE_HOLD_FRAME_RANGE == (2916, 3644)
    assert l2m.CONSUMED_2M_TRAIN_FRAME_RANGE == (0, 2186)
    assert l2m.FROZEN_BUILD_FRAME_RANGE == (0, 2186)
    assert l2m.PLANNED_SC_CALLS == 30
    assert l2m.PLANNED_TAG_INVOCATIONS == 20
    assert l2m.PLANNED_RECORDS == 20
    assert l2m.FROZEN_PUBLIC_CONTROL_BITS == FROZEN_PUBLIC_BITS
    assert l2m.FROZEN_TAG_MASTER == 2026092310
    assert l2m.SEED_PREFIX == "nbpolar-p20o-maintain-2m-seed"
    assert l2m.FROZEN_DERIVATION_SEEDS == (2026092321, 2026092322,
                                           2026092323, 2026092324)
    assert l2m.FROZEN_TRAIN_BLOCKS_PER_SEED == 4
    assert l2m.FROZEN_TRAIN_GENIE_CALLS == 32
    assert l2m.FROZEN_COUNTS_KEY.endswith("_N_ab_train_N_ab_train")
    assert l2m.FROZEN_COUNTS_KEY.startswith("type2_2M_20260121_183657")
    assert l2m.RAW_PRIOR_NPZ_KEYS == (
        "counts_ab", "f_raw", "p1", "p2", "p_b", "lambda_star",
        "floor_value", "h1", "h2", "h_total")
    assert l2m.ALT_L2_NPZ_KEYS == (
        "counts_ab", "f_alt", "p1", "p2_alt", "alpha", "floor_value",
        "h1_inc", "h2_alt", "h_total_alt")
    assert l2m.HAZARD_FIELDS == (
        "l2_order_digest", "l2_prefix_len", "l2_fail_in_prefix",
        "l2_fail_hazard_bits", "l2_fail_nbhd_mean_bits",
        "l2_prefix_hazard_mean_bits", "l2_fail_nbhd_floor_frac",
        "l2_prefix_floor_frac", "l2_fail_in_prefix_u_domain")
    assert l2m.U_DOMAIN_FIELD == "l2_fail_in_prefix_u_domain"
    assert l2m.FROZEN_DEV_PAIRS_PATH.endswith(
        "type2_2M_20260121_183657/pairs.parquet")
    assert l2m.FROZEN_DEV_PAIRS_PATH == p20l.FROZEN_DEV_PAIRS_PATH.replace(
        "type2_1p5M_20260121_183806", "type2_2M_20260121_183657")
    assert l2m.FROZEN_DEV_PAIRS_SIZE == 2458335
    assert len(l2m.FROZEN_DEV_PAIRS_SHA256) == 64
    assert l2m.FROZEN_CONSTRUCTION_DIGEST == p20l.FROZEN_CONSTRUCTION_DIGEST
    if l2m.pins_are_frozen():
        table = l2m.check_frozen_arm_table()
        k1, k2 = l2m.FROZEN_K1, l2m.FROZEN_K2
        assert table["a"]["k1"] == table["b"]["k1"] == k1
        assert table["a"]["k2"] == table["b"]["k2"] == k2
        assert table["a"]["leakage_bits"] == table["b"]["leakage_bits"]
        assert table["c"]["k1"] == table["d"]["k1"] == 0
        assert table["c"]["k2"] == table["d"]["k2"] == k2
        assert table["b"]["leakage_bits"] - table["a"]["leakage_bits"] == 0
        assert table["d"]["leakage_bits"] - table["c"]["leakage_bits"] == 0
        assert table["a"]["leakage_bits"] == 5 * (k1 + k2) + 64
        assert table["c"]["leakage_bits"] == 5 * k2 + 64
        totals = l2m.planned_totals(k1, k2)
        assert totals["planned_key_dependent_bits"] == (
            5 * (2 * (5 * (k1 + k2) + 64) + 2 * (5 * k2 + 64)))
        assert totals["planned_public_control_bits"] == 20 * FROZEN_PUBLIC_BITS
        literal = l2m.check_k_literals(k1=k1, k2=k2)
        assert literal["k_total"] == l2m.FROZEN_K_TOTAL
        assert literal["budget_literal"] == l2m.FROZEN_BUDGET_LITERAL
        assert p20m.budget_literal_display(l2m.FROZEN_H_TOTAL) == \
            l2m.FROZEN_BUDGET_LITERAL
        assert l2m.FROZEN_ALT_CE_INSAMPLE > 0.0
        assert l2m.FROZEN_D2_FEASIBLE in (True, False)


def test_frozen_command_byte_identical_when_pins_applied():
    if not l2m.pins_are_frozen():
        return  # pre-freeze probe state; the filled state is re-run post-freeze
    rebuilt = l2m.frozen_command()
    assert l2m.FROZEN_COMMAND == rebuilt
    for token in ("l2_alt_maintain_2m", "--prior-digest", "--alt-digest",
                  "--alt-prior", "--source 2M", "--floor 1e-15", "--n 32768",
                  f"--k1 {l2m.FROZEN_K1} --k2 {l2m.FROZEN_K2}",
                  "--dev-frames 2187 2826", "--block-frames 128",
                  "--remainder-frames 2827 2915", "--tag-master 2026092310",
                  "--chunk-rows 512 --tag-bits 64", "--order-digest", "--out-dir",
                  "timeout 1200", l2m.FROZEN_SESSION_PRIOR_DIGEST,
                  l2m.FROZEN_ALT_DIGEST, l2m.FROZEN_ORDER_DIGEST):
        assert token in l2m.FROZEN_COMMAND, token


# ---- raw-prior math vs independent literal ----

def test_raw_prior_rule_vs_independent_literal():
    for seed in TEST_SEEDS:
        counts = sparse_counts(seed)
        arrays = l2m.raw_prior_arrays(counts)
        assert set(arrays) == set(l2m.RAW_PRIOR_NPZ_KEYS)
        mat = counts.astype(np.float64)
        n_b = mat.sum(axis=0)
        total = mat.sum()
        p_global = mat.sum(axis=1) / total
        expected = np.empty_like(mat)
        for b in range(1024):
            if n_b[b] == 0:
                expected[:, b] = p_global
            else:
                expected[:, b] = mat[:, b] / n_b[b]
        hits = int(np.sum(expected < l2m.FROZEN_FLOOR))
        floored = np.maximum(expected, l2m.FROZEN_FLOOR)
        floored = floored / floored.sum(axis=0, keepdims=True)
        assert np.abs(arrays["f_raw"] - floored).max() <= 1e-12
        assert np.abs(arrays["f_raw"].sum(axis=0) - 1.0).max() <= 1e-12
        assert float(np.asarray(arrays["lambda_star"])) == 0.0
        assert float(np.asarray(arrays["floor_value"])) == l2m.FROZEN_FLOOR
        # p_b cross-check (column totals / total) and H literals via
        # the accepted entropy functional (never hand-filled).
        p_b = np.asarray(arrays["p_b"])
        assert np.abs(p_b - n_b / total).max() <= 1e-12
        assert abs(float(p_b.sum()) - 1.0) <= 1e-12
        h1 = float(np.sum(p_b * entropy_bits(np.asarray(arrays["p1"]), axis=0)))
        h2 = float(np.sum(p_b[None, :] * np.asarray(arrays["p1"])
                          * entropy_bits(np.asarray(arrays["p2"]), axis=2)))
        assert abs(h1 - float(np.asarray(arrays["h1"]))) <= 1e-12
        assert abs(h2 - float(np.asarray(arrays["h2"]))) <= 1e-12
        assert abs(float(np.asarray(arrays["h_total"])) - (h1 + h2)) <= 1e-12
        digest = psc.canonical_prior_digest(arrays)
        assert digest == psc.canonical_prior_digest(l2m.raw_prior_arrays(counts))
        assert hits >= 0 and int(np.sum(n_b == 0)) >= 0


# ---- alt rule, key sets ----

def test_alt_rule_and_key_sets():
    for seed in TEST_SEEDS:
        counts = sparse_counts(seed)
        arrays = l2m.raw_prior_arrays(counts)
        alt = l2m.alt_tables_2m(counts, incumbent_arrays=arrays)
        assert set(alt["arrays"]) == set(l2m.ALT_L2_NPZ_KEYS)
        assert float(np.asarray(alt["arrays"]["alpha"])) == 1.0
        assert float(np.asarray(alt["arrays"]["floor_value"])) == l2m.FROZEN_FLOOR
        mat = counts.astype(np.float64)
        n_b = mat.sum(axis=0)
        expected = (mat + 1.0) / (n_b + 1024.0)[None, :]
        expected = np.maximum(expected, l2m.FROZEN_FLOOR)
        expected = expected / expected.sum(axis=0, keepdims=True)
        assert np.abs(np.asarray(alt["arrays"]["f_alt"]) - expected).max() <= 1e-12
        assert alt["p1_equality_max_abs_diff"] == 0.0
        assert np.abs(np.asarray(alt["arrays"]["p1"])
                      - np.asarray(arrays["p1"])).max() <= 1e-12
        assert abs(alt["h_total_alt"] - (alt["h1_inc"] + alt["h2_alt"])) <= 1e-12
        assert abs(alt["h1_inc"] - float(np.asarray(arrays["h1"]))) <= 1e-12
        assert alt["f_alt_min"] >= l2m.FROZEN_FLOOR
        assert alt["f_alt_max"] <= 1.0


# ---- artifact key sets / digests / mode refusals ----

def test_derive_end_to_end_artifacts():
    counts = sparse_counts(TEST_SEEDS[4])
    with p20o_root() as root:
        result = derive_stub(root, counts=counts)
        # raw prior artifact: 10 keys, digest over canonical arrays.
        prior_path = Path(result["prior_path"])
        with np.load(prior_path, allow_pickle=False) as data:
            prior_keys = set(str(k) for k in data.files)
            prior_arrays = {k: np.asarray(data[k]) for k in data.files}
        assert prior_keys == set(l2m.RAW_PRIOR_NPZ_KEYS)
        assert result["prior_digest"] == psc.canonical_prior_digest(prior_arrays)
        assert result["prior_digest"] == psc.canonical_prior_digest(
            l2m.raw_prior_arrays(counts))
        assert float(np.asarray(prior_arrays["lambda_star"])) == 0.0
        assert result["counts_content_opens"] == 1
        assert result["protected_content_opens"] == 1
        # orders json: protocol/kind/n/permutations/digest.
        orders_path = Path(result["order_path"])
        doc = json.loads(orders_path.read_text(encoding="utf-8"))
        assert doc["protocol"] == l2m.PROTOCOL_NAME
        assert doc["kind"] == "raw-prior-orders-file"
        assert int(doc["n"]) == 32768
        assert int(doc["k1"]) + int(doc["k2"]) == int(doc["k_total"])
        for key in ("l1_order", "l2_order"):
            order = np.asarray(doc[key], dtype=np.int64)
            assert order.shape == (32768,)
            assert np.array_equal(np.sort(order), np.arange(32768))
        assert result["order_digest"] == hashlib.sha256(
            orders_path.read_bytes()).hexdigest()
        assert doc["derivation"]["prior_digest"] == result["prior_digest"]
        assert doc["derivation"]["train_seeds"] == list(l2m.FROZEN_DERIVATION_SEEDS)
        assert int(doc["derivation"]["train_blocks_used"]) == 16
        assert int(doc["derivation"]["train_genie_calls"]) == 32
        assert doc["derivation"]["program"] == l2m.FROZEN_ORDER_PROGRAM_PIN
        # alt artifact: 9 keys + exact byte digest.
        alt_path = Path(result["alt_path"])
        payload = alt_path.read_bytes()
        assert result["alt_digest"] == hashlib.sha256(payload).hexdigest()
        with np.load(io.BytesIO(payload), allow_pickle=False) as data:
            assert set(str(k) for k in data.files) == set(l2m.ALT_L2_NPZ_KEYS)
            assert float(np.asarray(data["alpha"])) == 1.0
            assert float(np.asarray(data["floor_value"])) == 1e-15
            assert np.asarray(data["counts_ab"]).dtype == np.float64
            assert np.asarray(data["counts_ab"]).shape == (1024, 1024)
            assert np.asarray(data["f_alt"]).shape == (1024, 1024)
            assert np.asarray(data["p1"]).shape == (32, 1024)
            assert np.asarray(data["p2_alt"]).shape == (32, 1024, 32)
        assert result["counts_total"] == int(round(float(counts.sum())))
        assert result["train_blocks_used"] == 16
        assert result["train_genie_calls"] == 32
        assert result["decoder_calls"] == 0
        assert result["sampling_calls"] == 32
        assert result["alt_construction_budget_feasibility"] in (
            "FEASIBLE", "ALT_CONSTRUCTION_BUDGET_INFEASIBLE")
        assert result["d1"]["feasible"] == (
            result["alt_construction_budget_feasibility"] == "FEASIBLE")
        assert result["d1"]["counts_total"] == int(round(float(counts.sum())))
        assert result["d1"]["alt_feasibility_ceiling_bits"] == \
            5 * int(result["k2"]) + 64
        assert abs(result["d1"]["alt_ideal_length_bits"]
                   - result["d1"]["ce_alt_insample_bits_per_symbol"] * 32768) <= 1e-6
        # fail-if-present on every product.
        with contextlib.ExitStack() as stack:
            stack.enter_context(restored_guards())
            stack.enter_context(stubbed_sampler())
            with patched(l2m, "FROZEN_COUNTS_PATH", str(root / "counts.npz")):
                assert_raises_match(
                    FileExistsError, "refusing to overwrite", l2m.run_derive_stage_a,
                    counts_path=root / "counts.npz", source="2M", alpha=1,
                    floor=1e-15, n=32768, target_f=1.3,
                    seeds=l2m.FROZEN_DERIVATION_SEEDS,
                    out_prior_path=root / "raw_prior.npz",
                    out_orders_path=root / "orders.json",
                    out_alt_path=root / "alt.npz",
                    expected_counts_total=int(round(float(counts.sum()))))


def test_cli_mode_refusals(capsys):
    assert l2m.main([]) == 2
    assert "ambiguous invocation refused" in capsys.readouterr().err
    assert l2m.main(["--derive"]) == 2
    assert "missing required Stage-A flags" in capsys.readouterr().err
    mixed = ["--derive", "--counts", "c", "--source", "2M", "--alpha", "1",
             "--floor", "1e-15", "--n", "32768", "--target-f", "1.3",
             "--deriv-seeds", "1", "2", "3", "4", "--out-prior", "p",
             "--out-orders", "o", "--out-alt", "a", "--k1", "1"]
    assert l2m.main(mixed) == 2
    assert "mixed invocation refused" in capsys.readouterr().err
    assert l2m.main(["--prior", "x"]) == 2
    assert "missing required Stage-B flags" in capsys.readouterr().err
    assert l2m.main(["--alpha", "1"]) == 2
    assert "Stage-A-only flags" in capsys.readouterr().err
    assert l2m.main(["--out-prior", "z"]) == 2
    assert "Stage-A-only flags" in capsys.readouterr().err
    assert l2m.main(["--out-dir", "z"]) == 2
    assert "missing required Stage-B flags" in capsys.readouterr().err


def test_k_literal_gate_refusals():
    if not l2m.pins_are_frozen():
        return  # pre-freeze probe state; re-run after the Stage-A fill
    assert_raises_match(ValueError, "k1=",
                        l2m.check_k_literals, k1=l2m.FROZEN_K1 + 1, k2=l2m.FROZEN_K2)
    assert_raises_match(ValueError, "k2=",
                        l2m.check_k_literals, k1=l2m.FROZEN_K1, k2=l2m.FROZEN_K2 + 1)
    assert_raises_match(ValueError, "source='2M'", l2m._check_source, "1M")
    assert_raises_match(ValueError, "source='2M'", l2m._check_source, "1p5M")
    assert_raises_match(ValueError, "n=32768", l2m._check_n, 1024)
    assert_raises_match(ValueError, "dev-frames", l2m._check_dev_frames, (2187, 2825))
    assert_raises_match(ValueError, "remainder-frames",
                        l2m._check_remainder_frames, (2827, 2916))
    assert_raises_match(ValueError, "tag-master", l2m._check_tag_master, 2026092280)
    assert_raises_match(ValueError, "prior-digest", l2m._check_prior_digest, "0" * 64)
    assert_raises_match(ValueError, "order-digest", l2m._check_order_digest, "0" * 64)
    assert_raises_match(ValueError, "alt-digest", l2m._check_alt_digest, "0" * 64)
    assert_raises_match(ValueError, "alpha", l2m._check_alpha, 0.5)
    assert_raises_match(ValueError, "target-f", l2m._check_target_f, 1.2)
    assert_raises_match(ValueError, "derivation requires the frozen seeds",
                        l2m._check_deriv_seeds, (1, 2, 3, 4))


# ---- D1 estimator exactness + D2 gate both ways ----

def test_d1_estimator_exact_tiny_fixture():
    counts = np.zeros((1024, 1024), dtype=np.float64)
    counts[0, 0] = 5.0           # u1 = 0, u2 = 0
    counts[33, 7] = 3.0          # u1 = 1, u2 = 1
    p2 = np.full((32, 1024, 32), 0.25, dtype=np.float64)
    p2[0, 0, 0] = 0.5
    p2[1, 7, 1] = 0.25
    ce = p20n.in_sample_l2_ce_bits_per_symbol(counts, p2)
    assert abs(ce - 1.375) <= 1e-12
    acc = 0.0
    for a, b in np.argwhere(counts > 0):
        acc += float(counts[a, b]) * (-np.log2(p2[(int(a) >> 5) & 31, int(b),
                                                  int(a) & 31]))
    assert abs(ce - acc / float(counts.sum())) <= 1e-12
    p2_zero = np.array(p2)
    p2_zero[0, 0, 0] = 0.0
    assert_raises_match(ValueError, "zero table mass",
                        p20n.in_sample_l2_ce_bits_per_symbol, counts, p2_zero)
    d1 = l2m.feasibility_literals_2m(counts, p2_incumbent=p2, p2_alt=p2,
                                     k2=6689, k_total=7020)
    assert d1["counts_total"] == 8
    assert d1["alt_feasibility_ceiling_bits"] == 33509
    assert d1["operational_ceiling_bits"] == 35164
    assert abs(d1["ce_alt_insample_bits_per_symbol"] - ce) <= 1e-12
    assert d1["feasible"] == (d1["alt_ideal_length_bits"] <= 33509)


def test_d2_gate_both_ways():
    counts = np.zeros((1024, 1024), dtype=np.float64)
    counts[0, 0] = 1000.0
    arrays = l2m.raw_prior_arrays(counts)
    alt = l2m.alt_tables_2m(counts, incumbent_arrays=arrays)
    # FEASIBLE at a generous K2 (ce_alt is small on a concentrated table).
    d1_ok = l2m.feasibility_literals_2m(
        counts, p2_incumbent=np.asarray(arrays["p2"], dtype=np.float64),
        p2_alt=alt["arrays"]["p2_alt"], k2=32768, k_total=32768)
    assert d1_ok["feasible"] is True
    assert d1_ok["alt_feasibility_ceiling_bits"] == 5 * 32768 + 64
    # INFEASIBLE at the L2-only ceiling 5*K2+64 = 64 with any positive CE.
    d1_bad = l2m.feasibility_literals_2m(
        counts, p2_incumbent=np.asarray(arrays["p2"], dtype=np.float64),
        p2_alt=alt["arrays"]["p2_alt"], k2=0, k_total=7020)
    assert d1_bad["feasible"] is False
    assert d1_bad["alt_feasibility_ceiling_bits"] == 64
    assert d1_bad["alt_ideal_length_bits"] > 64.0
    assert d1_bad["ce_alt_insample_bits_per_symbol"] > 0.0


# ---- gate refusals: source / exclusion / prior / alt / order ----

def test_source_and_exclusion_gate_refusals():
    assert_raises_match(ValueError, "1M full-pool path refused",
                        l2m.verify_dev_source_identity_2m,
                        l2m.REFUSED_1M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "1.5M session path refused",
                        l2m.verify_dev_source_identity_2m,
                        l2m.REFUSED_1P5M_DEV_PAIRS_PATH)
    assert_raises_match(ValueError, "dev-pairs=",
                        l2m.verify_dev_source_identity_2m, "elsewhere/pairs.parquet")
    assert l2m.verify_dev_source_identity_2m()["verified"] is True
    assert_raises_match(ValueError, "BLOCKED(dev_block_range_identity)",
                        l2m.verify_val_containment, (2187, 2825))
    assert_raises_match(ValueError, "BLOCKED(dev_block_range_identity)",
                        l2m.verify_val_containment, (2187, 2826), (2827, 2916))
    assert_raises_match(ValueError, "2M VAL",
                        l2m.verify_val_containment, (3000, 3001))
    assert_raises_match(ValueError, "lies outside 2M VAL",
                        l2m.verify_val_containment, (2916, 2917))
    assert_raises_match(ValueError, "overlaps consumed 2M TRAIN",
                        l2m.verify_consumed_exclusions_2m, (0, 1000))
    assert l2m.verify_consumed_exclusions_2m()["verified"] is True
    assert l2m.verify_consumed_exclusions_2m()["build_frames"] == [0, 2186]
    # Manifest identity refusals on an injected (non-real) manifest fixture.
    with p20o_root() as root:
        doc = json.loads(Path(l2m.FROZEN_MANIFEST_PATH).read_text(encoding="utf-8"))
        assert doc["schema"] == l2m.FROZEN_MANIFEST_SCHEMA
        tampered = json.loads(json.dumps(doc))
        tampered["per_source"][l2m.FROZEN_SOURCE_TAG]["pairs"]["train"] = 1
        bad = root / "manifest.json"
        bad.write_text(json.dumps(tampered), encoding="utf-8")
        assert_raises_match(ValueError, "2M TRAIN population",
                            l2m.verify_dev_manifest_2m, bad)
        bad_schema = root / "bad_schema.json"
        bad_schema.write_text(json.dumps({"schema": "wrong"}), encoding="utf-8")
        assert_raises_match(ValueError, "schema",
                            l2m.verify_dev_manifest_2m, bad_schema)
        assert_raises_match(FileNotFoundError, "split manifest not found",
                            l2m.verify_dev_manifest_2m, root / "nope.json")


def test_session_prior_gate_refusals():
    counts = sparse_counts(TEST_SEEDS[0])
    arrays = l2m.raw_prior_arrays(counts)
    digest = psc.canonical_prior_digest(arrays)
    h1 = float(np.asarray(arrays["h1"]))
    h2 = float(np.asarray(arrays["h2"]))
    total = h1 + h2
    ok = l2m.verify_session_prior_2m(
        arrays, expected_digest=digest, expected_h1=h1, expected_h2=h2,
        expected_total=total)
    assert ok["passed"] is True
    assert ok["counts_total"] == int(round(float(counts.sum())))
    assert_raises_match(ValueError, "session_prior_identity",
                        l2m.verify_session_prior_2m, arrays,
                        expected_digest="0" * 64, expected_h1=h1,
                        expected_h2=h2, expected_total=total)
    assert_raises_match(ValueError, "session_prior_identity",
                        l2m.verify_session_prior_2m, arrays,
                        expected_digest=digest, expected_h1=h1 + 1e-3,
                        expected_h2=h2, expected_total=total)
    for field, value in (("lambda_star", 1.0), ("floor_value", 1e-9)):
        tampered = dict(arrays)
        tampered[field] = np.asarray(value, dtype=np.float64)
        assert_raises_match(
            ValueError, "session_prior_identity", l2m.verify_session_prior_2m,
            tampered, expected_digest=psc.canonical_prior_digest(tampered),
            expected_h1=h1, expected_h2=h2, expected_total=total)
    missing = {k: v for k, v in arrays.items() if k != "h1"}
    assert_raises_match(ValueError, "session_prior_identity",
                        l2m.verify_session_prior_2m, missing,
                        expected_digest=digest, expected_h1=h1,
                        expected_h2=h2, expected_total=total)


def test_alt_identity_gate_refusals():
    counts = sparse_counts(TEST_SEEDS[5])
    arrays = l2m.raw_prior_arrays(counts)
    total = int(round(float(counts.sum())))
    with p20o_root() as root:
        result = derive_stub(root, counts=counts)
        path = Path(result["alt_path"])
        with np.load(path, allow_pickle=False) as data:
            alt_arrays = {str(k): np.asarray(data[k]) for k in data.files}
        with patched(l2m, "FROZEN_ALT_DIGEST", result["alt_digest"]), \
                patched(l2m, "FROZEN_MANIFEST_TRAIN_PAIRS", total), \
                patched(l2m, "FROZEN_ALT_H1_INC", result["alt_h1_inc"]):
            verified = l2m.verify_alt_l2_identity_2m(
                path, expected_digest=result["alt_digest"],
                incumbent_arrays=arrays)
            assert verified["passed"] is True
            assert verified["p1_equality_max_abs_diff"] <= 1e-12
            assert str(verified["file_digest"]) == result["alt_digest"]
            assert_raises_match(ValueError, "alt-digest",
                                l2m.verify_alt_l2_identity_2m, path,
                                expected_digest="0" * 64, incumbent_arrays=arrays)
        with patched(l2m, "FROZEN_ALT_DIGEST", "f" * 64):
            assert_raises_match(ValueError, "alt-table bytes sha256",
                                l2m.verify_alt_l2_identity_2m, path,
                                expected_digest="f" * 64, incumbent_arrays=arrays)
        with patched(l2m, "FROZEN_ALT_DIGEST", None):
            assert_raises_match(ValueError, "Stage-A freeze not yet applied",
                                l2m._check_alt_digest, result["alt_digest"])
        # alpha tamper
        tampered = dict(alt_arrays)
        tampered["alpha"] = np.asarray(0.5, dtype=np.float64)
        buf = io.BytesIO()
        np.savez(buf, **tampered)
        bad = root / "alpha_tamper.npz"
        bad.write_bytes(buf.getvalue())
        with patched(l2m, "FROZEN_ALT_DIGEST",
                     hashlib.sha256(bad.read_bytes()).hexdigest()), \
                patched(l2m, "FROZEN_MANIFEST_TRAIN_PAIRS", total):
            assert_raises_match(ValueError, "alpha_pin",
                                l2m.verify_alt_l2_identity_2m, bad,
                                expected_digest=l2m.FROZEN_ALT_DIGEST,
                                incumbent_arrays=arrays)
        # p1 tamper
        tampered = dict(alt_arrays)
        tampered["p1"] = np.zeros((32, 1024), dtype=np.float64)
        buf = io.BytesIO()
        np.savez(buf, **tampered)
        bad = root / "p1_tamper.npz"
        bad.write_bytes(buf.getvalue())
        with patched(l2m, "FROZEN_ALT_DIGEST",
                     hashlib.sha256(bad.read_bytes()).hexdigest()), \
                patched(l2m, "FROZEN_MANIFEST_TRAIN_PAIRS", total):
            assert_raises_match(ValueError, "p1_equality",
                                l2m.verify_alt_l2_identity_2m, bad,
                                expected_digest=l2m.FROZEN_ALT_DIGEST,
                                incumbent_arrays=arrays)
        # key-set tamper
        tampered = dict(alt_arrays)
        tampered.pop("f_alt")
        buf = io.BytesIO()
        np.savez(buf, **tampered)
        bad = root / "keys_tamper.npz"
        bad.write_bytes(buf.getvalue())
        with patched(l2m, "FROZEN_ALT_DIGEST",
                     hashlib.sha256(bad.read_bytes()).hexdigest()), \
                patched(l2m, "FROZEN_MANIFEST_TRAIN_PAIRS", total):
            assert_raises_match(ValueError, "keys must be exactly",
                                l2m.verify_alt_l2_identity_2m, bad,
                                expected_digest=l2m.FROZEN_ALT_DIGEST,
                                incumbent_arrays=arrays)


# ---- §7 instrumentation: presence, nullability, exact formulas ----

def test_instrumentation_fields_nullability_and_formulas():
    counts, p2, view, order, field = tiny_hazard_fixture()
    n = int(view["bob"].size)
    prefix = order[:TEST_K2]
    diag = recorder(view, p2, counts, order,
                    {"first_error_layer": "L1", "first_error_coord": 9})
    assert set(diag) == set(l2m.HAZARD_FIELDS)
    assert diag["l2_order_digest"] == TEST_ORDER_DIGEST
    assert diag["l2_prefix_len"] == TEST_K2
    assert diag["l2_prefix_hazard_mean_bits"] is not None
    assert diag["l2_prefix_floor_frac"] is not None
    for field_name in ("l2_fail_in_prefix", "l2_fail_hazard_bits",
                       "l2_fail_nbhd_mean_bits", "l2_fail_nbhd_floor_frac",
                       "l2_fail_in_prefix_u_domain"):
        assert diag[field_name] is None, field_name
    want_mean = float(np.mean(-np.log2(
        p2[view["high"][prefix], view["bob"][prefix], view["low"][prefix]])))
    assert abs(diag["l2_prefix_hazard_mean_bits"] - want_mean) <= 1e-12
    pos = int(prefix[42])
    low_hat_mismatch = np.asarray(view["low"]).copy()
    low_hat_mismatch[0] ^= 1
    diag2 = recorder(view, p2, counts, order,
                     {"first_error_layer": "L2", "first_error_coord": pos},
                     field=field, low_hat=low_hat_mismatch)
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    assert diag2["l2_fail_in_prefix"] is bool(mask[pos])
    assert abs(diag2["l2_fail_hazard_bits"]
               - float(-np.log2(p2[view["high"][pos], view["bob"][pos],
                                    view["low"][pos]]))) <= 1e-12
    window = np.arange(max(0, pos - 8), min(n - 1, pos + 8) + 1)
    want_nbhd = float(np.mean(-np.log2(
        p2[view["high"][window], view["bob"][window], view["low"][window]])))
    assert abs(diag2["l2_fail_nbhd_mean_bits"] - want_nbhd) <= 1e-12
    assert diag2["l2_fail_nbhd_floor_frac"] is not None
    # ninth scalar: U-domain first-mismatch membership, exact.
    u2_true = view["u2"]
    assert diag2["l2_fail_in_prefix_u_domain"] is bool(
        mask[int(np.flatnonzero(polar_transform(
            low_hat_mismatch, field=field, alpha=2) != u2_true)[0])])
    # The U-domain first mismatch of a single-coordinate flip is index 0 on
    # this transform (u0 depends on every natural coordinate), so both
    # membership outcomes are crafted via the order prefix: index 0 first
    # (in prefix -> True) vs index 0 last (out of prefix -> False).
    flip_hat = np.asarray(view["low"]).copy()
    flip_hat[0] ^= 1
    first_flip = int(np.flatnonzero(
        polar_transform(flip_hat, field=field, alpha=2) != u2_true)[0])
    assert first_flip == 0
    order_true = np.concatenate([[0], order[order != 0]]).astype(np.int64)
    order_false = np.concatenate([order[order != 0], [0]]).astype(np.int64)
    got_true = recorder(view, p2, counts, order_true,
                        {"first_error_layer": "L2", "first_error_coord": 0},
                        field=field, low_hat=flip_hat)
    got_false = recorder(view, p2, counts, order_false,
                         {"first_error_layer": "L2", "first_error_coord": 0},
                         field=field, low_hat=flip_hat)
    assert got_true["l2_fail_in_prefix_u_domain"] is True
    assert got_false["l2_fail_in_prefix_u_domain"] is False
    # the gated prefix length refuses anything else.
    with patched(l2m, "FROZEN_K2", TEST_K2), \
            patched(l2m, "FROZEN_ORDER_DIGEST", TEST_ORDER_DIGEST):
        assert_raises_match(ValueError, "gated prefix length",
                            l2m._l2_hazard_diagnostics, block={}, view=view,
                            p2_arm=p2, counts_arr=counts, l2_order=order,
                            k2=TEST_K2 - 1,
                            first_error={"first_error_layer": None,
                                         "first_error_coord": None})
        # an L2 failure without the field/low_hat seam refuses (never a silent null).
        assert_raises_match(ValueError, "U-domain cross-check requires",
                            l2m._l2_hazard_diagnostics, block={}, view=view,
                            p2_arm=p2, counts_arr=counts, l2_order=order,
                            k2=TEST_K2,
                            first_error={"first_error_layer": "L2",
                                         "first_error_coord": pos})
    # exact formulas do not mutate their inputs.
    snapshot = {k: np.array(view[k], copy=True)
                for k in ("bob", "high", "low", "u2", "u1_cond")}
    p2_snapshot = np.array(p2, copy=True)
    low_hat_snapshot = np.array(view["low"], copy=True)
    recorder(view, p2, counts, order,
             {"first_error_layer": "L2", "first_error_coord": pos},
             field=field, low_hat=low_hat_mismatch)
    for key, before in snapshot.items():
        assert np.array_equal(before, view[key]), key
    assert np.array_equal(p2_snapshot, p2)
    assert np.array_equal(low_hat_snapshot, view["low"])


def test_truth_isolation_recording_only(monkeypatch):
    counts = sparse_counts(TEST_SEEDS[6])
    arrays = l2m.raw_prior_arrays(counts)
    p2 = np.asarray(arrays["p2"], dtype=np.float64)
    p1 = np.asarray(arrays["p1"], dtype=np.float64)
    rng = np.random.default_rng(TEST_SEEDS[6])
    n = 64
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    block = {"block_index": 0, "frame_start": 2187, "frame_end": 2187,
             "high": high, "low": low, "bob": bob}
    view = {"bob": bob, "high": high, "low": low,
            "u2": np.zeros(n, dtype=np.int64)}
    result = opf.OperationalBlockResult(
        stream_seed=2187, block_index=0, outcome="exact", exact=True,
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

    def hostile_recorder(**kwargs):
        calls.append(dict(kwargs))
        # a recording-only call cannot feed anything back: poison the truth
        # it received after the decode has already completed.
        kwargs["view"]["low"][:] = (kwargs["view"]["low"] + 7) % 32
        return {field: "sentinel" for field in l2m.HAZARD_FIELDS}

    monkeypatch.setattr(l2m, "_l2_hazard_diagnostics", hostile_recorder)
    record = l2m._operational_record(
        result, spec=l2m.ArmSpec(
            "A_incumbent_L2_operational", "operational", 331, 6689,
            5 * 7020 + 64, l2m.OPERATIONAL_PROVENANCE, "incumbent"),
        arm_index=0, block=block,
        scoring=p20m._scoring_absent(), resources={},
        k_total=7020, budget_literal="test-budget-literal",
        prior_digest="0" * 64, alt_digest="0" * 64,
        order_digest="0" * 64, counts_arr=counts, p1=p1, p2=p2,
        l2_order=np.arange(n, dtype=np.int64), n=n, view=view, field=None)
    assert len(calls) == 1
    # the recorder is called post-decode with the hard-L1 candidate as U1_cond
    # on the operational arms, and its outputs land in the record fields only.
    assert calls[0]["view"]["u1_cond"] is result.high_hat
    assert record["l2_fail_hazard_bits"] == "sentinel"
    assert record["l2_prefix_floor_frac"] == "sentinel"
    assert record["l2_fail_in_prefix_u_domain"] == "sentinel"
    # decode-derived fields are exactly the pre-record result, untouched by the
    # post-decode truth mutation.
    assert record["outcome"] == "exact" and record["exact"] is True
    assert record["l1_exact"] is True and record["hard_l2_exact"] is True
    assert record["tag_pass"] is True and record["pair_exact"] is True
    assert record["first_error_layer"] is None
    assert record["first_error_coord"] is None
    assert record["arm"] == "A_incumbent_L2_operational"
    assert record["l2_construction"] == "incumbent"
    assert record["key_bit_delta_vs_control"] == 0


# ---- 2M VAL population + gate family (b)-(e) ----

def test_val_population_and_gate_family():
    table = val_table()
    formation = l2m.form_val_blocks(table)
    assert formation["dev_frame_range"] == [2187, 2826]
    assert formation["dev_frames"] == 640
    assert formation["dev_pairs"] == 163840
    assert [tuple(r) for r in formation["block_ranges"]] == list(l2m.FROZEN_BLOCK_RANGES)
    assert len(formation["blocks"]) == 5
    for block in formation["blocks"]:
        assert block["labels"].size == 32768
        assert int(block["high"].max()) < 32 and int(block["low"].max()) < 32
    assert formation["remainder"] == {
        "frame_start": 2827, "frame_end": 2915, "frames": 89,
        "symbols": 22784, "used": False}
    assert l2m.verify_val_containment()["verified"] is True
    assert l2m.verify_consumed_exclusions_2m()["verified"] is True
    assert l2m.verify_consumed_exclusions_2m()["build_frames"] == [0, 2186]
    # declared-range refusals refuse before any content open
    assert_raises_match(ValueError, "dev-frames",
                        l2m.form_val_blocks, table, dev_frames=(2187, 2825))
    assert_raises_match(ValueError, "remainder-frames",
                        l2m.form_val_blocks, table, remainder_frames=(2827, 2916))
    assert_raises_match(ValueError, "BLOCKED(dev_block_range_identity)",
                        l2m.verify_val_containment, (2187, 2825))
    assert_raises_match(ValueError, "lies outside 2M VAL",
                        l2m.verify_val_containment, (3000, 3001))
    assert_raises_match(ValueError, "consumed 2M TRAIN",
                        l2m.verify_consumed_exclusions_2m, (0, 1000))
    assert_raises_match(ValueError, "2M HOLD",
                        l2m.verify_consumed_exclusions_2m, (2187, 2826), (2916, 2917))
    # malformed population refuses inside the formation
    bad = table.copy()
    bad.loc[bad.index[0], "bob_symbol"] = 1024
    assert_raises_match(ValueError, "dev_population_exact",
                        l2m.form_val_blocks, bad)
    bad2 = table.copy()
    bad2 = bad2[bad2["frame_id"] != 2187]
    assert_raises_match(ValueError, "dev_population_exact",
                        l2m.form_val_blocks, bad2)


# ---- order-file gate ----

def _order_doc(*, prior_digest="a" * 64, k1=1000, k2=6000, n=32768,
               seeds=None, blocks_used=16, program=None):
    rng = np.random.default_rng(TEST_SEEDS[0])
    l1 = rng.permutation(n).astype(np.int64)
    l2 = rng.permutation(n).astype(np.int64)
    return {
        "protocol": l2m.PROTOCOL_NAME,
        "kind": "raw-prior-orders-file",
        "n": int(n),
        "k_total": int(k1 + k2),
        "k1": int(k1),
        "k2": int(k2),
        "l1_order": [int(v) for v in l1.tolist()],
        "l2_order": [int(v) for v in l2.tolist()],
        "derivation": {
            "program": l2m.FROZEN_ORDER_PROGRAM_PIN if program is None else program,
            "prior_digest": prior_digest,
            "train_seeds": [int(s) for s in (
                l2m.FROZEN_DERIVATION_SEEDS if seeds is None else seeds)],
            "train_blocks_used": int(blocks_used),
        },
    }


def test_order_file_gate_positive_and_refusals():
    with p20o_root() as root:
        path = root / "orders.json"
        path.write_text(json.dumps(_order_doc(), sort_keys=True) + "\n",
                        encoding="utf-8")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        with patched(l2m, "FROZEN_ORDER_DIGEST", digest):
            verified = l2m.verify_stage_b_order_file_2m(
                path, expected_digest=digest, expected_prior_digest="a" * 64,
                expected_k1=1000, expected_k2=6000, expected_k_total=7000)
            assert verified["verified"] is True
            assert verified["order_digest"] == digest
            assert_raises_match(ValueError, "order-file digest flag",
                                l2m.verify_stage_b_order_file_2m, path,
                                expected_digest="0" * 64,
                                expected_prior_digest="a" * 64,
                                expected_k1=1000, expected_k2=6000, expected_k_total=7000)
            assert_raises_match(ValueError, "k_total",
                                l2m.verify_stage_b_order_file_2m, path,
                                expected_digest=digest,
                                expected_prior_digest="a" * 64,
                                expected_k1=1001, expected_k2=6000, expected_k_total=7001)
        with patched(l2m, "FROZEN_ORDER_DIGEST", "b" * 64):
            assert_raises_match(ValueError, "order-file bytes sha256",
                                l2m.verify_stage_b_order_file_2m, path,
                                expected_digest="b" * 64,
                                expected_prior_digest="a" * 64,
                                expected_k1=1000, expected_k2=6000, expected_k_total=7000)
        # tampered provenance / permutation refusals (file digest re-pinned).
        for mutate, substr in (
                (lambda d: d["derivation"].__setitem__("prior_digest", "c" * 64),
                 "prior digest"),
                (lambda d: d["l1_order"].__setitem__(0, d["l1_order"][1]),
                 "not a permutation"),
                (lambda d: d["derivation"].__setitem__("train_seeds", [1, 2, 3, 4]),
                 "TRAIN seeds"),
                (lambda d: d.__setitem__("protocol", "other"),
                 "protocol"),
                (lambda d: d["derivation"].__setitem__("train_blocks_used", 15),
                 "block count")):
            doc = _order_doc()
            mutate(doc)
            bad = root / "bad.json"
            bad.write_text(json.dumps(doc, sort_keys=True) + "\n", encoding="utf-8")
            with patched(l2m, "FROZEN_ORDER_DIGEST",
                         hashlib.sha256(bad.read_bytes()).hexdigest()):
                assert_raises_match(
                    ValueError, substr, l2m.verify_stage_b_order_file_2m, bad,
                    expected_digest=l2m.FROZEN_ORDER_DIGEST,
                    expected_prior_digest="a" * 64, expected_k1=1000,
                    expected_k2=6000, expected_k_total=7000)


# ---- no Stage-B root + zero protected opens + zero Stage-B sampling ----

def test_no_stage_b_root_and_no_protected_opens_in_stage_a():
    counts = sparse_counts(TEST_SEEDS[0])
    with p20o_root() as root:
        result = derive_stub(root, counts=counts)
        assert result["counts_content_opens"] == 1
        assert result["protected_content_opens"] == 1
        assert result["decoder_calls"] == 0
        assert result["train_genie_calls"] == 32
        assert not Path(l2m.FROZEN_OUT_ROOT).exists()
        assert Path(l2m.FROZEN_OUT_ROOT).name == "l2_alt_maintain_2m"
    assert l2m._DEV_PARQUET_CONTENT_OPENED is False
    assert l2m._ALT_CONTENT_LOADED is False
    assert l2m._SESSION_PRIOR_CONTENT_LOADED is False
    source = Path(l2m.__file__).read_text(encoding="utf-8")
    for token in ("load_v25_channel_counts", "smooth_joint_to_conditional",
                  "LAMBDA_STAR", "137.3823795883264"):
        assert token not in source, token
    for token in ("_l2_hazard_diagnostics", "session_prior_identity",
                  "alt_l2_identity", "l2_fail_in_prefix_u_domain",
                  "l2_fail_nbhd_floor_frac", "A_incumbent_L2_operational",
                  "B_alt_L2_operational", "C_incumbent_L2_oracle", "D_alt_L2_oracle",
                  "2026092310", "nbpolar-p20o-maintain-2m-seed",
                  "from . import raw_prior_val_1p5m", "run_derive_stage_a",
                  "verify_dev_source_identity_2m", "verify_dev_manifest_2m",
                  "k_literal_exact", "alt_construction_budget_feasibility",
                  "TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE"):
        assert token in source, token


def test_zero_stage_b_sampling_pin():
    parser = l2m.build_parser()
    options = set()
    for action in parser._actions:
        options.update(action.option_strings)
    for forbidden in ("--train-seeds", "--seed", "--sample", "--rng", "--genie",
                      "--deriv-seeds-stage-b"):
        assert forbidden not in options, forbidden
    for name in l2m.STAGE_B_FLAGS:
        assert "seed" not in name and "sample" not in name
    assert "--deriv-seeds" in options  # Stage-A only
    assert "deriv_seeds" in l2m.STAGE_A_ONLY_FLAGS
    assert "seeds" not in l2m.run_l2_alt_maintain_2m.__code__.co_varnames
    source = Path(l2m.__file__).read_text(encoding="utf-8")
    # the one and only sampling mention is the frozen order-program pin text.
    assert source.count("default_rng") == 1
    assert "np.random.default_rng(seed)" in l2m.FROZEN_ORDER_PROGRAM_PIN
    assert source.count("sample_full_block") == 1
    assert "sample_full_block" in l2m.FROZEN_ORDER_PROGRAM_PIN
    assert "select_empirical_split" in l2m.FROZEN_ORDER_PROGRAM_PIN


def test_one_open_guards_refuse_reload():
    counts = sparse_counts(TEST_SEEDS[1])
    with p20o_root() as root:
        fixture = counts_npz(root, counts)
        with restored_guards():
            first = l2m.load_counts_2m(fixture)
            assert first["counts_content_opens"] == 1
            assert first["counts_total"] == int(round(float(counts.sum())))
            assert len(first["array_sha256"]) == 64
            assert first["shape"] == (1024, 1024)
            assert_raises_match(ValueError, "reopen refused",
                                l2m.load_counts_2m, fixture)
            assert l2m._COUNTS_CONTENT_OPENS == 1
        # a missing 2M key refuses without consuming the guard (fresh guards).
        with restored_guards():
            other = root / "other.npz"
            with open(other, "wb") as fh:
                np.savez(fh, **{"not_the_2M_key": counts})
            assert_raises_match(ValueError, "missing the frozen 2M key",
                                l2m.load_counts_2m, other)
            assert l2m._COUNTS_CONTENT_OPENS == 0


# ---- seed-domain grep rule ----

def test_grep_rule_seed_placement():
    master = "2026092310"
    test_seeds = [str(seed) for seed in TEST_SEEDS]
    deriv_seeds = [str(seed) for seed in l2m.FROZEN_DERIVATION_SEEDS]
    module_source = Path(l2m.__file__).read_text(encoding="utf-8")
    test_source = Path(__file__).read_text(encoding="utf-8")
    assert master in module_source
    for seed in test_seeds:
        assert seed in test_source, seed
        assert seed not in module_source, seed
    for seed in deriv_seeds:
        assert seed in module_source, seed
    # the test file may name the derivation seeds (P20O test document is an
    # allowed location); it must not contain any non-frozen seed lists.
    assert "FROZEN_DERIVATION_SEEDS" in test_source
    assert l2m.FROZEN_TAG_MASTER == 2026092310
    assert l2m.FROZEN_TAG_MASTER not in (
        p20m.FROZEN_TAG_MASTER, p20l.FROZEN_TAG_MASTER,
        p20n.FROZEN_TAG_MASTER)
    allowed_prefixes = (
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_maintain_2m.py",
        "comparison_bench/tests/test_nbpolar_l2_alt_maintain_2m.py",
        ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20o/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md",
    )
    for literal in [master] + test_seeds + deriv_seeds:
        for hit in _git_grep_hits(literal):
            assert hit.startswith(allowed_prefixes), (literal, hit)
