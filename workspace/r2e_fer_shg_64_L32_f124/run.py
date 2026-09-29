#!/usr/bin/env python3
"""R2E formal FER measurement: M2 + native SCL(L=32, top_m=4, CRC-16) at
f~1.24 (K_total=6657, k1=253/k2=6404; R2D-selected f1.24_s0380) on the frozen
64-block SHG `_1`/`_2` pool (DATA_LEDGER.md §7). Tier-Y one-shot delta-successor
of ``workspace/r2b_fer_shg_64_L32_f120/`` (executed, adjudicated). Full delta:
docs/nbpolar/R2E_L32_F124_DELTA_20260929.md.

Authorization: NOT YET GRANTED (see STATUS.yaml / AUTHORIZATION_PROMPT.md).

This measures the *native SCL implementation* (scl_joint_native, Rust whole
recursion; PI equivalence standard B, commit 8fcc9119 T-N1/T-N2), NOT a
reproduction of scl_joint.

Delta vs predecessor (everything else inherited verbatim):
 K (253/6404, shared K_total=6657; R2B was 302/6140), seeds
 (eval 2026092904 / tag 2026102904), new `stratum_selection` label
 (G3 "clean" / G2 "selection_touched") + taxonomy table + clean-layer
 descriptive Wilson + gbi-23 known-hard-block annotation. Decoder (native,
 L=32, top_m=4), budget (serial, 300 s/block, 4 GiB, 7200 s total), SC
 fidelity path (frozen K1=319/K2=6492) are inherited unchanged.

Non-goals / forbidden: no change to any frozen module; no write outside this
directory; no frame drawn outside the frozen 64-block pool; one-shot,
reruns=0 except a pre-measurement implementation-defect restart.

Output
------
``workspace/r2e_fer_shg_64_L32_f124/results.json`` (must be absent before this script
starts) plus one ``part_<SESSION>_<global_block_index:02d>.json`` per target
block (64 files). Nothing is written outside this directory.
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
# PLACEHOLDERS -- must be filled with the R2 contract's T6-frozen integers
# before this script is executed. NOT invented here (AGENTS.md §3: ambiguity
# -> STOP, do not guess). Per the task instruction's naming convention
# (eval_seed -> tag_master = eval_seed + 10000), so only R2_EVAL_SEED needs
# to be pasted from the frozen contract and R2_TAG_MASTER is then mechanical
# -- but BOTH are left as None here rather than half-filled, so a partial
# edit cannot silently slip through _fail()'s guard below.
# ---------------------------------------------------------------------------
# Filled by main thread 2026-09-28 from the frozen R2 contract (docs/decision-log.md
# 2026-09-28 entry, lines ~45-46; T6_PACKET_SKELETON_20260928.md §2).
R2_EVAL_SEED = 2026092904
R2_TAG_MASTER = 2026102904  # = R2_EVAL_SEED + 10000 (R2E delta: new seeds)

ARM = "B_M2_32f_candidate"
LIST_WIDTH_L = 32
TOP_M = 4
# --- R2E K delta: R2D-selected f1.24_s0380 (workspace/r2d_locate_f_k_g2/) -------
# Frozen integers (k1_share=0.0380, f_target=1.24 per R2D grid); no recomputation.
F_TARGET = 1.24
K_TOTAL = 6657
K1_R2B = 253  # name kept from R2B for minimal diff; value is R2E's k1
K2_R2B = 6404
assert (K_TOTAL, K1_R2B, K2_R2B) == (6657, 253, 6404), (K_TOTAL, K1_R2B, K2_R2B)
KNOWN_HARD_GBI = 23  # R2D: fails L2 in every grid config; annotated, still in denominator
CRC_BITS_EXTRA = 16  # scl_joint.CRC_BITS; disclosed once per block, extra vs SC path

# --- Frozen frame-boundary constants (DATA_LEDGER.md §7; identical for both
# sessions -- "段结构与 §1 同构", DATA_LEDGER.md:57-58) ------------------------
BLOCK_FRAMES = 128
A1_CAL_FIRST = 0
A1_CAL_BLOCKS = 8  # frames 0-1023
CHARHELD_FIRST = 1056
CHARHELD_BLOCKS = 10  # frames 1056-2335 used (62-frame remainder 2336-2397 unused, DATA_LEDGER.md:46)
HELDOUT_FIRST = 1838  # first frame of the HELDOUT sub-range within the CHAR/HELDOUT band (CHAR=1056-1837)
# EVAL band reuses the frozen scripts.m2_prior_validation.g2_eval_blocks() layout verbatim (2398-4189, 14x128).

# --- Budget (R2B; PI authorization text) -------------------------------------
MAX_PARALLEL = 1  # serial; native library uses its default thread count
BUDGET_WALL_S_PER_BLOCK = 300.0
BUDGET_RSS_GIB_PER_BLOCK = 4.0
BUDGET_WALL_S_TOTAL = 2.0 * 3600.0
HARD_TERMINATE_MARGIN_S = 120.0  # parent-side backstop margin over the per-block budget
_CLOCK = time.monotonic  # same mechanism as r2_binary_baseline_shg_64 `_total_wall_exceeded`


def _total_wall_exceeded(t_start: float) -> bool:
    """Total-wall check on the monotonic clock (strict >); mechanism copied from
    workspace/r2_binary_baseline_shg_64/run.py."""
    return (_CLOCK() - t_start) > BUDGET_WALL_S_TOTAL


RESULTS_PATH = THIS_DIR / "results.json"

SESSION_CFG = {
    "G2": dict(
        acq_id="20260113_SHG_Type2PPLN_3s",
        outcomes_path=(
            REPO_ROOT / "workspace" / "m2_prior_validation"
            / "20260113_SHG_Type2PPLN_3s_g2" / "per_block_outcomes.jsonl"
        ),
        read_fn="_read_timetags_production",
        global_offset=0,
    ),
    "G3": dict(
        acq_id="20260113_SHG_Type2PPLN_3s_2",
        outcomes_path=(
            REPO_ROOT / "workspace" / "m2_prior_validation"
            / "20260113_SHG_Type2PPLN_3s_2_g3" / "per_block_outcomes.jsonl"
        ),
        read_fn="_read_timetags_g3_production",
        global_offset=32,
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
    ``exec``'d under a synthetic name). Importing it performs no I/O (see
    its own module docstring guarantee)."""
    return importlib.import_module("scripts.m2_prior_validation")


