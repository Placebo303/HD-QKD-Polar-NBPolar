1. Question: Does executing the accepted GF(32) SC q-squared logaddexp.reduce minus-node in contiguous row chunks [32,128,512,2048] preserve bitwise/exception parity with the direct path across primitive boundary sizes and full-SC semantic controls while extending the reachable direct-SC ceiling through N=262144 (Tier-X non-claim descriptive record only; no threshold, winner, candidate, acceptance, attempt, or status change).
2. Parameters: probe seed=2026091780 (single RNG stream, order: primitives rows-asc x kinds uniform/wide/support -> N=64 controls F1/F2/F3/K4/C3/C4/T5 -> N=256 controls same -> scaling blocks N asc; C4 search draws data-dependent in count, stream-ordered); GF(32) primitive polynomial 37, alpha=2, float64, accepted _combination_index verified entrywise against field ops; probe-local _minus_block_chunked executes per contiguous row slice exactly gathered=first[:,index]+second[:,None,:] then np.logaddexp.reduce(gathered,axis=2) then accepted _normalize_rows over the full matrix; chunk rows=[32,128,512,2048]; temporary monkeypatch of sc._minus_block inside try/finally with is-identity verify after every run and at process end; primitive rows=[1,31,32,33,127,128,129,511,512,513,2048,8192] x kinds uniform[-20,0]/wide[-160,0]/deterministic -inf support (>=1 finite/row, values uniform[-20,0]) with direct-vs-every-chunk exact array equality + max finite abs err + support masks; full-SC N=[64,256] controls F1 moderate uniform[-20,0], F2 wide uniform[-160,0], F3 base uniform[-20,0] rows j%5==4 even symbols -inf, K4 25pct positions sorted rng.choice with values=direct undisclosed-decision argmax verified finite, C3 X11 pattern base uniform[-12,0] rows j%3==0 odd symbols -inf with positive-support values at K4 positions, C4 impossible search (even rows symbol-0-only, schedule pos=(t*7+arange(k)*3)%N k=16 then 32, t<400) requiring identical ImpossibleDisclosedValueError type+message per chunk, T5 exact-tie zeros/ramp arange-31/near-tie zeros with col1=-1e-9, V0 16-case invalid/nonfinite validation contract baselined before any monkeypatch entry with identical type+message per chunk, per-chunk parity fields exception type/message status u_hat x_hat decision metrics/scores known mask/count provenance; scaling one accepted-_normalize_rows-normalized uniform-[-20,0] block per N, direct+chunk512 paired N=[1024,4096,16384,65536], chunk512-only N=[131072,262144], exactly 3 timed reps/arm through N=16384 else exactly 1/arm, direct always before chunked, no warmups, wall+RSS per arm, resource failure=descriptive ceiling; memory estimates (N//2)*q*q*8 direct vs min(chunk,N//2)*q*q*8; results.json single record initialized before first semantic control and rewritten after every cell; bounds ulimit -v 2097152 + 1800s wall; single execution, one execution-error rerun allowed only unchanged with both recorded; semantic-mismatch/restoration-failure/external-input/production-edit STOP without rerun, no commit/push.
3. Command: cwd=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar; ulimit -v 2097152; timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - < /tmp/x12_body.py (staged byte-identically from the prereg python fence; body self-verifies staged bytes equal embedded bytes before any benchmark; single execution).

```python
"""X12 Tier-X frozen body: exact chunked minus-node SC scaling probe (descriptive only).

Accepted direct sc_decode vs probe-only exact row-chunked minus-node path that
temporarily monkeypatches the imported SC module's _minus_block (restored in
finally with is-identity proof after every run and at process end). Chunking
controls allocation only: each contiguous row slice executes the exact accepted
expression `gathered = first[:, index] + second[:, None, :]` then the same
`np.logaddexp.reduce(gathered, axis=2)` and the accepted _normalize_rows over
the full matrix. No change to axis order, dtype, field tables, support,
tie-breaking, or exception behavior.

Frozen matrix: probe seed 2026091780, single RNG stream in order primitives
(rows ascending x kinds uniform/wide/support) -> N=64 controls -> N=256
controls -> scaling blocks N ascending (C4 search draws are data-dependent in
count but stream-ordered); chunk rows [32,128,512,2048]; primitive rows
[1,31,32,33,127,128,129,511,512,513,2048,8192]; full-SC controls F1/F2/F3/K4/C3/
C4/T5 at N=64,256 plus the V0 16-case validation contract (baselined before any
monkeypatch entry); scaling direct+chunk512 paired at N=1024/4096/16384/65536
and chunk512-only at N=131072/262144 with 3 timed reps per arm through N=16384
and 1 per arm at N>=65536, direct always before chunked, no warmups. ONE
descriptive results.json record, checkpointed after every completed cell. No
artifact, evidence-root, raw/held-out/real/EVAL, tag, gate, FWHT/APP/SCL
access. No threshold, winner, candidate, acceptance, or label.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import sys
import time
import traceback
from pathlib import Path

import numpy as np

T0 = time.monotonic()

REPO = Path("/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar")
PROBE_DIR = REPO / "workspace" / "probes" / "nbpolar_x12_exact_chunked_sc_scaling"
PREREG_PATH = PROBE_DIR / "prereg.md"
RESULTS_PATH = PROBE_DIR / "results.json"
BODY_PATH = Path("/tmp/x12_body.py")
INTERPRETER = "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python"
COMMAND_TEXT = "ulimit -v 2097152; timeout 1800 " + INTERPRETER + " - < /tmp/x12_body.py"

SEED = 2026091780
Q = 32
ALPHA = 2
POLY = 37
CHUNKS = [32, 128, 512, 2048]
PRIM_ROWS = [1, 31, 32, 33, 127, 128, 129, 511, 512, 513, 2048, 8192]
PRIM_KINDS = ["uniform_m20", "wide_m160", "neginf_support"]
SC_NS = [64, 256]
SCALE_PAIRED_NS = [1024, 4096, 16384, 65536]
SCALE_CHUNKONLY_NS = [131072, 262144]
N_REP_SMALL = 3
N_REP_BIG = 1
VSZ_KB = 2097152
WALL_LIMIT_S = 1800
ATTEMPT = int(os.environ.get("X12_ATTEMPT", "1"))
PRIOR_SUMMARY_RAW = os.environ.get("X12_PRIOR_SUMMARY", "")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def fp(arr):
    return sha256_bytes(np.ascontiguousarray(np.asarray(arr)).tobytes())


def rss_peak():
    ru = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    hwm = None
    try:
        for line in open("/proc/self/status", encoding="utf-8"):
            if line.startswith("VmHWM:"):
                hwm = int(line.split()[1]) * 1024
                break
    except OSError:
        hwm = None
    vals = [v for v in (ru, hwm) if v]
    return {"ru_maxrss_bytes": ru, "vmhwm_bytes": hwm, "peak_bytes": max(vals) if vals else None}


PREREG_SHA = sha256_bytes(PREREG_PATH.read_bytes())
BODY_SHA = sha256_bytes(BODY_PATH.read_bytes())
_prereg_text = PREREG_PATH.read_text(encoding="utf-8")
_FENCE = "```python\n"
_f0 = _prereg_text.index(_FENCE) + len(_FENCE)
_f1 = _prereg_text.index("\n```", _f0)
_embedded = _prereg_text[_f0:_f1]
BODY_MATCH = bool(_embedded.encode("utf-8") == BODY_PATH.read_bytes())
if not BODY_MATCH:
    print("FATAL body_sha_match false; refusing to run the staged body")
    raise SystemExit(2)

REC = {
    "probe_id": "nbpolar_x12_exact_chunked_sc_scaling",
    "tier": "X",
    "status": "X12_RUNNING_CHECKPOINT",
    "question": "Exact row-chunked accepted-SC minus-node bitwise/exception parity and reachable-N ceiling (descriptive only)",
    "parameters": {
        "seed": SEED, "q": Q, "alpha": ALPHA, "primitive_polynomial": POLY,
        "chunk_rows": CHUNKS, "primitive_rows": PRIM_ROWS, "primitive_kinds": PRIM_KINDS,
        "full_sc_N": SC_NS,
        "scaling_paired_N": SCALE_PAIRED_NS, "scaling_chunkonly_N": SCALE_CHUNKONLY_NS,
        "scaling_chunk": 512,
        "timed_reps_per_arm_through_16384": N_REP_SMALL,
        "timed_reps_per_arm_at_or_above_65536": N_REP_BIG,
        "arm_order": "direct_before_chunked_every_rep_no_warmups",
        "rng_stream_order": "primitives(rows asc x kinds uniform/wide/support)->N64 controls->N256 controls->scaling blocks N asc; C4 search draws data-dependent in count, stream-ordered",
    },
    "command": COMMAND_TEXT,
    "prereg_sha256": PREREG_SHA,
    "body_sha256": BODY_SHA,
    "body_sha_match": BODY_MATCH,
    "field_identity": {},
    "validation_contract": {"cases": [], "all_parity": None},
    "primitive_cells": [],
    "full_sc": {},
    "scaling_cells": [],
    "restoration": {"invocations": 0, "all_pre_is_orig": None, "all_post_is_orig": None, "final_is_orig": None},
    "progress": {"completed_stages": [], "highest_completed_N": None},
    "executions": [],
    "rss_peak": None,
    "wall_s": None,
    "claim_boundary": "Tier-X non-claim probe: equality flags, errors, timings and RSS are descriptive records only; no threshold, winner, candidate, acceptance, or scientific label.",
}


def save():
    REC["wall_s"] = time.monotonic() - T0
    REC["rss_peak"] = rss_peak()
    RESULTS_PATH.write_text(json.dumps(REC, indent=1) + "\n", encoding="utf-8")


def stop(reason, detail):
    REC["status"] = "STOPPED_" + str(reason).upper()
    REC["stop_detail"] = detail
    save()
    print("STOP: %s %s" % (reason, json.dumps(detail)[:500]))
    raise SystemExit(2)


def main():
    sys.path.insert(0, str(REPO / "comparison_bench" / "src"))
    import comparison_bench.formal_ir.nbpolar.sc as sc_mod
    from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
    from comparison_bench.formal_ir.nbpolar.sc import (
        ImpossibleDisclosedValueError,
        _combination_index,
        _minus_block,
        _normalize_rows,
        sc_decode,
    )

    field = make_gf32()
    if int(field.q) != Q:
        stop("field_identity", {"q": int(field.q)})
    if int(getattr(field, "primitive_polynomial", -1)) != POLY:
        stop("field_identity", {"primitive_polynomial": getattr(field, "primitive_polynomial", None)})
    ORIG_MINUS = sc_mod._minus_block
    if ORIG_MINUS is not _minus_block:
        stop("module_identity", {"detail": "imported _minus_block is not sc_mod._minus_block at startup"})
    index = _combination_index(field, ALPHA, Q)
    for u in range(Q):
        for v in range(Q):
            if int(index[u, v]) != int(field.add(u, field.mul(ALPHA, v))):
                stop("index_identity", {"u": u, "v": v})
    REC["field_identity"] = {
        "q": int(field.q), "alpha": ALPHA, "primitive_polynomial": int(getattr(field, "primitive_polynomial")),
        "combination_index_matches_field_ops": True, "import_is_module_attr": True,
    }
    save()

    IDENT_LOG = []

    def make_chunked(chunk):
        c = int(chunk)
        if c <= 0:
            raise ValueError("chunk rows must be positive")
        def _minus_block_chunked(first, second, index_arg):
            rows = first.shape[0]
            out = np.empty((rows, Q), dtype=np.float64)
            for s in range(0, rows, c):
                e = s + c if s + c < rows else rows
                gathered = first[s:e][:, index_arg] + second[s:e][:, None, :]
                out[s:e] = np.logaddexp.reduce(gathered, axis=2)
            return _normalize_rows(out)
        _minus_block_chunked.chunk_rows = c
        return _minus_block_chunked

    def run_sc(metrics, chunk, kp=None, kv=None):
        if chunk is None:
            return sc_decode(metrics, field=field, alpha=ALPHA, known_positions=kp, known_values=kv)
        pre = sc_mod._minus_block is ORIG_MINUS
        sc_mod._minus_block = make_chunked(chunk)
        try:
            return sc_decode(metrics, field=field, alpha=ALPHA, known_positions=kp, known_values=kv)
        finally:
            sc_mod._minus_block = ORIG_MINUS
            post = sc_mod._minus_block is ORIG_MINUS
            IDENT_LOG.append({"pre_is_orig": bool(pre), "post_is_orig": bool(post)})
            if not (pre and post):
                stop("restoration_failure", {"chunk": chunk, "pre_is_orig": bool(pre), "post_is_orig": bool(post)})

    def attempt_sc(metrics, chunk, kp=None, kv=None):
        try:
            return {"raised": False, "result": run_sc(metrics, chunk, kp, kv)}
        except Exception as exc:
            return {"raised": True, "exc_type": type(exc).__name__, "message": str(exc)}

    def exc_summary(att):
        return {"raised": att["raised"], "exc_type": att.get("exc_type"), "message": att.get("message")}

    def cmp_valid(d, h):
        dm_d = np.asarray(d.decision_metrics)
        dm_h = np.asarray(h.decision_metrics)
        ds_d = np.asarray(d.decision_log_scores)
        ds_h = np.asarray(h.decision_log_scores)
        both = np.isfinite(dm_d) & np.isfinite(dm_h)
        ferr = float(np.abs(dm_d[both] - dm_h[both]).max()) if both.any() else None
        boths = np.isfinite(ds_d) & np.isfinite(ds_h)
        serr = float(np.abs(ds_d[boths] - ds_h[boths]).max()) if boths.any() else None
        return {
            "status_direct": d.status, "status_chunk": h.status,
            "status_equal": bool(d.status == h.status),
            "u_hat_exact": bool(np.array_equal(np.asarray(d.u_hat), np.asarray(h.u_hat))),
            "u_hat_mismatches": int((np.asarray(d.u_hat) != np.asarray(h.u_hat)).sum()),
            "x_hat_exact": bool(np.array_equal(np.asarray(d.x_hat), np.asarray(h.x_hat))),
            "x_hat_mismatches": int((np.asarray(d.x_hat) != np.asarray(h.x_hat)).sum()),
            "metrics_exact": bool(np.array_equal(dm_d, dm_h)),
            "max_finite_metric_abs_err": ferr,
            "metrics_support_equal": bool((np.isfinite(dm_d) == np.isfinite(dm_h)).all()),
            "metrics_argmax_mismatches": int((np.argmax(dm_d, axis=1) != np.argmax(dm_h, axis=1)).sum()),
            "scores_exact": bool(np.array_equal(ds_d, ds_h)),
            "max_finite_score_abs_err": serr,
            "known_mask_exact": bool(np.array_equal(np.asarray(d.known_mask), np.asarray(h.known_mask))),
            "known_count_equal": bool(int(d.known_count) == int(h.known_count)),
            "known_count": int(d.known_count),
            "provenance_equal": bool(d.metric_provenance == h.metric_provenance),
            "u_hat_sha_direct": fp(d.u_hat), "u_hat_sha_chunk": fp(h.u_hat),
            "metrics_sha_direct": fp(dm_d), "metrics_sha_chunk": fp(dm_h),
        }

    def parity_ok(c):
        return bool(c["status_equal"] and c["u_hat_exact"] and c["x_hat_exact"]
                    and c["metrics_exact"] and c["scores_exact"] and c["known_mask_exact"]
                    and c["known_count_equal"] and c["provenance_equal"] and c["metrics_support_equal"])

    def refresh_restoration():
        REC["restoration"] = {
            "invocations": len(IDENT_LOG),
            "all_pre_is_orig": all(e["pre_is_orig"] for e in IDENT_LOG) if IDENT_LOG else None,
            "all_post_is_orig": all(e["post_is_orig"] for e in IDENT_LOG) if IDENT_LOG else None,
            "final_is_orig": bool(sc_mod._minus_block is ORIG_MINUS),
        }

    def complete(stage, n=None):
        REC["progress"]["completed_stages"].append(stage)
        if n is not None and (REC["progress"]["highest_completed_N"] is None or n > REC["progress"]["highest_completed_N"]):
            REC["progress"]["highest_completed_N"] = int(n)
        refresh_restoration()
        save()

    rng = np.random.default_rng(SEED)

    # ---- V0: accepted invalid/nonfinite input-validation contract, baselined BEFORE any monkeypatch entry.
    base8 = np.zeros((8, Q), dtype=np.float64)
    _nan = base8.copy(); _nan[0, 0] = np.nan
    _pinf = base8.copy(); _pinf[1, 1] = np.inf
    _row = base8.copy(); _row[2, :] = -np.inf
    _wide = np.zeros((8, Q + 1), dtype=np.float64)
    _n48 = np.zeros((48, Q), dtype=np.float64)
    _flat = np.zeros(Q, dtype=np.float64)
    _bbool = np.zeros((8, Q), dtype=bool)
    V0 = [
        ("nan_entry", {"logp_x": _nan}),
        ("posinf_entry", {"logp_x": _pinf}),
        ("all_neginf_row", {"logp_x": _row}),
        ("width_mismatch", {"logp_x": _wide}),
        ("non_power_of_two_N", {"logp_x": _n48}),
        ("rank1_input", {"logp_x": _flat}),
        ("boolean_input", {"logp_x": _bbool}),
        ("positions_out_of_range", {"logp_x": base8, "known_positions": np.array([0, 99]), "known_values": np.array([0, 0])}),
        ("positions_repeat", {"logp_x": base8, "known_positions": np.array([3, 3]), "known_values": np.array([1, 2])}),
        ("positions_values_length", {"logp_x": base8, "known_positions": np.array([0, 1]), "known_values": np.array([0])}),
        ("positions_none_values_given", {"logp_x": base8, "known_positions": None, "known_values": np.array([0])}),
        ("positions_given_values_none", {"logp_x": base8, "known_positions": np.array([0]), "known_values": None}),
        ("float_positions", {"logp_x": base8, "known_positions": np.array([0.5]), "known_values": np.array([0])}),
        ("boolean_positions", {"logp_x": base8, "known_positions": np.array([True, False, True, False, True, False, True, False]), "known_values": np.zeros(8, dtype=np.int64)}),
        ("value_out_of_range", {"logp_x": base8, "known_positions": np.array([0]), "known_values": np.array([32])}),
        ("negative_position", {"logp_x": base8, "known_positions": np.array([-1]), "known_values": np.array([0])}),
    ]
    if sc_mod._minus_block is not ORIG_MINUS:
        stop("restoration_failure", {"detail": "monkeypatch active before V0 baseline"})
    for name, kw in V0:
        att0 = attempt_sc(kw["logp_x"], None, kw.get("known_positions"), kw.get("known_values"))
        if not att0["raised"]:
            stop("control_not_established", {"control": "V0_" + name, "detail": "baseline valid input did not raise"})
        entry = {"name": name, "baseline": exc_summary(att0), "per_chunk": {}, "parity": None}
        ok = True
        for chunk in CHUNKS:
            attc = attempt_sc(kw["logp_x"], chunk, kw.get("known_positions"), kw.get("known_values"))
            par = bool(attc["raised"] and attc["exc_type"] == att0["exc_type"] and attc["message"] == att0["message"])
            entry["per_chunk"][str(chunk)] = dict(exc_summary(attc), parity=par)
            ok = ok and par
        entry["parity"] = bool(ok)
        REC["validation_contract"]["cases"].append(entry)
        if not ok:
            complete("V0_" + name)
            stop("semantic_mismatch", {"control": "V0_" + name, "entry": entry})
        print("V0 %s baseline=%s parity=%s" % (name, att0["exc_type"], ok), flush=True)
    REC["validation_contract"]["all_parity"] = all(c["parity"] for c in REC["validation_contract"]["cases"])
    complete("V0_all")

    # ---- Primitive exact-chunked minus-node comparisons.
    def gen_pair(kind, rows):
        if kind == "uniform_m20":
            return rng.uniform(-20.0, 0.0, (rows, Q)), rng.uniform(-20.0, 0.0, (rows, Q))
        if kind == "wide_m160":
            return rng.uniform(-160.0, 0.0, (rows, Q)), rng.uniform(-160.0, 0.0, (rows, Q))
        if kind == "neginf_support":
            a = rng.uniform(-20.0, 0.0, (rows, Q))
            b = rng.uniform(-20.0, 0.0, (rows, Q))
            mask_a = ((np.arange(rows)[:, None] * 7 + np.arange(Q)[None, :]) % 4 == 0)
            mask_b = ((np.arange(rows)[:, None] * 5 + np.arange(Q)[None, :] + 1) % 4 == 0)
            a[mask_a] = -np.inf
            b[mask_b] = -np.inf
            for i in range(rows):
                if not np.isfinite(a[i]).any():
                    a[i, (i * 5) % Q] = -5.0
                if not np.isfinite(b[i]).any():
                    b[i, (i * 3 + 1) % Q] = -5.0
            return a, b
        raise ValueError("unknown primitive kind " + str(kind))

    for rows in PRIM_ROWS:
        for kind in PRIM_KINDS:
            first, second = gen_pair(kind, rows)
            ref = _minus_block(first, second, index)
            cell = {"rows": rows, "kind": kind,
                    "direct_finite_entries": int(np.isfinite(ref).sum()),
                    "per_chunk": {}}
            for chunk in CHUNKS:
                got = make_chunked(chunk)(first, second, index)
                both = np.isfinite(ref) & np.isfinite(got)
                err = float(np.abs(ref[both] - got[both]).max()) if both.any() else None
                sup_eq = bool((np.isfinite(ref) == np.isfinite(got)).all())
                ex = bool(np.array_equal(ref, got))
                cell["per_chunk"][str(chunk)] = {
                    "exact_equal": ex,
                    "max_finite_abs_err": err,
                    "support_equal": sup_eq,
                    "support_mismatch_rows": int((np.isfinite(ref) != np.isfinite(got)).any(axis=1).sum()),
                    "direct_gather_bytes": rows * Q * Q * 8,
                    "chunked_temp_bytes": min(chunk, rows) * Q * Q * 8,
                }
                if not (ex and sup_eq):
                    REC["primitive_cells"].append(cell)
                    complete("prim_rows=%d_kind=%s" % (rows, kind))
                    stop("semantic_mismatch", {"control": "primitive", "rows": rows, "kind": kind,
                                               "chunk": chunk, "cell": cell["per_chunk"][str(chunk)]})
            REC["primitive_cells"].append(cell)
            complete("prim_rows=%d_kind=%s" % (rows, kind))
            print("prim rows=%d kind=%s exact_all=%s" % (rows, kind, all(v["exact_equal"] for v in cell["per_chunk"].values())), flush=True)

    # ---- Full-SC semantic controls at N=64 and N=256.
    for N in SC_NS:
        nrec = {"N": N, "controls": {}}
        REC["full_sc"][str(N)] = nrec
        f1 = rng.uniform(-20.0, 0.0, (N, Q))
        f2 = rng.uniform(-160.0, 0.0, (N, Q))
        f3 = rng.uniform(-20.0, 0.0, (N, Q))
        for j in range(N):
            if j % 5 == 4:
                f3[j, 0::2] = -np.inf
        pos = np.sort(rng.choice(N, N // 4, replace=False)).astype(np.int64)

        def undisclosed_control(cid, metrics):
            att_d = attempt_sc(metrics, None)
            if att_d["raised"]:
                return {"control": cid, "direct": exc_summary(att_d), "per_chunk": {}, "parity": False,
                        "note": "direct raised on valid control"}
            uh_d = np.asarray(att_d["result"].u_hat)
            entry = {"control": cid, "direct": {"raised": False, "status": att_d["result"].status,
                                                "u_hat_sha": fp(uh_d),
                                                "u_hat_sum": int(uh_d.sum()),
                                                "coord0_choice": int(uh_d[0]),
                                                "u_hat_all_zero": bool((uh_d == 0).all()),
                                                "metrics_sha": fp(att_d["result"].decision_metrics)},
                     "per_chunk": {}, "parity": None}
            ok = True
            for chunk in CHUNKS:
                att_c = attempt_sc(metrics, chunk)
                if att_c["raised"]:
                    entry["per_chunk"][str(chunk)] = dict(exc_summary(att_c), parity=False)
                    ok = False
                else:
                    cmp = cmp_valid(att_d["result"], att_c["result"])
                    par = parity_ok(cmp)
                    entry["per_chunk"][str(chunk)] = dict(cmp, parity=par)
                    ok = ok and par
            entry["parity"] = bool(ok)
            return entry

        def disclosed_control(cid, metrics, positions, values):
            att_d = attempt_sc(metrics, None, positions, values)
            if att_d["raised"]:
                return {"control": cid, "direct": exc_summary(att_d), "per_chunk": {}, "parity": False,
                        "note": "direct raised on valid control"}
            entry = {"control": cid, "direct": {"raised": False, "status": att_d["result"].status,
                                                "u_hat_sha": fp(att_d["result"].u_hat),
                                                "metrics_sha": fp(att_d["result"].decision_metrics)},
                     "positions": [int(v) for v in np.asarray(positions).tolist()],
                     "values": [int(v) for v in np.asarray(values).tolist()],
                     "per_chunk": {}, "parity": None}
            ok = True
            for chunk in CHUNKS:
                att_c = attempt_sc(metrics, chunk, positions, values)
                if att_c["raised"]:
                    entry["per_chunk"][str(chunk)] = dict(exc_summary(att_c), parity=False)
                    ok = False
                else:
                    cmp = cmp_valid(att_d["result"], att_c["result"])
                    par = parity_ok(cmp)
                    entry["per_chunk"][str(chunk)] = dict(cmp, parity=par)
                    ok = ok and par
            entry["parity"] = bool(ok)
            return entry

        for cid, metrics in (("F1_moderate", f1), ("F2_wide", f2),
                             ("F3_neginf_jmod5_evenoff", f3)):
            entry = undisclosed_control(cid, metrics)
            nrec["controls"][cid] = entry
            if not entry["parity"]:
                complete("N%d_%s" % (N, cid), N)
                stop("semantic_mismatch", {"control": cid, "N": N})
            complete("N%d_%s" % (N, cid), N)
            print("N=%d %s parity=%s" % (N, cid, entry["parity"]), flush=True)

        # K4: 25% known coordinates from direct-positive support on the moderate block.
        att_free = attempt_sc(f1, None)
        if att_free["raised"]:
            complete("N%d_K4" % N, N)
            stop("control_not_established", {"control": "K4", "N": N, "direct": exc_summary(att_free)})
        dm_free = np.asarray(att_free["result"].decision_metrics)
        v4 = np.array([int(np.argmax(dm_free[p])) for p in pos.tolist()], dtype=np.int64)
        if not all(bool(np.isfinite(dm_free[p, v])) for p, v in zip(pos.tolist(), v4.tolist())):
            complete("N%d_K4" % N, N)
            stop("control_not_established", {"control": "K4", "N": N,
                                             "detail": "argmax-selected values lack finite direct support"})
        entry = disclosed_control("K4_known25pct_positive_support", f1, pos, v4)
        nrec["controls"]["K4_known25pct_positive_support"] = entry
        if not entry["parity"]:
            complete("N%d_K4" % N, N)
            stop("semantic_mismatch", {"control": "K4", "N": N})
        complete("N%d_K4" % N, N)
        print("N=%d K4 parity=%s" % (N, entry["parity"]), flush=True)

        # C3: X11 pattern (base uniform[-12,0]; rows j%3==0 odd symbols -inf) + positive-support values at pos.
        c3 = rng.uniform(-12.0, 0.0, (N, Q))
        for j in range(N):
            if j % 3 == 0:
                c3[j, 1::2] = -np.inf
        att_c3free = attempt_sc(c3, None)
        if att_c3free["raised"]:
            complete("N%d_C3" % N, N)
            stop("control_not_established", {"control": "C3", "N": N, "direct": exc_summary(att_c3free)})
        dm_c3 = np.asarray(att_c3free["result"].decision_metrics)
        v3 = np.array([int(np.argmax(dm_c3[p])) for p in pos.tolist()], dtype=np.int64)
        if not all(bool(np.isfinite(dm_c3[p, v])) for p, v in zip(pos.tolist(), v3.tolist())):
            complete("N%d_C3" % N, N)
            stop("control_not_established", {"control": "C3", "N": N,
                                             "detail": "argmax-selected values lack finite direct support"})
        entry = disclosed_control("C3_x11_pattern_positive_support", c3, pos, v3)
        nrec["controls"]["C3_x11_pattern_positive_support"] = entry
        if not entry["parity"]:
            complete("N%d_C3" % N, N)
            stop("semantic_mismatch", {"control": "C3", "N": N})
        complete("N%d_C3" % N, N)
        print("N=%d C3 parity=%s" % (N, entry["parity"]), flush=True)

        # C4: impossible-disclosure search (even rows symbol-0-only finite).
        found = None
        attempts = 0
        other_exceptions = 0
        for t in range(400):
            k = 16 if t < 200 else 32
            kk = k if k <= N else N // 2
            cpos = ((t * 7 + np.arange(kk) * 3) % N).astype(np.int64)
            cval = rng.integers(0, Q, kk).astype(np.int64)
            cbase = rng.uniform(-12.0, 0.0, (N, Q))
            for j in range(0, N, 2):
                cbase[j, 1:] = -np.inf
            attempts += 1
            att_d = attempt_sc(cbase, None, cpos, cval)
            if att_d["raised"] and att_d["exc_type"] == "ImpossibleDisclosedValueError":
                per = {}
                ok = True
                for chunk in CHUNKS:
                    att_c = attempt_sc(cbase, chunk, cpos, cval)
                    par = bool(att_c["raised"] and att_c["exc_type"] == att_d["exc_type"]
                               and att_c["message"] == att_d["message"])
                    per[str(chunk)] = dict(exc_summary(att_c), parity=par)
                    ok = ok and par
                found = {"control": "C4_impossible_disclosed_value", "search_index_t": t, "k": kk,
                         "positions": [int(v) for v in cpos.tolist()],
                         "values": [int(v) for v in cval.tolist()],
                         "exception_type": "ImpossibleDisclosedValueError",
                         "direct_message": att_d["message"], "per_chunk": per, "parity": bool(ok)}
                break
            elif att_d["raised"]:
                other_exceptions += 1
                continue
        if found is None:
            complete("N%d_C4" % N, N)
            stop("control_not_established", {"control": "C4", "N": N, "attempts": attempts,
                                             "other_exceptions": other_exceptions})
        found["search_attempts"] = attempts
        found["other_exceptions_seen"] = other_exceptions
        nrec["controls"]["C4_impossible_disclosed_value"] = found
        if not found["parity"]:
            complete("N%d_C4" % N, N)
            stop("semantic_mismatch", {"control": "C4", "N": N})
        complete("N%d_C4" % N, N)
        print("N=%d C4 t=%d k=%d parity=%s" % (N, found["search_index_t"], found["k"], found["parity"]), flush=True)

        # T5: near/exact ties, undisclosed.
        tie_defs = [
            ("exact_tie", np.zeros((N, Q), dtype=np.float64)),
            ("ramp", np.tile(np.arange(Q, dtype=np.float64) - 31.0, (N, 1))),
            ("near_tie", np.tile(np.zeros(Q, dtype=np.float64), (N, 1))),
        ]
        tie_defs[2][1][:, 1] = -1e-9
        t5 = {}
        nrec["controls"]["T5_ties"] = t5
        for name, blk in tie_defs:
            entry = undisclosed_control("T5_" + name, blk)
            t5[name] = entry
            if not entry["parity"]:
                complete("N%d_T5_%s" % (N, name), N)
                stop("semantic_mismatch", {"control": "T5_" + name, "N": N})
            complete("N%d_T5_%s" % (N, name), N)
            print("N=%d T5_%s parity=%s" % (N, name, entry["parity"]), flush=True)

    # ---- Scaling matrix: one normalized uniform-[-20,0] block per N from the same stream.
    for N in SCALE_PAIRED_NS + SCALE_CHUNKONLY_NS:
        paired = N in SCALE_PAIRED_NS
        nrep = N_REP_SMALL if N <= 16384 else N_REP_BIG
        block = _normalize_rows(rng.uniform(-20.0, 0.0, (N, Q)))
        cell = {"N": N, "paired": bool(paired), "timed_reps_per_arm": nrep,
                "arms": {},
                "direct_gather_bytes": (N // 2) * Q * Q * 8,
                "chunked_temp_bytes": min(512, N // 2) * Q * Q * 8,
                "direct_gather_formula": "(N//2)*q*q*8 float64 top-level minus gather",
                "chunked_temp_formula": "min(512,N//2)*q*q*8 float64 chunked minus temp"}
        if paired:
            d_times = []
            d_fp = None
            for rep in range(nrep):
                s = time.perf_counter()
                att_d = attempt_sc(block, None)
                e1 = time.perf_counter()
                if att_d["raised"]:
                    complete("scale_N=%d" % N, N)
                    stop("semantic_mismatch", {"control": "scaling_direct", "N": N,
                                               "direct": exc_summary(att_d)})
                d_times.append(e1 - s)
                d_fp = {"u_hat_sha": fp(att_d["result"].u_hat),
                        "metrics_sha": fp(att_d["result"].decision_metrics),
                        "status": att_d["result"].status}
                s2 = time.perf_counter()
                att_c = attempt_sc(block, 512)
                e2 = time.perf_counter()
                if att_c["raised"]:
                    complete("scale_N=%d" % N, N)
                    stop("semantic_mismatch", {"control": "scaling_chunk512", "N": N,
                                               "chunk": exc_summary(att_c)})
                cmp = cmp_valid(att_d["result"], att_c["result"])
                if not parity_ok(cmp):
                    complete("scale_N=%d" % N, N)
                    stop("semantic_mismatch", {"control": "scaling_parity", "N": N, "rep": rep})
                if "c_times" not in cell["arms"]:
                    cell["arms"]["c_times"] = []
                cell["arms"]["c_times"].append(e2 - s2)
            d_rss = rss_peak()
            cell["arms"]["direct"] = {"seconds_all": [float(t) for t in d_times],
                                      "median_s": float(np.median(np.asarray(d_times))),
                                      "rss_after_arm": d_rss,
                                      "fingerprint": d_fp}
            c_times = cell["arms"].pop("c_times")
            # Chunked RSS snapshot is cumulative; fresh snapshot now (descriptive).
            c_rss = rss_peak()
            cell["arms"]["chunk512"] = {"seconds_all": [float(t) for t in c_times],
                                        "median_s": float(np.median(np.asarray(c_times))),
                                        "rss_after_arm": c_rss,
                                        "u_hat_sha_matches_direct": True}
            print("scale N=%d paired d_med=%.4f c_med=%.4f" % (N, cell["arms"]["direct"]["median_s"], cell["arms"]["chunk512"]["median_s"]), flush=True)
        else:
            c_times = []
            for rep in range(nrep):
                s = time.perf_counter()
                att_c = attempt_sc(block, 512)
                e = time.perf_counter()
                if att_c["raised"]:
                    complete("scale_N=%d" % N, N)
                    stop("resource_or_error", {"control": "scaling_chunk512_only", "N": N,
                                               "chunk": exc_summary(att_c)})
                c_times.append(e - s)
            cell["arms"]["chunk512"] = {"seconds_all": [float(t) for t in c_times],
                                        "median_s": float(np.median(np.asarray(c_times))),
                                        "rss_after_arm": rss_peak(),
                                        "status": att_c["result"].status,
                                        "u_hat_sha": fp(att_c["result"].u_hat),
                                        "metrics_sha": fp(att_c["result"].decision_metrics)}
            print("scale N=%d chunkonly med=%.4f status=%s" % (N, cell["arms"]["chunk512"]["median_s"], att_c["result"].status), flush=True)
        REC["scaling_cells"].append(cell)
        complete("scale_N=%d" % N, N)

    if sc_mod._minus_block is not ORIG_MINUS:
        stop("restoration_failure", {"detail": "monkeypatch still active at process end"})
    refresh_restoration()
    if not (REC["restoration"]["all_pre_is_orig"] and REC["restoration"]["all_post_is_orig"]):
        stop("restoration_failure", {"restoration": REC["restoration"]})

    prior_executions = []
    if PRIOR_SUMMARY_RAW.strip():
        prior_executions.append(json.loads(PRIOR_SUMMARY_RAW))
    wall_s = time.monotonic() - T0
    REC["executions"] = prior_executions + [{
        "attempt": ATTEMPT,
        "command": COMMAND_TEXT,
        "cwd": str(REPO),
        "virtual_kb_limit": VSZ_KB,
        "wall_limit_s": WALL_LIMIT_S,
        "exit_code": 0,
        "wall_s": wall_s,
        "is_rerun": bool(ATTEMPT > 1),
    }]
    REC["status"] = "X12_PROBE_COMPLETE_DESCRIPTIVE_ONLY"
    REC["environment"] = {
        "interpreter": INTERPRETER,
        "python": sys.version,
        "numpy": str(np.__version__),
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
    }
    REC["access_scope"] = {
        "paths_read": [str(PREREG_PATH), str(BODY_PATH)],
        "paths_written": [str(RESULTS_PATH)],
        "modules_imported_readonly": [
            "comparison_bench.formal_ir.nbpolar.algebra",
            "comparison_bench.formal_ir.nbpolar.sc",
        ],
        "forbidden_opened": [],
    }
    REC["notes"] = [
        "Accepted sc.py was imported read-only and never modified; chunking lived only in a temporary monkeypatched _minus_block restored in finally with is-identity proof after every run and at process end.",
        "Per contiguous row slice the chunked path executes the exact accepted expression gathered=first[:,index]+second[:,None,:], the same np.logaddexp.reduce axis=2, and the accepted _normalize_rows over the full matrix.",
        "V0 validation baselines ran before the first monkeypatch entry; per-chunk V0 cases required identical exception type and message.",
        "C4 search draws are data-dependent in count but stream-ordered; all other draws are fixed-size in frozen order.",
        "Per-arm RSS snapshots are cumulative process high-water marks attributed descriptively, not isolated arm footprints.",
        "A resource failure at a registered N would have been recorded as a descriptive ceiling; none occurred unless recorded in scaling_cells/stop_detail.",
    ]
    save()
    print("prereg_sha256=%s" % PREREG_SHA)
    print("body_sha256=%s match=%s" % (BODY_SHA, BODY_MATCH))
    print("results_path=%s" % RESULTS_PATH)


try:
    main()
except SystemExit:
    raise
except BaseException:
    traceback.print_exc()
    try:
        stop("exception", {"error": "unhandled", "traceback_tail": traceback.format_exc()[-2000:]})
    except SystemExit:
        raise
```
