"""CRC-16-aided two-layer joint SCL decoding (new module; frozen files untouched).

Authorization and frozen values: PI ruling 2026-09-27, recorded verbatim in
``docs/decision-log.md`` ("PI 裁决三项：SCL 锁修订 T1 = DECIDED...") and mirrored
in ``openspec/changes/nbpolar-scl-lock-amendment/tasks.md`` T1/T2. This module
implements exactly that ruling's "M=4 implementation constraint" and does not
modify ``scl.py``, ``sc.py``, ``two_layer.py`` or ``prior.py`` -- it only
imports their public functions/objects by module-attribute reference.

Joint decode contract (frozen by the ruling)
---------------------------------------------
1. Run ``scl.scl_decode`` for layer 1 (L1, the high symbol) with the caller's
   ``list_width_L``. Its ranked candidates are already best-first by path
   metric ``m1 = log P(u1 | y, L1-disclosure)`` (natural log, ``scl.py``
   convention).
2. Take the top ``top_m`` L1 candidates (``top_m`` defaults to the frozen
   ``M=4``; fewer are taken verbatim if L1 produced fewer survivors).
3. For each of those L1 candidates, gather a fresh CANDIDATE_CONDITIONED L2
   metric via ``prior.gather_p2_metrics`` on that candidate's hard high
   estimate (``two_layer``-style, no state/APP carried from L1) and run a
   fresh ``scl.scl_decode`` for layer 2 (L2, the low symbol) with the same
   ``list_width_L``. Its candidates are ranked by
   ``m2 = log P(u2 | u1_candidate, y, L2-disclosure)``.
4. Merge every ``(u1, u2)`` pair produced across all expanded L1 candidates.
   Rank by ``m1 + m2`` descending; ties break by (L1 rank, L2 rank) in the
   order the two SCL calls already produced them -- both already
   canonically tie-broken by ``scl.py`` (larger metric first, then smallest
   symbol index, then smallest path index), so this composite order is
   itself deterministic.
5. Walk that merged order and return the first candidate whose packed Alice
   label string (``s = low + 32*high`` per position, ``two_layer.py``'s
   ``labels_to_bits`` MSB-first-per-symbol convention, reused unmodified)
   satisfies CRC-16 against the caller-supplied disclosed ``crc_true``. If no
   candidate passes, return the top joint-metric candidate with
   ``crc_failed=True`` (report-only flag; never silently promoted to a pass).
6. CRC bits: exactly 16, counted once in ``crc_bits`` regardless of pass/fail
   (the CRC value is a single 16-bit disclosure sent once per block; the
   Toeplitz tag stays a wholly separate downstream disclosure and is applied
   by the caller's existing verify flow, unmodified here).

At ``list_width_L=1`` there is exactly one L1 candidate and one L2 candidate
(``top_m`` is irrelevant), so the returned ``(high, low)`` estimate is
bit-identical to ``sc_decode``/``scl_decode(L=1)`` on the same inputs; the
CRC pass/fail flag is descriptive only and never changes which candidate is
returned when there is only one.

No data loading, no benchmark/output machinery, no I/O, no real data. This
module is a decoder-only extension; disclosure accounting beyond the 16 CRC
bits (L1/L2 disclosure, Toeplitz tag) stays the caller's responsibility,
exactly as it is for ``two_layer.run_two_layer_block``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import scl as scl_mod
from . import two_layer as two_layer_mod
from .prior import Provenance, gather_p2_metrics, probs_to_symbol_metric

CRC_BITS = 16
CRC_POLY = 0x1021
CRC_INIT = 0xFFFF
LABEL_SCALE = two_layer_mod.LABEL_SCALE  # 32; s = low + 32*high, unchanged import
TOP_M_DEFAULT = 4  # PI ruling 2026-09-27, D4/M=4 implementation constraint

__all__ = [
    "CRC_BITS",
    "CRC_POLY",
    "CRC_INIT",
    "TOP_M_DEFAULT",
    "top_l_prune",
    "crc16_ccitt_false_bits",
    "labels_crc16",
    "JointCandidate",
    "SCLJointResult",
    "scl_joint_decode",
]


def top_l_prune(path_metrics, position, is_spike, width_L):
    """Frozen standard top-L prune rule: keep the largest-metric ``width_L`` paths.

    Stable sort so equal metrics keep the canonical ``scl.scl_decode`` order
    (candidates already arrive at ``prune_rule`` pre-sorted best-first by
    ``(metric desc, symbol asc, path asc)``); this function never reorders
    within a metric tie, it only truncates. Mechanism is frozen: no knob.
    """
    metrics = np.asarray(path_metrics, dtype=np.float64)
    order = np.argsort(-metrics, kind="stable")
    width = int(width_L)
    return order[:width].astype(np.int64)


top_l_prune.__name__ = "top_l_prune"


def crc16_ccitt_false_bits(bits) -> int:
    """CRC-16/CCITT-FALSE over a bit-serial input (poly 0x1021, init 0xFFFF).

    ``bits`` is a 1D array of 0/1 values (MSB-first bit order, the caller's
    convention -- e.g. ``two_layer.labels_to_bits`` output). No reflection,
    no final XOR. Known check value: ``crc16_ccitt_false_bits`` of the ASCII
    bytes of ``"123456789"`` fed 8 bits at a time, MSB first, equals
    ``0x29B1`` (the published CRC-16/CCITT-FALSE check value).
    """
    arr = np.asarray(bits)
    if arr.ndim != 1:
        raise ValueError(f"CRC contract: bits must be one-dimensional, got shape {arr.shape}")
    crc = CRC_INIT
    for value in arr.tolist():
        bit = int(value) & 1
        msb = (crc >> 15) & 1
        crc = (crc << 1) & 0xFFFF
        if msb ^ bit:
            crc ^= CRC_POLY
    return crc


def labels_crc16(labels) -> int:
    """CRC-16 over Alice's packed label string (``s = low + 32*high`` per position).

    Reuses ``two_layer.labels_to_bits`` (10-bit MSB-first per symbol,
    unmodified import) so the bit order matches the project's existing
    packing convention exactly; this function adds nothing but the CRC.
    """
    bits = two_layer_mod.labels_to_bits(labels)
    return crc16_ccitt_false_bits(bits)


@dataclass(frozen=True, eq=False)
class JointCandidate:
    """One merged (L1, L2) candidate from the joint list, pre-CRC-check."""

    high: np.ndarray  # int64[N] L1 hard symbol candidate (x_candidates row)
    low: np.ndarray  # int64[N] L2 hard symbol candidate (x_candidates row)
    m1: float  # L1 path metric (natural log)
    m2: float  # L2 path metric conditioned on this L1 candidate
    joint_metric: float  # m1 + m2
    l1_rank: int  # 0-based rank within the top_m expanded L1 candidates
    l2_rank: int  # 0-based rank within that L1 candidate's L2 list


@dataclass(frozen=True, eq=False)
class SCLJointResult:
    """CRC-aided joint two-layer SCL decode output."""

    high_hat: np.ndarray  # int64[N] chosen high-layer estimate
    low_hat: np.ndarray  # int64[N] chosen low-layer estimate
    label_hat: np.ndarray  # int64[N] = low_hat + 32*high_hat
    m1: float
    m2: float
    joint_metric: float
    crc_true: int
    crc_hat: int
    crc_pass: bool
    crc_failed: bool  # True iff no candidate in the merged list passed CRC
    crc_bits: int  # always CRC_BITS (16); counted once regardless of pass/fail
    l1_survivor_count: int
    top_m_requested: int
    top_m_used: int  # min(top_m_requested, l1_survivor_count)
    candidates_considered: int  # total merged (u1,u2) pairs ranked
    requested_width: int  # list_width_L, mirrored from both scl_decode calls
    ranked_candidates: tuple  # tuple[JointCandidate, ...], best joint_metric first
    metric_provenance: dict


def scl_joint_decode(
    bob,
    crc_true: int,
    *,
    field,
    alpha: int = 2,
    p1_table,
    p2_table,
    d1_positions=None,
    d1_values=None,
    d2_positions=None,
    d2_values=None,
    list_width_L: int,
    top_m: int = TOP_M_DEFAULT,
) -> SCLJointResult:
    """CRC-16-aided joint two-layer SCL decode (module docstring has the contract).

    ``bob``/``p1_table``/``p2_table`` mirror ``two_layer.run_two_layer_block``'s
    Bob-only inputs (``build_p1_metrics``/``gather_p2_metrics`` do the actual
    gathering; this function never sees Alice truth). ``crc_true`` is the
    16-bit CRC Alice discloses (``labels_crc16`` of her true label string);
    the caller computes it, this function only checks candidates against it.
    ``d1_positions``/``d1_values`` and ``d2_positions``/``d2_values`` are the
    frozen L1/L2 disclosure coordinate/value pairs, contract-identical to
    ``sc_decode``'s ``known_positions``/``known_values``.
    """
    if isinstance(top_m, bool) or int(top_m) <= 0:
        raise ValueError(f"field/shape contract: top_m must be a positive integer, got {top_m!r}")
    top_m = int(top_m)

    bob_row = np.asarray(bob)[None, :]
    p1_probs = two_layer_mod.build_p1_metrics(bob_row, p1_table)[0]
    p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)

    l1_res = scl_mod.scl_decode(
        p1_metric.logp,
        field=field,
        alpha=alpha,
        known_positions=d1_positions,
        known_values=d1_values,
        list_width_L=list_width_L,
        prune_rule=top_l_prune,
    )

    top_m_used = min(top_m, l1_res.survivor_count)
    merged: list[JointCandidate] = []
    for l1_rank in range(top_m_used):
        high_cand = l1_res.x_candidates[l1_rank]
        m1 = float(l1_res.path_metrics[l1_rank])
        p2_probs = gather_p2_metrics(bob_row, high_cand[None, :], p2_table)[0]
        p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
        l2_res = scl_mod.scl_decode(
            p2_metric.logp,
            field=field,
            alpha=alpha,
            known_positions=d2_positions,
            known_values=d2_values,
            list_width_L=list_width_L,
            prune_rule=top_l_prune,
        )
        for l2_rank in range(l2_res.survivor_count):
            low_cand = l2_res.x_candidates[l2_rank]
            m2 = float(l2_res.path_metrics[l2_rank])
            merged.append(
                JointCandidate(
                    high=high_cand,
                    low=low_cand,
                    m1=m1,
                    m2=m2,
                    joint_metric=m1 + m2,
                    l1_rank=l1_rank,
                    l2_rank=l2_rank,
                )
            )

    # Canonical merge order: joint metric desc, then (l1_rank, l2_rank) asc --
    # both already canonically tie-broken inside their own scl_decode call.
    order = sorted(range(len(merged)), key=lambda k: (-merged[k].joint_metric, merged[k].l1_rank, merged[k].l2_rank))
    ranked = tuple(merged[k] for k in order)

    crc_true_int = int(crc_true)
    chosen = None
    crc_hat_chosen = None
    for cand in ranked:
        label = (cand.low + LABEL_SCALE * cand.high).astype(np.int64)
        crc_hat = labels_crc16(label)
        if crc_hat == crc_true_int:
            chosen = cand
            crc_hat_chosen = crc_hat
            break
    crc_failed = chosen is None
    if chosen is None:
        chosen = ranked[0]
        crc_hat_chosen = labels_crc16((chosen.low + LABEL_SCALE * chosen.high).astype(np.int64))

    label_hat = (chosen.low + LABEL_SCALE * chosen.high).astype(np.int64)
    provenance = {
        "l1_provenance": p1_metric.provenance.value,
        "l2_provenance": Provenance.CANDIDATE_CONDITIONED.value,
        "merge_rule": "joint_metric desc, tie-break (l1_rank, l2_rank) asc",
        "prune_rule": "top_l_prune",
        "crc": "CRC-16/CCITT-FALSE, poly=0x1021, init=0xFFFF, MSB-first, no reflect, no xorout",
        "label_convention": "s = low + 32*high per position (two_layer.py LABEL_SCALE=32)",
        "top_m_requested": top_m,
        "top_m_default": TOP_M_DEFAULT,
    }
    return SCLJointResult(
        high_hat=chosen.high,
        low_hat=chosen.low,
        label_hat=label_hat,
        m1=chosen.m1,
        m2=chosen.m2,
        joint_metric=chosen.joint_metric,
        crc_true=crc_true_int,
        crc_hat=int(crc_hat_chosen),
        crc_pass=bool(not crc_failed),
        crc_failed=bool(crc_failed),
        crc_bits=CRC_BITS,
        l1_survivor_count=l1_res.survivor_count,
        top_m_requested=top_m,
        top_m_used=top_m_used,
        candidates_considered=len(ranked),
        requested_width=int(list_width_L),
        ranked_candidates=ranked,
        metric_provenance=provenance,
    )
