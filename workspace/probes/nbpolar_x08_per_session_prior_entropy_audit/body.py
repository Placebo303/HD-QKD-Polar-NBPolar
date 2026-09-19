"""X08 Tier-X frozen body: per-session prior entropy audit (decoder-free).

ONE read-only content open of the digest-pinned P20H calibrated_prior.npz;
no protected counts NPZ, no parquet, no sibling-checkout artifact, no
decoder/RNG/tag call, no calibration refit, no lambda beyond the control
(137.3823795883264) and 0. Descriptive numbers only.
"""

from __future__ import annotations

import hashlib
import json
import math
import resource
import sys
import time
from pathlib import Path

T0 = time.perf_counter()

REPO = Path("/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar")
PROBE_ID = "nbpolar_x08_per_session_prior_entropy_audit"
PROBE_DIR = REPO / "workspace" / "probes" / PROBE_ID
PREREG_PATH = PROBE_DIR / "prereg.md"
RESULTS_PATH = PROBE_DIR / "results.json"
BODY_PATH = PROBE_DIR / "body.py"
NPZ_PATH = (
    REPO / ".workbuddy" / "queue"
    / "NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION"
    / "per_session_calibration" / "calibrated_prior.npz"
)

INTERPRETER = "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python"
COMMAND_TEXT = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && "
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "
    "MALLOC_ARENA_MAX=2 && timeout 120 " + INTERPRETER
    + " workspace/probes/nbpolar_x08_per_session_prior_entropy_audit/body.py"
)

QUESTION = (
    "Did the P20H per-session calibration's lambda=137.3823795883264 "
    "concentration smoothing inflate the 1.5M TRAIN prior entropy H1 relative "
    "to the P7-equivalent raw-count MLE + 1e-15 floor rule, and by how much? "
    "Descriptive decision input only."
)
DIGEST_PIN = "e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b"
LAMBDA_CONTROL = 137.3823795883264
FLOOR = 1e-15
STORED_H1 = 2.006647056368773
STORED_H2 = 1.9017235959286112
STORED_H_TOTAL = STORED_H1 + STORED_H2
N_BUDGET = 32768
K1_LEVELS = [319, 447, 575, 831]
KEY_BITS_REF = 34119
TOL = 1e-12

NOTES: list = []


def note(msg: str) -> None:
    NOTES.append(str(msg))


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def rss_bytes() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def k_total_for(h_total: float) -> int:
    raw = math.floor((1.3 * N_BUDGET * float(h_total) - 64.0) / 5.0)
    return max(0, min(65536, int(raw)))


def write_results(payload: dict) -> None:
    RESULTS_PATH.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- freeze bookkeeping (before any npz open)
prereg_raw = PREREG_PATH.read_bytes()
body_raw = BODY_PATH.read_bytes()
prereg_sha256 = sha256_bytes(prereg_raw)
body_sha256 = sha256_bytes(body_raw)
prereg_text = prereg_raw.decode("utf-8")
_FENCE = "```python\n"
_i0 = prereg_text.index(_FENCE) + len(_FENCE)
_i1 = prereg_text.index("\n```", _i0)
embedded_body = prereg_text[_i0:_i1]
body_sha_match = bool(embedded_body.encode("utf-8") == body_raw)
if not body_sha_match:
    write_results({
        "probe_id": PROBE_ID,
        "tier": "X",
        "status": "X08_PROBE_STOPPED_BODY_MISMATCH",
        "question": QUESTION,
        "prereg_sha256": prereg_sha256,
        "body_sha256": body_sha256,
        "body_sha_match": False,
        "command": COMMAND_TEXT,
        "interpreter": INTERPRETER,
        "wall_s": time.perf_counter() - T0,
        "rss_bytes": rss_bytes(),
        "decoder_calls": 0,
        "rng_calls": 0,
        "tag_calls": 0,
        "writes": [str(RESULTS_PATH)],
        "notes": ["body.py bytes differ from the prereg.md fenced block; no npz open attempted"],
    })
    print("STOP body/prereg byte mismatch; no npz open attempted")
    raise SystemExit(2)

# ------------------------------------------------- pure-code imports (no I/O, no npz open)
sys.path.insert(0, str(REPO / "comparison_bench" / "src"))
import numpy as np  # noqa: E402

from comparison_bench.formal_ir.nbpolar.prior import (  # noqa: E402
    derive_p1,
    derive_p2,
    smooth_joint_to_conditional,
)
from comparison_bench.formal_ir.nbpolar.target_construction import entropy_bits  # noqa: E402

try:
    from comparison_bench.formal_ir.nbpolar.per_session_calibration import (  # noqa: E402
        PRIOR_NPZ_KEYS,
        canonical_prior_digest,
    )
    digest_impl = "module:per_session_calibration.canonical_prior_digest"
