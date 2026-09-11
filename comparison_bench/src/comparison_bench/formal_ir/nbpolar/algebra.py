"""Phase 1 finite-field adapter for native NB-Polar.

Thin adapter over the pinned ``GF2mField`` semantics in
``nonbinary_field.py``. No field arithmetic is reimplemented here; this
module only pins the Phase 1 domains (GF4 for exhaustive tests, GF32 for
the MVP) and validates integer symbols in ``0..q-1``.
"""

from __future__ import annotations

from numbers import Integral

import numpy as np

from ..nonbinary_field import GF2mField, get_field_spec


def make_gf2m(m: int, primitive_polynomial: int) -> GF2mField:
    """Return the pinned ``GF2mField`` for ``q=2**m``.

    The requested primitive polynomial must equal the repository-pinned
    one for that ``m``; anything else raises ``ValueError``.
    """
    if isinstance(m, bool) or not isinstance(m, Integral):
        raise TypeError("m must be an integer")
    if isinstance(primitive_polynomial, bool) or not isinstance(primitive_polynomial, Integral):
        raise TypeError("primitive_polynomial must be an integer")
    m, primitive_polynomial = int(m), int(primitive_polynomial)
    if m <= 0:
        raise ValueError("m must be positive")
    spec = get_field_spec(1 << m)
    if spec.primitive_polynomial != primitive_polynomial:
        raise ValueError(
            f"primitive polynomial {primitive_polynomial} does not match "
            f"pinned {spec.primitive_polynomial} for GF({spec.q})"
        )
    return GF2mField(spec)


def make_gf32() -> GF2mField:
    """Return the frozen MVP field: GF32, polynomial basis, polynomial 37."""
    return make_gf2m(5, 37)


def validate_symbols(values, q: int, *, name: str = "symbols") -> np.ndarray:
    """Validate integer symbols in ``0..q-1``; return a new int64 vector.

    Rejects booleans, floats, non-integer objects, non-vector input, and
    out-of-range symbols. Never mutates the caller's input.
    """
    if isinstance(q, bool) or not isinstance(q, Integral) or int(q) <= 0:
        raise ValueError("q must be a positive integer")
    q = int(q)
    arr = np.asarray(values)
    if arr.dtype.kind == "b":
        raise TypeError(f"{name} must hold integer symbols, got boolean input")
    if arr.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional vector, got shape {arr.shape}")
    if arr.size == 0:
        return np.empty(0, dtype=np.int64)
    if arr.dtype.kind in "iu":
        out = arr.astype(np.int64, copy=True)
    elif arr.dtype.kind == "O":
        out = np.empty(arr.shape[0], dtype=np.int64)
        for index, value in enumerate(arr.tolist()):
            if isinstance(value, bool) or not isinstance(value, Integral):
                raise TypeError(f"{name}[{index}] must be an integer symbol, got {value!r}")
            out[index] = int(value)
    else:
        raise TypeError(f"{name} must hold integer symbols, got dtype {arr.dtype}")
    if out.size and (out.min() < 0 or out.max() >= q):
        raise ValueError(f"{name} symbols must lie in 0..{q - 1}")
    return out
