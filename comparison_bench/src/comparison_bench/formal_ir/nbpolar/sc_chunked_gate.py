"""NB-Polar Phase 4-P11 thin injected-data gate runner: exact chunked SC.

Frozen Tier-Y engineering gate (packet
``NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC``): proves the default-512 allocation
path of ``sc._minus_block`` is bitwise-equivalent to the unchunked golden
path (``chunk_rows=None``) across the frozen injected semantic matrix plus
one paired N=65536 block, then completes one default-512 N=262144 block
inside the frozen resource envelope. All inputs are RNG-injected from the
frozen seed; no artifact, evidence-root, raw, held-out, real, EVAL, tag or
protocol path is read. The single attempt is consumed at the first formal
``sc_decode`` call. Writes exactly four compact files; persists no input
vectors, decisions, metrics, decoded keys, raw arrays or artifacts.
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import platform
import resource
import sys
import time
import traceback
from pathlib import Path

import numpy as np

FROZEN_SEED = 2026091800
FROZEN_CHUNK_ROWS = 512
Q = 32
ALPHA = 2
PRIMITIVE_POLYNOMIAL = 37
PRIM_ROWS = [1, 31, 32, 33, 127, 128, 129, 511, 512, 513, 2048]
PRIM_KINDS = ["moderate_m20", "wide_m160", "neginf_support"]
SC_NS = [64, 256]
N_PAIRED = 65536
N_LARGE = 262144
RSS_HARD_LIMIT_BYTES = 1610612736
WALL_PLAN_TARGET_S = 120.0
RSS_PLAN_TARGET_BYTES = 1073741824
TIMEOUT_S = 600
VSZ_KB = 2097152
GATE_NAMES = [
    "semantic_parity",
    "paired_n65536_exact",
    "large_n262144_completion",
    "large_n262144_rss",
]
ATTEMPT_CONSUMPTION_POINT = (
    "first formal sc_decode call (step-1 N=64 F1_moderate direct arm); "
    "no artifact read is authorized or consumed"
)
NO_REOPEN_NOTE = (
    "N/A: no artifact/content file is opened at any point; every input is "
    "RNG-injected from the frozen seed, so there is nothing to reopen"
)
FOUR_FILES = [
    "frozen_plan.json",
    "equivalence_records.json",
    "scaling_record.json",
    "report.md",
]


class GateBlocked(Exception):
    """Earliest failing gate; carries the BLOCKED(<gate>) label."""

    def __init__(self, gate: str, detail: str = ""):
        super().__init__(f"BLOCKED({gate}){': ' + detail if detail else ''}")
        self.gate = gate


def _rss_peak() -> dict:
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


def _frozen_contract_check(sc_mod) -> None:
    params = inspect.signature(sc_mod._minus_block).parameters
    if params.get("chunk_rows", None) is None or params["chunk_rows"].default != 512:
        raise ValueError("frozen contract: _minus_block chunk_rows default must be exactly 512")
    if params["chunk_rows"].kind is not inspect.Parameter.KEYWORD_ONLY:
        raise ValueError("frozen contract: chunk_rows must be keyword-only")
    sc_params = inspect.signature(sc_mod.sc_decode).parameters
    if any("chunk" in name for name in sc_params):
        raise ValueError("frozen contract: sc_decode must expose no chunk argument")


def _gen_pair(rng, kind: str, rows: int):
    if kind == "moderate_m20":
        return rng.uniform(-20.0, 0.0, (rows, Q)), rng.uniform(-20.0, 0.0, (rows, Q))
    if kind == "wide_m160":
        return rng.uniform(-160.0, 0.0, (rows, Q)), rng.uniform(-160.0, 0.0, (rows, Q))
    if kind == "neginf_support":
        a = rng.uniform(-20.0, 0.0, (rows, Q))
        b = rng.uniform(-20.0, 0.0, (rows, Q))
        a[((np.arange(rows)[:, None] * 7 + np.arange(Q)[None, :]) % 4 == 0)] = -np.inf
        b[((np.arange(rows)[:, None] * 5 + np.arange(Q)[None, :] + 1) % 4 == 0)] = -np.inf
        for i in range(rows):
            if not np.isfinite(a[i]).any():
                a[i, (i * 5) % Q] = -5.0
            if not np.isfinite(b[i]).any():
                b[i, (i * 3 + 1) % Q] = -5.0
        return a, b
    raise ValueError(f"unknown primitive kind {kind!r}")


def _exc_summary(att: dict) -> dict:
    return {"raised": att["raised"], "exc_type": att.get("exc_type"), "message": att.get("message")}


def _cmp_results(direct, chunked) -> dict:
    dm_d = np.asarray(direct.decision_metrics)
    dm_c = np.asarray(chunked.decision_metrics)
    ds_d = np.asarray(direct.decision_log_scores)
    ds_c = np.asarray(chunked.decision_log_scores)
    both = np.isfinite(dm_d) & np.isfinite(dm_c)
    merr = float(np.abs(dm_d[both] - dm_c[both]).max()) if both.any() else None
    boths = np.isfinite(ds_d) & np.isfinite(ds_c)
    serr = float(np.abs(ds_d[boths] - ds_c[boths]).max()) if boths.any() else None
    return {
        "status_equal": bool(direct.status == chunked.status),
        "status": direct.status,
        "u_hat_exact": bool(np.array_equal(np.asarray(direct.u_hat), np.asarray(chunked.u_hat))),
        "u_hat_mismatches": int((np.asarray(direct.u_hat) != np.asarray(chunked.u_hat)).sum()),
        "x_hat_exact": bool(np.array_equal(np.asarray(direct.x_hat), np.asarray(chunked.x_hat))),
        "x_hat_mismatches": int((np.asarray(direct.x_hat) != np.asarray(chunked.x_hat)).sum()),
        "metrics_exact": bool(np.array_equal(dm_d, dm_c)),
        "max_finite_metric_abs_err": merr,
        "metrics_support_equal": bool((np.isfinite(dm_d) == np.isfinite(dm_c)).all()),
        "metrics_argmax_mismatches": int(
            (np.argmax(dm_d, axis=1) != np.argmax(dm_c, axis=1)).sum()
        ),
        "scores_exact": bool(np.array_equal(ds_d, ds_c)),
        "max_finite_score_abs_err": serr,
        "known_mask_exact": bool(
            np.array_equal(np.asarray(direct.known_mask), np.asarray(chunked.known_mask))
        ),
        "known_count_equal": bool(int(direct.known_count) == int(chunked.known_count)),
        "provenance_equal": bool(direct.metric_provenance == chunked.metric_provenance),
    }


def _parity_ok(cmp: dict) -> bool:
    return bool(
        cmp["status_equal"]
        and cmp["u_hat_exact"]
        and cmp["x_hat_exact"]
        and cmp["metrics_exact"]
        and cmp["scores_exact"]
        and cmp["known_mask_exact"]
        and cmp["known_count_equal"]
        and cmp["provenance_equal"]
        and cmp["metrics_support_equal"]
    )


def run_chunked_gate(seed: int, chunk_rows: int, out_dir: str) -> dict:
    """Execute the frozen P11 gate once and write exactly the four files."""
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    if int(seed) != FROZEN_SEED:
        raise ValueError(f"frozen gate requires seed={FROZEN_SEED}, got {seed!r}")
    if isinstance(chunk_rows, bool) or int(chunk_rows) != FROZEN_CHUNK_ROWS:
        raise ValueError(f"frozen gate requires chunk-rows={FROZEN_CHUNK_ROWS}, got {chunk_rows!r}")

    import comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc as sc_mod
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc import (
        _combination_index,
        _normalize_rows,
        sc_decode,
    )

    _frozen_contract_check(sc_mod)
    field = make_gf32()
    if int(field.q) != Q or int(getattr(field, "primitive_polynomial", -1)) != PRIMITIVE_POLYNOMIAL:
        raise ValueError("frozen gate requires GF(32) primitive polynomial 37")
    orig_minus = sc_mod._minus_block
    index = _combination_index(field, ALPHA, Q)

    def run_direct(metrics, kp=None, kv=None):
        sc_mod._minus_block = lambda f, s, idx: orig_minus(f, s, idx, chunk_rows=None)  # noqa: E731
        try:
            return sc_decode(metrics, field=field, alpha=ALPHA,
                             known_positions=kp, known_values=kv)
        finally:
            sc_mod._minus_block = orig_minus
            if sc_mod._minus_block is not orig_minus:
                raise RuntimeError("minus-block restoration failed")

    def run_chunked(metrics, kp=None, kv=None):
        if sc_mod._minus_block is not orig_minus:
            raise RuntimeError("chunked arm entered with patched minus-block")
        return sc_decode(metrics, field=field, alpha=ALPHA,
                         known_positions=kp, known_values=kv)

    def attempt(fn, *args, **kwargs):
        try:
            return {"raised": False, "result": fn(*args, **kwargs)}
        except Exception as exc:  # noqa: BLE001 — parity needs type+message
            return {"raised": True, "exc_type": type(exc).__name__, "message": str(exc)}

    t_all = time.perf_counter()
    rng = np.random.default_rng(FROZEN_SEED)
    primitive_cells: list = []
    full_sc: dict = {}
    v0_cases: list = []

    def fail(gate: str, detail: str = ""):
        raise GateBlocked(gate, detail)

    label = "EXACT_CHUNKED_SC_CANDIDATE"
    failed_gate = None
    try:
        # ---- Step 1a: primitive exact-chunked minus-node matrix.
        for rows in PRIM_ROWS:
            for kind in PRIM_KINDS:
                first, second = _gen_pair(rng, kind, rows)
                ref = orig_minus(first, second, index, chunk_rows=None)
                got = sc_mod._minus_block(first, second, index)
                both = np.isfinite(ref) & np.isfinite(got)
                cell = {
                    "rows": rows,
                    "kind": kind,
                    "exact_equal": bool(np.array_equal(ref, got)),
                    "max_finite_abs_err": float(np.abs(ref[both] - got[both]).max())
                    if both.any()
                    else None,
                    "support_equal": bool((np.isfinite(ref) == np.isfinite(got)).all()),
                    "support_mismatch_rows": int(
                        (np.isfinite(ref) != np.isfinite(got)).any(axis=1).sum()
                    ),
                }
                primitive_cells.append(cell)
                if not (cell["exact_equal"] and cell["support_equal"]):
                    fail("semantic_parity", f"primitive rows={rows} kind={kind}")

        # ---- Step 1b: V0 validation contract (identical type+message).
        base8 = np.zeros((8, Q), dtype=np.float64)
        nan_m = base8.copy()
        nan_m[0, 0] = np.nan
        pinf_m = base8.copy()
        pinf_m[1, 1] = np.inf
        row_m = base8.copy()
        row_m[2, :] = -np.inf
        V0 = [
            ("nan_entry", {"logp_x": nan_m}),
            ("posinf_entry", {"logp_x": pinf_m}),
            ("all_neginf_row", {"logp_x": row_m}),
            ("width_mismatch", {"logp_x": np.zeros((8, Q + 1))}),
            ("non_power_of_two_N", {"logp_x": np.zeros((48, Q))}),
            ("rank1_input", {"logp_x": np.zeros(Q)}),
            ("boolean_input", {"logp_x": np.zeros((8, Q), dtype=bool)}),
            ("positions_out_of_range", {"logp_x": base8, "kp": np.array([0, 99]),
                                        "kv": np.array([0, 0])}),
            ("positions_repeat", {"logp_x": base8, "kp": np.array([3, 3]),
                                  "kv": np.array([1, 2])}),
            ("positions_values_length", {"logp_x": base8, "kp": np.array([0, 1]),
                                         "kv": np.array([0])}),
            ("positions_none_values_given", {"logp_x": base8, "kp": None,
                                             "kv": np.array([0])}),
            ("positions_given_values_none", {"logp_x": base8, "kp": np.array([0]),
                                             "kv": None}),
            ("float_positions", {"logp_x": base8, "kp": np.array([0.5]),
                                 "kv": np.array([0])}),
            ("boolean_positions", {"logp_x": base8,
                                   "kp": np.array([True, False, True, False,
                                                   True, False, True, False]),
                                   "kv": np.zeros(8, dtype=np.int64)}),
            ("value_out_of_range", {"logp_x": base8, "kp": np.array([0]),
                                    "kv": np.array([32])}),
            ("negative_position", {"logp_x": base8, "kp": np.array([-1]),
                                   "kv": np.array([0])}),
        ]
        for name, kw in V0:
            att_d = attempt(run_direct, kw["logp_x"], kw.get("kp"), kw.get("kv"))
            if not att_d["raised"]:
                fail("semantic_parity", f"V0_{name} baseline did not raise")
            att_c = attempt(run_chunked, kw["logp_x"], kw.get("kp"), kw.get("kv"))
            par = bool(
                att_c["raised"]
                and att_c["exc_type"] == att_d["exc_type"]
                and att_c["message"] == att_d["message"]
            )
            v0_cases.append({"name": name, "baseline": _exc_summary(att_d),
                             "chunked": _exc_summary(att_c), "parity": par})
            if not par:
                fail("semantic_parity", f"V0_{name}")

        # ---- Step 1c: full-SC semantic controls at N=64 and N=256.
        for n in SC_NS:
            nrec: dict = {"N": n, "controls": {}}
            full_sc[str(n)] = nrec
            f1 = rng.uniform(-20.0, 0.0, (n, Q))
            f2 = rng.uniform(-160.0, 0.0, (n, Q))
            f3 = rng.uniform(-20.0, 0.0, (n, Q))
            for j in range(n):
                if j % 5 == 4:
                    f3[j, 0::2] = -np.inf
            pos = np.sort(rng.choice(n, n // 4, replace=False)).astype(np.int64)

            def check(cid, metrics, kp=None, kv=None):
                att_d = attempt(run_direct, metrics, kp, kv)
                if att_d["raised"]:
                    return {"control": cid, "direct": _exc_summary(att_d),
                            "chunked": None, "parity": False,
                            "note": "direct raised on valid control"}
                att_c = attempt(run_chunked, metrics, kp, kv)
                if att_c["raised"]:
                    return {"control": cid,
                            "direct": {"raised": False, "status": att_d["result"].status},
                            "chunked": _exc_summary(att_c), "parity": False}
                cmp = _cmp_results(att_d["result"], att_c["result"])
                return {"control": cid,
                        "direct": {"raised": False, "status": att_d["result"].status},
                        "comparison": cmp, "parity": _parity_ok(cmp)}

            for cid, metrics in (("F1_moderate", f1), ("F2_wide", f2),
                                 ("F3_neginf_jmod5_evenoff", f3)):
                entry = check(cid, metrics)
                nrec["controls"][cid] = entry
                if not entry["parity"]:
                    fail("semantic_parity", f"N={n} {cid}")

            att_free = attempt(run_direct, f1)
            if att_free["raised"]:
                fail("semantic_parity", f"N={n} K4 control not established")
            dm_free = np.asarray(att_free["result"].decision_metrics)
            v4 = np.array([int(np.argmax(dm_free[p])) for p in pos.tolist()], dtype=np.int64)
            if not all(bool(np.isfinite(dm_free[p, v])) for p, v in zip(pos.tolist(), v4.tolist())):
                fail("semantic_parity", f"N={n} K4 positive support not established")
            entry = check("K4_known25pct_positive_support", f1, pos, v4)
            nrec["controls"]["K4_known25pct_positive_support"] = entry
            if not entry["parity"]:
                fail("semantic_parity", f"N={n} K4")

            c3 = rng.uniform(-12.0, 0.0, (n, Q))
            for j in range(n):
                if j % 3 == 0:
                    c3[j, 1::2] = -np.inf
            att_c3 = attempt(run_direct, c3)
            if att_c3["raised"]:
                fail("semantic_parity", f"N={n} C3 control not established")
            dm_c3 = np.asarray(att_c3["result"].decision_metrics)
            v3 = np.array([int(np.argmax(dm_c3[p])) for p in pos.tolist()], dtype=np.int64)
            if not all(bool(np.isfinite(dm_c3[p, v])) for p, v in zip(pos.tolist(), v3.tolist())):
                fail("semantic_parity", f"N={n} C3 positive support not established")
            entry = check("C3_x11_pattern_positive_support", c3, pos, v3)
            nrec["controls"]["C3_x11_pattern_positive_support"] = entry
            if not entry["parity"]:
                fail("semantic_parity", f"N={n} C3")

            found = None
            attempts = 0
            for t in range(400):
                k = 16 if t < 200 else 32
                kk = k if k <= n else n // 2
                cpos = ((t * 7 + np.arange(kk) * 3) % n).astype(np.int64)
                cval = rng.integers(0, Q, kk).astype(np.int64)
                cbase = rng.uniform(-12.0, 0.0, (n, Q))
                for j in range(0, n, 2):
                    cbase[j, 1:] = -np.inf
                attempts += 1
                att_d = attempt(run_direct, cbase, cpos, cval)
                if att_d["raised"] and att_d["exc_type"] == "ImpossibleDisclosedValueError":
                    att_c = attempt(run_chunked, cbase, cpos, cval)
                    par = bool(
                        att_c["raised"]
                        and att_c["exc_type"] == att_d["exc_type"]
                        and att_c["message"] == att_d["message"]
                    )
                    found = {"control": "C4_impossible_disclosed_value",
                             "search_index_t": t, "k": kk,
                             "search_attempts": attempts,
                             "exception_type": "ImpossibleDisclosedValueError",
                             "direct_message": att_d["message"],
                             "chunked": _exc_summary(att_c), "parity": par}
                    break
                elif att_d["raised"]:
                    continue
            if found is None:
                fail("semantic_parity", f"N={n} C4 control not established")
            nrec["controls"]["C4_impossible_disclosed_value"] = found
            if not found["parity"]:
                fail("semantic_parity", f"N={n} C4")

            ties = {
                "exact_tie": np.zeros((n, Q), dtype=np.float64),
                "ramp": np.tile(np.arange(Q, dtype=np.float64) - 31.0, (n, 1)),
                "near_tie": np.tile(np.zeros(Q, dtype=np.float64), (n, 1)),
            }
            ties["near_tie"][:, 1] = -1e-9
            t5 = {}
            nrec["controls"]["T5_ties"] = t5
            for tname, blk in ties.items():
                entry = check("T5_" + tname, blk)
                t5[tname] = entry
                if not entry["parity"]:
                    fail("semantic_parity", f"N={n} T5_{tname}")

        # ---- Step 2: one paired N=65536 moderate all-finite block, direct first.
        paired_block = _normalize_rows(rng.uniform(-20.0, 0.0, (N_PAIRED, Q)))
        t2 = time.perf_counter()
        att_d2 = attempt(run_direct, paired_block)
        wall_direct = time.perf_counter() - t2
        if att_d2["raised"]:
            fail("paired_n65536_exact", f"direct raised: {_exc_summary(att_d2)}")
        t2 = time.perf_counter()
        att_c2 = attempt(run_chunked, paired_block)
        wall_chunked = time.perf_counter() - t2
        if att_c2["raised"]:
            fail("paired_n65536_exact", f"chunked raised: {_exc_summary(att_c2)}")
        cmp2 = _cmp_results(att_d2["result"], att_c2["result"])
        paired_record = {
            "N": N_PAIRED,
            "arm_order": "direct_before_chunked",
            "comparison": cmp2,
            "parity": _parity_ok(cmp2),
            "wall_s": {"direct": wall_direct, "chunked": wall_chunked},
            "rss_after": _rss_peak(),
        }
        if not paired_record["parity"]:
            fail("paired_n65536_exact", "comparison mismatch")

        # ---- Step 3: one default-512 N=262144 moderate all-finite block.
        large_block = _normalize_rows(rng.uniform(-20.0, 0.0, (N_LARGE, Q)))
        t3 = time.perf_counter()
        att_L = attempt(run_chunked, large_block)
        wall_large = time.perf_counter() - t3
        rss_large = _rss_peak()
        if att_L["raised"]:
            fail("large_n262144_completion", f"chunked raised: {_exc_summary(att_L)}")
        res_L = att_L["result"]
        finite_out = bool(
            np.isfinite(np.asarray(res_L.decision_metrics)).all()
            and np.isfinite(np.asarray(res_L.decision_log_scores)).all()
        )
        scaling_record = {
            "N": N_LARGE,
            "chunk_rows": FROZEN_CHUNK_ROWS,
            "status": res_L.status,
            "finite_outputs": finite_out,
            "wall_s": wall_large,
            "rss_bytes": rss_large,
            "rss_hard_limit_bytes": RSS_HARD_LIMIT_BYTES,
            "planning_targets_report_only": {
                "wall_s_target": WALL_PLAN_TARGET_S,
                "wall_s_met": bool(wall_large <= WALL_PLAN_TARGET_S),
                "rss_bytes_target": RSS_PLAN_TARGET_BYTES,
                "rss_bytes_met": bool((rss_large["peak_bytes"] or 0) <= RSS_PLAN_TARGET_BYTES),
            },
        }
        if res_L.status != "ok" or not finite_out:
            fail("large_n262144_completion", "status or finite-output check failed")
        if (rss_large["peak_bytes"] or 0) >= RSS_HARD_LIMIT_BYTES:
            fail("large_n262144_rss", f"peak {rss_large['peak_bytes']}")
    except GateBlocked as blocked:
        label = str(blocked)
        failed_gate = blocked.gate
        if "paired_record" not in dir():
            paired_record = None
        if "scaling_record" not in dir():
            scaling_record = None

    if sc_mod._minus_block is not orig_minus:
        raise RuntimeError("minus-block not restored at process end")
    wall_total = time.perf_counter() - t_all
    rss_final = _rss_peak()

    gates = {name: True for name in GATE_NAMES}
    if failed_gate is not None and failed_gate in gates:
        order = GATE_NAMES.index(failed_gate)
        for name in GATE_NAMES[order:]:
            gates[name] = False

    frozen_plan = {
        "packet": "NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC",
        "parameters": {
            "seed": FROZEN_SEED,
            "dtype": "float64",
            "q": Q,
            "alpha": ALPHA,
            "primitive_polynomial": PRIMITIVE_POLYNOMIAL,
            "chunk_rows": FROZEN_CHUNK_ROWS,
            "primitive_rows": PRIM_ROWS,
            "primitive_kinds": PRIM_KINDS,
            "full_sc_N": SC_NS,
            "paired_N": N_PAIRED,
            "large_N": N_LARGE,
            "arm_order_paired": "direct_before_chunked",
            "rng_stream_order": "primitives(rows asc x kinds)->V0(fixed)->N64 controls->N256 controls->N65536 block->N262144 block; C4 search draws data-dependent in count, stream-ordered",
        },
        "command": (
            "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && "
            "ulimit -v 2097152 && "
            "timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python "
            "-m comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc_chunked_gate "
            "--seed 2026091800 --chunk-rows 512 "
            "--out-dir .workbuddy/queue/NBPOLAR-PHASE4-P11-EXACT-CHUNKED-SC/exact_chunked_sc_gate"
        ),
        "environment": {
            "interpreter": sys.executable,
            "python": sys.version,
            "numpy": str(np.__version__),
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "attempt_accounting": {
            "attempts_allowed": 1,
            "attempts_consumed_before": 0,
            "attempts_consumed_by_this_run": 1,
            "consumption_point": ATTEMPT_CONSUMPTION_POINT,
            "artifact_reads_authorized": 0,
            "artifact_reads_consumed": 0,
            "no_reopen": NO_REOPEN_NOTE,
        },
        "gates": gates,
        "budgets": {
            "timeout_s": TIMEOUT_S,
            "vsz_kb": VSZ_KB,
            "rss_hard_limit_bytes": RSS_HARD_LIMIT_BYTES,
            "planning_wall_s_report_only": WALL_PLAN_TARGET_S,
            "planning_rss_bytes_report_only": RSS_PLAN_TARGET_BYTES,
        },
        "label": label,
    }
    equivalence_records = {
        "primitive_cells": primitive_cells,
        "primitive_totals": {
            "cells": len(primitive_cells),
            "all_exact": all(
                c["exact_equal"] and c["support_equal"] for c in primitive_cells
            ),
        },
        "validation_contract": v0_cases,
        "validation_totals": {
            "cases": len(v0_cases),
            "all_parity": all(c["parity"] for c in v0_cases),
        },
        "full_sc": full_sc,
        "paired_n65536": paired_record,
    }
    scaling_out = {
        "scaling_record": scaling_record,
        "wall_total_s": wall_total,
        "rss_final": rss_final,
    }

    lines = [
        "# P11 exact chunked SC gate report",
        "",
        f"label: {label}",
        f"seed: {FROZEN_SEED}; float64; GF({Q}) poly {PRIMITIVE_POLYNOMIAL} alpha {ALPHA}; "
        f"chunk_rows {FROZEN_CHUNK_ROWS} vs None",
        f"attempts: 1 allowed / 1 consumed at {ATTEMPT_CONSUMPTION_POINT}",
        f"artifact reads: 0 authorized / 0 consumed. {NO_REOPEN_NOTE}.",
        f"wall_total_s: {wall_total:.3f} (timeout {TIMEOUT_S} s); "
        f"rss_final_peak_bytes: {rss_final['peak_bytes']}",
        "",
        "## Step 1: semantic matrix (default-512 vs None)",
        f"primitive cells: {len(primitive_cells)}, "
        f"all_exact: {equivalence_records['primitive_totals']['all_exact']}",
    ]
    for cell in primitive_cells:
        lines.append(
            f"prim rows={cell['rows']} kind={cell['kind']} "
            f"exact={cell['exact_equal']} support={cell['support_equal']} "
            f"max_finite_abs_err={cell['max_finite_abs_err']} "
            f"support_mismatch_rows={cell['support_mismatch_rows']}"
        )
    lines.append(
        f"V0 cases: {len(v0_cases)}, "
        f"all_parity: {equivalence_records['validation_totals']['all_parity']}"
    )
    for case in v0_cases:
        lines.append(
            f"V0 {case['name']} baseline={case['baseline']['exc_type']}: "
            f"{case['baseline']['message']} parity={case['parity']}"
        )
    for nkey, nrec in full_sc.items():
        for cid, entry in nrec["controls"].items():
            if cid == "T5_ties":
                for tname, tentry in entry.items():
                    lines.append(f"N={nkey} T5_{tname} parity={tentry['parity']}")
            else:
                lines.append(f"N={nkey} {cid} parity={entry['parity']}")
    lines.append("")
    lines.append("## Step 2: paired N=65536 (direct first, then default-512)")
    if paired_record is None:
        lines.append("paired record: none (gate blocked before completion)")
    else:
        cmp = paired_record["comparison"]
        lines.append(
            f"parity={paired_record['parity']} status={cmp['status']} "
            f"u_hat_exact={cmp['u_hat_exact']} u_mismatches={cmp['u_hat_mismatches']} "
            f"x_hat_exact={cmp['x_hat_exact']} x_mismatches={cmp['x_hat_mismatches']} "
            f"metrics_exact={cmp['metrics_exact']} "
            f"max_finite_metric_abs_err={cmp['max_finite_metric_abs_err']} "
            f"support_equal={cmp['metrics_support_equal']} "
            f"argmax_mismatches={cmp['metrics_argmax_mismatches']} "
            f"scores_exact={cmp['scores_exact']} "
            f"max_finite_score_abs_err={cmp['max_finite_score_abs_err']} "
            f"known_mask_exact={cmp['known_mask_exact']} "
            f"known_count_equal={cmp['known_count_equal']} "
            f"provenance_equal={cmp['provenance_equal']}"
        )
        lines.append(
            f"wall_s direct={paired_record['wall_s']['direct']:.3f} "
            f"chunked={paired_record['wall_s']['chunked']:.3f}; "
            f"rss_peak_bytes={paired_record['rss_after']['peak_bytes']}"
        )
    lines.append("")
    lines.append("## Step 3: N=262144 default-512 completion and resources")
    if scaling_record is None:
        lines.append("scaling record: none (gate blocked before completion)")
    else:
        lines.append(
            f"status={scaling_record['status']} "
            f"finite_outputs={scaling_record['finite_outputs']} "
            f"wall_s={scaling_record['wall_s']:.3f} "
            f"(planning target <={WALL_PLAN_TARGET_S} s report-only) "
            f"rss_peak_bytes={scaling_record['rss_bytes']['peak_bytes']} "
            f"(hard limit {RSS_HARD_LIMIT_BYTES}; "
            f"planning target {RSS_PLAN_TARGET_BYTES} report-only)"
        )
    lines.append("")
    lines.append("## Gates")
    for name in GATE_NAMES:
        lines.append(f"{name}: {gates[name]}")
    lines.append("")
    lines.append("## Bounded wording")
    lines.append(
        "A candidate means the default-512 allocation path is bitwise-equivalent "
        "to the accepted unchunked reference everywhere in the frozen matrix and "
        "completes the single N=262144 block within the frozen resource envelope. "
        "One draw cannot discriminate timing variance: no throughput superiority "
        "claim is allowed, and the 120 s / 1 GiB values are report-only. This is "
        "not target-channel FER, efficiency, key-rate, scaling, qualification or "
        "promotion evidence; a candidate remains pending main-thread acceptance."
    )
    lines.append(
        "Outputs persist no input vectors, decisions, metrics, decoded keys, raw "
        "arrays or artifacts: only parameters, environment, equality/exception "
        "parities, counts, error magnitudes, walls, RSS, accounting and gates."
    )
    report = "\n".join(lines) + "\n"

    out_path.mkdir(parents=True, exist_ok=False)
    (out_path / "frozen_plan.json").write_text(json.dumps(frozen_plan, indent=1) + "\n")
    (out_path / "equivalence_records.json").write_text(
        json.dumps(equivalence_records, indent=1) + "\n"
    )
    (out_path / "scaling_record.json").write_text(json.dumps(scaling_out, indent=1) + "\n")
    (out_path / "report.md").write_text(report)
    written = sorted(p.name for p in out_path.iterdir())
    if written != sorted(FOUR_FILES):
        raise RuntimeError(f"output root must contain exactly {FOUR_FILES}, got {written}")
    return {"label": label, "out_dir": str(out_path), "files": written,
            "wall_total_s": wall_total}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-chunked-sc-gate",
        description="NB-Polar Phase 4-P11 exact chunked SC synthetic engineering gate",
    )
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--chunk-rows", required=True, type=int, dest="chunk_rows")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_chunked_gate(seed=args.seed, chunk_rows=args.chunk_rows,
                               out_dir=args.out_dir)
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p11 chunked sc gate refused: {exc}", file=sys.stderr)
        return 2
    except GateBlocked as blocked:
        # Unreachable: run_chunked_gate converts blocks into BLOCKED labels
        # inside the four files; this guards future refactors.
        print(f"nbpolar phase4-p11 chunked sc gate {blocked}", file=sys.stderr)
        return 1
    except Exception:  # noqa: BLE001 — never lose the traceback on unexpected failure
        traceback.print_exc()
        return 3
    print(json.dumps({"label": run["label"], "files": run["files"],
                      "wall_total_s": run["wall_total_s"]}))
    return 0 if run["label"] == "EXACT_CHUNKED_SC_CANDIDATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
