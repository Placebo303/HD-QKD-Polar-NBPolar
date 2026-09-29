"""Tier-X probe eff-sweep-native. Reuses scl-gate-t3/run.py helpers (imported, unmodified)."""
import json, os, sys, time, subprocess, statistics, math
import numpy as np
T3 = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/scl-gate-t3"
ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
PD = ROOT + "/workspace/probes/eff-sweep-native"
sys.path.insert(0, T3)
import run as t3  # scl-gate-t3 helpers
from comparison_bench.formal_ir.nbpolar import scl_joint, scl_joint_native
from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
scl_joint_native._default_threads = lambda: 4
scl_joint.scl_joint_decode = scl_joint_native.scl_joint_decode_native  # patch in-process only

SEEDS = (2026093010, 2026093011)
SHARE = 0.0469
GRID = [(16, f) for f in (1.15, 1.18, 1.20, 1.22, 1.25)] + [(32, f) for f in (1.15, 1.18, 1.20)]
SC_F = (1.20, 1.25)
BPS = int(os.environ.get("BLOCKS_PER_SEED", "16"))

def bin_cpu():
    o = subprocess.run("ps -eo pid,pcpu,etime,cmd | grep r2_binary_baseline | grep -v grep", shell=True, capture_output=True, text=True).stdout.strip()
    return o
log = open(PD + "/cpu_check_log.txt", "a")
last_chk = [0.0]
def cpu_check(force=False):
    if force or time.time() - last_chk[0] > 1200:
        last_chk[0] = time.time()
        line = time.strftime("%H:%M:%S ") + (bin_cpu() or "NO_BINARY_PROCESS")
        log.write(line + "\n"); log.flush(); print(line, flush=True)

def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return [max(0, c-h), min(1, c+h)]

def point(f, H):
    total = round(f * H * t3.N / 5)
    k1 = round(SHARE * total)
    return total, k1, total - k1

def main(mode):
    d = json.load(open(T3 + "/design.json"))
    H1 = np.asarray(d["H1"]); H2 = np.asarray(d["H2"]); H = d["H"]; HN = H * t3.N
    field = make_gf32()
    _, _, _, p1, p2, _ = t3.build_tables()
    pmf_sample = t3.sample_pmf(t3.Q)
    if mode == "smoke":
        total, k1, k2 = point(1.20, H)
        d1 = t3.worst_k(H1, k1); d2 = t3.worst_k(H2, k2)
        x, high, low, bob = t3.gen_block(1, 0, pmf_sample)
        t = time.perf_counter()
        r = t3.eval_scl_joint_block(999999, high, low, bob, field, p1, p2, d1, d2, 16)
        print("SMOKE L16 f1.20", r, "wall", time.perf_counter() - t)
        t = time.perf_counter()
        r = t3.eval_scl_joint_block(999999, high, low, bob, field, p1, p2, d1, d2, 32)
        print("SMOKE L32 f1.20", r, "wall", time.perf_counter() - t)
        return
    out_path = PD + "/results.json"
    assert not os.path.exists(out_path)
    cpu_check(True)
    T0 = time.time()
    res = {"probe_id": "eff-sweep-native", "tier": "X", "blocks_per_seed": BPS, "seeds": list(SEEDS),
           "H": H, "HN": HN, "threads": 4, "top_m": 4, "points": [], "sc_reference": []}
    def save():
        json.dump(res, open(PD + "/results_partial.json", "w"))
    def pinfo(f):
        total, k1, k2 = point(f, H)
        return total, k1, k2, (5*total)/HN, (5*total+16)/HN
    for L, f in GRID:
        total, k1, k2, fn, fc = pinfo(f)
        d1 = t3.worst_k(H1, k1); d2 = t3.worst_k(H2, k2)
        recs = []
        for si, seed in enumerate(SEEDS):
            for b in range(BPS):
                cpu_check()
                x, high, low, bob = t3.gen_block(seed, b, pmf_sample)
                bidx = (L * 10 + int(round(f*100))) % 100000 * 1000 + si*100 + b
                r = t3.eval_scl_joint_block(bidx, high, low, bob, field, p1, p2, d1, d2, L)
                r.update(seed=seed, block=b); recs.append(r)
        n = len(recs)
        cnt = {k: sum(bool(r[k]) for r in recs) for k in ("exact", "verify_failed", "undetected", "decode_failed", "crc_failed", "resource_abort")}
        fer_k = n - cnt["exact"]
        w = [r["block_wall_s"] for r in recs]
        res["points"].append({"L": L, "f_nominal": f, "total": total, "k1": k1, "k2": k2,
            "f_book_no_crc": fn, "f_book_with_crc": fc, "n_blocks": n, "counts": cnt,
            "FER_not_exact": fer_k / n, "wilson95_FER": wilson(fer_k, n),
            "per_seed_exact": {str(s): sum(r["exact"] for r in recs if r["seed"] == s) for s in SEEDS},
            "wall_per_block_mean_s": sum(w)/n, "wall_per_block_max_s": max(w), "records": recs})
        save(); print("DONE", L, f, cnt, "wall/blk", sum(w)/n, "elapsed", time.time()-T0, flush=True)
    for f in SC_F:
        total, k1, k2, fn, fc = pinfo(f)
        d1 = t3.worst_k(H1, k1); d2 = t3.worst_k(H2, k2)
        recs = []
        for si, seed in enumerate(SEEDS):
            for b in range(BPS):
                cpu_check()
                x, high, low, bob = t3.gen_block(seed, b, pmf_sample)
                r = t3.eval_sc_block(int(f*100)*1000 + si*100 + b, high, low, bob, field, p1, p2, d1, d2, k1, k2)
                r.update(seed=seed, block=b); recs.append(r)
        n = len(recs)
        cnt = {k: sum(bool(r[k]) for r in recs) for k in ("exact", "verify_failed", "undetected", "decode_failed", "resource_abort")}
        res["sc_reference"].append({"f_nominal": f, "total": total, "k1": k1, "k2": k2, "f_book_no_crc": fn,
            "n_blocks": n, "counts": cnt, "FER_not_exact": (n-cnt["exact"])/n,
            "wilson95_FER": wilson(n-cnt["exact"], n), "wall_per_block_mean_s": sum(r["block_wall_s"] for r in recs)/n, "records": recs})
        save()
    res["total_wall_s"] = time.time() - T0
    json.dump(res, open(out_path, "w"))
    print("WROTE results.json", res["total_wall_s"])

main(sys.argv[1])
