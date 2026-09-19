1. Question: Can the all-finite GF(32) SC minus-node probability convolution from accepted comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py be reproduced by a vectorized length-32 FWHT with inverse scaling by 32 (descriptive numerical-equivalence and scaling record only; Tier-X non-claim, no threshold, no winner, no label, no attempt consumed).
2. Parameters: probe seed=2026091740; GF(32) addition=5-bit XOR, alpha=2 field-multiplication permutation (q1[alpha*v]=p1[v]) verified bijective against accepted _combination_index; regimes=(a) dense logits uniform[-20,0], (b) dense logits uniform[-200,0], (c) one dominant symbol at 0.0 with others uniform[-80,-20], (d) deterministic 25pc -inf fallback rows (every 4th pair i%4==3, first-row even symbols -inf, >=1 finite value kept); row counts=[1,8,32,128,512,2048]; per regime x row cell: prototype vs accepted direct _minus_block reference with 2 untimed alternating warmups + exactly 7 timed reps per implementation with alternating first-order, every duration plus median recorded; prototype=AF-row rowwise max subtraction before exp, FWHT pointwise-product inverse/32, clip negative roundoff ONLY to zero with raw minimum reported, ANY nonfinite-input row dispatched to accepted direct _minus_block with fallback counts reported, output normalized to log probabilities via accepted _normalize_rows; plus unmodified accepted sc_decode profile at N=[64,256,1024] with 3 fresh injected all-finite uniform[-20,0] metric blocks per N (FWHT never spliced into SC); masters-equivalent=n/a Tier-X (no EVAL, no attempt, no candidate); bounds=ulimit -v 2097152 with 1800s wall; single execution, one execution-error rerun allowed only with unchanged parameters/model/seed and both executions recorded.
3. Command: cwd=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar; ulimit -v 2097152; timeout 1800 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - < /tmp/x10_body.py (staged byte-identically from the prereg python fence; body self-verifies staged bytes equal embedded bytes before any benchmark; single execution).

