"""Tier-X probe p16-vs-matched-design: on the N=32768 G1R2-matched channel
(explicit 1e-15 decode-table floor, identical convention to
workspace/probes/scl-gate-t3), at the real-contract frozen K1=319/K2=6492,
compare SC performance of the frozen P16 disclosure set (derived under the
old M0/"1M" prior) against a worst_k set genie-designed directly on THIS
matched channel (same design procedure as scl-gate-t3: design_seed=2026093000,
DESIGN_MC=64).

Authorization: PI-authorized Tier-X synthetic probe per AGENTS.md Section 10.4
/ docs/nbpolar/PROBE_TIER.md; operator packet delivered inline by the
coordinator (2026-09-28). Non-claim, descriptive planning evidence only:
no candidate/accepted token, no pass/fail verdict, no attempt accounting,
no real/artifact data. Writes only under
workspace/probes/p16-vs-matched-design/.

P16 source (read-only, frozen elsewhere, never re-derived here):
.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json
  cell.l1_order / cell.l2_order (permutations of range(32768)); frozen
  disclosure positions = l1_order[:k1] / l2_order[:k2] (verbatim reuse of the
  slicing rule at comparison_bench/src/comparison_bench/formal_ir/nbpolar/
  operational_f13.py:777-778). k1=319/k2=6492 in the file already match the
  real-contract frozen K1/K2 (g2_freeze.md), so no re-derivation is needed.
  freeze_sha256 = 055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b
  (must match g2_freeze.md's pinned digest -- checked below, hard assert).
  Construction channel: source/target "1M" (report.md), an OLD prior model --
  NOT the G1R2-matched real-CAL32 channel used here. No raw real data is
  read anywhere in this script; the P16 file is a frozen, already-materialized
  JSON artifact of positions and metadata only.

Channel / decode-table convention (verbatim from scl-gate-t3, inherited
unchanged): SAMPLING pmf = raw G1R2 CAL32 masses renormalized by dividing by
the raw sum 0.9999 (bit-identical to op-n32k-matched's matched_pmf); DECODE
pmf = prior.apply_explicit_floor(raw masses, 1e-15, reason=...) (floor
applied to the raw, not-yet-renormalized masses, then internally
renormalized); table[a,b] = decode_pmf[(b-a)%Q].
"""

from __future__ import annotations

import hashlib
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
PROBE_DIR = ROOT + "/workspace/probes/p16-vs-matched-design"
sys.path.insert(0, ROOT + "/comparison_bench/src")

from comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.formal_ir.nbpolar import sc as sc_mod
from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.formal_ir.nbpolar.prior import (
    build_p1_metrics, gather_p2_metrics, probs_to_symbol_metric, Provenance,
    apply_explicit_floor,
)
from comparison_bench.formal_ir.nbpolar.transform import polar_transform

PROBE_ID = "p16-vs-matched-design"
Q = 1024
N = 32768
ALPHA = 2
FLOOR = 1e-15
P_RAW = {"p0": 0.7562, "p1": 0.0018, "pm1": 0.2419}  # raw masses, sum 0.9999
RAW_SUM = 0.9999
DESIGN_SEED = 2026093000
DESIGN_MC = 64
DESIGN_SANITY_TOL = 0.01
SEEDS = (2026092810, 2026092811)
BLOCKS_PER_SEED = 16
K1 = 319
K2 = 6492
K_TOTAL = 6811
MASTER = tl.FROZEN_TOEPLITZ_MASTER
WALL_LIMIT_S = 3600.0
RSS_LIMIT = 2 * 1024 ** 3  # 2 GiB
P16_PATH = (ROOT + "/.workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/"
            "operational_f13_gate/construction_and_allocation.json")
P16_EXPECTED_DIGEST = "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"

OUT_PATH = PROBE_DIR + "/results.json"


def rss_bytes():
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def budget(t0):
    wall = time.perf_counter() - t0
    rss = rss_bytes()
    reasons = []
    if wall > WALL_LIMIT_S:
        reasons.append("wall_s>3600")
    if rss is not None and rss > RSS_LIMIT:
        reasons.append("rss>2GiB")
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
    p = matched_pmf_raw_array(q)
    s = p.sum()
    assert abs(s - RAW_SUM) < 1e-12, s
    p = p / s
    assert abs(p.sum() - 1.0) < 1e-12
    return p


def decode_pmf_floored(q, reason):
    return apply_explicit_floor(matched_pmf_raw_array(q), FLOOR, reason=reason)


