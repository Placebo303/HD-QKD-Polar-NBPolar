"""Focused G2 tests: list SC decoder over tiny in-memory metrics only.

T0/T1 lane for the frozen ``scl_decode`` interface (FREEZE_DRAFT.md section
3, post N1-N3 amendment): L=1 identity against ``sc_decode``, chunked
(row-budget 512) vs unchunked (None) equivalence, canonical tie-break,
one-hot loopback, disclosure/no-branch behavior, survivor-count bound,
prune-slot shape with a test-only top-L stub, input-order identity, and
path-refusal audits.

Scope: GF4/GF32 toy blocks (N<=16) built from local RNG streams with fresh
test-local seeds. No protected stores, no seed bands from prior tracks, no
decoder bodies outside ``sc``/``scl``, no file output, no performance claim.
Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments and uses plain
asserts plus local ``assert_raises`` helpers.
"""

from __future__ import annotations

import inspect
import sys
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import sc as sc_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import scl as scl_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
    make_gf2m,
    make_gf32,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc import sc_decode
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.scl import (
    SCLResult,
    scl_decode,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
    polar_transform,
)

# Fresh test-local seeds for this file only; no prior-track band is reused.
TEST_SEED_A = 2026092701
TEST_SEED_B = 2026092702
TEST_SEED_C = 2026092703

GF4 = make_gf2m(2, 7)
GF32 = make_gf32()


def assert_raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__} from {fn.__name__}{args}")


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def normalize_rows(mat):
    mat = np.asarray(mat, dtype=np.float64)
    with np.errstate(invalid="ignore"):
        lse = np.logaddexp.reduce(mat, axis=1, keepdims=True)
    return mat - lse


def top_l_stub():
    """Test-only prune stub: stable top-L by metric (not a frozen value)."""

    def stub(path_metrics, position, is_spike, width_L):
        order = np.argsort(-np.asarray(path_metrics, dtype=np.float64), kind="stable")
        return order[: int(width_L)].astype(np.int64)

    stub.__name__ = "top_l_stub"
    return stub


def recording_stub(record):
    """Top-L stub that records its call context for slot-shape asserts."""

    def stub(path_metrics, position, is_spike, width_L):
        record.append(
            {
                "metrics": np.asarray(path_metrics, dtype=np.float64),
                "position": position,
                "is_spike": is_spike,
                "width_L": width_L,
            }
        )
        order = np.argsort(-np.asarray(path_metrics, dtype=np.float64), kind="stable")
        return order[: int(width_L)].astype(np.int64)

    stub.__name__ = "recording_stub"
    return stub


def toy_metrics(seed, n, field, disclosure=()):
    rng = np.random.default_rng(seed)
    logp = normalize_rows(rng.normal(0, 1.2, size=(n, field.q)))
    ref = sc_decode(logp, field=field)
    dec = [int(v) for v in ref.u_hat]
    pos = list(disclosure)
    return logp, pos, [dec[p] for p in pos]


# --- T0: surface, signature, structure ---------------------------------------

def test_scl_surface_and_signature():
    assert set(["scl_decode", "SCLResult"]) <= set(dir(scl_mod))
    sig = inspect.signature(scl_decode)
    params = list(sig.parameters.values())
    assert [p.name for p in params] == [
        "logp_x", "field", "alpha", "known_positions", "known_values",
        "list_width_L", "prune_rule",
    ]
    assert params[0].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in params[1:])
    assert params[2].default == 2
    assert params[3].default is None and params[4].default is None
    assert params[5].default is inspect.Parameter.empty  # width: no default
    assert params[6].default is inspect.Parameter.empty  # prune slot: no default
    assert not any("chunk" in p.name for p in params)
    assert inspect.signature(sc_mod._minus_block).parameters["chunk_rows"].default == 512


