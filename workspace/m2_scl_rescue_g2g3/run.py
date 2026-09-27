#!/usr/bin/env python3
"""SCL(L=16, top_m=4, CRC-16) rescue attempt on the 9 known real-data B-arm
``verify_failed`` EVAL blocks from G2 (SHG `_1`) and G3 (SHG `_2`).

Authorization
-------------
PI, in-chat, 2026-09-28 (verbatim, recorded in ``AUTHORIZATION_PROMPT.md``
beside this file): "授权，用 SCL L=16 重解那 9 个失败块，可以继续往下推进".

Question (descriptive, non-claim)
----------------------------------
The 9 B-arm (``B_M2_32f_candidate``, M2 candidate + matched 32-frame CAL,
w=200/CIRCULAR, frozen K1=319/K2=6492, P16 construction) real-data EVAL
blocks that came back ``verify_failed`` under the frozen SC operational
path (G2 blocks 1/5/12; G3 blocks 0/1/2/4/10/11 — see
``workspace/analysis/g2g3-layer-attribution/REPORT.md``) are re-decoded
with a CRC-16-aided two-layer joint SCL decoder
(``comparison_bench/src/comparison_bench/formal_ir/nbpolar/scl_joint.py``,
``scl_joint_decode``, list_width_L=16, top_m=4) on the SAME EVAL data,
SAME CAL-fit M2 prior, SAME frozen P16 orders/K, SAME tag_master/seed per
session. How many of the 9 does it get exactly right (label-exact AND
accepted, where accepted = crc_pass AND tag_pass -- main-thread ruling F1,
2026-09-28, matching the T3 gate convention in
``workspace/probes/scl-gate-t3``)? This is a descriptive count, not a claim:
it does not change
``NBPOLAR_M2_PRIOR_G2_SUCCESS`` / ``NBPOLAR_M2_PRIOR_G3_SUCCESS``, the M2
status ladder, or any G2/G3 Wilson-gate verdict, and it consumes NO new
EVAL data (these 9 blocks were already decoded and recorded by G2/G3).

Reuse discipline (AGENTS.md §5.7, §10.1)
-----------------------------------------
This file imports and calls existing frozen functions; it does not copy
or re-derive any of their logic:

- ``scripts.m2_prior_validation`` (imported as a module, never edited):
  ``_load_g2_decoder_chain`` (frozen decoder chain loader),
  ``_read_timetags_production`` / ``_read_timetags_g3_production``,
  ``_align_frozen``, ``_yield_sweep_selfcheck``, ``_sweep_accept``,
  ``pair_narrow_nearest_unique``, ``chunk_frames``, ``g2_cal_ids``,
  ``fit_g2_arm``, ``_bind_g2_polar``, ``_frozen_m2``, ``_frozen_prior``,
  ``g2_eval_blocks``, ``g2_truth_views``, ``g2_first_error``,
  ``run_g2_block`` (the SAME SC block body G2/G3 used, for the fidelity
  check below), ``build_counts_1024``, ``model_entropy_bits``,
  ``contract_for_freeze``, plus the frozen constants
  (``G2_N``/``G2_K1``/``G2_K2``/``G2_CONSTRUCTION_PATH``/
  ``G2_CONSTRUCTION_DIGEST``/``G2_EVAL_SEED``/``G2_TAG_MASTER``/
  ``G3_EVAL_SEED``/``G3_TAG_MASTER``/``G3_REPRO_GATE``/``G1_FRAME_PAIRS``/
  ``G1_PEAK_TO_BG_MIN``).
- ``comparison_bench...nbpolar.scl_joint``: ``scl_joint_decode``,
  ``labels_crc16`` (loaded via the SAME stub-package technique
  ``_load_g2_decoder_chain`` already uses internally, so the module's own
  relative imports of ``scl``/``two_layer``/``prior`` resolve correctly;
  no frozen file is copied, edited, or reimplemented).

Non-goals / forbidden (frozen; matches TASK_PACKET.md)
-------------------------------------------------------
No change to ``sc.py``/``scl.py``/``scl_joint.py``/``two_layer.py``/
``transform.py``/``algebra.py``/``prior.py``/``prior_m2.py``/
``operational_f13*.py``/``m2_prior_validation.py``. No write under
``results/``, ``comparison_bench/outputs_comparison/``, or any existing
``workspace/m2_prior_validation/...`` directory (this script only READS
those per-block outcome files, for the fidelity check). No change to any
G2/G3 packet dir, STATUS.yaml, or frozen state string. No new EVAL data
(only the 9 already-consumed blocks are touched). One-shot: reruns=0; a
rerun to fix an execution defect (never a parameter/seed change) must be
recorded as a separate attempt, never silently overwritten.

Output
------
``workspace/m2_scl_rescue_g2g3/results.json`` (must be absent before this
script starts) plus one ``part_<SESSION>_<block>.json`` per target block.
Nothing is written outside this directory.
"""

