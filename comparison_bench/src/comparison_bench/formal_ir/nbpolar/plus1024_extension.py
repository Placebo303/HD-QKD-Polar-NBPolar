"""NB-Polar Phase 4-P20F N=32768 +1024 extension on the last same-file TRAIN tranche (Stage A, frozen).

Zero-tuning extension confirmation (strategy stage 2, second confirmation
round): with the frozen Model-F concentration prior, the ``1e-15``
floor, the accepted P16 construction order, the frozen kernel,
representation, transform and greedy SC all carried over byte-identical
from P20C/P20E, and the SAME +1024 L2 order-prefix step
(``K2 6492 -> 7516``) on ``B1_L2plus`` unchanged, does +1024 maintain
exact on the remaining NEW real development blocks -- and does a
P20C-style restoration event (B0 fail -> B1 exact) get a second
opportunity to replicate, or not? Nothing is varied: the only
deliberate differences from P20C/P20E are the new-block population and
the new P20F tag domain, both provenance/identity changes, never
algorithm changes.

Three hardcoded arms (never CLI-tunable, never extensible):

- ``B0_sc_base``: frozen greedy SC at base disclosure/construction via
  the accepted ``run_operational_block`` (operational, 2 SC + 1 tag per
  block).
- ``B1_L2plus``: frozen greedy SC at base + the carried-over +1024 L2
  step via frozen-order-prefix extension, all else identical, via the
  accepted ``run_operational_block`` (operational, the confirmation
  candidate; 2 SC + 1 tag per block).
- ``B2_true_l1_diagnostic``: true-L1-conditioned L2 at BASE disclosure
  via the accepted ``run_oracle_control_block`` (provenance
  ``ORACLE_TRUE_L1_CONTROL``, deployable=false, excluded from every
  operational aggregate; never described as a correction result).

Development population: same-file TRAIN subrange frames ``768..1151``
of the same registered 1M source (same pairs file identity as
P18/P19/P20B/P20C/P20E; the closed P18/P19 HOLD blocks ``1600..1983``
select nothing and are never re-entered; the consumed P20B VAL pool
``1200..1599`` is never re-entered; the consumed P20C DEV blocks
``0..383`` and the consumed P20E DEV blocks ``384..767`` are never
re-entered). Three NEW DEV blocks ``768..895`` / ``896..1023`` /
``1024..1151`` plus the declared never-used remainder ``1152..1199``.

Stage A only: this module is implementation plus focused injected tests.
The Stage-B evidence root stays absent until an independent Pre-EXECUTE
PASS plus a separate pasted Stage-B authorization. Zero protected reads,
zero real-data decoder execution, zero frozen-output writes outside the
run root, no commit or push, no
self-acceptance.
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

from ..shared import canonical_event, toeplitz_tag
from ..v35_algorithm_development import load_v25_channel_counts
from ...io.pairs_loader import load_pairs_table, normalize_pair_columns
from . import operational_f13 as opf
from . import holdout_microcheck as hm
from . import operational_f13_replication as opr
from . import holdout_backoff_diagnostic as hbd
from .algebra import make_gf32
from .prior import (
    Provenance,
    build_p1_metrics,
    derive_p1,
    derive_p2,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from .target_construction import (
    TargetPopulationContractError,
    target_preconditions,
)
from .transform import polar_transform
from .two_layer import (
    DISCLOSED_BITS_PER_COORDINATE,
    LABEL_SCALE,
    TAG_BITS,
    labels_to_bits,
    seed_bits_for,
)

# Reused accepted contracts (read-only; never reimplemented here).
run_operational_block = opf.run_operational_block
_decode_layer = opf._decode_layer
classify_operational_outcome = opf.classify_operational_outcome
run_oracle_control_block = hbd.run_oracle_control_block
OracleControlResult = hbd.OracleControlResult
verify_predecessor_construction = opr.verify_predecessor_construction
verify_split_manifest = hm.verify_split_manifest
holdout_nll_bits = hm.holdout_nll_bits
raw_symbol_error_rate = hm.raw_symbol_error_rate
form_holdout_blocks = hm.form_holdout_blocks
polar_transform_fn = polar_transform
make_gf32_fn = make_gf32
toeplitz_tag_fn = toeplitz_tag
build_p1_metrics_fn = build_p1_metrics
gather_p2_metrics_fn = gather_p2_metrics
probs_to_symbol_metric_fn = probs_to_symbol_metric

PROTOCOL_NAME = "nbpolar-p20f-plus1024-extension"
MODE = "dev-plus1024-extension"

Q = opf.Q
ALPHA = opf.ALPHA
N_BOB = hm.N_BOB
FROZEN_N = 32768
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
FROZEN_K1 = 319
FROZEN_K2 = 6492
FROZEN_K_TOTAL = 6811
# The single frozen disclosure factor (Stage-A freeze, never tuned
# afterwards): B1 discloses FROZEN_L2_DELTA_K2 = +1024 L2 symbols beyond
# the frozen base by frozen-order-prefix extension (the disclosed L2 set
# is the first FROZEN_K2_B1 positions of the frozen P16 L2 order).
FROZEN_L2_DELTA_K2 = 1024
FROZEN_K2_B1 = 7516  # 6492 + 1024
FROZEN_K_TOTAL_B1 = 7835  # 319 + 7516
FROZEN_B1_KEY_BIT_DELTA = 5120  # 5 * 1024 vs base
FROZEN_LEAKAGE_BITS = 34119  # 5 * 6811 + 64 (B0 base operational)
FROZEN_B1_LEAKAGE_BITS = 39239  # 5 * 7835 + 64 (B1 operational, +1024 L2)
FROZEN_CONTROL_LEAKAGE_BITS = 32524  # 5 * 6492 + 64 (oracle arm, K1 = 0)
FROZEN_PUBLIC_CONTROL_BITS = seed_bits_for(FROZEN_N)  # 327743
FROZEN_RAW_INPUT_BITS = 10 * FROZEN_N  # 327680 per block

DISCLOSURE_RULE = (
    "single preregistered L2 disclosure step: B1_L2plus discloses "
    "FROZEN_L2_DELTA_K2 = +1024 L2 symbols beyond the frozen base "
    "(K2 6492 -> 7516; K_total 6811 -> 7835) by FROZEN-ORDER-PREFIX "
    "EXTENSION -- the disclosed L2 set is the first 7516 positions of "
    "the frozen P16 L2 order (positions fixed by the construction file, "
    "never selected on closed blocks, the consumed VAL pool, or DEV "
    "data); B0 and B2 stay at base disclosure; the step doubles P19's "
    "probed +512 increment; no second step (no B1b) without a new packet"
)

# Development population: same-file TRAIN subrange frames of the registered
# 1M source. Same pairs-file identity as P18/P19/P20B/P20C/P20E; disjoint from
# closed HOLD 1600..1983 AND from the consumed P20B VAL pool 1200..1599
# AND from the consumed P20C DEV blocks 0..383 AND from the consumed P20E
# DEV blocks 384..767.
FROZEN_DEV_FRAME_RANGE = (768, 1151)
FROZEN_DEV_FRAMES = 384
FROZEN_DEV_PAIRS = 98304
FROZEN_BLOCK_COUNT = 3
FROZEN_BLOCK_FRAMES = 128
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_BLOCK_RANGES = ((768, 895), (896, 1023), (1024, 1151))
FROZEN_REMAINDER_FRAME_RANGE = (1152, 1199)
FROZEN_REMAINDER_FRAMES = 48
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
CLOSED_HOLD_FRAME_RANGE = (1600, 1983)  # P18/P19 blocks; never re-entered
CONSUMED_VAL_FRAME_RANGE = (1200, 1599)  # P20B pool; never re-entered
CONSUMED_P20C_DEV_FRAME_RANGE = (0, 383)  # P20C DEV blocks; never re-entered
CONSUMED_P20E_DEV_FRAME_RANGE = (384, 767)  # P20E DEV blocks; never re-entered
# Split-manifest TRAIN pool hosting the DEV subrange (same manifest as
# P18/P19/P20B/P20C; TRAIN 0..1199 by elimination with accepted VAL/HOLD).
FROZEN_MANIFEST_TRAIN_FRAMES = 1200
FROZEN_MANIFEST_TRAIN_PAIRS = 307200

FROZEN_TAG_MASTER = 2026092200
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = TAG_BITS  # 64
SEED_PREFIX = "nbpolar-p20f-plus1024-extension-seed"

OPERATIONAL_PROVENANCE = hbd.OPERATIONAL_PROVENANCE
ORACLE_PROVENANCE = hbd.ORACLE_PROVENANCE


@dataclass(frozen=True)
class ArmSpec:
    """One frozen P20F arm (never CLI-tunable, never extensible)."""

    name: str
    kind: str  # "operational" | "oracle_control"
    k1: int
    k2: int
    leakage_bits: int
    provenance: str


FROZEN_ARMS = (
    ArmSpec("B0_sc_base", "operational", FROZEN_K1, FROZEN_K2,
            FROZEN_LEAKAGE_BITS, OPERATIONAL_PROVENANCE),
    ArmSpec("B1_L2plus", "operational", FROZEN_K1, FROZEN_K2_B1,
            FROZEN_B1_LEAKAGE_BITS, OPERATIONAL_PROVENANCE),
    ArmSpec("B2_true_l1_diagnostic", "oracle_control", 0, FROZEN_K2,
            FROZEN_CONTROL_LEAKAGE_BITS, ORACLE_PROVENANCE),
)
FROZEN_ARM_NAMES = tuple(spec.name for spec in FROZEN_ARMS)
OPERATIONAL_ARM_NAMES = tuple(spec.name for spec in FROZEN_ARMS if spec.kind == "operational")
ORACLE_ARM_NAME = FROZEN_ARMS[-1].name
ARM_BY_NAME = {spec.name: spec for spec in FROZEN_ARMS}

# Frozen design accounting: 3 blocks x (2 + 2 + 1) SC, 9 tags.
PLANNED_SC_CALLS = FROZEN_BLOCK_COUNT * (2 + 2 + 1)  # 15
PLANNED_TAG_INVOCATIONS = len(FROZEN_ARMS) * FROZEN_BLOCK_COUNT  # 9
PLANNED_RECORDS = len(FROZEN_ARMS) * FROZEN_BLOCK_COUNT  # 9
FROZEN_TOTAL_KEY_DEPENDENT_BITS = sum(
    FROZEN_BLOCK_COUNT * spec.leakage_bits for spec in FROZEN_ARMS
)  # 317646 = 3*34119 + 3*39239 + 3*32524
FROZEN_TOTAL_PUBLIC_CONTROL_BITS = PLANNED_TAG_INVOCATIONS * FROZEN_PUBLIC_CONTROL_BITS

EXPECTED_NPZ_BYTES = hm.EXPECTED_NPZ_BYTES
FROZEN_COUNTS_PATH = hm.FROZEN_COUNTS_PATH
FROZEN_DEV_PAIRS_PATH = hm.FROZEN_HOLD_PAIRS_PATH  # same file, TRAIN frames selected
FROZEN_MANIFEST_PATH = hm.FROZEN_MANIFEST_PATH
FROZEN_MANIFEST_SCHEMA = hm.FROZEN_MANIFEST_SCHEMA
FROZEN_CONSTRUCTION_PATH = hm.FROZEN_CONSTRUCTION_PATH
FROZEN_CONSTRUCTION_DIGEST = hm.FROZEN_CONSTRUCTION_DIGEST
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20F-PLUS1024-EXTENSION/"
    "plus1024_extension"
)
NPZ_LOADER_IDENTITY = hm.NPZ_LOADER_IDENTITY
PAIRS_LOADER_IDENTITY = hm.PAIRS_LOADER_IDENTITY

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 600.0
EXTERNAL_TIMEOUT_S = 600
ULIMIT_VIRTUAL_KIB = 2097152

OUTCOMES = opf.OUTCOMES
COMPLETE_LABEL = "TARGET_EMPIRICAL_N32768_DEV_PLUS1024_EXTENSION_COMPLETE"

SUPPORT_RULE = (
    "f = counts / column totals; every cell below 1e-15 replaced by 1e-15; "
    "columns renormalized; p_b = column totals / total count; "
    "P1/P2 = accepted derive_p1/derive_p2(f) under A=32*U1+U2; "
    "no lambda, backoff, tuning, floor scan or fitting (exact P7 rule)"
)
DEV_BLOCK_RULE = (
    "TRAIN development formation (P18 pattern, P20F ranges): sort TRAIN rows by "
    "(frame_id, pair_idx); require exactly 384 frames 768..1151, 256 rows "
    "per frame, pair_idx 0..255 and symbols 0..1023; blocks 768..895 / "
    "896..1023 / 1024..1151 (128 frames = 32768 pairs each); frames "
    "1152..1199 are the declared never-used remainder; closed HOLD 1600..1983, "
    "consumed VAL 1200..1599, consumed P20C DEV 0..383 and consumed P20E DEV "
    "384..767 never selected; "
    "no shuffle, resampling, "
    "overlap, padding, pooling or fitting"
)
ARM_RULE = (
    "three frozen arms in block-major order B0_sc_base / B1_L2plus / "
    "B2_true_l1_diagnostic per block; B0 and B1 run the frozen greedy SC "
    "(2 SC + 1 tag per block) with identical prior/floor/order/kernel/ "
    "representation/SC; B0 discloses the frozen base K1=319/K2=6492 while "
    "B1 discloses K1=319/K2=7516 (the single +1024 L2 order-prefix step); "
    "B2 discloses K2 only and runs one oracle-conditioned L2 SC; 15 SC "
    "calls and 9 tags total; B2 carries ORACLE_TRUE_L1_CONTROL provenance, "
    "deployable=false, and is excluded from every operational aggregate; "
    "arms are constants, never CLI-tunable"
)
NLL_RULE = (
    "per block under the fixed floor-1e-15 TRAIN prior: "
    "l1_nll_bits = sum_i -log2 p1[high_i, bob_i]; "
    "l2_nll_bits = sum_i -log2 p2[high_i, bob_i, low_i]; "
    "total_nll_bits = l1 + l2 (bits per 32768-pair block); tags and "
    "truth never enter selection (there is no selection in this packet)"
)
RATIO_RULE = (
    "disclosure_ce_ratio = design leakage / true block total NLL bits is a "
    "sample cross-entropy-normalized disclosure ratio and is explicitly NOT "
    "qualification reconciliation efficiency"
)
TRUTH_BOUNDARY = (
    "Alice truth enters operational arms only through disclosed U values, "
    "tag construction and scoring (accepted run_operational_block boundary "
    "and sentinel, identical for B0 and B1); B2 additionally conditions "
    "its L2 metric on the true high layer and is provenance-isolated"
)
NO_THRESHOLD_RULE = (
    "there is no exact-count, FER, winner, monotonicity, superiority or "
    "qualification threshold and no recovery gate of any kind; any exact "
    "count (including 0/9 and any partial restoration) is descriptive "
    "COMPLETE when integrity holds; "
    "only integrity/resource failures produce BLOCKED(<earliest gate>)"
)
CLAIM_SCOPE = (
    "descriptive zero-tuning +1024 confirmation on NEW real development "
    "blocks (same-file TRAIN subrange, N=32768, three new DEV blocks); B2 is an "
    "oracle-labelled diagnostic control, never an operational protocol or "
    "deployable rate; not real-frame FER, reconciliation efficiency, "
    "leakage, key rate, scaling superiority, qualification or promotion "
    "evidence; the CE-normalized disclosure ratio is not qualification "
    "efficiency; undetected is never success"
)
OUTCOME_PRECEDENCE = list(hbd.OUTCOME_PRECEDENCE)

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "dev_split_manifest_identity",
    "dev_block_range_identity",
    "target_population_contract",
    "dev_population_exact",
    "blocks_exact_with_declared_remainder",
    "nine_records_exact",
    "sc_calls_exact",
    "tags_exact",
    "orders_valid_k_prefixes_within_registered_arms",
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
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.plus1024_extension "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --floor 1e-15 "
    "--n 32768 --k1 319 --k2 6492 "
    f"--construction {FROZEN_CONSTRUCTION_PATH} --construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
    f"--dev-pairs {FROZEN_DEV_PAIRS_PATH} "
    "--dev-frames 768 1151 --block-frames 128 --remainder-frames 1152 1199 "
    "--tag-master 2026092200 --chunk-rows 512 --tag-bits 64 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)

OUTPUT_FILES = (
    "frozen_plan.json",
    "input_and_predecessor_identity.json",
    "per_block_arm_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)
ATTEMPT_CONSUMPTION_POINT = "first protected content open (load_v25_channel_counts)"

# Process-level one-open guards: set at the first content open, never cleared.
_NPZ_CONTENT_OPENED = False
_DEV_PARQUET_CONTENT_OPENED = False


class Plus1024ExtensionContractError(ValueError):
    """Pre-open DEV-population/formation failure: BLOCKED(<earliest gate>)."""


class Plus1024ExtensionResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


def _check_floor(value) -> float:
    out = hm._check_floor(value)
    if out != FROZEN_FLOOR:
        raise ValueError(f"frozen point requires floor={FROZEN_FLOOR}, got {out}")
    return out


def _check_base_k1(value) -> int:
    out = opf._as_int(value, "k1", minimum=0)
    if out != FROZEN_K1:
        raise ValueError(f"frozen point requires k1={FROZEN_K1}, got {out}")
    return out


def _check_base_k2(value) -> int:
    out = opf._as_int(value, "k2", minimum=0)
    if out != FROZEN_K2:
        raise ValueError(f"frozen point requires k2={FROZEN_K2}, got {out}")
    return out


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


def check_frozen_arm_table() -> dict:
    """Fail-closed pin of the three frozen arms and their design accounting.

    Pure code-level check (no I/O): arm order, K values, the single +1024
    L2 prefix-extension step, leakage arithmetic, oracle label and the 15
    SC / 9 tag design totals. Any drift raises before any root exists.
    """
    if len(FROZEN_ARMS) != 3:
        raise ValueError(f"frozen arm table must hold 3 arms, got {len(FROZEN_ARMS)}")
    if FROZEN_ARM_NAMES != ("B0_sc_base", "B1_L2plus", "B2_true_l1_diagnostic"):
        raise ValueError(f"frozen arm order drifted: {FROZEN_ARM_NAMES!r}")
    base = FROZEN_ARMS[0]
    if (base.kind, base.k1, base.k2, base.leakage_bits, base.provenance) != (
        "operational", FROZEN_K1, FROZEN_K2, FROZEN_LEAKAGE_BITS,
        OPERATIONAL_PROVENANCE,
    ):
        raise ValueError("frozen B0_sc_base arm drifted from base")
    plus = FROZEN_ARMS[1]
    if (plus.kind, plus.k1, plus.k2, plus.leakage_bits, plus.provenance) != (
        "operational", FROZEN_K1, FROZEN_K2_B1, FROZEN_B1_LEAKAGE_BITS,
        OPERATIONAL_PROVENANCE,
    ):
        raise ValueError("frozen B1_L2plus arm drifted from base + 1024")
    if int(plus.k2) - int(base.k2) != FROZEN_L2_DELTA_K2:
        raise ValueError("frozen L2 disclosure step must be exactly +1024")
    if int(plus.leakage_bits) - int(base.leakage_bits) != FROZEN_B1_KEY_BIT_DELTA:
        raise ValueError("frozen B1 key-bit delta must be exactly +5120 vs base")
    control = FROZEN_ARMS[2]
    if (control.kind, control.k1, control.k2, control.provenance) != (
        "oracle_control", 0, FROZEN_K2, ORACLE_PROVENANCE
    ):
        raise ValueError("frozen B2_true_l1_diagnostic arm drifted")
    if FROZEN_K1 + FROZEN_K2 != FROZEN_K_TOTAL:
        raise ValueError("frozen base K1+K2 != K_total")
    if FROZEN_K2_B1 != FROZEN_K2 + FROZEN_L2_DELTA_K2:
        raise ValueError("frozen B1 K2 != base K2 + 1024")
    if FROZEN_K1 + FROZEN_K2_B1 != FROZEN_K_TOTAL_B1:
        raise ValueError("frozen B1 K1+K2 != B1 K_total")
    if FROZEN_LEAKAGE_BITS != DISCLOSED_BITS_PER_COORDINATE * FROZEN_K_TOTAL + TAG_BITS:
        raise ValueError("frozen base leakage != 5*(K1+K2)+64")
    if FROZEN_B1_LEAKAGE_BITS != DISCLOSED_BITS_PER_COORDINATE * FROZEN_K_TOTAL_B1 + TAG_BITS:
        raise ValueError("frozen B1 leakage != 5*(K1+K2_B1)+64")
    if FROZEN_CONTROL_LEAKAGE_BITS != DISCLOSED_BITS_PER_COORDINATE * FROZEN_K2 + TAG_BITS:
        raise ValueError("frozen control leakage != 5*K2+64")
    if PLANNED_SC_CALLS != 15:
        raise ValueError(f"frozen design must plan 15 SC calls, got {PLANNED_SC_CALLS}")
    if PLANNED_TAG_INVOCATIONS != 9:
        raise ValueError(f"frozen design must plan 9 tags, got {PLANNED_TAG_INVOCATIONS}")
    if FROZEN_L2_DELTA_K2 != 1024:
        raise ValueError(f"frozen L2 disclosure step must be +1024, got {FROZEN_L2_DELTA_K2}")
    h_total = float(opf.EXPECTED_H1 + opf.EXPECTED_H2)
    f_base = float(FROZEN_LEAKAGE_BITS / (FROZEN_N * h_total))
    if f_base > FROZEN_TARGET_F:
        raise ValueError("frozen base arm exceeds the accepted planning f<=1.3 budget")
    cap_ratio = float(FROZEN_LEAKAGE_BITS / FROZEN_RAW_INPUT_BITS)
    if not cap_ratio < 0.5:
        raise ValueError("frozen cap must sit well below raw input bits")
    b1_ratio = float(FROZEN_B1_LEAKAGE_BITS / FROZEN_RAW_INPUT_BITS)
    if not b1_ratio < 0.5:
        raise ValueError("frozen B1 cap must sit well below raw input bits")
    return {
        "arms": [spec.name for spec in FROZEN_ARMS],
        "planned_sc_calls": PLANNED_SC_CALLS,
        "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
        "l2_delta_k2": FROZEN_L2_DELTA_K2,
        "b1_k2": FROZEN_K2_B1,
        "base_leakage_bits": FROZEN_LEAKAGE_BITS,
        "b1_leakage_bits": FROZEN_B1_LEAKAGE_BITS,
        "b1_key_bit_delta_vs_base": FROZEN_B1_KEY_BIT_DELTA,
        "cap_vs_raw_ratio": cap_ratio,
        "b1_cap_vs_raw_ratio": b1_ratio,
    }


def verify_dev_block_identity() -> dict:
    """Pin the P20F DEV ranges and their quadruple disjointness gate.

    Pure code-level check (no I/O). The DEV ranges must overlap NONE of
    the consumed P20C DEV blocks 0..383, the consumed P20E DEV blocks
    384..767, the consumed P20B VAL pool 1200..1599, or the closed
    P18/P19 blocks 1600..1983; any overlap raises before any root
    exists and before either protected content open, consuming nothing.
    The consumed-P20C check runs first, then the consumed-P20E check,
    then the consumed-VAL check, then the closed-HOLD check: all four
    are safety properties and must fire even when the ranges also
    mismatch their literals.
    """
    p20c_first, p20c_last = CONSUMED_P20C_DEV_FRAME_RANGE
    for start, end in [tuple(r) for r in FROZEN_BLOCK_RANGES]:
        if not (end < p20c_first or start > p20c_last):
            raise ValueError(
                "P20F DEV block range "
                f"{start}..{end} overlaps consumed P20C DEV {p20c_first}..{p20c_last}"
            )
    rem_first, rem_last = [int(v) for v in FROZEN_REMAINDER_FRAME_RANGE]
    if not (rem_last < p20c_first or rem_first > p20c_last):
        raise ValueError("P20F DEV remainder overlaps consumed P20C DEV data")
    p20e_first, p20e_last = CONSUMED_P20E_DEV_FRAME_RANGE
    for start, end in [tuple(r) for r in FROZEN_BLOCK_RANGES]:
        if not (end < p20e_first or start > p20e_last):
            raise ValueError(
                "P20F DEV block range "
                f"{start}..{end} overlaps consumed P20E DEV {p20e_first}..{p20e_last}"
            )
    if not (rem_last < p20e_first or rem_first > p20e_last):
        raise ValueError("P20F DEV remainder overlaps consumed P20E DEV data")
    consumed_first, consumed_last = CONSUMED_VAL_FRAME_RANGE
    for start, end in [tuple(r) for r in FROZEN_BLOCK_RANGES]:
        if not (end < consumed_first or start > consumed_last):
            raise ValueError(
                "P20F DEV block range "
                f"{start}..{end} overlaps consumed VAL {consumed_first}..{consumed_last}"
            )
    if not (rem_last < consumed_first or rem_first > consumed_last):
        raise ValueError("P20F DEV remainder overlaps consumed VAL data")
    closed_first, closed_last = CLOSED_HOLD_FRAME_RANGE
    for start, end in [tuple(r) for r in FROZEN_BLOCK_RANGES]:
        if not (end < closed_first or start > closed_last):
            raise ValueError(
                "P20F DEV block range "
                f"{start}..{end} overlaps closed HOLD {closed_first}..{closed_last}"
            )
    if not (rem_last < closed_first or rem_first > closed_last):
        raise ValueError("P20F DEV remainder overlaps closed HOLD data")
    checks = {
        "n": FROZEN_N == int(hm.FROZEN_N),
        "base_k1": FROZEN_K1 == int(hm.FROZEN_K1),
        "base_k2": FROZEN_K2 == int(hm.FROZEN_K2),
        "block_count": FROZEN_BLOCK_COUNT == int(hm.FROZEN_BLOCK_COUNT),
        "block_frames": FROZEN_BLOCK_FRAMES == int(hm.FROZEN_BLOCK_FRAMES),
        "symbols_per_block": FROZEN_SYMBOLS_PER_BLOCK == int(hm.FROZEN_SYMBOLS_PER_BLOCK),
        "dev_frame_range": tuple(FROZEN_DEV_FRAME_RANGE) == (768, 1151),
        "dev_frames": FROZEN_DEV_FRAMES == 384,
        "dev_pairs": FROZEN_DEV_PAIRS == 98304,
        "block_ranges": tuple(tuple(r) for r in FROZEN_BLOCK_RANGES)
        == ((768, 895), (896, 1023), (1024, 1151)),
        "remainder_frame_range": tuple(FROZEN_REMAINDER_FRAME_RANGE) == (1152, 1199),
        "remainder_symbols": FROZEN_REMAINDER_SYMBOLS == 12288,
    }
    failing = sorted(name for name, ok in checks.items() if not ok)
    if failing:
        raise ValueError("P20F DEV block-range identity mismatch: " + ",".join(failing))
    return {
        "dev_frame_range": list(FROZEN_DEV_FRAME_RANGE),
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "remainder_frame_range": list(FROZEN_REMAINDER_FRAME_RANGE),
        "closed_hold_frame_range": list(CLOSED_HOLD_FRAME_RANGE),
        "consumed_val_frame_range": list(CONSUMED_VAL_FRAME_RANGE),
        "consumed_p20c_dev_frame_range": list(CONSUMED_P20C_DEV_FRAME_RANGE),
        "consumed_p20e_dev_frame_range": list(CONSUMED_P20E_DEV_FRAME_RANGE),
        "consumed_p20c_disjoint": True,
        "closed_disjoint": True,
        "consumed_disjoint": True,
        "verified": True,
    }


def verify_dev_manifest(path, *, source: str = FROZEN_SOURCE) -> dict:
    """Verify the V25 split manifest declares the TRAIN development pool.

    JSON read only; no protected content open. Reuses the accepted HOLD
    manifest identity (schema, source tag, 400 HOLD frames / 102400 pairs)
    and additionally requires the 1200-frame / 307200-pair TRAIN pool that
    hosts the P20F DEV subrange (frames 768..1151). Any mismatch raises
    before any root exists.
    """
    manifest = verify_split_manifest(path, source=source)
    if int(manifest.get("train_frames", -1)) != FROZEN_MANIFEST_TRAIN_FRAMES or int(
        manifest.get("train_pairs", -1)
    ) != FROZEN_MANIFEST_TRAIN_PAIRS:
        raise ValueError(
            "dev split manifest identity: 1M TRAIN population "
            f"{manifest.get('train_frames')} frames / {manifest.get('train_pairs')} pairs "
            f"!= frozen {FROZEN_MANIFEST_TRAIN_FRAMES} / {FROZEN_MANIFEST_TRAIN_PAIRS}"
        )
    manifest["dev_frames"] = FROZEN_MANIFEST_TRAIN_FRAMES
    manifest["dev_pairs"] = FROZEN_MANIFEST_TRAIN_PAIRS
    return manifest


def plus1024_seed_bits(
    master: int,
    n: int,
    arm: str,
    block_index: int,
    *,
    bit_length: int | None = None,
) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P20F domain).

    Rule: concatenate SHA-256 over
    ``"nbpolar-p20f-plus1024-extension-seed:<master>:<n>:<arm>:
    <block_index>:<counter>"`` for ``counter = 0, 1, ...`` (ASCII decimal),
    unpack each digest MSB-first and truncate to ``bit_length`` (default
    ``10*n + 63``). The P20F prefix and arm tokens differ from the P16, P17,
    P18, P19, P20B, P20C and P20E domains on purpose. Seed contents are public control
    and are never persisted; only the bit length is recorded.
    """
    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P20F seed domain: {arm!r}")
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


