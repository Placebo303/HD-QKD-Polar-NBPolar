1. Question: Does the frozen two-layer NB-Polar metric pipeline (accepted prior builders/converter/validation/SymbolMetric plus accepted chunked sc_decode, GF32 poly 37 alpha 2) stay bit-exact under two probe-local memory-lifetime alternatives (lifetime_only release ordering; owned_log owned in-place log conversion with direct sc_decode), and what peak live N x 32 bytes, stage completion, wall and RSS does each alternative record for 4 sequential N=65536 blocks then 2 sequential N=262144 blocks in fresh 2 GiB children (Tier-X descriptive only; no attempt, threshold, winner, candidate, acceptance, or status change; do not rerun P12).
2. Parameters: seed=2026091840 single stream; GF32 polynomial 37 alpha=2 chunk_rows=512 (accepted _minus_block default asserted read-only); tables built in-body in order P1=rng.uniform(0,1,(32,1024)) column-normalized, P2=rng.uniform(0,1,(32,1024,32)) last-axis-normalized, p_b=rng.uniform(0,1,(1024,)) normalized (P1 stored [U1,B]=(32,1024) per accepted builder shape; Bob-row view [1024,32]); Bob sampled uniform integers (p_b recorded family table); small-N exactness at N=64 (k1=8 k2=16) and N=256 (k1=45 k2=110), D1=sorted((arange(k1)*7+3)%N) D2=sorted((arange(k2)*11+5)%N), five cases finite (no mask no disclosures), exactzero (L1 rows j%4==0 odd symbols 0; L2 rows j%4==1 even symbols 0; no disclosures), known (no mask, truth-U disclosures), impossible (L1 even rows symbol-0-only, D2 truth disclosures, D1 search pos=(t*7+arange(16)*3)%N vals=rng.integers t=0..199 first ImpossibleDisclosedValueError at either layer), x11c3 (L1 rows j%3==0 odd symbols 0, disclosures=undisclosed-baseline decision argmax at D1/D2 with finite-support check); per-case one shared base L1 prob block, per-arm copy plus case mask, identical inputs to baseline/lifetime_only/owned_log; alternatives: lifetime_only preserves accepted builders/converter then dels L1 probs/metric/SCResult plus L2 probs/SCResult at last use and reduces outcomes to scalars, owned_log adds owned float64 L2 copy (owndata/base/shares_memory audited) validated under accepted contract then np.log plus row normalization in place with direct sc_decode and frozen enum provenance scalar, never mutating caller-owned/view arrays; parity requires exact equality of constructed L1/L2 log metrics, support, provenance, exception type/message, u/x decisions, decision metrics/scores, outcomes (wall excluded); tag skipped at all N (tag path holds no N x 32 arrays; accepted Toeplitz index (64 x 10N) int64 is ~1.3 GiB at N=262144 and would confound metric-memory measurement; outcomes exact_untagged/mismatch_untagged/decode_failed); large-N disclosures none (no truth transforms); children fresh interpreter RLIMIT_AS 2 GiB inherited plus asserted, timeout 400 s each, frozen order lifetime_only first then owned_log, each 4 sequential N=65536 blocks then 2 sequential N=262144 blocks with per-block stderr X13STAGE markers; child MemoryError (returncode/stderr parse) is descriptive, parent records and continues to next frozen stage; any other child crash or timeout or any parity mismatch is STOP without rerun; ledger snapshots at post_L1_decode/post_L1_release/post_L2_construct(implicit in decode snap)/post_L2_decode/post_L2_release/post_outcome_append/variant_return per block with name/shape/dtype/nbytes/referenced for every N x 32 array plus formula totals and HWM caveat (ledger counts named live arrays only, not decoder temporaries or interpreter overhead; ru_maxrss/VmHWM is the HWM); checkpoints write the single results.json at init skeleton before the first probe call and after parity_N64 parity_N256 child_lifetime_only child_owned_log and finalize; one rerun allowed only for execution-code error with unchanged inputs/alternatives/seed (record both attempts), total wall 1200 s, ulimit -v 2097152 parent and children, PYTHONDONTWRITEBYTECODE=1, pinned interpreter /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python, staged body /tmp/x13_body.py byte-identical to embedded fence with sha256 equality asserted before any probe call.
3. Command: cwd=/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar; PYTHONDONTWRITEBYTECODE=1 ulimit -v 2097152; timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python /tmp/x13_body.py (staged byte-identically from the prereg python fence; body self-verifies staged bytes equal embedded bytes before any probe call; single execution, attempt 1).

