#!/usr/bin/env python3
"""NBPOLAR-X16-SYNTHETIC-SCALE-DISCLOSURE - Tier-X probe body (frozen).

Restored operating point: N=32768 (15 levels), exact 2M disclosure literals
(K1=334 L1 true-u1 conditioning, K2=6746 L2 true-u2 SC disclosure), X15
0.75-diagonal channel kept verbatim (sharper than real => conservative).

Synthetic-only, decoder-free except the single greedy-SC (L=1) mismatch
oracle run per block for Q2. Stdlib + numpy only. Read-only reuse of the
accepted nbpolar modules (empirical_channel sampling recipes, prior
derive/convert, algebra field, transform re-encode check, sc oracle).
No list decoder is implemented or imported. No protected artifact
(pairs/V25 counts/parquet/1M/1.5M/2M content) is stat'ed, opened, or
imported - enforced by own-path-only file access plus a sys.modules
blocklist assert. Only file written: results.json (this directory).
Four injected self-tests run under --selftest (no results.json write).

Frozen recipes (TASK_PACKET.md section 2; X14/X15 section 2 reused VERBATIM):
  f_full[A,B] (1024x1024): per column b, DETERMINISTIC masses (no table RNG):
    A=b: 0.75 (diagonal pin); neighbors (b+k mod 1024, k=1..8) share 0.225
    (0.028125 each); rare15 (b+37k mod 1024, k=1..96) pre-floor 0 (preserves
    the 96/1024 = 9.375% floor pin); remaining 919 share 0.025 (~2.72e-5
    each). Disjointness asserted (37 coprime to 1024); violation raises
    X16_STOP_NONFINITE. Then the X14-identical pipeline: raw-count MLE (=
    the deterministic masses, already column-normalized) + 1e-15 floor +
    column renormalize to derive_p1 / derive_p2 (A = 32*U1 + U2,
    FULL_BOB_ONLY) to probs_to_symbol_metric.
  h_j = -log2 p2[u1_cond_j, b_j, u2_true_j] (frozen hazard atom).
  D1 (restored L1 disclosure, caller-side truth injection): u1_cond_j =
    u1_true_j at the first K1=334 natural positions; per-position
    argmax_u1 p1[u1,b] (ties to smallest index) elsewhere.
  pm = mean(h) over the disclosed L2 prefix = first K2=6746 natural
    positions (frozen l2_prefix_hazard_mean_bits recipe at restored K).
  spike iff e_j = h_j - pm >= 2.0 bits; strata [2,4)/[4,8)/[8,inf) + ref.
  Q1 rank: true u2_j in p2[u1_cond_j,b_j,:] mass-descending order, ties to
    smallest index; survives(L) iff rank <= L, L in {4,8}. Q1b: true u1_j
    in p1[:,b_j] column order, same rule.
  D2 (restored L2 disclosure): sc_decode receives known_positions =
    first K2=6746 natural positions with known_values = true u2 there
    (forced-correct, mirroring real disclosed semantics); all other
    positions decided by the argmax convention. Exact call:
    sc_decode(metric.logp, field=field, alpha=2,
    known_positions=np.arange(6746), known_values=u2_true[:6746]).
  Q2 F-median8 (user decision 2026-09-20; P20S section 3 verbatim):
    d_j = h_j - median(h over [j-8,j+8] clipped to [0,N)); detector =
    top-6746 by d_j, baseline = top-6746 by h_j (desc, ties to ascending
    index); coverage = selected-mismatch fraction of the single greedy
    sc_decode (L=1) run per block with D2 disclosure conditioning.
  Sanity gates (wiring/structure checks, checked BEFORE the main question;
    violation -> X16_STOP_SANITY_* + STOP, no repair):
    G1 (ONE-SIDED disclosure-bite gate): pooled greedy-SC mismatch
      ratio-of-sums < 0.75, else X16_STOP_SANITY_G1_HIGH. Derived ceiling
      (1-6746/32768)*31/32 ~= 0.769: at/above => disclosure did not bite.
      NO low-side stop; mismatch < 0.005 records a low-variance note and
      Q2 goes null-with-reason while Q1/Q1b proceed.
    G2: pooled Q1b non-spike L8 survival mean >= 0.50.
    G3: pooled spike fraction in [0.02, 0.70].
  On any gate stop the payload still carries the decoder-free scalars
    (G2 value, G3 value, calibration scalars) so the SC-path-disease vs
    channel-disease branch can be resolved without a second probe.
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

# Repo-root import of the accepted package (same convention as
# comparison_bench/tests/test_nbpolar_sc.py). No other sys.path edits.
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

# NOTE: "parquet" is intentionally NOT a module fragment here: importing the
# accepted comparison_bench package surface transitively loads
# pandas.io.parquet (pandas submodule, no file touched). Protected parquet
# *files* can never be opened: _own_path confines every file access to the
# probe root, and no reader for protected formats is ever imported.
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
            "X16_STOP_PROTECTED_PATH: refused module loaded: %s" % _mod_name
        )

# --- frozen constants (prereg line 2 verbatim values) ---
PROBE_ID = "NBPOLAR-X16-SYNTHETIC-SCALE-DISCLOSURE"
TIER = "X"
STATUS_OK = "X16_PROBE_COMPLETE_DESCRIPTIVE_ONLY"
N = 32768
Q = 32
ALPHA = 2
CHUNK_ROWS = 512
FLOOR = 1e-15
N_B = 1024
S_RARE = 96
RARE_STEP = 37  # coprime to 1024 -> 96 distinct rare symbols per column
DIAG_MASS = 0.75
N_NEIGH = 8
NEIGH_SHARE = 0.225
REST_SHARE = 0.025
K1_DISC = 334  # replayed 2M literal (exact, zero rounding at N=32768)
K2_DISC = 6746  # replayed 2M literal (exact, zero rounding at N=32768)
MASTER_SEED = 2026092380  # table-identity label only; NEVER a stream (no RNG draw)
BLOCK_SEEDS = (
    2026092381,
    2026092382,
    2026092383,
    2026092384,
    2026092385,
    2026092386,
    2026092387,
    2026092388,
)
BLOCKS_PER_SEED = 1
R_MEDIAN = 8
SPIKE_MARGIN = 2.0
BINS = ("[2,4)", "[4,8)", "[8,inf)", "nonsplike_ref")
SPIKE_BINS = ("[2,4)", "[4,8)", "[8,inf)")
LS = (4, 8)
G1_STOP_AT = 0.75  # ONE-SIDED: stop iff pooled mismatch ratio-of-sums >= 0.75
G1_LOW_VAR = 0.005  # below: low-variance note, Q2 null-with-reason, Q1/Q1b proceed
G2_MIN = 0.50
G3_LO, G3_HI = 0.02, 0.70
COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && "
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "
    "MALLOC_ARENA_MAX=2 && timeout 600 "
    "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python "
    "workspace/probes/nbpolar_x16_synthetic_scale_disclosure/body.py"
)
T0 = time.time()


class _Stop(Exception):
    def __init__(self, status, detail):
        super().__init__(detail)
        self.status = status
        self.detail = detail


# --- own-path-only file access (probe root only; never stat/open elsewhere) ---
def _own_path(rel):
    ap = os.path.normpath(os.path.join(HERE, rel))
    if ap != HERE and not ap.startswith(HERE + os.sep):
        raise _Stop("X16_STOP_PROTECTED_PATH", "path escapes probe root: %r" % rel)
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
        raise _Stop("X16_STOP_PREREG_MISMATCH", "prereg.md unreadable: %s" % exc)
    for token in (
        # NOTE: prereg.md holds the 3 verbatim PREREG_DRAFT lines, which never
        # spell the uppercase probe ID; identity is pinned by the lowercase
        # probe-root token from the frozen command line instead.
        "nbpolar_x16_synthetic_scale_disclosure",
        "F-median8",
        "2026092380",
        "2026092381..2026092388",
        "K1=334",
        "K2=6746",
        "N=32768",
        "timeout 600",
    ):
        if token not in text:
            raise _Stop(
                "X16_STOP_PREREG_MISMATCH", "prereg.md missing frozen token: %s" % token
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


# --- frozen channel recipe (X15 section 4 verbatim, at N=32768) ---
def _rare_symbols(b):
    return [(b + RARE_STEP * k) % N_B for k in range(1, S_RARE + 1)]


def _neighbor_symbols(b):
    return [(b + k) % N_B for k in range(1, N_NEIGH + 1)]


def _column_masses(b):
    """Deterministic per-column masses over Alice labels; no RNG.

    Returns (col, rare, neigh). col sums to exactly 1.0 pre-floor.
    """
    rare = _rare_symbols(b)
    neigh = _neighbor_symbols(b)
    if len(set(rare)) != S_RARE:
        raise _Stop(
            "X16_STOP_NONFINITE", "rare-symbol collision in column %d" % b
        )
    diag = int(b)
    if diag in rare or diag in neigh:
        raise _Stop(
            "X16_STOP_NONFINITE",
            "diagonal/rare/neighbor overlap in column %d" % b,
        )
    if set(rare) & set(neigh):
        raise _Stop(
            "X16_STOP_NONFINITE", "rare/neighbor overlap in column %d" % b
        )
    col = np.empty(N_B, dtype=np.float64)
    taken = np.zeros(N_B, dtype=bool)
    taken[diag] = True
    taken[np.asarray(neigh, dtype=np.int64)] = True
    taken[np.asarray(rare, dtype=np.int64)] = True
    n_rest = int((~taken).sum())
    if n_rest != N_B - 1 - N_NEIGH - S_RARE:  # 919
        raise _Stop(
            "X16_STOP_NONFINITE",
            "rest-cell count %d != 919 in column %d" % (n_rest, b),
        )
    col[diag] = DIAG_MASS
    col[np.asarray(neigh, dtype=np.int64)] = NEIGH_SHARE / float(N_NEIGH)
    col[np.asarray(rare, dtype=np.int64)] = 0.0
    col[~taken] = REST_SHARE / float(n_rest)
    return col, rare, neigh


def build_table():
    """Build the synthetic joint + arm tables; return dict of arrays/scalars.

    Deterministic: zero RNG draws (master seed is an identity label only).
    Returns (info, rng_calls_table=0). info holds f_pre, f, p1, p2,
    floor_hit_measured, model_mean_hazard_bits, plus calibration scalars
    f_min, f_max, model_h1_bits, model_h2_bits, diagonal_mass,
    argmax_hit_l1, argmax_hit_l2.
    """
    f_pre = np.empty((N_B, N_B), dtype=np.float64)
    for b in range(N_B):
        col, _, _ = _column_masses(b)
        if not math.isfinite(float(col.sum())) or abs(float(col.sum()) - 1.0) > 1e-12:
            raise _Stop(
                "X16_STOP_NONFINITE", "pre-floor column %d does not sum to 1" % b
            )
        f_pre[:, b] = col
    # X14-identical pipeline verbatim: raw-count MLE (= f_pre holding the
    # planted zeros) + 1e-15 floor + column renormalize. (prior helpers
    # floor/renormalize over the last axis, which is the Bob axis here, so
    # the column renormalization is written explicitly.)
    f = np.maximum(f_pre, FLOOR)
    f /= f.sum(axis=0, keepdims=True)
    if not (np.isfinite(f).all() and (f > 0).all()):
        raise _Stop("X16_STOP_NONFINITE", "non-positive/nonfinite floored table")
    p1 = prior.derive_p1(f)
    p2 = prior.derive_p2(f)
    floor_hit_measured = float((f_pre == 0.0).sum()) / float(N_B * N_B)
    if not math.isfinite(floor_hit_measured):
        raise _Stop("X16_STOP_NONFINITE", "nonfinite floor-hit rate")
    # Table-marginal expected hazard E[h], sampling-free exact: E over
    # b ~ uniform, u2|b from the floored joint column, u1_cond = argmax p1.
    u1c_all = np.argmax(p1, axis=0)  # (1024,), ties to smallest
    acc = 0.0
    for b in range(N_B):
        col_u2 = f.reshape(Q, Q, N_B)[:, :, b].sum(axis=0)  # P(u2|b), sums to 1
        row = p2[int(u1c_all[b]), b, :]
        acc += float(np.sum(col_u2 * -np.log2(row)))
    model_mean = acc / float(N_B)
    if not math.isfinite(model_mean):
        raise _Stop("X16_STOP_NONFINITE", "nonfinite model-mean hazard")
    # Calibration scalars (recorded descriptively, no gates): table f_min /
    # f_max (post-pipeline), model H1/H2 bits (uniform-b marginal entropies),
    # post-pipeline diagonal mass, pointwise argmax hit rates under the model
    # joint (L1: argmax_u1 p1 vs true u1; L2: argmax_u2 p2[u1c] vs true u2).
    f_min = float(f.min())
    f_max = float(f.max())
    h1_acc = 0.0
    h2_acc = 0.0
    hit1 = 0.0
    hit2 = 0.0
    for b in range(N_B):
        c1 = p1[:, b]
        h1_acc += float(-np.sum(c1 * np.log2(c1)))
        u1c = int(u1c_all[b])
        c2 = p2[u1c, b, :]
        h2_acc += float(-np.sum(c2 * np.log2(c2)))
        a1hat = int(np.argmax(c1))
        a2hat = int(np.argmax(c2))
        joint = f.reshape(Q, Q, N_B)[:, :, b]  # [u1, u2], sums to 1
        hit1 += float(joint[a1hat, :].sum())
        hit2 += float(joint[u1c, a2hat])
    model_h1 = h1_acc / float(N_B)
    model_h2 = h2_acc / float(N_B)
    argmax_hit_l1 = hit1 / float(N_B)
    argmax_hit_l2 = hit2 / float(N_B)
    diag_mass = float(np.mean(np.diag(f)))
    for v in (f_min, f_max, model_h1, model_h2, argmax_hit_l1, argmax_hit_l2,
              diag_mass):
        if not math.isfinite(v):
            raise _Stop("X16_STOP_NONFINITE", "nonfinite calibration scalar")
    return (
        {
            "f_pre": f_pre,
            "f": f,
            "p1": p1,
            "p2": p2,
            "floor_hit_measured": floor_hit_measured,
            "model_mean_hazard_bits": model_mean,
            "f_min": f_min,
            "f_max": f_max,
            "model_h1_bits": model_h1,
            "model_h2_bits": model_h2,
            "diagonal_mass": diag_mass,
            "argmax_hit_l1": argmax_hit_l1,
            "argmax_hit_l2": argmax_hit_l2,
        },
        0,
    )


def _ranks_in_mass_order(mass_rows, true_symbols):
    """1-based rank of each true symbol under mass-descending order.

    Ties break toward the smallest symbol index (the sc.py argmax
    convention) via stable descending argsort.
    """
    order = np.argsort(-np.asarray(mass_rows, dtype=np.float64), axis=1, kind="stable")
    true = np.asarray(true_symbols, dtype=np.int64).reshape(-1, 1)
    return (np.argmax(order == true, axis=1) + 1).astype(np.int64)


def _d1_cond(p1, bob, u1_true, k):
    """D1 L1 disclosure: true-u1 at the first-k natural positions, argmax
    hard-u1 elsewhere (ties to smallest index)."""
    cond = np.argmax(p1[:, np.asarray(bob)], axis=0)
    cond = np.asarray(cond, dtype=np.int64).copy()
    cond[: int(k)] = np.asarray(u1_true, dtype=np.int64)[: int(k)]
    return cond


def _bin_of_excess(e):
    if e >= 8.0:
        return "[8,inf)"
    if e >= 4.0:
        return "[4,8)"
    if e >= SPIKE_MARGIN:
        return "[2,4)"
    return "nonsplike_ref"


def _median8(h):
    out = np.empty(N, dtype=np.float64)
    for j in range(N):
        lo = j - R_MEDIAN if j - R_MEDIAN > 0 else 0
        hi = j + R_MEDIAN + 1 if j + R_MEDIAN + 1 < N else N
        out[j] = float(np.median(h[lo:hi]))
    return out


def _topk(desc_score, k):
    idx = np.lexsort(
        (np.arange(N, dtype=np.int64), -np.asarray(desc_score, dtype=np.float64))
    )
    return idx[:k]


def run_block(rng, tables, field, counters):
    """Run one N=32768 block; return per-position records + block scalars."""
    p_b = np.full(N_B, 1.0 / float(N_B), dtype=np.float64)
    bob, _, u1_true, u2_true = empirical_channel.sample_full_block(
        rng, p_b, tables["f"], Q, Q, N
    )
    counters["rng_calls"] += 2  # sample_bob + sample_full_block random draws
    p1 = tables["p1"]
    p2 = tables["p2"]
    # D1: disclosed L1 positions carry true u1; the rest use the operational
    # argmax-p1 hard-u1 path (X14 within-freeze reading kept undisclosed).
    u1_cond = _d1_cond(p1, bob, u1_true, K1_DISC)
    mass_true = p2[u1_cond, bob, u2_true]
    if not (np.isfinite(mass_true).all() and (mass_true > 0).all()):
        raise _Stop("X16_STOP_NONFINITE", "non-positive/nonfinite true-cell mass")
    h = -np.log2(mass_true)
    pm = float(np.mean(h[:K2_DISC]))  # disclosed L2 prefix (restored K)
    if not math.isfinite(pm):
        raise _Stop("X16_STOP_NONFINITE", "nonfinite prefix mean")
    excess = h - pm
    # Q1 / Q1b ranks (vectorized, sc.py tie convention).
    rank_q1 = _ranks_in_mass_order(p2[u1_cond, bob, :], u2_true)
    rank_q1b = _ranks_in_mass_order(p1[:, bob].transpose(1, 0), u1_true)
    # Q2 sole decoder use: one greedy sc_decode (L=1) on hard-u1 L2 metrics
    # with D2 disclosure conditioning (first-K2 positions forced to true u2).
    l2_rows = p2[u1_cond, bob, :]
    metric = prior.probs_to_symbol_metric(
        l2_rows,
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
    )
    known_pos = np.arange(K2_DISC, dtype=np.int64)
    known_val = np.asarray(u2_true[:K2_DISC], dtype=np.int64)
    try:
        res = sc.sc_decode(
            metric.logp,
            field=field,
            alpha=ALPHA,
            known_positions=known_pos,
            known_values=known_val,
        )
    except sc.ImpossibleDisclosedValueError as exc:
        raise _Stop("X16_STOP_IMPOSSIBLE", "disclosed truth w/o SC support: %s" % exc)
    counters["decoder_calls"] += 1
    if not np.array_equal(
        res.x_hat, transform.polar_transform(res.u_hat, field=field, alpha=ALPHA)
    ):
        raise _Stop("X16_STOP_SC_CONSISTENCY", "sc re-encode check failed")
    mismatch = res.u_hat != u2_true
    n_mm_disc = int(mismatch[:K2_DISC].sum())
    if n_mm_disc != 0:
        raise _Stop(
            "X16_STOP_NONFINITE",
            "disclosed positions mismatched (%d != 0): D2 wiring broken" % n_mm_disc,
        )
    # Q2 F-median8 detector vs mean-hazard baseline, top-K2 each.
    d = h - _median8(h)
    sel_local = set(_topk(d, K2_DISC).tolist())
    sel_base = set(_topk(h, K2_DISC).tolist())
    mm = set(np.flatnonzero(mismatch).tolist())
    return {
        "excess": excess,
        "rank_q1": rank_q1,
        "rank_q1b": rank_q1b,
        "n_mismatch": len(mm),
        "n_mm_in_local": len(mm & sel_local),
        "n_mm_in_base": len(mm & sel_base),
        "n_mm_in_disclosed": n_mm_disc,
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
            raise _Stop("X16_STOP_NONFINITE", "nonfinite pooled stat %s" % key)
    return out


def _gate_flags(mismatch_ratio, q1b_nonspike_l8_mean, spike_frac):
    """Pure sanity-gate predicates (wiring/structure checks, not verdicts).

    G1 is ONE-SIDED: pass iff mismatch_ratio < 0.75. No low-side stop.
    """
    g1 = mismatch_ratio is not None and mismatch_ratio < G1_STOP_AT
    g2 = (
        q1b_nonspike_l8_mean is not None
        and q1b_nonspike_l8_mean >= G2_MIN
    )
    g3 = spike_frac is not None and G3_LO <= spike_frac <= G3_HI
    return {"G1": bool(g1), "G2": bool(g2), "G3": bool(g3)}


def _assert_finite_tree(node, path="root"):
    if node is None:
        return
    if isinstance(node, bool):
        return
    if isinstance(node, (int, np.integer)):
        return
    if isinstance(node, (float, np.floating)):
        if not math.isfinite(float(node)):
            raise _Stop("X16_STOP_NONFINITE", "nonfinite at %s" % path)
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
    raise _Stop(
        "X16_STOP_NONFINITE", "non-scalar leaf at %s: %r" % (path, type(node))
    )


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
    raise _Stop("X16_STOP_NONFINITE", "non-plain leaf: %r" % type(node))


# --- injected self-tests (--selftest only; never write results.json) ---
def _selftest_rank_sanity():
    # X14-identical: rank-1-peaked rows + smallest-index tie-break.
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
    tables, table_rng = build_table()
    assert table_rng == 0, "deterministic table must draw no RNG"
    f_pre = tables["f_pre"]
    f = tables["f"]
    # Column sums: pre-floor exactly 1 (0.75+0.225+0.025), post exactly 1.
    assert np.allclose(f_pre.sum(axis=0), 1.0, atol=1e-12), "pre-floor col sums != 1"
    assert np.allclose(f.sum(axis=0), 1.0, atol=1e-12), "post col sums != 1"
    # Disjointness spot-checks + argmax = diagonal on every column.
    for b in (0, 1, 7, 8, 37, 100, 511, 1023):
        col, rare, neigh = _column_masses(b)
        assert len(set(rare)) == S_RARE
        assert b not in rare and b not in neigh and not (set(rare) & set(neigh))
        assert int(np.argmax(col)) == b, "argmax != diagonal at b=%d" % b
        assert int(np.argmax(f[:, b])) == b, "post-floor argmax != diagonal at b=%d" % b
    assert bool(
        (np.argmax(f, axis=0) == np.arange(N_B)).all()
    ), "post-floor argmax != diagonal somewhere"
    # Floor-hit: exactly 96/1024 planted zeros.
    rate = tables["floor_hit_measured"]
    assert rate == S_RARE / float(N_B) == 0.09375, "floor-hit != 96/1024: %r" % rate
    # Mass ledger spot-check on column 0.
    assert abs(float(f_pre[0, 0]) - 0.75) < 1e-15
    assert abs(float(f_pre[1, 0]) - NEIGH_SHARE / 8.0) < 1e-15
    assert abs(float(f_pre[37, 0]) - 0.0) < 1e-15
    print(
        "SELFTEST diagonal-smoke: PASS (colsums=1, disjoint, argmax=diag all 1024, "
        "floor-hit=%.6f=96/1024, rng=0)" % rate
    )


def _selftest_disclosure_wiring():
    # (i) exact restored-K prefix sizes live inside [0, N).
    assert K1_DISC == 334 and K2_DISC == 6746, "restored K literals wrong"
    assert 0 < K1_DISC < K2_DISC < N, "K1/K2/N ordering wrong"
    pos = np.arange(K2_DISC, dtype=np.int64)
    assert pos.shape == (K2_DISC,) and int(pos[0]) == 0 and int(pos[-1]) == K2_DISC - 1
    # (ii) D1 helper: first-k positions carry truth, rest carry argmax.
    p1_fake = np.full((Q, 6), 0.01, dtype=np.float64)
    p1_fake[5, :] = 0.9  # argmax = 5 everywhere
    bob_fake = np.zeros(6, dtype=np.int64)
    u1t_fake = np.arange(6, dtype=np.int64)  # truth 0..5, never 5 except j=5
    cond = _d1_cond(p1_fake, bob_fake, u1t_fake, 3)
    assert cond.tolist() == [0, 1, 2, 5, 5, 5], "D1 helper wiring wrong: %r" % cond
    # (iii) sc_decode accepts known_positions/known_values (exact D2 call
    # shape): all-known run returns truth exactly on a small block.
    field = algebra.make_gf32()
    n_small = 64
    rng = np.random.default_rng(2026092380)
    logp = np.asarray(rng.normal(size=(n_small, Q)), dtype=np.float64)
    truth = np.asarray(rng.integers(0, Q, size=n_small), dtype=np.int64)
    res_all = sc.sc_decode(
        logp,
        field=field,
        alpha=ALPHA,
        known_positions=np.arange(n_small, dtype=np.int64),
        known_values=truth,
    )
    assert np.array_equal(res_all.u_hat, truth), "all-known SC != truth"
    assert int(res_all.known_count) == n_small, "known_count wrong"
    # (iv) partial disclosure: disclosed positions contribute ZERO mismatches.
    k_half = n_small // 2
    res_part = sc.sc_decode(
        logp,
        field=field,
        alpha=ALPHA,
        known_positions=np.arange(k_half, dtype=np.int64),
        known_values=truth[:k_half],
    )
    mm = res_part.u_hat != truth
    assert not mm[:k_half].any(), "disclosed positions mismatched"
    print(
        "SELFTEST disclosure-wiring: PASS (K1=334/K2=6746 exact, D1 helper, "
        "all-known exact, disclosed-mismatch=0)"
    )


def _selftest_gate_asserts():
    ok = _gate_flags(0.30, 0.75, 0.10)
    assert ok == {"G1": True, "G2": True, "G3": True}, ok
    # G1 ONE-SIDED: stop iff >= 0.75 (derived ceiling ~= 0.769); no low-side stop.
    assert _gate_flags(0.75, 0.75, 0.10)["G1"] is False  # boundary stops
    assert _gate_flags(0.769, 0.75, 0.10)["G1"] is False  # ceiling stops
    assert _gate_flags(0.969, 0.75, 0.10)["G1"] is False  # X14/X15 ceiling stops
    assert _gate_flags(0.7499, 0.75, 0.10)["G1"] is True
    assert _gate_flags(0.0, 0.75, 0.10)["G1"] is True  # near-zero: informative, no stop
    assert _gate_flags(0.004, 0.75, 0.10)["G1"] is True  # low-variance note band, no stop
    assert _gate_flags(None, 0.75, 0.10)["G1"] is False
    assert _gate_flags(0.30, 0.49, 0.10)["G2"] is False
    assert _gate_flags(0.30, None, 0.10)["G2"] is False
    assert _gate_flags(0.30, 0.75, 0.019)["G3"] is False
    assert _gate_flags(0.30, 0.75, 0.701)["G3"] is False
    assert _gate_flags(0.30, 0.75, 0.02)["G3"] is True
    assert _gate_flags(0.30, 0.75, 0.70)["G3"] is True
    print("SELFTEST sanity-gate-asserts: PASS (G1 one-sided <0.75, G3 [0.02,0.70])")


def main():
    parser = argparse.ArgumentParser(prog="body.py")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        _selftest_rank_sanity()
        _selftest_diagonal_smoke()
        _selftest_disclosure_wiring()
        _selftest_gate_asserts()
        return 0

    notes = [
        "Tier-X descriptive probe only: no thresholds, no pass/fail, no verdicts; SCL stays locked whatever the numbers say.",
        "Restored operating point: N=32768 (15 levels), exact 2M disclosure literals K1=334/K2=6746, X15 0.75-diagonal channel (sharper than real => conservative).",
        "D1: u1_cond = true-u1 at the first 334 natural positions, argmax-p1 hard-u1 elsewhere (decoder-free, P20S U1hard convention kept undisclosed).",
        "D2: sc_decode receives known_positions = first 6746 natural positions with known_values = true u2 (forced-correct, mirroring real disclosed semantics); single sc_decode(L=1) per block = sole decoder use (Q2 mismatch oracle).",
        "Static order = natural order: positions iid under the model so table-marginal E[h] is position-free; pm = mean(h) over the first 6746 positions per block.",
        "Q1/Q1b per-seed fraction = survived/spike-positions pooled over the seed's 1 block; pooled = mean/sample-std(n-1)/range over 8 seeds; null when denominator is 0.",
        "Q2 per-seed coverage = selected-mismatches/mismatches pooled over the seed's 1 block (null when 0 mismatches); pooled = ratio-of-sums over all blocks plus seed mean/std/range; mismatch < 0.005 => Q2 null-with-reason while Q1/Q1b proceed.",
        "rng_calls counts Generator method calls: 0 table (deterministic per-column masses, master 2026092380 is an identity label only) + 16 block-sampling (8 blocks x 2); tag_calls = 0; zero protected opens.",
        "Measured floor-hit rate is over full f_full cells (planted-zero fraction); sampling never adjusts it.",
        "Sanity gates G1/G2/G3 are wiring/structure checks evaluated before the main question; any violation stops with X16_STOP_SANITY_* and no repair; stop payloads still carry the decoder-free scalars (G2/G3 values + calibration) for SC-path vs channel discrimination.",
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
            raise _Stop("X16_STOP_OVERSIZE", "results.json %d bytes > 2 MB" % size)
        sys.stderr.write("STOP %s: %s\n" % (status, detail))
        sys.exit(2)

    try:
        tables, table_rng_calls = build_table()
        counters = {"decoder_calls": 0, "rng_calls": int(table_rng_calls)}
        field = algebra.make_gf32()

        per_seed = {}
        for seed in BLOCK_SEEDS:
            rng = empirical_channel.make_rng(int(seed))
            surv_q1 = {b: {L: [0, 0] for L in LS} for b in BINS}
            surv_q1b = {b: {L: [0, 0] for L in LS} for b in BINS}
            spike_n = {b: 0 for b in BINS}
            mm_tot = mm_loc = mm_bas = 0
            for _ in range(BLOCKS_PER_SEED):
                blk = run_block(rng, tables, field, counters)
                for j in range(N):
                    b = _bin_of_excess(float(blk["excess"][j]))
                    spike_n[b] += 1
                    for L in LS:
                        s = surv_q1[b][L]
                        s[1] += 1
                        s[0] += 1 if int(blk["rank_q1"][j]) <= L else 0
                        t = surv_q1b[b][L]
                        t[1] += 1
                        t[0] += 1 if int(blk["rank_q1b"][j]) <= L else 0
                mm_tot += blk["n_mismatch"]
                mm_loc += blk["n_mm_in_local"]
                mm_bas += blk["n_mm_in_base"]
            seed_key = str(seed)
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
            per_seed[seed_key] = {
                "q1": q1_tab,
                "q1b": q1b_tab,
                "q2": {
                    "coverage_local_spike": (mm_loc / mm_tot) if mm_tot else None,
                    "coverage_mean_hazard": (mm_bas / mm_tot) if mm_tot else None,
                    "n_mismatch": mm_tot,
                },
                "spike_counts": dict(spike_n),
            }

        pooled_q1 = {}
        pooled_q1b = {}
        for b in BINS:
            for L in LS:
                key = "%s|L%d" % (b, L)
                pooled_q1[key] = _pooled_stats(
                    [per_seed[str(s)]["q1"][key]["frac"] for s in BLOCK_SEEDS]
                )
                pooled_q1b[key] = _pooled_stats(
                    [per_seed[str(s)]["q1b"][key]["frac"] for s in BLOCK_SEEDS]
                )
        q2_loc = [per_seed[str(s)]["q2"]["coverage_local_spike"] for s in BLOCK_SEEDS]
        q2_bas = [per_seed[str(s)]["q2"]["coverage_mean_hazard"] for s in BLOCK_SEEDS]
        mm_all = sum(per_seed[str(s)]["q2"]["n_mismatch"] for s in BLOCK_SEEDS)
        n_pos_total = len(BLOCK_SEEDS) * BLOCKS_PER_SEED * N
        pooled_q2 = {
            "local_spike_seed_stats": _pooled_stats(q2_loc),
            "mean_hazard_seed_stats": _pooled_stats(q2_bas),
            "ratio_of_sums": {
                "n_mismatch_total": mm_all,
            },
        }
        # Ratio-of-sums pooled Q2 from per-seed counts (cov*n per seed).
        loc_hit = sum(
            (per_seed[str(s)]["q2"]["coverage_local_spike"] or 0.0)
            * per_seed[str(s)]["q2"]["n_mismatch"]
            for s in BLOCK_SEEDS
        )
        bas_hit = sum(
            (per_seed[str(s)]["q2"]["coverage_mean_hazard"] or 0.0)
            * per_seed[str(s)]["q2"]["n_mismatch"]
            for s in BLOCK_SEEDS
        )
        pooled_q2["ratio_of_sums"]["coverage_local_spike"] = (
            (loc_hit / mm_all) if mm_all else None
        )
        pooled_q2["ratio_of_sums"]["coverage_mean_hazard"] = (
            (bas_hit / mm_all) if mm_all else None
        )
        pooled_spike = {
            b: sum(per_seed[str(s)]["spike_counts"][b] for s in BLOCK_SEEDS)
            for b in BINS
        }
        # Structure sanity gates BEFORE the main question (wiring checks only).
        mismatch_ratio = (mm_all / n_pos_total) if n_pos_total else None
        q1b_nonspike_l8 = pooled_q1b.get("nonsplike_ref|L8", {}).get("mean")
        n_spike_total = sum(pooled_spike[b] for b in SPIKE_BINS)
        spike_frac = (n_spike_total / n_pos_total) if n_pos_total else None
        flags = _gate_flags(mismatch_ratio, q1b_nonspike_l8, spike_frac)
        sanity_gates = {
            "G1_mismatch_ratio_of_sums": {
                "measured": mismatch_ratio,
                "stop_at_geq": G1_STOP_AT,
                "low_variance_note_below": G1_LOW_VAR,
                "pass": flags["G1"],
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
        evidence_base = {
            "probe_id": PROBE_ID,
            "tier": TIER,
            "question": "Q1/Q1b top-L true-cell survival at frozen-hazard spikes + Q2 F-median8 local-spike vs mean-hazard coverage at the restored operating point (descriptive only).",
            "frozen": {
                "N": N,
                "q": Q,
                "alpha": ALPHA,
                "gf32_poly": 37,
                "chunk_rows": CHUNK_ROWS,
                "floor": FLOOR,
                "diag_mass": DIAG_MASS,
                "n_neighbors": N_NEIGH,
                "neighbor_share": NEIGH_SHARE,
                "rest_share": REST_SHARE,
                "s_rare": S_RARE,
                "K1_disc": K1_DISC,
                "K2_disc": K2_DISC,
                "R_median": R_MEDIAN,
                "spike_margin_bits": SPIKE_MARGIN,
                "table_master_seed": MASTER_SEED,
                "block_seeds": list(BLOCK_SEEDS),
                "blocks_per_seed": BLOCKS_PER_SEED,
                "q2_detector": "F-median8: d_j = h_j - median(h over R=8 clipped natural neighborhood of j)",
                "d1": "u1_cond = true-u1 at first 334 natural positions, argmax-p1 elsewhere",
                "d2": "sc_decode(..., known_positions=arange(6746), known_values=true-u2[:6746])",
            },
            "per_seed": per_seed,
            "pooled": {
                "q1": pooled_q1,
                "q1b": pooled_q1b,
                "q2": pooled_q2,
                "spike_counts_total": pooled_spike,
            },
            "sanity_gates": sanity_gates,
            "calibration": {
                "table_f_min": tables["f_min"],
                "table_f_max": tables["f_max"],
                "model_h1_bits": tables["model_h1_bits"],
                "model_h2_bits": tables["model_h2_bits"],
                "diagonal_mass": tables["diagonal_mass"],
                "argmax_hit_l1": tables["argmax_hit_l1"],
                "argmax_hit_l2": tables["argmax_hit_l2"],
            },
            "floor_hit": {
                "measured": tables["floor_hit_measured"],
                "pin_planted": S_RARE / float(N_B),
            },
            "model_mean_hazard_bits": tables["model_mean_hazard_bits"],
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
        if not flags["G1"]:
            stop_with_evidence(
                "X16_STOP_SANITY_G1_HIGH",
                "pooled mismatch ratio-of-sums %r >= 0.75 (disclosure did not bite)" % mismatch_ratio,
                evidence_base,
            )
        if not flags["G2"]:
            stop_with_evidence(
                "X16_STOP_SANITY_G2",
                "pooled Q1b non-spike L8 mean %r < 0.50" % q1b_nonspike_l8,
                evidence_base,
            )
        if not flags["G3"]:
            stop_with_evidence(
                "X16_STOP_SANITY_G3",
                "pooled spike fraction %r outside [0.02, 0.70]" % spike_frac,
                evidence_base,
            )
        floor_pin = S_RARE / float(N_B)
        floor_recorded = 3063.0 / 32768.0
        q2_null_reason = None
        if mismatch_ratio is not None and mismatch_ratio < G1_LOW_VAR:
            q2_null_reason = (
                "low-variance note: pooled mismatch ratio-of-sums %r < 0.005 "
                "over %d positions; Q2 coverage recorded null-with-reason "
                "(DESCRIPTIVE-PASS, INFERENTIALLY VOID per X14 precedent) "
                "while Q1/Q1b proceed" % (mismatch_ratio, n_pos_total)
            )
            notes.append(q2_null_reason)
            pooled_q2["local_spike_seed_stats"] = _pooled_stats([])
            pooled_q2["mean_hazard_seed_stats"] = _pooled_stats([])
            pooled_q2["ratio_of_sums"]["coverage_local_spike"] = None
            pooled_q2["ratio_of_sums"]["coverage_mean_hazard"] = None
        pooled_q2["null_with_reason"] = q2_null_reason
        payload = dict(evidence_base)
        payload["status"] = STATUS_OK
        payload["floor_hit"] = {
            "measured": tables["floor_hit_measured"],
            "pin_planted": floor_pin,
            "recorded_real_block0": floor_recorded,
        }
        payload = _to_plain(payload)
        _assert_finite_tree(payload)
        size = _finish(payload)
        if size > 2 * 1024 * 1024:
            raise _Stop("X16_STOP_OVERSIZE", "results.json %d bytes > 2 MB" % size)
        payload["writes"] = [
            {
                "path": "workspace/probes/nbpolar_x16_synthetic_scale_disclosure/results.json",
                "size_bytes": size,
            }
        ]
        payload["wall_s"] = time.time() - T0
        _assert_finite_tree(payload)
        _finish(payload)
        print(
            "X16 probe complete: %d blocks, decoder_calls=%d rng_calls=%d "
            "floor_hit=%.6f mismatches=%d gates=%s" % (
                len(BLOCK_SEEDS) * BLOCKS_PER_SEED,
                counters["decoder_calls"],
                counters["rng_calls"],
                tables["floor_hit_measured"],
                mm_all,
                flags,
            )
        )
        return 0
    except _Stop as exc:
        # A _Stop raised before evidence_base exists (table build, prereg,
        # per-block wiring) carries no decoder-free evidence yet: emit the
        # minimal stop payload. Gate stops above already returned via
        # stop_with_evidence with full decoder-free scalars.
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
            "question": "Q1/Q1b top-L true-cell survival at frozen-hazard spikes + Q2 F-median8 local-spike vs mean-hazard coverage at the restored operating point (descriptive only).",
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
