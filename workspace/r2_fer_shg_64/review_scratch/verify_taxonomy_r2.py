#!/usr/bin/env python3
"""Round-2 Pre-EXECUTE review scratch: verify F1 fix + stop_undetected change (b)
by importing run.py's real _taxonomy_counts/_wilson (no copy-paste, no re-derivation)
and feeding synthetic block dicts covering every status branch. No I/O, no decoder,
no .ttbin read, no real data touched.
"""
import importlib.util
import sys
from pathlib import Path

RUN_PY = Path(r"D:\Code\HD-QKD_Polar_Comparison-nbpolar\workspace\r2_fer_shg_64\run.py")
spec = importlib.util.spec_from_file_location("r2_run_module_under_review", RUN_PY)
mod = importlib.util.module_from_spec(spec)
# Importing must NOT execute main() -- run.py guards with `if __name__ == "__main__"`.
spec.loader.exec_module(mod)
assert hasattr(mod, "_taxonomy_counts") and hasattr(mod, "_wilson")
print("[import] run.py imported without executing main() -- OK")


def scl(exact=False, verify_failed=False, decode_failed=False, undetected=False):
    return {"exact": exact, "verify_failed": verify_failed, "decode_failed": decode_failed, "undetected": undetected}


def blk(status, scl_val=None, fidelity_val=None):
    return {"status": status, "scl": scl_val, "fidelity": fidelity_val, "session": "G2", "global_block_index": 0}


blocks = [
    blk("ok", scl(exact=True)),                                   # 1 ok/exact
    blk("ok", scl(verify_failed=True)),                            # 2 ok/verify_failed
    blk("ok", scl(decode_failed=True)),                             # 3 ok/decode_failed
    blk("ok", scl(undetected=True)),                                # 4 ok/undetected
    blk("STOPPED_FIDELITY_MISMATCH", None),                         # 5 fidelity mismatch, scl=None
    blk("resource_abort_wall_pre_scl", None),                       # 6 abort before SCL call, scl=None
    blk("resource_abort_wall_post_scl", scl(exact=True)),           # 7 F1 regression: must NOT land in exact/D
    blk("resource_abort_wall_post_scl", scl(undetected=True)),      # 8 must NOT land in taxonomy undetected/D,
                                                                     #   but MUST trip stop_undetected
    blk("resource_abort_wall_hard_terminate", None),                # 9 parent-side terminate, scl=None
    blk("resource_abort_total_wall_budget_not_started", None),      # 10 parent-side not-started, scl=None
    blk("error:RuntimeError", None),                                # 11 in-worker exception
]

r = mod._taxonomy_counts(blocks)
print("[_taxonomy_counts]", r)

errs = []

if r["exact"] != 1:
    errs.append(f"exact expected 1 (block#1 only), got {r['exact']}")
if r["verify_failed"] != 1:
    errs.append(f"verify_failed expected 1 (block#2 only), got {r['verify_failed']}")
if r["decode_failed"] != 1:
    errs.append(f"decode_failed expected 1 (block#3 only), got {r['decode_failed']}")
if r["undetected"] != 1:
    errs.append(f"undetected(taxonomy) expected 1 (block#4 only -- ok-status), got {r['undetected']}")
if r["error"] != 1:
    errs.append(f"error expected 1 (block#11), got {r['error']}")
if r["fidelity_mismatch"] != 1:
    errs.append(f"fidelity_mismatch expected 1 (block#5), got {r['fidelity_mismatch']}")

if r["D_valid_denominator"] != 3:
    errs.append(f"D expected 3 (1+1+1, excluding block#7's leaked exact=True), got {r['D_valid_denominator']}")
if r["exact"] == 2:
    errs.append("F1 REGRESSION: block#7 (resource_abort_wall_post_scl, scl.exact=True) leaked into exact/D")
if r["undetected"] == 2:
    errs.append("block#8 (resource_abort_wall_post_scl, scl.undetected=True) leaked into taxonomy undetected")

# resource_abort: blocks whose status contains "resource_abort" substring:
# #6 pre_scl, #7 post_scl(exact), #8 post_scl(undetected), #9 hard_terminate, #10 not_started = 5
if r["resource_abort"] != 5:
    errs.append(f"resource_abort expected 5 (blocks #6,7,8,9,10), got {r['resource_abort']}")

# stop_undetected / undetected_block_ids logic, copied verbatim from run.py main()'s own lines.
n_undetected_total = sum(1 for b in blocks if b.get("scl") and b["scl"]["undetected"])
stop_undetected = bool(n_undetected_total >= 1)
undetected_block_ids = [
    {"session": b["session"], "global_block_index": b["global_block_index"]}
    for b in blocks if b.get("scl") and b["scl"]["undetected"]
]
print(f"[stop_undetected logic] n_undetected_total={n_undetected_total} stop_undetected={stop_undetected} "
      f"undetected_block_ids_len={len(undetected_block_ids)}")
if n_undetected_total != 2:
    errs.append(f"n_undetected_total expected 2 (block#4 ok + block#8 over-budget), got {n_undetected_total}")
if not stop_undetected:
    errs.append("stop_undetected expected True (block#4 and block#8 both undetected)")
if len(undetected_block_ids) != 2:
    errs.append(f"undetected_block_ids expected len 2, got {len(undetected_block_ids)}")

clean_blocks = [blk("ok", scl(exact=True)), blk("ok", scl(verify_failed=True)),
                blk("resource_abort_wall_pre_scl", None)]
n2 = sum(1 for b in clean_blocks if b.get("scl") and b["scl"]["undetected"])
if n2 != 0:
    errs.append(f"clean-set false positive: n_undetected_total={n2}, expected 0")

fidelity_compromised = bool(r["fidelity_mismatch"] >= 1)
if not fidelity_compromised:
    errs.append("fidelity_compromised expected True given 1 STOPPED_FIDELITY_MISMATCH block")

w = mod._wilson(r["verify_failed"] + r["decode_failed"], r["D_valid_denominator"])
print("[_wilson]", w)
if not (0.0 <= w["lower"] <= w["p_hat"] <= w["upper"] <= 1.0):
    errs.append(f"_wilson bounds violated: {w}")

print()
if errs:
    print(f"FAIL ({len(errs)} issue(s)):")
    for e in errs:
        print(" -", e)
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
