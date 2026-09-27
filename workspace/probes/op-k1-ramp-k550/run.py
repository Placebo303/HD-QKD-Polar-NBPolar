import os, sys, json, time, traceback
import numpy as np
try:
    import resource
except ImportError:
    resource = None

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
OUT = ROOT + "/workspace/probes/op-k1-ramp-k550/results.json"
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
# op-k1-ramp-k550 Tier-X runner derived from the C1 predecessor (l2-singlefactor-c1-k550/run.py);
# prepared only and not executed until main-thread freeze review (P3) passes.
K1_GRID = (10, 80, 160, 320, 450)
K2_SINGLE = 550
# disclosed=5*(k1+550) bits; f_book=disclosed/HN is BOOKKEEPING ONLY (never an efficiency point);
# k1 is a dose variable, not an efficiency claim; tag EXCLUDED from f (kdb=disclosed+64 in-run).
K1_POINTS = {
    10:  {"label": "k1_010", "disclosed": 2800, "f_book": 2.9344139789},
    80:  {"label": "k1_080", "disclosed": 3150, "f_book": 3.3013},
    160: {"label": "k1_160", "disclosed": 3550, "f_book": 3.7204},
    320: {"label": "k1_320", "disclosed": 4350, "f_book": 4.5589},
    450: {"label": "k1_450", "disclosed": 5000, "f_book": 5.2401},
}
BASE_ID = "L2-BASE-P16-FROZEN"
# Predecessor formula retained as comment (not executed): D=round(f*HN); kt=round(f*HN/5); k1=round(kt*319/6811); k2=round(kt*6492/6811)
SEEDS = (2026092701, 2026092702)
BLOCKS = 16
DESIGN_SEED = 2026092600
DESIGN_MC = 128
LIST_SIZE = 8
G2_K1, G2_K2 = 319, 6492
WALL_LIMIT_S = 600.0
RSS_LIMIT = 1 * 1024 ** 3
OUT_KEYS = ("exact", "undetected", "verify_failed", "decode_failed", "resource_abort")
ARMS = ("BASE",)
INTERPRETER = "/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python"
ENV = {"PYTHONDONTWRITEBYTECODE": "1", "NUMBA_CACHE_DIR": "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/op-k1-ramp-k550/.numba_cache",
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
        reasons.append("wall_s>600")
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
    # FROZEN single-factor k1 dose ramp (DP-K1..K5): k1 in K1_GRID, k2=550 fixed, no fallback point.
    # disclosed bits govern: 5*(k1+550); tag 64bit EXCLUDED from f (kdb=disclosed+64 in-run); A2 not run.
    # k1 is a DOSE VARIABLE, not an efficiency claim; f_book is bookkeeping only.
    for k1 in K1_GRID:
        pt = K1_POINTS[k1]
        k2 = K2_SINGLE
        kt = k1 + k2
        D = pt["disclosed"]
        assert D == 5 * (k1 + k2)
        cfgs.append({"f_target": pt["f_book"], "f_label": pt["label"], "k1": k1, "k2": k2,
                     "D_planned": D, "D_disclosed_a2": None,
                     "f_actual_a2": None, "k_total": kt,
                     "bits_a3_disclosed": 5 * (k1 + k2),
                     "f_actual_a3": 5 * (k1 + k2) / HN,
                     "info_per_plane_a2": None,
                     "a2_guard_swaps": [],
                     "a2_status": "not_run"})
    # d2 = worst_k(H2,550): same rule, design seed and DESIGN_MC as C1 => set-identical to C1 BASE.
    # d1 = worst_k(H1,k1): PER CONFIG (predecessor d1_shared semantics becomes per-config).
    d2_base = None
    if design_complete:
        d2_base = worst_k(H2, K2_SINGLE)
        for c in cfgs:
            c["d1"] = worst_k(H1, c["k1"])
            c["d2"] = d2_base
            c["d1_len"] = int(c["d1"].size)
            c["d2_len"] = int(d2_base.size)

    rows = []
    records = []
    op_total = dict.fromkeys(OUT_KEYS, 0)
    or_total = dict.fromkeys(OUT_KEYS, 0)
    per_point = {int(c["k1"]): {"operational": dict.fromkeys(OUT_KEYS, 0),
                                "oracle": dict.fromkeys(OUT_KEYS, 0),
                                "disclosed_bits": c["D_planned"],
                                "key_dependent_bits": set(),
                                "blocks": 0, "seeds": 0} for c in cfgs}
    div_defined = 0
    div_true = 0
    stopped = False
    stop_reasons = list(design_stop)
    completed_cells = 0
    expected_cells = len(ARMS) * len(SEEDS) * len(K1_GRID)

    if design_complete:
        for fi, c in enumerate(cfgs):
            if stopped:
                break
            for si, seed in enumerate(SEEDS):
                if stopped:
                    break
                nb = 0
                cell = {"opc": dict.fromkeys(OUT_KEYS, 0), "orc": dict.fromkeys(OUT_KEYS, 0),
                        "nf_a3": 0}
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
                    cell["orc"][oq.outcome] += 1
                    or_total[oq.outcome] += 1
                    pp = per_point[int(c["k1"])]
                    pp["operational"][op.outcome] += 1
                    pp["oracle"][oq.outcome] += 1
                    pp["key_dependent_bits"].add(int(op.key_dependent_bits))
                    pp["blocks"] += 1
                    if op.outcome == "undetected" or oq.outcome == "undetected":
                        stopped = True
                        stop_reasons.append("undetected")
                        break
                    if not op.label_match:
                        cell["nf_a3"] += 1
                    if res.oracle_candidate_divergence is not None:
                        div_defined += 1
                        if res.oracle_candidate_divergence:
                            div_true += 1
                    records.append({"seed": seed, "block": b, "k1": c["k1"], "k2": c["k2"],
                                    "f_label": c["f_label"],
                                    "operational": {"label_match": bool(op.label_match), "tag_invoked": bool(op.tag_invoked), "outcome": op.outcome},
                                    "oracle": {"label_match": bool(oq.label_match), "tag_invoked": bool(oq.tag_invoked), "outcome": oq.outcome}})
                    nb += 1
                if stopped:
                    break
                if nb == 0:
                    break
                per_point[int(c["k1"])]["seeds"] += 1
                n_exact_or = cell["orc"]["exact"]
                rows.append({"arm": "BASE", "f_target": c["f_target"], "f_label": c["f_label"],
                             "k1": c["k1"], "k2": c["k2"], "seed": seed, "blocks": nb,
                             "a2_sc_frame_errors": None, "a2_scl8_frame_errors": None,
                             "a3_op_frame_errors": cell["nf_a3"],
                             "a2_sc_fer": None, "a2_scl8_fer": None,
                             "a3_op_fer": cell["nf_a3"] / nb,
                             "a3_oracle_exact": n_exact_or,
                             "a3_oracle_exact_rate": n_exact_or / nb,
                             "a3_op_outcomes": cell["opc"], "a3_oracle_outcomes": cell["orc"],
                             "a2_status": "not_run",
                             "delta_a3_minus_a2_sc": None,
                             "delta_a3_minus_a2_scl8": None})
                completed_cells += 1
                log.append("cell %s k1=%d k2=%d seed=%d blocks=%d arm=BASE A2=not_run fer_a3_op=%.4f exact_or=%d"
                           % (c["f_label"], c["k1"], c["k2"], seed, nb, cell["nf_a3"] / nb,
                              cell["orc"]["exact"]))

    wall, rss, br = budget()
    if br:
        stopped = True
        stop_reasons.extend(br)
    stop_reasons = sorted(set(stop_reasons))
    if stopped or (not design_complete) or completed_cells < expected_cells:
        status = "incomplete"
    else:
        status = "ok"
    within = bool(status == "ok" and wall <= WALL_LIMIT_S
                  and (rss is None or rss <= RSS_LIMIT))

    per_point_out = {}
    for k1v in sorted(per_point):
        pp = per_point[k1v]
        per_point_out[str(k1v)] = {
            "k1": k1v, "k2": K2_SINGLE,
            "disclosed_bits": pp["disclosed_bits"],
            "f_book": K1_POINTS[k1v]["f_book"],
            "dose_semantics": "bookkeeping-only dose diagnostic",
            "blocks": pp["blocks"], "seeds": pp["seeds"],
            "operational_outcomes": dict(pp["operational"]),
            "oracle_outcomes": dict(pp["oracle"]),
            "key_dependent_bits_observed": sorted(pp["key_dependent_bits"]),
        }

    entry = dict(cfgs[0]) if cfgs else {}
    entry.pop("d1", None)
    entry.pop("d2", None)
    entry["arm"] = "BASE"
    entry["construction_id"] = BASE_ID
    entry["d2_len"] = int(d2_base.size) if d2_base is not None else None
    entry["per_cell"] = rows
    entry["summaries"] = {
        "a2_sc_fer": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
        "a2_scl8_fer": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
        "a3_op_fer": summarize([r["a3_op_fer"] for r in rows]),
        "a3_oracle_exact_rate": summarize([r["a3_oracle_exact_rate"] for r in rows]),
        "delta_a3_minus_a2_sc": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
        "delta_a3_minus_a2_scl8": {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0, "note": "not_run"},
    }
    entry["delta_complete"] = bool(len(rows) == len(SEEDS) * len(K1_GRID))
    by_arm = {"BASE": entry}

    results = {
        "probe_id": "op-k1-ramp-k550",
        "tier": "X",
        "status": status,
        "probe_runs": reruns + 1,
        "reruns": reruns,
        "within_budget": within,
        "stop_rules_triggered": stop_reasons,
        "prereg": {"path": "workspace/probes/op-k1-ramp-k550/prereg.md",
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
            "f_convention": "f = disclosed bits / (H * N); 64-bit Toeplitz tag EXCLUDED from f; A3 tag-inclusive leakage also reported via key_dependent_bits; f_book is BOOKKEEPING ONLY",
            "k1_grid": list(K1_GRID),
            "k2_single": K2_SINGLE,
            "k1_points": {str(k): dict(v) for k, v in K1_POINTS.items()},
            "seeds": list(SEEDS), "blocks_per_seed": BLOCKS,
            "blocks_per_point": BLOCKS * len(SEEDS),
            "arms": list(ARMS),
            "design_seed": DESIGN_SEED, "design_mc_samples": DESIGN_MC,
            "scl_list_size": LIST_SIZE,
            "g2_k1_k2_counts": [G2_K1, G2_K2],
            "a2_split_rule": "not_run (no A2 design/measurement in this probe; A2 summaries not_run)",
            "a3_split_rule": "k1 dose ramp: d1=worst_k(H1,k1) PER CONFIG; d2=worst_k(H2,550) shared and set-identical to C1 BASE (same design_seed/DESIGN_MC); disclosed=5*(k1+550); k1 is a dose variable, NOT an efficiency claim",
            "construction_ids": {"BASE": BASE_ID},
            "pairing": "per (seed, block): rng=default_rng([seed, block]); draw x=integers(0,1024,N) then delta=choice(1024,N,p=pmf); y=(x+delta)%1024; identical (x,y) reused across the k1 grid within that block and across op/oracle decoder arms",
            "a3_semantics": "run_two_layer_block operational arm FER = (label_match == False); outcomes exact/verify_failed/decode_failed/undetected/resource_abort counted isolated, undetected never merged into success; oracle arm + candidate divergence report-only; toeplitz_master=%d" % tl.FROZEN_TOEPLITZ_MASTER,
            "budget": {"wall_s": WALL_LIMIT_S, "rss_bytes": RSS_LIMIT,
                       "check": "every block and every 32 design samples; breach -> immediate stop, status incomplete, no tuning"},
            "rerun_policy": "one-shot reruns=0: execution-error rerun NOT allowed; any error -> status execution_error/incomplete with traceback, no retry, no parameter/seed change",
            "gates_removed_vs_C1": ["identical_or_overlap_gte_495_design_gate (not applicable: single arm)"],
            "gates_retained_vs_C1": ["undetected_isolation_stop", "budget_stop"],
            "dose_discipline": "every k1 point is a bookkeeping-only dose diagnostic; no point may be called an efficiency operating point",
            "deviations_from_C1": [
                "K1_FROZEN=10 replaced by K1_GRID=(10,80,160,320,450); k2=550 unchanged",
                "d1_shared replaced by per-config d1=worst_k(H1,k1)",
                "CAND arm and the BASE/CAND d2 overlap design gate removed (single arm)",
                "run seeds 2026092701..2026092702 (2 seeds x 16 blocks = 32 blocks per point); C1 used 4 seeds x 16 blocks",
                "wall limit 600 s (C1: 200 s) to cover 160 blocks over 5 points",
                "design seed 2026092600 and DESIGN_MC=128 UNCHANGED so d2 stays set-identical to C1 BASE"],
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
        "per_point": per_point_out,
        "arms": by_arm,
        "records": records,
        "a3_outcomes_operational_total": op_total,
        "a3_outcomes_oracle_total": or_total,
        "a3_oracle_candidate_divergence": {"defined": div_defined, "true": div_true,
                                            "note": "report-only, no threshold"},
        "cells": {"expected": expected_cells, "completed": completed_cells},
        "wall_s": wall,
        "peak_rss_bytes": rss,
        "run_log": log,
        "claims": "Tier-X non-claim dose diagnostic only: no threshold, no significance wording, no H-label conclusion, no pass/fail verdict, no candidate/accepted token, no attempt accounting, no real/artifact data, no R2 sizing input, writes only under workspace/probes/op-k1-ramp-k550/; every k1 point is a bookkeeping-only dose diagnostic and NOT an efficiency operating point",
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
        print("per_point:", json.dumps(out["per_point"], indent=2))
        s = out["arms"]["BASE"]["summaries"]

        def m(key):
            v = s[key]["mean"]
            return float(v) if v is not None else float("nan")
        print("arm=BASE n=%d  FER: A2-SC=%.4f A2-SCL8=%.4f A3op=%.4f oracle_exact_rate=%.4f | dSC=%+.4f dSCL8=%+.4f"
              % (s["a3_op_fer"]["n"], m("a2_sc_fer"), m("a2_scl8_fer"),
                 m("a3_op_fer"), m("a3_oracle_exact_rate"), m("delta_a3_minus_a2_sc"), m("delta_a3_minus_a2_scl8")))
        print("A3 outcomes(op):", out["a3_outcomes_operational_total"])
        print("A3 outcomes(or):", out["a3_outcomes_oracle_total"])
    except Exception:
        tb = traceback.format_exc()
        err = {"probe_id": "op-k1-ramp-k550", "tier": "X",
               "status": "execution_error", "probe_runs": 1, "reruns": 0,
               "error_traceback": tb, "wall_s": time.perf_counter() - T0}
        with open(OUT, "w") as fh:
            json.dump(err, fh, indent=2)
        print(tb)
        sys.exit(1)
