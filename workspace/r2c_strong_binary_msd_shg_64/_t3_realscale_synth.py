"""SYNTHETIC full-scale run (d=1024, N=32768, L=16, default RunConfig: M_design=1024, genie 4096 frames) with 2 synthetic
sessions x BLOCKS blocks (M2-like channel: pmf 0/+-1 = .83/.085/.085, tail floor 1e-9 in the SAMPLED channel; CAL32-like
8192 symbols; H(delta) ~ 0.83 bit).  No real data.  Output -> dry_run_realscale/ (gitignored).
Usage: python _t3_realscale_synth.py [workers] [blocks] [de_workers]"""
import sys, time, importlib.util
import numpy as np
HERE = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/r2c_strong_binary_msd_shg_64"
spec = importlib.util.spec_from_file_location("run_", HERE + "/run.py")
run = importlib.util.module_from_spec(spec); spec.loader.exec_module(run)
m = run.load_r2c()
workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
blocks = int(sys.argv[2]) if len(sys.argv) > 2 else 8
de_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 2
lab = m.load_lab(run.STAGE, run.LAB_SRC)
d, n = 1024, 32768
sess = []
for idx, name in enumerate(run.SESSIONS):
    rng = np.random.default_rng(100 + idx)
    pmf = np.full(d, 1e-9)
    pmf[0] = 0.83; pmf[1] = 0.085; pmf[-1] = 0.085
    pmf /= pmf.sum()
    H = float(-(pmf * np.log2(pmf)).sum())
    cdf = np.cumsum(pmf); cdf[-1] = 1
    def draw(size):
        a = rng.integers(0, d, size=size); dl = np.minimum(np.searchsorted(cdf, rng.random(size)), d - 1); return a, (a + dl) % d
    ca, cb = draw(8192); fa, fb = draw((128 * blocks, 256))
    bl = [{"session": name, "local_index": i, "global_block_index": idx * 32 + i, "frame_start": 128 * i, "frame_end": 128 * i + 127,
           "stratum_official": "EVAL_already_decoded", "stratum_task": "previously_decoded_eval"} for i in range(blocks)]
    print(name, "H(delta)=", round(H, 4), flush=True)
    sess.append(m.SessionInput(name=name, idx=idx, cal_a=ca, cal_b=cb, h_total_bits=H, f_nb=1.27, frames_a=fa, frames_b=fb, blocks=bl))
cfg = m.RunConfig(n_workers=workers, de_workers=de_workers)
out = run.THIS_DIR / "dry_run_realscale"
t0 = time.time()
res = m.run_pipeline(lab, cfg, sess, out, run.make_tag_fn(), t_start=t0)
print("TOTAL wall", round(time.time() - t0, 1), "s")
print("timing", res.get("timing"), "resources", res.get("resources"))
for l in res["point_labels"]:
    for s, v in res["per_point"][l]["per_session"].items():
        t = v["taxonomy"]
        print(l, s, "f_real", round(v["f_realized"], 4), "exact", t["exact"], "verify_failed", t["verify_failed"], "undetected", t["undetected"],
              "design_sum_p~", round(v["design_sum_p_tilde"], 4), "mu", np.round(v["mu"], 4).tolist(), "ks", list(map(int, v["ks"])))
    print(l, "measured_layer_errors", res["per_point"][l]["measured_layer_errors"])
