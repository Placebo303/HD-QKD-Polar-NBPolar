"""NB-Polar Phase 4-P20N fixed-disclosure ALT-L2 construction on 1.5M HOLD.

Thin importer of the accepted ``raw_prior_val_1p5m`` runner (read-only; that
module and every accepted module are never edited here). Exact delta list,
nothing else:

- (d1) alt-L2-table source -> the Stage-A ``alt_l2_tables_1p5m.npz``
  artifact (unit-pseudocount conditional under the frozen alpha=1 rule with
  the 1e-15 floor step retained) behind the new ``alt_l2_identity`` gate
  (file-bytes digest + alpha-1.0 pin + floor pin + exact key set +
  incumbent-p1 equality within 1e-12 + descriptive alt-H literals);
- (d2) K pins -> the CARRIED P20M integers (K1 331, K2 6689, K_total 7020
  literal display, never recomputed from the alt-H literals);
- (d3) orders -> the frozen P20M ``raw_prior_orders_1p5m.json`` reused
  read-only via the same order-file mechanism (the L1/L2 disclosed sets are
  the first-331 / first-6689 prefixes on ALL four arms; zero sampling);
- (d4) arms A/B/C/D (A = incumbent-L2 operational control = P20M G1
  construction; B = alt-L2 operational candidate; C = incumbent-L2 oracle =
  P20M G2 construction; D = alt-L2 oracle);
- (d5) new P20N tag domain (master 2026092300, prefix
  ``nbpolar-p20n-l2-alt-hold-1p5m-seed``);
- (d6) mandatory X09-R1 hazard instrumentation (eight scalars) computed
  post-decode in ``_l2_hazard_diagnostics``, recording-only;
- (d7) 1.5M HOLD population (first 512 HOLD frames 2213..2724, four blocks,
  remainder 2725..2766 never used) declared inside the TRAIN-exclusion
  gate family.

No SC/transform/floor/tag-semantics change; no second construction factor;
no smoothing parameter anywhere; zero sampling in both modes.

Two explicit modes, never mixed: (i) Stage-A derivation mode (``--derive``;
single read-only worktree input, zero protected opens) and (ii) Stage-B
frozen command mode (all Stage-B flags required, no production default).
Mixed or ambiguous invocation refuses before anything is read or written.

Stage-A pins (``FROZEN_ALT_DIGEST`` / ``FROZEN_ALT_CE_INSAMPLE`` /
``FROZEN_INCUMBENT_CE_INSAMPLE`` / ``FROZEN_ALT_IDEAL_LENGTH_BITS`` /
``FROZEN_D2_FEASIBLE``) are ``None`` until the Stage-A derivation fills
them; the Stage-B path refuses with ``Stage-A freeze not yet applied``
while any pin is ``None``, and refuses to proceed when the D2
``alt_construction_budget_feasibility`` outcome is not FEASIBLE.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ..shared import toeplitz_tag
from ..v35_algorithm_development import SOURCE_IDS
from ...io.pairs_loader import load_pairs_table, normalize_pair_columns
from . import l1_order_1p5m as p20l
from . import operational_f13 as opf
from . import per_session_calibration as psc
from . import raw_prior_val_1p5m as p20m
from .algebra import make_gf32
from .prior import derive_p1, derive_p2
from .target_construction import entropy_bits

# Reused accepted contracts (read-only; never reimplemented here).
run_operational_block = p20l.run_operational_block
run_oracle_control_block = p20l.run_oracle_control_block
OracleControlResult = p20l.OracleControlResult
verify_predecessor_construction = p20l.verify_predecessor_construction
verify_dev_source_identity = p20l.verify_dev_source_identity
verify_dev_manifest = p20l.verify_dev_manifest
verify_corrected_prior = p20m.verify_corrected_prior
verify_stage_b_order_file_p20m = p20m.verify_stage_b_order_file_p20m
budget_literal_display = p20m.budget_literal_display
raw_prior_val_1p5m_block_events = p20m.raw_prior_val_1p5m_block_events
raw_prior_val_1p5m_recount_events = p20m.raw_prior_val_1p5m_recount_events
# Carried-over P20M callsite-pattern helpers (record/floor diagnostics).
_stat_record = p20m._stat_record
_block_view = p20m._block_view
_dev_block_scoring = p20m._dev_block_scoring
_scoring_absent = p20m._scoring_absent
_selected_diagnostics = p20m._selected_diagnostics

PROTOCOL_NAME = "nbpolar-p20n-l2-alt-hold-1p5m"
MODE = "hold-l2-alt-1p5m"

Q = p20l.Q
ALPHA = p20l.ALPHA
N_BOB = p20l.N_BOB
FROZEN_N = 32768
FROZEN_SOURCE = "1p5M"
FROZEN_SOURCE_TAG = "type2_1p5M_20260121_183806"
FROZEN_FLOOR = 1e-15
FROZEN_ALPHA = 1.0
NORM_TOL = 1e-12

# (d2) Carried P20M disclosure point: literals replayed, never recomputed;
# the alt-H literals are descriptive only and never a budget input.
FROZEN_K1 = 331
FROZEN_K2 = 6689
FROZEN_K_TOTAL = 7020
FROZEN_H1_INC = 0.02519949692375297
FROZEN_H2_INC = 0.8003665547495433
FROZEN_H_TOTAL_INC = 0.8255660516732963
FROZEN_BUDGET_LITERAL = (
    "1.3*32768*0.8255660516732963-64 over 5, floored, clipped [0,65536] = 7020"
)
FROZEN_INCUMBENT_PATH = p20m.FROZEN_PRIOR_PATH
FROZEN_INCUMBENT_DIGEST = p20m.FROZEN_PRIOR_DIGEST
FROZEN_ORDER_FILE_PATH = p20m.FROZEN_ORDER_FILE_PATH
FROZEN_ORDER_DIGEST = p20m.FROZEN_ORDER_DIGEST
FROZEN_CONSTRUCTION_PATH = p20l.FROZEN_CONSTRUCTION_PATH
FROZEN_CONSTRUCTION_DIGEST = p20l.FROZEN_CONSTRUCTION_DIGEST
FROZEN_DEV_PAIRS_PATH = p20l.FROZEN_DEV_PAIRS_PATH
FROZEN_DEV_PAIRS_SIZE = p20l.FROZEN_DEV_PAIRS_SIZE
FROZEN_DEV_PAIRS_SHA256 = p20l.FROZEN_DEV_PAIRS_SHA256
FROZEN_MANIFEST_PATH = p20l.FROZEN_MANIFEST_PATH
FROZEN_MANIFEST_SCHEMA = p20l.FROZEN_MANIFEST_SCHEMA
FROZEN_PUBLIC_CONTROL_BITS = p20m.FROZEN_PUBLIC_CONTROL_BITS  # 327743
FROZEN_RAW_INPUT_BITS = 10 * FROZEN_N  # 327680 per block
FROZEN_MANIFEST_TRAIN_PAIRS = p20m.FROZEN_MANIFEST_TRAIN_PAIRS  # 424960

# (d1) Stage-A alt-L2-table artifact (file-bytes digest pinned at Stage A).
FROZEN_ALT_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/"
    "alt_l2_tables_1p5m.npz"
)
ALT_L2_NPZ_KEYS = (
    "counts_ab",
    "f_alt",
    "p1",
    "p2_alt",
    "alpha",
    "floor_value",
    "h1_inc",
    "h2_alt",
    "h_total_alt",
)

# (d7) HOLD population: FIRST 512 HOLD frames of the 1.5M session in
# (frame_id, pair_idx) order -> 4 blocks at N=32768; remainder never used.
FROZEN_DEV_FRAME_RANGE = (2213, 2724)
FROZEN_DEV_FRAMES = 512
FROZEN_DEV_PAIRS = 131072
FROZEN_BLOCK_COUNT = 4
FROZEN_BLOCK_FRAMES = 128
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_BLOCK_RANGES = ((2213, 2340), (2341, 2468), (2469, 2596), (2597, 2724))
FROZEN_REMAINDER_FRAME_RANGE = (2725, 2766)
FROZEN_REMAINDER_FRAMES = 42
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME  # 10752
INTRA_FILE_VAL_FRAME_RANGE = (1660, 2212)
INTRA_FILE_HOLD_FRAME_RANGE = (2213, 2766)
CONSUMED_TRAIN_FRAME_RANGE = (0, 1659)
CONSUMED_VAL_DEV_FRAME_RANGE = (1660, 2043)
VAL_REMAINDER_FRAME_RANGE = (2044, 2212)
FROZEN_BUILD_FRAME_RANGE = (0, 1659)
FROZEN_MANIFEST_TRAIN_FRAMES = p20m.FROZEN_MANIFEST_TRAIN_FRAMES
FROZEN_MANIFEST_VAL_FRAMES = p20m.FROZEN_MANIFEST_VAL_FRAMES
FROZEN_MANIFEST_HOLD_FRAMES = p20m.FROZEN_MANIFEST_HOLD_FRAMES
FROZEN_MANIFEST_VAL_PAIRS = p20m.FROZEN_MANIFEST_VAL_PAIRS
FROZEN_MANIFEST_HOLD_PAIRS = p20m.FROZEN_MANIFEST_HOLD_PAIRS

# (d5) new P20N tag domain.
FROZEN_TAG_MASTER = 2026092300
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = p20m.FROZEN_TAG_BITS  # 64
SEED_PREFIX = "nbpolar-p20n-l2-alt-hold-1p5m-seed"

# D1/D2 feasibility literals (descriptive construction-validity quantities).
FROZEN_ALT_CEILING_BITS = 5 * FROZEN_K2 + 64  # 33509 (L2-only gate ceiling)
FROZEN_OPERATIONAL_CEILING_BITS = 5 * FROZEN_K_TOTAL + 64  # 35164
FROZEN_HAZARD_R = 8

# Stage-B output root (must be ABSENT until an authorized Stage-B execution).
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20N-L2-ALT-CONSTRUCTION-HOLD-1P5M/"
    "l2_alt_hold_1p5m"
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "input_and_predecessor_identity.json",
    "per_block_arm_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)
ATTEMPT_CONSUMPTION_POINT = "first protected content open (HOLD pairs parquet)"
COMPLETE_LABEL = "TARGET_EMPIRICAL_N32768_HOLD_L2_ALT_CONSTRUCTION_1P5M_COMPLETE"

# ---- Stage-A pins (filled by the Stage-A derivation, 2026-09-19) ----
FROZEN_ALT_DIGEST = "6f4a4f7689d87e2c0a6c73617fdc9d79751a226661177a9bc6193feba2333e78"
FROZEN_ALT_CE_INSAMPLE = 0.9027311772313849
FROZEN_INCUMBENT_CE_INSAMPLE = 0.8003665547439149
FROZEN_ALT_IDEAL_LENGTH_BITS = 29580.69521551802
FROZEN_D2_FEASIBLE = True
FROZEN_ALT_FLOOR_HITS = 0
FROZEN_ALT_FLOOR_HIT_RATE = 0.0
FROZEN_ALT_ZERO_COLUMNS = 0
FROZEN_ALT_F_ALT_MIN = 0.000665335994677302
FROZEN_ALT_F_ALT_MAX = 0.24762550881953543

OPERATIONAL_PROVENANCE = p20l.OPERATIONAL_PROVENANCE
ORACLE_PROVENANCE = p20l.ORACLE_PROVENANCE


@dataclass(frozen=True)
class ArmSpec:
    """One frozen P20N arm (never CLI-tunable, never extensible)."""

    name: str
    kind: str  # "operational" | "oracle_control"
    k1: int
    k2: int
    leakage_bits: int
    provenance: str
    prior_source: str  # "incumbent" | "alt"


FROZEN_ARM_NAMES = (
    "A_incumbent_L2_operational",
    "B_alt_L2_operational",
    "C_incumbent_L2_oracle",
    "D_alt_L2_oracle",
)
OPERATIONAL_ARM_NAMES = ("A_incumbent_L2_operational", "B_alt_L2_operational")
ORACLE_ARM_NAMES = ("C_incumbent_L2_oracle", "D_alt_L2_oracle")

PLANNED_SC_CALLS = FROZEN_BLOCK_COUNT * (2 + 2 + 1 + 1)  # 24
PLANNED_TAG_INVOCATIONS = len(FROZEN_ARM_NAMES) * FROZEN_BLOCK_COUNT  # 16
PLANNED_RECORDS = FROZEN_BLOCK_COUNT * len(FROZEN_ARM_NAMES)  # 16
FROZEN_TOTAL_KEY_DEPENDENT_BITS = (
    8 * (5 * FROZEN_K_TOTAL + 64) + 8 * (5 * FROZEN_K2 + 64)
)  # 549384
FROZEN_TOTAL_PUBLIC_CONTROL_BITS = (
    PLANNED_TAG_INVOCATIONS * FROZEN_PUBLIC_CONTROL_BITS
)  # 5243888

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "incumbent_prior_identity",
    "alt_l2_identity",
    "alt_construction_budget_feasibility",
    "dev_split_manifest_identity",
    "dev_block_range_identity",
    "order_derivation_identity",
    "k_literal_exact",
    "target_population_contract",
    "dev_population_exact",
    "blocks_exact_with_declared_remainder",
    "sixteen_records_exact",
    "genie_calls_exact",
    "sc_calls_exact",
    "tags_exact",
    "orders_valid_k_prefixes_within_registered_arms",
    "hazard_instrumentation_complete",
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

HAZARD_FIELDS = (
    "l2_order_digest",
    "l2_prefix_len",
    "l2_fail_in_prefix",
    "l2_fail_hazard_bits",
    "l2_fail_nbhd_mean_bits",
    "l2_prefix_hazard_mean_bits",
    "l2_fail_nbhd_floor_frac",
    "l2_prefix_floor_frac",
)

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
    "ulimit -v 2097152\n"
    "timeout 900 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_hold_1p5m "
    f"--prior {FROZEN_INCUMBENT_PATH} --prior-digest {FROZEN_INCUMBENT_DIGEST} "
    f"--alt-prior {FROZEN_ALT_PATH} --alt-digest {FROZEN_ALT_DIGEST} "
    "--source 1p5M --floor 1e-15 --n 32768 --k1 331 --k2 6689 "
    f"--construction {FROZEN_CONSTRUCTION_PATH} "
    f"--construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
    f"--dev-pairs {FROZEN_DEV_PAIRS_PATH} "
    "--dev-frames 2213 2724 --block-frames 128 --remainder-frames 2725 2766 "
    "--tag-master 2026092300 --chunk-rows 512 --tag-bits 64 "
    f"--order-file {FROZEN_ORDER_FILE_PATH} --order-digest {FROZEN_ORDER_DIGEST} "
    f"--out-dir {FROZEN_OUT_ROOT}"
)

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 900.0
EXTERNAL_TIMEOUT_S = 900
ULIMIT_VIRTUAL_KIB = 2097152

# Process-level one-open guards: set at the first content load/open, never cleared.
_INCUMBENT_CONTENT_OPENED = False
_INCUMBENT_CONTENT_OPENS = 0
_ALT_CONTENT_OPENED = False
_ALT_CONTENT_OPENS = 0
_DEV_PARQUET_CONTENT_OPENED = False
_INCUMBENT_CONTENT_LOADED = False
_ALT_CONTENT_LOADED = False


class L2AltHold1p5mContractError(ValueError):
    """Pre-open population/formation failure: BLOCKED(<earliest gate>)."""


class L2AltHold1p5mResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


def _gate_call(gate_name, fn, *args, **kwargs):
    """Run an accepted gate helper read-only, tagged with the P20N gate name."""
    try:
        return fn(*args, **kwargs)
    except (ValueError, FileNotFoundError) as exc:
        raise L2AltHold1p5mContractError(f"BLOCKED({gate_name}): {exc}") from exc


def frozen_arm_table() -> tuple:
    """Materialize the four hardcoded arms (never CLI-tunable)."""
    return (
        ArmSpec("A_incumbent_L2_operational", "operational", FROZEN_K1, FROZEN_K2,
                FROZEN_OPERATIONAL_CEILING_BITS, OPERATIONAL_PROVENANCE, "incumbent"),
        ArmSpec("B_alt_L2_operational", "operational", FROZEN_K1, FROZEN_K2,
                FROZEN_OPERATIONAL_CEILING_BITS, OPERATIONAL_PROVENANCE, "alt"),
        ArmSpec("C_incumbent_L2_oracle", "oracle_control", 0, FROZEN_K2,
                FROZEN_ALT_CEILING_BITS, ORACLE_PROVENANCE, "incumbent"),
        ArmSpec("D_alt_L2_oracle", "oracle_control", 0, FROZEN_K2,
                FROZEN_ALT_CEILING_BITS, ORACLE_PROVENANCE, "alt"),
    )


def check_frozen_arm_table() -> dict:
    """Fail-closed pin of the four frozen arms and their design accounting.

    Pure code-level check (no I/O): arm names/order, the carried K literals,
    the 5K+64 leakage arithmetic, the construction swap (A/C incumbent,
    B/D alt), the shared-prefix rule and the 24 SC / 16 tag / 16 record
    design totals. Any drift raises before any root exists.
    """
    arms = frozen_arm_table()
    if tuple(spec.name for spec in arms) != FROZEN_ARM_NAMES:
        raise ValueError(f"frozen arm order drifted: {tuple(s.name for s in arms)!r}")
    a, b, c, d = arms
    if (a.kind, a.k1, a.k2, a.leakage_bits, a.prior_source, a.provenance) != (
            "operational", 331, 6689, 35164, "incumbent", OPERATIONAL_PROVENANCE):
        raise ValueError("frozen A_incumbent_L2_operational arm drifted")
    if (b.kind, b.k1, b.k2, b.leakage_bits, b.prior_source, b.provenance) != (
            "operational", 331, 6689, 35164, "alt", OPERATIONAL_PROVENANCE):
        raise ValueError("frozen B_alt_L2_operational arm drifted")
    if (c.kind, c.k1, c.k2, c.leakage_bits, c.prior_source, c.provenance) != (
            "oracle_control", 0, 6689, 33509, "incumbent", ORACLE_PROVENANCE):
        raise ValueError("frozen C_incumbent_L2_oracle arm drifted")
    if (d.kind, d.k1, d.k2, d.leakage_bits, d.prior_source, d.provenance) != (
            "oracle_control", 0, 6689, 33509, "alt", ORACLE_PROVENANCE):
        raise ValueError("frozen D_alt_L2_oracle arm drifted")
    if int(a.k1) + int(a.k2) != FROZEN_K_TOTAL:
        raise ValueError("frozen A K1+K2 != carried K_total 7020")
    if int(a.leakage_bits) != 5 * FROZEN_K_TOTAL + 64:
        raise ValueError("frozen A/B leakage != 5*7020+64")
    if int(c.leakage_bits) != 5 * FROZEN_K2 + 64:
        raise ValueError("frozen C/D leakage != 5*6689+64")
    if int(b.leakage_bits) - int(a.leakage_bits) != 0:
        raise ValueError("frozen B-vs-A key-bit delta must be exactly 0")
    if int(d.leakage_bits) - int(c.leakage_bits) != 0:
        raise ValueError("frozen D-vs-C key-bit delta must be exactly 0")
    if PLANNED_SC_CALLS != 24:
        raise ValueError(f"frozen design must plan 24 SC calls, got {PLANNED_SC_CALLS}")
    if PLANNED_TAG_INVOCATIONS != 16:
        raise ValueError(f"frozen design must plan 16 tags, got {PLANNED_TAG_INVOCATIONS}")
    if PLANNED_RECORDS != 16:
        raise ValueError(f"frozen design must plan 16 records, got {PLANNED_RECORDS}")
    if FROZEN_TOTAL_KEY_DEPENDENT_BITS != 549384:
        raise ValueError("frozen planned key-dependent total != 549384")
    if FROZEN_TOTAL_PUBLIC_CONTROL_BITS != 5243888:
        raise ValueError("frozen planned public total != 5243888")
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
        "planned_key_dependent_bits": FROZEN_TOTAL_KEY_DEPENDENT_BITS,
        "planned_public_control_bits": FROZEN_TOTAL_PUBLIC_CONTROL_BITS,
        "shared_l1_prefix": int(FROZEN_K1),
        "shared_l2_prefix": int(FROZEN_K2),
        "cap_vs_raw_ratio": cap_ratio,
    }


def alt_pins_frozen() -> dict:
    """Fail-closed Stage-A pin-state check for the Stage-B path."""
    pins = {
        "alt_digest": FROZEN_ALT_DIGEST,
        "ce_alt_insample_bits_per_symbol": FROZEN_ALT_CE_INSAMPLE,
        "ce_incumbent_insample_bits_per_symbol": FROZEN_INCUMBENT_CE_INSAMPLE,
        "alt_ideal_length_bits": FROZEN_ALT_IDEAL_LENGTH_BITS,
        "d2_feasible": FROZEN_D2_FEASIBLE,
        "alt_floor_hits": FROZEN_ALT_FLOOR_HITS,
        "alt_floor_hit_rate": FROZEN_ALT_FLOOR_HIT_RATE,
        "alt_zero_columns": FROZEN_ALT_ZERO_COLUMNS,
        "alt_f_alt_min": FROZEN_ALT_F_ALT_MIN,
        "alt_f_alt_max": FROZEN_ALT_F_ALT_MAX,
    }
    missing = sorted(name for name, value in pins.items() if value is None)
    if missing:
        raise ValueError(
            "Stage-A freeze not yet applied: missing pins: " + ",".join(missing)
        )
    return pins


# ---------------------------------------------------------------------------
# Frozen CLI flag checks (both modes; all flags required, no default).
# ---------------------------------------------------------------------------

def _check_alpha(value) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"frozen derivation requires alpha=1, got {value!r}") from exc
    if out != FROZEN_ALPHA:
        raise ValueError(f"frozen derivation requires alpha={FROZEN_ALPHA}, got {out}")
    return out


def _check_floor(value) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"frozen point requires floor={FROZEN_FLOOR}, got {value!r}") from exc
    if out != FROZEN_FLOOR:
        raise ValueError(f"frozen point requires floor={FROZEN_FLOOR}, got {out}")
    return out


def _check_source(value) -> str:
    if value != FROZEN_SOURCE:
        raise ValueError(f"frozen point requires source={FROZEN_SOURCE!r}, got {value!r}")
    if SOURCE_IDS.get(FROZEN_SOURCE) != FROZEN_SOURCE_TAG:
        raise ValueError("frozen source-tag vocabulary drifted")
    return FROZEN_SOURCE


def _check_n(value) -> int:
    out = opf._check_n(value)
    if out != FROZEN_N:
        raise ValueError(f"frozen point requires n={FROZEN_N}, got {out}")
    return out


def _check_k1(value) -> int:
    out = opf._as_int(value, "k1", minimum=0)
    if out != FROZEN_K1:
        raise ValueError(f"frozen point requires k1={FROZEN_K1}, got {out}")
    return out


def _check_k2(value) -> int:
    out = opf._as_int(value, "k2", minimum=0)
    if out != FROZEN_K2:
        raise ValueError(f"frozen point requires k2={FROZEN_K2}, got {out}")
    return out


def check_k_literals(*, k1, k2) -> dict:
    """K-literal gate: 331/6689/7020 replayed, never recomputed.

    The display literal is the carried P20M session-budget line recomputed
    from the carried incumbent session H (never from the alt-H literals);
    any other triple refuses before any SC call.
    """
    k1 = _check_k1(k1)
    k2 = _check_k2(k2)
    k_total = int(k1) + int(k2)
    if k_total != FROZEN_K_TOTAL:
        raise ValueError(
            f"BLOCKED(k_literal_exact): K1+K2={k_total} != frozen {FROZEN_K_TOTAL}"
        )
    if budget_literal_display(FROZEN_H_TOTAL_INC) != FROZEN_BUDGET_LITERAL:
        raise ValueError(
            "BLOCKED(k_literal_exact): carried budget-literal display drifted"
        )
    return {
        "k1": int(k1),
        "k2": int(k2),
        "k_total": k_total,
        "budget_literal": FROZEN_BUDGET_LITERAL,
        "recomputed_from": "carried P20M incumbent session H (never the alt-H literals)",
    }


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
    if digest != str(FROZEN_INCUMBENT_DIGEST):
        raise ValueError(
            "frozen point requires prior-digest=<P20M worktree-npz canonical digest>"
        )
    return digest


def _check_order_digest(value) -> str:
    digest = str(value)
    if digest != str(FROZEN_ORDER_DIGEST):
        raise ValueError("frozen point requires order-digest=<P20M order-file sha256>")
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


# ---------------------------------------------------------------------------
# (d1) Stage-A derivation: unit-pseudocount conditional + floor + derive_p2.
# Single read-only worktree input, zero protected opens, zero sampling.
# ---------------------------------------------------------------------------

def alt_prefloor_table(counts_ab) -> np.ndarray:
    """Unit-pseudocount conditional ``[Alice,Bob]`` before the floor.

    ``f_pre[a,b] = (counts_ab[a,b] + 1) / (n_b[b] + 1024)`` with the frozen
    literals 1 (pseudocount) and 1024 (Alice-alphabet size); zero columns
    fall back to ``p_global`` exactly. Pure; no smoothing parameter exists.
    """
    mat = np.asarray(counts_ab, dtype=np.float64)
    if mat.ndim != 2 or mat.shape[0] < 1 or mat.shape[1] < 1:
        raise ValueError(f"counts_ab must be 2-D non-empty, got {mat.shape}")
    if not np.isfinite(mat).all():
        raise ValueError("counts_ab must be finite")
    if (mat < 0).any():
        raise ValueError("counts_ab must be non-negative")
    total = float(mat.sum())
    if total <= 0:
        raise ValueError("counts_ab total must be positive")
    n_b = mat.sum(axis=0)
    p_global = mat.sum(axis=1) / total
    out = (mat + 1.0) / (n_b + float(N_BOB))[None, :]
    zero_cols = n_b == 0
    if zero_cols.any():
        out[:, zero_cols] = p_global[:, None]
    return np.ascontiguousarray(out)


def derive_alt_l2_arrays(counts_ab, *, incumbent_p1, incumbent_p_b,
                         incumbent_h1, floor: float = FROZEN_FLOOR) -> dict:
    """Apply the frozen alt rule to a ``[Alice,Bob]`` count matrix.

    Pure function (no I/O): unit-pseudocount conditional (alpha=1 literal,
    never a tunable weight) + ``1e-15`` floor step RETAINED formally +
    column renormalization; ``p2_alt`` via accepted ``derive_p2`` under
    ``A = 32*U1 + U2`` FULL_BOB_ONLY. The L1 path is byte-identical: the
    stored ``p1`` is the CARRIED incumbent ``p1`` (never re-derived), with
    the elementwise equality difference reported; ``h2_alt`` /
    ``h_total_alt`` are recomputed descriptively via the accepted
    ``entropy_bits`` functional on ``(p1_inc, p2_alt)`` and are NEVER a
    budget input.
    """
    pre = alt_prefloor_table(counts_ab)
    mat = np.asarray(counts_ab, dtype=np.float64)
    n_b = mat.sum(axis=0)
    floor = float(floor)
    floor_hits = int(np.sum(pre < floor))
    f_alt = np.maximum(pre, floor)
    f_alt = np.ascontiguousarray(f_alt / f_alt.sum(axis=0, keepdims=True))
    zero_columns = int(np.sum(n_b == 0))
    p2_alt = np.ascontiguousarray(derive_p2(f_alt))
    p1_inc = np.ascontiguousarray(np.asarray(incumbent_p1, dtype=np.float64))
    if p1_inc.shape != (Q, N_BOB):
        raise ValueError(f"incumbent p1 must be (32,1024), got {p1_inc.shape}")
    p_b = np.ascontiguousarray(np.asarray(incumbent_p_b, dtype=np.float64))
    if p_b.shape != (N_BOB,):
        raise ValueError(f"incumbent p_b must be (1024,), got {p_b.shape}")
    h1_inc = float(incumbent_h1)
    h2_alt = float(np.sum(p_b[None, :] * p1_inc * entropy_bits(p2_alt, axis=2)))
    p1_alt_derived = np.ascontiguousarray(derive_p1(f_alt))
    return {
        "f_alt": f_alt,
        "p2_alt": p2_alt,
        "p1": np.ascontiguousarray(p1_inc.copy()),
        "floor_hits": floor_hits,
        "floor_hit_rate": float(floor_hits) / float(pre.size),
        "floor_cells": int(pre.size),
        "zero_columns": zero_columns,
        "column_dev": float(np.abs(f_alt.sum(axis=0) - 1.0).max()),
        "f_alt_min": float(f_alt.min()),
        "f_alt_max": float(f_alt.max()),
        "p1_equality_max_abs_diff": float(np.abs(p1_inc - p1_inc).max()),
        "p1_alt_derived_max_abs_diff": float(np.abs(p1_alt_derived - p1_inc).max()),
        "h1_inc": h1_inc,
        "h2_alt": h2_alt,
        "h_total_alt": h1_inc + h2_alt,
    }


def in_sample_l2_ce_bits_per_symbol(counts_ab, p2_table) -> float:
    """D1 estimator: in-sample TRAIN L2 code length in bits per Alice symbol.

    ``(1/total) * sum_{a,b} counts_ab[a,b] * (-log2 p2[u1(a), b, u2(a)])``
    with ``u1(a) = (a>>5)&31`` and ``u2(a) = a&31``. The SAME TRAIN counts
    the tables were built from; a construction-validity quantity, never a
    decoding input and never a threshold on results.
    """
    counts = np.asarray(counts_ab, dtype=np.float64)
    if counts.shape != (N_BOB, N_BOB):
        raise ValueError(f"counts_ab must be (1024,1024), got {counts.shape}")
    if not np.isfinite(counts).all() or (counts < 0).any():
        raise ValueError("counts_ab must be finite and non-negative")
    total = float(counts.sum())
    if total <= 0:
        raise ValueError("counts_ab total must be positive")
    p2 = np.asarray(p2_table, dtype=np.float64)
    if p2.shape != (Q, N_BOB, Q):
        raise ValueError(f"p2 must be (32,1024,32), got {p2.shape}")
    sym = np.arange(N_BOB, dtype=np.int64)
    u1 = (sym >> 5) & 31
    u2 = sym & 31
    with np.errstate(divide="ignore"):
        masses = p2[u1[:, None], sym[None, :], u2[:, None]]
        if bool(((masses <= 0) & (counts > 0)).any()):
            raise ValueError("feasibility estimator: zero table mass at a counted cell")
        terms = -np.log2(np.where(masses > 0, masses, 1.0))
    return float(np.sum(np.where(counts > 0, counts * terms, 0.0)) / total)


def feasibility_literals(counts_ab, *, p2_incumbent, p2_alt) -> dict:
    """Compute the D1 feasibility literals (TRAIN-only, zero protected reads)."""
    ce_alt = in_sample_l2_ce_bits_per_symbol(counts_ab, p2_alt)
    ce_inc = in_sample_l2_ce_bits_per_symbol(counts_ab, p2_incumbent)
    ideal = float(ce_alt * FROZEN_N)
    return {
        "estimator": (
            "ce_insample_bits_per_symbol = (1/total) * sum_{a,b} "
            "counts_ab[a,b] * (-log2 p2[u1(a), b, u2(a)]) with "
            "u1(a)=(a>>5)&31, u2(a)=a&31; TRAIN counts only"
        ),
        "counts_total": int(round(float(np.asarray(counts_ab, dtype=np.float64).sum()))),
        "ce_alt_insample_bits_per_symbol": ce_alt,
        "ce_incumbent_insample_bits_per_symbol": ce_inc,
        "alt_feasibility_ceiling_bits": int(FROZEN_ALT_CEILING_BITS),
        "operational_ceiling_bits": int(FROZEN_OPERATIONAL_CEILING_BITS),
        "alt_ideal_length_bits": ideal,
        "feasible": bool(ideal <= float(FROZEN_ALT_CEILING_BITS)),
    }


def load_incumbent_prior_arrays(path, *, expected_digest: str) -> dict:
    """Load the P20M worktree npz read-only behind its canonical digest pin.

    Exact ``RAW_PRIOR_NPZ_KEYS`` key set + ``(1024,1024)`` counts + the
    canonical digest against the carried P20M pin. The single content open
    is recorded on the process-level no-reopen guard (worktree-file read,
    never a protected counts open).
    """
    global _INCUMBENT_CONTENT_OPENED, _INCUMBENT_CONTENT_OPENS
    if _INCUMBENT_CONTENT_OPENED:
        raise L2AltHold1p5mContractError(
            "reopen refused: the single worktree-npz read was already consumed"
        )
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"P20M worktree prior npz not found: {p}")
    try:
        data = np.load(str(p), allow_pickle=False)
        with data:
            keys = set(str(k) for k in data.files)
            if keys != set(p20m.RAW_PRIOR_NPZ_KEYS):
                raise L2AltHold1p5mContractError(
                    f"worktree prior keys must be exactly "
                    f"{sorted(p20m.RAW_PRIOR_NPZ_KEYS)}, got {sorted(keys)}"
                )
            arrays = {k: np.asarray(data[k]) for k in p20m.RAW_PRIOR_NPZ_KEYS}
    except ValueError as exc:
        if "worktree prior keys" in str(exc):
            raise
        raise L2AltHold1p5mContractError(f"worktree prior load failed ({exc})") from exc
    digest = psc.canonical_prior_digest(arrays)
    if digest != str(expected_digest):
        raise L2AltHold1p5mContractError(
            "worktree prior digest != frozen pin (refusing before any derivation)"
        )
    counts = np.asarray(arrays["counts_ab"], dtype=np.float64)
    if counts.shape != (N_BOB, N_BOB):
        raise L2AltHold1p5mContractError(
            f"worktree counts_ab must be (1024,1024), got {counts.shape}"
        )
    _INCUMBENT_CONTENT_OPENED = True
    _INCUMBENT_CONTENT_OPENS += 1
    return {"arrays": arrays, "digest": digest, "counts_ab": counts}


def run_derive_stage_a(*, prior_path=FROZEN_INCUMBENT_PATH, prior_digest=None,
                       alpha=None, floor=None, out_path=FROZEN_ALT_PATH,
                       expected_counts_total: int = FROZEN_MANIFEST_TRAIN_PAIRS) -> dict:
    """Execute the frozen Stage-A derivation once; write the alt-table file.

    The single read-only worktree-npz read (digest-reverified first) feeds
    the frozen alpha=1 rule; the product fails if present. ZERO protected
    opens: no V25 counts NPZ, no HOLD/VAL/DEV parquet, no 1M/2M contact,
    zero decoder execution, zero sampling, zero genie calls. D1 literals
    are computed from the SAME TRAIN counts and the D2
    ``alt_construction_budget_feasibility`` outcome is decided here,
    BEFORE any HOLD contact.
    """
    out = Path(out_path)
    if out.exists():
        raise FileExistsError(f"refusing to overwrite existing alt-L2 table: {out}")
    if prior_digest is None:
        raise ValueError("derive mode requires --prior-digest (frozen P20M pin)")
    digest_pin = _check_prior_digest(prior_digest)
    alpha_value = _check_alpha(alpha)
    floor_value = _check_floor(floor)
    if alpha_value != FROZEN_ALPHA or floor_value != FROZEN_FLOOR:
        raise ValueError("derive mode requires the frozen alpha=1 / floor=1e-15 pins")
    start = time.perf_counter()
    incumbent = load_incumbent_prior_arrays(prior_path, expected_digest=digest_pin)
    counts = np.ascontiguousarray(incumbent["counts_ab"])
    counts_total = int(round(float(counts.sum())))
    if counts_total != int(expected_counts_total):
        raise ValueError(
            f"counts total {counts_total} != manifest TRAIN pairs "
            f"{int(expected_counts_total)}"
        )
    cal = derive_alt_l2_arrays(
        counts, incumbent_p1=incumbent["arrays"]["p1"],
        incumbent_p_b=incumbent["arrays"]["p_b"],
        incumbent_h1=float(incumbent["arrays"]["h1"]),
    )
    arrays = {
        "counts_ab": counts,
        "f_alt": cal["f_alt"],
        "p1": cal["p1"],
        "p2_alt": cal["p2_alt"],
        "alpha": np.asarray(FROZEN_ALPHA, dtype=np.float64),
        "floor_value": np.asarray(floor_value, dtype=np.float64),
        "h1_inc": np.asarray(float(cal["h1_inc"]), dtype=np.float64),
        "h2_alt": np.asarray(float(cal["h2_alt"]), dtype=np.float64),
        "h_total_alt": np.asarray(float(cal["h_total_alt"]), dtype=np.float64),
    }
    # Serialize once in memory, pin the exact bytes, then write the file once.
    buffer = io.BytesIO()
    np.savez(buffer, **arrays)
    payload = buffer.getvalue()
    file_digest = hashlib.sha256(payload).hexdigest()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(payload)
    d1 = feasibility_literals(
        counts, p2_incumbent=np.asarray(incumbent["arrays"]["p2"], dtype=np.float64),
        p2_alt=cal["p2_alt"])
    feasible = bool(d1["feasible"])
    return {
        "mode": "stage-a-derive",
        "protocol": PROTOCOL_NAME,
        "alt_path": str(out),
        "alt_digest": file_digest,
        "alt_npz_keys": list(ALT_L2_NPZ_KEYS),
        "alpha": FROZEN_ALPHA,
        "floor_value": floor_value,
        "counts_total": counts_total,
        "floor_hits": int(cal["floor_hits"]),
        "floor_hit_rate": float(cal["floor_hit_rate"]),
        "floor_cells": int(cal["floor_cells"]),
        "zero_columns": int(cal["zero_columns"]),
        "column_dev": float(cal["column_dev"]),
        "f_alt_min": float(cal["f_alt_min"]),
        "f_alt_max": float(cal["f_alt_max"]),
        "p1_equality_max_abs_diff": float(cal["p1_equality_max_abs_diff"]),
        "p1_alt_derived_max_abs_diff": float(cal["p1_alt_derived_max_abs_diff"]),
        "h1_inc": float(cal["h1_inc"]),
        "h2_alt": float(cal["h2_alt"]),
        "h_total_alt": float(cal["h_total_alt"]),
        "d1": d1,
        "alt_construction_budget_feasibility": (
            "FEASIBLE" if feasible else "ALT_CONSTRUCTION_BUDGET_INFEASIBLE"
        ),
        "incumbent_digest": str(incumbent["digest"]),
        "incumbent_path": str(prior_path),
        "worktree_npz_content_opens": int(_INCUMBENT_CONTENT_OPENS),
        "sampling_calls": 0,
        "genie_calls": 0,
        "decoder_calls": 0,
        "protected_content_opens": 0,
        "wall_s": round(float(time.perf_counter() - start), 6),
    }


def verify_alt_l2_arrays(alt_arrays, *, incumbent_arrays) -> dict:
    """Pure alt-table identity checks (shared by the disk and injected seams)."""
    if set(alt_arrays) != set(ALT_L2_NPZ_KEYS):
        raise ValueError(
            f"alt-L2 table keys must be exactly {sorted(ALT_L2_NPZ_KEYS)}, "
            f"got {sorted(alt_arrays)}"
        )
    failing = []
    alpha = float(np.asarray(alt_arrays["alpha"]))
    floor_value = float(np.asarray(alt_arrays["floor_value"]))
    if alpha != FROZEN_ALPHA:
        failing.append("alpha_pin")
    if floor_value != FROZEN_FLOOR:
        failing.append("floor_pin")
    counts = np.asarray(alt_arrays["counts_ab"], dtype=np.float64)
    f_alt = np.asarray(alt_arrays["f_alt"], dtype=np.float64)
    p1_alt = np.asarray(alt_arrays["p1"], dtype=np.float64)
    p2_alt = np.asarray(alt_arrays["p2_alt"], dtype=np.float64)
    p_b = np.asarray(incumbent_arrays["p_b"], dtype=np.float64)
    p1_inc = np.asarray(incumbent_arrays["p1"], dtype=np.float64)
    if counts.shape != (N_BOB, N_BOB):
        raise ValueError(f"alt-L2 counts_ab must be (1024,1024), got {counts.shape}")
    if f_alt.shape != (N_BOB, N_BOB):
        raise ValueError(f"alt-L2 f_alt must be (1024,1024), got {f_alt.shape}")
    if p1_alt.shape != (Q, N_BOB):
        raise ValueError(f"alt-L2 p1 must be (32,1024), got {p1_alt.shape}")
    if p2_alt.shape != (Q, N_BOB, Q):
        raise ValueError(f"alt-L2 p2_alt must be (32,1024,32), got {p2_alt.shape}")
    total = float(counts.sum())
    if int(round(total)) != int(FROZEN_MANIFEST_TRAIN_PAIRS):
        failing.append("counts_total_pin")
    p1_equality = float(np.abs(p1_alt - p1_inc).max())
    if p1_equality > NORM_TOL:
        failing.append("p1_equality")
    h1_inc = float(np.asarray(alt_arrays["h1_inc"]))
    h2_alt = float(np.asarray(alt_arrays["h2_alt"]))
    h_total_alt = float(np.asarray(alt_arrays["h_total_alt"]))
    if abs(h1_inc - FROZEN_H1_INC) > NORM_TOL:
        failing.append("h1_inc_literal")
    if abs(h_total_alt - (h1_inc + h2_alt)) > NORM_TOL:
        failing.append("h_total_consistency")
    if total > 0:
        h2_recomputed = float(
            np.sum(p_b[None, :] * p1_alt * entropy_bits(p2_alt, axis=2))
        )
        if abs(h2_recomputed - h2_alt) > NORM_TOL:
            failing.append("h2_alt_recomputation")
    else:
        h2_recomputed = None
    if float(np.abs(f_alt.sum(axis=0) - 1.0).max()) > NORM_TOL:
        failing.append("f_alt_columns_normalized")
    if float(np.abs(p2_alt.sum(axis=2) - 1.0).max()) > NORM_TOL:
        failing.append("p2_alt_last_axis_normalized")
    if failing:
        raise ValueError(
            "BLOCKED(alt_l2_identity): failing checks: " + ",".join(failing)
        )
    return {
        "alpha": alpha,
        "floor_value": floor_value,
        "counts_total": int(round(total)),
        "p1_equality_max_abs_diff": p1_equality,
        "h1_inc": h1_inc,
        "h2_alt": h2_alt,
        "h2_alt_recomputed": h2_recomputed,
        "h_total_alt": h_total_alt,
        "f_alt": np.ascontiguousarray(f_alt),
        "p1": np.ascontiguousarray(p1_alt),
        "p2_alt": np.ascontiguousarray(p2_alt),
        "counts_ab": np.ascontiguousarray(counts),
        "keys": sorted(str(k) for k in alt_arrays),
        "failing": (),
        "passed": True,
    }


def verify_alt_l2_identity(path, *, expected_digest: str, incumbent_arrays) -> dict:
    """alt_l2_identity gate: file-bytes digest + pure alt-table checks.

    Worktree-file read only (never a protected open): the file-bytes sha256
    must equal the frozen ``--alt-digest`` (which itself must equal the
    Stage-A pin) before the pure identity checks run. Any mismatch raises
    before any SC call.
    """
    digest_pin = _check_alt_digest(expected_digest)
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Stage-A alt-L2 table not found: {p}")
    raw = p.read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    if file_digest != digest_pin:
        raise ValueError(
            "alt-table bytes sha256 != frozen --alt-digest "
            "(refusing before any SC call)"
        )
    try:
        data = np.load(io.BytesIO(raw), allow_pickle=False)
        with data:
            arrays = {str(k): np.asarray(data[k]) for k in data.files}
    except ValueError as exc:
        raise ValueError(f"alt-L2 table unreadable: {exc}") from exc
    verified = verify_alt_l2_arrays(arrays, incumbent_arrays=incumbent_arrays)
    verified["file_digest"] = file_digest
    verified["expected_digest"] = digest_pin
    verified["alt_path"] = str(p)
    return verified


# ---------------------------------------------------------------------------
# (d7) HOLD population: gate family (b)-(f) + deterministic block formation.
# ---------------------------------------------------------------------------

def verify_hold_containment(dev_frames=None, remainder_frames=None) -> dict:
    """Gate family (b): intra-file HOLD-containment (VAL-exterior first).

    Pure code-level check (no I/O): the DEV range and the declared remainder
    must lie wholly inside 1.5M HOLD 2213..2766 and overlap NONE of the
    VAL-exterior pool 1660..2212. The declared DEV must be exactly the FIRST
    512 HOLD frames (frozen HOLD base 2213: 2213..2724) with the frozen
    four-block decomposition; any violation raises before any protected
    content open.
    """
    dev_pair = (tuple(FROZEN_DEV_FRAME_RANGE) if dev_frames is None
                else tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    val_first, val_last = INTRA_FILE_VAL_FRAME_RANGE
    hold_first, hold_last = INTRA_FILE_HOLD_FRAME_RANGE
    dev_first, dev_last = dev_pair
    rem_first, rem_last = rem_pair
    if not (hold_first <= dev_first and dev_last <= hold_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): DEV {dev_first}..{dev_last} "
            f"lies outside 1.5M HOLD {hold_first}..{hold_last}"
        )
    if not (hold_first <= rem_first and rem_last <= hold_last):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): remainder {rem_first}..{rem_last} "
            f"lies outside 1.5M HOLD {hold_first}..{hold_last}"
        )
    if not (dev_last < val_first or dev_first > val_last):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): DEV overlaps the 1.5M "
            f"VAL-exterior pool {val_first}..{val_last}"
        )
    if not (rem_last < val_first or rem_first > val_last):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): remainder overlaps the 1.5M "
            f"VAL-exterior pool {val_first}..{val_last}"
        )
    if dev_pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): DEV {dev_pair} != frozen "
            f"{tuple(FROZEN_DEV_FRAME_RANGE)} (FIRST 512 HOLD frames)"
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
            "the four HOLD DEV blocks end"
        )
    return {
        "dev_frame_range": [int(dev_first), int(dev_last)],
        "remainder_frame_range": [int(rem_first), int(rem_last)],
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "intra_file_hold_frame_range": [int(hold_first), int(hold_last)],
        "intra_file_val_frame_range": [int(val_first), int(val_last)],
        "hold_contained": True,
        "val_exterior_disjoint": True,
        "first_512_hold_frames": True,
        "verified": True,
    }


def verify_consumed_exclusions(dev_frames=None, remainder_frames=None) -> dict:
    """Gate family (c)-(f): consumed-TRAIN / consumed-VAL / S2-ii declaration.

    Pure code-level check (no I/O): neither the DEV blocks nor the declared
    remainder overlap the consumed TRAIN 0..1659 (P20H/I/J/K), the consumed
    VAL DEV 1660..2043 (P20M) or the VAL remainder 2044..2212; the
    DEV/build-frames disjointness declaration is pinned with the frozen
    frame sets (build subset TRAIN 0..1659; DEV subset HOLD 2213..2724;
    disjoint by split identity). Any violation raises before any protected
    content open.
    """
    dev_pair = (tuple(FROZEN_DEV_FRAME_RANGE) if dev_frames is None
                else tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    ranges = [tuple(dev_pair)] + [tuple(r) for r in FROZEN_BLOCK_RANGES]
    for label, (start, end) in (
            ("consumed TRAIN 0..1659", CONSUMED_TRAIN_FRAME_RANGE),
            ("consumed VAL DEV 1660..2043", CONSUMED_VAL_DEV_FRAME_RANGE),
            ("VAL remainder 2044..2212", VAL_REMAINDER_FRAME_RANGE)):
        for r_start, r_end in ranges:
            if not (r_end < start or r_start > end):
                raise ValueError(
                    f"BLOCKED(dev_block_range_identity): declared range "
                    f"{r_start}..{r_end} overlaps {label}"
                )
    # The declared HOLD remainder (2725..2766) is counted, never decoded;
    # it must still avoid the consumed TRAIN and the whole VAL pool.
    for label, (start, end) in (
            ("consumed TRAIN 0..1659", CONSUMED_TRAIN_FRAME_RANGE),
            ("the 1.5M VAL pool 1660..2212", INTRA_FILE_VAL_FRAME_RANGE)):
        if not (rem_pair[1] < start or rem_pair[0] > end):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): declared HOLD remainder "
                f"{rem_pair[0]}..{rem_pair[1]} overlaps {label}"
            )
    build_first, build_last = FROZEN_BUILD_FRAME_RANGE
    dev_first, dev_last = dev_pair
    if (build_first, build_last) != CONSUMED_TRAIN_FRAME_RANGE:
        raise ValueError("build-frames declaration drifted from TRAIN 0..1659")
    if not (build_last < dev_first or dev_last < build_first):
        raise ValueError("DEV/build-frames disjointness violated (S2-ii)")
    return {
        "build_frames": [int(build_first), int(build_last)],
        "dev_frames": [int(dev_first), int(dev_last)],
        "remainder_frames": [int(rem_pair[0]), int(rem_pair[1])],
        "consumed_train_disjoint": True,
        "consumed_val_dev_disjoint": True,
        "val_remainder_disjoint": True,
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
    """Deterministic HOLD development validation plus block/remainder slicing.

    P20M ``form_dev_blocks`` pattern with the P20N HOLD ranges (the accepted
    helper is VAL-pinned, so this local formation carries the identical
    validation semantics for the HOLD pool). Accepts a normalized pairs
    frame (``frame_id``/``pair_idx``/``alice_symbol``/``bob_symbol``). Any
    malformed population raises ``BLOCKED(dev_population_exact)``; any
    declared-range mismatch raises
    ``BLOCKED(blocks_exact_with_declared_remainder)``. No sorting key other
    than ``(frame_id, pair_idx)`` and no sampling of any kind.
    """
    try:
        pair = tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames)
    except TypeError as exc:
        raise TypeError(f"dev-frames must be a pair of integers: {exc}") from exc
    if pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise L2AltHold1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"dev-frames {pair} != frozen {tuple(FROZEN_DEV_FRAME_RANGE)}"
        )
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise L2AltHold1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"block-frames {block_frames} != frozen {FROZEN_BLOCK_FRAMES}"
        )
    try:
        rem_pair = tuple(opf._as_int(v, "remainder-frames", minimum=0)
                         for v in remainder_frames)
    except TypeError as exc:
        raise TypeError(f"remainder-frames must be a pair of integers: {exc}") from exc
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise L2AltHold1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"remainder-frames {rem_pair} != frozen {tuple(FROZEN_REMAINDER_FRAME_RANGE)}"
        )
    try:
        frame_id = np.asarray(table["frame_id"], dtype=np.int64)
        pair_idx = np.asarray(table["pair_idx"], dtype=np.int64)
        alice = np.asarray(table["alice_symbol"], dtype=np.int64)
        bob = np.asarray(table["bob_symbol"], dtype=np.int64)
    except (KeyError, TypeError, ValueError) as exc:
        raise L2AltHold1p5mContractError(
            f"BLOCKED(dev_population_exact): loader frame is malformed: {exc}"
        ) from exc
    if not (frame_id.shape == pair_idx.shape == alice.shape == bob.shape) or frame_id.ndim != 1:
        raise L2AltHold1p5mContractError(
            "BLOCKED(dev_population_exact): column shapes disagree"
        )
    for name, values in (("alice_symbol", alice), ("bob_symbol", bob)):
        if values.size == 0 or values.min() < 0 or values.max() >= N_BOB:
            raise L2AltHold1p5mContractError(
                f"BLOCKED(dev_population_exact): {name} outside 0..{N_BOB - 1}"
            )
    dev_first, dev_last = pair
    # The declared never-used remainder lies OUTSIDE the DEV selection by
    # design (frozen --dev-frames 2213 2724), so its presence and span are
    # measured from the unfiltered pool before DEV slicing; the remainder is
    # never decoded, only counted.
    pool_frame_id = np.asarray(table["frame_id"], dtype=np.int64)
    selected = (frame_id >= dev_first) & (frame_id <= dev_last)
    rows = int(np.sum(selected))
    if rows == 0:
        raise L2AltHold1p5mContractError(
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
        raise L2AltHold1p5mContractError(
            "BLOCKED(dev_population_exact): DEV frames "
            f"{unique_frames.size} with range {int(unique_frames[0])}.."
            f"{int(unique_frames[-1])} != frozen {FROZEN_DEV_FRAMES} with range "
            f"{dev_first}..{dev_last}"
        )
    if rows != FROZEN_DEV_PAIRS:
        raise L2AltHold1p5mContractError(
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
        raise L2AltHold1p5mContractError(
            "BLOCKED(dev_population_exact): pair_idx is not exactly 0..255 per frame"
        )
    ranges = []
    first = dev_first
    for _ in range(FROZEN_BLOCK_COUNT):
        last = first + int(block_frames) - 1
        ranges.append((first, last))
        first = last + 1
    if tuple(ranges) != tuple(tuple(r) for r in FROZEN_BLOCK_RANGES):
        raise L2AltHold1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): block ranges "
            f"{tuple(ranges)} != frozen {tuple(tuple(r) for r in FROZEN_BLOCK_RANGES)}"
        )
    rem_first, rem_last = rem_pair
    if first != rem_first:
        raise L2AltHold1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder "
            f"{rem_first}..{rem_last} does not start where the four DEV blocks end"
        )
    # Declared-remainder evidence from the unfiltered pool (never decoded).
    remainder_rows = (pool_frame_id >= rem_first) & (pool_frame_id <= rem_last)
    remainder_frame_ids = pool_frame_id[remainder_rows]
    if int(np.sum(remainder_rows)) != FROZEN_REMAINDER_SYMBOLS:
        raise L2AltHold1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder rows "
            f"{int(np.sum(remainder_rows))} != frozen {FROZEN_REMAINDER_SYMBOLS}"
        )
    if (np.unique(remainder_frame_ids).size != FROZEN_REMAINDER_FRAMES
            or int(remainder_frame_ids.min()) != rem_first
            or int(remainder_frame_ids.max()) != rem_last):
        raise L2AltHold1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder frames "
            f"!= frozen {rem_first}..{rem_last} ({FROZEN_REMAINDER_FRAMES} frames)"
        )
    check = verify_hold_containment(pair, rem_pair)
    if not check["verified"]:
        raise L2AltHold1p5mContractError("BLOCKED(dev_block_range_identity)")
    check2 = verify_consumed_exclusions(pair, rem_pair)
    if not check2["verified"]:
        raise L2AltHold1p5mContractError("BLOCKED(dev_block_range_identity)")
    blocks = []
    for index, (start, end) in enumerate(ranges):
        mask = (frame_id >= start) & (frame_id <= end)
        if int(np.sum(mask)) != FROZEN_SYMBOLS_PER_BLOCK:
            raise L2AltHold1p5mContractError(
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
# (d5) P20N tag domain.
# ---------------------------------------------------------------------------

def l2_alt_hold_1p5m_seed_bits(master: int, n: int, arm: str, block_index: int, *,
                               bit_length: int | None = None) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P20N domain).

    Rule: concatenate SHA-256 over
    ``"nbpolar-p20n-l2-alt-hold-1p5m-seed:<master>:<n>:<arm>:<block_index>:
    <counter>"`` for ``counter = 0, 1, ...`` (ASCII decimal), unpack each
    digest MSB-first and truncate to ``bit_length`` (default ``10*n + 63``).
    The P20N prefix and arm tokens differ from ALL prior domains on purpose.
    Seed contents are public control and are never persisted; only the bit
    length is recorded.
    """
    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P20N seed domain: {arm!r}")
    index = opf._as_int(block_index, "block_index", minimum=0)
    length = p20l.seed_bits_for(n) if bit_length is None else opf._as_int(
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
# (d6) Mandatory X09-R1 hazard instrumentation (recording-only, post-decode).
# ---------------------------------------------------------------------------

def _raw_p2_from_counts(counts_arr) -> np.ndarray:
    """Unfloored column-normalized TRAIN conditional ``p2`` from ``counts_ab``.

    Same recipe as the accepted ``raw_floor_diagnostics``: raw cell masses
    ``counts / column_total`` (zero for an unseen column) reshaped through
    the accepted ``derive_p2``. Pure; used only for the recorded floor
    fractions.
    """
    counts = np.asarray(counts_arr, dtype=np.float64)
    if counts.shape != (N_BOB, N_BOB):
        raise ValueError(f"counts must be (1024,1024), got {counts.shape}")
    col_totals = counts.sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.where(col_totals[None, :] > 0, counts / col_totals[None, :], 0.0)
    return np.ascontiguousarray(derive_p2(np.ascontiguousarray(raw)))


def _hazard_bits(p2_table, high_cell, bob, low_cell) -> np.ndarray:
    """``-log2`` arm-table mass at the given true/candidate cells (recording)."""
    mass = np.asarray(p2_table, dtype=np.float64)[high_cell, bob, low_cell]
    if not np.isfinite(mass).all() or (mass <= 0).any():
        raise ValueError(
            "hazard instrumentation: non-positive or non-finite arm-table mass"
        )
    return -np.log2(mass)


def _l2_hazard_diagnostics(*, block, view, p2_arm, counts_arr, l2_order, k2,
                           first_error) -> dict:
    """P20N mandatory recorder: eight scalars, post-decode, recording-only.

    Called after every SC call for the record has completed (after tag
    scoring) from the record writers at the carried-over P20M
    ``_selected_diagnostics`` code point. Reads truth (and the arm table)
    for RECORDING ONLY; its outputs are written into the record dict and
    are never passed to any decoder, metric builder, disclosure or order
    decision.

    Fields (frozen semantics; scalar-only):
    - ``l2_order_digest`` / ``l2_prefix_len``: frozen P20M order-file
      digest and the gated 6689 prefix length on every record;
    - ``l2_fail_in_prefix`` / ``l2_fail_hazard_bits`` /
      ``l2_fail_nbhd_mean_bits`` / ``l2_fail_nbhd_floor_frac``: null
      unless ``first_error_layer == L2``; otherwise the failing position's
      disclosed-prefix membership, its ``-log2`` arm-table mass at the true
      ``(U1_cond, B, U2)`` cell (``U1_cond`` = hard-L1 candidate on the
      operational arms, true high on the oracle arms; natural block symbol
      index per X09-R1 D4), the same quantity averaged over the frozen
      radius-R=8 window around the position (clipped to the block), and the
      fraction of window cells whose unfloored TRAIN conditional mass is
      below 1e-15;
    - ``l2_prefix_hazard_mean_bits`` / ``l2_prefix_floor_frac``: the same
      two quantities averaged over the disclosed-prefix positions using
      true cells, on every completed record (never null).
    """
    if int(k2) != int(FROZEN_K2):
        raise ValueError(
            "hazard instrumentation requires the gated prefix length "
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
    raw_p2 = _raw_p2_from_counts(counts_arr)
    diag = {
        "l2_order_digest": str(FROZEN_ORDER_DIGEST),
        "l2_prefix_len": int(k2),
        "l2_fail_in_prefix": None,
        "l2_fail_hazard_bits": None,
        "l2_fail_nbhd_mean_bits": None,
        "l2_prefix_hazard_mean_bits": None,
        "l2_fail_nbhd_floor_frac": None,
        "l2_prefix_floor_frac": None,
    }
    prefix_hazard = _hazard_bits(p2, high_true[prefix], bob[prefix], low_true[prefix])
    prefix_raw = raw_p2[high_true[prefix], bob[prefix], low_true[prefix]]
    diag["l2_prefix_hazard_mean_bits"] = float(np.mean(prefix_hazard))
    diag["l2_prefix_floor_frac"] = float(np.mean(prefix_raw < FROZEN_FLOOR))
    if first_error.get("first_error_layer") == "L2":
        pos = first_error.get("first_error_coord")
        if pos is None or not (0 <= int(pos) < n):
            raise ValueError(
                f"L2 failure requires a valid natural block symbol index, got {pos!r}"
            )
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
                         low_true[pos:pos + 1])[0]
        )
        lo = max(0, pos - int(FROZEN_HAZARD_R))
        hi = min(n - 1, pos + int(FROZEN_HAZARD_R))
        idx = np.arange(lo, hi + 1, dtype=np.int64)
        diag["l2_fail_nbhd_mean_bits"] = float(np.mean(
            _hazard_bits(p2, u1_cond[idx], bob[idx], low_true[idx])
        ))
        nbhd_raw = raw_p2[u1_cond[idx], bob[idx], low_true[idx]]
        diag["l2_fail_nbhd_floor_frac"] = float(np.mean(nbhd_raw < FROZEN_FLOOR))
    return diag