def form_dev_blocks(
    table,
    *,
    dev_frames=FROZEN_DEV_FRAME_RANGE,
    block_frames=FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
) -> dict:
    """Deterministic TRAIN development validation plus block/remainder slicing.

    P18 ``form_holdout_blocks`` pattern with P20F ranges (the accepted helper
    is HOLD-range-pinned and the HOLD blocks are closed, so this local
    formation carries the identical validation semantics for the TRAIN pool).
    Accepts a normalized pairs frame (``frame_id``/``pair_idx``/
    ``alice_symbol``/``bob_symbol``). Any malformed population raises
    ``BLOCKED(dev_population_exact)``; any declared-range mismatch raises
    ``BLOCKED(blocks_exact_with_declared_remainder)``. No sorting key other
    than ``(frame_id, pair_idx)`` and no sampling of any kind.
    """
    try:
        pair = tuple(opf._as_int(v, "dev-frames", minimum=0) for v in dev_frames)
    except TypeError as exc:
        raise TypeError(f"dev-frames must be a pair of integers: {exc}") from exc
    if pair != tuple(FROZEN_DEV_FRAME_RANGE):
        raise Plus1024ExtensionContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"dev-frames {pair} != frozen {tuple(FROZEN_DEV_FRAME_RANGE)}"
        )
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise Plus1024ExtensionContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"block-frames {block_frames} != frozen {FROZEN_BLOCK_FRAMES}"
        )
    try:
        rem_pair = tuple(opf._as_int(v, "remainder-frames", minimum=0) for v in remainder_frames)
    except TypeError as exc:
        raise TypeError(f"remainder-frames must be a pair of integers: {exc}") from exc
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise Plus1024ExtensionContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"remainder-frames {rem_pair} != frozen {tuple(FROZEN_REMAINDER_FRAME_RANGE)}"
        )
    try:
        frame_id = np.asarray(table["frame_id"], dtype=np.int64)
        pair_idx = np.asarray(table["pair_idx"], dtype=np.int64)
        alice = np.asarray(table["alice_symbol"], dtype=np.int64)
        bob = np.asarray(table["bob_symbol"], dtype=np.int64)
    except (KeyError, TypeError, ValueError) as exc:
        raise Plus1024ExtensionContractError(
            f"BLOCKED(dev_population_exact): loader frame is malformed: {exc}"
        ) from exc
    if not (frame_id.shape == pair_idx.shape == alice.shape == bob.shape) or frame_id.ndim != 1:
        raise Plus1024ExtensionContractError(
            "BLOCKED(dev_population_exact): column shapes disagree"
        )
    for name, values in (("alice_symbol", alice), ("bob_symbol", bob)):
        if values.size == 0 or values.min() < 0 or values.max() >= N_BOB:
            raise Plus1024ExtensionContractError(
                f"BLOCKED(dev_population_exact): {name} outside 0..{N_BOB - 1}"
            )
    dev_first, dev_last = pair
    # The declared never-used remainder (1152..1199) lies OUTSIDE the DEV
    # selection by design (frozen --dev-frames 768 1151), so its presence
    # and span are measured from the unfiltered pool before DEV slicing;
    # the remainder is never decoded, only counted.
    pool_frame_id = np.asarray(table["frame_id"], dtype=np.int64)
    selected = (frame_id >= dev_first) & (frame_id <= dev_last)
    rows = int(np.sum(selected))
    if rows == 0:
        raise Plus1024ExtensionContractError(
            "BLOCKED(dev_population_exact): no rows in the frozen DEV frame range"
        )
    frame_id = frame_id[selected]
    pair_idx = pair_idx[selected]
    alice = alice[selected]
    bob = bob[selected]
    unique_frames = np.unique(frame_id)
    if unique_frames.size != FROZEN_DEV_FRAMES or int(unique_frames[0]) != dev_first or int(
        unique_frames[-1]
    ) != dev_last:
        raise Plus1024ExtensionContractError(
            "BLOCKED(dev_population_exact): DEV frames "
            f"{unique_frames.size} with range {int(unique_frames[0])}..{int(unique_frames[-1])} "
            f"!= frozen {FROZEN_DEV_FRAMES} with range {dev_first}..{dev_last}"
        )
    if rows != FROZEN_DEV_PAIRS:
        raise Plus1024ExtensionContractError(
            f"BLOCKED(dev_population_exact): DEV rows {rows} != frozen {FROZEN_DEV_PAIRS}"
        )
    order = np.lexsort((pair_idx, frame_id))
    frame_id = frame_id[order]
    pair_idx = pair_idx[order]
    alice = alice[order]
    bob = bob[order]
    expected_pair = np.tile(np.arange(FROZEN_PAIRS_PER_FRAME, dtype=np.int64), FROZEN_DEV_FRAMES)
    if not np.array_equal(pair_idx, expected_pair):
        raise Plus1024ExtensionContractError(
            "BLOCKED(dev_population_exact): pair_idx is not exactly 0..255 per frame"
        )
    ranges = []
    first = dev_first
    for _ in range(FROZEN_BLOCK_COUNT):
        last = first + int(block_frames) - 1
        ranges.append((first, last))
        first = last + 1
    if tuple(ranges) != FROZEN_BLOCK_RANGES:
        raise Plus1024ExtensionContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): block ranges "
            f"{tuple(ranges)} != frozen {FROZEN_BLOCK_RANGES}"
        )
    rem_first, rem_last = rem_pair
    if first != rem_first:
        raise Plus1024ExtensionContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder "
            f"{rem_first}..{rem_last} does not start where the three DEV blocks end"
        )
    # Declared-remainder evidence from the unfiltered pool (never decoded):
    # exactly the frozen 48 frames 1152..1199 with 12288 rows.
    remainder_rows = (pool_frame_id >= rem_first) & (pool_frame_id <= rem_last)
    remainder_frame_ids = pool_frame_id[remainder_rows]
    if int(np.sum(remainder_rows)) != FROZEN_REMAINDER_SYMBOLS:
        raise Plus1024ExtensionContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder rows "
            f"{int(np.sum(remainder_rows))} != frozen {FROZEN_REMAINDER_SYMBOLS}"
        )
    if (np.unique(remainder_frame_ids).size != FROZEN_REMAINDER_FRAMES
            or int(remainder_frame_ids.min()) != rem_first
            or int(remainder_frame_ids.max()) != rem_last):
        raise Plus1024ExtensionContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder frames "
            f"!= frozen {rem_first}..{rem_last} ({FROZEN_REMAINDER_FRAMES} frames)"
        )
    p20c_first, p20c_last = CONSUMED_P20C_DEV_FRAME_RANGE
    p20e_first, p20e_last = CONSUMED_P20E_DEV_FRAME_RANGE
    closed_first, closed_last = CLOSED_HOLD_FRAME_RANGE
    consumed_first, consumed_last = CONSUMED_VAL_FRAME_RANGE
    for start, end in ranges:
        if not (end < p20c_first or start > p20c_last):
            raise Plus1024ExtensionContractError(
                "BLOCKED(blocks_exact_with_declared_remainder): DEV block "
                f"{start}..{end} overlaps consumed P20C DEV {p20c_first}..{p20c_last}"
            )
        if not (end < p20e_first or start > p20e_last):
            raise Plus1024ExtensionContractError(
                "BLOCKED(blocks_exact_with_declared_remainder): DEV block "
                f"{start}..{end} overlaps consumed P20E DEV {p20e_first}..{p20e_last}"
            )
        if not (end < consumed_first or start > consumed_last):
            raise Plus1024ExtensionContractError(
                "BLOCKED(blocks_exact_with_declared_remainder): DEV block "
                f"{start}..{end} overlaps consumed VAL {consumed_first}..{consumed_last}"
            )
        if not (end < closed_first or start > closed_last):
            raise Plus1024ExtensionContractError(
                "BLOCKED(blocks_exact_with_declared_remainder): DEV block "
                f"{start}..{end} overlaps closed HOLD {closed_first}..{closed_last}"
            )
    blocks = []
    for index, (start, end) in enumerate(ranges):
        mask = (frame_id >= start) & (frame_id <= end)
        if int(np.sum(mask)) != FROZEN_SYMBOLS_PER_BLOCK:
            raise Plus1024ExtensionContractError(
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
        "dev_frame_range": [dev_first, dev_last],
        "dev_frames": int(unique_frames.size),
        "dev_pairs": rows,
        "blocks": blocks,
        "block_ranges": [list(r) for r in ranges],
        "remainder": {
            "frame_start": rem_first,
            "frame_end": rem_last,
            "frames": FROZEN_REMAINDER_FRAMES,
            "symbols": int(np.sum(remainder_rows)),
            "used": False,
        },
    }


