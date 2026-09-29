# -*- coding: utf-8 -*-
"""R3 效率记账计算脚本（W1，案头计算，不解码、不读原始数据）。

读（只读）：
  workspace/r2_fer_shg_64/results.json（H_total、frozen K1/K2/N、blocks[] 运行时）
  workspace/r2_fer_shg_64/part_*.json（逐块失败计数）
  workspace/r2e_fer_shg_64_L32_f124/part_*.json + results.json（R2E 描述性对照 + 原生 L=32 运行时）
  workspace/r2b_fer_shg_64_L32_f120/part_*.json + results.json（R2B 原生 L=32 运行时）
  workspace/r2c_strong_binary_msd_shg_64/results.json（R2C F2/F3 描述性对照）
  workspace/probes/eff-sweep-native/results.json（合成原生 L=16/L=32 耗时）
写：
  workspace/closure_20260930/r3_accounting.json（本脚本同目录输出）
"""
import json
import glob
import math
import os

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
R2 = ROOT + "/workspace/r2_fer_shg_64"
R2E = ROOT + "/workspace/r2e_fer_shg_64_L32_f124"
R2B = ROOT + "/workspace/r2b_fer_shg_64_L32_f120"
R2C = ROOT + "/workspace/r2c_strong_binary_msd_shg_64"
EFFSWEEP = ROOT + "/workspace/probes/eff-sweep-native"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r3_accounting.json")

Z = 1.96  # Wilson 95%
N_SYM = 32768  # 每块符号数（冻结）
LOGQ_SUB = 5  # log2(32)，每个 GF(32) 冻结坐标 5 bit
CRC_BITS = 16  # 冻结（R2 frozen_params.crc_bits_extra 与各块 scl.crc_bits 交叉核对）
TAG_BITS = 64  # 冻结（R2C per_session tag_bits=64 交叉核对）
CAL_FRAMES = 32  # 每会话 CAL32 牺牲帧数
POOL_FRAMES_PER_SESSION = 4096  # 每会话进入 64 块池帧数（32 块 x 128 帧）


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def wilson(k, n, z=Z):
    """标准 Wilson 区间（z=1.96）。"""
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return center - half, center + half


def count_parts(pattern):
    """按记账口径逐块计数：scl.exact==False 或 status != 'ok' 计失败；undetected 单列。"""
    fails = []
    undet = []
    n = 0
    for fp in sorted(glob.glob(pattern)):
        d = load(fp)
        n += 1
        scl = d.get("scl") or {}
        if scl.get("exact") is False or d.get("status") != "ok":
            fails.append(d.get("global_block_index"))
        if scl.get("undetected"):
            undet.append(d.get("global_block_index"))
    return n, sorted(fails), sorted(undet)


def stats(xs):
    return {"n": len(xs), "mean": sum(xs) / len(xs), "max": max(xs), "min": min(xs)}


checks = []


def check(name, value, expected, tol=1e-4):
    diff = abs(value - expected)
    ok = diff <= tol
    checks.append({"name": name, "value": value, "expected": expected,
                   "abs_diff": diff, "tol": tol, "pass": ok})
    if not ok:
        raise SystemExit(f"STOP: {name} 文件值 {value!r} 与预期 {expected!r} 差 {diff!r} > {tol}")


# ---------- R2 主工作点 ----------
r2 = load(R2 + "/results.json")
frz = r2["frozen_params"]
K1, K2 = frz["k1"], frz["k2"]
assert frz["n"] == N_SYM
assert frz["list_width_L"] == 16 and frz["top_m"] == 4
assert frz["crc_bits_extra"] == CRC_BITS
H_G2 = r2["per_session"]["G2"]["h_total_bits"]
H_G3 = r2["per_session"]["G3"]["h_total_bits"]

D_blk = LOGQ_SUB * (K1 + K2) + CRC_BITS + TAG_BITS
D_blk_noCRC = LOGQ_SUB * (K1 + K2) + TAG_BITS

n_G2, fails_G2, undet_G2 = count_parts(R2 + "/part_G2_*.json")
n_G3, fails_G3, undet_G3 = count_parts(R2 + "/part_G3_*.json")

# §7 停下条件：失败块必须是 gbi23（G2）/ gbi38（G3），undetected 必须为 0
if sorted(fails_G2) != [23] or sorted(fails_G3) != [38]:
    raise SystemExit(f"STOP(§7): 失败块与已裁定不一致 G2={fails_G2} G3={fails_G3}")