except Exception as exc:  # inline fallback uses exactly the documented recipe
    PRIOR_NPZ_KEYS = (
        "counts_ab", "f_prior", "p1", "p2", "p_b",
        "lambda_star", "floor_value", "h1", "h2", "h_total",
    )
    def canonical_prior_digest(arrays: dict) -> str:  # type: ignore[no-redef]
        parts = []
        for key in sorted(arrays):
            arr = np.asarray(arrays[key])
            parts.append(key.encode("utf-8"))
            parts.append(str(tuple(int(v) for v in arr.shape)).encode("utf-8"))
            parts.append(str(arr.dtype).encode("utf-8"))
            parts.append(np.ascontiguousarray(arr).tobytes(order="C"))
        return hashlib.sha256(b"\x00".join(parts)).hexdigest()
    digest_impl = "inline-fallback:sorted-keys key+shape+dtype+C-order-bytes sha256"
    note("per_session_calibration import failed (%r); used inline digest fallback" % (exc,))

# ---------------------------------------------------------------- 1. stat BEFORE load
st0 = NPZ_PATH.stat()
size0 = int(st0.st_size)
mtime0 = int(st0.st_mtime_ns)

# ---------------------------------------------------------------- 2. single content open
open_count = 0
reopen_attempted = False
npz = np.load(str(NPZ_PATH), allow_pickle=False)
open_count = 1
with npz:
    keys = sorted(str(k) for k in npz.files)
    if set(keys) != set(PRIOR_NPZ_KEYS):
        st1 = NPZ_PATH.stat()
        write_results({
            "probe_id": PROBE_ID,
            "tier": "X",
            "status": "X08_PROBE_STOPPED_KEY_MISMATCH",
            "question": QUESTION,
            "prereg_sha256": prereg_sha256,
            "body_sha256": body_sha256,
            "body_sha_match": True,
            "artifact_open": {
                "path": str(NPZ_PATH),
                "size_bytes": size0,
                "mtime_ns": mtime0,
                "keys": keys,
                "expected_keys": sorted(PRIOR_NPZ_KEYS),
                "open_count": open_count,
                "reopen_attempted": reopen_attempted,
            },
            "command": COMMAND_TEXT,
            "interpreter": INTERPRETER,
            "wall_s": time.perf_counter() - T0,
            "rss_bytes": rss_bytes(),
            "decoder_calls": 0,
            "rng_calls": 0,
            "tag_calls": 0,
            "writes": [str(RESULTS_PATH)],
            "notes": NOTES + ["key-set mismatch; no entropy computed"],
        })
        print("STOP key-set mismatch")
        raise SystemExit(2)
    arrays = {k: np.asarray(npz[k]) for k in PRIOR_NPZ_KEYS}

# re-stat AFTER load; record unchanged
st1 = NPZ_PATH.stat()
size1 = int(st1.st_size)
mtime1 = int(st1.st_mtime_ns)
stat_unchanged = bool(size0 == size1 and mtime0 == mtime1)

digest_recomputed = canonical_prior_digest(arrays)
digest_match = bool(digest_recomputed == DIGEST_PIN)
if not digest_match:
    write_results({
        "probe_id": PROBE_ID,
        "tier": "X",
        "status": "X08_PROBE_STOPPED_DIGEST_MISMATCH",
        "question": QUESTION,
        "prereg_sha256": prereg_sha256,
        "body_sha256": body_sha256,
        "body_sha_match": True,
        "artifact_open": {
            "path": str(NPZ_PATH),
            "size_bytes": size0,
            "mtime_ns": mtime0,
            "size_bytes_after": size1,
            "mtime_ns_after": mtime1,
            "stat_unchanged": stat_unchanged,
            "keys": keys,
            "open_count": open_count,
            "reopen_attempted": reopen_attempted,
            "canonical_digest_recomputed": digest_recomputed,
            "canonical_digest_pin": DIGEST_PIN,
            "digest_impl": digest_impl,
            "digest_match": False,
        },
        "command": COMMAND_TEXT,
        "interpreter": INTERPRETER,
        "wall_s": time.perf_counter() - T0,
        "rss_bytes": rss_bytes(),
        "decoder_calls": 0,
        "rng_calls": 0,
        "tag_calls": 0,
        "writes": [str(RESULTS_PATH)],
        "notes": NOTES + ["canonical digest mismatch; no entropy computed"],
    })
    print("STOP digest mismatch")
    raise SystemExit(2)

counts_ab = np.asarray(arrays["counts_ab"], dtype=np.float64)
stored_f_prior = np.asarray(arrays["f_prior"], dtype=np.float64)
n_b = counts_ab.sum(axis=0)
total_count = float(counts_ab.sum())
p_b = n_b / total_count

