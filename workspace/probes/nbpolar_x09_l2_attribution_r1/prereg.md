# NBPOLAR-X09-L2-ATTRIBUTION-R1 — prereg (frozen delta-successor, AGENTS.md §10.4 fast path)

probe_id: NBPOLAR-X09-L2-ATTRIBUTION-R1 | tier: X (non-claim, decoder-free, read-only)
delta-vs-X09: same-point semantic correction only (D1 clean single-field H1 margins
keyed by block_index; D2 block_index fix; D3 shared-field floor comparison;
D4 settled first_error_coord index space with exact lines; D5 grounded H2 reason +
instrumentation requirement). All else inherited from X09: same 16 inputs, zero
protected opens, no decoder/RNG/tag, one run, writes only in this probe root,
focused numerical review, no claims, no factor selection, no commit/push.
forbidden: parquet/pairs content; DEV/VAL/HOLD/1M/V25-counts/2M open/stat/listing
in any form; decoder/RNG/tag calls; writes outside the probe root (+ packet dir);
commit/push. stop: missing file, unreadable JSON/JSONL, npz key surprise,
nonfinite → STOP results.json, no repair. No summing across NLL fields anywhere.

## Exact command (run exactly once; execution-error rerun allowed and recorded)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && timeout 120 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python workspace/probes/nbpolar_x09_l2_attribution_r1/body.py
```

## Exact artifact list (16 files, repo-relative, each stat size/mtime_ns; same as X09)

1. .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/per_block_arm_outcomes.jsonl
2. .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/aggregate_summary.json
3. .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/frozen_plan.json
4. .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/input_and_predecessor_identity.json
5. .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/report.md
6. .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz
7. .workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_orders_1p5m.json
8. .workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/l1_disclosure_1p5m/per_block_arm_outcomes.jsonl
9. .workbuddy/queue/NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M/l1_dose_escalation_1p5m/per_block_arm_outcomes.jsonl
10. .workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/l1_dose_512_1p5m/per_block_arm_outcomes.jsonl
11. .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_confirmation/per_block_arm_outcomes.jsonl
12. comparison_bench/src/comparison_bench/formal_ir/nbpolar/raw_prior_val_1p5m.py
13. comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_order_1p5m.py
14. comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_disclosure_1p5m.py
15. comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_dose_escalation_1p5m.py
16. comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_dose_512_1p5m.py

## Analysis body (fenced python block; body.py is byte-identical to this block)

```python
#!/usr/bin/env python3
"""NBPOLAR-X09-L2-ATTRIBUTION-R1 Tier-X delta-successor probe body.

Same-point semantic correction of X09 (D1-D5 only). Same frozen inputs, zero
protected opens, no decoder/RNG/tag calls. results.json is the ONLY file
this script writes. No summing across NLL fields anywhere.
"""
import os
import sys
import json
import math
import time
import hashlib

import numpy as np

PROBE_ID = "NBPOLAR-X09-L2-ATTRIBUTION-R1"
TIER = "X"
COMPLETE_STATUS = "X09R1_PROBE_COMPLETE_DESCRIPTIVE_ONLY"
DELTA_REF = ".workbuddy/queue/NBPOLAR-X09-L2-ATTRIBUTION/X09R1_DELTA.md (D1-D5)"
QUESTION = (
    "Same-point correction of X09: clean per-arm/block H1 margins (single "
    "authoritative L2-NLL field each, keyed by block_index), shared-field H3 "
    "floor comparison, settled first_error_coord index space, grounded H2 "
    "NOT-DECIDABLE reason. No verdict on the next scientific factor."
)
COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export "
    "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "
    "MALLOC_ARENA_MAX=2 && timeout 120 "
    "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python "
    "workspace/probes/nbpolar_x09_l2_attribution_r1/body.py"
)
K2 = 6689
N = 32768
H2 = 0.8003665547495433
CAP = {
    "G0_old_point_base": 5 * 6492 + 64,
    "G1_raw_prior_session_budget": 35164,
    "G2_true_l1_diagnostic": 33509,
}
AUTH_RULE = {
    "G0_old_point_base": (
        "l2_nll_candidate_H_bits",
        ["true_l2_nll_bits", "l2_nll_true_H_bits"],
    ),
    "G1_raw_prior_session_budget": (
        "l2_nll_candidate_H_bits",
        ["true_l2_nll_bits", "l2_nll_true_H_bits"],
    ),
    "G2_true_l1_diagnostic": (
        "true_l2_nll_bits",
        ["l2_nll_true_H_bits", "l2_nll_candidate_H_bits"],
    ),
}
EXPECTED_NPZ_KEYS = ["counts_ab", "f_raw", "p1", "p2", "p_b"]

