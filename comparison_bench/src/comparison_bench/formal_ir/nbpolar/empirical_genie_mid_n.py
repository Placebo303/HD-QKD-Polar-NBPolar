"""NB-Polar Phase 4-P15 empirical-genie mid-N scaling gate.

Frozen point (packet ``NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING``,
OpenSpec ``formal-ir-nbpolar-phase4-p0`` P15 delta): extend the accepted
P13/P14 empirical-genie residual curve to N=32768 and N=65536 with
empirical construction and independent DEV only. Decide whether either
registered N reaches the planning f=1.3 genie-residual UCB target. This
is a model-sampled construction/rate development gate, not operational
FER or real-data qualification; it does not retry P12's
operational/surrogate profile.

Frozen semantics:

- Input: one call to the accepted ``load_v25_channel_counts(path)``; a
  stat-only size check of exactly ``25,166,822`` bytes happens before the
  content open, and the single artifact read plus the single scientific
  attempt are consumed at the first NPZ content open (never reopened,
  never retried; a module-level reopen guard refuses a second NPZ-mode
  call). Refusals (absent root, CLI parse, chunk contract, N-to-seed
  grouping) happen before the content open; any post-open failure is
  ``BLOCKED(<earliest gate>)`` with consumption already spent.
- Support rule (the only one, exactly P7): column-normalize the raw
  counts, replace every cell below ``1e-15`` by ``1e-15``, renormalize
  each Bob column; ``p_b`` from the column totals; accepted
  ``derive_p1`` / ``derive_p2`` under the packing ``A = 32*U1 + U2``.
- Preconditions before any genie call: no zero Bob column; ``p_b``
  and conditional column error ``<= 1e-12``; raw-MLE in-sample
  population ``H1``/``H2``/total within ``1e-12`` of the V49 1M TRAIN
  literals; the floor-induced total-entropy change relative to the raw
  MLE table ``<= 1e-9``. Failure is
  ``BLOCKED(target_population_contract)`` with zero genie calls
  (consumption already spent: the refusal happens after the content
  open, so it is recorded in the stderr message and the freeze doc, and
  best-effort in the pre-created stub files, never as a fresh root).
- Matrix: N=32768/65536. Per N: TRAIN four streams x 4 blocks (16),
  DEV four disjoint streams x 4 blocks (16). Each stream restarts its
  RNG. Per block: ``B ~ p_b`` then ``A ~ P_floor(A|B)`` sampled once;
  L1 genie conditionals with the true U1 prefix; L2 genie conditionals
  with the true U1+U2 prefix (oracle-conditioned construction only).
  No decision arm, no tag and no Toeplitz master exist in this gate.
  Every genie call runs through the accepted P13 ``block_genie_risks``
  (whose ``sc_decode`` production default is exactly
  ``chunk_rows=512``, verified by contract check; the CLI value must
  equal 512). Planned genie calls = 128 (64 blocks x 2 layers).
- Construction: per TRAIN block accumulate coordinate risks
  ``h_i = -log2 p_i[U_i]`` and ``e_i = 1 - max p_i``; pool TRAIN risks
  per layer (means); persist only the pooled coordinate risks, never
  per-block metric/risk planes. Order each layer worst-first by the
  accepted ``(e, h, index)`` semantics. ``K_total`` is the frozen
  f-budget ``floor((1.3*N*(H1+H2)-64)/5)`` clipped to ``[0, 2N]`` with
  the entire budget used (6811 at N=32768, 13636 at N=65536); every
  feasible integer ``(K1, K2)`` with ``K1+K2=K_total`` is enumerated
  and the lexicographic minimum of ``(TRAIN residual e sum, K1, K2)``
  is selected. Orders, allocation and TRAIN residual are frozen before
  that N's first DEV block; DEV never changes them.
- DEV: per block the scalar residual
  ``R = sum(e1[undisclosed empirical coords])
       + sum(e2[undisclosed empirical coords])``
  for the frozen split. DEV is never selected or tuned from. Per N:
  the 16 DEV ``R`` values, mean, sample standard deviation, range and
  one-sided 95% Student-t upper confidence bound
  ``mean + 1.753050356*std/sqrt(16)`` (df=15). The residual is a genie
  union-bound construction proxy; it is not operational FER and not
  proof of any minimum N. Order stability across the four TRAIN
  streams (per-stream order Spearman against the pooled order) and
  allocation/resources are diagnostics only.
- Decision (implemented here, adjudicated by the main thread):
  ``TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_CANDIDATE`` if at least
  one registered N has the frozen one-sided DEV residual UCB
  ``<= 0.01`` (smallest such N recorded);
  ``..._NOT_CONFIRMED`` if integrity passes but no registered N meets
  it; otherwise ``BLOCKED(<earliest>)``.
- Outputs: exactly five scalar-only files (public orders plus scalar
  block statistics; never counts, sampled symbols, truth vectors,
  decoder outputs, metric planes or RNG state), created as stubs
  before the content open and checkpointed after every completed
  block/N. Per cell and per block record: wall, RSS HWM, Linux
  ``VmPeak`` and ``VmSize``. On MemoryError/resource failure the
  checkpoints are preserved, a BLOCKED summary is finalized if
  possible, and the run is never rerun.

No Model-F/held-out/raw/real frame, no other N in the frozen run, no
FWHT/APP/SCL, no operational decode, no FER/efficiency/key-rate
qualification or promotion, no commit. The claim scope is a
construction/rate development signal for the frozen V25 TRAIN target
population only.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import sys
import time
from dataclasses import dataclass
from numbers import Integral, Real
from pathlib import Path

import numpy as np

from ..v35_algorithm_development import load_v25_channel_counts
from .algebra import make_gf32
from .construction import disclosure_order_from_stats, spearman_rank_corr
from .empirical_channel import sample_full_block
from .empirical_genie_scaling import (
    block_genie_risks,
    residual_for_orders,
    select_empirical_split,
)
from .prior import (
    Provenance,
    build_p1_metrics,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from .sc import ImpossibleDisclosedValueError
from .target_construction import (
    PRECONDITION_ORDER,
    TargetPopulationContractError,
    target_preconditions,
)
from .target_n_scaling import budget_k_total
from .transform import polar_transform

try:  # POSIX (the frozen command runs under WSL); Windows native has no resource module.
    import resource
except ImportError:  # pragma: no cover - exercised only on Windows native
    resource = None

PROTOCOL_NAME = "nbpolar-p15-empirical-genie-mid-n-scaling-gate"
MODE = "target-population-empirical-genie-mid-n-scaling-gate"

Q = 32
ALPHA = 2
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
FROZEN_N_VALUES = (32768, 65536)
FROZEN_TRAIN_SEEDS = (
    2026091960, 2026091961, 2026091962, 2026091963,
    2026091980, 2026091981, 2026091982, 2026091983,
)
FROZEN_DEV_SEEDS = (
    2026091970, 2026091971, 2026091972, 2026091973,
    2026091990, 2026091991, 2026091992, 2026091993,
)
FROZEN_TRAIN_BLOCKS_PER_STREAM = 4
FROZEN_DEV_BLOCKS_PER_STREAM = 4
FROZEN_TRAIN_BLOCKS_PER_N = 16
FROZEN_DEV_BLOCKS_PER_N = 16
FROZEN_CHUNK_ROWS = 512
# 64 blocks (16 TRAIN + 16 DEV per N, two N cells) x 2 genie layers.
PLANNED_GENIE_CALLS = (
    2 * (FROZEN_TRAIN_BLOCKS_PER_N + FROZEN_DEV_BLOCKS_PER_N) * len(FROZEN_N_VALUES)
)

EXPECTED_NPZ_BYTES = 25166822
FROZEN_COUNTS_PATH = (
    "/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/"
    "nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P15-EMPIRICAL-GENIE-MID-N-SCALING/"
    "empirical_genie_mid_n_gate"
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

# One-sided 95% Student-t factor for df=15 (exactly 16 DEV blocks per N).
T_FACTOR_DF15_95 = 1.753050356
UCB_THRESHOLD = 0.01

CANDIDATE_LABEL = "TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_CANDIDATE"
NOT_CONFIRMED_LABEL = "TARGET_EMPIRICAL_GENIE_F13_MID_N_SCALING_NOT_CONFIRMED"

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 2100.0
EXTERNAL_TIMEOUT_S = 2100
ULIMIT_VIRTUAL_KIB = 2097152

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
    "(np.random.default_rng(stream seed)), blocks sequential, no global RNG"
)
TRUTH_BOUNDARY = (
    "Alice truth enters only sampling and oracle-conditioned genie rows; "
    "it never enters an undisclosed operational metric, decision or "
    "candidate label; there is no operational decoder in this gate, hence "
    "no tag, no Toeplitz master and no disclosed values"
)
CONSTRUCTION_RULE = (
    "per TRAIN block accumulate h_i=-log2 p_i[U_i], e_i=1-max p_i from the "
    "genie rows; pool means per layer; worst-first orders by accepted "
    "(e,h,index); K_total=floor((1.3*N*(H1+H2)-64)/5) clipped to [0,2N] "
    "(6811 at N=32768, 13636 at N=65536); all feasible (K1,K2) enumerated, "
    "lexicographic minimum of (TRAIN residual e sum, K1, K2); frozen before "
    "that N's first DEV block"
)
RESIDUAL_SCOPE = (
    "genie union-bound construction proxy: R sums undisclosed-coordinate "
    "genie error risks; it is not operational FER, not a real-channel "
    "result and not proof of any minimum N"
)

INTEGRITY_GATE_ORDER = (
    "target_population_contract",
    "two_n_cells_complete",
    "streams_disjoint_frozen",
    "orders_valid_frozen_before_dev",
    "budget_allocation_reproduced",
    "risks_finite",
    "zero_genie_exceptions",
    "truth_isolation",
    "no_unregistered_calls",
    "checkpoint_accounting_consistent",
    "attempt_read_accounting_exact",
    "resource_limits_met_and_no_abort",
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "construction_and_allocations.json",
    "per_block_genie_residuals.jsonl",
    "aggregate_summary.json",
    "report.md",
)

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
    "ulimit -v 2097152\n"
    "timeout 2100 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_mid_n "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --floor 1e-15 --target-f 1.3 "
    "--n-values 32768 65536 "
    "--train-seeds 2026091960 2026091961 2026091962 2026091963 "
    "2026091980 2026091981 2026091982 2026091983 "
    "--dev-seeds 2026091970 2026091971 2026091972 2026091973 "
    "2026091990 2026091991 2026091992 2026091993 "
    "--train-blocks-per-stream 4 --dev-blocks-per-stream 4 --chunk-rows 512 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)
CLAIM_SCOPE = (
    "frozen V25 TRAIN target-population empirical-genie mid-N "
    "construction/rate development signal only; not held-out or real frame "
    "FER, efficiency, key rate, scaling, qualification or promotion; the "
    "UCB is a genie construction proxy, not an FER threshold or proof of "
    "any minimum N; undetected has no meaning in this tag-free gate and no "
    "success bucket exists"
)

# Process-level reopen guard: set at the first NPZ content open, never cleared.
_NPZ_CONTENT_OPENED = False

__all__ = [
    "PROTOCOL_NAME",
    "MODE",
    "Q",
    "ALPHA",
    "FROZEN_SOURCE",
    "FROZEN_FLOOR",
    "FROZEN_TARGET_F",
    "FROZEN_N_VALUES",
    "FROZEN_TRAIN_SEEDS",
    "FROZEN_DEV_SEEDS",
    "FROZEN_TRAIN_BLOCKS_PER_STREAM",
    "FROZEN_DEV_BLOCKS_PER_STREAM",
    "FROZEN_TRAIN_BLOCKS_PER_N",
    "FROZEN_DEV_BLOCKS_PER_N",
    "FROZEN_CHUNK_ROWS",
    "PLANNED_GENIE_CALLS",
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
    "T_FACTOR_DF15_95",
    "UCB_THRESHOLD",
    "CANDIDATE_LABEL",
    "NOT_CONFIRMED_LABEL",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S",
    "ULIMIT_VIRTUAL_KIB",
    "ATTEMPT_CONSUMPTION_POINT",
    "ARTIFACT_READ_ACCOUNTING",
    "SUPPORT_RULE",
    "SAMPLING_RULE",
    "TRUTH_BOUNDARY",
    "CONSTRUCTION_RULE",
    "RESIDUAL_SCOPE",
    "INTEGRITY_GATE_ORDER",
    "OUTPUT_FILES",
    "FROZEN_COMMAND",
    "CLAIM_SCOPE",
    "EmpiricalGenieMidNResourceError",
    "student_t_ucb_95",
    "dev_block_residual",
    "run_empirical_genie_mid_n",
    "build_parser",
    "main",
]


class EmpiricalGenieMidNResourceError(RuntimeError):
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


def _check_power_of_two(value, name: str) -> int:
    size = _as_int(value, name, minimum=1)
    if size & (size - 1):
        raise ValueError(f"{name} must be a positive power of two, got {size}")
    return size


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


def student_t_ucb_95(values) -> dict:
    """Mean, sample std, range and one-sided 95% Student-t UCB of DEV residuals.

    The frozen gate always holds exactly 16 DEV blocks per N (df=15,
    factor ``1.753050356``); any other sample count returns the same
    descriptive statistics with ``ucb`` set to ``None`` (test-seam
    behaviour only, never the frozen run).
    """
    arr = np.asarray(values, dtype=np.float64).ravel()
    count = int(arr.shape[0])
    if count < 2:
        raise ValueError(f"need at least 2 residual values, got {count}")
    if not np.isfinite(arr).all():
        raise ValueError("residual values must be finite")
    mean = float(arr.mean())
    std = float(arr.std(ddof=1))
    if not np.isfinite(std):
        raise ValueError("sample standard deviation is nonfinite")
    ucb = None
    if count == FROZEN_DEV_BLOCKS_PER_N:
        ucb = float(mean + T_FACTOR_DF15_95 * std / math.sqrt(count))
    return {
        "n": count,
        "mean": mean,
        "std_sample": std,
        "min": float(arr.min()),
        "max": float(arr.max()),
        "ucb_95_t15": ucb,
    }


def dev_block_residual(risks: dict, *, l1_order, l2_order, k1: int, k2: int) -> float:
    """Scalar DEV residual from one block's genie rows; zero extra calls.

    Sums the undisclosed-coordinate ``e`` risks under the frozen empirical
    split. Pure: no genie call, no RNG, no I/O.
    """
    out = residual_for_orders(
        risks["e1"], risks["e2"],
        np.asarray(l1_order, dtype=np.int64), np.asarray(l2_order, dtype=np.int64),
        int(k1), int(k2),
    )
    if not np.isfinite(out):
        raise ValueError("DEV block residual must be finite")
    return float(out)


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


def _position_rank(order) -> np.ndarray:
    order = np.asarray(order, dtype=np.int64)
    pos = np.empty(order.shape[0], dtype=np.int64)
    pos[order] = np.arange(order.shape[0], dtype=np.int64)
    return pos


@dataclass(frozen=True, eq=False)
class EmpiricalGenieMidNRun:
    """In-memory P15 gate run (also returned by the runner)."""

    records: list
    construction: dict
    plan: dict
    summary: dict


def _stub_plan(*, out_path, source, floor, target_f, n_list, train_list, dev_list,
               train_bps, dev_bps, chunk_rows) -> dict:
    frozen_k = {
        str(int(n)): int(budget_k_total(int(n), EXPECTED_H1 + EXPECTED_H2, FROZEN_TARGET_F))
        for n in n_list
    }
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
        "residual_scope": RESIDUAL_SCOPE,
        "q": Q,
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "floor": float(floor),
        "target_f": float(target_f),
        "chunk_rows": int(chunk_rows),
        "n_values": [int(v) for v in n_list],
        "train_seeds": [int(s) for s in train_list],
        "dev_seeds": [int(s) for s in dev_list],
        "train_blocks_per_stream": int(train_bps),
        "dev_blocks_per_stream": int(dev_bps),
        "planned_genie_calls": int(PLANNED_GENIE_CALLS),
        "frozen_k_total_from_literals": frozen_k,
        "entropy_expectations": {
            "h1": EXPECTED_H1,
            "h2": EXPECTED_H2,
            "total": EXPECTED_TOTAL,
            "entropy_tol": ENTROPY_TOL,
            "column_tol": COLUMN_TOL,
            "floor_entropy_change_tol": FLOOR_ENTROPY_TOL,
        },
        "precondition_order": list(PRECONDITION_ORDER),
        "integrity_gate_order": list(INTEGRITY_GATE_ORDER),
        "decision": {
            "ucb_threshold": UCB_THRESHOLD,
            "t_factor_df15_95": T_FACTOR_DF15_95,
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
        "# NB-Polar Phase 4-P15 empirical-genie mid-N scaling gate",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- source/target: `{summary['source']}`; q={summary['q']}, "
        f"target_f={summary['target_f']}, chunk_rows={summary['chunk_rows']}",
        f"- N values: {summary['n_values']}; TRAIN streams/blocks per stream: "
        f"{summary['train_blocks_per_stream']} each; DEV: {summary['dev_blocks_per_stream']} each",
        f"- genie calls: {summary['genie_calls']}/{summary['planned_genie_calls']}; "
        f"wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes; "
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
        "## Per-N construction and DEV genie residuals (proxy, not FER)",
        "",
        "| N | K_total | K1 | K2 | TRAIN residual | mean | std | min | "
        "max | UCB |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for tag in (str(v) for v in summary["n_values"]):
        row = summary["per_n"].get(tag)
        if row is None:
            lines.append(f"| {tag} | pending | pending | pending | pending |")
            continue
        stats = row.get("stats") or {}
        lines.append(
            f"| {row['n']} | {row['k_total']} | {row['k1']} | {row['k2']} | "
            f"{row['train_residual']!r} | {stats.get('mean')!r} | {stats.get('std_sample')!r} | "
            f"{stats.get('min')!r} | {stats.get('max')!r} | {stats.get('ucb_95_t15')!r} |"
        )
    lines += [
        "",
        "## Per-N resources",
        "",
        "| N | wall_s | rss_hwm | VmPeak_kB | VmSize_kB |",
        "|---|---|---|---|---|",
    ]
    for tag in (str(v) for v in summary["n_values"]):
        row = summary["per_n"].get(tag)
        if row is None or "resources" not in row:
            lines.append(f"| {tag} | pending | pending | pending | pending |")
            continue
        res = row["resources"]
        lines.append(
            f"| {tag} | {res['wall_s']} | {res['rss_bytes_hwm']} | "
            f"{res['vm_peak_kb']} | {res['vm_size_kb']} |"
        )
    lines += [
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
        f"- smallest candidate N: {summary['smallest_candidate_n']}",
        "",
        f"**Scope:** {summary['claim_scope']}.",
        "",
    ]
    return "\n".join(lines)


def run_empirical_genie_mid_n(
    *,
    counts=None,
    counts_path=FROZEN_COUNTS_PATH,
    source: str = FROZEN_SOURCE,
    floor=FROZEN_FLOOR,
    target_f: float = FROZEN_TARGET_F,
    n_values=FROZEN_N_VALUES,
    train_seeds=FROZEN_TRAIN_SEEDS,
    dev_seeds=FROZEN_DEV_SEEDS,
    train_blocks_per_stream: int = FROZEN_TRAIN_BLOCKS_PER_STREAM,
    dev_blocks_per_stream: int = FROZEN_DEV_BLOCKS_PER_STREAM,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_entropies=None,
) -> EmpiricalGenieMidNRun:
    """Execute the frozen P15 empirical-genie mid-N scaling gate; write five files.

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
    target_f = _check_target_f(target_f)
    if target_f != FROZEN_TARGET_F:
        raise ValueError(f"frozen point requires target-f={FROZEN_TARGET_F}, got {target_f}")
    _check_chunk_contract(chunk_rows)
    n_list = [_check_power_of_two(v, "n-values entry") for v in n_values]
    if [int(v) for v in n_list] != [int(v) for v in FROZEN_N_VALUES]:
        raise ValueError(
            "frozen point requires n-values "
            f"{[int(v) for v in FROZEN_N_VALUES]}, got {[int(v) for v in n_list]}"
        )
    train_list = [_as_int(s, "train seed", minimum=0) for s in train_seeds]
    dev_list = [_as_int(s, "dev seed", minimum=0) for s in dev_seeds]
    train_bps = _as_int(train_blocks_per_stream, "train-blocks-per-stream", minimum=1)
    if train_bps != FROZEN_TRAIN_BLOCKS_PER_STREAM:
        raise ValueError(
            "frozen point requires train-blocks-per-stream="
            f"{FROZEN_TRAIN_BLOCKS_PER_STREAM}, got {train_bps}"
        )
    dev_bps = _as_int(dev_blocks_per_stream, "dev-blocks-per-stream", minimum=1)
    if dev_bps != FROZEN_DEV_BLOCKS_PER_STREAM:
        raise ValueError(
            "frozen point requires dev-blocks-per-stream="
            f"{FROZEN_DEV_BLOCKS_PER_STREAM}, got {dev_bps}"
        )
    # N-to-seed grouping: four TRAIN and four DEV streams per N, in N order.
    if len(train_list) != 4 * len(n_list):
        raise ValueError(
            f"train-seeds must hold 4 streams per N ({4 * len(n_list)}), got {len(train_list)}"
        )
    if len(dev_list) != 4 * len(n_list):
        raise ValueError(
            f"dev-seeds must hold 4 streams per N ({4 * len(n_list)}), got {len(dev_list)}"
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

    plan = _stub_plan(
        out_path=out_path, source=source, floor=floor, target_f=target_f,
        n_list=n_list, train_list=train_list, dev_list=dev_list,
        train_bps=train_bps, dev_bps=dev_bps, chunk_rows=chunk_rows,
    )

    # ---- create all five files BEFORE the content open (stub inventory).
    out_path.mkdir(parents=True)
    constructed: dict[str, dict] = {}
    try:
        _write_json(out_path / "frozen_plan.json", plan)
        _write_json(
            out_path / "construction_and_allocations.json",
            {"protocol": PROTOCOL_NAME, "status": "pending_content_open", "cells": constructed},
        )
        (out_path / "per_block_genie_residuals.jsonl").write_text("", encoding="utf-8")
        _write_json(
            out_path / "aggregate_summary.json",
            {"protocol": PROTOCOL_NAME, "status": "pending_content_open"},
        )
        (out_path / "report.md").write_text(
            "# NB-Polar Phase 4-P15 empirical-genie mid-N scaling gate\n\n"
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

        # ---- frozen preconditions: no genie call may happen before this passes.
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
        field = make_gf32()
        start = time.perf_counter()

        calls = {"genie": 0}
        dev_records: list[dict] = []
        per_n_cells: dict[str, dict] = {}
        provenance_violations = 0
        resource_stop: str | None = None

        def checkpoint(summary_doc: dict) -> None:
            _write_json(
                out_path / "construction_and_allocations.json",
                {
                    "protocol": PROTOCOL_NAME,
                    "frozen_before_first_dev": bool(per_n_cells),
                    "cells": {tag: dict(cell) for tag, cell in constructed.items()},
                },
            )
            _write_json(out_path / "aggregate_summary.json", summary_doc)
            (out_path / "report.md").write_text(_render_report(summary_doc), encoding="utf-8")

        def partial_summary(outcome_label: str, gates: dict, failing: list) -> dict:
            return {
                "analysis": PROTOCOL_NAME,
                "mode": MODE,
                "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "repository": "HD-QKD_Polar_Comparison-nbpolar",
                "source": source,
                "counts_path": accounting.get("counts_path"),
                "input_mode": accounting.get("input_mode"),
                "q": Q,
                "target_f": float(target_f),
                "chunk_rows": int(chunk_rows),
                "n_values": [int(v) for v in n_list],
                "train_seeds": [int(s) for s in train_list],
                "dev_seeds": [int(s) for s in dev_list],
                "train_blocks_per_stream": int(train_bps),
                "dev_blocks_per_stream": int(dev_bps),
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
                "per_n": {tag: dict(cell) for tag, cell in per_n_cells.items()},
                "dev_block_count": int(len(dev_records)),
                "genie_calls": int(calls["genie"]),
                "planned_genie_calls": int(PLANNED_GENIE_CALLS),
                "provenance_violations": int(provenance_violations),
                "integrity": {name: bool(gates.get(name, False)) for name in INTEGRITY_GATE_ORDER},
                "integrity_all_pass": bool(all(gates.get(name, False) for name in INTEGRITY_GATE_ORDER)),
                "failing_integrity_gates": list(failing),
                "outcome_label": outcome_label,
                "smallest_candidate_n": None,
                "wall_s": round(float(time.perf_counter() - start), 6),
                "rss_bytes_peak": _peak_rss_bytes(),
                "resource_stop_fired": bool(resource_stop is not None),
                "resource_stop_reason": resource_stop,
                "attempt_read_accounting": dict(accounting),
                "claim_scope": CLAIM_SCOPE,
            }

        for n_pos, n in enumerate(n_list):
            cell_start = time.perf_counter()
            cell_trains = train_list[4 * n_pos:4 * n_pos + 4]
            cell_devs = dev_list[4 * n_pos:4 * n_pos + 4]
            k_total = budget_k_total(n, h_total, target_f)
            leakage = 5 * k_total + 64
            budget_bits = float(target_f) * int(n) * h_total
            if not leakage <= budget_bits:
                raise TargetPopulationContractError(
                    f"BLOCKED(budget_allocation_reproduced): N={n} leakage {leakage} "
                    f"exceeds f-budget {budget_bits!r}"
                )

            # ---- TRAIN: pooled genie sufficient statistics per layer, plus
            # ---- per-stream accumulators for the diagnostics-only stability.
            acc_l1 = _empty_acc(n)
            acc_l2 = _empty_acc(n)
            stream_accs: list[dict] = []
            for seed in cell_trains:
                rng = np.random.default_rng(int(seed))
                s1, s2 = _empty_acc(n), _empty_acc(n)
                for _ in range(int(train_bps)):
                    reason = _budget_exceeded(start, cap)
                    if reason is not None:
                        resource_stop = reason
                        raise EmpiricalGenieMidNResourceError(
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
                        s1["impossible"] += 1
                        s2["impossible"] += 1
                        continue
                    for acc, vec, key in (
                        (acc_l1, risks["h1"], "h"), (acc_l1, risks["e1"], "e"),
                        (acc_l2, risks["h2"], "h"), (acc_l2, risks["e2"], "e"),
                        (s1, risks["h1"], "h"), (s1, risks["e1"], "e"),
                        (s2, risks["h2"], "h"), (s2, risks["e2"], "e"),
                    ):
                        acc[key] += vec
                    acc_l1["used"] += 1
                    acc_l2["used"] += 1
                    s1["used"] += 1
                    s2["used"] += 1
                stream_accs.append({"seed": int(seed), "l1": s1, "l2": s2})

            # ---- freeze empirical orders/allocation/TRAIN residual before DEV.
            used1 = max(int(acc_l1["used"]), 1)
            used2 = max(int(acc_l2["used"]), 1)
            e1_mean, h1_mean = acc_l1["e"] / used1, acc_l1["h"] / used1
            e2_mean, h2_mean = acc_l2["e"] / used2, acc_l2["h"] / used2
            split = select_empirical_split(n, e1_mean, h1_mean, e2_mean, h2_mean, k_total)
            pooled_l1 = np.asarray(split["l1_order"], dtype=np.int64)
            pooled_l2 = np.asarray(split["l2_order"], dtype=np.int64)
            # Diagnostics-only: per-stream order stability vs the pooled order.
            stability = {"l1": [], "l2": []}
            pooled_pos = {"l1": _position_rank(pooled_l1), "l2": _position_rank(pooled_l2)}
            for entry in stream_accs:
                for layer, acc in (("l1", entry["l1"]), ("l2", entry["l2"])):
                    used = max(int(acc["used"]), 1)
                    order = np.asarray(
                        disclosure_order_from_stats(acc["e"] / used, acc["h"] / used),
                        dtype=np.int64,
                    )
                    stability[layer].append(float(spearman_rank_corr(
                        _position_rank(order), pooled_pos[layer])))
            cell = {
                "n": int(n),
                "train_seeds": [int(s) for s in cell_trains],
                "dev_seeds": [int(s) for s in cell_devs],
                "train_blocks": int(len(cell_trains) * int(train_bps)),
                "train_used_l1": int(acc_l1["used"]),
                "train_used_l2": int(acc_l2["used"]),
                "train_impossible": int(acc_l1["impossible"] + acc_l2["impossible"]),
                "k_total": int(k_total),
                "k1": int(split["k1"]),
                "k2": int(split["k2"]),
                "train_residual": float(split["residual"]),
                "leakage_bits": int(leakage),
                "f": float(leakage / (int(n) * h_total)),
                "l1_order": [int(v) for v in np.asarray(split["l1_order"]).tolist()],
                "l2_order": [int(v) for v in np.asarray(split["l2_order"]).tolist()],
                "pooled_e1_mean": [float(v) for v in e1_mean.tolist()],
                "pooled_h1_mean": [float(v) for v in h1_mean.tolist()],
                "pooled_e2_mean": [float(v) for v in e2_mean.tolist()],
                "pooled_h2_mean": [float(v) for v in h2_mean.tolist()],
                "order_stability_spearman_vs_pooled": {
                    "l1": [float(v) for v in stability["l1"]],
                    "l2": [float(v) for v in stability["l2"]],
                    "diagnostic_only": True,
                },
            }
            freeze_sha = hashlib.sha256(
                json.dumps(
                    {k: cell[k] for k in (
                        "n", "k_total", "k1", "k2", "l1_order", "l2_order",
                        "pooled_e1_mean", "pooled_h1_mean",
                        "pooled_e2_mean", "pooled_h2_mean",
                    )},
                    sort_keys=True, separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            cell["freeze_sha256"] = freeze_sha
            constructed[str(int(n))] = cell
            per_n_cells[str(int(n))] = {
                **{k: cell[k] for k in (
                    "n", "train_seeds", "dev_seeds", "train_blocks",
                    "train_used_l1", "train_used_l2", "train_impossible",
                    "k_total", "k1", "k2", "train_residual", "leakage_bits", "f",
                )},
                "freeze_sha256": freeze_sha,
                "order_stability_spearman_vs_pooled": dict(
                    cell["order_stability_spearman_vs_pooled"]),
                "empirical_r": [],
                "block_errors": 0,
                "resources": _cell_resource_record(0.0),
            }
            emp = {
                "l1_order": pooled_l1,
                "l2_order": pooled_l2,
                "k1": int(split["k1"]),
                "k2": int(split["k2"]),
            }

            # ---- DEV: scalar residuals only; never select or tune from DEV.
            for seed in cell_devs:
                rng = np.random.default_rng(int(seed))
                for block_index in range(int(dev_bps)):
                    block_start = time.perf_counter()
                    reason = _budget_exceeded(start, cap)
                    if reason is not None:
                        resource_stop = reason
                        raise EmpiricalGenieMidNResourceError(
                            f"BLOCKED(resource_limits_met_and_no_abort): {reason} during DEV"
                        )
                    bob, _a_full, high, low = sample_full_block(
                        rng, entropy.p_b, entropy.f, Q, Q, n
                    )
                    u1 = polar_transform(high, field=field, alpha=ALPHA)
                    u2 = polar_transform(low, field=field, alpha=ALPHA)
                    try:
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
                        risks = block_genie_risks(
                            l1_metric.logp, u1, l2_metric.logp, u2,
                            field=field, calls=calls,
                        )
                        residual = dev_block_residual(
                            risks, l1_order=emp["l1_order"], l2_order=emp["l2_order"],
                            k1=emp["k1"], k2=emp["k2"],
                        )
                        record = {
                            "n": int(n),
                            "stream_seed": int(seed),
                            "block_index": int(block_index),
                            "r_empirical": float(residual),
                            "error": None,
                            "resources": _cell_resource_record(
                                time.perf_counter() - block_start),
                        }
                    except MemoryError:
                        raise
                    except Exception as exc:  # block failure: recorded, gate fails
                        record = {
                            "n": int(n),
                            "stream_seed": int(seed),
                            "block_index": int(block_index),
                            "r_empirical": None,
                            "error": type(exc).__name__,
                            "resources": _cell_resource_record(
                                time.perf_counter() - block_start),
                        }
                        per_n_cells[str(int(n))]["block_errors"] += 1
                    dev_records.append(record)
                    _append_jsonl(out_path / "per_block_genie_residuals.jsonl", record)
                    if record["error"] is None:
                        per_n_cells[str(int(n))]["empirical_r"].append(record["r_empirical"])
                    # Checkpoint the same five files after every completed block.
                    gates_now = _integrity_gates_partial(
                        out_path=out_path,
                        n_list=n_list, train_list=train_list, dev_list=dev_list,
                        train_bps=train_bps, dev_bps=dev_bps,
                        constructed=constructed, dev_records=dev_records,
                        calls=calls, accounting=accounting,
                        provenance_violations=provenance_violations,
                        start=start, cap=cap, resource_stop=resource_stop,
                        counts_shape=counts_arr.shape,
                        precondition_passed=bool(precondition_report.passed),
                    )
                    failing_now = [g for g in INTEGRITY_GATE_ORDER if not gates_now[g]]
                    checkpoint(partial_summary(f"RUNNING({len(dev_records)})", gates_now, failing_now))
            per_n_cells[str(int(n))]["resources"] = _cell_resource_record(
                time.perf_counter() - cell_start
            )

        # ---- per-N aggregates, classification and final gates.
        wall_s = time.perf_counter() - start
        rss_peak = _peak_rss_bytes()
        final_cells: dict[str, dict] = {}
        candidate_ns: list[int] = []
        for tag, pcell in per_n_cells.items():
            stats = student_t_ucb_95(pcell["empirical_r"]) if len(pcell["empirical_r"]) >= 2 else {
                "n": len(pcell["empirical_r"]), "mean": None, "std_sample": None,
                "min": None, "max": None, "ucb_95_t15": None,
            }
            final_cells[tag] = {
                **{k: pcell[k] for k in (
                    "n", "train_seeds", "dev_seeds", "train_blocks",
                    "train_used_l1", "train_used_l2", "train_impossible",
                    "k_total", "k1", "k2", "train_residual", "leakage_bits", "f",
                    "freeze_sha256", "order_stability_spearman_vs_pooled", "resources",
                )},
                "dev_blocks": int(len(pcell["empirical_r"])),
                "block_errors": int(pcell["block_errors"]),
                "stats": stats,
            }
            ucb = stats.get("ucb_95_t15")
            if ucb is not None and ucb <= UCB_THRESHOLD:
                candidate_ns.append(int(pcell["n"]))
        gates = _integrity_gates_partial(
            out_path=out_path,
            n_list=n_list, train_list=train_list, dev_list=dev_list,
            train_bps=train_bps, dev_bps=dev_bps,
            constructed=constructed, dev_records=dev_records,
            calls=calls, accounting=accounting,
            provenance_violations=provenance_violations,
            start=start, cap=cap, resource_stop=resource_stop,
            counts_shape=counts_arr.shape,
            precondition_passed=bool(precondition_report.passed),
            final_cells=final_cells,
        )
        failing = [g for g in INTEGRITY_GATE_ORDER if not gates[g]]
        if all(gates[g] for g in INTEGRITY_GATE_ORDER):
            outcome = CANDIDATE_LABEL if candidate_ns else NOT_CONFIRMED_LABEL
        else:
            outcome = f"BLOCKED({failing[0]})" if failing else "BLOCKED(unknown)"
        summary = partial_summary(outcome, gates, failing)
        summary["per_n"] = final_cells
        summary["smallest_candidate_n"] = min(candidate_ns) if candidate_ns else None
        summary["candidate_ns"] = sorted(candidate_ns)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        checkpoint(summary)
        return EmpiricalGenieMidNRun(
            records=dev_records,
            construction={
                "protocol": PROTOCOL_NAME,
                "frozen_before_first_dev": True,
                "cells": {tag: dict(cell) for tag, cell in constructed.items()},
            },
            plan=plan,
            summary=summary,
        )
    except EmpiricalGenieMidNResourceError:
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
                "# NB-Polar Phase 4-P15 empirical-genie mid-N scaling gate\n\n"
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
                "# NB-Polar Phase 4-P15 empirical-genie mid-N scaling gate\n\n"
                "outcome label: `BLOCKED(resource_limits_met_and_no_abort)`\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        raise EmpiricalGenieMidNResourceError(
            f"BLOCKED(resource_limits_met_and_no_abort): MemoryError: {exc}"
        ) from exc


def _integrity_gates_partial(
    *,
    out_path: Path,
    n_list,
    train_list,
    dev_list,
    train_bps,
    dev_bps,
    constructed: dict,
    dev_records: list,
    calls: dict,
    accounting: dict,
    provenance_violations: int,
    start: float,
    cap: float,
    resource_stop,
    counts_shape,
    precondition_passed: bool,
    final_cells: dict | None = None,
) -> dict:
    n_ints = [int(v) for v in n_list]
    shape_frozen = bool(
        n_ints == [int(v) for v in FROZEN_N_VALUES]
        and [int(s) for s in train_list] == [int(s) for s in FROZEN_TRAIN_SEEDS]
        and [int(s) for s in dev_list] == [int(s) for s in FROZEN_DEV_SEEDS]
        and int(train_bps) == FROZEN_TRAIN_BLOCKS_PER_STREAM
        and int(dev_bps) == FROZEN_DEV_BLOCKS_PER_STREAM
    )
    planned_train = len(n_ints) * 4 * int(train_bps)
    planned_dev = len(n_ints) * 4 * int(dev_bps)
    planned_calls = 2 * (planned_train + planned_dev)

    # Two complete N cells with 16 TRAIN + 16 DEV blocks per N (final only).
    if final_cells is None:
        cells_ok = True
    else:
        cells_ok = bool(
            sorted(int(t) for t in final_cells) == sorted(int(v) for v in FROZEN_N_VALUES)
            and all(
                int(final_cells[str(n)]["train_used_l1"]) == FROZEN_TRAIN_BLOCKS_PER_N
                and int(final_cells[str(n)]["train_used_l2"]) == FROZEN_TRAIN_BLOCKS_PER_N
                and int(final_cells[str(n)]["dev_blocks"]) == FROZEN_DEV_BLOCKS_PER_N
                and int(final_cells[str(n)]["block_errors"]) == 0
                for n in FROZEN_N_VALUES
            )
        )
    streams_ok = bool(
        set(int(s) for s in train_list).isdisjoint(int(s) for s in dev_list)
        and len(set(int(s) for s in train_list)) == len(train_list)
        and len(set(int(s) for s in dev_list)) == len(dev_list)
        and (not shape_frozen or (
            [int(s) for s in train_list] == [int(s) for s in FROZEN_TRAIN_SEEDS]
            and [int(s) for s in dev_list] == [int(s) for s in FROZEN_DEV_SEEDS]
        ))
    )

    # Valid orders: every frozen cell order is a permutation; freeze SHA
    # recomputed from the persisted construction matches.
    orders_ok = True
    for tag, cell in constructed.items():
        n = int(cell["n"])
        if not (_order_is_permutation(cell.get("l1_order"), n)
                and _order_is_permutation(cell.get("l2_order"), n)):
            orders_ok = False
            break
        recomputed = hashlib.sha256(
            json.dumps(
                {k: cell[k] for k in (
                    "n", "k_total", "k1", "k2", "l1_order", "l2_order",
                    "pooled_e1_mean", "pooled_h1_mean",
                    "pooled_e2_mean", "pooled_h2_mean",
                )},
                sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if recomputed != cell.get("freeze_sha256"):
            orders_ok = False
            break

    # Exact K budget/allocation replay from the literals and pooled risks.
    replay_ok = True
    for tag, cell in constructed.items():
        n = int(cell["n"])
        try:
            k_total = budget_k_total(n, EXPECTED_H1 + EXPECTED_H2, FROZEN_TARGET_F)
            replay = select_empirical_split(
                n,
                np.asarray(cell["pooled_e1_mean"]),
                np.asarray(cell["pooled_h1_mean"]),
                np.asarray(cell["pooled_e2_mean"]),
                np.asarray(cell["pooled_h2_mean"]),
                k_total,
            )
            leakage = 5 * k_total + 64
            budget = float(FROZEN_TARGET_F) * int(n) * (EXPECTED_H1 + EXPECTED_H2)
        except (ValueError, TypeError):
            replay_ok = False
            break
        if not (
            int(cell["k_total"]) == int(k_total)
            and int(cell["k1"]) == int(replay["k1"])
            and int(cell["k2"]) == int(replay["k2"])
            and abs(float(cell["train_residual"]) - float(replay["residual"])) <= 1e-9
            and [int(v) for v in cell["l1_order"]] == [int(v) for v in replay["l1_order"].tolist()]
            and [int(v) for v in cell["l2_order"]] == [int(v) for v in replay["l2_order"].tolist()]
            and int(leakage) <= budget
        ):
            replay_ok = False
            break

    finite_ok = True
    for tag, cell in constructed.items():
        for key in ("pooled_e1_mean", "pooled_h1_mean", "pooled_e2_mean", "pooled_h2_mean"):
            arr = np.asarray(cell.get(key, []), dtype=np.float64)
            if not (arr.size and np.isfinite(arr).all() and np.isfinite(float(cell.get("train_residual", np.nan)))):
                finite_ok = False
                break
        if not finite_ok:
            break
    if finite_ok:
        for record in dev_records:
            if record.get("error") is not None:
                finite_ok = False
                break
            if not np.isfinite(float(record["r_empirical"])):
                finite_ok = False
                break

    impossible_total = sum(int(cell.get("train_impossible", 0)) for cell in constructed.values())
    block_errors = sum(1 for record in dev_records if record.get("error") is not None)
    zero_exceptions = bool(impossible_total == 0 and block_errors == 0)

    truth_ok = bool(int(provenance_violations) == 0)
    calls_ok = bool(int(calls.get("genie", 0)) == int(planned_calls)) if final_cells is not None else bool(
        int(calls.get("genie", 0)) <= int(planned_calls)
    )
    files_ok = True
    try:
        for name in OUTPUT_FILES:
            if not out_path.joinpath(name).is_file():
                files_ok = False
                break
        if files_ok:
            with open(out_path / "per_block_genie_residuals.jsonl", "r", encoding="utf-8") as handle:
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
    resource_ok = bool(
        resource_stop is None
        and block_errors == 0
        and float(wall_now) <= float(cap)
        and (rss_now is None or int(rss_now) <= RSS_LIMIT_BYTES)
    )
    return {
        "target_population_contract": bool(precondition_passed),
        "two_n_cells_complete": bool(cells_ok and shape_frozen) if final_cells is not None else bool(shape_frozen),
        "streams_disjoint_frozen": bool(streams_ok and shape_frozen),
        "orders_valid_frozen_before_dev": bool(orders_ok and bool(constructed)),
        "budget_allocation_reproduced": bool(replay_ok and bool(constructed)),
        "risks_finite": bool(finite_ok and bool(constructed)),
        "zero_genie_exceptions": bool(zero_exceptions and bool(constructed)),
        "truth_isolation": bool(truth_ok),
        "no_unregistered_calls": bool(calls_ok),
        "checkpoint_accounting_consistent": bool(files_ok and accounting_exact),
        "attempt_read_accounting_exact": bool(accounting_exact),
        "resource_limits_met_and_no_abort": bool(resource_ok),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p15-empirical-genie-mid-n-scaling",
        description=(
            "NB-Polar Phase 4-P15 empirical-genie mid-N scaling development "
            "gate (frozen V25 1M TRAIN counts)"
        ),
    )
    parser.add_argument("--counts", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--floor", required=True, type=float)
    parser.add_argument("--target-f", required=True, type=float, dest="target_f")
    parser.add_argument("--n-values", required=True, type=int, nargs="+", dest="n_values")
    parser.add_argument("--train-seeds", required=True, type=int, nargs="+", dest="train_seeds")
    parser.add_argument("--dev-seeds", required=True, type=int, nargs="+", dest="dev_seeds")
    parser.add_argument("--train-blocks-per-stream", required=True, type=int,
                        dest="train_blocks_per_stream")
    parser.add_argument("--dev-blocks-per-stream", required=True, type=int,
                        dest="dev_blocks_per_stream")
    parser.add_argument("--chunk-rows", required=True, type=int, dest="chunk_rows")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_empirical_genie_mid_n(
            counts_path=args.counts,
            source=args.source,
            floor=args.floor,
            target_f=args.target_f,
            n_values=args.n_values,
            train_seeds=args.train_seeds,
            dev_seeds=args.dev_seeds,
            train_blocks_per_stream=args.train_blocks_per_stream,
            dev_blocks_per_stream=args.dev_blocks_per_stream,
            chunk_rows=args.chunk_rows,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p15 empirical genie mid-n refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "dev_block_count": summary["dev_block_count"],
                "integrity_all_pass": summary["integrity_all_pass"],
                "outcome_label": summary["outcome_label"],
                "smallest_candidate_n": summary["smallest_candidate_n"],
                "out_root": args.out_dir,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
