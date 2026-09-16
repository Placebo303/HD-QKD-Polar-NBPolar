"""NB-Polar Phase 4-P8 target rate SCREEN -> CONFIRM gate.

Frozen point (packet ``NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM``,
OpenSpec ``formal-ir-nbpolar-phase4-p0`` P8 delta): select the
lowest-disclosure static two-layer point that clears a frozen SCREEN
reliability rule over the exact ``7x5`` empirical-order grid, then test
that single selected point once on disjoint CONFIRM streams with a paired
BEC-order control.  This calibrates the finite-length target-population
rate point before any adaptive-rate, N-scaling, FWHT or SCL work.

Phase 4-P9 delta (packet
``NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION``, OpenSpec P9 delta):
reuses this module through the smallest explicit delta only -- a required
closed-choice ``--gate-id`` selecting the P9 protocol name, tag-domain
prefix and result labels, plus the frozen P9 ``8x7`` grid and output root.
All SC/prior/construction/tag/outcome/support/truth/accounting semantics
are unchanged; the P8 path is preserved byte-for-byte when the P8 gate id
is used.

Frozen semantics:

- Input: the accepted P7 pooled empirical L1/L2 orders from the immutable
  P7 ``construction_orders.json``; both must be valid 256-permutations and
  the recomputed canonical digest must equal the recorded P7 order identity
  ``8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104``,
  with the BEC orders equal to the accepted H1/H2-surrogate analytic
  orders -- all BEFORE opening the channel artifact.  Any mismatch is a
  fail-closed refusal consuming no read and no attempt.
- Channel: one call to the accepted ``load_v25_channel_counts(path)``; a
  stat-only size check of exactly ``25,166,822`` bytes happens before the
  content open, and the single artifact read plus the single scientific
  attempt are consumed at the first NPZ content open (never reopened,
  never retried).
- Support rule (the only one, exactly P7): column-normalize the raw
  counts, replace every cell below ``1e-15`` by ``1e-15``, renormalize each
  Bob column; ``p_b`` from the column totals; accepted ``derive_p1`` /
  ``derive_p2`` under the packing ``A = 32*U1 + U2``.  No lambda, backoff,
  tuning, floor scan or held-out fitting.
- Preconditions before any SC call: no zero Bob column; ``p_b`` and
  conditional column error ``<= 1e-12``; raw-MLE in-sample population
  ``H1``/``H2``/total within ``1e-12`` of the V49 1M TRAIN literals (the
  ratified P7 semantics); floor-induced total-entropy change relative to
  the raw MLE table ``<= 1e-9``.  Failure is
  ``BLOCKED(target_population_contract)`` and creates no output root.
- SCREEN: GF32 (primitive polynomial 37, alpha 2, natural order),
  ``N=256``; streams ``2026091680..2026091682`` x 64 common blocks (192);
  the exact grid ``K1=[8,10,12,16,24,32,45]`` x
  ``K2=[80,94,110,125,140]`` (35 configurations).  Each shared block is
  sampled once (``B ~ p_b`` then ``A ~ P_floor(A|B)``) and every grid point
  uses the identical block object.  Each configuration runs L1 then
  candidate-conditioned L2 from scratch, rebuilds the 10-bit label and
  invokes one phase/arm/block-domain-separated 64-bit Toeplitz tag
  (public master ``stream + 10000``).
- Eligibility per point: all 192 blocks accounted, undetected / nonfinite /
  resource_abort zero, one-sided 95% Wilson exact-recovery lower bound
  ``>= 0.95`` (at this frozen shape exactly ``exact >= 188/192``; both the
  bound and the count check are recorded).  Selection is the lexicographic
  minimum of ``(K1+K2, K1, K2)`` over eligible points only.  No eligible
  point stops without CONFIRM as ``TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT``.
- CONFIRM: streams ``2026091690..2026091694`` x 128 common blocks (640),
  asserted disjoint from SCREEN; only the selected empirical-order point
  plus a paired BEC-order control at the same selected K1/K2.  The point
  confirms iff empirical exact ``>= 618/640``, Wilson lower bound
  ``>= 0.95``, and undetected / nonfinite / resource_abort are zero.
- Accounting: a fully invoked point discloses exactly ``5*(K1+K2)+64``
  key-dependent bits and ``2623`` public control bits per invoked tag,
  with an independent literal transcript recount.

The only output is the explicit CLI and its five compact scalar-only
files; symbols, labels, disclosed values, decoded keys and raw seed bits
are never persisted.  No Model-F/held-out/raw/real frame, no ``N>256``, no
APP/SCL/FWHT, no production benchmark, no commit.  The claim scope is a
static development signal for the frozen V25 TRAIN empirical distribution
at ``N=256`` only -- not held-out or real frame FER, efficiency, key rate,
scaling, qualification or promotion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from numbers import Integral, Real
from pathlib import Path

import numpy as np

from ..shared import canonical_event, toeplitz_tag
from ..v35_algorithm_development import load_v25_channel_counts
from .algebra import make_gf32
from .construction import analytic_order
from .prior import (
    Provenance,
    build_p1_metrics,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from .protocol import WILSON_Z, wilson_lower_bound
from .sc import NumericNonfiniteError, sc_decode
from .target_construction import (
    PRECONDITION_ORDER,
    TargetPopulationContractError,
    classify_outcome,
    classify_pair,
    sample_target_block,
    target_preconditions,
)
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

PROTOCOL_NAME = "nbpolar-p8-target-rate-screen-confirm"
MODE = "static-target-rate-screen-confirm"

# P9 delta-only identifiers (packet NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION).
# The P8 constants above are untouched; the P8 path uses them byte-for-byte.
P8_GATE_ID = "p8-target-rate-screen-confirm"
P9_GATE_ID = "p9-lower-rate-boundary"
GATE_IDS = (P8_GATE_ID, P9_GATE_ID)
P9_PROTOCOL_NAME = "nbpolar-p9-lower-rate-boundary-screen-confirm"
P9_MODE = "static-lower-rate-boundary-screen-confirm"
P9_SEED_PREFIX = "nbpolar-p9-lower-rate-boundary-seed"
P8_FRAME_PREFIX = "nbpolar-p8-target-rate"
P9_FRAME_PREFIX = "nbpolar-p9-lower-rate-boundary"
P9_FROZEN_K1_GRID = (0, 2, 4, 6, 8, 12, 24, 45)
P9_FROZEN_K2_GRID = (0, 20, 40, 50, 60, 70, 80)
P9_FROZEN_NCONFIGS = 56
P9_FROZEN_SCREEN_SEEDS = (2026091710, 2026091711, 2026091712)
P9_FROZEN_CONFIRM_SEEDS = (
    2026091720,
    2026091721,
    2026091722,
    2026091723,
    2026091724,
)
P9_FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P9-LOWER-RATE-BOUNDARY-RESOLUTION/"
    "lower_rate_screen_confirm"
)
P9_CANDIDATE_LABEL = "TARGET_EMPIRICAL_LOWER_RATE_POINT_CANDIDATE"
P9_NO_ELIGIBLE_LABEL = "TARGET_LOWER_RATE_SCREEN_NO_ELIGIBLE_POINT"
P9_NOT_CONFIRMED_LABEL = "TARGET_EMPIRICAL_LOWER_RATE_POINT_NOT_CONFIRMED"
P8_CANDIDATE_LABEL = "TARGET_EMPIRICAL_RATE_POINT_CANDIDATE"
P8_NO_ELIGIBLE_LABEL = "TARGET_RATE_SCREEN_NO_ELIGIBLE_POINT"
P8_NOT_CONFIRMED_LABEL = "TARGET_EMPIRICAL_RATE_POINT_NOT_CONFIRMED"
# All prior official streams the P9 gate must stay disjoint from (P7 TRAIN
# 1650..52 + DEV 1660..64, P8 SCREEN 1680..82 + CONFIRM 1690..94).
P9_PRIOR_OFFICIAL_STREAMS = frozenset(
    (
        2026091650,
        2026091651,
        2026091652,
        2026091660,
        2026091661,
        2026091662,
        2026091663,
        2026091664,
        2026091680,
        2026091681,
        2026091682,
        2026091690,
        2026091691,
        2026091692,
        2026091693,
        2026091694,
    )
)

Q = 32
ALPHA = 2
FROZEN_N = 256
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_SCREEN_SEEDS = (2026091680, 2026091681, 2026091682)
FROZEN_SCREEN_BLOCKS = 64
FROZEN_SCREEN_TOTAL = 192
FROZEN_K1_GRID = (8, 10, 12, 16, 24, 32, 45)
FROZEN_K2_GRID = (80, 94, 110, 125, 140)
FROZEN_NCONFIGS = 35
FROZEN_CONFIRM_SEEDS = (2026091690, 2026091691, 2026091692, 2026091693, 2026091694)
FROZEN_CONFIRM_BLOCKS = 128
FROZEN_CONFIRM_TOTAL = 640
PUBLIC_TAG_MASTER_OFFSET = 10000

EXPECTED_NPZ_BYTES = 25166822
FROZEN_COUNTS_PATH = (
    "/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/"
    "nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz"
)
FROZEN_ORDERS_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P7-TARGET-EMPIRICAL-CONSTRUCTION/"
    "target_construction_gate/construction_orders.json"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P8-TARGET-RATE-SCREEN-CONFIRM/"
    "rate_screen_confirm"
)
LOADER_IDENTITY = (
    "comparison_bench.src.comparison_bench.formal_ir."
    "v35_algorithm_development.load_v25_channel_counts"
)
EXPECTED_ORDERS_SHA = "8ec690344897655418b71520b22e9e403dfa381ca193fe0d322cb13e1d714104"

EXPECTED_H1 = 0.02428054681872374
EXPECTED_H2 = 0.7767572780789994
EXPECTED_TOTAL = 0.8010378248977232
ENTROPY_TOL = 1e-12
COLUMN_TOL = 1e-12
FLOOR_ENTROPY_TOL = 1e-9

SCREEN_EXACT_MIN = 188
CONFIRM_EXACT_MIN = 618
WILSON_MIN = 0.95

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 3600.0
EXTERNAL_TIMEOUT_S = 3600
ULIMIT_VIRTUAL_KIB = 2097152

PHASES = ("screen", "confirm")
ARMS = ("empirical", "bec")
CELLS = ("both_exact", "empirical_only", "bec_only", "neither")
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
    "no lambda, backoff, tuning, floor scan or held-out fitting "
    "(exact P7 rule)"
)
SAMPLING_RULE = (
    "per shared block: B ~ p_b (rng.random(n) against the cumulative p_b), "
    "then A ~ P_floor(A|B) per coordinate (rng.random(n) against the "
    "cumulative column); high=A//32, low=A%32; explicit "
    "np.random.default_rng(stream seed), one stream RNG, no global RNG; "
    "every grid point uses the identical block object"
)
TRUTH_BOUNDARY = (
    "Alice truth enters only sampling, disclosed values, tag construction and "
    "scoring; it never enters an undisclosed operational metric, decision or "
    "candidate label; each arm restarts SC per layer with no state transfer; "
    "each arm copies its truth inputs and the per-arm sentinel proves the "
    "protected metrics/decisions stayed bitwise under truth mutation"
)
BEC_RULE = (
    "accepted P7 H1/H2-surrogate orders from construction_orders.json "
    "(analytic_order(epsilon_l, 256) with epsilon_l = H_l/5); report-only control"
)
SCREEN_RULE = (
    "eligible iff 192/192 blocks accounted, undetected/nonfinite/"
    "resource_abort zero, one-sided 95% Wilson exact-recovery lower bound "
    ">= 0.95 (at this shape exact >= 188/192); selection is the "
    "lexicographic minimum of (K1+K2, K1, K2) over eligible points only"
)

OUTCOME_PRECEDENCE = [
    "resource_abort: block not executed (preregistered budget stop)",
    "decode_failed: L1 or L2 SC exception / nonfinite marginals; no tag",
    "verify_failed: tag mismatch",
    "exact: tag pass and label == true label",
    "undetected: tag pass and not exact (never success)",
]

INTEGRITY_GATE_ORDER = (
    "orders_identity_and_permutations",
    "target_population_contract",
    "coverage_complete_and_disjoint",
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
    "confirm_empirical_exact_at_least_618_of_640",
    "confirm_empirical_wilson_lower_bound_at_least_0p95",
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "screen_records.json",
    "selection_and_confirmation_records.json",
    "transcript_accounting.json",
    "report.md",
)

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "ulimit -v 2097152\n"
    "timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_rate "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --orders {FROZEN_ORDERS_PATH} "
    "--n 256 --floor 1e-15 "
    "--screen-seeds 2026091680 2026091681 2026091682 --screen-blocks 64 "
    "--k1-grid 8 10 12 16 24 32 45 --k2-grid 80 94 110 125 140 "
    "--confirm-seeds 2026091690 2026091691 2026091692 2026091693 2026091694 "
    "--confirm-blocks 128 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)
CLAIM_SCOPE = (
    "frozen V25 TRAIN target-population static rate development signal at "
    "N=256 only; not held-out or real frame FER, efficiency, key rate, "
    "scaling, qualification or promotion; planning-only f is not "
    "real-channel efficiency; undetected is never success"
)
SEED_PREFIX = "nbpolar-p8-target-rate-seed"

P9_FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "ulimit -v 2097152\n"
    "timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_rate "
    "--gate-id p9-lower-rate-boundary "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --orders {FROZEN_ORDERS_PATH} "
    "--n 256 --floor 1e-15 "
    "--screen-seeds 2026091710 2026091711 2026091712 --screen-blocks 64 "
    "--k1-grid 0 2 4 6 8 12 24 45 --k2-grid 0 20 40 50 60 70 80 "
    "--confirm-seeds 2026091720 2026091721 2026091722 2026091723 2026091724 "
    "--confirm-blocks 128 "
    f"--out-dir {P9_FROZEN_OUT_ROOT}"
)


def _normalize_gate_id(gate_id) -> str:
    """Closed-choice gate resolution (P9 delta-only).

    ``None`` maps to the P8 gate for backward compatibility of the
    injected Python seams (all accepted P8 tests call without a gate id);
    the CLI never passes ``None`` because ``main`` refuses a missing
    ``--gate-id`` before any artifact access.  Any other unknown value
    raises ``ValueError``.
    """
    if gate_id is None:
        return P8_GATE_ID
    if gate_id not in GATE_IDS:
        raise ValueError(f"gate-id must be one of {list(GATE_IDS)}, got {gate_id!r}")
    return gate_id


def _gate_protocol(gate_id: str) -> str:
    return P9_PROTOCOL_NAME if gate_id == P9_GATE_ID else PROTOCOL_NAME


def _gate_mode(gate_id: str) -> str:
    return P9_MODE if gate_id == P9_GATE_ID else MODE


def _gate_seed_prefix(gate_id: str) -> str:
    return P9_SEED_PREFIX if gate_id == P9_GATE_ID else SEED_PREFIX


def _gate_frame_prefix(gate_id: str) -> str:
    return P9_FRAME_PREFIX if gate_id == P9_GATE_ID else P8_FRAME_PREFIX


def _gate_labels(gate_id: str) -> dict:
    if gate_id == P9_GATE_ID:
        return {
            "candidate": P9_CANDIDATE_LABEL,
            "not_confirmed": P9_NOT_CONFIRMED_LABEL,
            "no_eligible_point": P9_NO_ELIGIBLE_LABEL,
            "blocked": "BLOCKED(<earliest gate>)",
        }
    return {
        "candidate": P8_CANDIDATE_LABEL,
        "not_confirmed": P8_NOT_CONFIRMED_LABEL,
        "no_eligible_point": P8_NO_ELIGIBLE_LABEL,
        "blocked": "BLOCKED(<earliest gate>)",
    }


def _gate_grids(gate_id: str):
    if gate_id == P9_GATE_ID:
        return (P9_FROZEN_K1_GRID, P9_FROZEN_K2_GRID, P9_FROZEN_NCONFIGS)
    return (FROZEN_K1_GRID, FROZEN_K2_GRID, FROZEN_NCONFIGS)


def _gate_frozen_seeds(gate_id: str):
    if gate_id == P9_GATE_ID:
        return (P9_FROZEN_SCREEN_SEEDS, P9_FROZEN_CONFIRM_SEEDS)
    return (FROZEN_SCREEN_SEEDS, FROZEN_CONFIRM_SEEDS)


def _gate_frozen_command(gate_id: str) -> str:
    return P9_FROZEN_COMMAND if gate_id == P9_GATE_ID else FROZEN_COMMAND

__all__ = [
    "PROTOCOL_NAME",
    "MODE",
    "P8_GATE_ID",
    "P9_GATE_ID",
    "GATE_IDS",
    "P9_PROTOCOL_NAME",
    "P9_MODE",
    "P9_SEED_PREFIX",
    "P8_FRAME_PREFIX",
    "P9_FRAME_PREFIX",
    "P9_FROZEN_K1_GRID",
    "P9_FROZEN_K2_GRID",
    "P9_FROZEN_NCONFIGS",
    "P9_FROZEN_SCREEN_SEEDS",
    "P9_FROZEN_CONFIRM_SEEDS",
    "P9_FROZEN_OUT_ROOT",
    "P9_FROZEN_COMMAND",
    "P9_CANDIDATE_LABEL",
    "P9_NO_ELIGIBLE_LABEL",
    "P9_NOT_CONFIRMED_LABEL",
    "P8_CANDIDATE_LABEL",
    "P8_NO_ELIGIBLE_LABEL",
    "P8_NOT_CONFIRMED_LABEL",
    "P9_PRIOR_OFFICIAL_STREAMS",
    "Q",
    "ALPHA",
    "FROZEN_N",
    "FROZEN_SOURCE",
    "FROZEN_FLOOR",
    "FROZEN_SCREEN_SEEDS",
    "FROZEN_SCREEN_BLOCKS",
    "FROZEN_SCREEN_TOTAL",
    "FROZEN_K1_GRID",
    "FROZEN_K2_GRID",
    "FROZEN_NCONFIGS",
    "FROZEN_CONFIRM_SEEDS",
    "FROZEN_CONFIRM_BLOCKS",
    "FROZEN_CONFIRM_TOTAL",
    "PUBLIC_TAG_MASTER_OFFSET",
    "EXPECTED_NPZ_BYTES",
    "FROZEN_COUNTS_PATH",
    "FROZEN_ORDERS_PATH",
    "FROZEN_OUT_ROOT",
    "LOADER_IDENTITY",
    "EXPECTED_ORDERS_SHA",
    "EXPECTED_H1",
    "EXPECTED_H2",
    "EXPECTED_TOTAL",
    "ENTROPY_TOL",
    "COLUMN_TOL",
    "FLOOR_ENTROPY_TOL",
    "SCREEN_EXACT_MIN",
    "CONFIRM_EXACT_MIN",
    "WILSON_MIN",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S",
    "ULIMIT_VIRTUAL_KIB",
    "PHASES",
    "ARMS",
    "CELLS",
    "PUBLIC_CONTROL_BITS_PER_TAG",
    "ATTEMPT_CONSUMPTION_POINT",
    "ARTIFACT_READ_ACCOUNTING",
    "SUPPORT_RULE",
    "SAMPLING_RULE",
    "TRUTH_BOUNDARY",
    "BEC_RULE",
    "SCREEN_RULE",
    "OUTCOME_PRECEDENCE",
    "INTEGRITY_GATE_ORDER",
    "SCIENTIFIC_GATE_ORDER",
    "OUTPUT_FILES",
    "FROZEN_COMMAND",
    "CLAIM_SCOPE",
    "SeedPrefixError",
    "OrdersIdentityError",
    "TargetRateResourceError",
    "SharedBlock",
    "RateArmResult",
    "ConfirmBlockResult",
    "TargetRateRun",
    "screen_grid",
    "is_valid_permutation",
    "validate_orders_doc",
    "load_construction_orders",
    "screen_eligibility",
    "select_point",
    "sample_shared_blocks",
    "arm_seed_bits",
    "classify_outcome",
    "classify_pair",
    "run_rate_arm",
    "run_confirm_pair",
    "block_events",
    "recount_events",
    "run_target_rate",
    "build_parser",
    "main",
]


class SeedPrefixError(ValueError):
    """Internal misuse of an invalid phase/arm seed request (frozen prefix)."""


class OrdersIdentityError(ValueError):
    """The P7 orders file failed identity/permutation/surrogate checks (fail closed)."""


class TargetRateResourceError(RuntimeError):
    """The wall/RSS budget was exceeded before the run could complete."""


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


def screen_grid(
    k1_grid=FROZEN_K1_GRID, k2_grid=FROZEN_K2_GRID
) -> list:
    """The frozen static grid: ``[(k1, k2), ...]`` in K1-major order (35 points)."""
    return [(int(k1), int(k2)) for k1 in k1_grid for k2 in k2_grid]


def is_valid_permutation(order, *, n: int = FROZEN_N) -> bool:
    """True iff ``order`` is a permutation of ``0..n-1``."""
    try:
        arr = np.asarray(order, dtype=np.int64)
    except (TypeError, ValueError):
        return False
    return bool(arr.shape == (n,) and np.array_equal(np.sort(arr), np.arange(n)))


def validate_orders_doc(doc, *, expected_sha: str = EXPECTED_ORDERS_SHA) -> dict:
    """Validate a decoded P7 orders document (no file or NPZ access).

    Requires the recorded digest to equal ``expected_sha`` (the frozen P7
    order identity in production), the recomputed canonical digest of the
    ``layers`` payload to equal the recorded digest, both pooled empirical
    orders to be 256-permutations, and both BEC orders to equal the
    recomputed H1/H2-surrogate analytic orders.  Any failure raises
    :class:`OrdersIdentityError` and consumes nothing.  ``expected_sha`` is
    a documented test seam; production callers use the frozen default.
    """
    if not isinstance(doc, dict):
        raise OrdersIdentityError("P7 orders document is not a JSON object")
    recorded = doc.get("orders_sha256")
    if recorded != expected_sha:
        raise OrdersIdentityError(
            "P7 order identity mismatch before content open: "
            f"recorded {recorded!r} != expected {expected_sha!r}"
        )
    layers = doc.get("layers")
    if not isinstance(layers, dict) or set(layers) != {"l1", "l2"}:
        raise OrdersIdentityError("P7 orders file lacks the frozen l1/l2 layers payload")
    if _canonical_sha(layers) != recorded:
        raise OrdersIdentityError(
            "P7 orders payload digest mismatch before content open: "
            "recomputed canonical digest != recorded orders_sha256"
        )
    orders = {}
    for layer in ("l1", "l2"):
        rec = layers.get(layer)
        if not isinstance(rec, dict):
            raise OrdersIdentityError(f"P7 orders layer {layer!r} is not a record")
        pooled = (rec.get("pooled") or {}).get("order")
        if not is_valid_permutation(pooled, n=FROZEN_N):
            raise OrdersIdentityError(
                f"P7 pooled empirical {layer} order is not a valid 256-permutation"
            )
        bec = rec.get("bec") or {}
        eps = bec.get("epsilon")
        bec_order = bec.get("order")
        if not isinstance(eps, Real) or isinstance(eps, bool):
            raise OrdersIdentityError(f"P7 BEC {layer} epsilon is not a number")
        if not np.array_equal(
            np.asarray(bec_order, dtype=np.int64), analytic_order(float(eps), FROZEN_N)
        ):
            raise OrdersIdentityError(
                f"P7 BEC {layer} order is not the accepted H-surrogate analytic order"
            )
        if not is_valid_permutation(bec_order, n=FROZEN_N):
            raise OrdersIdentityError(f"P7 BEC {layer} order is not a valid 256-permutation")
        orders[f"{layer}_empirical"] = np.asarray(pooled, dtype=np.int64)
        orders[f"{layer}_bec"] = np.asarray(bec_order, dtype=np.int64)
        orders[f"eps_{layer}"] = float(eps)
    orders["sha256"] = recorded
    return orders


def load_construction_orders(path) -> dict:
    """Load and validate the accepted P7 orders file (no NPZ access).

    The frozen P7 order identity is enforced; any mismatch raises
    :class:`OrdersIdentityError` before any channel artifact is opened.
    """
    path = Path(path)
    if not path.is_file():
        raise OrdersIdentityError(f"P7 orders file not found: {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise OrdersIdentityError(f"P7 orders file is not readable JSON: {exc}") from exc
    return validate_orders_doc(doc)


def screen_eligibility(exact: int, total: int) -> dict:
    """Eligibility of one SCREEN point plus the independently verified count rule.

    Eligible iff the one-sided 95% Wilson exact-recovery lower bound is
    ``>= 0.95``.  At the frozen ``192``-block shape this holds exactly for
    ``exact >= 188``; both the bound and the count check are recorded with
    their agreement flag (verified by the focused tests over the full
    ``0..192`` range).
    """
    exact = _as_int(exact, "exact", minimum=0)
    total = _as_int(total, "total", minimum=0)
    if exact > total:
        raise ValueError(f"exact {exact} must not exceed total {total}")
    wilson_lb = wilson_lower_bound(exact, total, z=WILSON_Z) if total else 0.0
    count_rule = bool(total == FROZEN_SCREEN_TOTAL and exact >= SCREEN_EXACT_MIN)
    eligible = bool(wilson_lb >= WILSON_MIN)
    return {
        "exact": int(exact),
        "total": int(total),
        "wilson_lower_bound": float(wilson_lb),
        "wilson_z": float(WILSON_Z),
        "count_rule_188_of_192": count_rule,
        "wilson_count_agree": bool(eligible == count_rule) if total == FROZEN_SCREEN_TOTAL else None,
        "eligible": eligible,
    }


def select_point(configs) -> dict | None:
    """Exactly one eligible point: lexicographic minimum of ``(K1+K2, K1, K2)``.

    ``configs`` are per-configuration records carrying ``k1``, ``k2`` and
    ``eligible``.  Only eligible points compete; no outcome or runtime
    enters the tiebreak.  Returns the winning record, or ``None`` when no
    point is eligible.
    """
    eligible = [c for c in configs if bool(c.get("eligible"))]
    if not eligible:
        return None
    return min(eligible, key=lambda c: (int(c["k1"]) + int(c["k2"]), int(c["k1"]), int(c["k2"])))


@dataclass(frozen=True, eq=False)
class SharedBlock:
    """One sampled shared block; the identical object feeds every grid point."""

    stream_seed: int
    block_index: int
    bob: np.ndarray
    high: np.ndarray
    low: np.ndarray
    u1: np.ndarray
    u2: np.ndarray
    labels: np.ndarray
    label_bits: np.ndarray


def sample_shared_blocks(
    stream_seed: int,
    n_blocks: int,
    *,
    p_b,
    f_full,
    n: int,
    field,
) -> list:
    """Sample ``n_blocks`` shared blocks on one explicit stream RNG (no SC)."""
    stream_seed = _as_int(stream_seed, "stream_seed", minimum=0)
    n_blocks = _as_int(n_blocks, "n_blocks", minimum=1)
    rng = np.random.default_rng(stream_seed)
    blocks = []
    for block_index in range(n_blocks):
        bob, _a_full, high, low = sample_target_block(rng, p_b=p_b, f_full=f_full, n=n)
        u1 = polar_transform(high, field=field, alpha=ALPHA)
        u2 = polar_transform(low, field=field, alpha=ALPHA)
        labels = (low + LABEL_SCALE * high).astype(np.int64)
        blocks.append(
            SharedBlock(
                stream_seed=stream_seed,
                block_index=int(block_index),
                bob=bob,
                high=high,
                low=low,
                u1=u1,
                u2=u2,
                labels=labels,
                label_bits=labels_to_bits(labels),
            )
        )
    return blocks


def arm_seed_bits(
    phase: str,
    arm: str,
    block_index: int,
    *,
    master: int,
    bit_length: int = PUBLIC_CONTROL_BITS_PER_TAG,
    gate_id=None,
) -> np.ndarray:
    """Deterministic public per-phase/per-arm/per-block Toeplitz seed.

    P8 default domain when ``gate_id`` is omitted (byte-for-byte P8
    behavior); the P9 gate uses its own domain-separated prefix.
    """
    if phase not in PHASES:
        raise SeedPrefixError(f"phase must be one of {PHASES}, got {phase!r}")
    if arm not in ARMS:
        raise SeedPrefixError(f"arm must be one of {ARMS}, got {arm!r}")
    gate = _normalize_gate_id(gate_id)
    index = _as_int(block_index, "block_index", minimum=0)
    master_seed = _as_int(master, "master", minimum=0)
    length = _as_int(bit_length, "bit_length", minimum=1)
    prefix = f"{_gate_seed_prefix(gate)}:{master_seed}:{phase}:{arm}:{index}"
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
class RateArmResult:
    """One attempted rate arm block.  Arrays are in-memory only, never persisted."""

    phase: str
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
    k1: int
    k2: int
    high_hat: np.ndarray | None = None
    low_hat: np.ndarray | None = None
    label_hat: np.ndarray | None = None


def _abort_arm(phase: str, arm: str, *, k1: int, k2: int) -> RateArmResult:
    return RateArmResult(
        phase=phase,
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
        k1=int(k1),
        k2=int(k2),
    )


def run_rate_arm(
    *,
    phase: str,
    arm: str,
    block: SharedBlock,
    field,
    p1_table,
    p2_table,
    l1_order,
    l2_order,
    k1: int,
    k2: int,
    n: int = FROZEN_N,
    master: int,
    tag_fn=None,
    gate_id=None,
) -> RateArmResult:
    """One candidate-conditioned two-layer rate arm on a shared block.

    The operational path receives only Bob, the candidate and the frozen
    disclosures; truth is used only for the disclosed ``U`` values, the tag
    construction and scoring.  The per-arm truth sentinel mutates internal
    truth copies after the metrics and decisions exist.
    """
    if phase not in PHASES:
        raise ValueError(f"phase must be one of {PHASES}, got {phase!r}")
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")
    gate = _normalize_gate_id(gate_id)
    k1 = _as_int(k1, "k1", minimum=0)
    k2 = _as_int(k2, "k2", minimum=0)
    n = _as_int(n, "n", minimum=1)
    if k1 > n or k2 > n:
        raise ValueError(f"k1/k2 must lie in 0..{n}, got k1={k1}, k2={k2}")
    tag_fn = _check_tag_fn(tag_fn)
    # Internal truth copies: every computation below uses these copies only, so
    # the per-arm truth sentinel can mutate them and prove no aliasing.
    bob_arr = np.array(block.bob, dtype=np.int64, copy=True)
    high_arr = np.array(block.high, dtype=np.int64, copy=True)
    low_arr = np.array(block.low, dtype=np.int64, copy=True)
    u1_arr = np.array(block.u1, dtype=np.int64, copy=True)
    u2_arr = np.array(block.u2, dtype=np.int64, copy=True)
    labels_arr = np.array(block.labels, dtype=np.int64, copy=True)
    label_bits_arr = np.array(block.label_bits, dtype=np.uint8, copy=True)
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
        seed = arm_seed_bits(phase, arm, block.block_index, master=master, gate_id=gate)
        try:
            sc2 = _decode_layer(
                p2_metric.logp, field=field, positions=l2_positions, disclosed=u2_disclosed
            )
            low_hat = np.array(sc2.x_hat, copy=True)
            label_hat = (low_hat + LABEL_SCALE * high_hat).astype(np.int64)
            label_hat_bits = labels_to_bits(label_hat)
            label_match = bool(np.array_equal(label_hat, labels_arr))
            tag_true = tag_fn(label_bits_arr, seed, TAG_BITS)
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
    protected = [op_p1_metric.logp, u1_disclosed, u2_disclosed]
    if p2_metric is not None:
        protected.append(p2_metric.logp)
    for item in (high_hat, low_hat, label_hat, label_hat_bits):
        if item is not None:
            protected.append(item)
    isolated = _truth_isolation_sentinel(
        protected,
        [
            (high_arr, Q),
            (low_arr, Q),
            (u1_arr, Q),
            (u2_arr, Q),
            (labels_arr, 1 << 10),
        ],
    )
    return RateArmResult(
        phase=phase,
        arm=arm,
        outcome=outcome,
        exact=bool(outcome == "exact"),
        label_match=bool(label_match),
        tag_pass=bool(tag_pass),
        l1_provenance=op_p1_metric.provenance.value if not l1_failed else None,
        l2_provenance=p2_metric.provenance.value if p2_metric is not None else None,
        l1_executed=bool(not l1_failed),
        l1_decode_failed=bool(l1_failed),
        l2_invoked=bool(l2_invoked),
        l2_skipped_by_l1_failure=bool(l1_failed),
        l2_decode_failed=bool(l2_error is not None),
        tag_invoked=bool(tag_invoked),
        key_dependent_bits=int(
            DISCLOSED_BITS_PER_COORDINATE * k1
            + (DISCLOSED_BITS_PER_COORDINATE * k2 if l2_invoked else 0)
            + (TAG_BITS if tag_invoked else 0)
        ),
        public_control_bits=int(seed_bits_for(n) if tag_invoked else 0),
        nonfinite=bool(nonfinite),
        truth_leak_violation=bool(not isolated),
        l1_error_type=l1_error,
        l2_error_type=l2_error,
        wall_s=time.perf_counter() - arm_start,
        k1=int(k1),
        k2=int(k2),
        high_hat=high_hat,
        low_hat=low_hat,
        label_hat=label_hat,
    )


@dataclass(frozen=True, eq=False)
class ConfirmBlockResult:
    """One paired CONFIRM block: empirical arm plus BEC control arm."""

    stream_seed: int
    block_index: int
    empirical: RateArmResult
    bec: RateArmResult
    cell: str
    block_wall_s: float


def run_confirm_pair(
    block: SharedBlock,
    *,
    field,
    p1_table,
    p2_table,
    l1_orders: dict,
    l2_orders: dict,
    k1: int,
    k2: int,
    n: int = FROZEN_N,
    master: int,
    tag_fn=None,
    gate_id=None,
) -> ConfirmBlockResult:
    """Run the paired CONFIRM arms (empirical + BEC) at the same selected K."""
    block_start = time.perf_counter()
    tag_fn = _check_tag_fn(tag_fn)
    gate = _normalize_gate_id(gate_id)
    empirical = run_rate_arm(
        phase="confirm",
        arm="empirical",
        block=block,
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
        gate_id=gate,
    )
    bec = run_rate_arm(
        phase="confirm",
        arm="bec",
        block=block,
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
        gate_id=gate,
    )
    return ConfirmBlockResult(
        stream_seed=int(block.stream_seed),
        block_index=int(block.block_index),
        empirical=empirical,
        bec=bec,
        cell=classify_pair(empirical.exact, bec.exact),
        block_wall_s=time.perf_counter() - block_start,
    )


def _arm_record(arm: RateArmResult) -> dict:
    """Compact scalar-only record; symbol/label arrays are never persisted."""
    return {
        "phase": arm.phase,
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
        "k1": int(arm.k1),
        "k2": int(arm.k2),
        "wall_s": round(float(arm.wall_s), 6),
    }


def _aborted_arm_record(phase: str, arm: str, *, k1: int, k2: int) -> dict:
    return _arm_record(_abort_arm(phase, arm, k1=k1, k2=k2))


def _arm_record_consistent(arm: RateArmResult, *, n: int) -> bool:
    """Structural proof of one arm record under the frozen P8 rules."""
    if arm.phase not in PHASES or arm.arm not in ARMS or arm.outcome not in OUTCOMES:
        return False
    k1, k2 = int(arm.k1), int(arm.k2)
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
    phase: str,
    stream_seed: int,
    block_index: int,
    event_id: str,
    event_type: str,
    direction: str,
    parent_event_id: str | None,
    key_dependent_bits: int,
    public_control_bits: int,
    payload: dict,
    gate_id=None,
) -> dict:
    gate = _normalize_gate_id(gate_id)
    event = {
        "event_id": event_id,
        "frame_key": f"{_gate_frame_prefix(gate)}:{phase}:{int(stream_seed)}:{int(block_index)}",
        "method": "nbpolar_target_rate",
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


def block_events(
    phase: str,
    stream_seed: int,
    block_index: int,
    arm: RateArmResult,
    *,
    n: int,
    gate_id=None,
) -> list:
    """Canonical public transcript events: L1, L2 (when invoked), final tag."""
    if arm.outcome == "resource_abort":
        return []
    gate = _normalize_gate_id(gate_id)
    k1, k2 = int(arm.k1), int(arm.k2)
    events: list[dict] = []
    l1_id = f"block-{int(block_index)}-{phase}-{arm.arm}-l1-disclosure"
    events.append(
        _event(
            phase=phase,
            stream_seed=stream_seed,
            block_index=block_index,
            event_id=l1_id,
            event_type="l1_disclosure",
            direction="alice_to_bob",
            parent_event_id=None,
            key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k1,
            public_control_bits=0,
            payload={},
            gate_id=gate,
        )
    )
    if arm.l2_invoked:
        l2_id = f"block-{int(block_index)}-{phase}-{arm.arm}-l2-disclosure"
        events.append(
            _event(
                phase=phase,
                stream_seed=stream_seed,
                block_index=block_index,
                event_id=l2_id,
                event_type="l2_disclosure",
                direction="alice_to_bob",
                parent_event_id=l1_id,
                key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k2,
                public_control_bits=0,
                payload={},
                gate_id=gate,
            )
        )
        if arm.tag_invoked:
            events.append(
                _event(
                    phase=phase,
                    stream_seed=stream_seed,
                    block_index=block_index,
                    event_id=f"block-{int(block_index)}-{phase}-{arm.arm}-verification",
                    event_type="verification_tag",
                    direction="alice_to_bob",
                    parent_event_id=l2_id,
                    key_dependent_bits=TAG_BITS,
                    public_control_bits=seed_bits_for(n),
                    payload={"seed_bit_length": seed_bits_for(n)},
                    gate_id=gate,
                )
            )
    return events


def recount_events(events) -> dict:
    """Independent literal recount; phase and arm are read literally from the event id."""
    totals = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    by_phase = {phase: dict(totals) for phase in PHASES}
    by_arm = {arm: dict(totals) for arm in ARMS}
    event_types = {"l1_disclosure": 0, "l2_disclosure": 0, "verification_tag": 0}
    for event in events:
        parts = str(event["event_id"]).split("-")
        if (
            len(parts) < 5
            or parts[0] != "block"
            or parts[2] not in PHASES
            or parts[3] not in ARMS
        ):
            raise ValueError(f"transcript event id is not phase/arm-tagged: {event['event_id']!r}")
        phase, arm = parts[2], parts[3]
        key = int(event["key_dependent_bits"])
        public = int(event["public_control_bits"])
        totals["key_dependent_bits"] += key
        totals["public_control_bits"] += public
        by_phase[phase]["key_dependent_bits"] += key
        by_phase[phase]["public_control_bits"] += public
        by_arm[arm]["key_dependent_bits"] += key
        by_arm[arm]["public_control_bits"] += public
        event_type = str(event["event_type"])
        if event_type not in event_types:
            raise ValueError(f"transcript event type is not frozen: {event_type!r}")
        event_types[event_type] += 1
        if event_type == "verification_tag":
            totals["tag_invocations"] += 1
            by_phase[phase]["tag_invocations"] += 1
            by_arm[arm]["tag_invocations"] += 1
    return {
        "key_dependent_bits": totals["key_dependent_bits"],
        "public_control_bits": totals["public_control_bits"],
        "tag_invocations": totals["tag_invocations"],
        "event_types": dict(event_types),
        "by_phase": by_phase,
        "by_arm": by_arm,
    }


def _transcript_mismatches(incremental, incremental_by_phase, incremental_by_arm, recount) -> list:
    fields = ("key_dependent_bits", "public_control_bits", "tag_invocations")
    mismatches = []
    for name in fields:
        if int(incremental[name]) != int(recount[name]):
            mismatches.append(f"total:{name}:{int(incremental[name])}!={int(recount[name])}")
    for phase in PHASES:
        for name in fields:
            left = int(incremental_by_phase[phase][name])
            right = int(recount["by_phase"][phase][name])
            if left != right:
                mismatches.append(f"{phase}:{name}:{left}!={right}")
    for arm in ARMS:
        for name in fields:
            left = int(incremental_by_arm[arm][name])
            right = int(recount["by_arm"][arm][name])
            if left != right:
                mismatches.append(f"{arm}:{name}:{left}!={right}")
    return mismatches


@dataclass(frozen=True, eq=False)
class TargetRateRun:
    """In-memory P8/P9 gate run (also returned by the runner)."""

    screen_configs: list
    screen_blocks: list
    selection: dict | None
    confirm_results: list
    confirm_records: list
    events: list
    orders: dict
    plan: dict
    summary: dict


def _check_seed_lists(screen_seed_list, confirm_seed_list, gate_id=None) -> None:
    if not screen_seed_list or not confirm_seed_list:
        raise ValueError("at least one SCREEN and one CONFIRM stream seed are required")
    if len(set(screen_seed_list)) != len(screen_seed_list):
        raise ValueError("SCREEN stream seeds must be distinct")
    if len(set(confirm_seed_list)) != len(confirm_seed_list):
        raise ValueError("CONFIRM stream seeds must be distinct")
    if not set(screen_seed_list).isdisjoint(confirm_seed_list):
        raise ValueError("SCREEN and CONFIRM stream seeds must be disjoint")
    gate = _normalize_gate_id(gate_id)
    if gate == P9_GATE_ID:
        overlap = (set(screen_seed_list) | set(confirm_seed_list)) & set(
            P9_PRIOR_OFFICIAL_STREAMS
        )
        if overlap:
            raise ValueError(
                "P9 streams overlap prior official streams: "
                f"{sorted(int(s) for s in overlap)}"
            )


def run_target_rate(
    *,
    counts=None,
    counts_path=FROZEN_COUNTS_PATH,
    orders=None,
    orders_path=FROZEN_ORDERS_PATH,
    source: str = FROZEN_SOURCE,
    n: int = FROZEN_N,
    floor=FROZEN_FLOOR,
    screen_seeds=FROZEN_SCREEN_SEEDS,
    screen_blocks: int = FROZEN_SCREEN_BLOCKS,
    k1_grid=FROZEN_K1_GRID,
    k2_grid=FROZEN_K2_GRID,
    confirm_seeds=FROZEN_CONFIRM_SEEDS,
    confirm_blocks: int = FROZEN_CONFIRM_BLOCKS,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_entropies=None,
    tag_fn=None,
    gate_id=P8_GATE_ID,
) -> TargetRateRun:
    """Execute the frozen P8/P9 SCREEN -> CONFIRM gate and write exactly five files.

    ``counts``, ``orders``, ``expected_entropies`` and ``tag_fn`` are
    documented injected test seams; the frozen CLI passes only the frozen
    point, reads the P7 orders file first and the V25 NPZ through the
    accepted loader exactly once.  ``gate_id`` selects the P8 or P9
    protocol name, tag-domain prefix, labels and frozen grid; omitted it
    defaults to the P8 gate (accepted injected-test backward compatibility).
    """
    gate = _normalize_gate_id(gate_id)
    exp_k1_grid, exp_k2_grid, exp_nconfigs = _gate_grids(gate)
    exp_screen_seeds, exp_confirm_seeds = _gate_frozen_seeds(gate)
    gate_labels = _gate_labels(gate)
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
    k1_list = [_as_int(k, "k1 grid entry", minimum=0) for k in k1_grid]
    k2_list = [_as_int(k, "k2 grid entry", minimum=0) for k in k2_grid]
    if tuple(k1_list) != tuple(exp_k1_grid) or tuple(k2_list) != tuple(exp_k2_grid):
        raise ValueError(
            f"frozen point requires k1-grid={list(exp_k1_grid)} "
            f"k2-grid={list(exp_k2_grid)}, got {k1_list}/{k2_list}"
        )
    if any(k > n for k in k1_list + k2_list):
        raise ValueError(f"k1/k2 grid entries must lie in 0..{n}")
    screen_blocks = _as_int(screen_blocks, "screen_blocks", minimum=1)
    confirm_blocks = _as_int(confirm_blocks, "confirm_blocks", minimum=1)
    screen_seed_list = [_as_int(s, "screen seed", minimum=0) for s in screen_seeds]
    confirm_seed_list = [_as_int(s, "confirm seed", minimum=0) for s in confirm_seeds]
    _check_seed_lists(screen_seed_list, confirm_seed_list, gate_id=gate)
    cap = float(total_wall_s)
    if not np.isfinite(cap) or cap <= 0:
        raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")
    tag_fn = _check_tag_fn(tag_fn)
    grid = screen_grid(k1_list, k2_list)
    assert len(grid) == exp_nconfigs  # frozen grid shape, guarded by the grid check above

    # ---- orders first: identity/permutation/surrogate refusal before any NPZ access.
    if orders is None:
        loaded_orders = load_construction_orders(orders_path)
        orders_mode = "p7_file"
        orders_source = str(Path(orders_path))
    else:
        try:
            loaded_orders = {
                "l1_empirical": np.asarray(orders["l1_empirical"], dtype=np.int64),
                "l2_empirical": np.asarray(orders["l2_empirical"], dtype=np.int64),
                "l1_bec": np.asarray(orders["l1_bec"], dtype=np.int64),
                "l2_bec": np.asarray(orders["l2_bec"], dtype=np.int64),
            }
        except (TypeError, ValueError, KeyError) as exc:
            raise OrdersIdentityError(f"injected orders are not four int64 orders: {exc}") from exc
        for key in ("l1_empirical", "l2_empirical", "l1_bec", "l2_bec"):
            if not is_valid_permutation(loaded_orders[key], n=n):
                raise OrdersIdentityError(f"injected order {key!r} is not a valid 256-permutation")
        loaded_orders["sha256"] = "injected-test-orders"
        orders_mode = "injected"
        orders_source = None
    orders_digest_before = _canonical_sha(
        {key: loaded_orders[key].tolist() for key in ("l1_empirical", "l2_empirical", "l1_bec", "l2_bec")}
    )

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
            "orders_mode": orders_mode,
            "orders_source": orders_source,
            "orders_sha256": loaded_orders["sha256"],
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
            "orders_mode": orders_mode,
            "orders_source": orders_source,
            "orders_sha256": loaded_orders["sha256"],
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

    # ---- frozen preconditions: no SC call may happen before this passes.
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

    events: list = []
    incremental = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    incremental_by_phase = {phase: dict(incremental) for phase in PHASES}
    incremental_by_arm = {arm: dict(incremental) for arm in ARMS}
    resource_stop_fired = False

    def _tally(phase: str, stream_seed: int, block_index: int, arm: RateArmResult) -> None:
        if arm.outcome == "resource_abort":
            return
        incremental["key_dependent_bits"] += int(arm.key_dependent_bits)
        incremental["public_control_bits"] += int(arm.public_control_bits)
        incremental["tag_invocations"] += int(arm.tag_invoked)
        incremental_by_phase[phase]["key_dependent_bits"] += int(arm.key_dependent_bits)
        incremental_by_phase[phase]["public_control_bits"] += int(arm.public_control_bits)
        incremental_by_phase[phase]["tag_invocations"] += int(arm.tag_invoked)
        incremental_by_arm[arm.arm]["key_dependent_bits"] += int(arm.key_dependent_bits)
        incremental_by_arm[arm.arm]["public_control_bits"] += int(arm.public_control_bits)
        incremental_by_arm[arm.arm]["tag_invocations"] += int(arm.tag_invoked)
        events.extend(block_events(phase, stream_seed, block_index, arm, n=n, gate_id=gate))

    # ---- SCREEN: sample each shared block once; every grid point reuses it.
    screen_blocks_all: list = []
    for seed in screen_seed_list:
        screen_blocks_all.extend(
            sample_shared_blocks(seed, screen_blocks, p_b=entropy.p_b, f_full=entropy.f, n=n, field=field)
        )
    l1_empirical = np.asarray(loaded_orders["l1_empirical"], dtype=np.int64)
    l2_empirical = np.asarray(loaded_orders["l2_empirical"], dtype=np.int64)
    screen_configs: list = []
    for k1, k2 in grid:
        records: list = []
        arms: list = []
        for block in screen_blocks_all:
            reason = _budget_exceeded(start, cap)
            if reason is not None:
                resource_stop_fired = True
                break
            arm = run_rate_arm(
                phase="screen",
                arm="empirical",
                block=block,
                field=field,
                p1_table=p1,
                p2_table=p2,
                l1_order=l1_empirical,
                l2_order=l2_empirical,
                k1=k1,
                k2=k2,
                n=n,
                master=block.stream_seed + PUBLIC_TAG_MASTER_OFFSET,
                tag_fn=tag_fn,
                gate_id=gate,
            )
            arms.append(arm)
            records.append(
                {
                    "stream_seed": int(block.stream_seed),
                    "block_index": int(block.block_index),
                    "empirical": _arm_record(arm),
                }
            )
            _tally("screen", block.stream_seed, block.block_index, arm)
        if resource_stop_fired:
            # Abort-fill every remaining planned SCREEN arm of this and all
            # later configurations; CONFIRM is skipped and the label blocks.
            for block in screen_blocks_all[len(arms):]:
                records.append(
                    {
                        "stream_seed": int(block.stream_seed),
                        "block_index": int(block.block_index),
                        "empirical": _aborted_arm_record("screen", "empirical", k1=k1, k2=k2),
                    }
                )
            exact = sum(1 for arm in arms if arm.exact)
            eligibility = screen_eligibility(exact, len(screen_blocks_all))
            screen_configs.append(
                {
                    "k1": int(k1),
                    "k2": int(k2),
                    "n_blocks": len(screen_blocks_all),
                    "n_executed": len(arms),
                    "exact": int(exact),
                    "eligible": False,
                    "eligibility": dict(eligibility, eligible=False),
                    "outcome_counts": {
                        name: sum(1 for arm in arms if arm.outcome == name)
                        + (
                            len(screen_blocks_all) - len(arms)
                            if name == "resource_abort"
                            else 0
                        )
                        for name in OUTCOMES
                    },
                    "blocks": records,
                    "_arms": arms,
                }
            )
            for later_k1, later_k2 in grid[len(screen_configs):]:
                screen_configs.append(
                    {
                        "k1": int(later_k1),
                        "k2": int(later_k2),
                        "n_blocks": len(screen_blocks_all),
                        "n_executed": 0,
                        "exact": 0,
                        "eligible": False,
                        "eligibility": dict(screen_eligibility(0, len(screen_blocks_all)), eligible=False),
                        "outcome_counts": {
                            name: len(screen_blocks_all) if name == "resource_abort" else 0
                            for name in OUTCOMES
                        },
                        "blocks": [
                            {
                                "stream_seed": int(block.stream_seed),
                                "block_index": int(block.block_index),
                                "empirical": _aborted_arm_record(
                                    "screen", "empirical", k1=later_k1, k2=later_k2
                                ),
                            }
                            for block in screen_blocks_all
                        ],
                        "_arms": [],
                    }
                )
            break
        exact = sum(1 for arm in arms if arm.exact)
        eligibility = screen_eligibility(exact, len(screen_blocks_all))
        screen_configs.append(
            {
                "k1": int(k1),
                "k2": int(k2),
                "n_blocks": len(screen_blocks_all),
                "n_executed": len(arms),
                "exact": int(exact),
                "eligible": bool(eligibility["eligible"]),
                "eligibility": eligibility,
                "outcome_counts": {
                    name: sum(1 for arm in arms if arm.outcome == name) for name in OUTCOMES
                },
                "blocks": records,
                "_arms": arms,
            }
        )

    # ---- deterministic selection over eligible points only.
    selection = None if resource_stop_fired else select_point(screen_configs)
    selected_k1 = int(selection["k1"]) if selection is not None else None
    selected_k2 = int(selection["k2"]) if selection is not None else None

    # ---- CONFIRM: disjoint streams, selected point + paired BEC control only.
    confirm_results: list = []
    confirm_records: list = []
    if selection is not None:
        l1_orders = {
            "empirical": l1_empirical,
            "bec": np.asarray(loaded_orders["l1_bec"], dtype=np.int64),
        }
        l2_orders = {
            "empirical": l2_empirical,
            "bec": np.asarray(loaded_orders["l2_bec"], dtype=np.int64),
        }
        for seed in confirm_seed_list:
            if resource_stop_fired:
                break
            for block in sample_shared_blocks(
                seed, confirm_blocks, p_b=entropy.p_b, f_full=entropy.f, n=n, field=field
            ):
                reason = _budget_exceeded(start, cap)
                if reason is not None:
                    resource_stop_fired = True
                    break
                pair = run_confirm_pair(
                    block,
                    field=field,
                    p1_table=p1,
                    p2_table=p2,
                    l1_orders=l1_orders,
                    l2_orders=l2_orders,
                    k1=selected_k1,
                    k2=selected_k2,
                    n=n,
                    master=seed + PUBLIC_TAG_MASTER_OFFSET,
                    tag_fn=tag_fn,
                    gate_id=gate,
                )
                confirm_results.append(pair)
                confirm_records.append(
                    {
                        "stream_seed": int(pair.stream_seed),
                        "block_index": int(pair.block_index),
                        "cell": pair.cell,
                        "k1": int(selected_k1),
                        "k2": int(selected_k2),
                        "empirical": _arm_record(pair.empirical),
                        "bec": _arm_record(pair.bec),
                    }
                )
                _tally("confirm", pair.stream_seed, pair.block_index, pair.empirical)
                _tally("confirm", pair.stream_seed, pair.block_index, pair.bec)
        if resource_stop_fired:
            missing = len(confirm_seed_list) * confirm_blocks - len(confirm_results)
            for _ in range(missing):
                confirm_records.append(
                    {
                        "stream_seed": -1,
                        "block_index": -1,
                        "cell": classify_pair(False, False),
                        "k1": int(selected_k1),
                        "k2": int(selected_k2),
                        "empirical": _aborted_arm_record(
                            "confirm", "empirical", k1=selected_k1, k2=selected_k2
                        ),
                        "bec": _aborted_arm_record(
                            "confirm", "bec", k1=selected_k1, k2=selected_k2
                        ),
                    }
                )

    wall_s = time.perf_counter() - start
    rss_peak = _peak_rss_bytes()
    orders_digest_after = _canonical_sha(
        {key: loaded_orders[key].tolist() for key in ("l1_empirical", "l2_empirical", "l1_bec", "l2_bec")}
    )

    recount = recount_events(events)
    mismatches = _transcript_mismatches(incremental, incremental_by_phase, incremental_by_arm, recount)
    gates = _integrity_gates(
        precondition_report=precondition_report,
        counts_shape=counts_arr.shape,
        orders_mode=orders_mode,
        orders_digest_before=orders_digest_before,
        orders_digest_after=orders_digest_after,
        screen_seed_list=screen_seed_list,
        screen_blocks=screen_blocks,
        screen_configs=screen_configs,
        selection=selection,
        confirm_seed_list=confirm_seed_list,
        confirm_blocks=confirm_blocks,
        confirm_results=confirm_results,
        confirm_records=confirm_records,
        confirm_executed=selection is not None,
        incremental=incremental,
        incremental_by_phase=incremental_by_phase,
        incremental_by_arm=incremental_by_arm,
        recount=recount,
        mismatches=mismatches,
        accounting=accounting,
        wall_s=wall_s,
        rss_peak=rss_peak,
        resource_stop_fired=resource_stop_fired,
        n=n,
        gate_id=gate,
    )

    # ---- aggregates, scientific gates and the registered label.
    planned_screen = len(screen_seed_list) * screen_blocks
    planned_confirm = len(confirm_seed_list) * confirm_blocks if selection is not None else 0
    eligible_points = [
        {"k1": int(c["k1"]), "k2": int(c["k2"]), "exact": int(c["exact"])}
        for c in screen_configs
        if c["eligible"]
    ]
    confirm_empirical = [r.empirical for r in confirm_results]
    confirm_bec = [r.bec for r in confirm_results]
    confirm_exact = sum(1 for arm in confirm_empirical if arm.exact)
    confirm_bec_exact = sum(1 for arm in confirm_bec if arm.exact)
    confirm_cells = {
        name: sum(1 for r in confirm_records if r["cell"] == name) for name in CELLS
    }

    def outcome_counts(arms):
        return {name: sum(1 for arm in arms if arm.outcome == name) for name in OUTCOMES}

    confirm_per_stream = {}
    for seed in confirm_seed_list:
        recs = [r for r in confirm_records if int(r["stream_seed"]) == int(seed)]
        confirm_per_stream[str(int(seed))] = {
            "records": len(recs),
            "empirical_exact": sum(1 for r in recs if r["empirical"]["exact"]),
            "bec_exact": sum(1 for r in recs if r["bec"]["exact"]),
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
    confirm_wilson = (
        wilson_lower_bound(confirm_exact, planned_confirm, z=WILSON_Z) if planned_confirm else 0.0
    )
    confirm_count_rule = bool(
        planned_confirm == FROZEN_CONFIRM_TOTAL and confirm_exact >= CONFIRM_EXACT_MIN
    )
    scientific = {
        "confirm_empirical_exact_at_least_618_of_640": bool(
            planned_confirm == FROZEN_CONFIRM_TOTAL and confirm_exact >= CONFIRM_EXACT_MIN
        ),
        "confirm_empirical_wilson_lower_bound_at_least_0p95": bool(
            planned_confirm == FROZEN_CONFIRM_TOTAL and confirm_wilson >= WILSON_MIN
        ),
    }
    scientific_all_pass = all(scientific.values())
    integrity_all_pass = all(gates.values())
    failing_integrity = [name for name in INTEGRITY_GATE_ORDER if not gates[name]]
    failing_scientific = [name for name in SCIENTIFIC_GATE_ORDER if not scientific[name]]
    shape_is_frozen = bool(
        list(screen_seed_list) == list(exp_screen_seeds)
        and screen_blocks == FROZEN_SCREEN_BLOCKS
        and tuple(k1_list) == tuple(exp_k1_grid)
        and tuple(k2_list) == tuple(exp_k2_grid)
        and list(confirm_seed_list) == list(exp_confirm_seeds)
        and confirm_blocks == FROZEN_CONFIRM_BLOCKS
        and orders_mode == "p7_file"
    )
    if not integrity_all_pass:
        outcome_label = "BLOCKED"
    elif selection is None:
        outcome_label = gate_labels["no_eligible_point"]
    elif scientific_all_pass and shape_is_frozen:
        outcome_label = gate_labels["candidate"]
    else:
        outcome_label = gate_labels["not_confirmed"]
    blocked_detail = f"BLOCKED({failing_integrity[0]})" if failing_integrity else None

    def _mean_kdb(values) -> float:
        return float(np.mean([float(v) for v in values])) if values else 0.0

    if selection is not None:
        leakage_bits = DISCLOSED_BITS_PER_COORDINATE * (selected_k1 + selected_k2) + TAG_BITS
        selected_screen_kdb = [
            float(arm.key_dependent_bits)
            for c in screen_configs
            if c["k1"] == selected_k1 and c["k2"] == selected_k2
            for arm in c["_arms"]
        ]
        mean_kdb = _mean_kdb([float(arm.key_dependent_bits) for arm in confirm_empirical])
        if not confirm_empirical:
            mean_kdb = _mean_kdb(selected_screen_kdb)
    else:
        floor_point = min(grid, key=lambda kv: (kv[0] + kv[1], kv[0], kv[1]))
        leakage_bits = DISCLOSED_BITS_PER_COORDINATE * (floor_point[0] + floor_point[1]) + TAG_BITS
        mean_kdb = _mean_kdb(
            [
                float(arm.key_dependent_bits)
                for c in screen_configs
                if c["k1"] == floor_point[0] and c["k2"] == floor_point[1]
                for arm in c["_arms"]
            ]
        )
    nH = float(n) * float(entropy.h1 + entropy.h2)

    plan = {
        "protocol": _gate_protocol(gate),
        "mode": _gate_mode(gate),
        "gate_id": gate,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "out_root": str(out_path),
        "source": source,
        "counts_path": accounting.get("counts_path"),
        "expected_npz_bytes": EXPECTED_NPZ_BYTES,
        "loader": LOADER_IDENTITY,
        "orders_path": accounting.get("orders_source"),
        "orders_mode": orders_mode,
        "orders_sha256": loaded_orders["sha256"],
        "expected_orders_sha256": EXPECTED_ORDERS_SHA,
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
        "screen_seeds": [int(s) for s in screen_seed_list],
        "screen_blocks": int(screen_blocks),
        "planned_screen_blocks": int(planned_screen),
        "k1_grid": [int(k) for k in k1_list],
        "k2_grid": [int(k) for k in k2_list],
        "n_configs": int(len(grid)),
        "screen_rule": SCREEN_RULE,
        "screen_exact_min": SCREEN_EXACT_MIN,
        "confirm_seeds": [int(s) for s in confirm_seed_list],
        "confirm_blocks": int(confirm_blocks),
        "planned_confirm_blocks": int(len(confirm_seed_list) * confirm_blocks),
        "confirm_exact_min": CONFIRM_EXACT_MIN,
        "selection_rule": "lexicographic minimum of (K1+K2, K1, K2) over eligible points only",
        "toeplitz_masters": {
            "screen": [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in screen_seed_list],
            "confirm": [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in confirm_seed_list],
        },
        "sampling_rule": SAMPLING_RULE,
        "truth_boundary": TRUTH_BOUNDARY,
        "bec_control_rule": BEC_RULE,
        "phases": list(PHASES),
        "arms": list(ARMS),
        "outcome_buckets": list(OUTCOMES),
        "outcome_precedence": list(OUTCOME_PRECEDENCE),
        "disclosure_accounting": {
            "formula": "5*(K1+K2)+64 key-dependent bits per fully invoked point",
            "public_control_bits_per_tag": int(PUBLIC_CONTROL_BITS_PER_TAG),
            "recount_rule": "independent literal transcript recount equals the incremental totals",
        },
        "toeplitz": {
            "tag_bits": TAG_BITS,
            "public_seed_bits": int(PUBLIC_CONTROL_BITS_PER_TAG),
            "derivation": (
                f"MSB-first unpack of SHA-256('{_gate_seed_prefix(gate)}:<master>:<phase>:<arm>:"
                "<block>:<counter>') concatenated over counter=0,1,...; truncated to "
                "10*n+63 bits; public control, never persisted raw"
            ),
            "phase_labels": list(PHASES),
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
                "1M/TRAIN (nll_u1/nll_u2/nll_total); ratified P7 population "
                "raw-MLE in-sample semantics"
            ),
        },
        "precondition_order": list(PRECONDITION_ORDER),
        "integrity_gate_order": list(INTEGRITY_GATE_ORDER),
        "scientific_gates": {
            "confirm_empirical_exact_at_least_618_of_640": CONFIRM_EXACT_MIN,
            "confirm_empirical_wilson_lower_bound_at_least_0p95": WILSON_MIN,
            "wilson_z": float(WILSON_Z),
        },
        "labels": {
            "candidate": gate_labels["candidate"],
            "not_confirmed": gate_labels["not_confirmed"],
            "no_eligible_point": gate_labels["no_eligible_point"],
            "blocked": gate_labels["blocked"],
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
        "frozen_command": _gate_frozen_command(gate),
        "claim_scope": CLAIM_SCOPE,
    }
    screen_file = {
        "protocol": _gate_protocol(gate),
        "gate_id": gate,
        "n_configs": int(len(grid)),
        "planned_screen_blocks": int(planned_screen),
        "configs": [
            {
                "k1": int(c["k1"]),
                "k2": int(c["k2"]),
                "n_blocks": int(c["n_blocks"]),
                "n_executed": int(c["n_executed"]),
                "exact": int(c["exact"]),
                "eligible": bool(c["eligible"]),
                "eligibility": {
                    "exact": int(c["eligibility"]["exact"]),
                    "total": int(c["eligibility"]["total"]),
                    "wilson_lower_bound": float(c["eligibility"]["wilson_lower_bound"]),
                    "wilson_z": float(WILSON_Z),
                    "count_rule_188_of_192": bool(c["eligibility"]["count_rule_188_of_192"]),
                    "wilson_count_agree": c["eligibility"]["wilson_count_agree"],
                },
                "outcome_counts": {name: int(c["outcome_counts"][name]) for name in OUTCOMES},
                "blocks": [
                    {
                        "stream_seed": int(r["stream_seed"]),
                        "block_index": int(r["block_index"]),
                        "empirical": r["empirical"],
                    }
                    for r in c["blocks"]
                ],
            }
            for c in screen_configs
        ],
    }
    selection_file = {
        "protocol": _gate_protocol(gate),
        "gate_id": gate,
        "eligible_points": eligible_points,
        "selection_rule": "lexicographic minimum of (K1+K2, K1, K2) over eligible points only",
        "selected": (
            {"k1": int(selected_k1), "k2": int(selected_k2)} if selection is not None else None
        ),
        "confirm_executed": bool(selection is not None),
        "confirm": (
            {
                "k1": int(selected_k1),
                "k2": int(selected_k2),
                "planned_blocks": int(planned_confirm),
                "n_blocks": len(confirm_records),
                "empirical_exact": int(confirm_exact),
                "bec_exact": int(confirm_bec_exact),
                "empirical_exact_rate": round(confirm_exact / max(planned_confirm, 1), 9),
                "bec_exact_rate": round(confirm_bec_exact / max(planned_confirm, 1), 9),
                "paired_exact_gap": int(confirm_exact - confirm_bec_exact),
                "cells": {name: int(confirm_cells[name]) for name in CELLS},
                "empirical_outcomes": outcome_counts(confirm_empirical),
                "bec_outcomes": outcome_counts(confirm_bec),
                "per_stream": confirm_per_stream,
                "wilson_lower_bound": float(confirm_wilson),
                "wilson_z": float(WILSON_Z),
                "count_rule_618_of_640": confirm_count_rule,
                "blocks": confirm_records,
            }
            if selection is not None
            else {"executed": False}
        ),
    }
    summary = {
        "analysis": _gate_protocol(gate),
        "mode": _gate_mode(gate),
        "gate_id": gate,
        "created_utc": plan["created_utc"],
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "source": source,
        "counts_path": accounting.get("counts_path"),
        "orders_source": accounting.get("orders_source"),
        "orders_mode": orders_mode,
        "orders_sha256": loaded_orders["sha256"],
        "input_mode": accounting.get("input_mode"),
        "q": Q,
        "n": n,
        "floor": float(floor),
        "screen_seeds": [int(s) for s in screen_seed_list],
        "screen_blocks": int(screen_blocks),
        "planned_screen_blocks": int(planned_screen),
        "k1_grid": [int(k) for k in k1_list],
        "k2_grid": [int(k) for k in k2_list],
        "n_configs": int(len(grid)),
        "eligible_points": eligible_points,
        "selected": (
            {"k1": int(selected_k1), "k2": int(selected_k2)} if selection is not None else None
        ),
        "confirm_seeds": [int(s) for s in confirm_seed_list],
        "confirm_blocks": int(confirm_blocks),
        "planned_confirm_blocks": int(planned_confirm),
        "shape_is_frozen": shape_is_frozen,
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
            "epsilon_1": float(loaded_orders.get("eps_l1", float("nan"))),
            "epsilon_2": float(loaded_orders.get("eps_l2", float("nan"))),
            "report_only": True,
        },
        "confirm_cells": {name: int(confirm_cells[name]) for name in CELLS},
        "confirm_marginals": {
            "empirical_exact": int(confirm_exact),
            "bec_exact": int(confirm_bec_exact),
            "empirical_exact_rate": round(confirm_exact / max(planned_confirm, 1), 9),
            "bec_exact_rate": round(confirm_bec_exact / max(planned_confirm, 1), 9),
            "paired_exact_gap": int(confirm_exact - confirm_bec_exact),
            "empirical_outcomes": outcome_counts(confirm_empirical),
            "bec_outcomes": outcome_counts(confirm_bec),
        },
        "confirm_per_stream": confirm_per_stream,
        "confirm_wilson_lower_bound": float(confirm_wilson),
        "wilson_z": float(WILSON_Z),
        "confirm_count_rule_618_of_640": confirm_count_rule,
        "scientific": {name: bool(scientific[name]) for name in SCIENTIFIC_GATE_ORDER},
        "scientific_all_pass": scientific_all_pass,
        "failing_scientific_gates": failing_scientific,
        "integrity": {name: bool(gates[name]) for name in INTEGRITY_GATE_ORDER},
        "integrity_all_pass": integrity_all_pass,
        "failing_integrity_gates": failing_integrity,
        "blocked_detail": blocked_detail,
        "outcome_label": outcome_label,
        "disclosure_accounting": {
            "formula": "5*(K1+K2)+64 key-dependent bits per fully invoked point",
            "selected_leakage_bits": int(leakage_bits),
            "public_control_bits_per_tag": int(PUBLIC_CONTROL_BITS_PER_TAG),
            "key_dependent_bits_total": int(incremental["key_dependent_bits"]),
            "public_control_bits_total": int(incremental["public_control_bits"]),
            "tag_invocations": int(incremental["tag_invocations"]),
            "recount": {
                "key_dependent_bits": int(recount["key_dependent_bits"]),
                "public_control_bits": int(recount["public_control_bits"]),
                "tag_invocations": int(recount["tag_invocations"]),
                "event_types": dict(recount["event_types"]),
                "by_phase": {phase: dict(recount["by_phase"][phase]) for phase in PHASES},
                "by_arm": {arm: dict(recount["by_arm"][arm]) for arm in ARMS},
            },
            "incremental_by_phase": {
                phase: dict(incremental_by_phase[phase]) for phase in PHASES
            },
            "incremental_by_arm": {arm: dict(incremental_by_arm[arm]) for arm in ARMS},
            "mismatch_count": int(len(mismatches)),
            "mismatches": list(mismatches),
        },
        "planning_f": {
            "planning_only": True,
            "mean_key_dependent_bits": float(mean_kdb),
            "nH_bits": float(nH),
            "f": float(mean_kdb / nH),
            "note": (
                "planning-only fixed-design ratio; no gate depends on f; not "
                "real-channel efficiency"
            ),
        },
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_peak": rss_peak,
        "resource_stop_fired": bool(resource_stop_fired),
        "attempt_read_accounting": dict(accounting),
        "orders_unchanged_after_run": bool(orders_digest_after == orders_digest_before),
        "claim_scope": CLAIM_SCOPE,
    }
    out_path.mkdir(parents=True)
    _write_json(out_path / "frozen_plan.json", plan)
    _write_json(out_path / "screen_records.json", screen_file)
    _write_json(out_path / "selection_and_confirmation_records.json", selection_file)
    _write_json(
        out_path / "transcript_accounting.json",
        {
            "event_count": len(events),
            "incremental": dict(incremental),
            "incremental_by_phase": {phase: dict(incremental_by_phase[phase]) for phase in PHASES},
            "incremental_by_arm": {arm: dict(incremental_by_arm[arm]) for arm in ARMS},
            "recount": {
                "key_dependent_bits": int(recount["key_dependent_bits"]),
                "public_control_bits": int(recount["public_control_bits"]),
                "tag_invocations": int(recount["tag_invocations"]),
                "event_types": dict(recount["event_types"]),
                "by_phase": {phase: dict(recount["by_phase"][phase]) for phase in PHASES},
                "by_arm": {arm: dict(recount["by_arm"][arm]) for arm in ARMS},
            },
            "mismatch_count": int(len(mismatches)),
            "mismatches": list(mismatches),
        },
    )
    (out_path / "report.md").write_text(
        _render_report(summary, screen_file, gate_id=gate), encoding="utf-8"
    )
    return TargetRateRun(
        screen_configs=screen_configs,
        screen_blocks=screen_blocks_all,
        selection=selection,
        confirm_results=confirm_results,
        confirm_records=confirm_records,
        events=events,
        orders=loaded_orders,
        plan=plan,
        summary=summary,
    )


def _integrity_gates(
    *,
    precondition_report,
    counts_shape,
    orders_mode: str,
    orders_digest_before: str,
    orders_digest_after: str,
    screen_seed_list,
    screen_blocks: int,
    screen_configs,
    selection,
    confirm_seed_list,
    confirm_blocks: int,
    confirm_results,
    confirm_records,
    confirm_executed: bool,
    incremental,
    incremental_by_phase,
    incremental_by_arm,
    recount,
    mismatches,
    accounting: dict,
    wall_s: float,
    rss_peak,
    resource_stop_fired: bool,
    n: int,
    gate_id=None,
) -> dict:
    gate = _normalize_gate_id(gate_id)
    _, _, exp_nconfigs = _gate_grids(gate)
    planned_screen = int(len(list(screen_seed_list)) * int(screen_blocks))
    planned_confirm = int(len(list(confirm_seed_list)) * int(confirm_blocks))
    # Decision path: eligible SCREEN arms plus CONFIRM arms.  Rejected SCREEN
    # configurations are report-only (their verify/decode failures are the
    # screen working, not an integrity break); truth leakage is global.
    decision_arms: list = []
    for config in screen_configs:
        if config.get("eligible"):
            decision_arms.extend(config.get("_arms", []))
    decision_arms.extend([r.empirical for r in confirm_results])
    decision_arms.extend([r.bec for r in confirm_results])
    all_screen_arms: list = []
    for config in screen_configs:
        all_screen_arms.extend(config.get("_arms", []))
    all_arms = list(all_screen_arms) + [r.empirical for r in confirm_results] + [
        r.bec for r in confirm_results
    ]

    def count(arms, outcome):
        return sum(1 for arm in arms if arm.outcome == outcome)

    screen_ok = all(
        len(config.get("blocks", [])) == planned_screen
        and sum(config["outcome_counts"].values()) == planned_screen
        for config in screen_configs
    ) and len(screen_configs) == exp_nconfigs
    screen_streams_ok = bool(screen_configs) and all(
        sorted((r["stream_seed"], r["block_index"]) for r in config.get("blocks", []))
        == sorted(
            (int(seed), block)
            for seed in screen_seed_list
            for block in range(int(screen_blocks))
        )
        for config in screen_configs
    )
    confirm_ok = True
    if confirm_executed:
        confirm_ok = bool(
            len(confirm_records) == planned_confirm
            and {int(r["stream_seed"]) for r in confirm_records if int(r["stream_seed"]) >= 0}
            <= {int(s) for s in confirm_seed_list}
            and all(r["cell"] in CELLS for r in confirm_records)
            and all(
                int(r["k1"]) == int(selection["k1"]) and int(r["k2"]) == int(selection["k2"])
                for r in confirm_records
            )
        )
    coverage = bool(
        screen_ok
        and screen_streams_ok
        and confirm_ok
        and set(int(s) for s in screen_seed_list).isdisjoint(
            int(s) for s in confirm_seed_list
        )
    )
    per_record_ok = all(_arm_record_consistent(arm, n=n) for arm in all_arms)
    buckets_ok = all(
        sum(count(config.get("_arms", []), name) for name in OUTCOMES)
        + config["outcome_counts"].get("resource_abort", 0)
        == planned_screen
        for config in screen_configs
    )
    if confirm_executed:
        op = [r.empirical for r in confirm_results]
        bec = [r.bec for r in confirm_results]
        buckets_ok = bool(
            buckets_ok
            and sum(count(arms, name) for arms in (op, bec) for name in OUTCOMES)
            + 2 * (planned_confirm - len(confirm_results))
            == 2 * planned_confirm
        )
    executed = [arm for arm in all_arms if arm.outcome != "resource_abort"]
    fully_invoked = [
        arm for arm in executed if arm.tag_invoked and arm.l2_invoked and arm.l1_executed
    ]
    fully_invoked_exact = all(
        int(arm.key_dependent_bits)
        == DISCLOSED_BITS_PER_COORDINATE * (int(arm.k1) + int(arm.k2)) + TAG_BITS
        for arm in fully_invoked
    )
    tags_accounted = all(
        int(arm.public_control_bits) == (seed_bits_for(n) if arm.tag_invoked else 0)
        for arm in executed
    )
    totals_ok = (
        int(incremental["key_dependent_bits"]) == int(recount["key_dependent_bits"])
        and int(incremental["public_control_bits"]) == int(recount["public_control_bits"])
        and int(incremental["tag_invocations"]) == int(recount["tag_invocations"])
        and all(
            int(incremental_by_phase[phase][name]) == int(recount["by_phase"][phase][name])
            for phase in PHASES
            for name in ("key_dependent_bits", "public_control_bits", "tag_invocations")
        )
        and all(
            int(incremental_by_arm[arm][name]) == int(recount["by_arm"][arm][name])
            for arm in ARMS
            for name in ("key_dependent_bits", "public_control_bits", "tag_invocations")
        )
    )
    n_executed_arms = len(executed)
    n_l2 = sum(1 for arm in executed if arm.l2_invoked)
    n_tag = sum(1 for arm in executed if arm.tag_invoked)
    mode = str(accounting.get("input_mode"))
    if mode == "v25_npz":
        read_exact = (
            int(accounting["artifact_content_reads_consumed_by_this_run"]) == 1
            and int(accounting["attempts_consumed_by_this_run"]) == 1
            and int(accounting["open_count"]) == 1
            and bool(accounting["stat_size_checked"])
            and int(accounting["observed_npz_bytes"]) == int(accounting["expected_npz_bytes"])
            and str(accounting.get("orders_mode")) == "p7_file"
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
        "orders_identity_and_permutations": bool(
            orders_digest_after == orders_digest_before
            and str(accounting.get("orders_sha256")) in (EXPECTED_ORDERS_SHA, "injected-test-orders")
            and (orders_mode == "injected" or str(accounting.get("orders_mode")) == "p7_file")
        ),
        "target_population_contract": bool(precondition_report.passed),
        "coverage_complete_and_disjoint": coverage,
        "pairing_and_buckets": bool(buckets_ok and per_record_ok),
        "truth_leak_zero": not any(arm.truth_leak_violation for arm in all_arms),
        "undetected_zero": count(decision_arms, "undetected") == 0,
        "nonfinite_zero": not any(arm.nonfinite for arm in decision_arms),
        "resource_abort_zero": count(all_arms, "resource_abort") == 0
        and not resource_stop_fired,
        "disclosure_and_recount_exact": bool(
            fully_invoked_exact
            and tags_accounted
            and totals_ok
            and not mismatches
            and recount["event_types"].get("l1_disclosure", 0) == n_executed_arms
            and recount["event_types"].get("l2_disclosure", 0) == n_l2
            and recount["event_types"].get("verification_tag", 0) == n_tag
        ),
        "attempt_read_accounting_exact": accounting_exact,
        "resource_limits_met": bool(
            float(wall_s) <= TOTAL_WALL_S
            and (rss_peak is None or int(rss_peak) <= RSS_LIMIT_BYTES)
        ),
    }
    return gates


def _render_report(summary: dict, screen_file: dict, gate_id=None) -> str:
    gate = _normalize_gate_id(gate_id)
    if gate == P9_GATE_ID:
        title = "# NB-Polar Phase 4-P9 lower-rate boundary SCREEN -> CONFIRM gate"
        grid_header = f"## SCREEN grid ({P9_FROZEN_NCONFIGS} configurations)"
    else:
        title = "# NB-Polar Phase 4-P8 target rate SCREEN -> CONFIRM gate"
        grid_header = "## SCREEN grid (35 configurations)"
    lines = [
        title,
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- source/target: `{summary['source']}`; q={summary['q']}, N={summary['n']}, "
        f"floor={summary['floor']}",
        f"- SCREEN: {summary['screen_seeds']} x {summary['screen_blocks']} blocks = "
        f"{summary['planned_screen_blocks']} shared blocks x {summary['n_configs']} configs",
        f"- CONFIRM: {summary['confirm_seeds']} x {summary['confirm_blocks']} blocks",
        f"- orders: `{summary['orders_mode']}` sha `{summary['orders_sha256']}`",
        f"- wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes; "
        f"resource stop fired: {summary['resource_stop_fired']}",
        "",
        grid_header,
        "",
        "| k1 | k2 | exact/192 | wilson_lb | count_188 | eligible |",
        "|---|---|---|---|---|---|",
    ]
    for config in screen_file["configs"]:
        elig = config["eligibility"]
        lines.append(
            f"| {config['k1']} | {config['k2']} | {config['exact']}/{config['n_blocks']} | "
            f"{elig['wilson_lower_bound']!r} | {elig['count_rule_188_of_192']} | "
            f"{config['eligible']} |"
        )
    lines += [
        "",
        "## Deterministic selection",
        "",
        f"- eligible points: {summary['eligible_points']}",
        f"- selected: `{summary['selected']}`",
        f"- rule: lexicographic minimum of (K1+K2, K1, K2) over eligible points only",
        "",
        "## CONFIRM (selected point + paired BEC control)",
        "",
    ]
    confirm = summary["confirm_marginals"]
    if summary["selected"] is not None:
        lines += [
            f"- point: K1={summary['selected']['k1']}, K2={summary['selected']['k2']}",
            f"- empirical exact: {confirm['empirical_exact']}/{summary['planned_confirm_blocks']}; "
            f"BEC exact: {confirm['bec_exact']}/{summary['planned_confirm_blocks']}",
            f"- one-sided 95% Wilson lower bound: {summary['confirm_wilson_lower_bound']!r}; "
            f"count rule 618/640: {summary['confirm_count_rule_618_of_640']}",
            f"- paired cells: {summary['confirm_cells']}",
            "",
            "### CONFIRM per-stream (5x128)",
            "",
            "| stream | records | empirical_exact | bec_exact |",
            "|---|---|---|---|",
        ]
        for seed, rec in summary["confirm_per_stream"].items():
            lines.append(
                f"| {seed} | {rec['records']} | {rec['empirical_exact']} | {rec['bec_exact']} |"
            )
        lines.append("")
    else:
        lines += ["- CONFIRM not executed (no eligible SCREEN point).", ""]
    integrity = summary["integrity"]
    scientific = summary["scientific"]
    accounting = summary["disclosure_accounting"]
    lines += [
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
        f"- fully invoked point: `{accounting['formula']}`; public control "
        f"{accounting['public_control_bits_per_tag']} bits per tag",
        f"- selected-point leakage: {accounting['selected_leakage_bits']} key-dependent bits",
        f"- key-dependent total: {accounting['key_dependent_bits_total']}; public total: "
        f"{accounting['public_control_bits_total']}; tags: {accounting['tag_invocations']}",
        f"- recount mismatch count: {accounting['mismatch_count']}",
        "",
        "## Planning-only f",
        "",
        f"- mean key-dependent {summary['planning_f']['mean_key_dependent_bits']!r} bits / nH "
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
        prog="nbpolar-target-rate",
        description=(
            "NB-Polar Phase 4-P8/P9 target rate SCREEN -> CONFIRM development gate "
            "(frozen V25 1M TRAIN counts, accepted P7 orders)"
        ),
    )
    # Closed-choice gate selector (P9 delta-only). Optional at parse time so
    # accepted P8 callers without a gate id still parse; ``main`` refuses a
    # missing gate id before any artifact access, and the frozen P9 command
    # always carries ``--gate-id p9-lower-rate-boundary`` first.
    parser.add_argument(
        "--gate-id",
        required=False,
        default=None,
        choices=list(GATE_IDS),
        dest="gate_id",
    )
    parser.add_argument("--counts", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--orders", required=True)
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--floor", required=True, type=float)
    parser.add_argument("--screen-seeds", required=True, type=int, nargs="+", dest="screen_seeds")
    parser.add_argument("--screen-blocks", required=True, type=int, dest="screen_blocks")
    parser.add_argument("--k1-grid", required=True, type=int, nargs="+", dest="k1_grid")
    parser.add_argument("--k2-grid", required=True, type=int, nargs="+", dest="k2_grid")
    parser.add_argument(
        "--confirm-seeds", required=True, type=int, nargs="+", dest="confirm_seeds"
    )
    parser.add_argument("--confirm-blocks", required=True, type=int, dest="confirm_blocks")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.gate_id is None:
        print("nbpolar target rate refused: missing required --gate-id", file=sys.stderr)
        return 2
    try:
        gate = _normalize_gate_id(args.gate_id)
    except ValueError as exc:
        print(f"nbpolar target rate refused: {exc}", file=sys.stderr)
        return 2
    try:
        run = run_target_rate(
            counts_path=args.counts,
            source=args.source,
            orders_path=args.orders,
            n=args.n,
            floor=args.floor,
            screen_seeds=args.screen_seeds,
            screen_blocks=args.screen_blocks,
            k1_grid=args.k1_grid,
            k2_grid=args.k2_grid,
            confirm_seeds=args.confirm_seeds,
            confirm_blocks=args.confirm_blocks,
            out_dir=args.out_dir,
            gate_id=gate,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar target rate refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "gate_id": summary.get("gate_id"),
                "n_configs": summary["n_configs"],
                "eligible_points": summary["eligible_points"],
                "selected": summary["selected"],
                "confirm_empirical_exact": summary["confirm_marginals"]["empirical_exact"],
                "confirm_wilson_lower_bound": summary["confirm_wilson_lower_bound"],
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
