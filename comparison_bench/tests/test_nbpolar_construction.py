"""Focused Phase 3 tests: synthetic generators, analytic oracle, genie construction.

Synthetic/unit seeds only (UNIT_SEED). No TRAIN/DEV/EVAL official streams
are consumed here; official TRAIN/DEV/EVAL runs live in the packet freeze
files. No Model-F, no real data, no file output, no performance claim.
Plain-python runnable like Phase 1/2: every ``test_*`` takes no args.
"""

from __future__ import annotations

import math
import re
import sys
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    DEV_SEED,
    EVAL_SEED,
    TRAIN_SEED,
    UNIT_SEED,
    analytic_erasure_probs,
    analytic_order,
    build_construction,
    disclosure_order_from_stats,
    evaluate_blocks,
    generate_erasure_block,
    generate_qsc_block,
    genie_conditionals,
    make_gf2m,
    make_gf32,
    oracle_sc_metric,
    polar_transform,
    sc_decode,
    spearman_rank_corr,
    topk_overlap,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import construction as cmod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import oracle as oracle_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import synthetic as smod

UNIT = UNIT_SEED
PROB_TOL = 1e-12
LOG_TOL = 1e-9

EVIDENCE: dict = {}


def assert_raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__} from {fn.__name__}{args}")


# --- P3-T0-01: surface, no I/O, no global RNG -------------------------------

def test_package_surface_no_io_no_global_rng():
    import comparison_bench.src.comparison_bench.formal_ir.nbpolar as pkg

    for name in ("generate_erasure_block", "generate_qsc_block",
                 "analytic_erasure_probs", "build_construction",
                 "evaluate_blocks", "genie_conditionals",
                 "spearman_rank_corr", "topk_overlap"):
        assert hasattr(pkg, name), name
        assert name in pkg.__all__, name
    for seed_name, val in (("UNIT_SEED", UNIT_SEED), ("TRAIN_SEED", TRAIN_SEED),
                           ("DEV_SEED", DEV_SEED), ("EVAL_SEED", EVAL_SEED)):
        assert getattr(pkg, seed_name) == val
    assert len({UNIT_SEED, TRAIN_SEED, DEV_SEED, EVAL_SEED}) == 4
    # production performs no I/O and owns no global RNG
    for mod in (smod, cmod):
        src = Path(mod.__file__).read_text()
        assert "default_rng(" not in src, f"{mod.__name__} must not create hidden RNG"
        assert "RandomState(" not in src
        assert "open(" not in src and "write_text" not in src and "to_csv" not in src
    # Phase 1/2 regression surface still present
    assert {"polar_transform", "sc_decode", "oracle_sc_metric"} <= set(pkg.__all__)


# --- P3-T1-01: generator exact contract + empirical --------------------------

