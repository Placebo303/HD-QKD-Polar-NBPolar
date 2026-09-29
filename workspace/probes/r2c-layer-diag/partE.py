from common import *
from genie import *
layer = int(sys.argv[1]); mus = [float(v) for v in sys.argv[2].split(",")]; NF = 96
o = np.load(f"{OUT}/order_mc_L{layer}.npy"); dec = dec_new()
rng = np.random.default_rng(20260930 + layer)     # same frames as partB2
a, b, x, llr = draw_layer(rng, layer, NF * N); x = x.reshape(NF, N); llr = llr.reshape(NF, N)
u = np.stack([m.encode(lab, xi, NLOG) for xi in x])
out = []
for mu in mus:
    k = int(np.floor(N * (ch["caps"][layer] - mu))); mask = lab.polar.info_mask_from_order(o, k, N)
    r = {"layer": layer, "mu": mu, "k": k, "frames": NF}
    for L in (1, 4, 16, 32, 64):
        t = time.time(); r[f"SCL_minsum_L{L}"] = int(fer_scl(dec, o, k, x, llr, L).sum()); r[f"t_L{L}"] = round(time.time() - t, 1)
    r["SC_numpy_minsum"] = int(sc_decode(llr, mask, u, f_ms).sum())
    r["SC_numpy_exactboxplus"] = int(sc_decode(llr, mask, u, f_ex).sum())
    print(r, flush=True); out.append(r)
json.dump(out, open(f"{OUT}/partE_L{layer}.json", "w"), indent=1)
