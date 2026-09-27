"""Tier-X probe scl-gate-t3: SC vs SCL-joint (CRC-16, M=4, L in {4,8,16}) on the
G1R2-matched channel with an explicit 1e-15 decode-table floor, at two working
points on the N=32768 op-n32k-matched grid (T6421, k1 shares 4.69% and 9%).

Authorization: PI ruling commits dba253df (SCL lock amendment T1 DECIDED, T2
authorized, T3 authorized as Tier-X) and ae094620 (T3 second working point).
Operator packet delivered inline by the coordinator (2026-09-27); see the
operator's transcript/report for the full frozen parameter list. This file
implements exactly that frozen spec; no scientific status/verdict is produced
here (Tier-X, non-claim).

Frozen deltas vs workspace/probes/op-n32k-matched/run.py (inherited
unchanged otherwise: G1R2-matched raw masses, sign-fixed table convention,
GF32 two-layer SC/oracle semantics, FROZEN_TOEPLITZ_MASTER, worst_k design
rule, DESIGN_MC=64, per-(seed,block) rng=default_rng([seed,block]) pairing):

1. Decode-table floor: the DECODER's channel table (used to build p1/p2 and
   for the genie-SC design pass) is built from
   ``prior.apply_explicit_floor(raw_masses, 1e-15, reason=...)`` -- the
   real-data-matched convention. The (x,y) SAMPLING pmf is the ORIGINAL
   unfloored, 0.9999-renormalized matched_pmf (bit-identical to
   op-n32k-matched's own ``matched_pmf``), so per-(seed,block) draws
   reproduce op-n32k-matched's blocks exactly for pairing.
2. Two points only (both from the T6421/f_book~=1.20 row of
   op-n32k-matched's grid): A = k1=301/k2=6120 (share 4.69%,
   op-n32k-matched operational exact=10/16) and B = k1=578/k2=5843 (share
   9%, op-n32k-matched operational exact=0/16).
3. Arms: SC (``two_layer.run_two_layer_block`` operational path, same
   floored table -- a same-condition baseline re-run inside this probe, not
   a reuse of op-n32k-matched's old cached numbers) and SCL-joint
   (``scl_joint.scl_joint_decode``, L in {4,8,16}, top_m=4 default, CRC-16).
   Plus an oracle reference per (point, L): L1 fully disclosed at truth
   (``d1_positions=arange(N)``, degenerate/free SCL survivor), L2 via SCL at
   the same L -- cheap, no top_m expansion needed (top_m=1).
4. Toeplitz tag for the SCL-joint/oracle arms reuses ``two_layer``'s
   ``ARMS=("operational","oracle")``-restricted ``block_toeplitz_seed_bits``
   with arm="operational" (SCL-joint) / arm="oracle" (oracle ref) and the
   SAME block_index as the paired SC block for that (seed,block) -- same
   public verification context, different candidate -- then recomputes the
   tag directly via ``formal_ir.shared.toeplitz_tag`` (scl_joint has no
   built-in tag/verify path; two_layer's own verify is reused only for the
   SC arm).
5. accepted = crc_pass AND tag_pass; undetected = accepted AND NOT
   label_exact (isolated, never merged into exact/FER); exact = accepted AND
   label_exact; verify_failed = NOT accepted (covers CRC fail and/or tag
   fail); decode_failed / resource_abort counted separately.
6. Parallel (point, arm) split into <=7 OS processes (role=sc: SC arm both
   points; role=scl --point {A,B} --L {4,8,16}: 6 processes), each writing
   only its own ``part_<label>.json`` under this probe root; role=aggregate
   merges them into one ``results.json``.

No data loading beyond this file's own synthetic draws, no real/artifact
data, no output outside this probe's own root
(``workspace/probes/scl-gate-t3/``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

import numpy as np

try:
    import resource
except ImportError:
    resource = None

ROOT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar"
PROBE_DIR = ROOT + "/workspace/probes/scl-gate-t3"
sys.path.insert(0, ROOT + "/comparison_bench/src")

from comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.formal_ir.nbpolar import scl as scl_mod
from comparison_bench.formal_ir.nbpolar import sc as sc_mod
from comparison_bench.formal_ir.nbpolar import scl_joint
from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.formal_ir.nbpolar.prior import (
    build_p1_metrics, gather_p2_metrics, probs_to_symbol_metric, Provenance,
    apply_explicit_floor,
)
from comparison_bench.formal_ir.nbpolar.transform import polar_transform
from comparison_bench.formal_ir.shared import toeplitz_tag

PROBE_ID = "scl-gate-t3"
Q = 1024
N = 32768
ALPHA = 2
DISCLOSED_BITS_PER_COORDINATE = 5  # log2(32), same convention as two_layer/op-n32k-matched
TAG_BITS = tl.TAG_BITS  # 64
CRC_BITS = scl_joint.CRC_BITS  # 16
TOP_M_DEFAULT = 4
L_VALUES = (4, 8, 16)
FLOOR = 1e-15
P_RAW = {"p0": 0.7562, "p1": 0.0018, "pm1": 0.2419}  # raw masses, sum 0.9999
RAW_SUM = 0.9999
DESIGN_SEED = 2026093000
DESIGN_MC = 64
SEEDS = (2026093003, 2026093004)
BLOCKS = 8
DESIGN_SANITY_TOL = 0.01
MASTER = tl.FROZEN_TOEPLITZ_MASTER
WALL_LIMIT_S = 14400.0  # 4h, per-process self-check (processes run in parallel, not summed)
RSS_LIMIT = 1 * 1024 ** 3  # 1 GiB per process

POINTS = {
    "A": {"label": "A_T6421_k1_301_k2_6120", "total": 6421, "k1": 301, "k2": 6120,
          "share": 0.0469, "op_n32k_matched_exact": "10/16"},
    "B": {"label": "B_T6421_k1_578_k2_5843", "total": 6421, "k1": 578, "k2": 5843,
          "share": 0.09, "op_n32k_matched_exact": "0/16"},
}


def rss_bytes():
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def budget(t0):
    wall = time.perf_counter() - t0
    rss = rss_bytes()
    reasons = []
    if wall > WALL_LIMIT_S:
        reasons.append("wall_s>14400")
    if rss is not None and rss > RSS_LIMIT:
        reasons.append("rss>1GiB")
    return wall, rss, reasons


def summarize(xs):
    xs = [float(v) for v in xs]
    n = len(xs)
    if n == 0:
        return {"series": [], "mean": None, "sample_std": None, "range": None, "n": 0}
    mean = sum(xs) / n
    var = sum((v - mean) ** 2 for v in xs) / (n - 1) if n > 1 else 0.0
    return {"series": xs, "mean": mean, "sample_std": float(np.sqrt(var)),
            "range": [min(xs), max(xs)], "n": n}


def matched_pmf_raw_array(q):
    p = np.zeros(q, dtype=np.float64)
    p[0] = P_RAW["p0"]
    p[1 % q] = P_RAW["p1"]
    p[(q - 1) % q] = P_RAW["pm1"]
    return p


def sample_pmf(q):
    """Unfloored, 0.9999-renormalized pmf -- identical to op-n32k-matched's
    ``matched_pmf``; used ONLY to draw (x,y) so blocks reproduce exactly."""
    p = matched_pmf_raw_array(q)
    s = p.sum()
    assert abs(s - RAW_SUM) < 1e-12, s
    p = p / s
    assert abs(p.sum() - 1.0) < 1e-12
    return p


def decode_pmf_floored(q, reason):
    """Explicit-floor decode-table pmf (real-data-matched decoder convention)."""
    return apply_explicit_floor(matched_pmf_raw_array(q), FLOOR, reason=reason)


def build_tables():
    pmf_sample = sample_pmf(Q)
    pmf_decode = decode_pmf_floored(
        Q, reason="G1R2-matched explicit 1e-15 floor (scl-gate-t3 decoder table)"
    )
    delta = (np.arange(Q)[None, :] - np.arange(Q)[:, None]) % Q
    table_sample = pmf_sample[delta]  # only used for parity/logging, never for sampling directly
    table_decode = pmf_decode[delta]
    p1, p2 = tl.layer_metric_tables(table_decode)
    nz = pmf_decode[pmf_decode > 0]
    H = float(-(nz * np.log2(nz)).sum())
    return pmf_sample, pmf_decode, table_decode, p1, p2, H


def gen_block(seed, block, pmf_sample):
    """Bit-identical to op-n32k-matched's per-(seed,block) (x,y) draw."""
    rngb = np.random.default_rng([seed, block])
    x = rngb.integers(0, Q, size=N)
    dd = rngb.choice(Q, size=N, p=pmf_sample)
    y = (x + dd) % Q
    high = (x >> 5).astype(np.int64)
    low = (x & 31).astype(np.int64)
    bob = y.astype(np.int64)
    return x, high, low, bob


