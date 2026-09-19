# PREREG — NBPOLAR-X10-H2-SCALAR-ADJUDICATION (Tier-X, frozen)

Probe ID: `NBPOLAR-X10-H2-SCALAR-ADJUDICATION` · Tier X (non-claim, decoder-free).
Written BEFORE any frozen-input content read (2026-09-19; branch `codex/nbpolar-phase0`).

## Question
Adjudicate H2a–H2e (L2 order/metric non-generalization) solely from persisted
9-scalar instrumentation + coordinates for P20N (16 rows) + P20O (20 rows),
with P20M (9 rows) as overlap baseline; emit bounded recording-only
instrumentation requirements. Descriptive support labels
(SUPPORTED / REFUTED / NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS) with the single
strongest evidence line + exact descriptives; no significance claims.

## Exact parameters
- Main table: P20N 16 + P20O 20 = 36 rows; baseline P20M rows where fields overlap.
- H2a: within-block ordering by `l2_prefix_hazard_mean_bits` vs exactness; anomaly = exact arm pm exceeds failing arm pm (eps 1e-12).
- H2b: fails only; ratios fail/prefix and nbhd/prefix; SUPPORTED iff median fail/prefix > 1.10 (descriptive cutoff); arms A vs B, C/D separate.
- H2c: in-X fraction SUPPORTED iff >= 0.5 (descriptive); consolidate 12/14 (P20N) and 11/11-in-X-out-U (P20O).
- H2d: flat iff mean|fail_nbhd_floor − prefix_floor| <= 0.05 (descriptive).
- H2e: verdict NOT-DECIDABLE (series absent expected); list missing quantities.
- STOP (specific status, no input repair): missing/unreadable required file, malformed JSONL/summary, required count ≠ 16/20, nonfinite result.

## Exact command
```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && timeout 120 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python workspace/probes/nbpolar_x10_h2_scalar_adjudication/body.py
```

## Artifact list
Reads (worktree files only): P20N jsonl + summary, P20O jsonl + summary, P20M jsonl (optional), prereg.md + body.py (self-identity).
Stats-only (never opened, absence OK): raw_prior_orders_1p5m.json, raw_prior_orders_2m.json, raw_prior_1p5m.npz, raw_prior_2m.npz, alt_l2_tables_1p5m.npz, alt_l2_tables_2m.npz, l2_alt_hold_1p5m.py, l2_alt_maintain_2m.py.
Writes: `results.json` ONLY. Protected opens attempted: none (zero V25/pairs/1M/1.5M/2M stat-or-open).
Reruns on execution error allowed: 1, recorded.

## Frozen analysis body (byte-identical to body.py; runtime-asserted)

