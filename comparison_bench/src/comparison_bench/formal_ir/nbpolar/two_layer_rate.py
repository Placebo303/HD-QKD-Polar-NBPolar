"""Phase 6-R2 two-layer BEC rate-feasibility analysis (decoder-free).

Determines, under an explicit per-source binary-erasure surrogate, the smallest
block length at which the two-layer NB-Polar disclosure accounting reaches
``f <= 1.3``, and records the missing operational-L2 dependency as a decision
output.

Frozen model (packet ``NBPOLAR-PHASE6-R2-TWO-LAYER-RATE-FEASIBILITY``, OpenSpec
``formal-ir-nbpolar-phase6-r2-two-layer-rate-feasibility``):

- BEC polarization recurrence ``z_minus = 2z - z**2``, ``z_plus = z**2``
  applied in natural order and vectorized over the current spectrum.
- Per-layer erasure surrogate ``epsilon_l = H_l / 5`` for the accepted
  per-source L1/L2 conditional entropies ``H1``/``H2`` (bits/symbol over the
  5-bit GF32 plane).
- Whole-block FER budget ``1e-2`` split per allocation; the per-layer minimum-K
  selection is the smallest ``K`` whose worst-first suffix union bound
  ``sum(z[K:]) <= budget_l`` holds (suffix-sum based, ``K`` in ``0..N``).
- Accounting: ``leakage_bits = 5*(K1+K2) + 64``,
  ``leakage_bits_no_tag = 5*(K1+K2)``, ``nH = N*(H1+H2)``,
  ``f = leakage_bits/nH``, ``f_no_tag = leakage_bits_no_tag/nH``.
- Sensitivity axes: every registered source x {equal, entropy_proportional}
  FER allocation x ``N`` in ``2**8..2**18`` inclusive.

The single calibration point ``N=256, epsilon=0.05, budget=1e-2 -> K=43`` is
reproduced from the accepted single-layer convention before any table is
produced; calibration or cross-implementation failure is a hard stop.

Scope: this is a surrogate planning estimate only. It is NOT empirical
neighbor-shift channel performance, NOT a rigorous lower bound and NOT decoder
evidence. This module contains no SC/decoder call, no artifact/parquet/TTBin
read, no synthetic block sampling, no attempt/seed consumption and no RNG;
importing it performs no I/O.
"""

from __future__ import annotations

import argparse
import json
from numbers import Integral, Real
from pathlib import Path

import numpy as np

Q = 32
BITS_PER_COORDINATE = 5
TAG_BITS = 64
FER_BUDGET = 1e-2
F_TARGET = 1.3
N_EXPONENTS = tuple(range(8, 19))
CALIBRATION_N = 256
CALIBRATION_EPSILON = 0.05
CALIBRATION_BUDGET = 1e-2
CALIBRATION_K = 43
ALLOCATIONS = ("equal", "entropy_proportional")

OUTPUT_JSON_NAME = "two_layer_rate_sensitivity.json"
OUTPUT_REPORT_NAME = "R2_REPORT.md"

SURROGATE_DISCLAIMER = (
    "surrogate planning estimate only — not empirical neighbor-shift channel "
    "performance, not a rigorous lower bound, not decoder evidence"
)

