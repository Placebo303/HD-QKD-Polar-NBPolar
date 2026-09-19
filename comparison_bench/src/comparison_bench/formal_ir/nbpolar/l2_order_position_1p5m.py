"""NB-Polar Phase 4-P20R single-factor L2-order-position on 1.5M VAL remainder.

Thin importer of the accepted ``l2_alt_hold_ir_2m`` runner (read-only; that
module and every accepted module are never edited here), with the P20Q
``_ir_hazard_diagnostics`` code point as the carried-over callsite pattern
for the mandatory IR-1..IR-5 recorder extension. Exact delta list (packet
section 2, d1-d8), nothing else:

- (d1) population -> 1.5M VAL-remainder DEV (FIRST 128 VAL-remainder frames
  2044..2171, ONE 128-frame block at N=32768, stub 2172..2212 + 2M HOLD
  remainder 3556..3644 counted never decoded); consumed 1M pool / consumed
  1.5M ranges / consumed 2M ranges excluded as consumed;
- (d2) prior/alt/frozen-A-order sources -> the P20M/P20N frozen 1.5M files
  reused read-only behind replayed ``reuse_prior_identity`` +
  ``reuse_alt_identity`` + ``reuse_order_freeze_A`` gates (digests +
  lambda-0.0/alpha-1.0/floor pins + exact key sets + H-literal recomputation
  within 1e-12 + ``p_b`` cross-check + ``p1``-equality recheck within 1e-12;
  worktree-file reads only, never the V25 counts NPZ);
- (d3) K pins -> the P20M-derived (K_total,K1,K2)=(7020,331,6689) replayed
  as literals (never recomputed, never recarried from 2M; alt-H never a
  budget input);
- (d4) orders -> DUAL: the P20M frozen ``raw_prior_orders_1p5m.json``
  (byte-identical on arms A/C; disclosed sets = first-K1 / first-K2
  prefixes) + the Stage-A ``new_l2_order_1p5m.json`` (byte-identical on
  arms B/D; first-K2 prefix at identical size K2=6689; SET-delta IS the
  factor; L1 carried frozen on all arms);
- (d5) arms A/B/C/D per packet section 6 (same K, same alpha1 tables; the
  order SET is the only delta between A and B, mirrored between C and D);
- (d6) new P20R tag domain (master 2026092340, prefix
  ``nbpolar-p20r-order-position-1p5m-seed``);
- (d7) mandatory IR-1..IR-5 recorder extension (``_ir_hazard_diagnostics``,
  same caps/formulas as P20Q section 7) computed post-decode alongside the
  nine carried scalars with the arm-specific order digest (recording-only,
  bounded, truth-isolation sentinel);
- (d8) 1.5M-VAL-remainder population + DEV/build-frames disjointness
  declared inside the TRAIN-exclusion gate (S2-ii: build subset 1.5M TRAIN
  0..1659 vs DEV subset 1.5M VAL-remainder 2044..2171).

The single new-B order permutation is derived by the frozen program
``derive_new_l2_order`` (worktree-prior arrays ONLY, deterministic, zero
sampling/genie/seeds, zero protected reads) implementing the frozen B-1
ranking functional (user decision 2026-09-19, full text in
``TASK_PACKET.md`` section 3; this module SHALL NOT invent or alter it):
rank all 32768 L2 positions by descending alt-table true-cell hazard mass
(-log2 mass at each position's true (U1_cond,B,U2) cell under p2_alt with
U1_cond = hard-L1 candidate, the same hazard definition as the IR
recorders), take the first K2=6689 positions as arm B's disclosed L2 set;
tie-break by ascending natural block coordinate. Position j is identified
with the (b,u2) cell j = b*32+u2 (C-order); U1_cond(b) = argmax_u1 p1[u1,b]
(hard-L1 candidate from the incumbent p1); p2_alt is recomputed from the
``counts_ab`` worktree array by the frozen alpha=1 rule (unit pseudocount +
1e-15 floor + column renormalize + accepted ``derive_p2``), which reproduces
the frozen alt file bit-exactly. Arm A's set stays the frozen
incumbent-order first-K2 prefix.

No SC/transform/floor-semantics/tag-semantics change; no second factor; no
lambda anywhere; no derivation or sampling at any stage beyond the frozen
deterministic permutation (genie 0+0).

Three explicit modes, never mixed: (i) Stage-A reuse verification
(``--verify-reuse``; worktree-file digest recomputation ONLY, zero
protected opens), (ii) Stage-A new-order derivation (``--derive-new-order``;
worktree-prior arrays ONLY, deterministic, zero sampling, fail-if-present
output), and (iii) Stage-B frozen command mode (all Stage-B flags required,
no production default). Mixed or ambiguous invocation refuses before
anything is read or written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ..shared import toeplitz_tag
from ..v35_algorithm_development import SOURCE_IDS
from ...io.pairs_loader import load_pairs_table, normalize_pair_columns
from . import l2_alt_hold_ir_2m as p20q
from . import l2_alt_hold_1p5m as p20n
from . import l1_order_1p5m as p20l
from . import operational_f13 as opf
from . import raw_prior_val_1p5m as p20m
from . import l2_alt_maintain_2m as p20o
from .algebra import make_gf32
from .prior import derive_p2
from .transform import polar_transform

# Reused accepted contracts (read-only; never reimplemented here).
run_operational_block = p20q.run_operational_block
run_oracle_control_block = p20q.run_oracle_control_block
OracleControlResult = p20q.OracleControlResult
verify_predecessor_construction = p20q.verify_predecessor_construction
verify_dev_manifest_1p5m = p20l.verify_dev_manifest
verify_corrected_prior_1p5m = p20m.verify_corrected_prior
verify_alt_l2_arrays_1p5m = p20n.verify_alt_l2_arrays
verify_alt_l2_identity_1p5m = p20n.verify_alt_l2_identity
verify_stage_b_order_file_p20m = p20m.verify_stage_b_order_file_p20m
feasibility_literals_1p5m = p20n.feasibility_literals
check_k_literals = p20n.check_k_literals
verify_budget_literal = p20m.verify_budget_literal
_l2_hazard_diagnostics_1p5m = p20n._l2_hazard_diagnostics
_hazard_bits = p20q._hazard_bits
_raw_p2_from_counts = p20q._raw_p2_from_counts
first_error_coordinate = p20q.first_error_coordinate
l1_prefix_positions = p20q.l1_prefix_positions
l2_prefix_positions = p20q.l2_prefix_positions
seed_bits_for = p20q.seed_bits_for
_stat_record = p20q._stat_record
_block_view = p20q._block_view
_dev_block_scoring = p20q._dev_block_scoring
_scoring_absent = p20q._scoring_absent
_selected_diagnostics = p20q._selected_diagnostics
raw_prior_val_1p5m_block_events = p20q.raw_prior_val_1p5m_block_events
raw_prior_val_1p5m_recount_events = p20q.raw_prior_val_1p5m_recount_events
ir_payload_complete = p20q.ir_payload_complete
oracle_isolation_ok_2m_names = p20q.oracle_isolation_ok
_ir_hist_edges = p20q._ir_hist_edges
_ir_hist_counts = p20q._ir_hist_counts
alt_prefloor_table = p20n.alt_prefloor_table
HAZARD_FIELDS = p20o.HAZARD_FIELDS
OPERATIONAL_PROVENANCE = p20q.OPERATIONAL_PROVENANCE
ORACLE_PROVENANCE = p20q.ORACLE_PROVENANCE
ArmSpec = p20o.ArmSpec

PROTOCOL_NAME = "nbpolar-p20r-order-position-1p5m"
MODE = "val-remainder-order-position-1p5m"

Q = p20q.Q  # 32
ALPHA = p20q.ALPHA  # 2
N_BOB = p20q.N_BOB  # 1024
FROZEN_N = 32768
FROZEN_SOURCE = "1p5M"
FROZEN_SOURCE_TAG = "type2_1p5M_20260121_183806"
FROZEN_FLOOR = 1e-15
FROZEN_ALPHA = 1.0
FROZEN_TARGET_F = 1.3
NORM_TOL = 1e-12
FROZEN_HAZARD_R = 8
FROZEN_PUBLIC_CONTROL_BITS = p20q.FROZEN_PUBLIC_CONTROL_BITS  # 327743
FROZEN_RAW_INPUT_BITS = 10 * FROZEN_N  # 327680 per block
FROZEN_L2_CONSTRUCTION = "alt-α1"

# (d1/d8) 1.5M-VAL-remainder population: FIRST 128 VAL-remainder frames in
# (frame_id, pair_idx) order (frozen VAL-remainder base 2044 = TRAIN 1660 +
# P20M DEV 384 manifest-count arithmetic: DEV 2044..2171; ONE 128-frame
# block; stub 2172..2212 counted never decoded; 1.5M TRAIN 0..1659 are the
# build frames; consumed VAL DEV 1660..2043 + consumed HOLD 2213..2766 never
# touched; 2M HOLD remainder 3556..3644 counted never decoded).
FROZEN_DEV_FRAME_RANGE = (2044, 2171)
FROZEN_DEV_FRAMES = 128
FROZEN_DEV_PAIRS = 32768
FROZEN_BLOCK_COUNT = 1
FROZEN_BLOCK_FRAMES = 128
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_BLOCK_RANGES = ((2044, 2171),)
FROZEN_REMAINDER_FRAME_RANGE = (2172, 2212)
FROZEN_REMAINDER_FRAMES = 41
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
INTRA_FILE_VAL_FRAME_RANGE = (1660, 2212)
CONSUMED_1P5M_TRAIN_FRAME_RANGE = (0, 1659)
CONSUMED_1P5M_VAL_DEV_FRAME_RANGE = (1660, 2043)
CONSUMED_1P5M_HOLD_FRAME_RANGE = (2213, 2766)
CONSUMED_1P5M_HOLD_DEV_FRAME_RANGE = (2213, 2724)
CONSUMED_1P5M_HOLD_REMAINDER_FRAME_RANGE = (2725, 2766)
# S2-ii build frames: counts/build frames hold 1.5M TRAIN 0..1659 only.
FROZEN_BUILD_FRAME_RANGE = (0, 1659)
# Counted-never-decoded 2M HOLD remainder (never contacted beyond counting).
FROZEN_2M_HOLD_REMAINDER_FRAME_RANGE = (3556, 3644)
FROZEN_2M_HOLD_REMAINDER_FRAMES = 89
FROZEN_2M_HOLD_REMAINDER_SYMBOLS = (
    FROZEN_2M_HOLD_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
)
# Consumed cross-session identities (fail-closed by source tag; frame
# integers alone are never identity).
CONSUMED_1M_SOURCE_TAG = p20o.CONSUMED_1M_SOURCE_TAG
CONSUMED_2M_SOURCE_TAG = "type2_2M_20260121_183657"
CONSUMED_1M_FRAME_RANGE = (0, 1199)
CONSUMED_2M_TRAIN_FRAME_RANGE = (0, 2186)
CONSUMED_2M_VAL_FRAME_RANGE = (2187, 2915)
CONSUMED_2M_HOLD_DEV_FRAME_RANGE = (2916, 3555)
FROZEN_MANIFEST_TRAIN_FRAMES = 1660
FROZEN_MANIFEST_TRAIN_PAIRS = 424960
FROZEN_MANIFEST_VAL_FRAMES = 553
FROZEN_MANIFEST_VAL_PAIRS = 141568
FROZEN_MANIFEST_HOLD_FRAMES = 554
FROZEN_MANIFEST_HOLD_PAIRS = 141824

# Device source identity: the 1.5M pairs parquet ONLY (same session file as
# P20M; provenance pins frozen by the v13r3fresh build-manifest cross-check;
# the 1.5M file itself is NEVER opened/statted/listed in Stage A). The
# size/sha literals below are build-manifest provenance constants; the size
# is additionally enforced from stat before the content open at run level.
FROZEN_DEV_PAIRS_PATH = p20l.FROZEN_DEV_PAIRS_PATH
FROZEN_DEV_PAIRS_SIZE = p20l.FROZEN_DEV_PAIRS_SIZE
FROZEN_DEV_PAIRS_SHA256 = p20l.FROZEN_DEV_PAIRS_SHA256
REFUSED_1M_DEV_PAIRS_PATH = p20l.REFUSED_1M_DEV_PAIRS_PATH
REFUSED_2M_DEV_PAIRS_PATH = p20l.REFUSED_2M_DEV_PAIRS_PATH
FROZEN_CONSTRUCTION_PATH = p20l.FROZEN_CONSTRUCTION_PATH
FROZEN_CONSTRUCTION_DIGEST = p20l.FROZEN_CONSTRUCTION_DIGEST
FROZEN_MANIFEST_PATH = p20l.FROZEN_MANIFEST_PATH
FROZEN_MANIFEST_SCHEMA = p20l.FROZEN_MANIFEST_SCHEMA
PAIRS_LOADER_IDENTITY = p20l.PAIRS_LOADER_IDENTITY

# (d6) new P20R tag domain.
FROZEN_TAG_MASTER = 2026092340
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = 64
SEED_PREFIX = "nbpolar-p20r-order-position-1p5m-seed"

# (d2/d3) P20M/P20N reuse pins, replayed as literals (never recomputed, never
# recarried from 2M; the alt-H literals are descriptive only, never budget
# inputs).
FROZEN_SESSION_PRIOR_DIGEST = (
    "372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac"
)
FROZEN_ORDER_DIGEST_A = (
    "a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638"
)
FROZEN_ALT_DIGEST = (
    "6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78"
)
FROZEN_H1 = 0.02519949692375297
FROZEN_H2 = 0.8003665547495433
FROZEN_H_TOTAL = 0.8255660516732963
FROZEN_BUDGET_LITERAL = (
    "1.3*32768*0.8255660516732963-64 over 5, floored, clipped [0,65536] = 7020"
)
FROZEN_K_TOTAL = 7020
FROZEN_K1 = 331
FROZEN_K2 = 6689
FROZEN_ALT_H1_INC = 0.02519949692375297
FROZEN_ALT_H2_ALT = 1.4447543021770293
FROZEN_ALT_H_TOTAL_ALT = 1.4699537991007823
# D1/D2 replay literals (P20N freeze; construction-validity quantities,
# never decoding inputs and never thresholds on results).
FROZEN_CE_ALT = 0.9027311772313849
FROZEN_CE_INCUMBENT = 0.8003665547439149
FROZEN_ALT_IDEAL_LENGTH_BITS = 29580.69521551802
FROZEN_D2_MARGIN_BITS = 3928.304784481981
FROZEN_D2_FEASIBLE = True

# Stage-A reuse products (frozen paths; digests pinned above).
FROZEN_PRIOR_PATH = p20m.FROZEN_PRIOR_PATH
FROZEN_ORDER_FILE_PATH = p20m.FROZEN_ORDER_FILE_PATH
FROZEN_ALT_PATH = p20n.FROZEN_ALT_PATH
FROZEN_NEW_ORDER_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/"
    "new_l2_order_1p5m.json"
)
# Stage-A new-B order digest pin (filled once by the frozen derivation;
# gate on equality thereafter).
FROZEN_NEW_ORDER_DIGEST_B = (
    "c78532860d74512046a1a53224bc6643de0e495614103774df67ba7e5203e751"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20R-ORDER-POSITION-1P5M/"
    "l2_order_position_1p5m"
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "input_and_predecessor_identity.json",
    "per_block_arm_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)
ATTEMPT_CONSUMPTION_POINT = "first protected content open (VAL-remainder pairs parquet)"
COMPLETE_LABEL = (
    "TARGET_EMPIRICAL_N32768_VAL_REMAINDER_ORDER_POSITION_1P5M_COMPLETE"
)

# Exact keys of the reused Stage-A artifacts (no more, no fewer).
RAW_PRIOR_NPZ_KEYS = p20m.RAW_PRIOR_NPZ_KEYS  # 10 keys
ALT_L2_NPZ_KEYS = p20n.ALT_L2_NPZ_KEYS  # 9 keys

# New-B order file identity (frozen format; mirrors the frozen-A order file
# keys with the P20R protocol + derivation provenance).
NEW_ORDER_PROTOCOL = PROTOCOL_NAME
NEW_ORDER_KIND = "new-l2-order-file"

# Frozen derivation-program pin (module + function + rule + determinism).
NEW_ORDER_PROGRAM_PIN = (
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar."
    "l2_order_position_1p5m:derive_new_l2_order -- "
    "frozen alpha=1 recompute (alt_prefloor_table + 1e-15 floor + column "
    "renormalize + accepted derive_p2) + hard-L1 argmax over incumbent p1 "
    "+ per-(b,u2)-cell hazard -log2 p2_alt[u1hard[b],b,u2] + C-order cell "
    "index j=b*32+u2 + stable descending argsort (ties ascending j); "
    "deterministic; zero sampling/genie/seeds; inputs worktree "
    "raw_prior_1p5m.npz arrays only"
)
NEW_ORDER_RANKING_FUNCTIONAL = (
    "B-1 (user decision 2026-09-19, TASK_PACKET section 3): rank all 32768 "
    "L2 positions by descending alt-table true-cell hazard mass (-log2 mass "
    "at each position's true (U1_cond,B,U2) cell under p2_alt with U1_cond = "
    "hard-L1 candidate, the same hazard definition as the IR recorders), "
    "take the first K2=6689 positions as arm B's disclosed L2 set; "
    "tie-break by ascending natural block coordinate"
)

FROZEN_ARM_NAMES = (
    "A_frozen-order_operational",
    "B_new-order_operational",
    "C_frozen-order_oracle",
    "D_new-order_oracle",
)
OPERATIONAL_ARM_NAMES = (
    "A_frozen-order_operational", "B_new-order_operational",
)
ORACLE_ARM_NAMES = (
    "C_frozen-order_oracle", "D_new-order_oracle",
)
PLANNED_SC_CALLS = 6
PLANNED_TAG_INVOCATIONS = 4
PLANNED_RECORDS = 4

# (d7) mandatory IR-1..IR-5 pins (all frozen PRESENT, bounded,
# recording-only, post-decode; same caps/formulas as P20Q section 7; the
# truth-isolation boundary is pinned in the record writers and covered by
# the sentinel test).
IR1_BINS = 64
IR1_EDGE_LO_BITS = 1e-3
IR1_EDGE_HI_BITS = 32.0
IR3_LO_MULT = 1.0
IR3_HI_MULT = 2.0
IR4_TOPK = 16
IR5_CAP = 4096
IR_FIELDS = p20q.IR_FIELDS

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "reuse_prior_identity",
    "reuse_alt_identity",
    "alt_construction_budget_feasibility_replayed",
    "dev_split_manifest_identity",
    "dev_block_range_identity",
    "order_derivation_identity",
    "frozen_order_identity_A",
    "new_order_identity_B",
    "order_derivation_program_identity",
    "k_literal_exact",
    "budget_literal_replayed",
    "target_population_contract",
    "dev_population_exact",
    "blocks_exact_with_declared_remainder",
    "four_records_exact",
    "genie_calls_exact",
    "sc_calls_exact",
    "tags_exact",
    "orders_valid_k_prefixes_within_registered_arms",
    "order_set_delta_recorded",
    "hazard_instrumentation_complete",
    "ir_payload_complete",
    "floor_hit_rate_reported",
    "oracle_isolation",
    "buckets_disjoint_exhaustive",
    "undetected_zero",
    "nonfinite_zero",
    "truth_isolation",
    "disclosure_recount_exact",
    "one_open_per_protected_input",
    "input_stat_unchanged",
    "no_unregistered_access",
    "resource_limits_met_and_no_abort",
)

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 1200.0
EXTERNAL_TIMEOUT_S = 1200
ULIMIT_VIRTUAL_KIB = 2097152

# Process-level one-open guards: set at first content load/open, never cleared.
_SESSION_PRIOR_CONTENT_LOADED = False
_ALT_CONTENT_LOADED = False
_DEV_PARQUET_CONTENT_OPENED = False


class L2OrderPosition1p5mContractError(ValueError):
    """Pre-open population/formation failure: BLOCKED(<earliest gate>)."""


class L2OrderPosition1p5mResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


def _gate_call(gate_name, fn, *args, **kwargs):
    """Run an accepted gate helper read-only, tagged with the P20R gate name."""
    try:
        return fn(*args, **kwargs)
    except (ValueError, FileNotFoundError) as exc:
        raise L2OrderPosition1p5mContractError(f"BLOCKED({gate_name}): {exc}") from exc


def pins_frozen() -> dict:
    """Fail-closed Stage-A pin-state check: every pin must be filled."""
    pins = {
        "session_prior_digest": FROZEN_SESSION_PRIOR_DIGEST,
        "order_digest_A": FROZEN_ORDER_DIGEST_A,
        "new_order_digest_B": FROZEN_NEW_ORDER_DIGEST_B,
        "alt_digest": FROZEN_ALT_DIGEST,
        "h1": FROZEN_H1,
        "h2": FROZEN_H2,
        "h_total": FROZEN_H_TOTAL,
        "k_total": FROZEN_K_TOTAL,
        "k1": FROZEN_K1,
        "k2": FROZEN_K2,
        "d2_feasible": FROZEN_D2_FEASIBLE,
        "tag_master": FROZEN_TAG_MASTER,
    }
    missing = sorted(name for name, value in pins.items() if value is None)
    if missing:
        raise ValueError(
            "Stage-A freeze not yet applied: pins None: " + ",".join(missing)
        )
    return pins


def pins_are_frozen() -> bool:
    """Non-raising pin-state probe (test seam for the pre/post-fill states)."""
    try:
        pins_frozen()
    except ValueError:
        return False
    return True


# ---------------------------------------------------------------------------
# (d5) arms: four hardcoded specs, never CLI-tunable, never extensible.
# Construction, K sizes, floor and decoder are byte-identical between A and
# B; the disclosed-L2 SET delta IS the factor (mirrored between C and D).
# ---------------------------------------------------------------------------

def planned_totals(k1: int, k2: int) -> dict:
    """Frozen section 5 planned disclosure totals from the carried integers."""
    k1, k2 = int(k1), int(k2)
    if k1 < 0 or k2 < 0:
        raise ValueError(f"planned point must be non-negative, got {(k1, k2)}")
    k_total = k1 + k2
    key_total = FROZEN_BLOCK_COUNT * (
        2 * (5 * k_total + 64) + 2 * (5 * k2 + 64)
    )
    return {
        "k1": k1,
        "k2": k2,
        "k_total": k_total,
        "operational_key_dependent_bits": 5 * k_total + 64,
        "oracle_key_dependent_bits": 5 * k2 + 64,
        "planned_key_dependent_bits": int(key_total),
        "planned_public_control_bits": int(
            PLANNED_TAG_INVOCATIONS * FROZEN_PUBLIC_CONTROL_BITS),
        "planned_sc_calls": PLANNED_SC_CALLS,
        "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
        "planned_records": PLANNED_RECORDS,
    }


def frozen_arm_table() -> tuple:
    """Materialize the four hardcoded arms from the Stage-A pins."""
    pins = pins_frozen()
    k1, k2 = int(pins["k1"]), int(pins["k2"])
    k_total = int(pins["k_total"])
    if k1 + k2 != k_total:
        raise ValueError(
            f"Stage-A pins inconsistent: K1+K2={k1 + k2} != K_total={k_total}")
    return (
        ArmSpec("A_frozen-order_operational", "operational", k1, k2,
                5 * k_total + 64, OPERATIONAL_PROVENANCE, "alt"),
        ArmSpec("B_new-order_operational", "operational", k1, k2,
                5 * k_total + 64, OPERATIONAL_PROVENANCE, "alt"),
        ArmSpec("C_frozen-order_oracle", "oracle_control", 0, k2,
                5 * k2 + 64, ORACLE_PROVENANCE, "alt"),
        ArmSpec("D_new-order_oracle", "oracle_control", 0, k2,
                5 * k2 + 64, ORACLE_PROVENANCE, "alt"),
    )


def check_frozen_arm_table() -> dict:
    """Fail-closed pin of the four frozen arms and their design accounting.

    Pure code-level check (no I/O): arm names/order, the Stage-A replayed
    (K1,K2,K_total), the 5K+64 leakage arithmetic, the frozen alpha1
    construction on all four arms (A/C frozen order, B/D new order, SAME K),
    the B-A / D-C exact zero key-bit deltas and the 6 SC / 4 tag / 4 record
    design totals. Any drift raises before any root exists.
    """
    arms = frozen_arm_table()
    if tuple(spec.name for spec in arms) != FROZEN_ARM_NAMES:
        raise ValueError(f"frozen arm order drifted: {tuple(s.name for s in arms)!r}")
    a, b, c, d = arms
    pins = pins_frozen()
    k1, k2 = int(pins["k1"]), int(pins["k2"])
    k_total = int(pins["k_total"])
    if (a.kind, a.k1, a.k2, a.prior_source, a.provenance) != (
            "operational", k1, k2, "alt", OPERATIONAL_PROVENANCE):
        raise ValueError("frozen A_frozen-order_operational arm drifted")
    if (b.kind, b.k1, b.k2, b.prior_source, b.provenance) != (
            "operational", k1, k2, "alt", OPERATIONAL_PROVENANCE):
        raise ValueError("frozen B_new-order_operational arm drifted")
    if (c.kind, c.k1, c.k2, c.prior_source, c.provenance) != (
            "oracle_control", 0, k2, "alt", ORACLE_PROVENANCE):
        raise ValueError("frozen C_frozen-order_oracle arm drifted")
    if (d.kind, d.k1, d.k2, d.prior_source, d.provenance) != (
            "oracle_control", 0, k2, "alt", ORACLE_PROVENANCE):
        raise ValueError("frozen D_new-order_oracle arm drifted")
    if int(a.k1) + int(a.k2) != k_total:
        raise ValueError("frozen A K1+K2 != Stage-A K_total")
    if int(a.leakage_bits) != 5 * k_total + 64:
        raise ValueError("frozen A/B leakage != 5*(K1+K2)+64")
    if int(c.leakage_bits) != 5 * k2 + 64:
        raise ValueError("frozen C/D leakage != 5*K2+64")
    if int(b.leakage_bits) - int(a.leakage_bits) != 0:
        raise ValueError("frozen B-vs-A key-bit delta must be exactly 0")
    if int(d.leakage_bits) - int(c.leakage_bits) != 0:
        raise ValueError("frozen D-vs-C key-bit delta must be exactly 0")
    if PLANNED_SC_CALLS != 6:
        raise ValueError(f"frozen design must plan 6 SC calls, got {PLANNED_SC_CALLS}")
    if PLANNED_TAG_INVOCATIONS != 4:
        raise ValueError(
            f"frozen design must plan 4 tags, got {PLANNED_TAG_INVOCATIONS}")
    if PLANNED_RECORDS != 4:
        raise ValueError(f"frozen design must plan 4 records, got {PLANNED_RECORDS}")
    totals = planned_totals(k1, k2)
    expected_key_total = FROZEN_BLOCK_COUNT * (
        2 * (5 * (k1 + k2) + 64) + 2 * (5 * k2 + 64))
    if int(totals["planned_key_dependent_bits"]) != int(expected_key_total):
        raise ValueError("frozen planned key-dependent total drifted")
    if int(totals["planned_public_control_bits"]) != 4 * FROZEN_PUBLIC_CONTROL_BITS:
        raise ValueError("frozen planned public total != 4*327743")
    cap_ratio = float(a.leakage_bits / FROZEN_RAW_INPUT_BITS)
    if not cap_ratio < 0.5:
        raise ValueError("frozen A/B cap must sit well below raw input bits")
    return {
        "arms": [spec.name for spec in arms],
        "a": {"k1": int(a.k1), "k2": int(a.k2), "leakage_bits": int(a.leakage_bits)},
        "b": {"k1": int(b.k1), "k2": int(b.k2), "leakage_bits": int(b.leakage_bits)},
        "c": {"k1": int(c.k1), "k2": int(c.k2), "leakage_bits": int(c.leakage_bits)},
        "d": {"k1": int(d.k1), "k2": int(d.k2), "leakage_bits": int(d.leakage_bits)},
        "public_control_bits": int(FROZEN_PUBLIC_CONTROL_BITS),
        "planned_sc_calls": PLANNED_SC_CALLS,
        "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
        "planned_records": PLANNED_RECORDS,
        "planned_key_dependent_bits": totals["planned_key_dependent_bits"],
        "planned_public_control_bits": totals["planned_public_control_bits"],
        "shared_l1_prefix": int(k1),
        "shared_l2_prefix": int(k2),
        "cap_vs_raw_ratio": cap_ratio,
    }


# ---------------------------------------------------------------------------
# Frozen CLI flag checks (all modes; all flags required, no default).
# ---------------------------------------------------------------------------

def _check_source(value) -> str:
    if value != FROZEN_SOURCE:
        raise ValueError(f"frozen point requires source={FROZEN_SOURCE!r}, got {value!r}")
    if SOURCE_IDS.get(FROZEN_SOURCE) != FROZEN_SOURCE_TAG:
        raise ValueError("frozen point source-tag identity drifted")
    return FROZEN_SOURCE


def _check_floor(value) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"frozen point requires floor={FROZEN_FLOOR}, got {value!r}") from exc
    if out != FROZEN_FLOOR:
        raise ValueError(f"frozen point requires floor={FROZEN_FLOOR}, got {out}")
    return out


def _check_n(value) -> int:
    out = opf._check_n(value)
    if int(out) != int(FROZEN_N):
        raise ValueError(f"frozen point requires n={FROZEN_N}, got {out}")
    return int(out)


def _check_k1(value) -> int:
    out = opf._as_int(value, "k1", minimum=0)
    if int(out) != int(FROZEN_K1):
        raise ValueError(f"frozen point requires k1={FROZEN_K1}, got {out}")
    return int(out)


def _check_k2(value) -> int:
    out = opf._as_int(value, "k2", minimum=0)
    if int(out) != int(FROZEN_K2):
        raise ValueError(f"frozen point requires k2={FROZEN_K2}, got {out}")
    return int(out)


def _check_tag_master(value) -> int:
    out = opf._as_int(value, "tag_master", minimum=0)
    if out != FROZEN_TAG_MASTER:
        raise ValueError(f"frozen point requires tag-master={FROZEN_TAG_MASTER}, got {out}")
    return out


def _check_dev_frames(value) -> tuple:
    try:
        pair = tuple(opf._as_int(v, "dev-frames", minimum=0) for v in value)
    except TypeError as exc:
        raise TypeError(f"dev-frames must be a pair of integers: {exc}") from exc
    if pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise ValueError(
            f"frozen point requires dev-frames={tuple(FROZEN_DEV_FRAME_RANGE)}, got {pair}"
        )
    return pair


def _check_remainder_frames(value) -> tuple:
    try:
        pair = tuple(opf._as_int(v, "remainder-frames", minimum=0) for v in value)
    except TypeError as exc:
        raise TypeError(f"remainder-frames must be a pair of integers: {exc}") from exc
    if pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise ValueError(
            "frozen point requires remainder-frames="
            f"{tuple(FROZEN_REMAINDER_FRAME_RANGE)}, got {pair}"
        )
    return pair


def _check_prior_digest(value) -> str:
    digest = str(value)
    if digest != str(FROZEN_SESSION_PRIOR_DIGEST):
        raise ValueError(
            "frozen point requires prior-digest=<Stage-A 1.5M canonical prior digest>"
        )
    return digest


def _check_order_digest_A(value) -> str:
    digest = str(value)
    if digest != str(FROZEN_ORDER_DIGEST_A):
        raise ValueError(
            "frozen point requires order-digest=<Stage-A frozen-A order-file sha256>"
        )
    return digest


def _check_new_order_digest_B(value) -> str:
    if FROZEN_NEW_ORDER_DIGEST_B is None:
        raise ValueError("Stage-A freeze not yet applied: new-B order digest pin is None")
    digest = str(value)
    if digest != str(FROZEN_NEW_ORDER_DIGEST_B):
        raise ValueError(
            "frozen point requires new-order-digest=<Stage-A new-B order-file sha256>"
        )
    return digest


def _check_alt_digest(value) -> str:
    digest = str(value)
    if digest != str(FROZEN_ALT_DIGEST):
        raise ValueError(
            "frozen point requires alt-digest=<Stage-A frozen alt-table file sha256>"
        )
    return digest


def frozen_command(*, k1=None, k2=None) -> str:
    """The frozen Stage-B command (all flags required, no default)."""
    if k1 is None:
        k1 = FROZEN_K1
    if k2 is None:
        k2 = FROZEN_K2
    if k1 is None or k2 is None or FROZEN_SESSION_PRIOR_DIGEST is None \
            or FROZEN_ALT_DIGEST is None or FROZEN_ORDER_DIGEST_A is None \
            or FROZEN_NEW_ORDER_DIGEST_B is None:
        raise ValueError("Stage-A freeze not yet applied: Stage-B pins are None")
    return (
        "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
        "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
        "ulimit -v 2097152\n"
        "timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
        "comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_order_position_1p5m "
        f"--prior {FROZEN_PRIOR_PATH} --prior-digest {FROZEN_SESSION_PRIOR_DIGEST} "
        f"--alt-prior {FROZEN_ALT_PATH} --alt-digest {FROZEN_ALT_DIGEST} "
        f"--source 1p5M --floor 1e-15 --n 32768 --k1 {int(k1)} --k2 {int(k2)} "
        f"--construction {FROZEN_CONSTRUCTION_PATH} "
        f"--construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
        f"--dev-pairs {FROZEN_DEV_PAIRS_PATH} "
        "--dev-frames 2044 2171 --block-frames 128 --remainder-frames 2172 2212 "
        "--tag-master 2026092340 --chunk-rows 512 --tag-bits 64 "
        f"--order-file {FROZEN_ORDER_FILE_PATH} --order-digest {FROZEN_ORDER_DIGEST_A} "
        f"--new-order-file {FROZEN_NEW_ORDER_PATH} "
        f"--new-order-digest {FROZEN_NEW_ORDER_DIGEST_B} "
        f"--out-dir {FROZEN_OUT_ROOT}"
    )


FROZEN_COMMAND = frozen_command() if pins_are_frozen() else None


# ---------------------------------------------------------------------------
# Stage-A new-B order derivation (section 3 contract + frozen B-1
# functional; worktree-prior arrays ONLY; deterministic; zero sampling,
# zero genie, zero protected reads).
# ---------------------------------------------------------------------------

def derive_new_l2_order(prior_arrays) -> dict:
    """Derive the alternate L2-order permutation from worktree prior arrays.

    Pure function (no I/O, no RNG, no sampler): recomputes ``p2_alt`` from
    the ``counts_ab`` array by the frozen alpha=1 rule, takes the hard-L1
    candidate ``u1hard[b] = argmax_u1 p1[u1,b]`` from the incumbent ``p1``,
    ranks the 32768 (b,u2) cells (C-order index ``j = b*32+u2``) by
    descending ``-log2 p2_alt[u1hard[b],b,u2]`` with ties broken by
    ascending ``j`` (stable descending argsort). Returns the length-32768
    new-L2 permutation plus the carried frozen L1 reference inputs needed
    by the file writer. Any non-positive table mass raises (never a silent
    fill).
    """
    if set(prior_arrays) != set(RAW_PRIOR_NPZ_KEYS):
        raise ValueError(
            f"derivation requires exactly {sorted(RAW_PRIOR_NPZ_KEYS)}, "
            f"got {sorted(prior_arrays)}"
        )
    counts_ab = np.ascontiguousarray(
        np.asarray(prior_arrays["counts_ab"], dtype=np.float64))
    if counts_ab.shape != (N_BOB, N_BOB):
        raise ValueError(f"counts_ab must be (1024,1024), got {counts_ab.shape}")
    p1 = np.ascontiguousarray(np.asarray(prior_arrays["p1"], dtype=np.float64))
    if p1.shape != (Q, N_BOB):
        raise ValueError(f"incumbent p1 must be (32,1024), got {p1.shape}")
    # Frozen alpha=1 recompute from the counts array only.
    pre = alt_prefloor_table(counts_ab)
    f_alt = np.maximum(pre, float(FROZEN_FLOOR))
    f_alt = np.ascontiguousarray(f_alt / f_alt.sum(axis=0, keepdims=True))
    p2_alt = np.ascontiguousarray(derive_p2(np.ascontiguousarray(f_alt)))
    if p2_alt.shape != (Q, N_BOB, Q):
        raise ValueError(f"recomputed p2_alt must be (32,1024,32), got {p2_alt.shape}")
    # Hard-L1 candidate per b (deterministic argmax; ties -> smallest u1).
    u1hard = np.argmax(p1, axis=0).astype(np.int64)
    if u1hard.shape != (N_BOB,):
        raise ValueError(f"hard-L1 candidate must be (1024,), got {u1hard.shape}")
    b_idx = np.arange(N_BOB, dtype=np.int64)[:, None]
    u2_idx = np.arange(Q, dtype=np.int64)[None, :]
    masses = p2_alt[u1hard[:, None], b_idx, u2_idx]
    if not np.isfinite(masses).all() or bool((masses <= 0).any()):
        raise ValueError(
            "new-order derivation: non-positive or non-finite alt-table mass "
            "at a hard-L1-conditioned cell"
        )
    hazards = -np.log2(masses)
    flat = np.ascontiguousarray(hazards.reshape(-1))
    if flat.shape != (FROZEN_N,):
        raise ValueError(f"cell hazards must be length {FROZEN_N}, got {flat.shape}")
    new_l2_order = np.argsort(-flat, kind="stable").astype(np.int64)
    if set(new_l2_order.tolist()) != set(range(FROZEN_N)):
        raise ValueError("derived new-L2 order is not a permutation of 0..N-1")
    return {
        "new_l2_order": np.ascontiguousarray(new_l2_order),
        "cell_hazards": np.ascontiguousarray(flat),
        "u1hard": np.ascontiguousarray(u1hard),
        "k2": int(FROZEN_K2),
        "program": NEW_ORDER_PROGRAM_PIN,
        "ranking_functional": NEW_ORDER_RANKING_FUNCTIONAL,
        "sampling_calls": 0,
        "genie_calls": 0,
    }


def write_new_order_file(path, *, prior_arrays, l1_order, prior_digest: str) -> dict:
    """Write the Stage-A new-B order file (fail-if-present; deterministic).

    Worktree-prior arrays ONLY (plus the frozen-A L1 carried verbatim and
    the replayed prior digest for provenance). The file holds the full L1
    (carried frozen) + new-L2 permutations plus provenance (reused-prior
    digest + program pin + zero-sampling attestation). Refuses if the
    output already exists.
    """
    out = Path(path)
    if out.exists():
        raise FileExistsError(f"refusing to overwrite existing new-order file: {out}")
    derived = derive_new_l2_order(prior_arrays)
    l1 = np.asarray(l1_order, dtype=np.int64).ravel()
    if l1.shape != (FROZEN_N,) or set(l1.tolist()) != set(range(FROZEN_N)):
        raise ValueError("carried L1 order is not a permutation of 0..N-1")
    if str(prior_digest) != str(FROZEN_SESSION_PRIOR_DIGEST):
        raise ValueError("new-order provenance prior digest != frozen reuse pin")
    doc = {
        "protocol": NEW_ORDER_PROTOCOL,
        "kind": NEW_ORDER_KIND,
        "n": int(FROZEN_N),
        "k_total": int(FROZEN_K_TOTAL),
        "k1": int(FROZEN_K1),
        "k2": int(FROZEN_K2),
        "l1_order": [int(v) for v in l1.tolist()],
        "l2_order": [int(v) for v in derived["new_l2_order"].tolist()],
        "derivation": {
            "reused_prior_digest": str(prior_digest),
            "program": NEW_ORDER_PROGRAM_PIN,
            "ranking_functional": NEW_ORDER_RANKING_FUNCTIONAL,
            "cell_convention": "j=b*32+u2 C-order over (b,u2)",
            "zero_sampling_attestation": True,
            "sampling_calls": 0,
            "genie_calls": 0,
        },
    }
    payload = json.dumps(doc, sort_keys=True) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(payload, encoding="utf-8")
    file_digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return {
        "new_order_file": str(out),
        "new_order_digest": file_digest,
        "k1": int(FROZEN_K1),
        "k2": int(FROZEN_K2),
        "program": NEW_ORDER_PROGRAM_PIN,
        "verified": True,
    }


def verify_new_order_file(path, *, expected_digest: str,
                          expected_prior_digest: str,
                          frozen_l1_order, expected_k1: int,
                          expected_k2: int, expected_k_total: int) -> dict:
    """Verify the Stage-A new-B order file (``new_order_identity_B`` gate).

    Worktree-file read only (never a protected open): the file-bytes
    sha256 must equal the frozen ``--new-order-digest`` (which itself must
    equal the Stage-A pin), the document must carry the frozen P20R
    protocol/kind with ``n == 32768``, the L2 order must be a permutation
    of ``0..N-1``, the L1 order must equal the carried frozen P20M L1 order
    array (L1-carried check), the frozen prefix lengths must equal the
    replayed (K1,K2), and the derivation provenance (reused-prior digest +
    program pin + zero-sampling attestation) must replay exactly. Any
    mismatch raises before any SC call. Stage B performs zero sampling:
    this function loads a frozen file, never a sampler.
    """
    if FROZEN_NEW_ORDER_DIGEST_B is None:
        raise ValueError("Stage-A freeze not yet applied: new-B order digest pin is None")
    if str(expected_digest) != str(FROZEN_NEW_ORDER_DIGEST_B):
        raise ValueError("new-order-file digest flag != frozen Stage-A new-B digest")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Stage-A new-B order file not found: {p}")
    raw = p.read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    if file_digest != str(expected_digest):
        raise ValueError(
            "new-order-file bytes sha256 != frozen --new-order-digest "
            "(refusing before any SC call)"
        )
    try:
        doc = json.loads(raw.decode("utf-8"))
    except ValueError as exc:
        raise ValueError(f"new-order file unreadable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("protocol") != NEW_ORDER_PROTOCOL:
        raise ValueError("new-order file protocol != frozen P20R protocol")
    if doc.get("kind") != NEW_ORDER_KIND:
        raise ValueError("new-order file kind != new-l2-order-file")
    if int(doc.get("n", -1)) != FROZEN_N:
        raise ValueError("new-order file n != frozen N")
    try:
        l1_order = np.asarray(doc["l1_order"], dtype=np.int64).ravel()
        l2_order = np.asarray(doc["l2_order"], dtype=np.int64).ravel()
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"new-order file orders malformed: {exc}") from exc
    if l2_order.shape != (FROZEN_N,) or set(l2_order.tolist()) != set(range(FROZEN_N)):
        raise ValueError("new-order file l2_order is not a permutation of 0..N-1")
    frozen_l1 = np.asarray(frozen_l1_order, dtype=np.int64).ravel()
    if l1_order.shape != (FROZEN_N,) or not np.array_equal(l1_order, frozen_l1):
        raise ValueError("new-order file l1_order != carried frozen P20M L1 order")
    if int(doc.get("k_total", -1)) != int(expected_k_total):
        raise ValueError("new-order file k_total != replayed K_total")
    if int(doc.get("k1", -1)) != int(expected_k1):
        raise ValueError("new-order file k1 != replayed K1")
    if int(doc.get("k2", -1)) != int(expected_k2):
        raise ValueError("new-order file k2 != replayed K2")
    derivation = doc.get("derivation")
    if not isinstance(derivation, dict):
        raise ValueError("new-order file derivation provenance missing")
    if str(derivation.get("reused_prior_digest")) != str(expected_prior_digest):
        raise ValueError("new-order derivation prior digest != frozen reuse pin")
    if str(derivation.get("program")) != str(NEW_ORDER_PROGRAM_PIN):
        raise ValueError("new-order derivation program pin != frozen program pin")
    if derivation.get("zero_sampling_attestation") is not True:
        raise ValueError("new-order derivation zero-sampling attestation != true")
    return {
        "new_order_file": str(p),
        "new_order_digest": file_digest,
        "n": int(FROZEN_N),
        "l1_order": np.ascontiguousarray(l1_order),
        "l2_order": np.ascontiguousarray(l2_order),
        "k_total": int(expected_k_total),
        "k1": int(expected_k1),
        "k2": int(expected_k2),
        "prior_digest": str(expected_prior_digest),
        "program": str(NEW_ORDER_PROGRAM_PIN),
        "verified": True,
    }


def order_set_delta(frozen_l2_order, new_l2_order, k2: int) -> dict:
    """Byte-exact A-vs-B disclosed-L2-set delta (the single factor).

    Pure helper (no I/O): the symmetric difference between the frozen-A
    first-K2 prefix and the new-B first-K2 prefix with full rank
    displacement (each member's rank in the other full order). Size-delta
    is exactly 0 by design.
    """
    k2 = int(k2)
    frozen = np.asarray(frozen_l2_order, dtype=np.int64).ravel()
    new = np.asarray(new_l2_order, dtype=np.int64).ravel()
    if frozen.shape != (FROZEN_N,) or new.shape != (FROZEN_N,):
        raise ValueError("order arrays must both be length-32768 permutations")
    set_a = set(int(v) for v in frozen[:k2].tolist())
    set_b = set(int(v) for v in new[:k2].tolist())
    a_minus_b = sorted(set_a - set_b)
    b_minus_a = sorted(set_b - set_a)
    rank_in_new = {int(v): i for i, v in enumerate(new.tolist())}
    rank_in_frozen = {int(v): i for i, v in enumerate(frozen.tolist())}
    return {
        "k2": k2,
        "a_disclosed_size": len(set_a),
        "b_disclosed_size": len(set_b),
        "size_delta_b_minus_a": len(set_b) - len(set_a),
        "intersection_size": len(set_a & set_b),
        "a_minus_b": a_minus_b,
        "b_minus_a": b_minus_a,
        "a_minus_b_count": len(a_minus_b),
        "b_minus_a_count": len(b_minus_a),
        "a_minus_b_ranks_in_new_order": [rank_in_new[v] for v in a_minus_b],
        "b_minus_a_ranks_in_frozen_order": [rank_in_frozen[v] for v in b_minus_a],
    }


# ---------------------------------------------------------------------------
# Stage-A reuse verification (worktree-file digest recomputation ONLY; zero
# protected opens at every stage; the V25 counts NPZ is never
# opened/statted/listed and DEV is never contacted here).
# ---------------------------------------------------------------------------

def verify_reuse(
    *,
    prior,
    alt_prior,
    order_file,
    new_order_file,
    prior_digest: str,
    alt_digest: str,
    order_digest: str,
    new_order_digest: str,
    h1: float,
    h2: float,
    h_total: float,
    k1: int,
    k2: int,
    ce_alt: float,
    ce_incumbent: float,
    alt_ideal_length_bits: float,
    d2_feasible: bool,
) -> dict:
    """Replay the P20M/P20N reuse pins from worktree files BEFORE any DEV contact.

    Loads the frozen 1.5M worktree files read-only (never the V25 counts
    NPZ, never any pairs parquet): canonical prior digest + H-literal
    recomputation within 1e-12 + ``p_b`` cross-check + floor pins (inside
    the accepted verifier), file-bytes alt/frozen-A-order digests +
    alpha-1.0/floor pins + exact key sets + ``p1``-equality within 1e-12 +
    descriptive alt-H replay, the new-B order identity (file-bytes digest +
    L1-carried + program pin + zero-sampling attestation) with the byte-exact
    A-vs-B set-delta table, K-literal replay with the S2-i budget-literal
    display, and the D1/D2 feasibility replay recomputed from the worktree
    counts. Any replay mismatch raises with DEV untouched (DEV read stays
    0/1) and no Stage-B request may follow.
    """
    with open(prior, "rb") as fh:
        data = np.load(fh, allow_pickle=False)
        with data:
            raw_arrays = {k: np.asarray(data[k]) for k in data.files}
    session_prior_verified = _gate_call(
        "reuse_prior_identity", verify_corrected_prior_1p5m,
        raw_arrays, expected_digest=str(prior_digest),
        expected_h1=float(h1), expected_h2=float(h2),
        expected_total=float(h_total))
    k_literals = _gate_call(
        "k_literal_exact", check_k_literals, k1=k1, k2=k2)
    if str(k_literals["budget_literal"]) != str(FROZEN_BUDGET_LITERAL):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(k_literal_exact): budget-literal display != frozen S2-i replay"
        )
    alt_verified = _gate_call(
        "reuse_alt_identity", verify_alt_l2_identity_1p5m, str(alt_prior),
        expected_digest=str(alt_digest), incumbent_arrays=raw_arrays)
    order_pin = _gate_call(
        "reuse_order_freeze_A", verify_stage_b_order_file_p20m, str(order_file),
        expected_digest=str(order_digest),
        expected_prior_digest=str(prior_digest),
        expected_k1=int(k1), expected_k2=int(k2),
        expected_k_total=int(k_literals["k_total"]))
    new_order_pin = _gate_call(
        "new_order_identity_B", verify_new_order_file, str(new_order_file),
        expected_digest=str(new_order_digest),
        expected_prior_digest=str(prior_digest),
        frozen_l1_order=np.asarray(order_pin["l1_order"]),
        expected_k1=int(k1), expected_k2=int(k2),
        expected_k_total=int(k_literals["k_total"]))
    program_pin = str(new_order_pin.get("program"))
    if program_pin != str(NEW_ORDER_PROGRAM_PIN):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(order_derivation_program_identity): program pin != frozen pin"
        )
    set_delta = order_set_delta(
        np.asarray(order_pin["l2_order"]), np.asarray(new_order_pin["l2_order"]),
        int(k2))
    if int(set_delta["size_delta_b_minus_a"]) != 0:
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(order_set_delta_recorded): B-A disclosed-size delta != 0"
        )
    counts_ab = np.asarray(raw_arrays["counts_ab"], dtype=np.float64)
    d1 = feasibility_literals_1p5m(
        counts_ab, p2_incumbent=np.asarray(raw_arrays["p2"]),
        p2_alt=np.asarray(alt_verified["p2_alt"]))
    replay_failing = []
    if abs(float(d1["ce_alt_insample_bits_per_symbol"]) - float(ce_alt)) > 1e-9:
        replay_failing.append("ce_alt_literal")
    if abs(float(d1["ce_incumbent_insample_bits_per_symbol"])
           - float(ce_incumbent)) > 1e-9:
        replay_failing.append("ce_incumbent_literal")
    if abs(float(d1["alt_ideal_length_bits"]) - float(alt_ideal_length_bits)) > 1e-6:
        replay_failing.append("alt_ideal_length_bits_literal")
    if bool(d1["feasible"]) is not True:
        replay_failing.append("d2_not_feasible")
    if bool(d2_feasible) is not True:
        replay_failing.append("d2_feasible_pin_not_true")
    if replay_failing:
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(alt_construction_budget_feasibility_replayed): "
            "D1/D2 replay mismatch: " + ",".join(replay_failing)
            + " (DEV untouched, no Stage-B request)"
        )
    margin = float(d1["alt_feasibility_ceiling_bits"]) - float(
        d1["alt_ideal_length_bits"])
    return {
        "prior_digest": str(session_prior_verified["digest"]),
        "h1": float(session_prior_verified["h1"]),
        "h2": float(session_prior_verified["h2"]),
        "h_total": float(session_prior_verified["h_total"]),
        "counts_total": int(session_prior_verified["counts_total"]),
        "floor_hits": int(session_prior_verified["floor_hits"]),
        "k_literals": dict(k_literals),
        "alt_file_digest": str(alt_verified["file_digest"]),
        "p1_equality_max_abs_diff": float(
            alt_verified["p1_equality_max_abs_diff"]),
        "alt_h_literals": {
            "h1_inc": float(alt_verified["h1_inc"]),
            "h2_alt": float(alt_verified["h2_alt"]),
            "h_total_alt": float(alt_verified["h_total_alt"]),
        },
        "order_digest_A": str(order_pin["order_digest"]),
        "new_order_digest_B": str(new_order_pin["new_order_digest"]),
        "new_order_program": program_pin,
        "set_delta": set_delta,
        "d1": {
            "ce_alt_insample_bits_per_symbol": float(
                d1["ce_alt_insample_bits_per_symbol"]),
            "ce_incumbent_insample_bits_per_symbol": float(
                d1["ce_incumbent_insample_bits_per_symbol"]),
            "alt_feasibility_ceiling_bits": int(
                d1["alt_feasibility_ceiling_bits"]),
            "operational_ceiling_bits": int(d1["operational_ceiling_bits"]),
            "alt_ideal_length_bits": float(d1["alt_ideal_length_bits"]),
        },
        "d2_feasible": True,
        "d2_margin_bits": margin,
        "dev_contact": 0,
        "verified": True,
    }


# ---------------------------------------------------------------------------
# (d1/d8) gate family (a)->(g): cross-file first, then intra-file
# VAL-remainder-containment, consumed-1M / consumed-1.5M / consumed-2M
# exclusions incl. the DEV/build-frames disjointness declaration (S2-ii),
# then reuse-prior + reuse-alt + frozen-A-order + new-B-order +
# derivation-program + K-literal + order-position-identity pins. All pure
# code-level checks (no I/O); any violation raises before any protected
# content open.
# ---------------------------------------------------------------------------

def verify_dev_source_identity_1p5m(dev_pairs=None) -> dict:
    """Gate (a): cross-file 1.5M source identity (FIRST, before any open)."""
    candidate = FROZEN_DEV_PAIRS_PATH if dev_pairs is None else str(dev_pairs)
    if candidate == REFUSED_1M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20R DEV source gate: 1M full-pool path refused "
            f"({REFUSED_1M_DEV_PAIRS_PATH!r}); the entire 1M pool is "
            "fail-closed against P20R DEV selection"
        )
    if candidate == REFUSED_2M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20R DEV source gate: reserved 2M path refused "
            f"({REFUSED_2M_DEV_PAIRS_PATH!r}); the entire 2M session is "
            "fail-closed against P20R DEV selection"
        )
    if candidate != FROZEN_DEV_PAIRS_PATH:
        raise ValueError(
            "frozen point requires dev-pairs="
            f"{FROZEN_DEV_PAIRS_PATH!r}, got {candidate!r}"
        )
    checks = {
        "source": FROZEN_SOURCE == "1p5M",
        "source_tag": FROZEN_SOURCE_TAG == SOURCE_IDS[FROZEN_SOURCE],
    }
    failing = sorted(name for name, ok in checks.items() if not ok)
    if failing:
        raise ValueError("P20R DEV source identity mismatch: " + ",".join(failing))
    return {
        "source": FROZEN_SOURCE,
        "source_tag": FROZEN_SOURCE_TAG,
        "dev_pairs_path": FROZEN_DEV_PAIRS_PATH,
        "dev_pairs_size_bytes": FROZEN_DEV_PAIRS_SIZE,
        "dev_pairs_sha256": FROZEN_DEV_PAIRS_SHA256,
        "build_manifest_path": FROZEN_MANIFEST_PATH,
        "refused_1m_path": REFUSED_1M_DEV_PAIRS_PATH,
        "refused_2m_path": REFUSED_2M_DEV_PAIRS_PATH,
        "verified": True,
    }


def verify_val_remainder_containment(dev_frames=None, remainder_frames=None) -> dict:
    """Gate (b): intra-file 1.5M VAL-remainder containment (VAL 1660..2212)."""
    dev_pair = (tuple(FROZEN_DEV_FRAME_RANGE) if dev_frames is None
                else tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    val_first, val_last = INTRA_FILE_VAL_FRAME_RANGE
    train_first, train_last = CONSUMED_1P5M_TRAIN_FRAME_RANGE
    hold_first, hold_last = CONSUMED_1P5M_HOLD_FRAME_RANGE
    dev_first, dev_last = dev_pair
    rem_first, rem_last = rem_pair
    for label, (start, end) in (("DEV", dev_pair), ("remainder", rem_pair)):
        if not (val_first <= start and end <= val_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"lies outside 1.5M VAL {val_first}..{val_last}"
            )
        if not (end < train_first or start > train_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"overlaps 1.5M TRAIN {train_first}..{train_last}"
            )
        if not (end < hold_first or start > hold_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"overlaps 1.5M HOLD {hold_first}..{hold_last}"
            )
    val_dev_first, val_dev_last = CONSUMED_1P5M_VAL_DEV_FRAME_RANGE
    for label, (start, end) in (("DEV", dev_pair), ("remainder", rem_pair)):
        if not (end < val_dev_first or start > val_dev_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"overlaps consumed 1.5M VAL DEV {val_dev_first}..{val_dev_last}"
            )
    if dev_pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): DEV {dev_pair} != frozen "
            f"{tuple(FROZEN_DEV_FRAME_RANGE)} (FIRST 128 VAL-remainder frames)"
        )
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): remainder {rem_pair} != frozen "
            f"{tuple(FROZEN_REMAINDER_FRAME_RANGE)}"
        )
    first = dev_first
    blocks = []
    for _ in range(FROZEN_BLOCK_COUNT):
        blocks.append((first, first + FROZEN_BLOCK_FRAMES - 1))
        first += FROZEN_BLOCK_FRAMES
    if tuple(blocks) != tuple(tuple(r) for r in FROZEN_BLOCK_RANGES):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): block decomposition "
            f"{tuple(blocks)} != frozen {tuple(tuple(r) for r in FROZEN_BLOCK_RANGES)}"
        )
    if first != rem_first:
        raise ValueError(
            "BLOCKED(dev_block_range_identity): remainder does not start where "
            "the VAL-remainder DEV block ends"
        )
    return {
        "dev_frame_range": [int(dev_first), int(dev_last)],
        "remainder_frame_range": [int(rem_first), int(rem_last)],
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "intra_file_val_frame_range": [int(val_first), int(val_last)],
        "val_remainder_contained": True,
        "train_exterior_disjoint": True,
        "hold_disjoint": True,
        "val_dev_disjoint": True,
        "first_128_val_remainder_frames": True,
        "verified": True,
    }


def verify_consumed_exclusions_val_remainder(
        dev_frames=None, remainder_frames=None) -> dict:
    """Gates (c)-(e): consumed-1M / consumed-1.5M / consumed-2M + S2-ii."""
    dev_pair = (tuple(FROZEN_DEV_FRAME_RANGE) if dev_frames is None
                else tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    ranges = [tuple(dev_pair)] + [tuple(r) for r in FROZEN_BLOCK_RANGES]
    for label, (start, end) in (
            ("consumed 1.5M TRAIN 0..1659", CONSUMED_1P5M_TRAIN_FRAME_RANGE),
            ("consumed 1.5M VAL DEV 1660..2043", CONSUMED_1P5M_VAL_DEV_FRAME_RANGE),
            ("consumed 1.5M HOLD 2213..2766", CONSUMED_1P5M_HOLD_FRAME_RANGE)):
        for r_start, r_end in ranges:
            if not (r_end < start or r_start > end):
                raise ValueError(
                    f"BLOCKED(dev_block_range_identity): declared range "
                    f"{r_start}..{r_end} overlaps {label}"
                )
    if not (rem_pair[1] < CONSUMED_1P5M_HOLD_FRAME_RANGE[0]
            or rem_pair[0] > CONSUMED_1P5M_HOLD_FRAME_RANGE[1]):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): declared stub "
            f"{rem_pair[0]}..{rem_pair[1]} overlaps consumed 1.5M HOLD"
        )
    build_first, build_last = FROZEN_BUILD_FRAME_RANGE
    dev_first, dev_last = dev_pair
    if (build_first, build_last) != CONSUMED_1P5M_TRAIN_FRAME_RANGE:
        raise ValueError("build-frames declaration drifted from 1.5M TRAIN 0..1659")
    if not (build_last < dev_first or dev_last < build_first):
        raise ValueError("DEV/build-frames disjointness violated (S2-ii)")
    if FROZEN_SOURCE_TAG == CONSUMED_1M_SOURCE_TAG \
            or FROZEN_SOURCE_TAG == CONSUMED_2M_SOURCE_TAG:
        raise ValueError("DEV source tag collides with a consumed session (impossible)")
    return {
        "build_frames": [int(build_first), int(build_last)],
        "dev_frames": [int(dev_first), int(dev_last)],
        "remainder_frames": [int(rem_pair[0]), int(rem_pair[1])],
        "dev_source_tag": FROZEN_SOURCE_TAG,
        "consumed_1m_source_tag": CONSUMED_1M_SOURCE_TAG,
        "consumed_2m_source_tag": CONSUMED_2M_SOURCE_TAG,
        "consumed_1m_frames": list(CONSUMED_1M_FRAME_RANGE),
        "consumed_1p5m_train_frames": list(CONSUMED_1P5M_TRAIN_FRAME_RANGE),
        "consumed_1p5m_val_dev_frames": list(CONSUMED_1P5M_VAL_DEV_FRAME_RANGE),
        "consumed_1p5m_hold_frames": list(CONSUMED_1P5M_HOLD_FRAME_RANGE),
        "consumed_2m_train_frames": list(CONSUMED_2M_TRAIN_FRAME_RANGE),
        "consumed_2m_val_frames": list(CONSUMED_2M_VAL_FRAME_RANGE),
        "consumed_2m_hold_dev_frames": list(CONSUMED_2M_HOLD_DEV_FRAME_RANGE),
        "hold_remainder_2m_counted_never_decoded": list(
            FROZEN_2M_HOLD_REMAINDER_FRAME_RANGE),
        "consumed_1p5m_train_disjoint": True,
        "consumed_1p5m_val_dev_disjoint": True,
        "consumed_1p5m_hold_disjoint": True,
        "consumed_1m_disjoint_by_identity": True,
        "consumed_2m_disjoint_by_identity": True,
        "stub_never_decoded": True,
        "disjoint": True,
        "verified": True,
    }


def form_val_remainder_blocks(
    table,
    *,
    dev_frames=FROZEN_DEV_FRAME_RANGE,
    block_frames: int = FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
) -> dict:
    """Deterministic 1.5M VAL-remainder development validation plus slicing."""
    try:
        pair = tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames)
    except TypeError as exc:
        raise TypeError(f"dev-frames must be a pair of integers: {exc}") from exc
    if pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"dev-frames {pair} != frozen {tuple(FROZEN_DEV_FRAME_RANGE)}"
        )
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"block-frames {block_frames} != frozen {FROZEN_BLOCK_FRAMES}"
        )
    try:
        rem_pair = tuple(opf._as_int(v, "remainder-frames", minimum=0)
                         for v in remainder_frames)
    except TypeError as exc:
        raise TypeError(f"remainder-frames must be a pair of integers: {exc}") from exc
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"remainder-frames {rem_pair} != frozen {tuple(FROZEN_REMAINDER_FRAME_RANGE)}"
        )
    try:
        frame_id = np.asarray(table["frame_id"], dtype=np.int64)
        pair_idx = np.asarray(table["pair_idx"], dtype=np.int64)
        alice = np.asarray(table["alice_symbol"], dtype=np.int64)
        bob = np.asarray(table["bob_symbol"], dtype=np.int64)
    except (KeyError, TypeError, ValueError) as exc:
        raise L2OrderPosition1p5mContractError(
            f"BLOCKED(dev_population_exact): loader frame is malformed: {exc}"
        ) from exc
    if not (frame_id.shape == pair_idx.shape == alice.shape == bob.shape) \
            or frame_id.ndim != 1:
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(dev_population_exact): column shapes disagree"
        )
    for name, values in (("alice_symbol", alice), ("bob_symbol", bob)):
        if values.size == 0 or values.min() < 0 or values.max() >= N_BOB:
            raise L2OrderPosition1p5mContractError(
                f"BLOCKED(dev_population_exact): {name} outside 0..{N_BOB - 1}"
            )
    dev_first, dev_last = pair
    pool_frame_id = np.asarray(table["frame_id"], dtype=np.int64)
    selected = (frame_id >= dev_first) & (frame_id <= dev_last)
    rows = int(np.sum(selected))
    if rows == 0:
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(dev_population_exact): no rows in the frozen DEV frame range"
        )
    frame_id = frame_id[selected]
    pair_idx = pair_idx[selected]
    alice = alice[selected]
    bob = bob[selected]
    unique_frames = np.unique(frame_id)
    if (unique_frames.size != FROZEN_DEV_FRAMES
            or int(unique_frames[0]) != dev_first
            or int(unique_frames[-1]) != dev_last):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(dev_population_exact): DEV frames "
            f"{unique_frames.size} with range {int(unique_frames[0])}.."
            f"{int(unique_frames[-1])} != frozen {FROZEN_DEV_FRAMES} with range "
            f"{dev_first}..{dev_last}"
        )
    if rows != FROZEN_DEV_PAIRS:
        raise L2OrderPosition1p5mContractError(
            f"BLOCKED(dev_population_exact): DEV rows {rows} != frozen {FROZEN_DEV_PAIRS}"
        )
    order = np.lexsort((pair_idx, frame_id))
    frame_id = frame_id[order]
    pair_idx = pair_idx[order]
    alice = alice[order]
    bob = bob[order]
    expected_pair = np.tile(
        np.arange(FROZEN_PAIRS_PER_FRAME, dtype=np.int64), FROZEN_DEV_FRAMES
    )
    if not np.array_equal(pair_idx, expected_pair):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(dev_population_exact): pair_idx is not exactly 0..255 per frame"
        )
    ranges = []
    first = dev_first
    for _ in range(FROZEN_BLOCK_COUNT):
        last = first + int(block_frames) - 1
        ranges.append((first, last))
        first = last + 1
    if tuple(ranges) != tuple(tuple(r) for r in FROZEN_BLOCK_RANGES):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): block ranges "
            f"{tuple(ranges)} != frozen {tuple(tuple(r) for r in FROZEN_BLOCK_RANGES)}"
        )
    rem_first, rem_last = rem_pair
    if first != rem_first:
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder "
            f"{rem_first}..{rem_last} does not start where the DEV block ends"
        )
    remainder_rows = (pool_frame_id >= rem_first) & (pool_frame_id <= rem_last)
    remainder_frame_ids = pool_frame_id[remainder_rows]
    if int(np.sum(remainder_rows)) != FROZEN_REMAINDER_SYMBOLS:
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder rows "
            f"{int(np.sum(remainder_rows))} != frozen {FROZEN_REMAINDER_SYMBOLS}"
        )
    if (np.unique(remainder_frame_ids).size != FROZEN_REMAINDER_FRAMES
            or int(remainder_frame_ids.min()) != rem_first
            or int(remainder_frame_ids.max()) != rem_last):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder frames "
            f"!= frozen {rem_first}..{rem_last} ({FROZEN_REMAINDER_FRAMES} frames)"
        )
    check = verify_val_remainder_containment(pair, rem_pair)
    if not check["verified"]:
        raise L2OrderPosition1p5mContractError("BLOCKED(dev_block_range_identity)")
    check2 = verify_consumed_exclusions_val_remainder(pair, rem_pair)
    if not check2["verified"]:
        raise L2OrderPosition1p5mContractError("BLOCKED(dev_block_range_identity)")
    blocks = []
    for index, (start, end) in enumerate(ranges):
        mask = (frame_id >= start) & (frame_id <= end)
        if int(np.sum(mask)) != FROZEN_SYMBOLS_PER_BLOCK:
            raise L2OrderPosition1p5mContractError(
                "BLOCKED(blocks_exact_with_declared_remainder): block "
                f"{index} holds {int(np.sum(mask))} pairs != {FROZEN_SYMBOLS_PER_BLOCK}"
            )
        blocks.append({
            "block_index": index,
            "frame_start": int(start),
            "frame_end": int(end),
            "frame_count": int(block_frames),
            "labels": alice[mask].copy(),
            "bob": bob[mask].copy(),
            "high": (alice[mask] // Q).astype(np.int64),
            "low": (alice[mask] % Q).astype(np.int64),
        })
    return {
        "dev_frame_range": [int(dev_first), int(dev_last)],
        "dev_frames": int(unique_frames.size),
        "dev_pairs": rows,
        "blocks": blocks,
        "block_ranges": [list(r) for r in ranges],
        "remainder": {
            "frame_start": int(rem_first),
            "frame_end": int(rem_last),
            "frames": FROZEN_REMAINDER_FRAMES,
            "symbols": int(np.sum(remainder_rows)),
            "used": False,
        },
    }


# ---------------------------------------------------------------------------
# (d6) P20R tag domain.
# ---------------------------------------------------------------------------

def l2_order_position_1p5m_seed_bits(master: int, n: int, arm: str, block_index: int,
                                     *, bit_length: int | None = None) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P20R domain)."""
    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P20R seed domain: {arm!r}")
    index = opf._as_int(block_index, "block_index", minimum=0)
    length = seed_bits_for(n) if bit_length is None else opf._as_int(
        bit_length, "bit_length", minimum=1)
    prefix = f"{SEED_PREFIX}:{master_seed}:{int(n)}:{arm}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < length:
        buf.extend(hashlib.sha256(
            f"{prefix}:{int(index)}:{counter}".encode("ascii")).digest())
        counter += 1
    bits = np.unpackbits(np.frombuffer(bytes(buf), dtype=np.uint8), bitorder="big")
    return bits[:length].astype(np.uint8)


# ---------------------------------------------------------------------------
# (d7) Mandatory IR-1..IR-5 recorder (recording-only, post-decode; same
# caps/formulas as P20Q section 7, K2 pinned to the 1.5M point).
# ---------------------------------------------------------------------------

def _ir_hazard_diagnostics(*, view, p2_arm, l2_order, k2, first_error,
                           prefix_mean) -> dict:
    """P20R mandatory IR recorder: IR-1..IR-5, post-decode, recording-only.

    Called after every SC call for the record has completed (after tag
    scoring) from the successor's ``_operational_record`` /
    ``_control_record`` equivalents alongside the nine carried scalars (the
    P20Q ``_ir_hazard_diagnostics`` code point is the carried-over callsite
    pattern). Reads truth (and the arm table) for RECORDING ONLY; its
    outputs are written into the record dict and are never passed to any
    decoder, metric builder, disclosure or order decision. The record's OWN
    order (frozen-A on A/C, new-B on B/D) splits every prefix flag.

    Fields (frozen semantics, same caps/formulas as P20Q section 7):
    - IR-1 ``ir1_hist_edges_bits`` (65 float64, frozen log-spaced formula)
      + ``ir1_hist_prefix_counts`` / ``ir1_hist_outside_counts`` (64 int
      each; disclosed-L2-prefix vs outside split in X-domain); every
      completed record, never null;
    - IR-2 ``ir2_first_error_hazard_rank_pct`` (fraction of block positions
      with hazard <= fail-site hazard; 1.0 = most hazardous); null unless
      ``first_error_layer == L2`` with a valid coordinate;
    - IR-3 ``ir3_thresh_lo_bits`` = 1.0 x record prefix-mean,
      ``ir3_thresh_hi_bits`` = 2.0 x record prefix-mean + above-threshold
      prefix counts/fracs; every completed record, never null;
    - IR-4 top-16 hazardous positions (coords, hazards, X-domain prefix
      flags, 1-based hazard ranks); every completed record, never null;
    - IR-5 capped series (first 4096 natural-order hazards float32 +
      prefix flags + truncation flag + total length); every completed
      record, never null.
    """
    if int(k2) != int(FROZEN_K2):
        raise ValueError(
            "IR instrumentation requires the gated prefix length "
            f"{FROZEN_K2}, got {int(k2)}"
        )
    bob = np.asarray(view["bob"], dtype=np.int64)
    high_true = np.asarray(view["high"], dtype=np.int64)
    low_true = np.asarray(view["low"], dtype=np.int64)
    n = int(bob.size)
    order = np.asarray(l2_order, dtype=np.int64)
    if order.shape != (n,):
        raise ValueError(
            f"l2_order must be a length-{n} natural block index permutation, "
            f"got shape {order.shape}"
        )
    prefix = order[:int(k2)]
    p2 = np.asarray(p2_arm, dtype=np.float64)
    u1_cond = view.get("u1_cond")
    if u1_cond is None:
        u1_cond = high_true
    u1_cond = np.asarray(u1_cond, dtype=np.int64)
    if u1_cond.shape != (n,):
        raise ValueError(f"view u1_cond must be length {n}, got {u1_cond.shape}")
    hazards = _hazard_bits(p2, u1_cond, bob, low_true)
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    edges = _ir_hist_edges()
    prefix_haz = hazards[mask]
    outside_haz = hazards[~mask]
    out = {
        "ir1_hist_edges_bits": [float(v) for v in edges],
        "ir1_hist_prefix_counts": _ir_hist_counts(prefix_haz, edges),
        "ir1_hist_outside_counts": _ir_hist_counts(outside_haz, edges),
    }
    rank_pct = None
    if first_error.get("first_error_layer") == "L2":
        pos = first_error.get("first_error_coord")
        if pos is None or not (0 <= int(pos) < n):
            raise ValueError(
                f"L2 failure requires a valid natural block symbol index, got {pos!r}"
            )
        pos = int(pos)
        rank_pct = float(np.mean(hazards <= hazards[pos]))
    out["ir2_first_error_hazard_rank_pct"] = rank_pct
    pm = float(prefix_mean)
    lo = IR3_LO_MULT * pm
    hi = IR3_HI_MULT * pm
    above_lo = int(np.sum(prefix_haz > lo))
    above_hi = int(np.sum(prefix_haz > hi))
    out["ir3_thresh_lo_bits"] = float(lo)
    out["ir3_thresh_hi_bits"] = float(hi)
    out["ir3_prefix_above_lo_count"] = above_lo
    out["ir3_prefix_above_lo_frac"] = float(above_lo / int(k2))
    out["ir3_prefix_above_hi_count"] = above_hi
    out["ir3_prefix_above_hi_frac"] = float(above_hi / int(k2))
    serial = np.arange(n, dtype=np.int64)
    full_order = np.lexsort((serial, -hazards))
    topk = full_order[:IR4_TOPK]
    rank_of = np.empty(n, dtype=np.int64)
    rank_of[full_order] = np.arange(1, n + 1, dtype=np.int64)
    out["ir4_topk_coords"] = [int(v) for v in topk]
    out["ir4_topk_hazard_bits"] = [float(hazards[v]) for v in topk]
    out["ir4_topk_in_prefix"] = [bool(mask[v]) for v in topk]
    out["ir4_topk_ranks"] = [int(rank_of[v]) for v in topk]
    m = min(n, IR5_CAP)
    out["ir5_series_hazard_bits"] = [float(v) for v in
                                     np.asarray(hazards[:m], dtype=np.float32)]
    out["ir5_series_in_prefix"] = [bool(v) for v in mask[:m]]
    out["ir5_series_truncated"] = bool(n > IR5_CAP)
    out["ir5_series_total_len"] = int(n)
    return out


def ir_payload_tables(records) -> dict:
    """Descriptive H2 decision quantities (never thresholds, never verdicts)."""
    completed = [r for r in records if str(r.get("outcome")) != "resource_abort"]
    ir2_all, ir2_a, ir2_b, ir2_oracle = [], [], [], []
    ir1_rows, ir3_rows, ir4_rows = [], [], []
    trunc_flags = []
    for record in completed:
        pct = record.get("ir2_first_error_hazard_rank_pct")
        arm = str(record.get("arm"))
        if pct is not None:
            pct = float(pct)
            ir2_all.append(pct)
            if arm == "A_frozen-order_operational":
                ir2_a.append(pct)
            elif arm == "B_new-order_operational":
                ir2_b.append(pct)
            else:
                ir2_oracle.append(pct)
        prefix_counts = record.get("ir1_hist_prefix_counts", [])
        outside_counts = record.get("ir1_hist_outside_counts", [])
        tail = sum(prefix_counts[-8:]) if len(prefix_counts) == IR1_BINS else None
        ir1_rows.append({
            "arm": arm,
            "block_index": int(record.get("block_index", -1)),
            "prefix_mass": int(sum(prefix_counts)),
            "outside_mass": int(sum(outside_counts)),
            "prefix_tail8_mass": None if tail is None else int(tail),
        })
        ir3_rows.append({
            "arm": arm,
            "block_index": int(record.get("block_index", -1)),
            "thresh_lo_bits": record.get("ir3_thresh_lo_bits"),
            "thresh_hi_bits": record.get("ir3_thresh_hi_bits"),
            "prefix_above_lo_count": record.get("ir3_prefix_above_lo_count"),
            "prefix_above_lo_frac": record.get("ir3_prefix_above_lo_frac"),
            "prefix_above_hi_count": record.get("ir3_prefix_above_hi_count"),
            "prefix_above_hi_frac": record.get("ir3_prefix_above_hi_frac"),
        })
        flags = record.get("ir4_topk_in_prefix", [])
        ir4_rows.append({
            "arm": arm,
            "block_index": int(record.get("block_index", -1)),
            "topk_in_prefix_count": int(sum(1 for v in flags if v)),
            "topk_ranks": list(record.get("ir4_topk_ranks", [])),
        })
        trunc_flags.append(bool(record.get("ir5_series_truncated")))

    def _dist(values):
        if not values:
            return {"count": 0, "median": None, "min": None, "max": None}
        ordered = sorted(values)
        mid = len(ordered) // 2
        median = (ordered[mid] if len(ordered) % 2 == 1
                  else 0.5 * (ordered[mid - 1] + ordered[mid]))
        return {"count": len(ordered), "median": float(median),
                "min": float(ordered[0]), "max": float(ordered[-1])}

    return {
        "ir2_rank_pct_all": _dist(ir2_all),
        "ir2_rank_pct_a_operational": _dist(ir2_a),
        "ir2_rank_pct_b_operational": _dist(ir2_b),
        "ir2_rank_pct_oracle": _dist(ir2_oracle),
        "ir1_histogram_rows": ir1_rows,
        "ir3_threshold_rows": ir3_rows,
        "ir4_topk_rows": ir4_rows,
        "ir5_truncated_all": bool(all(trunc_flags)) if trunc_flags else False,
        "ir5_cap": int(IR5_CAP),
        "records_completed": len(completed),
    }


# ---------------------------------------------------------------------------
# Nine carried scalars (arm-specific order digest) + hazard gate.
# ---------------------------------------------------------------------------

def _arm_order_digest(arm_name: str) -> str:
    """Arm-specific L2 order digest (frozen-A on A/C, new-B on B/D)."""
    if arm_name in ("A_frozen-order_operational", "C_frozen-order_oracle"):
        if FROZEN_ORDER_DIGEST_A is None:
            raise ValueError("Stage-A freeze not yet applied: frozen-A digest pin is None")
        return str(FROZEN_ORDER_DIGEST_A)
    if arm_name in ("B_new-order_operational", "D_new-order_oracle"):
        if FROZEN_NEW_ORDER_DIGEST_B is None:
            raise ValueError("Stage-A freeze not yet applied: new-B digest pin is None")
        return str(FROZEN_NEW_ORDER_DIGEST_B)
    raise ValueError(f"unknown frozen arm: {arm_name!r}")


def _nine_scalars_for_arm(*, arm_name, block, view, p2_arm, counts_arr,
                          l2_order, k2, first_error, field, low_hat) -> dict:
    """Accepted nine-scalar recorder with the arm-specific order digest.

    Calls the accepted 1.5M ``_l2_hazard_diagnostics`` read-only with the
    record's OWN order array (frozen-A on A/C, new-B on B/D) for the eight
    X-domain scalars, then carries the frozen ninth U-domain scalar
    (``l2_fail_in_prefix_u_domain``) with the accepted P20O formula
    (U-domain first-mismatch index of ``polar_transform(low_hat)`` vs
    ``view['u2']`` tested against the record's OWN disclosed prefix; null
    unless ``first_error_layer == L2``); only the recorded
    ``l2_order_digest`` label is arm-specific (the computation is
    byte-identical to the accepted recorders).
    """
    nine = _l2_hazard_diagnostics_1p5m(
        block=block, view=view, p2_arm=p2_arm, counts_arr=counts_arr,
        l2_order=l2_order, k2=int(k2), first_error=first_error)
    nine["l2_order_digest"] = _arm_order_digest(arm_name)
    nine["l2_fail_in_prefix_u_domain"] = None
    if first_error.get("first_error_layer") == "L2":
        n = int(np.asarray(view["bob"]).size)
        order = np.asarray(l2_order, dtype=np.int64)
        mask = np.zeros(n, dtype=bool)
        mask[order[:int(k2)]] = True
        if field is None or low_hat is None:
            raise ValueError(
                "U-domain cross-check requires the GF32 field and the decoded "
                "L2 hat under an L2 failure"
            )
        u2_true = np.asarray(view["u2"], dtype=np.int64)
        if u2_true.shape != (n,):
            raise ValueError(f"view u2 must be length {n}, got {u2_true.shape}")
        u2_hat = polar_transform(
            np.asarray(low_hat, dtype=np.int64), field=field, alpha=ALPHA)
        mismatch = np.flatnonzero(np.asarray(u2_hat, dtype=np.int64) != u2_true)
        if mismatch.size == 0:
            raise ValueError(
                "U-domain first-mismatch index absent under an L2 failure"
            )
        nine["l2_fail_in_prefix_u_domain"] = bool(mask[int(mismatch[0])])
    return nine


def hazard_instrumentation_complete(records) -> bool:
    """All nine section 7 scalars present with frozen nullability per record.

    Same nullability semantics as the accepted gate; the order-digest rule
    is arm-specific (frozen-A digest on A/C records, new-B digest on B/D
    records) with the gated prefix length 6689 on every completed record.
    """
    if not records:
        return False
    for record in records:
        if str(record.get("outcome")) == "resource_abort":
            continue
        if any(field not in record for field in HAZARD_FIELDS):
            return False
        try:
            want_digest = _arm_order_digest(str(record.get("arm")))
        except ValueError:
            return False
        if str(record.get("l2_order_digest")) != str(want_digest):
            return False
        if int(record.get("l2_prefix_len", -1)) != int(FROZEN_K2):
            return False
        if record.get("l2_prefix_hazard_mean_bits") is None:
            return False
        if record.get("l2_prefix_floor_frac") is None:
            return False
        fail_fields = (
            "l2_fail_in_prefix", "l2_fail_hazard_bits",
            "l2_fail_nbhd_mean_bits", "l2_fail_nbhd_floor_frac",
            "l2_fail_in_prefix_u_domain",
        )
        if record.get("first_error_layer") == "L2":
            for field in fail_fields:
                if record.get(field) is None:
                    return False
        else:
            for field in fail_fields:
                if record.get(field) is not None:
                    return False
    return True


def maintenance_diagnostics(records) -> dict:
    """Descriptive B-vs-A and D-vs-C maintenance/restoration (never a threshold).

    ``b_maintained_count`` = blocks where A is exact AND B is exact;
    ``b_restored_count`` = blocks where A fails and B is exact; the A->B
    transition table covers all four cells. The C->D pair is diagnostic
    only (oracle arms, never operational). ``*_exact_blocks`` report the
    per-arm exact counts including the standalone B-exact count. Same logic
    as the accepted helper; only the frozen arm-name quadruple differs.
    """
    by_block: dict = {}
    for record in records:
        try:
            by_block.setdefault(int(record["block_index"]), {})[
                str(record.get("arm"))] = record
        except (KeyError, TypeError, ValueError):
            continue
    b_restored = b_maintain = d_restored = d_maintain = 0
    a_exact = b_exact = c_exact = d_exact = 0
    a_to_b = {"a_exact_b_exact": 0, "a_exact_b_fail": 0,
              "a_fail_b_exact": 0, "a_fail_b_fail": 0}
    c_to_d = {"c_exact_d_exact": 0, "c_exact_d_fail": 0,
              "c_fail_d_exact": 0, "c_fail_d_fail": 0}
    moves = []
    for block_index in sorted(by_block):
        cell = by_block[block_index]
        a = cell.get("A_frozen-order_operational")
        b = cell.get("B_new-order_operational")
        c = cell.get("C_frozen-order_oracle")
        d = cell.get("D_new-order_oracle")
        if a is not None and b is not None:
            a_ok, b_ok = bool(a.get("exact")), bool(b.get("exact"))
            a_exact += int(a_ok)
            b_exact += int(b_ok)
            if a_ok and b_ok:
                b_maintain += 1
                a_to_b["a_exact_b_exact"] += 1
            elif a_ok and not b_ok:
                a_to_b["a_exact_b_fail"] += 1
            elif not a_ok and b_ok:
                b_restored += 1
                a_to_b["a_fail_b_exact"] += 1
            else:
                a_to_b["a_fail_b_fail"] += 1
        if c is not None and d is not None:
            c_ok, d_ok = bool(c.get("exact")), bool(d.get("exact"))
            c_exact += int(c_ok)
            d_exact += int(d_ok)
            if c_ok and d_ok:
                d_maintain += 1
                c_to_d["c_exact_d_exact"] += 1
            elif c_ok and not d_ok:
                c_to_d["c_exact_d_fail"] += 1
            elif not c_ok and d_ok:
                d_restored += 1
                c_to_d["c_fail_d_exact"] += 1
            else:
                c_to_d["c_fail_d_fail"] += 1
        moves.append({
            "block_index": block_index,
            "a_first_error_layer": None if a is None else a.get("first_error_layer"),
            "b_first_error_layer": None if b is None else b.get("first_error_layer"),
            "c_first_error_layer": None if c is None else c.get("first_error_layer"),
            "d_first_error_layer": None if d is None else d.get("first_error_layer"),
        })
    return {
        "b_maintained_count": int(b_maintain),
        "b_restored_count": int(b_restored),
        "d_maintained_count": int(d_maintain),
        "d_restored_count": int(d_restored),
        "b_exact_blocks": int(b_exact),
        "a_exact_blocks": int(a_exact),
        "c_exact_blocks": int(c_exact),
        "d_exact_blocks": int(d_exact),
        "a_to_b_transition_table": dict(a_to_b),
        "c_to_d_transition_table": dict(c_to_d),
        "first_error_moves": moves,
    }


def _arm_aggregate(records, spec) -> dict:
    arm_records = [r for r in records if r.get("arm") == spec.name]
    outcomes: dict = {}
    for record in arm_records:
        outcomes[str(record.get("outcome"))] = outcomes.get(
            str(record.get("outcome")), 0) + 1
    rates = [r.get("floor_hit_rate") for r in arm_records
             if r.get("floor_hit_rate") is not None]
    prefix = [r.get("l2_prefix_hazard_mean_bits") for r in arm_records
              if r.get("l2_prefix_hazard_mean_bits") is not None]
    return {
        "arm": spec.name,
        "l2_construction": FROZEN_L2_CONSTRUCTION,
        "records": len(arm_records),
        "exact_count": sum(1 for r in arm_records if r.get("exact") is True),
        "outcomes": outcomes,
        "floor_hit_rate_mean": (float(sum(rates) / len(rates)) if rates else None),
        "l2_prefix_hazard_mean_bits_mean": (
            float(sum(prefix) / len(prefix)) if prefix else None
        ),
    }


def build_aggregates(records) -> dict:
    """Descriptive aggregates: oracle excluded from every operational aggregate."""
    operational = [r for r in records if r.get("arm_kind") == "operational"]
    oracle = [r for r in records if r.get("arm_kind") == "oracle_control"]
    arms = frozen_arm_table() if pins_are_frozen() else ()
    arm_table = {spec.name: _arm_aggregate(records, spec) for spec in arms} if arms else {}
    op_outcomes: dict = {}
    for record in operational:
        op_outcomes[str(record.get("outcome"))] = op_outcomes.get(
            str(record.get("outcome")), 0) + 1
    return {
        "operational": {
            "records": len(operational),
            "exact_count": sum(1 for r in operational if r.get("exact") is True),
            "outcomes": op_outcomes,
        },
        "oracle": {
            "records": len(oracle),
            "exact_count": sum(1 for r in oracle if r.get("exact") is True),
        },
        "maintenance": maintenance_diagnostics(records),
        "arms": arm_table,
        "undetected_count": sum(1 for r in records if r.get("outcome") == "undetected"),
        "nonfinite_count": sum(1 for r in records if r.get("nonfinite") is True),
    }


def oracle_isolation_ok(records, *, final: bool) -> bool:
    """C/D carry ORACLE provenance, deployable=false, never operational."""
    for record in records:
        arm = record.get("arm")
        if arm in ORACLE_ARM_NAMES:
            if record.get("arm_provenance") != ORACLE_PROVENANCE:
                return False
            if record.get("deployable") is not False:
                return False
            if record.get("oracle_control") is not True:
                return False
            if record.get("hard_l2_exact") is not None or record.get("pair_exact") is not None:
                return False
        elif arm in OPERATIONAL_ARM_NAMES:
            if record.get("arm_provenance") != OPERATIONAL_PROVENANCE:
                return False
            if record.get("oracle_control") is not False:
                return False
            if record.get("deployable") is not True:
                return False
        else:
            return False
    if final and len(records) != PLANNED_RECORDS:
        return False
    return True


# ---------------------------------------------------------------------------
# Stage-B records (construction point + floor fields + nine carried scalars
# with the arm-specific order digest + IR-1..IR-5). The P20Q
# ``_ir_hazard_diagnostics`` callsite pattern is carried over; the IR call
# sits directly beside the nine-scalar call, post-decode.
# ---------------------------------------------------------------------------

def _base_record_fields(*, spec, arm_index, block, scoring, oracle, k_total,
                        budget_literal, prior_digest, alt_digest,
                        order_digest) -> dict:
    total_nll = scoring.get("total_nll_bits")
    return {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "arm": spec.name,
        "arm_index": int(arm_index),
        "arm_kind": spec.kind,
        "arm_provenance": spec.provenance,
        "l2_construction": FROZEN_L2_CONSTRUCTION,
        "prior_source": spec.prior_source,
        "block_index": int(block["block_index"]),
        "frame_start": int(block["frame_start"]),
        "frame_end": int(block["frame_end"]),
        "frame_count": FROZEN_BLOCK_FRAMES,
        "k1": int(spec.k1),
        "k2": int(spec.k2),
        "k_total": int(k_total),
        "budget_literal": str(budget_literal),
        "prior_digest": str(prior_digest),
        "alt_digest": str(alt_digest),
        "l1_order_digest": str(FROZEN_ORDER_DIGEST_A),
        "l2_order_digest": str(order_digest),
        "full_block_key_dependent_bits": int(spec.leakage_bits),
        "public_control_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS),
        "disclosure_ce_ratio": (
            float(spec.leakage_bits / total_nll) if total_nll else None
        ),
        "key_bit_delta_vs_control": int(
            spec.leakage_bits - (5 * int(k_total) + 64)
            if spec.kind == "operational"
            else spec.leakage_bits - (5 * int(spec.k2) + 64)),
        "oracle_truth_use": bool(oracle),
        "oracle_control": bool(oracle),
        "deployable": bool(not oracle),
        "raw_ser": scoring.get("raw_ser"),
        "true_l1_nll_bits": scoring.get("l1_nll_bits"),
        "true_l2_nll_bits": scoring.get("l2_nll_bits"),
        "true_total_nll_bits": scoring.get("total_nll_bits"),
        "true_total_nll_bits_per_pair": scoring.get("total_nll_bits_per_pair"),
    }


def _selected_fields(diag: dict) -> dict:
    return {
        "raw_zero_count_hits": diag.get("raw_zero_count_hits"),
        "floor_hits_1e15": diag.get("floor_hits_1e15"),
        "floor_hits": diag.get("floor_hits_1e15"),
        "floor_hit_log_loss_bits": diag.get("floor_hit_log_loss_bits"),
        "floor_hit_rate": diag.get("floor_hit_rate"),
        "l2_nll_candidate_H_bits": diag.get("l2_nll_candidate_H_bits"),
        "l2_nll_true_H_bits": diag.get("l2_nll_true_H_bits"),
        "selected_total_nll_bits": diag.get("selected_total_nll_bits"),
    }


def _operational_record(result, *, spec, arm_index, block, scoring, resources,
                        k_total, budget_literal, prior_digest, alt_digest,
                        order_digest, counts_arr, p1, p2, l2_order, n, view,
                        field, diag=None, error=None) -> dict:
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=False,
        k_total=k_total, budget_literal=budget_literal, prior_digest=prior_digest,
        alt_digest=alt_digest, order_digest=order_digest)
    first_error = first_error_coordinate(
        result.high_hat, result.low_hat, block["high"], block["low"])
    record.update({
        "outcome": result.outcome,
        "exact": bool(result.exact),
        "label_match": bool(result.label_match),
        "tag_pass": bool(result.tag_pass),
        "l1_exact": bool(result.l1_exact),
        "hard_l2_exact": bool(result.hard_l2_exact),
        "oracle_l2_exact": None,
        "pair_exact": bool(result.pair_exact),
        "first_error_layer": first_error["first_error_layer"],
        "first_error_coord": first_error["first_error_coord"],
        "l1_executed": bool(result.l1_executed),
        "l2_invoked": bool(result.l2_invoked),
        "tag_invoked": bool(result.tag_invoked),
        "sc_calls_this_record": (
            int(1 if result.l1_executed or result.l1_decode_failed else 0)
            + int(1 if result.l2_invoked else 0)
        ),
        "actual_key_dependent_bits": int(result.key_dependent_bits),
        "actual_public_control_bits": int(result.public_control_bits),
        "nonfinite": bool(result.nonfinite),
        "truth_leak_violation": bool(result.truth_leak_violation),
        "error": error,
        "wall_s": round(float(result.wall_s), 6),
        "resources": dict(resources),
    })
    selected = diag if diag is not None else _selected_diagnostics(
        high_sel=result.high_hat, low_sel=result.low_hat, view=view,
        counts_arr=counts_arr, p1=p1, p2=p2, n=n)
    record.update(_selected_fields(selected))
    # Recording-only recorders at the carried-over P20Q code point; all SC
    # calls for this record have completed before these calls. Truth enters
    # for RECORDING ONLY and never flows back into any decoder input.
    view_arm = dict(view)
    view_arm["u1_cond"] = (
        result.high_hat if result.high_hat is not None else view["high"])
    nine = _nine_scalars_for_arm(
        arm_name=spec.name, block=block, view=view_arm, p2_arm=p2,
        counts_arr=counts_arr, l2_order=l2_order, k2=FROZEN_K2,
        first_error=first_error, field=field, low_hat=result.low_hat)
    record.update(nine)
    record.update(_ir_hazard_diagnostics(
        view=view_arm, p2_arm=p2, l2_order=l2_order, k2=FROZEN_K2,
        first_error=first_error,
        prefix_mean=nine["l2_prefix_hazard_mean_bits"]))
    return record


