"""Focused Phase 4-P20N fixed-disclosure ALT-L2 construction tests.

Injected/synthetic counts, priors, artifacts and fresh additive
``workspace/p20n/<uuid>/`` temp roots only. The V25 channel-counts NPZ, every
registered pairs parquet (1M, 1.5M HOLD/VAL/TRAIN, reserved 2M), the real P16
construction root, the real split manifest, the real P20M worktree products
and every accepted evidence root are NEVER content-opened, statted, or listed
here (the single read-only worktree-npz open happens only in the authorized
Stage-A derivation command, never in tests). Focused tests use their own
fresh seeds ``2026092301..2026092307`` and never the frozen P20N tag master
``2026092300``.

There is no sampling code path in the runner module; tests that need
deterministic fixture bytes use ``np.random.default_rng`` with the fresh
test-local seeds only.
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
    l2_alt_hold_1p5m as l2h,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    raw_prior_val_1p5m as p20m,
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
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import derive_p2
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never the frozen P20N tag master 2026092300.
TEST_SEEDS = (2026092301, 2026092302, 2026092303, 2026092304,
              2026092305, 2026092306, 2026092307)

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
    """Derivation tests consume one-open guards; restore them afterwards."""
    state = (
        l2h._INCUMBENT_CONTENT_OPENED, l2h._INCUMBENT_CONTENT_OPENS,
        l2h._ALT_CONTENT_OPENED, l2h._ALT_CONTENT_OPENS,
        l2h._DEV_PARQUET_CONTENT_OPENED,
        l2h._INCUMBENT_CONTENT_LOADED, l2h._ALT_CONTENT_LOADED,
    )
    try:
        yield
    finally:
        (l2h._INCUMBENT_CONTENT_OPENED, l2h._INCUMBENT_CONTENT_OPENS,
         l2h._ALT_CONTENT_OPENED, l2h._ALT_CONTENT_OPENS,
         l2h._DEV_PARQUET_CONTENT_OPENED,
         l2h._INCUMBENT_CONTENT_LOADED, l2h._ALT_CONTENT_LOADED) = state


@contextlib.contextmanager
def p20n_root():
    """Fresh additive workspace/p20n/<uuid>/ temp root, cleaned afterwards."""
    root = REPO_ROOT / "workspace" / "p20n" / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    assert "workspace" in root.parts and "p20n" in root.parts
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


def prior_arrays(counts: np.ndarray) -> dict:
    """Synthetic incumbent-shaped prior via the accepted raw rule (no lambda)."""
    return dict(p20m.build_raw_prior_arrays(counts))


def stub_npz(directory, arrays: dict, name: str = "p20m_stub.npz"):
    """Fabricate a P20M-shaped worktree npz (never the real P20M product)."""
    path = Path(directory) / name
    with open(path, "wb") as fh:
        np.savez(fh, **{k: arrays[k] for k in p20m.RAW_PRIOR_NPZ_KEYS})
    return path, psc.canonical_prior_digest(arrays)


def derive_stub_alt(root, arrays: dict, *, counts_total: int, name: str = "alt.npz"):
    """Run the Stage-A derivation on a synthetic stub behind patched pins."""
    stub_path, stub_digest = stub_npz(root, arrays, name="stub.npz")
    with restored_guards(), patched(l2h, "FROZEN_INCUMBENT_DIGEST", stub_digest):
        return l2h.run_derive_stage_a(
            prior_path=stub_path, prior_digest=stub_digest, alpha=1, floor=1e-15,
            out_path=Path(root) / name, expected_counts_total=int(counts_total))


def hold_table(*, seed: int = TEST_SEEDS[2]) -> pd.DataFrame:
    """HOLD-like pairs frame: 512 DEV frames 2213..2724 + 42-frame remainder."""
    rng = np.random.default_rng(int(seed))
    frames = np.repeat(np.arange(2213, 2725), 256)
    pair_idx = np.tile(np.arange(256), 512)
    dev = pd.DataFrame({
        "frame_id": frames,
        "pair_idx": pair_idx,
        "alice_symbol": rng.integers(0, 1024, size=frames.size),
        "bob_symbol": rng.integers(0, 1024, size=frames.size),
    })
    rem_frames = np.repeat(np.arange(2725, 2767), 256)
    rem = pd.DataFrame({
        "frame_id": rem_frames,
        "pair_idx": np.tile(np.arange(256), 42),
        "alice_symbol": rng.integers(0, 1024, size=rem_frames.size),
        "bob_symbol": rng.integers(0, 1024, size=rem_frames.size),
    })
    # Extra non-HOLD rows must not influence the declared HOLD slicing.
    extra = pd.DataFrame({
        "frame_id": np.repeat([1660, 2044, 0, 1659], 256),
        "pair_idx": np.tile(np.arange(256), 4),
        "alice_symbol": rng.integers(0, 1024, size=4 * 256),
        "bob_symbol": rng.integers(0, 1024, size=4 * 256),
    })
    return pd.concat([dev, rem, extra], ignore_index=True).sample(
        frac=1.0, random_state=int(seed)).reset_index(drop=True)


def tiny_hazard_fixture(*, seed: int = TEST_SEEDS[3], n: int = 6700):
    """Length-n natural-index truth vectors + tables for the §7 recorder."""
    rng = np.random.default_rng(int(seed))
    counts = sparse_counts(seed, cells=1024, hi=20)
    p2 = np.ascontiguousarray(derive_p2(np.ascontiguousarray(l2h.alt_prefloor_table(counts))))
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    order = rng.permutation(n).astype(np.int64)
    view = {"bob": bob, "high": high, "low": low, "u1_cond": high}
    return counts, p2, view, order


def _git_grep_hits(literal: str):
    proc = subprocess.run(
        ["git", "grep", "-l", "--untracked", literal, "--",
         "comparison_bench", "openspec", ".workbuddy", "docs"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1), proc.stderr
    return [line for line in proc.stdout.splitlines() if line.strip()]


# ---- frozen literals, arms, command ----

def test_frozen_literals_arms_and_command():
    assert l2h.FROZEN_K1 == 331 and l2h.FROZEN_K2 == 6689
    assert l2h.FROZEN_K_TOTAL == 7020
    assert l2h.FROZEN_ALT_CEILING_BITS == 33509
    assert l2h.FROZEN_OPERATIONAL_CEILING_BITS == 35164
    assert l2h.FROZEN_HAZARD_R == 8
    assert l2h.FROZEN_DEV_FRAME_RANGE == (2213, 2724)
    assert l2h.FROZEN_BLOCK_RANGES == ((2213, 2340), (2341, 2468),
                                       (2469, 2596), (2597, 2724))
    assert l2h.FROZEN_REMAINDER_FRAME_RANGE == (2725, 2766)
    assert l2h.FROZEN_REMAINDER_FRAMES == 42
    assert l2h.FROZEN_REMAINDER_SYMBOLS == 10752
    assert l2h.PLANNED_SC_CALLS == 24
    assert l2h.PLANNED_TAG_INVOCATIONS == 16
    assert l2h.PLANNED_RECORDS == 16
    assert l2h.FROZEN_TOTAL_KEY_DEPENDENT_BITS == 549384
    assert l2h.FROZEN_TOTAL_PUBLIC_CONTROL_BITS == 5243888
    assert l2h.FROZEN_PUBLIC_CONTROL_BITS == FROZEN_PUBLIC_BITS
    table = l2h.check_frozen_arm_table()
    assert table["a"]["k1"] == table["b"]["k1"] == 331
    assert table["a"]["k2"] == table["b"]["k2"] == 6689
    assert table["a"]["leakage_bits"] == table["b"]["leakage_bits"] == 35164
    assert table["c"]["leakage_bits"] == table["d"]["leakage_bits"] == 33509
    assert table["c"]["k1"] == table["d"]["k1"] == 0
    assert table["c"]["k2"] == table["d"]["k2"] == 6689
    # B-vs-A and D-vs-C key-bit deltas are exactly 0 by construction.
    assert table["b"]["leakage_bits"] - table["a"]["leakage_bits"] == 0
    assert table["d"]["leakage_bits"] - table["c"]["leakage_bits"] == 0
    literal = l2h.check_k_literals(k1=331, k2=6689)
    assert literal["k_total"] == 7020
    assert literal["budget_literal"] == l2h.FROZEN_BUDGET_LITERAL
    assert p20m.budget_literal_display(l2h.FROZEN_H_TOTAL_INC) == l2h.FROZEN_BUDGET_LITERAL
    command = l2h.FROZEN_COMMAND
    for token in ("l2_alt_hold_1p5m", "--prior-digest", "--alt-digest",
                  "--alt-prior", "--source 1p5M", "--floor 1e-15", "--n 32768",
                  "--k1 331 --k2 6689", "--dev-frames 2213 2724",
                  "--block-frames 128", "--remainder-frames 2725 2766",
                  "--tag-master 2026092300", "--chunk-rows 512 --tag-bits 64",
                  "--order-digest", "--out-dir",
                  l2h.FROZEN_INCUMBENT_DIGEST, l2h.FROZEN_ORDER_DIGEST):
        assert token in command, token
    assert l2h.FROZEN_INCUMBENT_DIGEST == p20m.FROZEN_PRIOR_DIGEST
    assert l2h.FROZEN_ORDER_DIGEST == p20m.FROZEN_ORDER_DIGEST
    assert l2h.ALT_L2_NPZ_KEYS == ("counts_ab", "f_alt", "p1", "p2_alt", "alpha",
                                   "floor_value", "h1_inc", "h2_alt", "h_total_alt")


# ---- alt rule vs independent literal ----

def test_alt_rule_vs_independent_literal():
    for seed in TEST_SEEDS:
        counts = sparse_counts(seed)
        arrays = prior_arrays(counts)
        cal = l2h.derive_alt_l2_arrays(
            counts, incumbent_p1=arrays["p1"], incumbent_p_b=arrays["p_b"],
            incumbent_h1=float(arrays["h1"]))
        mat = counts.astype(np.float64)
        n_b = mat.sum(axis=0)
        total = mat.sum()
        p_global = mat.sum(axis=1) / total
        expected = np.empty_like(mat)
        for b in range(1024):
            if n_b[b] == 0:
                expected[:, b] = p_global
            else:
                expected[:, b] = (mat[:, b] + 1.0) / (n_b[b] + 1024.0)
        floor_hits = int(np.sum(expected < l2h.FROZEN_FLOOR))
        floored = np.maximum(expected, l2h.FROZEN_FLOOR)
        floored = floored / floored.sum(axis=0, keepdims=True)
        assert np.abs(cal["f_alt"] - floored).max() <= 1e-12
        assert cal["floor_hits"] == floor_hits
        assert cal["zero_columns"] == int(np.sum(n_b == 0))
        assert float(cal["f_alt"].min()) >= l2h.FROZEN_FLOOR
        assert np.abs(cal["f_alt"].sum(axis=0) - 1.0).max() <= 1e-12
        # p2_alt literal: (C[u1,u2,b] + 1) / (C_u1 + 32).
        cube = mat.reshape(32, 32, 1024)
        slice_totals = cube.sum(axis=1)
        nz = np.argwhere(counts > 0)
        for a, b in nz[:: max(1, nz.shape[0] // 17)]:
            u1, u2 = int(a) >> 5, int(a) & 31
            want = (cube[u1, u2, b] + 1.0) / (slice_totals[u1, b] + 32.0)
            assert abs(float(cal["p2_alt"][u1, b, u2]) - float(want)) <= 1e-12
        # L1 is carried (byte-identical), never re-derived under the alt rule.
        assert np.abs(cal["p1"] - arrays["p1"]).max() <= 1e-12
        assert cal["p1_equality_max_abs_diff"] == 0.0
        assert cal["p1_alt_derived_max_abs_diff"] > 1e-6
        # Descriptive alt-H consistency on (p1_inc, p2_alt).
        assert abs(cal["h_total_alt"] - (cal["h1_inc"] + cal["h2_alt"])) <= 1e-12
        assert cal["h1_inc"] == float(arrays["h1"])


# ---- artifact key set / dtype / alpha / digest ----

def test_derive_artifact_end_to_end():
    counts = sparse_counts(TEST_SEEDS[4])
    arrays = prior_arrays(counts)
    with p20n_root() as root:
        result = derive_stub_alt(root, arrays, counts_total=int(round(counts.sum())))
        out = Path(result["alt_path"])
        payload = out.read_bytes()
        assert result["alt_digest"] == hashlib.sha256(payload).hexdigest()
        with np.load(io.BytesIO(payload), allow_pickle=False) as data:
            assert set(str(k) for k in data.files) == set(l2h.ALT_L2_NPZ_KEYS)
            assert float(np.asarray(data["alpha"])) == 1.0
            assert float(np.asarray(data["floor_value"])) == 1e-15
            assert np.asarray(data["counts_ab"]).dtype == np.float64
            assert np.asarray(data["f_alt"]).dtype == np.float64
            assert np.asarray(data["p1"]).dtype == np.float64
            assert np.asarray(data["p2_alt"]).dtype == np.float64
            assert np.asarray(data["counts_ab"]).shape == (1024, 1024)
            assert np.asarray(data["f_alt"]).shape == (1024, 1024)
            assert np.asarray(data["p1"]).shape == (32, 1024)
            assert np.asarray(data["p2_alt"]).shape == (32, 1024, 32)
        assert result["counts_total"] == int(round(counts.sum()))
        assert result["worktree_npz_content_opens"] == 1
        assert result["sampling_calls"] == 0 and result["genie_calls"] == 0
        assert result["decoder_calls"] == 0 and result["protected_content_opens"] == 0
        # fail-if-present
        with restored_guards(), patched(l2h, "FROZEN_INCUMBENT_DIGEST",
                                        result["incumbent_digest"]):
            assert_raises_match(FileExistsError, "refusing to overwrite",
                                l2h.run_derive_stage_a,
                                prior_path=root / "stub.npz",
                                prior_digest=result["incumbent_digest"], alpha=1,
                                floor=1e-15, out_path=out,
                                expected_counts_total=int(round(counts.sum())))


# ---- digest / alpha / p1 / key-set gate refusals and the positive path ----

def test_alt_identity_gate():
    counts = sparse_counts(TEST_SEEDS[5])
    arrays = prior_arrays(counts)
    with p20n_root() as root:
        result = derive_stub_alt(root, arrays, counts_total=int(round(counts.sum())))
        path = Path(result["alt_path"])
        with patched(l2h, "FROZEN_ALT_DIGEST", result["alt_digest"]), \
                patched(l2h, "FROZEN_MANIFEST_TRAIN_PAIRS", int(round(counts.sum()))), \
                patched(l2h, "FROZEN_H1_INC", float(result["h1_inc"])):
            verified = l2h.verify_alt_l2_identity(
                path, expected_digest=result["alt_digest"], incumbent_arrays=arrays)
            assert verified["passed"] is True
            assert verified["p1_equality_max_abs_diff"] <= 1e-12
            assert str(verified["file_digest"]) == result["alt_digest"]
            # order: pin/flag mismatch refuses first, then bytes-digest mismatch
            assert_raises_match(ValueError, "alt-digest",
                                l2h.verify_alt_l2_identity, path,
                                expected_digest="0" * 64, incumbent_arrays=arrays)
        with patched(l2h, "FROZEN_ALT_DIGEST", "f" * 64):
            assert_raises_match(ValueError, "alt-table bytes sha256",
                                l2h.verify_alt_l2_identity, path,
                                expected_digest="f" * 64, incumbent_arrays=arrays)
        with patched(l2h, "FROZEN_ALT_DIGEST", None):
            assert_raises_match(ValueError, "Stage-A freeze not yet applied",
                                l2h._check_alt_digest, result["alt_digest"])
        # alpha tamper
        with np.load(path, allow_pickle=False) as data:
            tampered = {str(k): np.asarray(data[k]) for k in data.files}
        tampered["alpha"] = np.asarray(0.5, dtype=np.float64)
        bad = root / "alpha_tamper.npz"
        buf = io.BytesIO()
        np.savez(buf, **tampered)
        bad.write_bytes(buf.getvalue())
        with patched(l2h, "FROZEN_ALT_DIGEST", hashlib.sha256(bad.read_bytes()).hexdigest()):
            assert_raises_match(ValueError, "alpha_pin",
                                l2h.verify_alt_l2_identity, bad,
                                expected_digest=l2h.FROZEN_ALT_DIGEST,
                                incumbent_arrays=arrays)
        # p1 tamper
        tampered = dict(l2h_tampered_arrays(path))
        tampered["p1"] = np.zeros((32, 1024), dtype=np.float64)
        bad = root / "p1_tamper.npz"
        buf = io.BytesIO()
        np.savez(buf, **tampered)
        bad.write_bytes(buf.getvalue())
        with patched(l2h, "FROZEN_ALT_DIGEST", hashlib.sha256(bad.read_bytes()).hexdigest()):
            assert_raises_match(ValueError, "p1_equality",
                                l2h.verify_alt_l2_identity, bad,
                                expected_digest=l2h.FROZEN_ALT_DIGEST,
                                incumbent_arrays=arrays)
        # key-set tamper
        tampered = dict(l2h_tampered_arrays(path))
        tampered.pop("f_alt")
        bad = root / "keys_tamper.npz"
        buf = io.BytesIO()
        np.savez(buf, **tampered)
        bad.write_bytes(buf.getvalue())
        with patched(l2h, "FROZEN_ALT_DIGEST", hashlib.sha256(bad.read_bytes()).hexdigest()):
            assert_raises_match(ValueError, "keys must be exactly",
                                l2h.verify_alt_l2_identity, bad,
                                expected_digest=l2h.FROZEN_ALT_DIGEST,
                                incumbent_arrays=arrays)


def l2h_tampered_arrays(path):
    with np.load(path, allow_pickle=False) as data:
        return {str(k): np.asarray(data[k]) for k in data.files}


# ---- D1 estimator exactness + D2 gate both ways ----

def test_d1_estimator_exact_tiny_fixture():
    counts = np.zeros((1024, 1024), dtype=np.float64)
    counts[0, 0] = 5.0           # u1 = 0, u2 = 0
    counts[33, 7] = 3.0          # u1 = 1, u2 = 1
    p2 = np.full((32, 1024, 32), 0.25, dtype=np.float64)
    p2[0, 0, 0] = 0.5
    p2[1, 7, 1] = 0.25
    ce = l2h.in_sample_l2_ce_bits_per_symbol(counts, p2)
    assert abs(ce - 1.375) <= 1e-12
    acc = 0.0
    for a, b in np.argwhere(counts > 0):
        acc += float(counts[a, b]) * (-np.log2(p2[(int(a) >> 5) & 31, int(b),
                                                  int(a) & 31]))
    assert abs(ce - acc / float(counts.sum())) <= 1e-12
    # counted zero-mass cell refuses
    p2_zero = np.array(p2)
    p2_zero[0, 0, 0] = 0.0
    assert_raises_match(ValueError, "zero table mass",
                        l2h.in_sample_l2_ce_bits_per_symbol, counts, p2_zero)


def test_d2_gate_feasible_and_infeasible():
    counts_ok = np.zeros((1024, 1024), dtype=np.float64)
    counts_ok[0, 0] = 1000.0
    arrays_ok = prior_arrays(counts_ok)
    with p20n_root() as root:
        result = derive_stub_alt(root, arrays_ok,
                                 counts_total=int(round(counts_ok.sum())))
        assert result["alt_construction_budget_feasibility"] == "FEASIBLE"
        assert result["d1"]["feasible"] is True
        assert result["d1"]["alt_ideal_length_bits"] <= 33509
        assert result["d1"]["alt_feasibility_ceiling_bits"] == 33509
        assert result["d1"]["operational_ceiling_bits"] == 35164
        assert result["d1"]["counts_total"] == 1000
    counts_bad = np.zeros((1024, 1024), dtype=np.float64)
    counts_bad[0, 0] = 1.0
    arrays_bad = prior_arrays(counts_bad)
    with p20n_root() as root:
        result = derive_stub_alt(root, arrays_bad,
                                 counts_total=int(round(counts_bad.sum())))
        assert result["alt_construction_budget_feasibility"] == \
            "ALT_CONSTRUCTION_BUDGET_INFEASIBLE"
        assert result["d1"]["feasible"] is False
        assert result["d1"]["alt_ideal_length_bits"] > 33509
        # the literals are reported even on the INFEASIBLE branch
        assert result["d1"]["ce_alt_insample_bits_per_symbol"] > 0.0


# ---- mode / missing-flag / K-literal refusals ----

def test_cli_mode_refusals(capsys):
    assert l2h.main([]) == 2
    assert "ambiguous invocation refused" in capsys.readouterr().err
    assert l2h.main(["--derive"]) == 2
    assert "missing required Stage-A flags" in capsys.readouterr().err
    mixed = ["--derive", "--prior", "x", "--prior-digest", "y", "--alpha", "1",
             "--floor", "1e-15", "--out", "z", "--source", "1p5M"]
    assert l2h.main(mixed) == 2
    assert "mixed invocation refused" in capsys.readouterr().err
    assert l2h.main(["--prior", "x"]) == 2
    assert "missing required Stage-B flags" in capsys.readouterr().err
    assert l2h.main(["--alpha", "1"]) == 2
    assert "Stage-A-only flags" in capsys.readouterr().err
    assert l2h.main(["--out", "z"]) == 2
    assert "Stage-A-only flags" in capsys.readouterr().err


def test_k_literal_gate_refusals():
    assert_raises_match(ValueError, "k1=331", l2h.check_k_literals, k1=330, k2=6689)
    assert_raises_match(ValueError, "k2=6689", l2h.check_k_literals, k1=331, k2=6688)
    assert_raises_match(ValueError, "source='1p5M'", l2h._check_source, "1M")
    assert_raises_match(ValueError, "n=32768", l2h._check_n, 1024)
    assert_raises_match(ValueError, "dev-frames", l2h._check_dev_frames, (2213, 2723))
    assert_raises_match(ValueError, "remainder-frames", l2h._check_remainder_frames,
                        (2725, 2767))
    assert_raises_match(ValueError, "tag-master", l2h._check_tag_master, 2026092280)
    assert_raises_match(ValueError, "prior-digest", l2h._check_prior_digest, "0" * 64)
    assert_raises_match(ValueError, "order-digest", l2h._check_order_digest, "0" * 64)
    assert_raises_match(ValueError, "alpha", l2h._check_alpha, 0.5)


# ---- §7 instrumentation: presence, nullability, exact formulas ----

def test_instrumentation_fields_nullability_and_formulas():
    counts, p2, view, order = tiny_hazard_fixture()
    n = int(view["bob"].size)
    diag = l2h._l2_hazard_diagnostics(
        block={}, view=view, p2_arm=p2, counts_arr=counts, l2_order=order,
        k2=6689, first_error={"first_error_layer": "L1", "first_error_coord": 9})
    assert set(diag) == set(l2h.HAZARD_FIELDS)
    assert diag["l2_order_digest"] == l2h.FROZEN_ORDER_DIGEST
    assert diag["l2_prefix_len"] == 6689
    for field in ("l2_fail_in_prefix", "l2_fail_hazard_bits",
                  "l2_fail_nbhd_mean_bits", "l2_fail_nbhd_floor_frac"):
        assert diag[field] is None, field
    assert diag["l2_prefix_hazard_mean_bits"] is not None
    assert diag["l2_prefix_floor_frac"] is not None
    prefix = order[:6689]
    high = view["high"][prefix]
    bob = view["bob"][prefix]
    low = view["low"][prefix]
    want_mean = float(np.mean(-np.log2(p2[high, bob, low])))
    assert abs(diag["l2_prefix_hazard_mean_bits"] - want_mean) <= 1e-12
    pos = 42
    diag2 = l2h._l2_hazard_diagnostics(
        block={}, view=view, p2_arm=p2, counts_arr=counts, l2_order=order,
        k2=6689, first_error={"first_error_layer": "L2", "first_error_coord": pos})
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
    # the gated prefix length refuses anything else
    assert_raises_match(ValueError, "gated prefix length",
                        l2h._l2_hazard_diagnostics, block={}, view=view, p2_arm=p2,
                        counts_arr=counts, l2_order=order, k2=6688,
                        first_error={"first_error_layer": None, "first_error_coord": None})
    # exact formulas do not mutate their inputs
    snapshot = {k: np.array(view[k], copy=True) for k in ("bob", "high", "low", "u1_cond")}
    p2_snapshot = np.array(p2, copy=True)
    l2h._l2_hazard_diagnostics(
        block={}, view=view, p2_arm=p2, counts_arr=counts, l2_order=order, k2=6689,
        first_error={"first_error_layer": "L2", "first_error_coord": pos})
    for key, before in snapshot.items():
        assert np.array_equal(before, view[key]), key
    assert np.array_equal(p2_snapshot, p2)


def test_truth_isolation_recording_only(monkeypatch):
    counts = sparse_counts(TEST_SEEDS[6])
    arrays = prior_arrays(counts)
    p2 = np.asarray(arrays["p2"], dtype=np.float64)
    p1 = np.asarray(arrays["p1"], dtype=np.float64)
    rng = np.random.default_rng(TEST_SEEDS[6])
    n = 64
    bob = rng.integers(0, 1024, size=n)
    high = rng.integers(0, 32, size=n)
    low = rng.integers(0, 32, size=n)
    block = {"block_index": 0, "frame_start": 2213, "frame_end": 2213,
             "high": high, "low": low, "bob": bob}
    view = {"bob": bob, "high": high, "low": low}
    result = opf.OperationalBlockResult(
        stream_seed=2213, block_index=0, outcome="exact", exact=True,
        label_match=True, tag_pass=True, l1_provenance=opf.Provenance.PRIOR_ONLY.value,
        l2_provenance=opf.Provenance.CANDIDATE_CONDITIONED.value, l1_executed=True,
        l1_decode_failed=False, l2_invoked=True, l2_skipped_by_l1_failure=False,
        l2_decode_failed=False, tag_invoked=True, key_dependent_bits=35164,
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
        return {
            "l2_order_digest": l2h.FROZEN_ORDER_DIGEST, "l2_prefix_len": 6689,
            "l2_fail_in_prefix": "sentinel", "l2_fail_hazard_bits": "sentinel",
            "l2_fail_nbhd_mean_bits": "sentinel",
            "l2_prefix_hazard_mean_bits": "sentinel",
            "l2_fail_nbhd_floor_frac": "sentinel", "l2_prefix_floor_frac": "sentinel",
        }

    monkeypatch.setattr(l2h, "_l2_hazard_diagnostics", hostile_recorder)
    record = l2h._operational_record(
        result, spec=l2h.frozen_arm_table()[0], arm_index=0, block=block,
        scoring=p20m._scoring_absent(), resources={},
        k_total=7020, budget_literal=l2h.FROZEN_BUDGET_LITERAL,
        alt_digest="0" * 64, order_digest=l2h.FROZEN_ORDER_DIGEST,
        counts_arr=counts, p1=p1, p2=p2, l2_order=np.arange(n, dtype=np.int64),
        n=n, view=view)
    assert len(calls) == 1
    # the recorder is called post-decode with the hard-L1 candidate as U1_cond
    # on the operational arms, and its outputs land in the record fields only.
    assert calls[0]["view"]["u1_cond"] is result.high_hat
    assert record["l2_fail_hazard_bits"] == "sentinel"
    assert record["l2_prefix_floor_frac"] == "sentinel"
    # decode-derived fields are exactly the pre-record result, untouched by the
    # post-decode truth mutation.
    assert record["outcome"] == "exact" and record["exact"] is True
    assert record["l1_exact"] is True and record["hard_l2_exact"] is True
    assert record["tag_pass"] is True and record["pair_exact"] is True
    assert record["first_error_layer"] is None
    assert record["first_error_coord"] is None
    assert record["arm"] == "A_incumbent_L2_operational"
    assert record["l2_construction"] == "incumbent"


# ---- HOLD population + gate family (b)-(f) ----

def test_hold_population_and_gate_family():
    table = hold_table()
    formation = l2h.form_hold_blocks(table)
    assert formation["dev_frame_range"] == [2213, 2724]
    assert formation["dev_frames"] == 512
    assert formation["dev_pairs"] == 131072
    assert [tuple(r) for r in formation["block_ranges"]] == list(l2h.FROZEN_BLOCK_RANGES)
    assert len(formation["blocks"]) == 4
    for block in formation["blocks"]:
        assert block["labels"].size == 32768
        assert int(block["high"].max()) < 32 and int(block["low"].max()) < 32
    assert formation["remainder"] == {
        "frame_start": 2725, "frame_end": 2766, "frames": 42,
        "symbols": 10752, "used": False}
    assert l2h.verify_hold_containment()["verified"] is True
    assert l2h.verify_consumed_exclusions()["verified"] is True
    assert l2h.verify_consumed_exclusions()["build_frames"] == [0, 1659]
    # declared-range refusals refuse before any content open
    assert_raises_match(ValueError, "dev-frames",
                        l2h.form_hold_blocks, table, dev_frames=(2213, 2723))
    assert_raises_match(ValueError, "remainder-frames",
                        l2h.form_hold_blocks, table, remainder_frames=(2725, 2767))
    assert_raises_match(ValueError, "BLOCKED(dev_block_range_identity)",
                        l2h.verify_hold_containment, (1660, 1787))
    assert_raises_match(ValueError, "0..1659",
                        l2h.verify_consumed_exclusions, (0, 383))
    assert_raises_match(ValueError, "1660..2043",
                        l2h.verify_consumed_exclusions, (1660, 1787))
    assert_raises_match(ValueError, "2044..2212",
                        l2h.verify_consumed_exclusions, (2044, 2212))
    # malformed population refuses inside the formation
    bad = table.copy()
    bad.loc[bad.index[0], "bob_symbol"] = 1024
    assert_raises_match(ValueError, "dev_population_exact",
                        l2h.form_hold_blocks, bad)


# ---- no Stage-B root + zero protected opens + zero sampling ----

def test_no_stage_b_root_and_no_protected_opens_in_stage_a():
    counts = sparse_counts(TEST_SEEDS[0])
    arrays = prior_arrays(counts)
    with p20n_root() as root:
        result = derive_stub_alt(root, arrays, counts_total=int(round(counts.sum())))
        assert result["sampling_calls"] == 0
        assert result["genie_calls"] == 0
        assert result["decoder_calls"] == 0
        assert result["protected_content_opens"] == 0
        assert result["worktree_npz_content_opens"] == 1
        assert not Path(l2h.FROZEN_OUT_ROOT).exists()
        assert Path(l2h.FROZEN_OUT_ROOT).name == "l2_alt_hold_1p5m"
    assert l2h._DEV_PARQUET_CONTENT_OPENED is False
    assert l2h._ALT_CONTENT_LOADED is False
    assert l2h._INCUMBENT_CONTENT_LOADED is False
    source = Path(l2h.__file__).read_text(encoding="utf-8")
    for token in ("load_v25_channel_counts", "FROZEN_COUNTS_PATH", "channel_counts",
                  "smooth_joint_to_conditional", "LAMBDA_STAR", "137.3823795883264",
                  "select_empirical_split", "sample_full_block", "block_genie_risks",
                  "default_rng", "lambda"):
        assert token not in source, token
    for token in ("_l2_hazard_diagnostics", "alt_l2_identity", "l2_prefix_hazard_mean_bits",
                  "l2_fail_nbhd_floor_frac", "A_incumbent_L2_operational",
                  "B_alt_L2_operational", "C_incumbent_L2_oracle", "D_alt_L2_oracle",
                  "2026092300", "nbpolar-p20n-l2-alt-hold-1p5m-seed",
                  "from . import raw_prior_val_1p5m", "verify_dev_source_identity",
                  "verify_dev_manifest", "k_literal_exact", "alt_construction_budget_feasibility"):
        assert token in source, token


def test_zero_sampling_pin_and_no_seed_flags():
    parser = l2h.build_parser()
    options = set()
    for action in parser._actions:
        options.update(action.option_strings)
    for forbidden in ("--train-seeds", "--seed", "--sample", "--rng", "--genie"):
        assert forbidden not in options, forbidden
    assert "--derive" in options and "--alpha" in options and "--out" in options
    for name in l2h.STAGE_B_FLAGS + l2h.STAGE_A_ONLY_FLAGS:
        assert "seed" not in name and "sample" not in name
    source = Path(l2h.__file__).read_text(encoding="utf-8")
    assert "np.random" not in source
    assert "block_genie_risks" not in source
    assert "select_empirical_split" not in source
    assert "sample_full_block" not in source


def test_frozen_stage_b_root_absent_before_authorization():
    # Stage-A invariant: the Stage-B evidence root must be ABSENT (it exists
    # only after an independently authorized Stage-B execution).
    assert not Path(l2h.FROZEN_OUT_ROOT).exists()
    assert l2h.ATTEMPT_CONSUMPTION_POINT.startswith("first protected content open")


# ---- one-open guards refuse reloads ----

def test_one_open_guards_refuse_reload():
    counts = sparse_counts(TEST_SEEDS[1])
    arrays = prior_arrays(counts)
    with p20n_root() as root:
        stub_path, stub_digest = stub_npz(root, arrays)
        with restored_guards(), patched(l2h, "FROZEN_INCUMBENT_DIGEST", stub_digest):
            first = l2h.run_derive_stage_a(
                prior_path=stub_path, prior_digest=stub_digest, alpha=1,
                floor=1e-15, out_path=root / "a.npz",
                expected_counts_total=int(round(counts.sum())))
            assert first["worktree_npz_content_opens"] == 1
            assert_raises_match(ValueError, "reopen refused",
                                l2h.load_incumbent_prior_arrays, stub_path,
                                expected_digest=stub_digest)
            assert_raises_match(FileExistsError, "refusing to overwrite",
                                l2h.run_derive_stage_a, prior_path=stub_path,
                                prior_digest=stub_digest, alpha=1, floor=1e-15,
                                out_path=root / "a.npz",
                                expected_counts_total=int(round(counts.sum())))


# ---- seed-domain grep rule ----

def test_grep_rule_seed_placement():
    master = "2026092300"
    test_seeds = [str(seed) for seed in TEST_SEEDS]
    module_source = Path(l2h.__file__).read_text(encoding="utf-8")
    test_source = Path(__file__).read_text(encoding="utf-8")
    assert master in module_source
    for seed in test_seeds:
        assert seed in test_source, seed
        assert seed not in module_source, seed
    assert l2h.FROZEN_TAG_MASTER == 2026092300
    assert l2h.FROZEN_TAG_MASTER not in (
        p20m.FROZEN_TAG_MASTER, p20l.FROZEN_TAG_MASTER)
    allowed_prefixes = (
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_1p5m.py",
        "comparison_bench/tests/test_nbpolar_l2_alt_hold_1p5m.py",
        ".workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/specs/nbpolar-phase4-p20n/",
        "openspec/changes/formal-ir-nbpolar-phase4-p0/tasks.md",
    )
    for literal in [master] + test_seeds:
        for hit in _git_grep_hits(literal):
            assert hit.startswith(allowed_prefixes), (literal, hit)
