"""Unit test for run.py's aggregation + cross-comparison logic, using FAKE
in-memory part-file-shaped data (no real part files, no real data, no I/O
except this script's own asserts/prints). Covers every `status` branch the
real pipeline can produce: ok/exact, ok/verify_failed, ok/undetected,
ok/decode_failed (schema-completeness, never expected from SC but the
counting logic must handle it), resource_abort_wall_mid_grid (excluded from
D), and a block-level `error:*` status with an empty `grid` list (must not
crash aggregation and must not be silently counted anywhere). Also exercises
`build_cross_comparison`'s frame-range-mismatch detection and
missing-in-NB-parts detection using a hand-built fake `nb_parts` dict (NOT
read from workspace/r2_fer_shg_64/ -- that packet's real part files are
read separately, read-only, by `load_nb_parts()`, never exercised by this
synthetic test)."""
from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(THIS_DIR))

import run as drv  # noqa: E402


def _cw(applicable=80, msg_exact=80):
    return {
        "n_codewords_applicable": applicable, "n_codewords_msg_exact": msg_exact,
        "msg_exact_rate": (msg_exact / applicable) if applicable else None,
        "all_applicable_msg_exact": bool(applicable > 0 and msg_exact == applicable),
    }


def _grid_ok(margin, *, exact=False, verify_failed=False, decode_failed=False, undetected=False,
             accepted=None, ca=None):
    if accepted is None:
        accepted = exact or undetected
    return {
        "sc_margin": margin, "status": "ok",
        "sc_disclosed_total": 1000, "scl_disclosed_total": 1200,
        "tag_pass": accepted, "accepted": accepted, "exact": exact,
        "undetected": undetected, "verify_failed": verify_failed, "decode_failed": decode_failed,
        "ca_scl_descriptive": ca if ca is not None else _cw(),
    }


def _grid_abort(margin, status="resource_abort_wall_mid_grid"):
    return {"sc_margin": margin, "status": status}


FAKE_RECORDS = [
    # Block 1: G2 A1_CAL, both margins exact
    {
        "session": "G2", "global_block_index": 0, "frame_start": 0, "frame_end": 127,
        "stratum_official": "A1_CAL_characterization", "stratum_task": "never_decoded",
        "status": "ok",
        "grid": [_grid_ok(0.05, exact=True), _grid_ok(0.12, exact=True)],
    },
    # Block 2: G2 HELDOUT, margin 0.05 verify_failed, margin 0.12 resource_abort
    {
        "session": "G2", "global_block_index": 1, "frame_start": 128, "frame_end": 255,
        "stratum_official": "HELDOUT_model_selection", "stratum_task": "heldout_model_selection",
        "status": "ok",
        "grid": [_grid_ok(0.05, verify_failed=True, ca=_cw(80, 60)), _grid_abort(0.12)],
    },
    # Block 3: G2 EVAL, margin 0.05 undetected, margin 0.12 exact
    {
        "session": "G2", "global_block_index": 2, "frame_start": 256, "frame_end": 383,
        "stratum_official": "EVAL_already_decoded", "stratum_task": "previously_decoded_eval",
        "status": "ok",
        "grid": [_grid_ok(0.05, undetected=True, accepted=True), _grid_ok(0.12, exact=True)],
    },
    # Block 4: G3, block-level error, EMPTY grid -- must not crash / must not count anywhere
    {
        "session": "G3", "global_block_index": 32, "frame_start": 0, "frame_end": 127,
        "stratum_official": "A1_CAL_characterization", "stratum_task": "never_decoded",
        "status": "error:RuntimeError", "grid": [], "error": {"type": "RuntimeError", "message": "synthetic"},
    },
    # Block 5: G3 HELDOUT(pure-CHAR sub-label=never_decoded), both margins exact
    {
        "session": "G3", "global_block_index": 33, "frame_start": 128, "frame_end": 255,
        "stratum_official": "HELDOUT_model_selection", "stratum_task": "never_decoded",
        "status": "ok",
        "grid": [_grid_ok(0.05, exact=True), _grid_ok(0.12, exact=True)],
    },
    # Block 6: G3 EVAL, decode_failed schema-completeness branch (never expected from SC, must still count correctly)
    {
        "session": "G3", "global_block_index": 34, "frame_start": 256, "frame_end": 383,
        "stratum_official": "EVAL_already_decoded", "stratum_task": "previously_decoded_eval",
        "status": "ok",
        "grid": [_grid_ok(0.05, decode_failed=True), _grid_ok(0.12, exact=True)],
    },
    # Block 7 (Pre-EXECUTE round 1 C1 regression): RSS-check override.
    # status flipped to resource_abort_rss_post_decode AFTER the tag decision
    # already produced undetected=True -> the security signal must STILL be
    # caught by stop_undetected/undetected_ids and counted in `undetected`,
    # while the entry stays OUT of D (status != "ok") and is counted in
    # resource_abort.
    {
        "session": "G3", "global_block_index": 35, "frame_start": 384, "frame_end": 511,
        "stratum_official": "EVAL_already_decoded", "stratum_task": "previously_decoded_eval",
        "status": "ok",
        "grid": [dict(_grid_ok(0.05, undetected=True, accepted=True), status="resource_abort_rss_post_decode")],
    },
]


