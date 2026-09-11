"""Phase 4-P2-R1 CAL diagnostic: Bob-axis selection on [U1,B,U2].

``f3`` layout is ``[U1,B,U2]`` with ``U1=U2=32`` and ``B=n_b`` (production
1024, tests use a small asymmetric ``n_b``). For a fixed ``u1`` and supported
Bob indices ``nz_b``, the frozen selection is ``f3[u1, nz_b, :]`` with shape
``(K,32)`` and weights ``p_b[nz_b,None]`` with shape ``(K,1)``. The weighted
mean row entropy is ``H(U2|U1=u1,B)`` in bits.

NumPy + stdlib only. No sibling/decoder/Model-F I/O, no default production
path, no file output. All failures raise ``ValueError``/``TypeError`` with
the ``diagnostic contract:`` prefix.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "Q_SYMBOL",
    "NORM_TOL",
    "select_bob_slice",
    "row_entropies_bits",
    "weighted_conditional_entropy",
]

Q_SYMBOL = 32
NORM_TOL = 1e-12


def select_bob_slice(f3, u1, nz_b) -> np.ndarray:
    """Select supported Bob rows for fixed ``u1``: ``f3[u1, nz_b, :]``.

    ``f3`` is ``[U1,B,U2]`` ``(32,n_b,32)``; ``u1`` is one ``U1`` label;
    ``nz_b`` holds ``K>=1`` Bob indices. Returns ``(K,32)``.
    """
    f3 = np.asarray(f3)
    if f3.ndim != 3:
        raise ValueError(f"diagnostic contract: f3 must be [U1,B,U2] 3D, got shape {f3.shape}")
    if f3.shape[0] != Q_SYMBOL or f3.shape[2] != Q_SYMBOL or f3.shape[1] < 1:
        raise ValueError(f"diagnostic contract: f3 must be [U1,B,U2] (32,n_b,32), got shape {f3.shape}")
    if isinstance(u1, bool) or not isinstance(u1, (int, np.integer)):
        raise TypeError(f"diagnostic contract: u1 must be an integer, got {u1!r}")
    u1 = int(u1)
    if not 0 <= u1 < Q_SYMBOL:
        raise ValueError(f"diagnostic contract: u1 must lie in 0..{Q_SYMBOL - 1}, got {u1}")
    nz_b = np.asarray(nz_b)
    if nz_b.dtype.kind == "b":
        raise TypeError("diagnostic contract: nz_b must hold integers, got boolean input")
    if nz_b.ndim != 1:
        raise ValueError(f"diagnostic contract: nz_b must be 1D, got shape {nz_b.shape}")
    if nz_b.size == 0:
        raise ValueError("diagnostic contract: nz_b must hold at least one Bob index")
    if nz_b.dtype.kind not in "iu":
        raise TypeError(f"diagnostic contract: nz_b must hold integers, got dtype {nz_b.dtype}")
    nz_b = nz_b.astype(np.int64, copy=True)
    if nz_b.size and (nz_b.min() < 0 or nz_b.max() >= f3.shape[1]):
        raise ValueError(f"diagnostic contract: nz_b entries must lie in 0..{f3.shape[1] - 1}")
    return f3[u1, nz_b, :]


def row_entropies_bits(cond) -> np.ndarray:
    """Per-row Shannon entropy in bits for ``(K,32)`` distributions."""
    mat = np.asarray(cond, dtype=np.float64)
    if mat.ndim != 2 or mat.shape[1] != Q_SYMBOL or mat.shape[0] < 1:
        raise ValueError(f"diagnostic contract: cond must be (K,32), got shape {mat.shape}")
    if not np.isfinite(mat).all():
        raise ValueError("diagnostic contract: cond must be finite")
    if (mat < 0).any():
        raise ValueError("diagnostic contract: cond must be non-negative")
    if float(np.abs(mat.sum(axis=1) - 1).max()) > NORM_TOL:
        raise ValueError("diagnostic contract: cond rows must sum to 1 within 1e-12")
    with np.errstate(divide="ignore"):
        logp = np.log2(mat, out=np.zeros_like(mat), where=mat > 0)
    return -(mat * logp).sum(axis=1)


def weighted_conditional_entropy(cond, weights) -> float:
    """Weighted mean row entropy in bits: ``sum(w*H)/sum(w)``."""
    mat = np.asarray(cond, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    if mat.ndim != 2 or mat.shape[1] != Q_SYMBOL or mat.shape[0] < 1:
        raise ValueError(f"diagnostic contract: cond must be (K,32), got shape {mat.shape}")
    if w.ndim == 2 and w.shape[1] == 1:
        w = w[:, 0]
    if w.ndim != 1 or w.shape[0] != mat.shape[0]:
        raise ValueError(
            f"diagnostic contract: weights must be (K,) or (K,1) with K={mat.shape[0]}, "
            f"got shape {np.asarray(weights).shape}"
        )
    if not np.isfinite(w).all():
        raise ValueError("diagnostic contract: weights must be finite")
    if (w < 0).any():
        raise ValueError("diagnostic contract: weights must be non-negative")
    total = float(w.sum())
    if not np.isfinite(total) or total <= 0:
        raise ValueError("diagnostic contract: total weight must be positive")
    h = row_entropies_bits(mat)
    return float((w * h).sum() / total)