def worst_k(hvec, k):
    return np.sort(np.argsort(-hvec, kind="stable")[:k]).astype(np.int64)


# ------------------------- role: design -------------------------------------

def cmd_design(args):
    t0 = time.perf_counter()
    out_path = PROBE_DIR + "/design.json"
    if os.path.exists(out_path):
        print("REFUSE: design.json already exists; not overwriting (no-overwrite rule)")
        sys.exit(2)

    field = make_gf32()
    pmf_sample, pmf_decode, table_decode, p1, p2, H = build_tables()
    HN = H * N

    rng = np.random.default_rng(DESIGN_SEED)
    H1 = np.zeros(N)
    H2 = np.zeros(N)
    allpos = np.arange(N)
    mdone = 0
    stopped_reasons = []
    for m in range(DESIGN_MC):
        if m > 0 and m % 32 == 0:
            _, _, br = budget(t0)
            if br:
                stopped_reasons = br
                break
        x = rng.integers(0, Q, size=N)
        dd = rng.choice(Q, size=N, p=pmf_sample)
        y = (x + dd) % Q
        high = (x >> 5).astype(np.int64)
        low = (x & 31).astype(np.int64)
        bob = y.astype(np.int64)
        mtr1 = probs_to_symbol_metric(build_p1_metrics(bob[None, :], p1)[0],
                                       provenance=Provenance.PRIOR_ONLY)
        r1 = sc_mod.sc_decode(mtr1.logp, field=field, alpha=ALPHA, known_positions=allpos,
                                       known_values=polar_transform(high, field=field, alpha=ALPHA))
        pr = np.exp(r1.decision_metrics)
        with np.errstate(divide="ignore"):
            lg = np.log2(pr, out=np.zeros_like(pr), where=pr > 0)
        H1 += -(np.where(pr > 0, pr * lg, 0.0)).sum(axis=1)
        mtr2 = probs_to_symbol_metric(gather_p2_metrics(bob[None, :], high[None, :], p2)[0],
                                       provenance=Provenance.ORACLE_CONDITIONED)
        r2 = sc_mod.sc_decode(mtr2.logp, field=field, alpha=ALPHA, known_positions=allpos,
                                       known_values=polar_transform(low, field=field, alpha=ALPHA))
        pr = np.exp(r2.decision_metrics)
        with np.errstate(divide="ignore"):
            lg = np.log2(pr, out=np.zeros_like(pr), where=pr > 0)
        H2 += -(np.where(pr > 0, pr * lg, 0.0)).sum(axis=1)
        mdone += 1
    if mdone:
        H1 /= mdone
        H2 /= mdone
    design_complete = (mdone == DESIGN_MC) and not stopped_reasons

    h1m = float(H1.mean()) if mdone else None
    h2m = float(H2.mean()) if mdone else None
    sanity = None
    if design_complete:
        diff = abs(h1m + h2m - H)
        sanity = {"H1_mean": h1m, "H2_mean": h2m, "sum": h1m + h2m, "H": H, "abs_diff": diff,
                  "tol": DESIGN_SANITY_TOL, "pass": bool(diff <= DESIGN_SANITY_TOL)}
        assert sanity["pass"], f"design sanity FAIL: |H1+H2-H|={diff} > {DESIGN_SANITY_TOL}"

    points = {}
    if design_complete and sanity and sanity["pass"]:
        for key, pt in POINTS.items():
            d1 = worst_k(H1, pt["k1"])
            d2 = worst_k(H2, pt["k2"])
            points[key] = {**pt, "d1": d1.tolist(), "d2": d2.tolist()}

    wall, rss, br = budget(t0)
    out = {
        "probe_id": PROBE_ID, "tier": "X", "step": "design",
        "status": "ok" if (design_complete and sanity and sanity["pass"]) else "design_incomplete_or_fail",
        "design_seed": DESIGN_SEED, "design_mc": DESIGN_MC, "mc_done": mdone,
        "stopped_reasons": stopped_reasons,
        "H": H, "HN": HN, "sanity": sanity,
        "H1": H1.tolist(), "H2": H2.tolist(),
        "points": points,
        "wall_s": wall, "peak_rss_bytes": rss,
    }
    with open(out_path, "w") as fh:
        json.dump(out, fh)
    print("WROTE", out_path, "status", out["status"], "wall_s", round(wall, 1))


