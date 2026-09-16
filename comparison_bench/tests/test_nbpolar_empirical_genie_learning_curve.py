"""Focused Phase 4-P14 empirical-genie learning-curve gate tests.

Injected tiny/synthetic tables and arrays plus temporary roots only. No V25
NPZ content open, no Model-F/raw/held-out/real/EVAL artifact, no production
invocation and no output outside a temporary directory. Focused tests use
their own fresh seeds 2026091741..2026091752 and never the frozen P14
streams 2026091930..2026091943 (nor any official prior seed).

The frozen N=16384 makes real sampling/genie calls too slow for unit
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

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import empirical_genie_learning_curve as ecl

REPO_ROOT = Path(__file__).resolve().parents[2]
N = 16384

# Fresh test-local seeds; the frozen P14 streams are only read from the
# module constants and are never used as inputs here.
TEST_TRAINS = tuple(2026091741 + i for i in range(8))
TEST_DEVS = tuple(2026091749 + i for i in range(4))

T_FACTOR = 1.695518782


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


def injected_counts(seed: int = 2026091741) -> np.ndarray:
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
    """Deterministic block-risk fake with the exact calls-counter contract."""

    def __init__(self):
        self.blocks = 0
        self.log = []

    def __call__(self, l1_logp, u1, l2_logp, u2, *, field, calls=None):
        if calls is not None:
            calls["genie"] = int(calls.get("genie", 0)) + 2
        k = self.blocks
        self.blocks += 1
        self.log.append(k)
        idx = np.arange(N, dtype=np.float64)
        if k < 128:
            base = float(k + 1)
            e1 = 0.005 * base + 1e-7 * idx
            h1 = 0.05 * base + 1e-6 * idx
            e2 = 0.003 * base + 1e-7 * idx
            h2 = 0.03 * base + 1e-6 * idx
        else:
            d = float(k - 128)
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


def train_formula(k: int):
    idx = np.arange(N, dtype=np.float64)
    base = float(k + 1)
    return (
        0.005 * base + 1e-7 * idx,
        0.05 * base + 1e-6 * idx,
        0.003 * base + 1e-7 * idx,
        0.03 * base + 1e-6 * idx,
    )


def dev_formula(d: int):
    idx = np.arange(N, dtype=np.float64)
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
    return ecl.run_empirical_genie_learning_curve(
        counts=counts, expected_entropies=seam, **kw
    )


def run_with_fakes(out, **over):
    genie = FakeGenie()
    with patched(ecl, "sample_full_block", fake_sample):
        with patched(ecl, "block_genie_risks", genie):
            run = full_run(out, **over)
    return run, genie


# ---- frozen arithmetic and matrix ----

def test_frozen_k_total_pinned_3399():
    # floor((1.3*16384*H-64)/5), H from the ratified literals; far from
    # any integer boundary under either float64 spelling of H1+H2.
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_n_scaling as tns,
    )

    for h in (ecl.EXPECTED_H1 + ecl.EXPECTED_H2, ecl.EXPECTED_TOTAL):
        raw = (1.3 * 16384 * h - 64.0) / 5.0
        assert math.floor(raw) == 3399, (repr(h), repr(raw))
        assert tns.budget_k_total(16384, h, 1.3) == 3399
    assert 5 * 3399 + 64 <= 1.3 * 16384 * (ecl.EXPECTED_H1 + ecl.EXPECTED_H2)


def test_frozen_matrix_constants_pinned():
    assert ecl.FROZEN_N == 16384
    assert ecl.FROZEN_PREFIX_BLOCKS == (8, 16, 32, 64, 128)
    assert ecl.FROZEN_TRAIN_SEEDS == tuple(2026091930 + i for i in range(8))
    assert ecl.FROZEN_DEV_SEEDS == tuple(2026091940 + i for i in range(4))
    assert ecl.FROZEN_TRAIN_BLOCKS_PER_STREAM == 16
    assert ecl.FROZEN_DEV_BLOCKS_PER_STREAM == 8
    assert ecl.FROZEN_TRAIN_BLOCKS == 128
    assert ecl.FROZEN_DEV_BLOCKS == 32
    assert ecl.PLANNED_GENIE_CALLS == 320
    assert ecl.FROZEN_CHUNK_ROWS == 512
    assert set(ecl.FROZEN_TRAIN_SEEDS).isdisjoint(ecl.FROZEN_DEV_SEEDS)
    # Fresh test seeds never touch the frozen streams or known priors.
    assert set(TEST_TRAINS).isdisjoint(ecl.FROZEN_TRAIN_SEEDS)
    assert set(TEST_DEVS).isdisjoint(ecl.FROZEN_DEV_SEEDS)
    assert set(TEST_TRAINS).isdisjoint(TEST_DEVS)


def test_p13_helpers_shared_not_reimplemented():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        empirical_genie_scaling as egs,
    )

    assert ecl.block_genie_risks is egs.block_genie_risks
    assert ecl.residual_for_orders is egs.residual_for_orders
    assert ecl.select_empirical_split is egs.select_empirical_split
    assert ecl.student_t_ucb_95 is egs.student_t_ucb_95


# ---- nested accumulation, call budget, streams ----

def test_nested_accumulation_no_repeated_calls_and_stream_major():
    seed_log = []
    real_factory = np.random.default_rng

    def logging_factory(seed=None, *args, **kwargs):
        seed_log.append(int(seed))
        return real_factory(seed, *args, **kwargs)

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        # Precompute outside the RNG-logging patch: injected_counts draws.
        counts = injected_counts()
        with patched(ecl, "sample_full_block", fake_sample):
            with patched(np.random, "default_rng", logging_factory):
                genie = FakeGenie()
                with patched(ecl, "block_genie_risks", genie):
                    run = full_run(out, counts=counts)
        assert sorted(p.name for p in out.iterdir()) == sorted(ecl.OUTPUT_FILES)
        # Exact call budget: 128 TRAIN + 32 DEV blocks x 2, each once.
        assert genie.blocks == 160
        assert genie.log == list(range(160))
        assert run.summary["genie_calls"] == 320
        assert run.summary["planned_genie_calls"] == 320
        assert run.summary["integrity"]["no_unregistered_calls"] is True
        # One RNG per stream in stream-major stream order: eight TRAIN
        # streams then four DEV streams (blocks run sequentially per RNG;
        # the genie fake's 160-call TRAIN-then-DEV log pins block order).
        assert seed_log == list(TEST_TRAINS) + list(TEST_DEVS)
        # Nested prefixes replay exactly from the running sums: prefix-B
        # pooled means equal the closed form over TRAIN blocks 0..B-1.
        prefixes = run.constructions["prefixes"]
        assert set(prefixes) == {"8", "16", "32", "64", "128"}
        for tag in ("8", "16", "32", "64", "128"):
            b = int(tag)
            cell = prefixes[tag]
            assert cell["train_blocks_used"] == b
            acc = [np.zeros(N) for _ in range(4)]
            for k in range(b):
                vecs = train_formula(k)
                for j in range(4):
                    acc[j] += vecs[j]
            for key, vec in zip(
                ("pooled_e1_mean", "pooled_h1_mean",
                 "pooled_e2_mean", "pooled_h2_mean"),
                [v / b for v in acc],
            ):
                assert np.allclose(np.asarray(cell[key]), vec, rtol=0, atol=1e-12), tag
        # Test-local seeds are not the frozen matrix: the shape gate fails.
        assert run.summary["outcome_label"] == "BLOCKED(streams_disjoint_frozen)"


def test_order_k_replay_per_prefix():
    with tempfile.TemporaryDirectory() as tmp:
        run, _ = run_with_fakes(Path(tmp) / "out")
    prefixes = run.constructions["prefixes"]
    for tag in ("8", "16", "32", "64", "128"):
        cell = prefixes[tag]
        replay = ecl.select_empirical_split(
            N,
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
    # The literal-K gate arm is pinned separately (3399); on injected data
    # the run K comes from the injected entropies, so only the permutation
    # and digest arm of the gate can hold here.
    assert run.summary["integrity"]["orders_valid_frozen_before_dev"] is True


def test_five_way_dev_scoring_from_one_decode():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, genie = run_with_fakes(out)
        # One decode per DEV block for all five prefixes: 32 DEV block-calls.
        assert genie.blocks == 160
        lines = (out / "per_block_genie_residuals.jsonl").read_text().splitlines()
        assert len(lines) == 32
        prefixes = run.constructions["prefixes"]
        for pos, line in enumerate(lines):
            record = json.loads(line)
            assert record["block_index"] == pos % 8
            assert record["error"] is None
            e1, h1, e2, h2 = dev_formula(pos)
            for tag in ("8", "16", "32", "64", "128"):
                cell = prefixes[tag]
                expected = ecl.residual_for_orders(
                    e1, e2,
                    np.asarray(cell["l1_order"]), np.asarray(cell["l2_order"]),
                    cell["k1"], cell["k2"],
                )
                assert abs(record[f"r_{tag}"] - expected) < 1e-9, (pos, tag)


def test_paired_ucb_and_report_only_recompute():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _ = run_with_fakes(out)
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar.construction import (
            spearman_rank_corr,
            topk_overlap,
        )

        dev = run.summary["dev"]
        assert dev["blocks"] == 32
        records = [
            json.loads(line)
            for line in (out / "per_block_genie_residuals.jsonl").read_text().splitlines()
        ]
    series = {tag: [r[f"r_{tag}"] for r in records]
              for tag in ("8", "16", "32", "64", "128")}
    for tag, stats in dev["per_prefix"].items():
        vals = series[tag]
        mean = math.fsum(vals) / 32
        var = math.fsum((v - mean) ** 2 for v in vals) / 31
        std = math.sqrt(var)
        assert abs(stats["mean"] - mean) < 1e-12, tag
        assert abs(stats["std_sample"] - std) < 1e-12, tag
        assert stats["min"] == min(vals) and stats["max"] == max(vals)
        assert abs(stats["ucb_95_t31"] - (mean + T_FACTOR * std / math.sqrt(32))) < 1e-9, tag
    base = series["8"]
    for b in (16, 32, 64, 128):
        diff = [v - m for v, m in zip(series[str(b)], base)]
        stats = dev["paired_vs_8"][f"R_{b}_minus_R_8"]
        mean = math.fsum(diff) / 32
        std = math.sqrt(math.fsum((v - mean) ** 2 for v in diff) / 31)
        assert abs(stats["mean"] - mean) < 1e-12, b
        assert abs(stats["ucb_95_t31"] - (mean + T_FACTOR * std / math.sqrt(32))) < 1e-9, b
    pairs = (("8", "16"), ("16", "32"), ("32", "64"), ("64", "128"))
    for lo, hi in pairs:
        diff = [v - m for v, m in zip(series[hi], series[lo])]
        stats = dev["adjacent"][f"R_{hi}_minus_R_{lo}_step"]
        mean = math.fsum(diff) / 32
        std = math.sqrt(math.fsum((v - mean) ** 2 for v in diff) / 31)
        assert abs(stats["mean"] - mean) < 1e-12, (lo, hi)
        assert abs(stats["ucb_95_t31"] - (mean + T_FACTOR * std / math.sqrt(32))) < 1e-9, (lo, hi)
    # Report-only: Spearman/top-K vs B=128, allocation movement, counts.
    prefixes = run.constructions["prefixes"]
    report = dev["report_only"]

    def posrank(order):
        order = np.asarray(order, dtype=np.int64)
        pos = np.empty(order.shape[0], dtype=np.int64)
        pos[order] = np.arange(order.shape[0], dtype=np.int64)
        return pos

    ref = prefixes["128"]
    for tag in ("8", "16", "32", "64"):
        cell = prefixes[tag]
        for layer in ("l1", "l2"):
            assert abs(report["spearman_vs_128"][tag][layer] - float(
                spearman_rank_corr(posrank(cell[f"{layer}_order"]),
                                   posrank(ref[f"{layer}_order"])))) < 1e-15
            depth = ref["k1"] if layer == "l1" else ref["k2"]
            if 1 <= depth <= N:
                assert abs(report["topk_overlap_vs_128"][tag][layer] - float(
                    topk_overlap(cell[f"{layer}_order"],
                                 ref[f"{layer}_order"], depth))) < 1e-15
    assert [(m["b"], m["k1"], m["k2"]) for m in report["allocation_movement"]] == [
        (int(tag), prefixes[tag]["k1"], prefixes[tag]["k2"])
        for tag in ("8", "16", "32", "64", "128")
    ]
    for tag in ("8", "16", "32", "64", "128"):
        counts = report["vs_r8_counts"][tag]
        vals, refv = series[tag], series["8"]
        assert counts == {
            "improved": sum(1 for v, m in zip(vals, refv) if v < m),
            "tied": sum(1 for v, m in zip(vals, refv) if v == m),
            "regressed": sum(1 for v, m in zip(vals, refv) if v > m),
        }, tag


def test_paired_diff_helper_edges():
    values = [0.02 + 0.001 * i for i in range(32)]
    got = ecl.paired_diff_stats(values)
    mean = math.fsum(values) / 32
    std = math.sqrt(math.fsum((v - mean) ** 2 for v in values) / 31)
    assert got["n"] == 32
    assert abs(got["mean"] - mean) < 1e-15
    assert abs(got["ucb_95_t31"] - (mean + T_FACTOR * std / math.sqrt(32))) < 1e-15
    short = ecl.paired_diff_stats(values[:8])
    assert short["ucb_95_t31"] is None
    assert_raises_match(ValueError, "finite", ecl.paired_diff_stats,
                        [0.1] * 31 + [float("nan")])


# ---- refusals, accounting ----

def test_seed_shape_and_frozen_value_refusals_before_open():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    def forbidden_genie(*args, **kwargs):
        raise AssertionError("no genie call may happen on refusal")

    with tempfile.TemporaryDirectory() as tmp:
        with patched(ecl, "load_v25_channel_counts", forbidden_loader):
            with patched(ecl, "block_genie_risks", forbidden_genie):
                assert_raises_match(
                    ValueError, "exactly 8 streams", full_run, Path(tmp) / "a",
                    train_seeds=list(TEST_TRAINS)[:7],
                )
                assert_raises_match(
                    ValueError, "disjoint", full_run, Path(tmp) / "b",
                    dev_seeds=list(TEST_TRAINS)[:4],
                )
                assert_raises_match(
                    ValueError, "n=16384", full_run, Path(tmp) / "c", n=8192,
                )
                assert_raises_match(
                    ValueError, "prefix-blocks", full_run, Path(tmp) / "d",
                    prefix_blocks=[8, 16, 32, 64],
                )
                assert_raises_match(
                    ValueError, "chunk-rows", full_run, Path(tmp) / "e",
                    chunk_rows=64,
                )
                assert_raises_match(
                    ValueError, "train-blocks-per-stream", full_run, Path(tmp) / "f",
                    train_blocks_per_stream=8,
                )
        for name in ("a", "b", "c", "d", "e", "f"):
            assert not (Path(tmp) / name).exists()


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
        with patched(ecl, "load_v25_channel_counts", forbidden_loader):
            with patched(ecl, "block_genie_risks", forbidden_genie):
                assert_raises_match(
                    FileExistsError, "refusing to overwrite",
                    full_run, root,
                )
        assert sentinel.read_text(encoding="utf-8") == "untouched"
        assert sorted(p.name for p in root.iterdir()) == ["sentinel.txt"]


def test_injected_path_zero_reads_attempts_and_files():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        run, _ = run_with_fakes(out)
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
        assert sorted(p.name for p in out.iterdir()) == sorted(ecl.OUTPUT_FILES)
        assert ecl._NPZ_CONTENT_OPENED is False
        res = run.summary["resources"]
        assert set(res) == {"wall_s", "rss_bytes_hwm", "vm_peak_kb", "vm_size_kb"}


def test_precondition_failure_zero_genie_and_blocked_stubs():
    seen = {"genie": 0}

    def boom_genie(*args, **kwargs):
        seen["genie"] += 1
        raise AssertionError("no genie call may happen before the contract passes")

    counts = injected_counts()
    counts[:, 0] = 0.0  # zero Bob column breaks the target contract
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(ecl, "sample_full_block", fake_sample):
            with patched(ecl, "block_genie_risks", boom_genie):
                assert_raises_match(
                    ecl.TargetPopulationContractError,
                    "BLOCKED(target_population_contract)",
                    ecl.run_empirical_genie_learning_curve, counts=counts,
                    expected_entropies=(ecl.EXPECTED_H1, ecl.EXPECTED_H2,
                                        ecl.EXPECTED_H1 + ecl.EXPECTED_H2),
                    train_seeds=list(TEST_TRAINS), dev_seeds=list(TEST_DEVS),
                    out_dir=root,
                )
        assert seen == {"genie": 0}
        assert sorted(p.name for p in root.iterdir()) == sorted(ecl.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(target_population_contract)"
        assert blocked["attempt_read_accounting"]["attempts_consumed_by_this_run"] == 0


def test_memory_error_classification_path():
    def oom(*args, **kwargs):
        raise MemoryError("injected exhaustion")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(ecl, "sample_full_block", fake_sample):
            with patched(ecl, "block_genie_risks", oom):
                assert_raises_match(
                    ecl.EmpiricalGenieLearningCurveResourceError,
                    "BLOCKED(resource_limits_met_and_no_abort)",
                    full_run, root,
                )
        assert sorted(p.name for p in root.iterdir()) == sorted(ecl.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"
        assert ecl._NPZ_CONTENT_OPENED is False


def test_chunk_contract_and_cli_parse_refusals():
    import subprocess

    assert ecl.FROZEN_CHUNK_ROWS == 512
    proc = subprocess.run(
        [sys.executable, "-m",
         "comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_learning_curve",
         "--counts", "x"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 2


def test_no_production_raw_hold_access_rule():
    text = Path(ecl.__file__).read_text(encoding="utf-8")
    # Functional-use tokens: the scope prose may name forbidden paths, but
    # the module must never call or import them (threshold/UCB prose and
    # "no Toeplitz/tag" scope statements are not uses).
    for token in ("toeplitz_tag", "TAG_BITS", "seed_bits_for", "load_v31",
                  "parquet", "TTBin", "ttbin", "fwht", "sc_decode(",
                  "HOLD_", "_HOLD", "EVAL_", "_EVAL", "analytic_order",
                  "allocate_layer_ks"):
        assert token not in text, token
    assert not hasattr(ecl, "sc_decode")  # SC only via accepted P13 genie call
    assert not hasattr(ecl, "toeplitz_tag")
    assert "load_v25_channel_counts" in text  # the single accepted loader
    assert "block_genie_risks" in text  # the single accepted genie choke point
    assert "target_preconditions" in text  # the accepted P7 contract
    assert "budget_k_total" in text  # the accepted P12/P13 f-budget