# ---------------------------------------------------------------------------
# Stage-B records (P20M schema: construction point + floor fields + §7).
# ---------------------------------------------------------------------------

def _base_record_fields(*, spec, arm_index, block, scoring, oracle, k_total,
                        budget_literal, alt_digest, order_digest) -> dict:
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
        "alt_digest": str(alt_digest),
        "l1_order_digest": str(order_digest),
        "l2_order_digest": str(order_digest),
        "full_block_key_dependent_bits": int(spec.leakage_bits),
        "public_control_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS),
        "disclosure_ce_ratio": (
            float(spec.leakage_bits / total_nll) if total_nll else None
        ),
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
                        k_total, budget_literal, alt_digest, order_digest,
                        counts_arr, p1, p2, l2_order, n, view, diag=None,
                        error=None) -> dict:
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=False,
        k_total=k_total, budget_literal=budget_literal, alt_digest=alt_digest,
        order_digest=order_digest)
    first_error = p20l.first_error_coordinate(
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
    # Recording-only recorder at the carried-over P20M code point; all SC
    # calls for this record have completed before this call.
    view_arm = dict(view)
    view_arm["u1_cond"] = (
        result.high_hat if result.high_hat is not None else view["high"])
    record.update(_l2_hazard_diagnostics(
        block=block, view=view_arm, p2_arm=p2, counts_arr=counts_arr,
        l2_order=l2_order, k2=FROZEN_K2, first_error=first_error))
    return record


def _control_record(result, *, spec, arm_index, block, scoring, resources,
                    k_total, budget_literal, alt_digest, order_digest,
                    counts_arr, p1, p2, l2_order, n, view, diag=None,
                    error=None) -> dict:
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=True,
        k_total=k_total, budget_literal=budget_literal, alt_digest=alt_digest,
        order_digest=order_digest)
    first_error = p20l.first_error_coordinate(None, result.low_hat, None, block["low"])
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
    record.update(_l2_hazard_diagnostics(
        block=block, view=view_arm, p2_arm=p2, counts_arr=counts_arr,
        l2_order=l2_order, k2=FROZEN_K2, first_error=first_error))
    return record


