"""Read-only revalidation of the frozen P6 adaptive hard-L1 evidence root.

Δ successor ``NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX``.  Reads only the five
stored P6 artifacts (per-block records, transcript accounting, frozen plan,
aggregate summary, report) and recomputes coverage, accounting, all 12 frozen
integrity gates and all 4 frozen scientific gates from scratch.

The only corrected gate is ``d1_exactly_nested_and_d2_disclosed_once``: L2
disclosures are grouped by the compound ``(stream_seed, block_index, arm)``
identity instead of the pre-R1 per-stream ``(block_index, arm)`` key (block
indices repeat across the five streams).  The stored per-block records supply
the 1280 D2 arm-block obligations; the recorded transcript/recount L2 event
total independently anchors the one-disclosure-per-obligation count.  Every
other gate is recomputed with the original frozen thresholds and the scalar
projection available in the persisted artifacts (stage tuples and per-event
payloads are not persisted; their scalar consequences are checked instead).

This module is pure stdlib (json/math/hashlib/pathlib): executed as a plain
script it never imports numpy, the SC decoder, the prior/layer modules, the
RNG or the tag/development-runner code.  It refuses to run if any of those
modules is already loaded; the reported decoder/rng/tag counters are asserted
zero.  The old root is opened read-only and its file inventory (sizes and
sha256) is re-verified unchanged before the single result file is written
outside the old root.  The persisted ``BLOCKED`` field is never rewritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Frozen P6 constants and thresholds (verbatim; the plan is cross-checked
# against them rather than trusted for them).
OUTPUT_FILES = (
    "frozen_plan.json",
    "per_block_paired_outcomes.json",
    "transcript_accounting.json",
    "aggregate_summary.json",
    "report.md",
)
ARMS = ("static", "adaptive")
OUTCOMES = ("exact", "undetected", "verify_failed", "decode_failed", "resource_abort")
TAG_OUTCOMES = ("exact", "undetected", "verify_failed")
CELLS = ("both_exact", "adaptive_only", "static_only", "neither")
DISCLOSED_BITS_PER_COORDINATE = 5
TAG_BITS = 64
FEEDBACK_CONTROL_BITS = 1
STATIC_K1 = 112
FROZEN_K2 = 140
FROZEN_PAIRS = 640
STATIC_EXACT_MIN = 620
RSS_LIMIT_BYTES = 2 * 1024**3
PRIOR_ONLY = "PRIOR_ONLY"
CANDIDATE_CONDITIONED = "CANDIDATE_CONDITIONED"
D2_GATE = "d1_exactly_nested_and_d2_disclosed_once"
INTEGRITY_GATE_ORDER = (
    "pairing_coverage_complete",
    "stream_block_identity_exact",
    "result_buckets_disjoint_exhaustive",
    D2_GATE,
    "provenance_and_truth_isolation_complete",
    "undetected_zero",
    "nonfinite_zero",
    "resource_abort_zero",
    "transcript_recount_mismatch_zero",
    "tag_feedback_public_control_accounting_and_union_bound_exact",
    "wall_rss_within_frozen_limits",
    "attempt_seed_accounting_exact",
)
SCIENTIFIC_GATE_ORDER = (
    "static_exact_at_least_620_of_640",
    "adaptive_exact_equals_static_exact",
    "paired_adaptive_only_zero_and_static_only_zero",
    "leakage_100_adaptive_le_85_static",
)

# The decoder/RNG/tag path must stay unloaded in this process.
FORBIDDEN_MODULES = (
    "numpy",
    "random",
    "comparison_bench.src.comparison_bench.formal_ir.shared",
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc",
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior",
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer",
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.penalty_gate",
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.incremental",
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.adaptive_l1",
)
CALL_COUNTERS = {"decoder_calls": 0, "rng_calls": 0, "tag_calls": 0}

REPO_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_ROOT = (
    REPO_ROOT
    / ".workbuddy/queue/NBPOLAR-PHASE4-P6-ADAPTIVE-HARD-L1/paired_adaptive_gate"
)
DEFAULT_OUT = (
    REPO_ROOT
    / ".workbuddy/queue/NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX/revalidation.json"
)


def _assert_clean_runtime() -> None:
    """Fail closed if any decoder/RNG/tag module is loaded or a counter fired."""
    loaded = sorted(name for name in FORBIDDEN_MODULES if name in sys.modules)
    if loaded:
        raise SystemExit(
            "refusing to run: decoder/RNG/tag path modules are loaded: " + ", ".join(loaded)
        )
    fired = sorted(name for name, count in CALL_COUNTERS.items() if count)
    if fired:
        raise SystemExit("refusing to run: non-zero call counters: " + ", ".join(fired))


def _inventory(root: Path) -> list[dict]:
    actual = sorted(p.name for p in root.iterdir() if p.is_file())
    if actual != sorted(OUTPUT_FILES):
        raise SystemExit(f"STOP: unexpected old-root file set: {actual}")
    inventory = []
    for name in OUTPUT_FILES:
        data = (root / name).read_bytes()
        inventory.append(
            {
                "file": name,
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return inventory


def _load(root: Path) -> tuple[dict, dict, dict, dict, str]:
    def read(name):
        return json.loads((root / name).read_text(encoding="utf-8"))

    return (
        read("frozen_plan.json"),
        read("per_block_paired_outcomes.json"),
        read("transcript_accounting.json"),
        read("aggregate_summary.json"),
        (root / "report.md").read_text(encoding="utf-8"),
    )


def _static_record_ok(arm: dict, *, d1_size: int, d2_size: int, seed_bits: int) -> bool:
    """Scalar projection of the frozen static per-record structural proof."""
    if arm["outcome"] not in OUTCOMES:
        return False
    if arm["outcome"] == "resource_abort":
        return int(arm["key_dependent_bits"]) == 0 and int(arm["public_control_bits"]) == 0 and not any(
            arm[key]
            for key in (
                "exact",
                "label_match",
                "tag_pass",
                "l1_executed",
                "l1_decode_failed",
                "l2_invoked",
                "l2_decode_failed",
                "tag_invoked",
                "nonfinite",
                "truth_leak_violation",
            )
        )
    if int(arm["levels_invoked"]) != 1 or int(arm["termination_stage"]) != 1:
        return False
    if int(arm["termination_k1"]) != d1_size or int(arm["feedback_invocations"]) != 0:
        return False
    if arm["l1_provenance"] != PRIOR_ONLY:
        return False
    if bool(arm["l1_executed"]) == bool(arm["l1_decode_failed"]):
        return False
    if arm["l1_decode_failed"]:
        if arm["l2_invoked"] or arm["l2_provenance"] is not None:
            return False
        if arm["outcome"] != "decode_failed":
            return False
    else:
        if not arm["l2_invoked"] or arm["l2_provenance"] != CANDIDATE_CONDITIONED:
            return False
        if arm["l2_decode_failed"]:
            if arm["outcome"] != "decode_failed":
                return False
        else:
            if arm["outcome"] not in TAG_OUTCOMES or int(arm["tag_invocations"]) != 1:
                return False
            if arm["outcome"] == "exact" and not (arm["tag_pass"] and arm["label_match"]):
                return False
            if arm["outcome"] == "undetected" and not (arm["tag_pass"] and not arm["label_match"]):
                return False
            if arm["outcome"] == "verify_failed" and arm["tag_pass"]:
                return False
    expected = (
        DISCLOSED_BITS_PER_COORDINATE * d1_size
        + (DISCLOSED_BITS_PER_COORDINATE * d2_size if arm["l2_invoked"] else 0)
        + (TAG_BITS if arm["tag_invoked"] else 0)
    )
    if int(arm["key_dependent_bits"]) != expected:
        return False
    if bool(arm["tag_invoked"]) != (int(arm["tag_invocations"]) == 1):
        return False
    if int(arm["public_seed_bits"]) != (seed_bits if arm["tag_invoked"] else 0):
        return False
    if int(arm["feedback_bits"]) != 0 or int(arm["public_control_bits"]) != int(arm["public_seed_bits"]):
        return False
    return True


def _adaptive_record_ok(arm: dict, *, levels, d2_size: int, seed_bits: int) -> bool:
    """Scalar projection of the frozen adaptive per-record structural proof.

    Stage tuples and per-event payloads are not persisted, so the stage-level
    conditions are reduced to their scalar consequences: at most one tag per
    invoked stage, feedback only before the terminal stage, the terminal stage
    tagged on every non-failure outcome and untagged on a decode failure.
    """
    if arm["outcome"] not in OUTCOMES:
        return False
    if arm["outcome"] == "resource_abort":
        return (
            int(arm["key_dependent_bits"]) == 0
            and int(arm["public_control_bits"]) == 0
            and int(arm["levels_invoked"]) == 0
            and not any(
                arm[key]
                for key in (
                    "exact",
                    "label_match",
                    "tag_pass",
                    "l1_executed",
                    "l1_decode_failed",
                    "l2_invoked",
                    "l2_decode_failed",
                    "tag_invoked",
                    "nonfinite",
                    "truth_leak_violation",
                )
            )
        )
    stage = int(arm["termination_stage"])
    if not 1 <= stage <= len(levels):
        return False
    if int(arm["termination_k1"]) != int(levels[stage - 1]):
        return False
    if int(arm["levels_invoked"]) != stage:
        return False
    if arm["l1_provenance"] != PRIOR_ONLY:
        return False
    if bool(arm["l1_executed"]) == bool(arm["l1_decode_failed"]):
        return False
    tags = int(arm["tag_invocations"])
    feedbacks = int(arm["feedback_invocations"])
    if feedbacks > stage - 1:
        return False
    if tags > stage:
        return False
    if bool(arm["tag_invoked"]) != (tags > 0):
        return False
    if bool(arm["l2_invoked"]) != (arm["l2_provenance"] == CANDIDATE_CONDITIONED):
        return False
    if arm["l1_decode_failed"] or arm["l2_decode_failed"]:
        if arm["outcome"] != "decode_failed":
            return False
        if tags > stage - 1:  # the failing terminal stage must not carry a tag
            return False
    elif not arm["l2_invoked"]:
        if arm["outcome"] != "decode_failed":
            return False
    else:
        if arm["outcome"] not in TAG_OUTCOMES:
            return False
        if tags < 1:  # the accepting/exhausted terminal stage is tagged
            return False
        if arm["outcome"] == "exact" and not (arm["tag_pass"] and arm["label_match"]):
            return False
        if arm["outcome"] == "undetected" and not (arm["tag_pass"] and not arm["label_match"]):
            return False
        if arm["outcome"] == "verify_failed" and (arm["tag_pass"] or stage != len(levels)):
            return False
    expected = (
        DISCLOSED_BITS_PER_COORDINATE * int(arm["termination_k1"])
        + (DISCLOSED_BITS_PER_COORDINATE * d2_size if arm["l2_invoked"] else 0)
        + TAG_BITS * tags
    )
    if int(arm["key_dependent_bits"]) != expected:
        return False
    if int(arm["public_seed_bits"]) != seed_bits * tags:
        return False
    if int(arm["feedback_bits"]) != FEEDBACK_CONTROL_BITS * feedbacks:
        return False
    if int(arm["public_control_bits"]) != int(arm["public_seed_bits"]) + int(arm["feedback_bits"]):
        return False
    return True


def _nested_d1_ok(plan: dict, records: list) -> bool:
    """Recompute the nested D1 proof from the persisted plan coordinate sets."""
    levels = [int(v) for v in plan["k1_levels"]]
    assertions = plan["nested_assertions"]
    if not (
        assertions["strict_nesting"]
        and assertions["order_prefix_matches"]
        and assertions["new_coordinates_disjoint"]
    ):
        return False
    if [int(v) for v in assertions["sizes"]] != levels:
        return False
    coords = plan["disclosure_coordinates"]
    sets = {k: {int(v) for v in coords["D1_by_level"][str(k)]} for k in levels}
    new = {k: [int(v) for v in coords["D1_new_positions_by_level"][str(k)]] for k in levels}
    prev: set = set()
    seen_new: set = set()
    for k in levels:
        current = sets[k]
        if len(current) != k or not prev <= current:
            return False
        if len(current) != len(prev) + len(new[k]):
            return False
        if len(set(new[k])) != len(new[k]) or set(new[k]) & (prev | seen_new):
            return False
        seen_new |= set(new[k])
        prev = current
    if seen_new != sets[levels[-1]]:
        return False
    return all(int(r["static"]["termination_k1"]) == int(plan["static_k1"]) for r in records)


def _d2_once_ok(records: list, transcript: dict, summary: dict, k2: int) -> bool:
    """Corrected compound-identity D2-once check.

    The stored records define the 1280 ``(stream_seed, block_index, arm)``
    arm-blocks with ``l2_invoked``; the recorded transcript/recount/summary L2
    event total must equal the obligation count, and the L2 term (``5*k2``) must
    be present in every such record's key-dependent bits.
    """
    counts: dict = {}
    for record in records:
        for arm_name in ARMS:
            arm = record[arm_name]
            if not arm["l2_invoked"]:
                continue
            key = (int(record["stream_seed"]), int(record["block_index"]), arm_name)
            counts[key] = counts.get(key, 0) + 1
    expected_l2 = set(counts)
    l2_key_ok = all(
        DISCLOSED_BITS_PER_COORDINATE * int(record[arm_name]["termination_k1"])
        + DISCLOSED_BITS_PER_COORDINATE * k2
        + TAG_BITS * int(record[arm_name]["tag_invocations"])
        == int(record[arm_name]["key_dependent_bits"])
        for record in records
        for arm_name in ARMS
        if record[arm_name]["l2_invoked"]
    )
    recorded = int(transcript["event_types"]["l2_disclosure"])
    recounted = int(transcript["recount"]["event_types"]["l2_disclosure"])
    summarized = int(summary["transcript"]["event_types"]["l2_disclosure"])
    return bool(
        l2_key_ok
        and all(count == 1 for count in counts.values())
        and len(expected_l2) == len(counts) == 1280
        and recorded == recounted == summarized == len(expected_l2)
    )


def _union_bound(invoked: int) -> float:
    return min(1.0, max(0, int(invoked)) * 2.0**-64)


def recompute(root: Path) -> dict:
    plan, per_block, transcript, summary, report = _load(root)
    records = per_block["blocks"]
    seeds = [int(s) for s in plan["seeds"]]
    blocks_per_seed = int(plan["blocks_per_seed"])
    planned = int(plan["planned_pairs"])
    levels = [int(v) for v in plan["k1_levels"]]
    k2 = int(plan["k2"])
    n = int(plan["n"])
    seed_bits = 10 * n + 63
    fields = (
        "key_dependent_bits",
        "public_seed_bits",
        "feedback_bits",
        "public_control_bits",
        "tag_invocations",
        "feedback_invocations",
    )

    # Coverage / identity.
    identity = {(int(r["stream_seed"]), int(r["block_index"])) for r in records}
    expected_identity = {(s, b) for s in seeds for b in range(blocks_per_seed)}
    pairing_ok = (
        len(records) == planned == FROZEN_PAIRS
        and int(per_block["planned_pairs"]) == planned
        and int(per_block["n_blocks"]) == len(records)
    )
    identity_ok = identity == expected_identity and len(records) == len(identity)

    # Structure / buckets.
    static_records = [r["static"] for r in records]
    adaptive_records = [r["adaptive"] for r in records]
    outcomes_ok = all(a["outcome"] in OUTCOMES for a in static_records + adaptive_records)
    static_ok = all(
        _static_record_ok(a, d1_size=int(levels[-1]), d2_size=k2, seed_bits=seed_bits)
        for a in static_records
    )
    adaptive_ok = all(
        _adaptive_record_ok(a, levels=levels, d2_size=k2, seed_bits=seed_bits)
        for a in adaptive_records
    )
    bucket_sums_ok = all(
        sum(sum(1 for a in arm_records if a["outcome"] == name) for name in OUTCOMES) == planned
        for arm_records in (static_records, adaptive_records)
    )

    # Gate 4: nested D1 and corrected compound-identity D2-once.
    nested_ok = _nested_d1_ok(plan, records)
    d2_once = _d2_once_ok(records, transcript, summary, k2)

    # Provenance / truth isolation, undetected, nonfinite, resource aborts.
    provenance_ok = (
        all((not a["l1_executed"]) or a["l1_provenance"] == PRIOR_ONLY for a in static_records + adaptive_records)
        and all(
            (not a["l2_invoked"]) or a["l2_provenance"] == CANDIDATE_CONDITIONED
            for a in static_records + adaptive_records
        )
        and not any(a["truth_leak_violation"] for a in static_records + adaptive_records)
    )
    undetected_zero = not any(a["outcome"] == "undetected" for a in static_records + adaptive_records)
    nonfinite_zero = not any(a["nonfinite"] for a in static_records + adaptive_records)
    abort_zero = not any(a["outcome"] == "resource_abort" for a in static_records + adaptive_records)

    # Gate 9 and 10: independent accounting recounts.
    incremental = transcript["incremental"]
    incremental_by_arm = transcript["incremental_by_arm"]
    recount = transcript["recount"]
    recount_problems = [
        f"total:{name}"
        for name in fields
        if int(incremental[name]) != int(recount[name])
    ] + [
        f"{arm}:{name}"
        for arm in ARMS
        for name in fields
        if int(incremental_by_arm[arm][name]) != int(recount["by_arm"][arm][name])
    ]
    transcript_recount_ok = (
        int(transcript["mismatch_count"]) == 0
        and list(transcript["mismatches"]) == []
        and not recount_problems
    )
    record_sums = {
        name: sum(int(a[name]) for a in static_records + adaptive_records) for name in fields
    }
    arm_sums = {
        arm: {
            name: sum(int(a[name]) for a in (static_records if arm == "static" else adaptive_records))
            for name in fields
        }
        for arm in ARMS
    }
    record_sums_ok = all(record_sums[name] == int(incremental[name]) for name in fields) and all(
        arm_sums[arm][name] == int(incremental_by_arm[arm][name]) for arm in ARMS for name in fields
    )
    tag_bits_ok = all(
        (not a["tag_invoked"]) or int(a["public_seed_bits"]) == seed_bits * int(a["tag_invocations"])
        for a in static_records + adaptive_records
    )
    control_bits_ok = all(
        int(a["feedback_bits"]) == FEEDBACK_CONTROL_BITS * int(a["feedback_invocations"])
        for a in static_records + adaptive_records
    )
    union_bound_ok = float(transcript["union_bound"]) == _union_bound(int(recount["tag_invocations"]))
    accounting_ok = bool(
        record_sums_ok
        and tag_bits_ok
        and control_bits_ok
        and union_bound_ok
        and int(recount["tag_invocations"]) == int(incremental["tag_invocations"])
        and int(recount["feedback_invocations"]) == int(incremental["feedback_invocations"])
    )

    # Gate 11/12.
    wall_ok = float(summary["wall_s"]) <= float(plan["budget"]["total_wall_s"])
    rss = summary["rss_bytes_peak"]
    rss_ok = rss is None or int(rss) <= RSS_LIMIT_BYTES
    refused = {int(v) for v in plan["refused_run_seeds"]}
    attempt_ok = (
        int(plan["attempts_allowed"]) == 1
        and int(plan["attempts_consumed_before"]) == 0
        and int(plan["attempts_consumed_by_this_run"]) == 1
        and int(plan["retries"]) == 0
        and len(set(seeds)) == len(seeds)
        and not any(s in refused for s in seeds)
        and int(summary["attempts_consumed_by_this_run"]) == 1
        and int(summary["retries"]) == 0
    )

    integrity = {
        "pairing_coverage_complete": bool(pairing_ok),
        "stream_block_identity_exact": bool(identity_ok),
        "result_buckets_disjoint_exhaustive": bool(
            outcomes_ok and static_ok and adaptive_ok and bucket_sums_ok
        ),
        D2_GATE: bool(nested_ok and d2_once),
        "provenance_and_truth_isolation_complete": bool(provenance_ok),
        "undetected_zero": bool(undetected_zero),
        "nonfinite_zero": bool(nonfinite_zero),
        "resource_abort_zero": bool(abort_zero),
        "transcript_recount_mismatch_zero": bool(transcript_recount_ok),
        "tag_feedback_public_control_accounting_and_union_bound_exact": accounting_ok,
        "wall_rss_within_frozen_limits": bool(wall_ok and rss_ok),
        "attempt_seed_accounting_exact": bool(attempt_ok),
    }

    # Four scientific gates with the frozen thresholds verbatim.
    static_exact = sum(1 for a in static_records if a["exact"])
    adaptive_exact = sum(1 for a in adaptive_records if a["exact"])
    cells = {
        cell: sum(
            1
            for r in records
            if _cell(r["static"]["exact"], r["adaptive"]["exact"]) == cell
        )
        for cell in CELLS
    }
    static_kd = int(incremental_by_arm["static"]["key_dependent_bits"])
    adaptive_kd = int(incremental_by_arm["adaptive"]["key_dependent_bits"])
    scientific = {
        "static_exact_at_least_620_of_640": bool(planned == FROZEN_PAIRS and static_exact >= STATIC_EXACT_MIN),
        "adaptive_exact_equals_static_exact": bool(adaptive_exact == static_exact),
        "paired_adaptive_only_zero_and_static_only_zero": bool(
            cells["adaptive_only"] == 0 and cells["static_only"] == 0
        ),
        "leakage_100_adaptive_le_85_static": bool(100 * adaptive_kd <= 85 * static_kd),
    }

    # The only permitted recomputed-vs-persisted difference is the diagnosed
    # identity correction: D2 gate false in the frozen run, true after repair.
    gate_differences = [
        {
            "gate": name,
            "recomputed": bool(integrity[name]),
            "persisted": bool(summary["integrity"][name]),
        }
        for name in INTEGRITY_GATE_ORDER
        if bool(integrity[name]) != bool(summary["integrity"][name])
    ] + [
        {
            "gate": name,
            "recomputed": bool(scientific[name]),
            "persisted": bool(summary["scientific"][name]),
        }
        for name in SCIENTIFIC_GATE_ORDER
        if bool(scientific[name]) != bool(summary["scientific"][name])
    ]
    if gate_differences != [{"gate": D2_GATE, "recomputed": True, "persisted": False}]:
        raise SystemExit(
            "STOP: gate discrepancies beyond the sole identity correction: "
            f"{gate_differences}"
        )

    report_label = None
    for line in report.splitlines():
        if line.startswith("- outcome label: `"):
            report_label = line.split("`")[1]
    l2_keys = {
        (int(r["stream_seed"]), int(r["block_index"]), arm_name)
        for r in records
        for arm_name in ARMS
        if r[arm_name]["l2_invoked"]
    }
    return {
        "integrity_gates": integrity,
        "scientific_gates": scientific,
        "paired": {
            "planned_pairs": planned,
            "records": len(records),
            "unique_identities": len(identity),
            "arms_per_record": len(ARMS),
            "identity_is_exact_product": bool(identity_ok),
        },
        "outcomes": {
            arm: {name: sum(1 for a in (static_records if arm == "static" else adaptive_records) if a["outcome"] == name) for name in OUTCOMES}
            for arm in ARMS
        },
        "cells": cells,
        "disclosure": {
            "static_total_key_dependent_bits": static_kd,
            "adaptive_total_key_dependent_bits": adaptive_kd,
            "static_tag_invocations": int(incremental_by_arm["static"]["tag_invocations"]),
            "adaptive_tag_invocations": int(incremental_by_arm["adaptive"]["tag_invocations"]),
            "static_public_control_bits": int(incremental_by_arm["static"]["public_control_bits"]),
            "adaptive_public_control_bits": int(incremental_by_arm["adaptive"]["public_control_bits"]),
            "total_tag_invocations": int(incremental["tag_invocations"]),
            "total_feedback_invocations": int(incremental["feedback_invocations"]),
        },
        "l2_disclosure": {
            "arm_block_obligations": sum(
                1 for r in records for arm_name in ARMS if r[arm_name]["l2_invoked"]
            ),
            "recorded_event_total": int(transcript["event_types"]["l2_disclosure"]),
            "recounted_event_total": int(transcript["recount"]["event_types"]["l2_disclosure"]),
            "compound_identity_distinct": len(l2_keys),
        },
        "marginals": {
            "static_exact": static_exact,
            "adaptive_exact": adaptive_exact,
            "static_exact_min": STATIC_EXACT_MIN,
            "frozen_pairs": FROZEN_PAIRS,
        },
        "persisted_summary": {
            "outcome_label": summary["outcome_label"],
            "integrity_all_pass": bool(summary["integrity_all_pass"]),
            "failing_integrity_gates": list(summary["failing_integrity_gates"]),
            "scientific_all_pass": bool(summary["scientific_all_pass"]),
            "persisted_integrity_gates": dict(summary["integrity"]),
            "persisted_scientific_gates": dict(summary["scientific"]),
            "report_outcome_label": report_label,
        },
        "gate_differences_vs_persisted": gate_differences,
        "cross_checks": {
            "plan_thresholds_verbatim": bool(
                int(plan["scientific_gates"]["static_exact_min"]) == STATIC_EXACT_MIN
                and int(plan["scientific_gates"]["frozen_pairs"]) == FROZEN_PAIRS
                and int(plan["static_k1"]) == STATIC_K1
                and k2 == FROZEN_K2
            ),
            "per_block_seeds_match_plan": list(per_block["seeds"]) == seeds,
            "summary_outcomes_match_records": all(
                summary["outcomes"][arm][name]
                == sum(1 for a in (static_records if arm == "static" else adaptive_records) if a["outcome"] == name)
                for arm in ARMS
                for name in OUTCOMES
            ),
            "summary_cells_match_records": dict(summary["cells"]) == cells,
            "summary_union_bound_matches_recount": float(summary["union_bound"])
            == _union_bound(int(recount["tag_invocations"])),
            "no_l2_exhaustion_blocks_zero": int(summary["no_l2_exhaustion_blocks"]) == 0,
            "resource_stop_not_fired": summary["resource_stop_fired"] is False,
            "report_label": report_label,
            "persisted_blocked_state_exact": bool(
                summary["outcome_label"] == "BLOCKED"
                and summary["integrity_all_pass"] is False
                and list(summary["failing_integrity_gates"]) == [D2_GATE]
                and summary["scientific_all_pass"] is True
                and report_label == "BLOCKED"
            ),
        },
    }


def _cell(static_exact: bool, adaptive_exact: bool) -> str:
    if static_exact and adaptive_exact:
        return "both_exact"
    if adaptive_exact:
        return "adaptive_only"
    if static_exact:
        return "static_only"
    return "neither"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-adaptive-l1-revalidate",
        description="read-only revalidation of the frozen P6 adaptive hard-L1 root",
    )
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    out = Path(args.out)
    if root in out.parents or out == root:
        raise SystemExit("refusing to write inside the read-only old root")
    _assert_clean_runtime()
    inventory_before = _inventory(root)
    recomputed = recompute(root)
    inventory_after = _inventory(root)
    if inventory_after != inventory_before:
        raise SystemExit("STOP: old-root inventory changed during read-only revalidation")
    integrity = recomputed["integrity_gates"]
    scientific = recomputed["scientific_gates"]
    all_true = all(integrity.values()) and all(scientific.values())
    if all_true:
        result_label = "ADAPTIVE_HARD_L1_DISCLOSURE_CANDIDATE"
    else:
        earliest = next((name for name in INTEGRITY_GATE_ORDER if not integrity[name]), None)
        if earliest is None:
            earliest = next(name for name in SCIENTIFIC_GATE_ORDER if not scientific[name])
        result_label = f"BLOCKED({earliest})"
    for name, count in CALL_COUNTERS.items():
        if count:
            raise SystemExit(f"STOP: non-zero {name}")
    result = {
        "task": "NBPOLAR-PHASE4-P6R1-GATE-IDENTITY-FIX",
        "mode": "read-only-revalidation",
        "root": str(root),
        "result_label": result_label,
        "corrected_gate": {"name": D2_GATE, "value": bool(integrity[D2_GATE])},
        "original_persisted": recomputed["persisted_summary"],
        "gate_differences_vs_persisted": recomputed["gate_differences_vs_persisted"],
        "integrity_gates": integrity,
        "integrity_all_pass": bool(all(integrity.values())),
        "failing_integrity_gates": [name for name in INTEGRITY_GATE_ORDER if not integrity[name]],
        "scientific_gates": scientific,
        "scientific_all_pass": bool(all(scientific.values())),
        "paired": recomputed["paired"],
        "outcomes": recomputed["outcomes"],
        "cells": recomputed["cells"],
        "disclosure": recomputed["disclosure"],
        "l2_disclosure": recomputed["l2_disclosure"],
        "marginals": recomputed["marginals"],
        "input_inventory": inventory_before,
        "input_inventory_after": inventory_after,
        "old_root_unchanged": True,
        "counters": dict(CALL_COUNTERS),
        "attempts_consumed": 0,
        "cross_checks": recomputed["cross_checks"],
        "notes": (
            "The persisted P6 BLOCKED label and its five files are unchanged; "
            "this successor recomputes the corrected compound-identity D2 gate "
            "and every other frozen gate read-only, with zero decoder/RNG/tag "
            "calls and zero attempt consumption."
        ),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "result_label": result_label,
                "corrected_gate": bool(integrity[D2_GATE]),
                "integrity_all_pass": bool(all(integrity.values())),
                "output": str(out),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
