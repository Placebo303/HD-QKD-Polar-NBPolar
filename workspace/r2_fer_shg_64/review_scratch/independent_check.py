#!/usr/bin/env python3
"""Independent Pre-RESULT recomputation for r2-fer-shg-64.

Pure stdlib, reads ONLY the 64 part_*.json files (never imports run.py),
recomputes pooled / by_stratum_task / by_stratum_official taxonomy + Wilson
CI with an independently-written formula, cross-checks against results.json,
and runs the fidelity / leakage / execution-consistency checks requested by
the review packet.
"""
import json
import math
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]  # workspace/r2_fer_shg_64
REPO = BASE.parents[1]


def wilson(k, n, z=1.96):
    if n <= 0:
        return None
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return {
        "k": k, "n": n, "p_hat": p,
        "lower": max(0.0, center - half),
        "upper": min(1.0, center + half),
    }


def load_parts():
    parts = []
    for p in sorted(BASE.glob("part_*.json")):
        with open(p, "r", encoding="utf-8") as fh:
            parts.append((p.name, json.load(fh)))
    return parts


def taxonomy(blocks):
    ok = [b for b in blocks if b.get("status") == "ok" and b.get("scl")]
    exact = sum(1 for b in ok if b["scl"]["exact"])
    verify_failed = sum(1 for b in ok if b["scl"]["verify_failed"])
    decode_failed = sum(1 for b in ok if b["scl"]["decode_failed"])
    undetected_ok = sum(1 for b in ok if b["scl"]["undetected"])
    resource_abort = sum(1 for b in blocks if "resource_abort" in str(b.get("status")))
    fidelity_mismatch = sum(1 for b in blocks if b.get("status") == "STOPPED_FIDELITY_MISMATCH")
    errors = sum(1 for b in blocks if str(b.get("status", "")).startswith("error"))
    d = exact + verify_failed + decode_failed
    return dict(
        n_blocks=len(blocks), exact=exact, verify_failed=verify_failed,
        decode_failed=decode_failed, undetected=undetected_ok,
        resource_abort=resource_abort, fidelity_mismatch=fidelity_mismatch,
        error=errors, D=d,
        p_hat=(verify_failed + decode_failed) / d if d else None,
        wilson=wilson(verify_failed + decode_failed, d) if d else None,
    )


