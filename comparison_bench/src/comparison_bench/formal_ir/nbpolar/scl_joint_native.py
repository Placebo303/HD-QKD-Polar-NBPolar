"""ctypes-native (Rust/C++) drop-in replacement for ``scl_joint.scl_joint_decode``.

Authorization: PI ruling 2026-09-29 ("选 B, 可以装一个cargo然后测c++和rust"),
this session (coder-fast). Frozen files untouched: ``scl.py``, ``sc.py``,
``scl_joint.py``, ``two_layer.py``, ``prior.py``, ``transform.py``,
``nonbinary_field.py`` are only imported by public module attribute, never
edited or monkeypatched -- and the already-existing ``scl_joint_fast.py``
(numba baseline-fast engine) is also left untouched. This module
deliberately does NOT import ``scl_joint_fast`` (which imports ``numba`` at
module scope): the point of the native backend is to run in the WSL
``timetagger`` venv used for real-data decoding, which has ``numpy`` but not
``numba`` installed (confirmed this session). ``_mul_row_table`` is
therefore a small local reimplementation (same one-line formula,
``field.mul(field.add(alpha, 0), v)`` for ``v in 0..q-1``, no behavior
difference) rather than a shared import, and this module returns
``scl.SCLResult`` (field-identical, also numba-free) instead of
``scl_joint_fast.SCLResultFast``.

Why this module exists
-----------------------
``scl_joint_decode`` (frozen reference) needs ~870 s/block at N=32768, L=16;
the numba ``scl_joint_fast`` engine ~120 s/block. Profiling shows the cost is
(i) the per-node ``minus``/``plus``/``polar_transform`` kernels and (ii) Python
control flow (~2N recursion nodes, list/array bookkeeping per node). This
module moves both into native code:

* Kernels: ``minus`` is an XOR-convolution over (Z/2)^5 (GF(32) addition is
  XOR; multiplication by a fixed nonzero element is GF(2)-linear), evaluated
  in the linear domain with per-operand max shifts, direct 32x32 sum of
  positive terms, exact log-domain per-entry fallback below 1e-250, fused row
  normalization. A Walsh-Hadamard version (O(q log q)) was tried first and
  REJECTED: its absolute round-off (~1e-16 * row peak) turns tiny-but-finite
  entries into false -inf and killed live paths at disclosed coordinates
  (``ImpossibleDisclosedValueError`` on the G1R2-matched channel, N=256).
  Exact -inf semantics are preserved; no fastmath anywhere.
* Whole-recursion decoder (Rust cdylib, ``_native/rust_kernels``): the entire
  list-SC recursion (segment-metric stack shared by ``Rc``, path prefixes in a
  parent-pointer arena, leaf candidate ordering ``(metric desc, symbol asc,
  path asc)``, frozen top-L keep, disclosed-coordinate forcing) runs in ONE
  ctypes call per ``scl_decode`` (GIL released), and the ``top_m`` L2
  decodes of a joint decode run in parallel Python threads. Python keeps only
  metric validation, CRC selection and joint merge (imported from
  ``scl_joint``, not reimplemented).
* Portable fallback: if only the C++ kernel library is available (native
  Windows via Strawberry Perl mingw g++; the Rust toolchain is WSL-only per PI
  ruling), the same kernels are called from Python control flow
  (:func:`_scl_decode_native_py`, one call per recursion level batched over
  live paths). Same numerics, ~7x slower than the whole-recursion path.

Equivalence standard B (PI ruling 2026-09-29): decisions must agree with the
frozen reference except at exact metric ties (relative gap <= 1e-9), and the
FER distribution on synthetic data must match; bit-identical rounding of every
float is *not* required. Note exact ties are common on this channel (e.g. a
row that is exactly uniform over 32 symbols): the reference breaks them with
its own ~1e-16 rounding noise, this module effectively by smallest symbol
index, so per-block ``label_hat`` agreement can be low while FER agrees --
see ``comparison_bench/tests/test_nbpolar_scl_joint_native.py`` (T-N1 tie
forensics, T-N2 paired FER).

No data loading, no benchmark/output machinery, no I/O, no real data.
"""

from __future__ import annotations

import ctypes
import os
import platform

