"""Focused Stage-1 tests for the M2 +/-1 prior CANDIDATE surface.

Decoder-free, synthetic fixtures only. No CAL/TTBin/real data, no
Model-F, no SC/decoder call, no benchmark, no claim. Runner checks use
temp roots only and assert the runner reads/creates nothing it should
not. Written without a pytest dependency so it runs under plain
``python`` and is still collected by pytest: every ``test_*`` takes no
arguments and uses plain asserts.

Packet: NBPOLAR-M2-PRIOR-STAGE1-IMPLEMENTATION, Spec 4 (T1--T12).
Tolerances are absolute maxima (1e-12 unless noted as exact).

Scope notes (reported, not smoothed):

- T3 table row ("differ exactly at 2 wrap cells, ==0.0 elsewhere"):
  the exact-2-cell statement holds PRE-FLOOR (frozen Spec 1 MOD
  semantics) and at fit-attribution level. Post-renorm the MOD
  difference necessarily spreads through per-B-column renorm, so the
  two joints are bit-identical in all columns except 0 and 1023 and
  differ (only) there; the wrap cells are the sole base-level
  difference. T3 asserts exactly this.
- T9 table row ("grep prior_m2|M2 in nbpolar/ zero hits"): two
  PRE-EXISTING ``M2_prefix`` lines in the committed frozen
  ``empirical_diagnostic.py`` (unrelated empirical-diagnostic
  identifier; file verified unmodified) collide with the bare ``M2``
  substring. T9 pins that allowlist instead of touching a frozen file:
  ``prior_m2`` zero hits, and every ``M2`` hit must be the
  pre-existing allowlisted lines.
"""

from __future__ import annotations

import ast
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir import prior_m2 as m2

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "m2_prior_validation.py"
NBPOLAR_DIR = (
    REPO_ROOT
    / "comparison_bench"
    / "src"
    / "comparison_bench"
    / "formal_ir"
    / "nbpolar"
)

SEED = 20260921
PROB_TOL = 1e-12
FROZEN_K1 = 319
FROZEN_K2 = 6492


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {str(err)!r}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r})")


def make_counts(seed=SEED):
    """Synthetic int64 (1024,1024) counts: zero cells + one empty column."""
    rng = np.random.default_rng(seed)
    counts = rng.integers(0, 5, size=(1024, 1024)).astype(np.int64)
    counts[rng.random((1024, 1024)) < 0.3] = 0
    counts[:, 700] = 0
    assert (counts == 0).any(), "fixture must hold zero cells"
    assert (counts.sum(axis=0) == 0).sum() == 1, "fixture needs one empty column"
    assert int(counts.sum()) > 0
    return counts


# ---------------------------------------------------------------- T1 oracle

def oracle_m2_joint(counts, mod):
    """Independent literal oracle: delta-matrix + bincount path (S8 style).

    Shares no helper with the module (module sums diagonal index sets;
    this builds the full delta matrix and bincounts it).
    """
    c = np.asarray(counts, dtype=np.float64)
    avec = np.arange(1024)
    dmat = (avec[:, None] - avec[None, :]) % 1024
    q = np.bincount(dmat.ravel(), weights=c.ravel(), minlength=1024)
    n = float(c.sum())
    q0, qp, qm = q[0] / n, q[1] / n, q[1023] / n
    if mod == "LINEAR_ONLY":
        qp -= float(c[0, 1023]) / n
        qm -= float(c[1023, 0]) / n
    base = np.zeros((1024, 1024), dtype=np.float64)
    b = np.arange(1024)
    base[b, b] = q0
    base[(b + 1) % 1024, b] = qp
    base[(b - 1) % 1024, b] = qm
    if mod == "LINEAR_ONLY":
        base[0, 1023] = 0.0
        base[1023, 0] = 0.0
    m = np.maximum(base, 1e-15)
    return m / m.sum(axis=0, keepdims=True)


def test_T1_adapter_joint_matches_independent_oracle():
    counts = make_counts()
    for mod in ("LINEAR_ONLY", "CIRCULAR"):
        got = m2.build_prior(counts, mode="M2", mod=mod)
        want = oracle_m2_joint(counts, mod)
        diff = float(np.abs(got - want).max())
        assert diff <= 1e-12, f"T1 oracle diff {diff:.3e} under {mod}"
        coldev = float(np.abs(got.sum(axis=0) - 1).max())
        assert coldev <= 1e-12, f"T1 column dev {coldev:.3e} under {mod}"


