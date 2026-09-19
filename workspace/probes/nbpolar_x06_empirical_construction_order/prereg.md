# X06 preregistration — empirical construction-order discriminator (Tier-X probe)

Probe root: `workspace/probes/nbpolar_x06_empirical_construction_order/`.
Tier: X (non-claim) under `AGENTS.md` section 10.4. This file — including the
complete executable body below — is frozen before the single accepted
artifact-content open. The probe root will contain exactly `prereg.md` and
`results.json`; no other file is written there.

## 1. Question

Using the accepted CAL Model-F distribution, do empirical genie construction
orders for L1 and oracle-conditioned L2 differ materially and stably from the
BEC analytic order, and do those orders change held-out model-sampled SC
recovery at the same disclosure sizes? Exploratory: no threshold, winner,
candidate/accepted label or qualification conclusion.

## 2. Frozen input and access accounting

- Read these sibling-checkout files exactly once into memory through the accepted
  `prior_artifact.load_prior_artifact` path:
  - `/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz`
  - `/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input_summary.json`
- The allowance is one artifact-content read (1/1), consumed at the first
  content open even if later work fails. No other artifact, raw parquet, TTBin,
  real-frame file, sibling write or earlier evidence-root write is permitted.
- Conditional table derivation only by the accepted path:
  `f = prior.smooth_joint_to_conditional(artifact.counts_ab, prior_artifact.LAMBDA_STAR)`,
  `p1 = prior.derive_p1(f)` `[U1,B] (32,1024)`,
  `p2 = prior.derive_p2(f)` `[U1,B,U2] (32,1024,32)`,
  `p_b = artifact.p_b` (stored axis-0 marginal, loader-validated).
- All arrays stay in memory in the same process for all streams; the open is
  never repeated and a second open is refused by a body guard.
- Recorded loader identity:
  `comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior_artifact.load_prior_artifact`.

## 3. Frozen experiment

- GF32, polynomial basis, primitive polynomial 37, alpha 2, natural SC order,
  N=256, q=32.
- Model sampling (accepted public source `empirical_channel`):
  `rng = empirical_channel.make_rng(stream)`;
  `bob, a_full, high, low = empirical_channel.sample_full_block(rng, p_b, f, 32, 32, 256)`.
  Frozen draw order per block: Bob labels first (`rng.random(256)` against the
  cumulative `p_b`), then Alice labels (`rng.random(256)`; per coordinate the
  cumulative column `f[:, bob_j]`); blocks in increasing index. `high = a_full // 32`,
  `low = a_full % 32`.
- TRAIN construction streams `2026091600, 2026091601, 2026091602`, 256 blocks
  each. DEV evaluation streams `2026091610..2026091614`, 128 blocks each.
  Streams are disjoint and probe-only; no EVAL stream exists.
- Metrics: L1 = `prior.build_p1_metrics(bob[None, :], p1)[0]` then
  `prior.probs_to_symbol_metric(..., PRIOR_ONLY)`; oracle-L2 =
  `prior.gather_p2_metrics(bob[None, :], high[None, :], p2)[0]` then
  `prior.probs_to_symbol_metric(..., ORACLE_CONDITIONED)`. (The 2D `[None, :]`
  call convention is the accepted X03 usage of these functions.)
- TRAIN accumulation per layer per stream: `construction.genie_conditionals`
  full-true semantics; `h_k += -log2 p(u_true)`, `e_k += 1 - max p`, exactly the
  accepted `build_construction` accumulation. `ImpossibleDisclosedValueError`
  blocks are counted and skipped; other exceptions stop the probe.
- Orders: `construction.disclosure_order_from_stats(e, h)` (worst-first
  descending `(e, h)`, ties by index). One pooled TRAIN order per layer from the
  pooled sufficient statistics: sums of all per-block `e`/`h` over the three
  TRAIN streams divided by the pooled used-block count (never selected after
  DEV).
- Order freeze: all five orders per layer are frozen and hashed
  (`orders_sha256`, canonical JSON) before the first DEV call; the hash is
  recomputed after DEV and must be unchanged.
- BEC analytic controls (surrogate only): `epsilon_l = H_l / log2(32)` with
  - `H1 = E_B[H(U1|B)] = -sum_b p_b[b] sum_u1 p1[u1,b] log2 p1[u1,b]`,
  - `H2 = E_{B,U1}[H(U2|U1,B)] = -sum_b p_b[b] sum_u1 p1[u1,b] sum_u2 p2[u1,b,u2] log2 p2[u1,b,u2]`,
  per-coordinate symbol-domain conditional entropies in bits from the same
  smoothed table; `construction.analytic_order(epsilon_l, 256)` gives the
  worst-first BEC order. This is a surrogate construction order only, not a
  channel claim about the model-sampled channel.

## 4. Frozen comparisons and DEV protocol

- Statistics per layer over the order set
  `{train_2026091600, train_2026091601, train_2026091602, pooled_empirical, bec}`:
  all 10 pairwise Spearman correlations of coordinate position ranks, and
  top-K overlaps at L1 K=`45,60,72,112` and L2 K=`140` (for every pair, so the
  pooled-empirical-vs-BEC rows are included); pooled/per-stream empirical risk
  vs BEC `z` Spearman; coordinate risk/entropy summaries; complete 256-coordinate
  permutations for all orders.
- DEV, per sampled block shared by all rows: fresh-restart `sc_decode` for each
  (order, K): L1 SC at K=`45,60,72,112` for `{pooled_empirical, bec}`; oracle-L2
  SC at K=`140` for `{pooled_empirical, bec}`. Disclosed positions are
  `order[:K]`, disclosed values are that layer's truth at those positions.
- `exact` = `u_hat == u_true` and `x_hat == x_true` (layer source word /
  layer symbol truth). `initial_error` = accepted pointwise pre-SC semantics
  (`argmax(metric log-rows) != layer symbol truth` in at least one symbol).
  Failure class: `exact` / `mismatch` / `decode_failed` / `nonfinite`
  (`NumericNonfiniteError` or non-finite decision metrics); non-`ValueError`
  exceptions from the decoder stop the probe.