def _abort_record(*, spec, arm_index, block, k_total, budget_literal,
                  alt_digest, order_digest) -> dict:
    record = {
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
        "alt_digest": str(alt_digest),
        "l1_order_digest": str(order_digest),
        "l2_order_digest": str(order_digest),
        "full_block_key_dependent_bits": int(spec.leakage_bits),
        "public_control_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS),
        "disclosure_ce_ratio": None,
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
            str(FROZEN_ORDER_DIGEST) if field == "l2_order_digest"
            else (int(FROZEN_K2) if field == "l2_prefix_len" else None)
        )
    return record


# ---------------------------------------------------------------------------
# Aggregates (oracle excluded; restoration descriptive only).
# ---------------------------------------------------------------------------

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


def restoration_diagnostics(records) -> dict:
    """Descriptive B-vs-A and D-vs-C restoration reading (never a threshold)."""
    by_block: dict = {}
    for record in records:
        try:
            by_block.setdefault(int(record["block_index"]), {})[
                str(record.get("arm"))] = record
        except (KeyError, TypeError, ValueError):
            continue
    b_restored = maintain = 0
    d_restored = 0
    a_exact = b_exact = c_exact = d_exact = 0
    moves = []
    for block_index in sorted(by_block):
        cell = by_block[block_index]
        a = cell.get("A_incumbent_L2_operational")
        b = cell.get("B_alt_L2_operational")
        c = cell.get("C_incumbent_L2_oracle")
        d = cell.get("D_alt_L2_oracle")
        if a is not None and b is not None:
            a_ok, b_ok = bool(a.get("exact")), bool(b.get("exact"))
            a_exact += int(a_ok)
            b_exact += int(b_ok)
            if not a_ok and b_ok:
                b_restored += 1
            if a_ok and b_ok:
                maintain += 1
        if c is not None and d is not None:
            c_ok, d_ok = bool(c.get("exact")), bool(d.get("exact"))
            c_exact += int(c_ok)
            d_exact += int(d_ok)
            if not c_ok and d_ok:
                d_restored += 1
        moves.append({
            "block_index": block_index,
            "a_first_error_layer": None if a is None else a.get("first_error_layer"),
            "b_first_error_layer": None if b is None else b.get("first_error_layer"),
            "c_first_error_layer": None if c is None else c.get("first_error_layer"),
            "d_first_error_layer": None if d is None else d.get("first_error_layer"),
        })
    return {
        "b_restored_count": int(b_restored),
        "b_maintain_count": int(maintain),
        "d_restored_count": int(d_restored),
        "a_exact_blocks": int(a_exact),
        "b_exact_blocks": int(b_exact),
        "c_exact_blocks": int(c_exact),
        "d_exact_blocks": int(d_exact),
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
        "l2_construction": spec.prior_source,
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
    arm_table = {spec.name: _arm_aggregate(records, spec)
                 for spec in frozen_arm_table()}
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
        "restoration": restoration_diagnostics(records),
        "arms": arm_table,
        "undetected_count": sum(1 for r in records if r.get("outcome") == "undetected"),
        "nonfinite_count": sum(1 for r in records if r.get("nonfinite") is True),
    }