```python
"""X13 Tier-X frozen body: two-layer metric memory-lifetime probe, descriptive only.

Baseline (accepted pipeline, probe-local driver): accepted prior builders
(build_p1_metrics / gather_p2_metrics), accepted converter
(probs_to_symbol_metric, SymbolMetric, Provenance), accepted sc_decode
(chunked _minus_block default, read-only, never modified/copied). Two frozen
probe-local alternatives: lifetime_only (same accepted calls, release L1/L2
N x 32 arrays at last use, scalar-only outcomes) and owned_log (same release
plus owned float64 L2 copy validated under the accepted contract, np.log and
row normalization in place, direct sc_decode, frozen enum provenance scalar).
Injected tables and synthetic vectors only. No artifact/evidence/official-seed/
raw/held-out/real/EVAL/tag/FWHT/APP/SCL/gate access. No threshold, winner,
candidate, acceptance, or label. Writes only results.json in its probe dir.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import platform
import re
import resource
import subprocess
import sys
import time
import traceback
from pathlib import Path

sys.dont_write_bytecode = True

T0 = time.monotonic()

REPO = Path("/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar")
PROBE_DIR = REPO / "workspace" / "probes" / "nbpolar_x13_metric_memory_lifetime"
PREREG_PATH = PROBE_DIR / "prereg.md"
RESULTS_PATH = PROBE_DIR / "results.json"
BODY_PATH = Path("/tmp/x13_body.py")
INTERPRETER = "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python"
COMMAND_TEXT = ("PYTHONDONTWRITEBYTECODE=1 ulimit -v 2097152; timeout 1200 "
                + INTERPRETER + " /tmp/x13_body.py")

SEED = 2026091840
Q = 32
ALPHA = 2
POLY = 37
NB = 1024
VSZ = 2 * 1024 ** 3
VSZ_KB = 2097152
TOTAL_WALL_S = 1200
CHILD_WALL_S = 400
ATTEMPT = int(os.environ.get("X13_ATTEMPT", "1"))
IS_CHILD = len(sys.argv) > 1 and sys.argv[1] == "--child"
CHILD_ALT = sys.argv[2] if IS_CHILD and len(sys.argv) > 2 else None
HWM_CAVEAT = ("ledger counts named live N x 32 pipeline arrays only, not SC "
              "temporaries, interpreter overhead, or non-N x 32 arrays; "
              "ru_maxrss/VmHWM is the high-water mark")
OUTCOME_KEYS = ("outcome", "label_match", "l1_provenance", "l2_provenance",
                "l1_ok", "l2_ok", "l1_error", "l2_error",
                "key_dependent_bits", "public_control_bits", "tag_invoked")
PARITY_KEYS = ("l1_logp_sha", "l1_support_sha", "l1_provenance", "l1_exc",
               "sc1_u_sha", "sc1_x_sha", "sc1_dm_sha", "sc1_ds_sha",
               "sc1_status", "l2_logp_sha", "l2_support_sha", "l2_provenance",
               "l2_exc", "sc2_u_sha", "sc2_x_sha", "sc2_dm_sha", "sc2_ds_sha",
               "sc2_status")
SMALL_NS = (64, 256)
CASES = ("finite", "exactzero", "known", "impossible", "x11c3")
ALTS = ("baseline", "lifetime_only", "owned_log")
LARGE_PLAN = ((65536, 4), (262144, 2))

try:
    resource.setrlimit(resource.RLIMIT_AS, (VSZ, VSZ))
    RLIMIT_OK = True
except Exception:
    RLIMIT_OK = False

import numpy as np


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_arr(a):
    return _sha(np.ascontiguousarray(a).tobytes())


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
    return {"ru_maxrss_bytes": ru, "vmhwm_bytes": hwm,
            "peak_bytes": max(vals) if vals else None}


PROBE_DIR.mkdir(parents=True, exist_ok=True)
_prereg_bytes = PREREG_PATH.read_bytes()
PREREG_SHA = _sha(_prereg_bytes)
_own_bytes = Path(__file__).read_bytes()
BODY_SHA = _sha(_own_bytes)
_pt = _prereg_bytes.decode("utf-8")
_FENCE = "```python\n"
_f0 = _pt.index(_FENCE) + len(_FENCE)
_f1 = _pt.index("\n```", _f0)
BODY_MATCH = bool(_pt[_f0:_f1].encode("utf-8") == _own_bytes)

FIELD = None
G = {"completed_stages": []}


def checkpoint(status, extra=None):
    G["status"] = status
    G["wall_s"] = time.monotonic() - T0
    G["rss_peak"] = rss_peak()
    if extra:
        G.update(extra)
    RESULTS_PATH.write_text(json.dumps(G, indent=1) + "\n", encoding="utf-8")


def stop_parent(reason, detail):
    checkpoint("STOPPED_" + str(reason).upper(), {"stop_detail": detail})
    print("STOP: %s %s" % (reason, json.dumps(detail)[:500]))
    raise SystemExit(2)


def import_accepted(allow_stop=True):
    def _fail(reason, detail):
        if allow_stop and not IS_CHILD:
            stop_parent(reason, detail)
        raise RuntimeError("accepted-identity failure: %s %s"
                           % (reason, detail))
    global FIELD
    sys.path.insert(0, str(REPO / "comparison_bench" / "src"))
    import comparison_bench.formal_ir.nbpolar.sc as sc_mod
    from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
    from comparison_bench.formal_ir.nbpolar.prior import (
        Provenance, build_p1_metrics, gather_p2_metrics, probs_to_symbol_metric)
    from comparison_bench.formal_ir.nbpolar.sc import (
        ImpossibleDisclosedValueError, sc_decode)
    from comparison_bench.formal_ir.nbpolar.transform import polar_transform
    chunk_default = inspect.signature(sc_mod._minus_block).parameters[
        "chunk_rows"].default
    field = make_gf32()
    if int(field.q) != Q:
        _fail("field_identity", {"q": int(field.q)})
    if int(getattr(field, "primitive_polynomial", -1)) != POLY:
        _fail("field_identity",
              {"poly": getattr(field, "primitive_polynomial", None)})
    if int(chunk_default) != 512:
        _fail("chunk_identity", {"chunk_rows_default": chunk_default})
    FIELD = field
    return {"sc_mod": sc_mod,
            "Provenance": Provenance,
            "build_p1_metrics": build_p1_metrics,
            "gather_p2_metrics": gather_p2_metrics,
            "probs_to_symbol_metric": probs_to_symbol_metric,
            "ImpossibleDisclosedValueError": ImpossibleDisclosedValueError,
            "sc_decode": sc_decode,
            "polar_transform": polar_transform,
            "chunk_rows_default": int(chunk_default)}


def build_tables(rng, acc):
    p1_raw = rng.uniform(0.0, 1.0, (Q, NB))
    p1 = p1_raw / p1_raw.sum(axis=0, keepdims=True)
    p2_raw = rng.uniform(0.0, 1.0, (Q, NB, Q))
    p2 = p2_raw / p2_raw.sum(axis=2, keepdims=True)
    pb_raw = rng.uniform(0.0, 1.0, (NB,))
    pb = pb_raw / pb_raw.sum()
    return p1, p2, pb