if undet_G2 or undet_G3 or r2.get("undetected_block_ids"):
    raise SystemExit(f"STOP(§7): undetected 非零 {undet_G2} {undet_G3} {r2.get('undetected_block_ids')}")

r2sess = {}
for sess, H, n, fails in (("G2", H_G2, n_G2, fails_G2), ("G3", H_G3, n_G3, fails_G3)):
    k = len(fails)
    p = k / n
    lo, hi = wilson(k, n)
    f_book = D_blk / (H * N_SYM)
    f_nocrc = D_blk_noCRC / (H * N_SYM)
    r2sess[sess] = {
        "H_total_bits": H, "n_blocks": n, "n_fail": k, "fail_gbi": fails,
        "p_hat": p, "wilson95": [lo, hi],
        "f_book": f_book, "f_book_noCRC": f_nocrc,
        "f_eff": f_book / (1.0 - p),
        "f_eff_upper_session": f_book / (1.0 - hi),
    }

n_pool = n_G2 + n_G3
k_pool = len(fails_G2) + len(fails_G3)
p_pool = k_pool / n_pool
wlo, whi = wilson(k_pool, n_pool)
for sess in ("G2", "G3"):
    r2sess[sess]["f_eff_upper_pooled"] = r2sess[sess]["f_book"] / (1.0 - whi)

lam_cal = CAL_FRAMES / (CAL_FRAMES + POOL_FRAMES_PER_SESSION)
eps_tag = 2.0 ** -64

# ---------- §3.2 预期值核对（差 > 1e-4 即停下） ----------
check("D_blk", D_blk, 34135)
check("D_blk_noCRC", D_blk_noCRC, 34119)
check("H_G2", H_G2, 0.8168138204133305, tol=0.0)
check("H_G3", H_G3, 0.8214782076249098, tol=0.0)
check("f_book_G2", r2sess["G2"]["f_book"], 1.275343)
check("f_book_G3", r2sess["G3"]["f_book"], 1.268101)
check("f_book_noCRC_G2", r2sess["G2"]["f_book_noCRC"], 1.27475)
check("f_book_noCRC_G3", r2sess["G3"]["f_book_noCRC"], 1.26751)
check("p_hat_G2", r2sess["G2"]["p_hat"], 1 / 32, tol=0.0)
check("p_hat_G3", r2sess["G3"]["p_hat"], 1 / 32, tol=0.0)
check("p_hat_pooled", p_pool, 2 / 64, tol=0.0)
check("wilson_pooled_lo", wlo, 0.008612)
check("wilson_pooled_hi", whi, 0.106975)
# 每会话 Wilson 预期以 ≈ 给出（[0.0055, 0.157]）：按舍入一致性核对并记录
for sess in ("G2", "G3"):
    lo, hi = r2sess["G2"]["wilson95"] if sess == "G2" else r2sess["G3"]["wilson95"]
    ok = (round(lo, 4) == 0.0055 and round(hi, 3) == 0.157)
    checks.append({"name": f"wilson_session_{sess}_rounded",
                   "value": [lo, hi], "expected": "[0.0055, 0.157] 舍入一致",
                   "abs_diff": None, "tol": None, "pass": ok})
    if not ok:
        raise SystemExit(f"STOP: wilson_session_{sess}={[lo, hi]} 与 ≈[0.0055,0.157] 舍入不一致")
check("f_eff_G2", r2sess["G2"]["f_eff"], 1.3165)
check("f_eff_G3", r2sess["G3"]["f_eff"], 1.3090)
# f_eff_upper pooled 预期以 ≈ 给出（3 位小数，隐含精度 ±5e-4，比 1e-4 判据更粗，
# 主线程 2026-09-30 裁决：按印刷精度做舍入一致性核对，数值本身不作任何改动）
for sess, exp3 in (("G2", 1.428), ("G3", 1.420)):
    v = r2sess[sess]["f_eff_upper_pooled"]
    ok = round(v, 3) == exp3
    checks.append({"name": f"f_eff_upper_pooled_{sess}_rounded",
                   "value": v, "expected": f"≈{exp3:.3f}（舍入到 3 位一致）",
                   "abs_diff": abs(v - exp3), "tol": "舍入一致",
                   "pass": ok})
    if not ok:
        raise SystemExit(f"STOP: f_eff_upper_pooled_{sess}={v} 舍入到 3 位不等于 {exp3}")
check("lambda_cal", lam_cal, 0.00775)
check("eps_tag", eps_tag, 5.4e-20)

