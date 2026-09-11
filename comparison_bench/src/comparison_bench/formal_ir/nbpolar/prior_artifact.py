"""Phase 4-P2 read-only prior-artifact adapter (synthetic phase).

Loads the single accepted Model-F CAL input artifact through a narrow
read-only boundary and returns a frozen in-memory record. Frozen schema is
reimplemented here from the accepted P0 contract
(``docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md``) and the locally documented
producer schema (``comparison_bench/tests/test_v72p2d5_model_f_input.py``
``test_M11_summary_frozen``); the sibling checkout is never imported and no
default production path exists -- both artifact paths are explicit caller
arguments, so synthetic tests can only inject temporary roots.

Accepted structure (TASK_PACKET.md frozen input)::

    model_f_input.npz              keys exactly {counts_ab, p_b}
    model_f_input_summary.json     frozen identity fields (see _EXPECTED_SUMMARY)

``counts_ab`` is ``[Alice,Bob]`` ``(1024,1024)`` int64 summing to exactly
262144 (1024 CAL frames 702..1725 x 256 pairs); ``p_b`` is the axis-0
column marginal ``(1024,)``. Provenance is ``PRIOR_ONLY`` /
``FULL_BOB_ONLY`` only; the loader takes no Alice truth vector and writes
nothing. All failures raise with the ``artifact contract:`` prefix and stop
before any SC/decoder use.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .prior import Conditioning, Provenance

__all__ = [
    "NORM_TOL",
    "N_LABELS",
    "N_SYMBOLS",
    "LAMBDA_STAR",
    "NPZ_FILENAME",
    "SUMMARY_FILENAME",
    "PriorArtifact",
    "load_prior_artifact",
]

NORM_TOL = 1e-12
N_LABELS = 1024
N_SYMBOLS = 262144
LAMBDA_STAR = 137.3823795883264
NPZ_FILENAME = "model_f_input.npz"
SUMMARY_FILENAME = "model_f_input_summary.json"
NPZ_KEYS = ("counts_ab", "p_b")

# Frozen summary identity, exactly as produced for the accepted artifact.
# ``status`` stays MODEL_F_INPUT_CANDIDATE: acceptance was recorded at cycle
# level and the protected immutable root was never rewritten (decision-log).
_EXPECTED_SUMMARY = {
    "schema": "v72p2d5_model_f_input_v1",
    "cycle": "V72P2D5-GF32-RATE-MOTHER",
    "session": "20260123_1M_600k_0dB",
    "source": "1M",
    "cal_start": 702,
    "cal_end": 1725,
    "n_frames": 1024,
    "pairs_per_frame": 256,
    "n_symbols": N_SYMBOLS,
    "axis": ["Alice", "Bob"],
    "dims": [N_LABELS, N_LABELS],
    "mapping": "symbol=low+32*high;high=U1;low=U2",
    "field": {"q": 32, "poly": 37},
    "lambda_star": LAMBDA_STAR,
    "selection": "D4R2 nested-CV refit",
    "cal_only": True,
    "val_rows_read": 0,
    "decoder_calls": 0,
    "p0_calls": 0,
    "formal": False,
    "status": "MODEL_F_INPUT_CANDIDATE",
    "artifact_files": [NPZ_FILENAME, SUMMARY_FILENAME],
}


@dataclass(frozen=True, eq=False)
class PriorArtifact:
    """Validated immutable CAL count tables with frozen identity/provenance."""

    counts_ab: np.ndarray  # int64 (1024,1024) [Alice,Bob], sum 262144, read-only
    p_b: np.ndarray  # float64 (1024,), axis-0 marginal, read-only
    summary: dict  # copy of the accepted summary identity
    conditioning: Conditioning  # FULL_BOB_ONLY (MVP frozen)
    provenance: Provenance  # PRIOR_ONLY (never posterior/APP)

    def __post_init__(self):
        counts = np.asarray(self.counts_ab)
        p_b = np.asarray(self.p_b)
        if counts.shape != (N_LABELS, N_LABELS):
            raise ValueError(
                f"artifact contract: counts_ab must be (1024,1024), got {counts.shape}"
            )
        if p_b.shape != (N_LABELS,):
            raise ValueError(
                f"artifact contract: p_b must be (1024,), got {p_b.shape}"
            )
        if self.conditioning is not Conditioning.FULL_BOB_ONLY:
            raise ValueError("artifact contract: conditioning must be FULL_BOB_ONLY")
        if self.provenance is not Provenance.PRIOR_ONLY:
            raise ValueError("artifact contract: provenance must be PRIOR_ONLY")
        if not isinstance(self.summary, dict):
            raise ValueError("artifact contract: summary must be a dict")
        object.__setattr__(self, "counts_ab", counts)
        object.__setattr__(self, "p_b", p_b)
        object.__setattr__(self, "summary", dict(self.summary))


def _fail(reason: str) -> ValueError:
    return ValueError(f"artifact contract: {reason}")


def _load_npz(npz_path: Path) -> dict:
    if npz_path.name != NPZ_FILENAME:
        raise _fail(f"npz basename must be {NPZ_FILENAME}, got {npz_path.name}")
    if not npz_path.is_file():
        raise _fail(f"npz path is not a regular file: {npz_path}")
    try:
        data = np.load(str(npz_path), allow_pickle=False)
        with data:
            keys = set(str(k) for k in data.files)
            if keys != set(NPZ_KEYS):
                raise _fail(f"npz keys must be exactly {sorted(NPZ_KEYS)}, got {sorted(keys)}")
            out = {k: np.asarray(data[k]) for k in NPZ_KEYS}
    except ValueError as exc:
        if str(exc).startswith("artifact contract:"):
            raise
        raise _fail(f"npz load failed ({exc})") from exc
    for key, arr in out.items():
        if arr.dtype.kind in ("O", "V"):
            raise _fail(f"npz key {key} holds object/void data (pickle forbidden)")
        if arr.dtype.kind == "b":
            raise _fail(f"npz key {key} holds boolean data")
    return out


def _check_counts(counts: np.ndarray) -> np.ndarray:
    if counts.shape != (N_LABELS, N_LABELS):
        raise _fail(f"counts_ab shape must be (1024,1024), got {counts.shape}")
    if counts.dtype.kind not in "iu":
        raise _fail(f"counts_ab must hold integers, got dtype {counts.dtype}")
    mat = counts.astype(np.int64, copy=True)
    if (mat < 0).any():
        raise _fail("counts_ab must be non-negative")
    total = int(mat.sum())
    if total != N_SYMBOLS:
        raise _fail(f"counts_ab sum must be exactly {N_SYMBOLS}, got {total}")
    mat.flags.writeable = False
    return mat


def _check_marginal(p_b: np.ndarray, counts: np.ndarray) -> np.ndarray:
    if p_b.shape != (N_LABELS,):
        raise _fail(f"p_b shape must be (1024,), got {p_b.shape}")
    try:
        vec = p_b.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise _fail(f"p_b must be numeric ({exc})") from exc
    if not np.isfinite(vec).all():
        raise _fail("p_b must be finite")
    if (vec < 0).any():
        raise _fail("p_b must be non-negative")
    if abs(float(vec.sum()) - 1.0) > NORM_TOL:
        raise _fail(f"p_b must sum to 1 within {NORM_TOL}, got {float(vec.sum())!r}")
    expect = counts.astype(np.float64).sum(axis=0) / float(N_SYMBOLS)
    if float(np.abs(vec - expect).max()) > NORM_TOL:
        raise _fail("p_b must equal counts_ab.sum(axis=0)/262144 within 1e-12")
    vec.flags.writeable = False
    return vec


def _check_summary(summary_path: Path, counts: np.ndarray) -> dict:
    if summary_path.name != SUMMARY_FILENAME:
        raise _fail(f"summary basename must be {SUMMARY_FILENAME}, got {summary_path.name}")
    if not summary_path.is_file():
        raise _fail(f"summary path is not a regular file: {summary_path}")
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise _fail(f"summary JSON parse failed ({exc})") from exc
    if not isinstance(summary, dict):
        raise _fail(f"summary must be a JSON object, got {type(summary).__name__}")
    for key, want in _EXPECTED_SUMMARY.items():
        if key not in summary:
            raise _fail(f"summary missing identity key {key!r}")
        if summary[key] != want:
            raise _fail(f"summary identity mismatch on {key!r}: {summary[key]!r} != {want!r}")
    if int(summary["n_symbols"]) != int(counts.sum()):
        raise _fail("summary n_symbols disagrees with counts_ab sum")
    if list(summary["dims"]) != list(counts.shape):
        raise _fail("summary dims disagree with counts_ab shape")
    return dict(summary)


def load_prior_artifact(npz_path, summary_path) -> PriorArtifact:
    """Load and validate the accepted CAL prior artifact (read-only).

    Both paths are explicit; there is no default root. No Alice truth is
    accepted, nothing is written, and the returned arrays are read-only.
    """
    npz = _load_npz(Path(npz_path))
    counts = _check_counts(npz["counts_ab"])
    p_b = _check_marginal(npz["p_b"], counts)
    summary = _check_summary(Path(summary_path), counts)
    return PriorArtifact(
        counts_ab=counts,
        p_b=p_b,
        summary=summary,
        conditioning=Conditioning.FULL_BOB_ONLY,
        provenance=Provenance.PRIOR_ONLY,
    )
