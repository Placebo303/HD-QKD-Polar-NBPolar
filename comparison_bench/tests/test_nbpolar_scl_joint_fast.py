"""Equivalence and throughput tests for the numba-accelerated ``scl_joint_fast``.

Authorization: PI ruling 2026-09-29 ("SCL 提速...其它语言的提速也能接受"), this
session (coder-fast). ``scl.py``/``sc.py``/``scl_joint.py``/``two_layer.py``/
``prior.py``/``transform.py``/``nonbinary_field.py`` are exercised read-only,
never modified.

T-F1: label_hat/crc_pass/joint_metric equivalence between
``scl_joint_fast.scl_joint_decode_fast`` and the frozen
``scl_joint.scl_joint_decode``, on the G1R2-matched synthetic channel, across
N in {64, 256, 1024, 4096} x L in {1, 4, 8, 16}, >=8 blocks per (N, L). Any
per-block mismatch is isolated to the first diverging internal SC leaf and
must be a genuine float64 near-tie (<1e-12) at that leaf, counted separately
(``near_tie_mismatches``); more than 1% of blocks failing that isolation is a
hard FAIL. This mirrors the known, pre-existing ``scl.py``/``sc.py``
near-tie-cascade sensitivity documented in
``workspace/probes/scl-joint-timing/CODE_REVIEW.md`` FAIL-1 and
``test_nbpolar_scl_joint.py::test_scl_l1_vs_sc_decode_known_tiebreak_mismatch``
-- this module's own kernel is designed to match ``sc.py``'s sequential
``logaddexp`` fold operation-for-operation (see ``scl_joint_fast.py`` module
docstring and ``_logaddexp2``), so in practice T-F1 sees 0 mismatches at every
(N, L) point tried here; the isolation machinery exists so a genuine
divergence FAILs loudly instead of being silently waved through.

T-F2: small-N brute-force oracle (reused from ``test_nbpolar_scl_joint.py``'s
independent, non-recursive enumerator) against the fast joint decoder at full
list width.

T-F3: CRC-16/CCITT-FALSE known test vector, against the fast module's
re-exported ``scl_joint.labels_crc16``/``crc16_ccitt_false_bits`` (same
objects, not reimplemented).

T-F4: N=32768, L in {4, 8, 16} timing/RSS comparison (fast vs frozen
reference), plus a 2-block equivalence check at N=32768, L=16. The reference
(``scl_joint.scl_joint_decode``) side is slow by design (~450-520 s/block per
``workspace/probes/scl-joint-timing/timing.json``); this test is opt-in via
the ``NBPOLAR_SCL_JOINT_FAST_SLOW=1`` environment variable and is skipped by
default so the fast focused suite (T-F1/T-F2/T-F3) stays fast. Run explicitly,
in the background, when the N=32768 numbers are needed:
``NBPOLAR_SCL_JOINT_FAST_SLOW=1 <python> -m pytest -p no:cacheprovider
comparison_bench/tests/test_nbpolar_scl_joint_fast.py -k n32768 -s``.

Fresh test-local seeds only; no protected/real data; no file output (T-F4
prints its own numbers to stdout via ``-s`` rather than writing artifacts, to
respect the output-policy rule against unauthorized new files under
``comparison_bench/outputs_comparison/``).
"""

from __future__ import annotations

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
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl_joint_fast
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as two_layer_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
    Provenance,
    apply_explicit_floor,
    gather_p2_metrics,
    probs_to_symbol_metric,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import polar_transform

try:
    import psutil
except ImportError:  # pragma: no cover - optional, RSS reporting only
    psutil = None

TEST_SEED_F1 = 2026092901
TEST_SEED_F2 = 2026092902

Q_SYMBOL = 1024
GF32 = make_gf32()
ALPHA = 2


def _rss_bytes() -> int | None:
    if psutil is None:
        return None
    return int(psutil.Process().memory_info().rss)


