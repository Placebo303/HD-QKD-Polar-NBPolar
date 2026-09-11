"""Genie Monte Carlo construction over synthetic side information.

Orientation (P3-MATH-01/04): Alice ``U = X G_N``; construction estimates
per-coordinate risks ``h_i = E[-log2 p_i[U_true]]`` and
``e_i = E[1-max p_i]`` where ``p_i`` is the exact SC conditional at the
true prefix ``U_<i`` given Bob side info. The genie path reuses the
accepted Phase 2 ``sc_decode`` with a *full-true* disclosure per TRAIN
sample and reads its ``decision_metrics`` rows. No new traversal core
exists, so the operational ``sc_decode`` API gains no truth argument
and the Phase 2 suite is unchanged. Later-known coordinates do not
alter earlier classic-SC rows (Phase 2 tested), so full-disclosure
rows equal true-prefix conditionals.

Disclosure (P3-MATH-05): construction returns an ordered U-coordinate
list; for count ``K`` Alice discloses actual ``U`` values at the first
``K`` coordinates. ``K`` is a synthetic development control here, not
a reconciliation-cost claim.

All functions take an explicit ``numpy.random.Generator``; seeds are
provenance integers recorded in results (no checksums). No I/O, no
global RNG, no binary ordering import.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral, Real

import numpy as np

from .sc import ImpossibleDisclosedValueError, NumericNonfiniteError, sc_decode
from .synthetic import analytic_erasure_probs, generate_erasure_block, generate_qsc_block
from .transform import polar_transform


@dataclass(frozen=True)
class ConstructionResult:
    """Genie construction outcome (training-only truth, evaluation-safe)."""

    channel: str  # "erasure" or "qsc"
    q: int
    n: int
    param: float  # epsilon or crossover p
    h: np.ndarray  # float64[N] conditional entropy risk in bits
    e: np.ndarray  # float64[N] conditional error risk
    disclosure_order: np.ndarray  # int64[N] permutation, worst first
    n_samples: int  # attempted TRAIN blocks
    n_used: int  # blocks accumulated (attempted minus impossible skips)
    n_impossible: int  # full-disclosure support failures (expect 0)
    train_seed: int  # provenance seed for the caller-owned RNG stream


@dataclass(frozen=True)
class BlockEvalResult:
    """Partial-disclosure SC evaluation over fresh blocks."""

    channel: str
    q: int
    n: int
    param: float
    k: int
    n_blocks: int
    n_exact: int  # U and X both match
    n_initial_error: int  # pointwise argmax(logp_x) != X in >=1 symbol
    n_impossible: int  # ImpossibleDisclosedValueError count
    n_other_failure: int  # any other exception count
    n_nan: int  # NaN/invalid-metric outcomes observed (expect 0)
    fail_indices: tuple  # block indices without exact recovery


def _check_field_q(field, q: int) -> None:
    fq = getattr(field, "q", None)
    if fq != int(q):
        raise ValueError(f"field q {fq} != declared q {q}")


def _check_channel(channel: str) -> str:
    if channel not in ("erasure", "qsc"):
        raise ValueError("channel must be 'erasure' or 'qsc'")
    return channel


def genie_conditionals(logp_x, u_true, *, field, alpha: int = 2) -> np.ndarray:
    """Genie SC conditionals at the true prefix via full-true disclosure.

    Training-only helper: takes Alice truth explicitly, forces every U
    coordinate through the existing ``sc_decode`` known-map, and returns
    the normalized decision rows. Operational evaluation never calls
    this; it discloses only the selected ``K`` subset.
    """
    n = np.asarray(logp_x).shape[0]
    full_pos = np.arange(n, dtype=np.int64)
    full_val = np.asarray(u_true, dtype=np.int64)
    res = sc_decode(logp_x, field=field, alpha=alpha,
                    known_positions=full_pos, known_values=full_val)
    return res.decision_metrics.copy()


def disclosure_order_from_stats(e: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Deterministic worst-first order: descending ``(e, h)``, ties by index."""
    e = np.asarray(e, dtype=np.float64)
    h = np.asarray(h, dtype=np.float64)
    n = e.shape[0]
    return np.array(sorted(range(n), key=lambda i: (-float(e[i]), -float(h[i]), int(i))),
                    dtype=np.int64)