def build_tables():
    pmf_sample = sample_pmf(Q)
    pmf_decode = decode_pmf_floored(
        Q, reason="G1R2-matched explicit 1e-15 floor (p16-vs-matched-design decoder table)"
    )
    delta = (np.arange(Q)[None, :] - np.arange(Q)[:, None]) % Q
    table_decode = pmf_decode[delta]
    p1, p2 = tl.layer_metric_tables(table_decode)
    nz = pmf_decode[pmf_decode > 0]
    H = float(-(nz * np.log2(nz)).sum())
    return pmf_sample, pmf_decode, table_decode, p1, p2, H


def gen_block(seed, block, pmf_sample):
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


def jaccard(a, b):
    sa, sb = set(int(v) for v in a), set(int(v) for v in b)
    inter = len(sa & sb)
    union = len(sa | sb)
    return {"intersection": inter, "union": union, "jaccard": (inter / union if union else None),
            "len_a": len(sa), "len_b": len(sb)}


def load_p16():
    with open(P16_PATH, "rb") as fh:
        raw = fh.read()
    obj = json.loads(raw)
    cell = obj["cell"]
    digest = cell["freeze_sha256"]
    if digest != P16_EXPECTED_DIGEST:
        raise ValueError(f"P16 freeze_sha256 mismatch: file={digest} expected={P16_EXPECTED_DIGEST}")
    if int(cell["k1"]) != K1 or int(cell["k2"]) != K2 or int(cell["n"]) != N:
        raise ValueError(f"P16 cell k1/k2/n mismatch: got k1={cell['k1']} k2={cell['k2']} n={cell['n']}")
    l1_order = np.asarray(cell["l1_order"], dtype=np.int64)
    l2_order = np.asarray(cell["l2_order"], dtype=np.int64)
    if l1_order.shape != (N,) or l2_order.shape != (N,):
        raise ValueError("P16 l1_order/l2_order must have length N")
    if len(set(l1_order.tolist())) != N or len(set(l2_order.tolist())) != N:
        raise ValueError("P16 l1_order/l2_order must be permutations of range(N)")
    d1 = np.sort(l1_order[:K1]).astype(np.int64)
    d2 = np.sort(l2_order[:K2]).astype(np.int64)
    return {
        "path": P16_PATH,
        "sha256_of_file_bytes": hashlib.sha256(raw).hexdigest(),
        "inner_freeze_sha256": digest,
        "d1": d1, "d2": d2,
        "protocol": obj.get("protocol"),
        "cell_k_total": int(cell["k_total"]),
        "cell_leakage_bits": int(cell["leakage_bits"]),
        "cell_f": float(cell["f"]),
    }


def run_design(t0, pmf_sample, p1, p2, field, H):
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
        # Hard assert per prereg step 4: design sanity failure aborts before any block work.
        assert sanity["pass"], f"design sanity FAIL: |H1+H2-H|={diff} > {DESIGN_SANITY_TOL}"
    return H1, H2, mdone, design_complete, sanity, stopped_reasons


def eval_arm(label, block_index, high, low, bob, high_true, field, p1, p2, d1, d2):
    res = tl.run_two_layer_block(
        block_index, high, low, bob, field=field, p1_table=p1, p2_table=p2,
        d1=d1, d2=d2, n=N, k1=K1, k2=K2, toeplitz_master=MASTER,
    )
    op = res.operational
    oq = res.oracle
    op_l1_exact = bool((not op.l1_decode_failed) and op.high_hat is not None
                        and np.array_equal(op.high_hat, high_true))
    op_l2_pure_error = bool(op_l1_exact and not op.label_match)
    oq_l1_exact = bool((not oq.l1_decode_failed) and oq.high_hat is not None
                        and np.array_equal(oq.high_hat, high_true))
    oq_l2_pure_error = bool(oq_l1_exact and not oq.label_match)
    return {
        "arm": label,
        "operational": {
            "outcome": op.outcome, "exact": bool(op.outcome == "exact"),
            "undetected": bool(op.outcome == "undetected"),
            "verify_failed": bool(op.outcome == "verify_failed"),
            "decode_failed": bool(op.outcome == "decode_failed"),
            "resource_abort": bool(op.outcome == "resource_abort"),
            "label_match": bool(op.label_match), "tag_pass": bool(op.tag_pass),
            "l1_exact": op_l1_exact, "l1_decode_failed": bool(op.l1_decode_failed),
            "l2_pure_error": op_l2_pure_error,
            "key_dependent_bits": int(op.key_dependent_bits),
        },
        "oracle": {
            "outcome": oq.outcome, "exact": bool(oq.outcome == "exact"),
            "undetected": bool(oq.outcome == "undetected"),
            "verify_failed": bool(oq.outcome == "verify_failed"),
            "decode_failed": bool(oq.outcome == "decode_failed"),
            "resource_abort": bool(oq.outcome == "resource_abort"),
            "label_match": bool(oq.label_match), "tag_pass": bool(oq.tag_pass),
            "l1_exact": oq_l1_exact, "l1_decode_failed": bool(oq.l1_decode_failed),
            "l2_pure_error": oq_l2_pure_error,
        },
        "block_wall_s": float(res.block_wall_s),
    }


