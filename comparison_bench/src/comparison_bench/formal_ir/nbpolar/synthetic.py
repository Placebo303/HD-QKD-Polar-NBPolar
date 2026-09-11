"""q-ary synthetic side-information generators + analytic erasure oracle.

Source orientation (P3-MATH-01): Alice source symbols ``X`` uniform in
``0..q-1``; Bob observes side information ``Y``; decoder input is
``logp_x[j,a] = ln P(X_j=a | Y_j)`` normalized to logsumexp 0.
Alice transforms ``U = X G_N`` (frozen natural-order transform).

Erasure (P3-MATH-02): with prob ``1-eps`` ``Y=X`` (one-hot posterior);
else ``Y=-1`` marker (uniform posterior). QSC (P3-MATH-03): ``Y=X``
w.p. ``1-p`` else uniform over other symbols; posterior ``1-p`` at
``Y`` and ``p/(q-1)`` elsewhere. Endpoint ``p=(q-1)/q`` gives the
uniform posterior and is supported.

All generators take an explicit ``numpy.random.Generator``; no global
RNG, no I/O. ``y`` uses ``-1`` for the erasure marker (distinct from
every valid symbol); QSC ``y`` always lies in ``0..q-1``.
"""

from __future__ import annotations

from numbers import Integral, Real

import numpy as np

# Frozen stream seeds: provenance only, never used as hidden global state.
UNIT_SEED = 2026091200
TRAIN_SEED = 2026091201
DEV_SEED = 2026091202
EVAL_SEED = 2026091203


def _check_q(q: int) -> int:
    if isinstance(q, bool) or not isinstance(q, Integral):
        raise TypeError("q must be an integer")
    q = int(q)
    if q < 2:
        raise ValueError("q must be at least 2")
    return q


def _check_N(n) -> int:
    if isinstance(n, bool) or not isinstance(n, Integral):
        raise TypeError("N must be an integer")
    n = int(n)
    if n < 1 or (n & (n - 1)):
        raise ValueError(f"polar length must be a positive power of two, got {n}")
    return n


def _check_rng(rng) -> None:
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be an explicit numpy.random.Generator (no hidden global RNG)")


def _check_prob(value, name: str, low: float, high: float) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    value = float(value)
    if not low <= value <= high:
        raise ValueError(f"{name} must lie in [{low}, {high}], got {value}")
    return value


def generate_erasure_block(rng, q: int, n: int, epsilon: float):
    """One q-ary erasure block: ``(x, y, logp_x)``.

    ``x`` int64[N] uniform; ``y`` int64[N] with ``-1`` at erasures;
    ``logp_x`` float64[N,q] normalized (one-hot at ``x`` when observed,
    ``-ln q`` uniform when erased).
    """
    _check_rng(rng)
    q = _check_q(q)
    n = _check_N(n)
    epsilon = _check_prob(epsilon, "epsilon", 0.0, 1.0)
    x = rng.integers(0, q, size=n).astype(np.int64)
    erased = rng.random(n) < epsilon
    y = np.where(erased, -1, x).astype(np.int64)
    logp = np.empty((n, q), dtype=np.float64)
    if np.any(erased):
        logp[erased] = -np.log(q)
    for j in np.where(~erased)[0]:
        logp[j, :] = -np.inf
        logp[j, int(x[j])] = 0.0
    return x, y, logp


def generate_qsc_block(rng, q: int, n: int, p: float):
    """One q-ary symmetric block: ``(x, y, logp_x)``.

    ``y=x`` w.p. ``1-p`` else uniform over the other ``q-1`` symbols.
    Posterior is ``1-p`` at ``y`` and ``p/(q-1)`` elsewhere (natural
    logs, normalized). ``p=(q-1)/q`` yields the uniform posterior.
    """
    _check_rng(rng)
    q = _check_q(q)
    n = _check_N(n)
    p = _check_prob(p, "p", 0.0, float(q - 1) / float(q))
    x = rng.integers(0, q, size=n).astype(np.int64)
    y = x.copy()
    flip = rng.random(n) < p
    for j in np.where(flip)[0]:
        # uniform over symbols != x[j] via one extra integer draw
        r = int(rng.integers(0, q - 1))
        y[j] = r if r < int(x[j]) else r + 1
    logp = np.empty((n, q), dtype=np.float64)
    if p == 0.0:
        for j in range(n):
            logp[j, :] = -np.inf
            logp[j, int(y[j])] = 0.0
    elif p == float(q - 1) / float(q):
        logp[:, :] = -np.log(q)
    else:
        lo = float(np.log(p / (q - 1)))
        hi = float(np.log(1.0 - p))
        logp[:, :] = lo
        logp[np.arange(n), y] = hi
    return x, y, logp


def analytic_erasure_probs(epsilon: float, n: int) -> np.ndarray:
    """Analytic q-ary erasure synthetic probs in natural U order.

    Recursion ``e_minus=2e-e^2``, ``e_plus=e^2`` applied per element:
    each entry ``e`` expands to consecutive ``[minus(e), plus(e)]``,
    matching the accepted transform's natural ``G_N`` order (index 0 is
    the all-minus coordinate). Preserves the mean exactly; endpoints
    0/1 map to all-0/all-1.
    """
    epsilon = _check_prob(epsilon, "epsilon", 0.0, 1.0)
    n = _check_N(n)
    vec = np.array([float(epsilon)], dtype=np.float64)
    while vec.shape[0] < n:
        out = np.empty(2 * vec.shape[0], dtype=np.float64)
        for j, e in enumerate(vec):
            out[2 * j] = 2.0 * e - e * e
            out[2 * j + 1] = e * e
        vec = out
    return vec