def build_construction(rng, *, field, alpha: int = 2, q: int, n: int,
                       channel: str, param: float, n_samples: int,
                       train_seed: int) -> ConstructionResult:
    """Run genie TRAIN and return risks plus disclosure order."""
    from numbers import Integral as _Int
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be an explicit numpy.random.Generator")
    if isinstance(q, bool) or not isinstance(q, _Int):
        raise TypeError("q must be an integer")
    q, n = int(q), int(n)
    if n < 1 or (n & (n - 1)):
        raise ValueError(f"polar length must be a positive power of two, got {n}")
    _check_field_q(field, q)
    channel = _check_channel(channel)
    if isinstance(param, bool) or not isinstance(param, Real):
        raise TypeError("param must be a real number")
    param = float(param)
    if isinstance(n_samples, bool) or not isinstance(n_samples, _Int) or int(n_samples) < 1:
        raise ValueError("n_samples must be a positive integer")
    n_samples = int(n_samples)
    if isinstance(train_seed, bool) or not isinstance(train_seed, _Int):
        raise TypeError("train_seed must be an integer provenance label")
    train_seed = int(train_seed)

    h_acc = np.zeros(n, dtype=np.float64)
    e_acc = np.zeros(n, dtype=np.float64)
    n_impossible = 0
    n_used = 0
    for _ in range(n_samples):
        if channel == "erasure":
            x, _, logp = generate_erasure_block(rng, q, n, param)
        else:
            x, _, logp = generate_qsc_block(rng, q, n, param)
        u_true = polar_transform(x, field=field, alpha=alpha)
        try:
            cond = genie_conditionals(logp, u_true, field=field, alpha=alpha)
        except ImpossibleDisclosedValueError:
            n_impossible += 1
            continue
        probs = np.exp(cond)
        h_acc += -cond[np.arange(n), u_true] / np.log(2.0)
        e_acc += 1.0 - probs.max(axis=1)
        n_used += 1
    h = h_acc / max(n_used, 1)
    e = e_acc / max(n_used, 1)
    order = disclosure_order_from_stats(e, h)
    return ConstructionResult(channel=channel, q=q, n=n, param=param,
                              h=h, e=e, disclosure_order=order,
                              n_samples=n_samples, n_used=n_used,
                              n_impossible=n_impossible, train_seed=train_seed)