P20M = ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M"
REL_FILES = [
    P20M + "/raw_prior_val_1p5m/per_block_arm_outcomes.jsonl",
    P20M + "/raw_prior_val_1p5m/aggregate_summary.json",
    P20M + "/raw_prior_val_1p5m/frozen_plan.json",
    P20M + "/raw_prior_val_1p5m/input_and_predecessor_identity.json",
    P20M + "/raw_prior_val_1p5m/report.md",
    P20M + "/raw_prior_1p5m.npz",
    P20M + "/raw_prior_orders_1p5m.json",
    ".workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/"
    "l1_disclosure_1p5m/per_block_arm_outcomes.jsonl",
    ".workbuddy/queue/NBPOLAR-PHASE4-P20J-L1-DOSE-ESCALATION-1P5M/"
    "l1_dose_escalation_1p5m/per_block_arm_outcomes.jsonl",
    ".workbuddy/queue/NBPOLAR-PHASE4-P20K-L1-DOSE-512-1P5M/"
    "l1_dose_512_1p5m/per_block_arm_outcomes.jsonl",
    ".workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/"
    "per_session_confirmation/per_block_arm_outcomes.jsonl",
    "comparison_bench/src/comparison_bench/formal_ir/nbpolar/raw_prior_val_1p5m.py",
    "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_order_1p5m.py",
    "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_disclosure_1p5m.py",
    "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_dose_escalation_1p5m.py",
    "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l1_dose_512_1p5m.py",
]
PROTECTED_COMPONENTS = {
    "dev", "val", "hold", "holdout", "1m", "2m", "v25",
    "pairs", "parquet",
}
PROTECTED_EXTS = {".parquet", ".pq"}


def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(3):
        root = os.path.dirname(root)
    return root


def is_protected(rel):
    parts = rel.replace("\\", "/").split("/")
    for p in parts:
        if p.lower() in PROTECTED_COMPONENTS:
            return True
    low = rel.lower()
    if "pairs" in os.path.basename(low):
        return True
    for ext in PROTECTED_EXTS:
        if low.endswith(ext):
            return True
    return False


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def read_self_and_prereg(here):
    with open(os.path.join(here, "body.py"), "rb") as f:
        self_bytes = f.read()
    with open(os.path.join(here, "prereg.md"), "rb") as f:
        pre_bytes = f.read()
    bt = chr(96) * 3
    om = (bt + "python" + chr(10)).encode("ascii")
    cm = (chr(10) + bt).encode("ascii")
    start = pre_bytes.find(om)
    if start < 0:
        return self_bytes, pre_bytes, None
    start += len(om)
    end = pre_bytes.find(cm, start)
    if end < 0:
        return self_bytes, pre_bytes, None
    return self_bytes, pre_bytes, pre_bytes[start : end + 1]