# ---------- §3.3 运行时 / RSS（从文件取数，不重跑） ----------
r2_scl = [b["resources"]["wall_scl_s"] for b in r2["blocks"]]
r2_sc = [b["resources"]["wall_sc_s"] for b in r2["blocks"]]
r2_rss = [b["resources"]["rss_gib_peak_advisory"] for b in r2["blocks"]]


def native_stats(d):
    scl, rss = [], []
    for fp in sorted(glob.glob(d + "/part_G*_*.json")):
        r = load(fp)["resources"]
        scl.append(r["wall_scl_s"])
        rss.append(r["rss_gib_peak_advisory"])
    return stats(scl), stats(rss)


r2e_scl, r2e_rss = native_stats(R2E)
r2b_scl, r2b_rss = native_stats(R2B)
bound_s = max(r2e_scl["max"], r2b_scl["max"])
bound_src = "R2E" if r2e_scl["max"] >= r2b_scl["max"] else "R2B"

ess = load(EFFSWEEP + "/results.json")
sweep = [{"L": p["L"], "f_nominal": p["f_nominal"], "k1": p["k1"], "k2": p["k2"],
          "n_blocks": p["n_blocks"], "counts": p["counts"],
          "wall_per_block_mean_s": p["wall_per_block_mean_s"],
          "wall_per_block_max_s": p["wall_per_block_max_s"],
          "f_book_with_crc": p["f_book_with_crc"]}
         for p in ess["points"]]
l16 = [p for p in sweep if p["L"] == 16]
l32 = [p for p in sweep if p["L"] == 32]
# 合成 L=16 典型吞吐：取最接近工作点 f 的点（f_nominal=1.25）
typ16 = min(l16, key=lambda p: abs(p["f_nominal"] - 1.25))

runtime = {
    "R2_scl_joint_L16": {"impl": "scl_joint Python/numba 参考实现", "data": "真实",
                         "wall_scl_s": stats(r2_scl), "wall_sc_s": stats(r2_sc),
                         "rss_gib_peak": stats(r2_rss)},
    "R2E_native_L32": {"impl": "原生 Rust SCL", "data": "真实",
                       "wall_scl_s": r2e_scl, "rss_gib_peak": r2e_rss},
    "R2B_native_L32": {"impl": "原生 Rust SCL", "data": "真实",
                       "wall_scl_s": r2b_scl, "rss_gib_peak": r2b_rss},
    "upper_bound_native_L16": {"value_s": bound_s, "source": bound_src,
                               "note": "由论证得到的上界，非 L=16 真实数据实测"},
    "throughput_sym_per_s": {
        "bound_conservative": N_SYM / bound_s,
        "synth_L16_typical_mean": N_SYM / typ16["wall_per_block_mean_s"],
        "synth_L16_typical_max": N_SYM / typ16["wall_per_block_max_s"],
        "scl_joint_reference_mean": N_SYM / (sum(r2_scl) / len(r2_scl)),
    },
    "eff_sweep": {"threads": ess["threads"], "H": ess["H"], "seeds": ess["seeds"],
                  "points": sweep, "typical_L16_point": typ16,
                  "sc_reference_summary": [
                      {"f_nominal": s.get("f_nominal"), "n_blocks": s.get("n_blocks"),
                       "counts": s.get("counts"),
                       "wall_per_block_mean_s": s.get("wall_per_block_mean_s")}
                      for s in (ess.get("sc_reference") or [])],
                  "note": "合成数据，仅供典型耗时参考"},
}

# ---------- §3.4 描述性对照（同一记账口径） ----------
r2e = load(R2E + "/results.json")
r2ef = r2e["frozen_params"]
D_r2e = LOGQ_SUB * (r2ef["k1"] + r2ef["k2"]) + CRC_BITS + TAG_BITS
nE_G2, failsE_G2, undetE_G2 = count_parts(R2E + "/part_G2_*.json")
nE_G3, failsE_G3, undetE_G3 = count_parts(R2E + "/part_G3_*.json")
r2e_table = {"D_blk": D_r2e, "k1": r2ef["k1"], "k2": r2ef["k2"], "L": 32,
             "undetected": undetE_G2 + undetE_G3, "sessions": {}}
for sess, H, n, fails in (("G2", r2e["per_session"]["G2"]["h_total_bits"], nE_G2, failsE_G2),
                          ("G3", r2e["per_session"]["G3"]["h_total_bits"], nE_G3, failsE_G3)):
    k = len(fails)
    p = k / n
    lo, hi = wilson(k, n)
    fb = D_r2e / (H * N_SYM)
    r2e_table["sessions"][sess] = {
        "H_total_bits": H, "n_blocks": n, "n_fail": k, "p_hat": p,
        "wilson95": [lo, hi], "f_book": fb,
        "f_book_file": r2e["per_session"][sess]["f_book_with_crc_computed"],
        "f_eff": fb / (1.0 - p), "f_eff_upper_session": fb / (1.0 - hi)}

