"""Focused Phase 4-P2-R1 tests: Bob-axis diagnostic on synthetic fixtures.

Synthetic arrays only. No artifact content, no CAL/TTBin/real data, no
Model-F, no SC decoder call, no construction/DEV/EVAL/benchmark, no file
output, no lambda/floor/K/rate selection, no performance claim. Written
without a pytest dependency so it runs under plain ``python``: every
``test_*`` takes no arguments and uses plain asserts plus a local
``assert_raises_match`` helper.

Covers TASK_PACKET.md gates R1-T0-01 and R1-T1-01--T1-08. R1-T2-01 stays a
runner gate (new tests plus all 79 predecessor tests). Tolerances are
absolute maxima (1e-12 unless noted). The asymmetric shape ``(32,7,32)``
with a mask selecting exactly 3 of 7 Bob states exposes the transpose that
square 32-valued axes hide.
"""

from __future__ import annotations

import ast
import inspect
import math
import sys
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import cal_diagnostic as diag_mod

TOL = 1e-12
Q = 32

MODULE_BANNED = (
    "pandas",
    "parquet",
    "TTBin",
    "sc_decode",
    "build_f_model",
    "prepare_model_f_prior",
    "fit_cal_prior",
    "benchmark",
)


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r})")


def asym_fixture():
    """Distinct asymmetric tensor (32,7,32) plus 3-of-7 Bob mask."""
    f3 = np.arange(32 * 7 * 32, dtype=np.float64).reshape(32, 7, 32)
    u1 = 5
    nz_b = np.array([1, 4, 5], dtype=np.int64)
    return f3, u1, nz_b


def prob_fixture():
    """Normalized asymmetric probabilities with sparse Bob support."""
    rng = np.random.default_rng(20260911)
    raw = rng.random((32, 7, 32)) + 0.1
    f3 = raw / raw.sum(axis=-1, keepdims=True)
    p_b = np.array([0.0, 0.2, 0.0, 0.0, 0.5, 0.3, 0.0], dtype=np.float64)
    assert abs(float(p_b.sum()) - 1.0) < 1e-15
    nz_b = np.flatnonzero(p_b != 0)
    assert nz_b.tolist() == [1, 4, 5]
    u1 = 5
    return f3, p_b, u1, nz_b


def test_r1_t000_import_without_io():
    """R1-T0-01: compile/import/help with no I/O and frozen contract words."""
    src = Path(diag_mod.__file__).read_text(encoding="utf-8")
    compile(src, diag_mod.__file__, "exec")
    tree = ast.parse(src)
    for node in tree.body:
        assert not (isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Call)), "module-level call"
    assert "[U1,B,U2]" in src
    assert "nz_b" in src
    import re
    assert re.search(r"f3\s*\[\s*u1\s*,\s*nz_b\s*,\s*:\s*\]", src), "frozen Bob-axis expression absent"
    assert not re.search(r"f3\s*\[\s*u1\s*,\s*:\s*,\s*nz_b\s*\]", src), "wrong axis expression present"
    assert callable(diag_mod.select_bob_slice)
    assert callable(diag_mod.weighted_conditional_entropy)
    assert callable(diag_mod.row_entropies_bits)
    assert inspect.getdoc(diag_mod) and "[U1,B,U2]" in inspect.getdoc(diag_mod)
    for fn in (diag_mod.select_bob_slice, diag_mod.weighted_conditional_entropy,
               diag_mod.row_entropies_bits):
        assert inspect.getdoc(fn), fn.__name__
    for name in MODULE_BANNED:
        assert name not in src, name
    allowed_roots = {"__future__", "numpy", "np"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split(".")[0] in allowed_roots | {"numpy"}, a.name
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] in allowed_roots, node.module


def test_r1_t101_wrong_shape():
    """R1-T1-01: old expression gives transposed (3,7) on (32,7,32)."""
    f3, u1, nz_b = asym_fixture()
    assert f3.shape == (32, 7, 32)
    assert nz_b.tolist() == [1, 4, 5]
    wrong = f3[u1, :, nz_b]
    assert wrong.shape == (3, 7), wrong.shape
    assert wrong.shape != (3, 32)
    for k in range(3):
        for b in range(7):
            assert wrong[k, b] == f3[u1, b, int(nz_b[k])], (k, b)


