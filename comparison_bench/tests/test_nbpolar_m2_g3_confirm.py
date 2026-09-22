"""Focused Phase-0 tests for the G3 Phase-A closure body (decoder-free)
plus the Phase-B one-shot three-arm decode body (--stage-g3-decode).

Synthetic fixtures + explicit fake seams ONLY (AGENTS.md §10.1 item 8:
test-only calls pass fake readers/chains — the production FileReader/
decoder chain is NEVER entered from these tests; the production chain
loader is never called here, and this file imports neither TimeTagger nor
Swabian).
No .ttbin/real data, no SHG contact, no claim. The on-disk construction
JSON is never read here (the fake verifies identity). The Phase-B decode
body is implemented in this dispatch with fake-chain tests ONLY; the
one-shot production decode is never run from here.
Written without a pytest dependency so it runs under plain ``python``
and is still collected by pytest: every ``test_*`` takes no arguments
and uses plain asserts. Run directly::

    /home/karel_303/.venvs/timetagger/bin/python \\
        comparison_bench/tests/test_nbpolar_m2_g3_confirm.py

Packet: NBPOLAR-M2-PRIOR-G3-CONFIRM, Phase 0 + A + B(body). G3-0 / G3-A / G3-1(body).
"""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import inspect
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
G3_PACKET_DIR = (
    REPO_ROOT / ".workbuddy" / "queue" / "NBPOLAR-M2-PRIOR-G3-CONFIRM"
)


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "m2_prior_validation_g3_test", str(RUNNER)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = _load_runner()


@contextlib.contextmanager
def _tmp():
    """Temp dir under repo workspace/ (auto-cleaned; never outside)."""
    root = REPO_ROOT / "workspace" / ".tmp_g3"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="m2g3_", dir=str(root)) as td:
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


def _full_g3_freeze():
    """Synthetic 19-key G3 freeze (frozen literals, G3 tag_master)."""
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
        "tag_master": 2026110101,
    }


def _write_g3_config(tmp):
    p = tmp / "g3_freeze_config.json"
    p.write_text(json.dumps(_full_g3_freeze()), encoding="utf-8")
    return p


# ------------------------------------------------------- fake closure seams
# These fakes substitute the frozen production functions named below. Their
# signatures are PINNED against the real ones in
# test_fake_signatures_pin_frozen_calls (the G2 lesson: a single-arg
# identity-lambda double hid a missing keyword-only `field`).

def _fake_reader(tA, tB, other_frac=0.0):
    """Fake acquisition reader substituting _read_timetags_g3_production."""
    def _read(acq_id):
        return {
            "tA": np.asarray(tA, dtype=np.int64),
            "tB": np.asarray(tB, dtype=np.int64),
            "n_events": int(np.asarray(tA).size + np.asarray(tB).size),
            "channel_hist": {1: int(np.asarray(tA).size),
                             5: int(np.asarray(tB).size)},
            "other_count": 0,
            "other_frac": float(other_frac),
            "primary": "synthetic",
        }
    return _read


def _fake_align(center=50, sigma=114.5, to_bg=999.0, status="ok"):
    """Fake alignment substituting _align_frozen."""
    def _align(tA, tB):
        return {
            "peak_center_ps": center,
            "peak_sigma_ps": sigma,
            "peak_to_bg": to_bg,
            "status": status,
        }
    return _align


def _fake_sweep(y_at=100, y_max=100):
    """Fake yield sweep substituting _yield_sweep_selfcheck."""
    def _sweep(tA, tB, derived_offset):
        return {
            "offsets": [int(derived_offset)],
            "yields": [int(y_max)],
            "coarse_step": 40960,
            "derived_offset": int(derived_offset),
            "yield_at_derived": int(y_at),
            "yield_max": int(y_max),
            "plateau_membership_ok": bool(y_at == y_max),
            "within_one_step_of_max_ok": True,
            "strict_exact_max": bool(y_at == y_max),
            "yield_max_ok": bool(y_at == y_max),
        }
    return _sweep


def _synthetic_coincident_timetags(n_pairs, seed=20261001):
    """n coincident timetag pairs (offset 50, jitter within window 200).

    tB is a 1 kHz grid; tA = tB - 50 + jitter([-100, 100]). Under the
    inherited pairing (offset +50, window 200) every event matches 1-1,
    so n_pairs pairs / n_pairs // 256 pre-skip frames result.
    """
    rng = np.random.default_rng(seed)
    tB = 10_000_000 + np.arange(n_pairs, dtype=np.int64) * 1000
    jitter = rng.integers(-100, 101, size=n_pairs).astype(np.int64)
    tA = tB - 50 + jitter
    return tA, tB


def _snapshot_packet_dirs():
    snap = {}
    for d in (G1_PACKET_DIR, G1R2_PACKET_DIR, G2_PACKET_DIR, G3_PACKET_DIR):
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


# ------------------------------------------------------- fake decode chain
# Phase-B fakes substitute the frozen production chain namespace consumed
# by run_stage_g3_decode (via run_g2_block/run_g2_eval). Their call shapes
# are PINNED against the real frozen signatures in
# test_g3d_fake_signatures_pin_every_substituted_frozen_call (the G2
# lesson: a single-arg identity-lambda double hid a missing keyword-only
# `field`). The production loader (_load_g2_decoder_chain) is NEVER
# called here.

