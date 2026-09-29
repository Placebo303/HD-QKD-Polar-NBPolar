from common import *
from genie import *
layer = int(sys.argv[1])
mus = [0.084, 0.04, 0.02] if layer < 7 else [0.0, 0.02, 0.03, 0.04, 0.06, 0.084]
NF = 64 if layer < 7 else 96
res = {"layer": layer, "cap": float(ch["caps"][layer]), "mus": mus, "NF": NF}
t = time.time()
o_de = m.de_order(lab, tables, PM, layer, d, layers, NLOG, root_seed=m.ROOT_SEED_BASE + layer)
def mc(nframes, fnode, seed, chunk=256):
    rng = np.random.default_rng(seed); Zt = np.zeros(N); Et = np.zeros(N); St = np.zeros(N)
    for c in range(nframes // chunk):
        a, b, x, llr = draw_layer(rng, layer, chunk * N)
        x = x.reshape(chunk, N); llr = llr.reshape(chunk, N)
        u = np.stack([m.encode(lab, xi, NLOG) for xi in x])
        Z, E, S = genie_sc_stats(llr, u, fnode); Zt += Z; Et += E; St += S
    return np.lexsort((-St / nframes, Zt / nframes)).astype(np.int64), Zt / nframes, Et / nframes
o_mc, Z, E = mc(4096, f_ms, 100 + layer)
np.save(f"{OUT}/order_mc_L{layer}.npy", o_mc); np.save(f"{OUT}/order_de_L{layer}.npy", o_de)
print("orders", time.time() - t, flush=True)
dec = dec_new(); rng = np.random.default_rng(20260930 + layer)
a, b, x, llr = draw_layer(rng, layer, NF * N); x = x.reshape(NF, N); llr = llr.reshape(NF, N)
rows = []
for mu in mus:
    k = int(np.floor(N * max(0.0, ch["caps"][layer] - mu)))
    if k < 16: continue
    r = {"mu": mu, "k": k, "k_over_N": k / N, "overlap_DE_MC": m.info_set_overlap(o_de, o_mc, k)}
    for nm, o in (("DE1024", o_de), ("MCms4096", o_mc)):
        e = fer_scl(dec, o, k, x, llr, 16); r["fer_" + nm] = int(e.sum())
    rows.append(r); print(layer, r, flush=True)
res["rows"] = rows
json.dump(res, open(f"{OUT}/partB2_L{layer}.json", "w"), indent=1)