def test_r1_t102_correct_selection():
    """R1-T1-02: frozen selection is (3,32) matching coordinate lookup."""
    f3, u1, nz_b = asym_fixture()
    got = diag_mod.select_bob_slice(f3, u1, nz_b)
    assert got.shape == (3, 32), got.shape
    for k in range(3):
        for u2 in range(32):
            assert got[k, u2] == f3[u1, int(nz_b[k]), u2], (k, u2)


def test_r1_t103_weighted_entropy_oracle():
    """R1-T1-03: weighted entropy matches a three-loop oracle within 1e-12."""
    f3, p_b, u1, nz_b = prob_fixture()
    weights = p_b[nz_b, None]
    assert weights.shape == (3, 1)
    cond = diag_mod.select_bob_slice(f3, u1, nz_b)
    assert cond.shape == (3, 32)
    prod = diag_mod.weighted_conditional_entropy(cond, weights)
    acc = 0.0
    total = 0.0
    for b in nz_b.tolist():
        w = float(p_b[int(b)])
        total += w
        h = 0.0
        for u2 in range(32):
            p = float(f3[u1, int(b), u2])
            if p > 0:
                h -= p * math.log2(p)
        acc += w * h
    oracle = acc / total
    assert abs(float(prod) - oracle) <= TOL, (prod, oracle)


def test_r1_t104_permutation_invariance():
    """R1-T1-04: simultaneous Bob/weight permutation is invariant 1e-12."""
    f3, p_b, u1, nz_b = prob_fixture()
    weights = p_b[nz_b, None]
    base = diag_mod.weighted_conditional_entropy(
        diag_mod.select_bob_slice(f3, u1, nz_b), weights)
    for perm in ([2, 0, 1], [1, 2, 0], [2, 1, 0]):
        idx = np.array(perm, dtype=np.int64)
        nz_p = nz_b[idx]
        w_p = weights[idx]
        got = diag_mod.weighted_conditional_entropy(
            diag_mod.select_bob_slice(f3, u1, nz_p), w_p)
        assert abs(float(got) - float(base)) <= TOL, (perm, got, base)


def test_r1_t105_zero_weight():
    """R1-T1-05: zero-weight rows cannot matter; zero total fails loudly."""
    f3, p_b, u1, nz_b = prob_fixture()
    cond_rest = diag_mod.select_bob_slice(f3, u1, nz_b)
    w_rest = p_b[nz_b, None]
    prod_rest = diag_mod.weighted_conditional_entropy(cond_rest, w_rest)
    cond_full = f3[u1, :, :]
    assert cond_full.shape == (7, 32)
    w_full = p_b[:, None]
    assert w_full.shape == (7, 1)
    prod_full = diag_mod.weighted_conditional_entropy(cond_full, w_full)
    assert abs(float(prod_full) - float(prod_rest)) <= TOL
    mutated = cond_full.copy()
    mutated[0, :] = 1.0 / 32
    mutated[2, :] = 0.0
    mutated[2, 3] = 1.0
    mutated[6, :] = 0.0
    mutated[6, 9] = 1.0
    prod_mut = diag_mod.weighted_conditional_entropy(mutated, w_full)
    assert abs(float(prod_mut) - float(prod_rest)) <= TOL
    assert_raises_match(ValueError, "diagnostic contract:",
                        diag_mod.weighted_conditional_entropy,
                        cond_rest, np.zeros((3, 1)))
    try:
        diag_mod.weighted_conditional_entropy(cond_rest, np.zeros((3, 1)))
    except ValueError as err:
        assert "weight" in str(err).lower(), str(err)
    else:  # pragma: no cover -- helper already asserted
        raise AssertionError("zero total weight must fail")


def test_r1_t106_onehot_uniform():
    """R1-T1-06: one-hot gives 0 bits, uniform gives exactly 5 bits."""
    onehot = np.zeros((3, 32), dtype=np.float64)
    onehot[:, 7] = 1.0
    w = np.ones((3, 1), dtype=np.float64)
    assert abs(float(diag_mod.weighted_conditional_entropy(onehot, w)) - 0.0) <= TOL
    uniform = np.full((3, 32), 1.0 / 32, dtype=np.float64)
    assert abs(float(diag_mod.weighted_conditional_entropy(uniform, w)) - 5.0) <= TOL


