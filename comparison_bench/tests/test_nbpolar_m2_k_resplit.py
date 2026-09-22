"""Focused D4 tests for packet NBPOLAR-M2-PRIOR-K-RESPLIT-D4.

REPORT ONLY - ADOPTS NEITHER BRANCH. Synthetic fixtures only; no
protected/real data read; no genie/decoder call anywhere here (hand-built
e/h vectors only - test-only paths never touch a real runner).

Written without a pytest dependency so it runs under plain ``python`` and
is still collected by pytest: every ``test_*`` takes no arguments and uses
plain asserts.

Covers D4-A (branch arithmetic incl. the R5 6946 tolerance), D4-B (frozen
selector provenance + k_total required/no-literal), D4-C (this file, green),
D4-D (no protected contact, no adoption language, H-proportional
non-selecting).
"""

from __future__ import annotations

import inspect
import json
import sys
from math import floor
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_scaling import (  # noqa: E402
    select_empirical_split,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "workspace" / "m2_prior_validation" / "k_resplit_d4"
RESULTS = OUT_DIR / "results.json"
REPORT = OUT_DIR / "report.md"
DRIVER = OUT_DIR / "derive_k_resplit.py"

N = 32768
H_M2 = 0.8168138204133305
EXPECTED_SEEDS = list(range(2026100101, 2026100116 + 1))


def literal_empirical_split(n, e1, h1, e2, h2, k_total):
    """Literal enumeration replay of the frozen split semantics."""
    e1 = [float(v) for v in e1]
    h1 = [float(v) for v in h1]
    e2 = [float(v) for v in e2]
    h2 = [float(v) for v in h2]
    o1 = sorted(range(n), key=lambda i: (-e1[i], -h1[i], i))
    o2 = sorted(range(n), key=lambda i: (-e2[i], -h2[i], i))
    best = None
    lo, hi = max(0, k_total - n), min(n, k_total)
    for k1 in range(lo, hi + 1):
        k2 = k_total - k1
        residual = sum(e1[i] for i in o1[k1:]) + sum(e2[i] for i in o2[k2:])
        key = (residual, k1, k2)
        if best is None or key < best[0]:
            best = (key, k1, k2, residual)
    return best[1], best[2], best[3]


def test_selector_replay_handbuilt_vectors():
    # Hand-built vectors with ties to exercise the (e, h, index) tie-break.
    n = 8
    e1 = [0.5, 0.1, 0.5, 0.0, 0.9, 0.1, 0.9, 0.3]
    h1 = [1.0, 2.0, 0.5, 0.0, 1.0, 2.0, 0.5, 3.0]
    e2 = [0.0, 0.7, 0.7, 0.2, 0.2, 0.8, 0.8, 0.4]
    h2 = [0.0, 1.5, 1.0, 4.0, 0.5, 2.0, 2.0, 1.0]
    for k_total in (0, 1, 5, 8, 15, 16):
        got = select_empirical_split(n, e1, h1, e2, h2, k_total)
        k1, k2, residual = literal_empirical_split(n, e1, h1, e2, h2, k_total)
        assert (got["k1"], got["k2"]) == (k1, k2), (k_total, got, (k1, k2))
        assert got["residual"] == residual, (k_total, got["residual"], residual)
        assert got["k1"] + got["k2"] == k_total


def test_branch_arithmetic_and_r5_tolerance():
    nh = N * H_M2
    assert nh == 26765.355267304014
    assert 1.3 * nh == 34794.96184749522
    assert floor((1.3 * nh - 64) / 5) == 6946
    for k, want in ((6811, 1.2747449), (6946, 1.2999641), (7020, 1.3137879)):
        f = (5 * k + 64) / nh
        assert round(f, 7) == want, (k, f)
    # R5: 6946 does NOT close to exactly 1.3 - deviation must survive.
    dev = (5 * 6946 + 64) / nh - 1.3
    assert dev != 0.0
    assert abs(dev - (-3.593628724951614e-05)) < 1e-12, dev
    payload = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert payload["arithmetic"]["branch_A_K_total"] == 6946
    assert payload["arithmetic"]["branch_B_f"]["6946"] == (5 * 6946 + 64) / nh
    assert "1.2999641" in REPORT.read_text(encoding="utf-8")


def test_k_total_required_no_literal():
    sig = inspect.signature(select_empirical_split)
    assert "k_total" in sig.parameters
    assert sig.parameters["k_total"].default is inspect.Parameter.empty
    src = DRIVER.read_text(encoding="utf-8")
    assert "def select_empirical_split" not in src
    for lit in ("6811", "6946", "7020"):
        assert f"h2_mean, {lit})" not in src, f"baked-in literal {lit}"


def test_import_provenance_not_reimplemented():
    src = DRIVER.read_text(encoding="utf-8")
    assert "empirical_genie_scaling import" in src
    assert "select_empirical_split" in src
    assert "def select_empirical_split" not in src
    assert "def residual_for_orders" not in src
    payload = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert payload["frozen_selector_provenance"]["reimplemented"] is False
    assert "empirical_genie_scaling.select_empirical_split" in (
        payload["frozen_selector_provenance"]["import"]
    )


def test_h_proportional_non_selecting_only():
    text = REPORT.read_text(encoding="utf-8")
    assert "NON-SELECTING" in text
    assert "BANNED as a selection rule" in text
    lowered = text.lower()
    for phrase in ("selected h-proportional", "h-proportional select",
                   "adopt the h-proportional", "use the h-proportional k"):
        assert phrase not in lowered, phrase
    payload = json.loads(RESULTS.read_text(encoding="utf-8"))
    for tag, cell in payload["splits"].items():
        note = cell["h_proportional_contrast_NON_SELECTING"]["note"]
        assert "never used to select" in note.lower(), (tag, note)


def test_no_protected_contact_no_adoption():
    payload = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert payload["protected_data_contact"] is False
    assert payload["synthetic_genie_train"]["genie_calls_registered"] == 32
    assert payload["synthetic_genie_train"]["blocks"] == 16
    assert payload["synthetic_genie_train"]["seeds"] == EXPECTED_SEEDS
    src = DRIVER.read_text(encoding="utf-8")
    for token in (".ttbin", "outputs_comparison", "load_v25_channel_counts",
                  "HD-QKD_Polar_Comparison\"", "results/"):
        assert token not in src, token
    text = REPORT.read_text(encoding="utf-8")
    assert "ADOPTS NEITHER" in text
    lowered = text.lower()
    for phrase in ("we adopt", "hereby adopt", "adopted the", "decision made",
                   "is chosen", "chosen branch", "selected branch",
                   "shall use k", "we claim", "is qualified",
                   "qualification passed", "claim is confirmed"):
        assert phrase not in lowered, phrase


if __name__ == "__main__":
    tests = sorted(
        (name, obj) for name, obj in globals().items()
        if name.startswith("test_") and callable(obj)
    )
    failed = 0
    for name, fn in tests:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - plain runner reports, never hides
            failed += 1
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")
        else:
            print(f"PASS {name}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
