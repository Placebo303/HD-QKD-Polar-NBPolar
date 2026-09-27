import os, sys, json, time, traceback
import numpy as np
try:
    import resource
except ImportError:
    resource = None

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
PROBE_ID = "op-fix-n1024-alloc"
OUT = ROOT + "/workspace/probes/op-fix-n1024-alloc/results.json"
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
# op-fix-n1024-alloc runner derived from op-peak-refine/run.py + op-n32k-ratio/run.py's
# label-keyed multi-total POINTS architecture (aggregation must be keyed by (total,k1,k2),
# never by k1 alone, since k1 values could in principle repeat across totals).
# DELTA vs predecessors: (1) SIGN FIX -- table[a,b] and Wmat[a,b] corrected from pmf[(a-b)%Q]
#     to pmf[(b-a)%Q] so table[a,b] = P(Bob=b|Alice=a) matches the true generative model
#     y=(x+delta)%Q (see workspace/op-n32k-ratio-packet/FOCUSED_REVIEW.md Part 2 and
#     workspace/probes/op-n32k-ratio/review_scratch/check_table_sign.py); (2) new grid
#     (3 totals x 5 k1 shares = 15 points); (3) new seeds; (4) new output root.
# Everything else (F4 pmf, M2 two-layer GF32 SC/oracle/operational semantics, toeplitz_master,
# worst_k design rule, undetected STOP/isolation, rng scheme, DESIGN_MC=128, design_seed
# 2026092600) inherited unchanged from op-peak-refine.
# disclosed = 5*(k1+k2) = 5*total; f_book = disclosed/(H*N) bookkeeping only (NOT an efficiency
# point), 64-bit Toeplitz tag EXCLUDED from f; kdb = disclosed+64 in-run.
# H*N = 0.9318300074841255*1024 = 954.1939276637445; totals = round(f*HN/5):
#   f1.30 -> 248, f1.60 -> 305, f2.00 -> 382.
# k1 = round(share*total); k2 = total - k1.
POINTS = (
    {"label": "T248_k1_12_k2_236",  "total": 248, "k1": 12,  "k2": 236, "share_target": "0.047", "disclosed": 1240, "f_book": 1.2995261907},
    {"label": "T248_k1_22_k2_226",  "total": 248, "k1": 22,  "k2": 226, "share_target": "0.09",  "disclosed": 1240, "f_book": 1.2995261907},
    {"label": "T248_k1_35_k2_213",  "total": 248, "k1": 35,  "k2": 213, "share_target": "0.14",  "disclosed": 1240, "f_book": 1.2995261907},
    {"label": "T248_k1_50_k2_198",  "total": 248, "k1": 50,  "k2": 198, "share_target": "0.20",  "disclosed": 1240, "f_book": 1.2995261907},
    {"label": "T248_k1_74_k2_174",  "total": 248, "k1": 74,  "k2": 174, "share_target": "0.30",  "disclosed": 1240, "f_book": 1.2995261907},
    {"label": "T305_k1_14_k2_291",  "total": 305, "k1": 14,  "k2": 291, "share_target": "0.047", "disclosed": 1525, "f_book": 1.5982076136},
    {"label": "T305_k1_27_k2_278",  "total": 305, "k1": 27,  "k2": 278, "share_target": "0.09",  "disclosed": 1525, "f_book": 1.5982076136},
    {"label": "T305_k1_43_k2_262",  "total": 305, "k1": 43,  "k2": 262, "share_target": "0.14",  "disclosed": 1525, "f_book": 1.5982076136},
    {"label": "T305_k1_61_k2_244",  "total": 305, "k1": 61,  "k2": 244, "share_target": "0.20",  "disclosed": 1525, "f_book": 1.5982076136},
    {"label": "T305_k1_92_k2_213",  "total": 305, "k1": 92,  "k2": 213, "share_target": "0.30",  "disclosed": 1525, "f_book": 1.5982076136},
    {"label": "T382_k1_18_k2_364",  "total": 382, "k1": 18,  "k2": 364, "share_target": "0.047", "disclosed": 1910, "f_book": 2.0016895357},
    {"label": "T382_k1_34_k2_348",  "total": 382, "k1": 34,  "k2": 348, "share_target": "0.09",  "disclosed": 1910, "f_book": 2.0016895357},
    {"label": "T382_k1_53_k2_329",  "total": 382, "k1": 53,  "k2": 329, "share_target": "0.14",  "disclosed": 1910, "f_book": 2.0016895357},
    {"label": "T382_k1_76_k2_306",  "total": 382, "k1": 76,  "k2": 306, "share_target": "0.20",  "disclosed": 1910, "f_book": 2.0016895357},
    {"label": "T382_k1_115_k2_267", "total": 382, "k1": 115, "k2": 267, "share_target": "0.30",  "disclosed": 1910, "f_book": 2.0016895357},
)
F_TARGETS = {248: 1.30, 305: 1.60, 382: 2.00}
SHARE_VALUES = {"0.047": 0.047, "0.09": 0.09, "0.14": 0.14, "0.20": 0.20, "0.30": 0.30}
BASE_ID = "A3-BASE-D1-WORST-H1-K1-D2-WORST-H2-K2-N1024-SIGNFIX"
SEEDS = (2026092901, 2026092902)
BLOCKS = 16
DESIGN_SEED = 2026092600
DESIGN_MC = 128
LIST_SIZE = 8
G2_K1, G2_K2 = 319, 6492
WALL_LIMIT_S = 1200.0
RSS_LIMIT = 1 * 1024 ** 3
OUT_KEYS = ("exact", "undetected", "verify_failed", "decode_failed", "resource_abort")
ARMS = ("BASE",)
INTERPRETER = "/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python"
ENV = {"PYTHONDONTWRITEBYTECODE": "1", "NUMBA_CACHE_DIR": "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-fix-n1024-alloc/.numba_cache",
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
        reasons.append("wall_s>1200")
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
    # SIGN FIX: table[a,b] = P(Bob=b|Alice=a) = pmf[(b-a)%Q] (true generative model y=(x+delta)%Q).
    # Predecessors (op-peak-refine, op-n32k-ratio) used pmf[(a-b)%Q] -- the mirror channel.
    table = pmf[(np.arange(Q)[None, :] - np.arange(Q)[:, None]) % Q]
    coldev = float(np.abs(table.sum(axis=0) - 1.0).max())
    p1, p2 = tl.layer_metric_tables(table)
    field = make_gf32()
    EJBs = [natural_EJB(i) for i in range(R)]

    Zall = np.empty((R, N), dtype=np.float64)
    Z0 = []
    # SIGN FIX (same correction applied to the Bhattacharyya/Z construction input).
    Wmat = pmf[(np.arange(Q)[None, :] - np.arange(Q)[:, None]) % Q]
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
    print(log[-1], flush=True)

    cfgs = []
    masks_list = []
    # FROZEN grid: three fixed totals (f_book 1.30/1.60/2.00) x five k1 shares; k2 = total - k1;
    # d1/d2 = worst_k per point; disclosed = 5*(k1+k2) governs arithmetic (tag 64bit EXCLUDED
    # from f; kdb = disclosed+64 in-run); A2 not run.
    for pt in POINTS:
        k1 = pt["k1"]
        k2 = pt["k2"]
        kt = k1 + k2
        # grid-consistency check against the frozen derivation rule (guards transcription typos only)
        assert kt == pt["total"] == int(round(F_TARGETS[pt["total"]] * HN / 5)), pt
        assert k1 == int(round(SHARE_VALUES[pt["share_target"]] * pt["total"])), pt
        assert pt["disclosed"] == 5 * kt and abs(pt["f_book"] - 5 * kt / HN) < 1e-9, pt
        D = pt["disclosed"]
        masks = np.ones((R, N), dtype=np.uint8)  # placeholder; A2 not run, not used
        Deff = None
        masks_list.append(masks)
        cfgs.append({"f_target": pt["f_book"], "f_label": pt["label"], "total": pt["total"],
                     "f_book_target": F_TARGETS[pt["total"]], "share_target": pt["share_target"],
                     "k1_share_actual": k1 / kt,
                     "D_planned": D, "D_disclosed_a2": Deff,
                     "f_actual_a2": None, "k_total": kt, "k1": k1, "k2": k2,
                     "bits_a3_disclosed": 5 * (k1 + k2),
                     "f_actual_a3": 5 * (k1 + k2) / HN,
                     "info_per_plane_a2": None,
                     "a2_guard_swaps": [],
                     "a2_status": "not_run"})
    d2_base = None
    if design_complete:
        # FROZEN: d1 = worst_k(H1, k1) and d2 = worst_k(H2, k2) recomputed per point from the single design (H1, H2) vectors.
        d2_base = None  # per-point d2 replaces the shared d2 (k2 varies per point)
        for c in cfgs:
            c["d1"] = worst_k(H1, c["k1"])
            c["d2"] = worst_k(H2, c["k2"])

    rows = []
    records = []
    op_total = dict.fromkeys(OUT_KEYS, 0)
    or_total = dict.fromkeys(OUT_KEYS, 0)
    per_label_op = {pt["label"]: dict.fromkeys(OUT_KEYS, 0) for pt in POINTS}
    per_label_or = {pt["label"]: dict.fromkeys(OUT_KEYS, 0) for pt in POINTS}
    assert len(per_label_op) == len(POINTS), "point labels must be unique"
    div_defined = 0
    div_true = 0
    a3_kdb = set()
    stopped = False
    stop_reasons = list(design_stop)
    completed_cells = 0
    expected_cells = len(ARMS) * len(SEEDS) * len(POINTS)

    if design_complete:
        for fi, c in enumerate(cfgs):
            if stopped:
                break
            for si, seed in enumerate(SEEDS):
                if stopped:
                    break
                nb = 0
                cell = {"nf_a3": 0, "opc": dict.fromkeys(OUT_KEYS, 0),
                        "orc": dict.fromkeys(OUT_KEYS, 0)}
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
                    high = (x >> 5).astype(np.int64)
                    low = (x & 31).astype(np.int64)
                    bob = y.astype(np.int64)
                    bidx = fi * 100000 + si * 1000 + b
                    res = tl.run_two_layer_block(bidx, high, low, bob, field=field,
                                                 p1_table=p1, p2_table=p2,
                                                 d1=c["d1"], d2=c["d2"], n=N,
                                                 k1=c["k1"], k2=c["k2"],
                                                 toeplitz_master=tl.FROZEN_TOEPLITZ_MASTER)
                    op = res.operational
                    oq = res.oracle
                    cell["opc"][op.outcome] += 1
                    op_total[op.outcome] += 1
                    per_label_op[c["f_label"]][op.outcome] += 1
                    cell["orc"][oq.outcome] += 1
                    or_total[oq.outcome] += 1
                    per_label_or[c["f_label"]][oq.outcome] += 1
                    a3_kdb.add(int(op.key_dependent_bits))
                    if op.outcome == "undetected" or oq.outcome == "undetected":
                        stopped = True
                        stop_reasons.append("undetected>0")
                        break
                    if not op.label_match:
                        cell["nf_a3"] += 1
                    if res.oracle_candidate_divergence is not None:
                        div_defined += 1
                        if res.oracle_candidate_divergence:
                            div_true += 1
                    records.append({"seed": seed, "block": b, "total": c["total"], "k1": c["k1"], "k2": c["k2"], "f_label": c["f_label"],
                                    "block_wall_s": float(res.block_wall_s),
                                    "operational": {"label_match": bool(op.label_match), "tag_invoked": bool(op.tag_invoked), "outcome": op.outcome},
                                    "oracle": {"label_match": bool(oq.label_match), "tag_invoked": bool(oq.tag_invoked), "outcome": oq.outcome}})
                    nb += 1
                if stopped:
                    break
                if nb == 0:
                    break
                rows.append({"f_target": c["f_target"], "f_label": c["f_label"], "total": c["total"], "k1": c["k1"], "k2": c["k2"],
                             "seed": seed, "blocks": nb,
                             "a2_sc_frame_errors": None, "a2_scl8_frame_errors": None,
                             "a3_op_frame_errors": cell["nf_a3"],
                             "a2_sc_fer": None, "a2_scl8_fer": None,
                             "a3_op_fer": cell["nf_a3"] / nb,
                             "a3_oracle_exact": cell["orc"]["exact"],
                             "a3_oracle_exact_rate": cell["orc"]["exact"] / nb,
                             "a3_op_outcomes": dict(cell["opc"]), "a3_oracle_outcomes": dict(cell["orc"]),
                             "a2_status": "not_run",
                             "delta_a3_minus_a2_sc": None,
                             "delta_a3_minus_a2_scl8": None})
                completed_cells += 1
                log.append("cell %s k1=%d k2=%d seed=%d blocks=%d A2=not_run fer_a3_op=%.4f op_exact=%d oracle_exact=%d"
                           % (c["f_label"], c["k1"], c["k2"], seed, nb,
                              cell["nf_a3"] / nb, cell["opc"]["exact"], cell["orc"]["exact"]))
                print(log[-1] + " wall=%.1f" % (time.perf_counter() - T0), flush=True)

    wall, rss, br = budget()
    if br:
        stopped = True
        stop_reasons.extend(br)
    stop_reasons = sorted(set(stop_reasons))
    if stopped or (not design_complete) or completed_cells < expected_cells:
        status = "incomplete"
    else:
        status = "ok"
    within = bool(status == "ok" and wall <= WALL_LIMIT_S and (rss is None or rss <= RSS_LIMIT))

    points = []
    for c in cfgs:
        rs = [r for r in rows if r["f_label"] == c["f_label"]]  # aggregate by unique point label, never by k1 alone
        entry = dict(c)
        entry.pop("d1", None)
        entry.pop("d2", None)
        entry["construction_id"] = BASE_ID
        entry["d1_len"] = int(c["k1"])
        entry["d2_len"] = int(c["k2"])
        entry["per_seed"] = rs
        entry["operational_totals"] = dict(per_label_op[c["f_label"]])
        entry["oracle_totals"] = dict(per_label_or[c["f_label"]])
        entry["summaries"] = {
            "a3_op_fer": summarize([r["a3_op_fer"] for r in rs]),
            "a3_oracle_exact_rate": summarize([r["a3_oracle_exact_rate"] for r in rs]),
            "a2_sc_fer": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
            "a2_scl8_fer": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
        }
        entry["delta_complete"] = bool(len(rs) == len(SEEDS))
        points.append(entry)

    results = {
        "probe_id": PROBE_ID,
        "tier": "X",
        "status": status,
        "probe_runs": reruns + 1,
        "reruns": reruns,
        "within_budget": within,
        "stop_rules_triggered": stop_reasons,
        "prereg": {"path": "workspace/probes/op-fix-n1024-alloc/prereg.md",
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
            "f_convention": "f = disclosed bits / (H * N); 64-bit Toeplitz tag EXCLUDED from f (convention carried from predecessors for comparability); A3 tag-inclusive leakage also reported via key_dependent_bits",
            "sign_fix": "table[a,b] and Wmat[a,b] corrected to pmf[(b-a)%Q] = P(Bob=b|Alice=a) matching y=(x+delta)%Q; predecessors op-peak-refine/op-n32k-ratio used pmf[(a-b)%Q] (mirror channel) -- see workspace/op-n32k-ratio-packet/FOCUSED_REVIEW.md Part 2",
            "single_factor": "k1 SHARE of a fixed total at N=1024 (sign-corrected table/Wmat): totals %s (f_book targets 1.30/1.60/2.00) x k1 shares (0.047,0.09,0.14,0.20,0.30); k2 = total - k1; d1 = worst_k(H1,k1) and d2 = worst_k(H2,k2) per point from the same frozen family rule; %d points" % (sorted(F_TARGETS), len(POINTS)),
            "points_grid": [dict(p) for p in POINTS],
            "f_targets_by_total": {str(k): v for k, v in F_TARGETS.items()},
            "share_values": dict(SHARE_VALUES),
            "seeds": list(SEEDS), "blocks_per_seed": BLOCKS,
            "blocks_per_point": len(SEEDS) * BLOCKS,
            "design_seed": DESIGN_SEED, "design_mc_samples": DESIGN_MC,
            "scl_list_size": LIST_SIZE,
            "g2_k1_k2_counts": [G2_K1, G2_K2],
            "a2_split_rule": "not_run (no A2 design/measurement in this probe; A2 summaries not_run)",
            "a3_split_rule": "FROZEN grid: labels %s; disclosed = 5*(k1+k2) bits per total (1240/1525/1910) (f_book bookkeeping only, NOT efficiency points; tag excluded); d1=worst_k(H1,k1) per point; d2=worst_k(H2,k2) per point; one N=1024 H1/H2 design (design_seed=%d, DESIGN_MC=%d, inherited unchanged from op-peak-refine)" % ([p["label"] for p in POINTS], DESIGN_SEED, DESIGN_MC),
            "construction_ids": {"BASE": BASE_ID},
            "pairing": "per (seed, block): rng=default_rng([seed, block]); draw x=integers(0,1024,N) then delta=choice(1024,N,p=pmf); y=(x+delta)%1024; identical (x,y) reused across all 15 grid points via the same (seed,block) index",
            "a3_semantics": "run_two_layer_block operational arm FER = (label_match == False); outcomes exact/verify_failed/decode_failed/undetected/resource_abort counted isolated, undetected never merged into success; oracle arm + candidate divergence report-only; toeplitz_master=%d" % tl.FROZEN_TOEPLITZ_MASTER,
            "budget": {"wall_s": WALL_LIMIT_S, "rss_bytes": RSS_LIMIT,
                       "check": "every block and every 32 design samples; breach -> immediate stop, status incomplete, no tuning"},
            "rerun_policy": "one-shot reruns=0; only an implementation-defect death before any measurement may be relaunched once after a fix (error record kept as results.execution_error_attempt1.json); no parameter/seed change",
            "deviations_from_plan_A_rows": [
                "N=1024 (plan A2/A3 row: N=2^15) - packet-frozen Tier-X scale-up, same as op-peak-refine",
                "480 blocks total (15 points x 2 seeds x 16; plan completion: >=1000 blocks) - Tier-X downscale one-shot",
                "grid %s; every point is a bookkeeping-only allocation diagnostic and NOT an efficiency point; no point may be described as a usable operating point" % ([p["label"] for p in POINTS],),
                "channel is parametric F4@q1024 (plan: measured-ternary synthetic) - predecessor froze F4",
                "A3 runs the two-layer GF32 path of the current M2 code (raw GF1024 SC infeasible at q=1024)",
                "64-bit Toeplitz tag excluded from f (convention carried from predecessors for comparability); tag still executed inside A3",
                "A2 not run (no A2 design/measurement; A2 summaries not_run) - predecessor froze cost saving",
                "table/Wmat sign fix vs op-peak-refine/op-n32k-ratio (see sign_fix field) -- the only semantic delta besides grid/seeds/output-root",
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
                   "construction_ids": {"BASE": BASE_ID}},
        "points": points,
        "records": records,
        "per_label_note": "outcomes are counted per point label (total,k1,k2) and globally; undetected is isolated and never merged into success; both arms failing together must not be attributed to L-H1 alone",
        "a3_outcomes_operational_total": dict(op_total),
        "a3_outcomes_oracle_total": dict(or_total),
        "a3_oracle_candidate_divergence": {"defined": div_defined, "true": div_true,
                                            "note": "report-only, no threshold"},
        "a3_key_dependent_bits_observed": sorted(a3_kdb),
        "cells": {"expected": expected_cells, "completed": completed_cells},
        "wall_s": wall,
        "peak_rss_bytes": rss,
        "run_log": log,
        "claims": "Tier-X non-claim planning evidence only: no threshold, no significance/better-than-baseline/construction-invalid/prior-attribution wording, no pass/fail verdict, no discriminating-separation A/B ruling, no auto-continuation list, no candidate/accepted token, no attempt accounting, no real/artifact data, no R2 sizing input, no efficiency/operating-point claim for any point, writes only under workspace/probes/op-fix-n1024-alloc/",
    }
    return results

if __name__ == "__main__":
    try:
        out = main()
        with open(OUT, "w") as fh:
            json.dump(out, fh, indent=2)
        print("WROTE", OUT)
        print("STATUS", out["status"], "WITHIN", out["within_budget"],
              "CELLS", out["cells"], "WALL", round(out["wall_s"], 3))
    except Exception:
        err = {
            "probe_id": PROBE_ID,
            "tier": "X",
            "status": "execution_error",
            "probe_runs": 1,
            "reruns": 0,
            "error_traceback": traceback.format_exc(),
            "wall_s": time.perf_counter() - T0,
        }
        try:
            with open(OUT, "w") as fh:
                json.dump(err, fh, indent=2)
        except Exception:
            pass
        print("ERROR wrote", OUT)
        traceback.print_exc()
        sys.exit(1)
