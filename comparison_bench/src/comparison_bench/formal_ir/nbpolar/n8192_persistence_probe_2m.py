"""NB-Polar Phase 4-P20T N=8192 persistence probe on the single 2M HOLD-tail DEV block.

Thin importer of accepted predecessors (read-only; no accepted file is
edited here), with ONLY the P20T N=8192 delta. Structural template: the
accepted ``l2_mechanism_probe_2m`` (P20S) runner; derivation template: the
P16 ``operational_f13`` construction/allocation pattern (P16-02: synthetic
TRAIN blocks, pooled risks, worst-first orders, K rule, TRAIN-residual
(K1,K2) selection) via the accepted ``raw_prior_val_1p5m``
``sample_synthetic_train_blocks`` choke point; the P20Q
``_ir_hazard_diagnostics`` code point is the carried-over callsite pattern
for the section 7 recorder extension. Exact delta list (packet section 2),
nothing else:

- (d1) population -> single-segment 2M HOLD-tail DEV ``3595..3626``
  (32 frames, ONE 8192-pair block at N=8192; no cross-split combining; the
  D1-A merge precedent is NOT invoked); declared HOLD remainder
  ``3627..3644`` (18 frames / 4608 pairs) + 1.5M VAL stub ``2172..2212``
  (41 / 10496) + 1.5M HOLD remainder ``2725..2766`` (42 / 10752) counted
  never decoded, never pooled; consumed 1M pool / all consumed 1.5M ranges
  / consumed 2M TRAIN-as-DEV + VAL DEV + HOLD DEV excluded as consumed;
- (d2) reuse -> the P20O worktree ``raw_prior_2m.npz`` ARRAYS ONLY
  (canonical digest replay + H-literal recomputation within 1e-12 + floor
  pins + ``p_b`` cross-check; worktree-file reads only, never the V25
  counts NPZ); formula shapes (budget, tag-length, K-split selection,
  F-median8 ranking, IR-1..IR-4, nine-scalar semantics); code paths
  (``sc.py``, ``sc_chunked_gate.py``, ``transform.py``, causal two-layer
  wiring, Toeplitz accounting, P20A resource/endpoint machinery,
  recount/gate machinery). N=32768 order/K/tag/leakage literals stay at
  N=32768 and SHALL NOT transfer;
- (d3) K pins -> DERIVED IN-PACKET: ``K_total =
  floor((1.3*8192*H-64)/5)`` from recomputed 2M H with ``(K1,K2)`` by
  exhaustive TRAIN-residual selection, frozen before DEV; NEVER from
  (334,6746), never from alt-H, never from 1.5M;
- (d4) orders -> DUAL FRESH at N=8192: Stage-A fresh L1/L2 worst-first
  order file (byte-identical on arms A/O) + Stage-A spike order file
  (byte-identical on arm B), each digest-gated, each disclosing first-K1 /
  first-K2 prefixes at identical sizes;
- (d5) arms A/B/O per packet section 6 (same K on A/B, carried K2 on O;
  incumbent ``p1`` + recomputed alpha1 ``p2_alt`` tables byte-identical on
  A/B; order SET is the only delta between A and B);
- (d6) new P20T tag domain (master 2026092400, prefix
  ``nbpolar-p20t-n8192-persistence-2m-seed``, 81983 bits/tag);
- (d7) N=8192 derivation program (worktree-prior-only synthetic TRAIN
  sampling under frozen seeds 2026092410..2026092413 x 4 blocks/stream =
  16 blocks + deterministic F-median8 spike permutation on the
  TRAIN-pooled mean L2 hazard with R=8 re-frozen for 8192-geometry, zero
  scoring-time sampling/genie, zero protected reads, frozen formula-id) +
  construction/order/spike-identity gates + derivation-program pin;
- (d8) single-segment DEV population + DEV/build-frames disjointness
  declared inside the TRAIN-exclusion gate (S2-ii: build subset 2M TRAIN
  0..2186 vs DEV HOLD 3595..3626);
- (d9) IR-5 N=8192-sized full-block binary series + manifest (48 KiB per
  record), same truth-isolation boundary.

No SC/transform/floor-semantics/tag-semantics change; no second factor; no
lambda anywhere; no K/floor/order/decoder/step/success-point selection on
closed blocks; no derivation or sampling on real frames.

Spike-h source (frozen Stage-A reading, recorded for Pre-EXECUTE
adjudication): the packet carries the F-median8 formula-id with R=8
re-frozen for 8192-geometry and requires the Stage-A spike permutation to
be deterministic with zero SCORING-time sampling/genie (PROMPT step 3),
zero protected reads, and worktree-prior-arrays-only inputs, inside the
single frozen 16-block derivation budget (section 8/section 9
``sampling_calls_exact``). No canonical sampling-free static length-8192
hazard vector exists over the prior arrays, so ``h`` is the TRAIN-pooled
mean L2 hazard ``h2_mean`` (length 8192) from the SINGLE frozen 16-block
synthetic sampling (section 3 d1 products, shared budget — the spike
derivation adds 0 sampling blocks and 0 genie calls of its own). The
formula SHAPE is carried (score = h - local median, descending rank,
ascending tie-break); the R=8 window convention is re-decided (re-frozen)
for the 8192 coordinate geometry rather than carried automatically.

Three explicit modes, never mixed: (i) Stage-A derivation (``--derive``;
worktree-prior arrays ONLY under the frozen seeds/budget, fail-if-present
outputs, runs exactly once); (ii) Stage-A derivation verification
(``--verify-derivation``; file-digest replay + K-rule replay + pin replay
from the Stage-A files with zero sampling, zero protected opens);
(iii) Stage-B frozen command mode (all Stage-B flags required, no
production default). Mixed or ambiguous invocation refuses before anything
is read or written.
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
from . import l2_alt_hold_1p5m as p20n
from . import operational_f13 as opf
from . import raw_prior_val_1p5m as p20m
from . import l2_alt_maintain_2m as p20o
from . import l2_mechanism_probe_2m as p20s
from .algebra import make_gf32
from .empirical_genie_scaling import select_empirical_split
from .per_session_calibration import canonical_prior_digest
from .prior import derive_p2
from .target_n_scaling import budget_k_total
from .transform import polar_transform

# Reused accepted contracts (read-only; never reimplemented here).
# 2M reuse layer (accepted P20O 2M pins): the session-H inputs, the
# worktree prior digest recipe and the formula/code paths below. ``p20m``
# is used ONLY for the session-agnostic budget-literal recomputation
# (``verify_budget_literal``: pure K_total math from same-run H, never a
# carried absolute), the synthetic TRAIN sampler
# (``sample_synthetic_train_blocks``: the accepted P13/P16 TRAIN choke
# point) and the raw-prior builder (test fixtures only); ``p20n`` ONLY
# for the session-agnostic frozen alpha=1 prefloor rule
# (``alt_prefloor_table``: pure counts math). No 1.5M file, path, frame
# range, or K literal enters this module. No N=32768 K/order/tag/leakage
# literal enters this module.
run_operational_block = p20o.run_operational_block
run_oracle_control_block = p20o.run_oracle_control_block
OracleControlResult = p20o.OracleControlResult
verify_dev_manifest_2m = p20o.verify_dev_manifest_2m
verify_session_prior_2m = p20o.verify_session_prior_2m
_hazard_bits = p20o._hazard_bits
_raw_p2_from_counts = p20o._raw_p2_from_counts
first_error_coordinate = p20o.first_error_coordinate
l1_prefix_positions = p20o.l1_prefix_positions
l2_prefix_positions = p20o.l2_prefix_positions
seed_bits_for = p20o.seed_bits_for
_stat_record = p20m._stat_record
_block_view = p20m._block_view
_dev_block_scoring = p20m._dev_block_scoring
_scoring_absent = p20m._scoring_absent
_selected_diagnostics = p20m._selected_diagnostics
n8192_recount_events = p20m.raw_prior_val_1p5m_recount_events
_ir_hist_edges = p20s._ir_hist_edges
_ir_hist_counts = p20s._ir_hist_counts
alt_prefloor_table = p20n.alt_prefloor_table
HAZARD_FIELDS = p20o.HAZARD_FIELDS
OPERATIONAL_PROVENANCE = p20o.OPERATIONAL_PROVENANCE
ORACLE_PROVENANCE = p20o.ORACLE_PROVENANCE
ArmSpec = p20o.ArmSpec

PROTOCOL_NAME = "nbpolar-p20t-n8192-persistence-2m"
MODE = "n8192-tail-persistence-probe-2m"

Q = p20o.Q  # 32
ALPHA = p20o.ALPHA  # 2
N_BOB = p20o.N_BOB  # 1024
NORM_TOL = 1e-12
FROZEN_N = 8192
FROZEN_SOURCE = "2M"
FROZEN_SOURCE_TAG = "type2_2M_20260121_183657"
FROZEN_FLOOR = 1e-15
FROZEN_ALPHA = 1.0
FROZEN_TARGET_F = 1.3
FROZEN_HAZARD_R = 8  # RE-FROZEN as a NEW freeze decision for 8192-geometry
FROZEN_PUBLIC_CONTROL_BITS = 10 * FROZEN_N + 63  # 81983 per tag
FROZEN_RAW_INPUT_BITS = 10 * FROZEN_N  # 81920 per block
FROZEN_L2_CONSTRUCTION = "alt-\u03b11"
FROZEN_SC_STAGES = 13  # log2(8192)

# Single-segment population (packet section 4; first-contiguous-block rule).
FROZEN_DEV_FRAMES_HOLD = (3595, 3626)
FROZEN_DEV_FRAMES = 32
FROZEN_DEV_PAIRS = 8192
FROZEN_BLOCK_COUNT = 1
FROZEN_BLOCK_FRAMES = 32
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_DEV_FRAME_LIST = tuple(range(3595, 3627))
INTRA_FILE_HOLD_FRAME_RANGE = (2916, 3644)
FROZEN_REMAINDER_FRAME_RANGE = (3627, 3644)
FROZEN_REMAINDER_FRAMES = 18
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_BUILD_FRAME_RANGE = (0, 2186)
CONSUMED_2M_TRAIN_FRAME_RANGE = (0, 2186)
CONSUMED_2M_VAL_DEV_FRAME_RANGE = (2187, 2826)
CONSUMED_2M_HOLD_DEV_FRAME_RANGE = (2916, 3555)
CONSUMED_1P5M_SOURCE_TAG = "type2_1p5M_20260121_183806"
CONSUMED_1P5M_TRAIN_FRAME_RANGE = (0, 1659)
CONSUMED_1P5M_VAL_FRAME_RANGE = (1660, 2212)
CONSUMED_1P5M_HOLD_FRAME_RANGE = (2213, 2766)
FROZEN_1P5M_VAL_STUB_FRAME_RANGE = (2172, 2212)
FROZEN_1P5M_VAL_STUB_FRAMES = 41
FROZEN_1P5M_VAL_STUB_SYMBOLS = (
    FROZEN_1P5M_VAL_STUB_FRAMES * FROZEN_PAIRS_PER_FRAME)
FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE = (2725, 2766)
FROZEN_1P5M_HOLD_REMAINDER_FRAMES = 42
FROZEN_1P5M_HOLD_REMAINDER_SYMBOLS = (
    FROZEN_1P5M_HOLD_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME)
FROZEN_MANIFEST_TRAIN_FRAMES = 2187
FROZEN_MANIFEST_TRAIN_PAIRS = 559872
FROZEN_MANIFEST_VAL_FRAMES = 729
FROZEN_MANIFEST_VAL_PAIRS = 186624
FROZEN_MANIFEST_HOLD_FRAMES = 729
FROZEN_MANIFEST_HOLD_PAIRS = 186624

# 1M pool fail-closed identity (path refusal by name; never opened).
CONSUMED_1M_SOURCE_TAG = "type2_1M_20260121_184040"
REFUSED_1M_DEV_PAIRS_PATH = (
    "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
    "v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet")
REFUSED_1P5M_DEV_PAIRS_PATH = (
    "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
    "v13r3fresh_pairs_20260816/type2_1p5M_20260121_183806/pairs.parquet")
FROZEN_DEV_PAIRS_PATH = (
    "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
    "v13r3fresh_pairs_20260816/type2_2M_20260121_183657/pairs.parquet")
FROZEN_MANIFEST_PATH = (
    "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
    "nbldpc_v25_20260818/run_04/split_manifest.json")
FROZEN_MANIFEST_SCHEMA = "nbldpc_v25_split_manifest_v1"

FROZEN_TAG_MASTER = 2026092400
SEED_PREFIX = "nbpolar-p20t-n8192-persistence-2m-seed"
FROZEN_CHUNK_ROWS = 128  # P11 precedent resized: 512/4, preserving 64 chunks
FROZEN_TAG_BITS = 64

# Stage-A derivation pins (packet section 3 d1; P16 4-streams x 4-blocks).
FROZEN_DERIVATION_SEEDS = (2026092410, 2026092411, 2026092412, 2026092413)
FROZEN_TRAIN_BLOCKS_PER_SEED = 4
FROZEN_TRAIN_BLOCKS_TOTAL = 16
FROZEN_TRAIN_GENIE_CALLS = 32  # L1+L2 per synthetic TRAIN block, Stage A only

# Reuse pins (packet section 3 p1; digest/H recomputed, never hand-filled).
FROZEN_PRIOR_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz")
FROZEN_SESSION_PRIOR_DIGEST = (
    "b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587")
FROZEN_H1 = 0.02566204884275839
FROZEN_H2 = 0.8069006731309893
FROZEN_H_TOTAL = 0.8325627219737477
FROZEN_ALT_FLOOR_HIT_RATE = p20o.FROZEN_ALT_FLOOR_HIT_RATE

# Stage-A product pins (filled at Stage-A close; None before the freeze).
FROZEN_K_TOTAL = 1760
FROZEN_K1 = 84
FROZEN_K2 = 1676
FROZEN_BUDGET_LITERAL = (
    "1.3*8192*0.8325627219737475-64 over 5, floored, clipped [0,16384] = 1760")
FROZEN_TRAIN_RESIDUAL = 0.013377854243068005
FROZEN_CONSTRUCTION_PATH_8192 = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/"
    "construction_and_allocation_8192.json")
FROZEN_CONSTRUCTION_DIGEST_8192 = (
    "d77466eca5b80840ba114ba76500d73d472a5f2818e1fc00b28abbd86d352bb6")
FROZEN_ORDER_PATH_8192 = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/"
    "fresh_orders_8192.json")
FROZEN_ORDER_DIGEST_A_8192 = (
    "66aefea8d88ef0160906ea37575aa4c4c0dbc0dda6fcd67513a61458198ade93")
FROZEN_SPIKE_ORDER_PATH_8192 = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/"
    "new_spike_order_8192.json")
FROZEN_SPIKE_ORDER_DIGEST_B_8192 = (
    "355a32d3551c065088da6627dc1ad4ec07b004b73d322567eddaf8cadf03352a")
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/"
    "n8192_persistence_probe_2m")
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
ATTEMPT_CONSUMPTION_POINT = "first protected content open (single 2M HOLD-tail pairs parquet)"
COMPLETE_LABEL = "TARGET_EMPIRICAL_N8192_TAIL_PERSISTENCE_PROBE_COMPLETE"

# Exact keys of the reused Stage-A worktree prior (no more, no fewer).
RAW_PRIOR_NPZ_KEYS = p20o.RAW_PRIOR_NPZ_KEYS  # 10 keys

# Fresh-order file identity (frozen format; mirrors the P20O order-file
# keys at the new N with the P20T protocol + derivation provenance).
ORDER_PROTOCOL = PROTOCOL_NAME
ORDER_KIND = "fresh-orders-file-8192"
CONSTRUCTION_PROTOCOL = PROTOCOL_NAME
CONSTRUCTION_KIND = "construction-and-allocation-8192"
SPIKE_ORDER_PROTOCOL = PROTOCOL_NAME
SPIKE_ORDER_KIND = "spike-l2-order-file-8192"

# Frozen derivation-program pin (module + function + rule + determinism).
DERIVATION_PROGRAM_PIN = (
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar."
    "n8192_persistence_probe_2m:run_derive_stage_a -- "
    "sample_synthetic_train_blocks(p_b, f_raw, p1, p2, seeds "
    "2026092410..2026092413, 4/stream = 16 blocks, n=8192, per-stream RNG "
    "restart, P13 true-prefix/oracle-conditioned genie rows) + pooled mean "
    "risks + select_empirical_split worst-first (e,h,index) exhaustive K1 "
    "enumeration (K2 = K_total - K1, TRAIN-residual minimum) + "
    "budget_k_total(8192, recomputed H, 1.3) + F-median8 spike on the "
    "TRAIN-pooled mean L2 hazard h2_mean (R=8 re-frozen for 8192-geometry, "
    "stable descending argsort, ties ascending); deterministic under the "
    "frozen seeds; inputs worktree raw_prior_2m.npz arrays only; the spike "
    "adds 0 sampling blocks + 0 genie calls beyond the frozen 16-block / "
    "32-genie budget"
)
SPIKE_FORMULA_ID = (
    "F_MEDIAN8_CARRIED_20260920_H_MINUS_LOCAL_MEDIAN_W8_R8_REFROZEN_8192")
SPIKE_FORMULA_TEXT = (
    "F-median8: score[i] = h[i] \u2212 median(h over the R=8 clipped "
    "natural neighborhood of i), where h[i] is the TRAIN-pooled mean L2 "
    "hazard at 8192-coordinate i from the single frozen 16-block synthetic "
    "TRAIN sampling (worktree raw_prior_2m.npz arrays only); rank all 8192 "
    "L2 positions by descending score; take the first K2 positions as arm "
    "B's disclosed L2 set; tie-break by ascending natural block coordinate; "
    "deterministic under the frozen seeds; zero scoring-time sampling, zero "
    "scoring-time genie calls, zero protected reads; arm A's set stays the "
    "newly-derived frozen-order-equivalent first-K2 prefix. R=8 is re-frozen "
    "as a NEW freeze decision for 8192-geometry (window convention "
    "re-decided for the 8192 coordinate geometry, not an automatic carry)."
)

FROZEN_ARM_NAMES = (
    "A_anchor_frozen_order_equivalent",
    "B_spike_local_order",
    "O_true_l1_oracle",
)
OPERATIONAL_ARM_NAMES = (
    "A_anchor_frozen_order_equivalent", "B_spike_local_order",
)
ORACLE_ARM_NAMES = (
    "O_true_l1_oracle",
)
PLANNED_SC_CALLS = 5
PLANNED_TAG_INVOCATIONS = 3
PLANNED_RECORDS = 3

# (d7) mandatory IR-1..IR-4 pins (all frozen PRESENT, bounded,
# recording-only, post-decode; same caps/formulas as P20Q section 7; the
# truth-isolation boundary is pinned in the record writers and covered by
# the sentinel test) + IR-5 N=8192-sized binary pins (d9).
IR1_BINS = 64
IR1_EDGE_LO_BITS = 1e-3
IR1_EDGE_HI_BITS = 32.0
IR3_LO_MULT = 1.0
IR3_HI_MULT = 2.0
IR4_TOPK = 16
# IR-5 N=8192-sized (d9): per record exactly three binary little-endian
# series (8192 float32-LE hazards + 8192 uint8 in-prefix flags + 8192 uint8
# U-domain flags) + `ir5full-v1` manifest linkage; binary `.bin` + JSON
# manifest ONLY (no text-JSON float dumps, no npz/npy/parquet).
IR5_FULL_N = 8192
IR5_FORMAT_VERSION = "ir5full-v1"
IR5_HAZARD_DTYPE = "<f4"
IR5_FLAG_DTYPE = "u1"
IR5_HAZARD_BYTES = 32768
IR5_FLAG_BYTES = 8192
IR5_PER_RECORD_BYTES = IR5_HAZARD_BYTES + 2 * IR5_FLAG_BYTES  # 49152 = 48 KiB
IR5_PER_RECORD_BUDGET_BYTES = 64 * 1024
IR5_ROOT_BUDGET_BYTES = 1536 * 1024
IR5_MAX_FILE_BYTES = 2 * 1024 * 1024
IR5_ARMV_PREFIX = {
    "A_anchor_frozen_order_equivalent": "A",
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
    "predecessor_r1_root_identity",
    "reuse_prior_arrays_identity",
    "new_construction_identity_8192",
    "fresh_order_identity_A_8192",
    "spike_order_identity_B_8192",
    "order_derivation_identity",
    "k_rule_derived",
    "target_population_contract",
    "dev_population_exact",
    "blocks_exact_with_declared_remainder",
    "three_records_exact",
    "sampling_calls_exact",
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

# Predecessor lineage (read-only reference, never re-derived, never carried
# as construction; pure string pins, zero I/O).
FROZEN_PREDECESSOR_LABEL = (
    "TARGET_EMPIRICAL_N32768_MERGED_MECHANISM_PROBE_2M_COMPLETE_ACCEPTED_DESCRIPTIVE")

# Process-level one-open guards: set at first content load/open, never cleared.
_SESSION_PRIOR_CONTENT_LOADED = False
_DEV_PARQUET_CONTENT_OPENED = False

class N8192PersistenceProbeContractError(ValueError):
    """Fail-closed contract refusal (gate BLOCKED)."""


class N8192PersistenceProbeResourceError(RuntimeError):
    """Resource-stop ownership (abort preserved, never success)."""


def _gate_call(gate_name, fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except (ValueError, FileExistsError, FileNotFoundError, OSError) as exc:
        raise N8192PersistenceProbeContractError(
            f"BLOCKED({gate_name}): {exc}") from exc


def _require_stage_a_pins() -> dict:
    """Fail-closed Stage-A pin check (K + budget + residual + 3 digests)."""
    missing = [name for name, value in (
        ("FROZEN_K_TOTAL", FROZEN_K_TOTAL),
        ("FROZEN_K1", FROZEN_K1),
        ("FROZEN_K2", FROZEN_K2),
        ("FROZEN_BUDGET_LITERAL", FROZEN_BUDGET_LITERAL),
        ("FROZEN_TRAIN_RESIDUAL", FROZEN_TRAIN_RESIDUAL),
        ("FROZEN_CONSTRUCTION_DIGEST_8192", FROZEN_CONSTRUCTION_DIGEST_8192),
        ("FROZEN_ORDER_DIGEST_A_8192", FROZEN_ORDER_DIGEST_A_8192),
        ("FROZEN_SPIKE_ORDER_DIGEST_B_8192",
         FROZEN_SPIKE_ORDER_DIGEST_B_8192),
    ) if value is None]
    if missing:
        raise N8192PersistenceProbeContractError(
            "Stage-A freeze not yet applied: "
            + ",".join(missing))
    return {
        "k_total": int(FROZEN_K_TOTAL),  # type: ignore[arg-type]
        "k1": int(FROZEN_K1),  # type: ignore[arg-type]
        "k2": int(FROZEN_K2),  # type: ignore[arg-type]
        "budget_literal": str(FROZEN_BUDGET_LITERAL),
        "train_residual": float(FROZEN_TRAIN_RESIDUAL),  # type: ignore[arg-type]
        "construction_digest": str(FROZEN_CONSTRUCTION_DIGEST_8192),
        "order_digest": str(FROZEN_ORDER_DIGEST_A_8192),
        "spike_order_digest": str(FROZEN_SPIKE_ORDER_DIGEST_B_8192),
    }


def pins_frozen() -> dict:
    """Stage-A pin snapshot (K + budget + residual + digests + formula)."""
    try:
        pins = _require_stage_a_pins()
    except N8192PersistenceProbeContractError:
        return {
            "k_total": None, "k1": None, "k2": None,
            "budget_literal": None, "train_residual": None,
            "construction_digest": None, "order_digest": None,
            "spike_order_digest": None, "formula_id": SPIKE_FORMULA_ID,
            "program": DERIVATION_PROGRAM_PIN, "frozen": False,
        }
    pins["formula_id"] = SPIKE_FORMULA_ID
    pins["program"] = DERIVATION_PROGRAM_PIN
    pins["frozen"] = True
    return pins


def pins_are_frozen() -> bool:
    return bool(pins_frozen().get("frozen"))


def planned_totals(k1: int, k2: int) -> dict:
    """Frozen section 5 planned disclosure totals from the derived integers."""
    k1, k2 = int(k1), int(k2)
    if k1 < 0 or k2 < 0:
        raise ValueError(f"planned point must be non-negative, got {(k1, k2)}")
    k_total = k1 + k2
    key_total = 2 * (5 * k_total + 64) + (5 * k2 + 64)
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
    """Materialize the three hardcoded arms from the Stage-A pins."""
    pins = _require_stage_a_pins()
    k1, k2 = int(pins["k1"]), int(pins["k2"])
    k_total = int(pins["k_total"])
    if k1 + k2 != k_total:
        raise ValueError(
            f"Stage-A pins inconsistent: K1+K2={k1 + k2} != K_total={k_total}")
    return (
        ArmSpec("A_anchor_frozen_order_equivalent", "operational", k1, k2,
                5 * k_total + 64, OPERATIONAL_PROVENANCE, "alt"),
        ArmSpec("B_spike_local_order", "operational", k1, k2,
                5 * k_total + 64, OPERATIONAL_PROVENANCE, "alt"),
        ArmSpec("O_true_l1_oracle", "oracle_control", 0, k2,
                5 * k2 + 64, ORACLE_PROVENANCE, "alt"),
    )


def check_frozen_arm_table() -> dict:
    """Fail-closed pin of the three frozen arms and their design accounting."""
    arms = frozen_arm_table()
    names = [spec.name for spec in arms]
    if names != list(FROZEN_ARM_NAMES):
        raise ValueError(f"frozen arm names {names} != {list(FROZEN_ARM_NAMES)}")
    kinds = [spec.kind for spec in arms]
    if kinds != ["operational", "operational", "oracle_control"]:
        raise ValueError(f"frozen arm kinds {kinds} unexpected")
    pins = _require_stage_a_pins()
    for spec in arms:
        if spec.kind == "operational":
            if (spec.k1, spec.k2) != (pins["k1"], pins["k2"]):
                raise ValueError("operational arm K != Stage-A pins")
            if spec.leakage_bits != 5 * pins["k_total"] + 64:
                raise ValueError("operational arm leakage != 5*K_total+64")
        else:
            if (spec.k1, spec.k2) != (0, pins["k2"]):
                raise ValueError("oracle arm K != (0, K2)")
            if spec.leakage_bits != 5 * pins["k2"] + 64:
                raise ValueError("oracle arm leakage != 5*K2+64")
    return {"arms": names, "k1": pins["k1"], "k2": pins["k2"],
            "k_total": pins["k_total"], "verified": True}


def _check_source(value) -> str:
    if str(value) != FROZEN_SOURCE:
        raise ValueError(f"frozen point requires source={FROZEN_SOURCE!r}, got {value!r}")
    return str(value)


def _check_floor(value) -> float:
    if float(value) != float(FROZEN_FLOOR):
        raise ValueError(f"frozen point requires floor={FROZEN_FLOOR}, got {value!r}")
    return float(value)


def _check_n(value) -> int:
    if int(value) != int(FROZEN_N):
        raise ValueError(f"frozen point requires n={FROZEN_N}, got {value!r}")
    return int(value)


def _check_k1(value) -> int:
    pins = _require_stage_a_pins()
    if int(value) != int(pins["k1"]):
        raise ValueError(f"frozen point requires k1={pins['k1']}, got {value!r}")
    return int(value)


def _check_k2(value) -> int:
    pins = _require_stage_a_pins()
    if int(value) != int(pins["k2"]):
        raise ValueError(f"frozen point requires k2={pins['k2']}, got {value!r}")
    return int(value)


def _check_chunk_contract_8192(chunk_rows: int) -> int:
    """Refuse anything but the frozen N=8192 chunk geometry before any artifact access.

    Carries the accepted structural contract (``sc._minus_block``
    chunk_rows default 512, keyword-only; ``sc_decode`` exposes no chunk
    argument) read-only, with the value pin re-frozen to 128 per the P11
    precedent (512/4, preserving 64 chunks at N=8192; frozen here, not
    tunable).
    """
    import inspect

    import comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc as sc_mod

    out = opf._as_int(chunk_rows, "chunk_rows", minimum=1)
    params = inspect.signature(sc_mod._minus_block).parameters
    if params.get("chunk_rows", None) is None or params["chunk_rows"].default != 512:
        raise ValueError(
            "frozen contract: _minus_block chunk_rows default must be exactly 512")
    if params["chunk_rows"].kind is not inspect.Parameter.KEYWORD_ONLY:
        raise ValueError("frozen contract: chunk_rows must be keyword-only")
    if any("chunk" in name for name in inspect.signature(sc_mod.sc_decode).parameters):
        raise ValueError("frozen contract: sc_decode must expose no chunk argument")
    if out != int(FROZEN_CHUNK_ROWS):
        raise ValueError(
            f"frozen point requires chunk-rows={int(FROZEN_CHUNK_ROWS)}, got {out}")
    return out


def _check_tag_master(value) -> int:
    if int(value) != int(FROZEN_TAG_MASTER):
        raise ValueError(
            f"frozen point requires tag-master={FROZEN_TAG_MASTER}, got {value!r}")
    return int(value)


def _check_dev_frames_hold(value) -> tuple:
    pair = tuple(opf._as_int(v, "dev-frames-hold", minimum=0) for v in value)
    if pair != tuple(FROZEN_DEV_FRAMES_HOLD):
        raise ValueError(
            f"frozen point requires dev-frames-hold={tuple(FROZEN_DEV_FRAMES_HOLD)}, "
            f"got {pair!r}")
    return pair


def _check_remainder_frames(value) -> tuple:
    pair = tuple(opf._as_int(v, "remainder-frames", minimum=0) for v in value)
    if pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise ValueError(
            "frozen point requires remainder-frames="
            f"{tuple(FROZEN_REMAINDER_FRAME_RANGE)}, got {pair!r}")
    return pair


def _check_prior_digest(value) -> str:
    if str(value) != str(FROZEN_SESSION_PRIOR_DIGEST):
        raise ValueError("prior-digest flag != frozen reuse pin")
    return str(value)


def _check_construction_digest(value) -> str:
    pins = _require_stage_a_pins()
    if str(value) != str(pins["construction_digest"]):
        raise ValueError("construction-digest flag != frozen Stage-A digest")
    return str(value)


def _check_order_digest_A(value) -> str:
    pins = _require_stage_a_pins()
    if str(value) != str(pins["order_digest"]):
        raise ValueError("order-digest flag != frozen Stage-A fresh-order digest")
    return str(value)


def _check_spike_order_digest_B(value) -> str:
    pins = _require_stage_a_pins()
    if str(value) != str(pins["spike_order_digest"]):
        raise ValueError("spike-order-digest flag != frozen Stage-A spike digest")
    return str(value)


def _check_spike_formula(value) -> str:
    if str(value) != str(SPIKE_FORMULA_ID):
        raise ValueError("--spike-formula != frozen F-median8 formula-id")
    return str(value)


def _check_deriv_seeds(value) -> tuple:
    seeds = tuple(opf._as_int(v, "derivation seed", minimum=0) for v in value)
    if seeds != tuple(FROZEN_DERIVATION_SEEDS):
        raise ValueError(
            f"derivation requires the frozen seeds {list(FROZEN_DERIVATION_SEEDS)}, "
            f"got {list(seeds)}")
    return seeds


def frozen_command(*, k1=None, k2=None) -> str:
    """Render the frozen Stage-B command with the Stage-A pins filled."""
    pins = _require_stage_a_pins()
    k1 = pins["k1"] if k1 is None else _check_k1(k1)
    k2 = pins["k2"] if k2 is None else _check_k2(k2)
    return (
        "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && "
        "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "
        "MALLOC_ARENA_MAX=2 && "
        "ulimit -v 2097152 && "
        "timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
        "comparison_bench.src.comparison_bench.formal_ir.nbpolar."
        "n8192_persistence_probe_2m "
        f"--prior {FROZEN_PRIOR_PATH} "
        f"--prior-digest {FROZEN_SESSION_PRIOR_DIGEST} "
        "--source 2M --floor 1e-15 --n 8192 "
        f"--k1 {int(k1)} --k2 {int(k2)} "
        f"--construction {FROZEN_CONSTRUCTION_PATH_8192} "
        f"--construction-digest {pins['construction_digest']} "
        f"--dev-pairs {FROZEN_DEV_PAIRS_PATH} "
        "--dev-frames-hold 3595 3626 --block-frames 32 "
        "--remainder-frames 3627 3644 "
        f"--tag-master {int(FROZEN_TAG_MASTER)} --chunk-rows 128 --tag-bits 64 "
        f"--order-file {FROZEN_ORDER_PATH_8192} "
        f"--order-digest {pins['order_digest']} "
        f"--spike-order-file {FROZEN_SPIKE_ORDER_PATH_8192} "
        f"--spike-order-digest {pins['spike_order_digest']} "
        f"--spike-formula {SPIKE_FORMULA_ID} "
        f"--out-dir {FROZEN_OUT_ROOT}"
    )


FROZEN_COMMAND = frozen_command() if pins_are_frozen() else None


# ---------------------------------------------------------------------------
# Stage-A derivation program (frozen section 3 d1/d2/d3/d4; runs exactly
# once via --derive; worktree-prior arrays ONLY under the frozen
# seeds/budget; zero counts-NPZ opens, zero real-frame use).
# ---------------------------------------------------------------------------

def derive_spike_order_8192(h2_mean) -> dict:
    """Derive the spike L2-order permutation under frozen F-median8.

    Pure function (no I/O, no RNG, no sampler, no genie): scores
    ``score[i] = h[i] - median(h over the R=8 clipped natural neighborhood
    of i)`` with ``h`` the TRAIN-pooled mean L2 hazard (length 8192) from
    the single frozen 16-block synthetic sampling, ``R =
    FROZEN_HAZARD_R`` (re-frozen for 8192-geometry), then ranks all 8192 L2
    positions by descending score with ties broken by ascending ``i``
    (stable descending argsort). Returns the length-8192 spike-L2
    permutation plus scores/medians. Sampling/genie calls are 0 by
    construction (no sampler exists here; the pooled means are inputs).
    """
    h = np.ascontiguousarray(np.asarray(h2_mean, dtype=np.float64)).ravel()
    if h.shape != (FROZEN_N,):
        raise ValueError(
            f"pooled mean L2 hazard must be length {FROZEN_N}, got {h.shape}")
    if not np.isfinite(h).all():
        raise ValueError("pooled mean L2 hazard must be finite")
    n = int(FROZEN_N)
    r = int(FROZEN_HAZARD_R)
    offsets = np.arange(-r, r + 1, dtype=np.int64)
    idx = np.arange(n, dtype=np.int64)[:, None] + offsets[None, :]
    valid = (idx >= 0) & (idx < n)
    window = np.where(valid, h[np.clip(idx, 0, n - 1)], np.nan)
    medians = np.ascontiguousarray(np.nanmedian(window, axis=1))
    if not np.isfinite(medians).all():
        raise ValueError("spike-order derivation: non-finite local median hazard")
    scores = np.ascontiguousarray(h - medians)
    spike_l2_order = np.argsort(-scores, kind="stable").astype(np.int64)
    if set(spike_l2_order.tolist()) != set(range(FROZEN_N)):
        raise ValueError("derived spike-L2 order is not a permutation of 0..N-1")
    return {
        "spike_l2_order": np.ascontiguousarray(spike_l2_order),
        "spike_scores": np.ascontiguousarray(scores),
        "spike_medians": np.ascontiguousarray(medians),
        "hazard_radius_R": int(r),
        "formula_id": SPIKE_FORMULA_ID,
        "program": DERIVATION_PROGRAM_PIN,
        "sampling_calls": 0,
        "genie_calls": 0,
    }


def run_derive_stage_a(*, prior_path=FROZEN_PRIOR_PATH,
                       expected_prior_digest: str = FROZEN_SESSION_PRIOR_DIGEST,
                       out_construction_path=FROZEN_CONSTRUCTION_PATH_8192,
                       out_orders_path=FROZEN_ORDER_PATH_8192,
                       out_spike_path=FROZEN_SPIKE_ORDER_PATH_8192,
                       seeds=FROZEN_DERIVATION_SEEDS,
                       blocks_per_seed: int = FROZEN_TRAIN_BLOCKS_PER_SEED,
                       n: int = FROZEN_N) -> dict:
    """Execute the frozen Stage-A derivation once; write the three products.

    The single read-only worktree-npz read (digest-reverified first, H
    recomputed within 1e-12) feeds the section 3 derivation; the products
    fail if present. Zero protected opens: no V25 counts NPZ, no
    DEV/VAL/HOLD parquet, no 1M/1.5M/2M contact beyond the worktree file,
    zero decoder execution. Model sampling runs here (Stage A) only, under
    the frozen 16-block budget and seeds.
    """
    out_construction = Path(out_construction_path)
    out_orders = Path(out_orders_path)
    out_spike = Path(out_spike_path)
    for path in (out_construction, out_orders, out_spike):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite existing Stage-A product: {path}")
    seeds = list(_check_deriv_seeds(seeds))
    if int(blocks_per_seed) != int(FROZEN_TRAIN_BLOCKS_PER_SEED):
        raise ValueError(
            "derivation requires blocks_per_seed="
            f"{int(FROZEN_TRAIN_BLOCKS_PER_SEED)}, got {int(blocks_per_seed)}")
    if int(n) != int(FROZEN_N):
        raise ValueError(f"derivation requires n={FROZEN_N}, got {n}")
    start = time.perf_counter()
    # The one read-only worktree open (digest + H re-verified; no-reopen
    # guarded at Stage B by the process-level one-open guard).
    with open(prior_path, "rb") as fh:
        data = np.load(fh, allow_pickle=False)
        with data:
            raw_arrays = {k: np.asarray(data[k]) for k in data.files}
    verified = _gate_call(
        "reuse_prior_arrays_identity", verify_session_prior_2m,
        raw_arrays, expected_digest=str(expected_prior_digest),
        expected_h1=float(FROZEN_H1), expected_h2=float(FROZEN_H2),
        expected_total=float(FROZEN_H_TOTAL))
    prior_digest = str(verified["digest"])
    h1, h2, h_total = float(verified["h1"]), float(verified["h2"]), float(
        verified["h_total"])
    # K rule derived in-packet from recomputed H (never hand-filled).
    k_total = int(budget_k_total(int(n), float(h_total), float(FROZEN_TARGET_F)))
    budget = p20m.verify_budget_literal(
        float(h_total), int(k_total), n=int(n), target_f=float(FROZEN_TARGET_F))
    budget_literal = str(budget["literal"])
    # 16 synthetic TRAIN blocks under the frozen derivation seeds.
    sampled = p20m.sample_synthetic_train_blocks(
        np.asarray(verified["p_b"]), np.asarray(raw_arrays["f_raw"]),
        np.asarray(verified["p1"]), np.asarray(verified["p2"]),
        seeds=seeds, blocks_per_seed=int(blocks_per_seed), n=int(n))
    if int(sampled["blocks_attempted"]) != int(FROZEN_TRAIN_BLOCKS_TOTAL):
        raise ValueError("derivation sampling budget != frozen 16-block budget")
    if int(sampled["blocks_used"]) != int(FROZEN_TRAIN_BLOCKS_TOTAL):
        raise ValueError(
            "derivation sampling used "
            f"{int(sampled['blocks_used'])} != frozen {int(FROZEN_TRAIN_BLOCKS_TOTAL)}")
    if int(sampled["calls"].get("genie", 0)) != int(FROZEN_TRAIN_GENIE_CALLS):
        raise ValueError("derivation genie-call accounting != frozen 32-genie budget")
    if int(sampled["provenance_violations"]) != 0:
        raise ValueError("derivation provenance violations != 0")
    split = select_empirical_split(
        int(n), sampled["e1_mean"], sampled["h1_mean"],
        sampled["e2_mean"], sampled["h2_mean"], int(k_total))
    k1, k2 = int(split["k1"]), int(split["k2"])
    if k1 + k2 != int(k_total):
        raise ValueError("TRAIN-residual selection K1+K2 != K_total")
    l1_order = np.asarray(split["l1_order"], dtype=np.int64)
    l2_order = np.asarray(split["l2_order"], dtype=np.int64)
    residual = float(split["residual"])
    # Spike order on the TRAIN-pooled mean L2 hazard (shared budget input;
    # the spike adds 0 sampling blocks + 0 genie calls of its own).
    spike = derive_spike_order_8192(sampled["h2_mean"])
    spike_l2_order = np.asarray(spike["spike_l2_order"], dtype=np.int64)
    set_delta = order_set_delta_8192(l2_order, spike_l2_order, int(k2))
    if int(set_delta["size_delta_b_minus_a"]) != 0:
        raise ValueError("A-vs-B disclosed-size delta != 0")
    derivation_common = {
        "program": DERIVATION_PROGRAM_PIN,
        "prior_path": str(prior_path),
        "prior_digest": prior_digest,
        "h1": h1,
        "h2": h2,
        "h_total": h_total,
        "budget_literal": budget_literal,
        "train_seeds": [int(s) for s in seeds],
        "train_blocks_per_seed": int(blocks_per_seed),
        "train_blocks_attempted": int(sampled["blocks_attempted"]),
        "train_blocks_used": int(sampled["blocks_used"]),
        "train_impossible": int(sampled["blocks_impossible"]),
        "train_genie_calls": int(sampled["calls"].get("genie", 0)),
        "provenance_violations": int(sampled["provenance_violations"]),
        "spike_sampling_calls": 0,
        "spike_genie_calls": 0,
        "floor_value": float(FROZEN_FLOOR),
        "alpha": float(FROZEN_ALPHA),
        "hazard_radius_R": int(FROZEN_HAZARD_R),
        "hazard_radius_R_refrozen_for_8192_geometry": True,
        "counts_content_opens": 0,
        "dev_contact": 0,
    }
    construction_doc = {
        "protocol": CONSTRUCTION_PROTOCOL,
        "kind": CONSTRUCTION_KIND,
        "n": int(n),
        "k_total": int(k_total),
        "k1": k1,
        "k2": k2,
        "train_residual": residual,
        "frozen_before_first_dev": True,
        "derivation": derivation_common,
    }
    orders_doc = {
        "protocol": ORDER_PROTOCOL,
        "kind": ORDER_KIND,
        "n": int(n),
        "k_total": int(k_total),
        "k1": k1,
        "k2": k2,
        "l1_order": [int(v) for v in l1_order.tolist()],
        "l2_order": [int(v) for v in l2_order.tolist()],
        "derivation": derivation_common,
    }
    spike_doc = {
        "protocol": SPIKE_ORDER_PROTOCOL,
        "kind": SPIKE_ORDER_KIND,
        "n": int(n),
        "k_total": int(k_total),
        "k1": k1,
        "k2": k2,
        "l1_order": [int(v) for v in l1_order.tolist()],
        "l2_order": [int(v) for v in spike_l2_order.tolist()],
        "derivation": dict(
            derivation_common,
            reused_prior_digest=prior_digest,
            formula_id=str(SPIKE_FORMULA_ID),
            formula_text=str(SPIKE_FORMULA_TEXT),
            cell_convention="TRAIN-pooled mean L2 hazard per 8192-coordinate",
            zero_sampling_attestation=True,
        ),
    }
    out_construction.parent.mkdir(parents=True, exist_ok=True)
    construction_payload = json.dumps(construction_doc, sort_keys=True) + "\n"
    out_construction.write_text(construction_payload, encoding="utf-8")
    orders_payload = json.dumps(orders_doc, sort_keys=True) + "\n"
    out_orders.write_text(orders_payload, encoding="utf-8")
    spike_payload = json.dumps(spike_doc, sort_keys=True) + "\n"
    out_spike.write_text(spike_payload, encoding="utf-8")
    return {
        "construction_path": str(out_construction),
        "construction_digest": hashlib.sha256(
            construction_payload.encode("utf-8")).hexdigest(),
        "order_path": str(out_orders),
        "order_digest": hashlib.sha256(
            orders_payload.encode("utf-8")).hexdigest(),
        "spike_order_path": str(out_spike),
        "spike_order_digest": hashlib.sha256(
            spike_payload.encode("utf-8")).hexdigest(),
        "prior_digest": prior_digest,
        "h1": h1,
        "h2": h2,
        "h_total": h_total,
        "budget_literal": budget_literal,
        "k_total": int(k_total),
        "k1": k1,
        "k2": k2,
        "train_residual": residual,
        "formula_id": str(SPIKE_FORMULA_ID),
        "program": DERIVATION_PROGRAM_PIN,
        "set_delta": set_delta,
        "train_blocks_used": int(sampled["blocks_used"]),
        "train_genie_calls": int(sampled["calls"].get("genie", 0)),
        "counts_content_opens": 0,
        "dev_contact": 0,
        "wall_s": round(float(time.perf_counter() - start), 6),
    }


def verify_construction_file_8192(path, *, expected_digest: str,
                                  expected_prior_digest: str,
                                  expected_k1: int, expected_k2: int,
                                  expected_k_total: int) -> dict:
    """Verify the Stage-A construction/allocation file (gate, worktree-file read only).

    File-bytes sha256 must equal the frozen digest; the document must carry
    the frozen P20T protocol/kind with ``n == 8192``; the K triple must
    equal the replayed in-packet integers; the budget literal must replay
    from recomputed H via the frozen rule; the derivation provenance (prior
    digest + program pin + frozen seeds + 16-block budget + floor/alpha
    pins + R=8 re-freeze) must replay exactly. Any mismatch raises before
    any SC call.
    """
    pins = _require_stage_a_pins()
    if str(expected_digest) != str(pins["construction_digest"]):
        raise ValueError("construction-file digest flag != frozen Stage-A digest")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Stage-A construction file not found: {p}")
    raw = p.read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    if file_digest != str(expected_digest):
        raise ValueError(
            "construction-file bytes sha256 != frozen --construction-digest "
            "(refusing before any SC call)")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except ValueError as exc:
        raise ValueError(f"construction file unreadable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("protocol") != CONSTRUCTION_PROTOCOL:
        raise ValueError("construction file protocol != frozen P20T protocol")
    if doc.get("kind") != CONSTRUCTION_KIND:
        raise ValueError("construction file kind != construction-and-allocation-8192")
    if int(doc.get("n", -1)) != FROZEN_N:
        raise ValueError("construction file n != frozen N")
    if doc.get("frozen_before_first_dev") is not True:
        raise ValueError("construction file not frozen before DEV")
    if int(doc.get("k_total", -1)) != int(expected_k_total):
        raise ValueError("construction file k_total != replayed K_total")
    if int(doc.get("k1", -1)) != int(expected_k1):
        raise ValueError("construction file k1 != replayed K1")
    if int(doc.get("k2", -1)) != int(expected_k2):
        raise ValueError("construction file k2 != replayed K2")
    derivation = doc.get("derivation")
    if not isinstance(derivation, dict):
        raise ValueError("construction file derivation provenance missing")
    if str(derivation.get("prior_digest")) != str(expected_prior_digest):
        raise ValueError("construction derivation prior digest != frozen reuse pin")
    if str(derivation.get("program")) != str(DERIVATION_PROGRAM_PIN):
        raise ValueError("construction derivation program pin != frozen program pin")
    if [int(s) for s in derivation.get("train_seeds", [])] != list(
            FROZEN_DERIVATION_SEEDS):
        raise ValueError("construction derivation seeds != frozen TRAIN seeds")
    if int(derivation.get("train_blocks_used", -1)) != int(
            FROZEN_TRAIN_BLOCKS_TOTAL):
        raise ValueError("construction derivation budget != frozen 16-block budget")
    if int(derivation.get("train_genie_calls", -1)) != int(
            FROZEN_TRAIN_GENIE_CALLS):
        raise ValueError("construction derivation genie != frozen 32-genie budget")
    if float(derivation.get("floor_value", -1.0)) != float(FROZEN_FLOOR):
        raise ValueError("construction derivation floor != frozen floor pin")
    if float(derivation.get("alpha", -1.0)) != float(FROZEN_ALPHA):
        raise ValueError("construction derivation alpha != frozen alpha pin")
    if derivation.get("hazard_radius_R_refrozen_for_8192_geometry") is not True:
        raise ValueError("construction derivation R=8 re-freeze attestation != true")
    # K-rule replay: the budget literal must equal the frozen-rule display
    # from the derivation H (never hand-filled, never from alt-H).
    replay = p20m.verify_budget_literal(
        float(derivation.get("h_total", float("nan"))), int(expected_k_total),
        n=FROZEN_N, target_f=float(FROZEN_TARGET_F))
    if str(replay["literal"]) != str(derivation.get("budget_literal")):
        raise ValueError("construction budget literal != frozen-rule replay")
    if str(derivation.get("budget_literal")) != str(pins["budget_literal"]):
        raise ValueError("construction budget literal != frozen Stage-A literal")
    residual = float(doc.get("train_residual", float("nan")))
    if not np.isfinite(residual):
        raise ValueError("construction TRAIN residual must be finite")
    if abs(residual - float(pins["train_residual"])) > 0.0:
        raise ValueError("construction TRAIN residual != frozen Stage-A residual")
    return {
        "construction_file": str(p),
        "construction_digest": file_digest,
        "n": int(FROZEN_N),
        "k_total": int(expected_k_total),
        "k1": int(expected_k1),
        "k2": int(expected_k2),
        "train_residual": residual,
        "train_blocks_used": int(derivation.get("train_blocks_used", -1)),
        "train_genie_calls": int(derivation.get("train_genie_calls", -1)),
        "prior_digest": str(expected_prior_digest),
        "program": str(DERIVATION_PROGRAM_PIN),
        "verified": True,
    }


def verify_fresh_order_file_8192(path, *, expected_digest: str,
                                 expected_prior_digest: str,
                                 expected_k1: int, expected_k2: int,
                                 expected_k_total: int) -> dict:
    """Verify the Stage-A fresh L1/L2 order file (``fresh_order_identity_A_8192``).

    Worktree-file read only: file-bytes sha256 equality, frozen
    protocol/kind/n, full L1+L2 permutations of 0..8191, K-triple replay,
    derivation provenance (prior digest + program pin + seeds + budget).
    Any mismatch raises before any SC call.
    """
    pins = _require_stage_a_pins()
    if str(expected_digest) != str(pins["order_digest"]):
        raise ValueError("order-file digest flag != frozen Stage-A digest")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Stage-A fresh-order file not found: {p}")
    raw = p.read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    if file_digest != str(expected_digest):
        raise ValueError(
            "order-file bytes sha256 != frozen --order-digest "
            "(refusing before any SC call)")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except ValueError as exc:
        raise ValueError(f"order file unreadable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("protocol") != ORDER_PROTOCOL:
        raise ValueError("order file protocol != frozen P20T protocol")
    if doc.get("kind") != ORDER_KIND:
        raise ValueError("order file kind != fresh-orders-file-8192")
    if int(doc.get("n", -1)) != FROZEN_N:
        raise ValueError("order file n != frozen N")
    try:
        l1_order = np.asarray(doc["l1_order"], dtype=np.int64).ravel()
        l2_order = np.asarray(doc["l2_order"], dtype=np.int64).ravel()
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"order file orders malformed: {exc}") from exc
    if l1_order.shape != (FROZEN_N,) or set(l1_order.tolist()) != set(
            range(FROZEN_N)):
        raise ValueError("order file l1_order is not a permutation of 0..N-1")
    if l2_order.shape != (FROZEN_N,) or set(l2_order.tolist()) != set(
            range(FROZEN_N)):
        raise ValueError("order file l2_order is not a permutation of 0..N-1")
    if int(doc.get("k_total", -1)) != int(expected_k_total):
        raise ValueError("order file k_total != replayed K_total")
    if int(doc.get("k1", -1)) != int(expected_k1):
        raise ValueError("order file k1 != replayed K1")
    if int(doc.get("k2", -1)) != int(expected_k2):
        raise ValueError("order file k2 != replayed K2")
    derivation = doc.get("derivation")
    if not isinstance(derivation, dict):
        raise ValueError("order file derivation provenance missing")
    if str(derivation.get("prior_digest")) != str(expected_prior_digest):
        raise ValueError("order derivation prior digest != frozen reuse pin")
    if str(derivation.get("program")) != str(DERIVATION_PROGRAM_PIN):
        raise ValueError("order derivation program pin != frozen program pin")
    if [int(s) for s in derivation.get("train_seeds", [])] != list(
            FROZEN_DERIVATION_SEEDS):
        raise ValueError("order derivation seeds != frozen TRAIN seeds")
    return {
        "order_file": str(p),
        "order_digest": file_digest,
        "n": int(FROZEN_N),
        "l1_order": np.ascontiguousarray(l1_order),
        "l2_order": np.ascontiguousarray(l2_order),
        "k_total": int(expected_k_total),
        "k1": int(expected_k1),
        "k2": int(expected_k2),
        "prior_digest": str(expected_prior_digest),
        "program": str(DERIVATION_PROGRAM_PIN),
        "verified": True,
    }


def verify_spike_order_file(path, *, expected_digest: str,
                            expected_prior_digest: str,
                            frozen_l1_order, expected_k1: int,
                            expected_k2: int, expected_k_total: int) -> dict:
    """Verify the Stage-A spike-B order file (``spike_order_identity_B_8192``).

    Worktree-file read only: file-bytes sha256 equality, frozen
    protocol/kind/n, spike-L2 permutation of 0..8191, L1-carried check
    against the fresh L1 order, K-triple replay, derivation provenance
    (prior digest + formula-id pin with the R=8 re-freeze + program pin +
    zero-sampling attestation). Any mismatch raises before any SC call.
    Stage B performs zero sampling: this function loads a frozen file,
    never a sampler.
    """
    pins = _require_stage_a_pins()
    if str(expected_digest) != str(pins["spike_order_digest"]):
        raise ValueError("spike-order-file digest flag != frozen Stage-A spike digest")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Stage-A spike-B order file not found: {p}")
    raw = p.read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    if file_digest != str(expected_digest):
        raise ValueError(
            "spike-order-file bytes sha256 != frozen --spike-order-digest "
            "(refusing before any SC call)")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except ValueError as exc:
        raise ValueError(f"spike-order file unreadable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("protocol") != SPIKE_ORDER_PROTOCOL:
        raise ValueError("spike-order file protocol != frozen P20T protocol")
    if doc.get("kind") != SPIKE_ORDER_KIND:
        raise ValueError("spike-order file kind != spike-l2-order-file-8192")
    if int(doc.get("n", -1)) != FROZEN_N:
        raise ValueError("spike-order file n != frozen N")
    try:
        l1_order = np.asarray(doc["l1_order"], dtype=np.int64).ravel()
        l2_order = np.asarray(doc["l2_order"], dtype=np.int64).ravel()
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"spike-order file orders malformed: {exc}") from exc
    if l2_order.shape != (FROZEN_N,) or set(l2_order.tolist()) != set(
            range(FROZEN_N)):
        raise ValueError("spike-order file l2_order is not a permutation of 0..N-1")
    frozen_l1 = np.asarray(frozen_l1_order, dtype=np.int64).ravel()
    if l1_order.shape != (FROZEN_N,) or not np.array_equal(l1_order, frozen_l1):
        raise ValueError("spike-order file l1_order != carried fresh L1 order")
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
    if derivation.get("hazard_radius_R_refrozen_for_8192_geometry") is not True:
        raise ValueError("spike-order R=8 re-freeze attestation != true")
    if str(derivation.get("program")) != str(DERIVATION_PROGRAM_PIN):
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
        "program": str(DERIVATION_PROGRAM_PIN),
        "verified": True,
    }


def order_set_delta_8192(fresh_l2_order, new_l2_order, k2: int) -> dict:
    """Byte-exact A-vs-B disclosed-L2-set delta (the single factor).

    Pure helper (no I/O): the symmetric difference between the fresh-A
    first-K2 prefix and the new-B first-K2 prefix with full rank
    displacement (each member's rank in the other full order). Size-delta
    is exactly 0 by design.
    """
    k2 = int(k2)
    fresh = np.asarray(fresh_l2_order, dtype=np.int64).ravel()
    new = np.asarray(new_l2_order, dtype=np.int64).ravel()
    if fresh.shape != (FROZEN_N,) or new.shape != (FROZEN_N,):
        raise ValueError("order arrays must both be length-8192 permutations")
    set_a = set(int(v) for v in fresh[:k2].tolist())
    set_b = set(int(v) for v in new[:k2].tolist())
    a_minus_b = sorted(set_a - set_b)
    b_minus_a = sorted(set_b - set_a)
    rank_in_new = {int(v): i for i, v in enumerate(new.tolist())}
    rank_in_fresh = {int(v): i for i, v in enumerate(fresh.tolist())}
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
        "b_minus_a_ranks_in_fresh_order": [rank_in_fresh[v] for v in b_minus_a],
    }


def verify_derivation(*, prior, construction_file, order_file,
                      spike_order_file, prior_digest: str,
                      construction_digest: str, order_digest: str,
                      spike_order_digest: str, spike_formula: str,
                      h1: float, h2: float, h_total: float,
                      k1: int, k2: int) -> dict:
    """Replay the reuse + derivation pins from worktree/Stage-A files BEFORE any DEV contact.

    Loads the frozen 2M worktree prior read-only (never the V25 counts
    NPZ, never any pairs parquet): canonical prior digest + H-literal
    recomputation within 1e-12 + ``p_b`` cross-check + floor pins; then the
    Stage-A construction/allocation identity (file-bytes digest +
    sampling-budget attestation + TRAIN-seed pins + (K1,K2) TRAIN-residual
    selection replay + K-rule replay), the fresh-order identity, and the
    spike-B order identity (file-bytes digest + L1-carried + formula-id
    with the R=8 re-freeze + program pin + zero-sampling attestation) with
    the byte-exact A-vs-B set-delta table. Zero sampling here (the frozen
    sampling ran once in ``--derive``). Any replay mismatch raises with DEV
    untouched (DEV read stays 0/1) and no Stage-B request may follow.
    """
    if str(spike_formula) != str(SPIKE_FORMULA_ID):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(order_derivation_identity): "
            "--spike-formula != frozen F-median8 formula-id")
    pins = _require_stage_a_pins()
    if int(k1) != int(pins["k1"]) or int(k2) != int(pins["k2"]):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(k_rule_derived): --k1/--k2 != frozen Stage-A literals")
    if int(k1) + int(k2) != int(pins["k_total"]):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(k_rule_derived): K1+K2 != frozen K_total")
    base = _gate_call(
        "reuse_prior_arrays_identity", verify_session_prior_2m,
        prior, expected_digest=str(prior_digest),
        expected_h1=float(h1), expected_h2=float(h2),
        expected_total=float(h_total))
    construction_pin = _gate_call(
        "new_construction_identity_8192", verify_construction_file_8192,
        str(construction_file), expected_digest=str(construction_digest),
        expected_prior_digest=str(prior_digest),
        expected_k1=int(k1), expected_k2=int(k2),
        expected_k_total=int(k1) + int(k2))
    order_pin = _gate_call(
        "fresh_order_identity_A_8192", verify_fresh_order_file_8192,
        str(order_file), expected_digest=str(order_digest),
        expected_prior_digest=str(prior_digest),
        expected_k1=int(k1), expected_k2=int(k2),
        expected_k_total=int(k1) + int(k2))
    spike_pin = _gate_call(
        "spike_order_identity_B_8192", verify_spike_order_file,
        str(spike_order_file), expected_digest=str(spike_order_digest),
        expected_prior_digest=str(prior_digest),
        frozen_l1_order=np.asarray(order_pin["l1_order"]),
        expected_k1=int(k1), expected_k2=int(k2),
        expected_k_total=int(k1) + int(k2))
    if str(spike_pin.get("program")) != str(DERIVATION_PROGRAM_PIN):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(order_derivation_identity): program pin != frozen pin")
    if str(spike_pin.get("formula_id")) != str(SPIKE_FORMULA_ID):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(order_derivation_identity): formula-id != frozen F-median8 pin")
    set_delta = order_set_delta_8192(
        np.asarray(order_pin["l2_order"]), np.asarray(spike_pin["l2_order"]),
        int(k2))
    if int(set_delta["size_delta_b_minus_a"]) != 0:
        raise N8192PersistenceProbeContractError(
            "BLOCKED(order_set_delta_recorded): B-A disclosed-size delta != 0")
    if int(set_delta["a_disclosed_size"]) != int(k2):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(order_set_delta_recorded): A disclosed size != K2")
    if int(set_delta["b_disclosed_size"]) != int(k2):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(order_set_delta_recorded): B disclosed size != K2")
    return {
        "prior_digest": str(base["digest"]),
        "h1": float(base["h1"]),
        "h2": float(base["h2"]),
        "h_total": float(base["h_total"]),
        "counts_total": int(base["counts_total"]),
        "floor_hits": int(base["floor_hits"]),
        "floor_hit_rate": float(base["floor_hit_rate"]),
        "zero_columns": int(base["zero_columns"]),
        "construction_digest": str(construction_pin["construction_digest"]),
        "train_residual": float(construction_pin["train_residual"]),
        "k_total": int(k1) + int(k2),
        "k1": int(k1),
        "k2": int(k2),
        "budget_literal": str(pins["budget_literal"]),
        "order_digest_A": str(order_pin["order_digest"]),
        "spike_order_digest_B": str(spike_pin["spike_order_digest"]),
        "spike_program": str(spike_pin["program"]),
        "spike_formula_id": str(spike_pin["formula_id"]),
        "set_delta": set_delta,
        "dev_contact": 0,
        "verified": True,
    }


# ---------------------------------------------------------------------------
# Gate family (a)->(g) (frozen section 4 order; cross-file first; every
# refusal lands before any protected content open and before any SC call).
# ---------------------------------------------------------------------------

def verify_dev_source_identity_2m(dev_pairs=None) -> dict:
    """Gate (a): cross-file 2M source identity (FIRST, before any open)."""
    candidate = FROZEN_DEV_PAIRS_PATH if dev_pairs is None else str(dev_pairs)
    if candidate == REFUSED_1M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20T DEV source gate: 1M full-pool path refused "
            f"({REFUSED_1M_DEV_PAIRS_PATH!r}); the entire 1M pool is "
            "fail-closed against P20T DEV selection")
    if candidate == REFUSED_1P5M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20T DEV source gate: 1.5M session path refused "
            f"({REFUSED_1P5M_DEV_PAIRS_PATH!r}); the entire 1.5M session is "
            "fail-closed against P20T DEV selection")
    if candidate != FROZEN_DEV_PAIRS_PATH:
        raise ValueError(
            "frozen point requires dev-pairs="
            f"{FROZEN_DEV_PAIRS_PATH!r}, got {candidate!r}")
    checks = {
        "source": FROZEN_SOURCE == "2M",
        "source_tag": FROZEN_SOURCE_TAG == SOURCE_IDS[FROZEN_SOURCE],
    }
    failing = sorted(name for name, ok in checks.items() if not ok)
    if failing:
        raise ValueError("P20T DEV source identity mismatch: " + ",".join(failing))
    return {
        "source": FROZEN_SOURCE,
        "source_tag": FROZEN_SOURCE_TAG,
        "dev_pairs_path": FROZEN_DEV_PAIRS_PATH,
        "build_manifest_path": (
            "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
            "v13r3fresh_pairs_20260816/type2_2M_20260121_183657/build_manifest.json"),
        "refused_1m_path": REFUSED_1M_DEV_PAIRS_PATH,
        "refused_1p5m_path": REFUSED_1P5M_DEV_PAIRS_PATH,
        "verified": True,
    }


def verify_single_segment_containment(dev_frames_hold=None,
                                      remainder_frames=None) -> dict:
    """Gate (b): intra-file single-segment containment.

    The DEV segment must lie wholly inside HOLD 2916..3644 with zero
    TRAIN/VAL-DEV/HOLD-DEV overlap, else refuse before any protected
    content open. The segment must equal the frozen pair and hold exactly
    one 32-frame block; the remainder must equal the frozen HOLD tail
    3627..3644. No cross-split combining is needed and the D1-A merge
    precedent is NOT invoked.
    """
    hold_pair = (tuple(FROZEN_DEV_FRAMES_HOLD) if dev_frames_hold is None
                 else tuple(opf._as_int(v, "dev-frames-hold", minimum=0)
                            for v in dev_frames_hold))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    hold_first, hold_last = INTRA_FILE_HOLD_FRAME_RANGE
    train_first, train_last = CONSUMED_2M_TRAIN_FRAME_RANGE
    valdev_first, valdev_last = CONSUMED_2M_VAL_DEV_FRAME_RANGE
    holddev_first, holddev_last = CONSUMED_2M_HOLD_DEV_FRAME_RANGE
    dev_first, dev_last = hold_pair
    rem_first, rem_last = rem_pair
    if not (hold_first <= dev_first and dev_last <= hold_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): DEV segment {dev_first}..{dev_last} "
            f"lies outside 2M HOLD {hold_first}..{hold_last}")
    if not (dev_last < train_first or dev_first > train_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): DEV segment {dev_first}..{dev_last} "
            f"overlaps 2M TRAIN {train_first}..{train_last}")
    if not (dev_last < valdev_first or dev_first > valdev_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): DEV segment {dev_first}..{dev_last} "
            f"overlaps consumed 2M VAL DEV {valdev_first}..{valdev_last}")
    if not (dev_last < holddev_first or dev_first > holddev_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): DEV segment {dev_first}..{dev_last} "
            f"overlaps consumed 2M HOLD DEV {holddev_first}..{holddev_last}")
    if hold_pair != tuple(FROZEN_DEV_FRAMES_HOLD):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): dev-frames-hold {hold_pair} != "
            f"frozen {tuple(FROZEN_DEV_FRAMES_HOLD)}")
    if (dev_last - dev_first + 1) != FROZEN_DEV_FRAMES:
        raise ValueError(
            "BLOCKED(dev_block_range_identity): DEV segment holds "
            f"{dev_last - dev_first + 1} != frozen {FROZEN_DEV_FRAMES} frames")
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): remainder-frames {rem_pair} != "
            f"frozen {tuple(FROZEN_REMAINDER_FRAME_RANGE)}")
    if not (dev_last < rem_first or dev_first > rem_last):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): DEV segment overlaps the "
            f"declared remainder {rem_first}..{rem_last}")
    return {
        "dev_frames_hold": [int(dev_first), int(dev_last)],
        "remainder_frames": [int(rem_first), int(rem_last)],
        "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
        "verified": True,
    }


def verify_single_segment_frame_set_identity(dev_frames_hold=None) -> dict:
    """Gate (g, frame part): the exact 32-frame list rule (3595..3626, in order)."""
    hold_pair = (tuple(FROZEN_DEV_FRAMES_HOLD) if dev_frames_hold is None
                 else tuple(opf._as_int(v, "dev-frames-hold", minimum=0)
                            for v in dev_frames_hold))
    frame_list = [int(f) for f in range(hold_pair[0], hold_pair[1] + 1)]
    if frame_list != list(FROZEN_DEV_FRAME_LIST):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): single-segment 32-frame list != "
            "frozen HOLD 3595..3626 rule")
    return {"dev_frame_list": frame_list, "verified": True}


def _ranges_overlap(first_a, last_a, first_b, last_b) -> bool:
    return not (last_a < first_b or first_a > last_b)


def verify_consumed_exclusions_single_segment(dev_frames_hold=None,
                                              remainder_frames=None) -> dict:
    """Gates (c)+(d)+(e): consumed-1M / consumed-1.5M / consumed-2M exclusions.

    The DEV segment must not overlap the entire 1M pool (any
    split/subrange), any 1.5M range (TRAIN 0..1659, VAL 1660..2212, HOLD
    2213..2766), or any consumed 2M range (TRAIN-as-DEV, VAL DEV
    2187..2826, HOLD DEV 2916..3555, P20S merged DEV 2827..2915 +
    3556..3594), including the DEV-vs-build-frames disjointness declaration
    (S2-ii: DEV vs build subset 2M TRAIN 0..2186 with the frame sets
    above). Frame integers alone are never identity: the cross-file gate
    (a) runs first.
    """
    hold_pair = (tuple(FROZEN_DEV_FRAMES_HOLD) if dev_frames_hold is None
                 else tuple(opf._as_int(v, "dev-frames-hold", minimum=0)
                            for v in dev_frames_hold))
    dev_first, dev_last = hold_pair
    refused: list[str] = []
    # 1M pool: excluded by the cross-file source gate (a) path refusal (the
    # entire 1M pool is fail-closed against P20T DEV selection by name);
    # the frame-range exclusions below cover every consumed numeric range.
    for label, (first, last) in (
            ("consumed-1.5M TRAIN 0..1659", CONSUMED_1P5M_TRAIN_FRAME_RANGE),
            ("consumed-1.5M VAL 1660..2212", CONSUMED_1P5M_VAL_FRAME_RANGE),
            ("consumed-1.5M HOLD 2213..2766", CONSUMED_1P5M_HOLD_FRAME_RANGE),
            ("consumed-2M TRAIN-as-DEV 0..2186", CONSUMED_2M_TRAIN_FRAME_RANGE),
            ("consumed-2M VAL DEV 2187..2826", CONSUMED_2M_VAL_DEV_FRAME_RANGE),
            ("consumed-2M HOLD DEV 2916..3555",
             CONSUMED_2M_HOLD_DEV_FRAME_RANGE),
            ("P20S merged DEV VAL 2827..2915", (2827, 2915)),
            ("P20S merged DEV HOLD 3556..3594", (3556, 3594))):
        if _ranges_overlap(dev_first, dev_last, first, last):
            refused.append(label)
    if refused:
        raise ValueError(
            "BLOCKED(dev_block_range_identity): DEV segment overlaps consumed "
            "range(s): " + ",".join(refused))
    disjoint = not _ranges_overlap(
        dev_first, dev_last, *FROZEN_BUILD_FRAME_RANGE)
    if not disjoint:
        raise ValueError(
            "BLOCKED(dev_block_range_identity): DEV overlaps build frames "
            f"{list(FROZEN_BUILD_FRAME_RANGE)} (S2-ii)")
    return {
        "dev_frames_hold": [int(dev_first), int(dev_last)],
        "build_frames": list(FROZEN_BUILD_FRAME_RANGE),
        "disjoint": True,
        "consumed_1m_excluded_by_source_gate": True,
        "consumed_1p5m_ranges": [
            list(CONSUMED_1P5M_TRAIN_FRAME_RANGE),
            list(CONSUMED_1P5M_VAL_FRAME_RANGE),
            list(CONSUMED_1P5M_HOLD_FRAME_RANGE)],
        "consumed_2m_ranges": [
            list(CONSUMED_2M_TRAIN_FRAME_RANGE),
            list(CONSUMED_2M_VAL_DEV_FRAME_RANGE),
            list(CONSUMED_2M_HOLD_DEV_FRAME_RANGE)],
        "verified": True,
    }


def form_single_segment_block(table, *, dev_frames_hold=FROZEN_DEV_FRAMES_HOLD,
                              block_frames: int = FROZEN_BLOCK_FRAMES,
                              remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
                              ) -> dict:
    """Deterministic single-segment development validation plus slicing.

    Selects the HOLD-tail DEV segment from the 2M table, validates exact
    frames, pair_idx exactly 0..255 per frame, sorted (frame_id, pair_idx)
    order, into ONE 8192-pair block, and validates the declared HOLD
    remainder from the pool (counted, never decoded). The 1.5M
    stub/remainder populations are recorded from the frozen constants
    (counted, never contacted beyond counting).
    """
    try:
        hold_pair = tuple(opf._as_int(v, "dev-frames-hold", minimum=0)
                          for v in dev_frames_hold)
    except TypeError as exc:
        raise TypeError(f"dev-frames-hold must be a pair of integers: {exc}") from exc
    if hold_pair != tuple(FROZEN_DEV_FRAMES_HOLD):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"dev-frames-hold {hold_pair} != frozen {tuple(FROZEN_DEV_FRAMES_HOLD)}")
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise N8192PersistenceProbeContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"block-frames {block_frames} != frozen {FROZEN_BLOCK_FRAMES}")
    try:
        rem_pair = tuple(opf._as_int(v, "remainder-frames", minimum=0)
                         for v in remainder_frames)
    except TypeError as exc:
        raise TypeError(f"remainder-frames must be a pair of integers: {exc}") from exc
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"remainder-frames {rem_pair} != frozen {tuple(FROZEN_REMAINDER_FRAME_RANGE)}")
    try:
        frame_id = np.asarray(table["frame_id"], dtype=np.int64)
        pair_idx = np.asarray(table["pair_idx"], dtype=np.int64)
        alice = np.asarray(table["alice_symbol"], dtype=np.int64)
        bob = np.asarray(table["bob_symbol"], dtype=np.int64)
    except (KeyError, TypeError, ValueError) as exc:
        raise N8192PersistenceProbeContractError(
            f"BLOCKED(dev_population_exact): loader frame is malformed: {exc}"
        ) from exc
    if not (frame_id.shape == pair_idx.shape == alice.shape == bob.shape) \
            or frame_id.ndim != 1:
        raise N8192PersistenceProbeContractError(
            "BLOCKED(dev_population_exact): column shapes disagree")
    for name, values in (("alice_symbol", alice), ("bob_symbol", bob)):
        if values.size == 0 or values.min() < 0 or values.max() >= N_BOB:
            raise N8192PersistenceProbeContractError(
                f"BLOCKED(dev_population_exact): {name} outside 0..{N_BOB - 1}")
    seg_first, seg_last = hold_pair
    selected = (frame_id >= seg_first) & (frame_id <= seg_last)
    rows = int(np.sum(selected))
    if rows == 0:
        raise N8192PersistenceProbeContractError(
            "BLOCKED(dev_population_exact): no rows in the frozen HOLD-tail range")
    seg_frame = frame_id[selected]
    seg_pair = pair_idx[selected]
    seg_alice = alice[selected]
    seg_bob = bob[selected]
    unique_frames = np.unique(seg_frame)
    if (unique_frames.size != FROZEN_DEV_FRAMES
            or int(unique_frames[0]) != seg_first
            or int(unique_frames[-1]) != seg_last):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(dev_population_exact): HOLD-tail frames "
            f"{unique_frames.size} with range {int(unique_frames[0])}.."
            f"{int(unique_frames[-1])} != frozen {FROZEN_DEV_FRAMES} with range "
            f"{seg_first}..{seg_last}")
    if rows != FROZEN_DEV_FRAMES * FROZEN_PAIRS_PER_FRAME:
        raise N8192PersistenceProbeContractError(
            f"BLOCKED(dev_population_exact): HOLD-tail rows {rows} != frozen "
            f"{FROZEN_DEV_FRAMES * FROZEN_PAIRS_PER_FRAME}")
    order = np.lexsort((seg_pair, seg_frame))
    seg_frame = seg_frame[order]
    seg_pair = seg_pair[order]
    seg_alice = seg_alice[order]
    seg_bob = seg_bob[order]
    expected_pair = np.tile(
        np.arange(FROZEN_PAIRS_PER_FRAME, dtype=np.int64), FROZEN_DEV_FRAMES)
    if not np.array_equal(seg_pair, expected_pair):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(dev_population_exact): HOLD-tail pair_idx is not exactly "
            "0..255 per frame")
    if [int(f) for f in range(seg_first, seg_last + 1)] != list(
            FROZEN_DEV_FRAME_LIST):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(dev_block_range_identity): single-segment 32-frame list != "
            "frozen HOLD 3595..3626 rule")
    rem_first, rem_last = rem_pair
    remainder_rows = (frame_id >= rem_first) & (frame_id <= rem_last)
    remainder_frame_ids = frame_id[remainder_rows]
    if int(np.sum(remainder_rows)) != FROZEN_REMAINDER_SYMBOLS:
        raise N8192PersistenceProbeContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder rows "
            f"{int(np.sum(remainder_rows))} != frozen {FROZEN_REMAINDER_SYMBOLS}")
    if (np.unique(remainder_frame_ids).size != FROZEN_REMAINDER_FRAMES
            or int(remainder_frame_ids.min()) != rem_first
            or int(remainder_frame_ids.max()) != rem_last):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder frames "
            f"!= frozen {rem_first}..{rem_last} ({FROZEN_REMAINDER_FRAMES} frames)")
    check = verify_single_segment_containment(hold_pair, rem_pair)
    if not check["verified"]:
        raise N8192PersistenceProbeContractError("BLOCKED(dev_block_range_identity)")
    check_frames = verify_single_segment_frame_set_identity(hold_pair)
    if not check_frames["verified"]:
        raise N8192PersistenceProbeContractError("BLOCKED(dev_block_range_identity)")
    check2 = verify_consumed_exclusions_single_segment(hold_pair, rem_pair)
    if not check2["verified"]:
        raise N8192PersistenceProbeContractError("BLOCKED(dev_block_range_identity)")
    block = {
        "block_index": 0,
        "segments": [list(hold_pair)],
        "frame_start": int(seg_first),
        "frame_end": int(seg_last),
        "frame_count": int(FROZEN_BLOCK_FRAMES),
        "hold_frames": int(FROZEN_DEV_FRAMES),
        "frame_list": [int(f) for f in range(seg_first, seg_last + 1)],
        "labels": seg_alice.copy(),
        "bob": seg_bob.copy(),
        "high": (seg_alice // Q).astype(np.int64),
        "low": (seg_alice % Q).astype(np.int64),
    }
    if int(block["labels"].size) != FROZEN_SYMBOLS_PER_BLOCK:
        raise N8192PersistenceProbeContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): single-segment block holds "
            f"{int(block['labels'].size)} pairs != {FROZEN_SYMBOLS_PER_BLOCK}")
    return {
        "dev_segments": [list(hold_pair)],
        "dev_frames": int(FROZEN_DEV_FRAMES),
        "dev_pairs": int(seg_frame.size),
        "blocks": [block],
        "dev_frame_list": [int(f) for f in range(seg_first, seg_last + 1)],
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


def n8192_persistence_probe_2m_seed_bits(master: int, n: int, arm: str,
                                         block_index: int,
                                         *, bit_length: int | None = None,
                                         ) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P20T domain)."""
    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P20T seed domain: {arm!r}")
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


def n8192_block_events(n: int, spec, block_index: int, frame_start: int,
                       record) -> list:
    """Per-record disclosure/tag events feeding the independent recount."""
    events = [{
        "event_type": "disclosed_block",
        "arm": spec.name,
        "block_index": int(block_index),
        "frame_start": int(frame_start),
        "key_dependent_bits": int(record.get("actual_key_dependent_bits", 0)),
        "public_control_bits": int(record.get("actual_public_control_bits", 0)),
    }]
    if record.get("tag_invoked"):
        events.append({
            "event_type": "verification_tag",
            "arm": spec.name,
            "block_index": int(block_index),
            "frame_start": int(frame_start),
            "key_dependent_bits": 0,
            "public_control_bits": int(FROZEN_PUBLIC_CONTROL_BITS),
        })
    return events


# ---------------------------------------------------------------------------
# (d7) Mandatory recorders (recording-only, post-decode; same caps/formulas
# as P20Q section 7 with the in-packet K2 pin + N=8192 sizing). The P20Q
# ``_ir_hazard_diagnostics`` code point is the carried-over callsite
# pattern for the section 7 recorder extension.
# ---------------------------------------------------------------------------

def _l2_hazard_diagnostics_8192(*, block, view, p2_arm, counts_arr, l2_order,
                                k2, first_error, field=None,
                                low_hat=None) -> dict:
    """P20T nine-scalar recorder (same semantics as the accepted 2M recorder).

    Called after every SC call for the record has completed (after tag
    scoring) from the record writers at the carried-over P20Q code point.
    Reads truth (and the arm table) for RECORDING ONLY; its outputs are
    written into the record dict and are never passed to any decoder,
    metric builder, disclosure or order decision. Differences vs the
    accepted 2M recorder: the gated prefix length is the in-packet K2
    (never 6746) and the block length is 8192 (via the view, never
    32768); floor 1e-15 and hazard radius R=8 (re-frozen) are unchanged.
    """
    pins = _require_stage_a_pins()
    if int(k2) != int(pins["k2"]):
        raise ValueError(
            "hazard instrumentation requires the gated prefix length "
            f"{pins['k2']}, got {int(k2)}")
    bob = np.asarray(view["bob"], dtype=np.int64)
    high_true = np.asarray(view["high"], dtype=np.int64)
    low_true = np.asarray(view["low"], dtype=np.int64)
    n = int(bob.size)
    if int(n) != int(FROZEN_N):
        raise ValueError(
            f"hazard instrumentation requires the full block N={FROZEN_N}, "
            f"got {int(n)}")
    order = np.asarray(l2_order, dtype=np.int64)
    if order.shape != (n,):
        raise ValueError(
            f"l2_order must be a length-{n} natural block index permutation, "
            f"got shape {order.shape}")
    prefix = order[:int(k2)]
    p2 = np.asarray(p2_arm, dtype=np.float64)
    raw_p2 = _raw_p2_from_counts(counts_arr)
    diag = {
        "l2_order_digest": None,
        "l2_prefix_len": int(k2),
        "l2_fail_in_prefix": None,
        "l2_fail_hazard_bits": None,
        "l2_fail_nbhd_mean_bits": None,
        "l2_prefix_hazard_mean_bits": None,
        "l2_fail_nbhd_floor_frac": None,
        "l2_prefix_floor_frac": None,
        "l2_fail_in_prefix_u_domain": None,
    }
    prefix_hazard = _hazard_bits(p2, high_true[prefix], bob[prefix], low_true[prefix])
    prefix_raw = raw_p2[high_true[prefix], bob[prefix], low_true[prefix]]
    diag["l2_prefix_hazard_mean_bits"] = float(np.mean(prefix_hazard))
    diag["l2_prefix_floor_frac"] = float(np.mean(prefix_raw < FROZEN_FLOOR))
    if first_error.get("first_error_layer") == "L2":
        pos = first_error.get("first_error_coord")
        if pos is None or not (0 <= int(pos) < n):
            raise ValueError(
                f"L2 failure requires a valid natural block symbol index, got {pos!r}")
        pos = int(pos)
        u1_cond = view.get("u1_cond")
        if u1_cond is None:
            raise ValueError("L2 failure requires the U1_cond view for the failing cell")
        u1_cond = np.asarray(u1_cond, dtype=np.int64)
        if u1_cond.shape != (n,):
            raise ValueError(f"view u1_cond must be length {n}, got {u1_cond.shape}")
        mask = np.zeros(n, dtype=bool)
        mask[prefix] = True
        diag["l2_fail_in_prefix"] = bool(mask[pos])
        diag["l2_fail_hazard_bits"] = float(
            _hazard_bits(p2, u1_cond[pos:pos + 1], bob[pos:pos + 1],
                         low_true[pos:pos + 1])[0])
        lo = max(0, pos - int(FROZEN_HAZARD_R))
        hi = min(n - 1, pos + int(FROZEN_HAZARD_R))
        idx = np.arange(lo, hi + 1, dtype=np.int64)
        diag["l2_fail_nbhd_mean_bits"] = float(np.mean(
            _hazard_bits(p2, u1_cond[idx], bob[idx], low_true[idx])))
        nbhd_raw = raw_p2[u1_cond[idx], bob[idx], low_true[idx]]
        diag["l2_fail_nbhd_floor_frac"] = float(np.mean(nbhd_raw < FROZEN_FLOOR))
        if field is None or low_hat is None:
            raise ValueError(
                "U-domain cross-check requires the GF32 field and the decoded "
                "L2 hat under an L2 failure")
        u2_true = np.asarray(view["u2"], dtype=np.int64)
        if u2_true.shape != (n,):
            raise ValueError(f"view u2 must be length {n}, got {u2_true.shape}")
        u2_hat = polar_transform(
            np.asarray(low_hat, dtype=np.int64), field=field, alpha=ALPHA)
        mismatch = np.flatnonzero(np.asarray(u2_hat, dtype=np.int64) != u2_true)
        if mismatch.size == 0:
            raise ValueError(
                "U-domain first-mismatch index absent under an L2 failure")
        diag["l2_fail_in_prefix_u_domain"] = bool(mask[int(mismatch[0])])
    return diag


def _arm_order_digest(arm_name: str) -> str:
    """Arm-specific L2 order digest (fresh-A on A/O, spike on B)."""
    pins = _require_stage_a_pins()
    if arm_name in ("A_anchor_frozen_order_equivalent", "O_true_l1_oracle"):
        return str(pins["order_digest"])
    if arm_name in ("B_spike_local_order",):
        return str(pins["spike_order_digest"])
    raise ValueError(f"unknown frozen arm: {arm_name!r}")


def _nine_scalars_for_arm(*, arm_name, block, view, p2_arm, counts_arr,
                          l2_order, k2, first_error, field, low_hat) -> dict:
    """Nine-scalar recorder with the arm-specific order digest.

    Calls the P20T nine-scalar recorder read-only with the record's OWN
    order array (fresh-A on A/O, spike on B); only the recorded
    ``l2_order_digest`` label is arm-specific.
    """
    nine = _l2_hazard_diagnostics_8192(
        block=block, view=view, p2_arm=p2_arm, counts_arr=counts_arr,
        l2_order=l2_order, k2=int(k2), first_error=first_error,
        field=field, low_hat=low_hat)
    nine["l2_order_digest"] = _arm_order_digest(arm_name)
    return nine


def _ir_hazard_diagnostics_8192(*, view, p2_arm, l2_order, k2, first_error,
                                prefix_mean) -> dict:
    """P20T mandatory IR recorder: IR-1..IR-4 (P20Q-identical) + IR-5 refs.

    Called after every SC call for the record has completed (after tag
    scoring) alongside the nine carried scalars (the P20Q
    ``_ir_hazard_diagnostics`` code point is the carried-over callsite
    pattern). Reads truth (and the arm table) for RECORDING ONLY; its
    outputs are written into the record dict and are never passed to any
    decoder, metric builder, disclosure or order decision. The record's OWN
    order (fresh-A on A/O, spike on B) splits every prefix flag.
    Differences vs P20S: the gated prefix length is the in-packet K2 and
    the block length is 8192 (never 6746/32768).

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
    - IR-5 N=8192-sized is NOT inline here: the full-block 8192 series are
      written by ``_ir5_full_block_writer_8192`` to binary ``.bin`` files +
      the ``ir5full-v1`` manifest (never text-JSON float dumps); the record
      carries manifest REFERENCES only.
    """
    pins = _require_stage_a_pins()
    if int(k2) != int(pins["k2"]):
        raise ValueError(
            "IR instrumentation requires the gated prefix length "
            f"{pins['k2']}, got {int(k2)}")
    bob = np.asarray(view["bob"], dtype=np.int64)
    high_true = np.asarray(view["high"], dtype=np.int64)
    low_true = np.asarray(view["low"], dtype=np.int64)
    n = int(bob.size)
    if int(n) != int(FROZEN_N):
        raise ValueError(
            f"IR instrumentation requires the full block N={FROZEN_N}, got {int(n)}")
    order = np.asarray(l2_order, dtype=np.int64)
    if order.shape != (n,):
        raise ValueError(
            f"l2_order must be a length-{n} natural block index permutation, "
            f"got shape {order.shape}")
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
                f"L2 failure requires a valid natural block symbol index, got {pos!r}")
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
    return out