# Frozen full-precision inputs. H1/H2 are the TRAIN NLL_U1/NLL_U2 values of
# ``docs/v49_distribution_tables/v49_train_val_hold_nll.csv``; the
# cross-references are the accepted V26 A02 and V27R audit rows.
FROZEN_SOURCES = {
    "1M": {
        "h1": 0.02428054681872374,
        "h2": 0.7767572780789994,
        "provenance": {
            "csv": (
                "docs/v49_distribution_tables/v49_train_val_hold_nll.csv:2 "
                "(source=1M, split=TRAIN, columns nll_u1,nll_u2)"
            ),
            "diagnosis_doc": "docs/v49-distribution-shift-diagnosis-20260827.md:78",
            "chain": [
                "docs/decision-log.md:402-404 (V27R review: H from channel_counts.npz matches frozen docs)",
                "docs/decision-log.md:2879-2891 (V26 A02 GF32+GF32 f=1.3 30/30)",
                "docs/nbldpc-v26-channel-informed-multilevel-de-report-20260819.md:39-40 (A02 L1/L2 H 0.02566205/0.80690067)",
            ],
        },
    },
    "1p5M": {
        "h1": 0.02519949687789926,
        "h2": 0.8003665547438703,
        "provenance": {
            "csv": (
                "docs/v49_distribution_tables/v49_train_val_hold_nll.csv:7 "
                "(source=1p5M, split=TRAIN, columns nll_u1,nll_u2)"
            ),
            "diagnosis_doc": "docs/v49-distribution-shift-diagnosis-20260827.md:81",
            "chain": [
                "docs/decision-log.md:402-404 (V27R review: H from channel_counts.npz matches frozen docs)",
                "docs/decision-log.md:2879-2891 (V26 A02 GF32+GF32 f=1.3 30/30)",
                "docs/nbldpc-v26-channel-informed-multilevel-de-report-20260819.md:39-40 (A02 L1/L2 H 0.02566205/0.80690067)",
            ],
        },
    },
    "2M": {
        "h1": 0.025662048796915037,
        "h2": 0.8069006731253232,
        "provenance": {
            "csv": (
                "docs/v49_distribution_tables/v49_train_val_hold_nll.csv:12 "
                "(source=2M, split=TRAIN, columns nll_u1,nll_u2)"
            ),
            "diagnosis_doc": "docs/v49-distribution-shift-diagnosis-20260827.md:84",
            "chain": [
                "docs/decision-log.md:402-404 (V27R review: H from channel_counts.npz matches frozen docs)",
                "docs/decision-log.md:2879-2891 (V26 A02 GF32+GF32 f=1.3 30/30)",
                "docs/nbldpc-v26-channel-informed-multilevel-de-report-20260819.md:39-40 (A02 L1/L2 H 0.02566205/0.80690067)",
            ],
        },
    },
}

H2_PROVENANCE_NOTE = (
    "H2 is the in-sample conditional entropy estimated as the TRAIN NLL of "
    "P_TRAIN(U2|B,U1) (column nll_u2); the same CSV row documents "
    "kl_sample = E[NLL]-E[H] ~= -1.5e-12. Cross-referenced to the accepted "
    "V26 A02 L1/L2 channel rows and the V27R audit review (channel_counts.npz "
    "recomputation matches the frozen docs; packet-documented agreement ~1e-15 "
    "with the accepted V32 audit chain)."
)

# R2-A07 decision output: code/doc evidence only, no execution.
L2_AUDIT = {
    "claim": (
        "oracle-L2 (true-L1-conditioned) and operational candidate-L2 have "
        "never entered SC execution; only the single-layer L1 high-plane path "
        "(label=32*x_hat, constant-zero low half) has executed"
    ),
    "code_evidence": [
        "sc.py:188 sc_decode(logp_x, *, field, alpha=2, known_positions=None, known_values=None): one full-Bob metric; the decoder API has no L1/L2 conditioning or prior argument",
        "protocol.py:12-13 docstring and protocol.py:137-139 labels_from_symbols: label_j = 32*x_j single-layer packing (low half constant zero)",
        "protocol.py:639 builds the block metric via generate_erasure_block (Bob-only one-hot/uniform posterior); no L1 estimate conditions it",
        "incremental.py:1440-1444 and 2191-2195 freeze single_layer_low_half_constant_zero: True; metrics built at incremental.py:1669/2290 and every level calls sc_decode on the same original Bob metric (incremental.py:532/691)",
        "prior.py:222 gather_p2_metrics (candidate-L2 gather on hard u1) is defined/exported (prior.py:46; __init__.py:52) but has zero production call sites; only tests/test_nbpolar_prior.py:229-237,302 call it and that file never invokes SC",
        "prior.py:67-68 ORACLE_CONDITIONED/CANDIDATE_CONDITIONED are never constructed outside the enum; prior_artifact.py:215 constructs PRIOR_ONLY only",
        "empirical_channel.py:1-25: the P3 empirical path reduces the full mapping to the high level by marginalizing the low symbol and its operational builder signature has no Alice/truth/u argument",
    ],
    "doc_evidence": [
        "docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md:37-38: app_fed_l2_prior EXCLUDED from first SC path; oracle_l2_prior REFERENCE pattern only; section 4 P2_true oracle-only, P2_hat executable dependency",
        "docs/nbpolar/ROADMAP.md:82-84: L1 exact, oracle-L2 on true L1 and operational L2 on the L1 candidate are separated Phase 4 diagnostics",
        "docs/decision-log.md:3811-3812 (2026-09-13): the roadmap's oracle-L2 and candidate-conditioned operational L2 paths have not been exercised by the Phase 5/6 gates",
        "P5 OPERATOR_RETURN.md:45-46 and P5_FREEZE.md:22: R2 label domain is the 10-bit single-layer embedding with low half constant zero",
        "P6 OPERATOR_RETURN.md:31: physical labels 32*x_hat; R1 OPERATOR_RETURN.md:1-6: frozen single-layer synthetic scope",
        "P3 OPERATOR_RETURN.md:9-12: Stage A/A2 qualified only the P1 metric (high symbol) into SC; Stage B ran the P1 metric only",
    ],
    "conclusion": (
        "VERIFIED: no L2 prior and no L2-conditioned SC has ever executed; "
        "all accepted P3/P5/P6/R1 gates used the single-layer L1 high-plane "
        "path only"
    ),
}

