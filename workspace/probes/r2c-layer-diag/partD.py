from common import *
NB = int(sys.argv[1]) if len(sys.argv) > 1 else 24
ords = {nm: [np.load(f"{OUT}/order_{nm}_L{l}.npy") for l in range(layers)] for nm in ("de", "mc")}
dec = dec_new(); res = {}
cdf = np.cumsum(PT); cdf[-1] = 1
for mu in (0.084, 0.04):
    ks = m.layer_ks(ch["caps"], mu, N)
    f = m.f_of_ks(ks, N, H_DELTA)
    for nm in ("de", "mc"):
        rng = np.random.default_rng(555)
        first = []; exact = 0; lay_err = np.zeros(layers, int); lay_cond_n = np.zeros(layers, int); lay_cond_err = np.zeros(layers, int)
        for bidx in range(NB):
            a = rng.integers(0, d, size=N); dl = np.minimum(np.searchsorted(cdf, rng.random(N)), d - 1); b = (a + dl) % d
            r = m.decode_block(lab, dec, ch["tables"], ords[nm], ks, a, b, layers=layers, n_log=NLOG, list_size=16)
            exact += r["exact"]; first.append(r["first_error_layer"])
            ok_so_far = True
            for lr in r["layers"]:
                if lr["disclosed"]: continue
                lay_err[lr["layer"]] += lr["err"]
                if ok_so_far:      # true-prefix-equivalent: all previous layers correct
                    lay_cond_n[lr["layer"]] += 1; lay_cond_err[lr["layer"]] += lr["err"]
                ok_so_far = ok_so_far and not lr["err"]
        res[f"mu{mu}_{nm}"] = {"f": f, "ks": ks.tolist(), "blocks": NB, "exact": int(exact), "first_error_layer": {str(l): first.count(l) for l in sorted(set(x for x in first if x is not None))},
                                "layer_err_counts": lay_err.tolist(), "layer_cond_err(prefix correct)": lay_cond_err.tolist(), "layer_cond_n": lay_cond_n.tolist()}
        print(mu, nm, res[f"mu{mu}_{nm}"], flush=True)
json.dump(res, open(f"{OUT}/partD.json", "w"), indent=1)
