"""NB-Polar Phase 4-P20M N=32768 raw-prior + session-budget operating-point swap.

Thin importer of the accepted ``l1_order_1p5m`` runner (read-only; that
module is never edited here): it already implements the VAL population,
the TRAIN-exclusion gate family, the Stage-A order-file + ``--order-digest``
mechanism with zero Stage-B sampling, and the P20A endpoint/taxonomy/
recount/resource machinery. Exact delta list, nothing else:

- (d1) prior source -> the Stage-A corrected-prior artifact
  (``raw_prior_1p5m.npz``) behind a new ``corrected_prior_identity`` gate
  (digest + lambda-0.0 pin + exact key set + H-literal recomputation
  within 1e-12 + ``p_b`` cross-check);
- (d2) K pins -> the Stage-A derived (K_total, K1, K2) with the S2-(i)
  budget-literal display recomputed from the same-run session H;
- (d3) orders -> the Stage-A frozen ``raw_prior_orders_1p5m.json`` via the
  reused order-file mechanism (L1+L2 worst-first orders from the corrected
  prior, digest-gated, zero Stage-B sampling);
- (d4) arms G0/G1/G2 (G0 = lambda-prior/P16-order control at 319/6492);
- (d5) new P20M tag domain (master 2026092280);
- (d6) per-record floor-hit fields + the S2 ``floor_hit_rate_reported`` gate;
- (d7) DEV/build-frames disjointness declared inside the TRAIN-exclusion
  gate (build subset TRAIN 0..1659; DEV subset VAL 1660..2043).

No SC/transform/floor/tag-semantics change; no second factor.

Two explicit modes, never mixed: (i) Stage-A derivation mode (``--derive``;
read-only worktree input, zero protected opens) and (ii) Stage-B frozen
command mode (all Stage-B flags required, no production default). Mixed or
ambiguous invocation refuses before anything is read or written.

Stage-A pins (``FROZEN_PRIOR_DIGEST`` / ``FROZEN_H1`` / ``FROZEN_H2`` /
``FROZEN_H_TOTAL`` / ``FROZEN_K_TOTAL`` / ``FROZEN_K1_G1`` /
``FROZEN_K2_G1`` / ``FROZEN_ORDER_DIGEST`` /
``FROZEN_CONSTRUCTION_FLOOR_HITS`` / ``FROZEN_CONSTRUCTION_FLOOR_HIT_RATE``)
are ``None`` until the Stage-A derivation fills them; the Stage-B path
refuses with ``Stage-A freeze not yet applied`` while any pin is ``None``.
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
from . import l1_order_1p5m as p20l
from . import per_session_calibration as psc
from ...io.pairs_loader import load_pairs_table, normalize_pair_columns
from .algebra import make_gf32
from .prior import Provenance, derive_p1, derive_p2
from .empirical_channel import sample_full_block
from .empirical_genie_scaling import block_genie_risks, select_empirical_split
from .target_construction import entropy_bits
from .target_n_scaling import budget_k_total
from .transform import polar_transform
from .two_layer import labels_to_bits, seed_bits_for

# Reused accepted contracts (read-only; never reimplemented here).
run_operational_block = p20l.run_operational_block
run_oracle_control_block = p20l.run_oracle_control_block
OracleControlResult = p20l.OracleControlResult
verify_predecessor_construction = p20l.verify_predecessor_construction
verify_dev_source_identity = p20l.verify_dev_source_identity
verify_dev_block_identity = p20l.verify_dev_block_identity
verify_dev_manifest = p20l.verify_dev_manifest
verify_lambda_prior = p20l.verify_stage_b_prior
form_dev_blocks = p20l.form_dev_blocks
candidate_nll_bits = p20l.candidate_nll_bits
raw_floor_diagnostics = p20l.raw_floor_diagnostics
first_error_coordinate = p20l.first_error_coordinate
l1_prefix_positions = p20l.l1_prefix_positions
l2_prefix_positions = p20l.l2_prefix_positions
holdout_nll_bits = p20l.holdout_nll_bits
raw_symbol_error_rate = p20l.raw_symbol_error_rate
polar_transform_fn = polar_transform
make_gf32_fn = make_gf32
toeplitz_tag_fn = toeplitz_tag

PROTOCOL_NAME = "nbpolar-p20m-raw-prior-val-1p5m"
MODE = "dev-raw-prior-val-1p5m"

Q = p20l.Q
ALPHA = p20l.ALPHA
N_BOB = p20l.N_BOB
FROZEN_N = 32768
FROZEN_SOURCE = "1p5M"
FROZEN_SOURCE_TAG = "type2_1p5M_20260121_183806"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
NORM_TOL = 1e-12
# (d4) G0 control pins: the carried-over failing point, never CLI-tunable.
FROZEN_K1_G0 = 319
FROZEN_K2_G0 = 6492
FROZEN_K_TOTAL_G0 = 6811
FROZEN_LEAKAGE_G0 = 34119  # 5 * 6811 + 64 (G0 operational control)
FROZEN_CONTROL_LEAKAGE_G2_SCALE = 5  # disclosed bits per coordinate
FROZEN_PUBLIC_CONTROL_BITS = seed_bits_for(FROZEN_N)  # 327743
FROZEN_RAW_INPUT_BITS = 10 * FROZEN_N  # 327680 per block

OPERATING_POINT_SWAP_RULE = (
    "single preregistered operating-point swap at the session-derived "
    "point: G1_raw_prior_session_budget runs the frozen greedy SC on the "
    "Stage-A corrected raw-count prior (no lambda anywhere) with the "
    "Stage-A derived (K1,K2) on the first-K1 of the frozen derived L1 "
    "order FILE and the first-K2 of the frozen derived L2 order FILE "
    "(positions fixed by the frozen files, never selected on closed "
    "blocks, the consumed 1M pool, P20H DEV 0..383, P20I DEV 384..767, "
    "P20J DEV 768..1151, P20K DEV + remainder 1152..1659, VAL remainder "
    "2044..2212, or new DEV data); G0_old_point_base is the carried-over "
    "failing point (lambda prior + frozen P16 orders at k1=319/k2=6492); "
    "G2_true_l1_diagnostic is the true-L1 oracle at the candidate K2; "
    "no K reselection, no second factor"
)

# Development population: identical pins to the accepted P20L population
# (FIRST 384 VAL frames 1660..2043; same manifest; same exclusions).
FROZEN_DEV_FRAME_RANGE = (1660, 2043)
FROZEN_DEV_FRAMES = 384
FROZEN_DEV_PAIRS = 98304
FROZEN_BLOCK_COUNT = 3
FROZEN_BLOCK_FRAMES = 128
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_BLOCK_RANGES = ((1660, 1787), (1788, 1915), (1916, 2043))
FROZEN_REMAINDER_FRAME_RANGE = (2044, 2212)
FROZEN_REMAINDER_FRAMES = 169
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
INTRA_FILE_VAL_FRAME_RANGE = (1660, 2212)
INTRA_FILE_HOLD_FRAME_RANGE = (2213, 2766)
P20H_DEV_FRAME_RANGE = (0, 383)
P20I_DEV_FRAME_RANGE = (384, 767)
P20J_DEV_FRAME_RANGE = (768, 1151)
P20K_DEV_REMAINDER_FRAME_RANGE = (1152, 1659)
# (d7) S2-ii build-frames declaration: counts/build frames hold TRAIN
# 0..1659 only (P20H input = 1.5M TRAIN counts); DEV holds VAL 1660..2043.
FROZEN_BUILD_FRAME_RANGE = (0, 1659)
FROZEN_MANIFEST_TRAIN_FRAMES = 1660
FROZEN_MANIFEST_TRAIN_PAIRS = 424960
FROZEN_MANIFEST_VAL_FRAMES = 553
FROZEN_MANIFEST_VAL_PAIRS = 141568
FROZEN_MANIFEST_HOLD_FRAMES = 554
FROZEN_MANIFEST_HOLD_PAIRS = 141824

# (d5) new P20M tag domain.
FROZEN_TAG_MASTER = 2026092280
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = 64
SEED_PREFIX = "nbpolar-p20m-raw-prior-val-1p5m-seed"

OPERATIONAL_PROVENANCE = p20l.OPERATIONAL_PROVENANCE
ORACLE_PROVENANCE = p20l.ORACLE_PROVENANCE

# Stage-A derivation seeds (frozen): 4 streams x 4 blocks = 16 synthetic
# TRAIN blocks model-sampled from the corrected prior (Stage A only).
FROZEN_DERIVATION_SEEDS = (2026092291, 2026092292, 2026092293, 2026092294)
FROZEN_TRAIN_BLOCKS_PER_SEED = 4
FROZEN_TRAIN_BLOCKS_TOTAL = 16
FROZEN_TRAIN_GENIE_CALLS = 32  # L1+L2 per synthetic block, Stage A only
FROZEN_ORDER_PROGRAM_PIN = (
    "accepted P13/P16 L1+L2-genie procedure: "
    "empirical_channel.sample_full_block(rng, p_b, f_raw, 32, 32, N) + "
    "transform.polar_transform(high, field, alpha=2) + "
    "transform.polar_transform(low, field, alpha=2) + "
    "prior.build_p1_metrics(bob[None,:], p1)[0] + "
    "prior.probs_to_symbol_metric(probs, provenance=PRIOR_ONLY) + "
    "prior.gather_p2_metrics(bob[None,:], high[None,:], p2)[0] + "
    "prior.probs_to_symbol_metric(probs, provenance=ORACLE_CONDITIONED) + "
    "empirical_genie_scaling.block_genie_risks(l1_logp, u1, l2_logp, u2) "
    "pooled over 16 model-sampled TRAIN blocks + "
    "empirical_genie_scaling.select_empirical_split worst-first (e,h,index) "
    "exhaustive K1 enumeration with K2 = K_total - K1; "
    "per-stream np.random.default_rng(seed), sequential blocks, no global RNG; "
    "never a real frame, never DEV"
)

# Read-only worktree input for the §3 derivation (worktree-file read,
# never a protected counts open).
FROZEN_WORKTREE_PRIOR_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/"
    "per_session_calibration/calibrated_prior.npz"
)
FROZEN_WORKTREE_PRIOR_DIGEST = (
    "e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b"
)
# G0 lambda-prior identity (carried over read-only from P20H/P20L).
FROZEN_LAMBDA_PRIOR_PATH = p20l.FROZEN_PRIOR_PATH
FROZEN_LAMBDA_PRIOR_DIGEST = p20l.FROZEN_PRIOR_DIGEST
FROZEN_LAMBDA_H1 = p20l.FROZEN_CAL_H1
FROZEN_LAMBDA_H2 = p20l.FROZEN_CAL_H2
FROZEN_LAMBDA_H_TOTAL = p20l.FROZEN_CAL_H_TOTAL

# Stage-A products (frozen paths; digests pinned below at Stage A).
FROZEN_PRIOR_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_1p5m.npz"
)
FROZEN_ORDER_FILE_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/"
    "raw_prior_orders_1p5m.json"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20M-RAW-PRIOR-VAL-1P5M/raw_prior_val_1p5m"
)
FROZEN_CONSTRUCTION_PATH = p20l.FROZEN_CONSTRUCTION_PATH
FROZEN_CONSTRUCTION_DIGEST = p20l.FROZEN_CONSTRUCTION_DIGEST
FROZEN_OLD_L1_ORDER_DIGEST = p20l.FROZEN_OLD_L1_ORDER_DIGEST
FROZEN_DEV_PAIRS_PATH = p20l.FROZEN_DEV_PAIRS_PATH
FROZEN_DEV_PAIRS_SIZE = p20l.FROZEN_DEV_PAIRS_SIZE
FROZEN_DEV_PAIRS_SHA256 = p20l.FROZEN_DEV_PAIRS_SHA256
FROZEN_MANIFEST_PATH = p20l.FROZEN_MANIFEST_PATH
FROZEN_MANIFEST_SCHEMA = p20l.FROZEN_MANIFEST_SCHEMA

# Exact keys of the Stage-A corrected-prior artifact (no more, no fewer).
RAW_PRIOR_NPZ_KEYS = (
    "counts_ab",
    "f_raw",
    "p1",
    "p2",
    "p_b",
    "lambda_star",
    "floor_value",
    "h1",
    "h2",
    "h_total",
)

# ---- Stage-A pins (filled by the Stage-A derivation, 2026-09-19) ----
FROZEN_PRIOR_DIGEST = "372dcc1cedbace1e699f60787d10eb298bb4bb3290519d2e6b19964ecf7d46ac"
FROZEN_H1 = 0.02519949692375297
FROZEN_H2 = 0.8003665547495433
FROZEN_H_TOTAL = 0.8255660516732963
FROZEN_K_TOTAL = 7020
FROZEN_K1_G1 = 331
FROZEN_K2_G1 = 6689
FROZEN_ORDER_DIGEST = "a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638"
FROZEN_CONSTRUCTION_FLOOR_HITS = 1046140
FROZEN_CONSTRUCTION_FLOOR_HIT_RATE = 0.9976768493652344


def pins_frozen() -> dict:
    """Fail-closed pin-state check: every Stage-A pin must be filled."""
    pins = {
        "prior_digest": FROZEN_PRIOR_DIGEST,
        "h1": FROZEN_H1,
        "h2": FROZEN_H2,
        "h_total": FROZEN_H_TOTAL,
        "k_total": FROZEN_K_TOTAL,
        "k1_g1": FROZEN_K1_G1,
        "k2_g1": FROZEN_K2_G1,
        "order_digest": FROZEN_ORDER_DIGEST,
        "construction_floor_hits": FROZEN_CONSTRUCTION_FLOOR_HITS,
        "construction_floor_hit_rate": FROZEN_CONSTRUCTION_FLOOR_HIT_RATE,
    }
    missing = sorted(name for name, value in pins.items() if value is None)
    if missing:
        raise ValueError(
            "Stage-A freeze not yet applied: missing pins: " + ",".join(missing)
        )
    return pins


def pins_are_frozen() -> bool:
    """Non-raising pin-state probe (test seam for the pre/post-fill states)."""
    try:
        pins_frozen()
    except ValueError:
        return False
    return True


PLANNED_SC_CALLS = FROZEN_BLOCK_COUNT * (2 + 2 + 1)  # 15
PLANNED_TAG_INVOCATIONS = len(("G0_old_point_base", "G1_raw_prior_session_budget",
                               "G2_true_l1_diagnostic")) * FROZEN_BLOCK_COUNT  # 9
PLANNED_RECORDS = 9

COMPLETE_LABEL = "TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE"

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "corrected_prior_identity",
    "dev_split_manifest_identity",
    "dev_block_range_identity",
    "order_derivation_identity",
    "budget_literal_recomputed",
    "target_population_contract",
    "dev_population_exact",
    "blocks_exact_with_declared_remainder",
    "nine_records_exact",
    "genie_calls_exact",
    "sc_calls_exact",
    "tags_exact",
    "orders_valid_k_prefixes_within_registered_arms",
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

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
    "ulimit -v 2097152\n"
    "timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.raw_prior_val_1p5m "
    f"--prior {FROZEN_PRIOR_PATH} --source 1p5M --floor 1e-15 "
    "--n 32768 --k1 331 --k2 6689 "
    f"--construction {FROZEN_CONSTRUCTION_PATH} --construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
    f"--dev-pairs {FROZEN_DEV_PAIRS_PATH} "
    "--dev-frames 1660 2043 --block-frames 128 --remainder-frames 2044 2212 "
    "--tag-master 2026092280 --chunk-rows 512 --tag-bits 64 "
    f"--order-file {FROZEN_ORDER_FILE_PATH} --order-digest a9f18a9fdad37c2cdf6e540c11d7ffede9b260275a7eae6a3a40a21da11bc638 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)

OUTPUT_FILES = (
    "frozen_plan.json",
    "input_and_predecessor_identity.json",
    "per_block_arm_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)
ATTEMPT_CONSUMPTION_POINT = "first protected content open (DEV pairs parquet)"

# Process-level one-open guards: set at the first content load/open, never cleared.
_WORKTREE_CONTENT_OPENED = False
_WORKTREE_CONTENT_OPENS = 0
_RAW_PRIOR_CONTENT_LOADED = False
_LAMBDA_PRIOR_CONTENT_LOADED = False
_DEV_PARQUET_CONTENT_OPENED = False

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 600.0
EXTERNAL_TIMEOUT_S = 600
ULIMIT_VIRTUAL_KIB = 2097152


class RawPriorVal1p5mContractError(ValueError):
    """Pre-open population/formation failure: BLOCKED(<earliest gate>)."""


class RawPriorVal1p5mResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


def _gate_call(gate_name, fn, *args, **kwargs):
    """Run an accepted gate helper read-only, tagged with the P20M gate name."""
    try:
        return fn(*args, **kwargs)
    except (ValueError, FileNotFoundError) as exc:
        raise RawPriorVal1p5mContractError(f"BLOCKED({gate_name}): {exc}") from exc


# ---------------------------------------------------------------------------
# (d4) arms: three hardcoded specs, never CLI-tunable, never extensible.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ArmSpec:
    """One frozen P20M arm (never CLI-tunable, never extensible)."""

    name: str
    kind: str  # "operational" | "oracle_control"
    k1: int
    k2: int
    leakage_bits: int
    provenance: str
    prior_source: str  # "lambda" (G0 control) | "raw" (G1/G2 candidate)


def build_arm_table(*, k1_g1: int, k2_g1: int) -> tuple:
    """Build the three frozen arm specs from the Stage-A derived G1 point.

    Pure: G0 is the carried-over failing point (lambda prior, P16 orders,
    319/6492); G1 is the corrected-prior candidate at the derived (K1,K2);
    G2 is the true-L1 oracle at the candidate K2. Leakage follows the
    frozen 5K+64 rule per arm.
    """
    k1_g1 = int(k1_g1)
    k2_g1 = int(k2_g1)
    if k1_g1 < 0 or k2_g1 < 0:
        raise ValueError(f"derived G1 point must be non-negative, got {(k1_g1, k2_g1)}")
    g1_leakage = 5 * (k1_g1 + k2_g1) + 64
    g2_leakage = 5 * k2_g1 + 64
    return (
        ArmSpec("G0_old_point_base", "operational", FROZEN_K1_G0, FROZEN_K2_G0,
                FROZEN_LEAKAGE_G0, OPERATIONAL_PROVENANCE, "lambda"),
        ArmSpec("G1_raw_prior_session_budget", "operational", k1_g1, k2_g1,
                g1_leakage, OPERATIONAL_PROVENANCE, "raw"),
        ArmSpec("G2_true_l1_diagnostic", "oracle_control", 0, k2_g1,
                g2_leakage, ORACLE_PROVENANCE, "raw"),
    )


def frozen_arm_table() -> tuple:
    """Materialize the frozen arm table from the Stage-A pins (refuses if unfrozen)."""
    pins = pins_frozen()
    return build_arm_table(k1_g1=int(pins["k1_g1"]), k2_g1=int(pins["k2_g1"]))


FROZEN_ARM_NAMES = (
    "G0_old_point_base",
    "G1_raw_prior_session_budget",
    "G2_true_l1_diagnostic",
)
OPERATIONAL_ARM_NAMES = (
    "G0_old_point_base",
    "G1_raw_prior_session_budget",
)
ORACLE_ARM_NAME = "G2_true_l1_diagnostic"


def check_frozen_arm_table() -> dict:
    """Fail-closed pin of the three frozen arms and their design accounting.

    Pure code-level check (no I/O): arm names/order, the G0 control pins,
    the 5K+64 leakage arithmetic on the Stage-A derived G1 point, the
    oracle label and the 15 SC / 9 tag design totals. Any drift raises
    before any root exists.
    """
    arms = frozen_arm_table()
    if tuple(spec.name for spec in arms) != FROZEN_ARM_NAMES:
        raise ValueError(
            f"frozen arm order drifted: {tuple(spec.name for spec in arms)!r}"
        )
    g0, g1, g2 = arms
    if (g0.kind, g0.k1, g0.k2, g0.leakage_bits, g0.prior_source,
            g0.provenance) != ("operational", 319, 6492, 34119, "lambda",
                               OPERATIONAL_PROVENANCE):
        raise ValueError("frozen G0_old_point_base arm drifted from the carried-over point")
    pins = pins_frozen()
    if (g1.kind, g1.k1, g1.k2, g1.prior_source, g1.provenance) != (
            "operational", int(pins["k1_g1"]), int(pins["k2_g1"]), "raw",
            OPERATIONAL_PROVENANCE):
        raise ValueError("frozen G1 arm drifted from the Stage-A derived point")
    if int(g1.leakage_bits) != 5 * (int(g1.k1) + int(g1.k2)) + 64:
        raise ValueError("frozen G1 leakage != 5*(K1+K2)+64")
    if (g2.kind, g2.k1, g2.prior_source, g2.provenance) != (
            "oracle_control", 0, "raw", ORACLE_PROVENANCE):
        raise ValueError("frozen G2_true_l1_diagnostic arm drifted")
    if int(g2.k2) != int(g1.k2):
        raise ValueError("frozen G2 K2 != candidate K2 (must equal G1 K2)")
    if int(g2.leakage_bits) != 5 * int(g2.k2) + 64:
        raise ValueError("frozen G2 leakage != 5*K2+64")
    if int(g1.k1) + int(g1.k2) != int(pins["k_total"]):
        raise ValueError("frozen G1 K1+K2 != frozen K_total")
    if PLANNED_SC_CALLS != 15:
        raise ValueError(f"frozen design must plan 15 SC calls, got {PLANNED_SC_CALLS}")
    if PLANNED_TAG_INVOCATIONS != 9:
        raise ValueError(f"frozen design must plan 9 tags, got {PLANNED_TAG_INVOCATIONS}")
    cap_ratio = float(g1.leakage_bits / FROZEN_RAW_INPUT_BITS)
    if not cap_ratio < 0.5:
        raise ValueError("frozen G1 cap must sit well below raw input bits")
    return {
        "arms": [spec.name for spec in arms],
        "g0": {"k1": int(g0.k1), "k2": int(g0.k2),
               "leakage_bits": int(g0.leakage_bits)},
        "g1": {"k1": int(g1.k1), "k2": int(g1.k2),
               "leakage_bits": int(g1.leakage_bits)},
        "g2": {"k1": int(g2.k1), "k2": int(g2.k2),
               "leakage_bits": int(g2.leakage_bits)},
        "public_control_bits": int(FROZEN_PUBLIC_CONTROL_BITS),
        "planned_sc_calls": PLANNED_SC_CALLS,
        "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
        "g1_cap_vs_raw_ratio": cap_ratio,
    }


# ---------------------------------------------------------------------------
# Frozen CLI flag checks (Stage-B; all flags required, no production default).
# ---------------------------------------------------------------------------

def _check_floor(value) -> float:
    from . import holdout_microcheck as hm

    out = hm._check_floor(value)
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
    from . import operational_f13 as opf

    out = opf._check_n(value)
    if out != FROZEN_N:
        raise ValueError(f"frozen point requires n={FROZEN_N}, got {out}")
    return out


def _check_g1_k1(value) -> int:
    from . import operational_f13 as opf

    out = opf._as_int(value, "k1", minimum=0)
    pins = pins_frozen()
    if out != int(pins["k1_g1"]):
        raise ValueError(f"frozen point requires k1={int(pins['k1_g1'])}, got {out}")
    return out


def _check_g1_k2(value) -> int:
    from . import operational_f13 as opf

    out = opf._as_int(value, "k2", minimum=0)
    pins = pins_frozen()
    if out != int(pins["k2_g1"]):
        raise ValueError(f"frozen point requires k2={int(pins['k2_g1'])}, got {out}")
    return out


def _check_tag_master(value) -> int:
    from . import operational_f13 as opf

    out = opf._as_int(value, "tag_master", minimum=0)
    if out != FROZEN_TAG_MASTER:
        raise ValueError(f"frozen point requires tag-master={FROZEN_TAG_MASTER}, got {out}")
    return out


def _check_dev_frames(value) -> tuple:
    from . import operational_f13 as opf

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
    from . import operational_f13 as opf

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


def _check_order_digest(value) -> str:
    digest = str(value)
    if FROZEN_ORDER_DIGEST is None:
        raise ValueError("Stage-A freeze not yet applied: order digest pin is None")
    if digest != str(FROZEN_ORDER_DIGEST):
        raise ValueError("frozen point requires order-digest=<Stage-A frozen order-file sha256>")
    return digest


# ---------------------------------------------------------------------------
# (d1) corrected-prior derivation (Stage A): raw-count MLE + 1e-15 floor +
# column renormalize, no lambda anywhere.
# ---------------------------------------------------------------------------

def raw_prefloor_table(counts_ab) -> np.ndarray:
    """Raw-count MLE conditional ``[Alice,Bob]`` before the floor.

    ``f_raw[a,b] = counts_ab[a,b] / n_b[b]`` with zero columns falling back
    to ``p_global`` exactly. Pure; no lambda parameter exists anywhere.
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
    with np.errstate(divide="ignore", invalid="ignore"):
        out = mat / n_b[None, :]
    zero_cols = n_b == 0
    if zero_cols.any():
        out[:, zero_cols] = p_global[:, None]
    return np.ascontiguousarray(out)