def test_scl_result_shape_and_types():
    logp, pos, val = toy_metrics(TEST_SEED_A, 8, GF4, disclosure=[0, 3])
    res = scl_decode(logp, field=GF4, known_positions=pos, known_values=val,
                     list_width_L=3, prune_rule=top_l_stub())
    assert isinstance(res, SCLResult) and res.status == "ok"
    assert res.survivor_count <= 3 and res.survivor_count >= 1
    assert res.requested_width == 3
    assert res.u_candidates.shape == (res.survivor_count, 8)
    assert res.x_candidates.shape == (res.survivor_count, 8)
    assert res.path_metrics.shape == (res.survivor_count,)
    assert res.u_candidates.dtype == np.int64 and res.x_candidates.dtype == np.int64
    assert res.path_metrics.dtype == np.float64
    assert res.known_mask.dtype == bool and res.known_mask.tolist() == [
        True, False, False, True, False, False, False, False]
    assert res.known_count == 2
    assert isinstance(res.pruned_count, int) and res.pruned_count >= 0
    assert res.metric_provenance["log_base"] == "natural"
    assert res.metric_provenance["list_width_L"] == 3
    assert res.metric_provenance["prune_rule"] == "top_l_stub"
    for row_u, row_x in zip(res.u_candidates.tolist(), res.x_candidates.tolist()):
        assert row_x == polar_transform(row_u, field=GF4).tolist()
    assert all(res.path_metrics[k] >= res.path_metrics[k + 1]
               for k in range(res.survivor_count - 1))  # best-first


# --- T0: L=1 identity with sc_decode ------------------------------------------

def check_l1_identity(logp, field, pos, val):
    ref = sc_decode(logp, field=field, known_positions=pos, known_values=val)
    res = scl_decode(logp, field=field, known_positions=pos, known_values=val,
                     list_width_L=1, prune_rule=top_l_stub())
    assert res.survivor_count == 1
    assert res.u_candidates[0].tolist() == ref.u_hat.tolist()
    assert res.x_candidates[0].tolist() == ref.x_hat.tolist()
    undisclosed = [i for i in range(ref.u_hat.shape[0]) if i not in set(pos)]
    assert res.path_metrics[0] == float(np.sum(ref.decision_log_scores[undisclosed]))


def test_l1_identity_gf4_n8():
    logp, _, _ = toy_metrics(TEST_SEED_A + 10, 8, GF4)
    ref = sc_decode(logp, field=GF4)
    dec = [int(v) for v in ref.u_hat]
    check_l1_identity(logp, GF4, [], [])
    check_l1_identity(logp, GF4, [0, 3], [dec[0], dec[3]])
    check_l1_identity(logp, GF4, list(range(8)), dec)
    # forced non-MAP disclosure still matches bit-identically
    forced = (dec[1] + 1) % GF4.q
    assert forced != dec[1]
    check_l1_identity(logp, GF4, [1], [forced])


def test_l1_identity_gf32_n8():
    rng = np.random.default_rng(TEST_SEED_B)
    logp = normalize_rows(rng.normal(0, 1.0, size=(8, GF32.q)))
    ref = sc_decode(logp, field=GF32)
    dec = [int(v) for v in ref.u_hat]
    check_l1_identity(logp, GF32, [], [])
    check_l1_identity(logp, GF32, [2, 5], [dec[2], dec[5]])


# --- T0: tie-break --------------------------------------------------------------

def test_tie_break_uniform():
    logp = np.zeros((2, GF4.q))  # uniform rows: every branch ties
    res = scl_decode(logp, field=GF4, list_width_L=2, prune_rule=top_l_stub())
    assert res.survivor_count == 2
    # smallest symbol first, then smallest path index
    assert res.u_candidates.tolist() == [[0, 0], [1, 0]]
    assert res.path_metrics[0] == res.path_metrics[1]
    res1 = scl_decode(logp, field=GF4, list_width_L=1, prune_rule=top_l_stub())
    assert res1.u_candidates.tolist() == [[0, 0]]  # argmax convention