# ---------------------------------------------------------------- support stats
n_cells = int(counts_ab.size)
zero_cells = int(np.sum(counts_ab == 0))
zero_columns = int(np.sum(n_b == 0))
nonzero_columns = int(np.sum(n_b > 0))
counts_total_int = int(round(total_count))


def entropy_variant(lam: float) -> dict:
    f_smooth = smooth_joint_to_conditional(counts_ab, lam)
    floor_hits = int(np.sum(f_smooth < FLOOR))
    f = np.maximum(f_smooth, FLOOR)
    f = f / f.sum(axis=0, keepdims=True)
    p1 = derive_p1(np.ascontiguousarray(f))
    p2 = derive_p2(np.ascontiguousarray(f))
    h1 = float(np.sum(p_b * entropy_bits(p1, axis=0)))
    h2 = float(np.sum(p_b[None, :] * p1 * entropy_bits(p2, axis=2)))
    for name, val in (("h1", h1), ("h2", h2)):
        if not math.isfinite(val):
            st1b = NPZ_PATH.stat()
            write_results({
                "probe_id": PROBE_ID,
                "tier": "X",
                "status": "X08_PROBE_STOPPED_NONFINITE",
                "question": QUESTION,
                "prereg_sha256": prereg_sha256,
                "body_sha256": body_sha256,
                "body_sha_match": True,
                "artifact_open": {
                    "path": str(NPZ_PATH),
                    "size_bytes": size0,
                    "mtime_ns": mtime0,
                    "keys": keys,
                    "open_count": open_count,
                    "reopen_attempted": reopen_attempted,
                    "canonical_digest_recomputed": digest_recomputed,
                    "canonical_digest_pin": DIGEST_PIN,
                    "digest_match": True,
                },
                "failing": {"lambda": lam, "name": name, "value": str(val)},
                "command": COMMAND_TEXT,
                "interpreter": INTERPRETER,
                "wall_s": time.perf_counter() - T0,
                "rss_bytes": rss_bytes(),
                "decoder_calls": 0,
                "rng_calls": 0,
                "tag_calls": 0,
                "writes": [str(RESULTS_PATH)],
                "notes": NOTES + ["nonfinite entropy value"],
            })
            print("STOP nonfinite value lam=%r %s=%s" % (lam, name, val))
            raise SystemExit(2)
    return {
        "f_smooth": f_smooth,
        "f": f,
        "p1": p1,
        "p2": p2,
        "h1": h1,
        "h2": h2,
        "h_total": h1 + h2,
        "floor_hits_cells": floor_hits,
        "floor_hits_fraction": floor_hits / n_cells,
    }


# ---------------------------------------------------------------- 3. two variants
var_L = entropy_variant(LAMBDA_CONTROL)
var_R = entropy_variant(0.0)

d_h1 = abs(var_L["h1"] - STORED_H1)
d_h2 = abs(var_L["h2"] - STORED_H2)
d_ht = abs(var_L["h_total"] - STORED_H_TOTAL)
stored_h_total = float(np.asarray(arrays["h_total"]))
f_prior_max_abs = float(np.abs(var_L["f"] - stored_f_prior).max())

# ---------------------------------------------------------------- 4. independent literal Variant R
mat = np.asarray(counts_ab, dtype=np.float64)
tot = float(mat.sum())
p_global = mat.sum(axis=1) / tot
nb = mat.sum(axis=0)
f_raw = np.empty_like(mat)
nz = nb > 0
f_raw[:, nz] = mat[:, nz] / nb[nz][None, :]
if bool((~nz).any()):
    f_raw[:, ~nz] = p_global[:, None]
f_lit = np.maximum(f_raw, FLOOR)
f_lit = f_lit / f_lit.sum(axis=0, keepdims=True)
p1_lit = derive_p1(np.ascontiguousarray(f_lit))
p2_lit = derive_p2(np.ascontiguousarray(f_lit))
h1_lit = float(np.sum(p_b * entropy_bits(p1_lit, axis=0)))
h2_lit = float(np.sum(p_b[None, :] * p1_lit * entropy_bits(p2_lit, axis=2)))
raw_vs_lit_f_max_abs = float(np.abs(var_R["f"] - f_lit).max())
raw_vs_lit_h1_abs = abs(var_R["h1"] - h1_lit)
raw_vs_lit_h2_abs = abs(var_R["h2"] - h2_lit)

# ---------------------------------------------------------------- 5. implied budgets
k_total_lambda = k_total_for(var_L["h_total"])
k_total_raw = k_total_for(var_R["h_total"])
l1_bits_lambda = N_BUDGET * var_L["h1"]
l1_bits_raw = N_BUDGET * var_R["h1"]