# R2-A09 decision output only; none of this is implemented here.
SUCCESSOR_PREREQUISITES = [
    (
        "(a) L2 prior extraction per the P0 contract (P2_true/P2_hat tensors, "
        "PHASE4_P0_PRIOR_CONTRACT.md section 4) with an explicit two-stage "
        "restart SC that conditions the low-plane metric on the accepted L1 "
        "hard candidate under the same provenance/fail-closed rules "
        "(no APP import; floor policy per P0 section 3)"
    ),
    (
        "(b) a paired two-layer development gate under the same accounting "
        "discipline (each coordinate disclosed once, one tag per accepted "
        "candidate, undetected isolated, no rerun/no tuning) with thresholds "
        "frozen before execution"
    ),
    (
        "(c) empirical construction and a scalable decoder sufficient for "
        "N >= 2**17 (e.g. FWHT q-ary SC); explicitly OUT OF SCOPE of R2"
    ),
]


def _check_epsilon(epsilon) -> float:
    if isinstance(epsilon, bool) or not isinstance(epsilon, Real):
        raise TypeError("epsilon must be a real number")
    value = float(epsilon)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"epsilon must lie in [0, 1], got {value}")
    return value


def _check_power_of_two(n) -> int:
    if isinstance(n, bool) or not isinstance(n, Integral):
        raise TypeError("n must be a power-of-two integer")
    size = int(n)
    if size < 1 or (size & (size - 1)):
        raise ValueError(f"n must be a positive power of two, got {size}")
    return size


def _check_budget(budget) -> float:
    if isinstance(budget, bool) or not isinstance(budget, Real):
        raise TypeError("budget must be a real number")
    value = float(budget)
    if not np.isfinite(value) or value < 0.0:
        raise ValueError(f"budget must be finite and >= 0, got {value}")
    return value


def _check_spectrum(spectrum) -> np.ndarray:
    arr = np.asarray(spectrum, dtype=np.float64)
    if arr.ndim != 1 or arr.size < 1:
        raise ValueError("spectrum must be a non-empty 1-D array")
    if not np.all(np.isfinite(arr)):
        raise ValueError("spectrum must be finite")
    if float(arr.min()) < 0.0 or float(arr.max()) > 1.0:
        raise ValueError("spectrum entries must lie in [0, 1]")
    return arr


def erasure_spectrum(epsilon, n) -> np.ndarray:
    """Operational BEC polarization spectrum in natural order.

    ``z_minus = 2z - z**2`` expands to the even index, ``z_plus = z**2`` to
    the odd index (index 0 is the all-minus coordinate), vectorized over the
    current spectrum for any power-of-two ``n``.
    """
    epsilon = _check_epsilon(epsilon)
    n = _check_power_of_two(n)
    vec = np.array([epsilon], dtype=np.float64)
    while vec.size < n:
        out = np.empty(2 * vec.size, dtype=np.float64)
        out[0::2] = 2.0 * vec - vec * vec
        out[1::2] = vec * vec
        vec = out
    return vec