def candidate_nll_bits(bob, high, low, p1_table, p2_table) -> dict:
    """Inf-tolerant total NLL in bits for diagnostic scoring.

    Same coherent model as ``holdout_nll_bits`` (frozen floored TRAIN
    tables, ``-log2`` sums) but exact-zero support ranks ``+inf`` instead of
    raising: diagnostics need a total order and the greedy path always scores
    finite (SC never emits exact-zero-support symbols). Pure scoring; takes
    no decision input and never selects.
    """
    b = np.asarray(bob, dtype=np.int64)
    h = np.asarray(high, dtype=np.int64)
    lo = np.asarray(low, dtype=np.int64)
    if not (b.shape == h.shape == lo.shape) or b.ndim != 1:
        raise ValueError("candidate scoring requires equal one-dimensional vectors")
    p1 = np.asarray(p1_table, dtype=np.float64)
    p2 = np.asarray(p2_table, dtype=np.float64)
    if p1.shape != (Q, N_BOB) or p2.shape != (Q, N_BOB, Q):
        raise ValueError("frozen prior tables must be [U1,B] and [U1,B,U2]")
    probs1 = p1[h, b]
    probs2 = p2[h, b, lo]
    with np.errstate(divide="ignore"):
        terms = -np.log2(np.where(probs1 > 0, probs1, np.nan))
        terms2 = -np.log2(np.where(probs2 > 0, probs2, np.nan))
    # Exact-zero support ranks +inf instead of raising; note inf * 0 is nan,
    # so the finite and non-finite cases stay on separate branches.
    if bool(np.isnan(terms).any()):
        l1 = float("inf")
    else:
        l1 = float(np.sum(terms))
    if bool(np.isnan(terms2).any()):
        l2 = float("inf")
    else:
        l2 = float(np.sum(terms2))
    n = int(b.size)
    return {"l1_nll_bits": l1, "l2_nll_bits": l2, "total_nll_bits": l1 + l2, "pairs": n}