# ---------------------------------------------------------------- T2 M0 switch

def literal_m0_joint(counts):
    """Independent literal S8 fit_m0 reimplementation (shares no helper)."""
    c = np.asarray(counts, dtype=np.float64)
    n_b = c.sum(axis=0)
    empty = n_b == 0
    denom = np.where(empty, 1.0, n_b)
    m = c / denom[None, :]
    if np.any(empty):
        m[:, empty] = 1.0 / 1024.0
    mm = np.maximum(m, 1e-15)
    return mm / mm.sum(axis=0, keepdims=True)


def test_T2_m0_switch_bit_exact():
    counts = make_counts()
    assert (counts == 0).any(), "T2 fixture must hold zero cells"
    assert (counts.sum(axis=0) == 0).any(), "T2 fixture needs an empty column"
    got = m2.build_prior(counts, mode="M0", mod="LINEAR_ONLY")
    want = literal_m0_joint(counts)
    diff = float(np.abs(got - want).max())
    assert diff == 0.0, f"T2 bit-exactness violated: max-abs-diff {diff!r}"
    got_circ = m2.build_prior(counts, mode="M0", mod="CIRCULAR")
    assert float(np.abs(got - got_circ).max()) == 0.0, "T2: M0 must ignore MOD"
    assert_raises_match(ValueError, "m2 contract:", m2.build_prior, counts, mode="M9")


# ---------------------------------------------------------------- T3 MOD toggle

def test_T3_mod_toggle_wrap_cells_and_fit_attribution():
    c = np.zeros((1024, 1024), dtype=np.int64)
    c[5, 5] = 10
    c[6, 5] = 4
    c[7, 8] = 3
    c[0, 1023] = 7
    c[1023, 0] = 5
    c[100, 200] = 2
    n_total = 31
    assert int(c.sum()) == n_total
    t_lin = m2.fit_m2_triple(c, mod="LINEAR_ONLY")
    t_circ = m2.fit_m2_triple(c, mod="CIRCULAR")
    assert t_lin["n0"] == 10 and isinstance(t_lin["n0"], int)
    assert t_lin["n_plus"] == 4, t_lin
    assert t_lin["n_minus"] == 3, t_lin
    assert t_lin["n_total"] == n_total
    assert t_circ["n_plus"] == 4 + 7, t_circ
    assert t_circ["n_minus"] == 3 + 5, t_circ
    assert t_circ["n0"] == 10 and t_circ["n_total"] == n_total
    assert t_lin["q_plus1"] == 4 / 31 and t_circ["q_plus1"] == 11 / 31
    assert t_lin["q_minus1"] == 3 / 31 and t_circ["q_minus1"] == 8 / 31
    assert t_lin["mod"] == "LINEAR_ONLY" and t_circ["mod"] == "CIRCULAR"

    q0, qp, qm = 0.7, 0.2, 0.05
    j_lin = m2.build_m2_joint(q0, qp, qm, mod="LINEAR_ONLY")
    j_circ = m2.build_m2_joint(q0, qp, qm, mod="CIRCULAR")
    diff = np.abs(j_circ - j_lin)
    changed_cols = sorted(int(b) for b in np.where(diff.sum(axis=0) > 0)[0])
    assert changed_cols == [0, 1023], f"T3 changed columns {changed_cols}"
    untouched = np.delete(diff, [0, 1023], axis=1)
    assert float(untouched.max()) == 0.0, "T3: 1022/1024 columns must be bit-identical"
    assert j_circ[0, 1023] != j_lin[0, 1023], "T3: wrap cell (0,1023) must toggle"
    assert j_circ[1023, 0] != j_lin[1023, 0], "T3: wrap cell (1023,0) must toggle"
    assert j_circ[0, 1023] > j_lin[0, 1023], "T3: priced neighbour must beat floor"
    assert j_circ[1023, 0] > j_lin[1023, 0], "T3: priced neighbour must beat floor"
    assert_raises_match(ValueError, "m2 contract:", m2.build_m2_joint, q0, qp, qm, mod="WRAP")
    assert_raises_match(
        ValueError, "m2 contract:", m2.build_m2_joint, q0, qp, qm, floor=1e-14
    )


# ---------------------------------------------------------------- T4/T5 logp

