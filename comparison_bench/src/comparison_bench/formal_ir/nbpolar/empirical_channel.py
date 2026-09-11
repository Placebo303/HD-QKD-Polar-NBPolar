"""Phase 4-P3 synthetic empirical channel: model-sampled Bob/Alice blocks + P1 metrics.

Synthetic Stage A/A2 only: all probability tables are caller-injected
 NumPy arrays (hand-built or seeded). No artifact, parquet, TTBin,
 real-frame, DEV/EVAL, or sibling read exists in this module.

Model-sampled source (TASK_PACKET Stage A, high-symbol level)::

    B ~ p_b                      (Bob full labels, shape (N,) or (F,N))
    X_high[j] ~ P_high(. | B[j]) (Alice high symbols, same shape)
    P1 metric[j,a] = P_high[a | B[j]]   (Bob + table only)

The full 10-bit production mapping (``A_full = low + 32*high``) reduces
to this high level by marginalizing the low symbol; the generic
``(q_high, q_low)`` split/combine helpers below mirror
``prior.split_symbol/combine_symbol`` exactly at ``(32,32)`` and
degenerate to direct sampling at ``q_low=1``. Packing round-trips are
tested against ``prior``; the operational gather never takes Alice
truth.

Truth isolation: the operational builder signature is
``build_p1_metrics(bob, p1_table)`` -- no Alice/truth/U argument exists.
Alice truth leaves the sampler only toward frozen disclosure maps and
scoring in tests/diagnostics, never toward the metric builder or SC
likelihood.

Canonical representation (P3-A14): probabilities are adapter-internal;
the decoder-facing canonical form is the normalized natural-log row
(``logsumexp == 0``, exact zero as ``-inf``) owned by the accepted
``prior.probs_to_symbol_metric`` converter. This module returns
probability rows; conversion ownership is documented, never duplicated.

NumPy + stdlib only. No local imports: no SC/oracle/artifact coupling
by construction. All failures raise ``TypeError``/``ValueError`` with
the ``channel contract:`` / ``seed contract:`` prefix.
"""

from __future__ import annotations

from numbers import Integral

import numpy as np

__all__ = [
    "NORM_TOL",
    "Q_HIGH_PROD",
    "Q_LOW_PROD",
    "N_LABELS_PROD",
    "P3_UNIT_SEED",
    "P3_TRAIN_SEED",
    "P3_DIAG_SEED",
    "BANNED_SEEDS",
    "make_rng",
    "split_labels",
    "combine_labels",
    "derive_p1_from_full",
    "sample_bob",
    "sample_high_given_bob",
    "sample_full_block",
    "build_p1_metrics",
    "build_p1_metrics_literal",
]

NORM_TOL = 1e-12
Q_HIGH_PROD = 32
Q_LOW_PROD = 32
N_LABELS_PROD = 1024

# Frozen synthetic seeds: selected before sampling, disjoint from every
# predecessor stream. Phase 3 seeds 2026091200..1213 and all earlier
# official seeds (1200..1203 unit/train/dev/eval, 20260911 sc-oracle,
# 20260930 prior-adapter) are banned and refused by make_rng.
P3_UNIT_SEED = 2026091314
P3_TRAIN_SEED = 2026091315
P3_DIAG_SEED = 2026091316
BANNED_SEEDS = frozenset(range(2026091200, 2026091214))


def make_rng(seed: int) -> np.random.Generator:
    """Return ``default_rng(seed)``; banned predecessor seeds are refused."""
    if isinstance(seed, bool) or not isinstance(seed, Integral):
        raise TypeError(f"seed contract: seed must be an integer, got {seed!r}")
    seed = int(seed)
    if seed in BANNED_SEEDS:
        raise ValueError(f"seed contract: seed {seed} is a banned predecessor stream")
    return np.random.default_rng(seed)


def _check_q(value, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"channel contract: {name} must be an integer, got {value!r}")
    value = int(value)
    if value < 1:
        raise ValueError(f"channel contract: {name} must be >= 1, got {value}")
    return value


