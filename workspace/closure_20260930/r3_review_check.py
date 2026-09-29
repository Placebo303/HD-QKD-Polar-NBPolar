# -*- coding: utf-8 -*-
"""R3 独立审查重算脚本（只读，不写任何结果目录）。输出到 stdout 供审查记录。"""
import json, glob, math

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"

def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def wilson(k, n, z=1.96):
    p = k / n
    d = 1.0 + z*z/n
    c = (p + z*z/(2.0*n)) / d
    h = z*math.sqrt(p*(1.0-p)/n + z*z/(4.0*n*n)) / d
    return (c-h, c+h)

out = {}
# ---- A. R2 parts 独立计数 ----
for sess, pat in (("G2", "/workspace/r2_fer_shg_64/part_G2_*.json"),
                  ("G3", "/workspace/r2_fer_shg_64/part_G3_*.json")):
    fps = sorted(glob.glob(ROOT+pat))
    n = len(fps); fails = []; undet = []; det = []
    for fp in fps:
        d = load(fp)
        scl = d.get("scl") or {}
        ex = scl.get("exact"); st = d.get("status"); ud = scl.get("undetected")
        gbi = d.get("global_block_index")
        if ex is False or st != "ok":
            fails.append((gbi, ex, st, scl.get("verify_failed"), fp.split("/")[-1]))
        if ud:
            undet.append(gbi)
        det.append((gbi, ex, st, ud))
    out[sess] = {"n": n, "fails": fails, "undet": undet}
    print(f"R2 {sess}: n={n} fails={fails} undet={undet}")

r2 = load(ROOT+"/workspace/r2_fer_shg_64/results.json")
print("R2 frozen:", {k: r2["frozen_params"].get(k) for k in ("n","k1","k2","list_width_L","top_m","crc_bits_extra","construction_digest")})
for sess in ("G2","G3"):
    ps = r2["per_session"][sess]
    print(f"R2 per_session.{sess}: h_total={ps.get('h_total_bits')!r} f_book_with_crc={ps.get('f_book_with_crc_computed')!r} f_book_no_crc={ps.get('f_book_no_crc_computed')!r} kdb_with_crc={ps.get('kdb_with_crc')!r} kdb_no_crc={ps.get('kdb_no_crc')!r}")
print("R2 taxonomy_pooled:", json.dumps(r2.get("taxonomy_pooled"), ensure_ascii=False)[:800])
print("R2 undetected_block_ids:", r2.get("undetected_block_ids"), "resource_abort:", r2.get("resource_abort_block_ids"))

# 独立算 D, f, wilson, f_eff
K1, K2 = 319, 6492
D = 5*(K1+K2)+16+64; Dn = 5*(K1+K2)+64
print(f"D_blk={D} D_noCRC={Dn}")
for sess in ("G2","G3"):
    H = r2["per_session"][sess]["h_total_bits"]
    fb = D/(H*32768); fn = Dn/(H*32768)
    print(f"{sess}: f_book={fb!r} f_noCRC={fn!r}")
    for k,n in ((1,32),(2,64),(0,32),(0,64),(3,64),(18,64),(2,32),(16,32)):
        lo,hi = wilson(k,n)
        print(f"  wilson({k}/{n})=[{lo!r},{hi!r}]")
    for k,n in ((1,32),):
        lo,hi = wilson(k,n)
        print(f"  {sess} f_eff={fb/(1-k/n)!r} f_eff_up_sess={fb/(1-hi)!r}", end=" ")
    _,ph = wilson(2,64)
    print(f"f_eff_up_pooled={fb/(1-ph)!r}")
print(f"lam_cal={32/(32+4096)!r} eps_tag={2.0**-64!r}")

# ---- C. runtime ----
blks = r2["blocks"]
scl = [b["resources"]["wall_scl_s"] for b in blks]
sc = [b["resources"]["wall_sc_s"] for b in blks]
rss = [b["resources"]["rss_gib_peak_advisory"] for b in blks]
print(f"R2 scl n={len(scl)} mean={sum(scl)/len(scl)!r} max={max(scl)!r} min={min(scl)!r}")
print(f"R2 sc mean={sum(sc)/len(sc)!r} max={max(sc)!r} min={min(sc)!r}")
print(f"R2 rss mean={sum(rss)/len(rss)!r} max={max(rss)!r} min={min(rss)!r}")
print("R2 blocks keys sample:", sorted(blks[0].get("resources",{}).keys()))
print("R2 blocks[0].scl keys:", sorted((blks[0].get("scl") or {}).keys()), "crc_bits=", (blks[0].get("scl") or {}).get("crc_bits"))

def natstat(d):
    s=[]; r=[]
    fps = sorted(glob.glob(ROOT+d+"/part_G*_*.json"))
    keys=None
    for fp in fps:
        rr = load(fp)["resources"]
        if keys is None: keys=sorted(rr.keys())
        s.append(rr["wall_scl_s"]); r.append(rr["rss_gib_peak_advisory"])
    return len(s), sum(s)/len(s), max(s), min(s), sum(r)/len(r), max(r), min(r), keys

