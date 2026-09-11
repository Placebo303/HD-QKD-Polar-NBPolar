"""Focused Phase 4-P2 tests: prior-artifact loader on synthetic fixtures.

Synthetic temporary NPZ/JSON fixtures only. No sibling or production path
access, no CAL/TTBin/real data, no Model-F, no SC decoder call, no
benchmark, no file output beyond the temporary fixtures, no floor from
data, no performance claim. Written without a pytest dependency so it runs
under plain ``python`` and is still collected by pytest elsewhere: every
``test_*`` function takes no arguments and uses plain asserts plus a local
``assert_raises_match`` helper.

Covers TASK_PACKET.md gates P2-T0-01 and P2-T1-01--T1-12 on synthetic
data. P2-T0-02 / P2-T2-02 need the authorized diagnostic entrypoint and
the sole content read, so they stay closed until independent Pre-EXECUTE
PASS. Tolerances are absolute maxima (1e-12 unless noted).
"""

from __future__ import annotations

import ast
import inspect
import json
import sys
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    Conditioning,
    Provenance,
    build_p1_metrics,
    derive_p1,
    derive_p2,
    probs_to_symbol_metric,
    smooth_joint_to_conditional,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    prior_artifact as pa_mod,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    prior as prior_mod,
)

LAM = 137.3823795883264
NORM_TOL = 1e-12
TOTAL = 262144

BANNED_IDENTIFIERS = (
    "build_f_model",
    "prepare_model_f_prior",
    "get_l1_app_prior_l2",
    "app_fed_l2_prior",
    "sc_decode",
    "v72p2d5_gf32_rate_mother",
    "workspace/v72p2d5_model_f_input",
    "pandas",
    "parquet",
)


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def valid_summary():
    """Independent literal pin of the frozen summary schema (cf. M11)."""
    return {
        "schema": "v72p2d5_model_f_input_v1",
        "cycle": "V72P2D5-GF32-RATE-MOTHER",
        "session": "20260123_1M_600k_0dB",
        "source": "1M",
        "cal_start": 702,
        "cal_end": 1725,
        "n_frames": 1024,
        "pairs_per_frame": 256,
        "n_symbols": TOTAL,
        "axis": ["Alice", "Bob"],
        "dims": [1024, 1024],
        "mapping": "symbol=low+32*high;high=U1;low=U2",
        "field": {"q": 32, "poly": 37},
        "lambda_star": LAM,
        "selection": "D4R2 nested-CV refit",
        "cal_only": True,
        "val_rows_read": 0,
        "decoder_calls": 0,
        "p0_calls": 0,
        "formal": False,
        "status": "MODEL_F_INPUT_CANDIDATE",
        "artifact_files": ["model_f_input.npz", "model_f_input_summary.json"],
    }


def sparse_counts():
    """Asymmetric sparse counts summing to exactly 262144 (transpose-sensitive)."""
    counts = np.zeros((1024, 1024), dtype=np.int64)
    counts[33, 7] = 200000
    counts[7, 33] = 10000
    counts[0, 0] = TOTAL - 210000
    assert int(counts.sum()) == TOTAL
    return counts


