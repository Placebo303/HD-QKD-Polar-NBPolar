import os, sys, json, time, traceback
import numpy as np
try:
    import resource
except ImportError:
    resource = None

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
OUT = ROOT + "/workspace/probes/l2-singlefactor-c1-k550/results.json"
sys.path.insert(0, "/mnt/d/Code/qkd-reconciliation-lab/src")
from comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.formal_ir.nbpolar.prior import (build_p1_metrics, gather_p2_metrics,
    probs_to_symbol_metric, Provenance)
from comparison_bench.formal_ir.nbpolar.sc import sc_decode
from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.formal_ir.nbpolar.transform import polar_transform
from qkd_recon import polar_core as pc

T0 = time.perf_counter()
Q = 1024; R = 10; N = 1024; NLOG = 10; ALPHA = 2
P_F4 = {"p0": 0.75, "p1": 0.24, "pm1": 0.005, "prest": 0.005}
# C1 Tier-X runner derived from the k550 predecessor; prepared only and not executed.
K1_FROZEN = 10
K2_SINGLE = 550
K2_GRID = (550,)
# disclosed=5*(10+550)=2800 bits; f_book=disclosed/HN bookkeeping only (NOT an efficiency point), tag EXCLUDED (DP-N2); kdb=disclosed+64 in-run
K2_POINTS = {
    550: {"label": "k2_550", "disclosed": 2800, "f_book": 2.9344139789},
}
BASE_ID = "L2-BASE-P16-FROZEN"
CAND_ID = "L2-CAND-BEST-H2-550"
# Predecessor formula retained as comment (not executed): D=round(f*HN); kt=round(f*HN/5); k1=round(kt*319/6811); k2=round(kt*6492/6811)
SEEDS = (2026092601, 2026092602, 2026092603, 2026092604)
BLOCKS = 16
DESIGN_SEED = 2026092600
DESIGN_MC = 128
LIST_SIZE = 8
G2_K1, G2_K2 = 319, 6492
WALL_LIMIT_S = 200.0
RSS_LIMIT = 1 * 1024 ** 3
OUT_KEYS = ("exact", "undetected", "verify_failed", "decode_failed", "resource_abort")
ARMS2 = ("BASE", "CAND")
INTERPRETER = "/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python"
ENV = {"PYTHONDONTWRITEBYTECODE": "1", "NUMBA_CACHE_DIR": "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/l2-singlefactor-c1-k550/.numba_cache",
       "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
       "NUMBA_NUM_THREADS": "1", "PYTHONPATH": ROOT + "/comparison_bench/src"}

def rss_bytes():
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024

def budget():
    wall = time.perf_counter() - T0
    rss = rss_bytes()
    reasons = []
    if wall > WALL_LIMIT_S:
        reasons.append("wall_s>200")
    if rss is not None and rss > RSS_LIMIT:
        reasons.append("rss>1GiB")
    return wall, rss, reasons

def summarize(xs):
    xs = [float(v) for v in xs]
    n = len(xs)
    if n == 0:
        return {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0}
    mean = sum(xs) / n
    var = sum((v - mean) ** 2 for v in xs) / (n - 1) if n > 1 else 0.0
    return {"series": xs, "mean": mean, "sample_std": float(np.sqrt(var)),
            "range": [min(xs), max(xs)], "n": n}

def f4_pmf(q):
    p = np.zeros(q)
    p[0] = P_F4["p0"]
    p[1 % q] = P_F4["p1"]
    p[(q - 1) % q] = P_F4["pm1"]
    rest = [d for d in range(q) if d not in (0, 1 % q, (q - 1) % q)]
    for d in rest:
        p[d] = P_F4["prest"] / (q - 3)
    assert abs(p.sum() - 1.0) < 1e-12
    return p

def natural_EJB(i):
    E = 1 << i
    L = 1 << (R - 1 - i)
    e = np.arange(E)[:, None, None]
    b = np.array([0, 1])[None, :, None]
    l = np.arange(L)[None, None, :]
    return (e | (b << i) | (l << (i + 1))).astype(np.int64)

