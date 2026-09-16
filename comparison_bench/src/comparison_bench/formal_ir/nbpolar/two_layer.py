"""NB-Polar Phase 4-P4 two-stage SC operational closed loop (synthetic only).

Frozen point and semantics (packet ``NBPOLAR-PHASE4-P4-TWO-LAYER-OPERATIONAL-SC``,
OpenSpec ``formal-ir-nbpolar-phase4-p4-two-layer-operational-sc``):

- GF32, primitive polynomial 37, alpha 2, natural-order transform; ``N=256``.
- Injected synthetic joint table: source ``A = 32*high + low`` with ``high``,
  ``low`` iid uniform GF32; independent layer-erasure observation
  ``B_high = high`` w.p. ``1-epsilon1`` else uniform,
  ``B_low = low`` w.p. ``1-epsilon2`` else uniform,
  ``B = 32*B_high + B_low``.  With ``A`` and ``B`` both uniform the accepted
  ``[Alice,Bob]`` table is exactly the conditional
  ``f[a,b] = P(B_high=b_h|A_high=a_h) * P(B_low=b_l|A_low=a_l)``, column
  normalized to 1 within ``1e-12``; ``derive_p1``/``derive_p2`` produce the
  metric tables.  Generative/table equivalence: the table-derived ``P1``/``P2``
  rows equal the model conditionals by construction, and per-block sampling
  uses the explicit run-seed RNG (``high``, ``low``, then the two layer
  observations).
- Alice transforms ``U1 = polar_transform(high)`` and ``U2 =
  polar_transform(low)``; ``D1 = sorted(analytic_order(epsilon1, N)[:k1])``
  and ``D2 = sorted(analytic_order(epsilon2, N)[:k2])`` disclose actual GF32
  values including zeros (never sentinels).
- Operational arm (causal, strict): ``P1`` metric from Bob only, provenance
  ``PRIOR_ONLY``, one SC call with the L1 disclosures; the source-domain hard
  candidate ``high_hat = sc1.x_hat``; ``P2_hat`` gathered on Bob and the
  candidate, provenance ``CANDIDATE_CONDITIONED``, one fresh SC call with the
  L2 disclosures; ``low_hat = sc2.x_hat``; ``label_hat = low_hat +
  32*high_hat``; one final 64-bit Toeplitz tag over the MSB-first 10-bit
  expansion with the per-arm/per-block SHA-256 counter-stream seed and arm
  label ``operational``.
- Oracle arm (strictly isolated diagnostic, same block and disclosures):
  ``P2_true`` gathered on Bob and the true high layer, provenance
  ``ORACLE_CONDITIONED``, one fresh SC call with the SAME ``D2/U2[D2]``;
  ``label_oracle = low_hat_oracle + 32*high_true``; one final tag with arm
  label ``oracle``.  Truth enters only the oracle arm, the disclosed-U map and
  scoring; it never enters the operational metric, decoder args or tag.
- No state, APP, belief or partial sum crosses from L1 to L2: the L2 metric is
  gathered from scratch and every SC call is fresh (no warm start, no reuse of
  ``sc1`` objects).
- Outcome buckets per arm (disjoint, exhaustive over planned blocks):
  ``exact`` (tag pass AND label == true label), ``undetected`` (tag pass and
  not exact; never success), ``verify_failed``, ``decode_failed`` (L1 or L2 SC
  exception / nonfinite marginals; no tag for that arm), ``resource_abort``.
  Per-layer sub-buckets are recorded (L1 executed/decode_failed, L2
  invoked/skipped-by-L1-failure/decode_failed, tag invoked).
- Accounting per executed arm: ``5*k1`` L1 disclosure, ``5*k2`` when L2 is
  invoked, ``64`` when the one final tag is invoked; a fully invoked arm totals
  ``5*(k1+k2)+64 = 839``.  Each tag consumes 2623 public seed bits, reported
  separately.  An independent literal transcript recount must equal the
  incremental totals with zero mismatch.
- Truth-isolation sentinel: truth copies are adversarially mutated after the
  metrics and decisions exist; the operational metric and decisions must stay
  bitwise unchanged (violations counted, must be 0).
- Wrong-L1 propagation hook: a documented assessment override forces the L1
  candidate wrong and the operational ``P2_hat`` is compared bitwise against
  ``P2_true``; the per-block ``oracle_candidate_divergence`` flag and its count
  are report-only with no threshold.

Note on the frozen model: because the layer-erasure observation is independent
per layer, the table-derived ``P2`` rows are mathematically independent of the
high symbol (float64 rounding only).  The pre-run injected propagation check and
the focused tests therefore use a hand-built layer-dependent table to prove the
wrong-L1 hook detects real divergence; the frozen run's divergence count stays
report-only.

Only synthetic injected tables: no Model-F stored file, no columnar or
TT-binary reader, no real frame, no method-adapter layer, no scalable decoder
or Phase 7 path, no import-time I/O, no global RNG.  The only output is the
explicit dev-gate CLI below and its five compact scalar-only files; symbols,
labels, disclosed values, decoded keys and raw seed bits are never persisted.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from numbers import Integral, Real
from pathlib import Path

import numpy as np

from ..shared import canonical_event, toeplitz_tag, transcript_summary
from .algebra import make_gf32, validate_symbols
from .construction import analytic_order
from .prior import (
    N_LABELS,
    Provenance,
    build_p1_metrics,
    derive_p1,
    derive_p2,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from .sc import NumericNonfiniteError, sc_decode
from .transform import polar_transform

try:  # POSIX (the frozen command runs under WSL); Windows native has no resource module.
    import resource
except ImportError:  # pragma: no cover - exercised only on Windows native
    resource = None

PROTOCOL_NAME = "nbpolar-two-layer-operational-sc"
MODE = "paired-two-layer-dev-gate"
DEFAULT_Q = 32
ALPHA = 2
DEFAULT_N = 256
DEFAULT_EPSILON1 = 0.05
DEFAULT_EPSILON2 = 0.20
DEFAULT_K1 = 45
DEFAULT_K2 = 110
FROZEN_BLOCKS = 96

# Frozen seeds.  2026091360 is the single authorized run seed and 2026091361
# the public Toeplitz master.  Both were used only as P6-R1 TEST-LOCAL seeds
# (R1_FREEZE.md section 6: "R1 tests use 2026091360..1363"), not as consumed
# official streams; that overlap is recorded for independent review.
FROZEN_RUN_SEED = 2026091360
FROZEN_TOEPLITZ_MASTER = 2026091361
BANNED_RUN_SEEDS = (
    frozenset(range(2026091200, 2026091214))
    | frozenset(range(2026091314, 2026091322))
    | {2026091330, 2026091340, 2026091341, 2026091350, 2026091351}
)

DISCLOSED_BITS_PER_COORDINATE = 5
LABEL_SCALE = 32
LABEL_BITS = 10
TAG_BITS = 64
MESSAGE_BITS = LABEL_BITS * DEFAULT_N  # 2560
SEED_BITS = MESSAGE_BITS + TAG_BITS - 1  # 2623 public control bits per tag
RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 3600.0
EXTERNAL_TIMEOUT_S = 3600
ULIMIT_VIRTUAL_KIB = 2097152

ARMS = ("operational", "oracle")
OUTCOMES = ("exact", "undetected", "verify_failed", "decode_failed", "resource_abort")
SEED_PREFIX = "nbpolar-p4-toeplitz-seed"

CLAIM_SCOPE = (
    "synthetic two-layer interface and cross-layer-propagation development "
    "signal only; this is not real-data FER, leakage efficiency, key rate, "
    "qualification, promotion or f<=1.3 evidence"
)

__all__ = [
    "PROTOCOL_NAME",
    "MODE",
    "DEFAULT_Q",
    "ALPHA",
    "DEFAULT_N",
    "DEFAULT_EPSILON1",
    "DEFAULT_EPSILON2",
    "DEFAULT_K1",
    "DEFAULT_K2",
    "FROZEN_BLOCKS",
    "FROZEN_RUN_SEED",
    "FROZEN_TOEPLITZ_MASTER",
    "BANNED_RUN_SEEDS",
    "DISCLOSED_BITS_PER_COORDINATE",
    "LABEL_SCALE",
    "LABEL_BITS",
    "TAG_BITS",
    "SEED_BITS",
    "seed_bits_for",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "ARMS",
    "OUTCOMES",
    "SEED_PREFIX",
    "validate_run_seed",
    "validate_toeplitz_master",
    "layer_observation_matrix",
    "build_injected_joint_table",
    "layer_metric_tables",
    "disclosure_coordinates",
    "frozen_disclosure_sets",
    "TwoLayerSample",
    "sample_two_layer_block",
    "block_toeplitz_seed_bits",
    "labels_to_bits",
    "injected_wrong_l1_propagation_check",
    "TwoLayerBlockResult",
    "ArmBlockResult",
    "run_two_layer_block",
    "block_events",
    "recount_transcript",
    "TwoLayerRun",
    "run_two_layer_dev_gate",
]


def _as_int(value, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer, got {value!r}")
    out = int(value)
    if minimum is not None and out < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {out}")
    return out


def seed_bits_for(n: int) -> int:
    """Public Toeplitz seed length for block length ``n``: ``10*n + 63``."""
    return LABEL_BITS * _as_int(n, "n", minimum=1) + TAG_BITS - 1


def _checked_epsilon(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, got {value!r}")
    out = float(value)
    if not 0.0 <= out <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1], got {out}")
    return out


def _checked_layer(values, n: int, name: str, alphabet: int = DEFAULT_Q) -> np.ndarray:
    arr = validate_symbols(values, alphabet, name=name)
    if arr.shape[0] != n:
        raise ValueError(f"shape contract: {name} must have length N={n}, got {arr.shape[0]}")
    return arr


def _checked_positions(values, n: int, k: int, name: str) -> np.ndarray:
    arr = np.asarray(values)
    if arr.dtype.kind == "b":
        raise TypeError(f"known-coordinate contract: {name} must hold integers, got boolean input")
    if arr.ndim != 1:
        raise ValueError(f"known-coordinate contract: {name} must be one-dimensional")
    out = arr.astype(np.int64)
    if out.shape != (k,):
        raise ValueError(f"known-coordinate contract: {name} must have length k={k}")
    if k == 0:
        return out
    if out.min() < 0 or out.max() >= n or len(set(out.tolist())) != k:
        raise ValueError(f"known-coordinate contract: {name} must be {k} distinct coordinates in 0..{n - 1}")
    return out


def validate_run_seed(seed) -> int:
    """Return ``seed`` if usable for a Phase 4-P4 run; refuse consumed streams."""
    out = _as_int(seed, "run_seed", minimum=0)
    if out in BANNED_RUN_SEEDS:
        raise ValueError(f"run seed {out} is banned (consumed by Phase 1-6)")
    return out


def validate_toeplitz_master(master) -> int:
    """Return ``master`` if usable as a public Toeplitz master; refuse consumed streams."""
    out = _as_int(master, "toeplitz_master", minimum=0)
    if out in BANNED_RUN_SEEDS:
        raise ValueError(f"toeplitz master {out} is banned (consumed by Phase 1-6)")
    return out


def layer_observation_matrix(epsilon) -> np.ndarray:
    """``(32,32)`` per-layer table ``P(B_layer=y | layer=x)``.

    ``B_layer = x`` w.p. ``1-epsilon`` and uniform over the full GF32 alphabet
    otherwise (rows sum to 1 exactly).
    """
    eps = _checked_epsilon(epsilon, "epsilon")
    mat = np.full((DEFAULT_Q, DEFAULT_Q), eps / DEFAULT_Q, dtype=np.float64)
    idx = np.arange(DEFAULT_Q)
    mat[idx, idx] += 1.0 - eps
    return mat


def build_injected_joint_table(*, epsilon1=DEFAULT_EPSILON1, epsilon2=DEFAULT_EPSILON2) -> np.ndarray:
    """Build the frozen ``[Alice,Bob]`` table explicitly; columns sum to 1 <=1e-12.

    Since ``A`` and ``B`` are both uniform, ``f[a,b] = P(A=a|B=b) =
    P(B=b|A=a)`` factorizes over the two independent layers:
    ``f[a,b] = Ph(b_high|a_high) * Pl(b_low|a_low)``.  No counts, no
    smoothing, no floor and no stored data product are used.
    """
    ph = layer_observation_matrix(epsilon1)
    pl = layer_observation_matrix(epsilon2)
    a_high, a_low = np.arange(N_LABELS) // DEFAULT_Q, np.arange(N_LABELS) % DEFAULT_Q
    b_high, b_low = np.arange(N_LABELS) // DEFAULT_Q, np.arange(N_LABELS) % DEFAULT_Q
    table = ph[a_high[:, None], b_high[None, :]] * pl[a_low[:, None], b_low[None, :]]
    deviation = float(np.abs(table.sum(axis=0) - 1.0).max())
    if deviation > 1e-12:
        raise AssertionError(f"joint table is not column normalized: max deviation {deviation:.3e}")
    return table


def layer_metric_tables(table) -> tuple:
    """Return the accepted ``P1 [U1,B]`` and ``P2 [U1,B,U2]`` metric tables."""
    return derive_p1(table), derive_p2(table)


def disclosure_coordinates(*, n: int = DEFAULT_N, k: int = DEFAULT_K1, epsilon=DEFAULT_EPSILON1) -> np.ndarray:
    """``sorted(analytic_order(epsilon, n)[:k])``; empty when ``k == 0``."""
    n = _as_int(n, "n", minimum=1)
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    k = _as_int(k, "k", minimum=0)
    if k > n:
        raise ValueError(f"k must lie in 0..{n}, got {k}")
    eps = _checked_epsilon(epsilon, "epsilon")
    order = analytic_order(eps, n)
    return np.sort(order[:k]).astype(np.int64)


def frozen_disclosure_sets(
    *,
    n: int = DEFAULT_N,
    k1: int = DEFAULT_K1,
    k2: int = DEFAULT_K2,
    epsilon1=DEFAULT_EPSILON1,
    epsilon2=DEFAULT_EPSILON2,
) -> tuple:
    """The frozen worst-first L1/L2 disclosure sets ``(D1, D2)``."""
    return (
        disclosure_coordinates(n=n, k=k1, epsilon=epsilon1),
        disclosure_coordinates(n=n, k=k2, epsilon=epsilon2),
    )


@dataclass(frozen=True, eq=False)
class TwoLayerSample:
    """One sampled block: layer truth, layer observations and packed Bob symbol."""

    high: np.ndarray  # int64[N] Alice high layer
    low: np.ndarray  # int64[N] Alice low layer
    b_high: np.ndarray  # int64[N] observed high layer
    b_low: np.ndarray  # int64[N] observed low layer
    bob: np.ndarray  # int64[N] = 32*b_high + b_low


def sample_two_layer_block(rng, *, n: int = DEFAULT_N, epsilon1=DEFAULT_EPSILON1, epsilon2=DEFAULT_EPSILON2) -> TwoLayerSample:
    """Sample one injected-model block with the caller-owned explicit RNG.

    Frozen draw order: ``high`` uniform, ``low`` uniform, then the ``B_high``
    observation (erasure mask, then replacement draws for erased positions)
    and the ``B_low`` observation.  No global RNG, no I/O.
    """
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be an explicit numpy.random.Generator (no hidden global RNG)")
    n = _as_int(n, "n", minimum=1)
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    eps1 = _checked_epsilon(epsilon1, "epsilon1")
    eps2 = _checked_epsilon(epsilon2, "epsilon2")

    high = rng.integers(0, DEFAULT_Q, size=n).astype(np.int64)
    low = rng.integers(0, DEFAULT_Q, size=n).astype(np.int64)
    b_high = high.copy()
    erased_high = rng.random(n) < eps1
    if bool(erased_high.any()):
        idx = np.where(erased_high)[0]
        b_high[idx] = rng.integers(0, DEFAULT_Q, size=idx.size).astype(np.int64)
    b_low = low.copy()
    erased_low = rng.random(n) < eps2
    if bool(erased_low.any()):
        idx = np.where(erased_low)[0]
        b_low[idx] = rng.integers(0, DEFAULT_Q, size=idx.size).astype(np.int64)
    return TwoLayerSample(
        high=high,
        low=low,
        b_high=b_high,
        b_low=b_low,
        bob=(LABEL_SCALE * b_high + b_low).astype(np.int64),
    )


def block_toeplitz_seed_bits(
    arm: str,
    block_index: int,
    *,
    master: int = FROZEN_TOEPLITZ_MASTER,
    bit_length: int = SEED_BITS,
) -> np.ndarray:
    """Deterministic public per-arm/per-block Toeplitz seed.

    Rule: concatenate SHA-256 over ``"nbpolar-p4-toeplitz-seed:<master>:
    <arm>:<block_index>:<counter>"`` for ``counter = 0, 1, ...`` (ASCII
    decimal), unpack each digest MSB-first, and truncate to ``bit_length``
    (default ``10*N + 63 = 2623``).  Seed contents are public control and are
    never persisted.
    """
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")
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


def _nonfinite_flag(exc: Exception) -> bool:
    return (
        isinstance(exc, NumericNonfiniteError)
        or "nonfinite" in str(exc).lower()
        or "nan" in str(exc).lower()
    )


def _truth_isolation_sentinel(protected, truth_arrays) -> bool:
    """Mutate every truth buffer in place; True means the protected set stayed bitwise.

    ``truth_arrays`` is a sequence of ``(array, modulus)`` pairs; ``protected``
    is the in-memory metric/decision set that must not alias any truth buffer.
    The caller's inputs are internal copies, never the caller's own arrays.
    """
    snapshots = [np.array(item, copy=True) for item in protected]
    for arr, modulus in truth_arrays:
        arr[...] = (arr + 1) % modulus
    for item, before in zip(protected, snapshots):
        if not np.array_equal(np.asarray(item), before):
            return False
    return True


def _candidate_divergence(p2_hat, p2_true) -> bool:
    """Report-only hook: candidate-conditioned metric differs bitwise from oracle."""
    return bool(not np.array_equal(np.asarray(p2_hat), np.asarray(p2_true)))


def injected_wrong_l1_propagation_check() -> dict:
    """Decoder-free pre-run proof that a forced-wrong L1 changes ``P2_hat``.

    Hand-injected layer-dependent table (not the frozen model): column
    ``b=0`` carries mass on ``A=0`` (high=0, low=0), ``A=1`` (high=0, low=1)
    and ``A=32`` (high=1, low=0) with weights 0.2/0.3/0.5; every other column
    is uniform.  Then ``p2[u1=0, 0, :] = (0.4, 0.6, 0, ...)`` while
    ``p2[u1=1, 0, :] = (1, 0, ...)``, so forcing the candidate wrong changes
    the operational metric and the reconstructed label.  No decoder call is
    made here: the attempt remains consumed by the first gate SC call.
    """
    table = np.full((N_LABELS, N_LABELS), 1.0 / N_LABELS, dtype=np.float64)
    table[:, 0] = 0.0
    table[0, 0] = 0.2
    table[1, 0] = 0.3
    table[LABEL_SCALE, 0] = 0.5
    p2_table = derive_p2(table)
    bob = np.array([[0]], dtype=np.int64)
    high_true = np.array([[1]], dtype=np.int64)
    high_wrong = np.array([[0]], dtype=np.int64)
    p2_true = gather_p2_metrics(bob, high_true, p2_table)[0]
    p2_hat = gather_p2_metrics(bob, high_wrong, p2_table)[0]
    metric_gap = float(np.abs(p2_hat - p2_true).max())
    low_true = np.array([1], dtype=np.int64)
    label_true = (low_true + LABEL_SCALE * high_true).astype(np.int64)
    label_hat = (low_true + LABEL_SCALE * high_wrong).astype(np.int64)
    label_divergent = bool(not np.array_equal(label_hat, label_true))
    return {
        "check": "injected_wrong_l1_propagation",
        "table": (
            "hand-injected column b=0 mass A=0/1/32 = 0.2/0.3/0.5; all other "
            "columns uniform over A"
        ),
        "decoder_calls": 0,
        "candidate_provenance": Provenance.CANDIDATE_CONDITIONED.value,
        "oracle_provenance": Provenance.ORACLE_CONDITIONED.value,
        "metric_max_abs_diff": metric_gap,
        "metric_divergent": bool(_candidate_divergence(p2_hat, p2_true)),
        "label_divergent": label_divergent,
        "passed": bool(
            _candidate_divergence(p2_hat, p2_true) and metric_gap > 0.25 and label_divergent
        ),
    }


@dataclass(frozen=True, eq=False)
class ArmBlockResult:
    """One attempted arm block.  Arrays are in-memory only and never persisted."""

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
    high_hat: np.ndarray | None = None
    low_hat: np.ndarray | None = None
    label_hat: np.ndarray | None = None


@dataclass(frozen=True, eq=False)
class TwoLayerBlockResult:
    """One paired two-layer block: operational arm plus isolated oracle arm."""

    block_index: int
    operational: ArmBlockResult
    oracle: ArmBlockResult
    oracle_candidate_divergence: bool | None
    block_wall_s: float
    # In-memory evidence for tests only; never persisted.
    p1_probs: np.ndarray | None = None
    p2_hat_probs: np.ndarray | None = None
    p2_true_probs: np.ndarray | None = None
    labels_true: np.ndarray | None = None
    u1_disclosed: np.ndarray | None = None
    u2_disclosed: np.ndarray | None = None
    low_hat_oracle: np.ndarray | None = None
    label_oracle: np.ndarray | None = None


def _abort_arm(arm: str) -> ArmBlockResult:
    return ArmBlockResult(
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


def _decode_layer(logp, *, field, positions, disclosed):
    """One fresh SC call plus the nonfinite-marginal fail-closed check."""
    result = sc_decode(
        logp,
        field=field,
        alpha=ALPHA,
        known_positions=positions,
        known_values=disclosed,
    )
    if bool(np.isnan(result.decision_metrics).any()) or bool(np.isposinf(result.decision_metrics).any()):
        raise NumericNonfiniteError("numeric nonfinite failure: invalid decision marginals")
    return result


def run_two_layer_block(
    block_index: int,
    high_true,
    low_true,
    bob,
    *,
    field,
    p1_table,
    p2_table,
    d1,
    d2,
    n: int = DEFAULT_N,
    k1: int = DEFAULT_K1,
    k2: int = DEFAULT_K2,
    toeplitz_master: int = FROZEN_TOEPLITZ_MASTER,
    tag_fn=None,
    l1_candidate_override=None,
    tag_override=None,
) -> TwoLayerBlockResult:
    """Run one paired operational + oracle two-layer block.

    ``tag_fn`` and ``l1_candidate_override``/``tag_override`` are documented
    test/assessment seams; the frozen gate never passes them.  The operational
    path receives only Bob, the candidate and the frozen disclosures; the
    oracle path receives the true high layer only inside its labelled
    diagnostic arm.
    """
    block_index = _as_int(block_index, "block_index", minimum=0)
    n = _as_int(n, "n", minimum=1)
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    k1 = _as_int(k1, "k1", minimum=0)
    k2 = _as_int(k2, "k2", minimum=0)
    if k1 > n or k2 > n:
        raise ValueError(f"k1/k2 must lie in 0..{n}, got k1={k1}, k2={k2}")
    q = int(getattr(field, "q", 0))
    if q != DEFAULT_Q:
        raise ValueError(f"field q {q} != frozen {DEFAULT_Q}")
    master = _as_int(toeplitz_master, "toeplitz_master", minimum=0)
    if tag_fn is None:
        tag_fn = toeplitz_tag
    if tag_override is not None:
        if not isinstance(tag_override, (bytes, bytearray)) or len(bytes(tag_override)) != TAG_BITS // 8:
            raise ValueError(f"tag_override must be {TAG_BITS // 8} bytes")

    high_arr = _checked_layer(high_true, n, "high_true", alphabet=DEFAULT_Q)
    low_arr = _checked_layer(low_true, n, "low_true", alphabet=DEFAULT_Q)
    bob_arr = _checked_layer(bob, n, "bob", alphabet=N_LABELS)
    pos1 = _checked_positions(d1, n, k1, "d1")
    pos2 = _checked_positions(d2, n, k2, "d2")

    u1_true = polar_transform(high_arr, field=field, alpha=ALPHA)
    u2_true = polar_transform(low_arr, field=field, alpha=ALPHA)
    labels_true = (low_arr + LABEL_SCALE * high_arr).astype(np.int64)
    labels_true_bits = labels_to_bits(labels_true)
    u1_disclosed = np.array(u1_true[pos1], copy=True)
    u2_disclosed = np.array(u2_true[pos2], copy=True)

    block_start = time.perf_counter()

    # ---- operational arm: Bob-only P1, one SC call, candidate-conditioned L2.
    op_start = time.perf_counter()
    op_p1_probs = build_p1_metrics(bob_arr[None, :], p1_table)[0]
    op_p1_metric = probs_to_symbol_metric(op_p1_probs, provenance=Provenance.PRIOR_ONLY)
    op_l1_error = None
    op_l2_error = None
    op_l1_failed = False
    op_nonfinite = False
    op_high_hat = None
    op_low_hat = None
    op_label_hat = None
    op_p2_probs = None
    op_p2_provenance = None
    op_label_match = False
    op_tag_pass = False
    op_tag_invoked = False
    try:
        sc1 = _decode_layer(op_p1_metric.logp, field=field, positions=pos1, disclosed=u1_disclosed)
        op_high_hat = np.array(sc1.x_hat, copy=True)
    except Exception as exc:  # SC failure contract: decode_failed, no tag
        op_l1_failed = True
        op_l1_error = type(exc).__name__
        op_nonfinite = _nonfinite_flag(exc)
    else:
        if l1_candidate_override is not None:
            op_high_hat = _checked_layer(l1_candidate_override, n, "l1_candidate_override", alphabet=DEFAULT_Q)

    if op_high_hat is not None:
        op_p2_probs = gather_p2_metrics(bob_arr[None, :], op_high_hat[None, :], p2_table)[0]
        op_p2_metric = probs_to_symbol_metric(
            op_p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED
        )
        op_p2_provenance = op_p2_metric.provenance.value
        seed = block_toeplitz_seed_bits(
            "operational", block_index, master=master, bit_length=seed_bits_for(n)
        )
        try:
            sc2 = _decode_layer(op_p2_metric.logp, field=field, positions=pos2, disclosed=u2_disclosed)
            op_low_hat = np.array(sc2.x_hat, copy=True)
            op_label_hat = (op_low_hat + LABEL_SCALE * op_high_hat).astype(np.int64)
            op_label_match = bool(np.array_equal(op_label_hat, labels_true))
            tag_true = tag_fn(labels_true_bits, seed, TAG_BITS)
            tag_hat = bytes(tag_override) if tag_override is not None else tag_fn(
                labels_to_bits(op_label_hat), seed, TAG_BITS
            )
            op_tag_pass = tag_hat == tag_true
            op_tag_invoked = True
        except Exception as exc:  # SC failure contract: decode_failed, no tag
            op_l2_error = type(exc).__name__
            op_nonfinite = op_nonfinite or _nonfinite_flag(exc)
    op_wall_s = time.perf_counter() - op_start

    if op_l1_failed and l1_candidate_override is not None:
        raise ValueError("l1_candidate_override requires a successful L1 decode")

    op_l2_failed = op_l2_error is not None
    op_l2_invoked = op_high_hat is not None
    if op_l1_failed:
        op_outcome = "decode_failed"
    elif op_l2_failed:
        op_outcome = "decode_failed"
    elif not op_tag_pass:
        op_outcome = "verify_failed"
    elif op_label_match:
        op_outcome = "exact"
    else:
        op_outcome = "undetected"
    op_kdb = (
        DISCLOSED_BITS_PER_COORDINATE * k1
        + (DISCLOSED_BITS_PER_COORDINATE * k2 if op_l2_invoked else 0)
        + (TAG_BITS if op_tag_invoked else 0)
    )
    op_result = ArmBlockResult(
        arm="operational",
        outcome=op_outcome,
        exact=bool(op_outcome == "exact"),
        label_match=op_label_match,
        tag_pass=op_tag_pass,
        l1_provenance=op_p1_metric.provenance.value,
        l2_provenance=op_p2_provenance,
        l1_executed=bool(not op_l1_failed),
        l1_decode_failed=bool(op_l1_failed),
        l2_invoked=bool(op_l2_invoked),
        l2_skipped_by_l1_failure=bool(op_l1_failed),
        l2_decode_failed=bool(op_l2_failed),
        tag_invoked=bool(op_tag_invoked),
        key_dependent_bits=int(op_kdb),
        public_control_bits=int(seed_bits_for(n) if op_tag_invoked else 0),
        nonfinite=bool(op_nonfinite),
        truth_leak_violation=False,  # updated by the sentinel below
        l1_error_type=op_l1_error,
        l2_error_type=op_l2_error,
        wall_s=op_wall_s,
        high_hat=op_high_hat,
        low_hat=op_low_hat,
        label_hat=op_label_hat,
    )

    # ---- oracle arm: true-L1-conditioned diagnostic, same block/disclosures.
    or_start = time.perf_counter()
    or_p2_probs = gather_p2_metrics(bob_arr[None, :], high_arr[None, :], p2_table)[0]
    or_p2_metric = probs_to_symbol_metric(or_p2_probs, provenance=Provenance.ORACLE_CONDITIONED)
    or_l2_error = None
    or_nonfinite = False
    or_low_hat = None
    or_label = None
    or_label_match = False
    or_tag_pass = False
    or_tag_invoked = False
    or_seed = block_toeplitz_seed_bits(
        "oracle", block_index, master=master, bit_length=seed_bits_for(n)
    )
    try:
        sc2o = _decode_layer(or_p2_metric.logp, field=field, positions=pos2, disclosed=u2_disclosed)
        or_low_hat = np.array(sc2o.x_hat, copy=True)
        or_label = (or_low_hat + LABEL_SCALE * high_arr).astype(np.int64)
        or_label_match = bool(np.array_equal(or_label, labels_true))
        tag_true_o = tag_fn(labels_true_bits, or_seed, TAG_BITS)
        tag_hat_o = bytes(tag_override) if tag_override is not None else tag_fn(
            labels_to_bits(or_label), or_seed, TAG_BITS
        )
        or_tag_pass = tag_hat_o == tag_true_o
        or_tag_invoked = True
    except Exception as exc:  # SC failure contract: decode_failed, no tag
        or_l2_error = type(exc).__name__
        or_nonfinite = _nonfinite_flag(exc)
    or_wall_s = time.perf_counter() - or_start

    if or_l2_error is not None:
        or_outcome = "decode_failed"
    elif not or_tag_pass:
        or_outcome = "verify_failed"
    elif or_label_match:
        or_outcome = "exact"
    else:
        or_outcome = "undetected"
    or_kdb = (
        DISCLOSED_BITS_PER_COORDINATE * k1
        + DISCLOSED_BITS_PER_COORDINATE * k2
        + (TAG_BITS if or_tag_invoked else 0)
    )
    or_result = ArmBlockResult(
        arm="oracle",
        outcome=or_outcome,
        exact=bool(or_outcome == "exact"),
        label_match=or_label_match,
        tag_pass=or_tag_pass,
        l1_provenance=None,
        l2_provenance=or_p2_metric.provenance.value,
        l1_executed=True,
        l1_decode_failed=False,
        l2_invoked=True,
        l2_skipped_by_l1_failure=False,
        l2_decode_failed=bool(or_l2_error is not None),
        tag_invoked=bool(or_tag_invoked),
        key_dependent_bits=int(or_kdb),
        public_control_bits=int(seed_bits_for(n) if or_tag_invoked else 0),
        nonfinite=bool(or_nonfinite),
        truth_leak_violation=False,  # updated by the sentinel below
        l1_error_type=None,
        l2_error_type=or_l2_error,
        wall_s=or_wall_s,
        low_hat=or_low_hat,
        label_hat=or_label,
    )

    divergence = None
    if op_p2_probs is not None:
        divergence = _candidate_divergence(op_p2_probs, or_p2_probs)

    # ---- truth-isolation sentinel: mutate truth copies after metrics exist.
    labels_true_out = np.array(labels_true, copy=True)
    protected = [op_p1_metric.logp, or_p2_probs, u1_disclosed, u2_disclosed]
    for item in (op_p2_probs, op_high_hat, op_low_hat, op_label_hat, or_low_hat, or_label):
        if item is not None:
            protected.append(item)
    isolated = _truth_isolation_sentinel(
        protected,
        [(high_arr, DEFAULT_Q), (low_arr, DEFAULT_Q), (u1_true, DEFAULT_Q), (u2_true, DEFAULT_Q), (labels_true, N_LABELS)],
    )
    op_result = dataclasses.replace(op_result, truth_leak_violation=bool(not isolated))
    or_result = dataclasses.replace(or_result, truth_leak_violation=bool(not isolated))

    return TwoLayerBlockResult(
        block_index=block_index,
        operational=op_result,
        oracle=or_result,
        oracle_candidate_divergence=divergence,
        block_wall_s=time.perf_counter() - block_start,
        p1_probs=op_p1_probs,
        p2_hat_probs=op_p2_probs,
        p2_true_probs=or_p2_probs,
        labels_true=labels_true_out,
        u1_disclosed=u1_disclosed,
        u2_disclosed=u2_disclosed,
        low_hat_oracle=or_low_hat,
        label_oracle=or_label,
    )


def _event(
    *,
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
        "frame_key": f"nbpolar-p4-synthetic:{int(block_index)}",
        "method": "nbpolar_two_layer",
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
    result: TwoLayerBlockResult,
    *,
    k1: int = DEFAULT_K1,
    k2: int = DEFAULT_K2,
    n: int = DEFAULT_N,
) -> list:
    """Canonical public transcript events: L1 disclosure, L2 disclosure, final tag.

    One event triple per executed arm, in that order; an arm that fails before
    the tag emits only the disclosures it actually executed.
    """
    seed_length = seed_bits_for(n)
    events: list[dict] = []
    for arm_name, arm in (("operational", result.operational), ("oracle", result.oracle)):
        if arm.outcome == "resource_abort":
            continue
        l1_id = f"block-{int(result.block_index)}-{arm_name}-l1-disclosure"
        events.append(
            _event(
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
                        block_index=result.block_index,
                        event_id=f"block-{int(result.block_index)}-{arm_name}-verification",
                        event_type="verification_tag",
                        direction="alice_to_bob",
                        parent_event_id=l2_id,
                        key_dependent_bits=TAG_BITS,
                        public_control_bits=seed_length,
                        payload={"seed_bit_length": seed_length},
                    )
                )
    return events


def recount_transcript(events) -> dict:
    """Independent literal recount; does not reuse ``transcript_summary``.

    The arm is read literally from the ``block-<i>-<arm>-...`` event id; an
    unknown arm fails closed.  Per-arm totals and event-type counts are
    returned for the mismatch gate.
    """
    counts = {
        arm: {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
        for arm in ARMS
    }
    event_types = {"l1_disclosure": 0, "l2_disclosure": 0, "verification_tag": 0}
    key_dependent = 0
    public_control = 0
    tag_invocations = 0
    for event in events:
        parts = str(event["event_id"]).split("-")
        if len(parts) < 4 or parts[0] != "block" or parts[2] not in ARMS:
            raise ValueError(f"transcript event id is not arm-tagged: {event['event_id']!r}")
        arm = parts[2]
        key = int(event["key_dependent_bits"])
        public = int(event["public_control_bits"])
        key_dependent += key
        public_control += public
        counts[arm]["key_dependent_bits"] += key
        counts[arm]["public_control_bits"] += public
        event_type = str(event["event_type"])
        if event_type not in event_types:
            raise ValueError(f"transcript event type is not frozen: {event_type!r}")
        event_types[event_type] += 1
        if event_type == "verification_tag":
            counts[arm]["tag_invocations"] += 1
            tag_invocations += 1
    return {
        "key_dependent_bits": key_dependent,
        "public_control_bits": public_control,
        "tag_invocations": tag_invocations,
        "event_types": event_types,
        "by_arm": counts,
    }


@dataclass(frozen=True, eq=False)
class TwoLayerRun:
    """In-memory two-layer dev-gate run (also returned by the runner)."""

    results: list
    records: list
    events: list
    incremental: dict
    incremental_by_arm: dict
    recount: dict
    mismatches: list
    summary: dict


def _arm_record(arm: ArmBlockResult) -> dict:
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


def _block_record(result: TwoLayerBlockResult) -> dict:
    return {
        "block_index": int(result.block_index),
        "block_wall_s": round(float(result.block_wall_s), 6),
        "oracle_candidate_divergence": (
            None if result.oracle_candidate_divergence is None else bool(result.oracle_candidate_divergence)
        ),
        "operational": _arm_record(result.operational),
        "oracle": _arm_record(result.oracle),
    }


def _arm_record_consistent(arm: ArmBlockResult, *, k1: int, k2: int, n: int = DEFAULT_N) -> bool:
    """Structural proof of one arm record under the frozen two-layer rules."""
    if arm.outcome not in OUTCOMES:
        return False
    if arm.arm not in ARMS:
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
    if arm.l2_invoked and arm.l2_provenance is None:
        return False
    return True


def _transcript_mismatches(incremental, incremental_by_arm, recount) -> list:
    fields = ("key_dependent_bits", "public_control_bits", "tag_invocations")
    mismatches = []
    for field_name in fields:
        if int(incremental[field_name]) != int(recount[field_name]):
            mismatches.append(
                f"total:{field_name}:{int(incremental[field_name])}!={int(recount[field_name])}"
            )
    for arm in ARMS:
        for field_name in fields:
            left = int(incremental_by_arm[arm][field_name])
            right = int(recount["by_arm"][arm][field_name])
            if left != right:
                mismatches.append(f"{arm}:{field_name}:{left}!={right}")
    return mismatches


def _hard_gates(
    *,
    results,
    blocks: int,
    n: int = DEFAULT_N,
    k1: int,
    k2: int,
    incremental: dict,
    incremental_by_arm: dict,
    recount: dict,
    mismatches,
    pre_check: dict,
) -> dict:
    op = [r.operational for r in results]
    orc = [r.oracle for r in results]
    executed = [r for r in results if r.operational.outcome != "resource_abort"]

    def count(arms, outcome):
        return sum(1 for arm in arms if arm.outcome == outcome)

    l1_ok = sum(1 for arm in op + orc if arm.l1_executed)
    l1_fail = sum(1 for arm in op + orc if arm.l1_decode_failed)
    l2_inv = sum(1 for arm in op + orc if arm.l2_invoked)
    l2_skip = sum(1 for arm in op + orc if arm.l2_skipped_by_l1_failure)
    l2_fail = sum(1 for arm in op + orc if arm.l2_decode_failed)
    tag_inv = sum(1 for arm in op + orc if arm.tag_invoked)
    tag_outcomes = count(op, "exact") + count(op, "undetected") + count(op, "verify_failed")
    tag_outcomes += count(orc, "exact") + count(orc, "undetected") + count(orc, "verify_failed")
    executed_arms = len(executed) * len(ARMS)
    fully_invoked = [
        arm
        for arm in op + orc
        if arm.tag_invoked and arm.l2_invoked and arm.l1_executed
    ]
    fully_exact = all(
        int(arm.key_dependent_bits) == DISCLOSED_BITS_PER_COORDINATE * (k1 + k2) + TAG_BITS
        for arm in fully_invoked
    )
    no_extra_tags = all(
        not (arm.tag_invoked and int(arm.public_control_bits) != seed_bits_for(n))
        for arm in op + orc
    )
    per_record_ok = all(_arm_record_consistent(arm, k1=k1, k2=k2, n=n) for arm in op + orc)
    buckets_ok = all(
        sum(count(arms, name) for name in OUTCOMES) == blocks for arms in (op, orc)
    )
    sub_buckets_ok = (
        l1_ok + l1_fail == executed_arms
        and l2_inv == l1_ok
        and l2_inv + l2_skip == executed_arms
        and l2_fail <= l2_inv
        and tag_inv == tag_outcomes
    )
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
    gates = {
        "paired_coverage_complete": len(results) == blocks and len(executed) == blocks,
        "both_arms_l2_invoked_for_l1_candidates": all(
            (not a.l1_executed) or (a.l2_invoked and b.l2_invoked)
            for a, b in zip(op, orc)
        ),
        "p1_provenance_prior_only": all(
            (not arm.l1_executed) or arm.l1_provenance == Provenance.PRIOR_ONLY.value for arm in op
        ),
        "candidate_provenance_candidate_conditioned": all(
            (not arm.l2_invoked) or arm.l2_provenance == Provenance.CANDIDATE_CONDITIONED.value
            for arm in op
        ),
        "oracle_provenance_oracle_conditioned": all(
            (not arm.l2_invoked) or arm.l2_provenance == Provenance.ORACLE_CONDITIONED.value
            for arm in orc
        ),
        "operational_truth_leak_zero": not any(arm.truth_leak_violation for arm in op),
        "undetected_zero": count(op, "undetected") == 0 and count(orc, "undetected") == 0,
        "nonfinite_zero": not any(arm.nonfinite for arm in op + orc),
        "resource_abort_zero": count(op, "resource_abort") == 0 and count(orc, "resource_abort") == 0,
        "outcome_buckets_disjoint_exhaustive": bool(buckets_ok and sub_buckets_ok and per_record_ok),
        "disclosures_exact": bool(fully_exact and no_extra_tags and per_record_ok),
        "transcript_recount_mismatch_zero": bool(not mismatches and totals_ok),
        "pre_run_injected_wrong_l1_propagation_passed": bool(pre_check.get("passed") is True),
    }
    return gates


def _peak_rss_bytes() -> int | None:
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _frozen_plan(
    *,
    run_seed: int,
    toeplitz_master: int,
    blocks: int,
    n: int,
    epsilon1: float,
    epsilon2: float,
    k1: int,
    k2: int,
    d1,
    d2,
    total_wall_s: float,
) -> dict:
    return {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "run_seed": int(run_seed),
        "toeplitz_master": int(toeplitz_master),
        "planned_blocks": int(blocks),
        "q": DEFAULT_Q,
        "n": int(n),
        "k1": int(k1),
        "k2": int(k2),
        "epsilon1": float(epsilon1),
        "epsilon2": float(epsilon2),
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "model": {
            "generative": (
                "A=32*high+low with high/low iid uniform GF32; B_high=high w.p. "
                "1-epsilon1 else uniform; B_low=low w.p. 1-epsilon2 else uniform; "
                "B=32*B_high+B_low"
            ),
            "table": (
                "f[a,b] = P(B_high=bh|A_high=ah) * P(B_low=bl|A_low=al); A and B "
                "uniform, so f is the accepted [Alice,Bob] conditional; columns sum "
                "to 1 within 1e-12"
            ),
            "generative_table_equivalence": (
                "derive_p1/derive_p2 of the explicit table equal the generative "
                "model conditionals by construction; per-block sampling uses the "
                "run-seed RNG (high, low, then the two layer observations)"
            ),
        },
        "disclosure_rule": (
            "D1 = sorted(analytic_order(epsilon1, n)[:k1]); D2 = "
            "sorted(analytic_order(epsilon2, n)[:k2]); publish actual GF32 "
            "U1[D1]/U2[D2] values including zeros; SC known_positions = the "
            "sorted sets"
        ),
        "disclosure_coordinates": {
            "D1": [int(v) for v in d1],
            "D2": [int(v) for v in d2],
        },
        "arms": list(ARMS),
        "provenance_rules": {
            "p1_operational": Provenance.PRIOR_ONLY.value,
            "p2_operational": Provenance.CANDIDATE_CONDITIONED.value,
            "p2_oracle": Provenance.ORACLE_CONDITIONED.value,
            "truth_allowed_only_in": ["oracle arm", "disclosed-U map", "scoring"],
            "no_app_or_soft_belief": True,
        },
        "restart_rule": (
            "no state/APP/belief/partial-sum transfer: each L2 is a fresh sc_decode "
            "call on a metric gathered from scratch; no warm start and no reuse of "
            "sc1 objects"
        ),
        "outcome_precedence": [
            "resource_abort: block not executed (preregistered budget stop)",
            "decode_failed: L1 or L2 SC exception / nonfinite marginals; no tag for that arm",
            "verify_failed: tag mismatch",
            "exact: tag pass and label == true label",
            "undetected: tag pass and not exact (never success)",
        ],
        "accounting": {
            "l1_disclosure_bits": DISCLOSED_BITS_PER_COORDINATE * int(k1),
            "l2_disclosure_bits": DISCLOSED_BITS_PER_COORDINATE * int(k2),
            "tag_bits": TAG_BITS,
            "fully_invoked_arm_bits": DISCLOSED_BITS_PER_COORDINATE * int(k1 + k2) + TAG_BITS,
            "public_control_bits_per_tag": seed_bits_for(n),
            "recount_rule": "independent literal transcript recount equals the incremental totals",
        },
        "toeplitz": {
            "tag_bits": TAG_BITS,
            "master_seed": int(toeplitz_master),
            "derivation": (
                "MSB-first unpack of SHA-256('nbpolar-p4-toeplitz-seed:<master>:"
                "<arm>:<block_index>:<counter>') concatenated over counter=0,1,...; "
                "truncated to 10*n + 63 bits; public control, never persisted raw"
            ),
            "seed_bits": seed_bits_for(n),
            "arm_labels": list(ARMS),
        },
        "budget": {
            "total_wall_s": float(total_wall_s),
            "external_timeout_s": EXTERNAL_TIMEOUT_S,
            "ulimit_virtual_kib": ULIMIT_VIRTUAL_KIB,
            "rss_bytes_max": RSS_LIMIT_BYTES,
        },
        "refused_run_seeds": sorted(int(v) for v in BANNED_RUN_SEEDS),
        "seed_overlap_note": (
            "2026091360/2026091361 were used only as P6-R1 TEST-LOCAL seeds "
            "(R1_FREEZE.md section 6: R1 tests use 2026091360..1363); they are not "
            "consumed official streams. This overlap is reported for independent "
            "Pre-EXECUTE adjudication."
        ),
        "attempt_consumption_point": "first gate SC call",
        "attempts_allowed": 1,
        "attempts_consumed": 1,
    }


def _counts(arms):
    return {name: sum(1 for arm in arms if arm.outcome == name) for name in OUTCOMES}


def _build_summary(
    *,
    results,
    blocks: int,
    n: int,
    epsilon1: float,
    epsilon2: float,
    k1: int,
    k2: int,
    run_seed: int,
    toeplitz_master: int,
    incremental: dict,
    incremental_by_arm: dict,
    recount: dict,
    mismatches,
    pre_check: dict,
    wall_s: float,
    resource_stop_fired: bool,
) -> dict:
    op = [r.operational for r in results]
    orc = [r.oracle for r in results]
    gates = _hard_gates(
        results=results,
        blocks=blocks,
        n=n,
        k1=k1,
        k2=k2,
        incremental=incremental,
        incremental_by_arm=incremental_by_arm,
        recount=recount,
        mismatches=mismatches,
        pre_check=pre_check,
    )
    executed = sum(1 for arm in op if arm.outcome != "resource_abort")
    error_types: dict[str, int] = {}
    for arm in op + orc:
        if arm.l1_error_type:
            error_types[arm.l1_error_type] = error_types.get(arm.l1_error_type, 0) + 1
        if arm.l2_error_type:
            error_types[arm.l2_error_type] = error_types.get(arm.l2_error_type, 0) + 1
    divergence_defined = sum(1 for r in results if r.oracle_candidate_divergence is not None)
    divergence_count = sum(1 for r in results if r.oracle_candidate_divergence)
    all_pass = all(bool(value) for value in gates.values())
    return {
        "analysis": PROTOCOL_NAME,
        "mode": MODE,
        "run_seed": int(run_seed),
        "toeplitz_master": int(toeplitz_master),
        "planned_blocks": int(blocks),
        "n": int(n),
        "q": DEFAULT_Q,
        "epsilon1": float(epsilon1),
        "epsilon2": float(epsilon2),
        "k1": int(k1),
        "k2": int(k2),
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_peak": _peak_rss_bytes(),
        "resource_stop_fired": bool(resource_stop_fired),
        "attempt_consumption_point": "first gate SC call",
        "attempts_allowed": 1,
        "attempts_consumed_by_this_run": 1,
        "outcome_totals": {"operational": _counts(op), "oracle": _counts(orc)},
        "attempted": {"operational": int(executed), "oracle": int(executed)},
        "coverage": round(executed / blocks, 9),
        "report_only": {
            "exact": {
                "operational": sum(1 for arm in op if arm.exact),
                "oracle": sum(1 for arm in orc if arm.exact),
            },
            "oracle_candidate_divergence_count": int(divergence_count),
            "oracle_candidate_divergence_defined": int(divergence_defined),
            "note": "report-only; no threshold (interface gate, not a performance gate)",
        },
        "accounting": {
            "l1_disclosure_bits_per_arm": DISCLOSED_BITS_PER_COORDINATE * int(k1),
            "l2_disclosure_bits_per_arm": DISCLOSED_BITS_PER_COORDINATE * int(k2),
            "tag_bits": TAG_BITS,
            "fully_invoked_arm_bits": DISCLOSED_BITS_PER_COORDINATE * int(k1 + k2) + TAG_BITS,
            "key_dependent_bits_total": int(incremental["key_dependent_bits"]),
            "public_control_bits_total": int(incremental["public_control_bits"]),
            "public_control_bits_per_tag": seed_bits_for(n),
            "tag_invocations": {
                "operational": int(incremental_by_arm["operational"]["tag_invocations"]),
                "oracle": int(incremental_by_arm["oracle"]["tag_invocations"]),
            },
        },
        "transcript": {
            "event_count": int(sum(recount["event_types"].values())),
            "event_types": dict(recount["event_types"]),
            "incremental": dict(incremental),
            "recount": dict(recount),
            "mismatch_count": int(len(mismatches)),
            "mismatches": list(mismatches),
            "transcript_sha256": None,
        },
        "pre_run_injected_wrong_l1_propagation": dict(pre_check),
        "truth_leak_count": {
            "operational": sum(1 for arm in op if arm.truth_leak_violation),
            "oracle": sum(1 for arm in orc if arm.truth_leak_violation),
        },
        "nonfinite_count": {
            "operational": sum(1 for arm in op if arm.nonfinite),
            "oracle": sum(1 for arm in orc if arm.nonfinite),
        },
        "decode_error_types": error_types,
        "hard_gates": {name: bool(value) for name, value in gates.items()},
        "candidate": "TWO_LAYER_OPERATIONAL_SC_CANDIDATE" if all_pass else None,
        "claim_scope": CLAIM_SCOPE,
    }


def _render_report(summary: dict) -> str:
    totals = summary["outcome_totals"]
    gates = summary["hard_gates"]
    lines = [
        "# NB-Polar Phase 4-P4 two-layer operational SC — synthetic development gate",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- run seed: `{summary['run_seed']}`; Toeplitz master: "
        f"`{summary['toeplitz_master']}`; planned blocks: {summary['planned_blocks']}",
        f"- point: q={summary['q']}, N={summary['n']}, epsilon1={summary['epsilon1']}, "
        f"epsilon2={summary['epsilon2']}, k1={summary['k1']}, k2={summary['k2']}",
        f"- wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes",
        "",
        "## Outcomes (per arm, disjoint and exhaustive)",
        "",
        "| arm | exact | undetected | verify_failed | decode_failed | resource_abort |",
        "|---|---|---|---|---|---|",
    ]
    for arm in ARMS:
        row = totals[arm]
        lines.append(
            f"| {arm} | {row['exact']} | {row['undetected']} | {row['verify_failed']} | "
            f"{row['decode_failed']} | {row['resource_abort']} |"
        )
    lines += [
        "",
        f"- attempt consumption point: {summary['attempt_consumption_point']}; "
        f"attempts consumed by this run: {summary['attempts_consumed_by_this_run']}",
        f"- report-only exact: {summary['report_only']['exact']}; "
        f"oracle/candidate divergence: "
        f"{summary['report_only']['oracle_candidate_divergence_count']} of "
        f"{summary['report_only']['oracle_candidate_divergence_defined']} defined "
        "(no threshold)",
        "",
        "## Accounting",
        "",
        f"- L1 disclosure per arm: {summary['accounting']['l1_disclosure_bits_per_arm']} bits; "
        f"L2 disclosure per arm: {summary['accounting']['l2_disclosure_bits_per_arm']} bits; "
        f"tag: {summary['accounting']['tag_bits']} bits.",
        f"- fully invoked arm: {summary['accounting']['fully_invoked_arm_bits']} bits.",
        f"- key-dependent total: {summary['accounting']['key_dependent_bits_total']}; "
        f"public control total: {summary['accounting']['public_control_bits_total']} "
        f"({summary['accounting']['public_control_bits_per_tag']} bits per tag invocation).",
        f"- transcript events: {summary['transcript']['event_count']} "
        f"{summary['transcript']['event_types']}; recount mismatch count: "
        f"{summary['transcript']['mismatch_count']}.",
        "",
        "## Hard gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in gates.items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        f"- candidate label: `{summary['candidate']}`",
        "",
        f"**Scope:** {summary['claim_scope']}.",
        "",
    ]
    return "\n".join(lines)


def run_two_layer_dev_gate(
    *,
    run_seed,
    toeplitz_master,
    blocks,
    out_root,
    n: int = DEFAULT_N,
    epsilon1=DEFAULT_EPSILON1,
    epsilon2=DEFAULT_EPSILON2,
    k1: int = DEFAULT_K1,
    k2: int = DEFAULT_K2,
    total_wall_s=TOTAL_WALL_S,
) -> TwoLayerRun:
    """Execute the frozen two-layer paired gate and write exactly five files.

    Refuses an existing output root before any decoder call; creates the root
    only after the run.  The single attempt is consumed at the first gate SC
    call (block 0, operational L1).
    """
    out_path = Path(out_root)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    seed = validate_run_seed(run_seed)
    master = validate_toeplitz_master(toeplitz_master)
    blocks = _as_int(blocks, "blocks", minimum=1)
    n = _as_int(n, "n", minimum=1)
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    if n > DEFAULT_N:
        raise ValueError(f"n must not exceed the frozen N={DEFAULT_N}, got {n}")
    k1 = _as_int(k1, "k1", minimum=0)
    k2 = _as_int(k2, "k2", minimum=0)
    if k1 > n or k2 > n:
        raise ValueError(f"k1/k2 must lie in 0..{n}, got k1={k1}, k2={k2}")
    eps1 = _checked_epsilon(epsilon1, "epsilon1")
    eps2 = _checked_epsilon(epsilon2, "epsilon2")
    total_cap = float(total_wall_s)
    if not np.isfinite(total_cap) or total_cap <= 0:
        raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")

    field = make_gf32()
    table = build_injected_joint_table(epsilon1=eps1, epsilon2=eps2)
    p1_table, p2_table = layer_metric_tables(table)
    d1, d2 = frozen_disclosure_sets(n=n, k1=k1, k2=k2, epsilon1=eps1, epsilon2=eps2)

    pre_check = injected_wrong_l1_propagation_check()
    if not pre_check["passed"]:
        raise RuntimeError(f"pre-run injected wrong-L1 propagation check failed: {pre_check}")

    rng = np.random.default_rng(seed)
    results: list = []
    incremental = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    incremental_by_arm = {
        arm: {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
        for arm in ARMS
    }
    events: list = []
    resource_stop_fired = False
    start = time.perf_counter()

    for block_index in range(blocks):
        if time.perf_counter() - start > total_cap:
            resource_stop_fired = True
            for aborted in range(block_index, blocks):
                results.append(
                    TwoLayerBlockResult(
                        block_index=aborted,
                        operational=_abort_arm("operational"),
                        oracle=_abort_arm("oracle"),
                        oracle_candidate_divergence=None,
                        block_wall_s=0.0,
                    )
                )
            break
        sample = sample_two_layer_block(rng, n=n, epsilon1=eps1, epsilon2=eps2)
        result = run_two_layer_block(
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
        events.extend(block_events(result, k1=k1, k2=k2, n=n))
        for arm_name, arm in (("operational", result.operational), ("oracle", result.oracle)):
            if arm.outcome == "resource_abort":
                continue
            for field_name, value in (
                ("key_dependent_bits", int(arm.key_dependent_bits)),
                ("public_control_bits", int(arm.public_control_bits)),
                ("tag_invocations", int(arm.tag_invoked)),
            ):
                incremental[field_name] += value
                incremental_by_arm[arm_name][field_name] += value

    recount = recount_transcript(events)
    mismatches = _transcript_mismatches(incremental, incremental_by_arm, recount)
    summary = _build_summary(
        results=results,
        blocks=blocks,
        n=n,
        epsilon1=eps1,
        epsilon2=eps2,
        k1=k1,
        k2=k2,
        run_seed=seed,
        toeplitz_master=master,
        incremental=incremental,
        incremental_by_arm=incremental_by_arm,
        recount=recount,
        mismatches=mismatches,
        pre_check=pre_check,
        wall_s=time.perf_counter() - start,
        resource_stop_fired=resource_stop_fired,
    )
    summary["transcript"]["transcript_sha256"] = transcript_summary(events)["transcript_sha256"]

    records = [_block_record(result) for result in results]
    plan = _frozen_plan(
        run_seed=seed,
        toeplitz_master=master,
        blocks=blocks,
        n=n,
        epsilon1=eps1,
        epsilon2=eps2,
        k1=k1,
        k2=k2,
        d1=d1,
        d2=d2,
        total_wall_s=total_cap,
    )
    out_path.mkdir(parents=True)
    _write_json(out_path / "frozen_plan.json", plan)
    _write_json(
        out_path / "per_block_two_layer_outcomes.json",
        {"n_blocks": len(records), "blocks": records},
    )
    _write_json(
        out_path / "transcript_accounting.json",
        {
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
            "public_control_bits_per_tag": seed_bits_for(n),
            "transcript_sha256": summary["transcript"]["transcript_sha256"],
        },
    )
    _write_json(out_path / "aggregate_summary.json", summary)
    (out_path / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return TwoLayerRun(
        results=results,
        records=records,
        events=events,
        incremental=incremental,
        incremental_by_arm=incremental_by_arm,
        recount=recount,
        mismatches=mismatches,
        summary=summary,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-two-layer",
        description="NB-Polar Phase 4-P4 two-layer operational SC synthetic dev gate",
    )
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--epsilon1", required=True, type=float)
    parser.add_argument("--epsilon2", required=True, type=float)
    parser.add_argument("--k1", required=True, type=int)
    parser.add_argument("--k2", required=True, type=int)
    parser.add_argument("--blocks", required=True, type=int)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--toeplitz-master", required=True, type=int, dest="toeplitz_master")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_two_layer_dev_gate(
            run_seed=args.seed,
            toeplitz_master=args.toeplitz_master,
            blocks=args.blocks,
            out_root=args.out_dir,
            n=args.n,
            epsilon1=args.epsilon1,
            epsilon2=args.epsilon2,
            k1=args.k1,
            k2=args.k2,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p4 two-layer gate refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "run_seed": summary["run_seed"],
                "planned_blocks": summary["planned_blocks"],
                "outcome_totals": summary["outcome_totals"],
                "candidate": summary["candidate"],
                "out_root": args.out_dir,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
