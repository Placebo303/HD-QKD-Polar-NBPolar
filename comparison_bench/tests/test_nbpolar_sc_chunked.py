"""Focused Phase 4-P11 tests: exact chunked minus-node vs unchunked golden path.

Injected arrays only with fresh test-local seeds. No out-of-scope store,
private data, or gate-output path is touched; the frozen gate seed is read
from the runner constants only and is never executed here. Temporary
directories only.

Written without a pytest dependency so it runs under plain ``python`` and
is still collected by pytest: every ``test_*`` takes no arguments, uses
plain asserts and restores any monkeypatched module attribute in ``finally``.
"""

from __future__ import annotations

import inspect
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import sc as sc_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import sc_chunked_gate as gate_mod
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.sc import (
    _combination_index,
    _normalize_rows,
    sc_decode,
)

FIELD = make_gf32()
Q = 32
ALPHA = 2
CHUNKS = [32, 128, 512, 2048]
PRIM_ROWS = [1, 31, 32, 33, 127, 128, 129, 511, 512, 513, 2048]
# Fresh test-local seeds; the frozen gate seed is never executed in tests.
TEST_SEED_A = 2026091811
TEST_SEED_B = 2026091812
TEST_SEED_C = 2026091813


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


def gen_pair(rng, kind, rows):
    if kind == "moderate":
        return rng.uniform(-20.0, 0.0, (rows, Q)), rng.uniform(-20.0, 0.0, (rows, Q))
    if kind == "wide":
        return rng.uniform(-160.0, 0.0, (rows, Q)), rng.uniform(-160.0, 0.0, (rows, Q))
    if kind == "neginf":
        a = rng.uniform(-20.0, 0.0, (rows, Q))
        b = rng.uniform(-20.0, 0.0, (rows, Q))
        a[((np.arange(rows)[:, None] * 7 + np.arange(Q)[None, :]) % 4 == 0)] = -np.inf
        b[((np.arange(rows)[:, None] * 5 + np.arange(Q)[None, :] + 1) % 4 == 0)] = -np.inf
        for i in range(rows):
            if not np.isfinite(a[i]).any():
                a[i, (i * 5) % Q] = -5.0
            if not np.isfinite(b[i]).any():
                b[i, (i * 3 + 1) % Q] = -5.0
        return a, b
    raise ValueError(kind)


def run_with_chunk(metrics, chunk, kp=None, kv=None):
    """Run sc_decode with _minus_block forced to an explicit chunk_rows."""
    orig = sc_mod._minus_block
    if chunk == "default":
        return sc_decode(metrics, field=FIELD, alpha=ALPHA,
                         known_positions=kp, known_values=kv)
    sc_mod._minus_block = lambda f, s, idx: orig(f, s, idx, chunk_rows=chunk)  # noqa: E731
    try:
        return sc_decode(metrics, field=FIELD, alpha=ALPHA,
                         known_positions=kp, known_values=kv)
    finally:
        sc_mod._minus_block = orig
        assert sc_mod._minus_block is orig


def attempt(fn, *args, **kwargs):
    try:
        return {"raised": False, "result": fn(*args, **kwargs)}
    except Exception as exc:  # noqa: BLE001 — parity needs type+message
        return {"raised": True, "exc_type": type(exc).__name__, "message": str(exc)}


def cmp_valid(direct, got):
    dm_d = np.asarray(direct.decision_metrics)
    dm_g = np.asarray(got.decision_metrics)
    ds_d = np.asarray(direct.decision_log_scores)
    ds_g = np.asarray(got.decision_log_scores)
    return bool(
        direct.status == got.status
        and np.array_equal(np.asarray(direct.u_hat), np.asarray(got.u_hat))
        and np.array_equal(np.asarray(direct.x_hat), np.asarray(got.x_hat))
        and np.array_equal(dm_d, dm_g)
        and np.array_equal(ds_d, ds_g)
        and (np.isfinite(dm_d) == np.isfinite(dm_g)).all()
        and np.array_equal(np.asarray(direct.known_mask), np.asarray(got.known_mask))
        and int(direct.known_count) == int(got.known_count)
        and direct.metric_provenance == got.metric_provenance
    )


def test_chunk_default_is_512():
    sig = inspect.signature(sc_mod._minus_block)
    param = sig.parameters["chunk_rows"]
    assert param.default == 512
    assert param.kind is inspect.Parameter.KEYWORD_ONLY
    rng = np.random.default_rng(TEST_SEED_A)
    first, second = gen_pair(rng, "moderate", 100)
    index = _combination_index(FIELD, ALPHA, Q)
    assert np.array_equal(sc_mod._minus_block(first, second, index),
                          sc_mod._minus_block(first, second, index, chunk_rows=512))


