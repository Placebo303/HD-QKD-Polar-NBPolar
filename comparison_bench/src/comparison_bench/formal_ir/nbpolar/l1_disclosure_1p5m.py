"""NB-Polar Phase 4-P20I N=32768 L1-disclosure +128 single-factor diagnostic on type2_1p5M_20260121_183806 (Stage A, frozen).

L1-disclosure single-factor packet (strategy stage 2): with ONE
preregistered change against P20H -- L1 disclosure +ΔK1=128 via the
frozen order-prefix rule (Stage-A frozen, Stage-B read-only) -- and
everything else carried over from P20H (per-session prior
digest-pinned read-only, K2 base 6492, floor 1e-15, N=32768, greedy SC
only, new P20I tag domains only), zero further tuning: does +128 L1
restore any complete operational block on three NEW 1.5M TRAIN blocks
(384..767) -- and where does the first error move when L1 disclosure
grows while L2 disclosure stays at base? The only deliberate
differences from P20H are the +128 L1 order-prefix step and the new
P20I tag domain, both provenance/identity changes under the frozen
program, never algorithm changes.

Three hardcoded arms (never CLI-tunable, never extensible):

- ``C0_sc_base``: frozen greedy SC at base disclosure/construction via
  the accepted ``run_operational_block`` (operational, 2 SC + 1 tag per
  block).
- ``C1_L1plus``: frozen greedy SC at base + the frozen +128 L1 step
  via frozen-order-prefix extension (K1 319 -> 447 on the SAME frozen
  P16 L1 order), all else identical, via the accepted
  ``run_operational_block`` (operational, the single-factor candidate;
  2 SC + 1 tag per block).
- ``C2_true_l1_diagnostic``: true-L1-conditioned L2 at BASE disclosure
  via the accepted ``run_oracle_control_block`` (provenance
  ``ORACLE_TRUE_L1_CONTROL``, deployable=false, excluded from every
  operational aggregate; never described as a correction result).

Development population: the NEXT 384 TRAIN frames of the independent
1.5M session file ``type2_1p5M_20260121_183806/pairs.parquet`` in
``(frame_id, pair_idx)`` order after the consumed P20H DEV prefix
(frozen TRAIN base 0: frames ``384..767``; all remaining 1.5M TRAIN
frames ``768..1659`` are never used). Three NEW DEV blocks
``384..511`` / ``512..639`` / ``640..767`` plus the declared
never-used remainder ``768..1659`` (892 frames / 228352 pairs, counted
from the pool but never decoded). The ENTIRE 1M pool and the reserved
2M file are excluded by the fail-closed cross-file source-tag+digest
gate before any SC call; DEV ranges must additionally overlap NONE of
the 1.5M VAL/HOLD frame sets (intra-file gate, checked second) and
NONE of the consumed P20H DEV prefix ``0..383`` (P20H-DEV exclusion
gate, checked third); the Stage-B prior/table/literal digest must
equal the §3 frozen digest before any SC call
(calibration-identity gate, checked fourth).

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
from ..v35_algorithm_development import SOURCE_IDS
from .per_session_calibration import (
    FROZEN_LAMBDA as FROZEN_CALIBRATION_LAMBDA,
    PRIOR_NPZ_KEYS,
    canonical_prior_digest,
    load_calibrated_prior,
)
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

PROTOCOL_NAME = "nbpolar-p20i-l1-disclosure-1p5m"
MODE = "dev-l1-disclosure-1p5m"

Q = opf.Q
ALPHA = opf.ALPHA
N_BOB = hm.N_BOB
FROZEN_N = 32768
FROZEN_SOURCE = "1p5M"
FROZEN_SOURCE_TAG = "type2_1p5M_20260121_183806"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
FROZEN_K1 = 319
FROZEN_K2 = 6492
FROZEN_K_TOTAL = 6811
# The single frozen disclosure factor (Stage-A freeze, never tuned
# afterwards): C1 discloses FROZEN_L1_DELTA_K1 = +128 L1 symbols beyond
# the frozen base by frozen-order-prefix extension (the disclosed L1 set
# is the first FROZEN_K1_C1 positions of the frozen P16 L1 order --
# isomorphic with the accepted K2 prefix rule, no reselection, no
# re-ranking, on ANY data).
FROZEN_L1_DELTA_K1 = 128
FROZEN_K1_C1 = 447  # 319 + 128
FROZEN_K_TOTAL_C1 = 6939  # 447 + 6492
FROZEN_C1_KEY_BIT_DELTA = 640  # 5 * 128 vs base
FROZEN_LEAKAGE_BITS = 34119  # 5 * 6811 + 64 (C0 base operational)
FROZEN_C1_LEAKAGE_BITS = 34759  # 5 * 6939 + 64 (C1 operational, +128 L1)
FROZEN_CONTROL_LEAKAGE_BITS = 32524  # 5 * 6492 + 64 (oracle arm, K1 = 0)
FROZEN_PUBLIC_CONTROL_BITS = seed_bits_for(FROZEN_N)  # 327743
FROZEN_RAW_INPUT_BITS = 10 * FROZEN_N  # 327680 per block

DISCLOSURE_RULE = (
    "single preregistered L1 disclosure step: C1_L1plus discloses "
    "FROZEN_L1_DELTA_K1 = +128 L1 symbols beyond the frozen base "
    "(K1 319 -> 447; K_total 6811 -> 6939) by FROZEN-ORDER-PREFIX "
    "EXTENSION -- the disclosed L1 set is the first 447 positions of "
    "the frozen P16 L1 order (positions fixed by the construction file, "
    "never selected on closed blocks, the consumed 1M pool, P20H DEV "
    "0..383, or new DEV data); C0 and C2 stay at base disclosure; the "
    "step replays P19's L1-fix quantum (319 -> 447); no second tier (no "
    "C1b) without a new packet"
)

# Development population: the NEXT 384 TRAIN frames of the independent
# 1.5M session file in (frame_id, pair_idx) order after the consumed
# P20H DEV prefix 0..383. Frozen TRAIN base 0 comes from JSON provenance
# only (split-manifest counts + frozen time-ordered split code + 0-based
# 1M precedent under the identical pipeline, carried over from P20H §3);
# the runner fail-closes on any layout drift before any SC call, so a
# wrong base BLOCKS instead of misattributing. The 1M full pool and the
# reserved 2M file are excluded by the cross-file source-tag+digest gate
# (never frame numbers alone); DEV must additionally overlap NONE of the
# 1.5M VAL/HOLD frame sets (intra-file gate, checked second) and NONE of
# the consumed P20H DEV prefix 0..383 (P20H-DEV exclusion gate, checked
# third).
FROZEN_DEV_FRAME_RANGE = (384, 767)
FROZEN_DEV_FRAMES = 384
FROZEN_DEV_PAIRS = 98304
FROZEN_BLOCK_COUNT = 3
FROZEN_BLOCK_FRAMES = 128
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME
FROZEN_BLOCK_RANGES = ((384, 511), (512, 639), (640, 767))
FROZEN_REMAINDER_FRAME_RANGE = (768, 1659)
FROZEN_REMAINDER_FRAMES = 892
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME
INTRA_FILE_VAL_FRAME_RANGE = (1660, 2212)  # 1.5M VAL; never selected
INTRA_FILE_HOLD_FRAME_RANGE = (2213, 2766)  # 1.5M HOLD; never selected
P20H_DEV_FRAME_RANGE = (0, 383)  # consumed P20H DEV prefix; never selected
# Split-manifest 1.5M TRAIN pool hosting the DEV prefix (TRAIN 1660 / VAL
# 553 / HOLD 554 by the frozen time-ordered split code; TRAIN base 0 by
# same-pipeline parity with the accepted 1M 0-based layout).
FROZEN_MANIFEST_TRAIN_FRAMES = 1660
FROZEN_MANIFEST_TRAIN_PAIRS = 424960
FROZEN_MANIFEST_VAL_FRAMES = 553
FROZEN_MANIFEST_VAL_PAIRS = 141568
FROZEN_MANIFEST_HOLD_FRAMES = 554
FROZEN_MANIFEST_HOLD_PAIRS = 141824

FROZEN_TAG_MASTER = 2026092230
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = TAG_BITS  # 64
SEED_PREFIX = "nbpolar-p20i-l1-disclosure-1p5m-seed"

OPERATIONAL_PROVENANCE = hbd.OPERATIONAL_PROVENANCE
ORACLE_PROVENANCE = hbd.ORACLE_PROVENANCE


@dataclass(frozen=True)
class ArmSpec:
    """One frozen P20I arm (never CLI-tunable, never extensible)."""

    name: str
    kind: str  # "operational" | "oracle_control"
    k1: int
    k2: int
    leakage_bits: int
    provenance: str


FROZEN_ARMS = (
    ArmSpec("C0_sc_base", "operational", FROZEN_K1, FROZEN_K2,
            FROZEN_LEAKAGE_BITS, OPERATIONAL_PROVENANCE),
    ArmSpec("C1_L1plus", "operational", FROZEN_K1_C1, FROZEN_K2,
            FROZEN_C1_LEAKAGE_BITS, OPERATIONAL_PROVENANCE),
    ArmSpec("C2_true_l1_diagnostic", "oracle_control", 0, FROZEN_K2,
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
)  # 304206 = 3*34119 + 3*34759 + 3*32524
FROZEN_TOTAL_PUBLIC_CONTROL_BITS = PLANNED_TAG_INVOCATIONS * FROZEN_PUBLIC_CONTROL_BITS

# Stage-A frozen per-session calibration identity (carried over
# read-only from P20H): Stage B loads ONLY this digest-pinned prior file
# read-only; the V25 counts NPZ is never opened in Stage B (no counts
# path, no counts loader, no counts open). FROZEN_PRIOR_DIGEST and the
# recalibrated literals are frozen by the P20H Stage-A calibration
# product. This packet performs zero calibration opens.
FROZEN_PRIOR_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/"
    "per_session_calibration/calibrated_prior.npz"
)
FROZEN_PRIOR_DIGEST = "e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b"
# Accepted fitting-program constant (provenance: D4R2 nested-CV refit via
# prior_artifact.LAMBDA_STAR; must equal the calibration module pin).
FROZEN_LAMBDA = 137.3823795883264
# Recalibrated H1/H2/TOTAL literals from the Stage-A calibration product
# (replacing the 1M literals for the target_population_contract gate).
FROZEN_CAL_H1 = 2.006647056368773
FROZEN_CAL_H2 = 1.9017235959286112
FROZEN_CAL_H_TOTAL = 3.908370652297384
# Cross-file source identity (quadruple gate, first): the DEV content open
# must match this 1.5M pairs path + size/sha pin. Any 1M full-pool path or
# the reserved 2M path refuses before any SC call (bare frame integers
# collide across files, so source-tag + digest pin is the identity --
# never frame numbers alone). The paths are derived from the accepted 1M
# pairs path by session-tag substitution (no new path literal, so the
# no-production-path source ban stays intact); the 2M constant below is a
# refusal string only: the reserved file is never opened, statted, or read.
FROZEN_DEV_PAIRS_PATH = hm.FROZEN_HOLD_PAIRS_PATH.replace(
    "type2_1M_20260121_184040", "type2_1p5M_20260121_183806")
FROZEN_DEV_PAIRS_SIZE = 1869178  # build-manifest provenance pin (bytes)
FROZEN_DEV_PAIRS_SHA256 = (
    "ca351e5205e76600530121066af4e0e1e5278061745c0797368a49443570a06b"
)  # build-manifest provenance pin (never recomputed from content here)
REFUSED_1M_DEV_PAIRS_PATH = hm.FROZEN_HOLD_PAIRS_PATH  # 1M full pool; never DEV
REFUSED_2M_DEV_PAIRS_PATH = hm.FROZEN_HOLD_PAIRS_PATH.replace(
    "type2_1M_20260121_184040", "type2_2M_20260121_183657"
)  # reserved; refusal string only, never touched
FROZEN_MANIFEST_PATH = hm.FROZEN_MANIFEST_PATH
FROZEN_MANIFEST_SCHEMA = hm.FROZEN_MANIFEST_SCHEMA
FROZEN_CONSTRUCTION_PATH = hm.FROZEN_CONSTRUCTION_PATH
FROZEN_CONSTRUCTION_DIGEST = hm.FROZEN_CONSTRUCTION_DIGEST
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P20I-L1-DISCLOSURE-1P5M/"
    "l1_disclosure_1p5m"
)
PRIOR_LOADER_IDENTITY = (
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar."
    "per_session_calibration.load_calibrated_prior"
)
PAIRS_LOADER_IDENTITY = hm.PAIRS_LOADER_IDENTITY

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 600.0
EXTERNAL_TIMEOUT_S = 600
ULIMIT_VIRTUAL_KIB = 2097152

OUTCOMES = opf.OUTCOMES
COMPLETE_LABEL = "TARGET_EMPIRICAL_N32768_DEV_L1_DISCLOSURE_1P5M_COMPLETE"

SUPPORT_RULE = (
    "per-session TRAIN calibration (§3 program, Stage-A frozen): "
    "f = (counts + lambda*p_global)/(n_b + lambda) with the frozen "
    "lambda 137.3823795883264 on the 1.5M TRAIN counts array; every cell "
    "below 1e-15 replaced by 1e-15; columns renormalized; "
    "p_b = column totals / total count; P1/P2 = accepted "
    "derive_p1/derive_p2(f) under A=32*U1+U2; Stage B loads the "
    "digest-pinned calibrated_prior.npz read-only (no NPZ open, no "
    "refit, no relambda, no DEV contact before the freeze)"
)
DEV_BLOCK_RULE = (
    "TRAIN development formation (P18 pattern, P20I ranges): sort TRAIN rows by "
    "(frame_id, pair_idx); require exactly 384 frames 384..767, 256 rows "
    "per frame, pair_idx 0..255 and symbols 0..1023; blocks 384..511 / "
    "512..639 / 640..767 (128 frames = 32768 pairs each); frames "
    "768..1659 are the declared never-used remainder; the 1M full pool "
    "and the reserved 2M file never selected (cross-file gate first); "
    "1.5M VAL 1660..2212 and 1.5M HOLD 2213..2766 never selected "
    "(intra-file gate second); consumed P20H DEV 0..383 never selected "
    "(P20H-DEV exclusion gate third); "
    "no shuffle, resampling, "
    "overlap, padding, pooling or fitting"
)
ARM_RULE = (
    "three frozen arms in block-major order C0_sc_base / C1_L1plus / "
    "C2_true_l1_diagnostic per block; C0 and C1 run the frozen greedy SC "
    "(2 SC + 1 tag per block) with identical prior/floor/order/kernel/ "
    "representation/SC; C0 discloses the frozen base K1=319/K2=6492 while "
    "C1 discloses K1=447/K2=6492 (the single +128 L1 order-prefix step on "
    "the SAME frozen P16 L1 order); "
    "C2 discloses K2 only and runs one oracle-conditioned L2 SC; 15 SC "
    "calls and 9 tags total; C2 carries ORACLE_TRUE_L1_CONTROL provenance, "
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
    "and sentinel, identical for C0 and C1); C2 additionally conditions "
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
    "descriptive +128 L1-disclosure diagnostic on new-segment 1.5M TRAIN "
    "blocks (N=32768, three DEV blocks 384..767) under the frozen "
    "per-session-calibrated prior; C2 is an "
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
    "calibration_identity",
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
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.l1_disclosure_1p5m "
    f"--prior {FROZEN_PRIOR_PATH} --source 1p5M --floor 1e-15 "
    "--n 32768 --k1 319 --k2 6492 "
    f"--construction {FROZEN_CONSTRUCTION_PATH} --construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
    f"--dev-pairs {FROZEN_DEV_PAIRS_PATH} "
    "--dev-frames 384 767 --block-frames 128 --remainder-frames 768 1659 "
    "--tag-master 2026092230 --chunk-rows 512 --tag-bits 64 "
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

# Process-level one-open guards: set at the first content open/load, never cleared.
_PRIOR_CONTENT_LOADED = False
_DEV_PARQUET_CONTENT_OPENED = False


class L1Disclosure1p5mContractError(ValueError):
    """Pre-open DEV-population/formation failure: BLOCKED(<earliest gate>)."""


class L1Disclosure1p5mResourceError(RuntimeError):
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


def check_frozen_calibration_pins() -> dict:
    """Fail-closed pin of the Stage-A frozen calibration identity.

    Pure code-level check (no I/O): the lambda literal must equal the
    calibration-module pin (which itself equals
    ``prior_artifact.LAMBDA_STAR``), the floor must equal the frozen
    floor, the prior digest must be a real 64-hex pin (never the
    Stage-A sentinel), and the recalibrated literals must be finite.
    Any drift raises before any root exists.
    """
    from . import per_session_calibration as psc

    if float(FROZEN_LAMBDA) != float(psc.FROZEN_LAMBDA):
        raise ValueError("frozen calibration lambda drifted from the calibration module pin")
    if float(FROZEN_LAMBDA) != 137.3823795883264:
        raise ValueError("frozen calibration lambda != accepted procedure literal")
    if FROZEN_FLOOR != 1e-15:
        raise ValueError("frozen calibration floor drifted")
    digest = str(FROZEN_PRIOR_DIGEST)
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("frozen prior digest is not a Stage-A 64-hex pin")
    for name, value in (("h1", FROZEN_CAL_H1), ("h2", FROZEN_CAL_H2),
                        ("h_total", FROZEN_CAL_H_TOTAL)):
        if not isinstance(value, float) or not np.isfinite(value):
            raise ValueError(f"frozen recalibrated literal {name} is not finite")
    if abs((float(FROZEN_CAL_H1) + float(FROZEN_CAL_H2)) - float(FROZEN_CAL_H_TOTAL)) > 1e-12:
        raise ValueError("frozen recalibrated literals do not sum within 1e-12")
    return {
        "lambda": float(FROZEN_LAMBDA),
        "floor": float(FROZEN_FLOOR),
        "prior_digest": digest,
        "h1": float(FROZEN_CAL_H1),
        "h2": float(FROZEN_CAL_H2),
        "h_total": float(FROZEN_CAL_H_TOTAL),
    }


def verify_stage_b_prior(prior_arrays: dict, *, expected_h1=None, expected_h2=None,
                         expected_total=None) -> dict:
    """Verify the loaded calibrated prior against the Stage-A freeze.

    Pure array check (no I/O): canonical digest equality with the frozen
    Stage-A pin (calibration identity), lambda/floor pins, exact NPZ key
    set, and recomputed H1/H2/TOTAL within 1e-12 of the recalibrated
    literals (target population contract on the calibrated population).
    ``expected_*`` are the documented injected test seam; the frozen CLI
    always uses the frozen literals. Any mismatch raises before any SC
    call. Returns the verified ``p1``/``p2``/``p_b``/``counts`` views plus
    the recomputed digest and entropies.
    """
    if set(prior_arrays) != set(PRIOR_NPZ_KEYS):
        raise ValueError(
            f"prior keys must be exactly {sorted(PRIOR_NPZ_KEYS)}, got {sorted(prior_arrays)}"
        )
    digest = canonical_prior_digest({k: np.asarray(prior_arrays[k]) for k in PRIOR_NPZ_KEYS})
    failing = []
    if digest != str(FROZEN_PRIOR_DIGEST):
        failing.append("prior_digest_mismatch")
    if float(np.asarray(prior_arrays["lambda_star"])) != float(FROZEN_LAMBDA):
        failing.append("lambda_pin_mismatch")
    if float(np.asarray(prior_arrays["floor_value"])) != float(FROZEN_FLOOR):
        failing.append("floor_pin_mismatch")
    exp_h1 = float(FROZEN_CAL_H1) if expected_h1 is None else float(expected_h1)
    exp_h2 = float(FROZEN_CAL_H2) if expected_h2 is None else float(expected_h2)
    exp_total = float(FROZEN_CAL_H_TOTAL) if expected_total is None else float(expected_total)
    p_b = np.asarray(prior_arrays["p_b"], dtype=np.float64)
    p1 = np.asarray(prior_arrays["p1"], dtype=np.float64)
    p2 = np.asarray(prior_arrays["p2"], dtype=np.float64)
    try:
        from .target_construction import entropy_bits as _entropy_bits

        h1 = float(np.sum(p_b * _entropy_bits(p1, axis=0)))
        h2 = float(np.sum(p_b[None, :] * p1 * _entropy_bits(p2, axis=2)))
    except (ValueError, IndexError) as exc:
        raise ValueError(f"prior entropy recomputation failed: {exc}") from exc
    if abs(h1 - exp_h1) > 1e-12:
        failing.append("h1_matches_literal")
    if abs(h2 - exp_h2) > 1e-12:
        failing.append("h2_matches_literal")
    if abs((h1 + h2) - exp_total) > 1e-12:
        failing.append("total_matches_literal")
    if abs(float(p_b.sum()) - 1.0) > 1e-12:
        failing.append("p_b_normalized")
    if float(np.abs(p1.sum(axis=0) - 1.0).max()) > 1e-12:
        failing.append("conditional_columns_normalized")
    if failing:
        raise ValueError(
            "BLOCKED(calibration_identity/target_population_contract): failing checks: "
            + ",".join(failing)
        )
    counts_arr = np.asarray(prior_arrays["counts_ab"], dtype=np.float64)
    if counts_arr.shape != (1024, 1024):
        raise ValueError(f"prior counts_ab must be (1024,1024), got {counts_arr.shape}")
    return {
        "digest": digest,
        "p1": np.ascontiguousarray(p1),
        "p2": np.ascontiguousarray(p2),
        "p_b": np.ascontiguousarray(p_b),
        "counts": np.ascontiguousarray(counts_arr),
        "h1": h1,
        "h2": h2,
        "h_total": h1 + h2,
        "failing": (),
        "passed": True,
    }


def check_frozen_arm_table() -> dict:
    """Fail-closed pin of the three frozen arms and their design accounting.

    Pure code-level check (no I/O): arm order, K values, the single +128
    L1 prefix-extension step, leakage arithmetic, oracle label and the 15
    SC / 9 tag design totals. Any drift raises before any root exists.
    """
    if len(FROZEN_ARMS) != 3:
        raise ValueError(f"frozen arm table must hold 3 arms, got {len(FROZEN_ARMS)}")
    if FROZEN_ARM_NAMES != ("C0_sc_base", "C1_L1plus", "C2_true_l1_diagnostic"):
        raise ValueError(f"frozen arm order drifted: {FROZEN_ARM_NAMES!r}")
    base = FROZEN_ARMS[0]
    if (base.kind, base.k1, base.k2, base.leakage_bits, base.provenance) != (
        "operational", FROZEN_K1, FROZEN_K2, FROZEN_LEAKAGE_BITS,
        OPERATIONAL_PROVENANCE,
    ):
        raise ValueError("frozen C0_sc_base arm drifted from base")
    plus = FROZEN_ARMS[1]
    if (plus.kind, plus.k1, plus.k2, plus.leakage_bits, plus.provenance) != (
        "operational", FROZEN_K1_C1, FROZEN_K2, FROZEN_C1_LEAKAGE_BITS,
        OPERATIONAL_PROVENANCE,
    ):
        raise ValueError("frozen C1_L1plus arm drifted from base + 128")
    if int(plus.k1) - int(base.k1) != FROZEN_L1_DELTA_K1:
        raise ValueError("frozen L1 disclosure step must be exactly +128")
    if int(plus.leakage_bits) - int(base.leakage_bits) != FROZEN_C1_KEY_BIT_DELTA:
        raise ValueError("frozen C1 key-bit delta must be exactly +640 vs base")
    control = FROZEN_ARMS[2]
    if (control.kind, control.k1, control.k2, control.provenance) != (
        "oracle_control", 0, FROZEN_K2, ORACLE_PROVENANCE
    ):
        raise ValueError("frozen C2_true_l1_diagnostic arm drifted")
    if FROZEN_K1 + FROZEN_K2 != FROZEN_K_TOTAL:
        raise ValueError("frozen base K1+K2 != K_total")
    if FROZEN_K1_C1 != FROZEN_K1 + FROZEN_L1_DELTA_K1:
        raise ValueError("frozen C1 K1 != base K1 + 128")
    if FROZEN_K1_C1 + FROZEN_K2 != FROZEN_K_TOTAL_C1:
        raise ValueError("frozen C1 K1+K2 != C1 K_total")
    if FROZEN_LEAKAGE_BITS != DISCLOSED_BITS_PER_COORDINATE * FROZEN_K_TOTAL + TAG_BITS:
        raise ValueError("frozen base leakage != 5*(K1+K2)+64")
    if FROZEN_C1_LEAKAGE_BITS != DISCLOSED_BITS_PER_COORDINATE * FROZEN_K_TOTAL_C1 + TAG_BITS:
        raise ValueError("frozen C1 leakage != 5*(K1_C1+K2)+64")
    if FROZEN_CONTROL_LEAKAGE_BITS != DISCLOSED_BITS_PER_COORDINATE * FROZEN_K2 + TAG_BITS:
        raise ValueError("frozen control leakage != 5*K2+64")
    if PLANNED_SC_CALLS != 15:
        raise ValueError(f"frozen design must plan 15 SC calls, got {PLANNED_SC_CALLS}")
    if PLANNED_TAG_INVOCATIONS != 9:
        raise ValueError(f"frozen design must plan 9 tags, got {PLANNED_TAG_INVOCATIONS}")
    if FROZEN_L1_DELTA_K1 != 128:
        raise ValueError(f"frozen L1 disclosure step must be +128, got {FROZEN_L1_DELTA_K1}")
    h_total = float(opf.EXPECTED_H1 + opf.EXPECTED_H2)
    f_base = float(FROZEN_LEAKAGE_BITS / (FROZEN_N * h_total))
    if f_base > FROZEN_TARGET_F:
        raise ValueError("frozen base arm exceeds the accepted planning f<=1.3 budget")
    cap_ratio = float(FROZEN_LEAKAGE_BITS / FROZEN_RAW_INPUT_BITS)
    if not cap_ratio < 0.5:
        raise ValueError("frozen cap must sit well below raw input bits")
    c1_ratio = float(FROZEN_C1_LEAKAGE_BITS / FROZEN_RAW_INPUT_BITS)
    if not c1_ratio < 0.5:
        raise ValueError("frozen C1 cap must sit well below raw input bits")
    return {
        "arms": [spec.name for spec in FROZEN_ARMS],
        "planned_sc_calls": PLANNED_SC_CALLS,
        "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
        "l1_delta_k1": FROZEN_L1_DELTA_K1,
        "c1_k1": FROZEN_K1_C1,
        "base_leakage_bits": FROZEN_LEAKAGE_BITS,
        "c1_leakage_bits": FROZEN_C1_LEAKAGE_BITS,
        "c1_key_bit_delta_vs_base": FROZEN_C1_KEY_BIT_DELTA,
        "cap_vs_raw_ratio": cap_ratio,
        "c1_cap_vs_raw_ratio": c1_ratio,
    }


def verify_dev_source_identity(dev_pairs=None) -> dict:
    """Pin the 1.5M cross-file source identity (quadruple gate, FIRST).

    Pure string/constant check (no I/O): the DEV content-open path must be
    exactly the frozen 1.5M pairs path. The 1M full-pool path and the
    reserved 2M path refuse with their own messages (bare frame integers
    collide across files, so source-tag + digest pin is the identity --
    never frame numbers alone); any other path refuses as well. Raises
    before any root exists and before either protected content open,
    consuming nothing. The size/sha pins below are build-manifest
    provenance constants; the size is additionally enforced from stat
    before the content open at run level.
    """
    candidate = FROZEN_DEV_PAIRS_PATH if dev_pairs is None else str(dev_pairs)
    if candidate == REFUSED_1M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20I DEV source gate: 1M full-pool path refused "
            f"({REFUSED_1M_DEV_PAIRS_PATH!r}); the entire 1M pool is "
            "fail-closed against P20I DEV selection"
        )
    if candidate == REFUSED_2M_DEV_PAIRS_PATH:
        raise ValueError(
            "P20I DEV source gate: reserved 2M path refused "
            f"({REFUSED_2M_DEV_PAIRS_PATH!r}); the 2M file stays pristine "
            "under this packet"
        )
    if candidate != FROZEN_DEV_PAIRS_PATH:
        raise ValueError(
            "frozen point requires dev-pairs="
            f"{FROZEN_DEV_PAIRS_PATH!r}, got {candidate!r}"
        )
    # Self-consistency of the patchable path/size/sha provenance values
    # lives in the frozen-constants test (literals) and at run level
    # (stat-size enforcement); this dict pins only the never-patched
    # source vocabulary.
    checks = {
        "source": FROZEN_SOURCE == "1p5M",
        "source_tag": FROZEN_SOURCE_TAG == SOURCE_IDS[FROZEN_SOURCE],
    }
    failing = sorted(name for name, ok in checks.items() if not ok)
    if failing:
        raise ValueError("P20I DEV source identity mismatch: " + ",".join(failing))
    return {
        "source": FROZEN_SOURCE,
        "source_tag": FROZEN_SOURCE_TAG,
        "dev_pairs_path": FROZEN_DEV_PAIRS_PATH,
        "dev_pairs_size_bytes": FROZEN_DEV_PAIRS_SIZE,
        "dev_pairs_sha256": FROZEN_DEV_PAIRS_SHA256,
        "refused_1m_path": REFUSED_1M_DEV_PAIRS_PATH,
        "refused_2m_path": REFUSED_2M_DEV_PAIRS_PATH,
        "verified": True,
    }


def verify_dev_block_identity() -> dict:
    """Pin the P20I DEV ranges and their disjointness gates.

    Pure code-level check (no I/O). This is the quadruple gate's SECOND
    and THIRD parts: the cross-file source gate
    (``verify_dev_source_identity``) runs first. The DEV ranges must
    overlap NONE of the 1.5M VAL frame set 1660..2212 or the 1.5M HOLD
    frame set 2213..2766 (intra-file gate, checked second, VAL first),
    and NONE of the consumed P20H DEV prefix 0..383 (P20H-DEV exclusion
    gate, checked third); any overlap raises before any root exists and
    before either protected content open, consuming nothing. The VAL,
    HOLD and P20H-DEV checks run in that frozen order: all are safety
    properties and must fire even when the ranges also mismatch their
    literals.
    """
    val_first, val_last = INTRA_FILE_VAL_FRAME_RANGE
    for start, end in [tuple(r) for r in FROZEN_BLOCK_RANGES]:
        if not (end < val_first or start > val_last):
            raise ValueError(
                "P20I DEV block range "
                f"{start}..{end} overlaps 1.5M VAL {val_first}..{val_last}"
            )
    rem_first, rem_last = [int(v) for v in FROZEN_REMAINDER_FRAME_RANGE]
    if not (rem_last < val_first or rem_first > val_last):
        raise ValueError("P20I DEV remainder overlaps 1.5M VAL data")
    hold_first, hold_last = INTRA_FILE_HOLD_FRAME_RANGE
    for start, end in [tuple(r) for r in FROZEN_BLOCK_RANGES]:
        if not (end < hold_first or start > hold_last):
            raise ValueError(
                "P20I DEV block range "
                f"{start}..{end} overlaps 1.5M HOLD {hold_first}..{hold_last}"
            )
    if not (rem_last < hold_first or rem_first > hold_last):
        raise ValueError("P20I DEV remainder overlaps 1.5M HOLD data")
    p20h_first, p20h_last = P20H_DEV_FRAME_RANGE
    for start, end in [tuple(r) for r in FROZEN_BLOCK_RANGES]:
        if not (end < p20h_first or start > p20h_last):
            raise ValueError(
                "P20I DEV block range "
                f"{start}..{end} overlaps consumed P20H DEV {p20h_first}..{p20h_last}"
            )
    if not (rem_last < p20h_first or rem_first > p20h_last):
        raise ValueError("P20I DEV remainder overlaps consumed P20H DEV data")
    checks = {
        "n": FROZEN_N == int(hm.FROZEN_N),
        "base_k1": FROZEN_K1 == int(hm.FROZEN_K1),
        "base_k2": FROZEN_K2 == int(hm.FROZEN_K2),
        "block_count": FROZEN_BLOCK_COUNT == int(hm.FROZEN_BLOCK_COUNT),
        "block_frames": FROZEN_BLOCK_FRAMES == int(hm.FROZEN_BLOCK_FRAMES),
        "symbols_per_block": FROZEN_SYMBOLS_PER_BLOCK == int(hm.FROZEN_SYMBOLS_PER_BLOCK),
        "dev_frame_range": tuple(FROZEN_DEV_FRAME_RANGE) == (384, 767),
        "dev_frames": FROZEN_DEV_FRAMES == 384,
        "dev_pairs": FROZEN_DEV_PAIRS == 98304,
        "block_ranges": tuple(tuple(r) for r in FROZEN_BLOCK_RANGES)
        == ((384, 511), (512, 639), (640, 767)),
        "remainder_frame_range": tuple(FROZEN_REMAINDER_FRAME_RANGE) == (768, 1659),
        "remainder_frames": FROZEN_REMAINDER_FRAMES == 892,
        "remainder_symbols": FROZEN_REMAINDER_SYMBOLS == 228352,
        "intra_val_range": tuple(INTRA_FILE_VAL_FRAME_RANGE) == (1660, 2212),
        "intra_hold_range": tuple(INTRA_FILE_HOLD_FRAME_RANGE) == (2213, 2766),
        "p20h_dev_range": tuple(P20H_DEV_FRAME_RANGE) == (0, 383),
    }
    failing = sorted(name for name, ok in checks.items() if not ok)
    if failing:
        raise ValueError("P20I DEV block-range identity mismatch: " + ",".join(failing))
    return {
        "dev_frame_range": list(FROZEN_DEV_FRAME_RANGE),
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "remainder_frame_range": list(FROZEN_REMAINDER_FRAME_RANGE),
        "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
        "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
        "p20h_dev_frame_range": list(P20H_DEV_FRAME_RANGE),
        "intra_val_disjoint": True,
        "intra_hold_disjoint": True,
        "p20h_dev_disjoint": True,
        "verified": True,
    }


def verify_dev_manifest(path, *, source: str = FROZEN_SOURCE) -> dict:
    """Verify the V25 split manifest declares the 1.5M TRAIN development pool.

    JSON read only; no protected content open. The accepted
    ``verify_split_manifest`` helper is source-pinned to 1M by fail-closed
    equality (it refuses any other source), so this local check mirrors
    its validation line-for-line under the P20I source/pins: accepted
    schema, the 1.5M source tag, and exactly the TRAIN 1660/424960 +
    VAL 553/141568 + HOLD 554/141824 counts that host the P20I DEV segment
    (frames 384..767). Any mismatch raises before any root exists.
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
    if train_frames != FROZEN_MANIFEST_TRAIN_FRAMES or train_pairs != FROZEN_MANIFEST_TRAIN_PAIRS:
        raise ValueError(
            "dev split manifest identity: 1.5M TRAIN population "
            f"{train_frames} frames / {train_pairs} pairs "
            f"!= frozen {FROZEN_MANIFEST_TRAIN_FRAMES} / {FROZEN_MANIFEST_TRAIN_PAIRS}"
        )
    if val_frames != FROZEN_MANIFEST_VAL_FRAMES or val_pairs != FROZEN_MANIFEST_VAL_PAIRS:
        raise ValueError(
            "dev split manifest identity: 1.5M VAL population "
            f"{val_frames} frames / {val_pairs} pairs "
            f"!= frozen {FROZEN_MANIFEST_VAL_FRAMES} / {FROZEN_MANIFEST_VAL_PAIRS}"
        )
    if hold_frames != FROZEN_MANIFEST_HOLD_FRAMES or hold_pairs != FROZEN_MANIFEST_HOLD_PAIRS:
        raise ValueError(
            "dev split manifest identity: 1.5M HOLD population "
            f"{hold_frames} frames / {hold_pairs} pairs "
            f"!= frozen {FROZEN_MANIFEST_HOLD_FRAMES} / {FROZEN_MANIFEST_HOLD_PAIRS}"
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
        "dev_frames": FROZEN_MANIFEST_TRAIN_FRAMES,
        "dev_pairs": FROZEN_MANIFEST_TRAIN_PAIRS,
    }


