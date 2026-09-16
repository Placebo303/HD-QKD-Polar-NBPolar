"""Phase 4-P3 diagnostic entrypoint: synthetic now, one artifact run later.

Synthetic mode (Stage A/A2, no artifact read) builds injected asymmetric
tables with a frozen caller seed, samples model blocks through
``empirical_channel``, compares the vectorized gather against the
literal reference, runs reference SC, and -- on tiny domains only --
checks every SC conditional against ``empirical_oracle``.

Artifact mode (legacy minimal payload) and Stage B mode both load the
single accepted CAL artifact once via ``prior_artifact``. Stage B
(``--mode stageb``) is the frozen P3 diagnostic: one artifact load, the
frozen B1-B5 case matrix, per-case soft stop and total wall guard, and
exactly five compact output files written at the end. It MUST NOT run
before independent Pre-EXECUTE PASS; ordinary tests only exercise the
injected-table seam ``_run_stageb_from_tables`` and the refusal paths
with nonexistent temporary paths, never the sibling root.

Frozen-argument discipline: every scientific parameter is an explicit
required argument (no defaults to production paths); an existing
``--out`` root is never overwritten; banned predecessor seeds
(2026091200..1213) are refused. No I/O at import, no global RNG.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from numbers import Integral
from pathlib import Path

import numpy as np

from .empirical_channel import (
    BANNED_SEEDS,
    P3_DIAG_SEED,
    P3_TRAIN_SEED,
    P3_UNIT_SEED,
    build_p1_metrics,
    build_p1_metrics_literal,
    make_rng,
    sample_bob,
    sample_high_given_bob,
)

__all__ = [
    "BANNED_SEEDS",
    "P3_UNIT_SEED",
    "P3_TRAIN_SEED",
    "P3_DIAG_SEED",
    "STAGEB_SEED",
    "STAGEB_SOFT_CAP_S",
    "STAGEB_TOTAL_CAP_S",
    "STAGEB_B1_N",
    "STAGEB_B1_BLOCKS",
    "STAGEB_B2_N",
    "STAGEB_B2_BLOCKS",
    "STAGEB_B3_N",
    "STAGEB_B3_BLOCKS",
    "STAGEB_B4_N",
    "STAGEB_B4_REPS",
    "STAGEB_MASK_NAMES",
    "STAGEB_ATTRIBUTION_CATEGORIES",
    "STAGEB_OUT_FILES",
    "stageb_masks",
    "classify_stageb_failure",
    "run_stageb_diagnostic",
    "run_synthetic_diagnostic",
    "run_artifact_diagnostic",
    "build_parser",
    "main",
]


def _probs_to_log(probs) -> np.ndarray:
    """Generic prob-row to log-row conversion (any ``q``).

    Same semantics as the accepted ``prior.probs_to_symbol_metric``
    (``0 -> -inf``, rows to ``logsumexp 0``), which pins ``q=32``;
    Stage A tests prove bitwise parity at ``q=32`` (P3-A14), so artifact
    mode converts identically to the accepted helper.
    """
    mat = np.asarray(probs, dtype=np.float64)
    with np.errstate(divide="ignore"):
        logp = np.log(mat, out=np.full_like(mat, -np.inf), where=mat > 0)
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(logp, axis=1, keepdims=True)
    return logp - lse


def _check_out(out) -> Path:
    outp = Path(out)
    if outp.exists():
        raise FileExistsError(f"refuse to overwrite existing out dir: {outp}")
    return outp


def _check_positive_int(value, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"diagnostic contract: {name} must be an integer")
    value = int(value)
    if value < 1:
        raise ValueError(f"diagnostic contract: {name} must be >= 1")
    return value


def _median_seconds(fn, reps: int = 5) -> float:
    fn()  # warm-up, never measured
    spans = []
    for _ in range(reps):
        start = time.perf_counter()
        fn()
        spans.append(time.perf_counter() - start)
    return float(np.median(np.asarray(spans, dtype=np.float64)))


def _peak_rss_gib():
    """Peak RSS in GiB; ``ru_maxrss`` is KiB on Linux and bytes on macOS."""
    try:
        import resource

        raw = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        scale = 1024.0**3 if sys.platform == "darwin" else 1024.0**2
        return raw / scale
    except Exception:
        return None


def _injected_tables(rng, q: int, n_b: int):
    """Asymmetric injected ``(p_b, p1)``: dense columns, one sparse column."""
    raw_b = rng.random(n_b) + 0.2
    p_b = (raw_b / raw_b.sum()).astype(np.float64)
    raw = rng.random((q, n_b)) + 0.1
    raw[:, -1] = 0.0
    raw[0, -1] = 1.0  # deterministic sparse column keeps exact-zero support
    p1 = (raw / raw.sum(axis=0, keepdims=True)).astype(np.float64)
    return p_b, p1


def _field_for_q(q: int):
    from .algebra import make_gf2m, make_gf32

    if int(q) == 4:
        return make_gf2m(2, 7)
    if int(q) == 32:
        return make_gf32()
    raise ValueError(f"diagnostic contract: q must be 4 or 32, got {q}")


def run_synthetic_diagnostic(*, q: int, n: int, n_b: int, seed: int,
                             n_blocks: int, out) -> dict:
    """Run the synthetic tiny/block diagnostic into a fresh ``out`` dir."""
    from .empirical_oracle import MAX_ORACLE_CANDIDATES, empirical_oracle_sc_metric
    from .sc import sc_decode
    from .transform import polar_transform

    if int(q) not in (4, 32):
        raise ValueError(f"diagnostic contract: q must be 4 or 32, got {q}")
    if int(n) < 1 or (int(n) & (int(n) - 1)):
        raise ValueError(f"diagnostic contract: n must be a positive power of two, got {n}")
    n_b = _check_positive_int(n_b, "n_b")
    n_blocks = _check_positive_int(n_blocks, "n_blocks")
    outp = _check_out(out)
    rng = make_rng(seed)  # refuses banned predecessor streams
    q, n = int(q), int(n)

    p_b, p1 = _injected_tables(rng, q, n_b)
    field = _field_for_q(q)

    max_prob_err = 0.0
    max_log_err = 0.0
    support_mismatches = 0
    oracle_rows = 0
    n_exact = 0
    tiny = q**n <= MAX_ORACLE_CANDIDATES
    for _ in range(n_blocks):
        bob = sample_bob(rng, p_b, n)
        truth = sample_high_given_bob(rng, bob, p1)
        probs = build_p1_metrics(bob, p1)
        ref = build_p1_metrics_literal(bob, p1)
        max_prob_err = max(max_prob_err, float(np.abs(probs - ref).max()))
        support_mismatches += int(
            np.sum(np.isfinite(probs) != np.isfinite(ref))
        )
        logp = _probs_to_log(probs)
        res = sc_decode(logp, field=field, alpha=2)
        u_true = polar_transform(truth, field=field, alpha=2)
        if np.array_equal(res.u_hat, u_true):
            n_exact += 1
        if tiny:
            for i in range(n):
                ora = empirical_oracle_sc_metric(logp, res.u_hat[:i].tolist(),
                                                 field=field, alpha=2)
                prod = res.decision_metrics[i]
                max_prob_err = max(
                    max_prob_err, float(np.abs(np.exp(prod) - np.exp(ora)).max()))
                both = np.isfinite(prod) & np.isfinite(ora)
                if np.any(both):
                    max_log_err = max(
                        max_log_err, float(np.abs(prod[both] - ora[both]).max()))
                support_mismatches += int(np.sum(np.isfinite(prod) != np.isfinite(ora)))
                oracle_rows += 1

    bob_batch = sample_bob(rng, p_b, n * 4).reshape(4, n)
    metric_med = _median_seconds(lambda: build_p1_metrics(bob_batch, p1))
    probe = build_p1_metrics(sample_bob(rng, p_b, n), p1)
    probe_log = _probs_to_log(probe)
    decode_med = _median_seconds(
        lambda: sc_decode(probe_log, field=field, alpha=2))
    rss = _peak_rss_gib()
    payload = {
        "entry": "empirical_synthetic_diagnostic",
        "q": q,
        "n": n,
        "n_b": n_b,
        "seed": int(seed),
        "n_blocks": n_blocks,
        "tiny_oracle": bool(tiny),
        "oracle_rows": oracle_rows,
        "max_prob_err": max_prob_err,
        "max_log_err": max_log_err,
        "support_mismatches": support_mismatches,
        "n_exact": n_exact,
        "metric_median_s": metric_med,
        "decode_median_s": decode_med,
        "peak_rss_gib": rss,
        "metric_shape": [4, n, q],
    }
    outp.mkdir(parents=True, exist_ok=False)
    (outp / "synthetic_summary.json").write_text(json.dumps(payload, indent=2))
    (outp / "report.md").write_text(
        "# P3 synthetic diagnostic (no artifact)\n\n"
        f"q={q} n={n} n_b={n_b} seed={seed} blocks={n_blocks}\n\n"
        f"tiny_oracle={tiny} rows={oracle_rows} "
        f"max_prob_err={max_prob_err:.3e} max_log_err={max_log_err:.3e} "
        f"support_mismatches={support_mismatches} n_exact={n_exact}\n\n"
        f"metric_median_s={metric_med:.6f} decode_median_s={decode_med:.6f} "
        f"peak_rss_gib={rss}\n"
    )
    return payload


def run_artifact_diagnostic(*, npz_path, summary_path, seed: int,
                            n: int, n_blocks: int, out) -> dict:
    """Stage B artifact diagnostic (requires Pre-EXECUTE PASS; not Stage A)."""
    from .prior import derive_p1, smooth_joint_to_conditional
    from .prior_artifact import LAMBDA_STAR, load_prior_artifact

    outp = _check_out(out)
    n_blocks = _check_positive_int(n_blocks, "n_blocks")
    if int(n) < 1 or (int(n) & (int(n) - 1)):
        raise ValueError(f"diagnostic contract: n must be a positive power of two, got {n}")
    rng = make_rng(seed)  # refuses banned streams before any artifact open
    artifact = load_prior_artifact(npz_path, summary_path)
    f_table = smooth_joint_to_conditional(artifact.counts_ab, LAMBDA_STAR)
    p1 = derive_p1(f_table)
    p_b = np.asarray(artifact.p_b, dtype=np.float64)
    payload = run_synthetic_payload_from_tables(
        rng=rng, p_b=p_b, p1=p1, q=32, n=int(n), seed=int(seed),
        n_blocks=n_blocks, outp=outp,
    )
    return payload


def run_synthetic_payload_from_tables(*, rng, p_b, p1, q: int, n: int,
                                      seed: int, n_blocks: int, outp: Path) -> dict:
    """Shared measurement core writing the Stage B compact file set."""
    from .empirical_oracle import MAX_ORACLE_CANDIDATES, empirical_oracle_sc_metric
    from .sc import sc_decode
    from .transform import polar_transform

    field = _field_for_q(q)
    tiny = q**n <= MAX_ORACLE_CANDIDATES
    oracle_rows = 0
    max_prob_err = 0.0
    max_log_err = 0.0
    support_mismatches = 0
    n_exact = 0
    for _ in range(n_blocks):
        bob = sample_bob(rng, p_b, n)
        truth = sample_high_given_bob(rng, bob, p1)
        probs = build_p1_metrics(bob, p1)
        logp = _probs_to_log(probs)
        res = sc_decode(logp, field=field, alpha=2)
        if np.array_equal(res.u_hat, polar_transform(truth, field=field, alpha=2)):
            n_exact += 1
        if tiny:
            for i in range(n):
                ora = empirical_oracle_sc_metric(logp, res.u_hat[:i].tolist(),
                                                 field=field, alpha=2)
                prod = res.decision_metrics[i]
                max_prob_err = max(
                    max_prob_err, float(np.abs(np.exp(prod) - np.exp(ora)).max()))
                both = np.isfinite(prod) & np.isfinite(ora)
                if np.any(both):
                    max_log_err = max(
                        max_log_err, float(np.abs(prod[both] - ora[both]).max()))
                support_mismatches += int(np.sum(np.isfinite(prod) != np.isfinite(ora)))
                oracle_rows += 1
    bob_batch = sample_bob(rng, p_b, n * 4).reshape(4, n)
    metric_med = _median_seconds(lambda: build_p1_metrics(bob_batch, p1))
    probe = build_p1_metrics(sample_bob(rng, p_b, n), p1)
    probe_log = _probs_to_log(probe)
    decode_med = _median_seconds(lambda: sc_decode(probe_log, field=field, alpha=2))
    rss = _peak_rss_gib()
    frozen = {"q": q, "n": n, "seed": seed, "n_blocks": n_blocks,
              "tiny_oracle": bool(tiny)}
    oracle_records = {"rows": oracle_rows, "max_prob_err": max_prob_err,
                      "max_log_err": max_log_err,
                      "support_mismatches": support_mismatches}
    stress = {"metric_median_s": metric_med, "decode_median_s": decode_med,
              "peak_rss_gib": rss, "metric_shape": [4, n, q]}
    summary = {"n_exact": n_exact, "n_blocks": n_blocks, **oracle_records}
    outp.mkdir(parents=True, exist_ok=False)
    (outp / "frozen_plan.json").write_text(json.dumps(frozen, indent=2))
    (outp / "oracle_records.json").write_text(json.dumps(oracle_records, indent=2))
    (outp / "stress_and_profile.json").write_text(json.dumps(stress, indent=2))
    (outp / "diagnostic_summary.json").write_text(json.dumps(summary, indent=2))
    (outp / "report.md").write_text(
        "# P3 artifact diagnostic summary\n\n" + json.dumps(summary, indent=2) + "\n"
    )
    return summary


# --- Stage B: frozen accepted-artifact model-sampled diagnostic -------------
#
# Frozen case matrix (TASK_PACKET Stage B + round freeze; do not widen):
#   B1  GF32 N=2 and N=4, 64 model-sampled blocks each, no disclosure,
#       every SC conditional vs the vectorized exhaustive oracle.
#   B2  N=16 and N=64, masks M1-M5 x 16 blocks each.
#   B3  N=256, masks M1-M5 x 8 blocks each (40 total), no oracle.
#   B4  N=64/256/1024 metric-only and decode-only timing, 1 warm-up +
#       5 measured calls, median.
#   B5  earliest-layer attribution of every non-exact executed block.
#
# Attribution precedence, per non-exact executed block (matches
# ``classify_stageb_failure`` exactly): artifact_adapter_support >
# normalization > disclosure_contradiction > SC_numeric > unattributed
# (unclassified decoder exceptions; frozen crash=0) >
# expected_under_disclosure (finite non-exact with an undisclosed MAP
# mismatch) > SC_decision (remaining finite non-exact blocks).
# Resource soft-stop blocks are recorded as ``resource_abort`` and are
# never merged into exact counts or attribution-as-failure.

STAGEB_SEED = P3_DIAG_SEED  # frozen 2026091316
STAGEB_SOFT_CAP_S = 120.0  # per-case soft stop (seconds)
STAGEB_TOTAL_CAP_S = 3600.0  # whole-run guard (seconds)
STAGEB_RSS_LIMIT_BYTES = 2147483648  # 2 GiB envelope, recorded in the plan
STAGEB_PROB_TOL = 1e-12
STAGEB_LOG_TOL = 1e-9
STAGEB_B1_N = (2, 4)
STAGEB_B1_BLOCKS = 64
STAGEB_B2_N = (16, 64)
STAGEB_B2_BLOCKS = 16
STAGEB_B3_N = 256
STAGEB_B3_BLOCKS = 8
STAGEB_B4_N = (64, 256, 1024)
STAGEB_B4_REPS = 5
STAGEB_MASK_NAMES = (
    "M1_all_but_one",
    "M2_prefix",
    "M3_suffix",
    "M4_alternating",
    "M5_construction_order",
)
STAGEB_ATTRIBUTION_CATEGORIES = (
    "artifact_adapter_support",
    "normalization",
    "disclosure_contradiction",
    "SC_numeric",
    "SC_decision",
    "expected_under_disclosure",
    "unattributed",
)
STAGEB_OUT_FILES = (
    "frozen_plan.json",
    "oracle_records.json",
    "stress_and_profile.json",
    "diagnostic_summary.json",
    "report.md",
)


def stageb_masks(n: int) -> dict:
    """Frozen Stage B disclosure masks M1-M5 for block length ``n``.

    Disclosed values are always the true U symbols at the returned
    positions (the caller maps them). M5 is the first ``N/2`` positions
    of the accepted Phase 3 O3 ``construction.analytic_order(0.05, n)``,
    imported unchanged with the count frozen at ``N/2``.
    """
    from .construction import analytic_order

    n = _check_positive_int(n, "n")
    if n < 2 or (n & (n - 1)):
        raise ValueError(f"stageb contract: n must be a power of two >= 2, got {n}")
    half = n // 2
    return {
        "M1_all_but_one": np.arange(n - 1, dtype=np.int64),
        "M2_prefix": np.arange(half, dtype=np.int64),
        "M3_suffix": np.arange(half, n, dtype=np.int64),
        "M4_alternating": np.arange(0, n, 2, dtype=np.int64),
        "M5_construction_order": np.asarray(
            analytic_order(0.05, n)[:half], dtype=np.int64
        ),
    }


def classify_stageb_failure(
    *,
    outcome: str,
    support_failure: bool = False,
    normalization_failure: bool = False,
    under_disclosure_ambiguous: bool = False,
    unclassified_error: bool = False,
) -> str:
    """Earliest-layer attribution category for one non-exact executed block.

    ``outcome`` is one of ``impossible`` / ``nonfinite`` / ``other``
    (finite but non-exact) for an executed block; ``exact`` and
    ``resource_abort`` are not failures and raise.
    """
    if support_failure:
        return "artifact_adapter_support"
    if normalization_failure:
        return "normalization"
    if outcome == "impossible":
        return "disclosure_contradiction"
    if outcome == "nonfinite":
        return "SC_numeric"
    if outcome == "other":
        if unclassified_error:
            return "unattributed"
        if under_disclosure_ambiguous:
            return "expected_under_disclosure"
        return "SC_decision"
    raise ValueError(
        f"attribution contract: outcome {outcome!r} is not a non-exact failure"
    )


def _stageb_error_kind(exc) -> tuple:
    """``(outcome, unclassified)`` for an SC exception other than impossible."""
    from .sc import NumericNonfiniteError

    if isinstance(exc, NumericNonfiniteError):
        return "nonfinite", False
    message = str(exc).lower()
    if "nan" in message or "nonfinite" in message:
        return "nonfinite", False
    return "other", True


def _stageb_expired(deadline: float) -> bool:
    return time.perf_counter() >= deadline


def _stageb_case_deadline(soft_cap_s: float, total_deadline: float) -> float:
    return min(time.perf_counter() + float(soft_cap_s), float(total_deadline))


def _stageb_blank_attribution() -> dict:
    return {name: 0 for name in STAGEB_ATTRIBUTION_CATEGORIES}


def _truth_leak_violation(*, bob, high, p1, probs, res, field,
                          known_positions=None, known_values=None) -> int:
    """0 if an adversarial post-metric truth mutation leaves metrics+decisions bitwise.

    A mutable copy of the sampled truth is adversarially shifted after the
    metric exists; the metric is rebuilt from Bob + table only and any SC
    rerun receives the already-frozen disclosed values. Any bitwise change
    counts as a violation.
    """
    from .prior import probs_to_symbol_metric
    from .sc import sc_decode

    mutated = np.array(high, dtype=np.int64, copy=True)
    mutated[:] = (mutated + 7) % 32  # adversarial; must not influence anything below
    probs2 = build_p1_metrics(bob, p1)
    if not np.array_equal(probs, probs2):
        return 1
    if res is None:
        return 0
    logp2 = probs_to_symbol_metric(probs2).logp
    try:
        res2 = sc_decode(logp2, field=field, alpha=2,
                         known_positions=known_positions,
                         known_values=known_values)
    except Exception:
        return 1
    if not np.array_equal(res.u_hat, res2.u_hat):
        return 1
    if not np.array_equal(res.x_hat, res2.x_hat):
        return 1
    if not np.array_equal(res.decision_metrics, res2.decision_metrics):
        return 1
    return 0


def _stageb_b1_case(rng, p_b, p1, n: int, n_blocks: int, *, field,
                    soft_cap_s: float, total_deadline: float) -> dict:
    """B1: tiny oracle sweep over every SC conditional, no disclosure."""
    from .empirical_oracle import empirical_oracle_conditionals_vectorized
    from .prior import probs_to_symbol_metric
    from .sc import NumericNonfiniteError, sc_decode
    from .transform import polar_transform

    deadline = _stageb_case_deadline(soft_cap_s, total_deadline)
    n = int(n)
    rec = {
        "case": f"B1_N{n}",
        "n": n,
        "n_blocks": int(n_blocks),
        "n_blocks_planned": int(n_blocks),
        "n_executed": 0,
        "n_resource_abort": 0,
        "n_exact": 0,
        "n_impossible": 0,
        "n_other": 0,
        "n_nonfinite": 0,
        "oracle_rows": 0,
        "max_prob_err": 0.0,
        "max_log_err": 0.0,
        "support_mismatches": 0,
        "numeric_failures": 0,
        "decode_exceptions": 0,
        "oracle_exceptions": 0,
        "truth_leak_violations": 0,
        "oracle_wall_s": 0.0,
        "wall_s": 0.0,
        "attribution": _stageb_blank_attribution(),
    }
    start = time.perf_counter()
    for _ in range(int(n_blocks)):
        if _stageb_expired(deadline):
            rec["n_resource_abort"] += 1
            continue
        bob = sample_bob(rng, p_b, n)
        high = sample_high_given_bob(rng, bob, p1)
        probs = build_p1_metrics(bob, p1)
        logp = probs_to_symbol_metric(probs).logp
        support_failure = bool(np.any(probs[np.arange(n), high] == 0))
        normalization_failure = bool(
            np.abs(np.logaddexp.reduce(logp, axis=1)).max() > 1e-9
        )
        u_true = polar_transform(high, field=field, alpha=2)
        res = None
        outcome = None
        unclassified = False
        try:
            res = sc_decode(logp, field=field, alpha=2)
            if np.isnan(res.decision_metrics).any() or np.isposinf(
                    res.decision_metrics).any():
                rec["numeric_failures"] += 1
                outcome = "nonfinite"
            elif np.array_equal(res.u_hat, u_true):
                outcome = "exact"
            else:
                outcome = "other"
        except NumericNonfiniteError:
            rec["numeric_failures"] += 1
            outcome = "nonfinite"
        except (ValueError, TypeError) as exc:
            rec["decode_exceptions"] += 1
            outcome, unclassified = _stageb_error_kind(exc)
        rec["n_executed"] += 1
        if outcome == "exact":
            rec["n_exact"] += 1
        elif outcome == "nonfinite":
            rec["n_nonfinite"] += 1
        elif outcome == "other":
            rec["n_other"] += 1
        if res is not None:
            oracle_start = time.perf_counter()
            try:
                chain = empirical_oracle_conditionals_vectorized(
                    logp, [res.u_hat[:i].tolist() for i in range(n)], field=field
                )
            except (ValueError, TypeError):
                rec["oracle_exceptions"] += 1
            else:
                for i in range(n):
                    prod = res.decision_metrics[i]
                    ora = chain[i]
                    both = np.isfinite(prod) & np.isfinite(ora)
                    rec["max_prob_err"] = max(
                        rec["max_prob_err"],
                        float(np.abs(np.exp(prod) - np.exp(ora)).max()),
                    )
                    if both.any():
                        rec["max_log_err"] = max(
                            rec["max_log_err"],
                            float(np.abs(prod[both] - ora[both]).max()),
                        )
                    rec["support_mismatches"] += int(
                        np.sum(np.isfinite(prod) != np.isfinite(ora))
                    )
                    rec["oracle_rows"] += 1
            rec["oracle_wall_s"] += time.perf_counter() - oracle_start
        rec["truth_leak_violations"] += _truth_leak_violation(
            bob=bob, high=high, p1=p1, probs=probs, res=res, field=field
        )
        if outcome != "exact":
            category = classify_stageb_failure(
                outcome=outcome,
                support_failure=support_failure,
                normalization_failure=normalization_failure,
                unclassified_error=unclassified,
            )
            rec["attribution"][category] += 1
    rec["wall_s"] = time.perf_counter() - start
    rec["gates"] = _stageb_b1_gates(rec)
    return rec


def _stageb_b1_gates(rec: dict) -> dict:
    complete = (
        rec["n_resource_abort"] == 0
        and rec["n_executed"] == rec["n_blocks_planned"]
    )
    return {
        "coverage_complete": complete,
        "max_prob_err": rec["max_prob_err"] <= STAGEB_PROB_TOL,
        "max_log_err": rec["max_log_err"] <= STAGEB_LOG_TOL,
        "support_mismatches": rec["support_mismatches"] == 0,
        "numeric_failures": rec["numeric_failures"] == 0,
        "decode_exceptions": rec["decode_exceptions"] == 0,
        "oracle_exceptions": rec["oracle_exceptions"] == 0,
        "truth_leak": rec["truth_leak_violations"] == 0,
    }


def _stageb_disclosure_case(rng, p_b, p1, n: int, mask_name: str, positions,
                            n_blocks: int, *, field, soft_cap_s: float,
                            total_deadline: float, initial_map: bool = False) -> dict:
    """B2/B3: masked-disclosure decode matrix with per-block accounting."""
    from .prior import probs_to_symbol_metric
    from .sc import (
        ImpossibleDisclosedValueError,
        NumericNonfiniteError,
        sc_decode,
    )
    from .transform import polar_transform

    deadline = _stageb_case_deadline(soft_cap_s, total_deadline)
    n = int(n)
    positions = np.asarray(positions, dtype=np.int64)
    rec = {
        "case": f"B{2 if not initial_map else 3}_N{n}_{mask_name}",
        "n": n,
        "mask": mask_name,
        "n_disclosed": int(positions.size),
        "n_blocks": int(n_blocks),
        "n_blocks_planned": int(n_blocks),
        "n_executed": 0,
        "n_resource_abort": 0,
        "n_exact": 0,
        "n_impossible": 0,
        "n_other": 0,
        "n_nonfinite": 0,
        "truth_leak_violations": 0,
        "wall_s": 0.0,
        "attribution": _stageb_blank_attribution(),
    }
    if initial_map:
        rec["n_initial_error"] = 0
    start = time.perf_counter()
    for _ in range(int(n_blocks)):
        if _stageb_expired(deadline):
            rec["n_resource_abort"] += 1
            continue
        bob = sample_bob(rng, p_b, n)
        high = sample_high_given_bob(rng, bob, p1)
        probs = build_p1_metrics(bob, p1)
        logp = probs_to_symbol_metric(probs).logp
        support_failure = bool(np.any(probs[np.arange(n), high] == 0))
        normalization_failure = bool(
            np.abs(np.logaddexp.reduce(logp, axis=1)).max() > 1e-9
        )
        if initial_map and np.any(np.argmax(logp, axis=1) != high):
            rec["n_initial_error"] += 1
        u_true = polar_transform(high, field=field, alpha=2)
        known_values = u_true[positions]
        res = None
        outcome = None
        unclassified = False
        try:
            res = sc_decode(logp, field=field, alpha=2,
                            known_positions=positions, known_values=known_values)
            if np.isnan(res.decision_metrics).any() or np.isposinf(
                    res.decision_metrics).any():
                outcome = "nonfinite"
            elif np.array_equal(res.u_hat, u_true) and np.array_equal(res.x_hat, high):
                outcome = "exact"
            else:
                outcome = "other"
        except ImpossibleDisclosedValueError:
            outcome = "impossible"
        except NumericNonfiniteError:
            outcome = "nonfinite"
        except (ValueError, TypeError) as exc:
            outcome, unclassified = _stageb_error_kind(exc)
        rec["n_executed"] += 1
        if outcome == "exact":
            rec["n_exact"] += 1
        elif outcome == "impossible":
            rec["n_impossible"] += 1
        elif outcome == "nonfinite":
            rec["n_nonfinite"] += 1
        else:
            rec["n_other"] += 1
        rec["truth_leak_violations"] += _truth_leak_violation(
            bob=bob, high=high, p1=p1, probs=probs, res=res, field=field,
            known_positions=positions, known_values=known_values,
        )
        if outcome != "exact":
            mask_bool = np.zeros(n, dtype=bool)
            mask_bool[positions] = True
            ambiguous = bool(np.any(
                (~mask_bool) & (np.argmax(logp, axis=1) != high)
            ))
            category = classify_stageb_failure(
                outcome=outcome,
                support_failure=support_failure,
                normalization_failure=normalization_failure,
                under_disclosure_ambiguous=ambiguous,
                unclassified_error=unclassified,
            )
            rec["attribution"][category] += 1
    rec["wall_s"] = time.perf_counter() - start
    if initial_map:
        rec["n_nan"] = rec["n_nonfinite"]  # frozen B3 report alias
    return rec


def _stageb_timed_median(fn, *, deadline: float, reps: int) -> tuple:
    """One warm-up + up to ``reps`` measured calls; median and count."""
    fn()  # warm-up, never measured
    spans = []
    for _ in range(int(reps)):
        if _stageb_expired(deadline):
            break
        start = time.perf_counter()
        fn()
        spans.append(time.perf_counter() - start)
    if not spans:
        return None, 0
    return float(np.median(np.asarray(spans, dtype=np.float64))), len(spans)


def _stageb_profile_case(rng, p_b, p1, n: int, positions, *, field,
                         soft_cap_s: float, total_deadline: float) -> dict:
    """B4: metric-only and decode-only timing at one block length."""
    from .prior import probs_to_symbol_metric
    from .sc import ImpossibleDisclosedValueError, NumericNonfiniteError, sc_decode
    from .transform import polar_transform

    deadline = _stageb_case_deadline(soft_cap_s, total_deadline)
    n = int(n)
    positions = np.asarray(positions, dtype=np.int64)
    rec = {
        "case": f"B4_N{n}",
        "n": n,
        "n_disclosed": int(positions.size),
        "reps_planned": STAGEB_B4_REPS,
        "n_metric_measured": 0,
        "n_decode_measured": 0,
        "metric_median_s": None,
        "decode_median_s": None,
        "metric_batch_shape": None,
        "metric_shape": None,
        "decision_shape": None,
        "decode_status": None,
        "disclosed_value_source": None,
        "peak_rss_gib": None,
        "resource_abort": False,
        "complete": False,
        "wall_s": 0.0,
    }
    if _stageb_expired(deadline):
        rec["resource_abort"] = True
        return rec
    start = time.perf_counter()
    bob_batch = sample_bob(rng, p_b, 4 * n).reshape(4, n)
    rec["metric_batch_shape"] = list(build_p1_metrics(bob_batch, p1).shape)
    metric_med, n_metric = _stageb_timed_median(
        lambda: build_p1_metrics(bob_batch, p1),
        deadline=deadline, reps=STAGEB_B4_REPS,
    )
    rec["metric_median_s"] = metric_med
    rec["n_metric_measured"] = n_metric

    bob = sample_bob(rng, p_b, n)
    probs = build_p1_metrics(bob, p1)
    logp = probs_to_symbol_metric(probs).logp
    rec["metric_shape"] = list(logp.shape)
    high = sample_high_given_bob(rng, bob, p1)
    u_true = polar_transform(high, field=field, alpha=2)
    values = u_true[positions]
    rec["disclosed_value_source"] = "true_U"

    def _decode():
        return sc_decode(logp, field=field, alpha=2,
                         known_positions=positions, known_values=values)

    try:
        probe = _decode()
    except ImpossibleDisclosedValueError:
        values = np.argmax(logp, axis=1)[positions].astype(np.int64)
        rec["disclosed_value_source"] = "metric_argmax"
        try:
            probe = _decode()
        except (ImpossibleDisclosedValueError, NumericNonfiniteError):
            rec["decode_status"] = "disclosure_unavailable"
            rec["peak_rss_gib"] = _peak_rss_gib()
            rec["resource_abort"] = True
            rec["wall_s"] = time.perf_counter() - start
            return rec
    except NumericNonfiniteError:
        rec["decode_status"] = "numeric_failure"
        rec["peak_rss_gib"] = _peak_rss_gib()
        rec["resource_abort"] = True
        rec["wall_s"] = time.perf_counter() - start
        return rec
    rec["decode_status"] = "ok"
    rec["decision_shape"] = list(probe.decision_metrics.shape)
    decode_med, n_decode = _stageb_timed_median(
        _decode, deadline=deadline, reps=STAGEB_B4_REPS
    )
    rec["decode_median_s"] = decode_med
    rec["n_decode_measured"] = n_decode
    rec["peak_rss_gib"] = _peak_rss_gib()
    rec["complete"] = (
        n_metric >= STAGEB_B4_REPS and n_decode >= STAGEB_B4_REPS
    )
    rec["resource_abort"] = not rec["complete"]
    rec["wall_s"] = time.perf_counter() - start
    return rec


def _stageb_merge_totals(records, keys) -> dict:
    totals = {key: 0 for key in keys}
    for rec in records:
        for key in keys:
            totals[key] += int(rec[key])
    return totals


def _stageb_merge_attribution(records) -> dict:
    totals = _stageb_blank_attribution()
    for rec in records:
        for name, count in rec["attribution"].items():
            totals[name] += int(count)
    return totals


def _stageb_plan(outp, seed, artifact_identity, wall_s) -> dict:
    """Frozen plan/identity record (no artifact content, metadata only)."""
    return {
        "entry": "empirical_stageb_diagnostic",
        "scope": (
            "P3 Stage B: model-sampled accepted-CAL-prior P1 metric into the "
            "accepted q-ary SC decoder; interface qualification only"
        ),
        "q": 32,
        "seed": int(seed),
        "invocation": {
            "mode": "stageb",
            "npz_path": None if artifact_identity is None else artifact_identity["npz_path"],
            "summary_path": None if artifact_identity is None else artifact_identity["summary_path"],
            "out": str(outp),
        },
        "artifact": artifact_identity if artifact_identity is not None else {
            "source": "caller-injected tables (test seam)"
        },
        "attempt_accounting": {
            "attempts_allowed": 1,
            "consumed_at_write": 1 if artifact_identity is not None else 0,
            "consumed_on": "first artifact content open",
        },
        "seeds": {
            "stageb_diagnostic": int(seed),
            "unit_not_used": P3_UNIT_SEED,
            "train_not_used": P3_TRAIN_SEED,
            "banned_predecessor_range": sorted(BANNED_SEEDS),
        },
        "derivation": (
            "prior.smooth_joint_to_conditional(counts_ab, LAMBDA_STAR) -> "
            "prior.derive_p1; p_b = artifact.p_b; "
            "probs -> prior.probs_to_symbol_metric (q=32)"
        ),
        "b1": {
            "n": list(STAGEB_B1_N),
            "blocks_per_n": STAGEB_B1_BLOCKS,
            "disclosure": "none",
            "oracle": "empirical_oracle vectorized exhaustive backend",
            "thresholds": {
                "max_prob_err": STAGEB_PROB_TOL,
                "max_log_err": STAGEB_LOG_TOL,
                "support_mismatches": 0,
                "numeric_failures": 0,
                "truth_leak_violations": 0,
            },
        },
        "b2": {
            "n": list(STAGEB_B2_N),
            "masks": list(STAGEB_MASK_NAMES),
            "blocks_per_mask": STAGEB_B2_BLOCKS,
        },
        "b3": {
            "n": STAGEB_B3_N,
            "masks": list(STAGEB_MASK_NAMES),
            "blocks_per_mask": STAGEB_B3_BLOCKS,
            "total_blocks": STAGEB_B3_BLOCKS * len(STAGEB_MASK_NAMES),
            "exhaustive_oracle": False,
            "hard_gate": "zero crash/nonfinite/truth-leak only",
        },
        "b4": {
            "n": list(STAGEB_B4_N),
            "reps": STAGEB_B4_REPS,
            "metric_batch_frames": 4,
            "decode_disclosure_mask": "M5_construction_order first N//2",
        },
        "b5": {"categories": list(STAGEB_ATTRIBUTION_CATEGORIES)},
        "budget": {
            "total_s": STAGEB_TOTAL_CAP_S,
            "per_case_soft_s": STAGEB_SOFT_CAP_S,
            "rss_bytes_max": STAGEB_RSS_LIMIT_BYTES,
        },
        "out_files": list(STAGEB_OUT_FILES),
        "wall_s": float(wall_s),
        "no_claim_note": (
            "Candidate-scope interface diagnostic only. No FER, leakage, "
            "key-rate, reconciliation, construction/K or performance claim."
        ),
    }


def _stageb_report(summary: dict, plan: dict) -> str:
    lines = [
        "# P3 Stage B empirical-prior SC interface diagnostic",
        "",
        f"- seed: {plan['seed']}",
        f"- artifact attempt consumed at write: "
        f"{plan['attempt_accounting']['consumed_at_write']}",
        f"- wall_s: {summary['wall_s']:.3f}",
        "",
        "## B1 tiny oracle gates",
        "",
        "| case | executed | exact | oracle rows | max prob err | max log err | "
        "support mismatch | numeric fail | truth leak | gates |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for rec in summary["b1"]:
        gates = rec["gates"]
        lines.append(
            f"| {rec['case']} | {rec['n_executed']}/{rec['n_blocks_planned']} | "
            f"{rec['n_exact']} | {rec['oracle_rows']} | "
            f"{rec['max_prob_err']:.3e} | {rec['max_log_err']:.3e} | "
            f"{rec['support_mismatches']} | "
            f"{rec['numeric_failures'] + rec['decode_exceptions']} | "
            f"{rec['truth_leak_violations']} | "
            f"{'PASS' if all(gates.values()) else 'FAIL'} |"
        )
    lines += [
        "",
        "## B2/B3 disclosure-shape matrix",
        "",
        "| case | mask | disclosed | planned | executed | exact | impossible | "
        "other | nonfinite | initial MAP err | wall s |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for rec in summary["b2"]["cases"] + summary["b3"]["cases"]:
        lines.append(
            f"| {rec['case']} | {rec['mask']} | {rec['n_disclosed']} | "
            f"{rec['n_blocks_planned']} | {rec['n_executed']} | {rec['n_exact']} | "
            f"{rec['n_impossible']} | {rec['n_other']} | {rec['n_nonfinite']} | "
            f"{rec.get('n_initial_error', '-')} | {rec['wall_s']:.3f} |"
        )
    b2_totals = summary["b2"]["totals"]
    b3_totals = summary["b3"]["totals"]
    lines += [
        "",
        f"B2 totals: exact={b2_totals['n_exact']} "
        f"impossible={b2_totals['n_impossible']} other={b2_totals['n_other']} "
        f"nonfinite={b2_totals['n_nonfinite']} "
        f"resource_abort={b2_totals['n_resource_abort']}",
        f"B3 totals: exact={b3_totals['n_exact']} "
        f"impossible={b3_totals['n_impossible']} other={b3_totals['n_other']} "
        f"nonfinite={b3_totals['n_nonfinite']} "
        f"initial_map_err={b3_totals['n_initial_error']} "
        f"resource_abort={b3_totals['n_resource_abort']}",
        "",
        "## B5 earliest-layer attribution (non-exact executed blocks)",
        "",
        "| category | count |",
        "|---|---|",
    ]
    for name in STAGEB_ATTRIBUTION_CATEGORIES:
        lines.append(f"| {name} | {summary['b5']['totals'][name]} |")
    lines += [
        "",
        "## B4 resource profile (median of >=5 measured calls after warm-up)",
        "",
        "| N | metric median s | decode median s | metric batch shape | "
        "metric shape | decision shape | peak RSS GiB | complete |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for rec in summary["b4"]["profiles"]:
        lines.append(
            f"| {rec['n']} | {rec['metric_median_s']} | {rec['decode_median_s']} | "
            f"{rec['metric_batch_shape']} | {rec['metric_shape']} | "
            f"{rec['decision_shape']} | {rec['peak_rss_gib']} | {rec['complete']} |"
        )
    lines += [
        "",
        "## Hard gates",
        "",
        f"- `hard_gates_pass`: {summary['hard_gates_pass']}",
        f"- `truth_leak_violations`: {summary['truth_leak_violations']}",
        f"- `resource_abort_blocks`: {summary['resource_abort_blocks']}",
        f"- `candidate_conclusion`: {summary['candidate_conclusion']}",
        "",
        summary["candidate_conclusion_note"],
        "",
    ]
    return "\n".join(lines)


def _run_stageb_from_tables(*, rng, p_b, p1, seed, out,
                            soft_cap_s: float = STAGEB_SOFT_CAP_S,
                            total_cap_s: float = STAGEB_TOTAL_CAP_S,
                            artifact_identity: dict = None) -> dict:
    """Frozen Stage B matrix on caller-supplied tables (artifact or injected).

    Used by :func:`run_stageb_diagnostic` after the single artifact load and
    by tests with injected tables and temporary roots. Writes exactly
    ``STAGEB_OUT_FILES`` into a root created only at the end.
    """
    if not isinstance(rng, np.random.Generator):
        raise TypeError(
            "stageb contract: rng must be an explicit numpy.random.Generator"
        )
    outp = _check_out(out)
    p1_arr = np.asarray(p1, dtype=np.float64)
    if p1_arr.ndim != 2 or p1_arr.shape[0] != 32 or p1_arr.shape[1] < 1:
        raise ValueError(
            f"stageb contract: p1 must be [U1,B] with 32 rows, got {p1_arr.shape}"
        )
    p_b_arr = np.asarray(p_b, dtype=np.float64)
    field = _field_for_q(32)
    start = time.perf_counter()
    total_deadline = start + float(total_cap_s)

    b1 = [
        _stageb_b1_case(rng, p_b_arr, p1_arr, n, STAGEB_B1_BLOCKS,
                        field=field, soft_cap_s=soft_cap_s,
                        total_deadline=total_deadline)
        for n in STAGEB_B1_N
    ]
    b2 = []
    for n in STAGEB_B2_N:
        masks = stageb_masks(n)
        for mask_name in STAGEB_MASK_NAMES:
            b2.append(_stageb_disclosure_case(
                rng, p_b_arr, p1_arr, n, mask_name, masks[mask_name],
                STAGEB_B2_BLOCKS, field=field, soft_cap_s=soft_cap_s,
                total_deadline=total_deadline,
            ))
    b3 = []
    b3_masks = stageb_masks(STAGEB_B3_N)
    for mask_name in STAGEB_MASK_NAMES:
        b3.append(_stageb_disclosure_case(
            rng, p_b_arr, p1_arr, STAGEB_B3_N, mask_name,
            b3_masks[mask_name], STAGEB_B3_BLOCKS, field=field,
            soft_cap_s=soft_cap_s, total_deadline=total_deadline,
            initial_map=True,
        ))
    b4 = [
        _stageb_profile_case(
            rng, p_b_arr, p1_arr, n,
            stageb_masks(n)["M5_construction_order"], field=field,
            soft_cap_s=soft_cap_s, total_deadline=total_deadline,
        )
        for n in STAGEB_B4_N
    ]

    b2_totals = _stageb_merge_totals(b2, (
        "n_blocks_planned", "n_executed", "n_resource_abort", "n_exact",
        "n_impossible", "n_other", "n_nonfinite", "truth_leak_violations",
    ))
    b3_totals = _stageb_merge_totals(b3, (
        "n_blocks_planned", "n_executed", "n_resource_abort", "n_exact",
        "n_impossible", "n_other", "n_nonfinite", "n_nan", "n_initial_error",
        "truth_leak_violations",
    ))
    b2_totals["wall_s"] = float(sum(rec["wall_s"] for rec in b2))
    b3_totals["wall_s"] = float(sum(rec["wall_s"] for rec in b3))

    scored_cases = b1 + b2 + b3
    attribution_totals = _stageb_merge_attribution(scored_cases)
    truth_leak_total = int(sum(rec["truth_leak_violations"] for rec in scored_cases))
    resource_abort_blocks = int(
        sum(rec["n_resource_abort"] for rec in scored_cases)
    )
    resource_abort_profiles = int(sum(1 for rec in b4 if rec["resource_abort"]))
    nonfinite_total = int(
        sum(rec["n_nonfinite"] for rec in b2 + b3)
    ) + int(sum(rec["numeric_failures"] for rec in b1))

    b1_all_gates_pass = all(
        all(rec["gates"].values()) for rec in b1
    )
    hard_gates = {
        "b1_all_gates": bool(b1_all_gates_pass),
        "b2_b3_zero_nonfinite": nonfinite_total == 0,
        "b2_b3_zero_unattributed": attribution_totals["unattributed"] == 0,
        "b2_b3_coverage_complete": all(
            rec["n_resource_abort"] == 0
            and rec["n_executed"] == rec["n_blocks_planned"]
            for rec in b2 + b3
        ),
        "b4_complete": all(rec["complete"] for rec in b4),
        "zero_truth_leak": truth_leak_total == 0,
    }
    hard_gates_pass = bool(all(hard_gates.values()))
    wall_s = time.perf_counter() - start
    peak_rss = _peak_rss_gib()

    summary = {
        "entry": "empirical_stageb_diagnostic",
        "q": 32,
        "seed": int(seed),
        "wall_s": float(wall_s),
        "b1": b1,
        "b2": {"cases": b2, "totals": b2_totals},
        "b3": {"cases": b3, "totals": b3_totals},
        "b4": {"profiles": b4, "peak_rss_gib": peak_rss},
        "b5": {
            "categories": list(STAGEB_ATTRIBUTION_CATEGORIES),
            "per_case": {
                rec["case"]: dict(rec["attribution"]) for rec in scored_cases
            },
            "totals": attribution_totals,
            "b4_scored_blocks": 0,  # B4 is timing-only, never scored/attributed
        },
        "truth_leak_violations": truth_leak_total,
        "resource_abort_blocks": resource_abort_blocks,
        "resource_abort_profiles": resource_abort_profiles,
        "nonfinite_total": nonfinite_total,
        "hard_gates": hard_gates,
        "hard_gates_pass": hard_gates_pass,
        "candidate_conclusion": (
            "EMPIRICAL_PRIOR_SC_INTERFACE_CANDIDATE" if hard_gates_pass else None
        ),
        "candidate_conclusion_note": (
            "Candidate label only: acceptance is owned by the main thread and "
            "an independent Pre-RESULT review. This is not real-data FER, "
            "reconciliation, leakage, key rate or construction/K evidence."
        ),
    }

    plan = _stageb_plan(outp, seed, artifact_identity, wall_s)
    oracle_records = {
        "entry": "empirical_stageb_oracle_records",
        "backend": "empirical_oracle_conditionals_vectorized",
        "max_candidates": 1 << 20,
        "b1": [
            {key: rec[key] for key in (
                "case", "n", "n_blocks_planned", "n_executed",
                "n_resource_abort", "oracle_rows", "max_prob_err",
                "max_log_err", "support_mismatches", "numeric_failures",
                "decode_exceptions", "oracle_exceptions",
                "truth_leak_violations", "oracle_wall_s", "gates",
            )}
            for rec in b1
        ],
    }
    stress_and_profile = {
        "entry": "empirical_stageb_stress_and_profile",
        "b2_b3_wall_s": {
            "b2": {"cases": b2_totals["wall_s"]},
            "b3": {"cases": b3_totals["wall_s"]},
        },
        "b4": {"profiles": b4, "peak_rss_gib": peak_rss},
        "peak_rss_gib": peak_rss,
    }

    outp.mkdir(parents=True, exist_ok=False)
    (outp / "frozen_plan.json").write_text(json.dumps(plan, indent=2))
    (outp / "oracle_records.json").write_text(
        json.dumps(oracle_records, indent=2)
    )
    (outp / "stress_and_profile.json").write_text(
        json.dumps(stress_and_profile, indent=2)
    )
    (outp / "diagnostic_summary.json").write_text(json.dumps(summary, indent=2))
    (outp / "report.md").write_text(_stageb_report(summary, plan))
    return summary


def run_stageb_diagnostic(*, npz_path, summary_path, seed, out) -> dict:
    """Stage B: one accepted-artifact load, then the frozen B1-B5 matrix.

    Requires independent Pre-EXECUTE PASS. The output root is refused if
    it exists (checked before any artifact content is opened); the banned
    seed check also precedes the load. The root is created only at the
    end, after the frozen matrix produced all five files.
    """
    from .prior import derive_p1, smooth_joint_to_conditional
    from .prior_artifact import LAMBDA_STAR, load_prior_artifact

    outp = _check_out(out)
    rng = make_rng(seed)  # refuses banned streams before any artifact open
    npz_file = Path(npz_path)
    summary_file = Path(summary_path)
    artifact = load_prior_artifact(npz_file, summary_file)  # single load/attempt
    f_table = smooth_joint_to_conditional(artifact.counts_ab, LAMBDA_STAR)
    p1 = derive_p1(f_table)
    p_b = np.asarray(artifact.p_b, dtype=np.float64)
    identity = {
        "npz_path": str(npz_file),
        "npz_bytes": int(npz_file.stat().st_size),
        "summary_path": str(summary_file),
        "summary_bytes": int(summary_file.stat().st_size),
        "loader": "prior_artifact.load_prior_artifact",
        "lambda_star": float(LAMBDA_STAR),
        "counts_ab_shape": list(artifact.counts_ab.shape),
        "p_b_shape": list(artifact.p_b.shape),
        "derived_p1_shape": list(p1.shape),
    }
    return _run_stageb_from_tables(
        rng=rng, p_b=p_b, p1=p1, seed=int(seed), out=outp,
        soft_cap_s=STAGEB_SOFT_CAP_S, total_cap_s=STAGEB_TOTAL_CAP_S,
        artifact_identity=identity,
    )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Phase 4-P3 empirical diagnostic")
    ap.add_argument("--mode", required=True, choices=("synthetic", "artifact", "stageb"))
    ap.add_argument("--q", required=False, type=int, default=None)
    ap.add_argument("--n", required=False, type=int, default=None)
    ap.add_argument("--n-b", required=False, type=int, default=None)
    ap.add_argument("--seed", required=True, type=int)
    ap.add_argument("--n-blocks", required=False, type=int, default=None)
    ap.add_argument("--npz", required=False, type=str, default=None)
    ap.add_argument("--summary", required=False, type=str, default=None)
    ap.add_argument("--out", required=True, type=str)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.mode == "synthetic":
            if args.q is None or args.n is None or args.n_b is None \
                    or args.n_blocks is None:
                raise ValueError(
                    "diagnostic contract: synthetic mode requires --q, --n, "
                    "--n-b and --n-blocks")
            payload = run_synthetic_diagnostic(
                q=args.q, n=args.n, n_b=args.n_b, seed=args.seed,
                n_blocks=args.n_blocks, out=args.out)
        elif args.mode == "artifact":
            if args.q is None or args.n is None or args.n_blocks is None \
                    or not args.npz or not args.summary:
                raise ValueError(
                    "diagnostic contract: artifact mode requires --q, --n, "
                    "--n-blocks, --npz and --summary")
            payload = run_artifact_diagnostic(
                npz_path=args.npz, summary_path=args.summary, seed=args.seed,
                n=args.n, n_blocks=args.n_blocks, out=args.out)
        else:
            if not args.npz or not args.summary:
                raise ValueError(
                    "diagnostic contract: stageb mode requires --npz and --summary")
            payload = run_stageb_diagnostic(
                npz_path=args.npz, summary_path=args.summary, seed=args.seed,
                out=args.out)
    except (ValueError, TypeError, FileExistsError) as exc:
        print(f"empirical_diagnostic refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