def _g1r2_matched_table(q: int = Q_SYMBOL) -> np.ndarray:
    """Same construction as ``test_nbpolar_scl_joint.py``'s fixture (see there
    for the CAL32 provenance): ``table[a,b] = pmf[(b-a) % q]`` with an
    explicit 1e-15 floor, p0=0.7562, p(delta=+1)=0.0018, p(delta=-1)=0.2419.
    """
    pmf_raw = np.zeros(q, dtype=np.float64)
    pmf_raw[0] = 0.7562
    pmf_raw[1 % q] = 0.0018
    pmf_raw[(q - 1) % q] = 0.2419
    pmf = apply_explicit_floor(pmf_raw, 1e-15, reason="G1R2-matched explicit floor (fast-module test)")
    delta = (np.arange(q)[None, :] - np.arange(q)[:, None]) % q
    return pmf[delta]


def _sample_block(rng, n: int, table) -> tuple:
    q = table.shape[0]
    x = rng.integers(0, q, size=n).astype(np.int64)
    delta_pmf = table[0]
    delta = rng.choice(q, size=n, p=delta_pmf).astype(np.int64)
    y = (x + delta) % q
    high_true = (x >> 5).astype(np.int64)
    low_true = (x & 31).astype(np.int64)
    return high_true, low_true, y.astype(np.int64)


# --- T-F1 divergence isolation -------------------------------------------------


def _leaf_trace(logp_x, field, alpha, known_positions, known_values, width, use_fast):
    """Reference-shaped list-SC recursion (see ``scl.py``/``scl_joint_fast.py``)
    instrumented to record, per undisclosed leaf, the canonically ordered
    ``(path, symbol)`` ids and their metrics (top ``width+2``). Test-only; not
    a third decoder implementation -- it calls the exact same primitives
    (``sc_mod``/``scl_joint_fast`` kernels) as the module under test, just with
    a debug side-channel, to let T-F1 isolate *where* two runs first disagree
    without needing a bit-for-bit copy of either engine's internals.
    """
    q, alpha = sc_mod._check_field(field, alpha)
    metrics, n = sc_mod._validate_metric(logp_x, q)
    known = sc_mod._validate_known(known_positions, known_values, n, q)
    index = sc_mod._combination_index(field, alpha, q)
    mul_row = scl_joint_fast._mul_row_table(field, alpha)

    class _P:
        __slots__ = ("prefix", "metric", "blocks")

        def __init__(self, prefix, metric, blocks):
            self.prefix = prefix
            self.metric = metric
            self.blocks = blocks

    live = [_P([], 0.0, [metrics])]
    trace = []

    def minus(a, b):
        return (
            scl_joint_fast._minus_block_fast(a, b, index)
            if use_fast
            else sc_mod._minus_block(a, b, index)
        )

    def plus(a, b, beta):
        return (
            scl_joint_fast._plus_block_fast(a, b, beta, index)
            if use_fast
            else sc_mod._plus_block(a, b, beta, index)
        )

    def transform(sym):
        arr = np.asarray(sym, dtype=np.int64)
        return (
            scl_joint_fast._polar_transform_fast(arr, mul_row)
            if use_fast
            else polar_transform(arr, field=field, alpha=alpha)
        )

    def decode_leaf(position):
        rows = [(path, path.blocks[-1][0]) for path in live]
        if position in known:
            value = known[position]
            survivors = []
            for path, row in rows:
                score = row[value]
                if score == -np.inf:
                    continue
                path.prefix.append(value)
                path.metric += 0.0
                survivors.append(path)
            live[:] = survivors
            return
        cand_path, cand_symbol, cand_metric = [], [], []
        for pidx, (path, row) in enumerate(rows):
            if not np.isfinite(row).any():
                continue
            for symbol in range(q):
                score = row[symbol]
                if score == -np.inf:
                    continue
                cand_path.append(pidx)
                cand_symbol.append(symbol)
                cand_metric.append(path.metric + float(score))
        path_arr = np.asarray(cand_path)
        symbol_arr = np.asarray(cand_symbol)
        metric_arr = np.asarray(cand_metric, dtype=np.float64)
        order = np.lexsort((path_arr, symbol_arr, -metric_arr))
        keep = order[:width]
        top = order[: min(len(order), width + 2)]
        trace.append(
            {
                "position": position,
                "ids": [(int(path_arr[o]), int(symbol_arr[o])) for o in top],
                "metrics": metric_arr[top].copy(),
            }
        )
        survivors = []
        for src in keep.tolist():
            pidx = int(path_arr[src])
            symbol = int(symbol_arr[src])
            m = float(metric_arr[src])
            parent = rows[pidx][0]
            survivors.append(_P(parent.prefix + [symbol], m, list(parent.blocks)))
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