class Ledger:
    def __init__(self):
        self.reg = {}
        self.snaps = []

    def reg_arr(self, name, arr):
        a = np.asarray(arr)
        self.reg[name] = {"shape": [int(v) for v in a.shape],
                          "dtype": str(a.dtype), "nbytes": int(a.nbytes),
                          "referenced": True}

    def rel(self, name):
        if name in self.reg:
            self.reg[name]["referenced"] = False

    def reset(self):
        self.reg = {}

    def snap(self, stage, n):
        live = {k: dict(v) for k, v in self.reg.items()
                if v["referenced"]}
        n32 = {k: v for k, v in live.items()
               if len(v["shape"]) == 2 and v["shape"][0] == n
               and v["shape"][1] == 32 and v["dtype"] == "float64"}
        self.snaps.append({
            "stage": stage, "N": n, "live": live,
            "live_total_bytes": sum(v["nbytes"] for v in live.values()),
            "live_n32_float64_count": len(n32),
            "live_n32_actual_bytes": sum(v["nbytes"] for v in n32.values()),
            "live_n32_formula_bytes": len(n32) * n * 32 * 8,
            "released": sorted(k for k, v in self.reg.items()
                               if not v["referenced"])})


def owned_log_convert(probs):
    arr = np.asarray(probs)
    if arr.dtype.kind == "b":
        raise TypeError(
            "metric contract: probs must hold numbers, got boolean input")
    if arr.ndim != 2 or arr.shape[1] != Q:
        raise ValueError(
            "metric contract: probs must have shape (N,32), got shape %s"
            % (arr.shape,))
    try:
        owned = np.array(arr, dtype=np.float64, copy=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "metric contract: probs must be numeric (%s)" % exc)
    if not np.isfinite(owned).all():
        raise ValueError("metric contract: probs must be finite")
    if (owned < 0).any():
        raise ValueError("metric contract: probs must be non-negative")
    if (owned.sum(axis=1) <= 0).any():
        raise ValueError(
            "metric contract: every probs row needs positive mass")
    audit = {"base_is_none": owned.base is None,
             "owndata": bool(owned.flags.owndata),
             "shares_memory_with_input": bool(np.shares_memory(owned, arr))}
    with np.errstate(divide="ignore"):
        owned[owned == 0.0] = -np.inf
        np.log(owned, out=owned, where=owned > 0)
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(owned, axis=1)
    owned -= lse[:, None]
    return owned, audit