def test_T4_prob_rows_to_logp_normalization():
    rng = np.random.default_rng(SEED + 1)
    probs = rng.random((64, 32)) + 0.01
    logp = m2.prob_rows_to_logp(probs)
    assert logp.shape == (64, 32) and logp.dtype == np.float64
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(logp, axis=1)
    assert float(np.abs(lse).max()) <= 1e-12, f"T4 logsumexp {float(np.abs(lse).max()):.3e}"
    assert not np.isnan(logp).any() and not np.isposinf(logp).any()


def test_T5_exact_zero_to_neginf():
    rng = np.random.default_rng(SEED + 2)
    probs = rng.random((8, 32)) + 0.05
    probs[0, 0] = 0.0
    probs[1, [3, 7, 31]] = 0.0
    probs[2, :] = 0.0
    probs[2, 5] = 0.25
    logp = m2.prob_rows_to_logp(probs)
    assert bool((logp == -np.inf).any()), "T5 needs -inf entries"
    assert ((logp == -np.inf) == (probs == 0.0)).all(), "T5: -inf exactly at zeros"
    assert not np.isnan(logp).any(), "T5: no NaN"
    assert not np.isposinf(logp).any(), "T5: no +inf"
    assert not bool(np.isneginf(logp).all(axis=1).any()), "T5: no all--inf row"
    bad = np.zeros((2, 32))
    assert_raises_match(ValueError, "m2 contract:", m2.prob_rows_to_logp, bad)
    neg = np.full((2, 32), 0.5)
    neg[0, 0] = -0.1
    assert_raises_match(ValueError, "m2 contract:", m2.prob_rows_to_logp, neg)
    wide = np.full((2, 31), 0.5)
    assert_raises_match(ValueError, "m2 contract:", m2.prob_rows_to_logp, wide)


# ---------------------------------------------------------------- T6 packing

def test_T6_packing_round_trip_exhaustive():
    for s in range(1024):
        low, high = m2.split_symbol(s)
        assert (low, high) == (s & 31, (s >> 5) & 31), f"T6 split({s})"
        assert m2.combine_symbol(low, high) == s, f"T6 round-trip({s})"
    assert_raises_match(ValueError, "m2 contract:", m2.split_symbol, -1)
    assert_raises_match(ValueError, "m2 contract:", m2.split_symbol, 1024)
    assert_raises_match(TypeError, "m2 contract:", m2.split_symbol, True)
    assert_raises_match(ValueError, "m2 contract:", m2.combine_symbol, 32, 0)
    assert_raises_match(ValueError, "m2 contract:", m2.combine_symbol, 0, 32)


# ---------------------------------------------------------------- T7 equivariance

def test_T7_batch_permutation_equivariance():
    rng = np.random.default_rng(SEED + 3)
    probs = rng.random((48, 32)) + 0.01
    perm = rng.permutation(48)
    out_perm = m2.prob_rows_to_logp(probs[perm])
    out_ref = m2.prob_rows_to_logp(probs)[perm]
    diff = float(np.abs(out_perm - out_ref).max())
    assert diff <= 1e-12, f"T7 equivariance diff {diff:.3e}"


# ---------------------------------------------------------------- T8 loopback

def test_T8_noiseless_loopback_decoder_free():
    n = 16
    truth = np.arange(n) % 32
    probs = np.zeros((n, 32))
    probs[np.arange(n), truth] = 1.0
    logp = m2.prob_rows_to_logp(probs)
    assert (logp.argmax(axis=1) == truth).all(), "T8: argmax must recover one-hot"
    src = Path(m2.__file__).read_text(encoding="utf-8")
    assert "sc_decode" not in src, "T8: Stage 1 module must not touch sc_decode"
    assert "genie_conditionals" not in src, "T8: no genie path in Stage 1 module"


# ---------------------------------------------------------------- T9 frozen untouched

def _git(*args):
    if shutil.which("git") is None:
        raise AssertionError("git is required for T9 but was not found")
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc


def test_T9_frozen_package_untouched():
    frozen = [
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/sc.py",
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/algebra.py",
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/transform.py",
    ]
    proc = _git("diff", "--stat", "--", *frozen)
    assert proc.returncode == 0, f"T9 git failed: {proc.stderr}"
    assert proc.stdout.strip() == "", f"T9 frozen files modified:\n{proc.stdout}"
    hits_prior = []
    hits_m2_other = []
    for path in sorted(NBPOLAR_DIR.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        if "prior_m2" in text:
            hits_prior.append(path.name)
        for i, line in enumerate(text.splitlines(), 1):
            if "M2" in line and "M2_prefix" not in line:
                hits_m2_other.append(f"{path.name}:{i}:{line.strip()}")
    assert hits_prior == [], f"T9 prior_m2 leaked into nbpolar/: {hits_prior}"
    assert hits_m2_other == [], f"T9 non-allowlisted M2 hits: {hits_m2_other}"
    allow_file = NBPOLAR_DIR / "empirical_diagnostic.py"
    proc = _git("status", "--porcelain", "--", str(allow_file))
    assert proc.stdout.strip() == "", "T9 allowlist file must be unmodified"


# ---------------------------------------------------------------- T10 no import

def test_T10_no_import_of_frozen_package():
    src = Path(m2.__file__).read_text(encoding="utf-8")
    pattern = re.compile(r"from.*nbpolar|import.*nbpolar|from \. |import \.")
    assert pattern.search(src) is None, f"T10 grep hit: {pattern.search(src).group(0)!r}"
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert (node.level or 0) == 0, f"T10 relative import: {ast.dump(node)}"
            root = (node.module or "").split(".")[0]
            assert root not in ("nbpolar", "comparison_bench"), f"T10 frozen import: {root}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in ("nbpolar", "comparison_bench", "TimeTagger"), (
                    f"T10 frozen import: {alias.name}"
                )
    assert "TimeTagger" not in src, "T10: no TimeTagger in the decoder-free module"


# ---------------------------------------------------------------- T11 K replay

def literal_empirical_split(n, e1, h1, e2, h2, k_total):
    """Independent literal enumeration: worst-first (e,h,index), exhaustive K1."""
    o1 = sorted(range(n), key=lambda i: (-float(e1[i]), -float(h1[i]), int(i)))
    o2 = sorted(range(n), key=lambda i: (-float(e2[i]), -float(h2[i]), int(i)))
    lo, hi = max(0, k_total - n), min(n, k_total)
    best = None
    for k1 in range(lo, hi + 1):
        k2 = k_total - k1
        residual = sum(float(e1[i]) for i in o1[k1:]) + sum(
            float(e2[i]) for i in o2[k2:]
        )
        key = (residual, int(k1), int(k2))
        if best is None or key < best[0]:
            best = (key, int(k1), int(k2), residual)
    return best[1], best[2], best[3]


def test_T11_k_resplit_replay_synthetic_no_h_proportional():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_scaling import (
        select_empirical_split,
    )

    rng = np.random.default_rng(SEED + 4)
    n = 16
    e1 = rng.integers(0, 8, size=n) / 8.0
    h1 = rng.integers(0, 16, size=n).astype(np.float64)
    e2 = rng.integers(0, 8, size=n) / 8.0
    h2 = rng.integers(0, 16, size=n).astype(np.float64)
    for k_total in (0, 5, 2 * n - 1, 2 * n):
        got = select_empirical_split(n, e1, h1, e2, h2, k_total)
        k1, k2, residual = literal_empirical_split(n, e1, h1, e2, h2, k_total)
        assert got["k1"] == k1 and got["k2"] == k2, (
            f"T11 split mismatch at k_total={k_total}: {got} vs {(k1, k2)}"
        )
        assert got["residual"] == residual, (
            f"T11 residual mismatch at k_total={k_total}: "
            f"{got['residual']!r} vs {residual!r}"
        )
    for path in (Path(m2.__file__), RUNNER):
        text = path.read_text(encoding="utf-8")
        assert "proportional" not in text.lower(), (
            f"T11 H-proportional text present in {path.name}"
        )


# ---------------------------------------------------------------- T12 runner

FULL_FREEZE = {
    "B_tail": "0.0002",
    "a1_cal_ids": "ids-a1",
    "block_formation_fallback": "complete-blocks-only",
    "cal_frame_ids": "ids-cal",
    "cal_split_rule": "fit32-score-heldout",
    "char_sample_pairs": "200000",
    "delta_min": "0.02",
    "disjointness_matrix": "matrix",
    "g2_arms": "A1,A2,B",
    "g2_blocks": "16",
    "g2_fail_rule": "fail-rule",
    "g2_inconclusive_rule": "inconclusive-rule",
    "g2_success_rule": "success-rule",
    "heldout_frame_ids": "ids-heldout",
    "mod_boundary": "LINEAR_ONLY",
    "pairing_window_primary": "500",
    "pairing_window_sensitivity": "900",
    "skip_frames": "702",
    "tag_master": "TAG1",
}