```python-x10-body
#!/usr/bin/env python3
"""NBPOLAR-X10-H2-SCALAR-ADJUDICATION — Tier-X probe body (frozen).

Decoder-free, RNG-free, tag-free. Stdlib only. Reads only the frozen
worktree artifacts named in TASK_PACKET.md; stats (never opens) any *.npz;
never stats/opens protected content (V25 counts NPZ / pairs parquet /
1M/1.5M/2M content). Only file written: results.json (this directory).
Runtime-asserts byte-identity with the fenced code block in prereg.md.
"""
import datetime
import hashlib
import json
import math
import os
import statistics
import sys
import time

PROBE_ID = "NBPOLAR-X10-H2-SCALAR-ADJUDICATION"
TIER = "X"
STATUS_OK = "X10_PROBE_COMPLETE_DESCRIPTIVE_ONLY"
COMMAND = ("cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && export OPENBLAS_NUM_THREADS=1 "
           "OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2 && timeout 120 "
           "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python "
           "workspace/probes/nbpolar_x10_h2_scalar_adjudication/body.py")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

# Repo-relative frozen inputs. required=True -> STOP if missing/unreadable.
P20N_JSONL = ".workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/per_block_arm_outcomes.jsonl"
P20N_SUM = ".workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/aggregate_summary.json"
P20O_JSONL = ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/per_block_arm_outcomes.jsonl"
P20O_SUM = ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/aggregate_summary.json"
P20M_JSONL = ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/per_block_arm_outcomes.jsonl"
# Optional geometry/runner inventory only (absence -> record absent, no STOP; npz never opened).
OPTIONAL_INVENTORY = [
    ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/raw_prior_orders_1p5m.json",
    ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/raw_prior_orders_2m.json",
    ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m/raw_prior_1p5m.npz",
    ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/raw_prior_2m.npz",
    ".workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/l2_alt_hold_1p5m/alt_l2_tables_1p5m.npz",
    ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/l2_alt_maintain_2m/alt_l2_tables_2m.npz",
    "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_hold_1p5m.py",
    "comparison_bench/src/comparison_bench/formal_ir/nbpolar/l2_alt_maintain_2m.py",
]
T0 = time.time()


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(65536), b""):
            h.update(ch)
    return h.hexdigest()


def strict_json_loads(text):
    def bad(v):
        raise ValueError("nonfinite constant %s" % v)
    return json.loads(text, parse_constant=bad)


def stat_entry(rel, required):
    ap = os.path.join(ROOT, rel)
    try:
        st = os.stat(ap)
        return {"path": rel, "present": True, "required": required,
                "size_bytes": st.st_size,
                "mtime_epoch": st.st_mtime,
                "mtime_iso": datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).isoformat()}
    except OSError as e:
        return {"path": rel, "present": False, "required": required,
                "size_bytes": None, "mtime_epoch": None, "mtime_iso": None,
                "error": "%s: %s" % (type(e).__name__, e)}


def finish(results_path, payload):
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
        f.write("\n")
    return results_path


def base_payload(extra_status, inventory, prereg_sha, body_sha, match, notes_extra):
    try:
        import resource
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    except Exception:
        rss = 0
    return {
        "probe_id": PROBE_ID, "tier": TIER, "status": extra_status,
        "question": ("Does persisted 9-scalar instrumentation + coordinates adjudicate H2 "
                     "(L2 order/metric non-generalization: alt restores blocks despite higher CE / "
                     "higher prefix hazard means)? Descriptive support labels only."),
        "prereg_sha256": prereg_sha, "body_sha256": body_sha, "body_sha_match": match,
        "artifact_inventory": {"artifacts": inventory, "protected_opens_attempted": False},
        "command": COMMAND,
        "interpreter": {"executable": sys.executable, "version": sys.version.splitlines()[0]},
        "wall_s": time.time() - T0, "rss_bytes": rss,
        "decoder_calls": 0, "rng_calls": 0, "tag_calls": 0,
        "writes": [], "notes": notes_extra,
    }


# --- prereg/body byte-identity (own probe files only; allowed) ---
PREREG = os.path.join(HERE, "prereg.md")
BODY = os.path.join(HERE, "body.py")
with open(PREREG, "r", encoding="utf-8") as f:
    prereg_text = f.read()
with open(BODY, "r", encoding="utf-8") as f:
    body_text = f.read()
_F = chr(96) * 3  # fence built at runtime so this source never holds a literal fence
_OPEN = _F + "python-x10-body"
block = prereg_text.split(_OPEN, 1)[1].split(_F, 1)[0]
if block.startswith("\n"):
    block = block[1:]
BODY_MATCH = (block == body_text)
assert BODY_MATCH, "body.py not byte-identical to prereg.md fenced block"
PREREG_SHA = sha_file(PREREG)
BODY_SHA = sha_file(BODY)
RESULTS = os.path.join(HERE, "results.json")

inventory = [stat_entry(P20N_JSONL, True), stat_entry(P20N_SUM, True),
             stat_entry(P20O_JSONL, True), stat_entry(P20O_SUM, True),
             stat_entry(P20M_JSONL, False)]
for rel in OPTIONAL_INVENTORY:
    inventory.append(stat_entry(rel, False))
by_path = {e["path"]: e for e in inventory}


def stop(status, detail, notes_extra=None):
    p = base_payload(status, inventory, PREREG_SHA, BODY_SHA, True, notes_extra or [])
    p["stop_detail"] = detail
    finish(RESULTS, p)
    sys.stderr.write("STOP %s: %s\n" % (status, detail))
    sys.exit(2)


for rel in (P20N_JSONL, P20N_SUM, P20O_JSONL, P20O_SUM):
    if not by_path[rel]["present"]:
        stop("X10_STOP_MISSING_FILE", "required file absent: %s" % rel)


def read_jsonl(rel):
    rows = []
    try:
        with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as f:
            for ln, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    rows.append((ln, strict_json_loads(line)))
                except ValueError as e:
                    stop("X10_STOP_MALFORMED_JSONL", "%s line %d: %s" % (rel, ln, e))
    except OSError as e:
        stop("X10_STOP_MISSING_FILE", "unreadable %s: %s" % (rel, e))
    return rows


def read_summary(rel):
    try:
        with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as f:
            return strict_json_loads(f.read())
    except ValueError as e:
        stop("X10_STOP_MALFORMED_SUMMARY", "%s: %s" % (rel, e))
    except OSError as e:
        stop("X10_STOP_MISSING_FILE", "unreadable %s: %s" % (rel, e))


n_rows = read_jsonl(P20N_JSONL)
o_rows = read_jsonl(P20O_JSONL)
m_rows = read_jsonl(P20M_JSONL) if by_path[P20M_JSONL]["present"] else []
if len(n_rows) != 16:
    stop("X10_STOP_RECORD_COUNT_MISMATCH", "P20N records %d, expected 16" % len(n_rows))
if len(o_rows) != 20:
    stop("X10_STOP_RECORD_COUNT_MISMATCH", "P20O records %d, expected 20" % len(o_rows))
n_sum = read_summary(P20N_SUM)
o_sum = read_summary(P20O_SUM)

# --- normalization helpers ---
def g(rec, *names):
    for k in names:
        if k in rec:
            return rec[k]
    return None


def num(x):
    if isinstance(x, bool) or x is None:
        return None
    if isinstance(x, (int, float)):
        v = float(x)
        return v if math.isfinite(v) else None
    if isinstance(x, str):
        try:
            v = float(x.strip())
            return v if math.isfinite(v) else None
        except ValueError:
            return None
    return None


def tri(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)) and math.isfinite(x) and x in (0, 1):
        return bool(x)
    if isinstance(x, str):
        s = x.strip().lower()
        if s in ("true", "yes", "1", "in", "in_prefix", "in-x", "inx"):
            return True
        if s in ("false", "no", "0", "out", "outside", "out_prefix", "out-x", "outx"):
            return False
    return None


FAIL_TOKS = ("fail", "mismatch", "error", "incorrect", "wrong", "no_verified", "no_success", "abort", "unverif")
OK_TOKS = ("exact", "success", " ok", "pass", "verif", "correct", "match")


def is_exact(rec):
    o = g(rec, "outcome", "status", "result", "verdict")
    if isinstance(o, str) and o.strip():
        s = " " + o.strip().lower() + " "
        if any(t in s for t in FAIL_TOKS):
            return False
        if any(t in s for t in OK_TOKS):
            return True
    for k in ("exact", "success", "ok"):
        if k in rec and isinstance(rec[k], bool):
            return rec[k]
    t = tri(g(rec, "tag_pass", "tag_ok", "tag", "mac_pass"))
    m = tri(g(rec, "label_match", "label_ok", "match", "exact_match"))
    if t is not None and m is not None:
        return bool(t and m)
    if t is not None:
        return bool(t)
    if m is not None:
        return bool(m)
    return None


ID_KEYS = {"session", "sess", "session_id", "dataset", "window", "range", "val_range",
           "block", "block_id", "block_index", "b", "blk", "arm", "method", "variant",
           "decoder", "config", "K1", "K2", "k1", "k2", "outcome", "status", "result",
           "verdict", "first_error_layer", "fail_layer", "error_layer", "layer",
           "first_error_coord", "fail_coord", "error_coord", "coord", "position",
           "nat_coord", "u", "u1", "tag_pass", "tag_ok", "tag", "mac_pass",
           "label_match", "label_ok", "match", "exact_match", "exact", "success", "ok",
           "key_bits", "keybits", "n_key_bits", "verified_bits", "bits"}


def norm_row(src, ln, rec):
    row = {"_src": src, "_line": ln}
    row["packet"] = src
    row["session"] = g(rec, "session", "sess", "session_id", "dataset", "window", "range", "val_range")
    row["block"] = g(rec, "block", "block_id", "block_index", "blk", "b")
    row["arm"] = g(rec, "arm", "method", "variant", "decoder", "config")
    for k in ("K1", "K2", "k1", "k2", "first_error_layer", "fail_layer", "error_layer",
              "first_error_coord", "fail_coord", "error_coord", "coord", "position",
              "nat_coord", "u", "u1", "key_bits", "keybits", "n_key_bits"):
        if k in rec and not isinstance(rec[k], (list, dict)):
            v = rec[k]
            row[k] = v if not isinstance(v, str) or len(v) <= 120 else v[:120]
    for k in ("outcome", "status", "result", "verdict"):
        if k in rec and isinstance(rec[k], str) and len(rec[k]) <= 120:
            row[k] = rec[k]
    for k in ("tag_pass", "tag_ok", "label_match", "label_ok", "match"):
        if k in rec and not isinstance(rec[k], (list, dict)):
            row[k] = rec[k]
    # nine-scalar instrumentation: keep every scalar whose key smells like instrumentation.
    for k, v in rec.items():
        if isinstance(v, (list, dict)):
            continue
        lk = k.lower()
        if k in row:
            continue
        if (lk.startswith("l2_") or lk.startswith("ce") or "hazard" in lk or "prefix" in lk
                or "fail" in lk or "floor" in lk or "nbhd" in lk or k in ID_KEYS):
            row[k] = v if not isinstance(v, str) or len(v) <= 120 else v[:120]
    return row


def pm_of(r):
    return num(r.get("l2_prefix_hazard_mean_bits", g(r, "prefix_hazard_mean_bits", "prefix_mean_bits",
                                                     "ce_mean_bits", "l2_prefix_mean_bits")))


table = ([norm_row("P20N", ln, r) for ln, r in n_rows]
         + [norm_row("P20O", ln, r) for ln, r in o_rows]
         + [norm_row("P20M", ln, r) for ln, r in m_rows])
for r in table:
    r["exact"] = is_exact(r)
    for v in r.values():
        if isinstance(v, float) and not math.isfinite(v):
            stop("X10_STOP_NONFINITE", "nonfinite scalar in record_table row %s line %s" % (r["_src"], r["_line"]))

main = [r for r in table if r["_src"] in ("P20N", "P20O")]


def rid(r):
    return "%s/%s/b%s/%s" % (r["_src"], r.get("session"), r.get("block"), r.get("arm"))


# --- H2a: average-quality ordering within blocks ---
blocks = {}
for r in main:
    blocks.setdefault((r["_src"], json.dumps(r.get("session"), sort_keys=True, default=str),
                       json.dumps(r.get("block"), sort_keys=True, default=str)), []).append(r)
n_eval = n_anom = 0
gaps = []
per_block = []
for key, rs in sorted(blocks.items(), key=lambda kv: str(kv[0])):
    ev = [(r, pm_of(r), r["exact"]) for r in rs]
    ev = [t for t in ev if t[1] is not None and t[2] is not None]
    if not any(e for _, _, e in ev) or not any(not e for _, _, e in ev):
        continue
    n_eval += 1
    fail_min = min(p for _, p, e in ev if not e)
    ex_max = max(p for _, p, e in ev if e)
    gap = ex_max - fail_min
    hit = gap > 1e-12
    n_anom += bool(hit)
    per_block.append({"block": key[0] + "|" + key[2], "n": len(ev),
                      "fail_min_pm": fail_min, "exact_max_pm": ex_max,
                      "gap": gap, "anomaly": bool(hit)})
    gaps.append((gap, key, ev))
if n_eval == 0:
    h2a_verdict, h2a_evid = "NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS", "no block has both exact and non-exact arms with prefix means"
elif n_anom >= 1:
    gaps.sort(reverse=True)
    gp, key, ev = gaps[0]
    det = "; ".join("%s pm=%.4f exact=%s" % (rid(r), p, e) for r, p, e in sorted(ev, key=lambda t: t[1]))
    h2a_verdict = "REFUTED"
    h2a_evid = "block %s %s: exact arm pm exceeds failing arm pm by %.4f bits [%s]" % (key[0], key[2], gp, det)
else:
    h2a_verdict = "SUPPORTED"
    h2a_evid = "all %d evaluable blocks: every exact arm pm <= every failing arm pm" % n_eval
h2a = {"verdict": h2a_verdict, "evidence": h2a_evid,
       "stats": {"n_blocks": len(blocks), "n_evaluable": n_eval, "n_anomaly": n_anom,
                 "per_block": per_block}}

# --- H2b: first-error hazard vs prefix mean (fails only) ---
def arm_group(a):
    s = str(a).strip().upper() if a is not None else "?"
    return s if s in ("A", "B", "C", "D") else "OTHER:" + s


ratios_all, nbhd_all, by_arm, strong = [], [], {}, None
for r in main:
    if r["exact"] is not True and r["exact"] is not False:
        continue
    if r["exact"]:
        continue
    pm = pm_of(r)
    fh = num(r.get("l2_fail_hazard_bits"))
    nm = num(r.get("l2_fail_nbhd_mean_bits"))
    if pm is not None and pm > 0 and fh is not None:
        q = fh / pm
        if not math.isfinite(q):
            stop("X10_STOP_NONFINITE", "nonfinite H2b ratio at %s" % rid(r))
        ratios_all.append(q)
        by_arm.setdefault(arm_group(r.get("arm")), []).append(q)
        if strong is None or q > strong[0]:
            strong = (q, r, fh, pm)
    if pm is not None and pm > 0 and nm is not None:
        qn = nm / pm
        if math.isfinite(qn):
            nbhd_all.append(qn)


def summ(xs):
    if not xs:
        return {"n": 0}
    s = sorted(xs)
    return {"n": len(xs), "min": s[0], "p50": statistics.median(s), "max": s[-1],
            "mean": statistics.fmean(s)}


if not ratios_all:
    h2b_verdict, h2b_evid = "NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS", "no failing record carries both l2_fail_hazard_bits and prefix mean"
else:
    med = statistics.median(ratios_all)
    r0, fh0, pm0 = strong[1], strong[2], strong[3]
    base = "median fail/prefix ratio %.3f over n=%d" % (med, len(ratios_all))
    if med > 1.10:
        h2b_verdict, h2b_evid = "SUPPORTED", base + " (>1.10 descriptive cutoff): fail sites elevated; strongest %s fh=%.4f pm=%.4f ratio=%.3f" % (rid(r0), fh0, pm0, strong[0])
    else:
        h2b_verdict, h2b_evid = "REFUTED", base + " (<=1.10 descriptive cutoff): no fail-site elevation; strongest %s ratio=%.3f" % (rid(r0), strong[0])
h2b = {"verdict": h2b_verdict, "evidence": h2b_evid,
       "stats": {"fail_prefix_ratio": summ(ratios_all),
                 "nbhd_prefix_ratio": summ(nbhd_all),
                 "by_arm_fail_prefix_ratio": {k: summ(v) for k, v in sorted(by_arm.items())}}}

# --- H2c: coordinates + cross-tab with X / U-domain ---
fails = [r for r in main if r["exact"] is False]
coords = {}
inX_known = inX_true = 0
p20n_inX_known = p20n_inX_true = 0
p20o_inX_true = p20o_outU_given_inX = 0
for r in fails:
    c = num(g(r, "first_error_coord", "fail_coord", "error_coord", "coord", "position", "nat_coord", "u1", "u"))
    if c is not None:
        coords.setdefault((r["_src"], arm_group(r.get("arm"))), []).append(c)
    ix = tri(r.get("l2_fail_in_prefix"))
    if ix is not None:
        inX_known += 1
        inX_true += bool(ix)
        if r["_src"] == "P20N":
            p20n_inX_known += 1
            p20n_inX_true += bool(ix)
        if r["_src"] == "P20O" and ix:
            p20o_inX_true += 1
            iu = tri(r.get("l2_fail_in_prefix_u_domain"))
            if iu is False:
                p20o_outU_given_inX += 1
coord_stats = {("%s/%s" % k): {"n": len(v), "min": min(v), "p50": statistics.median(v),
                               "max": max(v), "mean": statistics.fmean(v)}
               for k, v in sorted(coords.items(), key=lambda kv: str(kv[0]))}
if inX_known == 0:
    h2c_verdict, h2c_evid = "NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS", "l2_fail_in_prefix absent on all failing records"
else:
    frac = inX_true / inX_known
    xtab = "in-X %d/%d (%.3f); P20N in-X %d/%d vs frozen 12/14; P20O in-X %d with out-of-U %d vs frozen 11/11" % (
        inX_true, inX_known, frac, p20n_inX_true, p20n_inX_known, p20o_inX_true, p20o_outU_given_inX)
    if frac >= 0.5:
        h2c_verdict, h2c_evid = "SUPPORTED", xtab + " — fails concentrate inside prefix X (>=0.5 descriptive)"
    else:
        h2c_verdict, h2c_evid = "REFUTED", xtab + " — fails do not concentrate inside X (<0.5 descriptive)"
h2c = {"verdict": h2c_verdict, "evidence": h2c_evid,
       "stats": {"n_fails": len(fails), "inX_known": inX_known, "inX_true": inX_true,
                 "p20n_inX": [p20n_inX_true, p20n_inX_known],
                 "p20o_inX_true": p20o_inX_true, "p20o_outU_given_inX": p20o_outU_given_inX,
                 "coord_distribution_per_src_arm": coord_stats}}

# --- H2d: floor separation (expected flat) ---
diffs = []
for r in main:
    f = num(r.get("l2_fail_nbhd_floor_frac"))
    p = num(r.get("l2_prefix_floor_frac"))
    if f is not None and p is not None:
        d = abs(f - p)
        if not math.isfinite(d):
            stop("X10_STOP_NONFINITE", "nonfinite H2d diff at %s" % rid(r))
        diffs.append(d)
if not diffs:
    h2d_verdict, h2d_evid = "NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS", "no record carries both floor fractions"
else:
    mad = statistics.fmean(diffs)
    if mad <= 0.05:
        h2d_verdict, h2d_evid = "SUPPORTED", "flat confirmed: mean|fail_nbhd_floor - prefix_floor| = %.4f over n=%d (<=0.05 descriptive)" % (mad, len(diffs))
    else:
        h2d_verdict, h2d_evid = "REFUTED", "separation present: mean|diff| = %.4f over n=%d (>0.05 descriptive)" % (mad, len(diffs))
h2d = {"verdict": h2d_verdict, "evidence": h2d_evid,
       "stats": {"n_pairs": len(diffs), "mean_abs_diff": (statistics.fmean(diffs) if diffs else None),
                 "max_abs_diff": (max(diffs) if diffs else None)}}

# --- H2e: static-order geometry gap ---
series_keys = set()
for _, rec in n_rows + o_rows + m_rows:
    for k, v in rec.items():
        if isinstance(v, (list, dict)) and any(t in k.lower() for t in
                                               ("hazard", "position", "order", "series", "cell", "u1", "per_")):
            series_keys.add(k)
h2e = {"verdict": "NOT-DECIDABLE-FROM-PERSISTED-ARTIFACTS",
       "evidence": ("per-block (b,u1) sequences and per-position hazard series are absent "
                    "(prefix means only); series-like keys found: %s" % sorted(series_keys)),
       "stats": {"series_like_keys_present": sorted(series_keys)},
       "missing_quantities": [
           "per-position (b,u1) natural-coordinate sequence per block",
           "per-position L2 hazard (bits) over the full block using true cells",
           "prefix-membership mask per position (X) and u-domain mask per position (P20O)",
           "hazard rank of the first-error coordinate within its block distribution",
           "frozen static order permutation actually decoded under",
       ]}

hypothesis_table = [
    {"id": "H2a", "verdict": h2a_verdict, "evidence": h2a_evid},
    {"id": "H2b", "verdict": h2b_verdict, "evidence": h2b_evid},
    {"id": "H2c", "verdict": h2c_verdict, "evidence": h2c_evid},
    {"id": "H2d", "verdict": h2d_verdict, "evidence": h2d_evid},
    {"id": "H2e", "verdict": h2e["verdict"], "evidence": h2e["evidence"]},
]

instrumentation_requirements = [
    {"id": "IR-1", "what": "Per-record hazard histograms over the block using true cells: 64 log-spaced bins x {prefix, outside}.",
     "h_link": "H2a/H2b", "size_cap": "<= 64x2 int32 counts + 65 float64 edges, ~1 KB/record, recording-only.",
     "truth_isolation": "Computed post-hoc from frozen hazard table + frozen truth; never an input to decode/tag decisions."},
    {"id": "IR-2", "what": "Hazard-rank percentile of the first-error coordinate within its block hazard distribution (one float; null when exact).",
     "h_link": "H2b/H2c", "size_cap": "1 float64/record.",
     "truth_isolation": "Post-hoc rank join only; does not steer the decoder."},
    {"id": "IR-3", "what": "Count/measure of prefix positions above a hazard threshold (count + fraction + max, at 1-2 frozen thresholds).",
     "h_link": "H2a", "size_cap": "<= 3 scalars/threshold, <= 2 thresholds/record.",
     "truth_isolation": "Thresholds frozen before the run; counts recorded, never fed back."},
    {"id": "IR-4", "what": "Top-k hazardous positions with block ranks (k<=16): coordinate + hazard + prefix flag each.",
     "h_link": "H2c/H2e", "size_cap": "<= 16x3 scalars/record.",
     "truth_isolation": "Hazard-order listing only; error-coordinate join is post-hoc."},
    {"id": "IR-5", "what": "Capped per-position series (only if IR-1..IR-4 leave H2 undecided): per-position (hazard, prefix flag), block-length capped at 4096 entries, float32.",
     "h_link": "H2e", "size_cap": "<= 4096x2 float32 (~32 KB)/record; omit on longer blocks with explicit truncation flag.",
     "truth_isolation": "Recording-only dump of the frozen hazard table + masks; decoder consumes only the frozen order as before."},
]

notes = [
    "Assumption: arm A = incumbent contrast, arm B = alt contrast (packet context); arms C/D reported separately, never merged.",
    "Descriptive cutoffs (1.10 / 0.5 / 0.05) are labeling aids, not significance tests; no p-values computed.",
    "P20M baseline rows included where fields overlap; H2a-H2d use P20N+P20O main table only.",
    "NPZ candidates stat-only, never opened; no protected paths touched (no V25/pairs/1M/1.5M/2M stat or open).",
    "Execution-error reruns so far: 0.",
]


def ce_hint(s):
    if not isinstance(s, dict):
        return None
    out = {}
    def walk(d, pre=""):
        if isinstance(d, dict):
            for k, v in d.items():
                lk = (pre + "." + str(k)).lower()
                if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and any(
                        t in lk for t in ("ce", "leak", "hazard", "mean", "eff")):
                    out[lk] = float(v)
                elif isinstance(v, dict) and len(pre) < 60:
                    walk(v, pre + "." + str(k))
    walk(s)
    return dict(list(out.items())[:24])


payload = base_payload(STATUS_OK, inventory, PREREG_SHA, BODY_SHA, True, notes)
payload.update({
    "record_table": table,
    "record_counts": {"P20N": len(n_rows), "P20O": len(o_rows), "P20M": len(m_rows),
                      "main_36": len(main), "expected": {"P20N": 16, "P20O": 20, "P20M": 9}},
    "summary_context": {"P20N_ce_hint": ce_hint(n_sum), "P20O_ce_hint": ce_hint(o_sum)},
    "hypothesis_table": hypothesis_table,
    "h2a": h2a, "h2b": h2b, "h2c": h2c, "h2d": h2d, "h2e": h2e,
    "instrumentation_requirements": instrumentation_requirements,
})
for v in (payload["wall_s"],):
    if not math.isfinite(v):
        stop("X10_STOP_NONFINITE", "nonfinite wall_s")
finish(RESULTS, payload)
st = os.stat(RESULTS)
payload["writes"] = [{"path": "workspace/probes/nbpolar_x10_h2_scalar_adjudication/results.json",
                      "size_bytes": st.st_size, "mtime_epoch": st.st_mtime,
                      "mtime_iso": datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc).isoformat()}]
finish(RESULTS, payload)
print("X10 probe complete: %d main + %d baseline rows; %s" % (
    len(main), len(table) - len(main),
    "; ".join(h["id"] + "=" + h["verdict"] for h in hypothesis_table)))
```
