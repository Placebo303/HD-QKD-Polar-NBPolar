import json, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # m2_scl_check_g2g3_success
PRED = os.path.join(os.path.dirname(ROOT), "m2_scl_rescue_g2g3")

def load_outcomes(path):
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if d.get("arm") == "B_M2_32f_candidate":
                out[d["block_index"]] = d
    return out

g2_outcomes = load_outcomes(os.path.join(ROOT, "..", "m2_prior_validation", "20260113_SHG_Type2PPLN_3s_g2", "per_block_outcomes.jsonl"))
g3_outcomes = load_outcomes(os.path.join(ROOT, "..", "m2_prior_validation", "20260113_SHG_Type2PPLN_3s_2_g3", "per_block_outcomes.jsonl"))
OUTCOMES = {"G2": g2_outcomes, "G3": g3_outcomes}

FIDELITY_FIELDS = ["outcome", "first_error_coordinate", "first_error_layer", "l1_exact", "hard_l2_exact"]

errors = []
n_preserved_exact = n_broken = n_undetected = n_fidelity_ok = n_fidelity_mismatch = 0
part_files = sorted(glob.glob(os.path.join(ROOT, "part_*.json")))
assert len(part_files) == 19, f"expected 19 part files, found {len(part_files)}"

blocks_seen = []

for pf in part_files:
    d = json.load(open(pf, encoding="utf-8"))
    session = d["session"]
    bi = d["block_index"]
    blocks_seen.append((session, bi))

    # 1. Independent fidelity recompute against frozen per_block_outcomes.jsonl
    frozen_row = OUTCOMES[session].get(bi)
    if frozen_row is None:
        errors.append(f"{session}/{bi}: no frozen per_block_outcomes row found")
        continue
    expected = {k: frozen_row.get(k) for k in FIDELITY_FIELDS}
    actual = d["fidelity"]["actual"]
    my_match = all((expected.get(k) == actual.get(k)) for k in FIDELITY_FIELDS)
    reported_match = d["fidelity"]["match"]
    if my_match != reported_match:
        errors.append(f"{session}/{bi}: fidelity match mismatch: mine={my_match} reported={reported_match}")
    if d["fidelity"]["expected"] != expected:
        errors.append(f"{session}/{bi}: reported 'expected' block differs from my independent frozen-row extraction: {d['fidelity']['expected']} vs {expected}")
    if my_match:
        n_fidelity_ok += 1
    else:
        n_fidelity_mismatch += 1
    # frozen row should say outcome=exact for all 19 targets
    if frozen_row.get("outcome") != "exact":
        errors.append(f"{session}/{bi}: frozen outcome is not 'exact': {frozen_row.get('outcome')}")

    # 2. Independent recompute of label_exact/crc_pass/tag_pass/accepted/exact/undetected/verify_failed
    r = d["rescue"]
    my_crc_pass = (r["crc_hat"] == r["crc_true"])
    my_label_exact = (r["l1_error_symbols_scl"] == 0 and r["l2_error_symbols_scl"] == 0)
    # tag_pass cannot be independently recomputed from part JSON (raw tag values not persisted);
    # cross-check only for internal consistency below.
    reported_tag_pass = r["tag_pass"]
    my_accepted = my_crc_pass and reported_tag_pass
    my_exact = my_accepted and my_label_exact
    my_undetected = my_accepted and (not my_label_exact)
    my_verify_failed = not my_accepted

    if my_crc_pass != r["crc_pass"]:
        errors.append(f"{session}/{bi}: crc_pass mismatch: mine={my_crc_pass} reported={r['crc_pass']}")
    if my_label_exact != r["label_exact"]:
        errors.append(f"{session}/{bi}: label_exact mismatch: mine={my_label_exact} reported={r['label_exact']}")
    if my_accepted != r["accepted"]:
        errors.append(f"{session}/{bi}: accepted mismatch: mine={my_accepted} reported={r['accepted']}")
    if my_exact != r["exact"]:
        errors.append(f"{session}/{bi}: exact mismatch: mine={my_exact} reported={r['exact']}")
    if my_undetected != r["undetected"]:
        errors.append(f"{session}/{bi}: undetected mismatch: mine={my_undetected} reported={r['undetected']}")
    if my_verify_failed != r["verify_failed"]:
        errors.append(f"{session}/{bi}: verify_failed mismatch: mine={my_verify_failed} reported={r['verify_failed']}")

    # 3-way exclusivity/exhaustiveness
    triple = [r["exact"], r["undetected"], r["verify_failed"]]
    if sum(1 for v in triple if v) != 1:
        errors.append(f"{session}/{bi}: exact/undetected/verify_failed not mutually exclusive & exhaustive: {triple}")

    if r["exact"]:
        n_preserved_exact += 1
    if r["verify_failed"]:
        n_broken += 1
    if r["undetected"]:
        n_undetected += 1

    if d["status"] != "ok":
        errors.append(f"{session}/{bi}: status != ok: {d['status']}")

