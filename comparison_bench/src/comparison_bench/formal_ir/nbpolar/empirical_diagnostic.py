"""Phase 4-P3 diagnostic entrypoint: synthetic now, one artifact run later.

Synthetic mode (Stage A/A2, no artifact read) builds injected asymmetric
tables with a frozen caller seed, samples model blocks through
``empirical_channel``, compares the vectorized gather against the
literal reference, runs reference SC, and -- on tiny domains only --
checks every SC conditional against ``empirical_oracle``.

Artifact mode (Stage B, after independent Pre-EXECUTE PASS only) loads
the single accepted CAL artifact once via ``prior_artifact`` and repeats
the same measurements from the in-memory table. It is implemented and
guarded here but MUST NOT run before that review; ordinary tests only
exercise its refusal paths with nonexistent temporary paths, never the
sibling root.

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
    try:
        import resource

        return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0**3))
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


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Phase 4-P3 empirical diagnostic")
    ap.add_argument("--mode", required=True, choices=("synthetic", "artifact"))
    ap.add_argument("--q", required=True, type=int)
    ap.add_argument("--n", required=True, type=int)
    ap.add_argument("--n-b", required=False, type=int, default=None)
    ap.add_argument("--seed", required=True, type=int)
    ap.add_argument("--n-blocks", required=True, type=int)
    ap.add_argument("--npz", required=False, type=str, default=None)
    ap.add_argument("--summary", required=False, type=str, default=None)
    ap.add_argument("--out", required=True, type=str)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.mode == "synthetic":
            if args.n_b is None:
                raise ValueError("diagnostic contract: synthetic mode requires --n-b")
            payload = run_synthetic_diagnostic(
                q=args.q, n=args.n, n_b=args.n_b, seed=args.seed,
                n_blocks=args.n_blocks, out=args.out)
        else:
            if not args.npz or not args.summary:
                raise ValueError(
                    "diagnostic contract: artifact mode requires --npz and --summary")
            payload = run_artifact_diagnostic(
                npz_path=args.npz, summary_path=args.summary, seed=args.seed,
                n=args.n, n_blocks=args.n_blocks, out=args.out)
    except (ValueError, TypeError, FileExistsError) as exc:
        print(f"empirical_diagnostic refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