def evaluate_blocks(rng, *, field, alpha: int = 2, q: int, n: int,
                    channel: str, param: float, disclosure_order,
                    k: int, n_blocks: int) -> BlockEvalResult:
    """Decode fresh blocks with the first-``k`` disclosed U values.

    The decoder receives only the disclosed subset; truth outside it is
    never passed. ``ImpossibleDisclosedValueError`` counts as a
    non-exact outcome with an ``impossible`` tag (never silent).
    """
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be an explicit numpy.random.Generator")
    q, n = int(q), int(n)
    if n < 1 or (n & (n - 1)):
        raise ValueError(f"polar length must be a positive power of two, got {n}")
    _check_field_q(field, q)
    channel = _check_channel(channel)
    param = float(param)
    order = np.asarray(disclosure_order, dtype=np.int64).ravel()
    if order.shape != (n,) or set(order.tolist()) != set(range(n)):
        raise ValueError("disclosure_order must be a permutation of 0..N-1")
    if not isinstance(k, Integral) or isinstance(k, bool) or not 0 <= int(k) <= n:
        raise ValueError(f"k must lie in 0..{n}")
    k = int(k)
    if not isinstance(n_blocks, Integral) or isinstance(n_blocks, bool) or int(n_blocks) < 1:
        raise ValueError("n_blocks must be a positive integer")
    n_blocks = int(n_blocks)

    pos = order[:k].astype(np.int64)
    n_exact = 0
    n_init = 0
    n_imposs = 0
    n_other = 0
    n_nan = 0
    fails: list[int] = []
    for b in range(n_blocks):
        if channel == "erasure":
            x, _, logp = generate_erasure_block(rng, q, n, param)
        else:
            x, _, logp = generate_qsc_block(rng, q, n, param)
        if np.isnan(logp).any():
            n_nan += 1
        # pointwise Bob MAP before SC; uniform rows argmax to 0 (smallest index)
        if np.any(np.argmax(logp, axis=1) != x):
            n_init += 1
        u_true = polar_transform(x, field=field, alpha=alpha)
        try:
            res = sc_decode(logp, field=field, alpha=alpha,
                            known_positions=pos, known_values=u_true[pos] if k else [])
        except ImpossibleDisclosedValueError:
            n_imposs += 1
            fails.append(b)
            continue
        except (NumericNonfiniteError, ValueError) as exc:
            msg = str(exc)
            if "NaN" in msg or "nonfinite" in msg or "nan" in msg.lower():
                n_nan += 1
            n_other += 1
            fails.append(b)
            continue
        if np.isnan(res.decision_metrics).any():
            n_nan += 1
            fails.append(b)
            continue
        if np.array_equal(res.u_hat, u_true) and np.array_equal(res.x_hat, x):
            n_exact += 1
        else:
            fails.append(b)
    return BlockEvalResult(channel=channel, q=q, n=n, param=param, k=k,
                           n_blocks=n_blocks, n_exact=n_exact,
                           n_initial_error=n_init, n_impossible=n_imposs,
                           n_other_failure=n_other, n_nan=n_nan,
                           fail_indices=tuple(fails))


def spearman_rank_corr(a, b) -> float:
    """Spearman rank correlation with average-tie ranks (no scipy)."""
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    if a.shape != b.shape or a.size < 2:
        raise ValueError("inputs must be equal-length vectors with size>=2")

    def _avg_rank(v: np.ndarray) -> np.ndarray:
        order = np.argsort(v, kind="mergesort")
        r = np.empty(v.shape[0], dtype=np.float64)
        i = 0
        while i < v.shape[0]:
            j = i
            while j + 1 < v.shape[0] and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = 0.5 * (i + j)
            for t in range(i, j + 1):
                r[order[t]] = avg
            i = j + 1
        return r

    ra, rb = _avg_rank(a), _avg_rank(b)
    ma, mb = float(ra.mean()), float(rb.mean())
    num = float(((ra - ma) * (rb - mb)).sum())
    den = float(np.sqrt(((ra - ma) ** 2).sum() * ((rb - mb) ** 2).sum()))
    if den == 0.0:
        return 0.0
    return num / den


def topk_overlap(order_a, order_b, k: int) -> float:
    """Fraction of shared entries among the first-``k`` of two orders."""
    a = list(np.asarray(order_a).ravel().tolist())
    b = list(np.asarray(order_b).ravel().tolist())
    if not isinstance(k, Integral) or isinstance(k, bool) or not 0 < int(k) <= len(a):
        raise ValueError("k must lie in 1..N")
    k = int(k)
    return len(set(a[:k]).intersection(set(b[:k]))) / float(k)


def analytic_order(eps: float, n: int) -> np.ndarray:
    """Worst-first analytic order (descending erasure prob, ties by index)."""
    z = analytic_erasure_probs(eps, n)
    return np.array(sorted(range(n), key=lambda i: (-float(z[i]), int(i))), dtype=np.int64)