def worst_k(Hvec, k):
    return np.sort(np.argsort(-Hvec, kind="stable")[:k]).astype(np.int64)

def best_k(Hvec, k):
    return np.sort(np.argsort(Hvec, kind="stable")[:k]).astype(np.int64)
def a2_masks(D):
    order = np.argsort(Zall.ravel(), kind="stable")
    info = order[: R * N - D]
    masks = np.zeros((R, N), dtype=np.uint8)
    masks[info // N, info % N] = 1
    guard = []
    for i in range(R):
        if masks[i].sum() == 0:
            pos = int(np.argmin(Zall[i]))
            masks[i, pos] = 1
            guard.append([int(i), pos])
    return masks, int(R * N - masks.sum()), guard

def plane_llr(logp_sym, E, i):
    if E.shape[1] == 0:
        e = np.zeros(N, dtype=np.int64)
    else:
        e = (E * (1 << np.arange(E.shape[1], dtype=np.int64))).sum(axis=1).astype(np.int64)
    TT = EJBs[i][e]
    ev = logp_sym[np.arange(N)[:, None, None], TT]
    e0 = np.logaddexp.reduce(ev[:, 0, :], axis=1)
    e1 = np.logaddexp.reduce(ev[:, 1, :], axis=1)
    return e0 - e1

def a2_chain(dec, logp_sym, masks, fv, u_true):
    E = np.zeros((N, 0), dtype=np.int64)
    ok = True
    for i in range(R):
        llr = np.ascontiguousarray(plane_llr(logp_sym, E, i), dtype=np.float64)
        if dec == "sc":
            uh = pc.sc_decode_batch(llr[None, :], masks[i], fv[i:i + 1], NLOG)[0]
        else:
            uh = pc.scl_decode_batch(llr[None, :], masks[i], fv[i:i + 1], NLOG, LIST_SIZE)[0]
    # NOTE: retained byte-identical to predecessor (A2 not run; loop body kept for traceability)
        if not np.array_equal(uh, u_true[i]):
            ok = False
        xh = pc.polar_encode(uh, NLOG).astype(np.int64)
        E = np.column_stack([E, xh]) if E.shape[1] else xh[:, None]
    return ok

def main():
    global Zall, EJBs
    reruns = 0
    log = []
    design_stop = []
    pmf = f4_pmf(Q)
    logpmf = np.log(pmf)
    H = float(-(pmf[pmf > 0] * np.log2(pmf[pmf > 0])).sum())
    HN = H * N
    table = pmf[(np.arange(Q)[:, None] - np.arange(Q)[None, :]) % Q]
    coldev = float(np.abs(table.sum(axis=0) - 1.0).max())
    p1, p2 = tl.layer_metric_tables(table)
    field = make_gf32()
    EJBs = [natural_EJB(i) for i in range(R)]

    Zall = np.empty((R, N), dtype=np.float64)
    Z0 = []
    Wmat = pmf[(np.arange(Q)[:, None] - np.arange(Q)[None, :]) % Q]
    for i in range(R):
        Ej = EJBs[i]
        Pm = Wmat[:, Ej].sum(axis=3) / (1 << (R - 1))
        z0 = float(np.sqrt(Pm[:, :, 0] * Pm[:, :, 1]).sum())
        Z0.append(z0)
        z = np.array([z0])
        while z.shape[0] < N:
            zn = np.empty(2 * z.shape[0])
            zn[0::2] = np.minimum(1.0, 2 * z - z * z)
            zn[1::2] = z * z
            z = zn
        Zall[i] = z
    log.append("A2 pooled-Z design done; Z0=" + repr([round(v, 6) for v in Z0]))

    rng = np.random.default_rng(DESIGN_SEED)
    H1 = np.zeros(N)
    H2 = np.zeros(N)
    allpos = np.arange(N)
    design_stopped = False
    mdone = 0
    for m in range(DESIGN_MC):
        if m > 0 and m % 32 == 0:
            _, _, br = budget()
            if br:
                design_stopped = True
                design_stop = list(br)
                break
        x = rng.integers(0, Q, size=N)
        dd = rng.choice(Q, size=N, p=pmf)
        y = (x + dd) % Q
        high = (x >> 5).astype(np.int64)
        low = (x & 31).astype(np.int64)
        bob = y.astype(np.int64)
        mtr1 = probs_to_symbol_metric(build_p1_metrics(bob[None, :], p1)[0],
                                      provenance=Provenance.PRIOR_ONLY)
        r1 = sc_decode(mtr1.logp, field=field, alpha=ALPHA, known_positions=allpos,
                       known_values=polar_transform(high, field=field, alpha=ALPHA))
        pr = np.exp(r1.decision_metrics)
        with np.errstate(divide="ignore"):
            lg = np.log2(pr, out=np.zeros_like(pr), where=pr > 0)
        H1 += -(np.where(pr > 0, pr * lg, 0.0)).sum(axis=1)
        mtr2 = probs_to_symbol_metric(gather_p2_metrics(bob[None, :], high[None, :], p2)[0],
                                      provenance=Provenance.ORACLE_CONDITIONED)
        r2 = sc_decode(mtr2.logp, field=field, alpha=ALPHA, known_positions=allpos,
                       known_values=polar_transform(low, field=field, alpha=ALPHA))
        pr = np.exp(r2.decision_metrics)
        with np.errstate(divide="ignore"):
            lg = np.log2(pr, out=np.zeros_like(pr), where=pr > 0)
        H2 += -(np.where(pr > 0, pr * lg, 0.0)).sum(axis=1)
        mdone += 1
    if mdone:
        H1 /= mdone
        H2 /= mdone
    design_complete = (mdone == DESIGN_MC) and (not design_stopped)
    log.append("A3 MC genie design samples=%d/%d complete=%s wall=%.3f"
               % (mdone, DESIGN_MC, design_complete, time.perf_counter() - T0))

    cfgs = []
    masks_list = []
    # FROZEN single-factor point (DP-N2 TASK_PACKET §3): k1=10 fixed; k2=550 single, no fallback point; disclosed=5*(10+550)=2800 bits frozen, NOT via f formula.
    # ORIG predecessor formula retained (not executed): D=round(f*HN); kt=round(f*HN/5); k1=round(kt*319/6811); k2=round(kt*6492/6811)
    # disclosed bits govern; tag 64bit EXCLUDED from f (kdb=disclosed+64 in-run); A2 not run.
    for k2 in K2_GRID:
        pt = K2_POINTS[k2]
        k1 = K1_FROZEN
        kt = k1 + k2
        D = pt["disclosed"]
        # ORIG A2 line retained (not executed, A2 not run per point): masks, Deff, guard = a2_masks(D)
        if False:  # A2 design/measurement skipped; retain ORIG call for byte-diff traceability
            masks, Deff, guard = a2_masks(D)
        masks = np.ones((R, N), dtype=np.uint8)  # placeholder; A2 not run, not used
        Deff = None
        guard = []
        masks_list.append(masks)
        cfgs.append({"f_target": pt["f_book"], "f_label": pt["label"], "k2": k2,
                     "D_planned": D, "D_disclosed_a2": Deff,
                     "f_actual_a2": None, "k_total": kt, "k1": k1, "k2": k2,
                     "bits_a3_disclosed": 5 * (k1 + k2),
                     "f_actual_a3": 5 * (k1 + k2) / HN,
                     "info_per_plane_a2": None,
                     "a2_guard_swaps": guard,
                     "a2_status": "not_run"})
    # C1 reverse-Shannon control: only the H2 ordering direction changes; rows and budget are shared.
    CAND_DEF = {
        "candidate_id": CAND_ID,
        "blocked": False,
        "rule": "best_k(H2,550) = sorted(stable_argsort(H2)[:550])",
        "fn": "probe-local best_k(Hvec,k)",
        "semantics": "select the 550 lowest row Shannon entropies H2; stable ascending sort breaks ties by ascending original index",
        "sources": "same 128 ORACLE_CONDITIONED MC design rows and same H2 vector as BASE; no new inputs or decoder calls",
        "declaration": "BASE=worst_k(H2,550), CAND=best_k(H2,550); both are 550-element sets from identical design rows and have the same disclosure budget",
    }
    d1_shared = None
    d2_base = None
    d2_cand = None
    if design_complete:
        # FROZEN (single-factor): d1=worst_k(H1,10) shared; BASE d2=worst_k(H2,550) (same formula family as k2-dose-ramp L250);
        # CAND C1 d2=best_k(H2,550) (ascending stable H2; same rows and budget).
        d1_shared = worst_k(H1, K1_FROZEN)
        d2_base = worst_k(H2, K2_SINGLE)
        d2_cand = best_k(H2, K2_SINGLE)
        for c in cfgs:
            c["d1"] = d1_shared
            c["d2_base"] = d2_base
            c["d2"] = d2_base  # BASE governs the d2 key; CAND arm uses c["d2_cand"]
            c["d2_cand"] = d2_cand

    # DESIGN-STAGE mandatory C1 overlap gate (pre-measurement): BASE vs CAND d2 overlap.
    # Gate: identical (predecessor logic inter==k and union==k) OR overlap>=495/550 -> non_discriminating stop before measurement.
    OVERLAP_NONDISCRIMINATING_MIN = 495
    d2_overlap = {"d2_overlap_count": None, "jaccard": None, "identical": None,
                  "gate_min": OVERLAP_NONDISCRIMINATING_MIN,
                  "note": "design incomplete; overlap not computable"}
    premeasurement_stop = None
    if design_complete and d2_base is not None and d2_cand is not None:
        sb = set(int(v) for v in np.asarray(d2_base).ravel().tolist())
        sc = set(int(v) for v in np.asarray(d2_cand).ravel().tolist())
        inter = len(sb & sc)
        union = len(sb | sc)
        ident = bool(inter == K2_SINGLE and union == K2_SINGLE)
        d2_overlap = {"d2_overlap_count": inter, "jaccard": (inter / union if union else None),
                      "identical": ident, "gate_min": OVERLAP_NONDISCRIMINATING_MIN,
                      "note": "design-stage readout before measurement"}
        if ident or inter >= OVERLAP_NONDISCRIMINATING_MIN:
            premeasurement_stop = "non_discriminating"

    rows = []
    records = []
    op_total = {a: dict.fromkeys(OUT_KEYS, 0) for a in ARMS2}
    or_total = {a: dict.fromkeys(OUT_KEYS, 0) for a in ARMS2}
    div_defined = 0
    div_true = 0
    a3_kdb = set()
    stopped = False
    stop_reasons = list(design_stop)
    completed_cells = 0
    expected_cells = len(ARMS2) * len(SEEDS)

    if design_complete and premeasurement_stop is None:
        for fi, c in enumerate(cfgs):
            if stopped:
                break
            masks = masks_list[fi]
            for si, seed in enumerate(SEEDS):
                if stopped:
                    break
                nb = 0
                cell = {a: {"nf_a3": 0, "opc": dict.fromkeys(OUT_KEYS, 0),
                            "orc": dict.fromkeys(OUT_KEYS, 0)} for a in ARMS2}
                for b in range(BLOCKS):
                    _, _, br = budget()
                    if br:
                        stopped = True
                        stop_reasons.extend(br)
                        break
                    rngb = np.random.default_rng([seed, b])
                    x = rngb.integers(0, Q, size=N)
                    dd = rngb.choice(Q, size=N, p=pmf)
                    y = (x + dd) % Q
                    if False:  # A2 not run per point; ORIG A2 lines retained (not executed)
                        src_all = ((x[None, :] >> np.arange(R)[:, None]) & 1).astype(np.int8)
                        u_true = np.stack([pc.polar_encode(src_all[i], NLOG) for i in range(R)])
                        fv = np.zeros((R, N), dtype=np.uint8)
                        nd = masks == 0
                        fv[nd] = u_true[nd]
                        logp_sym = logpmf[(y[:, None] - np.arange(Q)[None, :]) % Q]
                        if not a2_chain("sc", logp_sym, masks, fv, u_true):
                            pass
                        if not a2_chain("scl", logp_sym, masks, fv, u_true):
                            pass
                    high = (x >> 5).astype(np.int64)
                    low = (x & 31).astype(np.int64)
                    bob = y.astype(np.int64)
                    bidx = fi * 100000 + si * 1000 + b
                    for arm_id in ARMS2:
                        d2 = c["d2_base"] if arm_id == "BASE" else c["d2_cand"]
                        res = tl.run_two_layer_block(bidx, high, low, bob, field=field,
                                                     p1_table=p1, p2_table=p2,
                                                     d1=c["d1"], d2=d2, n=N,
                                                     k1=c["k1"], k2=c["k2"],
                                                     toeplitz_master=tl.FROZEN_TOEPLITZ_MASTER)
                        op = res.operational
                        oq = res.oracle
                        cell[arm_id]["opc"][op.outcome] += 1
                        op_total[arm_id][op.outcome] += 1
                        cell[arm_id]["orc"][oq.outcome] += 1
                        or_total[arm_id][oq.outcome] += 1
                        a3_kdb.add(int(op.key_dependent_bits))
                        if op.outcome == "undetected" or oq.outcome == "undetected":
                            stopped = True
                            stop_reasons.append("undetected>0")
                            break
                        if not op.label_match:
                            cell[arm_id]["nf_a3"] += 1
                        if res.oracle_candidate_divergence is not None:
                            div_defined += 1
                            if res.oracle_candidate_divergence:
                                div_true += 1
                        records.append({"seed": seed, "block": b, "arm": arm_id, "k2": c["k2"], "f_label": c["f_label"],
                                        "operational": {"label_match": bool(op.label_match), "tag_invoked": bool(op.tag_invoked), "outcome": op.outcome},
                                        "oracle": {"label_match": bool(oq.label_match), "tag_invoked": bool(oq.tag_invoked), "outcome": oq.outcome}})
                    if stopped:
                        break
                    nb += 1
                if stopped:
                    break
                if nb == 0:
                    break
                for arm_id in ARMS2:
                    cc = cell[arm_id]
                    n_exact_or = cc["orc"]["exact"]
                    rows.append({"arm": arm_id, "f_target": c["f_target"], "f_label": c["f_label"], "k2": c["k2"], "seed": seed, "blocks": nb,
                                 "a2_sc_frame_errors": None, "a2_scl8_frame_errors": None,
                                 "a3_op_frame_errors": cc["nf_a3"],
                                 "a2_sc_fer": None, "a2_scl8_fer": None,
                                 "a3_op_fer": cc["nf_a3"] / nb,
                                 "a3_oracle_exact": n_exact_or,
                                 "a3_oracle_exact_rate": n_exact_or / nb,
                                 "a3_op_outcomes": cc["opc"], "a3_oracle_outcomes": cc["orc"],
                                 "a2_status": "not_run",
                                 "delta_a3_minus_a2_sc": None,
                                 "delta_a3_minus_a2_scl8": None})
                    completed_cells += 1
                log.append("cell %s k2=%d seed=%d blocks=%d arms=BASE+CAND A2=not_run fer_a3_op_BASE=%.4f fer_a3_op_CAND=%.4f exact_or_BASE=%d exact_or_CAND=%d"
                           % (c["f_label"], c["k2"], seed, nb, cell["BASE"]["nf_a3"] / nb,
                              cell["CAND"]["nf_a3"] / nb, cell["BASE"]["orc"]["exact"], cell["CAND"]["orc"]["exact"]))

    # PAIRED discordance (DP-N4 readout): per (seed,block) compare BASE vs CAND oracle outcomes.
    # Only complete pairs (both arms recorded) count; the two mismatch directions counted separately.
    paired_oracle = {}
    for r in records:
        paired_oracle.setdefault((r["seed"], r["block"]), {})[r["arm"]] = r["oracle"]["outcome"]
    paired_per_seed = {}
    for s in SEEDS:
        b_only = 0
        c_only = 0
        npair = 0
        for b in range(BLOCKS):
            pair = paired_oracle.get((s, b), {})
            if "BASE" not in pair or "CAND" not in pair:
                continue
            npair += 1
            ob = (pair["BASE"] == "exact")
            oc = (pair["CAND"] == "exact")
            if ob and not oc:
                b_only += 1
            if oc and not ob:
                c_only += 1
        paired_per_seed[str(s)] = {"pairs": npair, "base_only_exact": b_only, "cand_only_exact": c_only}
    paired_total = {"pairs": sum(v["pairs"] for v in paired_per_seed.values()),
                    "base_only_exact": sum(v["base_only_exact"] for v in paired_per_seed.values()),
                    "cand_only_exact": sum(v["cand_only_exact"] for v in paired_per_seed.values())}

    wall, rss, br = budget()
    if br:
        stopped = True
        stop_reasons.extend(br)
    stop_reasons = sorted(set(stop_reasons))
    if premeasurement_stop == "non_discriminating":
        status = "non_discriminating"
    elif stopped or (not design_complete) or (premeasurement_stop is not None) or completed_cells < expected_cells:
        status = "incomplete"
    else:
        status = "ok"
    within = bool(status in ("ok", "non_discriminating") and wall <= WALL_LIMIT_S
                  and (rss is None or rss <= RSS_LIMIT))

    by_arm = {}
    for arm_id in ARMS2:
        rs = [r for r in rows if r["arm"] == arm_id]
        entry = dict(cfgs[0]) if cfgs else {}
        entry.pop("d1", None)
        entry.pop("d2", None)
        entry.pop("d2_base", None)
        entry.pop("d2_cand", None)
        entry["arm"] = arm_id
        entry["construction_id"] = BASE_ID if arm_id == "BASE" else CAND_ID
        entry["d1_len"] = int(d1_shared.size) if d1_shared is not None else None
        entry["d2_len"] = int(K2_SINGLE)
        entry["per_seed"] = rs
        entry["summaries"] = {
            "a2_sc_fer": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
            "a2_scl8_fer": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
            "a3_op_fer": summarize([r["a3_op_fer"] for r in rs]),
            "a3_oracle_exact_rate": summarize([r["a3_oracle_exact_rate"] for r in rs]),
            "delta_a3_minus_a2_sc": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
            "delta_a3_minus_a2_scl8": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
        }
        entry["delta_complete"] = bool(len(rs) == len(SEEDS))
        by_arm[arm_id] = entry

    results = {
        "probe_id": "l2-singlefactor-c1-k550",
        "tier": "X",
        "status": status,
        "probe_runs": reruns + 1,
        "reruns": reruns,
        "within_budget": within,
        "stop_rules_triggered": stop_reasons,
        "prereg": {"path": "workspace/probes/l2-singlefactor-c1-k550/prereg.md",
                   "entries": ["Q", "P", "C"],
                   "note": "Q/P/C recorded verbatim in prereg.md; frozen parameters mirrored structurally under frozen_params; executed command = prereg C entry with interpreter/env mirrored under execution"},
        "frozen_params": {
            "channel": {"name": "F4@q1024", "q": Q,
                        "p_delta0": P_F4["p0"], "p_delta_plus1": P_F4["p1"],
                        "p_delta_minus1": P_F4["pm1"],
                        "residual_mass": P_F4["prest"], "residual_spread_over": Q - 3,
                        "model": "y = (x + delta) mod 1024, x uniform"},
            "H": H, "H_times_N": HN,
            "N": N, "n_log": NLOG, "planes": R,
            "f_convention": "f = disclosed bits / (H * N); 64-bit Toeplitz tag EXCLUDED from f (convention carried from N=256 predecessor for comparability); A3 tag-inclusive leakage also reported via key_dependent_bits",
            "k2_single": K2_SINGLE,
            "k2_point": dict(K2_POINTS[K2_SINGLE]),
            "seeds": list(SEEDS), "blocks_per_seed": BLOCKS,
            "design_seed": DESIGN_SEED, "design_mc_samples": DESIGN_MC,
            "scl_list_size": LIST_SIZE,
            "g2_k1_k2_counts": [G2_K1, G2_K2],
            "a2_split_rule": "not_run (no A2 design/measurement in this probe; A2 summaries not_run)",
            "a3_split_rule": "FROZEN single-factor point: k1=10 fixed, k2=550 single no fallback, disclosed=5*(10+550)=2800 bits (f_book~=2.93441 bookkeeping only, NOT an efficiency point; tag excluded); d1=worst_k(H1,10) shared MC genie; BASE d2=worst_k(H2,550) probe-local; CAND C1 d2=best_k(H2,550) (ascending stable H2, same rows/budget)",
            "construction_ids": {"BASE": BASE_ID, "CAND": CAND_ID},
            "pairing": "per (seed, block): rng=default_rng([seed, block]); draw x=integers(0,1024,N) then delta=choice(1024,N,p=pmf); y=(x+delta)%1024; identical (x,y) reused across BASE/CAND two construction arms and across op/oracle two decoder arms",
            "a3_semantics": "run_two_layer_block operational arm FER = (label_match == False); outcomes exact/verify_failed/decode_failed/undetected/resource_abort counted isolated, undetected never merged into success; oracle arm + candidate divergence report-only; toeplitz_master=%d" % tl.FROZEN_TOEPLITZ_MASTER,
            "budget": {"wall_s": WALL_LIMIT_S, "rss_bytes": RSS_LIMIT,
                       "check": "every block and every 32 design samples; breach -> immediate stop, status incomplete, no tuning"},
            "rerun_policy": "one-shot reruns=0: execution-error rerun NOT allowed; any error -> status execution_error/incomplete with traceback, no retry, no parameter/seed change",
            "deviations_from_plan_A_rows": [
                "N=1024 (plan A2/A3 row: N=2^15) - packet-frozen Tier-X scale-up, same as predecessor",
                "128 blocks single-factor point (2 construction arms x 4 seeds x 16; plan completion: >=1000 blocks) - Tier-X downscale one-shot",
                "single k2=550 point disclosed=2800 bits f_book~=2.93441 bookkeeping only, NOT an efficiency point and NOT a pre-claimed non-floor point: unmeasured interpolation between k2-ramp 400-end (oracle 2/32) and 700-end (oracle 32/32); floor or ceiling landing ends descriptively with no on-the-spot point change or resampling; tag excluded from f - packet froze single-factor construction-ordering test",
                "channel is parametric F4@q1024 (plan: measured-ternary synthetic) - packet froze F4",
                "A3 runs the two-layer GF32 path of the current M2 code (raw GF1024 SC infeasible at q=1024)",
                "64-bit Toeplitz tag excluded from f (convention carried from predecessors for comparability); tag still executed inside A3",
                "A2 not run (no A2 design/measurement; A2 summaries not_run) - packet froze cost saving",
                "non-claim Tier-X: no pass/fail threshold, no significance wording, no Wilson interval, no scoreboard row, no R2 sizing input"],
        },
        "execution": {"interpreter": INTERPRETER, "env": ENV,
                      "invocation": "run.py invoked by the preregistered C command",
                      "python_version": sys.version.split()[0], "numpy_version": np.__version__},
        "design": {"a2_Z0_per_plane": Z0, "a2_selection": "pooled worst-Z-first",
                   "a3_design_samples": mdone,
                   "a3_H1_mean": float(H1.mean()) if mdone else None,
                   "a3_H2_mean": float(H2.mean()) if mdone else None,
                   "joint_table_colsum_max_dev": coldev,
                   "construction_ids": {"BASE": BASE_ID, "CAND": CAND_ID}},
        "d2_overlap": d2_overlap,
        "cand_def": CAND_DEF,
        "paired_oracle_discordance": {"per_seed": paired_per_seed, "total": paired_total,
                                      "note": "descriptive only: per-(seed,block) BASE vs CAND oracle outcome mismatch directions; complete pairs only; no significance wording"},
        "arms": by_arm,
        "records": records,
        "paired_note": "single-factor point: A2 not_run, deltas not_run; identical (x,y) shared across BASE/CAND construction arms; per-arm A3 op/oracle outcomes + per-block records govern; paired oracle discordance two directions (base_only_exact/cand_only_exact) descriptive; L-H3 continued exclusion via label_match/tag_invoked/outcome",
        "a3_outcomes_operational_total": op_total,
        "a3_outcomes_oracle_total": or_total,
        "a3_oracle_candidate_divergence": {"defined": div_defined, "true": div_true,
                                            "note": "report-only, no threshold"},
        "a3_key_dependent_bits_observed": sorted(a3_kdb),
        "cells": {"expected": expected_cells, "completed": completed_cells},
        "wall_s": wall,
        "peak_rss_bytes": rss,
        "run_log": log,
        "claims": "Tier-X non-claim planning evidence only: no threshold, no significance/better-than-baseline/construction-invalid/prior-attribution wording, no pass/fail verdict, no discriminating-separation A/B ruling, no auto-continuation list, no candidate/accepted token, no attempt accounting, no real/artifact data, no R2 sizing input, writes only under workspace/probes/l2-singlefactor-c1-k550/; status non_discriminating = BASE/CAND d2 identical or overlap>=495/550, pre-measurement stop, one run one record; both arms failing together must not be attributed to L-H1 alone",
    }
    return results

if __name__ == "__main__":
    try:
        out = main()
        with open(OUT, "w") as fh:
            json.dump(out, fh, indent=2)
        print("WROTE", OUT)
        print(json.dumps({k: out[k] for k in ("status", "within_budget", "probe_runs",
                                              "reruns", "cells", "wall_s",
                                              "peak_rss_bytes", "stop_rules_triggered")}, indent=2))
        print("d2_overlap:", json.dumps(out["d2_overlap"], indent=2))
        print("cand_def:", json.dumps(out["cand_def"], indent=2))
        print("paired_oracle_discordance total:", json.dumps(out["paired_oracle_discordance"]["total"]))
        print("paired_oracle_discordance per_seed:", json.dumps(out["paired_oracle_discordance"]["per_seed"]))
        for arm_id in sorted(out["arms"]):
            s = out["arms"][arm_id]["summaries"]

            def m(key):
                v = s[key]["mean"]
                return float(v) if v is not None else float("nan")
            print("arm=%s n=%d  FER: A2-SC=%.4f A2-SCL8=%.4f A3op=%.4f oracle_exact_rate=%.4f | dSC=%+.4f dSCL8=%+.4f"
                  % (arm_id, s["a3_op_fer"]["n"], m("a2_sc_fer"), m("a2_scl8_fer"),
                     m("a3_op_fer"), m("a3_oracle_exact_rate"), m("delta_a3_minus_a2_sc"), m("delta_a3_minus_a2_scl8")))
        print("A3 outcomes(op):", out["a3_outcomes_operational_total"])
        print("A3 outcomes(or):", out["a3_outcomes_oracle_total"])
    except Exception:
        tb = traceback.format_exc()
        err = {"probe_id": "l2-singlefactor-c1-k550", "tier": "X",
               "status": "execution_error", "probe_runs": 1, "reruns": 0,
               "error_traceback": tb, "wall_s": time.perf_counter() - T0}
        with open(OUT, "w") as fh:
            json.dump(err, fh, indent=2)
        print(tb)
        sys.exit(1)