def derive_raw_prior_arrays(counts_ab) -> dict:
    """Apply the frozen §3 raw rule to a ``[Alice,Bob]`` count matrix.

    Pure function (no I/O): raw-count MLE + ``1e-15`` floor + column
    renormalization, accepted ``derive_p1``/``derive_p2`` under
    ``A = 32*U1 + U2`` FULL_BOB_ONLY, and the floor-table entropy
    functionals (the quantities that drive SC) as the session literals.
    There is no lambda parameter: smoothing is absent by construction.
    """
    pre = raw_prefloor_table(counts_ab)
    mat = np.asarray(counts_ab, dtype=np.float64)
    n_b = mat.sum(axis=0)
    total = float(mat.sum())
    p_b = n_b / total
    floor = float(FROZEN_FLOOR)
    floor_hits = int(np.sum(pre < floor))
    f_raw = np.maximum(pre, floor)
    f_raw = f_raw / f_raw.sum(axis=0, keepdims=True)
    zero_columns = int(np.sum(n_b == 0))
    p1 = derive_p1(np.ascontiguousarray(f_raw))
    p2 = derive_p2(np.ascontiguousarray(f_raw))
    h1 = float(np.sum(p_b * entropy_bits(p1, axis=0)))
    h2 = float(np.sum(p_b[None, :] * p1 * entropy_bits(p2, axis=2)))
    column_dev = float(np.abs(f_raw.sum(axis=0) - 1.0).max())
    cells = int(pre.size)
    return {
        "f_raw": np.ascontiguousarray(f_raw),
        "p1": np.ascontiguousarray(p1),
        "p2": np.ascontiguousarray(p2),
        "p_b": np.ascontiguousarray(p_b),
        "column_totals": np.ascontiguousarray(n_b),
        "counts_total": int(round(total)),
        "h1": h1,
        "h2": h2,
        "h_total": h1 + h2,
        "floor_hits": floor_hits,
        "floor_hit_rate": float(floor_hits) / float(cells),
        "floor_cells": cells,
        "zero_columns": zero_columns,
        "column_dev": column_dev,
    }


