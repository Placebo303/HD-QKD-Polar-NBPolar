"""Independent exhaustive SC-conditional oracle (test reference only).

Independence: this module imports only the accepted Phase 1 surface
(``polar_transform_reference``) plus ``numpy``/``itertools``. It never
imports production SC recursion, minus/plus helpers, partial-sum
helpers, validation, normalization, or decision logic from ``sc.py``.
Block scores are literal ``sum_j logp_x[j, X_j]`` with
``X = polar_transform_reference(U)``; conditionals aggregate scores by
candidate ``U_i`` with a standalone stable logsumexp, then normalize.

The oracle takes an explicit candidate prefix, so tests can evaluate
conditionals at decoded, forced, or adversarial prefixes. It must not
be mistaken for a decoder: enumeration is exponential and guarded to
tiny domains (at most 4096 full candidates).
"""

from __future__ import annotations

import itertools
from numbers import Integral

import numpy as np

from .transform import polar_transform_reference

MAX_ORACLE_CANDIDATES = 4096


def _oracle_logsumexp(values) -> float:
    """Standalone max-subtraction logsumexp; all-`-inf` maps to `-inf`."""
    arr = np.asarray(values, dtype=np.float64).ravel()
    top = np.max(arr)
    if top == -np.inf:
        return -np.inf
    if not np.isfinite(top):
        raise ValueError("oracle metric failure: nonfinite aggregate")
    return float(top + np.log(np.sum(np.exp(arr - top))))


def _check_oracle_metric(logp_x, field, alpha: int):
    q = getattr(field, "q", None)
    if isinstance(q, bool) or not isinstance(q, Integral) or int(q) <= 0:
        raise ValueError("oracle contract: field must expose a positive integer q")
    q = int(q)
    if isinstance(alpha, bool) or not isinstance(alpha, Integral) or not 0 <= int(alpha) < q:
        raise ValueError("oracle contract: alpha must be an integer symbol in 0..q-1")
    mat = np.asarray(logp_x)
    if mat.dtype.kind == "b" or mat.ndim != 2:
        raise ValueError("oracle contract: logp_x must be a 2-D float array")
    try:
        mat = mat.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"oracle contract: logp_x must be convertible to float64 ({exc})") from exc
    n, qq = mat.shape
    if qq != q or n < 1 or (n & (n - 1)):
        raise ValueError("oracle contract: logp_x must have shape (2**k, field.q)")
    if np.isnan(mat).any() or np.isposinf(mat).any():
        raise ValueError("oracle contract: logp_x must not contain NaN or +inf")
    if np.isneginf(mat).all(axis=1).any():
        raise ValueError("oracle contract: every logp_x row needs finite support")
    if q**n > MAX_ORACLE_CANDIDATES:
        raise ValueError(f"oracle contract: q**N={q ** n} exceeds tiny-domain cap {MAX_ORACLE_CANDIDATES}")
    return mat, n, q, int(alpha)


def _check_prefix(prefix, n: int, q: int) -> list:
    arr = np.asarray(prefix)
    if arr.dtype.kind == "b" or arr.ndim != 1:
        raise ValueError("oracle contract: prefix must be a one-dimensional integer vector")
    if arr.size >= n:
        raise ValueError("oracle contract: prefix length must be below N")
    out = []
    for index, value in enumerate(arr.tolist()):
        if isinstance(value, bool) or not isinstance(value, Integral) or not 0 <= int(value) < q:
            raise ValueError(f"oracle contract: prefix[{index}] must be a symbol in 0..{q - 1}")
        out.append(int(value))
    return out


def oracle_block_log_score(logp_x, u_candidate, *, field, alpha: int = 2) -> float:
    """Literal block score ``sum_j logp_x[j, X_j]`` for one U candidate."""
    mat, n, q, alpha = _check_oracle_metric(logp_x, field, alpha)
    full = _check_prefix(u_candidate, n + 1, q)
    if len(full) != n:
        raise ValueError("oracle contract: candidate must hold exactly N symbols")
    vec = np.asarray(full, dtype=np.int64)
    encoded = polar_transform_reference(vec, field=field, alpha=alpha)
    return float(sum(float(mat[j, int(encoded[j])]) for j in range(n)))


def oracle_sc_metric(logp_x, prefix, *, field, alpha: int = 2) -> np.ndarray:
    """Exhaustive conditional for ``U[len(prefix)]`` given ``prefix``.

    Enumerates every suffix assignment, scores each complete candidate
    with the literal block score, aggregates by candidate symbol with
    the standalone logsumexp, and normalizes. An all-`-inf` row reports
    an impossible prefix.
    """
    mat, n, q, alpha = _check_oracle_metric(logp_x, field, alpha)
    fixed = _check_prefix(prefix, n, q)
    coord = len(fixed)
    out = np.empty(q, dtype=np.float64)
    for symbol in range(q):
        scores = []
        for suffix in itertools.product(range(q), repeat=n - 1 - coord):
            vec = np.array(fixed + [symbol] + list(suffix), dtype=np.int64)
            encoded = polar_transform_reference(vec, field=field, alpha=alpha)
            scores.append(sum(float(mat[j, int(encoded[j])]) for j in range(n)))
        out[symbol] = _oracle_logsumexp(scores)
    top = _oracle_logsumexp(out)
    if top == -np.inf:
        return out
    return out - top


def compare_sc_vectors(
    production,
    oracle,
    *,
    n: int,
    coordinate: int,
    prefix,
    prob_tol: float = 1e-12,
    log_tol: float = 1e-9,
):
    """Compare one production decision row against the oracle row.

    Returns ``(max_probability_error, max_finite_log_error,
    support_mismatches)``; raises ``AssertionError`` carrying N,
    coordinate, prefix, candidate symbol, both values, and the
    finite/support mismatch summary on any tolerance breach.
    """
    prod = np.asarray(production, dtype=np.float64).ravel()
    ora = np.asarray(oracle, dtype=np.float64).ravel()
    tag = f"N={n} coord={coordinate} prefix={list(prefix)}"
    if prod.shape != ora.shape:
        raise AssertionError(f"SC/oracle shape mismatch: {tag} shapes {prod.shape} vs {ora.shape}")
    if np.isnan(prod).any() or np.isnan(ora).any():
        raise AssertionError(f"SC/oracle NaN: {tag}")
    support = int(np.sum(np.isfinite(prod) != np.isfinite(ora)))
    prob_err = float(np.max(np.abs(np.exp(prod) - np.exp(ora))))
    both = np.isfinite(prod) & np.isfinite(ora)
    log_err = float(np.max(np.abs(prod[both] - ora[both]))) if np.any(both) else 0.0
    if support or prob_err > prob_tol or log_err > log_tol:
        bad = int(np.argmax(np.abs(np.exp(prod) - np.exp(ora))))
        raise AssertionError(
            f"SC/oracle mismatch: {tag} symbol={bad} prod={prod[bad]!r} oracle={ora[bad]!r} "
            f"prob_err={prob_err:.3e} log_err={log_err:.3e} support_mismatches={support}"
        )
    return prob_err, log_err, support