import numpy as np

from . import scl as scl_mod
from . import scl_joint as scl_joint_mod
from . import sc as sc_mod
from .prior import Provenance, gather_p2_metrics, probs_to_symbol_metric
from . import two_layer as two_layer_mod


def _mul_row_table(field, alpha: int) -> np.ndarray:
    """``mul_row[v] = field.mul(field.add(alpha, 0), v)`` for ``v in 0..q-1``.

    Local reimplementation of ``scl_joint_fast._mul_row_table`` (same
    one-line formula, built once per decode call from the frozen field
    object) so this module has no import-time dependency on ``numba`` (see
    module docstring). Built once per decode call; 32 Python calls,
    negligible next to the native O(N log N) kernels below.
    """
    a = field.add(alpha, 0)
    q = field.q
    row = np.empty(q, dtype=np.int64)
    for v in range(q):
        row[v] = field.mul(a, v)
    return row

__all__ = [
    "scl_joint_decode_native",
    "NativeBackendUnavailableError",
    "native_backend_info",
]

_NATIVE_DIR = os.path.join(os.path.dirname(__file__), "_native")


class NativeBackendUnavailableError(RuntimeError):
    """Raised when no native (Rust or C++) kernel shared library can be loaded."""


def _candidate_lib_paths() -> list[tuple[str, str]]:
    """Return ``[(backend_name, path), ...]`` in preference order for this OS."""
    system = platform.system()
    if system == "Linux":
        return [
            ("rust", os.path.join(_NATIVE_DIR, "libnbpolar_kernels_rust.so")),
            ("cpp", os.path.join(_NATIVE_DIR, "libnbpolar_kernels.so")),
        ]
    if system == "Windows":
        return [
            ("cpp", os.path.join(_NATIVE_DIR, "nbpolar_kernels_win.dll")),
        ]
    if system == "Darwin":
        return [
            ("cpp", os.path.join(_NATIVE_DIR, "libnbpolar_kernels.dylib")),
        ]
    return []


def _load_library():
    tried = []
    for backend, path in _candidate_lib_paths():
        if not os.path.isfile(path):
            tried.append(f"{backend}:{path} (not built)")
            continue
        try:
            lib = ctypes.CDLL(path)
        except OSError as exc:  # pragma: no cover - environment-dependent
            tried.append(f"{backend}:{path} (load failed: {exc})")
            continue
        lib.nbpolar_minus_block_f64.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
            ctypes.c_longlong, ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_longlong), ctypes.POINTER(ctypes.c_longlong),
            ctypes.POINTER(ctypes.c_double),
        ]
        lib.nbpolar_minus_block_f64.restype = None
        lib.nbpolar_plus_block_f64.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.c_longlong, ctypes.c_longlong,
            ctypes.POINTER(ctypes.c_longlong),
            ctypes.POINTER(ctypes.c_double),
        ]
        lib.nbpolar_plus_block_f64.restype = None
        lib.nbpolar_polar_transform_batch_f64.argtypes = [
            ctypes.POINTER(ctypes.c_longlong), ctypes.c_longlong, ctypes.c_longlong,
            ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong),
        ]
        lib.nbpolar_polar_transform_batch_f64.restype = None
        if hasattr(lib, "nbpolar_scl_decode_f64"):
            lib.nbpolar_scl_decode_f64.argtypes = [
                ctypes.POINTER(ctypes.c_double), ctypes.c_longlong, ctypes.c_longlong,
                ctypes.POINTER(ctypes.c_longlong), ctypes.POINTER(ctypes.c_longlong),
                ctypes.c_longlong,
                ctypes.POINTER(ctypes.c_int8), ctypes.POINTER(ctypes.c_longlong),
                ctypes.c_longlong,
                ctypes.POINTER(ctypes.c_longlong), ctypes.POINTER(ctypes.c_double),
                ctypes.POINTER(ctypes.c_longlong),
            ]
            lib.nbpolar_scl_decode_f64.restype = None
        return backend, path, lib
    raise NativeBackendUnavailableError(
        "no native minus/plus/transform kernel library could be loaded; tried: "
        + "; ".join(tried)
        + f". Build one via {_NATIVE_DIR}/build_rust.sh (WSL) or "
          f"{_NATIVE_DIR}/build_cpp.sh / build_cpp.ps1 (WSL or Windows)."
    )