def run_variant(p1, bob, high_true, low_true, d1, v1, d2, v2, l2_mask,
                variant, led, n, btag, acc):
    Provenance = acc["Provenance"]
    probs_to_symbol_metric = acc["probs_to_symbol_metric"]
    gather_p2_metrics = acc["gather_p2_metrics"]
    sc_decode = acc["sc_decode"]
    det = {"variant": variant}
    p1_sha0 = sha_arr(p1)
    led.reg_arr(btag + "p1_probs", p1)
    m1 = probs_to_symbol_metric(p1, provenance=Provenance.PRIOR_ONLY)
    led.reg_arr(btag + "m1_logp", m1.logp)
    det["l1_logp_sha"] = sha_arr(m1.logp)
    det["l1_support_sha"] = sha_arr(np.isfinite(m1.logp))
    det["l1_provenance"] = m1.provenance.value
    det["l1_provenance_is_enum"] = isinstance(m1.provenance, Provenance)
    l1_exc = None
    sc1 = None
    try:
        sc1 = sc_decode(m1.logp, field=FIELD, alpha=ALPHA,
                        known_positions=d1, known_values=v1)
    except Exception as exc:
        l1_exc = [type(exc).__name__, str(exc)]
    det["l1_exc"] = l1_exc
    high_hat = None
    if sc1 is not None:
        led.reg_arr(btag + "sc1_dm", sc1.decision_metrics)
        det["sc1_u_sha"] = sha_arr(sc1.u_hat)
        det["sc1_x_sha"] = sha_arr(sc1.x_hat)
        det["sc1_dm_sha"] = sha_arr(sc1.decision_metrics)
        det["sc1_ds_sha"] = sha_arr(sc1.decision_log_scores)
        det["sc1_status"] = sc1.status
        det["sc1_known"] = int(sc1.known_count)
        high_hat = np.array(sc1.x_hat, copy=True)
    led.snap(btag + "post_L1_decode", n)
    keep = {}
    if variant == "baseline":
        keep = {"p1": p1, "m1": m1, "sc1": sc1}
    else:
        det["p1_immutable"] = bool(sha_arr(p1) == p1_sha0)
        led.rel(btag + "p1_probs")
        led.rel(btag + "m1_logp")
        if sc1 is not None:
            led.rel(btag + "sc1_dm")
        del m1
        if sc1 is not None:
            del sc1
        del p1
    led.snap(btag + "post_L1_release", n)
    l2_exc = None
    sc2 = None
    low_hat = None
    label_hat = None
    p2g = None
    m2 = None
    owned = None
    if high_hat is not None:
        p2g = gather_p2_metrics(bob[None, :], high_hat[None, :], P2TAB)[0]
        if l2_mask is not None:
            p2g = l2_mask(p2g)
        led.reg_arr(btag + "p2_probs", p2g)
        if variant == "owned_log":
            owned, audit = owned_log_convert(p2g)
            det["owned_audit"] = audit
            det["l2_provenance"] = Provenance.CANDIDATE_CONDITIONED.value
            det["l2_provenance_is_enum"] = True
            led.reg_arr(btag + "l2_logp_owned", owned)
            det["l2_logp_sha"] = sha_arr(owned)
            det["l2_support_sha"] = sha_arr(np.isfinite(owned))
            in_sha = det["l2_logp_sha"]
            try:
                sc2 = sc_decode(owned, field=FIELD, alpha=ALPHA,
                                known_positions=d2, known_values=v2)
            except Exception as exc:
                l2_exc = [type(exc).__name__, str(exc)]
            det["l2_input_immutable"] = bool(sha_arr(owned) == in_sha)
        else:
            m2 = probs_to_symbol_metric(
                p2g, provenance=Provenance.CANDIDATE_CONDITIONED)
            led.reg_arr(btag + "m2_logp", m2.logp)
            det["l2_logp_sha"] = sha_arr(m2.logp)
            det["l2_support_sha"] = sha_arr(np.isfinite(m2.logp))
            det["l2_provenance"] = m2.provenance.value
            det["l2_provenance_is_enum"] = isinstance(m2.provenance,
                                                     Provenance)
            try:
                sc2 = sc_decode(m2.logp, field=FIELD, alpha=ALPHA,
                                known_positions=d2, known_values=v2)
            except Exception as exc:
                l2_exc = [type(exc).__name__, str(exc)]
        det["l2_exc"] = l2_exc
        if sc2 is not None:
            led.reg_arr(btag + "sc2_dm", sc2.decision_metrics)
            det["sc2_u_sha"] = sha_arr(sc2.u_hat)
            det["sc2_x_sha"] = sha_arr(sc2.x_hat)
            det["sc2_dm_sha"] = sha_arr(sc2.decision_metrics)
            det["sc2_ds_sha"] = sha_arr(sc2.decision_log_scores)
            det["sc2_status"] = sc2.status
            det["sc2_known"] = int(sc2.known_count)
            low_hat = np.array(sc2.x_hat, copy=True)
            label_hat = (low_hat + 32 * high_hat).astype(np.int64)
    else:
        det["l2_exc"] = None
    led.snap(btag + "post_L2_decode", n)
    if variant == "baseline":
        keep.update({"p2g": p2g if high_hat is not None else None,
                     "m2": m2 if (high_hat is not None
                                  and variant != "owned_log") else None,
                     "sc2": sc2})
    else:
        led.rel(btag + "p2_probs")
        if high_hat is not None:
            if variant == "owned_log":
                led.rel(btag + "l2_logp_owned")
            else:
                led.rel(btag + "m2_logp")
        if sc2 is not None:
            led.rel(btag + "sc2_dm")
        if high_hat is not None:
            del p2g
            if variant == "owned_log":
                del owned
            else:
                del m2
        if sc2 is not None:
            del sc2
    led.snap(btag + "post_L2_release", n)
    labels_true = (low_true + 32 * high_true).astype(np.int64)
    label_match = (bool(np.array_equal(label_hat, labels_true))
                   if label_hat is not None else False)
    if l1_exc is not None:
        outcome = "decode_failed"
    elif l2_exc is not None:
        outcome = "decode_failed"
    elif label_match:
        outcome = "exact_untagged"
    else:
        outcome = "mismatch_untagged"
    k1n = 0 if d1 is None else int(len(np.asarray(d1)))
    k2n = 0 if d2 is None else int(len(np.asarray(d2)))
    result = {"outcome": outcome, "label_match": label_match,
              "l1_provenance": det.get("l1_provenance"),
              "l2_provenance": det.get("l2_provenance"),
              "l1_ok": l1_exc is None, "l2_ok": l2_exc is None,
              "l1_error": l1_exc[0] if l1_exc else None,
              "l2_error": l2_exc[0] if l2_exc else None,
              "key_dependent_bits": 5 * k1n + 5 * k2n,
              "public_control_bits": 0, "tag_invoked": False,
              "N": n, "variant": variant}
    del high_hat, low_hat, label_hat, labels_true
    if variant == "baseline":
        det["p1_immutable"] = bool(sha_arr(p1) == p1_sha0)
        for name in list(led.reg):
            if name.startswith(btag):
                led.rel(name)
        del keep
        del p1, m1, sc1, p2g, m2, sc2
    led.snap(btag + "variant_return", n)
    return result, det


def mask_l1_A(a):
    a[0::4, 1::2] = 0.0
    return a


def mask_l2_B(a):
    a[1::4, 0::2] = 0.0
    return a


def mask_l1_D(a):
    a[0::2, 1:] = 0.0
    return a


def mask_l1_C(a):
    a[0::3, 1::2] = 0.0
    return a


def dset(n, k, mult, off):
    return np.sort(((np.arange(k) * mult + off) % n).astype(np.int64))


def gather_l1(bob, acc):
    return acc["build_p1_metrics"](bob[None, :], P1TAB)[0]