```python
"""X10 Tier-X frozen body: GF(32) FWHT minus-kernel scaling probe (descriptive only).

Read-only import of the accepted SC source (never modified); synthetic-logit
comparison of the frozen FWHT prototype vs accepted `_minus_block`; unmodified
`sc_decode` profile; ONE descriptive results.json record. No artifact,
evidence-root, raw/held-out/real/EVAL, decoder-gate, official-stream, or tag
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
from pathlib import Path

import numpy as np

T0 = time.monotonic()

REPO = Path("/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar")
PROBE_DIR = REPO / "workspace" / "probes" / "nbpolar_x10_fwht_kernel_scaling"
PREREG_PATH = PROBE_DIR / "prereg.md"
RESULTS_PATH = PROBE_DIR / "results.json"
BODY_PATH = Path("/tmp/x10_body.py")
INTERPRETER = "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python"
COMMAND_TEXT = INTERPRETER + " - < /tmp/x10_body.py"

SEED = 2026091740
Q = 32
ALPHA = 2
ROW_COUNTS = [1, 8, 32, 128, 512, 2048]
REGIME_IDS = ["dense_m20", "dense_m200", "dominant", "fallback"]
N_WARM = 2
N_REP = 7
SC_NS = [64, 256, 1024]
SC_BLOCKS_PER_N = 3
VSZ_KB = 2097152
WALL_LIMIT_S = 1800
ATTEMPT = int(os.environ.get("X10_ATTEMPT", "1"))
PRIOR_SUMMARY_RAW = os.environ.get("X10_PRIOR_SUMMARY", "")


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
        "probe_id": "nbpolar_x10_fwht_kernel_scaling",
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
    from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
    from comparison_bench.formal_ir.nbpolar.sc import (
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
    perm_fwd = np.array([field.mul(ALPHA, v) for v in range(Q)], dtype=np.int64)
    if sorted(perm_fwd.tolist()) != list(range(Q)):
        stop("perm_not_bijection", {"perm_fwd": perm_fwd.tolist()})
    index = _combination_index(field, ALPHA, Q)
    for u in range(Q):
        for v in range(Q):
            if int(index[u, v]) != int(field.add(u, field.mul(ALPHA, v))):
                stop("index_identity", {"u": u, "v": v})

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

    def fwht_minus_block(first, second):
        first = np.asarray(first, dtype=np.float64)
        second = np.asarray(second, dtype=np.float64)
        rows = first.shape[0]
        out = np.empty((rows, Q), dtype=np.float64)
        fb = ~np.isfinite(first).all(axis=1) | ~np.isfinite(second).all(axis=1)
        nfb = int(fb.sum())
        if nfb:
            out[fb] = _minus_block(first[fb], second[fb], index)
        ok = ~fb
        raw_min = None
        if ok.any():
            f0 = first[ok]
            f1 = second[ok]
            m0 = f0.max(axis=1, keepdims=True)
            m1 = f1.max(axis=1, keepdims=True)
            with np.errstate(over="ignore", under="ignore"):
                p0 = np.exp(f0 - m0)
                p1 = np.exp(f1 - m1)
            q1 = np.empty_like(p1)
            q1[:, perm_fwd] = p1
            with np.errstate(over="ignore", under="ignore", invalid="ignore"):
                conv = fwht_block(fwht_block(p0) * fwht_block(q1)) / float(Q)
            raw_min = float(conv.min())
            clipped = np.where(conv < 0.0, 0.0, conv)
            with np.errstate(divide="ignore"):
                out[ok] = _normalize_rows(np.log(clipped))
        return out, raw_min, nfb

    def probs(mat):
        m = np.asarray(mat, dtype=np.float64)
        out = np.zeros_like(m)
        fin = np.isfinite(m)
        with np.errstate(over="ignore"):
            out[fin] = np.exp(m[fin])
        return out

    rng = np.random.default_rng(SEED)

    def gen_pair(regime, rows):
        if regime == "dense_m20":
            return rng.uniform(-20.0, 0.0, (rows, Q)), rng.uniform(-20.0, 0.0, (rows, Q))
        if regime == "dense_m200":
            return rng.uniform(-200.0, 0.0, (rows, Q)), rng.uniform(-200.0, 0.0, (rows, Q))
        if regime == "dominant":
            a = rng.uniform(-80.0, -20.0, (rows, Q))
            b = rng.uniform(-80.0, -20.0, (rows, Q))
            a[np.arange(rows), rng.integers(0, Q, rows)] = 0.0
            b[np.arange(rows), rng.integers(0, Q, rows)] = 0.0
            return a, b
        if regime == "fallback":
            a = rng.uniform(-20.0, 0.0, (rows, Q))
            b = rng.uniform(-20.0, 0.0, (rows, Q))
            for i in range(rows):
                if i % 4 == 3:
                    a[i, 0::2] = -np.inf
            return a, b
        raise ValueError("unknown regime " + str(regime))

    lit_a3 = np.full((1, Q), -3.0)
    lit_b3 = np.full((1, Q), -3.0)
    lit_a3[0, 5] = 0.0
    lit_b3[0, 9] = 0.0
    literal_defs = [
        ("uniform_zero", np.zeros((1, Q), dtype=np.float64), np.zeros((1, Q), dtype=np.float64)),
        ("ramp_vs_zero", np.arange(Q, dtype=np.float64).reshape(1, Q) - 31.0, np.zeros((1, Q), dtype=np.float64)),
        ("peak_vs_peak", lit_a3, lit_b3),
    ]
    literal_checks = []
    for name, la, lb in literal_defs:
        ref = _minus_block(la, lb, index)
        pro, raw_min, nfb = fwht_minus_block(la, lb)
        both = np.isfinite(ref) & np.isfinite(pro)
        literal_checks.append({
            "name": name,
            "max_abs_prob_err": float(np.abs(probs(pro) - probs(ref)).max()),
            "finite_log_err": float(np.abs(ref[both] - pro[both]).max()) if both.any() else None,
            "argmax_equal": bool(np.argmax(ref, axis=1)[0] == np.argmax(pro, axis=1)[0]),
            "support_equal": bool((np.isfinite(ref) == np.isfinite(pro)).all()),
            "raw_negative_minimum": raw_min,
            "fallback_rows": nfb,
        })

    cells = []
    for regime in REGIME_IDS:
        for rows in ROW_COUNTS:
            first, second = gen_pair(regime, rows)
            ref_out = _minus_block(first, second, index)
            proto_out, raw_min, nfb = fwht_minus_block(first, second)
            for _ in range(N_WARM):
                fwht_minus_block(first, second)
                _minus_block(first, second, index)
            proto_times = []
            direct_times = []
            for rep in range(N_REP):
                if rep % 2 == 0:
                    s = time.perf_counter()
                    fwht_minus_block(first, second)
                    e1 = time.perf_counter()
                    _minus_block(first, second, index)
                    e2 = time.perf_counter()
                    proto_times.append(e1 - s)
                    direct_times.append(e2 - e1)
                else:
                    s = time.perf_counter()
                    _minus_block(first, second, index)
                    e1 = time.perf_counter()
                    fwht_minus_block(first, second)
                    e2 = time.perf_counter()
                    direct_times.append(e1 - s)
                    proto_times.append(e2 - e1)
            pr = probs(ref_out)
            pp = probs(proto_out)
            both = np.isfinite(ref_out) & np.isfinite(proto_out)
            proto_med = float(np.median(np.asarray(proto_times)))
            direct_med = float(np.median(np.asarray(direct_times)))
            cells.append({
                "regime": regime,
                "rows": rows,
                "max_abs_prob_err": float(np.abs(pp - pr).max()),
                "finite_log_err": float(np.abs(ref_out[both] - proto_out[both]).max()) if both.any() else None,
                "argmax_mismatch_rows": int((np.argmax(ref_out, axis=1) != np.argmax(proto_out, axis=1)).sum()),
                "support_mismatch_rows": int((np.isfinite(ref_out) != np.isfinite(proto_out)).any(axis=1).sum()),
                "raw_negative_minimum": raw_min,
                "fallback_rows": nfb,
                "proto_seconds_all": [float(t) for t in proto_times],
                "direct_seconds_all": [float(t) for t in direct_times],
                "proto_median_s": proto_med,
                "direct_median_s": direct_med,
                "direct_median_over_proto_median_descriptive": (direct_med / proto_med) if proto_med > 0 else None,
            })
            print("cell %s rows=%d prob_err=%.3e log_err=%s argmm=%d supmm=%d rawmin=%s fb=%d proto_med=%.6f direct_med=%.6f" % (
                regime, rows, cells[-1]["max_abs_prob_err"], str(cells[-1]["finite_log_err"]),
                cells[-1]["argmax_mismatch_rows"], cells[-1]["support_mismatch_rows"],
                str(raw_min), nfb, proto_med, direct_med))

    sc_profile = []
    for n in SC_NS:
        for blk in range(SC_BLOCKS_PER_N):
            m = rng.uniform(-20.0, 0.0, (n, Q))
            s = time.perf_counter()
            res = sc_decode(m, field=field, alpha=ALPHA)
            e = time.perf_counter()
            sc_profile.append({
                "N": n, "block": blk, "seconds": float(e - s),
                "status": res.status, "u_hat_sum": int(np.asarray(res.u_hat).sum()),
            })
            print("sc N=%d block=%d seconds=%.6f status=%s" % (n, blk, e - s, res.status))

    finite_logs = [c["finite_log_err"] for c in cells if c["finite_log_err"] is not None]
    aggregates = {
        "worst_max_abs_prob_err": max(c["max_abs_prob_err"] for c in cells),
        "worst_finite_log_err": max(finite_logs) if finite_logs else None,
        "total_argmax_mismatch_rows": sum(c["argmax_mismatch_rows"] for c in cells),
        "total_support_mismatch_rows": sum(c["support_mismatch_rows"] for c in cells),
        "min_raw_negative_minimum": min(c["raw_negative_minimum"] for c in cells if c["raw_negative_minimum"] is not None),
        "total_fallback_rows": sum(c["fallback_rows"] for c in cells),
    }

    memory_estimates = []
    for rows in ROW_COUNTS:
        memory_estimates.append({
            "rows": rows,
            "direct_q2_gather_bytes": rows * Q * Q * 8,
            "direct_formula": "rows*q*q*8 float64 gather (first[:,index]+second[:,None,:])",
            "fwht_q_storage_bytes": 2 * rows * Q * 8,
            "fwht_formula": "2*rows*q*8 float64 spectra (product in place; output rows*q*8 separate)",
        })

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
        "probe_id": "nbpolar_x10_fwht_kernel_scaling",
        "tier": "X",
        "status": "X10_PROBE_COMPLETE_DESCRIPTIVE_ONLY",
        "question": "FWHT numerical-equivalence and scaling record for the all-finite GF(32) SC minus-node (descriptive only)",
        "parameters": {
            "seed": SEED, "q": Q, "alpha": ALPHA,
            "regimes": REGIME_IDS, "row_counts": ROW_COUNTS,
            "untimed_warmups_per_implementation": N_WARM, "timed_reps_per_implementation": N_REP,
            "alternating_order": True, "sc_N": SC_NS, "sc_blocks_per_N": SC_BLOCKS_PER_N,
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
        "literal_checks": literal_checks,
        "cells": cells,
        "memory_estimates": memory_estimates,
        "sc_profile": sc_profile,
        "aggregates": aggregates,
        "environment": {
            "interpreter": INTERPRETER,
            "python": sys.version,
            "numpy": str(np.__version__),
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "access_scope": {
            "paths_read": [str(PREREG_PATH)],
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
        "claim_boundary": "Tier-X non-claim probe: ratios and errors are descriptive records only; no threshold, winner, candidate, acceptance, or scientific label.",
        "notes": [
            "Accepted sc.py was imported read-only and never modified; FWHT was never spliced into sc_decode.",
            "Fallback regime placement is deterministic (pair i with i%4==3; first-row even symbols -inf); finite values come from the frozen probe RNG stream.",
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
except BaseException as exc:
    import traceback
    traceback.print_exc()
    stop("exception", {"error": repr(exc)})
```