# ------------------------- shared per-block evaluators ------------------------

def eval_sc_block(block_index, high, low, bob, field, p1, p2, d1, d2, k1, k2):
    res = tl.run_two_layer_block(
        block_index, high, low, bob, field=field, p1_table=p1, p2_table=p2,
        d1=d1, d2=d2, n=N, k1=k1, k2=k2, toeplitz_master=MASTER,
    )
    op = res.operational
    return {
        "outcome": op.outcome,
        "exact": bool(op.outcome == "exact"),
        "undetected": bool(op.outcome == "undetected"),
        "verify_failed": bool(op.outcome == "verify_failed"),
        "decode_failed": bool(op.outcome == "decode_failed"),
        "resource_abort": bool(op.outcome == "resource_abort"),
        "label_match": bool(op.label_match),
        "tag_pass": bool(op.tag_pass),
        "tag_invoked": bool(op.tag_invoked),
        "key_dependent_bits": int(op.key_dependent_bits),
        "block_wall_s": float(res.block_wall_s),
    }


def _scl_style_eval(block_index, arm_name, high, low, bob, field, p1, p2,
                     d1_positions, d1_values, d2, L, top_m):
    t0 = time.perf_counter()
    labels_true = (low + tl.LABEL_SCALE * high).astype(np.int64)
    labels_true_bits = tl.labels_to_bits(labels_true)
    u2_true = polar_transform(low, field=field, alpha=ALPHA)
    val2 = u2_true[d2]
    crc_true = scl_joint.labels_crc16(labels_true)
    seed_bits = tl.block_toeplitz_seed_bits(arm_name, block_index, master=MASTER,
                                             bit_length=tl.seed_bits_for(N))
    tag_true = toeplitz_tag(labels_true_bits, seed_bits, TAG_BITS)
    try:
        got = scl_joint.scl_joint_decode(
            bob, crc_true, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=d1_positions, d1_values=d1_values, d2_positions=d2, d2_values=val2,
            list_width_L=L, top_m=top_m,
        )
    except (scl_mod.ImpossibleDisclosedValueError, scl_mod.NumericNonfiniteError) as exc:
        wall = time.perf_counter() - t0
        return {
            "outcome": "decode_failed", "label_exact": False, "crc_pass": False,
            "crc_failed": True, "tag_pass": False, "accepted": False, "undetected": False,
            "exact": False, "verify_failed": False, "decode_failed": True, "resource_abort": False,
            "error_type": type(exc).__name__, "block_wall_s": wall,
        }
    except MemoryError as exc:
        wall = time.perf_counter() - t0
        return {
            "outcome": "resource_abort", "label_exact": False, "crc_pass": False,
            "crc_failed": True, "tag_pass": False, "accepted": False, "undetected": False,
            "exact": False, "verify_failed": False, "decode_failed": False, "resource_abort": True,
            "error_type": "MemoryError", "block_wall_s": wall,
        }
    label_exact = bool(got.label_hat.tolist() == labels_true.tolist())
    tag_hat = toeplitz_tag(tl.labels_to_bits(got.label_hat), seed_bits, TAG_BITS)
    tag_pass = bool(tag_hat == tag_true)
    accepted = bool(got.crc_pass and tag_pass)
    undetected = bool(accepted and not label_exact)
    exact = bool(accepted and label_exact)
    verify_failed = bool(not accepted)
    outcome = "exact" if exact else ("undetected" if undetected else "verify_failed")
    wall = time.perf_counter() - t0
    return {
        "outcome": outcome, "label_exact": label_exact, "crc_pass": bool(got.crc_pass),
        "crc_failed": bool(got.crc_failed), "tag_pass": tag_pass, "accepted": accepted,
        "undetected": undetected, "exact": exact, "verify_failed": verify_failed,
        "decode_failed": False, "resource_abort": False,
        "crc_bits": int(got.crc_bits), "top_m_used": int(got.top_m_used),
        "l1_survivor_count": int(got.l1_survivor_count),
        "candidates_considered": int(got.candidates_considered),
        "block_wall_s": wall,
    }