def _ir5_full_block_arrays_8192(*, view, p2_arm, l2_order, k2, low_hat,
                                field) -> dict:
    """Full-block IR-5 arrays at N=8192 (recording-only, post-decode).

    ``hazards_f32``: true-cell ``-log2`` mass in natural block order under
    the record's own arm table (``u1_cond`` from the view, else the true
    high); ``inprefix_u8``: X-domain disclosed-prefix flags under the
    record's OWN order (fresh-A on A/O, spike on B); ``inu_u8``:
    U-domain mismatch flags (``u2_hat`` vs ``u2_true``; all-zero when no
    U-domain estimate exists, i.e. ``low_hat`` is None). All shapes
    (8192,). Truth enters for RECORDING ONLY and never flows back into
    any decoder input.
    """
    pins = _require_stage_a_pins()
    if int(k2) != int(pins["k2"]):
        raise ValueError(
            "IR-5 instrumentation requires the gated prefix length "
            f"{pins['k2']}, got {int(k2)}")
    bob = np.asarray(view["bob"], dtype=np.int64)
    high_true = np.asarray(view["high"], dtype=np.int64)
    low_true = np.asarray(view["low"], dtype=np.int64)
    n = int(bob.size)
    if int(n) != int(IR5_FULL_N):
        raise ValueError(
            f"IR-5 instrumentation requires the full block N={IR5_FULL_N}, got {int(n)}")
    order = np.asarray(l2_order, dtype=np.int64)
    if order.shape != (n,):
        raise ValueError(
            f"l2_order must be a length-{n} natural block index permutation, "
            f"got shape {order.shape}")
    prefix = order[:int(k2)]
    p2 = np.asarray(p2_arm, dtype=np.float64)
    u1_cond = view.get("u1_cond")
    if u1_cond is None:
        u1_cond = high_true
    u1_cond = np.asarray(u1_cond, dtype=np.int64)
    if u1_cond.shape != (n,):
        raise ValueError(f"view u1_cond must be length {n}, got {u1_cond.shape}")
    hazards = _hazard_bits(p2, u1_cond, bob, low_true)
    if hazards.shape != (n,) or not np.isfinite(
            np.asarray(hazards, dtype=np.float64)).all():
        raise ValueError("IR-5 full-block hazards must be finite length-8192")
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