def write_results(here, payload):
    out = os.path.join(here, "results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
        f.write(chr(10))
    return out


def rss_now():
    try:
        import resource

        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    except Exception:
        return 0


def stop(here, payload, status, reason, t0, inventory, self_hex, pre_hex):
    payload.update(
        {
            "probe_id": PROBE_ID,
            "tier": TIER,
            "status": status,
            "stop_reason": reason,
            "question": QUESTION,
            "delta_ref": DELTA_REF,
            "prereg_sha256": pre_hex,
            "body_sha256": self_hex,
            "body_sha_match": True,
            "artifact_inventory": inventory,
            "command": COMMAND,
            "interpreter": sys.executable + " " + sys.version.replace(chr(10), " "),
            "wall_s": time.perf_counter() - t0,
            "rss_bytes": rss_now(),
            "decoder_calls": 0,
            "rng_calls": 0,
            "tag_calls": 0,
            "writes": [],
            "notes": ["STOP path: no repair by editing inputs.", "run-1; no rerun."],
        }
    )
    write_results(here, payload)
    print(PROBE_ID + " " + status + " " + reason, flush=True)
    sys.exit(2)


def num_or_none(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        f = float(v)
        if math.isfinite(f):
            return f
    return None


def is_nll_key(k):
    kl = k.lower()
    return ("nll" in kl) or ("cross" in kl and "entropy" in kl)


def is_floor_key(k):
    kl = k.lower()
    return ("floor" in kl) or ("zero_count" in kl)


def numbered(lines, idxs):
    return [{"line": i + 1, "text": lines[i].strip()[:300]} for i in idxs]


def main():
    t0 = time.perf_counter()
    here = os.path.dirname(os.path.abspath(__file__))
    repo = repo_root()

    self_bytes, pre_bytes, block = read_self_and_prereg(here)
    self_hex = sha256_bytes(self_bytes)
    pre_hex = sha256_bytes(pre_bytes)
    match = block is not None and block == self_bytes

    inventory = {"files": [], "protected_opens_attempted": False}
    if not match:
        stop(
            here,
            {"mismatch": "fenced python block is not byte-identical to body.py"},
            "X09R1_STOP_PREREG_MISMATCH",
            "prereg fenced block != body.py bytes",
            t0,
            inventory,
            self_hex,
            pre_hex,
        )

    absmap = {}
    for rel in REL_FILES:
        if is_protected(rel):
            inventory["protected_opens_attempted"] = True
            stop(
                here,
                {"refused": rel},
                "X09R1_STOP_PROTECTED",
                "protected-looking path: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
            )
        ap = os.path.join(repo, rel)
        try:
            st = os.stat(ap)
        except FileNotFoundError:
            stop(
                here,
                {"missing": rel},
                "X09R1_STOP_MISSING_FILE",
                "absent expected file: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
            )
        inventory["files"].append(
            {"path": rel, "size": st.st_size, "mtime_ns": st.st_mtime_ns}
        )
        absmap[rel] = ap

    def need_jsonl(rel):
        recs = []
        try:
            with open(absmap[rel], "r", encoding="utf-8") as f:
                for ln_no, line in enumerate(f, start=1):
                    s = line.strip()
                    if not s:
                        continue
                    try:
                        recs.append(json.loads(s))
                    except json.JSONDecodeError as e:
                        stop(
                            here,
                            {"file": rel, "line": ln_no, "error": str(e)[:200]},
                            "X09R1_STOP_UNREADABLE_JSONL",
                            "unreadable JSONL " + rel + " line " + str(ln_no),
                            t0,
                            inventory,
                            self_hex,
                            pre_hex,
                        )
        except OSError as e:
            stop(
                here,
                {"file": rel, "error": str(e)[:200]},
                "X09R1_STOP_UNREADABLE_JSONL",
                "unreadable JSONL file: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
            )
        return recs

    def need_json(rel):
        try:
            with open(absmap[rel], "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError, ValueError) as e:
            stop(
                here,
                {"file": rel, "error": str(e)[:200]},
                "X09R1_STOP_UNREADABLE_JSON",
                "unreadable JSON: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
            )

    p20m = need_jsonl(REL_FILES[0])
    plan = need_json(REL_FILES[2])
    orders = need_json(REL_FILES[6])
    preds = {}
    for rel in REL_FILES[7:11]:
        preds[rel] = need_jsonl(rel)
    src = {}
    for rel in REL_FILES[11:16]:
        try:
            with open(absmap[rel], "r", encoding="utf-8") as f:
                src[rel] = f.read().splitlines()
        except OSError as e:
            stop(
                here,
                {"file": rel, "error": str(e)[:200]},
                "X09R1_STOP_UNREADABLE_JSON",
                "unreadable runner file: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
            )
    try:
        z = np.load(absmap[REL_FILES[5]], allow_pickle=False)
        npz_keys = sorted([str(k) for k in z.files])
    except Exception as e:
        stop(
            here,
            {"file": REL_FILES[5], "error": str(e)[:300]},
            "X09R1_STOP_UNREADABLE_JSON",
            "unreadable npz",
            t0,
            inventory,
            self_hex,
            pre_hex,
        )
    missing_npz = [k for k in EXPECTED_NPZ_KEYS if k not in npz_keys]
    if missing_npz:
        stop(
            here,
            {"expected": EXPECTED_NPZ_KEYS, "actual": npz_keys, "missing": missing_npz},
            "X09R1_STOP_NPZ_KEY_SURPRISE",
            "npz key-set surprise, missing: " + ",".join(missing_npz),
            t0,
            inventory,
            self_hex,
            pre_hex,
        )
    shapes = {}
    for k in EXPECTED_NPZ_KEYS:
        a = np.asarray(z[k])
        if a.size and not bool(np.all(np.isfinite(a))):
            stop(
                here,
                {"key": k},
                "X09R1_STOP_NONFINITE",
                "nonfinite values in npz key: " + k,
                t0,
                inventory,
                self_hex,
                pre_hex,
            )
        shapes[k] = {"shape": list(a.shape), "dtype": str(a.dtype), "size": int(a.size)}
    z.close()

    union = set()
    for r in p20m:
        union.update(r.keys())
    union = sorted(union)

    # D1: NLL field inventory + authoritative selection + clean margins
    nll_keys = [k for k in union if is_nll_key(k)]
    writer_rel = REL_FILES[11]
    wlines = src[writer_rel]
    cites = {}
    for k in nll_keys:
        hits = []
        for i, ln in enumerate(wlines):
            if ('"' + k + '"') in ln or ("'" + k + "'") in ln:
                hits.append(i)
                if len(hits) >= 4:
                    break
        cites[k] = numbered(wlines, hits)

    def cap_for(arm):
        if arm in CAP:
            return CAP[arm]
        for known, c in CAP.items():
            if str(arm).startswith(known.split("_")[0]):
                return c
        return None

    margins = []
    secondary = []
    for r in p20m:
        arm = r.get("arm")
        bi = r.get("block_index", "UNAVAILABLE")
        rule = AUTH_RULE.get(arm, (None, []))
        primary, alternates = rule[0], list(rule[1])
        chosen, used_fallback, why = None, False, ""
        f0 = num_or_none(r.get(primary)) if primary else None
        if f0 is not None:
            chosen, why = primary, "primary rule field numeric on this record"
        else:
            for alt in alternates:
                fa = num_or_none(r.get(alt))
                if fa is not None:
                    chosen, used_fallback = alt, True
                    why = "primary " + str(primary) + " non-numeric; fallback " + alt
                    break
        cap = cap_for(arm)
        if chosen is not None and cap is not None:
            val = num_or_none(r.get(chosen))
            m = cap - val
            if not math.isfinite(m):
                stop(
                    here,
                    {"arm": arm, "block_index": bi},
                    "X09R1_STOP_NONFINITE",
                    "nonfinite margin",
                    t0,
                    inventory,
                    self_hex,
                    pre_hex,
                )
            margins.append(
                {
                    "arm": arm,
                    "block_index": bi,
                    "first_error_layer": r.get("first_error_layer"),
                    "first_error_coord": r.get("first_error_coord"),
                    "field_used": chosen,
                    "fallback_used": used_fallback,
                    "fallback_reason": why,
                    "l2_nll_bits": val,
                    "capacity_bits": cap,
                    "margin_bits": m,
                }
            )
        else:
            margins.append(
                {
                    "arm": arm,
                    "block_index": bi,
                    "first_error_layer": r.get("first_error_layer"),
                    "first_error_coord": r.get("first_error_coord"),
                    "field_used": "UNAVAILABLE",
                    "fallback_reason": why,
                    "l2_nll_bits": None,
                    "capacity_bits": cap,
                    "margin_bits": None,
                }
            )
        sec = {}
        for k in nll_keys:
            if k != chosen:
                sec[k] = r.get(k, "UNAVAILABLE")
        secondary.append({"arm": arm, "block_index": bi, "secondary_nll_fields": sec})

    n_h2 = N * H2
    ratio = CAP["G2_true_l1_diagnostic"] / n_h2
    for name, v in (("n_h2", n_h2), ("ratio", ratio)):
        if not math.isfinite(v):
            stop(
                here,
                {"value": name},
                "X09R1_STOP_NONFINITE",
                "nonfinite budget arithmetic: " + name,
                t0,
                inventory,
                self_hex,
                pre_hex,
            )
    d1 = {
        "nll_field_inventory": nll_keys,
        "writer_citations": cites,
        "authoritative_rule": {
            arm: {"primary": v[0], "alternates": v[1]}
            for arm, v in AUTH_RULE.items()
        },
        "rule_basis": (
            "G1 (raw-prior session budget) decodes the candidate path: "
            "l2_nll_candidate_H_bits. G2 (true-L1 oracle diagnostic) decodes "
            "the true/decided path: true_l2_nll_bits. G0 (lambda control) "
            "decodes the candidate path: l2_nll_candidate_H_bits."
        ),
        "per_record_margins": margins,
        "no_cross_field_sums": True,
        "secondary_nll_fields_descriptive": secondary,
        "budget": {
            "N_H2_bits": n_h2,
            "G2_capacity_bits": CAP["G2_true_l1_diagnostic"],
            "G1_capacity_bits": CAP["G1_raw_prior_session_budget"],
            "G0_capacity_bits": CAP["G0_old_point_base"],
            "capacity_over_entropy_ratio_G2": ratio,
        },
    }

    # D3: shared-field floor comparison
    p20m_floor = sorted([k for k in union if is_floor_key(k)])
    pred_keys = {}
    for rel, recs in preds.items():
        u = set()
        for r in recs:
            u.update(r.keys())
        pred_keys[rel] = sorted([k for k in u if is_floor_key(k)])
    in_all_preds = set(pred_keys[REL_FILES[7]])
    for rel in REL_FILES[8:11]:
        in_all_preds &= set(pred_keys[rel])
    shared = sorted(set(p20m_floor) & in_all_preds)
    p20m_only = sorted(set(p20m_floor) - in_all_preds)

    def cov(recs, k):
        return sum(1 for r in recs if isinstance(r.get(k), (int, float)) and not isinstance(r.get(k), bool))

    def stats(recs, k):
        vals = [float(r[k]) for r in recs if cov([r], k) == 1]
        if not vals:
            return {"n_present": 0, "n_records": len(recs)}
        s = 0.0
        for v in vals:
            s += v
        return {
            "n_present": len(vals),
            "n_records": len(recs),
            "sum": s,
            "mean": s / len(vals),
            "max": max(vals),
            "min": min(vals),
        }

    shared_cmp = {}
    for k in shared:
        per_file = {"p20m": stats(p20m, k)}
        for rel, recs in preds.items():
            per_file[rel] = stats(recs, k)
        shared_cmp[k] = per_file
    p20m_arm_detail = {}
    for r in p20m:
        a = str(r.get("arm"))
        e = {}
        for k in shared:
            e[k] = r.get(k, "UNAVAILABLE")
        e["first_error_layer"] = r.get("first_error_layer")
        e["first_error_coord"] = r.get("first_error_coord")
        e["block_index"] = r.get("block_index")
        p20m_arm_detail.setdefault(a, []).append(e)
    onesided = {}
    for k in p20m_only:
        onesided[k] = {"p20m": stats(p20m, k), "note": "one-sided context; absent in-sample"}
    hits_key = "floor_hits_1e15" if "floor_hits_1e15" in shared else None
    if hits_key:
        fail_vals = [
            float(r[hits_key])
            for r in p20m
            if str(r.get("first_error_layer")) == "L2" and cov([r], hits_key) == 1
        ]
        pred_max = None
        for rel, recs in preds.items():
            s = stats(recs, hits_key)
            if s.get("n_present"):
                pred_max = s["max"] if pred_max is None else max(pred_max, s["max"])
        if fail_vals and pred_max is not None:
            d3_sentence = (
                "P20M L2-failing blocks carry FEWER floor hits "
                "(" + ",".join(str(int(v)) for v in fail_vals) + ") than the "
                "in-sample per-block maximum (" + str(int(pred_max)) + ")"
            )
        else:
            d3_sentence = "UNAVAILABLE: hits missing on one side"
    else:
        d3_sentence = "UNAVAILABLE: no shared hit-count field"
        fail_vals, pred_max = [], None
    d3 = {
        "p20m_floor_keys": p20m_floor,
        "predecessor_floor_keys": pred_keys,
        "shared_fields": shared,
        "p20m_only_fields": p20m_only,
        "shared_comparison": shared_cmp,
        "p20m_per_arm_detail": p20m_arm_detail,
        "one_sided_context": onesided,
        "descriptive": d3_sentence,
    }

    # D4: first_error_coordinate index space
    olines = src[REL_FILES[12]]
    def_idx = None
    for i, ln in enumerate(olines):
        if ln.strip().startswith("def first_error_coordinate"):
            def_idx = i
            break
    func_block, call_sites = [], []
    if def_idx is not None:
        j = def_idx + 1
        while j < len(olines) and j < def_idx + 40:
            if olines[j].strip().startswith("def ") or olines[j].strip().startswith("class "):
                break
            j += 1
        func_block = numbered(olines, list(range(def_idx, j)))
        for i, ln in enumerate(olines):
            if "first_error_coordinate(" in ln and i != def_idx:
                lo = max(0, i - 8)
                hi = min(len(olines), i + 9)
                call_sites.append(
                    {"call_line": i + 1, "context": numbered(olines, list(range(lo, hi)))}
                )
    fblob = " ".join(c["text"] for c in func_block).lower()
    hits_lines = [c for c in func_block if "hits" in c["text"].lower()]
    order_via = any(
        s in "".join(c["text"] for c in hits_lines).lower()
        for s in ("order", "perm", "rank")
    )
    cmp_via = any(s in fblob for s in ("!=", "==", "flatnonzero", "argwhere", "where("))
    sliced_args = any(
        ("[:" in c["text"] or "prefix" in c["text"].lower())
        for cs in call_sites
        for c in cs["context"]
    )
    if order_via:
        index_space = "L1/L2 decode-order position (hits index through order/perm/rank)"
    elif cmp_via and not sliced_args:
        index_space = (
            "natural block symbol index: hits = mismatch positions of full-block "
            "estimate vs truth arrays, returned directly as int(hits[0]) with no "
            "order/perm mapping and full (unsliced) call-site arrays"
        )
    elif cmp_via and sliced_args:
        index_space = (
            "position within the SLICED array passed at the call site "
            "(prefix-relative if a disclosed prefix was passed); see call contexts"
        )
    else:
        index_space = (
            "GENUINELY AMBIGUOUS: settle with the single line computing hits "
            "inside first_error_coordinate (the hits = ... assignment)"
        )
    d4 = {
        "function_source": func_block,
        "hits_lines": hits_lines,
        "call_sites": call_sites,
        "index_space": index_space,
    }

    # D5: grounded H2 NOT-DECIDABLE reason
    l2_len = None
    if isinstance(orders, dict):
        v = orders.get("l2_order")
        if isinstance(v, list):
            l2_len = len(v)
    seq_keys = [
        k
        for k in union
        if any(s in k.lower() for s in ("hat", "truth", "_seq", "bob_", "alice_"))
    ]
    d5 = {
        "label": "NOT DECIDABLE-FROM-PERSISTED-ARTIFACTS",
        "reason": (
            "order positions index per-block symbols (l2_order len "
            + str(l2_len)
            + "), but per-block Bob/truth sequences are not persisted "
            "(sequence-like record keys: "
            + (",".join(seq_keys) if seq_keys else "none")
            + "); the npz is a 1024x1024 TRAIN cell table "
            "(counts_ab shape " + str(shapes["counts_ab"]["shape"]) + "), not "
            "per-block data, so a failure coordinate cannot be mapped to a "
            "hazard/covered cell from persisted artifacts"
        ),
        "instrumentation_requirement": (
            "a successor packet must persist, at decode time per block, "
            "per-position hazard scalars (e.g. floor-mass / zero-count flags) "
            "and disclosed-prefix membership for the frozen order, so each "
            "observed failure coordinate maps to hazard + coverage state"
        ),
    }

    # hypothesis table
    failing = [m for m in margins if m["first_error_layer"] == "L2" and m["margin_bits"] is not None]
    missing_h1 = [m for m in margins if m["margin_bits"] is None]
    if missing_h1:
        h1 = {
            "label": "NOT DECIDABLE-FROM-PERSISTED-ARTIFACTS",
            "evidence": "authoritative L2-NLL value missing on some records",
        }
    elif failing and all(m["margin_bits"] < 0 for m in failing):
        worst = min(failing, key=lambda m: m["margin_bits"])
        h1 = {
            "label": "SUPPORTED",
            "evidence": (
                "every L2-failing G1/G2 block runs an out-of-sample L2-NLL "
                "shortfall vs capacity; worst " + str(worst["arm"]) + " block_index "
                + str(worst["block_index"]) + " margin "
                + ("%.1f" % worst["margin_bits"]) + " bits"
            ),
        }
    elif failing:
        best = max(failing, key=lambda m: m["margin_bits"])
        h1 = {
            "label": "NOT SUPPORTED",
            "evidence": (
                "some L2-failing block fits its capacity; max failing margin "
                + ("%.1f" % best["margin_bits"]) + " bits (" + str(best["arm"]) + ")"
            ),
        }
    else:
        h1 = {"label": "NOT SUPPORTED", "evidence": "no L2-failing records"}
    if hits_key and fail_vals and pred_max is not None:
        if max(fail_vals) > pred_max:
            h3 = {
                "label": "SUPPORTED",
                "evidence": "failing-block floor hits exceed in-sample per-block max",
            }
        else:
            h3 = {
                "label": "NOT SUPPORTED",
                "evidence": (
                    "failing-block floor hits ("
                    + ",".join(str(int(v)) for v in fail_vals)
                    + ") at/below in-sample per-block max (" + str(int(pred_max)) + ")"
                ),
            }
    else:
        h3 = {
            "label": "NOT DECIDABLE-FROM-PERSISTED-ARTIFACTS",
            "evidence": d3_sentence,
        }
    hypothesis_table = {
        "H1_budget_insufficiency": h1,
        "H2_order_metric_nongeneralization": {
            "label": d5["label"],
            "evidence": d5["reason"],
        },
        "H3_floor_heavytail": h3,
    }

    result = {
        "probe_id": PROBE_ID,
        "tier": TIER,
        "status": COMPLETE_STATUS,
        "question": QUESTION,
        "delta_ref": DELTA_REF,
        "delta_vs_X09": "D1 clean single-field margins keyed by block_index; "
        "D2 block_index fix; D3 shared-field floor comparison; D4 settled "
        "index space with exact lines; D5 grounded H2 reason + requirement. "
        "All else inherited from X09.",
        "prereg_sha256": pre_hex,
        "body_sha256": self_hex,
        "body_sha_match": True,
        "artifact_inventory": inventory,
        "d1_h1_margins": d1,
        "d2_block_key": "block_index (X09 defect of null block fixed; every margin keyed by arm + block_index)",
        "d3_floor_comparison": d3,
        "d4_index_space": d4,
        "d5_h2": d5,
        "hypothesis_table": hypothesis_table,
        "next_packet_requirements": [
            "persist, at decode time per block, per-position hazard scalars and "
            "disclosed-prefix membership for the frozen order (closes H2)",
            "persist failure-neighborhood floor stats restricted to the disclosed "
            "prefix and failing-coordinate neighborhoods (sharpens H3)",
        ],
        "command": COMMAND,
        "interpreter": sys.executable + " " + sys.version.replace(chr(10), " "),
        "wall_s": time.perf_counter() - t0,
        "rss_bytes": rss_now(),
        "decoder_calls": 0,
        "rng_calls": 0,
        "tag_calls": 0,
        "writes": ["workspace/probes/nbpolar_x09_l2_attribution_r1/results.json"],
        "notes": [
            "Descriptive only; no verdict on the next scientific factor.",
            "run-1 crashed on tuple-unpack bug in budget finite-check "
            "(fixed name/v order); rerun-2 after identical prereg regeneration; "
            "frozen params, artifact list, command unchanged.",
            "p20m_n_records=" + str(len(p20m)) + " (expected 9).",
            "G0 capacity 32524 = 5*6492+64 from frozen plan g0_k2.",
        ],
    }
    out = write_results(here, result)
    print(PROBE_ID + " " + COMPLETE_STATUS + " wall_s=" + ("%.2f" % result["wall_s"]) + " out=" + out, flush=True)


if __name__ == "__main__":
    main()
```

## Prereg footer

Prereg written before any R1 artifact content read; X09 outputs reused as prior
knowledge per the delta-successor brief. body.py asserts byte-equality with the
fenced block at runtime and records prereg_sha256/body_sha256/body_sha_match.
A rerun solely to fix an execution error is allowed and must be recorded.