from __future__ import annotations

import importlib
import json
import multiprocessing as mp
import sys
import time
import traceback
from pathlib import Path

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Frozen target set (verbatim from workspace/analysis/g2g3-layer-attribution/
# REPORT.md §3/§4: the 9 B_M2_32f_candidate verify_failed blocks).
# ---------------------------------------------------------------------------
TARGETS = [
    ("G2", 1), ("G2", 5), ("G2", 12),
    ("G3", 0), ("G3", 1), ("G3", 2), ("G3", 4), ("G3", 10), ("G3", 11),
]

ARM = "B_M2_32f_candidate"
LIST_WIDTH_L = 16
TOP_M = 4
CRC_BITS_EXTRA = 16  # scl_joint.CRC_BITS; disclosed once per block, extra vs SC path

MAX_PARALLEL = 8
BUDGET_WALL_S_PER_BLOCK = 1200.0
BUDGET_RSS_GIB_PER_BLOCK = 2.0
HARD_TERMINATE_MARGIN_S = 120.0  # parent-side backstop margin over the block budget

RESULTS_PATH = THIS_DIR / "results.json"

SESSION_CFG = {
    "G2": dict(
        acq_id="20260113_SHG_Type2PPLN_3s",
        outcomes_path=(
            REPO_ROOT / "workspace" / "m2_prior_validation"
            / "20260113_SHG_Type2PPLN_3s_g2" / "per_block_outcomes.jsonl"
        ),
        read_fn="_read_timetags_production",
    ),
    "G3": dict(
        acq_id="20260113_SHG_Type2PPLN_3s_2",
        outcomes_path=(
            REPO_ROOT / "workspace" / "m2_prior_validation"
            / "20260113_SHG_Type2PPLN_3s_2_g3" / "per_block_outcomes.jsonl"
        ),
        read_fn="_read_timetags_g3_production",
    ),
}

# Populated once in the parent BEFORE forking; inherited by children via
# copy-on-write fork memory (never pickled, never re-derived per block).
_CTX: dict = {}


def _fail(msg: str, code: int = 2):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _load_mod():
    """Import the frozen runner module by its real package path (never
    ``exec``'d under a synthetic name), so its own internal deferred
    imports (``from scripts.census_intake_20260921 import ...``) resolve
    exactly as they do in production. Importing it performs no I/O (see
    its own module docstring guarantee)."""
    return importlib.import_module("scripts.m2_prior_validation")


def _load_scl_joint(mod):
    """Load ``...nbpolar.scl_joint`` via the SAME stub-package technique
    ``mod._load_g2_decoder_chain`` uses for the other frozen nbpolar leaves
    (registers bare parent packages in ``sys.modules`` pointing at the real
    directories, so the real file is executed with its own relative imports
    intact — no copy, no rewrite)."""
    chain = mod._load_g2_decoder_chain()
    base_nb = "comparison_bench.src.comparison_bench.formal_ir.nbpolar"
    scl_joint_mod = importlib.import_module(base_nb + ".scl_joint")
    return chain, scl_joint_mod


def _expected_row(session: str, block_index: int) -> dict:
    """Read (read-only) the frozen per_block_outcomes.jsonl row for arm B,
    this block. Never writes to the G2/G3 out_root."""
    path = SESSION_CFG[session]["outcomes_path"]
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("arm") == ARM and int(row.get("block_index")) == int(block_index):
                return row
    raise LookupError(f"{session}: no per_block_outcomes.jsonl row for arm={ARM} block={block_index}")


def _reproduce_session_context(mod, chain, scl_joint_mod, session: str) -> dict:
    """Reproduce, by calling the SAME frozen functions the G2/G3 body
    calls (never re-derived logic), everything one session needs to
    decode its B-arm EVAL blocks: aligned/paired/chunked frames, the B-arm
    CAL fit, p1/p2 tables, frozen P16 orders, and the session-level
    disclosure/entropy bookkeeping (H_total via the frozen
    ``model_entropy_bits`` helper). Read-only against raw data; writes
    nothing anywhere (including no G2/G3 out_root).

    ``chain``/``scl_joint_mod`` are loaded ONCE by the caller (``main()``)
    and passed in, never re-loaded per session: attempt 1 (2026-09-28)
    called ``_load_scl_joint`` -> ``mod._load_g2_decoder_chain()`` once per
    session (twice total in one process) and died on the second call with
    ``ValueError: pandas.__spec__ is None`` -- the frozen loader's own
    pandas-absent guard (``importlib.util.find_spec("pandas") is None and
    "pandas" not in sys.modules``) is not safe to evaluate twice in one
    process once it has already installed its spec-less fail-closed stub
    into ``sys.modules["pandas"]`` on the first call. That death happened
    entirely inside decoder-chain/module loading, before any raw-data read,
    CAL fit, or decode call for the affected session -- zero measurement
    was ever attempted. Fix: load the chain/module once in ``main()``
    (identical singleton, valid for both sessions) instead of loading it
    fresh per session. See ``session_setup_execution_error_attempt1.json``
    for the full attempt-1 record."""
    cfg = SESSION_CFG[session]

    identity = chain.verify_predecessor_construction(
        mod.G2_CONSTRUCTION_PATH, expected_digest=mod.G2_CONSTRUCTION_DIGEST
    )
    l1_order = identity["l1_order"]
    l2_order = identity["l2_order"]
    if len(l1_order) != mod.G2_N or len(l2_order) != mod.G2_N:
        raise RuntimeError(f"{session}: order length {len(l1_order)}/{len(l2_order)} != N={mod.G2_N}")

    read = getattr(mod, cfg["read_fn"])
    got = read(cfg["acq_id"])
    tA, tB = got["tA"], got["tB"]
    if float(got.get("other_frac", 0.0)) > 0.20:
        raise RuntimeError(f"{session}: CHANNEL_FAIL other_frac={got.get('other_frac')}")
    peak = mod._align_frozen(tA, tB)
    if not (
        peak.get("status") == "ok"
        and peak.get("peak_to_bg") is not None
        and float(peak.get("peak_to_bg")) >= mod.G1_PEAK_TO_BG_MIN
    ):
        raise RuntimeError(f"{session}: ALIGN_FAIL {peak}")
    offset = int(peak.get("peak_center_ps"))
    sweep = mod._yield_sweep_selfcheck(tA, tB, offset)
    sweep_ok, sweep["yield_note"] = mod._sweep_accept(sweep)
    if not sweep_ok:
        raise RuntimeError(f"{session}: ALIGN_INCONSISTENT offset={offset}")
    alice, bob = mod.pair_narrow_nearest_unique(tA, tB, offset, 200)
    del tA, tB
    n_pairs = int(alice.size)
    n_frames = n_pairs // mod.G1_FRAME_PAIRS

    if session == "G3":
        gate = mod.G3_REPRO_GATE
    else:
        gate = mod.contract_for_freeze({"pairing_window_primary": 200})["repro_gate"]
    if not (
        peak.get("peak_center_ps") == gate["peak_center_ps"]
        and peak.get("peak_sigma_ps") == gate["peak_sigma_ps"]
        and peak.get("status") == gate["status"]
        and n_pairs == gate["n_pairs"]
        and n_frames == gate["n_frames"]
    ):
        raise RuntimeError(
            f"{session}: ALIGN_INCONSISTENT reproduction gate mismatch "
            f"(expected {gate}; observed peak={peak.get('peak_center_ps')}/"
            f"{peak.get('peak_sigma_ps')}/{peak.get('status')} n_pairs={n_pairs} n_frames={n_frames})"
        )
    frames_a, frames_b, ledger = mod.chunk_frames(alice, bob, 702)
    del alice, bob

    m2_mod = mod._frozen_m2()
    prior_mod = mod._frozen_prior()
    cal_ids = mod.g2_cal_ids(ARM)
    cal_a = frames_a[cal_ids].ravel()
    cal_b = frames_b[cal_ids].ravel()
    fit = mod.fit_g2_arm(ARM, cal_a, cal_b, "CIRCULAR", m2_mod)
    p1_table = np.asarray(prior_mod.derive_p1(fit["joint"]), dtype=np.float64)
    p2_table = np.asarray(prior_mod.derive_p2(fit["joint"]), dtype=np.float64)

    counts = mod.build_counts_1024(cal_a, cal_b)
    p_b = counts.sum(axis=0).astype(np.float64)
    p_b = p_b / p_b.sum()
    entropy = mod.model_entropy_bits(fit["joint"], p_b, prior_mod)
    h_total_bits = float(entropy["H_total_bits"])

    field = chain.make_gf32()
    alpha = int(chain.alpha)
    polar_fn = mod._bind_g2_polar(chain.polar_transform, field, alpha)

    eval_blocks = mod.g2_eval_blocks()
    tag_master = int(mod.G2_TAG_MASTER if session == "G2" else mod.G3_TAG_MASTER)
    eval_seed = int(mod.G2_EVAL_SEED if session == "G2" else mod.G3_EVAL_SEED)

    kdb_no_crc = int(chain.disclosed_bits_per_coordinate * (mod.G2_K1 + mod.G2_K2) + chain.tag_bits)
    kdb_with_crc = int(kdb_no_crc + CRC_BITS_EXTRA)
    f_book_no_crc = kdb_no_crc / (h_total_bits * mod.G2_N)
    f_book_with_crc = kdb_with_crc / (h_total_bits * mod.G2_N)

    return dict(
        session=session,
        chain=chain,
        scl_joint_mod=scl_joint_mod,
        prior_mod=prior_mod,
        l1_order=l1_order,
        l2_order=l2_order,
        frames_a=frames_a,
        frames_b=frames_b,
        fit=fit,
        p1_table=p1_table,
        p2_table=p2_table,
        field=field,
        alpha=alpha,
        polar_fn=polar_fn,
        eval_blocks=eval_blocks,
        tag_master=tag_master,
        eval_seed=eval_seed,
        k1=int(mod.G2_K1),
        k2=int(mod.G2_K2),
        n=int(mod.G2_N),
        h_total_bits=h_total_bits,
        kdb_no_crc=kdb_no_crc,
        kdb_with_crc=kdb_with_crc,
        f_book_no_crc=f_book_no_crc,
        f_book_with_crc=f_book_with_crc,
        align_peak=dict(peak),
        n_pairs=n_pairs,
        n_frames=n_frames,
    )


_FIDELITY_FIELDS = ("outcome", "first_error_coordinate", "first_error_layer", "l1_exact", "hard_l2_exact")


def _fidelity_check(mod, ctx: dict, session: str, block_index: int) -> dict:
    """Re-run the SAME frozen SC block body (``run_g2_block``) G2/G3 used
    for this one block, and diff the 5 recorded fields against the frozen
    ``per_block_outcomes.jsonl`` row. Any diff => the caller must STOP
    before attempting the SCL rescue for this block."""
    eval_blocks = ctx["eval_blocks"]
    s, e = eval_blocks[block_index]
    bob = ctx["frames_b"][s : e + 1].ravel()
    alice = ctx["frames_a"][s : e + 1].ravel()
    actual = mod.run_g2_block(
        arm=ARM,
        block_index=block_index,
        eval_frames=[s, e],
        bob=bob,
        alice=alice,
        fit=ctx["fit"],
        p1_table=ctx["p1_table"],
        p2_table=ctx["p2_table"],
        l1_order=ctx["l1_order"],
        l2_order=ctx["l2_order"],
        k1=ctx["k1"],
        k2=ctx["k2"],
        tag_master=ctx["tag_master"],
        eval_seed=ctx["eval_seed"],
        chain=ctx["chain"],
        polar_fn=ctx["polar_fn"],
        prior_mod=ctx["prior_mod"],
    )
    expected = _expected_row(session, block_index)
    mismatches = [
        f"{k}: expected={expected.get(k)!r} actual={actual.get(k)!r}"
        for k in _FIDELITY_FIELDS
        if expected.get(k) != actual.get(k)
    ]
    return {
        "match": len(mismatches) == 0,
        "mismatches": mismatches,
        "expected": {k: expected.get(k) for k in _FIDELITY_FIELDS},
        "actual": {k: actual.get(k) for k in _FIDELITY_FIELDS},
        "alice": alice,
        "bob": bob,
        "eval_frames": [int(s), int(e)],
    }


def _rescue_block(mod, ctx: dict, session: str, block_index: int, alice: np.ndarray, bob: np.ndarray) -> dict:
    """CRC-16-aided joint SCL(L=16, top_m=4) re-decode of one block, scored
    against Alice truth and the SAME per-block Toeplitz tag G2/G3 used
    (same tag_master/eval_seed/block_index => same
    ``operational_seed_bits`` stream; only the disclosed CRC-16 is new)."""
    chain = ctx["chain"]
    scl_joint_mod = ctx["scl_joint_mod"]
    prior_mod = ctx["prior_mod"]
    l1_pos = np.asarray(ctx["l1_order"], dtype=np.int64)[: ctx["k1"]]
    l2_pos = np.asarray(ctx["l2_order"], dtype=np.int64)[: ctx["k2"]]

    views = mod.g2_truth_views(alice, ctx["polar_fn"])
    high_true, low_true = views["high"], views["low"]
    u1_true, u2_true = views["u1"], views["u2"]
    labels_true = views["labels"]

    crc_true = int(scl_joint_mod.labels_crc16(labels_true))

    res = scl_joint_mod.scl_joint_decode(
        bob,
        crc_true,
        field=ctx["field"],
        alpha=ctx["alpha"],
        p1_table=ctx["p1_table"],
        p2_table=ctx["p2_table"],
        d1_positions=l1_pos,
        d1_values=u1_true[l1_pos],
        d2_positions=l2_pos,
        d2_values=u2_true[l2_pos],
        list_width_L=LIST_WIDTH_L,
        top_m=TOP_M,
    )

    n = ctx["n"]
    seed = chain.operational_seed_bits(ctx["tag_master"], n, block_index, bit_length=chain.seed_bits_for(n))
    labels_true_bits = chain.labels_to_bits(labels_true)
    label_hat_bits = chain.labels_to_bits(res.label_hat)
    tag_true = chain.toeplitz_tag(labels_true_bits, seed, chain.tag_bits)
    tag_hat = chain.toeplitz_tag(label_hat_bits, seed, chain.tag_bits)
    tag_pass = bool(tag_hat == tag_true)
    crc_pass = bool(res.crc_pass)

    label_exact = bool(np.array_equal(np.asarray(res.label_hat), np.asarray(labels_true)))
    l1_exact_scl = bool(np.array_equal(np.asarray(res.high_hat), high_true))
    hard_l2_exact_scl = bool(np.array_equal(np.asarray(res.low_hat), low_true))
    l1_error_symbols_scl = int(np.sum(np.asarray(res.high_hat) != high_true))
    l2_error_symbols_scl = int(np.sum(np.asarray(res.low_hat) != low_true))

    # Main-thread ruling F1 (2026-09-28): accepted must match the T3 gate
    # convention (workspace/probes/scl-gate-t3) -- CRC AND tag both pass, not
    # tag alone. crc_pass and tag_pass are both recorded separately below.
    accepted = bool(crc_pass and tag_pass)
    exact = bool(accepted and label_exact)
    undetected = bool(accepted and not label_exact)  # isolated; never merged into exact
    verify_failed = bool(not accepted)

    return {
        "list_width_L": LIST_WIDTH_L,
        "top_m_requested": TOP_M,
        "top_m_used": int(res.top_m_used),
        "l1_survivor_count": int(res.l1_survivor_count),
        "candidates_considered": int(res.candidates_considered),
        "m1": float(res.m1),
        "m2": float(res.m2),
        "joint_metric": float(res.joint_metric),
        "crc_bits": int(res.crc_bits),
        "crc_true": crc_true,
        "crc_hat": int(res.crc_hat),
        "crc_pass": crc_pass,
        "tag_pass": tag_pass,
        "label_exact": label_exact,
        "accepted": accepted,
        "exact": exact,
        "undetected": undetected,
        "verify_failed": verify_failed,
        "l1_exact_scl": l1_exact_scl,
        "hard_l2_exact_scl": hard_l2_exact_scl,
        "l1_error_symbols_scl": l1_error_symbols_scl,
        "l2_error_symbols_scl": l2_error_symbols_scl,
        "metric_provenance": dict(res.metric_provenance),
    }


def _peak_rss_gib():
    try:
        with open("/proc/self/status", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    return float(line.split()[1]) / 1024.0**2
    except Exception:
        pass
    return None


def _part_path(session: str, block_index: int) -> Path:
    return THIS_DIR / f"part_{session}_{block_index:02d}.json"


def _run_one_block_entry(session: str, block_index: int):
    """Top-level worker body (forked child; inherits ``_CTX`` via
    copy-on-write memory, never pickled). Writes exactly one part file and
    never raises across the process boundary (any failure is captured and
    recorded in the part file itself)."""
    t0 = time.perf_counter()
    status = "ok"
    error = None
    fidelity = None
    rescue = None
    wall_fidelity_s = None
    wall_rescue_s = None
    try:
        mod = _CTX["_mod"]
        ctx = _CTX[session]
        t_fid0 = time.perf_counter()
        fidelity_full = _fidelity_check(mod, ctx, session, block_index)
        wall_fidelity_s = time.perf_counter() - t_fid0
        fidelity = {k: fidelity_full[k] for k in ("match", "mismatches", "expected", "actual", "eval_frames")}
        if not fidelity_full["match"]:
            status = "STOPPED_FIDELITY_MISMATCH"
        else:
            elapsed_so_far = time.perf_counter() - t0
            if elapsed_so_far > BUDGET_WALL_S_PER_BLOCK:
                status = "resource_abort_wall_pre_rescue"
            else:
                t_res0 = time.perf_counter()
                rescue = _rescue_block(
                    mod, ctx, session, block_index, fidelity_full["alice"], fidelity_full["bob"]
                )
                wall_rescue_s = time.perf_counter() - t_res0
                if (time.perf_counter() - t0) > BUDGET_WALL_S_PER_BLOCK:
                    status = "resource_abort_wall_post_rescue"  # completed but over budget; recorded, not silently accepted
    except Exception as exc:  # never propagate across the process boundary
        status = f"error:{type(exc).__name__}"
        error = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
    wall_total_s = time.perf_counter() - t0
    record = {
        "session": session,
        "block_index": block_index,
        "arm": ARM,
        "status": status,
        "fidelity": fidelity,
        "rescue": rescue,
        "error": error,
        "resources": {
            "wall_fidelity_s": wall_fidelity_s,
            "wall_rescue_s": wall_rescue_s,
            "wall_total_s": wall_total_s,
            "rss_gib_peak_advisory": _peak_rss_gib(),
            "budget_wall_s": BUDGET_WALL_S_PER_BLOCK,
            "budget_rss_gib": BUDGET_RSS_GIB_PER_BLOCK,
        },
    }
    with open(_part_path(session, block_index), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)


def _timeout_part_record(session: str, block_index: int, elapsed_s: float) -> dict:
    return {
        "session": session,
        "block_index": block_index,
        "arm": ARM,
        "status": "resource_abort_wall_hard_terminate",
        "fidelity": None,
        "rescue": None,
        "error": {"type": "ParentTerminated", "message": f"exceeded budget+margin at {elapsed_s:.1f}s"},
        "resources": {
            "wall_fidelity_s": None,
            "wall_rescue_s": None,
            "wall_total_s": elapsed_s,
            "rss_gib_peak_advisory": None,
            "budget_wall_s": BUDGET_WALL_S_PER_BLOCK,
            "budget_rss_gib": BUDGET_RSS_GIB_PER_BLOCK,
        },
    }


def _launch_all(targets):
    if "fork" not in mp.get_all_start_methods():
        _fail("this launcher requires the 'fork' start method (Linux/WSL); refusing to run under spawn")
    ctx_mp = mp.get_context("fork")
    procs: dict = {}
    started_at: dict = {}
    pending = list(targets)
    while pending or procs:
        while pending and len(procs) < MAX_PARALLEL:
            session, block_index = pending.pop(0)
            p = ctx_mp.Process(target=_run_one_block_entry, args=(session, block_index))
            p.start()
            procs[(session, block_index)] = p
            started_at[(session, block_index)] = time.time()
        finished = []
        for key, p in list(procs.items()):
            if not p.is_alive():
                p.join()
                finished.append(key)
                continue
            elapsed = time.time() - started_at[key]
            if elapsed > BUDGET_WALL_S_PER_BLOCK + HARD_TERMINATE_MARGIN_S:
                p.terminate()
                p.join(timeout=10)
                with open(_part_path(*key), "w", encoding="utf-8") as fh:
                    json.dump(_timeout_part_record(key[0], key[1], elapsed), fh, indent=2, sort_keys=True)
                finished.append(key)
        for key in finished:
            procs.pop(key, None)
        if procs:
            time.sleep(2.0)


def main() -> int:
    if RESULTS_PATH.exists():
        _fail(f"refusing to run: {RESULTS_PATH} already exists (additive-only; one-shot)")
    for session, block_index in TARGETS:
        part = _part_path(session, block_index)
        if part.exists():
            _fail(f"refusing to run: {part} already exists (additive-only; one-shot)")

    t0 = time.time()
    mod = _load_mod()
    # Load the frozen decoder chain + scl_joint module ONCE (process-global
    # singleton, valid for both sessions) -- NOT once per session. See
    # _reproduce_session_context's docstring / session_setup_execution_error_attempt1.json
    # for why a second per-session load previously crashed.
    chain, scl_joint_mod = _load_scl_joint(mod)
    global _CTX
    _CTX["_mod"] = mod
    for session in ("G2", "G3"):
        print(f"[setup] reproducing {session} session context (raw read + align + CAL fit)...", file=sys.stderr)
        _CTX[session] = _reproduce_session_context(mod, chain, scl_joint_mod, session)
        print(f"[setup] {session} ready: H_total={_CTX[session]['h_total_bits']:.6f} bits, "
              f"f_book_no_crc={_CTX[session]['f_book_no_crc']:.6f}, "
              f"f_book_with_crc={_CTX[session]['f_book_with_crc']:.6f}", file=sys.stderr)

    _launch_all(TARGETS)

    blocks = []
    for session, block_index in TARGETS:
        part = _part_path(session, block_index)
        with open(part, "r", encoding="utf-8") as fh:
            blocks.append(json.load(fh))

    n_fidelity_ok = sum(1 for b in blocks if b["fidelity"] and b["fidelity"]["match"])
    n_fidelity_mismatch = sum(1 for b in blocks if b["fidelity"] and not b["fidelity"]["match"])
    n_rescued_exact = sum(1 for b in blocks if b.get("rescue") and b["rescue"]["exact"])
    n_still_failed = sum(1 for b in blocks if b.get("rescue") and not b["rescue"]["exact"])
    n_undetected = sum(1 for b in blocks if b.get("rescue") and b["rescue"]["undetected"])
    n_errors = sum(1 for b in blocks if str(b["status"]).startswith("error") or "resource_abort" in str(b["status"]))

    # Main-thread ruling D3 (2026-09-28): any single-block STOPPED_FIDELITY_MISMATCH
    # compromises the whole run's rescue tally -- flag it at top level and drop the
    # aggregate rescue counts from summary (per-block detail stays in "blocks").
    fidelity_compromised = bool(n_fidelity_mismatch > 0)
    if fidelity_compromised:
        summary = {
            "n_targets": len(TARGETS),
            "n_fidelity_ok": n_fidelity_ok,
            "n_fidelity_mismatch": n_fidelity_mismatch,
            "n_errors_or_aborts": n_errors,
            "note": (
                "fidelity_compromised=true: at least one block failed the fidelity "
                "check, so NO aggregate rescue count is reported here (see "
                "results['blocks'][*]['rescue'] for whatever per-block rescue data "
                "did run; main-thread ruling D3, 2026-09-28)."
            ),
        }
    else:
        summary = {
            "n_targets": len(TARGETS),
            "n_fidelity_ok": n_fidelity_ok,
            "n_fidelity_mismatch": n_fidelity_mismatch,
            "n_rescued_exact": n_rescued_exact,
            "n_still_failed": n_still_failed,
            "n_undetected": n_undetected,
            "n_errors_or_aborts": n_errors,
        }

    results = {
        "probe_id": "m2-scl-rescue-g2g3",
        "classification": (
            "Descriptive real-data re-decode diagnostic; NOT a Tier-X synthetic probe "
            "(reads real .ttbin data) and NOT a Tier-Y decision gate (no threshold, no "
            "success/fail verdict, no state-string change, no candidate/accepted token, "
            "consumes no new EVAL data -- the 9 blocks were already decoded and recorded "
            "by G2/G3). See TASK_PACKET.md for the main-thread classification question."
        ),
        "authorization": {
            "who": "PI",
            "when": "2026-09-28",
            "verbatim": "授权，用 SCL L=16 重解那 9 个失败块，可以继续往下推进",
            "source": "AUTHORIZATION_PROMPT.md (this directory)",
        },
        "frozen_params": {
            "arm": ARM,
            "list_width_L": LIST_WIDTH_L,
            "top_m": TOP_M,
            "crc_bits_extra": CRC_BITS_EXTRA,
            "k1": _CTX["G2"]["k1"],
            "k2": _CTX["G2"]["k2"],
            "n": _CTX["G2"]["n"],
            "construction_digest": mod.G2_CONSTRUCTION_DIGEST,
            "tag_master": {"G2": _CTX["G2"]["tag_master"], "G3": _CTX["G3"]["tag_master"]},
            "eval_seed": {"G2": _CTX["G2"]["eval_seed"], "G3": _CTX["G3"]["eval_seed"]},
        },
        "targets": [{"session": s, "block_index": b} for s, b in TARGETS],
        "per_session": {
            session: {
                "h_total_bits": _CTX[session]["h_total_bits"],
                "kdb_no_crc": _CTX[session]["kdb_no_crc"],
                "kdb_with_crc": _CTX[session]["kdb_with_crc"],
                "f_book_no_crc": _CTX[session]["f_book_no_crc"],
                "f_book_with_crc": _CTX[session]["f_book_with_crc"],
                "n_pairs": _CTX[session]["n_pairs"],
                "n_frames": _CTX[session]["n_frames"],
                "align_peak": _CTX[session]["align_peak"],
            }
            for session in ("G2", "G3")
        },
        "fidelity_compromised": fidelity_compromised,
        "blocks": blocks,
        "summary": summary,
        "claims": (
            "No significance test, no threshold, no pass/fail verdict, no "
            "candidate/accepted promotion, no change to NBPOLAR_M2_PRIOR_G2_SUCCESS / "
            "NBPOLAR_M2_PRIOR_G3_SUCCESS / M2 status ladder, no attempt counted. "
            "n_rescued_exact / 9 is a raw descriptive count only, and is WITHHELD "
            "entirely (see summary.note) when fidelity_compromised=true (main-thread "
            "ruling D3, 2026-09-28)."
        ),
        "timing": {"wall_s_total": time.time() - t0},
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
    if fidelity_compromised:
        print(
            f"DONE fidelity_compromised=True fidelity_ok={n_fidelity_ok}/9 "
            f"fidelity_mismatch={n_fidelity_mismatch} (aggregate rescue counts "
            f"WITHHELD per D3) errors_or_aborts={n_errors} wall_s={time.time()-t0:.1f}",
            file=sys.stderr,
        )
    else:
        print(
            f"DONE fidelity_ok={n_fidelity_ok}/9 fidelity_mismatch={n_fidelity_mismatch} "
            f"rescued_exact={n_rescued_exact} still_failed={n_still_failed} "
            f"undetected={n_undetected} errors_or_aborts={n_errors} "
            f"wall_s={time.time()-t0:.1f}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