def _ir5_full_block_writer_8192(*, out_dir, arm_name, block_index, arrays,
                                order_digest) -> dict:
    """Write the three N=8192 IR-5 ``.bin`` files (fail-if-present) + record refs.

    Called post-decode (after tag scoring) alongside the nine carried
    scalars and the IR-1..IR-4 recorder (the P20Q ``_ir_hazard_diagnostics``
    code point is the carried-over callsite pattern). Binary ``.bin`` +
    JSON manifest ONLY — never text-JSON float dumps, never
    npz/npy/parquet. Per-record total is 48 KiB (under the 64 KiB budget).
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
        raise ValueError("IR-5 hazards must be 8192 float32-LE")
    if inprefix.shape != (IR5_FULL_N,) or inu.shape != (IR5_FULL_N,):
        raise ValueError("IR-5 flag series must both be length 8192 uint8")
    payloads = (
        (f"{prefix}_hazard_bits_f32le.bin", hazards.tobytes()),
        (f"{prefix}_inprefix_u8.bin", inprefix.tobytes()),
        (f"{prefix}_inu_u8.bin", inu.tobytes()),
    )
    if len(payloads[0][1]) != IR5_HAZARD_BYTES:
        raise ValueError("IR-5 hazard payload must be exactly 32768 B")
    if len(payloads[1][1]) != IR5_FLAG_BYTES or len(payloads[2][1]) != IR5_FLAG_BYTES:
        raise ValueError("IR-5 flag payloads must each be exactly 8192 B")
    if sum(len(p[1]) for p in payloads) > IR5_PER_RECORD_BUDGET_BYTES:
        raise ValueError("IR-5 per-record payload exceeds the 64 KiB budget")
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
    """``ir5_full_manifest_identity`` gate: nine N=8192 ``.bin`` files byte-present.

    The ``ir5full-v1`` manifest must list exactly the nine frozen files
    with per-file sha256 + shape + dtype + endianness + order-identity +
    record linkage; every digest is recomputed from disk and must match,
    every file must respect the ~2 MB evidence-size rule.
    """
    pins = _require_stage_a_pins()
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
            raise ValueError(f"IR-5 entry {name}: shape != [8192]")
        if str(entry.get("dtype")) != str(dtype):
            raise ValueError(f"IR-5 entry {name}: dtype != {dtype}")
        if str(entry.get("endianness")) != str(endian):
            raise ValueError(f"IR-5 entry {name}: endianness != little")
        if str(entry.get("order_identity")) not in (
                str(pins["order_digest"]), str(pins["spike_order_digest"])):
            raise ValueError(f"IR-5 entry {name}: order_identity != fresh-A/spike digest")
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

    Same caps/formulas/nullability as the accepted P20Q gate at the
    in-packet K2/N=8192 pins; records carry manifest REFERENCES (file
    names + digests + ``ir5full-v1`` + total length) instead of inline
    float arrays (file-byte presence + digest equality is enforced by the
    ``ir5_full_manifest_identity`` gate).
    """
    pins = _require_stage_a_pins()
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
        if str(record.get("l2_order_digest")) not in (
                str(pins["order_digest"]), str(pins["spike_order_digest"])):
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
    """Descriptive within-N Q-G1/Q-G2 quantities (never thresholds, never verdicts)."""
    completed = [r for r in records if str(r.get("outcome")) != "resource_abort"]
    ir2_all, ir2_a, ir2_b, ir2_oracle = [], [], [], []
    ir1_rows, ir3_rows, ir4_rows = [], [], []
    for record in completed:
        pct = record.get("ir2_first_error_hazard_rank_pct")
        arm = str(record.get("arm"))
        if pct is not None:
            pct = float(pct)
            ir2_all.append(pct)
            if arm == "A_anchor_frozen_order_equivalent":
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
        "within_n_only": True,
        "cross_n_inference": False,
        "ir2_rank_pct_all": _dist(ir2_all),
        "ir2_rank_pct_a_operational": _dist(ir2_a),
        "ir2_rank_pct_b_operational": _dist(ir2_b),
        "ir2_rank_pct_oracle": _dist(ir2_oracle),
        "ir1_histogram_rows": ir1_rows,
        "ir3_threshold_rows": ir3_rows,
        "ir4_topk_rows": ir4_rows,
        "ir5_n8192_sized_full_block": True,
        "ir5_format_version": str(IR5_FORMAT_VERSION),
        "ir5_full_n": int(IR5_FULL_N),
        "records_completed": len(completed),
    }