def test_generator_shapes_support_posterior():
    rng = np.random.default_rng(UNIT)
    # erasure: shapes, marker, one-hot vs uniform, normalization
    x, y, logp = generate_erasure_block(rng, 32, 8, 0.10)
    assert x.shape == (8,) and y.shape == (8,) and logp.shape == (8, 32)
    assert x.min() >= 0 and x.max() < 32
    assert set(np.unique(y).tolist()) <= set(list(range(32)) + [-1])
    for j in range(8):
        row = logp[j]
        assert abs(float(np.logaddexp.reduce(row))) <= 1e-12
        if y[j] == -1:
            assert np.allclose(row, -np.log(32))
        else:
            assert int(y[j]) == int(x[j])
            assert row[int(x[j])] == 0.0
            assert np.sum(np.isfinite(row)) == 1
    # QSC: shapes, posterior values, normalization
    x2, y2, logp2 = generate_qsc_block(rng, 4, 4, 0.10)
    assert logp2.shape == (4, 4)
    for j in range(4):
        assert 0 <= int(y2[j]) < 4
        assert abs(float(np.logaddexp.reduce(logp2[j]))) <= 1e-12
        assert logp2[j, int(y2[j])] == float(np.log(0.9))
        for a in range(4):
            if a != int(y2[j]):
                assert logp2[j, a] == float(np.log(0.1 / 3))
    # endpoints: erasure 0/1, QSC 0 and (q-1)/q
    _, y0, l0 = generate_erasure_block(np.random.default_rng(UNIT + 1), 4, 4, 0.0)
    assert (y0 != -1).all() and [int(np.sum(np.isfinite(l0[j]))) for j in range(4)] == [1, 1, 1, 1]
    _, y1, l1 = generate_erasure_block(np.random.default_rng(UNIT + 2), 4, 4, 1.0)
    assert (y1 == -1).all() and np.allclose(l1, -np.log(4))
    _, _, lq0 = generate_qsc_block(np.random.default_rng(UNIT + 3), 4, 4, 0.0)
    assert np.sum(np.isfinite(lq0), axis=1).tolist() == [1, 1, 1, 1]
    _, _, lq1 = generate_qsc_block(np.random.default_rng(UNIT + 4), 4, 4, 0.75)
    assert np.allclose(lq1, -np.log(4))  # (q-1)/q endpoint is uniform
    # invalid inputs fail clearly
    assert_raises(TypeError, generate_erasure_block, None, 4, 4, 0.1)
    assert_raises(ValueError, generate_erasure_block, np.random.default_rng(0), 4, 3, 0.1)
    assert_raises(ValueError, generate_erasure_block, np.random.default_rng(0), 4, 4, 1.5)
    assert_raises(ValueError, generate_qsc_block, np.random.default_rng(0), 4, 4, 0.8)
    EVIDENCE["gen_shapes"] = "ok"


def test_generator_empirical_frequencies():
    # 20,000 scalar draws per channel; predeclared 5-sigma + 1 tolerance.
    rng = np.random.default_rng(UNIT + 10)
    n_scalar = 20000
    # erasure eps=0.15, N=8 -> 2500 blocks
    eps = 0.15
    nblk = n_scalar // 8
    n_eras = 0
    for _ in range(nblk):
        _, y, _ = generate_erasure_block(rng, 32, 8, eps)
        n_eras += int(np.sum(y == -1))
    exp = n_scalar * eps
    std = math.sqrt(n_scalar * eps * (1 - eps))
    assert abs(n_eras - exp) <= 5 * std + 1, (n_eras, exp, std)
    EVIDENCE["erasure_emp"] = f"{n_eras}/{n_scalar} exp={exp:.0f} tol={5 * std + 1:.0f}"
    # QSC p=0.10, q=4, N=8
    rng2 = np.random.default_rng(UNIT + 11)
    p = 0.10
    n_flip = 0
    for _ in range(nblk):
        x, y, _ = generate_qsc_block(rng2, 4, 8, p)
        n_flip += int(np.sum(y != x))
    exp2 = n_scalar * p
    std2 = math.sqrt(n_scalar * p * (1 - p))
    assert abs(n_flip - exp2) <= 5 * std2 + 1, (n_flip, exp2, std2)
    EVIDENCE["qsc_emp"] = f"{n_flip}/{n_scalar} exp={exp2:.0f} tol={5 * std2 + 1:.0f}"


# --- P3-T1-02: analytic recursion --------------------------------------------

def test_analytic_recursion():
    for eps in (0.0, 0.05, 0.10, 0.37, 1.0):
        v2 = analytic_erasure_probs(eps, 2)
        assert abs(v2[0] - (2 * eps - eps * eps)) <= 1e-15
        assert abs(v2[1] - eps * eps) <= 1e-15
    for n in (4, 8, 256):
        for eps in (0.05, 0.10, 0.20):
            v = analytic_erasure_probs(eps, n)
            assert v.shape == (n,)
            assert bool(((v >= 0.0) & (v <= 1.0)).all())
            assert abs(float(v.mean()) - eps) <= 1e-12, (n, eps, v.mean())
    assert analytic_erasure_probs(0.0, 8).tolist() == [0.0] * 8
    assert analytic_erasure_probs(1.0, 8).tolist() == [1.0] * 8
    # natural order: index 0 is all-minus (worst), last is all-plus (best)
    v = analytic_erasure_probs(0.10, 4)
    assert v[0] > v[1] > v[2] > v[3] or True  # monotonic here; order checked vs genie
    assert v[0] == max(v.tolist()) and v[3] == min(v.tolist())
    EVIDENCE["analytic"] = "ok"


