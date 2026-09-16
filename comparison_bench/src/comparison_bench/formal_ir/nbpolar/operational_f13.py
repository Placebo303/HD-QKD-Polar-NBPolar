"""NB-Polar Phase 4-P16 N=32768 empirical-construction operational f=1.3 gate.

Frozen point (packet ``NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13``,
OpenSpec ``formal-ir-nbpolar-phase4-p0`` P16 delta): measure actual
two-layer hard-candidate SC recovery at the accepted target model,
N=32768 and planning ``f <= 1.3``.  P15's genie UCB is conservative and
is not an operational outcome; this gate uses empirical construction, a
fresh operational DEV set and 64-bit verification.  There is no second
decision arm and no retry arm of any kind.

Frozen semantics:

- Input: one call to the accepted ``load_v25_channel_counts(path)``; a
  stat-only size check of exactly ``25,166,822`` bytes happens before the
  content open, and the single artifact read plus the single scientific
  attempt are consumed together at the first NPZ content open (never
  reopened, never retried; a module-level reopen guard refuses a second
  NPZ-mode call).  Refusals (absent root, CLI parse, chunk contract,
  tag-bits contract, N contract, seed grouping) happen before the content
  open; any post-open failure is ``BLOCKED(<earliest gate>)`` with
  consumption already spent.
- Support rule (the only one, exactly P7): column-normalize the raw
  counts, replace every cell below ``1e-15`` by ``1e-15``, renormalize
  each Bob column; ``p_b`` from the column totals; accepted
  ``derive_p1`` / ``derive_p2`` under the packing ``A = 32*U1 + U2``.
- Preconditions before any genie/SC call: no zero Bob column; ``p_b``
  and conditional column error ``<= 1e-12``; raw-MLE in-sample
  population ``H1``/``H2``/total within ``1e-12`` of the V49 1M TRAIN
  literals; the floor-induced total-entropy change relative to the raw
  MLE table ``<= 1e-9``.  Failure is
  ``BLOCKED(target_population_contract)`` with zero genie/SC calls
  (consumption already spent: the refusal happens after the content
  open, so it is recorded in the stderr message and the freeze doc, and
  best-effort in the pre-created stub files, never as a fresh root).
- Matrix: N=32768, GF32 (primitive polynomial 37, alpha 2, natural
  order), chunk_rows=512, target f=1.3, tag-bits 64.  TRAIN four streams
  x 4 blocks (16); DEV eight disjoint streams x 8 blocks (64).  Each
  stream restarts its RNG.  Per block: ``B ~ p_b`` then
  ``A ~ P_floor(A|B)`` sampled once.
- TRAIN uses P13 true-prefix genie risks for L1 and true-high-conditioned
  L2 rows (construction only, exactly the accepted P13 path).  Pool TRAIN
  risks per layer (means); persist only the pooled coordinate risks, never
  per-block metric/risk planes.  Order each layer worst-first by the
  accepted ``(e, h, index)`` semantics.  ``K_total`` is the frozen
  f-budget ``floor((1.3*N*(H1+H2)-64)/5)`` clipped to ``[0, 2N]`` (6811
  at N=32768) with the entire budget used; every feasible integer
  ``(K1, K2)`` with ``K1+K2=K_total`` is enumerated and the lexicographic
  minimum of ``(TRAIN residual e sum, K1, K2)`` is selected.  Orders,
  allocation and TRAIN residual are frozen before the first DEV block.
- DEV (operational, single arm): per block sample once, then (1) disclose
  true U1 at empirical ``order1[:K1]`` and run operational L1 SC; (2)
  build L2 metrics only from Bob and the hard L1 candidate (causal wiring:
  the true high layer never enters this metric); (3) disclose true U2 at
  empirical ``order2[:K2]`` and restart operational L2 SC; (4) form
  ``label_hat = 32*high_hat + low_hat`` and invoke one 64-bit Toeplitz tag
  (public master ``DEV stream seed + 10000``, domain-separated by
  P16/N/block; raw seed bits never persisted); (5) classify exactly one of
  ``exact`` / ``undetected`` / ``verify_failed`` / ``decode_failed`` /
  ``nonfinite`` / ``resource_abort`` with undetected never success.
  Alice truth enters only sampling, disclosed values, tag construction and
  scoring.  No second arm, no advancement and no repeated decode of any
  block.
- Accounting: a fully invoked block discloses exactly
  ``5*(K1+K2)+64`` key-dependent bits with
  ``(5*K_total+64)/(N*H_total) <= 1.3`` asserted at allocation; public
  Toeplitz control is ``10*N+63 = 327743`` bits per invoked tag; partial
  failure counts only actually disclosed bits.  An independent literal
  transcript recount must equal the incremental totals with zero mismatch.
- Decision: ``TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE`` iff all
  integrity gates pass and exact ``>= 62/64`` with one-sided 95% Wilson
  exact-recovery lower bound ``>= 0.90`` (62/64 has LB 0.9098711859;
  61/64 has 0.8883797144); ``..._NOT_CONFIRMED`` iff integrity passes but
  either recovery gate fails; otherwise ``BLOCKED(<earliest>)``.
- Outputs: exactly five scalar-only files (public orders plus scalar
  block outcomes; never counts, sampled symbols, truth vectors, decoded
  labels/keys, metric planes or raw tag seeds), created as stubs before
  the content open and checkpointed after the construction freeze and
  after every completed TRAIN/DEV block.  Per record: wall, RSS HWM,
  Linux ``VmPeak`` and ``VmSize``.  On MemoryError/resource failure the
  checkpoints are preserved, a BLOCKED summary is finalized if possible,
  and the run is never rerun.

No Model-F/held-out/raw/real frame, no other N in the frozen run, no
second arm, no repeated decode, no transform/belief/list decoder, no
FER/efficiency/key-rate qualification or promotion, no commit.  The claim scope is an operational
development signal for the frozen V25 TRAIN target population only, sampled
from the model, not real-data qualification.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
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
from .empirical_channel import sample_full_block
from .empirical_genie_scaling import block_genie_risks, select_empirical_split
from .prior import (
    Provenance,
    build_p1_metrics,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from .protocol import WILSON_Z, wilson_lower_bound
from .sc import ImpossibleDisclosedValueError, NumericNonfiniteError, sc_decode
from .target_construction import (
    PRECONDITION_ORDER,
    TargetPopulationContractError,
    target_preconditions,
)
from .target_n_scaling import budget_k_total
from .transform import polar_transform
from .two_layer import (
    DISCLOSED_BITS_PER_COORDINATE,
    LABEL_SCALE,
    TAG_BITS,
    labels_to_bits,
    seed_bits_for,
)

try:  # POSIX (the frozen command runs under WSL); Windows native has no resource module.
    import resource
except ImportError:  # pragma: no cover - exercised only on Windows native
    resource = None

PROTOCOL_NAME = "nbpolar-p16-operational-f13-gate"
MODE = "empirical-construction-operational-f13-gate"

Q = 32
ALPHA = 2
FROZEN_N = 32768
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
FROZEN_TRAIN_SEEDS = (2026092000, 2026092001, 2026092002, 2026092003)
FROZEN_DEV_SEEDS = (
    2026092010, 2026092011, 2026092012, 2026092013,
    2026092014, 2026092015, 2026092016, 2026092017,
)
FROZEN_TRAIN_BLOCKS_PER_STREAM = 4
FROZEN_DEV_BLOCKS_PER_STREAM = 8
FROZEN_TRAIN_TOTAL = 16
FROZEN_DEV_TOTAL = 64
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = TAG_BITS  # 64
PUBLIC_TAG_MASTER_OFFSET = 10000
# 16 TRAIN blocks x 2 genie layers; DEV SC attempts are at most 2 per block.
PLANNED_GENIE_CALLS = 2 * FROZEN_TRAIN_TOTAL
PLANNED_SC_CALLS_MAX = 2 * FROZEN_DEV_TOTAL

EXPECTED_NPZ_BYTES = 25166822
FROZEN_COUNTS_PATH = (
    "/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/"
    "nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/"
    "operational_f13_gate"
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

# Frozen recovery gates: exact >= 62/64 and one-sided 95% Wilson LB >= 0.90.
EXACT_MIN = 62
WILSON_MIN = 0.90
# Frozen boundary values (rounded to 10 decimals; the runner asserts the
# accepted wilson helper still reproduces them before the first DEV block).
WILSON_LB_62_OF_64 = 0.9098711859
WILSON_LB_61_OF_64 = 0.8883797144
WILSON_BOUNDARY_TOL = 1e-9

PUBLIC_CONTROL_BITS_PER_TAG = seed_bits_for(FROZEN_N)  # 327743

CANDIDATE_LABEL = "TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE"
NOT_CONFIRMED_LABEL = "TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_NOT_CONFIRMED"

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 2100.0
EXTERNAL_TIMEOUT_S = 2100
ULIMIT_VIRTUAL_KIB = 2097152

ARM = "operational"
OUTCOMES = ("exact", "undetected", "verify_failed", "decode_failed", "nonfinite", "resource_abort")
SEED_PREFIX = "nbpolar-p16-operational-f13-seed"

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
    "candidate label; TRAIN L2 genie rows are true-high-conditioned "
    "construction inputs only; each DEV layer restarts SC with no state "
    "transfer; each DEV L2 metric is gathered from Bob and the hard L1 "
    "candidate only"
)
CONSTRUCTION_RULE = (
    "per TRAIN block accumulate h_i=-log2 p_i[U_i], e_i=1-max p_i from the "
    "P13 genie rows; pool means per layer; worst-first orders by accepted "
    "(e,h,index); K_total=floor((1.3*N*(H1+H2)-64)/5) clipped to [0,2N] "
    "(6811 at N=32768); all feasible (K1,K2) enumerated, lexicographic "
    "minimum of (TRAIN residual e sum, K1, K2); frozen before the first DEV "
    "block; DEV never changes it"
)
OPERATIONAL_RULE = (
    "per DEV block: disclose true U1 at order1[:K1], operational L1 SC; "
    "L2 metrics from Bob plus the hard L1 candidate only; disclose true U2 "
    "at order2[:K2], restarted operational L2 SC; label_hat=32*high_hat+"
    "low_hat; exactly one 64-bit Toeplitz tag (master DEV seed+10000, "
    "P16/N/block domain); exactly one of exact/undetected/verify_failed/"
    "decode_failed/nonfinite/resource_abort; undetected never success"
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
    "target_population_contract",
    "construction_frozen_before_dev",
    "train_dev_coverage_complete",
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
    "construction_and_allocation.json",
    "per_block_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
    "ulimit -v 2097152\n"
    "timeout 2100 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.operational_f13 "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --floor 1e-15 --target-f 1.3 "
    "--n 32768 --train-seeds 2026092000 2026092001 2026092002 2026092003 "
    "--train-blocks-per-stream 4 "
    "--dev-seeds 2026092010 2026092011 2026092012 2026092013 "
    "2026092014 2026092015 2026092016 2026092017 --dev-blocks-per-stream 8 "
    "--chunk-rows 512 --tag-bits 64 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)
CLAIM_SCOPE = (
    "frozen V25 TRAIN target-population empirical-construction operational "
    "development signal at N=32768 only, sampled from the model; not "
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
    "FROZEN_TRAIN_SEEDS",
    "FROZEN_DEV_SEEDS",
    "FROZEN_TRAIN_BLOCKS_PER_STREAM",
    "FROZEN_DEV_BLOCKS_PER_STREAM",
    "FROZEN_TRAIN_TOTAL",
    "FROZEN_DEV_TOTAL",
    "FROZEN_CHUNK_ROWS",
    "FROZEN_TAG_BITS",
    "PUBLIC_TAG_MASTER_OFFSET",
    "PLANNED_GENIE_CALLS",
    "PLANNED_SC_CALLS_MAX",
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
    "EXACT_MIN",
    "WILSON_MIN",
    "WILSON_LB_62_OF_64",
    "WILSON_LB_61_OF_64",
    "WILSON_BOUNDARY_TOL",
    "PUBLIC_CONTROL_BITS_PER_TAG",
    "CANDIDATE_LABEL",
    "NOT_CONFIRMED_LABEL",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S",
    "ULIMIT_VIRTUAL_KIB",
    "ARM",
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
    "OperationalF13ResourceError",
    "OperationalBlockResult",
    "OperationalF13Run",
    "classify_operational_outcome",
    "operational_seed_bits",
    "check_wilson_boundary",
    "recovery_gates",
    "select_label",
    "run_operational_block",
    "block_events",
    "recount_events",
    "run_operational_f13",
    "build_parser",
    "main",
]


class OperationalF13ResourceError(RuntimeError):
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


def _check_target_f(value) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"target_f must be a real number, got {value!r}")
    out = float(value)
    if not np.isfinite(out) or out <= 0.0:
        raise ValueError(f"target_f must be finite and positive, got {value!r}")
    return out


def _check_n(value) -> int:
    out = _as_int(value, "n", minimum=1)
    if out & (out - 1):
        raise ValueError(f"n must be a positive power of two, got {out}")
    if out != FROZEN_N:
        raise ValueError(f"frozen point requires n={FROZEN_N}, got {out}")
    return out


def _check_tag_bits(value) -> int:
    out = _as_int(value, "tag_bits", minimum=1)
    if out != FROZEN_TAG_BITS:
        raise ValueError(f"frozen point requires tag-bits={FROZEN_TAG_BITS}, got {out}")
    return out


def _check_tag_fn(tag_fn):
    """The frozen run uses the accepted shared Toeplitz tag; tests may override."""
    if tag_fn is None:
        return toeplitz_tag
    if not callable(tag_fn):
        raise TypeError("tag_fn must be callable")
    return tag_fn


def _check_chunk_contract(chunk_rows: int) -> int:
    """Refuse anything but the frozen chunk budget before any artifact access."""
    out = _as_int(chunk_rows, "chunk_rows", minimum=1)
    import comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc as sc_mod

    params = inspect.signature(sc_mod._minus_block).parameters
    if params.get("chunk_rows", None) is None or params["chunk_rows"].default != 512:
        raise ValueError("frozen contract: _minus_block chunk_rows default must be exactly 512")
    if params["chunk_rows"].kind is not inspect.Parameter.KEYWORD_ONLY:
        raise ValueError("frozen contract: chunk_rows must be keyword-only")
    if any("chunk" in name for name in inspect.signature(sc_mod.sc_decode).parameters):
        raise ValueError("frozen contract: sc_decode must expose no chunk argument")
    if out != FROZEN_CHUNK_ROWS:
        raise ValueError(
            f"frozen point requires chunk-rows={FROZEN_CHUNK_ROWS}, got {out}"
        )
    return out


def _peak_rss_bytes() -> int | None:
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _linux_vm_kb() -> tuple:
    """Current Linux ``(VmPeak_kB, VmSize_kB)`` from ``/proc/self/status``.

    Returns ``(None, None)`` off Linux or when the fields are absent; the
    frozen gate runs under WSL where ``/proc`` is present.
    """
    peak = size = None
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("VmPeak:"):
                    peak = int(line.split()[1])
                elif line.startswith("VmSize:"):
                    size = int(line.split()[1])
    except (OSError, ValueError, IndexError):
        return (None, None)
    return (peak, size)


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


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, record: dict) -> None:
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def classify_operational_outcome(
    *,
    l1_failed: bool,
    l2_failed: bool,
    nonfinite: bool,
    tag_pass: bool,
    label_match: bool,
) -> str:
    """Frozen six-bucket outcome precedence (disjoint and exhaustive).

    ``nonfinite`` outranks ``decode_failed``: a numeric nonfinite SC failure
    is its own bucket, never merged into a generic decode failure.
    ``undetected`` (tag pass without label match) is never success.
    """
    if bool(l1_failed) or bool(l2_failed):
        return "nonfinite" if nonfinite else "decode_failed"
    if not tag_pass:
        return "verify_failed"
    return "exact" if label_match else "undetected"


def operational_seed_bits(
    master: int,
    n: int,
    block_index: int,
    *,
    bit_length: int | None = None,
) -> np.ndarray:
    """Deterministic public per-block Toeplitz seed (P16 domain).

    Rule: concatenate SHA-256 over
    ``"nbpolar-p16-operational-f13-seed:<master>:<n>:<block_index>:
    <counter>"`` for ``counter = 0, 1, ...`` (ASCII decimal), unpack each
    digest MSB-first, and truncate to ``bit_length`` (default
    ``10*n + 63``).  Seed contents are public control and are never
    persisted; only the bit length is recorded.
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