- Persist per-block scalars only: stream, block, layer, order id, K, exact flag,
  initial-error flag, failure class. No source/Bob/U/decoded/disclosed vectors or
  metric arrays. `undetected` is not applicable without a tag; it is neither
  invented nor merged into `exact`.
- Report per-stream and pooled exact/mismatch/decode_failed/nonfinite counts and
  paired four-cell tables (`both_exact`, `empirical_only`, `bec_only`, `neither`)
  for `pooled_empirical` vs `bec`.

## 5. Output schema (results.json)

```json
{
  "probe_id": "nbpolar_x06_empirical_construction_order",
  "tier": "X-non-claim",
  "status": "completed",
  "prereg_sha256": "...", "body_sha256": "...", "body_sha_match": true,
  "interpreter": {"executable": "...", "python_version": "...", "numpy_version": "..."},
  "command": {"text": "...", "staged_body_path": "/tmp/x06_body.log", "cwd": "..."},
  "artifact_open": {"loader": "...", "npz_path": "...", "summary_path": "...",
                     "artifact_content_reads_allowed": 1,
                     "artifact_content_reads_consumed": 1, "open_count": 1,
                     "open_completed_utc": "...", "lambda_star": 137.3823795883264,
                     "summary_identity": {...}, "derivation": {...},
                     "table_checks": {...}},
  "config": {"q": 32, "primitive_polynomial": 37, "alpha": 2, "n": 256,
             "train_streams": [2026091600, 2026091601, 2026091602],
             "dev_streams": [2026091610, 2026091611, 2026091612, 2026091613, 2026091614],
             "l1_ks": [45, 60, 72, 112], "l2_ks": [140], "sampler": "...",
             "metrics": {...}, "orders": "...", "bec": {...}, "limits": {...}},
  "entropy": {"h1_bits": 0.0, "h2_bits": 0.0, "epsilon1": 0.0, "epsilon2": 0.0,
               "z_l1": [256 floats], "z_l2": [256 floats],
               "surrogate_only": true, "bec_cross_check": {...}},
  "train": {"streams": [{"seed": 0, "l1": {"n_used": 0, "n_impossible": 0,
              "e": [256], "h": [256], "e_summary": {...}, "h_summary": {...},
              "order": [256]}, "l2": {...}}], "pooled": {...}},
  "orders": {"l1": {"train_2026091600": [256], "train_2026091601": [256],
             "train_2026091602": [256], "pooled_empirical": [256], "bec": [256]},
             "l2": {...}},
  "orders_sha256": "...",
  "statistics": {"l1": {"pairwise": {...}, "risk_vs_bec_z_spearman": {...},
                 "risk_summaries": {...}, "bec": {...}}, "l2": {...}},
  "dev": {"per_block": [{"stream": 0, "block": 0, "layer": "L1",
           "order": "pooled_empirical", "k": 45, "exact": false,
           "initial_error": true, "failure_class": "mismatch"}],
           "aggregates": {"pooled": {...}, "per_stream": {...}},
           "failure_class_note": "..."},
  "counters": {...}, "truth_isolation": {...},
  "wall_s": 0.0, "phase_wall_s": {"train": 0.0, "dev": 0.0},
  "rss_bytes_peak": 0,
  "commands": [{"n": 1, "command_full_text": "...", "exit_code": 0,
                "stdout_tail": "...", "stderr_tail": ""}],
  "notes": {...}
}
```

## 6. Write scope, prohibitions, stop rules

- Writes exactly `workspace/probes/nbpolar_x06_empirical_construction_order/{prereg.md,results.json}`
  plus `/tmp` staging/log files. No production module edit, no sibling-checkout
  write, no earlier evidence-root write, no ledger/memory/index update, no
  commit or push.
- Forbidden: raw/real data, candidate-conditioned L2, end-to-end claims, new
  scientific attempt, EVAL, N>256, FWHT, APP, SCL, learned policy,
  qualification/promotion, threshold/pass-fail/winner/candidate label.
- Limits: 2 GiB RSS and 3600 s wall; the body aborts and writes a stopped record
  if either is exceeded.
- STOP with the failure root preserved and no retry on: input mismatch,
  target-root presence, loader/normalization failure, truth leak, nonfinite
  value, resource limit, unexpected decoder exception.
- Failure/partial records are written as `results.json` with a `stopped_*`
  status; `artifact_content_reads_consumed` is recorded as 1 once the open is
  attempted, never retried.

## 7. Execution contract

- Interpreter: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
  (POSIX/Python 3.12; numpy recorded in results).