def test_none_is_golden_direct():
    rng = np.random.default_rng(TEST_SEED_A + 1)
    index = _combination_index(FIELD, ALPHA, Q)
    for rows, kind in ((1, "moderate"), (33, "wide"), (129, "neginf")):
        first, second = gen_pair(rng, kind, rows)
        got = sc_mod._minus_block(first, second, index, chunk_rows=None)
        # Literal accepted expression recomputed in-test as drift guard.
        gathered = first[:, index] + second[:, None, :]
        ref = _normalize_rows(np.logaddexp.reduce(gathered, axis=2))
        assert np.array_equal(got, ref)


def test_primitive_exact_parity_matrix():
    rng = np.random.default_rng(TEST_SEED_A + 2)
    index = _combination_index(FIELD, ALPHA, Q)
    cells = 0
    for rows in PRIM_ROWS:
        for kind in ("moderate", "wide", "neginf"):
            first, second = gen_pair(rng, kind, rows)
            ref = sc_mod._minus_block(first, second, index, chunk_rows=None)
            for chunk in CHUNKS:
                got = sc_mod._minus_block(first, second, index, chunk_rows=chunk)
                assert np.array_equal(got, ref), (rows, kind, chunk)
                assert (np.isfinite(got) == np.isfinite(ref)).all()
                cells += 1
    assert cells == len(PRIM_ROWS) * 3 * len(CHUNKS)


