# -*- coding: utf-8 -*-
"""净密钥产出比较（纯案头重算，不解码、不读原始数据、不跑 run.py）.

只读输入（已提交文件）：
  workspace/r2_fer_shg_64/results.json + part_*.json
  workspace/r2e_fer_shg_64_L32_f124/results.json + part_*.json
  workspace/r2b_fer_shg_64_L32_f120/results.json + part_*.json
  workspace/r2c_strong_binary_msd_shg_64/results.json + part_*.json
  workspace/r2_binary_baseline_shg_64/results.json（仅参照 f_book / p_hat，不进入主结论）

冻结口径（见 docs/nbpolar/NET_SECRET_KEY_COMPARISON_20260930.md）：
  N = 32768；q = 1024；H(A) = 10 bit/符号（均匀性假设，非实测）。
  每符号泄漏 = f_eff * H(A|B)；每成功符号净密钥 r(x) = H(A) - x - f_eff*H(A|B)。
  盈亏平衡 x* = H(A) - f_eff*H(A|B)。
  每池符号净密钥 = (1-p_hat)*(H(A)-x) - f_book*H(A|B) = (1-p_hat)*r(x)。
  方案间差值 Δr = -(f_eff,A - f_eff,B)*H(A|B)，与 x 无关。
  Wilson 95%（z=1.96）；f_eff_upper = f_book/(1-p_upper)。
"""
import glob
import json
import math
import os

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
OUT_DIR = os.path.join(ROOT, "workspace", "netkey_20260930")

N_SYM = 32768
H_A = 10.0  # bit/符号：Alice 符号在 q=1024 上均匀的假设（无实测 H(A)，见主文档）
Z = 1.96


def wilson(k, n, z=Z):
    """Wilson 得分区间的 (lower, upper)。"""
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
    """从 part_*.json 逐块数 NB 方案失败：status != ok 或 scl.verify_failed 或 not scl.exact。

    返回 {session: {'n': int, 'k': int, 'fail_gbi': [...], 'undet_gbi': [...]}}。
    """
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
    """从 r2c part_*.json 按 points[].label 逐块数二元某 f 点的失败（exact False 即失败）。"""
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


def sess_row(f_book, H, n, k):
    """单会话行：p_hat、Wilson、f_eff、f_eff 上/下界、泄漏、x*、r 网格。"""
    p = k / n
    lo, up = wilson(k, n)
    f_eff = f_book / (1.0 - p) if p < 1.0 else float("inf")
    f_eff_up = f_book / (1.0 - up) if up < 1.0 else float("inf")
    f_eff_lo = f_book / (1.0 - lo) if lo < 1.0 else float("inf")
    leak = f_eff * H
    chi_star = H_A - leak
    I_AB = H_A - H
    chi_grid = [0.0, 0.5 * I_AB, chi_star]
    r_grid = [H_A - c - leak for c in chi_grid]
    # 每池符号净密钥 r_pool(c) = (1-p)*(H_A-c) - f_book*H
    r_pool = [(1.0 - p) * (H_A - c) - f_book * H for c in chi_grid]
    return {
        "f_book": f_book, "H": H, "n": n, "k": k, "p_hat": p,
        "wilson_lo": lo, "wilson_up": up,
        "f_eff": f_eff, "f_eff_lo": f_eff_lo, "f_eff_up": f_eff_up,
        "leak": leak, "chi_star": chi_star, "I_AB": I_AB,
        "chi_grid": chi_grid, "r_success": r_grid, "r_pool": r_pool,
    }