def test_stub_determinism():
    stub = top_l_stub()
    vec = np.array([-1.0, -0.5, -0.5, -2.0])
    assert stub(vec, 3, False, 2).tolist() == stub(vec, 3, False, 2).tolist() == [1, 2]


# --- T0: chunked (512) vs unchunked (None) equivalence ----------------------------

def run_with_chunk(metrics, chunk, kp=None, kv=None, width=2):
    orig = sc_mod._minus_block
    seen = []
    if chunk == "default":
        return scl_decode(metrics, field=GF4, known_positions=kp, known_values=kv,
                          list_width_L=width, prune_rule=top_l_stub()), seen
    def wrapper(first, second, idx, chunk_rows=512):
        seen.append(chunk_rows)
        return orig(first, second, idx, chunk_rows=chunk)
    sc_mod._minus_block = wrapper
    try:
        return scl_decode(metrics, field=GF4, known_positions=kp, known_values=kv,
                          list_width_L=width, prune_rule=top_l_stub()), seen
    finally:
        sc_mod._minus_block = orig
        assert sc_mod._minus_block is orig


def test_chunked_vs_none_equivalence():
    logp, pos, val = toy_metrics(TEST_SEED_C, 8, GF4, disclosure=[1, 4])
    ref, seen_default = run_with_chunk(logp, "default", pos, val)
    assert seen_default == []  # scl_decode never passes chunk_rows explicitly
    got_none, _ = run_with_chunk(logp, None, pos, val)
    got_512, seen_512 = run_with_chunk(logp, 512, pos, val)
    assert all(c == 512 or c is None for c in seen_512) or seen_512 == []
    for got in (got_none, got_512):
        assert got.u_candidates.tolist() == ref.u_candidates.tolist()
        assert got.x_candidates.tolist() == ref.x_candidates.tolist()
        assert np.array_equal(got.path_metrics, ref.path_metrics)
        assert got.survivor_count == ref.survivor_count
        assert got.pruned_count == ref.pruned_count
        assert np.array_equal(got.known_mask, ref.known_mask)
    # undisclosed arm as well
    ref2, _ = run_with_chunk(logp, "default", None, None, width=3)
    got2, _ = run_with_chunk(logp, None, None, None, width=3)
    assert got2.u_candidates.tolist() == ref2.u_candidates.tolist()
    assert np.array_equal(got2.path_metrics, ref2.path_metrics)


# --- T1: one-hot loopback / disclosure / no-branch -------------------------------

def test_one_hot_loopback():
    rng = np.random.default_rng(TEST_SEED_A + 20)
    for field, n in ((GF4, 4), (GF32, 8)):
        u_true = rng.integers(0, field.q, size=n).tolist()
        x_true = polar_transform(np.asarray(u_true), field=field).tolist()
        one = np.full((n, field.q), -np.inf)
        one[np.arange(n), np.asarray(x_true)] = 0.0
        res = scl_decode(one, field=field, list_width_L=3, prune_rule=top_l_stub())
        assert res.u_candidates[0].tolist() == u_true
        assert res.x_candidates[0].tolist() == x_true
        # all-known disclosure returns the forced word exactly with zero metric
        full = scl_decode(one, field=field, known_positions=list(range(n)),
                          known_values=u_true, list_width_L=3, prune_rule=top_l_stub())
        assert full.survivor_count == 1
        assert full.u_candidates[0].tolist() == u_true
        assert full.path_metrics.tolist() == [0.0]
        assert full.pruned_count == 0