def hazard_instrumentation_complete(records) -> bool:
    """All nine section 7 scalars present with frozen nullability per record.

    Same nullability semantics as the accepted gate; the order-digest rule
    is arm-specific (fresh-A digest on A/O records, spike digest on B
    records) with the gated in-packet K2 prefix length on every completed
    record.
    """
    pins = _require_stage_a_pins()
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
        if int(record.get("l2_prefix_len", -1)) != int(pins["k2"]):
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
    counting vocabulary is out of scope for this packet by form, and the
    A-vs-B factor lives in the byte-exact order set-delta plus the
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
# with the arm-specific order digest + IR-1..IR-5 at N=8192). The P20Q
# ``_ir_hazard_diagnostics`` callsite pattern is carried over; the IR call
# sits directly beside the nine-scalar call, post-decode.
# ---------------------------------------------------------------------------

def _base_record_fields(*, spec, arm_index, block, scoring, oracle, k_total,
                        budget_literal, prior_digest, order_digest) -> dict:
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
        "budget_rule_replayed": True,
        "construction_digest_8192": str(FROZEN_CONSTRUCTION_DIGEST_8192),
        "prior_digest": str(prior_digest),
        "l1_order_digest": str(FROZEN_ORDER_DIGEST_A_8192),
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
                        k_total, budget_literal, prior_digest,
                        order_digest, counts_arr, p1, p2, l2_order, n, view,
                        field, diag=None, error=None, ir5_dir) -> dict:
    pins = _require_stage_a_pins()
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=False,
        k_total=k_total, budget_literal=budget_literal, prior_digest=prior_digest,
        order_digest=order_digest)
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
        counts_arr=counts_arr, l2_order=l2_order, k2=int(pins["k2"]),
        first_error=first_error, field=field, low_hat=result.low_hat)
    record.update(nine)
    record.update(_ir_hazard_diagnostics_8192(
        view=view_arm, p2_arm=p2, l2_order=l2_order, k2=int(pins["k2"]),
        first_error=first_error,
        prefix_mean=nine["l2_prefix_hazard_mean_bits"]))
    # IR-5 N=8192-sized full-block writer (d9): recording-only, post-decode.
    # Truth enters for RECORDING ONLY and never flows back into any
    # decoder input; the record carries manifest REFERENCES only.
    ir5_arrays = _ir5_full_block_arrays_8192(
        view=view_arm, p2_arm=p2, l2_order=l2_order, k2=int(pins["k2"]),
        low_hat=result.low_hat, field=field)
    record.update(_ir5_full_block_writer_8192(
        out_dir=ir5_dir, arm_name=spec.name,
        block_index=int(block["block_index"]), arrays=ir5_arrays,
        order_digest=order_digest))
    return record


