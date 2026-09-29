# -*- coding: utf-8 -*-
"""只读审查 scratch：核对总报告数字 vs 来源文件。只读，不写任何结果目录。"""
import json, math, os

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
out = []

def log(s):
    out.append(s)
    print(s)

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c-h), min(1.0, c+h))

def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)

# ---- R2 ----
r2 = load("workspace/r2_fer_shg_64/results.json")
log("== R2 ==")
log("per_session G2 h=%r f_with=%r f_no=%r kdb_with=%r kdb_no=%r" % (
    r2["per_session"]["G2"].get("h_total_bits"),
    r2["per_session"]["G2"].get("f_book_with_crc_computed", r2["per_session"]["G2"].get("f_book_with_crc")),
    r2["per_session"]["G2"].get("f_book_no_crc_computed", r2["per_session"]["G2"].get("f_book_no_crc")),
    r2["per_session"]["G2"].get("kdb_with_crc"), r2["per_session"]["G2"].get("kdb_no_crc")))
log("per_session G3 h=%r f_with=%r f_no=%r" % (
    r2["per_session"]["G3"].get("h_total_bits"),
    r2["per_session"]["G3"].get("f_book_with_crc_computed", r2["per_session"]["G3"].get("f_book_with_crc")),
    r2["per_session"]["G3"].get("f_book_no_crc_computed", r2["per_session"]["G3"].get("f_book_no_crc"))))
tp = r2.get("taxonomy_pooled", {})
log("pooled=%s" % json.dumps({k: tp.get(k) for k in ["n_blocks","D_valid_denominator","D","exact","verify_failed","decode_failed","undetected","resource_abort","p_hat","phat","wilson_95ci","wilson_95_ci"]}, ensure_ascii=False))
log("recalc wilson(2,64)=%r" % (wilson(2,64),))
for key in ["taxonomy_by_stratum_task","taxonomy_by_stratum_official"]:
    log("%s=%s" % (key, json.dumps(r2.get(key), ensure_ascii=False)[:2000]))
log("frozen=%s" % json.dumps(r2.get("frozen_params", {}), ensure_ascii=False)[:1500])
# seeds
fp = r2.get("frozen_params", {})
log("R2 seeds: eval=%r tag=%r" % (fp.get("eval_seed_shared"), fp.get("tag_master_shared")))
# timing: mean/max wall_scl, rss max
try:
    blks = r2.get("blocks", [])
    import statistics
    scl = [b["resources"]["wall_scl_s"] for b in blks if "resources" in b and "wall_scl_s" in b["resources"]]
    sc = [b["resources"]["wall_sc_s"] for b in blks if "resources" in b and "wall_sc_s" in b["resources"]]
    rss = [b["resources"]["rss_gib_peak_advisory"] for b in blks if "resources" in b and "rss_gib_peak_advisory" in b["resources"]]
    if scl:
        log("R2 scl n=%d mean=%.6f max=%.6f min=%.6f thr_mean=%.6f" % (len(scl), sum(scl)/len(scl), max(scl), min(scl), 32768/(sum(scl)/len(scl))))
    if sc:
        log("R2 sc mean=%.6f max=%.6f" % (sum(sc)/len(sc), max(sc)))
    if rss:
        log("R2 rss max=%.6f" % max(rss))
except Exception as e:
    log("R2 timing err %r" % e)

# ---- R2E ----
r2e = load("workspace/r2e_fer_shg_64_L32_f124/results.json")
log("== R2E ==")
log("pooled=%s" % json.dumps(r2e.get("taxonomy_pooled", {}), ensure_ascii=False)[:800])
log("per_session=%s" % json.dumps(r2e.get("per_session", {}), ensure_ascii=False)[:1500])
log("frozen K=%r seeds eval=%r tag=%r" % (r2e.get("frozen_params", {}).get("K_total", r2e.get("frozen_params", {})), r2e.get("frozen_params", {}).get("eval_seed"), r2e.get("frozen_params", {}).get("tag_master")))
log("frozen_params=%s" % json.dumps(r2e.get("frozen_params", {}), ensure_ascii=False)[:1200])
log("recalc wilson(3,64)=%r" % (wilson(3,64),))

# ---- R2B ----
r2b = load("workspace/r2b_fer_shg_64_L32_f120/results.json")
log("== R2B ==")
log("pooled=%s" % json.dumps(r2b.get("taxonomy_pooled", {}), ensure_ascii=False)[:800])
log("per_session=%s" % json.dumps(r2b.get("per_session", {}), ensure_ascii=False)[:1500])
log("frozen_params=%s" % json.dumps(r2b.get("frozen_params", {}), ensure_ascii=False)[:1200])
log("recalc wilson(14,64)=%r" % (wilson(14,64),))

# ---- R2C ----
r2c = load("workspace/r2c_strong_binary_msd_shg_64/results.json")
log("== R2C ==")
pp = r2c.get("per_point", {})
for F in ["F1","F2","F3","F4"]:
    d = pp.get(F, {})
    log("%s keys=%s" % (F, list(d.keys())[:10]))
    for G in ["G2","G3"]:
        s = d.get("per_session", {}).get(G, {})
        log("%s %s f_realized=%r K_frozen=%r tag_bits=%r exact=%r fail=%r" % (
            F, G, s.get("f_realized"), s.get("K_frozen", s.get("k_frozen", s.get("Kfrozen"))), s.get("tag_bits"),
            s.get("exact", s.get("n_exact")), s.get("verify_failed", s.get("n_fail"))))
    tax = d.get("taxonomy", d.get("taxonomy_pooled", {}))
    log("%s taxonomy=%s" % (F, json.dumps(tax, ensure_ascii=False)[:600]))
log("R2C pairing=%s" % json.dumps(r2c.get("nb_scl_L16_pairing", r2c.get("pairing", {})), ensure_ascii=False)[:1500])
# invariance / CV
for G in ["G2","G3"]:
    inv = r2c.get("invariance", {}).get(G, r2c.get("per_session", {}).get(G, {}))
    log("R2C inv %s=%s" % (G, json.dumps(inv, ensure_ascii=False)[:400]))
log("R2C top keys=%s" % list(r2c.keys()))
log("recalc wilson F2 pooled(18,64)=%r F3 pooled(0,64)=%r F1(64,64)=%r" % (wilson(18,64), wilson(0,64), wilson(64,64)))

# ---- binary baseline ----
bb = load("workspace/r2_binary_baseline_shg_64/results.json")
log("== binary baseline ==")
log("top keys=%s" % list(bb.keys())[:20])
s = json.dumps(bb, ensure_ascii=False)
log("len=%d" % len(s))
# try points
for k in ["points","margins","per_margin","results","grid"]:
    if k in bb:
        log("bb[%s]=%s" % (k, json.dumps(bb[k], ensure_ascii=False)[:2000]))

# ---- R3 json (read-only!) ----
r3 = load("workspace/closure_20260930/r3_accounting.json")
log("== R3 json keys=%s" % list(r3.keys())[:20])
log("R3=%s" % json.dumps(r3, ensure_ascii=False)[:3000])

# ---- probes eff-sweep ----
try:
    pr = load("workspace/probes/eff-sweep-native/results.json")
    log("probe keys=%s" % list(pr.keys())[:10])
    log("probe=%s" % json.dumps(pr, ensure_ascii=False)[:1500])
except Exception as e:
    log("probe err %r" % e)

with open("/tmp/opencode/report_review_dump.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