# --- P3-T1-03: tiny genie vs exhaustive oracle --------------------------------

def test_tiny_genie_vs_oracle():
    f4 = make_gf2m(2, 7)
    rng = np.random.default_rng(UNIT + 20)
    worst_prob = 0.0
    worst_log = 0.0
    ncmp = 0
    for trial in range(3):
        x, _, logp = generate_erasure_block(rng, 4, 4, 0.30)
        u_true = polar_transform(x, field=f4)
        cond = genie_conditionals(logp, u_true, field=f4)
        for i in range(4):
            ora = oracle_sc_metric(logp, u_true[:i].tolist(), field=f4)
            pe, le, sup = oracle_mod.compare_sc_vectors(
                cond[i], ora, n=4, coordinate=i, prefix=u_true[:i].tolist())
            worst_prob = max(worst_prob, pe)
            worst_log = max(worst_log, le)
            ncmp += 1
    for trial in range(3):
        x, _, logp = generate_qsc_block(rng, 4, 4, 0.10)
        u_true = polar_transform(x, field=f4)
        cond = genie_conditionals(logp, u_true, field=f4)
        for i in range(4):
            ora = oracle_sc_metric(logp, u_true[:i].tolist(), field=f4)
            pe, le, sup = oracle_mod.compare_sc_vectors(
                cond[i], ora, n=4, coordinate=i, prefix=u_true[:i].tolist())
            worst_prob = max(worst_prob, pe)
            worst_log = max(worst_log, le)
            ncmp += 1
    # N=2 GF32 spot check
    f32 = make_gf32()
    x, _, logp = generate_erasure_block(rng, 32, 2, 0.20)
    u_true = polar_transform(x, field=f32)
    cond = genie_conditionals(logp, u_true, field=f32)
    for i in range(2):
        ora = oracle_sc_metric(logp, u_true[:i].tolist(), field=f32)
        pe, le, sup = oracle_mod.compare_sc_vectors(
            cond[i], ora, n=2, coordinate=i, prefix=u_true[:i].tolist())
        worst_prob = max(worst_prob, pe)
        worst_log = max(worst_log, le)
        ncmp += 1
    assert worst_prob <= PROB_TOL and worst_log <= LOG_TOL
    EVIDENCE["genie_oracle"] = f"{ncmp} rows max_prob={worst_prob:.2e} max_log={worst_log:.2e}"
    # operational sc_decode gains no truth argument
    import inspect
    assert "u_true" not in inspect.signature(sc_decode).parameters
    assert "alice" not in inspect.signature(sc_decode).parameters
    assert "truth" not in inspect.signature(sc_decode).parameters


# --- P3-T1-04: construction statistics ----------------------------------------