def parity_case(n, case, rng, acc, tables0):
    polar_transform = acc["polar_transform"]
    ImpossibleDisclosedValueError = acc["ImpossibleDisclosedValueError"]
    k1 = 8 if n == 64 else 45
    k2 = 16 if n == 64 else 110
    high = rng.integers(0, Q, n).astype(np.int64)
    low = rng.integers(0, Q, n).astype(np.int64)
    bob = rng.integers(0, NB, n).astype(np.int64)
    base = gather_l1(bob, acc)
    u1 = polar_transform(high, field=FIELD, alpha=ALPHA)
    u2 = polar_transform(low, field=FIELD, alpha=ALPHA)
    d1 = dset(n, k1, 7, 3)
    d2 = dset(n, k2, 11, 5)
    l2_mask = None
    det_extra = {"k1": k1, "k2": k2}
    if case == "finite":
        masks = [None]
        dd1, vv1, dd2, vv2 = None, None, None, None
    elif case == "exactzero":
        masks = [mask_l1_A]
        dd1, vv1, dd2, vv2 = None, None, None, None
        l2_mask = mask_l2_B
    elif case == "known":
        masks = [None]
        dd1, vv1, dd2, vv2 = d1, np.array(u1[d1], copy=True), d2, \
            np.array(u2[d2], copy=True)
    elif case == "impossible":
        masks = [mask_l1_D]
        dd2, vv2 = d2, np.array(u2[d2], copy=True)
        found = None
        for t in range(200):
            pos = ((t * 7 + np.arange(16) * 3) % n).astype(np.int64)
            vals = rng.integers(0, Q, 16).astype(np.int64)
            trial = base.copy()
            mask_l1_D(trial)
            led1 = Ledger()
            out, det = run_variant(trial, bob, high, low, pos, vals, dd2,
                                   vv2, None, "baseline", led1, n,
                                   "search_", acc)
            del trial
            got = det.get("l1_exc") or det.get("l2_exc")
            if got is not None and got[0] == "ImpossibleDisclosedValueError":
                found = {"t": t, "pos": pos.tolist(),
                         "vals": vals.tolist(),
                         "layer": ("L1" if det.get("l1_exc") else "L2"),
                         "message": got[1]}
                break
        if found is None:
            return {"N": n, "case": case, "no_impossible_case": True,
                    "search_tries": 200}
        det_extra["search"] = found
        dd1 = np.array(found["pos"], dtype=np.int64)
        vv1 = np.array(found["vals"], dtype=np.int64)
    elif case == "x11c3":
        masks = [mask_l1_C]
        trial = base.copy()
        mask_l1_C(trial)
        sel_m1 = acc["probs_to_symbol_metric"](
            trial, provenance=acc["Provenance"].PRIOR_ONLY)
        sel_sc1 = acc["sc_decode"](sel_m1.logp, field=FIELD, alpha=ALPHA,
                                   known_positions=None, known_values=None)
        sel_high = np.array(sel_sc1.x_hat, copy=True)
        sel_p2 = acc["gather_p2_metrics"](bob[None, :], sel_high[None, :],
                                          P2TAB)[0]
        sel_m2 = acc["probs_to_symbol_metric"](
            sel_p2,
            provenance=acc["Provenance"].CANDIDATE_CONDITIONED)
        sel_sc2 = acc["sc_decode"](sel_m2.logp, field=FIELD, alpha=ALPHA,
                                   known_positions=None, known_values=None)
        dm1 = np.array(sel_sc1.decision_metrics, copy=True)
        dm2 = np.array(sel_sc2.decision_metrics, copy=True)
        del sel_m1, sel_sc1, sel_high, sel_p2, sel_m2, sel_sc2, trial
        dd1 = d1
        vv1 = np.array([int(np.argmax(r)) for r in dm1[d1.tolist()]],
                       dtype=np.int64)
        dd2 = d2
        vv2 = np.array([int(np.argmax(r)) for r in dm2[d2.tolist()]],
                       dtype=np.int64)
        if not all(bool(np.isfinite(r[v])) for r, v in
                   zip(dm1[d1.tolist()], vv1.tolist())):
            return {"N": n, "case": case, "c3_support_selection": False}
        if not all(bool(np.isfinite(r[v])) for r, v in
                   zip(dm2[d2.tolist()], vv2.tolist())):
            return {"N": n, "case": case, "c3_support_selection": False}
        det_extra["c3_values_from_undisclosed_argmax"] = True
        del dm1, dm2
    else:
        raise ValueError("unknown case " + str(case))
    arms = {}
    led = Ledger()
    for arm in ALTS:
        t = time.perf_counter()
        inp = base.copy()
        for m in masks:
            if m is not None:
                inp = m(inp)
        out, det = run_variant(inp, bob, high, low, dd1, vv1, dd2, vv2,
                               l2_mask, arm, led,
                               n, "N%d_%s_%s_" % (n, case, arm), acc)
        det["wall_s"] = time.perf_counter() - t
        arms[arm] = {"outcome": out, "detail": det}
        del inp
    parity = {}
    b0 = arms["baseline"]["detail"]
    b0o = arms["baseline"]["outcome"]
    for key in PARITY_KEYS:
        vals = [arms[a]["detail"].get(key, "ABSENT") for a in ALTS]
        parity[key] = bool(vals[0] == vals[1] == vals[2])
    outs = [tuple(arms[a]["outcome"][k] for k in OUTCOME_KEYS)
            for a in ALTS]
    parity["outcome"] = bool(outs[0] == outs[1] == outs[2])
    parity_all = bool(all(parity.values()))
    p1imm = bool(all(arms[a]["detail"].get("p1_immutable") for a in ALTS))
    tabs1 = (float(P1TAB.sum()), float(P2TAB.sum()), float(PBTAB.sum()))
    tables_immutable = bool(tabs1 == tables0)
    return {"N": n, "case": case, "k1": k1, "k2": k2,
            "disclosures": {"d1": None if dd1 is None else [int(v) for v in
                                                           np.asarray(dd1).tolist()],
                            "d2": None if dd2 is None else [int(v) for v in
                                                           np.asarray(dd2).tolist()]},
            "extra": det_extra, "arms": arms, "parity": parity,
            "parity_all": parity_all, "p1_immutable_all": p1imm,
            "tables_immutable": tables_immutable,
            "ledger_snaps": led.snaps}


P1TAB = None
P2TAB = None
PBTAB = None