def _control_record(result, *, spec, arm_index, block, scoring, resources,
                    k_total, budget_literal, prior_digest, alt_digest,
                    order_digest, counts_arr, p1, p2, l2_order, n, view,
                    field, diag=None, error=None) -> dict:
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=True,
        k_total=k_total, budget_literal=budget_literal, prior_digest=prior_digest,
        alt_digest=alt_digest, order_digest=order_digest)
    first_error = first_error_coordinate(None, result.low_hat, None, block["low"])
    record.update({
        "outcome": result.outcome,
        "exact": bool(result.exact),
        "label_match": bool(result.label_match),
        "tag_pass": bool(result.tag_pass),
        "l1_exact": None,
        "hard_l2_exact": None,
        "oracle_l2_exact": bool(result.oracle_l2_exact),
        "pair_exact": None,
        "first_error_layer": first_error["first_error_layer"],
        "first_error_coord": first_error["first_error_coord"],
        "l1_executed": False,
        "l2_invoked": bool(result.l2_invoked),
        "tag_invoked": bool(result.tag_invoked),
        "sc_calls_this_record": int(1 if result.l2_invoked else 0),
        "actual_key_dependent_bits": int(result.key_dependent_bits),
        "actual_public_control_bits": int(result.public_control_bits),
        "nonfinite": bool(result.nonfinite),
        "truth_leak_violation": bool(result.truth_leak_violation),
        "error": error,
        "wall_s": round(float(result.wall_s), 6),
        "resources": dict(resources),
    })
    selected = diag if diag is not None else _selected_diagnostics(
        high_sel=view["high"] if result.low_hat is not None else None,
        low_sel=result.low_hat, view=view,
        counts_arr=counts_arr, p1=p1, p2=p2, n=n)
    record.update(_selected_fields(selected))
    view_arm = dict(view)
    view_arm["u1_cond"] = view["high"]
    nine = _nine_scalars_for_arm(
        arm_name=spec.name, block=block, view=view_arm, p2_arm=p2,
        counts_arr=counts_arr, l2_order=l2_order, k2=FROZEN_K2,
        first_error=first_error, field=field, low_hat=result.low_hat)
    record.update(nine)
    record.update(_ir_hazard_diagnostics(
        view=view_arm, p2_arm=p2, l2_order=l2_order, k2=FROZEN_K2,
        first_error=first_error,
        prefix_mean=nine["l2_prefix_hazard_mean_bits"]))
    return record