_BACKEND_NAME: str | None = None
_BACKEND_PATH: str | None = None
_LIB = None


def _ensure_lib():
    global _BACKEND_NAME, _BACKEND_PATH, _LIB
    if _LIB is None:
        _BACKEND_NAME, _BACKEND_PATH, _LIB = _load_library()
    return _LIB


def native_backend_info() -> dict:
    """Which native library is actually loaded (for provenance/logging)."""
    _ensure_lib()
    return {"backend": _BACKEND_NAME, "path": _BACKEND_PATH}


def _ptr(arr: np.ndarray, ctype):
    return arr.ctypes.data_as(ctypes.POINTER(ctype))


def _minus_block_native(first: np.ndarray, second: np.ndarray, cv: np.ndarray, cv_inv: np.ndarray) -> np.ndarray:
    lib = _ensure_lib()
    rows, q = first.shape
    first_c = np.ascontiguousarray(first, dtype=np.float64)
    second_c = np.ascontiguousarray(second, dtype=np.float64)
    out = np.empty((rows, q), dtype=np.float64)
    lib.nbpolar_minus_block_f64(
        _ptr(first_c, ctypes.c_double), _ptr(second_c, ctypes.c_double),
        rows, q, _ptr(cv, ctypes.c_longlong), _ptr(cv_inv, ctypes.c_longlong),
        _ptr(out, ctypes.c_double),
    )
    return out


def _plus_block_native(first: np.ndarray, second: np.ndarray, beta: np.ndarray, cv: np.ndarray) -> np.ndarray:
    lib = _ensure_lib()
    rows, q = first.shape
    first_c = np.ascontiguousarray(first, dtype=np.float64)
    second_c = np.ascontiguousarray(second, dtype=np.float64)
    beta_c = np.ascontiguousarray(beta, dtype=np.int64)
    out = np.empty((rows, q), dtype=np.float64)
    lib.nbpolar_plus_block_f64(
        _ptr(first_c, ctypes.c_double), _ptr(second_c, ctypes.c_double),
        _ptr(beta_c, ctypes.c_longlong), rows, q, _ptr(cv, ctypes.c_longlong),
        _ptr(out, ctypes.c_double),
    )
    return out


def _polar_transform_batch_native(symbols: np.ndarray, q: int, mul_row: np.ndarray) -> np.ndarray:
    lib = _ensure_lib()
    rows, n = symbols.shape
    buf = np.ascontiguousarray(symbols, dtype=np.int64).copy()
    lib.nbpolar_polar_transform_batch_f64(
        _ptr(buf, ctypes.c_longlong), rows, n, q, _ptr(mul_row, ctypes.c_longlong),
    )
    return buf


# --------------------------------------------------------------------------
# List-SC engine: same control-flow shape as scl.py's scl_decode /
# scl_joint_fast._scl_decode_fast, swapping only the three kernel calls for
# the native ones above. Frozen top_l_prune hardcoded, same as
# scl_joint_fast (see that module's docstring for why there is no generic
# prune_rule slot here either).
# --------------------------------------------------------------------------


class _NativePath:
    __slots__ = ("prefix", "metric", "blocks")

    def __init__(self, prefix, metric, blocks):
        self.prefix = prefix
        self.metric = metric
        self.blocks = blocks


