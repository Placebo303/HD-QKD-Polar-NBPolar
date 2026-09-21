"""Focused Phase-0 tests for the G1R2 (w=200 / CIRCULAR) contract routing.

Decoder-free, synthetic fixtures only. No .ttbin/real data, no decoder
call, no claim. Production data paths are NEVER invoked: every
in-process execution passes an explicit fake seam (``_read_timetags`` /
``_packet_dir``); the on-disk freeze-config is only READ. Written
without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments and uses
plain asserts. Run directly::

    python comparison_bench/tests/test_nbpolar_m2_g1r2_contract.py

Packet: NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR, delta item 8.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "m2_prior_validation.py"
G1R2_CONFIG = (
    REPO_ROOT / ".workbuddy" / "queue"
    / "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR" / "g1r2_freeze_config.json"
)


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "m2_prior_validation_g1r2_test", str(RUNNER)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = _load_runner()


@contextlib.contextmanager
def _tmp():
    """Temp dir under repo workspace/ (auto-cleaned; never outside)."""
    root = REPO_ROOT / "workspace" / ".tmp_g1r2"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="m2g1r2_", dir=str(root)) as td:
        yield Path(td)


def _expect_exit2(fn):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            fn()
    except SystemExit as exc:
        assert exc.code == 2, f"exit code {exc.code!r}, want 2"
        return buf.getvalue()
    raise AssertionError("did not exit(2)")


def _full_freeze(window):
    """Synthetic 19-key freeze selecting the given window contract."""
    cfg = json.loads(G1R2_CONFIG.read_text(encoding="utf-8"))
    cfg["pairing_window_primary"] = window
    if window == 500:
        cfg["pairing_window_sensitivity"] = 200
        cfg["mod_boundary"] = "LINEAR_ONLY"
        cfg["tag_master"] = 2026102201
    return cfg


def _closure_fixtures(window, n_pairs, n_frames, n_postskip):
    freeze = _full_freeze(window)
    align = {
        "peak_center_ps": 50,
        "peak_sigma_ps": 112.45189572400645,
        "peak_to_bg": 1366.27,
        "status": "ok",
    }
    sweep = {"yield_at_derived": 7, "yield_max": 7, "yield_max_ok": True}
    pairing = {
        "rule": "(N) narrow nearest-unique",
        "window": window,
        "offset_ps": 50,
        "n_pairs": n_pairs,
        "n_frames": n_frames,
        "tier": "FULL",
        "frozen": {"d": 1024, "bin_width_ps": 200,
                   "period_ps": 204800, "frame_pairs": 256},
    }
    ledger = {"complete_frames": n_postskip}
    segments = m.segment_frame_lists(n_postskip)
    named = {name: segments[name] for name, _, _ in m.SEG_RANGES}
    matrix = m.disjointness_matrix(
        {k: named[k] for k in ("a1_cal", "cal32", "char", "heldout", "eval")}
    )
    return freeze, align, sweep, pairing, ledger, named, matrix


# ------------------------------------------------------- R1/R2 selection

def test_R1_contract_selection_g1_legacy():
    for w in (500, "500"):
        c = m.contract_for_window(w)
        assert c["repro_gate"] is m.REPRO_GATE, "G1 must keep the legacy gate object"
        assert c["repro_gate"]["n_pairs"] == 1269268, c["repro_gate"]
        assert c["repro_gate"]["n_frames"] == 4958, c["repro_gate"]
        assert c["packet_dir"] == m.G1_PACKET_DIR, c["packet_dir"]
        assert c["config_name"] == "g1_freeze_config.json", c["config_name"]
        assert c["label"] == "G1", c["label"]
        assert c["packet"] == "NBPOLAR-M2-PRIOR-G1-REALDATA-NLL", c["packet"]
        assert c["science_mode"] == "g1-science", c["science_mode"]
    # Alignment literals shared.
    assert m.REPRO_GATE["peak_center_ps"] == 50
    assert m.REPRO_GATE["peak_sigma_ps"] == 112.45189572400645
    assert m.REPRO_GATE["status"] == "ok"


def test_R2_contract_selection_g1r2():
    for w in (200, "200"):
        c = m.contract_for_window(w)
        assert c["repro_gate"] is m.REPRO_GATE_G1R2
        assert c["repro_gate"]["n_pairs"] == 1259992, c["repro_gate"]
        assert c["repro_gate"]["n_frames"] == 4921, c["repro_gate"]
        assert c["packet_dir"] == m.G1R2_PACKET_DIR, c["packet_dir"]
        assert c["packet_dir"].name == "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR"
        assert c["config_name"] == "g1r2_freeze_config.json", c["config_name"]
        assert c["label"] == "G1R2", c["label"]
        assert c["packet"] == "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR", c["packet"]
        assert c["science_mode"] == "g1r2-science", c["science_mode"]
    # Alignment literals shared with G1.
    assert m.REPRO_GATE_G1R2["peak_center_ps"] == 50
    assert m.REPRO_GATE_G1R2["peak_sigma_ps"] == 112.45189572400645
    assert m.REPRO_GATE_G1R2["status"] == "ok"
    # Freeze-keyed selection (never data-inferred).
    assert m.contract_for_freeze({"pairing_window_primary": 200})["label"] == "G1R2"
    assert m.contract_for_freeze({"pairing_window_primary": 500})["label"] == "G1"


def test_R3_unknown_window_exit2_never_default():
    for bad in (300, 0, -1, None, "abc", ""):
        err = _expect_exit2(lambda b=bad: m.contract_for_window(b))
        assert "no science contract" in err, f"{bad!r}: {err.strip()}"
    err = _expect_exit2(lambda: m.contract_for_freeze({}))
    assert "no science contract" in err, err.strip()


# ------------------------------------------------------- R4 reserve

def test_R4_reserve_ledger_driven():
    # G1 ledger reproduces the legacy SEG_RESERVE range exactly.
    r500 = m.reserve_ids_for_ledger(4256)
    assert r500["ids"] == list(range(4190, 4256)) == \
        list(range(m.SEG_RESERVE[1], m.SEG_RESERVE[2] + 1)), r500
    assert len(r500["ids"]) == 66 and r500["note"] == ""
    # G1R2 ledger stops at 4218 — never emits 4219+.
    r200 = m.reserve_ids_for_ledger(4219)
    assert r200["ids"] == list(range(4190, 4219)), r200
    assert len(r200["ids"]) == 29 and r200["ids"][-1] == 4218
    assert all(i < 4219 for i in r200["ids"]) and r200["note"] == ""
    # At/below the allocation: empty reserve + recorded note, never invented.
    for n in (4190, 4189, 0):
        r = m.reserve_ids_for_ledger(n)
        assert r["ids"] == [] and "never invented" in r["note"], (n, r)


# ------------------------------------------------------- R5 G1 legacy intact

def test_R5_g1_legacy_literals_intact():
    assert m.REPRO_GATE == {
        "peak_center_ps": 50,
        "peak_sigma_ps": 112.45189572400645,
        "status": "ok",
        "n_pairs": 1269268,
        "n_frames": 4958,
    }, m.REPRO_GATE
    assert m.SEG_RESERVE == ("reserve", 4190, 4255), m.SEG_RESERVE
    assert m.G1_PACKET_DIR.name == "NBPOLAR-M2-PRIOR-G1-REALDATA-NLL"
    assert m.ALLOCATED_FRAMES == 4190


# ------------------------------------------------------- R6/R7 closure routing

def test_R6_closure_outputs_g1r2_labels_routed_fake_packet_dir():
    freeze, align, sweep, pairing, ledger, named, matrix = _closure_fixtures(
        200, 1259992, 4921, 4219)
    with _tmp() as tmp:
        out_root = tmp / "out"
        fake_packet = tmp / "packet"
        # Snapshot production configs: this test must not touch them.
        before = {}
        for p in (m.G1_PACKET_DIR / "g1_freeze_config.json", G1R2_CONFIG):
            before[p] = p.read_bytes() if p.is_file() else None
        g1 = m._closure_outputs(
            acq_id="SYNTH", out_root=out_root, freeze=freeze, align=align,
            sweep=sweep, pairing=pairing, ledger=ledger, segments=named,
            matrix=matrix, elapsed_s=1.0, _packet_dir=fake_packet)
        assert g1["packet"] == "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR", g1["packet"]
        assert g1["mode"] == "closure-only", g1["mode"]
        assert g1["reproduction_gate"]["expected"]["n_pairs"] == 1259992
        assert g1["reproduction_gate"]["match5"] is True
        got = json.loads((out_root / "g1.json").read_text(encoding="utf-8"))
        assert got["packet"] == "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR"
        cal = json.loads((out_root / "cal_ids.json").read_text(encoding="utf-8"))
        assert cal["reserve_frame_ids"] == list(range(4190, 4219)), cal["reserve_frame_ids"][-3:]
        assert all(i < 4219 for i in cal["reserve_frame_ids"])
        assert cal["reserve_note"] == ""
        log = (out_root / "run_log.md").read_text(encoding="utf-8")
        assert log.splitlines()[0] == (
            "# G1R2 Phase-A closure run log — NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR"), log.splitlines()[0]
        assert "reserve 4190-4218" in log, log
        assert "reserve 4190-4255" not in log, log
        emitted = fake_packet / "g1r2_freeze_config.json"
        assert emitted.is_file(), "must route to the successor packet dir name"
        cfg = json.loads(emitted.read_text(encoding="utf-8"))
        assert m._missing_freeze_keys(cfg) == [], m._missing_freeze_keys(cfg)
        assert cfg["cal_frame_ids"] == list(range(1024, 1056))
        assert cfg["heldout_frame_ids"] == list(range(1838, 2398))
        assert cfg["a1_cal_ids"] == list(range(0, 1024))
        # Production packet dirs untouched by this test.
        for p, blob in before.items():
            after = p.read_bytes() if p.is_file() else None
            assert after == blob, f"production file touched: {p}"


def test_R7_closure_outputs_g1_labels_reproduce_fake_packet_dir():
    freeze, align, sweep, pairing, ledger, named, matrix = _closure_fixtures(
        500, 1269268, 4958, 4256)
    with _tmp() as tmp:
        out_root = tmp / "out"
        fake_packet = tmp / "packet"
        g1 = m._closure_outputs(
            acq_id="SYNTH", out_root=out_root, freeze=freeze, align=align,
            sweep=sweep, pairing=pairing, ledger=ledger, segments=named,
            matrix=matrix, elapsed_s=1.0, _packet_dir=fake_packet)
        assert g1["packet"] == "NBPOLAR-M2-PRIOR-G1-REALDATA-NLL", g1["packet"]
        assert g1["reproduction_gate"]["expected"]["n_pairs"] == 1269268
        assert g1["reproduction_gate"]["match5"] is True
        cal = json.loads((out_root / "cal_ids.json").read_text(encoding="utf-8"))
        assert cal["reserve_frame_ids"] == list(range(4190, 4256)), len(cal["reserve_frame_ids"])
        log = (out_root / "run_log.md").read_text(encoding="utf-8")
        assert log.splitlines()[0] == (
            "# G1 Phase-A closure run log — NBPOLAR-M2-PRIOR-G1-REALDATA-NLL"), log.splitlines()[0]
        assert "reserve 4190-4255" in log, log
        emitted = fake_packet / "g1_freeze_config.json"
        assert emitted.is_file(), "G1 must still route to its legacy config name"
        cfg = json.loads(emitted.read_text(encoding="utf-8"))
        assert m._missing_freeze_keys(cfg) == []


# ------------------------------------------------------- R8 on-disk config

def test_R8_on_disk_g1r2_config_exact_values():
    cfg = m.load_freeze_config(G1R2_CONFIG)
    assert m._missing_freeze_keys(cfg) == []
    assert cfg["B_tail"] == 2.0e-4 and cfg["delta_min"] == 0.020
    assert cfg["pairing_window_primary"] == 200
    assert cfg["pairing_window_sensitivity"] == 500
    assert cfg["skip_frames"] == 702
    assert cfg["mod_boundary"] == "CIRCULAR"
    assert cfg["tag_master"] == 2026103001
    assert cfg["char_sample_pairs"] == 200192 and cfg["g2_blocks"] == 14
    assert cfg["cal_split_rule"] == (
        "RULE-FIT32-SCORE-HELDOUT: fit all 32, score disjoint held-out, seed N/A")
    assert cfg["g2_success_rule"] == (
        "Wilson-lower(B) > Wilson-upper(A2), strict non-overlap, z=1.96")
    assert cfg["g2_inconclusive_rule"] == (
        "point(B) > point(A2) but CIs overlap => bounded negative")
    assert cfg["g2_fail_rule"] == "point(B) <= point(A2)"
    assert cfg["block_formation_fallback"] == (
        "COMPLETE-BLOCKS-ONLY, else INSUFFICIENT=>INCONCLUSIVE (never pad/reuse/shrink)")
    assert cfg["g2_arms"] == ["A1_M0_1024f_incumbent", "A2_M0_32f_matched",
                              "B_M2_32f_candidate"]
    assert cfg["a1_cal_ids"] == list(range(0, 1024))
    assert cfg["cal_frame_ids"] == list(range(1024, 1056))
    assert cfg["heldout_frame_ids"] == list(range(1838, 2398))
    mx = cfg["disjointness_matrix"]
    assert mx["all_disjoint"] is True and len(mx["pairwise_overlap"]) == 10
    assert all(v == 0 for v in mx["pairwise_overlap"].values()), mx


# ------------------------------------------------------- R9 mechanics unchanged

def test_R9_inherited_mechanics_unchanged():
    full = {k: f"value-{k}" for k in m.REQUIRED_FREEZE_KEYS}
    assert len(m.REQUIRED_FREEZE_KEYS) == 19
    # 19-key enforcement: null/absent => exit 2, never a default.
    assert m._missing_freeze_keys(full) == []
    bad = dict(full)
    bad["pairing_window_primary"] = None
    assert m._missing_freeze_keys(bad) == ["pairing_window_primary"]
    # --authorized gate.
    err = _expect_exit2(lambda: m._require_authorized(False))
    assert "--authorized" in err
    m._require_authorized(True)
    # Flag<->key cross-check still catches a window mismatch.
    mism = m._cross_check_mismatches({"window_primary": "200"}, dict(full))
    assert len(mism) == 1 and "pairing_window_primary" in mism[0], mism
    # K pin 319/6492.
    m._check_k_pin("319", "6492")
    err = _expect_exit2(lambda: m._check_k_pin("319", "6493"))
    assert "6492" in err, err.strip()
    # Out-root confinement: workspace-only + forbidden trees.
    assert m._out_root_workspace_refusal(REPO_ROOT / "workspace" / "x") is None
    assert m._out_root_workspace_refusal(REPO_ROOT / "results" / "x") is not None
    assert m._out_root_refusal(REPO_ROOT / "results" / "x") is not None
    assert m._out_root_refusal(
        REPO_ROOT / "comparison_bench" / "outputs_comparison" / "y") is not None
    # --closure-only store_true + import purity + entry shape (AST).
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    found_closure = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument":
            names = [a.value for a in node.args
                     if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            if "--closure-only" in names:
                kw = {k.arg: k.value for k in node.keywords}
                assert isinstance(kw["action"], ast.Constant) and kw["action"].value == "store_true"
                found_closure = True
    assert found_closure, "--closure-only argument missing"
    src = RUNNER.read_text(encoding="utf-8")
    assert src.index("sys.path.insert") < src.index('sys.modules.setdefault("TimeTagger"')
    assert "def main(argv=None)" in src and '__main__' in src
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for modname in mods:
                assert modname.split(".")[0] not in (
                    "TimeTagger", "Swabian", "src", "scripts",
                    "nbpolar", "comparison_bench", "pandas", "scipy"), modname


# ------------------------------------------------------- R10 science body contract-driven (static)

def test_R10_science_body_no_g1_hardcode():
    src = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    bodies = {n.name: ast.get_source_segment(src, n)
              for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for fname in ("run_closure", "run_g1_science", "_closure_outputs"):
        body = bodies[fname]
        assert body is not None, fname
        assert "NBPOLAR-M2-PRIOR-G1-REALDATA-NLL" not in body, (
            f"{fname} still hardcodes the G1 packet label")
        assert "REPRO_GATE[" not in body and "dict(REPRO_GATE)" not in body, (
            f"{fname} still references the legacy gate directly")
    assert 'contract["packet"]' in bodies["run_g1_science"]
    assert 'contract["science_mode"]' in bodies["run_g1_science"]
    assert "contract_for_freeze" in bodies["run_g1_science"]
    assert "contract_for_freeze" in bodies["run_closure"]
    assert "reserve_ids_for_ledger" in bodies["_closure_outputs"]


if __name__ == "__main__":
    names = sorted(n for n in list(globals()) if n.startswith("test_"))
    failures = []
    for name in names:
        try:
            globals()[name]()
        except AssertionError as exc:
            failures.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")
        except Exception as exc:
            failures.append(f"{name}: unexpected {type(exc).__name__}: {exc}")
            print(f"FAIL {name}: unexpected {type(exc).__name__}: {exc}")
        else:
            print(f"PASS {name}")
    print(f"{len(names) - len(failures)}/{len(names)} passed")
    raise SystemExit(1 if failures else 0)
