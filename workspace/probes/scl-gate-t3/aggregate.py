"""Aggregate part_*.json (written by run.py's sc/scl workers) into results.json.

Tier-X: this script only merges already-computed per-block records; it adds
no new decode, no threshold, no pass/fail verdict. Aggregation key is
(point, arm, L) and must be unique -- asserted below. Writes only
results.json under this probe's own root.
"""
from __future__ import annotations

import glob
import json
import os

PROBE_DIR = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/scl-gate-t3"
OUT_KEYS = ("exact", "undetected", "verify_failed", "decode_failed", "resource_abort")
DISCLOSED_BITS_PER_COORDINATE = 5
TAG_BITS = 64
CRC_BITS = 16


def totals_from_records(records, key_fn):
    out = dict.fromkeys(OUT_KEYS, 0)
    for r in records:
        out[key_fn(r)] += 1
    return out


def sc_outcome(r):
    return r["outcome"]


def scl_outcome(r):
    return r["outcome"]


def flips(sc_records, scl_records):
    """Per-(seed,block) pairing: SC fail->SCL success, SC success->SCL fail.

    'success' == arm's own 'exact' bucket (accepted AND label-correct)."""
    sc_by_key = {(r["seed"], r["block"]): r["exact"] for r in sc_records}
    scl_by_key = {(r["seed"], r["block"]): r["exact"] for r in scl_records}
    common = sorted(set(sc_by_key) & set(scl_by_key))
    sc_fail_scl_ok = sum(1 for k in common if (not sc_by_key[k]) and scl_by_key[k])
    sc_ok_scl_fail = sum(1 for k in common if sc_by_key[k] and (not scl_by_key[k]))
    return {"paired_blocks": len(common), "sc_fail_scl_success": sc_fail_scl_ok,
            "sc_success_scl_fail": sc_ok_scl_fail}


def main():
    out_path = PROBE_DIR + "/results.json"
    if os.path.exists(out_path):
        print("REFUSE: results.json already exists; not overwriting")
        return 2

    design = json.load(open(PROBE_DIR + "/design.json"))
    sc_path = PROBE_DIR + "/part_SC.json"
    if not os.path.exists(sc_path):
        print("MISSING part_SC.json -- aggregate incomplete, not writing results.json yet")
        return 1
    sc_part = json.load(open(sc_path))

    scl_paths = sorted(glob.glob(PROBE_DIR + "/part_SCL_*_L*.json"))
    scl_parts = [json.load(open(p)) for p in scl_paths]

    # Uniqueness of (point, L) aggregation key.
    keys = [(p["point"], p["L"]) for p in scl_parts]
    assert len(keys) == len(set(keys)), f"duplicate (point,L) aggregation keys: {keys}"

    rows = []
    all_flips = {}
    for part in scl_parts:
        pkey, L = part["point"], part["L"]
        scl_recs = part["scl_records"]
        or_recs = part["oracle_records"]
        sc_recs = sc_part["records"].get(pkey, [])
        scl_totals = totals_from_records(scl_recs, scl_outcome)
        or_totals = totals_from_records(or_recs, scl_outcome)
        sc_totals = totals_from_records(sc_recs, sc_outcome)
        fl = flips(sc_recs, scl_recs)
        all_flips[f"{pkey}_L{L}"] = fl
        rows.append({
            "point": pkey, "L": L, "top_m": part.get("top_m"),
            "part_status": part["status"], "part_wall_s": part["wall_s"],
            "part_peak_rss_bytes": part["peak_rss_bytes"],
            "n_scl_blocks": len(scl_recs), "n_oracle_blocks": len(or_recs),
            "n_sc_blocks": len(sc_recs),
            "sc_totals": sc_totals,
            "scl_totals": scl_totals,
            "oracle_totals": or_totals,
            "flips_vs_sc": fl,
        })

    pt_info = {k: {kk: vv for kk, vv in v.items() if kk not in ("d1", "d2")}
               for k, v in design["points"].items()}
    for k, pt in pt_info.items():
        k1, k2 = pt["k1"], pt["k2"]
        disclosed_no_crc = DISCLOSED_BITS_PER_COORDINATE * (k1 + k2)
        disclosed_with_crc = disclosed_no_crc + CRC_BITS
        pt["disclosed_bits_no_crc"] = disclosed_no_crc
        pt["disclosed_bits_with_crc"] = disclosed_with_crc
        pt["f_book_no_crc"] = disclosed_no_crc / design["HN"]
        pt["f_book_with_crc"] = disclosed_with_crc / design["HN"]
        pt["key_dependent_bits"] = disclosed_with_crc + TAG_BITS

    results = {
        "probe_id": "scl-gate-t3", "tier": "X", "status": "ok",
        "design_status": design["status"], "design_sanity": design["sanity"],
        "H": design["H"], "HN": design["HN"],
        "points": pt_info,
        "sc_part_status": sc_part["status"], "sc_part_wall_s": sc_part["wall_s"],
        "sc_part_peak_rss_bytes": sc_part["peak_rss_bytes"],
        "sc_part_stop_reasons": sc_part.get("stop_reasons", []),
        "rows": rows,
        "scl_part_files": scl_paths,
        "claims": "Tier-X non-claim planning evidence only: no threshold, no "
                  "pass/fail verdict, no candidate/accepted token, no attempt "
                  "accounting, no real/artifact data, writes only under "
                  "workspace/probes/scl-gate-t3/",
    }
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=2)
    print("WROTE", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