def raw_floor_diagnostics(bob, high, low, counts_arr, p1_table, p2_table, *, floor=FROZEN_FLOOR) -> dict:
    """Raw zero-count hits, floor hits and their log loss for one candidate.

    ``raw`` is the unfloored column-normalized TRAIN conditional; a lookup
    with raw mass below ``floor`` was replaced by the floor before SC, so
    ``floor_hits`` counts exactly the lookups whose SC support came from the
    floor, and ``floor_hit_log_loss_bits`` is their ``-log2`` contribution
    under the floored tables. Pure scoring; takes no decision input.
    """
    b = np.asarray(bob, dtype=np.int64)
    h = np.asarray(high, dtype=np.int64)
    lo = np.asarray(low, dtype=np.int64)
    counts = np.asarray(counts_arr, dtype=np.float64)
    if counts.shape != (N_BOB, N_BOB):
        raise ValueError(f"counts must be (1024,1024), got {counts.shape}")
    col_totals = counts.sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.where(col_totals[None, :] > 0, counts / col_totals[None, :], 0.0)
    raw_p1 = derive_p1(np.ascontiguousarray(raw))
    raw_p2 = derive_p2(np.ascontiguousarray(raw))
    p1 = np.asarray(p1_table, dtype=np.float64)
    p2 = np.asarray(p2_table, dtype=np.float64)
    r1 = raw_p1[h, b]
    r2 = raw_p2[h, b, lo]
    zero_hits = int(np.sum(r1 == 0) + np.sum(r2 == 0))
    floor_hits = int(np.sum(r1 < float(floor)) + np.sum(r2 < float(floor)))
    mask = np.concatenate([r1 < float(floor), r2 < float(floor)])
    floored_entries = np.concatenate([p1[h, b], p2[h, b, lo]])[mask]
    with np.errstate(divide="ignore"):
        loss = float(-np.sum(np.log2(np.where(floored_entries > 0, floored_entries, np.nan))))
    if bool(np.isnan(loss)):
        loss = float("inf")
    return {
        "raw_zero_count_hits": zero_hits,
        "floor_hits_1e15": floor_hits,
        "floor_hit_log_loss_bits": loss,
    }


def first_error_coordinate(high_hat, low_hat, high_true, low_true) -> dict:
    """First mismatch coordinate and layer for attribution (scoring only)."""
    if high_hat is not None:
        diff = np.asarray(high_hat) != np.asarray(high_true)
        hits = np.flatnonzero(diff)
        if hits.size:
            return {"first_error_layer": "L1", "first_error_coord": int(hits[0])}
    if low_hat is not None:
        diff = np.asarray(low_hat) != np.asarray(low_true)
        hits = np.flatnonzero(diff)
        if hits.size:
            return {"first_error_layer": "L2", "first_error_coord": int(hits[0])}
    return {"first_error_layer": None, "first_error_coord": None}


def l2_prefix_positions(l2_order, k2: int) -> np.ndarray:
    """Frozen-order-prefix L2 disclosure positions for a registered arm.

    The disclosed L2 set is the first ``k2`` positions of the frozen P16
    L2 order (B0/B2: ``k2 = 6492``; B1: ``k2 = 7516``). Positions are fixed
    by the construction file, never selected on closed blocks, the
    consumed VAL pool, or DEV data. Pure view helper; takes no decision
    input.
    """
    order = np.asarray(l2_order, dtype=np.int64)
    k2 = opf._as_int(k2, "k2", minimum=0)
    if k2 > order.size:
        raise ValueError(f"k2={k2} exceeds the frozen L2 order length {order.size}")
    return order[:k2]


def _dev_block_scoring(block, p1_table, p2_table) -> dict:
    """Descriptive per-block scalars shared by every arm of that block."""
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


def _base_record_fields(*, spec, arm_index, block, scoring, oracle) -> dict:
    total_nll = scoring.get("total_nll_bits")
    return {
        "protocol": PROTOCOL_NAME,
        "arm": spec.name,
        "arm_index": int(arm_index),
        "arm_kind": spec.kind,
        "arm_provenance": spec.provenance,
        "block_index": int(block["block_index"]),
        "frame_start": int(block["frame_start"]),
        "frame_end": int(block["frame_end"]),
        "frame_count": FROZEN_BLOCK_FRAMES,
        "l1_prefix_len": int(spec.k1),
        "l2_prefix_len": int(spec.k2),
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


def _operational_record(result, *, spec, arm_index, block, scoring, resources,
                          disclosure=None, diag=None, error=None) -> dict:
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=False)
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
        "k1": int(result.k1),
        "k2": int(result.k2),
        "wall_s": round(float(result.wall_s), 6),
        "resources": dict(resources),
    })
    diag = diag or {}
    record.update({
        "raw_zero_count_hits": diag.get("raw_zero_count_hits"),
        "floor_hits_1e15": diag.get("floor_hits_1e15"),
        "floor_hit_log_loss_bits": diag.get("floor_hit_log_loss_bits"),
        "l2_nll_candidate_H_bits": diag.get("l2_nll_candidate_H_bits"),
        "l2_nll_true_H_bits": diag.get("l2_nll_true_H_bits"),
        "selected_total_nll_bits": diag.get("selected_total_nll_bits"),
    })
    disclosure = disclosure or {}
    is_plus = bool(spec.name == "B1_L2plus")
    record.update({
        "l2_delta_k2_applied": int(FROZEN_L2_DELTA_K2) if is_plus else 0,
        "l2_disclosure_rule": (
            "frozen-order-prefix-extension" if is_plus else "base"),
        "key_bit_delta_vs_base": int(FROZEN_B1_KEY_BIT_DELTA) if is_plus else 0,
    })
    return record


def _control_record(result, *, spec, arm_index, block, scoring, resources,
                    diag=None, error=None) -> dict:
    record = _base_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=True)
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
        "k1": int(spec.k1),
        "k2": int(spec.k2),
        "wall_s": round(float(result.wall_s), 6),
        "resources": dict(resources),
    })
    diag = diag or {}
    record.update({
        "raw_zero_count_hits": diag.get("raw_zero_count_hits"),
        "floor_hits_1e15": diag.get("floor_hits_1e15"),
        "floor_hit_log_loss_bits": diag.get("floor_hit_log_loss_bits"),
        "l2_nll_candidate_H_bits": diag.get("l2_nll_candidate_H_bits"),
        "l2_nll_true_H_bits": diag.get("l2_nll_true_H_bits"),
        "selected_total_nll_bits": diag.get("selected_total_nll_bits"),
    })
    record.update({
        "l2_delta_k2_applied": 0,
        "l2_disclosure_rule": "base",
        "key_bit_delta_vs_base": 0,
    })
    return record


def _abort_record(*, spec, arm_index, block, resources) -> dict:
    return {
        "protocol": PROTOCOL_NAME,
        "arm": spec.name,
        "arm_index": int(arm_index),
        "arm_kind": spec.kind,
        "arm_provenance": spec.provenance,
        "block_index": int(block["block_index"]),
        "frame_start": int(block["frame_start"]),
        "frame_end": int(block["frame_end"]),
        "frame_count": FROZEN_BLOCK_FRAMES,
        "l1_prefix_len": int(spec.k1),
        "l2_prefix_len": int(spec.k2),
        "full_block_key_dependent_bits": int(spec.leakage_bits),
        "public_control_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS),
        "disclosure_ce_ratio": None,
        "oracle_truth_use": bool(spec.kind == "oracle_control"),
        "oracle_control": bool(spec.kind == "oracle_control"),
        "deployable": bool(spec.kind != "oracle_control"),
        "raw_ser": None,
        "true_l1_nll_bits": None,
        "true_l2_nll_bits": None,
        "true_total_nll_bits": None,
        "true_total_nll_bits_per_pair": None,
        "outcome": "resource_abort",
        "exact": False,
        "label_match": False,
        "tag_pass": False,
        "l1_exact": False if spec.kind == "operational" else None,
        "hard_l2_exact": False if spec.kind == "operational" else None,
        "oracle_l2_exact": None if spec.kind == "operational" else False,
        "pair_exact": False if spec.kind == "operational" else None,
        "first_error_layer": None,
        "first_error_coord": None,
        "l1_executed": False,
        "l2_invoked": False,
        "tag_invoked": False,
        "sc_calls_this_record": 0,
        "actual_key_dependent_bits": 0,
        "actual_public_control_bits": 0,
        "nonfinite": False,
        "truth_leak_violation": False,
        "error": None,
        "k1": int(spec.k1),
        "k2": int(spec.k2),
        "raw_zero_count_hits": None,
        "floor_hits_1e15": None,
        "floor_hit_log_loss_bits": None,
        "l2_nll_candidate_H_bits": None,
        "l2_nll_true_H_bits": None,
        "selected_total_nll_bits": None,
        "l2_delta_k2_applied": None,
        "l2_disclosure_rule": None,
        "key_bit_delta_vs_base": None,
        "wall_s": 0.0,
        "resources": dict(resources),
    }


def _operational_record_consistent(record, spec, n) -> bool:
    try:
        if record.get("protocol") != PROTOCOL_NAME:
            return False
        if record.get("arm") != spec.name or int(record.get("arm_index", -1)) < 0:
            return False
        if record.get("arm_kind") != "operational":
            return False
        if record.get("outcome") not in OUTCOMES:
            return False
        if int(record.get("l1_prefix_len", -1)) != int(spec.k1):
            return False
        if int(record.get("l2_prefix_len", -1)) != int(spec.k2):
            return False
        if record.get("oracle_l2_exact") is not None:
            return False
        if spec.name == "B1_L2plus":
            if int(record.get("l2_delta_k2_applied", -1)) != FROZEN_L2_DELTA_K2:
                return False
            if record.get("l2_disclosure_rule") != "frozen-order-prefix-extension":
                return False
            if int(record.get("key_bit_delta_vs_base", -1)) != FROZEN_B1_KEY_BIT_DELTA:
                return False
        else:
            if int(record.get("l2_delta_k2_applied", -1)) != 0:
                return False
            if record.get("l2_disclosure_rule") != "base":
                return False
            if int(record.get("key_bit_delta_vs_base", -1)) != 0:
                return False
        for key in ("l1_exact", "hard_l2_exact", "pair_exact", "exact",
                    "label_match", "tag_pass"):
            if not isinstance(record.get(key), bool):
                return False
        if record.get("outcome") == "exact" and not (
            record.get("exact") and record.get("label_match") and record.get("tag_pass")
        ):
            return False
        if record.get("outcome") == "undetected" and not (
            record.get("tag_pass") and not record.get("label_match")
        ):
            return False
        return True
    except (TypeError, ValueError):
        return False


def _control_record_consistent(record, spec, n) -> bool:
    try:
        if record.get("protocol") != PROTOCOL_NAME:
            return False
        if record.get("arm") != spec.name:
            return False
        if record.get("arm_kind") != "oracle_control":
            return False
        if record.get("outcome") not in OUTCOMES:
            return False
        if record.get("l1_exact") is not None or record.get("hard_l2_exact") is not None:
            return False
        if record.get("pair_exact") is not None:
            return False
        if not isinstance(record.get("oracle_l2_exact"), bool):
            return False
        if not isinstance(record.get("oracle_truth_use"), bool) or not record.get(
            "oracle_truth_use"
        ):
            return False
        return True
    except (TypeError, ValueError):
        return False


def record_dict_consistent(record, *, n) -> bool:
    """Fail-closed per-record schema check used by the gates."""
    try:
        spec = ARM_BY_NAME[str(record.get("arm"))]
    except KeyError:
        return False
    if spec.kind == "operational":
        return _operational_record_consistent(record, spec, n)
    return _control_record_consistent(record, spec, n)


def _partition(records):
    operational = [r for r in records if r.get("arm_kind") == "operational"]
    control = [r for r in records if r.get("arm_kind") == "oracle_control"]
    return operational, control