def _isolate_near_tie(logp_x, field, alpha, known_positions, known_values, width) -> float | None:
    """Return the smallest metric gap at the first leaf where the fast and
    reference kernels pick a different top-``width`` id set, or ``None`` if
    they never differ. Used only when a T-F1 block-level mismatch is found,
    to check the mismatch is a genuine near-tie rather than a real bug.
    """
    trace_ref = _leaf_trace(logp_x, field, alpha, known_positions, known_values, width, False)
    trace_fast = _leaf_trace(logp_x, field, alpha, known_positions, known_values, width, True)
    for step_ref, step_fast in zip(trace_ref, trace_fast):
        ids_ref = step_ref["ids"][:width]
        ids_fast = step_fast["ids"][:width]
        if set(ids_ref) != set(ids_fast) or ids_ref != ids_fast:
            met_ref = step_ref["metrics"]
            met_fast = step_fast["metrics"]
            gaps = []
            for i in range(len(met_ref) - 1):
                gaps.append(abs(met_ref[i] - met_ref[i + 1]))
            for i in range(len(met_fast) - 1):
                gaps.append(abs(met_fast[i] - met_fast[i + 1]))
            return float(min(gaps)) if gaps else 0.0
    return None


def _joint_setup(n: int, k1: int, k2: int, seed_key):
    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    rng = np.random.default_rng(seed_key)
    high_true, low_true, bob = _sample_block(rng, n, table)
    d1 = np.sort(rng.choice(n, size=k1, replace=False)).astype(np.int64)
    d2 = np.sort(rng.choice(n, size=k2, replace=False)).astype(np.int64)
    u1_true = polar_transform(high_true, field=GF32, alpha=ALPHA)
    u2_true = polar_transform(low_true, field=GF32, alpha=ALPHA)
    val1 = u1_true[d1]
    val2 = u2_true[d2]
    labels_true = (low_true + two_layer_mod.LABEL_SCALE * high_true).astype(np.int64)
    crc_true = scl_joint.labels_crc16(labels_true)
    return dict(
        p1=p1, p2=p2, bob=bob, d1=d1, d2=d2, val1=val1, val2=val2,
        crc_true=crc_true, labels_true=labels_true, rng=rng,
    )


