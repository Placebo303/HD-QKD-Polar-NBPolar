"""Synthetic timing of the CAL32-only construction steps at d=1024 (no N=32768 decode, no DE). Single process."""
import sys, time, importlib.util
import numpy as np
sys.path.insert(0, "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2c_strong_binary_msd_shg_64")
spec = importlib.util.spec_from_file_location("run_", "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2c_strong_binary_msd_shg_64/run.py")
run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
m = run.load_r2c()
lab = m.load_lab(run.STAGE, run.LAB_SRC)
d = 1024
rng = np.random.default_rng(1)
pmf = np.full(d, 3e-5); pmf[0] = 0.55
for s, v in ((1, 0.14), (2, 0.05), (3, 0.02)):
    pmf[s] = v; pmf[-s] = v
pmf /= pmf.sum()
cdf = np.cumsum(pmf); cdf[-1] = 1
a = rng.integers(0, d, 8192); b = (a + np.minimum(np.searchsorted(cdf, rng.random(8192)), d - 1)) % d
cfg = m.RunConfig()
t = time.perf_counter()
con = m.freeze_construction(lab, cfg, "S", 0, a, b, 0.82)
print("freeze_construction wall", round(time.perf_counter() - t, 2), "s; source", con["cv"]["source"], "R", round(con["invariance"]["R_resid"], 3), round(con["invariance"]["R_marginal"], 3))
print("caps", np.round(con["channel"]["caps"], 4), "sum", round(con["channel"]["sum_caps"], 4), "10-sum", round(10 - con["channel"]["sum_caps"], 4), "H(pmf)", round(con["channel"]["pmf_entropy_bits"], 4))
t = time.perf_counter()
for f in (1.2, 1.3, 1.6):
    mu = m.solve_mu_for_f(con["channel"]["caps"], f, cfg.n, 0.82)
    print("f", f, "mu", round(mu, 5), "ks", m.layer_ks(con["channel"]["caps"], mu, cfg.n).tolist())
print("solve wall", round(time.perf_counter() - t, 3))
print("peak rss GiB", m._peak_rss_gib())
