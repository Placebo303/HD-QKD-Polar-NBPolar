"""Numba-accelerated drop-in replacement for ``scl_joint.scl_joint_decode``.

Authorization: PI ruling 2026-09-29 ("SCL 提速...其它语言的提速也能接受"),
this session (coder-fast). Frozen files untouched: ``scl.py``, ``sc.py``,
``scl_joint.py``, ``two_layer.py``, ``prior.py``, ``transform.py``,
``nonbinary_field.py`` are only imported by public module attribute, never
edited or monkeypatched.

Why this module exists
-----------------------
``scl_joint.scl_joint_decode`` (M=4, two independent ``scl.scl_decode`` calls
per L1 candidate) is a correctness reference, not a throughput target -- its
own docstrings say so explicitly. At N=32768, list_width_L=16 it measures
~450-520 s/block (``workspace/probes/scl-joint-timing/timing.json``), too slow
for the planned efficiency sweeps. Profiling (same probe's CODE_REVIEW.md and
its underlying timing capture) attributes >99% of wall time to
``sc.py::_minus_block``/``_plus_block`` (materializing a ``(rows, q, q)``
NumPy temporary per call, then ``np.logaddexp.reduce``) and
``transform.py::polar_transform`` calling ``nonbinary_field.GF2mField.add``/
``mul`` (Python method calls with ``isinstance``/``Integral`` ABC checks) tens
of millions of times.

What changed vs. the reference algorithm
-----------------------------------------
Only the *numerical implementation* of three primitives, never the frozen
*algorithm* or *tie-break rule*:

1. GF(32) ``add``/``mul`` -> precomputed lookup tables (XOR is closed-form;
   ``mul_row[v] = field.mul(alpha, v)`` is a 32-entry table built once per
   decode call from the frozen ``GF2mField`` -- the field object itself is
   still the single source of truth for the table values).
2. ``sc._minus_block``/``sc._plus_block`` -> ``@njit(parallel=True)`` kernels
   (:func:`_minus_block_fast`, :func:`_plus_block_fast`) that compute the same
   ``logsumexp_v L0[u+alpha*v] + L1[v]`` quantity per row without allocating a
   ``(rows, q, q)`` temporary, using a scalar :func:`_logaddexp2` folded
   sequentially left-to-right over the q axis -- the same order and the same
   branch structure (``a==b`` fast path, else ``amax + log1p(exp(-|diff|))``)
   as NumPy's ``logaddexp`` C ufunc loop, so a fold over it matches
   ``np.logaddexp.reduce`` closely, not just approximates it (an earlier
   two-pass max-trick prototype was tried and rejected here: mathematically
   equivalent but *not* the same operation order, and empirically produced
   far more ~1e-15 rounding flips against ``sc.py``'s own near-ties -- see the
   commit history / :func:`_logaddexp2` docstring). Row/global normalization
   (``logsumexp == 0``, exact-zero rows kept as ``-inf``) is preserved.
3. ``transform.polar_transform`` -> :func:`_polar_transform_fast`, the exact
   same natural-order butterfly loop (same ``base``/``size`` stepping order),
   with ``field.add(u0, field.mul(a, u1))`` replaced by ``u0 ^ mul_row[u1]``.
   This is integer XOR/table-lookup arithmetic: bit-identical to the frozen
   ``transform.py`` for every input, no rounding difference possible.

The list-decoding *control flow* (path list, segment-metric stack, leaf
decision, canonical tie-break, top-L truncation, final ranking) is copied
verbatim from ``scl.py``'s structure in :func:`_scl_decode_fast` -- same
recursion shape, same ``(path_arr, symbol_arr, -metric_arr)`` lexsort key,
same ``pruned_count`` accounting, same ``argsort(-final_metrics,
kind="stable")`` final order. The one deliberate simplification: this module
is used only from :func:`scl_joint_decode_fast`, which -- exactly like
``scl_joint.scl_joint_decode`` -- always uses the frozen ``top_l_prune``
(``keep the largest-metric width_L paths, stable order``); because candidates
already arrive at that rule in canonical desc order, ``top_l_prune`` reduces
to slicing the first ``width`` entries, so :func:`_scl_decode_fast` has no
generic ``prune_rule`` slot (unlike ``scl.scl_decode``). It is not a
general-purpose replacement for ``scl.scl_decode``.

:func:`scl_joint_decode_fast` is otherwise a line-for-line copy of
``scl_joint.scl_joint_decode``'s merge/CRC/ranking logic (imported, not
reimplemented, from ``scl_joint`` itself: ``top_l_prune`` naming,
``JointCandidate``, ``SCLJointResult``, ``labels_crc16``, ``LABEL_SCALE``,
``TOP_M_DEFAULT``), with only the inner ``scl.scl_decode`` calls swapped for
``_scl_decode_fast``. Equivalence is a *test-verified numerical claim*, not
architectural sharing: see
``comparison_bench/tests/test_nbpolar_scl_joint_fast.py`` T-F1 for the
per-block agreement statistics and the known-near-tie carve-out (the same
``scl.py``/``sc.py`` float64 near-tie sensitivity documented in
``workspace/probes/scl-joint-timing/CODE_REVIEW.md`` FAIL-1 and
``test_nbpolar_scl_joint.py::test_scl_l1_vs_sc_decode_known_tiebreak_mismatch``
applies here too, plus this module's own residual rounding difference from
using scalar ``exp``/``log1p`` calls -- via LLVM/numba's lowering -- rather
than NumPy's ufunc loop for the same formula, on top of it).

No data loading, no benchmark/output machinery, no I/O, no real data.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numba import njit, prange

from . import scl as scl_mod
from . import scl_joint as scl_joint_mod
from . import sc as sc_mod
from .prior import Provenance, gather_p2_metrics, probs_to_symbol_metric
from . import two_layer as two_layer_mod

__all__ = [
    "scl_joint_decode_fast",
    "SCLResultFast",
]


# --------------------------------------------------------------------------
# Numba kernels: same math as sc.py's _minus_block/_plus_block/normalize and
# transform.py's polar_transform, no GF2mField object calls in the hot loop.
# --------------------------------------------------------------------------


LOGE2 = 0.6931471805599453094172321214581766  # np.log(2.0), matches NPY_LOGE2


@njit(cache=True, inline="always")
def _logaddexp2(a: float, b: float) -> float:
    """Scalar ``log(exp(a)+exp(b))``; same branch structure as NumPy's
    ``logaddexp`` C ufunc loop (``a==b`` fast path, else stable ``amax +
    log1p(exp(-|diff|))``), so a sequential fold over this matches
    ``np.logaddexp.reduce`` to the same rounding, not just the same value.
    """
    if a == b:
        return a + LOGE2
    diff = a - b
    if diff > 0.0:
        return a + np.log1p(np.exp(-diff))
    else:
        return b + np.log1p(np.exp(diff))


@njit(cache=True, parallel=True)
def _minus_block_fast(first: np.ndarray, second: np.ndarray, index: np.ndarray) -> np.ndarray:
    """``out[r,a] = normalize_a( logsumexp_v(first[r, index[a,v]] + second[r,v]) )``.

    Same quantity as ``sc._minus_block(..., chunk_rows=None)``, computed with
    the *same* sequential left-to-right ``logaddexp`` fold that
    ``np.logaddexp.reduce`` performs over an axis of length q=32 (below
    NumPy's pairwise-summation threshold, which in any case only applies to
    ``np.add``, not ``logaddexp``) -- chosen deliberately over a two-pass
    max-trick log-sum-exp (tried first; empirically produced far more
    tie-break-flipping ~1e-15 rounding differences against ``sc.py``, because
    every such flip cascades through the rest of the SC recursion) to keep
    this reimplementation's numerical output close to bit-identical with the
    frozen reference on non-tied inputs, matching (not just approximating)
    ``sc.py``'s own rounding.
    """
    rows = first.shape[0]
    q = first.shape[1]
    out = np.empty((rows, q), dtype=np.float64)
    for r in prange(rows):
        frow = first[r]
        srow = second[r]
        for a in range(q):
            acc = frow[index[a, 0]] + srow[0]
            for v in range(1, q):
                val = frow[index[a, v]] + srow[v]
                acc = _logaddexp2(acc, val)
            out[r, a] = acc
        lse = out[r, 0]
        for a in range(1, q):
            lse = _logaddexp2(lse, out[r, a])
        if lse == -np.inf:
            continue  # all-(-inf) row: sc._normalize_rows leaves it untouched
        for a in range(q):
            out[r, a] -= lse
    return out


@njit(cache=True, parallel=True)
def _plus_block_fast(first: np.ndarray, second: np.ndarray, beta: np.ndarray, index: np.ndarray) -> np.ndarray:
    """``out[r,v] = normalize_v( first[r, index[beta[r],v]] + second[r,v] )``.

    Same quantity as ``sc._plus_block``; normalization uses the same
    sequential ``logaddexp`` fold as :func:`_minus_block_fast`.
    """
    rows = first.shape[0]
    q = first.shape[1]
    out = np.empty((rows, q), dtype=np.float64)
    for r in prange(rows):
        frow = first[r]
        srow = second[r]
        b = beta[r]
        for v in range(q):
            out[r, v] = frow[index[b, v]] + srow[v]
        lse = out[r, 0]
        for v in range(1, q):
            lse = _logaddexp2(lse, out[r, v])
        if lse == -np.inf:
            continue
        for v in range(q):
            out[r, v] -= lse
    return out


@njit(cache=True, parallel=True)
def _polar_transform_batch_fast(symbols: np.ndarray, mul_row: np.ndarray) -> np.ndarray:
    """Batched :func:`_polar_transform_fast` over independent rows (one per
    live SCL path). Used by :func:`_scl_decode_fast` to compute every live
    path's ``beta`` in one numba call instead of ``L`` separate tiny calls --
    see the module docstring's note on path-batching the ``minus``/``plus``
    kernels for why call count (not per-call FLOPs) is the bottleneck near
    the leaves of the recursion.
    """
    rows, n = symbols.shape
    out = symbols.copy()
    for r in prange(rows):
        row = out[r]
        size = 1
        while size < n:
            step = 2 * size
            base = 0
            while base < n:
                for j in range(size):
                    u0 = row[base + j]
                    u1 = row[base + j + size]
                    row[base + j] = u0 ^ mul_row[u1]
                base += step
            size *= 2
    return out


@njit(cache=True)
def _polar_transform_fast(symbols: np.ndarray, mul_row: np.ndarray) -> np.ndarray:
    """Bit-identical to ``transform.polar_transform`` for the fixed ``a=alpha``.

    Same natural-order butterfly loop (``x0 = u0 ^ mul_row[u1]``, ``x1 = u1``);
    XOR/table-lookup integer arithmetic only, so this is an exact
    reimplementation, not an approximation -- unlike the log-domain kernels
    above there is no rounding difference to disclose.
    """
    out = symbols.copy()
    n = out.shape[0]
    size = 1
    while size < n:
        step = 2 * size
        base = 0
        while base < n:
            for j in range(size):
                u0 = out[base + j]
                u1 = out[base + j + size]
                out[base + j] = u0 ^ mul_row[u1]
            base += step
        size *= 2
    return out


def _mul_row_table(field, alpha: int) -> np.ndarray:
    """``mul_row[v] = field.mul(field.add(alpha, 0), v)`` for ``v in 0..q-1``.

    Built once per decode call from the frozen field object (single source of
    truth for the table values); 32 Python calls, negligible next to the
    O(N log N) kernels above.
    """
    a = field.add(alpha, 0)
    q = field.q
    row = np.empty(q, dtype=np.int64)
    for v in range(q):
        row[v] = field.mul(a, v)
    return row


# --------------------------------------------------------------------------
# List-SC engine: same control-flow shape as scl.py's scl_decode, swapping
# only the three primitives above. Frozen top_l_prune hardcoded (see module
# docstring) -- no generic prune_rule slot.
# --------------------------------------------------------------------------


class _FastPath:
    __slots__ = ("prefix", "metric", "blocks")

    def __init__(self, prefix, metric, blocks):
        self.prefix = prefix
        self.metric = metric
        self.blocks = blocks


@dataclass(frozen=True, eq=False)
class SCLResultFast:
    """Same field set as ``scl.SCLResult``; independent dataclass (own module)."""

    u_candidates: np.ndarray
    x_candidates: np.ndarray
    path_metrics: np.ndarray
    survivor_count: int
    requested_width: int
    pruned_count: int
    status: str
    known_count: int
    known_mask: np.ndarray
    metric_provenance: dict


def _scl_decode_fast(
    logp_x,
    *,
    field,
    alpha: int = 2,
    known_positions=None,
    known_values=None,
    list_width_L: int,
) -> SCLResultFast:
    """Fast list-SC decode; frozen top_l_prune only (see module docstring).

    Validation (``metric contract``, ``field/shape contract``,
    ``known-coordinate contract``) is reused verbatim from ``sc.py``/``scl.py``
    private helpers -- these run once per decode call, not in the hot loop, so
    reusing them costs nothing and keeps every error category and message
    identical to the frozen reference.
    """
    q, alpha = sc_mod._check_field(field, alpha)
    metrics, n = sc_mod._validate_metric(logp_x, q)
    known = sc_mod._validate_known(known_positions, known_values, n, q)
    width = scl_mod._check_width(list_width_L)
    index = sc_mod._combination_index(field, alpha, q)
    mul_row = _mul_row_table(field, alpha)

    live_paths = [_FastPath([], 0.0, [metrics])]
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
            child = _FastPath(parent.prefix + [symbol], metric_val, list(parent.blocks))
            survivors.append(child)
        live_paths[:] = survivors

    def decode_segment(offset: int, size: int) -> None:
        if size == 1:
            decode_leaf(offset)
            return
        half = size // 2
        # Batch every live path's minus/plus/transform call into one numba
        # invocation (concatenated along axis 0) instead of one call per path.
        # sc.py/scl.py call these once *per path*; for L paths and ~2*(N-1)
        # internal nodes that is up to 2*(N-1)*L tiny numba dispatches, most
        # of them (near the leaves) doing O(1) rows of real work each -- call
        # overhead, not FLOPs, dominates there. Concatenating first cuts the
        # call count back to ~2*(N-1) regardless of L, and gives prange more
        # rows per launch to actually parallelize over.
        firsts = np.concatenate([path.blocks[-1][:half] for path in live_paths], axis=0)
        seconds = np.concatenate([path.blocks[-1][half:] for path in live_paths], axis=0)
        combined = _minus_block_fast(firsts, seconds, index)
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
        betas = _polar_transform_batch_fast(prefixes, mul_row).reshape(-1)
        combined2 = _plus_block_fast(firsts2, seconds2, betas, index)
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
    x_candidates = np.stack(
        [_polar_transform_fast(row, mul_row) for row in u_candidates]
    ).astype(np.int64, copy=False)
    path_metrics = final_metrics[final_order]
    known_mask = np.zeros(n, dtype=bool)
    known_mask[list(known)] = True
    provenance = {
        "input_role": "prior: logp_x[j,a] = ln P(X_j=a | Bob/context), rows normalized to logsumexp 0",
        "row_role": "classic source SC conditionals: per-path metrics accumulate ln P(U_i=u_i | prefix, B/context), suffix marginalized",
        "log_base": "natural",
        "normalization": "float64; every produced row normalized, exact-zero support kept as -inf",
        "tie_break": "larger path metric first, then smallest symbol index, then smallest path index",
        "kernel": "row-vector F_alpha with x0=u0+alpha*u1, x1=u1, natural order (numba/table-based)",
        "q": q,
        "alpha": alpha,
        "primitive_polynomial": getattr(field, "primitive_polynomial", None),
        "list_width_L": width,
        "prune_rule": "top_l_prune",
        "engine": "scl_joint_fast (numba njit, sequential logaddexp fold)",
    }
    return SCLResultFast(
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


# --------------------------------------------------------------------------
# Joint two-layer CRC-aided decode: same merge/CRC/ranking as scl_joint.py.
# --------------------------------------------------------------------------


def scl_joint_decode_fast(
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
    """Numba-accelerated drop-in for ``scl_joint.scl_joint_decode``.

    Identical inputs/outputs (``scl_joint.SCLJointResult``) and identical
    merge/CRC/ranking logic (imported from ``scl_joint``, not reimplemented);
    only the inner list-SC engine is :func:`_scl_decode_fast` instead of
    ``scl.scl_decode``. See module docstring for the numerical difference and
    ``test_nbpolar_scl_joint_fast.py`` T-F1 for the measured agreement rate.
    """
    if isinstance(top_m, bool) or int(top_m) <= 0:
        raise ValueError(f"field/shape contract: top_m must be a positive integer, got {top_m!r}")
    top_m = int(top_m)

    bob_row = np.asarray(bob)[None, :]
    p1_probs = two_layer_mod.build_p1_metrics(bob_row, p1_table)[0]
    p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)

    l1_res = _scl_decode_fast(
        p1_metric.logp,
        field=field,
        alpha=alpha,
        known_positions=d1_positions,
        known_values=d1_values,
        list_width_L=list_width_L,
    )

    top_m_used = min(top_m, l1_res.survivor_count)
    merged: list = []
    for l1_rank in range(top_m_used):
        high_cand = l1_res.x_candidates[l1_rank]
        m1 = float(l1_res.path_metrics[l1_rank])
        p2_probs = gather_p2_metrics(bob_row, high_cand[None, :], p2_table)[0]
        p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
        l2_res = _scl_decode_fast(
            p2_metric.logp,
            field=field,
            alpha=alpha,
            known_positions=d2_positions,
            known_values=d2_values,
            list_width_L=list_width_L,
        )
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
        range(len(merged)), key=lambda k: (-merged[k].joint_metric, merged[k].l1_rank, merged[k].l2_rank)
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
    provenance = {
        "l1_provenance": p1_metric.provenance.value,
        "l2_provenance": Provenance.CANDIDATE_CONDITIONED.value,
        "merge_rule": "joint_metric desc, tie-break (l1_rank, l2_rank) asc",
        "prune_rule": "top_l_prune",
        "crc": "CRC-16/CCITT-FALSE, poly=0x1021, init=0xFFFF, MSB-first, no reflect, no xorout",
        "label_convention": "s = low + 32*high per position (two_layer.py LABEL_SCALE=32)",
        "top_m_requested": top_m,
        "top_m_default": scl_joint_mod.TOP_M_DEFAULT,
        "engine": "scl_joint_fast (numba njit, sequential logaddexp fold)",
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