def _abort_record(*, spec, arm_index, block, k_total, budget_literal,
                  prior_digest, alt_digest, order_digest) -> dict:
    record = {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "arm": spec.name,
        "arm_index": int(arm_index),
        "arm_provenance": spec.provenance,
        "l2_construction": FROZEN_L2_CONSTRUCTION,
        "prior_source": spec.prior_source,
        "block_index": int(block["block_index"]),
        "frame_start": int(block["frame_start"]),
        "frame_end": int(block["frame_end"]),
        "frame_count": FROZEN_BLOCK_FRAMES,
        "k1": int(spec.k1),
        "k2": int(spec.k2),
        "k_total": int(k_total),
        "budget_literal": str(budget_literal),
        "prior_digest": str(prior_digest),
        "alt_digest": str(alt_digest),
        "l1_order_digest": str(FROZEN_ORDER_DIGEST_A),
        "l2_order_digest": str(order_digest),
        "full_block_key_dependent_bits": int(spec.leakage_bits),
        "public_control_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS),
        "disclosure_ce_ratio": None,
        "key_bit_delta_vs_control": None,
        "oracle_truth_use": bool(spec.kind == "oracle_control"),
        "oracle_control": bool(spec.kind == "oracle_control"),
        "deployable": bool(spec.kind != "oracle_control"),
        "outcome": "resource_abort",
        "exact": False,
        "floor_hit_rate": None,
        "sc_calls_this_record": 0,
        "actual_key_dependent_bits": 0,
        "actual_public_control_bits": 0,
        "nonfinite": False,
        "truth_leak_violation": False,
        "error": "resource_abort",
        "resources": {},
    }
    for field in HAZARD_FIELDS:
        record[field] = (
            str(order_digest) if field == "l2_order_digest"
            else (int(FROZEN_K2) if field == "l2_prefix_len" else None)
        )
    for field in IR_FIELDS:
        record[field] = None
    return record


