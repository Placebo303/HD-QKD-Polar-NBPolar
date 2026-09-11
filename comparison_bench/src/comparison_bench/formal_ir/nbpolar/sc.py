"""Reference log-domain q-ary successive-cancellation (SC) decoder.

Classic source SC over the frozen natural-order NB-Polar transform
(``G_N = F_alpha tensor_power n`` with the row-vector kernel
``x0 = u0 + alpha*u1``, ``x1 = u1``).

Input metric contract: ``logp_x[j, a]`` is ``ln P(X_j = a | Bob/context)``
as float64 with the symbol axis last. The decoder validates shape
``(N, q)``, rejects NaN, positive infinity, boolean input, and rows
without finite support, then normalizes every row
(``logsumexp == 0``). Exact-zero support (``-inf``) is preserved end to
end and never replaced by uniform metrics.

SC semantics: coordinate ``i`` is decided from
``P(U_i | U_0..U_{i-1}, B/context)`` with the undecoded suffix
marginalized. Disclosed (known) coordinates hold actual GF symbols,
including zero; position membership is tracked separately from symbol
value. A forced value with exact-zero conditional support raises
``ImpossibleDisclosedValueError``. The operational decoder takes no
Alice truth: callers build metrics externally and pass only disclosed
positions/values.

Failure categories are stable: ``metric contract``, ``field/shape
contract``, ``known-coordinate contract``, ``impossible disclosed
value`` (``ImpossibleDisclosedValueError``), and ``numeric nonfinite
failure`` (``NumericNonfiniteError``).

Complexity is ``O(N q^2 log N)`` NumPy vector operations plus field
operations for partial sums: a correctness reference, not a throughput
target. This module is standalone: no prior adapters, no data loaders,
no benchmark or output machinery, no list decoding, and no legacy
decoder interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral

import numpy as np

from .algebra import validate_symbols
from .transform import polar_transform


class ImpossibleDisclosedValueError(ValueError):
    """A disclosed U value has exact-zero SC conditional support at its turn."""


class NumericNonfiniteError(ValueError):
    """Internal metric arithmetic produced a nonfinite value."""


@dataclass(frozen=True, eq=False)
class SCResult:
    """Reference SC output (hard decisions plus per-coordinate conditionals)."""

    u_hat: np.ndarray  # int64[N] decoded source word, natural order
    x_hat: np.ndarray  # int64[N] re-encoded word, x_hat = u_hat G_N
    status: str  # terminal status; "ok" on every returned result
    decision_metrics: np.ndarray  # float64[N,q] normalized SC conditionals
    decision_log_scores: np.ndarray  # float64[N] chosen-symbol log score
    metric_provenance: dict  # input/row roles, log base, kernel identity
    known_count: int  # number of disclosed coordinates
    known_mask: np.ndarray  # bool[N]; True marks disclosed positions


def _is_power_of_two(n: int) -> bool:
    return n >= 1 and (n & (n - 1)) == 0


def _check_field(field, alpha: int):
    q = getattr(field, "q", None)
    if isinstance(q, bool) or not isinstance(q, Integral) or int(q) <= 0:
        raise ValueError("field/shape contract: decoder field must expose a positive integer q")
    q = int(q)
    for name in ("add", "mul"):
        if not callable(getattr(field, name, None)):
            raise ValueError(f"field/shape contract: decoder field lacks callable {name}")
    if isinstance(alpha, bool) or not isinstance(alpha, Integral):
        raise ValueError("field/shape contract: alpha must be an integer symbol")
    alpha = int(alpha)
    if not 0 <= alpha < q:
        raise ValueError(f"field/shape contract: alpha must lie in 0..{q - 1}")
    return q, alpha


def _normalize_rows(mat: np.ndarray) -> np.ndarray:
    """Normalize each row to logsumexp 0; keep all-`-inf` rows for the caller."""
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(mat, axis=1)
    if np.isnan(lse).any():
        raise NumericNonfiniteError("numeric nonfinite failure: NaN in metric normalization")
    out = mat.copy()
    finite = np.isfinite(lse)
    out[finite] -= lse[finite, None]
    return out


def _validate_metric(logp_x, q: int) -> tuple[np.ndarray, int]:
    arr = np.asarray(logp_x)
    if arr.dtype.kind == "b":
        raise TypeError("metric contract: logp_x must hold float log-scores, got boolean input")
    if arr.ndim != 2:
        raise ValueError(f"metric contract: logp_x must have shape (N, q), got shape {arr.shape}")
    try:
        mat = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"metric contract: logp_x must be convertible to float64 ({exc})") from exc
    n, qq = mat.shape
    if qq != q:
        raise ValueError(f"field/shape contract: logp_x width {qq} != field q {q}")
    if not _is_power_of_two(n):
        raise ValueError(f"field/shape contract: block length N={n} is not a positive power of two")
    if np.isnan(mat).any():
        raise ValueError("metric contract: logp_x must not contain NaN")
    if np.isposinf(mat).any():
        raise ValueError("metric contract: logp_x must not contain positive infinity")
    if np.isneginf(mat).all(axis=1).any():
        raise ValueError("metric contract: every logp_x row needs finite support")
    return _normalize_rows(mat), n


def _validate_positions(positions, n: int) -> np.ndarray:
    arr = np.asarray(positions)
    if arr.dtype.kind == "b":
        raise TypeError("known-coordinate contract: positions must hold integers, got boolean input")
    if arr.ndim != 1:
        raise ValueError("known-coordinate contract: positions must be one-dimensional")
    if arr.size == 0:
        return np.empty(0, dtype=np.int64)
    if arr.dtype.kind in "iu":
        out = arr.astype(np.int64, copy=True)
    elif arr.dtype.kind == "O":
        out = np.empty(arr.shape[0], dtype=np.int64)
        for index, value in enumerate(arr.tolist()):
            if isinstance(value, bool) or not isinstance(value, Integral):
                raise TypeError(
                    f"known-coordinate contract: positions[{index}] must be an integer, got {value!r}"
                )
            out[index] = int(value)
    else:
        raise TypeError("known-coordinate contract: positions must hold integers")
    if out.min() < 0 or out.max() >= n:
        raise ValueError(f"known-coordinate contract: positions must lie in 0..{n - 1}")
    if len(set(out.tolist())) != out.size:
        raise ValueError("known-coordinate contract: positions must not repeat")
    return out


def _validate_known(known_positions, known_values, n: int, q: int) -> dict:
    if known_positions is None and known_values is None:
        return {}
    if known_positions is None or known_values is None:
        raise ValueError("known-coordinate contract: positions and values must be given together")
    pos = _validate_positions(known_positions, n)
    try:
        val = validate_symbols(known_values, q, name="known_values")
    except (TypeError, ValueError) as exc:
        raise type(exc)(f"known-coordinate contract: {exc}") from exc
    if pos.shape[0] != val.shape[0]:
        raise ValueError("known-coordinate contract: positions and values lengths differ")
    return dict(zip(pos.tolist(), val.tolist()))


def _combination_index(field, alpha: int, q: int) -> np.ndarray:
    """Precompute ``index[u, v] = u + alpha*v`` once per decode."""
    scaled = field.add(alpha, 0)
    index = np.empty((q, q), dtype=np.int64)
    for u in range(q):
        for v in range(q):
            index[u, v] = field.add(u, field.mul(scaled, v))
    return index


def _minus_block(first: np.ndarray, second: np.ndarray, index: np.ndarray) -> np.ndarray:
    """Left synthetic metrics: ``logsumexp_v L0[u+alpha*v] + L1[v]``, normalized."""
    gathered = first[:, index] + second[:, None, :]
    return _normalize_rows(np.logaddexp.reduce(gathered, axis=2))


def _plus_block(first: np.ndarray, second: np.ndarray, beta: np.ndarray, index: np.ndarray) -> np.ndarray:
    """Right metrics conditioned on encoded partial sums ``beta``, normalized."""
    rows = np.arange(first.shape[0])[:, None]
    return _normalize_rows(first[rows, index[beta]] + second)


def sc_decode(logp_x, *, field, alpha: int = 2, known_positions=None, known_values=None) -> SCResult:
    """Run reference q-ary SC and return hard decisions plus conditionals.

    ``known_positions``/``known_values`` are parallel arrays mapping U
    coordinates to disclosed GF symbols (zero is a value, never
    unknown); input order is irrelevant. Unspecified coordinates are
    decided by maximum conditional probability with ties broken toward
    the smallest symbol index.
    """
    q, alpha = _check_field(field, alpha)
    metrics, n = _validate_metric(logp_x, q)
    known = _validate_known(known_positions, known_values, n, q)
    index = _combination_index(field, alpha, q)

    u_hat = np.empty(n, dtype=np.int64)
    decision_metrics = np.empty((n, q), dtype=np.float64)
    decision_log_scores = np.empty(n, dtype=np.float64)

    def decode_segment(block: np.ndarray, offset: int) -> None:
        size = block.shape[0]
        if size == 1:
            row = block[0]
            decision_metrics[offset] = row
            if offset in known:
                choice = known[offset]
                if row[choice] == -np.inf:
                    raise ImpossibleDisclosedValueError(
                        f"impossible disclosed value: U[{offset}]={choice} has exact-zero support"
                    )
            else:
                if not np.isfinite(row).any():
                    raise NumericNonfiniteError(
                        f"numeric nonfinite failure: no finite support at U[{offset}]"
                    )
                choice = int(np.argmax(row))
            u_hat[offset] = choice
            decision_log_scores[offset] = float(row[choice])
            return
        half = size // 2
        left_in = _minus_block(block[:half], block[half:], index)
        decode_segment(left_in, offset)
        beta = polar_transform(u_hat[offset : offset + half], field=field, alpha=alpha)
        right_in = _plus_block(block[:half], block[half:], beta, index)
        decode_segment(right_in, offset + half)

    decode_segment(metrics, 0)
    x_hat = polar_transform(u_hat, field=field, alpha=alpha)
    known_mask = np.zeros(n, dtype=bool)
    known_mask[list(known)] = True
    provenance = {
        "input_role": "prior: logp_x[j,a] = ln P(X_j=a | Bob/context), rows normalized to logsumexp 0",
        "row_role": "classic source SC conditionals: decision_metrics[i,a] = ln P(U_i=a | U_<i, B/context), suffix marginalized",
        "log_base": "natural",
        "normalization": "float64; every produced row normalized, exact-zero support kept as -inf",
        "tie_break": "argmax chooses the smallest symbol index on ties",
        "kernel": "row-vector F_alpha with x0=u0+alpha*u1, x1=u1, natural order",
        "q": q,
        "alpha": alpha,
        "primitive_polynomial": getattr(field, "primitive_polynomial", None),
    }
    return SCResult(
        u_hat=u_hat,
        x_hat=x_hat,
        status="ok",
        decision_metrics=decision_metrics,
        decision_log_scores=decision_log_scores,
        metric_provenance=provenance,
        known_count=len(known),
        known_mask=known_mask,
    )