# ---------------------------------------------------------------------------
# Stage-B integrity gates (frozen §9 order; all true or BLOCKED).
# ---------------------------------------------------------------------------

def hazard_instrumentation_complete(records) -> bool:
    """All eight §7 scalars present with the frozen nullability per record."""
    if not records:
        return False
    for record in records:
        if str(record.get("outcome")) == "resource_abort":
            continue
        if any(field not in record for field in HAZARD_FIELDS):
            return False
        if str(record.get("l2_order_digest")) != str(FROZEN_ORDER_DIGEST):
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
        )
        if record.get("first_error_layer") == "L2":
            if record.get("l2_fail_in_prefix") is None:
                return False
            for field in fail_fields[1:]:
                if record.get(field) is None:
                    return False
        else:
            for field in fail_fields:
                if record.get(field) is not None:
                    return False
    return True


def _integrity_gates(*, n, k1, k2, k_total, arms, identity, manifest,
                     dev_source_pin, dev_pin, disjoint_pin, order_pin,
                     formation, records, events, calls, incremental, accounting,
                     provenance_violations, cap, wall_s, resource_stop,
                     incumbent_verified, alt_verified, hazard_pin,
                     prior_stat_before, prior_stat_after, alt_stat_before,
                     alt_stat_after, dev_stat_before, dev_stat_after,
                     registered_paths, opened_paths, final: bool) -> dict:
    gates: dict = {}
    gates["predecessor_construction_identity"] = bool(identity is not None)
    gates["incumbent_prior_identity"] = bool(
        incumbent_verified is not None and bool(incumbent_verified.get("passed")))
    gates["alt_l2_identity"] = bool(
        alt_verified is not None and bool(alt_verified.get("passed")))
    gates["alt_construction_budget_feasibility"] = bool(FROZEN_D2_FEASIBLE is True)
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
            and int(k1) == FROZEN_K1 and int(k2) == FROZEN_K2
            and int(k1) + int(k2) == FROZEN_K_TOTAL
            and str(hazard_pin.get("budget_literal")) == FROZEN_BUDGET_LITERAL)
    except (AttributeError, TypeError, ValueError):
        gates["k_literal_exact"] = False
    gates["target_population_contract"] = bool(
        incumbent_verified is not None and bool(incumbent_verified.get("passed")))
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
    gates["sixteen_records_exact"] = (
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
        shared_l1 = p20l.l1_prefix_positions(order_pin["l1_order"], FROZEN_K1)
        shared_l2 = p20l.l2_prefix_positions(order_pin["l2_order"], FROZEN_K2)
        orders_ok = (
            shared_l1.shape == (FROZEN_K1,)
            and shared_l2.shape == (FROZEN_K2,)
            and int(arms[0].k1) == FROZEN_K1 and int(arms[0].k2) == FROZEN_K2
            and int(arms[1].k1) == FROZEN_K1 and int(arms[1].k2) == FROZEN_K2
            and int(arms[2].k1) == 0 and int(arms[2].k2) == FROZEN_K2
            and int(arms[3].k1) == 0 and int(arms[3].k2) == FROZEN_K2
        )
    except (ValueError, IndexError, AttributeError, TypeError):
        orders_ok = False
    gates["orders_valid_k_prefixes_within_registered_arms"] = bool(orders_ok)
    gates["hazard_instrumentation_complete"] = bool(
        hazard_instrumentation_complete(records))
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
        and int(accounting.get("incumbent_content_loads", -1)) <= 1
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


def l2_alt_hold_1p5m_label(gates: dict) -> str:
    """Descriptive COMPLETE iff every integrity gate holds, else BLOCKED(first)."""
    failing = [g for g in INTEGRITY_GATE_ORDER if not gates.get(g, False)]
    if not failing:
        return COMPLETE_LABEL
    return f"BLOCKED({failing[0]})"


@dataclass(frozen=True, eq=False)
class L2AltHold1p5mRun:
    """In-memory P20N Stage-B run (also returned by the runner)."""

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
        "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
        "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
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
        "planned_key_dependent_bits": FROZEN_TOTAL_KEY_DEPENDENT_BITS,
        "planned_public_control_bits": FROZEN_TOTAL_PUBLIC_CONTROL_BITS,
        "hazard_window_R": int(FROZEN_HAZARD_R),
        "frozen_command": FROZEN_COMMAND,
        "frozen_plan_manifest": manifest,
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
    }
    opf._write_json(out_path / "frozen_plan.json", plan)
    return plan


