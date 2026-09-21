"""NB-Polar M2 +/-1 parametric prior adapter (CANDIDATE, Stage-1 surface).

Decoder-free preparation-only module for packet
``NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION`` (OpenSpec change
``nbpolar-prior-rebaseline`` T2 at Stage-1 scope). M2 is a CANDIDATE,
never the baseline; the incumbent stays the raw-MLE table (M0, P7 rule).

What this module does (packet Spec 1, frozen):

- ``fit_m2_triple``: per-session triple (q0, q+1, q-1) over delta in
  {0, +1, -1} from int64 ``counts_ab`` ``[Alice, Bob]`` (axis 0 Alice,
  matching ``build_model_f_input``); rest mass goes to the floor.
- ``build_m2_joint``: expand the triple to the full model-implied
  1024x1024 P(A|B), then ``maximum(FLOOR)`` + per-B-column renorm.
- ``build_m0_joint``: the incumbent P7 raw-MLE-plus-floor rule
  (S8 ``fit_m0`` literally), NEVER the lambda-concentration formula.
- ``build_prior``: ``mode in {"M2", "M0"}`` switch (M0 ignores MOD).
- ``split_symbol`` / ``combine_symbol``: vendored packing contracts
  (``U1 = s >> 5``, ``U2 = s & 31``, ``s = low + 32*high``).
- ``prob_rows_to_logp``: ``(N, 32)`` to log domain (``0 -> -inf``,
  rows logsumexp 0) per the ``sc.py`` consumer contract.

MOD boundary (frozen value, not a tunable): ``LINEAR_ONLY`` (default)
counts the two wrap cells ``(0,1023)`` / ``(1023,0)`` as tail (floor,
conservative); ``CIRCULAR`` prices them as neighbours. A fixed-triple
MOD toggle changes EXACTLY those 2 cells pre-floor and nothing else.
The freeze records ``mod_boundary`` explicitly; G1/G2 never switch it
post-freeze.

Layer factorization is CALLER-side and never lives here: the caller
applies the UNCHANGED frozen ``derive_p1`` -> ``(32,1024)`` ``[U1,B]``
and ``derive_p2`` -> ``(32,1024,32)``, then ``build_p1_metrics`` /
``gather_p2_metrics`` + ``probs_to_symbol_metric(provenance=PRIOR_ONLY)``.
M2 induces P1/P2 solely through the joint it supplies.

Hard boundaries: NumPy + stdlib only. Zero dependence on the frozen
``nbpolar`` package (no relative imports either). Synthetic fixtures only; no CAL/artifact
reads, no decoder call, no claim.
"""

from __future__ import annotations

from numbers import Integral, Real

import numpy as np

__all__ = [
    "N_LABELS",
    "Q_SYMBOL",
    "FLOOR",
    "MODES",
    "DEFAULT_MOD",
    "fit_m2_triple",
    "build_m2_joint",
    "build_m0_joint",
    "build_prior",
    "split_symbol",
    "combine_symbol",
    "prob_rows_to_logp",
]

N_LABELS = 1024
Q_SYMBOL = 32
FLOOR = 1e-15
MODES = ("LINEAR_ONLY", "CIRCULAR")
DEFAULT_MOD = "LINEAR_ONLY"


def _checked_mod(mod: str) -> str:
    if mod not in MODES:
        raise ValueError(
            f"m2 contract: mod must be one of {list(MODES)}, got {mod!r}"
        )
    return mod


def _checked_counts(counts) -> np.ndarray:
    arr = np.asarray(counts)
    if arr.dtype.kind == "b":
        raise TypeError("m2 contract: counts must hold numbers, got boolean input")
    if arr.ndim != 2 or arr.shape != (N_LABELS, N_LABELS):
        raise ValueError(
            "m2 contract: counts must be [Alice,Bob] with shape "
            f"({N_LABELS},{N_LABELS}), got shape {arr.shape}"
        )
    if arr.dtype.kind not in "iu":
        raise TypeError(
            f"m2 contract: counts must hold integers, got dtype {arr.dtype}"
        )
    mat = arr.astype(np.int64, copy=True)
    if (mat < 0).any():
        raise ValueError("m2 contract: counts must be non-negative")
    if int(mat.sum()) <= 0:
        raise ValueError("m2 contract: counts total must be positive")
    return mat


