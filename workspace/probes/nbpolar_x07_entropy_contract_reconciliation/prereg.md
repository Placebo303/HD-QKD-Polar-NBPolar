# X07 Tier-X prereg — entropy-contract reconciliation (frozen before artifact open)

- Task packet: `.workbuddy/queue/NBPOLAR-X07-ENTROPY-CONTRACT-RECONCILIATION/TASK_PACKET.md`
- Authorization prompt: `.workbuddy/queue/NBPOLAR-X07-ENTROPY-CONTRACT-RECONCILIATION/AUTHORIZATION_PROMPT.md`
- Probe id: `nbpolar_x07_entropy_contract_reconciliation`
- Tier: X (non-claim, descriptive). Output root: `workspace/probes/nbpolar_x07_entropy_contract_reconciliation/` with exactly `prereg.md` and `results.json`.
- Frozen (UTC): 2026-09-13T17:46:01Z (the body re-reads this file and records its sha256; the frozen analysis body below is executed byte-identically from `/tmp/x07_body.py`).
- Scope: identify the exact distributions, weighting, axis convention and smoothing operation behind (a) the V49 1M TRAIN `H1+H2 = 0.801` report, (b) the accepted Model-F smoothed table, and (c) the distribution X06 sampled (`B~p_b`, then `A~f(·|B)`), without selecting or tuning an estimator.

## Question

Why does the accepted V49 TRAIN channel report approximately `H1+H2 = 0.801 bits/symbol`
while the Model-F distribution sampled by X06 reports approximately `7.61 bits/symbol`
(X06's own recorded totals are `7.509440314835753` table-based and `7.519452511434579`
genie-NLL-mean based)? Which population, conditional table, Bob weighting, axis/packing
convention and smoothing operation is behind each number?

## Single artifact content read

Exactly ONE call, consuming artifact-content read allowance 1/1:

`comparison_bench.formal_ir.nbpolar.prior_artifact.load_prior_artifact(`

`  '/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz',`

`  '/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input_summary.json')`

No reopen, no retry after the content read, no other sibling artifact or raw data.
Arrays stay in memory only.

## Registered inputs (read-only, hashed in results.json)

- `docs/v49_distribution_tables/v49_train_val_hold_nll.csv` — frozen 1M TRAIN row.
- `docs/v49-distribution-shift-diagnosis-20260827.md` — entropy-contract sections (row cross-check).
- `workspace/probes/nbpolar_x06_empirical_construction_order/results.json` — X06 table h1/h2, genie h means, sampler config, artifact identity.
- `docs/nbpolar/PHASE4_P0_PRIOR_CONTRACT.md` — P0 prior contract, axis/packing, lifecycle.
- `.workbuddy/queue/NBPOLAR-PHASE4-P2-CAL-DEV/cal_prior_validation/cal_prior_summary.json` — accepted P2 entropies/CE.
- Additional recorded provenance documents (repo-only): `comparison_bench/outputs_comparison/nonbinary_diagnostics/nbldpc_v25_20260818/run_04/data_inventory.json` (V25 1M source identity/raw SER/delta support), `comparison_bench/outputs_comparison/v72p2d4r2_cal_gf32_model_rate_audit_20260905/{manifest.json,report.md}` (D4R2 session + held-out CE), `docs/research_cycles/V72P2D5-GF32-RATE-MOTHER/G1_INFORMATION_RECOVERY_R2_REVIEW_R1.md` (candidate in-sample CE/MI).

## Frozen formulas (bits; `xlog2x(p) = -p·log2(p)` with `xlog2x(0) = 0`)

Axis/packing frozen from P0: tables are `[Alice,Bob]`; `A = 32·U1 + U2` with `high = U1 = A>>5`, `low = U2 = A&31`; `symbol = low + 32·high`.

```text
p_b[b]      = stored artifact Bob marginal (validated against counts-derived marginal, tol 1e-12; never normalized into agreement)
n_b[b]      = sum_a counts[a,b]
p_global[a] = sum_b counts[a,b] / sum(counts)
p_mle(a|b)  = counts[a,b] / n_b[b]                                  (raw-count MLE)
f           = smooth_joint_to_conditional(counts, LAMBDA_STAR)      (accepted table)
f(a|b)      = (counts[a,b] + lambda*p_global[a]) / (n_b[b] + lambda); zero-mass columns -> p_global
p1(f)[u1,b] = sum_u2 f[32*u1+u2, b]                                 derive_p1
p2(f)[u1,b,u2] = f[32*u1+u2, b] / p1(f)[u1,b]                       derive_p2
H(A|B)      = -sum_b p_b[b] sum_a xlog2x(p(a|b))
H1          = -sum_b p_b[b] sum_u1 xlog2x(p1[u1,b])
H2          = -sum_b p_b[b] sum_u1 p1[u1,b] sum_u2 xlog2x(p2[u1,b,u2])
CE(p_mle->f)= -sum_b p_b[b] sum_a p_mle(a|b) log2 f(a|b)            (chain: CE1+CE2)
CE(f->p_mle)= -sum_b p_b[b] sum_a f(a|b) log2 p_mle(a|b)            (+inf if f has mass on zero MLE support)
chain residual = H1 + H2 - H(A|B)                                   (must be <= 1e-10)
```

An independent literal implementation (scalar `math.log2` loops, no shared vectorized helper) recomputes `H(A|B)`, `H1`, `H2`, `CE(p_mle->f)` for the raw MLE and the accepted table, plus `lambda=0`; the vectorized/literal max absolute difference is reported.

`lambda = 0` is recomputed once for attribution only (`smooth_joint_to_conditional(counts, 0.0)` must equal the item-1 MLE table). No lambda scan, no tuning.

X06 sampling law (from X06 prereg `config.sampler`): `B ~ p_b`, then `A | B ~ f(·|B)`. Expected layer conditional entropies therefore equal the accepted smoothed-model entropies under `p_b` (`H1_f`, `H2_f`); X06's recorded `entropy.h1_bits/h2_bits` are computed from exactly those `p1/p2` tables. X06's recorded genie means are a different functional (per-coordinate NLL in the polar-transformed domain after full-true disclosure) and are compared descriptively with an across-coordinate dispersion SE.

## Frozen tolerances

- `TOL_PB = 1e-12` (p_b vs counts-derived Bob marginal; mismatch is reported and STOPs, never repaired)
- `TOL_NORM = 1e-12` (column/symbol normalization deviations, axis/layout sentinels)
- `TOL_CHAIN = 1e-10` (chain residual)
- `TOL_LITERAL = 1e-9` (vectorized vs literal max abs difference)
- `TOL_RECORD = 1e-9` (X06/P2 recorded-value cross-checks; V49 doc row vs CSV)
- quantile method: linear (NumPy default)

## Output schema (`results.json`)

`probe_id, tier, status, prereg_sha256, body_sha256, body_sha_match, artifact_open`
(count/identity/allowance, `open_count=1`, no reopen/retry, 0 decoder/RNG/tag/construction),
`inputs` (path+sha256+bytes), `v49_record`, `x06_record`, `p2_record`, `p0_record`,
`v25_record`, `d4r2_record`, `g1_record`, `quantities` (raw MLE, accepted smoothed,
lambda=0, CE decompositions, marginals/MI), `provenance_table` (each row: source population,
conditional table, Bob weights, smoothing, entropy/CE/sampling-model type), `vectorized_vs_literal`,
`chain`, `axis_packing_controls`, `support_aggregates`, `smoothing_diagnostics`,
`v49_comparisons`, `x06_sampling_law`, `earliest_contract_divergence`, `resource`
(`wall_s`, `rss_bytes_peak`), `commands`, `notes`.
Only aggregates and quantiles are persisted: no 1024x1024 table, raw counts, samples or private vectors.

## Stop rules

STOP and preserve the output root (no retry) on: input/root mismatch, a second artifact open,
`p_b` mismatch > `TOL_PB`, axis/layout/transpose sentinel disagreement > `TOL_NORM`,
packing round-trip failure, vectorized-vs-literal disagreement > `TOL_LITERAL`,
chain residual > `TOL_CHAIN`, nonfinite required result, or recorded-value cross-check
failure > `TOL_RECORD`. A stop writes a `STOPPED_*` `results.json` with the checks performed.

Forbidden: production/OpenSpec behavior edits, decoder/RNG/tag/construction call, `sc_decode`/FWHT/APP/SCL, estimator selection/tuning, second artifact open, raw/real data, EVAL, N>256 work, threshold/pass-fail/candidate/accepted, ledger/memory/index update, commit/push.