def _load_scl_joint(mod):
    """Load ``...nbpolar.scl_joint`` via the SAME stub-package technique
    ``mod._load_g2_decoder_chain`` uses for the other frozen nbpolar leaves
    (identical to the predecessor; no copy, no rewrite)."""
    chain = mod._load_g2_decoder_chain()
    base_nb = "comparison_bench.src.comparison_bench.formal_ir.nbpolar"
    scl_joint_mod = importlib.import_module(base_nb + ".scl_joint")
    native_mod = importlib.import_module(base_nb + ".scl_joint_native")
    native_mod.native_backend_info()  # fail fast if no native library loads
    return chain, (scl_joint_mod, native_mod)


def _stratum_band_blocks(first_frame: int, n_blocks: int) -> list:
    """Pure: n_blocks contiguous 128-frame windows starting at first_frame."""
    out = []
    for i in range(n_blocks):
        s = first_frame + i * BLOCK_FRAMES
        out.append((s, s + BLOCK_FRAMES - 1))
    return out


def build_session_blocks(mod, session: str) -> list:
    """Build the 32 frozen R2 block descriptors for one session, in frame
    order: A1_CAL (8) -> CHAR/HELDOUT (10) -> EVAL (14). Pure given `mod`
    (only used to read the frozen ``g2_eval_blocks()`` layout).

    Two DISTINCT stratum labels are recorded per block (see TASK_PACKET.md
    §3 decision point D_NEW_STRATUM_LABELS -- flagged, not silently
    resolved):

    - ``stratum_official``: the exact DATA_LEDGER.md §7 / tasks.md D-ACQ-03
      DECIDED label (``A1_CAL_characterization`` / ``HELDOUT_model_selection``
      / ``EVAL_already_decoded``), unchanged, coarse (the whole 1056-2397
      band is one official stratum).
    - ``stratum_task``: this packet's finer request-level label
      (``never_decoded`` / ``heldout_model_selection`` /
      ``previously_decoded_eval``), which additionally splits the CHAR
      portion (1056-1837, no HELDOUT frame in the block) from the HELDOUT
      portion (any frame >=1838 in the block) of the same official
      HELDOUT_model_selection band, per the task's conservative
      any-HELDOUT-frame-in-block rule.

    ``global_block_index`` is a NEW, 0..63 globally-unique-across-both-
    sessions index (session offset 0 for G2, 32 for G3), required because
    the R2 tag_master is shared across both sessions and
    ``operational_seed_bits(master, n, block_index)`` depends on nothing
    else -- see TASK_PACKET.md decision point D_NEW_SEED_SCHEME.
    """
    offset = SESSION_CFG[session]["global_offset"]
    out = []
    idx = 0
    for (s, e) in _stratum_band_blocks(A1_CAL_FIRST, A1_CAL_BLOCKS):
        out.append(dict(
            session=session, local_index=idx, global_block_index=offset + idx,
            frame_start=s, frame_end=e,
            stratum_official="A1_CAL_characterization", stratum_task="never_decoded",
            eval_original_index=None, fidelity_check_applicable=False,
        ))
        idx += 1
    for (s, e) in _stratum_band_blocks(CHARHELD_FIRST, CHARHELD_BLOCKS):
        stratum_task = "heldout_model_selection" if e >= HELDOUT_FIRST else "never_decoded"
        out.append(dict(
            session=session, local_index=idx, global_block_index=offset + idx,
            frame_start=s, frame_end=e,
            stratum_official="HELDOUT_model_selection", stratum_task=stratum_task,
            eval_original_index=None, fidelity_check_applicable=False,
        ))
        idx += 1
    eval_blocks = mod.g2_eval_blocks()  # frozen [s,e] pairs, index 0..13
    for orig_index, (s, e) in enumerate(eval_blocks):
        out.append(dict(
            session=session, local_index=idx, global_block_index=offset + idx,
            frame_start=s, frame_end=e,
            stratum_official="EVAL_already_decoded", stratum_task="previously_decoded_eval",
            eval_original_index=orig_index, fidelity_check_applicable=True,
        ))
        idx += 1
    if idx != 32:
        raise AssertionError(f"{session}: block generation drift, expected 32 blocks, got {idx}")
    n_never = sum(1 for b in out if b["stratum_task"] == "never_decoded")
    n_held = sum(1 for b in out if b["stratum_task"] == "heldout_model_selection")
    n_eval = sum(1 for b in out if b["stratum_task"] == "previously_decoded_eval")
    if (n_never, n_held, n_eval) != (14, 4, 14):
        raise AssertionError(
            f"{session}: stratum_task layout drift, expected (14,4,14) got {(n_never, n_held, n_eval)}"
        )
    return out