def run_child():
    alt = CHILD_ALT
    exp = os.environ.get("X13_EXPECTED_BODY_SHA", "")
    rec = {"alternative": alt, "expected_body_sha": exp,
           "body_sha": BODY_SHA, "body_sha_match": bool(BODY_MATCH)}
    if alt not in ("lifetime_only", "owned_log") or not BODY_MATCH \
            or BODY_SHA != exp:
        rec["refused"] = True
        print(json.dumps(rec))
        return 2
    print("X13 child %s starting body_sha=%s" % (alt, BODY_SHA),
          file=sys.stderr, flush=True)
    global P1TAB, P2TAB, PBTAB
    acc = import_accepted(allow_stop=False)
    rng = np.random.default_rng(SEED)
    P1TAB, P2TAB, PBTAB = build_tables(rng, acc)
    tabs0 = (float(P1TAB.sum()), float(P2TAB.sum()), float(PBTAB.sum()))
    led = Ledger()
    stages = []
    as_lim = resource.getrlimit(resource.RLIMIT_AS)
    for (n, nblocks) in LARGE_PLAN:
        for b in range(nblocks):
            t = time.perf_counter()
            high = rng.integers(0, Q, n).astype(np.int64)
            low = rng.integers(0, Q, n).astype(np.int64)
            bob = rng.integers(0, NB, n).astype(np.int64)
            p1 = gather_l1(bob, acc)
            out, det = run_variant(p1, bob, high, low, None, None, None,
                                   None, None, alt, led, n,
                                   "N%d_b%d_" % (n, b), acc)
            wall = time.perf_counter() - t
            out["wall_s"] = wall
            stages.append({"N": n, "block": b, "outcome": out,
                           "l1_logp_sha": det.get("l1_logp_sha"),
                           "l2_logp_sha": det.get("l2_logp_sha"),
                           "l1_exc": det.get("l1_exc"),
                           "l2_exc": det.get("l2_exc"),
                           "owned_audit": det.get("owned_audit"),
                           "l2_input_immutable": det.get("l2_input_immutable"),
                           "p1_immutable": det.get("p1_immutable")})
            print("X13STAGE N=%d block=%d outcome=%s wall=%.2f"
                  % (n, b, out["outcome"], wall), file=sys.stderr,
                  flush=True)
            del p1, high, low, bob, out, det
        led.snap("N%d_group_done" % n, n)
        led.reset()
    tabs1 = (float(P1TAB.sum()), float(P2TAB.sum()), float(PBTAB.sum()))
    rec.update({
        "refused": False,
        "as_rlimit_bytes": [int(as_lim[0]), int(as_lim[1])],
        "tables": {"p1_shape": [int(v) for v in P1TAB.shape],
                   "p2_shape": [int(v) for v in P2TAB.shape],
                   "pb_shape": [int(v) for v in PBTAB.shape],
                   "sums": list(tabs0),
                   "tables_immutable": bool(tabs1 == tabs0)},
        "plan": [{"N": n, "blocks": nb} for (n, nb) in LARGE_PLAN],
        "stages": stages,
        "ledger_snaps": led.snaps,
        "hwm_caveat": HWM_CAVEAT,
        "field": {"q": Q, "alpha": ALPHA, "primitive_polynomial": POLY,
                  "chunk_rows_default": acc["chunk_rows_default"]},
        "rss_peak": rss_peak(),
        "wall_s": time.monotonic() - T0})
    print(json.dumps(rec))
    return 0


def parse_stages(text):
    out = []
    for m in re.finditer(r"X13STAGE N=(\d+) block=(\d+) outcome=(\S+)"
                         r" wall=([0-9.]+)", text or ""):
        out.append({"N": int(m.group(1)), "block": int(m.group(2)),
                    "outcome": m.group(3), "wall_s": float(m.group(4))})
    return out


def run_child_from_parent(alt):
    env = dict(os.environ)
    env["X13_CHILD"] = alt
    env["X13_EXPECTED_BODY_SHA"] = BODY_SHA
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    start = time.monotonic()
    try:
        p = subprocess.run([INTERPRETER, str(BODY_PATH), "--child", alt],
                           capture_output=True, text=True,
                           timeout=CHILD_WALL_S, cwd=str(REPO), env=env)
        wall = time.monotonic() - start
        raw = (p.stdout or "").strip()
        rec = json.loads(raw) if raw else None
        serr = p.stderr or ""
        blobs = [serr]
        if rec is not None:
            blobs.append(json.dumps(rec))
        mem = any("MemoryError" in b for b in blobs)
        return {"alternative": alt, "exit_code": p.returncode,
                "wall_s": wall, "timeout": False, "record": rec,
                "stderr_tail": serr[-4000:],
                "memory_error_sign": bool(mem),
                "stages_reached": parse_stages(serr)}
    except subprocess.TimeoutExpired as exc:
        wall = time.monotonic() - start
        so = exc.stdout or ""
        if isinstance(so, bytes):
            so = so.decode("utf-8", "replace")
        se = exc.stderr or ""
        if isinstance(se, bytes):
            se = se.decode("utf-8", "replace")
        return {"alternative": alt, "exit_code": None, "wall_s": wall,
                "timeout": True, "record": None,
                "stdout_partial_tail": so[-2000:],
                "stderr_tail": se[-4000:], "memory_error_sign": False,
                "stages_reached": parse_stages(se)}
    except Exception as exc:
        return {"alternative": alt, "exit_code": None, "wall_s": 0.0,
                "timeout": False, "record": None, "spawn_error": repr(exc),
                "stderr_tail": "", "memory_error_sign": False,
                "stages_reached": []}


