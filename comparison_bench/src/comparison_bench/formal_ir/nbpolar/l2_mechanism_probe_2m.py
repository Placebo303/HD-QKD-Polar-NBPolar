"""NB-Polar Phase 4-P20S maximum-information mechanism probe on the merged final 2M block.

Thin importer of the accepted ``l2_alt_hold_ir_2m`` runner (read-only; that
module and every accepted module are never edited here), with the P20Q
``_ir_hazard_diagnostics`` code point as the carried-over callsite pattern
for the mandatory IR-1..IR-4 recorder extension and the P20R
``l2_order_position_1p5m`` ``derive_new_l2_order`` derivation-program
pattern reference for the spike-order derivation. Exact delta list (packet
section 2, d1-d9), nothing else:

- (d1) population -> merged 2M DEV (VAL-remainder tail 2827..2915 +
  HOLD-remainder head 3556..3594, VAL-segment-then-HOLD-segment, ONE
  128-frame block at N=32768; HOLD tail 3595..3644 + 1.5M VAL stub
  2172..2212 + 1.5M HOLD remainder 2725..2766 counted never decoded);
  consumed 1M pool / all consumed 1.5M ranges / consumed 2M TRAIN-as-DEV +
  VAL DEV + HOLD DEV excluded as consumed;
- (d2) prior/orders/alt sources -> the P20O frozen 2M files reused
  read-only behind replayed ``reuse_prior_identity`` +
  ``reuse_alt_identity`` + ``reuse_order_freeze_A`` gates (digests +
  lambda-0.0/alpha-1.0/floor pins + exact key sets + H-literal
  recomputation within 1e-12 + ``p_b`` cross-check + ``p1``-equality
  recheck within 1e-12; worktree-file reads only, never the V25 counts
  NPZ);
- (d3) K pins -> the P20O-derived (K_total,K1,K2)=(7080,334,6746) replayed
  as literals (never recomputed, never recarried from 1.5M, never from
  alt-H);
- (d4) orders -> DUAL: frozen-A order file (``raw_prior_orders_2m.json``,
  byte-identical on arms A/O) + Stage-A spike order file
  (``new_spike_order_2m.json``, byte-identical on arm B), each
  digest-gated, each disclosing first-K1 / first-K2 prefixes at identical
  sizes;
- (d5) arms A/B/O per packet section 6 (same K on A/B, carried K2 on O;
  same alpha1 tables; order SET is the only delta between A and B);
- (d6) new P20S tag domain (master 2026092360, prefix
  ``nbpolar-p20s-mechanism-probe-2m-seed``);
- (d7) spike-order derivation program (worktree-prior-only,
  deterministic, zero sampling/genie, zero protected reads, frozen
  DECIDED 2026-09-20 F-median8 section 3 formula-id) + dual
  order-identity gates + derivation-program pin;
- (d8) merged-DEV population + DEV/build-frames disjointness declared
  inside the TRAIN-exclusion gate (S2-ii: build subset 2M TRAIN 0..2186 vs
  merged DEV subset VAL 2827..2915 + HOLD 3556..3594);
- (d9) IR-5 UNCAPPED full-block binary series + manifest replacing the
  P20Q 4096 cap, same truth-isolation boundary.

No SC/transform/floor-semantics/tag-semantics change; no second factor; no
lambda anywhere; no derivation or sampling at any stage beyond the frozen
deterministic spike permutation (genie 0+0).

The single spike-B order permutation is derived by the frozen program
``derive_spike_l2_order`` (worktree-prior arrays ONLY, deterministic, zero
sampling/genie/seeds, zero protected reads) implementing the frozen
DECIDED 2026-09-20 F-median8 formula (verbatim packet section 3 text; this
module SHALL NOT invent or alter it): "F-median8: score[i] = h[i] - median(h
over the R=8 clipped natural neighborhood of i), where h[i] is the frozen
arm-table hazard atom (-log2 true-cell mass, same recipe as the IR
recorders); rank all 32768 L2 positions by descending score; take the first
K2=6746 positions as arm B's disclosed L2 set; tie-break by ascending
natural block coordinate; deterministic, zero sampling, zero genie calls,
zero protected reads (inputs: worktree ``raw_prior_2m.npz`` arrays only);
arm A's set stays the frozen incumbent-order first-K2 prefix." Position j
is identified with the (b,u2) cell j = b*32+u2 (C-order); U1_cond(b) =
argmax_u1 p1[u1,b] (hard-L1 candidate from the incumbent p1); p2_alt is
recomputed from the ``counts_ab`` worktree array by the frozen alpha=1 rule
(unit pseudocount + 1e-15 floor + column renormalize + accepted
``derive_p2``), which reproduces the frozen alt file bit-exactly. Arm A's
set stays the frozen incumbent-order first-K2 prefix.

Three explicit modes, never mixed: (i) Stage-A reuse verification
(``--verify-reuse``; worktree-file digest recomputation ONLY, zero
protected opens), (ii) Stage-A spike-order derivation
(``--derive-spike-order``; worktree-prior arrays ONLY, deterministic, zero
sampling, fail-if-present output), and (iii) Stage-B frozen command mode
(all Stage-B flags required, no production default). Mixed or ambiguous
invocation refuses before anything is read or written.
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
from . import operational_f13 as opf
from . import raw_prior_val_1p5m as p20m
from . import l2_alt_maintain_2m as p20o
from .algebra import make_gf32
from .prior import derive_p2
from .transform import polar_transform

# Reused accepted contracts (read-only; never reimplemented here).
# 2M reuse layer (accepted P20O/P20Q 2M pins): every digest/H/K/order
# literal below replays the P20O 2M freeze; ``p20m`` is used ONLY for the
# session-agnostic budget-literal recomputation
# (``verify_budget_literal``: pure K_total math from same-run H, never a
# carried absolute) and ``p20n`` ONLY for the session-agnostic frozen
# alpha=1 prefloor rule (``alt_prefloor_table``: pure counts math). No
# 1.5M file, path, frame range, or K literal enters this module.
run_operational_block = p20q.run_operational_block
run_oracle_control_block = p20q.run_oracle_control_block
OracleControlResult = p20q.OracleControlResult
verify_predecessor_construction = p20q.verify_predecessor_construction
verify_dev_manifest_2m = p20q.verify_dev_manifest_2m
verify_session_prior_2m = p20q.verify_session_prior_2m
verify_alt_l2_arrays_2m = p20q.verify_alt_l2_arrays_2m
verify_alt_l2_identity_2m = p20q.verify_alt_l2_identity_2m
verify_stage_b_order_file_2m = p20q.verify_stage_b_order_file_2m
feasibility_literals_2m = p20q.feasibility_literals_2m
check_k_literals = p20q.check_k_literals
verify_reuse_2m = p20q.verify_reuse
verify_budget_literal = p20m.verify_budget_literal
_l2_hazard_diagnostics_2m = p20o._l2_hazard_diagnostics
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
_ir_hist_edges = p20q._ir_hist_edges
_ir_hist_counts = p20q._ir_hist_counts
alt_prefloor_table = p20n.alt_prefloor_table
HAZARD_FIELDS = p20o.HAZARD_FIELDS
OPERATIONAL_PROVENANCE = p20q.OPERATIONAL_PROVENANCE
ORACLE_PROVENANCE = p20q.ORACLE_PROVENANCE
ArmSpec = p20o.ArmSpec

PROTOCOL_NAME = "nbpolar-p20s-mechanism-probe-2m"
MODE = "merged-mechanism-probe-2m"

Q = p20q.Q  # 32
ALPHA = p20q.ALPHA  # 2
N_BOB = p20q.N_BOB  # 1024
FROZEN_N = 32768
FROZEN_SOURCE = "2M"
FROZEN_SOURCE_TAG = "type2_2M_20260121_183657"
FROZEN_FLOOR = 1e-15
FROZEN_ALPHA = 1.0
FROZEN_TARGET_F = 1.3
NORM_TOL = 1e-12
FROZEN_HAZARD_R = 8
FROZEN_PUBLIC_CONTROL_BITS = p20q.FROZEN_PUBLIC_CONTROL_BITS  # 327743
FROZEN_RAW_INPUT_BITS = 10 * FROZEN_N  # 327680 per block
FROZEN_L2_CONSTRUCTION = "alt-α1"

# (d1/d8) merged-2M population: VAL-remainder tail 2827..2915 (89 frames)
# FOLLOWED BY HOLD-remainder head 3556..3594 (39 frames), in
# (frame_id, pair_idx) order within each segment, VAL-segment-then-HOLD
# concatenation -> ONE 128-frame block at N=32768 (D1-A block-convention
# amendment, final block only; manifest-count arithmetic: TRAIN 2187
# [0..2186] + VAL 729 [2187..2915] = VAL-remainder tail 2827..2915; HOLD
# base 2916 + P20Q DEV 640 = HOLD remainder 3556..3644, head 3556..3594
# used, tail 3595..3644 counted never decoded; 2M TRAIN 0..2186 are the
# build frames; consumed 2M VAL DEV 2187..2826 + HOLD DEV 2916..3555 never
# touched; 1.5M VAL stub 2172..2212 + HOLD remainder 2725..2766 counted
# never decoded, never contacted beyond counting).
FROZEN_DEV_FRAMES_VAL = (2827, 2915)
FROZEN_DEV_VAL_FRAMES = 89
FROZEN_DEV_FRAMES_HOLD = (3556, 3594)
FROZEN_DEV_HOLD_FRAMES = 39
FROZEN_DEV_FRAMES = 128
FROZEN_DEV_PAIRS = 32768
FROZEN_BLOCK_COUNT = 1
FROZEN_BLOCK_FRAMES = 128
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_BLOCK_SEGMENTS = (FROZEN_DEV_FRAMES_VAL, FROZEN_DEV_FRAMES_HOLD)
FROZEN_MERGED_FRAME_LIST = tuple(
    list(range(FROZEN_DEV_FRAMES_VAL[0], FROZEN_DEV_FRAMES_VAL[1] + 1))
    + list(range(FROZEN_DEV_FRAMES_HOLD[0], FROZEN_DEV_FRAMES_HOLD[1] + 1))
)
FROZEN_REMAINDER_FRAME_RANGE = (3595, 3644)
FROZEN_REMAINDER_FRAMES = 50
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
INTRA_FILE_VAL_FRAME_RANGE = (2187, 2915)
INTRA_FILE_HOLD_FRAME_RANGE = (2916, 3644)
CONSUMED_2M_TRAIN_FRAME_RANGE = (0, 2186)
CONSUMED_2M_VAL_DEV_FRAME_RANGE = (2187, 2826)
CONSUMED_2M_HOLD_DEV_FRAME_RANGE = (2916, 3555)
CONSUMED_1P5M_TRAIN_FRAME_RANGE = (0, 1659)
CONSUMED_1P5M_VAL_FRAME_RANGE = (1660, 2212)
CONSUMED_1P5M_HOLD_FRAME_RANGE = (2213, 2766)
# S2-ii build frames: counts/build frames hold 2M TRAIN 0..2186 only.
FROZEN_BUILD_FRAME_RANGE = (0, 2186)
# Counted-never-decoded 1.5M remainders (never contacted beyond counting).
FROZEN_1P5M_VAL_STUB_FRAME_RANGE = (2172, 2212)
FROZEN_1P5M_VAL_STUB_FRAMES = 41
FROZEN_1P5M_VAL_STUB_SYMBOLS = (
    FROZEN_1P5M_VAL_STUB_FRAMES * FROZEN_PAIRS_PER_FRAME
)
FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE = (2725, 2766)
FROZEN_1P5M_HOLD_REMAINDER_FRAMES = 42
FROZEN_1P5M_HOLD_REMAINDER_SYMBOLS = (
    FROZEN_1P5M_HOLD_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
)
# Consumed cross-session identities (fail-closed by source tag; frame
# integers alone are never identity).
CONSUMED_1M_SOURCE_TAG = p20o.CONSUMED_1M_SOURCE_TAG
CONSUMED_1P5M_SOURCE_TAG = p20o.CONSUMED_1P5M_SOURCE_TAG
CONSUMED_1M_FRAME_RANGE = (0, 1199)
FROZEN_MANIFEST_TRAIN_FRAMES = 2187
FROZEN_MANIFEST_TRAIN_PAIRS = 559872
FROZEN_MANIFEST_VAL_FRAMES = 729
FROZEN_MANIFEST_VAL_PAIRS = 186624
FROZEN_MANIFEST_HOLD_FRAMES = 729
FROZEN_MANIFEST_HOLD_PAIRS = 186624

# Device source identity: the 2M pairs parquet ONLY (same session file as
# P20O/P20Q; provenance pin frozen by the v13r3fresh build-manifest
# cross-check; the 2M file itself is NEVER opened/statted/listed in Stage
# A). The size/sha literals below are build-manifest provenance constants;
# the size is additionally enforced from stat before the content open at
# run level.
FROZEN_DEV_PAIRS_PATH = p20o.FROZEN_DEV_PAIRS_PATH
FROZEN_DEV_PAIRS_SIZE = p20o.FROZEN_DEV_PAIRS_SIZE
FROZEN_DEV_PAIRS_SHA256 = p20o.FROZEN_DEV_PAIRS_SHA256
REFUSED_1M_DEV_PAIRS_PATH = p20o.REFUSED_1M_DEV_PAIRS_PATH
REFUSED_1P5M_DEV_PAIRS_PATH = p20o.REFUSED_1P5M_DEV_PAIRS_PATH
FROZEN_DEV_BUILD_MANIFEST_PATH = p20o.FROZEN_DEV_BUILD_MANIFEST_PATH
FROZEN_CONSTRUCTION_PATH = p20o.FROZEN_CONSTRUCTION_PATH
FROZEN_CONSTRUCTION_DIGEST = p20o.FROZEN_CONSTRUCTION_DIGEST
FROZEN_MANIFEST_PATH = p20o.FROZEN_MANIFEST_PATH
FROZEN_MANIFEST_SCHEMA = p20o.FROZEN_MANIFEST_SCHEMA
PAIRS_LOADER_IDENTITY = p20o.PAIRS_LOADER_IDENTITY

# (d6) new P20S tag domain.
FROZEN_TAG_MASTER = 2026092360
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = 64
SEED_PREFIX = "nbpolar-p20s-mechanism-probe-2m-seed"

# (d2/d3) P20O reuse pins, replayed as literals (never recomputed, never
# recarried from 1.5M; the alt-H literals are descriptive only, never
# budget inputs).
FROZEN_SESSION_PRIOR_DIGEST = (
    "b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587"
)
FROZEN_ORDER_DIGEST_A = (
    "b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906"
)
FROZEN_ALT_DIGEST = (
    "98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5"
)
FROZEN_H1 = 0.02566204884275839
FROZEN_H2 = 0.8069006731309893
FROZEN_H_TOTAL = 0.8325627219737477
FROZEN_BUDGET_LITERAL = (
    "1.3*32768*0.8325627219737477-64 over 5, floored, clipped [0,65536] = 7080"
)
FROZEN_K_TOTAL = 7080
FROZEN_K1 = 334
FROZEN_K2 = 6746
FROZEN_ALT_H1_INC = 0.02566204884275839
FROZEN_ALT_H2_ALT = 1.3245794596410305
FROZEN_ALT_H_TOTAL_ALT = 1.3502415084837889
# D1/D2 replay literals (P20O freeze; construction-validity quantities,
# never decoding inputs and never thresholds on results).
FROZEN_CE_ALT = 0.8850983725781965
FROZEN_CE_INCUMBENT = 0.8069006731253678
FROZEN_ALT_IDEAL_LENGTH_BITS = 29002.90347264234
FROZEN_D2_MARGIN_BITS = 4791.09652735766
FROZEN_D2_FEASIBLE = True

# Stage-A reuse products (frozen paths; digests pinned above).
FROZEN_PRIOR_PATH = p20o.FROZEN_PRIOR_PATH
FROZEN_ORDER_FILE_PATH = p20o.FROZEN_ORDER_FILE_PATH
FROZEN_ALT_PATH = p20o.FROZEN_ALT_PATH
FROZEN_SPIKE_ORDER_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/"
    "new_spike_order_2m.json"
)
# Stage-A spike order digest pin (filled once by the frozen derivation;
# gate on equality thereafter).
FROZEN_SPIKE_ORDER_DIGEST_B = (
    "139f34c3152dfd5c7389c860b4f52ce23e5b6759465714fdb86ab5c605de1864"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/"
    "l2_mechanism_probe_2m"
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "input_and_predecessor_identity.json",
    "per_block_arm_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
    "ir5_full_manifest.json",
    "A_hazard_bits_f32le.bin",
    "A_inprefix_u8.bin",
    "A_inu_u8.bin",
    "B_hazard_bits_f32le.bin",
    "B_inprefix_u8.bin",
    "B_inu_u8.bin",
    "O_hazard_bits_f32le.bin",
    "O_inprefix_u8.bin",
    "O_inu_u8.bin",
)
ATTEMPT_CONSUMPTION_POINT = "first protected content open (merged 2M pairs parquet)"
COMPLETE_LABEL = (
    "TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE"
)

# Exact keys of the reused Stage-A artifacts (no more, no fewer).
RAW_PRIOR_NPZ_KEYS = p20o.RAW_PRIOR_NPZ_KEYS  # 10 keys
ALT_L2_NPZ_KEYS = p20o.ALT_L2_NPZ_KEYS  # 9 keys

# Spike-B order file identity (frozen format; mirrors the frozen-A order
# file keys with the P20S protocol + derivation provenance).
SPIKE_ORDER_PROTOCOL = PROTOCOL_NAME
SPIKE_ORDER_KIND = "spike-l2-order-file"

# Frozen derivation-program pin (module + function + rule + determinism).
SPIKE_PROGRAM_PIN = (
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar."
    "l2_mechanism_probe_2m:derive_spike_l2_order -- "
    "frozen alpha=1 recompute (alt_prefloor_table + 1e-15 floor + column "
    "renormalize + accepted derive_p2) + hard-L1 argmax over incumbent p1 "
    "+ per-(b,u2)-cell hazard -log2 p2_alt[u1hard[b],b,u2] + F-median8 "
    "local-excess score h[i]-median(W8(i)) R=8 clipped natural neighborhood "
    "+ C-order cell index j=b*32+u2 + stable descending argsort (ties "
    "ascending j); deterministic; zero sampling/genie/seeds; inputs "
    "worktree raw_prior_2m.npz arrays only"
)
SPIKE_FORMULA_ID = "F_MEDIAN8_DECIDED_20260920_H_MINUS_LOCAL_MEDIAN_W8"
SPIKE_FORMULA_TEXT = (
    "F-median8: score[i] = h[i] \u2212 median(h over the R=8 clipped "
    "natural neighborhood of i), where h[i] is the frozen arm-table hazard "
    "atom (-log2 true-cell mass, same recipe as the IR recorders); rank all "
    "32768 L2 positions by descending score; take the first K2=6746 "
    "positions as arm B's disclosed L2 set; tie-break by ascending natural "
    "block coordinate; deterministic, zero sampling, zero genie calls, zero "
    "protected reads (inputs: worktree `raw_prior_2m.npz` arrays only); arm "
    "A's set stays the frozen incumbent-order first-K2 prefix."
)

FROZEN_ARM_NAMES = (
    "A_anchor_frozen_order",
    "B_spike_local_order",
    "O_true_l1_oracle",
)
OPERATIONAL_ARM_NAMES = (
    "A_anchor_frozen_order", "B_spike_local_order",
)
ORACLE_ARM_NAMES = (
    "O_true_l1_oracle",
)
PLANNED_SC_CALLS = 5
PLANNED_TAG_INVOCATIONS = 3
PLANNED_RECORDS = 3

# (d7/d9) mandatory IR-1..IR-4 pins (all frozen PRESENT, bounded,
# recording-only, post-decode; same caps/formulas as P20Q section 7; the
# truth-isolation boundary is pinned in the record writers and covered by
# the sentinel test) + IR-5 UNCAPPED full-block binary pins (d9).
IR1_BINS = 64
IR1_EDGE_LO_BITS = 1e-3
IR1_EDGE_HI_BITS = 32.0
IR3_LO_MULT = 1.0
IR3_HI_MULT = 2.0
IR4_TOPK = 16
# IR-5 UNCAPPED (d9): per record exactly three binary little-endian series
# (32768 float32-LE hazards + 32768 uint8 in-prefix flags + 32768 uint8
# U-domain flags) + `ir5full-v1` manifest linkage; binary `.bin` + JSON
# manifest ONLY (no text-JSON float dumps, no npz/npy/parquet).
IR5_FULL_N = 32768
IR5_FORMAT_VERSION = "ir5full-v1"
IR5_HAZARD_DTYPE = "<f4"
IR5_FLAG_DTYPE = "u1"
IR5_HAZARD_BYTES = 131072
IR5_FLAG_BYTES = 32768
IR5_PER_RECORD_BUDGET_BYTES = 400 * 1024
IR5_ROOT_BUDGET_BYTES = 1536 * 1024
IR5_MAX_FILE_BYTES = 2 * 1024 * 1024
IR5_ARMV_PREFIX = {
    "A_anchor_frozen_order": "A",
    "B_spike_local_order": "B",
    "O_true_l1_oracle": "O",
}
IR_FIELDS = (
    "ir1_hist_edges_bits",
    "ir1_hist_prefix_counts",
    "ir1_hist_outside_counts",
    "ir2_first_error_hazard_rank_pct",
    "ir3_thresh_lo_bits",
    "ir3_thresh_hi_bits",
    "ir3_prefix_above_lo_count",
    "ir3_prefix_above_lo_frac",
    "ir3_prefix_above_hi_count",
    "ir3_prefix_above_hi_frac",
    "ir4_topk_coords",
    "ir4_topk_hazard_bits",
    "ir4_topk_in_prefix",
    "ir4_topk_ranks",
    "ir5_hazard_bits_file",
    "ir5_hazard_bits_sha256",
    "ir5_inprefix_file",
    "ir5_inprefix_sha256",
    "ir5_inu_file",
    "ir5_inu_sha256",
    "ir5_format_version",
    "ir5_total_len",
)

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "reuse_prior_identity",
    "reuse_alt_identity",
    "alt_construction_budget_feasibility_replayed",
    "dev_split_manifest_identity",
    "dev_block_range_identity",
    "order_derivation_identity",
    "frozen_order_identity_A",
    "spike_order_identity_B",
    "order_derivation_program_identity",
    "k_literal_exact",
    "budget_literal_replayed",
    "target_population_contract",
    "dev_population_exact",
    "blocks_exact_with_declared_remainder",
    "three_records_exact",
    "genie_calls_exact",
    "sc_calls_exact",
    "tags_exact",
    "orders_valid_k_prefixes_within_registered_arms",
    "order_set_delta_recorded",
    "hazard_instrumentation_complete",
    "ir_payload_complete",
    "ir5_full_manifest_identity",
    "evidence_size_rule_met",
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


class L2MechanismProbe2mContractError(ValueError):
    """Pre-open population/formation failure: BLOCKED(<earliest gate>)."""


class L2MechanismProbe2mResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


def _gate_call(gate_name, fn, *args, **kwargs):
    """Run an accepted gate helper read-only, tagged with the P20S gate name."""
    try:
        return fn(*args, **kwargs)
    except (ValueError, FileNotFoundError) as exc:
        raise L2MechanismProbe2mContractError(f"BLOCKED({gate_name}): {exc}") from exc


def pins_frozen() -> dict:
    """Fail-closed Stage-A pin-state check: every pin must be filled."""
    pins = {
        "session_prior_digest": FROZEN_SESSION_PRIOR_DIGEST,
        "order_digest_A": FROZEN_ORDER_DIGEST_A,
        "spike_order_digest_B": FROZEN_SPIKE_ORDER_DIGEST_B,
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
# (d5) arms: three hardcoded specs, never CLI-tunable, never extensible.
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
        2 * (5 * k_total + 64) + (5 * k2 + 64)
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
        ArmSpec("A_anchor_frozen_order", "operational", k1, k2,
                5 * k_total + 64, OPERATIONAL_PROVENANCE, "alt"),
        ArmSpec("B_spike_local_order", "operational", k1, k2,
                5 * k_total + 64, OPERATIONAL_PROVENANCE, "alt"),
        ArmSpec("O_true_l1_oracle", "oracle_control", 0, k2,
                5 * k2 + 64, ORACLE_PROVENANCE, "alt"),
    )


def check_frozen_arm_table() -> dict:
    """Fail-closed pin of the three frozen arms and their design accounting.

    Pure code-level check (no I/O): arm names/order, the Stage-A replayed
    (K1,K2,K_total), the 5K+64 leakage arithmetic, the frozen alpha1
    construction on all three arms (A frozen order, B spike order at the
    SAME K, O frozen-order true-L1 oracle at carried K2), the B-A exact
    zero key-bit delta and the 5 SC / 3 tag / 3 record design totals. Any
    drift raises before any root exists.
    """
    arms = frozen_arm_table()
    if tuple(spec.name for spec in arms) != FROZEN_ARM_NAMES:
        raise ValueError(f"frozen arm order drifted: {tuple(s.name for s in arms)!r}")
    a, b, o = arms
    pins = pins_frozen()
    k1, k2 = int(pins["k1"]), int(pins["k2"])
    k_total = int(pins["k_total"])
    if (a.kind, a.k1, a.k2, a.prior_source, a.provenance) != (
            "operational", k1, k2, "alt", OPERATIONAL_PROVENANCE):
        raise ValueError("frozen A_anchor_frozen_order arm drifted")
    if (b.kind, b.k1, b.k2, b.prior_source, b.provenance) != (
            "operational", k1, k2, "alt", OPERATIONAL_PROVENANCE):
        raise ValueError("frozen B_spike_local_order arm drifted")
    if (o.kind, o.k1, o.k2, o.prior_source, o.provenance) != (
            "oracle_control", 0, k2, "alt", ORACLE_PROVENANCE):
        raise ValueError("frozen O_true_l1_oracle arm drifted")
    if int(a.k1) + int(a.k2) != k_total:
        raise ValueError("frozen A K1+K2 != Stage-A K_total")
    if int(a.leakage_bits) != 5 * k_total + 64:
        raise ValueError("frozen A/B leakage != 5*(K1+K2)+64")
    if int(o.leakage_bits) != 5 * k2 + 64:
        raise ValueError("frozen O leakage != 5*K2+64")
    if int(b.leakage_bits) - int(a.leakage_bits) != 0:
        raise ValueError("frozen B-vs-A key-bit delta must be exactly 0")
    if PLANNED_SC_CALLS != 5:
        raise ValueError(f"frozen design must plan 5 SC calls, got {PLANNED_SC_CALLS}")
    if PLANNED_TAG_INVOCATIONS != 3:
        raise ValueError(
            f"frozen design must plan 3 tags, got {PLANNED_TAG_INVOCATIONS}")
    if PLANNED_RECORDS != 3:
        raise ValueError(f"frozen design must plan 3 records, got {PLANNED_RECORDS}")
    totals = planned_totals(k1, k2)
    expected_key_total = FROZEN_BLOCK_COUNT * (
        2 * (5 * (k1 + k2) + 64) + (5 * k2 + 64))
    if int(totals["planned_key_dependent_bits"]) != int(expected_key_total):
        raise ValueError("frozen planned key-dependent total drifted")
    if int(totals["planned_public_control_bits"]) != 3 * FROZEN_PUBLIC_CONTROL_BITS:
        raise ValueError("frozen planned public total != 3*327743")
    cap_ratio = float(a.leakage_bits / FROZEN_RAW_INPUT_BITS)
    if not cap_ratio < 0.5:
        raise ValueError("frozen A/B cap must sit well below raw input bits")
    return {
        "arms": [spec.name for spec in arms],
        "a": {"k1": int(a.k1), "k2": int(a.k2), "leakage_bits": int(a.leakage_bits)},
        "b": {"k1": int(b.k1), "k2": int(b.k2), "leakage_bits": int(b.leakage_bits)},
        "o": {"k1": int(o.k1), "k2": int(o.k2), "leakage_bits": int(o.leakage_bits)},
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


def _check_dev_frames_val(value) -> tuple:
    try:
        pair = tuple(opf._as_int(v, "dev-frames-val", minimum=0) for v in value)
    except TypeError as exc:
        raise TypeError(f"dev-frames-val must be a pair of integers: {exc}") from exc
    if pair != tuple(FROZEN_DEV_FRAMES_VAL):
        raise ValueError(
            f"frozen point requires dev-frames-val={tuple(FROZEN_DEV_FRAMES_VAL)}, got {pair}"
        )
    return pair


def _check_dev_frames_hold(value) -> tuple:
    try:
        pair = tuple(opf._as_int(v, "dev-frames-hold", minimum=0) for v in value)
    except TypeError as exc:
        raise TypeError(f"dev-frames-hold must be a pair of integers: {exc}") from exc
    if pair != tuple(FROZEN_DEV_FRAMES_HOLD):
        raise ValueError(
            "frozen point requires dev-frames-hold="
            f"{tuple(FROZEN_DEV_FRAMES_HOLD)}, got {pair}"
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
            "frozen point requires prior-digest=<Stage-A 2M canonical prior digest>"
        )
    return digest


def _check_order_digest_A(value) -> str:
    digest = str(value)
    if digest != str(FROZEN_ORDER_DIGEST_A):
        raise ValueError(
            "frozen point requires order-digest=<Stage-A frozen-A order-file sha256>"
        )
    return digest


def _check_spike_order_digest_B(value) -> str:
    if FROZEN_SPIKE_ORDER_DIGEST_B is None:
        raise ValueError("Stage-A freeze not yet applied: spike-B order digest pin is None")
    digest = str(value)
    if digest != str(FROZEN_SPIKE_ORDER_DIGEST_B):
        raise ValueError(
            "frozen point requires spike-order-digest=<Stage-A spike-B order-file sha256>"
        )
    return digest


def _check_spike_formula(value) -> str:
    formula = str(value)
    if formula != str(SPIKE_FORMULA_ID):
        raise ValueError(
            "frozen point requires spike-formula=<Stage-A frozen DECIDED 2026-09-20 "
            "F-median8 formula-id>"
        )
    return formula


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
            or FROZEN_SPIKE_ORDER_DIGEST_B is None:
        raise ValueError("Stage-A freeze not yet applied: Stage-B pins are None")
    return (
        "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
        "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
        "ulimit -v 2097152\n"
        "timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
        "comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_mechanism_probe_2m "
        f"--prior {FROZEN_PRIOR_PATH} --prior-digest {FROZEN_SESSION_PRIOR_DIGEST} "
        f"--alt-prior {FROZEN_ALT_PATH} --alt-digest {FROZEN_ALT_DIGEST} "
        f"--source 2M --floor 1e-15 --n 32768 --k1 {int(k1)} --k2 {int(k2)} "
        f"--construction {FROZEN_CONSTRUCTION_PATH} "
        f"--construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
        f"--dev-pairs {FROZEN_DEV_PAIRS_PATH} "
        "--dev-frames-val 2827 2915 --dev-frames-hold 3556 3594 --block-frames 128 "
        "--remainder-frames 3595 3644 "
        "--tag-master 2026092360 --chunk-rows 512 --tag-bits 64 "
        f"--order-file {FROZEN_ORDER_FILE_PATH} --order-digest {FROZEN_ORDER_DIGEST_A} "
        f"--spike-order-file {FROZEN_SPIKE_ORDER_PATH} "
        f"--spike-order-digest {FROZEN_SPIKE_ORDER_DIGEST_B} "
        f"--spike-formula {SPIKE_FORMULA_ID} "
        f"--out-dir {FROZEN_OUT_ROOT}"
    )


FROZEN_COMMAND = frozen_command() if pins_are_frozen() else None


# ---------------------------------------------------------------------------
# Stage-A new-B order derivation (section 3 contract + frozen B-1
# functional; worktree-prior arrays ONLY; deterministic; zero sampling,
# zero genie, zero protected reads).
# ---------------------------------------------------------------------------

def derive_spike_l2_order(prior_arrays) -> dict:
    """Derive the spike L2-order permutation under frozen F-median8.

    Pure function (no I/O, no RNG, no sampler): recomputes ``p2_alt`` from
    the ``counts_ab`` array by the frozen alpha=1 rule, takes the hard-L1
    candidate ``u1hard[b] = argmax_u1 p1[u1,b]`` from the incumbent ``p1``,
    forms the static hazard vector ``h[j] = -log2 p2_alt[u1hard[b],b,u2]``
    at cell ``j = b*32+u2`` (C-order flatten of the (1024,32) table), then
    scores ``score[i] = h[i] - median(h over the R=8 clipped natural
    neighborhood of i)`` with ``R = FROZEN_HAZARD_R`` and ranks all 32768
    L2 positions by descending score with ties broken by ascending ``j``
    (stable descending argsort). Returns the length-32768 spike-L2
    permutation plus the carried frozen-L1 reference inputs needed by the
    file writer. Any non-positive table mass raises (never a silent fill).
    Sampling/genie calls are 0 by construction (no sampler exists here).
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
            "spike-order derivation: non-positive or non-finite alt-table mass "
            "at a hard-L1-conditioned cell"
        )
    hazards = -np.log2(masses)
    flat = np.ascontiguousarray(hazards.reshape(-1))
    if flat.shape != (FROZEN_N,):
        raise ValueError(f"cell hazards must be length {FROZEN_N}, got {flat.shape}")
    # F-median8 local-excess scores (frozen DECIDED 2026-09-20 formula-id).
    n = int(FROZEN_N)
    r = int(FROZEN_HAZARD_R)
    offsets = np.arange(-r, r + 1, dtype=np.int64)
    idx = np.arange(n, dtype=np.int64)[:, None] + offsets[None, :]
    valid = (idx >= 0) & (idx < n)
    window = np.where(valid, flat[np.clip(idx, 0, n - 1)], np.nan)
    medians = np.ascontiguousarray(np.nanmedian(window, axis=1))
    if not np.isfinite(medians).all():
        raise ValueError("spike-order derivation: non-finite local median hazard")
    scores = np.ascontiguousarray(flat - medians)
    spike_l2_order = np.argsort(-scores, kind="stable").astype(np.int64)
    if set(spike_l2_order.tolist()) != set(range(FROZEN_N)):
        raise ValueError("derived spike-L2 order is not a permutation of 0..N-1")
    return {
        "spike_l2_order": np.ascontiguousarray(spike_l2_order),
        "cell_hazards": np.ascontiguousarray(flat),
        "cell_scores": np.ascontiguousarray(scores),
        "cell_medians": np.ascontiguousarray(medians),
        "u1hard": np.ascontiguousarray(u1hard),
        "k2": int(FROZEN_K2),
        "formula_id": SPIKE_FORMULA_ID,
        "program": SPIKE_PROGRAM_PIN,
        "sampling_calls": 0,
        "genie_calls": 0,
    }