def test_r1_t107_chain_identity():
    """R1-T1-07: P1+P2 chain matches direct joint entropy within 1e-12."""
    rng = np.random.default_rng(20260912)
    n_b = 4
    p_b = rng.random(n_b) + 0.2
    p_b = p_b / p_b.sum()
    p1_raw = rng.random((32, n_b)) + 0.1
    p1 = p1_raw / p1_raw.sum(axis=0, keepdims=True)
    p2_raw = rng.random((32, n_b, 32)) + 0.1
    p2 = p2_raw / p2_raw.sum(axis=-1, keepdims=True)
    nz_b = np.arange(n_b, dtype=np.int64)
    weights = p_b[nz_b, None]
    h1_mod = diag_mod.weighted_conditional_entropy(p1[:, nz_b].T, weights)
    acc = 0.0
    for u1 in range(32):
        sl = diag_mod.select_bob_slice(p2, u1, nz_b)
        w_u1 = (p1[u1, nz_b] * p_b[nz_b])[:, None]
        if float(w_u1.sum()) > 0:
            h_u1 = diag_mod.weighted_conditional_entropy(sl, w_u1)
        else:
            h_u1 = 0.0
        acc += float(w_u1.sum()) * float(h_u1)
    h2_mod = acc / float(p_b[nz_b].sum())
    chain_mod = float(h1_mod) + float(h2_mod)
    wsum = float(p_b[nz_b].sum())
    h1_or = 0.0
    h2_or = 0.0
    h_direct = 0.0
    for b in nz_b.tolist():
        b = int(b)
        wb = float(p_b[b])
        h1_b = 0.0
        for u1 in range(32):
            p = float(p1[u1, b])
            if p > 0:
                h1_b -= p * math.log2(p)
        h1_or += wb * h1_b
        h_j = 0.0
        for u1 in range(32):
            pu1 = float(p1[u1, b])
            h_u1b = 0.0
            for u2 in range(32):
                q = float(p2[u1, b, u2])
                if q > 0:
                    h_u1b -= q * math.log2(q)
                joint = pu1 * q
                if joint > 0:
                    h_j -= joint * math.log2(joint)
            h2_or += wb * pu1 * h_u1b
        h_direct += wb * h_j
    h1_or /= wsum
    h2_or /= wsum
    h_direct /= wsum
    chain_or = h1_or + h2_or
    assert abs(chain_or - h_direct) <= TOL, (chain_or, h_direct)
    assert abs(chain_mod - h_direct) <= TOL, (chain_mod, h_direct)
    assert abs(chain_mod - chain_or) <= TOL, (chain_mod, chain_or)


def test_r1_t108_no_forbidden_paths():
    """R1-T1-08: module and tests enter no CAL/decoder/Model-F/output path."""
    src = Path(diag_mod.__file__).read_text(encoding="utf-8")
    for name in MODULE_BANNED:
        assert name not in src, name
    own = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(own)
    skip = next(n for n in tree.body
                if isinstance(n, ast.FunctionDef) and n.name == "test_r1_t108_no_forbidden_paths")
    lo, hi = skip.lineno, (skip.end_lineno or skip.lineno)
    frags = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    frags.add(id(v))
    banned_assign = next(n for n in tree.body
                         if isinstance(n, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == "MODULE_BANNED"
                                 for t in n.targets))
    blo, bhi = banned_assign.lineno, (banned_assign.end_lineno or banned_assign.lineno)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in frags:
                continue
            ln = getattr(node, "lineno", 0) or 0
            if lo <= ln <= hi:
                continue
            if blo <= ln <= bhi:
                continue
            val = node.value
            assert not val.startswith("/"), val
            assert not (len(val) > 2 and val[1] == ":"), val
            assert val not in ("sc_decode", "build_f_model", "prepare_model_f_prior",
                               "fit_cal_prior", "benchmark"), val
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in (
                "test_r1_t108_no_forbidden_paths", "assert_raises_match",
                "asym_fixture", "prob_fixture"):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Attribute) and sub.attr in ("savez", "savez_compressed", "savetxt"):
                ln = getattr(sub, "lineno", 0) or 0
                if not (lo <= ln <= hi):
                    raise AssertionError("file output call outside T108")
            if isinstance(sub, ast.Name) and sub.id in ("sc_decode", "fit_cal_prior"):
                raise AssertionError(f"decoder path: {sub.id}")


if __name__ == "__main__":
    names = sorted(n for n, v in sorted(globals().items())
                   if n.startswith("test_") and callable(v))
    failed = 0
    for name in names:
        try:
            globals()[name]()
        except Exception as err:  # noqa: BLE001 -- minimal runner reports only
            failed += 1
            print(f"FAIL {name}: {type(err).__name__}: {err}")
        else:
            print(f"ok {name}")
    print(f"{len(names) - failed}/{len(names)} passed")
    sys.exit(1 if failed else 0)
