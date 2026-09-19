"""NB-Polar Phase 4-P20O maintain-confirmation of ALT-L2-LAPLACE-alpha1 at
the per-session disclosure point on FIRST-USE 2M VAL blocks.

Thin importer of the accepted ``raw_prior_val_1p5m`` runner (read-only; that
module and every accepted module are never edited here), with the accepted
``l2_alt_hold_1p5m`` construction-swap/instrumentation pattern as the
read-only reference. Exact delta list, nothing else:

- (d1) prior source -> the Stage-A 2M raw-prior artifact
  (``raw_prior_2m.npz``) behind a new ``session_prior_identity`` gate
  (canonical digest + lambda-0.0 pin + floor pin + exact 10-key set +
  H-literal recomputation within 1e-12 + ``p_b`` cross-check);
- (d2) alt-L2-table source -> the Stage-A 2M alt artifact
  (``alt_l2_tables_2m.npz``) behind a new ``alt_l2_identity`` gate
  (file-bytes digest + alpha-1.0 pin + floor pin + exact 9-key set +
  incumbent-p1 equality within 1e-12 + descriptive alt-H literals);
- (d3) K pins -> the Stage-A 2M-derived (K_total,K1,K2) with the S2-(i)
  budget-literal display recomputed from the same-run 2M session H (never
  a carried absolute);
- (d4) orders -> the Stage-A frozen ``raw_prior_orders_2m.json`` via the
  reused order-file mechanism (2M-derived L1+L2 worst-first orders,
  digest-gated, byte-identical on all four arms, zero Stage-B sampling);
- (d5) arms A/B/C/D (A = 2M-incumbent-L2 operational; B = 2M-alt-L2
  operational; C = 2M-incumbent oracle; D = 2M-alt oracle) with the SAME
  2M-derived order prefixes;
- (d6) new P20O tag domain (master 2026092310, prefix
  ``nbpolar-p20o-maintain-2m-seed``);
- (d7) mandatory X09-R1 hazard instrumentation (eight scalars plus the
  ninth U-domain cross-check scalar ``l2_fail_in_prefix_u_domain``,
  frozen PRESENT) computed post-decode in ``_l2_hazard_diagnostics``,
  recording-only, truth-isolated;
- (d8) 2M-VAL population (DEV 2187..2826, five blocks at N=32768,
  remainder 2827..2915 counted never decoded) declared inside the
  TRAIN-exclusion gate family (a)->(g).

No SC/transform/floor-semantics/tag-semantics change; no second
construction factor; no lambda anywhere.

Two explicit modes, never mixed: (i) Stage-A derivation mode (``--derive``;
the SINGLE protected counts open of the 2M ``--source 2M`` TRAIN array,
zero DEV contact) and (ii) Stage-B frozen command mode (all Stage-B flags
required, no production default). Mixed or ambiguous invocation refuses
before anything is read or written.

Stage-A pins (``FROZEN_SESSION_PRIOR_DIGEST`` / ``FROZEN_H1`` / ... /
``FROZEN_K1`` / ``FROZEN_K2`` / ``FROZEN_ORDER_DIGEST`` /
``FROZEN_ALT_DIGEST`` / ``FROZEN_D2_FEASIBLE`` / ...) are ``None`` until
the Stage-A derivation fills them; the Stage-B path refuses with
``Stage-A freeze not yet applied`` while any pin is ``None``, and refuses
to proceed when the D2 ``alt_construction_budget_feasibility`` outcome is
not FEASIBLE.
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
from ..v35_algorithm_development import NPZ_KEYS, SOURCE_IDS
from ...io.pairs_loader import load_pairs_table, normalize_pair_columns
from . import holdout_microcheck as hm
from . import l1_order_1p5m as p20l
from . import l2_alt_hold_1p5m as p20n
from . import operational_f13 as opf
from . import per_session_calibration as psc
from . import raw_prior_val_1p5m as p20m
from .algebra import make_gf32
from .empirical_genie_scaling import select_empirical_split
from .target_construction import entropy_bits
from .target_n_scaling import budget_k_total
from .transform import polar_transform

# Reused accepted contracts (read-only; never reimplemented here).
run_operational_block = p20l.run_operational_block
run_oracle_control_block = p20l.run_oracle_control_block
OracleControlResult = p20l.OracleControlResult
verify_predecessor_construction = p20m.verify_predecessor_construction
first_error_coordinate = p20l.first_error_coordinate
l1_prefix_positions = p20l.l1_prefix_positions
l2_prefix_positions = p20l.l2_prefix_positions
seed_bits_for = p20l.seed_bits_for
_stat_record = p20m._stat_record
_block_view = p20m._block_view
_dev_block_scoring = p20m._dev_block_scoring
_scoring_absent = p20m._scoring_absent
_selected_diagnostics = p20m._selected_diagnostics
raw_prior_val_1p5m_block_events = p20m.raw_prior_val_1p5m_block_events
raw_prior_val_1p5m_recount_events = p20m.raw_prior_val_1p5m_recount_events

PROTOCOL_NAME = "nbpolar-p20o-2m-maintain-confirmation"
MODE = "val-2m-maintain-confirmation"

Q = p20l.Q  # 32
ALPHA = p20l.ALPHA  # 2
N_BOB = p20l.N_BOB  # 1024
FROZEN_N = 32768
FROZEN_SOURCE = "2M"
FROZEN_SOURCE_TAG = "type2_2M_20260121_183657"
FROZEN_FLOOR = 1e-15
FROZEN_ALPHA = 1.0
FROZEN_TARGET_F = 1.3
NORM_TOL = 1e-12
FROZEN_HAZARD_R = 8
FROZEN_PUBLIC_CONTROL_BITS = p20m.FROZEN_PUBLIC_CONTROL_BITS  # 327743
FROZEN_RAW_INPUT_BITS = 10 * FROZEN_N  # 327680 per block

# (d1) counts source: the SINGLE authorized protected open in Stage A is the
# 2M ``--source 2M`` TRAIN array of the canonical V25 counts NPZ. The
# canonical data root is the sibling-checkout convention already pinned by
# the accepted ``holdout_microcheck.FROZEN_COUNTS_PATH`` (all accepted
# nbpolar modules read the V25 counts from that absolute root; this worktree
# does not carry the gitignored ``*.npz``). ONLY the 2M array is ever
# materialized; no other member content is read.
FROZEN_COUNTS_PATH = hm.FROZEN_COUNTS_PATH
FROZEN_COUNTS_PATH_CANONICAL_REL = (
    "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
    "nbldpc_v25_20260818/run_04/channel_counts.npz"
)
FROZEN_COUNTS_KEY = NPZ_KEYS["2M"]  # type2_2M_..._N_ab_train_N_ab_train

# (d8) 2M-VAL population: FIRST 640 VAL frames in (frame_id, pair_idx)
# order (frozen VAL base 2187: DEV 2187..2826; five 128-frame blocks;
# VAL remainder 2827..2915 counted never decoded; 2M TRAIN 0..2186 are the
# build frames; 2M HOLD 2916..3644 never touched).
FROZEN_DEV_FRAME_RANGE = (2187, 2826)
FROZEN_DEV_FRAMES = 640
FROZEN_DEV_PAIRS = 163840
FROZEN_BLOCK_COUNT = 5
FROZEN_BLOCK_FRAMES = 128
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_BLOCK_RANGES = (
    (2187, 2314), (2315, 2442), (2443, 2570), (2571, 2698), (2699, 2826),
)
FROZEN_REMAINDER_FRAME_RANGE = (2827, 2915)
FROZEN_REMAINDER_FRAMES = 89
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
INTRA_FILE_VAL_FRAME_RANGE = (2187, 2915)
INTRA_FILE_HOLD_FRAME_RANGE = (2916, 3644)
CONSUMED_2M_TRAIN_FRAME_RANGE = (0, 2186)
CONSUMED_2M_HOLD_FRAME_RANGE = (2916, 3644)
# S2-ii build frames: counts/build frames hold 2M TRAIN 0..2186 only.
FROZEN_BUILD_FRAME_RANGE = (0, 2186)
# Consumed cross-session identities (fail-closed by source tag; frame
# integers alone are never identity).
CONSUMED_1M_SOURCE_TAG = SOURCE_IDS["1M"]
CONSUMED_1P5M_SOURCE_TAG = SOURCE_IDS["1p5M"]
CONSUMED_1M_FRAME_RANGE = (0, 1199)
CONSUMED_1P5M_FRAME_RANGE = (0, 2766)
FROZEN_MANIFEST_TRAIN_FRAMES = 2187
FROZEN_MANIFEST_TRAIN_PAIRS = 559872
FROZEN_MANIFEST_VAL_FRAMES = 729
FROZEN_MANIFEST_VAL_PAIRS = 186624
FROZEN_MANIFEST_HOLD_FRAMES = 729
FROZEN_MANIFEST_HOLD_PAIRS = 186624

# Device source identity: the 2M pairs parquet ONLY (provenance pin frozen
# at Stage A by the v13r3fresh build-manifest cross-check; the 2M file
# itself is NEVER opened/statted/listed in Stage A). The size/sha literals
# below are build-manifest provenance constants; the size is additionally
# enforced from stat before the content open at run level.
FROZEN_DEV_PAIRS_PATH = hm.FROZEN_HOLD_PAIRS_PATH.replace(
    "type2_1M_20260121_184040", FROZEN_SOURCE_TAG)
FROZEN_DEV_PAIRS_SIZE = 2458335  # v13r3fresh build_manifest provenance (bytes)
FROZEN_DEV_PAIRS_SHA256 = (
    "d5a36eec8a03ce7e801bba4fd4b2e62cf8aef13c1efe1166766db79364ffc307"
)  # build-manifest provenance pin (never recomputed from content here)
REFUSED_1M_DEV_PAIRS_PATH = hm.FROZEN_HOLD_PAIRS_PATH  # 1M full pool; never DEV
REFUSED_1P5M_DEV_PAIRS_PATH = hm.FROZEN_HOLD_PAIRS_PATH.replace(
    "type2_1M_20260121_184040", "type2_1p5M_20260121_183806"
)  # entire 1.5M session is fail-closed; refusal string only, never touched
FROZEN_DEV_BUILD_MANIFEST_PATH = (
    "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
    "v13r3fresh_pairs_20260816/build_manifest.json"
)
FROZEN_CONSTRUCTION_PATH = p20l.FROZEN_CONSTRUCTION_PATH
FROZEN_CONSTRUCTION_DIGEST = p20l.FROZEN_CONSTRUCTION_DIGEST
FROZEN_MANIFEST_PATH = p20l.FROZEN_MANIFEST_PATH
FROZEN_MANIFEST_SCHEMA = p20l.FROZEN_MANIFEST_SCHEMA
PAIRS_LOADER_IDENTITY = p20l.PAIRS_LOADER_IDENTITY

# (d6) new P20O tag domain.
FROZEN_TAG_MASTER = 2026092310
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = 64
SEED_PREFIX = "nbpolar-p20o-maintain-2m-seed"

# Derivation seeds (frozen): 4 streams x 4 blocks = 16 synthetic TRAIN
# blocks model-sampled from the 2M raw prior, L1+L2 genie, Stage A only.
FROZEN_DERIVATION_SEEDS = (2026092321, 2026092322, 2026092323, 2026092324)
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

# Stage-A products (frozen paths; digests pinned below at Stage A).
FROZEN_PRIOR_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/raw_prior_2m.npz"
)
FROZEN_ORDER_FILE_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/"
    "raw_prior_orders_2m.json"
)
FROZEN_ALT_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/"
    "alt_l2_tables_2m.npz"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20O-2M-MAINTAIN-CONFIRMATION/"
    "l2_alt_maintain_2m"
)
OUTPUT_FILES = (
    "frozen_plan.json",
    "input_and_predecessor_identity.json",
    "per_block_arm_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)
ATTEMPT_CONSUMPTION_POINT = "first protected content open (VAL pairs parquet)"
COMPLETE_LABEL = "TARGET_EMPIRICAL_N32768_VAL_MAINTAIN_ALT_CONSTRUCTION_2M_COMPLETE"

# Exact keys of the Stage-A artifacts (no more, no fewer).
RAW_PRIOR_NPZ_KEYS = p20m.RAW_PRIOR_NPZ_KEYS  # 10 keys
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

OPERATIONAL_PROVENANCE = p20l.OPERATIONAL_PROVENANCE
ORACLE_PROVENANCE = p20l.ORACLE_PROVENANCE

# ---- Stage-A pins (filled by the Stage-A derivation, 2026-09-19) ----
FROZEN_COUNTS_ARRAY_SHA256 = "e391a3466eee4354f76d65be7093f78b8322103178b6d8577331dbcd092351e4"
FROZEN_COUNTS_TOTAL = 559872
FROZEN_SESSION_PRIOR_DIGEST = "b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587"
FROZEN_SESSION_PRIOR_FLOOR_HITS = 1045941
FROZEN_SESSION_PRIOR_FLOOR_HIT_RATE = 0.9974870681762695
FROZEN_SESSION_PRIOR_ZERO_COLUMNS = 0
FROZEN_H1 = 0.02566204884275839
FROZEN_H2 = 0.8069006731309893
FROZEN_H_TOTAL = 0.8325627219737477
FROZEN_BUDGET_LITERAL = "1.3*32768*0.8325627219737477-64 over 5, floored, clipped [0,65536] = 7080"
FROZEN_K_TOTAL = 7080
FROZEN_K1 = 334
FROZEN_K2 = 6746
FROZEN_ORDER_DIGEST = "b2255449d2422b8f9cd08ee6bdf1e1c40ce7787a0e9107c7819da8acf3bd0906"
FROZEN_ORDER_TRAIN_RESIDUAL = 3.603823440223586e-07
FROZEN_ALT_DIGEST = "98e25495d2e7adcc3332f48279f6f1c824b3f129c3e2cbca93a718c0d1ae5fb5"
FROZEN_ALT_FLOOR_HITS = 0
FROZEN_ALT_FLOOR_HIT_RATE = 0.0
FROZEN_ALT_ZERO_COLUMNS = 0
FROZEN_ALT_F_ALT_MIN = 0.0006071645415907555
FROZEN_ALT_F_ALT_MAX = 0.2895392278953916
FROZEN_ALT_P1_EQUALITY_MAX_ABS_DIFF = 0.0
FROZEN_ALT_H1_INC = 0.02566204884275839
FROZEN_ALT_H2_ALT = 1.3245794596410305
FROZEN_ALT_H_TOTAL_ALT = 1.3502415084837889
FROZEN_ALT_CE_INSAMPLE = 0.8850983725781965
FROZEN_INCUMBENT_CE_INSAMPLE = 0.8069006731253678
FROZEN_ALT_IDEAL_LENGTH_BITS = 29002.90347264234
FROZEN_D2_FEASIBLE = True


def pins_frozen() -> dict:
    """Fail-closed Stage-A pin-state check: every pin must be filled."""
    pins = {
        "counts_array_sha256": FROZEN_COUNTS_ARRAY_SHA256,
        "counts_total": FROZEN_COUNTS_TOTAL,
        "session_prior_digest": FROZEN_SESSION_PRIOR_DIGEST,
        "session_prior_floor_hits": FROZEN_SESSION_PRIOR_FLOOR_HITS,
        "session_prior_floor_hit_rate": FROZEN_SESSION_PRIOR_FLOOR_HIT_RATE,
        "session_prior_zero_columns": FROZEN_SESSION_PRIOR_ZERO_COLUMNS,
        "h1": FROZEN_H1,
        "h2": FROZEN_H2,
        "h_total": FROZEN_H_TOTAL,
        "budget_literal": FROZEN_BUDGET_LITERAL,
        "k_total": FROZEN_K_TOTAL,
        "k1": FROZEN_K1,
        "k2": FROZEN_K2,
        "order_digest": FROZEN_ORDER_DIGEST,
        "order_train_residual": FROZEN_ORDER_TRAIN_RESIDUAL,
        "alt_digest": FROZEN_ALT_DIGEST,
        "alt_floor_hits": FROZEN_ALT_FLOOR_HITS,
        "alt_floor_hit_rate": FROZEN_ALT_FLOOR_HIT_RATE,
        "alt_zero_columns": FROZEN_ALT_ZERO_COLUMNS,
        "alt_f_alt_min": FROZEN_ALT_F_ALT_MIN,
        "alt_f_alt_max": FROZEN_ALT_F_ALT_MAX,
        "alt_p1_equality_max_abs_diff": FROZEN_ALT_P1_EQUALITY_MAX_ABS_DIFF,
        "alt_h1_inc": FROZEN_ALT_H1_INC,
        "alt_h2_alt": FROZEN_ALT_H2_ALT,
        "alt_h_total_alt": FROZEN_ALT_H_TOTAL_ALT,
        "alt_ce_insample": FROZEN_ALT_CE_INSAMPLE,
        "incumbent_ce_insample": FROZEN_INCUMBENT_CE_INSAMPLE,
        "alt_ideal_length_bits": FROZEN_ALT_IDEAL_LENGTH_BITS,
        "d2_feasible": FROZEN_D2_FEASIBLE,
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


PLANNED_SC_CALLS = FROZEN_BLOCK_COUNT * (2 + 2 + 1 + 1)  # 30
PLANNED_TAG_INVOCATIONS = 4 * FROZEN_BLOCK_COUNT  # 20
PLANNED_RECORDS = FROZEN_BLOCK_COUNT * 4  # 20

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "session_prior_identity",
    "alt_l2_identity",
    "alt_construction_budget_feasibility",
    "dev_split_manifest_identity",
    "dev_block_range_identity",
    "order_derivation_identity",
    "k_literal_exact",
    "budget_literal_recomputed",
    "target_population_contract",
    "dev_population_exact",
    "blocks_exact_with_declared_remainder",
    "twenty_records_exact",
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

# (d7) the eight X09-R1 scalars plus the ninth U-domain cross-check scalar
# (frozen PRESENT by the main-thread instruction; recording-only).
HAZARD_FIELDS = (
    "l2_order_digest",
    "l2_prefix_len",
    "l2_fail_in_prefix",
    "l2_fail_hazard_bits",
    "l2_fail_nbhd_mean_bits",
    "l2_prefix_hazard_mean_bits",
    "l2_fail_nbhd_floor_frac",
    "l2_prefix_floor_frac",
    "l2_fail_in_prefix_u_domain",
)
U_DOMAIN_FIELD = "l2_fail_in_prefix_u_domain"

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 1200.0
EXTERNAL_TIMEOUT_S = 1200
ULIMIT_VIRTUAL_KIB = 2097152

# Process-level one-open guards: set at first content load/open, never cleared.
_COUNTS_CONTENT_OPENED = False
_COUNTS_CONTENT_OPENS = 0
_SESSION_PRIOR_CONTENT_LOADED = False
_ALT_CONTENT_LOADED = False
_DEV_PARQUET_CONTENT_OPENED = False


class L2AltMaintain2mContractError(ValueError):
    """Pre-open population/formation failure: BLOCKED(<earliest gate>)."""


class L2AltMaintain2mResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


def _gate_call(gate_name, fn, *args, **kwargs):
    """Run an accepted gate helper read-only, tagged with the P20O gate name."""
    try:
        return fn(*args, **kwargs)
    except (ValueError, FileNotFoundError) as exc:
        raise L2AltMaintain2mContractError(f"BLOCKED({gate_name}): {exc}") from exc


# ---------------------------------------------------------------------------
# (d5) arms: four hardcoded specs, never CLI-tunable, never extensible.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ArmSpec:
    """One frozen P20O arm (never CLI-tunable, never extensible)."""

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


def planned_totals(k1: int, k2: int) -> dict:
    """Frozen §5 planned disclosure totals from the derived integers."""
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
        ArmSpec("A_incumbent_L2_operational", "operational", k1, k2,
                5 * k_total + 64, OPERATIONAL_PROVENANCE, "incumbent"),
        ArmSpec("B_alt_L2_operational", "operational", k1, k2,
                5 * k_total + 64, OPERATIONAL_PROVENANCE, "alt"),
        ArmSpec("C_incumbent_L2_oracle", "oracle_control", 0, k2,
                5 * k2 + 64, ORACLE_PROVENANCE, "incumbent"),
        ArmSpec("D_alt_L2_oracle", "oracle_control", 0, k2,
                5 * k2 + 64, ORACLE_PROVENANCE, "alt"),
    )


def check_frozen_arm_table() -> dict:
    """Fail-closed pin of the four frozen arms and their design accounting.

    Pure code-level check (no I/O): arm names/order, the Stage-A derived
    (K1,K2,K_total), the 5K+64 leakage arithmetic, the construction swap
    (A/C incumbent, B/D alt), the SAME-prefix rule, the B-A / D-C exact
    zero key-bit deltas and the 30 SC / 20 tag / 20 record design totals.
    Any drift raises before any root exists.
    """
    arms = frozen_arm_table()
    if tuple(spec.name for spec in arms) != FROZEN_ARM_NAMES:
        raise ValueError(f"frozen arm order drifted: {tuple(s.name for s in arms)!r}")
    a, b, c, d = arms
    pins = pins_frozen()
    k1, k2 = int(pins["k1"]), int(pins["k2"])
    k_total = int(pins["k_total"])
    if (a.kind, a.k1, a.k2, a.prior_source, a.provenance) != (
            "operational", k1, k2, "incumbent", OPERATIONAL_PROVENANCE):
        raise ValueError("frozen A_incumbent_L2_operational arm drifted")
    if (b.kind, b.k1, b.k2, b.prior_source, b.provenance) != (
            "operational", k1, k2, "alt", OPERATIONAL_PROVENANCE):
        raise ValueError("frozen B_alt_L2_operational arm drifted")
    if (c.kind, c.k1, c.k2, c.prior_source, c.provenance) != (
            "oracle_control", 0, k2, "incumbent", ORACLE_PROVENANCE):
        raise ValueError("frozen C_incumbent_L2_oracle arm drifted")
    if (d.kind, d.k1, d.k2, d.prior_source, d.provenance) != (
            "oracle_control", 0, k2, "alt", ORACLE_PROVENANCE):
        raise ValueError("frozen D_alt_L2_oracle arm drifted")
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
    if PLANNED_SC_CALLS != 30:
        raise ValueError(f"frozen design must plan 30 SC calls, got {PLANNED_SC_CALLS}")
    if PLANNED_TAG_INVOCATIONS != 20:
        raise ValueError(f"frozen design must plan 20 tags, got {PLANNED_TAG_INVOCATIONS}")
    if PLANNED_RECORDS != 20:
        raise ValueError(f"frozen design must plan 20 records, got {PLANNED_RECORDS}")
    totals = planned_totals(k1, k2)
    expected_key_total = FROZEN_BLOCK_COUNT * (
        2 * (5 * (k1 + k2) + 64) + 2 * (5 * k2 + 64))
    if int(totals["planned_key_dependent_bits"]) != int(expected_key_total):
        raise ValueError("frozen planned key-dependent total drifted")
    if int(totals["planned_public_control_bits"]) != 20 * FROZEN_PUBLIC_CONTROL_BITS:
        raise ValueError("frozen planned public total != 20*327743")
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


def _check_target_f(value) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"frozen derivation requires target-f={FROZEN_TARGET_F}, got {value!r}"
        ) from exc
    if out != FROZEN_TARGET_F:
        raise ValueError(
            f"frozen derivation requires target-f={FROZEN_TARGET_F}, got {out}")
    return out


def _check_k1(value) -> int:
    out = opf._as_int(value, "k1", minimum=0)
    pins = pins_frozen()
    if out != int(pins["k1"]):
        raise ValueError(f"frozen point requires k1={int(pins['k1'])}, got {out}")
    return out


def _check_k2(value) -> int:
    out = opf._as_int(value, "k2", minimum=0)
    pins = pins_frozen()
    if out != int(pins["k2"]):
        raise ValueError(f"frozen point requires k2={int(pins['k2'])}, got {out}")
    return out


def check_k_literals(*, k1, k2) -> dict:
    """K-literal gate: the Stage-A derived triple replayed, never recarried.

    The display literal is recomputed from the same-run 2M session H
    (S2-i) and must equal the Stage-A frozen literal; any other triple
    refuses before any SC call. The alt-H literals never enter here.
    """
    k1 = _check_k1(k1)
    k2 = _check_k2(k2)
    pins = pins_frozen()
    k_total = int(k1) + int(k2)
    if k_total != int(pins["k_total"]):
        raise ValueError(
            f"BLOCKED(k_literal_exact): K1+K2={k_total} != frozen "
            f"{int(pins['k_total'])}"
        )
    literal = p20m.budget_literal_display(
        float(pins["h_total"]), n=FROZEN_N, target_f=FROZEN_TARGET_F)
    if str(literal) != str(pins["budget_literal"]):
        raise ValueError(
            "BLOCKED(k_literal_exact): same-run session budget-literal "
            "display drifted from the Stage-A frozen literal"
        )
    return {
        "k1": int(k1),
        "k2": int(k2),
        "k_total": k_total,
        "budget_literal": str(pins["budget_literal"]),
        "recomputed_from": (
            "same-run 2M session H (S2-i; never carried, never the alt-H)"
        ),
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


def _check_counts_path(value, *, frozen=None) -> str:
    """The counts source must resolve to the canonical 2M counts NPZ ONLY."""
    frozen = FROZEN_COUNTS_PATH if frozen is None else str(frozen)
    candidate = str(value)
    if Path(candidate).resolve() != Path(frozen).resolve():
        raise ValueError(
            "derivation requires the canonical V25 counts file "
            f"{frozen!r} (the 2M source array is the SINGLE protected open); "
            f"got {candidate!r}"
        )
    return candidate


def _check_deriv_seeds(value) -> tuple:
    try:
        seeds = tuple(opf._as_int(v, "deriv-seeds", minimum=0) for v in value)
    except TypeError as exc:
        raise TypeError(f"deriv-seeds must be integers: {exc}") from exc
    if seeds != tuple(int(s) for s in FROZEN_DERIVATION_SEEDS):
        raise ValueError(
            "derivation requires the frozen seeds "
            f"{list(FROZEN_DERIVATION_SEEDS)}, got {list(seeds)}"
        )
    return seeds


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
        "comparison_bench.src.comparison_bench.formal_ir.nbpolar.l2_alt_maintain_2m "
        f"--prior {FROZEN_PRIOR_PATH} --prior-digest {FROZEN_SESSION_PRIOR_DIGEST} "
        f"--alt-prior {FROZEN_ALT_PATH} --alt-digest {FROZEN_ALT_DIGEST} "
        f"--source 2M --floor 1e-15 --n 32768 --k1 {int(k1)} --k2 {int(k2)} "
        f"--construction {FROZEN_CONSTRUCTION_PATH} "
        f"--construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
        f"--dev-pairs {FROZEN_DEV_PAIRS_PATH} "
        "--dev-frames 2187 2826 --block-frames 128 --remainder-frames 2827 2915 "
        "--tag-master 2026092310 --chunk-rows 512 --tag-bits 64 "
        f"--order-file {FROZEN_ORDER_FILE_PATH} --order-digest {FROZEN_ORDER_DIGEST} "
        f"--out-dir {FROZEN_OUT_ROOT}"
    )


FROZEN_COMMAND = frozen_command() if pins_are_frozen() else None


# ---------------------------------------------------------------------------
# Stage-A counts open: the 2M ``--source 2M`` TRAIN array ONLY.
# ---------------------------------------------------------------------------

def load_counts_2m(path, *, expected_key: str = FROZEN_COUNTS_KEY) -> dict:
    """Open the canonical V25 counts NPZ once and materialize ONLY 2M.

    The single protected counts-calibration open (no-reopen guarded). The
    npz member listing comes from the zip directory; NO other member
    content is ever read (never the 1M/1.5M arrays, never any other
    source). Returns the raw counts plus the 2M-array-only identity
    (shape/dtype/total/C-order bytes sha256) -- no whole-file hash is
    computed, so no other array's bytes are touched.
    """
    global _COUNTS_CONTENT_OPENED, _COUNTS_CONTENT_OPENS
    if _COUNTS_CONTENT_OPENED:
        raise L2AltMaintain2mContractError(
            "reopen refused: the single protected counts open was already consumed"
        )
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"V25 counts npz not found: {p}")
    st = p.stat()
    with np.load(str(p), allow_pickle=False) as data:
        if str(expected_key) not in set(str(k) for k in data.files):
            raise L2AltMaintain2mContractError(
                f"V25 counts npz is missing the frozen 2M key {expected_key!r}"
            )
        arr = np.asarray(data[expected_key], dtype=np.float64)
    _COUNTS_CONTENT_OPENED = True
    _COUNTS_CONTENT_OPENS += 1
    if arr.shape != (N_BOB, N_BOB):
        raise L2AltMaintain2mContractError(
            f"2M counts must be (1024,1024), got {arr.shape}"
        )
    if not np.isfinite(arr).all() or (arr < 0).any():
        raise L2AltMaintain2mContractError("2M counts must be finite and non-negative")
    return {
        "counts_ab": np.ascontiguousarray(arr),
        "source": FROZEN_SOURCE,
        "source_tag": FROZEN_SOURCE_TAG,
        "counts_key": str(expected_key),
        "shape": tuple(int(v) for v in arr.shape),
        "dtype": str(arr.dtype),
        "counts_total": int(round(float(arr.sum()))),
        "array_sha256": hashlib.sha256(
            np.ascontiguousarray(arr).tobytes(order="C")).hexdigest(),
        "npz_size_bytes": int(st.st_size),
        "counts_content_opens": int(_COUNTS_CONTENT_OPENS),
    }


# ---------------------------------------------------------------------------
# (d1)/(d2) derivation: raw prior + alt table from the SAME 2M counts.
# ---------------------------------------------------------------------------

def raw_prior_arrays(counts_ab) -> dict:
    """Stage-A 2M raw prior arrays exactly as stored (accepted P20M rule)."""
    return dict(p20m.build_raw_prior_arrays(counts_ab))


def alt_tables_2m(counts_ab, *, incumbent_arrays: dict) -> dict:
    """Stage-A 2M alt-L2 arrays (frozen alpha=1 rule on the SAME counts).

    The L1 path is byte-identical: the stored ``p1`` is the Stage-A 2M
    incumbent ``p1`` (never re-derived); ``h2_alt``/``h_total_alt`` are
    recomputed descriptively and are never a budget input.
    """
    cal = p20n.derive_alt_l2_arrays(
        counts_ab,
        incumbent_p1=incumbent_arrays["p1"],
        incumbent_p_b=incumbent_arrays["p_b"],
        incumbent_h1=float(incumbent_arrays["h1"]),
        floor=FROZEN_FLOOR,
    )
    p1_equality = float(
        np.abs(np.asarray(cal["p1"]) - np.asarray(incumbent_arrays["p1"])).max())
    return {
        "arrays": {
            "counts_ab": np.ascontiguousarray(
                np.asarray(counts_ab, dtype=np.float64)),
            "f_alt": cal["f_alt"],
            "p1": cal["p1"],
            "p2_alt": cal["p2_alt"],
            "alpha": np.asarray(FROZEN_ALPHA, dtype=np.float64),
            "floor_value": np.asarray(float(FROZEN_FLOOR), dtype=np.float64),
            "h1_inc": np.asarray(float(cal["h1_inc"]), dtype=np.float64),
            "h2_alt": np.asarray(float(cal["h2_alt"]), dtype=np.float64),
            "h_total_alt": np.asarray(float(cal["h_total_alt"]), dtype=np.float64),
        },
        "floor_hits": int(cal["floor_hits"]),
        "floor_hit_rate": float(cal["floor_hit_rate"]),
        "floor_cells": int(cal["floor_cells"]),
        "zero_columns": int(cal["zero_columns"]),
        "column_dev": float(cal["column_dev"]),
        "f_alt_min": float(cal["f_alt_min"]),
        "f_alt_max": float(cal["f_alt_max"]),
        "p1_equality_max_abs_diff": p1_equality,
        "h1_inc": float(cal["h1_inc"]),
        "h2_alt": float(cal["h2_alt"]),
        "h_total_alt": float(cal["h_total_alt"]),
    }


def feasibility_literals_2m(counts_ab, *, p2_incumbent, p2_alt,
                            k2: int, k_total: int) -> dict:
    """D1 feasibility literals (TRAIN-only, zero protected reads).

    ``ce_alt``/``ce_incumbent`` use the accepted in-sample L2 estimator on
    the SAME 2M TRAIN counts the tables were built from; the L2-only gate
    ceiling is ``5*K2+64`` and the operational ceiling ``5*K_total+64``
    (reference). Construction-validity quantities only, never decoding
    inputs and never thresholds on results.
    """
    ce_alt = p20n.in_sample_l2_ce_bits_per_symbol(counts_ab, p2_alt)
    ce_inc = p20n.in_sample_l2_ce_bits_per_symbol(counts_ab, p2_incumbent)
    total = float(np.asarray(counts_ab, dtype=np.float64).sum())
    ideal = float(ce_alt * FROZEN_N)
    ceiling = int(5 * int(k2) + 64)
    return {
        "estimator": (
            "ce_insample_bits_per_symbol = (1/total) * sum_{a,b} "
            "counts_ab[a,b] * (-log2 p2[u1(a), b, u2(a)]) with "
            "u1(a)=(a>>5)&31, u2(a)=a&31; 2M TRAIN counts only"
        ),
        "counts_total": int(round(total)),
        "ce_alt_insample_bits_per_symbol": float(ce_alt),
        "ce_incumbent_insample_bits_per_symbol": float(ce_inc),
        "alt_feasibility_ceiling_bits": ceiling,
        "operational_ceiling_bits": int(5 * int(k_total) + 64),
        "alt_ideal_length_bits": ideal,
        "feasible": bool(ideal <= float(ceiling)),
    }


def run_derive_stage_a(
    *,
    counts_path=FROZEN_COUNTS_PATH,
    source=None,
    alpha=None,
    floor=None,
    n=None,
    target_f=None,
    seeds=None,
    out_prior_path=FROZEN_PRIOR_PATH,
    out_orders_path=FROZEN_ORDER_FILE_PATH,
    out_alt_path=FROZEN_ALT_PATH,
    expected_counts_total: int = FROZEN_MANIFEST_TRAIN_PAIRS,
) -> dict:
    """Execute the frozen Stage-A derivation once; write the three products.

    The SINGLE protected counts open of the 2M ``--source 2M`` TRAIN array
    (all checks and fail-if-present refusals run BEFORE the open) feeds
    the frozen raw rule, the 16 synthetic TRAIN blocks under the frozen
    derivation seeds (32 L1+L2 genie calls, Stage A only, never a real
    frame), the frozen split selection and the alpha=1 alt rule on the
    SAME counts. ZERO DEV contact: no 2M VAL/HOLD open/stat/listing, no
    1M/1.5M contact, zero decoder execution. D1 literals are computed and
    the D2 ``alt_construction_budget_feasibility`` outcome is decided
    here, BEFORE any VAL contact.
    """
    out_prior = Path(out_prior_path)
    out_orders = Path(out_orders_path)
    out_alt = Path(out_alt_path)
    for out in (out_prior, out_orders, out_alt):
        if out.exists():
            raise FileExistsError(f"refusing to overwrite existing Stage-A product: {out}")
    source_value = _check_source(source)
    alpha_value = _check_alpha(alpha)
    floor_value = _check_floor(floor)
    n_value = _check_n(n)
    target_value = _check_target_f(target_f)
    seeds_value = list(_check_deriv_seeds(
        seeds if seeds is not None else FROZEN_DERIVATION_SEEDS))
    path_value = _check_counts_path(counts_path)
    start = time.perf_counter()
    opened = load_counts_2m(path_value)
    counts = opened["counts_ab"]
    counts_total = int(opened["counts_total"])
    if counts_total != int(expected_counts_total):
        raise L2AltMaintain2mContractError(
            f"2M counts total {counts_total} != manifest 2M TRAIN pairs "
            f"{int(expected_counts_total)}"
        )
    # §3 raw rule (no lambda anywhere) + same-run session H literals.
    cal = p20m.derive_raw_prior_arrays(counts)
    arrays = raw_prior_arrays(counts)
    prior_digest = psc.canonical_prior_digest(arrays)
    h1, h2, h_total = float(cal["h1"]), float(cal["h2"]), float(cal["h_total"])
    # S2-(i) budget literal recomputed from the same-run 2M session H.
    budget = p20m.verify_budget_literal(
        h_total, budget_k_total(n_value, h_total, target_value),
        n=n_value, target_f=target_value)
    k_total = int(budget["k_total"])
    # 16 synthetic TRAIN blocks under the frozen derivation seeds.
    sampled = p20m.sample_synthetic_train_blocks(
        cal["p_b"], cal["f_raw"], cal["p1"], cal["p2"],
        seeds=seeds_value, blocks_per_seed=FROZEN_TRAIN_BLOCKS_PER_SEED,
        n=n_value,
    )
    genie_calls = int(sampled["calls"].get("genie", 0))
    if genie_calls != 2 * int(sampled["blocks_used"]):
        raise ValueError("derivation genie-call accounting != 2 per used block")
    if int(sampled["provenance_violations"]) != 0:
        raise ValueError("derivation provenance violations != 0")
    split = select_empirical_split(
        n_value, sampled["e1_mean"], sampled["h1_mean"],
        sampled["e2_mean"], sampled["h2_mean"], k_total)
    k1, k2 = int(split["k1"]), int(split["k2"])
    l1_order = np.asarray(split["l1_order"], dtype=np.int64)
    l2_order = np.asarray(split["l2_order"], dtype=np.int64)
    out_prior.parent.mkdir(parents=True, exist_ok=True)
    with open(out_prior, "wb") as fh:
        np.savez(fh, **arrays)
    order_doc = {
        "protocol": PROTOCOL_NAME,
        "kind": "raw-prior-orders-file",
        "n": int(n_value),
        "k_total": int(k_total),
        "k1": int(k1),
        "k2": int(k2),
        "l1_order": [int(v) for v in l1_order.tolist()],
        "l2_order": [int(v) for v in l2_order.tolist()],
        "derivation": {
            "program": FROZEN_ORDER_PROGRAM_PIN,
            "prior_path": str(out_prior),
            "prior_digest": prior_digest,
            "counts_path": str(path_value),
            "counts_source": source_value,
            "counts_source_tag": FROZEN_SOURCE_TAG,
            "counts_key": str(opened["counts_key"]),
            "counts_array_sha256": str(opened["array_sha256"]),
            "train_seeds": [int(s) for s in seeds_value],
            "train_blocks_per_seed": int(FROZEN_TRAIN_BLOCKS_PER_SEED),
            "train_blocks_attempted": int(sampled["blocks_attempted"]),
            "train_blocks_used": int(sampled["blocks_used"]),
            "train_impossible": int(sampled["blocks_impossible"]),
            "train_genie_calls": genie_calls,
            "provenance_violations": int(sampled["provenance_violations"]),
            "budget_literal": str(budget["literal"]),
            "counts_total": counts_total,
            "floor_hits": int(cal["floor_hits"]),
            "floor_hit_rate": float(cal["floor_hit_rate"]),
            "zero_columns": int(cal["zero_columns"]),
            "train_residual": float(split["residual"]),
        },
    }
    out_orders.write_text(
        json.dumps(order_doc, sort_keys=True) + "\n", encoding="utf-8")
    order_digest = hashlib.sha256(out_orders.read_bytes()).hexdigest()
    # §3 alpha=1 alt table from the SAME counts (L1 carried byte-identical).
    alt = alt_tables_2m(counts, incumbent_arrays=arrays)
    buffer = io.BytesIO()
    np.savez(buffer, **alt["arrays"])
    payload = buffer.getvalue()
    alt_digest = hashlib.sha256(payload).hexdigest()
    out_alt.write_bytes(payload)
    # D1 literals + D2 gate BEFORE any VAL contact.
    d1 = feasibility_literals_2m(
        counts, p2_incumbent=np.asarray(arrays["p2"], dtype=np.float64),
        p2_alt=alt["arrays"]["p2_alt"], k2=k2, k_total=k_total)
    feasible = bool(d1["feasible"])
    wall_s = round(float(time.perf_counter() - start), 6)
    return {
        "mode": "stage-a-derive",
        "protocol": PROTOCOL_NAME,
        "counts_path": str(path_value),
        "counts_source": source_value,
        "counts_source_tag": FROZEN_SOURCE_TAG,
        "counts_key": str(opened["counts_key"]),
        "counts_array_sha256": str(opened["array_sha256"]),
        "counts_shape": list(opened["shape"]),
        "counts_dtype": str(opened["dtype"]),
        "counts_total": counts_total,
        "npz_size_bytes": int(opened["npz_size_bytes"]),
        "counts_content_opens": int(opened["counts_content_opens"]),
        "prior_path": str(out_prior),
        "prior_digest": prior_digest,
        "prior_npz_keys": list(RAW_PRIOR_NPZ_KEYS),
        "lambda_star": 0.0,
        "floor_value": floor_value,
        "h1": h1,
        "h2": h2,
        "h_total": h_total,
        "floor_hits": int(cal["floor_hits"]),
        "floor_hit_rate": float(cal["floor_hit_rate"]),
        "floor_cells": int(cal["floor_cells"]),
        "zero_columns": int(cal["zero_columns"]),
        "column_dev": float(cal["column_dev"]),
        "budget_literal": str(budget["literal"]),
        "k_total": k_total,
        "k1": k1,
        "k2": k2,
        "order_path": str(out_orders),
        "order_digest": order_digest,
        "order_n": int(n_value),
        "train_residual": float(split["residual"]),
        "derivation_seeds": [int(s) for s in seeds_value],
        "train_blocks_used": int(sampled["blocks_used"]),
        "train_blocks_impossible": int(sampled["blocks_impossible"]),
        "train_genie_calls": genie_calls,
        "provenance_violations": int(sampled["provenance_violations"]),
        "alt_path": str(out_alt),
        "alt_digest": alt_digest,
        "alt_npz_keys": list(ALT_L2_NPZ_KEYS),
        "alpha": float(FROZEN_ALPHA),
        "alt_floor_hits": int(alt["floor_hits"]),
        "alt_floor_hit_rate": float(alt["floor_hit_rate"]),
        "alt_floor_cells": int(alt["floor_cells"]),
        "alt_zero_columns": int(alt["zero_columns"]),
        "alt_column_dev": float(alt["column_dev"]),
        "alt_f_alt_min": float(alt["f_alt_min"]),
        "alt_f_alt_max": float(alt["f_alt_max"]),
        "alt_p1_equality_max_abs_diff": float(alt["p1_equality_max_abs_diff"]),
        "alt_h1_inc": float(alt["h1_inc"]),
        "alt_h2_alt": float(alt["h2_alt"]),
        "alt_h_total_alt": float(alt["h_total_alt"]),
        "d1": d1,
        "alt_construction_budget_feasibility": (
            "FEASIBLE" if feasible else "ALT_CONSTRUCTION_BUDGET_INFEASIBLE"
        ),
        "sampling_calls": genie_calls,
        "decoder_calls": 0,
        "protected_content_opens": int(opened["counts_content_opens"]),
        "wall_s": wall_s,
    }


# ---------------------------------------------------------------------------
# Stage-B identity gates (pure; run before any protected content open).
# ---------------------------------------------------------------------------

def verify_dev_source_identity_2m(dev_pairs=None) -> dict:
    """Gate (a): cross-file 2M source identity (FIRST, before any open).

    Pure string/constant check (no I/O): the DEV content-open path must be
    exactly the frozen 2M pairs path. The 1M full-pool path and the 1.5M
    session path refuse with their own messages (bare frame integers
    collide across files, so source-tag + manifest provenance pin is the
    identity -- never frame numbers alone); any other path refuses as
    well. Raises before any root exists and before either protected
    content open, consuming nothing.
    """
    candidate = FROZEN_DEV_PAIRS_PATH if dev_pairs is None else str(dev_pairs)
    if candidate == REFUSED_1M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20O DEV source gate: 1M full-pool path refused "
            f"({REFUSED_1M_DEV_PAIRS_PATH!r}); the entire 1M pool is "
            "fail-closed against P20O DEV selection"
        )
    if candidate == REFUSED_1P5M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20O DEV source gate: 1.5M session path refused "
            f"({REFUSED_1P5M_DEV_PAIRS_PATH!r}); the entire 1.5M session is "
            "fail-closed against P20O DEV selection"
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
        raise ValueError("P20O DEV source identity mismatch: " + ",".join(failing))
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


def verify_val_containment(dev_frames=None, remainder_frames=None) -> dict:
    """Gate (b): intra-file 2M VAL containment (VAL 2187..2915).

    Pure code-level check (no I/O): the DEV range and the declared
    remainder must lie wholly inside 2M VAL 2187..2915, must overlap NONE
    of 2M TRAIN 0..2186 (build frames) or 2M HOLD 2916..3644, and the
    declared DEV must be exactly the FIRST 640 VAL frames (frozen VAL
    base 2187: 2187..2826) with the frozen five-block decomposition. Any
    violation raises before any protected content open.
    """
    dev_pair = (tuple(FROZEN_DEV_FRAME_RANGE) if dev_frames is None
                else tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    val_first, val_last = INTRA_FILE_VAL_FRAME_RANGE
    hold_first, hold_last = INTRA_FILE_HOLD_FRAME_RANGE
    train_first, train_last = CONSUMED_2M_TRAIN_FRAME_RANGE
    dev_first, dev_last = dev_pair
    rem_first, rem_last = rem_pair
    for label, (start, end) in (("DEV", dev_pair), ("remainder", rem_pair)):
        if not (val_first <= start and end <= val_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"lies outside 2M VAL {val_first}..{val_last}"
            )
        if not (end < hold_first or start > hold_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"overlaps 2M HOLD {hold_first}..{hold_last}"
            )
        if not (end < train_first or start > train_last):
            raise ValueError(
                f"BLOCKED(dev_block_range_identity): {label} {start}..{end} "
                f"overlaps 2M TRAIN {train_first}..{train_last}"
            )
    if dev_pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise ValueError(
            f"BLOCKED(dev_block_range_identity): DEV {dev_pair} != frozen "
            f"{tuple(FROZEN_DEV_FRAME_RANGE)} (FIRST 640 VAL frames)"
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
            "the five VAL DEV blocks end"
        )
    return {
        "dev_frame_range": [int(dev_first), int(dev_last)],
        "remainder_frame_range": [int(rem_first), int(rem_last)],
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "intra_file_val_frame_range": [int(val_first), int(val_last)],
        "intra_file_hold_frame_range": [int(hold_first), int(hold_last)],
        "val_contained": True,
        "train_exterior_disjoint": True,
        "hold_disjoint": True,
        "first_640_val_frames": True,
        "verified": True,
    }


def verify_consumed_exclusions_2m(dev_frames=None, remainder_frames=None) -> dict:
    """Gates (c)-(e): consumed-1M / consumed-1.5M / S2-ii declaration.

    Pure code-level check (no I/O). The 2M DEV selection is identity-tagged
    (``type2_2M_20260121_183657``): the entire 1M pool and the entire 1.5M
    session are fail-closed by source-tag + cross-file gate (a) -- bare
    frame integers are never identity. Within the 2M identity, neither the
    DEV blocks nor the declared remainder overlap the consumed 2M TRAIN
    0..2186 or 2M HOLD 2916..3644; the DEV/build-frames disjointness
    declaration is pinned with the frozen frame sets (build subset TRAIN
    0..2186; DEV subset VAL 2187..2826; disjoint by split identity). Any
    violation raises before any protected content open.
    """
    dev_pair = (tuple(FROZEN_DEV_FRAME_RANGE) if dev_frames is None
                else tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames))
    rem_pair = (tuple(FROZEN_REMAINDER_FRAME_RANGE) if remainder_frames is None
                else tuple(opf._as_int(v, "remainder-frames", minimum=0)
                           for v in remainder_frames))
    ranges = [tuple(dev_pair)] + [tuple(r) for r in FROZEN_BLOCK_RANGES]
    for label, (start, end) in (
            ("consumed 2M TRAIN 0..2186", CONSUMED_2M_TRAIN_FRAME_RANGE),
            ("2M HOLD 2916..3644", CONSUMED_2M_HOLD_FRAME_RANGE)):
        for r_start, r_end in ranges:
            if not (r_end < start or r_start > end):
                raise ValueError(
                    f"BLOCKED(dev_block_range_identity): declared range "
                    f"{r_start}..{r_end} overlaps {label}"
                )
    if not (rem_pair[1] < CONSUMED_2M_HOLD_FRAME_RANGE[0]
            or rem_pair[0] > CONSUMED_2M_HOLD_FRAME_RANGE[1]):
        raise ValueError(
            "BLOCKED(dev_block_range_identity): declared 2M VAL remainder "
            f"{rem_pair[0]}..{rem_pair[1]} overlaps 2M HOLD"
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
        "consumed_2m_hold_disjoint": True,
        "consumed_1m_disjoint_by_identity": True,
        "consumed_1p5m_disjoint_by_identity": True,
        "val_remainder_never_decoded": True,
        "disjoint": True,
        "verified": True,
    }


def verify_dev_manifest_2m(path, *, source: str = FROZEN_SOURCE) -> dict:
    """Verify the V25 split manifest declares the 2M development pool.

    JSON read only; no protected content open. Accepted schema, the 2M
    source tag, and exactly the 2M TRAIN 2187/559872 + VAL 729/186624 +
    HOLD 729/186624 counts whose VAL cell hosts the P20O DEV segment.
    Any mismatch raises before any root exists.
    """
    if source != FROZEN_SOURCE:
        raise ValueError(f"frozen point requires source={FROZEN_SOURCE!r}, got {source!r}")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"split manifest not found: {p}")
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(f"dev split manifest identity unreadable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("schema") != FROZEN_MANIFEST_SCHEMA:
        raise ValueError(
            "dev split manifest identity: schema "
            f"{doc.get('schema')!r} != accepted {FROZEN_MANIFEST_SCHEMA!r}"
        )
    per_source = doc.get("per_source")
    tag = SOURCE_IDS[source]
    cell = per_source.get(tag) if isinstance(per_source, dict) else None
    if not isinstance(cell, dict):
        raise ValueError(f"dev split manifest identity: missing per_source entry {tag!r}")
    try:
        frames = cell["frames"]
        pairs = cell["pairs"]
        train_frames = int(frames["train"])
        train_pairs = int(pairs["train"])
        val_frames = int(frames["val"])
        val_pairs = int(pairs["val"])
        hold_frames = int(frames["hold"])
        hold_pairs = int(pairs["hold"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"dev split manifest identity: missing counts: {exc}") from exc
    for label, got, want_frames, want_pairs in (
            ("2M TRAIN", (train_frames, train_pairs),
             FROZEN_MANIFEST_TRAIN_FRAMES, FROZEN_MANIFEST_TRAIN_PAIRS),
            ("2M VAL", (val_frames, val_pairs),
             FROZEN_MANIFEST_VAL_FRAMES, FROZEN_MANIFEST_VAL_PAIRS),
            ("2M HOLD", (hold_frames, hold_pairs),
             FROZEN_MANIFEST_HOLD_FRAMES, FROZEN_MANIFEST_HOLD_PAIRS)):
        if got != (want_frames, want_pairs):
            raise ValueError(
                f"dev split manifest identity: {label} population {got} "
                f"!= frozen {want_frames} frames / {want_pairs} pairs"
            )
    return {
        "manifest_path": str(p),
        "schema": FROZEN_MANIFEST_SCHEMA,
        "source": source,
        "source_tag": tag,
        "train_frames": train_frames,
        "train_pairs": train_pairs,
        "val_frames": val_frames,
        "val_pairs": val_pairs,
        "hold_frames": hold_frames,
        "hold_pairs": hold_pairs,
        "dev_frames": FROZEN_MANIFEST_VAL_FRAMES,
        "dev_pairs": FROZEN_MANIFEST_VAL_PAIRS,
    }


def verify_session_prior_2m(prior_arrays, *, expected_digest: str,
                            expected_h1: float, expected_h2: float,
                            expected_total: float) -> dict:
    """``session_prior_identity`` gate: Stage-A 2M raw prior.

    Pure array check (no I/O): exact 10-key set, canonical digest equality
    with the Stage-A pin, lambda-0.0 / floor pins, recomputed H1/H2/TOTAL
    within 1e-12 of the frozen literals, the ``p_b`` cross-check against
    the ``counts_ab`` column totals / total, and column normalization.
    Any mismatch raises before any SC call.
    """
    try:
        verified = p20m.verify_corrected_prior(
            prior_arrays, expected_digest=expected_digest,
            expected_h1=expected_h1, expected_h2=expected_h2,
            expected_total=expected_total)
    except ValueError as exc:
        raise ValueError(f"BLOCKED(session_prior_identity): {exc}") from exc
    return verified


def verify_alt_l2_arrays_2m(alt_arrays, *, incumbent_arrays) -> dict:
    """Pure 2M alt-table identity checks (shared by disk and injected seams)."""
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
    if FROZEN_ALT_H1_INC is not None and abs(h1_inc - float(FROZEN_ALT_H1_INC)) > NORM_TOL:
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


def verify_alt_l2_identity_2m(path, *, expected_digest: str,
                              incumbent_arrays) -> dict:
    """``alt_l2_identity`` gate: file-bytes digest + pure alt-table checks.

    Worktree-file read only (never a protected open): the file-bytes
    sha256 must equal the frozen ``--alt-digest`` (which itself must equal
    the Stage-A pin) before the pure identity checks run. Any mismatch
    raises before any SC call.
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
    verified = verify_alt_l2_arrays_2m(arrays, incumbent_arrays=incumbent_arrays)
    verified["file_digest"] = file_digest
    verified["expected_digest"] = digest_pin
    verified["alt_path"] = str(p)
    return verified