def write_spike_order_file(path, *, prior_arrays, l1_order, prior_digest: str) -> dict:
    """Write the Stage-A spike-B order file (fail-if-present; deterministic).

    Worktree-prior arrays ONLY (plus the frozen-A L1 carried verbatim and
    the replayed prior digest for provenance). The file holds the full L1
    (carried frozen) + spike-L2 permutations plus provenance (reused-prior
    digest + formula-id + program pin + zero-sampling attestation). Refuses
    if the output already exists.
    """
    out = Path(path)
    if out.exists():
        raise FileExistsError(f"refusing to overwrite existing spike-order file: {out}")
    derived = derive_spike_l2_order(prior_arrays)
    l1 = np.asarray(l1_order, dtype=np.int64).ravel()
    if l1.shape != (FROZEN_N,) or set(l1.tolist()) != set(range(FROZEN_N)):
        raise ValueError("carried L1 order is not a permutation of 0..N-1")
    if str(prior_digest) != str(FROZEN_SESSION_PRIOR_DIGEST):
        raise ValueError("spike-order provenance prior digest != frozen reuse pin")
    doc = {
        "protocol": SPIKE_ORDER_PROTOCOL,
        "kind": SPIKE_ORDER_KIND,
        "n": int(FROZEN_N),
        "k_total": int(FROZEN_K_TOTAL),
        "k1": int(FROZEN_K1),
        "k2": int(FROZEN_K2),
        "l1_order": [int(v) for v in l1.tolist()],
        "l2_order": [int(v) for v in derived["spike_l2_order"].tolist()],
        "derivation": {
            "reused_prior_digest": str(prior_digest),
            "formula_id": str(SPIKE_FORMULA_ID),
            "formula_text": str(SPIKE_FORMULA_TEXT),
            "program": SPIKE_PROGRAM_PIN,
            "cell_convention": "j=b*32+u2 C-order over (b,u2)",
            "hazard_radius_R": int(FROZEN_HAZARD_R),
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
        "spike_order_file": str(out),
        "spike_order_digest": file_digest,
        "k1": int(FROZEN_K1),
        "k2": int(FROZEN_K2),
        "formula_id": str(SPIKE_FORMULA_ID),
        "program": SPIKE_PROGRAM_PIN,
        "verified": True,
    }


def verify_spike_order_file(path, *, expected_digest: str,
                          expected_prior_digest: str,
                          frozen_l1_order, expected_k1: int,
                          expected_k2: int, expected_k_total: int) -> dict:
    """Verify the Stage-A spike-B order file (``spike_order_identity_B`` gate).

    Worktree-file read only (never a protected open): the file-bytes
    sha256 must equal the frozen ``--spike-order-digest`` (which itself
    must equal the Stage-A pin), the document must carry the frozen P20S
    protocol/kind with ``n == 32768``, the L2 order must be a permutation
    of ``0..N-1``, the L1 order must equal the carried frozen P20O L1 order
    array (L1-carried check), the frozen prefix lengths must equal the
    replayed (K1,K2), and the derivation provenance (reused-prior digest +
    formula-id pin + program pin + zero-sampling attestation) must replay
    exactly. Any mismatch raises before any SC call. Stage B performs zero
    sampling: this function loads a frozen file, never a sampler.
    """
    if FROZEN_SPIKE_ORDER_DIGEST_B is None:
        raise ValueError("Stage-A freeze not yet applied: spike-B order digest pin is None")
    if str(expected_digest) != str(FROZEN_SPIKE_ORDER_DIGEST_B):
        raise ValueError("spike-order-file digest flag != frozen Stage-A spike-B digest")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Stage-A spike-B order file not found: {p}")
    raw = p.read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    if file_digest != str(expected_digest):
        raise ValueError(
            "spike-order-file bytes sha256 != frozen --spike-order-digest "
            "(refusing before any SC call)"
        )
    try:
        doc = json.loads(raw.decode("utf-8"))
    except ValueError as exc:
        raise ValueError(f"spike-order file unreadable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("protocol") != SPIKE_ORDER_PROTOCOL:
        raise ValueError("spike-order file protocol != frozen P20S protocol")
    if doc.get("kind") != SPIKE_ORDER_KIND:
        raise ValueError("spike-order file kind != spike-l2-order-file")
    if int(doc.get("n", -1)) != FROZEN_N:
        raise ValueError("spike-order file n != frozen N")
    try:
        l1_order = np.asarray(doc["l1_order"], dtype=np.int64).ravel()
        l2_order = np.asarray(doc["l2_order"], dtype=np.int64).ravel()
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"spike-order file orders malformed: {exc}") from exc
    if l2_order.shape != (FROZEN_N,) or set(l2_order.tolist()) != set(range(FROZEN_N)):
        raise ValueError("spike-order file l2_order is not a permutation of 0..N-1")
    frozen_l1 = np.asarray(frozen_l1_order, dtype=np.int64).ravel()
    if l1_order.shape != (FROZEN_N,) or not np.array_equal(l1_order, frozen_l1):
        raise ValueError("spike-order file l1_order != carried frozen P20O L1 order")
    if int(doc.get("k_total", -1)) != int(expected_k_total):
        raise ValueError("spike-order file k_total != replayed K_total")
    if int(doc.get("k1", -1)) != int(expected_k1):
        raise ValueError("spike-order file k1 != replayed K1")
    if int(doc.get("k2", -1)) != int(expected_k2):
        raise ValueError("spike-order file k2 != replayed K2")
    derivation = doc.get("derivation")
    if not isinstance(derivation, dict):
        raise ValueError("spike-order file derivation provenance missing")
    if str(derivation.get("reused_prior_digest")) != str(expected_prior_digest):
        raise ValueError("spike-order derivation prior digest != frozen reuse pin")
    if str(derivation.get("formula_id")) != str(SPIKE_FORMULA_ID):
        raise ValueError("spike-order derivation formula-id != frozen F-median8 pin")
    if str(derivation.get("program")) != str(SPIKE_PROGRAM_PIN):
        raise ValueError("spike-order derivation program pin != frozen program pin")
    if derivation.get("zero_sampling_attestation") is not True:
        raise ValueError("spike-order derivation zero-sampling attestation != true")
    return {
        "spike_order_file": str(p),
        "spike_order_digest": file_digest,
        "n": int(FROZEN_N),
        "l1_order": np.ascontiguousarray(l1_order),
        "l2_order": np.ascontiguousarray(l2_order),
        "k_total": int(expected_k_total),
        "k1": int(expected_k1),
        "k2": int(expected_k2),
        "prior_digest": str(expected_prior_digest),
        "formula_id": str(SPIKE_FORMULA_ID),
        "program": str(SPIKE_PROGRAM_PIN),
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
    spike_order_file,
    prior_digest: str,
    alt_digest: str,
    order_digest: str,
    spike_order_digest: str,
    spike_formula: str,
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
    """Replay the P20O reuse pins + spike identity from worktree files BEFORE any DEV contact.

    Loads the frozen 2M worktree files read-only (never the V25 counts
    NPZ, never any pairs parquet): the accepted P20Q ``verify_reuse``
    replays the canonical prior digest + H-literal recomputation within
    1e-12 + ``p_b`` cross-check + floor pins, file-bytes alt/frozen-A-order
    digests + alpha-1.0/floor pins + exact key sets + ``p1``-equality
    within 1e-12 + descriptive alt-H replay, K-literal replay with the S2-i
    budget-literal display, and the D1/D2 feasibility replay recomputed
    from the worktree counts; this wrapper then verifies the spike-B order
    identity (file-bytes digest + L1-carried + formula-id + program pin +
    zero-sampling attestation) with the byte-exact A-vs-B set-delta table
    and pins the D2 margin literal. Any replay mismatch raises with DEV
    untouched (merged-DEV read stays 0/1) and no Stage-B request may
    follow.
    """
    if str(spike_formula) != str(SPIKE_FORMULA_ID):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(order_derivation_program_identity): "
            "--spike-formula != frozen F-median8 formula-id"
        )
    base = _gate_call(
        "reuse_prior_identity", verify_reuse_2m,
        prior=prior, alt_prior=alt_prior, order_file=order_file,
        prior_digest=str(prior_digest), alt_digest=str(alt_digest),
        order_digest=str(order_digest), h1=float(h1), h2=float(h2),
        h_total=float(h_total), k1=int(k1), k2=int(k2),
        ce_alt=float(ce_alt), ce_incumbent=float(ce_incumbent),
        alt_ideal_length_bits=float(alt_ideal_length_bits),
        d2_feasible=bool(d2_feasible))
    order_pin = _gate_call(
        "reuse_order_freeze_A", verify_stage_b_order_file_2m, str(order_file),
        expected_digest=str(order_digest),
        expected_prior_digest=str(prior_digest),
        expected_k1=int(k1), expected_k2=int(k2),
        expected_k_total=int(base["k_literals"]["k_total"]))
    spike_pin = _gate_call(
        "spike_order_identity_B", verify_spike_order_file, str(spike_order_file),
        expected_digest=str(spike_order_digest),
        expected_prior_digest=str(prior_digest),
        frozen_l1_order=np.asarray(order_pin["l1_order"]),
        expected_k1=int(k1), expected_k2=int(k2),
        expected_k_total=int(base["k_literals"]["k_total"]))
    if str(spike_pin.get("program")) != str(SPIKE_PROGRAM_PIN):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(order_derivation_program_identity): program pin != frozen pin"
        )
    if str(spike_pin.get("formula_id")) != str(SPIKE_FORMULA_ID):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(order_derivation_program_identity): formula-id != frozen F-median8 pin"
        )
    set_delta = order_set_delta(
        np.asarray(order_pin["l2_order"]), np.asarray(spike_pin["l2_order"]),
        int(k2))
    if int(set_delta["size_delta_b_minus_a"]) != 0:
        raise L2MechanismProbe2mContractError(
            "BLOCKED(order_set_delta_recorded): B-A disclosed-size delta != 0"
        )
    if abs(float(base["d2_margin_bits"]) - float(FROZEN_D2_MARGIN_BITS)) > 1e-6:
        raise L2MechanismProbe2mContractError(
            "BLOCKED(alt_construction_budget_feasibility_replayed): "
            "D2 margin != frozen replay literal (DEV untouched, no Stage-B request)"
        )
    return {
        "prior_digest": str(base["prior_digest"]),
        "h1": float(base["h1"]),
        "h2": float(base["h2"]),
        "h_total": float(base["h_total"]),
        "counts_total": int(base["counts_total"]),
        "floor_hits": int(base["floor_hits"]),
        "k_literals": dict(base["k_literals"]),
        "alt_file_digest": str(base["alt_file_digest"]),
        "p1_equality_max_abs_diff": float(base["p1_equality_max_abs_diff"]),
        "alt_h_literals": dict(base["alt_h_literals"]),
        "order_digest_A": str(base["order_digest"]),
        "spike_order_digest_B": str(spike_pin["spike_order_digest"]),
        "spike_program": str(spike_pin["program"]),
        "spike_formula_id": str(spike_pin["formula_id"]),
        "set_delta": set_delta,
        "d1": dict(base["d1"]),
        "d2_feasible": True,
        "d2_margin_bits": float(base["d2_margin_bits"]),
        "dev_contact": 0,
        "verified": True,
    }