def _control_record(result, *, spec, arm_index, block, scoring, resources,
                    k_total, budget_literal, prior_digest,
                    order_digest, counts_arr, p1, p2, l2_order, n, view,
                    field, diag=None, error=None, ir5_dir) -> dict:
    pins = _require_stage_a_pins()
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=True,
        k_total=k_total, budget_literal=budget_literal, prior_digest=prior_digest,
        order_digest=order_digest)
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
        counts_arr=counts_arr, l2_order=l2_order, k2=int(pins["k2"]),
        first_error=first_error, field=field, low_hat=result.low_hat)
    record.update(nine)
    record.update(_ir_hazard_diagnostics_8192(
        view=view_arm, p2_arm=p2, l2_order=l2_order, k2=int(pins["k2"]),
        first_error=first_error,
        prefix_mean=nine["l2_prefix_hazard_mean_bits"]))
    # IR-5 N=8192-sized full-block writer (d9): recording-only, post-decode.
    ir5_arrays = _ir5_full_block_arrays_8192(
        view=view_arm, p2_arm=p2, l2_order=l2_order, k2=int(pins["k2"]),
        low_hat=result.low_hat, field=field)
    record.update(_ir5_full_block_writer_8192(
        out_dir=ir5_dir, arm_name=spec.name,
        block_index=int(block["block_index"]), arrays=ir5_arrays,
        order_digest=order_digest))
    return record


