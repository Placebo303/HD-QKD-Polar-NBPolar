"""NB-Polar Phase 4-P7 target-population empirical construction gate.

Frozen point (packet ``NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION``,
OpenSpec ``formal-ir-nbpolar-phase4-p0`` P7 delta): build and execute one
target-population, model-sampled NB-Polar development gate from the V25 ``1M``
TRAIN count matrix -- not the Model-F CAL artifact rejected for this purpose by
X07 -- and test whether pooled empirical genie orders support reliable
two-layer hard-candidate SC at a conservative fixed disclosure point.

Frozen semantics:

- Input: one call to the accepted ``load_v25_channel_counts(path)``; a stat-only
  size check of exactly ``25,166,822`` bytes happens before the content open,
  and the single artifact read plus the single scientific attempt are consumed
  at the first NPZ content open (never reopened, never retried).
- Support rule (the only one): column-normalize the raw counts, replace every
  cell below ``1e-15`` by ``1e-15``, renormalize each Bob column; ``p_b`` from
  the column totals; accepted ``derive_p1``/``derive_p2`` under the packing
  ``A = 32*U1 + U2``.  No lambda, backoff, tuning, floor scan or held-out
  fitting.
- Preconditions before any genie/SC call: no zero Bob column; ``p_b`` and
  conditional column error ``<= 1e-12``; ``H1``/``H2``/total within ``1e-12``
  of the V49 1M TRAIN literals; floor-induced total-entropy change relative to
  the raw MLE table ``<= 1e-9``.  Failure is
  ``BLOCKED(target_population_contract)`` and creates no output root.
- Construction: GF32 (primitive polynomial 37, alpha 2, natural order),
  ``N=256``; TRAIN ``2026091650..2026091652`` x 256 blocks; DEV
  ``2026091660..2026091664`` x 128 common blocks (640 pairs); per-DEV-stream
  public Toeplitz master ``stream + 10000``, domain-separated by arm/block.
  Sampling is ``B ~ p_b`` then ``A ~ P_floor(A|B)`` with ``high = A//32``,
  ``low = A%32``.  L1 and oracle-conditioned L2 use the accepted
  ``genie_conditionals`` accumulation per TRAIN stream and pooled; pooled
  worst-first orders are frozen before any DEV call.  BEC analytic controls use
  ``epsilon_l = H_l/5`` and are report-only.
- DEV: two paired arms per block (empirical pooled orders; BEC control orders),
  each with a fresh per-layer SC restart, the rebuilt 10-bit label, one 64-bit
  Toeplitz tag and the accepted outcome buckets
  (``exact``/``undetected``/``verify_failed``/``decode_failed``/
  ``resource_abort``).  Alice truth enters only sampling, disclosed values, tag
  construction and scoring.
- Accounting: a fully invoked arm discloses exactly ``5*(45+140)+64 = 989``
  key-dependent bits and ``2623`` public control bits per invoked tag, with an
  independent literal transcript recount.

The only output is the explicit CLI and its five compact scalar-only files;
symbols, labels, disclosed values, decoded keys and raw seed bits are never
persisted.  No Model-F/held-out/raw/real frame, no ``N>256``, no APP/SCL/FWHT,
no production benchmark, no commit.  The claim scope is a construction/protocol
development signal for the frozen V25 TRAIN empirical distribution at ``N=256``
only -- not held-out or real frame FER, efficiency, key rate, scaling,
qualification or promotion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass, replace
from numbers import Integral, Real
from pathlib import Path

import numpy as np

from ..shared import canonical_event, toeplitz_tag
from ..v35_algorithm_development import load_v25_channel_counts
from .algebra import make_gf32
from .construction import (
    analytic_order,
    disclosure_order_from_stats,
    genie_conditionals,
    spearman_rank_corr,
    topk_overlap,
)
from .empirical_channel import sample_full_block
from .prior import (
    Provenance,
    build_p1_metrics,
    derive_p1,
    derive_p2,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from .protocol import WILSON_Z, wilson_lower_bound
from .sc import ImpossibleDisclosedValueError, NumericNonfiniteError, sc_decode
from .transform import polar_transform
from .two_layer import (
    DISCLOSED_BITS_PER_COORDINATE,
    LABEL_SCALE,
    OUTCOMES,
    TAG_BITS,
    labels_to_bits,
    seed_bits_for,
)

try:  # POSIX (the frozen command runs under WSL); Windows native has no resource module.
    import resource
except ImportError:  # pragma: no cover - exercised only on Windows native
    resource = None

PROTOCOL_NAME = "nbpolar-p7-target-empirical-construction-gate"
MODE = "paired-target-population-dev-gate"

Q = 32
ALPHA = 2
FROZEN_N = 256
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_TRAIN_SEEDS = (2026091650, 2026091651, 2026091652)
FROZEN_TRAIN_BLOCKS = 256
FROZEN_DEV_SEEDS = (2026091660, 2026091661, 2026091662, 2026091663, 2026091664)
FROZEN_DEV_BLOCKS = 128
FROZEN_PAIRS = 640
FROZEN_K1 = 45
FROZEN_K2 = 140
PUBLIC_TAG_MASTER_OFFSET = 10000

EXPECTED_NPZ_BYTES = 25166822
FROZEN_COUNTS_PATH = (
    "/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/"
    "nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/"
    "target_construction_gate"
)
LOADER_IDENTITY = (
    "comparison_bench.src.comparison_bench.formal_ir."
    "v35_algorithm_development.load_v25_channel_counts"
)

EXPECTED_H1 = 0.02428054681872374
EXPECTED_H2 = 0.7767572780789994
EXPECTED_TOTAL = 0.8010378248977232
ENTROPY_TOL = 1e-12
COLUMN_TOL = 1e-12
FLOOR_ENTROPY_TOL = 1e-9

SPEARMAN_MIN = 0.95
EXACT_MIN = 620
WILSON_MIN = 0.95

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 3600.0
EXTERNAL_TIMEOUT_S = 3600
ULIMIT_VIRTUAL_KIB = 2097152

ARMS = ("empirical", "bec")
CELLS = ("both_exact", "empirical_only", "bec_only", "neither")
FULLY_INVOKED_ARM_BITS = DISCLOSED_BITS_PER_COORDINATE * (FROZEN_K1 + FROZEN_K2) + TAG_BITS
L1_DISCLOSURE_BITS = DISCLOSED_BITS_PER_COORDINATE * FROZEN_K1
L2_DISCLOSURE_BITS = DISCLOSED_BITS_PER_COORDINATE * FROZEN_K2
PUBLIC_CONTROL_BITS_PER_TAG = seed_bits_for(FROZEN_N)  # 2623

ATTEMPT_CONSUMPTION_POINT = "first NPZ content open (load_v25_channel_counts)"
ARTIFACT_READ_ACCOUNTING = {
    "artifact_content_reads_allowed": 1,
    "artifact_content_reads_consumed_before": 0,
    "artifact_content_reads_consumed_by_this_run": 1,
    "attempts_allowed": 1,
    "attempts_consumed_before": 0,
    "attempts_consumed_by_this_run": 1,
    "retries": 0,
    "reopen_attempted": False,
    "retry_after_open": False,
}

SUPPORT_RULE = (
    "f = counts / column totals; every cell below 1e-15 replaced by 1e-15; "
    "columns renormalized; p_b = column totals / total count; "
    "P1/P2 = accepted derive_p1/derive_p2(f) under A=32*U1+U2; "
    "no lambda, backoff, tuning, floor scan or held-out fitting"
)
SAMPLING_RULE = (
    "per block: B ~ p_b (rng.random(n) against the cumulative p_b), then "
    "A ~ P_floor(A|B) per coordinate (rng.random(n) against the cumulative "
    "column); high=A//32, low=A%32; explicit np.random.default_rng(stream "
    "seed), one stream RNG, no global RNG"
)
TRUTH_BOUNDARY = (
    "Alice truth enters only sampling, disclosed values, tag construction and "
    "scoring; it never enters an undisclosed operational metric, decision or "
    "candidate label; each arm restarts SC per layer with no state transfer"
)
BEC_RULE = "epsilon_l = H_l / 5; analytic_order(epsilon_l, n); report-only control"

OUTCOME_PRECEDENCE = [
    "resource_abort: block not executed (preregistered budget stop)",
    "decode_failed: L1 or L2 SC exception / nonfinite marginals; no tag",
    "verify_failed: tag mismatch",
    "exact: tag pass and label == true label",
    "undetected: tag pass and not exact (never success)",
]

PRECONDITION_ORDER = (
    "no_zero_bob_column",
    "p_b_normalized",
    "conditional_columns_normalized",
    "h1_matches_literal",
    "h2_matches_literal",
    "total_matches_literal",
    "floor_entropy_change_at_most_1e-9",
)
INTEGRITY_GATE_ORDER = (
    "target_population_contract",
    "coverage_complete_and_disjoint",
    "orders_frozen_permutations_provenance",
    "pairing_and_buckets",
    "truth_leak_zero",
    "undetected_zero",
    "nonfinite_zero",
    "resource_abort_zero",
    "disclosure_and_recount_exact",
    "attempt_read_accounting_exact",
    "resource_limits_met",
)
SCIENTIFIC_GATE_ORDER = (
    "train_spearman_min_at_least_0p95",
    "empirical_exact_at_least_620_of_640",
    "empirical_wilson_lower_bound_at_least_0p95",
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "construction_orders.json",
    "per_block_paired_outcomes.json",
    "aggregate_summary.json",
    "report.md",
)

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "ulimit -v 2097152\n"
    "timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_construction "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --n 256 --floor 1e-15 "
    "--train-seeds 2026091650 2026091651 2026091652 --train-blocks 256 "
    "--dev-seeds 2026091660 2026091661 2026091662 2026091663 2026091664 "
    "--dev-blocks 128 --k1 45 --k2 140 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)
CLAIM_SCOPE = (
    "frozen V25 TRAIN target-population empirical construction development "
    "signal at N=256 only; not held-out or real frame FER, efficiency, key "
    "rate, scaling, qualification or promotion; planning-only f is not "
    "real-channel efficiency; undetected is never success"
)
SEED_PREFIX = "nbpolar-p7-target-construction-seed"

__all__ = [
    "PROTOCOL_NAME",
    "MODE",
    "Q",
    "ALPHA",
    "FROZEN_N",
    "FROZEN_SOURCE",
    "FROZEN_FLOOR",
    "FROZEN_TRAIN_SEEDS",
    "FROZEN_TRAIN_BLOCKS",
    "FROZEN_DEV_SEEDS",
    "FROZEN_DEV_BLOCKS",
    "FROZEN_PAIRS",
    "FROZEN_K1",
    "FROZEN_K2",
    "PUBLIC_TAG_MASTER_OFFSET",
    "EXPECTED_NPZ_BYTES",
    "FROZEN_COUNTS_PATH",
    "FROZEN_OUT_ROOT",
    "LOADER_IDENTITY",
    "EXPECTED_H1",
    "EXPECTED_H2",
    "EXPECTED_TOTAL",
    "ENTROPY_TOL",
    "COLUMN_TOL",
    "FLOOR_ENTROPY_TOL",
    "SPEARMAN_MIN",
    "EXACT_MIN",
    "WILSON_MIN",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S",
    "ULIMIT_VIRTUAL_KIB",
    "ARMS",
    "CELLS",
    "FULLY_INVOKED_ARM_BITS",
    "L1_DISCLOSURE_BITS",
    "L2_DISCLOSURE_BITS",
    "PUBLIC_CONTROL_BITS_PER_TAG",
    "ATTEMPT_CONSUMPTION_POINT",
    "ARTIFACT_READ_ACCOUNTING",
    "SUPPORT_RULE",
    "SAMPLING_RULE",
    "TRUTH_BOUNDARY",
    "BEC_RULE",
    "OUTCOME_PRECEDENCE",
    "PRECONDITION_ORDER",
    "INTEGRITY_GATE_ORDER",
    "SCIENTIFIC_GATE_ORDER",
    "OUTPUT_FILES",
    "FROZEN_COMMAND",
    "CLAIM_SCOPE",
    "SeedPrefixError",
    "TargetPopulationContractError",
    "TargetConstructionResourceError",
    "TargetConditional",
    "EntropyReport",
    "PreconditionReport",
    "DevArmResult",
    "PairedBlockResult",
    "TargetConstructionRun",
    "entropy_bits",
    "build_target_conditional",
    "target_entropies",
    "target_preconditions",
    "sample_target_block",
    "accumulate_genie",
    "order_from_acc",
    "pool_accumulators",
    "position_rank",
    "spearman_orders",
    "bec_orders",
    "arm_seed_bits",
    "classify_outcome",
    "classify_pair",
    "run_dev_arm",
    "run_dev_block",
    "block_events",
    "recount_events",
    "run_target_construction",
    "build_parser",
    "main",
]


class SeedPrefixError(ValueError):
    """Internal misuse of an invalid arm/block seed request (frozen prefix)."""


class TargetPopulationContractError(ValueError):
    """The frozen target-population contract failed before any genie/SC call."""


class TargetConstructionResourceError(RuntimeError):
    """The wall/RSS budget was exceeded before the DEV phase could complete."""


def _as_int(value, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer, got {value!r}")
    out = int(value)
    if minimum is not None and out < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {out}")
    return out


def _check_floor(value) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"floor must be a real number, got {value!r}")
    out = float(value)
    if not np.isfinite(out) or not 0.0 < out < 1.0:
        raise ValueError(f"floor must lie in (0, 1), got {value!r}")
    return out


def _check_power_of_two(value, name: str) -> int:
    size = _as_int(value, name, minimum=1)
    if size & (size - 1):
        raise ValueError(f"{name} must be a positive power of two, got {size}")
    return size


def _check_tag_fn(tag_fn):
    """The frozen run uses the accepted shared Toeplitz tag; tests may override."""
    if tag_fn is None:
        return toeplitz_tag
    if not callable(tag_fn):
        raise TypeError("tag_fn must be callable")
    return tag_fn


def _peak_rss_bytes() -> int | None:
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _budget_exceeded(start: float, cap: float) -> str | None:
    """Return the breached resource name, or ``None``.

    The frozen run uses the module-level ``TOTAL_WALL_S``/``RSS_LIMIT_BYTES``;
    the guard is a documented monkeypatch seam for focused tests only.
    """
    if time.perf_counter() - start > cap:
        return "wall_s"
    rss = _peak_rss_bytes()
    if rss is not None and rss > RSS_LIMIT_BYTES:
        return "rss_bytes"
    return None


def _canonical_sha(obj) -> str:
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def entropy_bits(probs, axis=-1) -> np.ndarray:
    """``-sum p log2 p`` in bits with the exact-zero convention ``0 log 0 = 0``."""
    arr = np.asarray(probs, dtype=np.float64)
    if not np.isfinite(arr).all() or (arr < 0).any():
        raise ValueError("entropy contract: probabilities must be finite and non-negative")
    safe = np.where(arr > 0.0, arr, 1.0)
    terms = np.where(arr > 0.0, -arr * np.log2(safe), 0.0)
    return terms.sum(axis=axis)


@dataclass(frozen=True, eq=False)
class TargetConditional:
    """Floored, column-normalized target conditional plus source marginals."""

    f: np.ndarray  # float64 [A,B] conditional table (floored, renormalized)
    p_b: np.ndarray  # float64[B] Bob marginal from the column totals
    raw: np.ndarray  # float64 [A,B] raw counts
    column_totals: np.ndarray  # float64[B]
    total_count: float
    floor: float
    column_dev: float  # max |sum_a f[a,b] - 1|


def build_target_conditional(counts, *, floor=FROZEN_FLOOR) -> TargetConditional:
    """Apply the only permitted support rule to a ``[Alice,Bob]`` count matrix."""
    floor = _check_floor(floor)
    arr = np.asarray(counts)
    if arr.dtype.kind == "b":
        raise TypeError("target population contract: counts must hold numbers, got boolean input")
    if arr.ndim != 2:
        raise ValueError(f"target population contract: counts must be 2-D, got shape {arr.shape}")
    if arr.shape[0] < 1 or arr.shape[1] < 1:
        raise ValueError(f"target population contract: counts must be non-empty, got {arr.shape}")
    try:
        mat = arr.astype(np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"target population contract: counts must be numeric ({exc})") from exc
    if not np.isfinite(mat).all():
        raise ValueError("target population contract: counts must be finite")
    if (mat < 0).any():
        raise ValueError("target population contract: counts must be non-negative")
    column_totals = mat.sum(axis=0)
    if (column_totals <= 0.0).any():
        zero = int(np.sum(column_totals <= 0.0))
        raise TargetPopulationContractError(
            f"zero Bob column(s) present: {zero} of {column_totals.shape[0]}"
        )
    total = float(column_totals.sum())
    if not np.isfinite(total) or total <= 0.0:
        raise ValueError("target population contract: counts total must be positive")
    p_b = column_totals / total
    f = mat / column_totals[None, :]
    f = np.maximum(f, floor)
    f = f / f.sum(axis=0, keepdims=True)
    return TargetConditional(
        f=f,
        p_b=p_b,
        raw=mat,
        column_totals=column_totals,
        total_count=total,
        floor=floor,
        column_dev=float(np.abs(f.sum(axis=0) - 1.0).max()),
    )


@dataclass(frozen=True, eq=False)
class EntropyReport:
    """Target entropies in bits: population (checked) plus floored guard.

    ``h1``/``h2``/``total`` are the in-sample population conditional entropies
    of the RAW MLE table (V26/V49 chain: ``H1 = E_B H(P1(:,b))`` and
    ``H2 = E_{B,U1} H(P2(u1,b,:))``), i.e. the functionals whose 1M TRAIN
    values are the frozen literals.  ``floor_*`` are the same functionals on
    the floored protocol table used for sampling; the pool floor only enters
    the gate through the ``floor_change`` guard.
    """

    h1: float  # population E_B[H(U1|B)]
    h2: float  # population E_{B,U1}[H(U2|U1,B)]
    total: float
    floor_h1: float  # same functionals on the floored protocol table
    floor_h2: float
    floor_total: float
    floor_change: float  # |floor_total - population total|
    f: np.ndarray  # floored conditional table (in memory only)
    p_b: np.ndarray  # [B] Bob marginal
    p1: np.ndarray  # [U1,B] accepted derived table of f (in memory only)
    p2: np.ndarray  # [U1,B,U2] accepted derived table of f (in memory only)


def target_entropies(counts, *, floor=FROZEN_FLOOR) -> EntropyReport:
    """Frozen entropy functionals on the raw MLE and floored tables.

    The checked ``h1``/``h2``/``total`` are the population in-sample
    conditional entropies (the accepted V26/V49 "H from channel_counts.npz"
    functional); the floored protocol table's entropies are reported only for
    the floor-change guard.  On a sparse count matrix the 1e-15 cell floor
    renormalizes each column by ``1 + (#zero cells)*1e-15`` and adds
    ``~1e-15``-mass slices, which shifts the floored entropy by ~1e-10; the
    frozen 1e-12 literal tolerance therefore applies to the population values.
    """
    table = build_target_conditional(counts, floor=floor)
    p1 = derive_p1(table.f)
    p2 = derive_p2(table.f)
    floor_h1 = float(np.sum(table.p_b * entropy_bits(p1, axis=0)))
    floor_h2 = float(np.sum(table.p_b[None, :] * p1 * entropy_bits(p2, axis=2)))
    floor_total = floor_h1 + floor_h2
    raw_f = table.raw / table.column_totals[None, :]
    raw_p1 = derive_p1(raw_f)
    raw_p2 = derive_p2(raw_f)
    h1 = float(np.sum(table.p_b * entropy_bits(raw_p1, axis=0)))
    h2 = float(np.sum(table.p_b[None, :] * raw_p1 * entropy_bits(raw_p2, axis=2)))
    total = h1 + h2
    return EntropyReport(
        h1=h1,
        h2=h2,
        total=total,
        floor_h1=floor_h1,
        floor_h2=floor_h2,
        floor_total=floor_total,
        floor_change=abs(floor_total - total),
        f=table.f,
        p_b=table.p_b,
        p1=p1,
        p2=p2,
    )


@dataclass(frozen=True, eq=False)
class PreconditionReport:
    """All frozen target-population preconditions and their observed values."""

    checks: dict
    failing: tuple
    passed: bool
    entropy: EntropyReport | None
    p_b: np.ndarray | None
    column_dev: float | None
    message: str


def target_preconditions(
    counts,
    *,
    floor=FROZEN_FLOOR,
    expected_h1=EXPECTED_H1,
    expected_h2=EXPECTED_H2,
    expected_total=EXPECTED_TOTAL,
    entropy_tol=ENTROPY_TOL,
    column_tol=COLUMN_TOL,
    floor_change_tol=FLOOR_ENTROPY_TOL,
) -> PreconditionReport:
    """Evaluate every frozen precondition without making any genie/SC call."""
    checks = {name: False for name in PRECONDITION_ORDER}
    try:
        table = build_target_conditional(counts, floor=floor)
    except TargetPopulationContractError as exc:
        return PreconditionReport(
            checks=checks,
            failing=tuple(PRECONDITION_ORDER),
            passed=False,
            entropy=None,
            p_b=None,
            column_dev=None,
            message=str(exc),
        )
    checks["no_zero_bob_column"] = True
    checks["p_b_normalized"] = bool(abs(float(table.p_b.sum()) - 1.0) <= column_tol)
    checks["conditional_columns_normalized"] = bool(table.column_dev <= column_tol)
    entropy = target_entropies(counts, floor=floor)
    checks["h1_matches_literal"] = bool(abs(entropy.h1 - float(expected_h1)) <= entropy_tol)
    checks["h2_matches_literal"] = bool(abs(entropy.h2 - float(expected_h2)) <= entropy_tol)
    checks["total_matches_literal"] = bool(
        abs(entropy.total - float(expected_total)) <= entropy_tol
    )
    checks["floor_entropy_change_at_most_1e-9"] = bool(entropy.floor_change <= floor_change_tol)
    failing = tuple(name for name in PRECONDITION_ORDER if not checks[name])
    return PreconditionReport(
        checks=checks,
        failing=failing,
        passed=not failing,
        entropy=entropy,
        p_b=table.p_b,
        column_dev=table.column_dev,
        message="",
    )


def sample_target_block(rng, *, p_b, f_full, n, q_high=Q, q_low=Q):
    """Sample one ``(bob, a_full, high, low)`` block via the accepted sampler.

    Frozen draw order: Bob labels first, then Alice labels per coordinate,
    exactly the accepted ``empirical_channel.sample_full_block`` semantics.
    """
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be an explicit numpy.random.Generator (no hidden global RNG)")
    return sample_full_block(rng, p_b, f_full, q_high, q_low, n)


def accumulate_genie(acc: dict, logp_x, u_true, *, field) -> None:
    """Accepted ``build_construction`` genie accumulation with explicit skips."""
    try:
        cond = genie_conditionals(logp_x, u_true, field=field, alpha=ALPHA)
    except ImpossibleDisclosedValueError:
        acc["impossible"] += 1
        return
    probs = np.exp(cond)
    rows = np.arange(cond.shape[0])
    acc["h"] += -cond[rows, u_true] / np.log(2.0)
    acc["e"] += 1.0 - probs.max(axis=1)
    acc["used"] += 1


def _empty_acc(n: int) -> dict:
    return {
        "h": np.zeros(n, dtype=np.float64),
        "e": np.zeros(n, dtype=np.float64),
        "used": 0,
        "impossible": 0,
    }


def pool_accumulators(accs) -> dict:
    """Pool per-stream sufficient statistics exactly as the P7 freeze."""
    return {
        "h": sum(item["h"] for item in accs),
        "e": sum(item["e"] for item in accs),
        "used": sum(int(item["used"]) for item in accs),
        "impossible": sum(int(item["impossible"]) for item in accs),
    }


def order_from_acc(acc: dict) -> np.ndarray:
    used = max(int(acc["used"]), 1)
    return disclosure_order_from_stats(acc["e"] / used, acc["h"] / used)


def position_rank(order) -> np.ndarray:
    order = np.asarray(order, dtype=np.int64)
    pos = np.empty(order.shape[0], dtype=np.int64)
    pos[order] = np.arange(order.shape[0], dtype=np.int64)
    return pos


def spearman_orders(order_a, order_b) -> float:
    return float(spearman_rank_corr(position_rank(order_a), position_rank(order_b)))


def bec_orders(h1: float, h2: float, *, n: int = FROZEN_N) -> tuple:
    """``(eps1, eps2, bec_l1_order, bec_l2_order)`` from ``epsilon_l = H_l/5``."""
    eps1 = min(1.0, max(0.0, float(h1) / float(np.log2(Q))))
    eps2 = min(1.0, max(0.0, float(h2) / float(np.log2(Q))))
    return eps1, eps2, analytic_order(eps1, n), analytic_order(eps2, n)


def arm_seed_bits(
    arm: str,
    block_index: int,
    *,
    master: int,
    bit_length: int = PUBLIC_CONTROL_BITS_PER_TAG,
) -> np.ndarray:
    """Deterministic public per-arm/per-block Toeplitz seed (P7 domain)."""
    if arm not in ARMS:
        raise SeedPrefixError(f"arm must be one of {ARMS}, got {arm!r}")
    index = _as_int(block_index, "block_index", minimum=0)
    master_seed = _as_int(master, "master", minimum=0)
    length = _as_int(bit_length, "bit_length", minimum=1)
    prefix = f"{SEED_PREFIX}:{master_seed}:{arm}:{index}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < length:
        buf.extend(hashlib.sha256(f"{prefix}:{counter}".encode("ascii")).digest())
        counter += 1
    bits = np.unpackbits(np.frombuffer(bytes(buf), dtype=np.uint8), bitorder="big")
    return bits[:length].astype(np.uint8)


def _nonfinite_flag(exc: Exception) -> bool:
    return (
        isinstance(exc, NumericNonfiniteError)
        or "nonfinite" in str(exc).lower()
        or "nan" in str(exc).lower()
    )


def _decode_layer(logp, *, field, positions, disclosed):
    """One fresh SC call plus the nonfinite-marginal fail-closed check."""
    result = sc_decode(
        logp,
        field=field,
        alpha=ALPHA,
        known_positions=positions,
        known_values=disclosed,
    )
    if bool(np.isnan(result.decision_metrics).any()) or bool(
        np.isposinf(result.decision_metrics).any()
    ):
        raise NumericNonfiniteError("numeric nonfinite failure: invalid decision marginals")
    return result


def classify_outcome(*, l1_failed: bool, l2_failed: bool, tag_pass: bool, label_match: bool) -> str:
    """Accepted two-layer outcome precedence (disjoint and exhaustive)."""
    if l1_failed or l2_failed:
        return "decode_failed"
    if not tag_pass:
        return "verify_failed"
    return "exact" if label_match else "undetected"


def classify_pair(empirical_exact: bool, bec_exact: bool) -> str:
    """Paired four-cell label; the four cells are disjoint and exhaustive."""
    if empirical_exact and bec_exact:
        return "both_exact"
    if empirical_exact:
        return "empirical_only"
    if bec_exact:
        return "bec_only"
    return "neither"


@dataclass(frozen=True, eq=False)
class DevArmResult:
    """One attempted DEV arm block.  Arrays are in-memory only, never persisted."""

    arm: str
    outcome: str
    exact: bool
    label_match: bool
    tag_pass: bool
    l1_provenance: str | None
    l2_provenance: str | None
    l1_executed: bool
    l1_decode_failed: bool
    l2_invoked: bool
    l2_skipped_by_l1_failure: bool
    l2_decode_failed: bool
    tag_invoked: bool
    key_dependent_bits: int
    public_control_bits: int
    nonfinite: bool
    truth_leak_violation: bool
    l1_error_type: str | None
    l2_error_type: str | None
    wall_s: float
    protected: tuple = ()
    truth_copies: tuple = ()
    high_hat: np.ndarray | None = None
    low_hat: np.ndarray | None = None
    label_hat: np.ndarray | None = None


def _abort_arm(arm: str) -> DevArmResult:
    return DevArmResult(
        arm=arm,
        outcome="resource_abort",
        exact=False,
        label_match=False,
        tag_pass=False,
        l1_provenance=None,
        l2_provenance=None,
        l1_executed=False,
        l1_decode_failed=False,
        l2_invoked=False,
        l2_skipped_by_l1_failure=False,
        l2_decode_failed=False,
        tag_invoked=False,
        key_dependent_bits=0,
        public_control_bits=0,
        nonfinite=False,
        truth_leak_violation=False,
        l1_error_type=None,
        l2_error_type=None,
        wall_s=0.0,
    )


def run_dev_arm(
    *,
    arm: str,
    block_index: int,
    bob,
    high_true,
    low_true,
    u1_true,
    u2_true,
    labels_true,
    labels_true_bits,
    field,
    p1_table,
    p2_table,
    l1_order,
    l2_order,
    k1: int = FROZEN_K1,
    k2: int = FROZEN_K2,
    n: int = FROZEN_N,
    master: int,
    tag_fn=None,
) -> DevArmResult:
    """One candidate-conditioned two-layer DEV arm on a single block.

    The operational path receives only Bob, the candidate and the frozen
    disclosures; truth is used only for the disclosed ``U`` values, the tag
    construction and scoring.
    """
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")
    block_index = _as_int(block_index, "block_index", minimum=0)
    k1 = _as_int(k1, "k1", minimum=0)
    k2 = _as_int(k2, "k2", minimum=0)
    n = _as_int(n, "n", minimum=1)
    if k1 > n or k2 > n:
        raise ValueError(f"k1/k2 must lie in 0..{n}, got k1={k1}, k2={k2}")
    tag_fn = _check_tag_fn(tag_fn)
    # Internal truth copies: every computation below uses these copies only, so
    # the block-level truth sentinel can mutate them and prove no aliasing.
    bob_arr = np.array(bob, dtype=np.int64, copy=True)
    high_arr = np.array(high_true, dtype=np.int64, copy=True)
    low_arr = np.array(low_true, dtype=np.int64, copy=True)
    u1_arr = np.array(u1_true, dtype=np.int64, copy=True)
    u2_arr = np.array(u2_true, dtype=np.int64, copy=True)
    labels_arr = np.array(labels_true, dtype=np.int64, copy=True)
    l1_positions = np.asarray(l1_order, dtype=np.int64)[:k1]
    l2_positions = np.asarray(l2_order, dtype=np.int64)[:k2]

    arm_start = time.perf_counter()
    op_p1_probs = build_p1_metrics(bob_arr[None, :], p1_table)[0]
    op_p1_metric = probs_to_symbol_metric(op_p1_probs, provenance=Provenance.PRIOR_ONLY)
    u1_disclosed = np.array(u1_arr[l1_positions], copy=True)
    l1_error = None
    l2_error = None
    l1_failed = False
    nonfinite = False
    high_hat = None
    low_hat = None
    label_hat = None
    label_hat_bits = None
    p2_metric = None
    tag_pass = False
    tag_invoked = False
    label_match = False

    try:
        sc1 = _decode_layer(
            op_p1_metric.logp, field=field, positions=l1_positions, disclosed=u1_disclosed
        )
        high_hat = np.array(sc1.x_hat, copy=True)
    except Exception as exc:  # SC failure contract: decode_failed, no tag
        l1_failed = True
        l1_error = type(exc).__name__
        nonfinite = _nonfinite_flag(exc)

    if high_hat is not None:
        # Candidate-conditioned L2: the metric is gathered from Bob and the hard
        # L1 candidate only; the true high layer never enters this metric.
        p2_probs = gather_p2_metrics(bob_arr[None, :], high_hat[None, :], p2_table)[0]
        p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
        u2_disclosed = np.array(u2_arr[l2_positions], copy=True)
        seed = arm_seed_bits(arm, block_index, master=master, bit_length=seed_bits_for(n))
        try:
            sc2 = _decode_layer(
                p2_metric.logp, field=field, positions=l2_positions, disclosed=u2_disclosed
            )
            low_hat = np.array(sc2.x_hat, copy=True)
            label_hat = (low_hat + LABEL_SCALE * high_hat).astype(np.int64)
            label_hat_bits = labels_to_bits(label_hat)
            label_match = bool(np.array_equal(label_hat, labels_arr))
            tag_true = tag_fn(labels_true_bits, seed, TAG_BITS)
            tag_hat = tag_fn(label_hat_bits, seed, TAG_BITS)
            tag_pass = tag_hat == tag_true
            tag_invoked = True
        except Exception as exc:  # SC failure contract: decode_failed, no tag
            l2_error = type(exc).__name__
            nonfinite = nonfinite or _nonfinite_flag(exc)
    else:
        u2_disclosed = np.empty(0, dtype=np.int64)

    outcome = classify_outcome(
        l1_failed=l1_failed,
        l2_failed=l2_error is not None,
        tag_pass=tag_pass,
        label_match=label_match,
    )
    l2_invoked = high_hat is not None
    l1_provenance = op_p1_metric.provenance.value if not l1_failed else None
    l2_provenance = p2_metric.provenance.value if p2_metric is not None else None
    key_dependent_bits = (
        DISCLOSED_BITS_PER_COORDINATE * k1
        + (DISCLOSED_BITS_PER_COORDINATE * k2 if l2_invoked else 0)
        + (TAG_BITS if tag_invoked else 0)
    )
    protected = [op_p1_metric.logp, u1_disclosed, u2_disclosed]
    if p2_metric is not None:
        protected.append(p2_metric.logp)
    for item in (high_hat, low_hat, label_hat, label_hat_bits):
        if item is not None:
            protected.append(item)
    return DevArmResult(
        arm=arm,
        outcome=outcome,
        exact=bool(outcome == "exact"),
        label_match=bool(label_match),
        tag_pass=bool(tag_pass),
        l1_provenance=l1_provenance,
        l2_provenance=l2_provenance,
        l1_executed=bool(not l1_failed),
        l1_decode_failed=bool(l1_failed),
        l2_invoked=bool(l2_invoked),
        l2_skipped_by_l1_failure=bool(l1_failed),
        l2_decode_failed=bool(l2_error is not None),
        tag_invoked=bool(tag_invoked),
        key_dependent_bits=int(key_dependent_bits),
        public_control_bits=int(seed_bits_for(n) if tag_invoked else 0),
        nonfinite=bool(nonfinite),
        truth_leak_violation=False,  # updated by the block sentinel
        l1_error_type=l1_error,
        l2_error_type=l2_error,
        wall_s=time.perf_counter() - arm_start,
        protected=tuple(protected),
        truth_copies=(high_arr, low_arr, u1_arr, u2_arr, labels_arr),
        high_hat=high_hat,
        low_hat=low_hat,
        label_hat=label_hat,
    )


def _truth_isolation_sentinel(protected, truth_arrays) -> bool:
    """Mutate every truth copy; True means the protected set stayed bitwise."""
    snapshots = [np.array(item, copy=True) for item in protected]
    for arr, modulus in truth_arrays:
        arr[...] = (arr + 1) % modulus
    for item, before in zip(protected, snapshots):
        if not np.array_equal(np.asarray(item), before):
            return False
    return True


@dataclass(frozen=True, eq=False)
class PairedBlockResult:
    """One paired DEV block: empirical arm plus BEC control arm."""

    block_index: int
    empirical: DevArmResult
    bec: DevArmResult
    cell: str
    truth_leak_violation: bool
    block_wall_s: float


def run_dev_block(
    block_index: int,
    bob,
    high_true,
    low_true,
    u1_true,
    u2_true,
    labels_true,
    labels_true_bits,
    *,
    field,
    p1_table,
    p2_table,
    l1_orders: dict,
    l2_orders: dict,
    k1: int = FROZEN_K1,
    k2: int = FROZEN_K2,
    n: int = FROZEN_N,
    master: int,
    tag_fn=None,
) -> PairedBlockResult:
    """Run the two paired arms on one block and apply the truth sentinel."""
    block_start = time.perf_counter()
    empirical = run_dev_arm(
        arm="empirical",
        block_index=block_index,
        bob=bob,
        high_true=high_true,
        low_true=low_true,
        u1_true=u1_true,
        u2_true=u2_true,
        labels_true=labels_true,
        labels_true_bits=labels_true_bits,
        field=field,
        p1_table=p1_table,
        p2_table=p2_table,
        l1_order=l1_orders["empirical"],
        l2_order=l2_orders["empirical"],
        k1=k1,
        k2=k2,
        n=n,
        master=master,
        tag_fn=tag_fn,
    )
    bec = run_dev_arm(
        arm="bec",
        block_index=block_index,
        bob=bob,
        high_true=high_true,
        low_true=low_true,
        u1_true=u1_true,
        u2_true=u2_true,
        labels_true=labels_true,
        labels_true_bits=labels_true_bits,
        field=field,
        p1_table=p1_table,
        p2_table=p2_table,
        l1_order=l1_orders["bec"],
        l2_order=l2_orders["bec"],
        k1=k1,
        k2=k2,
        n=n,
        master=master,
        tag_fn=tag_fn,
    )
    protected = list(empirical.protected) + list(bec.protected)
    protected.append(np.asarray(labels_true_bits, dtype=np.uint8))
    truth_arrays = []
    for result in (empirical, bec):
        truth_arrays.extend(zip(result.truth_copies, (Q, Q, Q, Q, 1 << 10)))
    isolated = _truth_isolation_sentinel(protected, truth_arrays)
    empirical = replace(empirical, truth_leak_violation=bool(not isolated))
    bec = replace(bec, truth_leak_violation=bool(not isolated))
    return PairedBlockResult(
        block_index=int(block_index),
        empirical=empirical,
        bec=bec,
        cell=classify_pair(empirical.exact, bec.exact),
        truth_leak_violation=bool(not isolated),
        block_wall_s=time.perf_counter() - block_start,
    )


def _arm_record(arm: DevArmResult) -> dict:
    """Compact scalar-only record; symbol/label arrays are never persisted."""
    return {
        "arm": arm.arm,
        "outcome": arm.outcome,
        "exact": bool(arm.exact),
        "label_match": bool(arm.label_match),
        "tag_pass": bool(arm.tag_pass),
        "l1_provenance": arm.l1_provenance,
        "l2_provenance": arm.l2_provenance,
        "l1_executed": bool(arm.l1_executed),
        "l1_decode_failed": bool(arm.l1_decode_failed),
        "l2_invoked": bool(arm.l2_invoked),
        "l2_skipped_by_l1_failure": bool(arm.l2_skipped_by_l1_failure),
        "l2_decode_failed": bool(arm.l2_decode_failed),
        "tag_invoked": bool(arm.tag_invoked),
        "key_dependent_bits": int(arm.key_dependent_bits),
        "public_control_bits": int(arm.public_control_bits),
        "nonfinite": bool(arm.nonfinite),
        "truth_leak_violation": bool(arm.truth_leak_violation),
        "l1_error_type": arm.l1_error_type,
        "l2_error_type": arm.l2_error_type,
        "wall_s": round(float(arm.wall_s), 6),
    }


def _block_record(stream_seed: int, result: PairedBlockResult) -> dict:
    return {
        "stream_seed": int(stream_seed),
        "block_index": int(result.block_index),
        "cell": result.cell,
        "empirical": _arm_record(result.empirical),
        "bec": _arm_record(result.bec),
    }


def _aborted_block_record(stream_seed: int, block_index: int) -> dict:
    return {
        "stream_seed": int(stream_seed),
        "block_index": int(block_index),
        "cell": classify_pair(False, False),
        "empirical": _arm_record(_abort_arm("empirical")),
        "bec": _arm_record(_abort_arm("bec")),
    }


def _aborted_pair(block_index: int) -> PairedBlockResult:
    return PairedBlockResult(
        block_index=int(block_index),
        empirical=_abort_arm("empirical"),
        bec=_abort_arm("bec"),
        cell=classify_pair(False, False),
        truth_leak_violation=False,
        block_wall_s=0.0,
    )


def _arm_record_consistent(arm: DevArmResult, *, k1: int, k2: int, n: int) -> bool:
    """Structural proof of one arm record under the frozen P7 rules."""
    if arm.outcome not in OUTCOMES or arm.arm not in ARMS:
        return False
    if arm.outcome == "resource_abort":
        return (
            int(arm.key_dependent_bits) == 0
            and int(arm.public_control_bits) == 0
            and not any(
                (
                    arm.exact,
                    arm.label_match,
                    arm.tag_pass,
                    arm.l1_executed,
                    arm.l1_decode_failed,
                    arm.l2_invoked,
                    arm.l2_skipped_by_l1_failure,
                    arm.l2_decode_failed,
                    arm.tag_invoked,
                    arm.nonfinite,
                    arm.truth_leak_violation,
                )
            )
        )
    if arm.l1_executed == arm.l1_decode_failed:
        return False
    if arm.l1_decode_failed and arm.l2_invoked:
        return False
    if not arm.l1_decode_failed and not arm.l2_invoked:
        return False  # every L1 candidate must invoke L2
    if arm.l2_skipped_by_l1_failure != arm.l1_decode_failed:
        return False
    if arm.l2_decode_failed and not arm.l2_invoked:
        return False
    tag_outcomes = ("exact", "undetected", "verify_failed")
    if arm.tag_invoked != (arm.outcome in tag_outcomes):
        return False
    if arm.outcome == "decode_failed" and not (arm.l1_decode_failed or arm.l2_decode_failed):
        return False
    if arm.outcome != "decode_failed" and (arm.l1_decode_failed or arm.l2_decode_failed):
        return False
    if arm.outcome == "exact" and not (arm.tag_pass and arm.label_match):
        return False
    if arm.outcome == "undetected" and not (arm.tag_pass and not arm.label_match):
        return False
    if arm.outcome == "verify_failed" and arm.tag_pass:
        return False
    expected_kdb = (
        DISCLOSED_BITS_PER_COORDINATE * k1
        + (DISCLOSED_BITS_PER_COORDINATE * k2 if arm.l2_invoked else 0)
        + (TAG_BITS if arm.tag_invoked else 0)
    )
    if int(arm.key_dependent_bits) != expected_kdb:
        return False
    if int(arm.public_control_bits) != (seed_bits_for(n) if arm.tag_invoked else 0):
        return False
    if arm.l1_executed and arm.l1_provenance != Provenance.PRIOR_ONLY.value:
        return False
    if arm.l2_invoked and arm.l2_provenance != Provenance.CANDIDATE_CONDITIONED.value:
        return False
    return True


def _event(
    *,
    stream_seed: int,
    block_index: int,
    event_id: str,
    event_type: str,
    direction: str,
    parent_event_id: str | None,
    key_dependent_bits: int,
    public_control_bits: int,
    payload: dict,
) -> dict:
    event = {
        "event_id": event_id,
        "frame_key": f"nbpolar-p7-target-construction:{int(stream_seed)}:{int(block_index)}",
        "method": "nbpolar_target_construction",
        "event_type": event_type,
        "direction": direction,
        "parent_event_id": parent_event_id,
        "pass_id": 0,
        "block_id": int(block_index),
        "key_dependent_bits": int(key_dependent_bits),
        "public_control_bits": int(public_control_bits),
        "payload": payload,
    }
    canonical_event(event)  # fail closed on malformed or secret-bearing payloads
    return event


def block_events(stream_seed: int, result: PairedBlockResult, *, k1: int, k2: int, n: int) -> list:
    """Canonical public transcript events: L1, L2 (when invoked), final tag."""
    events: list[dict] = []
    for arm_name, arm in (("empirical", result.empirical), ("bec", result.bec)):
        if arm.outcome == "resource_abort":
            continue
        l1_id = f"block-{int(result.block_index)}-{arm_name}-l1-disclosure"
        events.append(
            _event(
                stream_seed=stream_seed,
                block_index=result.block_index,
                event_id=l1_id,
                event_type="l1_disclosure",
                direction="alice_to_bob",
                parent_event_id=None,
                key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * int(k1),
                public_control_bits=0,
                payload={},
            )
        )
        if arm.l2_invoked:
            l2_id = f"block-{int(result.block_index)}-{arm_name}-l2-disclosure"
            events.append(
                _event(
                    stream_seed=stream_seed,
                    block_index=result.block_index,
                    event_id=l2_id,
                    event_type="l2_disclosure",
                    direction="alice_to_bob",
                    parent_event_id=l1_id,
                    key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * int(k2),
                    public_control_bits=0,
                    payload={},
                )
            )
            if arm.tag_invoked:
                events.append(
                    _event(
                        stream_seed=stream_seed,
                        block_index=result.block_index,
                        event_id=f"block-{int(result.block_index)}-{arm_name}-verification",
                        event_type="verification_tag",
                        direction="alice_to_bob",
                        parent_event_id=l2_id,
                        key_dependent_bits=TAG_BITS,
                        public_control_bits=seed_bits_for(n),
                        payload={"seed_bit_length": seed_bits_for(n)},
                    )
                )
    return events


def recount_events(events) -> dict:
    """Independent literal recount; the arm is read literally from the event id."""
    totals = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    by_arm = {arm: dict(totals) for arm in ARMS}
    event_types = {"l1_disclosure": 0, "l2_disclosure": 0, "verification_tag": 0}
    for event in events:
        parts = str(event["event_id"]).split("-")
        if len(parts) < 4 or parts[0] != "block" or parts[2] not in ARMS:
            raise ValueError(f"transcript event id is not arm-tagged: {event['event_id']!r}")
        arm = parts[2]
        key = int(event["key_dependent_bits"])
        public = int(event["public_control_bits"])
        totals["key_dependent_bits"] += key
        totals["public_control_bits"] += public
        by_arm[arm]["key_dependent_bits"] += key
        by_arm[arm]["public_control_bits"] += public
        event_type = str(event["event_type"])
        if event_type not in event_types:
            raise ValueError(f"transcript event type is not frozen: {event_type!r}")
        event_types[event_type] += 1
        if event_type == "verification_tag":
            totals["tag_invocations"] += 1
            by_arm[arm]["tag_invocations"] += 1
    return {
        "key_dependent_bits": totals["key_dependent_bits"],
        "public_control_bits": totals["public_control_bits"],
        "tag_invocations": totals["tag_invocations"],
        "event_types": dict(event_types),
        "by_arm": by_arm,
    }


def _transcript_mismatches(incremental, incremental_by_arm, recount) -> list:
    fields = ("key_dependent_bits", "public_control_bits", "tag_invocations")
    mismatches = []
    for name in fields:
        if int(incremental[name]) != int(recount[name]):
            mismatches.append(f"total:{name}:{int(incremental[name])}!={int(recount[name])}")
    for arm in ARMS:
        for name in fields:
            left = int(incremental_by_arm[arm][name])
            right = int(recount["by_arm"][arm][name])
            if left != right:
                mismatches.append(f"{arm}:{name}:{left}!={right}")
    return mismatches


def _order_provenance(
    *,
    layer: str,
    train_acc: dict,
    train_seeds,
    per_stream_orders: dict,
    pooled_acc: dict,
    pooled_order,
    bec_eps: float,
    bec_order,
    n: int,
) -> dict:
    per_stream_records = {
        str(int(seed)): {
            "order": [int(v) for v in per_stream_orders[int(seed)].tolist()],
            "n_used": int(train_acc[int(seed)][layer]["used"]),
            "n_impossible": int(train_acc[int(seed)][layer]["impossible"]),
            "e_sum": float(train_acc[int(seed)][layer]["e"].sum()),
            "h_sum": float(train_acc[int(seed)][layer]["h"].sum()),
        }
        for seed in train_seeds
    }
    pooled_h = sum(train_acc[int(seed)][layer]["h"] for seed in train_seeds)
    pooled_e = sum(train_acc[int(seed)][layer]["e"] for seed in train_seeds)
    provenance_consistent = bool(
        int(pooled_acc["used"])
        == sum(int(train_acc[int(seed)][layer]["used"]) for seed in train_seeds)
        and int(pooled_acc["impossible"])
        == sum(int(train_acc[int(seed)][layer]["impossible"]) for seed in train_seeds)
        and np.array_equal(pooled_acc["h"], pooled_h)
        and np.array_equal(pooled_acc["e"], pooled_e)
    )
    permutation = bool(
        np.array_equal(np.sort(np.asarray(pooled_order)), np.arange(n))
        and np.array_equal(np.sort(np.asarray(bec_order)), np.arange(n))
        and all(
            np.array_equal(np.sort(per_stream_orders[int(seed)]), np.arange(n))
            for seed in train_seeds
        )
    )
    return {
        "layer": layer,
        "per_stream": per_stream_records,
        "pooled": {
            "rule": "sum of the per-stream sufficient statistics over all TRAIN streams",
            "order": [int(v) for v in pooled_order.tolist()],
            "n_used": int(pooled_acc["used"]),
            "n_impossible": int(pooled_acc["impossible"]),
            "e_sum": float(pooled_acc["e"].sum()),
            "h_sum": float(pooled_acc["h"].sum()),
        },
        "bec": {
            "rule": BEC_RULE,
            "epsilon": float(bec_eps),
            "order": [int(v) for v in bec_order.tolist()],
            "report_only": True,
        },
        "permutation": permutation,
        "provenance_consistent": provenance_consistent,
    }


def _integrity_gates(
    *,
    precondition_report: PreconditionReport,
    counts_shape,
    train_seeds,
    train_blocks,
    train_blocks_attempted: int,
    dev_seeds,
    dev_blocks,
    results,
    records,
    layers: dict,
    orders_frozen: bool,
    orders_unchanged: bool,
    incremental,
    incremental_by_arm,
    recount,
    mismatches,
    accounting: dict,
    wall_s: float,
    rss_peak: int | None,
    resource_stop_fired: bool,
    k1: int,
    k2: int,
    n: int,
) -> dict:
    planned = int(len(list(dev_seeds)) * int(dev_blocks))
    op = [r.empirical for r in results]
    bec = [r.bec for r in results]
    executed = [r for r in results if r.empirical.outcome != "resource_abort"]
    executed_arms = len(executed) * len(ARMS)

    def count(arms, outcome):
        return sum(1 for arm in arms if arm.outcome == outcome)

    l1_ok = sum(1 for arm in op + bec if arm.l1_executed)
    l1_fail = sum(1 for arm in op + bec if arm.l1_decode_failed)
    l2_inv = sum(1 for arm in op + bec if arm.l2_invoked)
    l2_skip = sum(1 for arm in op + bec if arm.l2_skipped_by_l1_failure)
    l2_fail = sum(1 for arm in op + bec if arm.l2_decode_failed)
    tag_inv = sum(1 for arm in op + bec if arm.tag_invoked)
    tag_outcomes = sum(
        count(arms, name)
        for arms in (op, bec)
        for name in ("exact", "undetected", "verify_failed")
    )
    fully_invoked = [
        arm for arm in op + bec if arm.tag_invoked and arm.l2_invoked and arm.l1_executed
    ]
    fully_invoked_exact = all(
        int(arm.key_dependent_bits) == DISCLOSED_BITS_PER_COORDINATE * (k1 + k2) + TAG_BITS
        for arm in fully_invoked
    )
    per_record_ok = all(_arm_record_consistent(arm, k1=k1, k2=k2, n=n) for arm in op + bec)
    buckets_ok = all(
        sum(count(arms, name) for name in OUTCOMES) == len(results) for arms in (op, bec)
    )
    sub_buckets_ok = (
        l1_ok + l1_fail == executed_arms
        and l2_inv == l1_ok
        and l2_inv + l2_skip == executed_arms
        and l2_fail <= l2_inv
        and tag_inv == tag_outcomes
    )
    cells_ok = bool(sum(1 for r in records if r["cell"] in CELLS) == len(records))
    totals_ok = (
        int(incremental["key_dependent_bits"]) == int(recount["key_dependent_bits"])
        and int(incremental["public_control_bits"]) == int(recount["public_control_bits"])
        and int(incremental["tag_invocations"]) == int(recount["tag_invocations"])
        and all(
            int(incremental_by_arm[arm][name]) == int(recount["by_arm"][arm][name])
            for arm in ARMS
            for name in ("key_dependent_bits", "public_control_bits", "tag_invocations")
        )
    )
    tags_accounted = all(
        int(arm.public_control_bits) == (seed_bits_for(n) if arm.tag_invoked else 0)
        and int(arm.key_dependent_bits)
        == (
            DISCLOSED_BITS_PER_COORDINATE * k1
            + (DISCLOSED_BITS_PER_COORDINATE * k2 if arm.l2_invoked else 0)
            + (TAG_BITS if arm.tag_invoked else 0)
        )
        for arm in op + bec
        if arm.outcome != "resource_abort"
    )
    train_seed_set = {int(s) for s in train_seeds}
    dev_seed_set = {int(s) for s in dev_seeds}
    streams_ok = bool(
        {int(r["stream_seed"]) for r in records} == dev_seed_set
        and all(
            sum(1 for r in records if int(r["stream_seed"]) == seed) == int(dev_blocks)
            for seed in dev_seed_set
        )
    )
    coverage = bool(
        int(train_blocks_attempted) == len(train_seed_set) * int(train_blocks)
        and len(results) == planned
        and len(records) == planned
        and streams_ok
        and train_seed_set.isdisjoint(dev_seed_set)
    )
    mode = str(accounting.get("input_mode"))
    if mode == "v25_npz":
        read_exact = (
            int(accounting["artifact_content_reads_consumed_by_this_run"]) == 1
            and int(accounting["attempts_consumed_by_this_run"]) == 1
            and int(accounting["open_count"]) == 1
            and bool(accounting["stat_size_checked"])
            and int(accounting["observed_npz_bytes"]) == int(accounting["expected_npz_bytes"])
        )
    else:
        read_exact = (
            int(accounting["artifact_content_reads_consumed_by_this_run"]) == 0
            and int(accounting["attempts_consumed_by_this_run"]) == 0
            and int(accounting["open_count"]) == 0
        )
    accounting_exact = bool(
        read_exact
        and int(accounting["artifact_content_reads_consumed_before"]) == 0
        and int(accounting["attempts_consumed_before"]) == 0
        and int(accounting["retries"]) == 0
        and not bool(accounting["reopen_attempted"])
        and not bool(accounting["retry_after_open"])
        and tuple(counts_shape) == (1024, 1024)
    )
    gates = {
        "target_population_contract": bool(precondition_report.passed),
        "coverage_complete_and_disjoint": coverage,
        "orders_frozen_permutations_provenance": bool(
            orders_frozen
            and orders_unchanged
            and all(
                bool(layers[layer]["permutation"]) and bool(layers[layer]["provenance_consistent"])
                for layer in ("l1", "l2")
            )
        ),
        "pairing_and_buckets": bool(
            buckets_ok and sub_buckets_ok and per_record_ok and cells_ok and len(results) == planned
        ),
        "truth_leak_zero": not any(arm.truth_leak_violation for arm in op + bec),
        "undetected_zero": count(op, "undetected") == 0 and count(bec, "undetected") == 0,
        "nonfinite_zero": not any(arm.nonfinite for arm in op + bec),
        "resource_abort_zero": count(op, "resource_abort") == 0
        and count(bec, "resource_abort") == 0
        and not resource_stop_fired,
        "disclosure_and_recount_exact": bool(
            fully_invoked_exact
            and tags_accounted
            and totals_ok
            and not mismatches
            and recount["event_types"].get("l1_disclosure", 0) == executed_arms
            and recount["event_types"].get("l2_disclosure", 0) == l2_inv
            and recount["event_types"].get("verification_tag", 0) == tag_inv
        ),
        "attempt_read_accounting_exact": accounting_exact,
        "resource_limits_met": bool(
            float(wall_s) <= TOTAL_WALL_S
            and (rss_peak is None or int(rss_peak) <= RSS_LIMIT_BYTES)
        ),
    }
    return gates


@dataclass(frozen=True, eq=False)
class TargetConstructionRun:
    """In-memory P7 gate run (also returned by the runner)."""

    results: list
    records: list
    events: list
    orders: dict
    plan: dict
    summary: dict


def run_target_construction(
    *,
    counts=None,
    counts_path=FROZEN_COUNTS_PATH,
    source: str = FROZEN_SOURCE,
    n: int = FROZEN_N,
    floor=FROZEN_FLOOR,
    train_seeds=FROZEN_TRAIN_SEEDS,
    train_blocks: int = FROZEN_TRAIN_BLOCKS,
    dev_seeds=FROZEN_DEV_SEEDS,
    dev_blocks: int = FROZEN_DEV_BLOCKS,
    k1: int = FROZEN_K1,
    k2: int = FROZEN_K2,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_entropies=None,
    tag_fn=None,
) -> TargetConstructionRun:
    """Execute the frozen P7 gate and write exactly five compact files.

    ``counts``, ``expected_entropies`` and ``tag_fn`` are documented injected
    test seams; the frozen CLI passes only the frozen point and reads the V25
    NPZ through the accepted loader exactly once.
    """
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    n = _check_power_of_two(n, "n")
    if n != FROZEN_N:
        raise ValueError(f"frozen point requires n={FROZEN_N}, got {n}")
    floor = _check_floor(floor)
    if floor != FROZEN_FLOOR:
        raise ValueError(f"frozen point requires floor={FROZEN_FLOOR}, got {floor}")
    if source != FROZEN_SOURCE:
        raise ValueError(f"frozen point requires source={FROZEN_SOURCE!r}, got {source!r}")
    k1 = _as_int(k1, "k1", minimum=0)
    k2 = _as_int(k2, "k2", minimum=0)
    if (k1, k2) != (FROZEN_K1, FROZEN_K2):
        raise ValueError(f"frozen point requires k1={FROZEN_K1}, k2={FROZEN_K2}, got {k1}/{k2}")
    train_blocks = _as_int(train_blocks, "train_blocks", minimum=1)
    dev_blocks = _as_int(dev_blocks, "dev_blocks", minimum=1)
    train_seed_list = [_as_int(s, "train seed", minimum=0) for s in train_seeds]
    dev_seed_list = [_as_int(s, "dev seed", minimum=0) for s in dev_seeds]
    if not train_seed_list or not dev_seed_list:
        raise ValueError("at least one TRAIN and one DEV stream seed are required")
    if len(set(train_seed_list)) != len(train_seed_list):
        raise ValueError("TRAIN stream seeds must be distinct")
    if len(set(dev_seed_list)) != len(dev_seed_list):
        raise ValueError("DEV stream seeds must be distinct")
    if not set(train_seed_list).isdisjoint(dev_seed_list):
        raise ValueError("TRAIN and DEV stream seeds must be disjoint")
    cap = float(total_wall_s)
    if not np.isfinite(cap) or cap <= 0:
        raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")
    tag_fn = _check_tag_fn(tag_fn)

    # ---- input: stat-only check, then the single accepted content open.
    if counts is None:
        path = Path(counts_path)
        if not path.is_file():
            raise FileNotFoundError(f"V25 channel counts file not found: {path}")
        observed_bytes = int(path.stat().st_size)
        if observed_bytes != EXPECTED_NPZ_BYTES:
            raise ValueError(
                "V25 channel counts size mismatch before content open: "
                f"observed {observed_bytes} != expected {EXPECTED_NPZ_BYTES}"
            )
        loaded = load_v25_channel_counts(str(path))
        if source not in loaded:
            raise ValueError(f"source {source!r} missing from the loaded V25 counts")
        counts_arr = np.asarray(loaded[source])
        accounting = {
            "input_mode": "v25_npz",
            "counts_path": str(path),
            "expected_npz_bytes": int(EXPECTED_NPZ_BYTES),
            "observed_npz_bytes": int(observed_bytes),
            "stat_size_checked": True,
            "loader": LOADER_IDENTITY,
            "artifact_content_reads_allowed": 1,
            "artifact_content_reads_consumed_before": 0,
            "artifact_content_reads_consumed_by_this_run": 1,
            "open_count": 1,
            "attempts_allowed": 1,
            "attempts_consumed_before": 0,
            "attempts_consumed_by_this_run": 1,
            "retries": 0,
            "reopen_attempted": False,
            "retry_after_open": False,
            "consumption_point": ATTEMPT_CONSUMPTION_POINT,
        }
    else:
        counts_arr = np.asarray(counts)
        accounting = {
            "input_mode": "injected_counts",
            "counts_path": None,
            "expected_npz_bytes": None,
            "observed_npz_bytes": None,
            "stat_size_checked": False,
            "loader": None,
            "artifact_content_reads_allowed": 1,
            "artifact_content_reads_consumed_before": 0,
            "artifact_content_reads_consumed_by_this_run": 0,
            "open_count": 0,
            "attempts_allowed": 1,
            "attempts_consumed_before": 0,
            "attempts_consumed_by_this_run": 0,
            "retries": 0,
            "reopen_attempted": False,
            "retry_after_open": False,
            "consumption_point": ATTEMPT_CONSUMPTION_POINT,
        }
    if counts_arr.shape != (1024, 1024):
        raise ValueError(f"frozen target requires counts shape (1024,1024), got {counts_arr.shape}")

    # ---- frozen preconditions: no genie/SC call may happen before this passes.
    if expected_entropies is None:
        expected_h1, expected_h2, expected_total = EXPECTED_H1, EXPECTED_H2, EXPECTED_TOTAL
    else:
        expected_h1, expected_h2, expected_total = (float(v) for v in expected_entropies)
    precondition_report = target_preconditions(
        counts_arr,
        floor=floor,
        expected_h1=expected_h1,
        expected_h2=expected_h2,
        expected_total=expected_total,
    )
    if not precondition_report.passed:
        raise TargetPopulationContractError(
            "BLOCKED(target_population_contract): failing preconditions: "
            + ",".join(precondition_report.failing)
        )
    entropy = precondition_report.entropy
    p1 = entropy.p1
    p2 = entropy.p2
    field = make_gf32()
    start = time.perf_counter()

    # ---- TRAIN streams: genie sufficient statistics.
    train_acc: dict = {}
    train_blocks_attempted = 0
    for seed in train_seed_list:
        rng = np.random.default_rng(int(seed))
        acc = {"l1": _empty_acc(n), "l2": _empty_acc(n)}
        for _block_index in range(train_blocks):
            reason = _budget_exceeded(start, cap)
            if reason is not None:
                raise TargetConstructionResourceError(
                    f"resource limit {reason} exceeded during TRAIN before order freeze"
                )
            bob, _a_full, high, low = sample_target_block(
                rng, p_b=entropy.p_b, f_full=entropy.f, n=n
            )
            u1 = polar_transform(high, field=field, alpha=ALPHA)
            u2 = polar_transform(low, field=field, alpha=ALPHA)
            l1_metric = probs_to_symbol_metric(
                build_p1_metrics(bob[None, :], p1)[0], provenance=Provenance.PRIOR_ONLY
            )
            accumulate_genie(acc["l1"], l1_metric.logp, u1, field=field)
            l2_metric = probs_to_symbol_metric(
                gather_p2_metrics(bob[None, :], high[None, :], p2)[0],
                provenance=Provenance.ORACLE_CONDITIONED,
            )
            accumulate_genie(acc["l2"], l2_metric.logp, u2, field=field)
        train_acc[int(seed)] = acc
        train_blocks_attempted += train_blocks

    # ---- freeze every pooled/per-stream/BEC order before any DEV call.
    eps1, eps2, bec_l1_order, bec_l2_order = bec_orders(entropy.h1, entropy.h2, n=n)
    bec_by_layer = {"l1": (eps1, bec_l1_order), "l2": (eps2, bec_l2_order)}
    layers: dict = {}
    for layer in ("l1", "l2"):
        per_stream_orders = {
            int(seed): order_from_acc(train_acc[int(seed)][layer]) for seed in train_seed_list
        }
        pooled_acc = pool_accumulators([train_acc[int(seed)][layer] for seed in train_seed_list])
        pooled_order = order_from_acc(pooled_acc)
        eps, bec_order = bec_by_layer[layer]
        layers[layer] = _order_provenance(
            layer=layer,
            train_acc=train_acc,
            train_seeds=train_seed_list,
            per_stream_orders=per_stream_orders,
            pooled_acc=pooled_acc,
            pooled_order=pooled_order,
            bec_eps=eps,
            bec_order=bec_order,
            n=n,
        )
    orders_sha256 = _canonical_sha(layers)

    # ---- DEV: two paired arms per frozen block.
    l1_orders = {
        "empirical": np.asarray(layers["l1"]["pooled"]["order"], dtype=np.int64),
        "bec": np.asarray(layers["l1"]["bec"]["order"], dtype=np.int64),
    }
    l2_orders = {
        "empirical": np.asarray(layers["l2"]["pooled"]["order"], dtype=np.int64),
        "bec": np.asarray(layers["l2"]["bec"]["order"], dtype=np.int64),
    }
    plan_pairs = [(int(seed), block) for seed in dev_seed_list for block in range(dev_blocks)]
    results: list = []
    records: list = []
    events: list = []
    incremental = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    incremental_by_arm = {arm: dict(incremental) for arm in ARMS}
    resource_stop_fired = False
    current_seed = None
    rng = None
    for pair_index, (seed, block_index) in enumerate(plan_pairs):
        reason = _budget_exceeded(start, cap)
        if reason is not None:
            resource_stop_fired = True
            for seed2, block2 in plan_pairs[pair_index:]:
                results.append(_aborted_pair(block2))
                records.append(_aborted_block_record(seed2, block2))
            break
        if seed != current_seed:
            current_seed = seed
            rng = np.random.default_rng(seed)
        bob, _a_full, high, low = sample_target_block(
            rng, p_b=entropy.p_b, f_full=entropy.f, n=n
        )
        u1 = polar_transform(high, field=field, alpha=ALPHA)
        u2 = polar_transform(low, field=field, alpha=ALPHA)
        labels_true = (low + LABEL_SCALE * high).astype(np.int64)
        labels_true_bits = labels_to_bits(labels_true)
        result = run_dev_block(
            block_index,
            bob,
            high,
            low,
            u1,
            u2,
            labels_true,
            labels_true_bits,
            field=field,
            p1_table=p1,
            p2_table=p2,
            l1_orders=l1_orders,
            l2_orders=l2_orders,
            k1=k1,
            k2=k2,
            n=n,
            master=seed + PUBLIC_TAG_MASTER_OFFSET,
            tag_fn=tag_fn,
        )
        results.append(result)
        records.append(_block_record(seed, result))
        events.extend(block_events(seed, result, k1=k1, k2=k2, n=n))
        for arm in (result.empirical, result.bec):
            if arm.outcome == "resource_abort":
                continue
            incremental["key_dependent_bits"] += int(arm.key_dependent_bits)
            incremental["public_control_bits"] += int(arm.public_control_bits)
            incremental["tag_invocations"] += int(arm.tag_invoked)
            incremental_by_arm[arm.arm]["key_dependent_bits"] += int(arm.key_dependent_bits)
            incremental_by_arm[arm.arm]["public_control_bits"] += int(arm.public_control_bits)
            incremental_by_arm[arm.arm]["tag_invocations"] += int(arm.tag_invoked)
    wall_s = time.perf_counter() - start
    rss_peak = _peak_rss_bytes()
    orders_unchanged = _canonical_sha(layers) == orders_sha256

    recount = recount_events(events)
    mismatches = _transcript_mismatches(incremental, incremental_by_arm, recount)
    gates = _integrity_gates(
        precondition_report=precondition_report,
        counts_shape=counts_arr.shape,
        train_seeds=train_seed_list,
        train_blocks=train_blocks,
        train_blocks_attempted=train_blocks_attempted,
        dev_seeds=dev_seed_list,
        dev_blocks=dev_blocks,
        results=results,
        records=records,
        layers=layers,
        orders_frozen=True,
        orders_unchanged=orders_unchanged,
        incremental=incremental,
        incremental_by_arm=incremental_by_arm,
        recount=recount,
        mismatches=mismatches,
        accounting=accounting,
        wall_s=wall_s,
        rss_peak=rss_peak,
        resource_stop_fired=resource_stop_fired,
        k1=k1,
        k2=k2,
        n=n,
    )

    # ---- aggregates, scientific gates and the registered label.
    planned = len(plan_pairs)
    op_arms = [r.empirical for r in results]
    bec_arms = [r.bec for r in results]
    cells = {name: sum(1 for r in records if r["cell"] == name) for name in CELLS}

    def outcome_counts(arms):
        return {name: sum(1 for arm in arms if arm.outcome == name) for name in OUTCOMES}

    empirical_exact = sum(1 for arm in op_arms if arm.exact)
    bec_exact = sum(1 for arm in bec_arms if arm.exact)
    per_stream = {}
    for seed in dev_seed_list:
        recs = [r for r in records if int(r["stream_seed"]) == int(seed)]
        per_stream[str(int(seed))] = {
            "records": len(recs),
            "empirical": {
                "outcome_counts": {
                    name: sum(1 for r in recs if r["empirical"]["outcome"] == name)
                    for name in OUTCOMES
                }
            },
            "bec": {
                "outcome_counts": {
                    name: sum(1 for r in recs if r["bec"]["outcome"] == name)
                    for name in OUTCOMES
                }
            },
        }
    stability = {}
    for layer in ("l1", "l2"):
        order_map = {
            f"train_{int(seed)}": np.asarray(
                layers[layer]["per_stream"][str(int(seed))]["order"], dtype=np.int64
            )
            for seed in train_seed_list
        }
        order_map["pooled_empirical"] = np.asarray(layers[layer]["pooled"]["order"], dtype=np.int64)
        order_map["bec"] = np.asarray(layers[layer]["bec"]["order"], dtype=np.int64)
        empirical_names = [name for name in order_map if name != "bec"]
        pairwise = {}
        min_rho = 1.0
        for i, left in enumerate(empirical_names):
            for right in empirical_names[i + 1 :]:
                rho = spearman_orders(order_map[left], order_map[right])
                pairwise[f"{left}|{right}"] = rho
                min_rho = min(min_rho, rho)
        k_top = k1 if layer == "l1" else k2
        stability[layer] = {
            "order_names": empirical_names,
            "min_pairwise_spearman": float(min_rho),
            "pairwise_train_orders": pairwise,
            "bec_report_only": {
                f"{name}|bec": spearman_orders(order_map[name], order_map["bec"])
                for name in empirical_names
            },
            "topk_vs_bec_report_only": {
                "k": int(k_top),
                "overlap": {
                    f"{name}|bec": topk_overlap(order_map[name], order_map["bec"], k_top)
                    for name in empirical_names
                },
            },
        }
    min_spearman = min(
        stability["l1"]["min_pairwise_spearman"], stability["l2"]["min_pairwise_spearman"]
    )
    wilson_lb = wilson_lower_bound(empirical_exact, planned, z=WILSON_Z) if planned else 0.0
    scientific = {
        "train_spearman_min_at_least_0p95": bool(min_spearman >= SPEARMAN_MIN),
        "empirical_exact_at_least_620_of_640": bool(
            planned == FROZEN_PAIRS and empirical_exact >= EXACT_MIN
        ),
        "empirical_wilson_lower_bound_at_least_0p95": bool(
            planned == FROZEN_PAIRS and wilson_lb >= WILSON_MIN
        ),
    }
    scientific_all_pass = all(scientific.values())
    integrity_all_pass = all(gates.values())
    failing_integrity = [name for name in INTEGRITY_GATE_ORDER if not gates[name]]
    failing_scientific = [name for name in SCIENTIFIC_GATE_ORDER if not scientific[name]]
    shape_is_frozen_640 = bool(
        planned == FROZEN_PAIRS
        and train_seed_list == list(FROZEN_TRAIN_SEEDS)
        and train_blocks == FROZEN_TRAIN_BLOCKS
        and dev_seed_list == list(FROZEN_DEV_SEEDS)
        and dev_blocks == FROZEN_DEV_BLOCKS
    )
    if not integrity_all_pass:
        outcome_label = "BLOCKED"
    elif scientific_all_pass and shape_is_frozen_640:
        outcome_label = "TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE"
    else:
        outcome_label = "TARGET_EMPIRICAL_CONSTRUCTION_NOT_CONFIRMED"
    blocked_detail = f"BLOCKED({failing_integrity[0]})" if failing_integrity else None
    leakage_bits = DISCLOSED_BITS_PER_COORDINATE * (k1 + k2) + TAG_BITS
    leakage_no_tag = DISCLOSED_BITS_PER_COORDINATE * (k1 + k2)
    nH = float(n) * float(entropy.h1 + entropy.h2)
    fully_invoked_count = sum(
        1
        for arm in op_arms + bec_arms
        if arm.tag_invoked and arm.l2_invoked and arm.l1_executed
    )
    summary = {
        "analysis": PROTOCOL_NAME,
        "mode": MODE,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "source": source,
        "counts_path": accounting.get("counts_path"),
        "input_mode": accounting.get("input_mode"),
        "q": Q,
        "n": n,
        "k1": k1,
        "k2": k2,
        "floor": float(floor),
        "train_seeds": [int(s) for s in train_seed_list],
        "train_blocks": int(train_blocks),
        "dev_seeds": [int(s) for s in dev_seed_list],
        "dev_blocks": int(dev_blocks),
        "planned_pairs": int(planned),
        "toeplitz_masters": [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in dev_seed_list],
        "shape_is_frozen_640": shape_is_frozen_640,
        "entropy": {
            "h1": float(entropy.h1),
            "h2": float(entropy.h2),
            "total": float(entropy.total),
            "floor_h1": float(entropy.floor_h1),
            "floor_h2": float(entropy.floor_h2),
            "floor_total": float(entropy.floor_total),
            "floor_entropy_change": float(entropy.floor_change),
            "expected_h1": float(expected_h1),
            "expected_h2": float(expected_h2),
            "expected_total": float(expected_total),
            "population_functional": (
                "raw-MLE in-sample conditional entropies H1=E_B H(P1(:,b)), "
                "H2=E_{B,U1} H(P2(u1,b,:)) (accepted V26/V49 chain; the frozen "
                "literals are these values)"
            ),
            "floor_functional": (
                "same functionals on the floor-renormalized protocol table "
                "(reported only for the floor-change guard)"
            ),
            "tolerances": {
                "entropy": ENTROPY_TOL,
                "column": COLUMN_TOL,
                "floor_entropy_change": FLOOR_ENTROPY_TOL,
            },
            "checks": dict(precondition_report.checks),
            "column_dev": float(precondition_report.column_dev),
            "p_b_sum": float(np.sum(precondition_report.p_b)),
        },
        "bec_controls": {
            "rule": BEC_RULE,
            "epsilon_1": float(layers["l1"]["bec"]["epsilon"]),
            "epsilon_2": float(layers["l2"]["bec"]["epsilon"]),
            "report_only": True,
        },
        "cells": cells,
        "marginals": {
            "empirical_exact": int(empirical_exact),
            "bec_exact": int(bec_exact),
            "empirical_exact_rate": round(empirical_exact / max(planned, 1), 9),
            "bec_exact_rate": round(bec_exact / max(planned, 1), 9),
            "paired_exact_gap": int(empirical_exact - bec_exact),
            "empirical_outcomes": outcome_counts(op_arms),
            "bec_outcomes": outcome_counts(bec_arms),
            "fully_invoked_arms": int(fully_invoked_count),
        },
        "per_stream": per_stream,
        "construction_stability": stability,
        "scientific": {name: bool(scientific[name]) for name in SCIENTIFIC_GATE_ORDER},
        "scientific_all_pass": scientific_all_pass,
        "failing_scientific_gates": failing_scientific,
        "wilson_lower_bound": float(wilson_lb),
        "wilson_z": float(WILSON_Z),
        "integrity": {name: bool(gates[name]) for name in INTEGRITY_GATE_ORDER},
        "integrity_all_pass": integrity_all_pass,
        "failing_integrity_gates": failing_integrity,
        "blocked_detail": blocked_detail,
        "outcome_label": outcome_label,
        "disclosure_accounting": {
            "disclosed_bits_per_coordinate": DISCLOSED_BITS_PER_COORDINATE,
            "l1_bits_per_arm": int(L1_DISCLOSURE_BITS),
            "l2_bits_per_arm": int(L2_DISCLOSURE_BITS),
            "tag_bits": TAG_BITS,
            "fully_invoked_arm_bits": int(FULLY_INVOKED_ARM_BITS),
            "public_control_bits_per_tag": int(PUBLIC_CONTROL_BITS_PER_TAG),
            "key_dependent_bits_total": int(incremental["key_dependent_bits"]),
            "public_control_bits_total": int(incremental["public_control_bits"]),
            "tag_invocations": int(incremental["tag_invocations"]),
            "recount": {
                "key_dependent_bits": int(recount["key_dependent_bits"]),
                "public_control_bits": int(recount["public_control_bits"]),
                "tag_invocations": int(recount["tag_invocations"]),
                "event_types": dict(recount["event_types"]),
                "by_arm": {arm: dict(recount["by_arm"][arm]) for arm in ARMS},
            },
            "incremental_by_arm": {arm: dict(incremental_by_arm[arm]) for arm in ARMS},
            "mismatch_count": int(len(mismatches)),
            "mismatches": list(mismatches),
        },
        "planning_f": {
            "planning_only": True,
            "leakage_bits": int(leakage_bits),
            "leakage_bits_no_tag": int(leakage_no_tag),
            "nH_bits": float(nH),
            "f": float(leakage_bits / nH),
            "f_no_tag": float(leakage_no_tag / nH),
            "note": (
                "planning-only fixed-design ratio; no gate depends on f; not "
                "real-channel efficiency"
            ),
        },
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_peak": rss_peak,
        "resource_stop_fired": bool(resource_stop_fired),
        "attempt_read_accounting": dict(accounting),
        "orders_sha256": orders_sha256,
        "orders_unchanged_after_dev": bool(orders_unchanged),
        "claim_scope": CLAIM_SCOPE,
    }
    plan = {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "created_utc": summary["created_utc"],
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "out_root": str(out_path),
        "source": source,
        "counts_path": accounting.get("counts_path"),
        "expected_npz_bytes": EXPECTED_NPZ_BYTES,
        "loader": LOADER_IDENTITY,
        "support_rule": SUPPORT_RULE,
        "q": Q,
        "n": int(n),
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "floor": float(floor),
        "train_seeds": [int(s) for s in train_seed_list],
        "train_blocks": int(train_blocks),
        "dev_seeds": [int(s) for s in dev_seed_list],
        "dev_blocks": int(dev_blocks),
        "planned_pairs": int(planned),
        "toeplitz_masters": [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in dev_seed_list],
        "sampling_rule": SAMPLING_RULE,
        "truth_boundary": TRUTH_BOUNDARY,
        "bec_control_rule": BEC_RULE,
        "arms": list(ARMS),
        "k1": int(k1),
        "k2": int(k2),
        "outcome_buckets": list(OUTCOMES),
        "outcome_precedence": list(OUTCOME_PRECEDENCE),
        "disclosure_accounting": {
            "l1_disclosure_bits": int(L1_DISCLOSURE_BITS),
            "l2_disclosure_bits": int(L2_DISCLOSURE_BITS),
            "tag_bits": TAG_BITS,
            "fully_invoked_arm_bits": int(FULLY_INVOKED_ARM_BITS),
            "public_control_bits_per_tag": int(PUBLIC_CONTROL_BITS_PER_TAG),
            "recount_rule": (
                "independent literal transcript recount equals the incremental totals"
            ),
        },
        "toeplitz": {
            "tag_bits": TAG_BITS,
            "public_seed_bits": int(PUBLIC_CONTROL_BITS_PER_TAG),
            "derivation": (
                f"MSB-first unpack of SHA-256('{SEED_PREFIX}:<master>:<arm>:<block>"
                ":<counter>') concatenated over counter=0,1,...; truncated to "
                "10*n+63 bits; public control, never persisted raw"
            ),
            "arm_labels": list(ARMS),
        },
        "entropy_expectations": {
            "h1": EXPECTED_H1,
            "h2": EXPECTED_H2,
            "total": EXPECTED_TOTAL,
            "entropy_tol": ENTROPY_TOL,
            "column_tol": COLUMN_TOL,
            "floor_entropy_change_tol": FLOOR_ENTROPY_TOL,
            "provenance": (
                "docs/v49_distribution_tables/v49_train_val_hold_nll.csv row "
                "1M/TRAIN (nll_u1/nll_u2/nll_total); V27R review recomputes H "
                "from channel_counts.npz and matches the frozen docs"
            ),
        },
        "precondition_order": list(PRECONDITION_ORDER),
        "integrity_gate_order": list(INTEGRITY_GATE_ORDER),
        "scientific_gates": {
            "train_spearman_min_at_least_0p95": SPEARMAN_MIN,
            "empirical_exact_at_least_620_of_640": EXACT_MIN,
            "empirical_wilson_lower_bound_at_least_0p95": WILSON_MIN,
            "wilson_z": float(WILSON_Z),
        },
        "labels": {
            "candidate": "TARGET_EMPIRICAL_CONSTRUCTION_CANDIDATE",
            "not_confirmed": "TARGET_EMPIRICAL_CONSTRUCTION_NOT_CONFIRMED",
            "blocked": "BLOCKED(<earliest gate>)",
        },
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
        "artifact_read_accounting": dict(ARTIFACT_READ_ACCOUNTING),
        "budget": {
            "total_wall_s": float(TOTAL_WALL_S),
            "external_timeout_s": EXTERNAL_TIMEOUT_S,
            "ulimit_virtual_kib": ULIMIT_VIRTUAL_KIB,
            "rss_bytes_max": RSS_LIMIT_BYTES,
        },
        "output_files": list(OUTPUT_FILES),
        "frozen_command": FROZEN_COMMAND,
        "claim_scope": CLAIM_SCOPE,
    }
    construction_orders = {
        "protocol": PROTOCOL_NAME,
        "source": source,
        "n": int(n),
        "train_seeds": [int(s) for s in train_seed_list],
        "train_blocks": int(train_blocks),
        "orders_sha256": orders_sha256,
        "frozen_before_dev": True,
        "orders_unchanged_after_dev": bool(orders_unchanged),
        "layers": layers,
    }
    out_path.mkdir(parents=True)
    _write_json(out_path / "frozen_plan.json", plan)
    _write_json(out_path / "construction_orders.json", construction_orders)
    _write_json(
        out_path / "per_block_paired_outcomes.json",
        {
            "planned_pairs": int(planned),
            "train_seeds": [int(s) for s in train_seed_list],
            "dev_seeds": [int(s) for s in dev_seed_list],
            "n_blocks": len(records),
            "blocks": records,
        },
    )
    _write_json(out_path / "aggregate_summary.json", summary)
    (out_path / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return TargetConstructionRun(
        results=results,
        records=records,
        events=events,
        orders=construction_orders,
        plan=plan,
        summary=summary,
    )


def _render_report(summary: dict) -> str:
    cells = summary["cells"]
    marginals = summary["marginals"]
    integrity = summary["integrity"]
    scientific = summary["scientific"]
    accounting = summary["disclosure_accounting"]
    entropy = summary["entropy"]
    stability = summary["construction_stability"]
    lines = [
        "# NB-Polar Phase 4-P7 target-population empirical construction gate",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- source/target: `{summary['source']}`; q={summary['q']}, N={summary['n']}, "
        f"K1={summary['k1']}, K2={summary['k2']}, floor={summary['floor']}",
        f"- TRAIN: {summary['train_seeds']} x {summary['train_blocks']} blocks; "
        f"DEV: {summary['dev_seeds']} x {summary['dev_blocks']} "
        f"= {summary['planned_pairs']} paired blocks",
        f"- wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes; "
        f"resource stop fired: {summary['resource_stop_fired']}",
        "",
        "## Target population contract",
        "",
        f"- H1: {entropy['h1']!r} (expected {entropy['expected_h1']!r})",
        f"- H2: {entropy['h2']!r} (expected {entropy['expected_h2']!r})",
        f"- total: {entropy['total']!r} (expected {entropy['expected_total']!r})",
        f"- floored-table total: {entropy['floor_total']!r}; floor-induced change: "
        f"{entropy['floor_entropy_change']!r}",
        f"- column deviation: {entropy['column_dev']!r}; p_b sum: {entropy['p_b_sum']!r}",
        f"- BEC control epsilons: {summary['bec_controls']['epsilon_1']!r} / "
        f"{summary['bec_controls']['epsilon_2']!r} (report-only)",
        "",
        "## Construction stability (minimum pairwise TRAIN-order Spearman)",
        "",
        f"- L1: {stability['l1']['min_pairwise_spearman']!r}; "
        f"L2: {stability['l2']['min_pairwise_spearman']!r}",
        "",
        "## Paired DEV results",
        "",
        "| cell | count |",
        "|---|---|",
        f"| both_exact | {cells['both_exact']} |",
        f"| empirical_only | {cells['empirical_only']} |",
        f"| bec_only | {cells['bec_only']} |",
        f"| neither | {cells['neither']} |",
        "",
        f"- empirical exact: {marginals['empirical_exact']}/{summary['planned_pairs']}; "
        f"BEC exact: {marginals['bec_exact']}/{summary['planned_pairs']}; "
        f"one-sided 95% Wilson lower bound: {summary['wilson_lower_bound']!r}",
        "",
        "## Integrity gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in integrity.items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        "## Scientific gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in scientific.items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        "## Disclosure accounting",
        "",
        f"- fully invoked arm: {accounting['fully_invoked_arm_bits']} key-dependent bits "
        f"(L1 {accounting['l1_bits_per_arm']} + L2 {accounting['l2_bits_per_arm']} + "
        f"tag {accounting['tag_bits']}); public control "
        f"{accounting['public_control_bits_per_tag']} bits per tag",
        f"- key-dependent total: {accounting['key_dependent_bits_total']}; public total: "
        f"{accounting['public_control_bits_total']}; tags: {accounting['tag_invocations']}",
        f"- recount mismatch count: {accounting['mismatch_count']}",
        "",
        "## Planning-only f",
        "",
        f"- leakage {summary['planning_f']['leakage_bits']} bits / nH "
        f"{summary['planning_f']['nH_bits']!r} = f {summary['planning_f']['f']!r} "
        f"(planning-only; not real-channel efficiency)",
        "",
        f"- outcome label: `{summary['outcome_label']}`",
        "",
        f"**Scope:** {summary['claim_scope']}.",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p7-target-construction",
        description=(
            "NB-Polar Phase 4-P7 target-population empirical construction "
            "development gate (frozen V25 1M TRAIN counts)"
        ),
    )
    parser.add_argument("--counts", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--floor", required=True, type=float)
    parser.add_argument("--train-seeds", required=True, type=int, nargs="+", dest="train_seeds")
    parser.add_argument("--train-blocks", required=True, type=int, dest="train_blocks")
    parser.add_argument("--dev-seeds", required=True, type=int, nargs="+", dest="dev_seeds")
    parser.add_argument("--dev-blocks", required=True, type=int, dest="dev_blocks")
    parser.add_argument("--k1", required=True, type=int)
    parser.add_argument("--k2", required=True, type=int)
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_target_construction(
            counts_path=args.counts,
            source=args.source,
            n=args.n,
            floor=args.floor,
            train_seeds=args.train_seeds,
            train_blocks=args.train_blocks,
            dev_seeds=args.dev_seeds,
            dev_blocks=args.dev_blocks,
            k1=args.k1,
            k2=args.k2,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p7 target construction refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "planned_pairs": summary["planned_pairs"],
                "cells": summary["cells"],
                "empirical_exact": summary["marginals"]["empirical_exact"],
                "wilson_lower_bound": summary["wilson_lower_bound"],
                "integrity_all_pass": summary["integrity_all_pass"],
                "scientific_all_pass": summary["scientific_all_pass"],
                "outcome_label": summary["outcome_label"],
                "out_root": args.out_dir,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
