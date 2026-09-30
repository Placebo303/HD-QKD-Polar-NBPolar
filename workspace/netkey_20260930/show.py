# -*- coding: utf-8 -*-
"""打印 netkey.json 关键表（辅助，只读）。"""
import json
R = json.load(open("/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/netkey_20260930/netkey.json", encoding="utf-8"))
names = ["NB_R2", "NB_R2E", "NB_R2B", "BIN_F2", "BIN_F3"]
for sc in ("G2", "G3", "pooled"):
    print("== beta", sc)
    rows = [(n, R[n]["pooled"] if sc == "pooled" else R[n]["sessions"][sc]) for n in names]
    for m, mm in R["BASELINE_REF"]["margins"].items():
        rows.append(("BASE_m" + m, mm["pooled"] if sc == "pooled" else mm["sessions"][sc]))
    for n, r in rows:
        print("%-10s f=%.4f k/n=%d/%d p=%.4f W=[%.4f,%.4f] chi*=%.4f beta=%.4f beta_eff=%.4f beta_eff_up=%.4f  I=%.4f" % (
            n, r["f_book"] if "f_book_wavg" not in r else r["f_book_wavg"], r["k"], r["n"], r["p_hat"], r["wilson_lo"], r["wilson_up"],
            r["chi_star"], r["beta"], r["beta_eff"], r["beta_eff_at_wilson_up"], r["I_AB"]))
    print("-- r_pool chi=0..8")
    for n, r in rows:
        print("%-10s" % n, " ".join("%7.4f" % r["r_pool"][str(c)] for c in range(9)))
        if "r_pool_exact" in r:
            print("  exact-check maxdiff", max(abs(r["r_pool_exact"][str(c)] - r["r_pool"][str(c)]) for c in range(9)))
for key, d in R["delta_r_pool"].items():
    for sc, v in d.items():
        print(key, sc, " | ".join("%d:%+.3f[%+.3f,%+.3f]%s" % (c, v[str(c)]["point"], v[str(c)]["box_lo"], v[str(c)]["box_hi"], "D" if v[str(c)]["distinguishable"] else "-") for c in (0, 2, 4, 6, 8)))
for key, d in R["delta_r_pool"].items():
    for sc, v in d.items():
        ds = [c for c in range(9) if v[str(c)]["distinguishable"]]
        print("DIST", key, sc, ds)