results = {
    "probe_id": PROBE_ID,
    "tier": "X",
    "status": "X08_PROBE_COMPLETE_DESCRIPTIVE_ONLY",
    "question": QUESTION,
    "prereg_sha256": prereg_sha256,
    "body_sha256": body_sha256,
    "body_sha_match": True,
    "artifact_open": {
        "path": str(NPZ_PATH),
        "size_bytes": size0,
        "mtime_ns": mtime0,
        "size_bytes_after": size1,
        "mtime_ns_after": mtime1,
        "stat_unchanged": stat_unchanged,
        "keys": keys,
        "open_count": open_count,
        "reopen_attempted": reopen_attempted,
        "canonical_digest_recomputed": digest_recomputed,
        "canonical_digest_pin": DIGEST_PIN,
        "digest_impl": digest_impl,
        "digest_match": True,
    },
    "counts_stats": {
        "shape": [int(v) for v in counts_ab.shape],
        "total": counts_total_int,
        "total_float": total_count,
        "zero_cells": zero_cells,
        "zero_columns": zero_columns,
        "nonzero_columns": nonzero_columns,
    },
    "variant_lambda_control": {
        "lambda": LAMBDA_CONTROL,
        "h1": var_L["h1"],
        "h2": var_L["h2"],
        "h_total": var_L["h_total"],
        "floor_hits_cells": var_L["floor_hits_cells"],
        "floor_hits_fraction": var_L["floor_hits_fraction"],
        "stored_h1": STORED_H1,
        "stored_h2": STORED_H2,
        "stored_h_total": STORED_H_TOTAL,
        "stored_h_total_from_npz": stored_h_total,
        "stored_lambda_star": float(np.asarray(arrays["lambda_star"])),
        "stored_floor_value": float(np.asarray(arrays["floor_value"])),
        "literal_abs_delta": {"h1": d_h1, "h2": d_h2, "h_total": d_ht},
        "tolerance": TOL,
    },
    "variant_raw_floor": {
        "rule": "raw-count MLE + 1e-15 floor + column renormalize (lam=0.0; zero columns fall back to p_global)",
        "lambda": 0.0,
        "h1": var_R["h1"],
        "h2": var_R["h2"],
        "h_total": var_R["h_total"],
        "floor_hits_cells": var_R["floor_hits_cells"],
        "floor_hits_fraction": var_R["floor_hits_fraction"],
        "zero_column_fallback_columns": zero_columns,
    },
    "cross_checks": {
        "lambda_f_prior_vs_stored_f_prior_max_abs": f_prior_max_abs,
        "raw_vs_independent_literal_max_abs": raw_vs_lit_f_max_abs,
        "raw_vs_independent_literal_h1_abs": raw_vs_lit_h1_abs,
        "raw_vs_independent_literal_h2_abs": raw_vs_lit_h2_abs,
        "tolerance": TOL,
        "entropy_impl": "comparison_bench.formal_ir.nbpolar.target_construction.entropy_bits (-sum p log2 p, 0log0=0)",
    },
    "implied_budget": {
        "N": N_BUDGET,
        "formula": "floor((1.3*32768*H_total - 64)/5) clipped [0,65536]",
        "k_total_lambda": k_total_lambda,
        "k_total_raw": k_total_raw,
        "frozen_key_bits_reference": KEY_BITS_REF,
        "frozen_k1_levels": list(K1_LEVELS),
        "l1_side_info_bits_at_H1": {
            "formula": "N*H1",
            "lambda_smoothing": l1_bits_lambda,
            "raw_floor": l1_bits_raw,
        },
    },
    "command": COMMAND_TEXT,
    "interpreter": INTERPRETER,
    "wall_s": time.perf_counter() - T0,
    "rss_bytes": rss_bytes(),
    "decoder_calls": 0,
    "rng_calls": 0,
    "tag_calls": 0,
    "writes": [str(RESULTS_PATH)],
    "notes": NOTES + [
        "single npz content open; no reopen; no protected/parquet/sibling opens",
        "Variant L must reproduce stored h1/h2 within 1e-12; abs deltas recorded descriptively",
        "reruns_to_fix_execution_errors: none",
    ],
}

# ---------------------------------------------------------------- 6. write results.json
write_results(results)

# ---------------------------------------------------------------- 7. stdout summary
print("digest_match=True")
print("L h1=%.15f h2=%.15f total=%.15f" % (var_L["h1"], var_L["h2"], var_L["h_total"]))
print("L literal_abs_delta h1=%.3e h2=%.3e total=%.3e" % (d_h1, d_h2, d_ht))
print("R h1=%.15f h2=%.15f total=%.15f" % (var_R["h1"], var_R["h2"], var_R["h_total"]))
print("R floor_hits=%d zero_columns=%d" % (var_R["floor_hits_cells"], zero_columns))
print("K_total lambda=%d raw=%d" % (k_total_lambda, k_total_raw))
print("f_prior_max_abs=%.3e raw_vs_lit_max_abs=%.3e" % (f_prior_max_abs, raw_vs_lit_f_max_abs))