def _expected_row(session: str, eval_original_index: int) -> dict:
    """Read (read-only) the frozen per_block_outcomes.jsonl row for arm B,
    this EVAL block. Never writes to the G2/G3 out_root."""
    path = SESSION_CFG[session]["outcomes_path"]
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("arm") == ARM and int(row.get("block_index")) == int(eval_original_index):
                return row
    raise LookupError(f"{session}: no per_block_outcomes.jsonl row for arm={ARM} block={eval_original_index}")


def _reproduce_session_context(mod, chain, mods, session: str) -> dict:
    """Reproduce, by calling the SAME frozen functions the G2/G3 body
    calls (never re-derived logic), everything one session needs to decode
    ANY of its 32 R2 blocks: aligned/paired/chunked frames (all post-skip
    frames, not just EVAL), the B-arm CAL fit (from CAL32, 1024-1055,
    unchanged), p1/p2 tables, frozen P16 orders, and the session-level
    disclosure/entropy bookkeeping. Read-only against raw data; writes
    nothing anywhere. Identical to the predecessor's function of the same
    name except it no longer needs a special-cased `eval_blocks` fetch
    (kept, since build_session_blocks() also needs it, but computed once
    here and reused)."""
    scl_joint_mod, native_mod = mods
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

    if R2_TAG_MASTER is None or R2_EVAL_SEED is None:
        _fail(
            "R2_TAG_MASTER/R2_EVAL_SEED are still PLACEHOLDERS (None); "
            "fill them from the R2 contract's T6-frozen values before running. "
            "Refusing to fabricate a value (AGENTS.md §3: ambiguity -> STOP)."
        )
    tag_master = int(R2_TAG_MASTER)
    eval_seed = int(R2_EVAL_SEED)

    kdb_no_crc = int(chain.disclosed_bits_per_coordinate * (K1_R2B + K2_R2B) + chain.tag_bits)
    kdb_with_crc = int(kdb_no_crc + CRC_BITS_EXTRA)
    f_book_no_crc = kdb_no_crc / (h_total_bits * mod.G2_N)
    f_book_with_crc = kdb_with_crc / (h_total_bits * mod.G2_N)

    return dict(
        session=session,
        chain=chain,
        scl_joint_mod=scl_joint_mod,
        native_mod=native_mod,
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
        tag_master=tag_master,
        eval_seed=eval_seed,
        k1=int(K1_R2B),
        k2=int(K2_R2B),
        k1_sc=int(mod.G2_K1),  # SC fidelity/descriptive path: frozen 319/6492 (unchanged)
        k2_sc=int(mod.G2_K2),
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


def _sc_call(mod, ctx: dict, block: dict) -> dict:
    """One descriptive/fidelity SC decode of one block via the frozen,
    frame-range-generic ``run_g2_block`` (TASK_PACKET.md §4 records the
    evidence it is not EVAL-specific: it only consumes `bob`/`alice`
    arrays of length N=32768 plus a `block_index` used solely for seed
    derivation). Uses `global_block_index` for the seed (NOT
    `eval_original_index`) -- see build_session_blocks()'s docstring."""
    s, e = block["frame_start"], block["frame_end"]
    bob = ctx["frames_b"][s : e + 1].ravel()
    alice = ctx["frames_a"][s : e + 1].ravel()
    actual = mod.run_g2_block(
        arm=ARM,
        block_index=block["global_block_index"],
        eval_frames=[s, e],
        bob=bob,
        alice=alice,
        fit=ctx["fit"],
        p1_table=ctx["p1_table"],
        p2_table=ctx["p2_table"],
        l1_order=ctx["l1_order"],
        l2_order=ctx["l2_order"],
        k1=ctx["k1_sc"],
        k2=ctx["k2_sc"],
        tag_master=ctx["tag_master"],
        eval_seed=ctx["eval_seed"],
        chain=ctx["chain"],
        polar_fn=ctx["polar_fn"],
        prior_mod=ctx["prior_mod"],
    )
    return {"actual": actual, "alice": alice, "bob": bob}


def _fidelity_check(mod, ctx: dict, session: str, block: dict, sc_result: dict) -> dict:
    """EVAL blocks only: diff the SC reproduction against the frozen
    ``per_block_outcomes.jsonl`` row. Any diff on the 5 recorded fields =>
    the caller must STOP before the SCL preservation-check step for this
    block (unchanged mechanism from the predecessor)."""
    actual = sc_result["actual"]
    expected = _expected_row(session, block["eval_original_index"])
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
        "eval_frames": [int(block["frame_start"]), int(block["frame_end"])],
    }