def oracle_isolation_ok(records, *, final: bool) -> bool:
    """B2 provenance isolation: excluded from every operational aggregate."""
    operational, control = _partition(records)
    for record in control:
        if record.get("arm_provenance") != ORACLE_PROVENANCE:
            return False
        if record.get("deployable") is not False:
            return False
    for record in operational:
        if record.get("arm_provenance") != OPERATIONAL_PROVENANCE:
            return False
        if record.get("oracle_truth_use") is not False:
            return False
        if record.get("deployable") is not True:
            return False
    if final:
        if len(control) != FROZEN_BLOCK_COUNT:
            return False
        if len(operational) != 2 * FROZEN_BLOCK_COUNT:
            return False
    return True


def recovery_diagnostics(records) -> dict:
    """Descriptive per-arm recovery plus the B1-vs-B0 disclosure comparison.

    No threshold, no winner, no superiority claim: any exact count
    (including 0/9 and any partial restoration) is COMPLETE when
    integrity holds.
    """
    by_arm = {spec.name: [] for spec in FROZEN_ARMS}
    for record in records:
        if record.get("arm") in by_arm:
            by_arm[record["arm"]].append(record)
    per_arm = {}
    for name, arm_records in by_arm.items():
        per_arm[name] = {
            "records": len(arm_records),
            "exact_count": sum(1 for r in arm_records if r.get("exact") is True),
            "outcomes": {outcome: sum(1 for r in arm_records if r.get("outcome") == outcome)
                          for outcome in OUTCOMES},
        }
    disclosure_blocks = []
    b0_by_block = {r.get("block_index"): r for r in by_arm["B0_sc_base"]}
    b1_by_block = {r.get("block_index"): r for r in by_arm["B1_L2plus"]}
    for block_index in sorted(set(b0_by_block) | set(b1_by_block)):
        r0 = b0_by_block.get(block_index, {})
        r1 = b1_by_block.get(block_index, {})
        disclosure_blocks.append({
            "block_index": int(block_index),
            "b0_exact": r0.get("exact"),
            "b0_outcome": r0.get("outcome"),
            "b1_exact": r1.get("exact"),
            "b1_outcome": r1.get("outcome"),
            "l2_delta_k2_applied": r1.get("l2_delta_k2_applied"),
            "b1_restored_given_b0_failed": bool(
                r1.get("exact") is True and r0.get("exact") is not True),
        })
    b1_records = by_arm["B1_L2plus"]
    return {
        "per_arm": per_arm,
        "b1_restored_count": sum(
            1 for r in disclosure_blocks if r.get("b1_restored_given_b0_failed") is True),
        "disclosure_blocks": disclosure_blocks,
    }


def _arm_aggregate(records, spec) -> dict:
    arm_records = [r for r in records if r.get("arm") == spec.name]
    return {
        "arm": spec.name,
        "records": len(arm_records),
        "exact_count": sum(1 for r in arm_records if r.get("exact") is True),
        "key_dependent_bits": sum(int(r.get("actual_key_dependent_bits") or 0)
                                  for r in arm_records),
        "public_control_bits": sum(int(r.get("actual_public_control_bits") or 0)
                                   for r in arm_records),
    }


def build_aggregates(records) -> dict:
    """Per-arm aggregates; the oracle arm never enters operational totals."""
    operational, control = _partition(records)
    arms = {spec.name: _arm_aggregate(records, spec) for spec in FROZEN_ARMS}
    return {
        "arms": arms,
        "operational": {
            "records": len(operational),
            "exact_count": sum(1 for r in operational if r.get("exact") is True),
            "key_dependent_bits": sum(int(r.get("actual_key_dependent_bits") or 0)
                                      for r in operational),
            "public_control_bits": sum(int(r.get("actual_public_control_bits") or 0)
                                       for r in operational),
        },
        "oracle_control": {
            "records": len(control),
            "exact_count": sum(1 for r in control if r.get("exact") is True),
        },
        "recovery": recovery_diagnostics(records),
    }


def plus1024_extension_label(gates: dict) -> str:
    """Descriptive label: COMPLETE iff every integrity gate holds."""
    failing = [name for name in INTEGRITY_GATE_ORDER if not gates.get(name, False)]
    if not failing:
        return COMPLETE_LABEL
    return f"BLOCKED({failing[0]})"


def _backoff_event(
    *, n, arm, block_index, frame_start, event_id, event_type, direction,
    parent_event_id, key_dependent_bits, public_control_bits, payload,
) -> dict:
    event = {
        "event_id": event_id,
        "frame_key": (
            f"nbpolar-p20f-plus1024-extension:{int(n)}:{int(frame_start)}:{int(block_index)}"
        ),
        "method": "nbpolar_plus1024_extension",
        "event_type": event_type,
        "direction": direction,
        "parent_event_id": parent_event_id,
        "pass_id": 0,
        "block_id": int(block_index),
        "key_dependent_bits": int(key_dependent_bits),
        "public_control_bits": int(public_control_bits),
        "payload": payload,
    }
    canonical_event(event)  # fail closed on malformed or secret-bearing payloads
    return event


def plus1024_block_events(n: int, spec, block_index: int, frame_start: int, record) -> list:
    """Canonical public transcript events derived from one persisted record."""
    if record.get("outcome") == "resource_abort":
        return []
    events: list[dict] = []
    l1_id = None
    if record.get("l1_executed") and spec.kind == "operational":
        l1_id = f"block-{int(n)}-{int(block_index)}-{spec.name}-l1-disclosure"
        events.append(_backoff_event(
            n=n, arm=spec.name, block_index=block_index, frame_start=frame_start,
            event_id=l1_id, event_type="l1_disclosure", direction="alice_to_bob",
            parent_event_id=None,
            key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * int(spec.k1),
            public_control_bits=0, payload={},
        ))
    l2_id = None
    if record.get("l2_invoked"):
        l2_id = f"block-{int(n)}-{int(block_index)}-{spec.name}-l2-disclosure"
        events.append(_backoff_event(
            n=n, arm=spec.name, block_index=block_index, frame_start=frame_start,
            event_id=l2_id, event_type="l2_disclosure", direction="alice_to_bob",
            parent_event_id=l1_id,
            key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * int(spec.k2),
            public_control_bits=0, payload={},
        ))
    if record.get("tag_invoked"):
        events.append(_backoff_event(
            n=n, arm=spec.name, block_index=block_index, frame_start=frame_start,
            event_id=f"block-{int(n)}-{int(block_index)}-{spec.name}-verification",
            event_type="verification_tag", direction="alice_to_bob",
            parent_event_id=l2_id,
            key_dependent_bits=TAG_BITS,
            public_control_bits=seed_bits_for(int(n)),
            payload={"seed_bit_length": seed_bits_for(int(n))},
        ))
    return events


def plus1024_recount_events(events) -> dict:
    """Independent literal recount; N and arm are read literally from the event id."""
    totals = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    event_types = {"l1_disclosure": 0, "l2_disclosure": 0, "verification_tag": 0}
    for event in events:
        parts = str(event["event_id"]).split("-")
        if len(parts) < 5 or parts[0] != "block" or parts[3] not in FROZEN_ARM_NAMES:
            raise ValueError(f"transcript event id is not N/arm-tagged: {event['event_id']!r}")
        key = int(event["key_dependent_bits"])
        public = int(event["public_control_bits"])
        totals["key_dependent_bits"] += key
        totals["public_control_bits"] += public
        event_type = str(event["event_type"])
        if event_type not in event_types:
            raise ValueError(f"transcript event type is not frozen: {event_type!r}")
        event_types[event_type] += 1
        if event_type == "verification_tag":
            totals["tag_invocations"] += 1
    return {
        "key_dependent_bits": totals["key_dependent_bits"],
        "public_control_bits": totals["public_control_bits"],
        "tag_invocations": totals["tag_invocations"],
        "event_types": dict(event_types),
    }


@dataclass(frozen=True, eq=False)
class Plus1024ExtensionRun:
    """In-memory P20F diagnostic run (also returned by the runner)."""

    summary: dict
    records: tuple
    gates: dict


def _stat_record(path) -> dict:
    if path is None:
        return {"path": None, "size_bytes": None, "mtime_ns": None}
    st = Path(path).stat()
    return {"path": str(path), "size_bytes": int(st.st_size), "mtime_ns": int(st.st_mtime_ns)}


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


def _stub_plan(
    *, out_path, source, floor, n, k1, k2, construction, digest,
    dev_pairs, manifest_path, dev_frames, block_frames, remainder_frames,
    tag_master, chunk_rows, tag_bits, identity, manifest, dev_pin,
) -> dict:
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
        "k_total": int(k1 + k2),
        "l2_delta_k2": int(FROZEN_L2_DELTA_K2),
        "b1_k2": int(FROZEN_K2_B1),
        "b1_k_total": int(FROZEN_K_TOTAL_B1),
        "construction": str(construction),
        "construction_digest": str(digest),
        "dev_pairs": str(dev_pairs),
        "manifest_path": str(manifest_path),
        "dev_frames": [int(dev_frames[0]), int(dev_frames[1])],
        "block_frames": int(block_frames),
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "remainder_frames": [int(remainder_frames[0]), int(remainder_frames[1])],
        "closed_hold_frame_range": list(CLOSED_HOLD_FRAME_RANGE),
        "consumed_val_frame_range": list(CONSUMED_VAL_FRAME_RANGE),
        "consumed_p20c_dev_frame_range": list(CONSUMED_P20C_DEV_FRAME_RANGE),
        "consumed_p20e_dev_frame_range": list(CONSUMED_P20E_DEV_FRAME_RANGE),
        "tag_master": int(tag_master),
        "tag_seed_domain": f"{SEED_PREFIX}:<master>:<n>:<arm>:<block_index>",
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "arms": [
            {"name": spec.name, "kind": spec.kind, "k1": int(spec.k1),
             "k2": int(spec.k2), "leakage_bits": int(spec.leakage_bits),
             "provenance": spec.provenance}
            for spec in FROZEN_ARMS
        ],
        "planned_sc_calls": PLANNED_SC_CALLS,
        "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
        "planned_records": PLANNED_RECORDS,
        "base_leakage_bits": int(FROZEN_LEAKAGE_BITS),
        "b1_leakage_bits": int(FROZEN_B1_LEAKAGE_BITS),
        "b1_key_bit_delta_vs_base": int(FROZEN_B1_KEY_BIT_DELTA),
        "control_leakage_bits": int(FROZEN_CONTROL_LEAKAGE_BITS),
        "public_control_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS),
        "raw_input_bits_per_block": int(FROZEN_RAW_INPUT_BITS),
        "total_key_dependent_bits_if_all_invoked": int(FROZEN_TOTAL_KEY_DEPENDENT_BITS),
        "total_public_control_bits_if_all_tags": int(FROZEN_TOTAL_PUBLIC_CONTROL_BITS),
        "support_rule": SUPPORT_RULE,
        "dev_block_rule": DEV_BLOCK_RULE,
        "arm_rule": ARM_RULE,
        "disclosure_rule": DISCLOSURE_RULE,
        "nll_rule": NLL_RULE,
        "ratio_rule": RATIO_RULE,
        "truth_boundary": TRUTH_BOUNDARY,
        "no_threshold_rule": NO_THRESHOLD_RULE,
        "claim_scope": CLAIM_SCOPE,
        "outcome_precedence": list(OUTCOME_PRECEDENCE),
        "single_factor": "NOTHING varied: carried-over +1024 order-prefix step on B1; prior/floor/construction-order/kernel/representation/SC identical across arms; only the new-block population and new P20F tag domain differ",
        "deferred": ["independent-session confirmation (1.5M/2M candidate)", "disclosure-minimality probe (+512 vs +1024)", "negative-branch P20D fixed-disclosure alternative L2 construction", "positive-branch efficiency-optimization round"],
    }
    opf._write_json(out_path / "frozen_plan.json", plan)
    identity_doc = {
        "predecessor_construction": identity,
        "split_manifest": manifest,
        "dev_block_pin": dev_pin,
        "expected_npz_bytes": EXPECTED_NPZ_BYTES,
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
    }
    opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
    (out_path / "per_block_arm_outcomes.jsonl").write_text("", encoding="utf-8")
    opf._write_json(out_path / "aggregate_summary.json", {"status": "RUNNING"})
    (out_path / "report.md").write_text("# P20F plus1024 extension (RUNNING)\n", encoding="utf-8")
    return plan


