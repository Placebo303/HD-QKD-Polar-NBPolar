# -*- coding: utf-8 -*-
"""净密钥产出比较 v2（纯案头重算，不解码、不读原始数据、不跑 run.py）.

2026-09-30 PI 批准的方法更正（M1-M5）：
  M1 主指标 = 每原始符号净密钥
       r_pool(chi) = (1-p)*(H(A) - chi - f_book*H(A|B))
     成功块产出 H(A)-chi-f_book*H(A|B)，失败块产出 0，块间独立，失败块披露不扣其他块。
     每成功符号量 r_succ(chi) = H(A)-chi-f_book*H(A|B) 只作辅助，不作比较主证据。
  M2 Δr_pool = r_pool,A - r_pool,B
            = (pB-pA)*(H(A)-chi) - [(1-pA)*fA - (1-pB)*fB]*H(A|B)   （依赖 chi、H(A)）
  M3 Δr_pool 带 Wilson95 保守区间：r_pool 对 p 线性，取 p 在 [lo,up] 的四个角点
     的最小/最大（chi<=chi* 时等价于 A 用 p 上界、B 用 p 下界给下界，反之给上界）。
  M4 chi 网格 0..8（步长 1 bit）+ 各方案 chi* = H(A) - f_book*H(A|B)（r_pool=0）。
  M5 beta = (H(A)-f_book*H)/I(A;B)；beta_eff = (1-p)*beta；I = H(A)-H(A|B)。

输入（只读）：r2 / r2e / r2b / r2c 的 results.json + part_*.json，
  冻结二元基线 results.json（f 与失败率取实际网格值）。
H(A)=10 bit/符号为假设（无实测 H(A) bit 值）。
"""
import glob
import json
import math
import os

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
OUT_DIR = os.path.join(ROOT, "workspace", "netkey_20260930")

N_SYM = 32768
H_A = 10.0  # bit/符号：假设（Alice 符号在 q=1024 上均匀），非实测
Z = 1.96
CHI_GRID = list(range(0, 9))  # 0..8 bit，步长 1


def wilson(k, n, z=Z):
    """Wilson 得分区间 (lower, upper)。"""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    den = 1.0 + z * z / n
    c = p + z * z / (2.0 * n)
    m = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return ((c - m) / den, (c + m) / den)


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def count_nb_failures(d):
    """part_*.json 逐块数 NB 失败：status!=ok 或 scl.verify_failed 或 not scl.exact。"""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, d, "part_*.json"))):
        b = load_json(f)
        sess = b["session"]
        e = out.setdefault(sess, {"n": 0, "k": 0, "fail_gbi": [], "undet_gbi": []})
        e["n"] += 1
        s = b.get("scl", {})
        failed = (b.get("status") != "ok") or s.get("verify_failed", False) \
            or (not s.get("exact", True))
        if failed:
            e["k"] += 1
            e["fail_gbi"].append(b.get("global_block_index"))
        if s.get("undetected", False):
            e["undet_gbi"].append(b.get("global_block_index"))
    return out


def count_r2c_failures(label):
    """r2c part_*.json 按 points[].label 逐块数二元某 f 点的失败（exact False 即失败）。"""
    d = "workspace/r2c_strong_binary_msd_shg_64"
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, d, "part_*.json"))):
        b = load_json(f)
        sess = b["session"]
        e = out.setdefault(sess, {"n": 0, "k": 0, "fail_gbi": [], "undet_gbi": []})
        for p in b["points"]:
            if p["label"] == label:
                e["n"] += 1
                if not p.get("exact", False):
                    e["k"] += 1
                    e["fail_gbi"].append(b.get("global_block_index"))
    return out


def make_row(d_leak, H, n, k, f_book=None):
    """通用行。d_leak = 每原始符号披露 = f_book*H(A|B)（pooled 时为 n 加权均值）。

    r_pool(chi) = (1-p)*(H_A - chi - d_leak)；r_succ(chi) = H_A - chi - d_leak（辅助）。
    """
    p = k / n
    lo, up = wilson(k, n)
    I_AB = H_A - H
    beta = (H_A - d_leak) / I_AB
    return {
        "f_book": f_book if f_book is not None else d_leak / H,
        "H": H, "I_AB": I_AB, "n": n, "k": k, "p_hat": p,
        "wilson_lo": lo, "wilson_up": up,
        "d_leak": d_leak,
        "chi_star": H_A - d_leak,
        "beta": beta, "beta_eff": (1.0 - p) * beta,
        "beta_eff_at_wilson_up": (1.0 - up) * beta,
        "beta_eff_at_wilson_lo": (1.0 - lo) * beta,
        "r_pool": {str(c): (1.0 - p) * (H_A - c - d_leak) for c in CHI_GRID},
        "r_succ_aux": {str(c): (H_A - c - d_leak) for c in CHI_GRID},
    }