def _abort_record(*, spec, arm_index, block, k_total, budget_literal,
                  prior_digest, order_digest) -> dict:
    pins = _require_stage_a_pins()
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
        "budget_rule_replayed": True,
        "construction_digest_8192": str(FROZEN_CONSTRUCTION_DIGEST_8192),
        "prior_digest": str(prior_digest),
        "l1_order_digest": str(FROZEN_ORDER_DIGEST_A_8192),
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
            else (int(pins["k2"]) if field == "l2_prefix_len" else None)
        )
    for field in IR_FIELDS:
        record[field] = None
    return record


# ---------------------------------------------------------------------------
# Stage-B integrity gates (frozen section 9 order; all true or BLOCKED).
# ---------------------------------------------------------------------------

def _integrity_gates(*, n, k1, k2, k_total, arms, identity, manifest,
                     dev_source_pin, dev_pin, disjoint_pin, construction_pin,
                     order_pin_A,
                     spike_order_pin_B, set_delta, formation, records, events,
                     calls, incremental, accounting, provenance_violations,
                     cap, wall_s, resource_stop, session_prior_verified,
                     alt_recomputed, hazard_pin, prior_stat_before,
                     prior_stat_after, dev_stat_before, dev_stat_after,
                     registered_paths, opened_paths, ir5_manifest, out_root,
                     final: bool) -> dict:
    pins = _require_stage_a_pins()
    gates: dict = {}
    gates["predecessor_r1_root_identity"] = bool(
        identity is not None and manifest is not None
        and str(identity.get("predecessor_label", "")) == str(
            FROZEN_PREDECESSOR_LABEL))
    gates["reuse_prior_arrays_identity"] = bool(
        session_prior_verified is not None
        and bool(session_prior_verified.get("passed")))
    gates["new_construction_identity_8192"] = bool(
        order_pin_A is not None and bool(order_pin_A.get("verified"))
        and spike_order_pin_B is not None
        and bool(spike_order_pin_B.get("verified"))
        and str(order_pin_A.get("program")) == str(DERIVATION_PROGRAM_PIN))
    gates["fresh_order_identity_A_8192"] = bool(
        order_pin_A is not None and bool(order_pin_A.get("verified"))
        and str(order_pin_A.get("order_digest")) == str(pins["order_digest"]))
    gates["spike_order_identity_B_8192"] = bool(
        spike_order_pin_B is not None and bool(spike_order_pin_B.get("verified"))
        and str(spike_order_pin_B.get("spike_order_digest"))
        == str(pins["spike_order_digest"]))
    gates["order_derivation_identity"] = bool(
        spike_order_pin_B is not None
        and str(spike_order_pin_B.get("program")) == str(DERIVATION_PROGRAM_PIN)
        and str(spike_order_pin_B.get("formula_id")) == str(SPIKE_FORMULA_ID))
    try:
        recomputed = p20m.verify_budget_literal(
            float(FROZEN_H_TOTAL), int(k_total), n=FROZEN_N,
            target_f=FROZEN_TARGET_F)
        gates["k_rule_derived"] = bool(
            int(k_total) == int(pins["k_total"])
            and int(k1) == int(pins["k1"]) and int(k2) == int(pins["k2"])
            and int(k1) + int(k2) == int(k_total)
            and int(recomputed["k_total"]) == int(pins["k_total"])
            and str(hazard_pin.get("budget_literal")) == str(pins["budget_literal"]))
    except (AttributeError, TypeError, ValueError):
        gates["k_rule_derived"] = False
    gates["target_population_contract"] = bool(
        session_prior_verified is not None
        and bool(session_prior_verified.get("passed")))
    try:
        population_ok = (
            int(formation["dev_frames"]) == FROZEN_DEV_FRAMES
            and int(formation["dev_pairs"]) == FROZEN_DEV_PAIRS
            and [list(s) for s in formation["dev_segments"]]
            == [list(FROZEN_DEV_FRAMES_HOLD)]
            and list(formation["dev_frame_list"]) == list(FROZEN_DEV_FRAME_LIST)
        )
    except (KeyError, TypeError, ValueError):
        population_ok = False
    gates["dev_population_exact"] = bool(population_ok)
    try:
        counted = formation["counted_1p5m_never_decoded"]
        stub_symbols = (int(FROZEN_1P5M_VAL_STUB_SYMBOLS)
                        + int(FROZEN_1P5M_HOLD_REMAINDER_SYMBOLS))
        stub_frames = (int(FROZEN_1P5M_VAL_STUB_FRAMES)
                       + int(FROZEN_1P5M_HOLD_REMAINDER_FRAMES))
        blocks_ok = (
            len(formation["blocks"]) == FROZEN_BLOCK_COUNT
            and formation["remainder"]["used"] is False
            and int(formation["remainder"]["frames"]) == FROZEN_REMAINDER_FRAMES
            and int(formation["remainder"]["symbols"]) == FROZEN_REMAINDER_SYMBOLS
            and int(formation["remainder"]["frame_start"]) == int(
                FROZEN_REMAINDER_FRAME_RANGE[0])
            and counted["used"] is False
            and list(counted["val_stub_frames"]) == list(
                FROZEN_1P5M_VAL_STUB_FRAME_RANGE)
            and list(counted["hold_remainder_frames"]) == list(
                FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE)
            and int(counted["val_stub_symbols"])
            + int(counted["hold_remainder_symbols"]) == stub_symbols
            and stub_frames == 83
            and stub_symbols == 21248
        )
    except (KeyError, TypeError, ValueError):
        blocks_ok = False
    gates["blocks_exact_with_declared_remainder"] = bool(blocks_ok)
    gates["dev_split_manifest_identity"] = bool(
        manifest is not None
        and int(manifest.get("train_pairs", -1)) == FROZEN_MANIFEST_TRAIN_PAIRS
        and int(manifest.get("val_pairs", -1)) == FROZEN_MANIFEST_VAL_PAIRS
        and int(manifest.get("hold_pairs", -1)) == FROZEN_MANIFEST_HOLD_PAIRS)
    gates["dev_block_range_identity"] = bool(
        dev_pin is not None and dev_source_pin is not None
        and disjoint_pin is not None and bool(disjoint_pin.get("disjoint"))
        and bool(dev_pin.get("verified")))
    gates["three_records_exact"] = (
        len(records) == PLANNED_RECORDS if final else len(records) <= PLANNED_RECORDS)
    try:
        sampling_ok = (
            int(calls.get("genie", -1)) == 0
            and construction_pin is not None
            and bool(construction_pin.get("verified"))
            and int(construction_pin.get("train_blocks_used", -1)) == int(
                FROZEN_TRAIN_BLOCKS_TOTAL)
            and int(construction_pin.get("train_genie_calls", -1)) == int(
                FROZEN_TRAIN_GENIE_CALLS))
    except (AttributeError, TypeError, ValueError):
        sampling_ok = False
    gates["sampling_calls_exact"] = bool(sampling_ok)
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
        fresh_l2 = l2_prefix_positions(order_pin_A["l2_order"], int(k2))
        spike_l2 = l2_prefix_positions(spike_order_pin_B["l2_order"], int(k2))
        orders_ok = (
            shared_l1.shape == (int(k1),)
            and fresh_l2.shape == (int(k2),)
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
            and int(set_delta.get("a_disclosed_size", -1)) == int(pins["k2"])
            and int(set_delta.get("b_disclosed_size", -1)) == int(pins["k2"]))
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
    recount = n8192_recount_events(events)
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
        and int(accounting.get("dev_content_opens", -1)) <= 1
        and accounting.get("reopen_attempted") is False)
    gates["input_stat_unchanged"] = bool(
        prior_stat_before == prior_stat_after
        and dev_stat_before == dev_stat_after)
    gates["no_unregistered_access"] = bool(
        set(opened_paths) <= set(registered_paths))
    rss_peak = opf._peak_rss_bytes()
    gates["resource_limits_met_and_no_abort"] = bool(
        resource_stop is None and float(wall_s) <= float(cap)
        and (rss_peak is None or int(rss_peak) <= RSS_LIMIT_BYTES)
        and all(r.get("outcome") != "resource_abort" for r in records))
    return gates


def n8192_persistence_probe_2m_label(gates: dict) -> str:
    """Descriptive COMPLETE iff every integrity gate holds, else BLOCKED(first)."""
    failing = [g for g in INTEGRITY_GATE_ORDER if not gates.get(g, False)]
    if not failing:
        return COMPLETE_LABEL
    return f"BLOCKED({failing[0]})"


@dataclass(frozen=True, eq=False)
class N8192PersistenceProbe2mRun:
    """In-memory P20T Stage-B run (also returned by the runner)."""

    summary: dict
    records: tuple
    gates: dict


# ---------------------------------------------------------------------------
# Stage-B orchestration.
# ---------------------------------------------------------------------------

def _write_frozen_plan(out_path: Path, *, source, floor, n, k1, k2, k_total,
                       budget_literal, train_residual, construction,
                       construction_digest, prior_path, prior_digest,
                       dev_pairs, manifest_path, dev_frames_hold,
                       block_frames, remainder_frames, tag_master, chunk_rows,
                       tag_bits, order_file, order_digest, spike_order_file,
                       spike_order_digest, spike_formula, identity, manifest,
                       dev_source_pin, dev_pin, disjoint_pin, frame_set_pin,
                       construction_pin, order_pin_A, spike_order_pin_B,
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
        "budget_rule": "floor((1.3*8192*H-64)/5)_DERIVED_IN_PACKET_FROM_RECOMPUTED_H",
        "train_residual": float(train_residual),
        "construction": str(construction),
        "construction_digest": str(construction_digest),
        "prior_path": str(prior_path),
        "prior_digest": str(prior_digest),
        "dev_pairs": str(dev_pairs),
        "manifest_path": str(manifest_path),
        "dev_frames_hold": [int(dev_frames_hold[0]), int(dev_frames_hold[1])],
        "dev_frame_list": [int(f) for f in FROZEN_DEV_FRAME_LIST],
        "block_frames": int(block_frames),
        "remainder_frames": [int(remainder_frames[0]), int(remainder_frames[1])],
        "build_frames": [int(FROZEN_BUILD_FRAME_RANGE[0]),
                         int(FROZEN_BUILD_FRAME_RANGE[1])],
        "dev_source": dict(dev_source_pin),
        "dev_block_pin": dict(dev_pin),
        "build_dev_disjointness_s2_ii": dict(disjoint_pin),
        "single_segment_frame_set_identity": dict(frame_set_pin),
        "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
        "consumed_2m_train_frame_range": list(CONSUMED_2M_TRAIN_FRAME_RANGE),
        "consumed_2m_val_dev_frame_range": list(CONSUMED_2M_VAL_DEV_FRAME_RANGE),
        "consumed_2m_hold_dev_frame_range": list(CONSUMED_2M_HOLD_DEV_FRAME_RANGE),
        "hold_tail_remainder_counted_never_decoded": {
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
                        "excluded_by": "gate-a path refusal"},
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
        "tag_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS),
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "sc_stages": int(FROZEN_SC_STAGES),
        "order_file_A": str(order_file),
        "order_digest_A": str(order_digest),
        "spike_order_file_B": str(spike_order_file),
        "spike_order_digest_B": str(spike_order_digest),
        "spike_formula_id": str(spike_formula),
        "spike_program": str(DERIVATION_PROGRAM_PIN),
        "derivation_train_seeds": [int(s) for s in FROZEN_DERIVATION_SEEDS],
        "derivation_train_blocks": int(FROZEN_TRAIN_BLOCKS_TOTAL),
        "derivation_train_genie_calls": int(FROZEN_TRAIN_GENIE_CALLS),
        "order_set_delta": {
            key: (list(value) if isinstance(value, list) else value)
            for key, value in dict(set_delta).items()
        },
        "order_k1": int(order_pin_A.get("k1", -1)),
        "order_k2": int(order_pin_A.get("k2", -1)),
        "construction_k1": int(construction_pin.get("k1", -1)),
        "construction_k2": int(construction_pin.get("k2", -1)),
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
        "hazard_window_R_refrozen_for_8192_geometry": True,
        "hazard_fields": list(HAZARD_FIELDS),
        "u_domain_scalar_frozen_present": True,
        "arm_order_digest_rule": "fresh-A on A/O, spike on B",
        "ir_fields": list(IR_FIELDS),
        "ir3_threshold_multipliers": [IR3_LO_MULT, IR3_HI_MULT],
        "ir1_bins": int(IR1_BINS),
        "ir4_topk": int(IR4_TOPK),
        "ir5_mode": "N8192_SIZED_FULL_BLOCK_8192_BINARY_LE_BIN_PLUS_MANIFEST",
        "ir5_format_version": str(IR5_FORMAT_VERSION),
        "ir5_encoding": "f32le hazard + u8 inprefix + u8 inu per record",
        "ir5_per_record_bytes": int(IR5_PER_RECORD_BYTES),
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
        "# NB-Polar Phase 4-P20T N=8192 persistence probe on the single 2M "
        "HOLD-tail DEV block with N=8192-sized full-block IR-5",
        "",
        f"- protocol: `{summary.get('analysis')}` (mode `{summary.get('mode')}`)",
        f"- source: `{summary.get('source')}`; N={summary.get('n')}; "
        f"K1={summary.get('k1')} K2={summary.get('k2')} K_total={summary.get('k_total')} "
        "(in-packet K-rule derivation from recomputed 2M H, TRAIN-residual split)",
        "- alt-L2 construction: unit-pseudocount conditional alpha1 on all "
        "arms (recomputed from the worktree counts by the frozen rule); "
        f"construction digest `{summary.get('construction_digest_8192')}`",
        f"- fresh-A order digest: `{summary.get('order_digest_A')}` "
        f"(first-{summary.get('k1')} / first-{summary.get('k2')} prefixes on A/O); "
        f"spike-B order digest: `{summary.get('spike_order_digest_B')}` "
        f"(first-{summary.get('k2')} prefix on B; formula "
        f"`{summary.get('spike_formula_id')}`); set-delta "
        f"|A-B|={set_delta.get('a_minus_b_count')} "
        f"|B-A|={set_delta.get('b_minus_a_count')} "
        f"(size-delta {set_delta.get('size_delta_b_minus_a')})",
        f"- single-segment DEV: HOLD {summary.get('dev_frames_hold')} "
        f"(remainder {summary.get('remainder_frames')} never used; 1.5M "
        "stub/remainder counted never decoded)",
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
        f"IR-5 N=8192-sized={ir_payload.get('ir5_n8192_sized_full_block')} "
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
        "descriptive N=8192 persistence probe (n=1, within-N paired "
        "comparison only, Q-G1/Q-G2) of one spike-local L2-order position "
        "rule under the frozen alpha1 construction at in-packet disclosure "
        "with full-block hazard geometry recorded: no FER / reliability / "
        "efficiency / leakage / key-rate / recovery / scaling / promotion "
        "claim is made; no cross-N inference; no H2 input; the DEV block is "
        "consumed by this packet regardless of outcome.",
        "",
    ]
    return "\n".join(lines)