def verify_dev_source_identity_2m(dev_pairs=None) -> dict:
    """Gate (a): cross-file 2M source identity (FIRST, before any open)."""
    candidate = FROZEN_DEV_PAIRS_PATH if dev_pairs is None else str(dev_pairs)
    if candidate == REFUSED_1M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20S DEV source gate: 1M full-pool path refused "
            f"({REFUSED_1M_DEV_PAIRS_PATH!r}); the entire 1M pool is "
            "fail-closed against P20S DEV selection"
        )
    if candidate == REFUSED_1P5M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20S DEV source gate: 1.5M session path refused "
            f"({REFUSED_1P5M_DEV_PAIRS_PATH!r}); the entire 1.5M session is "
            "fail-closed against P20S DEV selection"
        )
    if candidate != FROZEN_DEV_PAIRS_PATH:
        raise ValueError(
            "frozen point requires dev-pairs="
            f"{FROZEN_DEV_PAIRS_PATH!r}, got {candidate!r}"
        )
    checks = {
        "source": FROZEN_SOURCE == "2M",
        "source_tag": FROZEN_SOURCE_TAG == SOURCE_IDS[FROZEN_SOURCE],
    }
    failing = sorted(name for name, ok in checks.items() if not ok)
    if failing:
        raise ValueError("P20S DEV source identity mismatch: " + ",".join(failing))
    return {
        "source": FROZEN_SOURCE,
        "source_tag": FROZEN_SOURCE_TAG,
        "dev_pairs_path": FROZEN_DEV_PAIRS_PATH,
        "dev_pairs_size_bytes": FROZEN_DEV_PAIRS_SIZE,
        "dev_pairs_sha256": FROZEN_DEV_PAIRS_SHA256,
        "build_manifest_path": FROZEN_DEV_BUILD_MANIFEST_PATH,
        "refused_1m_path": REFUSED_1M_DEV_PAIRS_PATH,
        "refused_1p5m_path": REFUSED_1P5M_DEV_PAIRS_PATH,
        "verified": True,
    }


