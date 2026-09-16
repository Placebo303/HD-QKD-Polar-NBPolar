"""NB-Polar Phase 4-P12 target-population f=1.3 N-scaling profile.

Frozen point (packet ``NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE``,
OpenSpec ``formal-ir-nbpolar-phase4-p0`` P12 delta): measure whether
target-model recovery improves with N when every point is held to the actual
leakage budget ``f <= 1.3``.  This is a development profile, not
qualification or an empirical-order scaling claim.

Frozen semantics:

- Input: one call to the accepted ``load_v25_channel_counts(path)``; a
  stat-only size check of exactly ``25,166,822`` bytes happens before the
  content open, and the single artifact read plus the single scientific
  attempt are consumed at the first NPZ content open (never reopened, never
  retried; a module-level reopen guard refuses a second NPZ-mode call).
- Support rule (the only one, exactly P7): column-normalize the raw counts,
  replace every cell below ``1e-15`` by ``1e-15``, renormalize each Bob
  column; ``p_b`` from the column totals; accepted ``derive_p1`` /
  ``derive_p2`` under the packing ``A = 32*U1 + U2``.  No lambda, backoff,
  tuning, floor scan or held-out fitting.
- Preconditions before any SC call: no zero Bob column; ``p_b`` and
  conditional column error ``<= 1e-12``; raw-MLE in-sample population
  ``H1``/``H2``/total within ``1e-12`` of the V49 1M TRAIN literals; the
  floor-induced total-entropy change relative to the raw MLE table
  ``<= 1e-9``.  Failure is ``BLOCKED(target_population_contract)`` with
  zero SC calls and no output root (consumption already spent: the refusal
  happens after the content open, so it is recorded in the stderr message
  and the freeze doc, never in an output file).
- Budget: per N, ``K_total = floor((1.3*N*(H1+H2)-64)/5)`` clipped to
  ``[0, 2N]`` with the entire budget used, hence
  ``leakage = 5*K_total + 64 <= 1.3*N*H`` (asserted at allocation time).
- Construction: N-specific analytic BEC reliabilities (float64
  ``z- = 2z-z^2``, ``z+ = z^2`` from ``epsilon_l = H_l/5`` via the accepted
  ``analytic_erasure_probs``), stable descending orders with coordinate
  index tie-break via the accepted ``analytic_order``; every feasible
  integer ``K1`` (``K2 = K_total - K1``) enumerated and the lexicographic
  minimum of (sum of undisclosed L1+L2 reliabilities, K1, K2) selected.
  All K/order/residual values are frozen before the first SC call.  These
  are analytic BEC orders; the P7 N=256 empirical order is never reused or
  extrapolated.
- Execution matrix (exactly 128 blocks): N/seeds/blocks = 256/2026091820/64,
  4096/2026091821/32, 16384/2026091822/16, 65536/2026091823/8,
  131072/2026091824/4, 262144/2026091825/4.  Master = seed + 10000,
  domain-separated by P12/N/layer/block.  Per block: ``B ~ p_b`` then
  ``A ~ P_floor(A|B)`` sampled once; L1; candidate-conditioned L2; label
  rebuild; exactly one 64-bit Toeplitz tag.  No comparator, oracle,
  adaptive retry or repeated block.  Every SC call runs through the
  accepted ``sc_decode`` whose ``_minus_block`` production default is
  exactly ``chunk_rows=512`` (verified by contract check; the CLI value
  must equal 512).
- Buckets (``exact``/``verify_failed``/``decode_failed``/``undetected``/
  ``resource_abort``) are mutually exclusive and exhaustive; ``undetected``
  is never success.  Alice truth enters only sampling, disclosed values,
  tag construction and scoring.  A fully invoked block discloses exactly
  ``5*(K1+K2)+64`` key-dependent bits and ``seed_bits_for(N)`` public
  control bits per invoked tag, with an independent literal recount;
  partial failure counts only actually disclosed bits.
- Outputs: exactly five scalar-only files (public orders plus scalar
  outcomes; never sampled symbols, decoded keys, metrics, raw counts or
  raw tag seeds).  Per N: K/residual/leakage/f and tag-free f; full bucket
  counts; exact fraction and the two-sided 95% Clopper-Pearson interval;
  wall/RSS; key/public/tag accounting with the literal recount.
- Hard gates are integrity/completion only (no recovery threshold; large-N
  samples are too small for qualification).  All true returns
  ``TARGET_F13_N_SCALING_PROFILE_CANDIDATE``; otherwise the earliest
  ``BLOCKED(<gate>)``.  Recovery trend and first success are report-only.

No Model-F/held-out/raw/real frame, no other N in the frozen run, no
FWHT/APP/SCL, no FER/efficiency/key-rate qualification or promotion, no
commit.  The claim scope is a development signal for the frozen V25 TRAIN
target population only.
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
from .sc import NumericNonfiniteError, sc_decode
from .synthetic import analytic_erasure_probs
from .target_construction import (
    PRECONDITION_ORDER,
    TargetPopulationContractError,
    classify_outcome,
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

PROTOCOL_NAME = "nbpolar-p12-target-f13-n-scaling-profile"
MODE = "target-population-f13-n-scaling-profile"

Q = 32
ALPHA = 2
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
FROZEN_N_VALUES = (256, 4096, 16384, 65536, 131072, 262144)
FROZEN_STREAM_SEEDS = (2026091820, 2026091821, 2026091822, 2026091823, 2026091824, 2026091825)
FROZEN_BLOCKS = (64, 32, 16, 8, 4, 4)
FROZEN_TOTAL_BLOCKS = 128
PUBLIC_TAG_MASTER_OFFSET = 10000
FROZEN_CHUNK_ROWS = 512

EXPECTED_NPZ_BYTES = 25166822
FROZEN_COUNTS_PATH = (
    "/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/"
    "nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P12-TARGET-F13-N-SCALING-PROFILE/"
    "target_f13_n_scaling"
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

CP_ALPHA = 0.05  # two-sided 95% Clopper-Pearson interval

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 1800.0
EXTERNAL_TIMEOUT_S = 1800
ULIMIT_VIRTUAL_KIB = 2097152

ARM = "profile"
LAYERS = ("l1", "l2")
CANDIDATE_LABEL = "TARGET_F13_N_SCALING_PROFILE_CANDIDATE"

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
    "column); high=A//32, low=A%32; one explicit stream RNG per N "
    "(np.random.default_rng(stream seed)), blocks sequential, no global RNG"
)
TRUTH_BOUNDARY = (
    "Alice truth enters only sampling, disclosed values, tag construction and "
    "scoring; it never enters an undisclosed operational metric, decision or "
    "candidate label; each layer restarts SC with no state transfer"
)
BEC_RULE = (
    "N-specific analytic BEC reliabilities (float64 z-=2z-z^2, z+=z^2 from "
    "epsilon_l=H_l/5 via analytic_erasure_probs); stable descending orders "
    "with coordinate index tie-break via analytic_order; never the P7 "
    "empirical orders"
)
BUDGET_RULE = (
    "K_total=floor((1.3*N*(H1+H2)-64)/5) clipped to [0,2N], entire budget "
    "used, leakage=5*K_total+64 <= 1.3*N*H asserted; every feasible integer "
    "K1 (K2=K_total-K1) enumerated, lexicographic minimum of (undisclosed "
    "L1+L2 reliability sum, K1, K2); frozen before the first SC call"
)

OUTCOME_PRECEDENCE = [
    "resource_abort: block not executed (preregistered budget stop)",
    "decode_failed: L1 or L2 SC exception / nonfinite marginals; no tag",
    "verify_failed: tag mismatch",
    "exact: tag pass and label == true label",
    "undetected: tag pass and not exact (never success)",
]

PRECONDITION_GATE = "target_population_contract"
INTEGRITY_GATE_ORDER = (
    "target_population_contract",
    "six_n_rows_and_128_blocks",
    "budget_allocation_orders_reproduced",
    "coverage_complete",
    "buckets_disjoint_exhaustive",
    "truth_leak_zero",
    "disclosure_and_recount_exact",
    "attempt_read_accounting_exact",
    "resource_limits_met_and_no_abort",
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "allocation_and_orders.json",
    "per_block_outcomes.json",
    "aggregate_summary.json",
    "report.md",
)

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "ulimit -v 2097152\n"
    "timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.target_n_scaling "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --floor 1e-15 --target-f 1.3 "
    "--n-values 256 4096 16384 65536 131072 262144 "
    "--stream-seeds 2026091820 2026091821 2026091822 2026091823 2026091824 2026091825 "
    "--blocks 64 32 16 8 4 4 --chunk-rows 512 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)
CLAIM_SCOPE = (
    "frozen V25 TRAIN target-population f=1.3 N-scaling development signal "
    "only; not held-out or real frame FER, efficiency, key rate, scaling "
    "superiority, qualification or promotion; recovery trend and first "
    "success are report-only (no threshold); undetected is never success"
)
SEED_PREFIX = "nbpolar-p12-n-scaling-seed"
SEED_LAYER = "verify"  # the single verification-tag layer: exactly one tag per block

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
    "FROZEN_STREAM_SEEDS",
    "FROZEN_BLOCKS",
    "FROZEN_TOTAL_BLOCKS",
    "PUBLIC_TAG_MASTER_OFFSET",
    "FROZEN_CHUNK_ROWS",
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
    "CP_ALPHA",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S",
    "ULIMIT_VIRTUAL_KIB",
    "ARM",
    "LAYERS",
    "CANDIDATE_LABEL",
    "ATTEMPT_CONSUMPTION_POINT",
    "ARTIFACT_READ_ACCOUNTING",
    "SUPPORT_RULE",
    "SAMPLING_RULE",
    "TRUTH_BOUNDARY",
    "BEC_RULE",
    "BUDGET_RULE",
    "OUTCOME_PRECEDENCE",
    "INTEGRITY_GATE_ORDER",
    "OUTPUT_FILES",
    "FROZEN_COMMAND",
    "CLAIM_SCOPE",
    "SeedPrefixError",
    "TargetNScalingResourceError",
    "ScaleArmResult",
    "ScaleBlockResult",
    "TargetNScalingRun",
    "budget_k_total",
    "allocate_layer_ks",
    "clopper_pearson_interval",
    "profile_seed_bits",
    "run_scale_arm",
    "block_events",
    "recount_events",
    "run_target_n_scaling",
    "build_parser",
    "main",
]


class SeedPrefixError(ValueError):
    """Internal misuse of an invalid N/block seed request (frozen prefix)."""


class TargetNScalingResourceError(RuntimeError):
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


def budget_k_total(n: int, h_total: float, target_f: float = FROZEN_TARGET_F) -> int:
    """Frozen f-budget: ``floor((target_f*N*H-64)/5)`` clipped to ``[0, 2N]``."""
    n = _check_power_of_two(n, "n")
    h_total = float(h_total)
    if not np.isfinite(h_total) or h_total < 0.0:
        raise ValueError(f"h_total must be finite and non-negative, got {h_total!r}")
    target_f = _check_target_f(target_f)
    raw = int(math.floor((float(target_f) * int(n) * h_total - 64.0) / 5.0))
    return max(0, min(2 * int(n), raw))


def allocate_layer_ks(
    n: int, h1: float, h2: float, k_total: int
) -> dict:
    """Enumerate every feasible ``K1`` and lexicographically minimize.

    Returns ``k1``, ``k2``, the minimized undisclosed-reliability ``residual``,
    the frozen ``l1_order``/``l2_order`` (worst-first, index tie-break), the
    ``eps1``/``eps2`` surrogates and the per-layer reliability vectors.
    Infeasible ``K1`` values (outside ``[max(0,K-N), min(N,K)]``) never
    compete; ties break toward smaller ``K1``, then smaller ``K2``.
    """
    n = _check_power_of_two(n, "n")
    k_total = _as_int(k_total, "k_total", minimum=0)
    if k_total > 2 * n:
        raise ValueError(f"k_total must lie in 0..{2 * n}, got {k_total}")
    eps1 = min(1.0, max(0.0, float(h1) / 5.0))
    eps2 = min(1.0, max(0.0, float(h2) / 5.0))
    z1 = np.asarray(analytic_erasure_probs(eps1, n), dtype=np.float64)
    z2 = np.asarray(analytic_erasure_probs(eps2, n), dtype=np.float64)
    l1_order = np.asarray(analytic_order(eps1, n), dtype=np.int64)
    l2_order = np.asarray(analytic_order(eps2, n), dtype=np.int64)
    disclosed1 = np.concatenate([[0.0], np.cumsum(z1[l1_order])])
    disclosed2 = np.concatenate([[0.0], np.cumsum(z2[l2_order])])
    total1, total2 = float(z1.sum()), float(z2.sum())
    lo, hi = max(0, k_total - n), min(n, k_total)
    best = None
    for k1 in range(lo, hi + 1):
        k2 = k_total - k1
        residual = (total1 - float(disclosed1[k1])) + (total2 - float(disclosed2[k2]))
        key = (residual, int(k1), int(k2))
        if best is None or key < best[0]:
            best = (key, int(k1), int(k2), float(residual))
    _, k1, k2, residual = best
    return {
        "k1": int(k1),
        "k2": int(k2),
        "k_total": int(k_total),
        "residual": float(residual),
        "eps1": float(eps1),
        "eps2": float(eps2),
        "l1_order": np.asarray(l1_order, dtype=np.int64),
        "l2_order": np.asarray(l2_order, dtype=np.int64),
        "z1": np.asarray(z1, dtype=np.float64),
        "z2": np.asarray(z2, dtype=np.float64),
    }


def _betacf(a: float, b: float, x: float) -> float:
    maxit, eps, fpmin = 200, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, maxit + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = c * d
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _betai(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta ``I_x(a, b)`` via continued fraction."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(a * math.log(x) + b * math.log1p(-x) - lbeta) * _betacf(a, b, x) / a
    return 1.0 - (
        math.exp(b * math.log1p(-x) + a * math.log(x) - lbeta) * _betacf(b, a, 1.0 - x) / b
    )


def _beta_ppf(p: float, a: float, b: float) -> float:
    if not 0.0 < p < 1.0:
        raise ValueError(f"p must lie in (0, 1), got {p!r}")
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _betai(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clopper_pearson_interval(exact: int, total: int, alpha: float = CP_ALPHA) -> tuple:
    """Two-sided ``1 - alpha`` Clopper-Pearson interval for a binomial proportion.

    Edges: ``exact == 0`` gives lower 0; ``exact == total`` gives upper 1;
    ``total == 0`` gives ``(0, 1)``.
    """
    exact = _as_int(exact, "exact", minimum=0)
    total = _as_int(total, "total", minimum=0)
    if exact > total:
        raise ValueError(f"exact {exact} must not exceed total {total}")
    alpha = float(alpha)
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must lie in (0, 1), got {alpha!r}")
    if total == 0:
        return (0.0, 1.0)
    lo = 0.0 if exact == 0 else _beta_ppf(alpha / 2.0, float(exact), float(total - exact + 1))
    hi = (
        1.0
        if exact == total
        else _beta_ppf(1.0 - alpha / 2.0, float(exact + 1), float(total - exact))
    )
    return (float(min(1.0, max(0.0, lo))), float(min(1.0, max(0.0, hi))))


def profile_seed_bits(
    master: int,
    n: int,
    block_index: int,
    *,
    bit_length: int | None = None,
) -> np.ndarray:
    """Deterministic public per-N/per-block Toeplitz seed (P12 domain)."""
    master_seed = _as_int(master, "master", minimum=0)
    n = _as_int(n, "n", minimum=1)
    index = _as_int(block_index, "block_index", minimum=0)
    length = seed_bits_for(n) if bit_length is None else _as_int(bit_length, "bit_length", minimum=1)
    prefix = f"{SEED_PREFIX}:{master_seed}:{int(n)}:{SEED_LAYER}:{int(index)}"
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
class ScaleArmResult:
    """One attempted scaling-profile block.  Arrays are in-memory only."""

    n: int
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


@dataclass(frozen=True, eq=False)
class ScaleBlockResult:
    """One executed scaling-profile block (single operational arm)."""

    n: int
    stream_seed: int
    block_index: int
    arm: ScaleArmResult
    block_wall_s: float


def _abort_arm(n: int, stream_seed: int, block_index: int, *, k1: int, k2: int) -> ScaleArmResult:
    return ScaleArmResult(
        n=int(n),
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


def run_scale_arm(
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
) -> ScaleArmResult:
    """One candidate-conditioned two-layer scaling arm on a single block.

    The operational path receives only Bob, the hard L1 candidate and the
    frozen disclosures; truth is used only for the disclosed ``U`` values,
    the tag construction and scoring.
    """
    n = _check_power_of_two(n, "n")
    stream_seed = _as_int(stream_seed, "stream_seed", minimum=0)
    block_index = _as_int(block_index, "block_index", minimum=0)
    k1 = _as_int(k1, "k1", minimum=0)
    k2 = _as_int(k2, "k2", minimum=0)
    if k1 > n or k2 > n:
        raise ValueError(f"k1/k2 must lie in 0..{n}, got k1={k1}, k2={k2}")
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
        seed = profile_seed_bits(master, n, block_index, bit_length=seed_bits_for(n))
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
    return ScaleArmResult(
        n=int(n),
        stream_seed=int(stream_seed),
        block_index=int(block_index),
        outcome=outcome,
        exact=bool(outcome == "exact"),
        label_match=bool(label_match),
        tag_pass=bool(tag_pass),
        l1_provenance=op_p1_metric.provenance.value if not l1_failed else None,
        l2_provenance=p2_metric.provenance.value if p2_metric is not None else None,
        l1_executed=bool(not l1_failed),
        l2_invoked=bool(l2_invoked),
        l1_decode_failed=bool(l1_failed),
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


def _arm_record(arm: ScaleArmResult) -> dict:
    """Compact scalar-only record; symbol/label arrays are never persisted."""
    return {
        "n": int(arm.n),
        "stream_seed": int(arm.stream_seed),
        "block_index": int(arm.block_index),
        "arm": ARM,
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


def _aborted_block_record(n: int, stream_seed: int, block_index: int, *, k1: int, k2: int) -> dict:
    return _arm_record(_abort_arm(n, stream_seed, block_index, k1=k1, k2=k2))


def _arm_record_consistent(arm: ScaleArmResult) -> bool:
    """Structural proof of one arm record under the frozen P12 rules."""
    n, k1, k2 = int(arm.n), int(arm.k1), int(arm.k2)
    if arm.outcome not in OUTCOMES:
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
    if arm.exact and arm.outcome != "exact":
        return False  # undetected is never success
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
    n: int,
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
        "frame_key": f"nbpolar-p12-n-scaling:{int(n)}:{int(stream_seed)}:{int(block_index)}",
        "method": "nbpolar_target_n_scaling",
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


def block_events(n: int, stream_seed: int, arm: ScaleArmResult) -> list:
    """Canonical public transcript events: L1, L2 (when invoked), final tag."""
    if arm.outcome == "resource_abort":
        return []
    k1, k2 = int(arm.k1), int(arm.k2)
    block_index = int(arm.block_index)
    events: list[dict] = []
    l1_id = f"block-{int(n)}-{block_index}-{ARM}-l1-disclosure"
    events.append(
        _event(
            n=n,
            stream_seed=stream_seed,
            block_index=block_index,
            event_id=l1_id,
            event_type="l1_disclosure",
            direction="alice_to_bob",
            parent_event_id=None,
            key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k1,
            public_control_bits=0,
            payload={},
        )
    )
    if arm.l2_invoked:
        l2_id = f"block-{int(n)}-{block_index}-{ARM}-l2-disclosure"
        events.append(
            _event(
                n=n,
                stream_seed=stream_seed,
                block_index=block_index,
                event_id=l2_id,
                event_type="l2_disclosure",
                direction="alice_to_bob",
                parent_event_id=l1_id,
                key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k2,
                public_control_bits=0,
                payload={},
            )
        )
        if arm.tag_invoked:
            events.append(
                _event(
                    n=n,
                    stream_seed=stream_seed,
                    block_index=block_index,
                    event_id=f"block-{int(n)}-{block_index}-{ARM}-verification",
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
    by_n: dict[str, dict] = {}
    event_types = {"l1_disclosure": 0, "l2_disclosure": 0, "verification_tag": 0}
    for event in events:
        parts = str(event["event_id"]).split("-")
        if len(parts) < 5 or parts[0] != "block" or parts[3] != ARM:
            raise ValueError(f"transcript event id is not N/arm-tagged: {event['event_id']!r}")
        n_tag = parts[1]
        slot = by_n.setdefault(
            n_tag,
            {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0},
        )
        key = int(event["key_dependent_bits"])
        public = int(event["public_control_bits"])
        totals["key_dependent_bits"] += key
        totals["public_control_bits"] += public
        slot["key_dependent_bits"] += key
        slot["public_control_bits"] += public
        event_type = str(event["event_type"])
        if event_type not in event_types:
            raise ValueError(f"transcript event type is not frozen: {event_type!r}")
        event_types[event_type] += 1
        if event_type == "verification_tag":
            totals["tag_invocations"] += 1
            slot["tag_invocations"] += 1
    return {
        "key_dependent_bits": totals["key_dependent_bits"],
        "public_control_bits": totals["public_control_bits"],
        "tag_invocations": totals["tag_invocations"],
        "event_types": dict(event_types),
        "by_n": {tag: dict(slot) for tag, slot in by_n.items()},
    }


def _transcript_mismatches(incremental, incremental_by_n, recount) -> list:
    fields = ("key_dependent_bits", "public_control_bits", "tag_invocations")
    mismatches = []
    for name in fields:
        if int(incremental[name]) != int(recount[name]):
            mismatches.append(f"total:{name}:{int(incremental[name])}!={int(recount[name])}")
    for n_tag, slot in incremental_by_n.items():
        for name in fields:
            left = int(slot[name])
            right = int(recount["by_n"].get(str(n_tag), {}).get(name, -1))
            if left != right:
                mismatches.append(f"n={n_tag}:{name}:{left}!={right}")
    return mismatches


@dataclass(frozen=True, eq=False)
class TargetNScalingRun:
    """In-memory P12 profile run (also returned by the runner)."""

    results: list
    records: list
    events: list
    allocation: dict
    plan: dict
    summary: dict


def run_target_n_scaling(
    *,
    counts=None,
    counts_path=FROZEN_COUNTS_PATH,
    source: str = FROZEN_SOURCE,
    floor=FROZEN_FLOOR,
    target_f: float = FROZEN_TARGET_F,
    n_values=FROZEN_N_VALUES,
    stream_seeds=FROZEN_STREAM_SEEDS,
    blocks=FROZEN_BLOCKS,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_entropies=None,
    tag_fn=None,
) -> TargetNScalingRun:
    """Execute the frozen P12 N-scaling profile and write exactly five files.

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
    n_list = [_check_power_of_two(v, "n-values entry") for v in n_values]
    seed_list = [_as_int(s, "stream seed", minimum=0) for s in stream_seeds]
    block_list = [_as_int(b, "blocks entry", minimum=1) for b in blocks]
    if not (len(n_list) == len(seed_list) == len(block_list)) or not n_list:
        raise ValueError("n-values, stream-seeds and blocks must be non-empty lists of equal length")
    if len(set(seed_list)) != len(seed_list):
        raise ValueError("stream seeds must be distinct")
    if len(set(n_list)) != len(n_list):
        raise ValueError("n-values must be distinct")
    cap = float(total_wall_s)
    if not np.isfinite(cap) or cap <= 0:
        raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")
    tag_fn = _check_tag_fn(tag_fn)

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

    # ---- freeze every per-N budget/allocation/order before the first SC call.
    allocation_rows: list[dict] = []
    for n, seed, n_blocks in zip(n_list, seed_list, block_list):
        k_total = budget_k_total(n, h_total, target_f)
        leakage = DISCLOSED_BITS_PER_COORDINATE * k_total + TAG_BITS
        budget_bits = float(target_f) * int(n) * h_total
        if not leakage <= budget_bits:
            raise TargetPopulationContractError(
                f"BLOCKED(budget_allocation_orders_reproduced): N={n} leakage {leakage} "
                f"exceeds f-budget {budget_bits!r}"
            )
        alloc = allocate_layer_ks(n, h1, h2, k_total)
        allocation_rows.append(
            {
                "n": int(n),
                "stream_seed": int(seed),
                "blocks": int(n_blocks),
                "master": int(seed) + PUBLIC_TAG_MASTER_OFFSET,
                "k_total": int(k_total),
                "k1": int(alloc["k1"]),
                "k2": int(alloc["k2"]),
                "residual": float(alloc["residual"]),
                "eps1": float(alloc["eps1"]),
                "eps2": float(alloc["eps2"]),
                "leakage_bits": int(leakage),
                "leakage_bits_no_tag": int(DISCLOSED_BITS_PER_COORDINATE * k_total),
                "nH_bits": float(int(n) * h_total),
                "f": float(leakage / (int(n) * h_total)),
                "f_no_tag": float(
                    (DISCLOSED_BITS_PER_COORDINATE * k_total) / (int(n) * h_total)
                ),
                "l1_order": [int(v) for v in alloc["l1_order"].tolist()],
                "l2_order": [int(v) for v in alloc["l2_order"].tolist()],
            }
        )
    allocation_frozen_sha = hashlib.sha256(
        json.dumps(
            [{k: row[k] for k in ("n", "k_total", "k1", "k2", "l1_order", "l2_order")}
             for row in allocation_rows],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    # ---- execution: one stream RNG per N, blocks sequential, single arm.
    results: list = []
    records: list = []
    events: list = []
    incremental = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    incremental_by_n = {
        str(int(row["n"])): {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
        for row in allocation_rows
    }
    resource_stop_fired = False
    stop_reason: str | None = None
    for row_pos, row in enumerate(allocation_rows):
        n, seed, n_blocks = row["n"], row["stream_seed"], row["blocks"]
        n_tag = str(n)
        rng = np.random.default_rng(int(seed))
        for block_index in range(int(n_blocks)):
            reason = _budget_exceeded(start, cap)
            if reason is not None:
                resource_stop_fired = True
                stop_reason = reason
                for rest in range(block_index, int(n_blocks)):
                    arm = _abort_arm(n, seed, rest, k1=row["k1"], k2=row["k2"])
                    results.append(
                        ScaleBlockResult(n=n, stream_seed=seed, block_index=rest, arm=arm, block_wall_s=0.0)
                    )
                    records.append(_arm_record(arm))
                for later in allocation_rows[row_pos + 1 :]:
                    for rest in range(int(later["blocks"])):
                        arm = _abort_arm(
                            later["n"], later["stream_seed"], rest,
                            k1=later["k1"], k2=later["k2"],
                        )
                        results.append(
                            ScaleBlockResult(
                                n=later["n"], stream_seed=later["stream_seed"],
                                block_index=rest, arm=arm, block_wall_s=0.0,
                            )
                        )
                        records.append(_arm_record(arm))
                break
            bob, _a_full, high, low = sample_target_block(
                rng, p_b=entropy.p_b, f_full=entropy.f, n=n
            )
            u1 = polar_transform(high, field=field, alpha=ALPHA)
            u2 = polar_transform(low, field=field, alpha=ALPHA)
            labels_true = (low + LABEL_SCALE * high).astype(np.int64)
            labels_true_bits = labels_to_bits(labels_true)
            block_start = time.perf_counter()
            arm = run_scale_arm(
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
                l1_order=np.asarray(row["l1_order"], dtype=np.int64),
                l2_order=np.asarray(row["l2_order"], dtype=np.int64),
                k1=row["k1"],
                k2=row["k2"],
                master=int(seed) + PUBLIC_TAG_MASTER_OFFSET,
                tag_fn=tag_fn,
            )
            results.append(
                ScaleBlockResult(
                    n=n, stream_seed=seed, block_index=block_index, arm=arm,
                    block_wall_s=time.perf_counter() - block_start,
                )
            )
            records.append(_arm_record(arm))
            events.extend(block_events(n, seed, arm))
            if arm.outcome != "resource_abort":
                incremental["key_dependent_bits"] += int(arm.key_dependent_bits)
                incremental["public_control_bits"] += int(arm.public_control_bits)
                incremental["tag_invocations"] += int(arm.tag_invoked)
                slot = incremental_by_n[n_tag]
                slot["key_dependent_bits"] += int(arm.key_dependent_bits)
                slot["public_control_bits"] += int(arm.public_control_bits)
                slot["tag_invocations"] += int(arm.tag_invoked)
        if resource_stop_fired:
            break
    wall_s = time.perf_counter() - start
    rss_peak = _peak_rss_bytes()

    # ---- allocation unchanged after execution (no adaptive repair).
    allocation_recomputed = hashlib.sha256(
        json.dumps(
            [{k: row[k] for k in ("n", "k_total", "k1", "k2", "l1_order", "l2_order")}
             for row in allocation_rows],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    allocation_unchanged = allocation_recomputed == allocation_frozen_sha

    recount = recount_events(events)
    mismatches = _transcript_mismatches(incremental, incremental_by_n, recount)
    gates = _integrity_gates(
        precondition_report=precondition_report,
        counts_shape=counts_arr.shape,
        n_list=n_list,
        seed_list=seed_list,
        block_list=block_list,
        allocation_rows=allocation_rows,
        allocation_unchanged=allocation_unchanged,
        results=results,
        records=records,
        incremental=incremental,
        incremental_by_n=incremental_by_n,
        recount=recount,
        mismatches=mismatches,
        accounting=accounting,
        wall_s=wall_s,
        rss_peak=rss_peak,
        resource_stop_fired=resource_stop_fired,
        target_f=float(target_f),
        h_total=h_total,
    )

    # ---- per-N aggregates with two-sided 95% Clopper-Pearson intervals.
    planned_total = int(sum(block_list))
    per_n: dict[str, dict] = {}
    for row in allocation_rows:
        n = row["n"]
        arms = [r.arm for r in results if int(r.n) == int(n)]
        buckets = {name: sum(1 for arm in arms if arm.outcome == name) for name in OUTCOMES}
        exact = int(buckets["exact"])
        total = int(len(arms))
        lo, hi = clopper_pearson_interval(exact, total, CP_ALPHA)
        per_n[str(n)] = {
            "n": int(n),
            "stream_seed": int(row["stream_seed"]),
            "planned_blocks": int(row["blocks"]),
            "attempted_blocks": int(total),
            "k_total": int(row["k_total"]),
            "k1": int(row["k1"]),
            "k2": int(row["k2"]),
            "residual": float(row["residual"]),
            "leakage_bits": int(row["leakage_bits"]),
            "leakage_bits_no_tag": int(row["leakage_bits_no_tag"]),
            "f": float(row["f"]),
            "f_no_tag": float(row["f_no_tag"]),
            "buckets": buckets,
            "exact": int(exact),
            "exact_fraction": float(exact / max(total, 1)),
            "clopper_pearson_95": {
                "alpha": float(CP_ALPHA),
                "two_sided": True,
                "lower": float(lo),
                "upper": float(hi),
            },
            "nonfinite": int(sum(1 for arm in arms if arm.nonfinite)),
            "truth_leak_violations": int(sum(1 for arm in arms if arm.truth_leak_violation)),
            "key_dependent_bits": int(sum(int(arm.key_dependent_bits) for arm in arms)),
            "public_control_bits": int(sum(int(arm.public_control_bits) for arm in arms)),
            "tag_invocations": int(sum(1 for arm in arms if arm.tag_invoked)),
            "recount": {
                name: int(recount["by_n"].get(str(n), {}).get(name, 0))
                for name in ("key_dependent_bits", "public_control_bits", "tag_invocations")
            },
            "wall_s": round(float(sum(r.block_wall_s for r in results if int(r.n) == int(n))), 6),
        }
    exact_total = int(sum(1 for r in results if r.arm.exact))
    first_success_n = None
    for row in allocation_rows:
        if int(per_n[str(row["n"])]["exact"]) > 0:
            first_success_n = int(row["n"])
            break
    integrity_all_pass = all(gates.values())
    failing_integrity = [name for name in INTEGRITY_GATE_ORDER if not gates[name]]
    shape_is_frozen = bool(
        list(n_list) == list(FROZEN_N_VALUES)
        and list(seed_list) == list(FROZEN_STREAM_SEEDS)
        and list(block_list) == list(FROZEN_BLOCKS)
    )
    outcome_label = (
        CANDIDATE_LABEL
        if integrity_all_pass
        else f"BLOCKED({failing_integrity[0]})" if failing_integrity else "BLOCKED(unknown)"
    )
    summary = {
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
        "stream_seeds": [int(s) for s in seed_list],
        "blocks": [int(b) for b in block_list],
        "planned_blocks": int(planned_total),
        "toeplitz_masters": [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in seed_list],
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
        "per_n": per_n,
        "recovery_report_only": {
            "exact_total": int(exact_total),
            "planned_total": int(planned_total),
            "first_success_n": first_success_n,
            "no_threshold": True,
            "note": (
                "descriptive only: recovery trend and first observed success "
                "carry no pass/fail threshold (large-N samples are too small "
                "for qualification)"
            ),
        },
        "integrity": {name: bool(gates[name]) for name in INTEGRITY_GATE_ORDER},
        "integrity_all_pass": integrity_all_pass,
        "failing_integrity_gates": failing_integrity,
        "outcome_label": outcome_label,
        "disclosure_accounting": {
            "disclosed_bits_per_coordinate": DISCLOSED_BITS_PER_COORDINATE,
            "tag_bits": TAG_BITS,
            "key_dependent_bits_total": int(incremental["key_dependent_bits"]),
            "public_control_bits_total": int(incremental["public_control_bits"]),
            "tag_invocations": int(incremental["tag_invocations"]),
            "incremental_by_n": {tag: dict(slot) for tag, slot in incremental_by_n.items()},
            "recount": {
                "key_dependent_bits": int(recount["key_dependent_bits"]),
                "public_control_bits": int(recount["public_control_bits"]),
                "tag_invocations": int(recount["tag_invocations"]),
                "event_types": dict(recount["event_types"]),
                "by_n": {tag: dict(slot) for tag, slot in recount["by_n"].items()},
            },
            "mismatch_count": int(len(mismatches)),
            "mismatches": list(mismatches),
        },
        "wall_s": round(float(wall_s), 6),
        "rss_bytes_peak": rss_peak,
        "resource_stop_fired": bool(resource_stop_fired),
        "resource_stop_reason": stop_reason,
        "attempt_read_accounting": dict(accounting),
        "allocation_frozen_sha256": allocation_frozen_sha,
        "allocation_unchanged_after_execution": bool(allocation_unchanged),
        "claim_scope": CLAIM_SCOPE,
    }
    plan = {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "created_utc": summary["created_utc"],
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "out_root": str(out_path),
        "source": source,
        "counts_path": accounting.get("counts_path"),
        "expected_npz_bytes": EXPECTED_NPZ_BYTES,
        "loader": LOADER_IDENTITY,
        "support_rule": SUPPORT_RULE,
        "sampling_rule": SAMPLING_RULE,
        "truth_boundary": TRUTH_BOUNDARY,
        "bec_rule": BEC_RULE,
        "budget_rule": BUDGET_RULE,
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
        "stream_seeds": [int(s) for s in seed_list],
        "blocks": [int(b) for b in block_list],
        "planned_blocks": int(planned_total),
        "toeplitz_masters": [int(s) + PUBLIC_TAG_MASTER_OFFSET for s in seed_list],
        "toeplitz": {
            "tag_bits": TAG_BITS,
            "seed_layer": SEED_LAYER,
            "derivation": (
                f"MSB-first unpack of SHA-256('{SEED_PREFIX}:<master>:<n>:"
                f"{SEED_LAYER}:<block>:<counter>') concatenated over "
                "counter=0,1,...; truncated to 10*n+63 bits; public control, "
                "never persisted raw"
            ),
        },
        "arms": [ARM],
        "outcome_buckets": list(OUTCOMES),
        "outcome_precedence": list(OUTCOME_PRECEDENCE),
        "clopper_pearson": {"alpha": float(CP_ALPHA), "two_sided": True},
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
        "labels": {
            "candidate": CANDIDATE_LABEL,
            "blocked": "BLOCKED(<earliest gate>)",
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
        "frozen_command": FROZEN_COMMAND,
        "claim_scope": CLAIM_SCOPE,
    }
    allocation_doc = {
        "protocol": PROTOCOL_NAME,
        "frozen_before_first_sc": True,
        "allocation_unchanged_after_execution": bool(allocation_unchanged),
        "allocation_sha256": allocation_frozen_sha,
        "rows": [
            {k: row[k] for k in (
                "n", "stream_seed", "blocks", "master", "k_total", "k1", "k2",
                "residual", "eps1", "eps2", "leakage_bits", "leakage_bits_no_tag",
                "nH_bits", "f", "f_no_tag", "l1_order", "l2_order",
            )}
            for row in allocation_rows
        ],
    }
    out_path.mkdir(parents=True)
    _write_json(out_path / "frozen_plan.json", plan)
    _write_json(out_path / "allocation_and_orders.json", allocation_doc)
    _write_json(
        out_path / "per_block_outcomes.json",
        {
            "planned_blocks": int(planned_total),
            "n_values": [int(v) for v in n_list],
            "stream_seeds": [int(s) for s in seed_list],
            "blocks": [int(b) for b in block_list],
            "n_blocks": len(records),
            "blocks_outcomes": records,
        },
    )
    _write_json(out_path / "aggregate_summary.json", summary)
    (out_path / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return TargetNScalingRun(
        results=results,
        records=records,
        events=events,
        allocation=allocation_doc,
        plan=plan,
        summary=summary,
    )


def _integrity_gates(
    *,
    precondition_report,
    counts_shape,
    n_list,
    seed_list,
    block_list,
    allocation_rows,
    allocation_unchanged: bool,
    results,
    records,
    incremental,
    incremental_by_n,
    recount,
    mismatches,
    accounting: dict,
    wall_s: float,
    rss_peak: int | None,
    resource_stop_fired: bool,
    target_f: float,
    h_total: float,
) -> dict:
    planned = int(sum(int(b) for b in block_list))
    arms = [r.arm for r in results]
    executed = [arm for arm in arms if arm.outcome != "resource_abort"]

    def count(outcome):
        return sum(1 for arm in arms if arm.outcome == outcome)

    l1_ok = sum(1 for arm in arms if arm.l1_executed)
    l1_fail = sum(1 for arm in arms if arm.l1_decode_failed)
    l2_inv = sum(1 for arm in arms if arm.l2_invoked)
    l2_skip = sum(1 for arm in arms if arm.l2_skipped_by_l1_failure)
    l2_fail = sum(1 for arm in arms if arm.l2_decode_failed)
    tag_inv = sum(1 for arm in arms if arm.tag_invoked)
    tag_outcomes = sum(count(name) for name in ("exact", "undetected", "verify_failed"))
    executed_n = len(executed)
    fully_invoked = [
        arm for arm in arms if arm.tag_invoked and arm.l2_invoked and arm.l1_executed
    ]
    alloc_by_n = {int(row["n"]): row for row in allocation_rows}
    fully_invoked_exact = all(
        int(arm.key_dependent_bits)
        == DISCLOSED_BITS_PER_COORDINATE * int(alloc_by_n[int(arm.n)]["k_total"]) + TAG_BITS
        for arm in fully_invoked
    )
    tags_accounted = all(
        int(arm.public_control_bits) == (seed_bits_for(int(arm.n)) if arm.tag_invoked else 0)
        for arm in arms
    )
    per_record_ok = all(_arm_record_consistent(arm) for arm in arms)
    buckets_ok = sum(count(name) for name in OUTCOMES) == len(results)
    sub_buckets_ok = (
        l1_ok + l1_fail == executed_n
        and l2_inv == l1_ok
        and l2_inv + l2_skip == executed_n
        and l2_fail <= l2_inv
        and tag_inv == tag_outcomes
    )
    totals_ok = (
        int(incremental["key_dependent_bits"]) == int(recount["key_dependent_bits"])
        and int(incremental["public_control_bits"]) == int(recount["public_control_bits"])
        and int(incremental["tag_invocations"]) == int(recount["tag_invocations"])
        and all(
            int(incremental_by_n[tag][name]) == int(recount["by_n"].get(str(tag), {}).get(name, -1))
            for tag in incremental_by_n
            for name in ("key_dependent_bits", "public_control_bits", "tag_invocations")
        )
    )
    shape_frozen = bool(
        list(int(v) for v in n_list) == list(FROZEN_N_VALUES)
        and list(int(s) for s in seed_list) == list(FROZEN_STREAM_SEEDS)
        and list(int(b) for b in block_list) == list(FROZEN_BLOCKS)
    )
    streams_ok = all(
        sum(1 for r in records if int(r["n"]) == int(n) and int(r["stream_seed"]) == int(seed))
        == int(n_blocks)
        for n, seed, n_blocks in zip(n_list, seed_list, block_list)
    )
    coverage = bool(
        len(results) == planned and len(records) == planned and streams_ok
    )
    # Independent reproduction of every budget/allocation/order from the literals.
    reproduced = bool(allocation_unchanged)
    if reproduced:
        for row in allocation_rows:
            n = int(row["n"])
            k_total = budget_k_total(n, EXPECTED_H1 + EXPECTED_H2, FROZEN_TARGET_F)
            alloc = allocate_layer_ks(n, EXPECTED_H1, EXPECTED_H2, k_total)
            leakage = DISCLOSED_BITS_PER_COORDINATE * k_total + TAG_BITS
            budget = float(FROZEN_TARGET_F) * int(n) * (EXPECTED_H1 + EXPECTED_H2)
            if not (
                int(row["k_total"]) == int(k_total)
                and int(row["k1"]) == int(alloc["k1"])
                and int(row["k2"]) == int(alloc["k2"])
                and [int(v) for v in row["l1_order"]] == [int(v) for v in alloc["l1_order"].tolist()]
                and [int(v) for v in row["l2_order"]] == [int(v) for v in alloc["l2_order"].tolist()]
                and abs(float(row["residual"]) - float(alloc["residual"])) <= 1e-9
                and int(row["leakage_bits"]) == int(leakage)
                and float(row["f"]) <= float(FROZEN_TARGET_F)
                and int(leakage) <= budget
            ):
                reproduced = False
                break
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
    gates = {
        "target_population_contract": bool(precondition_report.passed),
        "six_n_rows_and_128_blocks": bool(shape_frozen and planned == FROZEN_TOTAL_BLOCKS),
        "budget_allocation_orders_reproduced": bool(reproduced),
        "coverage_complete": bool(coverage),
        "buckets_disjoint_exhaustive": bool(buckets_ok and sub_buckets_ok and per_record_ok),
        "truth_leak_zero": not any(arm.truth_leak_violation for arm in arms),
        "disclosure_and_recount_exact": bool(
            fully_invoked_exact
            and tags_accounted
            and totals_ok
            and not mismatches
            and recount["event_types"].get("l1_disclosure", 0) == executed_n
            and recount["event_types"].get("l2_disclosure", 0) == l2_inv
            and recount["event_types"].get("verification_tag", 0) == tag_inv
        ),
        "attempt_read_accounting_exact": accounting_exact,
        "resource_limits_met_and_no_abort": bool(
            count("resource_abort") == 0
            and not resource_stop_fired
            and float(wall_s) <= TOTAL_WALL_S
            and (rss_peak is None or int(rss_peak) <= RSS_LIMIT_BYTES)
        ),
    }
    return gates


def _render_report(summary: dict) -> str:
    integrity = summary["integrity"]
    accounting = summary["disclosure_accounting"]
    entropy = summary["entropy"]
    recovery = summary["recovery_report_only"]
    lines = [
        "# NB-Polar Phase 4-P12 target-population f=1.3 N-scaling profile",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- source/target: `{summary['source']}`; q={summary['q']}, "
        f"target_f={summary['target_f']}, chunk_rows={summary['chunk_rows']}",
        f"- N values: {summary['n_values']}; streams: {summary['stream_seeds']}; "
        f"blocks: {summary['blocks']} = {summary['planned_blocks']} planned blocks",
        f"- wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes; "
        f"resource stop fired: {summary['resource_stop_fired']}",
        "",
        "## Target population contract",
        "",
        f"- H1: {entropy['h1']!r} (expected {entropy['expected_h1']!r})",
        f"- H2: {entropy['h2']!r} (expected {entropy['expected_h2']!r})",
        f"- total: {entropy['total']!r} (expected {entropy['expected_total']!r})",
        f"- floored-table total: {entropy['floor_total']!r}; floor-induced change: "
        f"{entropy['floor_entropy_change']!r}",
        f"- column deviation: {entropy['column_dev']!r}; p_b sum: {entropy['p_b_sum']!r}",
        "",
        "## Per-N profile (report-only recovery)",
        "",
        "| N | K_total | K1 | K2 | residual | leakage | f | f_no_tag | "
        "exact | fraction | CP95 lo | CP95 hi | wall_s |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for tag in (str(v) for v in summary["n_values"]):
        row = summary["per_n"][tag]
        cp = row["clopper_pearson_95"]
        lines.append(
            f"| {row['n']} | {row['k_total']} | {row['k1']} | {row['k2']} | "
            f"{row['residual']!r} | {row['leakage_bits']} | {row['f']!r} | "
            f"{row['f_no_tag']!r} | {row['exact']}/{row['attempted_blocks']} | "
            f"{row['exact_fraction']!r} | {cp['lower']!r} | {cp['upper']!r} | "
            f"{row['wall_s']} |"
        )
    lines += [
        "",
        "## Per-N buckets",
        "",
        "| N | exact | verify_failed | decode_failed | undetected | resource_abort | "
        "nonfinite |",
        "|---|---|---|---|---|---|---|",
    ]
    for tag in (str(v) for v in summary["n_values"]):
        row = summary["per_n"][tag]
        buckets = row["buckets"]
        lines.append(
            f"| {row['n']} | {buckets['exact']} | {buckets['verify_failed']} | "
            f"{buckets['decode_failed']} | {buckets['undetected']} | "
            f"{buckets['resource_abort']} | {row['nonfinite']} |"
        )
    lines += [
        "",
        f"- recovery (report-only, no threshold): exact total "
        f"{recovery['exact_total']}/{recovery['planned_total']}; first success N: "
        f"{recovery['first_success_n']}",
        "",
        "## Integrity gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in integrity.items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        "## Disclosure accounting",
        "",
        f"- key-dependent total: {accounting['key_dependent_bits_total']}; public total: "
        f"{accounting['public_control_bits_total']}; tags: {accounting['tag_invocations']}",
        f"- recount mismatch count: {accounting['mismatch_count']}",
        "",
        f"- outcome label: `{summary['outcome_label']}`",
        "",
        f"**Scope:** {summary['claim_scope']}.",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p12-target-n-scaling",
        description=(
            "NB-Polar Phase 4-P12 target-population f=1.3 N-scaling development "
            "profile (frozen V25 1M TRAIN counts)"
        ),
    )
    parser.add_argument("--counts", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--floor", required=True, type=float)
    parser.add_argument("--target-f", required=True, type=float, dest="target_f")
    parser.add_argument("--n-values", required=True, type=int, nargs="+", dest="n_values")
    parser.add_argument("--stream-seeds", required=True, type=int, nargs="+", dest="stream_seeds")
    parser.add_argument("--blocks", required=True, type=int, nargs="+", dest="blocks")
    parser.add_argument("--chunk-rows", required=True, type=int, dest="chunk_rows")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_target_n_scaling(
            counts_path=args.counts,
            source=args.source,
            floor=args.floor,
            target_f=args.target_f,
            n_values=args.n_values,
            stream_seeds=args.stream_seeds,
            blocks=args.blocks,
            chunk_rows=args.chunk_rows,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p12 target n-scaling refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "planned_blocks": summary["planned_blocks"],
                "per_n_exact": {
                    tag: row["exact"] for tag, row in summary["per_n"].items()
                },
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