def _check_p_b(p_b) -> np.ndarray:
    arr = np.asarray(p_b)
    if arr.dtype.kind == "b":
        raise TypeError("channel contract: p_b must hold numbers, got boolean input")
    if arr.ndim != 1:
        raise ValueError(f"channel contract: p_b must be 1D, got shape {arr.shape}")
    if arr.shape[0] < 1:
        raise ValueError("channel contract: p_b must hold at least one Bob label")
    try:
        vec = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"channel contract: p_b must be numeric ({exc})") from exc
    if not np.isfinite(vec).all():
        raise ValueError("channel contract: p_b must be finite")
    if (vec < 0).any():
        raise ValueError("channel contract: p_b must be non-negative")
    if abs(float(vec.sum()) - 1.0) > NORM_TOL:
        raise ValueError(
            "channel contract: p_b must sum to 1 within 1e-12, "
            f"got {float(vec.sum())!r}"
        )
    return vec


def _check_p1(p1_table) -> np.ndarray:
    arr = np.asarray(p1_table)
    if arr.dtype.kind == "b":
        raise TypeError("channel contract: p1_table must hold numbers, got boolean input")
    if arr.ndim != 2:
        raise ValueError(
            f"channel contract: p1_table must be [high,Bob], got shape {arr.shape}"
        )
    try:
        mat = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"channel contract: p1_table must be numeric ({exc})") from exc
    if mat.shape[0] < 2 or mat.shape[1] < 1:
        raise ValueError(
            f"channel contract: p1_table must be (q>=2, n_b>=1), got shape {mat.shape}"
        )
    if not np.isfinite(mat).all():
        raise ValueError("channel contract: p1_table must be finite")
    if (mat < 0).any():
        raise ValueError("channel contract: p1_table must be non-negative")
    dev = float(np.abs(mat.sum(axis=0) - 1).max())
    if dev > NORM_TOL:
        raise ValueError(
            "channel contract: p1_table columns must sum to 1 within 1e-12, "
            f"max deviation {dev:.3e}"
        )
    return mat


def _check_f_full(f_full, q_high: int, q_low: int) -> np.ndarray:
    arr = np.asarray(f_full)
    if arr.dtype.kind == "b":
        raise TypeError("channel contract: f_full must hold numbers, got boolean input")
    want = (int(q_high) * int(q_low),)
    if arr.ndim != 2 or arr.shape[0] != want[0] or arr.shape[1] < 1:
        raise ValueError(
            "channel contract: f_full must be [A_full,Bob] "
            f"({want[0]},n_b), got shape {arr.shape}"
        )
    try:
        mat = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"channel contract: f_full must be numeric ({exc})") from exc
    if not np.isfinite(mat).all():
        raise ValueError("channel contract: f_full must be finite")
    if (mat < 0).any():
        raise ValueError("channel contract: f_full must be non-negative")
    dev = float(np.abs(mat.sum(axis=0) - 1).max())
    if dev > NORM_TOL:
        raise ValueError(
            "channel contract: f_full columns must sum to 1 within 1e-12, "
            f"max deviation {dev:.3e}"
        )
    return mat


def _check_rng(rng) -> None:
    if not isinstance(rng, np.random.Generator):
        raise TypeError(
            "channel contract: rng must be an explicit numpy.random.Generator"
        )


def _check_len(n, name: str) -> int:
    if isinstance(n, bool) or not isinstance(n, Integral):
        raise TypeError(f"channel contract: {name} must be an integer, got {n!r}")
    n = int(n)
    if n < 1:
        raise ValueError(f"channel contract: {name} must be >= 1, got {n}")
    return n