def l1_disclosure_seed_bits(
    master: int,
    n: int,
    arm: str,
    block_index: int,
    *,
    bit_length: int | None = None,
) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P20I domain).

    Rule: concatenate SHA-256 over
    ``"nbpolar-p20i-l1-disclosure-1p5m-seed:<master>:<n>:<arm>:
    <block_index>:<counter>"`` for ``counter = 0, 1, ...`` (ASCII decimal),
    unpack each digest MSB-first and truncate to ``bit_length`` (default
    ``10*n + 63``). The P20I prefix and arm tokens differ from the P16, P17,
    P18, P19, P20B, P20C, P20E, P20F, P20G and P20H domains on purpose. Seed contents are public control
    and are never persisted; only the bit length is recorded.
    """
    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P20I seed domain: {arm!r}")
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

    P18 ``form_holdout_blocks`` pattern with P20I ranges (the accepted helper
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
        raise L1Disclosure1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"dev-frames {pair} != frozen {tuple(FROZEN_DEV_FRAME_RANGE)}"
        )
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise L1Disclosure1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"block-frames {block_frames} != frozen {FROZEN_BLOCK_FRAMES}"
        )
    try:
        rem_pair = tuple(opf._as_int(v, "remainder-frames", minimum=0) for v in remainder_frames)
    except TypeError as exc:
        raise TypeError(f"remainder-frames must be a pair of integers: {exc}") from exc
    if rem_pair != tuple(FROZEN_REMAINDER_FRAME_RANGE):
        raise L1Disclosure1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"remainder-frames {rem_pair} != frozen {tuple(FROZEN_REMAINDER_FRAME_RANGE)}"
        )
    try:
        frame_id = np.asarray(table["frame_id"], dtype=np.int64)
        pair_idx = np.asarray(table["pair_idx"], dtype=np.int64)
        alice = np.asarray(table["alice_symbol"], dtype=np.int64)
        bob = np.asarray(table["bob_symbol"], dtype=np.int64)
    except (KeyError, TypeError, ValueError) as exc:
        raise L1Disclosure1p5mContractError(
            f"BLOCKED(dev_population_exact): loader frame is malformed: {exc}"
        ) from exc
    if not (frame_id.shape == pair_idx.shape == alice.shape == bob.shape) or frame_id.ndim != 1:
        raise L1Disclosure1p5mContractError(
            "BLOCKED(dev_population_exact): column shapes disagree"
        )
    for name, values in (("alice_symbol", alice), ("bob_symbol", bob)):
        if values.size == 0 or values.min() < 0 or values.max() >= N_BOB:
            raise L1Disclosure1p5mContractError(
                f"BLOCKED(dev_population_exact): {name} outside 0..{N_BOB - 1}"
            )
    dev_first, dev_last = pair
    # The declared never-used remainder (768..1659) lies OUTSIDE the DEV
    # selection by design (frozen --dev-frames 384 767), so its presence
    # and span are measured from the unfiltered pool before DEV slicing;
    # the remainder is never decoded, only counted.
    pool_frame_id = np.asarray(table["frame_id"], dtype=np.int64)
    selected = (frame_id >= dev_first) & (frame_id <= dev_last)
    rows = int(np.sum(selected))
    if rows == 0:
        raise L1Disclosure1p5mContractError(
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
        raise L1Disclosure1p5mContractError(
            "BLOCKED(dev_population_exact): DEV frames "
            f"{unique_frames.size} with range {int(unique_frames[0])}..{int(unique_frames[-1])} "
            f"!= frozen {FROZEN_DEV_FRAMES} with range {dev_first}..{dev_last}"
        )
    if rows != FROZEN_DEV_PAIRS:
        raise L1Disclosure1p5mContractError(
            f"BLOCKED(dev_population_exact): DEV rows {rows} != frozen {FROZEN_DEV_PAIRS}"
        )
    order = np.lexsort((pair_idx, frame_id))
    frame_id = frame_id[order]
    pair_idx = pair_idx[order]
    alice = alice[order]
    bob = bob[order]
    expected_pair = np.tile(np.arange(FROZEN_PAIRS_PER_FRAME, dtype=np.int64), FROZEN_DEV_FRAMES)
    if not np.array_equal(pair_idx, expected_pair):
        raise L1Disclosure1p5mContractError(
            "BLOCKED(dev_population_exact): pair_idx is not exactly 0..255 per frame"
        )
    ranges = []
    first = dev_first
    for _ in range(FROZEN_BLOCK_COUNT):
        last = first + int(block_frames) - 1
        ranges.append((first, last))
        first = last + 1
    if tuple(ranges) != FROZEN_BLOCK_RANGES:
        raise L1Disclosure1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): block ranges "
            f"{tuple(ranges)} != frozen {FROZEN_BLOCK_RANGES}"
        )
    rem_first, rem_last = rem_pair
    if first != rem_first:
        raise L1Disclosure1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder "
            f"{rem_first}..{rem_last} does not start where the three DEV blocks end"
        )
    # Declared-remainder evidence from the unfiltered pool (never decoded):
    # exactly the frozen 892 frames 768..1659 with 228352 rows.
    remainder_rows = (pool_frame_id >= rem_first) & (pool_frame_id <= rem_last)
    remainder_frame_ids = pool_frame_id[remainder_rows]
    if int(np.sum(remainder_rows)) != FROZEN_REMAINDER_SYMBOLS:
        raise L1Disclosure1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder rows "
            f"{int(np.sum(remainder_rows))} != frozen {FROZEN_REMAINDER_SYMBOLS}"
        )
    if (np.unique(remainder_frame_ids).size != FROZEN_REMAINDER_FRAMES
            or int(remainder_frame_ids.min()) != rem_first
            or int(remainder_frame_ids.max()) != rem_last):
        raise L1Disclosure1p5mContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder frames "
            f"!= frozen {rem_first}..{rem_last} ({FROZEN_REMAINDER_FRAMES} frames)"
        )
    val_first, val_last = INTRA_FILE_VAL_FRAME_RANGE
    hold_first, hold_last = INTRA_FILE_HOLD_FRAME_RANGE
    p20h_first, p20h_last = P20H_DEV_FRAME_RANGE
    for start, end in ranges:
        if not (end < val_first or start > val_last):
            raise L1Disclosure1p5mContractError(
                "BLOCKED(blocks_exact_with_declared_remainder): DEV block "
                f"{start}..{end} overlaps 1.5M VAL {val_first}..{val_last}"
            )
        if not (end < hold_first or start > hold_last):
            raise L1Disclosure1p5mContractError(
                "BLOCKED(blocks_exact_with_declared_remainder): DEV block "
                f"{start}..{end} overlaps 1.5M HOLD {hold_first}..{hold_last}"
            )
        if not (end < p20h_first or start > p20h_last):
            raise L1Disclosure1p5mContractError(
                "BLOCKED(blocks_exact_with_declared_remainder): DEV block "
                f"{start}..{end} overlaps consumed P20H DEV {p20h_first}..{p20h_last}"
            )
    blocks = []
    for index, (start, end) in enumerate(ranges):
        mask = (frame_id >= start) & (frame_id <= end)
        if int(np.sum(mask)) != FROZEN_SYMBOLS_PER_BLOCK:
            raise L1Disclosure1p5mContractError(
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


def l1_prefix_positions(l1_order, k1: int) -> np.ndarray:
    """Frozen-order-prefix L1 disclosure positions for a registered arm.

    The disclosed L1 set is the first ``k1`` positions of the SAME frozen
    P16 L1 order (C0: ``k1 = 319``; C1: ``k1 = 447``) -- isomorphic with
    the accepted K2 prefix rule, no reselection, no re-ranking, on ANY
    data (P20I DEV, P20H DEV, closed 1M ranges, 2M). Positions are fixed
    by the construction file, never selected on closed blocks, the
    consumed 1M pool, consumed P20H DEV, or new DEV data. Pure view
    helper; takes no decision input.
    """
    order = np.asarray(l1_order, dtype=np.int64)
    k1 = opf._as_int(k1, "k1", minimum=0)
    if k1 > order.size:
        raise ValueError(f"k1={k1} exceeds the frozen L1 order length {order.size}")
    return order[:k1]


def l2_prefix_positions(l2_order, k2: int) -> np.ndarray:
    """Frozen-order-prefix L2 disclosure positions for a registered arm.

    The disclosed L2 set is the first ``k2`` positions of the frozen P16
    L2 order (all P20I arms: ``k2 = 6492`` base). Positions are fixed
    by the construction file, never selected on closed blocks, the
    consumed 1M pool, consumed P20H DEV, or new DEV data. Pure view
    helper; takes no decision input.
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
    is_plus = bool(spec.name == "C1_L1plus")
    record.update({
        "l1_delta_k1_applied": int(FROZEN_L1_DELTA_K1) if is_plus else 0,
        "l1_disclosure_rule": (
            "frozen-order-prefix-extension" if is_plus else "base"),
        "key_bit_delta_vs_base": int(FROZEN_C1_KEY_BIT_DELTA) if is_plus else 0,
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
        "l1_delta_k1_applied": 0,
        "l1_disclosure_rule": "base",
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
        "l1_delta_k1_applied": None,
        "l1_disclosure_rule": None,
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
        if spec.name == "C1_L1plus":
            if int(record.get("l1_delta_k1_applied", -1)) != FROZEN_L1_DELTA_K1:
                return False
            if record.get("l1_disclosure_rule") != "frozen-order-prefix-extension":
                return False
            if int(record.get("key_bit_delta_vs_base", -1)) != FROZEN_C1_KEY_BIT_DELTA:
                return False
        else:
            if int(record.get("l1_delta_k1_applied", -1)) != 0:
                return False
            if record.get("l1_disclosure_rule") != "base":
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
    """C2 provenance isolation: excluded from every operational aggregate."""
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
    """Descriptive per-arm recovery plus the C1-vs-C0 disclosure comparison.

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
    c0_by_block = {r.get("block_index"): r for r in by_arm["C0_sc_base"]}
    c1_by_block = {r.get("block_index"): r for r in by_arm["C1_L1plus"]}
    for block_index in sorted(set(c0_by_block) | set(c1_by_block)):
        r0 = c0_by_block.get(block_index, {})
        r1 = c1_by_block.get(block_index, {})
        disclosure_blocks.append({
            "block_index": int(block_index),
            "c0_exact": r0.get("exact"),
            "c0_outcome": r0.get("outcome"),
            "c1_exact": r1.get("exact"),
            "c1_outcome": r1.get("outcome"),
            "l1_delta_k1_applied": r1.get("l1_delta_k1_applied"),
            "c1_restored_given_c0_failed": bool(
                r1.get("exact") is True and r0.get("exact") is not True),
        })
    c1_records = by_arm["C1_L1plus"]
    return {
        "per_arm": per_arm,
        "c1_restored_count": sum(
            1 for r in disclosure_blocks if r.get("c1_restored_given_c0_failed") is True),
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


def l1_disclosure_1p5m_label(gates: dict) -> str:
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
            f"nbpolar-p20i-l1-disclosure-1p5m:{int(n)}:{int(frame_start)}:{int(block_index)}"
        ),
        "method": "nbpolar_l1_disclosure_1p5m",
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


def l1_disclosure_block_events(n: int, spec, block_index: int, frame_start: int, record) -> list:
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


def l1_disclosure_recount_events(events) -> dict:
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
class L1Disclosure1p5mRun:
    """In-memory P20I diagnostic run (also returned by the runner)."""

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
    prior_path, prior_digest, dev_pairs, manifest_path, dev_frames, block_frames,
    remainder_frames, tag_master, chunk_rows, tag_bits, identity, manifest,
    dev_source_pin, dev_pin,
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
        "l1_delta_k1": int(FROZEN_L1_DELTA_K1),
        "c1_k1": int(FROZEN_K1_C1),
        "c1_k_total": int(FROZEN_K_TOTAL_C1),
        "construction": str(construction),
        "construction_digest": str(digest),
        "prior_path": str(prior_path),
        "prior_digest": str(prior_digest),
        "calibration_lambda": float(FROZEN_LAMBDA),
        "calibration_floor": float(FROZEN_FLOOR),
        "recalibrated_h1": float(FROZEN_CAL_H1),
        "recalibrated_h2": float(FROZEN_CAL_H2),
        "recalibrated_h_total": float(FROZEN_CAL_H_TOTAL),
        "dev_pairs": str(dev_pairs),
        "manifest_path": str(manifest_path),
        "dev_frames": [int(dev_frames[0]), int(dev_frames[1])],
        "block_frames": int(block_frames),
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "remainder_frames": [int(remainder_frames[0]), int(remainder_frames[1])],
        "dev_source": dict(dev_source_pin),
        "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
        "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
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
        "c1_leakage_bits": int(FROZEN_C1_LEAKAGE_BITS),
        "c1_key_bit_delta_vs_base": int(FROZEN_C1_KEY_BIT_DELTA),
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
        "single_factor": "ONE preregistered change vs P20H: L1 disclosure +128 via the frozen order-prefix rule (Stage-A frozen, read-only in Stage B); per-session prior digest-pinned read-only, K2 base, floor, construction-order, kernel, representation and SC carried over from P20H; only the +128 L1 step and the new P20I tag domain differ",
        "deferred": ["c1-restoration maintain-confirmation round", "c1-zero-restoration P20D fixed-disclosure alternative L2 construction", "disclosure-minimality probe (+64 vs +128 vs +256)", "efficiency optimization round", "second independent session on the reserved 2M file"],
    }
    opf._write_json(out_path / "frozen_plan.json", plan)
    identity_doc = {
        "predecessor_construction": identity,
        "split_manifest": manifest,
        "dev_source_pin": dev_source_pin,
        "dev_source_pin": dev_source_pin,
        "dev_block_pin": dev_pin,
        "expected_prior_digest": str(FROZEN_PRIOR_DIGEST),
        "recalibrated_literals": {
            "h1": float(FROZEN_CAL_H1),
            "h2": float(FROZEN_CAL_H2),
            "h_total": float(FROZEN_CAL_H_TOTAL),
        },
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
    }
    opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
    (out_path / "per_block_arm_outcomes.jsonl").write_text("", encoding="utf-8")
    opf._write_json(out_path / "aggregate_summary.json", {"status": "RUNNING"})
    (out_path / "report.md").write_text("# P20I l1 disclosure 1p5m (RUNNING)\n", encoding="utf-8")
    return plan


def _render_report(summary: dict) -> str:
    lines = [
        "# NB-Polar Phase 4-P20I l1 disclosure 1p5m",
        "",
        f"- protocol: `{summary['analysis']}` (mode `{summary['mode']}`)",
        f"- source: `{summary['source']}`; n={summary['n']}, "
        f"k1={summary['k1']}, k2={summary['k2']}, C1 K1={summary['c1_k1']} "
        f"(+{summary['l1_delta_k1']} L1 order-prefix step)",
        f"- DEV blocks: {summary['block_ranges']}; remainder {summary['remainder_frames']} (never used)",
        f"- DEV source: `{summary['dev_source']['dev_pairs_path']}` "
        f"(size {summary['dev_source']['dev_pairs_size_bytes']} B, sha "
        f"`{summary['dev_source']['dev_pairs_sha256'][:8]}...`; 1M full pool "
        "and reserved 2M refused by the cross-file gate); "
        f"1.5M VAL: {summary['intra_file_val_frame_range']} (never selected); "
        f"1.5M HOLD: {summary['intra_file_hold_frame_range']} (never selected)",
        f"- base cap: {summary['base_leakage_bits']} key bits/block; "
        f"C1 cap: {summary['c1_leakage_bits']} key bits/block "
        f"(raw {summary['raw_input_bits_per_block']} bits; ratios "
        f"{summary['cap_vs_raw_ratio']:.6f} / {summary['c1_cap_vs_raw_ratio']:.6f})",
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
        "## C1-vs-C0 disclosure comparison (descriptive)",
        "",
        f"- C1 restored a complete block where C0 failed on "
        f"{recovery['c1_restored_count']}/{len(recovery['disclosure_blocks'])} blocks",
    ]
    for row in recovery["disclosure_blocks"]:
        lines.append(
            f"- block {row['block_index']}: C0 {row['c0_outcome']} "
            f"(exact={row['c0_exact']}) vs C1 {row['c1_outcome']} "
            f"(exact={row['c1_exact']}, dK1={row['l1_delta_k1_applied']}, "
            f"restored={row['c1_restored_given_c0_failed']})"
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
    *, out_path, n, k1, k2, identity, manifest, dev_source_pin, dev_pin,
    l1_order, l2_order,
    formation, records, events, calls, incremental, accounting,
    provenance_violations, start, cap, resource_stop, precondition_passed,
    calibration_passed,
    final, prior_stat_before, prior_stat_after, dev_stat_before, dev_stat_after,
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
    try:
        source_now = verify_dev_source_identity()
    except ValueError:
        source_now = None
    dev_pin_ok = bool(
        isinstance(dev_source_pin, dict)
        and dev_source_pin.get("verified") is True
        and isinstance(source_now, dict)
        and source_now.get("verified") is True
        and isinstance(dev_pin, dict)
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
    # Block-major slot order: (C0,C1,C2) per block; each arm covers each block.
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
        recount = l1_disclosure_recount_events(events)
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
            "prior": 1 if accounting.get("prior_input_mode") == "frozen_prior_file" else 0,
            "dev": 1 if accounting.get("dev_input_mode") == "pairs_parquet" else 0,
        }
        one_open_ok = bool(
            int(accounting["counts_content_opens"]) == 0
            and int(accounting["prior_content_loads"]) == expected_opens["prior"]
            and int(accounting["dev_content_opens"]) == expected_opens["dev"]
            and int(accounting["attempts_consumed_by_this_run"]) == 1
            and int(accounting["retries"]) == 0
            and not bool(accounting["reopen_attempted"])
            and not bool(accounting["retry_after_open"])
        )
    else:
        one_open_ok = bool(
            int(accounting["counts_content_opens"]) == 0
            and int(accounting["prior_content_loads"]) == 0
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
        stat_unchanged(prior_stat_before, prior_stat_after)
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
        "calibration_identity": bool(calibration_passed),
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
        f"# P20I l1 disclosure 1p5m\n\nBLOCKED({message})\n", encoding="utf-8")


def run_l1_disclosure_1p5m(
    *,
    prior=None,
    prior_path=FROZEN_PRIOR_PATH,
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
    expected_literals=None,
) -> L1Disclosure1p5mRun:
    """Execute the frozen P20I three-arm diagnostic once; write five files.

    ``prior`` and ``dev_table`` plus ``expected_literals`` are documented
    injected test seams; the frozen CLI passes only the frozen point, loads
    the Stage-A frozen calibrated prior read-only exactly once, and reads
    the DEV parquet through its accepted loader exactly once. The V25
    counts NPZ is never opened in Stage B. The +128 L1 step on C1 is
    hardcoded (never CLI-tunable): C1 runs the accepted operational path
    with ``k1 = base k1 + 128`` on the same frozen L1 order
    (order-prefix extension, isomorphic with the K2 rule).
    """
    global _PRIOR_CONTENT_LOADED, _DEV_PARQUET_CONTENT_OPENED
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
    check_frozen_calibration_pins()

    # Predecessor identity, cross-file source gate, split manifest and
    # the DEV pin are verified before any root exists and before either
    # content open/load; a mismatch consumes nothing. Gate order is
    # frozen: cross-file source-tag+digest gate first, intra-file
    # DEV-vs-VAL/HOLD gate second.
    if str(construction_digest) != FROZEN_CONSTRUCTION_DIGEST:
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = verify_predecessor_construction(construction, expected_digest=construction_digest)
    identity = verified["record"]
    dev_source_pin = verify_dev_source_identity(dev_pairs)
    manifest = verify_dev_manifest(manifest_path, source=source)
    dev_pin = verify_dev_block_identity()
    l1_order = np.asarray(verified["l1_order"], dtype=np.int64)
    l2_order = np.asarray(verified["l2_order"], dtype=np.int64)

    # One-open guards are refusals before any content load/open of either input.
    if prior is None and _PRIOR_CONTENT_LOADED:
        raise ValueError("reload refused: the single prior content load was already consumed")
    if dev_table is None and _DEV_PARQUET_CONTENT_OPENED:
        raise ValueError("reopen refused: the single DEV parquet content open was already consumed")

    # Input existence and stat-only metadata come before any content load/open.
    real_prior = prior is None
    real_dev = dev_table is None
    if real_prior:
        prior_file = Path(prior_path)
        if not prior_file.is_file():
            raise FileNotFoundError(f"Stage-A calibrated prior not found: {prior_file}")
        prior_stat_before = _stat_record(prior_file)
    else:
        prior_stat_before = _stat_record(None)
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
    if real_prior:
        registered_paths.append(str(Path(prior_path).resolve()))
    if real_dev:
        registered_paths.append(str(Path(dev_pairs).resolve()))
    opened_paths: list[str] = []

    plan = _stub_plan(
        out_path=out_path, source=source, floor=floor, n=n, k1=k1, k2=k2,
        construction=construction, digest=construction_digest,
        prior_path=prior_path if real_prior else None,
        prior_digest=str(FROZEN_PRIOR_DIGEST), dev_pairs=dev_pairs,
        manifest_path=manifest_path, dev_frames=dev_frames, block_frames=block_frames,
        remainder_frames=remainder_frames, tag_master=tag_master, chunk_rows=chunk_rows,
        tag_bits=tag_bits, identity=identity, manifest=manifest,
        dev_source_pin=dev_source_pin, dev_pin=dev_pin,
    )
    accounting = {
        "input_mode": "real" if (real_prior or real_dev) else "injected",
        "prior_input_mode": "frozen_prior_file" if real_prior else "injected_prior",
        "dev_input_mode": "pairs_parquet" if real_dev else "injected_table",
        "prior_path": str(prior_path) if real_prior else None,
        "dev_pairs_path": str(dev_pairs) if real_dev else None,
        "manifest_path": str(manifest_path),
        "construction_path": str(construction),
        "prior_loader": PRIOR_LOADER_IDENTITY if real_prior else None,
        "pairs_loader": PAIRS_LOADER_IDENTITY if real_dev else None,
        "registered_content_paths": registered_paths,
        "opened_content_paths": opened_paths,
        "artifact_content_reads_allowed_per_input": 1,
        "counts_content_opens": 0,
        "prior_content_loads": 0,
        "dev_content_opens": 0,
        "attempts_allowed": 1,
        "attempts_consumed_by_this_run": 0,
        "retries": 0,
        "reopen_attempted": False,
        "retry_after_open": False,
    }

    start = time.perf_counter()
    try:
        # ---- input 1: the single Stage-A prior load + calibration-identity gate.
        if real_prior:
            loaded_prior = load_calibrated_prior(str(prior_path))
            _PRIOR_CONTENT_LOADED = True
            accounting["prior_content_loads"] = 1
            opened_paths.append(str(Path(prior_path).resolve()))
            prior_arrays = dict(loaded_prior["arrays"])
        else:
            prior_arrays = dict(prior)
        # ---- frozen calibration identity + recalibrated-literal contract:
        # no SC call may happen before this passes.
        if expected_literals is None:
            verified_prior = verify_stage_b_prior(prior_arrays)
        else:
            exp_h1, exp_h2, exp_total = (float(v) for v in expected_literals)
            verified_prior = verify_stage_b_prior(
                prior_arrays, expected_h1=exp_h1, expected_h2=exp_h2,
                expected_total=exp_total,
            )
        p1 = verified_prior["p1"]
        p2 = verified_prior["p2"]
        counts_arr = verified_prior["counts"]
        precondition_passed = bool(verified_prior["passed"])
        calibration_passed = True  # digest+pin part passed iff no raise above

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
                manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
                l1_order=l1_order, l2_order=l2_order,
                formation=formation, records=records, events=events, calls=calls,
                incremental=incremental, accounting=accounting,
                provenance_violations=provenance_violations, start=start,
                cap=budget_cap, resource_stop=resource_stop,
                precondition_passed=bool(precondition_passed),
                calibration_passed=bool(calibration_passed), final=final,
                prior_stat_before=prior_stat_before, prior_stat_after=prior_stat_before,
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
                "l1_delta_k1": int(FROZEN_L1_DELTA_K1),
                "c1_k1": int(FROZEN_K1_C1),
                "c1_k_total": int(FROZEN_K_TOTAL_C1),
                "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
                "remainder_frames": list(FROZEN_REMAINDER_FRAME_RANGE),
                "dev_source": dict(dev_source_pin),
                "intra_file_val_frame_range": list(INTRA_FILE_VAL_FRAME_RANGE),
                "intra_file_hold_frame_range": list(INTRA_FILE_HOLD_FRAME_RANGE),
                "base_leakage_bits": int(FROZEN_LEAKAGE_BITS),
                "c1_leakage_bits": int(FROZEN_C1_LEAKAGE_BITS),
                "c1_key_bit_delta_vs_base": int(FROZEN_C1_KEY_BIT_DELTA),
                "raw_input_bits_per_block": int(FROZEN_RAW_INPUT_BITS),
                "cap_vs_raw_ratio": float(FROZEN_LEAKAGE_BITS / FROZEN_RAW_INPUT_BITS),
                "c1_cap_vs_raw_ratio": float(FROZEN_C1_LEAKAGE_BITS / FROZEN_RAW_INPUT_BITS),
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
            seed = l1_disclosure_seed_bits(tag_master, n, spec.name, block_index,
                                            bit_length=seed_bits_for(n))

            def _tag_fn(bits, _seed, tag_bits, _fixed=seed):
                return toeplitz_tag(bits, _fixed, tag_bits)

            block_start = time.perf_counter()
            if spec.kind == "operational":
                # C0 and C1 share the accepted operational path bit-for-bit
                # except the disclosed L1 prefix length: C0 runs k1=319
                # (base) while C1 runs k1=447 (the single frozen +128
                # order-prefix step) on the SAME frozen L1 order. The step
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
            for event in l1_disclosure_block_events(n, spec, block_index, frame_start, record):
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
        if real_prior:
            prior_stat_after = _stat_record(Path(prior_path))
        else:
            prior_stat_after = _stat_record(None)
        if real_dev:
            dev_stat_after = _stat_record(Path(dev_pairs))
        else:
            dev_stat_after = _stat_record(None)
        gates = _integrity_gates(
            out_path=out_path, n=n, k1=k1, k2=k2, identity=identity,
            manifest=manifest, dev_source_pin=dev_source_pin, dev_pin=dev_pin,
                l1_order=l1_order, l2_order=l2_order,
            formation=formation, records=records, events=events, calls=calls,
            incremental=incremental, accounting=accounting,
            provenance_violations=provenance_violations, start=start,
            cap=budget_cap, resource_stop=resource_stop,
            precondition_passed=bool(precondition_passed),
            calibration_passed=bool(calibration_passed), final=True,
            prior_stat_before=prior_stat_before, prior_stat_after=prior_stat_after,
            dev_stat_before=dev_stat_before, dev_stat_after=dev_stat_after,
            registered_paths=registered_paths, opened_paths=opened_paths,
        )
        outcome_label = l1_disclosure_1p5m_label(gates)
        summary = partial_summary(outcome_label, gates)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        identity_doc = {
            "predecessor_construction": identity,
            "split_manifest": manifest,
            "dev_source_pin": dev_source_pin,
        "dev_block_pin": dev_pin,
            "expected_prior_digest": str(FROZEN_PRIOR_DIGEST),
            "recalibrated_literals": {
                "h1": float(FROZEN_CAL_H1),
                "h2": float(FROZEN_CAL_H2),
                "h_total": float(FROZEN_CAL_H_TOTAL),
            },
            "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
            "prior_stat_before": prior_stat_before,
            "prior_stat_after": prior_stat_after,
            "dev_stat_before": dev_stat_before,
            "dev_stat_after": dev_stat_after,
            "attempt_read_accounting": dict(accounting, opened_content_paths=list(opened_paths)),
        }
        opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
        persist(summary)
        return L1Disclosure1p5mRun(summary=summary, records=tuple(records), gates=gates)
    except L1Disclosure1p5mResourceError as exc:
        _finalize_blocked_with_accounting(
            out_path, accounting, opened_paths, resource_stop or str(exc))
        raise
    except MemoryError as exc:
        label = f"resource stop: MemoryError: {exc}"
        try:
            _finalize_blocked_with_accounting(out_path, accounting, opened_paths, label)
        except (OSError, ValueError):
            pass
        raise L1Disclosure1p5mResourceError(label) from exc


def _finalize_blocked_with_accounting(out_path, accounting, opened_paths, message: str) -> None:
    summary = {
        "analysis": PROTOCOL_NAME,
        "outcome_label": f"BLOCKED({message})",
        "attempt_read_accounting": dict(accounting, opened_content_paths=list(opened_paths)),
    }
    opf._write_json(Path(out_path) / "aggregate_summary.json", summary)
    (Path(out_path) / "report.md").write_text(
        f"# P20I l1 disclosure 1p5m\n\nBLOCKED({message})\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p20i-l1-disclosure-1p5m",
        description=(
            "NB-Polar Phase 4-P20I N=32768 L1-disclosure +128 single-factor "
            "diagnostic (Stage-A frozen calibrated prior, verified P16 "
            "construction, three new-segment 1.5M TRAIN DEV blocks, three "
            "frozen arms)"
        ),
    )
    parser.add_argument("--prior", required=True)
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
        run = run_l1_disclosure_1p5m(
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
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p20i l1 disclosure 1p5m refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "records_completed": summary["records_completed"],
                "operational_exact_count": summary["aggregates"]["operational"]["exact_count"],
                "c1_restored_count": summary["aggregates"]["recovery"]["c1_restored_count"],
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
    "FROZEN_K_TOTAL", "FROZEN_L1_DELTA_K1", "FROZEN_K1_C1", "FROZEN_K_TOTAL_C1",
    "FROZEN_C1_KEY_BIT_DELTA", "FROZEN_LEAKAGE_BITS", "FROZEN_C1_LEAKAGE_BITS",
    "FROZEN_CONTROL_LEAKAGE_BITS",
    "FROZEN_PUBLIC_CONTROL_BITS", "FROZEN_RAW_INPUT_BITS",
    "DISCLOSURE_RULE",
    "FROZEN_DEV_FRAME_RANGE", "FROZEN_DEV_FRAMES", "FROZEN_DEV_PAIRS",
    "FROZEN_BLOCK_COUNT", "FROZEN_BLOCK_FRAMES", "FROZEN_PAIRS_PER_FRAME",
    "FROZEN_SYMBOLS_PER_BLOCK", "FROZEN_BLOCK_RANGES",
    "FROZEN_REMAINDER_FRAME_RANGE", "FROZEN_REMAINDER_FRAMES",
    "FROZEN_REMAINDER_SYMBOLS", "INTRA_FILE_VAL_FRAME_RANGE",
    "INTRA_FILE_HOLD_FRAME_RANGE",
    "FROZEN_MANIFEST_TRAIN_FRAMES", "FROZEN_MANIFEST_TRAIN_PAIRS",
    "FROZEN_MANIFEST_VAL_FRAMES", "FROZEN_MANIFEST_VAL_PAIRS",
    "FROZEN_MANIFEST_HOLD_FRAMES", "FROZEN_MANIFEST_HOLD_PAIRS",
    "P20H_DEV_FRAME_RANGE",
    "FROZEN_TAG_MASTER", "FROZEN_CHUNK_ROWS", "FROZEN_TAG_BITS",
    "SEED_PREFIX", "OPERATIONAL_PROVENANCE", "ORACLE_PROVENANCE",
    "FROZEN_PRIOR_PATH", "FROZEN_PRIOR_DIGEST", "FROZEN_LAMBDA",
    "FROZEN_CAL_H1", "FROZEN_CAL_H2", "FROZEN_CAL_H_TOTAL",
    "FROZEN_DEV_PAIRS_PATH",
    "FROZEN_DEV_PAIRS_SIZE", "FROZEN_DEV_PAIRS_SHA256",
    "REFUSED_1M_DEV_PAIRS_PATH", "REFUSED_2M_DEV_PAIRS_PATH",
    "FROZEN_SOURCE_TAG",
    "FROZEN_MANIFEST_PATH", "FROZEN_MANIFEST_SCHEMA", "FROZEN_CONSTRUCTION_PATH",
    "FROZEN_CONSTRUCTION_DIGEST", "FROZEN_OUT_ROOT", "PRIOR_LOADER_IDENTITY",
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
    "L1Disclosure1p5mContractError", "L1Disclosure1p5mResourceError",
    "L1Disclosure1p5mRun", "check_frozen_arm_table",
    "check_frozen_calibration_pins", "verify_stage_b_prior",
    "verify_dev_source_identity", "verify_dev_block_identity",
    "verify_dev_manifest",
    "l1_disclosure_seed_bits", "form_dev_blocks", "candidate_nll_bits",
    "raw_floor_diagnostics", "first_error_coordinate",
    "l1_prefix_positions", "l2_prefix_positions",
    "run_operational_block", "run_oracle_control_block", "OracleControlResult",
    "verify_predecessor_construction", "verify_split_manifest",
    "holdout_nll_bits", "raw_symbol_error_rate", "form_holdout_blocks",
    "polar_transform_fn", "make_gf32_fn", "toeplitz_tag_fn",
    "build_p1_metrics_fn", "gather_p2_metrics_fn", "probs_to_symbol_metric_fn",
    "oracle_isolation_ok", "recovery_diagnostics", "build_aggregates",
    "l1_disclosure_1p5m_label", "l1_disclosure_block_events",
    "l1_disclosure_recount_events", "run_l1_disclosure_1p5m",
    "build_parser", "main",
]