def verify_stage_b_order_file_2m(path, *, expected_digest: str,
                                 expected_prior_digest: str, expected_k1: int,
                                 expected_k2: int, expected_k_total: int) -> dict:
    """``order_derivation_identity`` gate: Stage-A frozen 2M order file.

    Worktree-file read only (never a protected open): the file-bytes
    sha256 must equal the frozen ``--order-digest`` (which itself must
    equal the Stage-A pin), the document must carry the frozen
    protocol/kind with ``n == 32768``, BOTH L1 and L2 orders must be
    permutations of ``0..N-1``, the frozen prefix lengths must equal the
    Stage-A derived (K1,K2,K_total), and the derivation provenance
    (2M-prior digest + program pin + derivation seeds + 16 blocks) must
    replay exactly. Stage B performs zero sampling: this function loads a
    frozen file, never a sampler.
    """
    if FROZEN_ORDER_DIGEST is None:
        raise ValueError("Stage-A freeze not yet applied: order digest pin is None")
    if str(expected_digest) != str(FROZEN_ORDER_DIGEST):
        raise ValueError("order-file digest flag != frozen Stage-A order digest")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Stage-A frozen 2M order file not found: {p}")
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
        raise ValueError("order file protocol != frozen P20O protocol")
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
        raise ValueError("order file derivation prior digest != frozen 2M prior digest")
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
# (d8) 2M VAL population: deterministic block formation (never sampled).
# ---------------------------------------------------------------------------