def write_fixture(root, counts=None, p_b=None, summary=None, npz_extra=None):
    """Write a synthetic artifact pair under ``root``; returns (npz, json) paths."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    counts = sparse_counts() if counts is None else counts
    if p_b is None:
        p_b = counts.astype(np.float64).sum(axis=0) / float(TOTAL)
    if summary is None:
        summary = valid_summary()
    payload = {"counts_ab": counts, "p_b": np.asarray(p_b, dtype=np.float64)}
    if npz_extra:
        payload.update(npz_extra)
    np.savez_compressed(str(root / "model_f_input.npz"), **payload)
    (root / "model_f_input_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    return root / "model_f_input.npz", root / "model_f_input_summary.json"


def oracle_smooth(counts, lam):
    """Independent literal-formula oracle (loops, no shared helper)."""
    grid = [[float(v) for v in row] for row in np.asarray(counts).tolist()]
    n_a, n_b = len(grid), len(grid[0])
    total = sum(sum(row) for row in grid)
    p_global = [sum(grid[a][b] for b in range(n_b)) / total for a in range(n_a)]
    n_bcol = [sum(grid[a][b] for a in range(n_a)) for b in range(n_b)]
    out = [[0.0] * n_b for _ in range(n_a)]
    for a in range(n_a):
        for b in range(n_b):
            if n_bcol[b] == 0:
                out[a][b] = p_global[a]
            else:
                out[a][b] = (grid[a][b] + lam * p_global[a]) / (n_bcol[b] + lam)
    return np.array(out, dtype=np.float64)


def test_t000_import_without_io():
    """P2-T0-01: module compiles/imports with no module-level I/O call."""
    src = Path(pa_mod.__file__).read_text(encoding="utf-8")
    compile(src, pa_mod.__file__, "exec")
    tree = ast.parse(src)
    for node in tree.body:
        assert not (isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Call)), "module-level call"
    assert pa_mod.NPZ_FILENAME == "model_f_input.npz"
    assert pa_mod.SUMMARY_FILENAME == "model_f_input_summary.json"


def test_t101_keys_exact():
    """P2-T1-01: exactly two NPZ keys; object arrays rejected."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        npz, js = write_fixture(tmp)
        rec = pa_mod.load_prior_artifact(npz, js)
        assert int(rec.counts_ab.sum()) == TOTAL
        with tempfile.TemporaryDirectory() as tmp2:
            write_fixture(tmp2, npz_extra={"extra": np.zeros(3)})
            npz2 = Path(tmp2) / "model_f_input.npz"
            js2 = Path(tmp2) / "model_f_input_summary.json"
            assert_raises_match(ValueError, "artifact contract:",
                               pa_mod.load_prior_artifact, npz2, js2)
        with tempfile.TemporaryDirectory() as tmp3:
            tmp3p = Path(tmp3)
            counts = sparse_counts()
            p_b = counts.astype(np.float64).sum(axis=0) / float(TOTAL)
            np.savez(str(tmp3p / "model_f_input.npz"), counts_ab=counts)
            (tmp3p / "model_f_input_summary.json").write_text(
                json.dumps(valid_summary()), encoding="utf-8")
            assert_raises_match(ValueError, "artifact contract:",
                               pa_mod.load_prior_artifact,
                               tmp3p / "model_f_input.npz",
                               tmp3p / "model_f_input_summary.json")
        with tempfile.TemporaryDirectory() as tmp4:
            tmp4p = Path(tmp4)
            obj = np.empty(3, dtype=object)
            obj[:] = [1, 2, 3]
            np.savez(str(tmp4p / "model_f_input.npz"),
                     counts_ab=obj, p_b=np.full(1024, 1.0 / 1024))
            (tmp4p / "model_f_input_summary.json").write_text(
                json.dumps(valid_summary()), encoding="utf-8")
            assert_raises_match(ValueError, "artifact contract:",
                               pa_mod.load_prior_artifact,
                               tmp4p / "model_f_input.npz",
                               tmp4p / "model_f_input_summary.json")


def test_t102_counts_shape_sum():
    """P2-T1-02: counts (1024,1024) integer, non-negative, sum exactly 262144."""
    import tempfile
    cases = [
        ("shape", np.zeros((1023, 1024), dtype=np.int64)),
        ("neg", None),  # built below
        ("float", np.zeros((1024, 1024), dtype=np.float64)),
        ("bool", np.zeros((1024, 1024), dtype=bool)),
    ]
    bad_neg = sparse_counts().copy()
    bad_neg[0, 0] = -1
    bad_sum = sparse_counts().copy()
    bad_sum[0, 0] = int(bad_sum[0, 0]) - 1
    with tempfile.TemporaryDirectory() as tmp:
        for name, arr in cases:
            if name == "neg":
                arr = bad_neg
            if name == "float":
                arr = arr.copy()
                arr[0, 0] = float(TOTAL)
            with tempfile.TemporaryDirectory() as one:
                if name == "bool":
                    one_p = Path(one)
                    p_b = np.full(1024, 1.0 / 1024)
                    np.savez_compressed(
                        str(one_p / "model_f_input.npz"), counts_ab=arr, p_b=p_b)
                    (one_p / "model_f_input_summary.json").write_text(
                        json.dumps(valid_summary()), encoding="utf-8")
                else:
                    write_fixture(one, counts=arr)
                assert_raises_match(ValueError, "artifact contract:",
                                   pa_mod.load_prior_artifact,
                                   Path(one) / "model_f_input.npz",
                                   Path(one) / "model_f_input_summary.json"), name
        with tempfile.TemporaryDirectory() as one:
            write_fixture(one, counts=bad_sum)
            assert_raises_match(ValueError, "artifact contract:",
                               pa_mod.load_prior_artifact,
                               Path(one) / "model_f_input.npz",
                               Path(one) / "model_f_input_summary.json")