def eval_scl_joint_block(block_index, high, low, bob, field, p1, p2, d1, d2, L, top_m=TOP_M_DEFAULT):
    u1_true = polar_transform(high, field=field, alpha=ALPHA)
    val1 = u1_true[d1]
    return _scl_style_eval(block_index, "operational", high, low, bob, field, p1, p2,
                            d1, val1, d2, L, top_m)


def eval_oracle_block(block_index, high, low, bob, field, p1, p2, d2, L):
    u1_true = polar_transform(high, field=field, alpha=ALPHA)
    d1_full = np.arange(N, dtype=np.int64)
    return _scl_style_eval(block_index, "oracle", high, low, bob, field, p1, p2,
                            d1_full, u1_true, d2, L, top_m=1)


def block_index_for(point_key, seed_idx, block):
    point_idx = {"A": 0, "B": 1}[point_key]
    return point_idx * 1000 + seed_idx * 100 + block


# ------------------------- role: sc worker -----------------------------------

def cmd_sc(args):
    t0 = time.perf_counter()
    design = json.load(open(PROBE_DIR + "/design.json"))
    if design["status"] != "ok":
        print("REFUSE: design.json status !=ok:", design["status"])
        sys.exit(2)
    field = make_gf32()
    _, _, _, p1, p2, _ = build_tables()
    pmf_sample = sample_pmf(Q)

    out_path = PROBE_DIR + "/part_SC.json"
    if os.path.exists(out_path):
        print("REFUSE: already exists:", out_path)
        sys.exit(2)

    records = {}
    stopped = False
    stop_reasons = []
    for pkey, pt in design["points"].items():
        d1 = np.asarray(pt["d1"], dtype=np.int64)
        d2 = np.asarray(pt["d2"], dtype=np.int64)
        k1, k2 = pt["k1"], pt["k2"]
        recs = []
        for si, seed in enumerate(SEEDS):
            for b in range(BLOCKS):
                _, _, br = budget(t0)
                if br:
                    stopped = True
                    stop_reasons = br
                    break
                x, high, low, bob = gen_block(seed, b, pmf_sample)
                bidx = block_index_for(pkey, si, b)
                r = eval_sc_block(bidx, high, low, bob, field, p1, p2, d1, d2, k1, k2)
                r.update({"seed": int(seed), "block": int(b)})
                recs.append(r)
            if stopped:
                break
        records[pkey] = recs
        if stopped:
            break

    wall, rss, br = budget(t0)
    if br:
        stop_reasons = sorted(set(stop_reasons + br))
        stopped = True
    out = {
        "part": "SC", "probe_id": PROBE_ID, "tier": "X",
        "status": "incomplete" if stopped else "ok",
        "stop_reasons": stop_reasons,
        "records": records,
        "wall_s": wall, "peak_rss_bytes": rss,
    }
    with open(out_path, "w") as fh:
        json.dump(out, fh)
    print("WROTE", out_path, "status", out["status"], "wall_s", round(wall, 1))