def _fake_construction(session_offset: int) -> dict:
    # Internally consistent with drv.LAYER_N/CODEWORDS_PER_LAYER/CRC_BITS so
    # the aggregation's DERIVED tag_bits-recovery arithmetic
    # (kdb_sc - sum(frozen_bits_total_sc)) is genuinely checked, not just
    # the pass-through fields (kdb_sc/f_book_sc themselves).
    fake_tag_bits = 64
    layers_05 = [{"layer_idx": i, "ber": 0.01 * (i + 1), "cap": 0.9, "k": 3000 + i} for i in range(3)]
    layers_12 = [{"layer_idx": i, "ber": 0.01 * (i + 1), "cap": 0.9, "k": 2500 + i} for i in range(3)]
    frozen_sc_05 = sum((drv.LAYER_N - ly["k"]) * drv.CODEWORDS_PER_LAYER for ly in layers_05)
    frozen_sc_12 = sum((drv.LAYER_N - ly["k"]) * drv.CODEWORDS_PER_LAYER for ly in layers_12)
    return {
        "status": "OK", "target_f": 1.27,
        "grid_points": [
            {"sc_margin": 0.05, "all_layers_usable": True, "kdb_sc": frozen_sc_05 + fake_tag_bits,
             "kdb_scl": frozen_sc_05 + fake_tag_bits + 3 * drv.CRC_BITS * drv.CODEWORDS_PER_LAYER,
             "f_book_sc": 1.20, "f_book_scl": 1.30, "layers": layers_05},
            {"sc_margin": 0.12, "all_layers_usable": True, "kdb_sc": frozen_sc_12 + fake_tag_bits,
             "kdb_scl": frozen_sc_12 + fake_tag_bits + 3 * drv.CRC_BITS * drv.CODEWORDS_PER_LAYER,
             "f_book_sc": 1.35, "f_book_scl": 1.45, "layers": layers_12},
        ],
    }


def _fake_scl_records(records):
    """Pass-2 (CA-SCL) records derived from the fake SC records: one ok entry per SC-ok grid entry."""
    out = []
    for rec in records:
        ents = [
            {"sc_margin": g["sc_margin"], "status": "ok", "ca_scl_descriptive": g["ca_scl_descriptive"]}
            for g in rec.get("grid", []) if g.get("status") == "ok"
        ]
        if ents:
            out.append({"session": rec["session"], "global_block_index": rec["global_block_index"],
                        "frame_start": rec["frame_start"], "frame_end": rec["frame_end"],
                        "status": "ok", "grid": ents, "dry_run": False})
    return out