def split_labels(a_full, q_low: int):
    """Split full labels ``s = low + q_low*high`` into ``(low, high)``.

    Mirrors ``prior.split_symbol`` at ``q_low=32`` (``low=s&31``,
    ``high=(s>>5)&31``); ``q_low=1`` degenerates to ``(0, s)`` direct mode.
    """
    q_low = _check_q(q_low, "q_low")
    arr = np.asarray(a_full)
    if arr.dtype.kind == "b":
        raise TypeError("channel contract: labels must hold integers, got boolean input")
    if arr.size and arr.dtype.kind not in "iu":
        # object/float labels are rejected loudly, never truncated
        raise TypeError(
            f"channel contract: labels must hold integers, got dtype {arr.dtype}"
        )
    vec = arr.astype(np.int64, copy=False)
    if vec.size and vec.min() < 0:
        raise ValueError("channel contract: label must be >= 0")
    # ponytail: divmod is the whole packing; no per-symbol loop needed
    return (vec % q_low).astype(np.int64), (vec // q_low).astype(np.int64)


def combine_labels(low, high, q_low: int):
    """Combine ``(low, high)`` into full labels ``low + q_low*high``."""
    q_low = _check_q(q_low, "q_low")
    lo = np.asarray(low)
    hi = np.asarray(high)
    if lo.dtype.kind == "b" or hi.dtype.kind == "b":
        raise TypeError("channel contract: labels must hold integers, got boolean input")
    if lo.shape != hi.shape:
        raise ValueError(
            f"channel contract: low shape {lo.shape} != high shape {hi.shape}"
        )
    if lo.size and (lo.dtype.kind not in "iu" or hi.dtype.kind not in "iu"):
        raise TypeError("channel contract: labels must hold integers")
    lo64 = lo.astype(np.int64, copy=False)
    hi64 = hi.astype(np.int64, copy=False)
    if lo64.size and (lo64.min() < 0 or lo64.max() >= q_low):
        raise ValueError(f"channel contract: low entries must lie in 0..{q_low - 1}")
    if hi64.size and hi64.min() < 0:
        raise ValueError("channel contract: high entries must be >= 0")
    return (lo64 + q_low * hi64).astype(np.int64)


def derive_p1_from_full(f_full, q_high: int, q_low: int) -> np.ndarray:
    """Marginalize ``f_full[A,B]`` over the low symbol to ``p1[high,B]``.

    Row-major layout ``A = low + q_low*high`` matches the frozen
    ``prior.derive_p1`` reshape at ``(32,32)``.
    """
    q_high = _check_q(q_high, "q_high")
    q_low = _check_q(q_low, "q_low")
    mat = _check_f_full(f_full, q_high, q_low)
    n_b = mat.shape[1]
    cube = mat.reshape(int(q_high), int(q_low), n_b)
    return cube.sum(axis=1)


def sample_bob(rng, p_b, n: int) -> np.ndarray:
    """Sample ``n`` Bob labels from ``p_b`` with an explicit RNG."""
    _check_rng(rng)
    vec = _check_p_b(p_b)
    n = _check_len(n, "n")
    edges = np.cumsum(vec)
    draws = rng.random(n)
    return np.searchsorted(edges, draws, side="left").astype(np.int64)


def sample_high_given_bob(rng, bob, p1_table) -> np.ndarray:
    """Sample one Alice high symbol per Bob label from ``p1_table`` columns."""
    _check_rng(rng)
    mat = _check_p1(p1_table)
    bobs = np.asarray(bob)
    if bobs.dtype.kind == "b":
        raise TypeError("channel contract: bob must hold integers, got boolean input")
    if bobs.ndim != 1:
        raise ValueError(f"channel contract: bob must be 1D, got shape {bobs.shape}")
    if bobs.size and bobs.dtype.kind not in "iu":
        raise TypeError("channel contract: bob must hold integers")
    idx = bobs.astype(np.int64, copy=False)
    if idx.size and (idx.min() < 0 or idx.max() >= mat.shape[1]):
        raise ValueError(
            f"channel contract: bob entries must lie in 0..{mat.shape[1] - 1}"
        )
    draws = rng.random(idx.shape[0])
    out = np.empty(idx.shape[0], dtype=np.int64)
    for j, (b, r) in enumerate(zip(idx.tolist(), draws.tolist())):
        col = mat[:, int(b)]
        edge = 0.0
        pick = mat.shape[0] - 1
        for a in range(mat.shape[0]):
            edge += float(col[a])
            if r < edge:
                pick = a
                break
        out[j] = pick
    return out


def sample_full_block(rng, p_b, f_full, q_high: int, q_low: int, n: int):
    """Sample one model block: ``(bob, a_full, high, low)`` int64 ``(N,)``.

    Generator-only truth source. Callers forward ``bob`` plus the accepted
    table to the metric builder; ``a_full``/``high``/``low`` go only to
    frozen disclosure maps and scoring.
    """
    _check_rng(rng)
    q_high = _check_q(q_high, "q_high")
    q_low = _check_q(q_low, "q_low")
    vec = _check_p_b(p_b)
    mat = _check_f_full(f_full, q_high, q_low)
    if vec.shape[0] != mat.shape[1]:
        raise ValueError(
            f"channel contract: p_b length {vec.shape[0]} != "
            f"f_full Bob width {mat.shape[1]}"
        )
    n = _check_len(n, "n")
    bob = sample_bob(rng, vec, n)
    draws = rng.random(n)
    a_full = np.empty(n, dtype=np.int64)
    for j in range(n):
        col = mat[:, int(bob[j])]
        edge = 0.0
        pick = mat.shape[0] - 1
        for a in range(mat.shape[0]):
            edge += float(col[a])
            if draws[j] < edge:
                pick = a
                break
        a_full[j] = pick
    low = (a_full % q_low).astype(np.int64)
    high = (a_full // q_low).astype(np.int64)
    return bob, a_full, high, low


def build_p1_metrics(bob, p1_table) -> np.ndarray:
    """Operational vectorized P1 metric path: gather rows per Bob label.

    Takes Bob labels plus the table only -- no Alice/truth/U argument
    exists by signature. Supports 1D ``bob`` ``(N,)`` -> ``(N,q)`` and
    2D ``bob`` ``(F,N)`` -> ``(F,N,q)`` probability rows.
    """
    mat = _check_p1(p1_table)
    q, n_b = mat.shape
    bobs = np.asarray(bob)
    if bobs.dtype.kind == "b":
        raise TypeError("channel contract: bob must hold integers, got boolean input")
    if bobs.ndim not in (1, 2):
        raise ValueError(f"channel contract: bob must be 1D or 2D, got shape {bobs.shape}")
    if bobs.size and bobs.dtype.kind not in "iu":
        raise TypeError("channel contract: bob must hold integers")
    idx = bobs.astype(np.int64, copy=False)
    if idx.size and (idx.min() < 0 or idx.max() >= n_b):
        raise ValueError(f"channel contract: bob entries must lie in 0..{n_b - 1}")
    if bobs.ndim == 1:
        return mat[:, idx].transpose(1, 0).copy()
    return mat[:, idx].transpose(1, 2, 0).copy()


def build_p1_metrics_literal(bob, p1_table) -> np.ndarray:
    """Independently written literal-loop reference for the gather.

    Plain-Python per-cell copy of ``p1_table[a,b]``; test/reference only,
    never the operational path. Must agree with :func:`build_p1_metrics`
    within 1e-12 with zero support mismatches.
    """
    mat = _check_p1(p1_table)
    q, n_b = mat.shape
    grid = [[float(mat[a, b]) for b in range(n_b)] for a in range(q)]
    bobs = np.asarray(bob)
    if bobs.dtype.kind == "b":
        raise TypeError("channel contract: bob must hold integers, got boolean input")
    if bobs.ndim not in (1, 2):
        raise ValueError(f"channel contract: bob must be 1D or 2D, got shape {bobs.shape}")
    idx = bobs.tolist()
    if bobs.ndim == 1:
        out = np.empty((len(idx), q), dtype=np.float64)
        for j, b in enumerate(idx):
            if not isinstance(b, int) or not 0 <= b < n_b:
                raise ValueError(
                    f"channel contract: bob entries must lie in 0..{n_b - 1}"
                )
            for a in range(q):
                out[j, a] = grid[a][int(b)]
        return out
    out = np.empty((len(idx), len(idx[0]), q), dtype=np.float64)
    for f in range(len(idx)):
        for j, b in enumerate(idx[f]):
            if not isinstance(b, int) or not 0 <= b < n_b:
                raise ValueError(
                    f"channel contract: bob entries must lie in 0..{n_b - 1}"
                )
            for a in range(q):
                out[f, j, a] = grid[a][int(b)]
    return out
