#!/usr/bin/env python3
"""R2D descriptive real-data locating probe (Tier X, non-claim): where do f and the
k1/k2 split put the native SCL (L=32, top_m=4, CRC-16) on the G2 session's 32 blocks?

Grid: f_target in {1.22,1.24,1.26} x k1 share in {0.0469,0.0380}  (6 configs) x 32 G2
blocks = 192 SCL decodes, 4 worker processes, native threads 2 per process.
G3 is never read or decoded (kept as a clean layer). No SC path, no SC fidelity gate.
Copied/adapted from workspace/r2b_fer_shg_64_L32_f120/run.py (unchanged there).
Outputs only in this directory: results.json + part_<cfg>_G2_<idx:02d>.json.
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

R2D_EVAL_SEED = 2026092903
R2D_TAG_MASTER = 2026102903
ARM = "B_M2_32f_candidate"
LIST_WIDTH_L = 32
TOP_M = 4
H_BAR_FOR_K = (0.8168138 + 0.8214782) / 2.0  # same definition as R2B
N_FRAME = 32768
F_TARGETS = (1.22, 1.24, 1.26)
K1_SHARES = (0.0469, 0.0380)
CRC_BITS_EXTRA = 16


def build_configs() -> list:
    """Config-major, f ascending, share 0.0469 before 0.0380."""
    out = []
    for f in F_TARGETS:
        for sh in K1_SHARES:
            k_total = int(round(f * H_BAR_FOR_K * N_FRAME / 5))
            k1 = int(round(sh * k_total))
            out.append(dict(cfg=f"f{f:.2f}_s{int(round(sh * 1e4)):04d}", f_target=f, k1_share=sh,
                            k_total=k_total, k1=k1, k2=k_total - k1))
    return out


CONFIGS = build_configs()

NATIVE_THREADS = 2
N_WORKERS = 4
BUDGET_WALL_S_PER_TASK = 300.0
BUDGET_RSS_GIB_PER_TASK = 4.0
BUDGET_WALL_S_TOTAL = 3.5 * 3600.0  # raised from 2 h by main thread 2026-09-29 (WSL nproc=8)
HARD_TERMINATE_MARGIN_S = 120.0
_CLOCK = time.monotonic

BLOCK_FRAMES = 128
A1_CAL_FIRST, A1_CAL_BLOCKS = 0, 8
CHARHELD_FIRST, CHARHELD_BLOCKS = 1056, 10
HELDOUT_FIRST = 1838

RESULTS_PATH = THIS_DIR / "results.json"
PRIOR_R2B = REPO_ROOT / "workspace" / "r2b_fer_shg_64_L32_f120" / "results.json"
PRIOR_R2 = REPO_ROOT / "workspace" / "r2_fer_shg_64" / "results.json"
G2_CFG = dict(acq_id="20260113_SHG_Type2PPLN_3s", read_fn="_read_timetags_production")

_CTX: dict = {}


def _total_wall_exceeded(t_start: float) -> bool:
    return (_CLOCK() - t_start) > BUDGET_WALL_S_TOTAL


def _fail(msg: str, code: int = 2):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _load_mod():
    return importlib.import_module("scripts.m2_prior_validation")


def _load_scl_joint(mod):
    chain = mod._load_g2_decoder_chain()
    base_nb = "comparison_bench.src.comparison_bench.formal_ir.nbpolar"
    scl_joint_mod = importlib.import_module(base_nb + ".scl_joint")
    native_mod = importlib.import_module(base_nb + ".scl_joint_native")
    native_mod.native_backend_info()
    # Native thread count: the module has no env var; scl_joint_native._default_threads()
    # (= os.cpu_count()) sets L1 nthreads and L2 nthreads = that // top_m_used. Override
    # it at runtime in this process only (frozen file untouched; children inherit via fork).
    native_mod._default_threads = lambda: NATIVE_THREADS
    return chain, (scl_joint_mod, native_mod)


def build_g2_blocks(mod) -> list:
    """32 frozen G2 block descriptors: A1_CAL(8) -> CHAR/HELDOUT(10) -> EVAL(14)."""
    out, idx = [], 0

    def add(s, e, so, st, ev):
        nonlocal idx
        out.append(dict(session="G2", local_index=idx, global_block_index=idx, frame_start=s, frame_end=e,
                        stratum_official=so, stratum_task=st, eval_original_index=ev))
        idx += 1

    for i in range(A1_CAL_BLOCKS):
        s = A1_CAL_FIRST + i * BLOCK_FRAMES
        add(s, s + BLOCK_FRAMES - 1, "A1_CAL_characterization", "never_decoded", None)
    for i in range(CHARHELD_BLOCKS):
        s = CHARHELD_FIRST + i * BLOCK_FRAMES
        e = s + BLOCK_FRAMES - 1
        add(s, e, "HELDOUT_model_selection", "heldout_model_selection" if e >= HELDOUT_FIRST else "never_decoded", None)
    for oi, (s, e) in enumerate(mod.g2_eval_blocks()):
        add(s, e, "EVAL_already_decoded", "previously_decoded_eval", oi)
    if idx != 32:
        raise AssertionError(f"G2 block generation drift: {idx}")
    return out


def _reproduce_g2_context(mod, chain, mods) -> dict:
    """Same frozen-function chain as R2B `_reproduce_session_context`, G2 only."""
    scl_joint_mod, native_mod = mods
    identity = chain.verify_predecessor_construction(mod.G2_CONSTRUCTION_PATH,
                                                     expected_digest=mod.G2_CONSTRUCTION_DIGEST)
    l1_order, l2_order = identity["l1_order"], identity["l2_order"]
    got = getattr(mod, G2_CFG["read_fn"])(G2_CFG["acq_id"])
    tA, tB = got["tA"], got["tB"]
    if float(got.get("other_frac", 0.0)) > 0.20:
        raise RuntimeError(f"CHANNEL_FAIL other_frac={got.get('other_frac')}")
    peak = mod._align_frozen(tA, tB)
    if not (peak.get("status") == "ok" and peak.get("peak_to_bg") is not None
            and float(peak["peak_to_bg"]) >= mod.G1_PEAK_TO_BG_MIN):
        raise RuntimeError(f"ALIGN_FAIL {peak}")
    offset = int(peak["peak_center_ps"])
    sweep = mod._yield_sweep_selfcheck(tA, tB, offset)
    ok, sweep["yield_note"] = mod._sweep_accept(sweep)
    if not ok:
        raise RuntimeError(f"ALIGN_INCONSISTENT offset={offset}")
    alice, bob = mod.pair_narrow_nearest_unique(tA, tB, offset, 200)
    del tA, tB
    n_pairs = int(alice.size)
    n_frames = n_pairs // mod.G1_FRAME_PAIRS
    gate = mod.contract_for_freeze({"pairing_window_primary": 200})["repro_gate"]
    if not (peak.get("peak_center_ps") == gate["peak_center_ps"] and peak.get("peak_sigma_ps") == gate["peak_sigma_ps"]
            and peak.get("status") == gate["status"] and n_pairs == gate["n_pairs"] and n_frames == gate["n_frames"]):
        raise RuntimeError(f"ALIGN_INCONSISTENT reproduction gate mismatch (expected {gate})")
    frames_a, frames_b, _ = mod.chunk_frames(alice, bob, 702)
    del alice, bob

    m2_mod, prior_mod = mod._frozen_m2(), mod._frozen_prior()
    cal_ids = mod.g2_cal_ids(ARM)
    cal_a, cal_b = frames_a[cal_ids].ravel(), frames_b[cal_ids].ravel()
    fit = mod.fit_g2_arm(ARM, cal_a, cal_b, "CIRCULAR", m2_mod)
    p1_table = np.asarray(prior_mod.derive_p1(fit["joint"]), dtype=np.float64)
    p2_table = np.asarray(prior_mod.derive_p2(fit["joint"]), dtype=np.float64)
    counts = mod.build_counts_1024(cal_a, cal_b)
    p_b = counts.sum(axis=0).astype(np.float64)
    p_b = p_b / p_b.sum()
    h_total_bits = float(mod.model_entropy_bits(fit["joint"], p_b, prior_mod)["H_total_bits"])

    field = chain.make_gf32()
    alpha = int(chain.alpha)
    return dict(
        chain=chain, scl_joint_mod=scl_joint_mod, native_mod=native_mod, l1_order=l1_order, l2_order=l2_order,
        frames_a=frames_a, frames_b=frames_b, p1_table=p1_table, p2_table=p2_table, field=field, alpha=alpha,
        polar_fn=mod._bind_g2_polar(chain.polar_transform, field, alpha),
        tag_master=int(R2D_TAG_MASTER), eval_seed=int(R2D_EVAL_SEED), n=int(mod.G2_N),
        h_total_bits=h_total_bits, n_pairs=n_pairs, n_frames=n_frames, align_peak=dict(peak),
    )


def f_book(chain, h_total_bits, n, k_total):
    no_crc = int(chain.disclosed_bits_per_coordinate * k_total + chain.tag_bits)
    with_crc = no_crc + CRC_BITS_EXTRA
    return dict(kdb_no_crc=no_crc, kdb_with_crc=with_crc,
                f_book_no_crc=no_crc / (h_total_bits * n), f_book_with_crc=with_crc / (h_total_bits * n))


def _scl_call(mod, ctx: dict, block: dict, alice, bob) -> dict:
    """Identical to R2B `_scl_call` (native SCL L=32 top_m=4, CRC-16, tag via
    operational_seed_bits(tag_master, n, global_block_index)); k1/k2 come from ctx."""
    chain, scl_joint_mod = ctx["chain"], ctx["scl_joint_mod"]
    l1_pos = np.asarray(ctx["l1_order"], dtype=np.int64)[: ctx["k1"]]
    l2_pos = np.asarray(ctx["l2_order"], dtype=np.int64)[: ctx["k2"]]
    views = mod.g2_truth_views(alice, ctx["polar_fn"])
    high_true, low_true, u1_true, u2_true, labels_true = (views[k] for k in ("high", "low", "u1", "u2", "labels"))
    crc_true = int(scl_joint_mod.labels_crc16(labels_true))
    res = ctx["native_mod"].scl_joint_decode_native(
        bob, crc_true, field=ctx["field"], alpha=ctx["alpha"], p1_table=ctx["p1_table"], p2_table=ctx["p2_table"],
        d1_positions=l1_pos, d1_values=u1_true[l1_pos], d2_positions=l2_pos, d2_values=u2_true[l2_pos],
        list_width_L=LIST_WIDTH_L, top_m=TOP_M)
    n = ctx["n"]
    seed = chain.operational_seed_bits(ctx["tag_master"], n, block["global_block_index"],
                                       bit_length=chain.seed_bits_for(n))
    tag_true = chain.toeplitz_tag(chain.labels_to_bits(labels_true), seed, chain.tag_bits)
    tag_hat = chain.toeplitz_tag(chain.labels_to_bits(res.label_hat), seed, chain.tag_bits)
    tag_pass, crc_pass = bool(tag_hat == tag_true), bool(res.crc_pass)
    label_exact = bool(np.array_equal(np.asarray(res.label_hat), np.asarray(labels_true)))
    decode_failed = bool(int(res.l1_survivor_count) == 0 or int(res.candidates_considered) == 0)
    accepted = bool(crc_pass and tag_pass and not decode_failed)
    return {
        "list_width_L": LIST_WIDTH_L, "top_m_requested": TOP_M, "top_m_used": int(res.top_m_used),
        "l1_survivor_count": int(res.l1_survivor_count), "candidates_considered": int(res.candidates_considered),
        "m1": float(res.m1), "m2": float(res.m2), "joint_metric": float(res.joint_metric),
        "crc_pass": crc_pass, "tag_pass": tag_pass, "label_exact": label_exact, "accepted": accepted,
        "exact": bool(accepted and label_exact),
        "undetected": bool(accepted and not label_exact),
        "verify_failed": bool((not accepted) and not decode_failed),
        "decode_failed": decode_failed,
        "l1_exact_scl": bool(np.array_equal(np.asarray(res.high_hat), high_true)),
        "hard_l2_exact_scl": bool(np.array_equal(np.asarray(res.low_hat), low_true)),
        "l1_error_symbols_scl": int(np.sum(np.asarray(res.high_hat) != high_true)),
        "l2_error_symbols_scl": int(np.sum(np.asarray(res.low_hat) != low_true)),
        "k1_scl": int(ctx["k1"]), "k2_scl": int(ctx["k2"]),
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


def _part_path(cfg: str, idx: int) -> Path:
    return THIS_DIR / f"part_{cfg}_G2_{idx:02d}.json"


def _base_record(task: dict) -> dict:
    b, c = task["block"], task["config"]
    return {"cfg": c["cfg"], "f_target": c["f_target"], "k1_share": c["k1_share"], "k_total": c["k_total"],
            "k1": c["k1"], "k2": c["k2"], "global_block_index": b["global_block_index"],
            "frame_start": b["frame_start"], "frame_end": b["frame_end"],
            "stratum_official": b["stratum_official"], "stratum_task": b["stratum_task"],
            "eval_original_index": b["eval_original_index"], "arm": ARM}


def _run_task(task: dict):
    """Forked child: one (config, block) SCL decode; writes one part file; never raises."""
    b, c = task["block"], task["config"]
    t0 = time.perf_counter()
    status, error, scl = "ok", None, None
    try:
        mod, ctx = _CTX["_mod"], dict(_CTX["G2"], k1=c["k1"], k2=c["k2"])
        s, e = b["frame_start"], b["frame_end"]
        bob = ctx["frames_b"][s: e + 1].ravel()
        alice = ctx["frames_a"][s: e + 1].ravel()
        scl = _scl_call(mod, ctx, b, alice, bob)
        if time.perf_counter() - t0 > BUDGET_WALL_S_PER_TASK:
            status = "resource_abort_wall_post_scl"
        rss = _peak_rss_gib()
        if rss is not None and rss > BUDGET_RSS_GIB_PER_TASK:
            status = "resource_abort_rss_post_scl"
    except Exception as exc:
        status = f"error:{type(exc).__name__}"
        error = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
    rec = _base_record(task)
    rec.update(status=status, scl=scl, error=error,
               resources=dict(wall_total_s=time.perf_counter() - t0, rss_gib_peak_advisory=_peak_rss_gib(),
                              native_threads=NATIVE_THREADS))
    with open(_part_path(c["cfg"], b["global_block_index"]), "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)


def _abort_record(task: dict, reason: str, elapsed_s: float = 0.0) -> dict:
    rec = _base_record(task)
    rec.update(status=reason, scl=None, error={"type": "ParentAbort", "message": f"{reason} at {elapsed_s:.1f}s"},
               resources=dict(wall_total_s=elapsed_s, rss_gib_peak_advisory=None, native_threads=NATIVE_THREADS))
    return rec


def _write(path: Path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)


def _launch_all(tasks: list, launch_start: float, n_workers: int = None):
    n_workers = N_WORKERS if n_workers is None else n_workers
    if "fork" not in mp.get_all_start_methods():
        _fail("requires the 'fork' start method (Linux/WSL)")
    mpc = mp.get_context("fork")
    key = lambda t: (t["config"]["cfg"], t["block"]["global_block_index"])
    by_key = {key(t): t for t in tasks}
    pending, procs, started = list(by_key), {}, {}
    total_hit = False
    while pending or procs:
        if not total_hit and _total_wall_exceeded(launch_start):
            total_hit = True
            print(f"[budget] total wall exceeded; {len(pending)} tasks not started", file=sys.stderr)
        while pending and len(procs) < n_workers and not total_hit:
            k = pending.pop(0)
            p = mpc.Process(target=_run_task, args=(by_key[k],))
            p.start()
            procs[k], started[k] = p, time.time()
        if total_hit and pending:
            for k in pending:
                _write(_part_path(*k), _abort_record(by_key[k], "not_started_total_wall_budget"))
            pending = []
        done = []
        for k, p in list(procs.items()):
            if not p.is_alive():
                p.join()
                done.append(k)
                continue
            el = time.time() - started[k]
            if el > BUDGET_WALL_S_PER_TASK + HARD_TERMINATE_MARGIN_S:
                p.terminate()
                p.join(timeout=10)
                _write(_part_path(*k), _abort_record(by_key[k], "resource_abort_wall_hard_terminate", el))
                done.append(k)
        for k in done:
            procs.pop(k, None)
        if procs or (pending and not total_hit):
            time.sleep(1.0)


def _wilson(k: int, n: int, z: float = 1.96) -> dict:
    if n <= 0:
        return {"k": k, "n": n, "p_hat": None, "lower": None, "upper": None}
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2.0 * n)) / d
    h = z * ((p * (1.0 - p) / n + z * z / (4.0 * n * n)) ** 0.5) / d
    return {"k": k, "n": n, "z": z, "p_hat": p, "lower": max(0.0, c - h), "upper": min(1.0, c + h)}


def _taxonomy(blocks: list) -> dict:
    ok = [b for b in blocks if b.get("status") == "ok" and b.get("scl")]
    ex = sum(b["scl"]["exact"] for b in ok)
    vf = sum(b["scl"]["verify_failed"] for b in ok)
    df = sum(b["scl"]["decode_failed"] for b in ok)
    ud = sum(1 for b in blocks if b.get("scl") and b["scl"]["undetected"])
    d = ex + vf + df
    fails = [b for b in ok if b["scl"]["verify_failed"] or b["scl"]["decode_failed"]]
    l1_fail = [b["global_block_index"] for b in fails if not b["scl"]["l1_exact_scl"]]
    l2_only = [b["global_block_index"] for b in fails if b["scl"]["l1_exact_scl"] and not b["scl"]["hard_l2_exact_scl"]]
    other = [b["global_block_index"] for b in fails if b["scl"]["l1_exact_scl"] and b["scl"]["hard_l2_exact_scl"]]
    return {
        "n_blocks": len(blocks), "exact": ex, "verify_failed": vf, "decode_failed": df, "undetected": ud,
        "resource_abort": sum(1 for b in blocks if "resource_abort" in str(b["status"])),
        "error": sum(1 for b in blocks if str(b["status"]).startswith("error")),
        "not_started": sum(1 for b in blocks if str(b["status"]).startswith("not_started")),
        "D_valid_denominator": d,
        "wilson_95ci_fail": _wilson(vf + df, d),
        "failure_attribution": {"L1_not_exact_blocks": l1_fail, "L1_exact_L2_not_exact_blocks": l2_only,
                                "L1_L2_exact_but_failed_blocks": other},
        "STOP_undetected": bool(ud >= 1),
    }


def _prior_by_block(path: Path) -> dict:
    """Read-only per-G2-block SCL outcome of a prior measurement (descriptive cross-table)."""
    out = {}
    with open(path, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    for b in d["blocks"]:
        if b["session"] == "G2" and b.get("scl"):
            s = b["scl"]
            out[b["global_block_index"]] = dict(exact=s["exact"], l1_exact=s["l1_exact_scl"], l2_exact=s["hard_l2_exact_scl"])
    return out


def _selection_rule(per_cfg: dict) -> dict:
    """Mechanical prereg rule: among configs with verify_failed<=1 (and no undetected, none unfinished),
    smallest f; tie -> k1 share 0.0469. None qualifies -> hand to PI."""
    ok = []
    for c in CONFIGS:
        t = per_cfg[c["cfg"]]["taxonomy"]
        finished = t["D_valid_denominator"] == 32 and t["not_started"] == 0 and t["error"] == 0 and t["resource_abort"] == 0
        if finished and not t["STOP_undetected"] and t["verify_failed"] + t["decode_failed"] <= 1:
            ok.append(c)
    if not ok:
        return {"selected": None, "note": "no config satisfies verify_failed<=1 on G2; report to PI"}
    fmin = min(c["f_target"] for c in ok)
    tied = [c for c in ok if c["f_target"] == fmin]
    pick = max(tied, key=lambda c: c["k1_share"])  # 0.0469 preferred on ties
    return {"selected": pick["cfg"], "qualifying": [c["cfg"] for c in ok]}


def main() -> int:
    if RESULTS_PATH.exists() or list(THIS_DIR.glob("part_*.json")):
        _fail(f"refusing to run: results.json or part_*.json already exists in {THIS_DIR} (additive-only)")
    t0 = _CLOCK()
    mod = _load_mod()
    chain, mods = _load_scl_joint(mod)
    _CTX["_mod"] = mod
    print("[setup] reproducing G2 context (G3 never read)...", file=sys.stderr)
    g2 = _reproduce_g2_context(mod, chain, mods)
    _CTX["G2"] = g2
    blocks_meta = build_g2_blocks(mod)
    cfg_table = []
    for c in CONFIGS:
        cfg_table.append(dict(c, **f_book(chain, g2["h_total_bits"], g2["n"], c["k_total"])))
        print(f"[setup] {c['cfg']}: K={c['k_total']} k1={c['k1']} k2={c['k2']} f_book_crc={cfg_table[-1]['f_book_with_crc']:.6f}",
              file=sys.stderr)
    tasks = [dict(config=c, block=b) for c in CONFIGS for b in blocks_meta]
    assert len(tasks) == 192
    _launch_all(tasks, t0)

    per_cfg = {}
    for c in CONFIGS:
        recs = []
        for b in blocks_meta:
            with open(_part_path(c["cfg"], b["global_block_index"]), "r", encoding="utf-8") as fh:
                recs.append(json.load(fh))
        per_cfg[c["cfg"]] = {"config": next(x for x in cfg_table if x["cfg"] == c["cfg"]), "taxonomy": _taxonomy(recs),
                             "blocks": recs}
    prior_r2b, prior_r2 = _prior_by_block(PRIOR_R2B), _prior_by_block(PRIOR_R2)
    cross = []
    for b in blocks_meta:
        i = b["global_block_index"]
        row = dict(global_block_index=i, stratum_task=b["stratum_task"], stratum_official=b["stratum_official"],
                   R2_f127_L16=prior_r2.get(i), R2B_f120_L32=prior_r2b.get(i))
        for c in CONFIGS:
            s = per_cfg[c["cfg"]]["blocks"][i].get("scl")
            row[c["cfg"]] = None if s is None else dict(exact=s["exact"], l1_exact=s["l1_exact_scl"], l2_exact=s["hard_l2_exact_scl"])
        cross.append(row)
    results = {
        "probe_id": "r2d-locate-f-k-g2",
        "classification": "Tier-X descriptive locating probe on G2 only (non-claim); G2 blocks become 'selection-touched' stratum (R2).",
        "frozen_params": dict(list_width_L=LIST_WIDTH_L, top_m=TOP_M, eval_seed=R2D_EVAL_SEED, tag_master=R2D_TAG_MASTER,
                              h_bar_for_k=H_BAR_FOR_K, workers=N_WORKERS, native_threads=NATIVE_THREADS,
                              budget=dict(wall_s_per_task=BUDGET_WALL_S_PER_TASK, rss_gib=BUDGET_RSS_GIB_PER_TASK,
                                          wall_s_total=BUDGET_WALL_S_TOTAL),
                              native_backend=mods[1].native_backend_info()),
        "g2_session": dict(h_total_bits=g2["h_total_bits"], n_pairs=g2["n_pairs"], n_frames=g2["n_frames"],
                           align_peak=g2["align_peak"]),
        "config_table": cfg_table,
        "per_config": {k: {"config": v["config"], "taxonomy": v["taxonomy"]} for k, v in per_cfg.items()},
        "per_config_blocks": {k: v["blocks"] for k, v in per_cfg.items()},
        "cross_table": cross,
        "selection_rule_evaluation": _selection_rule(per_cfg),
        "stop_undetected_configs": [k for k, v in per_cfg.items() if v["taxonomy"]["STOP_undetected"]],
        "timing": {"wall_s_total": _CLOCK() - t0},
    }
    _write(RESULTS_PATH, results)
    for k, v in per_cfg.items():
        t = v["taxonomy"]
        print(f"{k}: exact={t['exact']} vf={t['verify_failed']} df={t['decode_failed']} ud={t['undetected']} "
              f"ns={t['not_started']} err={t['error']}", file=sys.stderr)
    print(f"DONE selection={results['selection_rule_evaluation']} wall_s={_CLOCK()-t0:.1f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