## Frozen analysis body (executed byte-identically from `/tmp/x07_body.py`)

```python
"""X07 Tier-X frozen body: entropy-contract reconciliation (decoder-free).

Single Model-F artifact content read; no decoder/RNG/tag/construction/sc_decode/
FWHT/APP/SCL call; no lambda scan or tuning; no production/OpenSpec edit.
Aggregates and quantiles only (no 1024x1024 table, raw counts, samples or
private vectors are persisted). STOP semantics preserve the output root and
never retry after the artifact content read.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import resource
import sys
import time
from pathlib import Path

import numpy as np

T0 = time.monotonic()

REPO = Path("/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar")
PROBE_DIR = REPO / "workspace" / "probes" / "nbpolar_x07_entropy_contract_reconciliation"
PREREG_PATH = PROBE_DIR / "prereg.md"
RESULTS_PATH = PROBE_DIR / "results.json"
BODY_PATH = Path("/tmp/x07_body.py")
INTERPRETER = "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python"
COMMAND_TEXT = INTERPRETER + " - < /tmp/x07_body.py"

NPZ_PATH = Path(
    "/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz"
)
SUMMARY_PATH = Path(
    "/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input_summary.json"
)

V49_CSV = REPO / "docs" / "v49_distribution_tables" / "v49_train_val_hold_nll.csv"
V49_MD = REPO / "docs" / "v49-distribution-shift-diagnosis-20260827.md"
X06_JSON = REPO / "workspace" / "probes" / "nbpolar_x06_empirical_construction_order" / "results.json"
P0_MD = REPO / "docs" / "nbpolar" / "PHASE4_P0_PRIOR_CONTRACT.md"
P2_JSON = (
    REPO / ".workbuddy" / "queue" / "NBPOLAR-PHASE4-P2-CAL-DEV" / "cal_prior_validation" / "cal_prior_summary.json"
)
V25_INV = (
    REPO / "comparison_bench" / "outputs_comparison" / "nonbinary_diagnostics"
    / "nbldpc_v25_20260818" / "run_04" / "data_inventory.json"
)
D4R2_MANIFEST = (
    REPO / "comparison_bench" / "outputs_comparison"
    / "v72p2d4r2_cal_gf32_model_rate_audit_20260905" / "manifest.json"
)
D4R2_REPORT = (
    REPO / "comparison_bench" / "outputs_comparison"
    / "v72p2d4r2_cal_gf32_model_rate_audit_20260905" / "report.md"
)
G1_REVIEW = (
    REPO / "docs" / "research_cycles" / "V72P2D5-GF32-RATE-MOTHER"
    / "G1_INFORMATION_RECOVERY_R2_REVIEW_R1.md"
)

N = 1024
Q = 32
TOTAL_SYMBOLS = 262144
V49_N_TRAIN_1M = 307200
V49_MIN_NB_1M = 210
RARE_NB = 10
LOG2N = math.log2(N)

TOL_PB = 1e-12
TOL_NORM = 1e-12
TOL_CHAIN = 1e-10
TOL_LITERAL = 1e-9
TOL_RECORD = 1e-9

NOTES = []


def note(msg):
    NOTES.append(str(msg))


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def xlog2x(mat):
    m = np.asarray(mat, dtype=np.float64)
    out = np.zeros_like(m)
    np.log2(m, out=out, where=m > 0)
    return -m * out


def weighted_quantile(values, weights, qs):
    order = np.argsort(values, kind="stable")
    v = np.asarray(values, dtype=np.float64)[order]
    w = np.asarray(weights, dtype=np.float64)[order]
    cw = np.cumsum(w) / float(np.sum(w))
    return {("%.2f" % q): float(np.interp(q, cw, v)) for q in qs}


# ---------------------------------------------------------------- freeze bookkeeping
prereg_sha256 = sha256_file(PREREG_PATH)
body_sha256 = sha256_file(BODY_PATH)
prereg_text = PREREG_PATH.read_text(encoding="utf-8")
_FENCE = "```python\n"
_i0 = prereg_text.index(_FENCE) + len(_FENCE)
_i1 = prereg_text.index("\n```", _i0)
embedded_body = prereg_text[_i0:_i1]
body_sha_match = bool(embedded_body.encode("utf-8") == BODY_PATH.read_bytes())
if not body_sha_match:
    print("FATAL body_sha_match false; refusing to run the staged body")
    raise SystemExit(2)

sys.path.insert(0, str(REPO / "comparison_bench" / "src"))
from comparison_bench.formal_ir.nbpolar import prior, prior_artifact  # noqa: E402

LAMBDA_STAR = float(prior_artifact.LAMBDA_STAR)

STDOUT = []
FAILURE = {"active": False, "reason": None, "detail": None}
OPEN_RECORD = None