def _render_report(summary: dict) -> str:
    lines = [
        "# NB-Polar Phase 4-P20F plus1024 extension",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- source: `{summary['source']}`; n={summary['n']}, "
        f"k1={summary['k1']}, k2={summary['k2']}, B1 K2={summary['b1_k2']} "
        f"(+{summary['l2_delta_k2']} L2 order-prefix step)",
        f"- DEV blocks: {summary['block_ranges']}; remainder {summary['remainder_frames']} (never used)",
        f"- closed HOLD: {summary['closed_hold_frame_range']} (never selected); "
        f"consumed VAL: {summary['consumed_val_frame_range']} (never selected); "
        f"consumed P20C DEV: {summary['consumed_p20c_dev_frame_range']} (never selected); "
        f"consumed P20E DEV: {summary['consumed_p20e_dev_frame_range']} (never selected)",
        f"- base cap: {summary['base_leakage_bits']} key bits/block; "
        f"B1 cap: {summary['b1_leakage_bits']} key bits/block "
        f"(raw {summary['raw_input_bits_per_block']} bits; ratios "
        f"{summary['cap_vs_raw_ratio']:.6f} / {summary['b1_cap_vs_raw_ratio']:.6f})",
        f"- wall: {summary['wall_s']} s; peak RSS: {summary['rss_bytes_peak']} bytes; "
        f"resource stop fired: {summary['resource_stop_fired']}",
        "",
        "## Per-arm outcomes (descriptive, no threshold)",
        "",
    ]
    for name, cell in summary["aggregates"]["arms"].items():
        lines.append(
            f"- {name}: {cell['exact_count']}/{cell['records']} exact; "
            f"key {cell['key_dependent_bits']} bits; public {cell['public_control_bits']} bits"
        )
    recovery = summary["aggregates"]["recovery"]
    lines += [
        "",
        "## B1-vs-B0 disclosure comparison (descriptive)",
        "",
        f"- B1 restored a complete block where B0 failed on "
        f"{recovery['b1_restored_count']}/{len(recovery['disclosure_blocks'])} blocks",
    ]
    for row in recovery["disclosure_blocks"]:
        lines.append(
            f"- block {row['block_index']}: B0 {row['b0_outcome']} "
            f"(exact={row['b0_exact']}) vs B1 {row['b1_outcome']} "
            f"(exact={row['b1_exact']}, dK2={row['l2_delta_k2_applied']}, "
            f"restored={row['b1_restored_given_b0_failed']})"
        )
    lines += [
        "",
        "## Integrity",
        "",
        f"- gates all pass: {summary['integrity_all_pass']}",
        f"- failing: {summary['failing_integrity_gates']}",
        f"- label: `{summary['outcome_label']}`",
        "",
        f"{summary['claim_scope']}",
        "",
    ]
    return "\n".join(lines)


def _integrity_gates(
    *, out_path, n, k1, k2, identity, manifest, dev_pin, l1_order, l2_order,
    formation, records, events, calls, incremental, accounting,
    provenance_violations, start, cap, resource_stop, precondition_passed,
    final, npz_stat_before, npz_stat_after, dev_stat_before, dev_stat_after,
    registered_paths, opened_paths,
) -> dict:
    n = int(n)
    k1 = int(k1)
    k2 = int(k2)

    identity_ok = bool(
        isinstance(identity, dict)
        and identity.get("digest_match") is True
        and identity.get("digest_recomputed") == FROZEN_CONSTRUCTION_DIGEST
        and int(identity.get("n", -1)) == FROZEN_N
        and int(identity.get("k_total", -1)) == FROZEN_K_TOTAL
        and int(identity.get("k1", -2)) == int(k1) == FROZEN_K1
        and int(identity.get("k2", -2)) == int(k2) == FROZEN_K2
    )
    manifest_ok = bool(
        isinstance(manifest, dict)
        and manifest.get("schema") == FROZEN_MANIFEST_SCHEMA
        and manifest.get("source") == FROZEN_SOURCE
        and int(manifest.get("dev_frames", -1)) == FROZEN_MANIFEST_TRAIN_FRAMES
        and int(manifest.get("dev_pairs", -1)) == FROZEN_MANIFEST_TRAIN_PAIRS
    )
    try:
        dev_now = verify_dev_block_identity()
    except ValueError:
        dev_now = None
    dev_pin_ok = bool(
        isinstance(dev_pin, dict)
        and dev_pin.get("verified") is True
        and isinstance(dev_now, dict)
        and dev_now.get("verified") is True
    )

    population_ok = bool(
        int(formation["dev_frames"]) == FROZEN_DEV_FRAMES
        and int(formation["dev_pairs"]) == FROZEN_DEV_PAIRS
        and list(formation["dev_frame_range"]) == list(FROZEN_DEV_FRAME_RANGE)
        and all(
            len(block["bob"]) == FROZEN_SYMBOLS_PER_BLOCK
            and len(block["high"]) == FROZEN_SYMBOLS_PER_BLOCK
            and len(block["low"]) == FROZEN_SYMBOLS_PER_BLOCK
            for block in formation["blocks"]
        )
    )
    if final:
        population_ok = bool(population_ok and len(formation["blocks"]) == FROZEN_BLOCK_COUNT)
    blocks_ok = bool(
        [tuple(r) for r in formation["block_ranges"]] == [tuple(r) for r in FROZEN_BLOCK_RANGES]
        and formation["remainder"]["used"] is False
        and int(formation["remainder"]["frames"]) == FROZEN_REMAINDER_FRAMES
        and int(formation["remainder"]["symbols"]) == FROZEN_REMAINDER_SYMBOLS
        and list(formation["dev_frame_range"]) == list(FROZEN_DEV_FRAME_RANGE)
    )
    # Block-major slot order: (B0,B1,B2) per block; each arm covers each block.
    expected_sequence = [
        tuple(r) for b in FROZEN_BLOCK_RANGES for r in (b, b, b)
    ]
    observed_sequence = [(int(r["frame_start"]), int(r["frame_end"])) for r in records]
    per_arm_counts = {
        spec.name: sum(1 for r in records if r.get("arm") == spec.name)
        for spec in FROZEN_ARMS
    }
    if final:
        blocks_ok = bool(
            blocks_ok
            and len(records) == PLANNED_RECORDS
            and observed_sequence == expected_sequence
            and all(count == FROZEN_BLOCK_COUNT for count in per_arm_counts.values())
        )

    records_ok = bool(final and len(records) == PLANNED_RECORDS)
    if not final:
        records_ok = bool(len(records) <= PLANNED_RECORDS)

    error_free = all(record.get("error") is None for record in records)
    derived_sc = 0
    for record in records:
        if record.get("error") is not None or record.get("outcome") == "resource_abort":
            continue
        spec = ARM_BY_NAME.get(str(record.get("arm")))
        if spec is None:
            continue
        if spec.kind == "operational":
            derived_sc += 1 + int(bool(record.get("l2_invoked")))
        else:
            derived_sc += int(bool(record.get("l2_invoked")))
    derived_tags = sum(1 for record in records if record.get("tag_invoked"))
    full_budget = bool(
        derived_sc == PLANNED_SC_CALLS and derived_tags == PLANNED_TAG_INVOCATIONS
    )
    accounted_partial = bool(resource_stop is not None and full_budget is False)
    sc_ok = bool(
        set(calls) == {"sc"}
        and error_free
        and int(calls.get("sc", -1)) == int(derived_sc)
        and (full_budget or accounted_partial)
    )
    tags_ok = bool(
        int(incremental["tag_invocations"]) == int(derived_tags)
        and (full_budget or accounted_partial)
    )

    orders_ok = bool(
        opf._order_is_permutation(l1_order, n) and opf._order_is_permutation(l2_order, n)
    )
    prefixes_ok = True
    for record in records:
        spec = ARM_BY_NAME.get(str(record.get("arm")))
        if spec is None:
            prefixes_ok = False
            break
        if int(record.get("k1", -1)) != int(spec.k1) or int(record.get("k2", -1)) != int(spec.k2):
            prefixes_ok = False
            break
        if int(record.get("arm_index", -1)) != FROZEN_ARM_NAMES.index(spec.name):
            prefixes_ok = False
            break
        if record["outcome"] != "resource_abort":
            expected_kdb = (
                DISCLOSED_BITS_PER_COORDINATE * int(spec.k1)
                + (DISCLOSED_BITS_PER_COORDINATE * int(spec.k2)
                   if record.get("l2_invoked") else 0)
                + (TAG_BITS if record.get("tag_invoked") else 0)
            )
            if int(record.get("actual_key_dependent_bits", -1)) != expected_kdb:
                prefixes_ok = False
                break
            if int(record.get("full_block_key_dependent_bits", -1)) != int(spec.leakage_bits):
                prefixes_ok = False
                break
        elif int(record.get("actual_key_dependent_bits", -1)) != 0:
            prefixes_ok = False
            break
    orders_ok = bool(orders_ok and prefixes_ok)

    oracle_ok = bool(
        int(provenance_violations) == 0 and oracle_isolation_ok(records, final=final)
    )

    buckets_ok = True
    seen_keys = set()
    for record in records:
        key = (str(record.get("arm")), int(record.get("block_index", -1)))
        if key in seen_keys:
            buckets_ok = False
            break
        seen_keys.add(key)
        if not record_dict_consistent(record, n=n):
            buckets_ok = False
            break
    if final:
        buckets_ok = bool(buckets_ok and len(records) == PLANNED_RECORDS)

    truth_ok = bool(
        int(provenance_violations) == 0
        and all(not record.get("truth_leak_violation", True) for record in records)
    )
    undetected_ok = bool(all(record.get("outcome") != "undetected" for record in records))
    nonfinite_ok = bool(
        all(record.get("outcome") != "nonfinite" for record in records)
        and all(not record.get("nonfinite", True) for record in records)
    )

    files_ok = True
    try:
        for name in OUTPUT_FILES:
            if not out_path.joinpath(name).is_file():
                files_ok = False
                break
        if files_ok:
            with open(out_path / "per_block_arm_outcomes.jsonl", "r", encoding="utf-8") as handle:
                if sum(1 for _ in handle) != len(records):
                    files_ok = False
    except OSError:
        files_ok = False

    try:
        recount = plus1024_recount_events(events)
        mismatches = opf._transcript_mismatches(incremental, recount)
        recount_ok = not mismatches
    except ValueError:
        recount_ok = False
    disclosure_ok = bool(recount_ok and files_ok)
    if disclosure_ok:
        for record in records:
            if record.get("error") is not None or record.get("outcome") == "resource_abort":
                continue
            spec = ARM_BY_NAME.get(str(record.get("arm")))
            if spec is None:
                disclosure_ok = False
                break
            expected_kdb = (
                DISCLOSED_BITS_PER_COORDINATE * int(spec.k1)
                + (DISCLOSED_BITS_PER_COORDINATE * int(spec.k2)
                   if record.get("l2_invoked") else 0)
                + (TAG_BITS if record.get("tag_invoked") else 0)
            )
            expected_public = seed_bits_for(n) if record.get("tag_invoked") else 0
            if (
                int(record.get("actual_key_dependent_bits", -1)) != expected_kdb
                or int(record.get("actual_public_control_bits", -1)) != expected_public
            ):
                disclosure_ok = False
                break

    mode = str(accounting.get("input_mode"))
    if mode == "real":
        expected_opens = {
            "counts": 1 if accounting.get("counts_input_mode") == "v25_npz" else 0,
            "dev": 1 if accounting.get("dev_input_mode") == "pairs_parquet" else 0,
        }
        one_open_ok = bool(
            int(accounting["counts_content_opens"]) == expected_opens["counts"]
            and int(accounting["dev_content_opens"]) == expected_opens["dev"]
            and int(accounting["attempts_consumed_by_this_run"]) == 1
            and int(accounting["retries"]) == 0
            and not bool(accounting["reopen_attempted"])
            and not bool(accounting["retry_after_open"])
        )
    else:
        one_open_ok = bool(
            int(accounting["counts_content_opens"]) == 0
            and int(accounting["dev_content_opens"]) == 0
            and int(accounting["attempts_consumed_by_this_run"]) == 0
            and int(accounting["retries"]) == 0
            and not bool(accounting["reopen_attempted"])
            and not bool(accounting["retry_after_open"])
        )

    def stat_unchanged(before: dict, after: dict) -> bool:
        if before.get("path") is None:
            return after.get("path") is None
        return bool(
            before.get("size_bytes") == after.get("size_bytes")
            and before.get("mtime_ns") == after.get("mtime_ns")
        )

    stat_ok = bool(
        stat_unchanged(npz_stat_before, npz_stat_after)
        and stat_unchanged(dev_stat_before, dev_stat_after)
    )
    access_ok = bool(set(calls) == {"sc"} and list(opened_paths) == list(registered_paths))

    wall_now = time.perf_counter() - start
    rss_now = opf._peak_rss_bytes()
    aborts = sum(1 for record in records if record.get("outcome") == "resource_abort")
    resource_ok = bool(
        resource_stop is None
        and aborts == 0
        and float(wall_now) <= float(cap)
        and (rss_now is None or int(rss_now) <= RSS_LIMIT_BYTES)
    )
    return {
        "predecessor_construction_identity": bool(identity_ok),
        "dev_split_manifest_identity": bool(manifest_ok),
        "dev_block_range_identity": bool(dev_pin_ok),
        "target_population_contract": bool(precondition_passed),
        "dev_population_exact": bool(population_ok),
        "blocks_exact_with_declared_remainder": bool(blocks_ok),
        "nine_records_exact": bool(records_ok),
        "sc_calls_exact": bool(sc_ok),
        "tags_exact": bool(tags_ok),
        "orders_valid_k_prefixes_within_registered_arms": bool(orders_ok),
        "oracle_isolation": bool(oracle_ok),
        "buckets_disjoint_exhaustive": bool(buckets_ok),
        "undetected_zero": bool(undetected_ok),
        "nonfinite_zero": bool(nonfinite_ok),
        "truth_isolation": bool(truth_ok),
        "disclosure_recount_exact": bool(disclosure_ok),
        "one_open_per_protected_input": bool(one_open_ok),
        "input_stat_unchanged": bool(stat_ok),
        "no_unregistered_access": bool(access_ok),
        "resource_limits_met_and_no_abort": bool(resource_ok),
    }


