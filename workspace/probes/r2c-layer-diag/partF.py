from common import *
# inject ONE confidently-wrong symbol (|LLR| = clip 30, sign wrong) per frame; MC order; mu=0.084
layer = int(sys.argv[1]); NF = 64; mu = float(sys.argv[2]) if len(sys.argv) > 2 else 0.084
o = np.load(f"{OUT}/order_mc_L{layer}.npy"); k = int(np.floor(N * (ch["caps"][layer] - mu)))
dec = dec_new(); rng = np.random.default_rng(31 + layer)
a, b, x, llr = draw_layer(rng, layer, NF * N); x = x.reshape(NF, N); llr = llr.reshape(NF, N).copy()
e0 = fer_scl(dec, o, k, x, llr, 16).sum()
pos = rng.integers(0, N, size=NF)
inj = llr.copy()
for j in range(NF): inj[j, pos[j]] = -(1 - 2 * x[j, pos[j]]) * 30.0
e1 = fer_scl(dec, o, k, x, inj, 16).sum()
inj2 = llr.copy()
for j in range(NF): inj2[j, pos[j]] = -(1 - 2 * x[j, pos[j]]) * 10.0
e2 = fer_scl(dec, o, k, x, inj2, 16).sum()
r = {"layer": layer, "mu": mu, "k": k, "frames": NF, "fail_clean": int(e0), "fail_1_wrong_at_30": int(e1), "fail_1_wrong_at_10": int(e2)}
print(r); json.dump(r, open(f"{OUT}/partF_L{layer}_mu{mu}.json", "w"))
