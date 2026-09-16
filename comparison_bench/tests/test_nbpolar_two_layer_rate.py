"""Focused Phase 6-R2 two-layer rate tests (R2-A02..A06 + scope checks).

Decoder-free analysis only: no SC/decoder call, no artifact/parquet/TTBin read,
no synthetic block sampling, no attempt/seed consumption. Temporary output is
confined to pytest temp directories.

Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments and uses plain
asserts.
"""

from __future__ import annotations

import ast
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    two_layer_rate as tlr,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.synthetic import (
    analytic_erasure_probs,
)

MODULE_PATH = Path(tlr.__file__).resolve()
REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_H = {
    "1M": (0.02428054681872374, 0.7767572780789994),
    "1p5M": (0.02519949687789926, 0.8003665547438703),
    "2M": (0.025662048796915037, 0.8069006731253232),
}

_RESULT = None


def _result():
    global _RESULT
    if _RESULT is None:
        _RESULT = tlr.run_analysis()
    return _RESULT


def _expect_error(fn, exc_type=Exception):
    try:
        fn()
    except exc_type:
        return True
    raise AssertionError(f"expected {exc_type.__name__}")


def _brute_min_k(spectrum, budget):
    z = sorted((float(v) for v in spectrum), reverse=True)
    for k in range(len(z) + 1):
        if sum(z[k:]) <= budget:
            return k
    raise AssertionError("brute force should always terminate at K=N")


def test_recurrence_matches_literal_oracle():
    for n in (1, 2, 4, 8):
        for epsilon in (0.0, 1.0, 1e-6, 0.05, 0.5):
            got = tlr.erasure_spectrum(epsilon, n)
            literal = np.asarray(tlr.literal_erasure_spectrum(epsilon, n))
            assert got.shape == (n,)
            assert literal.shape == (n,)
            assert float(np.max(np.abs(got - literal))) == 0.0
    assert np.array_equal(tlr.erasure_spectrum(0.0, 4), np.zeros(4))
    assert np.array_equal(tlr.erasure_spectrum(1.0, 4), np.ones(4))
    assert np.array_equal(tlr.erasure_spectrum(0.05, 2), np.array([2 * 0.05 - 0.05**2, 0.05**2]))


def test_operational_matches_accepted_recurrence():
    for n in (2, 16, 256):
        for epsilon in (0.0, 1e-6, 0.05, 1.0):
            diff = float(
                np.max(
                    np.abs(
                        tlr.erasure_spectrum(epsilon, n)
                        - analytic_erasure_probs(epsilon, n)
                    )
                )
            )
            assert diff <= 1e-15
    diff = float(
        np.max(
            np.abs(
                tlr.erasure_spectrum(0.05, 256)
                - analytic_erasure_probs(0.05, 256)
            )
        )
    )
    assert diff <= 1e-15


def test_minimum_k_matches_brute_force_and_edges():
    for n in (1, 2, 4, 8, 16):
        for epsilon in (0.03, 0.1, 0.5):
            z = tlr.erasure_spectrum(epsilon, n)
            for budget in (0.0, 1e-3, 1e-2, 0.1, 0.5, 10.0):
                k, residual = tlr.minimum_disclosure_count(z, budget)
                assert 0 <= k <= n
                assert k == _brute_min_k(z, budget)
                assert abs(residual - float(np.sum(np.sort(z)[::-1][k:]))) <= 1e-15
    k, residual = tlr.minimum_disclosure_count([0.5, 0.0, 0.0], 0.0)
    assert (k, residual) == (1, 0.0)
    k, residual = tlr.minimum_disclosure_count([0.5, 0.25], 10.0)
    assert (k, residual) == (0, 0.75)
    _expect_error(lambda: tlr.minimum_disclosure_count([0.5, 1.5], 0.1), ValueError)
    _expect_error(lambda: tlr.minimum_disclosure_count(np.array([]), 0.1), ValueError)
    _expect_error(lambda: tlr.minimum_disclosure_count([0.5], -0.1), ValueError)


def test_calibration_k43_hard_assert():
    spectrum = tlr.erasure_spectrum(0.05, 256)
    k, residual = tlr.minimum_disclosure_count(spectrum, 1e-2)
    assert k == 43
    assert residual <= 1e-2
    sorted_desc = np.sort(spectrum)[::-1]
    assert float(np.sum(sorted_desc[42:])) > 1e-2  # K=42 must miss the budget
    calibration = tlr.verify_calibration()
    assert calibration["pass"] is True
    assert calibration["k_operational"] == 43
    assert calibration["k_literal_oracle"] == 43
    assert calibration["operational_vs_literal_max_abs_diff"] <= 1e-15
    tlr._check_calibration(43, 43, 0.0)
    _expect_error(lambda: tlr._check_calibration(42, 42, 0.0), AssertionError)
    _expect_error(lambda: tlr._check_calibration(43, 44, 0.0), AssertionError)
    _expect_error(lambda: tlr._check_calibration(43, 43, 1e-14), AssertionError)


