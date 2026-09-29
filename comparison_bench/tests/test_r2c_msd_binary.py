"""R2C strongest-binary arm: T0-T3 tests (contract §11), SYNTHETIC data only.

Run (WSL; no pytest in the project venv, so borrow the pure-python pytest from
the timetagger venv by *appending* its site-packages so numpy/numba stay the
project-venv versions)::

    cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar
    /home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python -c "import sys; \
sys.path.append('/home/karel_303/.venvs/timetagger/lib/python3.12/site-packages'); \
import pytest; sys.exit(pytest.main(['-p','no:cacheprovider','comparison_bench/tests/test_r2c_msd_binary.py','-x','-q']))"

Also runnable with plain ``python`` (every ``test_*`` takes no arguments).
Heavy timing tests (N=32768, L=16) run only with ``R2C_HEAVY=1``.
No real data: no ttbin, no CAL32, no lab ``data/`` slice, no results/ read
other than the ``workspace/r2_fer_shg_64/part_*.json`` NB pairing fixture
being replaced by a tiny temporary fake.  Lab repository is read-only: all
writes go to ``workspace/r2c_test_runs/`` (additive uuid dirs).
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
import itertools
import json
import math
import os
import sys
import textwrap
import uuid
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
MOD_PATH = REPO / "comparison_bench" / "src" / "comparison_bench" / "formal_ir" / "nbpolar" / "r2c_msd_binary.py"
PM2_PATH = REPO / "comparison_bench" / "src" / "comparison_bench" / "formal_ir" / "prior_m2.py"
VERIF_PATH = REPO / "src" / "reconciliation" / "verification.py"
TEST_ROOT = REPO / "workspace" / "r2c_test_runs"
LAB_ROOT = Path("/mnt/d/Code/qkd-reconciliation-lab")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m = _load("r2c_msd_binary_under_test", MOD_PATH)
_LAB = {}


def lab():
    if "lab" not in _LAB:
        _LAB["snap0"] = m.lab_snapshot(LAB_ROOT)
        _LAB["lab"] = m.load_lab(TEST_ROOT / "stage", str(LAB_ROOT / "src"))
    return _LAB["lab"]


def fresh_dir() -> Path:
    p = TEST_ROOT / uuid.uuid4().hex
    p.mkdir(parents=True, exist_ok=True)
    return p


# --------------------------------------------------------------------------- #
# Synthetic circulant channel
# --------------------------------------------------------------------------- #
def synth_pmf(d: int) -> np.ndarray:
    p = np.full(d, 1e-4)
    p[0] = 0.78
    for s, v in ((1, 0.08), (2, 0.02), (3, 0.005)):
        p[s % d] = v
        p[(-s) % d] = v
    return p / p.sum()


def entropy_bits(p: np.ndarray) -> float:
    return float(-(p * np.log2(p)).sum())


def sample_pairs(rng, pmf, size):
    d = pmf.size
    a = rng.integers(0, d, size=size)
    cdf = np.cumsum(pmf)
    cdf[-1] = 1.0
    dl = np.minimum(np.searchsorted(cdf, rng.random(size)), d - 1)
    return a, (a + dl) % d


def make_session(name, idx, d, n_log, seed, *, n_cal=8192, n_blocks=3, poison=False, f_nb=1.4):
    rng = np.random.default_rng(seed)
    pmf = synth_pmf(d)
    n = 1 << n_log
    fp = n // 128
    cal_a, cal_b = sample_pairs(rng, pmf, n_cal)
    nf = n_blocks * 128
    fa, fb = sample_pairs(rng if not poison else np.random.default_rng(seed + 999), pmf, (nf, fp))
    strata_o = ("A1_CAL_characterization", "HELDOUT_model_selection", "EVAL_already_decoded")
    strata_t = ("never_decoded", "heldout_model_selection", "previously_decoded_eval")
    blocks = [{"session": name, "local_index": i, "global_block_index": idx * 100 + i, "frame_start": i * 128, "frame_end": i * 128 + 127,
               "stratum_official": strata_o[i % 3], "stratum_task": strata_t[i % 3]} for i in range(n_blocks)]
    return m.SessionInput(name=name, idx=idx, cal_a=cal_a, cal_b=cal_b, h_total_bits=entropy_bits(pmf), f_nb=f_nb,
                          frames_a=fa, frames_b=fb, blocks=blocks), pmf


def small_cfg(**kw):
    base = dict(n_log=10, d=64, list_size=8, m_design=16, m_root=512, de_samples=128, f3_bracket=(1.05, 2.2),
                n_workers=1, de_workers=1, design_chunk=8, wall_total_s=600.0)
    base.update(kw)
    return m.RunConfig(**base)


def tag_fn_factory():
    v = _load("verif_under_test", VERIF_PATH)

    def tag_fn(bits, block_index):
        return v.universal_hash_tag(bits=bits, point_id="r2c-test", layer_id=0, block_index=int(block_index), tag_bits=64)
    return tag_fn


# =========================================================================== #
# T0
# =========================================================================== #
def test_T0a_lab_import_stage_build_and_lab_untouched():
    L = lab()
    assert Path(L.lib).resolve().parent.parent == (TEST_ROOT / "stage").resolve()
    assert str(L.scl.CPP_DIR).startswith(str(TEST_ROOT.resolve()))
    snap1 = m.lab_snapshot(LAB_ROOT)
    assert m.snapshots_equal(_LAB["snap0"], snap1), "lab git status / src files changed"
    prov = m.lab_used_files_provenance(LAB_ROOT)
    assert len(prov) == 5 and all(p["git_diff_quiet"] for p in prov), prov


def test_T0b_m2_pmf_matches_prior_m2_joint_and_is_circulant():
    L = lab()
    pm2 = _load("prior_m2_under_test", PM2_PATH)
    d = 1024
    rng = np.random.default_rng(7)
    a, b = sample_pairs(rng, synth_pmf(d), 8192)
    counts = m.joint_from_symbols(a, b, d)
    trip = pm2.fit_m2_triple(counts, mod="CIRCULAR")
    joint = pm2.build_m2_joint(trip["q0"], trip["q_plus1"], trip["q_minus1"], mod="CIRCULAR")
    # circulant structure: joint[a,b] depends only on (b-a) mod d
    idx = m.np.arange(d)
    delta = (idx[None, :] - idx[:, None]) % d
    for dl in (0, 1, d - 1, 2, 500):
        vals = joint[delta == dl]
        assert np.allclose(vals, vals[0], rtol=0, atol=1e-13), dl
    p_fit = L.msd.difference_pmf(joint, d)
    p_gen = m.m2_pmf(m.delta_counts(a, b, d), d)
    assert np.max(np.abs(p_fit - p_gen)) < 1e-12
    assert abs(p_gen.sum() - 1.0) < 1e-12


def test_T0d_conventions_bitplanes_prefix_llr_sign():
    L = lab()
    d, layers = 8, 3
    sym = np.arange(8)
    assert plane_msb_ok(sym, layers)
    # prefix_from_bits is MSB first
    planes = [np.array([1, 0]), np.array([0, 1]), np.array([1, 1])]
    assert list(L.msd.prefix_from_bits(planes, 3)) == [0b101, 0b011]
    assert list(L.msd.prefix_from_bits(planes, 2)) == [0b10, 0b01]
    assert list(m.bits_to_symbols(planes)) == [0b101, 0b011]
    # LLR sign vs numpy hand computation from the raw joint (alpha=0 -> exact ratio)
    rng = np.random.default_rng(3)
    counts = rng.integers(1, 50, size=(d, d)).astype(np.float64)
    tables = L.msd.build_msd_llr_tables(counts, d, smoothing=0.0, clip=1e9)
    for layer in range(layers):
        for b in range(d):
            for v in range(1 << layer):
                lo = v << (layers - layer)  # symbols with prefix v, then bit 0/1
                half = 1 << (layers - layer - 1)
                p0 = counts[lo:lo + half, b].sum()
                p1 = counts[lo + half:lo + 2 * half, b].sum()
                got = float(L.msd.conditional_llr(tables, layer, np.array([b]), np.array([v]))[0])
                assert abs(got - math.log(p0 / p1)) < 1e-9
                assert (got > 0) == (p0 > p1)  # LLR > 0  <=>  bit 0 more likely


def plane_msb_ok(sym, layers):
    return all(list(m.plane_bits(sym, i, layers)) == [(s >> (layers - 1 - i)) & 1 for s in sym] for i in range(layers))


def test_T0c_n32768_l16_single_codeword_timing_heavy():
    if os.environ.get("R2C_HEAVY") != "1":
        return
    import time
    L = lab()
    cfg = m.RunConfig()
    d, n = cfg.d, cfg.n
    pmf = synth_pmf(d)
    dcounts = pmf * 8192
    ch = m.build_channel(L, "P-M2", dcounts, d)
    rng = np.random.default_rng(1)
    a, b = sample_pairs(rng, pmf, n)
    layer = 8
    k = int(m.layer_ks(ch["caps"], 0.02, n)[layer])
    dec = L.scl.MsdSclDecoder()
    x = m.plane_bits(a, layer, 10)
    llr = ch["tables"].llr[layer][a >> (10 - layer), b]
    for label, order in (("PW reliable order", L.polar.reliable_order(n)), ("random order (worst-case timing)", rng.permutation(n))):
        m.decode_layer(L, dec, llr, order, k, x, 15, 16)  # warm
        t0 = time.perf_counter()
        xh, _ = m.decode_layer(L, dec, llr, order, k, x, 15, 16)
        dt = time.perf_counter() - t0
        print(f"T0c: N=32768 L=16 k={k} [{label}] single codeword {dt:.3f}s ok={np.array_equal(xh, x)} peak_rss_gib={m._peak_rss_gib():.3f}")
    assert dt < 30.0  # worst-case (random order) single-codeword wall


# =========================================================================== #
# T1
# =========================================================================== #
def _inc(l, u):
    s = (1 - 2 * u) * l
    return math.log1p(math.exp(-s)) if s >= 0 else -s + math.log1p(math.exp(s))


def _sc_pm(llr, u):
    """Min-sum SC path metric of a fully specified u (independent reference of the engine's semantics)."""
    n = len(llr)
    if n == 1:
        return _inc(llr[0], int(u[0])), np.array([int(u[0])])
    h = n // 2
    l1, l2 = llr[:h], llr[h:]
    f = np.sign(l1) * np.sign(l2) * np.minimum(np.abs(l1), np.abs(l2))
    pl, xl = _sc_pm(f, u[:h])
    g = l2 + (1 - 2 * xl) * l1
    pr, xr = _sc_pm(g, u[h:])
    return pl + pr, np.concatenate([xl ^ xr, xr])


def test_T1a_full_list_scl_equals_exhaustive_search_and_matches_numba_reference():
    """L >= 2^k: engine == exhaustive minimum of the engine's own (min-sum) path metric, pm equal.
    Exact-ML agreement is NOT asserted (the lab engine's f-node is min-sum, msd_scl.cpp:15); it is reported."""
    L = lab()
    dec = L.scl.MsdSclDecoder()
    rng = np.random.default_rng(1)
    n_cases = agree_ms = agree_ml = 0
    max_pm_err = 0.0
    for n_log in (3, 4):
        n = 1 << n_log
        for _ in range(40):
            k = int(rng.integers(1, min(8, n) + 1))
            info = np.sort(rng.choice(n, k, replace=False))
            mask = np.zeros(n, np.uint8)
            mask[info] = 1
            x_true = rng.integers(0, 2, n).astype(np.int8)
            llr = rng.normal(0, 2.0, n).astype(np.float32)
            u_true = m.encode(L, x_true, n_log)
            frozen = (u_true * (1 - mask.astype(np.int8))).astype(np.uint8)
            uh, pm, _ = dec.decode_batch(llr.reshape(1, -1), mask, frozen.reshape(1, -1), n_log, 1 << k)
            l64 = llr.astype(np.float64)
            best_ms = best_ml = None
            for bits in itertools.product([0, 1], repeat=k):
                u = u_true.astype(np.int64).copy()
                u[info] = bits
                pmv, x = _sc_pm(l64, u)
                if best_ms is None or pmv < best_ms[0]:
                    best_ms = (pmv, u.copy())
                ml = sum(_inc(l64[j], int(x[j])) for j in range(n))
                if best_ml is None or ml < best_ml[0]:
                    best_ml = (ml, u.copy())
            n_cases += 1
            agree_ms += int(np.array_equal(uh[0], best_ms[1]))
            agree_ml += int(np.array_equal(uh[0], best_ml[1]))
            max_pm_err = max(max_pm_err, abs(float(pm[0]) - best_ms[0]))
            # numba reference (same semantics), L=16, bit-exact
            ref = L.polar.scl_decode_batch(l64.reshape(1, -1), mask, frozen.reshape(1, -1), n_log, 16)
            uh16, _, _ = dec.decode_batch(llr.reshape(1, -1), mask, frozen.reshape(1, -1), n_log, 16)
            assert np.array_equal(ref[0].astype(np.int8), uh16[0]), (n_log, k)
    print(f"T1a: engine==min-sum exhaustive {agree_ms}/{n_cases}, ==exact-ML {agree_ml}/{n_cases}, max|pm err|={max_pm_err:.2e}")
    assert agree_ms == n_cases
    assert max_pm_err < 1e-3
    assert agree_ml >= 0.8 * n_cases


def test_T1a2_numba_reference_larger_n_bit_exact():
    L = lab()
    dec = L.scl.MsdSclDecoder()
    rng = np.random.default_rng(11)
    n_log, n = 8, 256
    for _ in range(4):
        k = 100
        order = rng.permutation(n)
        mask = L.polar.info_mask_from_order(order, k, n)
        x = rng.integers(0, 2, n).astype(np.int8)
        llr = (rng.normal(0, 1.0, n) + 1.2 * (1 - 2 * x)).astype(np.float32)
        u = m.encode(L, x, n_log)
        frozen = (u * (1 - mask.astype(np.int8))).astype(np.uint8)
        a = dec.decode_batch(llr.reshape(1, -1), mask, frozen.reshape(1, -1), n_log, 16)[0][0]
        b = L.polar.scl_decode_batch(llr.astype(np.float64).reshape(1, -1), mask, frozen.reshape(1, -1), n_log, 16)[0]
        assert np.array_equal(a, b.astype(np.int8))


def test_T1b_zero_frozen_values_fail_true_frozen_values_succeed():
    L = lab()
    dec = L.scl.MsdSclDecoder()
    rng = np.random.default_rng(5)
    n_log, n, k = 10, 1024, 300
    order = L.polar.reliable_order(n)
    mask = L.polar.info_mask_from_order(order, k, n)
    n_fail_zero = n_fail_true = 0
    for _ in range(6):
        x = rng.integers(0, 2, n).astype(np.int8)
        llr = (rng.normal(0, 1.0, n) + 3.0 * (1 - 2 * x)).astype(np.float32)  # easy channel
        u = m.encode(L, x, n_log)
        good = (u * (1 - mask.astype(np.int8))).astype(np.uint8)
        zero = np.zeros(n, np.uint8)
        xh_t = m.encode(L, dec.decode_batch(llr.reshape(1, -1), mask, good.reshape(1, -1), n_log, 8)[0][0], n_log)
        xh_z = m.encode(L, dec.decode_batch(llr.reshape(1, -1), mask, zero.reshape(1, -1), n_log, 8)[0][0], n_log)
        n_fail_true += int(not np.array_equal(xh_t, x))
        n_fail_zero += int(not np.array_equal(xh_z, x))
        # decode_layer must ignore whatever sits on info positions of the frozen vector
        xh_w, _ = m.decode_layer(L, dec, llr, order, k, x, n_log, 8)
        assert np.array_equal(xh_w, xh_t)
    assert n_fail_true == 0 and n_fail_zero == 6, (n_fail_true, n_fail_zero)


def test_T1c_rate_allocation_and_f_accounting():
    n = 32768
    caps = np.array([0.999, 0.99, 0.97, 0.9, 0.7, 0.5, 0.3, 0.1, 0.02, 0.005])
    # hand check for mu = 0.02
    mu = 0.02
    ks = m.layer_ks(caps, mu, n)
    hand = [int(math.floor(n * max(0.0, c - mu))) for c in caps]
    hand = [0 if k < 16 else k for k in hand]
    assert list(ks) == hand
    assert ks[-1] == 0 and ks[-2] == 0  # caps <= mu -> 0 ; whole layer disclosed
    kf = sum(n - k for k in hand)
    assert m.k_frozen(ks, n) == kf
    h = 0.8168138204133305
    assert abs(m.f_of_ks(ks, n, h) - (kf + 64) / (h * n)) < 1e-15
    # k < MIN_K -> whole-layer disclosure
    caps2 = np.array([0.0004, 0.00045])  # 32768*0.0004=13 <16
    assert list(m.layer_ks(caps2, 0.0, n)) == [0, 0]
    assert m.k_frozen(m.layer_ks(caps2, 0.0, n), n) == 2 * n
    # monotone K_frozen(mu) and bisection
    mus = np.linspace(0, 1.0, 400)
    kfs = [m.k_frozen(m.layer_ks(caps, x, n), n) for x in mus]
    assert all(b >= a for a, b in zip(kfs, kfs[1:]))
    for target in (7.5, 9.0, 11.0, 12.0):
        mu_s = m.solve_mu_for_f(caps, target, n, h)
        f_hi = m.f_of_mu(caps, mu_s, n, h)
        assert f_hi >= target
        assert m.f_of_mu(caps, max(0.0, mu_s - 1e-6), n, h) <= f_hi
        assert f_hi - target < 5e-3  # one step
    # bound
    try:
        m.solve_mu_for_f(caps, 1e6, n, h)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_T1d_de_root_sign_alignment_bsc_consistency():
    """root path with a BSC-equivalent root == de_llr_populations: pre-registered thresholds
    (top-N/2 reliable-set overlap >= 0.85 and >= (self-seed overlap - 0.10))."""
    L = lab()
    n_log, ber = 8, 0.11
    n = 1 << n_log
    lam = math.log((1 - ber) / ber)
    rng = np.random.default_rng(0)
    root = np.where(rng.random(4096) < ber, -lam, lam)  # symbol-aligned (all-zero codeword)
    pop_root = L.de.de_llr_populations_from_root(root, n_log, n_samples=2048, seed=20260929)
    pop_bsc = L.de.de_llr_populations(n_log, ber, n_samples=2048, seed=20260929)
    pop_bsc2 = L.de.de_llr_populations(n_log, ber, n_samples=2048, seed=1)
    o_root = L.de.de_order_from_population(pop_root)
    o_bsc = L.de.de_order_from_population(pop_bsc)
    o_bsc2 = L.de.de_order_from_population(pop_bsc2)
    ov = m.info_set_overlap(o_root, o_bsc, n // 2)
    ov_self = m.info_set_overlap(o_bsc, o_bsc2, n // 2)
    print(f"T1d: overlap root-vs-bsc={ov:.3f} bsc-vs-bsc(seed)={ov_self:.3f}")
    assert ov >= 0.85 and ov >= ov_self - 0.10
    pe_root = np.mean(pop_root < 0, axis=1)
    pe_bsc = np.mean(pop_bsc < 0, axis=1)
    assert np.mean(pop_root) > 0 and np.mean(pop_bsc) > 0
    assert abs(pe_root.mean() - pe_bsc.mean()) < 0.02
    # aligned-LLR builder: sign convention  L*(1-2a)  (layer-0 of a clean channel -> mostly positive)
    d, layers = 8, 3
    counts = np.diag(np.full(d, 100.0)) + 1.0
    tables = L.msd.build_msd_llr_tables(counts, d, smoothing=0.0)
    pmf = np.full(d, 0.0) + 0.0
    pmf[0] = 0.95
    pmf[1:] = 0.05 / (d - 1)
    r = m.de_root_llr(tables, pmf, 2, d, layers, m_root=4000, seed=1)
    assert (r > 0).mean() > 0.9


# =========================================================================== #
# T2
# =========================================================================== #
def test_T2a_small_end_to_end_accounting_and_consistency():
    L = lab()
    d, n_log = 64, 10
    cfg = small_cfg(d=d, n_log=n_log)
    s1, pmf = make_session("G2", 0, d, n_log, seed=101, n_blocks=4)
    s2, _ = make_session("G3", 1, d, n_log, seed=202, n_blocks=4, f_nb=1.5)
    out = fresh_dir() / "run"
    res = m.run_pipeline(L, cfg, [s1, s2], out, tag_fn_factory())
    assert res["block_accounting"]["consistent"] and res["block_accounting"]["n_expected_block_points"] == 2 * 4 * 4
    n = cfg.n
    for s in (s1, s2):
        con = json.loads((out / f"construction_frozen_{s.name}.json").read_text())
        assert con["invariance"]["compatible"]
        caps = np.array(con["channel"]["caps"])
        # chain-rule identity: layers - sum(caps) == H(delta) of the effective pmf (exact); the contract-7
        # H_total comparison (tolerance 0.03 bit on real data) is only reported, see caps_consistency.
        assert abs(con["caps_consistency"]["layers_minus_sum_caps"] - con["channel"]["pmf_entropy_bits"]) < 1e-9
        assert abs(con["caps_consistency"]["diff_bits"]) < 0.15, con["caps_consistency"]
        for lab_ in m.POINT_LABELS:
            p = res["per_point"][lab_]["per_session"][s.name]
            ks = np.array(p["ks"])
            hand_f = (sum(n - int(k) for k in ks) + 64) / (s.h_total_bits * n)  # hand formula
            assert abs(p["f_realized"] - hand_f) < 1e-12
            assert p["K_frozen"] == sum(n - int(k) for k in ks)
            # k only from caps and mu
            mu = con["points"][lab_]["mu"]
            assert list(m.layer_ks(caps, mu, n)) == list(ks)
        f = [res["per_point"][l]["per_session"][s.name]["f_realized"] for l in m.POINT_LABELS]
        assert f[0] < f[1] + 0.2 and f[3] > f[2]  # F4 = F3 + 0.10 (grid step)
        assert abs((f[3] - f[2]) - 0.10) < 0.02
    # taxonomy sane, undetected isolated, decode outcome fractions
    for lab_ in m.POINT_LABELS:
        t = res["per_point"][lab_]["pooled"]
        assert t["exact"] + t["verify_failed"] + t["undetected"] == 8
        assert t["D_valid_denominator"] == t["exact"] + t["verify_failed"]
        assert t["decode_failed"] == 0
    # high-f point should not be worse than the lowest-f point in exact count (loose, 8 blocks)
    e = {l: res["per_point"][l]["pooled"]["exact"] for l in m.POINT_LABELS}
    assert e["F4"] >= 6, e


def test_T2b_no_test_block_leakage_signature_and_poison():
    L = lab()
    # (1) signatures / AST: construction-side functions have no test-data parameter and never name test arrays
    bad_names = {"blocks", "block", "frames_a", "frames_b", "test", "a_sym", "b_sym", "session_input", "sessions_in"}
    for fn in (m.freeze_construction, m.compute_orders, m.build_f_grid, m.DesignEvaluator.__init__, m.DesignEvaluator.evaluate_many,
               m.cv_select_pmf, m.invariance_check, m.build_channel, m.de_order, m.solve_mu_for_f, m.layer_ks):
        params = set(inspect.signature(fn).parameters)
        assert not (params & bad_names), (fn.__name__, params & bad_names)
        src = inspect.getsource(fn)
        tree = ast.parse(textwrap.dedent(src))
        names = {n_.id for n_ in ast.walk(tree) if isinstance(n_, ast.Name)} | {n_.attr for n_ in ast.walk(tree) if isinstance(n_, ast.Attribute)}
        assert not (names & {"frames_a", "frames_b", "blocks", "a_sym", "b_sym"}), (fn.__name__, names & {"frames_a", "frames_b", "blocks"})
    # (2) runtime: poisoned test frames (different blocks, same CAL) -> identical construction outputs
    d, n_log = 64, 10
    cfg = small_cfg(d=d, n_log=n_log, m_design=8)
    outs = []
    for poison in (False, True):
        sA, _ = make_session("G2", 0, d, n_log, seed=11, n_blocks=2, poison=poison)
        sA2, _ = make_session("G3", 1, d, n_log, seed=12, n_blocks=2, poison=poison)
        out = fresh_dir() / "run"
        m.run_pipeline(L, cfg, [sA, sA2], out, tag_fn_factory())
        outs.append(out)
    for name in ("G2", "G3"):
        a = json.loads((outs[0] / f"construction_frozen_{name}.json").read_text())
        b = json.loads((outs[1] / f"construction_frozen_{name}.json").read_text())
        _strip_wall(a)
        _strip_wall(b)
        assert a == b, name
    # test-side outputs must differ (the poison actually changed the test data)
    pa = (outs[0] / "part_G2_00.json").read_text()
    pb = (outs[1] / "part_G2_00.json").read_text()
    assert pa != pb


def _strip_wall(o):
    if isinstance(o, dict):
        for k in list(o):
            if "wall" in k or "rss" in k:
                del o[k]
            else:
                _strip_wall(o[k])
    elif isinstance(o, list):
        for x in o:
            _strip_wall(x)


def test_T2c_layer_loop_matches_independent_polar_run_style_reproduction():
    """Pipeline layer loop == independent re-implementation of lab polar_run's layer loop (read, not imported)
    on the SAME tables, SAME k and SAME frames.  Synthetic data (lab data/ slice deliberately not used)."""
    L = lab()
    P, MC = L.polar, L.msd
    d, n_log, frames = 64, 10, 6
    n = 1 << n_log
    layers = 6
    pmf = synth_pmf(d)
    rng = np.random.default_rng(77)
    cal_a, cal_b = sample_pairs(rng, pmf, 8192)
    counts_d = m.joint_from_symbols(cal_a, cal_b, d)
    tables, _ = MC.build_msd_llr_tables_shift(counts_d, d, smoothing=1.0, smoothing_mode="diff_pmf")
    caps = MC.conditional_capacities(counts_d, d)["conditional_mi_bits"]
    order = P.reliable_order(n)  # same order for both implementations
    for mu_ in (0.06, 0.30):
        ks = m.layer_ks(np.array(caps), mu_, n)
        a_t, b_t = sample_pairs(rng, pmf, frames * n)
        a_f = a_t.reshape(frames, n)
        b_f = b_t.reshape(frames, n)
        dec = L.scl.MsdSclDecoder()
        # --- polar_run style (batch over frames, continue with a_hat even when wrong; k=0 -> disclose truth)
        prefix: list[np.ndarray] = []
        for i in range(layers):
            shift = layers - 1 - i
            a_bits = ((a_t >> shift) & 1).reshape(frames, n).astype(np.int8)
            if ks[i] == 0:
                prefix.append(a_bits.reshape(-1))
                continue
            pref = MC.prefix_from_bits(prefix, i)
            llr_batch = np.ascontiguousarray(MC.conditional_llr(tables, i, b_t, pref).reshape(frames, n), np.float64)
            u_full = P.polar_encode_batch_frames(a_bits, n_log)
            mask = P.info_mask_from_order(order, int(ks[i]), n)
            fidx = np.flatnonzero(1 - mask)
            frozen = np.zeros((frames, n), dtype=np.uint8)
            frozen[:, fidx] = u_full[:, fidx]
            u_hat, _, _ = dec.decode_batch(llr_batch, mask, frozen, n_log, 8, engine="compact")
            a_hat = P.polar_encode_batch_frames(u_hat, n_log)
            prefix.append(a_hat.reshape(-1))
        ref_planes = [p.reshape(frames, n) for p in prefix]
        # --- pipeline (single codeword per block)
        orders = [order] * layers
        n_err_ref = 0
        for j in range(frames):
            res = m.decode_block(L, dec, tables, orders, ks, a_f[j], b_f[j], layers=layers, n_log=n_log, list_size=8)
            for i in range(layers):
                assert np.array_equal(m.plane_bits(res["a_hat"], i, layers), ref_planes[i][j].astype(np.int8)), (j, i)
            n_err_ref += int(not res["exact"])
        print(f"T2c: mu={mu_} {frames} frames, layer-by-layer identical; blocks with errors={n_err_ref}")
        if mu_ == 0.30:
            assert n_err_ref < frames, "no successful frame at the generous margin"


def test_T2d_n32768_l16_synthetic_smoke_heavy():
    if os.environ.get("R2C_HEAVY") != "1":
        return
    import time
    L = lab()
    cfg = m.RunConfig()
    d, n, layers = cfg.d, cfg.n, cfg.layers
    pmf = synth_pmf(d)
    a0, b0 = sample_pairs(np.random.default_rng(3), pmf, 65536)
    dcounts = m.delta_counts(a0, b0, d)
    ch = m.build_channel(L, "P-HIST", dcounts, d)  # synthetic tails beyond +-1: P-M2 would be mismatched
    h = entropy_bits(pmf)
    rng = np.random.default_rng(9)
    a, b = sample_pairs(rng, pmf, n)
    orders = []
    t0 = time.perf_counter()
    for i in range(layers):
        root = m.de_root_llr(ch["tables"], ch["pmf"], i, d, layers, m_root=m.M_ROOT, seed=5 + i)
        pop = L.de.de_llr_populations_from_root(root, cfg.n_log, n_samples=m.DE_SAMPLES, seed=m.DE_SEED)
        orders.append(L.de.de_order_from_population(pop))
        del pop
        print(f"T2d: DE layer {i} done {time.perf_counter()-t0:.1f}s rss={m._peak_rss_gib():.2f}GiB", flush=True)
    dec = L.scl.MsdSclDecoder()
    outcomes = {}
    for f in (1.6, 1.25):
        mu = m.solve_mu_for_f(ch["caps"], f, n, h)
        ks = m.layer_ks(ch["caps"], mu, n)
        t0 = time.perf_counter()
        r = m.decode_block(L, dec, ch["tables"], orders, ks, a, b, layers=layers, n_log=cfg.n_log, list_size=16)
        outcomes[f] = (r["exact"], r["first_error_layer"])
        print(f"T2d: f={f} mu={mu:.4f} exact={r['exact']} first_err={r['first_error_layer']} wall={time.perf_counter()-t0:.1f}s ks={ks.tolist()}", flush=True)
    assert outcomes[1.6][0], outcomes  # generous rate margin must succeed on this synthetic channel


def test_T2e_de_seed_sensitivity_heavy():
    """Descriptive only (contract 4): info-set overlap of two DE seeds for one layer at N=32768."""
    if os.environ.get("R2C_HEAVY") != "1":
        return
    import time
    L = lab()
    d = 1024
    pmf = synth_pmf(d)
    a0, b0 = sample_pairs(np.random.default_rng(3), pmf, 65536)
    ch = m.build_channel(L, "P-M2", m.delta_counts(a0, b0, d), d)
    layer = 8
    root = m.de_root_llr(ch["tables"], ch["pmf"], layer, d, 10, m_root=m.M_ROOT, seed=5)
    k = int(m.layer_ks(ch["caps"], 0.02, 1 << 15)[layer])
    orders = []
    for sd in (m.DE_SEED, m.DE_SEED + 1):
        t0 = time.perf_counter()
        pop = L.de.de_llr_populations_from_root(root, 15, n_samples=m.DE_SAMPLES, seed=sd)
        orders.append(L.de.de_order_from_population(pop))
        del pop
        print(f"T2e: DE seed {sd} {time.perf_counter()-t0:.1f}s rss={m._peak_rss_gib():.2f}GiB", flush=True)
    print(f"T2e: layer {layer} k={k} info-set overlap(two seeds)={m.info_set_overlap(orders[0], orders[1], k):.4f}")


# =========================================================================== #
# Aggregation / verification helpers
# =========================================================================== #
def test_aggregation_undetected_isolation_wilson_pairing():
    entries = [{"status": "ok", "outcome": "exact"}] * 5 + [{"status": "ok", "outcome": "verify_failed"}] * 2 + \
              [{"status": "ok", "outcome": "undetected"}] + [{"status": "resource_abort_codeword_wall"}] + \
              [{"status": "error:X"}] + [{"status": "not_started_total_wall_budget"}]
    t = m.taxonomy(entries)
    assert (t["exact"], t["verify_failed"], t["undetected"], t["D_valid_denominator"]) == (5, 2, 1, 7)
    assert t["resource_abort"] == 1 and t["error"] == 1 and t["not_started"] == 1
    assert abs(t["p_hat"] - 2 / 7) < 1e-15
    w = m.wilson(0, 10)
    assert w["lower"] == 0.0 and abs(w["upper"] - 0.2775) < 1e-3
    assert m.classify(True, True) == "exact" and m.classify(False, True) == "undetected" and m.classify(False, False) == "verify_failed"
    c = m.contingency_2x2([(True, True), (True, False), (False, True), (False, False), (False, False)])
    assert (c["bin_exact_nb_exact"], c["bin_exact_nb_nonexact"], c["bin_nonexact_nb_exact"], c["bin_nonexact_nb_nonexact"]) == (1, 1, 1, 2)
    # tag: exact -> pass; inexact with a hash collision impossible in practice -> fail
    tag_fn = tag_fn_factory()
    a = np.arange(64) % 16
    assert m.block_tag_pass(a, a.copy(), True, lambda bits: tag_fn(bits, 3), 4)
    ah = a.copy()
    ah[5] ^= 1
    assert not m.block_tag_pass(a, ah, False, lambda bits: tag_fn(bits, 3), 4)


def test_pmf_cv_selection_rule_and_invariance_gate():
    L = lab()
    d = 64
    rng = np.random.default_rng(4)
    pmf = synth_pmf(d)
    a, b = sample_pairs(rng, pmf, 8192)
    cv = m.cv_select_pmf(L, a, b, d)
    assert cv["source"] in ("P-M2", "P-HIST") and cv["folds"] == 8
    # a heavy-tailed channel (mass beyond +-1) must make the M2 model lose the CV
    heavy = np.full(d, 0.002)
    heavy[0], heavy[1], heavy[-1] = 0.5, 0.15, 0.15
    heavy /= heavy.sum()
    a2, b2 = sample_pairs(rng, heavy, 8192)
    cv2 = m.cv_select_pmf(L, a2, b2, d)
    assert cv2["source"] == "P-HIST" and cv2["hist_minus_m2"] > m.CV_TIE_NAT
    # invariance gate: circulant synthetic data passes; a non-circulant joint (delta depends on a) fails
    inv = m.invariance_check(L, a, b, d, seed=1)
    assert inv["compatible"], inv
    delta_bad = np.where(a < d // 2, 0, 9)
    b_bad = (a + delta_bad) % d
    inv_bad = m.invariance_check(L, a, b_bad, d, seed=1)
    assert not inv_bad["compatible"], inv_bad


def test_pipeline_stop_when_invariance_fails_and_one_shot_guard():
    L = lab()
    d, n_log = 64, 10
    cfg = small_cfg(d=d, n_log=n_log)
    s, _ = make_session("G2", 0, d, n_log, seed=5, n_blocks=1)
    delta_bad = np.where(s.cal_a < d // 2, 0, 9)
    s.cal_b = (s.cal_a + delta_bad) % d
    out = fresh_dir() / "run"
    r = m.run_pipeline(L, cfg, [s], out, tag_fn_factory())
    assert r["status"] == "STOP_model_incompatible"
    assert not list(out.glob("part_*.json")) and not (out / "results.json").exists()
    # one-shot guard
    s2, _ = make_session("G2", 0, d, n_log, seed=6, n_blocks=1)
    out2 = fresh_dir() / "run"
    out2.mkdir(parents=True)
    (out2 / "results.json").write_text("{}")
    try:
        m.run_pipeline(L, cfg, [s2], out2, tag_fn_factory())
        raise AssertionError("expected refusal")
    except RuntimeError as exc:
        assert "refusing" in str(exc)


# =========================================================================== #
# T3 (milestone): full synthetic flow, parallel vs serial strict replay, NB pairing, lab untouched
# =========================================================================== #
def test_T3_full_flow_strict_replay_and_lab_untouched():
    L = lab()
    d, n_log = 64, 10
    nb_dir = fresh_dir() / "nb"
    nb_dir.mkdir(parents=True)
    sessions = []
    for name, idx, seed in (("G2", 0, 31), ("G3", 1, 32)):
        s, _ = make_session(name, idx, d, n_log, seed=seed, n_blocks=3)
        sessions.append(s)
        for b in s.blocks:  # fake NB parts (tiny stand-in for workspace/r2_fer_shg_64/part_*.json)
            (nb_dir / f"part_{name}_{b['global_block_index']:02d}.json").write_text(json.dumps(
                {"session": name, "global_block_index": b["global_block_index"], "frame_start": b["frame_start"],
                 "frame_end": b["frame_end"], "status": "ok", "scl": {"exact": (b["local_index"] % 2 == 0), "undetected": False}}))
    recs = []
    for nw in (1, 2):
        cfg = small_cfg(d=d, n_log=n_log, n_workers=nw, de_workers=nw, m_design=8)
        out = fresh_dir() / "run"
        res = m.run_pipeline(L, cfg, sessions, out, tag_fn_factory(), nb_dir=nb_dir)
        recs.append((out, res))
    for name in ("G2", "G3"):
        for gi in range(3):
            a = json.loads((recs[0][0] / f"part_{name}_{(0 if name == 'G2' else 1) * 100 + gi:02d}.json").read_text())
            b = json.loads((recs[1][0] / f"part_{name}_{(0 if name == 'G2' else 1) * 100 + gi:02d}.json").read_text())
            _strip_wall(a)
            _strip_wall(b)
            assert a == b, (name, gi)
        ca = json.loads((recs[0][0] / f"construction_frozen_{name}.json").read_text())
        cb = json.loads((recs[1][0] / f"construction_frozen_{name}.json").read_text())
        _strip_wall(ca)
        _strip_wall(cb)
        assert ca == cb
    r0 = recs[0][1]
    for lab_ in m.POINT_LABELS:
        pair = r0["per_point"][lab_]["nb_scl_L16_pairing"]
        assert pair["table"]["n"] == 6 and not pair["frame_range_mismatch"] and not pair["excluded_blocks"]
        assert sum(pair["table"][k] for k in pair["table"] if k != "n") == 6
        for st in m.STRATUM_OFFICIAL:
            assert st in r0["per_point"][lab_]["by_stratum_official"]
    assert r0["block_accounting"]["consistent"]
    assert m.snapshots_equal(_LAB["snap0"], m.lab_snapshot(LAB_ROOT)), "lab modified during T3"


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except Exception as exc:  # noqa: BLE001
                fails += 1
                import traceback
                traceback.print_exc()
                print("FAIL", name, exc)
    raise SystemExit(1 if fails else 0)
