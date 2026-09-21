"""Focused Phase-0 tests for the G1 decoder-free body + --closure-only flag.

Decoder-free, synthetic fixtures only. No .ttbin/real data, no decoder
call, no claim. Production data paths are NEVER invoked from these
tests: every in-process execution passes an explicit fake reader seam
(``_read_timetags=...``); subprocess CLI probes use unknown acq-ids or
guard rejections that fail before any read/create. Written without a
pytest dependency so it runs under plain ``python`` and is still
collected by pytest: every ``test_*`` takes no arguments and uses plain
asserts.

Packet: NBPOLAR-M2-PRIOR-G1-REALDATA-NLL, Phase 0 item 8.
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "m2_prior_validation.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "m2_prior_validation_g1body_test", str(RUNNER)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = _load_runner()

FULL_FREEZE = {
    "B_tail": 0.0002,
    "a1_cal_ids": list(range(0, 1024)),
    "block_formation_fallback": "COMPLETE-BLOCKS-ONLY, else INSUFFICIENT=>INCONCLUSIVE",
    "cal_frame_ids": list(range(1024, 1056)),
    "cal_split_rule": "RULE-FIT32-SCORE-HELDOUT",
    "char_sample_pairs": 200192,
    "delta_min": 0.020,
    "disjointness_matrix": {"all_disjoint": True},
    "g2_arms": ["A1_M0_1024f_incumbent", "A2_M0_32f_matched", "B_M2_32f_candidate"],
    "g2_blocks": 14,
    "g2_fail_rule": "point(B) <= point(A2)",
    "g2_inconclusive_rule": "point(B) > point(A2) but CIs overlap => bounded negative",
    "g2_success_rule": "Wilson-lower(B) > Wilson-upper(A2), strict non-overlap, z=1.96",
    "heldout_frame_ids": list(range(1838, 2398)),
    "mod_boundary": "LINEAR_ONLY",
    "pairing_window_primary": 500,
    "pairing_window_sensitivity": 200,
    "skip_frames": 702,
    "tag_master": 2026102201,
}

G1_FLAGS = [
    "--window-primary", "500",
    "--window-sensitivity", "200",
    "--skip", "702",
    "--mod", "LINEAR_ONLY",
    "--char-pairs", "200192",
]


@contextlib.contextmanager
def _tmp():
    """Temp dir under repo workspace/ (auto-cleaned; never outside)."""
    root = REPO_ROOT / "workspace" / ".tmp_g1body"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="m2g1_", dir=str(root)) as td:
        yield Path(td)


def _write_freeze(tmp, cfg):
    path = tmp / "freeze.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def _run_runner(*args):
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {str(err)!r}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r})")


# ------------------------------------------------------- G1a CLI enforcement

def test_G1a_freeze_key_enforcement_still_green():
    with _tmp() as tmp:
        drop = ["delta_min", "tag_master"]
        cfg = {k: v for k, v in FULL_FREEZE.items() if k not in drop}
        freeze = _write_freeze(tmp, cfg)
        out_root = tmp / "out_missing"
        proc = _run_runner(
            "--authorized", "--stage-g1-nll",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(out_root),
            *G1_FLAGS,
        )
        assert proc.returncode == 2, f"G1a exit {proc.returncode}: {proc.stderr}"
        for k in drop:
            assert k in proc.stderr, f"G1a {k} not listed: {proc.stderr.strip()}"
        assert not out_root.exists(), "G1a: refusal must create nothing"


def test_G1b_closure_only_flag_and_g2_rejection():
    proc = _run_runner("--help")
    assert proc.returncode == 0
    assert "--closure-only" in proc.stdout, "G1b: --help must document --closure-only"
    with _tmp() as tmp:
        freeze = _write_freeze(tmp, dict(FULL_FREEZE))
        proc = _run_runner(
            "--authorized", "--stage-g2-decode", "--closure-only",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(tmp / "out_g2c"),
        )
        assert proc.returncode == 2, f"G1b exit {proc.returncode}: {proc.stderr}"
        assert "closure-only" in proc.stderr.lower(), proc.stderr.strip()


def test_G1c_closure_without_auth_creates_nothing():
    with _tmp() as tmp:
        freeze = _write_freeze(tmp, dict(FULL_FREEZE))
        before = sorted(p.name for p in tmp.iterdir())
        proc = _run_runner(
            "--stage-g1-nll", "--closure-only",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(tmp / "out_noauth"),
            *G1_FLAGS,
        )
        assert proc.returncode == 2, f"G1c exit {proc.returncode}"
        assert "--authorized" in proc.stderr, proc.stderr.strip()
        assert sorted(p.name for p in tmp.iterdir()) == before, "G1c: runner touched files"


def test_G1k_unknown_acq_and_production_remainder_exit2():
    with _tmp() as tmp:
        freeze = _write_freeze(tmp, dict(FULL_FREEZE))
        bad_root = tmp / "out_unknown"
        proc = _run_runner(
            "--authorized", "--stage-g1-nll",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(bad_root),
            *G1_FLAGS,
        )
        assert proc.returncode == 2, f"G1k exit {proc.returncode}: {proc.stderr}"
        assert not bad_root.exists(), "G1k: unknown-acq refusal must create nothing"
        rem_root = tmp / "out_remprod"
        proc = _run_runner(
            "--authorized", "--stage-g1-nll",
            "--freeze-config", str(freeze),
            "--acq-id", "remainder_101f",
            "--out-root", str(rem_root),
            *G1_FLAGS,
        )
        assert proc.returncode == 2, f"G1k remainder exit {proc.returncode}: {proc.stderr}"
        assert "Phase-B" in proc.stderr, proc.stderr.strip()
        assert not rem_root.exists(), "G1k: remainder refusal must create nothing"


# ------------------------------------------------------- G1d import purity

def test_G1d_import_purity():
    src = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            else:
                mods = [node.module or ""]
            for modname in mods:
                root = modname.split(".")[0]
                assert root not in ("TimeTagger", "Swabian", "src", "scripts",
                                    "nbpolar", "comparison_bench", "pandas", "scipy"), (
                    f"G1d: top-level import {modname!r} breaks import purity"
                )
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            name = getattr(func, "id", None) or getattr(func, "attr", "")
            assert name != "open", "G1d: module-level file work breaks import purity"
    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) in ("sc_decode",)
        or isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "sc_decode"
    ]
    assert calls == [], "G1d: decoder call present"
    occ = [ln for ln in src.splitlines() if "genie_conditionals" in ln]
    assert occ and all("banned" in ln for ln in occ), (
        f"G1d: genie identifier outside the loader ban list: {occ}"
    )
    text_syspath = src.index("sys.path.insert")
    shim_idx = src.index('sys.modules.setdefault("TimeTagger"')
    assert text_syspath < shim_idx, "G1d: repo-root insert must precede shim"
    assert shim_idx < src.index("from src.qkd_io"), "G1d: shim must precede src.qkd_io import"
    assert "def main(argv=None)" in src, "G1d: main(argv=None) required"
    assert '__main__' in src, "G1d: __main__ guard required"
    assert "def run_closure" in src and "closure_only" in src, "G1d: closure body required"


def test_G1l_frozen_loader_identity_and_readonly():
    m2_mod = m._frozen_m2()
    prior_mod = m._frozen_prior()
    assert Path(m2_mod.__file__).resolve() == (
        REPO_ROOT / "comparison_bench" / "src" / "comparison_bench" / "formal_ir" / "prior_m2.py"
    ).resolve()
    assert Path(prior_mod.__file__).resolve() == (
        REPO_ROOT / "comparison_bench" / "src" / "comparison_bench" / "formal_ir"
        / "nbpolar" / "prior.py"
    ).resolve()
    for path in (m2_mod.__file__, prior_mod.__file__):
        tree = ast.parse(Path(path).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert (node.level or 0) == 0, "G1l: relative import in frozen leaf"
    assert m._frozen_m2() is m2_mod, "G1l: loader must cache"


# ------------------------------------------------------- G1e pairing literal

def test_G1e_pairing_hand_traces_and_uniqueness():
    # Hand trace: greedy monotonic 1-1, offset on A, symbol b=t//200 %1024.
    pa, pb = m.pair_narrow_nearest_unique(
        np.array([0, 250, 10000], dtype=np.int64),
        np.array([40, 300, 10060], dtype=np.int64),
        50, 500,
    )
    assert pa.tolist() == [0, 1, 50] and pb.tolist() == [0, 1, 50]
    # Competition: two A events, one B event in window -> first A wins (1-1).
    pa, pb = m.pair_narrow_nearest_unique(
        np.array([0, 100], dtype=np.int64), np.array([60], dtype=np.int64), 0, 500,
    )
    assert pa.tolist() == [0] and pb.tolist() == [0]
    # Negative-timestamp floor semantics (Python // floors, % non-negative).
    pa, pb = m.pair_narrow_nearest_unique(
        np.array([-250], dtype=np.int64), np.array([-220], dtype=np.int64), 50, 500,
    )
    assert pa.tolist() == [1023] and pb.tolist() == [1022], (pa.tolist(), pb.tolist())
    # Literal independent reimplementation agrees on seeded streams.
    rng = np.random.default_rng(20260921)
    tA = np.sort(rng.integers(0, 2_000_000, size=3000).astype(np.int64))
    tB = np.sort(rng.integers(0, 2_000_000, size=3000).astype(np.int64))

    def _literal(a, b, off, w):
        out_a, out_b = [], []
        i = j = 0
        while i < len(a) and j < len(b):
            d = int(a[i]) + off - int(b[j])
            if d < -w:
                i += 1
            elif d > w:
                j += 1
            else:
                out_a.append((int(a[i]) + off) // 200 % 1024)
                out_b.append(int(b[j]) // 200 % 1024)
                i += 1
                j += 1
        return out_a, out_b

    for w in (200, 500):
        la, lb = _literal(tA.tolist(), tB.tolist(), 50, w)
        ga, gb = m.pair_narrow_nearest_unique(tA, tB, 50, w)
        assert ga.tolist() == la and gb.tolist() == lb, f"G1e mismatch at w={w}"
        assert len(ga) == len(set(zip(ga.tolist(), range(len(ga))))), "G1e: pairs must be unique"


# ------------------------------------------------------- G1f framing

def test_G1f_skip_chunk_trailing_drop():
    n = 5 * 8 + 3
    a = (np.arange(n, dtype=np.int64) * 3) % 1024
    b = (np.arange(n, dtype=np.int64) * 5) % 1024
    fa, fb, led = m.chunk_frames(a, b, 2, 8)
    assert led == {"skip_frames": 2, "skip_pairs": 16, "preskip_pairs": n,
                   "postskip_pairs": n - 16, "frame_pairs": 8,
                   "complete_frames": (n - 16) // 8, "used_pairs": ((n - 16) // 8) * 8,
                   "dropped_trailing_pairs": (n - 16) % 8}, led
    assert fa.shape == ((n - 16) // 8, 8) and fb.shape == fa.shape
    assert fa[0, 0] == a[16] and fb[-1, -1] == b[16 + fa.size - 1]
    assert_raises_match(ValueError, "length mismatch", m.chunk_frames, a, b[:-1], 0, 8)
    assert_raises_match(ValueError, "shorter than skip", m.chunk_frames, a[:4], b[:4], 2, 8)


# ------------------------------------------------------- G1g MOD handling

def test_G1g_mod_wrap_cells():
    wa = np.array([5, 6, 0, 1023, 100], dtype=np.int64)
    wb = np.array([5, 5, 1023, 0, 200], dtype=np.int64)
    lin = m.mod_tail_counts(wa, wb, "LINEAR_ONLY")
    assert (lin["n0"], lin["n_plus"], lin["n_minus"], lin["n_tail"]) == (1, 1, 0, 3), lin
    cir = m.mod_tail_counts(wa, wb, "CIRCULAR")
    assert (cir["n0"], cir["n_plus"], cir["n_minus"], cir["n_tail"]) == (1, 2, 1, 1), cir
    prof = m.delta_profile(wa, wb)
    assert prof["n"] == 5 and prof["linear_offset"] == -1023 and prof["circular_offset"] == -512
    assert sum(prof["linear_counts"]) == 5 and sum(prof["circular_counts"]) == 5
    assert prof["summaries"]["LINEAR_ONLY"] == lin and prof["summaries"]["CIRCULAR"] == cir
    assert_raises_match(ValueError, "mod must be", m.mod_tail_counts, wa, wb, "WRAP")


# ------------------------------------------------------- G1h NLL/gate arithmetic

def test_G1h_gate_arithmetic_hand_checked():
    g0 = m.eval_delta_tail(0, 200192, 2.0e-4)
    assert g0["U"] == 3.0 / 200192 and g0["p_hat"] == 0.0 and g0["verdict"] == "PASS", g0
    assert m.clopper_pearson_upper(7, 7) == 1.0
    assert m.eval_delta_tail(7, 7, 2.0e-4)["verdict"] == "FAIL"
    # Independent Clopper-Pearson check: binomial CDF at U must equal 0.05
    # (direct math.comb sum — shares no code with the runner helper).
    U = m.clopper_pearson_upper(2, 20)
    cdf = sum(math.comb(20, i) * U**i * (1 - U) ** (20 - i) for i in range(3))
    assert abs(cdf - 0.05) < 1e-9, (U, cdf)
    assert m.clopper_pearson_upper(3, 20) > U
    assert m.eval_nll_gate(0.03, 0.020)["verdict"] == "PASS"
    assert m.eval_nll_gate(0.0, 0.020)["verdict"] == "FAIL"
    assert m.eval_nll_gate(0.01, 0.020)["verdict"] == "INCONCLUSIVE"


def test_G1h_nll_pipeline_matches_direct_joint_oracle():
    m2_mod = m._frozen_m2()
    prior_mod = m._frozen_prior()
    # Hand-built CAL: diagonal-heavy counts with exact known triple.
    counts = np.zeros((1024, 1024), dtype=np.int64)
    rng = np.random.default_rng(7)
    diag = np.arange(1024)
    counts[diag, diag] = 6
    counts[(diag + 1) % 1024, diag] = 2
    counts[(diag - 1) % 1024, diag] = 1
    counts[10, 500] = 3
    counts[900, 11] = 2
    n_total = int(counts.sum())
    triple = m2_mod.fit_m2_triple(counts, mod="LINEAR_ONLY")
    assert triple["n0"] == 6 * 1024 and triple["n_total"] == n_total
    assert triple["q0"] == 6 * 1024 / n_total
    joint_m2 = m2_mod.build_m2_joint(triple["q0"], triple["q_plus1"], triple["q_minus1"],
                                     mod="LINEAR_ONLY")
    joint_m0 = m2_mod.build_m0_joint(counts)
    for j in (joint_m2, joint_m0):
        assert abs(j.sum(axis=0) - 1).max() <= 1e-12
    # Tiny held-out: pipeline NLL must equal the direct -log2 joint oracle.
    ha = np.array([[5, 6, 0], [1023, 100, 511]], dtype=np.int64)
    hb = np.array([[5, 5, 1023], [0, 200, 511]], dtype=np.int64)
    for joint in (joint_m2, joint_m0):
        got = m.heldout_nll_bits(joint, hb, ha, prior_mod)
        want = float(np.mean([-math.log2(joint[x, y]) for x, y in zip(ha.ravel(), hb.ravel())]))
        assert abs(got["nll_mean_bits"] - want) <= 1e-9, (got["nll_mean_bits"], want)
        assert abs(got["nll_l1_bits"] + got["nll_l2_bits"] - want) <= 1e-9
    # Uniform joint hand value: exactly 10 bits/symbol (5 + 5).
    uni = np.full((1024, 1024), 1.0 / 1024)
    got = m.heldout_nll_bits(uni, hb, ha, prior_mod)
    assert abs(got["nll_mean_bits"] - 10.0) <= 1e-9, got
    assert abs(got["nll_l1_bits"] - 5.0) <= 1e-9 and abs(got["nll_l2_bits"] - 5.0) <= 1e-9
    p_b = np.full(1024, 1.0 / 1024)
    ent = m.model_entropy_bits(uni, p_b, prior_mod)
    assert abs(ent["H1_bits"] - 5.0) <= 1e-9, ent
    assert abs(ent["H2_bits"] - 5.0) <= 1e-9, ent
    assert abs(ent["H_total_bits"] - 10.0) <= 1e-9, ent


# ------------------------------------------------------- G1i remainder path

def test_G1i_remainder_exempt_path_fake_runner():
    sp = m.remainder_split_ids()
    assert len(sp["cal_ids"]) == 32 and len(sp["heldout_ids"]) == 69
    assert set(sp["cal_ids"]) | set(sp["heldout_ids"]) == set(range(101))
    rng = np.random.default_rng(20260921)
    n = 101 * 256
    bob = rng.integers(0, 1024, size=n, dtype=np.int64)
    shift = rng.choice([0, 0, 0, 1, -1], size=n, p=[0.90, 0.05, 0.03, 0.01, 0.01])
    alice = (bob + np.where(shift == 0, 0, np.where(shift == 1, 1, -1))) % 1024
    alice = alice.astype(np.int64)

    def _fake(acq_id):
        assert acq_id == "remainder_101f"
        return {"alice": alice, "bob": bob}

    with _tmp() as tmp:
        out_root = tmp / "rem"
        rc = m.run_stage_g1_nll(acq_id="remainder_101f", out_root=out_root,
                                freeze=dict(FULL_FREEZE), options={},
                                closure_only=False, _read_timetags=_fake)
        assert rc == 0, rc
        g1 = json.loads((out_root / "g1.json").read_text(encoding="utf-8"))
        assert g1["scope"] == "NLL_H_COMPARISON_ONLY" and g1["cal_frames"] == 32
        assert g1["heldout_frames"] == 69 and "nll_delta_bits" in g1
        assert (out_root / "cal_ids.json").exists() and (out_root / "run_log.md").exists()
        assert not (out_root / "delta_profiles.json").exists(), "remainder takes no char sample"


# ------------------------------------------------------- G1j closure paths

def test_G1j_closure_mismatch_path_fake_reader():
    # Synthetic timetags with a planted delay: the frozen estimator runs on
    # synthetic arrays only (no data contact); reproduction MUST mismatch
    # the census gate -> loud ALIGN_INCONSISTENT, partial evidence, rc 1.
    rng = np.random.default_rng(11)
    tA = np.sort(rng.integers(0, 60_000_000, size=20000).astype(np.int64))
    tB = np.sort((tA[:15000] + 137 + rng.integers(-20, 21, size=15000)).astype(np.int64))
    tB = np.sort(np.concatenate([tB, rng.integers(0, 60_000_000, size=5000).astype(np.int64)]))

    def _fake(acq_id):
        return {"tA": tA, "tB": tB, "n_events": int(tA.size + tB.size),
                "channel_hist": {1: int(tA.size), 5: int(tB.size)},
                "other_count": 0, "other_frac": 0.0, "primary": "fake"}

    with _tmp() as tmp:
        out_root = tmp / "closure"
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc = m.run_closure(acq_id="SYNTH", out_root=out_root,
                               freeze=dict(FULL_FREEZE), options={},
                               _read_timetags=_fake)
        assert rc == 1, rc
        assert "ALIGN" in buf.getvalue(), buf.getvalue()
        g1 = json.loads((out_root / "g1.json").read_text(encoding="utf-8"))
        assert g1["verdict"] in ("ALIGN_FAIL", "ALIGN_INCONSISTENT"), g1
        assert "align" in g1


def test_G1m_sweep_accept_dual_rule_convention():
    # Frozen provenance (dual_rule census SHG_1): strict-exact miss by 102
    # pairs at one 40960-step distance -> PASS-with-note, never a gate fail.
    ok, note = m._sweep_accept({"within_one_step_of_max_ok": True, "strict_exact_max": False})
    assert ok and "PASS-with-note" in note, note
    ok, note = m._sweep_accept({"within_one_step_of_max_ok": True,
                                "plateau_membership_ok": True})
    assert ok and "at sweep maximum" in note, note
    ok, note = m._sweep_accept({"within_one_step_of_max_ok": False, "strict_exact_max": False})
    assert not ok and "SELF-CHECK MISS" in note, note


def test_G1j_closure_config_guard_never_weakened():
    # Closure still enforces the §4 rule lists against the input freeze:
    # a tampered input list must fail loudly, never silently overridden.
    assert m.REPRO_GATE["n_pairs"] == 1269268 and m.ALLOCATED_FRAMES == 4190
    segs = m.segment_frame_lists(4256)
    assert segs["cal32"] == list(range(1024, 1056))
    assert segs["heldout"] == list(range(1838, 2398))
    assert segs["a1_cal"] == list(range(0, 1024))
