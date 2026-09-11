"""Independent tiny-N exhaustive oracle for the P3 empirical SC interface.

Independence: imports only the accepted Phase 1 dense reference
(``polar_transform_reference``) plus ``numpy``/``itertools``. Never
imports production SC recursion, minus/plus helpers, partial-sum
helpers, validation, normalization, decision logic (``sc.py``), the
Phase 2 oracle (``oracle.py``), the channel sampler, or any artifact
loader. Block scores are literal ``sum_j logp_x[j, X_j]`` with
``X = polar_transform_reference(U)``; conditionals aggregate scores by
candidate ``U_i`` with a standalone max-subtraction logsumexp, then
normalize.

Math: the joint over a block factors as a product of per-position
``P_high`` rows, so log-scores add. A direct probability-product
implementation was tried and rejected: products of ``N`` tiny rows
underflow below ~1e-308 while the log-sum stays finite (see
``EXPLORATION_NOTES.md`` P3-A19); the literal log-sum below is the
retained reference arithmetic.

The oracle takes an explicit candidate prefix, so tests evaluate
conditionals at decoded, forced, or adversarial prefixes. Enumeration
is exponential and guarded to tiny domains (at most 4096 full
candidates: GF4 N<=4, GF32 N<=2). Not a decoder.
"""

from __future__ import annotations

import itertools
from numbers import Integral

import numpy as np

from .transform import polar_transform_reference

MAX_ORACLE_CANDIDATES = 4096

__all__ = [
    "MAX_ORACLE_CANDIDATES",
    "empirical_block_score",
    "empirical_oracle_sc_metric",
]


def _standalone_logsumexp(values) -> float:
    """Max-subtraction logsumexp; all-``-inf`` maps to ``-inf``."""
    flat = np.asarray(values, dtype=np.float64).ravel()
    peak = float(np.max(flat))
    if peak == -np.inf:
        return -np.inf
    if not np.isfinite(peak):
        raise ValueError("empirical oracle failure: nonfinite aggregate")
    return float(peak + np.log(float(np.sum(np.exp(flat - peak)))))


def _check_logp(logp_x, field, alpha: int):
    q = getattr(field, "q", None)
    if isinstance(q, bool) or not isinstance(q, Integral) or int(q) <= 0:
        raise ValueError("empirical oracle contract: field must expose positive integer q")
    q = int(q)
    if isinstance(alpha, bool) or not isinstance(alpha, Integral):
        raise ValueError("empirical oracle contract: alpha must be an integer symbol")
    alpha = int(alpha)
    if not 0 <= alpha < q:
        raise ValueError(
            f"empirical oracle contract: alpha must lie in 0..{q - 1}"
        )
    mat = np.asarray(logp_x)
    if mat.dtype.kind == "b" or mat.ndim != 2:
        raise ValueError("empirical oracle contract: logp_x must be a 2-D float array")
    try:
        mat = mat.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"empirical oracle contract: logp_x must convert to float64 ({exc})"
        ) from exc
    n, qq = mat.shape
    if qq != q or n < 1 or (n & (n - 1)):
        raise ValueError("empirical oracle contract: logp_x must have shape (2**k, field.q)")
    if np.isnan(mat).any() or np.isposinf(mat).any():
        raise ValueError("empirical oracle contract: logp_x must not contain NaN or +inf")
    if np.isneginf(mat).all(axis=1).any():
        raise ValueError("empirical oracle contract: every logp_x row needs finite support")
    if q**n > MAX_ORACLE_CANDIDATES:
        raise ValueError(
            f"empirical oracle contract: q**N={q ** n} exceeds tiny cap "
            f"{MAX_ORACLE_CANDIDATES}"
        )
    return mat, n, q, alpha


def _check_prefix(prefix, n: int, q: int) -> list:
    arr = np.asarray(prefix)
    if arr.dtype.kind == "b" or arr.ndim != 1:
        raise ValueError("empirical oracle contract: prefix must be a 1-D integer vector")
    if arr.size >= n:
        raise ValueError("empirical oracle contract: prefix length must be below N")
    out: list[int] = []
    for pos, value in enumerate(arr.tolist()):
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise ValueError(
                f"empirical oracle contract: prefix[{pos}] must be an integer symbol"
            )
        if not 0 <= int(value) < q:
            raise ValueError(
                f"empirical oracle contract: prefix[{pos}] must lie in 0..{q - 1}"
            )
        out.append(int(value))
    return out


def empirical_block_score(logp_x, u_candidate, *, field, alpha: int = 2) -> float:
    """Literal block score ``sum_j logp_x[j, X_j]`` for one U candidate."""
    mat, n, q, alpha = _check_logp(logp_x, field, alpha)
    full = _check_prefix(u_candidate, n + 1, q)
    if len(full) != n:
        raise ValueError("empirical oracle contract: candidate must hold exactly N symbols")
    vec = np.asarray(full, dtype=np.int64)
    coded = polar_transform_reference(vec, field=field, alpha=alpha)
    total = 0.0
    for j in range(n):
        total += float(mat[j, int(coded[j])])
    return total


def empirical_oracle_sc_metric(logp_x, prefix, *, field, alpha: int = 2) -> np.ndarray:
    """Exhaustive conditional for ``U[len(prefix)]`` given ``prefix``.

    Every suffix assignment is enumerated, each complete candidate is
    scored with the literal block sum, scores are aggregated per
    candidate symbol with the standalone logsumexp, and the row is
    normalized. An all-``-inf`` row reports an impossible prefix.
    """
    mat, n, q, alpha = _check_logp(logp_x, field, alpha)
    fixed = _check_prefix(prefix, n, q)
    coord = len(fixed)
    rows = np.empty(q, dtype=np.float64)
    for symbol in range(q):
        acc: list[float] = []
        for suffix in itertools.product(range(q), repeat=n - 1 - coord):
            vec = np.array(fixed + [symbol] + list(suffix), dtype=np.int64)
            coded = polar_transform_reference(vec, field=field, alpha=alpha)
            total = 0.0
            for j in range(n):
                total += float(mat[j, int(coded[j])])
            acc.append(total)
        rows[symbol] = _standalone_logsumexp(acc)
    peak = _standalone_logsumexp(rows)
    if peak == -np.inf:
        return rows
    return rows - peak