- Working directory: `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- Staged body: `/tmp/x06_body.log`, byte-identical to the body embedded below.
  The body re-reads this prereg, extracts the body, and compares sha256 with the
  staged file before the artifact open; a mismatch stops the probe.
- One execution planned; no rerun and no parameter change after the content
  open.
- Pre-open rehearsal (synthetic only, no sibling read): the exact body text was
  executed against a synthetic accepted-shape `model_f_input` pair under
  `/tmp/x06_rehearsal/` with 2 TRAIN / 2 DEV blocks before this prereg was
  frozen. It completed with `status: "completed"`, valid 256-permutations,
  `recount_mismatch == 0`, and `orders_unchanged_after_dev == true`. The
  rehearsal fixed one call-shape issue only (the accepted 2D `[None, :]`
  convention of `build_p1_metrics`/`gather_p2_metrics`, as already used by X03);
  no scientific parameter changed.

## 8. Frozen command (complete executed body; no probe script file)

```bash
cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - <<'X06'
"""X06 frozen probe body: empirical vs BEC construction orders (Tier-X, non-claim).

Executed once from the repository root as
``/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - < /tmp/x06_body.log``

Consumes exactly one artifact content open through the accepted loader
``prior_artifact.load_prior_artifact``; all streams then run in-memory in this
same process. Writes only ``workspace/probes/nbpolar_x06_empirical_construction_order/results.json``.
"""
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import empirical_channel as ec
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.construction import (
    analytic_order,
    disclosure_order_from_stats,
    genie_conditionals,
    spearman_rank_corr,
    topk_overlap,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    Provenance,
    build_p1_metrics,
    derive_p1,
    derive_p2,
    gather_p2_metrics,
    probs_to_symbol_metric,
    smooth_joint_to_conditional,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior_artifact import (
    LAMBDA_STAR,
    load_prior_artifact,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc import (
    ImpossibleDisclosedValueError,
    NumericNonfiniteError,
    sc_decode,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.synthetic import analytic_erasure_probs
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform

try:  # POSIX only (the frozen command runs under WSL); Windows native has no resource module.
    import resource
except ImportError:  # pragma: no cover
    resource = None

ROOT = Path("workspace/probes/nbpolar_x06_empirical_construction_order")
PREREG = ROOT / "prereg.md"
OUT = ROOT / "results.json"
BODY_LOG = Path("/tmp/x06_body.log")
NPZ_PATH = "/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input.npz"
SUMMARY_PATH = "/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1/model_f_input_summary.json"
COMMAND_TEXT = "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - < /tmp/x06_body.log"

PROBE_ID = "nbpolar_x06_empirical_construction_order"
N = 256
Q = 32
POLY = 37
ALPHA = 2
LOG2 = float(np.log(2.0))
TRAIN_STREAMS = (2026091600, 2026091601, 2026091602)
TRAIN_BLOCKS = 256
DEV_STREAMS = (2026091610, 2026091611, 2026091612, 2026091613, 2026091614)
DEV_BLOCKS = 128
L1_KS = (45, 60, 72, 112)
L2_KS = (140,)
DEV_ORDER_IDS = ("pooled_empirical", "bec")
FAILURE_CLASSES = ("exact", "mismatch", "decode_failed", "nonfinite")
WALL_CAP_S = 3600.0
RSS_CAP_BYTES = 2 * 1024 ** 3

LOG = []
OPEN_ATTEMPTED = False
OPEN_DONE = False
PREREG_SHA = {"value": None}
BODY_SHA = {"value": None, "match": None}
START_WALL = time.monotonic()


class _ResourceAbort(RuntimeError):
    def __init__(self, kind, stage, value):
        super().__init__("resource limit %s exceeded at %s: %r" % (kind, stage, value))
        self.kind = kind
        self.stage = stage
        self.value = value


def log(message):
    text = str(message)
    LOG.append(text)
    print(text, flush=True)


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def peak_rss_bytes():
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def canonical_sha(obj):
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def interpreter_record():
    return {
        "executable": sys.executable,
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
    }


def xlog2x(x):
    arr = np.asarray(x, dtype=np.float64)
    out = np.zeros_like(arr)
    mask = arr > 0
    out[mask] = arr[mask] * np.log2(arr[mask])
    return out


def summarize(vec):
    v = np.asarray(vec, dtype=np.float64).ravel()
    return {
        "min": float(v.min()),
        "max": float(v.max()),
        "mean": float(v.mean()),
        "median": float(np.median(v)),
        "q25": float(np.quantile(v, 0.25)),
        "q75": float(np.quantile(v, 0.75)),
        "sum": float(v.sum()),
        "count_zero": int(np.sum(v == 0.0)),
        "count_positive": int(np.sum(v > 0.0)),
    }


def body_from_command(command):
    lines = command.splitlines()
    start = next(i for i, line in enumerate(lines) if line.rstrip().endswith("<<'X06'"))
    stop = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "X06")
    return "\n".join(lines[start + 1:stop]) + "\n"


def guard(t0, stage):
    elapsed = time.monotonic() - t0
    if elapsed > WALL_CAP_S:
        raise _ResourceAbort("wall_s", stage, elapsed)
    rss = peak_rss_bytes()
    if rss is not None and rss > RSS_CAP_BYTES:
        raise _ResourceAbort("rss_bytes", stage, rss)


def is_nonfinite_exception(exc):
    if isinstance(exc, NumericNonfiniteError):
        return True
    text = str(exc).lower()
    return ("nonfinite" in text) or ("nan" in text)


def classify_decode(logp, known_positions, known_values, u_true, x_true, field):
    """Fresh SC decode once; exact/mismatch/decode_failed/nonfinite taxonomy.

    Non-ValueError exceptions are unexpected decoder exceptions and propagate
    to the caller (stop rule), never silently classified.
    """
    try:
        res = sc_decode(
            logp, field=field, alpha=ALPHA,
            known_positions=known_positions, known_values=known_values,
        )
    except ValueError as exc:
        return ("nonfinite" if is_nonfinite_exception(exc) else "decode_failed"), type(exc).__name__
    if bool(np.isnan(res.decision_metrics).any()) or bool(np.isposinf(res.decision_metrics).any()):
        return "nonfinite", None
    if bool(np.array_equal(res.u_hat, u_true)) and bool(np.array_equal(res.x_hat, x_true)):
        return "exact", None
    return "mismatch", None


def accum_genie(acc, logp, u_true, field):
    """Accepted genie full-true semantics: e=1-max p, h=-log2 p(u_true)."""
    try:
        cond = genie_conditionals(logp, u_true, field=field, alpha=ALPHA)
    except ImpossibleDisclosedValueError:
        acc["impossible"] += 1
        return
    probs = np.exp(cond)
    idx = np.arange(cond.shape[0])
    acc["h"] += -cond[idx, u_true] / LOG2
    acc["e"] += 1.0 - probs.max(axis=1)
    acc["used"] += 1


def run_train_stream(seed, field, f_table, p_b, p1, p2, t0):
    rng = ec.make_rng(int(seed))
    acc = {
        layer: {"h": np.zeros(N, dtype=np.float64), "e": np.zeros(N, dtype=np.float64),
                "used": 0, "impossible": 0}
        for layer in ("l1", "l2")
    }
    for b in range(TRAIN_BLOCKS):
        guard(t0, "train:%d:block=%d" % (seed, b))
        bob, _a_full, high, low = ec.sample_full_block(rng, p_b, f_table, Q, Q, N)
        u1 = polar_transform(high, field=field, alpha=ALPHA)
        u2 = polar_transform(low, field=field, alpha=ALPHA)
        l1_metric = probs_to_symbol_metric(build_p1_metrics(bob[None, :], p1)[0], provenance=Provenance.PRIOR_ONLY)
        accum_genie(acc["l1"], l1_metric.logp, u1, field)
        l2_metric = probs_to_symbol_metric(
            gather_p2_metrics(bob[None, :], high[None, :], p2)[0], provenance=Provenance.ORACLE_CONDITIONED
        )
        accum_genie(acc["l2"], l2_metric.logp, u2, field)
    return acc


def order_from_acc(acc):
    used = max(int(acc["used"]), 1)
    return disclosure_order_from_stats(acc["e"] / used, acc["h"] / used)


def position_rank(order):
    order = np.asarray(order, dtype=np.int64)
    pos = np.empty(order.shape[0], dtype=np.int64)
    pos[order] = np.arange(order.shape[0], dtype=np.int64)
    return pos


def spearman_orders(order_a, order_b):
    return float(spearman_rank_corr(position_rank(order_a), position_rank(order_b)))


def counts_from_rows(rows):
    counts = {}
    for r in rows:
        key = (r["layer"], r["order"], int(r["k"]))
        cell = counts.setdefault(
            key, {"records": 0, "initial_error": 0, **{name: 0 for name in FAILURE_CLASSES}}
        )
        cell["records"] += 1
        cell[r["failure_class"]] += 1
        cell["initial_error"] += int(bool(r["initial_error"]))
    return counts


def paired_four_cell(rows):
    by_unit = {}
    for r in rows:
        by_unit.setdefault((r["stream"], r["block"], r["layer"], int(r["k"])), {})[r["order"]] = r
    cells = {}
    incomplete = 0
    for (stream, block, layer, k), pair in by_unit.items():
        if set(pair) != set(DEV_ORDER_IDS):
            incomplete += 1
            continue
        key = "%s|k=%d" % (layer, k)
        cell = cells.setdefault(
            key, {"pairs": 0, "both_exact": 0, "empirical_only": 0, "bec_only": 0, "neither": 0}
        )
        cell["pairs"] += 1
        emp = pair["pooled_empirical"]["failure_class"] == "exact"
        bec = pair["bec"]["failure_class"] == "exact"
        if emp and bec:
            cell["both_exact"] += 1
        elif emp:
            cell["empirical_only"] += 1
        elif bec:
            cell["bec_only"] += 1
        else:
            cell["neither"] += 1
    return {"cells": cells, "incomplete_pairs": incomplete}


def aggregate_dev(rows):
    counts = counts_from_rows(rows)
    out = {}
    for key, cell in counts.items():
        layer, oid, k = key
        out.setdefault(layer, {}).setdefault(oid, {})[str(k)] = {
            **{name: int(cell[name]) for name in ("records",) + FAILURE_CLASSES},
            "initial_error": int(cell["initial_error"]),
        }
    return {"counts": out, "paired_four_cell": paired_four_cell(rows)}


def write_stopped(status, checks, failures, reason, stage=None, extra=None):
    payload = {
        "probe_id": PROBE_ID,
        "tier": "X-non-claim",
        "status": status,
        "stop_reason": reason,
        "stop_stage": stage,
        "input_integrity": {"checks": checks, "failures": int(failures)},
        "prereg_sha256": PREREG_SHA["value"],
        "body_sha256": BODY_SHA["value"],
        "body_sha_match": BODY_SHA["match"],
        "interpreter": interpreter_record(),
        "command": {"text": COMMAND_TEXT, "staged_body_path": str(BODY_LOG)},
        "artifact_open": {
            "loader": "comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior_artifact.load_prior_artifact",
            "npz_path": NPZ_PATH,
            "summary_path": SUMMARY_PATH,
            "artifact_content_reads_allowed": 1,
            "artifact_content_reads_consumed": int(OPEN_ATTEMPTED),
            "open_completed": bool(OPEN_DONE),
        },
        "wall_s": time.monotonic() - START_WALL,
        "rss_bytes_peak": peak_rss_bytes(),
        "commands": [{
            "n": 1,
            "kind": "frozen X06 Tier-X probe body (single artifact content open; no rerun)",
            "command_full_text": COMMAND_TEXT,
            "exit_code": 1,
            "stdout_tail": "\n".join(LOG[-40:]),
            "stderr_tail": "",
        }],
        "notes": {
            "scope": "Tier-X non-claim probe; no threshold, winner, candidate/accepted token or qualification conclusion",
            "write_scope": "exactly workspace/probes/nbpolar_x06_empirical_construction_order/{prereg.md,results.json} plus /tmp logs",
            "failure_retention": "failure root preserved with no retry; one artifact content read is not repeated",
        },
    }
    if extra:
        payload.update(extra)
    try:
        write_json(OUT, payload)
    except Exception as exc:  # never hide a failure-root write problem
        log("write_stopped failed: %s: %s" % (type(exc).__name__, exc))


def main():
    global OPEN_ATTEMPTED, OPEN_DONE
    t0 = time.monotonic()
    checks = []

    def check(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        return bool(ok)

    # ---------------- pre-open integrity gates (no artifact content touched) ----------------
    listing = sorted(p.name for p in ROOT.iterdir()) if ROOT.is_dir() else None
    check("probe_root_exists", ROOT.is_dir(), str(ROOT))
    check("probe_root_exactly_prereg_only", listing == ["prereg.md"], listing)
    check("results_json_absent", not OUT.exists(), str(OUT))
    body_ok = check("staged_body_present", BODY_LOG.is_file(), str(BODY_LOG))
    if body_ok:
        BODY_SHA["value"] = hashlib.sha256(BODY_LOG.read_bytes()).hexdigest()
    if PREREG.is_file():
        text = PREREG.read_text(encoding="utf-8")
        PREREG_SHA["value"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        match = re.search(r"```bash\n(.*?)\n```", text, re.S)
        check("prereg_bash_block_found", match is not None, None)
        if match is not None:
            embedded_sha = hashlib.sha256(body_from_command(match.group(1)).encode("utf-8")).hexdigest()
            BODY_SHA["match"] = BODY_SHA["value"] == embedded_sha
            check("body_sha_match", BODY_SHA["match"],
                  {"staged": BODY_SHA["value"], "embedded": embedded_sha})
    else:
        check("prereg_present", False, str(PREREG))

    failures = sum(1 for c in checks if not c["ok"])
    log("X06 pre-open checks: %d, failures: %d" % (len(checks), failures))
    if failures:
        write_stopped("stopped_pre_open_integrity", checks, failures,
                      "pre-open integrity gate failed", stage="pre_open")
        return 1

    # ---------------- the single artifact content open ----------------
    try:
        OPEN_ATTEMPTED = True
        log("ARTIFACT OPEN 1/1 via prior_artifact.load_prior_artifact at %s" % utcnow())
        artifact = load_prior_artifact(NPZ_PATH, SUMMARY_PATH)
        OPEN_DONE = True
    except Exception as exc:
        write_stopped("stopped_loader_failure", checks, 0,
                      "loader failure: %s: %s" % (type(exc).__name__, exc), stage="artifact_open")
        return 1
    open_utc = utcnow()
    log("artifact open completed: %s" % open_utc)

    # ---------------- accepted table derivation (in-memory only) ----------------
    counts = artifact.counts_ab
    p_b = np.array(artifact.p_b, dtype=np.float64, copy=True)
    f_table = smooth_joint_to_conditional(counts, LAMBDA_STAR)
    p1 = derive_p1(f_table)
    p2 = derive_p2(f_table)
    table_checks = {
        "counts_shape": list(counts.shape),
        "counts_dtype": str(counts.dtype),
        "counts_sum": int(counts.sum()),
        "p_b_shape": list(p_b.shape),
        "p_b_sum": float(p_b.sum()),
        "f_shape": list(f_table.shape),
        "f_min": float(f_table.min()),
        "f_max": float(f_table.max()),
        "f_column_dev_max": float(np.abs(f_table.sum(axis=0) - 1.0).max()),
        "p1_shape": list(p1.shape),
        "p1_column_dev_max": float(np.abs(p1.sum(axis=0) - 1.0).max()),
        "p2_shape": list(p2.shape),
        "p2_symbol_dev_max": float(np.abs(p2.sum(axis=2) - 1.0).max()),
        "f_finite": bool(np.isfinite(f_table).all()),
        "f_nonnegative": bool((f_table >= 0).all()),
    }
    table_ok = (
        table_checks["counts_sum"] == 262144
        and abs(table_checks["p_b_sum"] - 1.0) <= 1e-12
        and table_checks["f_shape"] == [1024, 1024]
        and table_checks["p1_shape"] == [32, 1024]
        and table_checks["p2_shape"] == [32, 1024, 32]
        and table_checks["f_column_dev_max"] <= 1e-9
        and table_checks["p1_column_dev_max"] <= 1e-9
        and table_checks["p2_symbol_dev_max"] <= 1e-9
        and table_checks["f_finite"] and table_checks["f_nonnegative"]
    )
    checks.append({"name": "table_derivation_contract", "ok": bool(table_ok), "detail": table_checks})
    if not table_ok:
        write_stopped("stopped_table_contract", checks, 1,
                      "derived table contract mismatch", stage="table_derivation")
        return 1

    field = make_gf32()

    try:
        # ---------------- TRAIN construction (orders frozen before any DEV call) ----------------
        train_start = time.monotonic()
        train_acc = {}
        for seed in TRAIN_STREAMS:
            train_acc[seed] = run_train_stream(seed, field, f_table, p_b, p1, p2, t0)
            log("TRAIN stream %d complete: l1_used=%d l2_used=%d"
                % (seed, train_acc[seed]["l1"]["used"], train_acc[seed]["l2"]["used"]))
        train_wall = time.monotonic() - train_start

        pooled_acc = {}
        for layer in ("l1", "l2"):
            pooled_acc[layer] = {
                "h": sum(train_acc[s][layer]["h"] for s in TRAIN_STREAMS),
                "e": sum(train_acc[s][layer]["e"] for s in TRAIN_STREAMS),
                "used": sum(train_acc[s][layer]["used"] for s in TRAIN_STREAMS),
                "impossible": sum(train_acc[s][layer]["impossible"] for s in TRAIN_STREAMS),
            }

        # BEC analytic surrogate controls: epsilon_l = H_l / log2(32), H_l from the same table.
        h1_cond_per_b = -xlog2x(p1).sum(axis=0)
        h1_bits = float(np.sum(p_b * h1_cond_per_b))
        h2_cond_per_ub = -xlog2x(p2).sum(axis=2)
        h2_bits = float(np.sum(p1 * p_b[None, :] * h2_cond_per_ub))
        eps1_raw = h1_bits / float(np.log2(Q))
        eps2_raw = h2_bits / float(np.log2(Q))
        eps1 = float(min(1.0, max(0.0, eps1_raw)))
        eps2 = float(min(1.0, max(0.0, eps2_raw)))
        z1 = analytic_erasure_probs(eps1, N)
        z2 = analytic_erasure_probs(eps2, N)
        bec_l1 = analytic_order(eps1, N)
        bec_l2 = analytic_order(eps2, N)
        bec_cross_check = {
            "l1_matches_sorted_z": bool(np.array_equal(
                bec_l1, np.array(sorted(range(N), key=lambda i: (-float(z1[i]), i)), dtype=np.int64))),
            "l2_matches_sorted_z": bool(np.array_equal(
                bec_l2, np.array(sorted(range(N), key=lambda i: (-float(z2[i]), i)), dtype=np.int64))),
        }

        orders_np = {}
        orders_public = {}
        for layer, bec_order in (("l1", bec_l1), ("l2", bec_l2)):
            layer_orders = {}
            for seed in TRAIN_STREAMS:
                layer_orders["train_%d" % seed] = order_from_acc(train_acc[seed][layer])
            layer_orders["pooled_empirical"] = order_from_acc(pooled_acc[layer])
            layer_orders["bec"] = bec_order
            orders_np[layer] = layer_orders
            orders_public[layer] = {name: [int(v) for v in arr.tolist()] for name, arr in layer_orders.items()}
        orders_sha256 = canonical_sha(orders_public)
        log("orders frozen before DEV: sha256=%s" % orders_sha256)

        # ---------------- DEV evaluation (fresh-restart SC per order/K) ----------------
        dev_start = time.monotonic()
        dev_rows = []
        expected_records = len(DEV_STREAMS) * DEV_BLOCKS * (
            len(DEV_ORDER_IDS) * len(L1_KS) + len(DEV_ORDER_IDS) * len(L2_KS)
        )
        counts_online = {}
        for seed in DEV_STREAMS:
            rng = ec.make_rng(int(seed))
            for b in range(DEV_BLOCKS):
                guard(t0, "dev:%d:block=%d" % (seed, b))
                bob, _a_full, high, low = ec.sample_full_block(rng, p_b, f_table, Q, Q, N)
                u1 = polar_transform(high, field=field, alpha=ALPHA)
                u2 = polar_transform(low, field=field, alpha=ALPHA)
                l1_logp = probs_to_symbol_metric(
                    build_p1_metrics(bob[None, :], p1)[0], provenance=Provenance.PRIOR_ONLY
                ).logp
                l2_logp = probs_to_symbol_metric(
                    gather_p2_metrics(bob[None, :], high[None, :], p2)[0], provenance=Provenance.ORACLE_CONDITIONED
                ).logp
                init1 = bool(np.any(np.argmax(l1_logp, axis=1) != high))
                init2 = bool(np.any(np.argmax(l2_logp, axis=1) != low))
                layer_specs = (
                    ("L1", l1_logp, u1, high, init1, orders_np["l1"], L1_KS),
                    ("oracle_L2", l2_logp, u2, low, init2, orders_np["l2"], L2_KS),
                )
                for layer_name, logp, u_true, x_true, init_err, layer_orders, ks in layer_specs:
                    for oid in DEV_ORDER_IDS:
                        order = layer_orders[oid]
                        for k in ks:
                            pos = order[:k]
                            cls, _exc = classify_decode(logp, pos, u_true[pos], u_true, x_true, field)
                            row = {
                                "stream": int(seed), "block": int(b), "layer": layer_name,
                                "order": oid, "k": int(k), "exact": cls == "exact",
                                "initial_error": bool(init_err), "failure_class": cls,
                            }
                            dev_rows.append(row)
                            key = (layer_name, oid, int(k))
                            cell = counts_online.setdefault(
                                key, {"records": 0, "initial_error": 0,
                                      **{name: 0 for name in FAILURE_CLASSES}}
                            )
                            cell["records"] += 1
                            cell[cls] += 1
                            cell["initial_error"] += int(bool(init_err))
            log("DEV stream %d complete (%d blocks)" % (seed, DEV_BLOCKS))
        dev_wall = time.monotonic() - dev_start

        # ---------------- recount / freeze integrity ----------------
        recount = counts_from_rows(dev_rows)
        recount_mismatch = sum(
            abs(int(counts_online[key][name]) - int(recount.get(key, {}).get(name, -1)))
            for key in counts_online for name in ("records", "initial_error") + FAILURE_CLASSES
        )
        key_set_mismatch = int(set(counts_online) != set(recount))
        orders_unchanged = canonical_sha(orders_public) == orders_sha256
        duplicate_rows = len(dev_rows) - len({
            (r["stream"], r["block"], r["layer"], r["order"], r["k"]) for r in dev_rows
        })
        record_count_ok = len(dev_rows) == expected_records
        if (recount_mismatch or key_set_mismatch or duplicate_rows or not record_count_ok
                or not orders_unchanged):
            write_stopped(
                "stopped_recount_mismatch", checks, 0,
                "independent recount / freeze integrity mismatch", stage="recount",
                extra={"counters": {
                    "recount_mismatch": recount_mismatch,
                    "key_set_mismatch": key_set_mismatch,
                    "duplicate_rows": duplicate_rows,
                    "records": len(dev_rows),
                    "expected_records": expected_records,
                    "orders_unchanged_after_dev": orders_unchanged,
                }},
            )
            return 1

        # ---------------- descriptive statistics ----------------
        statistics = {}
        for layer, ks in (("l1", L1_KS), ("l2", L2_KS)):
            ids = ["train_%d" % s for s in TRAIN_STREAMS] + ["pooled_empirical", "bec"]
            pairs = {}
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    a, b = ids[i], ids[j]
                    pairs["%s__vs__%s" % (a, b)] = {
                        "spearman_position_rank": spearman_orders(orders_np[layer][a], orders_np[layer][b]),
                        "topk_overlap": {str(k): float(topk_overlap(orders_np[layer][a], orders_np[layer][b], k)) for k in ks},
                    }
            risk_summaries = {
                "train_%d" % s: {"e": summarize(train_acc[s][layer]["e"] / max(train_acc[s][layer]["used"], 1)),
                                 "h": summarize(train_acc[s][layer]["h"] / max(train_acc[s][layer]["used"], 1))}
                for s in TRAIN_STREAMS
            }
            risk_summaries["pooled_empirical"] = {
                "e": summarize(pooled_acc[layer]["e"] / max(pooled_acc[layer]["used"], 1)),
                "h": summarize(pooled_acc[layer]["h"] / max(pooled_acc[layer]["used"], 1)),
            }
            z = z1 if layer == "l1" else z2
            eps = eps1 if layer == "l1" else eps2
            risk_vs_z = {}
            for name in ["train_%d" % s for s in TRAIN_STREAMS]:
                acc = train_acc[int(name.split("_")[1])][layer]
                risk_vs_z[name] = float(spearman_rank_corr(acc["e"] / max(int(acc["used"]), 1), z))
            risk_vs_z["pooled_empirical"] = float(spearman_rank_corr(
                pooled_acc[layer]["e"] / max(int(pooled_acc[layer]["used"]), 1), z))
            statistics[layer] = {
                "pairwise": pairs,
                "risk_vs_bec_z_spearman": risk_vs_z,
                "risk_summaries": risk_summaries,
                "bec": {"epsilon": eps, "z_summary": summarize(z)},
            }

        train_streams_out = []
        for seed in TRAIN_STREAMS:
            entry = {"seed": int(seed), "blocks_attempted": int(TRAIN_BLOCKS)}
            for layer in ("l1", "l2"):
                acc = train_acc[seed][layer]
                used = max(int(acc["used"]), 1)
                entry[layer] = {
                    "n_used": int(acc["used"]),
                    "n_impossible": int(acc["impossible"]),
                    "e": [float(v) for v in (acc["e"] / used).tolist()],
                    "h": [float(v) for v in (acc["h"] / used).tolist()],
                    "e_summary": summarize(acc["e"] / used),
                    "h_summary": summarize(acc["h"] / used),
                    "order": orders_public[layer]["train_%d" % seed],
                }
            train_streams_out.append(entry)
        pooled_out = {"blocks_attempted": int(TRAIN_BLOCKS * len(TRAIN_STREAMS))}
        for layer in ("l1", "l2"):
            acc = pooled_acc[layer]
            used = max(int(acc["used"]), 1)
            pooled_out[layer] = {
                "n_used": int(acc["used"]),
                "n_impossible": int(acc["impossible"]),
                "e": [float(v) for v in (acc["e"] / used).tolist()],
                "h": [float(v) for v in (acc["h"] / used).tolist()],
                "e_summary": summarize(acc["e"] / used),
                "h_summary": summarize(acc["h"] / used),
                "order": orders_public[layer]["pooled_empirical"],
            }

        dev_aggregates = {
            "pooled": aggregate_dev(dev_rows),
            "per_stream": {
                str(seed): aggregate_dev([r for r in dev_rows if r["stream"] == seed])
                for seed in DEV_STREAMS
            },
        }
        for scope in [dev_aggregates["pooled"]] + list(dev_aggregates["per_stream"].values()):
            if scope["paired_four_cell"]["incomplete_pairs"] != 0:
                raise RuntimeError("paired four-cell table has incomplete pairs; refusing to guess")

        payload = {
            "probe_id": PROBE_ID,
            "tier": "X-non-claim",
            "status": "completed",
            "prereg_sha256": PREREG_SHA["value"],
            "body_sha256": BODY_SHA["value"],
            "body_sha_match": BODY_SHA["match"],
            "interpreter": interpreter_record(),
            "command": {"text": COMMAND_TEXT, "staged_body_path": str(BODY_LOG), "cwd": str(Path.cwd())},
            "artifact_open": {
                "loader": "comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior_artifact.load_prior_artifact",
                "npz_path": NPZ_PATH,
                "summary_path": SUMMARY_PATH,
                "artifact_content_reads_allowed": 1,
                "artifact_content_reads_consumed": 1,
                "open_count": 1,
                "open_completed_utc": open_utc,
                "lambda_star": float(LAMBDA_STAR),
                "summary_identity": {k: artifact.summary[k] for k in sorted(artifact.summary)},
                "derivation": {
                    "f_table": "prior.smooth_joint_to_conditional(artifact.counts_ab, prior_artifact.LAMBDA_STAR); shape [Alice,Bob]",
                    "p1_table": "prior.derive_p1(f_table); shape [U1,B] = (32,1024)",
                    "p2_table": "prior.derive_p2(f_table); shape [U1,B,U2] = (32,1024,32)",
                    "p_b": "artifact.p_b (stored axis-0 marginal; loader-validated against counts_ab)",
                },
                "table_checks": table_checks,
            },
            "config": {
                "q": Q, "primitive_polynomial": POLY, "alpha": ALPHA, "n": N,
                "ordering": "natural (no bit reversal)",
                "train_streams": [int(s) for s in TRAIN_STREAMS],
                "train_blocks_per_stream": int(TRAIN_BLOCKS),
                "dev_streams": [int(s) for s in DEV_STREAMS],
                "dev_blocks_per_stream": int(DEV_BLOCKS),
                "l1_ks": [int(k) for k in L1_KS],
                "l2_ks": [int(k) for k in L2_KS],
                "sampler": "empirical_channel.make_rng(stream) + empirical_channel.sample_full_block(rng, p_b, f, 32, 32, 256): Bob ~ p_b then Alice ~ f[:,Bob]; high=Alice//32, low=Alice%32",
                "metrics": {
                    "l1": "prior.build_p1_metrics(bob, p1) -> prior.probs_to_symbol_metric(PRIOR_ONLY)",
                    "oracle_l2": "prior.gather_p2_metrics(bob, high_true, p2) -> prior.probs_to_symbol_metric(ORACLE_CONDITIONED)",
                    "sc": "sc.sc_decode fresh restart per (order, K); known_positions=order[:K], known_values=layer_truth[order[:K]]",
                },
                "orders": "construction.disclosure_order_from_stats: worst-first descending (e, h), ties by index; pooled SUMS of per-block e/h divided by pooled used blocks (never selected after DEV)",
                "bec": {
                    "epsilon_definition": "epsilon_l = H_l / log2(32) bits",
                    "entropy_definition": (
                        "H1 = E_B[H(U1|B)] = -sum_b p_b[b] sum_u1 p1[u1,b] log2 p1[u1,b]; "
                        "H2 = E_{B,U1}[H(U2|U1,B)] = -sum_b p_b[b] sum_u1 p1[u1,b] sum_u2 p2[u1,b,u2] log2 p2[u1,b,u2]; "
                        "per-coordinate symbol-domain conditional entropies in bits from the same smoothed table"
                    ),
                    "order": "construction.analytic_order(epsilon_l, 256)",
                    "surrogate_only": True,
                },
                "limits": {"wall_cap_s": WALL_CAP_S, "rss_cap_bytes": RSS_CAP_BYTES},
                "failure_classes": list(FAILURE_CLASSES),
            },
            "entropy": {
                "h1_bits": h1_bits, "h2_bits": h2_bits,
                "epsilon1": eps1, "epsilon2": eps2,
                "epsilon1_raw": eps1_raw, "epsilon2_raw": eps2_raw,
                "epsilon_clamped": bool(eps1 != eps1_raw or eps2 != eps2_raw),
                "z_l1": [float(v) for v in z1.tolist()],
                "z_l2": [float(v) for v in z2.tolist()],
                "surrogate_only": True,
                "surrogate_note": "BEC analytic control is a surrogate construction order only; not a channel claim about the model-sampled channel.",
                "bec_cross_check": bec_cross_check,
            },
            "train": {"streams": train_streams_out, "pooled": pooled_out},
            "orders": orders_public,
            "orders_sha256": orders_sha256,
            "statistics": statistics,
            "dev": {
                "per_block": dev_rows,
                "aggregates": dev_aggregates,
                "failure_class_note": "per-block scalars only (stream, block, layer, order, k, exact, initial_error, failure_class); no source/Bob/U/decoded/disclosed vectors or metric arrays persisted; 'undetected' is not applicable without a tag and is neither invented nor merged into exact",
            },
            "counters": {
                "train_blocks_attempted": int(TRAIN_BLOCKS * len(TRAIN_STREAMS)),
                "train_blocks_used_l1": int(pooled_acc["l1"]["used"]),
                "train_blocks_used_l2": int(pooled_acc["l2"]["used"]),
                "train_impossible_l1": int(pooled_acc["l1"]["impossible"]),
                "train_impossible_l2": int(pooled_acc["l2"]["impossible"]),
                "dev_records": len(dev_rows),
                "dev_records_expected": expected_records,
                "duplicate_rows": duplicate_rows,
                "recount_mismatch": recount_mismatch,
                "key_set_mismatch": key_set_mismatch,
                "orders_unchanged_after_dev": orders_unchanged,
                "input_integrity_failures": 0,
                "resource_abort": None,
            },
            "truth_isolation": {
                "l1_metric_inputs": "prior.build_p1_metrics(bob, p1) receives Bob labels plus the accepted table only (no truth argument exists)",
                "oracle_l2_metric_inputs": "prior.gather_p2_metrics(bob, high_true, p2) uses the true L1 labels by design (ORACLE_CONDITIONED); permitted for oracle-L2 conditioning",
                "disclosure_values": "known_values come only from the frozen order prefixes of that layer's truth; no undisclosed truth is passed to sc_decode",
                "order_selection": "all orders derived from TRAIN streams only, frozen and hashed before the first DEV call; hash recomputed unchanged after DEV",
                "dev_persistence": "scalars only; no source/Bob/U/decoded/disclosed vectors or metric arrays",
            },
            "wall_s": time.monotonic() - t0,
            "phase_wall_s": {"train": train_wall, "dev": dev_wall},
            "rss_bytes_peak": peak_rss_bytes(),
            "commands": [{
                "n": 1,
                "kind": "frozen X06 Tier-X probe body (single artifact content open; no rerun)",
                "command_full_text": COMMAND_TEXT,
                "exit_code": 0,
                "stdout_tail": "\n".join(LOG[-40:]),
                "stderr_tail": "",
            }],
            "notes": {
                "scope": "Tier-X non-claim probe; no threshold, winner, candidate/accepted token or qualification conclusion",
                "streams": "probe-only disjoint streams; no EVAL stream exists; TRAIN and DEV seeds disjoint",
                "bec": "analytic BEC control is a surrogate construction order only (epsilon_l = H_l/5 bits)",
                "undetected": "not applicable (no tag stage); never invented or merged into exact",
                "public_coordinate_statistics": "per-coordinate TRAIN e/h vectors and BEC z vectors are public scalar statistics included so the reviewer can recompute ranks/overlaps; no source/Bob/U/decoded/disclosed vectors or metric arrays are persisted",
                "write_scope": "exactly workspace/probes/nbpolar_x06_empirical_construction_order/{prereg.md,results.json} plus /tmp logs",
                "artifact_reads": "one content open consumed 1/1; no raw parquet/TTBin, no sibling write, no earlier evidence-root write",
                "no_rerun": "design frozen before the content open; no retry or parameter change",
                "review": "independent reviewer-go focused review required before any downstream use",
            },
        }
        write_json(OUT, payload)
        log("X06 complete: records=%d wall_s=%.1f rss=%s"
            % (len(dev_rows), payload["wall_s"], payload["rss_bytes_peak"]))
        return 0
    except _ResourceAbort as exc:
        write_stopped("stopped_resource_limit", checks, 0, str(exc), stage=exc.stage,
                      extra={"resource_abort": {"kind": exc.kind, "stage": exc.stage, "value": exc.value},
                             "wall_s": time.monotonic() - t0, "rss_bytes_peak": peak_rss_bytes()})
        return 1


try:
    RC = main()
except SystemExit:
    raise
except Exception as exc:
    log("X06 execution error: %s: %s" % (type(exc).__name__, exc))
    write_stopped("stopped_unexpected_error", [], 0,
                  "%s: %s" % (type(exc).__name__, exc), stage="unhandled")
    RC = 1
raise SystemExit(RC)
X06
```

## 9. Staged execution hash record

- staged path: `/tmp/x06_body.log`
- body sha256: `37273d0d6095a4c168152aec9ac0836ca9a3b1dd36e624901fa77b59e89cd280`
- body byte length: 36155
- command: `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python - < /tmp/x06_body.log` (cwd `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`)
- recorded after staging, before the artifact content open; the embedded body text was not changed by this record.

