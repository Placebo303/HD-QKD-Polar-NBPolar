1. Question: Does the frozen exact-semantics hybrid minus-node (X10 FWHT formula for all-finite row pairs with per-row range <=20.0 nat-log units, accepted direct _minus_block for every other row, numerical-safety direct recompute for eligible rows whose raw inverse-FWHT convolution is <=0 or nonfinite) produce end-to-end SC equivalence with descriptive scaling across N=64/256/1024/4096/16384 in moderate, mixed and wide injected-metric regimes (Tier-X non-claim descriptive record only; no threshold, no winner, no candidate, no acceptance, no attempt consumed).
2. Parameters: probe seed=2026091760 (single RNG stream; timing blocks generated first for N ascending x regimes moderate/mixed/wide, then controls C1..C5 in order); GF(32) primitive polynomial 37, alpha=2, float64, accepted _combination_index verified entrywise against field ops, frozen X10 butterfly order, inverse scale 1/32; row-pair FWHT-eligible ONLY when both input rows entirely finite AND each row max-min <=20.0; eligible rows via rowwise-max-stabilized FWHT (spectra product/32, log, NO clipping); ineligible rows via accepted direct _minus_block unmodified; reassemble original row order then accepted _normalize_rows over the full matrix; numerical-safety fallback counted separately (eligible row with any raw conv value <=0 or nonfinite produced row is discarded and recomputed with direct; hybrid never manufactures/deletes exact support); probe-only temporary monkeypatch of imported sc module _minus_block during sc_decode calls, restored in finally, module-identity is-checks before/after every hybrid call; N=[64,256,1024,4096,16384] x regimes moderate=logits uniform[-12,0], mixed=even rows uniform[-12,0] with odd rows uniform[-80,0] via two draws and row-alternating selection, wide=logits uniform[-120,0]; exactly ONE frozen metric block per (N,regime) shared by direct and hybrid; 1 untimed warmup per implementation for N<=1024 and none above; exactly 5 timed reps per implementation for N<=4096 and 3 for N=16384 with alternating first implementation; NO known/disclosed coordinates in the timing matrix; N=64 deterministic semantic controls C1=all-finite moderate + 16 disclosed coords (sorted rng.choice positions, rng.integers values), C2=finite wide + SAME disclosures, C3=-inf pattern (rows j%3==0 odd symbols -inf, >=1 finite per row) with disclosure values = argmax of undisclosed-direct decision rows at the C1 positions (direct-positive support only), C4=impossible-disclosure search (even rows symbol-0-only finite, candidates pos=(t*7+arange(k)*3)%64 with k=16 for t<200 else k=32 and rng values, up to 400 attempts; selected case must raise the SAME ImpossibleDisclosedValueError type+message in direct and hybrid), C5=X10-style exact-tie all-zeros block + ramp block (every row arange(32)-31) + near-tie block (zeros with symbol1 at -1e-9) requiring accepted smallest-symbol tie behavior in BOTH modes with the ENTIRE 32-symbol score ordering reported for decision coordinate 0; per timing cell persist raw durations, medians, direct/hybrid ratio, u_hat/x_hat mismatches, decision argmax mismatches, max finite decision-log-metric error, support mismatches, status parity, hybrid counters (minus calls, total rows, eligible rows, dynamic-range fallback, nonfinite-input fallback, numerical-safety fallback, direct rows, FWHT rows) summed over timed hybrid reps only, FWHT fraction; STOP (with stop record) on any support/status/exception-parity failure, monkeypatch-restore failure, C4 search exhaustion, or tie-behavior failure; bounds=ulimit -v 2097152 with 1800s wall; single execution, one execution-error rerun allowed only with unchanged parameters/seed/semantics and both executions recorded.
3. Command: cwd=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar; ulimit -v 2097152; timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - < /tmp/x11_body.py (staged byte-identically from the prereg python fence; body self-verifies staged bytes equal embedded bytes before any benchmark; single execution).

