"""NB-Polar Phase 4-P19 N=32768 1M-HOLD layer/backoff diagnostic.

Frozen packet ``NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC``, OpenSpec
``formal-ir-nbpolar-phase4-p0`` P19 delta: on the exact three accepted P18
HOLD blocks (frames 1600..1727, 1728..1855, 1856..1983 of the 1M
``pairs.parquet``, 128 frames = 32768 pairs each) determine *descriptively*
whether additional L1 disclosure (+128 coordinates), additional L2
disclosure (+512 coordinates), both, or true-L1 conditioning changes hard
recovery.  This is the smallest finite-length backoff diagnostic justified
by P18's 0/3 accepted descriptive microcheck.  It has no FER, winner,
monotonicity or qualification threshold: every recovery pattern is a
descriptive COMPLETE when integrity holds.

Frozen semantics:

- Predecessor identity first, before any output root exists and before
  either protected content open: the P16 accepted
  ``construction_and_allocation.json`` is read (JSON only) and verified
  (N=32768, K_total=6811, K1=319, K2=6492, valid L1/L2 orders, canonical
  digest ``055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b``,
  K/f replay ``leakage 34119 <= 1.3*N*H``); the V25 run_04
  ``split_manifest.json`` is read (JSON only) and must declare the 1M
  source as 400 HOLD frames / 102400 HOLD pairs; and the accepted P18
  module is pinned at code level (same N, base K1/K2, block ranges,
  remainder, frame range).  Any mismatch stops with zero protected reads
  and zero attempts.
- Protected inputs, each content-opened exactly once: (1) the V25 1M TRAIN
  ``channel_counts.npz`` through the accepted ``load_v25_channel_counts``
  after a stat-only size check of exactly ``25,166,822`` bytes, used only
  to rebuild the frozen floor-1e-15 prior and repeat the accepted
  population guards; (2) the 1M ``pairs.parquet`` through the accepted
  ``load_pairs_table``/``normalize_pair_columns`` loader, used only for
  HOLD frames 1600..1999.  The single scientific attempt is consumed at
  the first protected content open (the NPZ); module-level guards refuse
  any second content open of either input.  Input size/mtime are recorded
  (stat only) before the opens and re-checked unchanged after the run.
- Deterministic block formation through the accepted P18
  ``form_holdout_blocks``: sort HOLD rows by ``(frame_id, pair_idx)``;
  require exactly 400 frames 1600..1999, exactly 256 rows per frame,
  ``pair_idx`` 0..255 and symbols 0..1023.  Blocks are frames
  1600..1727, 1728..1855 and 1856..1983 (three exact non-overlapping
  N=32768 blocks); frames 1984..1999 (4096 pairs) are the declared unused
  remainder and never enter any block.  No shuffle, resampling, overlap,
  padding, pooling or fitting anywhere; the runner contains no
  random-number generator path.
- Five frozen arms, run in this exact order, using the verified P16
  empirical orders and ``chunk_rows=512`` with the P19 tag master
  ``2026092060`` and P19/arm/block seed-domain separation:
  1. ``base``: operational K1=319, K2=6492; leakage 34119 bits.
  2. ``l1_plus``: operational K1=447, K2=6492; leakage 34759 bits.
  3. ``l2_plus``: operational K1=319, K2=7004; leakage 36679 bits.
  4. ``both_plus``: operational K1=447, K2=7004; leakage 37319 bits.
  5. ``true_l1_control``: true U1 used ONLY as an oracle-labelled L2
     conditioning/label control; discloses K2=6492, runs one L2 SC and at
     most one tag, carries provenance ``ORACLE_TRUE_L1_CONTROL`` and is
     excluded from every operational aggregate.  It is never an
     operational protocol or deployable rate.
  The increments +128 L1 / +512 L2 are fixed; the four operational arms
  cost two SC calls per block (L1 + candidate-conditioned L2) and the
  control one, for 27 SC calls and 15 tags total.  The ``base`` arm alone
  replays the accepted f<=1.3 planning budget; ``l1_plus``/``l2_plus``/
  ``both_plus`` disclose above it by the fixed increments and are
  descriptive diagnostic disclosure levels, not qualified operational
  points.
- Alice truth enters operational arms only through disclosures, tag
  construction and scoring (accepted ``run_operational_block`` truth
  boundary and sentinel); the control's extra truth use (true U1 metric
  conditioning and label reconstruction) is confined to its own arm and
  provenance label.
- Scalar outputs per (arm, block): outcome bucket, L1 correctness, tag
  result, disclosure/public bits, raw channel SER, per-layer and total NLL
  in bits under the fixed TRAIN prior, the sample
  ``arm_leakage / observed_block_NLL_bits`` cross-entropy-normalized
  disclosure ratio (explicitly NOT qualification efficiency), and
  wall/RSS/VmPeak/VmSize.  Paired recovery tables versus ``base``, a
  first-operational-recovery-arm pointer and a neutral non-monotone flag
  are reported without any threshold.
- Integrity gates: predecessor/manifest/P18 identities; population and
  exact blocks with the declared remainder; exactly 15 records; exactly 27
  SC calls and 15 tags (the fully accounted partial transcript is accepted
  only under a registered resource stop, where the resource gate is the
  blocker); K/order prefix arithmetic per arm; oracle isolation (control
  records excluded from operational aggregates; provenance enforced);
  exhaustive disjoint buckets; undetected/nonfinite/truth-leak zero;
  literal transcript recount; one open per protected input; unchanged
  input stats; no unregistered calls.  All gates true ->
  ``TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE`` for every
  recovery pattern (0/3..3/3 alike); otherwise
  ``BLOCKED(<earliest gate>)``.
- Exactly five scalar-only files under the absent root, created as stubs
  before the opens and checkpointed after every (arm, block) record; no
  private vectors, labels, metrics, keys or raw tag seed bits are
  persisted.  2 GiB virtual limit, 2 GiB RSS cap and 600 s budget;
  MemoryError is caught around the entire post-open path, checkpoints are
  preserved and the run is never rerun, repaired, retuned or cleaned up.

No Model-F/raw/real/EVAL frame, no other N, no transform/belief/list
decoder and no soft-marginal path, no added arm or grid, no
shuffle/sampling/fitting on HOLD, no remainder use, no production
benchmark, no FER/efficiency/key-rate qualification or promotion, no
commit.  Scope: a descriptive real-input layer/backoff diagnostic of the
frozen V25 1M HOLD split, not real-frame FER or reconciliation-efficiency
evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from numbers import Real
from pathlib import Path

import numpy as np

from ...io.pairs_loader import load_pairs_table, normalize_pair_columns
from ..shared import canonical_event, toeplitz_tag
from ..v35_algorithm_development import load_v25_channel_counts
from . import holdout_microcheck as hm
from . import operational_f13 as opf
from .algebra import make_gf32
from .holdout_microcheck import (
    form_holdout_blocks,
    holdout_nll_bits,
    raw_symbol_error_rate,
    verify_split_manifest,
)
from .operational_f13 import _decode_layer, run_operational_block
from .operational_f13_replication import verify_predecessor_construction
from .prior import Provenance, gather_p2_metrics, probs_to_symbol_metric
from .target_construction import TargetPopulationContractError, target_preconditions
from .transform import polar_transform
from .two_layer import (
    DISCLOSED_BITS_PER_COORDINATE,
    LABEL_SCALE,
    TAG_BITS,
    labels_to_bits,
    seed_bits_for,
)

PROTOCOL_NAME = "nbpolar-p19-holdout-backoff-diagnostic"
MODE = "holdout-backoff-diagnostic"

Q = 32
ALPHA = 2
FROZEN_N = 32768
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
FROZEN_K1 = 319  # base/operational frozen point
FROZEN_K2 = 6492
FROZEN_K_TOTAL = 6811
FROZEN_L1_INCREMENT = 128
FROZEN_L2_INCREMENT = 512
FROZEN_LEAKAGE_BITS = 34119  # 5 * 6811 + 64 (base arm)
FROZEN_PUBLIC_CONTROL_BITS = seed_bits_for(FROZEN_N)  # 327743
FROZEN_BLOCK_COUNT = 3
FROZEN_BLOCK_FRAMES = 128
FROZEN_PAIRS_PER_FRAME = 256
FROZEN_SYMBOLS_PER_BLOCK = FROZEN_BLOCK_FRAMES * FROZEN_PAIRS_PER_FRAME  # 32768
FROZEN_HOLD_FRAME_RANGE = (1600, 1999)
FROZEN_HOLD_FRAMES = 400
FROZEN_HOLD_PAIRS = 102400
FROZEN_BLOCK_RANGES = ((1600, 1727), (1728, 1855), (1856, 1983))
FROZEN_REMAINDER_FRAME_RANGE = (1984, 1999)
FROZEN_REMAINDER_FRAMES = 16
FROZEN_REMAINDER_SYMBOLS = FROZEN_REMAINDER_FRAMES * FROZEN_PAIRS_PER_FRAME  # 4096
FROZEN_TAG_MASTER = 2026092060
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = TAG_BITS  # 64

OPERATIONAL_PROVENANCE = "OPERATIONAL"
ORACLE_PROVENANCE = "ORACLE_TRUE_L1_CONTROL"

EXPECTED_NPZ_BYTES = 25166822
EXPECTED_HOLD_PARQUET_BYTES = 1354289  # provenance only (never a refusal)
FROZEN_COUNTS_PATH = (
    "/mnt/d/Code/HD-QKD_Polar_Comparison/comparison_bench/outputs_comparison/"
    "nonbinary_diagnostics/nbldpc_v25_20260818/run_04/channel_counts.npz"
)
FROZEN_HOLD_PAIRS_PATH = (
    "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
    "v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet"
)
FROZEN_MANIFEST_PATH = (
    "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
    "nbldpc_v25_20260818/run_04/split_manifest.json"
)
FROZEN_CONSTRUCTION_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/"
    "operational_f13_gate/construction_and_allocation.json"
)
FROZEN_CONSTRUCTION_DIGEST = (
    "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P19-HOLDOUT-BACKOFF-DIAGNOSTIC/"
    "holdout_backoff_diagnostic"
)
NPZ_LOADER_IDENTITY = (
    "comparison_bench.src.comparison_bench.formal_ir."
    "v35_algorithm_development.load_v25_channel_counts"
)
PAIRS_LOADER_IDENTITY = (
    "comparison_bench.src.comparison_bench.io.pairs_loader."
    "load_pairs_table+normalize_pair_columns"
)

RSS_LIMIT_BYTES = 2 * 1024**3
TOTAL_WALL_S = 600.0
EXTERNAL_TIMEOUT_S = 600
ULIMIT_VIRTUAL_KIB = 2097152

SEED_PREFIX = "nbpolar-p19-holdout-backoff-diagnostic-seed"

ATTEMPT_CONSUMPTION_POINT = "first protected content open (load_v25_channel_counts)"

OUTPUT_FILES = (
    "frozen_plan.json",
    "input_and_predecessor_identity.json",
    "per_block_arm_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)

COMPLETE_LABEL = "TARGET_EMPIRICAL_N32768_HOLD_BACKOFF_DIAGNOSTIC_COMPLETE"

OUTCOMES = opf.OUTCOMES


@dataclass(frozen=True)
class ArmSpec:
    """One frozen P19 arm (never CLI-tunable, never extensible)."""

    name: str
    kind: str  # "operational" | "oracle_control"
    k1: int
    k2: int
    leakage_bits: int
    provenance: str


FROZEN_ARMS = (
    ArmSpec("base", "operational", FROZEN_K1, FROZEN_K2, FROZEN_LEAKAGE_BITS,
            OPERATIONAL_PROVENANCE),
    ArmSpec("l1_plus", "operational", FROZEN_K1 + FROZEN_L1_INCREMENT, FROZEN_K2,
            34759, OPERATIONAL_PROVENANCE),
    ArmSpec("l2_plus", "operational", FROZEN_K1, FROZEN_K2 + FROZEN_L2_INCREMENT,
            36679, OPERATIONAL_PROVENANCE),
    ArmSpec("both_plus", "operational", FROZEN_K1 + FROZEN_L1_INCREMENT,
            FROZEN_K2 + FROZEN_L2_INCREMENT, 37319, OPERATIONAL_PROVENANCE),
    ArmSpec("true_l1_control", "oracle_control", 0, FROZEN_K2, 32524,
            ORACLE_PROVENANCE),
)
FROZEN_ARM_NAMES = tuple(spec.name for spec in FROZEN_ARMS)
OPERATIONAL_ARM_NAMES = tuple(spec.name for spec in FROZEN_ARMS if spec.kind == "operational")
BASE_ARM_NAME = FROZEN_ARMS[0].name
ORACLE_ARM_NAME = FROZEN_ARMS[-1].name

# Frozen design accounting (asserted in ``check_frozen_arm_table``).
PLANNED_SC_CALLS = sum(
    FROZEN_BLOCK_COUNT * (2 if spec.kind == "operational" else 1)
    for spec in FROZEN_ARMS
)  # 27
PLANNED_TAG_INVOCATIONS = len(FROZEN_ARMS) * FROZEN_BLOCK_COUNT  # 15
FROZEN_TOTAL_KEY_DEPENDENT_BITS = sum(
    FROZEN_BLOCK_COUNT * spec.leakage_bits for spec in FROZEN_ARMS
)  # 526200
FROZEN_TOTAL_PUBLIC_CONTROL_BITS = PLANNED_TAG_INVOCATIONS * FROZEN_PUBLIC_CONTROL_BITS

ARM_BY_NAME = {spec.name: spec for spec in FROZEN_ARMS}

SUPPORT_RULE = (
    "f = counts / column totals; every cell below 1e-15 replaced by 1e-15; "
    "columns renormalized; p_b = column totals / total count; "
    "P1/P2 = accepted derive_p1/derive_p2(f) under A=32*U1+U2; "
    "no lambda, backoff, tuning, floor scan or fitting on HOLD (exact P7 rule)"
)
BLOCK_RULE = (
    "accepted P18 form_holdout_blocks: sort HOLD rows by (frame_id, pair_idx); "
    "require exactly 400 frames 1600..1999, 256 rows per frame, pair_idx "
    "0..255 and symbols 0..1023; blocks 1600..1727 / 1728..1855 / 1856..1983 "
    "(128 frames = 32768 pairs each); frames 1984..1999 are the declared "
    "unused remainder; no shuffle, resampling, overlap, padding, pooling or "
    "fitting"
)
ARM_RULE = (
    "five frozen arms in order base(319,6492) / l1_plus(447,6492) / "
    "l2_plus(319,7004) / both_plus(447,7004) / true_l1_control(oracle, "
    "K1=0, K2=6492); increments +128 L1 / +512 L2 fixed; four operational "
    "arms run one L1 plus one candidate-conditioned L2 SC per block and the "
    "control one oracle-conditioned L2 SC; 27 SC calls and 15 tags total; "
    "the control carries ORACLE_TRUE_L1_CONTROL provenance and is excluded "
    "from operational aggregates; arms are constants, never CLI-tunable"
)
NLL_RULE = (
    "per block under the fixed floor-1e-15 TRAIN prior: "
    "l1_nll_bits = sum_i -log2 p1[high_i, bob_i]; "
    "l2_nll_bits = sum_i -log2 p2[high_i, bob_i, low_i]; "
    "total_nll_bits = l1 + l2 (bits per 32768-pair block); descriptive "
    "scoring only, never a metric input"
)
RATIO_RULE = (
    "disclosure_ce_ratio = arm_leakage_bits / total_nll_bits for every "
    "registered (arm, block) record with an observed NLL (the numerator is "
    "the registered full-block arm disclosure, so a partially invoked block "
    "keeps a nominal value; actual disclosure is the transcript recount); "
    "aggregate = arm_leakage_bits * observed_blocks / total_nll_bits; a "
    "sample cross-entropy-normalized descriptive disclosure ratio, "
    "explicitly NOT qualification reconciliation efficiency"
)
TRUTH_BOUNDARY = (
    "Alice truth enters operational arms only through disclosed values, tag "
    "construction and scoring (accepted run_operational_block boundary and "
    "sentinel); the true_l1_control's extra truth use (true U1 metric "
    "conditioning and label reconstruction) is confined to that arm and its "
    "provenance label; operational L1/L2 metrics and decisions never see "
    "truth"
)
OPERATIONAL_RULE = (
    "per operational block: disclose true U1 at verified order1[:K1], one "
    "operational L1 SC; L2 metrics from Bob plus the hard L1 candidate "
    "only; disclose true U2 at verified order2[:K2], one restarted "
    "operational L2 SC; label_hat=32*high_hat+low_hat; one 64-bit Toeplitz "
    "tag in the P19/N/arm/block seed domain (public master 2026092060); "
    "exactly one of exact/undetected/verify_failed/decode_failed/nonfinite/"
    "resource_abort; undetected never success"
)
ORACLE_RULE = (
    "the true_l1_control arm conditions the L2 metric on true U1, labels "
    "label_hat=32*true_U1+low_hat, discloses true U2 at verified "
    "order2[:K2], runs one L2 SC and at most one tag, and carries "
    "ORACLE_TRUE_L1_CONTROL provenance; it is never presented as an "
    "operational protocol or deployable rate and never enters operational "
    "aggregates"
)
NO_THRESHOLD_RULE = (
    "there is no exact-count, FER, winner, monotonicity, superiority or "
    "qualification threshold and no recovery gate of any kind; every "
    "recovery pattern (0/3..3/3) is a descriptive COMPLETE when integrity "
    "holds; only integrity/resource failures produce BLOCKED(<earliest gate>)"
)
CLAIM_SCOPE = (
    "descriptive real-input layer/backoff diagnostic of the frozen V25 1M "
    "HOLD split at N=32768 only (three accepted P18 chronological blocks, "
    "frames 1600..1983); the true-L1 arm is an oracle-labelled diagnostic "
    "control, never an operational protocol or deployable rate; not "
    "real-frame FER, reconciliation efficiency, leakage, key rate, scaling "
    "superiority, qualification or promotion evidence; the CE-normalized "
    "disclosure ratio is not qualification efficiency; undetected is never "
    "success"
)

OUTCOME_PRECEDENCE = [
    "resource_abort: arm not executed (preregistered budget stop)",
    "nonfinite: numeric nonfinite failure in L1/L2 SC; no tag",
    "decode_failed: other L1/L2 SC exception; no tag",
    "verify_failed: tag mismatch",
    "exact: tag pass and label == true label",
    "undetected: tag pass and not exact (never success)",
]

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "hold_split_manifest_identity",
    "p18_block_range_identity",
    "target_population_contract",
    "hold_population_exact",
    "blocks_exact_with_declared_remainder",
    "fifteen_records_exact",
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
    "cd /mnt/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
    "ulimit -v 2097152\n"
    "timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_backoff_diagnostic "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --floor 1e-15 "
    "--n 32768 --k1 319 --k2 6492 "
    f"--construction {FROZEN_CONSTRUCTION_PATH} --construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
    f"--hold-pairs {FROZEN_HOLD_PAIRS_PATH} "
    "--hold-frames 1600 1999 --block-frames 128 --remainder-frames 1984 1999 "
    "--tag-master 2026092060 --chunk-rows 512 --tag-bits 64 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)

# Process-level one-open guards: set at the first content open, never cleared.
_NPZ_CONTENT_OPENED = False
_HOLD_PARQUET_CONTENT_OPENED = False

__all__ = [
    "PROTOCOL_NAME", "MODE", "Q", "ALPHA", "FROZEN_N", "FROZEN_SOURCE",
    "FROZEN_FLOOR", "FROZEN_TARGET_F", "FROZEN_K1", "FROZEN_K2",
    "FROZEN_K_TOTAL", "FROZEN_L1_INCREMENT", "FROZEN_L2_INCREMENT",
    "FROZEN_LEAKAGE_BITS", "FROZEN_PUBLIC_CONTROL_BITS", "FROZEN_BLOCK_COUNT",
    "FROZEN_BLOCK_FRAMES", "FROZEN_PAIRS_PER_FRAME", "FROZEN_SYMBOLS_PER_BLOCK",
    "FROZEN_HOLD_FRAME_RANGE", "FROZEN_HOLD_FRAMES", "FROZEN_HOLD_PAIRS",
    "FROZEN_BLOCK_RANGES", "FROZEN_REMAINDER_FRAME_RANGE",
    "FROZEN_REMAINDER_FRAMES", "FROZEN_REMAINDER_SYMBOLS", "FROZEN_TAG_MASTER",
    "FROZEN_CHUNK_ROWS", "FROZEN_TAG_BITS", "OPERATIONAL_PROVENANCE",
    "ORACLE_PROVENANCE", "EXPECTED_NPZ_BYTES", "EXPECTED_HOLD_PARQUET_BYTES",
    "FROZEN_COUNTS_PATH", "FROZEN_HOLD_PAIRS_PATH", "FROZEN_MANIFEST_PATH",
    "FROZEN_CONSTRUCTION_PATH", "FROZEN_CONSTRUCTION_DIGEST", "FROZEN_OUT_ROOT",
    "NPZ_LOADER_IDENTITY", "PAIRS_LOADER_IDENTITY", "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S", "EXTERNAL_TIMEOUT_S", "ULIMIT_VIRTUAL_KIB", "SEED_PREFIX",
    "ATTEMPT_CONSUMPTION_POINT", "OUTPUT_FILES", "COMPLETE_LABEL", "OUTCOMES",
    "ArmSpec", "FROZEN_ARMS", "FROZEN_ARM_NAMES", "OPERATIONAL_ARM_NAMES",
    "BASE_ARM_NAME", "ORACLE_ARM_NAME", "ARM_BY_NAME", "PLANNED_SC_CALLS",
    "PLANNED_TAG_INVOCATIONS", "FROZEN_TOTAL_KEY_DEPENDENT_BITS",
    "FROZEN_TOTAL_PUBLIC_CONTROL_BITS", "SUPPORT_RULE", "BLOCK_RULE",
    "ARM_RULE", "NLL_RULE", "RATIO_RULE", "TRUTH_BOUNDARY", "OPERATIONAL_RULE",
    "ORACLE_RULE", "NO_THRESHOLD_RULE", "CLAIM_SCOPE", "OUTCOME_PRECEDENCE",
    "INTEGRITY_GATE_ORDER", "FROZEN_COMMAND",
    "BackoffDiagnosticContractError", "BackoffDiagnosticResourceError",
    "OracleControlResult", "BackoffDiagnosticRun", "check_frozen_arm_table",
    "verify_p18_block_identity", "backoff_seed_bits", "run_oracle_control_block",
    "oracle_isolation_ok", "recovery_diagnostics", "build_aggregates",
    "backoff_label", "backoff_block_events", "backoff_recount_events",
    "run_backoff_diagnostic", "build_parser", "main",
]


class BackoffDiagnosticContractError(ValueError):
    """Post-open population/formation failure: BLOCKED(<earliest gate>)."""


class BackoffDiagnosticResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


def _check_floor(value) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"floor must be a real number, got {value!r}")
    out = float(value)
    if not np.isfinite(out) or not 0.0 < out < 1.0:
        raise ValueError(f"floor must lie in (0, 1), got {value!r}")
    return out


def _check_base_k1(value) -> int:
    out = opf._as_int(value, "k1", minimum=0)
    if out != FROZEN_K1:
        raise ValueError(f"frozen point requires base k1={FROZEN_K1}, got {out}")
    return out


def _check_base_k2(value) -> int:
    out = opf._as_int(value, "k2", minimum=0)
    if out != FROZEN_K2:
        raise ValueError(f"frozen point requires base k2={FROZEN_K2}, got {out}")
    return out


def _check_tag_master(value) -> int:
    out = opf._as_int(value, "tag_master", minimum=0)
    if out != FROZEN_TAG_MASTER:
        raise ValueError(f"frozen point requires tag-master={FROZEN_TAG_MASTER}, got {out}")
    return out


def check_frozen_arm_table() -> dict:
    """Fail-closed pin of the five frozen arms and their design accounting.

    Pure code-level check (no I/O): arm order, K values, increments,
    leakage arithmetic, oracle label and the 27 SC / 15 tag design totals.
    Any drift raises before any root exists.
    """
    if len(FROZEN_ARMS) != 5:
        raise ValueError(f"frozen arm table must hold 5 arms, got {len(FROZEN_ARMS)}")
    if FROZEN_ARM_NAMES != ("base", "l1_plus", "l2_plus", "both_plus", "true_l1_control"):
        raise ValueError(f"frozen arm order drifted: {FROZEN_ARM_NAMES!r}")
    base = FROZEN_ARMS[0]
    if (base.kind, base.k1, base.k2, base.leakage_bits, base.provenance) != (
        "operational", FROZEN_K1, FROZEN_K2, FROZEN_LEAKAGE_BITS, OPERATIONAL_PROVENANCE
    ):
        raise ValueError("frozen base arm drifted from the accepted P16 point")
    if FROZEN_K1 + FROZEN_K2 != FROZEN_K_TOTAL:
        raise ValueError("frozen base K1+K2 != K_total")
    if FROZEN_LEAKAGE_BITS != DISCLOSED_BITS_PER_COORDINATE * FROZEN_K_TOTAL + TAG_BITS:
        raise ValueError("frozen base leakage != 5*(K1+K2)+64")
    expected_rows = (
        ("l1_plus", "operational", FROZEN_K1 + FROZEN_L1_INCREMENT, FROZEN_K2),
        ("l2_plus", "operational", FROZEN_K1, FROZEN_K2 + FROZEN_L2_INCREMENT),
        ("both_plus", "operational", FROZEN_K1 + FROZEN_L1_INCREMENT,
         FROZEN_K2 + FROZEN_L2_INCREMENT),
    )
    for expected, spec in zip(expected_rows, FROZEN_ARMS[1:4]):
        if (spec.name, spec.kind, spec.k1, spec.k2) != expected:
            raise ValueError(f"frozen arm {spec.name!r} drifted from its registered increments")
    control = FROZEN_ARMS[4]
    if (control.kind, control.k1, control.k2, control.provenance) != (
        "oracle_control", 0, FROZEN_K2, ORACLE_PROVENANCE
    ):
        raise ValueError("frozen true_l1_control arm drifted")
    for spec in FROZEN_ARMS:
        want = DISCLOSED_BITS_PER_COORDINATE * (spec.k1 + spec.k2) + TAG_BITS
        if spec.leakage_bits != want:
            raise ValueError(f"frozen arm {spec.name!r} leakage {spec.leakage_bits} != {want}")
    if PLANNED_SC_CALLS != 27:
        raise ValueError(f"frozen design must plan 27 SC calls, got {PLANNED_SC_CALLS}")
    if PLANNED_TAG_INVOCATIONS != 15:
        raise ValueError(f"frozen design must plan 15 tags, got {PLANNED_TAG_INVOCATIONS}")
    h_total = float(opf.EXPECTED_H1 + opf.EXPECTED_H2)
    f_base = float(FROZEN_LEAKAGE_BITS / (FROZEN_N * h_total))
    if f_base > FROZEN_TARGET_F:
        raise ValueError("frozen base arm exceeds the accepted planning f<=1.3 budget")
    return {
        "arm_names": list(FROZEN_ARM_NAMES),
        "planned_sc_calls": int(PLANNED_SC_CALLS),
        "planned_tag_invocations": int(PLANNED_TAG_INVOCATIONS),
        "total_key_dependent_bits": int(FROZEN_TOTAL_KEY_DEPENDENT_BITS),
        "total_public_control_bits": int(FROZEN_TOTAL_PUBLIC_CONTROL_BITS),
        "base_f": f_base,
        "base_within_planning_f": bool(f_base <= FROZEN_TARGET_F),
        "verified": True,
    }


def verify_p18_block_identity() -> dict:
    """Pin the accepted P18 N/block/remainder constants (code level, no I/O).

    The P18 module is the accepted predecessor; a drift there (or here)
    raises before any root exists and before either protected content
    open, consuming nothing.
    """
    checks = {
        "n": FROZEN_N == int(hm.FROZEN_N),
        "base_k1": FROZEN_K1 == int(hm.FROZEN_K1),
        "base_k2": FROZEN_K2 == int(hm.FROZEN_K2),
        "k_total": FROZEN_K_TOTAL == int(hm.FROZEN_K_TOTAL),
        "construction_digest": FROZEN_CONSTRUCTION_DIGEST == str(hm.FROZEN_CONSTRUCTION_DIGEST),
        "block_count": FROZEN_BLOCK_COUNT == int(hm.FROZEN_BLOCK_COUNT),
        "block_frames": FROZEN_BLOCK_FRAMES == int(hm.FROZEN_BLOCK_FRAMES),
        "block_ranges": tuple(tuple(r) for r in FROZEN_BLOCK_RANGES)
        == tuple(tuple(r) for r in hm.FROZEN_BLOCK_RANGES),
        "symbols_per_block": FROZEN_SYMBOLS_PER_BLOCK == int(hm.FROZEN_SYMBOLS_PER_BLOCK),
        "hold_frame_range": tuple(FROZEN_HOLD_FRAME_RANGE) == tuple(hm.FROZEN_HOLD_FRAME_RANGE),
        "hold_frames": FROZEN_HOLD_FRAMES == int(hm.FROZEN_HOLD_FRAMES),
        "hold_pairs": FROZEN_HOLD_PAIRS == int(hm.FROZEN_HOLD_PAIRS),
        "remainder_frame_range": tuple(FROZEN_REMAINDER_FRAME_RANGE)
        == tuple(hm.FROZEN_REMAINDER_FRAME_RANGE),
        "remainder_frames": FROZEN_REMAINDER_FRAMES == int(hm.FROZEN_REMAINDER_FRAMES),
        "remainder_symbols": FROZEN_REMAINDER_SYMBOLS == int(hm.FROZEN_REMAINDER_SYMBOLS),
    }
    failing = sorted(name for name, ok in checks.items() if not ok)
    if failing:
        raise ValueError("accepted P18 block-range identity mismatch: " + ",".join(failing))
    return {
        "p18_module": ("comparison_bench.src.comparison_bench.formal_ir.nbpolar."
                       "holdout_microcheck"),
        "checks": {name: bool(ok) for name, ok in checks.items()},
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "remainder_frame_range": list(FROZEN_REMAINDER_FRAME_RANGE),
        "hold_frame_range": list(FROZEN_HOLD_FRAME_RANGE),
        "verified": True,
    }


def backoff_seed_bits(
    master: int,
    n: int,
    arm: str,
    block_index: int,
    *,
    bit_length: int | None = None,
) -> np.ndarray:
    """Deterministic public per-(arm, block) Toeplitz seed (P19 domain).

    Rule: concatenate SHA-256 over
    ``"nbpolar-p19-holdout-backoff-diagnostic-seed:<master>:<n>:<arm>:
    <block_index>:<counter>"`` for ``counter = 0, 1, ...`` (ASCII decimal),
    unpack each digest MSB-first and truncate to ``bit_length`` (default
    ``10*n + 63``).  The P19 prefix and the arm token differ from the P16,
    P17 and P18 domains on purpose: scored tags here never share a prior
    seed domain.  Seed contents are public control and are never persisted;
    only the bit length is recorded.
    """
    master_seed = opf._as_int(master, "master", minimum=0)
    n = opf._as_int(n, "n", minimum=1)
    if arm not in FROZEN_ARM_NAMES:
        raise ValueError(f"unknown frozen arm for the P19 seed domain: {arm!r}")
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


@dataclass(frozen=True, eq=False)
class OracleControlResult:
    """One oracle-labelled true-L1 control attempt (in-memory only)."""

    frame_start: int
    block_index: int
    outcome: str
    exact: bool
    label_match: bool
    tag_pass: bool
    l2_invoked: bool
    l2_decode_failed: bool
    tag_invoked: bool
    key_dependent_bits: int
    public_control_bits: int
    nonfinite: bool
    truth_leak_violation: bool
    l2_error_type: str | None
    wall_s: float
    k2: int
    provenance: str
    oracle_truth_use: bool
    low_hat: np.ndarray | None = None


def run_oracle_control_block(
    *,
    n: int,
    block_index: int,
    frame_start: int,
    bob,
    high_true,
    low_true,
    u1_true,
    u2_true,
    labels_true,
    labels_true_bits,
    field,
    p2_table,
    l2_order,
    k2: int,
    master: int,
    tag_fn=None,
    calls=None,
) -> OracleControlResult:
    """One oracle-labelled L2-only control block (never an operational path).

    True U1 conditions the L2 metric (``ORACLE_CONDITIONED`` provenance) and
    reconstructs the label; the metric takes no other Alice input.  Exactly
    one L2 SC call and at most one tag; no L1 SC and no L1 disclosure.  The
    arm is provenance-isolated (``ORACLE_TRUE_L1_CONTROL``) and excluded
    from every operational aggregate.
    """
    n = opf._as_int(n, "n", minimum=1)
    if n & (n - 1):
        raise ValueError(f"n must be a power of two, got {n}")
    block_index = opf._as_int(block_index, "block_index", minimum=0)
    k2 = opf._as_int(k2, "k2", minimum=0)
    if k2 > n:
        raise ValueError(f"k2 must lie in 0..{n}, got {k2}")
    master = opf._as_int(master, "master", minimum=0)
    tag_fn = opf._check_tag_fn(tag_fn)
    # Internal truth copies: every computation below uses these copies only,
    # so the truth sentinel can mutate them and prove no aliasing.
    bob_arr = np.array(bob, dtype=np.int64, copy=True)
    high_arr = np.array(high_true, dtype=np.int64, copy=True)
    low_arr = np.array(low_true, dtype=np.int64, copy=True)
    u1_arr = np.array(u1_true, dtype=np.int64, copy=True)
    u2_arr = np.array(u2_true, dtype=np.int64, copy=True)
    labels_arr = np.array(labels_true, dtype=np.int64, copy=True)
    label_bits_arr = np.array(labels_true_bits, dtype=np.uint8, copy=True)
    l2_positions = np.asarray(l2_order, dtype=np.int64)[:k2]

    arm_start = time.perf_counter()
    # The [U1,B,U2] table's U1 index is the true high-layer symbol (the same
    # index space the accepted operational path conditions on with its hard
    # L1 candidate); the transform-domain ``u1_true`` vector is retained only
    # as a truth-isolation guard input.
    p2_probs = gather_p2_metrics(bob_arr[None, :], high_arr[None, :], p2_table)[0]
    metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.ORACLE_CONDITIONED)
    u2_disclosed = np.array(u2_arr[l2_positions], copy=True)
    l2_error = None
    nonfinite = False
    low_hat = None
    label_hat = None
    label_hat_bits = None
    tag_pass = False
    tag_invoked = False
    label_match = False
    try:
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + 1
        sc2 = _decode_layer(
            metric.logp, field=field, positions=l2_positions, disclosed=u2_disclosed
        )
        low_hat = np.array(sc2.x_hat, copy=True)
        label_hat = (low_hat + LABEL_SCALE * high_arr).astype(np.int64)
        label_hat_bits = labels_to_bits(label_hat)
        label_match = bool(np.array_equal(label_hat, labels_arr))
        seed = backoff_seed_bits(master, n, ORACLE_ARM_NAME, block_index,
                                 bit_length=seed_bits_for(n))
        tag_true = tag_fn(label_bits_arr, seed, TAG_BITS)
        tag_hat = tag_fn(label_hat_bits, seed, TAG_BITS)
        tag_pass = tag_hat == tag_true
        tag_invoked = True
    except Exception as exc:  # SC failure contract: decode_failed/nonfinite, no tag
        l2_error = type(exc).__name__
        nonfinite = opf._nonfinite_flag(exc)
    outcome = opf.classify_operational_outcome(
        l1_failed=False,
        l2_failed=l2_error is not None,
        nonfinite=nonfinite,
        tag_pass=tag_pass,
        label_match=label_match,
    )
    protected = [metric.logp, u2_disclosed]
    for item in (low_hat, label_hat, label_hat_bits):
        if item is not None:
            protected.append(item)
    isolated = opf._truth_isolation_sentinel(
        protected,
        [(high_arr, Q), (low_arr, Q), (u1_arr, Q), (u2_arr, Q), (labels_arr, 1 << 10)],
    )
    return OracleControlResult(
        frame_start=int(frame_start),
        block_index=int(block_index),
        outcome=outcome,
        exact=bool(outcome == "exact"),
        label_match=bool(label_match),
        tag_pass=bool(tag_pass),
        l2_invoked=True,
        l2_decode_failed=bool(l2_error is not None),
        tag_invoked=bool(tag_invoked),
        key_dependent_bits=int(
            DISCLOSED_BITS_PER_COORDINATE * k2 + (TAG_BITS if tag_invoked else 0)
        ),
        public_control_bits=int(seed_bits_for(n) if tag_invoked else 0),
        nonfinite=bool(nonfinite),
        truth_leak_violation=bool(not isolated),
        l2_error_type=l2_error,
        wall_s=time.perf_counter() - arm_start,
        k2=int(k2),
        provenance=ORACLE_PROVENANCE,
        oracle_truth_use=True,
        low_hat=low_hat,
    )


def _block_scoring(block, p1_table, p2_table) -> dict:
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


def _p19_record_fields(*, spec, arm_index, block, scoring, oracle) -> dict:
    total_nll = scoring.get("total_nll_bits")
    return {
        "protocol": PROTOCOL_NAME,
        "arm": spec.name,
        "arm_index": int(arm_index),
        "arm_kind": spec.kind,
        "arm_provenance": spec.provenance,
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
        "raw_ser": scoring.get("raw_ser"),
        "l1_nll_bits": scoring.get("l1_nll_bits"),
        "l2_nll_bits": scoring.get("l2_nll_bits"),
        "total_nll_bits": scoring.get("total_nll_bits"),
        "total_nll_bits_per_pair": scoring.get("total_nll_bits_per_pair"),
    }


def _operational_record(result, *, spec, arm_index, block, scoring, resources, error=None) -> dict:
    """P19 scalar record for one operational arm/block (accepted record core)."""
    record = opf._block_record(result, resources=resources, error=error)
    record.pop("stream_seed", None)
    record["l1_correct"] = bool(
        result.l1_executed
        and result.high_hat is not None
        and np.array_equal(result.high_hat, block["high"])
    )
    record.update(_p19_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=False
    ))
    return record


def _control_record(result, *, spec, arm_index, block, scoring, resources, error=None) -> dict:
    """P19 scalar record for the oracle-labelled control arm/block."""
    record = {
        "block_index": int(result.block_index),
        "outcome": result.outcome,
        "exact": bool(result.exact),
        "label_match": bool(result.label_match),
        "tag_pass": bool(result.tag_pass),
        "l1_provenance": None,
        "l2_provenance": Provenance.ORACLE_CONDITIONED.value,
        "l1_executed": False,
        "l1_decode_failed": False,
        "l2_invoked": bool(result.l2_invoked),
        "l2_skipped_by_l1_failure": False,
        "l2_decode_failed": bool(result.l2_decode_failed),
        "tag_invoked": bool(result.tag_invoked),
        "key_dependent_bits": int(result.key_dependent_bits),
        "public_control_bits": int(result.public_control_bits),
        "nonfinite": bool(result.nonfinite),
        "truth_leak_violation": bool(result.truth_leak_violation),
        "l1_error_type": None,
        "l2_error_type": result.l2_error_type,
        "error": error,
        "k1": int(spec.k1),
        "k2": int(spec.k2),
        "l1_correct": None,
        "wall_s": round(float(result.wall_s), 6),
        "resources": dict(resources),
    }
    record.update(_p19_record_fields(
        spec=spec, arm_index=arm_index, block=block, scoring=scoring, oracle=True
    ))
    record["provenance"] = result.provenance
    return record


def _abort_record(*, spec, arm_index, block, resources) -> dict:
    """P19 scalar record for one abort-filled (arm, block) slot."""
    record = {
        "block_index": int(block["block_index"]),
        "outcome": "resource_abort",
        "exact": False,
        "label_match": False,
        "tag_pass": False,
        "l1_provenance": None,
        "l2_provenance": None,
        "l1_executed": False,
        "l1_decode_failed": False,
        "l2_invoked": False,
        "l2_skipped_by_l1_failure": False,
        "l2_decode_failed": False,
        "tag_invoked": False,
        "key_dependent_bits": 0,
        "public_control_bits": 0,
        "nonfinite": False,
        "truth_leak_violation": False,
        "l1_error_type": None,
        "l2_error_type": None,
        "error": None,
        "k1": int(spec.k1),
        "k2": int(spec.k2),
        "l1_correct": False if spec.kind == "operational" else None,
        "wall_s": 0.0,
        "resources": dict(resources),
    }
    record.update(_p19_record_fields(
        spec=spec, arm_index=arm_index, block=block,
        scoring=_scoring_absent(), oracle=(spec.kind == "oracle_control"),
    ))
    if spec.kind == "oracle_control":
        record["provenance"] = ORACLE_PROVENANCE
    return record


def _operational_record_consistent(record, spec, n) -> bool:
    if not opf._record_dict_consistent(record, n=n, k1=spec.k1, k2=spec.k2):
        return False
    if record.get("arm") != spec.name or record.get("arm_kind") != "operational":
        return False
    if record.get("arm_provenance") != OPERATIONAL_PROVENANCE:
        return False
    if record.get("oracle_truth_use") is not False or record.get("oracle_control") is not False:
        return False
    if int(record.get("l1_prefix_len", -1)) != int(spec.k1):
        return False
    if int(record.get("l2_prefix_len", -1)) != int(spec.k2):
        return False
    return True


def _control_record_consistent(record, spec, n) -> bool:
    if record.get("outcome") not in OUTCOMES:
        return False
    if record.get("error") is not None:
        return False
    if int(record.get("k1", -1)) != 0 or int(record.get("k2", -1)) != int(spec.k2):
        return False
    if record.get("arm") != spec.name or record.get("arm_kind") != "oracle_control":
        return False
    if record.get("arm_provenance") != ORACLE_PROVENANCE:
        return False
    if record.get("provenance") != ORACLE_PROVENANCE:
        return False
    if record.get("oracle_truth_use") is not True or record.get("oracle_control") is not True:
        return False
    if record.get("l1_provenance") is not None or record.get("l1_executed") is not False:
        return False
    if record.get("l1_decode_failed") is not False or record.get("l2_skipped_by_l1_failure") is not False:
        return False
    if record["outcome"] == "resource_abort":
        return bool(
            int(record["key_dependent_bits"]) == 0
            and int(record["public_control_bits"]) == 0
            and not any((
                record["exact"], record["label_match"], record["tag_pass"],
                record["l2_invoked"], record["l2_decode_failed"],
                record["tag_invoked"], record["nonfinite"],
                record["truth_leak_violation"],
            ))
            and record["l2_provenance"] is None
        )
    if not record.get("l2_invoked"):
        return False
    if record.get("l2_provenance") != Provenance.ORACLE_CONDITIONED.value:
        return False
    tag_outcomes = ("exact", "undetected", "verify_failed")
    if bool(record.get("tag_invoked")) != (record["outcome"] in tag_outcomes):
        return False
    if record["outcome"] == "nonfinite" and not (
        record["l2_decode_failed"] and record["nonfinite"]
    ):
        return False
    if record["outcome"] == "decode_failed" and not (
        record["l2_decode_failed"] and not record["nonfinite"]
    ):
        return False
    if record["outcome"] not in ("decode_failed", "nonfinite") and record["l2_decode_failed"]:
        return False
    if record["outcome"] == "exact" and not (record["tag_pass"] and record["label_match"]):
        return False
    if record["outcome"] == "undetected" and not (record["tag_pass"] and not record["label_match"]):
        return False
    if record["outcome"] == "verify_failed" and record["tag_pass"]:
        return False
    if bool(record["exact"]) != (record["outcome"] == "exact"):
        return False
    expected_kdb = (
        DISCLOSED_BITS_PER_COORDINATE * int(spec.k2)
        + (TAG_BITS if record.get("tag_invoked") else 0)
    )
    if int(record["key_dependent_bits"]) != expected_kdb:
        return False
    if int(record["public_control_bits"]) != (seed_bits_for(n) if record.get("tag_invoked") else 0):
        return False
    return True


def record_dict_consistent(record, *, n) -> bool:
    """P19 structural proof of one persisted (arm, block) record."""
    spec = ARM_BY_NAME.get(str(record.get("arm")))
    if spec is None:
        return False
    if int(record.get("arm_index", -1)) != FROZEN_ARM_NAMES.index(spec.name):
        return False
    if spec.kind == "operational":
        return _operational_record_consistent(record, spec, n)
    return _control_record_consistent(record, spec, n)


def _partition(records):
    """Split records into the operational and oracle-control partitions."""
    operational = [
        r for r in records
        if r.get("arm_kind") == "operational" and r.get("arm_provenance") == OPERATIONAL_PROVENANCE
    ]
    control = [
        r for r in records
        if r.get("arm_kind") == "oracle_control" and r.get("arm_provenance") == ORACLE_PROVENANCE
    ]
    return operational, control


def oracle_isolation_ok(records, *, final: bool) -> bool:
    """Control truth never enters operational partitions or aggregates."""
    operational, control = _partition(records)
    if len(operational) + len(control) != len(records):
        return False
    for record in operational:
        if record.get("arm_provenance") == ORACLE_PROVENANCE:
            return False
        if record.get("oracle_truth_use") is not False:
            return False
        if record.get("l2_provenance") == Provenance.ORACLE_CONDITIONED.value:
            return False
    for record in control:
        if record.get("arm_provenance") != ORACLE_PROVENANCE:
            return False
        if record.get("oracle_truth_use") is not True:
            return False
    if final:
        if len(operational) != len(OPERATIONAL_ARM_NAMES) * FROZEN_BLOCK_COUNT:
            return False
        if len(control) != FROZEN_BLOCK_COUNT:
            return False
    return True


def recovery_diagnostics(records) -> dict:
    """Descriptive paired recovery tables versus the base arm (no threshold)."""
    operational, _ = _partition(records)
    by_arm = {name: [] for name in OPERATIONAL_ARM_NAMES}
    for record in operational:
        if record.get("arm") in by_arm:
            by_arm[record["arm"]].append(record)
    exact_counts = [
        sum(1 for record in by_arm[name] if record.get("outcome") == "exact")
        for name in OPERATIONAL_ARM_NAMES
    ]
    non_monotone = any(
        exact_counts[i + 1] < exact_counts[i] for i in range(len(exact_counts) - 1)
    )
    first_recovery = next(
        (name for name, count in zip(OPERATIONAL_ARM_NAMES, exact_counts) if count > 0),
        None,
    )
    base_outcomes = {
        int(record["block_index"]): record.get("outcome")
        for record in by_arm[BASE_ARM_NAME]
    }
    paired = {}
    for name in OPERATIONAL_ARM_NAMES[1:]:
        pair_counts = {}
        recovered = lost = same = 0
        for record in by_arm[name]:
            base_outcome = base_outcomes.get(int(record["block_index"]))
            key = f"{base_outcome}->{record.get('outcome')}"
            pair_counts[key] = pair_counts.get(key, 0) + 1
            if base_outcome != "exact" and record.get("outcome") == "exact":
                recovered += 1
            elif base_outcome == "exact" and record.get("outcome") != "exact":
                lost += 1
            else:
                same += 1
        paired[name] = {
            "pair_counts": dict(sorted(pair_counts.items())),
            "recovered_vs_base": int(recovered),
            "lost_vs_base": int(lost),
            "same_outcome": int(same),
        }
    return {
        "base_arm": BASE_ARM_NAME,
        "ordered_operational_arms": list(OPERATIONAL_ARM_NAMES),
        "exact_counts_ordered": [int(c) for c in exact_counts],
        "exact_definition": ("outcome == exact (tag pass and label match); "
                             "undetected is never success"),
        "first_operational_recovery_arm": first_recovery,
        "ordered_exact_counts_non_monotone": bool(non_monotone),
        "non_monotone_note": ("reported neutrally: no monotonicity, superiority, "
                              "winner or threshold claim is made; exact counts are "
                              "descriptive"),
        "paired_vs_base": paired,
        "no_threshold_note": ("descriptive only; there is no recovery, winner or "
                              "qualification threshold"),
    }


def _arm_aggregate(records, spec) -> dict:
    outcome_counts = {name: 0 for name in OUTCOMES}
    for record in records:
        if record.get("outcome") in outcome_counts:
            outcome_counts[record["outcome"]] += 1
    key_bits = sum(int(r.get("key_dependent_bits", 0)) for r in records)
    public_bits = sum(int(r.get("public_control_bits", 0)) for r in records)
    total_nll = sum(
        float(r["total_nll_bits"]) for r in records if r.get("total_nll_bits") is not None
    )
    observed = sum(1 for r in records if r.get("total_nll_bits") is not None)
    return {
        "arm": spec.name,
        "kind": spec.kind,
        "k1": int(spec.k1),
        "k2": int(spec.k2),
        "leakage_bits_full_block": int(spec.leakage_bits),
        "provenance": spec.provenance,
        "blocks": int(len(records)),
        "outcome_counts": {name: int(outcome_counts[name]) for name in OUTCOMES},
        "exact_count": int(outcome_counts["exact"]),
        "key_dependent_bits": int(key_bits),
        "public_control_bits": int(public_bits),
        "total_nll_bits": float(total_nll),
        "ce_normalized_disclosure_ratio": (
            float(spec.leakage_bits * observed / total_nll) if total_nll > 0 else None
        ),
        "ratio_note": ("sample cross-entropy-normalized descriptive disclosure ratio, "
                       "explicitly NOT qualification reconciliation efficiency"),
    }


def build_aggregates(records) -> dict:
    """Operational and oracle-control aggregates with a strict partition."""
    operational, control = _partition(records)
    operational_arms = {
        spec.name: _arm_aggregate([r for r in operational if r.get("arm") == spec.name], spec)
        for spec in FROZEN_ARMS if spec.kind == "operational"
    }
    control_spec = FROZEN_ARMS[-1]
    control_arms = {
        control_spec.name: _arm_aggregate(
            [r for r in control if r.get("arm") == control_spec.name], control_spec)
    }
    merged_outcomes = {name: 0 for name in OUTCOMES}
    for spec in FROZEN_ARMS:
        if spec.kind != "operational":
            continue
        for name in OUTCOMES:
            merged_outcomes[name] += operational_arms[spec.name]["outcome_counts"][name]
    return {
        "operational": {
            "arms": operational_arms,
            "record_count": int(len(operational)),
            "outcome_counts": merged_outcomes,
            "exact_count": int(sum(a["exact_count"] for a in operational_arms.values())),
            "key_dependent_bits": int(sum(
                a["key_dependent_bits"] for a in operational_arms.values())),
            "public_control_bits": int(sum(
                a["public_control_bits"] for a in operational_arms.values())),
            "total_nll_bits": float(sum(a["total_nll_bits"] for a in operational_arms.values())),
            "oracle_control_excluded": True,
        },
        "oracle_control": {
            "arms": control_arms,
            "record_count": int(len(control)),
            "provenance": ORACLE_PROVENANCE,
            "deployable": False,
            "excluded_from_operational_aggregates": True,
            "notice": ("oracle-labelled true-L1 diagnostic control: never an "
                       "operational protocol or deployable rate"),
        },
        "partition": {
            "operational": int(len(operational)),
            "oracle_control": int(len(control)),
            "unassigned": int(len(records) - len(operational) - len(control)),
            "total": int(len(records)),
        },
        "recovery": recovery_diagnostics(records),
    }


def backoff_label(gates: dict) -> str:
    """Frozen label selection: COMPLETE iff all integrity gates pass.

    No recovery input exists in this runner; every recovery pattern
    (0/3..3/3 exact) yields the same COMPLETE label.
    """
    failing = [name for name in INTEGRITY_GATE_ORDER if not gates.get(name, False)]
    if failing:
        return f"BLOCKED({failing[0]})"
    return COMPLETE_LABEL


def _backoff_event(
    *, n, arm, block_index, frame_start, event_id, event_type, direction,
    parent_event_id, key_dependent_bits, public_control_bits, payload,
) -> dict:
    event = {
        "event_id": event_id,
        "frame_key": (
            f"nbpolar-p19-holdout-backoff-diagnostic:{int(n)}:{int(frame_start)}:{int(block_index)}"
        ),
        "method": "nbpolar_holdout_backoff_diagnostic",
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


def backoff_block_events(n: int, spec, block_index: int, frame_start: int, record) -> list:
    """Canonical public transcript events derived from one persisted record."""
    if record.get("outcome") == "resource_abort":
        return []
    events: list[dict] = []
    l1_id = None
    if record.get("l1_executed"):
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


def backoff_recount_events(events) -> dict:
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
class BackoffDiagnosticRun:
    """In-memory P19 diagnostic run (also returned by the runner)."""

    records: list
    events: list
    identity: dict
    manifest: dict
    p18_pin: dict
    plan: dict
    summary: dict


def _arm_plan_rows(h_total: float) -> list:
    rows = []
    for index, spec in enumerate(FROZEN_ARMS):
        leakage = int(spec.leakage_bits)
        rows.append({
            "arm_index": int(index),
            "arm": spec.name,
            "kind": spec.kind,
            "k1": int(spec.k1),
            "k2": int(spec.k2),
            "l1_prefix": f"order1[:{int(spec.k1)}]",
            "l2_prefix": f"order2[:{int(spec.k2)}]",
            "leakage_bits_full_block": leakage,
            "leakage_over_nh": float(leakage / (FROZEN_N * h_total)),
            "within_planning_f": bool(leakage <= FROZEN_TARGET_F * FROZEN_N * h_total),
            "sc_calls_per_block": (2 if spec.kind == "operational" else 1),
            "tags_per_block": 1,
            "provenance": spec.provenance,
        })
    return rows


def _stub_plan(*, out_path, source, floor, n, k1, k2, construction, digest,
               hold_pairs, manifest_path, hold_frames, block_frames,
               remainder_frames, tag_master, chunk_rows, tag_bits, identity,
               manifest, p18_pin) -> dict:
    h_total = float(opf.EXPECTED_H1 + opf.EXPECTED_H2)
    return {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "out_root": str(out_path),
        "source": source,
        "counts_path": FROZEN_COUNTS_PATH,
        "expected_npz_bytes": EXPECTED_NPZ_BYTES,
        "npz_loader": NPZ_LOADER_IDENTITY,
        "hold_pairs_path": str(hold_pairs),
        "expected_hold_parquet_bytes": EXPECTED_HOLD_PARQUET_BYTES,
        "pairs_loader": PAIRS_LOADER_IDENTITY,
        "manifest_path": str(manifest_path),
        "manifest_identity": dict(manifest),
        "p18_block_range_identity": dict(p18_pin),
        "support_rule": SUPPORT_RULE,
        "block_rule": BLOCK_RULE,
        "arm_rule": ARM_RULE,
        "nll_rule": NLL_RULE,
        "ratio_rule": RATIO_RULE,
        "truth_boundary": TRUTH_BOUNDARY,
        "operational_rule": OPERATIONAL_RULE,
        "oracle_rule": ORACLE_RULE,
        "no_threshold_rule": NO_THRESHOLD_RULE,
        "outcome_precedence": list(OUTCOME_PRECEDENCE),
        "q": Q,
        "field": {
            "name": "GF32 polynomial basis",
            "primitive_polynomial": 37,
            "alpha": ALPHA,
            "index_order": "natural",
        },
        "n": int(n),
        "floor": float(floor),
        "target_f": float(FROZEN_TARGET_F),
        "base_k1": int(k1),
        "base_k2": int(k2),
        "base_k_total": int(k1) + int(k2),
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "tag_master": int(tag_master),
        "tag_seed_domain": f"{SEED_PREFIX}:<master>:<n>:<arm>:<block_index>",
        "public_control_bits_per_tag": FROZEN_PUBLIC_CONTROL_BITS,
        "hold_frame_range": [int(v) for v in hold_frames],
        "hold_frames": FROZEN_HOLD_FRAMES,
        "hold_pairs": FROZEN_HOLD_PAIRS,
        "block_frames": int(block_frames),
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "block_count": FROZEN_BLOCK_COUNT,
        "remainder_frame_range": [int(v) for v in remainder_frames],
        "remainder_symbols": FROZEN_REMAINDER_SYMBOLS,
        "arms": _arm_plan_rows(h_total),
        "planned_sc_calls": int(PLANNED_SC_CALLS),
        "planned_tag_invocations": int(PLANNED_TAG_INVOCATIONS),
        "planned_records": int(len(FROZEN_ARMS) * FROZEN_BLOCK_COUNT),
        "full_block_key_dependent_bits": {
            spec.name: int(spec.leakage_bits) for spec in FROZEN_ARMS
        },
        "total_key_dependent_bits_if_all_invoked": int(FROZEN_TOTAL_KEY_DEPENDENT_BITS),
        "total_public_control_bits_if_all_tags": int(FROZEN_TOTAL_PUBLIC_CONTROL_BITS),
        "backoff_note": (
            "base replays the accepted P16 operational point (leakage 34119 <= "
            "1.3*N*H); l1_plus/l2_plus/both_plus disclose above the accepted "
            "planning budget by the fixed increments (+128 L1 / +512 L2 "
            "coordinates) and are descriptive diagnostic disclosure levels, not "
            "qualified operational points; true_l1_control is an oracle-labelled "
            "diagnostic control, never an operational protocol or deployable rate"
        ),
        "predecessor": {
            "construction_path": str(construction),
            "construction_digest": str(digest),
            "identity": dict(identity),
        },
        "entropy_expectations": {
            "h1": opf.EXPECTED_H1,
            "h2": opf.EXPECTED_H2,
            "total": opf.EXPECTED_TOTAL,
            "entropy_tol": opf.ENTROPY_TOL,
            "column_tol": opf.COLUMN_TOL,
            "floor_entropy_change_tol": opf.FLOOR_ENTROPY_TOL,
        },
        "f_inequality_base_only": {
            "leakage_bits": FROZEN_LEAKAGE_BITS,
            "limit_bits": float(FROZEN_TARGET_F * int(n) * h_total),
        },
        "precondition_order": list(opf.PRECONDITION_ORDER),
        "integrity_gate_order": list(INTEGRITY_GATE_ORDER),
        "decision": {
            "complete": COMPLETE_LABEL,
            "blocked": "BLOCKED(<earliest gate>)",
            "recovery_threshold": None,
            "zero_recovery_is_complete": True,
            "three_recovery_is_complete": True,
        },
        "attempt_consumption_point": ATTEMPT_CONSUMPTION_POINT,
        "budget": {
            "total_wall_s": float(TOTAL_WALL_S),
            "external_timeout_s": EXTERNAL_TIMEOUT_S,
            "ulimit_virtual_kib": ULIMIT_VIRTUAL_KIB,
            "rss_bytes_max": RSS_LIMIT_BYTES,
            "env": {
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
                "MALLOC_ARENA_MAX": "2",
            },
        },
        "output_files": list(OUTPUT_FILES),
        "frozen_command": FROZEN_COMMAND,
        "claim_scope": CLAIM_SCOPE,
    }


def _render_report(summary: dict) -> str:
    lines = [
        "# NB-Polar Phase 4-P19 N=32768 1M-HOLD layer/backoff diagnostic",
        "",
        f"- protocol: `{summary.get('analysis')}` (mode `{summary.get('mode')}`)",
        f"- source/target: `{summary.get('source')}`; q={summary.get('q')}, "
        f"n={summary.get('n')}, base K1={summary.get('k1')}, base K2={summary.get('k2')}, "
        f"chunk_rows={summary.get('chunk_rows')}, tag_bits={summary.get('tag_bits')}",
        f"- HOLD frames: {summary.get('hold', {}).get('hold_frame_range')}; "
        f"blocks: {summary.get('hold', {}).get('block_ranges')}; "
        f"unused remainder: {summary.get('hold', {}).get('remainder')}",
        f"- records: {summary.get('records_completed')}/{summary.get('records_expected')}; "
        f"SC calls: {summary.get('sc_calls')}/{summary.get('planned_sc_calls')}; "
        f"tags: {summary.get('tag_invocations')}/{summary.get('planned_tag_invocations')}",
        f"- wall: {summary.get('wall_s')} s; peak RSS: {summary.get('rss_bytes_peak')} bytes; "
        f"resource stop fired: {summary.get('resource_stop_fired')}",
        "",
        "## Frozen arms (K, leakage, per-block SC calls; no threshold)",
        "",
        "| arm | kind | K1 | K2 | leakage bits | SC/block | provenance | exact (of 3) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    operational = summary.get("operational", {})
    control = summary.get("oracle_control", {})
    for spec in FROZEN_ARMS:
        cell = operational.get("arms", {}).get(spec.name) or control.get("arms", {}).get(spec.name, {})
        lines.append(
            f"| {spec.name} | {spec.kind} | {spec.k1} | {spec.k2} | "
            f"{spec.leakage_bits} | {2 if spec.kind == 'operational' else 1} | "
            f"{spec.provenance} | {cell.get('exact_count')} |"
        )
    recovery = summary.get("recovery", {})
    lines += [
        "",
        "## Descriptive recovery diagnostics (no threshold, no winner)",
        "",
        f"- ordered operational exact counts: {recovery.get('exact_counts_ordered')}",
        f"- first operational recovery arm: {recovery.get('first_operational_recovery_arm')}",
        f"- ordered exact counts non-monotone: "
        f"{recovery.get('ordered_exact_counts_non_monotone')} "
        f"({recovery.get('non_monotone_note')})",
        "",
        "| arm | paired vs base | recovered vs base | lost vs base |",
        "|---|---|---|---|",
    ]
    for name, cell in recovery.get("paired_vs_base", {}).items():
        lines.append(
            f"| {name} | {cell.get('pair_counts')} | {cell.get('recovered_vs_base')} | "
            f"{cell.get('lost_vs_base')} |"
        )
    lines += [
        "",
        "## Oracle control (provenance-isolated; never an operational protocol)",
        "",
        f"- {control.get('notice')}",
        f"- control records: {control.get('record_count')} (excluded from every "
        "operational aggregate); deployable: False",
        "",
        "## Disclosure and verification accounting",
        "",
        f"- operational key-dependent bits: "
        f"{operational.get('key_dependent_bits')}; control key-dependent bits (isolated): "
        f"{control.get('arms', {}).get('true_l1_control', {}).get('key_dependent_bits')}",
        f"- public control bits: {summary.get('disclosure', {}).get('public_control_bits')} "
        f"(fixed per-tag value {FROZEN_PUBLIC_CONTROL_BITS})",
        f"- transcript recount: {summary.get('disclosure', {}).get('recount')}",
        f"- transcript recount mismatches: {summary.get('disclosure', {}).get('mismatches')}",
        f"- CE-normalized disclosure ratio note: "
        f"{summary.get('disclosure', {}).get('ratio_note')}",
        "",
        "## Integrity gates",
        "",
        "| gate | result |",
        "|---|---|",
    ]
    for name, value in summary.get("integrity", {}).items():
        lines.append(f"| {name} | {value} |")
    lines += [
        "",
        f"- outcome label: `{summary.get('outcome_label')}`",
        f"- recovery threshold: {summary.get('decision', {}).get('recovery_threshold')} "
        "(none; every 0/3..3/3 recovery pattern is a descriptive COMPLETE)",
        "",
        f"**Scope:** {summary.get('claim_scope')}.",
        "",
    ]
    return "\n".join(lines)


def _integrity_gates(
    *, out_path, n, p18_pin, identity, manifest, l1_order, l2_order, formation,
    records, events, calls, incremental, accounting, provenance_violations,
    start, cap, resource_stop, precondition_passed, final,
    npz_stat_before, npz_stat_after, hold_stat_before, hold_stat_after,
    registered_paths, opened_paths, k1, k2,
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
        and manifest.get("schema") == hm.FROZEN_MANIFEST_SCHEMA
        and int(manifest.get("hold_frames", -1)) == FROZEN_HOLD_FRAMES
        and int(manifest.get("hold_pairs", -1)) == FROZEN_HOLD_PAIRS
    )
    try:
        p18_now = verify_p18_block_identity()
    except ValueError:
        p18_now = None
    p18_ok = bool(
        isinstance(p18_pin, dict)
        and p18_pin.get("verified") is True
        and isinstance(p18_now, dict)
        and p18_now.get("verified") is True
    )

    population_ok = bool(
        int(formation["hold_frames"]) == FROZEN_HOLD_FRAMES
        and int(formation["hold_pairs"]) == FROZEN_HOLD_PAIRS
        and list(formation["hold_frame_range"]) == list(FROZEN_HOLD_FRAME_RANGE)
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
        and list(formation["hold_frame_range"]) == list(FROZEN_HOLD_FRAME_RANGE)
    )
    expected_ranges = [tuple(r) for r in FROZEN_BLOCK_RANGES]
    observed_ranges = [(int(r["frame_start"]), int(r["frame_end"])) for r in records]
    per_arm_counts = {
        spec.name: sum(1 for r in records if r.get("arm") == spec.name)
        for spec in FROZEN_ARMS
    }
    if final:
        blocks_ok = bool(
            blocks_ok
            and len(records) == len(FROZEN_ARMS) * FROZEN_BLOCK_COUNT
            and all(
                observed_ranges[i * FROZEN_BLOCK_COUNT:(i + 1) * FROZEN_BLOCK_COUNT]
                == expected_ranges
                for i in range(len(FROZEN_ARMS))
            )
            and all(count == FROZEN_BLOCK_COUNT for count in per_arm_counts.values())
        )

    records_ok = bool(final and len(records) == len(FROZEN_ARMS) * FROZEN_BLOCK_COUNT)
    if not final:
        records_ok = bool(len(records) <= len(FROZEN_ARMS) * FROZEN_BLOCK_COUNT)

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
            if int(record.get("key_dependent_bits", -1)) != expected_kdb:
                prefixes_ok = False
                break
            if int(record.get("full_block_key_dependent_bits", -1)) != int(spec.leakage_bits):
                prefixes_ok = False
                break
        elif int(record.get("key_dependent_bits", -1)) != 0:
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
        recount = backoff_recount_events(events)
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
                int(record.get("key_dependent_bits", -1)) != expected_kdb
                or int(record.get("public_control_bits", -1)) != expected_public
            ):
                disclosure_ok = False
                break

    mode = str(accounting.get("input_mode"))
    if mode == "real":
        expected_opens = {
            "counts": 1 if accounting.get("counts_input_mode") == "v25_npz" else 0,
            "hold": 1 if accounting.get("hold_input_mode") == "pairs_parquet" else 0,
        }
        one_open_ok = bool(
            int(accounting["counts_content_opens"]) == expected_opens["counts"]
            and int(accounting["hold_content_opens"]) == expected_opens["hold"]
            and int(accounting["attempts_consumed_by_this_run"]) == 1
            and int(accounting["retries"]) == 0
            and not bool(accounting["reopen_attempted"])
            and not bool(accounting["retry_after_open"])
        )
    else:
        one_open_ok = bool(
            int(accounting["counts_content_opens"]) == 0
            and int(accounting["hold_content_opens"]) == 0
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
        and stat_unchanged(hold_stat_before, hold_stat_after)
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
        "hold_split_manifest_identity": bool(manifest_ok),
        "p18_block_range_identity": bool(p18_ok),
        "target_population_contract": bool(precondition_passed),
        "hold_population_exact": bool(population_ok),
        "blocks_exact_with_declared_remainder": bool(blocks_ok),
        "fifteen_records_exact": bool(records_ok),
        "sc_calls_exact": bool(sc_ok),
        "tags_exact": bool(tags_ok),
        "orders_valid_k_prefixes_within_registered_arms": bool(orders_ok and identity_ok),
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


def _stat_record(path) -> dict:
    if path is None:
        return {"path": None, "size_bytes": None, "mtime_ns": None}
    st = Path(path).stat()
    return {"path": str(path), "size_bytes": int(st.st_size), "mtime_ns": int(st.st_mtime_ns)}


def _block_view(block, field) -> dict:
    """Per-block truth views shared by the five arms (computed once)."""
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


def run_backoff_diagnostic(
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
    hold_pairs=FROZEN_HOLD_PAIRS_PATH,
    hold_table=None,
    manifest_path=FROZEN_MANIFEST_PATH,
    hold_frames=FROZEN_HOLD_FRAME_RANGE,
    block_frames: int = FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
    tag_master: int = FROZEN_TAG_MASTER,
    chunk_rows: int = FROZEN_CHUNK_ROWS,
    tag_bits: int = FROZEN_TAG_BITS,
    out_dir,
    total_wall_s: float = TOTAL_WALL_S,
    expected_entropies=None,
) -> BackoffDiagnosticRun:
    """Execute the frozen P19 five-arm diagnostic once; write five files.

    ``counts`` and ``hold_table`` plus ``expected_entropies`` are documented
    injected test seams; the frozen CLI passes only the frozen point and
    reads each protected input through its accepted loader exactly once.
    """
    global _NPZ_CONTENT_OPENED, _HOLD_PARQUET_CONTENT_OPENED
    out_path = Path(out_dir)
    if out_path.exists():
        raise FileExistsError(f"refusing to overwrite existing output root: {out_path}")
    floor = _check_floor(floor)
    if floor != FROZEN_FLOOR:
        raise ValueError(f"frozen point requires floor={FROZEN_FLOOR}, got {floor}")
    if source != FROZEN_SOURCE:
        raise ValueError(f"frozen point requires source={FROZEN_SOURCE!r}, got {source!r}")
    n = opf._check_n(n)
    k1 = _check_base_k1(k1)
    k2 = _check_base_k2(k2)
    opf._check_chunk_contract(chunk_rows)
    opf._check_tag_bits(tag_bits)
    hold_frames = hm._check_frame_range(hold_frames, "hold-frames", FROZEN_HOLD_FRAME_RANGE)
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise ValueError(
            f"frozen point requires block-frames={FROZEN_BLOCK_FRAMES}, got {block_frames}")
    remainder_frames = hm._check_frame_range(
        remainder_frames, "remainder-frames", FROZEN_REMAINDER_FRAME_RANGE)
    tag_master = _check_tag_master(tag_master)
    check_frozen_arm_table()

    # Predecessor identity, split manifest and the accepted P18 pin are
    # verified before any root exists and before either protected content
    # open; a mismatch consumes nothing.
    if str(construction_digest) != FROZEN_CONSTRUCTION_DIGEST:
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = verify_predecessor_construction(construction, expected_digest=construction_digest)
    identity = verified["record"]
    manifest = verify_split_manifest(manifest_path, source=source)
    p18_pin = verify_p18_block_identity()
    l1_order = np.asarray(verified["l1_order"], dtype=np.int64)
    l2_order = np.asarray(verified["l2_order"], dtype=np.int64)

    # One-open guards are refusals before any content open of either input.
    if counts is None and _NPZ_CONTENT_OPENED:
        raise ValueError("reopen refused: the single NPZ content open was already consumed")
    if hold_table is None and _HOLD_PARQUET_CONTENT_OPENED:
        raise ValueError("reopen refused: the single HOLD parquet content open was already consumed")

    # Input existence and stat-only metadata come before any content open.
    real_counts = counts is None
    real_hold = hold_table is None
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
    if real_hold:
        hold_path = Path(hold_pairs)
        if not hold_path.is_file():
            raise FileNotFoundError(f"1M HOLD pairs parquet not found: {hold_path}")
        hold_stat_before = _stat_record(hold_path)
    else:
        hold_stat_before = _stat_record(None)
    registered_paths = []
    if real_counts:
        registered_paths.append(str(Path(counts_path).resolve()))
    if real_hold:
        registered_paths.append(str(Path(hold_pairs).resolve()))
    opened_paths: list[str] = []

    plan = _stub_plan(
        out_path=out_path, source=source, floor=floor, n=n, k1=k1, k2=k2,
        construction=construction, digest=construction_digest, hold_pairs=hold_pairs,
        manifest_path=manifest_path, hold_frames=hold_frames, block_frames=block_frames,
        remainder_frames=remainder_frames, tag_master=tag_master, chunk_rows=chunk_rows,
        tag_bits=tag_bits, identity=identity, manifest=manifest, p18_pin=p18_pin,
    )
    accounting = {
        "input_mode": "real" if (real_counts or real_hold) else "injected",
        "counts_input_mode": "v25_npz" if real_counts else "injected_counts",
        "hold_input_mode": "pairs_parquet" if real_hold else "injected_table",
        "counts_path": str(counts_path) if real_counts else None,
        "hold_pairs_path": str(hold_pairs) if real_hold else None,
        "manifest_path": str(manifest_path),
        "construction_path": str(construction),
        "npz_loader": NPZ_LOADER_IDENTITY if real_counts else None,
        "pairs_loader": PAIRS_LOADER_IDENTITY if real_hold else None,
        "registered_content_paths": registered_paths,
        "opened_content_paths": opened_paths,
        "artifact_content_reads_allowed_per_input": 1,
        "counts_content_opens": 0,
        "hold_content_opens": 0,
        "attempts_allowed": 1,
        "attempts_consumed_by_this_run": 0,
        "retries": 0,
        "reopen_attempted": False,
        "retry_after_open": False,
        "consumption_point": ATTEMPT_CONSUMPTION_POINT,
    }
    npz_stat_after = dict(npz_stat_before)
    hold_stat_after = dict(hold_stat_before)
    identity_doc = {
        "protocol": PROTOCOL_NAME,
        "mode": MODE,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repository": "HD-QKD_Polar_Comparison-nbpolar",
        "out_root": str(out_path),
        "predecessor_construction": dict(identity),
        "hold_split_manifest": dict(manifest),
        "p18_block_range_identity": dict(p18_pin),
        "input_stats_before": {
            "counts_npz": dict(npz_stat_before),
            "hold_pairs_parquet": dict(hold_stat_before),
        },
        "input_stats_after": {
            "counts_npz": dict(npz_stat_after),
            "hold_pairs_parquet": dict(hold_stat_after),
        },
        "attempt_read_accounting": accounting,
        "claim_scope": CLAIM_SCOPE,
    }

    # ---- create all five files BEFORE the content open (stub inventory).
    out_path.mkdir(parents=True)
    try:
        opf._write_json(out_path / "frozen_plan.json", plan)
        opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
        (out_path / "per_block_arm_outcomes.jsonl").write_text("", encoding="utf-8")
        opf._write_json(
            out_path / "aggregate_summary.json",
            {"protocol": PROTOCOL_NAME, "status": "pending_content_open"},
        )
        (out_path / "report.md").write_text(
            "# NB-Polar Phase 4-P19 N=32768 1M-HOLD layer/backoff diagnostic\n\n"
            "status: pending_content_open\n",
            encoding="utf-8",
        )
        start = time.perf_counter()

        def persist(summary_doc: dict) -> None:
            opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
            opf._write_json(out_path / "aggregate_summary.json", summary_doc)
            (out_path / "report.md").write_text(_render_report(summary_doc), encoding="utf-8")

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

        # ---- input 2: the single HOLD parquet content open, HOLD rows only.
        if real_hold:
            table = load_pairs_table(Path(hold_pairs))
            _HOLD_PARQUET_CONTENT_OPENED = True
            accounting["hold_content_opens"] = 1
            opened_paths.append(str(Path(hold_pairs).resolve()))
            if int(accounting["attempts_consumed_by_this_run"]) < 1:
                accounting["attempts_consumed_by_this_run"] = 1
        else:
            table = hold_table
        table = normalize_pair_columns(table)
        formation = form_holdout_blocks(
            table, hold_frames=hold_frames, block_frames=block_frames,
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

        views = [_block_view(block, field) for block in formation["blocks"]]
        scoring_by_block = [
            _block_scoring(block, p1, p2) for block in formation["blocks"]
        ]
        slots = [
            (arm_index, spec, block_index, block)
            for arm_index, spec in enumerate(FROZEN_ARMS)
            for block_index, block in enumerate(formation["blocks"])
        ]
        total_slots = len(slots)

        def current_gates(*, final: bool) -> dict:
            return _integrity_gates(
                out_path=out_path, n=n, p18_pin=p18_pin, identity=identity,
                manifest=manifest, l1_order=l1_order, l2_order=l2_order,
                formation=formation, records=records, events=events, calls=calls,
                incremental=incremental, accounting=accounting,
                provenance_violations=provenance_violations, start=start,
                cap=budget_cap, resource_stop=resource_stop,
                precondition_passed=bool(precondition_report.passed), final=final,
                npz_stat_before=npz_stat_before, npz_stat_after=npz_stat_after,
                hold_stat_before=hold_stat_before, hold_stat_after=hold_stat_after,
                registered_paths=registered_paths, opened_paths=opened_paths,
                k1=k1, k2=k2,
            )

        def partial_summary(outcome_label: str, gates: dict) -> dict:
            aggregates = build_aggregates(records)
            try:
                recount = backoff_recount_events(events)
                mismatches = opf._transcript_mismatches(incremental, recount)
            except ValueError:
                recount = {
                    "key_dependent_bits": None,
                    "public_control_bits": None,
                    "tag_invocations": None,
                    "event_types": {},
                }
                mismatches = ["recount_unavailable"]
            return {
                "analysis": PROTOCOL_NAME,
                "mode": MODE,
                "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "repository": "HD-QKD_Polar_Comparison-nbpolar",
                "source": source,
                "counts_path": accounting.get("counts_path"),
                "hold_pairs_path": accounting.get("hold_pairs_path"),
                "input_mode": accounting.get("input_mode"),
                "q": Q,
                "n": int(n),
                "k1": int(k1),
                "k2": int(k2),
                "target_f": float(FROZEN_TARGET_F),
                "chunk_rows": int(chunk_rows),
                "tag_bits": int(tag_bits),
                "tag_master": int(tag_master),
                "identity": dict(identity),
                "manifest": dict(manifest),
                "p18_block_range_identity": dict(p18_pin),
                "input_stats_before": {
                    "counts_npz": dict(npz_stat_before),
                    "hold_pairs_parquet": dict(hold_stat_before),
                },
                "input_stats_after": {
                    "counts_npz": dict(npz_stat_after),
                    "hold_pairs_parquet": dict(hold_stat_after),
                },
                "entropy": {
                    "h1": float(entropy.h1),
                    "h2": float(entropy.h2),
                    "total": float(entropy.total),
                    "floor_total": float(entropy.floor_total),
                    "floor_entropy_change": float(entropy.floor_change),
                    "expected_h1": float(expected_h1),
                    "expected_h2": float(expected_h2),
                    "expected_total": float(expected_total),
                    "checks": dict(precondition_report.checks),
                    "column_dev": float(precondition_report.column_dev),
                    "p_b_sum": float(np.sum(precondition_report.p_b)),
                },
                "hold": {
                    "hold_frame_range": formation["hold_frame_range"],
                    "hold_frames": formation["hold_frames"],
                    "hold_pairs": formation["hold_pairs"],
                    "block_ranges": formation["block_ranges"],
                    "block_count": len(formation["blocks"]),
                    "remainder": dict(formation["remainder"]),
                },
                "arms": _arm_plan_rows(float(opf.EXPECTED_H1 + opf.EXPECTED_H2)),
                "records_completed": int(len(records)),
                "records_expected": int(total_slots),
                "sc_calls": int(calls["sc"]),
                "planned_sc_calls": int(PLANNED_SC_CALLS),
                "tag_invocations": int(incremental["tag_invocations"]),
                "planned_tag_invocations": int(PLANNED_TAG_INVOCATIONS),
                "provenance_violations": int(provenance_violations),
                "operational": aggregates["operational"],
                "oracle_control": aggregates["oracle_control"],
                "partition": aggregates["partition"],
                "recovery": aggregates["recovery"],
                "disclosure": {
                    "key_dependent_bits": int(incremental["key_dependent_bits"]),
                    "public_control_bits": int(incremental["public_control_bits"]),
                    "tag_invocations": int(incremental["tag_invocations"]),
                    "recount": recount,
                    "mismatches": mismatches,
                    "planned_total_key_dependent_bits": int(FROZEN_TOTAL_KEY_DEPENDENT_BITS),
                    "planned_total_public_control_bits": int(FROZEN_TOTAL_PUBLIC_CONTROL_BITS),
                    "public_control_bits_per_tag": int(FROZEN_PUBLIC_CONTROL_BITS),
                    "ratio_note": ("sample cross-entropy-normalized descriptive "
                                   "disclosure ratios, explicitly NOT qualification "
                                   "reconciliation efficiency"),
                },
                "decision": {
                    "complete": COMPLETE_LABEL,
                    "blocked": "BLOCKED(<earliest gate>)",
                    "recovery_threshold": None,
                    "zero_recovery_is_complete": True,
                    "three_recovery_is_complete": True,
                },
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
                    gates_now = current_gates(final=False)
                    persist(partial_summary(
                        f"RUNNING(record {len(records)}/{total_slots})", gates_now))
                rejected = True
                break
            view = views[block_index]
            scoring = scoring_by_block[block_index]
            frame_start = int(block["frame_start"])
            seed = backoff_seed_bits(tag_master, n, spec.name, block_index,
                                     bit_length=seed_bits_for(n))

            def _tag_fn(bits, _seed, tag_bits, _fixed=seed):
                return toeplitz_tag(bits, _fixed, tag_bits)

            block_start = time.perf_counter()
            if spec.kind == "operational":
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
                    raise
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
                record = _operational_record(
                    result, spec=spec, arm_index=arm_index, block=block,
                    scoring=scoring, resources=resources, error=error,
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
                    raise
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
                record = _control_record(
                    result, spec=spec, arm_index=arm_index, block=block,
                    scoring=scoring, resources=resources, error=error,
                )

            records.append(record)
            opf._append_jsonl(out_path / "per_block_arm_outcomes.jsonl", record)
            for event in backoff_block_events(n, spec, block_index, frame_start, record):
                events.append(event)
                incremental["key_dependent_bits"] += int(event["key_dependent_bits"])
                incremental["public_control_bits"] += int(event["public_control_bits"])
                if str(event["event_type"]) == "verification_tag":
                    incremental["tag_invocations"] += 1
            gates_now = current_gates(final=False)
            persist(partial_summary(
                f"RUNNING(record {len(records)}/{total_slots})", gates_now))

        # ---- closing stat checks, final gates, label and evidence.
        wall_s = time.perf_counter() - start
        rss_peak = opf._peak_rss_bytes()
        if real_counts:
            npz_stat_after = _stat_record(counts_path)
            identity_doc["input_stats_after"]["counts_npz"] = dict(npz_stat_after)
        if real_hold:
            hold_stat_after = _stat_record(hold_pairs)
            identity_doc["input_stats_after"]["hold_pairs_parquet"] = dict(hold_stat_after)
        identity_doc["attempt_read_accounting"] = dict(
            accounting, counts_content_opens=accounting["counts_content_opens"],
            hold_content_opens=accounting["hold_content_opens"],
            opened_content_paths=list(opened_paths),
            attempt_read_accounting_finalized=True,
        )
        gates = current_gates(final=True)
        outcome = backoff_label(gates)
        summary = partial_summary(outcome, gates)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        summary["input_stats_after"] = {
            "counts_npz": dict(npz_stat_after),
            "hold_pairs_parquet": dict(hold_stat_after),
        }
        summary["attempt_read_accounting"] = dict(
            accounting, opened_content_paths=list(opened_paths), finalized=True)
        summary["rejected_after_resource_stop"] = bool(rejected)
        persist(summary)
        return BackoffDiagnosticRun(
            records=records,
            events=events,
            identity=dict(identity),
            manifest=dict(manifest),
            p18_pin=dict(p18_pin),
            plan=plan,
            summary=summary,
        )
    except BackoffDiagnosticContractError as exc:
        _finalize_blocked(out_path, identity_doc, accounting, opened_paths, str(exc))
        raise
    except hm.HoldoutMicrocheckContractError as exc:
        _finalize_blocked(out_path, identity_doc, accounting, opened_paths, str(exc))
        raise
    except TargetPopulationContractError as exc:
        _finalize_blocked(out_path, identity_doc, accounting, opened_paths, str(exc))
        raise
    except MemoryError as exc:
        label = "BLOCKED(resource_limits_met_and_no_abort)"
        _finalize_blocked(
            out_path, identity_doc, accounting, opened_paths,
            f"{label}: MemoryError: {exc}",
        )
        raise BackoffDiagnosticResourceError(f"{label}: MemoryError: {exc}") from exc


def _finalize_blocked(out_path, identity_doc, accounting, opened_paths, message: str) -> None:
    """Best-effort BLOCKED stubs after a post-open failure; never a fresh root."""
    try:
        label = str(message).split(":", 1)[0]
        identity_doc["attempt_read_accounting"] = dict(
            accounting, opened_content_paths=list(opened_paths),
            attempt_read_accounting_finalized=True,
        )
        opf._write_json(out_path / "input_and_predecessor_identity.json", identity_doc)
        blocked = {
            "protocol": PROTOCOL_NAME,
            "mode": MODE,
            "status": label,
            "outcome_label": label,
            "message": str(message),
            "attempt_read_accounting": dict(accounting, opened_content_paths=list(opened_paths)),
            "claim_scope": CLAIM_SCOPE,
        }
        opf._write_json(out_path / "aggregate_summary.json", blocked)
        (out_path / "report.md").write_text(
            "# NB-Polar Phase 4-P19 N=32768 1M-HOLD layer/backoff diagnostic\n\n"
            f"outcome label: `{label}`\n\n{message}\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p19-holdout-backoff-diagnostic",
        description=(
            "NB-Polar Phase 4-P19 N=32768 1M HOLD layer/backoff diagnostic "
            "(frozen V25 counts, verified P16 construction, three accepted P18 "
            "HOLD blocks, five frozen arms)"
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
    parser.add_argument("--hold-pairs", required=True, dest="hold_pairs")
    parser.add_argument("--hold-frames", required=True, type=int, nargs=2, dest="hold_frames")
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
        run = run_backoff_diagnostic(
            counts_path=args.counts,
            source=args.source,
            floor=args.floor,
            n=args.n,
            k1=args.k1,
            k2=args.k2,
            construction=args.construction,
            construction_digest=args.construction_digest,
            hold_pairs=args.hold_pairs,
            hold_frames=tuple(args.hold_frames),
            block_frames=args.block_frames,
            remainder_frames=tuple(args.remainder_frames),
            tag_master=args.tag_master,
            chunk_rows=args.chunk_rows,
            tag_bits=args.tag_bits,
            out_dir=args.out_dir,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        print(f"nbpolar phase4-p19 backoff diagnostic refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "records_completed": summary["records_completed"],
                "operational_exact_count": summary["operational"]["exact_count"],
                "operational_exact_counts_ordered": summary["recovery"]["exact_counts_ordered"],
                "first_operational_recovery_arm": summary["recovery"]["first_operational_recovery_arm"],
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