def verify_merged_containment(dev_frames_val=None, dev_frames_hold=None,
                          remainder_frames=None) -> dict:
    """Gate (b): intra-file dual-segment merged containment.

    The VAL segment must lie wholly inside VAL 2187..2915 with zero
    TRAIN/VAL-DEV overlap AND the HOLD segment wholly inside HOLD
    2916..3644 with zero HOLD-DEV overlap, else refuse before any
    protected content open. Both segments must equal the frozen pair and
    sum to exactly one 128-frame block; the remainder must equal the
    frozen HOLD tail 3595..3644.
    """
    val_pair = (tuple(FROZEN_DEV_FRAMES_VAL) if dev_frames_val is None
                else tuple(opf._as_int(v, "dev-frames-val", minimum=0)
                           for v in dev_frames_val))
    hold_pair = (tuple(FROZEN_DEV_FRAMES_HOLD) if dev_frames_hold is None
                 else tuple(opf._as_int(v, "dev-frames-hold", minimum=0)
                            for v in dev_frames_hold))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    val_first, val_last = INTRA_FILE_VAL_FRAME_RANGE
    hold_first, hold_last = INTRA_FILE_HOLD_FRAME_RANGE
    train_first, train_last = CONSUMED_2M_TRAIN_FRAME_RANGE
    valdev_first, valdev_last = CONSUMED_2M_VAL_DEV_FRAME_RANGE
    holddev_first, holddev_last = CONSUMED_2M_HOLD_DEV_FRAME_RANGE
    dev_v_first, dev_v_last = val_pair
    dev_h_first, dev_h_last = hold_pair
    rem_first, rem_last = rem_pair
    if not (val_first <= dev_v_first and dev_v_last <= val_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): VAL segment {dev_v_first}..{dev_v_last} "
            f"lies outside 2M VAL {val_first}..{val_last}"
        )
    if not (dev_v_last < train_first or dev_v_first > train_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): VAL segment {dev_v_first}..{dev_v_last} "
            f"overlaps 2M TRAIN {train_first}..{train_last}"
        )
    if not (dev_v_last < valdev_first or dev_v_first > valdev_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): VAL segment {dev_v_first}..{dev_v_last} "
            f"overlaps consumed 2M VAL DEV {valdev_first}..{valdev_last}"
        )
    if not (hold_first <= dev_h_first and dev_h_last <= hold_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): HOLD segment {dev_h_first}..{dev_h_last} "
            f"lies outside 2M HOLD {hold_first}..{hold_last}"
        )
    if not (dev_h_last < holddev_first or dev_h_first > holddev_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): HOLD segment {dev_h_first}..{dev_h_last} "
            f"overlaps consumed 2M HOLD DEV {holddev_first}..{holddev_last}"
        )
    if val_pair != tuple(FROZEN_DEV_FRAMES_VAL):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): VAL segment {val_pair} != frozen "
            f"{tuple(FROZEN_DEV_FRAMES_VAL)} (VAL-remainder tail)"
        )
    if hold_pair != tuple(FROZEN_DEV_FRAMES_HOLD):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): HOLD segment {hold_pair} != frozen "
            f"{tuple(FROZEN_DEV_FRAMES_HOLD)} (HOLD-remainder head)"
        )
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): remainder {rem_pair} != frozen "
            f"{tuple(FROZEN_REMAINDER_FRAME_RANGE)}"
        )
    if (dev_v_last - dev_v_first + 1) + (dev_h_last - dev_h_first + 1) != FROZEN_DEV_FRAMES:
        raise ValueError(
            "BLOCKED(dev_block_range_identity): merged segments do not sum to "
            f"exactly one {FROZEN_DEV_FRAMES}-frame block"
        )
    if rem_first != dev_h_last + 1:
        raise ValueError(
            "BLOCKED(dev_block_range_identity): remainder does not start where "
            "the merged HOLD head ends"
        )
    return {
        "dev_frames_val": [int(dev_v_first), int(dev_v_last)],
        "dev_frames_hold": [int(dev_h_first), int(dev_h_last)],
        "remainder_frame_range": [int(rem_first), int(rem_last)],
        "block_segments": [list(s) for s in FROZEN_BLOCK_SEGMENTS],
        "intra_file_val_frame_range": [int(val_first), int(val_last)],
        "intra_file_hold_frame_range": [int(hold_first), int(hold_last)],
        "val_contained": True,
        "hold_contained": True,
        "train_exterior_disjoint": True,
        "val_dev_disjoint": True,
        "hold_dev_disjoint": True,
        "one_block_sums_128": True,
        "verified": True,
    }


def verify_merged_frame_set_identity(dev_frames_val=None, dev_frames_hold=None) -> dict:
    """Gate (g-part): exact 128-frame merged list rule (VAL-then-HOLD order)."""
    val_pair = (tuple(FROZEN_DEV_FRAMES_VAL) if dev_frames_val is None
                else tuple(opf._as_int(v, "dev-frames-val", minimum=0)
                           for v in dev_frames_val))
    hold_pair = (tuple(FROZEN_DEV_FRAMES_HOLD) if dev_frames_hold is None
                 else tuple(opf._as_int(v, "dev-frames-hold", minimum=0)
                            for v in dev_frames_hold))
    frames = (list(range(val_pair[0], val_pair[1] + 1))
              + list(range(hold_pair[0], hold_pair[1] + 1)))
    if frames != list(FROZEN_MERGED_FRAME_LIST):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): merged 128-frame list != frozen "
            "VAL-tail-then-HOLD-head rule (2827..2915 then 3556..3594)"
        )
    if len(frames) != FROZEN_DEV_FRAMES:
        raise ValueError(
            "BLOCKED(dev_block_range_identity): merged frame list length "
            f"{len(frames)} != {FROZEN_DEV_FRAMES}"
        )
    return {
        "merged_frame_list": [int(f) for f in frames],
        "merged_frames": len(frames),
        "val_tail_frames": int(val_pair[1] - val_pair[0] + 1),
        "hold_head_frames": int(hold_pair[1] - hold_pair[0] + 1),
        "verified": True,
    }


def verify_consumed_exclusions_merged(
        dev_frames_val=None, dev_frames_hold=None, remainder_frames=None) -> dict:
    """Gates (c)-(e): consumed-1M / consumed-1.5M / consumed-2M + S2-ii."""
    val_pair = (tuple(FROZEN_DEV_FRAMES_VAL) if dev_frames_val is None
                else tuple(opf._as_int(v, "dev-frames-val", minimum=0)
                           for v in dev_frames_val))
    hold_pair = (tuple(FROZEN_DEV_FRAMES_HOLD) if dev_frames_hold is None
                 else tuple(opf._as_int(v, "dev-frames-hold", minimum=0)
                            for v in dev_frames_hold))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    segments = [tuple(val_pair), tuple(hold_pair)]
    for label, (start, end) in (
            ("consumed 2M TRAIN 0..2186", CONSUMED_2M_TRAIN_FRAME_RANGE),
            ("consumed 2M VAL DEV 2187..2826", CONSUMED_2M_VAL_DEV_FRAME_RANGE),
            ("consumed 2M HOLD DEV 2916..3555", CONSUMED_2M_HOLD_DEV_FRAME_RANGE)):
        for r_start, r_end in segments:
            if not (r_end < start or r_start > end):
                raise ValueError(
                    f"BLOCKED(dev_block_range_identity): declared range "
                    f"{r_start}..{r_end} overlaps {label}"
                )
    if not (rem_pair[1] < CONSUMED_2M_HOLD_DEV_FRAME_RANGE[0]
            or rem_pair[0] > CONSUMED_2M_HOLD_DEV_FRAME_RANGE[1]):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): declared HOLD tail "
            f"{rem_pair[0]}..{rem_pair[1]} overlaps consumed 2M HOLD DEV"
        )
    build_first, build_last = FROZEN_BUILD_FRAME_RANGE
    if (build_first, build_last) != CONSUMED_2M_TRAIN_FRAME_RANGE:
        raise ValueError("build-frames declaration drifted from 2M TRAIN 0..2186")
    for r_start, r_end in segments:
        if not (build_last < r_start or r_end < build_first):
            raise ValueError("DEV/build-frames disjointness violated (S2-ii)")
    if FROZEN_SOURCE_TAG == CONSUMED_1M_SOURCE_TAG \
            or FROZEN_SOURCE_TAG == CONSUMED_1P5M_SOURCE_TAG:
        raise ValueError("DEV source tag collides with a consumed session (impossible)")
    return {
        "build_frames": [int(build_first), int(build_last)],
        "dev_frames_val": [int(val_pair[0]), int(val_pair[1])],
        "dev_frames_hold": [int(hold_pair[0]), int(hold_pair[1])],
        "remainder_frames": [int(rem_pair[0]), int(rem_pair[1])],
        "dev_source_tag": FROZEN_SOURCE_TAG,
        "consumed_1m_source_tag": CONSUMED_1M_SOURCE_TAG,
        "consumed_1p5m_source_tag": CONSUMED_1P5M_SOURCE_TAG,
        "consumed_1m_frames": list(CONSUMED_1M_FRAME_RANGE),
        "consumed_1p5m_train_frames": list(CONSUMED_1P5M_TRAIN_FRAME_RANGE),
        "consumed_1p5m_val_frames": list(CONSUMED_1P5M_VAL_FRAME_RANGE),
        "consumed_1p5m_hold_frames": list(CONSUMED_1P5M_HOLD_FRAME_RANGE),
        "consumed_2m_train_disjoint": True,
        "consumed_2m_val_dev_disjoint": True,
        "consumed_2m_hold_dev_disjoint": True,
        "consumed_1m_disjoint_by_identity": True,
        "consumed_1p5m_disjoint_by_identity": True,
        "hold_tail_never_decoded": True,
        "val_stub_1p5m_never_decoded": list(FROZEN_1P5M_VAL_STUB_FRAME_RANGE),
        "hold_remainder_1p5m_never_decoded": list(
            FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE),
        "disjoint": True,
        "verified": True,
    }


def form_merged_blocks(
    table,
    *,
    dev_frames_val=FROZEN_DEV_FRAMES_VAL,
    dev_frames_hold=FROZEN_DEV_FRAMES_HOLD,
    block_frames: int = FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
) -> dict:
    """Deterministic merged-2M development validation plus slicing.

    Selects the VAL-remainder tail and HOLD-remainder head segments from
    the 2M table, validates each segment (exact frames, pair_idx exactly
    0..255 per frame, sorted (frame_id, pair_idx) within the segment),
    concatenates VAL-segment-then-HOLD-segment into ONE 32768-pair block,
    and validates the declared HOLD tail remainder from the pool (counted,
    never decoded). The 1.5M stub/remainder populations are recorded from
    the frozen constants (counted, never contacted beyond counting).
    """
    try:
        val_pair = tuple(opf._as_int(v, "dev-frames-val", minimum=0)
                         for v in dev_frames_val)
    except TypeError as exc:
        raise TypeError(f"dev-frames-val must be a pair of integers: {exc}") from exc
    if val_pair != tuple(FROZEN_DEV_FRAMES_VAL):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"dev-frames-val {val_pair} != frozen {tuple(FROZEN_DEV_FRAMES_VAL)}"
        )
    try:
        hold_pair = tuple(opf._as_int(v, "dev-frames-hold", minimum=0)
                          for v in dev_frames_hold)
    except TypeError as exc:
        raise TypeError(f"dev-frames-hold must be a pair of integers: {exc}") from exc
    if hold_pair != tuple(FROZEN_DEV_FRAMES_HOLD):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"dev-frames-hold {hold_pair} != frozen {tuple(FROZEN_DEV_FRAMES_HOLD)}"
        )
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise L2MechanismProbe2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"block-frames {block_frames} != frozen {FROZEN_BLOCK_FRAMES}"
        )
    try:
        rem_pair = tuple(opf._as_int(v, "remainder-frames", minimum=0)
                         for v in remainder_frames)
    except TypeError as exc:
        raise TypeError(f"remainder-frames must be a pair of integers: {exc}") from exc
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"remainder-frames {rem_pair} != frozen {tuple(FROZEN_REMAINDER_FRAME_RANGE)}"
        )
    try:
        frame_id = np.asarray(table["frame_id"], dtype=np.int64)
        pair_idx = np.asarray(table["pair_idx"], dtype=np.int64)
        alice = np.asarray(table["alice_symbol"], dtype=np.int64)
        bob = np.asarray(table["bob_symbol"], dtype=np.int64)
    except (KeyError, TypeError, ValueError) as exc:
        raise L2MechanismProbe2mContractError(
            f"BLOCKED(dev_population_exact): loader frame is malformed: {exc}"
        ) from exc
    if not (frame_id.shape == pair_idx.shape == alice.shape == bob.shape) \
            or frame_id.ndim != 1:
        raise L2MechanismProbe2mContractError(
            "BLOCKED(dev_population_exact): column shapes disagree"
        )
    for name, values in (("alice_symbol", alice), ("bob_symbol", bob)):
        if values.size == 0 or values.min() < 0 or values.max() >= N_BOB:
            raise L2MechanismProbe2mContractError(
                f"BLOCKED(dev_population_exact): {name} outside 0..{N_BOB - 1}"
            )
    pool_frame_id = np.asarray(table["frame_id"], dtype=np.int64)
    seg_arrays = []
    for label, (seg_first, seg_last), seg_frames in (
            ("VAL tail", val_pair, FROZEN_DEV_VAL_FRAMES),
            ("HOLD head", hold_pair, FROZEN_DEV_HOLD_FRAMES)):
        selected = (frame_id >= seg_first) & (frame_id <= seg_last)
        rows = int(np.sum(selected))
        if rows == 0:
            raise L2MechanismProbe2mContractError(
                f"BLOCKED(dev_population_exact): no rows in the frozen {label} range"
            )
        seg_frame = frame_id[selected]
        seg_pair = pair_idx[selected]
        seg_alice = alice[selected]
        seg_bob = bob[selected]
        unique_frames = np.unique(seg_frame)
        if (unique_frames.size != seg_frames
                or int(unique_frames[0]) != seg_first
                or int(unique_frames[-1]) != seg_last):
            raise L2MechanismProbe2mContractError(
                f"BLOCKED(dev_population_exact): {label} frames "
                f"{unique_frames.size} with range {int(unique_frames[0])}.."
                f"{int(unique_frames[-1])} != frozen {seg_frames} with range "
                f"{seg_first}..{seg_last}"
            )
        if rows != seg_frames * FROZEN_PAIRS_PER_FRAME:
            raise L2MechanismProbe2mContractError(
                f"BLOCKED(dev_population_exact): {label} rows {rows} != frozen "
                f"{seg_frames * FROZEN_PAIRS_PER_FRAME}"
            )
        order = np.lexsort((seg_pair, seg_frame))
        seg_frame = seg_frame[order]
        seg_pair = seg_pair[order]
        seg_alice = seg_alice[order]
        seg_bob = seg_bob[order]
        expected_pair = np.tile(
            np.arange(FROZEN_PAIRS_PER_FRAME, dtype=np.int64), seg_frames
        )
        if not np.array_equal(seg_pair, expected_pair):
            raise L2MechanismProbe2mContractError(
                f"BLOCKED(dev_population_exact): {label} pair_idx is not exactly "
                "0..255 per frame"
            )
        seg_arrays.append((seg_frame, seg_alice, seg_bob))
    frame_cat = np.concatenate([seg_arrays[0][0], seg_arrays[1][0]])
    alice_cat = np.concatenate([seg_arrays[0][1], seg_arrays[1][1]])
    bob_cat = np.concatenate([seg_arrays[0][2], seg_arrays[1][2]])
    if int(frame_cat.size) != FROZEN_DEV_PAIRS:
        raise L2MechanismProbe2mContractError(
            f"BLOCKED(dev_population_exact): merged DEV rows {int(frame_cat.size)} "
            f"!= frozen {FROZEN_DEV_PAIRS}"
        )
    merged_list = ([int(f) for f in range(val_pair[0], val_pair[1] + 1)]
                   + [int(f) for f in range(hold_pair[0], hold_pair[1] + 1)])
    if merged_list != list(FROZEN_MERGED_FRAME_LIST):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(dev_block_range_identity): merged 128-frame list != frozen "
            "VAL-tail-then-HOLD-head rule"
        )
    rem_first, rem_last = rem_pair
    remainder_rows = (pool_frame_id >= rem_first) & (pool_frame_id <= rem_last)
    remainder_frame_ids = pool_frame_id[remainder_rows]
    if int(np.sum(remainder_rows)) != FROZEN_REMAINDER_SYMBOLS:
        raise L2MechanismProbe2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder rows "
            f"{int(np.sum(remainder_rows))} != frozen {FROZEN_REMAINDER_SYMBOLS}"
        )
    if (np.unique(remainder_frame_ids).size != FROZEN_REMAINDER_FRAMES
            or int(remainder_frame_ids.min()) != rem_first
            or int(remainder_frame_ids.max()) != rem_last):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder frames "
            f"!= frozen {rem_first}..{rem_last} ({FROZEN_REMAINDER_FRAMES} frames)"
        )
    check = verify_merged_containment(val_pair, hold_pair, rem_pair)
    if not check["verified"]:
        raise L2MechanismProbe2mContractError("BLOCKED(dev_block_range_identity)")
    check_frames = verify_merged_frame_set_identity(val_pair, hold_pair)
    if not check_frames["verified"]:
        raise L2MechanismProbe2mContractError("BLOCKED(dev_block_range_identity)")
    check2 = verify_consumed_exclusions_merged(val_pair, hold_pair, rem_pair)
    if not check2["verified"]:
        raise L2MechanismProbe2mContractError("BLOCKED(dev_block_range_identity)")
    block = {
        "block_index": 0,
        "segments": [list(val_pair), list(hold_pair)],
        "frame_start": int(val_pair[0]),
        "frame_end": int(hold_pair[1]),
        "frame_count": int(FROZEN_BLOCK_FRAMES),
        "val_frames": int(FROZEN_DEV_VAL_FRAMES),
        "hold_frames": int(FROZEN_DEV_HOLD_FRAMES),
        "merged_frame_list": merged_list,
        "labels": alice_cat.copy(),
        "bob": bob_cat.copy(),
        "high": (alice_cat // Q).astype(np.int64),
        "low": (alice_cat % Q).astype(np.int64),
    }
    if int(block["labels"].size) != FROZEN_SYMBOLS_PER_BLOCK:
        raise L2MechanismProbe2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): merged block holds "
            f"{int(block['labels'].size)} pairs != {FROZEN_SYMBOLS_PER_BLOCK}"
        )
    return {
        "dev_segments": [list(val_pair), list(hold_pair)],
        "dev_frames": int(FROZEN_DEV_FRAMES),
        "dev_pairs": int(frame_cat.size),
        "blocks": [block],
        "block_segments": [list(s) for s in FROZEN_BLOCK_SEGMENTS],
        "merged_frame_list": merged_list,
        "remainder": {
            "frame_start": int(rem_first),
            "frame_end": int(rem_last),
            "frames": FROZEN_REMAINDER_FRAMES,
            "symbols": int(np.sum(remainder_rows)),
            "used": False,
        },
        "counted_1p5m_never_decoded": {
            "val_stub_frames": list(FROZEN_1P5M_VAL_STUB_FRAME_RANGE),
            "val_stub_symbols": int(FROZEN_1P5M_VAL_STUB_SYMBOLS),
            "hold_remainder_frames": list(FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE),
            "hold_remainder_symbols": int(FROZEN_1P5M_HOLD_REMAINDER_SYMBOLS),
            "used": False,
        },
    }


