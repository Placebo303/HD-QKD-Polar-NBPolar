"""NB-Polar Phase 4-P20Q instrumented alpha1 confirmation on FIRST-USE 2M HOLD.

Thin importer of the accepted ``l2_alt_maintain_2m`` runner (read-only; that
module and every accepted module are never edited here), with the P20O
``_l2_hazard_diagnostics`` code point as the carried-over callsite pattern
for the mandatory IR-1..IR-5 recorder extension. Exact delta list (packet
section 2, d1-d8), nothing else:

- (d1) population -> 2M HOLD DEV (FIRST 640 HOLD frames 2916..3555, five
  128-frame blocks at N=32768, remainder 3556..3644 counted never decoded);
  2M VAL-DEV / VAL-remainder excluded as consumed;
- (d2) prior/orders/alt sources -> the P20O frozen files reused read-only
  behind replayed ``reuse_prior_identity`` + ``reuse_alt_identity`` +
  ``reuse_order_freeze`` gates (digests + lambda-0.0/alpha-1.0/floor pins +
  exact key sets + H-literal recomputation within 1e-12 + ``p_b``
  cross-check + ``p1``-equality recheck within 1e-12; worktree-file reads
  only, never the V25 counts NPZ);
- (d3) K pins -> the P20O-derived (K_total,K1,K2)=(7080,334,6746) replayed
  as literals (never recomputed, never recarried; alt-H never a budget
  input);
- (d4) orders -> the P20O frozen ``raw_prior_orders_2m.json`` via the
  reused order-file mechanism (byte-identical on all four arms; disclosed
  sets = first-K1 / first-K2 prefixes);
- (d5) arms A/B/C/D (same K, same frozen order prefixes as P20O);
- (d6) new P20Q tag domain (master 2026092330, prefix
  ``nbpolar-p20q-hold-ir-2m-seed``);
- (d7) mandatory IR-1..IR-5 recorder extension (``_ir_hazard_diagnostics``)
  computed post-decode alongside the nine carried scalars (recording-only,
  bounded, truth-isolation sentinel);
- (d8) 2M-HOLD population + DEV/build-frames disjointness declared inside
  the TRAIN-exclusion gate (S2-ii: build subset 2M TRAIN 0..2186 vs DEV
  subset 2M HOLD 2916..3555).

No SC/transform/floor-semantics/tag-semantics change; no second factor; no
lambda anywhere; no derivation or sampling at any stage (genie 0+0).

Two explicit modes, never mixed: (i) Stage-A reuse verification
(``--verify-reuse``; worktree-file digest recomputation ONLY, zero
protected opens) and (ii) Stage-B frozen command mode (all Stage-B flags
required, no production default). Mixed or ambiguous invocation refuses
before anything is read or written.
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
from . import l2_alt_maintain_2m as p20o
from . import l1_order_1p5m as p20l
from . import operational_f13 as opf
from . import raw_prior_val_1p5m as p20m
from .algebra import make_gf32

# Reused accepted contracts (read-only; never reimplemented here).
run_operational_block = p20o.run_operational_block
run_oracle_control_block = p20o.run_oracle_control_block
OracleControlResult = p20o.OracleControlResult
verify_predecessor_construction = p20o.verify_predecessor_construction
verify_dev_manifest_2m = p20o.verify_dev_manifest_2m
verify_session_prior_2m = p20o.verify_session_prior_2m
verify_alt_l2_arrays_2m = p20o.verify_alt_l2_arrays_2m
verify_alt_l2_identity_2m = p20o.verify_alt_l2_identity_2m
verify_stage_b_order_file_2m = p20o.verify_stage_b_order_file_2m
feasibility_literals_2m = p20o.feasibility_literals_2m
check_k_literals = p20o.check_k_literals
frozen_arm_table = p20o.frozen_arm_table
check_frozen_arm_table = p20o.check_frozen_arm_table
planned_totals = p20o.planned_totals
_l2_hazard_diagnostics = p20o._l2_hazard_diagnostics
_hazard_bits = p20o._hazard_bits
_raw_p2_from_counts = p20o._raw_p2_from_counts
first_error_coordinate = p20o.first_error_coordinate
l1_prefix_positions = p20o.l1_prefix_positions
l2_prefix_positions = p20o.l2_prefix_positions
seed_bits_for = p20o.seed_bits_for
_stat_record = p20o._stat_record
_block_view = p20o._block_view
_dev_block_scoring = p20o._dev_block_scoring
_scoring_absent = p20o._scoring_absent
_selected_diagnostics = p20o._selected_diagnostics
raw_prior_val_1p5m_block_events = p20o.raw_prior_val_1p5m_block_events
raw_prior_val_1p5m_recount_events = p20o.raw_prior_val_1p5m_recount_events
maintenance_diagnostics = p20o.maintenance_diagnostics
build_aggregates = p20o.build_aggregates
hazard_instrumentation_complete = p20o.hazard_instrumentation_complete
oracle_isolation_ok = p20o.oracle_isolation_ok
ArmSpec = p20o.ArmSpec

PROTOCOL_NAME = "nbpolar-p20q-hold-ir-confirmation-2m"
MODE = "hold-2m-ir-confirmation"

Q = p20o.Q  # 32
ALPHA = p20o.ALPHA  # 2
N_BOB = p20o.N_BOB  # 1024
FROZEN_N = 32768
FROZEN_SOURCE = "2M"
FROZEN_SOURCE_TAG = "type2_2M_20260121_183657"
FROZEN_FLOOR = 1e-15
FROZEN_ALPHA = 1.0
FROZEN_TARGET_F = 1.3
NORM_TOL = 1e-12
FROZEN_HAZARD_R = 8
FROZEN_PUBLIC_CONTROL_BITS = p20o.FROZEN_PUBLIC_CONTROL_BITS  # 327743
FROZEN_RAW_INPUT_BITS = 10 * FROZEN_N  # 327680 per block

# (d1/d8) 2M-HOLD population: FIRST 640 HOLD frames in (frame_id, pair_idx)
# order (frozen HOLD base 2916 = TRAIN 2187 + VAL 729 manifest-count
# arithmetic: DEV 2916..3555; five 128-frame blocks; HOLD remainder
# 3556..3644 counted never decoded; 2M TRAIN 0..2186 are the build frames;
# 2M VAL 2187..2915 consumed, never touched).
FROZEN_DEV_FRAME_RANGE = (2916, 3555)
FROZEN_DEV_FRAMES = 640
FROZEN_DEV_PAIRS = 163840
FROZEN_BLOCK_COUNT = 5
FROZEN_BLOCK_FRAMES = 128
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_BLOCK_RANGES = (
    (2916, 3043), (3044, 3171), (3172, 3299), (3300, 3427), (3428, 3555),
)
FROZEN_REMAINDER_FRAME_RANGE = (3556, 3644)
FROZEN_REMAINDER_FRAMES = 89
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
INTRA_FILE_HOLD_FRAME_RANGE = (2916, 3644)
CONSUMED_2M_TRAIN_FRAME_RANGE = (0, 2186)
CONSUMED_2M_VAL_FRAME_RANGE = (2187, 2915)
CONSUMED_2M_VAL_DEV_FRAME_RANGE = (2187, 2826)
CONSUMED_2M_VAL_REMAINDER_FRAME_RANGE = (2827, 2915)
# S2-ii build frames: counts/build frames hold 2M TRAIN 0..2186 only.
FROZEN_BUILD_FRAME_RANGE = (0, 2186)
# Consumed cross-session identities (fail-closed by source tag; frame
# integers alone are never identity).
CONSUMED_1M_SOURCE_TAG = p20o.CONSUMED_1M_SOURCE_TAG
CONSUMED_1P5M_SOURCE_TAG = p20o.CONSUMED_1P5M_SOURCE_TAG
CONSUMED_1M_FRAME_RANGE = (0, 1199)
CONSUMED_1P5M_FRAME_RANGE = (0, 2766)
FROZEN_MANIFEST_TRAIN_FRAMES = 2187
FROZEN_MANIFEST_TRAIN_PAIRS = 559872
FROZEN_MANIFEST_VAL_FRAMES = 729
FROZEN_MANIFEST_VAL_PAIRS = 186624
FROZEN_MANIFEST_HOLD_FRAMES = 729
FROZEN_MANIFEST_HOLD_PAIRS = 186624

# Device source identity: the 2M pairs parquet ONLY (same session file as
# P20O; provenance pin frozen by the v13r3fresh build-manifest cross-check;
# the 2M file itself is NEVER opened/statted/listed in Stage A). The
# size/sha literals below are build-manifest provenance constants; the size
# is additionally enforced from stat before the content open at run level.
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

# (d6) new P20Q tag domain.
FROZEN_TAG_MASTER = 2026092330
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = 64
SEED_PREFIX = "nbpolar-p20q-hold-ir-2m-seed"

# (d2/d3) P20O reuse pins, replayed as literals (never recomputed, never
# recarried; the alt-H literals are descriptive only, never budget inputs).
FROZEN_SESSION_PRIOR_DIGEST = (
    "b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587"
)
FROZEN_ORDER_DIGEST = (
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
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20Q-HOLD-IR-CONFIRMATION-2M/"
    "l2_alt_hold_ir_2m"
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "input_and_predecessor_identity.json",
    "per_block_arm_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)
ATTEMPT_CONSUMPTION_POINT = "first protected content open (HOLD pairs parquet)"
COMPLETE_LABEL = (
    "TARGET_EMPIRICAL_N32768_HOLD_IR_ALT_CONSTRUCTION_2M_COMPLETE"
)

# Exact keys of the reused Stage-A artifacts (no more, no fewer).
RAW_PRIOR_NPZ_KEYS = p20o.RAW_PRIOR_NPZ_KEYS  # 10 keys
ALT_L2_NPZ_KEYS = p20o.ALT_L2_NPZ_KEYS  # 9 keys

OPERATIONAL_PROVENANCE = p20o.OPERATIONAL_PROVENANCE
ORACLE_PROVENANCE = p20o.ORACLE_PROVENANCE

FROZEN_ARM_NAMES = p20o.FROZEN_ARM_NAMES
OPERATIONAL_ARM_NAMES = p20o.OPERATIONAL_ARM_NAMES
ORACLE_ARM_NAMES = p20o.ORACLE_ARM_NAMES
PLANNED_SC_CALLS = 30
PLANNED_TAG_INVOCATIONS = 20
PLANNED_RECORDS = 20

# (d7) mandatory IR-1..IR-5 pins (all frozen PRESENT, bounded,
# recording-only, post-decode; the truth-isolation boundary is pinned in
# the record writers and covered by the sentinel test).
IR1_BINS = 64
IR1_EDGE_LO_BITS = 1e-3
IR1_EDGE_HI_BITS = 32.0
IR3_LO_MULT = 1.0
IR3_HI_MULT = 2.0
IR4_TOPK = 16
IR5_CAP = 4096
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
    "ir5_series_hazard_bits",
    "ir5_series_in_prefix",
    "ir5_series_truncated",
    "ir5_series_total_len",
)

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "reuse_prior_identity",
    "reuse_alt_identity",
    "alt_construction_budget_feasibility_replayed",
    "dev_split_manifest_identity",
    "dev_block_range_identity",
    "order_derivation_identity",
    "k_literal_exact",
    "budget_literal_replayed",
    "target_population_contract",
    "dev_population_exact",
    "blocks_exact_with_declared_remainder",
    "twenty_records_exact",
    "genie_calls_exact",
    "sc_calls_exact",
    "tags_exact",
    "orders_valid_k_prefixes_within_registered_arms",
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


class L2AltHoldIr2mContractError(ValueError):
    """Pre-open population/formation failure: BLOCKED(<earliest gate>)."""


class L2AltHoldIr2mResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


def _gate_call(gate_name, fn, *args, **kwargs):
    """Run an accepted gate helper read-only, tagged with the P20Q gate name."""
    try:
        return fn(*args, **kwargs)
    except (ValueError, FileNotFoundError) as exc:
        raise L2AltHoldIr2mContractError(f"BLOCKED({gate_name}): {exc}") from exc


def pins_frozen() -> dict:
    """Fail-closed Stage-A pin-state check: every pin must be filled."""
    pins = {
        "session_prior_digest": FROZEN_SESSION_PRIOR_DIGEST,
        "order_digest": FROZEN_ORDER_DIGEST,
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
# Frozen CLI flag checks (both modes; all flags required, no default).
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
    if FROZEN_SESSION_PRIOR_DIGEST is None:
        raise ValueError("Stage-A freeze not yet applied: prior digest pin is None")
    digest = str(value)
    if digest != str(FROZEN_SESSION_PRIOR_DIGEST):
        raise ValueError(
            "frozen point requires prior-digest=<Stage-A 2M canonical prior digest>"
        )
    return digest


def _check_order_digest(value) -> str:
    if FROZEN_ORDER_DIGEST is None:
        raise ValueError("Stage-A freeze not yet applied: order digest pin is None")
    digest = str(value)
    if digest != str(FROZEN_ORDER_DIGEST):
        raise ValueError("frozen point requires order-digest=<Stage-A order-file sha256>")
    return digest


def _check_alt_digest(value) -> str:
    if FROZEN_ALT_DIGEST is None:
        raise ValueError("Stage-A freeze not yet applied: alt-table digest pin is None")
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
            or FROZEN_ALT_DIGEST is None or FROZEN_ORDER_DIGEST is None:
        raise ValueError("Stage-A freeze not yet applied: Stage-B pins are None")
    return (
        "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
        "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
        "ulimit -v 2097152\n"
        "timeout 1200 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
        "comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_ir_2m "
        f"--prior {FROZEN_PRIOR_PATH} --prior-digest {FROZEN_SESSION_PRIOR_DIGEST} "
        f"--alt-prior {FROZEN_ALT_PATH} --alt-digest {FROZEN_ALT_DIGEST} "
        f"--source 2M --floor 1e-15 --n 32768 --k1 {int(k1)} --k2 {int(k2)} "
        f"--construction {FROZEN_CONSTRUCTION_PATH} "
        f"--construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
        f"--dev-pairs {FROZEN_DEV_PAIRS_PATH} "
        "--dev-frames 2916 3555 --block-frames 128 --remainder-frames 3556 3644 "
        "--tag-master 2026092330 --chunk-rows 512 --tag-bits 64 "
        f"--order-file {FROZEN_ORDER_FILE_PATH} --order-digest {FROZEN_ORDER_DIGEST} "
        f"--out-dir {FROZEN_OUT_ROOT}"
    )


FROZEN_COMMAND = frozen_command() if pins_are_frozen() else None


# ---------------------------------------------------------------------------
# Stage-A reuse verification (worktree-file digest recomputation ONLY; zero
# protected opens at every stage; the V25 counts NPZ is never
# opened/statted/listed and HOLD is never contacted here).
# ---------------------------------------------------------------------------

def verify_reuse(
    *,
    prior,
    alt_prior,
    order_file,
    prior_digest: str,
    alt_digest: str,
    order_digest: str,
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
    """Replay the P20O reuse pins from worktree files BEFORE any HOLD contact.

    Loads the three frozen P20O worktree files read-only (never the V25
    counts NPZ, never any pairs parquet): canonical prior digest + H-literal
    recomputation within 1e-12 + ``p_b`` cross-check + floor pins (inside
    the accepted verifier), file-bytes alt/order digests + alpha-1.0/floor
    pins + exact key sets + ``p1``-equality within 1e-12 + descriptive alt-H
    replay, K-literal replay with the S2-i budget-literal display, and the
    D1/D2 feasibility replay recomputed from the worktree counts. Any
    replay mismatch raises with HOLD untouched (HOLD read stays 0/1) and no
    Stage-B request may follow.
    """
    with open(prior, "rb") as fh:
        data = np.load(fh, allow_pickle=False)
        with data:
            raw_arrays = {k: np.asarray(data[k]) for k in data.files}
    session_prior_verified = _gate_call(
        "reuse_prior_identity", verify_session_prior_2m,
        raw_arrays, expected_digest=str(prior_digest),
        expected_h1=float(h1), expected_h2=float(h2),
        expected_total=float(h_total))
    k_literals = _gate_call(
        "k_literal_exact", check_k_literals, k1=k1, k2=k2)
    if str(k_literals["budget_literal"]) != str(FROZEN_BUDGET_LITERAL):
        raise L2AltHoldIr2mContractError(
            "BLOCKED(k_literal_exact): budget-literal display != frozen S2-i replay"
        )
    alt_verified = _gate_call(
        "reuse_alt_identity", verify_alt_l2_identity_2m, str(alt_prior),
        expected_digest=str(alt_digest), incumbent_arrays=raw_arrays)
    order_pin = _gate_call(
        "reuse_order_freeze", verify_stage_b_order_file_2m, str(order_file),
        expected_digest=str(order_digest),
        expected_prior_digest=str(prior_digest),
        expected_k1=int(k1), expected_k2=int(k2),
        expected_k_total=int(k_literals["k_total"]))
    counts_ab = np.asarray(raw_arrays["counts_ab"], dtype=np.float64)
    d1 = feasibility_literals_2m(
        counts_ab, p2_incumbent=np.asarray(raw_arrays["p2"]),
        p2_alt=np.asarray(alt_verified["p2_alt"]),
        k2=int(k2), k_total=int(k_literals["k_total"]))
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
        raise L2AltHoldIr2mContractError(
            "BLOCKED(alt_construction_budget_feasibility_replayed): "
            "D1/D2 replay mismatch: " + ",".join(replay_failing)
            + " (HOLD untouched, no Stage-B request)"
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
        "order_digest": str(order_pin["order_digest"]),
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
        "hold_contact": 0,
        "verified": True,
    }


# ---------------------------------------------------------------------------
# (d1/d8) gate family (a)->(g): cross-file first, then intra-file
# HOLD-containment, consumed-1M / consumed-1.5M / consumed-2M (TRAIN-as-DEV
# + VAL DEV + VAL remainder) exclusions incl. the DEV/build-frames
# disjointness declaration (S2-ii), then reuse-prior + reuse-alt +
# order-freeze + K-literal + hold-confirmation-identity pins. All pure
# code-level checks (no I/O); any violation raises before any protected
# content open.
# ---------------------------------------------------------------------------

def verify_dev_source_identity_2m(dev_pairs=None) -> dict:
    """Gate (a): cross-file 2M source identity (FIRST, before any open)."""
    candidate = FROZEN_DEV_PAIRS_PATH if dev_pairs is None else str(dev_pairs)
    if candidate == REFUSED_1M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20Q DEV source gate: 1M full-pool path refused "
            f"({REFUSED_1M_DEV_PAIRS_PATH!r}); the entire 1M pool is "
            "fail-closed against P20Q DEV selection"
        )
    if candidate == REFUSED_1P5M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20Q DEV source gate: 1.5M session path refused "
            f"({REFUSED_1P5M_DEV_PAIRS_PATH!r}); the entire 1.5M session is "
            "fail-closed against P20Q DEV selection"
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
        raise ValueError("P20Q DEV source identity mismatch: " + ",".join(failing))
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


def verify_hold_containment(dev_frames=None, remainder_frames=None) -> dict:
    """Gate (b): intra-file 2M HOLD containment (HOLD 2916..3644)."""
    dev_pair = (tuple(FROZEN_DEV_FRAME_RANGE) if dev_frames is None
                else tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    hold_first, hold_last = INTRA_FILE_HOLD_FRAME_RANGE
    train_first, train_last = CONSUMED_2M_TRAIN_FRAME_RANGE
    val_first, val_last = CONSUMED_2M_VAL_FRAME_RANGE
    dev_first, dev_last = dev_pair
    rem_first, rem_last = rem_pair
    for label, (start, end) in (("DEV", dev_pair), ("remainder", rem_pair)):
        if not (hold_first <= start and end <= hold_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"lies outside 2M HOLD {hold_first}..{hold_last}"
            )
        if not (end < train_first or start > train_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"overlaps 2M TRAIN {train_first}..{train_last}"
            )
        if not (end < val_first or start > val_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"overlaps consumed 2M VAL {val_first}..{val_last}"
            )
    if dev_pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): DEV {dev_pair} != frozen "
            f"{tuple(FROZEN_DEV_FRAME_RANGE)} (FIRST 640 HOLD frames)"
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
            "the five HOLD DEV blocks end"
        )
    return {
        "dev_frame_range": [int(dev_first), int(dev_last)],
        "remainder_frame_range": [int(rem_first), int(rem_last)],
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "intra_file_hold_frame_range": [int(hold_first), int(hold_last)],
        "hold_contained": True,
        "train_exterior_disjoint": True,
        "val_disjoint": True,
        "first_640_hold_frames": True,
        "verified": True,
    }


def verify_consumed_exclusions_hold(dev_frames=None, remainder_frames=None) -> dict:
    """Gates (c)-(e): consumed-1M / consumed-1.5M / consumed-2M + S2-ii."""
    dev_pair = (tuple(FROZEN_DEV_FRAME_RANGE) if dev_frames is None
                else tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    ranges = [tuple(dev_pair)] + [tuple(r) for r in FROZEN_BLOCK_RANGES]
    for label, (start, end) in (
            ("consumed 2M TRAIN 0..2186", CONSUMED_2M_TRAIN_FRAME_RANGE),
            ("consumed 2M VAL 2187..2915", CONSUMED_2M_VAL_FRAME_RANGE)):
        for r_start, r_end in ranges:
            if not (r_end < start or r_start > end):
                raise ValueError(
                    f"BLOCKED(dev_block_range_identity): declared range "
                    f"{r_start}..{r_end} overlaps {label}"
                )
    if not (rem_pair[1] < CONSUMED_2M_VAL_FRAME_RANGE[0]
            or rem_pair[0] > CONSUMED_2M_VAL_FRAME_RANGE[1]):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): declared HOLD remainder "
            f"{rem_pair[0]}..{rem_pair[1]} overlaps consumed 2M VAL"
        )
    build_first, build_last = FROZEN_BUILD_FRAME_RANGE
    dev_first, dev_last = dev_pair
    if (build_first, build_last) != CONSUMED_2M_TRAIN_FRAME_RANGE:
        raise ValueError("build-frames declaration drifted from 2M TRAIN 0..2186")
    if not (build_last < dev_first or dev_last < build_first):
        raise ValueError("DEV/build-frames disjointness violated (S2-ii)")
    if FROZEN_SOURCE_TAG == CONSUMED_1M_SOURCE_TAG \
            or FROZEN_SOURCE_TAG == CONSUMED_1P5M_SOURCE_TAG:
        raise ValueError("DEV source tag collides with a consumed session (impossible)")
    return {
        "build_frames": [int(build_first), int(build_last)],
        "dev_frames": [int(dev_first), int(dev_last)],
        "remainder_frames": [int(rem_pair[0]), int(rem_pair[1])],
        "dev_source_tag": FROZEN_SOURCE_TAG,
        "consumed_1m_source_tag": CONSUMED_1M_SOURCE_TAG,
        "consumed_1p5m_source_tag": CONSUMED_1P5M_SOURCE_TAG,
        "consumed_1m_frames": list(CONSUMED_1M_FRAME_RANGE),
        "consumed_1p5m_frames": list(CONSUMED_1P5M_FRAME_RANGE),
        "consumed_2m_train_disjoint": True,
        "consumed_2m_val_disjoint": True,
        "consumed_1m_disjoint_by_identity": True,
        "consumed_1p5m_disjoint_by_identity": True,
        "hold_remainder_never_decoded": True,
        "disjoint": True,
        "verified": True,
    }


def form_hold_blocks(
    table,
    *,
    dev_frames=FROZEN_DEV_FRAME_RANGE,
    block_frames: int = FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
) -> dict:
    """Deterministic 2M HOLD development validation plus block/remainder slicing."""
    try:
        pair = tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames)
    except TypeError as exc:
        raise TypeError(f"dev-frames must be a pair of integers: {exc}") from exc
    if pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise L2AltHoldIr2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"dev-frames {pair} != frozen {tuple(FROZEN_DEV_FRAME_RANGE)}"
        )
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise L2AltHoldIr2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"block-frames {block_frames} != frozen {FROZEN_BLOCK_FRAMES}"
        )
    try:
        rem_pair = tuple(opf._as_int(v, "remainder-frames", minimum=0)
                         for v in remainder_frames)
    except TypeError as exc:
        raise TypeError(f"remainder-frames must be a pair of integers: {exc}") from exc
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise L2AltHoldIr2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"remainder-frames {rem_pair} != frozen {tuple(FROZEN_REMAINDER_FRAME_RANGE)}"
        )
    try:
        frame_id = np.asarray(table["frame_id"], dtype=np.int64)
        pair_idx = np.asarray(table["pair_idx"], dtype=np.int64)
        alice = np.asarray(table["alice_symbol"], dtype=np.int64)
        bob = np.asarray(table["bob_symbol"], dtype=np.int64)
    except (KeyError, TypeError, ValueError) as exc:
        raise L2AltHoldIr2mContractError(
            f"BLOCKED(dev_population_exact): loader frame is malformed: {exc}"
        ) from exc
    if not (frame_id.shape == pair_idx.shape == alice.shape == bob.shape) \
            or frame_id.ndim != 1:
        raise L2AltHoldIr2mContractError(
            "BLOCKED(dev_population_exact): column shapes disagree"
        )
    for name, values in (("alice_symbol", alice), ("bob_symbol", bob)):
        if values.size == 0 or values.min() < 0 or values.max() >= N_BOB:
            raise L2AltHoldIr2mContractError(
                f"BLOCKED(dev_population_exact): {name} outside 0..{N_BOB - 1}"
            )
    dev_first, dev_last = pair
    pool_frame_id = np.asarray(table["frame_id"], dtype=np.int64)
    selected = (frame_id >= dev_first) & (frame_id <= dev_last)
    rows = int(np.sum(selected))
    if rows == 0:
        raise L2AltHoldIr2mContractError(
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
        raise L2AltHoldIr2mContractError(
            "BLOCKED(dev_population_exact): DEV frames "
            f"{unique_frames.size} with range {int(unique_frames[0])}.."
            f"{int(unique_frames[-1])} != frozen {FROZEN_DEV_FRAMES} with range "
            f"{dev_first}..{dev_last}"
        )
    if rows != FROZEN_DEV_PAIRS:
        raise L2AltHoldIr2mContractError(
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
        raise L2AltHoldIr2mContractError(
            "BLOCKED(dev_population_exact): pair_idx is not exactly 0..255 per frame"
        )
    ranges = []
    first = dev_first
    for _ in range(FROZEN_BLOCK_COUNT):
        last = first + int(block_frames) - 1
        ranges.append((first, last))
        first = last + 1
    if tuple(ranges) != tuple(tuple(r) for r in FROZEN_BLOCK_RANGES):
        raise L2AltHoldIr2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): block ranges "
            f"{tuple(ranges)} != frozen {tuple(tuple(r) for r in FROZEN_BLOCK_RANGES)}"
        )
    rem_first, rem_last = rem_pair
    if first != rem_first:
        raise L2AltHoldIr2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder "
            f"{rem_first}..{rem_last} does not start where the five DEV blocks end"
        )
    remainder_rows = (pool_frame_id >= rem_first) & (pool_frame_id <= rem_last)
    remainder_frame_ids = pool_frame_id[remainder_rows]
    if int(np.sum(remainder_rows)) != FROZEN_REMAINDER_SYMBOLS:
        raise L2AltHoldIr2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder rows "
            f"{int(np.sum(remainder_rows))} != frozen {FROZEN_REMAINDER_SYMBOLS}"
        )
    if (np.unique(remainder_frame_ids).size != FROZEN_REMAINDER_FRAMES
            or int(remainder_frame_ids.min()) != rem_first
            or int(remainder_frame_ids.max()) != rem_last):
        raise L2AltHoldIr2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder frames "
            f"!= frozen {rem_first}..{rem_last} ({FROZEN_REMAINDER_FRAMES} frames)"
        )
    check = verify_hold_containment(pair, rem_pair)
    if not check["verified"]:
        raise L2AltHoldIr2mContractError("BLOCKED(dev_block_range_identity)")
    check2 = verify_consumed_exclusions_hold(pair, rem_pair)
    if not check2["verified"]:
        raise L2AltHoldIr2mContractError("BLOCKED(dev_block_range_identity)")
    blocks = []
    for index, (start, end) in enumerate(ranges):
        mask = (frame_id >= start) & (frame_id <= end)
        if int(np.sum(mask)) != FROZEN_SYMBOLS_PER_BLOCK:
            raise L2AltHoldIr2mContractError(
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
# (d6) P20Q tag domain.
# ---------------------------------------------------------------------------

def l2_alt_hold_ir_2m_seed_bits(master: int, n: int, arm: str, block_index: int,
                                *, bit_length: int | None = None) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P20Q domain)."""
    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P20Q seed domain: {arm!r}")
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
# (d7) Mandatory IR-1..IR-5 recorder (recording-only, post-decode).
# ---------------------------------------------------------------------------