def test_t103_marginal():
    """P2-T1-03: p_b (1024,) finite/non-negative, sums to 1, equals axis-0 marginal."""
    import tempfile
    counts = sparse_counts()
    good = counts.astype(np.float64).sum(axis=0) / float(TOTAL)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = Path(tmp)
        bad_shape = np.zeros(1023)
        write_fixture(tmp_p / "a", p_b=bad_shape)
        assert_raises_match(ValueError, "artifact contract:",
                           pa_mod.load_prior_artifact,
                           tmp_p / "a" / "model_f_input.npz",
                           tmp_p / "a" / "model_f_input_summary.json")
        drifted = good.copy()
        drifted[5] += 0.01
        drifted = drifted / drifted.sum()
        write_fixture(tmp_p / "b", p_b=drifted)
        assert_raises_match(ValueError, "artifact contract:",
                           pa_mod.load_prior_artifact,
                           tmp_p / "b" / "model_f_input.npz",
                           tmp_p / "b" / "model_f_input_summary.json")
        wrong_axis = counts.astype(np.float64).sum(axis=1) / float(TOTAL)
        assert not np.allclose(good, wrong_axis)
        write_fixture(tmp_p / "c", p_b=wrong_axis)
        assert_raises_match(ValueError, "artifact contract:",
                           pa_mod.load_prior_artifact,
                           tmp_p / "c" / "model_f_input.npz",
                           tmp_p / "c" / "model_f_input_summary.json")
        nan_pb = good.copy()
        nan_pb[9] = np.nan
        write_fixture(tmp_p / "d", p_b=nan_pb)
        assert_raises_match(ValueError, "artifact contract:",
                           pa_mod.load_prior_artifact,
                           tmp_p / "d" / "model_f_input.npz",
                           tmp_p / "d" / "model_f_input_summary.json")


def test_t104_axis_transpose():
    """P2-T1-04: asymmetric fixture proves [Alice,Bob] order is preserved."""
    import tempfile
    counts = sparse_counts()
    assert counts[33, 7] != counts[7, 33]
    with tempfile.TemporaryDirectory() as tmp:
        npz, js = write_fixture(Path(tmp) / "ab")
        rec = pa_mod.load_prior_artifact(npz, js)
        assert rec.counts_ab[33, 7] == 200000
        assert rec.counts_ab[7, 33] == 10000
        expect_pb = counts.astype(np.float64).sum(axis=0) / float(TOTAL)
        assert float(np.abs(rec.p_b - expect_pb).max()) == 0.0
        trans = counts.T.copy()
        t_pb = trans.astype(np.float64).sum(axis=0) / float(TOTAL)
        assert not np.allclose(t_pb, expect_pb)
        npz_t, js_t = write_fixture(Path(tmp) / "ba", counts=trans, p_b=t_pb)
        rec_t = pa_mod.load_prior_artifact(npz_t, js_t)
        assert not np.array_equal(rec.counts_ab, rec_t.counts_ab)
        assert not np.allclose(rec.p_b, rec_t.p_b)


