"""SYNTHETIC full-scale timing run (d=1024, N=32768, L=16, M_design=256, default RunConfig) with 2 synthetic
sessions x BLOCKS blocks.  No real data.  Output -> dry_run_realscale/ (gitignored).  Usage: python _t3_realscale_synth.py [workers] [blocks]"""
import sys, time, importlib.util
import numpy as np
HERE = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2c_strong_binary_msd_shg_64"
spec = importlib.util.spec_from_file_location("run_", HERE + "/run.py")
run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
m = run.load_r2c()
workers = int(sys.argv[1]) if len(sys.argv) > 1 else 8
blocks = int(sys.argv[2]) if len(sys.argv) > 2 else 3
lab = m.load_lab(run.STAGE, run.LAB_SRC)
d, n = 1024, 32768
sess = []
for idx, name in enumerate(run.SESSIONS):
    rng = np.random.default_rng(100 + idx)
    pmf = np.full(d, 1e-9)   # M2-like channel (mass on 0,+-1 only) so that P-M2 is selected, H(delta) ~ 0.82 bit (real-scale)
    pmf[0] = 0.83
    for s_, v in ((1, 0.085),):
        pmf[s_] = v; pmf[-s_] = v
    pmf /= pmf.sum()
    H = float(-(pmf * np.log2(pmf)).sum())
    cdf = np.cumsum(pmf); cdf[-1] = 1
    def draw(size):
        a = rng.integers(0, d, size=size); dl = np.minimum(np.searchsorted(cdf, rng.random(size)), d - 1); return a, (a + dl) % d
    ca, cb = draw(8192); fa, fb = draw((128 * blocks, 256))
    bl = [{"session": name, "local_index": i, "global_block_index": idx * 32 + i, "frame_start": 128 * i, "frame_end": 128 * i + 127,
           "stratum_official": "EVAL_already_decoded", "stratum_task": "previously_decoded_eval"} for i in range(blocks)]
    print(name, "H(delta)=", round(H, 4))
    sess.append(m.SessionInput(name=name, idx=idx, cal_a=ca, cal_b=cb, h_total_bits=H, f_nb=1.27 + 0.0 * idx, frames_a=fa, frames_b=fb, blocks=bl))
cfg = m.RunConfig(n_workers=workers, de_workers=3)
out = run.THIS_DIR / "dry_run_realscale"
t0 = time.time()
res = m.run_pipeline(lab, cfg, sess, out, run.make_tag_fn(), t_start=t0)
print("TOTAL wall", round(time.time() - t0, 1), "s")
print("timing", res.get("timing"), "resources", res.get("resources"))
for l in res["point_labels"]:
    print(l, {s: (round(v["f_realized"], 3), v["taxonomy"]["exact"], v["taxonomy"]["verify_failed"], round(v["design_sum_p_tilde"], 4)) for s, v in res["per_point"][l]["per_session"].items()})