for d in ("/workspace/r2e_fer_shg_64_L32_f124","/workspace/r2b_fer_shg_64_L32_f120"):
    n,me,ma,mi,rme,rma,rmi,keys = natstat(d)
    print(f"{d}: n={n} scl mean={me!r} max={ma!r} min={mi!r} rss mean={rme!r} max={rma!r} min={rmi!r} keys={keys}")
    # 失败计数
    for sess in ("G2","G3"):
        fps = sorted(glob.glob(ROOT+d+f"/part_{sess}_*.json"))
        f=0; u=0
        for fp in fps:
            dd=load(fp); s2=dd.get("scl") or {}
            if s2.get("exact") is False or dd.get("status")!="ok": f+=1
            if s2.get("undetected"): u+=1
        print(f"  {sess}: n={len(fps)} fail={f} undet={u}")

for d in ("/workspace/r2e_fer_shg_64_L32_f124","/workspace/r2b_fer_shg_64_L32_f120"):
    rr = load(ROOT+d+"/results.json")
    print(d, "frozen:", json.dumps(rr.get("frozen_params"), ensure_ascii=False)[:500])
    ps = rr.get("per_session",{})
    for sess in ("G2","G3"):
        if sess in ps:
            print(f"  {d} {sess}: h={ps[sess].get('h_total_bits')!r} f_book_file={ps[sess].get('f_book_with_crc_computed')!r}")
    print(f"  {d} taxonomy_pooled:", json.dumps(rr.get("taxonomy_pooled"), ensure_ascii=False)[:400])

# eff sweep
ess = load(ROOT+"/workspace/probes/eff-sweep-native/results.json")
print("eff-sweep keys:", sorted(ess.keys()), "threads=", ess.get("threads"), "H=", ess.get("H"), "seeds=", ess.get("seeds"))
for p in ess.get("points",[]):
    print(f"  L={p.get('L')} f={p.get('f_nominal')} n={p.get('n_blocks')} counts={p.get('counts')} mean={p.get('wall_per_block_mean_s')!r} max={p.get('wall_per_block_max_s')!r} f_book={p.get('f_book_with_crc')!r}")
print("sc_reference:", json.dumps(ess.get("sc_reference"), ensure_ascii=False)[:600])

# R2E D check
for d in ("/workspace/r2e_fer_shg_64_L32_f124",):
    rr = load(ROOT+d+"/results.json"); fr=rr["frozen_params"]
    print("R2E k1/k2/L:", fr.get("k1"), fr.get("k2"), fr.get("list_width_L"), "D=", 5*(fr.get("k1")+fr.get("k2"))+16+64)

# ---- D. R2C ----
r2c = load(ROOT+"/workspace/r2c_strong_binary_msd_shg_64/results.json")
print("R2C top keys:", sorted(r2c.keys()), "per_point:", sorted(r2c.get("per_point",{}).keys()))
for label in ("F2","F3"):
    per = r2c["per_point"][label]["per_session"]; pool = r2c["per_point"][label]["pooled"]
    print(f"R2C {label} pooled:", json.dumps(pool, ensure_ascii=False)[:400])
    for sess in ("G2","G3"):
        t = per[sess]
        print(f"  R2C {label}/{sess}: f_realized={t.get('f_realized')!r} K_frozen={t.get('K_frozen')!r} tag_bits={t.get('tag_bits')!r} taxonomy={json.dumps(t.get('taxonomy'), ensure_ascii=False)[:300]}")
print("R2C F2 G2 tag_bits check:", r2c["per_point"]["F2"]["per_session"]["G2"].get("tag_bits"))

# 吞吐验算
print("throughput: 32768/39.37917227298021=", 32768/39.37917227298021)
print("throughput: 32768/21.86891207363078=", 32768/21.86891207363078)
print("throughput: 32768/26.528139255940914=", 32768/26.528139255940914)
print("throughput: 32768/530.4223976186586=", 32768/530.4223976186586)
# f_eff 上界验算
fb2=1.2753426830727925; fb3=1.268101234613064
_,phi=wilson(2,64); _,sh=wilson(1,32)
print("G2 f_eff_up_pooled=", fb2/(1-phi), " G3=", fb3/(1-phi))
print("G2 f_eff_up_sess=", fb2/(1-sh), " G3=", fb3/(1-sh))
# R2C F3 上界验算
_,f3pu=wilson(0,64); _,f3su=wilson(0,32)
print("F3 pooled wilson upper=", f3pu, " sess upper=", f3su)
print("F3G2 f_eff_up_pooled=", 1.3124428818216216/(1-f3pu), " sess=", 1.3124428818216216/(1-f3su))
print("F3G3 f_eff_up_pooled=", 1.3135723320545871/(1-f3pu), " sess=", 1.3135723320545871/(1-f3su))
# R2E f_eff
print("R2E G2 fb=", 33365/(0.8168138204133305*32768), " feff=", (33365/(0.8168138204133305*32768))/(1-1/32))
print("R2E G3 fb=", 33365/(0.8214782076249098*32768), " feff=", (33365/(0.8214782076249098*32768))/(1-2/32))
_,e3hi=wilson(2,32)
print("R2E G3 f_eff_up_sess=", (33365/(0.8214782076249098*32768))/(1-e3hi))