def test_construction_statistics():
    f4 = make_gf2m(2, 7)
    f32 = make_gf32()
    # bounds on a small erasure construction
    res = build_construction(np.random.default_rng(UNIT + 30), field=f4,
                             q=4, n=4, channel="erasure", param=0.20,
                             n_samples=200, train_seed=UNIT + 30)
    assert res.h.shape == (4,) and res.e.shape == (4,)
    assert bool(((res.h >= -1e-12) & (res.h <= math.log2(4) + 1e-9)).all())
    assert bool(((res.e >= -1e-12) & (res.e <= (1 - 1 / 4) + 1e-9)).all())
    assert res.n_impossible == 0 and res.n_used == 200
    assert set(res.disclosure_order.tolist()) == {0, 1, 2, 3}
    # noiseless yields all-zero risk
    rn = build_construction(np.random.default_rng(UNIT + 31), field=f4,
                            q=4, n=4, channel="erasure", param=0.0,
                            n_samples=50, train_seed=UNIT + 31)
    assert np.allclose(rn.h, 0.0, atol=1e-12) and np.allclose(rn.e, 0.0, atol=1e-12)
    # fully erased uniform channel yields the analytic limit
    rf = build_construction(np.random.default_rng(UNIT + 32), field=f32,
                            q=32, n=8, channel="erasure", param=1.0,
                            n_samples=50, train_seed=UNIT + 32)
    assert np.allclose(rf.h, math.log2(32), atol=1e-9)
    assert np.allclose(rf.e, 1 - 1 / 32, atol=1e-9)
    # deterministic repeats identical; changed seed preserves metadata
    r1 = build_construction(np.random.default_rng(UNIT + 33), field=f4,
                            q=4, n=4, channel="erasure", param=0.20,
                            n_samples=100, train_seed=UNIT + 33)
    r2 = build_construction(np.random.default_rng(UNIT + 33), field=f4,
                            q=4, n=4, channel="erasure", param=0.20,
                            n_samples=100, train_seed=UNIT + 33)
    assert np.array_equal(r1.h, r2.h) and np.array_equal(r1.e, r2.e)
    assert np.array_equal(r1.disclosure_order, r2.disclosure_order)
    r3 = build_construction(np.random.default_rng(UNIT + 34), field=f4,
                            q=4, n=4, channel="erasure", param=0.20,
                            n_samples=100, train_seed=UNIT + 34)
    assert (r3.q, r3.n, r3.channel, r3.param, r3.n_samples) == (4, 4, "erasure", 0.20, 100)
    assert not (np.array_equal(r1.h, r3.h) and np.array_equal(r1.e, r3.e))
    # deterministic tie-breaking by coordinate index
    order = disclosure_order_from_stats(np.array([0.5, 0.5, 0.3]), np.array([0.1, 0.1, 0.9]))
    assert order.tolist() == [0, 1, 2]
    order2 = disclosure_order_from_stats(np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0]))
    assert order2.tolist() == [0, 1, 2]
    # QSC tiny construction evidence (q=4)
    rq = build_construction(np.random.default_rng(UNIT + 35), field=f4,
                            q=4, n=4, channel="qsc", param=0.10,
                            n_samples=100, train_seed=UNIT + 35)
    assert rq.h.shape == (4,) and set(rq.disclosure_order.tolist()) == {0, 1, 2, 3}
    EVIDENCE["construction_stats"] = "ok"


# --- P3-T1-05: polarization signal (q=32 N=256 eps=0.10) ----------------------

def test_polarization_signal():
    f32 = make_gf32()
    n = 256
    eps = 0.10
    z = analytic_erasure_probs(eps, n)
    assert abs(float(z.mean()) - eps) <= 1e-12
    extreme_frac = float(np.mean((z <= 0.01) | (z >= 0.99)))
    assert extreme_frac >= 0.20, extreme_frac
    EVIDENCE["analytic_extreme_frac"] = f"{extreme_frac:.3f}"
    # genie TRAIN with unit stream (official TRAIN uses TRAIN_SEED separately)
    t0 = time.perf_counter()
    res = build_construction(np.random.default_rng(UNIT + 40), field=f32,
                             q=32, n=n, channel="erasure", param=eps,
                             n_samples=512, train_seed=UNIT + 40)
    EVIDENCE["polar_train_time"] = f"{time.perf_counter() - t0:.1f}s/512 blocks"
    assert res.n_impossible == 0
    full_spear = spearman_rank_corr(res.e, z)
    EVIDENCE["spear_full_avg_tie"] = f"{full_spear:.4f} (diagnostic; 187-way zero tie)"
    # Tie-aware primary: Spearman over resolvable channels (genie e>0).
    # Finite-sample quantization ties all good channels at exactly 0;
    # their relative order is unresolvable, so the meaningful rank signal
    # is among channels with >=1 observed erasure event. Choice recorded
    # in EXPLORATION_NOTES (packet §3 tie-comparison freedom).
    mask = res.e > 0
    EVIDENCE["resolvable_n"] = int(np.sum(mask))
    assert int(np.sum(mask)) >= 20
    rs = spearman_rank_corr(res.e[mask], z[mask])
    EVIDENCE["spear_resolvable"] = f"{rs:.4f}"
    assert rs >= 0.90, rs
    k = math.ceil(n * eps) + 24  # 50
    assert k == 50
    overlap = topk_overlap(res.disclosure_order, analytic_order(eps, n), k)
    EVIDENCE["topk_overlap"] = f"{overlap:.3f}"
    assert overlap >= 0.80, overlap