def build_raw_prior_arrays(counts_ab) -> dict:
    """Corrected-prior arrays exactly as stored in ``raw_prior_1p5m.npz``."""
    cal = derive_raw_prior_arrays(counts_ab)
    mat = np.ascontiguousarray(np.asarray(counts_ab, dtype=np.float64))
    return {
        "counts_ab": mat,
        "f_raw": cal["f_raw"],
        "p1": cal["p1"],
        "p2": cal["p2"],
        "p_b": cal["p_b"],
        "lambda_star": np.asarray(0.0, dtype=np.float64),
        "floor_value": np.asarray(float(FROZEN_FLOOR), dtype=np.float64),
        "h1": np.asarray(float(cal["h1"]), dtype=np.float64),
        "h2": np.asarray(float(cal["h2"]), dtype=np.float64),
        "h_total": np.asarray(float(cal["h_total"]), dtype=np.float64),
    }


def load_worktree_counts_arrays(path, *, expected_digest: str) -> dict:
    """Load the §3 worktree npz read-only behind its digest pin.

    Checks the exact P20H key set, shapes, and the canonical digest
    against the frozen worktree pin; returns the arrays plus the
    recomputed digest. The single content open is recorded on the
    process-level no-reopen guard (worktree-file read, never a protected
    counts open).
    """
    global _WORKTREE_CONTENT_OPENED, _WORKTREE_CONTENT_OPENS
    if _WORKTREE_CONTENT_OPENED:
        raise RawPriorVal1p5mContractError(
            "reopen refused: the single worktree-npz read was already consumed"
        )
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"worktree prior npz not found: {p}")
    try:
        data = np.load(str(p), allow_pickle=False)
        with data:
            keys = set(str(k) for k in data.files)
            if keys != set(psc.PRIOR_NPZ_KEYS):
                raise RawPriorVal1p5mContractError(
                    f"worktree prior keys must be exactly {sorted(psc.PRIOR_NPZ_KEYS)}, "
                    f"got {sorted(keys)}"
                )
            arrays = {k: np.asarray(data[k]) for k in psc.PRIOR_NPZ_KEYS}
    except ValueError as exc:
        if "worktree prior keys" in str(exc):
            raise
        raise RawPriorVal1p5mContractError(f"worktree prior load failed ({exc})") from exc
    digest = psc.canonical_prior_digest(arrays)
    if digest != str(expected_digest):
        raise RawPriorVal1p5mContractError(
            "worktree prior digest != frozen pin (refusing before any derivation)"
        )
    counts = np.asarray(arrays["counts_ab"], dtype=np.float64)
    if counts.shape != (1024, 1024):
        raise RawPriorVal1p5mContractError(
            f"worktree counts_ab must be (1024,1024), got {counts.shape}"
        )
    _WORKTREE_CONTENT_OPENED = True
    _WORKTREE_CONTENT_OPENS += 1
    return {"arrays": arrays, "digest": digest, "counts_ab": counts}


def verify_corrected_prior(prior_arrays, *, expected_digest: str, expected_h1: float,
                           expected_h2: float, expected_total: float) -> dict:
    """Verify the Stage-A corrected prior (``corrected_prior_identity`` gate).

    Pure array check (no I/O): exact ``RAW_PRIOR_NPZ_KEYS`` key set,
    canonical digest equality with the frozen Stage-A pin, the
    lambda-0.0 / floor pins, recomputed H1/H2/TOTAL within 1e-12 of the
    frozen literals, the ``p_b`` cross-check against the ``counts_ab``
    column totals / total, and column normalization. Any mismatch raises
    before any SC call.
    """
    if set(prior_arrays) != set(RAW_PRIOR_NPZ_KEYS):
        raise ValueError(
            f"corrected prior keys must be exactly {sorted(RAW_PRIOR_NPZ_KEYS)}, "
            f"got {sorted(prior_arrays)}"
        )
    digest = psc.canonical_prior_digest(
        {k: np.asarray(prior_arrays[k]) for k in RAW_PRIOR_NPZ_KEYS}
    )
    failing = []
    if digest != str(expected_digest):
        failing.append("prior_digest_mismatch")
    if float(np.asarray(prior_arrays["lambda_star"])) != 0.0:
        failing.append("lambda_nonzero_smoothing_present")
    if float(np.asarray(prior_arrays["floor_value"])) != float(FROZEN_FLOOR):
        failing.append("floor_pin_mismatch")
    exp_h1, exp_h2, exp_total = float(expected_h1), float(expected_h2), float(expected_total)
    p_b = np.asarray(prior_arrays["p_b"], dtype=np.float64)
    p1 = np.asarray(prior_arrays["p1"], dtype=np.float64)
    p2 = np.asarray(prior_arrays["p2"], dtype=np.float64)
    f_raw = np.asarray(prior_arrays["f_raw"], dtype=np.float64)
    counts = np.asarray(prior_arrays["counts_ab"], dtype=np.float64)
    if counts.shape != (1024, 1024):
        raise ValueError(f"corrected prior counts_ab must be (1024,1024), got {counts.shape}")
    if f_raw.shape != (1024, 1024):
        raise ValueError(f"corrected prior f_raw must be (1024,1024), got {f_raw.shape}")
    if p1.shape != (32, 1024):
        raise ValueError(f"corrected prior p1 must be (32,1024), got {p1.shape}")
    if p2.shape != (32, 1024, 32):
        raise ValueError(f"corrected prior p2 must be (32,1024,32), got {p2.shape}")
    if p_b.shape != (1024,):
        raise ValueError(f"corrected prior p_b must be (1024,), got {p_b.shape}")
    try:
        h1 = float(np.sum(p_b * entropy_bits(p1, axis=0)))
        h2 = float(np.sum(p_b[None, :] * p1 * entropy_bits(p2, axis=2)))
    except (ValueError, IndexError) as exc:
        raise ValueError(f"corrected prior entropy recomputation failed: {exc}") from exc
    if abs(h1 - exp_h1) > NORM_TOL:
        failing.append("h1_matches_literal")
    if abs(h2 - exp_h2) > NORM_TOL:
        failing.append("h2_matches_literal")
    if abs((h1 + h2) - exp_total) > NORM_TOL:
        failing.append("total_matches_literal")
    # p_b cross-check: column totals / total recomputed from counts_ab.
    total = float(counts.sum())
    if total <= 0:
        failing.append("counts_total_positive")
        col_p_b = np.zeros_like(p_b)
    else:
        col_p_b = counts.sum(axis=0) / total
    if float(np.abs(col_p_b - p_b).max()) > NORM_TOL:
        failing.append("p_b_cross_check")
    if abs(float(p_b.sum()) - 1.0) > NORM_TOL:
        failing.append("p_b_normalized")
    if float(np.abs(f_raw.sum(axis=0) - 1.0).max()) > NORM_TOL:
        failing.append("f_raw_columns_normalized")
    if float(np.abs(p1.sum(axis=0) - 1.0).max()) > NORM_TOL:
        failing.append("conditional_columns_normalized")
    if float(np.abs(p2.sum(axis=2) - 1.0).max()) > NORM_TOL:
        failing.append("p2_last_axis_normalized")
    if failing:
        raise ValueError(
            "BLOCKED(corrected_prior_identity/target_population_contract): failing checks: "
            + ",".join(failing)
        )
    pre = raw_prefloor_table(counts)
    floor_hits = int(np.sum(pre < float(FROZEN_FLOOR)))
    return {
        "digest": digest,
        "f_raw": np.ascontiguousarray(f_raw),
        "p1": np.ascontiguousarray(p1),
        "p2": np.ascontiguousarray(p2),
        "p_b": np.ascontiguousarray(p_b),
        "counts": np.ascontiguousarray(counts),
        "h1": h1,
        "h2": h2,
        "h_total": h1 + h2,
        "counts_total": int(round(total)),
        "floor_hits": floor_hits,
        "floor_hit_rate": float(floor_hits) / float(pre.size),
        "zero_columns": int(np.sum(counts.sum(axis=0) == 0)),
        "failing": (),
        "passed": True,
    }


# ---------------------------------------------------------------------------
# (d2) session-derived budget: S2-(i) literal recomputation from same-run H.
# ---------------------------------------------------------------------------

def budget_literal_display(h_total: float, *, n: int = FROZEN_N,
                           target_f: float = FROZEN_TARGET_F) -> str:
    """Render the S2-(i) budget literal for the same-run session H."""
    k_total = budget_k_total(int(n), float(h_total), float(target_f))
    return (
        f"{float(target_f)}*{int(n)}*{float(h_total)!r}-64 over 5, floored, "
        f"clipped [0,{2 * int(n)}] = {int(k_total)}"
    )


def verify_budget_literal(h_total: float, k_total: int, *, n: int = FROZEN_N,
                          target_f: float = FROZEN_TARGET_F) -> dict:
    """Recompute K_total from the same-run session H; never a carried absolute."""
    expect = budget_k_total(int(n), float(h_total), float(target_f))
    if int(k_total) != int(expect):
        raise ValueError(
            f"BLOCKED(budget_literal_recomputed): K_total {int(k_total)} != "
            f"literal recomputation {int(expect)} from same-run H"
        )
    return {
        "k_total": int(expect),
        "h_total": float(h_total),
        "literal": budget_literal_display(h_total, n=n, target_f=target_f),
    }


# ---------------------------------------------------------------------------
# (d3) Stage-A frozen order file (L1+L2 worst-first orders, digest-gated).
# ---------------------------------------------------------------------------

def verify_stage_b_order_file_p20m(path, *, expected_digest: str,
                                   expected_prior_digest: str, expected_k1: int,
                                   expected_k2: int, expected_k_total: int) -> dict:
    """Verify the Stage-A frozen raw-prior order file (gate (g), order-freeze).

    Worktree-file read only (never a protected open): the file-bytes
    sha256 must equal the frozen ``--order-digest`` (which itself must
    equal the Stage-A pin), the document must carry the frozen
    protocol/kind with ``n == 32768``, BOTH L1 and L2 orders must be
    permutations of ``0..N-1``, the frozen prefix lengths must equal the
    derived (K1,K2), and the derivation provenance (corrected-prior
    digest + program pin + derivation seeds + 16 blocks) must replay
    exactly. Any mismatch raises before any SC call. Stage B performs
    zero sampling: this function loads a frozen file, never a sampler.
    """
    if FROZEN_ORDER_DIGEST is None:
        raise ValueError("Stage-A freeze not yet applied: order digest pin is None")
    if str(expected_digest) != str(FROZEN_ORDER_DIGEST):
        raise ValueError("order-file digest flag != frozen Stage-A order digest")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Stage-A frozen raw-prior order file not found: {p}")
    raw = p.read_bytes()
    file_digest = hashlib.sha256(raw).hexdigest()
    if file_digest != str(expected_digest):
        raise ValueError(
            "order-file bytes sha256 != frozen --order-digest "
            "(refusing before any SC call)"
        )
    try:
        doc = json.loads(raw.decode("utf-8"))
    except ValueError as exc:
        raise ValueError(f"order file unreadable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("protocol") != PROTOCOL_NAME:
        raise ValueError("order file protocol != frozen P20M protocol")
    if doc.get("kind") != "raw-prior-orders-file":
        raise ValueError("order file kind != raw-prior-orders-file")
    if int(doc.get("n", -1)) != FROZEN_N:
        raise ValueError("order file n != frozen N")
    try:
        l1_order = np.asarray(doc["l1_order"], dtype=np.int64).ravel()
        l2_order = np.asarray(doc["l2_order"], dtype=np.int64).ravel()
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"order file orders malformed: {exc}") from exc
    if l1_order.shape != (FROZEN_N,) or set(l1_order.tolist()) != set(range(FROZEN_N)):
        raise ValueError("order file l1_order is not a permutation of 0..N-1")
    if l2_order.shape != (FROZEN_N,) or set(l2_order.tolist()) != set(range(FROZEN_N)):
        raise ValueError("order file l2_order is not a permutation of 0..N-1")
    if int(doc.get("k_total", -1)) != int(expected_k_total):
        raise ValueError("order file k_total != derived K_total")
    if int(doc.get("k1", -1)) != int(expected_k1):
        raise ValueError("order file k1 != derived K1")
    if int(doc.get("k2", -1)) != int(expected_k2):
        raise ValueError("order file k2 != derived K2")
    derivation = doc.get("derivation")
    if not isinstance(derivation, dict):
        raise ValueError("order file derivation provenance missing")
    if str(derivation.get("prior_digest")) != str(expected_prior_digest):
        raise ValueError("order file derivation prior digest != frozen corrected-prior digest")
    if str(derivation.get("program")) != str(FROZEN_ORDER_PROGRAM_PIN):
        raise ValueError("order file derivation program pin != frozen program pin")
    if [int(s) for s in derivation.get("train_seeds", [])] != [
        int(s) for s in FROZEN_DERIVATION_SEEDS
    ]:
        raise ValueError("order file derivation TRAIN seeds != frozen derivation seeds")
    if int(derivation.get("train_blocks_used", -1)) != int(FROZEN_TRAIN_BLOCKS_TOTAL):
        raise ValueError("order file derivation TRAIN block count != frozen 16")
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
        "train_seeds": [int(s) for s in FROZEN_DERIVATION_SEEDS],
        "derivation": dict(derivation),
        "verified": True,
    }