def _scl_decode_native_py(
    logp_x,
    *,
    field,
    alpha: int = 2,
    known_positions=None,
    known_values=None,
    list_width_L: int,
) -> scl_mod.SCLResult:
    """Python-control-flow list-SC decode with native minus/plus/transform
    kernels (portable fallback: works with the C++ library, e.g. on Windows;
    also used as the cross-check for the whole-recursion Rust decoder).
    Frozen top_l_prune only.

    Validation is reused verbatim from ``sc.py``/``scl.py`` private helpers,
    exactly as ``scl_joint_fast._scl_decode_fast`` does.
    """
    q, alpha = sc_mod._check_field(field, alpha)
    metrics, n = sc_mod._validate_metric(logp_x, q)
    known = sc_mod._validate_known(known_positions, known_values, n, q)
    width = scl_mod._check_width(list_width_L)
    mul_row = _mul_row_table(field, alpha)
    cv = np.ascontiguousarray(mul_row, dtype=np.int64)
    cv_inv = np.empty(q, dtype=np.int64)
    cv_inv[cv] = np.arange(q, dtype=np.int64)

    live_paths = [_NativePath([], 0.0, [metrics])]
    pruned_total = [0]

    def decode_leaf(position: int) -> None:
        p_count = len(live_paths)
        rows_stack = np.empty((p_count, q), dtype=np.float64)
        for i, path in enumerate(live_paths):
            rows_stack[i] = path.blocks[-1][0]
        if position in known:
            value = known[position]
            scores = rows_stack[:, value]
            dead = scores == -np.inf
            n_dead = int(dead.sum())
            if n_dead:
                pruned_total[0] += n_dead
            nonfinite = ~np.isfinite(scores) & ~dead
            if nonfinite.any():
                raise sc_mod.NumericNonfiniteError(
                    f"numeric nonfinite failure: nonfinite score at U[{position}]"
                )
            survivors = []
            for i, path in enumerate(live_paths):
                if dead[i]:
                    continue
                path.prefix.append(int(value))
                path.metric += 0.0
                survivors.append(path)
            if not survivors:
                raise sc_mod.ImpossibleDisclosedValueError(
                    f"impossible disclosed value: U[{position}]={value} "
                    "has exact-zero support"
                )
            live_paths[:] = survivors
            return

        path_metric_vec = np.array([path.metric for path in live_paths], dtype=np.float64)
        full_metric = path_metric_vec[:, None] + rows_stack
        dead_mask = rows_stack == -np.inf
        pruned_total[0] += int(dead_mask.sum())
        finite_mask = ~dead_mask
        nonfinite = ~np.isfinite(rows_stack) & finite_mask
        if nonfinite.any():
            raise sc_mod.NumericNonfiniteError(
                f"numeric nonfinite failure: nonfinite score at U[{position}]"
            )
        path_arr, symbol_arr = np.nonzero(finite_mask)
        if path_arr.size == 0:
            raise sc_mod.NumericNonfiniteError(
                f"numeric nonfinite failure: no finite support at U[{position}]"
            )
        metric_arr = full_metric[path_arr, symbol_arr]
        order = np.lexsort((path_arr, symbol_arr, -metric_arr))
        keep_n = min(width, order.size)
        keep = order[:keep_n]
        pruned_total[0] += int(order.size - keep_n)

        survivors = []
        for source in keep.tolist():
            p_idx = int(path_arr[source])
            symbol = int(symbol_arr[source])
            metric_val = float(metric_arr[source])
            parent = live_paths[p_idx]
            child = _NativePath(parent.prefix + [symbol], metric_val, list(parent.blocks))
            survivors.append(child)
        live_paths[:] = survivors

    def decode_segment(offset: int, size: int) -> None:
        if size == 1:
            decode_leaf(offset)
            return
        half = size // 2
        firsts = np.concatenate([path.blocks[-1][:half] for path in live_paths], axis=0)
        seconds = np.concatenate([path.blocks[-1][half:] for path in live_paths], axis=0)
        combined = _minus_block_native(firsts, seconds, cv, cv_inv)
        for i, path in enumerate(live_paths):
            path.blocks.append(combined[i * half : (i + 1) * half])
        decode_segment(offset, half)
        for path in live_paths:
            path.blocks.pop()
        firsts2 = np.concatenate([path.blocks[-1][:half] for path in live_paths], axis=0)
        seconds2 = np.concatenate([path.blocks[-1][half:] for path in live_paths], axis=0)
        prefixes = np.stack(
            [np.asarray(path.prefix[offset : offset + half], dtype=np.int64) for path in live_paths]
        )
        betas = _polar_transform_batch_native(prefixes, q, cv).reshape(-1)
        combined2 = _plus_block_native(firsts2, seconds2, betas, cv)
        for i, path in enumerate(live_paths):
            path.blocks.append(combined2[i * half : (i + 1) * half])
        decode_segment(offset + half, half)
        for path in live_paths:
            path.blocks.pop()

    decode_segment(0, n)

    final_metrics = np.array([path.metric for path in live_paths], dtype=np.float64)
    final_order = np.argsort(-final_metrics, kind="stable")
    ranked = [live_paths[k] for k in final_order.tolist()]
    u_candidates = np.stack(
        [np.asarray(path.prefix, dtype=np.int64) for path in ranked]
    ).astype(np.int64, copy=False)
    x_candidates = _polar_transform_batch_native(u_candidates, q, cv)
    path_metrics = final_metrics[final_order]
    known_mask = np.zeros(n, dtype=bool)
    known_mask[list(known)] = True
    backend = native_backend_info()
    provenance = {
        "input_role": "prior: logp_x[j,a] = ln P(X_j=a | Bob/context), rows normalized to logsumexp 0",
        "row_role": "classic source SC conditionals: per-path metrics accumulate ln P(U_i=u_i | prefix, B/context), suffix marginalized",
        "log_base": "natural",
        "normalization": "float64; every produced row normalized, exact-zero support kept as -inf",
        "tie_break": "larger path metric first, then smallest symbol index, then smallest path index",
        "kernel": "row-vector F_alpha with x0=u0+alpha*u1, x1=u1, natural order (native WHT convolution)",
        "q": q,
        "alpha": alpha,
        "primitive_polynomial": getattr(field, "primitive_polynomial", None),
        "list_width_L": width,
        "prune_rule": "top_l_prune",
        "engine": f"scl_joint_native (python control flow + native kernels, backend={backend['backend']})",
    }
    return scl_mod.SCLResult(
        u_candidates=u_candidates,
        x_candidates=x_candidates,
        path_metrics=path_metrics,
        survivor_count=len(ranked),
        requested_width=width,
        pruned_count=int(pruned_total[0]),
        status="ok",
        known_count=len(known),
        known_mask=known_mask,
        metric_provenance=provenance,
    )