def _fake_g3_chain(scripts=None, oracle_exact=True, fixed_key=None):
    """Explicit fake decoder chain for the G3 decode body (test-only).

    ``scripts`` maps (arm, block) -> outcome bucket among exact /
    undetected / verify_failed / decode_failed / nonfinite. Unlisted
    pairs default to exact. Calls arrive in run_g2_eval loop order
    (arm-major over G2_ARMS, block-minor), so the fake keys scripts by
    call index — the production ``run_operational_block`` call carries no
    arm label. The fake mimics the frozen call accounting (2 SC calls +
    up to 2 tag_fn calls per invoked block) so wiring is exercised
    honestly; decisions are canned, never decoded. ``truth`` records the
    exact kwargs of every operational-block call (master/seed/K pin
    checks read it back).
    """
    scripts = scripts or {}
    order = (
        "A1_M0_1024f_incumbent",
        "A2_M0_32f_matched",
        "B_M2_32f_candidate",
    )
    state = {"n": 0}
    truth = {}

    def _fake_run_block(**kw):
        if fixed_key is not None:
            arm, blk = fixed_key
        else:
            idx = state["n"]
            state["n"] = idx + 1
            arm, blk = order[idx // 14], idx % 14
        truth[(arm, blk)] = {
            "n": kw["n"], "master": kw["master"],
            "stream_seed": kw["stream_seed"],
            "k1": kw["k1"], "k2": kw["k2"],
            "block_index": kw["block_index"],
        }
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
        assert field is not None and int(alpha) == 2
        n = int(np.asarray(logp).shape[0])
        if oracle_exact:
            return types.SimpleNamespace(
                x_hat=np.zeros(n, dtype=np.int64),
                _oracle_marker=True,
            )
        return types.SimpleNamespace(
            x_hat=np.ones(n, dtype=np.int64),
            _oracle_marker=True,
        )

    def _fake_polar(v, *, field, alpha=2):
        assert field is not None and int(alpha) == 2
        return np.asarray(v).copy()

    def _fake_verify(path, *, expected_digest):
        assert expected_digest == (
            "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
        ), expected_digest
        return {
            "l1_order": list(range(32768)),
            "l2_order": list(range(32768)),
        }

    chain = types.SimpleNamespace(
        run_operational_block=_fake_run_block,
        sc_decode=_fake_sc,
        toeplitz_tag=lambda bits, seed, tb: b"fake-tag",
        make_gf32=lambda: object(),
        labels_to_bits=lambda lab: np.zeros(10 * len(lab), dtype=np.uint8),
        operational_seed_bits=lambda master, n, blk: np.zeros(10 * n + 63, dtype=np.uint8),
        classify_operational_outcome=lambda **kw: "exact",
        verify_predecessor_construction=_fake_verify,
        polar_transform=_fake_polar,
        alpha=2,
    )
    return chain, truth


def _g3d_frames_bundle(n_frames=4190, seed=20260922):
    rng = np.random.default_rng(seed)
    fa = rng.integers(0, 1024, size=(n_frames, 256)).astype(np.int64)
    fb = rng.integers(0, 1024, size=(n_frames, 256)).astype(np.int64)
    return {"frames_a": fa, "frames_b": fb, "ledger_complete": n_frames}


def _run_g3d_stage(tmp, scripts=None, n_frames=4190, freeze=None, **kw):
    """Run the G3 decode body on synthetic frames + fake chain; return (rc, out_root)."""
    cfg = _write_g3_config(tmp)
    frz = freeze if freeze is not None else m.load_freeze_config(cfg)
    out_root = tmp / "out_g3d"
    chain, truth = _fake_g3_chain(scripts)
    rc = m.run_stage_g3_decode(
        acq_id=m.G3_TARGET_ACQ, out_root=out_root, freeze=frz, options={},
        _decode_chain=chain, _frames_bundle=_g3d_frames_bundle(n_frames),
        _config_path=cfg, **kw,
    )
    return rc, out_root, truth


# ------------------------------------------------------- 1 freeze keys + K

def test_freeze_19_keys_enforced():
    assert len(m.REQUIRED_FREEZE_KEYS) == 19
    full = _full_g3_freeze()
    assert m._missing_freeze_keys(full) == []
    for drop in (["tag_master"], ["g2_arms", "g2_blocks"]):
        cfg = {k: v for k, v in full.items() if k not in drop}
        assert m._missing_freeze_keys(cfg) == sorted(drop)
    nul = dict(full)
    nul["B_tail"] = None
    assert m._missing_freeze_keys(nul) == ["B_tail"]
    with _tmp() as tmp:
        p = _write_g3_config(tmp)
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


# ------------------------------------------------------- 2 stage-keyed routing + acq pin

def test_stage_keyed_routing():
    with _tmp() as tmp:
        assert m.check_g3_config_route(tmp / "g3_freeze_config.json") is None
        assert m.check_g3_config_route(tmp / "freeze.json") is not None
        assert m.check_g3_config_route(None) is not None
        # G1/G1R2/G2 packet-dir paths never route, even with a G3 name.
        for foreign in (
            G1_PACKET_DIR / "g1_freeze_config.json",
            G1R2_PACKET_DIR / "g1r2_freeze_config.json",
            G2_PACKET_DIR / "g2_freeze_config.json",
            G1_PACKET_DIR / "g3_freeze_config.json",
            G1R2_PACKET_DIR / "g3_freeze_config.json",
            G2_PACKET_DIR / "g3_freeze_config.json",
        ):
            assert m.check_g3_config_route(foreign) is not None, foreign
        # A non-G3 freeze exits 3 with zero contact.
        out_root = tmp / "never_created"
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc = m.run_stage_g3(
                acq_id=m.G3_TARGET_ACQ, out_root=out_root,
                freeze={k: f"value-{k}" for k in m.REQUIRED_FREEZE_KEYS},
                options={}, _config_path=tmp / "freeze.json",
            )
        assert rc == 3, rc
        assert "STAGE_BODY_PENDING_FREEZE" in buf.getvalue()
        assert not out_root.exists()


def test_acq_pin_single_target():
    with _tmp() as tmp:
        cfg = _write_g3_config(tmp)
        freeze = m.load_freeze_config(cfg)
        out_root = tmp / "out_acq"
        buf = io.StringIO()
        try:
            with contextlib.redirect_stderr(buf):
                m.run_stage_g3(
                    acq_id="20260113_SHG_Type2PPLN_3s", out_root=out_root,
                    freeze=freeze, options={}, _config_path=cfg,
                )
        except SystemExit as exc:
            assert exc.code == 2, exc.code
        else:
            raise AssertionError("off-target acq must exit(2)")
        assert "SHG" in buf.getvalue()
        assert not out_root.exists()


def test_g3_freeze_content_pins():
    with _tmp() as tmp:
        cfg = _write_g3_config(tmp)
        freeze = m.load_freeze_config(cfg)
        pkt = tmp / "pkt"
        pkt.mkdir()
        tA, tB = _synthetic_coincident_timetags(300)
        kw = dict(
            acq_id=m.G3_TARGET_ACQ, freeze=freeze, options={},
            _read_timetags=_fake_reader(tA, tB),
            _align_fn=_fake_align(), _sweep_fn=_fake_sweep(),
            _packet_dir=pkt, _config_path=cfg,
        )
        # tag_master drift (e.g. the G2 value) is refused, exit 2.
        bad = dict(freeze, tag_master=2026103001)
        err = _expect_exit2(lambda: m.run_stage_g3(
            out_root=tmp / "o1", **{**kw, "freeze": bad}))
        assert "tag_master" in err, err
        # window drift is refused, exit 2 (never a silent fallback).
        bad = dict(freeze, pairing_window_primary=500)
        err = _expect_exit2(lambda: m.run_stage_g3(
            out_root=tmp / "o2", **{**kw, "freeze": bad}))
        assert "pairing_window_primary" in err, err
        # G3 tag/seed arithmetic pinned.
        assert m.G3_TAG_MASTER == m.G3_EVAL_SEED + 10000 == 2026110101
        assert m.G3_EVAL_SEED == 2026100101


# ------------------------------------------------------- 3 signature pinning (G2 lesson)

def test_fake_signatures_pin_frozen_calls():
    # Every fake seam above must pin the REAL call signature it
    # substitutes (names + arity). The G2 defect (polar_transform()
    # missing keyword-only `field`) was hidden by a single-arg identity
    # lambda double; these pins fail loudly here instead of at Phase A.
    assert list(inspect.signature(m._read_timetags_g3_production).parameters) == ["acq_id"]
    assert list(inspect.signature(m._align_frozen).parameters) == ["tA", "tB"]
    assert list(inspect.signature(m._yield_sweep_selfcheck).parameters) == [
        "tA", "tB", "derived_offset"]
    tA0 = np.array([0, 1000], dtype=np.int64)
    tB0 = np.array([50, 1050], dtype=np.int64)
    r = _fake_reader(tA0, tB0)
    assert list(inspect.signature(r).parameters) == ["acq_id"]
    got = r("SYNTH")
    assert got["tA"].tolist() == [0, 1000] and got["tB"].tolist() == [50, 1050]
    a = _fake_align()
    assert list(inspect.signature(a).parameters) == ["tA", "tB"]
    assert set(a(tA0, tB0)) >= {"peak_center_ps", "peak_sigma_ps", "peak_to_bg", "status"}
    s = _fake_sweep()
    assert list(inspect.signature(s).parameters) == ["tA", "tB", "derived_offset"]
    assert set(s(tA0, tB0, 50)) >= {"yield_at_derived", "yield_max",
                                    "within_one_step_of_max_ok"}
    # The G3 closure takes NO decode chain and NO polar function: the
    # G2 defect class (wrong fake call shape reaching a decoder) cannot
    # recur on this path by construction.
    for fn in (m.run_stage_g3, m.run_g3_closure):
        params = set(inspect.signature(fn).parameters)
        assert "polar_fn" not in params, fn
        assert "_decode_chain" not in params, fn
        assert "chain" not in params, fn


# ------------------------------------------------------- 4 closure success (synthetic)

def test_closure_success_synthetic():
    # Ledger shaped like the real `_2` expectation: 4289 post-skip
    # frames (reserve 4190-4288, 99 ids), 14 complete EVAL blocks.
    n_pairs = 702 * 256 + 4289 * 256 + 10
    tA, tB = _synthetic_coincident_timetags(n_pairs)
    alice, bob = m.pair_narrow_nearest_unique(tA, tB, 50, 200)
    assert int(alice.size) == n_pairs, (int(alice.size), n_pairs)
    gate = {
        "peak_center_ps": 50,
        "peak_sigma_ps": 114.5,
        "status": "ok",
        "n_pairs": int(alice.size),
        "n_frames": int(alice.size) // 256,
    }
    old_gate = m.G3_REPRO_GATE
    m.G3_REPRO_GATE = gate
    try:
        before = _snapshot_packet_dirs()
        with _tmp() as tmp:
            cfg = _write_g3_config(tmp)
            freeze = m.load_freeze_config(cfg)
            out_root = tmp / "out"
            pkt = tmp / "pkt"
            pkt.mkdir()
            rc = m.run_stage_g3(
                acq_id=m.G3_TARGET_ACQ, out_root=out_root, freeze=freeze,
                options={},
                _read_timetags=_fake_reader(tA, tB),
                _align_fn=_fake_align(center=50, sigma=114.5),
                _sweep_fn=_fake_sweep(),
                _packet_dir=pkt, _config_path=cfg,
            )
            assert rc == 0, rc
            for name in ("g3.json", "cal_ids.json", "run_log.md"):
                assert (out_root / name).is_file(), name
            g3 = json.loads((out_root / "g3.json").read_text(encoding="utf-8"))
            assert g3["packet"] == "NBPOLAR-M2-PRIOR-G3-CONFIRM"
            assert g3["mode"] == "closure-only"
            assert g3["acq_id"] == m.G3_TARGET_ACQ
            assert g3["reproduction_gate"]["verdict"] == "REPRODUCED"
            assert g3["reproduction_gate"]["match5"] is True
            assert g3["ledger"]["complete_frames"] == 4289, g3["ledger"]
            assert g3["n_eval_blocks"] == 14
            assert g3["eval_blocks"] == m.g2_eval_blocks()
            assert g3["eval_blocks"][-1] == [4062, 4189]
            assert g3["disjointness_all_disjoint"] is True
            assert "decoder/model independence" in g3["participation_disclosure"]
            assert "NOT no-prior-contact independence" in g3["participation_disclosure"]
            cal = json.loads((out_root / "cal_ids.json").read_text(encoding="utf-8"))
            assert cal["a1_cal_ids"] == list(range(0, 1024))
            assert cal["cal_frame_ids"] == list(range(1024, 1056))
            assert cal["heldout_frame_ids"] == list(range(1838, 2398))
            assert cal["eval_blocks"] == m.g2_eval_blocks()
            assert cal["reserve_frame_ids"] == list(range(4190, 4289)), (
                cal["reserve_frame_ids"][:3], cal["reserve_frame_ids"][-3:])
            assert len(cal["disjointness_matrix"]["pairwise_overlap"]) == 10
            assert "decoder/model independence" in cal["participation_disclosure"]
            log = (out_root / "run_log.md").read_text(encoding="utf-8")
            assert "decoder/model independence" in log
            # Packet-dir config: all 19 keys non-null + eval_blocks extra.
            emitted = json.loads((pkt / "g3_freeze_config.json").read_text(encoding="utf-8"))
            assert m._missing_freeze_keys(emitted) == []
            assert emitted["tag_master"] == 2026110101
            assert emitted["eval_blocks"] == m.g2_eval_blocks()
            assert "decoder/model independence" in emitted["participation_disclosure"]
        _assert_packet_dirs_untouched(before)
    finally:
        m.G3_REPRO_GATE = old_gate


def test_closure_repro_mismatch_stops_loudly():
    n_pairs = 702 * 256 + 4289 * 256 + 10
    tA, tB = _synthetic_coincident_timetags(n_pairs)
    alice, _ = m.pair_narrow_nearest_unique(tA, tB, 50, 200)
    gate = {
        "peak_center_ps": 50,
        "peak_sigma_ps": 114.5,
        "status": "ok",
        "n_pairs": int(alice.size),
        "n_frames": int(alice.size) // 256,
    }
    old_gate = m.G3_REPRO_GATE
    m.G3_REPRO_GATE = gate
    try:
        before = _snapshot_packet_dirs()
        with _tmp() as tmp:
            cfg = _write_g3_config(tmp)
            freeze = m.load_freeze_config(cfg)
            out_root = tmp / "out"
            pkt = tmp / "pkt"
            pkt.mkdir()
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                rc = m.run_stage_g3(
                    acq_id=m.G3_TARGET_ACQ, out_root=out_root, freeze=freeze,
                    options={},
                    _read_timetags=_fake_reader(tA, tB),
                    _align_fn=_fake_align(center=50, sigma=999.0),
                    _sweep_fn=_fake_sweep(),
                    _packet_dir=pkt, _config_path=cfg,
                )
            assert rc == 1, rc
            assert "ALIGN_INCONSISTENT" in buf.getvalue(), buf.getvalue()
            g3 = json.loads((out_root / "g3.json").read_text(encoding="utf-8"))
            assert g3["verdict"] == "ALIGN_INCONSISTENT", g3
            assert "decoder/model independence" in g3["participation_disclosure"]
            # Failure path flushes forensics but NEVER the packet-dir config.
            assert not (pkt / "g3_freeze_config.json").exists()
        _assert_packet_dirs_untouched(before)
    finally:
        m.G3_REPRO_GATE = old_gate


def test_closure_insufficient_records_inconclusive():
    tA, tB = _synthetic_coincident_timetags(1000)
    alice, _ = m.pair_narrow_nearest_unique(tA, tB, 50, 200)
    gate = {
        "peak_center_ps": 50,
        "peak_sigma_ps": 114.5,
        "status": "ok",
        "n_pairs": int(alice.size),
        "n_frames": int(alice.size) // 256,
    }
    old_gate = m.G3_REPRO_GATE
    m.G3_REPRO_GATE = gate
    try:
        with _tmp() as tmp:
            cfg = _write_g3_config(tmp)
            freeze = m.load_freeze_config(cfg)
            out_root = tmp / "out"
            pkt = tmp / "pkt"
            pkt.mkdir()
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                rc = m.run_stage_g3(
                    acq_id=m.G3_TARGET_ACQ, out_root=out_root, freeze=freeze,
                    options={},
                    _read_timetags=_fake_reader(tA, tB),
                    _align_fn=_fake_align(center=50, sigma=114.5),
                    _sweep_fn=_fake_sweep(),
                    _packet_dir=pkt, _config_path=cfg,
                )
            assert rc == 1, rc
            assert "INSUFFICIENT" in buf.getvalue(), buf.getvalue()
            g3 = json.loads((out_root / "g3.json").read_text(encoding="utf-8"))
            assert g3["verdict"] == "INCONCLUSIVE", g3
            assert "INSUFFICIENT" in g3["reason"], g3
            assert not (pkt / "g3_freeze_config.json").exists()
    finally:
        m.G3_REPRO_GATE = old_gate


# ------------------------------------------------------- 5 Wilson reuse (not rewritten)

def test_wilson_gate_reused_not_rewritten():
    assert m.eval_g2_gate(14, 0)["verdict"] == "SUCCESS"
    assert m.eval_g2_gate(7, 7)["verdict"] == "FAIL"
    assert m.eval_g2_gate(0, 14)["verdict"] == "FAIL"
    assert m.eval_g2_gate(8, 7)["verdict"] == "INCONCLUSIVE"
    assert m.eval_g2_gate(14, 13)["verdict"] == "INCONCLUSIVE"
    z0 = m.wilson_interval(0, 14)
    assert z0["lower"] == 0.0 and abs(z0["upper"] - 0.21533) < 1e-4, z0
    # The G3 record carries the carried caveats verbatim.
    assert "M2 is a CANDIDATE" in m.G3_CAVEATS
    assert "decoder/model independence" in m.G3_CAVEATS


# ------------------------------------------------------- 6 CLI exit codes

def _run_cli(*args):
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        capture_output=True, text=True, timeout=120,
    )