def main():
    t0 = time.perf_counter()
    if os.path.exists(OUT_PATH):
        print("REFUSE: results.json already exists; not overwriting (no-overwrite rule)")
        sys.exit(2)

    field = make_gf32()
    pmf_sample, pmf_decode, table_decode, p1, p2, H = build_tables()
    HN = H * N
    f_book = 5.0 * K_TOTAL / HN

    p16 = load_p16()

    H1, H2, mdone, design_complete, sanity, design_stop = run_design(
        t0, pmf_sample, p1, p2, field, H
    )
    if not (design_complete and sanity and sanity["pass"]):
        wall, rss, _ = budget(t0)
        out = {
            "probe_id": PROBE_ID, "tier": "X", "status": "design_incomplete_or_fail",
            "design_mc_done": mdone, "design_stop_reasons": design_stop,
            "sanity": sanity, "wall_s": wall, "peak_rss_bytes": rss,
        }
        with open(OUT_PATH, "w") as fh:
            json.dump(out, fh, indent=2)
        print("WROTE", OUT_PATH, "status", out["status"])
        return

    d1_wk = worst_k(H1, K1)
    d2_wk = worst_k(H2, K2)

    jac_l1 = jaccard(p16["d1"], d1_wk)
    jac_l2 = jaccard(p16["d2"], d2_wk)

    arms = {
        "P16": {"d1": p16["d1"], "d2": p16["d2"]},
        "WK": {"d1": d1_wk, "d2": d2_wk},
    }
    variant_idx = {"P16": 0, "WK": 1}

    records = []
    stopped = False
    stop_reasons = []
    per_arm_op_exact = {"P16": [], "WK": []}
    per_arm_or_exact = {"P16": [], "WK": []}
    per_arm_per_seed_op_exact = {"P16": {}, "WK": {}}
    per_arm_per_seed_or_exact = {"P16": {}, "WK": {}}
    outcome_totals = {arm: {"operational": {}, "oracle": {}} for arm in arms}

    for arm_label, arm in arms.items():
        d1 = arm["d1"]
        d2 = arm["d2"]
        for si, seed in enumerate(SEEDS):
            op_exact_seed = 0
            or_exact_seed = 0
            for b in range(BLOCKS_PER_SEED):
                _, _, br = budget(t0)
                if br:
                    stopped = True
                    stop_reasons = br
                    break
                x, high, low, bob = gen_block(seed, b, pmf_sample)
                bidx = variant_idx[arm_label] * 1_000_000 + si * 1_000 + b
                r = eval_arm(arm_label, bidx, high, low, bob, high, field, p1, p2, d1, d2)
                r.update({"seed": int(seed), "block": int(b)})
                records.append(r)
                if r["operational"]["exact"]:
                    op_exact_seed += 1
                if r["oracle"]["exact"]:
                    or_exact_seed += 1
                for role in ("operational", "oracle"):
                    oc = r[role]["outcome"]
                    outcome_totals[arm_label][role][oc] = outcome_totals[arm_label][role].get(oc, 0) + 1
            per_arm_per_seed_op_exact[arm_label][int(seed)] = op_exact_seed
            per_arm_per_seed_or_exact[arm_label][int(seed)] = or_exact_seed
            per_arm_op_exact[arm_label].append(op_exact_seed)
            per_arm_or_exact[arm_label].append(or_exact_seed)
            if stopped:
                break
        if stopped:
            break

    wall, rss, br = budget(t0)
    if br:
        stop_reasons = sorted(set(stop_reasons + br))
        stopped = True

    total_blocks_per_arm = len(SEEDS) * BLOCKS_PER_SEED
    completed_per_arm = {arm: sum(per_arm_op_exact[arm]) >= 0 and
                          len([r for r in records if r["arm"] == arm]) for arm in arms}
    status = "incomplete" if stopped else "ok"

    out = {
        "probe_id": PROBE_ID, "tier": "X", "status": status,
        "reruns": 0,
        "question": ("On the same G1R2-matched synthetic channel (N=32768, explicit "
                     "1e-15 decode floor) and at the real-contract frozen K1=319/K2=6492, "
                     "how much worse (if at all) is the P16 frozen disclosure set "
                     "(derived under the old M0/'1M' prior) than a worst_k set designed "
                     "directly on THIS matched channel, under SC decoding?"),
        "stop_reasons": stop_reasons,
        "channel": {
            "name": "G1R2-matched@q1024", "q": Q, "n": N,
            "p_delta0_raw": P_RAW["p0"], "p_delta_plus1_raw": P_RAW["p1"],
            "p_delta_minus1_raw": P_RAW["pm1"], "raw_sum": RAW_SUM,
            "decode_floor": FLOOR,
            "H_floored": H, "HN_floored": HN,
            "f_book": f_book, "f_book_expected_approx": 1.273,
        },
        "k1": K1, "k2": K2, "k_total": K_TOTAL,
        "p16_source": {
            "path": "workspace-relative: .workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/"
                    "operational_f13_gate/construction_and_allocation.json (cell.l1_order/l2_order, "
                    "sliced [:k1]/[:k2] per operational_f13.py:777-778)",
            "sha256_of_file_bytes": p16["sha256_of_file_bytes"],
            "inner_freeze_sha256": p16["inner_freeze_sha256"],
            "matches_g2_freeze_digest": bool(p16["inner_freeze_sha256"] == P16_EXPECTED_DIGEST),
            "construction_protocol": p16["protocol"],
            "construction_channel_note": "source/target '1M' per operational_f13_gate/report.md -- "
                                          "an OLD M0 prior model, NOT the G1R2-matched real-CAL32 "
                                          "channel used in this probe",
            "cell_k_total": p16["cell_k_total"], "cell_leakage_bits": p16["cell_leakage_bits"],
            "cell_f_at_construction": p16["cell_f"],
        },
        "design": {
            "design_seed": DESIGN_SEED, "design_mc": DESIGN_MC, "mc_done": mdone,
            "sanity": sanity,
            "rule": "worst_k(H1,k1) / worst_k(H2,k2) via genie SC over DESIGN_MC synthetic "
                    "draws on the DECODE-floored G1R2-matched table (identical procedure to "
                    "workspace/probes/scl-gate-t3's cmd_design)",
        },
        "jaccard": {"l1": jac_l1, "l2": jac_l2},
        "seeds": list(SEEDS), "blocks_per_seed": BLOCKS_PER_SEED,
        "blocks_per_arm": total_blocks_per_arm,
        "pairing": "per (seed, block): rng=default_rng([seed, block]); draw x=integers(0,1024,N) "
                    "then delta=choice(1024,N,p=SAMPLING pmf); y=(x+delta)%1024; identical draw for "
                    "both arms at a given (seed, block)",
        "per_arm": {
            arm: {
                "operational_exact_total": sum(per_arm_op_exact[arm]),
                "operational_exact_over_total": f"{sum(per_arm_op_exact[arm])}/{total_blocks_per_arm}",
                "operational_exact_per_seed": per_arm_per_seed_op_exact[arm],
                "operational_exact_summary": summarize(per_arm_op_exact[arm]),
                "oracle_exact_total": sum(per_arm_or_exact[arm]),
                "oracle_exact_over_total": f"{sum(per_arm_or_exact[arm])}/{total_blocks_per_arm}",
                "oracle_exact_per_seed": per_arm_per_seed_or_exact[arm],
                "oracle_exact_summary": summarize(per_arm_or_exact[arm]),
                "operational_outcome_totals": outcome_totals[arm]["operational"],
                "oracle_outcome_totals": outcome_totals[arm]["oracle"],
                "d1_len": int(len(arms[arm]["d1"])), "d2_len": int(len(arms[arm]["d2"])),
            }
            for arm in arms
        },
        "records": records,
        "claims": "Tier-X non-claim planning evidence only: no threshold, no significance/"
                  "better-than-baseline/construction-invalid wording, no pass/fail verdict, no "
                  "candidate/accepted token, no attempt accounting, no real/artifact data (P16 "
                  "positions are a frozen already-materialized JSON artifact of positions/metadata, "
                  "not a live raw-data read; channel pmf is the same documented CAL32-derived "
                  "numeric parameter already used unchanged by op-n32k-matched/scl-gate-t3), writes "
                  "only under workspace/probes/p16-vs-matched-design/",
        "wall_s": wall, "peak_rss_bytes": rss,
        "within_budget": bool(status == "ok" and wall <= WALL_LIMIT_S and (rss is None or rss <= RSS_LIMIT)),
    }
    with open(OUT_PATH, "w") as fh:
        json.dump(out, fh, indent=2)
    print("WROTE", OUT_PATH, "status", out["status"], "wall_s", round(wall, 1),
          "peak_rss_GiB", round(rss / 1024**3, 3) if rss else None)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        err = {
            "probe_id": PROBE_ID, "tier": "X", "status": "execution_error",
            "error_traceback": traceback.format_exc(),
        }
        try:
            with open(PROBE_DIR + "/execution_error.json", "w") as fh:
                json.dump(err, fh, indent=2)
        except Exception:
            pass
        traceback.print_exc()
        sys.exit(1)