G1_FLAGS = [
    "--window-primary", "500",
    "--window-sensitivity", "900",
    "--skip", "702",
    "--mod", "LINEAR_ONLY",
    "--char-pairs", "200000",
]
G2_FLAGS = [
    "--window-primary", "500",
    "--mod", "LINEAR_ONLY",
    "--arms", "A1,A2,B",
    "--blocks", "16",
    "--k1", str(FROZEN_K1),
    "--k2", str(FROZEN_K2),
    "--tag-master", "TAG1",
]

_stage1_tmp_root = None


@contextlib.contextmanager
def _tmp():
    """Temp dir under repo workspace/ (auto-cleaned; never outside)."""
    root = REPO_ROOT / "workspace" / ".tmp_stage1"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="m2t12_", dir=str(root)) as td:
        yield Path(td)


def _write_freeze(tmp, cfg):
    path = tmp / "freeze.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


def _run_runner(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(cwd) if cwd is not None else None,
    )


def test_T12a_help_exit0_no_side_effects():
    with _tmp() as tmp:
        before = sorted(p.name for p in tmp.iterdir())
        proc = _run_runner("--help", cwd=tmp)
        assert proc.returncode == 0, f"T12a help exit {proc.returncode}: {proc.stderr}"
        assert "freeze-config" in proc.stdout and "--authorized" in proc.stdout
        assert sorted(p.name for p in tmp.iterdir()) == before, "T12a: --help wrote files"


def test_T12b_missing_and_null_freeze_keys_exit2_list_keys():
    with _tmp() as tmp:
        drop = ["delta_min", "tag_master"]
        cfg = {k: v for k, v in FULL_FREEZE.items() if k not in drop}
        freeze = _write_freeze(tmp, cfg)
        out_root = tmp / "out_missing"
        proc = _run_runner(
            "--authorized",
            "--stage-g1-nll",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(out_root),
            *G1_FLAGS,
        )
        assert proc.returncode == 2, f"T12b exit {proc.returncode}: {proc.stderr}"
        for k in drop:
            assert k in proc.stderr, f"T12b {k} not listed: {proc.stderr.strip()}"
        nul = dict(FULL_FREEZE)
        nul["B_tail"] = None
        freeze2 = _write_freeze(tmp, nul)
        proc = _run_runner(
            "--authorized",
            "--stage-g1-nll",
            "--freeze-config", str(freeze2),
            "--acq-id", "X",
            "--out-root", str(out_root),
            *G1_FLAGS,
        )
        assert proc.returncode == 2 and "B_tail" in proc.stderr, (
            f"T12b null exit {proc.returncode}: {proc.stderr.strip()}"
        )
        assert not out_root.exists(), "T12b: refusal must create nothing"


def test_T12c_no_authorized_nonzero_reads_creates_nothing():
    with _tmp() as tmp:
        freeze = _write_freeze(tmp, dict(FULL_FREEZE))
        before = sorted(p.name for p in tmp.iterdir())
        proc = _run_runner(
            "--stage-g1-nll",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(tmp / "out_noauth"),
            *G1_FLAGS,
            cwd=tmp,
        )
        assert proc.returncode != 0, "T12c: stage without --authorized must fail"
        assert "--authorized" in proc.stderr, f"T12c stderr: {proc.stderr.strip()}"
        assert sorted(p.name for p in tmp.iterdir()) == before, "T12c: runner touched files"


def test_T12d_authorized_is_store_true_ast():
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument":
            names = [
                a.value
                for a in node.args
                if isinstance(a, ast.Constant) and isinstance(a.value, str)
            ]
            kw = {k.arg: k.value for k in node.keywords}
            action = kw.get("action")
            if "--authorized" in names:
                found = True
                assert isinstance(action, ast.Constant) and action.value == "store_true", (
                    "T12d: --authorized must be action='store_true'"
                )
    assert found, "T12d: --authorized argument not found"


def test_T12e_runner_import_side_effect_free():
    with _tmp() as tmp:
        code = (
            "import sys; sys.path.insert(0, "
            + repr(str(REPO_ROOT / "scripts"))
            + "); import m2_prior_validation as m; "
            + "print('import-ok', m.FLAG_G1)"
        )
        proc = subprocess.run(
            [sys.executable, "-B", "-c", code],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(tmp),
        )
        assert proc.returncode == 0, f"T12e import failed: {proc.stderr}"
        assert "import-ok" in proc.stdout
        leftovers = sorted(p.name for p in tmp.iterdir())
        assert leftovers == [], f"T12e: import created files: {leftovers}"


