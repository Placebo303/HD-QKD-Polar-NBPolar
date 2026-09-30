# -*- coding: utf-8 -*-
"""从 netkey.json 全精度值一次性 round(.,3) 重生成文档 §4 三张表并原地替换。"""
import json, re
ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/"
R = json.load(open(ROOT + "workspace/netkey_20260930/netkey.json", encoding="utf-8"))
DOC = ROOT + "docs/nbpolar/NET_SECRET_KEY_COMPARISON_20260930.md"
schemes = [("NB R2", "NB_R2"), ("NB R2E", "NB_R2E"), ("NB R2B", "NB_R2B"), ("二元 F2", "BIN_F2"), ("二元 F3", "BIN_F3")]
margins = [("基线 m0.02", "0.02"), ("基线 m0.08", "0.08"), ("基线 m0.18", "0.18")]


def fmt_p(p):
    return "0" if p == 0 else "%.3f" % p


def wl(r):
    lo, up = r["wilson_lo"], r["wilson_up"]
    return "[%s,%.4f]" % ("0" if lo == 0 else "%.4f" % lo, up)


def row(label, r, pooled):
    f = r["f_book_wavg"] if pooled else r["f_book"]
    vals = " | ".join(("%.3f" % round(r["r_pool"][str(c)], 3)).replace("-", "−") for c in range(9))
    return "| %s | %.4f | %d/%d (%s) | %s | %.4f | %s |" % (label, f, r["k"], r["n"], fmt_p(r["p_hat"]), wl(r), r["chi_star"], vals)


hdr = "| 方案 | f_book%s | k/n (p̂) | Wilson | χ* | χ=0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
out = []
for title, sc in (("G2（H(A|B) = 0.8168）", "G2"), ("G3（H(A|B) = 0.8215）", "G3"), ("pooled（G2+G3 各 32 块，H(A|B) 均值 0.8191）", "pooled")):
    p = sc == "pooled"
    out.append("### " + title + "\n")
    out.append(hdr % ("（加权）" if p else ""))
    for lab, k in schemes:
        r = R[k]["pooled"] if p else R[k]["sessions"][sc]
        out.append(row(lab, r, p))
    for lab, m in margins:
        r = R["BASELINE_REF"]["margins"][m]["pooled"] if p else R["BASELINE_REF"]["margins"][m]["sessions"][sc]
        out.append(row(lab, r, p))
    out.append("")
new = "\n".join(out) + "\n"
txt = open(DOC, encoding="utf-8").read()
a = txt.index("### G2（H(A|B) = 0.8168）")
b = txt.index("## 5. β 表")
txt = txt[:a] + new + txt[b:]
old8 = "失败率 0.61–0.97（§4 表末三行，§5 表末三行）"
assert old8 in txt
txt = txt.replace(old8, "失败率 pooled 0.61–0.94（逐会话 0.56–0.97；§4 表末三行，§5 表末三行）")
open(DOC, "w", encoding="utf-8").write(txt)
print(new)