def test_disclosure_prefix_sizes_and_no_branch():
    rng = np.random.default_rng(TEST_SEED_B + 20)
    n = 8
    logp = normalize_rows(rng.normal(0, 1.2, size=(n, GF4.q)))
    ref = sc_decode(logp, field=GF4)
    dec = [int(v) for v in ref.u_hat]
    for k in (1, 2, 4):
        res = scl_decode(logp, field=GF4, known_positions=list(range(k)),
                         known_values=dec[:k], list_width_L=4, prune_rule=top_l_stub())
        assert res.known_count == k
        assert res.known_mask.tolist() == [i < k for i in range(n)]
        assert res.u_candidates[0][:k].tolist() == dec[:k]
    # forced non-MAP value at a disclosed position is taken without branching
    forced = (dec[0] + 2) % GF4.q
    res = scl_decode(logp, field=GF4, known_positions=[0], known_values=[forced],
                     list_width_L=2, prune_rule=top_l_stub())
    assert all(int(row[0]) == forced for row in res.u_candidates.tolist())
    assert res.path_metrics[0] >= res.path_metrics[-1]


def test_impossible_disclosed_value():
    one = np.full((2, GF4.q), -np.inf)
    one[np.arange(2), [0, 0]] = 0.0
    u_true = polar_transform([0, 0], field=GF4).tolist()
    assert u_true == [0, 0]
    bad = (u_true[0] + 1) % GF4.q
    assert_raises_match(sc_mod.ImpossibleDisclosedValueError, "impossible disclosed value",
                        sc_decode, one, field=GF4, known_positions=[0], known_values=[bad])
    # same category object: scl reuses the sc error, never a new category
    assert scl_mod.ImpossibleDisclosedValueError is sc_mod.ImpossibleDisclosedValueError
    assert_raises_match(sc_mod.ImpossibleDisclosedValueError, "impossible disclosed value",
                        scl_decode, one, field=GF4, known_positions=[0], known_values=[bad],
                        list_width_L=2, prune_rule=top_l_stub())


# --- T1: survivor bound, prune slot, order identity, contract carry-over ---------

def test_survivor_bound_across_widths():
    rng = np.random.default_rng(TEST_SEED_C + 20)
    logp = normalize_rows(rng.normal(0, 1.5, size=(8, GF4.q)))
    for width in (1, 2, 3, 5):
        res = scl_decode(logp, field=GF4, list_width_L=width, prune_rule=top_l_stub())
        assert 1 <= res.survivor_count <= width
        assert res.u_candidates.shape == (res.survivor_count, 8)
        assert res.requested_width == width


def test_prune_slot_shape():
    rng = np.random.default_rng(TEST_SEED_A + 30)
    logp = normalize_rows(rng.normal(0, 1.0, size=(4, GF4.q)))
    record = []
    res = scl_decode(logp, field=GF4, list_width_L=2, prune_rule=recording_stub(record))
    assert res.survivor_count <= 2
    assert len(record) == 4  # one prune call per undisclosed position
    for call in record:
        assert call["metrics"].dtype == np.float64 and call["metrics"].ndim == 1
        assert np.isfinite(call["metrics"]).all()
        assert isinstance(call["position"], int)
        assert call["is_spike"] is False
        assert call["width_L"] == 2
    assert [c["position"] for c in record] == [0, 1, 2, 3]


def test_width_and_prune_rejected():
    logp = np.zeros((2, GF4.q))
    for bad in (0, -1, -8):
        assert_raises_match(ValueError, "field/shape contract", scl_decode, logp,
                            field=GF4, list_width_L=bad, prune_rule=top_l_stub())
    for bad in (1.5, "2", True, None, (2,)):
        assert_raises_match(TypeError, "field/shape contract", scl_decode, logp,
                            field=GF4, list_width_L=bad, prune_rule=top_l_stub())
    try:
        scl_decode(logp, field=GF4, prune_rule=top_l_stub())
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError for missing list_width_L")
    for bad_prune in (None, 42, "top"):
        assert_raises_match(TypeError, "field/shape contract", scl_decode, logp,
                            field=GF4, list_width_L=2, prune_rule=bad_prune)

    def keep_too_many(metrics, position, is_spike, width_L):
        return np.arange(len(metrics) + 1, dtype=np.int64)

    assert_raises_match(ValueError, "field/shape contract", scl_decode, logp,
                        field=GF4, list_width_L=2, prune_rule=keep_too_many)

    def keep_oob(metrics, position, is_spike, width_L):
        return np.array([len(metrics)], dtype=np.int64)

    assert_raises_match(ValueError, "field/shape contract", scl_decode, logp,
                        field=GF4, list_width_L=2, prune_rule=keep_oob)

    def keep_empty(metrics, position, is_spike, width_L):
        return np.empty(0, dtype=np.int64)

    assert_raises_match(ValueError, "field/shape contract", scl_decode, logp,
                        field=GF4, list_width_L=2, prune_rule=keep_empty)

    def keep_bool(metrics, position, is_spike, width_L):
        return np.array([True] * min(2, len(metrics)))

    assert_raises_match(TypeError, "field/shape contract", scl_decode, logp,
                        field=GF4, list_width_L=2, prune_rule=keep_bool)