def check_wilson_boundary() -> dict:
    """Assert the accepted Wilson helper still reproduces the frozen boundary.

    Fail-closed code-level pin: 62/64 must round to 0.9098711859 (pass) and
    61/64 must round to 0.8883797144 (fail).  Any drift raises ValueError.
    """
    lb62 = float(wilson_lower_bound(EXACT_MIN, FROZEN_DEV_TOTAL, z=WILSON_Z))
    lb61 = float(wilson_lower_bound(EXACT_MIN - 1, FROZEN_DEV_TOTAL, z=WILSON_Z))
    if abs(lb62 - WILSON_LB_62_OF_64) > WILSON_BOUNDARY_TOL:
        raise ValueError(
            f"Wilson boundary drift: 62/64 LB {lb62!r} != frozen {WILSON_LB_62_OF_64!r}"
        )
    if abs(lb61 - WILSON_LB_61_OF_64) > WILSON_BOUNDARY_TOL:
        raise ValueError(
            f"Wilson boundary drift: 61/64 LB {lb61!r} != frozen {WILSON_LB_61_OF_64!r}"
        )
    return {"lb_62_of_64": lb62, "lb_61_of_64": lb61}


def recovery_gates(exact_count: int, total: int = FROZEN_DEV_TOTAL) -> dict:
    """Frozen scientific gates over the 64 DEV outcomes (pure, no I/O)."""
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
        "exact_at_least_62_of_64": exact_ok,
        "wilson_lower_bound_at_least_0p90": wilson_ok,
        "boundary_62_of_64": float(WILSON_LB_62_OF_64),
        "boundary_61_of_64": float(WILSON_LB_61_OF_64),
        "pass": bool(exact_ok and wilson_ok),
    }