def form_val_blocks(
    table,
    *,
    dev_frames=FROZEN_DEV_FRAME_RANGE,
    block_frames: int = FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
) -> dict:
    """Deterministic 2M VAL development validation plus block/remainder slicing.

    Accepted ``form_dev_blocks``/``form_hold_blocks`` pattern with the
    P20O VAL ranges: FIRST 640 VAL frames 2187..2826 in (frame_id,
    pair_idx) order -> five 128-frame blocks at N=32768; remainder
    2827..2915 counted never decoded. Any malformed population raises
    ``BLOCKED(dev_population_exact)``; any declared-range mismatch raises
    ``BLOCKED(blocks_exact_with_declared_remainder)``. No sorting key
    other than ``(frame_id, pair_idx)`` and no sampling of any kind.
    """
    try:
        pair = tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames)
    except TypeError as exc:
        raise TypeError(f"dev-frames must be a pair of integers: {exc}") from exc
    if pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise L2AltMaintain2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"dev-frames {pair} != frozen {tuple(FROZEN_DEV_FRAME_RANGE)}"
        )
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise L2AltMaintain2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"block-frames {block_frames} != frozen {FROZEN_BLOCK_FRAMES}"
        )
    try:
        rem_pair = tuple(opf._as_int(v, "remainder-frames", minimum=0)
                         for v in remainder_frames)
    except TypeError as exc:
        raise TypeError(f"remainder-frames must be a pair of integers: {exc}") from exc
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise L2AltMaintain2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"remainder-frames {rem_pair} != frozen {tuple(FROZEN_REMAINDER_FRAME_RANGE)}"
        )
    try:
        frame_id = np.asarray(table["frame_id"], dtype=np.int64)
        pair_idx = np.asarray(table["pair_idx"], dtype=np.int64)
        alice = np.asarray(table["alice_symbol"], dtype=np.int64)
        bob = np.asarray(table["bob_symbol"], dtype=np.int64)
    except (KeyError, TypeError, ValueError) as exc:
        raise L2AltMaintain2mContractError(
            f"BLOCKED(dev_population_exact): loader frame is malformed: {exc}"
        ) from exc
    if not (frame_id.shape == pair_idx.shape == alice.shape == bob.shape) or frame_id.ndim != 1:
        raise L2AltMaintain2mContractError(
            "BLOCKED(dev_population_exact): column shapes disagree"
        )
    for name, values in (("alice_symbol", alice), ("bob_symbol", bob)):
        if values.size == 0 or values.min() < 0 or values.max() >= N_BOB:
            raise L2AltMaintain2mContractError(
                f"BLOCKED(dev_population_exact): {name} outside 0..{N_BOB - 1}"
            )
    dev_first, dev_last = pair
    pool_frame_id = np.asarray(table["frame_id"], dtype=np.int64)
    selected = (frame_id >= dev_first) & (frame_id <= dev_last)
    rows = int(np.sum(selected))
    if rows == 0:
        raise L2AltMaintain2mContractError(
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
        raise L2AltMaintain2mContractError(
            "BLOCKED(dev_population_exact): DEV frames "
            f"{unique_frames.size} with range {int(unique_frames[0])}.."
            f"{int(unique_frames[-1])} != frozen {FROZEN_DEV_FRAMES} with range "
            f"{dev_first}..{dev_last}"
        )
    if rows != FROZEN_DEV_PAIRS:
        raise L2AltMaintain2mContractError(
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
        raise L2AltMaintain2mContractError(
            "BLOCKED(dev_population_exact): pair_idx is not exactly 0..255 per frame"
        )
    ranges = []
    first = dev_first
    for _ in range(FROZEN_BLOCK_COUNT):
        last = first + int(block_frames) - 1
        ranges.append((first, last))
        first = last + 1
    if tuple(ranges) != tuple(tuple(r) for r in FROZEN_BLOCK_RANGES):
        raise L2AltMaintain2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): block ranges "
            f"{tuple(ranges)} != frozen {tuple(tuple(r) for r in FROZEN_BLOCK_RANGES)}"
        )
    rem_first, rem_last = rem_pair
    if first != rem_first:
        raise L2AltMaintain2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder "
            f"{rem_first}..{rem_last} does not start where the five DEV blocks end"
        )
    remainder_rows = (pool_frame_id >= rem_first) & (pool_frame_id <= rem_last)
    remainder_frame_ids = pool_frame_id[remainder_rows]
    if int(np.sum(remainder_rows)) != FROZEN_REMAINDER_SYMBOLS:
        raise L2AltMaintain2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder rows "
            f"{int(np.sum(remainder_rows))} != frozen {FROZEN_REMAINDER_SYMBOLS}"
        )
    if (np.unique(remainder_frame_ids).size != FROZEN_REMAINDER_FRAMES
            or int(remainder_frame_ids.min()) != rem_first
            or int(remainder_frame_ids.max()) != rem_last):
        raise L2AltMaintain2mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder frames "
            f"!= frozen {rem_first}..{rem_last} ({FROZEN_REMAINDER_FRAMES} frames)"
        )
    check = verify_val_containment(pair, rem_pair)
    if not check["verified"]:
        raise L2AltMaintain2mContractError("BLOCKED(dev_block_range_identity)")
    check2 = verify_consumed_exclusions_2m(pair, rem_pair)
    if not check2["verified"]:
        raise L2AltMaintain2mContractError("BLOCKED(dev_block_range_identity)")
    blocks = []
    for index, (start, end) in enumerate(ranges):
        mask = (frame_id >= start) & (frame_id <= end)
        if int(np.sum(mask)) != FROZEN_SYMBOLS_PER_BLOCK:
            raise L2AltMaintain2mContractError(
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
# (d6) P20O tag domain.
# ---------------------------------------------------------------------------

def l2_alt_maintain_2m_seed_bits(master: int, n: int, arm: str, block_index: int,
                                 *, bit_length: int | None = None) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P20O domain).

    Rule: concatenate SHA-256 over
    ``"nbpolar-p20o-maintain-2m-seed:<master>:<n>:<arm>:<block_index>:
    <counter>"`` for ``counter = 0, 1, ...`` (ASCII decimal), unpack each
    digest MSB-first and truncate to ``bit_length`` (default ``10*n + 63``).
    The P20O prefix and arm tokens differ from ALL prior domains on purpose.
    Seed contents are public control and are never persisted; only the bit
    length is recorded.
    """
    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P20O seed domain: {arm!r}")
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
# (d7) Mandatory X09-R1 hazard instrumentation (recording-only, post-decode).
# ---------------------------------------------------------------------------

def _raw_p2_from_counts(counts_arr) -> np.ndarray:
    """Accepted P20N helper: unfloored column-normalized TRAIN conditional p2."""
    return p20n._raw_p2_from_counts(counts_arr)


def _hazard_bits(p2_table, high_cell, bob, low_cell) -> np.ndarray:
    """Accepted P20N helper: ``-log2`` arm-table mass at the given cells."""
    return p20n._hazard_bits(p2_table, high_cell, bob, low_cell)


def _l2_hazard_diagnostics(*, block, view, p2_arm, counts_arr, l2_order, k2,
                           first_error, field=None, low_hat=None) -> dict:
    """P20O mandatory recorder: nine scalars, post-decode, recording-only.

    Called after every SC call for the record has completed (after tag
    scoring) from the record writers at the carried-over P20M
    ``_selected_diagnostics`` code point. Reads truth (and the arm table)
    for RECORDING ONLY; its outputs are written into the record dict and
    are never passed to any decoder, metric builder, disclosure or order
    decision.

    Fields (frozen semantics; scalar-only):
    - ``l2_order_digest`` / ``l2_prefix_len``: frozen 2M order-file digest
      and the gated K2 prefix length on every record;
    - ``l2_fail_in_prefix`` / ``l2_fail_hazard_bits`` /
      ``l2_fail_nbhd_mean_bits`` / ``l2_fail_nbhd_floor_frac``: null
      unless ``first_error_layer == L2``; otherwise the failing position's
      disclosed-prefix membership (natural block symbol index per X09-R1
      D4), its ``-log2`` arm-table mass at the true ``(U1_cond, B, U2)``
      cell (``U1_cond`` = hard-L1 candidate on the operational arms, true
      high on the oracle arms), the same quantity averaged over the frozen
      radius-R=8 window around the position (clipped to the block), and the
      fraction of window cells whose unfloored TRAIN conditional mass is
      below 1e-15;
    - ``l2_prefix_hazard_mean_bits`` / ``l2_prefix_floor_frac``: the same
      two quantities averaged over the disclosed-prefix positions using
      true cells, on every completed record (never null);
    - ``l2_fail_in_prefix_u_domain`` (ninth scalar, frozen PRESENT): null
      unless ``first_error_layer == L2``, else whether the U-domain
      first-mismatch index (``polar_transform(low_hat)`` vs the U-domain
      truth ``view['u2']``; the disclosed L2 prefix set lives in the same
      U-domain index space) lies in the disclosed L2 prefix set; closes
      the domain-mixed ``l2_fail_in_prefix`` ambiguity in-run.
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
        # Ninth scalar: U-domain first-mismatch prefix membership.
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
        diag["l2_fail_in_prefix_u_domain"] = bool(mask[int(mismatch[0])])
    return diag