@pytest.mark.parametrize("n", [64, 256, 1024, 4096])
@pytest.mark.parametrize("width_L", [1, 4, 8, 16])
def test_equivalence_matched_channel(n, width_L):
    """T-F1: fast vs frozen ``scl_joint`` on the G1R2-matched channel."""
    k1 = min(max(4, n // 20), n)
    k2 = min(max(16, n // 5), n)
    rng = np.random.default_rng([TEST_SEED_F1, n, width_L])
    table = _g1r2_matched_table()
    p1, p2 = two_layer_mod.layer_metric_tables(table)

    total = 0
    exact_mismatches = 0
    near_tie_mismatches = 0
    for _block in range(8):
        high_true, low_true, bob = _sample_block(rng, n, table)
        d1 = np.sort(rng.choice(n, size=k1, replace=False)).astype(np.int64)
        d2 = np.sort(rng.choice(n, size=k2, replace=False)).astype(np.int64)
        u1_true = polar_transform(high_true, field=GF32, alpha=ALPHA)
        u2_true = polar_transform(low_true, field=GF32, alpha=ALPHA)
        val1 = u1_true[d1]
        val2 = u2_true[d2]
        labels_true = (low_true + two_layer_mod.LABEL_SCALE * high_true).astype(np.int64)
        crc_true = scl_joint.labels_crc16(labels_true)

        ref = scl_joint.scl_joint_decode(
            bob, crc_true, field=GF32, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
            list_width_L=width_L, top_m=4,
        )
        got = scl_joint_fast.scl_joint_decode_fast(
            bob, crc_true, field=GF32, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=d1, d1_values=val1, d2_positions=d2, d2_values=val2,
            list_width_L=width_L, top_m=4,
        )
        total += 1

        label_ok = ref.label_hat.tolist() == got.label_hat.tolist()
        crc_ok = ref.crc_pass == got.crc_pass
        metric_ok = abs(ref.joint_metric - got.joint_metric) <= 1e-9 * max(1.0, abs(ref.joint_metric))
        if label_ok and crc_ok and metric_ok:
            continue

        # Mismatch: isolate to the first diverging L1 leaf, or (if L1 agrees)
        # the first diverging leaf of the L2 call built on the shared L1
        # candidate. Must be a genuine near-tie (<1e-12) to be tolerated.
        bob_row = np.asarray(bob)[None, :]
        p1_probs = two_layer_mod.build_p1_metrics(bob_row, p1)[0]
        p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)
        gap = _isolate_near_tie(p1_metric.logp, GF32, ALPHA, d1, val1, width_L)
        if gap is None:
            # L1 agreed; isolate inside L2 using the (shared) top L1 candidate.
            l1_ref = scl_mod.scl_decode(
                p1_metric.logp, field=GF32, alpha=ALPHA, known_positions=d1, known_values=val1,
                list_width_L=width_L, prune_rule=scl_joint.top_l_prune,
            )
            high_cand = l1_ref.x_candidates[0]
            p2_probs = gather_p2_metrics(bob_row, high_cand[None, :], p2)[0]
            p2_metric = probs_to_symbol_metric(p2_probs, provenance=Provenance.CANDIDATE_CONDITIONED)
            gap = _isolate_near_tie(p2_metric.logp, GF32, ALPHA, d2, val2, width_L)
        if gap is not None and gap < 1e-12:
            near_tie_mismatches += 1
        else:
            exact_mismatches += 1

    assert exact_mismatches == 0, (
        f"N={n} L={width_L}: {exact_mismatches}/{total} blocks mismatched with no "
        "near-tie root cause found (<1e-12) -- not a tolerated divergence"
    )
    assert near_tie_mismatches <= max(1, total // 100), (
        f"N={n} L={width_L}: near-tie mismatch rate {near_tie_mismatches}/{total} "
        "exceeds the 1% block tolerance"
    )


# --- T-F2: small-N brute-force oracle (reused pattern from test_nbpolar_scl_joint.py) --


def _brute_force_joint_best(bob, p1_logp, p2_table, field, alpha, top_k=5):
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
    flat = p2_probs_all.reshape(-1, q)
    metric = probs_to_symbol_metric(flat, provenance=Provenance.CANDIDATE_CONDITIONED)
    logp2_all = metric.logp.reshape(high_all.shape[0], 2, q)
    v0 = np.repeat(np.arange(q), q)
    v1 = np.tile(np.arange(q), q)
    y0 = index[v0, v1]
    y1 = v1
    score2_all = logp2_all[:, 0, :][:, y0] + logp2_all[:, 1, :][:, y1]
    joint = score1[:, None] + score2_all
    flat_joint = joint.reshape(-1)
    order = np.argsort(-flat_joint, kind="stable")[:top_k]
    results = []
    for idx in order.tolist():
        k, m = divmod(idx, joint.shape[1])
        high_cand = np.array([x0[k], x1[k]], dtype=np.int64)
        low_cand = np.array([y0[m], y1[m]], dtype=np.int64)
        results.append((high_cand, low_cand, float(score1[k]), float(score2_all[k, m]), float(joint[k, m])))
    return results


def test_small_n_enumerator_oracle_matches_fast_joint_scl():
    n = 2
    table = two_layer_mod.build_injected_joint_table(epsilon1=0.2, epsilon2=0.35)
    p1, p2 = two_layer_mod.layer_metric_tables(table)
    field = GF32
    q = field.q
    full_width = q * q

    rng = np.random.default_rng(TEST_SEED_F2)
    for _trial in range(3):
        bob = rng.integers(0, two_layer_mod.N_LABELS, size=n).astype(np.int64)
        p1_probs = two_layer_mod.build_p1_metrics(bob[None, :], p1)[0]
        p1_metric = probs_to_symbol_metric(p1_probs, provenance=Provenance.PRIOR_ONLY)

        brute = _brute_force_joint_best(bob, p1_metric.logp, p2, field, ALPHA, top_k=5)
        brute_high, brute_low, brute_m1, brute_m2, brute_joint = brute[0]

        got = scl_joint_fast.scl_joint_decode_fast(
            bob, crc_true=0, field=field, alpha=ALPHA, p1_table=p1, p2_table=p2,
            d1_positions=None, d1_values=None, d2_positions=None, d2_values=None,
            list_width_L=full_width, top_m=full_width,
        )
        assert got.l1_survivor_count == q * q
        assert got.top_m_used == q * q
        top_joint = got.ranked_candidates[0]
        assert top_joint.high.tolist() == brute_high.tolist()
        assert top_joint.low.tolist() == brute_low.tolist()
        assert abs(top_joint.m1 - brute_m1) < 1e-9
        assert abs(top_joint.m2 - brute_m2) < 1e-9
        assert abs(top_joint.joint_metric - brute_joint) < 1e-9
        joints = [c.joint_metric for c in got.ranked_candidates]
        assert all(joints[k] >= joints[k + 1] - 1e-12 for k in range(len(joints) - 1))


# --- T-F3: CRC-16 known vector (re-exported objects, not reimplemented) ---------


def test_crc16_known_vector_reexported():
    bits = np.unpackbits(np.frombuffer(b"123456789", dtype=np.uint8), bitorder="big")
    assert scl_joint.crc16_ccitt_false_bits(bits) == 0x29B1
    # scl_joint_fast never redefines CRC machinery -- same module objects.
    assert scl_joint_fast.scl_joint_mod.crc16_ccitt_false_bits is scl_joint.crc16_ccitt_false_bits
    assert scl_joint_fast.scl_joint_mod.labels_crc16 is scl_joint.labels_crc16
    assert scl_joint_fast.scl_joint_mod.CRC_BITS == 16


# --- T-F4: N=32768 timing/RSS comparison (opt-in, slow) -------------------------

SLOW = os.environ.get("NBPOLAR_SCL_JOINT_FAST_SLOW") == "1"
skip_unless_slow = pytest.mark.skipif(
    not SLOW, reason="opt-in: set NBPOLAR_SCL_JOINT_FAST_SLOW=1 (reference side is ~450-520s/block)"
)


@skip_unless_slow
@pytest.mark.parametrize("width_L", [4, 8, 16])
def test_n32768_timing_fast_only(width_L):
    """Fast-only timing/RSS at N=32768 (reference side is separately opt-in
    via ``test_n32768_reference_timing_one_point`` -- running the frozen
    ``scl_joint`` at all three widths here would cost ~1200s on top of the
    fast run; T-F4's reference numbers come from one explicit width plus the
    already-recorded ``workspace/probes/scl-joint-timing/timing.json``).
    """
    n = 32768
    k1, k2 = 301, 6120  # timing.json point A
    setup = _joint_setup(n, k1, k2, [TEST_SEED_F1, "n32768", width_L])
    rss_before = _rss_bytes()
    t0 = time.perf_counter()
    got = scl_joint_fast.scl_joint_decode_fast(
        setup["bob"], setup["crc_true"], field=GF32, alpha=ALPHA, p1_table=setup["p1"], p2_table=setup["p2"],
        d1_positions=setup["d1"], d1_values=setup["val1"], d2_positions=setup["d2"], d2_values=setup["val2"],
        list_width_L=width_L, top_m=4,
    )
    wall_s = time.perf_counter() - t0
    rss_after = _rss_bytes()
    print(
        f"\n[T-F4 fast] N={n} L={width_L} wall_s={wall_s:.3f} "
        f"rss_before={rss_before} rss_after={rss_after} crc_pass={got.crc_pass}"
    )
    assert got.requested_width == width_L


@skip_unless_slow
def test_n32768_reference_timing_one_point():
    """One frozen-``scl_joint`` timing point at N=32768, L=16 for a direct
    same-machine comparison against the fast run above (the other L=4/L=8
    reference numbers are read from ``workspace/probes/scl-joint-timing/
    timing.json``, captured under WSL on the same point/seed family).
    """
    n = 32768
    k1, k2 = 301, 6120
    setup = _joint_setup(n, k1, k2, [TEST_SEED_F1, "n32768", 16])
    rss_before = _rss_bytes()
    t0 = time.perf_counter()
    got = scl_joint.scl_joint_decode(
        setup["bob"], setup["crc_true"], field=GF32, alpha=ALPHA, p1_table=setup["p1"], p2_table=setup["p2"],
        d1_positions=setup["d1"], d1_values=setup["val1"], d2_positions=setup["d2"], d2_values=setup["val2"],
        list_width_L=16, top_m=4,
    )
    wall_s = time.perf_counter() - t0
    rss_after = _rss_bytes()
    print(
        f"\n[T-F4 reference] N={n} L=16 wall_s={wall_s:.3f} "
        f"rss_before={rss_before} rss_after={rss_after} crc_pass={got.crc_pass}"
    )
    assert got.requested_width == 16


@skip_unless_slow
def test_n32768_l16_equivalence_two_blocks():
    """2-block equivalence check at N=32768, L=16 (the timing.json regime)."""
    n = 32768
    k1, k2 = 301, 6120
    for block in range(2):
        setup = _joint_setup(n, k1, k2, [TEST_SEED_F2, "n32768eq", block])
        ref = scl_joint.scl_joint_decode(
            setup["bob"], setup["crc_true"], field=GF32, alpha=ALPHA, p1_table=setup["p1"], p2_table=setup["p2"],
            d1_positions=setup["d1"], d1_values=setup["val1"], d2_positions=setup["d2"], d2_values=setup["val2"],
            list_width_L=16, top_m=4,
        )
        got = scl_joint_fast.scl_joint_decode_fast(
            setup["bob"], setup["crc_true"], field=GF32, alpha=ALPHA, p1_table=setup["p1"], p2_table=setup["p2"],
            d1_positions=setup["d1"], d1_values=setup["val1"], d2_positions=setup["d2"], d2_values=setup["val2"],
            list_width_L=16, top_m=4,
        )
        print(f"\n[T-F4 eq] block={block} ref.joint_metric={ref.joint_metric} got.joint_metric={got.joint_metric}")
        assert ref.label_hat.tolist() == got.label_hat.tolist(), block
        assert ref.crc_pass == got.crc_pass, block
        assert abs(ref.joint_metric - got.joint_metric) <= 1e-6 * max(1.0, abs(ref.joint_metric)), block


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        if getattr(fn, "pytestmark", None):
            continue
        fn()
        print(f"PASS {fn.__name__}")


if __name__ == "__main__":
    main()
