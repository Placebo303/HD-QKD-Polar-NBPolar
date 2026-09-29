"""Synthetic smoke for run.py (no raw data; single process, N=1024; writes only to a scratch dir).
WSL: /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python _smoke_synthetic.py
Checks: config table/K; native thread override; _scl_call with per-config k1/k2 via _run_task +
_launch_all (n_workers=1); startup guard; total-wall not_started path; wall boundary edge."""
import shutil
import sys
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as drv  # noqa: E402

mod = drv._load_mod()
chain, (scl_joint_mod, native_mod) = drv._load_scl_joint(mod)
print("native backend:", native_mod.native_backend_info(), "| _default_threads() ->", native_mod._default_threads())
assert native_mod._default_threads() == 2

# (1) config table
for H, name in ((0.8168138204133305, "G2"),):
    for c in drv.CONFIGS:
        fb = drv.f_book(chain, H, 32768, c["k_total"])
        print(c["cfg"], c["k_total"], c["k1"], c["k2"], f"f_no={fb['f_book_no_crc']:.6f} f_crc={fb['f_book_with_crc']:.6f}")
assert len(drv.CONFIGS) == 6 and all(c["k1"] + c["k2"] == c["k_total"] for c in drv.CONFIGS)
assert (drv.CONFIGS[1]["k_total"], drv.CONFIGS[1]["k1"]) == (drv.CONFIGS[0]["k_total"], round(0.0380 * drv.CONFIGS[0]["k_total"]))

# (2) synthetic ctx
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as tl  # noqa: E402
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import apply_explicit_floor  # noqa: E402

q, n = 1024, 1024
raw = np.zeros(q)
raw[0], raw[1], raw[q - 1] = 0.7562, 0.0018, 0.2419
pmf = apply_explicit_floor(raw, 1e-15, reason="smoke")
table = pmf[(np.arange(q)[None, :] - np.arange(q)[:, None]) % q]
p1, p2 = tl.layer_metric_tables(table)
field = chain.make_gf32()
alpha = int(chain.alpha)
rng = np.random.default_rng(20260929)
nb = 3
fa = rng.integers(0, q, size=(nb, n)).astype(np.int64)
fb_ = (fa + rng.choice(q, size=(nb, n), p=table[0])) % q
ctx = dict(chain=chain, scl_joint_mod=scl_joint_mod, native_mod=native_mod,
           l1_order=np.sort(rng.choice(n, 64, replace=False)), l2_order=np.sort(rng.choice(n, 400, replace=False)),
           frames_a=fa, frames_b=fb_, p1_table=p1, p2_table=p2, field=field, alpha=alpha,
           polar_fn=mod._bind_g2_polar(chain.polar_transform, field, alpha), tag_master=drv.R2D_TAG_MASTER,
           eval_seed=drv.R2D_EVAL_SEED, n=n)
drv._CTX["_mod"], drv._CTX["G2"] = mod, ctx

scratch = HERE / "_smoke_tmp"
shutil.rmtree(scratch, ignore_errors=True)
scratch.mkdir()
drv.THIS_DIR = scratch
cfgs = [dict(cfg="tA", f_target=1.0, k1_share=0.1, k_total=200, k1=10, k2=190),
        dict(cfg="tB", f_target=1.0, k1_share=0.1, k_total=300, k1=30, k2=270)]
blocks = [dict(session="G2", local_index=i, global_block_index=i, frame_start=i, frame_end=i,
               stratum_official="x", stratum_task="y", eval_original_index=None) for i in range(nb)]
tasks = [dict(config=c, block=b) for c in cfgs for b in blocks]
try:
    drv._launch_all(tasks, drv._CLOCK(), n_workers=1)
    for c in cfgs:
        for b in blocks:
            r = json.load(open(drv._part_path(c["cfg"], b["global_block_index"])))
            s = r["scl"]
            assert r["status"] == "ok", r
            assert s["k1_scl"] == c["k1"] and s["k2_scl"] == c["k2"] and r["resources"]["native_threads"] == 2
            assert s["exact"] + s["verify_failed"] + s["decode_failed"] + s["undetected"] == 1
    t = drv._taxonomy([json.load(open(drv._part_path("tA", b["global_block_index"]))) for b in blocks])
    print("taxonomy tA:", {k: t[k] for k in ("exact", "verify_failed", "decode_failed", "undetected", "D_valid_denominator")})
    print("launch/worker/part path ok; wall of last task:", r["resources"]["wall_total_s"])

    # total-wall path: budget 0 -> everything not_started
    for p in scratch.glob("part_*.json"):
        p.unlink()
    drv.BUDGET_WALL_S_TOTAL = -1.0
    drv._launch_all(tasks, drv._CLOCK(), n_workers=1)
    st = [json.load(open(drv._part_path(c["cfg"], b["global_block_index"])))["status"] for c in cfgs for b in blocks]
    assert set(st) == {"not_started_total_wall_budget"}, st
    print("total-wall not_started path ok")
    drv.BUDGET_WALL_S_TOTAL = 12600.0

    # startup guard
    drv.RESULTS_PATH = scratch / "results.json"
    try:
        drv.main()
        raise SystemExit("GUARD FAIL")
    except SystemExit as e:
        assert e.code == 2, e.code
    print("guard (part files present): refused (exit 2)")
finally:
    shutil.rmtree(scratch, ignore_errors=True)

drv._CLOCK = lambda: 7200.0
assert not drv._total_wall_exceeded(0.0)
drv._CLOCK = lambda: 7200.001
assert drv._total_wall_exceeded(0.0)
print("total_wall edge ok\nSMOKE PASS")
