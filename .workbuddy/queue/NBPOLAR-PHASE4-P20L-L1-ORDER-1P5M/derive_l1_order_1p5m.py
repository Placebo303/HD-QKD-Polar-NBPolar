"""NB-Polar Phase 4-P20L Stage-A ONLY L1-order derivation (synthetic, frozen).

Produces the frozen order file ``new_l1_order_1p5m.json`` (§9 identity)
from the §3 frozen P20H calibrated prior by the accepted P13/P16 L1-genie
procedure, L1-only: model-sampled synthetic TRAIN blocks from the frozen
prior under the frozen TRAIN seeds (4 streams x 4 blocks = 16 blocks,
never a real frame, never DEV) -> true-prefix genie L1 risks per block
-> pooled means per coordinate -> worst-first ``(e, h, index)`` order.

Stage-A ONLY: the Stage-B runner (``l1_order_1p5m``) never imports this
file (asserted by its source tests) and performs zero sampling. Worktree
prior-file read only; zero protected opens; zero DEV contact.

Usage (exact Stage-A command is recorded in P20L_FREEZE.md)::

    PYTHONPATH=comparison_bench/src <venv-python> \\
        .workbuddy/queue/NBPOLAR-PHASE4-P20L-L1-ORDER-1P5M/derive_l1_order_1p5m.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

from comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.formal_ir.nbpolar.construction import (
    disclosure_order_from_stats,
    spearman_rank_corr,
    topk_overlap,
)
from comparison_bench.formal_ir.nbpolar.empirical_channel import (
    build_p1_metrics,
    sample_full_block,
)
from comparison_bench.formal_ir.nbpolar.empirical_genie_scaling import (
    genie_layer_risks,
)
from comparison_bench.formal_ir.nbpolar.per_session_calibration import (
    load_calibrated_prior,
)
from comparison_bench.formal_ir.nbpolar.prior import (
    Provenance,
    probs_to_symbol_metric,
)
from comparison_bench.formal_ir.nbpolar.sc import (
    ImpossibleDisclosedValueError,
)
from comparison_bench.formal_ir.nbpolar.transform import polar_transform

PACKET_DIR = Path(__file__).resolve().parent
PRIOR_PATH = (
    PACKET_DIR.parent
    / "NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION"
    / "per_session_calibration"
    / "calibrated_prior.npz"
)
CONSTRUCTION_PATH = (
    PACKET_DIR.parent
    / "NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13"
    / "operational_f13_gate"
    / "construction_and_allocation.json"
)
OUT_PATH = PACKET_DIR / "new_l1_order_1p5m.json"

# Frozen derivation point (packet §6; confirmed exact, never assumed).
FROZEN_PRIOR_DIGEST = (
    "e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b"
)
FROZEN_N = 32768
FROZEN_Q = 32
FROZEN_ALPHA = 2
FROZEN_TRAIN_SEEDS = (2026092271, 2026092272, 2026092273, 2026092274)
FROZEN_TRAIN_BLOCKS_PER_SEED = 4
FROZEN_K1_PREFIX_LEN = 319

PROGRAM_PIN = (
    "accepted P13/P16 L1-genie procedure L1-half: "
    "empirical_channel.sample_full_block(rng, p_b, f_prior, 32, 32, N) + "
    "transform.polar_transform(high, field, alpha=2) + "
    "prior.build_p1_metrics(bob[None,:], p1)[0] + "
    "prior.probs_to_symbol_metric(probs, provenance=PRIOR_ONLY) + "
    "empirical_genie_scaling.genie_layer_risks(logp, u1, field) + "
    "construction.disclosure_order_from_stats(e_mean, h_mean); "
    "per-stream np.random.default_rng(seed), sequential blocks, no global RNG; "
    "L2 NOT derived, K NOT reselected"
)


def main() -> int:
    start = time.perf_counter()
    if OUT_PATH.exists():
        print(f"refusing to overwrite existing order file: {OUT_PATH}", file=sys.stderr)
        return 2
    loaded = load_calibrated_prior(str(PRIOR_PATH))
    if loaded["digest"] != FROZEN_PRIOR_DIGEST:
        print(
            f"prior digest mismatch: {loaded['digest']} != {FROZEN_PRIOR_DIGEST}",
            file=sys.stderr,
        )
        return 2
    arrays = loaded["arrays"]
    p_b = np.ascontiguousarray(np.asarray(arrays["p_b"], dtype=np.float64))
    f_prior = np.ascontiguousarray(np.asarray(arrays["f_prior"], dtype=np.float64))
    p1 = np.ascontiguousarray(np.asarray(arrays["p1"], dtype=np.float64))
    field = make_gf32()

    n = FROZEN_N
    h_acc = np.zeros(n, dtype=np.float64)
    e_acc = np.zeros(n, dtype=np.float64)
    n_used = 0
    n_impossible = 0
    provenance_violations = 0
    calls = {"genie": 0}
    for seed in FROZEN_TRAIN_SEEDS:
        rng = np.random.default_rng(int(seed))
        for _ in range(FROZEN_TRAIN_BLOCKS_PER_SEED):
            bob, _a_full, high, _low = sample_full_block(
                rng, p_b, f_prior, FROZEN_Q, FROZEN_Q, n
            )
            u1 = polar_transform(high, field=field, alpha=FROZEN_ALPHA)
            l1_metric = probs_to_symbol_metric(
                build_p1_metrics(bob[None, :], p1)[0],
                provenance=Provenance.PRIOR_ONLY,
            )
            if l1_metric.provenance != Provenance.PRIOR_ONLY:
                provenance_violations += 1
            try:
                e1, h1 = genie_layer_risks(
                    l1_metric.logp, u1, field=field, calls=calls
                )
            except ImpossibleDisclosedValueError:
                n_impossible += 1
                continue
            h_acc += h1
            e_acc += e1
            n_used += 1
    if n_used < 1:
        print("no TRAIN block survived genie accumulation", file=sys.stderr)
        return 2
    if provenance_violations:
        print(
            f"provenance violations: {provenance_violations}", file=sys.stderr
        )
        return 2
    e_mean = e_acc / n_used
    h_mean = h_acc / n_used
    l1_order = np.asarray(
        disclosure_order_from_stats(e_mean, h_mean), dtype=np.int64
    )
    if l1_order.shape != (n,) or set(l1_order.tolist()) != set(range(n)):
        print("derived L1 order is not a permutation of 0..N-1", file=sys.stderr)
        return 2

    payload = {
        "protocol": "nbpolar-p20l-l1-order-1p5m",
        "kind": "l1-order-file",
        "n": int(n),
        "l1_order": [int(v) for v in l1_order.tolist()],
        "k1_frozen_prefix_len": int(FROZEN_K1_PREFIX_LEN),
        "derivation": {
            "program": PROGRAM_PIN,
            "prior_path": str(PRIOR_PATH),
            "prior_digest": str(FROZEN_PRIOR_DIGEST),
            "train_seeds": [int(s) for s in FROZEN_TRAIN_SEEDS],
            "train_blocks_per_seed": int(FROZEN_TRAIN_BLOCKS_PER_SEED),
            "train_blocks_attempted": int(
                len(FROZEN_TRAIN_SEEDS) * FROZEN_TRAIN_BLOCKS_PER_SEED
            ),
            "train_blocks_used": int(n_used),
            "train_impossible": int(n_impossible),
            "train_genie_l1_calls": int(calls.get("genie", 0)),
            "provenance_violations": int(provenance_violations),
        },
    }
    OUT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    file_digest = hashlib.sha256(OUT_PATH.read_bytes()).hexdigest()

    # Old-order对照 (P16 construction JSON, read-only): difference degree /
    # overlap coordinates / P16-L1 digest pin for independent review.
    construction_doc = json.loads(CONSTRUCTION_PATH.read_text(encoding="utf-8"))
    old_order = np.asarray(
        construction_doc["cell"]["l1_order"], dtype=np.int64
    ).ravel()
    old_digest = hashlib.sha256(
        json.dumps(
            [int(v) for v in old_order.tolist()], separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    agreement = int(np.sum(l1_order == old_order))
    k = FROZEN_K1_PREFIX_LEN
    overlap = int(len(set(l1_order[:k].tolist()) & set(old_order[:k].tolist())))
    rank_new = np.empty(n, dtype=np.float64)
    rank_old = np.empty(n, dtype=np.float64)
    rank_new[l1_order] = np.arange(n, dtype=np.float64)
    rank_old[old_order] = np.arange(n, dtype=np.float64)
    print(
        json.dumps(
            {
                "order_file": str(OUT_PATH),
                "order_file_sha256": file_digest,
                "n": int(n),
                "train_blocks_used": int(n_used),
                "train_impossible": int(n_impossible),
                "train_genie_l1_calls": int(calls.get("genie", 0)),
                "old_l1_order_digest": old_digest,
                "full_position_agreement": agreement,
                "full_position_difference": int(n - agreement),
                f"top{k}_overlap_coordinates": overlap,
                f"top{k}_overlap_fraction": overlap / float(k),
                f"top{k}_topk_overlap": float(
                    topk_overlap(l1_order, old_order, k)
                ),
                "spearman_rank_corr": float(
                    spearman_rank_corr(rank_new, rank_old)
                ),
                "wall_s": round(float(time.perf_counter() - start), 6),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
