"""Synthetic smoke for run.py (no raw data, no results.json/part writes).
Run in WSL: /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python _smoke_synthetic.py
Checks: (1) f_book accounting for K_total=6442; (2) native L=32 call path via
run._scl_call on a small-N synthetic block (taxonomy fields, undetected isolation);
(3) startup guards refuse when results.json / a part file exists (redirected to a
scratch dir under this directory)."""
import importlib
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as drv  # noqa: E402

REPO = drv.REPO_ROOT
mod = drv._load_mod()
chain, (scl_joint_mod, native_mod) = drv._load_scl_joint(mod)
print("native backend:", native_mod.native_backend_info())

# (1) f accounting
for name, H in (("G2", 0.8168138204133305), ("G3", 0.8214782076249098)):
    no = int(chain.disclosed_bits_per_coordinate * (drv.K1_R2B + drv.K2_R2B) + chain.tag_bits)
    wc = no + drv.CRC_BITS_EXTRA
    print(f"{name}: kdb_no_crc={no} kdb_with_crc={wc} f_no={no/(H*32768):.6f} f_crc={wc/(H*32768):.6f}")
print("K_total,k1,k2 =", drv.K_TOTAL, drv.K1_R2B, drv.K2_R2B, "dbpc", chain.disclosed_bits_per_coordinate, "tag", chain.tag_bits)

# (2) native call path through run._scl_call
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as tl  # noqa: E402
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import apply_explicit_floor  # noqa: E402

q = 1024
raw = np.zeros(q)
raw[0], raw[1], raw[q - 1] = 0.7562, 0.0018, 0.2419
pmf = apply_explicit_floor(raw, 1e-15, reason="smoke")
table = pmf[(np.arange(q)[None, :] - np.arange(q)[:, None]) % q]
p1, p2 = tl.layer_metric_tables(table)
field = chain.make_gf32()
alpha = int(chain.alpha)
polar_fn = mod._bind_g2_polar(chain.polar_transform, field, alpha)
n = 1024
k1, k2 = 16, 250
rng = np.random.default_rng(20260929)
x = rng.integers(0, q, size=n).astype(np.int64)
delta = rng.choice(q, size=n, p=table[0]).astype(np.int64)
bob = (x + delta) % q
d1 = np.sort(rng.choice(n, size=k1, replace=False))
d2 = np.sort(rng.choice(n, size=k2, replace=False))
ctx = dict(chain=chain, scl_joint_mod=scl_joint_mod, native_mod=native_mod, l1_order=d1, l2_order=d2,
           k1=k1, k2=k2, p1_table=p1, p2_table=p2, field=field, alpha=alpha, polar_fn=polar_fn,
           tag_master=drv.R2_TAG_MASTER, n=n)
# l1_order/l2_order are sliced [:k], so pass the already-selected positions
res = drv._scl_call(mod, ctx, {"global_block_index": 5}, x, bob)
assert res["list_width_L"] == 32 and res["top_m_requested"] == 4
assert res["k1_scl"] == k1 and res["k2_scl"] == k2
assert res["native_backend"]["backend"] in ("rust", "cpp")
assert "rust" in res["metric_provenance"]["engine"] or "native" in res["metric_provenance"]["engine"]
assert res["exact"] + res["verify_failed"] + res["decode_failed"] + res["undetected"] == 1
print("scl_call ok:", {k: res[k] for k in ("exact", "verify_failed", "undetected", "decode_failed", "crc_pass", "tag_pass")},
      res["metric_provenance"]["engine"])

# (3) guards, redirected to a scratch dir inside this packet dir
scratch = HERE / "_smoke_guard_tmp"
scratch.mkdir(exist_ok=True)
try:
    drv.RESULTS_PATH = scratch / "results.json"
    drv.THIS_DIR = scratch
    (scratch / "results.json").write_text("{}")
    try:
        drv.main()
        raise SystemExit("GUARD FAIL: main ran with results.json present")
    except SystemExit as e:
        assert e.code == 2, e.code
    print("guard results.json: refused (exit 2)")
    (scratch / "results.json").unlink()
    (scratch / "part_G2_00.json").write_text("{}")
    try:
        drv.main()
        raise SystemExit("GUARD FAIL: main ran with part file present")
    except SystemExit as e:
        assert e.code == 2, e.code
    print("guard part file: refused (exit 2)")
finally:
    shutil.rmtree(scratch, ignore_errors=True)

# total-wall mechanism
drv._CLOCK = lambda: 7200.0
assert not drv._total_wall_exceeded(0.0)
drv._CLOCK = lambda: 7200.001
assert drv._total_wall_exceeded(0.0)
print("total_wall_exceeded edge ok")
print("SMOKE PASS")
