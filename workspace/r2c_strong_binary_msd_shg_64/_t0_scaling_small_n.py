"""Single-process SCL timing at N=4096/8192/16384 (L=16), synthetic; extrapolation input only."""
import sys, time, importlib.util
import numpy as np
spec = importlib.util.spec_from_file_location("run_", "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2c_strong_binary_msd_shg_64/run.py")
run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
m = run.load_r2c(); lab = m.load_lab(run.STAGE, run.LAB_SRC)
dec = lab.scl.MsdSclDecoder()
rng = np.random.default_rng(1)
for n_log in (12, 13, 14):
    n = 1 << n_log
    x = rng.integers(0, 2, n).astype(np.int8)
    llr = (rng.normal(0, 1, n) + 1.6 * (1 - 2 * x)).astype(np.float32)
    order = lab.polar.reliable_order(n)
    for rate in (0.5, 0.9):
        k = int(rate * n)
        m.decode_layer(lab, dec, llr, order, k, x, n_log, 16)
        t = time.perf_counter(); xh, pm = m.decode_layer(lab, dec, llr, order, k, x, n_log, 16); dt = time.perf_counter() - t
        print(f"N={n} L=16 rate={rate} {dt:.3f}s  ok={np.array_equal(xh, x)}")
print("rss", m._peak_rss_gib())
