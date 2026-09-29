"""Equivalence, oracle, CRC and timing tests for the native (Rust/C++) joint SCL.

Authorization: PI ruling 2026-09-29 ("选 B, 可以装一个cargo然后测c++和rust"),
this session (coder-fast). ``scl.py``/``sc.py``/``scl_joint.py``/``two_layer.py``/
``prior.py``/``transform.py``/``nonbinary_field.py``/``scl_joint_fast.py`` are
exercised read-only, never modified.

Equivalence standard B (PI): decisions agree with the frozen reference except at
exact metric ties, and the FER distribution on synthetic data agrees. Bit-level
rounding is NOT compared. Consequently a block whose ``label_hat`` differs from
the reference is not a failure by itself: T-N1 isolates the FIRST leaf at which
the two engines' canonical candidate lists diverge and requires the reference
score gap between the discarded/selected candidate pair at that leaf to be
<= 1e-9 relative (a tie); anything larger is FAIL. Both agreeing and tie-caused
disagreeing block counts are printed for every (N, L) point (``-s``).

Why ties are common here: rows are extremely peaked and, at undecodable
positions, two symbols can carry identical probability (e.g. 1/2 each); the
frozen reference resolves such a tie with ~1e-16 rounding noise of its own
sequential logaddexp fold, which a different (equally exact) evaluation order
cannot reproduce. The decision cascade after a flipped tie is expected and is
why T-N2 (FER equivalence on a paired block set) is the real acceptance test.

T-N1  decision equivalence, N in {64,256,1024} x L in {1,4,16}, 16 blocks each
      (N=4096 rows are opt-in slow: NBPOLAR_SCL_JOINT_NATIVE_SLOW=1).
T-N2  FER equivalence at N=4096, f~1.20 (scaled from the T6421 k1=301/k2=6120
      point), >=200 shared blocks, paired McNemar counts (opt-in slow).
T-N3  small-N brute-force ML oracle.
T-N4  CRC known vectors (CRC-16/CCITT-FALSE check value, independent bitwise
      reimplementation, and CRC-based selection of a non-top candidate).
T-N5  N=32768 timing/RSS at L in {4,8,16}, 2 blocks each (opt-in slow, run in
      the WSL timetagger venv).
Extra: whole-recursion native decoder == python-control-flow native decoder
      (same kernels) on Linux.

Fresh test-local seeds only; no protected/real data; no output files.
"""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

import numpy as np
import pytest

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import sc as sc_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl as scl_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl_joint
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl_joint_native as native
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as two_layer_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    Provenance,
    apply_explicit_floor,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform

TEST_SEED = 2026092911
Q_SYMBOL = 1024
GF32 = make_gf32()
ALPHA = 2
TIE_REL = 1e-9

SLOW = os.environ.get("NBPOLAR_SCL_JOINT_NATIVE_SLOW") == "1"
skip_unless_slow = pytest.mark.skipif(
    not SLOW, reason="opt-in: set NBPOLAR_SCL_JOINT_NATIVE_SLOW=1 (frozen reference side is slow)"
)
HAS_FULL = hasattr(native._ensure_lib(), "nbpolar_scl_decode_f64")


def _rss_mb() -> float:
    try:
        import resource

        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0  # Linux: KiB
    except ImportError:  # Windows
        return float("nan")


# --------------------------------------------------------------------------
# G1R2-matched synthetic channel (same construction as test_nbpolar_scl_joint*.py)
# --------------------------------------------------------------------------


def _g1r2_matched_table(q: int = Q_SYMBOL) -> np.ndarray:
    pmf_raw = np.zeros(q, dtype=np.float64)
    pmf_raw[0] = 0.7562
    pmf_raw[1 % q] = 0.0018
    pmf_raw[(q - 1) % q] = 0.2419
    pmf = apply_explicit_floor(pmf_raw, 1e-15, reason="G1R2-matched explicit floor (native test)")
    delta = (np.arange(q)[None, :] - np.arange(q)[:, None]) % q
    return pmf[delta]


