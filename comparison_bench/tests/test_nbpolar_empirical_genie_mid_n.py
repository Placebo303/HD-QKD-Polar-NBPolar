"""Focused Phase 4-P15 empirical-genie mid-N scaling gate tests.

Injected tiny/synthetic tables and arrays plus temporary roots only. No V25
NPZ content open, no Model-F/raw/held-out/real/EVAL artifact, no production
invocation and no output outside a temporary directory. Focused tests use
their own fresh seeds 2026091770..2026091785 and never the frozen P15
streams 2026091960..2026091993 (nor any official prior seed).

The frozen N=32768/65536 make real sampling/genie calls too slow for unit
tests, so runner tests patch the two documented seams
(``sample_full_block`` and the P13-shared ``block_genie_risks``) with
deterministic fakes; metrics, transform, orders, splits, statistics,
gates and checkpointing all run for real. Every ``test_*`` takes no
arguments, uses plain asserts and restores any monkeypatched module
attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import empirical_genie_mid_n as emn

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; the frozen P15 streams are only read from the
# module constants and are never used as inputs here.
TEST_TRAINS = tuple(2026091770 + i for i in range(8))
TEST_DEVS = tuple(2026091778 + i for i in range(8))

T_FACTOR_DF15 = 1.753050356
T_FACTOR_DF31 = 1.695518782  # P13's factor: must NOT appear in this gate

# Frozen K_total pinned by the packet arithmetic (floor((1.3*N*H-64)/5)).
FROZEN_K_TOTALS = ((32768, 6811), (65536, 13636))


@contextlib.contextmanager
def patched(obj, name, value):
    original = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, original)


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def injected_counts(seed: int = 2026091770) -> np.ndarray:
    """Sparse V25-like 1024x1024 count matrix: no zero Bob column."""
    rng = np.random.default_rng(seed)
    counts = np.zeros((1024, 1024), dtype=np.float64)
    cols = np.repeat(np.arange(1024), 2)
    rows = rng.integers(0, 1024, size=2048)
    counts[rows, cols] = rng.integers(1, 500, size=2048)
    extra = rng.choice(1024, size=497, replace=False)
    counts[extra, extra] += rng.integers(1, 500, size=extra.size)
    counts = counts * 4.0
    return counts / counts.sum() * 262144.0


def expected_seam(counts: np.ndarray) -> tuple:
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_construction as tc,
    )

    report = tc.target_entropies(counts)
    return report.h1, report.h2, report.total


class FakeGenie:
    """Deterministic block-risk fake with the exact calls-counter contract.

    Mirrors the runner's per-N TRAIN-then-DEV order: within each
    consecutive group of 32 calls the first 16 are TRAIN blocks and the
    last 16 are DEV blocks, so the TRAIN formula (first 32 TRAIN calls)
    differs from the DEV formula and TRAIN/DEV leakage is detectable.
    Vector length follows the decoded block (both frozen N values).
    """

    def __init__(self):
        self.blocks = 0
        self.log = []
        self.n_train = 0
        self.n_dev = 0

    def __call__(self, l1_logp, u1, l2_logp, u2, *, field, calls=None):
        if calls is not None:
            calls["genie"] = int(calls.get("genie", 0)) + 2
        k = self.blocks
        self.blocks += 1
        self.log.append(k)
        n = int(np.asarray(u1).shape[0])
        idx = np.arange(n, dtype=np.float64)
        if (k % 32) < 16:
            t = self.n_train
            self.n_train += 1
            base = float(t + 1)
            e1 = 0.005 * base + 1e-7 * idx
            h1 = 0.05 * base + 1e-6 * idx
            e2 = 0.003 * base + 1e-7 * idx
            h2 = 0.03 * base + 1e-6 * idx
        else:
            d = self.n_dev
            self.n_dev += 1
            e1 = 0.05 + 0.001 * d + 1e-7 * idx
            h1 = 0.5 + 0.01 * d + 1e-6 * idx
            e2 = 0.07 + 0.001 * d + 1e-7 * idx
            h2 = 0.7 + 0.01 * d + 1e-6 * idx
        return {"e1": e1, "h1": h1, "e2": e2, "h2": h2}


def fake_sample(rng, p_b, f_full, q_high, q_low, n):
    idx = np.arange(int(n), dtype=np.int64)
    bob = (idx % 1024).astype(np.int64)
    zeros = np.zeros(int(n), dtype=np.int64)
    return bob, zeros, zeros, zeros


def train_formula(k: int, n: int):
    idx = np.arange(n, dtype=np.float64)
    base = float(k + 1)
    return (
        0.005 * base + 1e-7 * idx,
        0.05 * base + 1e-6 * idx,
        0.003 * base + 1e-7 * idx,
        0.03 * base + 1e-6 * idx,
    )


def dev_formula(d: int, n: int):
    idx = np.arange(n, dtype=np.float64)
    return (
        0.05 + 0.001 * d + 1e-7 * idx,
        0.5 + 0.01 * d + 1e-6 * idx,
        0.07 + 0.001 * d + 1e-7 * idx,
        0.7 + 0.01 * d + 1e-6 * idx,
    )


def full_run(out, **over):
    kw = dict(
        train_seeds=list(TEST_TRAINS),
        dev_seeds=list(TEST_DEVS),
        out_dir=out,
    )
    kw.update(over)
    counts = kw.pop("counts", None)
    if counts is None:
        counts = injected_counts()
    seam = kw.pop("expected_entropies", None)
    if seam is None:
        seam = expected_seam(counts)
    return emn.run_empirical_genie_mid_n(
        counts=counts, expected_entropies=seam, **kw
    )


def run_with_fakes(out, **over):
    genie = FakeGenie()
    with patched(emn, "sample_full_block", fake_sample):
        with patched(emn, "block_genie_risks", genie):
            run = full_run(out, **over)
    return run, genie


# ---- frozen arithmetic and matrix ----

def test_frozen_k_totals_pinned():
    # floor((1.3*N*H-64)/5), H from the ratified literals; far from any
    # integer boundary under either float64 spelling of H1+H2.
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_n_scaling as tns,
    )

    for n, pinned in FROZEN_K_TOTALS:
        for h in (emn.EXPECTED_H1 + emn.EXPECTED_H2, emn.EXPECTED_TOTAL):
            raw = (1.3 * n * h - 64.0) / 5.0
            assert math.floor(raw) == pinned, (n, repr(h), repr(raw))
            assert tns.budget_k_total(n, h, 1.3) == pinned
        assert 5 * pinned + 64 <= 1.3 * n * (emn.EXPECTED_H1 + emn.EXPECTED_H2)


def test_frozen_matrix_constants_pinned():
    assert emn.FROZEN_N_VALUES == (32768, 65536)
    assert emn.FROZEN_TRAIN_SEEDS == tuple(
        [2026091960 + i for i in range(4)] + [2026091980 + i for i in range(4)]
    )
    assert emn.FROZEN_DEV_SEEDS == tuple(
        [2026091970 + i for i in range(4)] + [2026091990 + i for i in range(4)]
    )
    assert emn.FROZEN_TRAIN_BLOCKS_PER_STREAM == 4
    assert emn.FROZEN_DEV_BLOCKS_PER_STREAM == 4
    assert emn.FROZEN_TRAIN_BLOCKS_PER_N == 16
    assert emn.FROZEN_DEV_BLOCKS_PER_N == 16
    assert emn.PLANNED_GENIE_CALLS == 128  # 64 blocks x 2 layers
    assert emn.FROZEN_CHUNK_ROWS == 512
    assert set(emn.FROZEN_TRAIN_SEEDS).isdisjoint(emn.FROZEN_DEV_SEEDS)
    # Per-N and across-N stream separation of the frozen matrix.
    for pos in (0, 4):
        assert set(emn.FROZEN_TRAIN_SEEDS[pos:pos + 4]).isdisjoint(
            emn.FROZEN_DEV_SEEDS[pos:pos + 4])
    assert len(set(emn.FROZEN_TRAIN_SEEDS)) == 8
    assert len(set(emn.FROZEN_DEV_SEEDS)) == 8
    # Fresh test seeds never touch the frozen streams or known priors.
    assert set(TEST_TRAINS).isdisjoint(emn.FROZEN_TRAIN_SEEDS)
    assert set(TEST_DEVS).isdisjoint(emn.FROZEN_DEV_SEEDS)
    assert set(TEST_TRAINS).isdisjoint(emn.FROZEN_TRAIN_SEEDS + emn.FROZEN_DEV_SEEDS)
    assert set(TEST_TRAINS).isdisjoint(TEST_DEVS)


def test_p13_helpers_shared_not_reimplemented():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        empirical_genie_scaling as egs,
    )

    assert emn.block_genie_risks is egs.block_genie_risks
    assert emn.residual_for_orders is egs.residual_for_orders
    assert emn.select_empirical_split is egs.select_empirical_split
    # The df=31 P13 UCB helper is NOT shared: this gate holds 16 DEV
    # blocks per N (df=15) with its own factor.
    assert emn.student_t_ucb_95 is not egs.student_t_ucb_95


# ---- both-N grouping, separation, replay ----

def test_both_n_grouping_separation_and_call_budget():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, genie = run_with_fakes(out)
        assert sorted(p.name for p in out.iterdir()) == sorted(emn.OUTPUT_FILES)
        # N-to-seed grouping: first four streams per list serve N=32768,
        # the last four serve N=65536.
        cells = run.construction["cells"]
        assert set(cells) == {"32768", "65536"}
        assert cells["32768"]["train_seeds"] == list(TEST_TRAINS[:4])
        assert cells["32768"]["dev_seeds"] == list(TEST_DEVS[:4])
        assert cells["65536"]["train_seeds"] == list(TEST_TRAINS[4:])
        assert cells["65536"]["dev_seeds"] == list(TEST_DEVS[4:])
        # Stream separation per N and across N.
        for tag in ("32768", "65536"):
            cell = run.summary["per_n"][tag]
            assert set(cell["train_seeds"]).isdisjoint(cell["dev_seeds"]), tag
            assert len(cell["train_seeds"]) == 4 and len(cell["dev_seeds"]) == 4
        all_trains = (run.summary["per_n"]["32768"]["train_seeds"]
                      + run.summary["per_n"]["65536"]["train_seeds"])
        all_devs = (run.summary["per_n"]["32768"]["dev_seeds"]
                    + run.summary["per_n"]["65536"]["dev_seeds"])
        assert len(set(all_trains)) == 8
        assert len(set(all_devs)) == 8
        assert set(all_trains).isdisjoint(all_devs)
        # Exact call budget: 32 TRAIN + 32 DEV blocks x 2, each once.
        assert genie.blocks == 64
        assert genie.log == list(range(64))
        assert genie.n_train == 32 and genie.n_dev == 32
        assert run.summary["genie_calls"] == 128
        assert run.summary["planned_genie_calls"] == 128
        assert run.summary["integrity"]["no_unregistered_calls"] is True
        # Injected path: zero reads/attempts, exact accounting.
        assert run.summary["input_mode"] == "injected_counts"
        acc = run.summary["attempt_read_accounting"]
        assert acc["artifact_content_reads_consumed_by_this_run"] == 0
        assert acc["attempts_consumed_by_this_run"] == 0
        assert acc["open_count"] == 0
        assert run.summary["integrity"]["attempt_read_accounting_exact"] is True
        assert run.summary["integrity"]["checkpoint_accounting_consistent"] is True
        assert run.summary["integrity"]["risks_finite"] is True
        assert run.summary["integrity"]["truth_isolation"] is True
        assert run.summary["integrity"]["zero_genie_exceptions"] is True
        assert emn._NPZ_CONTENT_OPENED is False
        res = run.summary["per_n"]["32768"]["resources"]
        assert set(res) == {"wall_s", "rss_bytes_hwm", "vm_peak_kb", "vm_size_kb"}
        # Test-local seeds are not the frozen matrix: the shape gate fails.
        assert run.summary["outcome_label"] == "BLOCKED(two_n_cells_complete)"


def test_grouping_misuse_refusals_before_open():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    def forbidden_genie(*args, **kwargs):
        raise AssertionError("no genie call may happen on refusal")

    with tempfile.TemporaryDirectory() as tmp:
        with patched(emn, "load_v25_channel_counts", forbidden_loader):
            with patched(emn, "block_genie_risks", forbidden_genie):
                assert_raises_match(
                    ValueError, "4 streams per N", full_run, Path(tmp) / "a",
                    train_seeds=list(TEST_TRAINS)[:7],
                )
                assert_raises_match(
                    ValueError, "n-values", full_run, Path(tmp) / "b",
                    n_values=[32768],
                )
                assert_raises_match(
                    ValueError, "n-values", full_run, Path(tmp) / "c",
                    n_values=[32768, 65536, 131072],
                )
                assert_raises_match(
                    ValueError, "disjoint", full_run, Path(tmp) / "d",
                    dev_seeds=list(TEST_TRAINS),
                )
                assert_raises_match(
                    ValueError, "train-blocks-per-stream", full_run,
                    Path(tmp) / "e", train_blocks_per_stream=8,
                )
                assert_raises_match(
                    ValueError, "dev-blocks-per-stream", full_run,
                    Path(tmp) / "f", dev_blocks_per_stream=8,
                )
                assert_raises_match(
                    ValueError, "chunk-rows", full_run, Path(tmp) / "g",
                    chunk_rows=64,
                )
        for name in ("a", "b", "c", "d", "e", "f", "g"):
            assert not (Path(tmp) / name).exists()


def test_dev_residuals_match_formula_stats_and_no_truth_keys():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _ = run_with_fakes(out)
        lines = (out / "per_block_genie_residuals.jsonl").read_text().splitlines()
        assert len(lines) == 32
        records = [json.loads(line) for line in lines]
        assert {r["n"] for r in records} == {32768, 65536}
        # Records stream per N cell: first 16 N=32768 (DEV d=0..15),
        # then 16 N=65536 (DEV d=16..31).
        for pos, record in enumerate(records):
            n = 32768 if pos < 16 else 65536
            assert record["n"] == n
            assert record["block_index"] == pos % 4
            assert record["error"] is None
            assert set(record) == {"n", "stream_seed", "block_index",
                                   "r_empirical", "error", "resources"}
            assert set(record["resources"]) == {"wall_s", "rss_bytes_hwm",
                                                "vm_peak_kb", "vm_size_kb"}
            e1, _, e2, _ = dev_formula(pos, n)
            expected = emn.residual_for_orders(
                e1, e2,
                np.asarray(run.construction["cells"][str(n)]["l1_order"]),
                np.asarray(run.construction["cells"][str(n)]["l2_order"]),
                run.construction["cells"][str(n)]["k1"],
                run.construction["cells"][str(n)]["k2"],
            )
            assert abs(record["r_empirical"] - expected) < 1e-9, pos
        for tag, n in (("32768", 32768), ("65536", 65536)):
            vals = [r["r_empirical"] for r in records if r["n"] == n]
            assert len(vals) == 16
            stats = run.summary["per_n"][tag]["stats"]
            mean = math.fsum(vals) / 16
            std = math.sqrt(math.fsum((v - mean) ** 2 for v in vals) / 15)
            # Residuals reach ~1e4 at N=65536, so summation-order float
            # noise needs a 1e-9 absolute tolerance (relative ~1e-13).
            assert abs(stats["mean"] - mean) < 1e-9, tag
            assert abs(stats["std_sample"] - std) < 1e-9, tag
            assert stats["min"] == min(vals) and stats["max"] == max(vals)
            assert abs(stats["ucb_95_t15"] - (mean + T_FACTOR_DF15 * std / 4.0)) < 1e-9, tag
        for tag, n in (("32768", 32768), ("65536", 65536)):
            cell = run.construction["cells"][tag]
            # The frozen construction replays exactly from the pooled TRAIN
            # risks alone: DEV data never feeds it.
            replay = emn.select_empirical_split(
                n,
                np.asarray(cell["pooled_e1_mean"]),
                np.asarray(cell["pooled_h1_mean"]),
                np.asarray(cell["pooled_e2_mean"]),
                np.asarray(cell["pooled_h2_mean"]),
                cell["k_total"],
            )
            assert (replay["k1"], replay["k2"]) == (cell["k1"], cell["k2"]), tag
            assert abs(replay["residual"] - cell["train_residual"]) < 1e-15, tag
            assert replay["l1_order"].tolist() == cell["l1_order"], tag
            assert replay["l2_order"].tolist() == cell["l2_order"], tag
            # Pooled means equal the closed form over the 16 TRAIN fake
            # blocks of that N (TRAIN t=0..15 for N=32768, 16..31 for
            # N=65536).
            base = 0 if tag == "32768" else 16
            acc = [np.zeros(n) for _ in range(4)]
            for k in range(base, base + 16):
                vecs = train_formula(k, n)
                for j in range(4):
                    acc[j] += vecs[j]
            for key, vec in zip(
                ("pooled_e1_mean", "pooled_h1_mean",
                 "pooled_e2_mean", "pooled_h2_mean"),
                [v / 16 for v in acc],
            ):
                assert np.allclose(np.asarray(cell[key]), vec, rtol=0, atol=1e-12), tag
        assert run.summary["integrity"]["orders_valid_frozen_before_dev"] is True
        # The literal-K replay arm is pinned separately (frozen K pin
        # test); on injected data the run K comes from the injected
        # entropies, so only the formula arm of the gate can hold here.
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
            target_n_scaling as tns,
        )

        injected_h = run.summary["entropy"]["total"]
        for tag, n in (("32768", 32768), ("65536", 65536)):
            cell = run.construction["cells"][tag]
            assert cell["k_total"] == tns.budget_k_total(n, injected_h, 1.3), tag
            assert 5 * cell["k_total"] + 64 <= 1.3 * n * injected_h, tag
        # Scalar-only outputs carry no truth, symbol or key material.
        banned = {
            "bob", "high", "low", "u1_true", "u2_true", "a_full", "counts",
            "logp", "decision_metrics", "high_hat", "label_hat", "seed_bits",
            "rng_state", "p_b", "f_full", "r_bec", "bec",
        }

        def walk(node, keys):
            if isinstance(node, dict):
                for key, value in node.items():
                    keys.add(key)
                    walk(value, keys)
            elif isinstance(node, list):
                for value in node:
                    walk(value, keys)

        keys: set = set()
        walk(json.loads((out / "frozen_plan.json").read_text()), keys)
        walk(json.loads((out / "construction_and_allocations.json").read_text()), keys)
        walk(json.loads((out / "aggregate_summary.json").read_text()), keys)
        for line in lines:
            walk(json.loads(line), keys)
        assert not (keys & banned), keys & banned


# ---- df=15 UCB ----

def test_df15_ucb_literal_and_no_df31_factor():
    values = [0.02 + 0.001 * i for i in range(16)]
    got = emn.student_t_ucb_95(values)
    mean = math.fsum(values) / 16
    var = math.fsum((v - mean) ** 2 for v in values) / 15
    std = math.sqrt(var)
    assert got["n"] == 16
    assert abs(got["mean"] - mean) < 1e-15
    assert abs(got["std_sample"] - std) < 1e-15
    assert got["min"] == min(values) and got["max"] == max(values)
    assert abs(got["ucb_95_t15"] - (mean + 1.753050356 * std / math.sqrt(16))) < 1e-15
    # The df=31 factor belongs to P13's 32-block gate, never here.
    assert "ucb_95_t31" not in got
    short = emn.student_t_ucb_95(values[:8])
    assert short["ucb_95_t15"] is None  # test-seam shape: no t factor off N=16
    assert_raises_match(ValueError, "finite", emn.student_t_ucb_95,
                        [0.1] * 15 + [float("nan")])
    text = Path(emn.__file__).read_text(encoding="utf-8")
    assert T_FACTOR_DF31 != T_FACTOR_DF15
    assert "1.695518782" not in text
    assert "1.753050356" in text


def test_dev_block_residual_is_pure():
    e1 = np.array([0.5, 0.25, 0.125, 0.0625])
    e2 = np.array([0.1, 0.2, 0.3, 0.4])
    o1 = np.array([0, 1, 2, 3], dtype=np.int64)
    o2 = np.array([3, 2, 1, 0], dtype=np.int64)

    def boom(*args, **kwargs):
        raise AssertionError("DEV residual must add zero genie calls")

    with patched(emn, "block_genie_risks", boom):
        got = emn.dev_block_residual(
            {"e1": e1, "e2": e2}, l1_order=o1, l2_order=o2, k1=1, k2=2)
    assert abs(got - ((0.25 + 0.125 + 0.0625) + (0.2 + 0.1))) < 1e-15


# ---- refusals, accounting, failure paths ----

def test_checkpoint_resume_refusal_zero_execution():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    def forbidden_genie(*args, **kwargs):
        raise AssertionError("no genie call may happen on refusal")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        root.mkdir()
        sentinel = root / "sentinel.txt"
        sentinel.write_text("untouched", encoding="utf-8")
        with patched(emn, "load_v25_channel_counts", forbidden_loader):
            with patched(emn, "block_genie_risks", forbidden_genie):
                assert_raises_match(
                    FileExistsError, "refusing to overwrite",
                    full_run, root,
                )
        assert sentinel.read_text(encoding="utf-8") == "untouched"
        assert sorted(p.name for p in root.iterdir()) == ["sentinel.txt"]


def test_partial_failure_preserved_and_blocks_gate():
    genie = FakeGenie()
    real = genie.__call__

    def flaky(l1_logp, u1, l2_logp, u2, *, field, calls=None):
        if genie.blocks == 56:  # one DEV block of N=65536 fails
            if calls is not None:
                calls["genie"] = int(calls.get("genie", 0)) + 2
            genie.blocks += 1
            raise RuntimeError("injected block failure")
        return real(l1_logp, u1, l2_logp, u2, field=field, calls=calls)

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        with patched(emn, "sample_full_block", fake_sample):
            with patched(emn, "block_genie_risks", flaky):
                run = full_run(out)
        # The run completes with the failure recorded; partial evidence kept.
        assert sorted(p.name for p in out.iterdir()) == sorted(emn.OUTPUT_FILES)
        lines = (out / "per_block_genie_residuals.jsonl").read_text().splitlines()
        assert len(lines) == 32
        errors = [json.loads(line) for line in lines if json.loads(line)["error"] is not None]
        assert len(errors) == 1
        assert errors[0]["error"] == "RuntimeError"
        assert errors[0]["n"] == 65536
        assert errors[0]["r_empirical"] is None
        assert run.summary["integrity"]["zero_genie_exceptions"] is False
        assert run.summary["integrity"]["risks_finite"] is False
        assert run.summary["outcome_label"].startswith("BLOCKED(")
        assert run.summary["genie_calls"] == 128


def test_single_open_guard_refuses_reopen():
    saved = emn._NPZ_CONTENT_OPENED
    emn._NPZ_CONTENT_OPENED = True
    try:
        with tempfile.TemporaryDirectory() as tmp:
            # NPZ-mode call while the single open is consumed: reopen
            # refused without touching the filesystem counts path.
            assert_raises_match(
                ValueError, "reopen refused",
                emn.run_empirical_genie_mid_n,
                counts_path="/nonexistent/channel_counts.npz",
                train_seeds=list(TEST_TRAINS), dev_seeds=list(TEST_DEVS),
                out_dir=Path(tmp) / "out",
            )
    finally:
        emn._NPZ_CONTENT_OPENED = saved
    assert emn._NPZ_CONTENT_OPENED is False


def test_precondition_failure_zero_genie_and_blocked_stubs():
    seen = {"genie": 0}

    def boom_genie(*args, **kwargs):
        seen["genie"] += 1
        raise AssertionError("no genie call may happen before the contract passes")

    counts = injected_counts()
    counts[:, 0] = 0.0  # zero Bob column breaks the target contract
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(emn, "sample_full_block", fake_sample):
            with patched(emn, "block_genie_risks", boom_genie):
                assert_raises_match(
                    emn.TargetPopulationContractError,
                    "BLOCKED(target_population_contract)",
                    emn.run_empirical_genie_mid_n, counts=counts,
                    expected_entropies=(emn.EXPECTED_H1, emn.EXPECTED_H2,
                                        emn.EXPECTED_H1 + emn.EXPECTED_H2),
                    train_seeds=list(TEST_TRAINS), dev_seeds=list(TEST_DEVS),
                    out_dir=root,
                )
        assert seen == {"genie": 0}
        assert sorted(p.name for p in root.iterdir()) == sorted(emn.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(target_population_contract)"
        assert blocked["attempt_read_accounting"]["attempts_consumed_by_this_run"] == 0


def test_memory_error_classification_path():
    def oom(*args, **kwargs):
        raise MemoryError("injected exhaustion")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(emn, "sample_full_block", fake_sample):
            with patched(emn, "block_genie_risks", oom):
                assert_raises_match(
                    emn.EmpiricalGenieMidNResourceError,
                    "BLOCKED(resource_limits_met_and_no_abort)",
                    full_run, root,
                )
        assert sorted(p.name for p in root.iterdir()) == sorted(emn.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"
        assert emn._NPZ_CONTENT_OPENED is False


def test_chunk_contract_and_cli_parse_refusals():
    import subprocess

    assert emn.FROZEN_CHUNK_ROWS == 512
    proc = subprocess.run(
        [sys.executable, "-m",
         "comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_mid_n",
         "--counts", "x"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 2


def test_no_production_forbidden_access_rule():
    text = Path(emn.__file__).read_text(encoding="utf-8")
    # Functional-use tokens: the scope prose may name forbidden paths, but
    # the module must never call or import them. The BEC decision arm is
    # NONE in this gate, so no BEC residual/arm/allocation token may occur.
    for token in ("toeplitz_tag", "TAG_BITS", "seed_bits_for", "load_v31",
                  "parquet", "TTBin", "ttbin", "fwht", "sc_decode(",
                  "HOLD_", "_HOLD", "EVAL_", "_EVAL", "analytic_order",
                  "allocate_layer_ks", "bec_report_only", "r_bec", "bec_r",
                  "BEC_RULE"):
        assert token not in text, token
    assert not hasattr(emn, "sc_decode")  # SC only via accepted P13 genie call
    assert not hasattr(emn, "toeplitz_tag")
    assert "load_v25_channel_counts" in text  # the single accepted loader
    assert "block_genie_risks" in text  # the single accepted genie choke point
    assert "target_preconditions" in text  # the accepted P7 contract
    assert "budget_k_total" in text  # the accepted P12/P13 f-budget