def _checked_prob_table(counts) -> np.ndarray:
    arr = np.asarray(counts)
    if arr.dtype.kind == "b":
        raise TypeError("m2 contract: counts must hold numbers, got boolean input")
    if arr.ndim != 2 or arr.shape != (N_LABELS, N_LABELS):
        raise ValueError(
            "m2 contract: counts must be [Alice,Bob] with shape "
            f"({N_LABELS},{N_LABELS}), got shape {arr.shape}"
        )
    try:
        mat = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"m2 contract: counts must be numeric ({exc})") from exc
    if not np.isfinite(mat).all():
        raise ValueError("m2 contract: counts must be finite")
    if (mat < 0).any():
        raise ValueError("m2 contract: counts must be non-negative")
    return mat


def fit_m2_triple(counts_ab, *, mod: str = DEFAULT_MOD) -> dict:
    """Fit the per-session +/-1 triple from event counts.

    ``n0`` = event mass on ``a == b``; ``n_plus`` = mass on
    ``a == (b+1) % 1024`` excluding cell ``(0,1023)`` iff LINEAR_ONLY;
    ``n_minus`` = mass on ``a == (b-1) % 1024`` excluding cell
    ``(1023,0)`` iff LINEAR_ONLY; ``n_total`` = total event mass.
    Returns ``{q0, q_plus1, q_minus1, q_rest, n0, n_plus, n_minus,
    n_total, mod}`` with ``q = n_x / n_total``.
    """
    mod = _checked_mod(mod)
    mat = _checked_counts(counts_ab)
    b = np.arange(N_LABELS)
    n0 = int(mat[b, b].sum())
    n_plus = int(mat[(b + 1) % N_LABELS, b].sum())
    n_minus = int(mat[(b - 1) % N_LABELS, b].sum())
    if mod == "LINEAR_ONLY":
        n_plus -= int(mat[0, N_LABELS - 1])
        n_minus -= int(mat[N_LABELS - 1, 0])
    n_total = int(mat.sum())
    n = float(n_total)
    return {
        "q0": n0 / n,
        "q_plus1": n_plus / n,
        "q_minus1": n_minus / n,
        "q_rest": (n_total - n0 - n_plus - n_minus) / n,
        "n0": n0,
        "n_plus": n_plus,
        "n_minus": n_minus,
        "n_total": n_total,
        "mod": mod,
    }