# ------------------------- role: scl worker -----------------------------------

def cmd_scl(args):
    t0 = time.perf_counter()
    point_key = args.point
    L = args.L
    design = json.load(open(PROBE_DIR + "/design.json"))
    if design["status"] != "ok":
        print("REFUSE: design.json status !=ok:", design["status"])
        sys.exit(2)
    pt = design["points"][point_key]
    d1 = np.asarray(pt["d1"], dtype=np.int64)
    d2 = np.asarray(pt["d2"], dtype=np.int64)

    field = make_gf32()
    _, _, _, p1, p2, _ = build_tables()
    pmf_sample = sample_pmf(Q)

    out_path = PROBE_DIR + f"/part_SCL_{point_key}_L{L}.json"
    if os.path.exists(out_path):
        print("REFUSE: already exists:", out_path)
        sys.exit(2)

    scl_recs = []
    oracle_recs = []
    stopped = False
    stop_reasons = []
    for si, seed in enumerate(SEEDS):
        for b in range(BLOCKS):
            _, _, br = budget(t0)
            if br:
                stopped = True
                stop_reasons = br
                break
            x, high, low, bob = gen_block(seed, b, pmf_sample)
            bidx = block_index_for(point_key, si, b)
            r_scl = eval_scl_joint_block(bidx, high, low, bob, field, p1, p2, d1, d2, L)
            r_scl.update({"seed": int(seed), "block": int(b)})
            scl_recs.append(r_scl)
            r_or = eval_oracle_block(bidx, high, low, bob, field, p1, p2, d2, L)
            r_or.update({"seed": int(seed), "block": int(b)})
            oracle_recs.append(r_or)
        if stopped:
            break

    wall, rss, br = budget(t0)
    if br:
        stop_reasons = sorted(set(stop_reasons + br))
        stopped = True
    out = {
        "part": f"SCL_{point_key}_L{L}", "probe_id": PROBE_ID, "tier": "X",
        "point": point_key, "L": L, "top_m": TOP_M_DEFAULT,
        "status": "incomplete" if stopped else "ok",
        "stop_reasons": stop_reasons,
        "scl_records": scl_recs,
        "oracle_records": oracle_recs,
        "wall_s": wall, "peak_rss_bytes": rss,
    }
    with open(out_path, "w") as fh:
        json.dump(out, fh)
    print("WROTE", out_path, "status", out["status"], "wall_s", round(wall, 1))


