"""NB-Polar Phase 4-P20H per-session TRAIN calibration (Stage A, frozen).

The single deliberate delta vs P20G: the prior is per-session calibrated on
1.5M TRAIN counts by the frozen program below (Stage A, DEV-zero-contact,
read-only in Stage B). Everything else (construction/order/K/caps/floor)
is carried over byte-identical from P20C/P20E/P20F/P20G.

Frozen program = the accepted P0/P2 Model-F concentration fitting program,
isomorphic (same formula / smoothing / flow), new-session input only::

    p_global[a] = sum_b counts[a,b] / sum counts
    n_b[b]      = sum_a counts[a,b]
    f[a,b]      = (counts[a,b] + lambda * p_global[a]) / (n_b[b] + lambda)

Column meaning ``P(A|B)``, shape ``(1024,1024)`` ``[Alice,Bob]``; columns
sum to 1 within 1e-12; unseen-Bob columns fall back to ``p_global``
exactly. The banned per-cell twin (``build_f_model`` with ``counts+lam``)
is never called and never imported. Adapter chain: ``derive_p1`` /
``derive_p2`` under packing ``A = 32*U1 + U2``, joint-Bob conditioning
``FULL_BOB_ONLY``, fixed ``1e-15`` floor before SC, ``SymbolMetric``
log-domain contract. Lambda is the accepted fitting-program constant
``137.3823795883264`` (D4R2 nested-CV refit, carried via
``prior_artifact.LAMBDA_STAR``); no hand-fill, no DEV influence, no
per-session search, no floor search.

Input (sole allowed): 1.5M TRAIN counts ONLY via ``--source 1p5M``. The
module has no DEV/parquet code path at all, so DEV-zero-contact holds by
construction. Output: ``per_session_calibration/`` with the plan, the
input identity, the digest-pinned ``calibrated_prior.npz``, the
recalibrated H1/H2/TOTAL literals and the report. Stage B loads the prior
read-only behind a calibration-identity digest gate and refuses on
mismatch; no refit/resmoothing/relambda after any DEV contact.

Stage A only: this module plus focused injected tests plus the single
declared counts-calibration open. No decoder execution, no Stage-B output
root, no commit or push, no self-acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

from ..v35_algorithm_development import SOURCE_IDS, load_v25_channel_counts
from .prior import derive_p1, derive_p2, smooth_joint_to_conditional
from .prior_artifact import LAMBDA_STAR as ACCEPTED_LAMBDA_STAR
from .target_construction import entropy_bits
from . import holdout_microcheck as hm

PROTOCOL_NAME = "nbpolar-p20h-per-session-calibration"
MODE = "train-calibration-freeze"

FROZEN_SOURCE = "1p5M"
FROZEN_SOURCE_TAG = "type2_1p5M_20260121_183806"
# The accepted fitting-program constant procedure output (Stage-A frozen
# literal + provenance; no hand-fill, no DEV influence, no per-session
# search). Provenance: D4R2 nested-CV refit, carried via
# prior_artifact.LAMBDA_STAR (P0 contract row 1 / prior_artifact).
FROZEN_LAMBDA = 137.3823795883264
LAMBDA_PROVENANCE = (
    "D4R2 nested-CV refit constant carried via "
    "formal_ir.nbpolar.prior_artifact.LAMBDA_STAR; frozen procedure output, "
    "no DEV influence, no per-session search, no floor search"
)
FROZEN_FLOOR = 1e-15
FROZEN_PACKING = "A = 32*U1 + U2 (low = s&31 = U2, high = (s>>5)&31 = U1)"
FROZEN_CONDITIONING = "FULL_BOB_ONLY"
NORM_TOL = 1e-12

# Split-manifest 1.5M TRAIN pool hosting the calibration input (same pins
# as the Stage-B runner; cross-module equality is pinned by test).
FROZEN_MANIFEST_TRAIN_FRAMES = 1660
FROZEN_MANIFEST_TRAIN_PAIRS = 424960
FROZEN_MANIFEST_VAL_FRAMES = 553
FROZEN_MANIFEST_VAL_PAIRS = 141568
FROZEN_MANIFEST_HOLD_FRAMES = 554
FROZEN_MANIFEST_HOLD_PAIRS = 141824

FROZEN_COUNTS_PATH = hm.FROZEN_COUNTS_PATH
FROZEN_MANIFEST_PATH = hm.FROZEN_MANIFEST_PATH
FROZEN_MANIFEST_SCHEMA = hm.FROZEN_MANIFEST_SCHEMA
FROZEN_OUT_DIR = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/"
    "per_session_calibration"
)
NPZ_LOADER_IDENTITY = hm.NPZ_LOADER_IDENTITY

# Exact keys of calibrated_prior.npz (no more, no fewer).
PRIOR_NPZ_KEYS = (
    "counts_ab",
    "f_prior",
    "p1",
    "p2",
    "p_b",
    "lambda_star",
    "floor_value",
    "h1",
    "h2",
    "h_total",
)

OUTPUT_FILES = (
    "calibration_plan.json",
    "calibration_input_identity.json",
    "calibrated_prior.npz",
    "recalibrated_literals.json",
    "calibration_report.md",
)
ATTEMPT_CONSUMPTION_POINT = "first counts-calibration content open (load_v25_channel_counts)"

# Process-level one-open guard: set at the first counts content open, never cleared.
_COUNTS_CONTENT_OPENED = False


class PerSessionCalibrationError(ValueError):
    """Frozen calibration refusal: wrong input, pin mismatch or reopen."""


def _check_source(value) -> str:
    if value != FROZEN_SOURCE:
        raise PerSessionCalibrationError(
            f"frozen calibration requires source={FROZEN_SOURCE!r}, got {value!r}"
        )
    if SOURCE_IDS.get(FROZEN_SOURCE) != FROZEN_SOURCE_TAG:
        raise PerSessionCalibrationError("frozen source-tag vocabulary drifted")
    return FROZEN_SOURCE


def _check_lambda(value) -> float:
    try:
        lam = float(value)
    except (TypeError, ValueError) as exc:
        raise PerSessionCalibrationError(f"lambda must be numeric ({exc})") from exc
    if lam != float(FROZEN_LAMBDA):
        raise PerSessionCalibrationError(
            f"frozen calibration requires lambda={FROZEN_LAMBDA!r}, got {lam!r}"
        )
    return lam


def _check_floor(value) -> float:
    out = hm._check_floor(value)
    if out != FROZEN_FLOOR:
        raise PerSessionCalibrationError(
            f"frozen calibration requires floor={FROZEN_FLOOR}, got {out}"
        )
    return out


def verify_lambda_provenance() -> dict:
    """Pin the frozen lambda literal to its accepted provenance carrier."""
    if float(ACCEPTED_LAMBDA_STAR) != float(FROZEN_LAMBDA):
        raise PerSessionCalibrationError(
            "frozen lambda literal drifted from prior_artifact.LAMBDA_STAR"
        )
    return {"lambda": float(FROZEN_LAMBDA), "provenance": LAMBDA_PROVENANCE}


def calibrate_array(counts, *, lam=FROZEN_LAMBDA, floor=FROZEN_FLOOR) -> dict:
    """Apply the frozen §3 program to a ``[Alice,Bob]`` count matrix.

    Pure function (no I/O): concentration smoothing with the frozen
    lambda, ``1e-15`` floor + column renormalization, accepted
    ``derive_p1``/``derive_p2``, and the floor-table entropy functionals
    (the quantities that drive SC) as the recalibrated literals. The
    unfloored smoothed table's functionals are reported alongside so the
    floor-induced shift stays visible.
    """
    lam = _check_lambda(lam)
    floor = _check_floor(floor)
    verify_lambda_provenance()
    mat = np.asarray(counts, dtype=np.float64)
    if mat.ndim != 2 or mat.shape[0] < 1 or mat.shape[1] < 1:
        raise PerSessionCalibrationError(f"counts must be 2-D non-empty, got {mat.shape}")
    # Accepted concentration formula (P0/P2 isomorphic; banned twin excluded).
    f_smooth = smooth_joint_to_conditional(mat, lam)
    total = float(mat.sum())
    n_b = mat.sum(axis=0)
    p_b = n_b / total
    # Floor application isomorphic to build_target_conditional: per-cell
    # floor on the conditional, then column renormalization.
    f_prior = np.maximum(f_smooth, floor)
    f_prior = f_prior / f_prior.sum(axis=0, keepdims=True)
    p1 = derive_p1(np.ascontiguousarray(f_prior))
    p2 = derive_p2(np.ascontiguousarray(f_prior))
    h1 = float(np.sum(p_b * entropy_bits(p1, axis=0)))
    h2 = float(np.sum(p_b[None, :] * p1 * entropy_bits(p2, axis=2)))
    h_total = h1 + h2
    raw_p1 = derive_p1(np.ascontiguousarray(f_smooth))
    raw_p2 = derive_p2(np.ascontiguousarray(f_smooth))
    uh1 = float(np.sum(p_b * entropy_bits(raw_p1, axis=0)))
    uh2 = float(np.sum(p_b[None, :] * raw_p1 * entropy_bits(raw_p2, axis=2)))
    column_dev = float(np.abs(f_prior.sum(axis=0) - 1.0).max())
    return {
        "f_smooth": np.ascontiguousarray(f_smooth),
        "f_prior": np.ascontiguousarray(f_prior),
        "p1": np.ascontiguousarray(p1),
        "p2": np.ascontiguousarray(p2),
        "p_b": np.ascontiguousarray(p_b),
        "column_totals": np.ascontiguousarray(n_b),
        "total_count": total,
        "h1": h1,
        "h2": h2,
        "h_total": h_total,
        "unfloored_h1": uh1,
        "unfloored_h2": uh2,
        "unfloored_h_total": uh1 + uh2,
        "floor_change": abs(h_total - (uh1 + uh2)),
        "column_dev": column_dev,
    }


def canonical_prior_digest(arrays: dict) -> str:
    """Deterministic digest over the frozen prior arrays (Stage-B gate pin).

    Sorted-key canonical form ``key + shape + dtype + C-order bytes``;
    independent of NPZ zip timestamps. Both Stage A (freeze) and Stage B
    (verify) compute this exact function.
    """
    parts = []
    for key in sorted(arrays):
        arr = np.asarray(arrays[key])
        parts.append(key.encode("utf-8"))
        parts.append(str(tuple(int(v) for v in arr.shape)).encode("utf-8"))
        parts.append(str(arr.dtype).encode("utf-8"))
        parts.append(np.ascontiguousarray(arr).tobytes(order="C"))
    return hashlib.sha256(b"\x00".join(parts)).hexdigest()


def build_prior_arrays(counts, *, lam=FROZEN_LAMBDA, floor=FROZEN_FLOOR) -> dict:
    """Calibrated prior arrays exactly as stored in calibrated_prior.npz."""
    cal = calibrate_array(counts, lam=lam, floor=floor)
    mat = np.asarray(counts, dtype=np.float64)
    return {
        "counts_ab": np.ascontiguousarray(mat),
        "f_prior": cal["f_prior"],
        "p1": cal["p1"],
        "p2": cal["p2"],
        "p_b": cal["p_b"],
        "lambda_star": np.asarray(float(FROZEN_LAMBDA), dtype=np.float64),
        "floor_value": np.asarray(float(FROZEN_FLOOR), dtype=np.float64),
        "h1": np.asarray(float(cal["h1"]), dtype=np.float64),
        "h2": np.asarray(float(cal["h2"]), dtype=np.float64),
        "h_total": np.asarray(float(cal["h_total"]), dtype=np.float64),
    }


def load_calibrated_prior(path) -> dict:
    """Load and validate the Stage-A frozen prior (read-only, Stage B seam).

    Checks the exact key set, shapes/dtypes, column normalization within
    1e-12, the lambda/floor pins and literal self-consistency; returns the
    arrays plus the recomputed canonical digest. Digest equality against
    the Stage-A frozen pin is checked by the caller (Stage-B runner).
    """
    p = Path(path)
    if not p.is_file():
        raise PerSessionCalibrationError(f"calibrated prior not found: {p}")
    try:
        data = np.load(str(p), allow_pickle=False)
        with data:
            keys = set(str(k) for k in data.files)
            if keys != set(PRIOR_NPZ_KEYS):
                raise PerSessionCalibrationError(
                    f"prior keys must be exactly {sorted(PRIOR_NPZ_KEYS)}, got {sorted(keys)}"
                )
            arrays = {k: np.asarray(data[k]) for k in PRIOR_NPZ_KEYS}
    except ValueError as exc:
        if str(exc).startswith("frozen calibration requires") or "prior keys" in str(exc):
            raise
        raise PerSessionCalibrationError(f"prior load failed ({exc})") from exc
    counts = arrays["counts_ab"]
    f_prior = arrays["f_prior"]
    p1 = arrays["p1"]
    p2 = arrays["p2"]
    p_b = arrays["p_b"]
    if counts.shape != (1024, 1024):
        raise PerSessionCalibrationError(f"counts_ab must be (1024,1024), got {counts.shape}")
    if f_prior.shape != (1024, 1024):
        raise PerSessionCalibrationError(f"f_prior must be (1024,1024), got {f_prior.shape}")
    if p1.shape != (32, 1024):
        raise PerSessionCalibrationError(f"p1 must be (32,1024), got {p1.shape}")
    if p2.shape != (32, 1024, 32):
        raise PerSessionCalibrationError(f"p2 must be (32,1024,32), got {p2.shape}")
    if p_b.shape != (1024,):
        raise PerSessionCalibrationError(f"p_b must be (1024,), got {p_b.shape}")
    if float(arrays["lambda_star"]) != float(FROZEN_LAMBDA):
        raise PerSessionCalibrationError("prior lambda pin != frozen lambda")
    if float(arrays["floor_value"]) != float(FROZEN_FLOOR):
        raise PerSessionCalibrationError("prior floor pin != frozen floor")
    if abs(float(p_b.sum()) - 1.0) > NORM_TOL:
        raise PerSessionCalibrationError("prior p_b must sum to 1 within 1e-12")
    if float(np.abs(f_prior.sum(axis=0) - 1.0).max()) > NORM_TOL:
        raise PerSessionCalibrationError("prior f_prior columns must sum to 1 within 1e-12")
    if float(np.abs(p1.sum(axis=0) - 1.0).max()) > NORM_TOL:
        raise PerSessionCalibrationError("prior p1 columns must sum to 1 within 1e-12")
    if float(np.abs(p2.sum(axis=2) - 1.0).max()) > NORM_TOL:
        raise PerSessionCalibrationError("prior p2 last-axis must sum to 1 within 1e-12")
    h1 = float(np.sum(p_b * entropy_bits(p1, axis=0)))
    h2 = float(np.sum(p_b[None, :] * p1 * entropy_bits(p2, axis=2)))
    if abs(h1 - float(arrays["h1"])) > NORM_TOL:
        raise PerSessionCalibrationError("prior h1 literal != recomputed within 1e-12")
    if abs(h2 - float(arrays["h2"])) > NORM_TOL:
        raise PerSessionCalibrationError("prior h2 literal != recomputed within 1e-12")
    if abs((h1 + h2) - float(arrays["h_total"])) > NORM_TOL:
        raise PerSessionCalibrationError("prior h_total literal != recomputed within 1e-12")
    return {
        "arrays": arrays,
        "digest": canonical_prior_digest(arrays),
        "h1": h1,
        "h2": h2,
        "h_total": h1 + h2,
    }


def verify_manifest_for_calibration(path, *, source: str = FROZEN_SOURCE) -> dict:
    """Verify the V25 split manifest declares the 1.5M TRAIN pool (JSON only).

    Provenance read; no protected content open. Mirrors the accepted
    manifest validation under the P20H source/pins.
    """
    if source != FROZEN_SOURCE:
        raise PerSessionCalibrationError(
            f"frozen calibration requires source={FROZEN_SOURCE!r}, got {source!r}"
        )
    p = Path(path)
    if not p.is_file():
        raise PerSessionCalibrationError(f"split manifest not found: {p}")
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise PerSessionCalibrationError(f"split manifest unreadable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("schema") != FROZEN_MANIFEST_SCHEMA:
        raise PerSessionCalibrationError("split manifest schema != accepted")
    per_source = doc.get("per_source")
    tag = SOURCE_IDS[source]
    cell = per_source.get(tag) if isinstance(per_source, dict) else None
    if not isinstance(cell, dict):
        raise PerSessionCalibrationError(f"split manifest missing per_source entry {tag!r}")
    try:
        frames = cell["frames"]
        pairs = cell["pairs"]
        got = (
            int(frames["train"]), int(pairs["train"]),
            int(frames["val"]), int(pairs["val"]),
            int(frames["hold"]), int(pairs["hold"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise PerSessionCalibrationError(f"split manifest missing counts: {exc}") from exc
    want = (
        FROZEN_MANIFEST_TRAIN_FRAMES, FROZEN_MANIFEST_TRAIN_PAIRS,
        FROZEN_MANIFEST_VAL_FRAMES, FROZEN_MANIFEST_VAL_PAIRS,
        FROZEN_MANIFEST_HOLD_FRAMES, FROZEN_MANIFEST_HOLD_PAIRS,
    )
    if got != want:
        raise PerSessionCalibrationError(
            f"split manifest 1.5M pool {got} != frozen {want}"
        )
    return {
        "manifest_path": str(p),
        "schema": FROZEN_MANIFEST_SCHEMA,
        "source": source,
        "source_tag": tag,
        "train_frames": got[0],
        "train_pairs": got[1],
        "val_frames": got[2],
        "val_pairs": got[3],
        "hold_frames": got[4],
        "hold_pairs": got[5],
    }


def _stat_record(path) -> dict:
    if path is None:
        return {"path": None, "size_bytes": None, "mtime_ns": None}
    st = Path(path).stat()
    return {"path": str(path), "size_bytes": int(st.st_size), "mtime_ns": int(st.st_mtime_ns)}


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _render_report(plan: dict, identity: dict, literals: dict, digest: str) -> str:
    return "\n".join([
        "# NB-Polar Phase 4-P20H per-session TRAIN calibration",
        "",
        f"- protocol: `{plan['protocol']}` (mode `{plan['mode']}`)",
        f"- source: `{plan['source']}` ({plan['source_tag']}); "
        f"counts {plan['counts_shape']} sum {identity['counts_total']}",
        f"- lambda: `{plan['lambda']}` ({plan['lambda_provenance']})",
        f"- floor: `{plan['floor']}`; packing `{plan['packing']}`; "
        f"conditioning `{plan['conditioning']}`",
        f"- recalibrated literals: H1={literals['h1']!r} H2={literals['h2']!r} "
        f"TOTAL={literals['h_total']!r}",
        f"- floor change vs unfloored smoothed: {literals['floor_change']!r}; "
        f"column dev {literals['column_dev']!r}",
        f"- prior digest: `{digest}`",
        f"- input digest: `{identity['counts_sha256']}` "
        f"(npz {identity['npz_size_bytes']} B)",
        f"- manifest cross-check: TRAIN {identity['manifest_train_pairs']} pairs "
        f"== counts total {identity['counts_total']}: {identity['manifest_cross_check']}",
        f"- counts content opens: {identity['counts_content_opens']} (single declared open)",
        "",
        "Stage B loads `calibrated_prior.npz` read-only behind the "
        "calibration-identity digest gate and refuses on mismatch. No "
        "refit/resmoothing/relambda after any DEV contact.",
        "",
    ])


def run_per_session_calibration(
    *,
    counts=None,
    counts_path=FROZEN_COUNTS_PATH,
    source: str = FROZEN_SOURCE,
    lam=FROZEN_LAMBDA,
    floor=FROZEN_FLOOR,
    manifest_path=FROZEN_MANIFEST_PATH,
    out_dir=FROZEN_OUT_DIR,
) -> dict:
    """Execute the frozen Stage-A calibration once; write five files.

    ``counts`` is the documented injected test seam; the frozen CLI passes
    only the frozen point and reads the 1.5M TRAIN counts through the
    accepted loader exactly once. Any DEV/VAL/HOLD/1M/2M contact is
    impossible: this module has no pairs/parquet code path.
    """
    global _COUNTS_CONTENT_OPENED
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing calibration root: {out_path}")
    source = _check_source(source)
    lam = _check_lambda(lam)
    floor = _check_floor(floor)
    manifest = verify_manifest_for_calibration(manifest_path, source=source)
    if counts is None and _COUNTS_CONTENT_OPENED:
        raise PerSessionCalibrationError(
            "reopen refused: the single counts-calibration open was already consumed"
        )
    # Pre-open plan pins (fixed before any content open).
    plan = {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "source": source,
        "source_tag": FROZEN_SOURCE_TAG,
        "lambda": float(FROZEN_LAMBDA),
        "lambda_provenance": LAMBDA_PROVENANCE,
        "floor": float(FROZEN_FLOOR),
        "packing": FROZEN_PACKING,
        "conditioning": FROZEN_CONDITIONING,
        "formula": (
            "p_global[a] = sum_b counts[a,b]/sum counts; "
            "n_b[b] = sum_a counts[a,b]; "
            "f[a,b] = (counts[a,b] + lambda*p_global[a])/(n_b[b]+lambda)"
        ),
        "counts_shape": [1024, 1024],
        "counts_path": str(counts_path),
        "manifest_path": str(manifest_path),
        "banned_twin": "v72p2d5 build_f_model per-cell counts+lam (never called, never imported)",
    }
    out_path.mkdir(parents=True, exist_ok=False)
    _write_json(out_path / "calibration_plan.json", plan)

    start = time.perf_counter()
    real_counts = counts is None
    if real_counts:
        npz_path = Path(counts_path)
        if not npz_path.is_file():
            raise FileNotFoundError(f"V25 channel counts file not found: {npz_path}")
        npz_stat = _stat_record(npz_path)
        loaded = load_v25_channel_counts(str(counts_path))
        _COUNTS_CONTENT_OPENED = True
        if source not in loaded:
            raise PerSessionCalibrationError(
                f"source {source!r} missing from the loaded V25 counts"
            )
        counts_arr = np.asarray(loaded[source], dtype=np.float64)
    else:
        npz_stat = _stat_record(None)
        counts_arr = np.asarray(counts, dtype=np.float64)
    if counts_arr.shape != (1024, 1024):
        raise PerSessionCalibrationError(
            f"frozen calibration requires counts shape (1024,1024), got {counts_arr.shape}"
        )
    counts_total = int(round(float(counts_arr.sum())))
    counts_sha = hashlib.sha256(
        np.ascontiguousarray(counts_arr).tobytes(order="C")
    ).hexdigest()
    # Split-manifest cross-check: the TRAIN-only input must total exactly
    # the manifest TRAIN pairs. Fail-closed on mismatch.
    cross_ok = bool(counts_total == int(manifest["train_pairs"]))
    if not cross_ok:
        raise PerSessionCalibrationError(
            f"counts total {counts_total} != manifest TRAIN pairs {manifest['train_pairs']}"
        )
    cal = calibrate_array(counts_arr, lam=lam, floor=floor)
    arrays = build_prior_arrays(counts_arr, lam=lam, floor=floor)
    digest = canonical_prior_digest(arrays)
    with open(out_path / "calibrated_prior.npz", "wb") as fh:
        np.savez(
            fh,
            counts_ab=arrays["counts_ab"],
            f_prior=arrays["f_prior"],
            p1=arrays["p1"],
            p2=arrays["p2"],
            p_b=arrays["p_b"],
            lambda_star=arrays["lambda_star"],
            floor_value=arrays["floor_value"],
            h1=arrays["h1"],
            h2=arrays["h2"],
            h_total=arrays["h_total"],
        )
    identity = {
        "protocol": PROTOCOL_NAME,
        "source": source,
        "source_tag": FROZEN_SOURCE_TAG,
        "counts_path": str(counts_path) if real_counts else None,
        "npz_size_bytes": npz_stat["size_bytes"],
        "npz_loader": NPZ_LOADER_IDENTITY if real_counts else None,
        "counts_shape": [1024, 1024],
        "counts_dtype": str(counts_arr.dtype),
        "counts_total": counts_total,
        "counts_sha256": counts_sha,
        "manifest_train_pairs": int(manifest["train_pairs"]),
        "manifest_cross_check": cross_ok,
        "counts_content_opens": 1 if real_counts else 0,
        "attempts_consumed_by_this_run": 1 if real_counts else 0,
        "prior_digest": digest,
    }
    _write_json(out_path / "calibration_input_identity.json", identity)
    literals = {
        "protocol": PROTOCOL_NAME,
        "source": source,
        "h1": float(cal["h1"]),
        "h2": float(cal["h2"]),
        "h_total": float(cal["h_total"]),
        "derivation": (
            "floor-table entropy functionals on the calibrated prior: "
            "H1 = sum_b p_b[b] H(p1[:,b]); "
            "H2 = sum_{b,u1} p_b[b] p1[u1,b] H(p2[u1,b,:]); "
            "p_b from 1.5M TRAIN column totals; replaces the 1M literals "
            "for the target_population_contract gate"
        ),
        "lambda": float(FROZEN_LAMBDA),
        "floor": float(FROZEN_FLOOR),
        "unfloored_h_total": float(cal["unfloored_h_total"]),
        "floor_change": float(cal["floor_change"]),
        "column_dev": float(cal["column_dev"]),
        "counts_total": counts_total,
        "counts_sha256": counts_sha,
        "prior_digest": digest,
    }
    _write_json(out_path / "recalibrated_literals.json", literals)
    (out_path / "calibration_report.md").write_text(
        _render_report(plan, identity, literals, digest), encoding="utf-8"
    )
    return {
        "out_dir": str(out_path),
        "digest": digest,
        "h1": float(cal["h1"]),
        "h2": float(cal["h2"]),
        "h_total": float(cal["h_total"]),
        "counts_total": counts_total,
        "counts_sha256": counts_sha,
        "counts_content_opens": 1 if real_counts else 0,
        "wall_s": round(float(time.perf_counter() - start), 6),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p20h-per-session-calibration",
        description=(
            "NB-Polar Phase 4-P20H per-session TRAIN calibration (frozen "
            "P0/P2 concentration program on --source 1p5M counts only)"
        ),
    )
    parser.add_argument("--counts", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--lambda", required=True, type=float, dest="lambda_")
    parser.add_argument("--floor", required=True, type=float)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_per_session_calibration(
            counts_path=args.counts,
            source=args.source,
            lam=args.lambda_,
            floor=args.floor,
            manifest_path=args.manifest,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p20h per-session calibration refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL_NAME", "MODE", "FROZEN_SOURCE", "FROZEN_SOURCE_TAG",
    "FROZEN_LAMBDA", "LAMBDA_PROVENANCE", "FROZEN_FLOOR", "FROZEN_PACKING",
    "FROZEN_CONDITIONING", "NORM_TOL",
    "FROZEN_MANIFEST_TRAIN_FRAMES", "FROZEN_MANIFEST_TRAIN_PAIRS",
    "FROZEN_MANIFEST_VAL_FRAMES", "FROZEN_MANIFEST_VAL_PAIRS",
    "FROZEN_MANIFEST_HOLD_FRAMES", "FROZEN_MANIFEST_HOLD_PAIRS",
    "FROZEN_COUNTS_PATH", "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA",
    "FROZEN_OUT_DIR", "NPZ_LOADER_IDENTITY", "PRIOR_NPZ_KEYS", "OUTPUT_FILES",
    "ATTEMPT_CONSUMPTION_POINT",
    "PerSessionCalibrationError", "verify_lambda_provenance",
    "calibrate_array", "canonical_prior_digest", "build_prior_arrays",
    "load_calibrated_prior", "verify_manifest_for_calibration",
    "run_per_session_calibration", "build_parser", "main",
]