def test_two_layer_arithmetic_hand_computed():
    result = _result()
    row = next(
        r for r in result["table"]
        if r["source"] == "1M" and r["allocation"] == "equal" and r["n"] == 256
    )
    h1, h2 = FROZEN_H["1M"]
    assert row["k1"] == 10 and row["k2"] == 94
    assert row["leakage_bits"] == 5 * (10 + 94) + 64
    assert row["leakage_bits_no_tag"] == 5 * (10 + 94)
    assert row["nH"] == 256 * (h1 + h2)
    assert row["f"] == row["leakage_bits"] / row["nH"]
    assert row["f_no_tag"] == row["leakage_bits_no_tag"] / row["nH"]
    assert row["budget_1"] == row["budget_2"] == 0.01 / 2
    assert math.isclose(row["f"], 2.847868, rel_tol=1e-6)
    proportional = next(
        r for r in result["table"]
        if r["source"] == "2M" and r["allocation"] == "entropy_proportional" and r["n"] == 256
    )
    h1, h2 = FROZEN_H["2M"]
    assert math.isclose(proportional["budget_1"], 0.01 * h1 / (h1 + h2), rel_tol=1e-15)
    assert math.isclose(proportional["budget_2"], 0.01 * h2 / (h1 + h2), rel_tol=1e-15)
    assert math.isclose(proportional["budget_1"] + proportional["budget_2"], 0.01, rel_tol=1e-15)
    for r in result["table"]:
        assert 0 < r["f_no_tag"] < r["f"]  # the 64-bit tag is counted once


def test_axes_complete_and_all_finite():
    result = _result()
    assert result["checks"] == {
        "rows": 66,
        "expected_rows": 66,
        "all_k_in_range": True,
        "all_finite": True,
        "axes_complete": True,
    }
    seen = set()
    for row in result["table"]:
        seen.add((row["source"], row["allocation"], row["n"]))
        assert 0 <= row["k1"] <= row["n"]
        assert 0 <= row["k2"] <= row["n"]
        assert row["leakage_bits"] == 5 * (row["k1"] + row["k2"]) + 64
        for key in ("f", "f_no_tag", "nH", "residual_1", "residual_2", "budget_1", "budget_2"):
            assert np.isfinite(row[key])
    for source in FROZEN_H:
        for allocation in tlr.ALLOCATIONS:
            for exponent in tlr.N_EXPONENTS:
                assert (source, allocation, 2 ** exponent) in seen


def test_first_crossing_present_and_monotone():
    result = _result()
    for source in FROZEN_H:
        for allocation in tlr.ALLOCATIONS:
            hit = result["crossing"][source][allocation]
            assert hit is not None
            assert hit["f"] <= 1.3
            assert hit["first_n"] == 2 ** hit["first_exponent"]
            if hit["first_exponent"] > 8:
                previous = next(
                    r for r in result["table"]
                    if r["source"] == source
                    and r["allocation"] == allocation
                    and r["exponent"] == hit["first_exponent"] - 1
                )
                assert previous["f"] > 1.3


def test_module_source_has_no_decoder_or_rng():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    forbidden = {"sc", "oracle", "protocol", "empirical", "random"}
    for name in modules:
        assert not (set(name.split(".")) & forbidden), name
    assert "np.random" not in source
    assert "numpy.random" not in source
    assert "default_rng" not in source
    assert "RandomState" not in source


def test_import_writes_nothing():
    code = (
        "import sys; sys.path.insert(0, r'%s'); "
        "from comparison_bench.src.comparison_bench.formal_ir.nbpolar "
        "import two_layer_rate as t; print(t.CALIBRATION_K)" % REPO_ROOT
    )
    with tempfile.TemporaryDirectory() as tmp:
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=tmp,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert completed.returncode == 0, completed.stderr
        assert completed.stdout.strip() == "43"
        assert list(Path(tmp).iterdir()) == []


def test_result_artifact_schema_and_exactly_two_files():
    result = _result()
    with tempfile.TemporaryDirectory() as tmp:
        paths = tlr.write_result_artifacts(result, tmp)
        names = sorted(p.name for p in Path(tmp).iterdir())
        assert names == ["R2_REPORT.md", "two_layer_rate_sensitivity.json"]
        data = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
        for key in (
            "analysis",
            "surrogate_disclaimer",
            "model",
            "frozen_inputs",
            "calibration",
            "table",
            "crossing",
            "checks",
            "audit",
            "successor_prerequisites",
        ):
            assert key in data, key
        assert data["surrogate_disclaimer"] == tlr.SURROGATE_DISCLAIMER
        assert "not a rigorous lower bound" in data["surrogate_disclaimer"]
        assert "not decoder evidence" in data["surrogate_disclaimer"]
        assert len(data["table"]) == 66
        assert all(
            hit is not None
            for allocations in data["crossing"].values()
            for hit in allocations.values()
        )
        assert data["frozen_inputs"]["sources"]["1M"]["h1"] == FROZEN_H["1M"][0]
        assert "epsilon_l = H_l / 5" in data["model"]["entropy_to_erasure_mapping"]
        report = Path(paths["report"]).read_text(encoding="utf-8")
        assert tlr.SURROGATE_DISCLAIMER in report
        assert "R2-A07" in report and "R2-A09" in report
        assert "## 3. Calibration (R2-A03)" in report