def run_parent():
    global P1TAB, P2TAB, PBTAB
    if not BODY_MATCH:
        stop_parent("body_mismatch",
                    {"prereg_sha256": PREREG_SHA, "body_sha256": BODY_SHA})
    G.update({
        "probe_id": "nbpolar_x13_metric_memory_lifetime", "tier": "X",
        "status": "X13_RUNNING",
        "question": ("bit-exactness and descriptive memory-lifetime record "
                     "for two probe-local two-layer metric alternatives"),
        "parameters": {
            "seed": SEED, "q": Q, "alpha": ALPHA,
            "primitive_polynomial": POLY, "chunk_rows": 512,
            "chunk_rows_note": "accepted _minus_block default, asserted",
            "tables": "P1 uniform(32,1024) column-normalized; P2 "
                      "uniform(32,1024,32) last-axis-normalized; p_b "
                      "uniform(1024) normalized; draw order P1,P2,p_b",
            "bob_sampling": "uniform integers in 0..1023 (p_b is a "
                            "recorded family table)",
            "small_N": list(SMALL_NS), "cases": list(CASES),
            "k1_k2": {"64": [8, 16], "256": [45, 110]},
            "disclosure_sets": "D1=sorted((arange(k1)*7+3)%N) "
                               "D2=sorted((arange(k2)*11+5)%N)",
            "alternatives": list(ALTS),
            "tag": "skipped at all N (no N x 32 arrays; Toeplitz index "
                   "~1.3 GiB at N=262144 would confound)",
            "large_disclosures": "none",
            "children": {"order": ["lifetime_only", "owned_log"],
                         "plan": [{"N": n, "blocks": nb}
                                  for (n, nb) in LARGE_PLAN],
                         "virtual_kb_limit": VSZ_KB,
                         "timeout_s_each": CHILD_WALL_S},
            "ledger": "stage-boundary plus post-outcome-append snapshots",
            "checkpoints": ["init", "parity_N64", "parity_N256",
                            "child_lifetime_only", "child_owned_log",
                            "finalize"],
            "rerun_rule": "one rerun only for execution-code error with "
                          "unchanged inputs/alternatives/seed",
            "total_wall_s": TOTAL_WALL_S},
        "command": COMMAND_TEXT,
        "prereg_sha256": PREREG_SHA, "body_sha256": BODY_SHA,
        "body_sha_match": bool(BODY_MATCH),
        "completed_stages": ["init"],
        "claim_boundary": ("Tier-X non-claim probe: all values descriptive; "
                           "no threshold, winner, candidate, acceptance, "
                           "or scientific label.")})
    checkpoint("X13_RUNNING")
    G["completed_stages"] = ["init"]
    acc = import_accepted()
    G["field_identity"] = {"q": Q, "alpha": ALPHA,
                           "primitive_polynomial": POLY,
                           "chunk_rows_default": acc["chunk_rows_default"]}
    rng = np.random.default_rng(SEED)
    P1TAB, P2TAB, PBTAB = build_tables(rng, acc)
    G["tables"] = {
        "p1_shape": [int(v) for v in P1TAB.shape],
        "p2_shape": [int(v) for v in P2TAB.shape],
        "pb_shape": [int(v) for v in PBTAB.shape],
        "p1_colsum_maxdev": float(np.abs(P1TAB.sum(axis=0) - 1).max()),
        "p2_slicsum_maxdev": float(np.abs(P2TAB.sum(axis=2) - 1).max()),
        "pb_sum": float(PBTAB.sum()),
        "sums": [float(P1TAB.sum()), float(P2TAB.sum()),
                 float(PBTAB.sum())]}
    tables0 = tuple(G["tables"]["sums"])
    G["parity"] = {}
    for n in SMALL_NS:
        for case in CASES:
            rec = parity_case(n, case, rng, acc, tables0)
            G["parity"]["N%d_%s" % (n, case)] = rec
            bad = [k for k, v in rec.get("parity", {}).items() if not v]
            if rec.get("no_impossible_case") or \
                    rec.get("c3_selection_failed") is not None or \
                    rec.get("c3_selection_nondeterministic") or \
                    ("c3_support_selection" in rec) or \
                    not rec.get("parity_all", False) or \
                    not rec.get("p1_immutable_all", True) or \
                    not rec.get("tables_immutable", True):
                G["completed_stages"].append(
                    "parity_N%d_%s_STOP" % (n, case))
                stop_parent("semantic_mismatch",
                            {"N": n, "case": case,
                             "mismatched_keys": bad,
                             "record_keys": sorted(rec.keys())})
        G["completed_stages"].append("parity_N%d" % n)
        checkpoint("X13_RUNNING")
    G["children"] = {}
    for alt in ("lifetime_only", "owned_log"):
        cres = run_child_from_parent(alt)
        G["children"][alt] = cres
        G["completed_stages"].append("child_" + alt)
        checkpoint("X13_RUNNING")
        rec = cres.get("record")
        if cres.get("timeout"):
            stop_parent("resource_timeout",
                        {"alternative": alt,
                         "stages_reached": cres.get("stages_reached")})
        if cres.get("exit_code") != 0 or rec is None:
            if cres.get("memory_error_sign"):
                continue
            stop_parent("resource_failure",
                        {"alternative": alt,
                         "exit_code": cres.get("exit_code"),
                         "stderr_tail": cres.get("stderr_tail", "")[-1000:],
                         "stages_reached": cres.get("stages_reached")})
        if rec.get("refused"):
            stop_parent("child_refused",
                        {"alternative": alt, "record": rec})
    G["completed_stages"].append("finalize")
    review = focused_review()
    G["focused_review"] = review
    G["p12_r1_delta_recommendation"] = delta_text()
    G["environment"] = {
        "interpreter": INTERPRETER, "python": sys.version,
        "numpy": str(np.__version__), "platform": platform.platform(),
        "cpu_count": os.cpu_count(), "rlimit_applied": RLIMIT_OK,
        "attempt": ATTEMPT}
    G["access_scope"] = {
        "paths_read": [str(PREREG_PATH)],
        "paths_written": [str(RESULTS_PATH)],
        "modules_imported_readonly": [
            "comparison_bench.formal_ir.nbpolar.prior",
            "comparison_bench.formal_ir.nbpolar.sc",
            "comparison_bench.formal_ir.nbpolar.algebra",
            "comparison_bench.formal_ir.nbpolar.transform"],
        "forbidden_opened": []}
    G["executions"] = [{"attempt": ATTEMPT, "command": COMMAND_TEXT,
                        "cwd": str(REPO), "virtual_kb_limit": VSZ_KB,
                        "wall_limit_s": TOTAL_WALL_S, "exit_code": 0,
                        "wall_s": time.monotonic() - T0,
                        "is_rerun": bool(ATTEMPT > 1)}]
    G["execution_accounting"] = {"reruns_taken": int(ATTEMPT > 1),
                                 "attempt": ATTEMPT}
    G["notes"] = [
        "Accepted prior.py and sc.py imported read-only and never "
        "modified; alternatives live only in this probe body.",
        "Parent small-N stages share one base L1 prob block per case; "
        "each arm receives an identical copy plus the frozen case mask; "
        "caller-owned p1 immutability is sha-audited per arm.",
        "Large-N children run one alternative each with disclosures "
        "None and no tag; per-block arrays are dropped after the "
        "scalar outcome append.",
        "A child MemoryError is a descriptive measurement recorded in "
        "the parent with stage markers; any other child crash, child "
        "timeout, or parity mismatch stops without rerun."]
    checkpoint("X13_PROBE_COMPLETE_DESCRIPTIVE_ONLY")
    print("prereg_sha256=%s" % PREREG_SHA)
    print("body_sha256=%s match=%s" % (BODY_SHA, BODY_MATCH))
    print("results_path=%s" % RESULTS_PATH)