# check target coverage matches TASK_PACKET.md's stated 19-block list
expected_targets = sorted([("G2", i) for i in [0,2,3,4,6,7,8,9,10,11,13]] + [("G3", i) for i in [3,5,6,7,8,9,12,13]])
if sorted(blocks_seen) != expected_targets:
    errors.append(f"target block set mismatch: {sorted(blocks_seen)} vs expected {expected_targets}")

# compare against results.json's summary + fidelity_compromised
results = json.load(open(os.path.join(ROOT, "results.json"), encoding="utf-8"))
summary = results["summary"]
my_summary = {
    "n_targets": len(part_files),
    "n_fidelity_ok": n_fidelity_ok,
    "n_fidelity_mismatch": n_fidelity_mismatch,
    "n_preserved_exact": n_preserved_exact,
    "n_broken": n_broken,
    "n_undetected": n_undetected,
    "n_errors_or_aborts": 0,
}
if my_summary != summary:
    errors.append(f"summary mismatch: mine={my_summary} reported={summary}")

if results.get("fidelity_compromised") != False:
    errors.append(f"fidelity_compromised unexpectedly not False: {results.get('fidelity_compromised')}")
if n_fidelity_mismatch != 0 and results.get("fidelity_compromised") is not True:
    errors.append("fidelity mismatches found but fidelity_compromised not set True in results.json")

print("=== Independent recompute (this packet, 19 blocks) ===")
print("my_summary:", my_summary)
print("reported summary:", summary)
print("errors:", len(errors))
for e in errors:
    print(" -", e)

# f_book CRC delta check
per_session = results["per_session"]
for s in ("G2", "G3"):
    delta = per_session[s]["f_book_with_crc"] - per_session[s]["f_book_no_crc"]
    print(f"f_book CRC delta [{s}] = {delta:.6f}")

print()
print("=== Predecessor cross-check (workspace/m2_scl_rescue_g2g3) ===")
pred_results = json.load(open(os.path.join(PRED, "results.json"), encoding="utf-8"))
print("predecessor summary:", pred_results["summary"])
pred_blocks = {(b["session"], b["block_index"]): b["rescue"] for b in pred_results["blocks"]}
for k, v in sorted(pred_blocks.items()):
    print(" pred", k, "exact=", v["exact"], "undetected=", v["undetected"], "verify_failed=", v["verify_failed"])

print()
print("=== MERGED B-arm 28-block SCL(L=16) tally (predecessor 9 + this packet 19) ===")
cur_blocks = {(b["session"], b["block_index"]): b["rescue"] for b in results["blocks"]}
all_blocks = dict(pred_blocks)
overlap = set(all_blocks.keys()) & set(cur_blocks.keys())
if overlap:
    errors.append(f"target-set overlap between predecessor and this packet: {overlap}")
all_blocks.update(cur_blocks)
assert len(all_blocks) == 28, f"expected 28 merged blocks, got {len(all_blocks)}"

per_sess_tally = {"G2": {"exact": 0, "undetected": 0, "verify_failed": 0, "total": 0},
                   "G3": {"exact": 0, "undetected": 0, "verify_failed": 0, "total": 0}}
for (sess, bi), r in all_blocks.items():
    per_sess_tally[sess]["total"] += 1
    if r["exact"]:
        per_sess_tally[sess]["exact"] += 1
    if r["undetected"]:
        per_sess_tally[sess]["undetected"] += 1
    if r["verify_failed"]:
        per_sess_tally[sess]["verify_failed"] += 1

print("per-session tally:", per_sess_tally)
total_exact = per_sess_tally["G2"]["exact"] + per_sess_tally["G3"]["exact"]
total_undetected = per_sess_tally["G2"]["undetected"] + per_sess_tally["G3"]["undetected"]
total_verify_failed = per_sess_tally["G2"]["verify_failed"] + per_sess_tally["G3"]["verify_failed"]
print(f"TOTAL: exact={total_exact}/28 undetected={total_undetected} verify_failed={total_verify_failed}")

broken_blocks = [(k, v) for k, v in all_blocks.items() if v["verify_failed"]]
print("broken (verify_failed) blocks:", broken_blocks and [k for k, _ in broken_blocks])

print()
print("FINAL_ERROR_COUNT:", len(errors))
sys.exit(1 if errors else 0)