def _finalize_blocked(out_path, identity_doc, accounting, opened_paths, message: str) -> None:
    summary = {
        "analysis": PROTOCOL_NAME,
        "outcome_label": f"BLOCKED({message})",
        "attempt_read_accounting": dict(accounting, opened_content_paths=list(opened_paths)),
    }
    opf._write_json(out_path / "aggregate_summary.json", summary)
    (out_path / "report.md").write_text(
        f"# P20F plus1024 extension\n\nBLOCKED({message})\n", encoding="utf-8")


def run_plus1024_extension(
    *,
    counts=None,
    counts_path=FROZEN_COUNTS_PATH,
    source: str = FROZEN_SOURCE,
    floor=FROZEN_FLOOR,
    n: int = FROZEN_N,
    k1: int = FROZEN_K1,
    k2: int = FROZEN_K2,
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
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_entropies=None,
) -> Plus1024ExtensionRun:
    """Execute the frozen P20F three-arm diagnostic once; write five files.

    ``counts`` and ``dev_table`` plus ``expected_entropies`` are documented
    injected test seams; the frozen CLI passes only the frozen point and
    reads each protected input through its accepted loader exactly once.
    The +1024 L2 step on B1 is hardcoded (never CLI-tunable): B1 runs the
    accepted operational path with ``k2 = base k2 + 1024`` on the same
    frozen L2 order (order-prefix extension).
    """
    global _NPZ_CONTENT_OPENED, _DEV_PARQUET_CONTENT_OPENED
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    floor = _check_floor(floor)
    if source != FROZEN_SOURCE:
        raise ValueError(f"frozen point requires source={FROZEN_SOURCE!r}, got {source!r}")
    n = opf._check_n(n)
    k1 = _check_base_k1(k1)
    k2 = _check_base_k2(k2)
    opf._check_chunk_contract(chunk_rows)
    opf._check_tag_bits(tag_bits)
    dev_frames = _check_dev_frames(dev_frames)
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise ValueError(
            f"frozen point requires block-frames={FROZEN_BLOCK_FRAMES}, got {block_frames}")
    remainder_frames = _check_remainder_frames(remainder_frames)
    tag_master = _check_tag_master(tag_master)
    check_frozen_arm_table()

    # Predecessor identity, split manifest and the DEV pin are verified
    # before any root exists and before either protected content open; a
    # mismatch consumes nothing.
    if str(construction_digest) != FROZEN_CONSTRUCTION_DIGEST:
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = verify_predecessor_construction(construction, expected_digest=construction_digest)
    identity = verified["record"]
    manifest = verify_dev_manifest(manifest_path, source=source)
    dev_pin = verify_dev_block_identity()
    l1_order = np.asarray(verified["l1_order"], dtype=np.int64)
    l2_order = np.asarray(verified["l2_order"], dtype=np.int64)

    # One-open guards are refusals before any content open of either input.
    if counts is None and _NPZ_CONTENT_OPENED:
        raise ValueError("reopen refused: the single NPZ content open was already consumed")
    if dev_table is None and _DEV_PARQUET_CONTENT_OPENED:
        raise ValueError("reopen refused: the single DEV parquet content open was already consumed")

    # Input existence and stat-only metadata come before any content open.
    real_counts = counts is None
    real_dev = dev_table is None
    if real_counts:
        npz_path = Path(counts_path)
        if not npz_path.is_file():
            raise FileNotFoundError(f"V25 channel counts file not found: {npz_path}")
        npz_stat_before = _stat_record(npz_path)
        if npz_stat_before["size_bytes"] != EXPECTED_NPZ_BYTES:
            raise ValueError(
                "V25 channel counts size mismatch before content open: "
                f"observed {npz_stat_before['size_bytes']} != expected {EXPECTED_NPZ_BYTES}"
            )
    else:
        npz_stat_before = _stat_record(None)
    if real_dev:
        dev_path = Path(dev_pairs)
        if not dev_path.is_file():
            raise FileNotFoundError(f"1M DEV pairs parquet not found: {dev_path}")
        dev_stat_before = _stat_record(dev_path)
    else:
        dev_stat_before = _stat_record(None)
    registered_paths = []
    if real_counts:
        registered_paths.append(str(Path(counts_path).resolve()))
    if real_dev:
        registered_paths.append(str(Path(dev_pairs).resolve()))
    opened_paths: list[str] = []

    plan = _stub_plan(
        out_path=out_path, source=source, floor=floor, n=n, k1=k1, k2=k2,
        construction=construction, digest=construction_digest, dev_pairs=dev_pairs,
        manifest_path=manifest_path, dev_frames=dev_frames, block_frames=block_frames,
        remainder_frames=remainder_frames, tag_master=tag_master, chunk_rows=chunk_rows,
        tag_bits=tag_bits, identity=identity, manifest=manifest, dev_pin=dev_pin,
    )
    accounting = {
        "input_mode": "real" if (real_counts or real_dev) else "injected",
        "counts_input_mode": "v25_npz" if real_counts else "injected_counts",
        "dev_input_mode": "pairs_parquet" if real_dev else "injected_table",
        "counts_path": str(counts_path) if real_counts else None,
        "dev_pairs_path": str(dev_pairs) if real_dev else None,
        "manifest_path": str(manifest_path),
        "construction_path": str(construction),
        "npz_loader": NPZ_LOADER_IDENTITY if real_counts else None,
        "pairs_loader": PAIRS_LOADER_IDENTITY if real_dev else None,
        "registered_content_paths": registered_paths,
        "opened_content_paths": opened_paths,
        "artifact_content_reads_allowed_per_input": 1,
        "counts_content_opens": 0,
        "dev_content_opens": 0,
        "attempts_allowed": 1,
        "attempts_consumed_by_this_run": 0,
        "retries": 0,
        "reopen_attempted": False,
        "retry_after_open": False,
    }

    start = time.perf_counter()
    try:
        # ---- input 1: stat-only check, then the single NPZ content open.
        if real_counts:
            loaded = load_v25_channel_counts(str(counts_path))
            _NPZ_CONTENT_OPENED = True
            accounting["counts_content_opens"] = 1
            accounting["attempts_consumed_by_this_run"] = 1
            opened_paths.append(str(Path(counts_path).resolve()))
            if source not in loaded:
                raise ValueError(f"source {source!r} missing from the loaded V25 counts")
            counts_arr = np.asarray(loaded[source])
        else:
            counts_arr = np.asarray(counts)
        if counts_arr.shape != (1024, 1024):
            raise ValueError(f"frozen target requires counts shape (1024,1024), got {counts_arr.shape}")

        # ---- frozen preconditions: no SC call may happen before this passes.
        if expected_entropies is None:
            expected_h1, expected_h2, expected_total = (
                opf.EXPECTED_H1, opf.EXPECTED_H2, opf.EXPECTED_TOTAL,
            )
        else:
            expected_h1, expected_h2, expected_total = (float(v) for v in expected_entropies)
        precondition_report = target_preconditions(
            counts_arr, floor=floor, expected_h1=expected_h1,
            expected_h2=expected_h2, expected_total=expected_total,
        )
        if not precondition_report.passed:
            raise TargetPopulationContractError(
                "BLOCKED(target_population_contract): failing preconditions: "
                + ",".join(precondition_report.failing)
            )
        entropy = precondition_report.entropy
        p1 = entropy.p1
        p2 = entropy.p2

        # ---- input 2: the single DEV parquet content open, DEV rows only.
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
        calls = {"sc": 0}
        records: list[dict] = []
        events: list[dict] = []
        incremental = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
        provenance_violations = 0
        resource_stop: str | None = None
        budget_cap = float(total_wall_s)
        if not np.isfinite(budget_cap) or budget_cap <= 0:
            raise ValueError(f"total_wall_s must be finite and positive, got {total_wall_s!r}")

        def current_gates(*, final: bool) -> tuple:
            gates = _integrity_gates(
                out_path=out_path, n=n, k1=k1, k2=k2, identity=identity,
                manifest=manifest, dev_pin=dev_pin, l1_order=l1_order, l2_order=l2_order,
                formation=formation, records=records, events=events, calls=calls,
                incremental=incremental, accounting=accounting,
                provenance_violations=provenance_violations, start=start,
                cap=budget_cap, resource_stop=resource_stop,
                precondition_passed=bool(precondition_report.passed), final=final,
                npz_stat_before=npz_stat_before, npz_stat_after=npz_stat_before,
                dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_before,
                registered_paths=registered_paths, opened_paths=opened_paths,
            )
            failing = [g for g in INTEGRITY_GATE_ORDER if not gates[g]]
            return gates, failing

        def partial_summary(outcome_label: str, gates: dict) -> dict:
            outcome_counts = {name: 0 for name in OUTCOMES}
            for record in records:
                if record.get("outcome") in outcome_counts:
                    outcome_counts[record["outcome"]] += 1
            aggregates = build_aggregates(records)
            return {
                "analysis": PROTOCOL_NAME,
                "mode": MODE,
                "source": source,
                "n": int(n),
                "k1": int(k1),
                "k2": int(k2),
                "l2_delta_k2": int(FROZEN_L2_DELTA_K2),
                "b1_k2": int(FROZEN_K2_B1),
                "b1_k_total": int(FROZEN_K_TOTAL_B1),
                "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
                "remainder_frames": list(FROZEN_REMAINDER_FRAME_RANGE),
                "closed_hold_frame_range": list(CLOSED_HOLD_FRAME_RANGE),
                "consumed_val_frame_range": list(CONSUMED_VAL_FRAME_RANGE),
                "consumed_p20c_dev_frame_range": list(CONSUMED_P20C_DEV_FRAME_RANGE),
                "consumed_p20e_dev_frame_range": list(CONSUMED_P20E_DEV_FRAME_RANGE),
                "base_leakage_bits": int(FROZEN_LEAKAGE_BITS),
                "b1_leakage_bits": int(FROZEN_B1_LEAKAGE_BITS),
                "b1_key_bit_delta_vs_base": int(FROZEN_B1_KEY_BIT_DELTA),
                "raw_input_bits_per_block": int(FROZEN_RAW_INPUT_BITS),
                "cap_vs_raw_ratio": float(FROZEN_LEAKAGE_BITS / FROZEN_RAW_INPUT_BITS),
                "b1_cap_vs_raw_ratio": float(FROZEN_B1_LEAKAGE_BITS / FROZEN_RAW_INPUT_BITS),
                "outcome_counts": outcome_counts,
                "records_completed": len(records),
                "planned_records": PLANNED_RECORDS,
                "planned_sc_calls": PLANNED_SC_CALLS,
                "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
                "sc_calls": int(calls.get("sc", 0)),
                "tag_invocations": int(incremental.get("tag_invocations", 0)),
                "aggregates": aggregates,
                "integrity": {name: bool(gates.get(name, False)) for name in INTEGRITY_GATE_ORDER},
                "integrity_all_pass": bool(
                    all(gates.get(name, False) for name in INTEGRITY_GATE_ORDER)
                ),
                "failing_integrity_gates": [
                    name for name in INTEGRITY_GATE_ORDER if not gates.get(name, False)
                ],
                "outcome_label": outcome_label,
                "wall_s": round(float(time.perf_counter() - start), 6),
                "rss_bytes_peak": opf._peak_rss_bytes(),
                "resource_stop_fired": bool(resource_stop is not None),
                "resource_stop_reason": resource_stop,
                "attempt_read_accounting": dict(accounting, opened_content_paths=list(opened_paths)),
                "claim_scope": CLAIM_SCOPE,
            }

        def persist(summary_doc: dict) -> None:
            opf._write_json(out_path / "aggregate_summary.json", summary_doc)
            (out_path / "report.md").write_text(_render_report(summary_doc), encoding="utf-8")

        slots = []
        for block_index, block in enumerate(formation["blocks"]):
            for arm_index, spec in enumerate(FROZEN_ARMS):
                slots.append((arm_index, spec, block_index, block))
        total_slots = len(slots)
        views = {idx: _block_view(block, field) for idx, block in enumerate(formation["blocks"])}
        scoring_by_block = {}
        for idx, block in enumerate(formation["blocks"]):
            try:
                scoring_by_block[idx] = _dev_block_scoring(block, p1, p2)
            except ValueError:
                scoring_by_block[idx] = _scoring_absent()

        def selected_diagnostics(*, high_sel, low_sel, view) -> dict:
            diag = {
                "raw_zero_count_hits": None,
                "floor_hits_1e15": None,
                "floor_hit_log_loss_bits": None,
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
            cand = candidate_nll_bits(view["bob"], high_sel, low_sel, p1, p2)
            diag["l2_nll_candidate_H_bits"] = float(cand["l2_nll_bits"])
            diag["selected_total_nll_bits"] = float(cand["total_nll_bits"])
            true_cond = candidate_nll_bits(view["bob"], view["high"], low_sel, p1, p2)
            diag["l2_nll_true_H_bits"] = float(true_cond["l2_nll_bits"])
            return diag

        rejected = False
        for slot_index, (arm_index, spec, block_index, block) in enumerate(slots):
            reason = opf._budget_exceeded(start, budget_cap)
            if reason is not None:
                resource_stop = reason
                for rest_index in range(slot_index, total_slots):
                    rest_arm_index, rest_spec, _, rest_block = slots[rest_index]
                    record = _abort_record(
                        spec=rest_spec, arm_index=rest_arm_index, block=rest_block,
                        resources=opf._cell_resource_record(0.0),
                    )
                    records.append(record)
                    opf._append_jsonl(out_path / "per_block_arm_outcomes.jsonl", record)
                    gates_now, _ = current_gates(final=False)
                    persist(partial_summary(
                        f"RUNNING(record {len(records)}/{total_slots})", gates_now))
                rejected = True
                break
            view = views[block_index]
            scoring = scoring_by_block[block_index]
            frame_start = int(block["frame_start"])
            seed = plus1024_seed_bits(tag_master, n, spec.name, block_index,
                                            bit_length=seed_bits_for(n))

            def _tag_fn(bits, _seed, tag_bits, _fixed=seed):
                return toeplitz_tag(bits, _fixed, tag_bits)

            block_start = time.perf_counter()
            if spec.kind == "operational":
                # B0 and B1 share the accepted operational path bit-for-bit
                # except the disclosed L2 prefix length: B0 runs k2=6492
                # (base) while B1 runs k2=7516 (the single frozen +1024
                # order-prefix step) on the SAME frozen L2 order. The step
                # is hardcoded in the arm table, never CLI-tunable.
                try:
                    result = run_operational_block(
                        n=n, stream_seed=frame_start, block_index=block_index,
                        bob=view["bob"], high_true=view["high"], low_true=view["low"],
                        u1_true=view["u1"], u2_true=view["u2"], labels_true=view["labels"],
                        labels_true_bits=view["labels_bits"], field=field,
                        p1_table=p1, p2_table=p2, l1_order=l1_order, l2_order=l2_order,
                        k1=spec.k1, k2=spec.k2, master=tag_master,
                        tag_fn=_tag_fn, calls=calls,
                    )
                    error = None
                except MemoryError:
                    raise  # resource stop owns MemoryError; never decode_failed/nonfinite
                except Exception as exc:  # block failure: recorded, gate fails
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
                diag = selected_diagnostics(
                    high_sel=result.high_hat, low_sel=result.low_hat, view=view)
                record = _operational_record(
                    result, spec=spec, arm_index=arm_index, block=block,
                    scoring=scoring, resources=resources, diag=diag, error=error,
                )
            else:
                try:
                    result = run_oracle_control_block(
                        n=n, block_index=block_index, frame_start=frame_start,
                        bob=view["bob"], high_true=view["high"], low_true=view["low"],
                        u1_true=view["u1"], u2_true=view["u2"], labels_true=view["labels"],
                        labels_true_bits=view["labels_bits"], field=field,
                        p2_table=p2, l2_order=l2_order, k2=spec.k2,
                        master=tag_master, tag_fn=_tag_fn, calls=calls,
                    )
                    error = None
                except MemoryError:
                    raise  # resource stop owns MemoryError; never decode_failed/nonfinite
                except Exception as exc:  # control failure: recorded, gate fails
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
                diag = selected_diagnostics(
                    high_sel=view["high"] if result.low_hat is not None else None,
                    low_sel=result.low_hat, view=view)
                record = _control_record(
                    result, spec=spec, arm_index=arm_index, block=block,
                    scoring=scoring, resources=resources, diag=diag, error=error,
                )

            records.append(record)
            opf._append_jsonl(out_path / "per_block_arm_outcomes.jsonl", record)
            for event in plus1024_block_events(n, spec, block_index, frame_start, record):
                events.append(event)
                incremental["key_dependent_bits"] += int(event["key_dependent_bits"])
                incremental["public_control_bits"] += int(event["public_control_bits"])
                if str(event["event_type"]) == "verification_tag":
                    incremental["tag_invocations"] += 1
            gates_now, _ = current_gates(final=False)
            persist(partial_summary(
                f"RUNNING(record {len(records)}/{total_slots})", gates_now))

        # ---- closing stat checks, final gates, label and evidence.
        wall_s = time.perf_counter() - start
        rss_peak = opf._peak_rss_bytes()
        if real_counts:
            npz_stat_after = _stat_record(Path(counts_path))
        else:
            npz_stat_after = _stat_record(None)
        if real_dev:
            dev_stat_after = _stat_record(Path(dev_pairs))
        else:
            dev_stat_after = _stat_record(None)
        gates = _integrity_gates(
            out_path=out_path, n=n, k1=k1, k2=k2, identity=identity,
            manifest=manifest, dev_pin=dev_pin, l1_order=l1_order, l2_order=l2_order,
            formation=formation, records=records, events=events, calls=calls,
            incremental=incremental, accounting=accounting,
            provenance_violations=provenance_violations, start=start,
            cap=budget_cap, resource_stop=resource_stop,
            precondition_passed=bool(precondition_report.passed), final=True,
            npz_stat_before=npz_stat_before, npz_stat_after=npz_stat_after,
            dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_after,
            registered_paths=registered_paths, opened_paths=opened_paths,
        )
        outcome_label = plus1024_extension_label(gates)
        summary = partial_summary(outcome_label, gates)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        identity_doc = {
            "predecessor_construction": identity,
            "split_manifest": manifest,
            "dev_block_pin": dev_pin,
            "expected_npz_bytes": EXPECTED_NPZ_BYTES,
            "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
            "npz_stat_before": npz_stat_before,
            "npz_stat_after": npz_stat_after,
            "dev_stat_before": dev_stat_before,
            "dev_stat_after": dev_stat_after,
            "attempt_read_accounting": dict(accounting, opened_content_paths=list(opened_paths)),
        }
        opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
        persist(summary)
        return Plus1024ExtensionRun(summary=summary, records=tuple(records), gates=gates)
    except Plus1024ExtensionResourceError as exc:
        _finalize_blocked_with_accounting(
            out_path, accounting, opened_paths, resource_stop or str(exc))
        raise
    except MemoryError as exc:
        label = f"resource stop: MemoryError: {exc}"
        try:
            _finalize_blocked_with_accounting(out_path, accounting, opened_paths, label)
        except (OSError, ValueError):
            pass
        raise Plus1024ExtensionResourceError(label) from exc


def _finalize_blocked_with_accounting(out_path, accounting, opened_paths, message: str) -> None:
    summary = {
        "analysis": PROTOCOL_NAME,
        "outcome_label": f"BLOCKED({message})",
        "attempt_read_accounting": dict(accounting, opened_content_paths=list(opened_paths)),
    }
    opf._write_json(Path(out_path) / "aggregate_summary.json", summary)
    (Path(out_path) / "report.md").write_text(
        f"# P20F plus1024 extension\n\nBLOCKED({message})\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p20f-plus1024-extension",
        description=(
            "NB-Polar Phase 4-P20F N=32768 plus1024 extension "
            "(frozen V25 counts, verified P16 construction, three NEW TRAIN DEV "
            "blocks, three frozen arms)"
        ),
    )
    parser.add_argument("--counts", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--floor", required=True, type=float)
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--k1", required=True, type=int)
    parser.add_argument("--k2", required=True, type=int)
    parser.add_argument("--construction", required=True)
    parser.add_argument("--construction-digest", required=True, dest="construction_digest")
    parser.add_argument("--dev-pairs", required=True, dest="dev_pairs")
    parser.add_argument("--dev-frames", required=True, type=int, nargs=2, dest="dev_frames")
    parser.add_argument("--block-frames", required=True, type=int, dest="block_frames")
    parser.add_argument("--remainder-frames", required=True, type=int, nargs=2,
                        dest="remainder_frames")
    parser.add_argument("--tag-master", required=True, type=int, dest="tag_master")
    parser.add_argument("--chunk-rows", required=True, type=int, dest="chunk_rows")
    parser.add_argument("--tag-bits", required=True, type=int, dest="tag_bits")
    parser.add_argument("--out-dir", required=True, dest="out_dir")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run = run_plus1024_extension(
            counts_path=args.counts,
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
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p20f plus1024 extension refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "records_completed": summary["records_completed"],
                "operational_exact_count": summary["aggregates"]["operational"]["exact_count"],
                "b1_restored_count": summary["aggregates"]["recovery"]["b1_restored_count"],
                "integrity_all_pass": summary["integrity_all_pass"],
                "outcome_label": summary["outcome_label"],
                "out_root": args.out_dir,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROTOCOL_NAME", "MODE", "Q", "ALPHA", "N_BOB", "FROZEN_N", "FROZEN_SOURCE",
    "FROZEN_FLOOR", "FROZEN_TARGET_F", "FROZEN_K1", "FROZEN_K2",
    "FROZEN_K_TOTAL", "FROZEN_L2_DELTA_K2", "FROZEN_K2_B1", "FROZEN_K_TOTAL_B1",
    "FROZEN_B1_KEY_BIT_DELTA", "FROZEN_LEAKAGE_BITS", "FROZEN_B1_LEAKAGE_BITS",
    "FROZEN_CONTROL_LEAKAGE_BITS",
    "FROZEN_PUBLIC_CONTROL_BITS", "FROZEN_RAW_INPUT_BITS",
    "DISCLOSURE_RULE",
    "FROZEN_DEV_FRAME_RANGE", "FROZEN_DEV_FRAMES", "FROZEN_DEV_PAIRS",
    "FROZEN_BLOCK_COUNT", "FROZEN_BLOCK_FRAMES", "FROZEN_PAIRS_PER_FRAME",
    "FROZEN_SYMBOLS_PER_BLOCK", "FROZEN_BLOCK_RANGES",
    "FROZEN_REMAINDER_FRAME_RANGE", "FROZEN_REMAINDER_FRAMES",
    "FROZEN_REMAINDER_SYMBOLS", "CLOSED_HOLD_FRAME_RANGE",
    "CONSUMED_VAL_FRAME_RANGE", "CONSUMED_P20C_DEV_FRAME_RANGE",
    "CONSUMED_P20E_DEV_FRAME_RANGE",
    "FROZEN_MANIFEST_TRAIN_FRAMES", "FROZEN_MANIFEST_TRAIN_PAIRS",
    "FROZEN_TAG_MASTER", "FROZEN_CHUNK_ROWS", "FROZEN_TAG_BITS",
    "SEED_PREFIX", "OPERATIONAL_PROVENANCE", "ORACLE_PROVENANCE",
    "EXPECTED_NPZ_BYTES", "FROZEN_COUNTS_PATH", "FROZEN_DEV_PAIRS_PATH",
    "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA", "FROZEN_CONSTRUCTION_PATH",
    "FROZEN_CONSTRUCTION_DIGEST", "FROZEN_OUT_ROOT", "NPZ_LOADER_IDENTITY",
    "PAIRS_LOADER_IDENTITY", "RSS_LIMIT_BYTES", "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S", "ULIMIT_VIRTUAL_KIB", "OUTCOMES", "COMPLETE_LABEL",
    "SUPPORT_RULE", "DEV_BLOCK_RULE", "ARM_RULE", "NLL_RULE", "RATIO_RULE",
    "TRUTH_BOUNDARY", "NO_THRESHOLD_RULE",
    "CLAIM_SCOPE", "OUTCOME_PRECEDENCE", "INTEGRITY_GATE_ORDER",
    "FROZEN_COMMAND", "OUTPUT_FILES", "ATTEMPT_CONSUMPTION_POINT",
    "ArmSpec", "FROZEN_ARMS", "FROZEN_ARM_NAMES", "OPERATIONAL_ARM_NAMES",
    "ORACLE_ARM_NAME", "ARM_BY_NAME", "PLANNED_SC_CALLS",
    "PLANNED_TAG_INVOCATIONS", "PLANNED_RECORDS",
    "FROZEN_TOTAL_KEY_DEPENDENT_BITS", "FROZEN_TOTAL_PUBLIC_CONTROL_BITS",
    "Plus1024ExtensionContractError", "Plus1024ExtensionResourceError",
    "Plus1024ExtensionRun", "check_frozen_arm_table",
    "verify_dev_block_identity", "verify_dev_manifest",
    "plus1024_seed_bits", "form_dev_blocks", "candidate_nll_bits",
    "raw_floor_diagnostics", "first_error_coordinate",
    "l2_prefix_positions",
    "run_operational_block", "run_oracle_control_block", "OracleControlResult",
    "verify_predecessor_construction", "verify_split_manifest",
    "holdout_nll_bits", "raw_symbol_error_rate", "form_holdout_blocks",
    "polar_transform_fn", "make_gf32_fn", "toeplitz_tag_fn",
    "build_p1_metrics_fn", "gather_p2_metrics_fn", "probs_to_symbol_metric_fn",
    "oracle_isolation_ok", "recovery_diagnostics", "build_aggregates",
    "plus1024_extension_label", "plus1024_block_events",
    "plus1024_recount_events", "run_plus1024_extension",
    "build_parser", "main",
]