def pooled_row(sess_rows):
    """pooled：总披露/总产出口径。

    d_bar = 各会话每符号披露均值（n 加权）；H_bar = 各会话 H 均值（n 加权）；
    p_bar = 总失败/总块；f_eff_pool = d_bar/((1-p_bar)*H_bar)。
    每池符号净密钥 = ((1-p_s) 加权平均)*(H_A-c) - d_bar；
    每成功符号净密钥 = 每池净密钥/(1-p_bar)。
    """
    n_tot = sum(r["n"] for r in sess_rows.values())
    k_tot = sum(r["k"] for r in sess_rows.values())
    d_bar = sum(r["n"] * r["f_book"] * r["H"] for r in sess_rows.values()) / n_tot
    H_bar = sum(r["n"] * r["H"] for r in sess_rows.values()) / n_tot
    p_bar = k_tot / n_tot
    lo, up = wilson(k_tot, n_tot)
    f_eff = d_bar / ((1.0 - p_bar) * H_bar)
    f_eff_up = d_bar / ((1.0 - up) * H_bar)
    f_eff_lo = d_bar / ((1.0 - lo) * H_bar)
    leak = f_eff * H_bar
    chi_star = H_A - leak
    I_AB = H_A - H_bar
    # 每池符号净密钥（精确：各会话 (1-p_s) 加权）
    w_succ = sum(r["n"] * (1.0 - r["k"] / r["n"]) for r in sess_rows.values()) / n_tot
    chi_grid = [0.0, 0.5 * I_AB, chi_star]
    r_pool = [w_succ * (H_A - c) - d_bar for c in chi_grid]
    r_success = [v / (1.0 - p_bar) for v in r_pool]
    return {
        "f_book_wavg": d_bar / H_bar, "d_bar": d_bar, "H_bar": H_bar,
        "n": n_tot, "k": k_tot, "p_hat": p_bar,
        "wilson_lo": lo, "wilson_up": up,
        "f_eff": f_eff, "f_eff_lo": f_eff_lo, "f_eff_up": f_eff_up,
        "leak": leak, "chi_star": chi_star, "I_AB": I_AB,
        "chi_grid": chi_grid, "r_success": r_success, "r_pool": r_pool,
    }