def main() -> int:
    constructions = {"G2": _fake_construction(0), "G3": _fake_construction(32)}
    scl_records = _fake_scl_records(FAKE_RECORDS)
    results = drv.aggregate_results(FAKE_RECORDS, constructions, scl_records=scl_records)

    assert results["margins_present"] == [0.05, 0.12], results["margins_present"]
    assert results["stop_undetected"] is True, "block 3 margin 0.05 has undetected=True; must be caught"
    assert len(results["undetected_ids"]) == 2, results["undetected_ids"]  # block3 (ok) + block7 (rss-abort override)
    print(f"[agg] margins_present={results['margins_present']} stop_undetected={results['stop_undetected']}")

    by_margin = {p["sc_margin"]: p for p in results["per_margin"]}

    # margin 0.05: entries with status=="ok" across ALL 6 blocks (block4 has no
    # grid entries at all, block2's 0.12 entry is resource_abort not 0.05) ->
    # blocks 1,2,3,5,6 each contribute one 0.05 entry = 5 entries pooled.
    pooled_05 = by_margin[0.05]["taxonomy_pooled"]
    assert pooled_05["n_entries"] == 6, pooled_05
    # exact: block1(T), block5(T) = 2; verify_failed: block2(T) = 1;
    # decode_failed: block6(T) = 1; undetected: block3(T) = 1 (isolated, NOT in D)
    assert pooled_05["exact"] == 2, pooled_05
    assert pooled_05["verify_failed"] == 1, pooled_05
    assert pooled_05["decode_failed"] == 1, pooled_05
    assert pooled_05["undetected"] == 2, pooled_05  # block3 (ok) + block7 (rss-abort; still counted, isolated, not in D)
    assert pooled_05["D_valid_denominator"] == 4, pooled_05  # exact(2)+verify_failed(1)+decode_failed(1), undetected excluded
    assert pooled_05["resource_abort"] == 1, pooled_05  # block7's resource_abort_rss_post_decode
    assert pooled_05["error"] == 0, pooled_05
    print(f"[agg] margin=0.05 pooled={pooled_05}")

    # margin 0.12: block1(exact), block2(resource_abort, excluded from D but
    # counted in resource_abort), block3(exact), block5(exact), block6(exact)
    pooled_12 = by_margin[0.12]["taxonomy_pooled"]
    assert pooled_12["n_entries"] == 5, pooled_12
    assert pooled_12["exact"] == 4, pooled_12
    assert pooled_12["resource_abort"] == 1, pooled_12
    assert pooled_12["D_valid_denominator"] == 4, pooled_12
    print(f"[agg] margin=0.12 pooled={pooled_12}")

    # stratum_official breakdown sanity at margin 0.05: A1_CAL has block1(G2)+block4(G3,error,no grid)
    # -> only block1 contributes an entry -> n_entries==1, exact==1
    a1cal_05 = by_margin[0.05]["taxonomy_by_stratum_official"]["A1_CAL_characterization"]
    assert a1cal_05["n_entries"] == 1 and a1cal_05["exact"] == 1, a1cal_05
    # stratum_task at margin 0.05: never_decoded = block1(G2,A1_CAL) + block5(G3,HELDOUT/never_decoded) = 2 entries, both exact
    nd_05 = by_margin[0.05]["taxonomy_by_stratum_task"]["never_decoded"]
    assert nd_05["n_entries"] == 2 and nd_05["exact"] == 2, nd_05
    print(f"[agg] stratum breakdowns OK: A1_CAL@0.05={a1cal_05}, never_decoded@0.05={nd_05}")

    # f_breakdown: margin 0.05 must carry kdb_sc/kdb_scl/f_book_sc/f_book_scl,
    # AND the aggregation's DERIVED tag_bits recovery (kdb_sc minus the sum
    # of per-layer frozen_bits_total_sc) must reproduce the fixture's own
    # fake_tag_bits=64 exactly -- this checks the arithmetic, not just a
    # pass-through field.
    fb = by_margin[0.05]["f_breakdown_by_session"]["G2"]
    expected_kdb_sc = sum((drv.LAYER_N - 3000 - i) * drv.CODEWORDS_PER_LAYER for i in range(3)) + 64
    assert fb["kdb_sc"] == expected_kdb_sc and fb["f_book_sc"] == 1.20, (fb, expected_kdb_sc)
    assert fb["tag_bits"] == 64, fb
    print(f"[agg] f_breakdown G2@0.05={fb}")

    # ca_scl_descriptive pooling at margin 0.05: applicable across ok entries
    # block1(80,80) block2(80,60) block3(80,80) block5(80,80) block6(80,80) = 400 applicable, 380 exact
    ca_05 = pooled_05["ca_scl_descriptive"]
    assert ca_05["n_codewords_applicable"] == 400 and ca_05["n_codewords_msg_exact"] == 380, ca_05
    assert ca_05["n_sc_ok_entries"] == 5 and ca_05["n_ca_scl_ok_entries"] == 5 and ca_05["coverage"] == 1.0, ca_05
    print(f"[agg] ca_scl_descriptive pooled@0.05={ca_05}")

    # --- cross-comparison against a hand-built fake nb_parts dict ---------
    nb_parts = {
        ("G2", 0): {"status": "ok", "frame_start": 0, "frame_end": 127, "nb_sc_exact": True, "nb_scl_exact": True},
        ("G2", 1): {"status": "ok", "frame_start": 128, "frame_end": 255, "nb_sc_exact": False, "nb_scl_exact": True},
        ("G2", 2): {"status": "ok", "frame_start": 999, "frame_end": 1099, "nb_sc_exact": True, "nb_scl_exact": True},  # deliberate frame mismatch vs record's 256-383
        # ("G3", 32) is a block-level error block (skipped before the NB lookup, so NOT reported missing);
        # ("G3", 33) is deliberately OMITTED -> missing_nb
        ("G3", 34): {"status": "ok", "frame_start": 256, "frame_end": 383, "nb_sc_exact": False, "nb_scl_exact": False},
        # block 7 (rss-abort entry): present in NB parts, but the binary grid entry is not status=="ok" -> skipped, not matched
        ("G3", 35): {"status": "ok", "frame_start": 384, "frame_end": 511, "nb_sc_exact": True, "nb_scl_exact": True},
    }
    cross = drv.build_cross_comparison(FAKE_RECORDS, 0.05, nb_parts, drv._scl_index(scl_records))
    assert cross["n_blocks_missing_in_nb_parts"] == 1 and cross["missing_nb_keys"] == [("G3", 33)], cross
    assert len(cross["frame_range_mismatches"]) == 1 and cross["frame_range_mismatches"][0]["key"] == ("G2", 2), cross
    # matched (frame-consistent, both ok, margin 0.05 present) blocks: G2/0, G2/1, G3/34 = 3 (G3/32 error-skipped, G3/33 missing, G2/2 frame mismatch)
    assert cross["table_A_nb_sc_vs_binary_sc"]["n"] == 3, cross["table_A_nb_sc_vs_binary_sc"]
    # Table B2 comes from pass 2 and reports its coverage (all 3 matched blocks have an ok CA-SCL entry here)
    assert cross["table_B2_coverage"]["n_blocks_in_table_B2"] == 3 and cross["table_B2_coverage"]["n_blocks_matched_for_A_and_B1"] == 3, cross["table_B2_coverage"]
    print(f"[cross] missing={cross['n_blocks_missing_in_nb_parts']} mismatches={len(cross['frame_range_mismatches'])} table_A={cross['table_A_nb_sc_vs_binary_sc']}")

    print("[test_aggregation] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