def test_cli_exit_codes_no_side_effects():
    with _tmp() as tmp:
        assert _run_cli("--help").returncode == 0
        cfg = _write_g3_config(tmp)
        # No --authorized: exit 2 before any read/create.
        out_root = tmp / "out_noauth"
        proc = _run_cli(
            "--stage-g3-closure", "--freeze-config", str(cfg),
            "--acq-id", m.G3_TARGET_ACQ, "--out-root", str(out_root),
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "--authorized" in proc.stderr
        assert not out_root.exists()
        # --closure-only is G1-only: hard refusal with G3.
        out_root2 = tmp / "out_closure"
        proc = _run_cli(
            "--stage-g3-closure", "--freeze-config", str(cfg),
            "--acq-id", m.G3_TARGET_ACQ, "--out-root", str(out_root2),
            "--closure-only", "--authorized",
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "--closure-only" in proc.stderr
        assert not out_root2.exists()
        # K pin: exit 2, names 319, creates nothing.
        out_root3 = tmp / "out_k"
        proc = _run_cli(
            "--stage-g3-closure", "--freeze-config", str(cfg),
            "--acq-id", m.G3_TARGET_ACQ, "--out-root", str(out_root3),
            "--k1", "320", "--k2", "6492", "--authorized",
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "319" in proc.stderr
        assert not out_root3.exists()
        # Unrouted freeze name: exit 3, zero contact.
        other = tmp / "freeze.json"
        other.write_text(cfg.read_text(encoding="utf-8"), encoding="utf-8")
        out_root4 = tmp / "out_route"
        proc = _run_cli(
            "--stage-g3-closure", "--freeze-config", str(other),
            "--acq-id", m.G3_TARGET_ACQ, "--out-root", str(out_root4),
            "--authorized",
        )
        assert proc.returncode == 3, (proc.returncode, proc.stderr)
        assert "STAGE_BODY_PENDING_FREEZE" in proc.stderr
        assert not out_root4.exists()


# ------------------------------------------------------- 7 purity: no decode here

def test_import_purity_entry_shape_and_decode_flag():
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
    assert m.FLAG_G3 == "--stage-g3-closure"
    assert m.FLAG_G3D == "--stage-g3-decode"
    # Phase-B decode IS implemented in this dispatch: the flag must be a
    # registered CLI spelling (checked against live --help), distinct
    # from the closure flag.
    help_proc = subprocess.run(
        [sys.executable, str(RUNNER), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert help_proc.returncode == 0, help_proc.stderr
    assert "--stage-g3-closure" in help_proc.stdout, help_proc.stdout
    assert "--stage-g3-decode" in help_proc.stdout, help_proc.stdout
    # This test file itself: no TimeTagger/Swabian import, no production
    # decoder entry — tests can never enter production decode. (Code
    # references only: docstrings/comments/strings are Constants, never
    # Name or Attribute nodes, so prose cannot trip this pin. Keyword
    # spellings such as sc_decode=... are ast.keyword nodes, not Names.)
    tsrc = Path(__file__).read_text(encoding="utf-8")
    ttree = ast.parse(tsrc)
    for node in ast.walk(ttree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert a.name.split(".")[0] not in ("TimeTagger", "Swabian"), a.name
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in (
                "TimeTagger", "Swabian"), node.module
        elif isinstance(node, (ast.Name, ast.Attribute)):
            ident = node.id if isinstance(node, ast.Name) else node.attr
            assert ident not in ("_load_g2_decoder_chain", "sc_decode",
                                 "run_operational_block", "toeplitz_tag"), ident
    # The file never CALLS the production loader (string pins elsewhere
    # are literal references only, never calls).
    for node in ast.walk(ttree):
        if isinstance(node, ast.Call):
            fn = node.func
            ident = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", "")
            assert ident != "_load_g2_decoder_chain", "test must never call the loader"


# ------------------------------------------------------- 8 Phase-B decode body

def test_g3d_flag_registered_distinct_from_closure():
    assert m.FLAG_G3D == "--stage-g3-decode"
    assert m.FLAG_G3 == "--stage-g3-closure"
    assert m.FLAG_G3D != m.FLAG_G3
    assert callable(m.run_stage_g3_decode)
    params = set(inspect.signature(m.run_stage_g3_decode).parameters)
    assert {"acq_id", "out_root", "freeze", "options",
            "_decode_chain", "_frames_bundle", "_config_path"} <= params, params
    assert "polar_fn" not in params and "chain" not in params, params


def test_g3d_stage_keyed_routing_zero_contact():
    with _tmp() as tmp:
        assert m.check_g3_config_route(tmp / "g3_freeze_config.json") is None
        # G1/G1R2/G2 packet-dir paths never route, even with a G3 name.
        for foreign in (
            G1_PACKET_DIR / "g1_freeze_config.json",
            G1R2_PACKET_DIR / "g1r2_freeze_config.json",
            G2_PACKET_DIR / "g2_freeze_config.json",
            G1_PACKET_DIR / "g3_freeze_config.json",
            G1R2_PACKET_DIR / "g3_freeze_config.json",
            G2_PACKET_DIR / "g3_freeze_config.json",
        ):
            assert m.check_g3_config_route(foreign) is not None, foreign
        # Unrouted freeze name: exit 3, zero contact.
        out_root = tmp / "never_created_g3d"
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc = m.run_stage_g3_decode(
                acq_id=m.G3_TARGET_ACQ, out_root=out_root,
                freeze={k: f"value-{k}" for k in m.REQUIRED_FREEZE_KEYS},
                options={}, _config_path=tmp / "freeze.json",
            )
        assert rc == 3, rc
        assert "STAGE_BODY_PENDING_FREEZE" in buf.getvalue()
        assert not out_root.exists()


def test_g3d_acq_pin_and_reader_single_target():
    with _tmp() as tmp:
        cfg = _write_g3_config(tmp)
        freeze = m.load_freeze_config(cfg)
        # Stage-level: off-target acq exits 2, creates nothing.
        out_root = tmp / "out_acq_g3d"
        buf = io.StringIO()
        try:
            with contextlib.redirect_stderr(buf):
                m.run_stage_g3_decode(
                    acq_id="20260113_SHG_Type2PPLN_3s", out_root=out_root,
                    freeze=freeze, options={}, _config_path=cfg,
                )
        except SystemExit as exc:
            assert exc.code == 2, exc.code
        else:
            raise AssertionError("off-target G3 decode acq must exit(2)")
        assert "SHG" in buf.getvalue()
        assert not out_root.exists()
        # Reader-level single-target pin: ONLY SHG `_2` passes the guard.
        # The refusal precedes the TimeTagger shim, so no import happens.
        before = _snapshot_packet_dirs()
        err = _expect_exit2(
            lambda: m._read_timetags_g3_production("20260113_SHG_Type2PPLN_3s_1"))
        assert "20260113_SHG_Type2PPLN_3s_2" in err, err
        assert list(inspect.signature(m._read_timetags_g3_production).parameters) == ["acq_id"]
        _assert_packet_dirs_untouched(before)


def test_g3d_freeze_pins_k_and_arms_spelling():
    with _tmp() as tmp:
        cfg = _write_g3_config(tmp)
        freeze = m.load_freeze_config(cfg)
        kw = dict(acq_id=m.G3_TARGET_ACQ, options={}, _config_path=cfg)
        # tag_master drift (e.g. the G2 value) is refused, exit 2.
        bad = dict(freeze, tag_master=2026103001)
        err = _expect_exit2(lambda: m.run_stage_g3_decode(
            out_root=tmp / "o1", freeze=bad, **kw))
        assert "tag_master" in err, err
        assert not (tmp / "o1").exists()
        # window drift is refused, exit 2 (never a silent fallback).
        bad = dict(freeze, pairing_window_primary=500)
        err = _expect_exit2(lambda: m.run_stage_g3_decode(
            out_root=tmp / "o2", freeze=bad, **kw))
        assert "pairing_window_primary" in err, err
        # shorthand arms do NOT satisfy the verbatim guard (exit 2 if
        # passed); the full frozen triple passes the cross-check.
        mism = m._cross_check_mismatches({"arms": "A1,A2,B"}, freeze)
        assert len(mism) == 1 and "g2_arms" in mism[0], mism
        ok = m._cross_check_mismatches(
            {"arms": "A1_M0_1024f_incumbent,A2_M0_32f_matched,B_M2_32f_candidate"},
            freeze,
        )
        assert ok == []
        bad = dict(freeze, g2_arms=["A1", "A2", "B"])
        err = _expect_exit2(lambda: m.run_stage_g3_decode(
            out_root=tmp / "o3", freeze=bad, **kw))
        assert "g2_arms" in err, err
        # K pin + tag/seed arithmetic re-checked for the decode stage.
        m._check_k_pin("319", "6492")
        assert m.G3_TAG_MASTER == m.G3_EVAL_SEED + 10000 == 2026110101
        assert m.G3_EVAL_SEED == 2026100101
        # 19-key null/absent stays exit 2 on the decode path (via loader).
        q = tmp / "bad19.json"
        q.write_text(json.dumps(
            {k: v for k, v in freeze.items() if k != "skip_frames"}),
            encoding="utf-8")
        err = _expect_exit2(lambda: m.load_freeze_config(q))
        assert "skip_frames" in err


def _frozen_source_sig(relpath, funcname):
    """Static signature of a frozen function: [(name, kind)] (no import).

    Parses the frozen SOURCE with ast — the module is never imported, so
    this pins fake call shapes against the real frozen files with zero
    decoder entry and zero third-party imports (no pandas). Kinds are
    "pos" (positional-or-keyword) or "kwonly".
    """
    tree = ast.parse((REPO_ROOT / relpath).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == funcname:
            params = [(a.arg, "pos") for a in node.args.args]
            params += [(a.arg, "kwonly") for a in node.args.kwonlyargs]
            return params
    raise AssertionError(f"{funcname} not found in {relpath}")


def test_g3d_fake_signatures_pin_every_substituted_frozen_call():
    # Every frozen call the G3 decode substitutes through the fake chain
    # must match the REAL signature (names + keyword-only-ness). The G2
    # defect (polar_transform() missing keyword-only `field`) was hidden
    # by a single-arg identity-lambda double; these pins fail loudly
    # here instead of at the one-shot decode. Real shapes come from
    # static source parses (never an import: no pandas, no decoder
    # entry); fake shapes from inspect. Attribute access to the fake
    # entries uses getattr() with string literals so this file's own
    # purity pin (no Name/Attribute decoder entries) keeps holding.
    nb = "comparison_bench/src/comparison_bench/formal_ir/nbpolar"
    fir = "comparison_bench/src/comparison_bench/formal_ir"
    real_polar = _frozen_source_sig(f"{nb}/transform.py", "polar_transform")
    assert real_polar[0] == ("symbols", "pos"), real_polar
    assert dict(real_polar[1:]) == {"field": "kwonly", "alpha": "kwonly"}, real_polar
    real_sc = _frozen_source_sig(f"{nb}/sc.py", "sc_decode")
    assert real_sc[0] == ("logp_x", "pos"), real_sc
    assert dict(real_sc[1:]) == {
        "field": "kwonly", "alpha": "kwonly",
        "known_positions": "kwonly", "known_values": "kwonly"}, real_sc
    real_verify = _frozen_source_sig(
        f"{nb}/operational_f13_replication.py", "verify_predecessor_construction")
    assert real_verify[0] == ("construction_path", "pos"), real_verify
    assert dict(real_verify[1:]) == {"expected_digest": "kwonly"}, real_verify
    real_block = _frozen_source_sig(f"{nb}/operational_f13.py", "run_operational_block")
    assert [n for n, k in real_block if k == "pos"] == [], real_block
    assert {"n", "bob", "master", "tag_fn", "calls", "k1", "k2"} <= {
        n for n, _ in real_block}, real_block
    real_tag = _frozen_source_sig(f"{fir}/shared.py", "toeplitz_tag")
    assert [n for n, _ in real_tag][:2] == ["bits", "seed_bits"], real_tag
    real_l2b = _frozen_source_sig(f"{nb}/two_layer.py", "labels_to_bits")
    assert real_l2b[0] == ("labels", "pos"), real_l2b
    assert list(inspect.signature(m.run_g2_block).parameters) == [
        "arm", "block_index", "eval_frames", "bob", "alice", "fit",
        "p1_table", "p2_table", "l1_order", "l2_order", "k1", "k2",
        "tag_master", "eval_seed", "chain", "polar_fn", "prior_mod"]
    # The fake chain exposes every substituted entry with a matching
    # call shape (keyword-only-ness included).
    chain, _ = _fake_g3_chain()
    for attr in ("run_operational_block", "sc_decode", "toeplitz_tag",
                 "make_gf32", "labels_to_bits",
                 "verify_predecessor_construction", "polar_transform", "alpha"):
        assert hasattr(chain, attr), attr
    fake_polar = getattr(chain, "polar_transform")
    assert list(inspect.signature(fake_polar).parameters) == ["v", "field", "alpha"]
    assert inspect.signature(
        fake_polar).parameters["field"].kind == inspect.Parameter.KEYWORD_ONLY
    fake_sc = getattr(chain, "sc_decode")
    assert list(inspect.signature(fake_sc).parameters) == [
        "logp", "field", "alpha", "known_positions", "known_values"]
    assert {n for n, p in inspect.signature(fake_sc).parameters.items()
            if p.kind == inspect.Parameter.KEYWORD_ONLY} == {
        "field", "alpha", "known_positions", "known_values"}
    fake_verify = getattr(chain, "verify_predecessor_construction")
    assert list(inspect.signature(fake_verify).parameters) == ["path", "expected_digest"]
    assert inspect.signature(
        fake_verify).parameters[
        "expected_digest"].kind == inspect.Parameter.KEYWORD_ONLY
    # A single-arg polar double (the G2 defect shape) fails loudly.
    try:
        fake_polar(np.array([1, 2], dtype=np.int64))
    except TypeError as exc:
        assert "field" in str(exc)
    else:
        raise AssertionError("keyword-only field must be required by the fake")
    # The bound binder carries field/alpha as keywords (frozen contract).
    seen = {}

    def strict_polar(v, *, field, alpha=2):
        seen["field"] = field
        seen["alpha"] = alpha
        return np.asarray(v).copy()

    vec = np.array([3, 31, 0, 7], dtype=np.int64)
    bound = m._bind_g2_polar(strict_polar, object(), 2)
    assert bound(vec).tolist() == vec.tolist()
    assert seen["field"] is not None and seen["alpha"] == 2


def test_g3d_decode_body_reuses_g2_machinery():
    src = inspect.getsource(m.run_stage_g3_decode)
    for reused in ("_load_g2_decoder_chain", "fit_g2_arm", "_bind_g2_polar",
                   "run_g2_eval", "eval_g2_gate", "recount_g2_disclosure",
                   "g2_eval_blocks", "g2_cal_ids", "stamp_g3_record_domains"):
        assert reused in src, f"G3 decode must reuse {reused}"
    # No nested machinery: exactly one FunctionDef (the body itself).
    tree = ast.parse(src)
    assert sum(isinstance(n, ast.FunctionDef) for n in ast.walk(tree)) == 1
    # No rewritten gate/recount/layout: the single definitions live once.
    mod_src = inspect.getsource(m)
    assert mod_src.count("def wilson_interval") == 1
    assert mod_src.count("def eval_g2_gate") == 1
    assert mod_src.count("def recount_g2_disclosure") == 1
    assert mod_src.count("def run_g2_eval") == 1
    assert mod_src.count("def run_g2_block") == 1


def _wilson_g3d_independent(k, n, z=1.96):
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def test_g3d_wilson_gate_hand_computed():
    for k, n in ((0, 14), (14, 14), (7, 14), (8, 14), (3, 14), (11, 14), (1, 14)):
        got = m.wilson_interval(k, n)
        lo, hi = _wilson_g3d_independent(k, n)
        assert abs(got["lower"] - lo) <= 1e-12, (k, got, lo)
        assert abs(got["upper"] - hi) <= 1e-12, (k, got, hi)
        assert abs(got["p_hat"] - k / n) <= 1e-15
    # Boundaries clamp (hand values from the G2 suite).
    z0 = m.wilson_interval(0, 14)
    assert z0["lower"] == 0.0 and abs(z0["upper"] - 0.21533) < 1e-4, z0
    z14 = m.wilson_interval(14, 14)
    assert z14["upper"] == 1.0 and abs(z14["lower"] - 0.78467) < 1e-4, z14
    # Preregistered gate: strict non-overlap SUCCESS; point(B)<=point(A2)
    # FAIL; better-point overlap INCONCLUSIVE. A1 descriptive, no gate.
    assert m.eval_g2_gate(14, 0)["verdict"] == "SUCCESS"
    assert m.eval_g2_gate(14, 7)["verdict"] == "SUCCESS"
    assert m.eval_g2_gate(7, 7)["verdict"] == "FAIL"
    assert m.eval_g2_gate(0, 14)["verdict"] == "FAIL"
    assert m.eval_g2_gate(13, 14)["verdict"] == "FAIL"
    assert m.eval_g2_gate(8, 7)["verdict"] == "INCONCLUSIVE"
    assert m.eval_g2_gate(14, 13)["verdict"] == "INCONCLUSIVE"
    for b, a in ((14, 0), (14, 7), (8, 7), (7, 7), (13, 14), (0, 14), (14, 13)):
        g = m.eval_g2_gate(b, a)
        blo, _bhi = _wilson_g3d_independent(b, 14)
        _alo, ahi = _wilson_g3d_independent(a, 14)
        assert (g["verdict"] == "SUCCESS") == (blo > ahi), (b, a, g)
        assert (g["verdict"] == "FAIL") == (not (blo > ahi) and b / 14 <= a / 14), (b, a, g)


def test_g3d_success_shape_domains_caveats_counts():
    with _tmp() as tmp:
        # A2 exact on 7/14 only; B exact on 14/14 -> SUCCESS.
        scripts = {
            ("A2_M0_32f_matched", b): "verify_failed" for b in range(7, 14)
        }
        rc, out_root, truth = _run_g3d_stage(tmp, scripts)
        assert rc == 0, rc
        rows = (out_root / "per_block_outcomes.jsonl").read_text(
            encoding="utf-8").splitlines()
        assert len(rows) == 42, len(rows)
        # 3 SC calls per block x 42 blocks = 126; one tag per block.
        recs = [json.loads(r) for r in rows]
        assert all(r["sc_calls"] == 3 for r in recs), [r["sc_calls"] for r in recs]
        # NLL domain labels + participation disclosure on EVERY row.
        for r in recs:
            assert "u1" in r["nll_l2_trueH_domain"], r
            assert "high_hat" in r["nll_l2_candH_domain"], r
            assert "decoder/model independence" in r["participation_disclosure"], r
            assert "NOT no-prior-contact independence" in r["participation_disclosure"], r
        # Full measurement set present per block.
        for key in ("l1_exact", "hard_l2_exact", "oracle_l2_exact",
                    "pair_exact", "first_error_coordinate", "first_error_layer",
                    "n_raw_zero_hits", "floor_logloss_bits",
                    "nll_l2_trueH_bits", "nll_l2_candH_bits",
                    "tag_invoked", "key_dependent_bits", "wall_s"):
            assert all(key in r for r in recs), key
        summary = json.loads((out_root / "g3_summary.json").read_text(encoding="utf-8"))
        assert summary["packet"] == "NBPOLAR-M2-PRIOR-G3-CONFIRM"
        assert summary["acq_id"] == m.G3_TARGET_ACQ
        assert summary["verdict"] == "SUCCESS", summary["gate"]
        assert summary["nature"].startswith("Tier-Y")
        assert "M2 CANDIDATE" in summary["nature"]
        assert summary["arms"]["A1_M0_1024f_incumbent"]["exact"] == 14
        assert summary["arms"]["A1_M0_1024f_incumbent"]["mode"] == "M0"
        assert summary["arms"]["A2_M0_32f_matched"]["exact"] == 7
        assert summary["arms"]["B_M2_32f_candidate"]["exact"] == 14
        assert summary["arms"]["B_M2_32f_candidate"]["mode"] == "M2"
        assert summary["arms"]["B_M2_32f_candidate"]["undetected"] == 0
        assert summary["disclosure_recount"]["mismatches"] == []
        assert summary["construction"]["inner_digest"] == (
            "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
        )
        assert summary["construction"]["k1"] == 319
        assert summary["construction"]["k2"] == 6492
        assert "M2 is a CANDIDATE" in summary["caveats"]
        assert "decoder/model independence" in summary["caveats"]
        assert "decoder/model independence" in summary["participation_disclosure"]
        assert summary["calls"]["sc_calls"] == 42 * 3, summary["calls"]
        assert summary["calls"]["tag_invocations"] == 42, summary["calls"]
        assert summary["timing"]["wall_budget_s"] == 900.0
        assert summary["timing"]["rss_budget_gib"] == 2.0
        assert "u1" in summary["nll_domains"]["nll_l2_trueH_bits"]
        assert "high_hat" in summary["nll_domains"]["nll_l2_candH_bits"]
        # Frozen seeds reach the production call shape (G3 values).
        for (arm, blk), call in truth.items():
            assert call["master"] == 2026110101, (arm, blk, call)
            assert call["stream_seed"] == 2026100101, (arm, blk, call)
            assert (call["k1"], call["k2"]) == (319, 6492), (arm, blk, call)
        assert len(truth) == 42
        log = (out_root / "run_log.md").read_text(encoding="utf-8")
        assert "gate: SUCCESS" in log, log.splitlines()[3:6]
        assert "decoder/model independence" in log
        assert "M2 is a CANDIDATE" in log
        assert "sc_calls=126" in log
        cal = json.loads((out_root / "cal_ids.json").read_text(encoding="utf-8"))
        assert "decoder/model independence" in cal["participation_disclosure"]
        assert cal["eval_blocks"] == m.g2_eval_blocks()


def test_g3d_taxonomy_undetected_isolated_gate_exact_only():
    with _tmp() as tmp:
        # B 13 exact + 1 undetected vs A2 14 exact: gate sees 13 vs 14
        # (point below -> FAIL); undetected never merges into success.
        scripts = {("B_M2_32f_candidate", 13): "undetected"}
        for b in range(14):
            scripts.setdefault(("A2_M0_32f_matched", b), "exact")
        rc, out_root, _ = _run_g3d_stage(tmp, scripts)
        assert rc == 0, rc
        summary = json.loads((out_root / "g3_summary.json").read_text(encoding="utf-8"))
        assert summary["verdict"] == "FAIL", summary["gate"]
        b = summary["arms"]["B_M2_32f_candidate"]
        assert b["exact"] == 13 and b["undetected"] == 1, b
        assert b["outcomes"]["undetected"] == 1
        assert b["outcomes"]["exact"] == 13
        assert set(b["outcomes"]) == set(m.G2_OUTCOMES), b["outcomes"]
        assert len(b["outcomes"]) == 6
        assert sum(b["outcomes"].values()) == 14
        # Full-bucket sweep on single blocks through the real block body.
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
            k1=3, k2=5, tag_master=m.G3_TAG_MASTER, eval_seed=m.G3_EVAL_SEED,
            polar_fn=lambda v: np.asarray(v).copy(), prior_mod=prior_mod,
        )
        for outcome, want_exact, want_und in (
            ("exact", True, False),
            ("undetected", False, True),
            ("verify_failed", False, False),
            ("decode_failed", False, False),
            ("nonfinite", False, False),
        ):
            chain, _ = _fake_g3_chain(
                {("B_M2_32f_candidate", 0): outcome},
                fixed_key=("B_M2_32f_candidate", 0))
            rec = m.run_g2_block(
                arm="B_M2_32f_candidate", block_index=0, chain=chain, **kw)
            assert rec["outcome"] == outcome, (outcome, rec["outcome"])
            assert rec["exact"] is want_exact and rec["undetected"] is want_und, (
                outcome, rec)


def test_g3d_disclosure_recount_rule():
    with _tmp() as tmp:
        rc, out_root, _ = _run_g3d_stage(tmp)
        assert rc == 0, rc
        summary = json.loads((out_root / "g3_summary.json").read_text(encoding="utf-8"))
        assert summary["disclosure_recount"]["mismatches"] == []
        # Pure rule: tampering one row's key bits invalidates the recount.
        recs = [json.loads(r) for r in (out_root / "per_block_outcomes.jsonl").read_text(
            encoding="utf-8").splitlines()]
        assert m.recount_g2_disclosure(recs[:3])["mismatches"] == []
        tampered = [dict(r) for r in recs[:3]]
        tampered[0]["key_dependent_bits"] = 1
        assert m.recount_g2_disclosure(tampered)["mismatches"] != []


def test_g3d_budget_stop_records_blocker():
    old_budget = m.G2_BUDGET_S
    m.G2_BUDGET_S = 0.0
    try:
        with _tmp() as tmp:
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                rc, out_root, _ = _run_g3d_stage(tmp)
            assert rc == 1, rc
            assert "G3_BUDGET_EXCEEDED" in buf.getvalue(), buf.getvalue()
            summary = json.loads((out_root / "g3_summary.json").read_text(
                encoding="utf-8"))
            assert summary["verdict"] == "INCONCLUSIVE", summary
            assert summary["budget_aborted"] is True
            assert summary["calls"]["sc_calls"] == 0
            assert "decoder/model independence" in summary["participation_disclosure"]
            rows = (out_root / "per_block_outcomes.jsonl").read_text(
                encoding="utf-8").splitlines()
            assert len(rows) == 42, len(rows)
            assert all(json.loads(r)["outcome"] == "resource_abort" for r in rows)
    finally:
        m.G2_BUDGET_S = old_budget
    assert m.G2_BUDGET_S == 900.0


def test_g3d_insufficient_records_inconclusive():
    with _tmp() as tmp:
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            rc, out_root, _ = _run_g3d_stage(tmp, n_frames=100)
        assert rc == 1, rc
        assert "G3_INSUFFICIENT" in buf.getvalue(), buf.getvalue()
        summary = json.loads((out_root / "g3_summary.json").read_text(encoding="utf-8"))
        assert summary["verdict"] == "INCONCLUSIVE", summary
        assert "INSUFFICIENT" in summary["reason"], summary
        assert "decoder/model independence" in summary["participation_disclosure"]


def test_g3d_no_foreign_writes_snapshot_out_root_only():
    before = _snapshot_packet_dirs()
    with _tmp() as tmp:
        rc, out_root, _ = _run_g3d_stage(tmp)
        assert rc == 0, rc
        assert {p.name for p in out_root.iterdir()} == {
            "per_block_outcomes.jsonl", "g3_summary.json",
            "cal_ids.json", "run_log.md",
        }, sorted(p.name for p in out_root.iterdir())
        # The G3 out-root is the ONLY tree written: nothing under any
        # packet dir (G1/G1R2/G2/G3) and no G1/G2-named outputs inside.
        for name in ("g2_summary.json", "g3.json", "g1_freeze_config.json",
                     "g2_freeze_config.json", "g3_freeze_config.json"):
            assert not (out_root / name).exists(), name
    _assert_packet_dirs_untouched(before)


def test_g3d_cli_exit_codes_no_side_effects():
    with _tmp() as tmp:
        cfg = _write_g3_config(tmp)
        # No --authorized: exit 2 before any read/create.
        out_root = tmp / "out_noauth_g3d"
        proc = _run_cli(
            "--stage-g3-decode", "--freeze-config", str(cfg),
            "--acq-id", m.G3_TARGET_ACQ, "--out-root", str(out_root),
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "--authorized" in proc.stderr
        assert not out_root.exists()
        # Missing --freeze-config names the G3 decode flag (stage-aware;
        # the Pre-EXECUTE cosmetic defect is fixed, text only).
        out_root_m = tmp / "out_missing_g3d"
        proc = _run_cli(
            "--stage-g3-decode",
            "--acq-id", m.G3_TARGET_ACQ, "--out-root", str(out_root_m),
            "--authorized",
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "--stage-g3-decode" in proc.stderr, proc.stderr
        assert "--stage-g2-decode" not in proc.stderr, proc.stderr
        assert not out_root_m.exists()
        # --closure-only is G1-only: hard refusal with the G3 decode.
        out_root2 = tmp / "out_closure_g3d"
        proc = _run_cli(
            "--stage-g3-decode", "--freeze-config", str(cfg),
            "--acq-id", m.G3_TARGET_ACQ, "--out-root", str(out_root2),
            "--closure-only", "--authorized",
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "--closure-only" in proc.stderr
        assert not out_root2.exists()
        # K pin: exit 2, names 319, creates nothing.
        out_root3 = tmp / "out_k_g3d"
        proc = _run_cli(
            "--stage-g3-decode", "--freeze-config", str(cfg),
            "--acq-id", m.G3_TARGET_ACQ, "--out-root", str(out_root3),
            "--k1", "320", "--k2", "6492", "--authorized",
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert "319" in proc.stderr
        assert not out_root3.exists()
        # Unrouted freeze name: exit 3, zero contact.
        other = tmp / "freeze.json"
        other.write_text(cfg.read_text(encoding="utf-8"), encoding="utf-8")
        out_root4 = tmp / "out_route_g3d"
        proc = _run_cli(
            "--stage-g3-decode", "--freeze-config", str(other),
            "--acq-id", m.G3_TARGET_ACQ, "--out-root", str(out_root4),
            "--authorized",
        )
        assert proc.returncode == 3, (proc.returncode, proc.stderr)
        assert "STAGE_BODY_PENDING_FREEZE" in proc.stderr
        assert not out_root4.exists()
        # Off-target acq: exit 2, creates nothing.
        out_root5 = tmp / "out_acq_g3d"
        proc = _run_cli(
            "--stage-g3-decode", "--freeze-config", str(cfg),
            "--acq-id", "20260113_SHG_Type2PPLN_3s_1", "--out-root", str(out_root5),
            "--authorized",
        )
        assert proc.returncode == 2, (proc.returncode, proc.stderr)
        assert not out_root5.exists()


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
