import sys
from pathlib import Path
P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P.parents[1])); sys.path.insert(0, str(P))
import run as d

def ent(m, status="ok", **kw):
    e = {"sc_margin": m, "status": status, "exact": False, "undetected": False, "verify_failed": False, "decode_failed": False, "accepted": False}
    e.update(kw); return e
def rec(s, i, grid, so="EVAL_already_decoded", st="previously_decoded_eval", status="ok"):
    return {"session": s, "global_block_index": i, "frame_start": 0, "frame_end": 127, "stratum_official": so, "stratum_task": st, "status": status, "grid": grid}

# Case 1: only entry is rss-abort + undetected (accepted, not exact) -> D=0, stop True, ids listed
recs = [rec("G2", 0, [ent(0.05, "resource_abort_rss_post_decode", undetected=True, accepted=True)])]
r = d.aggregate_results(recs, {})
pm = r["per_margin"][0]["taxonomy_pooled"]
assert r["stop_undetected"] and len(r["undetected_ids"]) == 1
assert pm["D_valid_denominator"] == 0 and pm["p_hat"] is None and pm["wilson_95ci"] is None and pm["exact"] == 0
assert pm["undetected"] == 1 and pm["resource_abort"] == 1
# Case 2: rss-abort entry that is exact -> excluded from exact and D, counted resource_abort; no stop
recs = [rec("G2", 0, [ent(0.05, "resource_abort_rss_post_decode", exact=True, accepted=True), ent(0.12, exact=True, accepted=True)])]
r = d.aggregate_results(recs, {})
by = {p["sc_margin"]: p for p in r["per_margin"]}
assert not r["stop_undetected"] and r["undetected_ids"] == []
assert by[0.05]["taxonomy_pooled"]["exact"] == 0 and by[0.05]["taxonomy_pooled"]["D_valid_denominator"] == 0 and by[0.05]["taxonomy_pooled"]["resource_abort"] == 1
assert by[0.12]["taxonomy_pooled"]["exact"] == 1 and by[0.12]["taxonomy_pooled"]["D_valid_denominator"] == 1
# Case 3: undetected ok entry: counted undetected, not in exact/verify_failed/D; wall-abort entry w/o 'undetected' key doesn't crash
recs = [rec("G3", 32, [ent(0.05, undetected=True, accepted=True), {"sc_margin": 0.12, "status": "resource_abort_wall_mid_grid"}])]
r = d.aggregate_results(recs, {})
by = {p["sc_margin"]: p for p in r["per_margin"]}
t = by[0.05]["taxonomy_pooled"]
assert t["undetected"] == 1 and t["D_valid_denominator"] == 0 and r["stop_undetected"]
assert by[0.12]["taxonomy_pooled"]["resource_abort"] == 1 and by[0.12]["taxonomy_pooled"]["undetected"] == 0
# Case 4: block-level error record with partial ok grid entry: error not surfaced in results
recs = [rec("G2", 5, [ent(0.05, exact=True, accepted=True)], status="error:RuntimeError")]
r = d.aggregate_results(recs, {})
print("case4 taxonomy error count:", r["per_margin"][0]["taxonomy_pooled"]["error"], "exact:", r["per_margin"][0]["taxonomy_pooled"]["exact"], "keys:", sorted(r))
print("EDGE PASS")