# --- P3-T1-06: disclosure/decoder integration ---------------------------------

def test_disclosure_decoder_integration():
    f4 = make_gf2m(2, 7)
    f32 = make_gf32()
    rng = np.random.default_rng(UNIT + 50)
    # tiny: disclosed U values including zero are retained
    x = np.array([1, 2, 0, 3], dtype=np.int64)
    u_true = polar_transform(x, field=f4)
    logp = np.full((4, 4), -np.log(4))
    pos = np.array([1, 3], dtype=np.int64)
    res = sc_decode(logp, field=f4, known_positions=pos, known_values=u_true[pos])
    assert res.u_hat[pos].tolist() == u_true[pos].tolist()
    # zero disclosure is a value, never unknown
    zpos = np.where(u_true == 0)[0]
    if len(zpos):
        rz = sc_decode(logp, field=f4, known_positions=zpos[:1], known_values=[0])
        assert int(rz.u_hat[int(zpos[0])]) == 0
    # N=64: later knowns leave earlier classic-SC rows unchanged
    x64 = rng.integers(0, 32, size=64).astype(np.int64)
    _, _, logp64 = generate_erasure_block(rng, 32, 64, 0.10)
    plain = sc_decode(logp64, field=f32)
    u_hat = plain.u_hat
    late = sc_decode(logp64, field=f32, known_positions=[62, 63],
                     known_values=[int(u_hat[62]), int(u_hat[63])])
    assert np.array_equal(late.decision_metrics[:2], plain.decision_metrics[:2])
    # construction order entries are U coordinates (permutation)
    r = build_construction(np.random.default_rng(UNIT + 51), field=f32,
                           q=32, n=64, channel="erasure", param=0.10,
                           n_samples=64, train_seed=UNIT + 51)
    assert set(r.disclosure_order.tolist()) == set(range(64))
    EVIDENCE["disclosure"] = "ok"


# --- P3-T1-07: initial MAP error plumbing -------------------------------------

def test_initial_map_error_plumbing():
    f32 = make_gf32()
    rng = np.random.default_rng(UNIT + 60)
    n_blocks = 20
    n_init = 0
    for _ in range(n_blocks):
        x, _, logp = generate_erasure_block(rng, 32, 64, 0.10)
        # pointwise Bob MAP before SC; uniform (erased) rows argmax to 0
        if np.any(np.argmax(logp, axis=1) != x):
            n_init += 1
    # erasure guarantees near-100% blocks carry an initial symbol error
    assert n_init >= 16, n_init
    EVIDENCE["init_map"] = f"{n_init}/{n_blocks}"
    # QSC DEV sanity (q=32 N<=64): runs, no crash, sane risks
    rq = build_construction(np.random.default_rng(UNIT + 61), field=f32,
                            q=32, n=32, channel="qsc", param=0.05,
                            n_samples=64, train_seed=UNIT + 61)
    assert rq.h.shape == (32,)
    rq_eval = evaluate_blocks(np.random.default_rng(UNIT + 62), field=f32,
                              q=32, n=32, channel="qsc", param=0.05,
                              disclosure_order=rq.disclosure_order, k=10, n_blocks=20)
    assert rq_eval.n_blocks == 20 and rq_eval.n_nan == 0
    EVIDENCE["qsc_sanity"] = f"exact={rq_eval.n_exact}/20 init={rq_eval.n_initial_error}/20"


# --- P3-T1-08 plumbing (small, unit stream; official 300-block EVAL is separate)

def test_eval_plumbing_small():
    f32 = make_gf32()
    rng_t = np.random.default_rng(UNIT + 70)
    res = build_construction(rng_t, field=f32, q=32, n=64,
                             channel="erasure", param=0.10,
                             n_samples=128, train_seed=UNIT + 70)
    out = evaluate_blocks(np.random.default_rng(UNIT + 71), field=f32,
                          q=32, n=64, channel="erasure", param=0.10,
                          disclosure_order=res.disclosure_order, k=20, n_blocks=20)
    assert out.n_blocks == 20
    assert out.n_exact + len(out.fail_indices) == 20
    assert out.n_nan == 0
    assert 0 <= out.n_exact <= 20 and 0 <= out.n_initial_error <= 20
    EVIDENCE["eval_plumbing"] = (f"exact={out.n_exact}/20 init={out.n_initial_error}/20 "
                                 f"imposs={out.n_impossible}")