# ---------------------------------------------------------------------------
# Stage-B integrity gates (frozen section 9 order; all true or BLOCKED).
# ---------------------------------------------------------------------------

def _integrity_gates(*, n, k1, k2, k_total, arms, identity, manifest,
                     dev_source_pin, dev_pin, disjoint_pin, order_pin_A,
                     new_order_pin_B, set_delta, formation, records, events,
                     calls, incremental, accounting, provenance_violations,
                     cap, wall_s, resource_stop, session_prior_verified,
                     alt_verified, hazard_pin, prior_stat_before,
                     prior_stat_after, alt_stat_before, alt_stat_after,
                     dev_stat_before, dev_stat_after, registered_paths,
                     opened_paths, final: bool) -> dict:
    gates: dict = {}
    gates["predecessor_construction_identity"] = bool(
        identity is not None and manifest is not None)
    gates["reuse_prior_identity"] = bool(
        session_prior_verified is not None
        and bool(session_prior_verified.get("passed")))
    gates["reuse_alt_identity"] = bool(
        alt_verified is not None and bool(alt_verified.get("passed")))
    gates["alt_construction_budget_feasibility_replayed"] = bool(
        FROZEN_D2_FEASIBLE is True)
    gates["dev_split_manifest_identity"] = bool(
        manifest is not None
        and int(manifest.get("train_pairs", -1)) == FROZEN_MANIFEST_TRAIN_PAIRS
        and int(manifest.get("val_pairs", -1)) == FROZEN_MANIFEST_VAL_PAIRS
        and int(manifest.get("hold_pairs", -1)) == FROZEN_MANIFEST_HOLD_PAIRS)
    gates["dev_block_range_identity"] = bool(
        dev_pin is not None and dev_source_pin is not None
        and disjoint_pin is not None and bool(disjoint_pin.get("disjoint"))
        and bool(dev_pin.get("verified")))
    gates["order_derivation_identity"] = bool(
        order_pin_A is not None and bool(order_pin_A.get("verified")))
    gates["frozen_order_identity_A"] = bool(
        order_pin_A is not None and bool(order_pin_A.get("verified"))
        and str(order_pin_A.get("order_digest")) == str(FROZEN_ORDER_DIGEST_A))
    gates["new_order_identity_B"] = bool(
        new_order_pin_B is not None and bool(new_order_pin_B.get("verified"))
        and str(new_order_pin_B.get("new_order_digest"))
        == str(FROZEN_NEW_ORDER_DIGEST_B))
    gates["order_derivation_program_identity"] = bool(
        new_order_pin_B is not None
        and str(new_order_pin_B.get("program")) == str(NEW_ORDER_PROGRAM_PIN))
    try:
        gates["k_literal_exact"] = bool(
            bool(hazard_pin.get("k_literal"))
            and int(k1) == int(FROZEN_K1) and int(k2) == int(FROZEN_K2)
            and int(k1) + int(k2) == int(FROZEN_K_TOTAL)
            and str(hazard_pin.get("budget_literal")) == str(FROZEN_BUDGET_LITERAL))
    except (AttributeError, TypeError, ValueError):
        gates["k_literal_exact"] = False
    try:
        recomputed = verify_budget_literal(
            float(FROZEN_H_TOTAL), int(k_total), n=FROZEN_N,
            target_f=FROZEN_TARGET_F)
        gates["budget_literal_replayed"] = bool(
            int(recomputed["k_total"]) == int(FROZEN_K_TOTAL)
            and str(recomputed["literal"]) == str(FROZEN_BUDGET_LITERAL))
    except (AttributeError, TypeError, ValueError):
        gates["budget_literal_replayed"] = False
    gates["target_population_contract"] = bool(
        session_prior_verified is not None
        and bool(session_prior_verified.get("passed")))
    try:
        population_ok = (
            int(formation["dev_frames"]) == FROZEN_DEV_FRAMES
            and int(formation["dev_pairs"]) == FROZEN_DEV_PAIRS
            and list(formation["dev_frame_range"]) == list(FROZEN_DEV_FRAME_RANGE)
        )
    except (KeyError, TypeError, ValueError):
        population_ok = False
    gates["dev_population_exact"] = bool(population_ok)
    try:
        blocks_ok = (
            [tuple(r) for r in formation["block_ranges"]]
            == [tuple(r) for r in FROZEN_BLOCK_RANGES]
            and len(formation["blocks"]) == FROZEN_BLOCK_COUNT
            and formation["remainder"]["used"] is False
            and int(formation["remainder"]["frames"]) == FROZEN_REMAINDER_FRAMES
            and int(formation["remainder"]["symbols"]) == FROZEN_REMAINDER_SYMBOLS
            and list(formation["dev_frame_range"]) == list(FROZEN_DEV_FRAME_RANGE)
        )
    except (KeyError, TypeError, ValueError):
        blocks_ok = False
    gates["blocks_exact_with_declared_remainder"] = bool(blocks_ok)
    gates["four_records_exact"] = (
        len(records) == PLANNED_RECORDS if final else len(records) <= PLANNED_RECORDS)
    gates["genie_calls_exact"] = int(calls.get("genie", 0)) == 0
    sc_sum = sum(int(r.get("sc_calls_this_record", -1)) for r in records)
    gates["sc_calls_exact"] = (
        (int(calls.get("sc", -1)) == PLANNED_SC_CALLS and sc_sum == PLANNED_SC_CALLS)
        if final else int(calls.get("sc", 0)) <= PLANNED_SC_CALLS)
    tag_records = sum(1 for r in records if r.get("tag_invoked") is True)
    gates["tags_exact"] = (
        (int(incremental.get("tag_invocations", -1)) == PLANNED_TAG_INVOCATIONS
         and tag_records == PLANNED_TAG_INVOCATIONS)
        if final else int(incremental.get("tag_invocations", 0)) <= PLANNED_TAG_INVOCATIONS)
    try:
        shared_l1 = l1_prefix_positions(order_pin_A["l1_order"], int(k1))
        frozen_l2 = l2_prefix_positions(order_pin_A["l2_order"], int(k2))
        new_l2 = l2_prefix_positions(new_order_pin_B["l2_order"], int(k2))
        orders_ok = (
            shared_l1.shape == (int(k1),)
            and frozen_l2.shape == (int(k2),)
            and new_l2.shape == (int(k2),)
            and int(arms[0].k1) == int(k1) and int(arms[0].k2) == int(k2)
            and int(arms[1].k1) == int(k1) and int(arms[1].k2) == int(k2)
            and int(arms[2].k1) == 0 and int(arms[2].k2) == int(k2)
            and int(arms[3].k1) == 0 and int(arms[3].k2) == int(k2)
        )
    except (ValueError, IndexError, AttributeError, TypeError):
        orders_ok = False
    gates["orders_valid_k_prefixes_within_registered_arms"] = bool(orders_ok)
    try:
        gates["order_set_delta_recorded"] = bool(
            set_delta is not None
            and int(set_delta.get("size_delta_b_minus_a", -1)) == 0
            and int(set_delta.get("a_disclosed_size", -1)) == int(FROZEN_K2)
            and int(set_delta.get("b_disclosed_size", -1)) == int(FROZEN_K2))
    except (AttributeError, TypeError, ValueError):
        gates["order_set_delta_recorded"] = False
    gates["hazard_instrumentation_complete"] = bool(
        hazard_instrumentation_complete(records))
    gates["ir_payload_complete"] = bool(ir_payload_complete(records))
    floor_fields_present = all("floor_hit_rate" in r for r in records)

    def _rate_ok(record) -> bool:
        value = record.get("floor_hit_rate")
        if value is not None:
            return float(value) >= 0.0
        return str(record.get("outcome")) in ("decode_failed", "resource_abort")

    gates["floor_hit_rate_reported"] = bool(
        (not final or len(records) == PLANNED_RECORDS)
        and floor_fields_present
        and all(_rate_ok(r) for r in records)
        and hazard_pin.get("alt_floor_rate") is not None)
    gates["oracle_isolation"] = bool(oracle_isolation_ok(records, final=final))
    try:
        slots = {(str(r.get("arm")), int(r.get("block_index"))) for r in records}
        buckets_ok = (
            len(slots) == len(records)
            and (not final or slots == {
                (name, block) for name in FROZEN_ARM_NAMES
                for block in range(FROZEN_BLOCK_COUNT)})
            and all(str(r.get("outcome")) in (
                "exact", "verify_failed", "decode_failed", "nonfinite",
                "undetected", "resource_abort") for r in records)
        )
    except (TypeError, ValueError):
        buckets_ok = False
    gates["buckets_disjoint_exhaustive"] = bool(buckets_ok)
    gates["undetected_zero"] = all(r.get("outcome") != "undetected" for r in records)
    gates["nonfinite_zero"] = all(r.get("nonfinite") is not True for r in records)
    gates["truth_isolation"] = int(provenance_violations) == 0 and all(
        r.get("truth_leak_violation") is not True for r in records)
    recount = raw_prior_val_1p5m_recount_events(events)
    derived_key = sum(int(r.get("actual_key_dependent_bits", -1)) for r in records)
    derived_tags = sum(1 for r in records if r.get("tag_invoked") is True)
    gates["disclosure_recount_exact"] = bool(
        int(recount["key_dependent_bits"]) == int(derived_key)
        and int(recount["tag_invocations"]) == int(derived_tags)
        and int(incremental.get("key_dependent_bits", -1)) == int(derived_key)
        and int(incremental.get("tag_invocations", -1)) == int(derived_tags))
    gates["one_open_per_protected_input"] = bool(
        int(accounting.get("counts_content_opens", -1)) == 0
        and int(accounting.get("session_prior_content_loads", -1)) <= 1
        and int(accounting.get("alt_content_loads", -1)) <= 1
        and int(accounting.get("dev_content_opens", -1)) <= 1
        and accounting.get("reopen_attempted") is False)
    gates["input_stat_unchanged"] = bool(
        prior_stat_before == prior_stat_after
        and alt_stat_before == alt_stat_after
        and dev_stat_before == dev_stat_after)
    gates["no_unregistered_access"] = bool(
        set(opened_paths) <= set(registered_paths))
    rss_peak = opf._peak_rss_bytes()
    gates["resource_limits_met_and_no_abort"] = bool(
        resource_stop is None and float(wall_s) <= float(cap)
        and (rss_peak is None or int(rss_peak) <= RSS_LIMIT_BYTES)
        and all(r.get("outcome") != "resource_abort" for r in records))
    return gates