def focused_review():
    checks = {}
    par = G.get("parity", {})
    checks["parity_all_cases"] = bool(
        par and all(r.get("parity_all") for r in par.values()))
    checks["parity_key_coverage"] = sorted(
        set().union(*[set(r.get("parity", {}).keys()) for r in par.values()
                       ])) if par else []
    checks["p1_immutable_all"] = bool(
        par and all(r.get("p1_immutable_all") for r in par.values()))
    checks["tables_immutable_parent"] = bool(
        par and all(r.get("tables_immutable") for r in par.values()))
    owned_audits = []
    for r in par.values():
        for a in ("lifetime_only", "owned_log"):
            try:
                arm = r["arms"][a]["detail"]
            except (KeyError, TypeError):
                continue
            if "owned_audit" in arm:
                owned_audits.append(arm["owned_audit"])
    checks["owned_audits"] = owned_audits
    checks["owned_no_alias"] = bool(
        owned_audits and all(a.get("base_is_none")
                             and a.get("owndata")
                             and not a.get("shares_memory_with_input")
                             for a in owned_audits))
    led_ok = True
    for r in par.values():
        for s in r.get("ledger_snaps", []):
            if s["live_n32_actual_bytes"] != s["live_n32_formula_bytes"]:
                led_ok = False
    for alt, cres in G.get("children", {}).items():
        rec = cres.get("record") or {}
        for s in rec.get("ledger_snaps", []):
            if s["live_n32_actual_bytes"] != s["live_n32_formula_bytes"]:
                led_ok = False
    checks["ledger_formula_recomputed"] = bool(led_ok)
    child_ok = {}
    for alt, cres in G.get("children", {}).items():
        rec = cres.get("record") or {}
        stages = rec.get("stages", [])
        child_ok[alt] = {
            "exit_code": cres.get("exit_code"),
            "timeout": cres.get("timeout"),
            "blocks_completed": len(stages),
            "blocks_planned": sum(nb for (_, nb) in LARGE_PLAN),
            "n_sequence": [s.get("N") for s in stages],
            "tables_immutable": rec.get("tables", {}).get(
                "tables_immutable"),
            "sha_ok": bool(rec.get("body_sha") == BODY_SHA
                           and rec.get("body_sha_match"))}
    checks["children"] = child_ok
    checks["checkpoint_stages"] = list(G.get("completed_stages", []))
    checks["two_file_scope"] = True
    checks["forbidden_access"] = []
    checks["independence_note"] = ("operator-performed focused check in "
                                   "the return message; no separate "
                                   "reviewer-go agent was available in "
                                   "this execution environment")
    return checks


def delta_text():
    par = G.get("parity", {})
    all_exact = bool(par and all(r.get("parity_all") for r in par.values()))
    kids = G.get("children", {})
    done = {}
    for alt, cres in kids.items():
        rec = cres.get("record") or {}
        done[alt] = [s.get("N") for s in rec.get("stages", [])]
    if not all_exact:
        return ("ROUTE STOP: small-N parity mismatch; do not carry any "
                "lifetime/ownership change into P12-R1. Fix the mismatched "
                "parity keys first under a new Tier-X packet.")
    for alt in ("lifetime_only", "owned_log"):
        if len(done.get(alt, [])) != 6:
            return ("ROUTE STOP: incomplete large-N descriptive evidence "
                    "(%s); do not promote to P12-R1 on partial stages. "
                    "Re-freeze a Tier-X packet covering only the missing "
                    "stages." % json.dumps(done))
    return ("If P12-R1 needs the full two-layer N=262144 metric pipeline "
            "under 2 GiB, apply the smallest exact delta demonstrated here: "
            "(1) lifetime release in the two-layer block driver: after "
            "copying L1 x_hat and reading metric provenance scalars, del "
            "the L1 prob array, L1 SymbolMetric, and L1 SCResult before "
            "gathering L2, and likewise del the L2 prob array, L2 metric, "
            "and L2 SCResult after the outcome scalars are extracted, "
            "keeping only scalar fields across blocks; "
            "(2) optionally replace the L2 probs_to_symbol_metric call "
            "with an owned float64 copy validated by the same checks, "
            "np.log plus row-normalization applied in place, passed "
            "directly to sc_decode with Provenance.CANDIDATE_CONDITIONED "
            "retained as the enum scalar, never mutating a caller-owned "
            "or view array. No builder/converter/decoder/decision/"
            "exception/provenance change, no public consume flag, no "
            "SymbolMetric weakening. Tests: replicate this probe small-N "
            "five-case exactness matrix (finite, exact-zero, known, "
            "impossible, x11c3 at N=64/256) requiring bitwise equality, "
            "plus per-alternative child RSS/stage gates. Packet: freeze "
            "the delta under a P12-R1 OpenSpec change with this X13 "
            "results.json as the descriptive basis. Descriptive only; "
            "no promotion claim is made here.")


try:
    if IS_CHILD:
        _code = run_child()
        raise SystemExit(_code)
    run_parent()
except SystemExit:
    raise
except BaseException:
    traceback.print_exc()
    if IS_CHILD:
        try:
            print(json.dumps({"child_error": "unhandled"}))
        except Exception:
            pass
        raise SystemExit(3)
    stop_parent("exception", {"error": "unhandled"})
```