# ---------------------------------------------------------------------------
# (d5) P20M tag domain.
# ---------------------------------------------------------------------------

def raw_prior_val_1p5m_seed_bits(master: int, n: int, arm: str, block_index: int, *,
                                bit_length: int | None = None) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P20M domain).

    Rule: concatenate SHA-256 over
    ``"nbpolar-p20m-raw-prior-val-1p5m-seed:<master>:<n>:<arm>:
    <block_index>:<counter>"`` for ``counter = 0, 1, ...`` (ASCII decimal),
    unpack each digest MSB-first and truncate to ``bit_length`` (default
    ``10*n + 63``). The P20M prefix and arm tokens differ from ALL of
    P16/P17/P18/P19/P20B/P20C/P20E/P20F/P20G/P20H/P20I/P20J/P20K/P20L
    domains on purpose. Seed contents are public control and are never
    persisted; only the bit length is recorded.
    """
    from . import operational_f13 as opf

    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P20M seed domain: {arm!r}")
    index = opf._as_int(block_index, "block_index", minimum=0)
    length = seed_bits_for(n) if bit_length is None else opf._as_int(
        bit_length, "bit_length", minimum=1)
    prefix = f"{SEED_PREFIX}:{master_seed}:{int(n)}:{arm}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < length:
        buf.extend(hashlib.sha256(f"{prefix}:{int(index)}:{counter}".encode("ascii")).digest())
        counter += 1
    bits = np.unpackbits(np.frombuffer(bytes(buf), dtype=np.uint8), bitorder="big")
    return bits[:length].astype(np.uint8)


# ---------------------------------------------------------------------------
# (d7) DEV/build-frames disjointness declaration (S2-ii).
# ---------------------------------------------------------------------------

def verify_build_dev_disjointness() -> dict:
    """Pin the S2-ii disjointness declaration with the frozen frame sets.

    Pure code-level check (no I/O): counts/build frames hold TRAIN
    ``0..1659`` only; DEV holds VAL ``1660..2043``; the sets are disjoint
    by split identity. Any drift raises before any protected content open.
    """
    build_first, build_last = FROZEN_BUILD_FRAME_RANGE
    dev_first, dev_last = FROZEN_DEV_FRAME_RANGE
    if (build_first, build_last) != (0, 1659):
        raise ValueError("build-frames declaration drifted from TRAIN 0..1659")
    if (dev_first, dev_last) != (1660, 2043):
        raise ValueError("DEV declaration drifted from VAL 1660..2043")
    if not (build_last < dev_first or dev_last < build_first):
        raise ValueError("DEV/build-frames disjointness violated")
    return {
        "build_frames": [int(build_first), int(build_last)],
        "dev_frames": [int(dev_first), int(dev_last)],
        "disjoint": True,
    }


# ---------------------------------------------------------------------------
# Stage-A derivation: corrected prior + session-derived point + order file.
# Read-only worktree input, zero protected opens, zero DEV contact.
# ---------------------------------------------------------------------------

def sample_synthetic_train_blocks(p_b, f_raw, p1, p2, *, seeds, blocks_per_seed: int,
                                  n: int) -> dict:
    """Model-sample synthetic TRAIN blocks and pool L1+L2 genie risks.

    Accepted P13/P16 TRAIN procedure read-only: per-stream
    ``np.random.default_rng(seed)`` with sequential blocks and no global
    RNG; ``sample_full_block`` + polar transforms + PRIOR_ONLY L1 /
    ORACLE_CONDITIONED L2 metrics + ``block_genie_risks`` through the
    registered choke point. Never a real frame, never DEV. Returns the
    pooled mean risk vectors, the calls counter (``genie`` only) and the
    provenance-violation count (must be 0).
    """
    from .prior import build_p1_metrics, gather_p2_metrics, probs_to_symbol_metric

    seeds = [int(s) for s in seeds]
    blocks_per_seed = int(blocks_per_seed)
    n = int(n)
    if not seeds or blocks_per_seed < 1:
        raise ValueError("derivation requires non-empty seeds and >= 1 block per seed")
    field = make_gf32()
    calls: dict = {}
    provenance_violations = 0
    acc_e1 = np.zeros(n, dtype=np.float64)
    acc_h1 = np.zeros(n, dtype=np.float64)
    acc_e2 = np.zeros(n, dtype=np.float64)
    acc_h2 = np.zeros(n, dtype=np.float64)
    used = 0
    impossible = 0
    blocks_done = 0
    for seed in seeds:
        rng = np.random.default_rng(int(seed))
        for _ in range(blocks_per_seed):
            bob, _a_full, high, low = sample_full_block(
                rng, np.asarray(p_b), np.asarray(f_raw), Q, Q, n
            )
            u1 = polar_transform(high, field=field, alpha=ALPHA)
            u2 = polar_transform(low, field=field, alpha=ALPHA)
            l1_metric = probs_to_symbol_metric(
                build_p1_metrics(bob[None, :], np.asarray(p1))[0],
                provenance=Provenance.PRIOR_ONLY,
            )
            if l1_metric.provenance != Provenance.PRIOR_ONLY:
                provenance_violations += 1
            l2_metric = probs_to_symbol_metric(
                gather_p2_metrics(bob[None, :], high[None, :], np.asarray(p2))[0],
                provenance=Provenance.ORACLE_CONDITIONED,
            )
            if l2_metric.provenance != Provenance.ORACLE_CONDITIONED:
                provenance_violations += 1
            try:
                risks = block_genie_risks(
                    l1_metric.logp, u1, l2_metric.logp, u2,
                    field=field, calls=calls,
                )
            except Exception:
                impossible += 1
                continue
            acc_e1 += risks["e1"]
            acc_h1 += risks["h1"]
            acc_e2 += risks["e2"]
            acc_h2 += risks["h2"]
            used += 1
            blocks_done += 1
    if used < 1:
        raise ValueError("derivation sampling used zero blocks")
    return {
        "e1_mean": acc_e1 / used,
        "h1_mean": acc_h1 / used,
        "e2_mean": acc_e2 / used,
        "h2_mean": acc_h2 / used,
        "blocks_attempted": len(seeds) * blocks_per_seed,
        "blocks_used": used,
        "blocks_impossible": impossible,
        "calls": dict(calls),
        "provenance_violations": int(provenance_violations),
    }


def run_derive_stage_a(*, worktree_prior_path=FROZEN_WORKTREE_PRIOR_PATH,
                       expected_worktree_digest: str = FROZEN_WORKTREE_PRIOR_DIGEST,
                       out_prior_path=FROZEN_PRIOR_PATH,
                       out_orders_path=FROZEN_ORDER_FILE_PATH,
                       expected_counts_total: int = FROZEN_MANIFEST_TRAIN_PAIRS,
                       n: int = FROZEN_N,
                       seeds=FROZEN_DERIVATION_SEEDS,
                       blocks_per_seed: int = FROZEN_TRAIN_BLOCKS_PER_SEED) -> dict:
    """Execute the frozen Stage-A derivation once; write the two products.

    The single read-only worktree-npz read (digest-reverified first) feeds
    the §3 raw rule; the products fail if present. Zero protected opens:
    no V25 counts NPZ, no DEV/VAL/HOLD parquet, no 1M/2M contact, zero
    decoder execution. Model sampling runs here (Stage A) only.
    """
    out_prior = Path(out_prior_path)
    out_orders = Path(out_orders_path)
    if out_prior.exists():
        raise FileExistsError(f"refusing to overwrite existing raw prior: {out_prior}")
    if out_orders.exists():
        raise FileExistsError(f"refusing to overwrite existing order file: {out_orders}")
    seeds = [int(s) for s in seeds]
    if seeds != [int(s) for s in FROZEN_DERIVATION_SEEDS]:
        raise ValueError(
            f"derivation requires the frozen seeds {list(FROZEN_DERIVATION_SEEDS)}, "
            f"got {seeds}"
        )
    if int(blocks_per_seed) != int(FROZEN_TRAIN_BLOCKS_PER_SEED):
        raise ValueError(
            f"derivation requires blocks_per_seed={int(FROZEN_TRAIN_BLOCKS_PER_SEED)}, "
            f"got {int(blocks_per_seed)}"
        )
    if int(n) <= 0 or int(n) & (int(n) - 1):
        raise ValueError(f"derivation requires a positive power-of-two n, got {n}")
    start = time.perf_counter()
    # The one read-only worktree open (digest-reverified; no-reopen guarded).
    worktree = load_worktree_counts_arrays(
        worktree_prior_path, expected_digest=str(expected_worktree_digest)
    )
    counts_ab = worktree["counts_ab"]
    # §3 raw rule (no lambda anywhere).
    cal = derive_raw_prior_arrays(counts_ab)
    if int(cal["counts_total"]) != int(expected_counts_total):
        raise ValueError(
            f"counts total {int(cal['counts_total'])} != manifest TRAIN pairs "
            f"{int(expected_counts_total)}"
        )
    arrays = build_raw_prior_arrays(counts_ab)
    prior_digest = psc.canonical_prior_digest(arrays)
    h1, h2, h_total = float(cal["h1"]), float(cal["h2"]), float(cal["h_total"])
    # S2-(i) budget literal recomputed from the same-run session H.
    budget = verify_budget_literal(h_total, budget_k_total(int(n), h_total, 1.3), n=int(n))
    k_total = int(budget["k_total"])
    # 16 synthetic TRAIN blocks under the frozen derivation seeds.
    sampled = sample_synthetic_train_blocks(
        cal["p_b"], cal["f_raw"], cal["p1"], cal["p2"],
        seeds=seeds, blocks_per_seed=int(blocks_per_seed), n=int(n),
    )
    if int(sampled["calls"].get("genie", 0)) != 2 * int(sampled["blocks_used"]):
        raise ValueError("derivation genie-call accounting != 2 per used block")
    if int(sampled["provenance_violations"]) != 0:
        raise ValueError("derivation provenance violations != 0")
    split = select_empirical_split(
        int(n), sampled["e1_mean"], sampled["h1_mean"],
        sampled["e2_mean"], sampled["h2_mean"], k_total,
    )
    k1, k2 = int(split["k1"]), int(split["k2"])
    l1_order = np.asarray(split["l1_order"], dtype=np.int64)
    l2_order = np.asarray(split["l2_order"], dtype=np.int64)
    out_prior.parent.mkdir(parents=True, exist_ok=True)
    with open(out_prior, "wb") as fh:
        np.savez(
            fh,
            counts_ab=arrays["counts_ab"],
            f_raw=arrays["f_raw"],
            p1=arrays["p1"],
            p2=arrays["p2"],
            p_b=arrays["p_b"],
            lambda_star=arrays["lambda_star"],
            floor_value=arrays["floor_value"],
            h1=arrays["h1"],
            h2=arrays["h2"],
            h_total=arrays["h_total"],
        )
    order_doc = {
        "protocol": PROTOCOL_NAME,
        "kind": "raw-prior-orders-file",
        "n": int(n),
        "k_total": k_total,
        "k1": k1,
        "k2": k2,
        "l1_order": [int(v) for v in l1_order.tolist()],
        "l2_order": [int(v) for v in l2_order.tolist()],
        "derivation": {
            "program": FROZEN_ORDER_PROGRAM_PIN,
            "prior_path": str(out_prior),
            "prior_digest": prior_digest,
            "train_seeds": [int(s) for s in seeds],
            "train_blocks_per_seed": int(blocks_per_seed),
            "train_blocks_attempted": int(sampled["blocks_attempted"]),
            "train_blocks_used": int(sampled["blocks_used"]),
            "train_impossible": int(sampled["blocks_impossible"]),
            "train_genie_calls": int(sampled["calls"].get("genie", 0)),
            "provenance_violations": int(sampled["provenance_violations"]),
            "budget_literal": budget["literal"],
            "counts_total": int(cal["counts_total"]),
            "floor_hits": int(cal["floor_hits"]),
            "floor_hit_rate": float(cal["floor_hit_rate"]),
            "zero_columns": int(cal["zero_columns"]),
            "train_residual": float(split["residual"]),
        },
    }
    out_orders.write_text(json.dumps(order_doc, sort_keys=True) + "\n", encoding="utf-8")
    order_digest = hashlib.sha256(out_orders.read_bytes()).hexdigest()
    g1_leakage = 5 * (k1 + k2) + 64
    g2_leakage = 5 * k2 + 64
    return {
        "prior_path": str(out_prior),
        "prior_digest": prior_digest,
        "h1": h1,
        "h2": h2,
        "h_total": h_total,
        "budget_literal": budget["literal"],
        "k_total": k_total,
        "k1": k1,
        "k2": k2,
        "g0_leakage_bits": int(FROZEN_LEAKAGE_G0),
        "g1_leakage_bits": int(g1_leakage),
        "g2_leakage_bits": int(g2_leakage),
        "public_control_bits": int(FROZEN_PUBLIC_CONTROL_BITS),
        "order_path": str(out_orders),
        "order_digest": order_digest,
        "counts_total": int(cal["counts_total"]),
        "floor_hits": int(cal["floor_hits"]),
        "floor_hit_rate": float(cal["floor_hit_rate"]),
        "zero_columns": int(cal["zero_columns"]),
        "train_blocks_used": int(sampled["blocks_used"]),
        "train_genie_calls": int(sampled["calls"].get("genie", 0)),
        "train_residual": float(split["residual"]),
        "derivation_seeds": [int(s) for s in seeds],
        "worktree_digest": str(worktree["digest"]),
        "worktree_content_opens": int(_WORKTREE_CONTENT_OPENS),
        "wall_s": round(float(time.perf_counter() - start), 6),
    }


# ---------------------------------------------------------------------------
# Stage-B records (P20M schema: operating-point fields + floor-hit fields).
# ---------------------------------------------------------------------------

def _block_view(block, field) -> dict:
    """Per-block truth views shared by the three arms (computed once)."""
    high = np.asarray(block["high"], dtype=np.int64)
    low = np.asarray(block["low"], dtype=np.int64)
    labels = np.asarray(block["labels"], dtype=np.int64)
    return {
        "bob": np.asarray(block["bob"], dtype=np.int64),
        "high": high,
        "low": low,
        "labels": labels,
        "u1": polar_transform(high, field=field, alpha=ALPHA),
        "u2": polar_transform(low, field=field, alpha=ALPHA),
        "labels_bits": labels_to_bits(labels),
    }


def _dev_block_scoring(block, p1_table, p2_table) -> dict:
    """Descriptive per-block scalars under one arm's prior tables."""
    nll = holdout_nll_bits(block["bob"], block["high"], block["low"], p1_table, p2_table)
    ser = raw_symbol_error_rate(block["labels"], block["bob"])
    return {
        "raw_ser": float(ser),
        "l1_nll_bits": float(nll["l1_nll_bits"]),
        "l2_nll_bits": float(nll["l2_nll_bits"]),
        "total_nll_bits": float(nll["total_nll_bits"]),
        "total_nll_bits_per_pair": float(nll["total_nll_bits_per_pair"]),
    }


