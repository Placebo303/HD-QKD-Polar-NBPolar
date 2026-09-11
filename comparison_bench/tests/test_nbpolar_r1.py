"""Focused Phase 3-R1 tests: tie-aware rank gate, impossible-as-failure, analytic baseline.

R1 unit stream only (R1_UNIT_SEED and small offsets). Never consumes the
R1 TRAIN/DEV/EVAL streams and never touches the frozen EVAL out root.
No Model-F, no real data, no performance claim. Plain-python runnable:
every ``test_*`` takes no args.
"""

from __future__ import annotations

import math
import re
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    BlockEvalResult,
    analytic_construction,
    analytic_erasure_probs,
    analytic_order,
    build_construction,
    disclosure_order_from_stats,
    evaluate_blocks,
    failure_summary,
    generate_erasure_block,
    make_gf2m,
    make_gf32,
    oracle_sc_metric,
    polar_transform,
    resolvable_rank_corr,
    sc_decode,
    spearman_rank_corr,
    topk_overlap,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import construction as cmod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import eval_r1 as evalmod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import oracle as oracle_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.eval_r1 import (
    BANNED_SEEDS,
    R1_DEV_SEED,
    R1_EVAL_SEED,
    R1_TRAIN_SEED,
    R1_UNIT_SEED,
    parse_order,
    run_r1_eval,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc import (
    ImpossibleDisclosedValueError,
)

UNIT = R1_UNIT_SEED

EVIDENCE: dict = {}


def assert_raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__} from {fn.__name__}{args}")


# --- R1-D1: tie-aware rank gate ------------------------------------------------

def test_resolvable_rank_helper_semantics():
    a = np.array([0.1, 0.4, 0.2, 0.9])
    z = np.array([1.0, 3.0, 2.0, 4.0])
    rho, n = resolvable_rank_corr(a, z, min_n=2)
    assert abs(rho - 1.0) <= 1e-12 and n == 4
    rho_rev, _ = resolvable_rank_corr(a[::-1], z, min_n=2)
    assert abs(rho_rev + 1.0) <= 1e-12
    # zero-tied coordinates are excluded from the resolvable set
    e = np.array([0.0, 0.0, 0.5, 0.0, 0.9])
    zz = np.array([5.0, 1.0, 2.0, 4.0, 3.0])
    rho2, n2 = resolvable_rank_corr(e, zz, min_n=2)
    assert n2 == 2 and abs(rho2 - 1.0) <= 1e-12
    # unresolvable gate fails loudly, never falls back silently
    assert_raises(ValueError, resolvable_rank_corr, e, zz, min_n=3)
    assert_raises(ValueError, resolvable_rank_corr, np.zeros(4), z)
    assert_raises(ValueError, resolvable_rank_corr, a, z[:3])
    assert_raises(ValueError, resolvable_rank_corr, a, z, min_n=True)
    assert_raises(ValueError, resolvable_rank_corr, a, z, min_n=1)
    EVIDENCE["resolvable_helper"] = "ok"


def test_quantized_tie_demo():
    # 512-sample quantization of the analytic vector: good channels tie
    # at exactly 0, so the full-vector rank is tie-dominated while the
    # resolvable subset keeps the exact monotone signal.
    z = analytic_erasure_probs(0.10, 256)
    eq = np.floor(z * 512.0) / 512.0
    n_tie0 = int(np.sum(eq == 0.0))
    assert n_tie0 >= 100, n_tie0
    rho_res, n_res = resolvable_rank_corr(eq, z)
    assert n_res >= 20 and rho_res >= 0.99, (n_res, rho_res)
    full = spearman_rank_corr(eq, z)
    EVIDENCE["quant_tie"] = f"zero_tie={n_tie0} full={full:.4f} resolvable={rho_res:.4f}/n={n_res}"


def test_r1_construction_gate_new_stream():
    f32 = make_gf32()
    res = build_construction(np.random.default_rng(UNIT), field=f32,
                             q=32, n=256, channel="erasure", param=0.10,
                             n_samples=512, train_seed=UNIT)
    assert res.n_impossible == 0
    z = analytic_erasure_probs(0.10, 256)
    rho_res, n_res = resolvable_rank_corr(res.e, z)
    assert n_res >= 20 and rho_res >= 0.90, (n_res, rho_res)
    overlap = topk_overlap(res.disclosure_order, analytic_order(0.10, 256), 50)
    assert overlap >= 0.80, overlap
    full = spearman_rank_corr(res.e, z)
    EVIDENCE["r1_gate"] = (f"resolvable={rho_res:.4f}/n={n_res} overlap={overlap:.3f} "
                           f"full_reported={full:.4f}")


