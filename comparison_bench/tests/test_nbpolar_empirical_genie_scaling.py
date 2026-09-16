"""Focused Phase 4-P13 target empirical-genie f=1.3 scaling gate tests.

Injected tiny/synthetic tables and arrays plus temporary roots only.  No V25
NPZ content open, no Model-F/raw/held-out/real/EVAL artifact, no production
invocation and no output outside a temporary directory.  Focused tests use
their own fresh seeds 2026091620..2026091629 and never the frozen P13
streams 2026091860..2026091913 (nor any official prior seed).

Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments, uses plain
asserts and restores any monkeypatched module attribute in a ``finally``.
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

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import empirical_genie_scaling as egs
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32

REPO_ROOT = Path(__file__).resolve().parents[2]
FIELD = make_gf32()
# Fresh test-local seeds; the frozen P13 streams are only read from the
# module constants and are never used as inputs here.
TEST_SEED_A = 2026091620
TEST_SEED_B = 2026091621
TEST_SEED_C = 2026091622
TEST_SEED_D = 2026091623
TEST_SEED_E = 2026091624
TEST_SEED_F = 2026091625
TEST_SEED_G = 2026091626
TEST_SEED_H = 2026091627
TEST_SEED_I = 2026091628
TEST_SEED_J = 2026091629

TINY_TRAINS = (TEST_SEED_A, TEST_SEED_B, TEST_SEED_C, TEST_SEED_D)
TINY_DEVS = (TEST_SEED_E, TEST_SEED_F, TEST_SEED_G, TEST_SEED_H)

# Frozen K_total pinned by the packet arithmetic (floor((1.3*N*H-64)/5)).
FROZEN_K_TOTALS = ((4096, 840), (8192, 1693), (16384, 3399))
# Frozen report-only BEC splits from the accepted allocate_layer_ks
# (N, K_total, K1, K2, residual).
FROZEN_BEC_SPLITS = (
    (4096, 840, 37, 803, 3.363831923437399),
    (8192, 1693, 80, 1613, 2.264840263288221),
    (16384, 3399, 166, 3233, 1.2717801865443192),
)


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


def injected_counts(seed: int = TEST_SEED_A) -> np.ndarray:
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


def tiny_run(out, **over):
    # N=64 clears the frozen leakage assert under the injected entropies
    # (1.3*64*H >= 64 needs H >= 0.77); N=8 cannot, by the -64 tag term.
    kw = dict(
        counts=injected_counts(),
        n_values=[64],
        train_seeds=list(TINY_TRAINS),
        dev_seeds=list(TINY_DEVS),
        train_blocks_per_stream=1,
        dev_blocks_per_stream=2,
        out_dir=out,
    )
    kw.update(over)
    counts = kw.pop("counts")
    return egs.run_empirical_genie_scaling(
        counts=counts, expected_entropies=expected_seam(counts), **kw
    )


# ---- frozen arithmetic ----

def test_frozen_k_total_pinned():
    # floor((1.3*N*H-64)/5), H from the ratified literals; far from any
    # integer boundary under either float64 spelling of H1+H2.
    for n, pinned in FROZEN_K_TOTALS:
        for h in (egs.EXPECTED_H1 + egs.EXPECTED_H2, egs.EXPECTED_TOTAL):
            raw = (1.3 * n * h - 64.0) / 5.0
            assert math.floor(raw) == pinned, (n, repr(h), repr(raw))
            from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
                target_n_scaling as tns,
            )

            assert tns.budget_k_total(n, h, 1.3) == pinned


def test_frozen_bec_report_only_splits_pinned():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_n_scaling as tns,
    )

    for n, kt, k1, k2, resid in FROZEN_BEC_SPLITS:
        alloc = tns.allocate_layer_ks(n, egs.EXPECTED_H1, egs.EXPECTED_H2, kt)
        assert (alloc["k1"], alloc["k2"]) == (k1, k2), n
        assert abs(alloc["residual"] - resid) < 1e-12, n
        assert 5 * kt + 64 <= 1.3 * n * (egs.EXPECTED_H1 + egs.EXPECTED_H2)


def test_k_budget_clip_edges():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
        target_n_scaling as tns,
    )

    assert tns.budget_k_total(8, 0.0, 1.3) == 0  # floor(-64/5) clips to 0
    assert tns.budget_k_total(8, 1e6, 1.3) == 16  # clips to 2N
    assert_raises_match(ValueError, "k_total", egs.select_empirical_split,
                        8, np.zeros(8), np.zeros(8), np.zeros(8), np.zeros(8), 17)


# ---- literal tiny genie oracle ----

def test_literal_tiny_genie_oracle():
    # Hand-checkable N=1 rows (identity transform, so the genie SC rows
    # equal the normalized input rows) against the accepted call.
    peak = np.full(32, 0.5 / 31)
    peak[3] = 0.5
    quarter = np.full(32, 0.75 / 31)
    quarter[7] = 0.25
    l1_logp = np.log(peak.reshape(1, 32))
    l2_logp = np.log(quarter.reshape(1, 32))
    u1 = np.array([3], dtype=np.int64)
    u2 = np.array([7], dtype=np.int64)
    calls = {"genie": 0}
    risks = egs.block_genie_risks(l1_logp, u1, l2_logp, u2, field=FIELD, calls=calls)
    assert calls == {"genie": 2}
    # -log2(0.5)=1, -log2(0.25)=2, 1-0.5=0.5, 1-0.25=0.75.
    assert abs(risks["h1"][0] - 1.0) < 1e-12
    assert abs(risks["e1"][0] - 0.5) < 1e-12
    assert abs(risks["h2"][0] - 2.0) < 1e-12
    assert abs(risks["e2"][0] - 0.75) < 1e-12
    # Independent recomputation straight from the accepted call.
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.construction import (
        genie_conditionals as accepted_genie,
    )

    cond = accepted_genie(l1_logp, u1, field=FIELD, alpha=2)
    assert abs(float(-cond[0, 3] / math.log(2.0)) - risks["h1"][0]) < 1e-15
    assert abs(float(1.0 - np.exp(cond[0]).max()) - risks["e1"][0]) < 1e-15


# ---- empirical order, ties, split selection ----

def test_empirical_order_and_ties():
    e = np.array([0.5, 0.5, 0.1, 0.5])
    h = np.array([1.0, 2.0, 9.0, 1.0])
    split = egs.select_empirical_split(4, e, h, e, h, 0)
    # Worst-first (e,h,index): coords 1, 0, 3 tie on e=0.5, h breaks 1 first,
    # then index breaks 0 before 3.
    assert split["l1_order"].tolist() == [1, 0, 3, 2]
    assert split["l2_order"].tolist() == [1, 0, 3, 2]
    all_equal = egs.select_empirical_split(
        4, np.zeros(4), np.zeros(4), np.zeros(4), np.zeros(4), 2
    )
    assert all_equal["l1_order"].tolist() == [0, 1, 2, 3]
    assert (all_equal["k1"], all_equal["k2"]) == (0, 2)  # residual ties -> min K1


def test_exhaustive_split_selection_with_ties():
    # Flat risks: every split residuals-ties, so (K1,K2)=(0,K) must win.
    n = 8
    split = egs.select_empirical_split(
        n, np.ones(n), np.ones(n), np.ones(n), np.ones(n), 4
    )
    assert (split["k1"], split["k2"]) == (0, 4)
    assert abs(split["residual"] - 12.0) < 1e-12
    # Skewed risks: all budget must go to the worse layer.
    e1 = np.full(n, 0.9)
    e2 = np.full(n, 0.001)
    split = egs.select_empirical_split(n, e1, np.zeros(n), e2, np.zeros(n), 4)
    assert (split["k1"], split["k2"]) == (4, 0)
    assert abs(split["residual"] - (4 * 0.9 + 8 * 0.001)) < 1e-12


def test_scalar_dev_residual():
    e1 = np.array([0.5, 0.25, 0.125, 0.0625])
    e2 = np.array([0.1, 0.2, 0.3, 0.4])
    o1 = np.array([0, 1, 2, 3], dtype=np.int64)
    o2 = np.array([3, 2, 1, 0], dtype=np.int64)
    got = egs.residual_for_orders(e1, e2, o1, o2, 1, 2)
    assert abs(got - ((0.25 + 0.125 + 0.0625) + (0.2 + 0.1))) < 1e-15
    res = egs.dev_block_residuals(
        {"e1": e1, "e2": e2},
        emp={"l1_order": o1, "l2_order": o2, "k1": 1, "k2": 2},
        bec={"l1_order": o2, "l2_order": o1, "k1": 0, "k2": 0},
    )
    assert abs(res["r_empirical"] - got) < 1e-15
    assert abs(res["r_bec"] - (float(e1.sum()) + float(e2.sum()))) < 1e-15


def test_t_ucb_literal():
    values = [0.02 + 0.001 * i for i in range(32)]
    got = egs.student_t_ucb_95(values)
    mean = math.fsum(values) / 32
    var = math.fsum((v - mean) ** 2 for v in values) / 31
    std = math.sqrt(var)
    assert got["n"] == 32
    assert abs(got["mean"] - mean) < 1e-15
    assert abs(got["std_sample"] - std) < 1e-15
    assert got["min"] == min(values) and got["max"] == max(values)
    assert abs(got["ucb_95_t31"] - (mean + 1.695518782 * std / math.sqrt(32))) < 1e-15
    short = egs.student_t_ucb_95(values[:8])
    assert short["ucb_95_t31"] is None  # test-seam shape: no t factor off N=32
    assert_raises_match(ValueError, "finite", egs.student_t_ucb_95, [0.1] * 31 + [float("nan")])


def test_bec_report_only_no_extra_sc():
    e1 = np.array([0.5, 0.25, 0.125, 0.0625])
    e2 = np.array([0.1, 0.2, 0.3, 0.4])
    o1 = np.array([0, 1, 2, 3], dtype=np.int64)
    o2 = np.array([3, 2, 1, 0], dtype=np.int64)

    def boom(*args, **kwargs):
        raise AssertionError("BEC arm must add zero SC calls")

    with patched(egs, "genie_conditionals", boom):
        res = egs.dev_block_residuals(
            {"e1": e1, "e2": e2},
            emp={"l1_order": o1, "l2_order": o2, "k1": 2, "k2": 1},
            bec={"l1_order": o2, "l2_order": o1, "k1": 1, "k2": 3},
        )
    assert abs(res["r_empirical"] - ((0.125 + 0.0625) + (0.1 + 0.2 + 0.3))) < 1e-15
    assert abs(res["r_bec"] - ((0.5 + 0.25 + 0.125) + 0.4)) < 1e-15


def test_train_dev_separation_no_dev_leakage():
    with tempfile.TemporaryDirectory() as tmp:
        run = tiny_run(Path(tmp) / "out")
    cells = run.construction["cells"]
    assert set(cells) == {"64"}
    cell = cells["64"]
    # The frozen construction replays exactly from the pooled TRAIN risks
    # alone: DEV data never feeds it (mutation/isolation check).
    replay = egs.select_empirical_split(
        64,
        np.asarray(cell["pooled_e1_mean"]),
        np.asarray(cell["pooled_h1_mean"]),
        np.asarray(cell["pooled_e2_mean"]),
        np.asarray(cell["pooled_h2_mean"]),
        cell["k_total"],
    )
    assert (replay["k1"], replay["k2"]) == (cell["k1"], cell["k2"])
    assert abs(replay["residual"] - cell["train_residual"]) < 1e-15
    assert replay["l1_order"].tolist() == cell["l1_order"]
    assert replay["l2_order"].tolist() == cell["l2_order"]
    assert run.summary["train_seeds"] == list(TINY_TRAINS)
    assert run.summary["dev_seeds"] == list(TINY_DEVS)
    assert set(run.summary["train_seeds"]).isdisjoint(run.summary["dev_seeds"])


# ---- refusals, accounting, tiny end-to-end ----

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
        with patched(egs, "load_v25_channel_counts", forbidden_loader):
            with patched(egs, "genie_conditionals", forbidden_genie):
                assert_raises_match(
                    FileExistsError, "refusing to overwrite",
                    egs.run_empirical_genie_scaling,
                    counts=injected_counts(), n_values=[8],
                    train_seeds=list(TINY_TRAINS), dev_seeds=list(TINY_DEVS),
                    train_blocks_per_stream=1, dev_blocks_per_stream=2,
                    out_dir=root,
                )
        assert sentinel.read_text(encoding="utf-8") == "untouched"
        assert sorted(p.name for p in root.iterdir()) == ["sentinel.txt"]


def test_precondition_failure_zero_genie_and_blocked_stubs():
    seen = {"genie": 0}

    def boom_genie(*args, **kwargs):
        seen["genie"] += 1
        raise AssertionError("no genie call may happen before the contract passes")

    counts = injected_counts()
    counts[:, 0] = 0.0  # zero Bob column breaks the target contract
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(egs, "genie_conditionals", boom_genie):
            assert_raises_match(
                egs.TargetPopulationContractError,
                "BLOCKED(target_population_contract)",
                egs.run_empirical_genie_scaling, counts=counts,
                expected_entropies=(egs.EXPECTED_H1, egs.EXPECTED_H2,
                                    egs.EXPECTED_H1 + egs.EXPECTED_H2),
                n_values=[8], train_seeds=list(TINY_TRAINS),
                dev_seeds=list(TINY_DEVS),
                train_blocks_per_stream=1, dev_blocks_per_stream=2,
                out_dir=root,
            )
        assert seen == {"genie": 0}
        # Post-open failure: consumption spent, stub files carry BLOCKED.
        assert sorted(p.name for p in root.iterdir()) == sorted(egs.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(target_population_contract)"
        assert blocked["attempt_read_accounting"]["attempts_consumed_by_this_run"] == 0


def test_seed_grouping_enforced_before_open():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    with tempfile.TemporaryDirectory() as tmp:
        with patched(egs, "load_v25_channel_counts", forbidden_loader):
            assert_raises_match(
                ValueError, "4 streams per N", egs.run_empirical_genie_scaling,
                counts=injected_counts(), n_values=[8],
                train_seeds=list(TINY_TRAINS)[:3], dev_seeds=list(TINY_DEVS),
                out_dir=Path(tmp) / "a",
            )
            assert_raises_match(
                ValueError, "disjoint", egs.run_empirical_genie_scaling,
                counts=injected_counts(), n_values=[8],
                train_seeds=list(TINY_TRAINS), dev_seeds=list(TINY_TRAINS),
                out_dir=Path(tmp) / "b",
            )
            assert_raises_match(
                ValueError, "chunk-rows", egs.run_empirical_genie_scaling,
                counts=injected_counts(), n_values=[8],
                train_seeds=list(TINY_TRAINS), dev_seeds=list(TINY_DEVS),
                chunk_rows=64, out_dir=Path(tmp) / "c",
            )
        for name in ("a", "b", "c"):
            assert not (Path(tmp) / name).exists()


def test_no_production_loader_on_injected_path():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("production loader must not be called")

    with tempfile.TemporaryDirectory() as tmp:
        with patched(egs, "load_v25_channel_counts", forbidden_loader):
            run = tiny_run(Path(tmp) / "out")
        assert run.summary["input_mode"] == "injected_counts"
        acc = run.summary["attempt_read_accounting"]
        assert acc["artifact_content_reads_consumed_by_this_run"] == 0
        assert acc["attempts_consumed_by_this_run"] == 0
        assert acc["open_count"] == 0
        assert run.summary["integrity"]["attempt_read_accounting_exact"] is True


def test_tiny_end_to_end_files_calls_and_gates():
    seen = {"genie": 0}
    original = egs.genie_conditionals

    def counting(*args, **kwargs):
        seen["genie"] += 1
        return original(*args, **kwargs)

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        with patched(egs, "genie_conditionals", counting):
            run = tiny_run(out)
        assert sorted(p.name for p in out.iterdir()) == sorted(egs.OUTPUT_FILES)
        # 4 TRAIN + 8 DEV blocks x 2 genie calls: exact call budget.
        assert seen == {"genie": 24}
        assert run.summary["genie_calls"] == 24
        assert run.summary["planned_genie_calls"] == 24
        assert run.summary["integrity"]["no_unregistered_calls"] is True
        assert run.summary["integrity"]["zero_genie_exceptions"] is True
        assert run.summary["integrity"]["truth_isolation"] is True
        assert run.summary["integrity"]["risks_finite"] is True
        assert run.summary["outcome_label"] == "BLOCKED(three_n_cells_complete)"
        lines = (out / "per_block_genie_residuals.jsonl").read_text().splitlines()
        assert len(lines) == 8
        first = json.loads(lines[0])
        assert set(first) == {"n", "stream_seed", "block_index", "r_empirical", "r_bec", "error"}
        assert first["error"] is None
        # Per-N resources recorded with Linux Vm fields present-or-null.
        res = run.summary["per_n"]["64"]["resources"]
        assert set(res) == {"wall_s", "rss_bytes_hwm", "vm_peak_kb", "vm_size_kb"}
        # Scalar-only: no symbol/key/metric arrays persisted anywhere.
        for name in egs.OUTPUT_FILES:
            if name.endswith((".json", ".jsonl", ".md")):
                text = (out / name).read_text()
                assert "decision_metrics" not in text and "high_hat" not in text


def test_output_keys_carry_no_truth():
    banned = {
        "bob", "high", "low", "u1_true", "u2_true", "a_full", "counts",
        "logp", "decision_metrics", "high_hat", "label_hat", "seed_bits",
        "rng_state", "p_b", "f_full",
    }

    def walk(node, keys):
        if isinstance(node, dict):
            for key, value in node.items():
                keys.add(key)
                walk(value, keys)
        elif isinstance(node, list):
            for value in node:
                walk(value, keys)

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        tiny_run(out)
        keys: set = set()
        walk(json.loads((out / "frozen_plan.json").read_text()), keys)
        walk(json.loads((out / "construction_and_allocations.json").read_text()), keys)
        walk(json.loads((out / "aggregate_summary.json").read_text()), keys)
        for line in (out / "per_block_genie_residuals.jsonl").read_text().splitlines():
            walk(json.loads(line), keys)
    assert not (keys & banned), keys & banned


def test_memory_error_classification_path():
    def oom(*args, **kwargs):
        raise MemoryError("injected exhaustion")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(egs, "block_genie_risks", oom):
            assert_raises_match(
                egs.EmpiricalGenieScalingResourceError,
                "BLOCKED(resource_limits_met_and_no_abort)",
                egs.run_empirical_genie_scaling,
                counts=injected_counts(),
                expected_entropies=expected_seam(injected_counts()),
                n_values=[64], train_seeds=list(TINY_TRAINS),
                dev_seeds=list(TINY_DEVS),
                train_blocks_per_stream=1, dev_blocks_per_stream=2,
                out_dir=root,
            )
        # Checkpoints preserved, BLOCKED finalized, never rerun.
        assert sorted(p.name for p in root.iterdir()) == sorted(egs.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"
        assert egs._NPZ_CONTENT_OPENED is False


def test_resource_stop_path_is_blocked_error():
    with tempfile.TemporaryDirectory() as tmp:
        with patched(egs, "_budget_exceeded", lambda *a, **k: "wall_s"):
            assert_raises_match(
                egs.EmpiricalGenieScalingResourceError,
                "BLOCKED(resource_limits_met_and_no_abort)",
                tiny_run, Path(tmp) / "out",
            )


def test_chunk_contract_and_cli_parse_refusals():
    import subprocess

    assert egs.FROZEN_CHUNK_ROWS == 512
    # CLI parse failure refuses before any NPZ access (exit code 2 from argparse).
    proc = subprocess.run(
        [sys.executable, "-m",
         "comparison_bench.src.comparison_bench.formal_ir.nbpolar.empirical_genie_scaling",
         "--counts", "x"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 2


def test_no_production_raw_hold_access_rule():
    text = Path(egs.__file__).read_text(encoding="utf-8")
    # Functional-use tokens: the scope prose may name forbidden paths, but
    # the module must never call or import them (threshold/UCB prose and
    # "no Toeplitz/tag" scope statements are not uses).
    for token in ("toeplitz_tag", "TAG_BITS", "seed_bits_for", "load_v31",
                  "parquet", "TTBin", "ttbin", "fwht", "sc_decode(",
                  "HOLD_", "_HOLD", "EVAL_", "_EVAL"):
        assert token not in text, token
    assert not hasattr(egs, "sc_decode")  # SC only via accepted genie call
    assert not hasattr(egs, "toeplitz_tag")
    assert "load_v25_channel_counts" in text  # the single accepted loader
    assert "genie_conditionals" in text  # the single accepted genie choke point
