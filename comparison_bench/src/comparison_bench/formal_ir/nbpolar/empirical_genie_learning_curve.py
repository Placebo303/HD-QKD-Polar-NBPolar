"""NB-Polar Phase 4-P14 empirical-genie construction learning curve gate.

Frozen point (packet ``NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE``,
OpenSpec ``formal-ir-nbpolar-phase4-p0`` P14 delta): at P13's N=16384 point,
determine whether failure to reach the f=1.3 residual target was materially
caused by constructing from only eight TRAIN blocks. Build nested
8/16/32/64/128-block constructions from the one 128-block TRAIN sequence
and evaluate all five on the same independent 32 DEV blocks. This is a
model-sampled genie construction diagnostic, not operational FER or
real-data qualification.

Frozen semantics:

- Input: one call to the accepted ``load_v25_channel_counts(path)``; a
  stat-only size check of exactly ``25,166,822`` bytes happens before the
  content open, and the single artifact read plus the single scientific
  attempt are consumed at the first NPZ content open (never reopened,
  never retried; a module-level reopen guard refuses a second NPZ-mode
  call). Refusals (absent root, CLI parse, chunk/n/prefix/seed-shape
  contract) happen before the content open; any post-open failure is
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
  (consumption already spent: recorded in the stderr message and the
  freeze doc, and best-effort in the pre-created stub files, never as a
  fresh root).
- Matrix: N=16384 only. TRAIN eight streams x 16 blocks (128) in
  stream-major order (seed ascending, then block index ascending); DEV
  four disjoint streams x 8 blocks (32). Each stream restarts its RNG.
  Nested prefixes B=8/16/32/64/128 from that one TRAIN sequence. Each
  TRAIN block is decoded once per layer; the running risk sums serve
  every applicable prefix (no repeated calls: 128 TRAIN blocks x 2).
  Each DEV block is decoded once per layer and its genie rows score all
  five frozen constructions (32 DEV blocks x 2). Planned genie calls =
  320. Sampling, L1 true-prefix genie and oracle-conditioned L2 genie
  are exactly P13 (shared helpers). No tag or Toeplitz master exists in
  this gate.
- Construction: per TRAIN block accumulate coordinate risks
  ``h_i = -log2 p_i[U_i]`` and ``e_i = 1 - max p_i`` into running sums;
  at each prefix boundary pool means, order each layer worst-first by
  the accepted ``(e, h, index)`` semantics, and set
  ``K_total = floor((1.3*N*(H1+H2)-64)/5)`` clipped to ``[0, 2N]``
  (3399 at the frozen point); every feasible integer ``(K1, K2)`` with
  ``K1+K2=K_total`` is enumerated and the lexicographic minimum of
  ``(TRAIN residual e sum, K1, K2)`` is selected. All five
  constructions are frozen before the first DEV block.
- DEV: per block the five scalar residuals
  ``R_B = sum(e1[undisclosed coords of prefix B])
         + sum(e2[undisclosed coords of prefix B])``
  from the one decode. DEV is never selected or tuned from. Per B: the
  32 DEV ``R_B`` values, mean, sample standard deviation, range and
  one-sided 95% Student-t upper confidence bound
  ``mean + 1.695518782*std/sqrt(32)`` (df=31); paired ``R_B - R_8``
  and adjacent differences with mean/std/UCB. The residual is a genie
  union-bound construction proxy; it is not operational FER.
- Report-only: pairwise order Spearman/top-K overlap of each prefix
  against B=128, allocation movement across prefixes, and per-block
  improved/tied/regressed counts against R_8. P13's B=8 is a historical
  reference only: different-seed blocks are never merged and equality
  is never required.
- Decision (implemented here, adjudicated by the main thread):
  ``TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_CANDIDATE`` if the
  frozen B=128 one-sided DEV residual UCB ``<= 0.01``;
  ``..._NOT_CONFIRMED`` if integrity passes but it does not; otherwise
  ``BLOCKED(<earliest>)``. Other prefixes diagnose learning only.
- Outputs: exactly five scalar-only files (public orders plus scalar
  block statistics; never counts, sampled symbols, truth vectors,
  decoder outputs, metric planes or RNG state), created as stubs
  before the content open and checkpointed after every completed
  block. Per run: wall, RSS HWM, Linux ``VmPeak`` and ``VmSize``.
  On MemoryError/resource failure the checkpoints are preserved, a
  BLOCKED summary is finalized if possible, and the run is never rerun.

No Model-F/held-out/raw/real frame, no other N in the frozen run, no
FWHT/APP/SCL, no operational decode, no FER/efficiency/key-rate
qualification or promotion, no commit. The claim scope is a
construction learning-curve diagnostic for the frozen V25 TRAIN target
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
from .construction import spearman_rank_corr, topk_overlap
from .empirical_channel import sample_full_block
from .empirical_genie_scaling import (
    block_genie_risks,
    residual_for_orders,
    select_empirical_split,
    student_t_ucb_95,
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

PROTOCOL_NAME = "nbpolar-p14-empirical-genie-learning-curve-gate"
MODE = "target-population-empirical-genie-learning-curve-gate"

Q = 32
ALPHA = 2
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
FROZEN_N = 16384
FROZEN_TRAIN_SEEDS = (
    2026091930, 2026091931, 2026091932, 2026091933,
    2026091934, 2026091935, 2026091936, 2026091937,
)
FROZEN_DEV_SEEDS = (2026091940, 2026091941, 2026091942, 2026091943)
FROZEN_TRAIN_BLOCKS_PER_STREAM = 16
FROZEN_DEV_BLOCKS_PER_STREAM = 8
FROZEN_TRAIN_BLOCKS = 128
FROZEN_DEV_BLOCKS = 32
FROZEN_PREFIX_BLOCKS = (8, 16, 32, 64, 128)
FROZEN_CHUNK_ROWS = 512
PLANNED_GENIE_CALLS = 2 * (FROZEN_TRAIN_BLOCKS + FROZEN_DEV_BLOCKS)

EXPECTED_NPZ_BYTES = 25166822
FROZEN_COUNTS_PATH = (
    "/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/"
    "nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P14-EMPIRICAL-GENIE-LEARNING-CURVE/"
    "empirical_genie_learning_curve_gate"
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

# One-sided 95% Student-t factor for df=31 (exactly 32 DEV blocks).
T_FACTOR_DF31_95 = 1.695518782
UCB_THRESHOLD = 0.01

CANDIDATE_LABEL = "TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_CANDIDATE"
NOT_CONFIRMED_LABEL = "TARGET_EMPIRICAL_GENIE_F13_N16384_TRAIN128_NOT_CONFIRMED"

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 1800.0
EXTERNAL_TIMEOUT_S = 1800
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
    "(np.random.default_rng(stream seed)), stream-major TRAIN order "
    "(seed ascending, then block index ascending), no global RNG"
)
TRUTH_BOUNDARY = (
    "Alice truth enters only sampling and oracle-conditioned genie rows; "
    "it never enters an undisclosed operational metric, decision or "
    "candidate label; there is no operational decoder in this gate, hence "
    "no tag, no Toeplitz master and no disclosed values"
)
CONSTRUCTION_RULE = (
    "per TRAIN block accumulate h_i=-log2 p_i[U_i], e_i=1-max p_i into "
    "running sums; at each nested prefix boundary B=8/16/32/64/128 pool "
    "means, order worst-first by accepted (e,h,index); "
    "K_total=floor((1.3*N*(H1+H2)-64)/5) clipped to [0,2N] (3399 frozen); "
    "all feasible (K1,K2) enumerated, lexicographic minimum of "
    "(TRAIN residual e sum, K1, K2); every block decoded once per layer "
    "(320 planned genie calls); all five frozen before the first DEV block"
)
RESIDUAL_SCOPE = (
    "genie union-bound construction proxy: R_B sums undisclosed-coordinate "
    "genie error risks under prefix-B orders; it is not operational FER, "
    "not a real-channel result and not proof of any minimum N or TRAIN size"
)

INTEGRITY_GATE_ORDER = (
    "target_population_contract",
    "one_n_cell_complete",
    "nested_prefixes_exact",
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
    "learning_curve_constructions.json",
    "per_block_genie_residuals.jsonl",
    "aggregate_summary.json",
    "report.md",
)

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
    "ulimit -v 2097152\n"
    "timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_learning_curve "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --floor 1e-15 --target-f 1.3 "
    "--n 16384 "
    "--train-seeds 2026091930 2026091931 2026091932 2026091933 "
    "2026091934 2026091935 2026091936 2026091937 "
    "--train-blocks-per-stream 16 --prefix-blocks 8 16 32 64 128 "
    "--dev-seeds 2026091940 2026091941 2026091942 2026091943 "
    "--dev-blocks-per-stream 8 --chunk-rows 512 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)
CLAIM_SCOPE = (
    "frozen V25 TRAIN target-population empirical-genie learning-curve "
    "diagnostic at N=16384 only; not held-out or real frame FER, "
    "efficiency, key rate, scaling, qualification or promotion; other "
    "prefixes diagnose learning only; P13 B=8 is a historical reference, "
    "never merged and never required equal; undetected has no meaning in "
    "this tag-free gate and no success bucket exists"
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
    "FROZEN_N",
    "FROZEN_TRAIN_SEEDS",
    "FROZEN_DEV_SEEDS",
    "FROZEN_TRAIN_BLOCKS_PER_STREAM",
    "FROZEN_DEV_BLOCKS_PER_STREAM",
    "FROZEN_TRAIN_BLOCKS",
    "FROZEN_DEV_BLOCKS",
    "FROZEN_PREFIX_BLOCKS",
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
    "T_FACTOR_DF31_95",
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
    "EmpiricalGenieLearningCurveResourceError",
    "paired_diff_stats",
    "construction_report_only",
    "run_empirical_genie_learning_curve",
    "build_parser",
    "main",
]


class EmpiricalGenieLearningCurveResourceError(RuntimeError):
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


def _none_stats(count: int) -> dict:
    return {
        "n": int(count),
        "mean": None,
        "std_sample": None,
        "min": None,
        "max": None,
        "ucb_95_t31": None,
    }


def paired_diff_stats(values) -> dict:
    """Mean/sample-std/range/one-sided t-UCB of paired DEV differences.

    The frozen gate always holds exactly 32 DEV blocks (df=31, factor
    ``1.695518782``); any other sample count returns the same descriptive
    statistics with ``ucb_95_t31`` set to ``None`` (test-seam behaviour
    only, never the frozen run). Pure: no SC call, no RNG, no I/O.
    """
    return student_t_ucb_95(values)


def _freeze_construction(b: int, used: int, split: dict, e1m, h1m, e2m, h2m,
                         k_total: int, leakage: int, f_value: float) -> dict:
    cell = {
        "b": int(b),
        "train_blocks_used": int(used),
        "k_total": int(k_total),
        "k1": int(split["k1"]),
        "k2": int(split["k2"]),
        "train_residual": float(split["residual"]),
        "leakage_bits": int(leakage),
        "f": float(f_value),
        "l1_order": [int(v) for v in np.asarray(split["l1_order"]).tolist()],
        "l2_order": [int(v) for v in np.asarray(split["l2_order"]).tolist()],
        "pooled_e1_mean": [float(v) for v in np.asarray(e1m, dtype=np.float64).tolist()],
        "pooled_h1_mean": [float(v) for v in np.asarray(h1m, dtype=np.float64).tolist()],
        "pooled_e2_mean": [float(v) for v in np.asarray(e2m, dtype=np.float64).tolist()],
        "pooled_h2_mean": [float(v) for v in np.asarray(h2m, dtype=np.float64).tolist()],
    }
    cell["freeze_sha256"] = hashlib.sha256(
        json.dumps(
            {k: cell[k] for k in (
                "b", "k_total", "k1", "k2", "l1_order", "l2_order",
                "pooled_e1_mean", "pooled_h1_mean",
                "pooled_e2_mean", "pooled_h2_mean",
            )},
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return cell


def construction_report_only(constructions: dict) -> dict:
    """Report-only learning diagnostics across the five frozen prefixes.

    Pairwise order Spearman/top-K overlap of each prefix against B=128
    (top-K at the frozen B=128 layer allocation), allocation movement,
    and per-prefix improved/tied/regressed counts against R_8 are
    computed from persisted constructions and DEV records only: no SC
    call, no RNG, no selection. ``dev_r`` maps ``"8"``/``"16"``/... to
    equal-length DEV residual lists (empty mapping allowed for partial
    checkpoints, in which case counts are zero).
    """
    ref = constructions.get("128")
    spearman: dict[str, dict] = {}
    overlap: dict[str, dict] = {}
    if ref is not None:
        for tag in ("8", "16", "32", "64"):
            cell = constructions.get(tag)
            if cell is None:
                continue
            spearman[tag] = {
                "l1": float(spearman_rank_corr(
                    _position_rank(cell["l1_order"]), _position_rank(ref["l1_order"]))),
                "l2": float(spearman_rank_corr(
                    _position_rank(cell["l2_order"]), _position_rank(ref["l2_order"]))),
            }
            entry: dict[str, object] = {"k1": int(ref["k1"]), "k2": int(ref["k2"])}
            for layer, key in (("l1", "k1"), ("l2", "k2")):
                depth = int(ref[key])
                if 1 <= depth <= FROZEN_N:
                    entry[layer] = float(topk_overlap(
                        cell[f"{layer}_order"], ref[f"{layer}_order"], depth))
                else:
                    entry[layer] = None
            overlap[tag] = entry
    movement = [
        {"b": int(tag), "k1": int(constructions[tag]["k1"]),
         "k2": int(constructions[tag]["k2"])}
        for tag in ("8", "16", "32", "64", "128") if tag in constructions
    ]
    return {
        "spearman_vs_128": spearman,
        "topk_overlap_vs_128": overlap,
        "allocation_movement": movement,
    }


def _vs_r8_counts(dev_r: dict) -> dict:
    """Per-prefix improved/tied/regressed counts against R_8 (report-only)."""
    out: dict[str, dict] = {}
    base = np.asarray(dev_r.get("8", []), dtype=np.float64)
    for tag in ("8", "16", "32", "64", "128"):
        vals = np.asarray(dev_r.get(tag, []), dtype=np.float64)
        if vals.shape != base.shape or vals.size == 0:
            out[tag] = {"improved": 0, "tied": 0, "regressed": 0}
            continue
        out[tag] = {
            "improved": int(np.sum(vals < base)),
            "tied": int(np.sum(vals == base)),
            "regressed": int(np.sum(vals > base)),
        }
    return out


@dataclass(frozen=True, eq=False)
class EmpiricalGenieLearningCurveRun:
    """In-memory P14 gate run (also returned by the runner)."""

    records: list
    constructions: dict
    plan: dict
    summary: dict


def _stub_plan(*, out_path, source, floor, target_f, n, train_list, dev_list,
               train_bps, dev_bps, prefix_list, chunk_rows) -> dict:
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
        "n": int(n),
        "train_seeds": [int(s) for s in train_list],
        "dev_seeds": [int(s) for s in dev_list],
        "train_blocks_per_stream": int(train_bps),
        "dev_blocks_per_stream": int(dev_bps),
        "train_blocks_total": int(len(train_list) * int(train_bps)),
        "dev_blocks_total": int(len(dev_list) * int(dev_bps)),
        "prefix_blocks": [int(b) for b in prefix_list],
        "planned_genie_calls": int(PLANNED_GENIE_CALLS),
        "frozen_k_total_from_literals": int(
            budget_k_total(int(n), EXPECTED_H1 + EXPECTED_H2, FROZEN_TARGET_F)),
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
            "prefix": 128,
            "ucb_threshold": UCB_THRESHOLD,
            "t_factor_df31_95": T_FACTOR_DF31_95,
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
        "# NB-Polar Phase 4-P14 empirical-genie learning curve gate",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- source/target: `{summary['source']}`; q={summary['q']}, n={summary['n']}, "
        f"target_f={summary['target_f']}, chunk_rows={summary['chunk_rows']}",
        f"- TRAIN streams x blocks: {len(summary['train_seeds'])}x"
        f"{summary['train_blocks_per_stream']} = {summary['train_blocks_total']}; "
        f"DEV: {len(summary['dev_seeds'])}x{summary['dev_blocks_per_stream']} = "
        f"{summary['dev_blocks_total']}; prefixes: {summary['prefix_blocks']}",
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
        "## Per-prefix construction and DEV genie residuals (proxy, not FER)",
        "",
        "| B | K1 | K2 | TRAIN residual | mean | std | min | max | UCB |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for tag in ("8", "16", "32", "64", "128"):
        row = summary["dev"]["per_prefix"].get(tag)
        con = summary["constructions"].get(tag)
        if row is None or con is None:
            lines.append(f"| {tag} | pending | pending | pending | pending |")
            continue
        lines.append(
            f"| {tag} | {con['k1']} | {con['k2']} | {con['train_residual']!r} | "
            f"{row.get('mean')!r} | {row.get('std_sample')!r} | "
            f"{row.get('min')!r} | {row.get('max')!r} | {row.get('ucb_95_t31')!r} |"
        )
    lines += [
        "",
        "## Paired differences (mean/std/UCB, report-only except the B=128 rule)",
        "",
        "| contrast | mean | std | UCB |",
        "|---|---|---|---|",
    ]
    for name in ("R_16_minus_R_8", "R_32_minus_R_8", "R_64_minus_R_8", "R_128_minus_R_8"):
        row = summary["dev"]["paired_vs_8"].get(name)
        if row is None:
            lines.append(f"| {name} | pending | pending | pending |")
        else:
            lines.append(
                f"| {name} | {row.get('mean')!r} | {row.get('std_sample')!r} | "
                f"{row.get('ucb_95_t31')!r} |"
            )
    for name in ("R_16_minus_R_8_step", "R_32_minus_R_16_step",
                 "R_64_minus_R_32_step", "R_128_minus_R_64_step"):
        row = summary["dev"]["adjacent"].get(name)
        if row is None:
            lines.append(f"| {name} | pending | pending | pending |")
        else:
            lines.append(
                f"| {name} | {row.get('mean')!r} | {row.get('std_sample')!r} | "
                f"{row.get('ucb_95_t31')!r} |"
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
        "",
        f"**Scope:** {summary['claim_scope']}.",
        "",
    ]
    return "\n".join(lines)


def run_empirical_genie_learning_curve(
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
    prefix_blocks=FROZEN_PREFIX_BLOCKS,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_entropies=None,
) -> EmpiricalGenieLearningCurveRun:
    """Execute the frozen P14 empirical-genie learning-curve gate; write five files.

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
    n = _as_int(n, "n", minimum=1)
    if n != FROZEN_N:
        raise ValueError(f"frozen point requires n={FROZEN_N}, got {n}")
    prefix_list = [_as_int(b, "prefix-blocks entry", minimum=1) for b in prefix_blocks]
    if prefix_list != list(FROZEN_PREFIX_BLOCKS):
        raise ValueError(
            "frozen point requires prefix-blocks "
            f"{list(FROZEN_PREFIX_BLOCKS)}, got {prefix_list}"
        )
    train_list = [_as_int(s, "train seed", minimum=0) for s in train_seeds]
    dev_list = [_as_int(s, "dev seed", minimum=0) for s in dev_seeds]
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
    if len(set(train_list)) != len(train_list):
        raise ValueError("train stream seeds must be distinct")
    if len(set(dev_list)) != len(dev_list):
        raise ValueError("dev stream seeds must be distinct")
    if not set(train_list).isdisjoint(dev_list):
        raise ValueError("TRAIN and DEV stream seeds must be disjoint")
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
    cap = float(total_wall_s)
    if not np.isfinite(cap) or cap <= 0:
        raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")

    plan = _stub_plan(
        out_path=out_path, source=source, floor=floor, target_f=target_f,
        n=n, train_list=train_list, dev_list=dev_list,
        train_bps=train_bps, dev_bps=dev_bps, prefix_list=prefix_list,
        chunk_rows=chunk_rows,
    )

    # ---- create all five files BEFORE the content open (stub inventory).
    out_path.mkdir(parents=True)
    constructions: dict[str, dict] = {}
    try:
        _write_json(out_path / "frozen_plan.json", plan)
        _write_json(
            out_path / "learning_curve_constructions.json",
            {"protocol": PROTOCOL_NAME, "status": "pending_content_open",
             "n": int(n), "prefixes": constructions},
        )
        (out_path / "per_block_genie_residuals.jsonl").write_text("", encoding="utf-8")
        _write_json(
            out_path / "aggregate_summary.json",
            {"protocol": PROTOCOL_NAME, "status": "pending_content_open"},
        )
        (out_path / "report.md").write_text(
            "# NB-Polar Phase 4-P14 empirical-genie learning curve gate\n\n"
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
        k_total = budget_k_total(n, h_total, target_f)
        leakage = 5 * k_total + 64
        budget_bits = float(target_f) * int(n) * h_total
        if not leakage <= budget_bits:
            raise TargetPopulationContractError(
                f"BLOCKED(budget_allocation_reproduced): N={n} leakage {leakage} "
                f"exceeds f-budget {budget_bits!r}"
            )
        f_value = float(leakage / (int(n) * h_total))
        train_blocks_done = 0
        dev_records: list[dict] = []
        dev_r: dict[str, list] = {str(b): [] for b in prefix_list}
        provenance_violations = 0
        resource_stop: str | None = None
        acc_l1 = _empty_acc(n)
        acc_l2 = _empty_acc(n)

        def checkpoint(summary_doc: dict) -> None:
            _write_json(
                out_path / "learning_curve_constructions.json",
                {
                    "protocol": PROTOCOL_NAME,
                    "n": int(n),
                    "k_total": int(k_total),
                    "frozen_before_first_dev": bool(len(constructions) == len(prefix_list)),
                    "prefixes": {tag: dict(cell) for tag, cell in constructions.items()},
                },
            )
            _write_json(out_path / "aggregate_summary.json", summary_doc)
            (out_path / "report.md").write_text(_render_report(summary_doc), encoding="utf-8")

        def running_dev_stats() -> dict:
            return {
                str(b): (student_t_ucb_95(dev_r[str(b)])
                         if len(dev_r[str(b)]) >= 2 else _none_stats(len(dev_r[str(b)])))
                for b in prefix_list
            }

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
                "n": int(n),
                "target_f": float(target_f),
                "chunk_rows": int(chunk_rows),
                "train_seeds": [int(s) for s in train_list],
                "dev_seeds": [int(s) for s in dev_list],
                "train_blocks_per_stream": int(train_bps),
                "dev_blocks_per_stream": int(dev_bps),
                "train_blocks_total": int(len(train_list) * int(train_bps)),
                "dev_blocks_total": int(len(dev_list) * int(dev_bps)),
                "prefix_blocks": [int(b) for b in prefix_list],
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
                "k_total": int(k_total),
                "leakage_bits": int(leakage),
                "f": float(f_value),
                "constructions": {tag: {
                    "b": cell["b"], "train_blocks_used": cell["train_blocks_used"],
                    "k1": cell["k1"], "k2": cell["k2"],
                    "train_residual": cell["train_residual"],
                    "freeze_sha256": cell["freeze_sha256"],
                } for tag, cell in constructions.items()},
                "dev": {
                    "blocks": int(len(dev_records)),
                    "per_prefix": running_dev_stats(),
                    "paired_vs_8": {},
                    "adjacent": {},
                    "report_only": {},
                },
                "dev_block_count": int(len(dev_records)),
                "train_blocks_done": int(train_blocks_done),
                "genie_calls": int(calls["genie"]),
                "planned_genie_calls": int(PLANNED_GENIE_CALLS),
                "provenance_violations": int(provenance_violations),
                "integrity": {name: bool(gates.get(name, False)) for name in INTEGRITY_GATE_ORDER},
                "integrity_all_pass": bool(all(gates.get(name, False) for name in INTEGRITY_GATE_ORDER)),
                "failing_integrity_gates": list(failing),
                "outcome_label": outcome_label,
                "wall_s": round(float(time.perf_counter() - start), 6),
                "rss_bytes_peak": _peak_rss_bytes(),
                "resources": _cell_resource_record(time.perf_counter() - start),
                "resource_stop_fired": bool(resource_stop is not None),
                "resource_stop_reason": resource_stop,
                "attempt_read_accounting": dict(accounting),
                "claim_scope": CLAIM_SCOPE,
            }

        def live_gates() -> dict:
            return _integrity_gates(
                out_path=out_path,
                train_list=train_list, dev_list=dev_list,
                prefix_list=prefix_list,
                constructions=constructions, dev_records=dev_records,
                dev_r=dev_r, calls=calls, accounting=accounting,
                provenance_violations=provenance_violations,
                start=start, cap=cap, resource_stop=resource_stop,
                counts_shape=counts_arr.shape,
                precondition_passed=bool(precondition_report.passed),
                train_used_l1=int(acc_l1["used"]), train_used_l2=int(acc_l2["used"]),
                train_impossible=int(acc_l1["impossible"] + acc_l2["impossible"]),
                k_total=int(k_total), final=False,
            )

        # ---- TRAIN: single stream-major pass; running sums serve every prefix.
        prefix_set = set(int(b) for b in prefix_list)
        for seed in train_list:
            rng = np.random.default_rng(int(seed))
            for _ in range(int(train_bps)):
                reason = _budget_exceeded(start, cap)
                if reason is not None:
                    resource_stop = reason
                    raise EmpiricalGenieLearningCurveResourceError(
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
                if int(acc_l1["used"]) in prefix_set and str(int(acc_l1["used"])) not in constructions:
                    used = int(acc_l1["used"])
                    e1m = acc_l1["e"] / used
                    h1m = acc_l1["h"] / used
                    e2m = acc_l2["e"] / used
                    h2m = acc_l2["h"] / used
                    split = select_empirical_split(n, e1m, h1m, e2m, h2m, k_total)
                    constructions[str(used)] = _freeze_construction(
                        used, used, split, e1m, h1m, e2m, h2m,
                        k_total, leakage, f_value,
                    )
                gates_now = live_gates()
                failing_now = [g for g in INTEGRITY_GATE_ORDER if not gates_now[g]]
                checkpoint(partial_summary(f"TRAIN({train_blocks_done})", gates_now, failing_now))

        # ---- every construction frozen before the first DEV genie call.
        if len(constructions) != len(prefix_list):
            raise TargetPopulationContractError(
                "BLOCKED(nested_prefixes_exact): frozen prefixes "
                f"{sorted(constructions)} != {[int(b) for b in prefix_list]}"
            )
        frozen_arms = {
            str(b): {
                "l1_order": np.asarray(constructions[str(b)]["l1_order"], dtype=np.int64),
                "l2_order": np.asarray(constructions[str(b)]["l2_order"], dtype=np.int64),
                "k1": int(constructions[str(b)]["k1"]),
                "k2": int(constructions[str(b)]["k2"]),
            }
            for b in prefix_list
        }

        # ---- DEV: one decode per block; its genie rows score all five prefixes.
        for seed in dev_list:
            rng = np.random.default_rng(int(seed))
            for block_index in range(int(dev_bps)):
                reason = _budget_exceeded(start, cap)
                if reason is not None:
                    resource_stop = reason
                    raise EmpiricalGenieLearningCurveResourceError(
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
                    record = {
                        "n": int(n),
                        "stream_seed": int(seed),
                        "block_index": int(block_index),
                        "error": None,
                    }
                    for b in prefix_list:
                        arm = frozen_arms[str(int(b))]
                        record[f"r_{int(b)}"] = residual_for_orders(
                            risks["e1"], risks["e2"],
                            arm["l1_order"], arm["l2_order"], arm["k1"], arm["k2"],
                        )
                except MemoryError:
                    raise
                except Exception as exc:  # block failure: recorded, gate fails
                    record = {
                        "n": int(n),
                        "stream_seed": int(seed),
                        "block_index": int(block_index),
                        **{f"r_{int(b)}": None for b in prefix_list},
                        "error": type(exc).__name__,
                    }
                dev_records.append(record)
                _append_jsonl(out_path / "per_block_genie_residuals.jsonl", record)
                if record["error"] is None:
                    for b in prefix_list:
                        dev_r[str(int(b))].append(float(record[f"r_{int(b)}"]))
                gates_now = live_gates()
                failing_now = [g for g in INTEGRITY_GATE_ORDER if not gates_now[g]]
                checkpoint(partial_summary(f"RUNNING({len(dev_records)})", gates_now, failing_now))

        # ---- aggregates, classification and final gates.
        wall_s = time.perf_counter() - start
        rss_peak = _peak_rss_bytes()
        per_prefix = {
            str(b): (student_t_ucb_95(dev_r[str(b)])
                     if len(dev_r[str(b)]) >= 2 else _none_stats(len(dev_r[str(b)])))
            for b in prefix_list
        }
        base = np.asarray(dev_r["8"], dtype=np.float64)
        paired_vs_8 = {}
        for b in (16, 32, 64, 128):
            vals = np.asarray(dev_r[str(b)], dtype=np.float64)
            diff = (vals - base).tolist() if vals.shape == base.shape and vals.size >= 2 else []
            paired_vs_8[f"R_{b}_minus_R_8"] = (
                paired_diff_stats(diff) if len(diff) >= 2 else _none_stats(len(diff)))
        adjacent = {}
        for lo, hi in ((8, 16), (16, 32), (32, 64), (64, 128)):
            upper = np.asarray(dev_r[str(hi)], dtype=np.float64)
            lower = np.asarray(dev_r[str(lo)], dtype=np.float64)
            diff = ((upper - lower).tolist()
                    if upper.shape == lower.shape and upper.size >= 2 else [])
            adjacent[f"R_{hi}_minus_R_{lo}_step"] = (
                paired_diff_stats(diff) if len(diff) >= 2 else _none_stats(len(diff)))
        report_only = construction_report_only(constructions)
        report_only["vs_r8_counts"] = _vs_r8_counts(dev_r)
        gates = _integrity_gates(
            out_path=out_path,
            train_list=train_list, dev_list=dev_list,
            prefix_list=prefix_list,
            constructions=constructions, dev_records=dev_records,
            dev_r=dev_r, calls=calls, accounting=accounting,
            provenance_violations=provenance_violations,
            start=start, cap=cap, resource_stop=resource_stop,
            counts_shape=counts_arr.shape,
            precondition_passed=bool(precondition_report.passed),
            train_used_l1=int(acc_l1["used"]), train_used_l2=int(acc_l2["used"]),
            train_impossible=int(acc_l1["impossible"] + acc_l2["impossible"]),
            k_total=int(k_total), final=True,
        )
        failing = [g for g in INTEGRITY_GATE_ORDER if not gates[g]]
        ucb_128 = per_prefix["128"].get("ucb_95_t31")
        if all(gates[g] for g in INTEGRITY_GATE_ORDER):
            outcome = (CANDIDATE_LABEL
                       if ucb_128 is not None and ucb_128 <= UCB_THRESHOLD
                       else NOT_CONFIRMED_LABEL)
        else:
            outcome = f"BLOCKED({failing[0]})" if failing else "BLOCKED(unknown)"
        summary = partial_summary(outcome, gates, failing)
        summary["dev"] = {
            "blocks": int(len(dev_records)),
            "per_prefix": per_prefix,
            "paired_vs_8": paired_vs_8,
            "adjacent": adjacent,
            "report_only": report_only,
        }
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        checkpoint(summary)
        return EmpiricalGenieLearningCurveRun(
            records=dev_records,
            constructions={
                "protocol": PROTOCOL_NAME,
                "n": int(n),
                "k_total": int(k_total),
                "frozen_before_first_dev": True,
                "prefixes": {tag: dict(cell) for tag, cell in constructions.items()},
            },
            plan=plan,
            summary=summary,
        )
    except EmpiricalGenieLearningCurveResourceError:
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
                "# NB-Polar Phase 4-P14 empirical-genie learning curve gate\n\n"
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
                "# NB-Polar Phase 4-P14 empirical-genie learning curve gate\n\n"
                "outcome label: `BLOCKED(resource_limits_met_and_no_abort)`\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        raise EmpiricalGenieLearningCurveResourceError(
            f"BLOCKED(resource_limits_met_and_no_abort): MemoryError: {exc}"
        ) from exc


def _integrity_gates(
    *,
    out_path: Path,
    train_list,
    dev_list,
    prefix_list,
    constructions: dict,
    dev_records: list,
    dev_r: dict,
    calls: dict,
    accounting: dict,
    provenance_violations: int,
    start: float,
    cap: float,
    resource_stop,
    counts_shape,
    precondition_passed: bool,
    train_used_l1: int,
    train_used_l2: int,
    train_impossible: int,
    k_total: int,
    final: bool,
) -> dict:
    frozen_shape = bool(
        [int(s) for s in train_list] == list(FROZEN_TRAIN_SEEDS)
        and [int(s) for s in dev_list] == list(FROZEN_DEV_SEEDS)
    )
    frozen_prefix = bool([int(b) for b in prefix_list] == list(FROZEN_PREFIX_BLOCKS))

    if final:
        cells_ok = bool(
            int(train_used_l1) == FROZEN_TRAIN_BLOCKS
            and int(train_used_l2) == FROZEN_TRAIN_BLOCKS
            and len(dev_records) == FROZEN_DEV_BLOCKS
            and sum(1 for record in dev_records if record.get("error") is not None) == 0
        )
    else:
        cells_ok = True
    if final:
        nested_ok = bool(
            frozen_prefix
            and set(constructions) == {str(int(b)) for b in FROZEN_PREFIX_BLOCKS}
            and all(int(constructions[str(int(b))]["train_blocks_used"]) == int(b)
                    for b in FROZEN_PREFIX_BLOCKS)
        )
    else:
        nested_ok = bool(
            frozen_prefix
            and set(constructions) <= {str(int(b)) for b in FROZEN_PREFIX_BLOCKS}
            and all(int(constructions[tag]["train_blocks_used"]) == int(tag)
                    for tag in constructions)
        )
    streams_ok = bool(
        set(int(s) for s in train_list).isdisjoint(int(s) for s in dev_list)
        and len(set(int(s) for s in train_list)) == len(train_list)
        and len(set(int(s) for s in dev_list)) == len(dev_list)
        and frozen_shape
    )

    # Valid orders: every frozen prefix order is a permutation; freeze SHA
    # recomputed from the persisted construction matches.
    orders_ok = bool(constructions) if not final else bool(
        constructions and set(constructions) == {str(int(b)) for b in FROZEN_PREFIX_BLOCKS})
    for tag, cell in constructions.items():
        if not (_order_is_permutation(cell.get("l1_order"), FROZEN_N)
                and _order_is_permutation(cell.get("l2_order"), FROZEN_N)):
            orders_ok = False
            break
        recomputed = hashlib.sha256(
            json.dumps(
                {k: cell[k] for k in (
                    "b", "k_total", "k1", "k2", "l1_order", "l2_order",
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
    replay_ok = bool(constructions)
    if final:
        replay_ok = bool(
            constructions
            and set(constructions) == {str(int(b)) for b in FROZEN_PREFIX_BLOCKS})
    for tag, cell in constructions.items():
        try:
            expected_k = budget_k_total(
                FROZEN_N, EXPECTED_H1 + EXPECTED_H2, FROZEN_TARGET_F)
            replay = select_empirical_split(
                FROZEN_N,
                np.asarray(cell["pooled_e1_mean"]),
                np.asarray(cell["pooled_h1_mean"]),
                np.asarray(cell["pooled_e2_mean"]),
                np.asarray(cell["pooled_h2_mean"]),
                expected_k,
            )
            leakage = 5 * expected_k + 64
            budget = float(FROZEN_TARGET_F) * FROZEN_N * (EXPECTED_H1 + EXPECTED_H2)
        except (ValueError, TypeError):
            replay_ok = False
            break
        if not (
            int(cell["k_total"]) == int(expected_k)
            and int(cell["k_total"]) == int(k_total)
            and int(cell["k1"]) == int(replay["k1"])
            and int(cell["k2"]) == int(replay["k2"])
            and abs(float(cell["train_residual"]) - float(replay["residual"])) <= 1e-9
            and [int(v) for v in cell["l1_order"]] == [int(v) for v in replay["l1_order"].tolist()]
            and [int(v) for v in cell["l2_order"]] == [int(v) for v in replay["l2_order"].tolist()]
            and int(leakage) <= budget
        ):
            replay_ok = False
            break

    finite_ok = bool(constructions)
    for tag, cell in constructions.items():
        for key in ("pooled_e1_mean", "pooled_h1_mean", "pooled_e2_mean", "pooled_h2_mean"):
            arr = np.asarray(cell.get(key, []), dtype=np.float64)
            if not (arr.size and np.isfinite(arr).all()
                    and np.isfinite(float(cell.get("train_residual", np.nan)))):
                finite_ok = False
                break
        if not finite_ok:
            break
    if finite_ok:
        for record in dev_records:
            if record.get("error") is not None:
                finite_ok = False
                break
            if not all(np.isfinite(float(record[f"r_{int(b)}"])) for b in prefix_list):
                finite_ok = False
                break

    block_errors = sum(1 for record in dev_records if record.get("error") is not None)
    zero_exceptions = bool(int(train_impossible) == 0 and block_errors == 0
                           and (bool(constructions) or not final))

    truth_ok = bool(int(provenance_violations) == 0)
    if final:
        calls_ok = bool(int(calls.get("genie", 0)) == int(PLANNED_GENIE_CALLS))
    else:
        calls_ok = bool(int(calls.get("genie", 0)) <= int(PLANNED_GENIE_CALLS))
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
        "one_n_cell_complete": bool(cells_ok),
        "nested_prefixes_exact": bool(nested_ok),
        "streams_disjoint_frozen": bool(streams_ok),
        "orders_valid_frozen_before_dev": bool(orders_ok),
        "budget_allocation_reproduced": bool(replay_ok),
        "risks_finite": bool(finite_ok),
        "zero_genie_exceptions": bool(zero_exceptions),
        "truth_isolation": bool(truth_ok),
        "no_unregistered_calls": bool(calls_ok),
        "checkpoint_accounting_consistent": bool(files_ok and accounting_exact),
        "attempt_read_accounting_exact": bool(accounting_exact),
        "resource_limits_met_and_no_abort": bool(resource_ok),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p14-empirical-genie-learning-curve",
        description=(
            "NB-Polar Phase 4-P14 empirical-genie construction learning-curve "
            "development gate (frozen V25 1M TRAIN counts, N=16384)"
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
    parser.add_argument("--prefix-blocks", required=True, type=int, nargs="+",
                        dest="prefix_blocks")
    parser.add_argument("--chunk-rows", required=True, type=int, dest="chunk_rows")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_empirical_genie_learning_curve(
            counts_path=args.counts,
            source=args.source,
            floor=args.floor,
            target_f=args.target_f,
            n=args.n,
            train_seeds=args.train_seeds,
            dev_seeds=args.dev_seeds,
            train_blocks_per_stream=args.train_blocks_per_stream,
            dev_blocks_per_stream=args.dev_blocks_per_stream,
            prefix_blocks=args.prefix_blocks,
            chunk_rows=args.chunk_rows,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p14 empirical genie learning curve refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "dev_block_count": summary["dev_block_count"],
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
