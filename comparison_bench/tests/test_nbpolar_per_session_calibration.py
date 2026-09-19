"""Focused Phase 4-P20H per-session TRAIN calibration tests.

Injected/synthetic arrays and temporary roots only. The V25
channel-counts NPZ and every registered pairs parquet (1M, 1.5M, reserved
2M) are NEVER content-opened (the one real-mode test uses a stub loader
returning a synthetic array); the real P16 construction root, the real
split manifest, every real evidence root and the reserved 2M file are
never touched. Focused tests use their own fresh seeds
``2026092221..2026092227`` and never the frozen P20H tag master 2026092220
(nor any earlier frozen master/stream/probe seed) for real scoring.

Every ``test_*`` takes no arguments, uses plain asserts and restores any
monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import json
from pathlib import Path

import numpy as np

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    per_session_calibration as pc,
)

SEED_SMOOTH = 2026092221
SEED_SPARSE = 2026092222
SEED_FALLBACK = 2026092223
SEED_DIGEST = 2026092224
SEED_ROUNDTRIP = 2026092225
SEED_OPEN = 2026092226
SEED_FILES = 2026092227

FROZEN_LAMBDA_LITERAL = 137.3823795883264


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
    saved = pc._COUNTS_CONTENT_OPENED
    try:
        yield
    finally:
        pc._COUNTS_CONTENT_OPENED = saved


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def small_counts(seed=SEED_SMOOTH):
    """Tiny dense [Alice,Bob] count matrix for formula-isomorphism checks."""
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 50, size=(8, 5)).astype(np.float64) + 1.0)


def literal_full_pipeline(counts, lam, floor):
    """Independent full-pipeline oracle (no shared helper): §3 program."""
    mat = np.asarray(counts, dtype=np.float64)
    total = mat.sum()
    p_global = mat.sum(axis=1) / total
    n_b = mat.sum(axis=0)
    smooth = np.empty_like(mat)
    for b in range(mat.shape[1]):
        if n_b[b] == 0:
            smooth[:, b] = p_global
        else:
            smooth[:, b] = (mat[:, b] + lam * p_global) / (n_b[b] + lam)
    floored = np.maximum(smooth, floor)
    floored = floored / floored.sum(axis=0, keepdims=True)
    p_b = n_b / total
    # Packing A = 32*U1 + U2: Alice index a = 32*i + j.
    p1 = floored.reshape(32, 32, mat.shape[1]).sum(axis=1)
    joint = floored.reshape(32, 32, mat.shape[1])
    mass = joint.sum(axis=1)
    safe = np.where(mass == 0, 1.0, mass)
    p2 = (joint / safe[:, None, :]).transpose(0, 2, 1)
    p2[mass == 0] = 1.0 / 32
    with np.errstate(divide="ignore"):
        e1 = np.where(p1 > 0, -p1 * np.log2(np.where(p1 > 0, p1, 1.0)), 0.0).sum(axis=0)
        e2 = np.where(p2 > 0, -p2 * np.log2(np.where(p2 > 0, p2, 1.0)), 0.0).sum(axis=2)
    h1 = float(np.sum(p_b * e1))
    h2 = float(np.sum(p_b[None, :] * p1 * e2))
    return smooth, floored, p_b, p1, p2, h1, h2


def sparse_full_counts(seed=SEED_SPARSE):
    """Sparse V25-like 1024x1024 count matrix summing to the TRAIN total."""
    rng = np.random.default_rng(seed)
    counts = np.zeros((1024, 1024), dtype=np.float64)
    cols = np.repeat(np.arange(1024), 2)
    rows = rng.integers(0, 1024, size=2048)
    counts[rows, cols] = rng.integers(1, 500, size=2048)
    # Scale to the frozen 1.5M TRAIN total so the manifest cross-check passes.
    counts = counts / counts.sum() * 424960.0
    return counts


def make_manifest(directory, *, tamper=None):
    frames = {"train": 1660, "val": 553, "hold": 554}
    pairs = {"train": 424960, "val": 141568, "hold": 141824}
    if tamper == "train-pairs":
        pairs = dict(pairs, train=424959)
    doc = {
        "schema": "nbldpc_v25_split_manifest_v1",
        "per_source": {"type2_1p5M_20260121_183806": {"frames": frames, "pairs": pairs}},
    }
    path = Path(directory) / "split_manifest.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


# ---- frozen pins and provenance ----

def test_frozen_lambda_floor_source_pins():
    assert pc.FROZEN_LAMBDA == FROZEN_LAMBDA_LITERAL
    assert pc.FROZEN_FLOOR == 1e-15
    assert pc.FROZEN_SOURCE == "1p5M"
    assert pc.FROZEN_SOURCE_TAG == "type2_1p5M_20260121_183806"
    assert pc.FROZEN_CONDITIONING == "FULL_BOB_ONLY"
    assert pc.NORM_TOL == 1e-12
    assert pc._check_source("1p5M") == "1p5M"
    assert pc._check_lambda(FROZEN_LAMBDA_LITERAL) == FROZEN_LAMBDA_LITERAL
    assert pc._check_floor(1e-15) == 1e-15


def test_lambda_provenance_pin():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        prior_artifact as pa,
    )

    assert float(pa.LAMBDA_STAR) == FROZEN_LAMBDA_LITERAL
    pin = pc.verify_lambda_provenance()
    assert pin["lambda"] == FROZEN_LAMBDA_LITERAL
    assert "D4R2" in pin["provenance"]


def test_source_lambda_floor_refusals():
    assert_raises_match(pc.PerSessionCalibrationError, "source=",
                         pc._check_source, "1M")
    assert_raises_match(pc.PerSessionCalibrationError, "source=",
                         pc._check_source, "2M")
    assert_raises_match(pc.PerSessionCalibrationError, "lambda=",
                         pc._check_lambda, 100.0)
    assert_raises_match(pc.PerSessionCalibrationError, "lambda=",
                         pc._check_lambda, 0.0)
    assert_raises_match(pc.PerSessionCalibrationError, "floor=",
                         pc._check_floor, 1e-12)


def test_banned_twin_and_dev_tokens_absent():
    import inspect

    src = inspect.getsource(pc)
    for token in ("build_f_model(", "load_pairs_table", "normalize_pair_columns",
                  "form_dev_blocks", "dev_table", ".parquet", "pairs_loader"):
        assert token not in src, f"banned token present: {token}"


def test_manifest_pins_equal_runner():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        plus1024_per_session_confirmation as pe,
    )

    assert pc.FROZEN_MANIFEST_TRAIN_FRAMES == pe.FROZEN_MANIFEST_TRAIN_FRAMES == 1660
    assert pc.FROZEN_MANIFEST_TRAIN_PAIRS == pe.FROZEN_MANIFEST_TRAIN_PAIRS == 424960
    assert pc.FROZEN_MANIFEST_VAL_FRAMES == pe.FROZEN_MANIFEST_VAL_FRAMES == 553
    assert pc.FROZEN_MANIFEST_VAL_PAIRS == pe.FROZEN_MANIFEST_VAL_PAIRS == 141568
    assert pc.FROZEN_MANIFEST_HOLD_FRAMES == pe.FROZEN_MANIFEST_HOLD_FRAMES == 554
    assert pc.FROZEN_MANIFEST_HOLD_PAIRS == pe.FROZEN_MANIFEST_HOLD_PAIRS == 141824
    assert pc.FROZEN_MANIFEST_SCHEMA == pe.FROZEN_MANIFEST_SCHEMA
    assert pc.FROZEN_LAMBDA == pe.FROZEN_CALIBRATION_LAMBDA


# ---- program isomorphism ----

def test_smooth_isomorphic_to_literal_formula():
    counts = sparse_full_counts(seed=SEED_SMOOTH)
    cal = pc.calibrate_array(counts)
    smooth, floored, p_b, p1, p2, h1, h2 = literal_full_pipeline(
        counts, FROZEN_LAMBDA_LITERAL, 1e-15)
    assert np.abs(cal["f_smooth"] - smooth).max() <= 1e-12
    assert np.abs(cal["f_prior"] - floored).max() <= 1e-12
    assert np.abs(cal["p1"] - p1).max() <= 1e-12
    assert np.abs(cal["p2"] - p2).max() <= 1e-12
    assert np.abs(cal["p_b"] - p_b).max() <= 1e-12
    assert abs(cal["h1"] - h1) <= 1e-9
    assert abs(cal["h2"] - h2) <= 1e-9
    assert np.abs(cal["f_smooth"].sum(axis=0) - 1.0).max() <= 1e-12
    assert cal["column_dev"] <= 1e-12


def test_unseen_bob_column_falls_back_to_p_global():
    counts = sparse_full_counts(seed=SEED_FALLBACK)
    counts[:, 7] = 0.0  # unseen Bob column
    cal = pc.calibrate_array(counts)
    p_global = counts.sum(axis=1) / counts.sum()
    assert np.abs(cal["f_smooth"][:, 7] - p_global).max() == 0.0


def test_full_pipeline_shapes_positivity_and_literals():
    counts = sparse_full_counts()
    cal = pc.calibrate_array(counts)
    assert cal["f_prior"].shape == (1024, 1024)
    assert cal["p1"].shape == (32, 1024)
    assert cal["p2"].shape == (32, 1024, 32)
    assert cal["p_b"].shape == (1024,)
    assert bool((cal["f_prior"] > 0).all())
    assert bool((cal["p1"] > 0).all())
    assert bool((cal["p2"] > 0).all())
    assert abs(float(cal["p_b"].sum()) - 1.0) <= 1e-12
    for key in ("h1", "h2", "h_total"):
        assert np.isfinite(cal[key]) and cal[key] >= 0.0
    assert abs((cal["h1"] + cal["h2"]) - cal["h_total"]) <= 1e-12
    assert np.isfinite(cal["floor_change"]) and cal["floor_change"] >= 0.0


def test_prior_arrays_and_canonical_digest():
    counts = sparse_full_counts(seed=SEED_DIGEST)
    first = pc.build_prior_arrays(counts)
    second = pc.build_prior_arrays(counts)
    assert set(first) == set(pc.PRIOR_NPZ_KEYS)
    d1 = pc.canonical_prior_digest(first)
    d2 = pc.canonical_prior_digest(second)
    assert len(d1) == 64 and d1 == d2
    perturbed = dict(first)
    bumped = np.array(perturbed["p_b"], copy=True)
    bumped[0] += 1e-6
    perturbed["p_b"] = bumped
    assert pc.canonical_prior_digest(perturbed) != d1


def test_load_prior_roundtrip_and_tamper_refusals(tmp_path):
    counts = sparse_full_counts(seed=SEED_ROUNDTRIP)
    arrays = pc.build_prior_arrays(counts)
    path = tmp_path / "calibrated_prior.npz"
    with open(path, "wb") as fh:
        np.savez(fh, **arrays)
    loaded = pc.load_calibrated_prior(path)
    assert loaded["digest"] == pc.canonical_prior_digest(arrays)
    assert abs(loaded["h_total"] - (loaded["h1"] + loaded["h2"])) <= 1e-12

    def rewrite(mut):
        bad = dict(arrays)
        bad.update(mut)
        with open(path, "wb") as fh:
            np.savez(fh, **bad)

    tampered = np.array(arrays["h1"], copy=True).reshape(())
    rewrite({"h1": tampered + 1e-6})
    assert_raises_match(pc.PerSessionCalibrationError, "h1",
                         pc.load_calibrated_prior, path)
    rewrite({"lambda_star": np.asarray(100.0)})
    assert_raises_match(pc.PerSessionCalibrationError, "lambda",
                         pc.load_calibrated_prior, path)
    slim = {k: v for k, v in arrays.items() if k != "p_b"}
    with open(path, "wb") as fh:
        np.savez(fh, **slim)
    assert_raises_match(pc.PerSessionCalibrationError, "keys",
                         pc.load_calibrated_prior, path)


# ---- guards, manifest gate and file inventory ----

def test_manifest_verify_and_tamper_refusals(tmp_path):
    good = make_manifest(tmp_path)
    manifest = pc.verify_manifest_for_calibration(good, source="1p5M")
    assert manifest["train_pairs"] == 424960
    bad_dir = tmp_path / "sub"
    bad_dir.mkdir(parents=True, exist_ok=True)
    bad = make_manifest(bad_dir, tamper="train-pairs")
    assert_raises_match(pc.PerSessionCalibrationError, "pool",
                         pc.verify_manifest_for_calibration, bad, source="1p5M")
    assert_raises_match(pc.PerSessionCalibrationError, "source=",
                         pc.verify_manifest_for_calibration, good, source="1M")


def test_injected_run_writes_five_files_no_open(tmp_path):
    counts = sparse_full_counts(seed=SEED_FILES)
    man = make_manifest(tmp_path)
    out = tmp_path / "cal"
    with restored_open_guards():
        result = pc.run_per_session_calibration(
            counts=counts, manifest_path=str(man), out_dir=str(out))
    assert pc._COUNTS_CONTENT_OPENED is False
    assert result["counts_content_opens"] == 0
    assert result["counts_total"] == 424960
    assert sorted(p.name for p in out.iterdir()) == sorted(pc.OUTPUT_FILES)
    identity = json.loads((out / "calibration_input_identity.json").read_text())
    assert identity["manifest_cross_check"] is True
    literals = json.loads((out / "recalibrated_literals.json").read_text())
    assert abs((literals["h1"] + literals["h2"]) - literals["h_total"]) <= 1e-12
    assert literals["prior_digest"] == result["digest"]


def test_counts_total_mismatch_is_fail_closed(tmp_path):
    counts = sparse_full_counts() * 2.0  # total 849920 != TRAIN pairs
    man = make_manifest(tmp_path)
    with restored_open_guards():
        assert_raises_match(pc.PerSessionCalibrationError, "counts total",
                             pc.run_per_session_calibration,
                             counts=counts, manifest_path=str(man),
                             out_dir=str(tmp_path / "cal"))


def test_out_dir_refusal_consumes_nothing(tmp_path):
    counts = sparse_full_counts()
    man = make_manifest(tmp_path)
    out = tmp_path / "cal"
    out.mkdir()
    with restored_open_guards():
        assert_raises_match(FileExistsError, "refusing to overwrite",
                             pc.run_per_session_calibration,
                             counts=counts, manifest_path=str(man),
                             out_dir=str(out))
        assert pc._COUNTS_CONTENT_OPENED is False


def test_single_open_guard_with_stub_loader(tmp_path):
    counts = sparse_full_counts(seed=SEED_OPEN)
    man = make_manifest(tmp_path)

    def fake_loader(path):
        return {"1p5M": np.array(counts, copy=True)}

    out_a = tmp_path / "cal_a"
    out_b = tmp_path / "cal_b"
    with restored_open_guards():
        with patched(pc, "load_v25_channel_counts", fake_loader):
            first = pc.run_per_session_calibration(
                manifest_path=str(man), out_dir=str(out_a))
            assert first["counts_content_opens"] == 1
            assert pc._COUNTS_CONTENT_OPENED is True
            assert_raises_match(pc.PerSessionCalibrationError, "reopen refused",
                                 pc.run_per_session_calibration,
                                 manifest_path=str(man), out_dir=str(out_b))
    assert pc._COUNTS_CONTENT_OPENED is False


def test_cli_parser_pins_and_refusals():
    parser = pc.build_parser()
    args = parser.parse_args([
        "--counts", "c.npz", "--source", "1p5M",
        "--lambda", repr(FROZEN_LAMBDA_LITERAL), "--floor", "1e-15",
        "--manifest", "m.json", "--out-dir", "o",
    ])
    assert args.lambda_ == FROZEN_LAMBDA_LITERAL
    assert pc.main(["--counts", "c.npz", "--source", "1M",
                    "--lambda", repr(FROZEN_LAMBDA_LITERAL), "--floor", "1e-15",
                    "--manifest", "m.json", "--out-dir", "o"]) == 2
    assert pc.main(["--counts", "c.npz", "--source", "1p5M",
                    "--lambda", "100.0", "--floor", "1e-15",
                    "--manifest", "m.json", "--out-dir", "o"]) == 2


def test_zero_protected_opens_audit():
    assert pc._COUNTS_CONTENT_OPENED is False