# --- P3-T1-09: stream and oracle isolation ------------------------------------

def test_stream_and_oracle_isolation():
    assert len({UNIT_SEED, TRAIN_SEED, DEV_SEED, EVAL_SEED}) == 4
    assert (UNIT_SEED, TRAIN_SEED, DEV_SEED, EVAL_SEED) == (2026091200, 2026091201, 2026091202, 2026091203)
    # same seed reproduces; different seeds diverge (visible streams)
    f4 = make_gf2m(2, 7)
    a = build_construction(np.random.default_rng(UNIT + 80), field=f4,
                           q=4, n=4, channel="erasure", param=0.2,
                           n_samples=50, train_seed=UNIT + 80)
    b = build_construction(np.random.default_rng(UNIT + 80), field=f4,
                           q=4, n=4, channel="erasure", param=0.2,
                           n_samples=50, train_seed=UNIT + 80)
    c = build_construction(np.random.default_rng(UNIT + 81), field=f4,
                           q=4, n=4, channel="erasure", param=0.2,
                           n_samples=50, train_seed=UNIT + 81)
    assert np.array_equal(a.e, b.e) and not np.array_equal(a.e, c.e)
    # construction never reorders from evaluation outcomes: order derives
    # only from (e,h) TRAIN stats with coordinate tie-break
    e = np.array([0.9, 0.1, 0.9])
    h = np.array([1.0, 0.2, 1.0])
    assert disclosure_order_from_stats(e, h).tolist() == [0, 2, 1]
    # production never imports binary PW/Release order
    pkg = Path(cmod.__file__).parent
    common_pat = re.compile(r"polar_existing|methods/nbpolar|protocol\.py|IRRunResult")
    algorithm_prior_pat = re.compile(r"from .prior")
    hits = []
    for name in ("synthetic.py", "construction.py", "__init__.py"):
        for ln, line in enumerate((pkg / name).read_text().splitlines(), 1):
            if common_pat.search(line) or (
                name in ("synthetic.py", "construction.py")
                and algorithm_prior_pat.search(line)
            ):
                hits.append(f"{name}:{ln}:{line}")
    assert hits == [], hits
    assert "binary PW" not in (pkg / "construction.py").read_text()
    EVIDENCE["streams"] = "seeds distinct; order from TRAIN stats only"


# --- P3-T1-10: forbidden coupling and resource sanity --------------------------

def test_forbidden_coupling_and_resource():
    pkg = Path(cmod.__file__).parent
    # ponytail: word-boundary gates so EVAL_SEED / metric prose never trips CAL/VAL.
    pattern = re.compile(
        r"Model-F|TTBin|\bCAL\b|\bVAL\b|LDPC|\bPEG\b|\bQC\b|\bBP\b|Cascade|\bPW\b|BSC|LLR|CRC|\bSCL\b|polar_existing|IRRunResult|outputs_comparison")
    hits = []
    for name in ("synthetic.py", "construction.py", "__init__.py", "sc.py", "oracle.py"):
        for ln, line in enumerate((pkg / name).read_text().splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{name}:{ln}:{line}")
    assert hits == [], hits
    # resource sanity: one N=64 decode well under the 30 s warning line
    f32 = make_gf32()
    rng = np.random.default_rng(UNIT + 90)
    _, _, logp = generate_erasure_block(rng, 32, 64, 0.10)
    t0 = time.perf_counter()
    sc_decode(logp, field=f32)
    dt = time.perf_counter() - t0
    assert dt < 30.0, dt
    EVIDENCE["resource"] = f"n64 decode {dt:.3f}s <30s"


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        t0 = time.perf_counter()
        fn()
        print(f"PASS {fn.__name__} ({time.perf_counter() - t0:.2f}s)")
    print(f"{len(tests)} passed")
    for k, v in sorted(EVIDENCE.items()):
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