def test_T12f_k_pin_and_stage_body_exit3_zero_contact():
    with _tmp() as tmp:
        freeze = _write_freeze(tmp, dict(FULL_FREEZE))
        bad_root = tmp / "out_g2bad"
        bad = [a if a != str(FROZEN_K1) else "320" for a in G2_FLAGS]
        proc = _run_runner(
            "--authorized",
            "--stage-g2-decode",
            "--freeze-config", str(freeze),
            "--acq-id", "ACQ",
            "--out-root", str(bad_root),
            *bad,
        )
        assert proc.returncode == 2, f"T12f k-pin exit {proc.returncode}: {proc.stderr}"
        assert "319" in proc.stderr, f"T12f k-pin must name 319: {proc.stderr.strip()}"
        assert not bad_root.exists(), "T12f: k-pin refusal must create nothing"
        good_root = tmp / "out_g2good"
        assert not good_root.exists(), "T12f precondition: good out-root absent"
        proc = _run_runner(
            "--authorized",
            "--stage-g2-decode",
            "--freeze-config", str(freeze),
            "--acq-id", "ACQ",
            "--out-root", str(good_root),
            *G2_FLAGS,
        )
        assert proc.returncode == 3, f"T12f body exit {proc.returncode}: {proc.stderr}"
        assert "STAGE_BODY_PENDING_FREEZE" in proc.stderr, proc.stderr.strip()
        assert not good_root.exists(), "T12f: Stage-1 body must create nothing"


def test_T12g_flag_freeze_cross_check_mismatch_exit2():
    with _tmp() as tmp:
        freeze = _write_freeze(tmp, dict(FULL_FREEZE))
        flags = [a if a != "500" else "501" for a in G1_FLAGS]
        out_root = tmp / "out_xcheck"
        proc = _run_runner(
            "--authorized",
            "--stage-g1-nll",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(out_root),
            *flags,
        )
        assert proc.returncode == 2, f"T12g exit {proc.returncode}: {proc.stderr}"
        assert "pairing_window_primary" in proc.stderr, (
            f"T12g must list the key: {proc.stderr.strip()}"
        )
        assert not out_root.exists(), "T12g: cross-check refusal must create nothing"


def test_T12h_out_root_outside_workspace_refused():
    with _tmp() as tmp:
        freeze = _write_freeze(tmp, dict(FULL_FREEZE))
        # Referenced but never created: the runner must refuse before touching it.
        outside = Path(tempfile.gettempdir()) / f"m2_stage1_outside_{os.getpid()}" / "out"
        assert not outside.exists(), "T12h precondition: outside path absent"
        proc = _run_runner(
            "--authorized",
            "--stage-g1-nll",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(outside),
            *G1_FLAGS,
        )
        assert proc.returncode == 2, f"T12h exit {proc.returncode}: {proc.stderr}"
        assert "workspace" in proc.stderr, f"T12h stderr: {proc.stderr.strip()}"
        assert not outside.exists(), "T12h: refusal must create nothing"


def test_T12i_g1_body_executes_and_mutual_exclusion():
    # G1 body is REAL since the G1 freeze packet (decoder-free pairing/NLL
    # science in scripts/m2_prior_validation.py): an unknown acq-id fails
    # the inventory lookup (exit 2) creating nothing — it never exits 3.
    with _tmp() as tmp:
        freeze = _write_freeze(tmp, dict(FULL_FREEZE))
        good_root = tmp / "out_g1good"
        proc = _run_runner(
            "--authorized",
            "--stage-g1-nll",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(good_root),
            *G1_FLAGS,
        )
        assert proc.returncode == 2, f"T12i body exit {proc.returncode}: {proc.stderr}"
        assert not good_root.exists(), "T12i: unknown-acq refusal must create nothing"
        proc = _run_runner(
            "--authorized",
            "--stage-g1-nll",
            "--stage-g2-decode",
            "--freeze-config", str(freeze),
            "--acq-id", "X",
            "--out-root", str(good_root),
        )
        assert proc.returncode == 2, f"T12i exclusivity exit {proc.returncode}"


def test_T12j_selfcheck_passes():
    proc = _run_runner("--selfcheck")
    assert proc.returncode == 0, f"T12j exit {proc.returncode}:\n{proc.stdout}\n{proc.stderr}"
    assert "SELFCHECK_PASS" in proc.stdout, proc.stdout[-2000:]