def _ir_hist_edges() -> np.ndarray:
    """Frozen IR-1 bin edges: 65 float64, log-spaced over hazard-bits."""
    return np.concatenate((
        np.array([0.0], dtype=np.float64),
        np.logspace(np.log10(IR1_EDGE_LO_BITS), np.log10(IR1_EDGE_HI_BITS),
                    IR1_BINS, dtype=np.float64),
    ))


def _ir_hist_counts(hazards: np.ndarray, edges: np.ndarray) -> list:
    idx = np.clip(np.searchsorted(edges, hazards, side="right") - 1, 0, IR1_BINS - 1)
    counts = np.bincount(idx.astype(np.int64), minlength=IR1_BINS)
    return [int(v) for v in counts]


def _ir_hazard_diagnostics(*, view, p2_arm, l2_order, k2, first_error,
                           prefix_mean) -> dict:
    """P20Q mandatory IR recorder: IR-1..IR-5, post-decode, recording-only.

    Called after every SC call for the record has completed (after tag
    scoring) from the successor's ``_operational_record`` /
    ``_control_record`` equivalents alongside the nine carried scalars (the
    P20O ``_l2_hazard_diagnostics`` code point is the carried-over callsite
    pattern). Reads truth (and the arm table) for RECORDING ONLY; its
    outputs are written into the record dict and are never passed to any
    decoder, metric builder, disclosure or order decision.

    Fields (frozen semantics):
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


def ir_payload_complete(records) -> bool:
    """IR-1..IR-5 all PRESENT with frozen caps/nullability per record."""
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
        series = record.get("ir5_series_hazard_bits")
        if series is None or len(series) > IR5_CAP:
            return False
        if len(record.get("ir5_series_in_prefix", [])) != len(series):
            return False
        if record.get("ir5_series_truncated") is not True:
            return False
        if int(record.get("ir5_series_total_len", -1)) != int(FROZEN_N):
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
    trunc_flags = []
    for record in completed:
        pct = record.get("ir2_first_error_hazard_rank_pct")
        arm = str(record.get("arm"))
        if pct is not None:
            pct = float(pct)
            ir2_all.append(pct)
            if arm == "A_incumbent_L2_operational":
                ir2_a.append(pct)
            elif arm == "B_alt_L2_operational":
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
# Stage-B records (construction point + floor fields + nine carried scalars
# + IR-1..IR-5). The P20O ``_l2_hazard_diagnostics`` callsite pattern is
# carried over; the IR call sits directly beside it, post-decode.
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
        "l2_construction": spec.prior_source,
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
        "l1_order_digest": str(order_digest),
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
    # Recording-only recorders at the carried-over P20O code point; all SC
    # calls for this record have completed before these calls. Truth enters
    # for RECORDING ONLY and never flows back into any decoder input.
    view_arm = dict(view)
    view_arm["u1_cond"] = (
        result.high_hat if result.high_hat is not None else view["high"])
    nine = _l2_hazard_diagnostics(
        block=block, view=view_arm, p2_arm=p2, counts_arr=counts_arr,
        l2_order=l2_order, k2=FROZEN_K2, first_error=first_error,
        field=field, low_hat=result.low_hat)
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
    nine = _l2_hazard_diagnostics(
        block=block, view=view_arm, p2_arm=p2, counts_arr=counts_arr,
        l2_order=l2_order, k2=FROZEN_K2, first_error=first_error,
        field=field, low_hat=result.low_hat)
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
        "l2_construction": spec.prior_source,
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
        "l1_order_digest": str(order_digest),
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
    for field in p20o.HAZARD_FIELDS:
        record[field] = (
            str(FROZEN_ORDER_DIGEST) if field == "l2_order_digest"
            else (int(FROZEN_K2) if field == "l2_prefix_len" else None)
        )
    for field in IR_FIELDS:
        record[field] = None
    return record


# ---------------------------------------------------------------------------
# Stage-B integrity gates (frozen section 9 order; all true or BLOCKED).
# ---------------------------------------------------------------------------

def _integrity_gates(*, n, k1, k2, k_total, arms, identity, manifest,
                     dev_source_pin, dev_pin, disjoint_pin, order_pin,
                     formation, records, events, calls, incremental, accounting,
                     provenance_violations, cap, wall_s, resource_stop,
                     session_prior_verified, alt_verified, hazard_pin,
                     prior_stat_before, prior_stat_after, alt_stat_before,
                     alt_stat_after, dev_stat_before, dev_stat_after,
                     registered_paths, opened_paths, final: bool) -> dict:
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
        order_pin is not None and bool(order_pin.get("verified")))
    try:
        gates["k_literal_exact"] = bool(
            bool(hazard_pin.get("k_literal"))
            and int(k1) == int(FROZEN_K1) and int(k2) == int(FROZEN_K2)
            and int(k1) + int(k2) == int(FROZEN_K_TOTAL)
            and str(hazard_pin.get("budget_literal")) == str(FROZEN_BUDGET_LITERAL))
    except (AttributeError, TypeError, ValueError):
        gates["k_literal_exact"] = False
    try:
        recomputed = p20m.verify_budget_literal(
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
    gates["twenty_records_exact"] = (
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
        shared_l1 = l1_prefix_positions(order_pin["l1_order"], int(k1))
        shared_l2 = l2_prefix_positions(order_pin["l2_order"], int(k2))
        orders_ok = (
            shared_l1.shape == (int(k1),)
            and shared_l2.shape == (int(k2),)
            and int(arms[0].k1) == int(k1) and int(arms[0].k2) == int(k2)
            and int(arms[1].k1) == int(k1) and int(arms[1].k2) == int(k2)
            and int(arms[2].k1) == 0 and int(arms[2].k2) == int(k2)
            and int(arms[3].k1) == 0 and int(arms[3].k2) == int(k2)
        )
    except (ValueError, IndexError, AttributeError, TypeError):
        orders_ok = False
    gates["orders_valid_k_prefixes_within_registered_arms"] = bool(orders_ok)
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


def l2_alt_hold_ir_2m_label(gates: dict) -> str:
    """Descriptive COMPLETE iff every integrity gate holds, else BLOCKED(first)."""
    failing = [g for g in INTEGRITY_GATE_ORDER if not gates.get(g, False)]
    if not failing:
        return COMPLETE_LABEL
    return f"BLOCKED({failing[0]})"


@dataclass(frozen=True, eq=False)
class L2AltHoldIr2mRun:
    """In-memory P20Q Stage-B run (also returned by the runner)."""

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
                       order_file, order_digest, identity, manifest,
                       dev_source_pin, dev_pin, disjoint_pin, order_pin) -> dict:
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
        "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
        "consumed_2m_train_frame_range": list(CONSUMED_2M_TRAIN_FRAME_RANGE),
        "consumed_2m_val_frame_range": list(CONSUMED_2M_VAL_FRAME_RANGE),
        "consumed_sessions": {
            "1m_pool": {"source_tag": CONSUMED_1M_SOURCE_TAG,
                        "frames": list(CONSUMED_1M_FRAME_RANGE)},
            "1p5m_session": {"source_tag": CONSUMED_1P5M_SOURCE_TAG,
                             "frames": list(CONSUMED_1P5M_FRAME_RANGE)},
            "2m_train_build": {"source_tag": FROZEN_SOURCE_TAG,
                               "frames": list(CONSUMED_2M_TRAIN_FRAME_RANGE)},
            "2m_val": {"source_tag": FROZEN_SOURCE_TAG,
                       "frames": list(CONSUMED_2M_VAL_FRAME_RANGE)},
        },
        "tag_master": int(tag_master),
        "tag_seed_domain": f"{SEED_PREFIX}:<master>:<n>:<arm>:<block_index>",
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "order_file": str(order_file),
        "order_digest": str(order_digest),
        "order_k1": int(order_pin.get("k1", -1)),
        "order_k2": int(order_pin.get("k2", -1)),
        "identity_n": int(identity.get("n", -1)) if isinstance(identity, dict) else None,
        "arms": [
            {"name": spec.name, "kind": spec.kind, "k1": int(spec.k1),
             "k2": int(spec.k2), "leakage_bits": int(spec.leakage_bits),
             "l2_construction": spec.prior_source,
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
        "hazard_fields": list(p20o.HAZARD_FIELDS),
        "u_domain_scalar_frozen_present": True,
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
    lines = [
        "# NB-Polar Phase 4-P20Q instrumented alpha1 confirmation on 2M HOLD "
        "with mandatory H2 IR-1..IR-5",
        "",
        f"- protocol: `{summary.get('analysis')}` (mode `{summary.get('mode')}`)",
        f"- source: `{summary.get('source')}`; N={summary.get('n')}; "
        f"K1={summary.get('k1')} K2={summary.get('k2')} K_total={summary.get('k_total')} "
        "(2M-session-derived, S2-i literal replay)",
        "- alt-L2 construction: unit-pseudocount conditional; alt-table digest "
        f"`{summary.get('alt_digest')}`",
        f"- order file digest: `{summary.get('order_digest')}` "
        f"(shared first-{summary.get('k1')} / first-{summary.get('k2')} prefixes "
        "on all four arms)",
        f"- blocks: {summary.get('block_ranges')} "
        f"(remainder {summary.get('remainder_frames')} never used)",
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
        "descriptive HOLD confirmation reading on FIRST-USE 2M HOLD: no "
        "recovery / FER / superiority / qualification / promotion / reliability "
        "claim is made, and the H2 decision stays main-thread analysis after "
        "acceptance.",
        "",
    ]
    return "\n".join(lines)


def run_l2_alt_hold_ir_2m(
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
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
) -> L2AltHoldIr2mRun:
    """Execute the frozen P20Q four-arm HOLD-IR confirmation once; write five files.

    ``prior`` / ``alt_prior`` / ``dev_table`` are documented injected test
    seams; the frozen CLI passes only the frozen point, loads the Stage-A
    frozen 2M raw prior and alt table read-only exactly once each, loads
    the frozen 2M order file read-only behind the order-digest gate, and
    reads the 2M HOLD parquet through its accepted loader exactly once.
    The V25 counts NPZ is never opened at any stage. The construction swap
    is hardcoded (never CLI-tunable): A runs the incumbent L2 at the
    Stage-A (K1,K2), B the alt L2 at the SAME point, C the incumbent
    true-L1 oracle and D the alt true-L1 oracle at K2, all four on the
    SAME frozen 2M order prefixes. Stage B performs ZERO sampling (no
    seed flag, no sampler call; the genie counter is gated at 0).
    """
    global _SESSION_PRIOR_CONTENT_LOADED, _ALT_CONTENT_LOADED
    global _DEV_PARQUET_CONTENT_OPENED
    pins = pins_frozen()
    if pins["d2_feasible"] is not True:
        raise ValueError(
            "BLOCKED(alt_construction_budget_feasibility_replayed): Stage-A D2 "
            "outcome is not FEASIBLE (HOLD untouched; no Stage-B run)"
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
    order_digest = _check_order_digest(order_digest)
    if alt_digest is None:
        raise ValueError("frozen point requires --alt-digest equal to the Stage-A pin")
    alt_digest = _check_alt_digest(alt_digest)
    arms = frozen_arm_table() if check_frozen_arm_table() else ()

    # Gate family (a)->(g) in the frozen order before any protected content
    # open: predecessor construction identity, cross-file source identity
    # (a), intra-file HOLD-containment (b), consumed-1M / consumed-1.5M /
    # consumed-2M (TRAIN-as-DEV + VAL DEV + VAL remainder) + S2-ii (c)-(e),
    # then reuse-prior + reuse-alt + order-freeze + K-literal +
    # hold-confirmation-identity pins (f)-(g).
    if str(construction_digest) != str(FROZEN_CONSTRUCTION_DIGEST):
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = _gate_call("predecessor_construction_identity",
                          verify_predecessor_construction, construction,
                          expected_digest=construction_digest)
    identity = verified["record"]
    dev_source_pin = _gate_call("dev_block_range_identity",
                                verify_dev_source_identity_2m, dev_pairs)
    dev_pin = verify_hold_containment(dev_frames, remainder_frames)
    disjoint_pin = verify_consumed_exclusions_hold(dev_frames, remainder_frames)
    manifest = _gate_call("dev_split_manifest_identity", verify_dev_manifest_2m,
                          manifest_path, source=source)
    order_pin = _gate_call(
        "order_derivation_identity", verify_stage_b_order_file_2m, order_file,
        expected_digest=order_digest,
        expected_prior_digest=str(FROZEN_SESSION_PRIOR_DIGEST),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    # Hold-confirmation identity (g): the construction quadruple + tag
    # domain + source vocabulary must match the P20Q freeze.
    hold_identity = {
        "construction_quadruple": (PROTOCOL_NAME, MODE, FROZEN_SOURCE, SEED_PREFIX),
        "tag_master": int(tag_master),
        "order_digest": str(order_digest),
        "k1": int(k1),
        "k2": int(k2),
    }
    if hold_identity["construction_quadruple"] != (
            "nbpolar-p20q-hold-ir-confirmation-2m", "hold-2m-ir-confirmation",
            "2M", "nbpolar-p20q-hold-ir-2m-seed"):
        raise L2AltHoldIr2mContractError(
            "BLOCKED(dev_block_range_identity): hold-confirmation identity drifted")
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
        raise ValueError("reopen refused: the single HOLD parquet content open was consumed")

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
            raise FileNotFoundError(f"2M HOLD pairs parquet not found: {dev_path_obj}")
        dev_stat_before = _stat_record(dev_path_obj)
        if dev_stat_before["size_bytes"] != FROZEN_DEV_PAIRS_SIZE:
            raise ValueError(
                "2M HOLD pairs size mismatch before content open: "
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
        order_file=order_file, order_digest=order_digest, identity=identity,
        manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
        disjoint_pin=disjoint_pin, order_pin=order_pin)
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
        "pairs_loader": p20l.PAIRS_LOADER_IDENTITY if real_dev else None,
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

        # ---- input 3: the single HOLD parquet content open, HOLD rows only.
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
        formation = form_hold_blocks(
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
            "incumbent": (p1_inc, p2_inc, counts_inc),
            "alt": (p1_alt, p2_alt, counts_alt),
        }

        def current_gates(*, final: bool, wall_now: float) -> tuple:
            gates = _integrity_gates(
                n=n, k1=k1, k2=k2, k_total=k_total, arms=arms, identity=identity,
                manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
                disjoint_pin=disjoint_pin, order_pin=order_pin,
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
                "order_digest": str(order_pin.get("order_digest")),
                "alt_h_literals": alt_h_literals,
                "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
                "remainder_frames": list(FROZEN_REMAINDER_FRAME_RANGE),
                "dev_source": dict(dev_source_pin),
                "build_dev_disjointness_s2_ii": dict(disjoint_pin),
                "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
                "consumed_2m_val_frame_range": list(CONSUMED_2M_VAL_FRAME_RANGE),
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
                    "descriptive first-use 2M HOLD IR confirmation of the "
                    "frozen ALT-L2-LAPLACE-alpha1 construction at the per-session "
                    "(2M-TRAIN-derived) disclosure point (N=32768, five HOLD blocks "
                    "2916..3555) with the mandatory H2 IR-1..IR-5 payload under each "
                    "construction; C/D are oracle-labelled diagnostic controls, never an "
                    "operational protocol or deployable result; not real-frame FER, "
                    "reconciliation efficiency, leakage, key rate, scaling superiority, "
                    "qualification or promotion evidence; the CE-normalized disclosure "
                    "ratio is not qualification efficiency; undetected is never success; "
                    "no reliability, recovery or maintenance claim is licensed; the H2 "
                    "decision is main-thread analysis after acceptance, not a FER result; "
                    "2M HOLD is consumed by this packet regardless of outcome"
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
                        order_digest=order_digest)
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
            seed = l2_alt_hold_ir_2m_seed_bits(
                tag_master, n, spec.name, block_index, bit_length=seed_bits_for(n))

            def _tag_fn(bits, _seed, tag_bits, _fixed=seed):
                return toeplitz_tag(bits, _fixed, tag_bits)

            block_start = time.perf_counter()
            p1_use, p2_use, counts_use = prior_by_source[spec.prior_source]
            l1_use = np.asarray(order_pin["l1_order"], dtype=np.int64)
            l2_use = np.asarray(order_pin["l2_order"], dtype=np.int64)
            if spec.kind == "operational":
                # A/B share the accepted operational path bit-for-bit except
                # the L2 table: A runs the incumbent p2, B the alt p2, both
                # at the SAME Stage-A point on the SAME frozen 2M order
                # prefixes. The swap is hardcoded, never CLI-tunable.
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
                    order_digest=order_digest, counts_arr=counts_use, p1=p1_use,
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
                    order_digest=order_digest, counts_arr=counts_use, p1=p1_use,
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
            disjoint_pin=disjoint_pin, order_pin=order_pin,
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
        outcome_label = l2_alt_hold_ir_2m_label(gates)
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
            "order_file_pin": {
                "order_file": str(order_pin.get("order_file")),
                "order_digest": str(order_pin.get("order_digest")),
                "n": int(order_pin.get("n", -1)),
                "k1": int(order_pin.get("k1", -1)),
                "k2": int(order_pin.get("k2", -1)),
                "prior_digest": str(order_pin.get("prior_digest")),
                "train_seeds": [int(s) for s in order_pin.get("train_seeds", [])],
                "derivation_seed_pins_provenance_only": True,
                "verified": bool(order_pin.get("verified")),
            },
            "expected_order_digest": str(order_digest),
            "hold_confirmation_identity": hold_identity,
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
        return L2AltHoldIr2mRun(summary=summary, records=tuple(records), gates=gates)
    except L2AltHoldIr2mResourceError:
        raise
    except MemoryError as exc:
        raise L2AltHoldIr2mResourceError(
            f"resource stop: MemoryError: {exc}") from exc


VERIFY_REUSE_FLAGS = (
    "prior", "prior_digest", "alt_prior", "alt_digest",
    "k1", "k2", "order_file", "order_digest",
)
SHARED_FLAGS = ("source", "floor", "n")
STAGE_B_ONLY_FLAGS = (
    "prior", "prior_digest", "alt_prior", "alt_digest", "k1", "k2", "construction",
    "construction_digest", "dev_pairs", "dev_frames", "block_frames",
    "remainder_frames", "tag_master", "chunk_rows", "tag_bits",
    "order_file", "order_digest", "out_dir",
)
STAGE_B_FLAGS = SHARED_FLAGS + STAGE_B_ONLY_FLAGS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p20q-hold-ir-confirmation-2m",
        description=(
            "NB-Polar Phase 4-P20Q instrumented alpha1 confirmation on "
            "first-use 2M HOLD with mandatory H2 IR-1..IR-5: --verify-reuse "
            "replays the P20O reuse pins from worktree files with zero "
            "protected opens; otherwise all Stage-B flags are required "
            "(frozen command, no production default)"
        ),
    )
    parser.add_argument("--verify-reuse", action="store_true",
                        dest="verify_reuse",
                        help="Stage-A reuse-verification mode (all reuse flags required)")
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
    parser.add_argument("--out-dir", default=None, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
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
                order_file=args.order_file, prior_digest=args.prior_digest,
                alt_digest=args.alt_digest, order_digest=args.order_digest,
                h1=FROZEN_H1, h2=FROZEN_H2, h_total=FROZEN_H_TOTAL,
                k1=args.k1, k2=args.k2, ce_alt=FROZEN_CE_ALT,
                ce_incumbent=FROZEN_CE_INCUMBENT,
                alt_ideal_length_bits=FROZEN_ALT_IDEAL_LENGTH_BITS,
                d2_feasible=FROZEN_D2_FEASIBLE)
            print(json.dumps({
                "reuse_prior_digest": result["prior_digest"],
                "reuse_alt_digest": result["alt_file_digest"],
                "reuse_order_digest": result["order_digest"],
                "k_total": result["k_literals"]["k_total"],
                "d2_feasible": result["d2_feasible"],
                "d2_margin_bits": result["d2_margin_bits"],
                "hold_contact": result["hold_contact"],
                "verified": result["verified"],
            }, sort_keys=True))
            return 0
        given = [name for name in STAGE_B_FLAGS if getattr(args, name) is not None]
        missing = [name for name in STAGE_B_FLAGS if getattr(args, name) is None]
        if missing:
            if not given:
                raise ValueError(
                    "ambiguous invocation refused: neither --verify-reuse nor any "
                    "Stage-B flag was given; refusing before any read or write"
                )
            raise ValueError(
                "missing required Stage-B flags: " + ",".join(missing)
                + "; refusing before any read or write"
            )
        run = run_l2_alt_hold_ir_2m(
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
            "ir_payload": summary["aggregates"]["ir_payload"],
            "integrity_all_pass": summary["integrity_all_pass"],
            "outcome_label": summary["outcome_label"],
            "out_root": args.out_dir,
        }, sort_keys=True))
        return 0
    except (ValueError, FileExistsError, OSError,
            L2AltHoldIr2mContractError) as exc:
        print(f"nbpolar phase4-p20q 2m hold-ir refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL_NAME", "MODE", "Q", "ALPHA", "N_BOB", "FROZEN_N", "FROZEN_SOURCE",
    "FROZEN_SOURCE_TAG", "FROZEN_FLOOR", "FROZEN_ALPHA", "FROZEN_TARGET_F",
    "NORM_TOL", "FROZEN_HAZARD_R", "FROZEN_PUBLIC_CONTROL_BITS",
    "FROZEN_RAW_INPUT_BITS", "FROZEN_DEV_FRAME_RANGE", "FROZEN_DEV_FRAMES",
    "FROZEN_DEV_PAIRS", "FROZEN_BLOCK_COUNT", "FROZEN_BLOCK_FRAMES",
    "FROZEN_PAIRS_PER_FRAME", "FROZEN_SYMBOLS_PER_BLOCK", "FROZEN_BLOCK_RANGES",
    "FROZEN_REMAINDER_FRAME_RANGE", "FROZEN_REMAINDER_FRAMES",
    "FROZEN_REMAINDER_SYMBOLS", "INTRA_FILE_HOLD_FRAME_RANGE",
    "CONSUMED_2M_TRAIN_FRAME_RANGE", "CONSUMED_2M_VAL_FRAME_RANGE",
    "CONSUMED_2M_VAL_DEV_FRAME_RANGE", "CONSUMED_2M_VAL_REMAINDER_FRAME_RANGE",
    "FROZEN_BUILD_FRAME_RANGE", "FROZEN_MANIFEST_TRAIN_FRAMES",
    "FROZEN_MANIFEST_TRAIN_PAIRS", "FROZEN_MANIFEST_VAL_FRAMES",
    "FROZEN_MANIFEST_VAL_PAIRS", "FROZEN_MANIFEST_HOLD_FRAMES",
    "FROZEN_MANIFEST_HOLD_PAIRS", "FROZEN_DEV_PAIRS_PATH", "FROZEN_DEV_PAIRS_SIZE",
    "FROZEN_DEV_PAIRS_SHA256", "REFUSED_1M_DEV_PAIRS_PATH",
    "REFUSED_1P5M_DEV_PAIRS_PATH", "FROZEN_DEV_BUILD_MANIFEST_PATH",
    "FROZEN_CONSTRUCTION_PATH", "FROZEN_CONSTRUCTION_DIGEST",
    "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA", "PAIRS_LOADER_IDENTITY",
    "FROZEN_TAG_MASTER", "FROZEN_CHUNK_ROWS", "FROZEN_TAG_BITS", "SEED_PREFIX",
    "FROZEN_PRIOR_PATH", "FROZEN_ORDER_FILE_PATH", "FROZEN_ALT_PATH",
    "FROZEN_OUT_ROOT", "OUTPUT_FILES", "ATTEMPT_CONSUMPTION_POINT",
    "COMPLETE_LABEL", "RAW_PRIOR_NPZ_KEYS", "ALT_L2_NPZ_KEYS",
    "FROZEN_ARM_NAMES", "OPERATIONAL_ARM_NAMES", "ORACLE_ARM_NAMES",
    "PLANNED_SC_CALLS", "PLANNED_TAG_INVOCATIONS", "PLANNED_RECORDS",
    "INTEGRITY_GATE_ORDER", "IR_FIELDS", "IR1_BINS", "IR3_LO_MULT",
    "IR3_HI_MULT", "IR4_TOPK", "IR5_CAP", "FROZEN_COMMAND",
    "FROZEN_SESSION_PRIOR_DIGEST", "FROZEN_H1", "FROZEN_H2", "FROZEN_H_TOTAL",
    "FROZEN_BUDGET_LITERAL", "FROZEN_K_TOTAL", "FROZEN_K1", "FROZEN_K2",
    "FROZEN_ORDER_DIGEST", "FROZEN_ALT_DIGEST", "FROZEN_ALT_H1_INC",
    "FROZEN_ALT_H2_ALT", "FROZEN_ALT_H_TOTAL_ALT", "FROZEN_CE_ALT",
    "FROZEN_CE_INCUMBENT", "FROZEN_ALT_IDEAL_LENGTH_BITS",
    "FROZEN_D2_MARGIN_BITS", "FROZEN_D2_FEASIBLE", "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S", "EXTERNAL_TIMEOUT_S", "ULIMIT_VIRTUAL_KIB",
    "L2AltHoldIr2mContractError", "L2AltHoldIr2mResourceError",
    "L2AltHoldIr2mRun", "pins_frozen", "pins_are_frozen",
    "verify_reuse", "verify_dev_source_identity_2m", "verify_hold_containment",
    "verify_consumed_exclusions_hold", "form_hold_blocks",
    "l2_alt_hold_ir_2m_seed_bits", "_ir_hazard_diagnostics",
    "ir_payload_complete", "ir_payload_tables",
    "l2_alt_hold_ir_2m_label", "run_l2_alt_hold_ir_2m", "build_parser", "main",
    "VERIFY_REUSE_FLAGS", "SHARED_FLAGS", "STAGE_B_ONLY_FLAGS", "STAGE_B_FLAGS",
]