def literal_erasure_spectrum(epsilon, n):
    """Independent literal oracle: per-element recursion, no shared helpers.

    Returns a plain ``list[float]`` of length ``n``. Written separately from
    :func:`erasure_spectrum` so a shared vectorization bug cannot agree with
    itself; intended for tiny powers of two.
    """
    if isinstance(epsilon, bool) or not isinstance(epsilon, Real):
        raise TypeError("epsilon must be a real number")
    value = float(epsilon)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"epsilon must lie in [0, 1], got {value}")
    if isinstance(n, bool) or not isinstance(n, Integral):
        raise TypeError("n must be a power-of-two integer")
    size = int(n)
    if size < 1 or (size & (size - 1)):
        raise ValueError(f"n must be a positive power of two, got {size}")

    def expand(length, current):
        if length == 1:
            return [current]
        half = expand(length // 2, current)
        out = []
        for item in half:
            out.append(2.0 * item - item * item)
            out.append(item * item)
        return out

    return expand(size, value)


def minimum_disclosure_count(spectrum, budget):
    """Smallest ``K`` with worst-first residual ``sum(z[K:]) <= budget``.

    Returns ``(K, achieved_residual)`` with ``K`` in ``0..N`` and the residual
    ``0.0`` at ``K == N``. Uses a descending suffix sum, so the result is the
    minimum ``K`` under the registered union-bound rule.
    """
    z = _check_spectrum(spectrum)
    budget = _check_budget(budget)
    n = int(z.size)
    order = np.sort(z)[::-1]
    suffix = np.cumsum(order[::-1])[::-1]
    k = int(np.searchsorted(-suffix, -budget, side="left"))
    residual = float(suffix[k]) if k < n else 0.0
    return k, residual


def allocation_budgets(source, allocation):
    """Per-layer FER budgets for one source and allocation."""
    if source not in FROZEN_SOURCES:
        raise ValueError(f"unknown source {source!r}")
    h1 = float(FROZEN_SOURCES[source]["h1"])
    h2 = float(FROZEN_SOURCES[source]["h2"])
    if allocation == "equal":
        return FER_BUDGET / 2.0, FER_BUDGET / 2.0
    if allocation == "entropy_proportional":
        total = h1 + h2
        return FER_BUDGET * h1 / total, FER_BUDGET * h2 / total
    raise ValueError(f"unknown allocation {allocation!r}")


def _check_calibration(k_operational, k_literal, max_abs_diff) -> None:
    if k_operational != CALIBRATION_K or k_literal != CALIBRATION_K:
        raise AssertionError(
            "R2-A03 calibration hard stop: N=256 epsilon=0.05 budget=1e-2 "
            f"must give K={CALIBRATION_K}, got operational={k_operational} "
            f"literal={k_literal}"
        )
    if not max_abs_diff <= 1e-15:
        raise AssertionError(
            "R2-A02 hard stop: operational vs literal spectrum max abs diff "
            f"{max_abs_diff!r} exceeds 1e-15"
        )


def verify_calibration() -> dict:
    """Reproduce the accepted single-layer K=43 calibration; raise on failure."""
    spectrum = erasure_spectrum(CALIBRATION_EPSILON, CALIBRATION_N)
    k_operational, residual = minimum_disclosure_count(spectrum, CALIBRATION_BUDGET)
    literal = np.asarray(
        literal_erasure_spectrum(CALIBRATION_EPSILON, CALIBRATION_N),
        dtype=np.float64,
    )
    max_abs_diff = float(np.max(np.abs(spectrum - literal)))
    k_literal, _ = minimum_disclosure_count(literal, CALIBRATION_BUDGET)
    _check_calibration(k_operational, k_literal, max_abs_diff)
    return {
        "n": CALIBRATION_N,
        "epsilon": CALIBRATION_EPSILON,
        "whole_block_fer_budget": CALIBRATION_BUDGET,
        "k_expected": CALIBRATION_K,
        "k_operational": k_operational,
        "k_literal_oracle": k_literal,
        "achieved_residual": residual,
        "operational_vs_literal_max_abs_diff": max_abs_diff,
        "pass": True,
    }


def source_epsilon(source):
    """``(epsilon_1, epsilon_2) = (H1/5, H2/5)`` for one frozen source."""
    if source not in FROZEN_SOURCES:
        raise ValueError(f"unknown source {source!r}")
    return (
        float(FROZEN_SOURCES[source]["h1"]) / BITS_PER_COORDINATE,
        float(FROZEN_SOURCES[source]["h2"]) / BITS_PER_COORDINATE,
    )


def _validate_table(rows) -> dict:
    expected_rows = len(FROZEN_SOURCES) * len(ALLOCATIONS) * len(N_EXPONENTS)
    seen = set()
    all_k_in_range = True
    all_finite = True
    for row in rows:
        n = row["n"]
        if not (0 <= row["k1"] <= n and 0 <= row["k2"] <= n):
            all_k_in_range = False
        for key in ("f", "f_no_tag", "nH", "residual_1", "residual_2",
                    "leakage_bits", "leakage_bits_no_tag", "budget_1", "budget_2"):
            if not np.isfinite(row[key]):
                all_finite = False
        seen.add((row["source"], row["allocation"], n))
    axes_complete = (
        len(seen) == expected_rows
        and len(rows) == expected_rows
        and {n for _, _, n in seen} == {2 ** k for k in N_EXPONENTS}
    )
    checks = {
        "rows": len(rows),
        "expected_rows": expected_rows,
        "all_k_in_range": bool(all_k_in_range),
        "all_finite": bool(all_finite),
        "axes_complete": bool(axes_complete),
    }
    if not (checks["all_k_in_range"] and checks["all_finite"] and checks["axes_complete"]):
        raise RuntimeError(f"R2 completeness/finite hard stop: {checks}")
    return checks


def run_analysis() -> dict:
    """Compute the full frozen sensitivity table (calibration first)."""
    calibration = verify_calibration()
    rows = []
    for source in FROZEN_SOURCES:
        h1 = float(FROZEN_SOURCES[source]["h1"])
        h2 = float(FROZEN_SOURCES[source]["h2"])
        eps1, eps2 = source_epsilon(source)
        for allocation in ALLOCATIONS:
            budget_1, budget_2 = allocation_budgets(source, allocation)
            for exponent in N_EXPONENTS:
                n = 2 ** exponent
                k1, residual_1 = minimum_disclosure_count(
                    erasure_spectrum(eps1, n), budget_1
                )
                k2, residual_2 = minimum_disclosure_count(
                    erasure_spectrum(eps2, n), budget_2
                )
                leakage_bits = BITS_PER_COORDINATE * (k1 + k2) + TAG_BITS
                leakage_bits_no_tag = BITS_PER_COORDINATE * (k1 + k2)
                nH = n * (h1 + h2)
                rows.append(
                    {
                        "source": source,
                        "allocation": allocation,
                        "exponent": exponent,
                        "n": n,
                        "k1": k1,
                        "k2": k2,
                        "k_total": int(k1 + k2),
                        "budget_1": budget_1,
                        "budget_2": budget_2,
                        "residual_1": residual_1,
                        "residual_2": residual_2,
                        "leakage_bits": int(leakage_bits),
                        "leakage_bits_no_tag": int(leakage_bits_no_tag),
                        "nH": nH,
                        "f": leakage_bits / nH,
                        "f_no_tag": leakage_bits_no_tag / nH,
                    }
                )
    checks = _validate_table(rows)

    crossing = {}
    for source in FROZEN_SOURCES:
        crossing[source] = {}
        for allocation in ALLOCATIONS:
            first = next(
                (
                    row
                    for row in rows
                    if row["source"] == source
                    and row["allocation"] == allocation
                    and row["f"] <= F_TARGET
                ),
                None,
            )
            if first is None:
                crossing[source][allocation] = None
                continue
            crossing[source][allocation] = {
                "first_n": first["n"],
                "first_exponent": first["exponent"],
                "f": first["f"],
                "f_no_tag": first["f_no_tag"],
                "k1": first["k1"],
                "k2": first["k2"],
                "leakage_bits": first["leakage_bits"],
            }

    return {
        "analysis": "nbpolar-phase6-r2-two-layer-rate-feasibility",
        "surrogate_disclaimer": SURROGATE_DISCLAIMER,
        "model": {
            "q": Q,
            "bits_per_coordinate": BITS_PER_COORDINATE,
            "tag_bits": TAG_BITS,
            "whole_block_fer_budget": FER_BUDGET,
            "f_target": F_TARGET,
            "recurrence": "z_minus=2z-z**2; z_plus=z**2; natural order",
            "minimum_k_rule": (
                "smallest K in 0..N with sum(z[K:]) <= budget_l after sorting "
                "z descending (suffix-sum based)"
            ),
            "entropy_to_erasure_mapping": "epsilon_l = H_l / 5",
            "allocations": {
                "equal": "budget_l = 0.01/2 per layer",
                "entropy_proportional": "budget_l = 0.01*H_l/(H1+H2)",
            },
            "leakage_formula": "leakage_bits = 5*(K1+K2)+64",
            "leakage_no_tag_formula": "leakage_bits_no_tag = 5*(K1+K2)",
            "nH_formula": "nH = N*(H1+H2)",
            "f_formula": "f = leakage_bits/nH",
            "f_no_tag_formula": "f_no_tag = leakage_bits_no_tag/nH",
            "n_values": [2 ** k for k in N_EXPONENTS],
        },
        "frozen_inputs": {
            "sources": {
                name: {
                    "h1": data["h1"],
                    "h2": data["h2"],
                    "epsilon_1": data["h1"] / BITS_PER_COORDINATE,
                    "epsilon_2": data["h2"] / BITS_PER_COORDINATE,
                    "provenance": data["provenance"],
                }
                for name, data in FROZEN_SOURCES.items()
            },
            "h2_note": H2_PROVENANCE_NOTE,
        },
        "calibration": calibration,
        "table": rows,
        "crossing": crossing,
        "checks": checks,
        "audit": L2_AUDIT,
        "successor_prerequisites": SUCCESSOR_PREREQUISITES,
    }


def _fmt(value) -> str:
    return f"{value:.12g}"


def _render_report(result: dict) -> str:
    model = result["model"]
    calibration = result["calibration"]
    lines = [
        "# Phase 6-R2 — two-layer BEC rate feasibility (surrogate planning estimate)",
        "",
        f"**Label**: {result['surrogate_disclaimer']}.",
        "",
        "Decoder-free analysis. No SC call, no artifact/parquet/TTBin read, no "
        "synthetic block sampling, no attempt/seed consumption; old evidence "
        "roots untouched.",
        "",
        "## 1. Method and formulas",
        "",
        f"- BEC recurrence: `{model['recurrence']}`.",
        f"- Per-layer erasure surrogate: `{model['entropy_to_erasure_mapping']}` "
        "(bits/symbol over the 5-bit GF32 plane).",
        f"- Minimum-K rule: {model['minimum_k_rule']}.",
        "- FER allocations: "
        + "; ".join(f"`{name}`: {rule}" for name, rule in model["allocations"].items())
        + ".",
        f"- Accounting: `{model['leakage_formula']}`, "
        f"`{model['leakage_no_tag_formula']}`, `{model['nH_formula']}`, "
        f"`{model['f_formula']}`, `{model['f_no_tag_formula']}`.",
        f"- Sensitivity axes: N = 2**8..2**18 (11 values) x "
        f"{len(result['frozen_inputs']['sources'])} sources x "
        f"{len(model['allocations'])} allocations; f target <= {model['f_target']}.",
        "",
        "## 2. Frozen inputs and provenance",
        "",
        "| source | H1 | H2 | epsilon_1 | epsilon_2 | CSV | doc |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, data in result["frozen_inputs"]["sources"].items():
        lines.append(
            f"| {name} | {data['h1']!r} | {data['h2']!r} | {data['epsilon_1']!r} "
            f"| {data['epsilon_2']!r} | {data['provenance']['csv']} "
            f"| {data['provenance']['diagnosis_doc']} |"
        )
    lines += [
        "",
        f"{result['frozen_inputs']['h2_note']}",
        "",
        "## 3. Calibration (R2-A03)",
        "",
        f"N={calibration['n']}, epsilon={calibration['epsilon']}, whole-block FER "
        f"budget={calibration['whole_block_fer_budget']} -> K={calibration['k_operational']} "
        f"(expected {calibration['k_expected']}), residual union bound "
        f"{calibration['achieved_residual']!r}; literal oracle K="
        f"{calibration['k_literal_oracle']}, max |operational-literal| "
        f"{calibration['operational_vs_literal_max_abs_diff']!r}. PASS.",
        "",
        "## 4. Full sensitivity table",
        "",
    ]
    for source in result["frozen_inputs"]["sources"]:
        for allocation in model["allocations"]:
            lines += [
                f"### {source} / {allocation}",
                "",
                "| k | N | K1 | K2 | residual_1 | residual_2 | leakage_bits | f | f_no_tag |",
                "|---|---|---|---|---|---|---|---|---|",
            ]
            for row in result["table"]:
                if row["source"] == source and row["allocation"] == allocation:
                    lines.append(
                        f"| {row['exponent']} | {row['n']} | {row['k1']} | {row['k2']} "
                        f"| {_fmt(row['residual_1'])} | {_fmt(row['residual_2'])} "
                        f"| {row['leakage_bits']} | {_fmt(row['f'])} "
                        f"| {_fmt(row['f_no_tag'])} |"
                    )
            lines.append("")
    lines += [
        "## 5. First N meeting f <= 1.3 per axis",
        "",
        "| source | allocation | first N | exponent | K1 | K2 | leakage_bits | f | f_no_tag |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for source, allocations in result["crossing"].items():
        for allocation, hit in allocations.items():
            if hit is None:
                lines.append(f"| {source} | {allocation} | none <= 2**18 | - | - | - | - | - | - |")
                continue
            lines.append(
                f"| {source} | {allocation} | {hit['first_n']} | {hit['first_exponent']} "
                f"| {hit['k1']} | {hit['k2']} | {hit['leakage_bits']} | {_fmt(hit['f'])} "
                f"| {_fmt(hit['f_no_tag'])} |"
            )
    checks = result["checks"]
    lines += [
        "",
        "## 6. Checks",
        "",
        f"- rows {checks['rows']} / expected {checks['expected_rows']}; "
        f"all_k_in_range={checks['all_k_in_range']}; all_finite={checks['all_finite']}; "
        f"axes_complete={checks['axes_complete']}.",
        "",
        "## 7. R2-A07 audit — L2 execution coverage",
        "",
        f"Claim: {result['audit']['claim']}.",
        "",
        "Code evidence:",
    ]
    lines += [f"- {item}" for item in result["audit"]["code_evidence"]]
    lines += ["", "Document evidence:"]
    lines += [f"- {item}" for item in result["audit"]["doc_evidence"]]
    lines += [
        "",
        f"Conclusion: {result['audit']['conclusion']}.",
        "",
        "## 8. R2-A09 successor prerequisites (decision output only)",
        "",
    ]
    lines += [f"- {item}" for item in result["successor_prerequisites"]]
    lines += [
        "",
        "_No OpenSpec task box is checked by this report; acceptance remains a "
        "main-thread decision. BEC figures are surrogate planning estimates, not "
        "real-channel performance or decoder evidence._",
        "",
    ]
    return "\n".join(lines)


def write_result_artifacts(result: dict, out_dir) -> dict:
    """Write exactly the two frozen result artifacts into ``out_dir``."""
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / OUTPUT_JSON_NAME
    report_path = directory / OUTPUT_REPORT_NAME
    json_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_path.write_text(_render_report(result), encoding="utf-8")
    return {"json": str(json_path), "report": str(report_path)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Decoder-free Phase 6-R2 two-layer BEC rate-feasibility analysis; "
            "writes two_layer_rate_sensitivity.json and R2_REPORT.md"
        )
    )
    parser.add_argument("--out-dir", required=True, help="existing packet queue directory")
    args = parser.parse_args(argv)
    result = run_analysis()
    paths = write_result_artifacts(result, args.out_dir)
    print(
        json.dumps(
            {
                "written": paths,
                "calibration_k": result["calibration"]["k_operational"],
                "checks": result["checks"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