def main():
    parts = load_parts()
    print(f"loaded {len(parts)} part files")
    assert len(parts) == 64, f"expected 64 part files, got {len(parts)}"

    blocks = [b for _, b in parts]

    # sanity: unique global_block_index 0..63
    gbis = sorted(b["global_block_index"] for b in blocks)
    assert gbis == list(range(64)), "global_block_index not exactly 0..63"

    # --- 1. pooled / by_stratum_task / by_stratum_official ---
    pooled = taxonomy(blocks)
    print("POOLED:", pooled)

    by_task = {}
    for st in ("never_decoded", "heldout_model_selection", "previously_decoded_eval"):
        by_task[st] = taxonomy([b for b in blocks if b["stratum_task"] == st])
        print(f"TASK[{st}]:", by_task[st])

    by_official = {}
    for st in ("A1_CAL_characterization", "HELDOUT_model_selection", "EVAL_already_decoded"):
        by_official[st] = taxonomy([b for b in blocks if b["stratum_official"] == st])
        print(f"OFFICIAL[{st}]:", by_official[st])

    # per-session by task (28/8/28 split check within task groups per session)
    for sess in ("G2", "G3"):
        for st in ("never_decoded", "heldout_model_selection", "previously_decoded_eval"):
            n = sum(1 for b in blocks if b["session"] == sess and b["stratum_task"] == st)
            print(f"  count session={sess} task={st}: {n}")
    for sess in ("G2", "G3"):
        for st in ("A1_CAL_characterization", "HELDOUT_model_selection", "EVAL_already_decoded"):
            n = sum(1 for b in blocks if b["session"] == sess and b["stratum_official"] == st)
            print(f"  count session={sess} official={st}: {n}")

    # --- 2. threshold check ---
    D = pooled["D"]
    undetected = pooled["undetected"]
    print(f"\nTHRESHOLD: D={D} (>=56? {D>=56}), undetected={undetected} (==0? {undetected==0})")
    rule_verdict = "FER_MEASURED_AT_CONTRACT (would-be, per rule)" if (D >= 56 and undetected == 0) else "INSUFFICIENT or STOP"
    print(f"Independently-derived rule outcome (input only, not final adjudication): {rule_verdict}")

    # --- 3. undetected isolation check ---
    undetected_all_blocks = sum(1 for b in blocks if b.get("scl") and b["scl"]["undetected"])
    print(f"\nundetected scanning ALL blocks (stop_undetected basis): {undetected_all_blocks}")
    # accepted = crc_pass AND tag_pass check, exact = accepted AND label_exact check
    accepted_formula_violations = []
    exact_formula_violations = []
    for name, b in parts:
        scl = b.get("scl")
        if not scl:
            continue
        expected_accepted = bool(scl["crc_pass"] and scl["tag_pass"] and not scl["decode_failed"])
        if scl["accepted"] != expected_accepted:
            accepted_formula_violations.append(name)
        expected_exact = bool(scl["accepted"] and scl["label_exact"])
        if scl["exact"] != expected_exact:
            exact_formula_violations.append(name)
        expected_undetected = bool(scl["accepted"] and not scl["label_exact"])
        if scl["undetected"] != expected_undetected:
            print(f"  UNDETECTED FORMULA VIOLATION in {name}")
        expected_verify_failed = bool((not scl["accepted"]) and not scl["decode_failed"])
        if scl["verify_failed"] != expected_verify_failed:
            print(f"  VERIFY_FAILED FORMULA VIOLATION in {name}")
    print(f"accepted-formula violations: {accepted_formula_violations}")
    print(f"exact-formula violations: {exact_formula_violations}")

    # never merged check
    for name, b in parts:
        scl = b.get("scl")
        if scl and scl["undetected"] and scl["exact"]:
            print(f"  CRITICAL: {name} has BOTH undetected=True and exact=True")

    # --- 4. fidelity: 28 EVAL blocks ---
    eval_blocks = [b for b in blocks if b["stratum_task"] == "previously_decoded_eval"]
    print(f"\nEVAL blocks count: {len(eval_blocks)} (expect 28)")
    fidelity_mismatches = []
    for b in eval_blocks:
        fid = b.get("fidelity")
        if fid is None:
            fidelity_mismatches.append((b["session"], b["global_block_index"], "NO_FIDELITY_RECORD"))
            continue
        exp = fid["expected"]
        act = fid["actual"]
        for k in ("outcome", "first_error_coordinate", "first_error_layer", "l1_exact", "hard_l2_exact"):
            ev = exp.get(k)
            av = act.get(k)
            eq = (ev is None and av is None) or (ev == av)
            if not eq:
                fidelity_mismatches.append((b["session"], b["global_block_index"], k, ev, av))
        if fid.get("match") is not True:
            fidelity_mismatches.append((b["session"], b["global_block_index"], "match_field_false"))
    print(f"fidelity mismatches found: {fidelity_mismatches if fidelity_mismatches else 'NONE'}")

    # cross-check against predecessor descriptive results (28 blocks total across two dirs)
    pred_dirs = [
        REPO / "workspace" / "m2_scl_rescue_g2g3",
        REPO / "workspace" / "m2_scl_check_g2g3_success",
    ]
    pred_by_key = {}
    for d in pred_dirs:
        for p in sorted(d.glob("part_*.json")):
            with open(p, "r", encoding="utf-8") as fh:
                pb = json.load(fh)
            key = (pb.get("session"), pb.get("block_index") if "block_index" in pb else pb.get("eval_original_index"))
            pred_by_key[(p.name, d.name)] = pb
    print(f"\npredecessor part files loaded: {len(pred_by_key)} (expect 28: 9+19)")

    # Build lookup by (session, eval_original_index) -> outcome fields from predecessor,
    # matching by scanning each predecessor file's own recorded block_index/session.
    pred_lookup = {}
    for (fname, dname), pb in pred_by_key.items():
        sess = pb.get("session")
        # predecessor files use 'block_index' as the EVAL-native 0..13 index typically
        bidx = pb.get("block_index", pb.get("eval_original_index"))
        pred_lookup[(sess, bidx)] = (fname, dname, pb)

    print(f"predecessor lookup keys sample: {list(pred_lookup.keys())[:5]}")

    consistent = 0
    inconsistent = []
    checked = 0
    for b in eval_blocks:
        sess = b["session"]
        eoi = b["eval_original_index"]
        key = (sess, eoi)
        if key not in pred_lookup:
            inconsistent.append((sess, eoi, "NO_PREDECESSOR_RECORD_FOUND"))
            continue
        fname, dname, pb = pred_lookup[key]
        checked += 1
        pred_scl = pb.get("rescue") or pb.get("scl") or pb
        cur_scl = b.get("scl")
        # Compare exact/verify_failed/undetected/label_exact/crc_pass/tag_pass if present
        fields_to_cmp = ["exact", "verify_failed", "undetected", "label_exact", "crc_pass", "tag_pass"]
        mism = []
        for f in fields_to_cmp:
            pv = pred_scl.get(f) if isinstance(pred_scl, dict) else None
            cv = cur_scl.get(f) if cur_scl else None
            if pv is not None and pv != cv:
                mism.append((f, pv, cv))
        if mism:
            inconsistent.append((sess, eoi, fname, dname, mism))
        else:
            consistent += 1
    print(f"\nEVAL SCL cross-check vs predecessor: checked={checked}, consistent={consistent}, inconsistent={len(inconsistent)}")
    for row in inconsistent:
        print("  INCONSISTENT:", row)

    # --- 5. block framing / stratum / 128-frame / no CAL32 crossing ---
    CAL32_START, CAL32_END = 1024, 1055
    framing_issues = []
    for b in blocks:
        fs, fe = b["frame_start"], b["frame_end"]
        if fe - fs + 1 != 128:
            framing_issues.append((b["session"], b["global_block_index"], "not_128_frames", fs, fe))
        # crosses CAL32?
        if fs <= CAL32_END and fe >= CAL32_START:
            framing_issues.append((b["session"], b["global_block_index"], "crosses_CAL32", fs, fe))
    print(f"\nframing issues: {framing_issues if framing_issues else 'NONE'}")

    # --- 6. leakage recompute ---
    with open(BASE / "results.json", "r", encoding="utf-8") as fh:
        results = json.load(fh)
    kdb_no_crc_expected = 5 * (319 + 6492) + 64
    kdb_with_crc_expected = kdb_no_crc_expected + 16
    print(f"\nkdb_no_crc expected={kdb_no_crc_expected} (5*(319+6492)+64)")
    print(f"kdb_with_crc expected={kdb_with_crc_expected}")
    for sess in ("G2", "G3"):
        ps = results["per_session"][sess]
        h = ps["h_total_bits"]
        kdb_no_crc = ps["kdb_no_crc"]
        kdb_with_crc = ps["kdb_with_crc"]
        f_no = ps["f_book_no_crc_computed"]
        f_with = ps["f_book_with_crc_computed"]
        n = 32768
        recompute_f_no = kdb_no_crc / (h * n)
        recompute_f_with = kdb_with_crc / (h * n)
        print(f"  session {sess}: H_total={h:.6f} kdb_no_crc={kdb_no_crc} kdb_with_crc={kdb_with_crc} "
              f"f_no_crc(reported)={f_no:.6f} f_no_crc(recomputed)={recompute_f_no:.6f} "
              f"f_with_crc(reported)={f_with:.6f} f_with_crc(recomputed)={recompute_f_with:.6f}")

    # --- 7. session-level exact counts ---
    for sess in ("G2", "G3"):
        sess_blocks = [b for b in blocks if b["session"] == sess]
        tx = taxonomy(sess_blocks)
        print(f"\nsession {sess}: n={len(sess_blocks)} exact={tx['exact']} verify_failed={tx['verify_failed']} "
              f"decode_failed={tx['decode_failed']} undetected={tx['undetected']} D={tx['D']}")

    # --- 8. execution consistency (status, wall, RSS) ---
    non_ok = [b for b in blocks if b["status"] != "ok"]
    print(f"\nnon-ok status blocks: {len(non_ok)} (expect 0)")
    wall_totals = [b["resources"]["wall_total_s"] for b in blocks if b["resources"].get("wall_total_s") is not None]
    rss_peaks = [b["resources"]["rss_gib_peak_advisory"] for b in blocks if b["resources"].get("rss_gib_peak_advisory") is not None]
    over_wall = [b for b in blocks if b["resources"].get("wall_total_s", 0) > 1200.0]
    over_rss = [b for b in blocks if (b["resources"].get("rss_gib_peak_advisory") or 0) > 2.0]
    print(f"wall_total_s: min={min(wall_totals):.2f} max={max(wall_totals):.2f}")
    print(f"rss_gib_peak_advisory: min={min(rss_peaks):.4f} max={max(rss_peaks):.4f}")
    print(f"blocks over 1200s wall: {len(over_wall)}; blocks over 2GiB RSS: {len(over_rss)}")
    total_wall = results["timing"]["wall_s_total"]
    print(f"total wall_s (results.json timing): {total_wall:.1f} (<=10800? {total_wall <= 10800})")

    # --- 9. compare pooled/by_task/by_official against results.json's own reported values ---
    def cmp_tax(label, mine, theirs):
        keys = ["exact", "verify_failed", "decode_failed", "undetected", "resource_abort", "fidelity_mismatch"]
        diffs = []
        for k in keys:
            tk = "D_valid_denominator" if False else k
            mv = mine.get(k)
            tv = theirs.get(k if k in theirs else k)
            if mv != tv:
                diffs.append((k, mv, tv))
        if mine.get("D") != theirs.get("D_valid_denominator"):
            diffs.append(("D", mine.get("D"), theirs.get("D_valid_denominator")))
        print(f"  cmp[{label}] diffs: {diffs if diffs else 'NONE (match)'}")

    print("\n=== cross-check mine vs results.json ===")
    cmp_tax("pooled", pooled, results["taxonomy_pooled"])
    for st in ("never_decoded", "heldout_model_selection", "previously_decoded_eval"):
        cmp_tax(f"task/{st}", by_task[st], results["taxonomy_by_stratum_task"][st])
    for st in ("A1_CAL_characterization", "HELDOUT_model_selection", "EVAL_already_decoded"):
        cmp_tax(f"official/{st}", by_official[st], results["taxonomy_by_stratum_official"][st])

    print(f"\nresults.json stop_undetected={results['stop_undetected']} (mine all-block undetected count={undetected_all_blocks})")
    print(f"results.json fidelity_compromised={results['fidelity_compromised']}")

    print("\nDONE INDEPENDENT CHECK")


if __name__ == "__main__":
    main()