def check_full_sc_parity(n, seed):
    rng = np.random.default_rng(seed)
    f1 = rng.uniform(-20.0, 0.0, (n, Q))
    f2 = rng.uniform(-160.0, 0.0, (n, Q))
    f3 = rng.uniform(-20.0, 0.0, (n, Q))
    for j in range(n):
        if j % 5 == 4:
            f3[j, 0::2] = -np.inf
    pos = np.sort(rng.choice(n, n // 4, replace=False)).astype(np.int64)

    cases = [("F1", f1, None, None), ("F2", f2, None, None), ("F3", f3, None, None)]
    att_free = attempt(run_with_chunk, f1, None)
    assert not att_free["raised"]
    dm_free = np.asarray(att_free["result"].decision_metrics)
    v4 = np.array([int(np.argmax(dm_free[p])) for p in pos.tolist()], dtype=np.int64)
    assert all(bool(np.isfinite(dm_free[p, v])) for p, v in zip(pos.tolist(), v4.tolist()))
    cases.append(("K4", f1, pos, v4))
    c3 = rng.uniform(-12.0, 0.0, (n, Q))
    for j in range(n):
        if j % 3 == 0:
            c3[j, 1::2] = -np.inf
    att_c3 = attempt(run_with_chunk, c3, None)
    assert not att_c3["raised"]
    dm_c3 = np.asarray(att_c3["result"].decision_metrics)
    v3 = np.array([int(np.argmax(dm_c3[p])) for p in pos.tolist()], dtype=np.int64)
    assert all(bool(np.isfinite(dm_c3[p, v])) for p, v in zip(pos.tolist(), v3.tolist()))
    cases.append(("C3", c3, pos, v3))
    exact_tie = np.zeros((n, Q))
    ramp = np.tile(np.arange(Q, dtype=np.float64) - 31.0, (n, 1))
    near_tie = np.tile(np.zeros(Q), (n, 1))
    near_tie[:, 1] = -1e-9
    cases += [("T5_exact", exact_tie, None, None), ("T5_ramp", ramp, None, None),
              ("T5_near", near_tie, None, None)]
    for cid, metrics, kp, kv in cases:
        att_d = attempt(run_with_chunk, metrics, None, kp, kv)
        assert not att_d["raised"], (n, cid)
        for chunk in CHUNKS + ["default"]:
            att_c = attempt(run_with_chunk, metrics, chunk, kp, kv)
            assert not att_c["raised"], (n, cid, chunk)
            assert cmp_valid(att_d["result"], att_c["result"]), (n, cid, chunk)

    found = False
    for t in range(400):
        k = 16 if t < 200 else 32
        kk = k if k <= n else n // 2
        cpos = ((t * 7 + np.arange(kk) * 3) % n).astype(np.int64)
        cval = rng.integers(0, Q, kk).astype(np.int64)
        cbase = rng.uniform(-12.0, 0.0, (n, Q))
        for j in range(0, n, 2):
            cbase[j, 1:] = -np.inf
        att_d = attempt(run_with_chunk, cbase, None, cpos, cval)
        if att_d["raised"] and att_d["exc_type"] == "ImpossibleDisclosedValueError":
            for chunk in CHUNKS + ["default"]:
                att_c = attempt(run_with_chunk, cbase, chunk, cpos, cval)
                assert att_c["raised"], (n, "C4", chunk)
                assert att_c["exc_type"] == att_d["exc_type"]
                assert att_c["message"] == att_d["message"]
            found = True
            break
    assert found, f"N={n} C4 impossible-disclosure control not established"

    bad = np.zeros((8, Q))
    bad_nan = bad.copy()
    bad_nan[0, 0] = np.nan
    bad_inf = bad.copy()
    bad_inf[1, 1] = np.inf
    bad_row = bad.copy()
    bad_row[2, :] = -np.inf
    invalid = [
        bad_nan, bad_inf, bad_row, np.zeros((8, Q + 1)), np.zeros((48, Q)),
        np.zeros(Q), np.zeros((8, Q), dtype=bool),
    ]
    for idx, metrics in enumerate(invalid):
        att_d = attempt(run_with_chunk, metrics, None)
        assert att_d["raised"], (n, idx)
        for chunk in CHUNKS + ["default"]:
            att_c = attempt(run_with_chunk, metrics, chunk)
            assert att_c["raised"], (n, idx, chunk)
            assert att_c["exc_type"] == att_d["exc_type"]
            assert att_c["message"] == att_d["message"]


def test_full_sc_parity_n64():
    check_full_sc_parity(64, TEST_SEED_B)


def test_full_sc_parity_n256():
    check_full_sc_parity(256, TEST_SEED_C)


def test_public_signature_unchanged():
    sig = inspect.signature(sc_decode)
    params = list(sig.parameters.values())
    assert [p.name for p in params] == [
        "logp_x", "field", "alpha", "known_positions", "known_values"]
    assert params[0].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in params[1:])
    assert params[1].default is inspect.Parameter.empty
    assert params[2].default == 2
    assert params[3].default is None and params[4].default is None
    assert not any("chunk" in p.name for p in params)


def test_invalid_chunk_sizes_rejected():
    rng = np.random.default_rng(TEST_SEED_A + 3)
    first, second = gen_pair(rng, "moderate", 10)
    index = _combination_index(FIELD, ALPHA, Q)
    for bad in (True, False, 1.5, 512.0, "512", "", (512,), object()):
        assert_raises_match(TypeError, "chunk_rows",
                            sc_mod._minus_block, first, second, index, chunk_rows=bad)
    for bad in (0, -1, -512):
        assert_raises_match(ValueError, "chunk_rows",
                            sc_mod._minus_block, first, second, index, chunk_rows=bad)
    # Non-bool integrals (including numpy integers) are accepted.
    for good in (1, 33, np.int64(32)):
        got = sc_mod._minus_block(first, second, index, chunk_rows=good)
        assert got.shape == (10, Q)


def test_gate_runner_cli_requires_every_argument():
    parser = gate_mod.build_parser()
    for argv in ([], ["--seed", "1"], ["--seed", "1", "--chunk-rows", "512"]):
        try:
            parser.parse_args(argv)
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError(f"expected SystemExit for {argv}")
    # Frozen constants match the packet; read from constants, never executed.
    assert gate_mod.FROZEN_SEED == 2026091800
    assert gate_mod.FROZEN_CHUNK_ROWS == 512
    assert gate_mod.N_PAIRED == 65536 and gate_mod.N_LARGE == 262144
    assert gate_mod.RSS_HARD_LIMIT_BYTES == 1610612736
    assert gate_mod.FOUR_FILES == [
        "frozen_plan.json", "equivalence_records.json",
        "scaling_record.json", "report.md"]


def test_gate_runner_refusals_before_first_decode():
    orig_decode = sc_mod.sc_decode

    def bomb(*args, **kwargs):
        raise AssertionError("formal sc_decode must not run on a refusal path")

    sc_mod.sc_decode = bomb
    try:
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "gate"
            existing.mkdir()
            assert_raises(FileExistsError, gate_mod.run_chunked_gate,
                          seed=TEST_SEED_A, chunk_rows=512, out_dir=str(existing))
            missing = Path(tmp) / "never-created"
            assert_raises_match(ValueError, "seed", gate_mod.run_chunked_gate,
                                seed=TEST_SEED_A, chunk_rows=512, out_dir=str(missing))
            assert not missing.exists()
            assert_raises_match(ValueError, "chunk", gate_mod.run_chunked_gate,
                                seed=gate_mod.FROZEN_SEED, chunk_rows=32,
                                out_dir=str(missing))
            assert not missing.exists()
    finally:
        sc_mod.sc_decode = orig_decode
    assert sc_mod.sc_decode is orig_decode


def test_no_production_invocation_rule():
    source = Path(__file__).read_text()
    # Tokens assembled so the literals themselves never occur in this file.
    # (The frozen-seed constant check in the CLI test intentionally holds the
    # seed literal and is therefore not part of this list.)
    forbidden = [
        "exact_chunked" + "_sc_gate",
        "held" + "-out",
        "held" + "out",
        "E" + "VAL",
        ".n" + "pz",
        "outputs" + "_comparison",
        "res" + "ults/",
    ]
    for token in forbidden:
        assert token not in source, token


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        start = time.perf_counter()
        fn()
        print(f"PASS {fn.__name__} ({time.perf_counter() - start:.2f}s)")
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    main()
