"""NB-Polar Phase 4-P18 N=32768 1M-HOLD operational microcheck.

Frozen packet ``NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK``, OpenSpec
``formal-ir-nbpolar-phase4-p0`` P18 delta: run the accepted P16/P17
operational point exactly once on the only three complete, non-overlapping
N=32768 blocks available in the V25 1M HOLD split (frames 1600..1983 of the
``v13r3fresh`` 1M pairs parquet, 128 frames = 32768 pairs each). This is a
real-input microcheck of loading, ordering, fixed-TRAIN prior use, decoder
behavior and accounting. It is not a FER gate and has no recovery
threshold: 0..3 exact outcomes are all descriptive.

Frozen semantics:

- Predecessor identity first: before any output root exists and before
  either protected content open, the P16 accepted
  ``construction_and_allocation.json`` is read (JSON only) and verified
  (N=32768, K_total=6811, K1=319, K2=6492, valid L1/L2 orders, canonical
  digest ``055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b``),
  and the V25 run_04 ``split_manifest.json`` is read (JSON only) and must
  declare the 1M population as 400 HOLD frames / 102400 HOLD pairs. Any
  mismatch stops with zero protected reads and zero attempts. P16 remains
  immutable; no construction path exists here.
- Protected inputs, each content-opened exactly once: (1) the V25 1M TRAIN
  ``channel_counts.npz`` through the accepted ``load_v25_channel_counts``
  after a stat-only size check of exactly ``25,166,822`` bytes, used only
  to rebuild the frozen floor-1e-15 prior and repeat the accepted
  population guards; (2) the 1M ``pairs.parquet`` through the accepted
  ``load_pairs_table``/``normalize_pair_columns`` loader, used only for
  HOLD frames 1600..1999. The single scientific attempt is consumed at the
  first protected content open (the NPZ); a module-level guard refuses any
  second content open of either input. Input size/mtime are recorded
  before the opens (stat only) and re-checked unchanged after the run.
- Deterministic block formation (no shuffle, resampling, overlap, padding,
  pooling or fitting anywhere): sort HOLD rows by ``(frame_id, pair_idx)``;
  require exactly 400 frames (1600..1999), exactly 256 rows per frame,
  ``pair_idx`` 0..255 and symbols 0..1023. Blocks are frames
  1600..1727, 1728..1855 and 1856..1983 (three exact non-overlapping
  N=32768 blocks); frames 1984..1999 (4096 pairs) are the declared unused
  remainder and never enter any block.
- Operational path per block: exactly one L1 SC and one
  candidate-conditioned L2 SC through the accepted
  ``run_operational_block`` with the verified P16 orders and
  K1=319/K2=6492 at ``chunk_rows=512``; 10-bit label reconstruction; one
  64-bit Toeplitz tag in the P18/N/block seed domain (public master
  ``2026092050``). Alice truth enters only scoring, disclosed values and
  tag construction; it never enters Bob metrics, candidate priors or
  decisions.
- Descriptive scalars per block only: frame range, raw channel SER,
  per-layer and total NLL in bits under the fixed TRAIN prior,
  ``34119`` key-dependent bits, ``327743`` public-control bits, outcome
  bucket, L1 correctness, tag result and wall/RSS/VmPeak/VmSize. The
  sample ``34119 / total_nll_bits`` ratio is a descriptive
  cross-entropy-normalized disclosure ratio, explicitly NOT qualification
  reconciliation efficiency.
- Labels: all integrity gates true →
  ``TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE``
  regardless of 0..3 exact outcomes; any integrity/resource failure →
  ``BLOCKED(<earliest gate>)``. Recovery is never an integrity gate.
- Exactly five scalar-only files under the absent root, created as stubs
  before the opens and checkpointed after every block; no private
  vectors, labels, metrics, raw rows or tag seed bits are persisted. 2 GiB
  virtual limit, 2 GiB RSS cap and 600 s budget; MemoryError is caught
  around the entire post-open path, checkpoints are preserved and the run
  is never rerun, repaired, retuned or cleaned up.

No Model-F/raw/real/EVAL frame, no other N, no BEC arm, no retry or
refinement arm, no transform/belief/list decoder and no soft-marginal APP
path, no second tag, no fitting/sampling on HOLD, no production benchmark,
no FER/efficiency/key-rate qualification or promotion, no commit. Scope: a
real-input operational microcheck of the frozen V25 1M HOLD split, not
real-frame FER or reconciliation-efficiency evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass
from numbers import Integral, Real
from pathlib import Path

import numpy as np

from ...io.pairs_loader import load_pairs_table, normalize_pair_columns
from ..shared import canonical_event, toeplitz_tag
from ..v35_algorithm_development import SOURCE_IDS, load_v25_channel_counts
from . import operational_f13 as opf
from .algebra import make_gf32
from .operational_f13 import run_operational_block
from .operational_f13_replication import verify_predecessor_construction
from .target_construction import TargetPopulationContractError, target_preconditions
from .transform import polar_transform
from .two_layer import (
    DISCLOSED_BITS_PER_COORDINATE,
    TAG_BITS,
    labels_to_bits,
    seed_bits_for,
)

PROTOCOL_NAME = "nbpolar-p18-holdout-microcheck"
MODE = "holdout-microcheck"

Q = 32
N_BOB = 1024
ALPHA = 2
FROZEN_N = 32768
FROZEN_SOURCE = "1M"
FROZEN_FLOOR = 1e-15
FROZEN_TARGET_F = 1.3
FROZEN_K1 = 319
FROZEN_K2 = 6492
FROZEN_K_TOTAL = 6811
FROZEN_LEAKAGE_BITS = 34119  # 5 * 6811 + 64
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
FROZEN_TAG_MASTER = 2026092050
FROZEN_CHUNK_ROWS = 512
FROZEN_TAG_BITS = TAG_BITS  # 64
PLANNED_SC_CALLS_MAX = 2 * FROZEN_BLOCK_COUNT  # 6
PLANNED_TAG_INVOCATIONS = FROZEN_BLOCK_COUNT  # 3

EXPECTED_NPZ_BYTES = 25166822
EXPECTED_HOLD_PARQUET_BYTES = 1354289  # build_manifest provenance only (never a refusal)
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
FROZEN_MANIFEST_SCHEMA = "nbldpc_v25_split_manifest_v1"
FROZEN_CONSTRUCTION_PATH = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/"
    "operational_f13_gate/construction_and_allocation.json"
)
FROZEN_CONSTRUCTION_DIGEST = (
    "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
)
FROZEN_OUT_ROOT = (
    ".workbuddy/queue/NBPOLAR-PHASE4-P18-N32768-HOLDOUT-MICROCHECK/"
    "holdout_microcheck"
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

ARM = "microcheck"
METHOD = "nbpolar_holdout_microcheck"
OUTCOMES = opf.OUTCOMES
SEED_PREFIX = "nbpolar-p18-holdout-microcheck-seed"

ATTEMPT_CONSUMPTION_POINT = "first protected content open (load_v25_channel_counts)"

OUTPUT_FILES = (
    "frozen_plan.json",
    "input_and_construction_identity.json",
    "per_block_outcomes.jsonl",
    "aggregate_summary.json",
    "report.md",
)

INTEGRITY_GATE_ORDER = (
    "predecessor_construction_identity",
    "hold_split_manifest_identity",
    "target_population_contract",
    "hold_population_exact",
    "blocks_exact_with_declared_remainder",
    "orders_valid_k_replay_f_within_budget",
    "sc_calls_exact",
    "tags_exact",
    "buckets_disjoint_exhaustive",
    "truth_isolation",
    "undetected_zero",
    "nonfinite_zero",
    "disclosure_recount_exact",
    "one_open_per_protected_input",
    "input_stat_unchanged",
    "no_unregistered_access",
    "resource_limits_met_and_no_abort",
)

OUTCOME_PRECEDENCE = [
    "resource_abort: block not executed (preregistered budget stop)",
    "nonfinite: numeric nonfinite failure in L1/L2 SC; no tag",
    "decode_failed: other L1/L2 SC exception; no tag",
    "verify_failed: tag mismatch",
    "exact: tag pass and label == true label",
    "undetected: tag pass and not exact (never success)",
]

SUPPORT_RULE = (
    "f = counts / column totals; every cell below 1e-15 replaced by 1e-15; "
    "columns renormalized; p_b = column totals / total count; "
    "P1/P2 = accepted derive_p1/derive_p2(f) under A=32*U1+U2; no lambda, "
    "backoff, tuning, floor scan or fitting (exact P7 rule)"
)
BLOCK_RULE = (
    "sort HOLD rows by (frame_id, pair_idx); require exactly 400 frames "
    "1600..1999, 256 rows per frame, pair_idx 0..255 and symbols 0..1023; "
    "blocks 1600..1727 / 1728..1855 / 1856..1983 (128 frames = 32768 pairs "
    "each); frames 1984..1999 are the declared unused remainder; no "
    "shuffle, resampling, overlap, padding, pooling or fitting"
)
NLL_RULE = (
    "per block under the fixed floor-1e-15 TRAIN prior: "
    "l1_nll_bits = sum_i -log2 p1[high_i, bob_i]; "
    "l2_nll_bits = sum_i -log2 p2[high_i, bob_i, low_i]; "
    "total_nll_bits = l1 + l2 (bits per 32768-pair block); descriptive "
    "scoring only, never a metric input"
)
RATIO_RULE = (
    "disclosure_ce_ratio = 34119 / total_nll_bits for every registered "
    "block with an observed NLL (the numerator is the registered full-block "
    "disclosure, so a partially invoked block keeps a nominal value; actual "
    "disclosure is the transcript recount); aggregate = (34119 * observed "
    "blocks) / total_nll_bits; a sample cross-entropy-normalized "
    "descriptive disclosure ratio, explicitly NOT qualification "
    "reconciliation efficiency"
)
TRUTH_BOUNDARY = (
    "Alice truth enters only scoring (SER/NLL), disclosed values, tag "
    "construction and tag scoring; it never enters Bob metrics, candidate "
    "priors or decisions; each layer restarts SC with no state transfer; "
    "each L2 metric is gathered from Bob and the hard L1 candidate only"
)
OPERATIONAL_RULE = (
    "per block: disclose true U1 at verified order1[:K1], operational L1 "
    "SC; L2 metrics from Bob plus the hard L1 candidate only; disclose true "
    "U2 at verified order2[:K2], restarted operational L2 SC; "
    "label_hat=32*high_hat+low_hat; exactly one 64-bit Toeplitz tag in the "
    "P18/N/block seed domain (public master 2026092050); exactly one of "
    "exact/undetected/verify_failed/decode_failed/nonfinite/resource_abort; "
    "undetected never success"
)
NO_THRESHOLD_RULE = (
    "there is no exact-count, FER, winner or promotion threshold and no "
    "recovery gate of any kind; 0..3 exact outcomes are descriptive; only "
    "integrity/resource failures produce BLOCKED(<earliest gate>)"
)
CLAIM_SCOPE = (
    "real-input operational microcheck of the frozen V25 1M HOLD split at "
    "N=32768 only (three registered chronological blocks, frames "
    "1600..1983); descriptive loading/ordering/prior/decoder/accounting "
    "evidence, not real-frame FER, reconciliation efficiency, leakage, key "
    "rate, scaling superiority, qualification or promotion; the CE-"
    "normalized disclosure ratio is not qualification efficiency; "
    "undetected is never success"
)

FROZEN_COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar\n"
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2\n"
    "ulimit -v 2097152\n"
    "timeout 600 /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python -m "
    "comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_microcheck "
    f"--counts {FROZEN_COUNTS_PATH} --source 1M --floor 1e-15 "
    "--n 32768 --k1 319 --k2 6492 "
    f"--construction {FROZEN_CONSTRUCTION_PATH} --construction-digest {FROZEN_CONSTRUCTION_DIGEST} "
    f"--hold-pairs {FROZEN_HOLD_PAIRS_PATH} "
    "--hold-frames 1600 1999 --block-frames 128 --remainder-frames 1984 1999 "
    "--tag-master 2026092050 --chunk-rows 512 --tag-bits 64 "
    f"--out-dir {FROZEN_OUT_ROOT}"
)

# Process-level one-open guards: set at the first content open, never cleared.
_NPZ_CONTENT_OPENED = False
_HOLD_PARQUET_CONTENT_OPENED = False

__all__ = [
    "PROTOCOL_NAME",
    "MODE",
    "Q",
    "ALPHA",
    "FROZEN_N",
    "FROZEN_SOURCE",
    "FROZEN_FLOOR",
    "FROZEN_TARGET_F",
    "FROZEN_K1",
    "FROZEN_K2",
    "FROZEN_K_TOTAL",
    "FROZEN_LEAKAGE_BITS",
    "FROZEN_PUBLIC_CONTROL_BITS",
    "FROZEN_BLOCK_COUNT",
    "FROZEN_BLOCK_FRAMES",
    "FROZEN_PAIRS_PER_FRAME",
    "FROZEN_SYMBOLS_PER_BLOCK",
    "FROZEN_HOLD_FRAME_RANGE",
    "FROZEN_HOLD_FRAMES",
    "FROZEN_HOLD_PAIRS",
    "FROZEN_BLOCK_RANGES",
    "FROZEN_REMAINDER_FRAME_RANGE",
    "FROZEN_REMAINDER_FRAMES",
    "FROZEN_REMAINDER_SYMBOLS",
    "FROZEN_TAG_MASTER",
    "FROZEN_CHUNK_ROWS",
    "FROZEN_TAG_BITS",
    "PLANNED_SC_CALLS_MAX",
    "PLANNED_TAG_INVOCATIONS",
    "EXPECTED_NPZ_BYTES",
    "EXPECTED_HOLD_PARQUET_BYTES",
    "FROZEN_COUNTS_PATH",
    "FROZEN_HOLD_PAIRS_PATH",
    "FROZEN_MANIFEST_PATH",
    "FROZEN_MANIFEST_SCHEMA",
    "FROZEN_CONSTRUCTION_PATH",
    "FROZEN_CONSTRUCTION_DIGEST",
    "FROZEN_OUT_ROOT",
    "NPZ_LOADER_IDENTITY",
    "PAIRS_LOADER_IDENTITY",
    "RSS_LIMIT_BYTES",
    "TOTAL_WALL_S",
    "EXTERNAL_TIMEOUT_S",
    "ULIMIT_VIRTUAL_KIB",
    "ARM",
    "METHOD",
    "OUTCOMES",
    "SEED_PREFIX",
    "ATTEMPT_CONSUMPTION_POINT",
    "OUTPUT_FILES",
    "INTEGRITY_GATE_ORDER",
    "OUTCOME_PRECEDENCE",
    "SUPPORT_RULE",
    "BLOCK_RULE",
    "NLL_RULE",
    "RATIO_RULE",
    "TRUTH_BOUNDARY",
    "OPERATIONAL_RULE",
    "NO_THRESHOLD_RULE",
    "CLAIM_SCOPE",
    "FROZEN_COMMAND",
    "COMPLETE_LABEL",
    "HoldoutMicrocheckContractError",
    "HoldoutMicrocheckResourceError",
    "HoldoutMicrocheckRun",
    "holdout_seed_bits",
    "verify_split_manifest",
    "holdout_nll_bits",
    "raw_symbol_error_rate",
    "form_holdout_blocks",
    "hold_microcheck_label",
    "holdout_block_events",
    "holdout_recount_events",
    "run_holdout_microcheck",
    "build_parser",
    "main",
]

COMPLETE_LABEL = "TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_HOLD_MICROCHECK_COMPLETE"


class HoldoutMicrocheckContractError(ValueError):
    """Post-open hold-population/formation failure: BLOCKED(<earliest gate>)."""


class HoldoutMicrocheckResourceError(RuntimeError):
    """Wall/RSS/MemoryError stop: checkpoints preserved, BLOCKED, never rerun."""


def _as_int(value, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer, got {value!r}")
    out = int(value)
    if minimum is not None and out < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {out}")
    return out


def _check_floor(value) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"floor must be a real number, got {value!r}")
    out = float(value)
    if not np.isfinite(out) or not 0.0 < out < 1.0:
        raise ValueError(f"floor must lie in (0, 1), got {value!r}")
    return out


def _check_k1(value) -> int:
    out = _as_int(value, "k1", minimum=0)
    if out != FROZEN_K1:
        raise ValueError(f"frozen point requires k1={FROZEN_K1}, got {out}")
    return out


def _check_k2(value) -> int:
    out = _as_int(value, "k2", minimum=0)
    if out != FROZEN_K2:
        raise ValueError(f"frozen point requires k2={FROZEN_K2}, got {out}")
    return out


def _check_frame_range(value, name: str, expected: tuple) -> tuple:
    try:
        pair = tuple(_as_int(v, name, minimum=0) for v in value)
    except TypeError as exc:
        raise TypeError(f"{name} must be a pair of integers: {exc}") from exc
    if pair != tuple(expected):
        raise ValueError(f"frozen point requires {name}={tuple(expected)}, got {pair}")
    return pair


def _check_tag_master(value) -> int:
    out = _as_int(value, "tag_master", minimum=0)
    if out != FROZEN_TAG_MASTER:
        raise ValueError(f"frozen point requires tag-master={FROZEN_TAG_MASTER}, got {out}")
    return out


def holdout_seed_bits(
    master: int,
    n: int,
    block_index: int,
    *,
    bit_length: int | None = None,
) -> np.ndarray:
    """Deterministic public per-block Toeplitz seed (P18 domain).

    Rule: concatenate SHA-256 over
    ``"nbpolar-p18-holdout-microcheck-seed:<master>:<n>:<block_index>:
    <counter>"`` for ``counter = 0, 1, ...`` (ASCII decimal), unpack each
    digest MSB-first, and truncate to ``bit_length`` (default ``10*n + 63``).
    The P18 prefix differs from the P16 and P17 prefixes on purpose: scored
    tags here never share a prior seed domain. Seed contents are public
    control and are never persisted; only the bit length is recorded.
    """
    master_seed = _as_int(master, "master", minimum=0)
    n = _as_int(n, "n", minimum=1)
    index = _as_int(block_index, "block_index", minimum=0)
    length = seed_bits_for(n) if bit_length is None else _as_int(bit_length, "bit_length", minimum=1)
    prefix = f"{SEED_PREFIX}:{master_seed}:{int(n)}:{int(index)}"
    buf = bytearray()
    counter = 0
    while len(buf) * 8 < length:
        buf.extend(hashlib.sha256(f"{prefix}:{counter}".encode("ascii")).digest())
        counter += 1
    bits = np.unpackbits(np.frombuffer(bytes(buf), dtype=np.uint8), bitorder="big")
    return bits[:length].astype(np.uint8)


def verify_split_manifest(path, *, source: str = FROZEN_SOURCE) -> dict:
    """Verify the V25 split manifest declares the frozen 1M HOLD population.

    JSON read only; no protected content open. The manifest must carry the
    accepted schema and declare exactly 400 HOLD frames / 102400 HOLD pairs
    for the source's tag. Any mismatch raises before any root exists and
    before either protected content open, consuming nothing.
    """
    if source != FROZEN_SOURCE:
        raise ValueError(f"frozen point requires source={FROZEN_SOURCE!r}, got {source!r}")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"split manifest not found: {p}")
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(f"hold split manifest identity unreadable: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("schema") != FROZEN_MANIFEST_SCHEMA:
        raise ValueError(
            "hold split manifest identity: schema "
            f"{doc.get('schema')!r} != accepted {FROZEN_MANIFEST_SCHEMA!r}"
        )
    per_source = doc.get("per_source")
    tag = SOURCE_IDS[source]
    cell = per_source.get(tag) if isinstance(per_source, dict) else None
    if not isinstance(cell, dict):
        raise ValueError(f"hold split manifest identity: missing per_source entry {tag!r}")
    try:
        frames = cell["frames"]
        pairs = cell["pairs"]
        hold_frames = int(frames["hold"])
        hold_pairs = int(pairs["hold"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"hold split manifest identity: missing hold counts: {exc}") from exc
    if hold_frames != FROZEN_HOLD_FRAMES or hold_pairs != FROZEN_HOLD_PAIRS:
        raise ValueError(
            "hold split manifest identity: 1M HOLD population "
            f"{hold_frames} frames / {hold_pairs} pairs != frozen "
            f"{FROZEN_HOLD_FRAMES} / {FROZEN_HOLD_PAIRS}"
        )
    return {
        "manifest_path": str(p),
        "schema": FROZEN_MANIFEST_SCHEMA,
        "source": source,
        "source_tag": tag,
        "hold_frames": hold_frames,
        "hold_pairs": hold_pairs,
        "train_frames": int(frames.get("train", -1)),
        "val_frames": int(frames.get("val", -1)),
        "train_pairs": int(pairs.get("train", -1)),
        "val_pairs": int(pairs.get("val", -1)),
        "expected_hold_frames": FROZEN_HOLD_FRAMES,
        "expected_hold_pairs": FROZEN_HOLD_PAIRS,
    }


def holdout_nll_bits(bob, high, low, p1_table, p2_table) -> dict:
    """Per-layer and total NLL in bits under the fixed TRAIN prior.

    ``l1_nll_bits = sum_i -log2 p1[high_i, bob_i]`` and
    ``l2_nll_bits = sum_i -log2 p2[high_i, bob_i, low_i]``; the tables are
    the accepted derived P1/P2 of the floored TRAIN conditional. Pure
    scoring; takes no decision input.
    """
    b = np.asarray(bob, dtype=np.int64)
    h = np.asarray(high, dtype=np.int64)
    lo = np.asarray(low, dtype=np.int64)
    if not (b.shape == h.shape == lo.shape) or b.ndim != 1:
        raise ValueError("block scoring requires equal one-dimensional vectors")
    p1 = np.asarray(p1_table, dtype=np.float64)
    p2 = np.asarray(p2_table, dtype=np.float64)
    if p1.shape != (Q, N_BOB) or p2.shape != (Q, N_BOB, Q):
        raise ValueError("frozen prior tables must be [U1,B] and [U1,B,U2]")
    probs1 = p1[h, b]
    probs2 = p2[h, b, lo]
    if (probs1 <= 0).any() or (probs2 <= 0).any():
        raise ValueError("floored prior produced a non-positive probability")
    l1 = float(-np.sum(np.log2(probs1)))
    l2 = float(-np.sum(np.log2(probs2)))
    n = int(b.size)
    return {
        "l1_nll_bits": l1,
        "l2_nll_bits": l2,
        "total_nll_bits": l1 + l2,
        "l1_nll_bits_per_pair": l1 / n,
        "l2_nll_bits_per_pair": l2 / n,
        "total_nll_bits_per_pair": (l1 + l2) / n,
        "pairs": n,
    }


def raw_symbol_error_rate(alice, bob) -> float:
    """Raw block channel SER: ``mean(alice_symbol != bob_symbol)``."""
    a = np.asarray(alice, dtype=np.int64)
    b = np.asarray(bob, dtype=np.int64)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("raw SER requires equal one-dimensional vectors")
    return float(np.mean(a != b))


def form_holdout_blocks(
    table,
    *,
    hold_frames=FROZEN_HOLD_FRAME_RANGE,
    block_frames=FROZEN_BLOCK_FRAMES,
    remainder_frames=FROZEN_REMAINDER_FRAME_RANGE,
) -> dict:
    """Deterministic HOLD population validation plus block/remainder slicing.

    Accepts a normalized pairs frame (``frame_id``/``pair_idx``/
    ``alice_symbol``/``bob_symbol``). Any malformed population raises
    ``BLOCKED(hold_population_exact)``; any declared-range mismatch raises
    ``BLOCKED(blocks_exact_with_declared_remainder)``. No sorting key
    other than ``(frame_id, pair_idx)`` and no sampling of any kind.
    """
    hold_first, hold_last = _check_frame_range(hold_frames, "hold-frames", FROZEN_HOLD_FRAME_RANGE)
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise HoldoutMicrocheckContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): "
            f"block-frames {block_frames} != frozen {FROZEN_BLOCK_FRAMES}"
        )
    rem_first, rem_last = _check_frame_range(
        remainder_frames, "remainder-frames", FROZEN_REMAINDER_FRAME_RANGE
    )
    try:
        frame_id = np.asarray(table["frame_id"], dtype=np.int64)
        pair_idx = np.asarray(table["pair_idx"], dtype=np.int64)
        alice = np.asarray(table["alice_symbol"], dtype=np.int64)
        bob = np.asarray(table["bob_symbol"], dtype=np.int64)
    except (KeyError, TypeError, ValueError) as exc:
        raise HoldoutMicrocheckContractError(
            f"BLOCKED(hold_population_exact): loader frame is malformed: {exc}"
        ) from exc
    if not (frame_id.shape == pair_idx.shape == alice.shape == bob.shape) or frame_id.ndim != 1:
        raise HoldoutMicrocheckContractError(
            "BLOCKED(hold_population_exact): column shapes disagree"
        )
    for name, values in (("alice_symbol", alice), ("bob_symbol", bob)):
        if values.size == 0 or values.min() < 0 or values.max() >= N_BOB:
            raise HoldoutMicrocheckContractError(
                f"BLOCKED(hold_population_exact): {name} outside 0..{N_BOB - 1}"
            )
    selected = (frame_id >= hold_first) & (frame_id <= hold_last)
    rows = int(np.sum(selected))
    if rows == 0:
        raise HoldoutMicrocheckContractError(
            "BLOCKED(hold_population_exact): no rows in the frozen HOLD frame range"
        )
    frame_id = frame_id[selected]
    pair_idx = pair_idx[selected]
    alice = alice[selected]
    bob = bob[selected]
    unique_frames = np.unique(frame_id)
    if unique_frames.size != FROZEN_HOLD_FRAMES or int(unique_frames[0]) != hold_first or int(unique_frames[-1]) != hold_last:
        raise HoldoutMicrocheckContractError(
            "BLOCKED(hold_population_exact): HOLD frames "
            f"{unique_frames.size} with range {int(unique_frames[0])}..{int(unique_frames[-1])} "
            f"!= frozen {FROZEN_HOLD_FRAMES} with range {hold_first}..{hold_last}"
        )
    if rows != FROZEN_HOLD_PAIRS:
        raise HoldoutMicrocheckContractError(
            "BLOCKED(hold_population_exact): HOLD rows "
            f"{rows} != frozen {FROZEN_HOLD_PAIRS}"
        )
    order = np.lexsort((pair_idx, frame_id))
    frame_id = frame_id[order]
    pair_idx = pair_idx[order]
    alice = alice[order]
    bob = bob[order]
    expected_pair = np.tile(np.arange(FROZEN_PAIRS_PER_FRAME, dtype=np.int64), FROZEN_HOLD_FRAMES)
    if not np.array_equal(pair_idx, expected_pair):
        raise HoldoutMicrocheckContractError(
            "BLOCKED(hold_population_exact): pair_idx is not exactly 0..255 per frame"
        )
    # Blocks must tile the hold span exactly and the remainder must close it.
    ranges = []
    first = hold_first
    for _ in range(FROZEN_BLOCK_COUNT):
        last = first + int(block_frames) - 1
        ranges.append((first, last))
        first = last + 1
    if tuple(ranges) != FROZEN_BLOCK_RANGES:
        raise HoldoutMicrocheckContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): block ranges "
            f"{tuple(ranges)} != frozen {FROZEN_BLOCK_RANGES}"
        )
    if first != rem_first or hold_last != rem_last:
        raise HoldoutMicrocheckContractError(
            "BLOCKED(blocks_exact_with_declared_remainder): remainder "
            f"{rem_first}..{rem_last} does not close {FROZEN_HOLD_FRAME_RANGE}"
        )
    blocks = []
    for index, (start, end) in enumerate(ranges):
        mask = (frame_id >= start) & (frame_id <= end)
        if int(np.sum(mask)) != FROZEN_SYMBOLS_PER_BLOCK:
            raise HoldoutMicrocheckContractError(
                "BLOCKED(blocks_exact_with_declared_remainder): block "
                f"{index} holds {int(np.sum(mask))} pairs != "
                f"{FROZEN_SYMBOLS_PER_BLOCK}"
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
    remainder_mask = (frame_id >= rem_first) & (frame_id <= rem_last)
    return {
        "hold_frame_range": [hold_first, hold_last],
        "hold_frames": int(unique_frames.size),
        "hold_pairs": rows,
        "blocks": blocks,
        "block_ranges": [list(r) for r in ranges],
        "remainder": {
            "frame_start": rem_first,
            "frame_end": rem_last,
            "frames": FROZEN_REMAINDER_FRAMES,
            "symbols": int(np.sum(remainder_mask)),
            "used": False,
        },
    }


def hold_microcheck_label(gates: dict) -> str:
    """Frozen label selection: COMPLETE iff all integrity gates pass, else BLOCKED.

    No recovery input exists in this runner; 0..3 exact outcomes never
    change the label.
    """
    failing = [name for name in INTEGRITY_GATE_ORDER if not gates.get(name, False)]
    if failing:
        return f"BLOCKED({failing[0]})"
    return COMPLETE_LABEL


def holdout_block_events(n: int, block_index: int, frame_start: int, result) -> list:
    """Canonical public transcript events: L1, L2 (when invoked), final tag."""
    if result.outcome == "resource_abort":
        return []
    k1, k2 = int(result.k1), int(result.k2)
    events: list[dict] = []
    l1_id = f"block-{int(n)}-{int(block_index)}-{ARM}-l1-disclosure"
    events.append(_holdout_event(
        n=n, block_index=block_index, frame_start=frame_start,
        event_id=l1_id, event_type="l1_disclosure", direction="alice_to_bob",
        parent_event_id=None, key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k1,
        public_control_bits=0, payload={},
    ))
    if result.l2_invoked:
        l2_id = f"block-{int(n)}-{int(block_index)}-{ARM}-l2-disclosure"
        events.append(_holdout_event(
            n=n, block_index=block_index, frame_start=frame_start,
            event_id=l2_id, event_type="l2_disclosure", direction="alice_to_bob",
            parent_event_id=l1_id, key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k2,
            public_control_bits=0, payload={},
        ))
        if result.tag_invoked:
            events.append(_holdout_event(
                n=n, block_index=block_index, frame_start=frame_start,
                event_id=f"block-{int(n)}-{int(block_index)}-{ARM}-verification",
                event_type="verification_tag", direction="alice_to_bob",
                parent_event_id=l2_id, key_dependent_bits=TAG_BITS,
                public_control_bits=seed_bits_for(int(n)),
                payload={"seed_bit_length": seed_bits_for(int(n))},
            ))
    return events


def _holdout_event(
    *, n, block_index, frame_start, event_id, event_type, direction,
    parent_event_id, key_dependent_bits, public_control_bits, payload,
) -> dict:
    event = {
        "event_id": event_id,
        "frame_key": (
            f"nbpolar-p18-holdout-microcheck:{int(n)}:{int(frame_start)}:{int(block_index)}"
        ),
        "method": METHOD,
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


def holdout_recount_events(events) -> dict:
    """Independent literal recount; N and arm are read literally from the event id."""
    totals = {"key_dependent_bits": 0, "public_control_bits": 0, "tag_invocations": 0}
    event_types = {"l1_disclosure": 0, "l2_disclosure": 0, "verification_tag": 0}
    for event in events:
        parts = str(event["event_id"]).split("-")
        if len(parts) < 5 or parts[0] != "block" or parts[3] != ARM:
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
class HoldoutMicrocheckRun:
    """In-memory P18 HOLD microcheck run (also returned by the runner)."""

    records: list
    events: list
    construction: dict
    manifest: dict
    plan: dict
    summary: dict


def _stat_record(path) -> dict:
    if path is None:
        return {"path": None, "size_bytes": None, "mtime_ns": None}
    st = Path(path).stat()
    return {"path": str(path), "size_bytes": int(st.st_size), "mtime_ns": int(st.st_mtime_ns)}


def _stub_plan(
    *, out_path, source, floor, n, k1, k2, construction, digest, hold_pairs,
    manifest_path, hold_frames, block_frames, remainder_frames, tag_master,
    chunk_rows, tag_bits, identity, manifest,
) -> dict:
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
        "support_rule": SUPPORT_RULE,
        "block_rule": BLOCK_RULE,
        "nll_rule": NLL_RULE,
        "ratio_rule": RATIO_RULE,
        "truth_boundary": TRUTH_BOUNDARY,
        "operational_rule": OPERATIONAL_RULE,
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
        "k1": int(k1),
        "k2": int(k2),
        "k_total": int(k1) + int(k2),
        "chunk_rows": int(chunk_rows),
        "tag_bits": int(tag_bits),
        "tag_master": int(tag_master),
        "tag_seed_domain": f"{SEED_PREFIX}:<master>:<n>:<block_index>",
        "hold_frame_range": [int(v) for v in hold_frames],
        "hold_frames": FROZEN_HOLD_FRAMES,
        "hold_pairs": FROZEN_HOLD_PAIRS,
        "block_frames": int(block_frames),
        "block_ranges": [list(r) for r in FROZEN_BLOCK_RANGES],
        "block_count": FROZEN_BLOCK_COUNT,
        "remainder_frame_range": [int(v) for v in remainder_frames],
        "remainder_symbols": FROZEN_REMAINDER_SYMBOLS,
        "planned_sc_calls_max": PLANNED_SC_CALLS_MAX,
        "planned_tag_invocations": PLANNED_TAG_INVOCATIONS,
        "full_block_key_dependent_bits": FROZEN_LEAKAGE_BITS,
        "public_control_bits_per_tag": FROZEN_PUBLIC_CONTROL_BITS,
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
        "f_inequality": {
            "leakage_bits": FROZEN_LEAKAGE_BITS,
            "limit_bits": float(FROZEN_TARGET_F * int(n) * h_total),
        },
        "precondition_order": list(opf.PRECONDITION_ORDER),
        "integrity_gate_order": list(INTEGRITY_GATE_ORDER),
        "decision": {
            "complete": COMPLETE_LABEL,
            "blocked": "BLOCKED(<earliest gate>)",
            "recovery_threshold": None,
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
        "# NB-Polar Phase 4-P18 N=32768 1M-HOLD operational microcheck",
        "",
        f"- protocol: `{summary.get('analysis')}` (mode `{summary.get('mode')}`)",
        f"- source/target: `{summary.get('source')}`; q={summary.get('q')}, n={summary.get('n')}, "
        f"K1={summary.get('k1')}, K2={summary.get('k2')}, chunk_rows={summary.get('chunk_rows')}, "
        f"tag_bits={summary.get('tag_bits')}",
        f"- HOLD frames: {summary.get('hold', {}).get('hold_frame_range')}; "
        f"blocks: {summary.get('hold', {}).get('block_ranges')}; "
        f"unused remainder: {summary.get('hold', {}).get('remainder')}",
        f"- wall: {summary.get('wall_s')} s; peak RSS: {summary.get('rss_bytes_peak')} bytes; "
        f"resource stop fired: {summary.get('resource_stop_fired')}",
        "",
        "## Predecessor and split identities (verified before the content opens)",
        "",
        f"- P16 construction digest: `{summary.get('identity', {}).get('digest_recomputed')}` "
        f"(match: {summary.get('identity', {}).get('digest_match')})",
        f"- split manifest: `{summary.get('manifest', {}).get('manifest_path')}` declares "
        f"{summary.get('manifest', {}).get('hold_frames')} HOLD frames / "
        f"{summary.get('manifest', {}).get('hold_pairs')} HOLD pairs (frozen 400/102400)",
        "",
        "## Descriptive per-block scalars (no threshold, no recovery gate)",
        "",
        "| block | frames | outcome | raw SER | total NLL bits | L1 correct | tag | "
        "disclosure CE ratio |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for record in summary.get("blocks", []):
        lines.append(
            f"| {record['block_index']} | {record['frame_start']}..{record['frame_end']} | "
            f"{record['outcome']} | {record['raw_ser']!r} | {record['total_nll_bits']!r} | "
            f"{record['l1_correct']} | {record['tag_pass']} | "
            f"{record.get('disclosure_ce_ratio')} |"
        )
    lines += [
        "",
        f"- total NLL bits: {summary.get('nll', {}).get('total_nll_bits')}",
        f"- key-dependent bits: {summary.get('disclosure', {}).get('key_dependent_bits')} "
        f"(fixed full-block value {FROZEN_LEAKAGE_BITS})",
        f"- public control bits: {summary.get('disclosure', {}).get('public_control_bits')} "
        f"(fixed per-tag value {FROZEN_PUBLIC_CONTROL_BITS})",
        f"- transcript recount mismatches: {summary.get('disclosure', {}).get('mismatches')}",
        f"- sample CE-normalized disclosure ratio: "
        f"{summary.get('disclosure', {}).get('ce_normalized_disclosure_ratio')} "
        "(descriptive only; NOT qualification efficiency)",
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
        "(none; 0..3 exact outcomes are descriptive)",
        "",
        f"**Scope:** {summary.get('claim_scope')}.",
        "",
    ]
    return "\n".join(lines)


def run_holdout_microcheck(
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
) -> HoldoutMicrocheckRun:
    """Execute the frozen P18 HOLD microcheck; write five scalar-only files.

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
    k1 = _check_k1(k1)
    k2 = _check_k2(k2)
    opf._check_chunk_contract(chunk_rows)
    opf._check_tag_bits(tag_bits)
    hold_frames = _check_frame_range(hold_frames, "hold-frames", FROZEN_HOLD_FRAME_RANGE)
    if int(block_frames) != FROZEN_BLOCK_FRAMES:
        raise ValueError(f"frozen point requires block-frames={FROZEN_BLOCK_FRAMES}, got {block_frames}")
    remainder_frames = _check_frame_range(
        remainder_frames, "remainder-frames", FROZEN_REMAINDER_FRAME_RANGE
    )
    tag_master = _check_tag_master(tag_master)

    # Predecessor identity and split manifest are verified before any root
    # exists and before either protected content open; a mismatch consumes
    # nothing. The digest flag must name the frozen P16 digest; the verifier
    # then pins the flag to the file's recomputed digest.
    if str(construction_digest) != FROZEN_CONSTRUCTION_DIGEST:
        raise ValueError("predecessor construction identity: digest flag != frozen digest")
    verified = verify_predecessor_construction(construction, expected_digest=construction_digest)
    identity = verified["record"]
    manifest = verify_split_manifest(manifest_path, source=source)
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
        tag_bits=tag_bits, identity=identity, manifest=manifest,
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
        opf._write_json(out_path / "input_and_construction_identity.json", identity_doc)
        (out_path / "per_block_outcomes.jsonl").write_text("", encoding="utf-8")
        opf._write_json(
            out_path / "aggregate_summary.json",
            {"protocol": PROTOCOL_NAME, "status": "pending_content_open"},
        )
        (out_path / "report.md").write_text(
            "# NB-Polar Phase 4-P18 N=32768 1M-HOLD operational microcheck\n\n"
            "status: pending_content_open\n",
            encoding="utf-8",
        )
        start = time.perf_counter()

        def persist(identity_doc: dict, summary_doc: dict) -> None:
            opf._write_json(out_path / "input_and_construction_identity.json", identity_doc)
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

        def current_gates(*, final: bool) -> tuple:
            gates = _integrity_gates(
                out_path=out_path, n=n, k1=k1, k2=k2, identity=identity,
                manifest=manifest, l1_order=l1_order, l2_order=l2_order,
                formation=formation, records=records, events=events, calls=calls,
                incremental=incremental, accounting=accounting,
                provenance_violations=provenance_violations, start=start,
                cap=budget_cap, resource_stop=resource_stop,
                precondition_passed=bool(precondition_report.passed), final=final,
                npz_stat_before=npz_stat_before, npz_stat_after=npz_stat_after,
                hold_stat_before=hold_stat_before, hold_stat_after=hold_stat_after,
                registered_paths=registered_paths, opened_paths=opened_paths,
            )
            failing = [g for g in INTEGRITY_GATE_ORDER if not gates[g]]
            return gates, failing

        def partial_summary(outcome_label: str, gates: dict) -> dict:
            outcome_counts = {name: 0 for name in OUTCOMES}
            for record in records:
                if record.get("outcome") in outcome_counts:
                    outcome_counts[record["outcome"]] += 1
            total_nll = float(sum(
                record["total_nll_bits"] for record in records
                if record["total_nll_bits"] is not None
            ))
            l1_nll = float(sum(
                record["l1_nll_bits"] for record in records
                if record["l1_nll_bits"] is not None
            ))
            l2_nll = float(sum(
                record["l2_nll_bits"] for record in records
                if record["l2_nll_bits"] is not None
            ))
            try:
                recount = holdout_recount_events(events)
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
                "k_total": int(k1) + int(k2),
                "target_f": float(FROZEN_TARGET_F),
                "chunk_rows": int(chunk_rows),
                "tag_bits": int(tag_bits),
                "tag_master": int(tag_master),
                "identity": dict(identity),
                "manifest": dict(manifest),
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
                "blocks": [
                    {
                        "block_index": record["block_index"],
                        "frame_start": record["frame_start"],
                        "frame_end": record["frame_end"],
                        "outcome": record["outcome"],
                        "raw_ser": record["raw_ser"],
                        "total_nll_bits": record["total_nll_bits"],
                        "l1_correct": record["l1_correct"],
                        "tag_pass": record["tag_pass"],
                        "disclosure_ce_ratio": record["disclosure_ce_ratio"],
                    }
                    for record in records
                ],
                "outcome_counts": {name: int(outcome_counts[name]) for name in OUTCOMES},
                "exact_count": int(outcome_counts["exact"]),
                "block_count": int(len(records)),
                "nll": {
                    "l1_nll_bits": l1_nll,
                    "l2_nll_bits": l2_nll,
                    "total_nll_bits": total_nll,
                },
                "sc_calls": int(calls["sc"]),
                "planned_sc_calls_max": int(PLANNED_SC_CALLS_MAX),
                "tag_invocations": int(incremental["tag_invocations"]),
                "planned_tag_invocations": int(PLANNED_TAG_INVOCATIONS),
                "provenance_violations": int(provenance_violations),
                "disclosure": {
                    "full_block_key_dependent_bits": FROZEN_LEAKAGE_BITS,
                    "public_control_bits_per_tag": FROZEN_PUBLIC_CONTROL_BITS,
                    "key_dependent_bits": int(incremental["key_dependent_bits"]),
                    "public_control_bits": int(incremental["public_control_bits"]),
                    "tag_invocations": int(incremental["tag_invocations"]),
                    "recount": recount,
                    "mismatches": mismatches,
                    "ce_normalized_disclosure_ratio": (
                        float(
                            FROZEN_LEAKAGE_BITS * sum(
                                1 for record in records
                                if record.get("total_nll_bits") is not None
                            ) / total_nll
                        )
                        if total_nll > 0 else None
                    ),
                    "ratio_note": "descriptive sample CE-normalized ratio, NOT qualification efficiency",
                },
                "decision": {
                    "complete": COMPLETE_LABEL,
                    "blocked": "BLOCKED(<earliest gate>)",
                    "recovery_threshold": None,
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

        # ---- three registered blocks; checkpoint after every block.
        for block in formation["blocks"]:
            index = int(block["block_index"])
            frame_start = int(block["frame_start"])
            frame_end = int(block["frame_end"])
            reason = opf._budget_exceeded(start, budget_cap)
            if reason is not None:
                resource_stop = reason
                for rest in formation["blocks"][index:]:
                    abort = opf._abort_block(
                        int(rest["frame_start"]), int(rest["block_index"]), k1=k1, k2=k2
                    )
                    record = _holdout_record(
                        abort, frame_start=int(rest["frame_start"]),
                        frame_end=int(rest["frame_end"]), raw_ser=None,
                        nll=None, l1_correct=False,
                        resources=opf._cell_resource_record(0.0),
                    )
                    records.append(record)
                    opf._append_jsonl(out_path / "per_block_outcomes.jsonl", record)
                    gates_now, _ = current_gates(final=False)
                    persist(identity_doc, partial_summary(
                        f"RUNNING(block {len(records)}/3)", gates_now
                    ))
                break
            nll = holdout_nll_bits(block["bob"], block["high"], block["low"], p1, p2)
            ser = raw_symbol_error_rate(block["labels"], block["bob"])
            block_start = time.perf_counter()
            result = None
            error = None
            try:
                result = _execute_block(
                    n=n, block_index=index, frame_start=frame_start,
                    bob=block["bob"], high=block["high"], low=block["low"],
                    labels=block["labels"], field=field, p1_table=p1, p2_table=p2,
                    l1_order=l1_order, l2_order=l2_order, k1=k1, k2=k2,
                    tag_master=tag_master, calls=calls,
                )
            except MemoryError:
                raise
            except Exception as exc:  # block failure: recorded, gate fails
                error = type(exc).__name__
                result = opf.OperationalBlockResult(
                    stream_seed=int(frame_start),
                    block_index=index,
                    outcome="decode_failed",
                    exact=False,
                    label_match=False,
                    tag_pass=False,
                    l1_provenance=None,
                    l2_provenance=None,
                    l1_executed=False,
                    l1_decode_failed=True,
                    l2_invoked=False,
                    l2_skipped_by_l1_failure=True,
                    l2_decode_failed=False,
                    tag_invoked=False,
                    key_dependent_bits=0,
                    public_control_bits=0,
                    nonfinite=False,
                    truth_leak_violation=False,
                    l1_error_type=None,
                    l2_error_type=None,
                    wall_s=time.perf_counter() - block_start,
                    k1=k1,
                    k2=k2,
                )
            if result.truth_leak_violation:
                provenance_violations += 1
            resources = opf._cell_resource_record(time.perf_counter() - block_start)
            l1_correct = bool(
                result.l1_executed
                and result.high_hat is not None
                and np.array_equal(result.high_hat, block["high"])
            )
            record = _holdout_record(
                result, frame_start=frame_start, frame_end=frame_end,
                raw_ser=ser, nll=nll, l1_correct=l1_correct, resources=resources,
                error=error,
            )
            records.append(record)
            opf._append_jsonl(out_path / "per_block_outcomes.jsonl", record)
            if error is None:
                for event in holdout_block_events(n, index, frame_start, result):
                    events.append(event)
                    incremental["key_dependent_bits"] += int(event["key_dependent_bits"])
                    incremental["public_control_bits"] += int(event["public_control_bits"])
                    if str(event["event_type"]) == "verification_tag":
                        incremental["tag_invocations"] += 1
            gates_now, _ = current_gates(final=False)
            persist(identity_doc, partial_summary(
                f"RUNNING(block {len(records)}/3)", gates_now
            ))

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
        gates, _ = current_gates(final=True)
        outcome = hold_microcheck_label(gates)
        summary = partial_summary(outcome, gates)
        summary["wall_s"] = round(float(wall_s), 6)
        summary["rss_bytes_peak"] = rss_peak
        summary["input_stats_after"] = {
            "counts_npz": dict(npz_stat_after),
            "hold_pairs_parquet": dict(hold_stat_after),
        }
        summary["attempt_read_accounting"] = dict(
            accounting, opened_content_paths=list(opened_paths)
        )
        persist(identity_doc, summary)
        return HoldoutMicrocheckRun(
            records=records,
            events=events,
            construction={
                "protocol": PROTOCOL_NAME,
                "predecessor_verified_before_first_block": True,
                "identity": dict(identity),
            },
            manifest=manifest,
            plan=plan,
            summary=summary,
        )
    except HoldoutMicrocheckContractError as exc:
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
        raise HoldoutMicrocheckResourceError(f"{label}: MemoryError: {exc}") from exc


def _execute_block(
    *, n, block_index, frame_start, bob, high, low, labels, field, p1_table,
    p2_table, l1_order, l2_order, k1, k2, tag_master, calls,
):
    """One registered HOLD block through the accepted operational helper."""
    u1 = polar_transform(high, field=field, alpha=ALPHA)
    u2 = polar_transform(low, field=field, alpha=ALPHA)
    labels_true = np.asarray(labels, dtype=np.int64)
    labels_true_bits = labels_to_bits(labels_true)
    seed = holdout_seed_bits(tag_master, n, block_index, bit_length=seed_bits_for(n))

    def _tag_fn(bits, _seed, tag_bits, _fixed=seed):
        return toeplitz_tag(bits, _fixed, tag_bits)

    return run_operational_block(
        n=n,
        stream_seed=int(frame_start),
        block_index=int(block_index),
        bob=bob,
        high_true=high,
        low_true=low,
        u1_true=u1,
        u2_true=u2,
        labels_true=labels_true,
        labels_true_bits=labels_true_bits,
        field=field,
        p1_table=p1_table,
        p2_table=p2_table,
        l1_order=l1_order,
        l2_order=l2_order,
        k1=k1,
        k2=k2,
        master=tag_master,
        tag_fn=_tag_fn,
        calls=calls,
    )


def _holdout_record(
    result, *, frame_start, frame_end, raw_ser, nll, l1_correct, resources, error=None,
) -> dict:
    """Scalar-only P18 record: frame range plus descriptive block scalars."""
    record = opf._block_record(result, resources=resources, error=error)
    record.pop("stream_seed", None)
    record["frame_start"] = int(frame_start)
    record["frame_end"] = int(frame_end)
    record["frame_count"] = FROZEN_BLOCK_FRAMES
    record["raw_ser"] = raw_ser
    if nll is None:
        record["l1_nll_bits"] = None
        record["l2_nll_bits"] = None
        record["total_nll_bits"] = None
        record["total_nll_bits_per_pair"] = None
    else:
        record["l1_nll_bits"] = float(nll["l1_nll_bits"])
        record["l2_nll_bits"] = float(nll["l2_nll_bits"])
        record["total_nll_bits"] = float(nll["total_nll_bits"])
        record["total_nll_bits_per_pair"] = float(nll["total_nll_bits_per_pair"])
    record["l1_correct"] = bool(l1_correct)
    record["full_block_key_dependent_bits"] = FROZEN_LEAKAGE_BITS
    record["public_control_bits_per_tag"] = FROZEN_PUBLIC_CONTROL_BITS
    if record["total_nll_bits"] in (None, 0.0):
        record["disclosure_ce_ratio"] = None
    else:
        record["disclosure_ce_ratio"] = float(
            FROZEN_LEAKAGE_BITS / record["total_nll_bits"]
        )
    return record


def _finalize_blocked(out_path, identity_doc, accounting, opened_paths, message: str) -> None:
    """Best-effort BLOCKED stubs after a post-open failure; never a fresh root."""
    try:
        label = str(message).split(":", 1)[0]
        identity_doc["attempt_read_accounting"] = dict(
            accounting, opened_content_paths=list(opened_paths),
            attempt_read_accounting_finalized=True,
        )
        opf._write_json(out_path / "input_and_construction_identity.json", identity_doc)
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
            "# NB-Polar Phase 4-P18 N=32768 1M-HOLD operational microcheck\n\n"
            f"outcome label: `{label}`\n\n{message}\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def _integrity_gates(
    *,
    out_path, n, k1, k2, identity, manifest, l1_order, l2_order, formation,
    records, events, calls, incremental, accounting, provenance_violations,
    start, cap, resource_stop, precondition_passed, final,
    npz_stat_before, npz_stat_after, hold_stat_before, hold_stat_after,
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
        and int(manifest.get("hold_frames", -1)) == FROZEN_HOLD_FRAMES
        and int(manifest.get("hold_pairs", -1)) == FROZEN_HOLD_PAIRS
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
        population_ok = bool(
            population_ok and len(formation["blocks"]) == FROZEN_BLOCK_COUNT
        )
    blocks_ok = bool(
        [tuple(r) for r in formation["block_ranges"]] == [tuple(r) for r in FROZEN_BLOCK_RANGES]
        and formation["remainder"]["used"] is False
        and int(formation["remainder"]["frames"]) == FROZEN_REMAINDER_FRAMES
        and int(formation["remainder"]["symbols"]) == FROZEN_REMAINDER_SYMBOLS
        and list(formation["hold_frame_range"]) == list(FROZEN_HOLD_FRAME_RANGE)
    )
    if final:
        ranges = [(record["frame_start"], record["frame_end"]) for record in records]
        blocks_ok = bool(
            blocks_ok
            and len(records) == FROZEN_BLOCK_COUNT
            and ranges == [tuple(r) for r in FROZEN_BLOCK_RANGES]
        )

    h_total = float(opf.EXPECTED_H1 + opf.EXPECTED_H2)
    leakage = DISCLOSED_BITS_PER_COORDINATE * (k1 + k2) + TAG_BITS
    replay_ok = bool(
        int(k1) == FROZEN_K1
        and int(k2) == FROZEN_K2
        and int(k1) + int(k2) == FROZEN_K_TOTAL
        and int(leakage) == FROZEN_LEAKAGE_BITS
        and leakage <= FROZEN_TARGET_F * n * h_total
    )
    orders_ok = bool(
        opf._order_is_permutation(l1_order, n) and opf._order_is_permutation(l2_order, n)
    )

    buckets_ok = True
    for record in records:
        if record.get("outcome") not in OUTCOMES:
            buckets_ok = False
            break
        if record.get("error") is not None:
            buckets_ok = False
            break
        if not opf._record_dict_consistent(record, n=n, k1=k1, k2=k2):
            buckets_ok = False
            break
    if final and len(records) != FROZEN_BLOCK_COUNT:
        buckets_ok = False

    error_free = all(record.get("error") is None for record in records)
    expected_sc = sum(
        (1 + int(record.get("l2_invoked", 0)))
        for record in records
        if record.get("error") is None and record.get("outcome") != "resource_abort"
    )
    sc_ok = bool(
        set(calls) == {"sc"}
        and error_free
        and int(calls.get("sc", -1)) == int(expected_sc)
        and int(expected_sc) <= PLANNED_SC_CALLS_MAX
    )
    tags_ok = bool(
        int(incremental["tag_invocations"])
        == sum(1 for record in records if record.get("tag_invoked"))
        and int(incremental["tag_invocations"]) <= PLANNED_TAG_INVOCATIONS
    )

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
            with open(out_path / "per_block_outcomes.jsonl", "r", encoding="utf-8") as handle:
                if sum(1 for _ in handle) != len(records):
                    files_ok = False
    except OSError:
        files_ok = False

    try:
        recount = holdout_recount_events(events)
        mismatches = opf._transcript_mismatches(incremental, recount)
        recount_ok = not mismatches
    except ValueError:
        recount_ok = False
    disclosure_ok = bool(recount_ok and files_ok)
    if disclosure_ok:
        for record in records:
            if record.get("error") is not None or record.get("outcome") == "resource_abort":
                continue
            expected_kdb = (
                DISCLOSED_BITS_PER_COORDINATE * k1
                + (DISCLOSED_BITS_PER_COORDINATE * k2 if record.get("l2_invoked") else 0)
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
    access_ok = bool(
        set(calls) == {"sc"} and list(opened_paths) == list(registered_paths)
    )

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
        "target_population_contract": bool(precondition_passed),
        "hold_population_exact": bool(population_ok),
        "blocks_exact_with_declared_remainder": bool(blocks_ok),
        "orders_valid_k_replay_f_within_budget": bool(orders_ok and replay_ok and identity_ok),
        "sc_calls_exact": bool(sc_ok),
        "tags_exact": bool(tags_ok),
        "buckets_disjoint_exhaustive": bool(buckets_ok),
        "truth_isolation": bool(truth_ok),
        "undetected_zero": bool(undetected_ok),
        "nonfinite_zero": bool(nonfinite_ok),
        "disclosure_recount_exact": bool(disclosure_ok),
        "one_open_per_protected_input": bool(one_open_ok),
        "input_stat_unchanged": bool(stat_ok),
        "no_unregistered_access": bool(access_ok),
        "resource_limits_met_and_no_abort": bool(resource_ok),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nbpolar-p18-holdout-microcheck",
        description=(
            "NB-Polar Phase 4-P18 N=32768 1M HOLD operational microcheck "
            "(frozen V25 counts, P16 construction, three registered HOLD blocks)"
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
        run = run_holdout_microcheck(
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
        print(f"nbpolar phase4-p18 holdout microcheck refused: {exc}", file=sys.stderr)
        return 2
    summary = run.summary
    print(
        json.dumps(
            {
                "analysis": summary["analysis"],
                "block_count": summary["block_count"],
                "outcome_counts": summary["outcome_counts"],
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