def stop(reason, detail):
    """Write a failure-preserving results record, then exit non-zero (no retry)."""
    FAILURE["active"] = True
    FAILURE["reason"] = str(reason)
    FAILURE["detail"] = detail
    print("STOP: %s" % reason)
    out = {
        "probe_id": "nbpolar_x07_entropy_contract_reconciliation",
        "tier": "X",
        "status": "STOPPED_" + str(reason).upper(),
        "stop_detail": detail,
        "prereg_sha256": prereg_sha256,
        "body_sha256": body_sha256,
        "body_sha_match": body_sha_match,
        "artifact_open": OPEN_RECORD,
        "integrity_checks": checks,
        "commands": commands_log,
        "notes": NOTES,
        "wall_s": time.monotonic() - T0,
        "rss_bytes_peak": rss_bytes_peak(),
    }
    RESULTS_PATH.write_text(json.dumps(out, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    raise SystemExit(2)


def rss_bytes_peak():
    rusage = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    vmhwm = None
    try:
        for line in open("/proc/self/status", encoding="utf-8"):
            if line.startswith("VmHWM:"):
                vmhwm = int(line.split()[1]) * 1024
                break
    except OSError:
        vmhwm = None
    return {"ru_maxrss_bytes": rusage, "vmhwm_bytes": vmhwm, "peak_bytes": max([v for v in (rusage, vmhwm) if v])}


checks = {}
commands_log = [{
    "n": 1,
    "text": COMMAND_TEXT,
    "cwd": str(REPO),
    "kind": "frozen X07 Tier-X body (single artifact content read; no rerun)",
    "exit_code": 0,
}]

# ---------------------------------------------------------------- registered document reads
input_files = {
    "v49_csv": V49_CSV,
    "v49_md": V49_MD,
    "x06_results_json": X06_JSON,
    "p0_prior_contract_md": P0_MD,
    "p2_cal_prior_summary_json": P2_JSON,
    "v25_data_inventory_json": V25_INV,
    "d4r2_manifest_json": D4R2_MANIFEST,
    "d4r2_report_md": D4R2_REPORT,
    "g1_information_recovery_review_md": G1_REVIEW,
}
inputs = {}
for key, path in input_files.items():
    if not path.is_file():
        stop("input_missing", {"key": key, "path": str(path)})
    inputs[key] = {"path": str(path), "sha256": sha256_file(path), "bytes": int(path.stat().st_size)}

with open(V49_CSV, newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
sel = [r for r in rows if r["source"] == "1M" and r["split"] == "TRAIN"]
if len(sel) != 1:
    stop("v49_row_not_unique", {"rows": len(sel)})
csv_row = sel[0]
v49_csv = {
    "source": csv_row["source"],
    "split": csv_row["split"],
    "n": int(float(csv_row["n"])),
    "nll_u1": float(csv_row["nll_u1"]),
    "nll_u2": float(csv_row["nll_u2"]),
    "nll_total": float(csv_row["nll_total"]),
    "ent_u1_given_b": float(csv_row["ent"]),
    "kl_sample": float(csv_row["kl_sample"]),
    "ser": float(csv_row["ser"]),
    "u1_err": float(csv_row["u1_err"]),
    "u2_err": float(csv_row["u2_err"]),
    "zero_B": float(csv_row["zero_B"]),
    "rare_B": float(csv_row["rare_B"]),
}
doc_row_line = None
for ln in V49_MD.read_text(encoding="utf-8").splitlines():
    if ln.startswith("| 1M | TRAIN |"):
        doc_row_line = ln
        break
if doc_row_line is None:
    stop("v49_doc_row_missing", {"md": str(V49_MD)})
cells = [c.strip() for c in doc_row_line.strip().strip("|").split("|")]
doc_keys = ["n", "nll_u1", "nll_u2", "nll_total", "ent", "kl_sample", "ser", "u1_err", "u2_err", "zero_B", "rare_B"]
if len(cells) != len(doc_keys) + 2:
    stop("v49_doc_row_shape", {"cells": len(cells)})
v49_doc = {k: float(c) for k, c in zip(doc_keys, cells[2:])}
cmp_map = {
    "n": "n", "nll_u1": "nll_u1", "nll_u2": "nll_u2", "nll_total": "nll_total",
    "ent": "ent_u1_given_b", "kl_sample": "kl_sample", "ser": "ser",
    "u1_err": "u1_err", "u2_err": "u2_err", "zero_B": "zero_B", "rare_B": "rare_B",
}
v49_doc_vs_csv = {k: float(abs(float(v49_doc[k]) - float(v49_csv[m]))) for k, m in cmp_map.items()}
v49_doc_csv_max = max(v49_doc_vs_csv.values())
if v49_doc_csv_max > TOL_RECORD:
    stop("v49_doc_csv_mismatch", {"max_abs_diff": v49_doc_csv_max, "tol": TOL_RECORD})

x06 = load_json(X06_JSON)
x06_ent = x06["entropy"]
x06_open = x06["artifact_open"]
x06_pooled = x06["train"]["pooled"]
h1_vec = np.asarray(x06_pooled["l1"]["h"], dtype=np.float64)
h2_vec = np.asarray(x06_pooled["l2"]["h"], dtype=np.float64)
l1_mean = float(x06_pooled["l1"]["h_summary"]["mean"])
l2_mean = float(x06_pooled["l2"]["h_summary"]["mean"])
x06_record = {
    "h1_bits_table": float(x06_ent["h1_bits"]),
    "h2_bits_table": float(x06_ent["h2_bits"]),
    "h1_h2_bits_table_sum": float(x06_ent["h1_bits"]) + float(x06_ent["h2_bits"]),
    "epsilon1_raw": float(x06_ent["epsilon1_raw"]),
    "epsilon2_raw": float(x06_ent["epsilon2_raw"]),
    "genie_l1_mean": l1_mean,
    "genie_l2_mean": l2_mean,
    "genie_total_mean": l1_mean + l2_mean,
    "genie_l1_std_across_coords": float(np.std(h1_vec, ddof=1)),
    "genie_l2_std_across_coords": float(np.std(h2_vec, ddof=1)),
    "genie_l1_se_of_mean_approx": float(np.std(h1_vec, ddof=1) / math.sqrt(h1_vec.size)),
    "genie_l2_se_of_mean_approx": float(np.std(h2_vec, ddof=1) / math.sqrt(h2_vec.size)),
    "n_coords": int(h1_vec.size),
    "train_blocks_used_l1": int(x06["counters"]["train_blocks_used_l1"]),
    "train_blocks_used_l2": int(x06["counters"]["train_blocks_used_l2"]),
    "lambda_star": float(x06_open["lambda_star"]),
    "summary_identity": x06_open["summary_identity"],
    "table_checks": x06_open["table_checks"],
    "dev_pooled_L1_bec_k45": x06["dev"]["aggregates"]["pooled"]["counts"]["L1"]["bec"]["45"],
    "dev_pooled_oracle_L2_bec_k140": x06["dev"]["aggregates"]["pooled"]["counts"]["oracle_L2"]["bec"]["140"],
}

p2 = load_json(P2_JSON)
p2_record = {
    "entropies_bits_per_symbol": p2["entropies_bits_per_symbol"],
    "ce_resubstitution": float(p2["cal_resubstitution_bits"]["CE_resubstitution"]),
    "ce_resubstitution_note": p2["cal_resubstitution_bits"].get("note"),
    "fallbacks_support": p2["fallbacks_support"],
    "oracle_checks": p2["oracle_checks"],
    "gates": p2["gates"],
    "method": p2["method"],
}

p0_text = P0_MD.read_text(encoding="utf-8")
p0_d5_ce = re.search(r"CE 3\.814742/3\.347605/([0-9.]+)", p0_text)
p0_record = {
    "cal_lifecycle_session_present": bool("20260123_1M_600k_0dB" in p0_text),
    "cal_lifecycle_line": next((ln.strip() for ln in p0_text.splitlines() if "CAL: `20260123_1M_600k_0dB`" in ln), None),
    "d5_cal_ce_l1_l2_joint": (
        [3.814742, 3.347605, float(p0_d5_ce.group(1))] if p0_d5_ce else None
    ),
}

inv = load_json(V25_INV)
v25_src = [s for s in inv["primary_joint_data_sources"] if s["source_id"] == "type2_1M_20260121_184040"]
if len(v25_src) != 1:
    stop("v25_1m_source_missing", {"found": len(v25_src)})
src = v25_src[0]
v25_record = {
    "source_id": src["source_id"],
    "pairs_parquet": src["pairs_parquet"],
    "parquet_rows": int(src["parquet_rows"]),
    "acquisition_date": src["acquisition"]["date"],
    "bin_width_ps": int(src["bin_width_ps"]),
    "frame_period_ps": int(src["frame_period_ps"]),
    "delay_used_ps": src["delay_used_ps"],
    "pairing_mode": src["pairing_mode"],
    "raw_ser": float(src["raw_ser"]),
    "modular_delta_top": src["modular_delta_top"],
    "joint_counts_sparse_nonzero": int(src["sidecar_artifacts"]["joint_counts_sparse_nonzero"]),
    "joint_counts_sparse_total_count": int(src["sidecar_artifacts"]["joint_counts_sparse_total_count"]),
    "provenance_raw_ttbin": src["provenance_raw_ttbin"],
}

d4m = load_json(D4R2_MANIFEST)
d4r_text = D4R2_REPORT.read_text(encoding="utf-8")


def grab_float(pattern, text):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


d4_record = {
    "session": d4m["session"],
    "cal": d4m["cal"],
    "selected": d4m["selected"],
    "route": d4m["route"],
    "mapping": d4m["mapping"],
    "F_mean_joint": grab_float(r"- F mean_joint `([0-9.]+)`", d4r_text),
    "G_mean_joint": grab_float(r"- G mean_joint `([0-9.]+)`", d4r_text),
    "L_mean_joint": grab_float(r"- L mean_joint `([0-9.]+)`", d4r_text),
}

g1_text = G1_REVIEW.read_text(encoding="utf-8")
g1_record = {
    "candidate_in_sample_ce_sum": grab_float(r"candidate in-sample: CE `[0-9.]+ \+ [0-9.]+ = ([0-9.]+)`", g1_text),
    "candidate_in_sample_mi": grab_float(r"candidate in-sample: .*MI `([0-9.]+)`", g1_text),
    "candidate_truth_mass": grab_float(r"candidate in-sample: .*truth mass `([0-9.]+)`", g1_text),
    "d4_heldout_ce_sum": grab_float(r"D4 held-out: `[0-9.]+ \+ [0-9.]+ = ([0-9.]+)`", g1_text),
}

# ---------------------------------------------------------------- SINGLE artifact content read
if not NPZ_PATH.is_file() or not SUMMARY_PATH.is_file():
    stop("artifact_missing", {"npz": str(NPZ_PATH), "summary": str(SUMMARY_PATH)})
NPZ_BYTES = int(NPZ_PATH.stat().st_size)
SUMMARY_BYTES = int(SUMMARY_PATH.stat().st_size)
open_calls = []


def open_artifact_once():
    open_calls.append(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    return prior_artifact.load_prior_artifact(str(NPZ_PATH), str(SUMMARY_PATH))


artifact = open_artifact_once()
if len(open_calls) != 1:
    stop("second_artifact_open", {"open_calls": list(open_calls)})

counts = np.asarray(artifact.counts_ab)
p_b = np.asarray(artifact.p_b, dtype=np.float64)
summary = dict(artifact.summary)

OPEN_RECORD = {
    "loader": "comparison_bench.formal_ir.nbpolar.prior_artifact.load_prior_artifact",
    "npz_path": str(NPZ_PATH),
    "summary_path": str(SUMMARY_PATH),
    "npz_bytes": NPZ_BYTES,
    "summary_bytes": SUMMARY_BYTES,
    "open_count": len(open_calls),
    "opened_utc": open_calls[0],
    "artifact_content_reads_allowed": 1,
    "artifact_content_reads_consumed": 1,
    "reopen_attempted": False,
    "retry_after_open": False,
    "conditioning": artifact.conditioning.value,
    "provenance": artifact.provenance.value,
    "summary_identity": summary,
    "summary_lambda_star": float(summary.get("lambda_star", float("nan"))),
    "module_lambda_star": LAMBDA_STAR,
    "lambda_star_match": bool(float(summary.get("lambda_star", -1.0)) == LAMBDA_STAR),
    "decoder_calls": 0,
    "rng_calls": 0,
    "tag_calls": 0,
    "construction_calls": 0,
    "sc_decode_calls": 0,
}
checks["artifact_open"] = dict(OPEN_RECORD)

if list(counts.shape) != [N, N] or str(counts.dtype) != "int64":
    stop("artifact_counts_identity", {"shape": list(counts.shape), "dtype": str(counts.dtype)})
counts_sum = int(counts.sum())
if counts_sum != TOTAL_SYMBOLS:
    stop("artifact_counts_sum", {"sum": counts_sum})
p_b_sum = float(p_b.sum())

counts_f = counts.astype(np.float64)
n_b = counts_f.sum(axis=0)
p_b_emp = n_b / float(TOTAL_SYMBOLS)
pb_emp_dev = float(np.abs(p_b - p_b_emp).max())
row_marg = counts_f.sum(axis=1) / float(TOTAL_SYMBOLS)
transpose_sentinel = float(np.abs(p_b - row_marg).max())
zero_cols = int(np.sum(n_b == 0))
rare_cols = int(np.sum(n_b < RARE_NB))
if abs(p_b_sum - 1.0) > TOL_PB:
    stop("p_b_sum", {"sum": p_b_sum, "tol": TOL_PB})
if pb_emp_dev > TOL_PB:
    stop("p_b_vs_counts_marginal", {"max_abs_dev": pb_emp_dev, "tol": TOL_PB})
if zero_cols != 0:
    note("artifact has %d zero-mass Bob columns" % zero_cols)

p_mle = counts_f / n_b[None, :]
mle_col_dev = float(np.abs(p_mle.sum(axis=0) - 1.0).max())

f = prior.smooth_joint_to_conditional(counts, LAMBDA_STAR)
p1_f = prior.derive_p1(f)
p2_f = prior.derive_p2(f)
f3 = f.reshape(Q, Q, N)
f_zero = prior.smooth_joint_to_conditional(counts, 0.0)
lambda_zero_equals_mle_max_abs_diff = float(np.abs(f_zero - p_mle).max())
if lambda_zero_equals_mle_max_abs_diff > TOL_NORM:
    stop("lambda_zero_not_mle", {"max_abs_diff": lambda_zero_equals_mle_max_abs_diff, "tol": TOL_NORM})
f_col_dev = float(np.abs(f.sum(axis=0) - 1.0).max())
p1_col_dev = float(np.abs(p1_f.sum(axis=0) - 1.0).max())
p2_symbol_dev = float(np.abs(p2_f.sum(axis=2) - 1.0).max())
p1_m = prior.derive_p1(p_mle)
p2_m = prior.derive_p2(p_mle)

f_min = float(f.min())
f_max = float(f.max())
f_finite = bool(np.isfinite(f).all())
f_nonneg = bool((f >= 0.0).all())
mle_finite = bool(np.isfinite(p_mle).all())

if max(mle_col_dev, f_col_dev, p1_col_dev, p2_symbol_dev) > TOL_NORM:
    stop("normalization_deviation", {
        "mle_col_dev": mle_col_dev, "f_col_dev": f_col_dev,
        "p1_col_dev": p1_col_dev, "p2_symbol_dev": p2_symbol_dev, "tol": TOL_NORM,
    })

# ---------------------------------------------------------------- frozen quantities (vectorized)
H_mle = float(np.sum(p_b * xlog2x(p_mle).sum(axis=0)))
H1_mle = float(np.sum(p_b * xlog2x(p1_m).sum(axis=0)))
H2_mle = float(np.sum(p_b[None, :] * p1_m * xlog2x(p2_m).sum(axis=2)))
H_f = float(np.sum(p_b * xlog2x(f).sum(axis=0)))
H1_f = float(np.sum(p_b * xlog2x(p1_f).sum(axis=0)))
H2_f = float(np.sum(p_b[None, :] * p1_f * xlog2x(p2_f).sum(axis=2)))
H_lambda_zero = float(np.sum(p_b * xlog2x(f_zero).sum(axis=0)))

logp_f = np.log2(f)
CE_pmle_f = float(-np.sum(p_b * np.sum(p_mle * logp_f, axis=0)))
CE1_pmle_f = float(-np.sum(p_b * np.sum(p1_m * np.log2(p1_f), axis=0)))
CE2_pmle_f = float(-np.sum(p_b[None, :] * p1_m * np.sum(p2_m * np.log2(p2_f), axis=2)))

logp_mle = np.zeros_like(p_mle)
np.log2(p_mle, out=logp_mle, where=p_mle > 0)
f_on_support = np.where(p_mle > 0, f, 0.0)
CE_f_pmle_finite_part = float(-np.sum(p_b * np.sum(f_on_support * logp_mle, axis=0)))
mass_f_outside_mle_support = float(np.sum(p_b * np.sum(np.where(p_mle == 0, f, 0.0), axis=0)))

H_marginal_A = float(-np.sum(xlog2x(counts_f.sum(axis=1) / float(TOTAL_SYMBOLS))))
MI_mle = H_marginal_A - H_mle
MI_f = H_marginal_A - H_f

chain_mle_residual = H1_mle + H2_mle - H_mle
chain_f_residual = H1_f + H2_f - H_f
if max(abs(chain_mle_residual), abs(chain_f_residual)) > TOL_CHAIN:
    stop("chain_residual", {"mle": chain_mle_residual, "fitted": chain_f_residual, "tol": TOL_CHAIN})

for name, val in (("H_mle", H_mle), ("H_f", H_f), ("CE_pmle_f", CE_pmle_f),
                  ("H1_mle", H1_mle), ("H2_mle", H2_mle), ("H1_f", H1_f), ("H2_f", H2_f)):
    if not math.isfinite(val):
        stop("nonfinite_result", {"name": name, "value": str(val)})

# ---------------------------------------------------------------- independent literal implementation
def lit_H_ab(tab, w):
    total = 0.0
    for b in range(N):
        nb = 0.0
        for a in range(N):
            nb += float(tab[a, b])
        h = 0.0
        for a in range(N):
            p = float(tab[a, b]) / nb
            if p > 0.0:
                h -= p * math.log2(p)
        total += float(w[b]) * h
    return total


def lit_H1(tab1, w):
    total = 0.0
    for b in range(N):
        h = 0.0
        for u1 in range(Q):
            p = float(tab1[u1, b])
            if p > 0.0:
                h -= p * math.log2(p)
        total += float(w[b]) * h
    return total


def lit_H2(tab1, tab2, w):
    total = 0.0
    for b in range(N):
        acc = 0.0
        for u1 in range(Q):
            wt = float(tab1[u1, b])
            if wt <= 0.0:
                continue
            h = 0.0
            for u2 in range(Q):
                p = float(tab2[u1, b, u2])
                if p > 0.0:
                    h -= p * math.log2(p)
            acc += wt * h
        total += float(w[b]) * acc
    return total


def lit_CE(src_tab, dst_tab, w):
    total = 0.0
    for b in range(N):
        acc = 0.0
        for a in range(N):
            p = float(src_tab[a, b])
            if p > 0.0:
                acc += p * math.log2(float(dst_tab[a, b]))
        total += float(w[b]) * acc
    return -total


lit_H_mle = lit_H_ab(p_mle, p_b)
lit_H1_mle = lit_H1(p1_m, p_b)
lit_H2_mle = lit_H2(p1_m, p2_m, p_b)
lit_H_f = lit_H_ab(f, p_b)
lit_H1_f = lit_H1(p1_f, p_b)
lit_H2_f = lit_H2(p1_f, p2_f, p_b)
lit_CE_pmle_f = lit_CE(p_mle, f, p_b)
lit_H_lambda_zero = lit_H_ab(f_zero, p_b)

vec_lit = {
    "H_mle_direct": {"vectorized": H_mle, "literal": lit_H_mle},
    "H1_mle": {"vectorized": H1_mle, "literal": lit_H1_mle},
    "H2_mle": {"vectorized": H2_mle, "literal": lit_H2_mle},
    "H_f_direct": {"vectorized": H_f, "literal": lit_H_f},
    "H1_f": {"vectorized": H1_f, "literal": lit_H1_f},
    "H2_f": {"vectorized": H2_f, "literal": lit_H2_f},
    "CE_pmle_to_f": {"vectorized": CE_pmle_f, "literal": lit_CE_pmle_f},
    "H_lambda_zero": {"vectorized": H_lambda_zero, "literal": lit_H_lambda_zero},
}
vec_lit_max_abs_diff = 0.0
for entry in vec_lit.values():
    entry["abs_diff"] = abs(entry["vectorized"] - entry["literal"])
    vec_lit_max_abs_diff = max(vec_lit_max_abs_diff, entry["abs_diff"])
vec_lit["max_abs_diff"] = vec_lit_max_abs_diff
vec_lit["tolerance"] = TOL_LITERAL
vec_lit["pass"] = bool(vec_lit_max_abs_diff <= TOL_LITERAL)
if not vec_lit["pass"]:
    stop("vectorized_literal_disagreement", {"max_abs_diff": vec_lit_max_abs_diff, "tol": TOL_LITERAL})

# ---------------------------------------------------------------- axis / packing controls
pack_bad = []
for s in range(N):
    low, high = prior.split_symbol(s)
    if low != (s & 31) or high != ((s >> 5) & 31) or prior.combine_symbol(low, high) != s:
        pack_bad.append(s)
pack_roundtrip_ok = len(pack_bad) == 0
if not pack_roundtrip_ok:
    stop("packing_roundtrip", {"bad": pack_bad[:8], "count": len(pack_bad)})

layout_max = 0.0
for u1 in range(Q):
    for u2 in range(Q):
        d = float(np.abs(f3[u1, u2, :] - f[32 * u1 + u2, :]).max())
        if d > layout_max:
            layout_max = d

p1_sentinel_diff = 0.0
for b in range(N):
    for u1 in range(Q):
        ssum = 0.0
        for u2 in range(Q):
            ssum += float(f3[u1, u2, b])
        d = abs(ssum - float(p1_f[u1, b]))
        if d > p1_sentinel_diff:
            p1_sentinel_diff = d

p2_sentinel_diff = 0.0
for u1 in (0, 7, 31):
    for b in (0, 255, 777, 1023):
        mass = float(p1_f[u1, b])
        for u2 in range(Q):
            ref = float(f3[u1, u2, b]) / mass
            d = abs(ref - float(p2_f[u1, b, u2]))
            if d > p2_sentinel_diff:
                p2_sentinel_diff = d

alt_marginal = f3.sum(axis=0)  # [j,b]; if packing were A=32*U2+U1 this is the U1' marginal
H1_alt_packing = float(np.sum(p_b * xlog2x(alt_marginal).sum(axis=0)))

counts_T = np.ascontiguousarray(counts_f.T)
n_b_T = counts_T.sum(axis=0)
p_b_T = n_b_T / float(TOTAL_SYMBOLS)
p_T = counts_T / n_b_T[None, :]
H_transpose_own_pb = float(np.sum(p_b_T * xlog2x(p_T).sum(axis=0)))
H_transpose_stored_pb = float(np.sum(p_b * xlog2x(p_T).sum(axis=0)))

axis_controls = {
    "p_b_vs_counts_derived_bob_marginal_max_abs": pb_emp_dev,
    "p_b_vs_counts_derived_bob_marginal_tol": TOL_PB,
    "p_b_sum": p_b_sum,
    "p_b_equals_counts_marginal": bool(pb_emp_dev <= TOL_PB),
    "transpose_sentinel_row_marginal_max_abs": transpose_sentinel,
    "transpose_sentinel_recorded_p2": float(p2["gates"]["transpose_sentinel_diff"]),
    "transpose_sentinel_recorded_match": bool(
        abs(transpose_sentinel - float(p2["gates"]["transpose_sentinel_diff"])) <= TOL_RECORD
    ),
    "H_as_stored_Alice_Bob": H_mle,
    "H_transposed_with_own_p_b": H_transpose_own_pb,
    "H_transposed_with_stored_p_b": H_transpose_stored_pb,
    "H_transposed_own_minus_stored": H_transpose_own_pb - H_mle,
    "packing_roundtrip_ok": pack_roundtrip_ok,
    "packing_checked_symbols": N,
    "mapping_contract": "symbol=low+32*high; high=U1; low=U2 (A=32*U1+U2)",
    "packing_layout_max_abs_diff": layout_max,
    "p1_from_f3_sentinel_max_abs_diff": p1_sentinel_diff,
    "p2_from_f3_sentinel_max_abs_diff": p2_sentinel_diff,
    "alternative_packing_H1": H1_alt_packing,
    "alternative_packing_abs_diff_vs_frozen_H1": abs(H1_alt_packing - H1_f),
    "mle_column_sum_max_abs_dev": mle_col_dev,
    "f_column_sum_max_abs_dev": f_col_dev,
    "p1_column_sum_max_abs_dev": p1_col_dev,
    "p2_symbol_sum_max_abs_dev": p2_symbol_dev,
    "normalization_tol": TOL_NORM,
    "zero_mass_bob_columns": zero_cols,
    "rare_bob_columns_below_%d" % RARE_NB: rare_cols,
    "mle_finite": mle_finite,
    "f_finite": f_finite,
    "f_nonnegative": f_nonneg,
    "f_min": f_min,
    "f_max": f_max,
    "x06_recorded_f_column_dev_max": float(x06_open["table_checks"]["f_column_dev_max"]),
    "x06_recorded_p1_column_dev_max": float(x06_open["table_checks"]["p1_column_dev_max"]),
    "x06_recorded_p2_symbol_dev_max": float(x06_open["table_checks"]["p2_symbol_dev_max"]),
    "x06_recorded_f_min": float(x06_open["table_checks"]["f_min"]),
    "x06_recorded_f_max": float(x06_open["table_checks"]["f_max"]),
    "x06_recorded_counts_sum": int(x06_open["table_checks"]["counts_sum"]),
    "recomputed_counts_sum": counts_sum,
}
if max(layout_max, p1_sentinel_diff, p2_sentinel_diff) > TOL_NORM:
    stop("axis_layout_disagreement", {
        "layout_max": layout_max, "p1_sentinel_diff": p1_sentinel_diff,
        "p2_sentinel_diff": p2_sentinel_diff, "tol": TOL_NORM,
    })

# ---------------------------------------------------------------- delta-support aggregates
delta_counts = np.zeros(N, dtype=np.float64)
for a in range(N):
    delta_counts += np.roll(counts_f[a], -a)
delta_frac = delta_counts / float(TOTAL_SYMBOLS)
top_delta = sorted(
    ({"delta": int(k), "count": int(delta_counts[k]), "fraction": float(delta_frac[k])}
     for k in range(N) if delta_counts[k] > 0),
    key=lambda d: (-d["count"], d["delta"]),
)[:5]
diag_frac = float(counts_f.trace() / float(TOTAL_SYMBOLS))
nonzero_cells = int(np.count_nonzero(counts))
support_aggregates = {
    "nonzero_count_cells": nonzero_cells,
    "cell_occupancy_fraction": nonzero_cells / float(N * N),
    "P_A_equals_B": diag_frac,
    "ser": 1.0 - diag_frac,
    "top_modular_delta_b_minus_a": top_delta,
    "v49_1m_raw_ser_recorded": float(v25_record["raw_ser"]),
    "v49_1m_delta_top_recorded": v25_record["modular_delta_top"],
    "v49_1m_nonzero_joint_cells_recorded": int(v25_record["joint_counts_sparse_nonzero"]),
}

# ---------------------------------------------------------------- smoothing diagnostics
w_backoff = LAMBDA_STAR / (n_b + LAMBDA_STAR)
n_b_quantiles = np.quantile(n_b, [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0])
w_quantiles = np.quantile(w_backoff, [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0])
w_quantile_labels = ["0.00", "0.10", "0.25", "0.50", "0.75", "0.90", "1.00"]
w_pb_weighted_quantiles = weighted_quantile(w_backoff, p_b, [0.1, 0.25, 0.5, 0.75, 0.9])
w_pb_mean = float(np.sum(p_b * w_backoff))

w_max_v49 = LAMBDA_STAR / (V49_MIN_NB_1M + LAMBDA_STAR)
h2b = lambda x: -(x * math.log2(x) + (1.0 - x) * math.log2(1.0 - x))
v49_smoothing_upper_bound = h2b(w_max_v49) + v49_csv["nll_total"] + w_max_v49 * LOG2N
required_global_entropy_for_x06_scale = (H_f - h2b(w_max_v49) - v49_csv["nll_total"]) / w_max_v49

smoothing_diagnostics = {
    "lambda_star": LAMBDA_STAR,
    "lambda_zero_semantics": "smooth_joint_to_conditional(counts, 0.0) equals column-normalized raw counts (item 1 MLE) when all n_b>0",
    "n_b_quantiles": {lab: float(v) for lab, v in zip(w_quantile_labels, n_b_quantiles)},
    "n_b_mean": float(n_b.mean()),
    "n_b_sum": float(n_b.sum()),
    "zero_mass_columns": zero_cols,
    "nonzero_columns": int(np.sum(n_b > 0)),
    "columns_below_%d" % RARE_NB: rare_cols,
    "backoff_weight_lambda_over_nb_plus_lambda_quantiles": {lab: float(v) for lab, v in zip(w_quantile_labels, w_quantiles)},
    "backoff_weight_pb_weighted_quantiles": w_pb_weighted_quantiles,
    "backoff_weight_pb_weighted_mean": w_pb_mean,
    "backoff_weight_unweighted_mean": float(w_backoff.mean()),
    "H_mle": H_mle,
    "H_f": H_f,
    "H_increase_from_smoothing": H_f - H_mle,
    "CE_pmle_to_f": CE_pmle_f,
    "CE_pmle_to_f_minus_H_mle": CE_pmle_f - H_mle,
    "v49_min_n_b_recorded": V49_MIN_NB_1M,
    "v49_w_max": w_max_v49,
    "v49_smoothing_upper_bound_bits": v49_smoothing_upper_bound,
    "v49_smoothing_bound_terms": {
        "h2_w_max": h2b(w_max_v49),
        "v49_nll_total": v49_csv["nll_total"],
        "w_max_times_log2N": w_max_v49 * LOG2N,
        "assumption": "V49 1M TRAIN per-column n_b >= 210 and H(p_global) <= log2(1024); sum p_b H(mle_b) = V49 H(A|B) = nll_total",
    },
    "global_entropy_needed_to_reach_x06_scale_with_w_max": required_global_entropy_for_x06_scale,
    "log2_N": LOG2N,
    "shrinkage_can_explain_v49_to_x06": bool(v49_smoothing_upper_bound >= H_f),
}

# ---------------------------------------------------------------- V49 / X06 comparisons
x06_table_total = float(x06_ent["h1_bits"]) + float(x06_ent["h2_bits"])
x06_genie_total = l1_mean + l2_mean
v49_comparisons = {
    "v49_1M_TRAIN_nll_total": v49_csv["nll_total"],
    "v49_1M_TRAIN_nll_u1": v49_csv["nll_u1"],
    "v49_1M_TRAIN_nll_u2": v49_csv["nll_u2"],
    "v49_1M_TRAIN_H_u1_given_b": v49_csv["ent_u1_given_b"],
    "v49_1M_TRAIN_kl_sample": v49_csv["kl_sample"],
    "v49_functional_note": (
        "V49 nll_total is the pair-mean NLL of the true symbol under the TRAIN-only MLE prior "
        "(= cross-entropy of the empirical TRAIN distribution under its own MLE table); for the "
        "TRAIN pool kl_sample ~ 0, so it equals the plug-in conditional entropy H(A|B) of that "
        "population. V49 u1/u2 split follows (A>>5, A&31) with floor 1e-15 + renorm."
    ),
    "differences_vs_computed": {
        "v49_minus_artifact_raw_mle_H": v49_csv["nll_total"] - H_mle,
        "v49_minus_artifact_smoothed_H": v49_csv["nll_total"] - H_f,
        "v49_minus_artifact_CE_pmle_to_f": v49_csv["nll_total"] - CE_pmle_f,
        "v49_minus_x06_table_total": v49_csv["nll_total"] - x06_table_total,
        "v49_minus_x06_genie_total": v49_csv["nll_total"] - x06_genie_total,
        "artifact_raw_mle_H_minus_x06_genie_total": H_mle - x06_genie_total,
        "artifact_smoothed_H_minus_x06_genie_total": H_f - x06_genie_total,
    },
    "x06_table_total": x06_table_total,
    "x06_genie_total": x06_genie_total,
    "x06_recorded_h1_bits": float(x06_ent["h1_bits"]),
    "x06_recorded_h2_bits": float(x06_ent["h2_bits"]),
    "x06_genie_l1_mean": l1_mean,
    "x06_genie_l2_mean": l2_mean,
    "x06_assignment_quoted_total": 7.61,
    "x06_quoted_note": (
        "No X06 record equals 7.61. X06's recorded table-based total is h1_bits+h2_bits and its "
        "genie-NLL mean total is (l1_mean+l2_mean); the assignment's ~7.61 is an approximation of "
        "that scale, not a separately stored X06 quantity."
    ),
}
if abs(H1_f - float(x06_ent["h1_bits"])) > TOL_RECORD or abs(H2_f - float(x06_ent["h2_bits"])) > TOL_RECORD:
    stop("x06_table_mismatch", {
        "H1_f": H1_f, "x06_h1": float(x06_ent["h1_bits"]),
        "H2_f": H2_f, "x06_h2": float(x06_ent["h2_bits"]), "tol": TOL_RECORD,
    })

x06_sampling_law = {
    "law": "B ~ p_b (artifact Bob marginal = counts axis-1 marginal over Bob), then A | B ~ f(.,B) = smooth_joint_to_conditional(counts, LAMBDA_STAR)",
    "source": "X06 prereg config.sampler empirical_channel.sample_full_block(rng, p_b, f, 32, 32, 256); high=Alice//32, low=Alice%32",
    "algebraic_identity": (
        "E_{B~p_b} E_{U1|B}[-log2 p1_f(U1|B)] = sum_b p_b H(p1_f(.,b)) = H1_f; "
        "E_{B,U1,U2}[-log2 p2_f(U2|U1,B)] = sum_b p_b sum_u1 p1_f H(p2_f(u1,b,.)) = H2_f; "
        "hence the expected X06 layer conditional entropies equal the accepted smoothed-model "
        "entropies under p_b (item 2). X06's recorded entropy.h1_bits/h2_bits are computed from "
        "exactly those p1/p2 tables (X06 prereg lines 648-651), so they are the same functional."
    ),
    "expected_H1_f": H1_f,
    "expected_H2_f": H2_f,
    "expected_total": H1_f + H2_f,
    "x06_recorded_table_H1": float(x06_ent["h1_bits"]),
    "x06_recorded_table_H2": float(x06_ent["h2_bits"]),
    "abs_diff_H1": abs(H1_f - float(x06_ent["h1_bits"])),
    "abs_diff_H2": abs(H2_f - float(x06_ent["h2_bits"])),
    "comparison_basis_note": (
        "The genie means below are a DIFFERENT functional: per-coordinate NLL means over 768 pooled "
        "TRAIN blocks in the polar-transformed domain after full-true disclosure "
        "(construction.genie_conditionals -> sc_decode with all positions known). They are compared "
        "descriptively with an across-coordinate dispersion SE; coordinates are not independent."
    ),
    "x06_genie_l1_mean": l1_mean,
    "x06_genie_l2_mean": l2_mean,
    "x06_genie_total": x06_genie_total,
    "x06_genie_l1_se_approx": x06_record["genie_l1_se_of_mean_approx"],
    "x06_genie_l2_se_approx": x06_record["genie_l2_se_of_mean_approx"],
    "genie_l1_minus_H1_f": l1_mean - H1_f,
    "genie_l2_minus_H2_f": l2_mean - H2_f,
    "genie_total_minus_H_f": x06_genie_total - (H1_f + H2_f),
}

provenance_table = [
    {
        "row_id": "v49_1M_TRAIN_nll_total_ce",
        "value_bits_per_symbol": v49_csv["nll_total"],
        "source_population": "session type2_1M_20260121_184040, TRAIN frames 0..1199, 307200 pairs (V25 channel_counts.npz TRAIN-only)",
        "conditional_table": "TRAIN-only MLE P(U1|B), P(U2|U1,B) from joint counts, floor 1e-15 + renorm",
        "bob_weights": "TRAIN pool empirical Bob frequency",
        "smoothing": "floor 1e-15 only (no concentration/backoff)",
        "functional_type": "cross-entropy of true symbols under the TRAIN MLE prior (= NLL_total; plug-in conditional entropy of the TRAIN population)",
        "recorded_source": "docs/v49_distribution_tables/v49_train_val_hold_nll.csv row 1M/TRAIN",
    },
    {
        "row_id": "v49_1M_TRAIN_H_u1_given_b",
        "value_bits_per_symbol": v49_csv["ent_u1_given_b"],
        "source_population": "same V49 1M TRAIN",
        "conditional_table": "same TRAIN MLE P(U1|B)",
        "bob_weights": "TRAIN pool empirical Bob frequency",
        "smoothing": "floor 1e-15 only",
        "functional_type": "entropy H(U1|B) of the TRAIN MLE table",
        "recorded_source": "same CSV row",
    },
    {
        "row_id": "v49_1M_TRAIN_nll_u2",
        "value_bits_per_symbol": v49_csv["nll_u2"],
        "source_population": "same V49 1M TRAIN",
        "conditional_table": "same TRAIN MLE P(U2|U1,B)",
        "bob_weights": "TRAIN pool empirical Bob frequency",
        "smoothing": "floor 1e-15 only",
        "functional_type": "cross-entropy NLL_U2 of true U2 under P(U2|U1,B)",
        "recorded_source": "same CSV row",
    },
    {
        "row_id": "artifact_raw_mle_H_A_given_B",
        "value_bits_per_symbol": H_mle,
        "source_population": "session 20260123_1M_600k_0dB, CAL frames 702..1725, 262144 symbols (accepted Model-F artifact counts_ab)",
        "conditional_table": "column-normalized raw counts P_mle(A|B)",
        "bob_weights": "artifact p_b (validated equal to counts-derived Bob marginal within 1e-12)",
        "smoothing": "none",
        "functional_type": "plug-in conditional entropy H(A|B) of the counts",
        "recorded_source": "computed (vectorized + literal); artifact-open 1/1",
    },
    {
        "row_id": "artifact_raw_mle_H1",
        "value_bits_per_symbol": H1_mle,
        "source_population": "same artifact counts",
        "conditional_table": "p1_m = derive_p1(P_mle) [U1,B]",
        "bob_weights": "artifact p_b",
        "smoothing": "none",
        "functional_type": "entropy H(U1|B)",
        "recorded_source": "computed",
    },
    {
        "row_id": "artifact_raw_mle_H2",
        "value_bits_per_symbol": H2_mle,
        "source_population": "same artifact counts",
        "conditional_table": "p2_m = derive_p2(P_mle) [U1,B,U2]",
        "bob_weights": "artifact p_b",
        "smoothing": "none",
        "functional_type": "entropy H(U2|U1,B)",
        "recorded_source": "computed",
    },
    {
        "row_id": "artifact_smoothed_H_A_given_B",
        "value_bits_per_symbol": H_f,
        "source_population": "same artifact counts",
        "conditional_table": "f = smooth_joint_to_conditional(counts, LAMBDA_STAR) [A,B]",
        "bob_weights": "artifact p_b",
        "smoothing": "accepted concentration/backoff LAMBDA_STAR=137.3823795883264 (per-column weight lambda/(n_b+lambda))",
        "functional_type": "entropy of the accepted smoothed model under p_b",
        "recorded_source": "computed; must reproduce X06 h1+h2 and P2 H_chain within 1e-9",
    },
    {
        "row_id": "artifact_smoothed_H1",
        "value_bits_per_symbol": H1_f,
        "source_population": "same artifact counts",
        "conditional_table": "p1_f = derive_p1(f) [U1,B]",
        "bob_weights": "artifact p_b",
        "smoothing": "accepted LAMBDA_STAR",
        "functional_type": "entropy H(U1|B) of the smoothed model",
        "recorded_source": "computed; X06 entropy.h1_bits = 4.286720430201375",
    },
    {
        "row_id": "artifact_smoothed_H2",
        "value_bits_per_symbol": H2_f,
        "source_population": "same artifact counts",
        "conditional_table": "p2_f = derive_p2(f) [U1,B,U2]",
        "bob_weights": "artifact p_b",
        "smoothing": "accepted LAMBDA_STAR",
        "functional_type": "entropy H(U2|U1,B) of the smoothed model",
        "recorded_source": "computed; X06 entropy.h2_bits = 3.222719884634378",
    },
    {
        "row_id": "artifact_CE_pmle_to_f",
        "value_bits_per_symbol": CE_pmle_f,
        "source_population": "same artifact counts",
        "conditional_table": "source p_mle, evaluated under smoothed f",
        "bob_weights": "artifact p_b",
        "smoothing": "accepted LAMBDA_STAR",
        "functional_type": "cross-entropy of raw counts under the smoothed model (CE1+CE2 = %.15f + %.15f)" % (CE1_pmle_f, CE2_pmle_f),
        "recorded_source": "computed; compare P2 CE_resubstitution=5.5985039618345835 and G1 candidate in-sample sum=7.5094403148357545",
    },
    {
        "row_id": "artifact_CE_f_to_pmle",
        "value_bits_per_symbol": None,
        "source_population": "same artifact counts",
        "conditional_table": "source f, evaluated under MLE p_mle",
        "bob_weights": "artifact p_b",
        "smoothing": "accepted LAMBDA_STAR",
        "functional_type": "cross-entropy is +inf (f has positive mass on cells with zero MLE support); finite part over MLE support and out-of-support mass reported separately",
        "recorded_source": "computed",
    },
    {
        "row_id": "x06_sampled_law_expected_H",
        "value_bits_per_symbol": H1_f + H2_f,
        "source_population": "X06 synthetic TRAIN/DEV sampling law: B~p_b, A~f(.,B) from the same artifact table",
        "conditional_table": "f (accepted smoothed table)",
        "bob_weights": "artifact p_b",
        "smoothing": "accepted LAMBDA_STAR (source of the sampled law)",
        "functional_type": "expected layer conditional entropies of the sampling model = smoothed-model entropies under p_b",
        "recorded_source": "algebraic identity; X06 recorded h1_bits+h2_bits",
    },
    {
        "row_id": "x06_recorded_genie_nll_means",
        "value_bits_per_symbol": x06_genie_total,
        "source_population": "X06 pooled TRAIN genie statistics, 768 blocks/3 streams, polar-transformed domain, full-true disclosure",
        "conditional_table": "p1_f/p2_f metrics conditioned per coordinate with all previous coordinates disclosed true",
        "bob_weights": "artifact p_b",
        "smoothing": "accepted LAMBDA_STAR",
        "functional_type": "empirical NLL means (sampling estimate), NOT a table entropy",
        "recorded_source": "X06 results.json train.pooled.l1/l2.h_summary.mean",
    },
    {
        "row_id": "d4r2_d5_heldout_CE_joint",
        "value_bits_per_symbol": d4_record["F_mean_joint"],
        "source_population": "same 0dB session, nested-CV held-out outer folds (702..1725 partitioned)",
        "conditional_table": "F model (same smooth_joint_to_conditional family) fitted on training folds",
        "bob_weights": "model p_b",
        "smoothing": "accepted LAMBDA_STAR fitted per training fold",
        "functional_type": "held-out cross-entropy (nested CV), not in-sample entropy",
        "recorded_source": "D4R2 report F mean_joint; P0 contract cites D5 CE joint",
    },
]

quantities = {
    "artifact": {
        "raw_mle": {
            "H_A_given_B": H_mle,
            "H1_U1_given_B": H1_mle,
            "H2_U2_given_U1_B": H2_mle,
            "chain_residual": chain_mle_residual,
            "CE_pmle_to_pmle_equals_H": True,
        },
        "smoothed_accepted": {
            "H_A_given_B": H_f,
            "H1_U1_given_B": H1_f,
            "H2_U2_given_U1_B": H2_f,
            "chain_residual": chain_f_residual,
            "CE_pmle_to_f": CE_pmle_f,
            "CE_pmle_to_f_chain_terms": {"CE1": CE1_pmle_f, "CE2": CE2_pmle_f, "sum": CE1_pmle_f + CE2_pmle_f},
            "CE_f_to_pmle": {
                "unbounded": bool(mass_f_outside_mle_support > 0.0),
                "value": None,
                "label": "+inf (positive f mass on zero MLE support)" if mass_f_outside_mle_support > 0 else "finite",
                "finite_part_over_mle_support": CE_f_pmle_finite_part,
                "mass_f_outside_mle_support": mass_f_outside_mle_support,
            },
        },
        "lambda_zero_recompute": {
            "label": "diagnostic attribution only: lambda=0 reproduces the item 1 raw MLE table; no lambda scan or tuning",
            "smooth_joint_to_conditional_zero_vs_p_mle_max_abs_diff": lambda_zero_equals_mle_max_abs_diff,
            "H_A_given_B": H_lambda_zero,
            "CE_pmle_to_model": H_lambda_zero,
            "equals_raw_mle_H": bool(abs(H_lambda_zero - H_mle) <= TOL_LITERAL),
        },
        "marginals": {
            "H_Alice_marginal": H_marginal_A,
            "MI_raw_mle": MI_mle,
            "MI_smoothed": MI_f,
            "recorded_candidate_in_sample_MI": g1_record["candidate_in_sample_mi"],
        },
    },
    "v49": v49_csv,
    "x06": x06_record,
    "p2": p2_record,
    "p0": p0_record,
    "v25": v25_record,
    "d4r2": d4_record,
    "g1": g1_record,
}

earliest_contract_divergence = {
    "established": True,
    "divergence_id": "POPULATION_SESSION_IDENTITY_1M",
    "first_divergent_stage": (
        "accepted Model-F artifact CAL population (session 20260123_1M_600k_0dB, frames 702..1725) "
        "vs the V49 1M TRAIN population (session type2_1M_20260121_184040, frames 0..1199)"
    ),
    "explanation": (
        "The accepted artifact counts_ab is built from the 20260123_1M_600k_0dB acquisition "
        "(P0 contract section 5; prepare registry check), whose accepted/recorded model scale is "
        "CE ~= 7.15-7.51 bits/symbol. The V49 CSV 1M TRAIN row is built from the 2026-01-21 "
        "type2_1M acquisition (V25 channel_counts.npz TRAIN-only; V25 inventory raw_ser 0.2398, "
        "delta support {0:0.760, 1:0.238}), whose plug-in conditional entropy is 0.801 bits/symbol. "
        "X06 sampled B~p_b, A~f from the artifact, so its expected layer entropies are the artifact's "
        "smoothed-model entropies (7.50944), not the V49 value. The X06 all-zero recovery point "
        "(0/640 pooled exact at K=45..140) was produced on the artifact-sampled channel."
    ),
    "not_the_cause": [
        "axis/transpose: stored [Alice,Bob] is consistent; p_b equals the counts-derived Bob marginal (dev <= 1e-12); transpose sentinel reproduces the recorded 2.098e-4",
        "packing: exhaustive split/combine round trip passes; derive_p1/derive_p2 match literal f3 layout to <= 1e-12",
        "Bob weights: both sides use empirical Bob marginals of their own populations",
        "column normalization: deviations <= 1e-12; zero/rare columns reported",
        "smoothing: the accepted LAMBDA_STAR backoff can move the artifact's own in-sample entropy by %.4f bits and cannot by itself lift a 0.801-bit V49 channel to the 7.51-bit X06 scale (bound argument below)" % (H_f - H_mle),
    ],
    "supporting_evidence": [
        "P0 contract section 5 CAL lifecycle: 20260123_1M_600k_0dB, frames 702..1725, 262144 symbols",
        "prepare registry check: session must be 20260123_1M_600k_0dB; CAL ids 702..1725; parquet columns [frame_id,pair_idx,alice_symbol,bob_symbol]",
        "V49 report/CSV: 1M = type2_1M_20260121_184040, TRAIN 0..1199, n=307200, NLL_total=0.8010378248977232",
        "V25 data inventory: source_id type2_1M_20260121_184040, raw_ser=0.23977303568674083, modular_delta_top {0:0.7602, 1:0.2384}, 2545 nonzero joint cells",
        "D4R2 manifest session 20260123_1M_600k_0dB; report F mean_joint 7.162347, G mean_joint 9.999677",
        "P2 CAL summary: H_chain=7.509440314835754 for the artifact; CE_resubstitution=5.5985039618345835",
        "G1 review: candidate in-sample CE sum 7.5094403148357545, MI 2.48306874956704",
    ],
    "reported_values": {
        "v49_1M_TRAIN_nll_total": v49_csv["nll_total"],
        "artifact_raw_mle_H": H_mle,
        "artifact_smoothed_H": H_f,
        "artifact_CE_pmle_to_f": CE_pmle_f,
        "x06_table_total": x06_table_total,
        "x06_genie_total": x06_genie_total,
        "d4r2_heldout_CE_joint": d4_record["F_mean_joint"],
    },
    "claim_boundary": (
        "This is a descriptive provenance finding. It does not select an estimator, does not claim "
        "a channel or reconciliation performance, and does not modify any accepted artifact."
    ),
}

# ---------------------------------------------------------------- results assembly
wall_s = time.monotonic() - T0
rss = rss_bytes_peak()
if not math.isfinite(wall_s):
    stop("nonfinite_wall", {"wall_s": wall_s})

results = {
    "probe_id": "nbpolar_x07_entropy_contract_reconciliation",
    "tier": "X",
    "status": "X07_PROBE_COMPLETE_DESCRIPTIVE_ONLY",
    "title": "Entropy-contract reconciliation: V49 1M TRAIN vs accepted Model-F/X06 vs raw-MLE provenance",
    "prereg_sha256": prereg_sha256,
    "body_sha256": body_sha256,
    "body_sha_match": body_sha_match,
    "artifact_open": OPEN_RECORD,
    "inputs": inputs,
    "v49_record": {
        "csv_row": v49_csv,
        "doc_row": v49_doc,
        "doc_vs_csv_max_abs_diff": v49_doc_csv_max,
        "doc_vs_csv_tolerance": TOL_RECORD,
        "doc_vs_csv_match": bool(v49_doc_csv_max <= TOL_RECORD),
    },
    "x06_record": x06_record,
    "p2_record": p2_record,
    "p0_record": p0_record,
    "v25_record": v25_record,
    "d4r2_record": d4_record,
    "g1_record": g1_record,
    "quantities": quantities,
    "provenance_table": provenance_table,
    "vectorized_vs_literal": vec_lit,
    "chain": {
        "H_mle_chain_residual": chain_mle_residual,
        "H_f_chain_residual": chain_f_residual,
        "tolerance": TOL_CHAIN,
        "pass": bool(max(abs(chain_mle_residual), abs(chain_f_residual)) <= TOL_CHAIN),
    },
    "axis_packing_controls": axis_controls,
    "support_aggregates": support_aggregates,
    "smoothing_diagnostics": smoothing_diagnostics,
    "v49_comparisons": v49_comparisons,
    "x06_sampling_law": x06_sampling_law,
    "earliest_contract_divergence": earliest_contract_divergence,
    "resource": {
        "wall_s": wall_s,
        "rss_bytes_peak": rss["peak_bytes"],
        "rss_bytes_peak_rusage": rss["ru_maxrss_bytes"],
        "rss_bytes_peak_vmhwm": rss["vmhwm_bytes"],
    },
    "commands": commands_log,
    "notes": NOTES + [
        "Tier-X non-claim probe: no threshold, pass/fail science verdict, winner, candidate/accepted token or qualification conclusion.",
        "Exactly one Model-F artifact content read (open_count=1); no reopen, no retry after the content read; no sibling artifact or raw data read.",
        "No decoder, RNG, tag, construction or sc_decode call was made; no lambda scan or tuning; no production/OpenSpec behavior edit; no commit/push; no ledger/memory/index update.",
        "Only aggregates and quantiles are persisted: no 1024x1024 table, raw counts, samples or private vectors.",
        "Writing scope: workspace/probes/nbpolar_x07_entropy_contract_reconciliation/{prereg.md,results.json} plus /tmp staging of the frozen body.",
    ],
}

STDOUT.append("X07 artifact open 1/1 at %s" % OPEN_RECORD["opened_utc"])
STDOUT.append("H_mle=%.15f H1_mle=%.15f H2_mle=%.15f chain_res=%.3e" % (H_mle, H1_mle, H2_mle, chain_mle_residual))
STDOUT.append("H_f=%.15f H1_f=%.15f H2_f=%.15f chain_res=%.3e" % (H_f, H1_f, H2_f, chain_f_residual))
STDOUT.append("CE_pmle_to_f=%.15f" % CE_pmle_f)
STDOUT.append("vec_lit_max_abs_diff=%.3e tol=%.1e" % (vec_lit_max_abs_diff, TOL_LITERAL))
STDOUT.append("body_sha256=%s match=%s" % (body_sha256, body_sha_match))
STDOUT.append("results_path=%s" % RESULTS_PATH)
commands_log[0]["stdout_lines"] = list(STDOUT)
for line in STDOUT:
    print(line)

RESULTS_PATH.write_text(json.dumps(results, indent=1, sort_keys=False) + "\n", encoding="utf-8")
```

End of frozen X07 prereg. The body's sha256, the prereg sha256 and the byte-equality
check are recorded in `results.json` (`body_sha256`, `prereg_sha256`,
`body_sha_match`); the root is preserved on any STOP. No committed ledger/memory
update and no production/OpenSpec edit is part of this probe.
