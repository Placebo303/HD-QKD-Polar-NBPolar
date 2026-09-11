"""Phase 4-P1 pure prior adapter: Model-F counts to GF32 log metrics.

Frozen contract: ``docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md`` plus
``openspec/changes/formal-ir-nbpolar-phase4-p0/`` (design and specs). This
module implements the accepted per-Bob-column concentration formula only::

    p_global[a] = sum_b counts[a,b] / sum_{a,b} counts[a,b]
    n_b[b]      = sum_a counts[a,b]
    f[a,b]      = (counts[a,b] + lambda*p_global[a]) / (n_b[b] + lambda)

Tables are stored ``[Alice,Bob]`` (axis 0 Alice, axis 1 Bob). Symbol
packing is integer bit ops only (design section 3: ``low=s&31``,
``high=(s>>5)&31``, ``s=low+32*high``, ``U1=high``, ``U2=low``) -- never
GF(1024) field multiplication.

Hard boundaries: NumPy + stdlib only. Never imports the banned per-cell
twin (the rejected smoothing path in ``v72p2d5_gf32_rate_mother`` carrying
``LAMBDA_APPLICATION_CONTRACT_DEFECT``), any cross-layer APP belief path,
or any decoder/benchmark/loading machinery. Operational builders take no
Alice truth; the oracle gather helper lives in the test file only.
Lifecycle: synthetic fixtures only in P1 -- CAL/DEV/EVAL identities are
frozen by a later packet, never here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from numbers import Integral, Real

import numpy as np

__all__ = [
    "Conditioning",
    "Provenance",
    "SymbolMetric",
    "NORM_TOL",
    "Q_SYMBOL",
    "N_LABELS",
    "split_symbol",
    "combine_symbol",
    "smooth_joint_to_conditional",
    "derive_p1",
    "derive_p2",
    "build_p1_metrics",
    "gather_p2_metrics",
    "probs_to_symbol_metric",
    "apply_explicit_floor",
    "check_frame_ids_disjoint",
]

NORM_TOL = 1e-12
Q_SYMBOL = 32
N_LABELS = 1024


class Conditioning(Enum):
    """Joint-Bob conditioning selector (MVP freezes the only value)."""

    FULL_BOB_ONLY = "FULL_BOB_ONLY"


class Provenance(Enum):
    """Belief lineage; D7 pattern, never ``posterior``/``APP``."""

    PRIOR_ONLY = "PRIOR_ONLY"
    ORACLE_CONDITIONED = "ORACLE_CONDITIONED"
    CANDIDATE_CONDITIONED = "CANDIDATE_CONDITIONED"


def split_symbol(s: int) -> tuple[int, int]:
    """Split a 10-bit label into ``(low, high) = (U2, U1)`` (design sec 3)."""
    if isinstance(s, bool) or not isinstance(s, Integral):
        raise TypeError(f"axis contract: symbol must be an integer, got {s!r}")
    s = int(s)
    if not 0 <= s < N_LABELS:
        raise ValueError(f"axis contract: symbol must lie in 0..{N_LABELS - 1}, got {s}")
    return (s & 31, (s >> 5) & 31)


def combine_symbol(low: int, high: int) -> int:
    """Combine ``(low, high) = (U2, U1)`` into a 10-bit label (design sec 3)."""
    for name, value in (("low", low), ("high", high)):
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise TypeError(f"axis contract: {name} must be an integer, got {value!r}")
        if not 0 <= int(value) < Q_SYMBOL:
            raise ValueError(f"axis contract: {name} must lie in 0..{Q_SYMBOL - 1}, got {value!r}")
    return int(low) + 32 * int(high)


def _checked_lambda(lambda_: float) -> float:
    if isinstance(lambda_, bool) or not isinstance(lambda_, Real):
        raise TypeError(f"smoothing contract: lambda must be a real number, got {lambda_!r}")
    lam = float(lambda_)
    if not np.isfinite(lam) or lam < 0:
        raise ValueError(f"smoothing contract: lambda must be finite and >= 0, got {lambda_!r}")
    return lam


def smooth_joint_to_conditional(counts, lambda_: float) -> np.ndarray:
    """Apply the frozen concentration formula; ``counts`` is ``[Alice,Bob]``.

    Unseen-Bob columns (``n_b == 0``) fall back to ``p_global`` exactly;
    with ``lambda_ == 0`` that fallback also covers the ``0/0`` column.
    """
    arr = np.asarray(counts)
    if arr.dtype.kind == "b":
        raise TypeError("smoothing contract: counts must hold numbers, got boolean input")
    if arr.ndim != 2:
        raise ValueError(f"axis contract: counts must be [Alice,Bob], got shape {arr.shape}")
    if arr.shape[0] < 1 or arr.shape[1] < 1:
        raise ValueError(f"smoothing contract: counts must be non-empty, got shape {arr.shape}")
    try:
        mat = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"smoothing contract: counts must be numeric ({exc})") from exc
    if not np.isfinite(mat).all():
        raise ValueError("smoothing contract: counts must be finite")
    if (mat < 0).any():
        raise ValueError("smoothing contract: counts must be non-negative")
    total = mat.sum()
    if total <= 0:
        raise ValueError("smoothing contract: counts total must be positive")
    lam = _checked_lambda(lambda_)
    p_global = mat.sum(axis=1) / total
    n_b = mat.sum(axis=0)
    denom = n_b + lam
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (mat + lam * p_global[:, None]) / denom[None, :]
    zero_cols = n_b == 0
    if zero_cols.any():
        out[:, zero_cols] = p_global[:, None]
    return out


def _checked_joint_table(f, name: str = "f") -> np.ndarray:
    arr = np.asarray(f)
    if arr.dtype.kind == "b":
        raise TypeError(f"axis contract: {name} must hold probabilities, got boolean input")
    if arr.ndim != 2 or arr.shape != (N_LABELS, N_LABELS):
        raise ValueError(
            f"axis contract: {name} must be [Alice,Bob] with shape "
            f"({N_LABELS},{N_LABELS}), got shape {arr.shape}"
        )
    try:
        mat = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"smoothing contract: {name} must be numeric ({exc})") from exc
    if not np.isfinite(mat).all():
        raise ValueError(f"smoothing contract: {name} must be finite")
    if (mat < 0).any():
        raise ValueError(f"smoothing contract: {name} must be non-negative")
    colsum = mat.sum(axis=0)
    if np.abs(colsum - 1).max() > 1e-9:
        raise ValueError(
            "smoothing contract: joint columns must sum to 1, "
            f"max deviation {np.abs(colsum - 1).max():.3e}"
        )
    return mat


def derive_p1(f) -> np.ndarray:
    """Marginalize the joint to ``p1`` with shape ``[U1,B]`` ``(32,1024)``."""
    mat = _checked_joint_table(f)
    return mat.reshape(Q_SYMBOL, Q_SYMBOL, N_LABELS).sum(axis=1)


def derive_p2(f) -> np.ndarray:
    """Condition the joint to ``p2`` with shape ``[U1,B,U2]`` ``(32,1024,32)``.

    Zero-mass ``(U1,B)`` slices fall back to uniform ``1/32`` exactly.
    """
    mat = _checked_joint_table(f)
    joint = mat.reshape(Q_SYMBOL, Q_SYMBOL, N_LABELS)  # [U1,U2,B]
    mass = joint.sum(axis=1)  # [U1,B]
    safe = np.where(mass == 0, 1.0, mass)
    p2 = (joint / safe[:, None, :]).transpose(0, 2, 1)  # [U1,B,U2]
    p2[mass == 0] = 1.0 / Q_SYMBOL
    return p2


def _checked_index_vector(values, q: int, name: str, ndim: int = 2) -> np.ndarray:
    arr = np.asarray(values)
    if arr.dtype.kind == "b":
        raise TypeError(f"axis contract: {name} must hold integers, got boolean input")
    if arr.ndim != ndim:
        raise ValueError(f"axis contract: {name} must be {ndim}D, got shape {arr.shape}")
    if arr.size == 0:
        return np.empty(arr.shape, dtype=np.int64)
    if arr.dtype.kind in "iu":
        out = arr.astype(np.int64, copy=True)
    elif arr.dtype.kind == "O":
        flat = arr.tolist()
        out = np.empty(arr.shape, dtype=np.int64)

        def _fill(dst, src):
            for i, v in enumerate(src):
                if isinstance(src, list) and isinstance(v, list):
                    _fill(dst[i], v)
                else:
                    if isinstance(v, bool) or not isinstance(v, Integral):
                        raise TypeError(f"axis contract: {name} must hold integers, got {v!r}")
                    dst[i] = int(v)

        _fill(out, flat)
    else:
        raise TypeError(f"axis contract: {name} must hold integers, got dtype {arr.dtype}")
    if out.size and (out.min() < 0 or out.max() >= q):
        raise ValueError(f"axis contract: {name} entries must lie in 0..{q - 1}")
    return out


def build_p1_metrics(bob, p1_table) -> np.ndarray:
    """Gather ``p1`` rows per frame/position; takes no Alice input."""
    p1 = np.asarray(p1_table, dtype=np.float64)
    if p1.shape != (Q_SYMBOL, N_LABELS):
        raise ValueError(f"axis contract: p1_table must be [U1,B] (32,1024), got shape {p1.shape}")
    bobs = _checked_index_vector(bob, N_LABELS, "bob")
    return p1[:, bobs].transpose(1, 2, 0)


def gather_p2_metrics(bob, u1, p2_table) -> np.ndarray:
    """Gather candidate-L2 rows for hard ``u1`` estimates; takes no Alice truth."""
    p2 = np.asarray(p2_table, dtype=np.float64)
    if p2.shape != (Q_SYMBOL, N_LABELS, Q_SYMBOL):
        raise ValueError(
            f"axis contract: p2_table must be [U1,B,U2] (32,1024,32), got shape {p2.shape}"
        )
    bobs = _checked_index_vector(bob, N_LABELS, "bob")
    u1s = _checked_index_vector(u1, Q_SYMBOL, "u1")
    if bobs.shape != u1s.shape:
        raise ValueError(
            f"axis contract: bob shape {bobs.shape} != u1 shape {u1s.shape}"
        )
    return p2[u1s, bobs, :]


@dataclass(frozen=True, eq=False)
class SymbolMetric:
    """Immutable decoder-facing log metric with explicit lineage."""

    logp: np.ndarray  # float64[N,q], rows logsumexp 0, exact-zero kept as -inf
    conditioning: Conditioning  # FULL_BOB_ONLY (MVP frozen)
    provenance: Provenance  # PRIOR_ONLY | ORACLE_CONDITIONED | CANDIDATE_CONDITIONED
    symbol_order: tuple  # identity tuple 0..q-1
    normalization: str  # LOGSUMEXP_ZERO

    def __post_init__(self):
        arr = np.asarray(self.logp)
        if arr.dtype.kind == "b":
            raise TypeError("metric contract: logp must hold float log-scores, got boolean input")
        if arr.ndim != 2:
            raise ValueError(f"metric contract: logp must have shape (N, q), got shape {arr.shape}")
        try:
            mat = arr.astype(np.float64, copy=True)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"metric contract: logp must be convertible to float64 ({exc})") from exc
        n, q = mat.shape
        if n < 1:
            raise ValueError("metric contract: logp must hold at least one row")
        if tuple(self.symbol_order) != tuple(range(q)):
            raise ValueError("metric contract: symbol_order must be the identity tuple 0..q-1")
        if not isinstance(self.conditioning, Conditioning):
            raise ValueError(f"provenance contract: conditioning must be a Conditioning member")
        if self.conditioning is not Conditioning.FULL_BOB_ONLY:
            raise ValueError("provenance contract: only FULL_BOB_ONLY conditioning is frozen")
        if not isinstance(self.provenance, Provenance):
            raise ValueError("provenance contract: provenance must be a Provenance member")
        if self.normalization != "LOGSUMEXP_ZERO":
            raise ValueError("metric contract: normalization must be LOGSUMEXP_ZERO")
        if np.isnan(mat).any():
            raise ValueError("metric contract: logp must not contain NaN")
        if np.isposinf(mat).any():
            raise ValueError("metric contract: logp must not contain positive infinity")
        if np.isneginf(mat).all(axis=1).any():
            raise ValueError("metric contract: every logp row needs finite support")
        with np.errstate(invalid="ignore"):
            lse = np.logaddexp.reduce(mat, axis=1)
        if np.abs(lse).max() > 1e-9:
            raise ValueError(
                "metric contract: logp rows must be normalized to logsumexp 0, "
                f"max deviation {np.abs(lse).max():.3e}"
            )
        object.__setattr__(self, "logp", mat)
        object.__setattr__(self, "symbol_order", tuple(self.symbol_order))


def probs_to_symbol_metric(
    probs,
    *,
    conditioning: Conditioning = Conditioning.FULL_BOB_ONLY,
    provenance: Provenance = Provenance.PRIOR_ONLY,
) -> SymbolMetric:
    """Convert a prob table ``(N,32)`` to log domain: ``0 -> -inf``, rows renormed."""
    if not isinstance(conditioning, Conditioning) or conditioning is not Conditioning.FULL_BOB_ONLY:
        raise ValueError("provenance contract: only FULL_BOB_ONLY conditioning is frozen")
    if not isinstance(provenance, Provenance):
        raise ValueError("provenance contract: provenance must be a Provenance member")
    arr = np.asarray(probs)
    if arr.dtype.kind == "b":
        raise TypeError("metric contract: probs must hold numbers, got boolean input")
    if arr.ndim != 2 or arr.shape[1] != Q_SYMBOL:
        raise ValueError(f"metric contract: probs must have shape (N,32), got shape {arr.shape}")
    try:
        mat = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"metric contract: probs must be numeric ({exc})") from exc
    if not np.isfinite(mat).all():
        raise ValueError("metric contract: probs must be finite")
    if (mat < 0).any():
        raise ValueError("metric contract: probs must be non-negative")
    if (mat.sum(axis=1) <= 0).any():
        raise ValueError("metric contract: every probs row needs positive mass")
    with np.errstate(divide="ignore"):
        logp = np.log(mat, out=np.full_like(mat, -np.inf), where=mat > 0)
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(logp, axis=1)
    logp -= lse[:, None]
    return SymbolMetric(
        logp=logp,
        conditioning=conditioning,
        provenance=provenance,
        symbol_order=tuple(range(Q_SYMBOL)),
        normalization="LOGSUMEXP_ZERO",
    )


def apply_explicit_floor(probs, floor_value: float, *, reason: str) -> np.ndarray:
    """Opt-in floor with caller-recorded reason; never silent, never default."""
    if isinstance(floor_value, bool) or not isinstance(floor_value, Real):
        raise TypeError(f"metric contract: floor_value must be a real number, got {floor_value!r}")
    floor = float(floor_value)
    if not np.isfinite(floor) or not 0 < floor < 1:
        raise ValueError(f"metric contract: floor_value must lie in (0,1), got {floor_value!r}")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("provenance contract: floor reason must be a non-empty string")
    arr = np.asarray(probs, dtype=np.float64)
    if arr.ndim < 1:
        raise ValueError(f"metric contract: probs must have a symbol axis, got shape {arr.shape}")
    if not np.isfinite(arr).all() or (arr < 0).any():
        raise ValueError("metric contract: probs must be finite and non-negative")
    out = np.maximum(arr, floor)
    out = out / out.sum(axis=-1, keepdims=True)
    return out


def check_frame_ids_disjoint(*id_groups) -> None:
    """Lifecycle guard: frame-ID sets used for construction must not overlap.

    Reserved for the CAL/DEV/EVAL freeze (later packet); P1 calls it on
    synthetic IDs only. Raises with the ``lifecycle contract:`` prefix.
    """
    seen: dict[int, int] = {}
    for gi, group in enumerate(id_groups):
        try:
            ids = list(group)
        except TypeError as exc:
            raise TypeError(f"lifecycle contract: group {gi} is not iterable ({exc})") from exc
        for value in ids:
            if isinstance(value, bool) or not isinstance(value, Integral):
                raise TypeError(
                    f"lifecycle contract: group {gi} must hold integer frame IDs, got {value!r}"
                )
            key = int(value)
            if key in seen:
                raise ValueError(
                    f"lifecycle contract: frame ID {key} overlaps groups {seen[key]} and {gi}"
                )
            seen[key] = gi
