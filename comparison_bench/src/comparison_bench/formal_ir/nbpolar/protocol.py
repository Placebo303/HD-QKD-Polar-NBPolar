"""NB-Polar Phase 5 static reconciliation protocol (synthetic development only).

One frozen, non-adaptive protocol at the accepted Phase 3 point:

- GF32, primitive polynomial 37, alpha 2, natural-order transform;
- q-ary erasure channel, ``N=256``, ``epsilon=0.05``, ``K=45``;
- static disclosure set ``D = analytic_order(0.05, 256)[:45]`` (the 45
  highest-risk coordinates; Alice publishes their actual GF32 ``U``
  values, zeros included, and zero is never a sentinel);
- exactly one accepted reference :func:`sc_decode` call per attempted
  block on Bob's channel metric with only those coordinates known;
- full re-encoding to physical labels ``label_j = 32 * x_hat_j`` (10-bit
  embedding, low half constant zero in the single-layer convention);
- at most one final 64-bit Toeplitz verification per attempted block,
  computed after decoding. The tag never selects, retries or modifies a
  decoder path.

Terminal buckets (disjoint, exhaustive over planned blocks): ``exact``,
``undetected`` (tag pass on a non-exact block, never success),
``verify_failed`` (tag mismatch), ``decode_failed`` (SC exception or
nonfinite decision marginals; no verification invocation),
``resource_abort`` (block not executed because a preregistered budget
stop fired).

Accounting: ``key_dependent_bits = 5*K + (64 if verification invoked)``
per attempted block; the 2623-bit per-block Toeplitz seed is public
control and is reported separately. An independent literal recount walks
the in-memory event list and must equal the incremental totals.

This module is synthetic-only: no artifact, real-frame, benchmark,
rate-adaptation, SCL/CRC, retry or file output except the explicit
dev-gate CLI below. No import-time I/O, no global RNG. Truth isolation
is enforced by an adversarial post-decision mutation sentinel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from dataclasses import dataclass
from numbers import Integral
from pathlib import Path

import numpy as np

from ..shared import canonical_event, toeplitz_tag, transcript_summary
from .algebra import make_gf32, validate_symbols
from .construction import analytic_order
from .sc import NumericNonfiniteError, sc_decode
from .synthetic import generate_erasure_block
from .transform import polar_transform

try:  # POSIX (the frozen command runs under WSL); Windows native has no resource module.
    import resource
except ImportError:  # pragma: no cover - exercised only on Windows native
    resource = None

PROTOCOL_NAME = "nbpolar-static-protocol"
DEFAULT_Q = 32
DEFAULT_N = 256
DEFAULT_K = 45
EPSILON = 0.05
ALPHA = 2

# Frozen seeds. 2026091317 is reserved for the single authorized 300-block
# attempt and is never used by tests; 2026091318 is the public Toeplitz master.
FROZEN_RUN_SEED = 2026091317
TOEPLITZ_MASTER_SEED = 2026091318
BANNED_RUN_SEEDS = frozenset(range(2026091200, 2026091214)) | {
    2026091314,
    2026091315,
    2026091316,
}

DISCLOSED_BITS_PER_COORDINATE = 5
LABEL_SCALE = 32
LABEL_BITS = 10
TAG_BITS = 64
MESSAGE_BITS = LABEL_BITS * DEFAULT_N  # 2560
SEED_BITS = MESSAGE_BITS + TAG_BITS - 1  # 2623 public control bits per verification
WILSON_Z = 1.6448536269514722  # one-sided 95%
RSS_LIMIT_BYTES = 2 * 1024**3

# Budgets measured by the synthetic profile (see P5_FREEZE.md); no CLI default.
DEV_GATE_TOTAL_WALL_S = 300.0
DEV_GATE_PER_BLOCK_SOFT_CAP_S = 5.0

OUTCOMES = ("exact", "undetected", "verify_failed", "decode_failed", "resource_abort")

CLAIM_SCOPE = (
    "synthetic development signal only; this is not real-data FER, leakage "
    "efficiency, key rate, qualification or promotion evidence"
)


def _as_int(value, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer")
    out = int(value)
    if minimum is not None and out < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {out}")
    return out


def validate_run_seed(seed) -> int:
    """Return ``seed`` if usable for a Phase 5 run; refuse Phase 1-4 seeds."""
    out = _as_int(seed, "run_seed", minimum=0)
    if out in BANNED_RUN_SEEDS:
        raise ValueError(f"run seed {out} is banned (consumed by Phase 1-4)")
    return out


def static_disclosure_coordinates(
    n: int = DEFAULT_N, k: int = DEFAULT_K, epsilon: float = EPSILON
) -> np.ndarray:
    """The frozen static set: first ``k`` entries of the analytic order.

    ``analytic_order`` is worst-first (descending erasure probability, ties
    by index); the returned positions are sorted ascending because the SC
    known-coordinate contract is order-insensitive and a canonical order
    keeps transcripts deterministic.
    """
    n = _as_int(n, "n", minimum=1)
    k = _as_int(k, "k", minimum=0)
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    if k > n:
        raise ValueError(f"k must lie in 0..{n}, got {k}")
    order = analytic_order(float(epsilon), n)
    return np.sort(order[:k]).astype(np.int64)


def labels_from_symbols(symbols) -> np.ndarray:
    """Physical 10-bit labels: ``label_j = 32 * x_j`` (single-layer packing)."""
    arr = validate_symbols(symbols, DEFAULT_Q, name="symbols")
    return (arr * LABEL_SCALE).astype(np.int64)


def labels_to_bits(labels) -> np.ndarray:
    """MSB-first 10-bit expansion of a label vector; returns uint8[10*N]."""
    arr = np.asarray(labels)
    if arr.dtype.kind == "b" or arr.ndim != 1:
        raise ValueError("labels must be a one-dimensional integer vector")
    arr = arr.astype(np.int64)
    if arr.size == 0:
        raise ValueError("labels must be non-empty")
    if arr.min() < 0 or arr.max() >= (1 << LABEL_BITS):
        raise ValueError(f"labels must lie in 0..{(1 << LABEL_BITS) - 1}")
    shifts = np.arange(LABEL_BITS - 1, -1, -1, dtype=np.int64)
    return ((arr[:, None] >> shifts[None, :]) & 1).astype(np.uint8).reshape(-1)


def block_toeplitz_seed_bits(block_index: int, bit_length: int = SEED_BITS) -> np.ndarray:
    """Deterministic public per-block Toeplitz seed.

    Rule: concatenate SHA-256 over ``"nbpolar-p5-toeplitz-seed:<master>:
    <block_index>:<counter>"`` for ``counter = 0, 1, ...`` (ASCII, decimal),
    unpack each digest MSB-first, and truncate to ``bit_length``. Seed
    contents are public control and are never persisted.
    """
    index = _as_int(block_index, "block_index", minimum=0)
    bit_length = _as_int(bit_length, "bit_length", minimum=1)
    prefix = f"nbpolar-p5-toeplitz-seed:{TOEPLITZ_MASTER_SEED}:{index}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < bit_length:
        buf.extend(hashlib.sha256(f"{prefix}:{counter}".encode("ascii")).digest())
        counter += 1
    bits = np.unpackbits(np.frombuffer(bytes(buf), dtype=np.uint8), bitorder="big")
    return bits[:bit_length].astype(np.uint8)


def wilson_lower_bound(successes: int, n: int, z: float = WILSON_Z) -> float:
    """One-sided 95% Wilson lower bound for a binomial proportion."""
    successes = _as_int(successes, "successes", minimum=0)
    n = _as_int(n, "n", minimum=0)
    if successes > n:
        raise ValueError("successes must not exceed n")
    if n == 0:
        return 0.0
    p = successes / n
    denom = 1.0 + z * z / n
    center = p + z * z / (2.0 * n)
    margin = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return max(0.0, (center - margin) / denom)


def _truth_isolation_sentinel(logp, decisions, truth_arrays) -> bool:
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
class StaticBlockResult:
    """One attempted protocol block. Symbol/label arrays are in-memory only."""

    block_index: int
    outcome: str
    exact: bool
    verification_invoked: bool
    nonfinite: bool
    truth_leak_violation: bool
    key_dependent_bits: int
    public_control_bits: int
    pre_symbol_errors: int
    pre_bit_errors: int
    symbol_errors: int
    bit_errors: int
    wall_s: float
    error_type: str | None = None
    x_true: np.ndarray | None = None
    u_true: np.ndarray | None = None
    u_hat: np.ndarray | None = None
    x_hat: np.ndarray | None = None
    labels_true: np.ndarray | None = None
    labels_hat: np.ndarray | None = None


def _abort_result(block_index: int) -> StaticBlockResult:
    return StaticBlockResult(
        block_index=block_index,
        outcome="resource_abort",
        exact=False,
        verification_invoked=False,
        nonfinite=False,
        truth_leak_violation=False,
        key_dependent_bits=0,
        public_control_bits=0,
        pre_symbol_errors=-1,
        pre_bit_errors=-1,
        symbol_errors=-1,
        bit_errors=-1,
        wall_s=0.0,
    )


def _validate_positions(n: int, k: int, positions) -> np.ndarray:
    if positions is None:
        return static_disclosure_coordinates(n, k)
    arr = np.asarray(positions)
    if arr.dtype.kind not in "iu" or arr.ndim != 1:
        raise ValueError("disclosure positions must be a one-dimensional integer vector")
    out = np.sort(arr.astype(np.int64))
    if out.shape != (k,):
        raise ValueError(f"disclosure positions must have length k={k}")
    if k == 0:
        return out
    if out.min() < 0 or out.max() >= n or len(set(out.tolist())) != k:
        raise ValueError(f"disclosure positions must be {k} distinct coordinates in 0..{n - 1}")
    return out


def run_static_block(
    block_index: int,
    x,
    logp,
    *,
    field,
    n: int = DEFAULT_N,
    k: int = DEFAULT_K,
    disclosure_positions=None,
) -> StaticBlockResult:
    """One frozen static protocol block: disclose, decode once, verify once.

    ``x`` is Alice's GF32 source truth; ``logp`` is Bob's ``(N, q)`` channel
    metric. Alice's truth reaches only the transform, the disclosed map,
    the pre/post scoring and the tag; the decoder receives only the
    disclosed subset. Decode failure invokes no tag.
    """
    n = _as_int(n, "n", minimum=1)
    k = _as_int(k, "k", minimum=0)
    q = int(getattr(field, "q", 0))
    if q != DEFAULT_Q:
        raise ValueError(f"field q {q} != frozen {DEFAULT_Q}")
    x_arr = validate_symbols(x, q, name="x")
    if x_arr.shape[0] != n:
        raise ValueError(f"x must have length N={n}, got {x_arr.shape[0]}")
    logp_arr = np.asarray(logp, dtype=np.float64)
    if logp_arr.shape != (n, q):
        raise ValueError(f"logp must have shape ({n}, {q}), got {logp_arr.shape}")
    positions = _validate_positions(n, k, disclosure_positions)

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
        return StaticBlockResult(
            block_index=block_index,
            outcome="decode_failed",
            exact=False,
            verification_invoked=False,
            nonfinite=isinstance(exc, NumericNonfiniteError)
            or "nonfinite" in str(exc).lower()
            or "nan" in str(exc).lower(),
            truth_leak_violation=False,
            key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k,
            public_control_bits=0,
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

    # Keep pristine truth for the record, then let the sentinel mutate the
    # live truth buffers after the decisions exist.
    x_true_out = x_truth.copy()
    u_true_out = u_truth.copy()
    truth_isolated = _truth_isolation_sentinel(
        logp_arr,
        [sc.decision_metrics, sc.decision_log_scores, u_hat, x_hat, labels_hat],
        [x_truth, u_truth, disclosed],
    )

    seed = block_toeplitz_seed_bits(block_index, LABEL_BITS * n + TAG_BITS - 1)
    tag_true = toeplitz_tag(labels_true_bits, seed, TAG_BITS)
    tag_hat = toeplitz_tag(labels_hat_bits, seed, TAG_BITS)
    tag_pass = tag_true == tag_hat
    if not tag_pass:
        outcome = "verify_failed"
    elif exact:
        outcome = "exact"
    else:
        outcome = "undetected"

    return StaticBlockResult(
        block_index=block_index,
        outcome=outcome,
        exact=exact,
        verification_invoked=True,
        nonfinite=False,
        truth_leak_violation=not truth_isolated,
        key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k + TAG_BITS,
        public_control_bits=LABEL_BITS * n + TAG_BITS - 1,
        pre_symbol_errors=pre_symbol_errors,
        pre_bit_errors=pre_bit_errors,
        symbol_errors=symbol_errors,
        bit_errors=bit_errors,
        wall_s=time.perf_counter() - start,
        x_true=x_true_out,
        u_true=u_true_out,
        u_hat=u_hat,
        x_hat=x_hat,
        labels_true=labels_true,
        labels_hat=labels_hat,
    )


def _record_dict(result: StaticBlockResult, metric_wall_s: float = 0.0) -> dict:
    """Compact scalar record; symbol vectors are never persisted."""
    return {
        "block_index": int(result.block_index),
        "outcome": result.outcome,
        "exact": bool(result.exact),
        "verification_invoked": bool(result.verification_invoked),
        "key_dependent_bits": int(result.key_dependent_bits),
        "public_control_bits": int(result.public_control_bits),
        "nonfinite": bool(result.nonfinite),
        "truth_leak_violation": bool(result.truth_leak_violation),
        "error_type": result.error_type,
        "metric_wall_s": round(float(metric_wall_s), 6),
        "decode_wall_s": round(float(result.wall_s), 6),
    }


def _block_events(result: StaticBlockResult, k: int, n: int) -> list[dict]:
    """Canonical public transcript events for one attempted block."""
    frame_key = f"nbpolar-p5-synthetic:{int(result.block_index)}"
    seed_bits = LABEL_BITS * int(n) + TAG_BITS - 1
    disclosure = {
        "event_id": f"block-{int(result.block_index)}-disclosure",
        "frame_key": frame_key,
        "method": "nbpolar_static",
        "event_type": "static_disclosure",
        "direction": "alice_to_bob",
        "parent_event_id": None,
        "pass_id": 0,
        "block_id": int(result.block_index),
        "key_dependent_bits": DISCLOSED_BITS_PER_COORDINATE * int(k),
        "public_control_bits": 0,
        "payload": {},
    }
    events = [disclosure]
    if result.verification_invoked:
        events.append(
            {
                "event_id": f"block-{int(result.block_index)}-verification",
                "frame_key": frame_key,
                "method": "nbpolar_static",
                "event_type": "verification_tag",
                "direction": "alice_to_bob",
                "parent_event_id": disclosure["event_id"],
                "pass_id": 0,
                "block_id": int(result.block_index),
                "key_dependent_bits": TAG_BITS,
                "public_control_bits": seed_bits,
                "payload": {"seed_bit_length": seed_bits},
            }
        )
    for event in events:
        canonical_event(event)  # fail closed on malformed or secret-bearing payloads
    return events


def recount_transcript(events) -> dict:
    """Independent literal recount; does not reuse ``transcript_summary``."""
    key_dependent = 0
    public_control = 0
    verification_invocations = 0
    for event in events:
        key_dependent += int(event["key_dependent_bits"])
        public_control += int(event["public_control_bits"])
        if event["event_type"] == "verification_tag":
            verification_invocations += 1
    return {
        "key_dependent_bits": key_dependent,
        "public_control_bits": public_control,
        "verification_invocations": verification_invocations,
    }


def _peak_rss_bytes() -> int | None:
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


@dataclass(frozen=True, eq=False)
class ProtocolRun:
    """In-memory run record (also returned by :func:`run_dev_gate`)."""

    records: list
    events: list
    incremental: dict
    recount: dict
    mismatch_count: int
    summary: dict


def _build_summary(
    *,
    records,
    events,
    incremental,
    recount,
    mismatch_count,
    run_seed,
    blocks,
    n,
    k,
    resource_stop_fired,
    wall_s,
) -> dict:
    counts = {name: 0 for name in OUTCOMES}
    for record in records:
        counts[record.outcome] += 1
    attempted = blocks - counts["resource_abort"]
    exact = counts["exact"]
    undetected = counts["undetected"]
    verify_failed = counts["verify_failed"]
    decode_failed = counts["decode_failed"]
    verified = exact + undetected
    verification_invocations = exact + undetected + verify_failed
    key_dependent_total = sum(int(r.key_dependent_bits) for r in records)
    public_control_total = sum(int(r.public_control_bits) for r in records)
    average_key_dependent = (key_dependent_total / attempted) if attempted else 0.0
    truth_leak_count = sum(1 for r in records if r.truth_leak_violation)
    nonfinite_count = sum(1 for r in records if r.nonfinite)
    error_types: dict[str, int] = {}
    for record in records:
        if record.error_type:
            error_types[record.error_type] = error_types.get(record.error_type, 0) + 1
    per_block_consistent = all(
        (
            r.outcome == "resource_abort"
            and int(r.key_dependent_bits) == 0
            and int(r.public_control_bits) == 0
        )
        or (
            int(r.key_dependent_bits)
            == DISCLOSED_BITS_PER_COORDINATE * k + (TAG_BITS if r.verification_invoked else 0)
            and int(r.public_control_bits)
            == (LABEL_BITS * n + TAG_BITS - 1 if r.verification_invoked else 0)
        )
        for r in records
    )
    wilson = wilson_lower_bound(exact, attempted)
    gates = {
        "outcome_accounting_disjoint_exhaustive": sum(counts.values()) == blocks,
        "coverage_complete": attempted == blocks,
        "resource_stop_preregistered": counts["resource_abort"] == 0 or resource_stop_fired,
        "per_block_disclosure_consistent": bool(per_block_consistent),
        "verification_universe_consistent": verification_invocations
        == recount["verification_invocations"]
        == incremental["verification_invocations"],
        "recount_zero_mismatch": mismatch_count == 0
        and recount["key_dependent_bits"] == incremental["key_dependent_bits"]
        and recount["public_control_bits"] == incremental["public_control_bits"],
        "undetected_zero": undetected == 0,
        "truth_leak_zero": truth_leak_count == 0,
        "nonfinite_zero": nonfinite_count == 0,
        "wilson_lower_ge_0_90": wilson >= 0.90,
        "avg_key_dependent_below_input_bits": average_key_dependent < LABEL_BITS * n,
    }
    candidate = "STATIC_PROTOCOL_DEVELOPMENT_CANDIDATE" if all(gates.values()) else None
    return {
        "protocol": PROTOCOL_NAME,
        "mode": "dev-gate",
        "run_seed": int(run_seed),
        "planned_blocks": int(blocks),
        "n": int(n),
        "k": int(k),
        "epsilon": EPSILON,
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_peak": _peak_rss_bytes(),
        "resource_stop_fired": bool(resource_stop_fired),
        "outcome_totals": {name: int(counts[name]) for name in OUTCOMES},
        "attempted": int(attempted),
        "coverage": round(attempted / blocks, 9),
        "verified": int(verified),
        "verification_invocations": int(verification_invocations),
        "undetected": int(undetected),
        "key_dependent_bits_total": int(key_dependent_total),
        "public_control_bits_total": int(public_control_total),
        "per_verification_key_dependent_bits": DISCLOSED_BITS_PER_COORDINATE * k + TAG_BITS,
        "average_key_dependent_bits_per_attempted_block": round(average_key_dependent, 9),
        "transcript": {
            "event_count": len(events),
            "incremental": dict(incremental),
            "recount": dict(recount),
            "mismatch_count": int(mismatch_count),
            "transcript_sha256": transcript_summary(events)["transcript_sha256"],
        },
        "truth_leak_count": int(truth_leak_count),
        "nonfinite_count": int(nonfinite_count),
        "decode_error_types": error_types,
        "wilson": {
            "confidence": "one-sided 95%",
            "z": WILSON_Z,
            "successes": int(exact),
            "denominator": int(attempted),
            "lower_bound": wilson,
        },
        "hard_gates": {name: bool(value) for name, value in gates.items()},
        "candidate": candidate,
        "claim_scope": CLAIM_SCOPE,
    }


def execute_blocks(
    *,
    run_seed,
    blocks,
    n: int = DEFAULT_N,
    k: int = DEFAULT_K,
    field=None,
    total_wall_s: float | None = None,
    per_block_soft_cap_s: float | None = None,
) -> ProtocolRun:
    """Run ``blocks`` frozen synthetic protocol blocks (no file output)."""
    seed = validate_run_seed(run_seed)
    blocks = _as_int(blocks, "blocks", minimum=1)
    n = _as_int(n, "n", minimum=1)
    k = _as_int(k, "k", minimum=0)
    if field is None:
        field = make_gf32()
    if int(getattr(field, "q", 0)) != DEFAULT_Q:
        raise ValueError(f"field q {getattr(field, 'q', None)} != frozen {DEFAULT_Q}")
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    if k > n:
        raise ValueError(f"k must lie in 0..{n}, got {k}")
    total_cap = DEV_GATE_TOTAL_WALL_S if total_wall_s is None else float(total_wall_s)
    block_cap = (
        DEV_GATE_PER_BLOCK_SOFT_CAP_S if per_block_soft_cap_s is None else float(per_block_soft_cap_s)
    )
    positions = static_disclosure_coordinates(n, k)
    rng = np.random.default_rng(seed)

    records: list[StaticBlockResult] = []
    metric_walls: list[float] = []
    events: list[dict] = []
    incremental = {"key_dependent_bits": 0, "public_control_bits": 0, "verification_invocations": 0}
    resource_stop_fired = False
    start = time.perf_counter()

    for block_index in range(blocks):
        if time.perf_counter() - start > total_cap:
            resource_stop_fired = True
            records.extend(_abort_result(b) for b in range(block_index, blocks))
            metric_walls.extend(0.0 for _ in range(block_index, blocks))
            break
        metric_start = time.perf_counter()
        x, _y, logp = generate_erasure_block(rng, DEFAULT_Q, n, EPSILON)
        metric_wall_s = time.perf_counter() - metric_start
        result = run_static_block(
            block_index, x, logp, field=field, n=n, k=k, disclosure_positions=positions
        )
        records.append(result)
        metric_walls.append(metric_wall_s)
        events.extend(_block_events(result, k, n))
        incremental["key_dependent_bits"] += int(result.key_dependent_bits)
        incremental["public_control_bits"] += int(result.public_control_bits)
        incremental["verification_invocations"] += int(result.verification_invoked)
        if (metric_wall_s + result.wall_s) > block_cap:
            resource_stop_fired = True
            records.extend(_abort_result(b) for b in range(block_index + 1, blocks))
            metric_walls.extend(0.0 for _ in range(block_index + 1, blocks))
            break

    recount = recount_transcript(events)
    mismatch_count = sum(
        1
        for field_name in ("key_dependent_bits", "public_control_bits", "verification_invocations")
        if incremental[field_name] != recount[field_name]
    )
    # Records carry the metric split for the profile; summary stays scalar-only.
    summary = _build_summary(
        records=records,
        events=events,
        incremental=incremental,
        recount=recount,
        mismatch_count=mismatch_count,
        run_seed=seed,
        blocks=blocks,
        n=n,
        k=k,
        resource_stop_fired=resource_stop_fired,
        wall_s=time.perf_counter() - start,
    )
    record_dicts = [_record_dict(r, wall) for r, wall in zip(records, metric_walls)]
    return ProtocolRun(
        records=record_dicts,
        events=events,
        incremental=incremental,
        recount=recount,
        mismatch_count=mismatch_count,
        summary=summary,
    )


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _frozen_plan(*, run_seed, blocks, n, k, total_cap, block_cap) -> dict:
    return {
        "protocol": PROTOCOL_NAME,
        "mode": "dev-gate",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "run_seed": int(run_seed),
        "planned_blocks": int(blocks),
        "q": DEFAULT_Q,
        "n": int(n),
        "k": int(k),
        "epsilon": EPSILON,
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "channel": "q-ary erasure; observed symbol one-hot posterior, erased symbol uniform",
        "disclosure_rule": (
            "D = analytic_order(0.05, n)[:k] (worst-first slice of the accepted analytic "
            "order); publish actual U[D] values including zeros; SC known_positions = sorted(D)"
        ),
        "disclosure_coordinates": [int(v) for v in static_disclosure_coordinates(n, k)],
        "label_domain": {
            "packing": "label_j = 32 * x_hat_j",
            "bits_per_label": LABEL_BITS,
            "message_bits": LABEL_BITS * int(n),
            "single_layer_low_half_constant_zero": True,
        },
        "toeplitz": {
            "tag_bits": TAG_BITS,
            "master_seed": TOEPLITZ_MASTER_SEED,
            "derivation": (
                "MSB-first unpack of SHA-256('nbpolar-p5-toeplitz-seed:<master>:"
                "<block_index>:<counter>') concatenated over counter=0,1,...; "
                "truncated to seed_bits; public control, never persisted raw"
            ),
            "seed_bits": SEED_BITS,
        },
        "outcome_precedence": [
            "resource_abort: block not executed (preregistered budget stop)",
            "decode_failed: SC exception or nonfinite marginals; no verification invocation",
            "verify_failed: tag mismatch",
            "exact: tag pass and u_hat == U and labels_hat == labels_true",
            "undetected: tag pass and not exact",
        ],
        "budget": {
            "total_wall_s": float(total_cap),
            "per_block_soft_cap_s": float(block_cap),
            "rss_bytes_max": RSS_LIMIT_BYTES,
        },
        "attempt_consumption_point": "first scientific sc_decode call",
    }


def _write_report(path: Path, summary: dict) -> None:
    totals = summary["outcome_totals"]
    lines = [
        "# NB-Polar Phase 5 static protocol — synthetic development gate",
        "",
        f"- protocol: `{summary['protocol']}` (mode `{summary['mode']}`)",
        f"- run seed: `{summary['run_seed']}`; planned blocks: {summary['planned_blocks']}",
        f"- point: q={DEFAULT_Q}, N={summary['n']}, K={summary['k']}, epsilon={summary['epsilon']}",
        f"- wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes",
        "",
        "## Outcomes (disjoint, exhaustive)",
        "",
        "| bucket | count |",
        "|---|---|",
    ]
    for name in OUTCOMES:
        lines.append(f"| {name} | {totals[name]} |")
    lines += [
        "",
        f"- attempted: {summary['attempted']} (coverage {summary['coverage']})",
        f"- verified union (exact + undetected): {summary['verified']}",
        f"- verification invocations: {summary['verification_invocations']}",
        f"- key-dependent bits total: {summary['key_dependent_bits_total']}; "
        f"public control bits total: {summary['public_control_bits_total']}",
        f"- average key-dependent bits per attempted block: "
        f"{summary['average_key_dependent_bits_per_attempted_block']}",
        f"- transcript recount mismatch count: {summary['transcript']['mismatch_count']}",
        f"- truth-leak violations: {summary['truth_leak_count']}; nonfinite: {summary['nonfinite_count']}",
        "",
        "## One-sided 95% Wilson lower bound (exact recovery)",
        "",
        f"- successes/denominator: {summary['wilson']['successes']}/{summary['wilson']['denominator']}",
        f"- z: {summary['wilson']['z']}",
        f"- lower bound: {summary['wilson']['lower_bound']}",
        "",
        "## Hard gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in summary["hard_gates"].items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        f"- candidate label: `{summary['candidate']}`",
        "",
        f"**Scope:** {summary['claim_scope']}.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def run_dev_gate(
    *,
    run_seed,
    blocks,
    out_root,
    n: int = DEFAULT_N,
    k: int = DEFAULT_K,
    total_wall_s: float | None = None,
    per_block_soft_cap_s: float | None = None,
) -> ProtocolRun:
    """Execute the dev-gate blocks and write exactly five compact files.

    Refuses an existing output root (checked before any decoder call).
    """
    out_path = Path(out_root)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    seed = validate_run_seed(run_seed)
    total_cap = DEV_GATE_TOTAL_WALL_S if total_wall_s is None else float(total_wall_s)
    block_cap = (
        DEV_GATE_PER_BLOCK_SOFT_CAP_S if per_block_soft_cap_s is None else float(per_block_soft_cap_s)
    )
    run = execute_blocks(
        run_seed=seed,
        blocks=blocks,
        n=n,
        k=k,
        total_wall_s=total_cap,
        per_block_soft_cap_s=block_cap,
    )
    out_path.mkdir(parents=True)
    plan = _frozen_plan(run_seed=seed, blocks=blocks, n=n, k=k, total_cap=total_cap, block_cap=block_cap)
    _write_json(out_path / "frozen_plan.json", plan)
    _write_json(out_path / "per_block_outcomes.json", {"blocks": run.records, "n_blocks": len(run.records)})
    _write_json(
        out_path / "transcript_accounting.json",
        {
            "event_count": len(run.events),
            "incremental": run.incremental,
            "recount": run.recount,
            "mismatch_count": run.mismatch_count,
            "transcript_sha256": run.summary["transcript"]["transcript_sha256"],
        },
    )
    _write_json(out_path / "aggregate_summary.json", run.summary)
    _write_report(out_path / "report.md", run.summary)
    return run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-protocol",
        description="NB-Polar Phase 5 static protocol synthetic dev gate",
    )
    parser.add_argument("--mode", required=True, choices=["dev-gate"])
    parser.add_argument("--run-seed", required=True, type=int, dest="run_seed")
    parser.add_argument("--blocks", required=True, type=int)
    parser.add_argument("--out", required=True)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_dev_gate(run_seed=args.run_seed, blocks=args.blocks, out_root=args.out)
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase5 dev-gate refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "protocol": summary["protocol"],
                "run_seed": summary["run_seed"],
                "planned_blocks": summary["planned_blocks"],
                "outcome_totals": summary["outcome_totals"],
                "wilson_lower_bound": summary["wilson"]["lower_bound"],
                "candidate": summary["candidate"],
                "out_root": args.out,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
