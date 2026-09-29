import sys, os, importlib.util, time, json
import numpy as np
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"; sys.dont_write_bytecode = True
PK = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2c_strong_binary_msd_shg_64"
OUT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/r2c-layer-diag"
spec = importlib.util.spec_from_file_location("run_", PK + "/run.py")
run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
m = run.load_r2c()
lab = m.load_lab(run.STAGE, run.LAB_SRC)
d, layers, N, NLOG = 1024, 10, 32768, 15
def true_pmf(floor=1e-9):
    p = np.full(d, floor); p[0] = 0.83; p[1] = 0.085; p[-1] = 0.085
    return p / p.sum()
PT = true_pmf()
H_DELTA = float(-(PT*np.log2(PT)).sum())
PM = m.m2_pmf(PT * 1e9, d)   # model: floor 1e-15 on tail, mass at 0,+-1 from true
ch = m.build_channel(lab, "P-M2", PT * 1e9, d)   # tables, caps from model
tables, caps_model = ch["tables"], ch["caps"]
def joint(pmf):
    idx = (np.arange(d)[None, :] - np.arange(d)[:, None]) % d
    return pmf[idx] / d      # P(a,b)
def draw_layer(rng, layer, n):
    cdf = np.cumsum(PT); cdf[-1] = 1
    a = rng.integers(0, d, size=n); dl = np.minimum(np.searchsorted(cdf, rng.random(n)), d-1)
    b = (a + dl) % d
    x = ((a >> (layers-1-layer)) & 1).astype(np.int8)
    llr = tables.llr[layer][a >> (layers-layer), b]
    return a, b, x, llr
def dec_new(): return lab.scl.MsdSclDecoder()
def fer_scl(dec, order, k, x, llr, L=16):
    """x,llr: (F,N). Returns per-frame error bool."""
    mask = lab.polar.info_mask_from_order(order, int(k), N)
    inv = (1 - mask.astype(np.int8))
    u = np.stack([m.encode(lab, xi, NLOG) for xi in x])
    frozen = (u * inv[None, :]).astype(np.uint8)
    u_hat, pm, _ = dec.decode_batch(llr, mask, frozen, NLOG, L)
    return np.array([not np.array_equal(m.encode(lab, u_hat[j], NLOG), x[j]) for j in range(len(x))])
