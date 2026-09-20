"""List successive-cancellation (SCL) decoder over the frozen NB-Polar transform.

Thin list extension of the frozen reference SC decoder
(:mod:`comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc`): the same
row-vector kernel (``x0 = u0 + alpha*u1``, ``x1 = u1``), the same natural-log
normalized SC conditionals, and the same per-coordinate recursion. Each live
path carries its own segment-metric stack; the shared minus/plus kernels are
reused by module-attribute import from ``sc`` (internal ``chunk_rows=512``
default reused verbatim, never exposed as an ``scl_decode`` parameter).

Frozen contract (FREEZE_DRAFT.md section 3):

- Path metric: ``PM(path, i)`` is the sum over undisclosed ``j <= i`` of the
  natural-log SC conditional of the taken symbol, using the same normalized
  conditionals as ``sc_decode``. Disclosed positions contribute ``+0``
  (forced, never branched).
- Exact-zero (``-inf``) conditionals kill the branch immediately; kills are
  counted in ``pruned_count``. A disclosed value with ``-inf`` support kills
  that path; if every path dies at a disclosed position,
  ``ImpossibleDisclosedValueError`` is raised (same category as ``sc.py``).
- Cross-path tie-break is canonical and deterministic: larger metric first,
  then smaller symbol index (``sc.py`` argmax convention), then smaller path
  index. Candidates reach ``prune_rule`` in that canonical order.
- ``prune_rule`` is an opaque callable slot (mechanism values UNFROZEN)::
      prune_rule(path_metrics, position, is_spike, width_L) -> keep
  ``path_metrics`` is float64[P] over the canonically ordered finite
  candidates, ``position`` is the int U-coordinate, ``is_spike`` is a bool
  spike-stratum flag the decoder always passes as ``False`` (the decoder has
  no spike context; the slot carries it for future wiring), ``width_L`` is
  the requested int width. It returns survivor indices best-first with
  ``M <= L``. It must be deterministic (same inputs give the same keep set).
- ``L=1`` reproduces ``sc_decode`` bit-identically on ``u_hat``/``x_hat``,
  with ``path_metrics[0]`` equal to the sum of ``decision_log_scores`` over
  undisclosed positions.
- Error categories are carried verbatim from ``sc.py`` (metric contract,
  field/shape contract including the folded-in width contract, known-
  coordinate contract, ``ImpossibleDisclosedValueError``, numeric
  nonfinite); prune-slot misuse raises field/shape-contract errors.

No per-path per-position conditionals are stored (evidence-size rule).
Complexity mirrors ``sc.py`` per live path; this is a correctness reference,
not a throughput target. No data loading, no benchmark machinery, no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral

import numpy as np

from . import sc as sc_mod
from .transform import polar_transform

# Re-exported (same objects, no new error category).
ImpossibleDisclosedValueError = sc_mod.ImpossibleDisclosedValueError
NumericNonfiniteError = sc_mod.NumericNonfiniteError


@dataclass(frozen=True, eq=False)
class SCLResult:
    """List-decoder output: ranked candidates plus disclosure accounting."""

    u_candidates: np.ndarray  # int64[M,N] decoded source words, best-first
    x_candidates: np.ndarray  # int64[M,N] re-encoded words, best-first
    path_metrics: np.ndarray  # float64[M] accumulated log-scores, best-first
    survivor_count: int  # M, number of surviving paths (M <= L)
    requested_width: int  # L, caller-requested list width
    pruned_count: int  # total pruned branches across positions, descriptive
    status: str  # terminal status; "ok" on every returned result
    known_count: int  # number of disclosed coordinates
    known_mask: np.ndarray  # bool[N]; True marks disclosed positions
    metric_provenance: dict  # sc.py provenance + list width + prune_rule name


class _Path:
    """Mutable per-path decode state (internal only, never returned)."""

    __slots__ = ("prefix", "metric", "blocks")

    def __init__(self, prefix, metric, blocks):
        self.prefix = prefix  # list[int], decisions so far in natural order
        self.metric = metric  # float, accumulated undisclosed log-score
        self.blocks = blocks  # list[(s,q) float64], segment stack, root first


def _check_width(list_width_L: int) -> int:
    if isinstance(list_width_L, bool) or not isinstance(list_width_L, Integral):
        raise TypeError(
            f"field/shape contract: list_width_L must be a positive integer, got {list_width_L!r}"
        )
    width = int(list_width_L)
    if width <= 0:
        raise ValueError(
            f"field/shape contract: list_width_L must be positive, got {list_width_L!r}"
        )
    return width


def _check_keep(keep, n_candidates: int, width: int) -> np.ndarray:
    arr = np.asarray(keep)
    if arr.dtype.kind == "b":
        raise TypeError(
            "field/shape contract: prune_rule keep must hold integer indices, got boolean input"
        )
    if arr.ndim != 1:
        raise ValueError("field/shape contract: prune_rule keep must be one-dimensional")
    if arr.dtype.kind not in "iu":
        raise TypeError(
            "field/shape contract: prune_rule keep must hold integer indices, "
            f"got dtype {arr.dtype}"
        )
    out = arr.astype(np.int64, copy=True)
    if out.size == 0:
        raise ValueError("field/shape contract: prune_rule must keep at least one path")
    if out.size > width:
        raise ValueError(
            f"field/shape contract: prune_rule kept {out.size} paths, "
            f"at most list_width_L={width} allowed"
        )
    if out.min() < 0 or out.max() >= n_candidates:
        raise ValueError(
            "field/shape contract: prune_rule keep indices must lie in "
            f"0..{n_candidates - 1}"
        )
    if len(set(out.tolist())) != out.size:
        raise ValueError("field/shape contract: prune_rule keep must not repeat indices")
    return out


def scl_decode(
    logp_x,
    *,
    field,
    alpha: int = 2,
    known_positions=None,
    known_values=None,
    list_width_L,
    prune_rule,
) -> SCLResult:
    """Run list SC decoding and return ranked candidates plus accounting.

    ``logp_x``/``field``/``alpha``/``known_positions``/``known_values`` are
    contract-identical to ``sc_decode``; input ``known_positions`` order is
    irrelevant. ``list_width_L`` is a caller-supplied positive integer with
    no default. ``prune_rule`` is the opaque survivor-selection callable
    described in the module docstring (test-only top-L stub in tests).
    """
    q, alpha = sc_mod._check_field(field, alpha)
    metrics, n = sc_mod._validate_metric(logp_x, q)
    known = sc_mod._validate_known(known_positions, known_values, n, q)
    width = _check_width(list_width_L)
    if not callable(prune_rule):
        raise TypeError(
            f"field/shape contract: prune_rule must be callable, got {prune_rule!r}"
        )
    index = sc_mod._combination_index(field, alpha, q)

    live_paths = [_Path([], 0.0, [metrics])]
    pruned_total = [0]

    def decode_leaf(position: int) -> None:
        rows = [(path, path.blocks[-1][0]) for path in live_paths]
        if position in known:
            value = known[position]
            survivors = []
            for path, row in rows:
                score = row[value]
                if score == -np.inf:
                    pruned_total[0] += 1
                    continue
                if not np.isfinite(score):
                    raise sc_mod.NumericNonfiniteError(
                        f"numeric nonfinite failure: nonfinite score at U[{position}]"
                    )
                path.prefix.append(value)
                path.metric += 0.0
                survivors.append(path)
            if not survivors:
                raise sc_mod.ImpossibleDisclosedValueError(
                    f"impossible disclosed value: U[{position}]={value} "
                    "has exact-zero support"
                )
            live_paths[:] = survivors
            return
        cand_path: list[int] = []
        cand_symbol: list[int] = []
        cand_metric: list[float] = []
        for path_idx, (path, row) in enumerate(rows):
            if not np.isfinite(row).any():
                pruned_total[0] += q
                continue
            for symbol in range(q):
                score = row[symbol]
                if score == -np.inf:
                    pruned_total[0] += 1
                    continue
                if not np.isfinite(score):
                    raise sc_mod.NumericNonfiniteError(
                        f"numeric nonfinite failure: nonfinite score at U[{position}]"
                    )
                cand_path.append(path_idx)
                cand_symbol.append(symbol)
                cand_metric.append(path.metric + float(score))
        if not cand_path:
            raise sc_mod.NumericNonfiniteError(
                f"numeric nonfinite failure: no finite support at U[{position}]"
            )
        path_arr = np.asarray(cand_path, dtype=np.int64)
        symbol_arr = np.asarray(cand_symbol, dtype=np.int64)
        metric_arr = np.asarray(cand_metric, dtype=np.float64)
        order = np.lexsort((path_arr, symbol_arr, -metric_arr))
        ordered_metrics = metric_arr[order]
        keep = _check_keep(prune_rule(ordered_metrics, position, False, width), len(order), width)
        pruned_total[0] += len(order) - int(keep.size)
        survivors = []
        for slot in keep.tolist():
            source = int(order[int(slot)])
            parent = rows[int(path_arr[source])][0]
            child = _Path(
                parent.prefix + [int(symbol_arr[source])],
                float(metric_arr[source]),
                list(parent.blocks),
            )
            survivors.append(child)
        live_paths[:] = survivors

    def decode_segment(offset: int, size: int) -> None:
        if size == 1:
            decode_leaf(offset)
            return
        half = size // 2
        for path in live_paths:
            parent = path.blocks[-1]
            path.blocks.append(sc_mod._minus_block(parent[:half], parent[half:], index))
        decode_segment(offset, half)
        for path in live_paths:
            path.blocks.pop()
            parent = path.blocks[-1]
            beta = polar_transform(
                np.asarray(path.prefix[offset : offset + half], dtype=np.int64),
                field=field,
                alpha=alpha,
            )
            path.blocks.append(sc_mod._plus_block(parent[:half], parent[half:], beta, index))
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
        [polar_transform(row, field=field, alpha=alpha) for row in u_candidates]
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
        "kernel": "row-vector F_alpha with x0=u0+alpha*u1, x1=u1, natural order",
        "q": q,
        "alpha": alpha,
        "primitive_polynomial": getattr(field, "primitive_polynomial", None),
        "list_width_L": width,
        "prune_rule": getattr(prune_rule, "__name__", type(prune_rule).__name__),
    }
    return SCLResult(
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
