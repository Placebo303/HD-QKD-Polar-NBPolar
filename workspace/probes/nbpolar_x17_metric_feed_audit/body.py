#!/usr/bin/env python3
"""NBPOLAR-X17-METRIC-FEED-AUDIT - Tier-X probe body (frozen).

Audits the X16 SC-path disease (informative tables G2 0.999 / argmax-L1 0.944,
chance-level SC path with undisclosed mismatch 0.96838 ~= chance 0.96875).

Prime suspect H-a (probe-side U/X truth confusion, X16 body.py:420-421,
448-449, 465): X16 unpacked X-domain high/low from sample_full_block misnamed
as u1_true/u2_true, forced X values into U coordinates as known_values, and
scored u_hat (U-domain) against X-domain truth. Production two_layer.py
(629-634) transforms correctly and is untouched.

Design (TASK_PACKET.md sections 2/3, frozen):
  Small-N N=256 (X15 0.75-diagonal recipe verbatim) x 4 blocks, seeds
  2026092391..2394; P positive control (0.999-pin recipe) x 4 blocks, seeds
  2026092395..2398; C full-scale confirmation N=32768 (X16 recipe, corrected
  truth-side) x 1 block, seed 2026092399.
  Arms per small-N block (frozen greedy sc_decode L=1 only):
    A0 baseline replay: X16 verbatim (X-domain known_values + score vs the
       fed X array; disclosed match trivially by forcing = void check).
    A1 rescore-only: same decode as A0, additionally scored u_hat vs U-truth
       (= polar_transform(low)) and x_hat vs low. No new decode.
    A2 corrected feed: known_values = U-truth[:K2] (U-domain), scored vs
       U-truth. Metric conditioning (D1: first-K1 high + argmax-p1) is kept
       X16-verbatim: the p2 first axis is the X-domain high component, so
       conditioning on high was never the confused half.
    A3 oracle-u1: A2 + true-high conditioning everywhere (vs D1 argmax).
    A4 controls: (i) shuffled known order => u_hat bit-identical assert;
       (ii) bit-reversed metric rows => return to chance (natural order live);
       (iii) random-K disclosed set vs first-K set (iid equivalence).
    A5 controls: uniform-metric (=> chance) and sign-flipped-logp (at/above
       chance) sanity.
    P positive control (REQUIRED): near-noiseless channel, corrected feed +
       scoring. Preregistered EXPECTED band [0.00, 0.05] is a descriptive
       prediction, never a gate/verdict.
    P2 wiring assert: all-known decode returns truth exactly (selftest).
    C confirmation: N=32768, corrected truth-side A2-feed + A3-feed (2 SC).

Decoder-free Q1/Q1b machinery (hazard atom, spikes, ranks, F-median8) is kept
X16-verbatim over the X-domain label components the p1/p2 rows are
distributions over; G2 (Q1b-nonspike-L8 >= 0.50) and G3 (spike fraction in
[0.02, 0.70]) are retained as structural wiring checks. X16-G1 is RETIRED
(mismatch is now the measured audit variable; gating on it would prejudge
the audit) and recorded as retired, never evaluated.

Synthetic-only. Stdlib + numpy only. Read-only reuse of the accepted nbpolar
modules (empirical_channel sampling, prior derive/convert, algebra field,
transform truth-side mapping + re-encode check, sc oracle). No list decoder.
No accepted-module edits. No in-probe fix of any production code. No
protected artifact is stat'ed, opened, or imported. Only file written:
results.json (this directory). Self-tests run under --selftest.
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import numpy as np

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    algebra,
    empirical_channel,
    prior,
    sc,
    transform,
)

_REFUSED_MODULE_FRAGMENTS = (
    "pairs_loader",
    "toeplitz",
    "v25",
    "counts_ab",
    "raw_prior",
    "per_block_arm",
    "alt_l2_tables",
    "l2_alt_hold",
    "l2_alt_maintain",
    "l2_mechanism_probe",
)
for _mod_name in sys.modules:
    for _frag in _REFUSED_MODULE_FRAGMENTS:
        assert _frag not in _mod_name, (
            "X17_STOP_PROTECTED_PATH: refused module loaded: %s" % _mod_name
        )

# --- frozen constants (prereg line 2 verbatim values) ---
PROBE_ID = "NBPOLAR-X17-METRIC-FEED-AUDIT"
TIER = "X"
STATUS_OK = "X17_PROBE_COMPLETE_DESCRIPTIVE_ONLY"
N_SMALL = 256
N_CONFIRM = 32768
Q = 32
ALPHA = 2
CHUNK_ROWS = 512
FLOOR = 1e-15
N_B = 1024
S_RARE = 96
RARE_STEP = 37
K1_SMALL = 3  # floor(334/32768*256) = 2 -> 3 (min-1 rule per prereg)
K2_SMALL = 53  # floor(6746/32768*256) = 52.7 -> 53
K1_CONFIRM = 334
K2_CONFIRM = 6746
SEEDS_ARMS = (2026092391, 2026092392, 2026092393, 2026092394)
SEEDS_POSITIVE = (2026092395, 2026092396, 2026092397, 2026092398)
SEEDS_CONFIRM = (2026092399,)
BLOCKS_PER_SEED = 1
R_MEDIAN = 8
SPIKE_MARGIN = 2.0
BINS = ("[2,4)", "[4,8)", "[8,inf)", "nonsplike_ref")
SPIKE_BINS = ("[2,4)", "[4,8)", "[8,inf)")
LS = (4, 8)
G2_MIN = 0.50
G3_LO, G3_HI = 0.02, 0.70
# A-recipe: X15 0.75-diagonal verbatim. P-recipe: 0.999 pin, neighbors share
# 0.0009, rest 0.0001; shape otherwise X15-verbatim (rare96 pre-floor 0).
RECIPE_A = {"name": "X15-diagonal", "diag": 0.75, "neigh_share": 0.225,
            "rest_share": 0.025}
RECIPE_P = {"name": "near-noiseless-pin", "diag": 0.999, "neigh_share": 0.0009,
            "rest_share": 0.0001}
PREDICT_A0_CHANCE = 31.0 / 32.0  # 0.96875 undisclosed-region chance level
PREDICT_A2_BAND = [0.05, 0.45]  # descriptive only, never gated
PREDICT_P_BAND = [0.00, 0.05]  # descriptive only, never gated
COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && "
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "
    "MALLOC_ARENA_MAX=2 && timeout 600 "
    "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python "
    "workspace/probes/nbpolar_x17_metric_feed_audit/body.py"
)
T0 = time.time()


class _Stop(Exception):
    def __init__(self, status, detail):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _own_path(rel):
    ap = os.path.normpath(os.path.join(HERE, rel))
    if ap != HERE and not ap.startswith(HERE + os.sep):
        raise _Stop("X17_STOP_PROTECTED_PATH", "path escapes probe root: %r" % rel)
    return ap


def _open_own(rel, mode):
    return open(_own_path(rel), mode, encoding="utf-8")


def _sha_file(rel):
    digest = hashlib.sha256()
    with open(_own_path(rel), "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_prereg():
    try:
        with _open_own("prereg.md", "r") as handle:
            text = handle.read()
    except OSError as exc:
        raise _Stop("X17_STOP_PREREG_MISMATCH", "prereg.md unreadable: %s" % exc)
    for token in (
        "nbpolar_x17_metric_feed_audit",
        "2026092391..2398",
        "2026092399",
        "K1=3",
        "K2=53",
        "N=256",
        "N=32768",
        "timeout 600",
    ):
        if token not in text:
            raise _Stop(
                "X17_STOP_PREREG_MISMATCH", "prereg.md missing frozen token: %s" % token
            )
    return text


def _finish(payload):
    with _open_own("results.json", "w") as handle:
        json.dump(payload, handle, indent=1)
        handle.write("\n")
    return os.stat(_own_path("results.json")).st_size


def _rss_bytes():
    try:
        import resource

        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    except Exception:
        return 0


# --- frozen channel recipes (X15 section 4 shape verbatim, masses per recipe) ---
def _rare_symbols(b):
    return [(b + RARE_STEP * k) % N_B for k in range(1, S_RARE + 1)]


def _neighbor_symbols(b):
    return [(b + k) % N_B for k in range(1, 9)]


def _column_masses(b, recipe):
    rare = _rare_symbols(b)
    neigh = _neighbor_symbols(b)
    if len(set(rare)) != S_RARE:
        raise _Stop("X17_STOP_NONFINITE", "rare-symbol collision in column %d" % b)
    diag = int(b)
    if diag in rare or diag in neigh:
        raise _Stop(
            "X17_STOP_NONFINITE", "diagonal/rare/neighbor overlap in column %d" % b
        )
    if set(rare) & set(neigh):
        raise _Stop("X17_STOP_NONFINITE", "rare/neighbor overlap in column %d" % b)
    col = np.empty(N_B, dtype=np.float64)
    taken = np.zeros(N_B, dtype=bool)
    taken[diag] = True
    taken[np.asarray(neigh, dtype=np.int64)] = True
    taken[np.asarray(rare, dtype=np.int64)] = True
    n_rest = int((~taken).sum())
    if n_rest != N_B - 1 - 8 - S_RARE:  # 919
        raise _Stop(
            "X17_STOP_NONFINITE",
            "rest-cell count %d != 919 in column %d" % (n_rest, b),
        )
    col[diag] = recipe["diag"]
    col[np.asarray(neigh, dtype=np.int64)] = recipe["neigh_share"] / 8.0
    col[np.asarray(rare, dtype=np.int64)] = 0.0
    col[~taken] = recipe["rest_share"] / float(n_rest)
    return col


def build_table(recipe):
    """Build the synthetic joint + arm tables for a recipe; (info, 0 draws)."""
    f_pre = np.empty((N_B, N_B), dtype=np.float64)
    for b in range(N_B):
        col = _column_masses(b, recipe)
        if not math.isfinite(float(col.sum())) or abs(float(col.sum()) - 1.0) > 1e-12:
            raise _Stop(
                "X17_STOP_NONFINITE", "pre-floor column %d does not sum to 1" % b
            )
        f_pre[:, b] = col
    f = np.maximum(f_pre, FLOOR)
    f /= f.sum(axis=0, keepdims=True)
    if not (np.isfinite(f).all() and (f > 0).all()):
        raise _Stop("X17_STOP_NONFINITE", "non-positive/nonfinite floored table")
    p1 = prior.derive_p1(f)
    p2 = prior.derive_p2(f)
    floor_hit_measured = float((f_pre == 0.0).sum()) / float(N_B * N_B)
    u1c_all = np.argmax(p1, axis=0)
    acc = 0.0
    for b in range(N_B):
        col_u2 = f.reshape(Q, Q, N_B)[:, :, b].sum(axis=0)
        row = p2[int(u1c_all[b]), b, :]
        acc += float(np.sum(col_u2 * -np.log2(row)))
    model_mean = acc / float(N_B)
    f_min = float(f.min())
    f_max = float(f.max())
    h1_acc = h2_acc = hit1 = hit2 = 0.0
    for b in range(N_B):
        c1 = p1[:, b]
        h1_acc += float(-np.sum(c1 * np.log2(c1)))
        u1c = int(u1c_all[b])
        c2 = p2[u1c, b, :]
        h2_acc += float(-np.sum(c2 * np.log2(c2)))
        joint = f.reshape(Q, Q, N_B)[:, :, b]
        hit1 += float(joint[int(np.argmax(c1)), :].sum())
        hit2 += float(joint[u1c, int(np.argmax(c2))])
    out = {
        "f": f,
        "p1": p1,
        "p2": p2,
        "floor_hit_measured": floor_hit_measured,
        "model_mean_hazard_bits": model_mean,
        "f_min": f_min,
        "f_max": f_max,
        "model_h1_bits": h1_acc / float(N_B),
        "model_h2_bits": h2_acc / float(N_B),
        "diagonal_mass": float(np.mean(np.diag(f))),
        "argmax_hit_l1": hit1 / float(N_B),
        "argmax_hit_l2": hit2 / float(N_B),
    }
    for v in out.values():
        if isinstance(v, float) and not math.isfinite(v):
            raise _Stop("X17_STOP_NONFINITE", "nonfinite calibration scalar")
    return out, 0


def _ranks_in_mass_order(mass_rows, true_symbols):
    order = np.argsort(-np.asarray(mass_rows, dtype=np.float64), axis=1, kind="stable")
    true = np.asarray(true_symbols, dtype=np.int64).reshape(-1, 1)
    return (np.argmax(order == true, axis=1) + 1).astype(np.int64)


def _d1_cond(p1, bob, high, k):
    """D1 (X16-verbatim): X-domain high at first-k positions (the p2 first
    axis is the X-domain high component), argmax-p1 hard estimates elsewhere."""
    cond = np.argmax(p1[:, np.asarray(bob)], axis=0)
    cond = np.asarray(cond, dtype=np.int64).copy()
    cond[: int(k)] = np.asarray(high, dtype=np.int64)[: int(k)]
    return cond


def _bin_of_excess(e):
    if e >= 8.0:
        return "[8,inf)"
    if e >= 4.0:
        return "[4,8)"
    if e >= SPIKE_MARGIN:
        return "[2,4)"
    return "nonsplike_ref"


def _median_n(h, r, n):
    out = np.empty(n, dtype=np.float64)
    for j in range(n):
        lo = j - r if j - r > 0 else 0
        hi = j + r + 1 if j + r + 1 < n else n
        out[j] = float(np.median(h[lo:hi]))
    return out


def _topk_n(desc_score, k, n):
    idx = np.lexsort(
        (np.arange(n, dtype=np.int64), -np.asarray(desc_score, dtype=np.float64))
    )
    return idx[:k]


def _bitrev_index(n):
    nbits = int(math.log2(n))
    assert 2 ** nbits == n, "bit-reversal needs a power of two"
    out = np.empty(n, dtype=np.int64)
    for j in range(n):
        out[j] = int(bin(j)[2:].zfill(nbits)[::-1], 2)
    return out


def _sc_run(logp, field, known_pos, known_val, counters):
    try:
        res = sc.sc_decode(
            logp,
            field=field,
            alpha=ALPHA,
            known_positions=np.asarray(known_pos, dtype=np.int64),
            known_values=np.asarray(known_val, dtype=np.int64),
        )
    except sc.ImpossibleDisclosedValueError as exc:
        raise _Stop("X17_STOP_IMPOSSIBLE", "disclosed truth w/o SC support: %s" % exc)
    counters["decoder_calls"] += 1
    if not np.array_equal(
        res.x_hat, transform.polar_transform(res.u_hat, field=field, alpha=ALPHA)
    ):
        raise _Stop("X17_STOP_SC_CONSISTENCY", "sc re-encode check failed")
    return res


def _frac(mm):
    return float(np.mean(mm)) if mm.size else None


def run_small_block(rng, tables, field, counters, n, k1, k2):
    """One small-N block: decoder-free Q1/Q1b records + all SC arms.

    Returns dict with excess/ranks (X-domain true cells, X16-verbatim),
    per-arm mismatch fractions (overall + undisclosed-region), and the
    A4-shuffle identity flag. 8 sc_decode calls (A1 is a free rescore).
    """
    p_b = np.full(N_B, 1.0 / float(N_B), dtype=np.float64)
    bob, _, high, low = empirical_channel.sample_full_block(
        rng, p_b, tables["f"], Q, Q, n
    )
    counters["rng_calls"] += 2
    # Corrected truth-side (production two_layer.py:629-634 semantics):
    # X-domain component vectors -> U-domain truth via polar_transform.
    u1_true = transform.polar_transform(high, field=field, alpha=ALPHA)
    u2_true = transform.polar_transform(low, field=field, alpha=ALPHA)
    p1 = tables["p1"]
    p2 = tables["p2"]
    # D1 conditioning (X-domain high at first-k1, argmax elsewhere).
    u1_cond = _d1_cond(p1, bob, high, k1)
    mass_true = p2[u1_cond, bob, low]
    if not (np.isfinite(mass_true).all() and (mass_true > 0).all()):
        raise _Stop("X17_STOP_NONFINITE", "non-positive/nonfinite true-cell mass")
    h = -np.log2(mass_true)
    pm = float(np.mean(h[:k2]))
    if not math.isfinite(pm):
        raise _Stop("X17_STOP_NONFINITE", "nonfinite prefix mean")
    excess = h - pm
    rank_q1 = _ranks_in_mass_order(p2[u1_cond, bob, :], low)
    rank_q1b = _ranks_in_mass_order(p1[:, bob].transpose(1, 0), high)

    l2_rows_d1 = p2[u1_cond, bob, :]
    metric_d1 = prior.probs_to_symbol_metric(
        l2_rows_d1,
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
    )
    l2_rows_oracle = p2[high, bob, :]
    metric_oracle = prior.probs_to_symbol_metric(
        l2_rows_oracle,
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
    )

    arms = {}
    # A0: X16 verbatim replay (X-domain known_values, scored vs fed X array).
    res_a0 = _sc_run(metric_d1.logp, field, np.arange(k2), low[:k2], counters)
    mm_a0 = res_a0.u_hat != low
    if bool(mm_a0[:k2].any()):
        raise _Stop(
            "X17_STOP_NONFINITE", "A0 disclosed positions mismatched: D2 replay broken"
        )
    arms["A0"] = {"mm_all": _frac(mm_a0), "mm_undisc": _frac(mm_a0[k2:])}
    # A1: rescore-only of the SAME decode (no new decoder call).
    arms["A1"] = {
        "u_hat_vs_Utrue": _frac(res_a0.u_hat != u2_true),
        "x_hat_vs_Xtrue": _frac(res_a0.x_hat != low),
    }
    # A2: corrected U-truth feed, scored vs U-truth.
    res_a2 = _sc_run(metric_d1.logp, field, np.arange(k2), u2_true[:k2], counters)
    mm_a2 = res_a2.u_hat != u2_true
    if bool(mm_a2[:k2].any()):
        raise _Stop("X17_STOP_NONFINITE", "A2 disclosed positions mismatched")
    arms["A2"] = {"mm_all": _frac(mm_a2), "mm_undisc": _frac(mm_a2[k2:])}
    # A3: A2 + true-high conditioning everywhere.
    res_a3 = _sc_run(metric_oracle.logp, field, np.arange(k2), u2_true[:k2], counters)
    mm_a3 = res_a3.u_hat != u2_true
    if bool(mm_a3[:k2].any()):
        raise _Stop("X17_STOP_NONFINITE", "A3 disclosed positions mismatched")
    arms["A3"] = {"mm_all": _frac(mm_a3), "mm_undisc": _frac(mm_a3[k2:])}
    # A4i: shuffled known order (values follow positions) => bit-identical.
    perm = rng.permutation(k2)
    counters["rng_calls"] += 1
    res_shuf = _sc_run(
        metric_d1.logp, field, np.arange(k2)[perm], u2_true[np.arange(k2)[perm]],
        counters,
    )
    arms["A4_shuffle_identical"] = bool(np.array_equal(res_shuf.u_hat, res_a2.u_hat))
    # A4ii: bit-reversed metric rows (U coords stay natural).
    rev = _bitrev_index(n)
    metric_rev = prior.SymbolMetric(
        logp=np.ascontiguousarray(metric_d1.logp[rev]),
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
        symbol_order=tuple(range(Q)),
        normalization="LOGSUMEXP_ZERO",
    )
    res_rev = _sc_run(metric_rev.logp, field, np.arange(k2), u2_true[:k2], counters)
    mm_rev = res_rev.u_hat != u2_true
    arms["A4_reversed"] = {"mm_all": _frac(mm_rev), "mm_undisc": _frac(mm_rev[k2:])}
    # A4iii: random-K disclosed set.
    subset = np.sort(rng.choice(n, size=k2, replace=False))
    counters["rng_calls"] += 1
    res_rk = _sc_run(metric_d1.logp, field, subset, u2_true[subset], counters)
    mm_rk = res_rk.u_hat != u2_true
    arms["A4_randomK"] = {"mm_all": _frac(mm_rk)}
    # A5: uniform-metric and sign-flipped-logp controls (corrected disclosure).
    uni_rows = np.full((n, Q), 1.0 / float(Q), dtype=np.float64)
    metric_uni = prior.probs_to_symbol_metric(
        uni_rows,
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
    )
    res_uni = _sc_run(metric_uni.logp, field, np.arange(k2), u2_true[:k2], counters)
    mm_uni = res_uni.u_hat != u2_true
    arms["A5_uniform"] = {"mm_all": _frac(mm_uni), "mm_undisc": _frac(mm_uni[k2:])}
    neg = -np.asarray(metric_d1.logp, dtype=np.float64)
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(neg, axis=1)
    metric_flip = prior.SymbolMetric(
        logp=np.ascontiguousarray(neg - lse[:, None]),
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
        symbol_order=tuple(range(Q)),
        normalization="LOGSUMEXP_ZERO",
    )
    res_flip = _sc_run(metric_flip.logp, field, np.arange(k2), u2_true[:k2], counters)
    mm_flip = res_flip.u_hat != u2_true
    arms["A5_signflip"] = {"mm_all": _frac(mm_flip), "mm_undisc": _frac(mm_flip[k2:])}

    # Q2 F-median8 detector vs mean-hazard baseline, oracle = A2 mismatch.
    d = h - _median_n(h, R_MEDIAN, n)
    sel_local = set(_topk_n(d, k2, n).tolist())
    sel_base = set(_topk_n(h, k2, n).tolist())
    mm_set = set(np.flatnonzero(mm_a2).tolist())
    return {
        "excess": excess,
        "rank_q1": rank_q1,
        "rank_q1b": rank_q1b,
        "arms": arms,
        "n_mm_a2": len(mm_set),
        "n_mm_a2_in_local": len(mm_set & sel_local),
        "n_mm_a2_in_base": len(mm_set & sel_base),
    }


def run_positive_block(rng, tables, field, counters):
    """P positive-control block: near-noiseless channel, corrected feed."""
    p_b = np.full(N_B, 1.0 / float(N_B), dtype=np.float64)
    bob, _, high, low = empirical_channel.sample_full_block(
        rng, p_b, tables["f"], Q, Q, N_SMALL
    )
    counters["rng_calls"] += 2
    u2_true = transform.polar_transform(low, field=field, alpha=ALPHA)
    u1_cond = _d1_cond(tables["p1"], bob, high, K1_SMALL)
    metric = prior.probs_to_symbol_metric(
        tables["p2"][u1_cond, bob, :],
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
    )
    res = _sc_run(
        metric.logp, field, np.arange(K2_SMALL), u2_true[:K2_SMALL], counters
    )
    mm = res.u_hat != u2_true
    return {"mm_all": _frac(mm), "mm_undisc": _frac(mm[K2_SMALL:])}


def run_confirm_block(rng, tables, field, counters):
    """C full-scale block: X16 recipe at N=32768, corrected truth-side."""
    p_b = np.full(N_B, 1.0 / float(N_B), dtype=np.float64)
    bob, _, high, low = empirical_channel.sample_full_block(
        rng, p_b, tables["f"], Q, Q, N_CONFIRM
    )
    counters["rng_calls"] += 2
    u2_true = transform.polar_transform(low, field=field, alpha=ALPHA)
    u1_cond = _d1_cond(tables["p1"], bob, high, K1_CONFIRM)
    metric_d1 = prior.probs_to_symbol_metric(
        tables["p2"][u1_cond, bob, :],
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
    )
    metric_oracle = prior.probs_to_symbol_metric(
        tables["p2"][high, bob, :],
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
    )
    res_a2 = _sc_run(
        metric_d1.logp, field, np.arange(K2_CONFIRM), u2_true[:K2_CONFIRM], counters
    )
    res_a3 = _sc_run(
        metric_oracle.logp, field, np.arange(K2_CONFIRM), u2_true[:K2_CONFIRM],
        counters,
    )
    mm_a2 = res_a2.u_hat != u2_true
    mm_a3 = res_a3.u_hat != u2_true
    return {
        "A2_feed": {"mm_all": _frac(mm_a2), "mm_undisc": _frac(mm_a2[K2_CONFIRM:])},
        "A3_feed": {"mm_all": _frac(mm_a3), "mm_undisc": _frac(mm_a3[K2_CONFIRM:])},
    }


def _pooled_stats(values):
    xs = [float(v) for v in values if v is not None]
    if not xs:
        return {"n": 0, "mean": None, "sample_std": None, "min": None, "max": None}
    out = {
        "n": len(xs),
        "mean": float(statistics.fmean(xs)),
        "sample_std": float(statistics.stdev(xs)) if len(xs) >= 2 else None,
        "min": float(min(xs)),
        "max": float(max(xs)),
    }
    for key in ("mean", "sample_std", "min", "max"):
        val = out[key]
        if val is not None and not math.isfinite(val):
            raise _Stop("X17_STOP_NONFINITE", "nonfinite pooled stat %s" % key)
    return out


def _gate_flags(q1b_nonspike_l8_mean, spike_frac):
    g2 = q1b_nonspike_l8_mean is not None and q1b_nonspike_l8_mean >= G2_MIN
    g3 = spike_frac is not None and G3_LO <= spike_frac <= G3_HI
    return {"G2": bool(g2), "G3": bool(g3)}


def _assert_finite_tree(node, path="root"):
    if node is None:
        return
    if isinstance(node, bool):
        return
    if isinstance(node, (int, np.integer)):
        return
    if isinstance(node, (float, np.floating)):
        if not math.isfinite(float(node)):
            raise _Stop("X17_STOP_NONFINITE", "nonfinite at %s" % path)
        return
    if isinstance(node, (str, np.str_)):
        return
    if isinstance(node, dict):
        for key, val in node.items():
            _assert_finite_tree(val, "%s.%s" % (path, key))
        return
    if isinstance(node, (list, tuple, np.ndarray)):
        for i, val in enumerate(list(node)):
            _assert_finite_tree(val, "%s[%d]" % (path, i))
        return
    raise _Stop("X17_STOP_NONFINITE", "non-scalar leaf at %s: %r" % (path, type(node)))


def _to_plain(node):
    if node is None or isinstance(node, (str, bool)):
        return node
    if isinstance(node, (np.bool_,)):
        return bool(node)
    if isinstance(node, (np.integer,)):
        return int(node)
    if isinstance(node, (np.floating,)):
        return float(node)
    if isinstance(node, (int, float)):
        return node
    if isinstance(node, dict):
        return {str(k): _to_plain(v) for k, v in node.items()}
    if isinstance(node, (list, tuple)):
        return [_to_plain(v) for v in node]
    if isinstance(node, np.ndarray):
        return [_to_plain(v) for v in node.tolist()]
    raise _Stop("X17_STOP_NONFINITE", "non-plain leaf: %r" % type(node))


# --- injected self-tests (--selftest only; never write results.json) ---
def _selftest_rank_sanity():
    for true in (0, 7, 31):
        row = np.full((1, Q), 0.1 / 31.0, dtype=np.float64)
        row[0, true] = 0.9
        got = _ranks_in_mass_order(row, np.asarray([true], dtype=np.int64))
        assert int(got[0]) == 1, "peaked-row rank != 1 for true=%d" % true
    flat = np.full((1, Q), 1.0 / Q, dtype=np.float64)
    got = _ranks_in_mass_order(flat, np.arange(Q, dtype=np.int64))
    assert got.shape == (Q,), "uniform-row rank shape wrong"
    for k in range(Q):
        one = _ranks_in_mass_order(flat, np.asarray([k], dtype=np.int64))
        assert int(one[0]) == k + 1, "tie-break rank wrong at %d" % k
    print("SELFTEST rank-1-peaked-row+TIE-BREAK: PASS")


def _selftest_diagonal_smoke():
    for recipe, pin in ((RECIPE_A, 0.75), (RECIPE_P, 0.999)):
        tables, table_rng = build_table(recipe)
        assert table_rng == 0, "deterministic table must draw no RNG"
        f = tables["f"]
        assert np.allclose(f.sum(axis=0), 1.0, atol=1e-12), "post col sums != 1"
        assert bool(
            (np.argmax(f, axis=0) == np.arange(N_B)).all()
        ), "post-floor argmax != diagonal somewhere"
        for b in (0, 1, 37, 1023):
            col = _column_masses(b, recipe)
            assert int(np.argmax(col)) == b, "argmax != diagonal at b=%d" % b
        assert abs(float(np.mean(np.diag(f))) - pin) < 0.002, "diag pin off: %r" % (
            tables["diagonal_mass"]
        )
        rate = tables["floor_hit_measured"]
        assert rate == S_RARE / float(N_B) == 0.09375, "floor-hit != 96/1024"
    print("SELFTEST diagonal-smoke(A+P recipes): PASS")


def _selftest_domain_consistency():
    # Involution: G(G(x)) == x (characteristic-two kernel is its own inverse).
    field = algebra.make_gf32()
    rng = np.random.default_rng(2026092390)
    vec = np.asarray(rng.integers(0, Q, size=64), dtype=np.int64)
    assert np.array_equal(
        transform.polar_transform(
            transform.polar_transform(vec, field=field, alpha=ALPHA),
            field=field, alpha=ALPHA,
        ),
        vec,
    ), "transform involution broken"
    # P2 wiring assert: all-known U-truth decodes exactly.
    n_small = 64
    logp = np.asarray(rng.normal(size=(n_small, Q)), dtype=np.float64)
    truth = np.asarray(rng.integers(0, Q, size=n_small), dtype=np.int64)
    res_all = sc.sc_decode(
        logp, field=field, alpha=ALPHA,
        known_positions=np.arange(n_small, dtype=np.int64), known_values=truth,
    )
    assert np.array_equal(res_all.u_hat, truth), "all-known SC != truth"
    # X-fed control: X-domain values forced at U coordinates do NOT equal
    # U-domain truth (domain confusion is detectable, override is exact).
    x_vals = np.asarray(rng.integers(0, Q, size=n_small), dtype=np.int64)
    u_true = transform.polar_transform(x_vals, field=field, alpha=ALPHA)
    res_x = sc.sc_decode(
        logp, field=field, alpha=ALPHA,
        known_positions=np.arange(n_small, dtype=np.int64), known_values=x_vals,
    )
    assert np.array_equal(res_x.u_hat, x_vals), "forced X values not returned"
    assert float(np.mean(res_x.u_hat != u_true)) > 0.5, "X-fed unexpectedly == U-truth"
    print("SELFTEST domain-consistency+P2-all-known: PASS")


def _selftest_order_shuffle_identity():
    field = algebra.make_gf32()
    rng = np.random.default_rng(2026092390)
    n_small = 64
    logp = np.asarray(rng.normal(size=(n_small, Q)), dtype=np.float64)
    truth = np.asarray(rng.integers(0, Q, size=n_small), dtype=np.int64)
    k = 13
    res_plain = sc.sc_decode(
        logp, field=field, alpha=ALPHA,
        known_positions=np.arange(k, dtype=np.int64), known_values=truth[:k],
    )
    perm = rng.permutation(k)
    res_shuf = sc.sc_decode(
        logp, field=field, alpha=ALPHA,
        known_positions=np.arange(k)[perm], known_values=truth[np.arange(k)[perm]],
    )
    assert np.array_equal(res_shuf.u_hat, res_plain.u_hat), "shuffle changed u_hat"
    # Bit-reversal is an involution and a true permutation.
    rev = _bitrev_index(64)
    assert sorted(rev.tolist()) == list(range(64)), "bitrev not a permutation"
    assert np.array_equal(rev[rev], np.arange(64)), "bitrev not an involution"
    print("SELFTEST order-shuffle-identity+bitrev: PASS")


def _selftest_gate_asserts():
    ok = _gate_flags(0.75, 0.10)
    assert ok == {"G2": True, "G3": True}, ok
    assert _gate_flags(0.49, 0.10)["G2"] is False
    assert _gate_flags(None, 0.10)["G2"] is False
    assert _gate_flags(0.75, 0.019)["G3"] is False
    assert _gate_flags(0.75, 0.701)["G3"] is False
    assert _gate_flags(0.75, 0.02)["G3"] is True
    assert _gate_flags(0.75, 0.70)["G3"] is True
    print("SELFTEST sanity-gate-asserts(G2/G3; G1 retired): PASS")


def main():
    parser = argparse.ArgumentParser(prog="body.py")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        _selftest_rank_sanity()
        _selftest_diagonal_smoke()
        _selftest_domain_consistency()
        _selftest_order_shuffle_identity()
        _selftest_gate_asserts()
        return 0

    notes = [
        "Tier-X descriptive probe only: no thresholds, no pass/fail, no verdicts; SCL stays locked whatever the numbers say.",
        "X16-G1 RETIRED with justification: mismatch is the measured audit variable; stopping on it would prejudge the audit. G2/G3 retained as structural wiring checks (identical decoder-free machinery + identical channel family).",
        "H-a audit: X16 fed X-domain high/low as U known_values and scored U-output vs X-truth. A0 replays that verbatim (scores vs the fed X array, disclosed match trivially by forcing = void check). A1 rescores the SAME decode vs U-truth / X-truth. A2 feeds U-truth (polar_transform of X comps, production two_layer.py:629-634 semantics) and scores vs U-truth. Metric conditioning (D1 first-K1 high + argmax-p1) is X16-verbatim throughout: the p2 first axis is the X-domain high component, so conditioning was never the confused half.",
        "Q1/Q1b rank the X-domain label components (low/high) the p1/p2 rows are distributions over (X16-verbatim decoder-free machinery); SC arms use U-domain truth per production semantics. q1_method note records this split explicitly.",
        "decoder_calls actual = 4 seeds x 8 arm-decodes (A0,A2,A3,A4shuffle,A4reversed,A4randomK,A5uniform,A5signflip; A1 is a free rescore) + 4 P + 2 C = 38. rng_calls actual = 4 x (2 sample + 1 permutation + 1 choice) + 4 x 2 (P sample) + 1 x 2 (C sample) = 26. tag_calls = 0; zero protected opens.",
        "Predictions below are descriptive (never gates): A0 undisclosed ~= chance 0.96875; A2 in [0.05,0.45]; P in [0.00,0.05].",
    ]
    _check_prereg()

    def stop_with_evidence(status, detail, evidence):
        evidence["status"] = status
        evidence["stop_detail"] = detail
        evidence["wall_s"] = time.time() - T0
        evidence["rss_bytes"] = _rss_bytes()
        plain = _to_plain(evidence)
        _assert_finite_tree(plain)
        size = _finish(plain)
        if size > 2 * 1024 * 1024:
            raise _Stop("X17_STOP_OVERSIZE", "results.json %d bytes > 2 MB" % size)
        sys.stderr.write("STOP %s: %s\n" % (status, detail))
        sys.exit(2)

    try:
        tables_a, rng_a = build_table(RECIPE_A)
        tables_p, rng_p = build_table(RECIPE_P)
        counters = {"decoder_calls": 0, "rng_calls": int(rng_a + rng_p)}
        field = algebra.make_gf32()

        per_seed = {}
        for seed in SEEDS_ARMS:
            rng = empirical_channel.make_rng(int(seed))
            surv_q1 = {b: {L: [0, 0] for L in LS} for b in BINS}
            surv_q1b = {b: {L: [0, 0] for L in LS} for b in BINS}
            spike_n = {b: 0 for b in BINS}
            blk = run_small_block(
                rng, tables_a, field, counters, N_SMALL, K1_SMALL, K2_SMALL
            )
            for j in range(N_SMALL):
                b = _bin_of_excess(float(blk["excess"][j]))
                spike_n[b] += 1
                for L in LS:
                    s = surv_q1[b][L]
                    s[1] += 1
                    s[0] += 1 if int(blk["rank_q1"][j]) <= L else 0
                    t = surv_q1b[b][L]
                    t[1] += 1
                    t[0] += 1 if int(blk["rank_q1b"][j]) <= L else 0
            q1_tab = {}
            q1b_tab = {}
            for b in BINS:
                for L in LS:
                    s = surv_q1[b][L]
                    q1_tab["%s|L%d" % (b, L)] = {
                        "frac": (s[0] / s[1]) if s[1] else None,
                        "n": s[1],
                    }
                    t = surv_q1b[b][L]
                    q1b_tab["%s|L%d" % (b, L)] = {
                        "frac": (t[0] / t[1]) if t[1] else None,
                        "n": t[1],
                    }
            per_seed[str(seed)] = {
                "q1": q1_tab,
                "q1b": q1b_tab,
                "arms": blk["arms"],
                "q2": {
                    "coverage_local_spike": (
                        blk["n_mm_a2_in_local"] / blk["n_mm_a2"]
                    ) if blk["n_mm_a2"] else None,
                    "coverage_mean_hazard": (
                        blk["n_mm_a2_in_base"] / blk["n_mm_a2"]
                    ) if blk["n_mm_a2"] else None,
                    "n_mismatch_a2": blk["n_mm_a2"],
                },
                "spike_counts": dict(spike_n),
            }

        per_positive = {}
        for seed in SEEDS_POSITIVE:
            rng = empirical_channel.make_rng(int(seed))
            per_positive[str(seed)] = run_positive_block(rng, tables_p, field, counters)

        per_confirm = {}
        for seed in SEEDS_CONFIRM:
            rng = empirical_channel.make_rng(int(seed))
            per_confirm[str(seed)] = run_confirm_block(rng, tables_a, field, counters)

        pooled_q1 = {}
        pooled_q1b = {}
        for b in BINS:
            for L in LS:
                key = "%s|L%d" % (b, L)
                pooled_q1[key] = _pooled_stats(
                    [per_seed[str(s)]["q1"][key]["frac"] for s in SEEDS_ARMS]
                )
                pooled_q1b[key] = _pooled_stats(
                    [per_seed[str(s)]["q1b"][key]["frac"] for s in SEEDS_ARMS]
                )
        arm_keys = (
            "A0", "A1", "A2", "A3", "A4_reversed", "A4_randomK",
            "A5_uniform", "A5_signflip",
        )
        pooled_arms = {}
        for arm in arm_keys:
            sub = {}
            if arm == "A1":
                fields = ("u_hat_vs_Utrue", "x_hat_vs_Xtrue")
            elif arm == "A4_randomK":
                fields = ("mm_all",)
            else:
                fields = ("mm_all", "mm_undisc")
            for fld in fields:
                sub[fld] = _pooled_stats(
                    [per_seed[str(s)]["arms"][arm].get(fld) for s in SEEDS_ARMS]
                )
            pooled_arms[arm] = sub
        pooled_arms["A4_shuffle_identical"] = {
            "all": bool(
                all(
                    per_seed[str(s)]["arms"]["A4_shuffle_identical"]
                    for s in SEEDS_ARMS
                )
            ),
            "per_seed": {
                str(s): bool(per_seed[str(s)]["arms"]["A4_shuffle_identical"])
                for s in SEEDS_ARMS
            },
        }
        pooled_p = {
            "mm_all": _pooled_stats(
                [per_positive[str(s)]["mm_all"] for s in SEEDS_POSITIVE]
            ),
            "mm_undisc": _pooled_stats(
                [per_positive[str(s)]["mm_undisc"] for s in SEEDS_POSITIVE]
            ),
        }
        q2_loc = [
            per_seed[str(s)]["q2"]["coverage_local_spike"] for s in SEEDS_ARMS
        ]
        q2_bas = [
            per_seed[str(s)]["q2"]["coverage_mean_hazard"] for s in SEEDS_ARMS
        ]
        mm_a2_all = sum(
            per_seed[str(s)]["q2"]["n_mismatch_a2"] for s in SEEDS_ARMS
        )
        loc_hit = sum(
            (per_seed[str(s)]["q2"]["coverage_local_spike"] or 0.0)
            * per_seed[str(s)]["q2"]["n_mismatch_a2"]
            for s in SEEDS_ARMS
        )
        bas_hit = sum(
            (per_seed[str(s)]["q2"]["coverage_mean_hazard"] or 0.0)
            * per_seed[str(s)]["q2"]["n_mismatch_a2"]
            for s in SEEDS_ARMS
        )
        pooled_q2 = {
            "local_spike_seed_stats": _pooled_stats(q2_loc),
            "mean_hazard_seed_stats": _pooled_stats(q2_bas),
            "ratio_of_sums": {
                "n_mismatch_a2_total": mm_a2_all,
                "coverage_local_spike": (loc_hit / mm_a2_all) if mm_a2_all else None,
                "coverage_mean_hazard": (bas_hit / mm_a2_all) if mm_a2_all else None,
            },
        }
        pooled_spike = {
            b: sum(per_seed[str(s)]["spike_counts"][b] for s in SEEDS_ARMS)
            for b in BINS
        }
        n_pos_total = len(SEEDS_ARMS) * BLOCKS_PER_SEED * N_SMALL
        q1b_nonspike_l8 = pooled_q1b.get("nonsplike_ref|L8", {}).get("mean")
        n_spike_total = sum(pooled_spike[b] for b in SPIKE_BINS)
        spike_frac = (n_spike_total / n_pos_total) if n_pos_total else None
        flags = _gate_flags(q1b_nonspike_l8, spike_frac)
        sanity_gates = {
            "G1_X16_RETIRED": {
                "retired": True,
                "reason": "mismatch is the measured audit variable; gating on it would prejudge the audit",
            },
            "G2_q1b_nonspike_L8_mean": {
                "measured": q1b_nonspike_l8,
                "floor": G2_MIN,
                "pass": flags["G2"],
            },
            "G3_spike_fraction": {
                "measured": spike_frac,
                "band": [G3_LO, G3_HI],
                "pass": flags["G3"],
            },
        }

        def _calib(tables):
            return {
                "table_f_min": tables["f_min"],
                "table_f_max": tables["f_max"],
                "model_h1_bits": tables["model_h1_bits"],
                "model_h2_bits": tables["model_h2_bits"],
                "diagonal_mass": tables["diagonal_mass"],
                "argmax_hit_l1": tables["argmax_hit_l1"],
                "argmax_hit_l2": tables["argmax_hit_l2"],
            }

        evidence_base = {
            "probe_id": PROBE_ID,
            "tier": TIER,
            "question": "Which wiring defect explains the X16 SC-path disease (informative tables, chance-level SC path) - A0 replay, A1 rescore, A2 corrected feed, A3 oracle-u1 gap, A4 order/set controls, A5 log-domain controls, P positive control, C full-scale confirmation (descriptive only).",
            "frozen": {
                "N_small": N_SMALL,
                "N_confirm": N_CONFIRM,
                "q": Q,
                "alpha": ALPHA,
                "gf32_poly": 37,
                "chunk_rows": CHUNK_ROWS,
                "floor": FLOOR,
                "recipe_A": RECIPE_A,
                "recipe_P": RECIPE_P,
                "K1_small": K1_SMALL,
                "K2_small": K2_SMALL,
                "K1_confirm": K1_CONFIRM,
                "K2_confirm": K2_CONFIRM,
                "R_median": R_MEDIAN,
                "spike_margin_bits": SPIKE_MARGIN,
                "block_seeds_arms": list(SEEDS_ARMS),
                "block_seeds_positive": list(SEEDS_POSITIVE),
                "block_seeds_confirm": list(SEEDS_CONFIRM),
                "blocks_per_seed": BLOCKS_PER_SEED,
                "q1_method": "ranks over X-domain label components (low in p2 rows, high in p1 cols): the quantities the metric rows are distributions over; X16-verbatim decoder-free machinery",
                "u_truth_method": "U-domain truth = polar_transform of X-domain component vectors (production two_layer.py:629-634 semantics)",
                "predictions_descriptive_only": {
                    "A0_undisc": "~chance %.5f (bug replay)" % PREDICT_A0_CHANCE,
                    "A2_mm_band": list(PREDICT_A2_BAND),
                    "P_mm_band": list(PREDICT_P_BAND),
                },
            },
            "per_seed_arms": per_seed,
            "per_seed_positive": per_positive,
            "per_seed_confirm": per_confirm,
            "pooled": {
                "q1": pooled_q1,
                "q1b": pooled_q1b,
                "arms": pooled_arms,
                "positive": pooled_p,
                "q2_vs_A2_oracle": pooled_q2,
                "spike_counts_total": pooled_spike,
            },
            "sanity_gates": sanity_gates,
            "calibration": {
                "channel_A": _calib(tables_a),
                "channel_P": _calib(tables_p),
            },
            "floor_hit": {
                "measured": tables_a["floor_hit_measured"],
                "pin_planted": S_RARE / float(N_B),
            },
            "model_mean_hazard_bits": tables_a["model_mean_hazard_bits"],
            "command": COMMAND,
            "interpreter": {
                "executable": sys.executable,
                "version": sys.version.splitlines()[0],
            },
            "env_pins": {
                "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
                "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
                "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
                "MALLOC_ARENA_MAX": os.environ.get("MALLOC_ARENA_MAX"),
            },
            "wall_s": time.time() - T0,
            "decoder_calls": counters["decoder_calls"],
            "rng_calls": counters["rng_calls"],
            "tag_calls": 0,
            "protected_opens_attempted": False,
            "writes": [],
            "notes": notes,
            "prereg_sha256": _sha_file("prereg.md"),
            "body_sha256": _sha_file("body.py"),
        }
        if not flags["G2"]:
            stop_with_evidence(
                "X17_STOP_SANITY_G2",
                "pooled Q1b non-spike L8 mean %r < 0.50" % q1b_nonspike_l8,
                evidence_base,
            )
        if not flags["G3"]:
            stop_with_evidence(
                "X17_STOP_SANITY_G3",
                "pooled spike fraction %r outside [0.02, 0.70]" % spike_frac,
                evidence_base,
            )
        payload = dict(evidence_base)
        payload["status"] = STATUS_OK
        payload = _to_plain(payload)
        _assert_finite_tree(payload)
        size = _finish(payload)
        if size > 2 * 1024 * 1024:
            raise _Stop("X17_STOP_OVERSIZE", "results.json %d bytes > 2 MB" % size)
        payload["writes"] = [
            {
                "path": "workspace/probes/nbpolar_x17_metric_feed_audit/results.json",
                "size_bytes": size,
            }
        ]
        payload["wall_s"] = time.time() - T0
        _assert_finite_tree(payload)
        _finish(payload)
        print(
            "X17 probe complete: arms=%d P=%d C=%d decoder_calls=%d rng_calls=%d "
            "gates=%s" % (
                len(SEEDS_ARMS) * BLOCKS_PER_SEED,
                len(SEEDS_POSITIVE),
                len(SEEDS_CONFIRM),
                counters["decoder_calls"],
                counters["rng_calls"],
                flags,
            )
        )
        return 0
    except _Stop as exc:
        try:
            import resource

            rss = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
        except Exception:
            rss = 0
        payload = {
            "probe_id": PROBE_ID,
            "tier": TIER,
            "status": exc.status,
            "stop_detail": exc.detail,
            "question": "Which wiring defect explains the X16 SC-path disease (descriptive only).",
            "command": COMMAND,
            "interpreter": {
                "executable": sys.executable,
                "version": sys.version.splitlines()[0],
            },
            "wall_s": time.time() - T0,
            "rss_bytes": rss,
            "decoder_calls": 0,
            "rng_calls": 0,
            "tag_calls": 0,
            "protected_opens_attempted": False,
            "writes": [],
            "notes": notes,
        }
        try:
            _finish(_to_plain(payload))
        except Exception:
            pass
        sys.stderr.write("STOP %s: %s\n" % (exc.status, exc.detail))
        return 2


if __name__ == "__main__":
    sys.exit(main())