def _scoring_absent() -> dict:
    return {
        "raw_ser": None,
        "l1_nll_bits": None,
        "l2_nll_bits": None,
        "total_nll_bits": None,
        "total_nll_bits_per_pair": None,
    }


def _l1_order_digest_for_arm(spec, *, order_digest: str) -> str | None:
    if spec.name == "G0_old_point_base":
        return str(FROZEN_OLD_L1_ORDER_DIGEST)
    if spec.name == "G1_raw_prior_session_budget":
        return str(order_digest)
    return None


def _base_record_fields(*, spec, arm_index, block, scoring, oracle, k_total: int,
                        budget_literal: str, order_digest: str) -> dict:
    total_nll = scoring.get("total_nll_bits")
    return {
        "protocol": PROTOCOL_NAME,
        "arm": spec.name,
        "arm_index": int(arm_index),
        "arm_kind": spec.kind,
        "arm_provenance": spec.provenance,
        "prior_source": spec.prior_source,
        "block_index": int(block["block_index"]),
        "frame_start": int(block["frame_start"]),
        "frame_end": int(block["frame_end"]),
        "frame_count": FROZEN_BLOCK_FRAMES,
        "k1": int(spec.k1),
        "k2": int(spec.k2),
        "k_total": int(k_total),
        "budget_literal": str(budget_literal),
        "l1_order_digest": _l1_order_digest_for_arm(spec, order_digest=order_digest),
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


def _selected_diagnostics(*, high_sel, low_sel, view, counts_arr, p1, p2, n: int) -> dict:
    diag = {
        "raw_zero_count_hits": None,
        "floor_hits_1e15": None,
        "floor_hit_log_loss_bits": None,
        "floor_hit_rate": None,
        "l2_nll_candidate_H_bits": None,
        "l2_nll_true_H_bits": None,
        "selected_total_nll_bits": None,
    }
    if high_sel is None or low_sel is None:
        return diag
    try:
        hits = raw_floor_diagnostics(
            view["bob"], high_sel, low_sel, counts_arr, p1, p2)
    except ValueError:
        hits = {"raw_zero_count_hits": None, "floor_hits_1e15": None,
                "floor_hit_log_loss_bits": None}
    diag.update(hits)
    floor_hits = hits.get("floor_hits_1e15")
    diag["floor_hit_rate"] = (
        float(floor_hits) / float(2 * int(n)) if floor_hits is not None else None
    )
    cand = candidate_nll_bits(view["bob"], high_sel, low_sel, p1, p2)
    diag["l2_nll_candidate_H_bits"] = float(cand["l2_nll_bits"])
    diag["selected_total_nll_bits"] = float(cand["total_nll_bits"])
    true_cond = candidate_nll_bits(view["bob"], view["high"], low_sel, p1, p2)
    diag["l2_nll_true_H_bits"] = float(true_cond["l2_nll_bits"])
    return diag


def _operational_record(result, *, spec, arm_index, block, scoring, resources,
                        k_total, budget_literal, order_digest, counts_arr, p1, p2,
                        n, view, diag=None, error=None) -> dict:
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=False,
        k_total=k_total, budget_literal=budget_literal, order_digest=order_digest)
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
        "sc_calls_this_record": int(1 if result.l1_executed or result.l1_decode_failed else 0)
        + int(1 if result.l2_invoked else 0),
        "actual_key_dependent_bits": int(result.key_dependent_bits),
        "actual_public_control_bits": int(result.public_control_bits),
        "nonfinite": bool(result.nonfinite),
        "truth_leak_violation": bool(result.truth_leak_violation),
        "error": error,
        "wall_s": round(float(result.wall_s), 6),
        "resources": dict(resources),
    })
    diag = diag if diag is not None else _selected_diagnostics(
        high_sel=result.high_hat, low_sel=result.low_hat, view=view,
        counts_arr=counts_arr, p1=p1, p2=p2, n=n)
    record.update({
        "raw_zero_count_hits": diag.get("raw_zero_count_hits"),
        "floor_hits_1e15": diag.get("floor_hits_1e15"),
        "floor_hit_log_loss_bits": diag.get("floor_hit_log_loss_bits"),
        "floor_hit_rate": diag.get("floor_hit_rate"),
        "l2_nll_candidate_H_bits": diag.get("l2_nll_candidate_H_bits"),
        "l2_nll_true_H_bits": diag.get("l2_nll_true_H_bits"),
        "selected_total_nll_bits": diag.get("selected_total_nll_bits"),
    })
    record.update({
        "key_bit_delta_vs_G0": int(spec.leakage_bits) - int(FROZEN_LEAKAGE_G0),
    })
    return record


def _control_record(result, *, spec, arm_index, block, scoring, resources,
                    k_total, budget_literal, order_digest, counts_arr, p1, p2,
                    n, view, diag=None, error=None) -> dict:
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=True,
        k_total=k_total, budget_literal=budget_literal, order_digest=order_digest)
    first_error = first_error_coordinate(
        None, result.low_hat, None, block["low"])
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
    diag = diag if diag is not None else _selected_diagnostics(
        high_sel=view["high"] if result.low_hat is not None else None,
        low_sel=result.low_hat, view=view,
        counts_arr=counts_arr, p1=p1, p2=p2, n=n)
    record.update({
        "raw_zero_count_hits": diag.get("raw_zero_count_hits"),
        "floor_hits_1e15": diag.get("floor_hits_1e15"),
        "floor_hit_log_loss_bits": diag.get("floor_hit_log_loss_bits"),
        "floor_hit_rate": diag.get("floor_hit_rate"),
        "l2_nll_candidate_H_bits": diag.get("l2_nll_candidate_H_bits"),
        "l2_nll_true_H_bits": diag.get("l2_nll_true_H_bits"),
        "selected_total_nll_bits": diag.get("selected_total_nll_bits"),
    })
    record.update({"key_bit_delta_vs_G0": None})
    return record


def _abort_record(*, spec, arm_index, block, k_total, budget_literal,
                  order_digest, resources) -> dict:
    return {
        "protocol": PROTOCOL_NAME,
        "arm": spec.name,
        "arm_index": int(arm_index),
        "arm_kind": spec.kind,
        "arm_provenance": spec.provenance,
        "prior_source": spec.prior_source,
        "block_index": int(block["block_index"]),
        "frame_start": int(block["frame_start"]),
        "frame_end": int(block["frame_end"]),
        "frame_count": FROZEN_BLOCK_FRAMES,
        "k1": int(spec.k1),
        "k2": int(spec.k2),
        "k_total": int(k_total),
        "budget_literal": str(budget_literal),
        "l1_order_digest": _l1_order_digest_for_arm(spec, order_digest=order_digest),
        "full_block_key_dependent_bits": int(spec.leakage_bits),
        "public_control_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS),
        "disclosure_ce_ratio": None,
        "oracle_truth_use": bool(spec.kind == "oracle_control"),
        "oracle_control": bool(spec.kind == "oracle_control"),
        "deployable": bool(spec.kind != "oracle_control"),
        "outcome": "resource_abort",
        "exact": False,
        "key_bit_delta_vs_G0": None,
        "floor_hit_rate": None,
        "sc_calls_this_record": 0,
        "actual_key_dependent_bits": 0,
        "actual_public_control_bits": 0,
        "nonfinite": False,
        "truth_leak_violation": False,
        "error": "resource_abort",
        "resources": dict(resources),
    }


def _partition(records):
    operational = [r for r in records if r.get("arm_kind") == "operational"]
    oracle = [r for r in records if r.get("arm_kind") == "oracle_control"]
    return operational, oracle


def oracle_isolation_ok(records, *, final: bool) -> bool:
    """The oracle arm carries ORACLE provenance and never enters operational aggregates."""
    for record in records:
        if record.get("arm") == ORACLE_ARM_NAME:
            if record.get("arm_provenance") != ORACLE_PROVENANCE:
                return False
            if record.get("deployable") is not False:
                return False
            if record.get("oracle_control") is not True:
                return False
        elif record.get("arm") in OPERATIONAL_ARM_NAMES:
            if record.get("arm_provenance") != OPERATIONAL_PROVENANCE:
                return False
            if record.get("oracle_control") is not False:
                return False
        else:
            return False
    if final and len(records) != PLANNED_RECORDS:
        return False
    return True


def recovery_diagnostics(records) -> dict:
    """Descriptive G1-vs-G0 restoration reading (never a threshold)."""
    by_block: dict = {}
    for record in records:
        if record.get("arm_kind") != "operational":
            continue
        by_block.setdefault(int(record["block_index"]), {})[record["arm"]] = record
    restored = maintain = g0_exact_blocks = g1_exact_blocks = 0
    moves = []
    for block_index in sorted(by_block):
        cell = by_block[block_index]
        g0 = cell.get("G0_old_point_base")
        g1 = cell.get("G1_raw_prior_session_budget")
        if g0 is None or g1 is None:
            continue
        g0_exact = bool(g0.get("exact"))
        g1_exact = bool(g1.get("exact"))
        g0_exact_blocks += int(g0_exact)
        g1_exact_blocks += int(g1_exact)
        if not g0_exact and g1_exact:
            restored += 1
        if g0_exact and g1_exact:
            maintain += 1
        moves.append({
            "block_index": block_index,
            "g0_first_error_layer": g0.get("first_error_layer"),
            "g1_first_error_layer": g1.get("first_error_layer"),
        })
    return {
        "g1_restored_count": int(restored),
        "g1_maintain_count": int(maintain),
        "g0_exact_blocks": int(g0_exact_blocks),
        "g1_exact_blocks": int(g1_exact_blocks),
        "first_error_moves": moves,
    }


def _arm_aggregate(records, spec) -> dict:
    arm_records = [r for r in records if r.get("arm") == spec.name]
    outcomes: dict = {}
    for record in arm_records:
        outcomes[str(record.get("outcome"))] = outcomes.get(str(record.get("outcome")), 0) + 1
    rates = [r.get("floor_hit_rate") for r in arm_records
             if r.get("floor_hit_rate") is not None]
    return {
        "arm": spec.name,
        "records": len(arm_records),
        "exact_count": sum(1 for r in arm_records if r.get("exact") is True),
        "outcomes": outcomes,
        "floor_hit_rate_mean": (float(sum(rates) / len(rates)) if rates else None),
    }


