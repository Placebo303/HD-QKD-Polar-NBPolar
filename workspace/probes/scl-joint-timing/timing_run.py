"""T3-budget timing probe for scl_joint (non-claim; writes only this directory).

Measures single-block wall time and peak RSS for ``scl_joint.scl_joint_decode``
at N=32768 on the G1R2-matched channel (explicit 1e-15 floor), f_book~=1.20,
at the two T3 working points:

  A (D4, k1 share 4.69%): k1=301, k2=6120 (total=6421)  -- L in {4,8,16}
  B (L2-dominated, k1 share 9%): k1=578, k2=5843 (total=6421) -- L=16 only
    (PI-approved addition, commit ae094620; SC fails at L2 on this point)

Non-protocol seed (seed=1, not one of the frozen/banned run seeds). This is a
timing/budget measurement only: no FER/efficiency/decoding-quality claim, no
pass/fail verdict, no candidate/accepted token. Writes only
``workspace/probes/scl-joint-timing/timing.json``.
"""
import json
import sys
import time
import traceback

try:
    import resource
except ImportError:
    resource = None

sys.path.insert(0, "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar")
import numpy as np

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl_joint
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as two_layer_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import apply_explicit_floor
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform

OUT = "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar/workspace/probes/scl-joint-timing/timing.json"
N = 32768
Q = 1024
ALPHA = 2
SEED = 1  # non-protocol seed, per task instruction


def g1r2_matched_table(q=Q):
    pmf_raw = np.zeros(q, dtype=np.float64)
    pmf_raw[0] = 0.7562
    pmf_raw[1 % q] = 0.0018
    pmf_raw[(q - 1) % q] = 0.2419
    pmf = apply_explicit_floor(pmf_raw, 1e-15, reason="G1R2-matched explicit floor (timing probe)")
    delta = (np.arange(q)[None, :] - np.arange(q)[:, None]) % q
    return pmf[delta], pmf


def rss_bytes():
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def run_one(field, p1, p2, pmf_row0, k1, k2, list_width_L, seed):
    rng = np.random.default_rng(seed)
    x = rng.integers(0, Q, size=N).astype(np.int64)
    delta = rng.choice(Q, size=N, p=pmf_row0).astype(np.int64)
    y = (x + delta) % Q
    high_true = (x >> 5).astype(np.int64)
    low_true = (x & 31).astype(np.int64)
    bob = y.astype(np.int64)

    # worst-first disclosure would need an H1/H2 design pass (op-n32k-matched
    # style); for a pure timing measurement we use fixed prefix disclosure
    # sets of the right size instead (decode cost depends on N and list
    # width, not on which positions are disclosed).
    d1 = np.arange(k1, dtype=np.int64)
    d2 = np.arange(k2, dtype=np.int64)
    u1_true = polar_transform(high_true, field=field, alpha=ALPHA)
    u2_true = polar_transform(low_true, field=field, alpha=ALPHA)
    val1 = u1_true[d1]
    val2 = u2_true[d2]
    labels_true = (low_true + two_layer_mod.LABEL_SCALE * high_true).astype(np.int64)
    crc_true = scl_joint.labels_crc16(labels_true)

    rss_before = rss_bytes()
    t0 = time.perf_counter()
    result = scl_joint.scl_joint_decode(
        bob, crc_true, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
        d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
        list_width_L=list_width_L, top_m=scl_joint.TOP_M_DEFAULT,
    )
    wall_s = time.perf_counter() - t0
    rss_after = rss_bytes()
    return {
        "list_width_L": list_width_L,
        "top_m": scl_joint.TOP_M_DEFAULT,
        "wall_s": wall_s,
        "rss_bytes_before": rss_before,
        "rss_bytes_after": rss_after,
        "peak_rss_bytes": rss_after,
        "crc_pass": bool(result.crc_pass),
        "label_exact": bool(result.label_hat.tolist() == labels_true.tolist()),
        "l1_survivor_count": result.l1_survivor_count,
        "candidates_considered": result.candidates_considered,
    }


def main():
    log = []
    table, pmf = g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    field = make_gf32()

    points = [
        {"label": "A_D4_k1_301_k2_6120_share_0.0469", "k1": 301, "k2": 6120, "L_list": [4, 8, 16]},
        {"label": "B_L2dominated_k1_578_k2_5843_share_0.09", "k1": 578, "k2": 5843, "L_list": [16]},
    ]

    runs = []
    for pt in points:
        for L in pt["L_list"]:
            log.append(f"starting point={pt['label']} L={L} seed={SEED}")
            print(log[-1], flush=True)
            t_point0 = time.perf_counter()
            r = run_one(field, p1, p2, pmf, pt["k1"], pt["k2"], L, SEED)
            r["point_label"] = pt["label"]
            r["k1"] = pt["k1"]
            r["k2"] = pt["k2"]
            r["seed"] = SEED
            runs.append(r)
            log.append(
                "done point=%s L=%d wall_s=%.3f rss_bytes=%s label_exact=%s crc_pass=%s"
                % (pt["label"], L, r["wall_s"], r["peak_rss_bytes"], r["label_exact"], r["crc_pass"])
            )
            print(log[-1], flush=True)

    out = {
        "probe_id": "scl-joint-timing",
        "tier": "X",
        "purpose": "T3 machine-budget estimation only; not a FER/efficiency/decoding-quality claim",
        "channel": {"name": "G1R2-matched@q1024", "q": Q, "n": N, "convention": "table[a,b]=pmf[(b-a)%q]", "floor": 1e-15},
        "field": {"name": "GF32 polynomial basis", "primitive_polynomial": 37, "alpha": ALPHA},
        "f_book_target": 1.20,
        "top_m_default": scl_joint.TOP_M_DEFAULT,
        "disclosure_note": "fixed prefix positions (0..k-1) used for this timing-only probe, not the worst_k design rule used by T3 itself; decode wall time depends on N/list-width, not on which positions are disclosed",
        "seed": SEED,
        "seed_note": "non-protocol seed=1; not FROZEN_RUN_SEED/FROZEN_TOEPLITZ_MASTER, not a banned seed",
        "runs": runs,
        "run_log": log,
        "claims": "Tier-X non-claim timing-only measurement; writes only under workspace/probes/scl-joint-timing/",
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)
    print("WROTE", OUT)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        err = {"probe_id": "scl-joint-timing", "status": "execution_error", "error_traceback": traceback.format_exc()}
        with open(OUT, "w") as fh:
            json.dump(err, fh, indent=2)
        traceback.print_exc()
        sys.exit(1)
