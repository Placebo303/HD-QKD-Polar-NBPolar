"""Focused Phase 1 tests: field adapter, frozen NB-Polar transform, selection.

Synthetic tiny/deterministic vectors only. No decoder, no channel data,
no file output. Written without a pytest dependency so it runs under
plain ``python`` (pytest is not installed in this container) and is
still collected by pytest elsewhere: every ``test_*`` function takes no
arguments and uses plain asserts.
"""

from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    kernel_pair,
    make_gf2m,
    make_gf32,
    polar_transform,
    polar_transform_reference,
    transform_and_select,
    validate_symbols,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import transform as tmod

RNG_SEED = 20260911


def assert_raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__} from {fn.__name__}{args}")


def literal_recursive(u, field, alpha):
    """Third-path literal recursion: combine halves, recurse (no butterfly)."""
    u = [int(v) for v in u]
    n = len(u)
    if n == 1:
        return np.array(u, dtype=np.int64)
    h = n // 2
    lo = [field.add(u[i], field.mul(alpha, u[i + h])) for i in range(h)]
    hi = u[h:]
    return np.concatenate([literal_recursive(lo, field, alpha), literal_recursive(hi, field, alpha)])


# --- P1-T0-02: GF32 constants and closure -----------------------------------

def test_gf32_constants_observable():
    f = make_gf32()
    assert (f.q, f.m, f.primitive_polynomial) == (32, 5, 37)


def test_gf4_adapter_uses_pinned_polynomial():
    assert make_gf2m(2, 7).q == 4
    assert_raises(ValueError, make_gf2m, 5, 0x11)
    assert_raises(ValueError, make_gf2m, 2, 37)
    assert_raises(ValueError, make_gf2m, 0, 3)
    assert_raises(TypeError, make_gf2m, True, 37)


def test_alpha2_cycle_length_31():
    f = make_gf32()
    seen, v = set(), 1
    for _ in range(31):
        assert v not in seen
        seen.add(v)
        v = f.mul(v, 2)
    assert v == 1 and len(seen) == 31


def test_gf32_closure_exhaustive():
    f = make_gf32()
    for a, b in itertools.product(range(32), repeat=2):
        assert 0 <= f.add(a, b) < 32
        assert 0 <= f.mul(a, b) < 32


def test_invalid_symbols_fail():
    assert_raises(ValueError, validate_symbols, [32], 32)
    assert_raises(ValueError, validate_symbols, [-1], 32)
    assert_raises(TypeError, validate_symbols, [1.0, 2.0], 32)
    assert_raises(TypeError, validate_symbols, [True, False], 32)
    assert_raises(ValueError, validate_symbols, [[1, 2], [3, 4]], 32)
    assert_raises(ValueError, validate_symbols, 3, 32)


# --- P1-T1-01: literal kernel examples --------------------------------------

def test_kernel_literal_pairs_gf32():
    f = make_gf32()
    assert kernel_pair(0, 0, field=f) == (0, 0)
    assert kernel_pair(5, 0, field=f) == (5, 0)
    assert kernel_pair(0, 7, field=f) == (14, 7)  # 2*7 = x^3+x^2+x = 14
    assert kernel_pair(2, 1, field=f) == (0, 1)  # u0 == alpha*u1: XOR cancels
    assert f.mul(8, 8) == 10  # x^6 = x^3+x mod x^5+x^2+1
    assert kernel_pair(8, 8, field=f) == (24, 8)  # 2*8 = 16, 8^16 = 24


def test_kernel_literal_pair_gf4():
    f = make_gf2m(2, 7)
    assert f.mul(2, 2) == 3  # x^2 = x+1 mod x^2+x+1
    assert kernel_pair(2, 2, field=f) == (1, 2)  # 2^3 = 1
    assert kernel_pair(0, 0, field=f) == (0, 0)


def test_kernel_double_application_is_identity():
    for f in (make_gf32(), make_gf2m(2, 7)):
        for u0, u1 in [(0, 0), (5, 0), (0, 7), (2, 1), (8, 8), (1, 31)]:
            if max(u0, u1) >= f.q:
                continue
            x0, x1 = kernel_pair(u0, u1, field=f)
            assert kernel_pair(x0, x1, field=f) == (u0, u1)


# --- P1-T1-02: exhaustive GF4 N=4 oracle ------------------------------------

def test_exhaustive_gf4_n4_oracle():
    f = make_gf2m(2, 7)
    count = 0
    for tup in itertools.product(range(4), repeat=4):
        vec = np.array(tup, dtype=np.int64)
        fast = polar_transform(vec, field=f)
        ref = polar_transform_reference(vec, field=f)
        assert np.array_equal(fast, ref), tup
        assert np.array_equal(polar_transform(fast, field=f), vec), tup
        assert fast.dtype.kind in "iu" and fast.min() >= 0 and fast.max() < 4
        count += 1
    assert count == 256


# --- P1-T1-03: exhaustive GF32 N=2 oracle -----------------------------------