def test_order_identity():
    logp, _, _ = toy_metrics(TEST_SEED_B + 30, 8, GF4)
    ref = sc_decode(logp, field=GF4)
    dec = [int(v) for v in ref.u_hat]
    base = scl_decode(logp, field=GF4, known_positions=[0, 2, 5],
                      known_values=[dec[0], dec[2], dec[5]],
                      list_width_L=3, prune_rule=top_l_stub())
    shuf = scl_decode(logp, field=GF4, known_positions=[5, 0, 2],
                      known_values=[dec[5], dec[0], dec[2]],
                      list_width_L=3, prune_rule=top_l_stub())
    assert shuf.u_candidates.tolist() == base.u_candidates.tolist()
    assert shuf.x_candidates.tolist() == base.x_candidates.tolist()
    assert np.array_equal(shuf.path_metrics, base.path_metrics)
    assert shuf.pruned_count == base.pruned_count


def test_metric_contract_carryover():
    good = normalize_rows(np.random.default_rng(TEST_SEED_C + 30).normal(0, 1.0, size=(4, GF4.q)))
    bad_nan = good.copy()
    bad_nan[0, 0] = np.nan
    assert_raises_match(ValueError, "metric contract", scl_decode, bad_nan,
                        field=GF4, list_width_L=2, prune_rule=top_l_stub())
    bad_inf = good.copy()
    bad_inf[1, 1] = np.inf
    assert_raises_match(ValueError, "metric contract", scl_decode, bad_inf,
                        field=GF4, list_width_L=2, prune_rule=top_l_stub())
    assert_raises_match(TypeError, "metric contract", scl_decode,
                        np.zeros((4, GF4.q), dtype=bool),
                        field=GF4, list_width_L=2, prune_rule=top_l_stub())
    assert_raises_match(ValueError, "field/shape contract", scl_decode,
                        np.zeros((4, GF32.q)),
                        field=GF4, list_width_L=2, prune_rule=top_l_stub())
    assert_raises_match(ValueError, "field/shape contract", scl_decode,
                        np.zeros((3, GF4.q)),
                        field=GF4, list_width_L=2, prune_rule=top_l_stub())


# --- T1: path-refusal audit -------------------------------------------------------

def test_path_refusal_audit():
    scl_source = Path(scl_mod.__file__).read_text()
    test_source = Path(__file__).read_text()
    forbidden = [
        "work" + "space/probes",
        "bo" + "dy.py",
        "test_evidence" + "_package",
        "polar_" + "existing",
        "raw_" + "prior",
        ".n" + "pz",
        "outputs" + "_comparison",
        "resul" + "ts/",
        "par" + "quet",
        "V" + "25",
        "2026092" + "5",
        "held" + "-out",
        "E" + "VAL",
    ]
    for token in forbidden:
        assert token not in scl_source, token
        assert token not in test_source, token
    assert "from .sc import" not in scl_source  # module-attribute reuse only
    assert "open(" not in scl_source


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        start = time.perf_counter()
        fn()
        print(f"PASS {fn.__name__} ({time.perf_counter() - start:.2f}s)")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    main()
