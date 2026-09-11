"""Frozen natural-order NB-Polar transform over GF(2^m).

Row-vector convention, stated plainly::

    [x0, x1] = kernel([u0, u1])  with  x0 = u0 + alpha*u1,  x1 = u1.

The length-N map is ``G_N = F_alpha tensor_power log2(N)`` in natural
coordinate order: no bit reversal, no inherited baseline ordering. In
characteristic two the kernel is its own inverse, so applying the
transform twice returns the input. All functions return new arrays.
"""

from __future__ import annotations

from numbers import Integral

import numpy as np

from .algebra import validate_symbols


def _check_length(n: int) -> int:
    if n <= 0 or n & (n - 1):
        raise ValueError(f"polar length must be a positive power of two, got {n}")
    return n


def kernel_pair(u0, u1, *, field, alpha: int = 2):
    """Apply one frozen 2x2 kernel step; return ``(x0, x1)`` Python ints."""
    a = field.add(alpha, 0)
    return (field.add(u0, field.mul(a, u1)), field.add(u1, 0))


def polar_transform(symbols, *, field, alpha: int = 2) -> np.ndarray:
    """Fast butterfly transform ``x = u G_N``; returns a new int array.

    The caller's input is never mutated.
    """
    a = field.add(alpha, 0)
    out = validate_symbols(symbols, field.q, name="symbols")
    n = _check_length(out.shape[0])
    size = 1
    while size < n:
        step = 2 * size
        for base in range(0, n, step):
            for j in range(size):
                u0, u1 = out[base + j], out[base + j + size]
                out[base + j] = field.add(u0, field.mul(a, u1))
        size *= 2
    return out


def polar_transform_reference(symbols, *, field, alpha: int = 2) -> np.ndarray:
    """Independent dense reference ``x = u G_N``; never calls the butterfly.

    Builds the generator matrix literally as a Kronecker power of the
    2x2 kernel ``[[1, 0], [alpha, 1]]`` using field operations, then
    multiplies with characteristic-two (XOR) accumulation.
    """
    a = field.add(alpha, 0)
    vec = validate_symbols(symbols, field.q, name="symbols")
    n = _check_length(vec.shape[0])
    if n == 1:
        return vec
    q = field.q
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
    return np.bitwise_xor.reduce(mul_table[vec[:, None], gen], axis=0).astype(np.int64)


def _validate_coordinates(coordinates, n: int, *, name: str = "coordinates") -> np.ndarray:
    arr = np.asarray(coordinates)
    if arr.dtype.kind == "b":
        raise TypeError(f"{name} must hold integer coordinates, got boolean input")
    if arr.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional collection, got shape {arr.shape}")
    if arr.size == 0:
        return np.empty(0, dtype=np.int64)  # empty set selects nothing
    if arr.dtype.kind in "iu":
        coords = arr.astype(np.int64, copy=True)
    elif arr.dtype.kind == "O":
        coords = np.empty(arr.shape[0], dtype=np.int64)
        for index, value in enumerate(arr.tolist()):
            if isinstance(value, bool) or not isinstance(value, Integral):
                raise TypeError(f"{name}[{index}] must be an integer coordinate, got {value!r}")
            coords[index] = int(value)
    else:
        raise TypeError(f"{name} must hold integer coordinates, got dtype {arr.dtype}")
    if coords.size:
        if coords.min() < 0 or coords.max() >= n:
            raise ValueError(f"{name} coordinates must lie in 0..{n - 1}")
        if len(set(coords.tolist())) != coords.size:
            raise ValueError(f"{name} coordinates must not repeat")
    return coords


def transform_and_select(symbols, coordinates, *, field, alpha: int = 2):
    """Source-transform helper: ``u = transform(a)`` plus selected values.

    Returns ``(u, selected)`` where ``selected[k] == u[coordinates[k]]``:
    the caller's coordinate order is preserved and selected zeros are
    kept as zeros. This is not a reconciliation protocol: no disclosure
    accounting, tags, or decoder state are attached here.
    """
    vec = validate_symbols(symbols, field.q, name="symbols")
    _check_length(vec.shape[0])
    coords = _validate_coordinates(coordinates, vec.shape[0])
    u = polar_transform(vec, field=field, alpha=alpha)
    return u, u[coords]