def test_exhaustive_gf32_n2_oracle():
    f = make_gf32()
    count = 0
    for u0 in range(32):
        for u1 in range(32):
            vec = np.array([u0, u1], dtype=np.int64)
            fast = polar_transform(vec, field=f)
            ref = polar_transform_reference(vec, field=f)
            assert np.array_equal(fast, ref), (u0, u1)
            assert np.array_equal(polar_transform(fast, field=f), vec), (u0, u1)
            assert fast.min() >= 0 and fast.max() < 32
            count += 1
    assert count == 1024


# --- P1-T1-04: deterministic random lengths ---------------------------------

def test_random_lengths_fast_equals_reference_and_input_kept():
    f = make_gf32()
    rng = np.random.default_rng(RNG_SEED)
    for n in (8, 64, 256, 1024):
        for _ in range(20):
            vec = rng.integers(0, 32, size=n).astype(np.int64)
            snapshot = vec.copy()
            fast = polar_transform(vec, field=f)
            assert np.array_equal(vec, snapshot)
            assert np.array_equal(fast, polar_transform_reference(vec, field=f))
            assert np.array_equal(polar_transform(fast, field=f), vec)


def test_transform_rejects_bad_length_and_input():
    f = make_gf32()
    assert_raises(ValueError, polar_transform, [1, 2, 3], field=f)
    assert_raises(ValueError, polar_transform, [], field=f)
    assert_raises(ValueError, polar_transform, [0, 32], field=f)
    assert_raises(TypeError, polar_transform, [0.0, 1.0], field=f)


# --- P1-T1-05: no hidden bit reversal ---------------------------------------

def test_basis_vectors_match_natural_kronecker_order():
    f = make_gf32()
    y4 = polar_transform([0, 1, 0, 0], field=f)
    assert y4.tolist() == [2, 1, 0, 0]  # G_4 row 1; bit reversal would give [2, 0, 1, 0]
    assert y4.tolist() != [2, 0, 1, 0]
    e1 = np.zeros(8, dtype=np.int64)
    e1[1] = 1
    y8 = polar_transform(e1, field=f)
    assert y8.tolist() == [2, 1, 0, 0, 0, 0, 0, 0]  # G_8 row 1; row 4 would be [2,0,0,0,1,0,0,0]
    assert y8.tolist() != [2, 0, 0, 0, 1, 0, 0, 0]


def test_nonpalindromic_vectors_match_literal_order():
    f4 = make_gf2m(2, 7)
    u4 = np.array([1, 0, 3, 2], dtype=np.int64)  # reverse [2,3,0,1] differs
    assert polar_transform(u4, field=f4).tolist() == [1, 3, 0, 2]  # hand butterfly check
    assert np.array_equal(polar_transform(u4, field=f4), literal_recursive(u4, f4, 2))
    f32 = make_gf32()
    u8 = np.array([1, 2, 3, 4, 5, 6, 7, 0], dtype=np.int64)
    assert np.array_equal(polar_transform(u8, field=f32), literal_recursive(u8, f32, 2))
    assert np.array_equal(polar_transform(u8, field=f32), polar_transform_reference(u8, field=f32))


# --- P1-T1-06: source coordinate semantics ----------------------------------

def test_select_empty_unsorted_and_zero():
    f = make_gf32()
    a = np.array([1, 2, 3, 4], dtype=np.int64)
    u, sel = transform_and_select(a, [], field=f)
    assert sel.shape == (0,) and np.array_equal(u, polar_transform(a, field=f))
    u, sel = transform_and_select(a, [3, 0, 2], field=f)
    assert sel.tolist() == [int(u[3]), int(u[0]), int(u[2])]  # input order kept
    z = np.zeros(4, dtype=np.int64)
    uz, selz = transform_and_select(z, [1, 2], field=f)
    assert selz.shape == (2,) and selz.tolist() == [0, 0]  # zero retained, not dropped
    assert np.array_equal(uz, np.zeros(4, dtype=np.int64))


def test_select_rejects_bad_coordinates():
    f = make_gf32()
    a = [1, 2, 3, 4]
    assert_raises(ValueError, transform_and_select, a, [1, 1], field=f)
    assert_raises(ValueError, transform_and_select, a, [4], field=f)
    assert_raises(ValueError, transform_and_select, a, [-1], field=f)
    assert_raises(ValueError, transform_and_select, a, [[1, 2]], field=f)
    assert_raises(TypeError, transform_and_select, a, [1.0], field=f)


# --- P1-T1-07: forbidden-dependency audit ------------------------------------

def test_no_forbidden_production_dependencies():
    pkg = Path(tmod.__file__).parent
    pattern = re.compile(r"LDPC|PEG|QC|BP|Cascade|\bPW\b|BSC|LLR|CRC|Model-F|TTBin|polar_existing")
    hits = []
    for name in ("__init__.py", "algebra.py", "transform.py"):
        for lineno, line in enumerate((pkg / name).read_text().splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{name}:{lineno}:{line}")
    assert hits == []


# --- plain-python runner -----------------------------------------------------

def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    main()
