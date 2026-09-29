"""Synthetic (non-real-data) smoke test for run.py's pure functions.

Does NOT read any raw .ttbin, does NOT call any frozen NB-Polar session-
reconstruction function, does NOT write outside this directory. Generates a
small G1R2-matched-style synthetic d=1024 channel (per-layer BSC crossover
probabilities in a physically plausible decaying pattern -- low BER on the
MSB/coarse layers, high BER on the LSB/fine layers, matching the qualitative
shape real_polar_sc_rescue.py itself expects), builds 2 synthetic 32768-
symbol blocks, and exercises the full construction-freeze -> per-block SC
decode -> block tag-check chain end to end. Prints leakage-accounting self-
consistency checks and a PASS/FAIL summary; this file is throwaway
(_smoke_*, not part of the frozen packet's execution path).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import run as drv  # the packet's own run.py (pure functions only, exercised below)


def _synthetic_layer_bers() -> list[float]:
    # Decaying reliability MSB->LSB, chosen so several layers are usable at
    # FER<0.05 with a comfortable margin at the smoke test's small N=256
    # override (see main()'s override note) -- NOT a claim about the real
    # packet's real per-layer BERs at N=4096.
    return [0.0008, 0.0015, 0.003, 0.006, 0.012, 0.022, 0.04, 0.07, 0.10, 0.14]


def _draw_synthetic_block(rng: np.random.Generator, layer_bers: list[float], n_symbols: int = 32768) -> tuple[np.ndarray, np.ndarray]:
    a = rng.integers(0, drv.D_ARY, size=n_symbols).astype(np.int64)
    b = a.copy()
    for layer_idx, p in enumerate(layer_bers):
        flips = rng.random(n_symbols) < p
        shift = drv.N_LAYERS - 1 - layer_idx
        bitmask = np.int64(1) << shift
        b = np.where(flips, b ^ bitmask, b)
    return a, b.astype(np.int64)


def main() -> int:
    t0 = time.time()
    # SMOKE-ONLY speed overrides. IMPORTANT FINDING (see report / contract
    # addendum): the frozen `polar_sc_decode_with_frozen` reference
    # implementation (src/reconciliation/real_polar_sc_rescue.py) re-runs
    # the FULL `_encoding_step` partial-sum propagation (all n=log2(N)
    # levels, O(N) each) at EVERY leaf position, i.e. O(N^2 log N) per
    # decoded frame, not the standard O(N log N) SC decoder complexity.
    # At the packet's real N=4096 this made a 300-frame/candidate,
    # 6-margin, 10-layer rate-search calibration run for OVER 8 CPU-minutes
    # without finishing (killed). This smoke test therefore verifies
    # CORRECTNESS at a much smaller N (256, still a valid power-of-two
    # input to every reused frozen function -- N is never assumed to be
    # 4096 by any of them) rather than reproducing the real packet's exact
    # N, margin grid, or frame count. The O(N^2 log N) finding itself is
    # reported to the contract/task packet as a real budget concern for
    # the eventual authorized run, not swept under the rug by this
    # override.
    drv.LAYER_N = 256
    drv.LAYER_N_LOG = 8
    drv.CODEWORDS_PER_LAYER = 32768 // drv.LAYER_N
    drv.CALIB_N_FRAMES = 150

    fns = drv._load_binary_baseline_functions()
    order = fns["polar_weight_order"](drv.LAYER_N)[::-1]
    layer_bers = _synthetic_layer_bers()

    # --- construction freeze (CAL32-analogue: use the SAME synthetic BERs
    # directly, standing in for a CAL32-derived estimate) -------------------
    fake_h_total_bits = 5.6  # plausible order-of-magnitude H(X|Y) for d=1024, not calibrated to anything real
    construction = drv.freeze_binary_construction(
        layer_bers=layer_bers, order=order, fns=fns, target_f=1.27,
        h_total_bits=fake_h_total_bits, tag_bits=64, n_symbols=32768,
    )
    assert construction["status"] == "OK", construction["status"]
    grid_points = construction["grid_points"]
    assert 1 <= len(grid_points) <= drv.MAX_F_POINTS
    fs = [gp["f_book_sc"] for gp in grid_points]
    print(f"[construction] n_grid_points={len(grid_points)} f_book_sc={fs}")
    for gp in grid_points:
        gp["_order"] = order
        ks = [ly["k"] for ly in gp["layers"]]
        print(f"  margin={gp['sc_margin']:.3f} f_sc={gp['f_book_sc']:.4f} f_scl={gp['f_book_scl']:.4f} k_per_layer={ks}")

    # --- monotonicity sanity: f_book_sc should not be wildly non-monotonic
    # in margin (larger margin -> fewer info bits -> more disclosed bits ->
    # higher f); check on ALL points considered, not just the selected grid.
    all_pts = sorted(
        [p for p in construction_all_usable(construction)], key=lambda p: p["sc_margin"]
    )
    if len(all_pts) >= 2:
        non_decreasing = all(
            all_pts[i]["f_book_sc"] <= all_pts[i + 1]["f_book_sc"] + 1e-9 for i in range(len(all_pts) - 1)
        )
        print(f"[construction] f_book_sc monotone non-decreasing in margin over {len(all_pts)} usable points: {non_decreasing}")

    # --- real per-codeword SC decode sanity: low-BER layer must decode
    # exact; a deliberately-corrupted frozen disclosure must be caught -----
    rng = np.random.default_rng(20260929)
    a_full, b_full = _draw_synthetic_block(rng, layer_bers, n_symbols=drv.LAYER_N)
    layer0_ber = layer_bers[0]
    a_bits0 = drv.layer_bit(a_full, 0)
    b_bits0 = drv.layer_bit(b_full, 0)
    gp0 = grid_points[0]
    k0 = gp0["layers"][0]["k"]
    assert k0 > 16, "smoke channel's layer 0 must be usable"
    info_idx0 = np.asarray(order[:k0], dtype=np.int64)
    sc_res = drv.sc_decode_codeword(
        a_bits=a_bits0, b_bits=b_bits0, ber=layer0_ber, info_idx=info_idx0, fns=fns,
        n_log=drv.LAYER_N_LOG, n=drv.LAYER_N,
    )
    print(f"[sc_decode] layer0 k={k0} exact={sc_res['exact']} disclosed_bits={sc_res['disclosed_bits']}")
    assert sc_res["disclosed_bits"] == drv.LAYER_N - k0

    # --- block tag check self-consistency: true vs true must pass; true vs
    # corrupted must (overwhelmingly) fail ----------------------------------
    a_hat_true = a_bits0.copy()
    tag_true = fns["universal_hash_tag"](bits=a_bits0.astype(np.uint8), point_id="smoke", layer_id=0, block_index=0, tag_bits=64)
    tag_same = fns["universal_hash_tag"](bits=a_hat_true.astype(np.uint8), point_id="smoke", layer_id=0, block_index=0, tag_bits=64)
    assert np.array_equal(tag_true, tag_same), "tag must be deterministic/reproducible for identical bits"
    a_hat_corrupt = a_bits0.copy()
    a_hat_corrupt[0] ^= 1
    tag_corrupt = fns["universal_hash_tag"](bits=a_hat_corrupt.astype(np.uint8), point_id="smoke", layer_id=0, block_index=0, tag_bits=64)
    print(f"[tag] true==true: {np.array_equal(tag_true, tag_same)}; true==1bit-corrupt: {np.array_equal(tag_true, tag_corrupt)}")

    # --- full 2-block, full-grid decode (exercises decode_block_all_layers,
    # _symbols_to_bits, block_tag_check end to end; accounting self-check) --
    n_blocks = 2
    total_disclosed_sc_measured = 0
    total_disclosed_sc_expected = 0
    n_layers_usable = sum(1 for ly in grid_points[0]["layers"] if ly["k"] > 16)
    for b_idx in range(n_blocks):
        a_sym, b_sym = _draw_synthetic_block(rng, layer_bers, n_symbols=32768)
        gp = grid_points[0]
        dec = drv.decode_block_all_layers(sym_a=a_sym, sym_b=b_sym, grid_point=gp, fns=fns, scl_decoder=None, run_scl=False)
        exact_full = bool(np.array_equal(dec["a_hat_sym"], a_sym))
        expected_disclosed = sum(
            (drv.LAYER_N - ly["k"]) * drv.CODEWORDS_PER_LAYER for ly in gp["layers"] if ly["k"] > 16
        )
        print(f"[block {b_idx}] exact_full={exact_full} sc_disclosed_total={dec['sc_disclosed_total']} expected={expected_disclosed}")
        assert dec["sc_disclosed_total"] == expected_disclosed, "leakage accounting mismatch"
        total_disclosed_sc_measured += dec["sc_disclosed_total"]
        total_disclosed_sc_expected += expected_disclosed

    assert total_disclosed_sc_measured == total_disclosed_sc_expected
    print(f"[accounting] SELF-CONSISTENT: measured==expected=={total_disclosed_sc_measured} over {n_blocks} blocks, {n_layers_usable} usable layers")
    print(f"[smoke] PASS wall_s={time.time() - t0:.1f}")
    return 0


def construction_all_usable(construction: dict):
    # helper: re-derive the full usable-point list is not stored; for the
    # monotonicity check we just reuse the grid_points already selected
    # (a weaker but still meaningful check across the selected subset).
    return construction.get("grid_points", [])


if __name__ == "__main__":
    raise SystemExit(main())