def _checked_triple_q(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(
            f"m2 contract: {name} must be a real number, got {value!r}"
        )
    out = float(value)
    if not np.isfinite(out):
        raise ValueError(f"m2 contract: {name} must be finite, got {value!r}")
    if out < 0:
        raise ValueError(
            f"m2 contract: {name} must be non-negative, got {value!r}"
        )
    return out


def build_m2_joint(
    q0: float,
    q_plus1: float,
    q_minus1: float,
    *,
    mod: str = DEFAULT_MOD,
    floor: float = 1e-15,
) -> np.ndarray:
    """Expand a triple to the full 1024x1024 P(A|B) joint.

    Per-cell rule: ``q0`` where ``a == b``; ``q_plus1`` / ``q_minus1``
    on the +/-1 diagonals minus the LINEAR-excluded wrap cells;
    ``0`` elsewhere. Then ``maximum(floor)`` + per-B-column renorm.
    ``floor != 1e-15`` is a hard error (frozen literal, never a knob).
    """
    mod = _checked_mod(mod)
    if not floor == 1e-15:
        raise ValueError(
            f"m2 contract: floor is frozen at 1e-15, got {floor!r}"
        )
    q0 = _checked_triple_q(q0, "q0")
    q_plus1 = _checked_triple_q(q_plus1, "q_plus1")
    q_minus1 = _checked_triple_q(q_minus1, "q_minus1")
    if q0 + q_plus1 + q_minus1 > 1.0 + 1e-12:
        raise ValueError(
            "m2 contract: triple mass must not exceed 1, got "
            f"{q0 + q_plus1 + q_minus1!r}"
        )
    b = np.arange(N_LABELS)
    base = np.zeros((N_LABELS, N_LABELS), dtype=np.float64)
    base[b, b] = q0
    base[(b + 1) % N_LABELS, b] = q_plus1
    base[(b - 1) % N_LABELS, b] = q_minus1
    if mod == "LINEAR_ONLY":
        base[0, N_LABELS - 1] = 0.0
        base[N_LABELS - 1, 0] = 0.0
    joint = np.maximum(base, floor)
    return joint / joint.sum(axis=0, keepdims=True)


def build_m0_joint(counts_ab) -> np.ndarray:
    """Incumbent P7 table rule (S8 ``fit_m0`` literally).

    Raw-count MLE per B column, empty B column -> uniform ``1/1024``,
    then ``maximum(1e-15)`` + per-column renorm. NEVER the
    lambda-concentration formula.
    """
    mat = _checked_prob_table(counts_ab)
    n_b = mat.sum(axis=0)
    empty = n_b == 0
    denom = np.where(empty, 1.0, n_b)
    out = mat / denom[None, :]
    if empty.any():
        out[:, empty] = 1.0 / N_LABELS
    out = np.maximum(out, FLOOR)
    return out / out.sum(axis=0, keepdims=True)


def build_prior(counts_ab, *, mode: str, mod: str = DEFAULT_MOD) -> np.ndarray:
    """Build the P(A|B) joint for ``mode in {"M2", "M0"}`` (exact).

    M0 ignores MOD (identical output under either value). Unknown mode
    is a hard error.
    """
    if mode == "M2":
        triple = fit_m2_triple(counts_ab, mod=mod)
        return build_m2_joint(
            triple["q0"], triple["q_plus1"], triple["q_minus1"], mod=mod
        )
    if mode == "M0":
        return build_m0_joint(counts_ab)
    raise ValueError(
        f"m2 contract: mode must be one of ['M2', 'M0'], got {mode!r}"
    )


def split_symbol(s: int) -> tuple[int, int]:
    """Split a 10-bit label into ``(low, high) = (U2, U1)``."""
    if isinstance(s, bool) or not isinstance(s, Integral):
        raise TypeError(f"m2 contract: symbol must be an integer, got {s!r}")
    s = int(s)
    if not 0 <= s < N_LABELS:
        raise ValueError(
            f"m2 contract: symbol must lie in 0..{N_LABELS - 1}, got {s}"
        )
    return (s & 31, (s >> 5) & 31)


def combine_symbol(low: int, high: int) -> int:
    """Combine ``(low, high) = (U2, U1)`` into a 10-bit label."""
    for name, value in (("low", low), ("high", high)):
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise TypeError(
                f"m2 contract: {name} must be an integer, got {value!r}"
            )
        if not 0 <= int(value) < Q_SYMBOL:
            raise ValueError(
                f"m2 contract: {name} must lie in 0..{Q_SYMBOL - 1}, got {value!r}"
            )
    return int(low) + 32 * int(high)


def prob_rows_to_logp(probs) -> np.ndarray:
    """Convert a prob table ``(N,32)`` to log domain.

    ``0 -> -inf``, else ``ln p``, minus the rowwise logsumexp. Rows
    come out logsumexp 0 within 1e-12; no NaN / +inf; every row keeps
    finite support.
    """
    arr = np.asarray(probs)
    if arr.dtype.kind == "b":
        raise TypeError("m2 contract: probs must hold numbers, got boolean input")
    if arr.ndim != 2 or arr.shape[1] != Q_SYMBOL:
        raise ValueError(
            f"m2 contract: probs must have shape (N,32), got shape {arr.shape}"
        )
    if arr.shape[0] < 1:
        raise ValueError("m2 contract: probs must hold at least one row")
    try:
        mat = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"m2 contract: probs must be numeric ({exc})") from exc
    if not np.isfinite(mat).all():
        raise ValueError("m2 contract: probs must be finite")
    if (mat < 0).any():
        raise ValueError("m2 contract: probs must be non-negative")
    if (mat.sum(axis=1) <= 0).any():
        raise ValueError("m2 contract: every probs row needs positive mass")
    with np.errstate(divide="ignore"):
        logp = np.log(mat, out=np.full_like(mat, -np.inf), where=mat > 0)
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(logp, axis=1)
    return logp - lse[:, None]