def l2_mechanism_probe_2m_seed_bits(master: int, n: int, arm: str, block_index: int,
                                     *, bit_length: int | None = None) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P20S domain)."""
    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P20S seed domain: {arm!r}")
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
# caps/formulas as P20Q section 7, K2 pinned to the 2M point (6746)).
# ---------------------------------------------------------------------------

def _ir_hazard_diagnostics(*, view, p2_arm, l2_order, k2, first_error,
                           prefix_mean) -> dict:
    """P20S mandatory IR recorder: IR-1..IR-4 (P20Q-identical) + IR-5 UNCAPPED writer, post-decode, recording-only.

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
    - IR-5 UNCAPPED (d9) is NOT inline here: the full-block 32768
      series are written by ``_ir5_full_block_writer`` to binary ``.bin``
      files + the ``ir5full-v1`` manifest (never text-JSON float dumps);
      the record carries manifest REFERENCES only.
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
    if int(n) != int(IR5_FULL_N):
        raise ValueError(
            f"IR instrumentation requires the full block N={IR5_FULL_N}, got {int(n)}"
        )
    return out


def _ir5_full_block_arrays(*, view, p2_arm, l2_order, k2, low_hat, field) -> dict:
    """Full-block IR-5 arrays (recording-only, post-decode).

    ``hazards_f32``: true-cell ``-log2`` mass in natural block order under
    the record's own arm table (``u1_cond`` from the view, else the true
    high); ``inprefix_u8``: X-domain disclosed-prefix flags under the
    record's OWN order (frozen-A on A/O, spike on B); ``inu_u8``:
    U-domain mismatch flags (``u2_hat`` vs ``u2_true``; all-zero when no
    U-domain estimate exists, i.e. ``low_hat`` is None). All shapes
    (32768,). Truth enters for RECORDING ONLY and never flows back into
    any decoder input.
    """
    if int(k2) != int(FROZEN_K2):
        raise ValueError(
            "IR-5 instrumentation requires the gated prefix length "
            f"{FROZEN_K2}, got {int(k2)}"
        )
    bob = np.asarray(view["bob"], dtype=np.int64)
    high_true = np.asarray(view["high"], dtype=np.int64)
    low_true = np.asarray(view["low"], dtype=np.int64)
    n = int(bob.size)
    if int(n) != int(IR5_FULL_N):
        raise ValueError(
            f"IR-5 instrumentation requires the full block N={IR5_FULL_N}, got {int(n)}"
        )
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
    if hazards.shape != (n,) or not np.isfinite(np.asarray(hazards, dtype=np.float64)).all():
        raise ValueError("IR-5 full-block hazards must be finite length-32768")
    mask = np.zeros(n, dtype=bool)
    mask[prefix] = True
    u2_true = np.asarray(view["u2"], dtype=np.int64)
    if u2_true.shape != (n,):
        raise ValueError(f"view u2 must be length {n}, got {u2_true.shape}")
    if low_hat is None:
        inu = np.zeros(n, dtype=np.uint8)
    else:
        u2_hat = polar_transform(
            np.asarray(low_hat, dtype=np.int64), field=field, alpha=ALPHA)
        inu = (np.asarray(u2_hat, dtype=np.int64) != u2_true).astype(np.uint8)
    return {
        "hazards_f32": np.ascontiguousarray(
            np.asarray(hazards, dtype=IR5_HAZARD_DTYPE)),
        "inprefix_u8": np.ascontiguousarray(mask.astype(np.uint8)),
        "inu_u8": np.ascontiguousarray(inu),
    }


def _ir5_full_block_writer(*, out_dir, arm_name, block_index, arrays,
                           order_digest) -> dict:
    """Write the three IR-5 ``.bin`` files (fail-if-present) + record refs.

    Called post-decode (after tag scoring) from the successor's
    ``_operational_record`` / ``_control_record`` equivalents alongside
    the nine carried scalars and the IR-1..IR-4 recorder (the P20Q
    ``_ir_hazard_diagnostics`` code point is the carried-over callsite
    pattern). Binary ``.bin`` + JSON manifest ONLY — never text-JSON
    float dumps, never npz/npy/parquet. Per-record total is ~192 KiB
    (well under the ~400 KB budget).
    """
    try:
        prefix = IR5_ARMV_PREFIX[arm_name]
    except KeyError as exc:
        raise ValueError(f"unknown frozen arm for the IR-5 writer: {arm_name!r}") from exc
    hazards = np.ascontiguousarray(
        np.asarray(arrays["hazards_f32"], dtype=IR5_HAZARD_DTYPE))
    inprefix = np.ascontiguousarray(np.asarray(arrays["inprefix_u8"], dtype=np.uint8))
    inu = np.ascontiguousarray(np.asarray(arrays["inu_u8"], dtype=np.uint8))
    if hazards.shape != (IR5_FULL_N,) or hazards.dtype != np.dtype(IR5_HAZARD_DTYPE):
        raise ValueError("IR-5 hazards must be 32768 float32-LE")
    if inprefix.shape != (IR5_FULL_N,) or inu.shape != (IR5_FULL_N,):
        raise ValueError("IR-5 flag series must both be length 32768 uint8")
    payloads = (
        (f"{prefix}_hazard_bits_f32le.bin", hazards.tobytes()),
        (f"{prefix}_inprefix_u8.bin", inprefix.tobytes()),
        (f"{prefix}_inu_u8.bin", inu.tobytes()),
    )
    if len(payloads[0][1]) != IR5_HAZARD_BYTES:
        raise ValueError("IR-5 hazard payload must be exactly 131072 B")
    if len(payloads[1][1]) != IR5_FLAG_BYTES or len(payloads[2][1]) != IR5_FLAG_BYTES:
        raise ValueError("IR-5 flag payloads must each be exactly 32768 B")
    if sum(len(p[1]) for p in payloads) > IR5_PER_RECORD_BUDGET_BYTES:
        raise ValueError("IR-5 per-record payload exceeds the ~400 KB budget")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    digests = []
    for name, payload in payloads:
        p = out / name
        if p.exists():
            raise FileExistsError(f"refusing to overwrite existing IR-5 file: {p}")
        p.write_bytes(payload)
        digests.append(hashlib.sha256(payload).hexdigest())
    return {
        "ir5_hazard_bits_file": payloads[0][0],
        "ir5_hazard_bits_sha256": digests[0],
        "ir5_inprefix_file": payloads[1][0],
        "ir5_inprefix_sha256": digests[1],
        "ir5_inu_file": payloads[2][0],
        "ir5_inu_sha256": digests[2],
        "ir5_format_version": str(IR5_FORMAT_VERSION),
        "ir5_total_len": int(IR5_FULL_N),
        "ir5_order_digest": str(order_digest),
        "ir5_arm": str(arm_name),
        "ir5_block_index": int(block_index),
    }


def check_ir5_manifest_identity(out_root, manifest) -> dict:
    """``ir5_full_manifest_identity`` gate: nine ``.bin`` files byte-present.

    The ``ir5full-v1`` manifest must list exactly the nine frozen files
    with per-file sha256 + shape + dtype + endianness + order-identity +
    record linkage; every digest is recomputed from disk and must match,
    every file must respect the ~2 MB evidence-size rule.
    """
    if not isinstance(manifest, dict):
        raise ValueError("IR-5 manifest must be a JSON object")
    if str(manifest.get("format_version")) != str(IR5_FORMAT_VERSION):
        raise ValueError("IR-5 manifest format_version != ir5full-v1")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != 9:
        raise ValueError("IR-5 manifest must list exactly nine files")
    want_names = [n for n in OUTPUT_FILES if n.endswith(".bin")]
    got_names = [str(e.get("file")) for e in files]
    if sorted(got_names) != sorted(want_names):
        raise ValueError("IR-5 manifest file set != frozen nine .bin files")
    root = Path(out_root)
    total = 0
    for entry in files:
        name = str(entry.get("file"))
        if str(entry.get("format_version")) != str(IR5_FORMAT_VERSION):
            raise ValueError(f"IR-5 entry {name}: format_version != ir5full-v1")
        if "hazard" in name:
            shape, dtype, endian, nbytes = [IR5_FULL_N], IR5_HAZARD_DTYPE, "little", IR5_HAZARD_BYTES
        else:
            shape, dtype, endian, nbytes = [IR5_FULL_N], IR5_FLAG_DTYPE, "little", IR5_FLAG_BYTES
        if list(entry.get("shape", [])) != shape:
            raise ValueError(f"IR-5 entry {name}: shape != [32768]")
        if str(entry.get("dtype")) != str(dtype):
            raise ValueError(f"IR-5 entry {name}: dtype != {dtype}")
        if str(entry.get("endianness")) != str(endian):
            raise ValueError(f"IR-5 entry {name}: endianness != little")
        if str(entry.get("order_identity")) not in (
                str(FROZEN_ORDER_DIGEST_A), str(FROZEN_SPIKE_ORDER_DIGEST_B)):
            raise ValueError(f"IR-5 entry {name}: order_identity != frozen-A/spike digest")
        p = root / name
        if not p.is_file():
            raise FileNotFoundError(f"IR-5 file byte-absent: {p}")
        raw = p.read_bytes()
        total += len(raw)
        if len(raw) != int(entry.get("bytes", -1)) != nbytes:
            raise ValueError(f"IR-5 entry {name}: byte size mismatch")
        if hashlib.sha256(raw).hexdigest() != str(entry.get("sha256")):
            raise ValueError(f"IR-5 entry {name}: sha256 != manifest digest")
        if len(raw) > IR5_MAX_FILE_BYTES:
            raise ValueError(f"IR-5 entry {name}: exceeds the ~2 MB file rule")
    if total > IR5_ROOT_BUDGET_BYTES:
        raise ValueError("IR-5 nine-file total exceeds the ~1.5 MB root budget")
    return {"files": len(files), "bytes": total, "verified": True}


def ir_payload_complete(records) -> bool:
    """IR-1..IR-4 all PRESENT with frozen caps/nullability + IR-5 refs per record.

    Same caps/formulas/nullability as the accepted P20Q gate; the P20S
    difference is IR-5: records carry manifest REFERENCES (file names +
    digests + ``ir5full-v1`` + total length) instead of inline float
    arrays (file-byte presence + digest equality is enforced by the
    ``ir5_full_manifest_identity`` gate).
    """
    if not records:
        return False
    edges = _ir_hist_edges()
    for record in records:
        if str(record.get("outcome")) == "resource_abort":
            continue
        if any(field not in record for field in IR_FIELDS):
            return False
        rec_edges = record.get("ir1_hist_edges_bits")
        if rec_edges is None or len(rec_edges) != IR1_BINS + 1:
            return False
        if any(abs(a - b) > 1e-12 for a, b in zip(rec_edges, edges)):
            return False
        if len(record.get("ir1_hist_prefix_counts", [])) != IR1_BINS:
            return False
        if len(record.get("ir1_hist_outside_counts", [])) != IR1_BINS:
            return False
        if record.get("ir3_thresh_lo_bits") is None:
            return False
        if record.get("ir3_thresh_hi_bits") is None:
            return False
        if abs(float(record["ir3_thresh_hi_bits"])
               - 2.0 * float(record["ir3_thresh_lo_bits"])) > 1e-9:
            return False
        if len(record.get("ir4_topk_coords", [])) != IR4_TOPK:
            return False
        if len(record.get("ir4_topk_hazard_bits", [])) != IR4_TOPK:
            return False
        if len(record.get("ir4_topk_in_prefix", [])) != IR4_TOPK:
            return False
        if len(record.get("ir4_topk_ranks", [])) != IR4_TOPK:
            return False
        for key in ("ir5_hazard_bits_file", "ir5_hazard_bits_sha256",
                    "ir5_inprefix_file", "ir5_inprefix_sha256",
                    "ir5_inu_file", "ir5_inu_sha256"):
            if not record.get(key):
                return False
        if str(record.get("ir5_format_version")) != str(IR5_FORMAT_VERSION):
            return False
        if int(record.get("ir5_total_len", -1)) != int(IR5_FULL_N):
            return False
        if record.get("first_error_layer") == "L2":
            pct = record.get("ir2_first_error_hazard_rank_pct")
            if pct is None or not (0.0 <= float(pct) <= 1.0):
                return False
        else:
            if record.get("ir2_first_error_hazard_rank_pct") is not None:
                return False
    return True


def ir_payload_tables(records) -> dict:
    """Descriptive H2 decision quantities (never thresholds, never verdicts)."""
    completed = [r for r in records if str(r.get("outcome")) != "resource_abort"]
    ir2_all, ir2_a, ir2_b, ir2_oracle = [], [], [], []
    ir1_rows, ir3_rows, ir4_rows = [], [], []
    for record in completed:
        pct = record.get("ir2_first_error_hazard_rank_pct")
        arm = str(record.get("arm"))
        if pct is not None:
            pct = float(pct)
            ir2_all.append(pct)
            if arm == "A_anchor_frozen_order":
                ir2_a.append(pct)
            elif arm == "B_spike_local_order":
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
        "ir5_uncapped_full_block": True,
        "ir5_format_version": str(IR5_FORMAT_VERSION),
        "ir5_full_n": int(IR5_FULL_N),
        "records_completed": len(completed),
    }


def _arm_order_digest(arm_name: str) -> str:
    """Arm-specific L2 order digest (frozen-A on A/O, spike on B)."""
    if arm_name in ("A_anchor_frozen_order", "O_true_l1_oracle"):
        if FROZEN_ORDER_DIGEST_A is None:
            raise ValueError("Stage-A freeze not yet applied: frozen-A digest pin is None")
        return str(FROZEN_ORDER_DIGEST_A)
    if arm_name in ("B_spike_local_order",):
        if FROZEN_SPIKE_ORDER_DIGEST_B is None:
            raise ValueError("Stage-A freeze not yet applied: spike-B digest pin is None")
        return str(FROZEN_SPIKE_ORDER_DIGEST_B)
    raise ValueError(f"unknown frozen arm: {arm_name!r}")


