"""NB-Polar Phase 4-P17 N=32768 operational replication of the P16 f=1.3 gate.

Frozen point (packet ``NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION``,
OpenSpec ``formal-ir-nbpolar-phase4-p0`` P17 delta): independently repeat the
accepted P16 operational measurement at exactly the same target model, N,
construction, disclosure and protocol with 128 fresh DEV blocks. P16's 62/64
is report-only historical context and contributes zero observations to the
P17 decision. There is no second decision arm and no retry arm of any kind.

Frozen semantics:

- Predecessor: before any root is created and before the NPZ content open,
  read P16's accepted ``construction_and_allocation.json`` and verify
  N=32768, K_total=6811, K1=319, K2=6492, valid L1/L2 permutations and the
  canonical construction digest
  ``055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b``
  (recomputed here with the exact P16 canonical recipe). P16 stays
  immutable. Any mismatch stops before any attempt and consumes nothing.
- Input: one call to the accepted ``load_v25_channel_counts(path)``; a
  stat-only size check of exactly ``25,166,822`` bytes happens before the
  content open, and the single artifact read plus the single scientific
  attempt are consumed together at the first NPZ content open (never
  reopened, never rerun; a module-level reopen guard refuses a second
  NPZ-mode call). Refusals (absent root, CLI parse, construction identity,
  K flags, seed grouping, chunk/tag/N contracts) happen before the content
  open; any post-open failure is ``BLOCKED(<earliest gate>)`` with
  consumption already spent.
- Support rule (the only one, exactly P7): column-normalize the raw
  counts, replace every cell below ``1e-15`` by ``1e-15``, renormalize
  each Bob column; ``p_b`` from the column totals; accepted
  ``derive_p1`` / ``derive_p2`` under the packing ``A = 32*U1 + U2``.
- Preconditions before any SC call: no zero Bob column; ``p_b``
  and conditional column error ``<= 1e-12``; raw-MLE in-sample
  population ``H1``/``H2``/total within ``1e-12`` of the V49 1M literals;
  the floor-induced total-entropy change relative to the raw MLE table
  ``<= 1e-9``. Failure is ``BLOCKED(target_population_contract)`` with
  zero SC calls (consumption already spent: the refusal happens after the
  content open, so it is recorded in the stderr message and the freeze
  doc, and best-effort in the pre-created stub files, never as a fresh
  root).
- Matrix: N=32768, GF32 (primitive polynomial 37, alpha 2, natural
  order), chunk_rows=512, planning ``f = 1.3``, tag-bits 64. DEV is eight
  fresh streams ``2026092030..2026092037`` x 16 blocks (128 blocks),
  disjoint from every P16 stream. Each stream restarts its RNG. Per block:
  ``B ~ p_b`` then ``A ~ P_floor(A|B)`` sampled once.
- Construction: NONE exists in this runner. Orders and the ``(K1, K2)``
  allocation arrive only through the verified P16 file and are never
  recomputed, adjusted or extended here.
- DEV (operational, single arm): per block sample once, then (1) disclose
  true U1 at verified ``order1[:K1]`` and run the accepted operational L1
  SC; (2) build L2 metrics only from Bob and the hard L1 candidate (the
  true high layer never enters this metric); (3) disclose true U2 at
  verified ``order2[:K2]`` and restart operational L2 SC; (4) form
  ``label_hat = 32*high_hat + low_hat`` and invoke one 64-bit Toeplitz tag
  whose seed uses the P17 domain prefix (public master ``DEV stream seed
  + 10000``; raw seed bits never persisted); (5) classify exactly one of
  ``exact`` / ``undetected`` / ``verify_failed`` / ``decode_failed`` /
  ``nonfinite`` / ``resource_abort`` with undetected never success.
  Alice truth enters only sampling, disclosed values, tag construction and
  scoring. No second arm and no repeated decode of any block.
- Accounting: a fully invoked block discloses exactly
  ``5*(K1+K2)+64 = 34119`` key-dependent bits with
  ``(5*K_total+64)/(N*H_total) <= 1.3`` asserted from the literals;
  public Toeplitz control is ``10*N+63 = 327743`` bits per invoked tag;
  partial failure counts only actually disclosed bits. An independent
  literal transcript recount must equal the incremental totals with zero
  mismatch.
- Decision over the 128 P17 blocks only:
  ``TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE`` iff
  all integrity gates pass and exact ``>= 121/128`` with one-sided 95%
  Wilson exact-recovery lower bound ``>= 0.90`` (121/128 has LB
  0.9021084760; 120/128 has 0.8924595822);
  ``..._REPLICATION_NOT_CONFIRMED`` iff integrity passes but either
  recovery gate fails; otherwise ``BLOCKED(<earliest>)``.
- Outputs: exactly five scalar-only files (predecessor identity plus
  scalar block outcomes; never counts, sampled symbols, truth vectors,
  decoded labels/keys, metric planes or raw tag seeds), created as stubs
  before the content open and checkpointed after every completed DEV
  block. Per record: wall, RSS HWM, Linux ``VmPeak`` and ``VmSize``. On
  MemoryError/resource failure the checkpoints are preserved, a BLOCKED
  summary is finalized if possible, and the run is never rerun.

No Model-F/held-out/raw/real frame, no other N in the frozen run, no
second arm, no repeated decode, no transform/belief/list decoder, no
FER/efficiency/key-rate qualification or promotion, no commit. The claim
scope is an operational development signal for the frozen V25 1M
population only, sampled from the model, not real-data qualification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from dataclasses import dataclass
from numbers import Integral, Real
from pathlib import Path

import numpy as np

from ..shared import canonical_event, toeplitz_tag
from ..v35_algorithm_development import load_v25_channel_counts
from . import operational_f13 as opf
from .algebra import make_gf32
from .empirical_channel import sample_full_block
from .operational_f13 import classify_operational_outcome, run_operational_block
from .protocol import WILSON_Z, wilson_lower_bound
from .target_construction import (
    PRECONDITION_ORDER,
    TargetPopulationContractError,
    target_preconditions,
)
from .transform import polar_transform
from .two_layer import (
    DISCLOSED_BITS_PER_COORDINATE,
    LABEL_SCALE,
    TAG_BITS,
    labels_to_bits,
    seed_bits_for,
)

PROTOCOL_NAME = "nbpolar-p17-operational-replication-gate"
MODE = "operational-replication-gate"

Q = 32
ALPHA = 2
FROZEN_N = 32768
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
FROZEN_K1 = 319
FROZEN_K2 = 6492
FROZEN_K_TOTAL = 6811
FROZEN_LEAKAGE_BITS = 34119  # 5 * 6811 + 64
FROZEN_DEV_SEEDS = (
    2026092030, 2026092031, 2026092032, 2026092033,
    2026092034, 2026092035, 2026092036, 2026092037,
)
FROZEN_DEV_BLOCKS_PER_STREAM = 16
FROZEN_DEV_TOTAL = 128
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = TAG_BITS  # 64
PUBLIC_TAG_MASTER_OFFSET = 10000
# Every fully invoked block costs one L1 plus one L2 SC attempt.
PLANNED_SC_CALLS_MAX = 2 * FROZEN_DEV_TOTAL
PLANNED_TAG_INVOCATIONS = FROZEN_DEV_TOTAL

EXPECTED_NPZ_BYTES = 25166822
FROZEN_COUNTS_PATH = (
    "/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/"
    "nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz"
)
FROZEN_CONSTRUCTION_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/"
    "operational_f13_gate/construction_and_allocation.json"
)
FROZEN_CONSTRUCTION_DIGEST = (
    "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P17-N32768-OPERATIONAL-REPLICATION/"
    "operational_replication_gate"
)
LOADER_IDENTITY = (
    "comparison_bench.src.comparison_bench.formal_ir."
    "v35_algorithm_development.load_v25_channel_counts"
)

# P16 frozen streams as plain literals (cross-checked against the accepted
# P16 module in the focused tests); the P17 DEV set must avoid all of them.
P16_PRIOR_STREAMS = (
    2026092000, 2026092001, 2026092002, 2026092003,
    2026092010, 2026092011, 2026092012, 2026092013,
    2026092014, 2026092015, 2026092016, 2026092017,
)

# Frozen recovery gates: exact >= 121/128 and one-sided 95% Wilson LB >= 0.90.
EXACT_MIN = 121
WILSON_MIN = 0.90
# Frozen boundary values (rounded to 10 decimals; the runner asserts the
# accepted wilson helper still reproduces them before the first DEV block).
WILSON_LB_121_OF_128 = 0.9021084760
WILSON_LB_120_OF_128 = 0.8924595822
WILSON_BOUNDARY_TOL = 1e-9

PUBLIC_CONTROL_BITS_PER_TAG = seed_bits_for(FROZEN_N)  # 327743

CANDIDATE_LABEL = "TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_CANDIDATE"
NOT_CONFIRMED_LABEL = (
    "TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_REPLICATION_NOT_CONFIRMED"
)

# P16 report-only context (discussion only; zero weight in the P17 decision).
P16_REPORT_EXACT = 62
P16_REPORT_TOTAL = 64
P16_REPORT_WILSON_LB = 0.9098711859

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 2400.0
EXTERNAL_TIMEOUT_S = 2400
ULIMIT_VIRTUAL_KIB = 2097152

ARM = "replication"
METHOD = "nbpolar_operational_f13_replication"
OUTCOMES = ("exact", "undetected", "verify_failed", "decode_failed", "nonfinite", "resource_abort")
SEED_PREFIX = "nbpolar-p17-operational-replication-seed"

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
    "per block: B ~ p_b (rng.random(n) against the cumulative p_b), then "
    "A ~ P_floor(A|B) per coordinate (rng.random(n) against the cumulative "
    "column); high=A//32, low=A%32; one explicit RNG per stream "
    "(np.random.default_rng(stream seed)), blocks sequential, no global RNG; "
    "each DEV block sampled once"
)
TRUTH_BOUNDARY = (
    "Alice truth enters only sampling, disclosed values, tag construction and "
    "scoring; it never enters an undisclosed operational metric, decision or "
    "candidate label; each DEV layer restarts SC with no state transfer; "
    "each DEV L2 metric is gathered from Bob and the hard L1 candidate only"
)
CONSTRUCTION_RULE = (
    "no construction path exists in this runner; L1/L2 orders and the "
    "(K1, K2) allocation arrive only through the verified P16 file "
    "(identity checked before any attempt) and are never recomputed"
)
OPERATIONAL_RULE = (
    "per DEV block: disclose true U1 at verified order1[:K1], operational "
    "L1 SC; L2 metrics from Bob plus the hard L1 candidate only; disclose "
    "true U2 at verified order2[:K2], restarted operational L2 SC; "
    "label_hat=32*high_hat+low_hat; exactly one 64-bit Toeplitz tag in the "
    "P17/N/block seed domain (master DEV seed+10000); exactly one of "
    "exact/undetected/verify_failed/decode_failed/nonfinite/resource_abort; "
    "undetected never success"
)

OUTCOME_PRECEDENCE = [
    "resource_abort: block not executed (preregistered budget stop)",
    "nonfinite: numeric nonfinite failure in L1/L2 SC; no tag",
    "decode_failed: other L1/L2 SC exception; no tag",
    "verify_failed: tag mismatch",
    "exact: tag pass and label == true label",
    "undetected: tag pass and not exact (never success)",
]

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "target_population_contract",
    "construction_frozen_before_dev",
    "dev_coverage_complete",
    "streams_disjoint_frozen",
    "orders_valid_k_replay_f_within_budget",
    "buckets_disjoint_exhaustive",
    "truth_isolation",
    "undetected_zero",
    "nonfinite_zero",
    "no_unregistered_calls",
    "disclosure_recount_exact",
    "attempt_read_accounting_exact",
    "resource_limits_met_and_no_abort",
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "predecessor_construction_identity.json",
    "per_block_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
    "ulimit -v 2097152\n"
    "timeout 2400 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13_replication "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --floor 1e-15 "
    "--n 32768 --k1 319 --k2 6492 "
    f"--construction {FROZEN_CONSTRUCTION_PATH} --construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
    "--dev-seeds 2026092030 2026092031 2026092032 2026092033 "
    "2026092034 2026092035 2026092036 2026092037 --dev-blocks-per-stream 16 "
    "--chunk-rows 512 --tag-bits 64 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)
CLAIM_SCOPE = (
    "frozen V25 1M-population operational replication development signal at "
    "N=32768 only, sampled from the model; P16 blocks are report-only "
    "context and contribute zero observations to this decision; not "
    "held-out or real frame FER, efficiency, key rate, scaling superiority, "
    "qualification or promotion; planning f is not real-channel efficiency; "
    "undetected is never success"
)

# Process-level reopen guard: set at the first NPZ content open, never cleared.
_NPZ_CONTENT_OPENED = False

__all__ = [
    "PROTOCOL_NAME",
    "MODE",
    "Q",
    "ALPHA",
    "FROZEN_N",
    "FROZEN_SOURCE",
    "FROZEN_FLOOR",
    "FROZEN_TARGET_F",
    "FROZEN_K1",
    "FROZEN_K2",
    "FROZEN_K_TOTAL",
    "FROZEN_LEAKAGE_BITS",
    "FROZEN_DEV_SEEDS",
    "FROZEN_DEV_BLOCKS_PER_STREAM",
    "FROZEN_DEV_TOTAL",
    "FROZEN_CHUNK_ROWS",
    "FROZEN_TAG_BITS",
    "PUBLIC_TAG_MASTER_OFFSET",
    "PLANNED_SC_CALLS_MAX",
    "PLANNED_TAG_INVOCATIONS",
    "EXPECTED_NPZ_BYTES",
    "FROZEN_COUNTS_PATH",
    "FROZEN_CONSTRUCTION_PATH",
    "FROZEN_CONSTRUCTION_DIGEST",
    "FROZEN_OUT_ROOT",
    "LOADER_IDENTITY",
    "P16_PRIOR_STREAMS",
    "EXACT_MIN",
    "WILSON_MIN",
    "WILSON_LB_121_OF_128",
    "WILSON_LB_120_OF_128",
    "WILSON_BOUNDARY_TOL",
    "PUBLIC_CONTROL_BITS_PER_TAG",
    "CANDIDATE_LABEL",
    "NOT_CONFIRMED_LABEL",
    "P16_REPORT_EXACT",
    "P16_REPORT_TOTAL",
    "P16_REPORT_WILSON_LB",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S",
    "ULIMIT_VIRTUAL_KIB",
    "ARM",
    "METHOD",
    "OUTCOMES",
    "SEED_PREFIX",
    "ATTEMPT_CONSUMPTION_POINT",
    "ARTIFACT_READ_ACCOUNTING",
    "SUPPORT_RULE",
    "SAMPLING_RULE",
    "TRUTH_BOUNDARY",
    "CONSTRUCTION_RULE",
    "OPERATIONAL_RULE",
    "OUTCOME_PRECEDENCE",
    "INTEGRITY_GATE_ORDER",
    "OUTPUT_FILES",
    "FROZEN_COMMAND",
    "CLAIM_SCOPE",
    "ReplicationResourceError",
    "ReplicationRun",
    "replication_seed_bits",
    "verify_predecessor_construction",
    "check_wilson_boundary",
    "recovery_gates",
    "select_label",
    "replication_block_events",
    "replication_recount_events",
    "run_operational_replication",
    "build_parser",
    "main",
]


class ReplicationResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


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


def _check_n(value) -> int:
    out = _as_int(value, "n", minimum=1)
    if out & (out - 1):
        raise ValueError(f"n must be a positive power of two, got {out}")
    if out != FROZEN_N:
        raise ValueError(f"frozen point requires n={FROZEN_N}, got {out}")
    return out


def _check_k1(value) -> int:
    out = _as_int(value, "k1", minimum=0)
    if out != FROZEN_K1:
        raise ValueError(f"frozen point requires k1={FROZEN_K1}, got {out}")
    return out


def _check_k2(value) -> int:
    out = _as_int(value, "k2", minimum=0)
    if out != FROZEN_K2:
        raise ValueError(f"frozen point requires k2={FROZEN_K2}, got {out}")
    return out


def _check_tag_bits(value) -> int:
    out = _as_int(value, "tag_bits", minimum=1)
    if out != FROZEN_TAG_BITS:
        raise ValueError(f"frozen point requires tag-bits={FROZEN_TAG_BITS}, got {out}")
    return out


def replication_seed_bits(
    master: int,
    n: int,
    block_index: int,
    *,
    bit_length: int | None = None,
) -> np.ndarray:
    """Deterministic public per-block Toeplitz seed (P17 domain).

    Rule: concatenate SHA-256 over
    ``"nbpolar-p17-operational-replication-seed:<master>:<n>:<block_index>:
    <counter>"`` for ``counter = 0, 1, ...`` (ASCII decimal), unpack each
    digest MSB-first, and truncate to ``bit_length`` (default
    ``10*n + 63``). The P17 prefix differs from the P16 one on purpose:
    scored tags in this gate never share the P16 seed domain. Seed
    contents are public control and are never persisted; only the bit
    length is recorded.
    """
    master_seed = _as_int(master, "master", minimum=0)
    n = _as_int(n, "n", minimum=1)
    index = _as_int(block_index, "block_index", minimum=0)
    length = seed_bits_for(n) if bit_length is None else _as_int(bit_length, "bit_length", minimum=1)
    prefix = f"{SEED_PREFIX}:{master_seed}:{int(n)}:{int(index)}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < length:
        buf.extend(hashlib.sha256(f"{prefix}:{counter}".encode("ascii")).digest())
        counter += 1
    bits = np.unpackbits(np.frombuffer(bytes(buf), dtype=np.uint8), bitorder="big")
    return bits[:length].astype(np.uint8)


def _canonical_digest(cell: dict) -> str:
    """Recompute the P16 canonical freeze digest from a construction cell."""
    payload = {
        "n": int(cell["n"]),
        "k_total": int(cell["k_total"]),
        "k1": int(cell["k1"]),
        "k2": int(cell["k2"]),
        "l1_order": [int(v) for v in cell["l1_order"]],
        "l2_order": [int(v) for v in cell["l2_order"]],
        "pooled_e1_mean": [float(v) for v in cell["pooled_e1_mean"]],
        "pooled_h1_mean": [float(v) for v in cell["pooled_h1_mean"]],
        "pooled_e2_mean": [float(v) for v in cell["pooled_e2_mean"]],
        "pooled_h2_mean": [float(v) for v in cell["pooled_h2_mean"]],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def verify_predecessor_construction(construction_path, *, expected_digest: str) -> dict:
    """Verify the accepted P16 construction file before any attempt.

    Checks the P16 protocol marker, N/K1/K2/K_total, valid L1/L2
    permutations, the recomputed canonical digest against both the stored
    freeze digest and the required flag, and the K/f replay from the
    ratified literals. Any mismatch raises before any root exists and
    before the content open, consuming nothing. Returns the scalar
    identity record plus the verified orders for execution.
    """
    path = Path(construction_path)
    if not path.is_file():
        raise FileNotFoundError(f"predecessor construction file not found: {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(f"predecessor construction identity unreadable: {exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("cell"), dict):
        raise ValueError("predecessor construction identity: missing 'cell' mapping")
    if doc.get("protocol") != opf.PROTOCOL_NAME:
        raise ValueError(
            "predecessor construction identity: protocol "
            f"{doc.get('protocol')!r} != accepted {opf.PROTOCOL_NAME!r}"
        )
    if doc.get("frozen_before_first_dev") is not True:
        raise ValueError("predecessor construction identity: not frozen before DEV")
    cell = doc["cell"]
    for key, want in (
        ("n", FROZEN_N),
        ("k_total", FROZEN_K_TOTAL),
        ("k1", FROZEN_K1),
        ("k2", FROZEN_K2),
    ):
        try:
            got = int(cell[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"predecessor construction identity: missing {key}: {exc}"
            ) from exc
        if got != want:
            raise ValueError(
                f"predecessor construction identity: {key} {got} != frozen {want}"
            )
    if not (
        opf._order_is_permutation(cell.get("l1_order"), FROZEN_N)
        and opf._order_is_permutation(cell.get("l2_order"), FROZEN_N)
    ):
        raise ValueError("predecessor construction identity: orders are not valid permutations")
    recomputed = _canonical_digest(cell)
    if str(cell.get("freeze_sha256")) != recomputed:
        raise ValueError("predecessor construction identity: stored digest != recomputed digest")
    if str(expected_digest) != recomputed:
        raise ValueError("predecessor construction identity: digest flag != recomputed digest")
    h_total = float(opf.EXPECTED_H1 + opf.EXPECTED_H2)
    k_replay = math.floor((FROZEN_TARGET_F * FROZEN_N * h_total - TAG_BITS) / 5.0)
    if int(k_replay) != FROZEN_K_TOTAL or FROZEN_K1 + FROZEN_K2 != FROZEN_K_TOTAL:
        raise ValueError("predecessor construction identity: K replay mismatch")
    leakage = DISCLOSED_BITS_PER_COORDINATE * FROZEN_K_TOTAL + TAG_BITS
    if int(leakage) != FROZEN_LEAKAGE_BITS:
        raise ValueError("predecessor construction identity: leakage != 34119")
    if not leakage <= FROZEN_TARGET_F * FROZEN_N * h_total:
        raise ValueError("predecessor construction identity: f exceeds 1.3")
    l1_order = [int(v) for v in cell["l1_order"]]
    l2_order = [int(v) for v in cell["l2_order"]]
    return {
        "record": {
            "protocol": PROTOCOL_NAME,
            "predecessor_protocol": opf.PROTOCOL_NAME,
            "construction_path": str(path),
            "digest_expected": str(expected_digest),
            "digest_recomputed": recomputed,
            "digest_match": True,
            "n": FROZEN_N,
            "k_total": FROZEN_K_TOTAL,
            "k1": FROZEN_K1,
            "k2": FROZEN_K2,
            "leakage_bits": int(leakage),
            "f": float(leakage / (FROZEN_N * h_total)),
            "predecessor_dev_seeds": list(cell.get("dev_seeds", [])),
            "l1_len": len(l1_order),
            "l2_len": len(l2_order),
            "l1_head8": l1_order[:8],
            "l2_head8": l2_order[:8],
        },
        "l1_order": l1_order,
        "l2_order": l2_order,
    }


def check_wilson_boundary() -> dict:
    """Assert the accepted Wilson helper still reproduces the frozen boundary.

    Fail-closed code-level pin: 121/128 must round to 0.9021084760 (pass)
    and 120/128 must round to 0.8924595822 (fail). Any drift raises.
    """
    lb121 = float(wilson_lower_bound(EXACT_MIN, FROZEN_DEV_TOTAL, z=WILSON_Z))
    lb120 = float(wilson_lower_bound(EXACT_MIN - 1, FROZEN_DEV_TOTAL, z=WILSON_Z))
    if abs(lb121 - WILSON_LB_121_OF_128) > WILSON_BOUNDARY_TOL:
        raise ValueError(
            f"Wilson boundary drift: 121/128 LB {lb121!r} != frozen {WILSON_LB_121_OF_128!r}"
        )
    if abs(lb120 - WILSON_LB_120_OF_128) > WILSON_BOUNDARY_TOL:
        raise ValueError(
            f"Wilson boundary drift: 120/128 LB {lb120!r} != frozen {WILSON_LB_120_OF_128!r}"
        )
    return {"lb_121_of_128": lb121, "lb_120_of_128": lb120}


def recovery_gates(exact_count: int, total: int = FROZEN_DEV_TOTAL) -> dict:
    """Frozen scientific gates over the 128 P17 DEV outcomes (pure, no I/O).

    The total is pinned to 128: any other total (in particular the P16
    62/64 context) fails the count gate by structure and can never enter
    this decision.
    """
    exact_count = _as_int(exact_count, "exact_count", minimum=0)
    total = _as_int(total, "total", minimum=0)
    if exact_count > total:
        raise ValueError(f"exact_count {exact_count} must not exceed total {total}")
    lb = float(wilson_lower_bound(exact_count, total, z=WILSON_Z)) if total else 0.0
    exact_ok = bool(total == FROZEN_DEV_TOTAL and exact_count >= EXACT_MIN)
    wilson_ok = bool(lb >= WILSON_MIN)
    return {
        "exact_count": int(exact_count),
        "total": int(total),
        "wilson_z": float(WILSON_Z),
        "wilson_lower_bound": float(lb),
        "wilson_min": float(WILSON_MIN),
        "exact_at_least_121_of_128": exact_ok,
        "wilson_lower_bound_at_least_0p90": wilson_ok,
        "boundary_121_of_128": float(WILSON_LB_121_OF_128),
        "boundary_120_of_128": float(WILSON_LB_120_OF_128),
        "pass": bool(exact_ok and wilson_ok),
    }


def select_label(gates: dict, recovery_pass: bool) -> str:
    """Frozen label selection: candidate / not-confirmed / earliest BLOCKED."""
    failing = [name for name in INTEGRITY_GATE_ORDER if not gates.get(name, False)]
    if not failing:
        return CANDIDATE_LABEL if recovery_pass else NOT_CONFIRMED_LABEL
    return f"BLOCKED({failing[0]})"


def _p17_event(
    *,
    n: int,
    stream_seed: int,
    block_gidx: int,
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
        "frame_key": f"nbpolar-p17-operational-replication:{int(n)}:{int(stream_seed)}:{int(block_gidx)}",
        "method": METHOD,
        "event_type": event_type,
        "direction": direction,
        "parent_event_id": parent_event_id,
        "pass_id": 0,
        "block_id": int(block_gidx),
        "key_dependent_bits": int(key_dependent_bits),
        "public_control_bits": int(public_control_bits),
        "payload": payload,
    }
    canonical_event(event)  # fail closed on malformed or secret-bearing payloads
    return event


def replication_block_events(n: int, stream_seed: int, block_gidx: int, result) -> list:
    """Canonical public transcript events: L1, L2 (when invoked), final tag."""
    if result.outcome == "resource_abort":
        return []
    k1, k2 = int(result.k1), int(result.k2)
    events: list[dict] = []
    l1_id = f"block-{int(n)}-{int(block_gidx)}-{ARM}-l1-disclosure"
    events.append(
        _p17_event(
            n=n,
            stream_seed=stream_seed,
            block_gidx=block_gidx,
            event_id=l1_id,
            event_type="l1_disclosure",
            direction="alice_to_bob",
            parent_event_id=None,
            key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k1,
            public_control_bits=0,
            payload={},
        )
    )
    if result.l2_invoked:
        l2_id = f"block-{int(n)}-{int(block_gidx)}-{ARM}-l2-disclosure"
        events.append(
            _p17_event(
                n=n,
                stream_seed=stream_seed,
                block_gidx=block_gidx,
                event_id=l2_id,
                event_type="l2_disclosure",
                direction="alice_to_bob",
                parent_event_id=l1_id,
                key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k2,
                public_control_bits=0,
                payload={},
            )
        )
        if result.tag_invoked:
            events.append(
                _p17_event(
                    n=n,
                    stream_seed=stream_seed,
                    block_gidx=block_gidx,
                    event_id=f"block-{int(n)}-{int(block_gidx)}-{ARM}-verification",
                    event_type="verification_tag",
                    direction="alice_to_bob",
                    parent_event_id=l2_id,
                    key_dependent_bits=TAG_BITS,
                    public_control_bits=seed_bits_for(n),
                    payload={"seed_bit_length": seed_bits_for(n)},
                )
            )
    return events


def replication_recount_events(events) -> dict:
    """Independent literal recount; N and arm are read literally from the event id."""
    totals = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    event_types = {"l1_disclosure": 0, "l2_disclosure": 0, "verification_tag": 0}
    for event in events:
        parts = str(event["event_id"]).split("-")
        if len(parts) < 5 or parts[0] != "block" or parts[3] != ARM:
            raise ValueError(f"transcript event id is not N/arm-tagged: {event['event_id']!r}")
        key = int(event["key_dependent_bits"])
        public = int(event["public_control_bits"])
        totals["key_dependent_bits"] += key
        totals["public_control_bits"] += public
        event_type = str(event["event_type"])
        if event_type not in event_types:
            raise ValueError(f"transcript event type is not frozen: {event_type!r}")
        event_types[event_type] += 1
        if event_type == "verification_tag":
            totals["tag_invocations"] += 1
    return {
        "key_dependent_bits": totals["key_dependent_bits"],
        "public_control_bits": totals["public_control_bits"],
        "tag_invocations": totals["tag_invocations"],
        "event_types": dict(event_types),
    }


@dataclass(frozen=True, eq=False)
class ReplicationRun:
    """In-memory P17 replication run (also returned by the runner)."""

    records: list
    events: list
    construction: dict
    plan: dict
    summary: dict


def _stub_plan(*, out_path, source, floor, n, k1, k2, construction, digest,
               dev_list, dev_bps, chunk_rows, tag_bits, identity) -> dict:
    h_total = float(opf.EXPECTED_H1 + opf.EXPECTED_H2)
    return {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "out_root": str(out_path),
        "source": source,
        "counts_path": FROZEN_COUNTS_PATH,
        "expected_npz_bytes": EXPECTED_NPZ_BYTES,
        "loader": LOADER_IDENTITY,
        "support_rule": SUPPORT_RULE,
        "sampling_rule": SAMPLING_RULE,
        "truth_boundary": TRUTH_BOUNDARY,
        "construction_rule": CONSTRUCTION_RULE,
        "operational_rule": OPERATIONAL_RULE,
        "outcome_precedence": list(OUTCOME_PRECEDENCE),
        "q": Q,
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "n": int(n),
        "floor": float(floor),
        "target_f": float(FROZEN_TARGET_F),
        "k1": int(k1),
        "k2": int(k2),
        "k_total": int(k1) + int(k2),
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "dev_seeds": [int(s) for s in dev_list],
        "dev_blocks_per_stream": int(dev_bps),
        "dev_total": int(len(dev_list) * int(dev_bps)),
        "predecessor": {
            "construction_path": str(construction),
            "construction_digest": str(digest),
            "identity": dict(identity),
        },
        "predecessor_report_only": {
            "p16_exact": P16_REPORT_EXACT,
            "p16_total": P16_REPORT_TOTAL,
            "p16_wilson_lb": P16_REPORT_WILSON_LB,
            "pooled_into_decision": False,
        },
        "tag_master_rule": "DEV stream seed + 10000",
        "tag_seed_domain": f"{SEED_PREFIX}:<master>:<n>:<block_index>",
        "public_control_bits_per_tag": int(seed_bits_for(int(n))),
        "entropy_expectations": {
            "h1": opf.EXPECTED_H1,
            "h2": opf.EXPECTED_H2,
            "total": opf.EXPECTED_TOTAL,
            "entropy_tol": opf.ENTROPY_TOL,
            "column_tol": opf.COLUMN_TOL,
            "floor_entropy_change_tol": opf.FLOOR_ENTROPY_TOL,
        },
        "recovery_gates": {
            "exact_min": EXACT_MIN,
            "dev_total": FROZEN_DEV_TOTAL,
            "wilson_z": float(WILSON_Z),
            "wilson_min": float(WILSON_MIN),
            "boundary_121_of_128": float(WILSON_LB_121_OF_128),
            "boundary_120_of_128": float(WILSON_LB_120_OF_128),
        },
        "precondition_order": list(PRECONDITION_ORDER),
        "integrity_gate_order": list(INTEGRITY_GATE_ORDER),
        "decision": {
            "candidate": CANDIDATE_LABEL,
            "not_confirmed": NOT_CONFIRMED_LABEL,
            "blocked": "BLOCKED(<earliest gate>)",
        },
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
        "artifact_read_accounting": dict(ARTIFACT_READ_ACCOUNTING),
        "budget": {
            "total_wall_s": float(TOTAL_WALL_S),
            "external_timeout_s": EXTERNAL_TIMEOUT_S,
            "ulimit_virtual_kib": ULIMIT_VIRTUAL_KIB,
            "rss_bytes_max": RSS_LIMIT_BYTES,
            "env": {
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
                "MALLOC_ARENA_MAX": "2",
            },
        },
        "output_files": list(OUTPUT_FILES),
        "frozen_command": FROZEN_COMMAND,
        "claim_scope": CLAIM_SCOPE,
    }


def _render_report(summary: dict) -> str:
    lines = [
        "# NB-Polar Phase 4-P17 N=32768 operational replication of the P16 f=1.3 gate",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- source/target: `{summary['source']}`; q={summary['q']}, n={summary['n']}, "
        f"K1={summary['k1']}, K2={summary['k2']}, chunk_rows={summary['chunk_rows']}, "
        f"tag_bits={summary['tag_bits']}",
        f"- DEV streams x blocks: {summary['dev_blocks_per_stream']} each "
        f"({summary['dev_total']} blocks, fresh relative to P16)",
        f"- wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes; "
        f"resource stop fired: {summary['resource_stop_fired']}",
        "",
        "## Target population contract",
        "",
    ]
    entropy = summary["entropy"]
    lines += [
        f"- H1: {entropy['h1']!r} (expected {entropy['expected_h1']!r})",
        f"- H2: {entropy['h2']!r} (expected {entropy['expected_h2']!r})",
        f"- total: {entropy['total']!r} (expected {entropy['expected_total']!r})",
        f"- floored-table total: {entropy['floor_total']!r}; floor-induced change: "
        f"{entropy['floor_entropy_change']!r}",
        f"- column deviation: {entropy['column_dev']!r}; p_b sum: {entropy['p_b_sum']!r}",
        "",
        "## Predecessor construction identity (verified before any attempt)",
        "",
    ]
    identity = summary["identity"]
    lines += [
        f"- P16 file: `{identity['construction_path']}`",
        f"- canonical digest: `{identity['digest_recomputed']}` "
        f"(match: {identity['digest_match']})",
        f"- N={identity['n']}, K_total={identity['k_total']}, "
        f"K1={identity['k1']}, K2={identity['k2']}",
        f"- leakage bits: {identity['leakage_bits']}; f: {identity['f']!r} (<= 1.3 required)",
        "",
        "## Predecessor context (report-only; never pooled into the decision)",
        "",
        f"- P16 DEV: {summary['predecessor_report_only']['p16_exact']}/"
        f"{summary['predecessor_report_only']['p16_total']} exact, Wilson LB "
        f"{summary['predecessor_report_only']['p16_wilson_lb']!r} (zero-count margin).",
        "- These P16 observations contribute zero weight to the gates below; "
        "the decision uses exactly the 128 P17 blocks.",
        "",
        "## DEV operational outcomes (128 P17 blocks)",
        "",
        "| outcome | count |",
        "|---|---|",
    ]
    for name in OUTCOMES:
        lines.append(f"| {name} | {summary['outcome_counts'][name]} |")
    recovery = summary["recovery"]
    lines += [
        "",
        f"- exact fraction: {summary['exact_count']}/128 = {summary['exact_fraction']!r}",
        f"- one-sided 95% Wilson LB: {recovery['wilson_lower_bound']!r} "
        f"(>= 0.90 required; 121/128 boundary {recovery['boundary_121_of_128']!r}, "
        f"120/128 boundary {recovery['boundary_120_of_128']!r})",
        "",
        "## Disclosure and verification accounting",
        "",
        f"- key-dependent bits: {summary['disclosure']['key_dependent_bits']}",
        f"- public control bits: {summary['disclosure']['public_control_bits']}",
        f"- tag invocations: {summary['disclosure']['tag_invocations']}",
        f"- transcript recount mismatches: {summary['disclosure']['mismatches']}",
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
        f"- outcome label: `{summary['outcome_label']}`",
        "",
        f"**Scope:** {summary['claim_scope']}.",
        "",
    ]
    return "\n".join(lines)


def run_operational_replication(
    *,
    counts=None,
    counts_path=FROZEN_COUNTS_PATH,
    source: str = FROZEN_SOURCE,
    floor=FROZEN_FLOOR,
    n: int = FROZEN_N,
    k1: int = FROZEN_K1,
    k2: int = FROZEN_K2,
    construction=FROZEN_CONSTRUCTION_PATH,
    construction_digest: str = FROZEN_CONSTRUCTION_DIGEST,
    dev_seeds=FROZEN_DEV_SEEDS,
    dev_blocks_per_stream: int = FROZEN_DEV_BLOCKS_PER_STREAM,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    tag_bits: int = FROZEN_TAG_BITS,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_entropies=None,
) -> ReplicationRun:
    """Execute the frozen P17 operational replication; write five files.

    ``counts`` and ``expected_entropies`` are documented injected test
    seams; the frozen CLI passes only the frozen point and reads the V25
    NPZ through the accepted loader exactly once.
    """
    global _NPZ_CONTENT_OPENED
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    floor = _check_floor(floor)
    if floor != FROZEN_FLOOR:
        raise ValueError(f"frozen point requires floor={FROZEN_FLOOR}, got {floor}")
    if source != FROZEN_SOURCE:
        raise ValueError(f"frozen point requires source={FROZEN_SOURCE!r}, got {source!r}")
    n = _check_n(n)
    k1 = _check_k1(k1)
    k2 = _check_k2(k2)
    opf._check_chunk_contract(chunk_rows)
    _check_tag_bits(tag_bits)
    # Predecessor identity is verified before any root exists and before
    # the content open; a mismatch consumes nothing. The digest flag must
    # name the frozen P16 digest; the verifier then pins the flag to the
    # file's recomputed digest.
    if str(construction_digest) != FROZEN_CONSTRUCTION_DIGEST:
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = verify_predecessor_construction(construction, expected_digest=construction_digest)
    identity = verified["record"]
    l1_order = np.asarray(verified["l1_order"], dtype=np.int64)
    l2_order = np.asarray(verified["l2_order"], dtype=np.int64)
    dev_list = [_as_int(s, "dev seed", minimum=0) for s in dev_seeds]
    dev_bps = _as_int(dev_blocks_per_stream, "dev-blocks-per-stream", minimum=1)
    if len(dev_list) != len(FROZEN_DEV_SEEDS):
        raise ValueError(
            f"dev-seeds must hold exactly {len(FROZEN_DEV_SEEDS)} streams, "
            f"got {len(dev_list)}"
        )
    # Non-frozen groupings are not refused here: they run but fail the
    # exact-stream gates (dev_coverage_complete / streams_disjoint_frozen).
    if int(dev_bps) != FROZEN_DEV_BLOCKS_PER_STREAM:
        raise ValueError(
            "dev-blocks-per-stream must be "
            f"{FROZEN_DEV_BLOCKS_PER_STREAM}, got {int(dev_bps)}"
        )
    if len(set(dev_list)) != len(dev_list):
        raise ValueError("dev stream seeds must be distinct")
    if not set(int(s) for s in dev_list).isdisjoint(int(s) for s in P16_PRIOR_STREAMS):
        raise ValueError("P17 DEV streams must avoid every P16 stream")
    cap = float(total_wall_s)
    if not np.isfinite(cap) or cap <= 0:
        raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")

    plan = _stub_plan(
        out_path=out_path, source=source, floor=floor, n=n, k1=k1, k2=k2,
        construction=construction, digest=construction_digest,
        dev_list=dev_list, dev_bps=dev_bps, chunk_rows=chunk_rows,
        tag_bits=tag_bits, identity=identity,
    )

    # ---- create all five files BEFORE the content open (stub inventory).
    out_path.mkdir(parents=True)
    frozen_before_dev = True
    try:
        opf._write_json(out_path / "frozen_plan.json", plan)
        opf._write_json(out_path / "predecessor_construction_identity.json", identity)
        (out_path / "per_block_outcomes.jsonl").write_text("", encoding="utf-8")
        opf._write_json(
            out_path / "aggregate_summary.json",
            {"protocol": PROTOCOL_NAME, "status": "pending_content_open"},
        )
        (out_path / "report.md").write_text(
            "# NB-Polar Phase 4-P17 N=32768 operational replication of the P16 f=1.3 gate\n\n"
            "status: pending_content_open\n",
            encoding="utf-8",
        )

        # ---- input: stat-only check, then the single accepted content open.
        if counts is None:
            if _NPZ_CONTENT_OPENED:
                raise ValueError("reopen refused: the single NPZ content open was already consumed")
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
            _NPZ_CONTENT_OPENED = True
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

        # ---- frozen preconditions: no SC call may happen before this passes.
        if expected_entropies is None:
            expected_h1, expected_h2, expected_total = (
                opf.EXPECTED_H1, opf.EXPECTED_H2, opf.EXPECTED_TOTAL,
            )
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
        # Code-level pin: the accepted Wilson helper must still reproduce the
        # frozen 121/128 (pass) and 120/128 (fail) boundary values.
        boundary = check_wilson_boundary()
        field = make_gf32()
        start = time.perf_counter()

        calls = {"sc": 0}
        dev_records: list[dict] = []
        dev_events: list[dict] = []
        incremental = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
        provenance_violations = 0
        resource_stop: str | None = None

        def checkpoint(summary_doc: dict) -> None:
            opf._write_json(out_path / "predecessor_construction_identity.json", identity)
            opf._write_json(out_path / "aggregate_summary.json", summary_doc)
            (out_path / "report.md").write_text(_render_report(summary_doc), encoding="utf-8")

        def partial_summary(outcome_label: str, gates: dict, failing: list) -> dict:
            outcome_counts = {name: 0 for name in OUTCOMES}
            for record in dev_records:
                if record.get("outcome") in outcome_counts:
                    outcome_counts[record["outcome"]] += 1
            exact_count = int(outcome_counts["exact"])
            recovery = recovery_gates(exact_count)
            try:
                recount = replication_recount_events(dev_events)
            except ValueError:
                recount = {
                    "key_dependent_bits": None,
                    "public_control_bits": None,
                    "tag_invocations": None,
                    "event_types": {},
                }
            return {
                "analysis": PROTOCOL_NAME,
                "mode": MODE,
                "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "repository": "HD-QKD_Polar_Comparison-nbpolar",
                "source": source,
                "counts_path": accounting.get("counts_path"),
                "input_mode": accounting.get("input_mode"),
                "q": Q,
                "n": int(n),
                "k1": int(k1),
                "k2": int(k2),
                "k_total": int(k1) + int(k2),
                "target_f": float(FROZEN_TARGET_F),
                "chunk_rows": int(chunk_rows),
                "tag_bits": int(tag_bits),
                "dev_seeds": [int(s) for s in dev_list],
                "dev_blocks_per_stream": int(dev_bps),
                "dev_total": int(len(dev_list) * int(dev_bps)),
                "identity": dict(identity),
                "predecessor_report_only": {
                    "p16_exact": P16_REPORT_EXACT,
                    "p16_total": P16_REPORT_TOTAL,
                    "p16_wilson_lb": P16_REPORT_WILSON_LB,
                    "pooled_into_decision": False,
                },
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
                        "entropy": opf.ENTROPY_TOL,
                        "column": opf.COLUMN_TOL,
                        "floor_entropy_change": opf.FLOOR_ENTROPY_TOL,
                    },
                    "checks": dict(precondition_report.checks),
                    "column_dev": float(precondition_report.column_dev),
                    "p_b_sum": float(np.sum(precondition_report.p_b)),
                },
                "outcome_counts": {name: int(outcome_counts[name]) for name in OUTCOMES},
                "exact_count": int(exact_count),
                "exact_fraction": (float(exact_count) / float(len(dev_list) * int(dev_bps))
                                    if dev_records else 0.0),
                "recovery": recovery,
                "wilson_boundary_check": dict(boundary),
                "dev_block_count": int(len(dev_records)),
                "sc_calls": int(calls["sc"]),
                "planned_sc_calls_max": int(PLANNED_SC_CALLS_MAX),
                "tag_invocations": int(incremental["tag_invocations"]),
                "planned_tag_invocations": int(PLANNED_TAG_INVOCATIONS),
                "provenance_violations": int(provenance_violations),
                "disclosure": {
                    "key_dependent_bits": int(incremental["key_dependent_bits"]),
                    "public_control_bits": int(incremental["public_control_bits"]),
                    "tag_invocations": int(incremental["tag_invocations"]),
                    "recount": recount,
                    "mismatches": opf._transcript_mismatches(incremental, recount)
                    if recount["key_dependent_bits"] is not None else ["recount_unavailable"],
                },
                "integrity": {name: bool(gates.get(name, False)) for name in INTEGRITY_GATE_ORDER},
                "integrity_all_pass": bool(all(gates.get(name, False) for name in INTEGRITY_GATE_ORDER)),
                "failing_integrity_gates": list(failing),
                "outcome_label": outcome_label,
                "wall_s": round(float(time.perf_counter() - start), 6),
                "rss_bytes_peak": opf._peak_rss_bytes(),
                "resource_stop_fired": bool(resource_stop is not None),
                "resource_stop_reason": resource_stop,
                "attempt_read_accounting": dict(accounting),
                "claim_scope": CLAIM_SCOPE,
            }

        def current_gates(*, final: bool) -> tuple:
            gates = _integrity_gates(
                out_path=out_path,
                n=n,
                dev_list=dev_list,
                dev_bps=dev_bps,
                identity=identity,
                frozen_before_dev=frozen_before_dev,
                k1=k1,
                k2=k2,
                l1_order=l1_order,
                l2_order=l2_order,
                dev_records=dev_records,
                dev_events=dev_events,
                calls=calls,
                incremental=incremental,
                accounting=accounting,
                provenance_violations=provenance_violations,
                start=start,
                cap=cap,
                resource_stop=resource_stop,
                counts_shape=counts_arr.shape,
                precondition_passed=bool(precondition_report.passed),
                final=final,
            )
            failing = [g for g in INTEGRITY_GATE_ORDER if not gates[g]]
            return gates, failing

        # ---- DEV: one operational block per stream slot, checkpoint every block.
        gidx = 0
        stream_rngs: dict[int, np.random.Generator] = {}
        dev_positions = [(seed, block_index) for seed in dev_list for block_index in range(int(dev_bps))]
        for seed, block_index in dev_positions:
            reason = opf._budget_exceeded(start, cap)
            if reason is not None:
                resource_stop = reason
                for rest_seed, rest_block in dev_positions[gidx:]:
                    abort = opf._abort_block(rest_seed, rest_block, k1=k1, k2=k2)
                    record = opf._block_record(abort, resources=opf._cell_resource_record(0.0))
                    dev_records.append(record)
                    opf._append_jsonl(out_path / "per_block_outcomes.jsonl", record)
                    gates_now, failing_now = current_gates(final=False)
                    checkpoint(partial_summary(f"RUNNING(dev {len(dev_records)}/128)", gates_now, failing_now))
                    gidx += 1
                break
            # Each stream restarts its RNG; slots of a stream are sequential,
            # so one cached RNG per stream is exactly the frozen draw order.
            rng = stream_rngs.get(int(seed))
            if rng is None:
                rng = stream_rngs[int(seed)] = np.random.default_rng(int(seed))
            bob, _a_full, high, low = sample_full_block(
                rng, entropy.p_b, entropy.f, Q, Q, n
            )
            u1 = polar_transform(high, field=field, alpha=ALPHA)
            u2 = polar_transform(low, field=field, alpha=ALPHA)
            labels_true = (low + LABEL_SCALE * high).astype(np.int64)
            labels_true_bits = labels_to_bits(labels_true)
            master = int(seed) + PUBLIC_TAG_MASTER_OFFSET
            p17_seed = replication_seed_bits(master, n, gidx, bit_length=seed_bits_for(n))

            def _tag_fn(bits, _seed, tag_bits, _fixed=p17_seed):
                return toeplitz_tag(bits, _fixed, tag_bits)

            block_start = time.perf_counter()
            try:
                result = run_operational_block(
                    n=n,
                    stream_seed=seed,
                    block_index=block_index,
                    bob=bob,
                    high_true=high,
                    low_true=low,
                    u1_true=u1,
                    u2_true=u2,
                    labels_true=labels_true,
                    labels_true_bits=labels_true_bits,
                    field=field,
                    p1_table=p1,
                    p2_table=p2,
                    l1_order=l1_order,
                    l2_order=l2_order,
                    k1=k1,
                    k2=k2,
                    master=master,
                    tag_fn=_tag_fn,
                    calls=calls,
                )
                error = None
            except MemoryError:
                raise
            except Exception as exc:  # block failure: recorded, gate fails
                error = type(exc).__name__
                result = opf.OperationalBlockResult(
                    stream_seed=int(seed),
                    block_index=int(block_index),
                    outcome="decode_failed",
                    exact=False,
                    label_match=False,
                    tag_pass=False,
                    l1_provenance=None,
                    l2_provenance=None,
                    l1_executed=False,
                    l1_decode_failed=True,
                    l2_invoked=False,
                    l2_skipped_by_l1_failure=True,
                    l2_decode_failed=False,
                    tag_invoked=False,
                    key_dependent_bits=0,
                    public_control_bits=0,
                    nonfinite=False,
                    truth_leak_violation=False,
                    l1_error_type=None,
                    l2_error_type=None,
                    wall_s=time.perf_counter() - block_start,
                    k1=k1,
                    k2=k2,
                )
            if result.truth_leak_violation:
                provenance_violations += 1
            resources = opf._cell_resource_record(time.perf_counter() - block_start)
            record = opf._block_record(result, resources=resources, error=error)
            dev_records.append(record)
            opf._append_jsonl(out_path / "per_block_outcomes.jsonl", record)
            if error is None:
                for event in replication_block_events(n, seed, gidx, result):
                    dev_events.append(event)
                    incremental["key_dependent_bits"] += int(event["key_dependent_bits"])
                    incremental["public_control_bits"] += int(event["public_control_bits"])
                    if str(event["event_type"]) == "verification_tag":
                        incremental["tag_invocations"] += 1
            gidx += 1
            # Checkpoint the same five files after every DEV block.
            gates_now, failing_now = current_gates(final=False)
            checkpoint(partial_summary(f"RUNNING(dev {len(dev_records)}/128)", gates_now, failing_now))

        # ---- final gates, classification and evidence.
        wall_s = time.perf_counter() - start
        rss_peak = opf._peak_rss_bytes()
        gates, failing = current_gates(final=True)
        recovery = recovery_gates(sum(1 for r in dev_records if r.get("outcome") == "exact"))
        outcome = select_label(gates, recovery["pass"])
        summary = partial_summary(outcome, gates, failing)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        checkpoint(summary)
        return ReplicationRun(
            records=dev_records,
            events=dev_events,
            construction={
                "protocol": PROTOCOL_NAME,
                "predecessor_verified_before_first_block": True,
                "identity": dict(identity),
            },
            plan=plan,
            summary=summary,
        )
    except ReplicationResourceError:
        raise
    except TargetPopulationContractError:
        # Post-open BLOCKED: consumption already spent; best-effort BLOCKED
        # stubs (files were created before the open), then fail closed.
        try:
            blocked = {
                "protocol": PROTOCOL_NAME,
                "mode": MODE,
                "status": "BLOCKED(target_population_contract)",
                "outcome_label": "BLOCKED(target_population_contract)",
                "attempt_read_accounting": dict(accounting),
                "claim_scope": CLAIM_SCOPE,
            }
            opf._write_json(out_path / "aggregate_summary.json", blocked)
            (out_path / "report.md").write_text(
                "# NB-Polar Phase 4-P17 N=32768 operational replication of the P16 f=1.3 gate\n\n"
                "outcome label: `BLOCKED(target_population_contract)`\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        raise
    except MemoryError as exc:
        try:
            blocked = {
                "protocol": PROTOCOL_NAME,
                "mode": MODE,
                "status": "BLOCKED(resource_limits_met_and_no_abort)",
                "outcome_label": "BLOCKED(resource_limits_met_and_no_abort)",
                "reason": f"MemoryError: {exc}",
                "attempt_read_accounting": dict(accounting),
                "claim_scope": CLAIM_SCOPE,
            }
            opf._write_json(out_path / "aggregate_summary.json", blocked)
            (out_path / "report.md").write_text(
                "# NB-Polar Phase 4-P17 N=32768 operational replication of the P16 f=1.3 gate\n\n"
                "outcome label: `BLOCKED(resource_limits_met_and_no_abort)`\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        raise ReplicationResourceError(
            f"BLOCKED(resource_limits_met_and_no_abort): MemoryError: {exc}"
        ) from exc


def _integrity_gates(
    *,
    out_path: Path,
    n,
    dev_list,
    dev_bps,
    identity,
    frozen_before_dev,
    k1,
    k2,
    l1_order,
    l2_order,
    dev_records: list,
    dev_events: list,
    calls: dict,
    incremental: dict,
    accounting: dict,
    provenance_violations: int,
    start: float,
    cap: float,
    resource_stop,
    counts_shape,
    precondition_passed: bool,
    final: bool,
) -> dict:
    n = int(n)
    k1 = int(k1)
    k2 = int(k2)
    shape_frozen = bool(
        n == FROZEN_N
        and [int(s) for s in dev_list] == [int(s) for s in FROZEN_DEV_SEEDS]
        and int(dev_bps) == FROZEN_DEV_BLOCKS_PER_STREAM
    )

    identity_ok = bool(
        isinstance(identity, dict)
        and identity.get("digest_match") is True
        and identity.get("digest_recomputed") == FROZEN_CONSTRUCTION_DIGEST
        and int(identity.get("n", -1)) == FROZEN_N
        and int(identity.get("k_total", -1)) == FROZEN_K_TOTAL
        and int(identity.get("k1", -2)) == int(k1) == FROZEN_K1
        and int(identity.get("k2", -2)) == int(k2) == FROZEN_K2
    )

    coverage_ok = True
    if final:
        coverage_ok = bool(len(dev_records) == FROZEN_DEV_TOTAL and shape_frozen)
    streams_ok = bool(
        [int(s) for s in dev_list] == [int(s) for s in FROZEN_DEV_SEEDS]
        and len(set(int(s) for s in dev_list)) == len(dev_list)
        and set(int(s) for s in dev_list).isdisjoint(int(s) for s in P16_PRIOR_STREAMS)
    )

    # Valid orders: the verified P16 orders are permutations; K flags replay
    # the frozen allocation with f <= 1.3 from the ratified literals.
    h_total = float(opf.EXPECTED_H1 + opf.EXPECTED_H2)
    orders_ok = bool(
        opf._order_is_permutation(l1_order, n)
        and opf._order_is_permutation(l2_order, n)
    )
    leakage = DISCLOSED_BITS_PER_COORDINATE * (k1 + k2) + TAG_BITS
    replay_ok = bool(
        int(k1) == FROZEN_K1
        and int(k2) == FROZEN_K2
        and int(k1) + int(k2) == FROZEN_K_TOTAL
        and int(leakage) == FROZEN_LEAKAGE_BITS
        and leakage <= FROZEN_TARGET_F * int(n) * h_total
    )

    buckets_ok = True
    for record in dev_records:
        if record.get("outcome") not in OUTCOMES:
            buckets_ok = False
            break
        if record.get("error") is not None:
            buckets_ok = False
            break
        if not opf._record_dict_consistent(record, n=n, k1=k1, k2=k2):
            buckets_ok = False
            break
    if final and len(dev_records) != FROZEN_DEV_TOTAL:
        buckets_ok = False

    truth_ok = bool(
        int(provenance_violations) == 0
        and all(not record.get("truth_leak_violation", True) for record in dev_records)
    )
    undetected_ok = bool(all(record.get("outcome") != "undetected" for record in dev_records))
    nonfinite_ok = bool(
        all(record.get("outcome") != "nonfinite" for record in dev_records)
        and all(not record.get("nonfinite", True) for record in dev_records)
    )

    expected_sc = sum(
        (1 + int(record.get("l2_invoked", 0)))
        for record in dev_records
        if record.get("error") is None and record.get("outcome") != "resource_abort"
    )
    error_free = all(record.get("error") is None for record in dev_records)
    calls_ok = bool(
        set(calls) == {"sc"}
        and error_free
        and int(calls.get("sc", -1)) == int(expected_sc)
    )

    try:
        recount = replication_recount_events(dev_events)
        mismatches = opf._transcript_mismatches(incremental, recount)
        recount_ok = not mismatches
    except ValueError:
        recount_ok = False
    disclosure_ok = bool(recount_ok)
    if disclosure_ok:
        for record in dev_records:
            if record.get("error") is not None or record.get("outcome") == "resource_abort":
                continue
            expected_kdb = (
                DISCLOSED_BITS_PER_COORDINATE * k1
                + (DISCLOSED_BITS_PER_COORDINATE * k2 if record.get("l2_invoked") else 0)
                + (TAG_BITS if record.get("tag_invoked") else 0)
            )
            expected_public = seed_bits_for(n) if record.get("tag_invoked") else 0
            if (
                int(record.get("key_dependent_bits", -1)) != expected_kdb
                or int(record.get("public_control_bits", -1)) != expected_public
            ):
                disclosure_ok = False
                break

    files_ok = True
    try:
        for name in OUTPUT_FILES:
            if not out_path.joinpath(name).is_file():
                files_ok = False
                break
        if files_ok:
            with open(out_path / "per_block_outcomes.jsonl", "r", encoding="utf-8") as handle:
                if sum(1 for _ in handle) != len(dev_records):
                    files_ok = False
    except OSError:
        files_ok = False

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
    wall_now = time.perf_counter() - start
    rss_now = opf._peak_rss_bytes()
    aborts = sum(1 for record in dev_records if record.get("outcome") == "resource_abort")
    resource_ok = bool(
        resource_stop is None
        and aborts == 0
        and float(wall_now) <= float(cap)
        and (rss_now is None or int(rss_now) <= RSS_LIMIT_BYTES)
    )
    _files_ok = files_ok
    return {
        "predecessor_construction_identity": bool(identity_ok),
        "target_population_contract": bool(precondition_passed),
        "construction_frozen_before_dev": bool(frozen_before_dev and identity_ok),
        "dev_coverage_complete": bool(coverage_ok and shape_frozen) if final else bool(shape_frozen),
        "streams_disjoint_frozen": bool(streams_ok),
        "orders_valid_k_replay_f_within_budget": bool(orders_ok and replay_ok and identity_ok),
        "buckets_disjoint_exhaustive": bool(buckets_ok),
        "truth_isolation": bool(truth_ok),
        "undetected_zero": bool(undetected_ok),
        "nonfinite_zero": bool(nonfinite_ok),
        "no_unregistered_calls": bool(calls_ok),
        "disclosure_recount_exact": bool(disclosure_ok and _files_ok),
        "attempt_read_accounting_exact": bool(accounting_exact and _files_ok),
        "resource_limits_met_and_no_abort": bool(resource_ok),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p17-operational-replication",
        description=(
            "NB-Polar Phase 4-P17 N=32768 operational replication of the P16 "
            "f=1.3 gate (frozen V25 1M counts, verified P16 construction)"
        ),
    )
    parser.add_argument("--counts", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--floor", required=True, type=float)
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--k1", required=True, type=int)
    parser.add_argument("--k2", required=True, type=int)
    parser.add_argument("--construction", required=True)
    parser.add_argument("--construction-digest", required=True, dest="construction_digest")
    parser.add_argument("--dev-seeds", required=True, type=int, nargs="+", dest="dev_seeds")
    parser.add_argument("--dev-blocks-per-stream", required=True, type=int,
                        dest="dev_blocks_per_stream")
    parser.add_argument("--chunk-rows", required=True, type=int, dest="chunk_rows")
    parser.add_argument("--tag-bits", required=True, type=int, dest="tag_bits")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_operational_replication(
            counts_path=args.counts,
            source=args.source,
            floor=args.floor,
            n=args.n,
            k1=args.k1,
            k2=args.k2,
            construction=args.construction,
            construction_digest=args.construction_digest,
            dev_seeds=args.dev_seeds,
            dev_blocks_per_stream=args.dev_blocks_per_stream,
            chunk_rows=args.chunk_rows,
            tag_bits=args.tag_bits,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p17 operational replication refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "dev_block_count": summary["dev_block_count"],
                "exact_count": summary["exact_count"],
                "wilson_lower_bound": summary["recovery"]["wilson_lower_bound"],
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