def l2_order_position_1p5m_label(gates: dict) -> str:
    """Descriptive COMPLETE iff every integrity gate holds, else BLOCKED(first)."""
    failing = [g for g in INTEGRITY_GATE_ORDER if not gates.get(g, False)]
    if not failing:
        return COMPLETE_LABEL
    return f"BLOCKED({failing[0]})"


@dataclass(frozen=True, eq=False)
class L2OrderPosition1p5mRun:
    """In-memory P20R Stage-B run (also returned by the runner)."""

    summary: dict
    records: tuple
    gates: dict


# ---------------------------------------------------------------------------
# Stage-B orchestration.
# ---------------------------------------------------------------------------

def _write_frozen_plan(out_path: Path, *, source, floor, n, k1, k2, k_total,
                       budget_literal, construction, construction_digest,
                       prior_path, prior_digest, alt_path, alt_digest,
                       dev_pairs, manifest_path, dev_frames, block_frames,
                       remainder_frames, tag_master, chunk_rows, tag_bits,
                       order_file, order_digest, new_order_file,
                       new_order_digest, identity, manifest, dev_source_pin,
                       dev_pin, disjoint_pin, order_pin_A, new_order_pin_B,
                       set_delta) -> dict:
    out_path.mkdir(parents=True, exist_ok=False)
    plan = {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "source": source,
        "floor": float(floor),
        "n": int(n),
        "k1": int(k1),
        "k2": int(k2),
        "k_total": int(k_total),
        "budget_literal": str(budget_literal),
        "construction": str(construction),
        "construction_digest": str(construction_digest),
        "prior_path": str(prior_path),
        "prior_digest": str(prior_digest),
        "alt_path": str(alt_path),
        "alt_digest": str(alt_digest),
        "dev_pairs": str(dev_pairs),
        "manifest_path": str(manifest_path),
        "dev_frames": [int(dev_frames[0]), int(dev_frames[1])],
        "block_frames": int(block_frames),
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "remainder_frames": [int(remainder_frames[0]), int(remainder_frames[1])],
        "build_frames": [int(FROZEN_BUILD_FRAME_RANGE[0]),
                         int(FROZEN_BUILD_FRAME_RANGE[1])],
        "dev_source": dict(dev_source_pin),
        "dev_block_pin": dict(dev_pin),
        "build_dev_disjointness_s2_ii": dict(disjoint_pin),
        "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
        "consumed_1p5m_train_frame_range": list(CONSUMED_1P5M_TRAIN_FRAME_RANGE),
        "consumed_1p5m_val_dev_frame_range": list(CONSUMED_1P5M_VAL_DEV_FRAME_RANGE),
        "consumed_1p5m_hold_frame_range": list(CONSUMED_1P5M_HOLD_FRAME_RANGE),
        "hold_remainder_2m_counted_never_decoded": {
            "frames": list(FROZEN_2M_HOLD_REMAINDER_FRAME_RANGE),
            "frame_count": int(FROZEN_2M_HOLD_REMAINDER_FRAMES),
            "symbols": int(FROZEN_2M_HOLD_REMAINDER_SYMBOLS),
            "used": False,
        },
        "consumed_sessions": {
            "1m_pool": {"source_tag": CONSUMED_1M_SOURCE_TAG,
                        "frames": list(CONSUMED_1M_FRAME_RANGE)},
            "1p5m_train_build": {"source_tag": FROZEN_SOURCE_TAG,
                                 "frames": list(CONSUMED_1P5M_TRAIN_FRAME_RANGE)},
            "1p5m_val_dev": {"source_tag": FROZEN_SOURCE_TAG,
                             "frames": list(CONSUMED_1P5M_VAL_DEV_FRAME_RANGE)},
            "1p5m_hold": {"source_tag": FROZEN_SOURCE_TAG,
                          "frames": list(CONSUMED_1P5M_HOLD_FRAME_RANGE)},
            "2m_train_build": {"source_tag": CONSUMED_2M_SOURCE_TAG,
                               "frames": list(CONSUMED_2M_TRAIN_FRAME_RANGE)},
            "2m_val": {"source_tag": CONSUMED_2M_SOURCE_TAG,
                       "frames": list(CONSUMED_2M_VAL_FRAME_RANGE)},
            "2m_hold_dev": {"source_tag": CONSUMED_2M_SOURCE_TAG,
                            "frames": list(CONSUMED_2M_HOLD_DEV_FRAME_RANGE)},
        },
        "tag_master": int(tag_master),
        "tag_seed_domain": f"{SEED_PREFIX}:<master>:<n>:<arm>:<block_index>",
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "order_file_A": str(order_file),
        "order_digest_A": str(order_digest),
        "new_order_file_B": str(new_order_file),
        "new_order_digest_B": str(new_order_digest),
        "new_order_program": str(NEW_ORDER_PROGRAM_PIN),
        "new_order_ranking_functional": str(NEW_ORDER_RANKING_FUNCTIONAL),
        "order_set_delta": {
            key: (list(value) if isinstance(value, list) else value)
            for key, value in dict(set_delta).items()
        },
        "order_k1": int(order_pin_A.get("k1", -1)),
        "order_k2": int(order_pin_A.get("k2", -1)),
        "identity_n": int(identity.get("n", -1)) if isinstance(identity, dict) else None,
        "arms": [
            {"name": spec.name, "kind": spec.kind, "k1": int(spec.k1),
             "k2": int(spec.k2), "leakage_bits": int(spec.leakage_bits),
             "l2_construction": FROZEN_L2_CONSTRUCTION,
             "public_control_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS)}
            for spec in frozen_arm_table()
        ],
        "planned_sc_calls": PLANNED_SC_CALLS,
        "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
        "planned_records": PLANNED_RECORDS,
        "planned_key_dependent_bits": planned_totals(k1, k2)[
            "planned_key_dependent_bits"],
        "planned_public_control_bits": planned_totals(k1, k2)[
            "planned_public_control_bits"],
        "hazard_window_R": int(FROZEN_HAZARD_R),
        "hazard_fields": list(HAZARD_FIELDS),
        "u_domain_scalar_frozen_present": True,
        "arm_order_digest_rule": "frozen-A on A/C, new-B on B/D",
        "ir_fields": list(IR_FIELDS),
        "ir3_threshold_multipliers": [IR3_LO_MULT, IR3_HI_MULT],
        "ir1_bins": int(IR1_BINS),
        "ir4_topk": int(IR4_TOPK),
        "ir5_cap": int(IR5_CAP),
        "frozen_command": FROZEN_COMMAND,
        "frozen_plan_manifest": manifest,
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
    }
    opf._write_json(out_path / "frozen_plan.json", plan)
    return plan


def _render_report(summary: dict) -> str:
    aggregates = summary.get("aggregates", {})
    maintenance = aggregates.get("maintenance", {})
    ir_payload = aggregates.get("ir_payload", {})
    set_delta = summary.get("order_set_delta", {})
    lines = [
        "# NB-Polar Phase 4-P20R single-factor L2-order-position on 1.5M "
        "VAL remainder with mandatory H2 IR-1..IR-5",
        "",
        f"- protocol: `{summary.get('analysis')}` (mode `{summary.get('mode')}`)",
        f"- source: `{summary.get('source')}`; N={summary.get('n')}; "
        f"K1={summary.get('k1')} K2={summary.get('k2')} K_total={summary.get('k_total')} "
        "(1.5M-session-derived, S2-i literal replay)",
        "- alt-L2 construction: unit-pseudocount conditional alpha1 on all "
        "arms; alt-table digest "
        f"`{summary.get('alt_digest')}`",
        f"- frozen-A order digest: `{summary.get('order_digest_A')}` "
        f"(first-{summary.get('k1')} / first-{summary.get('k2')} prefixes on A/C); "
        f"new-B order digest: `{summary.get('new_order_digest_B')}` "
        f"(first-{summary.get('k2')} prefix on B/D); set-delta "
        f"|A-B|={set_delta.get('a_minus_b_count')} "
        f"|B-A|={set_delta.get('b_minus_a_count')} "
        f"(size-delta {set_delta.get('size_delta_b_minus_a')})",
        f"- blocks: {summary.get('block_ranges')} "
        f"(remainder {summary.get('remainder_frames')} never used; 2M HOLD "
        "remainder counted never decoded)",
        f"- outcome: `{summary.get('outcome_label')}`; "
        f"records {summary.get('records_completed')}/{summary.get('planned_records')}",
        f"- operational exact: "
        f"{aggregates.get('operational', {}).get('exact_count')} "
        f"(A {maintenance.get('a_exact_blocks')} / B {maintenance.get('b_exact_blocks')}); "
        f"b_restored_count={maintenance.get('b_restored_count')} "
        f"(descriptive: A fail -> B exact); "
        f"b_maintained_count={maintenance.get('b_maintained_count')} "
        "(A exact and B exact); A->B table "
        f"{maintenance.get('a_to_b_transition_table')}",
        f"- oracle exact: {aggregates.get('oracle', {}).get('exact_count')} "
        f"(C {maintenance.get('c_exact_blocks')} / D {maintenance.get('d_exact_blocks')}); "
        f"d_restored_count={maintenance.get('d_restored_count')} "
        "(diagnostic only, never operational)",
        f"- undetected: {aggregates.get('undetected_count')}; "
        f"nonfinite: {aggregates.get('nonfinite_count')}",
        f"- IR payload: rank-pct (all) {ir_payload.get('ir2_rank_pct_all')}; "
        f"IR-5 truncated-all={ir_payload.get('ir5_truncated_all')}",
        f"- SC calls: {summary.get('sc_calls')}/{summary.get('planned_sc_calls')} "
        f"(Stage-B sampling {summary.get('stage_b_sampling_calls')}); tags: "
        f"{summary.get('tag_invocations')}/{summary.get('planned_tag_invocations')}",
        f"- key bits: {summary.get('key_dependent_bits')}; "
        f"public bits: {summary.get('public_control_bits')}; "
        f"recount mismatch: {summary.get('recount_mismatch')}",
        f"- integrity: {'ALL PASS' if summary.get('integrity_all_pass') else 'BLOCKED'} "
        f"{summary.get('failing_integrity_gates')}",
        "",
        "C/D are oracle-labelled diagnostic controls, never an operational "
        "protocol or deployable result. The CE-normalized disclosure ratio is "
        "not qualification efficiency; undetected is never success. This is a "
        "descriptive VAL-remainder single-factor order-position reading on a "
        "FIRST-USE 1.5M VAL-remainder block: no recovery / FER / superiority / "
        "qualification / promotion / reliability claim is made, and the H2 "
        "decision stays main-thread analysis after acceptance.",
        "",
    ]
    return "\n".join(lines)


def run_l2_order_position_1p5m(
    *,
    prior=None,
    alt_prior=None,
    prior_path=FROZEN_PRIOR_PATH,
    prior_digest=None,
    alt_prior_path=FROZEN_ALT_PATH,
    alt_digest=None,
    source=None,
    floor=FROZEN_FLOOR,
    n=None,
    k1=None,
    k2=None,
    construction=FROZEN_CONSTRUCTION_PATH,
    construction_digest=FROZEN_CONSTRUCTION_DIGEST,
    manifest_path=FROZEN_MANIFEST_PATH,
    dev_pairs=FROZEN_DEV_PAIRS_PATH,
    dev_table=None,
    dev_frames=FROZEN_DEV_FRAME_RANGE,
    block_frames: int = FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
    tag_master=FROZEN_TAG_MASTER,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    tag_bits: int = FROZEN_TAG_BITS,
    order_file=FROZEN_ORDER_FILE_PATH,
    order_digest=None,
    new_order_file=FROZEN_NEW_ORDER_PATH,
    new_order_digest=None,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
) -> L2OrderPosition1p5mRun:
    """Execute the frozen P20R four-arm order-position run once; write five files.

    ``prior`` / ``alt_prior`` / ``dev_table`` are documented injected test
    seams; the frozen CLI passes only the frozen point, loads the Stage-A
    frozen 1.5M raw prior and alt table read-only exactly once each, loads
    the frozen-A 1.5M order file and the Stage-A new-B order file read-only
    behind their digest gates, and reads the 1.5M VAL-remainder parquet
    through its accepted loader exactly once. The V25 counts NPZ is never
    opened at any stage. The construction/order swap is hardcoded (never
    CLI-tunable): A runs the alt L2 at the Stage-A (K1,K2) on the frozen-A
    order prefixes, B the SAME alt L2 at the SAME point on the new-B order
    prefix, C the frozen-order true-L1 oracle and D the new-order true-L1
    oracle at K2. Stage B performs ZERO sampling (no seed flag, no sampler
    call; the genie counter is gated at 0).
    """
    global _SESSION_PRIOR_CONTENT_LOADED, _ALT_CONTENT_LOADED
    global _DEV_PARQUET_CONTENT_OPENED
    pins = pins_frozen()
    if pins["d2_feasible"] is not True:
        raise ValueError(
            "BLOCKED(alt_construction_budget_feasibility_replayed): Stage-A D2 "
            "outcome is not FEASIBLE (DEV untouched; no Stage-B run)"
        )
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    floor = _check_floor(floor)
    source = _check_source(source)
    n = _check_n(n)
    if k1 is None or k2 is None:
        raise ValueError("frozen point requires --k1/--k2 equal to the Stage-A literals")
    k_literals = check_k_literals(k1=k1, k2=k2)
    k1, k2, k_total = k_literals["k1"], k_literals["k2"], k_literals["k_total"]
    opf._check_chunk_contract(chunk_rows)
    opf._check_tag_bits(tag_bits)
    dev_frames = _check_dev_frames(dev_frames)
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise ValueError(
            f"frozen point requires block-frames={FROZEN_BLOCK_FRAMES}, got {block_frames}")
    remainder_frames = _check_remainder_frames(remainder_frames)
    tag_master = _check_tag_master(tag_master)
    if prior_digest is None:
        raise ValueError("frozen point requires --prior-digest equal to the Stage-A pin")
    prior_digest = _check_prior_digest(prior_digest)
    if order_digest is None:
        raise ValueError("frozen point requires --order-digest equal to the Stage-A pin")
    order_digest = _check_order_digest_A(order_digest)
    if new_order_digest is None:
        raise ValueError("frozen point requires --new-order-digest equal to the Stage-A pin")
    new_order_digest = _check_new_order_digest_B(new_order_digest)
    if alt_digest is None:
        raise ValueError("frozen point requires --alt-digest equal to the Stage-A pin")
    alt_digest = _check_alt_digest(alt_digest)
    arms = frozen_arm_table() if check_frozen_arm_table() else ()

    # Gate family (a)->(g) in the frozen order before any protected content
    # open: predecessor construction identity, cross-file source identity
    # (a), intra-file VAL-remainder-containment (b), consumed-1M /
    # consumed-1.5M / consumed-2M + S2-ii (c)-(e), then reuse-prior +
    # reuse-alt + frozen-A-order + new-B-order + derivation-program +
    # K-literal + order-position-identity pins (f)-(g).
    if str(construction_digest) != str(FROZEN_CONSTRUCTION_DIGEST):
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = _gate_call("predecessor_construction_identity",
                          verify_predecessor_construction, construction,
                          expected_digest=construction_digest)
    identity = verified["record"]
    dev_source_pin = _gate_call("dev_block_range_identity",
                                verify_dev_source_identity_1p5m, dev_pairs)
    dev_pin = verify_val_remainder_containment(dev_frames, remainder_frames)
    disjoint_pin = verify_consumed_exclusions_val_remainder(dev_frames, remainder_frames)
    manifest = _gate_call("dev_split_manifest_identity", verify_dev_manifest_1p5m,
                          manifest_path, source=source)
    order_pin_A = _gate_call(
        "frozen_order_identity_A", verify_stage_b_order_file_p20m, order_file,
        expected_digest=order_digest,
        expected_prior_digest=str(FROZEN_SESSION_PRIOR_DIGEST),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    new_order_pin_B = _gate_call(
        "new_order_identity_B", verify_new_order_file, new_order_file,
        expected_digest=new_order_digest,
        expected_prior_digest=str(FROZEN_SESSION_PRIOR_DIGEST),
        frozen_l1_order=np.asarray(order_pin_A["l1_order"]),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    if str(new_order_pin_B.get("program")) != str(NEW_ORDER_PROGRAM_PIN):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(order_derivation_program_identity): program pin drifted")
    set_delta = order_set_delta(
        np.asarray(order_pin_A["l2_order"]),
        np.asarray(new_order_pin_B["l2_order"]), int(k2))
    if int(set_delta["size_delta_b_minus_a"]) != 0:
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(order_set_delta_recorded): B-A disclosed-size delta != 0")
    # Order-position identity (g): the construction quadruple + tag
    # domain + source vocabulary must match the P20R freeze.
    order_identity = {
        "construction_quadruple": (PROTOCOL_NAME, MODE, FROZEN_SOURCE, SEED_PREFIX),
        "tag_master": int(tag_master),
        "order_digest_A": str(order_digest),
        "new_order_digest_B": str(new_order_digest),
        "k1": int(k1),
        "k2": int(k2),
    }
    if order_identity["construction_quadruple"] != (
            "nbpolar-p20r-order-position-1p5m", "val-remainder-order-position-1p5m",
            "1p5M", "nbpolar-p20r-order-position-1p5m-seed"):
        raise L2OrderPosition1p5mContractError(
            "BLOCKED(dev_block_range_identity): order-position identity drifted")
    hazard_pin = {
        "k_literal": True,
        "budget_literal": k_literals["budget_literal"],
        "alt_floor_rate": None,
    }

    # One-open guards are refusals before any content load/open of any input.
    if prior is None and _SESSION_PRIOR_CONTENT_LOADED:
        raise ValueError("reload refused: the single session-prior load was consumed")
    if alt_prior is None and _ALT_CONTENT_LOADED:
        raise ValueError("reload refused: the single alt-table load was consumed")
    if dev_table is None and _DEV_PARQUET_CONTENT_OPENED:
        raise ValueError("reopen refused: the single VAL-remainder parquet content open was consumed")

    # Input existence and stat-only metadata come before any content load/open.
    real_prior = prior is None
    real_alt = alt_prior is None
    real_dev = dev_table is None
    if real_prior:
        prior_file = Path(prior_path)
        if not prior_file.is_file():
            raise FileNotFoundError(f"Stage-A 1.5M raw prior not found: {prior_file}")
        prior_stat_before = _stat_record(prior_file)
    else:
        prior_stat_before = _stat_record(None)
    if real_alt:
        alt_file = Path(alt_prior_path)
        if not alt_file.is_file():
            raise FileNotFoundError(f"Stage-A alt-L2 table not found: {alt_file}")
        alt_stat_before = _stat_record(alt_file)
    else:
        alt_stat_before = _stat_record(None)
    if real_dev:
        dev_path_obj = Path(dev_pairs)
        if not dev_path_obj.is_file():
            raise FileNotFoundError(f"1.5M VAL-remainder pairs parquet not found: {dev_path_obj}")
        dev_stat_before = _stat_record(dev_path_obj)
        if dev_stat_before["size_bytes"] != FROZEN_DEV_PAIRS_SIZE:
            raise ValueError(
                "1.5M VAL-remainder pairs size mismatch before content open: "
                f"observed {dev_stat_before['size_bytes']} != "
                f"build-manifest pin {FROZEN_DEV_PAIRS_SIZE}"
            )
    else:
        dev_stat_before = _stat_record(None)
    registered_paths = []
    if real_prior:
        registered_paths.append(str(Path(prior_path).resolve()))
    if real_alt:
        registered_paths.append(str(Path(alt_prior_path).resolve()))
    if real_dev:
        registered_paths.append(str(Path(dev_pairs).resolve()))
    opened_paths: list[str] = []

    plan = _write_frozen_plan(
        out_path=out_path, source=source, floor=floor, n=n, k1=k1, k2=k2,
        k_total=k_total, budget_literal=k_literals["budget_literal"],
        construction=construction, construction_digest=construction_digest,
        prior_path=prior_path if real_prior else None, prior_digest=prior_digest,
        alt_path=alt_prior_path if real_alt else None, alt_digest=alt_digest,
        dev_pairs=dev_pairs, manifest_path=manifest_path, dev_frames=dev_frames,
        block_frames=block_frames, remainder_frames=remainder_frames,
        tag_master=tag_master, chunk_rows=chunk_rows, tag_bits=tag_bits,
        order_file=order_file, order_digest=order_digest,
        new_order_file=new_order_file, new_order_digest=new_order_digest,
        identity=identity, manifest=manifest, dev_source_pin=dev_source_pin,
        dev_pin=dev_pin, disjoint_pin=disjoint_pin, order_pin_A=order_pin_A,
        new_order_pin_B=new_order_pin_B, set_delta=set_delta)
    accounting = {
        "input_mode": "real" if (real_prior or real_alt or real_dev) else "injected",
        "session_prior_input_mode": "frozen_prior_file" if real_prior else "injected_prior",
        "alt_input_mode": "frozen_alt_file" if real_alt else "injected_alt",
        "dev_input_mode": "pairs_parquet" if real_dev else "injected_table",
        "prior_path": str(prior_path) if real_prior else None,
        "alt_prior_path": str(alt_prior_path) if real_alt else None,
        "dev_pairs_path": str(dev_pairs) if real_dev else None,
        "manifest_path": str(manifest_path),
        "construction_path": str(construction),
        "prior_loader": "per_session_calibration.canonical_prior_digest(read-only seam)" if real_prior else None,
        "pairs_loader": PAIRS_LOADER_IDENTITY if real_dev else None,
        "registered_content_paths": registered_paths,
        "opened_content_paths": opened_paths,
        "artifact_content_reads_allowed_per_input": 1,
        "counts_content_opens": 0,
        "session_prior_content_loads": 0,
        "alt_content_loads": 0,
        "dev_content_opens": 0,
        "attempts_allowed": 1,
        "attempts_consumed_by_this_run": 0,
        "retries": 0,
        "reopen_attempted": False,
        "retry_after_open": False,
    }

    start = time.perf_counter()
    try:
        # ---- input 1: the single session-prior load + reuse_prior_identity.
        if real_prior:
            with open(prior_path, "rb") as fh:
                data = np.load(fh, allow_pickle=False)
                with data:
                    raw_arrays = {k: np.asarray(data[k]) for k in data.files}
            _SESSION_PRIOR_CONTENT_LOADED = True
            accounting["session_prior_content_loads"] = 1
            opened_paths.append(str(Path(prior_path).resolve()))
        else:
            raw_arrays = dict(prior)
        session_prior_verified = verify_corrected_prior_1p5m(
            raw_arrays, expected_digest=prior_digest,
            expected_h1=float(FROZEN_H1), expected_h2=float(FROZEN_H2),
            expected_total=float(FROZEN_H_TOTAL))
        p1_inc = session_prior_verified["p1"]
        p2_inc = session_prior_verified["p2"]
        counts_inc = session_prior_verified["counts"]

        # ---- input 2: the single alt-table load + reuse_alt_identity gate.
        if real_alt:
            alt_verified = _gate_call(
                "reuse_alt_identity", verify_alt_l2_identity_1p5m, alt_prior_path,
                expected_digest=alt_digest, incumbent_arrays=raw_arrays)
            _ALT_CONTENT_LOADED = True
            accounting["alt_content_loads"] = 1
            opened_paths.append(str(Path(alt_prior_path).resolve()))
        else:
            alt_verified = verify_alt_l2_arrays_1p5m(
                dict(alt_prior), incumbent_arrays=raw_arrays)
        p1_alt = alt_verified["p1"]
        p2_alt = alt_verified["p2_alt"]
        counts_alt = alt_verified["counts_ab"]
        # The alt-table floor-hit rate is a Stage-A frozen literal.
        hazard_pin = {
            "k_literal": True,
            "budget_literal": k_literals["budget_literal"],
            "alt_floor_rate": p20n.FROZEN_ALT_FLOOR_HIT_RATE,
        }

        # ---- S2: the K-literal display + alt-H descriptive literals.
        budget_literal = k_literals["budget_literal"]
        alt_h_literals = {
            "h1_inc": float(alt_verified["h1_inc"]),
            "h2_alt": float(alt_verified["h2_alt"]),
            "h_total_alt": float(alt_verified["h_total_alt"]),
        }

        # ---- input 3: the single VAL-remainder parquet content open, DEV rows only.
        if real_dev:
            table = load_pairs_table(Path(dev_pairs))
            _DEV_PARQUET_CONTENT_OPENED = True
            accounting["dev_content_opens"] = 1
            opened_paths.append(str(Path(dev_pairs).resolve()))
            if int(accounting["attempts_consumed_by_this_run"]) < 1:
                accounting["attempts_consumed_by_this_run"] = 1
        else:
            table = dev_table
        table = normalize_pair_columns(table)
        formation = form_val_remainder_blocks(
            table, dev_frames=dev_frames, block_frames=block_frames,
            remainder_frames=remainder_frames,
        )

        field = make_gf32()
        calls = {"sc": 0, "genie": 0}
        records: list[dict] = []
        events: list[dict] = []
        incremental = {"key_dependent_bits": 0, "public_control_bits": 0,
                       "tag_invocations": 0}
        provenance_violations = 0
        resource_stop: str | None = None
        budget_cap = float(total_wall_s)
        if not np.isfinite(budget_cap) or budget_cap <= 0:
            raise ValueError(
                f"total_wall_s must be finite and positive, got {total_wall_s!r}")

        arm_specs = {spec.name: spec for spec in arms}
        prior_by_source = {
            "alt": (p1_alt, p2_alt, counts_alt),
        }
        l1_shared = np.asarray(order_pin_A["l1_order"], dtype=np.int64)
        l2_by_arm = {
            "A_frozen-order_operational": np.asarray(
                order_pin_A["l2_order"], dtype=np.int64),
            "B_new-order_operational": np.asarray(
                new_order_pin_B["l2_order"], dtype=np.int64),
            "C_frozen-order_oracle": np.asarray(
                order_pin_A["l2_order"], dtype=np.int64),
            "D_new-order_oracle": np.asarray(
                new_order_pin_B["l2_order"], dtype=np.int64),
        }
        digest_by_arm = {
            "A_frozen-order_operational": str(order_pin_A.get("order_digest")),
            "B_new-order_operational": str(new_order_pin_B.get("new_order_digest")),
            "C_frozen-order_oracle": str(order_pin_A.get("order_digest")),
            "D_new-order_oracle": str(new_order_pin_B.get("new_order_digest")),
        }

        def current_gates(*, final: bool, wall_now: float) -> tuple:
            gates = _integrity_gates(
                n=n, k1=k1, k2=k2, k_total=k_total, arms=arms, identity=identity,
                manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
                disjoint_pin=disjoint_pin, order_pin_A=order_pin_A,
                new_order_pin_B=new_order_pin_B, set_delta=set_delta,
                formation=formation, records=records, events=events, calls=calls,
                incremental=incremental, accounting=accounting,
                provenance_violations=provenance_violations,
                cap=budget_cap, wall_s=wall_now, resource_stop=resource_stop,
                session_prior_verified=session_prior_verified,
                alt_verified=alt_verified, hazard_pin=hazard_pin,
                prior_stat_before=prior_stat_before,
                prior_stat_after=prior_stat_before,
                alt_stat_before=alt_stat_before,
                alt_stat_after=alt_stat_before,
                dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_before,
                registered_paths=registered_paths, opened_paths=opened_paths,
                final=final)
            failing = [g for g in INTEGRITY_GATE_ORDER if not gates[g]]
            return gates, failing

        def partial_summary(outcome_label: str, gates: dict, wall_now: float) -> dict:
            aggregates = build_aggregates(records)
            aggregates["ir_payload"] = ir_payload_tables(records)
            recount = raw_prior_val_1p5m_recount_events(events)
            derived_key = sum(int(r.get("actual_key_dependent_bits", 0)) for r in records)
            return {
                "analysis": PROTOCOL_NAME,
                "mode": MODE,
                "source": source,
                "n": int(n),
                "k1": int(k1),
                "k2": int(k2),
                "k_total": int(k_total),
                "budget_literal": str(budget_literal),
                "prior_digest": str(prior_digest),
                "alt_digest": str(alt_digest),
                "order_digest_A": str(order_pin_A.get("order_digest")),
                "new_order_digest_B": str(new_order_pin_B.get("new_order_digest")),
                "new_order_program": str(NEW_ORDER_PROGRAM_PIN),
                "order_set_delta": {
                    key: (list(value) if isinstance(value, list) else value)
                    for key, value in dict(set_delta).items()
                },
                "alt_h_literals": alt_h_literals,
                "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
                "remainder_frames": list(FROZEN_REMAINDER_FRAME_RANGE),
                "hold_remainder_2m_counted_never_decoded": list(
                    FROZEN_2M_HOLD_REMAINDER_FRAME_RANGE),
                "dev_source": dict(dev_source_pin),
                "build_dev_disjointness_s2_ii": dict(disjoint_pin),
                "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
                "consumed_1p5m_val_dev_frame_range": list(
                    CONSUMED_1P5M_VAL_DEV_FRAME_RANGE),
                "raw_input_bits_per_block": int(FROZEN_RAW_INPUT_BITS),
                "records_completed": len(records),
                "planned_records": PLANNED_RECORDS,
                "planned_sc_calls": PLANNED_SC_CALLS,
                "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
                "sc_calls": int(calls.get("sc", 0)),
                "stage_b_sampling_calls": int(calls.get("genie", 0)),
                "tag_invocations": int(incremental.get("tag_invocations", 0)),
                "key_dependent_bits": int(incremental.get("key_dependent_bits", 0)),
                "public_control_bits": int(incremental.get("public_control_bits", 0)),
                "recount_mismatch": int(
                    recount["key_dependent_bits"] - derived_key),
                "aggregates": aggregates,
                "integrity": {name: bool(gates.get(name, False))
                              for name in INTEGRITY_GATE_ORDER},
                "integrity_all_pass": bool(
                    all(gates.get(name, False) for name in INTEGRITY_GATE_ORDER)),
                "failing_integrity_gates": [
                    name for name in INTEGRITY_GATE_ORDER if not gates.get(name, False)],
                "outcome_label": outcome_label,
                "wall_s": round(float(wall_now), 6),
                "rss_bytes_peak": opf._peak_rss_bytes(),
                "resource_stop_fired": bool(resource_stop is not None),
                "resource_stop_reason": resource_stop,
                "attempt_read_accounting": dict(
                    accounting, opened_content_paths=list(opened_paths)),
                "claim_scope": (
                    "descriptive first-use 1.5M VAL-remainder single-factor "
                    "L2-order-position reading at the frozen alpha1 "
                    "construction and the per-session (1.5M-TRAIN-derived) "
                    "disclosure point (N=32768, one VAL-remainder block "
                    "2044..2171) with the mandatory H2 IR-1..IR-5 payload "
                    "under each order; C/D are oracle-labelled diagnostic "
                    "controls, never an operational protocol or deployable "
                    "result; not real-frame FER, reconciliation efficiency, "
                    "leakage, key rate, scaling superiority, qualification "
                    "or promotion evidence; the CE-normalized disclosure "
                    "ratio is not qualification efficiency; undetected is "
                    "never success; no reliability, recovery or maintenance "
                    "claim is licensed; the H2 decision is main-thread "
                    "analysis after acceptance, not a FER result; 1.5M "
                    "VAL-remainder DEV is consumed by this packet regardless "
                    "of outcome"
                ),
            }

        def persist(summary_doc: dict) -> None:
            opf._write_json(out_path / "aggregate_summary.json", summary_doc)
            (out_path / "report.md").write_text(
                _render_report(summary_doc), encoding="utf-8")

        slots = []
        for block_index, block in enumerate(formation["blocks"]):
            for arm_index, spec in enumerate(arms):
                slots.append((arm_index, spec, block_index, block))
        total_slots = len(slots)
        views = {idx: _block_view(block, field)
                 for idx, block in enumerate(formation["blocks"])}
        scoring_cache: dict = {}

        def scoring_for(arm_name, block_index):
            key = (arm_name, block_index)
            if key not in scoring_cache:
                p1_use, p2_use, _ = prior_by_source[arm_specs[arm_name].prior_source]
                try:
                    scoring_cache[key] = _dev_block_scoring(
                        formation["blocks"][block_index], p1_use, p2_use)
                except ValueError:
                    scoring_cache[key] = _scoring_absent()
            return scoring_cache[key]

        for slot_index, (arm_index, spec, block_index, block) in enumerate(slots):
            reason = opf._budget_exceeded(start, budget_cap)
            if reason is not None:
                resource_stop = reason
                for rest_index in range(slot_index, total_slots):
                    rest_arm_index, rest_spec, _, rest_block = slots[rest_index]
                    record = _abort_record(
                        spec=rest_spec, arm_index=rest_arm_index, block=rest_block,
                        k_total=int(k_total), budget_literal=budget_literal,
                        prior_digest=prior_digest, alt_digest=alt_digest,
                        order_digest=digest_by_arm[rest_spec.name])
                    records.append(record)
                    opf._append_jsonl(out_path / "per_block_arm_outcomes.jsonl", record)
                    gates_now, _ = current_gates(
                        final=False, wall_now=time.perf_counter() - start)
                    persist(partial_summary(
                        f"RUNNING(record {len(records)}/{total_slots})", gates_now,
                        time.perf_counter() - start))
                break
            view = views[block_index]
            scoring = scoring_for(spec.name, block_index)
            frame_start = int(block["frame_start"])
            seed = l2_order_position_1p5m_seed_bits(
                tag_master, n, spec.name, block_index, bit_length=seed_bits_for(n))

            def _tag_fn(bits, _seed, tag_bits, _fixed=seed):
                return toeplitz_tag(bits, _fixed, tag_bits)

            block_start = time.perf_counter()
            p1_use, p2_use, counts_use = prior_by_source[spec.prior_source]
            l1_use = np.asarray(l1_shared, dtype=np.int64)
            l2_use = np.asarray(l2_by_arm[spec.name], dtype=np.int64)
            arm_digest = str(digest_by_arm[spec.name])
            if spec.kind == "operational":
                # A/B share the accepted operational path bit-for-bit except
                # the L2 order: A runs the frozen-A prefix, B the new-B
                # prefix, both at the SAME Stage-A point on the SAME alpha1
                # table. The swap is hardcoded, never CLI-tunable.
                try:
                    result = run_operational_block(
                        n=n, stream_seed=frame_start, block_index=block_index,
                        bob=view["bob"], high_true=view["high"], low_true=view["low"],
                        u1_true=view["u1"], u2_true=view["u2"],
                        labels_true=view["labels"],
                        labels_true_bits=view["labels_bits"], field=field,
                        p1_table=p1_use, p2_table=p2_use, l1_order=l1_use,
                        l2_order=l2_use, k1=spec.k1, k2=spec.k2, master=tag_master,
                        tag_fn=_tag_fn, calls=calls,
                    )
                    error = None
                except MemoryError:
                    raise
                except Exception as exc:
                    error = type(exc).__name__
                    result = opf.OperationalBlockResult(
                        stream_seed=frame_start, block_index=block_index,
                        outcome="decode_failed", exact=False, label_match=False,
                        tag_pass=False, l1_provenance=None, l2_provenance=None,
                        l1_executed=False, l1_decode_failed=True, l2_invoked=False,
                        l2_skipped_by_l1_failure=True, l2_decode_failed=False,
                        tag_invoked=False, key_dependent_bits=0, public_control_bits=0,
                        nonfinite=False, truth_leak_violation=False,
                        l1_error_type=None, l2_error_type=None,
                        wall_s=time.perf_counter() - block_start,
                        k1=spec.k1, k2=spec.k2,
                    )
                if result.truth_leak_violation:
                    provenance_violations += 1
                resources = opf._cell_resource_record(time.perf_counter() - block_start)
                record = _operational_record(
                    result, spec=spec, arm_index=arm_index, block=block,
                    scoring=scoring, resources=resources,
                    k_total=int(k_total), budget_literal=budget_literal,
                    prior_digest=prior_digest, alt_digest=alt_digest,
                    order_digest=arm_digest, counts_arr=counts_use, p1=p1_use,
                    p2=p2_use, l2_order=l2_use, n=n, view=view, field=field,
                    error=error)
            else:
                try:
                    result = run_oracle_control_block(
                        n=n, block_index=block_index, frame_start=frame_start,
                        bob=view["bob"], high_true=view["high"], low_true=view["low"],
                        u1_true=view["u1"], u2_true=view["u2"],
                        labels_true=view["labels"],
                        labels_true_bits=view["labels_bits"], field=field,
                        p2_table=p2_use, l2_order=l2_use, k2=spec.k2,
                        master=tag_master, tag_fn=_tag_fn, calls=calls,
                    )
                    error = None
                except MemoryError:
                    raise
                except Exception as exc:
                    error = type(exc).__name__
                    result = OracleControlResult(
                        frame_start=frame_start, block_index=block_index,
                        outcome="decode_failed", exact=False, label_match=False,
                        tag_pass=False, l2_invoked=False, l2_decode_failed=False,
                        tag_invoked=False, key_dependent_bits=0, public_control_bits=0,
                        nonfinite=False, truth_leak_violation=False, l2_error_type=None,
                        wall_s=time.perf_counter() - block_start, k2=spec.k2,
                        provenance=ORACLE_PROVENANCE, oracle_truth_use=True,
                    )
                if result.truth_leak_violation:
                    provenance_violations += 1
                resources = opf._cell_resource_record(time.perf_counter() - block_start)
                record = _control_record(
                    result, spec=spec, arm_index=arm_index, block=block,
                    scoring=scoring, resources=resources,
                    k_total=int(k_total), budget_literal=budget_literal,
                    prior_digest=prior_digest, alt_digest=alt_digest,
                    order_digest=arm_digest, counts_arr=counts_use, p1=p1_use,
                    p2=p2_use, l2_order=l2_use, n=n, view=view, field=field,
                    error=error)

            records.append(record)
            opf._append_jsonl(out_path / "per_block_arm_outcomes.jsonl", record)
            for event in raw_prior_val_1p5m_block_events(
                    n, spec, block_index, frame_start, record):
                events.append(event)
                incremental["key_dependent_bits"] += int(event["key_dependent_bits"])
                if str(event["event_type"]) == "verification_tag":
                    incremental["public_control_bits"] += int(event["public_control_bits"])
                    incremental["tag_invocations"] += 1
            gates_now, _ = current_gates(
                final=False, wall_now=time.perf_counter() - start)
            persist(partial_summary(
                f"RUNNING(record {len(records)}/{total_slots})", gates_now,
                time.perf_counter() - start))

        # ---- closing stat checks, final gates, label and evidence.
        wall_s = time.perf_counter() - start
        rss_peak = opf._peak_rss_bytes()
        if real_prior:
            prior_stat_after = _stat_record(Path(prior_path))
        else:
            prior_stat_after = _stat_record(None)
        if real_alt:
            alt_stat_after = _stat_record(Path(alt_prior_path))
        else:
            alt_stat_after = _stat_record(None)
        if real_dev:
            dev_stat_after = _stat_record(Path(dev_pairs))
        else:
            dev_stat_after = _stat_record(None)
        gates = _integrity_gates(
            n=n, k1=k1, k2=k2, k_total=k_total, arms=arms, identity=identity,
            manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
            disjoint_pin=disjoint_pin, order_pin_A=order_pin_A,
            new_order_pin_B=new_order_pin_B, set_delta=set_delta,
            formation=formation, records=records, events=events, calls=calls,
            incremental=incremental, accounting=accounting,
            provenance_violations=provenance_violations,
            cap=budget_cap, wall_s=wall_s, resource_stop=resource_stop,
            session_prior_verified=session_prior_verified,
            alt_verified=alt_verified, hazard_pin=hazard_pin,
            prior_stat_before=prior_stat_before, prior_stat_after=prior_stat_after,
            alt_stat_before=alt_stat_before, alt_stat_after=alt_stat_after,
            dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_after,
            registered_paths=registered_paths, opened_paths=opened_paths,
            final=True)
        outcome_label = l2_order_position_1p5m_label(gates)
        summary = partial_summary(outcome_label, gates, wall_s)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        identity_doc = {
            "predecessor_construction": identity,
            "split_manifest": manifest,
            "dev_source_pin": dev_source_pin,
            "dev_block_pin": dev_pin,
            "build_dev_disjointness_s2_ii": disjoint_pin,
            "expected_session_prior_digest": prior_digest,
            "session_prior_digest": str(session_prior_verified["digest"]),
            "recomputed_session_literals": {
                "h1": float(session_prior_verified["h1"]),
                "h2": float(session_prior_verified["h2"]),
                "h_total": float(session_prior_verified["h_total"]),
            },
            "alt_table_gate": {
                "alt_path": str(alt_verified.get("alt_path")),
                "expected_alt_digest": str(alt_digest),
                "file_digest": str(alt_verified.get("file_digest")),
                "alpha": float(alt_verified["alpha"]),
                "floor_value": float(alt_verified["floor_value"]),
                "keys": list(alt_verified["keys"]),
                "p1_equality_max_abs_diff": float(
                    alt_verified["p1_equality_max_abs_diff"]),
                "alt_h_literals": alt_h_literals,
                "verified": bool(alt_verified["passed"]),
            },
            "k_literal_display": budget_literal,
            "order_file_pin_A": {
                "order_file": str(order_pin_A.get("order_file")),
                "order_digest": str(order_pin_A.get("order_digest")),
                "n": int(order_pin_A.get("n", -1)),
                "k1": int(order_pin_A.get("k1", -1)),
                "k2": int(order_pin_A.get("k2", -1)),
                "prior_digest": str(order_pin_A.get("prior_digest")),
                "train_seeds": [int(s) for s in order_pin_A.get("train_seeds", [])],
                "derivation_seed_pins_provenance_only": True,
                "verified": bool(order_pin_A.get("verified")),
            },
            "expected_order_digest_A": str(order_digest),
            "new_order_file_pin_B": {
                "new_order_file": str(new_order_pin_B.get("new_order_file")),
                "new_order_digest": str(new_order_pin_B.get("new_order_digest")),
                "n": int(new_order_pin_B.get("n", -1)),
                "k1": int(new_order_pin_B.get("k1", -1)),
                "k2": int(new_order_pin_B.get("k2", -1)),
                "prior_digest": str(new_order_pin_B.get("prior_digest")),
                "program": str(new_order_pin_B.get("program")),
                "verified": bool(new_order_pin_B.get("verified")),
            },
            "expected_new_order_digest_B": str(new_order_digest),
            "order_set_delta": {
                key: (list(value) if isinstance(value, list) else value)
                for key, value in dict(set_delta).items()
            },
            "order_position_identity": order_identity,
            "ir_pins": {
                "ir3_threshold_multipliers": [IR3_LO_MULT, IR3_HI_MULT],
                "ir1_bins": int(IR1_BINS),
                "ir4_topk": int(IR4_TOPK),
                "ir5_cap": int(IR5_CAP),
            },
            "stage_b_sampling_calls": int(calls.get("genie", 0)),
            "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
            "prior_stat_before": prior_stat_before,
            "prior_stat_after": prior_stat_after,
            "alt_stat_before": alt_stat_before,
            "alt_stat_after": alt_stat_after,
            "dev_stat_before": dev_stat_before,
            "dev_stat_after": dev_stat_after,
            "attempt_read_accounting": dict(
                accounting, opened_content_paths=list(opened_paths)),
        }
        opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
        persist(summary)
        return L2OrderPosition1p5mRun(summary=summary, records=tuple(records), gates=gates)
    except L2OrderPosition1p5mResourceError:
        raise
    except MemoryError as exc:
        raise L2OrderPosition1p5mResourceError(
            f"resource stop: MemoryError: {exc}") from exc


VERIFY_REUSE_FLAGS = (
    "prior", "prior_digest", "alt_prior", "alt_digest",
    "k1", "k2", "order_file", "order_digest",
    "new_order_file", "new_order_digest",
)
DERIVE_NEW_ORDER_FLAGS = (
    "prior", "prior_digest", "order_file", "out",
)
SHARED_FLAGS = ("source", "floor", "n")
STAGE_B_ONLY_FLAGS = (
    "prior", "prior_digest", "alt_prior", "alt_digest", "k1", "k2", "construction",
    "construction_digest", "dev_pairs", "dev_frames", "block_frames",
    "remainder_frames", "tag_master", "chunk_rows", "tag_bits",
    "order_file", "order_digest", "new_order_file", "new_order_digest", "out_dir",
)
STAGE_B_FLAGS = SHARED_FLAGS + STAGE_B_ONLY_FLAGS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p20r-order-position-1p5m",
        description=(
            "NB-Polar Phase 4-P20R single-factor L2-order-position on first-use "
            "1.5M VAL remainder with mandatory H2 IR-1..IR-5: --verify-reuse "
            "replays the P20M/P20N reuse pins from worktree files with zero "
            "protected opens; --derive-new-order derives the Stage-A new-B "
            "order permutation from worktree-prior arrays only (deterministic, "
            "zero sampling); otherwise all Stage-B flags are required "
            "(frozen command, no production default)"
        ),
    )
    parser.add_argument("--verify-reuse", action="store_true",
                        dest="verify_reuse",
                        help="Stage-A reuse-verification mode (all reuse flags required)")
    parser.add_argument("--derive-new-order", action="store_true",
                        dest="derive_new_order",
                        help="Stage-A new-order derivation mode (derive flags required)")
    parser.add_argument("--prior", default=None)
    parser.add_argument("--prior-digest", default=None, dest="prior_digest")
    parser.add_argument("--alt-prior", default=None, dest="alt_prior")
    parser.add_argument("--alt-digest", default=None, dest="alt_digest")
    parser.add_argument("--source", default=None)
    parser.add_argument("--floor", default=None, type=float)
    parser.add_argument("--n", default=None, type=int)
    parser.add_argument("--k1", default=None, type=int)
    parser.add_argument("--k2", default=None, type=int)
    parser.add_argument("--construction", default=None)
    parser.add_argument("--construction-digest", default=None,
                        dest="construction_digest")
    parser.add_argument("--dev-pairs", default=None, dest="dev_pairs")
    parser.add_argument("--dev-frames", default=None, type=int, nargs=2,
                        dest="dev_frames")
    parser.add_argument("--block-frames", default=None, type=int,
                        dest="block_frames")
    parser.add_argument("--remainder-frames", default=None, type=int, nargs=2,
                        dest="remainder_frames")
    parser.add_argument("--tag-master", default=None, type=int, dest="tag_master")
    parser.add_argument("--chunk-rows", default=None, type=int, dest="chunk_rows")
    parser.add_argument("--tag-bits", default=None, type=int, dest="tag_bits")
    parser.add_argument("--order-file", default=None, dest="order_file")
    parser.add_argument("--order-digest", default=None, dest="order_digest")
    parser.add_argument("--new-order-file", default=None, dest="new_order_file")
    parser.add_argument("--new-order-digest", default=None, dest="new_order_digest")
    parser.add_argument("--out", default=None, dest="out")
    parser.add_argument("--out-dir", default=None, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if bool(args.verify_reuse) and bool(args.derive_new_order):
            raise ValueError(
                "mixed invocation refused: --verify-reuse and --derive-new-order "
                "never combine; refusing before any read or write"
            )
        if args.derive_new_order:
            given_b = [name for name in STAGE_B_ONLY_FLAGS
                       if name not in DERIVE_NEW_ORDER_FLAGS
                       and getattr(args, name) is not None]
            if given_b:
                raise ValueError(
                    "mixed invocation refused: --derive-new-order takes no Stage-B-only flags "
                    f"(got {given_b}); refusing before any read or write"
                )
            given_v = [name for name in VERIFY_REUSE_FLAGS
                       if name not in DERIVE_NEW_ORDER_FLAGS
                       and getattr(args, name) is not None]
            if given_v:
                raise ValueError(
                    "mixed invocation refused: --derive-new-order takes no --verify-reuse-only flags "
                    f"(got {given_v}); refusing before any read or write"
                )
            missing = [name for name in DERIVE_NEW_ORDER_FLAGS
                       if getattr(args, name) is None]
            if missing:
                raise ValueError(
                    "missing required --derive-new-order flags: " + ",".join(sorted(missing))
                    + "; refusing before any read or write"
                )
            with open(args.prior, "rb") as fh:
                data = np.load(fh, allow_pickle=False)
                with data:
                    raw_arrays = {k: np.asarray(data[k]) for k in data.files}
            _gate_call("reuse_prior_identity", verify_corrected_prior_1p5m,
                       raw_arrays, expected_digest=str(args.prior_digest),
                       expected_h1=float(FROZEN_H1), expected_h2=float(FROZEN_H2),
                       expected_total=float(FROZEN_H_TOTAL))
            try:
                frozen_doc = json.loads(
                    Path(args.order_file).read_bytes().decode("utf-8"))
                frozen_l1 = np.asarray(
                    frozen_doc["l1_order"], dtype=np.int64).ravel()
            except (ValueError, KeyError, TypeError) as exc:
                raise ValueError(f"frozen-A order file unreadable: {exc}") from exc
            written = write_new_order_file(
                args.out, prior_arrays=raw_arrays, l1_order=frozen_l1,
                prior_digest=str(args.prior_digest))
            print(json.dumps({
                "new_order_file": written["new_order_file"],
                "new_order_digest": written["new_order_digest"],
                "k1": written["k1"],
                "k2": written["k2"],
                "program": written["program"],
                "sampling_calls": 0,
                "genie_calls": 0,
                "dev_contact": 0,
            }, sort_keys=True))
            return 0
        if args.verify_reuse:
            given_b = [name for name in STAGE_B_ONLY_FLAGS
                       if name not in VERIFY_REUSE_FLAGS
                       and getattr(args, name) is not None]
            if given_b:
                raise ValueError(
                    "mixed invocation refused: --verify-reuse takes no Stage-B-only flags "
                    f"(got {given_b}); refusing before any read or write"
                )
            missing = [name for name in VERIFY_REUSE_FLAGS
                       if getattr(args, name) is None]
            if missing:
                raise ValueError(
                    "missing required --verify-reuse flags: " + ",".join(sorted(missing))
                    + "; refusing before any read or write"
                )
            result = verify_reuse(
                prior=args.prior, alt_prior=args.alt_prior,
                order_file=args.order_file, new_order_file=args.new_order_file,
                prior_digest=args.prior_digest, alt_digest=args.alt_digest,
                order_digest=args.order_digest,
                new_order_digest=args.new_order_digest,
                h1=FROZEN_H1, h2=FROZEN_H2, h_total=FROZEN_H_TOTAL,
                k1=args.k1, k2=args.k2, ce_alt=FROZEN_CE_ALT,
                ce_incumbent=FROZEN_CE_INCUMBENT,
                alt_ideal_length_bits=FROZEN_ALT_IDEAL_LENGTH_BITS,
                d2_feasible=FROZEN_D2_FEASIBLE)
            print(json.dumps({
                "reuse_prior_digest": result["prior_digest"],
                "reuse_alt_digest": result["alt_file_digest"],
                "reuse_order_digest_A": result["order_digest_A"],
                "new_order_digest_B": result["new_order_digest_B"],
                "new_order_program": result["new_order_program"],
                "k_total": result["k_literals"]["k_total"],
                "d2_feasible": result["d2_feasible"],
                "d2_margin_bits": result["d2_margin_bits"],
                "dev_contact": result["dev_contact"],
                "verified": result["verified"],
            }, sort_keys=True))
            return 0
        given = [name for name in STAGE_B_FLAGS if getattr(args, name) is not None]
        missing = [name for name in STAGE_B_FLAGS if getattr(args, name) is None]
        if missing:
            if not given:
                raise ValueError(
                    "ambiguous invocation refused: neither --verify-reuse nor "
                    "--derive-new-order nor any Stage-B flag was given; "
                    "refusing before any read or write"
                )
            raise ValueError(
                "missing required Stage-B flags: " + ",".join(missing)
                + "; refusing before any read or write"
            )
        run = run_l2_order_position_1p5m(
            prior_path=args.prior,
            prior_digest=args.prior_digest,
            alt_prior_path=args.alt_prior,
            alt_digest=args.alt_digest,
            source=args.source,
            floor=args.floor,
            n=args.n,
            k1=args.k1,
            k2=args.k2,
            construction=args.construction,
            construction_digest=args.construction_digest,
            dev_pairs=args.dev_pairs,
            dev_frames=tuple(args.dev_frames),
            block_frames=args.block_frames,
            remainder_frames=tuple(args.remainder_frames),
            tag_master=args.tag_master,
            chunk_rows=args.chunk_rows,
            tag_bits=args.tag_bits,
            order_file=args.order_file,
            order_digest=args.order_digest,
            new_order_file=args.new_order_file,
            new_order_digest=args.new_order_digest,
            out_dir=args.out_dir,
        )
        summary = run.summary
        print(json.dumps({
            "analysis": summary["analysis"],
            "records_completed": summary["records_completed"],
            "operational_exact_count": summary["aggregates"]["operational"][
                "exact_count"],
            "b_maintained_count": summary["aggregates"]["maintenance"][
                "b_maintained_count"],
            "b_restored_count": summary["aggregates"]["maintenance"][
                "b_restored_count"],
            "d_maintained_count": summary["aggregates"]["maintenance"][
                "d_maintained_count"],
            "d_restored_count": summary["aggregates"]["maintenance"][
                "d_restored_count"],
            "order_set_delta": {
                key: (list(value) if isinstance(value, list) else value)
                for key, value in dict(summary["order_set_delta"]).items()
                if not isinstance(value, list) or len(value) <= 16
            },
            "ir_payload": summary["aggregates"]["ir_payload"],
            "integrity_all_pass": summary["integrity_all_pass"],
            "outcome_label": summary["outcome_label"],
            "out_root": args.out_dir,
        }, sort_keys=True))
        return 0
    except (ValueError, FileExistsError, OSError,
            L2OrderPosition1p5mContractError) as exc:
        print(f"nbpolar phase4-p20r 1p5m order-position refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL_NAME", "MODE", "Q", "ALPHA", "N_BOB", "FROZEN_N", "FROZEN_SOURCE",
    "FROZEN_SOURCE_TAG", "FROZEN_FLOOR", "FROZEN_ALPHA", "FROZEN_TARGET_F",
    "NORM_TOL", "FROZEN_HAZARD_R", "FROZEN_PUBLIC_CONTROL_BITS",
    "FROZEN_RAW_INPUT_BITS", "FROZEN_L2_CONSTRUCTION", "FROZEN_DEV_FRAME_RANGE",
    "FROZEN_DEV_FRAMES", "FROZEN_DEV_PAIRS", "FROZEN_BLOCK_COUNT",
    "FROZEN_BLOCK_FRAMES", "FROZEN_PAIRS_PER_FRAME", "FROZEN_SYMBOLS_PER_BLOCK",
    "FROZEN_BLOCK_RANGES", "FROZEN_REMAINDER_FRAME_RANGE", "FROZEN_REMAINDER_FRAMES",
    "FROZEN_REMAINDER_SYMBOLS", "INTRA_FILE_VAL_FRAME_RANGE",
    "CONSUMED_1P5M_TRAIN_FRAME_RANGE", "CONSUMED_1P5M_VAL_DEV_FRAME_RANGE",
    "CONSUMED_1P5M_HOLD_FRAME_RANGE", "CONSUMED_1P5M_HOLD_DEV_FRAME_RANGE",
    "CONSUMED_1P5M_HOLD_REMAINDER_FRAME_RANGE", "FROZEN_BUILD_FRAME_RANGE",
    "FROZEN_2M_HOLD_REMAINDER_FRAME_RANGE", "FROZEN_2M_HOLD_REMAINDER_FRAMES",
    "FROZEN_2M_HOLD_REMAINDER_SYMBOLS", "FROZEN_MANIFEST_TRAIN_FRAMES",
    "FROZEN_MANIFEST_TRAIN_PAIRS", "FROZEN_MANIFEST_VAL_FRAMES",
    "FROZEN_MANIFEST_VAL_PAIRS", "FROZEN_MANIFEST_HOLD_FRAMES",
    "FROZEN_MANIFEST_HOLD_PAIRS", "FROZEN_DEV_PAIRS_PATH", "FROZEN_DEV_PAIRS_SIZE",
    "FROZEN_DEV_PAIRS_SHA256", "REFUSED_1M_DEV_PAIRS_PATH",
    "REFUSED_2M_DEV_PAIRS_PATH", "FROZEN_CONSTRUCTION_PATH",
    "FROZEN_CONSTRUCTION_DIGEST", "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA",
    "PAIRS_LOADER_IDENTITY", "FROZEN_TAG_MASTER", "FROZEN_CHUNK_ROWS",
    "FROZEN_TAG_BITS", "SEED_PREFIX", "FROZEN_PRIOR_PATH", "FROZEN_ORDER_FILE_PATH",
    "FROZEN_ALT_PATH", "FROZEN_NEW_ORDER_PATH", "FROZEN_NEW_ORDER_DIGEST_B",
    "FROZEN_OUT_ROOT", "OUTPUT_FILES", "ATTEMPT_CONSUMPTION_POINT",
    "COMPLETE_LABEL", "RAW_PRIOR_NPZ_KEYS", "ALT_L2_NPZ_KEYS",
    "NEW_ORDER_PROTOCOL", "NEW_ORDER_KIND", "NEW_ORDER_PROGRAM_PIN",
    "NEW_ORDER_RANKING_FUNCTIONAL", "FROZEN_ARM_NAMES", "OPERATIONAL_ARM_NAMES",
    "ORACLE_ARM_NAMES", "PLANNED_SC_CALLS", "PLANNED_TAG_INVOCATIONS",
    "PLANNED_RECORDS", "INTEGRITY_GATE_ORDER", "IR_FIELDS", "IR1_BINS",
    "IR3_LO_MULT", "IR3_HI_MULT", "IR4_TOPK", "IR5_CAP", "FROZEN_COMMAND",
    "FROZEN_SESSION_PRIOR_DIGEST", "FROZEN_H1", "FROZEN_H2", "FROZEN_H_TOTAL",
    "FROZEN_BUDGET_LITERAL", "FROZEN_K_TOTAL", "FROZEN_K1", "FROZEN_K2",
    "FROZEN_ORDER_DIGEST_A", "FROZEN_ALT_DIGEST", "FROZEN_ALT_H1_INC",
    "FROZEN_ALT_H2_ALT", "FROZEN_ALT_H_TOTAL_ALT", "FROZEN_CE_ALT",
    "FROZEN_CE_INCUMBENT", "FROZEN_ALT_IDEAL_LENGTH_BITS",
    "FROZEN_D2_MARGIN_BITS", "FROZEN_D2_FEASIBLE", "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S", "EXTERNAL_TIMEOUT_S", "ULIMIT_VIRTUAL_KIB",
    "L2OrderPosition1p5mContractError", "L2OrderPosition1p5mResourceError",
    "L2OrderPosition1p5mRun", "pins_frozen", "pins_are_frozen",
    "planned_totals", "frozen_arm_table", "check_frozen_arm_table",
    "derive_new_l2_order", "write_new_order_file", "verify_new_order_file",
    "order_set_delta", "verify_reuse", "verify_dev_source_identity_1p5m",
    "verify_val_remainder_containment", "verify_consumed_exclusions_val_remainder",
    "form_val_remainder_blocks", "l2_order_position_1p5m_seed_bits",
    "_ir_hazard_diagnostics", "ir_payload_tables",
    "l2_order_position_1p5m_label", "run_l2_order_position_1p5m", "build_parser",
    "main", "hazard_instrumentation_complete", "maintenance_diagnostics",
    "build_aggregates", "oracle_isolation_ok",
    "VERIFY_REUSE_FLAGS", "DERIVE_NEW_ORDER_FLAGS", "SHARED_FLAGS",
    "STAGE_B_ONLY_FLAGS", "STAGE_B_FLAGS",
]



