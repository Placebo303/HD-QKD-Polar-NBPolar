from common import *
from genie import *
layer = int(sys.argv[1]); NF = 96
mus = [0.084, 0.06]
t = time.time()
root = m.de_root_llr(tables, PM, layer, d, layers, m_root=4096, seed=m.ROOT_SEED_BASE + layer)
pop = lab.de.de_llr_populations_from_root(root, NLOG, n_samples=2400, seed=m.DE_SEED)
o24 = lab.de.de_order_from_population(pop); del pop
print("DE2400", time.time() - t, flush=True)
o_de = np.load(f"{OUT}/order_de_L{layer}.npy"); o_mc = np.load(f"{OUT}/order_mc_L{layer}.npy")
rng = np.random.default_rng(777 + layer); Et = np.zeros(N); nfr = 2048
for c in range(nfr // 256):
    a, b, x, llr = draw_layer(rng, layer, 256 * N); x = x.reshape(256, N); llr = llr.reshape(256, N)
    u = np.stack([m.encode(lab, xi, NLOG) for xi in x]); Z, E, S = genie_sc_stats(llr, u, f_ms); Et += E
Et /= nfr
dec = dec_new(); rng = np.random.default_rng(20260930 + layer)
a, b, x, llr = draw_layer(rng, layer, NF * N); x = x.reshape(NF, N); llr = llr.reshape(NF, N)
out = []
for mu in mus:
    k = int(np.floor(N * (ch["caps"][layer] - mu))); r = {"layer": layer, "mu": mu, "k": k}
    for nm, o in (("DE1024", o_de), ("DE2400", o24), ("MC4096", o_mc)):
        r["sumPe_freshMC2048_" + nm] = float(Et[o[:k]].sum()); r["n_bad_info(Pe>0.05)_" + nm] = int((Et[o[:k]] > 0.05).sum())
        r["overlap_vs_MC_" + nm] = m.info_set_overlap(o, o_mc, k)
    r["fer_DE2400"] = int(fer_scl(dec, o24, k, x, llr, 16).sum()); r["fer_DE1024"] = int(fer_scl(dec, o_de, k, x, llr, 16).sum()); r["fer_MC4096"] = int(fer_scl(dec, o_mc, k, x, llr, 16).sum())
    print(r, flush=True); out.append(r)
json.dump(out, open(f"{OUT}/partG_L{layer}.json", "w"), indent=1)