def _render_report(summary: dict) -> str:
    aggregates = summary.get("aggregates", {})
    restoration = aggregates.get("restoration", {})
    lines = [
        "# NB-Polar Phase 4-P20N fixed-disclosure ALT-L2 construction on 1.5M HOLD",
        "",
        f"- protocol: `{summary.get('analysis')}` (mode `{summary.get('mode')}`)",
        f"- source: `{summary.get('source')}`; N={summary.get('n')}; "
        f"K1={summary.get('k1')} K2={summary.get('k2')} K_total={summary.get('k_total')} "
        "(carried literals, never recomputed)",
        "- alt-L2 construction: unit-pseudocount conditional; alt-table digest "
        f"`{summary.get('alt_digest')}`",
        f"- order file digest: `{summary.get('order_digest')}` "
        "(shared first-331 / first-6689 prefixes on all four arms)",
        f"- blocks: {summary.get('block_ranges')} "
        f"(remainder {summary.get('remainder_frames')} never used)",
        f"- outcome: `{summary.get('outcome_label')}`; "
        f"records {summary.get('records_completed')}/{summary.get('planned_records')}",
        f"- operational exact: "
        f"{aggregates.get('operational', {}).get('exact_count')} "
        f"(A {restoration.get('a_exact_blocks')} / B {restoration.get('b_exact_blocks')}); "
        f"b_restored_count={restoration.get('b_restored_count')} "
        f"(descriptive: A fail -> B exact); maintain={restoration.get('b_maintain_count')}",
        f"- oracle exact: {aggregates.get('oracle', {}).get('exact_count')} "
        f"(C {restoration.get('c_exact_blocks')} / D {restoration.get('d_exact_blocks')}); "
        f"d_restored_count={restoration.get('d_restored_count')} "
        "(diagnostic only, never operational)",
        f"- undetected: {aggregates.get('undetected_count')}; "
        f"nonfinite: {aggregates.get('nonfinite_count')}",
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
        "not qualification efficiency; undetected is never success. No "
        "recovery / FER / superiority / qualification claim is made; the "
        "B-vs-A and D-vs-C readings are descriptive only.",
        "",
    ]
    return "\n".join(lines)


