"""NB-Polar Phase 4-P6 adaptive hard-L1 disclosure gate (synthetic only).

Frozen point (packet ``NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1``): GF32 polynomial
basis, primitive polynomial 37, alpha 2, natural order, ``N=256``;
``epsilon1=0.05``; strong dependent-L2 profile
``epsilon2(u1) = 0.02 + 0.36*u1/31``; analytic worst-first nested L1 prefixes
``K1 in [45, 60, 72, 112]`` with ``D1(K1) = sorted(analytic_order(0.05,
256)[:K1])``; fixed L2 prefix ``K2=140``; five fresh streams
2026091550..2026091554 with 128 common blocks each (640 paired blocks); public
Toeplitz master ``stream + 10000``, domain-separated per arm/block/level.

The gate runs two arms on identical sampled blocks and disclosures:

- **static arm** (``K1=112``): one fresh L1 SC call on the P1 prior metric,
  one fresh candidate-conditioned L2 SC call, one 64-bit Toeplitz tag; a fully
  invoked arm costs ``5*(112+140)+64 = 1324`` key-dependent bits;
- **adaptive arm**: for each one-based stage ``j`` with ``K1_j``, restart the
  L1 SC from the ORIGINAL P1 metric with the cumulative nested prefix, restart
  the candidate-conditioned L2 SC from the ORIGINAL P2 table gathered by the
  current hard L1 candidate, and verify the full 10-bit label with one 64-bit
  tag under that stage's level domain.  A tag match accepts and stops (exact
  iff the label equals truth; tag pass and not exact is ``undetected``, never
  merged with exact).  A mismatch before the terminal ``K1=112`` emits one
  public one-bit feedback and advances.  A nonterminal
  ``ImpossibleDisclosedValueError`` produces no candidate and no tag, emits one
  feedback bit and advances; at the terminal stage it is ``decode_failed``.
  Every other exception fails closed.  Decoder state, metrics, partial sums,
  candidate labels and tag seeds are never reused between stages.

Accounting per arm/block at the one-based termination stage ``j`` with
``K1=K_j``: ``5*(K_j+140) + 64*tag_invocations`` realized from executed
disclosures (cumulative L1 prefix, the once-per-arm/block L2 disclosure when L2
was invoked, one 64-bit tag per invocation); public seed bits
``2623*tag_invocations``; one public feedback bit per invocation; public
control = seed + feedback.  A decode rejection creates no tag.  An independent
literal transcript recount must equal the incremental totals with zero
mismatch; the verification union bound is ``min(1, tags * 2**-64)``.  Every
transcript event carries the public scalar ``stream_seed``; because block
indices repeat across streams, the D2-once gate keys on the compound
``(stream_seed, block_index, arm)`` identity.

Outcome labels: ``ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE`` iff every integrity
and scientific gate passes at the frozen 640-pair shape;
``ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED`` iff integrity passes but any
scientific gate fails; otherwise ``BLOCKED`` with the failing gate names.

Reuses the accepted P4/P5 modules unchanged: the strong-profile dependent
table/sampler (``penalty_gate``), the nested-schedule builder (``incremental``),
the two-layer primitives, provenance, SC failure taxonomy, Toeplitz tag and the
union bound (``two_layer``, ``shared``).  Synthetic injected tables only: no
stored data product, no real frame, no N>256, no scalable or list decoder, no
soft-APP path, no import-time I/O, no global RNG.  The only output is the
explicit development CLI and its five compact scalar-only files; symbols,
labels, disclosed values, decoded keys and raw seed bits are never persisted.
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

from ..shared import canonical_event, toeplitz_tag, verification_union_bound
from . import incremental as inc
from . import penalty_gate as pg
from . import two_layer as tl
from .algebra import make_gf32
from .prior import Provenance, build_p1_metrics, gather_p2_metrics, probs_to_symbol_metric
from .sc import ImpossibleDisclosedValueError

try:  # POSIX (the frozen command runs under WSL); Windows native has no resource module.
    import resource
except ImportError:  # pragma: no cover - exercised only on Windows native
    resource = None

PROTOCOL_NAME = "nbpolar-p4p6-adaptive-hard-l1-gate"
MODE = "paired-adaptive-hard-l1-dev-gate"
Q = 32
ALPHA = 2
LABEL_SCALE = 32
TAG_BITS = 64
DISCLOSED_BITS_PER_COORDINATE = 5
FEEDBACK_CONTROL_BITS = 1

FROZEN_N = 256
FROZEN_EPSILON1 = 0.05
FROZEN_PROFILE = "strong"
PROFILE_MEAN_EPSILON2 = 0.20
FROZEN_K1_LEVELS = (45, 60, 72, 112)
FROZEN_K2 = 140
STATIC_K1 = 112
FROZEN_SEEDS = (2026091550, 2026091551, 2026091552, 2026091553, 2026091554)
FROZEN_BLOCKS_PER_SEED = 128
FROZEN_PAIRS = 640
PUBLIC_TAG_MASTER_OFFSET = 10000
STATIC_EXACT_MIN = 620
STATIC_FULLY_INVOKED_BITS = DISCLOSED_BITS_PER_COORDINATE * (STATIC_K1 + FROZEN_K2) + TAG_BITS
RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 3600.0
EXTERNAL_TIMEOUT_S = 3600
ULIMIT_VIRTUAL_KIB = 2097152

# Planning-only surrogate provenance: H(A|B) = 2.134043324031305 bits from the
# accepted X04/X05 dependent-table chain rule; 256*H = 546.3150909520141.
H_A_GIVEN_B_REFERENCE_BITS = 2.134043324031305
PLANNING_DENOMINATOR_BITS = 546.3150909520141

# The Phase 1-6 consumed streams plus every consumed X-probe stream.  The P6
# frozen streams 2026091550..2026091554 are accepted and absent from this set.
BANNED_SEEDS = (
    frozenset(range(2026091200, 2026091214))
    | frozenset(range(2026091314, 2026091322))
    | frozenset({2026091330, 2026091340, 2026091341, 2026091350, 2026091351})
    | frozenset({2026091360, 2026091361})
    | frozenset(range(2026091400, 2026091405))
    | frozenset(range(2026091410, 2026091415))
    | frozenset(range(2026091420, 2026091425))
    | frozenset(range(2026091430, 2026091435))
    | frozenset(range(2026091450, 2026091453))
    | frozenset(range(2026091470, 2026091473))
    | frozenset(range(2026091490, 2026091495))
    | frozenset(range(2026091510, 2026091515))
)

ARMS = ("static", "adaptive")
CELLS = ("both_exact", "adaptive_only", "static_only", "neither")
TAG_OUTCOMES = ("exact", "undetected", "verify_failed")

INTEGRITY_GATE_ORDER = (
    "pairing_coverage_complete",
    "stream_block_identity_exact",
    "result_buckets_disjoint_exhaustive",
    "d1_exactly_nested_and_d2_disclosed_once",
    "provenance_and_truth_isolation_complete",
    "undetected_zero",
    "nonfinite_zero",
    "resource_abort_zero",
    "transcript_recount_mismatch_zero",
    "tag_feedback_public_control_accounting_and_union_bound_exact",
    "wall_rss_within_frozen_limits",
    "attempt_seed_accounting_exact",
)
SCIENTIFIC_GATE_ORDER = (
    "static_exact_at_least_620_of_640",
    "adaptive_exact_equals_static_exact",
    "paired_adaptive_only_zero_and_static_only_zero",
    "leakage_100_adaptive_le_85_static",
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "per_block_paired_outcomes.json",
    "transcript_accounting.json",
    "aggregate_summary.json",
    "report.md",
)
ATTEMPT_CONSUMPTION_POINT = "first scientific SC call (stream 2026091550, block 0, static L1)"
ATTEMPT_ACCOUNTING = {
    "attempts_allowed": 1,
    "attempts_consumed_before": 0,
    "attempts_consumed_by_this_run": 1,
    "retries": 0,
}
FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "ulimit -v 2097152\n"
    "timeout 3600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.adaptive_l1 "
    "--n 256 --epsilon1 0.05 --profile strong --k1-levels 45 60 72 112 "
    "--k2 140 --seeds 2026091550 2026091551 2026091552 2026091553 2026091554 "
    "--blocks-per-seed 128 --out-dir .workbuddy/queue/"
    "NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate"
)
CLAIM_SCOPE = (
    "synthetic N=256 development evidence only; this is not real-channel FER, "
    "reconciliation efficiency, key rate, qualification or promotion; "
    "undetected frames are never merged with exact frames and planning-only f "
    "is not real-channel efficiency"
)
SEED_DERIVATION = (
    "MSB-first unpack of SHA-256('nbpolar-p4p6-toeplitz-seed:<master>:<arm>:"
    "<block_index>:<level>:<counter>') concatenated over counter=0,1,...; "
    "truncated to 10*n + 63 bits; public control, never persisted raw; "
    "level = one-based invocation index within the arm"
)

__all__ = [
    "PROTOCOL_NAME",
    "MODE",
    "Q",
    "ALPHA",
    "TAG_BITS",
    "DISCLOSED_BITS_PER_COORDINATE",
    "FEEDBACK_CONTROL_BITS",
    "FROZEN_N",
    "FROZEN_EPSILON1",
    "FROZEN_PROFILE",
    "PROFILE_MEAN_EPSILON2",
    "FROZEN_K1_LEVELS",
    "FROZEN_K2",
    "STATIC_K1",
    "FROZEN_SEEDS",
    "FROZEN_BLOCKS_PER_SEED",
    "FROZEN_PAIRS",
    "PUBLIC_TAG_MASTER_OFFSET",
    "STATIC_EXACT_MIN",
    "STATIC_FULLY_INVOKED_BITS",
    "H_A_GIVEN_B_REFERENCE_BITS",
    "PLANNING_DENOMINATOR_BITS",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S",
    "ULIMIT_VIRTUAL_KIB",
    "BANNED_SEEDS",
    "ARMS",
    "CELLS",
    "TAG_OUTCOMES",
    "INTEGRITY_GATE_ORDER",
    "SCIENTIFIC_GATE_ORDER",
    "OUTPUT_FILES",
    "ATTEMPT_CONSUMPTION_POINT",
    "ATTEMPT_ACCOUNTING",
    "FROZEN_COMMAND",
    "CLAIM_SCOPE",
    "SEED_DERIVATION",
    "block_toeplitz_seed_bits",
    "classify_cell",
    "h_a_given_b_from_table",
    "AdaptiveArmResult",
    "PairedBlockResult",
    "ResultRow",
    "AdaptiveGateRun",
    "run_static_arm",
    "run_adaptive_arm",
    "run_paired_block",
    "paired_block_events",
    "recount_transcript",
    "run_adaptive_gate",
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


def block_toeplitz_seed_bits(
    arm: str,
    block_index: int,
    level: int,
    *,
    master: int,
    bit_length: int,
) -> np.ndarray:
    """Deterministic public per-arm/per-block/per-level Toeplitz seed.

    ``level`` is the one-based invocation index within the arm (static: 1;
    adaptive: the one-based stage).  Seed contents are public control and are
    never persisted.
    """
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")
    index = _as_int(block_index, "block_index", minimum=0)
    lvl = _as_int(level, "level", minimum=1)
    master_seed = _as_int(master, "master", minimum=0)
    length = _as_int(bit_length, "bit_length", minimum=1)
    prefix = f"nbpolar-p4p6-toeplitz-seed:{master_seed}:{arm}:{index}:{lvl}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < length:
        buf.extend(hashlib.sha256(f"{prefix}:{counter}".encode("ascii")).digest())
        counter += 1
    bits = np.unpackbits(np.frombuffer(bytes(buf), dtype=np.uint8), bitorder="big")
    return bits[:length].astype(np.uint8)


def classify_cell(static_exact: bool, adaptive_exact: bool) -> str:
    """Paired four-cell label; the four cells are disjoint and exhaustive."""
    if static_exact and adaptive_exact:
        return "both_exact"
    if adaptive_exact:
        return "adaptive_only"
    if static_exact:
        return "static_only"
    return "neither"


def h_a_given_b_from_table(table) -> dict:
    """Planning-only ``H(A|B)`` of the injected table (chain rule + cross-check).

    ``p(a,b) = table[a,b]/(32*32)`` (uniform A); entropies in bits.  The
    chain-rule value is cross-checked against the direct conditional entropy.
    """
    joint = np.asarray(table, dtype=np.float64) / float(Q * Q)
    p_b = joint.sum(axis=0)
    pos = joint > 0
    h_ab = float(-np.sum(joint[pos] * np.log2(joint[pos])))
    pos_b = p_b > 0
    h_b = float(-np.sum(p_b[pos_b] * np.log2(p_b[pos_b])))
    chain = h_ab - h_b
    with np.errstate(invalid="ignore", divide="ignore"):
        p_a_given_b = joint / p_b[None, :]
    pos_c = p_a_given_b > 0
    row_h = -np.sum(
        np.where(pos_c, p_a_given_b * np.log2(np.where(pos_c, p_a_given_b, 1.0)), 0.0),
        axis=0,
    )
    direct = float(np.sum(p_b * row_h))
    return {
        "h_a_given_b_bits": chain,
        "chain_rule_bits": chain,
        "direct_conditional_bits": direct,
        "chain_vs_direct_abs_diff": abs(chain - direct),
        "reference_bits": H_A_GIVEN_B_REFERENCE_BITS,
        "reference_abs_diff": abs(chain - H_A_GIVEN_B_REFERENCE_BITS),
        "derivation": (
            "H(A|B) = H(A,B) - H(B) from the injected [A,B] table; p(a,b) = "
            "table[a,b]/1024 (A uniform), p(b) = column sums /1024; log2 in "
            "bits; cross-checked against sum_b p(b) H(A|B=b)"
        ),
    }


@dataclass(frozen=True, eq=False)
class AdaptiveArmResult:
    """One attempted static or adaptive arm block.

    Symbol/label arrays, the stage tuples and the protected-array set are in
    memory only and never persisted; only the scalar accounting record is
    written.
    """

    block_index: int
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
    l2_decode_failed: bool
    tag_invoked: bool
    levels_invoked: int
    tag_invocations: int
    feedback_invocations: int
    termination_stage: int
    termination_k1: int
    key_dependent_bits: int
    public_seed_bits: int
    feedback_bits: int
    public_control_bits: int
    nonfinite: bool
    truth_leak_violation: bool
    l1_error_type: str | None
    l2_error_type: str | None
    wall_s: float
    tagged_stages: tuple = ()
    feedback_stages: tuple = ()
    rejected_stages: tuple = ()
    l2_stage: int | None = None
    high_hat: np.ndarray | None = None
    low_hat: np.ndarray | None = None
    label_hat: np.ndarray | None = None
    protected_arrays: tuple = ()


@dataclass(frozen=True, eq=False)
class PairedBlockResult:
    """One paired static + adaptive block on identical arrays and disclosures."""

    block_index: int
    static: AdaptiveArmResult
    adaptive: AdaptiveArmResult
    block_wall_s: float
    labels_true: np.ndarray | None = None
    p1_logp: np.ndarray | None = None


@dataclass(frozen=True, eq=False)
class ResultRow:
    """One persisted per-block row: stream identity plus both arm results."""

    stream_seed: int
    block_index: int
    static: AdaptiveArmResult
    adaptive: AdaptiveArmResult


def _abort_arm(block_index: int, arm: str) -> AdaptiveArmResult:
    return AdaptiveArmResult(
        block_index=int(block_index),
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
        l2_decode_failed=False,
        tag_invoked=False,
        levels_invoked=0,
        tag_invocations=0,
        feedback_invocations=0,
        termination_stage=0,
        termination_k1=0,
        key_dependent_bits=0,
        public_seed_bits=0,
        feedback_bits=0,
        public_control_bits=0,
        nonfinite=False,
        truth_leak_violation=False,
        l1_error_type=None,
        l2_error_type=None,
        wall_s=0.0,
    )


def _outcome_from_tag(tag_pass: bool, label_match: bool) -> str:
    if not tag_pass:
        return "verify_failed"
    return "exact" if label_match else "undetected"


def run_static_arm(
    block_index,
    *,
    field,
    p1_logp,
    p2_table,
    d1,
    d2,
    bob,
    u1_true,
    u2_true,
    labels_true,
    labels_true_bits,
    n,
    master,
    tag_fn=None,
) -> AdaptiveArmResult:
    """One fresh static endpoint arm at the frozen ``K1=112``/``K2=140``.

    The L1 metric is used as given (P1 prior, ``PRIOR_ONLY``); the L2 metric is
    gathered freshly from Bob and the hard L1 candidate
    (``CANDIDATE_CONDITIONED``); exactly one final tag is invoked when a
    candidate label exists.  ``tag_fn`` is a documented test seam.
    """
    if tag_fn is None:
        tag_fn = toeplitz_tag
    start = time.perf_counter()
    d1 = np.asarray(d1, dtype=np.int64)
    d2 = np.asarray(d2, dtype=np.int64)
    u1_disclosed = np.array(u1_true[d1], copy=True)
    u2_disclosed = np.array(u2_true[d2], copy=True)
    protected = [p1_logp, u2_disclosed]

    l1_failed = False
    l2_failed = False
    l1_error = None
    l2_error = None
    nonfinite = False
    candidate = None
    low_hat = None
    label_hat = None
    label_match = False
    tag_pass = False
    tag_invoked = False
    l2_invoked = False

    try:
        sc1 = tl._decode_layer(p1_logp, field=field, positions=d1, disclosed=u1_disclosed)
        candidate = np.array(sc1.x_hat, copy=True)
        protected.append(candidate)
    except Exception as exc:  # SC failure contract: decode_failed, no tag
        l1_failed = True
        l1_error = type(exc).__name__
        nonfinite = tl._nonfinite_flag(exc)

    if candidate is not None:
        l2_invoked = True
        try:
            p2_probs = gather_p2_metrics(bob[None, :], candidate[None, :], p2_table)[0]
            p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
            protected.extend([p2_probs, p2_metric.logp])
            sc2 = tl._decode_layer(
                p2_metric.logp, field=field, positions=d2, disclosed=u2_disclosed
            )
            low_hat = np.array(sc2.x_hat, copy=True)
            label_hat = (low_hat + LABEL_SCALE * candidate).astype(np.int64)
            protected.extend([low_hat, label_hat])
            label_match = bool(np.array_equal(label_hat, labels_true))
            seed = block_toeplitz_seed_bits(
                "static", block_index, 1, master=master, bit_length=tl.seed_bits_for(n)
            )
            tag_true = tag_fn(labels_true_bits, seed, TAG_BITS)
            tag_hat = tag_fn(tl.labels_to_bits(label_hat), seed, TAG_BITS)
            tag_pass = tag_true == tag_hat
            tag_invoked = True
        except Exception as exc:  # SC failure contract: decode_failed, no tag
            l2_failed = True
            l2_error = type(exc).__name__
            nonfinite = nonfinite or tl._nonfinite_flag(exc)

    if l1_failed or l2_failed:
        outcome = "decode_failed"
    else:
        outcome = _outcome_from_tag(tag_pass, label_match)
    key_dependent_bits = (
        DISCLOSED_BITS_PER_COORDINATE * int(d1.shape[0])
        + (DISCLOSED_BITS_PER_COORDINATE * int(d2.shape[0]) if l2_invoked else 0)
        + (TAG_BITS if tag_invoked else 0)
    )
    public_seed_bits = tl.seed_bits_for(n) if tag_invoked else 0
    return AdaptiveArmResult(
        block_index=int(block_index),
        arm="static",
        outcome=outcome,
        exact=bool(outcome == "exact"),
        label_match=label_match,
        tag_pass=tag_pass,
        l1_provenance=Provenance.PRIOR_ONLY.value,
        l2_provenance=(
            Provenance.CANDIDATE_CONDITIONED.value if l2_invoked else None
        ),
        l1_executed=bool(not l1_failed),
        l1_decode_failed=bool(l1_failed),
        l2_invoked=bool(l2_invoked),
        l2_decode_failed=bool(l2_failed),
        tag_invoked=bool(tag_invoked),
        levels_invoked=1,
        tag_invocations=1 if tag_invoked else 0,
        feedback_invocations=0,
        termination_stage=1,
        termination_k1=int(d1.shape[0]),
        key_dependent_bits=int(key_dependent_bits),
        public_seed_bits=int(public_seed_bits),
        feedback_bits=0,
        public_control_bits=int(public_seed_bits),
        nonfinite=bool(nonfinite),
        truth_leak_violation=False,  # updated by the paired sentinel
        l1_error_type=l1_error,
        l2_error_type=l2_error,
        wall_s=time.perf_counter() - start,
        tagged_stages=(0,) if tag_invoked else (),
        l2_stage=0 if l2_invoked else None,
        high_hat=candidate,
        low_hat=low_hat,
        label_hat=label_hat,
        protected_arrays=tuple(protected),
    )


def run_adaptive_arm(
    block_index,
    *,
    field,
    p1_logp,
    p2_table,
    d1_sets,
    d2,
    bob,
    u1_true,
    u2_true,
    labels_true,
    labels_true_bits,
    levels,
    n,
    master,
    tag_fn=None,
) -> AdaptiveArmResult:
    """One adaptive hard-L1 ladder block (nested restart, tag/feedback rules).

    Every stage restarts the L1 SC from the ORIGINAL ``p1_logp`` with the
    cumulative prefix, then restarts the candidate-conditioned L2 SC on a
    freshly gathered metric.  No decoder object, metric, partial sum,
    candidate label or tag seed crosses stages.
    """
    if tag_fn is None:
        tag_fn = toeplitz_tag
    start = time.perf_counter()
    levels = tuple(int(v) for v in levels)
    d1_sets = tuple(np.asarray(d, dtype=np.int64) for d in d1_sets)
    d2 = np.asarray(d2, dtype=np.int64)
    u2_disclosed = np.array(u2_true[d2], copy=True)
    protected = [p1_logp, u2_disclosed]

    levels_invoked = 0
    tag_invocations = 0
    feedback_invocations = 0
    tagged_stages: list = []
    feedback_stages: list = []
    rejected_stages: list = []
    l1_failed = False
    l2_failed = False
    l1_error = None
    l2_error = None
    nonfinite = False
    l2_invoked = False
    l2_stage = None
    candidate = None
    low_hat = None
    label_hat = None
    label_match = False
    tag_pass = False
    outcome = None
    termination_stage = 0

    for stage in range(len(levels)):
        levels_invoked += 1
        u1_disclosed = np.array(u1_true[d1_sets[stage]], copy=True)
        try:
            sc1 = tl._decode_layer(
                p1_logp, field=field, positions=d1_sets[stage], disclosed=u1_disclosed
            )
            candidate = np.array(sc1.x_hat, copy=True)
            protected.append(candidate)
        except ImpossibleDisclosedValueError as exc:
            # Nonterminal rejection: no candidate, no tag, one public feedback
            # bit, then advance to the next cumulative D1 increment.
            if stage + 1 < len(levels):
                rejected_stages.append(stage)
                feedback_stages.append(stage)
                feedback_invocations += 1
                continue
            l1_failed = True
            l1_error = type(exc).__name__
            termination_stage = stage + 1
            break
        except Exception as exc:  # all other exceptions fail closed
            l1_failed = True
            l1_error = type(exc).__name__
            nonfinite = tl._nonfinite_flag(exc)
            termination_stage = stage + 1
            break

        l2_invoked = True
        if l2_stage is None:
            l2_stage = stage
        try:
            p2_probs = gather_p2_metrics(bob[None, :], candidate[None, :], p2_table)[0]
            p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
            protected.extend([p2_probs, p2_metric.logp])
            sc2 = tl._decode_layer(
                p2_metric.logp, field=field, positions=d2, disclosed=u2_disclosed
            )
            low_hat = np.array(sc2.x_hat, copy=True)
            label_hat = (low_hat + LABEL_SCALE * candidate).astype(np.int64)
            protected.extend([low_hat, label_hat])
            label_match = bool(np.array_equal(label_hat, labels_true))
            seed = block_toeplitz_seed_bits(
                "adaptive", block_index, stage + 1, master=master, bit_length=tl.seed_bits_for(n)
            )
            tag_true = tag_fn(labels_true_bits, seed, TAG_BITS)
            tag_hat = tag_fn(tl.labels_to_bits(label_hat), seed, TAG_BITS)
            tag_pass = tag_true == tag_hat
            tag_invocations += 1
            tagged_stages.append(stage)
        except Exception as exc:  # all other exceptions fail closed
            l2_failed = True
            l2_error = type(exc).__name__
            nonfinite = nonfinite or tl._nonfinite_flag(exc)
            termination_stage = stage + 1
            break

        if tag_pass:
            outcome = _outcome_from_tag(tag_pass, label_match)
            termination_stage = stage + 1
            break
        if stage + 1 < len(levels):
            feedback_stages.append(stage)
            feedback_invocations += 1
            continue
        outcome = "verify_failed"
        termination_stage = stage + 1
        break

    if outcome is None:
        outcome = "decode_failed" if (l1_failed or l2_failed) else "verify_failed"
        termination_stage = termination_stage or levels_invoked
    termination_k1 = int(levels[termination_stage - 1])
    key_dependent_bits = (
        DISCLOSED_BITS_PER_COORDINATE * termination_k1
        + (DISCLOSED_BITS_PER_COORDINATE * int(d2.shape[0]) if l2_invoked else 0)
        + (TAG_BITS * tag_invocations)
    )
    public_seed_bits = tl.seed_bits_for(n) * tag_invocations
    feedback_bits = FEEDBACK_CONTROL_BITS * feedback_invocations
    return AdaptiveArmResult(
        block_index=int(block_index),
        arm="adaptive",
        outcome=outcome,
        exact=bool(outcome == "exact"),
        label_match=label_match,
        tag_pass=tag_pass,
        l1_provenance=Provenance.PRIOR_ONLY.value,
        l2_provenance=(
            Provenance.CANDIDATE_CONDITIONED.value if l2_invoked else None
        ),
        l1_executed=bool(not l1_failed),
        l1_decode_failed=bool(l1_failed),
        l2_invoked=bool(l2_invoked),
        l2_decode_failed=bool(l2_failed),
        tag_invoked=bool(tag_invocations > 0),
        levels_invoked=levels_invoked,
        tag_invocations=tag_invocations,
        feedback_invocations=feedback_invocations,
        termination_stage=termination_stage,
        termination_k1=termination_k1,
        key_dependent_bits=int(key_dependent_bits),
        public_seed_bits=int(public_seed_bits),
        feedback_bits=int(feedback_bits),
        public_control_bits=int(public_seed_bits + feedback_bits),
        nonfinite=bool(nonfinite),
        truth_leak_violation=False,  # updated by the paired sentinel
        l1_error_type=l1_error,
        l2_error_type=l2_error,
        wall_s=time.perf_counter() - start,
        tagged_stages=tuple(tagged_stages),
        feedback_stages=tuple(feedback_stages),
        rejected_stages=tuple(rejected_stages),
        l2_stage=l2_stage,
        high_hat=candidate,
        low_hat=low_hat,
        label_hat=label_hat,
        protected_arrays=tuple(protected),
    )


def run_paired_block(
    block_index,
    high_true,
    low_true,
    bob,
    *,
    field,
    p1_table,
    p2_table,
    d1_sets,
    d2,
    levels,
    n,
    master,
    tag_fn=None,
) -> PairedBlockResult:
    """Run both arms on one block and prove the truth boundary bitwise.

    The static arm and the adaptive arm receive identical sampled arrays and
    disclosed values; after scoring, the truth copies are adversarially mutated
    and every protected operational array must stay bitwise unchanged.
    """
    index = _as_int(block_index, "block_index", minimum=0)
    n = _as_int(n, "n", minimum=1)
    levels = tuple(_as_int(v, "k1_level", minimum=1) for v in levels)
    high_arr = tl._checked_layer(high_true, n, "high_true", alphabet=Q)
    low_arr = tl._checked_layer(low_true, n, "low_true", alphabet=Q)
    bob_arr = tl._checked_layer(bob, n, "bob", alphabet=Q * Q)

    u1_true = tl.polar_transform(high_arr, field=field, alpha=ALPHA)
    u2_true = tl.polar_transform(low_arr, field=field, alpha=ALPHA)
    labels_true = (low_arr + LABEL_SCALE * high_arr).astype(np.int64)
    labels_true_bits = tl.labels_to_bits(labels_true)

    p1_probs = build_p1_metrics(bob_arr[None, :], p1_table)[0]
    p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)
    block_start = time.perf_counter()

    static = run_static_arm(
        index,
        field=field,
        p1_logp=p1_metric.logp,
        p2_table=p2_table,
        d1=np.asarray(d1_sets[-1], dtype=np.int64),
        d2=d2,
        bob=bob_arr,
        u1_true=u1_true,
        u2_true=u2_true,
        labels_true=labels_true,
        labels_true_bits=labels_true_bits,
        n=n,
        master=master,
        tag_fn=tag_fn,
    )
    adaptive = run_adaptive_arm(
        index,
        field=field,
        p1_logp=p1_metric.logp,
        p2_table=p2_table,
        d1_sets=d1_sets,
        d2=d2,
        bob=bob_arr,
        u1_true=u1_true,
        u2_true=u2_true,
        labels_true=labels_true,
        labels_true_bits=labels_true_bits,
        levels=levels,
        n=n,
        master=master,
        tag_fn=tag_fn,
    )

    protected = list(static.protected_arrays) + list(adaptive.protected_arrays)
    truth_high = np.array(high_arr, copy=True)
    truth_low = np.array(low_arr, copy=True)
    truth_u1 = np.array(u1_true, copy=True)
    truth_u2 = np.array(u2_true, copy=True)
    truth_labels = np.array(labels_true, copy=True)
    isolated = tl._truth_isolation_sentinel(
        protected,
        [
            (truth_high, Q),
            (truth_low, Q),
            (truth_u1, Q),
            (truth_u2, Q),
            (truth_labels, Q * Q),
        ],
    )
    static = replace(static, truth_leak_violation=bool(not isolated))
    adaptive = replace(adaptive, truth_leak_violation=bool(not isolated))
    return PairedBlockResult(
        block_index=index,
        static=static,
        adaptive=adaptive,
        block_wall_s=time.perf_counter() - block_start,
        labels_true=np.array(labels_true, copy=True),
        p1_logp=p1_metric.logp,
    )


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
        "frame_key": f"nbpolar-p4p6-synthetic:{int(stream_seed)}:{int(block_index)}",
        "method": "nbpolar_adaptive_l1",
        "event_type": event_type,
        "direction": direction,
        "parent_event_id": parent_event_id,
        "pass_id": 0,
        "stream_seed": int(stream_seed),
        "block_id": int(block_index),
        "key_dependent_bits": int(key_dependent_bits),
        "public_control_bits": int(public_control_bits),
        "payload": payload,
    }
    canonical_event(event)  # fail closed on malformed or secret-bearing payloads
    return event


def paired_block_events(result: PairedBlockResult, *, stream_seed: int, nested, d2, n: int) -> list:
    """Canonical public transcript events for both arms, in protocol order.

    Static: L1 disclosure, L2 disclosure (when invoked), one tag.  Adaptive:
    one cumulative-increment L1 disclosure per invoked stage, one L2 disclosure
    per arm/block (when invoked), one tag per invoked stage and one one-bit
    control event per feedback (tag mismatch or nonterminal rejection).

    Block indices repeat across streams, so every event carries the public
    scalar ``stream_seed`` alongside ``block_id`` and the arm encoded in the
    event id: the unambiguous event identity is
    ``(stream_seed, block_index, arm)``.
    """
    stream_seed = _as_int(stream_seed, "stream_seed", minimum=0)
    seed_length = tl.seed_bits_for(n)
    events: list[dict] = []
    block_index = int(result.block_index)

    static = result.static
    if static.outcome != "resource_abort":
        l1_id = f"block-{block_index}-static-l1-disclosure"
        events.append(
            _event(
                stream_seed=stream_seed,
                block_index=block_index,
                event_id=l1_id,
                event_type="l1_disclosure",
                direction="alice_to_bob",
                parent_event_id=None,
                key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * int(static.termination_k1),
                public_control_bits=0,
                payload={},
            )
        )
        if static.l2_invoked:
            l2_id = f"block-{block_index}-static-l2-disclosure"
            events.append(
                _event(
                    stream_seed=stream_seed,
                    block_index=block_index,
                    event_id=l2_id,
                    event_type="l2_disclosure",
                    direction="alice_to_bob",
                    parent_event_id=l1_id,
                    key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * int(len(d2)),
                    public_control_bits=0,
                    payload={},
                )
            )
            if static.tag_invoked:
                events.append(
                    _event(
                        stream_seed=stream_seed,
                        block_index=block_index,
                        event_id=f"block-{block_index}-static-verification",
                        event_type="verification_tag",
                        direction="alice_to_bob",
                        parent_event_id=l2_id,
                        key_dependent_bits=TAG_BITS,
                        public_control_bits=seed_length,
                        payload={"seed_bit_length": seed_length},
                    )
                )

    adaptive = result.adaptive
    if adaptive.outcome != "resource_abort":
        parent = None
        for stage in range(adaptive.levels_invoked):
            l1_id = f"block-{block_index}-adaptive-l1-{stage}"
            events.append(
                _event(
                    stream_seed=stream_seed,
                    block_index=block_index,
                    event_id=l1_id,
                    event_type="l1_disclosure",
                    direction="alice_to_bob",
                    parent_event_id=parent,
                    key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE
                    * int(len(nested.new_positions[stage])),
                    public_control_bits=0,
                    payload={},
                )
            )
            parent = l1_id
            if adaptive.l2_stage == stage:
                l2_id = f"block-{block_index}-adaptive-l2"
                events.append(
                    _event(
                        stream_seed=stream_seed,
                        block_index=block_index,
                        event_id=l2_id,
                        event_type="l2_disclosure",
                        direction="alice_to_bob",
                        parent_event_id=parent,
                        key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * int(len(d2)),
                        public_control_bits=0,
                        payload={},
                    )
                )
                parent = l2_id
            if stage in adaptive.tagged_stages:
                verification_id = f"block-{block_index}-adaptive-verification-{stage}"
                events.append(
                    _event(
                        stream_seed=stream_seed,
                        block_index=block_index,
                        event_id=verification_id,
                        event_type="verification_tag",
                        direction="alice_to_bob",
                        parent_event_id=parent,
                        key_dependent_bits=TAG_BITS,
                        public_control_bits=seed_length,
                        payload={"seed_bit_length": seed_length},
                    )
                )
                parent = verification_id
            if stage in adaptive.feedback_stages:
                control_id = f"block-{block_index}-adaptive-control-{stage}"
                events.append(
                    _event(
                        stream_seed=stream_seed,
                        block_index=block_index,
                        event_id=control_id,
                        event_type="control",
                        direction="control",
                        parent_event_id=parent,
                        key_dependent_bits=0,
                        public_control_bits=FEEDBACK_CONTROL_BITS,
                        payload={
                            "reason": (
                                "decode_rejected_advance_next_level"
                                if stage in adaptive.rejected_stages
                                else "tag_mismatch_advance_next_level"
                            )
                        },
                    )
                )
                parent = control_id
    return events


def recount_transcript(events) -> dict:
    """Independent literal recount; parses the arm from the event id."""
    totals = {
        "key_dependent_bits": 0,
        "public_seed_bits": 0,
        "feedback_bits": 0,
        "public_control_bits": 0,
        "tag_invocations": 0,
        "feedback_invocations": 0,
    }
    by_arm = {arm: dict(totals) for arm in ARMS}
    event_types = {
        "l1_disclosure": 0,
        "l2_disclosure": 0,
        "verification_tag": 0,
        "control": 0,
    }
    for event in events:
        parts = str(event["event_id"]).split("-")
        if len(parts) < 3 or parts[0] != "block" or parts[2] not in ARMS:
            raise ValueError(f"transcript event id is not arm-tagged: {event['event_id']!r}")
        arm = parts[2]
        key = int(event["key_dependent_bits"])
        public = int(event["public_control_bits"])
        event_type = str(event["event_type"])
        if event_type not in event_types:
            raise ValueError(f"transcript event type is not frozen: {event_type!r}")
        event_types[event_type] += 1
        totals["key_dependent_bits"] += key
        totals["public_control_bits"] += public
        by_arm[arm]["key_dependent_bits"] += key
        by_arm[arm]["public_control_bits"] += public
        if event_type == "verification_tag":
            totals["tag_invocations"] += 1
            by_arm[arm]["tag_invocations"] += 1
            totals["public_seed_bits"] += public
            by_arm[arm]["public_seed_bits"] += public
        if event_type == "control":
            totals["feedback_invocations"] += 1
            by_arm[arm]["feedback_invocations"] += 1
            totals["feedback_bits"] += public
            by_arm[arm]["feedback_bits"] += public
    return {
        "key_dependent_bits": totals["key_dependent_bits"],
        "public_seed_bits": totals["public_seed_bits"],
        "feedback_bits": totals["feedback_bits"],
        "public_control_bits": totals["public_control_bits"],
        "tag_invocations": totals["tag_invocations"],
        "feedback_invocations": totals["feedback_invocations"],
        "event_types": event_types,
        "by_arm": by_arm,
    }


def _transcript_mismatches(incremental, incremental_by_arm, recount) -> list:
    fields = (
        "key_dependent_bits",
        "public_seed_bits",
        "feedback_bits",
        "public_control_bits",
        "tag_invocations",
        "feedback_invocations",
    )
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


@dataclass(frozen=True, eq=False)
class AdaptiveGateRun:
    """In-memory adaptive hard-L1 gate run (also returned by the runner)."""

    results: list
    records: list
    events: list
    plan: dict
    transcript: dict
    summary: dict


def _arm_record(arm: AdaptiveArmResult) -> dict:
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
        "l2_decode_failed": bool(arm.l2_decode_failed),
        "tag_invoked": bool(arm.tag_invoked),
        "levels_invoked": int(arm.levels_invoked),
        "tag_invocations": int(arm.tag_invocations),
        "feedback_invocations": int(arm.feedback_invocations),
        "termination_stage": int(arm.termination_stage),
        "termination_k1": int(arm.termination_k1),
        "key_dependent_bits": int(arm.key_dependent_bits),
        "public_seed_bits": int(arm.public_seed_bits),
        "feedback_bits": int(arm.feedback_bits),
        "public_control_bits": int(arm.public_control_bits),
        "nonfinite": bool(arm.nonfinite),
        "truth_leak_violation": bool(arm.truth_leak_violation),
        "l1_error_type": arm.l1_error_type,
        "l2_error_type": arm.l2_error_type,
        "wall_s": round(float(arm.wall_s), 6),
    }


def _block_record(result: PairedBlockResult, *, stream_seed: int) -> dict:
    return {
        "stream_seed": int(stream_seed),
        "block_index": int(result.block_index),
        "paired_cell": classify_cell(result.static.exact, result.adaptive.exact),
        "static": _arm_record(result.static),
        "adaptive": _arm_record(result.adaptive),
    }


def _static_record_consistent(arm: AdaptiveArmResult, *, d1_size: int, d2_size: int, n: int) -> bool:
    """Structural proof of one static record under the frozen rules."""
    if arm.arm != "static" or arm.outcome not in tl.OUTCOMES:
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
                    arm.l2_decode_failed,
                    arm.tag_invoked,
                    arm.nonfinite,
                    arm.truth_leak_violation,
                )
            )
        )
    if arm.levels_invoked != 1 or arm.termination_stage != 1:
        return False
    if arm.termination_k1 != d1_size or arm.feedback_invocations != 0:
        return False
    if arm.l1_provenance != Provenance.PRIOR_ONLY.value:
        return False
    if arm.l1_executed == arm.l1_decode_failed:
        return False
    if arm.l1_decode_failed:
        if arm.l2_invoked or arm.l2_provenance is not None:
            return False
        if arm.outcome != "decode_failed":
            return False
    else:
        if not arm.l2_invoked or arm.l2_provenance != Provenance.CANDIDATE_CONDITIONED.value:
            return False
        if arm.l2_decode_failed:
            if arm.outcome != "decode_failed":
                return False
        else:
            if arm.outcome not in TAG_OUTCOMES or arm.tag_invocations != 1:
                return False
            if arm.outcome == "exact" and not (arm.tag_pass and arm.label_match):
                return False
            if arm.outcome == "undetected" and not (arm.tag_pass and not arm.label_match):
                return False
            if arm.outcome == "verify_failed" and arm.tag_pass:
                return False
    expected_kdb = (
        DISCLOSED_BITS_PER_COORDINATE * d1_size
        + (DISCLOSED_BITS_PER_COORDINATE * d2_size if arm.l2_invoked else 0)
        + (TAG_BITS if arm.tag_invoked else 0)
    )
    if int(arm.key_dependent_bits) != expected_kdb:
        return False
    if arm.tag_invoked != (arm.tag_invocations == 1):
        return False
    if int(arm.public_seed_bits) != (tl.seed_bits_for(n) if arm.tag_invoked else 0):
        return False
    if int(arm.feedback_bits) != 0 or int(arm.public_control_bits) != int(arm.public_seed_bits):
        return False
    return True


def _adaptive_record_consistent(arm: AdaptiveArmResult, *, levels, d2_size: int, n: int) -> bool:
    """Structural proof of one adaptive record under the frozen rules."""
    if arm.arm != "adaptive" or arm.outcome not in tl.OUTCOMES:
        return False
    if arm.outcome == "resource_abort":
        return (
            int(arm.key_dependent_bits) == 0
            and int(arm.public_control_bits) == 0
            and int(arm.levels_invoked) == 0
            and not any(
                (
                    arm.exact,
                    arm.label_match,
                    arm.tag_pass,
                    arm.l1_executed,
                    arm.l1_decode_failed,
                    arm.l2_invoked,
                    arm.l2_decode_failed,
                    arm.tag_invoked,
                    arm.nonfinite,
                    arm.truth_leak_violation,
                )
            )
        )
    levels_t = tuple(int(v) for v in levels)
    if not 1 <= arm.termination_stage <= len(levels_t):
        return False
    if arm.termination_k1 != levels_t[arm.termination_stage - 1]:
        return False
    if arm.levels_invoked != arm.termination_stage:
        return False
    if arm.l1_provenance != Provenance.PRIOR_ONLY.value:
        return False
    if arm.l1_executed == arm.l1_decode_failed:
        return False
    if arm.feedback_invocations > arm.termination_stage - 1:
        return False
    if len(arm.feedback_stages) != arm.feedback_invocations:
        return False
    if len(arm.tagged_stages) != arm.tag_invocations:
        return False
    if arm.tag_invoked != (arm.tag_invocations > 0):
        return False
    if arm.l2_invoked != (arm.l2_provenance == Provenance.CANDIDATE_CONDITIONED.value):
        return False
    if arm.l1_decode_failed:
        if arm.outcome != "decode_failed":
            return False
        if arm.termination_stage - 1 in arm.tagged_stages:
            return False
    elif arm.l2_decode_failed:
        if arm.outcome != "decode_failed":
            return False
        if arm.termination_stage - 1 in arm.tagged_stages:
            return False
    else:
        if not arm.l2_invoked:
            if arm.outcome != "decode_failed":
                return False
        else:
            if arm.outcome not in TAG_OUTCOMES:
                return False
            if arm.termination_stage - 1 not in arm.tagged_stages:
                return False
            if arm.outcome == "exact" and not (arm.tag_pass and arm.label_match):
                return False
            if arm.outcome == "undetected" and not (arm.tag_pass and not arm.label_match):
                return False
            if arm.outcome == "verify_failed":
                if arm.tag_pass or arm.termination_stage != len(levels_t):
                    return False
    expected_kdb = (
        DISCLOSED_BITS_PER_COORDINATE * arm.termination_k1
        + (DISCLOSED_BITS_PER_COORDINATE * d2_size if arm.l2_invoked else 0)
        + TAG_BITS * arm.tag_invocations
    )
    if int(arm.key_dependent_bits) != expected_kdb:
        return False
    if int(arm.public_seed_bits) != tl.seed_bits_for(n) * arm.tag_invocations:
        return False
    if int(arm.feedback_bits) != FEEDBACK_CONTROL_BITS * arm.feedback_invocations:
        return False
    if int(arm.public_control_bits) != int(arm.public_seed_bits) + int(arm.feedback_bits):
        return False
    return True


def _integrity_gates(
    *,
    planned: int,
    results,
    stream_seeds,
    blocks_per_seed: int,
    events,
    nested,
    levels,
    k2: int,
    n: int,
    incremental,
    incremental_by_arm,
    recount,
    mismatches,
    union_bound: float,
    wall_s: float,
    total_wall_s: float,
    rss_bytes,
) -> dict:
    static = [r.static for r in results]
    adaptive = [r.adaptive for r in results]
    arms = static + adaptive
    expected_identity = {
        (int(seed), int(block))
        for seed in stream_seeds
        for block in range(int(blocks_per_seed))
    }
    actual_identity = {(int(r.stream_seed), int(r.block_index)) for r in results}
    outcomes_ok = all(a.outcome in tl.OUTCOMES for a in arms)
    static_ok = all(
        _static_record_consistent(
            a, d1_size=int(len(nested.sets[-1])), d2_size=int(k2), n=n
        )
        for a in static
    )
    adaptive_ok = all(
        _adaptive_record_consistent(a, levels=levels, d2_size=int(k2), n=n)
        for a in adaptive
    )
    bucket_sums_ok = all(
        sum(sum(1 for a in arm_list if a.outcome == name) for name in tl.OUTCOMES) == planned
        for arm_list in (static, adaptive)
    )
    l2_counts: dict = {}
    l2_key_ok = True
    for event in events:
        if event["event_type"] != "l2_disclosure":
            continue
        parts = str(event["event_id"]).split("-")
        # Block indices repeat across streams, so the once-per-arm/block check
        # must key on the compound (stream_seed, block_id, arm) identity.
        key = (int(event["stream_seed"]), int(event["block_id"]), parts[2])
        l2_counts[key] = l2_counts.get(key, 0) + 1
        if int(event["key_dependent_bits"]) != DISCLOSED_BITS_PER_COORDINATE * int(k2):
            l2_key_ok = False
    expected_l2 = {
        (int(r.stream_seed), int(r.block_index), arm.arm)
        for r in results
        for arm in (r.static, r.adaptive)
        if arm.l2_invoked
    }
    l2_once = (
        l2_key_ok
        and all(count == 1 for count in l2_counts.values())
        and set(l2_counts) == expected_l2
    )
    record_sums = {
        "key_dependent_bits": sum(int(a.key_dependent_bits) for a in arms),
        "public_seed_bits": sum(int(a.public_seed_bits) for a in arms),
        "feedback_bits": sum(int(a.feedback_bits) for a in arms),
        "public_control_bits": sum(int(a.public_control_bits) for a in arms),
        "tag_invocations": sum(int(a.tag_invocations) for a in arms),
        "feedback_invocations": sum(int(a.feedback_invocations) for a in arms),
    }
    record_sums_ok = all(
        record_sums[name] == int(incremental[name])
        for name in (
            "key_dependent_bits",
            "public_seed_bits",
            "feedback_bits",
            "public_control_bits",
            "tag_invocations",
            "feedback_invocations",
        )
    )
    seed_length = tl.seed_bits_for(n)
    tag_bits_ok = all(
        int(event["public_control_bits"]) == seed_length
        for event in events
        if event["event_type"] == "verification_tag"
    )
    control_bits_ok = all(
        int(event["public_control_bits"]) == FEEDBACK_CONTROL_BITS
        for event in events
        if event["event_type"] == "control"
    )
    return {
        "pairing_coverage_complete": bool(len(results) == planned),
        "stream_block_identity_exact": bool(actual_identity == expected_identity),
        "result_buckets_disjoint_exhaustive": bool(
            outcomes_ok and static_ok and adaptive_ok and bucket_sums_ok
        ),
        "d1_exactly_nested_and_d2_disclosed_once": bool(
            nested.strict_nesting
            and nested.order_prefix_matches
            and nested.new_coordinates_disjoint
            and tuple(int(v) for v in nested.sizes) == tuple(int(v) for v in levels)
            and all(
                len(nested.sets[i]) < len(nested.sets[i + 1])
                and bool(np.isin(nested.sets[i], nested.sets[i + 1]).all())
                for i in range(len(nested.sets) - 1)
            )
            and l2_once
            and all(
                int(r.static.termination_k1) == STATIC_K1 for r in results
            )
        ),
        "provenance_and_truth_isolation_complete": bool(
            all(
                (not a.l1_executed) or a.l1_provenance == Provenance.PRIOR_ONLY.value
                for a in arms
            )
            and all(
                (not a.l2_invoked) or a.l2_provenance == Provenance.CANDIDATE_CONDITIONED.value
                for a in arms
            )
            and not any(a.truth_leak_violation for a in arms)
        ),
        "undetected_zero": not any(a.outcome == "undetected" for a in arms),
        "nonfinite_zero": not any(a.nonfinite for a in arms),
        "resource_abort_zero": not any(a.outcome == "resource_abort" for a in arms),
        "transcript_recount_mismatch_zero": bool(not mismatches),
        "tag_feedback_public_control_accounting_and_union_bound_exact": bool(
            record_sums_ok
            and recount["tag_invocations"] == incremental["tag_invocations"]
            and recount["feedback_invocations"] == incremental["feedback_invocations"]
            and recount["key_dependent_bits"] == incremental["key_dependent_bits"]
            and recount["public_seed_bits"] == incremental["public_seed_bits"]
            and recount["feedback_bits"] == incremental["feedback_bits"]
            and recount["public_control_bits"] == incremental["public_control_bits"]
            and tag_bits_ok
            and control_bits_ok
            and union_bound == verification_union_bound(recount["tag_invocations"])
        ),
        "wall_rss_within_frozen_limits": bool(
            float(wall_s) <= float(total_wall_s)
            and (rss_bytes is None or int(rss_bytes) <= RSS_LIMIT_BYTES)
        ),
        "attempt_seed_accounting_exact": bool(
            int(ATTEMPT_ACCOUNTING["attempts_allowed"]) == 1
            and int(ATTEMPT_ACCOUNTING["attempts_consumed_before"]) == 0
            and int(ATTEMPT_ACCOUNTING["attempts_consumed_by_this_run"]) == 1
            and int(ATTEMPT_ACCOUNTING["retries"]) == 0
            and len(set(int(s) for s in stream_seeds)) == len(list(stream_seeds))
            and not any(int(s) in BANNED_SEEDS for s in stream_seeds)
        ),
    }


def _scientific_gates(*, planned, static_exact, adaptive_exact, cells, static_kd, adaptive_kd) -> dict:
    return {
        "static_exact_at_least_620_of_640": bool(
            int(planned) == FROZEN_PAIRS and int(static_exact) >= STATIC_EXACT_MIN
        ),
        "adaptive_exact_equals_static_exact": bool(int(adaptive_exact) == int(static_exact)),
        "paired_adaptive_only_zero_and_static_only_zero": bool(
            int(cells["adaptive_only"]) == 0 and int(cells["static_only"]) == 0
        ),
        "leakage_100_adaptive_le_85_static": bool(
            100 * int(adaptive_kd) <= 85 * int(static_kd)
        ),
    }


def _peak_rss_bytes() -> int | None:
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _empty_totals() -> dict:
    return {
        "key_dependent_bits": 0,
        "public_seed_bits": 0,
        "feedback_bits": 0,
        "public_control_bits": 0,
        "tag_invocations": 0,
        "feedback_invocations": 0,
    }


def _build_plan(
    *,
    out_path: Path,
    n: int,
    epsilon1: float,
    profile: str,
    levels,
    k2: int,
    seeds,
    blocks_per_seed: int,
    d1_sets,
    d2,
    nested,
    table_deviation: float,
    p2_maxdiff: float,
    entropy: dict,
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
        "epsilon1": float(epsilon1),
        "profile": profile,
        "epsilon2_formula": pg.PROFILE_FORMULAS[profile],
        "epsilon2_mean": PROFILE_MEAN_EPSILON2,
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "dependent_table": {
            "formula": "P(B|A) = Ph(B_high|high) * Pl(B_low|low, high)",
            "builder": "penalty_gate.build_dependent_joint_table(profile='strong')",
            "column_normalization_tolerance": 1e-12,
            "column_max_deviation": float(table_deviation),
            "p2_maxdiff_definition": (
                "max_{u1,u1',b,u2} |P2[u1,b,u2] - P2[u1',b,u2]| on the derived "
                "[U1,B,U2] table before any decoder call"
            ),
            "p2_maxdiff": float(p2_maxdiff),
            "p2_maxdiff_floor": pg.P2_MAXDIFF_FLOOR,
        },
        "k1_levels": [int(v) for v in levels],
        "k2": int(k2),
        "static_k1": STATIC_K1,
        "disclosure_rule": (
            "adaptive D1(K1_j) = sorted(analytic_order(0.05, n)[:K1_j]) strictly "
            "nested, worst-first; static D1 = sorted(analytic_order(0.05, n)[:112]); "
            "D2 = sorted(analytic_order(0.20, n)[:k2]) disclosed once per arm/block; "
            "actual GF32 U1[D1]/U2[D2] values including zeros; SC known_positions = "
            "the sorted sets"
        ),
        "disclosure_coordinates": {
            "D1_by_level": {
                str(int(k)): [int(v) for v in d1_sets[i]]
                for i, k in enumerate(levels)
            },
            "D1_new_positions_by_level": {
                str(int(k)): [int(v) for v in nested.new_positions[i]]
                for i, k in enumerate(levels)
            },
            "D2": [int(v) for v in d2],
        },
        "nested_assertions": {
            "rule": "D1(K1_j) = sorted(analytic_order(0.05, n)[:K1_j])",
            "sizes": [int(len(s)) for s in d1_sets],
            "strict_nesting": bool(nested.strict_nesting),
            "order_prefix_matches": bool(nested.order_prefix_matches),
            "new_coordinates_disjoint": bool(nested.new_coordinates_disjoint),
        },
        "arms": list(ARMS),
        "static_arm": (
            "one fresh L1 SC at K1=112 on the P1 prior metric, one "
            "candidate-conditioned L2 SC at K2, then one 64-bit verification tag; "
            "fully invoked cost 1324"
        ),
        "adaptive_arm": (
            "for each one-based stage j with K1_j in k1_levels: restart L1 SC from the "
            "ORIGINAL P1 metric with the cumulative nested prefix, restart the "
            "candidate-conditioned L2 SC from the ORIGINAL P2 table gathered by the "
            "current hard L1 candidate, verify the full 10-bit label with one 64-bit "
            "tag; tag match accepts and stops; mismatch before the terminal stage "
            "emits one feedback bit and advances; terminal mismatch is verify_failed; "
            "a nonterminal ImpossibleDisclosedValueError emits one feedback bit and "
            "advances; terminal impossible and all other exceptions are decode_failed; "
            "no decoder state, metric, partial sum, candidate label or tag seed is "
            "reused between stages"
        ),
        "restart_rule": (
            "every stage calls a fresh SC decode on the ORIGINAL P1 metric (L1) and a "
            "freshly gathered candidate-conditioned metric (L2); no warm start, no "
            "reuse of sc objects"
        ),
        "tag_rule": (
            "one 64-bit Toeplitz tag per invoked stage under the per-arm/block/level "
            "domain; static uses level 1; adaptive stage j uses level j"
        ),
        "feedback_rule": (
            "one public one-bit control per advance: tag mismatch before the terminal "
            "stage or nonterminal impossible disclosure"
        ),
        "impossible_rule": (
            "nonterminal ImpossibleDisclosedValueError: no candidate, no tag, one "
            "feedback bit, advance; terminal (K1=112): decode_failed; all other "
            "exceptions fail closed"
        ),
        "truth_scope": (
            "high_true/low_true enter only sampling, disclosed values, tag construction "
            "and scoring; they never enter any undisclosed operational metric, "
            "decision or tag seed"
        ),
        "seed_derivation": SEED_DERIVATION,
        "accounting": {
            "bits_per_coordinate": DISCLOSED_BITS_PER_COORDINATE,
            "tag_bits": TAG_BITS,
            "public_control_bits_per_tag": tl.seed_bits_for(n),
            "feedback_control_bits": FEEDBACK_CONTROL_BITS,
            "adaptive_key_dependent_bits_at_stage_j": (
                "5*(K_j+140) + 64*tag_invocations realized from executed disclosures "
                "(cumulative L1 prefix + once-per-arm/block L2 disclosure when L2 was "
                "invoked + one 64-bit tag per invocation)"
            ),
            "static_fully_invoked_bits": STATIC_FULLY_INVOKED_BITS,
            "fully_invoked_adaptive_bits_by_level": {
                str(int(k)): DISCLOSED_BITS_PER_COORDINATE * (int(k) + int(k2)) + TAG_BITS
                for k in levels
            },
            "public_seed_bits": "2623*tag_invocations",
            "feedback_bits": "feedback_invocations",
            "public_control_bits": "public_seed_bits + feedback_bits",
            "decode_rejection_creates_no_tag": True,
            "recount_rule": (
                "independent literal transcript recount equals the incremental per-arm "
                "and total totals with zero mismatch"
            ),
            "union_bound": "min(1.0, total_tag_invocations * 2**-64)",
        },
        "planning_only_f": {
            "definition": "mean_key_dependent_bits / (256*(H1+H2)); planning-only surrogate",
            "h_a_given_b_bits": float(entropy["h_a_given_b_bits"]),
            "h_a_given_b_reference_bits": H_A_GIVEN_B_REFERENCE_BITS,
            "denominator_bits": float(n) * float(entropy["h_a_given_b_bits"]),
            "denominator_reference_bits": PLANNING_DENOMINATOR_BITS,
            "scope": "not real-channel efficiency or qualification evidence",
        },
        "cells": list(CELLS),
        "cell_rule": (
            "both_exact = both arms exact; adaptive_only = adaptive exact and static "
            "not; static_only = static exact and adaptive not; neither = neither exact"
        ),
        "integrity_gate_order": list(INTEGRITY_GATE_ORDER),
        "scientific_gate_order": list(SCIENTIFIC_GATE_ORDER),
        "scientific_gates": {
            "static_exact_min": STATIC_EXACT_MIN,
            "frozen_pairs": FROZEN_PAIRS,
            "adaptive_exact_equals_static_exact": True,
            "paired_adaptive_only_zero": True,
            "paired_static_only_zero": True,
            "leakage_ratio": (
                "100*adaptive_total_key_dependent <= 85*static_total_key_dependent"
            ),
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
    levels,
    k2: int,
    static_k1: int,
    p2_maxdiff: float,
    entropy: dict,
    gates: dict,
    scientific: dict,
    cells: dict,
    incremental,
    incremental_by_arm,
    recount,
    mismatches,
    union_bound: float,
    wall_s: float,
    rss_bytes,
    resource_stop_fired: bool,
    no_l2_exhaustion_blocks: int,
) -> dict:
    static = [r.static for r in results]
    adaptive = [r.adaptive for r in results]
    static_exact = sum(1 for a in static if a.exact)
    adaptive_exact = sum(1 for a in adaptive if a.exact)
    denominator = max(int(planned), 1)
    static_kd = int(incremental_by_arm["static"]["key_dependent_bits"])
    adaptive_kd = int(incremental_by_arm["adaptive"]["key_dependent_bits"])
    static_mean = static_kd / denominator
    adaptive_mean = adaptive_kd / denominator
    percentage_saving = (
        100.0 * (static_kd - adaptive_kd) / static_kd if static_kd else 0.0
    )
    termination_histogram = {
        str(stage): sum(1 for a in adaptive if a.termination_stage == stage)
        for stage in range(1, len(levels) + 1)
    }
    termination_k1_histogram = {
        str(int(k)): sum(1 for a in adaptive if a.termination_k1 == int(k))
        for k in levels
    }
    per_stream = []
    for seed in seeds:
        rows = [r for r in results if int(r.stream_seed) == int(seed)]
        per_stream.append(
            {
                "stream_seed": int(seed),
                "toeplitz_master": int(seed) + PUBLIC_TAG_MASTER_OFFSET,
                "blocks": len(rows),
                "static_exact": sum(1 for r in rows if r.static.exact),
                "adaptive_exact": sum(1 for r in rows if r.adaptive.exact),
                "cells": {
                    cell: sum(
                        1
                        for r in rows
                        if classify_cell(r.static.exact, r.adaptive.exact) == cell
                    )
                    for cell in CELLS
                },
                "static_total_key_dependent_bits": sum(
                    int(r.static.key_dependent_bits) for r in rows
                ),
                "adaptive_total_key_dependent_bits": sum(
                    int(r.adaptive.key_dependent_bits) for r in rows
                ),
                "static_tag_invocations": sum(int(r.static.tag_invocations) for r in rows),
                "adaptive_tag_invocations": sum(
                    int(r.adaptive.tag_invocations) for r in rows
                ),
                "adaptive_feedback_invocations": sum(
                    int(r.adaptive.feedback_invocations) for r in rows
                ),
                "adaptive_termination_histogram": {
                    str(stage): sum(
                        1 for r in rows if r.adaptive.termination_stage == stage
                    )
                    for stage in range(1, len(levels) + 1)
                },
            }
        )
    integrity_all_pass = bool(all(gates.values()))
    failing = [name for name in INTEGRITY_GATE_ORDER if not gates[name]]
    scientific_all_pass = bool(all(scientific.values()))
    failing_scientific = [name for name in SCIENTIFIC_GATE_ORDER if not scientific[name]]
    if not integrity_all_pass:
        outcome_label = "BLOCKED"
    elif scientific_all_pass:
        outcome_label = "ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE"
    else:
        outcome_label = "ADAPTIVE_HARD_L1_DISCLOSURE_NOT_CONFIRMED"
    h_cond = float(entropy["h_a_given_b_bits"])
    planning_denominator = float(n) * h_cond
    return {
        "analysis": PROTOCOL_NAME,
        "mode": MODE,
        "seeds": [int(s) for s in seeds],
        "toeplitz_masters": [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in seeds],
        "planned_pairs": int(planned),
        "shape_is_frozen_640": bool(int(planned) == FROZEN_PAIRS),
        "n": int(n),
        "q": Q,
        "epsilon1": float(epsilon1),
        "profile": profile,
        "k1_levels": [int(v) for v in levels],
        "k2": int(k2),
        "static_k1": int(static_k1),
        "p2_maxdiff": float(p2_maxdiff),
        "outcomes": {
            "static": {
                name: sum(1 for a in static if a.outcome == name) for name in tl.OUTCOMES
            },
            "adaptive": {
                name: sum(1 for a in adaptive if a.outcome == name) for name in tl.OUTCOMES
            },
        },
        "cells": dict(cells),
        "marginals": {
            "static_exact": int(static_exact),
            "adaptive_exact": int(adaptive_exact),
            "static_exact_rate": round(static_exact / denominator, 9),
            "adaptive_exact_rate": round(adaptive_exact / denominator, 9),
        },
        "adaptive_termination_histogram": termination_histogram,
        "adaptive_termination_k1_histogram": termination_k1_histogram,
        "disclosure": {
            "static_total_key_dependent_bits": static_kd,
            "adaptive_total_key_dependent_bits": adaptive_kd,
            "static_mean_key_dependent_bits": static_mean,
            "adaptive_mean_key_dependent_bits": adaptive_mean,
            "mean_saving_bits": static_mean - adaptive_mean,
            "percentage_saving": percentage_saving,
            "static_fully_invoked_bits": STATIC_FULLY_INVOKED_BITS,
        },
        "tag_invocations": {
            "static": int(incremental_by_arm["static"]["tag_invocations"]),
            "adaptive": int(incremental_by_arm["adaptive"]["tag_invocations"]),
            "total": int(incremental["tag_invocations"]),
        },
        "feedback_invocations": {
            "static": 0,
            "adaptive": int(incremental_by_arm["adaptive"]["feedback_invocations"]),
            "total": int(incremental["feedback_invocations"]),
        },
        "public_control": {
            "static_public_seed_bits": int(incremental_by_arm["static"]["public_seed_bits"]),
            "static_feedback_bits": int(incremental_by_arm["static"]["feedback_bits"]),
            "static_public_control_bits": int(
                incremental_by_arm["static"]["public_control_bits"]
            ),
            "adaptive_public_seed_bits": int(
                incremental_by_arm["adaptive"]["public_seed_bits"]
            ),
            "adaptive_feedback_bits": int(incremental_by_arm["adaptive"]["feedback_bits"]),
            "adaptive_public_control_bits": int(
                incremental_by_arm["adaptive"]["public_control_bits"]
            ),
            "total_public_control_bits": int(incremental["public_control_bits"]),
        },
        "union_bound": union_bound,
        "union_bound_definition": "min(1.0, total_tag_invocations * 2**-64)",
        "public_control_bits_per_tag": tl.seed_bits_for(n),
        "no_l2_exhaustion_blocks": int(no_l2_exhaustion_blocks),
        "per_stream": per_stream,
        "planning_only_f": {
            "definition": "mean_key_dependent_bits / (256*(H1+H2)); planning-only surrogate",
            "h_a_given_b_bits": h_cond,
            "h_a_given_b_reference_bits": H_A_GIVEN_B_REFERENCE_BITS,
            "denominator_bits": planning_denominator,
            "denominator_reference_bits": PLANNING_DENOMINATOR_BITS,
            "static": static_mean / planning_denominator if planning_denominator else None,
            "adaptive": (
                adaptive_mean / planning_denominator if planning_denominator else None
            ),
            "scope": "not real-channel efficiency or qualification evidence",
        },
        "integrity": {name: bool(gates[name]) for name in INTEGRITY_GATE_ORDER},
        "integrity_all_pass": integrity_all_pass,
        "failing_integrity_gates": failing,
        "scientific": {name: bool(scientific[name]) for name in SCIENTIFIC_GATE_ORDER},
        "scientific_all_pass": scientific_all_pass,
        "failing_scientific_gates": failing_scientific,
        "outcome_label": outcome_label,
        "transcript": {
            "event_count": int(sum(recount["event_types"].values())),
            "event_types": dict(recount["event_types"]),
            "mismatch_count": int(len(mismatches)),
            "mismatches": list(mismatches),
            "incremental_by_arm": {arm: dict(incremental_by_arm[arm]) for arm in ARMS},
            "recount": {
                "key_dependent_bits": int(recount["key_dependent_bits"]),
                "public_seed_bits": int(recount["public_seed_bits"]),
                "feedback_bits": int(recount["feedback_bits"]),
                "public_control_bits": int(recount["public_control_bits"]),
                "tag_invocations": int(recount["tag_invocations"]),
                "feedback_invocations": int(recount["feedback_invocations"]),
                "event_types": dict(recount["event_types"]),
                "by_arm": {arm: dict(recount["by_arm"][arm]) for arm in ARMS},
            },
        },
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_peak": rss_bytes,
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
    disclosure = summary["disclosure"]
    lines = [
        "# NB-Polar Phase 4-P6 adaptive hard-L1 disclosure gate — synthetic signal",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- seeds: {summary['seeds']}; masters: {summary['toeplitz_masters']}; "
        f"planned pairs: {summary['planned_pairs']}",
        f"- point: q={summary['q']}, N={summary['n']}, epsilon1={summary['epsilon1']}, "
        f"profile={summary['profile']}, K1 levels={summary['k1_levels']}, K2={summary['k2']}",
        f"- wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes",
        "",
        "## Paired cells",
        "",
        "| cell | count |",
        "|---|---|",
        f"| both_exact | {cells['both_exact']} |",
        f"| adaptive_only | {cells['adaptive_only']} |",
        f"| static_only | {cells['static_only']} |",
        f"| neither | {cells['neither']} |",
        "",
        "## Disclosure",
        "",
        f"- static: {disclosure['static_total_key_dependent_bits']} key-dependent bits "
        f"(mean {disclosure['static_mean_key_dependent_bits']:.6f})",
        f"- adaptive: {disclosure['adaptive_total_key_dependent_bits']} key-dependent bits "
        f"(mean {disclosure['adaptive_mean_key_dependent_bits']:.6f})",
        f"- percentage saving: {disclosure['percentage_saving']:.6f}%",
        f"- tag invocations (static/adaptive/total): {summary['tag_invocations']['static']}/"
        f"{summary['tag_invocations']['adaptive']}/{summary['tag_invocations']['total']}; "
        f"feedback invocations: {summary['feedback_invocations']['total']}; union bound: "
        f"{summary['union_bound']}",
        f"- adaptive termination histogram: {summary['adaptive_termination_histogram']}",
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
        "## Scientific gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in summary["scientific"].items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        f"- outcome label: `{summary['outcome_label']}`",
        "",
        f"**Scope:** {summary['claim_scope']}.",
        "",
    ]
    return "\n".join(lines)


def run_adaptive_gate(
    *,
    n,
    epsilon1,
    profile,
    k1_levels,
    k2,
    seeds,
    blocks_per_seed,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
) -> AdaptiveGateRun:
    """Execute the frozen-point adaptive hard-L1 gate and write exactly five files.

    Refuses an existing output root before any decoder call, validates the
    frozen point and the refused seeds, checks the dependent-table
    ``p2_maxdiff`` floor, then runs the static and adaptive arms once per
    planned block.  The single attempt is consumed at the first scientific SC
    call.
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
    if profile not in pg.PROFILE_FORMULAS:
        raise ValueError(f"unknown dependent-L2 profile {profile!r}")
    if profile != FROZEN_PROFILE:
        raise ValueError(f"frozen point requires profile {FROZEN_PROFILE!r}, got {profile!r}")
    levels = tuple(_as_int(v, "k1_level", minimum=1) for v in k1_levels)
    if levels != FROZEN_K1_LEVELS:
        raise ValueError(f"frozen point requires k1_levels={FROZEN_K1_LEVELS}, got {levels}")
    k2 = _as_int(k2, "k2", minimum=0)
    if k2 != FROZEN_K2:
        raise ValueError(f"frozen point requires k2={FROZEN_K2}, got {k2}")
    seed_list = [_as_int(s, "seed", minimum=0) for s in seeds]
    if not seed_list:
        raise ValueError("at least one stream seed is required")
    if len(set(seed_list)) != len(seed_list):
        raise ValueError("stream seeds must be distinct")
    for seed in seed_list:
        if seed in BANNED_SEEDS:
            raise ValueError(f"seed {seed} is banned (consumed by Phase 1-6 / X-probes)")
    blocks = _as_int(blocks_per_seed, "blocks_per_seed", minimum=1)
    total_cap = float(total_wall_s)
    if not np.isfinite(total_cap) or total_cap <= 0:
        raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")
    planned = len(seed_list) * blocks

    table = pg.build_dependent_joint_table(profile=profile, epsilon1=eps1)
    table_deviation = float(np.abs(table.sum(axis=0) - 1.0).max())
    p1_table, p2_table = tl.layer_metric_tables(table)
    p2_maxdiff = pg.require_p2_maxdiff(pg.p2_cross_u1_maxdiff(p2_table))
    entropy = h_a_given_b_from_table(table)
    if entropy["chain_vs_direct_abs_diff"] > 1e-12:
        raise AssertionError(
            "H(A|B) chain rule and direct conditional disagree: "
            f"{entropy['chain_vs_direct_abs_diff']:.3e}"
        )
    if entropy["reference_abs_diff"] > 1e-9:
        raise AssertionError(
            f"H(A|B) {entropy['h_a_given_b_bits']} differs from the accepted reference "
            f"{H_A_GIVEN_B_REFERENCE_BITS}"
        )
    nested = inc.build_nested_schedule(n=n, epsilon=eps1, sizes=levels)
    if not (
        nested.strict_nesting
        and nested.order_prefix_matches
        and nested.new_coordinates_disjoint
    ):
        raise AssertionError("nested D1 schedule proof failed before any decoder call")
    d1_sets = nested.sets
    d2 = tl.disclosure_coordinates(n=n, k=k2, epsilon=PROFILE_MEAN_EPSILON2)
    if d2.shape != (k2,) or len(set(int(v) for v in d2.tolist())) != k2:
        raise AssertionError(f"D2 shape/unique contract failed: {d2.shape}")
    field = make_gf32()

    results: list = []
    records: list = []
    events: list = []
    incremental = _empty_totals()
    incremental_by_arm = {arm: _empty_totals() for arm in ARMS}
    resource_stop_fired = False
    no_l2_exhaustion_blocks = 0
    start = time.perf_counter()

    def accumulate(static_arm, adaptive_arm) -> None:
        for arm in (static_arm, adaptive_arm):
            if arm.outcome == "resource_abort":
                continue
            incremental["key_dependent_bits"] += int(arm.key_dependent_bits)
            incremental["public_seed_bits"] += int(arm.public_seed_bits)
            incremental["feedback_bits"] += int(arm.feedback_bits)
            incremental["public_control_bits"] += int(arm.public_control_bits)
            incremental["tag_invocations"] += int(arm.tag_invocations)
            incremental["feedback_invocations"] += int(arm.feedback_invocations)
            named = incremental_by_arm[arm.arm]
            named["key_dependent_bits"] += int(arm.key_dependent_bits)
            named["public_seed_bits"] += int(arm.public_seed_bits)
            named["feedback_bits"] += int(arm.feedback_bits)
            named["public_control_bits"] += int(arm.public_control_bits)
            named["tag_invocations"] += int(arm.tag_invocations)
            named["feedback_invocations"] += int(arm.feedback_invocations)

    for stream_seed in seed_list:
        master = stream_seed + PUBLIC_TAG_MASTER_OFFSET
        rng = np.random.default_rng(stream_seed)
        for block_index in range(blocks):
            if time.perf_counter() - start > total_cap:
                resource_stop_fired = True
                for aborted in range(block_index, blocks):
                    static_abort = _abort_arm(aborted, "static")
                    adaptive_abort = _abort_arm(aborted, "adaptive")
                    aborted_result = PairedBlockResult(
                        block_index=aborted,
                        static=static_abort,
                        adaptive=adaptive_abort,
                        block_wall_s=0.0,
                    )
                    results.append(
                        ResultRow(
                            stream_seed=int(stream_seed),
                            block_index=aborted,
                            static=static_abort,
                            adaptive=adaptive_abort,
                        )
                    )
                    records.append(
                        _block_record(aborted_result, stream_seed=int(stream_seed))
                    )
                break
            sample = pg.sample_dependent_block(rng, n=n, epsilon1=eps1, profile=profile)
            paired = run_paired_block(
                block_index,
                sample.high,
                sample.low,
                sample.bob,
                field=field,
                p1_table=p1_table,
                p2_table=p2_table,
                d1_sets=d1_sets,
                d2=d2,
                levels=levels,
                n=n,
                master=master,
            )
            results.append(
                ResultRow(
                    stream_seed=int(stream_seed),
                    block_index=block_index,
                    static=paired.static,
                    adaptive=paired.adaptive,
                )
            )
            records.append(_block_record(paired, stream_seed=int(stream_seed)))
            events.extend(
                paired_block_events(
                    paired, stream_seed=int(stream_seed), nested=nested, d2=d2, n=n
                )
            )
            accumulate(paired.static, paired.adaptive)
            if paired.adaptive.outcome == "decode_failed" and not paired.adaptive.l2_invoked:
                no_l2_exhaustion_blocks += 1
        if resource_stop_fired:
            break

    wall_s = time.perf_counter() - start
    recount = recount_transcript(events)
    mismatches = _transcript_mismatches(incremental, incremental_by_arm, recount)
    union_bound = verification_union_bound(recount["tag_invocations"])
    rss_bytes = _peak_rss_bytes()
    gates = _integrity_gates(
        planned=planned,
        results=results,
        stream_seeds=seed_list,
        blocks_per_seed=blocks,
        events=events,
        nested=nested,
        levels=levels,
        k2=k2,
        n=n,
        incremental=incremental,
        incremental_by_arm=incremental_by_arm,
        recount=recount,
        mismatches=mismatches,
        union_bound=union_bound,
        wall_s=wall_s,
        total_wall_s=total_cap,
        rss_bytes=rss_bytes,
    )
    cells = {
        cell: sum(
            1 for r in results if classify_cell(r.static.exact, r.adaptive.exact) == cell
        )
        for cell in CELLS
    }
    scientific = _scientific_gates(
        planned=planned,
        static_exact=sum(1 for r in results if r.static.exact),
        adaptive_exact=sum(1 for r in results if r.adaptive.exact),
        cells=cells,
        static_kd=int(incremental_by_arm["static"]["key_dependent_bits"]),
        adaptive_kd=int(incremental_by_arm["adaptive"]["key_dependent_bits"]),
    )
    summary = _build_summary(
        results=results,
        planned=planned,
        seeds=seed_list,
        n=n,
        epsilon1=eps1,
        profile=profile,
        levels=levels,
        k2=k2,
        static_k1=int(d1_sets[-1].shape[0]),
        p2_maxdiff=p2_maxdiff,
        entropy=entropy,
        gates=gates,
        scientific=scientific,
        cells=cells,
        incremental=incremental,
        incremental_by_arm=incremental_by_arm,
        recount=recount,
        mismatches=mismatches,
        union_bound=union_bound,
        wall_s=wall_s,
        rss_bytes=rss_bytes,
        resource_stop_fired=resource_stop_fired,
        no_l2_exhaustion_blocks=no_l2_exhaustion_blocks,
    )
    plan = _build_plan(
        out_path=out_path,
        n=n,
        epsilon1=eps1,
        profile=profile,
        levels=levels,
        k2=k2,
        seeds=seed_list,
        blocks_per_seed=blocks,
        d1_sets=d1_sets,
        d2=d2,
        nested=nested,
        table_deviation=table_deviation,
        p2_maxdiff=p2_maxdiff,
        entropy=entropy,
        total_wall_s=total_cap,
    )
    transcript = {
        "arms": list(ARMS),
        "event_count": len(events),
        "event_types": dict(recount["event_types"]),
        "incremental": dict(incremental),
        "incremental_by_arm": {arm: dict(incremental_by_arm[arm]) for arm in ARMS},
        "recount": {
            "key_dependent_bits": int(recount["key_dependent_bits"]),
            "public_seed_bits": int(recount["public_seed_bits"]),
            "feedback_bits": int(recount["feedback_bits"]),
            "public_control_bits": int(recount["public_control_bits"]),
            "tag_invocations": int(recount["tag_invocations"]),
            "feedback_invocations": int(recount["feedback_invocations"]),
            "event_types": dict(recount["event_types"]),
            "by_arm": {arm: dict(recount["by_arm"][arm]) for arm in ARMS},
        },
        "mismatch_count": len(mismatches),
        "mismatches": list(mismatches),
        "public_control_bits_per_tag": tl.seed_bits_for(n),
        "fully_invoked_static_arm_bits": STATIC_FULLY_INVOKED_BITS,
        "fully_invoked_adaptive_arm_bits_by_level": {
            str(int(k)): DISCLOSED_BITS_PER_COORDINATE * (int(k) + int(k2)) + TAG_BITS
            for k in levels
        },
        "union_bound": union_bound,
        "union_bound_definition": "min(1.0, total_tag_invocations * 2**-64)",
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
    return AdaptiveGateRun(
        results=results,
        records=records,
        events=events,
        plan=plan,
        transcript=transcript,
        summary=summary,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-adaptive-l1-gate",
        description="NB-Polar Phase 4-P6 adaptive hard-L1 disclosure synthetic dev gate",
    )
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--epsilon1", required=True, type=float)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--k1-levels", required=True, type=int, nargs="+", dest="k1_levels")
    parser.add_argument("--k2", required=True, type=int)
    parser.add_argument("--seeds", required=True, type=int, nargs="+")
    parser.add_argument("--blocks-per-seed", required=True, type=int, dest="blocks_per_seed")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_adaptive_gate(
            n=args.n,
            epsilon1=args.epsilon1,
            profile=args.profile,
            k1_levels=args.k1_levels,
            k2=args.k2,
            seeds=args.seeds,
            blocks_per_seed=args.blocks_per_seed,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p6 adaptive gate refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "planned_pairs": summary["planned_pairs"],
                "cells": summary["cells"],
                "disclosure": summary["disclosure"],
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