# --- R1 analytic baseline -------------------------------------------------------

def test_analytic_construction_exact():
    f32 = make_gf32()
    r = analytic_construction(field=f32, q=32, n=256, channel="erasure", param=0.10)
    z = analytic_erasure_probs(0.10, 256)
    assert np.array_equal(r.disclosure_order, analytic_order(0.10, 256))
    assert set(r.disclosure_order.tolist()) == set(range(256))
    assert np.allclose(r.h, z * 5.0, atol=0.0)
    assert np.allclose(r.e, z * (31.0 / 32.0), atol=0.0)
    assert bool(((r.h >= 0.0) & (r.h <= 5.0)).all())
    assert bool(((r.e >= 0.0) & (r.e <= 31.0 / 32.0)).all())
    assert (r.n_samples, r.n_used, r.n_impossible, r.train_seed) == (0, 0, 0, -1)
    # deterministic and sampling-free: repeat identical
    r2 = analytic_construction(field=f32, q=32, n=256, channel="erasure", param=0.10)
    assert np.array_equal(r.h, r2.h) and np.array_equal(r.disclosure_order, r2.disclosure_order)
    # erasure oracle only
    assert_raises(ValueError, analytic_construction, field=f32, q=32, n=8,
                  channel="qsc", param=0.10)
    assert_raises(ValueError, analytic_construction, field=f32, q=32, n=7,
                  channel="erasure", param=0.10)
    EVIDENCE["analytic_baseline"] = "ok"


# --- R1-D2: impossible disclosure is an explicit decode-failure class ----------

def test_failure_summary_accounting():
    good = BlockEvalResult(channel="erasure", q=32, n=8, param=0.1, k=2,
                           n_blocks=10, n_exact=7, n_initial_error=9,
                           n_impossible=2, n_other_failure=1, n_nan=0,
                           fail_indices=(3, 5, 8))
    s = failure_summary(good)
    assert s["n_failed_total"] == 3  # every non-exact attempt, one total
    assert s["n_impossible"] == 2  # separate class, inside the same total
    assert s["fail_indices"] == (3, 5, 8)
    bad = BlockEvalResult(channel="erasure", q=32, n=8, param=0.1, k=2,
                          n_blocks=10, n_exact=7, n_initial_error=9,
                          n_impossible=4, n_other_failure=0, n_nan=0,
                          fail_indices=(3, 5, 8))
    assert_raises(ValueError, failure_summary, bad)  # impossible > failed
    bad2 = BlockEvalResult(channel="erasure", q=32, n=8, param=0.1, k=2,
                           n_blocks=10, n_exact=7, n_initial_error=9,
                           n_impossible=1, n_other_failure=0, n_nan=0,
                           fail_indices=(3, 5))
    assert_raises(ValueError, failure_summary, bad2)  # exact+failed != attempted
    EVIDENCE["failure_summary"] = "ok"


def test_noiseless_wrong_disclosure_is_impossible_not_numeric():
    # Deterministic category proof: noiseless channel collapses the true
    # prefix conditional to one-hot, so forcing a wrong disclosed value
    # has exact-zero support (decode failure under a wrong prefix), while
    # the true value keeps positive support (tiny-oracle rule: only
    # positive oracle support for the forced value would indict the code).
    f4 = make_gf2m(2, 7)
    rng = np.random.default_rng(UNIT + 100)
    x, _, logp = generate_erasure_block(rng, 4, 4, 0.0)
    u_true = polar_transform(x, field=f4)
    wrong = (int(u_true[0]) + 1) % 4
    try:
        sc_decode(logp, field=f4, known_positions=[0], known_values=[wrong])
    except ImpossibleDisclosedValueError:
        pass
    else:
        raise AssertionError("wrong noiseless disclosure must be impossible")
    ora = oracle_sc_metric(logp, [], field=f4)
    cond = sc_decode(logp, field=f4,
                     known_positions=[0], known_values=[int(u_true[0])]).decision_metrics
    pe, le, sup = oracle_mod.compare_sc_vectors(cond[0], ora, n=4, coordinate=0, prefix=[])
    assert sup == 0 and pe <= 1e-12
    assert ora[int(u_true[0])] == 0.0  # true value keeps full support (log score 0)
    assert ora[wrong] == -np.inf  # forced wrong value has exact-zero support
    EVIDENCE["impossible_category"] = "ok"


