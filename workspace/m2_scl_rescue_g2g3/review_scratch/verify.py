import json, glob, os

base = "workspace/m2_scl_rescue_g2g3"
results = json.load(open(f"{base}/results.json", encoding="utf-8"))

parts = {}
for f in sorted(glob.glob(f"{base}/part_*.json")):
    r = json.load(open(f, encoding="utf-8"))
    parts[(r["session"], r["block_index"])] = r

print("n part files:", len(parts))

targets = [("G2",1),("G2",5),("G2",12),("G3",0),("G3",1),("G3",2),("G3",4),("G3",10),("G3",11)]
assert set(parts.keys()) == set(targets), "target set mismatch!"

# cross-check every block in results.json blocks list against part file
rb = {(b["session"], b["block_index"]): b for b in results["blocks"]}
assert set(rb.keys()) == set(targets)
for k in targets:
    if rb[k] != parts[k]:
        print("MISMATCH results.json block vs part file:", k)
    else:
        pass
print("All results.json blocks == part files:", all(rb[k]==parts[k] for k in targets))

# independent recompute of label_exact, crc_pass, tag_pass, accepted, exact, undetected, verify_failed
n_rescued_exact = 0
n_still_failed = 0
n_undetected = 0
n_fidelity_ok = 0
n_fidelity_mismatch = 0
per_source = {"G2": {"failed":0,"total":0}, "G3": {"failed":0,"total":0}}
accepted_eq_check = True
exact_eq_check = True
undetected_isolated = True

for k in targets:
    b = parts[k]
    session = b["session"]
    fid = b["fidelity"]
    if fid["match"]:
        n_fidelity_ok += 1
    else:
        n_fidelity_mismatch += 1
    r = b["rescue"]
    label_exact = r["label_exact"]
    crc_pass = r["crc_pass"]
    tag_pass = r["tag_pass"]
    accepted_recomputed = bool(crc_pass and tag_pass)
    exact_recomputed = bool(accepted_recomputed and label_exact)
    undetected_recomputed = bool(accepted_recomputed and not label_exact)
    verify_failed_recomputed = bool(not accepted_recomputed)

    if accepted_recomputed != r["accepted"]:
        accepted_eq_check = False
        print("accepted mismatch", k)
    if exact_recomputed != r["exact"]:
        exact_eq_check = False
        print("exact mismatch", k)
    if undetected_recomputed != r["undetected"]:
        undetected_isolated = False
        print("undetected mismatch", k)
    # exact should never be counted alongside undetected being true
    if r["exact"] and r["undetected"]:
        print("VIOLATION: exact and undetected both true for", k)

    per_source[session]["total"] += 1
    if exact_recomputed:
        n_rescued_exact += 1
    else:
        n_still_failed += 1
        per_source[session]["failed"] += 1
    if undetected_recomputed:
        n_undetected += 1

print("recomputed: n_fidelity_ok=%d n_fidelity_mismatch=%d n_rescued_exact=%d n_still_failed=%d n_undetected=%d" % (
    n_fidelity_ok, n_fidelity_mismatch, n_rescued_exact, n_still_failed, n_undetected))
print("results.json summary:", results["summary"])
print("per_source still-failed breakdown:", per_source)
print("accepted formula check pass:", accepted_eq_check)
print("exact formula check pass:", exact_eq_check)
print("undetected isolation check pass:", undetected_isolated)

# label_exact truth-object check: compare against alice truth - can't fully redo without re-deriving,
# but check that label_exact is only True when crc_true==crc_hat won't always hold (crc collisions),
# so just report crc_true==crc_hat vs label_exact relationship for sanity.
for k in targets:
    r = parts[k]["rescue"]
    print(k, "label_exact=", r["label_exact"], "crc_true==crc_hat:", r["crc_true"]==r["crc_hat"], "crc_pass:", r["crc_pass"])