def sess_row(f_book, H, n, k):
    return make_row(f_book * H, H, n, k, f_book=f_book)


def pooled_row(sess_rows):
    """pooled：n 加权。d_bar=Σ n·f·H/Σn，H_bar=Σ n·H/Σn，p_bar=Σk/Σn。
    另给 r_pool_exact（逐会话 (1-p_s)(c-d_s) 按 n 加权）用于核对 (1-p_bar)(c-d_bar) 近似。
    """
    n_tot = sum(r["n"] for r in sess_rows.values())
    k_tot = sum(r["k"] for r in sess_rows.values())
    d_bar = sum(r["n"] * r["d_leak"] for r in sess_rows.values()) / n_tot
    H_bar = sum(r["n"] * r["H"] for r in sess_rows.values()) / n_tot
    row = make_row(d_bar, H_bar, n_tot, k_tot)
    row["f_book_wavg"] = d_bar / H_bar
    row["r_pool_exact"] = {
        str(c): sum(r["n"] * (1.0 - r["p_hat"]) * (H_A - c - r["d_leak"])
                    for r in sess_rows.values()) / n_tot for c in CHI_GRID}
    return row


def delta_pool(ra, rb, chi):
    """Δr_pool 点估计（公式形式，用于核对代数）与 Wilson 角点区间。"""
    c = H_A - chi
    pt = (1 - ra["p_hat"]) * (c - ra["d_leak"]) - (1 - rb["p_hat"]) * (c - rb["d_leak"])
    # 代数形式：(pB-pA)*c - [(1-pA)*dA - (1-pB)*dB]，d = f*H
    alg = (rb["p_hat"] - ra["p_hat"]) * c \
        - ((1 - ra["p_hat"]) * ra["d_leak"] - (1 - rb["p_hat"]) * rb["d_leak"])
    assert abs(pt - alg) < 1e-12, (pt, alg)
    vals = []
    for pa in (ra["wilson_lo"], ra["wilson_up"]):
        for pb in (rb["wilson_lo"], rb["wilson_up"]):
            vals.append((1 - pa) * (c - ra["d_leak"]) - (1 - pb) * (c - rb["d_leak"]))
    lo, hi = min(vals), max(vals)
    # 方向核对（chi<=两方案 chi* 时）：下界 = A 用 p 上界、B 用 p 下界
    if c - ra["d_leak"] >= 0 and c - rb["d_leak"] >= 0:
        lo_dir = (1 - ra["wilson_up"]) * (c - ra["d_leak"]) - (1 - rb["wilson_lo"]) * (c - rb["d_leak"])
        hi_dir = (1 - ra["wilson_lo"]) * (c - ra["d_leak"]) - (1 - rb["wilson_up"]) * (c - rb["d_leak"])
        assert abs(lo - lo_dir) < 1e-12 and abs(hi - hi_dir) < 1e-12
    return {"point": pt, "box_lo": lo, "box_hi": hi, "distinguishable": not (lo <= 0.0 <= hi)}