def _scl_call(mod, ctx: dict, block: dict, alice: np.ndarray, bob: np.ndarray) -> dict:
    """CRC-16-aided joint native SCL(L=32, top_m=4) decode of one block, scored
    against Alice truth and the per-block Toeplitz tag under the R2 shared
    master + this block's `global_block_index` seed. Same computation as
    the predecessor's ``_rescue_block``, generalized to any block (not just
    the 19/28 EVAL-arm ones) and extended with a defensive `decode_failed`
    branch for C5 five-way-taxonomy schema completeness (see TASK_PACKET.md
    §3: `scl_joint_decode`'s list decoder always yields >=1 L1 survivor in
    every empirical precedent in this repo, so `decode_failed` is not
    expected to ever trigger for the SCL arm, but the field is not omitted)."""
    chain = ctx["chain"]
    scl_joint_mod = ctx["scl_joint_mod"]
    l1_pos = np.asarray(ctx["l1_order"], dtype=np.int64)[: ctx["k1"]]
    l2_pos = np.asarray(ctx["l2_order"], dtype=np.int64)[: ctx["k2"]]

    views = mod.g2_truth_views(alice, ctx["polar_fn"])
    high_true, low_true = views["high"], views["low"]
    u1_true, u2_true = views["u1"], views["u2"]
    labels_true = views["labels"]

    crc_true = int(scl_joint_mod.labels_crc16(labels_true))

    res = ctx["native_mod"].scl_joint_decode_native(
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
    seed = chain.operational_seed_bits(
        ctx["tag_master"], n, block["global_block_index"], bit_length=chain.seed_bits_for(n)
    )
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

    # Defensive C5 five-way-taxonomy completeness (see docstring above):
    # not expected to ever be true given the SCL list decoder's guaranteed
    # >=1 survivor, but not silently omitted from the schema.
    decode_failed = bool(int(res.l1_survivor_count) == 0 or int(res.candidates_considered) == 0)

    # Main-thread ruling F1 (inherited unchanged): accepted = crc_pass AND tag_pass.
    accepted = bool(crc_pass and tag_pass and not decode_failed)
    exact = bool(accepted and label_exact)
    undetected = bool(accepted and not label_exact)  # isolated; never merged into exact
    verify_failed = bool((not accepted) and not decode_failed)

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
        "decode_failed": decode_failed,
        "l1_exact_scl": l1_exact_scl,
        "hard_l2_exact_scl": hard_l2_exact_scl,
        "l1_error_symbols_scl": l1_error_symbols_scl,
        "l2_error_symbols_scl": l2_error_symbols_scl,
        "metric_provenance": dict(res.metric_provenance),
        "native_backend": ctx["native_mod"].native_backend_info(),
        "k1_scl": int(ctx["k1"]),
        "k2_scl": int(ctx["k2"]),
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


def _selection_label(session: str) -> str:
    """R2 stratification: G3 never took part in R2D f/k selection -> clean;
    G2 did -> selection_touched."""
    return {"G3": "clean", "G2": "selection_touched"}[session]


def _part_path(global_block_index: int, session: str) -> Path:
    return THIS_DIR / f"part_{session}_{global_block_index:02d}.json"


def _run_one_block_entry(block: dict):
    """Top-level worker body (forked child; inherits ``_CTX`` via
    copy-on-write memory, never pickled). Writes exactly one part file and
    never raises across the process boundary (any failure is captured and
    recorded in the part file itself)."""
    session = block["session"]
    t0 = time.perf_counter()
    status = "ok"
    error = None
    fidelity = None
    sc_descriptive = None
    scl = None
    wall_sc_s = None
    wall_scl_s = None
    try:
        mod = _CTX["_mod"]
        ctx = _CTX[session]

        t_sc0 = time.perf_counter()
        sc_result = _sc_call(mod, ctx, block)
        wall_sc_s = time.perf_counter() - t_sc0

        proceed = True
        if block["fidelity_check_applicable"]:
            fidelity_full = _fidelity_check(mod, ctx, session, block, sc_result)
            fidelity = fidelity_full
            if not fidelity_full["match"]:
                status = "STOPPED_FIDELITY_MISMATCH"
                proceed = False
        else:
            sc_descriptive = {k: sc_result["actual"][k] for k in _FIDELITY_FIELDS}
            sc_descriptive["note"] = "descriptive SC baseline; no comparison record exists; not a gate"

        if proceed:
            elapsed_so_far = time.perf_counter() - t0
            if elapsed_so_far > BUDGET_WALL_S_PER_BLOCK:
                status = "resource_abort_wall_pre_scl"
            else:
                t_scl0 = time.perf_counter()
                scl = _scl_call(mod, ctx, block, sc_result["alice"], sc_result["bob"])
                wall_scl_s = time.perf_counter() - t_scl0
                if (time.perf_counter() - t0) > BUDGET_WALL_S_PER_BLOCK:
                    status = "resource_abort_wall_post_scl"  # completed but over budget; recorded, not silently accepted
    except Exception as exc:  # never propagate across the process boundary
        status = f"error:{type(exc).__name__}"
        error = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
    wall_total_s = time.perf_counter() - t0
    record = {
        "session": session,
        "global_block_index": block["global_block_index"],
        "local_index": block["local_index"],
        "frame_start": block["frame_start"],
        "frame_end": block["frame_end"],
        "stratum_official": block["stratum_official"],
        "stratum_task": block["stratum_task"],
        "stratum_selection": _selection_label(session),
        "known_hard_block": bool(block["global_block_index"] == KNOWN_HARD_GBI),
        "eval_original_index": block["eval_original_index"],
        "arm": ARM,
        "status": status,
        "fidelity": fidelity,
        "sc_descriptive": sc_descriptive,
        "scl": scl,
        "error": error,
        "resources": {
            "wall_sc_s": wall_sc_s,
            "wall_scl_s": wall_scl_s,
            "wall_total_s": wall_total_s,
            "rss_gib_peak_advisory": _peak_rss_gib(),
            "budget_wall_s_per_block": BUDGET_WALL_S_PER_BLOCK,
            "budget_rss_gib_per_block": BUDGET_RSS_GIB_PER_BLOCK,
        },
    }
    with open(_part_path(block["global_block_index"], session), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)


def _resource_abort_record(block: dict, reason: str, elapsed_s: float = 0.0) -> dict:
    """Written directly by the parent (no child launched) when the total
    wall budget (BUDGET_WALL_S_TOTAL) is exhausted before a block's turn,
    or when a running block is hard-terminated for exceeding its per-block
    budget+margin."""
    return {
        "session": block["session"],
        "global_block_index": block["global_block_index"],
        "local_index": block["local_index"],
        "frame_start": block["frame_start"],
        "frame_end": block["frame_end"],
        "stratum_official": block["stratum_official"],
        "stratum_task": block["stratum_task"],
        "stratum_selection": _selection_label(block["session"]),
        "known_hard_block": bool(block["global_block_index"] == KNOWN_HARD_GBI),
        "eval_original_index": block["eval_original_index"],
        "arm": ARM,
        "status": reason,
        "fidelity": None,
        "sc_descriptive": None,
        "scl": None,
        "error": {"type": "ParentAbort", "message": f"{reason} at {elapsed_s:.1f}s"},
        "resources": {
            "wall_sc_s": None,
            "wall_scl_s": None,
            "wall_total_s": elapsed_s,
            "rss_gib_peak_advisory": None,
            "budget_wall_s_per_block": BUDGET_WALL_S_PER_BLOCK,
            "budget_rss_gib_per_block": BUDGET_RSS_GIB_PER_BLOCK,
        },
    }


def _launch_all(targets: list, launch_start: float):
    if "fork" not in mp.get_all_start_methods():
        _fail("this launcher requires the 'fork' start method (Linux/WSL); refusing to run under spawn")
    ctx_mp = mp.get_context("fork")
    procs: dict = {}
    started_at: dict = {}
    by_key = {(b["session"], b["global_block_index"]): b for b in targets}
    pending = list(by_key.keys())
    total_budget_hit = False
    while pending or procs:
        if not total_budget_hit and _total_wall_exceeded(launch_start):
            total_budget_hit = True
            print(
                f"[budget] BUDGET_WALL_S_TOTAL={BUDGET_WALL_S_TOTAL:.0f}s exceeded; "
                f"STOP launching new blocks ({len(pending)} not yet started)",
                file=sys.stderr,
            )
        while pending and len(procs) < MAX_PARALLEL and not total_budget_hit:
            key = pending.pop(0)
            p = ctx_mp.Process(target=_run_one_block_entry, args=(by_key[key],))
            p.start()
            procs[key] = p
            started_at[key] = time.time()
        if total_budget_hit and pending:
            for key in pending:
                with open(_part_path(key[1], key[0]), "w", encoding="utf-8") as fh:
                    json.dump(
                        _resource_abort_record(by_key[key], "not_started_total_wall_budget"),
                        fh, indent=2, sort_keys=True,
                    )
            pending = []
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
                with open(_part_path(key[1], key[0]), "w", encoding="utf-8") as fh:
                    json.dump(
                        _resource_abort_record(by_key[key], "resource_abort_wall_hard_terminate", elapsed),
                        fh, indent=2, sort_keys=True,
                    )
                finished.append(key)
        for key in finished:
            procs.pop(key, None)
        if procs or (pending and not total_budget_hit):
            time.sleep(2.0)


def _wilson(k: int, n: int, z: float = 1.96) -> dict:
    if n <= 0:
        return {"k": k, "n": n, "z": z, "p_hat": None, "lower": None, "upper": None}
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * ((p * (1.0 - p) / n + z * z / (4.0 * n * n)) ** 0.5) / denom
    return {"k": k, "n": n, "z": z, "p_hat": p, "lower": max(0.0, center - half), "upper": min(1.0, center + half)}


def _taxonomy_counts(blocks: list) -> dict:
    """Raw counts only (no verdict string; per prereg.md §4 instruction).
    ``D`` (valid denominator) = exact + verify_failed + decode_failed;
    undetected and resource_abort/error are isolated, never merged in."""
    # Pre-EXECUTE F1 fix (main thread 2026-09-28): only status=="ok" blocks enter the
    # taxonomy; e.g. resource_abort_wall_post_scl keeps its raw scl record in the part
    # file but must NOT also be counted into exact/verify_failed/decode_failed (D).
    ok = [b for b in blocks if b.get("status") == "ok" and b.get("scl")]
    exact = sum(1 for b in ok if b["scl"]["exact"])
    verify_failed = sum(1 for b in ok if b["scl"]["verify_failed"])
    decode_failed = sum(1 for b in ok if b["scl"]["decode_failed"])
    undetected = sum(1 for b in ok if b["scl"]["undetected"])
    resource_abort = sum(1 for b in blocks if "resource_abort" in str(b["status"]))
    errors = sum(1 for b in blocks if str(b["status"]).startswith("error"))
    not_started = sum(1 for b in blocks if str(b["status"]).startswith("not_started"))
    fidelity_mismatch = sum(1 for b in blocks if b["status"] == "STOPPED_FIDELITY_MISMATCH")
    d = exact + verify_failed + decode_failed
    p_hat = (verify_failed + decode_failed) / d if d > 0 else None
    return {
        "n_blocks": len(blocks),
        "exact": exact,
        "verify_failed": verify_failed,
        "decode_failed": decode_failed,
        "undetected": undetected,
        "resource_abort": resource_abort,
        "error": errors,
        "not_started": not_started,
        "fidelity_mismatch": fidelity_mismatch,
        "D_valid_denominator": d,
        "p_hat": p_hat,
        "wilson_95ci": _wilson(verify_failed + decode_failed, d) if d > 0 else None,
    }


def main() -> int:
    if RESULTS_PATH.exists():
        _fail(f"refusing to run: {RESULTS_PATH} already exists (additive-only; one-shot)")

    t0 = _CLOCK()
    mod = _load_mod()
    chain, (scl_joint_mod, native_mod) = _load_scl_joint(mod)
    global _CTX
    _CTX["_mod"] = mod

    all_targets = []
    for session in ("G2", "G3"):
        print(f"[setup] building {session} block descriptors + reproducing session context...", file=sys.stderr)
        blocks_meta = build_session_blocks(mod, session)
        for b in blocks_meta:
            part = _part_path(b["global_block_index"], session)
            if part.exists():
                _fail(f"refusing to run: {part} already exists (additive-only; one-shot)")
        _CTX[session] = _reproduce_session_context(mod, chain, (scl_joint_mod, native_mod), session)
        _CTX[session]["blocks_meta"] = blocks_meta
        print(
            f"[setup] {session} ready: H_total={_CTX[session]['h_total_bits']:.6f} bits, "
            f"f_book_with_crc={_CTX[session]['f_book_with_crc']:.6f}, blocks={len(blocks_meta)}",
            file=sys.stderr,
        )
        all_targets.extend(blocks_meta)

    if len(all_targets) != 64:
        raise AssertionError(f"expected 64 total R2 blocks, got {len(all_targets)}")

    _launch_all(all_targets, t0)

    blocks = []
    for b in all_targets:
        part = _part_path(b["global_block_index"], b["session"])
        with open(part, "r", encoding="utf-8") as fh:
            blocks.append(json.load(fh))

    by_stratum_official = {}
    for stratum in ("A1_CAL_characterization", "HELDOUT_model_selection", "EVAL_already_decoded"):
        by_stratum_official[stratum] = _taxonomy_counts([b for b in blocks if b["stratum_official"] == stratum])
    by_stratum_task = {}
    for stratum in ("never_decoded", "heldout_model_selection", "previously_decoded_eval"):
        by_stratum_task[stratum] = _taxonomy_counts([b for b in blocks if b["stratum_task"] == stratum])
    by_stratum_selection = {}
    for stratum in ("clean", "selection_touched"):
        by_stratum_selection[stratum] = _taxonomy_counts([b for b in blocks if b["stratum_selection"] == stratum])
    pooled = _taxonomy_counts(blocks)
    # Known hard block (R2D): annotated, still counted in every denominator above.
    known_hard = [
        {"session": b["session"], "global_block_index": b["global_block_index"], "status": b["status"],
         "scl": ({k: b["scl"][k] for k in ("exact", "verify_failed", "decode_failed", "undetected")} if b.get("scl") else None)}
        for b in blocks if b.get("known_hard_block")
    ]
    clean_note = "n=32 descriptive only; the primary judgment is the 64-block pooled result"

    # undetected is a security signal: STOP on ANY block's SCL record, including an
    # over-budget (resource_abort_wall_post_scl) block excluded from the taxonomy (F1 fix).
    n_undetected_total = sum(1 for b in blocks if b.get("scl") and b["scl"]["undetected"])
    stop_undetected = bool(n_undetected_total >= 1)
    # Main-thread ruling 2026-09-28 (D_NEW_FIDELITY_SCOPE): keep predecessor D3
    # semantics -- any EVAL-block fidelity mismatch means the input reconstruction
    # is suspect for the whole run, so the pooled result must not be adjudicated.
    fidelity_compromised = bool(pooled["fidelity_mismatch"] >= 1)
    undetected_block_ids = [
        {"session": b["session"], "global_block_index": b["global_block_index"]}
        for b in blocks if b.get("scl") and b["scl"]["undetected"]
    ]
    resource_abort_block_ids = [
        {"session": b["session"], "global_block_index": b["global_block_index"], "status": b["status"]}
        for b in blocks if "resource_abort" in str(b["status"])
    ]
    not_started_block_ids = [
        {"session": b["session"], "global_block_index": b["global_block_index"]}
        for b in blocks if str(b["status"]).startswith("not_started")
    ]

    results = {
        "probe_id": "r2e-fer-shg-64-L32-f124",
        "classification": (
            "Tier-Y one-shot measurement of the NATIVE SCL implementation (scl_joint_native, L=32, f~1.24, K=6657/253/6404), "
            "frozen 64-block pool per DATA_LEDGER.md §7. Delta-successor of workspace/r2b_fer_shg_64_L32_f120/ per "
            "AGENTS.md §10.4; NOT a reproduction of scl_joint. Requires independent "
            "Pre-EXECUTE AND Pre-RESULT review, explicit PI authorization, and main-thread "
            "adjudication of FER_MEASURED_AT_CONTRACT (this script computes NO verdict string)."
        ),
        "authorization": {
            "who": None,
            "when": None,
            "verbatim": None,
            "source": "AUTHORIZATION_PROMPT.md (this directory) -- NOT YET GRANTED",
        },
        "frozen_params": {
            "arm": ARM,
            "list_width_L": LIST_WIDTH_L,
            "top_m": TOP_M,
            "crc_bits_extra": CRC_BITS_EXTRA,
            "k1": _CTX["G2"]["k1"],
            "k2": _CTX["G2"]["k2"],
            "k_total": K_TOTAL,
            "f_target": F_TARGET,
            "k1_sc_fidelity": _CTX["G2"]["k1_sc"],
            "k2_sc_fidelity": _CTX["G2"]["k2_sc"],
            "decoder": "scl_joint_native.scl_joint_decode_native (Rust whole recursion), default native threads",
            "budget": {"wall_s_per_block": BUDGET_WALL_S_PER_BLOCK, "rss_gib_per_block": BUDGET_RSS_GIB_PER_BLOCK,
                       "wall_s_total": BUDGET_WALL_S_TOTAL, "max_parallel": MAX_PARALLEL},
            "n": _CTX["G2"]["n"],
            "construction_digest": mod.G2_CONSTRUCTION_DIGEST,
            "tag_master_shared": R2_TAG_MASTER,
            "eval_seed_shared": R2_EVAL_SEED,
            "k_source": "R2D f1.24_s0380 (workspace/r2d_locate_f_k_g2/RESULT_REVIEW.md)",
        },
        "per_session": {
            session: {
                "h_total_bits": _CTX[session]["h_total_bits"],
                "kdb_no_crc": _CTX[session]["kdb_no_crc"],
                "kdb_with_crc": _CTX[session]["kdb_with_crc"],
                "f_book_no_crc_computed": _CTX[session]["f_book_no_crc"],
                "f_book_with_crc_computed": _CTX[session]["f_book_with_crc"],
                "n_pairs": _CTX[session]["n_pairs"],
                "n_frames": _CTX[session]["n_frames"],
                "align_peak": _CTX[session]["align_peak"],
            }
            for session in ("G2", "G3")
        },
        "blocks": blocks,
        "taxonomy_by_stratum_official": by_stratum_official,
        "taxonomy_by_stratum_task": by_stratum_task,
        "taxonomy_by_stratum_selection": by_stratum_selection,
        "clean_layer_G3_descriptive": {"note": clean_note, **by_stratum_selection["clean"]},
        "known_hard_block_gbi23": known_hard,
        "taxonomy_pooled": pooled,
        "stop_undetected": stop_undetected,
        "fidelity_compromised": fidelity_compromised,
        "undetected_block_ids": undetected_block_ids,
        "resource_abort_block_ids": resource_abort_block_ids,
        "not_started_block_ids": not_started_block_ids,
        "selection_freedom_exercised": {
            "A1_CAL_characterization": "M0 (incumbent) prior fit only; not M2/NLL model selection.",
            "HELDOUT_model_selection": "Participated in the NLL model-selection scoring gate (G1R2/G2/G3).",
            "EVAL_already_decoded": "Not itself a model-selection step; decoded under the already-frozen candidate.",
            "selection_G2": "G2 32 blocks took part in the R2D f/k selection (stratum_selection=selection_touched; R2 separate stratum).",
            "selection_G3": "G3 32 blocks never took part in f/k selection (stratum_selection=clean).",
        },
        "claims": (
            "No verdict string, no FER_MEASURED_AT_CONTRACT judgment, no candidate/accepted promotion "
            "computed by this script -- raw taxonomy counts and Wilson CIs only. Adjudication is a "
            "main-thread act per AGENTS.md §10.3 Pre-RESULT review, using the judgment rules in "
            "docs/nbpolar/R2_REMAINING_DECISIONS_20260928.md (predicated on the T4 ledger rows this "
            "script's placeholders depend on being DECIDED before execution)."
        ),
        "timing": {"wall_s_total": _CLOCK() - t0},
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
    print(
        f"DONE n_blocks={len(blocks)} pooled_D={pooled['D_valid_denominator']} "
        f"pooled_exact={pooled['exact']} pooled_verify_failed={pooled['verify_failed']} "
        f"pooled_decode_failed={pooled['decode_failed']} pooled_undetected={pooled['undetected']} "
        f"stop_undetected={stop_undetected} resource_abort={pooled['resource_abort']} "
        f"fidelity_mismatch={pooled['fidelity_mismatch']} wall_s={_CLOCK()-t0:.1f}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