def _default_threads() -> int:
    return max(1, (os.cpu_count() or 1))


def _scl_decode_native(
    logp_x,
    *,
    field,
    alpha: int = 2,
    known_positions=None,
    known_values=None,
    list_width_L: int,
    nthreads: int | None = None,
) -> scl_mod.SCLResult:
    """List-SC decode, frozen top_l_prune only. Uses the whole-recursion Rust
    decoder (one ctypes call per decode, GIL released for its duration) when
    the loaded library exports ``nbpolar_scl_decode_f64``; otherwise falls
    back to :func:`_scl_decode_native_py`. Validation is the frozen
    ``sc.py``/``scl.py`` private helpers, exactly as ``scl_joint_fast`` does.
    """
    lib = _ensure_lib()
    if not hasattr(lib, "nbpolar_scl_decode_f64"):
        return _scl_decode_native_py(
            logp_x, field=field, alpha=alpha, known_positions=known_positions,
            known_values=known_values, list_width_L=list_width_L,
        )
    q, alpha = sc_mod._check_field(field, alpha)
    metrics, n = sc_mod._validate_metric(logp_x, q)
    known = sc_mod._validate_known(known_positions, known_values, n, q)
    width = scl_mod._check_width(list_width_L)
    mul_row = _mul_row_table(field, alpha)
    cv = np.ascontiguousarray(mul_row, dtype=np.int64)
    cv_inv = np.empty(q, dtype=np.int64)
    cv_inv[cv] = np.arange(q, dtype=np.int64)
    known_mask = np.zeros(n, dtype=np.int8)
    known_val = np.zeros(n, dtype=np.int64)
    for pos, val in known.items():
        known_mask[pos] = 1
        known_val[pos] = val
    metrics_c = np.ascontiguousarray(metrics, dtype=np.float64)
    out_u = np.zeros((width, n), dtype=np.int64)
    out_metric = np.zeros(width, dtype=np.float64)
    info = np.zeros(4, dtype=np.int64)
    lib.nbpolar_scl_decode_f64(
        _ptr(metrics_c, ctypes.c_double), n, q,
        _ptr(cv, ctypes.c_longlong), _ptr(cv_inv, ctypes.c_longlong), width,
        _ptr(known_mask, ctypes.c_int8), _ptr(known_val, ctypes.c_longlong),
        int(nthreads if nthreads is not None else _default_threads()),
        _ptr(out_u, ctypes.c_longlong), _ptr(out_metric, ctypes.c_double),
        _ptr(info, ctypes.c_longlong),
    )
    status, survivors, pruned, err_pos = (int(v) for v in info)
    if status == 1:
        raise sc_mod.ImpossibleDisclosedValueError(
            f"impossible disclosed value: U[{err_pos}]={known.get(err_pos)} has exact-zero support"
        )
    if status == 2:
        raise sc_mod.NumericNonfiniteError(
            f"numeric nonfinite failure: nonfinite score or no finite support at U[{err_pos}]"
        )
    u_candidates = out_u[:survivors].copy()
    x_candidates = _polar_transform_batch_native(u_candidates, q, cv)
    known_mask_b = np.zeros(n, dtype=bool)
    known_mask_b[list(known)] = True
    backend = native_backend_info()
    provenance = {
        "input_role": "prior: logp_x[j,a] = ln P(X_j=a | Bob/context), rows normalized to logsumexp 0",
        "row_role": "classic source SC conditionals: per-path metrics accumulate ln P(U_i=u_i | prefix, B/context), suffix marginalized",
        "log_base": "natural",
        "normalization": "float64; every produced row normalized, exact-zero support kept as -inf",
        "tie_break": "larger path metric first, then smallest symbol index, then smallest path index",
        "kernel": "row-vector F_alpha with x0=u0+alpha*u1, x1=u1, natural order (native linear-domain XOR convolution)",
        "q": q,
        "alpha": alpha,
        "primitive_polynomial": getattr(field, "primitive_polynomial", None),
        "list_width_L": width,
        "prune_rule": "top_l_prune",
        "engine": f"scl_joint_native (whole-recursion native decoder, backend={backend['backend']})",
    }
    return scl_mod.SCLResult(
        u_candidates=u_candidates,
        x_candidates=x_candidates,
        path_metrics=out_metric[:survivors].copy(),
        survivor_count=survivors,
        requested_width=width,
        pruned_count=pruned,
        status="ok",
        known_count=len(known),
        known_mask=known_mask_b,
        metric_provenance=provenance,
    )