def test_t105_summary_identity():
    """P2-T1-05: summary identity incl. session/CAL/axis/packing/GF/lambda/status/files."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = Path(tmp)
        npz, js = write_fixture(tmp_p / "ok")
        rec = pa_mod.load_prior_artifact(npz, js)
        assert rec.summary["session"] == "20260123_1M_600k_0dB"
        assert (rec.summary["cal_start"], rec.summary["cal_end"]) == (702, 1725)
        assert rec.summary["lambda_star"] == LAM
        assert rec.summary["artifact_files"] == [
            "model_f_input.npz", "model_f_input_summary.json"]
        tampers = [
            ("session", "bad"), ("cal_start", 700), ("cal_end", 1700),
            ("n_frames", 1000), ("pairs_per_frame", 128), ("n_symbols", 100),
            ("axis", ["Bob", "Alice"]), ("dims", [1024, 1023]),
            ("mapping", "other"), ("field", {"q": 32, "poly": 55}),
            ("lambda_star", 1.0), ("selection", "other"),
            ("cal_only", False), ("val_rows_read", 1), ("decoder_calls", 2),
            ("p0_calls", 3), ("formal", True), ("status", "OTHER"),
            ("schema", "other"), ("cycle", "other"), ("source", "other"),
            ("artifact_files", ["model_f_input.npz"]),
            ("artifact_files", ["model_f_input_summary.json", "model_f_input.npz"]),
        ]
        for key, val in tampers:
            with tempfile.TemporaryDirectory() as one:
                bad = valid_summary()
                bad[key] = val
                write_fixture(one, summary=bad)
                assert_raises_match(ValueError, "artifact contract:",
                                   pa_mod.load_prior_artifact,
                                   Path(one) / "model_f_input.npz",
                                   Path(one) / "model_f_input_summary.json"), (key, val)
        with tempfile.TemporaryDirectory() as one:
            bad = valid_summary()
            del bad["lambda_star"]
            write_fixture(one, summary=bad)
            assert_raises_match(ValueError, "artifact contract:",
                               pa_mod.load_prior_artifact,
                               Path(one) / "model_f_input.npz",
                               Path(one) / "model_f_input_summary.json")
        renamed = tmp_p / "renamed.npz"
        renamed.write_bytes(npz.read_bytes())
        assert_raises_match(ValueError, "artifact contract:",
                           pa_mod.load_prior_artifact, renamed, js)


def test_t106_formula_oracle():
    """P2-T1-06: P1 concentration formula on loaded counts vs loop oracle <=1e-12."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        npz, js = write_fixture(tmp)
        rec = pa_mod.load_prior_artifact(npz, js)
        prod = smooth_joint_to_conditional(rec.counts_ab, LAM)
        ref = oracle_smooth(rec.counts_ab, LAM)
        assert float(np.abs(prod - ref).max()) <= 1e-12


def test_t107_p1p2_slices():
    """P2-T1-07: P1/P2 shapes/normalization + loop check on asymmetric slices."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        npz, js = write_fixture(tmp)
        rec = pa_mod.load_prior_artifact(npz, js)
        f = oracle_smooth(rec.counts_ab, LAM)
        p1, p2 = derive_p1(f), derive_p2(f)
        assert p1.shape == (32, 1024)
        assert p2.shape == (32, 1024, 32)
        assert float(np.abs(p1.sum(axis=0) - 1).max()) <= NORM_TOL
        assert float(np.abs(p2.sum(axis=-1) - 1).max()) <= NORM_TOL
        for b in (0, 7, 33):
            for u1 in (0, 1, 7, 31):
                want = sum(float(f[u1 * 32 + u2, b]) for u2 in range(32))
                assert abs(float(p1[u1, b]) - want) <= 1e-12, (u1, b)
                mass = want
                for u2 in range(32):
                    w = (float(f[u1 * 32 + u2, b]) / mass) if mass else 1.0 / 32
                    assert abs(float(p2[u1, b, u2]) - w) <= 1e-12, (u1, b, u2)


def test_t108_fallbacks_support():
    """P2-T1-08: unseen-B -> p_global, zero (U1,B) -> uniform, exact-zero kept."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        npz, js = write_fixture(tmp)
        rec = pa_mod.load_prior_artifact(npz, js)
        counts = rec.counts_ab.astype(np.float64)
        n_bcol = counts.sum(axis=0)
        zero_cols = np.flatnonzero(n_bcol == 0)
        assert len(zero_cols) == 1024 - 3  # only Bob {0,7,33} observed
        f = smooth_joint_to_conditional(rec.counts_ab, LAM)
        p_global = counts.sum(axis=1) / float(TOTAL)
        assert float(np.abs(f[:, zero_cols] - p_global[:, None]).max()) == 0.0
        p2 = derive_p2(f)
        mass = f.reshape(32, 32, 1024).sum(axis=1)
        n_zero = int((mass == 0).sum())
        assert n_zero == 30 * 1024  # only Alice {0,1} observed -> U1 in {0,1}
        assert float(np.abs(p2[mass == 0] - 1.0 / 32).max()) == 0.0
        p1 = derive_p1(f)
        bob = np.array([[0, 7, 33, 500]])
        probs = build_p1_metrics(bob, p1)
        metric = probs_to_symbol_metric(probs[0])
        zero = probs[0] == 0
        assert zero.any()
        assert int(zero.sum()) == int((p1[:, [0, 7, 33, 500]] == 0).sum())
        assert (metric.logp[zero] == -np.inf).all()
        assert np.isfinite(metric.logp[~zero]).all()


