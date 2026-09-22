"""Focused Phase-0 tests for the G2 one-shot three-arm decode body.

Synthetic fixtures + explicit fake chain ONLY (AGENTS.md §10.1 item 8:
test-only calls pass a fake runner — the production decoder chain is
NEVER invoked from these tests; ``_load_g2_decoder_chain`` is never
called here). No .ttbin/real data, no SHG contact, no claim. The on-disk
construction JSON is never read here (the fake verifies identity).
Written without a pytest dependency so it runs under plain ``python``
and is still collected by pytest: every ``test_*`` takes no arguments
and uses plain asserts. Run directly::

    python comparison_bench/tests/test_nbpolar_m2_g2_decode.py

Packet: NBPOLAR-M2-PRIOR-G2-DECODE, Spec 2.
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
import types
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "m2_prior_validation.py"
G1_PACKET_DIR = REPO_ROOT / ".workbuddy" / "queue" / "NBPOLAR-M2-PRIOR-G1-REALDATA-NLL"
G1R2_PACKET_DIR = (
    REPO_ROOT / ".workbuddy" / "queue" / "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR"
)
G2_PACKET_DIR = (
    REPO_ROOT / ".workbuddy" / "queue" / "NBPOLAR-M2-PRIOR-G2-DECODE"
)


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "m2_prior_validation_g2_test", str(RUNNER)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = _load_runner()


@contextlib.contextmanager
def _tmp():
    """Temp dir under repo workspace/ (auto-cleaned; never outside)."""
    root = REPO_ROOT / "workspace" / ".tmp_g2"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="m2g2_", dir=str(root)) as td:
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


def _full_g2_freeze():
    """Synthetic 19-key G2 freeze (frozen literals, list ids)."""
    return {
        "B_tail": 0.0002,
        "a1_cal_ids": list(range(0, 1024)),
        "block_formation_fallback": (
            "COMPLETE-BLOCKS-ONLY, else INSUFFICIENT=>INCONCLUSIVE "
            "(never pad/reuse/shrink)"
        ),
        "cal_frame_ids": list(range(1024, 1056)),
        "cal_split_rule": (
            "RULE-FIT32-SCORE-HELDOUT: fit all 32, score disjoint held-out, seed N/A"
        ),
        "char_sample_pairs": 200192,
        "delta_min": 0.02,
        "disjointness_matrix": {"all_disjoint": True},
        "g2_arms": [
            "A1_M0_1024f_incumbent",
            "A2_M0_32f_matched",
            "B_M2_32f_candidate",
        ],
        "g2_blocks": 14,
        "g2_fail_rule": "point(B) <= point(A2)",
        "g2_inconclusive_rule": (
            "point(B) > point(A2) but CIs overlap => bounded negative"
        ),
        "g2_success_rule": (
            "Wilson-lower(B) > Wilson-upper(A2), strict non-overlap, z=1.96"
        ),
        "heldout_frame_ids": list(range(1838, 2398)),
        "mod_boundary": "CIRCULAR",
        "pairing_window_primary": 200,
        "pairing_window_sensitivity": 500,
        "skip_frames": 702,
        "tag_master": 2026103001,
    }


def _write_g2_config(tmp):
    p = tmp / "g2_freeze_config.json"
    p.write_text(json.dumps(_full_g2_freeze()), encoding="utf-8")
    return p


# ------------------------------------------------------- fake decode chain

def _fake_chain(scripts=None, oracle_exact=True, fixed_key=None):
    """Explicit fake decoder chain (test-only; production never entered).

    ``scripts`` maps (arm, block) -> outcome bucket among exact /
    undetected / verify_failed / decode_failed / nonfinite. Unlisted
    pairs default to exact. Calls arrive in run_g2_eval loop order
    (arm-major over G2_ARMS, block-minor), so the fake keys scripts by
    call index — the production ``run_operational_block`` call carries no
    arm label. The fake mimics the frozen call accounting
    (2 SC calls + up to 2 tag_fn calls per invoked block) so wiring is
    exercised honestly; decisions are canned, never decoded.
    """
    scripts = scripts or {}
    order = (
        "A1_M0_1024f_incumbent",
        "A2_M0_32f_matched",
        "B_M2_32f_candidate",
    )
    state = {"n": 0}

    def _fake_run_block(**kw):
        if fixed_key is not None:
            arm, blk = fixed_key
        else:
            idx = state["n"]
            state["n"] = idx + 1
            arm, blk = order[idx // 14], idx % 14
        outcome = scripts.get((arm, blk), "exact")
        calls = kw.get("calls")
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + 2
        high = np.array(kw["high_true"], copy=True)
        low = np.array(kw["low_true"], copy=True)
        tag_pass = outcome in ("exact", "undetected")
        label_match = outcome == "exact"
        if outcome == "undetected":
            low = low.copy()
            low[0] = (int(low[0]) + 1) % 32
        invoked = outcome not in ("decode_failed", "nonfinite")
        tag_fn = kw.get("tag_fn")
        if invoked and tag_fn is not None:
            tag_fn(b"0" * 10, b"1" * 73, 64)
            tag_fn(b"0" * 10, b"1" * 73, 64)
        failed = outcome in ("decode_failed", "nonfinite")
        return types.SimpleNamespace(
            outcome=outcome,
            tag_pass=tag_pass,
            label_match=label_match,
            l1_exact=(outcome == "exact"),
            hard_l2_exact=(outcome == "exact"),
            pair_exact=label_match,
            high_hat=(None if failed else high),
            low_hat=(None if failed else low),
            l1_executed=not failed,
            l1_decode_failed=failed,
            l2_invoked=invoked,
            l2_skipped_by_l1_failure=failed,
            l2_decode_failed=(outcome == "decode_failed"),
            tag_invoked=invoked,
            key_dependent_bits=(
                0 if failed
                else 5 * 319 + (5 * 6492 if invoked else 0) + (64 if invoked else 0)
            ),
            public_control_bits=(10 * kw["n"] + 63) if invoked else 0,
            nonfinite=(outcome == "nonfinite"),
            truth_leak_violation=False,
            l1_error_type=("FakeError" if failed else None),
            l2_error_type=None,
        )

    def _fake_sc(logp, *, field, alpha, known_positions, known_values):
        assert int(alpha) == 2
        n = int(np.asarray(logp).shape[0])
        if oracle_exact:
            # Oracle view is scored, not decoded, here: the fake recovers
            # the all-zero low layer exactly iff truth is all-zero (the
            # oracle-True unit uses an all-zero block; else False).
            return types.SimpleNamespace(
                x_hat=np.zeros(n, dtype=np.int64),
                _oracle_marker=True,
            )
        return types.SimpleNamespace(
            x_hat=np.ones(n, dtype=np.int64),
            _oracle_marker=True,
        )

    def _run_block_with_hint(**kw):
        return _fake_run_block(**kw)

    chain = types.SimpleNamespace(
        run_operational_block=_run_block_with_hint,
        sc_decode=_fake_sc,
        toeplitz_tag=lambda bits, seed, tb: b"fake-tag",
        make_gf32=lambda: object(),
        labels_to_bits=lambda lab: np.zeros(10 * len(lab), dtype=np.uint8),
        operational_seed_bits=lambda master, n, blk: np.zeros(10 * n + 63, dtype=np.uint8),
        classify_operational_outcome=lambda **kw: "exact",
        verify_predecessor_construction=(
            lambda path, *, expected_digest: {
                "l1_order": list(range(32768)),
                "l2_order": list(range(32768)),
            }
        ),
        polar_transform=lambda v, *, field=None, alpha=2: np.asarray(v).copy(),
        alpha=2,
    )
    return chain


def _run_block_fake(arm, blk, outcome="exact", oracle_exact=True, **kw):
    """One synthetic block through a single-use fake keyed at (arm, blk)."""
    chain = _fake_chain({(arm, blk): outcome}, oracle_exact=oracle_exact,
                        fixed_key=(arm, blk))
    return m.run_g2_block(arm=arm, block_index=blk, chain=chain, **kw)


def _frames_bundle(n_frames=4190, seed=20260922):
    rng = np.random.default_rng(seed)
    fa = rng.integers(0, 1024, size=(n_frames, 256)).astype(np.int64)
    fb = rng.integers(0, 1024, size=(n_frames, 256)).astype(np.int64)
    return {"frames_a": fa, "frames_b": fb, "ledger_complete": n_frames}


def _snapshot_packet_dirs():
    snap = {}
    for d in (G1_PACKET_DIR, G1R2_PACKET_DIR, G2_PACKET_DIR):
        if d.is_dir():
            for p in sorted(d.iterdir()):
                if p.is_file():
                    snap[p] = p.read_bytes()
        else:
            snap[d] = None
    return snap


def _assert_packet_dirs_untouched(before):
    after = _snapshot_packet_dirs()
    assert set(after) == set(before), (
        f"packet-dir file set changed: {sorted(set(after) ^ set(before))}"
    )
    for p, blob in before.items():
        if blob is None:
            assert after[p] is None, f"packet dir created: {p}"
        else:
            assert after[p] == blob, f"packet file touched: {p}"


# ------------------------------------------------------- 1 freeze keys + K

def test_freeze_19_keys_enforced():
    assert len(m.REQUIRED_FREEZE_KEYS) == 19
    full = _full_g2_freeze()
    assert m._missing_freeze_keys(full) == []
    for drop in (["tag_master"], ["g2_arms", "g2_blocks"]):
        cfg = {k: v for k, v in full.items() if k not in drop}
        assert m._missing_freeze_keys(cfg) == sorted(drop)
    nul = dict(full)
    nul["B_tail"] = None
    assert m._missing_freeze_keys(nul) == ["B_tail"]
    with _tmp() as tmp:
        p = _write_g2_config(tmp)
        assert set(m.load_freeze_config(p)) >= set(m.REQUIRED_FREEZE_KEYS)
        q = tmp / "bad.json"
        q.write_text(json.dumps({k: v for k, v in full.items() if k != "mod_boundary"}),
                     encoding="utf-8")
        err = _expect_exit2(lambda: m.load_freeze_config(q))
        assert "mod_boundary" in err


def test_k_pin_319_6492():
    m._check_k_pin("319", "6492")
    m._check_k_pin(None, None)
    err = _expect_exit2(lambda: m._check_k_pin("320", "6492"))
    assert "319" in err
    err = _expect_exit2(lambda: m._check_k_pin("319", "6493"))
    assert "6492" in err


# ------------------------------------------------------- 2 stage-keyed routing

def test_stage_keyed_routing():
    with _tmp() as tmp:
        assert m.check_g2_config_route(tmp / "g2_freeze_config.json") is None
        assert m.check_g2_config_route(tmp / "freeze.json") is not None
        assert m.check_g2_config_route(None) is not None
        # G1/G1R2 packet-dir paths never route, even with a G2 name.
        for foreign in (
            G1_PACKET_DIR / "g1_freeze_config.json",
            G1R2_PACKET_DIR / "g1r2_freeze_config.json",
            G1_PACKET_DIR / "g2_freeze_config.json",
            G1R2_PACKET_DIR / "g2_freeze_config.json",
        ):
            assert m.check_g2_config_route(foreign) is not None, foreign
        # A Stage-1-era freeze (name + window-500 contract) exits 3 with
        # zero contact — the G2 body is pending for THAT freeze.
        out_root = tmp / "never_created"
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc = m.run_stage_g2(
                acq_id="X", out_root=out_root,
                freeze={k: f"value-{k}" for k in m.REQUIRED_FREEZE_KEYS},
                options={}, _config_path=tmp / "freeze.json",
            )
        assert rc == 3, rc
        assert "STAGE_BODY_PENDING_FREEZE" in buf.getvalue()
        assert not out_root.exists()
        # G2 name but non-200 window: still exit 3 (no silent fallback).
        cfg = _full_g2_freeze()
        cfg["pairing_window_primary"] = 500
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc = m.run_stage_g2(
                acq_id="X", out_root=out_root, freeze=cfg, options={},
                _config_path=tmp / "g2_freeze_config.json",
            )
        assert rc == 3, rc
        assert not out_root.exists()


def test_no_g1_g1r2_write_success_path():
    before = _snapshot_packet_dirs()
    with _tmp() as tmp:
        cfg = _write_g2_config(tmp)
        freeze = m.load_freeze_config(cfg)
        out_root = tmp / "out"
        chain = _fake_chain()
        bundle = _frames_bundle()
        rc = m.run_stage_g2(
            acq_id="SYNTH", out_root=out_root, freeze=freeze, options={},
            _decode_chain=chain, _frames_bundle=bundle, _config_path=cfg,
        )
        assert rc == 0, rc
        for name in (
            "per_block_outcomes.jsonl", "g2_summary.json",
            "cal_ids.json", "run_log.md",
        ):
            assert (out_root / name).is_file(), name
    _assert_packet_dirs_untouched(before)


# ------------------------------------------------------- 3 block/frame arithmetic

def test_block_frame_arithmetic():
    blocks = m.g2_eval_blocks()
    assert len(blocks) == m.G2_BLOCKS == 14
    flat = [f for s, e in blocks for f in range(s, e + 1)]
    assert flat == list(range(2398, 4190)), (flat[:3], flat[-3:])
    assert len(flat) == 1792 == 14 * 128
    assert 128 * 256 == m.G2_N == 32768
    assert len(m.g2_cal_ids("A1_M0_1024f_incumbent")) == 1024
    assert len(m.g2_cal_ids("A1_M0_1024f_incumbent")) * 256 == 262144
    assert len(m.g2_cal_ids("A2_M0_32f_matched")) == 32
    assert len(m.g2_cal_ids("B_M2_32f_candidate")) * 256 == 8192


def test_cal_disjointness_enforcement():
    named = {
        "a1_cal": m.g2_cal_ids("A1_M0_1024f_incumbent"),
        "cal32": m.g2_cal_ids("A2_M0_32f_matched"),
        "char": list(range(1056, 1838)),
        "heldout": list(range(1838, 2398)),
        "eval": [f for s, e in m.g2_eval_blocks() for f in range(s, e + 1)],
    }
    mx = m.disjointness_matrix(named)
    assert mx["all_disjoint"] is True
    assert len(mx["pairwise_overlap"]) == 10
    assert all(v == 0 for v in mx["pairwise_overlap"].values())
    # A2 and B share the matched 32-frame CAL by freeze design...
    assert m.g2_cal_ids("A2_M0_32f_matched") == m.g2_cal_ids("B_M2_32f_candidate")
    # ...but every CAL is disjoint from EVAL.
    for arm in m.G2_ARMS:
        assert not (set(m.g2_cal_ids(arm)) & set(named["eval"])), arm
    try:
        m.g2_cal_ids("A9_NOPE")
    except ValueError as exc:
        assert "unknown G2 arm" in str(exc)
    else:
        raise AssertionError("unknown arm must raise")


# ------------------------------------------------------- 4 undetected isolation

def test_undetected_isolation():
    prior_mod = m._frozen_prior()
    m2_mod = m._frozen_m2()
    rng = np.random.default_rng(7)
    n = 512
    alice = rng.integers(0, 1024, size=n).astype(np.int64)
    bob = rng.integers(0, 1024, size=n).astype(np.int64)
    fit = m.fit_g2_arm("B_M2_32f_candidate", alice, bob, "CIRCULAR", m2_mod)
    p1 = prior_mod.derive_p1(fit["joint"])
    p2 = prior_mod.derive_p2(fit["joint"])
    kw = dict(
        eval_frames=[2398, 2525], bob=bob, alice=alice, fit=fit,
        p1_table=p1, p2_table=p2,
        l1_order=list(range(n)), l2_order=list(range(n)),
        k1=3, k2=5, tag_master=m.G2_TAG_MASTER, eval_seed=m.G2_EVAL_SEED,
        polar_fn=lambda v: np.asarray(v).copy(), prior_mod=prior_mod,
    )
    rec = _run_block_fake("B_M2_32f_candidate", 0, "undetected", **kw)
    assert rec["outcome"] == "undetected", rec["outcome"]
    assert rec["undetected"] is True and rec["exact"] is False
    assert rec["tag_pass"] is True and rec["label_match"] is False
    rec2 = _run_block_fake("B_M2_32f_candidate", 1, "verify_failed", **kw)
    assert rec2["outcome"] == "verify_failed"
    assert rec2["exact"] is False and rec2["undetected"] is False
    # Full-matrix taxonomy mapping on one block each.
    for outcome, want_exact, want_und in (
        ("exact", True, False),
        ("decode_failed", False, False),
        ("nonfinite", False, False),
    ):
        r = _run_block_fake("A2_M0_32f_matched", 2, outcome, **kw)
        assert r["outcome"] == outcome, (outcome, r["outcome"])
        assert r["exact"] is want_exact and r["undetected"] is want_und, (outcome, r)


def test_gate_counts_exact_only_excluding_undetected():
    # B 13 exact + 1 undetected vs A2 14 exact: gate sees 13 vs 14
    # (point below -> FAIL); undetected never merges into success.
    gate = m.eval_g2_gate(13, 14)
    assert gate["verdict"] == "FAIL", gate
    assert gate["b"]["k"] == 13 and gate["a2"]["k"] == 14


# ------------------------------------------------------- 5 Wilson gate, hand-computed

def _wilson_independent(k, n, z=1.96):
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def test_wilson_against_independent_values():
    for k, n in ((0, 14), (14, 14), (7, 14), (8, 14), (3, 14), (11, 14), (1, 14)):
        got = m.wilson_interval(k, n)
        lo, hi = _wilson_independent(k, n)
        assert abs(got["lower"] - lo) <= 1e-12, (k, got, lo)
        assert abs(got["upper"] - hi) <= 1e-12, (k, got, hi)
        assert abs(got["p_hat"] - k / n) <= 1e-15
    # Boundaries clamp.
    assert m.wilson_interval(0, 14)["lower"] == 0.0
    assert m.wilson_interval(14, 14)["upper"] == 1.0
    # Gate verdicts: strict non-overlap SUCCESS; equal points FAIL;
    # better-point overlap INCONCLUSIVE.
    assert m.eval_g2_gate(14, 0)["verdict"] == "SUCCESS"
    assert m.eval_g2_gate(14, 7)["verdict"] == "SUCCESS"
    assert m.eval_g2_gate(7, 7)["verdict"] == "FAIL"
    assert m.eval_g2_gate(0, 14)["verdict"] == "FAIL"
    assert m.eval_g2_gate(13, 14)["verdict"] == "FAIL"
    assert m.eval_g2_gate(8, 7)["verdict"] == "INCONCLUSIVE"
    assert m.eval_g2_gate(14, 13)["verdict"] == "INCONCLUSIVE"
    # SUCCESS ⟺ recomputed strict non-overlap; FAIL ⟺ not SUCCESS and
    # point(B) <= point(A2); else INCONCLUSIVE (property, not spelling).
    for b, a in ((14, 0), (14, 7), (8, 7), (7, 7), (13, 14), (0, 14), (14, 13)):
        g = m.eval_g2_gate(b, a)
        blo, _bhi = _wilson_independent(b, 14)
        _alo, ahi = _wilson_independent(a, 14)
        assert (g["verdict"] == "SUCCESS") == (blo > ahi), (b, a, g)
        assert (g["verdict"] == "FAIL") == (not (blo > ahi) and b / 14 <= a / 14), (b, a, g)


# ------------------------------------------------------- 6 exit codes

def test_stage_g2_exit0_success_and_summary_shape():
    with _tmp() as tmp:
        cfg = _write_g2_config(tmp)
        freeze = m.load_freeze_config(cfg)
        out_root = tmp / "out"
        # A2 exact on 7/14 only; B exact on 14/14 -> SUCCESS.
        scripts = {
            ("A2_M0_32f_matched", b): "verify_failed" for b in range(7, 14)
        }
        rc = m.run_stage_g2(
            acq_id="SYNTH", out_root=out_root, freeze=freeze, options={},
            _decode_chain=_fake_chain(scripts), _frames_bundle=_frames_bundle(),
            _config_path=cfg,
        )
        assert rc == 0, rc
        rows = (out_root / "per_block_outcomes.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(rows) == 42, len(rows)
        summary = json.loads((out_root / "g2_summary.json").read_text(encoding="utf-8"))
        assert summary["packet"] == "NBPOLAR-M2-PRIOR-G2-DECODE"
        assert summary["verdict"] == "SUCCESS", summary["gate"]
        assert summary["arms"]["A1_M0_1024f_incumbent"]["exact"] == 14
        assert summary["arms"]["A2_M0_32f_matched"]["exact"] == 7
        assert summary["arms"]["B_M2_32f_candidate"]["exact"] == 14
        assert summary["arms"]["B_M2_32f_candidate"]["undetected"] == 0
        assert summary["disclosure_recount"]["mismatches"] == []
        assert summary["construction"]["inner_digest"] == (
            "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
        )
        assert "M2 is a CANDIDATE" in summary["caveats"]
        assert summary["calls"]["sc_calls"] == 42 * 3, summary["calls"]
        assert summary["calls"]["tag_invocations"] == 42, summary["calls"]
        log = (out_root / "run_log.md").read_text(encoding="utf-8")
        assert "gate: SUCCESS" in log, log.splitlines()[3]


def test_stage_g2_exit1_insufficient_records_inconclusive():
    with _tmp() as tmp:
        cfg = _write_g2_config(tmp)
        freeze = m.load_freeze_config(cfg)
        out_root = tmp / "out"
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc = m.run_stage_g2(
                acq_id="SYNTH", out_root=out_root, freeze=freeze, options={},
                _decode_chain=_fake_chain(), _frames_bundle=_frames_bundle(n_frames=100),
                _config_path=cfg,
            )
        assert rc == 1, rc
        summary = json.loads((out_root / "g2_summary.json").read_text(encoding="utf-8"))
        assert summary["verdict"] == "INCONCLUSIVE", summary
        assert "INSUFFICIENT" in summary["reason"], summary
        assert "G2_INSUFFICIENT" in buf.getvalue()


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        capture_output=True, text=True, timeout=120,
    )


def test_cli_exit_codes_no_side_effects():
    with _tmp() as tmp:
        assert _run_cli("--help").returncode == 0
        cfg = _write_g2_config(tmp)
        # No --authorized: exit 2 before any read/create.
        out_root = tmp / "out_noauth"
        proc = _run_cli(
            "--stage-g2-decode", "--freeze-config", str(cfg),
            "--acq-id", "X", "--out-root", str(out_root),
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "--authorized" in proc.stderr
        assert not out_root.exists()
        # --closure-only is G1-only (B2): hard refusal with G2.
        out_root2 = tmp / "out_closure"
        proc = _run_cli(
            "--stage-g2-decode", "--freeze-config", str(cfg),
            "--acq-id", "X", "--out-root", str(out_root2),
            "--closure-only", "--authorized",
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "--closure-only" in proc.stderr
        assert not out_root2.exists()
        # K pin: exit 2, names 319, creates nothing.
        out_root3 = tmp / "out_k"
        proc = _run_cli(
            "--stage-g2-decode", "--freeze-config", str(cfg),
            "--acq-id", "X", "--out-root", str(out_root3),
            "--k1", "320", "--k2", "6492", "--authorized",
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "319" in proc.stderr
        assert not out_root3.exists()


# ------------------------------------------------------- 7 arms spelling (verbatim guard)

def test_arms_short_spelling_does_not_satisfy_verbatim_guard():
    # The packet Phase-B command spells `--arms A1,A2,B` while the freeze
    # carries the full triple. The verbatim flag↔key cross-check compares
    # normalized spellings exactly: the short spelling MISMATCHES (exit 2
    # if passed). Pinned here so the conflict is resolved explicitly by
    # the main thread before Phase B — never smoothed in code.
    freeze = _full_g2_freeze()
    mism = m._cross_check_mismatches({"arms": "A1,A2,B"}, freeze)
    assert len(mism) == 1 and "g2_arms" in mism[0], mism
    ok = m._cross_check_mismatches(
        {"arms": "A1_M0_1024f_incumbent,A2_M0_32f_matched,B_M2_32f_candidate"},
        freeze,
    )
    assert ok == []


# ------------------------------------------------------- 8 arm fitting modes

def test_fit_g2_arm_modes():
    m2_mod = m._frozen_m2()
    rng = np.random.default_rng(20260922)
    a = rng.integers(0, 1024, size=8192).astype(np.int64)
    b = rng.integers(0, 1024, size=8192).astype(np.int64)
    for arm, mode in (
        ("A1_M0_1024f_incumbent", "M0"),
        ("A2_M0_32f_matched", "M0"),
        ("B_M2_32f_candidate", "M2"),
    ):
        fit = m.fit_g2_arm(arm, a, b, "CIRCULAR", m2_mod)
        assert fit["mode"] == mode, (arm, fit["mode"])
        assert fit["n_cal_pairs"] == 8192
        assert fit["joint"].shape == (1024, 1024)
        assert abs(fit["joint"].sum(axis=0) - 1).max() <= 1e-9
        if mode == "M2":
            t = fit["triple"]
            assert abs(t["q0"] + t["q_plus1"] + t["q_minus1"] + t["q_rest"] - 1.0) <= 1e-12
        else:
            assert fit["triple"] is None
    try:
        m.fit_g2_arm("A9_NOPE", a, b, "CIRCULAR", m2_mod)
    except ValueError as exc:
        assert "unknown G2 arm" in str(exc)
    else:
        raise AssertionError("unknown arm must raise")


# ------------------------------------------------------- 10 polar binder contract

def test_polar_binder_pins_keyword_only_field():
    # Test-gap closure (G2-BLOCKED-POLARFN-FIELD): the frozen
    # polar_transform(symbols, *, field, alpha) requires keyword-only
    # field. The runner binds it via _bind_g2_polar; a signature-strict
    # fake (same contract as frozen) must succeed ONLY when field/alpha
    # arrive as keywords — a single-arg call shape fails loudly here
    # instead of at Phase B.
    seen = {}

    def strict_polar(v, *, field, alpha=2):
        seen["field"] = field
        seen["alpha"] = alpha
        return np.asarray(v).copy()

    vec = np.array([3, 31, 0, 7], dtype=np.int64)
    bound = m._bind_g2_polar(strict_polar, object(), 2)
    assert bound(vec).tolist() == vec.tolist()
    assert seen["field"] is not None and seen["alpha"] == 2
    try:
        strict_polar(vec)
    except TypeError as exc:
        assert "field" in str(exc)
    else:
        raise AssertionError("keyword-only field must be required")


# ------------------------------------------------------- 11 import purity

def test_import_purity_and_entry_shape():
    src = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = (
                [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            for modname in mods:
                assert modname.split(".")[0] not in (
                    "TimeTagger", "Swabian", "src", "scripts",
                    "nbpolar", "comparison_bench", "pandas", "scipy",
                    "yaml",
                ), modname
    assert src.index("sys.path.insert") < src.index('sys.modules.setdefault("TimeTagger"')
    assert "def main(argv=None)" in src and "__main__" in src
    # --closure-only stays store_true; the production chain loader is
    # deferred (no frozen-decoder import at module top).
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
    assert "def _load_g2_decoder_chain" in src
    assert "STAGE_BODY_PENDING_FREEZE" in src


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