r2c = load(R2C + "/results.json")
r2c_table = {}
for label in ("F2", "F3"):
    per = r2c["per_point"][label]["per_session"]
    pool = r2c["per_point"][label]["pooled"]
    entry = {"crc": "二元不付 CRC（RESULT_SUMMARY §结论：NB 侧付 CRC 16 位，二元侧不付）",
             "tag_bits": 64, "pooled": {}, "sessions": {}}
    kp, np = pool["n_entries"] - pool["exact"], pool["n_entries"]
    plo, phi = wilson(kp, np)
    entry["pooled"] = {"n": np, "n_fail": kp, "p_hat": kp / np, "wilson95": [plo, phi]}
    for sess in ("G2", "G3"):
        t = per[sess]["taxonomy"]
        k = t["n_entries"] - t["exact"]
        n = t["n_entries"]
        p = k / n
        lo, hi = wilson(k, n)
        fb = per[sess]["f_realized"]
        entry["sessions"][sess] = {
            "f_realized_as_f_book": fb, "K_frozen": per[sess]["K_frozen"],
            "n": n, "n_fail": k, "p_hat": p, "wilson95": [lo, hi],
            "f_eff": fb / (1.0 - p) if p < 1.0 else None,
            "f_eff_upper_session": fb / (1.0 - hi),
            "f_eff_upper_pooled": fb / (1.0 - phi)}
    r2c_table[label] = entry

check("R2C_F3_pooled_wilson_upper", r2c_table["F3"]["pooled"]["wilson95"][1], 0.0566)

out = {
    "frozen": {"N_sym": N_SYM, "K1": K1, "K2": K2, "crc_bits": CRC_BITS,
               "tag_bits": TAG_BITS,
               "H_total": {"G2": H_G2, "G3": H_G3},
               "sources": {
                   "N/K1/K2/L/top_m": "workspace/r2_fer_shg_64/results.json:frozen_params",
                   "H_total": "workspace/r2_fer_shg_64/results.json:per_session.<G>.h_total_bits",
                   "crc_bits": "workspace/r2_fer_shg_64/results.json:frozen_params.crc_bits_extra 及 blocks[].scl.crc_bits",
                   "tag_bits": "workspace/r2c_strong_binary_msd_shg_64/results.json:per_point.F2.per_session.G2.tag_bits (=64)"}},
    "D_blk": D_blk, "D_blk_noCRC": D_blk_noCRC,
    "R2": {"sessions": r2sess,
           "pooled": {"n": n_pool, "n_fail": k_pool, "p_hat": p_pool,
                      "wilson95": [wlo, whi], "undetected": 0}},
    "lambda_cal": {"value": lam_cal, "formula": "32/(32+4096)",
                   "source": "docs/nbpolar/DATA_LEDGER.md §7（CAL32=32 帧/会话排除；64 块池=32 块/会话 x 128 帧=4096 帧/会话）"},
    "eps_tag": {"value": eps_tag, "formula": "2^-64",
                "source": "冻结参数（Toeplitz tag 64 bit）"},
    "runtime": runtime,
    "descriptive": {"R2E": r2e_table, "R2C": r2c_table,
                    "note": "NB 与二元 FER 点不同，不得据此宣称胜负"},
    "expected_checks": checks,
}
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("wrote", OUT)
print(f"R2 G2 f_book={r2sess['G2']['f_book']:.6f} f_eff={r2sess['G2']['f_eff']:.4f} "
      f"f_eff_up={r2sess['G2']['f_eff_upper_pooled']:.4f}")
print(f"R2 G3 f_book={r2sess['G3']['f_book']:.6f} f_eff={r2sess['G3']['f_eff']:.4f} "
      f"f_eff_up={r2sess['G3']['f_eff_upper_pooled']:.4f}")
print(f"pooled wilson=[{wlo:.6f},{whi:.6f}] bound={bound_s:.2f}s ({bound_src}) "
      f"tp_cons={N_SYM / bound_s:.0f} tp_L16syn={N_SYM / typ16['wall_per_block_mean_s']:.0f} "
      f"tp_joint={N_SYM / (sum(r2_scl) / len(r2_scl)):.0f} sym/s")
print(f"checks: {sum(1 for c in checks if c['pass'])}/{len(checks)} pass")