def _sample_block(rng, n: int, table):
    q = table.shape[0]
    x = rng.integers(0, q, size=n).astype(np.int64)
    delta = rng.choice(q, size=n, p=table[0]).astype(np.int64)
    y = (x + delta) % q
    return (x >> 5).astype(np.int64), (x & 31).astype(np.int64), y.astype(np.int64)


def _make_block(rng, n, table, p1, p2, d1, d2):
    high, low, bob = _sample_block(rng, n, table)
    val1 = polar_transform(high, field=GF32, alpha=ALPHA)[d1]
    val2 = polar_transform(low, field=GF32, alpha=ALPHA)[d2]
    labels = (low + two_layer_mod.LABEL_SCALE * high).astype(np.int64)
    return dict(
        bob=bob, labels=labels, crc=scl_joint.labels_crc16(labels), d1=d1, d2=d2, val1=val1, val2=val2,
        p1=p1, p2=p2,
    )


def _kwargs(b, L, top_m=4):
    return dict(
        field=GF32, alpha=ALPHA, p1_table=b["p1"], p2_table=b["p2"],
        d1_positions=b["d1"], d1_values=b["val1"], d2_positions=b["d2"], d2_values=b["val2"],
        list_width_L=L, top_m=top_m,
    )


# --------------------------------------------------------------------------
# T-N1 tie forensics: reference-shaped recursion with pluggable kernels that
# records, per undisclosed leaf, the canonical candidate list (ids + metrics).
# --------------------------------------------------------------------------


def _leaf_trace(logp_x, known_positions, known_values, width, engine):
    q, alpha = sc_mod._check_field(GF32, ALPHA)
    metrics, n = sc_mod._validate_metric(logp_x, q)
    known = sc_mod._validate_known(known_positions, known_values, n, q)
    index = sc_mod._combination_index(GF32, alpha, q)
    mul_row = native._mul_row_table(GF32, alpha)
    cv = np.ascontiguousarray(mul_row, dtype=np.int64)
    cv_inv = np.empty(q, dtype=np.int64)
    cv_inv[cv] = np.arange(q, dtype=np.int64)

    class _P:
        __slots__ = ("prefix", "metric", "blocks")

        def __init__(self, prefix, metric, blocks):
            self.prefix, self.metric, self.blocks = prefix, metric, blocks

    live = [_P([], 0.0, [metrics])]
    trace = []

    def minus(a, b):
        if engine == "native":
            return native._minus_block_native(a, b, cv, cv_inv)
        return sc_mod._minus_block(a, b, index)

    def plus(a, b, beta):
        if engine == "native":
            return native._plus_block_native(a, b, beta, cv)
        return sc_mod._plus_block(a, b, beta, index)

    def transform(sym):
        return polar_transform(np.asarray(sym, dtype=np.int64), field=GF32, alpha=alpha)

    def decode_leaf(position):
        rows = [(path, path.blocks[-1][0]) for path in live]
        if position in known:
            value = known[position]
            survivors = []
            for path, row in rows:
                if row[value] == -np.inf:
                    continue
                path.prefix.append(value)
                survivors.append(path)
            live[:] = survivors
            return
        cp, cs, cm = [], [], []
        for pidx, (path, row) in enumerate(rows):
            for symbol in range(q):
                score = row[symbol]
                if score == -np.inf:
                    continue
                cp.append(pidx)
                cs.append(symbol)
                cm.append(path.metric + float(score))
        pa, sa, ma = np.asarray(cp), np.asarray(cs), np.asarray(cm, dtype=np.float64)
        order = np.lexsort((pa, sa, -ma))
        top = order[: width + 8]
        trace.append(
            {
                "position": position,
                "ids": [(int(pa[o]), int(sa[o])) for o in top],
                "metrics": ma[top].copy(),
                "all": {(int(pa[o]), int(sa[o])): float(ma[o]) for o in order},
            }
        )
        survivors = []
        for src in order[:width].tolist():
            parent = rows[int(pa[src])][0]
            survivors.append(_P(parent.prefix + [int(sa[src])], float(ma[src]), list(parent.blocks)))
        live[:] = survivors

    def decode_segment(offset, size):
        if size == 1:
            decode_leaf(offset)
            return
        half = size // 2
        for path in live:
            parent = path.blocks[-1]
            path.blocks.append(minus(parent[:half], parent[half:]))
        decode_segment(offset, half)
        for path in live:
            path.blocks.pop()
            parent = path.blocks[-1]
            beta = transform(path.prefix[offset : offset + half])
            path.blocks.append(plus(parent[:half], parent[half:], beta))
        decode_segment(offset + half, half)
        for path in live:
            path.blocks.pop()

    decode_segment(0, n)
    return trace