# ---------------------------------------------------------------------------
# Stage-B records (construction point + floor fields + the nine §7 scalars).
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
    # Recording-only recorder at the carried-over P20M code point; all SC
    # calls for this record have completed before this call.
    view_arm = dict(view)
    view_arm["u1_cond"] = (
        result.high_hat if result.high_hat is not None else view["high"])
    record.update(_l2_hazard_diagnostics(
        block=block, view=view_arm, p2_arm=p2, counts_arr=counts_arr,
        l2_order=l2_order, k2=FROZEN_K2, first_error=first_error,
        field=field, low_hat=result.low_hat))
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
    record.update(_l2_hazard_diagnostics(
        block=block, view=view_arm, p2_arm=p2, counts_arr=counts_arr,
        l2_order=l2_order, k2=FROZEN_K2, first_error=first_error,
        field=field, low_hat=result.low_hat))
    return record


def _abort_record(*, spec, arm_index, block, k_total, budget_literal,
                  prior_digest, alt_digest, order_digest) -> dict:
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
    for field in HAZARD_FIELDS:
        record[field] = (
            str(FROZEN_ORDER_DIGEST) if field == "l2_order_digest"
            else (int(FROZEN_K2) if field == "l2_prefix_len" else None)
        )
    return record


# ---------------------------------------------------------------------------
# Aggregates (oracle excluded; maintenance descriptive only).
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