def build_aggregates(records) -> dict:
    """Descriptive aggregates: oracle excluded from every operational aggregate."""
    operational, oracle = _partition(records)
    arms = frozen_arm_table() if pins_are_frozen() else ()
    arm_table = {spec.name: _arm_aggregate(records, spec) for spec in arms} if arms else {}
    op_outcomes: dict = {}
    for record in operational:
        op_outcomes[str(record.get("outcome"))] = op_outcomes.get(
            str(record.get("outcome")), 0) + 1
    recovery = recovery_diagnostics(records)
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
        "recovery": recovery,
        "arms": arm_table,
        "undetected_count": sum(1 for r in records if r.get("outcome") == "undetected"),
        "nonfinite_count": sum(1 for r in records if r.get("nonfinite") is True),
    }


def raw_prior_val_1p5m_block_events(n: int, spec, block_index: int, frame_start: int,
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


def raw_prior_val_1p5m_recount_events(events) -> dict:
    """Independent key/public/tag recount from the event stream."""
    key_bits = sum(int(e.get("key_dependent_bits", 0)) for e in events
                   if e.get("event_type") == "disclosed_block")
    public_bits = sum(int(e.get("public_control_bits", 0)) for e in events
                      if e.get("event_type") == "verification_tag")
    tags = sum(1 for e in events if e.get("event_type") == "verification_tag")
    return {
        "key_dependent_bits": int(key_bits),
        "public_control_bits": int(public_bits),
        "tag_invocations": int(tags),
    }


# ---------------------------------------------------------------------------
# Stage-B integrity gates (frozen §9 order; all true or BLOCKED).
# ---------------------------------------------------------------------------

def _stat_record(path) -> dict:
    if path is None:
        return {"path": None, "size_bytes": None, "mtime_ns": None}
    st = Path(path).stat()
    return {"path": str(path), "size_bytes": int(st.st_size), "mtime_ns": int(st.st_mtime_ns)}


def _integrity_gates(*, n, k1, k2, k_total, arms, identity, manifest,
                     dev_source_pin, dev_pin, disjoint_pin, p16_l1_order,
                     p16_l2_order, raw_l1_order, raw_l2_order, order_pin,
                     formation, records, events, calls, incremental, accounting,
                     provenance_violations, cap, wall_s, resource_stop,
                     raw_verified, lambda_verified, budget, construction_floor_hits,
                     prior_stat_before, prior_stat_after, lambda_stat_before,
                     lambda_stat_after, dev_stat_before, dev_stat_after,
                     registered_paths, opened_paths, final: bool) -> dict:
    from . import operational_f13 as opf

    gates: dict = {}
    gates["predecessor_construction_identity"] = bool(
        identity is not None and manifest is not None)
    gates["corrected_prior_identity"] = bool(
        raw_verified is not None and bool(raw_verified.get("passed")))
    gates["dev_split_manifest_identity"] = bool(
        manifest is not None
        and int(manifest.get("train_pairs", -1)) == FROZEN_MANIFEST_TRAIN_PAIRS
        and int(manifest.get("val_pairs", -1)) == FROZEN_MANIFEST_VAL_PAIRS
        and int(manifest.get("hold_pairs", -1)) == FROZEN_MANIFEST_HOLD_PAIRS)
    gates["dev_block_range_identity"] = bool(
        dev_pin is not None and dev_source_pin is not None
        and disjoint_pin is not None and bool(disjoint_pin.get("disjoint")))
    gates["order_derivation_identity"] = bool(
        order_pin is not None and bool(order_pin.get("verified")))
    gates["budget_literal_recomputed"] = bool(
        budget is not None and int(budget.get("k_total", -1)) == int(k_total)
        and int(k1) + int(k2) == int(k_total))
    gates["target_population_contract"] = bool(
        raw_verified is not None and bool(raw_verified.get("passed")))
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
    gates["nine_records_exact"] = (
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
        orders_ok = (
            l1_prefix_positions(p16_l1_order, FROZEN_K1_G0).shape == (FROZEN_K1_G0,)
            and l2_prefix_positions(p16_l2_order, FROZEN_K2_G0).shape == (FROZEN_K2_G0,)
            and l1_prefix_positions(raw_l1_order, k1).shape == (int(k1),)
            and l2_prefix_positions(raw_l2_order, k2).shape == (int(k2),)
            and int(k1) == int(arms[1].k1) and int(k2) == int(arms[1].k2)
            and int(arms[0].k1) == FROZEN_K1_G0 and int(arms[0].k2) == FROZEN_K2_G0
            and int(arms[2].k1) == 0 and int(arms[2].k2) == int(k2)
        )
    except (ValueError, IndexError, AttributeError):
        orders_ok = False
    gates["orders_valid_k_prefixes_within_registered_arms"] = bool(orders_ok)
    floor_fields_present = all("floor_hit_rate" in r for r in records)

    def _rate_ok(record) -> bool:
        # The floor-hit field is always present; its value is required
        # wherever a candidate was selected (decode_failed/resource_abort
        # records select no candidate, so None is the honest value there).
        value = record.get("floor_hit_rate")
        if value is not None:
            return float(value) >= 0.0
        return str(record.get("outcome")) in ("decode_failed", "resource_abort")

    gates["floor_hit_rate_reported"] = bool(
        (not final or len(records) == PLANNED_RECORDS)
        and floor_fields_present
        and all(_rate_ok(r) for r in records)
        and construction_floor_hits is not None)
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
        and int(accounting.get("raw_prior_content_loads", -1)) <= 1
        and int(accounting.get("lambda_prior_content_loads", -1)) <= 1
        and int(accounting.get("dev_content_opens", -1)) <= 1
        and accounting.get("reopen_attempted") is False)
    gates["input_stat_unchanged"] = bool(
        prior_stat_before == prior_stat_after
        and lambda_stat_before == lambda_stat_after
        and dev_stat_before == dev_stat_after)
    gates["no_unregistered_access"] = bool(
        set(opened_paths) <= set(registered_paths))
    rss_peak = opf._peak_rss_bytes()
    gates["resource_limits_met_and_no_abort"] = bool(
        resource_stop is None and float(wall_s) <= float(cap)
        and (rss_peak is None or int(rss_peak) <= RSS_LIMIT_BYTES)
        and all(r.get("outcome") != "resource_abort" for r in records))
    return gates


def raw_prior_val_1p5m_label(gates: dict) -> str:
    """Descriptive COMPLETE iff every integrity gate holds, else BLOCKED(first)."""
    failing = [g for g in INTEGRITY_GATE_ORDER if not gates.get(g, False)]
    if not failing:
        return COMPLETE_LABEL
    return f"BLOCKED({failing[0]})"


@dataclass(frozen=True, eq=False)
class RawPriorVal1p5mRun:
    """In-memory P20M run (also returned by the runner)."""

    summary: dict
    records: tuple
    gates: dict


def _stub_plan(*, out_path, source, floor, n, k1, k2, k_total, construction, digest,
               prior_path, prior_digest, lambda_prior_digest, dev_pairs, manifest_path,
               dev_frames, block_frames, remainder_frames, tag_master, chunk_rows,
               tag_bits, identity, manifest, dev_source_pin, dev_pin, disjoint_pin,
               order_file, order_digest, order_pin, budget) -> dict:
    out_path.mkdir(parents=True, exist_ok=False)
    plan = {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "analysis": PROTOCOL_NAME,
        "source": source,
        "floor": float(floor),
        "n": int(n),
        "k1": int(k1),
        "k2": int(k2),
        "k_total": int(k_total),
        "g0_k1": int(FROZEN_K1_G0),
        "g0_k2": int(FROZEN_K2_G0),
        "g0_leakage_bits": int(FROZEN_LEAKAGE_G0),
        "budget_literal": str(budget["literal"]),
        "operating_point_swap_rule": OPERATING_POINT_SWAP_RULE,
        "construction": str(construction),
        "construction_digest": str(digest),
        "prior_path": str(prior_path),
        "prior_digest": str(prior_digest),
        "lambda_prior_digest": str(lambda_prior_digest),
        "lambda_control": {"k1": int(FROZEN_K1_G0), "k2": int(FROZEN_K2_G0)},
        "dev_pairs": str(dev_pairs),
        "manifest_path": str(manifest_path),
        "dev_frames": [int(dev_frames[0]), int(dev_frames[1])],
        "block_frames": int(block_frames),
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "remainder_frames": [int(remainder_frames[0]), int(remainder_frames[1])],
        "build_frames": [int(FROZEN_BUILD_FRAME_RANGE[0]),
                         int(FROZEN_BUILD_FRAME_RANGE[1])],
        "dev_source": dict(dev_source_pin),
        "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
        "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
        "tag_master": int(tag_master),
        "tag_seed_domain": f"{SEED_PREFIX}:<master>:<n>:<arm>:<block_index>",
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "identity_n": int(identity.get("n", -1)) if isinstance(identity, dict) else None,
        "order_file": str(order_file),
        "order_digest": str(order_digest),
        "order_k1": int(order_pin.get("k1", -1)),
        "order_k2": int(order_pin.get("k2", -1)),
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
    }
    from . import operational_f13 as opf

    opf._write_json(out_path / "frozen_plan.json", plan)
    return plan


def _render_report(summary: dict) -> str:
    aggregates = summary.get("aggregates", {})
    recovery = aggregates.get("recovery", {})
    lines = [
        "# NB-Polar Phase 4-P20M raw-prior + session-budget operating-point swap",
        "",
        f"- protocol: `{summary.get('analysis')}` (mode `{summary.get('mode')}`)",
        f"- source: `{summary.get('source')}`; N={summary.get('n')}; "
        f"G1 K1={summary.get('k1')} K2={summary.get('k2')} "
        f"K_total={summary.get('k_total')}",
        f"- budget literal: `{summary.get('budget_literal')}`",
        f"- blocks: {summary.get('block_ranges')} "
        f"(remainder {summary.get('remainder_frames')} never used)",
        f"- outcome: `{summary.get('outcome_label')}`; "
        f"records {summary.get('records_completed')}/{summary.get('planned_records')}",
        f"- operational exact: "
        f"{aggregates.get('operational', {}).get('exact_count')} "
        f"(G0 {recovery.get('g0_exact_blocks')} / G1 {recovery.get('g1_exact_blocks')}); "
        f"g1_restored_count={recovery.get('g1_restored_count')} "
        f"(descriptive: G0 fail -> G1 exact); "
        f"maintain={recovery.get('g1_maintain_count')}",
        f"- oracle exact: {aggregates.get('oracle', {}).get('exact_count')} "
        f"(diagnostic only, never operational)",
        f"- undetected: {aggregates.get('undetected_count')}; "
        f"nonfinite: {aggregates.get('nonfinite_count')}",
        f"- SC calls: {summary.get('sc_calls')}/{summary.get('planned_sc_calls')} "
        f"(Stage-B sampling 0); tags: {summary.get('tag_invocations')}/"
        f"{summary.get('planned_tag_invocations')}",
        f"- key bits: {summary.get('key_dependent_bits')}; "
        f"public bits: {summary.get('public_control_bits')}; "
        f"recount mismatch: {summary.get('recount_mismatch')}",
        f"- integrity: {'ALL PASS' if summary.get('integrity_all_pass') else 'BLOCKED'} "
        f"{summary.get('failing_integrity_gates')}",
        "",
        "G2 is an oracle-labelled diagnostic control, never an operational "
        "protocol or deployable rate. The CE-normalized disclosure ratio is "
        "not qualification efficiency; undetected is never success.",
        "",
    ]
    return "\n".join(lines)


def run_raw_prior_val_1p5m(
    *,
    prior=None,
    lambda_prior=None,
    prior_path=FROZEN_PRIOR_PATH,
    lambda_prior_path=FROZEN_LAMBDA_PRIOR_PATH,
    source: str = FROZEN_SOURCE,
    floor=FROZEN_FLOOR,
    n: int = FROZEN_N,
    k1: int | None = None,
    k2: int | None = None,
    construction=FROZEN_CONSTRUCTION_PATH,
    construction_digest: str = FROZEN_CONSTRUCTION_DIGEST,
    dev_pairs=FROZEN_DEV_PAIRS_PATH,
    dev_table=None,
    manifest_path=FROZEN_MANIFEST_PATH,
    dev_frames=FROZEN_DEV_FRAME_RANGE,
    block_frames: int = FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
    tag_master: int = FROZEN_TAG_MASTER,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    tag_bits: int = FROZEN_TAG_BITS,
    order_file=FROZEN_ORDER_FILE_PATH,
    order_digest: str | None = None,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_raw=None,
    expected_lambda=None,
) -> RawPriorVal1p5mRun:
    """Execute the frozen P20M three-arm diagnostic once; write five files.

    ``prior`` / ``lambda_prior`` and ``dev_table`` plus ``expected_raw`` /
    ``expected_lambda`` are documented injected test seams; the frozen CLI
    passes only the frozen point, loads the Stage-A frozen corrected prior
    and the carried-over lambda prior read-only exactly once each, loads
    the Stage-A frozen order file read-only behind the order-digest gate,
    and reads the DEV parquet through its accepted loader exactly once.
    The V25 counts NPZ is never opened in Stage B. The operating-point
    swap is hardcoded (never CLI-tunable): G0 runs the lambda prior with
    the frozen P16 orders at 319/6492, G1 runs the corrected prior with
    the derived orders at the derived (K1,K2), G2 is the true-L1 oracle
    at the candidate K2. There is no derivation-seed flag and no sampling
    code path anywhere in Stage B.
    """
    from . import operational_f13 as opf

    global _RAW_PRIOR_CONTENT_LOADED, _LAMBDA_PRIOR_CONTENT_LOADED
    global _DEV_PARQUET_CONTENT_OPENED
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    pins = pins_frozen()
    floor = _check_floor(floor)
    source = _check_source(source)
    n = _check_n(n)
    if k1 is None or k2 is None:
        raise ValueError("frozen point requires --k1/--k2 equal to the Stage-A derived pins")
    k1 = _check_g1_k1(k1)
    k2 = _check_g1_k2(k2)
    k_total = int(k1) + int(k2)
    if k_total != int(pins["k_total"]):
        raise ValueError(
            f"frozen point requires k1+k2={int(pins['k_total'])}, got {k_total}")
    opf._check_chunk_contract(chunk_rows)
    opf._check_tag_bits(tag_bits)
    dev_frames = _check_dev_frames(dev_frames)
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise ValueError(
            f"frozen point requires block-frames={FROZEN_BLOCK_FRAMES}, got {block_frames}")
    remainder_frames = _check_remainder_frames(remainder_frames)
    tag_master = _check_tag_master(tag_master)
    if order_digest is None:
        raise ValueError("frozen point requires --order-digest equal to the Stage-A pin")
    order_digest = _check_order_digest(order_digest)
    arms = check_frozen_arm_table() and frozen_arm_table()

    # Gate order is frozen: predecessor identity, cross-file source-tag+digest
    # gate first (a), intra-file VAL-containment + HOLD gate second (VAL
    # first) (b), consumed-P20H/I/J/K-TRAIN + remainder exclusions (c)-(f)
    # with the S2-ii DEV/build-frames disjointness declaration, then
    # corrected-prior-identity + order-freeze + budget-literal (g) before
    # any SC call.
    if str(construction_digest) != FROZEN_CONSTRUCTION_DIGEST:
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = _gate_call("predecessor_construction_identity",
                          verify_predecessor_construction, construction,
                          expected_digest=construction_digest)
    identity = verified["record"]
    dev_source_pin = _gate_call("dev_block_range_identity", verify_dev_source_identity,
                                dev_pairs)
    manifest = _gate_call("dev_split_manifest_identity", verify_dev_manifest,
                          manifest_path, source=source)
    dev_pin = _gate_call("dev_block_range_identity", verify_dev_block_identity)
    disjoint_pin = verify_build_dev_disjointness()
    p16_l1_order = np.asarray(verified["l1_order"], dtype=np.int64)
    p16_l2_order = np.asarray(verified["l2_order"], dtype=np.int64)
    order_pin = _gate_call(
        "order_derivation_identity", verify_stage_b_order_file_p20m, order_file,
        expected_digest=order_digest,
        expected_prior_digest=str(pins["prior_digest"]),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
    raw_l1_order = np.asarray(order_pin["l1_order"], dtype=np.int64)
    raw_l2_order = np.asarray(order_pin["l2_order"], dtype=np.int64)

    # One-open guards are refusals before any content load/open of any input.
    if prior is None and _RAW_PRIOR_CONTENT_LOADED:
        raise ValueError("reload refused: the single raw-prior content load was consumed")
    if lambda_prior is None and _LAMBDA_PRIOR_CONTENT_LOADED:
        raise ValueError("reload refused: the single lambda-prior content load was consumed")
    if dev_table is None and _DEV_PARQUET_CONTENT_OPENED:
        raise ValueError("reopen refused: the single DEV parquet content open was consumed")

    # Input existence and stat-only metadata come before any content load/open.
    real_raw = prior is None
    real_lambda = lambda_prior is None
    real_dev = dev_table is None
    if real_raw:
        raw_file = Path(prior_path)
        if not raw_file.is_file():
            raise FileNotFoundError(f"Stage-A corrected prior not found: {raw_file}")
        prior_stat_before = _stat_record(raw_file)
    else:
        prior_stat_before = _stat_record(None)
    if real_lambda:
        lambda_file = Path(lambda_prior_path)
        if not lambda_file.is_file():
            raise FileNotFoundError(f"carried-over lambda prior not found: {lambda_file}")
        lambda_stat_before = _stat_record(lambda_file)
    else:
        lambda_stat_before = _stat_record(None)
    if real_dev:
        dev_path = Path(dev_pairs)
        if not dev_path.is_file():
            raise FileNotFoundError(f"1p5M DEV pairs parquet not found: {dev_path}")
        dev_stat_before = _stat_record(dev_path)
        if dev_stat_before["size_bytes"] != FROZEN_DEV_PAIRS_SIZE:
            raise ValueError(
                "1.5M DEV pairs size mismatch before content open: "
                f"observed {dev_stat_before['size_bytes']} != expected {FROZEN_DEV_PAIRS_SIZE}"
            )
    else:
        dev_stat_before = _stat_record(None)
    registered_paths = []
    if real_raw:
        registered_paths.append(str(Path(prior_path).resolve()))
    if real_lambda:
        registered_paths.append(str(Path(lambda_prior_path).resolve()))
    if real_dev:
        registered_paths.append(str(Path(dev_pairs).resolve()))
    opened_paths: list[str] = []

    if expected_raw is None:
        exp_digest = str(pins["prior_digest"])
        exp_h1, exp_h2, exp_total = (float(pins["h1"]), float(pins["h2"]),
                                    float(pins["h_total"]))
    else:
        exp_digest, exp_h1, exp_h2, exp_total = expected_raw
        exp_digest, exp_h1, exp_h2, exp_total = (
            str(exp_digest), float(exp_h1), float(exp_h2), float(exp_total))
    if expected_lambda is None:
        lam_exp = None
    else:
        lam_exp = (float(expected_lambda[0]), float(expected_lambda[1]),
                   float(expected_lambda[2]))

    budget_prelim = {"literal": budget_literal_display(float(exp_total))}
    plan = _stub_plan(
        out_path=out_path, source=source, floor=floor, n=n, k1=k1, k2=k2,
        k_total=k_total, construction=construction, digest=construction_digest,
        prior_path=prior_path if real_raw else None, prior_digest=exp_digest,
        lambda_prior_digest=str(FROZEN_LAMBDA_PRIOR_DIGEST), dev_pairs=dev_pairs,
        manifest_path=manifest_path, dev_frames=dev_frames, block_frames=block_frames,
        remainder_frames=remainder_frames, tag_master=tag_master, chunk_rows=chunk_rows,
        tag_bits=tag_bits, identity=identity, manifest=manifest,
        dev_source_pin=dev_source_pin, dev_pin=dev_pin, disjoint_pin=disjoint_pin,
        order_file=order_file, order_digest=order_digest, order_pin=order_pin,
        budget=budget_prelim,
    )
    accounting = {
        "input_mode": "real" if (real_raw or real_lambda or real_dev) else "injected",
        "prior_input_mode": "frozen_prior_file" if real_raw else "injected_prior",
        "dev_input_mode": "pairs_parquet" if real_dev else "injected_table",
        "prior_path": str(prior_path) if real_raw else None,
        "lambda_prior_path": str(lambda_prior_path) if real_lambda else None,
        "dev_pairs_path": str(dev_pairs) if real_dev else None,
        "manifest_path": str(manifest_path),
        "construction_path": str(construction),
        "prior_loader": "per_session_calibration.raw_prior(read-only)" if real_raw else None,
        "pairs_loader": p20l.PAIRS_LOADER_IDENTITY if real_dev else None,
        "registered_content_paths": registered_paths,
        "opened_content_paths": opened_paths,
        "artifact_content_reads_allowed_per_input": 1,
        "counts_content_opens": 0,
        "raw_prior_content_loads": 0,
        "lambda_prior_content_loads": 0,
        "dev_content_opens": 0,
        "attempts_allowed": 1,
        "attempts_consumed_by_this_run": 0,
        "retries": 0,
        "reopen_attempted": False,
        "retry_after_open": False,
    }

    start = time.perf_counter()
    try:
        # ---- input 1: the single corrected-prior load + identity gate.
        if real_raw:
            with open(prior_path, "rb") as fh:
                data = np.load(fh, allow_pickle=False)
                with data:
                    raw_arrays = {k: np.asarray(data[k]) for k in data.files}
            _RAW_PRIOR_CONTENT_LOADED = True
            accounting["raw_prior_content_loads"] = 1
            opened_paths.append(str(Path(prior_path).resolve()))
        else:
            raw_arrays = dict(prior)
        raw_verified = verify_corrected_prior(
            raw_arrays, expected_digest=exp_digest, expected_h1=exp_h1,
            expected_h2=exp_h2, expected_total=exp_total)
        p1_raw = raw_verified["p1"]
        p2_raw = raw_verified["p2"]
        counts_raw = raw_verified["counts"]

        # ---- input 2: the single carried-over lambda-prior load + identity gate.
        if real_lambda:
            loaded_lambda = psc.load_calibrated_prior(str(lambda_prior_path))
            _LAMBDA_PRIOR_CONTENT_LOADED = True
            accounting["lambda_prior_content_loads"] = 1
            opened_paths.append(str(Path(lambda_prior_path).resolve()))
            lambda_arrays = dict(loaded_lambda["arrays"])
        else:
            lambda_arrays = dict(lambda_prior)
        if lam_exp is None:
            lambda_verified = verify_lambda_prior(lambda_arrays)
        else:
            lambda_verified = verify_lambda_prior(
                lambda_arrays, expected_h1=lam_exp[0], expected_h2=lam_exp[1],
                expected_total=lam_exp[2])
        p1_lam = lambda_verified["p1"]
        p2_lam = lambda_verified["p2"]
        counts_lam = lambda_verified["counts"]

        # ---- S2-(i): the budget literal recomputed from the same-run session H.
        budget = verify_budget_literal(float(raw_verified["h_total"]), int(k_total), n=int(n))

        # ---- input 3: the single DEV parquet content open, DEV rows only.
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
        formation = form_dev_blocks(
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

        arm_by_name = {spec.name: spec for spec in arms}

        def current_gates(*, final: bool, wall_now: float) -> tuple:
            gates = _integrity_gates(
                n=n, k1=k1, k2=k2, k_total=k_total, arms=arms, identity=identity,
                manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
                disjoint_pin=disjoint_pin, p16_l1_order=p16_l1_order,
                p16_l2_order=p16_l2_order, raw_l1_order=raw_l1_order,
                raw_l2_order=raw_l2_order, order_pin=order_pin,
                formation=formation, records=records, events=events, calls=calls,
                incremental=incremental, accounting=accounting,
                provenance_violations=provenance_violations,
                cap=budget_cap, wall_s=wall_now, resource_stop=resource_stop,
                raw_verified=raw_verified, lambda_verified=lambda_verified,
                budget=budget,
                construction_floor_hits=order_pin["derivation"].get("floor_hits"),
                prior_stat_before=prior_stat_before, prior_stat_after=prior_stat_before,
                lambda_stat_before=lambda_stat_before,
                lambda_stat_after=lambda_stat_before,
                dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_before,
                registered_paths=registered_paths, opened_paths=opened_paths,
                final=final,
            )
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
                "g0_k1": int(FROZEN_K1_G0),
                "g0_k2": int(FROZEN_K2_G0),
                "budget_literal": str(budget["literal"]),
                "order_digest": str(order_pin.get("order_digest")),
                "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
                "remainder_frames": list(FROZEN_REMAINDER_FRAME_RANGE),
                "dev_source": dict(dev_source_pin),
                "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
                "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
                "g0_leakage_bits": int(FROZEN_LEAKAGE_G0),
                "g1_leakage_bits": int(
                    arm_by_name["G1_raw_prior_session_budget"].leakage_bits),
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
                    "descriptive raw-prior operating-point diagnostic on new-segment "
                    "1.5M VAL blocks (N=32768, three DEV blocks 1660..2043) under "
                    "the frozen corrected prior; G2 is an oracle-labelled "
                    "diagnostic control, never an operational protocol or "
                    "deployable rate; not real-frame FER, reconciliation "
                    "efficiency, leakage, key rate, scaling superiority, "
                    "qualification or promotion evidence; the CE-normalized "
                    "disclosure ratio is not qualification efficiency; "
                    "undetected is never success"
                ),
            }

        def persist(summary_doc: dict) -> None:
            opf._write_json(out_path / "aggregate_summary.json", summary_doc)
            (out_path / "report.md").write_text(
                _render_report(summary_doc), encoding="utf-8")

        arm_tables = {
            "G0_old_point_base": (p1_lam, p2_lam, counts_lam, p16_l1_order, p16_l2_order),
            "G1_raw_prior_session_budget": (p1_raw, p2_raw, counts_raw,
                                            raw_l1_order, raw_l2_order),
            "G2_true_l1_diagnostic": (p1_raw, p2_raw, counts_raw,
                                      raw_l1_order, raw_l2_order),
        }
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
                p1, p2, _, _, _ = arm_tables[arm_name]
                try:
                    scoring_cache[key] = _dev_block_scoring(
                        formation["blocks"][block_index], p1, p2)
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
                        k_total=int(rest_spec.k1) + int(rest_spec.k2), budget_literal=budget["literal"],
                        order_digest=order_digest,
                        resources=opf._cell_resource_record(0.0),
                    )
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
            seed = raw_prior_val_1p5m_seed_bits(
                tag_master, n, spec.name, block_index,
                bit_length=seed_bits_for(n))

            def _tag_fn(bits, _seed, tag_bits, _fixed=seed):
                return toeplitz_tag(bits, _fixed, tag_bits)

            block_start = time.perf_counter()
            p1_use, p2_use, counts_use, l1_use, l2_use = arm_tables[spec.name]
            if spec.kind == "operational":
                # G0 and G1 share the accepted operational path bit-for-bit
                # except prior + orders + K: G0 runs k1=319/k2=6492 on the
                # lambda prior with the frozen P16 orders while G1 runs the
                # derived (K1,K2) on the corrected prior with the frozen
                # derived orders. The swap is hardcoded in the arm table,
                # never CLI-tunable.
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
                    from . import operational_f13 as _opf

                    result = _opf.OperationalBlockResult(
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
                    budget_literal=budget["literal"], order_digest=order_digest,
                    counts_arr=counts_use, p1=p1_use, p2=p2_use, n=n, view=view,
                    error=error,
                )
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
                    budget_literal=budget["literal"], order_digest=order_digest,
                    counts_arr=counts_use, p1=p1_use, p2=p2_use, n=n, view=view,
                    error=error,
                )

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
        if real_raw:
            prior_stat_after = _stat_record(Path(prior_path))
        else:
            prior_stat_after = _stat_record(None)
        if real_lambda:
            lambda_stat_after = _stat_record(Path(lambda_prior_path))
        else:
            lambda_stat_after = _stat_record(None)
        if real_dev:
            dev_stat_after = _stat_record(Path(dev_pairs))
        else:
            dev_stat_after = _stat_record(None)
        gates = _integrity_gates(
            n=n, k1=k1, k2=k2, k_total=k_total, arms=arms, identity=identity,
            manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
            disjoint_pin=disjoint_pin, p16_l1_order=p16_l1_order,
            p16_l2_order=p16_l2_order, raw_l1_order=raw_l1_order,
            raw_l2_order=raw_l2_order, order_pin=order_pin,
            formation=formation, records=records, events=events, calls=calls,
            incremental=incremental, accounting=accounting,
            provenance_violations=provenance_violations,
            cap=budget_cap, wall_s=wall_s, resource_stop=resource_stop,
            raw_verified=raw_verified, lambda_verified=lambda_verified,
            budget=budget,
            construction_floor_hits=order_pin["derivation"].get("floor_hits"),
            prior_stat_before=prior_stat_before, prior_stat_after=prior_stat_after,
            lambda_stat_before=lambda_stat_before,
            lambda_stat_after=lambda_stat_after,
            dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_after,
            registered_paths=registered_paths, opened_paths=opened_paths,
            final=True,
        )
        outcome_label = raw_prior_val_1p5m_label(gates)
        summary = partial_summary(outcome_label, gates, wall_s)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        identity_doc = {
            "predecessor_construction": identity,
            "split_manifest": manifest,
            "dev_source_pin": dev_source_pin,
            "dev_block_pin": dev_pin,
            "build_dev_disjointness_s2_ii": disjoint_pin,
            "expected_corrected_prior_digest": exp_digest,
            "corrected_prior_digest": str(raw_verified["digest"]),
            "recomputed_literals": {
                "h1": float(raw_verified["h1"]),
                "h2": float(raw_verified["h2"]),
                "h_total": float(raw_verified["h_total"]),
            },
            "lambda_prior_digest": str(FROZEN_LAMBDA_PRIOR_DIGEST),
            "budget_literal": str(budget["literal"]),
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
            "expected_old_l1_order_digest": str(FROZEN_OLD_L1_ORDER_DIGEST),
            "derivation_seeds_provenance": [int(s) for s in FROZEN_DERIVATION_SEEDS],
            "stage_b_sampling_calls": int(calls.get("genie", 0)),
            "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
            "prior_stat_before": prior_stat_before,
            "prior_stat_after": prior_stat_after,
            "lambda_stat_before": lambda_stat_before,
            "lambda_stat_after": lambda_stat_after,
            "dev_stat_before": dev_stat_before,
            "dev_stat_after": dev_stat_after,
            "attempt_read_accounting": dict(
                accounting, opened_content_paths=list(opened_paths)),
        }
        opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
        persist(summary)
        return RawPriorVal1p5mRun(summary=summary, records=tuple(records), gates=gates)
    except RawPriorVal1p5mResourceError as exc:
        raise
    except MemoryError as exc:
        label = f"resource stop: MemoryError: {exc}"
        raise RawPriorVal1p5mResourceError(label) from exc