def _first_divergence_gap(logp_x, kpos, kval, width):
    """None if the canonical top-`width` lists agree at every leaf; otherwise the
    relative reference-score gap between the reference's candidate and the
    native engine's candidate at the first differing rank of the first
    diverging leaf (inf if the native candidate does not exist in the reference's
    candidate set, e.g. a support/-inf disagreement).
    """
    ref = _leaf_trace(logp_x, kpos, kval, width, "ref")
    got = _leaf_trace(logp_x, kpos, kval, width, "native")
    for r, g in zip(ref, got):
        ids_r, ids_g = r["ids"][:width], g["ids"][:width]
        if ids_r == ids_g:
            continue
        rank = next(i for i in range(len(ids_r)) if ids_r[i] != ids_g[i])
        metric_of = r["all"]  # every candidate of the reference at this leaf
        m_ref = r["metrics"][rank]
        if ids_g[rank] not in metric_of:
            return math.inf, r["position"], rank
        gap = abs(m_ref - metric_of[ids_g[rank]])
        return gap / max(1.0, abs(m_ref)), r["position"], rank
    return None


def _classify_mismatch(b, L, ref, got):
    """Return (category, rel_gap). category in {'tie', 'merge_tie', 'FAIL'}."""
    bob_row = np.asarray(b["bob"])[None, :]
    p1_probs = two_layer_mod.build_p1_metrics(bob_row, b["p1"])[0]
    p1_logp = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY).logp
    res = _first_divergence_gap(p1_logp, b["d1"], b["val1"], L)
    if res is not None:
        return ("tie" if res[0] <= TIE_REL else "FAIL"), res[0]
    l1 = scl_mod.scl_decode(
        p1_logp, field=GF32, alpha=ALPHA, known_positions=b["d1"], known_values=b["val1"],
        list_width_L=L, prune_rule=scl_joint.top_l_prune,
    )
    for rank in range(min(4, l1.survivor_count)):
        p2_probs = gather_p2_metrics(bob_row, l1.x_candidates[rank][None, :], b["p2"])[0]
        p2_logp = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED).logp
        res = _first_divergence_gap(p2_logp, b["d2"], b["val2"], L)
        if res is not None:
            return ("tie" if res[0] <= TIE_REL else "FAIL"), res[0]
    # No leaf-level divergence anywhere: the difference is in the joint merge
    # ranking; it must be a joint-metric tie.
    gap = abs(ref.joint_metric - got.joint_metric) / max(1.0, abs(ref.joint_metric))
    return ("merge_tie" if gap <= TIE_REL else "FAIL"), gap


N1_POINTS = [(64, 1), (64, 4), (64, 16), (256, 1), (256, 4), (256, 16), (1024, 1), (1024, 4), (1024, 16)]
N1_SLOW_POINTS = [(4096, 1), (4096, 4), (4096, 16)]


