# NBPOLAR-X09-L2-ATTRIBUTION — prereg (frozen, written BEFORE any artifact content read)

probe_id: NBPOLAR-X09-L2-ATTRIBUTION | tier: X (non-claim, decoder-free, read-only)
question: which mechanism explains the out-of-sample L2 failure at K2=6689
(P20M G1/G2 0/3 while TRAIN-segment oracle arms were 3/3 exact) — H1 budget
insufficiency, H2 order/metric non-generalization, or H3 floor/heavy-tail —
using ONLY already-persisted worktree artifacts.
frozen params: K2=6689, N=32768, H2=0.8003665547495433, G2 cap 33509 (=5*K2+64),
G1 cap 35164 (=5*331+5*6689+64), failure coords 26/3646/31.
forbidden: parquet/pairs content; DEV/VAL/HOLD/1M/V25-counts/2M open/stat/listing
in any form; decoder/RNG/tag calls; writes outside the probe root (+ packet dir);
commit/push. stop: missing file, unreadable JSON/JSONL, npz key surprise,
nonfinite → STOP results.json, no repair.

## Exact command (run exactly once)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && timeout 120 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python workspace/probes/nbpolar_x09_l2_attribution/body.py
```

## Exact artifact list (16 files, repo-relative, each stat size/mtime_ns)

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
"""NBPOLAR-X09-L2-ATTRIBUTION Tier-X probe body.

Non-claim, decoder-free, read-only diagnostic on already-persisted worktree
artifacts. Zero protected opens. No decoder/RNG/tag calls.
results.json is the ONLY file this script writes.
"""
import os
import sys
import json
import math
import time
import hashlib

import numpy as np

PROBE_ID = "NBPOLAR-X09-L2-ATTRIBUTION"
TIER = "X"
COMPLETE_STATUS = "X09_PROBE_COMPLETE_DESCRIPTIVE_ONLY"
QUESTION = (
    "Which mechanism explains the out-of-sample L2 failure at K2=6689 "
    "(P20M G1/G2 0/3 while TRAIN-segment oracle arms were 3/3 exact): "
    "(H1) K2 disclosure-budget insufficiency out-of-sample, "
    "(H2) L2 order/metric non-generalization, or "
    "(H3) floor/heavy-tail (TRAIN zero-count cell) exposure, "
    "using ONLY already-persisted worktree artifacts?"
)
COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export "
    "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "
    "MALLOC_ARENA_MAX=2 && timeout 120 "
    "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python "
    "workspace/probes/nbpolar_x09_l2_attribution/body.py"
)
K2 = 6689
N = 32768
H2 = 0.8003665547495433
FAILURE_COORDS = [26, 3646, 31]
EXPECTED_NPZ_KEYS = ["counts_ab", "f_raw", "p1", "p2", "p_b"]
FLOOR_KEYS = [
    "floor_hits_1e15",
    "floor_hit_rate",
    "floor_hit_log_loss_bits",
    "raw_zero_count_hits",
]
ENDPOINT_BOOLS = ["l1_exact", "hard_l2_exact", "pair_exact", "oracle_l2_exact"]
FIRST_ERROR_KEYS = ["first_error_layer", "first_error_coord"]

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


RERUN_RECORD = (
    "rerun-2: fixed repo_root() off-by-one (4 dirname levels -> 3) after "
    "run-1 false X09_STOP_MISSING_FILE (wall 0.006s, empty inventory); "
    "prereg fenced block updated identically before run-2; frozen params, "
    "artifact list, and command unchanged"
)


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
    self_path = os.path.join(here, "body.py")
    pre_path = os.path.join(here, "prereg.md")
    with open(self_path, "rb") as f:
        self_bytes = f.read()
    with open(pre_path, "rb") as f:
        pre_bytes = f.read()
    bt = chr(96) * 3
    open_marker = (bt + "python" + chr(10)).encode("ascii")
    close_marker = (chr(10) + bt).encode("ascii")
    start = pre_bytes.find(open_marker)
    if start < 0:
        return self_bytes, pre_bytes, None
    start += len(open_marker)
    end = pre_bytes.find(close_marker, start)
    if end < 0:
        return self_bytes, pre_bytes, None
    block = pre_bytes[start : end + 1]
    return self_bytes, pre_bytes, block


def base_result(**kw):
    return kw


def write_results(here, payload):
    out = os.path.join(here, "results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
        f.write(chr(10))
    return out


def stop(here, payload, status, reason, t0, inventory, self_hex, pre_hex, match):
    try:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    except Exception:
        rss = 0
    payload.update(
        {
            "probe_id": PROBE_ID,
            "tier": TIER,
            "status": status,
            "stop_reason": reason,
            "question": QUESTION,
            "prereg_sha256": pre_hex,
            "body_sha256": self_hex,
            "body_sha_match": match,
            "artifact_inventory": inventory,
            "command": COMMAND,
            "interpreter": sys.executable + " " + sys.version.replace(chr(10), " "),
            "wall_s": time.perf_counter() - t0,
            "rss_bytes": int(rss),
            "decoder_calls": 0,
            "rng_calls": 0,
            "tag_calls": 0,
            "writes": [],
            "notes": [
                "STOP path: no repair by editing inputs.",
                RERUN_RECORD,
            ],
        }
    )
    write_results(here, payload)
    print(PROBE_ID + " " + status + " " + reason, flush=True)
    sys.exit(2)


def grep_field(lines, field):
    hits = []
    for i, ln in enumerate(lines, start=1):
        if field in ln:
            hits.append({"line": i, "text": ln.strip()[:300]})
    return hits


def find_arm_key(records):
    for cand in ("arm", "group", "decoder", "method", "config"):
        if records and all(cand in r for r in records):
            return cand
    for cand in ("arm", "group", "decoder", "method", "config"):
        if records and any(cand in r for r in records):
            return cand
    return None


def num_or_none(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        f = float(v)
        if math.isfinite(f):
            return f
    return None


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
            "X09_STOP_PREREG_MISMATCH",
            "prereg fenced block != body.py bytes",
            t0,
            inventory,
            self_hex,
            pre_hex,
            False,
        )

    absmap = {}
    for rel in REL_FILES:
        if is_protected(rel):
            inventory["protected_opens_attempted"] = True
            stop(
                here,
                {"refused": rel},
                "X09_STOP_PROTECTED",
                "frozen list touched a protected-looking path: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
            )
        ap = os.path.join(repo, rel)
        try:
            st = os.stat(ap)
        except FileNotFoundError:
            stop(
                here,
                {"missing": rel},
                "X09_STOP_MISSING_FILE",
                "absent expected file: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
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
                            "X09_STOP_UNREADABLE_JSONL",
                            "unreadable JSONL " + rel + " line " + str(ln_no),
                            t0,
                            inventory,
                            self_hex,
                            pre_hex,
                            True,
                        )
        except OSError as e:
            stop(
                here,
                {"file": rel, "error": str(e)[:200]},
                "X09_STOP_UNREADABLE_JSONL",
                "unreadable JSONL file: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
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
                "X09_STOP_UNREADABLE_JSON",
                "unreadable JSON: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
            )

    p20m_recs = need_jsonl(REL_FILES[0])
    agg = need_json(REL_FILES[1])
    plan = need_json(REL_FILES[2])
    ident = need_json(REL_FILES[3])
    try:
        with open(absmap[REL_FILES[4]], "r", encoding="utf-8") as f:
            report_text = f.read()
    except OSError as e:
        stop(
            here,
            {"file": REL_FILES[4], "error": str(e)[:200]},
            "X09_STOP_UNREADABLE_JSON",
            "unreadable report.md",
            t0,
            inventory,
            self_hex,
            pre_hex,
            True,
        )
    orders = need_json(REL_FILES[6])
    pred_recs = {}
    for rel in REL_FILES[7:11]:
        pred_recs[rel] = need_jsonl(rel)

    runner_src = {}
    for rel in REL_FILES[11:16]:
        try:
            with open(absmap[rel], "r", encoding="utf-8") as f:
                runner_src[rel] = f.read().splitlines()
        except OSError as e:
            stop(
                here,
                {"file": rel, "error": str(e)[:200]},
                "X09_STOP_UNREADABLE_JSON",
                "unreadable runner file: " + rel,
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
            )

    try:
        z = np.load(absmap[REL_FILES[5]], allow_pickle=False)
        npz_keys = sorted([str(k) for k in z.files])
    except Exception as e:
        stop(
            here,
            {"file": REL_FILES[5], "error": str(e)[:300]},
            "X09_STOP_UNREADABLE_JSON",
            "unreadable npz: " + REL_FILES[5],
            t0,
            inventory,
            self_hex,
            pre_hex,
            True,
        )
    missing_npz = [k for k in EXPECTED_NPZ_KEYS if k not in npz_keys]
    if missing_npz:
        stop(
            here,
            {"expected": EXPECTED_NPZ_KEYS, "actual": npz_keys, "missing": missing_npz},
            "X09_STOP_NPZ_KEY_SURPRISE",
            "npz key-set surprise, missing: " + ",".join(missing_npz),
            t0,
            inventory,
            self_hex,
            pre_hex,
            True,
        )
    extra_npz = [k for k in npz_keys if k not in EXPECTED_NPZ_KEYS]

    arrays = {}
    for k in EXPECTED_NPZ_KEYS:
        try:
            a = np.asarray(z[k])
        except Exception as e:
            stop(
                here,
                {"key": k, "error": str(e)[:200]},
                "X09_STOP_NPZ_KEY_SURPRISE",
                "npz key unreadable: " + k,
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
            )
        arrays[k] = a
    z.close()

    npz_desc = {}
    for k, a in arrays.items():
        finite = bool(np.all(np.isfinite(a))) if a.size else True
        if not finite:
            stop(
                here,
                {"key": k},
                "X09_STOP_NONFINITE",
                "nonfinite values in npz key: " + k,
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
            )
        d = {
            "shape": list(a.shape),
            "dtype": str(a.dtype),
            "size": int(a.size),
            "min": float(np.min(a)) if a.size else None,
            "max": float(np.max(a)) if a.size else None,
            "sum": float(np.sum(a)) if a.size else None,
        }
        if not all(
            math.isfinite(x) for x in (d["min"], d["max"], d["sum"]) if x is not None
        ):
            stop(
                here,
                {"key": k, "desc": d},
                "X09_STOP_NONFINITE",
                "nonfinite summary for npz key: " + k,
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
            )
        npz_desc[k] = d

    # 1. field_semantics
    sem_fields = FIRST_ERROR_KEYS + ENDPOINT_BOOLS + FLOOR_KEYS
    field_semantics = {}
    for fld in sem_fields:
        cites = []
        for rel, lines in runner_src.items():
            for h in grep_field(lines, fld)[:6]:
                cites.append(
                    {"file": rel, "line": h["line"], "text": h["text"]}
                )
        field_semantics[fld] = cites
    writer_rel = REL_FILES[11]
    wlines = runner_src[writer_rel]
    coord_ctx = []
    for i, ln in enumerate(wlines):
        if "first_error_coord" in ln and "=" in ln:
            lo = max(0, i - 6)
            hi = min(len(wlines), i + 7)
            coord_ctx = [
                {"line": lo + j + 1, "text": wlines[lo + j].strip()[:300]}
                for j in range(hi - lo)
            ]
            break
    ctx_blob = " ".join(c["text"] for c in coord_ctx).lower()
    if any(
        s in ctx_blob
        for s in ("order", "perm", "rank", "_order[", "order[", "decode order")
    ):
        index_space = (
            "L1/L2 decode-order position (assignment context mentions order/perm/rank)"
        )
    elif any(
        s in ctx_blob
        for s in ("flatnonzero", "argwhere", "argmin", "natural", "symbol index")
    ):
        index_space = (
            "natural symbol index (assignment context mentions "
            "flatnonzero/argwhere/natural)"
        )
    else:
        index_space = (
            "AMBIGUOUS_FROM_GREP: quote lines above decide; "
            "both readings carried in order_geometry"
        )
    field_semantics["_first_error_coord_index_space"] = {
        "statement": index_space,
        "writer_file": writer_rel,
        "context": coord_ctx,
    }
    field_semantics["_endpoint_boolean_meaning"] = (
        "Per-record exact-reconstruction flags (True = that layer/pair matches "
        "reference exactly on that block/arm); writer citations above give "
        "exact definitions."
    )
    field_semantics["_floor_field_meaning"] = (
        "floor_hits_1e15 = count of likelihood evaluations that hit the 1e-15 "
        "probability floor; floor_hit_rate = hits / evaluations; "
        "floor_hit_log_loss_bits = bits of log-loss attributable to floor hits; "
        "raw_zero_count_hits = hits on TRAIN zero-count cells; "
        "verified against writer citations above."
    )

    # 2. available_fields
    def key_inventory(recs):
        union = set()
        per = []
        for r in recs:
            ks = sorted(r.keys())
            union.update(ks)
            per.append(ks)
        return sorted(union), per

    p20m_union, p20m_per = key_inventory(p20m_recs)
    pred_union = {}
    for rel, recs in pred_recs.items():
        u, _ = key_inventory(recs)
        pred_union[rel] = {"n_records": len(recs), "union_keys": u}

    def is_nll_key(k):
        kl = k.lower()
        if "nll" in kl:
            return True
        if "cross" in kl and "entropy" in kl:
            return True
        if kl.endswith("_bits") and ("l2" in kl or "layer" in kl or "ce" in kl):
            return True
        if kl in ("l2_log_loss_bits", "l2_nll_bits", "cond_nll_bits"):
            return True
        return False

    nll_keys_p20m = [k for k in p20m_union if is_nll_key(k)]
    nll_keys_pred = {}
    for rel, recs in pred_recs.items():
        u, _ = key_inventory(recs)
        nll_keys_pred[rel] = [k for k in u if is_nll_key(k)]
    logloss_like_p20m = [k for k in p20m_union if "log_loss" in k.lower()]

    available_fields = {
        "p20m_n_records": len(p20m_recs),
        "p20m_union_keys": p20m_union,
        "predecessors": pred_union,
        "p20m_l2_nll_like_keys": nll_keys_p20m,
        "predecessor_l2_nll_like_keys": nll_keys_pred,
        "p20m_log_loss_like_keys": logloss_like_p20m,
        "l2_nll_bits_status": (
            "PRESENT: " + ",".join(nll_keys_p20m)
            if nll_keys_p20m
            else "UNAVAILABLE: no per-record L2 NLL / cross-entropy / "
            "per-layer log-loss-bit field persisted in P20M records"
        ),
    }

    # 3. budget_attribution (H1)
    cap_g2 = 5 * K2 + 64
    cap_g1 = 5 * 331 + 5 * K2 + 64
    n_h2_bits = N * H2
    ratio_g2 = cap_g2 / n_h2_bits
    for v, name in (
        (cap_g2, "cap_g2"),
        (cap_g1, "cap_g1"),
        (n_h2_bits, "n_h2"),
        (ratio_g2, "ratio"),
    ):
        if not math.isfinite(v):
            stop(
                here,
                {"value": name},
                "X09_STOP_NONFINITE",
                "nonfinite budget arithmetic: " + name,
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
            )
    plan_hit_keys = []

    def walk_plan(obj, path, depth):
        if depth > 4 or len(plan_hit_keys) > 60:
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                kl = str(k).lower()
                if any(
                    s in kl
                    for s in ("k2", "k1", "cap", "budget", "disclos", "entropy", "h2")
                ):
                    plan_hit_keys.append(
                        {"path": path + "/" + str(k), "value": str(v)[:160]}
                    )
                walk_plan(v, path + "/" + str(k), depth + 1)
        elif isinstance(obj, list):
            for i, v in enumerate(obj[:20]):
                walk_plan(v, path + "/" + str(i), depth + 1)

    walk_plan(plan, "$", 0)
    budget_attribution = {
        "K2": K2,
        "N": N,
        "H2": H2,
        "capacity_5K2_plus_64_G2": cap_g2,
        "capacity_G2_expected_33509": cap_g2 == 33509,
        "capacity_G1_expected_35164": cap_g1 == 35164,
        "capacity_G1": cap_g1,
        "in_sample_conditional_entropy_N_H2_bits": n_h2_bits,
        "capacity_over_entropy_ratio_G2": ratio_g2,
        "frozen_plan_literal_hits": plan_hit_keys,
    }
    if nll_keys_p20m:
        margins = []
        for r in p20m_recs:
            tot = 0.0
            ok = True
            for k in nll_keys_p20m:
                f = num_or_none(r.get(k))
                if f is None:
                    ok = False
                    break
                tot += f
            if not ok:
                continue
            arm = r.get(find_arm_key(p20m_recs) or "arm", None)
            cap = cap_g1 if str(arm).upper().find("G1") >= 0 else cap_g2
            margins.append(
                {
                    "arm": arm,
                    "block": r.get("block", r.get("block_id", r.get("idx", None))),
                    "l2_nll_bits": tot,
                    "capacity": cap,
                    "margin_bits": cap - tot,
                }
            )
        budget_attribution["per_block_margins"] = margins
        budget_attribution["H1_from_persisted"] = (
            "compare margin_bits: negative = shortfall on that block"
        )
    else:
        budget_attribution["per_block_margins"] = "UNAVAILABLE"
        budget_attribution["H1_from_persisted"] = (
            "NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS: no per-record "
            "out-of-sample L2 NLL/CE bits persisted"
        )

    # 4. floor_attribution (H3)
    arm_key = find_arm_key(p20m_recs)
    floor_rows_p20m = []
    for i, r in enumerate(p20m_recs):
        row = {"idx": i}
        if arm_key:
            row["arm"] = r.get(arm_key)
        row["first_error_layer"] = r.get("first_error_layer")
        row["first_error_coord"] = r.get("first_error_coord")
        for k in FLOOR_KEYS:
            row[k] = r.get(k, "UNAVAILABLE")
        extra_floor = [
            k for k in r.keys() if "floor" in k.lower() and k not in FLOOR_KEYS
        ]
        for k in extra_floor:
            row[k] = r.get(k)
        floor_rows_p20m.append(row)

    def floor_totals(recs):
        tot = {}
        for k in FLOOR_KEYS:
            vals = [num_or_none(r.get(k)) for r in recs]
            vals = [v for v in vals if v is not None]
            tot[k] = {
                "n_present": len(vals),
                "n_records": len(recs),
                "sum": float(sum(vals)) if vals else None,
                "mean": float(sum(vals) / len(vals)) if vals else None,
                "max": float(max(vals)) if vals else None,
            }
        return tot

    floor_pred = {}
    for rel, recs in pred_recs.items():
        floor_pred[rel] = {
            "n_records": len(recs),
            "totals": floor_totals(recs),
        }
    p20m_l2_fail = [
        r
        for r in p20m_recs
        if str(r.get("first_error_layer", "")).upper() == "L2"
    ]
    p20m_fail_rates = [
        v
        for v in (num_or_none(r.get("floor_hit_rate")) for r in p20m_l2_fail)
        if v is not None
    ]
    pred_max_rate = None
    pred_means = {}
    for rel, recs in pred_recs.items():
        vals = [
            v
            for v in (num_or_none(r.get("floor_hit_rate")) for r in recs)
            if v is not None
        ]
        if vals:
            pred_means[rel] = float(sum(vals) / len(vals))
            m = float(max(vals))
            pred_max_rate = m if pred_max_rate is None else max(pred_max_rate, m)
    if p20m_fail_rates and pred_max_rate is not None:
        fail_mean = float(sum(p20m_fail_rates) / len(p20m_fail_rates))
        materially_more = (
            float(max(p20m_fail_rates)) > pred_max_rate
            or fail_mean > 2.0 * max(pred_means.values())
        )
        floor_comparison = {
            "p20m_l2_failing_floor_hit_rates": p20m_fail_rates,
            "predecessor_max_floor_hit_rate": pred_max_rate,
            "predecessor_mean_rates": pred_means,
            "failing_blocks_exceed_all_insample": bool(
                float(max(p20m_fail_rates)) > pred_max_rate
            ),
            "descriptive": (
                "L2-failing VAL blocks carry materially more floor exposure"
                if materially_more
                else "L2-failing VAL blocks are within in-sample floor exposure"
            ),
        }
    else:
        floor_comparison = {
            "descriptive": "UNAVAILABLE: floor_hit_rate missing on failing or "
            "in-sample blocks",
            "p20m_l2_failing_n": len(p20m_l2_fail),
            "predecessor_mean_rates": pred_means,
        }
    floor_attribution = {
        "arm_key": arm_key if arm_key else "UNAVAILABLE",
        "p20m_per_record": floor_rows_p20m,
        "p20m_totals": floor_totals(p20m_recs),
        "predecessors": floor_pred,
        "comparison": floor_comparison,
        "floor_attributable_bits_note": (
            "If a persisted per-record L2 log-loss field existed, "
            "floor-attributable bits = floor_hit_log_loss_bits on that record; "
            "else UNAVAILABLE (see available_fields)."
        ),
    }

    # 5. order_geometry (H2)
    orders_keys = sorted(orders.keys()) if isinstance(orders, dict) else []
    perm_info = {}
    l2_perm = None
    l2_key = None
    if isinstance(orders, dict):
        for k, v in orders.items():
            if isinstance(v, list) and len(v) > 100:
                head = v[:2000]
                if all(isinstance(x, int) for x in head):
                    perm_info[str(k)] = {
                        "len": len(v),
                        "is_full_perm": sorted(v) == list(range(len(v))),
                        "head10": v[:10],
                    }
                    kl = str(k).lower()
                    if "l2" in kl and ("order" in kl or "perm" in kl):
                        if l2_perm is None:
                            l2_perm = v
                            l2_key = str(k)
        if l2_perm is None:
            for k, v in orders.items():
                if isinstance(v, list) and len(v) > 100:
                    if all(isinstance(x, int) for x in v[:2000]):
                        if sorted(v) == list(range(len(v))):
                            l2_perm = v
                            l2_key = str(k) + " (fallback: first full perm)"
                            break
    counts = arrays["counts_ab"]
    fraw = arrays["f_raw"]
    pb = arrays["p_b"]
    cflat = counts.ravel()
    fflat = fraw.ravel()
    zero_mask = cflat == 0
    n_zero = int(np.sum(zero_mask))
    n_cells = int(cflat.size)
    floor_masses = sorted(set(fflat[zero_mask].tolist())) if n_zero else []
    pb_flat = pb.ravel()
    if pb_flat.size == cflat.size and float(np.sum(pb_flat)) > 0:
        floor_prob = float(np.sum(pb_flat[zero_mask]))
    else:
        floor_prob = None
    order_geometry = {
        "orders_keys": orders_keys,
        "perm_info": perm_info,
        "l2_perm_key": l2_key if l2_key else "UNAVAILABLE",
        "n_cells": n_cells,
        "n_train_zero_cells": n_zero,
        "frac_zero_cells": (n_zero / n_cells) if n_cells else None,
        "floor_mass_values": floor_masses[:8],
        "p_b_weighted_floor_prob": floor_prob,
        "npz_extra_keys": extra_npz,
        "npz_desc": npz_desc,
    }
    if l2_perm is not None and n_cells and len(l2_perm) == n_cells:
        top = set(l2_perm[:K2])
        zero_idx = set(np.flatnonzero(zero_mask).tolist())
        overlap = len(top & zero_idx)
        inv = [0] * n_cells
        for rank, nat in enumerate(l2_perm):
            inv[nat] = rank
        nat_reading = []
        for c in FAILURE_COORDS:
            if 0 <= c < n_cells:
                nat_reading.append(
                    {
                        "coord": c,
                        "rank": inv[c],
                        "in_disclosed_prefix": bool(inv[c] < K2),
                        "is_floor_hazard": bool(c in zero_idx),
                    }
                )
        pos_reading = []
        for c in FAILURE_COORDS:
            if 0 <= c < len(l2_perm):
                nat = l2_perm[c]
                pos_reading.append(
                    {
                        "order_position": c,
                        "natural_index": nat,
                        "in_disclosed_prefix": bool(c < K2),
                        "is_floor_hazard": bool(nat in zero_idx),
                    }
                )
        order_geometry.update(
            {
                "topK2_floor_hazard_overlap": overlap,
                "topK2_floor_hazard_fraction": overlap / K2,
                "failure_natural_index_reading": nat_reading,
                "failure_order_position_reading": pos_reading,
                "index_space_used_as_primary": index_space,
            }
        )
    else:
        order_geometry.update(
            {
                "topK2_floor_hazard_overlap": "UNAVAILABLE",
                "note": "L2 perm length != n_cells or perm not found; "
                "no geometry beyond key inventory",
            }
        )

    for v in (
        order_geometry.get("topK2_floor_hazard_fraction"),
        order_geometry.get("frac_zero_cells"),
        order_geometry.get("p_b_weighted_floor_prob"),
    ):
        if v is not None and not math.isfinite(float(v)):
            stop(
                here,
                {"value": v},
                "X09_STOP_NONFINITE",
                "nonfinite order-geometry value",
                t0,
                inventory,
                self_hex,
                pre_hex,
                True,
            )

    # 6. hypothesis_table
    if nll_keys_p20m:
        h1_label = "DECIDABLE-IN-RESULTS (see margins)"
        h1_ev = "per-record L2 NLL persisted; margins decide shortfall/surplus"
    else:
        h1_label = "NOT DECIDABLE-FROM-PERSISTED-ARTIFACTS"
        h1_ev = (
            "no per-record out-of-sample L2 NLL/CE bits persisted; in-sample "
            "budget arithmetic alone (cap "
            + str(cap_g2)
            + " vs N*H2 "
            + ("%.2f" % n_h2_bits)
            + ") cannot test out-of-sample shortfall"
        )
    fc = floor_comparison.get("descriptive", "")
    if "materially more" in fc:
        h3_label = "SUPPORTED"
        h3_ev = "L2-failing VAL blocks exceed in-sample floor exposure: " + fc
    elif "within in-sample" in fc:
        h3_label = "NOT SUPPORTED"
        h3_ev = "L2-failing VAL floor exposure within in-sample range: " + fc
    else:
        h3_label = "NOT DECIDABLE-FROM-PERSISTED-ARTIFACTS"
        h3_ev = "floor fields missing: " + fc
    frac_top = order_geometry.get("topK2_floor_hazard_fraction")
    nat_read = order_geometry.get("failure_natural_index_reading", [])
    if isinstance(nat_read, list) and nat_read:
        n_haz = sum(1 for e in nat_read if e.get("is_floor_hazard"))
        n_late = sum(1 for e in nat_read if not e.get("in_disclosed_prefix"))
        if n_late >= 2:
            h2_label = "SUPPORTED"
            h2_ev = (
                str(n_late)
                + "/3 failure coords rank at/after the disclosed prefix "
                "(order/metric non-generalization reading)"
            )
        elif n_haz >= 2:
            h2_label = "SUPPORTED"
            h2_ev = (
                str(n_haz)
                + "/3 failure coords are TRAIN zero-count (floor-hazard) cells; "
                "order placed hazard cells early (topK2 hazard fraction "
                + (str(round(float(frac_top), 4)) if frac_top is not None else "?")
                + ")"
            )
        else:
            h2_label = "NOT SUPPORTED"
            h2_ev = (
                "failures are early-rank disclosed non-hazard cells "
                "(" + str(n_haz) + "/3 hazard, " + str(n_late) + "/3 late)"
            )
    else:
        h2_label = "NOT DECIDABLE-FROM-PERSISTED-ARTIFACTS"
        h2_ev = "L2 permutation or cell geometry unavailable from persisted data"
    hypothesis_table = {
        "H1_budget_insufficiency": {"label": h1_label, "evidence": h1_ev},
        "H2_order_metric_nongeneralization": {"label": h2_label, "evidence": h2_ev},
        "H3_floor_heavytail": {"label": h3_label, "evidence": h3_ev},
    }

    # 7. next_packet_requirements
    reqs = []
    if not nll_keys_p20m:
        reqs.append(
            "persist per-record out-of-sample L2 NLL (cross-entropy) bits per "
            "arm/block, same block grid as P20M, to test H1 margins"
        )
    reqs.append(
        "persist failure-neighborhood floor stats: floor-hit counts/rates/bits "
        "restricted to disclosed prefix and to failing-coordinate neighborhoods"
    )
    reqs.append(
        "persist disclosed-prefix membership flags + L2 order ranks for the "
        "observed failure coordinates (26, 3646, 31) under the frozen order"
    )
    if l2_perm is None:
        reqs.append("persist the frozen L2 permutation actually used by the runner")
    next_packet_requirements = reqs

    try:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    except Exception:
        rss = 0
    result = {
        "probe_id": PROBE_ID,
        "tier": TIER,
        "status": COMPLETE_STATUS,
        "question": QUESTION,
        "prereg_sha256": pre_hex,
        "body_sha256": self_hex,
        "body_sha_match": True,
        "artifact_inventory": inventory,
        "field_semantics": field_semantics,
        "available_fields": available_fields,
        "budget_attribution": budget_attribution,
        "floor_attribution": floor_attribution,
        "order_geometry": order_geometry,
        "hypothesis_table": hypothesis_table,
        "next_packet_requirements": next_packet_requirements,
        "command": COMMAND,
        "interpreter": sys.executable + " " + sys.version.replace(chr(10), " "),
        "wall_s": time.perf_counter() - t0,
        "rss_bytes": int(rss),
        "decoder_calls": 0,
        "rng_calls": 0,
        "tag_calls": 0,
        "writes": [
            "workspace/probes/nbpolar_x09_l2_attribution/results.json"
        ],
        "notes": [
            "Descriptive only; no verdict about the next scientific factor.",
            RERUN_RECORD,
            "p20m_n_records=" + str(len(p20m_recs)) + " (expected 9).",
            "aggregate_summary top-level keys: "
            + ",".join(sorted(agg.keys())[:40] if isinstance(agg, dict) else []),
            "report.md chars: " + str(len(report_text)),
        ],
    }
    out = write_results(here, result)
    print(
        PROBE_ID
        + " "
        + COMPLETE_STATUS
        + " wall_s="
        + ("%.2f" % result["wall_s"])
        + " out="
        + out,
        flush=True,
    )


if __name__ == "__main__":
    main()
```

## Prereg footer

Prereg written before any artifact content read; only existence checks
(probe root ABSENT, packet dir absent, parent listings) were performed.
body.py asserts byte-equality with the fenced block at runtime and records
prereg_sha256/body_sha256/body_sha_match in results.json.
A rerun solely to fix an execution error is allowed and must be recorded
in results.json notes.