def main():
    res = {}
    H_check = {}

    # ---- NB 三方案：f_book 取 per_session.<G>.f_book_with_crc_computed ----
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
            f_book = ps["f_book_with_crc_computed"]
            c = counts[sess]
            assert c["undet_gbi"] == [], (name, sess)
            entry["sessions"][sess] = sess_row(f_book, ps["h_total_bits"], c["n"], c["k"])
            entry["sessions"][sess]["fail_gbi"] = c["fail_gbi"]
            entry["sessions"][sess]["D_blk"] = ps["kdb_with_crc"]
        entry["pooled"] = pooled_row(entry["sessions"])
        res[name] = entry

    # ---- 二元 R2C F2/F3：f 取 per_point.<F>.per_session.<G>.f_realized ----
    r2c = load_json(os.path.join(ROOT, "workspace/r2c_strong_binary_msd_shg_64/results.json"))
    assert r2c.get("undetected_block_ids", []) == []
    for F in ("F2", "F3"):
        name = "BIN_" + F
        entry = {"source_dir": "workspace/r2c_strong_binary_msd_shg_64", "sessions": {}}
        counts = count_r2c_failures(F)
        for sess in ("G2", "G3"):
            ps = r2c["per_point"][F]["per_session"][sess]
            assert ps["h_total_bits"] if "h_total_bits" in ps else True
            H = r2c["per_session_construction"][sess]["h_total_bits"]
            assert H == H_check[sess], (name, sess)
            c = counts[sess]
            # 与 results.json 内 taxonomy 交叉核对
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
        # pooled 与 results.json 交叉核对
        assert r2c["per_point"][F]["pooled"]["verify_failed"] == entry["pooled"]["k"], F
        res[name] = entry

    # ---- 可比性核对：F2 与 NB R2 的 D_blk 逐位相等 ----
    assert res["NB_R2"]["sessions"]["G2"]["D_blk"] == res["BIN_F2"]["sessions"]["G2"]["D_blk"] == 34135
    assert res["NB_R2"]["sessions"]["G3"]["D_blk"] == res["BIN_F2"]["sessions"]["G3"]["D_blk"] == 34135

    # ---- 冻结二元基线（仅参照）：SC f_book，taxonomy 失败率 ----
    base = load_json(os.path.join(ROOT, "workspace/r2_binary_baseline_shg_64/results.json"))
    Href = {"G2": H_check["G2"], "G3": H_check["G3"]}
    bref = {"source_dir": "workspace/r2_binary_baseline_shg_64", "margins": {}}
    for m in base["per_margin"]:
        marg = m["sc_margin"]
        fb = m["f_breakdown_by_session"]
        tx = m["taxonomy_by_session"]
        me = {"sessions": {}}
        for sess in ("G2", "G3"):
            k = tx[sess]["verify_failed"]
            n = tx[sess]["D_valid_denominator"]
            row = sess_row(fb[sess]["f_book_sc"], Href[sess], n, k)
            row["f_book_scl"] = fb[sess]["f_book_scl"]
            me["sessions"][sess] = row
        me["pooled"] = pooled_row(me["sessions"])
        bref["margins"][str(marg)] = me
    res["BASELINE_REF"] = bref

    # ---- Δr 表（与 x 无关）：point + Wilson 盒式区间 ----
    # 区间：[r_A(f_up_A) - r_B(f_lo_B), r_A(f_lo_A) - r_B(f_up_B)]，用每成功符号口径。
    def rate_at(row, f_eff):
        H = row.get("H", row.get("H_bar"))
        return H_A - f_eff * H  # x=0 处；Δr 与 x 无关，取 x=0 代表

    pairs = [("NB_R2E", "NB_R2"), ("NB_R2B", "NB_R2"),
             ("NB_R2", "BIN_F2"), ("NB_R2", "BIN_F3"), ("BIN_F2", "BIN_F3")]
    scopes = ["G2", "G3", "pooled"]
    delta = {}
    for a, b in pairs:
        key = a + "_minus_" + b
        delta[key] = {}
        for sc in scopes:
            ra = res[a]["pooled"] if sc == "pooled" else res[a]["sessions"][sc]
            rb = res[b]["pooled"] if sc == "pooled" else res[b]["sessions"][sc]
            H = ra["H_bar"] if sc == "pooled" else ra["H"]
            # pooled 两方案 H_bar 几乎相同（同 H 加权）；用 A 侧 H_bar，差值量级不受影响
            pt = rate_at(ra, ra["f_eff"]) - rate_at(rb, rb["f_eff"])
            lo = rate_at(ra, ra["f_eff_up"]) - rate_at(rb, rb["f_eff_lo"])
            hi = rate_at(ra, ra["f_eff_lo"]) - rate_at(rb, rb["f_eff_up"])
            delta[key][sc] = {"point": pt, "box_lo": lo, "box_hi": hi,
                              "covers_zero": (lo <= 0.0 <= hi)}
    res["delta_r_chi_independent"] = delta

    res["conventions"] = {
        "N_symbols_per_block": N_SYM, "q": 1024,
        "H_A_bits_per_symbol": H_A,
        "H_A_status": "assumption_uniform_not_measured",
        "H_cond_source": "per_session.<G>.h_total_bits of each results.json (cross-checked equal across files)",
        "H_cond": H_check,
        "wilson_z": Z,
        "formulas": {
            "leak_per_symbol": "f_eff * H(A|B)",
            "r_success": "H(A) - chi - f_eff*H(A|B)",
            "chi_star": "H(A) - f_eff*H(A|B)",
            "r_pool": "(1-p_hat)*(H(A)-chi) - f_book*H(A|B) = (1-p_hat)*r_success",
            "f_eff": "f_book/(1-p_hat)",
            "f_eff_upper": "f_book/(1-p_upper_wilson95)",
            "delta_r": "-(f_eff_A - f_eff_B)*H(A|B), chi-independent",
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