def test_t109_packing():
    """P2-T1-09: exhaustive packing identity over all 1024 labels."""
    for s in range(1024):
        low, high = prior_mod.split_symbol(s)
        assert (low, high) == (s & 31, (s >> 5) & 31), s
        assert prior_mod.combine_symbol(low, high) == s, s


def test_t110_no_truth_provenance():
    """P2-T1-10: loader takes no Alice input; record is PRIOR_ONLY/FULL_BOB_ONLY."""
    import tempfile
    params = set(inspect.signature(pa_mod.load_prior_artifact).parameters)
    assert params == {"npz_path", "summary_path"}, params
    assert all("alice" not in p.lower() for p in params)
    with tempfile.TemporaryDirectory() as tmp:
        npz, js = write_fixture(tmp)
        rec = pa_mod.load_prior_artifact(npz, js)
        assert rec.conditioning is Conditioning.FULL_BOB_ONLY
        assert rec.provenance is Provenance.PRIOR_ONLY
        assert not rec.counts_ab.flags.writeable
        assert not rec.p_b.flags.writeable


def test_t111_banned_imports():
    """P2-T1-11: no per-cell twin / historical decoder / production-data imports."""
    src = Path(pa_mod.__file__).read_text(encoding="utf-8")
    for name in BANNED_IDENTIFIERS:
        assert name not in src, name
    assert "allow_pickle=False" in src.replace(" ", "")
    # The test itself must never *access* a production path: no absolute
    # path literal and no reference to the accepted artifact root (words
    # like TTBin/parquet in prose are fine; path literals are not).
    own = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(own)
    skip = next(n for n in tree.body
                if isinstance(n, ast.FunctionDef) and n.name == "test_t111_banned_imports")
    frags = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    frags.add(id(v))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in frags:
                continue  # f-string fragment, never a path access
            val = node.value
            if getattr(node, "lineno", 0) is not None and skip.lineno <= getattr(node, "lineno", 0) <= (skip.end_lineno or 0):
                continue
            assert not val.startswith("/"), val
            assert not (len(val) > 2 and val[1] == ":"), val
            assert "v72p2d5_model_f_input/20260907" not in val, val


def test_t112_no_overwrite():
    """P2-T1-12: loader writes nothing; temp roots only; repeat loads stable."""
    import tempfile

    def snapshot(root):
        out = {}
        for p in sorted(Path(root).rglob("*")):
            if p.is_file():
                out[str(p.relative_to(root))] = p.read_bytes()
        return out

    with tempfile.TemporaryDirectory() as tmp:
        npz, js = write_fixture(tmp)
        before = snapshot(tmp)
        first = pa_mod.load_prior_artifact(npz, js)
        second = pa_mod.load_prior_artifact(str(npz), str(js))
        assert snapshot(tmp) == before
        assert np.array_equal(first.counts_ab, second.counts_ab)
        assert float(np.abs(first.p_b - second.p_b).max()) == 0.0


if __name__ == "__main__":
    names = sorted(n for n, v in sorted(globals().items())
                   if n.startswith("test_") and callable(v))
    failed = 0
    for name in names:
        try:
            globals()[name]()
        except Exception as err:  # noqa: BLE001 -- minimal runner reports only
            failed += 1
            print(f"FAIL {name}: {type(err).__name__}: {err}")
        else:
            print(f"ok {name}")
    print(f"{len(names) - failed}/{len(names)} passed")
    sys.exit(1 if failed else 0)