def test_eval_blocks_impossible_accounting_invariant():
    # Structural invariant over real SC runs: every impossible block is a
    # failed (non-exact) block and the failure summary balances, whatever
    # the sampled outcome is.
    f32 = make_gf32()
    checked = 0
    for off in range(4):
        r = build_construction(np.random.default_rng(UNIT + 200 + off), field=f32,
                               q=32, n=32, channel="erasure", param=0.15,
                               n_samples=32, train_seed=UNIT + 200 + off)
        out = evaluate_blocks(np.random.default_rng(UNIT + 210 + off), field=f32,
                              q=32, n=32, channel="erasure", param=0.15,
                              disclosure_order=r.disclosure_order, k=8, n_blocks=10)
        s = failure_summary(out)
        assert s["n_exact"] + s["n_failed_total"] == 10
        assert s["n_impossible"] <= s["n_failed_total"]
        checked += 1
    EVIDENCE["eval_invariant"] = f"{checked} small grids balance"


# --- R1 streams and eval-entry guards -------------------------------------------

def test_r1_seed_separation():
    assert len({R1_UNIT_SEED, R1_TRAIN_SEED, R1_DEV_SEED, R1_EVAL_SEED}) == 4
    assert (R1_UNIT_SEED, R1_TRAIN_SEED, R1_DEV_SEED, R1_EVAL_SEED) == (
        2026091210, 2026091211, 2026091212, 2026091213)
    assert not ({R1_UNIT_SEED, R1_TRAIN_SEED, R1_DEV_SEED, R1_EVAL_SEED} & set(BANNED_SEEDS))
    assert BANNED_SEEDS == frozenset({2026091200, 2026091201, 2026091202, 2026091203})
    EVIDENCE["r1_seeds"] = "distinct from predecessor 2026091200-1203"


def test_eval_entry_guards_and_tiny_run():
    # banned predecessor stream is refused before any RNG or file use
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "must_not_exist"
        assert_raises(ValueError, run_r1_eval, q=32, n=8, channel="erasure",
                      param=0.10, k=2, seed=2026091203,
                      order=np.arange(8), n_blocks=2, out=str(target))
        assert not target.exists()
        # non-permutation order refused with nothing written
        assert_raises(ValueError, run_r1_eval, q=32, n=8, channel="erasure",
                      param=0.10, k=2, seed=UNIT + 500,
                      order=np.zeros(8, dtype=np.int64), n_blocks=2, out=str(target))
        assert not target.exists()
        assert_raises(ValueError, parse_order, "0,1,,3")
        assert_raises(ValueError, parse_order, "0,1,x")
        # tiny end-to-end on a unit-derived stream (never the EVAL stream)
        tiny_order = disclosure_order_from_stats(
            np.array([0.5, 0.1, 0.9, 0.0, 0.3, 0.7, 0.2, 0.8]),
            np.zeros(8)).tolist()
        payload = run_r1_eval(q=32, n=8, channel="erasure", param=0.10, k=2,
                              seed=UNIT + 500, order=np.asarray(tiny_order),
                              n_blocks=2, out=str(target))
        assert payload["n_exact"] + payload["n_failed_total"] == 2
        assert (target / "eval_summary.json").exists()
        assert (target / "disclosure_order.txt").read_text().split(",").__len__() == 8
    EVIDENCE["eval_guards"] = "banned-seed and bad-order refused; tiny run ok"


def test_r1_surface_and_scope():
    import comparison_bench.src.comparison_bench.formal_ir.nbpolar as pkg

    for name in ("resolvable_rank_corr", "analytic_construction", "failure_summary"):
        assert hasattr(pkg, name), name
        assert name in pkg.__all__, name
    src = Path(evalmod.__file__).read_text()
    assert "RandomState(" not in src
    assert "default_rng(seed)" in src  # explicit caller-supplied seed only
    assert "open(" not in src  # Path.write_text only, single-shot out dir
    # scoped forbidden coupling over new/changed production files
    pattern = re.compile(
        r"Model-F|TTBin|\bCAL\b|\bVAL\b|LDPC|\bPEG\b|\bQC\b|\bBP\b|Cascade|\bPW\b|BSC|LLR|CRC|\bSCL\b|polar_existing|IRRunResult|outputs_comparison")
    hits = []
    for name in ("synthetic.py", "construction.py", "__init__.py", "eval_r1.py"):
        for ln, line in enumerate((Path(cmod.__file__).parent / name).read_text().splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{name}:{ln}:{line}")
    assert hits == [], hits
    # resource sanity retained
    f32 = make_gf32()
    rng = np.random.default_rng(UNIT + 600)
    _, _, logp = generate_erasure_block(rng, 32, 64, 0.10)
    t0 = time.perf_counter()
    sc_decode(logp, field=f32)
    assert time.perf_counter() - t0 < 30.0
    EVIDENCE["r1_scope"] = "surface+forbidden clean"


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