def resolvable_rank_corr(e, z, *, min_n: int = 20) -> tuple:
    """Spearman rank correlation over the finite-sample-resolvable subset.

    R1-D1: finite TRAIN quantizes ~187/256 good coordinates to exactly
    ``e == 0``; their internal order is quantization noise, so the
    full-vector rank mixes noise with signal. The meaningful rank signal
    is over coordinates with ``e > 0`` (>=1 observed risk event). Returns
    ``(rho, n)``. Raises ``ValueError`` when fewer than ``min_n``
    coordinates resolve: an unresolvable gate must fail loudly, never
    silently fall back to the noise-dominated full vector.
    """
    e = np.asarray(e, dtype=np.float64).ravel()
    z = np.asarray(z, dtype=np.float64).ravel()
    if e.shape != z.shape:
        raise ValueError("e and z must share shape")
    if isinstance(min_n, bool) or not isinstance(min_n, Integral) or int(min_n) < 2:
        raise ValueError("min_n must be an integer >= 2")
    mask = e > 0
    n = int(np.sum(mask))
    if n < int(min_n):
        raise ValueError(f"only {n} resolvable coordinates, need >= {int(min_n)}")
    return float(spearman_rank_corr(e[mask], z[mask])), n


def analytic_construction(*, field, alpha: int = 2, q: int, n: int,
                          channel: str, param: float) -> ConstructionResult:
    """Exact erasure baseline: disclosure order with no TRAIN sampling.

    Closed form for q-ary erasure: an erased row (prob ``z``) is uniform,
    so ``h = z*log2(q)`` and ``e = z*(1-1/q)`` exactly, and the order
    equals :func:`analytic_order`. ``train_seed=-1`` and zero sample
    counts record that no TRAIN stream was consumed. Erasure only: QSC
    has no closed-form oracle here (raises ``ValueError``).
    """
    if not isinstance(q, Integral) or isinstance(q, bool):
        raise TypeError("q must be an integer")
    q, n = int(q), int(n)
    if n < 1 or (n & (n - 1)):
        raise ValueError(f"polar length must be a positive power of two, got {n}")
    _check_field_q(field, q)
    if channel != "erasure":
        raise ValueError("analytic_construction is an erasure-channel oracle only")
    if isinstance(param, bool) or not isinstance(param, Real):
        raise TypeError("param must be a real number")
    param = float(param)
    if not 0.0 <= param <= 1.0:
        raise ValueError(f"epsilon must lie in [0, 1], got {param}")
    z = analytic_erasure_probs(param, n)
    h = z * float(np.log2(float(q)))
    e = z * (1.0 - 1.0 / float(q))
    return ConstructionResult(channel="erasure", q=q, n=n, param=param,
                              h=h, e=e, disclosure_order=analytic_order(param, n),
                              n_samples=0, n_used=0, n_impossible=0, train_seed=-1)


def failure_summary(result: BlockEvalResult) -> dict:
    """Explicit decode-failure accounting (R1-D2, prospective prereg).

    An ``ImpossibleDisclosedValueError`` after a wrong earlier undisclosed
    prefix is one failed decode and one non-exact block: reported
    separately as its own decode-failure class but included in the same
    total failure count. The only structural invariant is
    exact + failed == attempted; category overlaps (e.g. NaN paths) are
    preserved, never forced into a false partition.
    """
    n_failed = int(result.n_blocks) - int(result.n_exact)
    if n_failed < 0 or len(tuple(result.fail_indices)) != n_failed:
        raise ValueError("BlockEvalResult violates exact+failed==attempted")
    if int(result.n_impossible) > n_failed:
        raise ValueError("impossible count exceeds total failures")
    return {
        "n_blocks": int(result.n_blocks),
        "n_exact": int(result.n_exact),
        "n_failed_total": n_failed,
        "n_impossible": int(result.n_impossible),
        "n_other_failure": int(result.n_other_failure),
        "n_nan": int(result.n_nan),
        "n_initial_error": int(result.n_initial_error),
        "fail_indices": tuple(result.fail_indices),
    }