def run_l2_alt_hold_1p5m(
    *,
    prior=None,
    alt_prior=None,
    prior_path=FROZEN_INCUMBENT_PATH,
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
) -> L2AltHold1p5mRun:
    """Execute the frozen P20N four-arm diagnostic once; write five files.

    ``prior`` / ``alt_prior`` / ``dev_table`` are documented injected test
    seams; the frozen CLI passes only the frozen point, loads the Stage-A
    frozen alt table and the P20M incumbent prior read-only exactly once
    each, loads the frozen order file read-only behind the order-digest
    gate, and reads the HOLD parquet through its accepted loader exactly
    once. The V25 counts NPZ is never opened. The construction swap is
    hardcoded (never CLI-tunable): A runs the incumbent L2 at 331/6689, B
    the alt L2 at 331/6689, C the incumbent true-L1 oracle and D the alt
    true-L1 oracle at K2=6689, all four on the SAME frozen P20M order
    prefixes. There is no sampling code path anywhere in this module.
    """
    global _INCUMBENT_CONTENT_LOADED, _ALT_CONTENT_LOADED
    global _DEV_PARQUET_CONTENT_OPENED
    pins = alt_pins_frozen()
    if pins["d2_feasible"] is not True:
        raise ValueError(
            "BLOCKED(alt_construction_budget_feasibility): Stage-A D2 outcome is "
            "ALT_CONSTRUCTION_BUDGET_INFEASIBLE (HOLD untouched; no Stage-B run)"
        )
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    floor = _check_floor(floor)
    source = _check_source(source)
    n = _check_n(n)
    if k1 is None or k2 is None:
        raise ValueError("frozen point requires --k1/--k2 equal to the carried literals")
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
        raise ValueError("frozen point requires --prior-digest equal to the P20M pin")
    prior_digest = _check_prior_digest(prior_digest)
    if order_digest is None:
        raise ValueError("frozen point requires --order-digest equal to the P20M pin")
    order_digest = _check_order_digest(order_digest)
    if alt_digest is None:
        raise ValueError("frozen point requires --alt-digest equal to the Stage-A pin")
    alt_digest = _check_alt_digest(alt_digest)
    arms = frozen_arm_table() if check_frozen_arm_table() else ()

    # Gate family (a)->(g) in the frozen order before any protected content
    # open: predecessor construction identity, cross-file source-tag+digest
    # (a), intra-file HOLD-containment (b), consumed-TRAIN / consumed-VAL-DEV
    # / VAL-remainder exclusions + S2-ii DEV/build-frames declaration (c)-(f),
    # then order-freeze + K-literal + alt-identity (g).
    if str(construction_digest) != str(FROZEN_CONSTRUCTION_DIGEST):
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = _gate_call("predecessor_construction_identity",
                          verify_predecessor_construction, construction,
                          expected_digest=construction_digest)
    identity = verified["record"]
    dev_source_pin = _gate_call("dev_block_range_identity", verify_dev_source_identity,
                                dev_pairs)
    dev_pin = verify_hold_containment(dev_frames, remainder_frames)
    disjoint_pin = verify_consumed_exclusions(dev_frames, remainder_frames)
    manifest = _gate_call("dev_split_manifest_identity", verify_dev_manifest,
                          manifest_path, source=source)
    order_pin = _gate_call(
        "order_derivation_identity", verify_stage_b_order_file_p20m, order_file,
        expected_digest=order_digest,
        expected_prior_digest=str(FROZEN_INCUMBENT_DIGEST),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    hazard_pin = {
        "k_literal": True,
        "budget_literal": k_literals["budget_literal"],
        "alt_floor_rate": None,
    }

    # One-open guards are refusals before any content load/open of any input.
    if prior is None and _INCUMBENT_CONTENT_LOADED:
        raise ValueError("reload refused: the single incumbent-prior load was consumed")
    if alt_prior is None and _ALT_CONTENT_LOADED:
        raise ValueError("reload refused: the single alt-table load was consumed")
    if dev_table is None and _DEV_PARQUET_CONTENT_OPENED:
        raise ValueError("reopen refused: the single HOLD parquet content open was consumed")

    # Input existence and stat-only metadata come before any content load/open.
    real_incumbent = prior is None
    real_alt = alt_prior is None
    real_dev = dev_table is None
    if real_incumbent:
        incumbent_file = Path(prior_path)
        if not incumbent_file.is_file():
            raise FileNotFoundError(f"P20M incumbent prior not found: {incumbent_file}")
        prior_stat_before = _stat_record(incumbent_file)
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
            raise FileNotFoundError(f"1p5M HOLD pairs parquet not found: {dev_path_obj}")
        dev_stat_before = _stat_record(dev_path_obj)
        if dev_stat_before["size_bytes"] != FROZEN_DEV_PAIRS_SIZE:
            raise ValueError(
                "1.5M HOLD pairs size mismatch before content open: "
                f"observed {dev_stat_before['size_bytes']} != "
                f"expected {FROZEN_DEV_PAIRS_SIZE}"
            )
    else:
        dev_stat_before = _stat_record(None)
    registered_paths = []
    if real_incumbent:
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
        prior_path=prior_path if real_incumbent else None, prior_digest=prior_digest,
        alt_path=alt_prior_path if real_alt else None, alt_digest=alt_digest,
        dev_pairs=dev_pairs, manifest_path=manifest_path, dev_frames=dev_frames,
        block_frames=block_frames, remainder_frames=remainder_frames,
        tag_master=tag_master, chunk_rows=chunk_rows, tag_bits=tag_bits,
        order_file=order_file, order_digest=order_digest, identity=identity,
        manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
        disjoint_pin=disjoint_pin, order_pin=order_pin)
    accounting = {
        "input_mode": "real" if (real_incumbent or real_alt or real_dev) else "injected",
        "incumbent_input_mode": "frozen_prior_file" if real_incumbent else "injected_prior",
        "alt_input_mode": "frozen_alt_file" if real_alt else "injected_alt",
        "dev_input_mode": "pairs_parquet" if real_dev else "injected_table",
        "prior_path": str(prior_path) if real_incumbent else None,
        "alt_prior_path": str(alt_prior_path) if real_alt else None,
        "dev_pairs_path": str(dev_pairs) if real_dev else None,
        "manifest_path": str(manifest_path),
        "construction_path": str(construction),
        "prior_loader": "per_session_calibration.raw_prior(read-only seam)" if real_incumbent else None,
        "pairs_loader": p20l.PAIRS_LOADER_IDENTITY if real_dev else None,
        "registered_content_paths": registered_paths,
        "opened_content_paths": opened_paths,
        "artifact_content_reads_allowed_per_input": 1,
        "counts_content_opens": 0,
        "incumbent_content_loads": 0,
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
        # ---- input 1: the single incumbent-prior load + identity gate.
        if real_incumbent:
            with open(prior_path, "rb") as fh:
                data = np.load(fh, allow_pickle=False)
                with data:
                    raw_arrays = {k: np.asarray(data[k]) for k in data.files}
            _INCUMBENT_CONTENT_LOADED = True
            accounting["incumbent_content_loads"] = 1
            opened_paths.append(str(Path(prior_path).resolve()))
        else:
            raw_arrays = dict(prior)
        incumbent_verified = verify_corrected_prior(
            raw_arrays, expected_digest=prior_digest, expected_h1=FROZEN_H1_INC,
            expected_h2=FROZEN_H2_INC, expected_total=FROZEN_H_TOTAL_INC)
        p1_inc = incumbent_verified["p1"]
        p2_inc = incumbent_verified["p2"]
        counts_inc = incumbent_verified["counts"]

        # ---- input 2: the single alt-table load + alt_l2_identity gate.
        if real_alt:
            alt_verified = _gate_call(
                "alt_l2_identity", verify_alt_l2_identity, alt_prior_path,
                expected_digest=alt_digest, incumbent_arrays=raw_arrays)
            _ALT_CONTENT_LOADED = True
            accounting["alt_content_loads"] = 1
            opened_paths.append(str(Path(alt_prior_path).resolve()))
            alt_stat_after_load = _stat_record(Path(alt_prior_path))
        else:
            alt_verified = verify_alt_l2_arrays(
                dict(alt_prior), incumbent_arrays=raw_arrays)
        p1_alt = alt_verified["p1"]
        p2_alt = alt_verified["p2_alt"]
        counts_alt = alt_verified["counts_ab"]
        # The alt-table floor-hit rate is a Stage-A frozen literal.
        hazard_pin = {
            "k_literal": True,
            "budget_literal": k_literals["budget_literal"],
            "alt_floor_rate": FROZEN_ALT_FLOOR_HIT_RATE,
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
                incumbent_verified=incumbent_verified, alt_verified=alt_verified,
                hazard_pin=hazard_pin,
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
                "alt_digest": str(alt_digest),
                "order_digest": str(order_pin.get("order_digest")),
                "alt_h_literals": alt_h_literals,
                "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
                "remainder_frames": list(FROZEN_REMAINDER_FRAME_RANGE),
                "dev_source": dict(dev_source_pin),
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
                    "descriptive fixed-disclosure alternative-L2-construction "
                    "diagnostic on new-segment 1.5M HOLD blocks (N=32768, four "
                    "HOLD blocks 2213..2724) under the frozen incumbent prior "
                    "and the single preregistered alt-L2 conditional; C/D are "
                    "oracle-labelled diagnostic controls, never an operational "
                    "protocol or deployable result; not real-frame FER, "
                    "reconciliation efficiency, leakage, key rate, scaling "
                    "superiority, qualification or promotion evidence; the "
                    "CE-normalized disclosure ratio is not qualification "
                    "efficiency; undetected is never success; no reliability "
                    "or recovery claim is licensed"
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
                        k_total=int(rest_spec.k1) + int(rest_spec.k2),
                        budget_literal=budget_literal, alt_digest=alt_digest,
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
            seed = l2_alt_hold_1p5m_seed_bits(
                tag_master, n, spec.name, block_index, bit_length=p20l.seed_bits_for(n))

            def _tag_fn(bits, _seed, tag_bits, _fixed=seed):
                return toeplitz_tag(bits, _fixed, tag_bits)

            block_start = time.perf_counter()
            p1_use, p2_use, counts_use = prior_by_source[spec.prior_source]
            l1_use = np.asarray(order_pin["l1_order"], dtype=np.int64)
            l2_use = np.asarray(order_pin["l2_order"], dtype=np.int64)
            if spec.kind == "operational":
                # A/B share the accepted operational path bit-for-bit except
                # the L2 table: A runs the incumbent p2, B the alt p2, both
                # at the SAME carried 331/6689 point on the SAME frozen P20M
                # order prefixes. The swap is hardcoded, never CLI-tunable.
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
                    k_total=int(spec.k1) + int(spec.k2),
                    budget_literal=budget_literal, alt_digest=alt_digest,
                    order_digest=order_digest, counts_arr=counts_use, p1=p1_use,
                    p2=p2_use, l2_order=l2_use, n=n, view=view, error=error)
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
                    k_total=int(spec.k1) + int(spec.k2),
                    budget_literal=budget_literal, alt_digest=alt_digest,
                    order_digest=order_digest, counts_arr=counts_use, p1=p1_use,
                    p2=p2_use, l2_order=l2_use, n=n, view=view, error=error)

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
        if real_incumbent:
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
            incumbent_verified=incumbent_verified, alt_verified=alt_verified,
            hazard_pin=hazard_pin,
            prior_stat_before=prior_stat_before, prior_stat_after=prior_stat_after,
            alt_stat_before=alt_stat_before, alt_stat_after=alt_stat_after,
            dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_after,
            registered_paths=registered_paths, opened_paths=opened_paths,
            final=True)
        outcome_label = l2_alt_hold_1p5m_label(gates)
        summary = partial_summary(outcome_label, gates, wall_s)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        identity_doc = {
            "predecessor_construction": identity,
            "split_manifest": manifest,
            "dev_source_pin": dev_source_pin,
            "dev_block_pin": dev_pin,
            "build_dev_disjointness_s2_ii": disjoint_pin,
            "expected_incumbent_digest": prior_digest,
            "incumbent_digest": str(incumbent_verified["digest"]),
            "recomputed_incumbent_literals": {
                "h1": float(incumbent_verified["h1"]),
                "h2": float(incumbent_verified["h2"]),
                "h_total": float(incumbent_verified["h_total"]),
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
                "verified": bool(order_pin.get("verified")),
            },
            "expected_order_digest": str(order_digest),
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
        return L2AltHold1p5mRun(summary=summary, records=tuple(records), gates=gates)
    except L2AltHold1p5mResourceError:
        raise
    except MemoryError as exc:
        raise L2AltHold1p5mResourceError(
            f"resource stop: MemoryError: {exc}") from exc


STAGE_A_ONLY_FLAGS = ("alpha", "out")
SHARED_FLAGS = ("prior", "prior_digest", "floor")
STAGE_B_ONLY_FLAGS = (
    "alt_prior", "alt_digest", "source", "n", "k1", "k2", "construction",
    "construction_digest", "dev_pairs", "dev_frames", "block_frames",
    "remainder_frames", "tag_master", "chunk_rows", "tag_bits",
    "order_file", "order_digest", "out_dir",
)
STAGE_B_FLAGS = SHARED_FLAGS + STAGE_B_ONLY_FLAGS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p20n-l2-alt-hold-1p5m",
        description=(
            "NB-Polar Phase 4-P20N fixed-disclosure ALT-L2 construction on "
            "1.5M HOLD: --derive runs the Stage-A derivation on the read-only "
            "P20M worktree product; otherwise all Stage-B flags are required "
            "(frozen command, no production default)"
        ),
    )
    parser.add_argument("--derive", action="store_true",
                        help="Stage-A derivation mode (all Stage-A flags required)")
    parser.add_argument("--alpha", default=None, type=float,
                        help="Stage-A construction marker; only the frozen 1")
    parser.add_argument("--out", default=None, help="Stage-A alt-table output path")
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
        if args.derive:
            given_b = [name for name in STAGE_B_ONLY_FLAGS
                       if getattr(args, name) is not None]
            if given_b:
                raise ValueError(
                    "mixed invocation refused: --derive takes no Stage-B flags "
                    f"(got {given_b}); refusing before any read or write"
                )
            missing = [name for name in ("prior", "prior_digest", "alpha", "floor", "out")
                       if getattr(args, name) is None]
            if missing:
                raise ValueError(
                    "missing required Stage-A flags: " + ",".join(missing)
                    + "; refusing before any read or write"
                )
            result = run_derive_stage_a(
                prior_path=args.prior, prior_digest=args.prior_digest,
                alpha=args.alpha, floor=args.floor, out_path=args.out)
            print(json.dumps(result, sort_keys=True))
            return 0
        given_a = [name for name in STAGE_A_ONLY_FLAGS
                   if getattr(args, name) is not None]
        if given_a:
            raise ValueError(
                "mixed invocation refused: Stage-A-only flags "
                f"(got {given_a}) require --derive; refusing before any read or write"
            )
        given = [name for name in STAGE_B_FLAGS if getattr(args, name) is not None]
        missing = [name for name in STAGE_B_FLAGS if getattr(args, name) is None]
        if missing:
            if not given:
                raise ValueError(
                    "ambiguous invocation refused: neither --derive nor any "
                    "Stage-B flag was given; refusing before any read or write"
                )
            raise ValueError(
                "missing required Stage-B flags: " + ",".join(missing)
                + "; refusing before any read or write"
            )
        run = run_l2_alt_hold_1p5m(
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
            "b_restored_count": summary["aggregates"]["restoration"][
                "b_restored_count"],
            "d_restored_count": summary["aggregates"]["restoration"][
                "d_restored_count"],
            "integrity_all_pass": summary["integrity_all_pass"],
            "outcome_label": summary["outcome_label"],
            "out_root": args.out_dir,
        }, sort_keys=True))
        return 0
    except (ValueError, FileExistsError, OSError,
            L2AltHold1p5mContractError) as exc:
        print(f"nbpolar phase4-p20n l2 alt hold 1p5m refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL_NAME", "MODE", "Q", "ALPHA", "N_BOB", "FROZEN_N", "FROZEN_SOURCE",
    "FROZEN_SOURCE_TAG", "FROZEN_FLOOR", "FROZEN_ALPHA", "NORM_TOL",
    "FROZEN_K1", "FROZEN_K2", "FROZEN_K_TOTAL", "FROZEN_H1_INC",
    "FROZEN_H2_INC", "FROZEN_H_TOTAL_INC", "FROZEN_BUDGET_LITERAL",
    "FROZEN_INCUMBENT_PATH", "FROZEN_INCUMBENT_DIGEST", "FROZEN_ORDER_FILE_PATH",
    "FROZEN_ORDER_DIGEST", "FROZEN_CONSTRUCTION_PATH", "FROZEN_CONSTRUCTION_DIGEST",
    "FROZEN_DEV_PAIRS_PATH", "FROZEN_DEV_PAIRS_SIZE", "FROZEN_DEV_PAIRS_SHA256",
    "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA", "FROZEN_PUBLIC_CONTROL_BITS",
    "FROZEN_RAW_INPUT_BITS", "FROZEN_MANIFEST_TRAIN_PAIRS",
    "FROZEN_ALT_PATH", "ALT_L2_NPZ_KEYS",
    "FROZEN_DEV_FRAME_RANGE", "FROZEN_DEV_FRAMES", "FROZEN_DEV_PAIRS",
    "FROZEN_BLOCK_COUNT", "FROZEN_BLOCK_FRAMES", "FROZEN_PAIRS_PER_FRAME",
    "FROZEN_SYMBOLS_PER_BLOCK", "FROZEN_BLOCK_RANGES",
    "FROZEN_REMAINDER_FRAME_RANGE", "FROZEN_REMAINDER_FRAMES",
    "FROZEN_REMAINDER_SYMBOLS", "INTRA_FILE_VAL_FRAME_RANGE",
    "INTRA_FILE_HOLD_FRAME_RANGE", "CONSUMED_TRAIN_FRAME_RANGE",
    "CONSUMED_VAL_DEV_FRAME_RANGE", "VAL_REMAINDER_FRAME_RANGE",
    "FROZEN_BUILD_FRAME_RANGE",
    "FROZEN_TAG_MASTER", "FROZEN_CHUNK_ROWS", "FROZEN_TAG_BITS", "SEED_PREFIX",
    "FROZEN_ALT_CEILING_BITS", "FROZEN_OPERATIONAL_CEILING_BITS", "FROZEN_HAZARD_R",
    "FROZEN_OUT_ROOT", "OUTPUT_FILES", "ATTEMPT_CONSUMPTION_POINT",
    "COMPLETE_LABEL", "FROZEN_ALT_DIGEST", "FROZEN_ALT_CE_INSAMPLE",
    "FROZEN_INCUMBENT_CE_INSAMPLE", "FROZEN_ALT_IDEAL_LENGTH_BITS",
    "FROZEN_D2_FEASIBLE", "FROZEN_ALT_FLOOR_HITS", "FROZEN_ALT_FLOOR_HIT_RATE",
    "FROZEN_ALT_ZERO_COLUMNS", "FROZEN_ALT_F_ALT_MIN", "FROZEN_ALT_F_ALT_MAX",
    "OPERATIONAL_PROVENANCE", "ORACLE_PROVENANCE",
    "ArmSpec", "FROZEN_ARM_NAMES", "OPERATIONAL_ARM_NAMES", "ORACLE_ARM_NAMES",
    "PLANNED_SC_CALLS", "PLANNED_TAG_INVOCATIONS", "PLANNED_RECORDS",
    "FROZEN_TOTAL_KEY_DEPENDENT_BITS", "FROZEN_TOTAL_PUBLIC_CONTROL_BITS",
    "INTEGRITY_GATE_ORDER", "HAZARD_FIELDS", "FROZEN_COMMAND",
    "RSS_LIMIT_BYTES", "TOTAL_WALL_S", "EXTERNAL_TIMEOUT_S", "ULIMIT_VIRTUAL_KIB",
    "frozen_arm_table", "check_frozen_arm_table", "alt_pins_frozen",
    "check_k_literals", "alt_prefloor_table", "derive_alt_l2_arrays",
    "in_sample_l2_ce_bits_per_symbol", "feasibility_literals",
    "load_incumbent_prior_arrays", "run_derive_stage_a",
    "verify_alt_l2_arrays", "verify_alt_l2_identity",
    "verify_hold_containment", "verify_consumed_exclusions", "form_hold_blocks",
    "l2_alt_hold_1p5m_seed_bits", "_l2_hazard_diagnostics",
    "hazard_instrumentation_complete", "oracle_isolation_ok",
    "restoration_diagnostics", "build_aggregates", "l2_alt_hold_1p5m_label",
    "L2AltHold1p5mContractError", "L2AltHold1p5mResourceError", "L2AltHold1p5mRun",
    "run_l2_alt_hold_1p5m", "build_parser", "main",
    "STAGE_A_ONLY_FLAGS", "SHARED_FLAGS", "STAGE_B_ONLY_FLAGS", "STAGE_B_FLAGS",
]
