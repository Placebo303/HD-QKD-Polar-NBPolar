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

Vectorized backend (Stage B addition): the literal function above stays
exactly as accepted. ``empirical_oracle_sc_metric_vectorized`` evaluates
the same exhaustive conditional with the same standalone log-sum
arithmetic, but enumerates candidates in mixed-radix order (U_0 slowest)
once, applies the dense transform to the whole candidate batch with
:func:`batch_polar_transform_reference`, and evaluates each conditional
as a contiguous slice logsumexp. It carries its own, larger candidate cap
(``MAX_VECTOR_ORACLE_CANDIDATES``, q**N <= 1048576 = GF32 N=4) and never
changes the default behavior or the 4096 cap of the literal callers.
"""

from __future__ import annotations

import itertools
from numbers import Integral

import numpy as np

from .transform import polar_transform_reference

MAX_ORACLE_CANDIDATES = 4096
MAX_VECTOR_ORACLE_CANDIDATES = 1 << 20  # 1048576 == GF32 N=4

__all__ = [
    "MAX_ORACLE_CANDIDATES",
    "MAX_VECTOR_ORACLE_CANDIDATES",
    "batch_polar_transform_reference",
    "empirical_block_score",
    "empirical_oracle_conditionals_vectorized",
    "empirical_oracle_sc_metric",
    "empirical_oracle_sc_metric_vectorized",
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


def _check_logp(logp_x, field, alpha: int, *, max_candidates: int = MAX_ORACLE_CANDIDATES):
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
    if q**n > max_candidates:
        raise ValueError(
            f"empirical oracle contract: q**N={q ** n} exceeds tiny cap "
            f"{max_candidates}"
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


def empirical_oracle_sc_metric(
    logp_x,
    prefix,
    *,
    field,
    alpha: int = 2,
    max_candidates: int = MAX_ORACLE_CANDIDATES,
) -> np.ndarray:
    """Exhaustive conditional for ``U[len(prefix)]`` given ``prefix``.

    Every suffix assignment is enumerated, each complete candidate is
    scored with the literal block sum, scores are aggregated per
    candidate symbol with the standalone logsumexp, and the row is
    normalized. An all-``-inf`` row reports an impossible prefix.

    ``max_candidates`` defaults to the accepted tiny cap 4096; tests may
    pass the vector cap explicitly to compare the literal arithmetic
    against the vectorized backend outside the default domain. Existing
    callers keep the unchanged 4096 guard.
    """
    mat, n, q, alpha = _check_logp(logp_x, field, alpha, max_candidates=max_candidates)
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


def _dense_generator(field, alpha: int, n: int) -> np.ndarray:
    """Literal Kronecker-power generator matrix, exactly as the reference.

    Independent copy of the accepted dense construction (the frozen
    ``transform.py`` module is never modified): ``G_1 = [[1, 0],
    [alpha, 1]]`` and ``G_{2k} = [[G_k, 0], [alpha*G_k, G_k]]``.
    """
    q = field.q
    a = field.add(alpha, 0)
    mul_table = np.empty((q, q), dtype=np.int64)
    for i in range(q):
        for j in range(q):
            mul_table[i, j] = field.mul(i, j)
    gen = np.array([[1, 0], [a, 1]], dtype=np.int64)
    while gen.shape[0] < n:
        k = gen.shape[0]
        big = np.empty((2 * k, 2 * k), dtype=np.int64)
        big[:k, :k] = gen
        big[:k, k:] = 0
        big[k:, :k] = mul_table[a, gen]
        big[k:, k:] = gen
        gen = big
    return gen


def batch_polar_transform_reference(vectors, *, field, alpha: int = 2) -> np.ndarray:
    """Dense row-wise ``v G_N`` for a batch of candidate rows.

    ``vectors`` is an integer ``(M, N)`` array; the result is the int64
    ``(M, N)`` matrix of source-to-coded symbols. Row ``m`` of the result
    equals ``polar_transform_reference(vectors[m])`` (tested). Used only
    by the vectorized oracle to transform the whole candidate
    enumeration once.
    """
    q = getattr(field, "q", None)
    if isinstance(q, bool) or not isinstance(q, Integral) or int(q) <= 0:
        raise ValueError("empirical oracle contract: field must expose a positive integer q")
    q = int(q)
    arr = np.asarray(vectors)
    if arr.dtype.kind == "b":
        raise TypeError("empirical oracle contract: vectors must hold integers, got boolean input")
    if arr.ndim != 2:
        raise ValueError(
            f"empirical oracle contract: vectors must be 2-D (M,N), got shape {arr.shape}"
        )
    n = arr.shape[1]
    if n < 1 or (n & (n - 1)):
        raise ValueError("empirical oracle contract: vector length N must be a positive power of two")
    if arr.size and arr.dtype.kind not in "iu":
        raise TypeError("empirical oracle contract: vectors must hold integers")
    cand = arr.astype(np.int64, copy=True)
    if cand.size and (cand.min() < 0 or cand.max() >= q):
        raise ValueError(f"empirical oracle contract: vectors entries must lie in 0..{q - 1}")
    gen = _dense_generator(field, alpha, n)
    mul_table = np.empty((q, q), dtype=np.int64)
    for i in range(q):
        for j in range(q):
            mul_table[i, j] = field.mul(i, j)
    out = np.empty(cand.shape, dtype=np.int64)
    for j in range(n):
        acc = np.zeros(cand.shape[0], dtype=np.int64)
        for i in range(n):
            gi = int(gen[i, j])
            if gi:
                acc ^= mul_table[cand[:, i], gi]
        out[:, j] = acc
    return out


def _rows_logsumexp(mat: np.ndarray) -> np.ndarray:
    """Vectorized standalone logsumexp over axis 1; all-``-inf`` stays ``-inf``."""
    peaks = mat.max(axis=1)
    out = np.full(mat.shape[0], -np.inf, dtype=np.float64)
    finite = np.isfinite(peaks)
    if finite.any():
        sub = mat[finite]
        shifted = sub - peaks[finite, None]
        out[finite] = peaks[finite] + np.log(np.exp(shifted).sum(axis=1))
    return out


def _vectorized_scores(mat: np.ndarray, n: int, q: int, *, field, alpha: int):
    """Joint candidate scores over the full mixed-radix enumeration.

    Candidate index ``m`` encodes ``U_j = (m // q**(n-1-j)) % q``
    (``U_0`` slowest), matching the literal ``fixed + [symbol] + suffix``
    enumeration order. Scores are literal ``sum_j logp_x[j, X_j]``.
    """
    total = q**n
    idx = np.arange(total, dtype=np.int64)
    cand = np.empty((total, n), dtype=np.int64)
    for i in range(n):
        cand[:, i] = (idx // q ** (n - 1 - i)) % q
    coded = batch_polar_transform_reference(cand, field=field, alpha=alpha)
    scores = np.zeros(total, dtype=np.float64)
    for j in range(n):
        scores += mat[j, coded[:, j]]
    return scores


def empirical_oracle_conditionals_vectorized(
    logp_x,
    prefixes,
    *,
    field,
    alpha: int = 2,
    max_candidates: int = MAX_VECTOR_ORACLE_CANDIDATES,
) -> np.ndarray:
    """Vectorized exhaustive conditionals for a batch of prefixes.

    Returns a ``(len(prefixes), q)`` array: row ``k`` is the conditional
    for ``U[len(prefixes[k])]`` given ``prefixes[k]``, identical (same
    math, same normalization, all-``-inf`` preserved) to
    :func:`empirical_oracle_sc_metric`. The joint candidate scores are
    computed once; each prefix then selects one contiguous slice of the
    mixed-radix enumeration.

    Same failure contract as the literal oracle, with its own candidate
    cap (default ``MAX_VECTOR_ORACLE_CANDIDATES``).
    """
    mat, n, q, alpha = _check_logp(logp_x, field, alpha, max_candidates=max_candidates)
    try:
        entries = list(prefixes)
    except TypeError as exc:
        raise ValueError(
            "empirical oracle contract: prefixes must be a sequence of prefix vectors"
        ) from exc
    fixed_list = [_check_prefix(entry, n, q) for entry in entries]
    scores = _vectorized_scores(mat, n, q, field=field, alpha=alpha)
    out = np.empty((len(fixed_list), q), dtype=np.float64)
    for row, fixed in enumerate(fixed_list):
        coord = len(fixed)
        step = q ** (n - 1 - coord)
        base = 0
        for i, value in enumerate(fixed):
            base += value * q ** (n - 1 - i)
        rows = _rows_logsumexp(scores[base : base + q * step].reshape(q, step))
        peak = _standalone_logsumexp(rows)
        out[row] = rows if peak == -np.inf else rows - peak
    return out


def empirical_oracle_sc_metric_vectorized(
    logp_x,
    prefix,
    *,
    field,
    alpha: int = 2,
    max_candidates: int = MAX_VECTOR_ORACLE_CANDIDATES,
) -> np.ndarray:
    """Vectorized exhaustive conditional for ``U[len(prefix)]`` given ``prefix``.

    Thin single-prefix wrapper over
    :func:`empirical_oracle_conditionals_vectorized`.
    """
    return empirical_oracle_conditionals_vectorized(
        logp_x, [prefix], field=field, alpha=alpha, max_candidates=max_candidates
    )[0]