def main():
    res = {}
    H_check = {}

    nb_dirs = {
        "NB_R2": "workspace/r2_fer_shg_64",
        "NB_R2E": "workspace/r2e_fer_shg_64_L32_f124",
        "NB_R2B": "workspace/r2b_fer_shg_64_L32_f120",
    }
    for name, d in nb_dirs.items():
        rj = load_json(os.path.join(ROOT, d, "results.json"))
        counts = count_nb_failures(d)
        assert rj.get("undetected_block_ids", []) == [], name
        entry = {"source_dir": d, "sessions": {}}
        for sess in ("G2", "G3"):
            ps = rj["per_session"][sess]
            H_check.setdefault(sess, ps["h_total_bits"])
            assert ps["h_total_bits"] == H_check[sess], (name, sess)
            c = counts[sess]
            assert c["undet_gbi"] == [], (name, sess)
            row = sess_row(ps["f_book_with_crc_computed"], ps["h_total_bits"], c["n"], c["k"])
            row["fail_gbi"] = c["fail_gbi"]
            row["D_blk"] = ps["kdb_with_crc"]
            entry["sessions"][sess] = row
        entry["pooled"] = pooled_row(entry["sessions"])
        res[name] = entry

    r2c = load_json(os.path.join(ROOT, "workspace/r2c_strong_binary_msd_shg_64/results.json"))
    assert r2c.get("undetected_block_ids", []) == []
    for F in ("F2", "F3"):
        name = "BIN_" + F
        entry = {"source_dir": "workspace/r2c_strong_binary_msd_shg_64", "sessions": {}}
        counts = count_r2c_failures(F)
        for sess in ("G2", "G3"):
            ps = r2c["per_point"][F]["per_session"][sess]
            H = r2c["per_session_construction"][sess]["h_total_bits"]
            assert H == H_check[sess], (name, sess)
            c = counts[sess]
            tax = ps["taxonomy"]
            assert tax["verify_failed"] == c["k"], (name, sess, tax, c)
            assert tax["undetected"] == 0, (name, sess)
            row = sess_row(ps["f_realized"], H, c["n"], c["k"])
            row["fail_gbi"] = c["fail_gbi"]
            row["K_frozen"] = ps["K_frozen"]
            row["tag_bits"] = ps["tag_bits"]
            row["D_blk"] = ps["K_frozen"] + ps["tag_bits"]
            entry["sessions"][sess] = row
        entry["pooled"] = pooled_row(entry["sessions"])
        assert r2c["per_point"][F]["pooled"]["verify_failed"] == entry["pooled"]["k"], F
        res[name] = entry

    for s in ("G2", "G3"):
        assert res["NB_R2"]["sessions"][s]["D_blk"] == res["BIN_F2"]["sessions"][s]["D_blk"] == 34135

    # 冻结二元基线（f 与失败率取实际网格值）
    base = load_json(os.path.join(ROOT, "workspace/r2_binary_baseline_shg_64/results.json"))
    bref = {"source_dir": "workspace/r2_binary_baseline_shg_64", "margins": {}}
    for m in base["per_margin"]:
        marg = m["sc_margin"]
        fb = m["f_breakdown_by_session"]
        tx = m["taxonomy_by_session"]
        me = {"sessions": {}}
        for sess in ("G2", "G3"):
            k = tx[sess]["verify_failed"]
            n = tx[sess]["D_valid_denominator"]
            row = sess_row(fb[sess]["f_book_sc"], H_check[sess], n, k)
            me["sessions"][sess] = row
        me["pooled"] = pooled_row(me["sessions"])
        bref["margins"][str(marg)] = me
    res["BASELINE_REF"] = bref

    # Δr_pool：A = NB_R2，对 R2E / R2B / F2 / F3，per-session 与 pooled，chi=0..8
    pairs = [("NB_R2", "NB_R2E"), ("NB_R2", "NB_R2B"), ("NB_R2", "BIN_F2"), ("NB_R2", "BIN_F3")]
    delta = {}
    for a, b in pairs:
        key = a + "_minus_" + b
        delta[key] = {}
        for sc in ("G2", "G3", "pooled"):
            ra = res[a]["pooled"] if sc == "pooled" else res[a]["sessions"][sc]
            rb = res[b]["pooled"] if sc == "pooled" else res[b]["sessions"][sc]
            delta[key][sc] = {str(c): delta_pool(ra, rb, c) for c in CHI_GRID}
    res["delta_r_pool"] = delta

    res["conventions"] = {
        "N_symbols_per_block": N_SYM, "q": 1024,
        "H_A_bits_per_symbol": H_A,
        "H_A_status": "assumption_uniform_not_measured",
        "H_cond": H_check,
        "chi_grid_bits": CHI_GRID,
        "chi_status": "unmeasured_no_security_analysis_in_project; absolute r not a conclusion",
        "wilson_z": Z,
        "formulas": {
            "r_pool": "(1-p_hat)*(H(A) - chi - f_book*H(A|B))",
            "r_succ_aux": "H(A) - chi - f_book*H(A|B)",
            "chi_star": "H(A) - f_book*H(A|B)",
            "delta_r_pool": "(pB-pA)*(H(A)-chi) - [(1-pA)*fA - (1-pB)*fB]*H(A|B)",
            "beta": "(H(A) - f_book*H(A|B))/I(A;B)",
            "beta_eff": "(1-p_hat)*beta",
            "I_AB": "H(A)-H(A|B)",
            "wilson_box": "min/max of Δr over p_A,p_B in Wilson endpoints (linear in p)",
        },
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "netkey.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote " + out_path)


if __name__ == "__main__":
    main()
