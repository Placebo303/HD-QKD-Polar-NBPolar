from common import *
from genie import *
layer = int(sys.argv[1]); NF = int(sys.argv[2]) if len(sys.argv) > 2 else 128
MU = 0.084
k0 = int(np.floor(N * (ch["caps"][layer] - MU)))
res = {"layer": layer, "k_mu0.084": k0}
def de_chunked(mtot, seed0):
    zs, mls = [], []
    for c in range(mtot // 1024):
        root = m.de_root_llr(tables, PM, layer, d, layers, m_root=4096, seed=seed0 + 7 * c)
        pop = lab.de.de_llr_populations_from_root(root, NLOG, n_samples=1024, seed=seed0 + 1000 + c)
        zs.append(np.mean(np.exp(-np.abs(pop) / 2), axis=1)); mls.append(np.mean(pop, axis=1)); del pop
    z = np.mean(zs, 0); ml = np.mean(mls, 0)
    return np.lexsort((ml, z)).astype(np.int64), z
orders = {}
t = time.time()
orders["DE1024_impl"] = m.de_order(lab, tables, PM, layer, d, layers, NLOG, root_seed=m.ROOT_SEED_BASE + layer)  # session idx0
print("DE1024 impl", time.time() - t, flush=True)
orders["DE1024_altseed"], _ = de_chunked(1024, 777)
orders["DE4096"], _ = de_chunked(4096, 4242)
orders["DE16384"], zde = de_chunked(16384, 9999) if os.environ.get("BIG") else (None, None)
if orders["DE16384"] is None: del orders["DE16384"]
print("DE done", time.time() - t, flush=True)
def mc(nframes, fnode, seed, chunk=256):
    rng = np.random.default_rng(seed); Zt = np.zeros(N); Et = np.zeros(N); St = np.zeros(N)
    for c in range(nframes // chunk):
        a, b, x, llr = draw_layer(rng, layer, chunk * N)
        x = x.reshape(chunk, N); llr = llr.reshape(chunk, N)
        u = np.stack([m.encode(lab, xi, NLOG) for xi in x])
        Z, E, S = genie_sc_stats(llr, u, fnode)
        Zt += Z; Et += E; St += S
    Zt /= nframes; Et /= nframes; St /= nframes
    return np.lexsort((-St, Zt)).astype(np.int64), Zt, Et
orders["MCms256"], _, _ = mc(256, f_ms, 1)
orders["MCms4096"], Zms, Ems = mc(4096, f_ms, 2)
orders["MCex4096"], Zex, Eex = mc(4096, f_ex, 3)
orders["MCms1024"], _, _ = mc(1024, f_ms, 5)
print("MC done", time.time() - t, flush=True)
ref = "MCms4096"
res["overlap_vs_MCms4096_at_k"] = {n: m.info_set_overlap(o, orders[ref], k0) for n, o in orders.items()}
res["overlap_vs_DE1024_impl_at_k"] = {n: m.info_set_overlap(o, orders["DE1024_impl"], k0) for n, o in orders.items()}
# genie-SC expected block error (union bound) from MC bit-error stats for each order: sum of Pe over info set (MC-ms4096 stats)
def ub(order, k, E): return float(np.sum(E[order[:k]]))
res["ub_sumPe_ms(info set of order, k0)"] = {n: ub(o, k0, Ems) for n, o in orders.items()}
res["ub_sumPe_exact_f"] = {n: ub(o, k0, Eex) for n, o in orders.items()}
res["MC_ms4096_sumPe_top_k0(min-sum best)"] = float(np.sort(Ems)[:k0].sum())
res["MC_ex4096_sumPe_top_k0"] = float(np.sort(Eex)[:k0].sum())
res["sumZ_at_k0_ms"] = {n: float(np.sum(Zms[o[:k0]])) for n, o in orders.items()}
res["sumZ_at_k0_ms_best"] = float(np.sort(Zms)[:k0].sum())
# max k such that sum Pe<0.01 under min-sum genie (best order)
cs = np.cumsum(np.sort(Ems)); res["k_for_sumPe<0.01_ms"] = int(np.searchsorted(cs, 0.01)); 
cs2 = np.cumsum(np.sort(Eex)); res["k_for_sumPe<0.01_exact"] = int(np.searchsorted(cs2, 0.01))
res["k_for_sumZ<0.01_ms"] = int(np.searchsorted(np.cumsum(np.sort(Zms)), 0.01))
res["cap_N"] = float(N * ch["caps"][layer])
np.save(f"{OUT}/orders_L{layer}.npy", np.stack([orders[n] for n in orders]))
# FER at k0, common frames
dec = dec_new(); rng = np.random.default_rng(20260930 + layer)
a, b, x, llr = draw_layer(rng, layer, NF * N); x = x.reshape(NF, N); llr = llr.reshape(NF, N)
fer = {}
for n, o in orders.items():
    e = fer_scl(dec, o, k0, x, llr, 16); fer[n] = [int(e.sum()), NF]
    print(layer, n, fer[n], flush=True)
res["fer_L16_at_k0"] = fer
# sanity: are failing frames due to few bit errors? check bit errors count for DE1024 on failures
json.dump(res, open(f"{OUT}/partB_L{layer}.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items()}, indent=1))
