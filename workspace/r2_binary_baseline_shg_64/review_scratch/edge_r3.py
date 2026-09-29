"""Round-3 reviewer edge cases: REAL _run_one_block_entry/_run_scl_block_entry/_run_sessions on
synthetic N=256 data, tempdir only, fake clock, fake CA-SCL decoder (no .so build)."""
import sys, json, hashlib, tempfile
from pathlib import Path
import numpy as np
P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P.parents[1])); sys.path.insert(0, str(P))
import run as d

d.LAYER_N = 256; d.LAYER_N_LOG = 8; d.CODEWORDS_PER_LAYER = 32768 // 256

class Clock:
    t = 0.0
    def __call__(self): return self.t
clock = Clock()

class FakeScl:
    def __init__(self, cost): self.cost = cost; self.calls = 0
    def decode_batch(self, n, k, b, mask, llr):
        clock.t += self.cost; self.calls += 1
        return np.zeros((1, n), dtype=np.int8)

fns = d._load_binary_baseline_functions()
order = fns["polar_weight_order"](256)[::-1]
rng = np.random.default_rng(1)
def frames():
    a = rng.integers(0, 1024, size=(128, 256)).astype(np.int64)
    return a, a.copy()   # b == a -> SC exact
gp = {"sc_margin": 0.05, "_order": order, "layers": [{"layer_idx": i, "ber": 0.01, "k": (200 if i < 5 else 0)} for i in range(10)]}
def blocks(s, off, n=3):
    return [{"session": s, "global_block_index": off + i, "frame_start": 0, "frame_end": 127,
             "stratum_official": "A1_CAL_characterization", "stratum_task": "never_decoded"} for i in range(n)]

def setup(tmp, budget, scl_cost, prepare_cost=1.0, err_session=None):
    d.THIS_DIR = tmp; d.RESULTS_PATH = tmp / "results.json"; d.DRY_RUN_DIR = tmp / "dry_run"
    d._CLOCK = clock; clock.t = 0.0; d.BUDGET_WALL_S_TOTAL = budget
    dec = FakeScl(scl_cost)
    fa, fb = frames()
    for s in ("G2", "G3"):
        d._CTX[s] = dict(frames_a=fa, frames_b=fb, tag_bits=64, scl_decoder=dec)
    d._CTX["_fns"] = fns
    if err_session:
        del d._CTX[err_session]
    def prepare(s):
        clock.t += prepare_cost
        return {"grid_points": [gp]}
    return dec, prepare, (lambda s: blocks(s, 0 if s == "G2" else 32))

def snap(tmp, pat): return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(tmp.glob(pat))}

# E1: real block runners, pass 2 truncated mid-way; part files byte-identical across pass 2
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    dec, prepare, bf = setup(tmp, budget=10.0, scl_cost=0.0005)   # each SCL block ~ 80 cw * 0.0005 = 0.04 s of fake time (* no. of layers usable 5*8=40 cw) 
    # make pass 2 hit the budget after ~2 blocks: 40 cw * cost = 40*0.0005=0.02 per block -> use larger
    dec.cost = 1.0   # 40 s per block -> first pass-2 block starts at t~2 (<10), runs to 42 -> rest not_started
    orig = d._run_scl_block_entry; state = {}
    def wrapped(block, gps, dry_run=False):
        if "before" not in state: state["before"] = snap(tmp, "part_*.json")
        orig(block, gps, dry_run=dry_run)
    d._run_scl_block_entry = wrapped
    out = d._run_sessions(("G2", "G3"), bf, prepare, 0.0)
    d._run_scl_block_entry = orig
    after = snap(tmp, "part_*.json")
    assert state["before"] == after and len(after) == 6, "pass-1 parts changed / count"
    sc = [json.loads(p.read_text()) for p in sorted(tmp.glob("part_*.json"))]
    assert all(r["status"] == "ok" and r["grid"][0]["exact"] and r["grid"][0]["status"] == "ok" for r in sc), sc[0]
    scl = {p.name: json.loads(p.read_text()) for p in sorted(tmp.glob("scl_part_*.json"))}
    st = [r["status"] for r in scl.values()]
    print("scl part statuses:", st, "p2 run/not_started:", out["pass2_blocks_run"], out["pass2_blocks_not_started"])
    assert st.count("ok") == 1 and st.count(d.CA_SCL_NOT_STARTED) == 5
    ns = [r for r in scl.values() if r["status"] == d.CA_SCL_NOT_STARTED][0]
    assert ns["grid"] == [{"sc_margin": 0.05, "status": d.CA_SCL_NOT_STARTED}]
    recs = d._load_all_part_records(tmp); sr = d._load_all_scl_records(tmp)
    res = d.aggregate_results(recs, {}, expected_blocks=6, scl_records=sr)
    assert res["block_accounting"]["consistent"] and res["n_blocks_contributing"] == 6
    pm = res["per_margin"][0]["taxonomy_pooled"]
    assert pm["D_valid_denominator"] == 6 and pm["exact"] == 6
    c = pm["ca_scl_descriptive"]; print("coverage:", c)
    assert c["n_ca_scl_ok_entries"] == 1 and c["n_ca_scl_not_started_entries"] == 5 and abs(c["coverage"] - 1/6) < 1e-12
    print("E1 PASS")

# E2: block-level error in pass 1 (session ctx missing) -> no scl_part for it; accounting error
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    dec, prepare, bf = setup(tmp, budget=1e9, scl_cost=0.001, err_session="G3")
    out = d._run_sessions(("G2", "G3"), bf, prepare, 0.0)
    assert not list(tmp.glob("scl_part_G3_*")) and len(list(tmp.glob("scl_part_G2_*"))) == 3
    res = d.aggregate_results(d._load_all_part_records(tmp), {}, expected_blocks=6, scl_records=d._load_all_scl_records(tmp))
    ba = res["block_accounting"]
    assert ba["n_error"] == 3 and ba["n_blocks_contributing"] == 3 and ba["consistent"] and len(res["error_block_ids"]) == 3
    print("E2 PASS")

# E3: strict '>' boundary
d._CLOCK = lambda: 100.0; d.BUDGET_WALL_S_TOTAL = 100.0
assert not d._total_wall_exceeded(0.0); d._CLOCK = lambda: 100.0001; assert d._total_wall_exceeded(0.0)
print("E3 PASS (strict > boundary)")

# E4: an 'undetected' flag inside an scl record is NOT scanned by aggregate (arm has no tag/accept)
rec = {"session": "G2", "global_block_index": 0, "frame_start": 0, "frame_end": 127, "stratum_official": "A1_CAL_characterization",
       "stratum_task": "never_decoded", "status": "ok", "grid": [{"sc_margin": 0.05, "status": "ok", "exact": True, "undetected": False, "verify_failed": False, "decode_failed": False}]}
sclr = [{"session": "G2", "global_block_index": 0, "grid": [{"sc_margin": 0.05, "status": "ok", "undetected": True, "ca_scl_descriptive": {"n_codewords_applicable": 1, "n_codewords_msg_exact": 0, "all_applicable_msg_exact": False}}]}]
r = d.aggregate_results([rec], {}, expected_blocks=1, scl_records=sclr)
print("E4 stop_undetected with scl-only 'undetected':", r["stop_undetected"])