def _nine_scalars_for_arm(*, arm_name, block, view, p2_arm, counts_arr,
                          l2_order, k2, first_error, field, low_hat) -> dict:
    """Accepted nine-scalar recorder with the arm-specific order digest.

    Calls the accepted 2M ``_l2_hazard_diagnostics`` read-only with the
    record's OWN order array (frozen-A on A/O, spike on B); only the
    recorded ``l2_order_digest`` label is arm-specific (the computation is
    byte-identical to the accepted recorder).
    """
    nine = _l2_hazard_diagnostics_2m(
        block=block, view=view, p2_arm=p2_arm, counts_arr=counts_arr,
        l2_order=l2_order, k2=int(k2), first_error=first_error,
        field=field, low_hat=low_hat)
    nine["l2_order_digest"] = _arm_order_digest(arm_name)
    return nine


def hazard_instrumentation_complete(records) -> bool:
    """All nine section 7 scalars present with frozen nullability per record.

    Same nullability semantics as the accepted gate; the order-digest rule
    is arm-specific (frozen-A digest on A/O records, spike digest on B
    records) with the gated prefix length 6746 on every completed record.
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


def mechanism_diagnostics(records) -> dict:
    """Descriptive per-arm outcome rows (geometry probe; never transition cells).

    Per-arm exact/outcome rows are recorded for completeness but explicitly
    NOT read as recovery rates. No A/B transition table is computed:
    counting vocabulary is out of scope for this packet by D2 form, and
    the A-vs-B factor lives in the byte-exact order set-delta plus the
    geometry/coverage quantities only.
    """
    rows: dict = {}
    for arm in FROZEN_ARM_NAMES:
        cell = [r for r in records if str(r.get("arm")) == arm]
        outcomes: dict = {}
        for record in cell:
            outcomes[str(record.get("outcome"))] = outcomes.get(
                str(record.get("outcome")), 0) + 1
        rows[arm] = {
            "arm": arm,
            "records": len(cell),
            "exact_count": sum(1 for r in cell if r.get("exact") is True),
            "outcomes": outcomes,
            "first_error_layers": sorted(
                {str(r.get("first_error_layer")) for r in cell}),
        }
    return {
        "arms": rows,
        "transition_tables": None,
        "transition_cells_computed": False,
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
        "mechanism": mechanism_diagnostics(records),
        "arms": arm_table,
        "undetected_count": sum(1 for r in records if r.get("outcome") == "undetected"),
        "nonfinite_count": sum(1 for r in records if r.get("nonfinite") is True),
    }


def oracle_isolation_ok(records, *, final: bool) -> bool:
    """O carries ORACLE provenance, deployable=false, never operational."""
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
                        field, diag=None, error=None, ir5_dir) -> dict:
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
    # IR-5 UNCAPPED full-block writer (d9): recording-only, post-decode.
    # Truth enters for RECORDING ONLY and never flows back into any
    # decoder input; the record carries manifest REFERENCES only.
    ir5_arrays = _ir5_full_block_arrays(
        view=view_arm, p2_arm=p2, l2_order=l2_order, k2=FROZEN_K2,
        low_hat=result.low_hat, field=field)
    record.update(_ir5_full_block_writer(
        out_dir=ir5_dir, arm_name=spec.name,
        block_index=int(block["block_index"]), arrays=ir5_arrays,
        order_digest=order_digest))
    return record


def _control_record(result, *, spec, arm_index, block, scoring, resources,
                    k_total, budget_literal, prior_digest, alt_digest,
                    order_digest, counts_arr, p1, p2, l2_order, n, view,
                    field, diag=None, error=None, ir5_dir) -> dict:
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
    # IR-5 UNCAPPED full-block writer (d9): recording-only, post-decode.
    # Truth enters for RECORDING ONLY and never flows back into any
    # decoder input; the record carries manifest REFERENCES only.
    ir5_arrays = _ir5_full_block_arrays(
        view=view_arm, p2_arm=p2, l2_order=l2_order, k2=FROZEN_K2,
        low_hat=result.low_hat, field=field)
    record.update(_ir5_full_block_writer(
        out_dir=ir5_dir, arm_name=spec.name,
        block_index=int(block["block_index"]), arrays=ir5_arrays,
        order_digest=order_digest))
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
                     spike_order_pin_B, set_delta, formation, records, events,
                     calls, incremental, accounting, provenance_violations,
                     cap, wall_s, resource_stop, session_prior_verified,
                     alt_verified, hazard_pin, prior_stat_before,
                     prior_stat_after, alt_stat_before, alt_stat_after,
                     dev_stat_before, dev_stat_after, registered_paths,
                     opened_paths, ir5_manifest, out_root,
                     final: bool) -> dict:
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
    gates["spike_order_identity_B"] = bool(
        spike_order_pin_B is not None and bool(spike_order_pin_B.get("verified"))
        and str(spike_order_pin_B.get("spike_order_digest"))
        == str(FROZEN_SPIKE_ORDER_DIGEST_B))
    gates["order_derivation_program_identity"] = bool(
        spike_order_pin_B is not None
        and str(spike_order_pin_B.get("program")) == str(SPIKE_PROGRAM_PIN)
        and str(spike_order_pin_B.get("formula_id")) == str(SPIKE_FORMULA_ID))
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
            and [list(s) for s in formation["dev_segments"]]
            == [list(s) for s in FROZEN_BLOCK_SEGMENTS]
            and list(formation["merged_frame_list"]) == list(FROZEN_MERGED_FRAME_LIST)
        )
    except (KeyError, TypeError, ValueError):
        population_ok = False
    gates["dev_population_exact"] = bool(population_ok)
    try:
        counted = formation["counted_1p5m_never_decoded"]
        blocks_ok = (
            [list(s) for s in formation["block_segments"]]
            == [list(s) for s in FROZEN_BLOCK_SEGMENTS]
            and len(formation["blocks"]) == FROZEN_BLOCK_COUNT
            and formation["remainder"]["used"] is False
            and int(formation["remainder"]["frames"]) == FROZEN_REMAINDER_FRAMES
            and int(formation["remainder"]["symbols"]) == FROZEN_REMAINDER_SYMBOLS
            and int(formation["remainder"]["frame_start"]) == int(FROZEN_REMAINDER_FRAME_RANGE[0])
            and counted["used"] is False
            and list(counted["val_stub_frames"]) == list(FROZEN_1P5M_VAL_STUB_FRAME_RANGE)
            and list(counted["hold_remainder_frames"])
            == list(FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE)
        )
    except (KeyError, TypeError, ValueError):
        blocks_ok = False
    gates["blocks_exact_with_declared_remainder"] = bool(blocks_ok)
    gates["three_records_exact"] = (
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
        spike_l2 = l2_prefix_positions(spike_order_pin_B["l2_order"], int(k2))
        orders_ok = (
            shared_l1.shape == (int(k1),)
            and frozen_l2.shape == (int(k2),)
            and spike_l2.shape == (int(k2),)
            and int(arms[0].k1) == int(k1) and int(arms[0].k2) == int(k2)
            and int(arms[1].k1) == int(k1) and int(arms[1].k2) == int(k2)
            and int(arms[2].k1) == 0 and int(arms[2].k2) == int(k2)
            and len(arms) == 3
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
    try:
        gates["ir5_full_manifest_identity"] = bool(
            check_ir5_manifest_identity(out_root, ir5_manifest)["verified"])
    except (ValueError, FileNotFoundError, OSError, TypeError):
        gates["ir5_full_manifest_identity"] = False
    try:
        oversized = [str(p) for p in Path(out_root).rglob("*")
                     if p.is_file() and p.stat().st_size > IR5_MAX_FILE_BYTES]
        gates["evidence_size_rule_met"] = bool(not oversized)
    except OSError:
        gates["evidence_size_rule_met"] = False
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


def l2_mechanism_probe_2m_label(gates: dict) -> str:
    """Descriptive COMPLETE iff every integrity gate holds, else BLOCKED(first)."""
    failing = [g for g in INTEGRITY_GATE_ORDER if not gates.get(g, False)]
    if not failing:
        return COMPLETE_LABEL
    return f"BLOCKED({failing[0]})"


@dataclass(frozen=True, eq=False)
class L2MechanismProbe2mRun:
    """In-memory P20S Stage-B run (also returned by the runner)."""

    summary: dict
    records: tuple
    gates: dict


# ---------------------------------------------------------------------------
# Stage-B orchestration.
# ---------------------------------------------------------------------------

def _write_frozen_plan(out_path: Path, *, source, floor, n, k1, k2, k_total,
                       budget_literal, construction, construction_digest,
                       prior_path, prior_digest, alt_path, alt_digest,
                       dev_pairs, manifest_path, dev_frames_val, dev_frames_hold,
                       block_frames, remainder_frames, tag_master, chunk_rows,
                       tag_bits, order_file, order_digest, spike_order_file,
                       spike_order_digest, spike_formula, identity, manifest,
                       dev_source_pin, dev_pin, disjoint_pin, frame_set_pin,
                       order_pin_A, spike_order_pin_B, set_delta) -> dict:
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
        "dev_frames_val": [int(dev_frames_val[0]), int(dev_frames_val[1])],
        "dev_frames_hold": [int(dev_frames_hold[0]), int(dev_frames_hold[1])],
        "merged_frame_list": [int(f) for f in FROZEN_MERGED_FRAME_LIST],
        "block_segments": [list(s) for s in FROZEN_BLOCK_SEGMENTS],
        "block_frames": int(block_frames),
        "remainder_frames": [int(remainder_frames[0]), int(remainder_frames[1])],
        "build_frames": [int(FROZEN_BUILD_FRAME_RANGE[0]),
                         int(FROZEN_BUILD_FRAME_RANGE[1])],
        "dev_source": dict(dev_source_pin),
        "dev_block_pin": dict(dev_pin),
        "build_dev_disjointness_s2_ii": dict(disjoint_pin),
        "merged_frame_set_identity": dict(frame_set_pin),
        "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
        "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
        "consumed_2m_train_frame_range": list(CONSUMED_2M_TRAIN_FRAME_RANGE),
        "consumed_2m_val_dev_frame_range": list(CONSUMED_2M_VAL_DEV_FRAME_RANGE),
        "consumed_2m_hold_dev_frame_range": list(CONSUMED_2M_HOLD_DEV_FRAME_RANGE),
        "hold_tail_counted_never_decoded": {
            "frames": list(FROZEN_REMAINDER_FRAME_RANGE),
            "frame_count": int(FROZEN_REMAINDER_FRAMES),
            "symbols": int(FROZEN_REMAINDER_SYMBOLS),
            "used": False,
        },
        "stub_1p5m_counted_never_decoded": {
            "frames": list(FROZEN_1P5M_VAL_STUB_FRAME_RANGE),
            "frame_count": int(FROZEN_1P5M_VAL_STUB_FRAMES),
            "symbols": int(FROZEN_1P5M_VAL_STUB_SYMBOLS),
            "used": False,
        },
        "hold_remainder_1p5m_counted_never_decoded": {
            "frames": list(FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE),
            "frame_count": int(FROZEN_1P5M_HOLD_REMAINDER_FRAMES),
            "symbols": int(FROZEN_1P5M_HOLD_REMAINDER_SYMBOLS),
            "used": False,
        },
        "consumed_sessions": {
            "1m_pool": {"source_tag": CONSUMED_1M_SOURCE_TAG,
                        "frames": list(CONSUMED_1M_FRAME_RANGE)},
            "1p5m_train": {"source_tag": CONSUMED_1P5M_SOURCE_TAG,
                           "frames": list(CONSUMED_1P5M_TRAIN_FRAME_RANGE)},
            "1p5m_val": {"source_tag": CONSUMED_1P5M_SOURCE_TAG,
                         "frames": list(CONSUMED_1P5M_VAL_FRAME_RANGE)},
            "1p5m_hold": {"source_tag": CONSUMED_1P5M_SOURCE_TAG,
                          "frames": list(CONSUMED_1P5M_HOLD_FRAME_RANGE)},
            "2m_train_build": {"source_tag": FROZEN_SOURCE_TAG,
                               "frames": list(CONSUMED_2M_TRAIN_FRAME_RANGE)},
            "2m_val_dev": {"source_tag": FROZEN_SOURCE_TAG,
                           "frames": list(CONSUMED_2M_VAL_DEV_FRAME_RANGE)},
            "2m_hold_dev": {"source_tag": FROZEN_SOURCE_TAG,
                            "frames": list(CONSUMED_2M_HOLD_DEV_FRAME_RANGE)},
        },
        "tag_master": int(tag_master),
        "tag_seed_domain": f"{SEED_PREFIX}:<master>:<n>:<arm>:<block_index>",
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "order_file_A": str(order_file),
        "order_digest_A": str(order_digest),
        "spike_order_file_B": str(spike_order_file),
        "spike_order_digest_B": str(spike_order_digest),
        "spike_formula_id": str(spike_formula),
        "spike_program": str(SPIKE_PROGRAM_PIN),
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
        "arm_order_digest_rule": "frozen-A on A/O, spike on B",
        "ir_fields": list(IR_FIELDS),
        "ir3_threshold_multipliers": [IR3_LO_MULT, IR3_HI_MULT],
        "ir1_bins": int(IR1_BINS),
        "ir4_topk": int(IR4_TOPK),
        "ir5_mode": "UNCAPPED_FULL_BLOCK_32768_BINARY_LE_BIN_PLUS_MANIFEST",
        "ir5_format_version": str(IR5_FORMAT_VERSION),
        "ir5_encoding": "f32le hazard + u8 inprefix + u8 inu per record",
        "ir5_per_record_budget_bytes": int(IR5_PER_RECORD_BUDGET_BYTES),
        "ir5_root_budget_bytes": int(IR5_ROOT_BUDGET_BYTES),
        "ir5_max_file_bytes": int(IR5_MAX_FILE_BYTES),
        "frozen_command": FROZEN_COMMAND,
        "frozen_plan_manifest": manifest,
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
    }
    opf._write_json(out_path / "frozen_plan.json", plan)
    return plan


def _render_report(summary: dict) -> str:
    mechanism = summary.get("aggregates", {}).get("mechanism", {})
    ir_payload = summary.get("aggregates", {}).get("ir_payload", {})
    set_delta = summary.get("order_set_delta", {})
    arms_rows = mechanism.get("arms", {}) if isinstance(mechanism, dict) else {}
    lines = [
        "# NB-Polar Phase 4-P20S maximum-information mechanism probe on the "
        "merged final 2M block with uncapped full-block IR-5",
        "",
        f"- protocol: `{summary.get('analysis')}` (mode `{summary.get('mode')}`)",
        f"- source: `{summary.get('source')}`; N={summary.get('n')}; "
        f"K1={summary.get('k1')} K2={summary.get('k2')} K_total={summary.get('k_total')} "
        "(2M-session-derived, S2-i literal replay)",
        "- alt-L2 construction: unit-pseudocount conditional alpha1 on all "
        "arms; alt-table digest "
        f"`{summary.get('alt_digest')}`",
        f"- frozen-A order digest: `{summary.get('order_digest_A')}` "
        f"(first-{summary.get('k1')} / first-{summary.get('k2')} prefixes on A/O); "
        f"spike-B order digest: `{summary.get('spike_order_digest_B')}` "
        f"(first-{summary.get('k2')} prefix on B; formula "
        f"`{summary.get('spike_formula_id')}`); set-delta "
        f"|A-B|={set_delta.get('a_minus_b_count')} "
        f"|B-A|={set_delta.get('b_minus_a_count')} "
        f"(size-delta {set_delta.get('size_delta_b_minus_a')})",
        f"- merged block segments: {summary.get('block_segments')} "
        f"(remainder {summary.get('remainder_frames')} never used; HOLD tail + "
        "1.5M stub/remainder counted never decoded)",
        f"- outcome: `{summary.get('outcome_label')}`; "
        f"records {summary.get('records_completed')}/{summary.get('planned_records')}",
        f"- operational exact (recorded, NOT a recovery rate): "
        f"{summary.get('aggregates', {}).get('operational', {}).get('exact_count')}; "
        f"per-arm rows {arms_rows}",
        f"- oracle exact (diagnostic only, never operational): "
        f"{summary.get('aggregates', {}).get('oracle', {}).get('exact_count')}",
        f"- undetected: {summary.get('aggregates', {}).get('undetected_count')}; "
        f"nonfinite: {summary.get('aggregates', {}).get('nonfinite_count')}",
        f"- IR payload: rank-pct (all) {ir_payload.get('ir2_rank_pct_all')}; "
        f"IR-5 uncapped={ir_payload.get('ir5_uncapped_full_block')} "
        f"({ir_payload.get('ir5_format_version')})",
        f"- SC calls: {summary.get('sc_calls')}/{summary.get('planned_sc_calls')} "
        f"(Stage-B sampling {summary.get('stage_b_sampling_calls')}); tags: "
        f"{summary.get('tag_invocations')}/{summary.get('planned_tag_invocations')}",
        f"- key bits: {summary.get('key_dependent_bits')}; "
        f"public bits: {summary.get('public_control_bits')}; "
        f"recount mismatch: {summary.get('recount_mismatch')}",
        f"- integrity: {'ALL PASS' if summary.get('integrity_all_pass') else 'BLOCKED'} "
        f"{summary.get('failing_integrity_gates')}",
        "",
        "O is an oracle-labelled diagnostic control, never an operational "
        "protocol or deployable result. The CE-normalized disclosure ratio is "
        "not qualification efficiency; undetected is never success. This is a "
        "descriptive merged-block mechanism probe of one local-spike "
        "L2-order position rule under the frozen alpha1 construction at "
        "frozen disclosure with full-block hazard geometry recorded: no "
        "recovery / FER / superiority / qualification / promotion / "
        "reliability claim is made, and the H2 decision stays main-thread "
        "analysis after acceptance.",
        "",
    ]
    return "\n".join(lines)


def run_l2_mechanism_probe_2m(
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
    dev_frames_val=FROZEN_DEV_FRAMES_VAL,
    dev_frames_hold=FROZEN_DEV_FRAMES_HOLD,
    block_frames: int = FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
    tag_master=FROZEN_TAG_MASTER,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    tag_bits: int = FROZEN_TAG_BITS,
    order_file=FROZEN_ORDER_FILE_PATH,
    order_digest=None,
    spike_order_file=FROZEN_SPIKE_ORDER_PATH,
    spike_order_digest=None,
    spike_formula=None,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
) -> L2MechanismProbe2mRun:
    """Execute the frozen P20S three-arm mechanism-probe run once; write fifteen files.

    ``prior`` / ``alt_prior`` / ``dev_table`` are documented injected test
    seams; the frozen CLI passes only the frozen point, loads the Stage-A
    frozen 2M raw prior and alt table read-only exactly once each, loads
    the frozen-A 2M order file and the Stage-A spike-B order file read-only
    behind their digest gates, and reads the merged 2M DEV parquet through
    its accepted loader exactly once. The V25 counts NPZ is never
    opened at any stage. The construction/order swap is hardcoded (never
    CLI-tunable): A runs the alt L2 at the Stage-A (K1,K2) on the frozen-A
    order prefixes, B the SAME alt L2 at the SAME point on the new-B order
    prefix, and O the frozen-order true-L1 oracle (D-continuity) at
    carried K2. Stage B performs ZERO sampling (no seed flag, no sampler
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
    dev_frames_val = _check_dev_frames_val(dev_frames_val)
    dev_frames_hold = _check_dev_frames_hold(dev_frames_hold)
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
    if spike_order_digest is None:
        raise ValueError("frozen point requires --spike-order-digest equal to the Stage-A pin")
    spike_order_digest = _check_spike_order_digest_B(spike_order_digest)
    if spike_formula is None:
        raise ValueError("frozen point requires --spike-formula equal to the Stage-A formula-id")
    spike_formula = _check_spike_formula(spike_formula)
    if alt_digest is None:
        raise ValueError("frozen point requires --alt-digest equal to the Stage-A pin")
    alt_digest = _check_alt_digest(alt_digest)
    arms = frozen_arm_table() if check_frozen_arm_table() else ()

    # Gate family (a)->(g) in the frozen order before any protected content
    # open: predecessor construction identity, cross-file source identity
    # (a), intra-file dual-segment merged-containment (b), consumed-1M /
    # consumed-1.5M / consumed-2M + S2-ii (c)-(e), then reuse-prior +
    # reuse-alt + frozen-A-order + spike-B-order + derivation-program +
    # K-literal + order-position-identity pins (f)-(g).
    if str(construction_digest) != str(FROZEN_CONSTRUCTION_DIGEST):
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = _gate_call("predecessor_construction_identity",
                          verify_predecessor_construction, construction,
                          expected_digest=construction_digest)
    identity = verified["record"]
    dev_source_pin = _gate_call("dev_block_range_identity",
                                verify_dev_source_identity_2m, dev_pairs)
    dev_pin = verify_merged_containment(dev_frames_val, dev_frames_hold, remainder_frames)
    disjoint_pin = verify_consumed_exclusions_merged(
        dev_frames_val, dev_frames_hold, remainder_frames)
    frame_set_pin = _gate_call("dev_block_range_identity",
                               verify_merged_frame_set_identity,
                               dev_frames_val, dev_frames_hold)
    manifest = _gate_call("dev_split_manifest_identity", verify_dev_manifest_2m,
                          manifest_path, source=source)
    order_pin_A = _gate_call(
        "frozen_order_identity_A", verify_stage_b_order_file_2m, order_file,
        expected_digest=order_digest,
        expected_prior_digest=str(FROZEN_SESSION_PRIOR_DIGEST),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    spike_order_pin_B = _gate_call(
        "spike_order_identity_B", verify_spike_order_file, spike_order_file,
        expected_digest=spike_order_digest,
        expected_prior_digest=str(FROZEN_SESSION_PRIOR_DIGEST),
        frozen_l1_order=np.asarray(order_pin_A["l1_order"]),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    if str(spike_order_pin_B.get("program")) != str(SPIKE_PROGRAM_PIN):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(order_derivation_program_identity): program pin drifted")
    if str(spike_order_pin_B.get("formula_id")) != str(SPIKE_FORMULA_ID):
        raise L2MechanismProbe2mContractError(
            "BLOCKED(order_derivation_program_identity): formula-id drifted")
    set_delta = order_set_delta(
        np.asarray(order_pin_A["l2_order"]),
        np.asarray(spike_order_pin_B["l2_order"]), int(k2))
    if int(set_delta["size_delta_b_minus_a"]) != 0:
        raise L2MechanismProbe2mContractError(
            "BLOCKED(order_set_delta_recorded): B-A disclosed-size delta != 0")
    # Order-position identity (g): the construction quadruple + tag
    # domain + source vocabulary must match the P20S freeze.
    order_identity = {
        "construction_quadruple": (PROTOCOL_NAME, MODE, FROZEN_SOURCE, SEED_PREFIX),
        "tag_master": int(tag_master),
        "order_digest_A": str(order_digest),
        "spike_order_digest_B": str(spike_order_digest),
        "spike_formula_id": str(spike_formula),
        "k1": int(k1),
        "k2": int(k2),
    }
    if order_identity["construction_quadruple"] != (
            "nbpolar-p20s-mechanism-probe-2m", "merged-mechanism-probe-2m",
            "2M", "nbpolar-p20s-mechanism-probe-2m-seed"):
        raise L2MechanismProbe2mContractError(
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
        raise ValueError("reopen refused: the single merged-2M parquet content open was consumed")

    # Input existence and stat-only metadata come before any content load/open.
    real_prior = prior is None
    real_alt = alt_prior is None
    real_dev = dev_table is None
    if real_prior:
        prior_file = Path(prior_path)
        if not prior_file.is_file():
            raise FileNotFoundError(f"Stage-A 2M raw prior not found: {prior_file}")
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
            raise FileNotFoundError(f"merged 2M pairs parquet not found: {dev_path_obj}")
        dev_stat_before = _stat_record(dev_path_obj)
        if dev_stat_before["size_bytes"] != FROZEN_DEV_PAIRS_SIZE:
            raise ValueError(
                "merged 2M pairs size mismatch before content open: "
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
        dev_pairs=dev_pairs, manifest_path=manifest_path,
        dev_frames_val=dev_frames_val, dev_frames_hold=dev_frames_hold,
        block_frames=block_frames, remainder_frames=remainder_frames,
        tag_master=tag_master, chunk_rows=chunk_rows, tag_bits=tag_bits,
        order_file=order_file, order_digest=order_digest,
        spike_order_file=spike_order_file, spike_order_digest=spike_order_digest,
        spike_formula=spike_formula,
        identity=identity, manifest=manifest, dev_source_pin=dev_source_pin,
        dev_pin=dev_pin, disjoint_pin=disjoint_pin, frame_set_pin=frame_set_pin,
        order_pin_A=order_pin_A,
        spike_order_pin_B=spike_order_pin_B, set_delta=set_delta)
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
        session_prior_verified = verify_session_prior_2m(
            raw_arrays, expected_digest=prior_digest,
            expected_h1=float(FROZEN_H1), expected_h2=float(FROZEN_H2),
            expected_total=float(FROZEN_H_TOTAL))
        p1_inc = session_prior_verified["p1"]
        p2_inc = session_prior_verified["p2"]
        counts_inc = session_prior_verified["counts"]

        # ---- input 2: the single alt-table load + reuse_alt_identity gate.
        if real_alt:
            alt_verified = _gate_call(
                "reuse_alt_identity", verify_alt_l2_identity_2m, alt_prior_path,
                expected_digest=alt_digest, incumbent_arrays=raw_arrays)
            _ALT_CONTENT_LOADED = True
            accounting["alt_content_loads"] = 1
            opened_paths.append(str(Path(alt_prior_path).resolve()))
        else:
            alt_verified = verify_alt_l2_arrays_2m(
                dict(alt_prior), incumbent_arrays=raw_arrays)
        p1_alt = alt_verified["p1"]
        p2_alt = alt_verified["p2_alt"]
        counts_alt = alt_verified["counts_ab"]
        # The alt-table floor-hit rate is a Stage-A frozen literal.
        hazard_pin = {
            "k_literal": True,
            "budget_literal": k_literals["budget_literal"],
            "alt_floor_rate": p20o.FROZEN_ALT_FLOOR_HIT_RATE,
        }

        # ---- S2: the K-literal display + alt-H descriptive literals.
        budget_literal = k_literals["budget_literal"]
        alt_h_literals = {
            "h1_inc": float(alt_verified["h1_inc"]),
            "h2_alt": float(alt_verified["h2_alt"]),
            "h_total_alt": float(alt_verified["h_total_alt"]),
        }

        # ---- input 3: the single merged-2M parquet content open, DEV rows only.
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
        formation = form_merged_blocks(
            table, dev_frames_val=dev_frames_val, dev_frames_hold=dev_frames_hold,
            block_frames=block_frames, remainder_frames=remainder_frames,
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
            "A_anchor_frozen_order": np.asarray(
                order_pin_A["l2_order"], dtype=np.int64),
            "B_spike_local_order": np.asarray(
                spike_order_pin_B["l2_order"], dtype=np.int64),
            "O_true_l1_oracle": np.asarray(
                order_pin_A["l2_order"], dtype=np.int64),
        }
        digest_by_arm = {
            "A_anchor_frozen_order": str(order_pin_A.get("order_digest")),
            "B_spike_local_order": str(spike_order_pin_B.get("spike_order_digest")),
            "O_true_l1_oracle": str(order_pin_A.get("order_digest")),
        }

        ir5_box: dict = {"manifest": None}

        def current_gates(*, final: bool, wall_now: float) -> tuple:
            gates = _integrity_gates(
                n=n, k1=k1, k2=k2, k_total=k_total, arms=arms, identity=identity,
                manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
                disjoint_pin=disjoint_pin, order_pin_A=order_pin_A,
                spike_order_pin_B=spike_order_pin_B, set_delta=set_delta,
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
                ir5_manifest=ir5_box["manifest"], out_root=out_path,
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
                "spike_order_digest_B": str(spike_order_pin_B.get("spike_order_digest")),
                "spike_program": str(SPIKE_PROGRAM_PIN),
                "spike_formula_id": str(SPIKE_FORMULA_ID),
                "order_set_delta": {
                    key: (list(value) if isinstance(value, list) else value)
                    for key, value in dict(set_delta).items()
                },
                "alt_h_literals": alt_h_literals,
                "block_segments": [list(s) for s in FROZEN_BLOCK_SEGMENTS],
                "merged_frame_list": [int(f) for f in FROZEN_MERGED_FRAME_LIST],
                "remainder_frames": list(FROZEN_REMAINDER_FRAME_RANGE),
                "hold_tail_counted_never_decoded": {
                    "frames": list(FROZEN_REMAINDER_FRAME_RANGE),
                    "frame_count": int(FROZEN_REMAINDER_FRAMES),
                    "symbols": int(FROZEN_REMAINDER_SYMBOLS),
                    "used": False,
                },
                "stub_1p5m_counted_never_decoded": list(
                    FROZEN_1P5M_VAL_STUB_FRAME_RANGE),
                "hold_remainder_1p5m_counted_never_decoded": list(
                    FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE),
                "dev_source": dict(dev_source_pin),
                "build_dev_disjointness_s2_ii": dict(disjoint_pin),
                "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
                "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
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
                    "descriptive merged-block maximum-information mechanism "
                    "probe of one local-spike L2-order position rule under "
                    "the frozen alpha1 construction at the per-session "
                    "(2M-TRAIN-derived) disclosure point (N=32768, one "
                    "merged block VAL 2827..2915 + HOLD 3556..3594) with the "
                    "mandatory IR-1..IR-4 payload plus uncapped full-block "
                    "IR-5 series under each order; O is an oracle-labelled "
                    "diagnostic control, never an operational protocol or "
                    "deployable result; not real-frame FER, reconciliation "
                    "efficiency, leakage, key rate, scaling superiority, "
                    "qualification or promotion evidence; the CE-normalized "
                    "disclosure ratio is not qualification efficiency; "
                    "undetected is never success; per-record outcomes are "
                    "recorded but explicitly NOT read as recovery rates; no "
                    "reliability or recovery claim is licensed; the H2 "
                    "decision is main-thread analysis after acceptance, not "
                    "a block result; merged DEV is consumed by this packet "
                    "regardless of outcome"
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
            seed = l2_mechanism_probe_2m_seed_bits(
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
                # the L2 order: A runs the frozen-A prefix, B the spike-B
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
                    error=error, ir5_dir=out_path)
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
                    error=error, ir5_dir=out_path)

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
        # ---- IR-5 manifest: nine .bin files already written per record;
        # link them with digests + order identity + record linkage.
        ir5_entries = []
        for record in records:
            if str(record.get("outcome")) == "resource_abort":
                continue
            arm_prefix = IR5_ARMV_PREFIX[str(record.get("arm"))]
            for suffix, sha_key, nbytes, dtype in (
                    ("hazard_bits_f32le.bin", "ir5_hazard_bits_sha256",
                     IR5_HAZARD_BYTES, IR5_HAZARD_DTYPE),
                    ("inprefix_u8.bin", "ir5_inprefix_sha256",
                     IR5_FLAG_BYTES, IR5_FLAG_DTYPE),
                    ("inu_u8.bin", "ir5_inu_sha256",
                     IR5_FLAG_BYTES, IR5_FLAG_DTYPE)):
                ir5_entries.append({
                    "file": f"{arm_prefix}_{suffix}",
                    "sha256": str(record[sha_key]),
                    "shape": [int(IR5_FULL_N)],
                    "dtype": str(dtype),
                    "endianness": "little",
                    "order_identity": str(record.get("l2_order_digest")),
                    "arm": str(record.get("arm")),
                    "block_index": int(record.get("block_index")),
                    "bytes": int(nbytes),
                    "format_version": str(IR5_FORMAT_VERSION),
                })
        ir5_manifest_doc = {
            "format_version": str(IR5_FORMAT_VERSION),
            "files": ir5_entries,
        }
        opf._write_json(out_path / "ir5_full_manifest.json", ir5_manifest_doc)
        ir5_box["manifest"] = ir5_manifest_doc
        gates = _integrity_gates(
            n=n, k1=k1, k2=k2, k_total=k_total, arms=arms, identity=identity,
            manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
            disjoint_pin=disjoint_pin, order_pin_A=order_pin_A,
            spike_order_pin_B=spike_order_pin_B, set_delta=set_delta,
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
            ir5_manifest=ir5_manifest_doc, out_root=out_path,
            final=True)
        outcome_label = l2_mechanism_probe_2m_label(gates)
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
            "spike_order_file_pin_B": {
                "spike_order_file": str(spike_order_pin_B.get("spike_order_file")),
                "spike_order_digest": str(spike_order_pin_B.get("spike_order_digest")),
                "n": int(spike_order_pin_B.get("n", -1)),
                "k1": int(spike_order_pin_B.get("k1", -1)),
                "k2": int(spike_order_pin_B.get("k2", -1)),
                "prior_digest": str(spike_order_pin_B.get("prior_digest")),
                "program": str(spike_order_pin_B.get("program")),
                "formula_id": str(spike_order_pin_B.get("formula_id")),
                "verified": bool(spike_order_pin_B.get("verified")),
            },
            "expected_spike_order_digest_B": str(spike_order_digest),
            "expected_spike_formula_id": str(spike_formula),
            "order_set_delta": {
                key: (list(value) if isinstance(value, list) else value)
                for key, value in dict(set_delta).items()
            },
            "order_position_identity": order_identity,
            "ir_pins": {
                "ir3_threshold_multipliers": [IR3_LO_MULT, IR3_HI_MULT],
                "ir1_bins": int(IR1_BINS),
                "ir4_topk": int(IR4_TOPK),
                "ir5_mode": "UNCAPPED_FULL_BLOCK_32768_BINARY_LE_BIN_PLUS_MANIFEST",
                "ir5_format_version": str(IR5_FORMAT_VERSION),
                "ir5_per_record_budget_bytes": int(IR5_PER_RECORD_BUDGET_BYTES),
                "ir5_root_budget_bytes": int(IR5_ROOT_BUDGET_BYTES),
                "ir5_max_file_bytes": int(IR5_MAX_FILE_BYTES),
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
        return L2MechanismProbe2mRun(summary=summary, records=tuple(records), gates=gates)
    except L2MechanismProbe2mResourceError:
        raise
    except MemoryError as exc:
        raise L2MechanismProbe2mResourceError(
            f"resource stop: MemoryError: {exc}") from exc


VERIFY_REUSE_FLAGS = (
    "prior", "prior_digest", "alt_prior", "alt_digest",
    "k1", "k2", "order_file", "order_digest",
    "spike_order_file", "spike_order_digest", "spike_formula",
)
DERIVE_SPIKE_ORDER_FLAGS = (
    "prior", "prior_digest", "order_file", "out",
)
SHARED_FLAGS = ("source", "floor", "n")
STAGE_B_ONLY_FLAGS = (
    "prior", "prior_digest", "alt_prior", "alt_digest", "k1", "k2", "construction",
    "construction_digest", "dev_pairs", "dev_frames_val", "dev_frames_hold",
    "block_frames", "remainder_frames", "tag_master", "chunk_rows", "tag_bits",
    "order_file", "order_digest", "spike_order_file", "spike_order_digest",
    "spike_formula", "out_dir",
)
STAGE_B_FLAGS = SHARED_FLAGS + STAGE_B_ONLY_FLAGS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p20s-mechanism-probe-2m",
        description=(
            "NB-Polar Phase 4-P20S maximum-information mechanism probe on the "
            "merged final 2M block with uncapped full-block IR-5: "
            "--verify-reuse replays the P20O 2M reuse pins + spike-B identity "
            "from worktree files with zero protected opens; "
            "--derive-spike-order derives the Stage-A spike-B order "
            "permutation under frozen F-median8 from worktree-prior arrays "
            "only (deterministic, zero sampling); otherwise all Stage-B "
            "flags are required (frozen command, no production default)"
        ),
    )
    parser.add_argument("--verify-reuse", action="store_true",
                        dest="verify_reuse",
                        help="Stage-A reuse-verification mode (all reuse flags required)")
    parser.add_argument("--derive-spike-order", action="store_true",
                        dest="derive_spike_order",
                        help="Stage-A spike-order derivation mode (derive flags required)")
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
    parser.add_argument("--dev-frames-val", default=None, type=int, nargs=2,
                        dest="dev_frames_val")
    parser.add_argument("--dev-frames-hold", default=None, type=int, nargs=2,
                        dest="dev_frames_hold")
    parser.add_argument("--block-frames", default=None, type=int,
                        dest="block_frames")
    parser.add_argument("--remainder-frames", default=None, type=int, nargs=2,
                        dest="remainder_frames")
    parser.add_argument("--tag-master", default=None, type=int, dest="tag_master")
    parser.add_argument("--chunk-rows", default=None, type=int, dest="chunk_rows")
    parser.add_argument("--tag-bits", default=None, type=int, dest="tag_bits")
    parser.add_argument("--order-file", default=None, dest="order_file")
    parser.add_argument("--order-digest", default=None, dest="order_digest")
    parser.add_argument("--spike-order-file", default=None, dest="spike_order_file")
    parser.add_argument("--spike-order-digest", default=None, dest="spike_order_digest")
    parser.add_argument("--spike-formula", default=None, dest="spike_formula")
    parser.add_argument("--out", default=None, dest="out")
    parser.add_argument("--out-dir", default=None, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if bool(args.verify_reuse) and bool(args.derive_spike_order):
            raise ValueError(
                "mixed invocation refused: --verify-reuse and --derive-spike-order "
                "never combine; refusing before any read or write"
            )
        if args.derive_spike_order:
            given_b = [name for name in STAGE_B_ONLY_FLAGS
                       if name not in DERIVE_SPIKE_ORDER_FLAGS
                       and getattr(args, name) is not None]
            if given_b:
                raise ValueError(
                    "mixed invocation refused: --derive-spike-order takes no Stage-B-only flags "
                    f"(got {given_b}); refusing before any read or write"
                )
            given_v = [name for name in VERIFY_REUSE_FLAGS
                       if name not in DERIVE_SPIKE_ORDER_FLAGS
                       and getattr(args, name) is not None]
            if given_v:
                raise ValueError(
                    "mixed invocation refused: --derive-spike-order takes no --verify-reuse-only flags "
                    f"(got {given_v}); refusing before any read or write"
                )
            missing = [name for name in DERIVE_SPIKE_ORDER_FLAGS
                       if getattr(args, name) is None]
            if missing:
                raise ValueError(
                    "missing required --derive-spike-order flags: " + ",".join(sorted(missing))
                    + "; refusing before any read or write"
                )
            with open(args.prior, "rb") as fh:
                data = np.load(fh, allow_pickle=False)
                with data:
                    raw_arrays = {k: np.asarray(data[k]) for k in data.files}
            _gate_call("reuse_prior_identity", verify_session_prior_2m,
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
            written = write_spike_order_file(
                args.out, prior_arrays=raw_arrays, l1_order=frozen_l1,
                prior_digest=str(args.prior_digest))
            print(json.dumps({
                "spike_order_file": written["spike_order_file"],
                "spike_order_digest": written["spike_order_digest"],
                "k1": written["k1"],
                "k2": written["k2"],
                "formula_id": written["formula_id"],
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
                order_file=args.order_file, spike_order_file=args.spike_order_file,
                prior_digest=args.prior_digest, alt_digest=args.alt_digest,
                order_digest=args.order_digest,
                spike_order_digest=args.spike_order_digest,
                spike_formula=_check_spike_formula(args.spike_formula),
                h1=FROZEN_H1, h2=FROZEN_H2, h_total=FROZEN_H_TOTAL,
                k1=args.k1, k2=args.k2, ce_alt=FROZEN_CE_ALT,
                ce_incumbent=FROZEN_CE_INCUMBENT,
                alt_ideal_length_bits=FROZEN_ALT_IDEAL_LENGTH_BITS,
                d2_feasible=FROZEN_D2_FEASIBLE)
            print(json.dumps({
                "reuse_prior_digest": result["prior_digest"],
                "reuse_alt_digest": result["alt_file_digest"],
                "reuse_order_digest_A": result["order_digest_A"],
                "spike_order_digest_B": result["spike_order_digest_B"],
                "spike_program": result["spike_program"],
                "spike_formula_id": result["spike_formula_id"],
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
                    "--derive-spike-order nor any Stage-B flag was given; "
                    "refusing before any read or write"
                )
            raise ValueError(
                "missing required Stage-B flags: " + ",".join(missing)
                + "; refusing before any read or write"
            )
        run = run_l2_mechanism_probe_2m(
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
            dev_frames_val=tuple(args.dev_frames_val),
            dev_frames_hold=tuple(args.dev_frames_hold),
            block_frames=args.block_frames,
            remainder_frames=tuple(args.remainder_frames),
            tag_master=args.tag_master,
            chunk_rows=args.chunk_rows,
            tag_bits=args.tag_bits,
            order_file=args.order_file,
            order_digest=args.order_digest,
            spike_order_file=args.spike_order_file,
            spike_order_digest=args.spike_order_digest,
            spike_formula=args.spike_formula,
            out_dir=args.out_dir,
        )
        summary = run.summary
        print(json.dumps({
            "analysis": summary["analysis"],
            "records_completed": summary["records_completed"],
            "operational_exact_count": summary["aggregates"]["operational"][
                "exact_count"],
            "mechanism_arms": summary["aggregates"]["mechanism"]["arms"],
            "spike_program": summary.get("spike_program"),
            "spike_formula_id": summary.get("spike_formula_id"),
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
            L2MechanismProbe2mContractError) as exc:
        print(f"nbpolar phase4-p20s 2m mechanism-probe refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL_NAME", "MODE", "Q", "ALPHA", "N_BOB", "FROZEN_N", "FROZEN_SOURCE",
    "FROZEN_SOURCE_TAG", "FROZEN_FLOOR", "FROZEN_ALPHA", "FROZEN_TARGET_F",
    "NORM_TOL", "FROZEN_HAZARD_R", "FROZEN_PUBLIC_CONTROL_BITS",
    "FROZEN_RAW_INPUT_BITS", "FROZEN_L2_CONSTRUCTION", "FROZEN_DEV_FRAMES_VAL",
    "FROZEN_DEV_VAL_FRAMES", "FROZEN_DEV_FRAMES_HOLD", "FROZEN_DEV_HOLD_FRAMES",
    "FROZEN_DEV_FRAMES", "FROZEN_DEV_PAIRS", "FROZEN_BLOCK_COUNT",
    "FROZEN_BLOCK_FRAMES", "FROZEN_PAIRS_PER_FRAME", "FROZEN_SYMBOLS_PER_BLOCK",
    "FROZEN_BLOCK_SEGMENTS", "FROZEN_MERGED_FRAME_LIST",
    "FROZEN_REMAINDER_FRAME_RANGE", "FROZEN_REMAINDER_FRAMES",
    "FROZEN_REMAINDER_SYMBOLS", "INTRA_FILE_VAL_FRAME_RANGE",
    "INTRA_FILE_HOLD_FRAME_RANGE", "CONSUMED_2M_TRAIN_FRAME_RANGE",
    "CONSUMED_2M_VAL_DEV_FRAME_RANGE", "CONSUMED_2M_HOLD_DEV_FRAME_RANGE",
    "CONSUMED_1P5M_TRAIN_FRAME_RANGE", "CONSUMED_1P5M_VAL_FRAME_RANGE",
    "CONSUMED_1P5M_HOLD_FRAME_RANGE", "FROZEN_BUILD_FRAME_RANGE",
    "FROZEN_1P5M_VAL_STUB_FRAME_RANGE", "FROZEN_1P5M_VAL_STUB_FRAMES",
    "FROZEN_1P5M_VAL_STUB_SYMBOLS", "FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE",
    "FROZEN_1P5M_HOLD_REMAINDER_FRAMES", "FROZEN_1P5M_HOLD_REMAINDER_SYMBOLS",
    "CONSUMED_1M_SOURCE_TAG", "CONSUMED_1P5M_SOURCE_TAG", "CONSUMED_1M_FRAME_RANGE",
    "FROZEN_MANIFEST_TRAIN_FRAMES",
    "FROZEN_MANIFEST_TRAIN_PAIRS", "FROZEN_MANIFEST_VAL_FRAMES",
    "FROZEN_MANIFEST_VAL_PAIRS", "FROZEN_MANIFEST_HOLD_FRAMES",
    "FROZEN_MANIFEST_HOLD_PAIRS", "FROZEN_DEV_PAIRS_PATH", "FROZEN_DEV_PAIRS_SIZE",
    "FROZEN_DEV_PAIRS_SHA256", "REFUSED_1M_DEV_PAIRS_PATH",
    "REFUSED_1P5M_DEV_PAIRS_PATH", "FROZEN_DEV_BUILD_MANIFEST_PATH",
    "FROZEN_CONSTRUCTION_PATH",
    "FROZEN_CONSTRUCTION_DIGEST", "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA",
    "PAIRS_LOADER_IDENTITY", "FROZEN_TAG_MASTER", "FROZEN_CHUNK_ROWS",
    "FROZEN_TAG_BITS", "SEED_PREFIX", "FROZEN_PRIOR_PATH", "FROZEN_ORDER_FILE_PATH",
    "FROZEN_ALT_PATH", "FROZEN_SPIKE_ORDER_PATH", "FROZEN_SPIKE_ORDER_DIGEST_B",
    "FROZEN_OUT_ROOT", "OUTPUT_FILES", "ATTEMPT_CONSUMPTION_POINT",
    "COMPLETE_LABEL", "RAW_PRIOR_NPZ_KEYS", "ALT_L2_NPZ_KEYS",
    "SPIKE_ORDER_PROTOCOL", "SPIKE_ORDER_KIND", "SPIKE_PROGRAM_PIN",
    "SPIKE_FORMULA_ID", "SPIKE_FORMULA_TEXT", "FROZEN_ARM_NAMES",
    "OPERATIONAL_ARM_NAMES",
    "ORACLE_ARM_NAMES", "PLANNED_SC_CALLS", "PLANNED_TAG_INVOCATIONS",
    "PLANNED_RECORDS", "INTEGRITY_GATE_ORDER", "IR_FIELDS", "IR1_BINS",
    "IR1_EDGE_LO_BITS", "IR1_EDGE_HI_BITS",
    "IR3_LO_MULT", "IR3_HI_MULT", "IR4_TOPK", "IR5_FULL_N", "IR5_FORMAT_VERSION",
    "IR5_HAZARD_DTYPE", "IR5_FLAG_DTYPE", "IR5_HAZARD_BYTES", "IR5_FLAG_BYTES",
    "IR5_PER_RECORD_BUDGET_BYTES", "IR5_ROOT_BUDGET_BYTES", "IR5_MAX_FILE_BYTES",
    "IR5_ARMV_PREFIX", "FROZEN_COMMAND",
    "FROZEN_SESSION_PRIOR_DIGEST", "FROZEN_H1", "FROZEN_H2", "FROZEN_H_TOTAL",
    "FROZEN_BUDGET_LITERAL", "FROZEN_K_TOTAL", "FROZEN_K1", "FROZEN_K2",
    "FROZEN_ORDER_DIGEST_A", "FROZEN_ALT_DIGEST", "FROZEN_ALT_H1_INC",
    "FROZEN_ALT_H2_ALT", "FROZEN_ALT_H_TOTAL_ALT", "FROZEN_CE_ALT",
    "FROZEN_CE_INCUMBENT", "FROZEN_ALT_IDEAL_LENGTH_BITS",
    "FROZEN_D2_MARGIN_BITS", "FROZEN_D2_FEASIBLE", "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S", "EXTERNAL_TIMEOUT_S", "ULIMIT_VIRTUAL_KIB",
    "L2MechanismProbe2mContractError", "L2MechanismProbe2mResourceError",
    "L2MechanismProbe2mRun", "pins_frozen", "pins_are_frozen",
    "planned_totals", "frozen_arm_table", "check_frozen_arm_table",
    "derive_spike_l2_order", "write_spike_order_file", "verify_spike_order_file",
    "order_set_delta", "verify_reuse", "verify_dev_source_identity_2m",
    "verify_merged_containment", "verify_merged_frame_set_identity",
    "verify_consumed_exclusions_merged",
    "form_merged_blocks", "l2_mechanism_probe_2m_seed_bits",
    "_ir_hazard_diagnostics", "_ir5_full_block_arrays", "_ir5_full_block_writer",
    "check_ir5_manifest_identity", "ir_payload_tables",
    "l2_mechanism_probe_2m_label", "run_l2_mechanism_probe_2m", "build_parser",
    "main", "hazard_instrumentation_complete", "mechanism_diagnostics",
    "build_aggregates", "oracle_isolation_ok", "ir_payload_complete",
    "VERIFY_REUSE_FLAGS", "DERIVE_SPIKE_ORDER_FLAGS", "SHARED_FLAGS",
    "STAGE_B_ONLY_FLAGS", "STAGE_B_FLAGS",
]