# --------------------------------------------------------------------------
# Joint two-layer CRC-aided decode: same merge/CRC/ranking as scl_joint.py,
# imported (not reimplemented), exactly like scl_joint_fast.scl_joint_decode_fast.
# --------------------------------------------------------------------------


def scl_joint_decode_native(
    bob,
    crc_true: int,
    *,
    field,
    alpha: int = 2,
    p1_table,
    p2_table,
    d1_positions=None,
    d1_values=None,
    d2_positions=None,
    d2_values=None,
    list_width_L: int,
    top_m: int = scl_joint_mod.TOP_M_DEFAULT,
):
    """ctypes-native drop-in for ``scl_joint.scl_joint_decode``.

    Identical inputs/outputs (``scl_joint.SCLJointResult``) and identical
    merge/CRC/ranking logic (imported from ``scl_joint``, not reimplemented);
    only the inner list-SC engine is :func:`_scl_decode_native` instead of
    ``scl.scl_decode`` / ``scl_joint_fast._scl_decode_fast``. Raises
    :class:`NativeBackendUnavailableError` if no native library is built for
    this OS (see ``_native/build_rust.sh`` / ``build_cpp.sh`` / ``build_cpp.ps1``).
    """
    if isinstance(top_m, bool) or int(top_m) <= 0:
        raise ValueError(f"field/shape contract: top_m must be a positive integer, got {top_m!r}")
    top_m = int(top_m)

    bob_row = np.asarray(bob)[None, :]
    p1_probs = two_layer_mod.build_p1_metrics(bob_row, p1_table)[0]
    p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)

    l1_res = _scl_decode_native(
        p1_metric.logp,
        field=field,
        alpha=alpha,
        known_positions=d1_positions,
        known_values=d1_values,
        list_width_L=list_width_L,
    )

    top_m_used = min(top_m, l1_res.survivor_count)
    p2_logps = []
    for l1_rank in range(top_m_used):
        high_cand = l1_res.x_candidates[l1_rank]
        p2_probs = gather_p2_metrics(bob_row, high_cand[None, :], p2_table)[0]
        p2_logps.append(
            probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED).logp
        )

    def _l2(logp):
        return _scl_decode_native(
            logp, field=field, alpha=alpha, known_positions=d2_positions,
            known_values=d2_values, list_width_L=list_width_L,
            nthreads=max(1, _default_threads() // max(1, top_m_used)),
        )

    # The top_m L2 decodes are independent; the whole-recursion native call
    # releases the GIL (ctypes), so run them in threads.
    if top_m_used > 1 and hasattr(_ensure_lib(), "nbpolar_scl_decode_f64"):
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=top_m_used) as pool:
            l2_results = list(pool.map(_l2, p2_logps))
    else:
        l2_results = [_l2(lp) for lp in p2_logps]

    merged: list[scl_joint_mod.JointCandidate] = []
    for l1_rank, l2_res in enumerate(l2_results):
        high_cand = l1_res.x_candidates[l1_rank]
        m1 = float(l1_res.path_metrics[l1_rank])
        for l2_rank in range(l2_res.survivor_count):
            low_cand = l2_res.x_candidates[l2_rank]
            m2 = float(l2_res.path_metrics[l2_rank])
            merged.append(
                scl_joint_mod.JointCandidate(
                    high=high_cand,
                    low=low_cand,
                    m1=m1,
                    m2=m2,
                    joint_metric=m1 + m2,
                    l1_rank=l1_rank,
                    l2_rank=l2_rank,
                )
            )

    order = sorted(
        range(len(merged)),
        key=lambda k: (-merged[k].joint_metric, merged[k].l1_rank, merged[k].l2_rank),
    )
    ranked = tuple(merged[k] for k in order)

    crc_true_int = int(crc_true)
    chosen = None
    crc_hat_chosen = None
    for cand in ranked:
        label = (cand.low + scl_joint_mod.LABEL_SCALE * cand.high).astype(np.int64)
        crc_hat = scl_joint_mod.labels_crc16(label)
        if crc_hat == crc_true_int:
            chosen = cand
            crc_hat_chosen = crc_hat
            break
    crc_failed = chosen is None
    if chosen is None:
        chosen = ranked[0]
        crc_hat_chosen = scl_joint_mod.labels_crc16(
            (chosen.low + scl_joint_mod.LABEL_SCALE * chosen.high).astype(np.int64)
        )

    label_hat = (chosen.low + scl_joint_mod.LABEL_SCALE * chosen.high).astype(np.int64)
    backend = native_backend_info()
    provenance = {
        "l1_provenance": p1_metric.provenance.value,
        "l2_provenance": Provenance.CANDIDATE_CONDITIONED.value,
        "merge_rule": "joint_metric desc, tie-break (l1_rank, l2_rank) asc",
        "prune_rule": "top_l_prune",
        "crc": "CRC-16/CCITT-FALSE, poly=0x1021, init=0xFFFF, MSB-first, no reflect, no xorout",
        "label_convention": "s = low + 32*high per position (two_layer.py LABEL_SCALE=32)",
        "top_m_requested": top_m,
        "top_m_default": scl_joint_mod.TOP_M_DEFAULT,
        "engine": f"scl_joint_native (ctypes, backend={backend['backend']})",
    }
    return scl_joint_mod.SCLJointResult(
        high_hat=chosen.high,
        low_hat=chosen.low,
        label_hat=label_hat,
        m1=chosen.m1,
        m2=chosen.m2,
        joint_metric=chosen.joint_metric,
        crc_true=crc_true_int,
        crc_hat=int(crc_hat_chosen),
        crc_pass=bool(not crc_failed),
        crc_failed=bool(crc_failed),
        crc_bits=scl_joint_mod.CRC_BITS,
        l1_survivor_count=l1_res.survivor_count,
        top_m_requested=top_m,
        top_m_used=top_m_used,
        candidates_considered=len(ranked),
        requested_width=int(list_width_L),
        ranked_candidates=ranked,
        metric_provenance=provenance,
    )