def select_label(gates: dict, recovery_pass: bool) -> str:
    """Frozen label selection: candidate / not-confirmed / earliest BLOCKED."""
    failing = [name for name in INTEGRITY_GATE_ORDER if not gates.get(name, False)]
    if not failing:
        return CANDIDATE_LABEL if recovery_pass else NOT_CONFIRMED_LABEL
    return f"BLOCKED({failing[0]})"


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
class OperationalBlockResult:
    """One attempted operational DEV block.  Arrays are in-memory only."""

    stream_seed: int
    block_index: int
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


def _abort_block(stream_seed: int, block_index: int, *, k1: int, k2: int) -> OperationalBlockResult:
    return OperationalBlockResult(
        stream_seed=int(stream_seed),
        block_index=int(block_index),
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


def run_operational_block(
    *,
    n: int,
    stream_seed: int,
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
    k1: int,
    k2: int,
    master: int,
    tag_fn=None,
    calls=None,
    l1_candidate_override=None,
) -> OperationalBlockResult:
    """One causal two-layer operational block on a single sampled block.

    The operational path receives only Bob, the hard L1 candidate and the
    frozen disclosures; truth is used only for the disclosed ``U`` values,
    the tag construction and scoring.  Every SC call runs through the
    accepted chunked ``sc_decode`` (production default ``chunk_rows=512``).
    ``tag_fn`` and ``l1_candidate_override`` are documented test/assessment
    seams; the frozen gate never passes them.
    """
    n = _as_int(n, "n", minimum=1)
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    stream_seed = _as_int(stream_seed, "stream_seed", minimum=0)
    block_index = _as_int(block_index, "block_index", minimum=0)
    k1 = _as_int(k1, "k1", minimum=0)
    k2 = _as_int(k2, "k2", minimum=0)
    if k1 > n or k2 > n:
        raise ValueError(f"k1/k2 must lie in 0..{n}, got k1={k1}, k2={k2}")
    master = _as_int(master, "master", minimum=0)
    tag_fn = _check_tag_fn(tag_fn)
    # Internal truth copies: every computation below uses these copies only, so
    # the truth sentinel can mutate them and prove no aliasing.
    bob_arr = np.array(bob, dtype=np.int64, copy=True)
    high_arr = np.array(high_true, dtype=np.int64, copy=True)
    low_arr = np.array(low_true, dtype=np.int64, copy=True)
    u1_arr = np.array(u1_true, dtype=np.int64, copy=True)
    u2_arr = np.array(u2_true, dtype=np.int64, copy=True)
    labels_arr = np.array(labels_true, dtype=np.int64, copy=True)
    label_bits_arr = np.array(labels_true_bits, dtype=np.uint8, copy=True)
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
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + 1
        sc1 = _decode_layer(
            op_p1_metric.logp, field=field, positions=l1_positions, disclosed=u1_disclosed
        )
        high_hat = np.array(sc1.x_hat, copy=True)
    except Exception as exc:  # SC failure contract: decode_failed/nonfinite, no tag
        l1_failed = True
        l1_error = type(exc).__name__
        nonfinite = _nonfinite_flag(exc)
    else:
        if l1_candidate_override is not None:
            override = np.asarray(l1_candidate_override, dtype=np.int64)
            if override.shape != (n,):
                raise ValueError(f"l1_candidate_override must have shape ({n},)")
            high_hat = np.array(override, copy=True)

    if l1_failed and l1_candidate_override is not None:
        raise ValueError("l1_candidate_override requires a successful L1 decode")

    if high_hat is not None:
        # Candidate-conditioned L2: the metric is gathered from Bob and the hard
        # L1 candidate only; the true high layer never enters this metric.
        p2_probs = gather_p2_metrics(bob_arr[None, :], high_hat[None, :], p2_table)[0]
        p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
        u2_disclosed = np.array(u2_arr[l2_positions], copy=True)
        seed = operational_seed_bits(master, n, block_index, bit_length=seed_bits_for(n))
        try:
            if calls is not None:
                calls["sc"] = int(calls.get("sc", 0)) + 1
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
        except Exception as exc:  # SC failure contract: decode_failed/nonfinite, no tag
            l2_error = type(exc).__name__
            nonfinite = nonfinite or _nonfinite_flag(exc)
    else:
        u2_disclosed = np.empty(0, dtype=np.int64)

    outcome = classify_operational_outcome(
        l1_failed=l1_failed,
        l2_failed=l2_error is not None,
        nonfinite=nonfinite,
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
    return OperationalBlockResult(
        stream_seed=int(stream_seed),
        block_index=int(block_index),
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


def _block_record(result: OperationalBlockResult, *, resources: dict, error=None) -> dict:
    """Compact scalar-only record; symbol/label arrays are never persisted."""
    return {
        "stream_seed": int(result.stream_seed),
        "block_index": int(result.block_index),
        "outcome": result.outcome,
        "exact": bool(result.exact),
        "label_match": bool(result.label_match),
        "tag_pass": bool(result.tag_pass),
        "l1_provenance": result.l1_provenance,
        "l2_provenance": result.l2_provenance,
        "l1_executed": bool(result.l1_executed),
        "l1_decode_failed": bool(result.l1_decode_failed),
        "l2_invoked": bool(result.l2_invoked),
        "l2_skipped_by_l1_failure": bool(result.l2_skipped_by_l1_failure),
        "l2_decode_failed": bool(result.l2_decode_failed),
        "tag_invoked": bool(result.tag_invoked),
        "key_dependent_bits": int(result.key_dependent_bits),
        "public_control_bits": int(result.public_control_bits),
        "nonfinite": bool(result.nonfinite),
        "truth_leak_violation": bool(result.truth_leak_violation),
        "l1_error_type": result.l1_error_type,
        "l2_error_type": result.l2_error_type,
        "error": error,
        "k1": int(result.k1),
        "k2": int(result.k2),
        "wall_s": round(float(result.wall_s), 6),
        "resources": dict(resources),
    }


def _record_dict_consistent(record: dict, *, n: int, k1: int, k2: int) -> bool:
    """Structural proof of one persisted DEV record under the frozen rules."""
    if record.get("outcome") not in OUTCOMES:
        return False
    if record.get("error") is not None:
        return False
    if int(record.get("k1", -1)) != int(k1) or int(record.get("k2", -1)) != int(k2):
        return False
    if record["outcome"] == "resource_abort":
        return (
            int(record["key_dependent_bits"]) == 0
            and int(record["public_control_bits"]) == 0
            and not any(
                (
                    record["exact"],
                    record["label_match"],
                    record["tag_pass"],
                    record["l1_executed"],
                    record["l1_decode_failed"],
                    record["l2_invoked"],
                    record["l2_skipped_by_l1_failure"],
                    record["l2_decode_failed"],
                    record["tag_invoked"],
                    record["nonfinite"],
                    record["truth_leak_violation"],
                )
            )
            and record["l1_provenance"] is None
            and record["l2_provenance"] is None
        )
    if bool(record["l1_executed"]) == bool(record["l1_decode_failed"]):
        return False
    if record["l1_decode_failed"] and record["l2_invoked"]:
        return False
    if not record["l1_decode_failed"] and not record["l2_invoked"]:
        return False  # every L1 candidate must invoke L2
    if bool(record["l2_skipped_by_l1_failure"]) != bool(record["l1_decode_failed"]):
        return False
    if record["l2_decode_failed"] and not record["l2_invoked"]:
        return False
    tag_outcomes = ("exact", "undetected", "verify_failed")
    if bool(record["tag_invoked"]) != (record["outcome"] in tag_outcomes):
        return False
    if record["outcome"] == "nonfinite" and not (
        (record["l1_decode_failed"] or record["l2_decode_failed"]) and record["nonfinite"]
    ):
        return False
    if record["outcome"] == "decode_failed" and not (
        (record["l1_decode_failed"] or record["l2_decode_failed"]) and not record["nonfinite"]
    ):
        return False
    if record["outcome"] != "decode_failed" and record["outcome"] != "nonfinite" and (
        record["l1_decode_failed"] or record["l2_decode_failed"]
    ):
        return False
    if record["outcome"] == "exact" and not (record["tag_pass"] and record["label_match"]):
        return False
    if record["outcome"] == "undetected" and not (record["tag_pass"] and not record["label_match"]):
        return False
    if record["outcome"] == "verify_failed" and record["tag_pass"]:
        return False
    if bool(record["exact"]) != (record["outcome"] == "exact"):
        return False  # undetected is never success
    expected_kdb = (
        DISCLOSED_BITS_PER_COORDINATE * int(k1)
        + (DISCLOSED_BITS_PER_COORDINATE * int(k2) if record["l2_invoked"] else 0)
        + (TAG_BITS if record["tag_invoked"] else 0)
    )
    if int(record["key_dependent_bits"]) != expected_kdb:
        return False
    if int(record["public_control_bits"]) != (seed_bits_for(n) if record["tag_invoked"] else 0):
        return False
    if record["l1_executed"] and record["l1_provenance"] != Provenance.PRIOR_ONLY.value:
        return False
    if record["l2_invoked"] and record["l2_provenance"] != Provenance.CANDIDATE_CONDITIONED.value:
        return False
    return True


def _event(
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
        "frame_key": f"nbpolar-p16-operational-f13:{int(n)}:{int(stream_seed)}:{int(block_gidx)}",
        "method": "nbpolar_operational_f13",
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


def block_events(n: int, stream_seed: int, block_gidx: int, result: OperationalBlockResult) -> list:
    """Canonical public transcript events: L1, L2 (when invoked), final tag."""
    if result.outcome == "resource_abort":
        return []
    k1, k2 = int(result.k1), int(result.k2)
    events: list[dict] = []
    l1_id = f"block-{int(n)}-{int(block_gidx)}-{ARM}-l1-disclosure"
    events.append(
        _event(
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
            _event(
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
                _event(
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


def recount_events(events) -> dict:
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


def _transcript_mismatches(incremental, recount) -> list:
    fields = ("key_dependent_bits", "public_control_bits", "tag_invocations")
    mismatches = []
    for name in fields:
        if int(incremental[name]) != int(recount[name]):
            mismatches.append(f"total:{name}:{int(incremental[name])}!={int(recount[name])}")
    return mismatches


@dataclass(frozen=True, eq=False)
class OperationalF13Run:
    """In-memory P16 gate run (also returned by the runner)."""

    records: list
    events: list
    construction: dict
    plan: dict
    summary: dict


def _empty_acc(n: int) -> dict:
    return {
        "h": np.zeros(n, dtype=np.float64),
        "e": np.zeros(n, dtype=np.float64),
        "used": 0,
        "impossible": 0,
    }


def _order_is_permutation(order, n: int) -> bool:
    try:
        arr = np.asarray(order, dtype=np.int64).ravel()
    except (TypeError, ValueError):
        return False
    return bool(arr.shape == (n,) and np.array_equal(np.sort(arr), np.arange(n)))


def _stub_plan(*, out_path, source, floor, target_f, n, train_list, dev_list,
               train_bps, dev_bps, chunk_rows, tag_bits) -> dict:
    frozen_k = int(budget_k_total(int(n), EXPECTED_H1 + EXPECTED_H2, FROZEN_TARGET_F))
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
        "target_f": float(target_f),
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "train_seeds": [int(s) for s in train_list],
        "dev_seeds": [int(s) for s in dev_list],
        "train_blocks_per_stream": int(train_bps),
        "dev_blocks_per_stream": int(dev_bps),
        "train_total": int(len(train_list) * int(train_bps)),
        "dev_total": int(len(dev_list) * int(dev_bps)),
        "tag_master_rule": "DEV stream seed + 10000",
        "tag_seed_domain": f"{SEED_PREFIX}:<master>:<n>:<block_index>",
        "public_control_bits_per_tag": int(seed_bits_for(int(n))),
        "frozen_k_total_from_literals": {str(int(n)): frozen_k},
        "entropy_expectations": {
            "h1": EXPECTED_H1,
            "h2": EXPECTED_H2,
            "total": EXPECTED_TOTAL,
            "entropy_tol": ENTROPY_TOL,
            "column_tol": COLUMN_TOL,
            "floor_entropy_change_tol": FLOOR_ENTROPY_TOL,
        },
        "recovery_gates": {
            "exact_min": EXACT_MIN,
            "dev_total": FROZEN_DEV_TOTAL,
            "wilson_z": float(WILSON_Z),
            "wilson_min": float(WILSON_MIN),
            "boundary_62_of_64": float(WILSON_LB_62_OF_64),
            "boundary_61_of_64": float(WILSON_LB_61_OF_64),
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


def _cell_resource_record(wall_s: float) -> dict:
    rss = _peak_rss_bytes()
    peak_kb, size_kb = _linux_vm_kb()
    return {
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_hwm": rss,
        "vm_peak_kb": peak_kb,
        "vm_size_kb": size_kb,
    }


def _render_report(summary: dict) -> str:
    lines = [
        "# NB-Polar Phase 4-P16 N=32768 empirical-construction operational f=1.3 gate",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- source/target: `{summary['source']}`; q={summary['q']}, n={summary['n']}, "
        f"target_f={summary['target_f']}, chunk_rows={summary['chunk_rows']}, "
        f"tag_bits={summary['tag_bits']}",
        f"- TRAIN streams x blocks: {summary['train_blocks_per_stream']} each "
        f"({summary['train_total']} blocks); DEV: {summary['dev_blocks_per_stream']} each "
        f"({summary['dev_total']} blocks)",
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
        "## Construction and allocation (frozen before DEV)",
        "",
    ]
    construction = summary["construction"]
    if "k_total" not in construction:
        lines += [
            f"- status: `{construction.get('status', 'pending_freeze')}`; "
            f"TRAIN blocks done: {construction.get('train_blocks_done', 0)}",
            "",
        ]
    else:
        lines += [
            f"- K_total: {construction['k_total']} "
            f"(floor((1.3*N*H-64)/5) = floor({construction['k_total_raw']!r}) = "
            f"{construction['k_total']})",
            f"- split: K1={construction['k1']}, K2={construction['k2']}; "
            f"TRAIN residual: {construction['train_residual']!r}",
            f"- leakage bits: {construction['leakage_bits']} "
            f"(5*K_total+64); f: {construction['f']!r} (<= 1.3 required)",
            f"- freeze digest: `{construction['freeze_sha256']}`",
            "",
        ]
    lines += [
        "## DEV operational outcomes (64 blocks)",
        "",
        "| outcome | count |",
        "|---|---|",
    ]
    for name in OUTCOMES:
        lines.append(f"| {name} | {summary['outcome_counts'][name]} |")
    recovery = summary["recovery"]
    lines += [
        "",
        f"- exact fraction: {summary['exact_count']}/64 = {summary['exact_fraction']!r}",
        f"- one-sided 95% Wilson LB: {recovery['wilson_lower_bound']!r} "
        f"(>= 0.90 required; 62/64 boundary {recovery['boundary_62_of_64']!r}, "
        f"61/64 boundary {recovery['boundary_61_of_64']!r})",
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


def run_operational_f13(
    *,
    counts=None,
    counts_path=FROZEN_COUNTS_PATH,
    source: str = FROZEN_SOURCE,
    floor=FROZEN_FLOOR,
    target_f: float = FROZEN_TARGET_F,
    n: int = FROZEN_N,
    train_seeds=FROZEN_TRAIN_SEEDS,
    dev_seeds=FROZEN_DEV_SEEDS,
    train_blocks_per_stream: int = FROZEN_TRAIN_BLOCKS_PER_STREAM,
    dev_blocks_per_stream: int = FROZEN_DEV_BLOCKS_PER_STREAM,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    tag_bits: int = FROZEN_TAG_BITS,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_entropies=None,
    tag_fn=None,
) -> OperationalF13Run:
    """Execute the frozen P16 operational f=1.3 gate; write five files.

    ``counts``, ``expected_entropies`` and ``tag_fn`` are documented injected
    test seams; the frozen CLI passes only the frozen point and reads the V25
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
    target_f = _check_target_f(target_f)
    if target_f != FROZEN_TARGET_F:
        raise ValueError(f"frozen point requires target-f={FROZEN_TARGET_F}, got {target_f}")
    _check_chunk_contract(chunk_rows)
    _check_tag_bits(tag_bits)
    n = _check_n(n)
    train_list = [_as_int(s, "train seed", minimum=0) for s in train_seeds]
    dev_list = [_as_int(s, "dev seed", minimum=0) for s in dev_seeds]
    train_bps = _as_int(train_blocks_per_stream, "train-blocks-per-stream", minimum=1)
    dev_bps = _as_int(dev_blocks_per_stream, "dev-blocks-per-stream", minimum=1)
    if len(train_list) != len(FROZEN_TRAIN_SEEDS):
        raise ValueError(
            f"train-seeds must hold exactly {len(FROZEN_TRAIN_SEEDS)} streams, "
            f"got {len(train_list)}"
        )
    if len(dev_list) != len(FROZEN_DEV_SEEDS):
        raise ValueError(
            f"dev-seeds must hold exactly {len(FROZEN_DEV_SEEDS)} streams, "
            f"got {len(dev_list)}"
        )
    if int(train_bps) != FROZEN_TRAIN_BLOCKS_PER_STREAM:
        raise ValueError(
            "train-blocks-per-stream must be "
            f"{FROZEN_TRAIN_BLOCKS_PER_STREAM}, got {int(train_bps)}"
        )
    if int(dev_bps) != FROZEN_DEV_BLOCKS_PER_STREAM:
        raise ValueError(
            "dev-blocks-per-stream must be "
            f"{FROZEN_DEV_BLOCKS_PER_STREAM}, got {int(dev_bps)}"
        )
    if len(set(train_list)) != len(train_list):
        raise ValueError("train stream seeds must be distinct")
    if len(set(dev_list)) != len(dev_list):
        raise ValueError("dev stream seeds must be distinct")
    if not set(train_list).isdisjoint(dev_list):
        raise ValueError("TRAIN and DEV stream seeds must be disjoint")
    cap = float(total_wall_s)
    if not np.isfinite(cap) or cap <= 0:
        raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")
    tag_fn = _check_tag_fn(tag_fn)

    plan = _stub_plan(
        out_path=out_path, source=source, floor=floor, target_f=target_f,
        n=n, train_list=train_list, dev_list=dev_list,
        train_bps=train_bps, dev_bps=dev_bps, chunk_rows=chunk_rows,
        tag_bits=tag_bits,
    )

    # ---- create all five files BEFORE the content open (stub inventory).
    out_path.mkdir(parents=True)
    constructed: dict = {}
    try:
        _write_json(out_path / "frozen_plan.json", plan)
        _write_json(
            out_path / "construction_and_allocation.json",
            {"protocol": PROTOCOL_NAME, "status": "pending_content_open"},
        )
        (out_path / "per_block_outcomes.jsonl").write_text("", encoding="utf-8")
        _write_json(
            out_path / "aggregate_summary.json",
            {"protocol": PROTOCOL_NAME, "status": "pending_content_open"},
        )
        (out_path / "report.md").write_text(
            "# NB-Polar Phase 4-P16 N=32768 empirical-construction operational f=1.3 gate\n\n"
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
        h1, h2 = float(entropy.h1), float(entropy.h2)
        h_total = h1 + h2
        # Code-level pin: the accepted Wilson helper must still reproduce the
        # frozen 62/64 (pass) and 61/64 (fail) boundary values.
        boundary = check_wilson_boundary()
        field = make_gf32()
        start = time.perf_counter()

        calls = {"genie": 0, "sc": 0}
        train_blocks_done = 0
        dev_records: list[dict] = []
        dev_events: list[dict] = []
        incremental = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
        provenance_violations = 0
        resource_stop: str | None = None

        def checkpoint(summary_doc: dict) -> None:
            _write_json(
                out_path / "construction_and_allocation.json",
                {
                    "protocol": PROTOCOL_NAME,
                    "frozen_before_first_dev": bool(constructed),
                    "cell": dict(constructed),
                },
            )
            _write_json(out_path / "aggregate_summary.json", summary_doc)
            (out_path / "report.md").write_text(_render_report(summary_doc), encoding="utf-8")

        def partial_summary(outcome_label: str, gates: dict, failing: list) -> dict:
            outcome_counts = {name: 0 for name in OUTCOMES}
            for record in dev_records:
                if record.get("outcome") in outcome_counts:
                    outcome_counts[record["outcome"]] += 1
            exact_count = int(outcome_counts["exact"])
            recovery = recovery_gates(exact_count)
            try:
                recount = recount_events(dev_events)
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
                "target_f": float(target_f),
                "chunk_rows": int(chunk_rows),
                "tag_bits": int(tag_bits),
                "train_seeds": [int(s) for s in train_list],
                "dev_seeds": [int(s) for s in dev_list],
                "train_blocks_per_stream": int(train_bps),
                "dev_blocks_per_stream": int(dev_bps),
                "train_total": int(len(train_list) * int(train_bps)),
                "dev_total": int(len(dev_list) * int(dev_bps)),
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
                "construction": dict(constructed) if constructed else {
                    "status": "pending_freeze",
                    "train_blocks_done": int(train_blocks_done),
                },
                "outcome_counts": {name: int(outcome_counts[name]) for name in OUTCOMES},
                "exact_count": int(exact_count),
                "exact_fraction": (float(exact_count) / float(len(dev_list) * int(dev_bps))
                                    if dev_records else 0.0),
                "recovery": recovery,
                "wilson_boundary_check": dict(boundary),
                "dev_block_count": int(len(dev_records)),
                "genie_calls": int(calls["genie"]),
                "planned_genie_calls": int(PLANNED_GENIE_CALLS),
                "sc_calls": int(calls["sc"]),
                "planned_sc_calls_max": int(PLANNED_SC_CALLS_MAX),
                "provenance_violations": int(provenance_violations),
                "disclosure": {
                    "key_dependent_bits": int(incremental["key_dependent_bits"]),
                    "public_control_bits": int(incremental["public_control_bits"]),
                    "tag_invocations": int(incremental["tag_invocations"]),
                    "recount": recount,
                    "mismatches": _transcript_mismatches(incremental, recount)
                    if recount["key_dependent_bits"] is not None else ["recount_unavailable"],
                },
                "integrity": {name: bool(gates.get(name, False)) for name in INTEGRITY_GATE_ORDER},
                "integrity_all_pass": bool(all(gates.get(name, False) for name in INTEGRITY_GATE_ORDER)),
                "failing_integrity_gates": list(failing),
                "outcome_label": outcome_label,
                "wall_s": round(float(time.perf_counter() - start), 6),
                "rss_bytes_peak": _peak_rss_bytes(),
                "resource_stop_fired": bool(resource_stop is not None),
                "resource_stop_reason": resource_stop,
                "attempt_read_accounting": dict(accounting),
                "claim_scope": CLAIM_SCOPE,
            }

        def current_gates(*, final: bool) -> tuple:
            gates = _integrity_gates(
                out_path=out_path,
                n=n,
                train_list=train_list,
                dev_list=dev_list,
                train_bps=train_bps,
                dev_bps=dev_bps,
                constructed=constructed,
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

        # ---- TRAIN: pooled genie sufficient statistics per layer (exactly P13).
        acc_l1 = _empty_acc(n)
        acc_l2 = _empty_acc(n)
        for seed in train_list:
            rng = np.random.default_rng(int(seed))
            for _ in range(int(train_bps)):
                reason = _budget_exceeded(start, cap)
                if reason is not None:
                    resource_stop = reason
                    raise OperationalF13ResourceError(
                        f"BLOCKED(resource_limits_met_and_no_abort): {reason} during TRAIN"
                    )
                bob, _a_full, high, low = sample_full_block(
                    rng, entropy.p_b, entropy.f, Q, Q, n
                )
                u1 = polar_transform(high, field=field, alpha=ALPHA)
                u2 = polar_transform(low, field=field, alpha=ALPHA)
                l1_metric = probs_to_symbol_metric(
                    build_p1_metrics(bob[None, :], p1)[0],
                    provenance=Provenance.PRIOR_ONLY,
                )
                if l1_metric.provenance != Provenance.PRIOR_ONLY:
                    provenance_violations += 1
                l2_metric = probs_to_symbol_metric(
                    gather_p2_metrics(bob[None, :], high[None, :], p2)[0],
                    provenance=Provenance.ORACLE_CONDITIONED,
                )
                if l2_metric.provenance != Provenance.ORACLE_CONDITIONED:
                    provenance_violations += 1
                try:
                    risks = block_genie_risks(
                        l1_metric.logp, u1, l2_metric.logp, u2,
                        field=field, calls=calls,
                    )
                except ImpossibleDisclosedValueError:
                    acc_l1["impossible"] += 1
                    acc_l2["impossible"] += 1
                    continue
                acc_l1["h"] += risks["h1"]
                acc_l1["e"] += risks["e1"]
                acc_l1["used"] += 1
                acc_l2["h"] += risks["h2"]
                acc_l2["e"] += risks["e2"]
                acc_l2["used"] += 1
                train_blocks_done += 1
                # Checkpoint the same five files after every TRAIN block.
                gates_now, failing_now = current_gates(final=False)
                checkpoint(partial_summary(f"RUNNING(train {train_blocks_done}/16)", gates_now, failing_now))

        # ---- freeze empirical orders/allocation/TRAIN residual before DEV.
        k_total_raw = (float(target_f) * int(n) * h_total - 64.0) / 5.0
        k_total = budget_k_total(n, h_total, target_f)
        leakage = DISCLOSED_BITS_PER_COORDINATE * k_total + TAG_BITS
        budget_bits = float(target_f) * int(n) * h_total
        if not leakage <= budget_bits:
            raise TargetPopulationContractError(
                f"BLOCKED(orders_valid_k_replay_f_within_budget): leakage {leakage} "
                f"exceeds f-budget {budget_bits!r}"
            )
        used1 = max(int(acc_l1["used"]), 1)
        used2 = max(int(acc_l2["used"]), 1)
        e1_mean, h1_mean = acc_l1["e"] / used1, acc_l1["h"] / used1
        e2_mean, h2_mean = acc_l2["e"] / used2, acc_l2["h"] / used2
        split = select_empirical_split(n, e1_mean, h1_mean, e2_mean, h2_mean, k_total)
        k1, k2 = int(split["k1"]), int(split["k2"])
        freeze_sha = hashlib.sha256(
            json.dumps(
                {
                    "n": int(n),
                    "k_total": int(k_total),
                    "k1": int(k1),
                    "k2": int(k2),
                    "l1_order": [int(v) for v in split["l1_order"].tolist()],
                    "l2_order": [int(v) for v in split["l2_order"].tolist()],
                    "pooled_e1_mean": [float(v) for v in e1_mean.tolist()],
                    "pooled_h1_mean": [float(v) for v in h1_mean.tolist()],
                    "pooled_e2_mean": [float(v) for v in e2_mean.tolist()],
                    "pooled_h2_mean": [float(v) for v in h2_mean.tolist()],
                },
                sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        constructed.update({
            "n": int(n),
            "train_seeds": [int(s) for s in train_list],
            "dev_seeds": [int(s) for s in dev_list],
            "train_blocks": int(len(train_list) * int(train_bps)),
            "train_used_l1": int(acc_l1["used"]),
            "train_used_l2": int(acc_l2["used"]),
            "train_impossible": int(acc_l1["impossible"] + acc_l2["impossible"]),
            "k_total": int(k_total),
            "k_total_raw": float(k_total_raw),
            "k1": int(k1),
            "k2": int(k2),
            "train_residual": float(split["residual"]),
            "leakage_bits": int(leakage),
            "f": float(leakage / (int(n) * h_total)),
            "l1_order": [int(v) for v in split["l1_order"].tolist()],
            "l2_order": [int(v) for v in split["l2_order"].tolist()],
            "pooled_e1_mean": [float(v) for v in e1_mean.tolist()],
            "pooled_h1_mean": [float(v) for v in h1_mean.tolist()],
            "pooled_e2_mean": [float(v) for v in e2_mean.tolist()],
            "pooled_h2_mean": [float(v) for v in h2_mean.tolist()],
            "freeze_sha256": freeze_sha,
        })
        l1_order = np.asarray(constructed["l1_order"], dtype=np.int64)
        l2_order = np.asarray(constructed["l2_order"], dtype=np.int64)
        gates_now, failing_now = current_gates(final=False)
        checkpoint(partial_summary("FROZEN(construction before DEV)", gates_now, failing_now))

        # ---- DEV: one operational block per stream slot, checkpoint every block.
        gidx = 0
        stream_rngs: dict[int, np.random.Generator] = {}
        dev_positions = [(seed, block_index) for seed in dev_list for block_index in range(int(dev_bps))]
        for seed, block_index in dev_positions:
            reason = _budget_exceeded(start, cap)
            if reason is not None:
                resource_stop = reason
                for rest_seed, rest_block in dev_positions[gidx:]:
                    abort = _abort_block(rest_seed, rest_block, k1=k1, k2=k2)
                    record = _block_record(abort, resources=_cell_resource_record(0.0))
                    dev_records.append(record)
                    _append_jsonl(out_path / "per_block_outcomes.jsonl", record)
                    gates_now, failing_now = current_gates(final=False)
                    checkpoint(partial_summary(f"RUNNING(dev {len(dev_records)}/64)", gates_now, failing_now))
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
                    master=int(seed) + PUBLIC_TAG_MASTER_OFFSET,
                    tag_fn=tag_fn,
                    calls=calls,
                )
                error = None
            except MemoryError:
                raise
            except Exception as exc:  # block failure: recorded, gate fails
                error = type(exc).__name__
                # An escaped failure is not a clean decode failure: keep a
                # zero-disclosure record but mark the error so the buckets
                # gate fails closed.
                result = OperationalBlockResult(
                    stream_seed=result.stream_seed,
                    block_index=result.block_index,
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
            resources = _cell_resource_record(time.perf_counter() - block_start)
            record = _block_record(result, resources=resources, error=error)
            dev_records.append(record)
            _append_jsonl(out_path / "per_block_outcomes.jsonl", record)
            if error is None:
                for event in block_events(n, seed, gidx, result):
                    dev_events.append(event)
                    incremental["key_dependent_bits"] += int(event["key_dependent_bits"])
                    incremental["public_control_bits"] += int(event["public_control_bits"])
                    if str(event["event_type"]) == "verification_tag":
                        incremental["tag_invocations"] += 1
            gidx += 1
            # Checkpoint the same five files after every DEV block.
            gates_now, failing_now = current_gates(final=False)
            checkpoint(partial_summary(f"RUNNING(dev {len(dev_records)}/64)", gates_now, failing_now))

        # ---- final gates, classification and evidence.
        wall_s = time.perf_counter() - start
        rss_peak = _peak_rss_bytes()
        gates, failing = current_gates(final=True)
        recovery = recovery_gates(sum(1 for r in dev_records if r.get("outcome") == "exact"))
        outcome = select_label(gates, recovery["pass"])
        summary = partial_summary(outcome, gates, failing)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        checkpoint(summary)
        return OperationalF13Run(
            records=dev_records,
            events=dev_events,
            construction={
                "protocol": PROTOCOL_NAME,
                "frozen_before_first_dev": True,
                "cell": dict(constructed),
            },
            plan=plan,
            summary=summary,
        )
    except OperationalF13ResourceError:
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
            _write_json(out_path / "aggregate_summary.json", blocked)
            (out_path / "report.md").write_text(
                "# NB-Polar Phase 4-P16 N=32768 empirical-construction operational f=1.3 gate\n\n"
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
            _write_json(out_path / "aggregate_summary.json", blocked)
            (out_path / "report.md").write_text(
                "# NB-Polar Phase 4-P16 N=32768 empirical-construction operational f=1.3 gate\n\n"
                "outcome label: `BLOCKED(resource_limits_met_and_no_abort)`\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        raise OperationalF13ResourceError(
            f"BLOCKED(resource_limits_met_and_no_abort): MemoryError: {exc}"
        ) from exc


def _integrity_gates(
    *,
    out_path: Path,
    n,
    train_list,
    dev_list,
    train_bps,
    dev_bps,
    constructed: dict,
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
    shape_frozen = bool(
        n == FROZEN_N
        and [int(s) for s in train_list] == list(FROZEN_TRAIN_SEEDS)
        and [int(s) for s in dev_list] == list(FROZEN_DEV_SEEDS)
        and int(train_bps) == FROZEN_TRAIN_BLOCKS_PER_STREAM
        and int(dev_bps) == FROZEN_DEV_BLOCKS_PER_STREAM
    )
    frozen_k1 = int(constructed.get("k1", -1)) if constructed else -1
    frozen_k2 = int(constructed.get("k2", -1)) if constructed else -1

    train_complete = bool(
        constructed
        and int(constructed.get("train_used_l1", -1)) == FROZEN_TRAIN_TOTAL
        and int(constructed.get("train_used_l2", -1)) == FROZEN_TRAIN_TOTAL
        and int(constructed.get("train_impossible", 1)) == 0
    )
    coverage_ok = True
    if final:
        coverage_ok = bool(
            train_complete and len(dev_records) == FROZEN_DEV_TOTAL
        )
    streams_ok = bool(
        set(int(s) for s in train_list).isdisjoint(int(s) for s in dev_list)
        and len(set(int(s) for s in train_list)) == len(train_list)
        and len(set(int(s) for s in dev_list)) == len(dev_list)
        and [int(s) for s in train_list] == list(FROZEN_TRAIN_SEEDS)
        and [int(s) for s in dev_list] == list(FROZEN_DEV_SEEDS)
    )

    # Valid orders: frozen orders are permutations; freeze SHA recomputed
    # from the persisted construction matches; K budget/allocation replays
    # exactly from the literals and pooled risks with f <= 1.3.
    orders_ok = True
    replay_ok = True
    if constructed:
        if not (
            _order_is_permutation(constructed.get("l1_order"), n)
            and _order_is_permutation(constructed.get("l2_order"), n)
        ):
            orders_ok = False
        else:
            recomputed = hashlib.sha256(
                json.dumps(
                    {
                        "n": int(constructed["n"]),
                        "k_total": int(constructed["k_total"]),
                        "k1": int(constructed["k1"]),
                        "k2": int(constructed["k2"]),
                        "l1_order": [int(v) for v in constructed["l1_order"]],
                        "l2_order": [int(v) for v in constructed["l2_order"]],
                        "pooled_e1_mean": [float(v) for v in constructed["pooled_e1_mean"]],
                        "pooled_h1_mean": [float(v) for v in constructed["pooled_h1_mean"]],
                        "pooled_e2_mean": [float(v) for v in constructed["pooled_e2_mean"]],
                        "pooled_h2_mean": [float(v) for v in constructed["pooled_h2_mean"]],
                    },
                    sort_keys=True, separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            if recomputed != constructed.get("freeze_sha256"):
                orders_ok = False
        try:
            k_total = budget_k_total(n, EXPECTED_H1 + EXPECTED_H2, FROZEN_TARGET_F)
            replay = select_empirical_split(
                n,
                np.asarray(constructed["pooled_e1_mean"]),
                np.asarray(constructed["pooled_h1_mean"]),
                np.asarray(constructed["pooled_e2_mean"]),
                np.asarray(constructed["pooled_h2_mean"]),
                k_total,
            )
            leakage = DISCLOSED_BITS_PER_COORDINATE * k_total + TAG_BITS
            budget = float(FROZEN_TARGET_F) * int(n) * (EXPECTED_H1 + EXPECTED_H2)
        except (ValueError, TypeError):
            replay_ok = False
        else:
            replay_ok = bool(
                int(constructed["k_total"]) == int(k_total)
                and int(constructed["k1"]) == int(replay["k1"])
                and int(constructed["k2"]) == int(replay["k2"])
                and abs(float(constructed["train_residual"]) - float(replay["residual"])) <= 1e-9
                and [int(v) for v in constructed["l1_order"]] == [int(v) for v in replay["l1_order"].tolist()]
                and [int(v) for v in constructed["l2_order"]] == [int(v) for v in replay["l2_order"].tolist()]
                and int(leakage) <= budget
            )
    else:
        orders_ok = True
        replay_ok = True

    buckets_ok = True
    for record in dev_records:
        if record.get("outcome") not in OUTCOMES:
            buckets_ok = False
            break
        if record.get("error") is not None:
            buckets_ok = False
            break
        if not _record_dict_consistent(record, n=n, k1=frozen_k1, k2=frozen_k2):
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

    if constructed:
        expected_sc = sum(
            (1 + int(record.get("l2_invoked", 0)))
            for record in dev_records
            if record.get("error") is None and record.get("outcome") != "resource_abort"
        )
        error_free = all(record.get("error") is None for record in dev_records)
        if final:
            calls_ok = bool(
                int(calls.get("genie", -1)) == int(PLANNED_GENIE_CALLS)
                and error_free
                and int(calls.get("sc", -1)) == int(expected_sc)
            )
        else:
            calls_ok = bool(
                int(calls.get("genie", -1)) <= int(PLANNED_GENIE_CALLS)
                and error_free
                and int(calls.get("sc", -1)) == int(expected_sc)
            )
    else:
        calls_ok = bool(
            int(calls.get("genie", -1)) <= int(PLANNED_GENIE_CALLS)
            and int(calls.get("sc", 0)) == 0
        )

    try:
        recount = recount_events(dev_events)
        mismatches = _transcript_mismatches(incremental, recount)
        recount_ok = not mismatches
    except ValueError:
        recount_ok = False
    disclosure_ok = bool(recount_ok)
    if disclosure_ok and constructed:
        for record in dev_records:
            if record.get("error") is not None or record.get("outcome") == "resource_abort":
                continue
            expected_kdb = (
                DISCLOSED_BITS_PER_COORDINATE * frozen_k1
                + (DISCLOSED_BITS_PER_COORDINATE * frozen_k2 if record.get("l2_invoked") else 0)
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
    rss_now = _peak_rss_bytes()
    aborts = sum(1 for record in dev_records if record.get("outcome") == "resource_abort")
    resource_ok = bool(
        resource_stop is None
        and aborts == 0
        and float(wall_now) <= float(cap)
        and (rss_now is None or int(rss_now) <= RSS_LIMIT_BYTES)
    )
    return {
        "target_population_contract": bool(precondition_passed),
        "construction_frozen_before_dev": bool(constructed and train_complete),
        "train_dev_coverage_complete": bool(coverage_ok and shape_frozen) if final else bool(shape_frozen),
        "streams_disjoint_frozen": bool(streams_ok),
        "orders_valid_k_replay_f_within_budget": bool(orders_ok and replay_ok and bool(constructed)),
        "buckets_disjoint_exhaustive": bool(buckets_ok),
        "truth_isolation": bool(truth_ok),
        "undetected_zero": bool(undetected_ok),
        "nonfinite_zero": bool(nonfinite_ok),
        "no_unregistered_calls": bool(calls_ok),
        "disclosure_recount_exact": bool(disclosure_ok and files_ok),
        "attempt_read_accounting_exact": bool(accounting_exact and files_ok),
        "resource_limits_met_and_no_abort": bool(resource_ok),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p16-operational-f13",
        description=(
            "NB-Polar Phase 4-P16 N=32768 empirical-construction operational f=1.3 "
            "development gate (frozen V25 1M TRAIN counts)"
        ),
    )
    parser.add_argument("--counts", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--floor", required=True, type=float)
    parser.add_argument("--target-f", required=True, type=float, dest="target_f")
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--train-seeds", required=True, type=int, nargs="+", dest="train_seeds")
    parser.add_argument("--dev-seeds", required=True, type=int, nargs="+", dest="dev_seeds")
    parser.add_argument("--train-blocks-per-stream", required=True, type=int,
                        dest="train_blocks_per_stream")
    parser.add_argument("--dev-blocks-per-stream", required=True, type=int,
                        dest="dev_blocks_per_stream")
    parser.add_argument("--chunk-rows", required=True, type=int, dest="chunk_rows")
    parser.add_argument("--tag-bits", required=True, type=int, dest="tag_bits")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_operational_f13(
            counts_path=args.counts,
            source=args.source,
            floor=args.floor,
            target_f=args.target_f,
            n=args.n,
            train_seeds=args.train_seeds,
            dev_seeds=args.dev_seeds,
            train_blocks_per_stream=args.train_blocks_per_stream,
            dev_blocks_per_stream=args.dev_blocks_per_stream,
            chunk_rows=args.chunk_rows,
            tag_bits=args.tag_bits,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p16 operational f13 refused: {exc}", file=sys.stderr)
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