def maintenance_diagnostics(records) -> dict:
    """Descriptive B-vs-A and D-vs-C maintenance/restoration (never a threshold).

    ``b_maintained_count`` = blocks where A is exact AND B is exact;
    ``b_restored_count`` = blocks where A fails and B is exact; the A->B
    transition table covers all four cells. The C->D pair is diagnostic
    only (oracle arms, never operational). ``*_exact_blocks`` report the
    per-arm exact counts including the standalone B-exact count.
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
        a = cell.get("A_incumbent_L2_operational")
        b = cell.get("B_alt_L2_operational")
        c = cell.get("C_incumbent_L2_oracle")
        d = cell.get("D_alt_L2_oracle")
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


# ---------------------------------------------------------------------------
# Stage-B integrity gates (frozen §9 order; all true or BLOCKED).
# ---------------------------------------------------------------------------

def hazard_instrumentation_complete(records) -> bool:
    """All nine §7 scalars present with the frozen nullability per record."""
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
    gates["session_prior_identity"] = bool(
        session_prior_verified is not None
        and bool(session_prior_verified.get("passed")))
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
            and int(k1) == int(FROZEN_K1) and int(k2) == int(FROZEN_K2)
            and int(k1) + int(k2) == int(FROZEN_K_TOTAL)
            and str(hazard_pin.get("budget_literal")) == str(FROZEN_BUDGET_LITERAL))
    except (AttributeError, TypeError, ValueError):
        gates["k_literal_exact"] = False
    try:
        recomputed = p20m.verify_budget_literal(
            float(FROZEN_H_TOTAL), int(k_total), n=FROZEN_N,
            target_f=FROZEN_TARGET_F)
        gates["budget_literal_recomputed"] = bool(
            int(recomputed["k_total"]) == int(FROZEN_K_TOTAL)
            and str(recomputed["literal"]) == str(FROZEN_BUDGET_LITERAL))
    except (AttributeError, TypeError, ValueError):
        gates["budget_literal_recomputed"] = False
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


def l2_alt_maintain_2m_label(gates: dict) -> str:
    """Descriptive COMPLETE iff every integrity gate holds, else BLOCKED(first)."""
    failing = [g for g in INTEGRITY_GATE_ORDER if not gates.get(g, False)]
    if not failing:
        return COMPLETE_LABEL
    return f"BLOCKED({failing[0]})"


@dataclass(frozen=True, eq=False)
class L2AltMaintain2mRun:
    """In-memory P20O Stage-B run (also returned by the runner)."""

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
        "consumed_sessions": {
            "1m_pool": {"source_tag": CONSUMED_1M_SOURCE_TAG,
                        "frames": list(CONSUMED_1M_FRAME_RANGE)},
            "1p5m_session": {"source_tag": CONSUMED_1P5M_SOURCE_TAG,
                             "frames": list(CONSUMED_1P5M_FRAME_RANGE)},
            "2m_train_build": {"source_tag": FROZEN_SOURCE_TAG,
                               "frames": list(CONSUMED_2M_TRAIN_FRAME_RANGE)},
            "2m_hold": {"source_tag": FROZEN_SOURCE_TAG,
                        "frames": list(CONSUMED_2M_HOLD_FRAME_RANGE)},
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
        "hazard_fields": list(HAZARD_FIELDS),
        "u_domain_scalar_frozen_present": True,
        "frozen_command": FROZEN_COMMAND,
        "frozen_plan_manifest": manifest,
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
    }
    opf._write_json(out_path / "frozen_plan.json", plan)
    return plan


def _render_report(summary: dict) -> str:
    aggregates = summary.get("aggregates", {})
    maintenance = aggregates.get("maintenance", {})
    lines = [
        "# NB-Polar Phase 4-P20O maintain-confirmation of ALT-L2-LAPLACE-alpha1 "
        "at per-session disclosure on 2M VAL",
        "",
        f"- protocol: `{summary.get('analysis')}` (mode `{summary.get('mode')}`)",
        f"- source: `{summary.get('source')}`; N={summary.get('n')}; "
        f"K1={summary.get('k1')} K2={summary.get('k2')} K_total={summary.get('k_total')} "
        "(2M-session-derived, S2-i literal recomputation)",
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
        "descriptive maintain-confirmation reading on FIRST-USE 2M VAL: no "
        "recovery / FER / superiority / qualification / promotion / reliability "
        "claim is made, and the positive/negative branch decision stays with "
        "the main thread after acceptance.",
        "",
    ]
    return "\n".join(lines)


def run_l2_alt_maintain_2m(
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
) -> L2AltMaintain2mRun:
    """Execute the frozen P20O four-arm maintain-confirmation once; write five files.

    ``prior`` / ``alt_prior`` / ``dev_table`` are documented injected test
    seams; the frozen CLI passes only the frozen point, loads the Stage-A
    frozen 2M raw prior and alt table read-only exactly once each, loads
    the frozen 2M order file read-only behind the order-digest gate, and
    reads the 2M VAL parquet through its accepted loader exactly once.
    The V25 counts NPZ is never opened in Stage B. The construction swap
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
            "BLOCKED(alt_construction_budget_feasibility): Stage-A D2 outcome is "
            "ALT_CONSTRUCTION_BUDGET_INFEASIBLE (VAL untouched; no Stage-B run)"
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
    # (a), intra-file VAL-containment (b), consumed-1M / consumed-1.5M /
    # S2-ii declaration (c)-(e), then prior/alt/order-freeze/K-literal (f)-(g).
    if str(construction_digest) != str(FROZEN_CONSTRUCTION_DIGEST):
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = _gate_call("predecessor_construction_identity",
                          verify_predecessor_construction, construction,
                          expected_digest=construction_digest)
    identity = verified["record"]
    dev_source_pin = _gate_call("dev_block_range_identity",
                                verify_dev_source_identity_2m, dev_pairs)
    dev_pin = verify_val_containment(dev_frames, remainder_frames)
    disjoint_pin = verify_consumed_exclusions_2m(dev_frames, remainder_frames)
    manifest = _gate_call("dev_split_manifest_identity", verify_dev_manifest_2m,
                          manifest_path, source=source)
    order_pin = _gate_call(
        "order_derivation_identity", verify_stage_b_order_file_2m, order_file,
        expected_digest=order_digest,
        expected_prior_digest=str(FROZEN_SESSION_PRIOR_DIGEST),
        expected_k1=int(k1), expected_k2=int(k2), expected_k_total=int(k_total))
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
        raise ValueError("reopen refused: the single VAL parquet content open was consumed")

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
            raise FileNotFoundError(f"2M VAL pairs parquet not found: {dev_path_obj}")
        dev_stat_before = _stat_record(dev_path_obj)
        if dev_stat_before["size_bytes"] != FROZEN_DEV_PAIRS_SIZE:
            raise ValueError(
                "2M VAL pairs size mismatch before content open: "
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
        # ---- input 1: the single session-prior load + session_prior_identity.
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

        # ---- input 2: the single alt-table load + alt_l2_identity gate.
        if real_alt:
            alt_verified = _gate_call(
                "alt_l2_identity", verify_alt_l2_identity_2m, alt_prior_path,
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
            "alt_floor_rate": FROZEN_ALT_FLOOR_HIT_RATE,
        }

        # ---- S2: the K-literal display + alt-H descriptive literals.
        budget_literal = k_literals["budget_literal"]
        alt_h_literals = {
            "h1_inc": float(alt_verified["h1_inc"]),
            "h2_alt": float(alt_verified["h2_alt"]),
            "h_total_alt": float(alt_verified["h_total_alt"]),
        }

        # ---- input 3: the single VAL parquet content open, VAL rows only.
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
        formation = form_val_blocks(
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
                    "descriptive first-use 2M VAL maintain-confirmation of the "
                    "frozen ALT-L2-LAPLACE-alpha1 construction at the per-session "
                    "(2M-TRAIN-derived) disclosure point (N=32768, five VAL blocks "
                    "2187..2826) under the Stage-A 2M raw prior and the single "
                    "preregistered alt-L2 conditional; C/D are oracle-labelled "
                    "diagnostic controls, never an operational protocol or "
                    "deployable result; not real-frame FER, reconciliation "
                    "efficiency, leakage, key rate, scaling superiority, "
                    "qualification or promotion evidence; the CE-normalized "
                    "disclosure ratio is not qualification efficiency; undetected "
                    "is never success; no reliability, recovery or maintenance "
                    "claim is licensed; 2M is consumed by this packet regardless "
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
            seed = l2_alt_maintain_2m_seed_bits(
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
        outcome_label = l2_alt_maintain_2m_label(gates)
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
        return L2AltMaintain2mRun(summary=summary, records=tuple(records), gates=gates)
    except L2AltMaintain2mResourceError:
        raise
    except MemoryError as exc:
        raise L2AltMaintain2mResourceError(
            f"resource stop: MemoryError: {exc}") from exc


STAGE_A_ONLY_FLAGS = (
    "counts", "alpha", "target_f", "deriv_seeds",
    "out_prior", "out_orders", "out_alt",
)
STAGE_A_REQUIRED_FLAGS = ("counts", "alpha", "target_f", "deriv_seeds",
                          "out_prior", "out_orders", "out_alt")
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
        prog="nbpolar-p20o-2m-maintain-confirmation",
        description=(
            "NB-Polar Phase 4-P20O maintain-confirmation of ALT-L2-LAPLACE-"
            "alpha1 on first-use 2M VAL: --derive runs the Stage-A derivation "
            "with the SINGLE protected open of the 2M TRAIN counts array; "
            "otherwise all Stage-B flags are required (frozen command, no "
            "production default)"
        ),
    )
    parser.add_argument("--derive", action="store_true",
                        help="Stage-A derivation mode (all Stage-A flags required)")
    parser.add_argument("--counts", default=None,
                        help="Stage-A canonical V25 counts npz (2M array only)")
    parser.add_argument("--alpha", default=None, type=float,
                        help="Stage-A construction marker; only the frozen 1")
    parser.add_argument("--target-f", default=None, type=float, dest="target_f",
                        help="Stage-A frozen budget target; only 1.3")
    parser.add_argument("--deriv-seeds", default=None, type=int, nargs=4,
                        dest="deriv_seeds", help="Stage-A frozen derivation seeds")
    parser.add_argument("--out-prior", default=None, dest="out_prior")
    parser.add_argument("--out-orders", default=None, dest="out_orders")
    parser.add_argument("--out-alt", default=None, dest="out_alt")
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
            missing = [name for name in STAGE_A_REQUIRED_FLAGS
                       if getattr(args, name) is None]
            missing += [name for name in SHARED_FLAGS
                        if getattr(args, name) is None]
            if missing:
                raise ValueError(
                    "missing required Stage-A flags: " + ",".join(sorted(missing))
                    + "; refusing before any read or write"
                )
            result = run_derive_stage_a(
                counts_path=args.counts, source=args.source, alpha=args.alpha,
                floor=args.floor, n=args.n, target_f=args.target_f,
                seeds=tuple(args.deriv_seeds), out_prior_path=args.out_prior,
                out_orders_path=args.out_orders, out_alt_path=args.out_alt)
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
        run = run_l2_alt_maintain_2m(
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
            "integrity_all_pass": summary["integrity_all_pass"],
            "outcome_label": summary["outcome_label"],
            "out_root": args.out_dir,
        }, sort_keys=True))
        return 0
    except (ValueError, FileExistsError, OSError,
            L2AltMaintain2mContractError) as exc:
        print(f"nbpolar phase4-p20o 2m maintain refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL_NAME", "MODE", "Q", "ALPHA", "N_BOB", "FROZEN_N", "FROZEN_SOURCE",
    "FROZEN_SOURCE_TAG", "FROZEN_FLOOR", "FROZEN_ALPHA", "FROZEN_TARGET_F",
    "NORM_TOL", "FROZEN_HAZARD_R", "FROZEN_PUBLIC_CONTROL_BITS",
    "FROZEN_RAW_INPUT_BITS", "FROZEN_COUNTS_PATH", "FROZEN_COUNTS_PATH_CANONICAL_REL",
    "FROZEN_COUNTS_KEY", "FROZEN_DEV_FRAME_RANGE", "FROZEN_DEV_FRAMES",
    "FROZEN_DEV_PAIRS", "FROZEN_BLOCK_COUNT", "FROZEN_BLOCK_FRAMES",
    "FROZEN_PAIRS_PER_FRAME", "FROZEN_SYMBOLS_PER_BLOCK", "FROZEN_BLOCK_RANGES",
    "FROZEN_REMAINDER_FRAME_RANGE", "FROZEN_REMAINDER_FRAMES",
    "FROZEN_REMAINDER_SYMBOLS", "INTRA_FILE_VAL_FRAME_RANGE",
    "INTRA_FILE_HOLD_FRAME_RANGE", "CONSUMED_2M_TRAIN_FRAME_RANGE",
    "CONSUMED_2M_HOLD_FRAME_RANGE", "FROZEN_BUILD_FRAME_RANGE",
    "FROZEN_MANIFEST_TRAIN_FRAMES", "FROZEN_MANIFEST_TRAIN_PAIRS",
    "FROZEN_MANIFEST_VAL_FRAMES", "FROZEN_MANIFEST_VAL_PAIRS",
    "FROZEN_MANIFEST_HOLD_FRAMES", "FROZEN_MANIFEST_HOLD_PAIRS",
    "FROZEN_DEV_PAIRS_PATH", "FROZEN_DEV_PAIRS_SIZE", "FROZEN_DEV_PAIRS_SHA256",
    "REFUSED_1M_DEV_PAIRS_PATH", "REFUSED_1P5M_DEV_PAIRS_PATH",
    "FROZEN_DEV_BUILD_MANIFEST_PATH", "FROZEN_CONSTRUCTION_PATH",
    "FROZEN_CONSTRUCTION_DIGEST", "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA",
    "PAIRS_LOADER_IDENTITY", "FROZEN_TAG_MASTER", "FROZEN_CHUNK_ROWS",
    "FROZEN_TAG_BITS", "SEED_PREFIX", "FROZEN_DERIVATION_SEEDS",
    "FROZEN_TRAIN_BLOCKS_PER_SEED", "FROZEN_TRAIN_BLOCKS_TOTAL",
    "FROZEN_TRAIN_GENIE_CALLS", "FROZEN_ORDER_PROGRAM_PIN", "FROZEN_PRIOR_PATH",
    "FROZEN_ORDER_FILE_PATH", "FROZEN_ALT_PATH", "FROZEN_OUT_ROOT",
    "OUTPUT_FILES", "ATTEMPT_CONSUMPTION_POINT", "COMPLETE_LABEL",
    "RAW_PRIOR_NPZ_KEYS", "ALT_L2_NPZ_KEYS", "FROZEN_ARM_NAMES",
    "OPERATIONAL_ARM_NAMES", "ORACLE_ARM_NAMES", "PLANNED_SC_CALLS",
    "PLANNED_TAG_INVOCATIONS", "PLANNED_RECORDS", "INTEGRITY_GATE_ORDER",
    "HAZARD_FIELDS", "U_DOMAIN_FIELD", "FROZEN_COMMAND", "FROZEN_SESSION_PRIOR_DIGEST",
    "FROZEN_H1", "FROZEN_H2", "FROZEN_H_TOTAL", "FROZEN_BUDGET_LITERAL",
    "FROZEN_K_TOTAL", "FROZEN_K1", "FROZEN_K2", "FROZEN_ORDER_DIGEST",
    "FROZEN_ALT_DIGEST", "FROZEN_ALT_FLOOR_HITS", "FROZEN_ALT_FLOOR_HIT_RATE",
    "FROZEN_ALT_ZERO_COLUMNS", "FROZEN_ALT_F_ALT_MIN", "FROZEN_ALT_F_ALT_MAX",
    "FROZEN_ALT_H1_INC", "FROZEN_ALT_H2_ALT", "FROZEN_ALT_H_TOTAL_ALT",
    "FROZEN_ALT_CE_INSAMPLE", "FROZEN_INCUMBENT_CE_INSAMPLE",
    "FROZEN_ALT_IDEAL_LENGTH_BITS", "FROZEN_D2_FEASIBLE",
    "FROZEN_COUNTS_ARRAY_SHA256", "FROZEN_COUNTS_TOTAL",
    "FROZEN_SESSION_PRIOR_FLOOR_HITS", "FROZEN_SESSION_PRIOR_FLOOR_HIT_RATE",
    "FROZEN_SESSION_PRIOR_ZERO_COLUMNS", "FROZEN_ORDER_TRAIN_RESIDUAL",
    "FROZEN_ALT_P1_EQUALITY_MAX_ABS_DIFF", "RSS_LIMIT_BYTES", "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S", "ULIMIT_VIRTUAL_KIB", "L2AltMaintain2mContractError",
    "L2AltMaintain2mResourceError", "ArmSpec", "L2AltMaintain2mRun",
    "pins_frozen", "pins_are_frozen", "planned_totals", "frozen_arm_table",
    "check_frozen_arm_table", "check_k_literals", "frozen_command",
    "load_counts_2m", "raw_prior_arrays", "alt_tables_2m",
    "feasibility_literals_2m", "run_derive_stage_a",
    "verify_dev_source_identity_2m", "verify_val_containment",
    "verify_consumed_exclusions_2m", "verify_dev_manifest_2m",
    "verify_session_prior_2m", "verify_alt_l2_arrays_2m",
    "verify_alt_l2_identity_2m", "verify_stage_b_order_file_2m",
    "form_val_blocks", "l2_alt_maintain_2m_seed_bits", "_l2_hazard_diagnostics",
    "hazard_instrumentation_complete", "oracle_isolation_ok",
    "maintenance_diagnostics", "build_aggregates", "l2_alt_maintain_2m_label",
    "run_l2_alt_maintain_2m", "build_parser", "main", "STAGE_A_ONLY_FLAGS",
    "SHARED_FLAGS", "STAGE_B_ONLY_FLAGS", "STAGE_B_FLAGS",
]
