"""NB-Polar Phase 4-P5 hard-L1 conditioning penalty gate (synthetic only).

Frozen point (packet ``NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY``): GF32
polynomial basis, primitive polynomial 37, alpha 2, natural order, ``N=256``;
``epsilon1=0.05``; strong dependent-L2 profile
``epsilon2(u1) = 0.02 + 0.36*u1/31`` (mean 0.20); ``K1=45``, ``K2=140``;
three fresh streams 2026091470..2026091472 with 128 paired blocks each (384
pairs, one attempt); public tag master ``seed + 10000``.

The injected ``[Alice,Bob]`` table is ``P(B|A) = Ph(B_high|high) *
Pl(B_low|low, high)`` with a q=32 marked-erasure kernel whose per-position
erasure probability is the profile function of the HIGH value; columns sum to 1
within 1e-12.  Unlike the P4 independent-layer model, the L2 metric rows now
differ across ``u1``; ``p2_maxdiff`` is the exact cross-``u1`` all-pairs maximum
difference of the derived ``P2`` (0.34875 at the strong profile) and is computed
and required to be >= 0.30 before any decoder call.

The gate runs the accepted ``two_layer.run_two_layer_block`` in memory for the
paired operational + isolated-oracle arms, records the four-cell paired table
(``both_exact`` / ``oracle_only`` / ``operational_only`` / ``neither``), and
computes the one-sided 95% exact lower bound ``L`` for the oracle-only event by
monotone bisection of ``sum_{j=X}^{384} C(384,j) L^j (1-L)^(384-j) = 0.05``
(``X`` = oracle-only count; stdlib ``math`` only, log-space terms; ``X=0`` ->
0.0 and ``X=384`` -> ``0.05**(1/384)``).  A binomial interval is never applied
to the difference of two marginal rates.

Outcome label: ``HARD_L1_CONDITIONING_PENALTY_CANDIDATE`` iff every integrity
gate passes and the frozen discriminator passes at the 384-pair shape,
``HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED`` iff integrity passes but the
discriminator fails, otherwise ``BLOCKED`` with the failing gate names.  The
label is a synthetic single-point N=256 mechanism signal only: not real-data
FER, efficiency, qualification or promotion; operational-arm numbers are
interface diagnostics.

Reuses the accepted P4 module unchanged (no decoder, construction, prior or
protocol edits).  Synthetic injected tables only: no stored data product, no
real frame, no N>256, no scalable or list decoder, no cross-layer soft path, no
import-time I/O, no global RNG.  The only output is the explicit development
CLI and its five compact scalar-only files; symbols, labels, disclosed values
and raw seed bits are never persisted.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from numbers import Integral, Real
from pathlib import Path

import numpy as np

from . import two_layer as tl
from .algebra import make_gf32
from .prior import Provenance

try:  # POSIX (the frozen command runs under WSL); Windows native has no resource module.
    import resource
except ImportError:  # pragma: no cover - exercised only on Windows native
    resource = None

PROTOCOL_NAME = "nbpolar-p5-hard-conditioning-penalty-gate"
MODE = "paired-penalty-dev-gate"
Q = 32
ALPHA = 2
LABEL_SCALE = 32
FROZEN_N = 256
FROZEN_EPSILON1 = 0.05
FROZEN_PROFILE = "strong"
PROFILE_MEAN_EPSILON2 = 0.20
FROZEN_K1 = 45
FROZEN_K2 = 140
FROZEN_SEEDS = (2026091470, 2026091471, 2026091472)
FROZEN_BLOCKS_PER_SEED = 128
FROZEN_PAIRS = 384
PUBLIC_TAG_MASTER_OFFSET = 10000
P2_MAXDIFF_FLOOR = 0.30
ORACLE_EXACT_MIN = 365
LOWER_BOUND_MIN = 0.30
LOWER_BOUND_TARGET = 0.05
TAG_BITS = 64
DISCLOSED_BITS_PER_COORDINATE = 5
FULLY_INVOKED_ARM_BITS = DISCLOSED_BITS_PER_COORDINATE * (FROZEN_K1 + FROZEN_K2) + TAG_BITS
RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 3600.0
EXTERNAL_TIMEOUT_S = 3600
ULIMIT_VIRTUAL_KIB = 2097152
ATTEMPT_CONSUMPTION_POINT = "first gate L1 SC call (stream 0, block 0)"
# Frozen accounting record: one allowed attempt, none consumed before this run,
# exactly one consumed by the single gate pass, no retries and no ledger update.
ATTEMPT_ACCOUNTING = {
    "attempts_allowed": 1,
    "attempts_consumed_before": 0,
    "attempts_consumed_by_this_run": 1,
    "retries": 0,
}
PROFILE_FORMULAS = {
    "weak": "0.14 + 0.12*u1/31",
    "medium": "0.08 + 0.24*u1/31",
    "strong": "0.02 + 0.36*u1/31",
}
# The P4 accepted runner refuses the Phase 1-6 consumed streams; P5 additionally
# refuses the P4 gate streams 2026091360/2026091361 and accepts 2026091470..1472.
BANNED_SEEDS = frozenset(tl.BANNED_RUN_SEEDS) | {2026091360, 2026091361}
ARMS = ("operational", "oracle")
CELLS = ("both_exact", "oracle_only", "operational_only", "neither")
INTEGRITY_GATE_ORDER = (
    "pairing_coverage_complete",
    "p2_maxdiff_at_least_0p30",
    "provenance_candidate_oracle_complete",
    "operational_truth_leak_zero",
    "undetected_zero",
    "nonfinite_zero",
    "resource_abort_zero",
    "cells_disjoint_exhaustive",
    "disclosures_exact_and_transcript_recount_zero",
    "attempt_accounting_at_frozen_point",
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "per_block_paired_outcomes.json",
    "transcript_accounting.json",
    "aggregate_summary.json",
    "report.md",
)
FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "ulimit -v 2097152\n"
    "timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.penalty_gate "
    "--n 256 --epsilon1 0.05 --profile strong --k1 45 --k2 140 "
    "--seeds 2026091470 2026091471 2026091472 --blocks-per-seed 128 "
    "--out-dir .workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/"
    "paired_penalty_gate"
)
CLAIM_SCOPE = (
    "synthetic single-point N=256 hard-conditioning penalty signal only; not "
    "real-data FER, efficiency, qualification or promotion; operational-arm "
    "numbers are interface diagnostics"
)

__all__ = [
    "PROTOCOL_NAME",
    "MODE",
    "Q",
    "ALPHA",
    "FROZEN_N",
    "FROZEN_EPSILON1",
    "FROZEN_PROFILE",
    "PROFILE_MEAN_EPSILON2",
    "FROZEN_K1",
    "FROZEN_K2",
    "FROZEN_SEEDS",
    "FROZEN_BLOCKS_PER_SEED",
    "FROZEN_PAIRS",
    "PUBLIC_TAG_MASTER_OFFSET",
    "P2_MAXDIFF_FLOOR",
    "ORACLE_EXACT_MIN",
    "LOWER_BOUND_MIN",
    "LOWER_BOUND_TARGET",
    "TAG_BITS",
    "DISCLOSED_BITS_PER_COORDINATE",
    "FULLY_INVOKED_ARM_BITS",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S",
    "ULIMIT_VIRTUAL_KIB",
    "ATTEMPT_CONSUMPTION_POINT",
    "ATTEMPT_ACCOUNTING",
    "PROFILE_FORMULAS",
    "BANNED_SEEDS",
    "ARMS",
    "CELLS",
    "INTEGRITY_GATE_ORDER",
    "OUTPUT_FILES",
    "FROZEN_COMMAND",
    "CLAIM_SCOPE",
    "profile_epsilon2",
    "build_dependent_joint_table",
    "p2_cross_u1_maxdiff",
    "require_p2_maxdiff",
    "DependentBlock",
    "sample_dependent_block",
    "classify_cell",
    "binomial_tail_probability",
    "exact_lower_bound",
    "PenaltyGateRun",
    "run_penalty_gate",
    "build_parser",
    "main",
]


def _as_int(value, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer, got {value!r}")
    out = int(value)
    if minimum is not None and out < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {out}")
    return out


def _checked_epsilon(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, got {value!r}")
    out = float(value)
    if not 0.0 <= out <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1], got {out}")
    return out


def profile_epsilon2(profile: str) -> np.ndarray:
    """Per-``u1`` erasure vector of the frozen dependent-L2 profiles (mean 0.20)."""
    u1 = np.arange(Q, dtype=np.float64)
    if profile == "weak":
        e2 = 0.14 + 0.12 * u1 / 31.0
    elif profile == "medium":
        e2 = 0.08 + 0.24 * u1 / 31.0
    elif profile == "strong":
        e2 = 0.02 + 0.36 * u1 / 31.0
    else:
        raise ValueError(f"unknown dependent-L2 profile {profile!r}")
    if not np.isclose(float(e2.mean()), PROFILE_MEAN_EPSILON2, atol=1e-12):
        raise AssertionError(f"profile {profile} mean epsilon2 != {PROFILE_MEAN_EPSILON2}")
    return e2


def build_dependent_joint_table(*, profile: str, epsilon1=FROZEN_EPSILON1) -> np.ndarray:
    """Explicit ``[Alice,Bob]`` table ``P(B|A) = Ph(B_high|high) * Pl(B_low|low, high)``.

    The low-layer kernel depends on the HIGH value through the profile erasure
    probability ``epsilon2(high)``.  Columns sum to 1 within 1e-12 by
    construction (asserted, never renormalized, so the derived ``P2`` is the
    exact frozen arithmetic).
    """
    eps1 = _checked_epsilon(epsilon1, "epsilon1")
    e2 = profile_epsilon2(profile)
    ph = tl.layer_observation_matrix(eps1)
    a = np.arange(Q * Q)
    ah, al = a // Q, a % Q
    b = np.arange(Q * Q)
    bh, bl = b // Q, b % Q
    table = np.zeros((Q * Q, Q * Q), dtype=np.float64)
    for high in range(Q):
        pl = tl.layer_observation_matrix(float(e2[high]))
        idx = np.where(ah == high)[0]
        table[np.ix_(idx, b)] = ph[high, bh][None, :] * pl[al[idx][:, None], bl[None, :]]
    deviation = float(np.abs(table.sum(axis=0) - 1.0).max())
    if deviation > 1e-12:
        raise AssertionError(f"dependent joint table is not column normalized: {deviation:.3e}")
    return table


def p2_cross_u1_maxdiff(p2) -> float:
    """``max_{u1,u1',b,u2} |P2[u1,b,u2] - P2[u1',b,u2]|`` (exact all-pairs form)."""
    arr = np.asarray(p2, dtype=np.float64)
    if arr.shape != (Q, Q * Q, Q):
        raise ValueError(f"axis contract: p2 must be [U1,B,U2] ({Q},{Q * Q},{Q}), got {arr.shape}")
    return float((arr.max(axis=0) - arr.min(axis=0)).max())


def require_p2_maxdiff(value, *, floor: float = P2_MAXDIFF_FLOOR) -> float:
    """Fail closed before any decoder call when the table carries no hard penalty."""
    out = float(value)
    if not out >= float(floor):
        raise ValueError(f"refusing to decode: p2_maxdiff {out!r} < floor {float(floor)!r}")
    return out


@dataclass(frozen=True, eq=False)
class DependentBlock:
    """One sampled dependent-model block: layer truth and packed Bob symbol."""

    high: np.ndarray  # int64[N] Alice high layer
    low: np.ndarray  # int64[N] Alice low layer
    bob: np.ndarray  # int64[N] = 32*b_high + b_low


def sample_dependent_block(rng, *, n: int, epsilon1, profile: str) -> DependentBlock:
    """Sample one block with the caller-owned explicit RNG.

    Frozen draw order: ``high`` uniform GF32, ``low`` uniform GF32, the
    ``B_high`` observation (erasure mask with ``epsilon1``, then replacement
    draws for erased positions), then the ``B_low`` observation (erasure mask
    with the per-position ``epsilon2(high)``, then replacements).  No global
    RNG, no I/O.
    """
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be an explicit numpy.random.Generator (no hidden global RNG)")
    n = _as_int(n, "n", minimum=1)
    eps1 = _checked_epsilon(epsilon1, "epsilon1")
    e2 = profile_epsilon2(profile)

    high = rng.integers(0, Q, size=n).astype(np.int64)
    low = rng.integers(0, Q, size=n).astype(np.int64)
    b_high = high.copy()
    erased_high = rng.random(n) < eps1
    if bool(erased_high.any()):
        idx = np.where(erased_high)[0]
        b_high[idx] = rng.integers(0, Q, size=idx.size).astype(np.int64)
    b_low = low.copy()
    erased_low = rng.random(n) < e2[high]
    if bool(erased_low.any()):
        idx = np.where(erased_low)[0]
        b_low[idx] = rng.integers(0, Q, size=idx.size).astype(np.int64)
    return DependentBlock(high=high, low=low, bob=(LABEL_SCALE * b_high + b_low).astype(np.int64))


def classify_cell(operational_exact: bool, oracle_exact: bool) -> str:
    """Paired four-cell label; the four cells are disjoint and exhaustive."""
    if operational_exact and oracle_exact:
        return "both_exact"
    if operational_exact:
        return "operational_only"
    if oracle_exact:
        return "oracle_only"
    return "neither"


def binomial_tail_probability(level, n: int, x: int) -> float:
    """``P[Bin(n, level) >= x]`` summed in log space (stdlib ``math`` only)."""
    level = float(level)
    n = _as_int(n, "n", minimum=1)
    x = _as_int(x, "x", minimum=0)
    if x > n:
        return 0.0
    if level <= 0.0:
        return 1.0 if x == 0 else 0.0
    if level >= 1.0:
        return 1.0
    log_level = math.log(level)
    log_left = math.log1p(-level)
    total = 0.0
    for j in range(x, n + 1):
        total += math.exp(math.log(math.comb(n, j)) + j * log_level + (n - j) * log_left)
    return total


def exact_lower_bound(x, n, *, target: float = LOWER_BOUND_TARGET) -> float:
    """One-sided 95% exact lower bound ``L`` with ``P[Bin(n, L) >= x] = target``.

    Monotone bisection (the tail is increasing in ``L``); log-space terms only.
    Frozen edge handling: ``x=0`` -> ``0.0``; ``x=n`` -> ``target**(1/n)``.
    """
    x = _as_int(x, "x", minimum=0)
    n = _as_int(n, "n", minimum=1)
    if x > n:
        raise ValueError(f"x must lie in 0..{n}, got {x}")
    target = float(target)
    if not 0.0 < target < 1.0:
        raise ValueError(f"target must lie in (0, 1), got {target!r}")
    if x == 0:
        return 0.0
    if x == n:
        return float(target ** (1.0 / n))
    lo, hi = 0.0, 1.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        if binomial_tail_probability(mid, n, x) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


@dataclass(frozen=True, eq=False)
class PenaltyGateRun:
    """In-memory paired penalty gate run (also returned by the runner)."""

    results: list
    records: list
    events: list
    plan: dict
    transcript: dict
    summary: dict


def _arm_record(arm) -> dict:
    """Compact scalar-only record; symbol/label arrays are never persisted."""
    return {
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


def _block_record(stream_seed: int, result) -> dict:
    return {
        "stream_seed": int(stream_seed),
        "block_index": int(result.block_index),
        "cell": classify_cell(result.operational.exact, result.oracle.exact),
        "operational": _arm_record(result.operational),
        "oracle": _arm_record(result.oracle),
    }


def _literal_recount(events) -> dict:
    """Independent literal transcript recount (parses the arm from the event id)."""
    totals = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    by_arm = {arm: dict(totals) for arm in ARMS}
    event_types = {"l1_disclosure": 0, "l2_disclosure": 0, "verification_tag": 0}
    for event in events:
        parts = str(event["event_id"]).split("-")
        if len(parts) < 3 or parts[0] != "block" or parts[2] not in ARMS:
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


def _integrity_gates(
    *,
    planned: int,
    results,
    p2_maxdiff: float,
    incremental,
    incremental_by_arm,
    recount,
    mismatches,
    k1: int,
    k2: int,
    n: int,
) -> tuple:
    op = [r.operational for r in results]
    orc = [r.oracle for r in results]
    both = sum(1 for a, b in zip(op, orc) if a.exact and b.exact)
    oracle_only = sum(1 for a, b in zip(op, orc) if (not a.exact) and b.exact)
    operational_only = sum(1 for a, b in zip(op, orc) if a.exact and (not b.exact))
    neither = sum(1 for a, b in zip(op, orc) if (not a.exact) and (not b.exact))
    cells = {
        "both_exact": both,
        "oracle_only": oracle_only,
        "operational_only": operational_only,
        "neither": neither,
    }
    provenance_operational = sum(
        1 for a in op if a.l2_provenance == Provenance.CANDIDATE_CONDITIONED.value
    )
    provenance_oracle = sum(
        1 for b in orc if b.l2_provenance == Provenance.ORACLE_CONDITIONED.value
    )
    fully_invoked = [a for a in op + orc if a.tag_invoked and a.l2_invoked and a.l1_executed]
    fully_invoked_exact = all(
        int(a.key_dependent_bits) == DISCLOSED_BITS_PER_COORDINATE * (k1 + k2) + TAG_BITS
        for a in fully_invoked
    )
    tag_public_exact = all(
        int(a.public_control_bits) == tl.seed_bits_for(n) for a in op + orc if a.tag_invoked
    )
    totals_match = all(
        int(incremental[name]) == int(recount[name])
        for name in ("key_dependent_bits", "public_control_bits", "tag_invocations")
    ) and all(
        int(incremental_by_arm[arm][name]) == int(recount["by_arm"][arm][name])
        for arm in ARMS
        for name in ("key_dependent_bits", "public_control_bits", "tag_invocations")
    )
    gates = {
        "pairing_coverage_complete": len(results) == planned,
        "p2_maxdiff_at_least_0p30": bool(float(p2_maxdiff) >= P2_MAXDIFF_FLOOR),
        "provenance_candidate_oracle_complete": bool(
            provenance_operational == planned and provenance_oracle == planned
        ),
        "operational_truth_leak_zero": not any(a.truth_leak_violation for a in op),
        "undetected_zero": not any(a.outcome == "undetected" for a in op + orc),
        "nonfinite_zero": not any(a.nonfinite for a in op + orc),
        "resource_abort_zero": not any(a.outcome == "resource_abort" for a in op + orc),
        "cells_disjoint_exhaustive": bool(sum(cells.values()) == planned),
        "disclosures_exact_and_transcript_recount_zero": bool(
            fully_invoked_exact and tag_public_exact and not mismatches and totals_match
        ),
        "attempt_accounting_at_frozen_point": bool(
            int(ATTEMPT_ACCOUNTING["attempts_allowed"]) == 1
            and int(ATTEMPT_ACCOUNTING["attempts_consumed_before"]) == 0
            and int(ATTEMPT_ACCOUNTING["attempts_consumed_by_this_run"]) == 1
            and int(ATTEMPT_ACCOUNTING["retries"]) == 0
            and len(results) == planned
        ),
    }
    provenance_counts = {
        "operational_candidate_conditioned": provenance_operational,
        "oracle_oracle_conditioned": provenance_oracle,
    }
    return gates, cells, provenance_counts


def _peak_rss_bytes() -> int | None:
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_plan(
    *,
    out_path: Path,
    n: int,
    epsilon1: float,
    profile: str,
    k1: int,
    k2: int,
    seeds,
    blocks_per_seed: int,
    d1,
    d2,
    table_deviation: float,
    p2_maxdiff: float,
    total_wall_s: float,
) -> dict:
    masters = [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in seeds]
    return {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "out_root": str(out_path),
        "seeds": [int(s) for s in seeds],
        "toeplitz_masters": masters,
        "blocks_per_seed": int(blocks_per_seed),
        "planned_pairs": int(len(list(seeds)) * blocks_per_seed),
        "q": Q,
        "n": int(n),
        "k1": int(k1),
        "k2": int(k2),
        "epsilon1": float(epsilon1),
        "profile": profile,
        "epsilon2_formula": PROFILE_FORMULAS[profile],
        "epsilon2_mean": PROFILE_MEAN_EPSILON2,
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "dependent_table": {
            "formula": "P(B|A) = Ph(B_high|high) * Pl(B_low|low, high)",
            "kernel": (
                "q=32 marked-erasure kernel; per-position erasure probability is "
                "the profile function of the HIGH value"
            ),
            "column_normalization_tolerance": 1e-12,
            "column_max_deviation": float(table_deviation),
            "p2_maxdiff_definition": (
                "max_{u1,u1',b,u2} |P2[u1,b,u2] - P2[u1',b,u2]| on the derived "
                "[U1,B,U2] table before any decoder call"
            ),
            "p2_maxdiff": float(p2_maxdiff),
            "p2_maxdiff_floor": P2_MAXDIFF_FLOOR,
        },
        "disclosure_rule": (
            "D1 = sorted(analytic_order(0.05, n)[:k1]); D2 = "
            "sorted(analytic_order(0.20, n)[:k2]); publish actual GF32 U1[D1]/U2[D2] "
            "values including zeros; SC known_positions = the sorted sets"
        ),
        "disclosure_coordinates": {
            "D1": [int(v) for v in d1],
            "D2": [int(v) for v in d2],
        },
        "arms": list(ARMS),
        "pairing": (
            "one run_two_layer_block call per block; the operational and oracle arms "
            "share the block, the disclosures and the stream Toeplitz master"
        ),
        "sampling_order": (
            "per block: high uniform, low uniform, B_high erasure mask + replacements, "
            "B_low erasure mask with per-position epsilon2(high) + replacements; "
            "explicit np.random.default_rng(seed) per stream, no global RNG"
        ),
        "provenance_rules": {
            "p1_operational": Provenance.PRIOR_ONLY.value,
            "p2_operational": Provenance.CANDIDATE_CONDITIONED.value,
            "p2_oracle": Provenance.ORACLE_CONDITIONED.value,
            "truth_allowed_only_in": ["oracle arm", "disclosed-U map", "scoring"],
            "no_app_or_soft_belief": True,
        },
        "cells": list(CELLS),
        "cell_rule": (
            "both_exact = op and oracle exact; oracle_only = not op and oracle; "
            "operational_only = op and not oracle (structurally impossible when the "
            "L1 candidate is correct; must be 0); neither = not op and not oracle"
        ),
        "integrity_gate_order": list(INTEGRITY_GATE_ORDER),
        "discriminator": {
            "oracle_exact_min": ORACLE_EXACT_MIN,
            "operational_only_max": 0,
            "lower_bound_target": LOWER_BOUND_TARGET,
            "lower_bound_threshold": LOWER_BOUND_MIN,
            "definition": (
                "oracle_exact >= 365; operational_only == 0; L = root of "
                "sum_{j=X}^{384} C(384,j) L^j (1-L)^(384-j) = 0.05 by monotone "
                "bisection with X = oracle_only count; X=0 -> 0.0; X=384 -> "
                "0.05**(1/384); pass iff all three"
            ),
            "shape_required": FROZEN_PAIRS,
        },
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
        "attempts_allowed": 1,
        "attempts_consumed_before": 0,
        "attempts_consumed_by_this_run": 1,
        "retries": 0,
        "budget": {
            "total_wall_s": float(total_wall_s),
            "external_timeout_s": EXTERNAL_TIMEOUT_S,
            "ulimit_virtual_kib": ULIMIT_VIRTUAL_KIB,
            "rss_bytes_max": RSS_LIMIT_BYTES,
        },
        "refused_run_seeds": sorted(int(v) for v in BANNED_SEEDS),
        "frozen_command": FROZEN_COMMAND,
        "claim_scope": CLAIM_SCOPE,
    }


def _build_summary(
    *,
    results,
    planned: int,
    seeds,
    n: int,
    epsilon1: float,
    profile: str,
    k1: int,
    k2: int,
    p2_maxdiff: float,
    gates: dict,
    cells: dict,
    provenance_counts: dict,
    incremental,
    incremental_by_arm,
    recount,
    mismatches,
    wall_s: float,
    resource_stop_fired: bool,
) -> dict:
    op = [r.operational for r in results]
    orc = [r.oracle for r in results]
    operational_exact = sum(1 for a in op if a.exact)
    oracle_exact = sum(1 for b in orc if b.exact)
    x_oracle_only = int(cells["oracle_only"])
    lower_bound = exact_lower_bound(x_oracle_only, FROZEN_PAIRS)
    discriminator = {
        "oracle_exact_min_met": bool(oracle_exact >= ORACLE_EXACT_MIN),
        "operational_only_zero": bool(cells["operational_only"] == 0),
        "lower_bound_above_0p30": bool(lower_bound > LOWER_BOUND_MIN),
    }
    discriminator["passed"] = bool(all(discriminator.values()))
    integrity_all_pass = bool(all(gates.values()))
    failing = [name for name in INTEGRITY_GATE_ORDER if not gates[name]]
    if not integrity_all_pass:
        outcome_label = "BLOCKED"
    elif discriminator["passed"] and planned == FROZEN_PAIRS:
        outcome_label = "HARD_L1_CONDITIONING_PENALTY_CANDIDATE"
    else:
        outcome_label = "HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED"
    denominator = max(planned, 1)
    return {
        "analysis": PROTOCOL_NAME,
        "mode": MODE,
        "seeds": [int(s) for s in seeds],
        "toeplitz_masters": [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in seeds],
        "planned_pairs": int(planned),
        "shape_is_frozen_384": bool(planned == FROZEN_PAIRS),
        "n": int(n),
        "q": Q,
        "epsilon1": float(epsilon1),
        "profile": profile,
        "k1": int(k1),
        "k2": int(k2),
        "p2_maxdiff": float(p2_maxdiff),
        "cells": dict(cells),
        "marginals": {
            "operational_exact": int(operational_exact),
            "oracle_exact": int(oracle_exact),
            "operational_exact_rate": round(operational_exact / denominator, 9),
            "oracle_exact_rate": round(oracle_exact / denominator, 9),
            "paired_exact_gap": int(oracle_exact - operational_exact),
            "operational_outcomes": {
                name: sum(1 for a in op if a.outcome == name) for name in tl.OUTCOMES
            },
            "oracle_outcomes": {
                name: sum(1 for b in orc if b.outcome == name) for name in tl.OUTCOMES
            },
        },
        "X": x_oracle_only,
        "lower_bound": lower_bound,
        "lower_bound_definition": (
            "root of sum_{j=X}^{384} C(384,j) L^j (1-L)^(384-j) = 0.05 by monotone "
            "bisection; X=0 -> 0.0; X=384 -> 0.05**(1/384)"
        ),
        "integrity": {name: bool(gates[name]) for name in INTEGRITY_GATE_ORDER},
        "integrity_all_pass": integrity_all_pass,
        "failing_integrity_gates": failing,
        "provenance_counts": dict(provenance_counts),
        "discriminator": discriminator,
        "outcome_label": outcome_label,
        "accounting": {
            "l1_disclosure_bits_per_arm": DISCLOSED_BITS_PER_COORDINATE * int(k1),
            "l2_disclosure_bits_per_arm": DISCLOSED_BITS_PER_COORDINATE * int(k2),
            "tag_bits": TAG_BITS,
            "fully_invoked_arm_bits": DISCLOSED_BITS_PER_COORDINATE * int(k1 + k2) + TAG_BITS,
            "key_dependent_bits_total": int(incremental["key_dependent_bits"]),
            "public_control_bits_total": int(incremental["public_control_bits"]),
            "public_control_bits_per_tag": tl.seed_bits_for(n),
            "tag_invocations": int(incremental["tag_invocations"]),
        },
        "transcript": {
            "event_count": int(sum(recount["event_types"].values())),
            "event_types": dict(recount["event_types"]),
            "mismatch_count": int(len(mismatches)),
            "mismatches": list(mismatches),
            "incremental": dict(incremental),
            "incremental_by_arm": {arm: dict(incremental_by_arm[arm]) for arm in ARMS},
            "recount": {
                "key_dependent_bits": int(recount["key_dependent_bits"]),
                "public_control_bits": int(recount["public_control_bits"]),
                "tag_invocations": int(recount["tag_invocations"]),
                "event_types": dict(recount["event_types"]),
                "by_arm": {arm: dict(recount["by_arm"][arm]) for arm in ARMS},
            },
        },
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_peak": _peak_rss_bytes(),
        "resource_stop_fired": bool(resource_stop_fired),
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
        "attempts_allowed": 1,
        "attempts_consumed_before": 0,
        "attempts_consumed_by_this_run": 1,
        "retries": 0,
        "claim_scope": CLAIM_SCOPE,
    }


def _render_report(summary: dict) -> str:
    cells = summary["cells"]
    lines = [
        "# NB-Polar Phase 4-P5 hard-L1 conditioning penalty gate — synthetic statistic",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- seeds: {summary['seeds']}; masters: {summary['toeplitz_masters']}; "
        f"planned pairs: {summary['planned_pairs']}",
        f"- point: q={summary['q']}, N={summary['n']}, epsilon1={summary['epsilon1']}, "
        f"profile={summary['profile']}, k1={summary['k1']}, k2={summary['k2']}",
        f"- p2_maxdiff: {summary['p2_maxdiff']} (floor {P2_MAXDIFF_FLOOR})",
        f"- wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes",
        "",
        "## Paired four-cell table",
        "",
        "| cell | count |",
        "|---|---|",
        f"| both_exact | {cells['both_exact']} |",
        f"| oracle_only | {cells['oracle_only']} |",
        f"| operational_only | {cells['operational_only']} |",
        f"| neither | {cells['neither']} |",
        "",
        f"- X (oracle-only event count): {summary['X']}; one-sided 95% exact lower "
        f"bound L: {summary['lower_bound']}",
        "",
        "## Integrity gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in summary["integrity"].items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        "## Discriminator",
        "",
    ]
    for name, value in summary["discriminator"].items():
        lines.append(f"- {name}: {value}")
    lines += [
        "",
        f"- outcome label: `{summary['outcome_label']}`",
        "",
        f"**Scope:** {summary['claim_scope']}.",
        "",
    ]
    return "\n".join(lines)


def run_penalty_gate(
    *,
    n,
    epsilon1,
    profile,
    k1,
    k2,
    seeds,
    blocks_per_seed,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
) -> PenaltyGateRun:
    """Execute the frozen-point paired penalty gate and write exactly five files.

    Refuses an existing output root before any decoder call, validates the
    frozen point and the refused seeds, computes ``p2_maxdiff`` on the injected
    table and refuses to decode when it is below the floor, then runs one
    ``two_layer.run_two_layer_block`` call per block.  The single attempt is
    consumed at the first gate L1 SC call (stream 0, block 0).
    """
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    n = _as_int(n, "n", minimum=1)
    if n != FROZEN_N:
        raise ValueError(f"frozen point requires n={FROZEN_N}, got {n}")
    eps1 = _checked_epsilon(epsilon1, "epsilon1")
    if eps1 != FROZEN_EPSILON1:
        raise ValueError(f"frozen point requires epsilon1={FROZEN_EPSILON1}, got {eps1}")
    if profile not in PROFILE_FORMULAS:
        raise ValueError(f"unknown dependent-L2 profile {profile!r}")
    if profile != FROZEN_PROFILE:
        raise ValueError(f"frozen point requires profile {FROZEN_PROFILE!r}, got {profile!r}")
    k1 = _as_int(k1, "k1", minimum=0)
    k2 = _as_int(k2, "k2", minimum=0)
    if (k1, k2) != (FROZEN_K1, FROZEN_K2):
        raise ValueError(
            f"frozen point requires k1={FROZEN_K1}, k2={FROZEN_K2}, got k1={k1}, k2={k2}"
        )
    seed_list = [_as_int(s, "seed", minimum=0) for s in seeds]
    if not seed_list:
        raise ValueError("at least one stream seed is required")
    if len(set(seed_list)) != len(seed_list):
        raise ValueError("stream seeds must be distinct")
    for seed in seed_list:
        if seed in BANNED_SEEDS:
            raise ValueError(f"seed {seed} is banned (consumed by Phase 1-6)")
    blocks = _as_int(blocks_per_seed, "blocks_per_seed", minimum=1)
    total_cap = float(total_wall_s)
    if not np.isfinite(total_cap) or total_cap <= 0:
        raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")
    planned = len(seed_list) * blocks

    table = build_dependent_joint_table(profile=profile, epsilon1=eps1)
    table_deviation = float(np.abs(table.sum(axis=0) - 1.0).max())
    p1_table, p2_table = tl.layer_metric_tables(table)
    p2_maxdiff = require_p2_maxdiff(p2_cross_u1_maxdiff(p2_table))
    d1, d2 = tl.frozen_disclosure_sets(
        n=n, k1=k1, k2=k2, epsilon1=eps1, epsilon2=PROFILE_MEAN_EPSILON2
    )
    field = make_gf32()

    results: list = []
    records: list = []
    events: list = []
    incremental = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    incremental_by_arm = {
        arm: {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
        for arm in ARMS
    }
    resource_stop_fired = False
    start = time.perf_counter()

    for stream_seed in seed_list:
        master = stream_seed + PUBLIC_TAG_MASTER_OFFSET
        rng = np.random.default_rng(stream_seed)
        for block_index in range(blocks):
            if time.perf_counter() - start > total_cap:
                resource_stop_fired = True
                for aborted in range(block_index, blocks):
                    results.append(
                        tl.TwoLayerBlockResult(
                            block_index=aborted,
                            operational=tl._abort_arm("operational"),
                            oracle=tl._abort_arm("oracle"),
                            oracle_candidate_divergence=None,
                            block_wall_s=0.0,
                        )
                    )
                break
            sample = sample_dependent_block(
                rng, n=n, epsilon1=eps1, profile=profile
            )
            result = tl.run_two_layer_block(
                block_index,
                sample.high,
                sample.low,
                sample.bob,
                field=field,
                p1_table=p1_table,
                p2_table=p2_table,
                d1=d1,
                d2=d2,
                n=n,
                k1=k1,
                k2=k2,
                toeplitz_master=master,
            )
            results.append(result)
            records.append(_block_record(stream_seed, result))
            events.extend(tl.block_events(result, k1=k1, k2=k2, n=n))
            for arm_name, arm in (
                ("operational", result.operational),
                ("oracle", result.oracle),
            ):
                if arm.outcome == "resource_abort":
                    continue
                incremental["key_dependent_bits"] += int(arm.key_dependent_bits)
                incremental["public_control_bits"] += int(arm.public_control_bits)
                incremental["tag_invocations"] += int(arm.tag_invoked)
                incremental_by_arm[arm_name]["key_dependent_bits"] += int(arm.key_dependent_bits)
                incremental_by_arm[arm_name]["public_control_bits"] += int(arm.public_control_bits)
                incremental_by_arm[arm_name]["tag_invocations"] += int(arm.tag_invoked)
        if resource_stop_fired:
            break

    recount = _literal_recount(events)
    mismatches = _transcript_mismatches(incremental, incremental_by_arm, recount)
    gates, cells, provenance_counts = _integrity_gates(
        planned=planned,
        results=results,
        p2_maxdiff=p2_maxdiff,
        incremental=incremental,
        incremental_by_arm=incremental_by_arm,
        recount=recount,
        mismatches=mismatches,
        k1=k1,
        k2=k2,
        n=n,
    )
    wall_s = time.perf_counter() - start
    summary = _build_summary(
        results=results,
        planned=planned,
        seeds=seed_list,
        n=n,
        epsilon1=eps1,
        profile=profile,
        k1=k1,
        k2=k2,
        p2_maxdiff=p2_maxdiff,
        gates=gates,
        cells=cells,
        provenance_counts=provenance_counts,
        incremental=incremental,
        incremental_by_arm=incremental_by_arm,
        recount=recount,
        mismatches=mismatches,
        wall_s=wall_s,
        resource_stop_fired=resource_stop_fired,
    )
    plan = _build_plan(
        out_path=out_path,
        n=n,
        epsilon1=eps1,
        profile=profile,
        k1=k1,
        k2=k2,
        seeds=seed_list,
        blocks_per_seed=blocks,
        d1=d1,
        d2=d2,
        table_deviation=table_deviation,
        p2_maxdiff=p2_maxdiff,
        total_wall_s=total_cap,
    )
    transcript = {
        "event_count": len(events),
        "event_types": dict(recount["event_types"]),
        "incremental": dict(incremental),
        "incremental_by_arm": {arm: dict(incremental_by_arm[arm]) for arm in ARMS},
        "recount": {
            "key_dependent_bits": int(recount["key_dependent_bits"]),
            "public_control_bits": int(recount["public_control_bits"]),
            "tag_invocations": int(recount["tag_invocations"]),
            "event_types": dict(recount["event_types"]),
            "by_arm": {arm: dict(recount["by_arm"][arm]) for arm in ARMS},
        },
        "mismatch_count": len(mismatches),
        "mismatches": list(mismatches),
        "public_control_bits_per_tag": tl.seed_bits_for(n),
        "fully_invoked_arm_bits": DISCLOSED_BITS_PER_COORDINATE * (k1 + k2) + TAG_BITS,
        "per_pair_disclosure_bits_per_fully_invoked_arm": (
            DISCLOSED_BITS_PER_COORDINATE * (k1 + k2) + TAG_BITS
        ),
    }

    out_path.mkdir(parents=True)
    _write_json(out_path / "frozen_plan.json", plan)
    _write_json(
        out_path / "per_block_paired_outcomes.json",
        {
            "planned_pairs": planned,
            "seeds": [int(s) for s in seed_list],
            "n_blocks": len(records),
            "blocks": records,
        },
    )
    _write_json(out_path / "transcript_accounting.json", transcript)
    _write_json(out_path / "aggregate_summary.json", summary)
    (out_path / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return PenaltyGateRun(
        results=results,
        records=records,
        events=events,
        plan=plan,
        transcript=transcript,
        summary=summary,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-penalty-gate",
        description="NB-Polar Phase 4-P5 hard-L1 conditioning penalty synthetic dev gate",
    )
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--epsilon1", required=True, type=float)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--k1", required=True, type=int)
    parser.add_argument("--k2", required=True, type=int)
    parser.add_argument("--seeds", required=True, type=int, nargs="+")
    parser.add_argument("--blocks-per-seed", required=True, type=int, dest="blocks_per_seed")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_penalty_gate(
            n=args.n,
            epsilon1=args.epsilon1,
            profile=args.profile,
            k1=args.k1,
            k2=args.k2,
            seeds=args.seeds,
            blocks_per_seed=args.blocks_per_seed,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p5 penalty gate refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "planned_pairs": summary["planned_pairs"],
                "cells": summary["cells"],
                "X": summary["X"],
                "lower_bound": summary["lower_bound"],
                "integrity_all_pass": summary["integrity_all_pass"],
                "outcome_label": summary["outcome_label"],
                "out_root": args.out_dir,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