def _run_tn1(n, L, blocks=16):
    k1 = min(max(4, n // 20), n)
    k2 = min(max(16, n // 5), n)
    rng = np.random.default_rng([TEST_SEED, n, L])
    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    agree = tie = merge_tie = 0
    fails = []
    gaps = []
    t_ref = t_nat = 0.0
    for _ in range(blocks):
        d1 = np.sort(rng.choice(n, size=k1, replace=False)).astype(np.int64)
        d2 = np.sort(rng.choice(n, size=k2, replace=False)).astype(np.int64)
        b = _make_block(rng, n, table, p1, p2, d1, d2)
        t0 = time.perf_counter()
        ref = scl_joint.scl_joint_decode(b["bob"], b["crc"], **_kwargs(b, L))
        t1 = time.perf_counter()
        got = native.scl_joint_decode_native(b["bob"], b["crc"], **_kwargs(b, L))
        t2 = time.perf_counter()
        t_ref += t1 - t0
        t_nat += t2 - t1
        if ref.label_hat.tolist() == got.label_hat.tolist() and ref.crc_pass == got.crc_pass:
            agree += 1
            continue
        cat, gap = _classify_mismatch(b, L, ref, got)
        gaps.append(gap)
        if cat == "tie":
            tie += 1
        elif cat == "merge_tie":
            merge_tie += 1
        else:
            fails.append(gap)
    print(
        f"\n[T-N1] N={n} L={L} blocks={blocks} label_agree={agree} mismatch_tie={tie} "
        f"mismatch_merge_tie={merge_tie} mismatch_FAIL={len(fails)} "
        f"max_rel_gap={max(gaps) if gaps else 0.0:.3e} ref_s={t_ref:.1f} native_s={t_nat:.2f} "
        f"backend={native.native_backend_info()['backend']} full={HAS_FULL}"
    )
    return agree, tie, merge_tie, fails


@pytest.mark.parametrize("n,width_L", N1_POINTS)
def test_tn1_decision_equivalence(n, width_L):
    agree, tie, merge_tie, fails = _run_tn1(n, width_L)
    assert not fails, (
        f"N={n} L={width_L}: {len(fails)} mismatching blocks whose first diverging leaf "
        f"is NOT a tie (rel gaps {fails}); tie tolerance {TIE_REL}"
    )
    assert agree + tie + merge_tie == 16


@skip_unless_slow
@pytest.mark.parametrize("n,width_L", N1_SLOW_POINTS)
def test_tn1_decision_equivalence_n4096(n, width_L):
    agree, tie, merge_tie, fails = _run_tn1(n, width_L)
    assert not fails, f"N={n} L={width_L}: non-tie divergences {fails}"


# --------------------------------------------------------------------------
# Extra: whole-recursion native decoder == python-control-flow native decoder
# --------------------------------------------------------------------------


@pytest.mark.skipif(not HAS_FULL, reason="whole-recursion decoder only in the Rust library")
@pytest.mark.parametrize("width_L", [1, 4, 16])
def test_whole_recursion_equals_python_control_flow(width_L):
    n = 256
    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    rng = np.random.default_rng([TEST_SEED, 7, width_L])
    for _ in range(4):
        d1 = np.sort(rng.choice(n, size=12, replace=False)).astype(np.int64)
        b = _make_block(rng, n, table, p1, p2, d1, d1)
        logp = probs_to_symbol_metric(
            two_layer_mod.build_p1_metrics(b["bob"][None, :], p1)[0], provenance=Provenance.PRIOR_ONLY
        ).logp
        kw = dict(field=GF32, alpha=ALPHA, known_positions=d1, known_values=b["val1"], list_width_L=width_L)
        full = native._scl_decode_native(logp, **kw)
        py = native._scl_decode_native_py(logp, **kw)
        assert np.array_equal(full.u_candidates, py.u_candidates)
        assert np.array_equal(full.x_candidates, py.x_candidates)
        assert np.allclose(full.path_metrics, py.path_metrics, rtol=0, atol=1e-9)
        assert full.pruned_count == py.pruned_count
        assert full.survivor_count == py.survivor_count


# --------------------------------------------------------------------------
# T-N2: FER equivalence at N=4096, f~1.20, paired McNemar (opt-in slow)
# --------------------------------------------------------------------------

TN2_N = 4096
TN2_K1, TN2_K2 = 38, 764  # T6421 point A (k1=301, k2=6120 at N=32768) scaled by 1/8
TN2_BLOCKS = int(os.environ.get("NBPOLAR_TN2_BLOCKS", "200"))
TN2_L = int(os.environ.get("NBPOLAR_TN2_L", "16"))
TN2_DESIGN_MC = 8


def _tn2_design(table, p1, p2):
    """Genie-SC entropy design (same recipe as workspace/probes/scl-gate-t3/run.py
    ``cmd_design``) at N=4096; returns the worst-k1 / worst-k2 coordinates."""
    rng = np.random.default_rng([TEST_SEED, 8])
    n = TN2_N
    allpos = np.arange(n)
    h1 = np.zeros(n)
    h2 = np.zeros(n)
    for _ in range(TN2_DESIGN_MC):
        high, low, bob = _sample_block(rng, n, table)
        for which, sym, acc in ((1, high, h1), (2, low, h2)):
            if which == 1:
                pr0 = two_layer_mod.build_p1_metrics(bob[None, :], p1)[0]
                logp = probs_to_symbol_metric(pr0, provenance=Provenance.PRIOR_ONLY).logp
            else:
                pr0 = gather_p2_metrics(bob[None, :], high[None, :], p2)[0]
                logp = probs_to_symbol_metric(pr0, provenance=Provenance.ORACLE_CONDITIONED).logp
            r = sc_mod.sc_decode(
                logp, field=GF32, alpha=ALPHA, known_positions=allpos,
                known_values=polar_transform(sym, field=GF32, alpha=ALPHA),
            )
            pr = np.exp(r.decision_metrics)
            lg = np.log2(pr, out=np.zeros_like(pr), where=pr > 0)
            acc += -(np.where(pr > 0, pr * lg, 0.0)).sum(axis=1)
    h1 /= TN2_DESIGN_MC
    h2 /= TN2_DESIGN_MC
    d1 = np.sort(np.argsort(-h1, kind="stable")[:TN2_K1]).astype(np.int64)
    d2 = np.sort(np.argsort(-h2, kind="stable")[:TN2_K2]).astype(np.int64)
    return d1, d2


_TN2_STATE: dict = {}


def _tn2_block(idx):
    b = _make_block(
        np.random.default_rng([TEST_SEED, 9, idx]), TN2_N, _TN2_STATE["table"],
        _TN2_STATE["p1"], _TN2_STATE["p2"], _TN2_STATE["d1"], _TN2_STATE["d2"],
    )
    return b


def _tn2_summarize(b, res):
    ok = res.label_hat.tolist() == b["labels"].tolist()
    return (bool(ok), bool(res.crc_pass), bool(res.crc_pass and not ok))  # exact, crc_pass, undetected


def _tn2_ref_worker(idx):
    b = _tn2_block(idx)
    return _tn2_summarize(b, scl_joint.scl_joint_decode(b["bob"], b["crc"], **_kwargs(b, TN2_L)))


@skip_unless_slow
def test_tn2_fer_equivalence_n4096():
    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    d1, d2 = _tn2_design(table, p1, p2)
    _TN2_STATE.update(table=table, p1=p1, p2=p2, d1=d1, d2=d2)

    t0 = time.perf_counter()
    try:
        ctx = mp.get_context("fork")
        with ctx.Pool(min(16, os.cpu_count() or 1)) as pool:
            ref = pool.map(_tn2_ref_worker, range(TN2_BLOCKS), chunksize=1)
    except ValueError:  # no fork (Windows): serial
        ref = [_tn2_ref_worker(i) for i in range(TN2_BLOCKS)]
    t_ref = time.perf_counter() - t0

    t0 = time.perf_counter()
    got = []
    for i in range(TN2_BLOCKS):
        b = _tn2_block(i)
        got.append(_tn2_summarize(b, native.scl_joint_decode_native(b["bob"], b["crc"], **_kwargs(b, TN2_L))))
    t_nat = time.perf_counter() - t0

    ref_ok = np.array([r[0] for r in ref])
    got_ok = np.array([g[0] for g in got])
    b_cnt = int(np.sum(ref_ok & ~got_ok))  # ref success, native fail
    c_cnt = int(np.sum(~ref_ok & got_ok))  # ref fail, native success
    fer_ref = 1.0 - ref_ok.mean()
    fer_got = 1.0 - got_ok.mean()
    disc = b_cnt + c_cnt
    # exact two-sided McNemar (binomial) p-value
    if disc == 0:
        p_val = 1.0
    else:
        k = min(b_cnt, c_cnt)
        p_val = min(1.0, 2.0 * sum(math.comb(disc, i) for i in range(k + 1)) / 2.0**disc)
    print(
        f"\n[T-N2] N={TN2_N} L={TN2_L} blocks={TN2_BLOCKS} k1={TN2_K1} k2={TN2_K2} "
        f"FER_ref={fer_ref:.4f} ({int((~ref_ok).sum())}/{TN2_BLOCKS}) "
        f"FER_native={fer_got:.4f} ({int((~got_ok).sum())}/{TN2_BLOCKS}) "
        f"McNemar b(ref ok,nat fail)={b_cnt} c(ref fail,nat ok)={c_cnt} p={p_val:.3f} "
        f"undetected_ref={sum(r[2] for r in ref)} undetected_native={sum(g[2] for g in got)} "
        f"crc_pass_ref={sum(r[1] for r in ref)} crc_pass_native={sum(g[1] for g in got)} "
        f"ref_wall_s={t_ref:.0f} native_wall_s={t_nat:.0f}"
    )
    assert p_val > 0.01, "paired FER differs significantly (McNemar p<=0.01)"


# --------------------------------------------------------------------------
# T-N3: small-N brute-force oracle (top candidate == ML solution)
# --------------------------------------------------------------------------


def _brute_force_joint(bob, p1_logp, p2_table, field, alpha, top_k=8):
    q = field.q
    index = sc_mod._combination_index(field, alpha, q)
    u0 = np.repeat(np.arange(q), q)
    u1 = np.tile(np.arange(q), q)
    x0 = index[u0, u1]
    x1 = u1
    score1 = p1_logp[0, x0] + p1_logp[1, x1]
    high_all = np.stack([x0, x1], axis=1)
    bob_bcast = np.broadcast_to(np.asarray(bob), high_all.shape)
    p2_probs_all = gather_p2_metrics(bob_bcast, high_all, p2_table)
    metric = probs_to_symbol_metric(p2_probs_all.reshape(-1, q), provenance=Provenance.CANDIDATE_CONDITIONED)
    logp2_all = metric.logp.reshape(high_all.shape[0], 2, q)
    v0 = np.repeat(np.arange(q), q)
    v1 = np.tile(np.arange(q), q)
    y0 = index[v0, v1]
    y1 = v1
    score2_all = logp2_all[:, 0, :][:, y0] + logp2_all[:, 1, :][:, y1]
    joint = score1[:, None] + score2_all
    order = np.argsort(-joint.reshape(-1), kind="stable")[:top_k]
    out = []
    for idx in order.tolist():
        k, m = divmod(idx, joint.shape[1])
        out.append(
            (np.array([x0[k], x1[k]], dtype=np.int64), np.array([y0[m], y1[m]], dtype=np.int64),
             float(score1[k]), float(score2_all[k, m]), float(joint[k, m]))
        )
    return out


def test_tn3_small_n_enumerator_oracle():
    n = 2
    table = two_layer_mod.build_injected_joint_table(epsilon1=0.2, epsilon2=0.35)
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    q = GF32.q
    full_width = q * q
    rng = np.random.default_rng(TEST_SEED + 3)
    for _trial in range(3):
        bob = rng.integers(0, two_layer_mod.N_LABELS, size=n).astype(np.int64)
        p1_metric = probs_to_symbol_metric(
            two_layer_mod.build_p1_metrics(bob[None, :], p1)[0], provenance=Provenance.PRIOR_ONLY
        )
        brute = _brute_force_joint(bob, p1_metric.logp, p2, GF32, ALPHA)
        b_high, b_low, b_m1, b_m2, b_joint = brute[0]
        got = native.scl_joint_decode_native(
            bob, crc_true=0, field=GF32, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=None, d1_values=None, d2_positions=None, d2_values=None,
            list_width_L=full_width, top_m=full_width,
        )
        assert got.l1_survivor_count == q * q and got.top_m_used == q * q
        top = got.ranked_candidates[0]
        assert abs(top.joint_metric - b_joint) < 1e-9
        assert abs(top.m1 - b_m1) < 1e-9 and abs(top.m2 - b_m2) < 1e-9
        if abs(brute[0][4] - brute[1][4]) > 1e-9:  # unique ML solution: words must match too
            assert top.high.tolist() == b_high.tolist() and top.low.tolist() == b_low.tolist()
        joints = [c.joint_metric for c in got.ranked_candidates]
        assert all(joints[k] >= joints[k + 1] - 1e-12 for k in range(len(joints) - 1))
        # first few ranked joint metrics equal the brute-force top list
        for k in range(len(brute)):
            assert abs(joints[k] - brute[k][4]) < 1e-9


# --------------------------------------------------------------------------
# T-N4: CRC known vectors
# --------------------------------------------------------------------------


def _crc16_ccitt_false_bitwise(bits) -> int:
    """Independent bit-serial reference (poly 0x1021, init 0xFFFF, no reflect/xorout)."""
    crc = 0xFFFF
    for bit in bits:
        top = (crc >> 15) & 1
        crc = (crc << 1) & 0xFFFF
        if top ^ int(bit):
            crc ^= 0x1021
    return crc


def test_tn4_crc_check_value_and_independent_impl():
    bits = np.unpackbits(np.frombuffer(b"123456789", dtype=np.uint8), bitorder="big")
    assert scl_joint.crc16_ccitt_false_bits(bits) == 0x29B1
    assert _crc16_ccitt_false_bitwise(bits) == 0x29B1
    rng = np.random.default_rng(TEST_SEED + 4)
    for _ in range(20):
        labels = rng.integers(0, 1024, size=int(rng.integers(1, 40))).astype(np.int64)
        lbits = two_layer_mod.labels_to_bits(labels)
        assert scl_joint.labels_crc16(labels) == _crc16_ccitt_false_bitwise(lbits)
    # native re-uses the frozen CRC objects (no re-implementation)
    assert native.scl_joint_mod.crc16_ccitt_false_bits is scl_joint.crc16_ccitt_false_bits
    assert native.scl_joint_mod.labels_crc16 is scl_joint.labels_crc16


def test_tn4_native_crc_selects_non_top_candidate():
    """Full-list N=2 decode: set crc_true to the CRC of the k-th brute-force
    candidate; native must return exactly that candidate (first CRC match in
    merged joint-metric order) and report crc_pass with a matching crc_hat."""
    n = 2
    table = two_layer_mod.build_injected_joint_table(epsilon1=0.2, epsilon2=0.35)
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    q = GF32.q
    rng = np.random.default_rng(TEST_SEED + 44)
    bob = rng.integers(0, two_layer_mod.N_LABELS, size=n).astype(np.int64)
    p1_metric = probs_to_symbol_metric(
        two_layer_mod.build_p1_metrics(bob[None, :], p1)[0], provenance=Provenance.PRIOR_ONLY
    )
    brute = _brute_force_joint(bob, p1_metric.logp, p2, GF32, ALPHA, top_k=8)
    labels = [(low + two_layer_mod.LABEL_SCALE * high).astype(np.int64) for high, low, *_ in brute]
    crcs = [_crc16_ccitt_false_bitwise(two_layer_mod.labels_to_bits(lab)) for lab in labels]
    target = 3
    assert crcs[target] not in crcs[:target], "seed picked a colliding CRC; change seed"
    got = native.scl_joint_decode_native(
        bob, crc_true=crcs[target], field=GF32, alpha=ALPHA, p1_table=p1, p2_table=p2,
        list_width_L=q * q, top_m=q * q,
    )
    assert got.crc_pass and not got.crc_failed
    assert got.crc_hat == crcs[target] == got.crc_true
    assert got.label_hat.tolist() == labels[target].tolist()
    # wrong CRC (matches nothing in the list unless collision): fall back to top candidate
    bad = (crcs[0] ^ 0x1234) & 0xFFFF
    got_bad = native.scl_joint_decode_native(
        bob, crc_true=bad, field=GF32, alpha=ALPHA, p1_table=p1, p2_table=p2,
        list_width_L=q * q, top_m=q * q,
    )
    any_match = any(
        _crc16_ccitt_false_bitwise(
            two_layer_mod.labels_to_bits((c.low + two_layer_mod.LABEL_SCALE * c.high).astype(np.int64))
        ) == bad
        for c in got_bad.ranked_candidates
    )
    if not any_match:
        assert got_bad.crc_failed and not got_bad.crc_pass
        assert got_bad.label_hat.tolist() == labels[0].tolist()
    assert got.crc_bits == 16


# --------------------------------------------------------------------------
# T-N5: N=32768 timing / RSS (opt-in slow; run in the WSL timetagger venv)
# --------------------------------------------------------------------------

_T3_DESIGN = Path(__file__).resolve().parents[2] / "workspace" / "probes" / "scl-gate-t3" / "design.json"


@skip_unless_slow
@pytest.mark.parametrize("width_L", [4, 8, 16])
def test_tn5_n32768_timing(width_L):
    n = 32768
    k1, k2 = 301, 6120
    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    if _T3_DESIGN.exists():  # synthetic Tier-X design for exactly this point (A)
        pt = json.loads(_T3_DESIGN.read_text())["points"]["A"]
        d1 = np.asarray(pt["d1"], dtype=np.int64)
        d2 = np.asarray(pt["d2"], dtype=np.int64)
        design = "scl-gate-t3 point A worst-k design"
    else:
        rng0 = np.random.default_rng([TEST_SEED, 10])
        d1 = np.sort(rng0.choice(n, size=k1, replace=False)).astype(np.int64)
        d2 = np.sort(rng0.choice(n, size=k2, replace=False)).astype(np.int64)
        design = "random positions"
    walls = []
    for blk in range(2):
        rng = np.random.default_rng([TEST_SEED, 11, width_L, blk])
        b = _make_block(rng, n, table, p1, p2, d1, d2)
        t0 = time.perf_counter()
        got = native.scl_joint_decode_native(b["bob"], b["crc"], **_kwargs(b, width_L))
        walls.append(time.perf_counter() - t0)
        exact = got.label_hat.tolist() == b["labels"].tolist()
        print(
            f"\n[T-N5] N={n} L={width_L} block={blk} wall_s={walls[-1]:.2f} maxrss_MB={_rss_mb():.0f} "
            f"crc_pass={got.crc_pass} exact={exact} design='{design}' "
            f"backend={native.native_backend_info()['backend']} full={HAS_FULL} cpus={os.cpu_count()}"
        )
    print(f"[T-N5] N={n} L={width_L} wall_s per block: {walls}")
    assert all(w > 0 for w in walls)


def main():
    for fn in (test_tn3_small_n_enumerator_oracle, test_tn4_crc_check_value_and_independent_impl,
               test_tn4_native_crc_selects_non_top_candidate):
        fn()
        print(f"PASS {fn.__name__}")


if __name__ == "__main__":
    main()