def run_n8192_persistence_probe_2m(
    *,
    prior=None,
    prior_path=FROZEN_PRIOR_PATH,
    prior_digest=None,
    source=None,
    floor=FROZEN_FLOOR,
    n=None,
    k1=None,
    k2=None,
    construction=FROZEN_CONSTRUCTION_PATH_8192,
    construction_digest=None,
    manifest_path=FROZEN_MANIFEST_PATH,
    dev_pairs=FROZEN_DEV_PAIRS_PATH,
    dev_table=None,
    dev_frames_hold=FROZEN_DEV_FRAMES_HOLD,
    block_frames: int = FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
    tag_master=FROZEN_TAG_MASTER,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    tag_bits: int = FROZEN_TAG_BITS,
    order_file=FROZEN_ORDER_PATH_8192,
    order_digest=None,
    spike_order_file=FROZEN_SPIKE_ORDER_PATH_8192,
    spike_order_digest=None,
    spike_formula=None,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
) -> N8192PersistenceProbe2mRun:
    """Execute the frozen P20T three-arm N=8192 persistence-probe run once; write fifteen files.

    ``prior`` / ``dev_table`` are documented injected test seams; the
    frozen CLI passes only the frozen point, loads the Stage-A frozen 2M
    worktree prior read-only exactly once, recomputes the alpha1 L2 tables
    from the worktree counts by the frozen rule (no alt file), loads the
    Stage-A fresh 2M order file and the Stage-A spike order file read-only
    behind their digest gates, and reads the single-segment 2M HOLD-tail
    DEV parquet through its accepted loader exactly once. The V25 counts
    NPZ is never opened at any stage. The construction/order swap is
    hardcoded (never CLI-tunable): A runs the recomputed alpha1 L2 at the
    Stage-A (K1,K2) on the fresh-A order prefixes, B the SAME alpha1 L2 at
    the SAME point on the spike order prefix, and O the fresh-order
    true-L1 oracle (D-continuity) at carried K2. Stage B performs ZERO
    sampling (no seed flag, no sampler call; the genie counter is gated
    at 0).
    """
    global _SESSION_PRIOR_CONTENT_LOADED
    global _DEV_PARQUET_CONTENT_OPENED
    pins = pins_frozen()
    if pins["frozen"] is not True:
        raise ValueError(
            "BLOCKED(new_construction_identity_8192): Stage-A pins not frozen "
            "(DEV untouched; no Stage-B run)")
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    floor = _check_floor(floor)
    source = _check_source(source)
    n = _check_n(n)
    if k1 is None or k2 is None:
        raise ValueError("frozen point requires --k1/--k2 equal to the Stage-A literals")
    k1 = _check_k1(k1)
    k2 = _check_k2(k2)
    k_total = int(k1) + int(k2)
    if k_total != int(pins["k_total"]):
        raise ValueError("frozen point requires K1+K2 equal to the Stage-A K_total")
    opf._check_tag_bits(tag_bits)
    _check_chunk_contract_8192(chunk_rows)
    dev_frames_hold = _check_dev_frames_hold(dev_frames_hold)
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise ValueError(
            f"frozen point requires block-frames={FROZEN_BLOCK_FRAMES}, got {block_frames}")
    remainder_frames = _check_remainder_frames(remainder_frames)
    tag_master = _check_tag_master(tag_master)
    if prior_digest is None:
        raise ValueError("frozen point requires --prior-digest equal to the Stage-A pin")
    prior_digest = _check_prior_digest(prior_digest)
    if construction_digest is None:
        raise ValueError(
            "frozen point requires --construction-digest equal to the Stage-A pin")
    construction_digest = _check_construction_digest(construction_digest)
    if order_digest is None:
        raise ValueError("frozen point requires --order-digest equal to the Stage-A pin")
    order_digest = _check_order_digest_A(order_digest)
    if spike_order_digest is None:
        raise ValueError(
            "frozen point requires --spike-order-digest equal to the Stage-A pin")
    spike_order_digest = _check_spike_order_digest_B(spike_order_digest)
    if spike_formula is None:
        raise ValueError(
            "frozen point requires --spike-formula equal to the Stage-A formula-id")
    spike_formula = _check_spike_formula(spike_formula)
    arms = frozen_arm_table() if check_frozen_arm_table() else ()

    # Gate family (a)->(g) in the frozen order before any protected content
    # open: predecessor lineage pin, cross-file source identity (a),
    # intra-file single-segment containment (b), consumed-1M /
    # consumed-1.5M / consumed-2M + S2-ii (c)-(e), then reuse-prior +
    # new-construction + fresh-order + spike-order + derivation-program +
    # K-rule + order-position-identity pins (f)-(g).
    identity = {"predecessor_label": str(FROZEN_PREDECESSOR_LABEL), "n": int(n)}
    dev_source_pin = _gate_call("dev_block_range_identity",
                                verify_dev_source_identity_2m, dev_pairs)
    dev_pin = verify_single_segment_containment(dev_frames_hold, remainder_frames)
    disjoint_pin = verify_consumed_exclusions_single_segment(
        dev_frames_hold, remainder_frames)
    frame_set_pin = _gate_call("dev_block_range_identity",
                               verify_single_segment_frame_set_identity,
                               dev_frames_hold)
    manifest = _gate_call("dev_split_manifest_identity", verify_dev_manifest_2m,
                          manifest_path, source=source)
    construction_pin = _gate_call(
        "new_construction_identity_8192", verify_construction_file_8192,
        construction, expected_digest=construction_digest,
        expected_prior_digest=str(FROZEN_SESSION_PRIOR_DIGEST),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    order_pin_A = _gate_call(
        "fresh_order_identity_A_8192", verify_fresh_order_file_8192, order_file,
        expected_digest=order_digest,
        expected_prior_digest=str(FROZEN_SESSION_PRIOR_DIGEST),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    spike_order_pin_B = _gate_call(
        "spike_order_identity_B_8192", verify_spike_order_file, spike_order_file,
        expected_digest=spike_order_digest,
        expected_prior_digest=str(FROZEN_SESSION_PRIOR_DIGEST),
        frozen_l1_order=np.asarray(order_pin_A["l1_order"]),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    if str(spike_order_pin_B.get("program")) != str(DERIVATION_PROGRAM_PIN):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(order_derivation_identity): program pin drifted")
    if str(spike_order_pin_B.get("formula_id")) != str(SPIKE_FORMULA_ID):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(order_derivation_identity): formula-id drifted")
    set_delta = order_set_delta_8192(
        np.asarray(order_pin_A["l2_order"]),
        np.asarray(spike_order_pin_B["l2_order"]), int(k2))
    if int(set_delta["size_delta_b_minus_a"]) != 0:
        raise N8192PersistenceProbeContractError(
            "BLOCKED(order_set_delta_recorded): B-A disclosed-size delta != 0")
    # Order-position identity (g): the construction quadruple + tag
    # domain + source vocabulary must match the P20T freeze.
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
            "nbpolar-p20t-n8192-persistence-2m", "n8192-tail-persistence-probe-2m",
            "2M", "nbpolar-p20t-n8192-persistence-2m-seed"):
        raise N8192PersistenceProbeContractError(
            "BLOCKED(dev_block_range_identity): order-position identity drifted")
    # Frozen-point declaration (pins; the rule itself is replayed post-load
    # from same-run H and in the k_rule_derived gate from the frozen H).
    hazard_pin = {
        "k_literal": True,
        "budget_literal": str(pins["budget_literal"]),
        "alt_floor_rate": float(FROZEN_ALT_FLOOR_HIT_RATE),
    }

    # One-open guards are refusals before any content load/open of any input.
    if prior is None and _SESSION_PRIOR_CONTENT_LOADED:
        raise ValueError("reload refused: the single session-prior load was consumed")
    if dev_table is None and _DEV_PARQUET_CONTENT_OPENED:
        raise ValueError(
            "reopen refused: the single HOLD-tail parquet content open was consumed")

    # Input existence and stat-only metadata come before any content load/open.
    real_prior = prior is None
    real_dev = dev_table is None
    if real_prior:
        prior_file = Path(prior_path)
        if not prior_file.is_file():
            raise FileNotFoundError(f"Stage-A 2M worktree prior not found: {prior_file}")
        prior_stat_before = _stat_record(prior_file)
    else:
        prior_stat_before = _stat_record(None)
    if real_dev:
        dev_path_obj = Path(dev_pairs)
        if not dev_path_obj.is_file():
            raise FileNotFoundError(f"HOLD-tail 2M pairs parquet not found: {dev_path_obj}")
        dev_stat_before = _stat_record(dev_path_obj)
    else:
        dev_stat_before = _stat_record(None)
    registered_paths = []
    if real_prior:
        registered_paths.append(str(Path(prior_path).resolve()))
    if real_dev:
        registered_paths.append(str(Path(dev_pairs).resolve()))
    opened_paths: list[str] = []

    plan = _write_frozen_plan(
        out_path=out_path, source=source, floor=floor, n=n, k1=k1, k2=k2,
        k_total=k_total, budget_literal=str(pins["budget_literal"]),
        train_residual=float(construction_pin["train_residual"]),
        construction=construction, construction_digest=construction_digest,
        prior_path=prior_path if real_prior else None, prior_digest=prior_digest,
        dev_pairs=dev_pairs, manifest_path=manifest_path,
        dev_frames_hold=dev_frames_hold,
        block_frames=block_frames, remainder_frames=remainder_frames,
        tag_master=tag_master, chunk_rows=chunk_rows, tag_bits=tag_bits,
        order_file=order_file, order_digest=order_digest,
        spike_order_file=spike_order_file, spike_order_digest=spike_order_digest,
        spike_formula=spike_formula,
        identity=identity, manifest=manifest, dev_source_pin=dev_source_pin,
        dev_pin=dev_pin, disjoint_pin=disjoint_pin, frame_set_pin=frame_set_pin,
        construction_pin=construction_pin, order_pin_A=order_pin_A,
        spike_order_pin_B=spike_order_pin_B, set_delta=set_delta)
    accounting = {
        "input_mode": "real" if (real_prior or real_dev) else "injected",
        "session_prior_input_mode": "frozen_prior_file" if real_prior else "injected_prior",
        "dev_input_mode": "pairs_parquet" if real_dev else "injected_table",
        "prior_path": str(prior_path) if real_prior else None,
        "dev_pairs_path": str(dev_pairs) if real_dev else None,
        "manifest_path": str(manifest_path),
        "construction_path": str(construction),
        "prior_loader": "per_session_calibration.canonical_prior_digest(read-only seam)" if real_prior else None,
        "pairs_loader": p20o.PAIRS_LOADER_IDENTITY if real_dev else None,
        "registered_content_paths": registered_paths,
        "opened_content_paths": opened_paths,
        "artifact_content_reads_allowed_per_input": 1,
        "counts_content_opens": 0,
        "session_prior_content_loads": 0,
        "dev_content_opens": 0,
        "attempts_allowed": 1,
        "attempts_consumed_by_this_run": 0,
        "retries": 0,
        "reopen_attempted": False,
        "retry_after_open": False,
    }

    start = time.perf_counter()
    try:
        # ---- input 1: the single session-prior load + reuse_prior_arrays_identity.
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
        counts_inc = session_prior_verified["counts"]
        # Same-run-H budget display (the frozen rule from recomputed H;
        # never hand-filled, never from alt-H).
        same_run_budget = p20m.verify_budget_literal(
            float(session_prior_verified["h_total"]), int(k_total), n=int(n),
            target_f=float(FROZEN_TARGET_F))
        hazard_pin = {
            "k_literal": True,
            "budget_literal": str(same_run_budget["literal"]),
            "alt_floor_rate": float(FROZEN_ALT_FLOOR_HIT_RATE),
        }

        # ---- alpha1 L2 recompute from the worktree counts (frozen rule, no alt file).
        pre = alt_prefloor_table(counts_inc)
        f_alt = np.maximum(pre, float(FROZEN_FLOOR))
        f_alt = np.ascontiguousarray(f_alt / f_alt.sum(axis=0, keepdims=True))
        p2_alt = np.ascontiguousarray(derive_p2(np.ascontiguousarray(f_alt)))
        if p2_alt.shape != (Q, N_BOB, Q):
            raise ValueError(
                f"recomputed p2_alt must be (32,1024,32), got {p2_alt.shape}")
        if not np.isfinite(p2_alt).all() or bool((p2_alt <= 0).any()):
            raise ValueError("recomputed p2_alt must be finite and positive")
        p1_equality = float(np.abs(
            np.asarray(p1_inc, dtype=np.float64)
            - np.asarray(raw_arrays["p1"], dtype=np.float64)).max())
        if not np.isfinite(p1_equality) or p1_equality > NORM_TOL:
            raise ValueError(
                "recomputed-alt p1-equality exceeds 1e-12 "
                "(refusing before any SC call)")
        alt_recomputed = {
            "alpha": float(FROZEN_ALPHA),
            "floor_value": float(FROZEN_FLOOR),
            "keys": ["counts_ab", "f_alt", "p1", "p2_alt", "alpha", "floor_value"],
            "p1_equality_max_abs_diff": p1_equality,
            "recomputed_from": "worktree counts_ab by the frozen alpha=1 rule",
            "passed": True,
        }

        # ---- input 2: the single HOLD-tail parquet content open, DEV rows only.
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
        formation = form_single_segment_block(
            table, dev_frames_hold=dev_frames_hold,
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
            "alt": (np.asarray(p1_inc), np.asarray(p2_alt),
                    np.asarray(counts_inc)),
        }
        l1_shared = np.asarray(order_pin_A["l1_order"], dtype=np.int64)
        l2_by_arm = {
            "A_anchor_frozen_order_equivalent": np.asarray(
                order_pin_A["l2_order"], dtype=np.int64),
            "B_spike_local_order": np.asarray(
                spike_order_pin_B["l2_order"], dtype=np.int64),
            "O_true_l1_oracle": np.asarray(
                order_pin_A["l2_order"], dtype=np.int64),
        }
        digest_by_arm = {
            "A_anchor_frozen_order_equivalent": str(order_pin_A.get("order_digest")),
            "B_spike_local_order": str(spike_order_pin_B.get("spike_order_digest")),
            "O_true_l1_oracle": str(order_pin_A.get("order_digest")),
        }
        ir5_box: dict = {"manifest": None}

        def current_gates(*, final: bool, wall_now: float) -> tuple:
            gates = _integrity_gates(
                n=n, k1=k1, k2=k2, k_total=k_total, arms=arms, identity=identity,
                manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
                disjoint_pin=disjoint_pin, construction_pin=construction_pin,
                order_pin_A=order_pin_A,
                spike_order_pin_B=spike_order_pin_B, set_delta=set_delta,
                formation=formation, records=records, events=events, calls=calls,
                incremental=incremental, accounting=accounting,
                provenance_violations=provenance_violations,
                cap=budget_cap, wall_s=wall_now, resource_stop=resource_stop,
                session_prior_verified=session_prior_verified,
                alt_recomputed=alt_recomputed, hazard_pin=hazard_pin,
                prior_stat_before=prior_stat_before,
                prior_stat_after=prior_stat_before,
                dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_before,
                registered_paths=registered_paths, opened_paths=opened_paths,
                ir5_manifest=ir5_box["manifest"], out_root=out_path,
                final=final)
            failing = [g for g in INTEGRITY_GATE_ORDER if not gates[g]]
            return gates, failing

        def partial_summary(outcome_label: str, gates: dict, wall_now: float) -> dict:
            aggregates = build_aggregates(records)
            aggregates["ir_payload"] = ir_payload_tables(records)
            recount = n8192_recount_events(events)
            derived_key = sum(int(r.get("actual_key_dependent_bits", 0)) for r in records)
            return {
                "analysis": PROTOCOL_NAME,
                "mode": MODE,
                "source": source,
                "n": int(n),
                "k1": int(k1),
                "k2": int(k2),
                "k_total": int(k_total),
                "budget_literal": str(same_run_budget["literal"]),
                "train_residual": float(construction_pin["train_residual"]),
                "prior_digest": str(prior_digest),
                "construction_digest_8192": str(construction_pin["construction_digest"]),
                "order_digest_A": str(order_pin_A.get("order_digest")),
                "spike_order_digest_B": str(spike_order_pin_B.get("spike_order_digest")),
                "spike_program": str(DERIVATION_PROGRAM_PIN),
                "spike_formula_id": str(SPIKE_FORMULA_ID),
                "order_set_delta": {
                    key: (list(value) if isinstance(value, list) else value)
                    for key, value in dict(set_delta).items()
                },
                "dev_frames_hold": list(FROZEN_DEV_FRAMES_HOLD),
                "block_segments": [list(FROZEN_DEV_FRAMES_HOLD)],
                "dev_frame_list": [int(f) for f in FROZEN_DEV_FRAME_LIST],
                "remainder_frames": list(FROZEN_REMAINDER_FRAME_RANGE),
                "hold_tail_remainder_counted_never_decoded": {
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
                    "descriptive N=8192 persistence probe (n=1, within-N "
                    "paired comparison only, Q-G1/Q-G2) of one spike-local "
                    "L2-order position rule under the frozen alpha1 "
                    "construction at the in-packet (TRAIN-residual) "
                    "disclosure point (N=8192, one single-segment block "
                    "HOLD 3595..3626) with the mandatory IR-1..IR-4 payload "
                    "plus N=8192-sized full-block IR-5 series under each "
                    "order; O is an oracle-labelled diagnostic control, "
                    "never an operational protocol or deployable result; "
                    "not real-frame FER, reconciliation efficiency, "
                    "leakage, key rate, scaling superiority, qualification "
                    "or promotion evidence; the CE-normalized disclosure "
                    "ratio is not qualification efficiency; undetected is "
                    "never success; per-record outcomes are recorded but "
                    "explicitly NOT read as recovery rates; no reliability "
                    "or recovery claim is licensed; no cross-N inference; "
                    "the H2 decision is main-thread analysis after "
                    "acceptance, not a block result; DEV is consumed by "
                    "this packet regardless of outcome"
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
                        k_total=int(k_total), budget_literal=str(
                            same_run_budget["literal"]),
                        prior_digest=prior_digest,
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
            seed = n8192_persistence_probe_2m_seed_bits(
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
                # the L2 order: A runs the fresh-A prefix, B the spike-B
                # prefix, both at the SAME Stage-A point on the SAME
                # recomputed alpha1 table. The swap is hardcoded, never
                # CLI-tunable.
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
                        l1_exact=False, hard_l2_exact=False,
                        oracle_l2_exact=None, pair_exact=False,
                        high_hat=None, low_hat=None, label_hat=None,
                    )
                if result.truth_leak_violation:
                    provenance_violations += 1
                resources = opf._cell_resource_record(time.perf_counter() - block_start)
                record = _operational_record(
                    result, spec=spec, arm_index=arm_index, block=block,
                    scoring=scoring, resources=resources,
                    k_total=int(k_total), budget_literal=str(
                        same_run_budget["literal"]),
                    prior_digest=prior_digest,
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
                    k_total=int(k_total), budget_literal=str(
                        same_run_budget["literal"]),
                    prior_digest=prior_digest,
                    order_digest=arm_digest, counts_arr=counts_use, p1=p1_use,
                    p2=p2_use, l2_order=l2_use, n=n, view=view, field=field,
                    error=error, ir5_dir=out_path)

            records.append(record)
            opf._append_jsonl(out_path / "per_block_arm_outcomes.jsonl", record)
            for event in n8192_block_events(
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
            disjoint_pin=disjoint_pin, construction_pin=construction_pin,
            order_pin_A=order_pin_A,
            spike_order_pin_B=spike_order_pin_B, set_delta=set_delta,
            formation=formation, records=records, events=events, calls=calls,
            incremental=incremental, accounting=accounting,
            provenance_violations=provenance_violations,
            cap=budget_cap, wall_s=wall_s, resource_stop=resource_stop,
            session_prior_verified=session_prior_verified,
            alt_recomputed=alt_recomputed, hazard_pin=hazard_pin,
            prior_stat_before=prior_stat_before, prior_stat_after=prior_stat_after,
            dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_after,
            registered_paths=registered_paths, opened_paths=opened_paths,
            ir5_manifest=ir5_manifest_doc, out_root=out_path,
            final=True)
        outcome_label = n8192_persistence_probe_2m_label(gates)
        summary = partial_summary(outcome_label, gates, wall_s)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        identity_doc = {
            "predecessor_label": str(FROZEN_PREDECESSOR_LABEL),
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
            "alt_recompute_gate": {
                "alpha": float(alt_recomputed["alpha"]),
                "floor_value": float(alt_recomputed["floor_value"]),
                "keys": list(alt_recomputed["keys"]),
                "p1_equality_max_abs_diff": float(
                    alt_recomputed["p1_equality_max_abs_diff"]),
                "recomputed_from": str(alt_recomputed["recomputed_from"]),
                "verified": bool(alt_recomputed["passed"]),
            },
            "k_rule_display": str(same_run_budget["literal"]),
            "train_residual": float(construction_pin["train_residual"]),
            "construction_file_pin": {
                "construction_file": str(construction_pin.get("construction_file")),
                "construction_digest": str(construction_pin.get("construction_digest")),
                "n": int(construction_pin.get("n", -1)),
                "k1": int(construction_pin.get("k1", -1)),
                "k2": int(construction_pin.get("k2", -1)),
                "prior_digest": str(construction_pin.get("prior_digest")),
                "program": str(construction_pin.get("program")),
                "verified": bool(construction_pin.get("verified")),
            },
            "order_file_pin_A": {
                "order_file": str(order_pin_A.get("order_file")),
                "order_digest": str(order_pin_A.get("order_digest")),
                "n": int(order_pin_A.get("n", -1)),
                "k1": int(order_pin_A.get("k1", -1)),
                "k2": int(order_pin_A.get("k2", -1)),
                "prior_digest": str(order_pin_A.get("prior_digest")),
                "program": str(order_pin_A.get("program")),
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
            "derivation_train_seeds": [int(s) for s in FROZEN_DERIVATION_SEEDS],
            "derivation_train_blocks": int(FROZEN_TRAIN_BLOCKS_TOTAL),
            "derivation_train_genie_calls": int(FROZEN_TRAIN_GENIE_CALLS),
            "ir_pins": {
                "ir3_threshold_multipliers": [IR3_LO_MULT, IR3_HI_MULT],
                "ir1_bins": int(IR1_BINS),
                "ir4_topk": int(IR4_TOPK),
                "ir5_mode": "N8192_SIZED_FULL_BLOCK_8192_BINARY_LE_BIN_PLUS_MANIFEST",
                "ir5_format_version": str(IR5_FORMAT_VERSION),
                "ir5_per_record_bytes": int(IR5_PER_RECORD_BYTES),
                "ir5_per_record_budget_bytes": int(IR5_PER_RECORD_BUDGET_BYTES),
                "ir5_root_budget_bytes": int(IR5_ROOT_BUDGET_BYTES),
                "ir5_max_file_bytes": int(IR5_MAX_FILE_BYTES),
            },
            "stage_b_sampling_calls": int(calls.get("genie", 0)),
            "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
            "prior_stat_before": prior_stat_before,
            "prior_stat_after": prior_stat_after,
            "dev_stat_before": dev_stat_before,
            "dev_stat_after": dev_stat_after,
            "attempt_read_accounting": dict(
                accounting, opened_content_paths=list(opened_paths)),
        }
        opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
        persist(summary)
        return N8192PersistenceProbe2mRun(summary=summary, records=tuple(records),
                                          gates=gates)
    except N8192PersistenceProbeResourceError:
        raise
    except MemoryError as exc:
        raise N8192PersistenceProbeResourceError(
            f"resource stop: MemoryError: {exc}") from exc


VERIFY_DERIVATION_FLAGS = (
    "prior", "prior_digest", "construction", "construction_digest",
    "k1", "k2", "order_file", "order_digest",
    "spike_order_file", "spike_order_digest", "spike_formula",
)
DERIVE_FLAGS = (
    "prior", "prior_digest", "out_construction", "out_orders", "out_spike",
)
SHARED_FLAGS = ("source", "floor", "n")
STAGE_B_ONLY_FLAGS = (
    "prior", "prior_digest", "k1", "k2", "construction",
    "construction_digest", "dev_pairs", "dev_frames_hold",
    "block_frames", "remainder_frames", "tag_master", "chunk_rows", "tag_bits",
    "order_file", "order_digest", "spike_order_file", "spike_order_digest",
    "spike_formula", "out_dir",
)
STAGE_B_FLAGS = SHARED_FLAGS + STAGE_B_ONLY_FLAGS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p20t-n8192-persistence-2m",
        description=(
            "NB-Polar Phase 4-P20T N=8192 persistence probe on the single 2M "
            "HOLD-tail DEV block: --derive runs the frozen Stage-A N=8192 "
            "derivation once (worktree-prior arrays ONLY under the frozen "
            "seeds/budget); --verify-derivation replays the reuse + "
            "derivation pins from the Stage-A files with zero sampling and "
            "zero protected opens; otherwise all Stage-B flags are required "
            "(frozen command, no production default)"
        ),
    )
    parser.add_argument("--derive", action="store_true", dest="derive",
                        help="Stage-A derivation mode (derive flags required)")
    parser.add_argument("--verify-derivation", action="store_true",
                        dest="verify_derivation",
                        help="Stage-A derivation-verification mode (all verify flags required)")
    parser.add_argument("--prior", default=None)
    parser.add_argument("--prior-digest", default=None, dest="prior_digest")
    parser.add_argument("--out-construction", default=None, dest="out_construction")
    parser.add_argument("--out-orders", default=None, dest="out_orders")
    parser.add_argument("--out-spike", default=None, dest="out_spike")
    parser.add_argument("--source", default=None)
    parser.add_argument("--floor", default=None, type=float)
    parser.add_argument("--n", default=None, type=int)
    parser.add_argument("--k1", default=None, type=int)
    parser.add_argument("--k2", default=None, type=int)
    parser.add_argument("--construction", default=None)
    parser.add_argument("--construction-digest", default=None,
                        dest="construction_digest")
    parser.add_argument("--dev-pairs", default=None, dest="dev_pairs")
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
    parser.add_argument("--out-dir", default=None, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if bool(args.derive) and bool(args.verify_derivation):
            raise ValueError(
                "mixed invocation refused: --derive and --verify-derivation "
                "never combine; refusing before any read or write")
        if args.derive:
            given_b = [name for name in STAGE_B_ONLY_FLAGS
                       if name not in DERIVE_FLAGS
                       and getattr(args, name) is not None]
            if given_b:
                raise ValueError(
                    "mixed invocation refused: --derive takes no Stage-B-only flags "
                    f"(got {given_b}); refusing before any read or write")
            given_v = [name for name in VERIFY_DERIVATION_FLAGS
                       if name not in DERIVE_FLAGS
                       and getattr(args, name) is not None]
            if given_v:
                raise ValueError(
                    "mixed invocation refused: --derive takes no --verify-derivation "
                    f"flags (got {given_v}); refusing before any read or write")
            missing = [name for name in DERIVE_FLAGS
                       if getattr(args, name) is None]
            if missing:
                raise ValueError(
                    "missing required --derive flags: " + ",".join(sorted(missing))
                    + "; refusing before any read or write")
            derived = run_derive_stage_a(
                prior_path=args.prior,
                expected_prior_digest=str(args.prior_digest),
                out_construction_path=args.out_construction,
                out_orders_path=args.out_orders,
                out_spike_path=args.out_spike)
            print(json.dumps({
                "construction_path": derived["construction_path"],
                "construction_digest": derived["construction_digest"],
                "order_path": derived["order_path"],
                "order_digest": derived["order_digest"],
                "spike_order_path": derived["spike_order_path"],
                "spike_order_digest": derived["spike_order_digest"],
                "prior_digest": derived["prior_digest"],
                "h1": derived["h1"],
                "h2": derived["h2"],
                "h_total": derived["h_total"],
                "budget_literal": derived["budget_literal"],
                "k_total": derived["k_total"],
                "k1": derived["k1"],
                "k2": derived["k2"],
                "train_residual": derived["train_residual"],
                "formula_id": derived["formula_id"],
                "program": derived["program"],
                "train_blocks_used": derived["train_blocks_used"],
                "train_genie_calls": derived["train_genie_calls"],
                "counts_content_opens": derived["counts_content_opens"],
                "dev_contact": derived["dev_contact"],
            }, sort_keys=True))
            return 0
        if args.verify_derivation:
            given_b = [name for name in STAGE_B_ONLY_FLAGS
                       if name not in VERIFY_DERIVATION_FLAGS
                       and getattr(args, name) is not None]
            if given_b:
                raise ValueError(
                    "mixed invocation refused: --verify-derivation takes no Stage-B-only "
                    f"flags (got {given_b}); refusing before any read or write")
            missing = [name for name in VERIFY_DERIVATION_FLAGS
                       if getattr(args, name) is None]
            if missing:
                raise ValueError(
                    "missing required --verify-derivation flags: " + ",".join(
                        sorted(missing))
                    + "; refusing before any read or write")
            with open(args.prior, "rb") as fh:
                data = np.load(fh, allow_pickle=False)
                with data:
                    raw_arrays = {k: np.asarray(data[k]) for k in data.files}
            result = verify_derivation(
                prior=raw_arrays, construction_file=args.construction,
                order_file=args.order_file, spike_order_file=args.spike_order_file,
                prior_digest=args.prior_digest,
                construction_digest=args.construction_digest,
                order_digest=args.order_digest,
                spike_order_digest=args.spike_order_digest,
                spike_formula=_check_spike_formula(args.spike_formula),
                h1=FROZEN_H1, h2=FROZEN_H2, h_total=FROZEN_H_TOTAL,
                k1=args.k1, k2=args.k2)
            print(json.dumps({
                "reuse_prior_digest": result["prior_digest"],
                "h1": result["h1"],
                "h2": result["h2"],
                "h_total": result["h_total"],
                "construction_digest": result["construction_digest"],
                "train_residual": result["train_residual"],
                "reuse_order_digest_A": result["order_digest_A"],
                "spike_order_digest_B": result["spike_order_digest_B"],
                "spike_program": result["spike_program"],
                "spike_formula_id": result["spike_formula_id"],
                "k_total": result["k_total"],
                "k1": result["k1"],
                "k2": result["k2"],
                "budget_literal": result["budget_literal"],
                "dev_contact": result["dev_contact"],
                "verified": result["verified"],
            }, sort_keys=True))
            return 0
        given = [name for name in STAGE_B_FLAGS if getattr(args, name) is not None]
        missing = [name for name in STAGE_B_FLAGS if getattr(args, name) is None]
        if missing:
            if not given:
                raise ValueError(
                    "ambiguous invocation refused: neither --derive nor "
                    "--verify-derivation nor any Stage-B flag was given; "
                    "refusing before any read or write")
            raise ValueError(
                "missing required Stage-B flags: " + ",".join(missing)
                + "; refusing before any read or write")
        run = run_n8192_persistence_probe_2m(
            prior_path=args.prior,
            prior_digest=args.prior_digest,
            source=args.source,
            floor=args.floor,
            n=args.n,
            k1=args.k1,
            k2=args.k2,
            construction=args.construction,
            construction_digest=args.construction_digest,
            dev_pairs=args.dev_pairs,
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
            N8192PersistenceProbeContractError) as exc:
        print(f"nbpolar phase4-p20t 2m n8192 persistence-probe refused: {exc}",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL_NAME", "MODE", "Q", "ALPHA", "N_BOB", "NORM_TOL", "FROZEN_N",
    "FROZEN_SOURCE", "FROZEN_SOURCE_TAG", "FROZEN_FLOOR", "FROZEN_ALPHA",
    "FROZEN_TARGET_F", "FROZEN_HAZARD_R", "FROZEN_PUBLIC_CONTROL_BITS",
    "FROZEN_RAW_INPUT_BITS", "FROZEN_L2_CONSTRUCTION", "FROZEN_SC_STAGES",
    "FROZEN_DEV_FRAMES_HOLD", "FROZEN_DEV_FRAMES", "FROZEN_DEV_PAIRS",
    "FROZEN_BLOCK_COUNT", "FROZEN_BLOCK_FRAMES", "FROZEN_PAIRS_PER_FRAME",
    "FROZEN_SYMBOLS_PER_BLOCK", "FROZEN_DEV_FRAME_LIST",
    "INTRA_FILE_HOLD_FRAME_RANGE", "FROZEN_REMAINDER_FRAME_RANGE",
    "FROZEN_REMAINDER_FRAMES", "FROZEN_REMAINDER_SYMBOLS",
    "FROZEN_BUILD_FRAME_RANGE", "CONSUMED_2M_TRAIN_FRAME_RANGE",
    "CONSUMED_2M_VAL_DEV_FRAME_RANGE", "CONSUMED_2M_HOLD_DEV_FRAME_RANGE",
    "CONSUMED_1P5M_SOURCE_TAG", "CONSUMED_1P5M_TRAIN_FRAME_RANGE",
    "CONSUMED_1P5M_VAL_FRAME_RANGE", "CONSUMED_1P5M_HOLD_FRAME_RANGE",
    "FROZEN_1P5M_VAL_STUB_FRAME_RANGE", "FROZEN_1P5M_VAL_STUB_FRAMES",
    "FROZEN_1P5M_VAL_STUB_SYMBOLS", "FROZEN_1P5M_HOLD_REMAINDER_FRAME_RANGE",
    "FROZEN_1P5M_HOLD_REMAINDER_FRAMES",
    "FROZEN_1P5M_HOLD_REMAINDER_SYMBOLS", "FROZEN_MANIFEST_TRAIN_FRAMES",
    "FROZEN_MANIFEST_TRAIN_PAIRS", "FROZEN_MANIFEST_VAL_FRAMES",
    "FROZEN_MANIFEST_VAL_PAIRS", "FROZEN_MANIFEST_HOLD_FRAMES",
    "FROZEN_MANIFEST_HOLD_PAIRS", "CONSUMED_1M_SOURCE_TAG",
    "REFUSED_1M_DEV_PAIRS_PATH", "REFUSED_1P5M_DEV_PAIRS_PATH",
    "FROZEN_DEV_PAIRS_PATH", "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA",
    "FROZEN_TAG_MASTER", "SEED_PREFIX", "FROZEN_CHUNK_ROWS", "FROZEN_TAG_BITS",
    "FROZEN_DERIVATION_SEEDS", "FROZEN_TRAIN_BLOCKS_PER_SEED",
    "FROZEN_TRAIN_BLOCKS_TOTAL", "FROZEN_TRAIN_GENIE_CALLS",
    "FROZEN_PRIOR_PATH", "FROZEN_SESSION_PRIOR_DIGEST", "FROZEN_H1",
    "FROZEN_H2", "FROZEN_H_TOTAL", "FROZEN_ALT_FLOOR_HIT_RATE",
    "FROZEN_K_TOTAL", "FROZEN_K1", "FROZEN_K2", "FROZEN_BUDGET_LITERAL",
    "FROZEN_TRAIN_RESIDUAL", "FROZEN_CONSTRUCTION_PATH_8192",
    "FROZEN_CONSTRUCTION_DIGEST_8192", "FROZEN_ORDER_PATH_8192",
    "FROZEN_ORDER_DIGEST_A_8192", "FROZEN_SPIKE_ORDER_PATH_8192",
    "FROZEN_SPIKE_ORDER_DIGEST_B_8192", "FROZEN_OUT_ROOT", "OUTPUT_FILES",
    "ATTEMPT_CONSUMPTION_POINT", "COMPLETE_LABEL", "RAW_PRIOR_NPZ_KEYS",
    "ORDER_PROTOCOL", "ORDER_KIND", "CONSTRUCTION_PROTOCOL",
    "CONSTRUCTION_KIND", "SPIKE_ORDER_PROTOCOL", "SPIKE_ORDER_KIND",
    "DERIVATION_PROGRAM_PIN", "SPIKE_FORMULA_ID", "SPIKE_FORMULA_TEXT",
    "FROZEN_ARM_NAMES", "OPERATIONAL_ARM_NAMES",
    "ORACLE_ARM_NAMES", "PLANNED_SC_CALLS", "PLANNED_TAG_INVOCATIONS",
    "PLANNED_RECORDS", "INTEGRITY_GATE_ORDER", "IR_FIELDS", "IR1_BINS",
    "IR1_EDGE_LO_BITS", "IR1_EDGE_HI_BITS",
    "IR3_LO_MULT", "IR3_HI_MULT", "IR4_TOPK", "IR5_FULL_N", "IR5_FORMAT_VERSION",
    "IR5_HAZARD_DTYPE", "IR5_FLAG_DTYPE", "IR5_HAZARD_BYTES", "IR5_FLAG_BYTES",
    "IR5_PER_RECORD_BYTES", "IR5_PER_RECORD_BUDGET_BYTES",
    "IR5_ROOT_BUDGET_BYTES", "IR5_MAX_FILE_BYTES",
    "IR5_ARMV_PREFIX", "FROZEN_COMMAND",
    "FROZEN_PREDECESSOR_LABEL", "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S", "EXTERNAL_TIMEOUT_S", "ULIMIT_VIRTUAL_KIB",
    "N8192PersistenceProbeContractError", "N8192PersistenceProbeResourceError",
    "N8192PersistenceProbe2mRun", "pins_frozen", "pins_are_frozen",
    "planned_totals", "frozen_arm_table", "check_frozen_arm_table",
    "frozen_command", "derive_spike_order_8192", "run_derive_stage_a",
    "verify_construction_file_8192", "verify_fresh_order_file_8192",
    "verify_spike_order_file", "order_set_delta_8192", "verify_derivation",
    "verify_dev_source_identity_2m", "verify_single_segment_containment",
    "verify_single_segment_frame_set_identity",
    "verify_consumed_exclusions_single_segment",
    "form_single_segment_block", "n8192_persistence_probe_2m_seed_bits",
    "n8192_block_events", "n8192_recount_events",
    "hazard_instrumentation_complete", "mechanism_diagnostics",
    "build_aggregates", "oracle_isolation_ok", "ir_payload_complete",
    "ir_payload_tables", "check_ir5_manifest_identity",
    "n8192_persistence_probe_2m_label", "run_n8192_persistence_probe_2m",
    "build_parser", "main",
    "VERIFY_DERIVATION_FLAGS", "DERIVE_FLAGS", "SHARED_FLAGS",
    "STAGE_B_ONLY_FLAGS", "STAGE_B_FLAGS",
]