# ------------------------- role: smoke (non-protocol, not counted) ----------

def cmd_smoke(args):
    """1-block, L=4, seed=1 (explicitly non-protocol) smoke check. Not a result."""
    design = json.load(open(PROBE_DIR + "/design.json"))
    pt = design["points"]["A"]
    d1 = np.asarray(pt["d1"], dtype=np.int64)
    d2 = np.asarray(pt["d2"], dtype=np.int64)
    field = make_gf32()
    _, _, _, p1, p2, _ = build_tables()
    pmf_sample = sample_pmf(Q)
    x, high, low, bob = gen_block(1, 0, pmf_sample)  # seed=1: non-protocol, never in SEEDS
    t0 = time.perf_counter()
    r = eval_scl_joint_block(999999, high, low, bob, field, p1, p2, d1, d2, 4)
    print("SMOKE non-protocol L=4:", r, "wall_s", round(time.perf_counter() - t0, 2))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="role", required=True)
    sub.add_parser("design")
    sub.add_parser("sc")
    p_scl = sub.add_parser("scl")
    p_scl.add_argument("--point", choices=["A", "B"], required=True)
    p_scl.add_argument("--L", type=int, choices=list(L_VALUES), required=True)
    sub.add_parser("smoke")
    args = ap.parse_args()
    try:
        {"design": cmd_design, "sc": cmd_sc, "scl": cmd_scl, "smoke": cmd_smoke}[args.role](args)
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
