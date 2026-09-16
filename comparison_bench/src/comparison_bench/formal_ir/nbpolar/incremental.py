"""NB-Polar Phase 6 fixed incremental reconciliation protocol (synthetic only).

Frozen nested-disclosure schedule at the accepted Phase 5 point:

- GF32 polynomial basis, primitive polynomial 37, alpha 2, natural order;
- q-ary erasure channel, ``N=256``, ``epsilon=0.05``;
- worst-first order ``analytic_order(0.05, 256)`` with nested sizes
  ``K=(29, 33, 37, 41, 45)``; level ``i`` uses ``D_i = sorted(order[:K_i])``;
- level ``i`` publishes only the actual GF32 ``U`` values of the newly
  added coordinates ``D_i minus D_{i-1}`` (zeros are values, never
  sentinels); every coordinate is counted exactly once;
- every invoked level runs a fresh :func:`sc_decode` call on the SAME
  original Bob metric with the cumulative ``known_positions=D_i`` and
  ``known_values=U[D_i]``: no decoder state, belief, partial sum or hard
  decision crosses levels;
- every invoked level uses one independent 64-bit Toeplitz tag over the
  MSB-first 10-bit label expansion (``label_j = 32 * x_hat_j``, message
  domain ``10*N = 2560`` bits). A tag match accepts the current candidate
  and terminates the schedule. A mismatch discards that candidate and
  advances exactly to the next frozen level; there is no candidate
  ranking, no selection, no skip and no decoder-parameter change. A
  matching non-exact candidate is ``undetected`` and never success; a
  final-level mismatch is ``verify_failed``. A decode exception or
  nonfinite decision marginals at any invoked level stop the block
  fail-closed (no further levels) as ``decode_failed``. A block not
  executed because a preregistered budget stop fired is ``resource_abort``.

Accounting (``j`` = number of tag invocations on the block): a block
terminated at level ``j`` discloses ``5*K_j + 64*j`` key-dependent bits;
a ``decode_failed`` at level ``i`` (1-based) discloses
``5*K_i + 64*(i-1)``; ``resource_abort`` discloses 0. Each tag invocation
also consumes ``10*N + 63 = 2623`` public seed bits. Each level advance
emits one public feedback ``control`` event (``key_dependent_bits=0``,
``public_control_bits=1``) counted separately as
``feedback_control_invocations`` / ``feedback_control_bits`` and included
in the public-control total with the split reported. The verification
union bound is ``min(1.0, total_tag_invocations * 2**-64)`` over both
arms, with per-arm and total invocation counts; consistency with the
independent transcript recount is a hard gate.

Paired development mode runs the frozen static K=45 comparator and the
incremental schedule on one shared synthetic stream: for every block the
generator is called once and both arms consume the identical arrays in
the same order. The static comparator re-implements the accepted Phase 5
semantics thinly with this module's own seed derivation; it is an in-run
comparator and never reads the immutable Phase 5 evidence root.

Per-arm/per-block/per-level seeds come from an MSB-first SHA-256 counter
stream over ``"nbpolar-p6-toeplitz-seed:<master>:<arm>:<block_index>:
<level>:<counter>"`` truncated to ``10*N + 63`` bits and are public
control, never persisted raw. The level index is 0-based: the static
comparator uses level 0, the incremental schedule uses levels 0..4 for
the frozen sizes ``(29, 33, 37, 41, 45)``.

Phase 6-R1 adds one mode on top of the same frozen semantics: at the
non-final levels (K=29/33/37/41) an ``ImpossibleDisclosedValueError``
becomes ``decode_rejected_continue`` -- the intermediate rejection is
recorded, no candidate is created and no tag is invoked, exactly one
public feedback request is counted, the next fixed increment is disclosed
(cumulative set) and SC restarts from scratch on the ORIGINAL metric. At
the final level K=45 the same error stays terminal ``decode_failed``. No
other exception continues (``NumericNonfiniteError``, other
``ValueError``/``TypeError`` and nonfinite marginals stay fail-closed
terminal at any level). No decoder state, belief, partial sum or hard
decision crosses levels. The three-arm development mode runs the static
K=45 comparator, the strict-stop incremental arm and the R1 arm on the
identical per-block arrays and reports rescued/persisted/regressed/other
paired counts against the strict arm.

This module is synthetic-only: no stored evidence file, real-frame,
learned-policy, rate-adaptation, SCL/CRC or retry path, no import-time
I/O, no global RNG, and no output except the explicit dev-gate CLI below.
Truth isolation is enforced by an adversarial post-decision mutation
sentinel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from numbers import Integral
from pathlib import Path

import numpy as np

from ..shared import (
    canonical_event,
    toeplitz_tag,
    transcript_summary,
    verification_union_bound,
)
from .algebra import make_gf32, validate_symbols
from .construction import analytic_order
from .protocol import (
    DEFAULT_K,
    DEFAULT_N,
    EPSILON,
    LABEL_BITS,
    OUTCOMES,
    TAG_BITS,
    WILSON_Z,
    labels_from_symbols,
    labels_to_bits,
    static_disclosure_coordinates,
    wilson_lower_bound,
)
from .sc import ImpossibleDisclosedValueError, NumericNonfiniteError, sc_decode
from .synthetic import generate_erasure_block
from .transform import polar_transform

try:  # POSIX (the frozen command runs under WSL); Windows native has no resource module.
    import resource
except ImportError:  # pragma: no cover - exercised only on Windows native
    resource = None

PROTOCOL_NAME = "nbpolar-incremental-protocol"
MODE = "paired-dev-gate"
DEFAULT_Q = 32
ALPHA = 2

# Frozen Phase 6 schedule: strictly nested worst-first cumulative sizes.
FROZEN_K = (29, 33, 37, 41, 45)
FROZEN_BLOCKS = 300
MIN_EXACT = 285
WILSON_LB_MIN = 0.90
DISCLOSURE_SAVING_NUM = 95
DISCLOSURE_SAVING_DEN = 100

# Frozen seeds. 2026091340 is reserved for the single authorized paired
# 300-block attempt and is never used by tests; 2026091341 is the public
# Toeplitz master. Both were proven absent from HEAD and from every
# accepted/consumed Phase 1-5 stream before the freeze.
FROZEN_RUN_SEED = 2026091340
TOEPLITZ_MASTER_SEED = 2026091341
BANNED_RUN_SEEDS = (
    frozenset(range(2026091200, 2026091214))
    | frozenset(range(2026091314, 2026091321))
    | {2026091330}
)

# Phase 6-R1 three-arm decode-reject-advance development mode. The frozen
# point, schedule, order, decoder, tag domain, accounting and thresholds are
# the Phase 6 ones; only non-final impossible-disclosure handling differs.
THREE_ARM_MODE = "three-arm-paired-dev-gate"
R1_PROTOCOL_NAME = "nbpolar-decode-reject-advance-protocol"
R1_FROZEN_BLOCKS = 300
# Frozen R1 seeds. 2026091350 is reserved for the single authorized
# three-arm 300-block attempt and is never used by tests; 2026091351 is the
# R1 public Toeplitz master. Both were proven absent from HEAD and from every
# accepted/consumed Phase 1-6 stream before this freeze.
R1_RUN_SEED = 2026091350
R1_TOEPLITZ_MASTER_SEED = 2026091351
# R1 refuses every Phase 1-6 consumed seed plus 2026091321 and the two Phase 6
# evidence seeds 2026091340/2026091341. `BANNED_RUN_SEEDS` and
# `validate_run_seed` stay byte-pinned to Phase 6; R1 uses this extension.
R1_BANNED_RUN_SEEDS = BANNED_RUN_SEEDS | {2026091321, 2026091340, 2026091341}
# Seed namespace for both incremental arms: a block that never rejects is
# bit-identical between the strict-stop and R1 arms, so the paired comparison
# isolates the rejection delta. The static arm keeps its own namespace.
INCREMENTAL_SEED_ARM = "incremental"
R1_RESULT_ARM = "incremental_r1"

DISCLOSED_BITS_PER_COORDINATE = 5
LABEL_SCALE = 32
FEEDBACK_CONTROL_BITS = 1
MESSAGE_BITS = LABEL_BITS * DEFAULT_N  # 2560
SEED_BITS = MESSAGE_BITS + TAG_BITS - 1  # 2623 public control bits per tag
RSS_LIMIT_BYTES = 2 * 1024**3

# Budgets frozen from the paired N=256 profile (see P6_FREEZE.md, P6_IMPLEMENTATION_NOTES.md).
DEV_GATE_TOTAL_WALL_S = 600.0
DEV_GATE_PER_PAIRED_BLOCK_SOFT_CAP_S = 10.0

# Budgets frozen from the three-arm N=256 profile (60 injected blocks, seed
# 2026091399, temp root; see R1_FREEZE.md, R1_IMPLEMENTATION_NOTES.md):
# projected 300-block wall ~15.7 s mean / ~16.0 s p90; observed max paired
# block 121.6 ms; peak RSS ~103 MiB. Total = ~57x projected mean; per-block
# soft cap = ~123x observed max; external timeout T = 1800 s = 2x total.
THREE_ARM_TOTAL_WALL_S = 900.0
THREE_ARM_PER_PAIRED_BLOCK_SOFT_CAP_S = 15.0

ARMS = ("static", "incremental")

CLAIM_SCOPE = (
    "synthetic paired development signal only; this is not real-data FER, "
    "leakage efficiency, key rate, qualification or promotion evidence"
)


def _as_int(value, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer")
    out = int(value)
    if minimum is not None and out < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {out}")
    return out


def validate_run_seed(seed) -> int:
    """Return ``seed`` if usable for a Phase 6 run; refuse consumed seeds."""
    out = _as_int(seed, "run_seed", minimum=0)
    if out in BANNED_RUN_SEEDS:
        raise ValueError(f"run seed {out} is banned (consumed by Phase 1-5)")
    return out


def validate_r1_run_seed(seed) -> int:
    """Return ``seed`` if usable for the Phase 6-R1 three-arm run.

    This is the R1 extension of the banned-run-seed validator: it refuses
    every Phase 1-6 consumed seed plus 2026091321 and the two Phase 6
    evidence seeds 2026091340/2026091341. ``validate_run_seed`` stays
    byte-pinned to Phase 6 so predecessor behavior is unchanged.
    """
    out = _as_int(seed, "run_seed", minimum=0)
    if out in R1_BANNED_RUN_SEEDS:
        raise ValueError(f"run seed {out} is banned (consumed by Phase 1-6)")
    return out


def seed_bits_for(n: int) -> int:
    """Public Toeplitz seed length for block length ``n``: ``10*n + 63``."""
    return LABEL_BITS * _as_int(n, "n", minimum=1) + TAG_BITS - 1


def block_toeplitz_seed_bits(
    arm: str,
    block_index: int,
    level: int,
    bit_length: int | None = None,
    *,
    master: int | None = None,
) -> np.ndarray:
    """Deterministic public per-arm/per-block/per-level Toeplitz seed.

    Rule: concatenate SHA-256 over ``"nbpolar-p6-toeplitz-seed:<master>:
    <arm>:<block_index>:<level>:<counter>"`` for ``counter = 0, 1, ...``
    (ASCII decimal), unpack each digest MSB-first, and truncate to
    ``bit_length`` (default ``10*N + 63`` for the frozen point). Seed
    contents are public control and are never persisted. ``master``
    defaults to the Phase 6 public master; the R1 run passes 2026091351.
    """
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")
    index = _as_int(block_index, "block_index", minimum=0)
    lvl = _as_int(level, "level", minimum=0)
    master_seed = TOEPLITZ_MASTER_SEED if master is None else _as_int(master, "master", minimum=0)
    length = SEED_BITS if bit_length is None else _as_int(bit_length, "bit_length", minimum=1)
    prefix = f"nbpolar-p6-toeplitz-seed:{master_seed}:{arm}:{index}:{lvl}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < length:
        buf.extend(hashlib.sha256(f"{prefix}:{counter}".encode("ascii")).digest())
        counter += 1
    bits = np.unpackbits(np.frombuffer(bytes(buf), dtype=np.uint8), bitorder="big")
    return bits[:length].astype(np.uint8)


@dataclass(frozen=True, eq=False)
class NestedSchedule:
    """Frozen nested disclosure sets plus their structural proof flags."""

    n: int
    epsilon: float
    sizes: tuple
    sets: tuple
    new_positions: tuple
    order_prefix_matches: bool
    strict_nesting: bool
    new_coordinates_disjoint: bool


def build_nested_schedule(*, n: int = DEFAULT_N, epsilon: float = EPSILON, sizes=FROZEN_K) -> NestedSchedule:
    """Build ``D_i = sorted(analytic_order(epsilon, n)[:K_i])`` and prove nesting.

    ``sizes`` is a test-only parameterization hook; the frozen Phase 6 run
    always uses ``FROZEN_K`` and never searches or changes it.
    """
    n = _as_int(n, "n", minimum=1)
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    sizes_t = tuple(_as_int(k, "schedule size", minimum=1) for k in sizes)
    if not sizes_t:
        raise ValueError("schedule must contain at least one size")
    if any(b <= a for a, b in zip(sizes_t, sizes_t[1:])):
        raise ValueError("schedule sizes must be strictly increasing")
    if sizes_t[-1] > n:
        raise ValueError(f"schedule sizes must lie in 1..{n}, got {sizes_t[-1]}")
    order = analytic_order(float(epsilon), n)
    sets = tuple(np.sort(order[:k]).astype(np.int64) for k in sizes_t)
    new_positions = (sets[0],) + tuple(
        np.setdiff1d(sets[i], sets[i - 1]).astype(np.int64) for i in range(1, len(sets))
    )
    prefix_ok = all(
        np.array_equal(s, np.sort(order[:k]).astype(np.int64)) for s, k in zip(sets, sizes_t)
    )
    nesting_ok = all(
        len(sets[i]) < len(sets[i + 1]) and bool(np.isin(sets[i], sets[i + 1]).all())
        for i in range(len(sets) - 1)
    )
    flat = [int(v) for arr in new_positions for v in arr.tolist()]
    disjoint_ok = len(flat) == len(set(flat)) == len(sets[-1])
    return NestedSchedule(
        n=n,
        epsilon=float(epsilon),
        sizes=sizes_t,
        sets=sets,
        new_positions=new_positions,
        order_prefix_matches=bool(prefix_ok),
        strict_nesting=bool(nesting_ok),
        new_coordinates_disjoint=bool(disjoint_ok),
    )


def truth_isolation_sentinel(logp, decisions, truth_arrays) -> bool:
    """Adversarially mutate truth copies; True means Bob stayed bitwise unchanged.

    ``decisions`` and ``truth_arrays`` are parallel in-memory arrays. A
    decision that aliases a truth buffer changes under the mutation and is
    detected; the caller's statistical inputs are not modified.
    """
    metric_before = np.array(logp, copy=True)
    decisions_before = [np.array(d, copy=True) for d in decisions]
    for arr in truth_arrays:
        arr[...] = (arr + 1) % DEFAULT_Q
    unchanged = bool(np.array_equal(np.asarray(logp), metric_before))
    for decision, before in zip(decisions, decisions_before):
        if not np.array_equal(np.asarray(decision), before):
            unchanged = False
    return unchanged


@dataclass(frozen=True, eq=False)
class ArmBlockResult:
    """One attempted arm block. Symbol/label arrays are in-memory only."""

    block_index: int
    arm: str
    outcome: str
    exact: bool
    accepted_level: int  # 0-based accepted level; -1 when no level accepted
    decode_failed_level: int  # 0-based level whose decode failed; -1 otherwise
    levels_invoked: int
    tag_invocations: int
    feedback_control_invocations: int
    key_dependent_bits: int
    public_seed_bits: int
    feedback_control_bits: int
    public_control_bits: int
    nonfinite: bool
    truth_leak_violation: bool
    pre_symbol_errors: int
    pre_bit_errors: int
    symbol_errors: int
    bit_errors: int
    wall_s: float
    error_type: str | None = None
    u_hat: np.ndarray | None = None
    x_hat: np.ndarray | None = None
    labels_hat: np.ndarray | None = None
    # R1 only: intermediate decode-rejected levels (strict blocks leave both
    # empty/zero). A rejection is never a final outcome bucket.
    rejected_levels: tuple = ()
    decode_rejected_continue_count: int = 0


def _abort_result(block_index: int, arm: str) -> ArmBlockResult:
    return ArmBlockResult(
        block_index=block_index,
        arm=arm,
        outcome="resource_abort",
        exact=False,
        accepted_level=-1,
        decode_failed_level=-1,
        levels_invoked=0,
        tag_invocations=0,
        feedback_control_invocations=0,
        key_dependent_bits=0,
        public_seed_bits=0,
        feedback_control_bits=0,
        public_control_bits=0,
        nonfinite=False,
        truth_leak_violation=False,
        pre_symbol_errors=-1,
        pre_bit_errors=-1,
        symbol_errors=-1,
        bit_errors=-1,
        wall_s=0.0,
    )


def _validate_common(block_index, x, logp, field, n: int):
    n = _as_int(n, "n", minimum=1)
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    block_index = _as_int(block_index, "block_index", minimum=0)
    q = int(getattr(field, "q", 0))
    if q != DEFAULT_Q:
        raise ValueError(f"field q {q} != frozen {DEFAULT_Q}")
    x_arr = validate_symbols(x, q, name="x")
    if x_arr.shape[0] != n:
        raise ValueError(f"x must have length N={n}, got {x_arr.shape[0]}")
    logp_arr = np.asarray(logp, dtype=np.float64)
    if logp_arr.shape != (n, q):
        raise ValueError(f"logp must have shape ({n}, {q}), got {logp_arr.shape}")
    return block_index, x_arr, logp_arr, q


def run_incremental_block(
    block_index: int,
    x,
    logp,
    *,
    field,
    n: int = DEFAULT_N,
    sizes=FROZEN_K,
    nested: NestedSchedule | None = None,
    tag_fn=None,
) -> ArmBlockResult:
    """One fixed incremental block: nested disclosure, restart SC per level, per-level tag.

    Phase 6 strict-stop semantics, signature and behavior unchanged: any
    decode exception at any invoked level is terminal ``decode_failed``.
    ``tag_fn`` is a documented test-only seam; the production default is
    :func:`comparison_bench.src.comparison_bench.formal_ir.shared.toeplitz_tag`.
    """
    return _run_incremental_block_impl(
        block_index,
        x,
        logp,
        field=field,
        n=n,
        sizes=sizes,
        nested=nested,
        tag_fn=tag_fn,
        advance_on_reject=False,
        arm="incremental",
    )


def run_incremental_r1_block(
    block_index: int,
    x,
    logp,
    *,
    field,
    n: int = DEFAULT_N,
    sizes=FROZEN_K,
    nested: NestedSchedule | None = None,
    tag_fn=None,
) -> ArmBlockResult:
    """One R1 block: non-final impossible disclosure advances, everything else as Phase 6.

    At a non-final level an ``ImpossibleDisclosedValueError`` records an
    intermediate rejection (no candidate, no tag, one public feedback
    request) and the next frozen level restarts SC from scratch on the
    ORIGINAL metric. At the final level the same error stays terminal
    ``decode_failed``. No other exception continues. Both incremental arms
    share the ``incremental`` seed namespace so a non-rejecting block is
    bit-identical between strict and R1.
    """
    return _run_incremental_block_impl(
        block_index,
        x,
        logp,
        field=field,
        n=n,
        sizes=sizes,
        nested=nested,
        tag_fn=tag_fn,
        advance_on_reject=True,
        arm=R1_RESULT_ARM,
    )


def _run_incremental_block_impl(
    block_index: int,
    x,
    logp,
    *,
    field,
    n: int = DEFAULT_N,
    sizes=FROZEN_K,
    nested: NestedSchedule | None = None,
    tag_fn=None,
    advance_on_reject: bool,
    arm: str,
) -> ArmBlockResult:
    block_index, x_arr, logp_arr, q = _validate_common(block_index, x, logp, field, n)
    if tag_fn is None:
        tag_fn = toeplitz_tag
    if nested is None:
        nested = build_nested_schedule(n=n, sizes=sizes)
    if nested.n != n or tuple(nested.sizes) != tuple(sizes):
        raise ValueError("nested schedule does not match the requested n/sizes")

    x_truth = np.array(x_arr, copy=True)
    u_truth = polar_transform(x_truth, field=field, alpha=ALPHA)
    labels_true = labels_from_symbols(x_truth)
    labels_true_bits = labels_to_bits(labels_true)

    pre_symbols = np.argmax(logp_arr, axis=1).astype(np.int64)
    pre_labels = labels_from_symbols(pre_symbols)
    pre_symbol_errors = int(np.count_nonzero(pre_symbols != x_arr))
    pre_bit_errors = int(np.count_nonzero(labels_to_bits(pre_labels) != labels_true_bits))

    seed_length = seed_bits_for(n)
    levels = len(nested.sizes)
    decisions: list = []
    disclosed_list: list = []
    rejected_levels: list = []
    tag_invocations = 0
    feedback_control_invocations = 0
    levels_invoked = 0
    accepted_level = -1
    decode_failed_level = -1
    error_type = None
    nonfinite = False
    u_hat = x_hat = labels_hat = None
    outcome = None
    start = time.perf_counter()

    for level, positions in enumerate(nested.sets):
        levels_invoked += 1
        disclosed = np.array(u_truth[positions], copy=True)
        disclosed_list.append(disclosed)
        try:
            sc = sc_decode(
                logp_arr,
                field=field,
                alpha=ALPHA,
                known_positions=positions,
                known_values=disclosed,
            )
            if bool(np.isnan(sc.decision_metrics).any()) or bool(np.isposinf(sc.decision_metrics).any()):
                raise NumericNonfiniteError(
                    "numeric nonfinite failure: invalid decision marginals"
                )
        except ImpossibleDisclosedValueError as exc:
            # R1 delta only: at a NON-final level the intermediate rejection
            # advances. No candidate, no tag, one public feedback request;
            # the next iteration discloses the next fixed increment and calls
            # sc_decode fresh on the original metric.
            if advance_on_reject and level + 1 < levels:
                rejected_levels.append(level)
                feedback_control_invocations += 1
                continue
            decode_failed_level = level
            outcome = "decode_failed"
            error_type = type(exc).__name__
            break
        except Exception as exc:  # SC failure contract: fail closed, no further level, no tag
            decode_failed_level = level
            outcome = "decode_failed"
            nonfinite = (
                isinstance(exc, NumericNonfiniteError)
                or "nonfinite" in str(exc).lower()
                or "nan" in str(exc).lower()
            )
            error_type = type(exc).__name__
            break
        decisions.extend(
            [
                np.array(sc.decision_metrics, copy=True),
                np.array(sc.decision_log_scores, copy=True),
                np.array(sc.u_hat, copy=True),
                np.array(sc.x_hat, copy=True),
            ]
        )
        candidate_u = np.array(sc.u_hat, copy=True)
        candidate_x = np.array(sc.x_hat, copy=True)
        candidate_labels = labels_from_symbols(candidate_x)
        candidate_bits = labels_to_bits(candidate_labels)
        exact = bool(
            np.array_equal(candidate_u, u_truth) and np.array_equal(candidate_labels, labels_true)
        )
        seed = block_toeplitz_seed_bits(INCREMENTAL_SEED_ARM, block_index, level, seed_length)
        tag_invocations += 1
        tag_true = tag_fn(labels_true_bits, seed, TAG_BITS)
        tag_hat = tag_fn(candidate_bits, seed, TAG_BITS)
        if tag_true == tag_hat:
            outcome = "exact" if exact else "undetected"
            accepted_level = level
            u_hat, x_hat, labels_hat = candidate_u, candidate_x, candidate_labels
            break
        if level + 1 < levels:
            feedback_control_invocations += 1
    if outcome is None:
        outcome = "verify_failed"

    if outcome == "decode_failed":
        key_dependent_bits = (
            DISCLOSED_BITS_PER_COORDINATE * int(nested.sizes[decode_failed_level])
            + TAG_BITS * tag_invocations
        )
    else:
        terminal_level = accepted_level if accepted_level >= 0 else levels - 1
        key_dependent_bits = (
            DISCLOSED_BITS_PER_COORDINATE * int(nested.sizes[terminal_level])
            + TAG_BITS * tag_invocations
        )
    public_seed_bits = seed_length * tag_invocations
    feedback_control_bits = FEEDBACK_CONTROL_BITS * feedback_control_invocations
    public_control_bits = public_seed_bits + feedback_control_bits

    symbol_errors = -1
    bit_errors = -1
    if labels_hat is not None:
        symbol_errors = int(np.count_nonzero(labels_hat != labels_true))
        bit_errors = int(np.count_nonzero(labels_to_bits(labels_hat) != labels_true_bits))
    final_decisions = list(decisions)
    if u_hat is not None:
        final_decisions.extend([u_hat, x_hat, labels_hat])
    truth_isolated = truth_isolation_sentinel(
        logp_arr, final_decisions, [x_truth, u_truth] + disclosed_list
    )

    return ArmBlockResult(
        block_index=block_index,
        arm=arm,
        outcome=outcome,
        exact=bool(outcome == "exact"),
        accepted_level=accepted_level,
        decode_failed_level=decode_failed_level,
        levels_invoked=levels_invoked,
        tag_invocations=tag_invocations,
        feedback_control_invocations=feedback_control_invocations,
        key_dependent_bits=key_dependent_bits,
        public_seed_bits=public_seed_bits,
        feedback_control_bits=feedback_control_bits,
        public_control_bits=public_control_bits,
        nonfinite=nonfinite,
        truth_leak_violation=not truth_isolated,
        pre_symbol_errors=pre_symbol_errors,
        pre_bit_errors=pre_bit_errors,
        symbol_errors=symbol_errors,
        bit_errors=bit_errors,
        wall_s=time.perf_counter() - start,
        error_type=error_type,
        u_hat=u_hat,
        x_hat=x_hat,
        labels_hat=labels_hat,
        rejected_levels=tuple(rejected_levels),
        decode_rejected_continue_count=len(rejected_levels),
    )


def run_static_comparator_block(
    block_index: int,
    x,
    logp,
    *,
    field,
    n: int = DEFAULT_N,
    k: int = DEFAULT_K,
    tag_fn=None,
) -> ArmBlockResult:
    """The paired static K=45 comparator: Phase 5 semantics, Phase 6 seeds.

    One SC call on the frozen static set, at most one 64-bit Toeplitz
    verification, ``5*K + 64`` (or ``5*K`` on decode failure) key-dependent
    bits. This is an in-run comparator only; the immutable Phase 5 evidence
    root is never read.
    """
    block_index, x_arr, logp_arr, q = _validate_common(block_index, x, logp, field, n)
    k = _as_int(k, "k", minimum=0)
    if k > n:
        raise ValueError(f"k must lie in 0..{n}, got {k}")
    if tag_fn is None:
        tag_fn = toeplitz_tag
    positions = static_disclosure_coordinates(n, k)
    seed_length = seed_bits_for(n)

    x_truth = np.array(x_arr, copy=True)
    u_truth = polar_transform(x_truth, field=field, alpha=ALPHA)
    disclosed = np.array(u_truth[positions], copy=True)
    labels_true = labels_from_symbols(x_truth)
    labels_true_bits = labels_to_bits(labels_true)

    pre_symbols = np.argmax(logp_arr, axis=1).astype(np.int64)
    pre_labels = labels_from_symbols(pre_symbols)
    pre_symbol_errors = int(np.count_nonzero(pre_symbols != x_arr))
    pre_bit_errors = int(np.count_nonzero(labels_to_bits(pre_labels) != labels_true_bits))

    start = time.perf_counter()
    try:
        sc = sc_decode(
            logp_arr,
            field=field,
            alpha=ALPHA,
            known_positions=positions,
            known_values=disclosed,
        )
        if bool(np.isnan(sc.decision_metrics).any()) or bool(np.isposinf(sc.decision_metrics).any()):
            raise NumericNonfiniteError("numeric nonfinite failure: invalid decision marginals")
    except Exception as exc:  # SC failure contract: decode_failed, no tag
        return ArmBlockResult(
            block_index=block_index,
            arm="static",
            outcome="decode_failed",
            exact=False,
            accepted_level=-1,
            decode_failed_level=0,
            levels_invoked=1,
            tag_invocations=0,
            feedback_control_invocations=0,
            key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k,
            public_seed_bits=0,
            feedback_control_bits=0,
            public_control_bits=0,
            nonfinite=isinstance(exc, NumericNonfiniteError)
            or "nonfinite" in str(exc).lower()
            or "nan" in str(exc).lower(),
            truth_leak_violation=False,
            pre_symbol_errors=pre_symbol_errors,
            pre_bit_errors=pre_bit_errors,
            symbol_errors=-1,
            bit_errors=-1,
            wall_s=time.perf_counter() - start,
            error_type=type(exc).__name__,
        )

    u_hat = np.array(sc.u_hat, copy=True)
    x_hat = np.array(sc.x_hat, copy=True)
    labels_hat = labels_from_symbols(x_hat)
    labels_hat_bits = labels_to_bits(labels_hat)
    exact = bool(np.array_equal(u_hat, u_truth) and np.array_equal(labels_hat, labels_true))
    symbol_errors = int(np.count_nonzero(labels_hat != labels_true))
    bit_errors = int(np.count_nonzero(labels_hat_bits != labels_true_bits))

    seed = block_toeplitz_seed_bits("static", block_index, 0, seed_length)
    tag_true = tag_fn(labels_true_bits, seed, TAG_BITS)
    tag_hat = tag_fn(labels_hat_bits, seed, TAG_BITS)
    tag_pass = tag_true == tag_hat
    if not tag_pass:
        outcome = "verify_failed"
        accepted_level = -1
    elif exact:
        outcome = "exact"
        accepted_level = 0
    else:
        outcome = "undetected"
        accepted_level = 0

    truth_isolated = truth_isolation_sentinel(
        logp_arr,
        [sc.decision_metrics, sc.decision_log_scores, u_hat, x_hat, labels_hat],
        [x_truth, u_truth, disclosed],
    )
    return ArmBlockResult(
        block_index=block_index,
        arm="static",
        outcome=outcome,
        exact=bool(exact),
        accepted_level=accepted_level,
        decode_failed_level=-1,
        levels_invoked=1,
        tag_invocations=1,
        feedback_control_invocations=0,
        key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k + TAG_BITS,
        public_seed_bits=seed_length,
        feedback_control_bits=0,
        public_control_bits=seed_length,
        nonfinite=False,
        truth_leak_violation=not truth_isolated,
        pre_symbol_errors=pre_symbol_errors,
        pre_bit_errors=pre_bit_errors,
        symbol_errors=symbol_errors,
        bit_errors=bit_errors,
        wall_s=time.perf_counter() - start,
        u_hat=u_hat,
        x_hat=x_hat,
        labels_hat=labels_hat,
    )


def _rejections_consistent(result: ArmBlockResult, nested: NestedSchedule) -> bool:
    """R1 proof that recorded rejections are strictly increasing non-final levels."""
    rejected = tuple(result.rejected_levels)
    if int(result.decode_rejected_continue_count) != len(rejected):
        return False
    final_limit = len(nested.sizes) - 1
    for value in rejected:
        if isinstance(value, bool) or not isinstance(value, Integral):
            return False
        if int(value) < 0 or int(value) >= final_limit:
            return False
    return all(int(b) > int(a) for a, b in zip(rejected, rejected[1:]))


def incremental_record_consistent(
    result: ArmBlockResult, nested: NestedSchedule, *, advance_on_reject: bool = False
) -> bool:
    """Per-block schedule/accounting consistency proof for the incremental arm.

    ``advance_on_reject`` selects the R1 rules (intermediate rejections
    advance); the default is the strict-stop Phase 6 proof and requires that
    no rejection was recorded. The R1 branch additionally requires that the
    advance count equals the number of rejected levels and that tag seeding,
    key-dependent bits and terminating levels follow the frozen rules.
    """
    sizes = [int(v) for v in nested.sizes]
    levels = len(sizes)
    if result.outcome == "resource_abort":
        return (
            result.levels_invoked == 0
            and result.tag_invocations == 0
            and result.feedback_control_invocations == 0
            and result.key_dependent_bits == 0
            and result.public_control_bits == 0
            and int(result.decode_rejected_continue_count) == 0
            and tuple(result.rejected_levels) == ()
        )
    if result.public_seed_bits != seed_bits_for(nested.n) * result.tag_invocations:
        return False
    if result.feedback_control_bits != FEEDBACK_CONTROL_BITS * result.feedback_control_invocations:
        return False
    if result.public_control_bits != result.public_seed_bits + result.feedback_control_bits:
        return False
    if not advance_on_reject:
        if int(result.decode_rejected_continue_count) != 0 or tuple(result.rejected_levels) != ():
            return False
        if result.outcome == "decode_failed":
            level = result.decode_failed_level
            return (
                0 <= level < levels
                and result.levels_invoked == level + 1
                and result.tag_invocations == level
                and result.feedback_control_invocations == level
                and result.key_dependent_bits
                == DISCLOSED_BITS_PER_COORDINATE * sizes[level] + TAG_BITS * level
            )
        if result.outcome in ("exact", "undetected"):
            level = result.accepted_level
            return (
                0 <= level < levels
                and result.levels_invoked == level + 1
                and result.tag_invocations == level + 1
                and result.feedback_control_invocations == level
                and result.key_dependent_bits
                == DISCLOSED_BITS_PER_COORDINATE * sizes[level] + TAG_BITS * (level + 1)
            )
        if result.outcome == "verify_failed":
            return (
                result.accepted_level == -1
                and result.levels_invoked == levels
                and result.tag_invocations == levels
                and result.feedback_control_invocations == levels - 1
                and result.key_dependent_bits
                == DISCLOSED_BITS_PER_COORDINATE * sizes[-1] + TAG_BITS * levels
            )
        return False
    if not _rejections_consistent(result, nested):
        return False
    rejected = int(result.decode_rejected_continue_count)
    # Every invoked level is tagged or rejected, except a failing final level
    # which produces neither.
    terminal_extra = 1 if result.outcome == "decode_failed" else 0
    if result.levels_invoked != result.tag_invocations + rejected + terminal_extra:
        return False
    if result.feedback_control_invocations != result.levels_invoked - 1:
        return False
    if result.outcome == "decode_failed":
        level = result.decode_failed_level
        return (
            0 <= level < levels
            and all(int(v) < level for v in result.rejected_levels)
            and result.levels_invoked == level + 1
            and result.key_dependent_bits
            == DISCLOSED_BITS_PER_COORDINATE * sizes[level]
            + TAG_BITS * result.tag_invocations
        )
    if result.outcome in ("exact", "undetected"):
        level = result.accepted_level
        return (
            0 <= level < levels
            and all(int(v) < level for v in result.rejected_levels)
            and result.levels_invoked == level + 1
            and result.key_dependent_bits
            == DISCLOSED_BITS_PER_COORDINATE * sizes[level]
            + TAG_BITS * result.tag_invocations
        )
    if result.outcome == "verify_failed":
        return (
            result.accepted_level == -1
            and result.levels_invoked == levels
            and result.key_dependent_bits
            == DISCLOSED_BITS_PER_COORDINATE * sizes[-1] + TAG_BITS * result.tag_invocations
        )
    return False


def static_record_consistent(result: ArmBlockResult, n: int = DEFAULT_N, k: int = DEFAULT_K) -> bool:
    """Per-block accounting consistency proof for the static comparator arm."""
    if result.outcome == "resource_abort":
        return (
            result.levels_invoked == 0
            and result.tag_invocations == 0
            and result.key_dependent_bits == 0
            and result.public_control_bits == 0
        )
    if result.levels_invoked != 1 or result.feedback_control_invocations != 0:
        return False
    if result.outcome == "decode_failed":
        return (
            result.tag_invocations == 0
            and result.key_dependent_bits == DISCLOSED_BITS_PER_COORDINATE * k
            and result.public_seed_bits == 0
            and result.public_control_bits == 0
        )
    if result.outcome in ("exact", "undetected", "verify_failed"):
        return (
            result.tag_invocations == 1
            and result.key_dependent_bits == DISCLOSED_BITS_PER_COORDINATE * k + TAG_BITS
            and result.public_seed_bits == seed_bits_for(n)
            and result.public_control_bits == seed_bits_for(n)
        )
    return False


def _arm_record(result: ArmBlockResult) -> dict:
    """Compact scalar record; symbol/label vectors are never persisted."""
    return {
        "arm": result.arm,
        "block_index": int(result.block_index),
        "outcome": result.outcome,
        "exact": bool(result.exact),
        "accepted_level": int(result.accepted_level),
        "decode_failed_level": int(result.decode_failed_level),
        "levels_invoked": int(result.levels_invoked),
        "tag_invocations": int(result.tag_invocations),
        "feedback_control_invocations": int(result.feedback_control_invocations),
        "key_dependent_bits": int(result.key_dependent_bits),
        "public_seed_bits": int(result.public_seed_bits),
        "feedback_control_bits": int(result.feedback_control_bits),
        "public_control_bits": int(result.public_control_bits),
        "nonfinite": bool(result.nonfinite),
        "truth_leak_violation": bool(result.truth_leak_violation),
        "error_type": result.error_type,
        "pre_symbol_errors": int(result.pre_symbol_errors),
        "pre_bit_errors": int(result.pre_bit_errors),
        "symbol_errors": int(result.symbol_errors),
        "bit_errors": int(result.bit_errors),
        "wall_s": round(float(result.wall_s), 6),
    }


def terminating_level(result: ArmBlockResult, nested: NestedSchedule) -> int:
    """The 0-based level that terminated the block; -1 for ``resource_abort``."""
    if result.outcome == "resource_abort":
        return -1
    if result.outcome == "decode_failed":
        return int(result.decode_failed_level)
    if result.outcome in ("exact", "undetected"):
        return int(result.accepted_level)
    if result.outcome == "verify_failed":
        return len(nested.sizes) - 1
    return -1


def _r1_arm_record(result: ArmBlockResult, nested: NestedSchedule) -> dict:
    """Scalar-only R1 block record: base fields plus rejection/terminating facts."""
    record = _arm_record(result)
    level = terminating_level(result, nested)
    record["rejected_levels"] = [int(v) for v in result.rejected_levels]
    record["decode_rejected_continue_count"] = int(result.decode_rejected_continue_count)
    record["terminating_level"] = int(level)
    record["terminating_k"] = int(nested.sizes[level]) if level >= 0 else -1
    return record


def rescue_comparison(strict_results, r1_results) -> dict:
    """Frozen paired identities against the strict-stop arm.

    ``rescued = (strict != exact and r1 == exact)``; ``persisted = (strict
    outcome == r1 outcome)``; ``regressed = (strict == exact and r1 !=
    exact)``; ``other`` is the remainder (listed, expected empty). The four
    buckets partition the paired blocks.
    """
    if len(strict_results) != len(r1_results):
        raise ValueError("strict and R1 arm results must be paired one-to-one")
    rescued, persisted, regressed, other = [], [], [], []
    for strict, r1 in zip(strict_results, r1_results):
        if int(strict.block_index) != int(r1.block_index):
            raise ValueError("strict and R1 arm block indices differ")
        strict_exact = strict.outcome == "exact"
        r1_exact = r1.outcome == "exact"
        index = int(strict.block_index)
        if not strict_exact and r1_exact:
            rescued.append(index)
        elif strict.outcome == r1.outcome:
            persisted.append(index)
        elif strict_exact and not r1_exact:
            regressed.append(index)
        else:
            other.append(index)
    return {
        "rescued": len(rescued),
        "persisted": len(persisted),
        "regressed": len(regressed),
        "other": len(other),
        "rescued_block_indices": rescued,
        "persisted_block_indices": persisted,
        "regressed_block_indices": regressed,
        "other_block_indices": other,
        "partition_exhaustive": bool(
            len(rescued) + len(persisted) + len(regressed) + len(other) == len(strict_results)
        ),
    }


def _event(
    *,
    block_index: int,
    event_id: str,
    method: str,
    event_type: str,
    direction: str,
    parent_event_id: str | None,
    key_dependent_bits: int,
    public_control_bits: int,
    payload: dict,
) -> dict:
    event = {
        "event_id": event_id,
        "frame_key": f"nbpolar-p6-synthetic:{int(block_index)}",
        "method": method,
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


def static_block_events(result: ArmBlockResult, n: int = DEFAULT_N, k: int = DEFAULT_K) -> list:
    """Canonical public transcript events for one static comparator block."""
    if result.outcome == "resource_abort":
        return []
    frame_key = f"nbpolar-p6-synthetic:{int(result.block_index)}"
    events = []
    disclosure_id = f"block-{int(result.block_index)}-static-disclosure"
    events.append(
        _event(
            block_index=result.block_index,
            event_id=disclosure_id,
            method="nbpolar_static",
            event_type="static_disclosure",
            direction="alice_to_bob",
            parent_event_id=None,
            key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * int(k),
            public_control_bits=0,
            payload={},
        )
    )
    if result.tag_invocations:
        seed_length = seed_bits_for(n)
        events.append(
            _event(
                block_index=result.block_index,
                event_id=f"block-{int(result.block_index)}-static-verification",
                method="nbpolar_static",
                event_type="verification_tag",
                direction="alice_to_bob",
                parent_event_id=disclosure_id,
                key_dependent_bits=TAG_BITS,
                public_control_bits=seed_length,
                payload={"seed_bit_length": seed_length},
            )
        )
    return events


def incremental_block_events(
    result: ArmBlockResult, nested: NestedSchedule, *, advance_on_reject: bool = False
) -> list:
    """Canonical public transcript events for one incremental block.

    In R1 mode a decode-rejected level emitted a disclosure and a feedback
    control but no verification tag; tag events are placed on the
    non-rejected invoked levels in order. The strict default is unchanged.
    """
    if result.outcome == "resource_abort":
        return []
    seed_length = seed_bits_for(nested.n)
    events = []
    parent = None
    if advance_on_reject:
        rejected = {int(v) for v in result.rejected_levels}
        tags_left = int(result.tag_invocations)
        controls_left = int(result.feedback_control_invocations)
        for level in range(result.levels_invoked):
            rejected_here = level in rejected
            disclosure_id = f"block-{int(result.block_index)}-lvl-{level}-disclosure"
            events.append(
                _event(
                    block_index=result.block_index,
                    event_id=disclosure_id,
                    method="nbpolar_incremental_r1",
                    event_type="incremental_disclosure",
                    direction="alice_to_bob",
                    parent_event_id=parent,
                    key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE
                    * int(len(nested.new_positions[level])),
                    public_control_bits=0,
                    payload={},
                )
            )
            parent = disclosure_id
            if not rejected_here and tags_left > 0:
                verification_id = f"block-{int(result.block_index)}-lvl-{level}-verification"
                events.append(
                    _event(
                        block_index=result.block_index,
                        event_id=verification_id,
                        method="nbpolar_incremental_r1",
                        event_type="verification_tag",
                        direction="alice_to_bob",
                        parent_event_id=parent,
                        key_dependent_bits=TAG_BITS,
                        public_control_bits=seed_length,
                        payload={"seed_bit_length": seed_length},
                    )
                )
                parent = verification_id
                tags_left -= 1
            if level + 1 < result.levels_invoked and controls_left > 0:
                control_id = f"block-{int(result.block_index)}-lvl-{level}-control"
                events.append(
                    _event(
                        block_index=result.block_index,
                        event_id=control_id,
                        method="nbpolar_incremental_r1",
                        event_type="control",
                        direction="control",
                        parent_event_id=parent,
                        key_dependent_bits=0,
                        public_control_bits=FEEDBACK_CONTROL_BITS,
                        payload={
                            "reason": (
                                "decode_rejected_advance_next_level"
                                if rejected_here
                                else "tag_mismatch_advance_next_level"
                            )
                        },
                    )
                )
                parent = control_id
                controls_left -= 1
        return events
    for level in range(result.levels_invoked):
        disclosure_id = f"block-{int(result.block_index)}-lvl-{level}-disclosure"
        events.append(
            _event(
                block_index=result.block_index,
                event_id=disclosure_id,
                method="nbpolar_incremental",
                event_type="incremental_disclosure",
                direction="alice_to_bob",
                parent_event_id=parent,
                key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE
                * int(len(nested.new_positions[level])),
                public_control_bits=0,
                payload={},
            )
        )
        parent = disclosure_id
        if level < result.tag_invocations:
            verification_id = f"block-{int(result.block_index)}-lvl-{level}-verification"
            events.append(
                _event(
                    block_index=result.block_index,
                    event_id=verification_id,
                    method="nbpolar_incremental",
                    event_type="verification_tag",
                    direction="alice_to_bob",
                    parent_event_id=parent,
                    key_dependent_bits=TAG_BITS,
                    public_control_bits=seed_length,
                    payload={"seed_bit_length": seed_length},
                )
            )
            parent = verification_id
        if level < result.feedback_control_invocations:
            control_id = f"block-{int(result.block_index)}-lvl-{level}-control"
            events.append(
                _event(
                    block_index=result.block_index,
                    event_id=control_id,
                    method="nbpolar_incremental",
                    event_type="control",
                    direction="control",
                    parent_event_id=parent,
                    key_dependent_bits=0,
                    public_control_bits=FEEDBACK_CONTROL_BITS,
                    payload={"reason": "tag_mismatch_advance_next_level"},
                )
            )
            parent = control_id
    return events


def recount_transcript(events) -> dict:
    """Independent literal recount; does not reuse ``transcript_summary``."""
    key_dependent = 0
    public_control = 0
    verification_invocations = 0
    feedback_control_invocations = 0
    for event in events:
        key_dependent += int(event["key_dependent_bits"])
        public_control += int(event["public_control_bits"])
        if event["event_type"] == "verification_tag":
            verification_invocations += 1
        if event["event_type"] == "control":
            feedback_control_invocations += 1
    return {
        "key_dependent_bits": key_dependent,
        "public_control_bits": public_control,
        "verification_invocations": verification_invocations,
        "feedback_control_invocations": feedback_control_invocations,
    }


def _incremental_totals(results) -> dict:
    return {
        "key_dependent_bits": sum(int(r.key_dependent_bits) for r in results),
        "public_seed_bits": sum(int(r.public_seed_bits) for r in results),
        "feedback_control_bits": sum(int(r.feedback_control_bits) for r in results),
        "public_control_bits": sum(int(r.public_control_bits) for r in results),
        "verification_invocations": sum(int(r.tag_invocations) for r in results),
        "feedback_control_invocations": sum(
            int(r.feedback_control_invocations) for r in results
        ),
    }


def _outcome_counts(results) -> dict:
    counts = {name: 0 for name in OUTCOMES}
    for result in results:
        counts[result.outcome] += 1
    return counts


def _peak_rss_bytes() -> int | None:
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _abort_pair(block_index: int, records: list, static_results: list, incremental_results: list, nested) -> None:
    static_results.append(_abort_result(block_index, "static"))
    incremental_results.append(_abort_result(block_index, "incremental"))
    records.append(
        {
            "block_index": int(block_index),
            "paired_match": True,
            "metric_wall_s": 0.0,
            "static_wall_s": 0.0,
            "incremental_wall_s": 0.0,
            "paired_wall_s": 0.0,
            "static": _arm_record(static_results[-1]),
            "incremental": _arm_record(incremental_results[-1]),
        }
    )


def run_paired_block(
    block_index: int,
    x,
    logp,
    *,
    field,
    n: int = DEFAULT_N,
    sizes=FROZEN_K,
    static_k: int = DEFAULT_K,
    nested: NestedSchedule | None = None,
    tag_fn=None,
) -> dict:
    """Run both arms on identical arrays and prove the metric was not mutated."""
    if nested is None:
        nested = build_nested_schedule(n=n, sizes=sizes)
    snap_x = np.array(np.asarray(x), copy=True)
    snap_logp = np.array(np.asarray(logp), copy=True)
    static = run_static_comparator_block(
        block_index, x, logp, field=field, n=n, k=static_k, tag_fn=tag_fn
    )
    static_ok = bool(
        np.array_equal(np.asarray(x), snap_x) and np.array_equal(np.asarray(logp), snap_logp)
    )
    incremental = run_incremental_block(
        block_index, x, logp, field=field, n=n, sizes=sizes, nested=nested, tag_fn=tag_fn
    )
    incremental_ok = bool(
        np.array_equal(np.asarray(x), snap_x) and np.array_equal(np.asarray(logp), snap_logp)
    )
    return {
        "block_index": int(block_index),
        "paired_match": bool(static_ok and incremental_ok),
        "metric_wall_s": 0.0,
        "static_wall_s": round(float(static.wall_s), 6),
        "incremental_wall_s": round(float(incremental.wall_s), 6),
        "paired_wall_s": 0.0,
        "static_result": static,
        "incremental_result": incremental,
        "nested": nested,
    }


def run_three_arm_block(
    block_index: int,
    x,
    logp,
    *,
    field,
    n: int = DEFAULT_N,
    sizes=FROZEN_K,
    static_k: int = DEFAULT_K,
    nested: NestedSchedule | None = None,
    tag_fn=None,
) -> dict:
    """Run static K45, strict-stop and R1 arms on identical arrays, in order.

    The three arms consume the same ``(x, logp)`` objects in the frozen order
    (static, strict-stop, R1); ``paired_match`` is false if any arm mutated
    either input.
    """
    if nested is None:
        nested = build_nested_schedule(n=n, sizes=sizes)
    snap_x = np.array(np.asarray(x), copy=True)
    snap_logp = np.array(np.asarray(logp), copy=True)

    def unchanged() -> bool:
        return bool(
            np.array_equal(np.asarray(x), snap_x) and np.array_equal(np.asarray(logp), snap_logp)
        )

    pair_start = time.perf_counter()
    static = run_static_comparator_block(
        block_index, x, logp, field=field, n=n, k=static_k, tag_fn=tag_fn
    )
    static_ok = unchanged()
    strict = run_incremental_block(
        block_index, x, logp, field=field, n=n, sizes=sizes, nested=nested, tag_fn=tag_fn
    )
    strict_ok = unchanged()
    r1 = run_incremental_r1_block(
        block_index, x, logp, field=field, n=n, sizes=sizes, nested=nested, tag_fn=tag_fn
    )
    r1_ok = unchanged()
    return {
        "block_index": int(block_index),
        "paired_match": bool(static_ok and strict_ok and r1_ok),
        "metric_wall_s": 0.0,
        "static_wall_s": round(float(static.wall_s), 6),
        "strict_wall_s": round(float(strict.wall_s), 6),
        "r1_wall_s": round(float(r1.wall_s), 6),
        "three_arm_wall_s": round(time.perf_counter() - pair_start, 6),
        "static_result": static,
        "strict_result": strict,
        "r1_result": r1,
        "nested": nested,
    }


def _abort_three_arm(
    block_index: int,
    records: list,
    static_results: list,
    strict_results: list,
    r1_results: list,
    nested: NestedSchedule,
) -> None:
    static_results.append(_abort_result(block_index, "static"))
    strict_results.append(_abort_result(block_index, "incremental"))
    r1_results.append(_abort_result(block_index, R1_RESULT_ARM))
    records.append(
        {
            "block_index": int(block_index),
            "paired_match": True,
            "metric_wall_s": 0.0,
            "static_wall_s": 0.0,
            "strict_wall_s": 0.0,
            "r1_wall_s": 0.0,
            "three_arm_wall_s": 0.0,
            "static": _r1_arm_record(static_results[-1], nested),
            "strict_stop": _r1_arm_record(strict_results[-1], nested),
            "r1": _r1_arm_record(r1_results[-1], nested),
        }
    )


def _build_plan(*, run_seed, blocks, nested, total_cap, block_cap) -> dict:
    return {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "run_seed": int(run_seed),
        "planned_blocks": int(blocks),
        "q": DEFAULT_Q,
        "n": int(nested.n),
        "epsilon": float(nested.epsilon),
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "channel": "q-ary erasure; observed symbol one-hot posterior, erased symbol uniform",
        "order": "analytic_order(0.05, 256), worst-first (descending erasure probability, ties by index)",
        "schedule": {
            "K": [int(v) for v in nested.sizes],
            "D_sets": [[int(v) for v in arr.tolist()] for arr in nested.sets],
            "new_coordinates": [[int(v) for v in arr.tolist()] for arr in nested.new_positions],
            "strict_nesting": bool(nested.strict_nesting),
            "order_prefix_matches": bool(nested.order_prefix_matches),
            "new_coordinates_disjoint": bool(nested.new_coordinates_disjoint),
        },
        "static_comparator": {
            "K": DEFAULT_K,
            "D": [int(v) for v in static_disclosure_coordinates(nested.n, DEFAULT_K)],
            "disclosure_rule": "publish actual U[D] values including zeros; the decoder receives the known set sorted(D)",
            "restarts_per_block": 1,
        },
        "disclosure_rule": (
            "level i publishes only actual GF32 U values of D_i minus D_{i-1} (zeros are "
            "values); the decoder receives the cumulative known set D_i with those actual "
            "values; each coordinate is counted once"
        ),
        "restart_rule": "every invoked level runs a fresh sc_decode on the same original Bob metric",
        "label_domain": {
            "packing": "single-layer 10-bit embedding: high five bits carry the GF32 symbol, low five bits zero",
            "bits_per_label": LABEL_BITS,
            "message_bits": LABEL_BITS * int(nested.n),
            "single_layer_low_half_constant_zero": True,
        },
        "toeplitz": {
            "tag_bits": TAG_BITS,
            "master_seed": TOEPLITZ_MASTER_SEED,
            "derivation": (
                "MSB-first unpack of SHA-256('nbpolar-p6-toeplitz-seed:<master>:<arm>:"
                "<block_index>:<level>:<counter>') concatenated over counter=0,1,...; "
                "truncated to seed_bits; level index 0-based (static level 0, incremental "
                "levels 0..4); public control, never persisted raw"
            ),
            "seed_bits": seed_bits_for(nested.n),
        },
        "accounting": {
            "disclosed_bits_per_coordinate": DISCLOSED_BITS_PER_COORDINATE,
            "formula_terminated": "5*K_j + 64*j (j = tag invocations)",
            "formula_decode_failed_at_level_i_1based": "5*K_i + 64*(i-1)",
            "formula_resource_abort": 0,
            "feedback_control_bits_per_advance": FEEDBACK_CONTROL_BITS,
        },
        "union_bound": "min(1.0, total_tag_invocations * 2**-64)",
        "outcome_precedence": [
            "resource_abort: block not executed (preregistered budget stop)",
            "decode_failed: SC exception or nonfinite marginals at an invoked level; stop fail-closed",
            "verify_failed: final-level tag mismatch after all frozen levels",
            "exact: tag match and the candidate equals Alice source word with equal label vectors",
            "undetected: tag match and not exact (never success)",
        ],
        "budget": {
            "total_wall_s": float(total_cap),
            "per_paired_block_soft_cap_s": float(block_cap),
            "rss_bytes_max": RSS_LIMIT_BYTES,
        },
        "refused_run_seeds": sorted(int(v) for v in BANNED_RUN_SEEDS),
        "attempt_consumption_point": "first scientific sc_decode call of the paired run (static comparator, block 0)",
    }


def _candidate_gates(
    *,
    run_seed,
    blocks,
    paired_records,
    static_results,
    incremental_results,
    nested,
    resource_stop_fired,
    static_recount,
    incremental_recount,
    static_totals,
    incremental_totals,
) -> dict:
    static_counts = _outcome_counts(static_results)
    incremental_counts = _outcome_counts(incremental_results)
    static_attempted = blocks - static_counts["resource_abort"]
    incremental_attempted = blocks - incremental_counts["resource_abort"]
    static_key = static_totals["key_dependent_bits"]
    incremental_key = incremental_totals["key_dependent_bits"]
    incremental_exact = incremental_counts["exact"]
    incremental_wilson = wilson_lower_bound(incremental_exact, incremental_attempted)
    total_tag_invocations = (
        static_totals["verification_invocations"] + incremental_totals["verification_invocations"]
    )
    recount_total_tags = (
        static_recount["verification_invocations"] + incremental_recount["verification_invocations"]
    )
    static_mismatch = sum(
        1
        for field_name in (
            "key_dependent_bits",
            "public_control_bits",
            "verification_invocations",
            "feedback_control_invocations",
        )
        if static_totals[field_name] != static_recount[field_name]
    )
    incremental_mismatch = sum(
        1
        for field_name in (
            "key_dependent_bits",
            "public_control_bits",
            "verification_invocations",
            "feedback_control_invocations",
        )
        if incremental_totals[field_name] != incremental_recount[field_name]
    )
    schedule_consistent = bool(
        nested.order_prefix_matches
        and nested.strict_nesting
        and nested.new_coordinates_disjoint
        and all(incremental_record_consistent(r, nested) for r in incremental_results)
        and all(static_record_consistent(r, nested.n, DEFAULT_K) for r in static_results)
    )
    plan_identity = (
        int(run_seed) == FROZEN_RUN_SEED
        and int(blocks) == FROZEN_BLOCKS
        and int(nested.n) == DEFAULT_N
        and tuple(int(v) for v in nested.sizes) == tuple(FROZEN_K)
        and float(nested.epsilon) == float(EPSILON)
    )
    gates = {
        "frozen_plan_identity": bool(plan_identity),
        "paired_identical_blocks": bool(
            len(paired_records) == blocks and all(bool(r["paired_match"]) for r in paired_records)
        ),
        "outcome_buckets_disjoint_exhaustive_both_arms": bool(
            sum(static_counts.values()) == blocks and sum(incremental_counts.values()) == blocks
        ),
        "paired_coverage_complete": bool(
            static_attempted == blocks and incremental_attempted == blocks
        ),
        "incremental_undetected_zero": bool(incremental_counts["undetected"] == 0),
        "incremental_exact_ge_285": bool(incremental_exact >= MIN_EXACT),
        "incremental_wilson_lower_ge_0_90": bool(incremental_wilson >= WILSON_LB_MIN),
        "equal_attempted_denominators": bool(static_attempted == incremental_attempted),
        "incremental_avg_key_dependent_le_95pct_static": bool(
            static_attempted == incremental_attempted
            and incremental_key * DISCLOSURE_SAVING_DEN <= DISCLOSURE_SAVING_NUM * static_key
        ),
        "frozen_order_nesting_and_schedule_consistency": bool(schedule_consistent),
        "invocation_universe_equals_recount_both_arms": bool(
            static_recount["verification_invocations"]
            == static_totals["verification_invocations"]
            and incremental_recount["verification_invocations"]
            == incremental_totals["verification_invocations"]
            and incremental_recount["feedback_control_invocations"]
            == incremental_totals["feedback_control_invocations"]
        ),
        "union_bound_consistent": bool(
            total_tag_invocations == recount_total_tags
            and verification_union_bound(total_tag_invocations) == verification_union_bound(recount_total_tags)
            and verification_union_bound(static_totals["verification_invocations"])
            == verification_union_bound(static_recount["verification_invocations"])
            and verification_union_bound(incremental_totals["verification_invocations"])
            == verification_union_bound(incremental_recount["verification_invocations"])
        ),
        "recount_zero_mismatch": bool(static_mismatch == 0 and incremental_mismatch == 0),
        "truth_leak_zero": bool(
            all(not r.truth_leak_violation for r in static_results)
            and all(not r.truth_leak_violation for r in incremental_results)
        ),
        "nonfinite_zero": bool(
            all(not r.nonfinite for r in static_results)
            and all(not r.nonfinite for r in incremental_results)
        ),
        "resource_stop_preregistered": bool(
            (static_counts["resource_abort"] == 0 and incremental_counts["resource_abort"] == 0)
            or resource_stop_fired
        ),
        "feedback_control_counted": bool(
            incremental_totals["feedback_control_invocations"]
            == incremental_recount["feedback_control_invocations"]
            and incremental_totals["feedback_control_bits"]
            == FEEDBACK_CONTROL_BITS * incremental_totals["feedback_control_invocations"]
            and incremental_totals["public_control_bits"]
            == incremental_totals["public_seed_bits"]
            + incremental_totals["feedback_control_bits"]
        ),
        "public_control_counted": bool(
            static_totals["public_control_bits"] == static_recount["public_control_bits"]
            and static_totals["public_control_bits"] == static_totals["public_seed_bits"]
            and incremental_totals["public_control_bits"]
            == incremental_recount["public_control_bits"]
        ),
    }
    return {
        "gates": gates,
        "static_counts": static_counts,
        "incremental_counts": incremental_counts,
        "static_attempted": static_attempted,
        "incremental_attempted": incremental_attempted,
        "incremental_wilson": incremental_wilson,
        "static_mismatch": static_mismatch,
        "incremental_mismatch": incremental_mismatch,
        "total_tag_invocations": total_tag_invocations,
        "recount_total_tags": recount_total_tags,
    }


def run_paired_dev_gate(
    *,
    run_seed,
    blocks,
    out_root,
    total_wall_s: float | None = None,
    per_paired_block_soft_cap_s: float | None = None,
):
    """Execute the paired development gate and write exactly five compact files.

    Refuses an existing output root and a banned run seed before any
    decoder call. The frozen command passes ``run_seed=2026091340``,
    ``blocks=300`` and the absent output root below.
    """
    out_path = Path(out_root)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    seed = validate_run_seed(run_seed)
    blocks = _as_int(blocks, "blocks", minimum=1)
    n = DEFAULT_N
    sizes = FROZEN_K
    total_cap = DEV_GATE_TOTAL_WALL_S if total_wall_s is None else float(total_wall_s)
    block_cap = (
        DEV_GATE_PER_PAIRED_BLOCK_SOFT_CAP_S
        if per_paired_block_soft_cap_s is None
        else float(per_paired_block_soft_cap_s)
    )
    field = make_gf32()
    nested = build_nested_schedule(n=n, epsilon=EPSILON, sizes=sizes)
    rng = np.random.default_rng(seed)

    static_results: list = []
    incremental_results: list = []
    paired_records: list = []
    static_events: list = []
    incremental_events: list = []
    resource_stop_fired = False
    start = time.perf_counter()

    for block_index in range(blocks):
        if time.perf_counter() - start > total_cap:
            resource_stop_fired = True
            for remaining in range(block_index, blocks):
                _abort_pair(remaining, paired_records, static_results, incremental_results, nested)
            break
        metric_start = time.perf_counter()
        x, _y, logp = generate_erasure_block(rng, DEFAULT_Q, n, EPSILON)
        metric_wall = time.perf_counter() - metric_start
        snap_x = np.array(x, copy=True)
        snap_logp = np.array(logp, copy=True)
        pair_start = time.perf_counter()
        static = run_static_comparator_block(block_index, x, logp, field=field, n=n, k=DEFAULT_K)
        static_ok = bool(np.array_equal(x, snap_x) and np.array_equal(logp, snap_logp))
        incremental = run_incremental_block(
            block_index, x, logp, field=field, n=n, sizes=sizes, nested=nested
        )
        incremental_ok = bool(
            np.array_equal(x, snap_x) and np.array_equal(logp, snap_logp)
        )
        paired_wall = time.perf_counter() - pair_start
        static_results.append(static)
        incremental_results.append(incremental)
        static_events.extend(static_block_events(static, n, DEFAULT_K))
        incremental_events.extend(incremental_block_events(incremental, nested))
        paired_records.append(
            {
                "block_index": int(block_index),
                "paired_match": bool(static_ok and incremental_ok),
                "metric_wall_s": round(float(metric_wall), 6),
                "static_wall_s": round(float(static.wall_s), 6),
                "incremental_wall_s": round(float(incremental.wall_s), 6),
                "paired_wall_s": round(float(paired_wall), 6),
                "static": _arm_record(static),
                "incremental": _arm_record(incremental),
            }
        )
        if paired_wall > block_cap:
            resource_stop_fired = True
            for remaining in range(block_index + 1, blocks):
                _abort_pair(remaining, paired_records, static_results, incremental_results, nested)
            break

    static_recount = recount_transcript(static_events)
    incremental_recount = recount_transcript(incremental_events)
    static_totals = _incremental_totals(static_results)
    incremental_totals = _incremental_totals(incremental_results)
    gate_bundle = _candidate_gates(
        run_seed=seed,
        blocks=blocks,
        paired_records=paired_records,
        static_results=static_results,
        incremental_results=incremental_results,
        nested=nested,
        resource_stop_fired=resource_stop_fired,
        static_recount=static_recount,
        incremental_recount=incremental_recount,
        static_totals=static_totals,
        incremental_totals=incremental_totals,
    )
    gates = gate_bundle["gates"]
    wall_s = time.perf_counter() - start
    static_wilson = wilson_lower_bound(
        gate_bundle["static_counts"]["exact"], gate_bundle["static_attempted"]
    )
    incremental_wilson = gate_bundle["incremental_wilson"]
    static_key = static_totals["key_dependent_bits"]
    incremental_key = incremental_totals["key_dependent_bits"]
    union_bound = {
        "static_tag_invocations": int(static_totals["verification_invocations"]),
        "incremental_tag_invocations": int(incremental_totals["verification_invocations"]),
        "total_tag_invocations": int(gate_bundle["total_tag_invocations"]),
        "recount_total_tag_invocations": int(gate_bundle["recount_total_tags"]),
        "static": verification_union_bound(static_totals["verification_invocations"]),
        "incremental": verification_union_bound(incremental_totals["verification_invocations"]),
        "total": verification_union_bound(gate_bundle["total_tag_invocations"]),
    }
    public_control = {
        "static_seed_bits": int(static_totals["public_seed_bits"]),
        "incremental_seed_bits": int(incremental_totals["public_seed_bits"]),
        "incremental_feedback_control_invocations": int(
            incremental_totals["feedback_control_invocations"]
        ),
        "incremental_feedback_control_bits": int(incremental_totals["feedback_control_bits"]),
        "total_public_control_bits": int(
            static_totals["public_control_bits"] + incremental_totals["public_control_bits"]
        ),
        "incremental_split": {
            "seed_bits": int(incremental_totals["public_seed_bits"]),
            "feedback_control_bits": int(incremental_totals["feedback_control_bits"]),
        },
    }
    aggregate = {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "run_seed": int(seed),
        "planned_blocks": int(blocks),
        "completed_blocks": int(len(paired_records)),
        "q": DEFAULT_Q,
        "n": int(n),
        "epsilon": float(EPSILON),
        "schedule_sizes": [int(v) for v in sizes],
        "static_k": DEFAULT_K,
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_peak": _peak_rss_bytes(),
        "resource_stop_fired": bool(resource_stop_fired),
        "static": {
            "outcome_totals": {k: int(v) for k, v in gate_bundle["static_counts"].items()},
            "attempted": int(gate_bundle["static_attempted"]),
            "coverage": round(gate_bundle["static_attempted"] / blocks, 9),
            "key_dependent_bits_total": int(static_key),
            "average_key_dependent_bits_per_attempted_block": round(
                (static_key / gate_bundle["static_attempted"]) if gate_bundle["static_attempted"] else 0.0,
                9,
            ),
            "public_seed_bits_total": int(static_totals["public_seed_bits"]),
            "feedback_control_bits_total": int(static_totals["feedback_control_bits"]),
            "public_control_bits_total": int(static_totals["public_control_bits"]),
            "tag_invocations_total": int(static_totals["verification_invocations"]),
            "wilson": {
                "confidence": "one-sided 95%",
                "z": WILSON_Z,
                "successes": int(gate_bundle["static_counts"]["exact"]),
                "denominator": int(gate_bundle["static_attempted"]),
                "lower_bound": static_wilson,
            },
        },
        "incremental": {
            "outcome_totals": {k: int(v) for k, v in gate_bundle["incremental_counts"].items()},
            "attempted": int(gate_bundle["incremental_attempted"]),
            "coverage": round(gate_bundle["incremental_attempted"] / blocks, 9),
            "key_dependent_bits_total": int(incremental_key),
            "average_key_dependent_bits_per_attempted_block": round(
                (incremental_key / gate_bundle["incremental_attempted"])
                if gate_bundle["incremental_attempted"]
                else 0.0,
                9,
            ),
            "public_seed_bits_total": int(incremental_totals["public_seed_bits"]),
            "feedback_control_bits_total": int(incremental_totals["feedback_control_bits"]),
            "public_control_bits_total": int(incremental_totals["public_control_bits"]),
            "tag_invocations_total": int(incremental_totals["verification_invocations"]),
            "feedback_control_invocations_total": int(
                incremental_totals["feedback_control_invocations"]
            ),
            "wilson": {
                "confidence": "one-sided 95%",
                "z": WILSON_Z,
                "successes": int(gate_bundle["incremental_counts"]["exact"]),
                "denominator": int(gate_bundle["incremental_attempted"]),
                "lower_bound": incremental_wilson,
            },
        },
        "disclosure_comparison": {
            "static_key_dependent_total": int(static_key),
            "incremental_key_dependent_total": int(incremental_key),
            "static_attempted": int(gate_bundle["static_attempted"]),
            "incremental_attempted": int(gate_bundle["incremental_attempted"]),
            "integer_rule": "incremental_total * 100 <= 95 * static_total",
            "lhs": int(incremental_key) * DISCLOSURE_SAVING_DEN,
            "rhs": DISCLOSURE_SAVING_NUM * int(static_key),
            "saving_fraction": round(
                ((static_key - incremental_key) / static_key) if static_key else 0.0, 9
            ),
        },
        "union_bound": union_bound,
        "public_control": public_control,
        "transcript": {
            "static_event_count": len(static_events),
            "incremental_event_count": len(incremental_events),
            "static_recount": dict(static_recount),
            "incremental_recount": dict(incremental_recount),
            "static_mismatch_count": int(gate_bundle["static_mismatch"]),
            "incremental_mismatch_count": int(gate_bundle["incremental_mismatch"]),
            "static_transcript_sha256": transcript_summary(static_events)["transcript_sha256"],
            "incremental_transcript_sha256": transcript_summary(incremental_events)[
                "transcript_sha256"
            ],
        },
        "truth_leak_count": {
            "static": int(sum(1 for r in static_results if r.truth_leak_violation)),
            "incremental": int(sum(1 for r in incremental_results if r.truth_leak_violation)),
        },
        "nonfinite_count": {
            "static": int(sum(1 for r in static_results if r.nonfinite)),
            "incremental": int(sum(1 for r in incremental_results if r.nonfinite)),
        },
        "decode_error_types": {
            "static": {
                r.error_type: sum(1 for q in static_results if q.error_type == r.error_type)
                for r in static_results
                if r.error_type
            },
            "incremental": {
                r.error_type: sum(1 for q in incremental_results if q.error_type == r.error_type)
                for r in incremental_results
                if r.error_type
            },
        },
        "hard_gates": {name: bool(value) for name, value in gates.items()},
        "candidate": "FIXED_INCREMENTAL_DEVELOPMENT_CANDIDATE"
        if all(gates.values())
        else None,
        "claim_scope": CLAIM_SCOPE,
        "attempt_consumption": (
            "first scientific sc_decode call of the paired run; on any failure the "
            "single attempt stays consumed with no rerun, seed change or tuning"
        ),
    }
    accounting = {
        "static_event_count": len(static_events),
        "incremental_event_count": len(incremental_events),
        "static": {
            "incremental": dict(static_totals),
            "recount": dict(static_recount),
            "mismatch_count": int(gate_bundle["static_mismatch"]),
            "transcript_sha256": transcript_summary(static_events)["transcript_sha256"],
        },
        "incremental": {
            "incremental": dict(incremental_totals),
            "recount": dict(incremental_recount),
            "mismatch_count": int(gate_bundle["incremental_mismatch"]),
            "transcript_sha256": transcript_summary(incremental_events)["transcript_sha256"],
        },
        "union_bound": union_bound,
        "public_control": public_control,
    }

    plan = _build_plan(
        run_seed=seed, blocks=blocks, nested=nested, total_cap=total_cap, block_cap=block_cap
    )
    out_path.mkdir(parents=True)
    _write_json(out_path / "frozen_plan.json", plan)
    _write_json(
        out_path / "per_block_paired_outcomes.json",
        {"n_blocks": len(paired_records), "blocks": paired_records},
    )
    _write_json(out_path / "transcript_accounting.json", accounting)
    _write_json(out_path / "aggregate_comparison.json", aggregate)
    _write_report(out_path / "report.md", aggregate)
    return {
        "plan": plan,
        "paired_records": paired_records,
        "accounting": accounting,
        "aggregate": aggregate,
        "static_results": static_results,
        "incremental_results": incremental_results,
        "static_events": static_events,
        "incremental_events": incremental_events,
        "static_totals": static_totals,
        "incremental_totals": incremental_totals,
        "nested": nested,
    }


def _three_arm_gates(
    *,
    run_seed,
    blocks,
    paired_records,
    static_results,
    strict_results,
    r1_results,
    nested,
    resource_stop_fired,
    static_recount,
    strict_recount,
    r1_recount,
    static_totals,
    strict_totals,
    r1_totals,
) -> dict:
    static_counts = _outcome_counts(static_results)
    strict_counts = _outcome_counts(strict_results)
    r1_counts = _outcome_counts(r1_results)
    static_attempted = blocks - static_counts["resource_abort"]
    strict_attempted = blocks - strict_counts["resource_abort"]
    r1_attempted = blocks - r1_counts["resource_abort"]
    static_key = static_totals["key_dependent_bits"]
    r1_key = r1_totals["key_dependent_bits"]
    r1_wilson = wilson_lower_bound(r1_counts["exact"], r1_attempted)
    total_tag_invocations = (
        static_totals["verification_invocations"]
        + strict_totals["verification_invocations"]
        + r1_totals["verification_invocations"]
    )
    recount_total_tags = (
        static_recount["verification_invocations"]
        + strict_recount["verification_invocations"]
        + r1_recount["verification_invocations"]
    )
    recount_fields = (
        "key_dependent_bits",
        "public_control_bits",
        "verification_invocations",
        "feedback_control_invocations",
    )
    static_mismatch = sum(1 for name in recount_fields if static_totals[name] != static_recount[name])
    strict_mismatch = sum(1 for name in recount_fields if strict_totals[name] != strict_recount[name])
    r1_mismatch = sum(1 for name in recount_fields if r1_totals[name] != r1_recount[name])
    schedule_consistent = bool(
        nested.order_prefix_matches
        and nested.strict_nesting
        and nested.new_coordinates_disjoint
        and all(static_record_consistent(r, nested.n, DEFAULT_K) for r in static_results)
        and all(incremental_record_consistent(r, nested) for r in strict_results)
        and all(incremental_record_consistent(r, nested, advance_on_reject=True) for r in r1_results)
    )
    strict_pinned = bool(
        all(
            incremental_record_consistent(r, nested)
            and int(r.decode_rejected_continue_count) == 0
            and tuple(r.rejected_levels) == ()
            and r.arm == "incremental"
            for r in strict_results
        )
        and all(r.arm == R1_RESULT_ARM for r in r1_results)
    )
    plan_identity = (
        int(run_seed) == R1_RUN_SEED
        and int(blocks) == R1_FROZEN_BLOCKS
        and int(nested.n) == DEFAULT_N
        and tuple(int(v) for v in nested.sizes) == tuple(FROZEN_K)
        and float(nested.epsilon) == float(EPSILON)
    )
    gates = {
        "frozen_plan_identity": bool(plan_identity),
        "three_arm_identical_blocks": bool(
            len(paired_records) == blocks and all(bool(r["paired_match"]) for r in paired_records)
        ),
        "outcome_buckets_disjoint_exhaustive_all_arms": bool(
            sum(static_counts.values()) == blocks
            and sum(strict_counts.values()) == blocks
            and sum(r1_counts.values()) == blocks
        ),
        "coverage_complete_all_arms": bool(
            static_attempted == blocks and strict_attempted == blocks and r1_attempted == blocks
        ),
        "r1_undetected_zero": bool(r1_counts["undetected"] == 0),
        "r1_exact_ge_285": bool(r1_counts["exact"] >= MIN_EXACT),
        "r1_wilson_lower_ge_0_90": bool(r1_wilson >= WILSON_LB_MIN),
        "r1_avg_key_dependent_le_95pct_static": bool(
            static_attempted == r1_attempted
            and static_attempted == strict_attempted
            and static_key > 0
            and r1_key * DISCLOSURE_SAVING_DEN <= DISCLOSURE_SAVING_NUM * static_key
        ),
        "frozen_order_nesting_and_schedule_consistency": bool(schedule_consistent),
        "invocation_universe_equals_recount_all_arms": bool(
            static_recount["verification_invocations"] == static_totals["verification_invocations"]
            and strict_recount["verification_invocations"] == strict_totals["verification_invocations"]
            and r1_recount["verification_invocations"] == r1_totals["verification_invocations"]
            and r1_recount["feedback_control_invocations"]
            == r1_totals["feedback_control_invocations"]
            and strict_recount["feedback_control_invocations"]
            == strict_totals["feedback_control_invocations"]
        ),
        "union_bound_consistent": bool(
            total_tag_invocations == recount_total_tags
            and verification_union_bound(total_tag_invocations)
            == verification_union_bound(recount_total_tags)
            and verification_union_bound(static_totals["verification_invocations"])
            == verification_union_bound(static_recount["verification_invocations"])
            and verification_union_bound(strict_totals["verification_invocations"])
            == verification_union_bound(strict_recount["verification_invocations"])
            and verification_union_bound(r1_totals["verification_invocations"])
            == verification_union_bound(r1_recount["verification_invocations"])
        ),
        "recount_zero_mismatch": bool(static_mismatch == 0 and strict_mismatch == 0 and r1_mismatch == 0),
        "truth_leak_zero": bool(
            all(not r.truth_leak_violation for r in static_results)
            and all(not r.truth_leak_violation for r in strict_results)
            and all(not r.truth_leak_violation for r in r1_results)
        ),
        "nonfinite_zero": bool(
            all(not r.nonfinite for r in static_results)
            and all(not r.nonfinite for r in strict_results)
            and all(not r.nonfinite for r in r1_results)
        ),
        "resource_stop_preregistered": bool(
            (
                static_counts["resource_abort"] == 0
                and strict_counts["resource_abort"] == 0
                and r1_counts["resource_abort"] == 0
            )
            or resource_stop_fired
        ),
        "feedback_counted": bool(
            r1_totals["feedback_control_invocations"] == r1_recount["feedback_control_invocations"]
            and r1_totals["feedback_control_bits"]
            == FEEDBACK_CONTROL_BITS * r1_totals["feedback_control_invocations"]
            and r1_totals["public_control_bits"]
            == r1_totals["public_seed_bits"] + r1_totals["feedback_control_bits"]
            and strict_totals["feedback_control_invocations"]
            == strict_recount["feedback_control_invocations"]
            and strict_totals["feedback_control_bits"]
            == FEEDBACK_CONTROL_BITS * strict_totals["feedback_control_invocations"]
            and strict_totals["public_control_bits"]
            == strict_totals["public_seed_bits"] + strict_totals["feedback_control_bits"]
        ),
        "public_control_counted": bool(
            static_totals["public_control_bits"] == static_recount["public_control_bits"]
            and static_totals["public_control_bits"] == static_totals["public_seed_bits"]
            and strict_totals["public_control_bits"] == strict_recount["public_control_bits"]
            and r1_totals["public_control_bits"] == r1_recount["public_control_bits"]
        ),
        "strict_arm_pinned_consistency": bool(strict_pinned),
    }
    return {
        "gates": gates,
        "static_counts": static_counts,
        "strict_counts": strict_counts,
        "r1_counts": r1_counts,
        "static_attempted": static_attempted,
        "strict_attempted": strict_attempted,
        "r1_attempted": r1_attempted,
        "r1_wilson": r1_wilson,
        "static_mismatch": static_mismatch,
        "strict_mismatch": strict_mismatch,
        "r1_mismatch": r1_mismatch,
        "total_tag_invocations": total_tag_invocations,
        "recount_total_tags": recount_total_tags,
    }


def _arm_aggregate(*, name, counts, attempted, totals, wilson, blocks, results) -> dict:
    return {
        "name": name,
        "outcome_totals": {key: int(value) for key, value in counts.items()},
        "attempted": int(attempted),
        "coverage": round(attempted / blocks, 9),
        "key_dependent_bits_total": int(totals["key_dependent_bits"]),
        "average_key_dependent_bits_per_attempted_block": round(
            (totals["key_dependent_bits"] / attempted) if attempted else 0.0, 9
        ),
        "public_seed_bits_total": int(totals["public_seed_bits"]),
        "feedback_control_bits_total": int(totals["feedback_control_bits"]),
        "public_control_bits_total": int(totals["public_control_bits"]),
        "tag_invocations_total": int(totals["verification_invocations"]),
        "feedback_control_invocations_total": int(totals["feedback_control_invocations"]),
        "levels_invoked_total": int(sum(int(r.levels_invoked) for r in results)),
        "accepted_level_histogram": {
            str(level): int(sum(1 for r in results if r.accepted_level == level))
            for level in range(len(FROZEN_K))
        },
        "decode_failed_level_histogram": {
            str(level): int(sum(1 for r in results if r.decode_failed_level == level))
            for level in range(len(FROZEN_K))
        },
        "wilson": {
            "confidence": "one-sided 95%",
            "z": WILSON_Z,
            "successes": int(counts["exact"]),
            "denominator": int(attempted),
            "lower_bound": wilson,
        },
    }


def _three_arm_plan(*, run_seed, blocks, nested, total_cap, block_cap) -> dict:
    return {
        "protocol": R1_PROTOCOL_NAME,
        "mode": THREE_ARM_MODE,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "run_seed": int(run_seed),
        "planned_blocks": int(blocks),
        "q": DEFAULT_Q,
        "n": int(nested.n),
        "epsilon": float(nested.epsilon),
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "channel": "q-ary erasure; observed symbol one-hot posterior, erased symbol uniform",
        "order": "analytic_order(0.05, 256), worst-first (descending erasure probability, ties by index)",
        "arms": ["static", "strict_stop", "r1"],
        "seed_derivation": {
            "master_seed": R1_TOEPLITZ_MASTER_SEED,
            "namespace": (
                "static arm uses 'static'; both incremental arms use 'incremental' so a block "
                "that never rejects is bit-identical between strict-stop and R1 and the paired "
                "comparison isolates the rejection delta"
            ),
            "rule": (
                "MSB-first unpack of SHA-256('nbpolar-p6-toeplitz-seed:<master>:<arm>:"
                "<block_index>:<level>:<counter>') concatenated over counter=0,1,...; "
                "truncated to seed_bits; level index 0-based (static level 0, incremental "
                "levels 0..4); public control, never persisted raw"
            ),
            "seed_bits": seed_bits_for(nested.n),
        },
        "schedule": {
            "K": [int(v) for v in nested.sizes],
            "D_sets": [[int(v) for v in arr.tolist()] for arr in nested.sets],
            "new_coordinates": [[int(v) for v in arr.tolist()] for arr in nested.new_positions],
            "strict_nesting": bool(nested.strict_nesting),
            "order_prefix_matches": bool(nested.order_prefix_matches),
            "new_coordinates_disjoint": bool(nested.new_coordinates_disjoint),
        },
        "static_comparator": {
            "K": DEFAULT_K,
            "D": [int(v) for v in static_disclosure_coordinates(nested.n, DEFAULT_K)],
            "disclosure_rule": "publish actual U[D] values including zeros; the decoder receives the known set sorted(D)",
            "restarts_per_block": 1,
        },
        "disclosure_rule": (
            "level i publishes only actual GF32 U values of D_i minus D_{i-1} (zeros are "
            "values); the decoder receives the cumulative known set D_i with those actual "
            "values; each coordinate is counted once"
        ),
        "restart_rule": "every invoked level runs a fresh sc_decode on the same original Bob metric",
        "rejection_rule": {
            "terminal_error": "ImpossibleDisclosedValueError",
            "non_final_levels": "K=29/33/37/41 (levels 0..3): decode_rejected_continue",
            "final_level": "K=45 (level 4): terminal decode_failed",
            "advance": (
                "record the intermediate rejection; create and verify no candidate; invoke "
                "no tag; count exactly one public feedback request; disclose the next fixed "
                "increment and restart SC from scratch on the original metric"
            ),
            "other_exceptions": (
                "NumericNonfiniteError, other ValueError/TypeError and nonfinite decision "
                "marginals stay fail-closed terminal decode_failed at every level"
            ),
            "not_success": "an intermediate rejection is never success and never a final outcome bucket",
        },
        "label_domain": {
            "packing": "single-layer 10-bit embedding: high five bits carry the GF32 symbol, low five bits zero",
            "bits_per_label": LABEL_BITS,
            "message_bits": LABEL_BITS * int(nested.n),
            "single_layer_low_half_constant_zero": True,
        },
        "toeplitz": {
            "tag_bits": TAG_BITS,
            "master_seed": R1_TOEPLITZ_MASTER_SEED,
            "derivation": (
                "MSB-first unpack of SHA-256('nbpolar-p6-toeplitz-seed:<master>:<arm>:"
                "<block_index>:<level>:<counter>') concatenated over counter=0,1,...; "
                "truncated to seed_bits; level index 0-based (static level 0, incremental "
                "levels 0..4); public control, never persisted raw"
            ),
            "seed_bits": seed_bits_for(nested.n),
        },
        "accounting": {
            "disclosed_bits_per_coordinate": DISCLOSED_BITS_PER_COORDINATE,
            "formula_terminated": "5*K_j + 64*j (j = tag invocations)",
            "formula_decode_failed_at_level_i": "5*K_i + 64*j (j = tag invocations before the failing level)",
            "formula_resource_abort": 0,
            "feedback_control_bits_per_advance": FEEDBACK_CONTROL_BITS,
            "feedback_rule": (
                "one public feedback request per level advance: a tag mismatch or a non-final "
                "decode rejection; total advances = levels_invoked - 1"
            ),
        },
        "union_bound": "min(1.0, total_tag_invocations * 2**-64)",
        "outcome_precedence": [
            "resource_abort: block not executed (preregistered budget stop)",
            "decode_failed: SC exception or nonfinite marginals at an invoked level; stop fail-closed",
            "verify_failed: final-level tag mismatch after all frozen levels",
            "exact: tag match and the candidate equals Alice source word with equal label vectors",
            "undetected: tag match and not exact (never success)",
            "decode_rejected_continue: intermediate transition only, never a final outcome bucket",
        ],
        "budget": {
            "total_wall_s": float(total_cap),
            "per_paired_block_soft_cap_s": float(block_cap),
            "rss_bytes_max": RSS_LIMIT_BYTES,
        },
        "refused_run_seeds": sorted(int(v) for v in R1_BANNED_RUN_SEEDS),
        "attempt_consumption_point": (
            "first scientific sc_decode call of the three-arm run (static comparator arm, block 0)"
        ),
    }


def run_three_arm_paired_dev_gate(
    *,
    run_seed,
    blocks,
    out_root,
    total_wall_s: float | None = None,
    per_paired_block_soft_cap_s: float | None = None,
):
    """Execute the three-arm R1 development gate and write exactly five files.

    Refuses an existing output root and a banned R1 run seed before any
    decoder call. The frozen command passes ``run_seed=2026091350``,
    ``blocks=300`` and the absent R1 output root.
    """
    out_path = Path(out_root)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    seed = validate_r1_run_seed(run_seed)
    blocks = _as_int(blocks, "blocks", minimum=1)
    n = DEFAULT_N
    sizes = FROZEN_K
    total_cap = THREE_ARM_TOTAL_WALL_S if total_wall_s is None else float(total_wall_s)
    block_cap = (
        THREE_ARM_PER_PAIRED_BLOCK_SOFT_CAP_S
        if per_paired_block_soft_cap_s is None
        else float(per_paired_block_soft_cap_s)
    )
    field = make_gf32()
    nested = build_nested_schedule(n=n, epsilon=EPSILON, sizes=sizes)
    rng = np.random.default_rng(seed)

    static_results: list = []
    strict_results: list = []
    r1_results: list = []
    paired_records: list = []
    static_events: list = []
    strict_events: list = []
    r1_events: list = []
    resource_stop_fired = False
    start = time.perf_counter()

    for block_index in range(blocks):
        if time.perf_counter() - start > total_cap:
            resource_stop_fired = True
            for remaining in range(block_index, blocks):
                _abort_three_arm(
                    remaining, paired_records, static_results, strict_results, r1_results, nested
                )
            break
        metric_start = time.perf_counter()
        x, _y, logp = generate_erasure_block(rng, DEFAULT_Q, n, EPSILON)
        metric_wall = time.perf_counter() - metric_start
        three = run_three_arm_block(
            block_index, x, logp, field=field, n=n, sizes=sizes, nested=nested
        )
        static = three["static_result"]
        strict = three["strict_result"]
        r1 = three["r1_result"]
        static_results.append(static)
        strict_results.append(strict)
        r1_results.append(r1)
        static_events.extend(static_block_events(static, n, DEFAULT_K))
        strict_events.extend(incremental_block_events(strict, nested))
        r1_events.extend(incremental_block_events(r1, nested, advance_on_reject=True))
        paired_records.append(
            {
                "block_index": int(block_index),
                "paired_match": bool(three["paired_match"]),
                "metric_wall_s": round(float(metric_wall), 6),
                "static_wall_s": three["static_wall_s"],
                "strict_wall_s": three["strict_wall_s"],
                "r1_wall_s": three["r1_wall_s"],
                "three_arm_wall_s": three["three_arm_wall_s"],
                "static": _r1_arm_record(static, nested),
                "strict_stop": _r1_arm_record(strict, nested),
                "r1": _r1_arm_record(r1, nested),
            }
        )
        if metric_wall + three["three_arm_wall_s"] > block_cap:
            resource_stop_fired = True
            for remaining in range(block_index + 1, blocks):
                _abort_three_arm(
                    remaining, paired_records, static_results, strict_results, r1_results, nested
                )
            break

    static_recount = recount_transcript(static_events)
    strict_recount = recount_transcript(strict_events)
    r1_recount = recount_transcript(r1_events)
    static_totals = _incremental_totals(static_results)
    strict_totals = _incremental_totals(strict_results)
    r1_totals = _incremental_totals(r1_results)
    gate_bundle = _three_arm_gates(
        run_seed=seed,
        blocks=blocks,
        paired_records=paired_records,
        static_results=static_results,
        strict_results=strict_results,
        r1_results=r1_results,
        nested=nested,
        resource_stop_fired=resource_stop_fired,
        static_recount=static_recount,
        strict_recount=strict_recount,
        r1_recount=r1_recount,
        static_totals=static_totals,
        strict_totals=strict_totals,
        r1_totals=r1_totals,
    )
    gates = gate_bundle["gates"]
    wall_s = time.perf_counter() - start
    static_wilson = wilson_lower_bound(
        gate_bundle["static_counts"]["exact"], gate_bundle["static_attempted"]
    )
    strict_wilson = wilson_lower_bound(
        gate_bundle["strict_counts"]["exact"], gate_bundle["strict_attempted"]
    )
    rescue = rescue_comparison(strict_results, r1_results)
    static_key = static_totals["key_dependent_bits"]
    r1_key = r1_totals["key_dependent_bits"]
    union_bound = {
        "static_tag_invocations": int(static_totals["verification_invocations"]),
        "strict_stop_tag_invocations": int(strict_totals["verification_invocations"]),
        "r1_tag_invocations": int(r1_totals["verification_invocations"]),
        "total_tag_invocations": int(gate_bundle["total_tag_invocations"]),
        "recount_total_tag_invocations": int(gate_bundle["recount_total_tags"]),
        "static": verification_union_bound(static_totals["verification_invocations"]),
        "strict_stop": verification_union_bound(strict_totals["verification_invocations"]),
        "r1": verification_union_bound(r1_totals["verification_invocations"]),
        "total": verification_union_bound(gate_bundle["total_tag_invocations"]),
    }
    public_control = {
        "static_seed_bits": int(static_totals["public_seed_bits"]),
        "strict_stop_seed_bits": int(strict_totals["public_seed_bits"]),
        "r1_seed_bits": int(r1_totals["public_seed_bits"]),
        "strict_stop_feedback_control_invocations": int(
            strict_totals["feedback_control_invocations"]
        ),
        "strict_stop_feedback_control_bits": int(strict_totals["feedback_control_bits"]),
        "r1_feedback_control_invocations": int(r1_totals["feedback_control_invocations"]),
        "r1_feedback_control_bits": int(r1_totals["feedback_control_bits"]),
        "total_public_control_bits": int(
            static_totals["public_control_bits"]
            + strict_totals["public_control_bits"]
            + r1_totals["public_control_bits"]
        ),
        "r1_split": {
            "seed_bits": int(r1_totals["public_seed_bits"]),
            "feedback_control_bits": int(r1_totals["feedback_control_bits"]),
        },
        "strict_stop_split": {
            "seed_bits": int(strict_totals["public_seed_bits"]),
            "feedback_control_bits": int(strict_totals["feedback_control_bits"]),
        },
    }
    rejected_histogram = {
        str(level): int(sum(1 for r in r1_results if level in tuple(r.rejected_levels)))
        for level in range(len(FROZEN_K) - 1)
    }
    terminating_histogram = {
        str(level): int(sum(1 for r in r1_results if terminating_level(r, nested) == level))
        for level in range(-1, len(FROZEN_K))
    }
    aggregate = {
        "protocol": R1_PROTOCOL_NAME,
        "mode": THREE_ARM_MODE,
        "run_seed": int(seed),
        "planned_blocks": int(blocks),
        "completed_blocks": int(len(paired_records)),
        "q": DEFAULT_Q,
        "n": int(n),
        "epsilon": float(EPSILON),
        "schedule_sizes": [int(v) for v in sizes],
        "static_k": DEFAULT_K,
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_peak": _peak_rss_bytes(),
        "resource_stop_fired": bool(resource_stop_fired),
        "static": _arm_aggregate(
            name="static",
            counts=gate_bundle["static_counts"],
            attempted=gate_bundle["static_attempted"],
            totals=static_totals,
            wilson=static_wilson,
            blocks=blocks,
            results=static_results,
        ),
        "strict_stop": _arm_aggregate(
            name="strict_stop",
            counts=gate_bundle["strict_counts"],
            attempted=gate_bundle["strict_attempted"],
            totals=strict_totals,
            wilson=strict_wilson,
            blocks=blocks,
            results=strict_results,
        ),
        "r1": _arm_aggregate(
            name="r1",
            counts=gate_bundle["r1_counts"],
            attempted=gate_bundle["r1_attempted"],
            totals=r1_totals,
            wilson=gate_bundle["r1_wilson"],
            blocks=blocks,
            results=r1_results,
        ),
        "r1_rejection_accounting": {
            "decode_rejected_continue_count_total": int(
                sum(int(r.decode_rejected_continue_count) for r in r1_results)
            ),
            "blocks_with_at_least_one_rejection": int(
                sum(1 for r in r1_results if int(r.decode_rejected_continue_count) > 0)
            ),
            "rejected_level_histogram": rejected_histogram,
            "terminating_level_histogram": terminating_histogram,
            "levels_invoked_total": int(sum(int(r.levels_invoked) for r in r1_results)),
            "tag_invocations_total": int(r1_totals["verification_invocations"]),
            "feedback_control_invocations_total": int(r1_totals["feedback_control_invocations"]),
        },
        "disclosure_comparison": {
            "static_key_dependent_total": int(static_key),
            "r1_key_dependent_total": int(r1_key),
            "static_attempted": int(gate_bundle["static_attempted"]),
            "r1_attempted": int(gate_bundle["r1_attempted"]),
            "integer_rule": "r1_total * 100 <= 95 * static_total",
            "lhs": int(r1_key) * DISCLOSURE_SAVING_DEN,
            "rhs": DISCLOSURE_SAVING_NUM * int(static_key),
            "saving_fraction": round(
                ((static_key - r1_key) / static_key) if static_key else 0.0, 9
            ),
        },
        "rescue_comparison_against_strict": dict(rescue),
        "union_bound": union_bound,
        "public_control": public_control,
        "transcript": {
            "static_event_count": len(static_events),
            "strict_stop_event_count": len(strict_events),
            "r1_event_count": len(r1_events),
            "static_recount": dict(static_recount),
            "strict_stop_recount": dict(strict_recount),
            "r1_recount": dict(r1_recount),
            "static_mismatch_count": int(gate_bundle["static_mismatch"]),
            "strict_stop_mismatch_count": int(gate_bundle["strict_mismatch"]),
            "r1_mismatch_count": int(gate_bundle["r1_mismatch"]),
            "static_transcript_sha256": transcript_summary(static_events)["transcript_sha256"],
            "strict_stop_transcript_sha256": transcript_summary(strict_events)[
                "transcript_sha256"
            ],
            "r1_transcript_sha256": transcript_summary(r1_events)["transcript_sha256"],
        },
        "truth_leak_count": {
            "static": int(sum(1 for r in static_results if r.truth_leak_violation)),
            "strict_stop": int(sum(1 for r in strict_results if r.truth_leak_violation)),
            "r1": int(sum(1 for r in r1_results if r.truth_leak_violation)),
        },
        "nonfinite_count": {
            "static": int(sum(1 for r in static_results if r.nonfinite)),
            "strict_stop": int(sum(1 for r in strict_results if r.nonfinite)),
            "r1": int(sum(1 for r in r1_results if r.nonfinite)),
        },
        "decode_error_types": {
            "static": {
                r.error_type: sum(1 for q in static_results if q.error_type == r.error_type)
                for r in static_results
                if r.error_type
            },
            "strict_stop": {
                r.error_type: sum(1 for q in strict_results if q.error_type == r.error_type)
                for r in strict_results
                if r.error_type
            },
            "r1": {
                r.error_type: sum(1 for q in r1_results if q.error_type == r.error_type)
                for r in r1_results
                if r.error_type
            },
        },
        "hard_gates": {name: bool(value) for name, value in gates.items()},
        "candidate": "DECODE_REJECT_ADVANCE_DEVELOPMENT_CANDIDATE"
        if all(gates.values())
        else None,
        "claim_scope": CLAIM_SCOPE,
        "attempt_consumption": (
            "first scientific sc_decode call of the three-arm run; on any failure the "
            "single attempt stays consumed with no rerun, seed change or tuning"
        ),
    }
    accounting = {
        "static_event_count": len(static_events),
        "strict_stop_event_count": len(strict_events),
        "r1_event_count": len(r1_events),
        "static": {
            "incremental": dict(static_totals),
            "recount": dict(static_recount),
            "mismatch_count": int(gate_bundle["static_mismatch"]),
            "transcript_sha256": transcript_summary(static_events)["transcript_sha256"],
        },
        "strict_stop": {
            "incremental": dict(strict_totals),
            "recount": dict(strict_recount),
            "mismatch_count": int(gate_bundle["strict_mismatch"]),
            "transcript_sha256": transcript_summary(strict_events)["transcript_sha256"],
        },
        "r1": {
            "incremental": dict(r1_totals),
            "recount": dict(r1_recount),
            "mismatch_count": int(gate_bundle["r1_mismatch"]),
            "transcript_sha256": transcript_summary(r1_events)["transcript_sha256"],
        },
        "union_bound": union_bound,
        "public_control": public_control,
    }

    plan = _three_arm_plan(
        run_seed=seed, blocks=blocks, nested=nested, total_cap=total_cap, block_cap=block_cap
    )
    out_path.mkdir(parents=True)
    _write_json(out_path / "frozen_plan.json", plan)
    _write_json(
        out_path / "per_block_three_arm_outcomes.json",
        {"n_blocks": len(paired_records), "blocks": paired_records},
    )
    _write_json(out_path / "transcript_accounting.json", accounting)
    _write_json(out_path / "aggregate_comparison.json", aggregate)
    _write_three_arm_report(out_path / "report.md", aggregate)
    return {
        "plan": plan,
        "paired_records": paired_records,
        "accounting": accounting,
        "aggregate": aggregate,
        "static_results": static_results,
        "strict_results": strict_results,
        "r1_results": r1_results,
        "static_events": static_events,
        "strict_events": strict_events,
        "r1_events": r1_events,
        "static_totals": static_totals,
        "strict_totals": strict_totals,
        "r1_totals": r1_totals,
        "nested": nested,
    }


def _write_three_arm_report(path: Path, aggregate: dict) -> None:
    static = aggregate["static"]
    strict = aggregate["strict_stop"]
    r1 = aggregate["r1"]
    comparison = aggregate["disclosure_comparison"]
    rescue = aggregate["rescue_comparison_against_strict"]
    lines = [
        "# NB-Polar Phase 6-R1 decode-reject-advance — three-arm synthetic development gate",
        "",
        f"- protocol: `{aggregate['protocol']}` (mode `{aggregate['mode']}`)",
        f"- run seed: `{aggregate['run_seed']}`; planned blocks: {aggregate['planned_blocks']}",
        f"- point: q={aggregate['q']}, N={aggregate['n']}, epsilon={aggregate['epsilon']}",
        f"- nested K: {aggregate['schedule_sizes']}; static comparator K: {aggregate['static_k']}",
        f"- wall: {aggregate['wall_s']} s; peak RSS: {aggregate['rss_bytes_peak']} bytes",
        "",
        "## Outcomes (disjoint, exhaustive; static | strict-stop | R1)",
        "",
        "| bucket | static | strict-stop | r1 |",
        "|---|---|---|---|",
    ]
    for name in OUTCOMES:
        lines.append(
            f"| {name} | {static['outcome_totals'][name]} | {strict['outcome_totals'][name]} "
            f"| {r1['outcome_totals'][name]} |"
        )
    lines += [
        "",
        f"- attempted: static {static['attempted']} (coverage {static['coverage']}); "
        f"strict-stop {strict['attempted']} (coverage {strict['coverage']}); "
        f"r1 {r1['attempted']} (coverage {r1['coverage']})",
        f"- tag invocations: static {static['tag_invocations_total']}; "
        f"strict-stop {strict['tag_invocations_total']}; r1 {r1['tag_invocations_total']}",
        f"- key-dependent bits total: static {static['key_dependent_bits_total']}; "
        f"strict-stop {strict['key_dependent_bits_total']}; r1 {r1['key_dependent_bits_total']}",
        f"- average key-dependent bits per attempted block: static "
        f"{static['average_key_dependent_bits_per_attempted_block']}; strict-stop "
        f"{strict['average_key_dependent_bits_per_attempted_block']}; r1 "
        f"{r1['average_key_dependent_bits_per_attempted_block']}",
        f"- 5% integer rule vs static: {comparison['lhs']} <= {comparison['rhs']} "
        f"(saving fraction {comparison['saving_fraction']})",
        f"- R1 rejections: {aggregate['r1_rejection_accounting']['decode_rejected_continue_count_total']} "
        f"across {aggregate['r1_rejection_accounting']['blocks_with_at_least_one_rejection']} blocks; "
        f"rejected-level histogram {aggregate['r1_rejection_accounting']['rejected_level_histogram']}",
        f"- paired identities vs strict-stop: rescued {rescue['rescued']}, persisted "
        f"{rescue['persisted']}, regressed {rescue['regressed']}, other {rescue['other']}",
        f"- public control: {aggregate['public_control']['total_public_control_bits']} bits "
        f"(static seed {aggregate['public_control']['static_seed_bits']}; strict-stop seed "
        f"{aggregate['public_control']['strict_stop_seed_bits']}; r1 seed "
        f"{aggregate['public_control']['r1_seed_bits']}; r1 feedback "
        f"{aggregate['public_control']['r1_feedback_control_bits']})",
        f"- verification union bound (total): {aggregate['union_bound']['total']} over "
        f"{aggregate['union_bound']['total_tag_invocations']} tag invocations",
        f"- transcript mismatch counts: static {aggregate['transcript']['static_mismatch_count']}; "
        f"strict-stop {aggregate['transcript']['strict_stop_mismatch_count']}; r1 "
        f"{aggregate['transcript']['r1_mismatch_count']}",
        f"- truth-leak violations: {aggregate['truth_leak_count']}; "
        f"nonfinite: {aggregate['nonfinite_count']}",
        "",
        "## One-sided 95% Wilson lower bound (exact recovery)",
        "",
        f"- static: {static['wilson']['successes']}/{static['wilson']['denominator']} -> "
        f"{static['wilson']['lower_bound']}",
        f"- strict-stop: {strict['wilson']['successes']}/{strict['wilson']['denominator']} -> "
        f"{strict['wilson']['lower_bound']}",
        f"- r1: {r1['wilson']['successes']}/{r1['wilson']['denominator']} -> "
        f"{r1['wilson']['lower_bound']}",
        "",
        "## Hard gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in aggregate["hard_gates"].items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        f"- candidate label: `{aggregate['candidate']}`",
        "",
        f"**Scope:** {aggregate['claim_scope']}.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, aggregate: dict) -> None:
    static = aggregate["static"]
    incremental = aggregate["incremental"]
    comparison = aggregate["disclosure_comparison"]
    lines = [
        "# NB-Polar Phase 6 fixed incremental — paired synthetic development gate",
        "",
        f"- protocol: `{aggregate['protocol']}` (mode `{aggregate['mode']}`)",
        f"- run seed: `{aggregate['run_seed']}`; planned blocks: {aggregate['planned_blocks']}",
        f"- point: q={aggregate['q']}, N={aggregate['n']}, epsilon={aggregate['epsilon']}",
        f"- nested K: {aggregate['schedule_sizes']}; static comparator K: {aggregate['static_k']}",
        f"- wall: {aggregate['wall_s']} s; peak RSS: {aggregate['rss_bytes_peak']} bytes",
        "",
        "## Outcomes (disjoint, exhaustive; static | incremental)",
        "",
        "| bucket | static | incremental |",
        "|---|---|---|",
    ]
    for name in OUTCOMES:
        lines.append(
            f"| {name} | {static['outcome_totals'][name]} | {incremental['outcome_totals'][name]} |"
        )
    lines += [
        "",
        f"- attempted: static {static['attempted']} (coverage {static['coverage']}); "
        f"incremental {incremental['attempted']} (coverage {incremental['coverage']})",
        f"- tag invocations: static {static['tag_invocations_total']}; "
        f"incremental {incremental['tag_invocations_total']}",
        f"- key-dependent bits total: static {static['key_dependent_bits_total']}; "
        f"incremental {incremental['key_dependent_bits_total']}",
        f"- average key-dependent bits per attempted block: static "
        f"{static['average_key_dependent_bits_per_attempted_block']}; incremental "
        f"{incremental['average_key_dependent_bits_per_attempted_block']}",
        f"- 5% integer rule: {comparison['lhs']} <= {comparison['rhs']} "
        f"(saving fraction {comparison['saving_fraction']})",
        f"- public control: {aggregate['public_control']['total_public_control_bits']} bits "
        f"(static seed {aggregate['public_control']['static_seed_bits']}; incremental seed "
        f"{aggregate['public_control']['incremental_seed_bits']}; feedback "
        f"{aggregate['public_control']['incremental_feedback_control_bits']})",
        f"- verification union bound (total): {aggregate['union_bound']['total']} over "
        f"{aggregate['union_bound']['total_tag_invocations']} tag invocations",
        f"- transcript mismatch counts: static {aggregate['transcript']['static_mismatch_count']}; "
        f"incremental {aggregate['transcript']['incremental_mismatch_count']}",
        f"- truth-leak violations: {aggregate['truth_leak_count']}; "
        f"nonfinite: {aggregate['nonfinite_count']}",
        "",
        "## One-sided 95% Wilson lower bound (exact recovery)",
        "",
        f"- static: {static['wilson']['successes']}/{static['wilson']['denominator']} -> "
        f"{static['wilson']['lower_bound']}",
        f"- incremental: {incremental['wilson']['successes']}/"
        f"{incremental['wilson']['denominator']} -> {incremental['wilson']['lower_bound']}",
        "",
        "## Hard gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in aggregate["hard_gates"].items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        f"- candidate label: `{aggregate['candidate']}`",
        "",
        f"**Scope:** {aggregate['claim_scope']}.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-incremental",
        description="NB-Polar Phase 6 / 6-R1 incremental synthetic dev gate",
    )
    parser.add_argument("--mode", required=True, choices=[MODE, THREE_ARM_MODE])
    parser.add_argument("--run-seed", required=True, type=int, dest="run_seed")
    parser.add_argument("--blocks", required=True, type=int)
    parser.add_argument("--out", required=True)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.mode == THREE_ARM_MODE:
            run = run_three_arm_paired_dev_gate(
                run_seed=args.run_seed, blocks=args.blocks, out_root=args.out
            )
        else:
            run = run_paired_dev_gate(run_seed=args.run_seed, blocks=args.blocks, out_root=args.out)
    except (ValueError, FileExistsError, OSError) as exc:
        label = "three-arm dev-gate" if args.mode == THREE_ARM_MODE else "paired dev-gate"
        print(f"nbpolar phase6 {label} refused: {exc}", file=sys.stderr)
        return 2
    aggregate = run["aggregate"]
    if args.mode == THREE_ARM_MODE:
        payload = {
            "protocol": aggregate["protocol"],
            "run_seed": aggregate["run_seed"],
            "planned_blocks": aggregate["planned_blocks"],
            "static_outcomes": aggregate["static"]["outcome_totals"],
            "strict_stop_outcomes": aggregate["strict_stop"]["outcome_totals"],
            "r1_outcomes": aggregate["r1"]["outcome_totals"],
            "r1_wilson_lower_bound": aggregate["r1"]["wilson"]["lower_bound"],
            "rescue_comparison_against_strict": aggregate["rescue_comparison_against_strict"],
            "disclosure_comparison": aggregate["disclosure_comparison"],
            "candidate": aggregate["candidate"],
            "out_root": args.out,
        }
    else:
        payload = {
            "protocol": aggregate["protocol"],
            "run_seed": aggregate["run_seed"],
            "planned_blocks": aggregate["planned_blocks"],
            "static_outcomes": aggregate["static"]["outcome_totals"],
            "incremental_outcomes": aggregate["incremental"]["outcome_totals"],
            "incremental_wilson_lower_bound": aggregate["incremental"]["wilson"]["lower_bound"],
            "disclosure_comparison": aggregate["disclosure_comparison"],
            "candidate": aggregate["candidate"],
            "out_root": args.out,
        }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