```python
"""X11 Tier-X frozen body: hybrid FWHT end-to-end SC probe (descriptive only).

Accepted direct sc_decode vs a probe-only hybrid path that temporarily
monkeypatches the imported SC module's _minus_block (restored in finally):
FWHT for all-finite row pairs with per-row range <= 20 nat units, accepted
direct _minus_block otherwise, numerical-safety direct recompute for eligible
rows with raw inverse-FWHT values <=0 or nonfinite output. One frozen synthetic
metric block per (N, regime); N=64 semantic controls C1..C5. ONE descriptive
results.json record. No artifact, evidence-root, raw/held-out/real/EVAL,
decoder-gate, official-stream, or tag access. No threshold, winner, candidate,
acceptance, or label.
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
PROBE_DIR = REPO / "workspace" / "probes" / "nbpolar_x11_hybrid_fwht_endtoend"
PREREG_PATH = PROBE_DIR / "prereg.md"
RESULTS_PATH = PROBE_DIR / "results.json"
X10_RESULTS_PATH = REPO / "workspace" / "probes" / "nbpolar_x10_fwht_kernel_scaling" / "results.json"
BODY_PATH = Path("/tmp/x11_body.py")
INTERPRETER = "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python"
COMMAND_TEXT = "ulimit -v 2097152; timeout 1800 " + INTERPRETER + " - < /tmp/x11_body.py"

SEED = 2026091760
Q = 32
ALPHA = 2
RANGE_CAP = 20.0
NS = [64, 256, 1024, 4096, 16384]
REGIME_IDS = ["moderate", "mixed", "wide"]
N_REP_SMALL = 5
N_REP_BIG = 3
VSZ_KB = 2097152
WALL_LIMIT_S = 1800
ATTEMPT = int(os.environ.get("X11_ATTEMPT", "1"))
PRIOR_SUMMARY_RAW = os.environ.get("X11_PRIOR_SUMMARY", "")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


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


def stop(reason, detail):
    out = {
        "probe_id": "nbpolar_x11_hybrid_fwht_endtoend",
        "tier": "X",
        "status": "STOPPED_" + str(reason).upper(),
        "stop_detail": detail,
        "prereg_sha256": PREREG_SHA,
        "body_sha256": BODY_SHA,
        "body_sha_match": BODY_MATCH,
        "wall_s": time.monotonic() - T0,
        "rss_peak": rss_peak(),
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("STOP: %s" % reason)
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
    if int(getattr(field, "primitive_polynomial", -1)) != 37:
        stop("field_identity", {"primitive_polynomial": getattr(field, "primitive_polynomial", None)})
    ORIG_MINUS = sc_mod._minus_block
    if ORIG_MINUS is not _minus_block:
        stop("module_identity", {"detail": "imported _minus_block is not sc_mod._minus_block at startup"})
    perm_fwd = np.array([field.mul(ALPHA, v) for v in range(Q)], dtype=np.int64)
    if sorted(perm_fwd.tolist()) != list(range(Q)):
        stop("perm_not_bijection", {"perm_fwd": perm_fwd.tolist()})
    index = _combination_index(field, ALPHA, Q)
    for u in range(Q):
        for v in range(Q):
            if int(index[u, v]) != int(field.add(u, field.mul(ALPHA, v))):
                stop("index_identity", {"u": u, "v": v})

    x10rec = json.loads(X10_RESULTS_PATH.read_text(encoding="utf-8"))

    def fwht_block(mat):
        out = np.array(mat, dtype=np.float64, copy=True)
        n = out.shape[1]
        h = 1
        while h < n:
            for start in range(0, n, 2 * h):
                u = out[:, start:start + h].copy()
                v = out[:, start + h:start + 2 * h].copy()
                out[:, start:start + h] = u + v
                out[:, start + h:start + 2 * h] = u - v
            h *= 2
        return out

    IDENT_LOG = []

    def fresh_stats():
        return {"minus_calls": 0, "total_rows": 0, "eligible_rows": 0,
                "nonfinite_input_fallback": 0, "dynamic_range_fallback": 0,
                "numerical_safety_fallback": 0, "fwht_rows": 0, "direct_rows": 0}

    def make_hybrid(stats):
        def hybrid_minus(first, second, index_arg):
            f0in = np.asarray(first, dtype=np.float64)
            f1in = np.asarray(second, dtype=np.float64)
            rows = f0in.shape[0]
            stats["minus_calls"] += 1
            stats["total_rows"] += rows
            fin = np.isfinite(f0in).all(axis=1) & np.isfinite(f1in).all(axis=1)
            r0 = f0in.max(axis=1) - f0in.min(axis=1)
            r1 = f1in.max(axis=1) - f1in.min(axis=1)
            eligible = fin & (r0 <= RANGE_CAP) & (r1 <= RANGE_CAP)
            stats["eligible_rows"] += int(eligible.sum())
            stats["nonfinite_input_fallback"] += int((~fin).sum())
            stats["dynamic_range_fallback"] += int((fin & ~eligible).sum())
            out = np.empty((rows, Q), dtype=np.float64)
            inelig = ~eligible
            if inelig.any():
                out[inelig] = ORIG_MINUS(f0in[inelig], f1in[inelig], index_arg)
                stats["direct_rows"] += int(inelig.sum())
            if eligible.any():
                idx = np.where(eligible)[0]
                g0 = f0in[idx]
                g1 = f1in[idx]
                m0 = g0.max(axis=1, keepdims=True)
                m1 = g1.max(axis=1, keepdims=True)
                with np.errstate(over="ignore", under="ignore"):
                    p0 = np.exp(g0 - m0)
                    p1 = np.exp(g1 - m1)
                q1p = np.empty_like(p1)
                q1p[:, perm_fwd] = p1
                with np.errstate(over="ignore", under="ignore", invalid="ignore"):
                    conv = fwht_block(fwht_block(p0) * fwht_block(q1p)) / float(Q)
                bad = (conv <= 0.0).any(axis=1) | (~np.isfinite(conv).all(axis=1))
                with np.errstate(divide="ignore", invalid="ignore"):
                    lg = np.log(conv)
                bad = bad | (~np.isfinite(lg).all(axis=1))
                nbad = int(bad.sum())
                stats["numerical_safety_fallback"] += nbad
                good = ~bad
                if good.any():
                    out[idx[good]] = lg[good]
                    stats["fwht_rows"] += int(good.sum())
                if bad.any():
                    out[idx[bad]] = ORIG_MINUS(g0[bad], g1[bad], index_arg)
                    stats["direct_rows"] += nbad
            return _normalize_rows(out)
        return hybrid_minus

    def run_direct(metrics, kp=None, kv=None):
        return sc_decode(metrics, field=field, alpha=ALPHA, known_positions=kp, known_values=kv)

    def run_hybrid(metrics, stats, kp=None, kv=None):
        pre = sc_mod._minus_block is ORIG_MINUS
        sc_mod._minus_block = make_hybrid(stats)
        try:
            return sc_decode(metrics, field=field, alpha=ALPHA, known_positions=kp, known_values=kv)
        finally:
            sc_mod._minus_block = ORIG_MINUS
            IDENT_LOG.append({"pre_is_orig": bool(pre),
                              "post_is_orig": bool(sc_mod._minus_block is ORIG_MINUS)})

    def compare_ok(dres, hres):
        dd = np.asarray(dres.decision_metrics)
        hh = np.asarray(hres.decision_metrics)
        both = np.isfinite(dd) & np.isfinite(hh)
        return {
            "u_hat_mismatches": int((np.asarray(dres.u_hat) != np.asarray(hres.u_hat)).sum()),
            "x_hat_mismatches": int((np.asarray(dres.x_hat) != np.asarray(hres.x_hat)).sum()),
            "decision_argmax_mismatches": int((np.argmax(dd, axis=1) != np.argmax(hh, axis=1)).sum()),
            "support_mismatch_rows": int(((np.isfinite(dd) != np.isfinite(hh)).any(axis=1)).sum()),
            "max_finite_decision_log_metric_error": float(np.abs(dd[both] - hh[both]).max()) if both.any() else None,
            "status_direct": dres.status,
            "status_hybrid": hres.status,
            "status_parity": bool(dres.status == hres.status),
        }

    def worst_cmp(cmps):
        keys = ("u_hat_mismatches", "x_hat_mismatches", "decision_argmax_mismatches", "support_mismatch_rows")
        out = {k: max(c[k] for c in cmps) for k in keys}
        errs = [c["max_finite_decision_log_metric_error"] for c in cmps
                if c["max_finite_decision_log_metric_error"] is not None]
        out["max_finite_decision_log_metric_error"] = max(errs) if errs else None
        out["status_parity_all"] = all(c["status_parity"] for c in cmps)
        out["status_direct"] = cmps[0]["status_direct"]
        out["status_hybrid"] = cmps[0]["status_hybrid"]
        return out

    rng = np.random.default_rng(SEED)

    def gen_block(n, regime):
        if regime == "moderate":
            return rng.uniform(-12.0, 0.0, (n, Q))
        if regime == "wide":
            return rng.uniform(-120.0, 0.0, (n, Q))
        if regime == "mixed":
            a = rng.uniform(-12.0, 0.0, (n, Q))
            b = rng.uniform(-80.0, 0.0, (n, Q))
            sel = (np.arange(n) % 2 == 0)[:, None]
            return np.where(sel, a, b)
        raise ValueError("unknown regime " + str(regime))

    blocks = {}
    for n in NS:
        for regime in REGIME_IDS:
            blocks[(n, regime)] = gen_block(n, regime)

    cells = []
    for n in NS:
        for regime in REGIME_IDS:
            block = blocks[(n, regime)]
            nrep = N_REP_SMALL if n <= 4096 else N_REP_BIG
            nwarm = 1 if n <= 1024 else 0
            for _ in range(nwarm):
                run_direct(block)
                run_hybrid(block, fresh_stats())
            d_times = []
            h_times = []
            firsts = []
            cmps = []
            agg = fresh_stats()
            for rep in range(nrep):
                if rep % 2 == 0:
                    firsts.append("direct")
                    s = time.perf_counter()
                    dres = run_direct(block)
                    e1 = time.perf_counter()
                    hres = run_hybrid(block, agg)
                    e2 = time.perf_counter()
                    d_times.append(e1 - s)
                    h_times.append(e2 - e1)
                else:
                    firsts.append("hybrid")
                    s = time.perf_counter()
                    hres = run_hybrid(block, agg)
                    e1 = time.perf_counter()
                    dres = run_direct(block)
                    e2 = time.perf_counter()
                    h_times.append(e1 - s)
                    d_times.append(e2 - e1)
                cmps.append(compare_ok(dres, hres))
            w = worst_cmp(cmps)
            if w["support_mismatch_rows"]:
                stop("support_parity", {"N": n, "regime": regime, "worst": w})
            if not w["status_parity_all"]:
                stop("status_parity", {"N": n, "regime": regime, "worst": w})
            d_med = float(np.median(np.asarray(d_times)))
            h_med = float(np.median(np.asarray(h_times)))
            tot = agg["total_rows"]
            cells.append({
                "N": n, "regime": regime, "timed_reps_per_implementation": nrep,
                "untimed_warmups_per_implementation": nwarm, "first_impl_per_rep": firsts,
                "direct_seconds_all": [float(t) for t in d_times],
                "hybrid_seconds_all": [float(t) for t in h_times],
                "direct_median_s": d_med, "hybrid_median_s": h_med,
                "direct_over_hybrid_descriptive": (d_med / h_med) if h_med > 0 else None,
                "worst_discrepancy_across_reps": w,
                "hybrid_counters_timed_reps_only": dict(agg),
                "fwht_fraction_descriptive": (agg["fwht_rows"] / tot) if tot else None,
            })
            print("cell N=%d %s reps=%d d_med=%.6f h_med=%.6f u_mm=%d x_mm=%d argmm=%d ferr=%s fwht_frac=%s" % (
                n, regime, nrep, d_med, h_med, w["u_hat_mismatches"], w["x_hat_mismatches"],
                w["decision_argmax_mismatches"], str(w["max_finite_decision_log_metric_error"]),
                str(cells[-1]["fwht_fraction_descriptive"])))

    controls = {}
    c1_metrics = rng.uniform(-12.0, 0.0, (64, Q))
    c_pos = np.sort(rng.choice(64, 16, replace=False)).astype(np.int64)
    c_val = rng.integers(0, Q, 16).astype(np.int64)
    d1 = run_direct(c1_metrics, c_pos, c_val)
    s1 = fresh_stats()
    h1 = run_hybrid(c1_metrics, s1, c_pos, c_val)
    w1 = compare_ok(d1, h1)
    if w1["support_mismatch_rows"] or not w1["status_parity"]:
        stop("support_parity", {"control": "C1", "worst": w1})
    controls["C1_moderate_disclosed16"] = {
        "positions": [int(v) for v in c_pos.tolist()],
        "values": [int(v) for v in c_val.tolist()],
        "discrepancy": w1, "hybrid_counters": dict(s1),
    }
    print("control C1 u_mm=%d x_mm=%d argmm=%d ferr=%s" % (
        w1["u_hat_mismatches"], w1["x_hat_mismatches"],
        w1["decision_argmax_mismatches"], str(w1["max_finite_decision_log_metric_error"])))

    c2_metrics = rng.uniform(-120.0, 0.0, (64, Q))
    d2 = run_direct(c2_metrics, c_pos, c_val)
    s2 = fresh_stats()
    h2 = run_hybrid(c2_metrics, s2, c_pos, c_val)
    w2 = compare_ok(d2, h2)
    if w2["support_mismatch_rows"] or not w2["status_parity"]:
        stop("support_parity", {"control": "C2", "worst": w2})
    controls["C2_wide_same_disclosures"] = {
        "positions": [int(v) for v in c_pos.tolist()],
        "values": [int(v) for v in c_val.tolist()],
        "discrepancy": w2, "hybrid_counters": dict(s2),
    }
    print("control C2 u_mm=%d x_mm=%d argmm=%d ferr=%s" % (
        w2["u_hat_mismatches"], w2["x_hat_mismatches"],
        w2["decision_argmax_mismatches"], str(w2["max_finite_decision_log_metric_error"])))

    c3_metrics = rng.uniform(-12.0, 0.0, (64, Q))
    for j in range(64):
        if j % 3 == 0:
            c3_metrics[j, 1::2] = -np.inf
    d3free = run_direct(c3_metrics)
    dm3 = np.asarray(d3free.decision_metrics)
    v3 = np.array([int(np.argmax(dm3[p])) for p in c_pos.tolist()], dtype=np.int64)
    if not all(bool(np.isfinite(dm3[p, v])) for p, v in zip(c_pos.tolist(), v3.tolist())):
        stop("c3_support_selection", {"detail": "argmax-selected values lack finite direct support"})
    d3 = run_direct(c3_metrics, c_pos, v3)
    s3 = fresh_stats()
    h3 = run_hybrid(c3_metrics, s3, c_pos, v3)
    w3 = compare_ok(d3, h3)
    if w3["support_mismatch_rows"] or not w3["status_parity"]:
        stop("support_parity", {"control": "C3", "worst": w3})
    controls["C3_nonfinite_direct_support_values"] = {
        "pattern": "rows j with j%3==0 have odd symbols -inf (16 finite even symbols kept); all rows keep >=1 finite",
        "positions": [int(v) for v in c_pos.tolist()],
        "values_from_direct_positive_support": [int(v) for v in v3.tolist()],
        "discrepancy": w3, "hybrid_counters": dict(s3),
    }
    print("control C3 u_mm=%d x_mm=%d argmm=%d ferr=%s" % (
        w3["u_hat_mismatches"], w3["x_hat_mismatches"],
        w3["decision_argmax_mismatches"], str(w3["max_finite_decision_log_metric_error"])))

    c4_found = None
    c4_attempts = 0
    c4_other_exceptions = 0
    for t in range(400):
        k = 16 if t < 200 else 32
        pos = ((t * 7 + np.arange(k) * 3) % 64).astype(np.int64)
        vals = rng.integers(0, Q, k).astype(np.int64)
        base = rng.uniform(-12.0, 0.0, (64, Q))
        for j in range(64):
            if j % 2 == 0:
                base[j, 1:] = -np.inf
        c4_attempts += 1
        try:
            run_direct(base, pos, vals)
        except ImpossibleDisclosedValueError as exc:
            s4 = fresh_stats()
            try:
                run_hybrid(base, s4, pos, vals)
            except ImpossibleDisclosedValueError as exc2:
                if str(exc2) == str(exc):
                    c4_found = {
                        "search_index_t": t, "k": k,
                        "positions": [int(v) for v in pos.tolist()],
                        "values": [int(v) for v in vals.tolist()],
                        "exception_type": "ImpossibleDisclosedValueError",
                        "direct_message": str(exc), "hybrid_message": str(exc2),
                        "messages_equal": True, "hybrid_counters": dict(s4),
                    }
                    break
                stop("exception_parity", {"control": "C4", "direct_message": str(exc),
                                          "hybrid_message": str(exc2)})
            stop("exception_parity", {"control": "C4",
                                      "detail": "hybrid did not raise while direct raised ImpossibleDisclosedValueError",
                                      "direct_message": str(exc)})
        except Exception:
            c4_other_exceptions += 1
            continue
    if c4_found is None:
        stop("c4_no_impossible_case", {"attempts": c4_attempts, "other_exceptions": c4_other_exceptions})
    controls["C4_impossible_disclosed_value"] = dict(c4_found)
    controls["C4_impossible_disclosed_value"]["search_attempts"] = c4_attempts
    controls["C4_impossible_disclosed_value"]["other_exceptions_seen"] = c4_other_exceptions
    print("control C4 found t=%d k=%d msg=%s" % (c4_found["search_index_t"], c4_found["k"], c4_found["direct_message"]))

    tie_blocks = [
        ("exact_tie", np.zeros((64, Q), dtype=np.float64)),
        ("ramp", np.tile(np.arange(Q, dtype=np.float64) - 31.0, (64, 1))),
        ("near_tie", np.tile(np.zeros(Q, dtype=np.float64), (64, 1))),
    ]
    tie_blocks[2][1][:, 1] = -1e-9
    c5 = {}
    for name, blk in tie_blocks:
        dd = run_direct(blk)
        ss = fresh_stats()
        hh = run_hybrid(blk, ss)
        ww = compare_ok(dd, hh)
        if ww["support_mismatch_rows"] or not ww["status_parity"]:
            stop("support_parity", {"control": "C5_" + name, "worst": ww})
        row0d = np.asarray(dd.decision_metrics)[0]
        row0h = np.asarray(hh.decision_metrics)[0]
        c5[name] = {
            "discrepancy": ww, "hybrid_counters": dict(ss),
            "u_hat_all_zero_direct": bool((np.asarray(dd.u_hat) == 0).all()),
            "u_hat_all_zero_hybrid": bool((np.asarray(hh.u_hat) == 0).all()),
            "u_hat_sum_direct": int(np.asarray(dd.u_hat).sum()),
            "u_hat_sum_hybrid": int(np.asarray(hh.u_hat).sum()),
            "coord0_choice_direct": int(np.asarray(dd.u_hat)[0]),
            "coord0_choice_hybrid": int(np.asarray(hh.u_hat)[0]),
            "coord0_score_order_direct": np.argsort(-row0d, kind="stable").tolist(),
            "coord0_score_order_hybrid": np.argsort(-row0h, kind="stable").tolist(),
            "coord0_scores_direct": [float(v) for v in row0d.tolist()],
            "coord0_scores_hybrid": [float(v) for v in row0h.tolist()],
        }
        print("control C5 %s u0d=%d u0h=%d allzero_d=%s allzero_h=%s argmm=%d ferr=%s" % (
            name, c5[name]["u_hat_sum_direct"], c5[name]["u_hat_sum_hybrid"],
            str(c5[name]["u_hat_all_zero_direct"]), str(c5[name]["u_hat_all_zero_hybrid"]),
            ww["decision_argmax_mismatches"], str(ww["max_finite_decision_log_metric_error"])))
    if not (c5["exact_tie"]["u_hat_all_zero_direct"] and c5["exact_tie"]["u_hat_all_zero_hybrid"]):
        stop("tie_behavior", {"detail": "exact-tie block did not decode to all-zero (smallest-symbol tie) in both modes",
                              "c5_exact_tie": c5["exact_tie"]})
    controls["C5_ties"] = c5

    identity_ok = (all(e["pre_is_orig"] and e["post_is_orig"] for e in IDENT_LOG)
                   and (sc_mod._minus_block is ORIG_MINUS))
    if not identity_ok:
        stop("module_identity", {"detail": "monkeypatch restore proof failed",
                                 "check_count": len(IDENT_LOG)})
    module_identity = {
        "hybrid_invocations": len(IDENT_LOG),
        "all_pre_is_orig": all(e["pre_is_orig"] for e in IDENT_LOG),
        "all_post_is_orig": all(e["post_is_orig"] for e in IDENT_LOG),
        "current_is_orig": bool(sc_mod._minus_block is ORIG_MINUS),
        "restored": True,
    }

    total = fresh_stats()
    for cell in cells:
        for key in total:
            total[key] += cell["hybrid_counters_timed_reps_only"][key]
    for ckey in ("C1_moderate_disclosed16", "C2_wide_same_disclosures", "C3_nonfinite_direct_support_values"):
        for key in total:
            total[key] += controls[ckey]["hybrid_counters"][key]
    for key in total:
        total[key] += controls["C4_impossible_disclosed_value"]["hybrid_counters"][key]
    for name in ("exact_tie", "ramp", "near_tie"):
        for key in total:
            total[key] += controls["C5_ties"][name]["hybrid_counters"][key]
    trows = total["total_rows"]
    by_N = {}
    for n in NS:
        sub = [c for c in cells if c["N"] == n]
        serrs = [c["worst_discrepancy_across_reps"]["max_finite_decision_log_metric_error"] for c in sub]
        by_N[str(n)] = {
            "direct_over_hybrid_by_regime": {c["regime"]: c["direct_over_hybrid_descriptive"] for c in sub},
            "fwht_fraction_by_regime": {c["regime"]: c["fwht_fraction_descriptive"] for c in sub},
            "worst_u_hat_mismatches": max(c["worst_discrepancy_across_reps"]["u_hat_mismatches"] for c in sub),
            "worst_x_hat_mismatches": max(c["worst_discrepancy_across_reps"]["x_hat_mismatches"] for c in sub),
            "worst_decision_argmax_mismatches": max(
                c["worst_discrepancy_across_reps"]["decision_argmax_mismatches"] for c in sub),
            "worst_support_mismatch_rows": max(
                c["worst_discrepancy_across_reps"]["support_mismatch_rows"] for c in sub),
            "worst_finite_decision_log_metric_error": max(serrs) if serrs else None,
        }
    by_regime = {}
    for regime in REGIME_IDS:
        sub = [c for c in cells if c["regime"] == regime]
        by_regime[regime] = {
            "direct_over_hybrid_by_N": {str(c["N"]): c["direct_over_hybrid_descriptive"] for c in sub},
            "fwht_fraction_by_N": {str(c["N"]): c["fwht_fraction_descriptive"] for c in sub},
        }
    timing_table = [{"N": c["N"], "regime": c["regime"], "direct_median_s": c["direct_median_s"],
                     "hybrid_median_s": c["hybrid_median_s"],
                     "direct_over_hybrid_descriptive": c["direct_over_hybrid_descriptive"]} for c in cells]
    worst_all = {
        "worst_u_hat_mismatches": max(c["worst_discrepancy_across_reps"]["u_hat_mismatches"] for c in cells),
        "worst_x_hat_mismatches": max(c["worst_discrepancy_across_reps"]["x_hat_mismatches"] for c in cells),
        "worst_decision_argmax_mismatches": max(
            c["worst_discrepancy_across_reps"]["decision_argmax_mismatches"] for c in cells),
        "worst_support_mismatch_rows": max(
            c["worst_discrepancy_across_reps"]["support_mismatch_rows"] for c in cells),
        "worst_finite_decision_log_metric_error": max(
            c["worst_discrepancy_across_reps"]["max_finite_decision_log_metric_error"] for c in cells),
    }

    prior_executions = []
    if PRIOR_SUMMARY_RAW.strip():
        prior_executions.append(json.loads(PRIOR_SUMMARY_RAW))
    wall_s = time.monotonic() - T0
    executions = prior_executions + [{
        "attempt": ATTEMPT,
        "command": COMMAND_TEXT,
        "cwd": str(REPO),
        "virtual_kb_limit": VSZ_KB,
        "wall_limit_s": WALL_LIMIT_S,
        "exit_code": 0,
        "wall_s": wall_s,
        "is_rerun": bool(ATTEMPT > 1),
    }]

    results = {
        "probe_id": "nbpolar_x11_hybrid_fwht_endtoend",
        "tier": "X",
        "status": "X11_PROBE_COMPLETE_DESCRIPTIVE_ONLY",
        "question": "Hybrid FWHT/direct-fallback minus-node end-to-end SC equivalence and scaling record (descriptive only)",
        "parameters": {
            "seed": SEED, "q": Q, "alpha": ALPHA, "range_cap_nat_units": RANGE_CAP,
            "N_values": NS, "regimes": REGIME_IDS,
            "regime_definitions": {
                "moderate": "logits uniform[-12,0]",
                "mixed": "even rows uniform[-12,0], odd rows uniform[-80,0]",
                "wide": "logits uniform[-120,0]",
            },
            "one_frozen_block_per_cell_shared": True,
            "untimed_warmups_per_implementation_N_le_1024": 1,
            "untimed_warmups_above_1024": 0,
            "timed_reps_per_implementation_N_le_4096": N_REP_SMALL,
            "timed_reps_per_implementation_N16384": N_REP_BIG,
            "alternating_first_implementation": True,
            "timing_disclosures": "none",
            "semantic_controls": ["C1", "C2", "C3", "C4", "C5"],
            "counters_cover": "timed hybrid reps only; warmups untimed and uncounted",
        },
        "command": COMMAND_TEXT,
        "prereg_sha256": PREREG_SHA,
        "body_sha256": BODY_SHA,
        "body_sha_match": BODY_MATCH,
        "field_identity": {
            "q": int(field.q), "alpha": ALPHA,
            "primitive_polynomial": int(getattr(field, "primitive_polynomial")),
            "perm_fwd_alpha2_is_bijection": True,
            "combination_index_matches_field_ops": True,
        },
        "x10_inherited_assumptions": {
            "source": str(X10_RESULTS_PATH),
            "question": x10rec.get("question"),
            "parameters": x10rec.get("parameters"),
            "field_identity": x10rec.get("field_identity"),
            "aggregates": x10rec.get("aggregates"),
            "notes": x10rec.get("notes"),
            "kernel_formula": "rowwise-max-stabilized exp; second spectrum permuted by alpha=2 field multiplication; FWHT pointwise-product inverse scaled by 1/32; X10 clipped negative roundoff to zero (raw minimum reported) and routed nonfinite-input rows to accepted direct _minus_block; frozen butterfly order identical to this probe fwht_block",
        },
        "timing_cells": cells,
        "timing_table_descriptive": timing_table,
        "aggregates_by_N": by_N,
        "aggregates_by_regime": by_regime,
        "worst_timing_discrepancy": worst_all,
        "hybrid_counters_total": total,
        "fwht_fraction_overall_descriptive": (total["fwht_rows"] / trows) if trows else None,
        "fallback_fractions_descriptive": {
            "dynamic_range": (total["dynamic_range_fallback"] / trows) if trows else None,
            "nonfinite_input": (total["nonfinite_input_fallback"] / trows) if trows else None,
            "numerical_safety": (total["numerical_safety_fallback"] / trows) if trows else None,
            "numerical_safety_over_eligible": (total["numerical_safety_fallback"] / total["eligible_rows"])
            if total["eligible_rows"] else None,
        },
        "semantic_controls": controls,
        "module_identity": module_identity,
        "environment": {
            "interpreter": INTERPRETER,
            "python": sys.version,
            "numpy": str(np.__version__),
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "access_scope": {
            "paths_read": [str(PREREG_PATH), str(X10_RESULTS_PATH)],
            "paths_written": [str(RESULTS_PATH)],
            "modules_imported_readonly": [
                "comparison_bench.formal_ir.nbpolar.algebra",
                "comparison_bench.formal_ir.nbpolar.sc",
            ],
            "forbidden_opened": [],
        },
        "executions": executions,
        "rss_peak": rss_peak(),
        "wall_s": wall_s,
        "claim_boundary": "Tier-X non-claim probe: ratios, fractions and errors are descriptive records only; no threshold, winner, candidate, acceptance, or scientific label.",
        "notes": [
            "Accepted sc.py was imported read-only and never modified; hybrid logic lived only in a temporary monkeypatched _minus_block restored in finally with is-identity proof.",
            "Eligible FWHT rows used log of the raw inverse-FWHT convolution with NO clipping; rows with raw values <=0 or nonfinite output were recomputed with the accepted direct reference and counted as numerical-safety fallback.",
            "Reassembled eligible/ineligible rows were passed through the accepted _normalize_rows once over the full matrix.",
            "Timing metric blocks were injected synthetic normalized logits; no artifact, evidence-root, raw/held-out/real/EVAL, tag, official-seed, or gate data was touched.",
        ],
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    print("prereg_sha256=%s" % PREREG_SHA)
    print("body_sha256=%s match=%s" % (BODY_SHA, BODY_MATCH))
    print("results_path=%s" % RESULTS_PATH)


try:
    main()
except SystemExit:
    raise
except BaseException:
    traceback.print_exc()
    stop("exception", {"error": "unhandled"})
```