STAGE_B_FLAGS = (
    "prior", "source", "floor", "n", "k1", "k2", "construction",
    "construction_digest", "dev_pairs", "dev_frames", "block_frames",
    "remainder_frames", "tag_master", "chunk_rows", "tag_bits",
    "order_file", "order_digest", "out_dir",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p20m-raw-prior-val-1p5m",
        description=(
            "NB-Polar Phase 4-P20M N=32768 raw-prior + session-budget "
            "operating-point swap: --derive runs the Stage-A derivation on "
            "the read-only worktree input; otherwise all Stage-B flags are "
            "required (frozen command, no production default)"
        ),
    )
    parser.add_argument("--derive", action="store_true",
                        help="Stage-A derivation mode (no other flags allowed)")
    parser.add_argument("--prior", default=None)
    parser.add_argument("--source", default=None)
    parser.add_argument("--floor", default=None, type=float)
    parser.add_argument("--n", default=None, type=int)
    parser.add_argument("--k1", default=None, type=int)
    parser.add_argument("--k2", default=None, type=int)
    parser.add_argument("--construction", default=None)
    parser.add_argument("--construction-digest", default=None, dest="construction_digest")
    parser.add_argument("--dev-pairs", default=None, dest="dev_pairs")
    parser.add_argument("--dev-frames", default=None, type=int, nargs=2, dest="dev_frames")
    parser.add_argument("--block-frames", default=None, type=int, dest="block_frames")
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
    given = [name for name in STAGE_B_FLAGS if getattr(args, name) is not None]
    try:
        if args.derive:
            if given:
                raise ValueError(
                    "mixed invocation refused: --derive takes no Stage-B flags "
                    f"(got {given}); refusing before any read or write"
                )
            result = run_derive_stage_a()
        else:
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
            run = run_raw_prior_val_1p5m(
                prior_path=args.prior,
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
                "g1_restored_count": summary["aggregates"]["recovery"][
                    "g1_restored_count"],
                "integrity_all_pass": summary["integrity_all_pass"],
                "outcome_label": summary["outcome_label"],
                "out_root": args.out_dir,
            }, sort_keys=True))
            return 0
    except (ValueError, FileExistsError, OSError,
            RawPriorVal1p5mContractError) as exc:
        print(f"nbpolar phase4-p20m raw prior val 1p5m refused: {exc}", file=sys.stderr)
        return 2
    if args.derive:
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL_NAME", "MODE", "Q", "ALPHA", "N_BOB", "FROZEN_N", "FROZEN_SOURCE",
    "FROZEN_SOURCE_TAG", "FROZEN_FLOOR", "FROZEN_TARGET_F", "NORM_TOL",
    "FROZEN_K1_G0", "FROZEN_K2_G0", "FROZEN_K_TOTAL_G0", "FROZEN_LEAKAGE_G0",
    "FROZEN_PUBLIC_CONTROL_BITS", "FROZEN_RAW_INPUT_BITS",
    "OPERATING_POINT_SWAP_RULE",
    "FROZEN_DEV_FRAME_RANGE", "FROZEN_DEV_FRAMES", "FROZEN_DEV_PAIRS",
    "FROZEN_BLOCK_COUNT", "FROZEN_BLOCK_FRAMES", "FROZEN_PAIRS_PER_FRAME",
    "FROZEN_SYMBOLS_PER_BLOCK", "FROZEN_BLOCK_RANGES",
    "FROZEN_REMAINDER_FRAME_RANGE", "FROZEN_REMAINDER_FRAMES",
    "FROZEN_REMAINDER_SYMBOLS", "INTRA_FILE_VAL_FRAME_RANGE",
    "INTRA_FILE_HOLD_FRAME_RANGE",
    "P20H_DEV_FRAME_RANGE", "P20I_DEV_FRAME_RANGE", "P20J_DEV_FRAME_RANGE",
    "P20K_DEV_REMAINDER_FRAME_RANGE", "FROZEN_BUILD_FRAME_RANGE",
    "FROZEN_MANIFEST_TRAIN_FRAMES", "FROZEN_MANIFEST_TRAIN_PAIRS",
    "FROZEN_MANIFEST_VAL_FRAMES", "FROZEN_MANIFEST_VAL_PAIRS",
    "FROZEN_MANIFEST_HOLD_FRAMES", "FROZEN_MANIFEST_HOLD_PAIRS",
    "FROZEN_TAG_MASTER", "FROZEN_CHUNK_ROWS", "FROZEN_TAG_BITS",
    "SEED_PREFIX", "OPERATIONAL_PROVENANCE", "ORACLE_PROVENANCE",
    "FROZEN_DERIVATION_SEEDS", "FROZEN_TRAIN_BLOCKS_PER_SEED",
    "FROZEN_TRAIN_BLOCKS_TOTAL", "FROZEN_TRAIN_GENIE_CALLS",
    "FROZEN_ORDER_PROGRAM_PIN",
    "FROZEN_WORKTREE_PRIOR_PATH", "FROZEN_WORKTREE_PRIOR_DIGEST",
    "FROZEN_LAMBDA_PRIOR_PATH", "FROZEN_LAMBDA_PRIOR_DIGEST",
    "FROZEN_LAMBDA_H1", "FROZEN_LAMBDA_H2", "FROZEN_LAMBDA_H_TOTAL",
    "FROZEN_PRIOR_PATH", "FROZEN_ORDER_FILE_PATH", "FROZEN_OUT_ROOT",
    "FROZEN_CONSTRUCTION_PATH", "FROZEN_CONSTRUCTION_DIGEST",
    "FROZEN_OLD_L1_ORDER_DIGEST",
    "FROZEN_DEV_PAIRS_PATH", "FROZEN_DEV_PAIRS_SIZE", "FROZEN_DEV_PAIRS_SHA256",
    "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA",
    "RAW_PRIOR_NPZ_KEYS",
    "FROZEN_PRIOR_DIGEST", "FROZEN_H1", "FROZEN_H2", "FROZEN_H_TOTAL",
    "FROZEN_K_TOTAL", "FROZEN_K1_G1", "FROZEN_K2_G1", "FROZEN_ORDER_DIGEST",
    "FROZEN_CONSTRUCTION_FLOOR_HITS", "FROZEN_CONSTRUCTION_FLOOR_HIT_RATE",
    "pins_frozen", "pins_are_frozen",
    "PLANNED_SC_CALLS", "PLANNED_TAG_INVOCATIONS", "PLANNED_RECORDS",
    "COMPLETE_LABEL", "INTEGRITY_GATE_ORDER", "FROZEN_COMMAND", "OUTPUT_FILES",
    "ATTEMPT_CONSUMPTION_POINT",
    "ArmSpec", "FROZEN_ARM_NAMES", "OPERATIONAL_ARM_NAMES", "ORACLE_ARM_NAME",
    "build_arm_table", "frozen_arm_table", "check_frozen_arm_table",
    "RawPriorVal1p5mContractError", "RawPriorVal1p5mResourceError",
    "RawPriorVal1p5mRun",
    "raw_prefloor_table", "derive_raw_prior_arrays", "build_raw_prior_arrays",
    "load_worktree_counts_arrays", "verify_corrected_prior",
    "budget_literal_display", "verify_budget_literal",
    "verify_stage_b_order_file_p20m", "raw_prior_val_1p5m_seed_bits",
    "verify_build_dev_disjointness",
    "sample_synthetic_train_blocks", "run_derive_stage_a",
    "run_operational_block", "run_oracle_control_block", "OracleControlResult",
    "verify_predecessor_construction", "verify_dev_source_identity",
    "verify_dev_block_identity", "verify_dev_manifest", "verify_lambda_prior",
    "form_dev_blocks", "candidate_nll_bits", "raw_floor_diagnostics",
    "first_error_coordinate", "l1_prefix_positions", "l2_prefix_positions",
    "holdout_nll_bits", "raw_symbol_error_rate",
    "polar_transform_fn", "make_gf32_fn", "toeplitz_tag_fn",
    "oracle_isolation_ok", "recovery_diagnostics", "build_aggregates",
    "raw_prior_val_1p5m_label", "raw_prior_val_1p5m_block_events",
    "raw_prior_val_1p5m_recount_events", "run_raw_prior_val_1p5m",
    "STAGE_B_FLAGS", "build_parser", "main",
]
