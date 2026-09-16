"""Focused Phase 4-P5 hard-conditioning penalty gate tests.

Synthetic/injected fixtures only.  No stored data product, no real frame, no
DEV/EVAL stream, no sibling read, no method adapter and no output outside a
temporary directory.  Focused tests use their own fresh seeds >= 2026091480 and
never the frozen gate seeds 2026091470..2026091472.

Written without a pytest dependency so it runs under plain ``python`` and is
still collected by pytest: every ``test_*`` takes no arguments, uses plain
asserts and restores any monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import penalty_gate as pg
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import two_layer as tl
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import make_gf32
from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import derive_p2

FIELD = make_gf32()
REPO_ROOT = Path(__file__).resolve().parents[2]
# Fresh test-local seeds (>= 2026091480); the frozen gate seeds are only read
# from the module constants and are never used as inputs here.
TEST_SEED_A = 2026091480
TEST_SEED_B = 2026091481
TEST_SEED_C = 2026091482
TEST_SEED_D = 2026091483
TEST_SEED_E = 2026091484
TEST_SEED_F = 2026091485
TEST_SEEDS = (TEST_SEED_A, TEST_SEED_B, TEST_SEED_C, TEST_SEED_D, TEST_SEED_E, TEST_SEED_F)
PROB_TOL = 1e-12

FORBIDDEN_MARKERS = (
    "outputs_comparison",
    "model_f",
    "v72p2d5",
    "parquet",
    "ttbin",
    "dev_seed",
    "eval_seed",
    "benchmark",
    "sibling",
    "artifact",
    "results/",
    "fwht",
    "scl/crc",
    "scl_crc",
    "app_fed",
    "app_prior",
    "get_l1_app",
    "pandas",
    "pyarrow",
    "scipy",
)


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


@contextlib.contextmanager
def patched(obj, name, value):
    original = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, original)


def literal_stream(seed, n, epsilon1, profile, blocks):
    """Literal re-implementation of the documented dependent draw order."""
    e2 = pg.profile_epsilon2(profile)
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(blocks):
        high = rng.integers(0, 32, size=n).astype(np.int64)
        low = rng.integers(0, 32, size=n).astype(np.int64)
        b_high = high.copy()
        erased_high = rng.random(n) < epsilon1
        if bool(erased_high.any()):
            idx = np.where(erased_high)[0]
            b_high[idx] = rng.integers(0, 32, size=idx.size).astype(np.int64)
        b_low = low.copy()
        erased_low = rng.random(n) < e2[high]
        if bool(erased_low.any()):
            idx = np.where(erased_low)[0]
            b_low[idx] = rng.integers(0, 32, size=idx.size).astype(np.int64)
        out.append((high, low, (32 * b_high + b_low).astype(np.int64)))
    return out


def literal_tail(level, n, x):
    """Direct product-sum tail ``P[Bin(n, level) >= x]`` (no log space)."""
    return math.fsum(
        math.comb(n, j) * (level**j) * ((1.0 - level) ** (n - j)) for j in range(x, n + 1)
    )


def literal_lower_bound(x, n, target=0.05):
    """Independent bisection on the direct tail (increasing in level)."""
    if x == 0:
        return 0.0
    if x == n:
        return target ** (1.0 / n)
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        if literal_tail(mid, n, x) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def gate_kwargs(seed, blocks=2):
    return {
        "n": 256,
        "epsilon1": 0.05,
        "profile": "strong",
        "k1": 45,
        "k2": 140,
        "seeds": [seed],
        "blocks_per_seed": blocks,
    }


def test_p5_dependent_table_normalization_and_p2_maxdiff():
    spans = {"weak": 0.12, "medium": 0.24, "strong": 0.36}
    for profile, span in spans.items():
        table = pg.build_dependent_joint_table(profile=profile, epsilon1=0.05)
        assert float(np.abs(table.sum(axis=0) - 1.0).max()) <= 1e-12
        assert table.shape == (1024, 1024)
        p2 = derive_p2(table)
        value = pg.p2_cross_u1_maxdiff(p2)
        # Closed form: the per-u1 diagonal kernel spans e2, with the 31/32 factor.
        assert abs(value - span * 31.0 / 32.0) < 1e-12, (profile, value)
        e2 = pg.profile_epsilon2(profile)
        assert abs(float(e2.mean()) - 0.20) < 1e-12
        assert float(e2.min()) >= 0.0 and float(e2.max()) <= 1.0
    strong = pg.build_dependent_joint_table(profile="strong", epsilon1=0.05)
    p2 = derive_p2(strong)
    assert abs(pg.p2_cross_u1_maxdiff(p2) - 0.34875) < 1e-12
    # Literal formula oracle: p2[u1, 32*bh+bl, u2] == Pl_{e2(u1)}[u2, bl].
    e2 = pg.profile_epsilon2("strong")
    for u1 in (0, 13, 31):
        pl = tl.layer_observation_matrix(float(e2[u1]))
        for bh in (0, 5, 31):
            for bl in (0, 9, 31):
                for u2 in (0, 7, 31):
                    assert abs(p2[u1, 32 * bh + bl, u2] - pl[u2, bl]) < PROB_TOL
    # Floor helper: >= 0.30 passes, below fails; weak/medium tables are refused.
    assert pg.require_p2_maxdiff(0.30) == 0.30
    assert pg.require_p2_maxdiff(0.34875) == 0.34875
    assert_raises_match(ValueError, "p2_maxdiff", pg.require_p2_maxdiff, 0.299999)
    for profile in ("weak", "medium"):
        table = pg.build_dependent_joint_table(profile=profile, epsilon1=0.05)
        assert pg.p2_cross_u1_maxdiff(derive_p2(table)) < pg.P2_MAXDIFF_FLOOR
    assert_raises_match(ValueError, "profile", pg.profile_epsilon2, "bogus")
    assert_raises_match(
        ValueError,
        "p2",
        pg.p2_cross_u1_maxdiff,
        np.zeros((3, 4, 5), dtype=np.float64),
    )


def test_p5_sampler_determinism_and_draw_order():
    def stream(seed, blocks=3):
        rng = np.random.default_rng(seed)
        return [
            pg.sample_dependent_block(rng, n=8, epsilon1=0.05, profile="strong")
            for _ in range(blocks)
        ]

    first = stream(TEST_SEED_A)
    second = stream(TEST_SEED_A)
    other = stream(TEST_SEED_B)
    for left, right in zip(first, second):
        assert np.array_equal(left.high, right.high)
        assert np.array_equal(left.low, right.low)
        assert np.array_equal(left.bob, right.bob)
    assert any(not np.array_equal(a.high, b.high) for a, b in zip(first, other))
    literal = literal_stream(TEST_SEED_A, 8, 0.05, "strong", 3)
    for sampled, (high, low, bob) in zip(first, literal):
        assert np.array_equal(sampled.high, high)
        assert np.array_equal(sampled.low, low)
        assert np.array_equal(sampled.bob, bob)
    for sampled in first:
        assert sampled.high.min() >= 0 and sampled.high.max() < 32
        assert sampled.low.min() >= 0 and sampled.low.max() < 32
        assert sampled.bob.min() >= 0 and sampled.bob.max() < 1024
    assert_raises_match(
        TypeError, "Generator", pg.sample_dependent_block, np.random, n=4, epsilon1=0.05,
        profile="strong",
    )


def test_p5_four_cell_classifier_and_structural_impossibility():
    assert pg.classify_cell(True, True) == "both_exact"
    assert pg.classify_cell(True, False) == "operational_only"
    assert pg.classify_cell(False, True) == "oracle_only"
    assert pg.classify_cell(False, False) == "neither"
    assert set(pg.CELLS) == {"both_exact", "oracle_only", "operational_only", "neither"}
    # Structural argument: a correct L1 candidate makes the operational and
    # oracle L2 metrics bitwise identical (same block, same disclosures), so
    # op exact and oracle not exact can never both hold.  Full L1 disclosure
    # forces the candidate exact on every sampled block.
    n, k1, k2 = 4, 4, 2
    table = pg.build_dependent_joint_table(profile="strong", epsilon1=0.05)
    p1, p2 = tl.layer_metric_tables(table)
    d1 = np.arange(n, dtype=np.int64)
    d2 = tl.disclosure_coordinates(n=n, k=k2, epsilon=0.20)
    for offset in range(3):
        sample = pg.sample_dependent_block(
            np.random.default_rng(TEST_SEED_C + offset), n=n, epsilon1=0.05, profile="strong"
        )
        result = tl.run_two_layer_block(
            0,
            sample.high,
            sample.low,
            sample.bob,
            field=FIELD,
            p1_table=p1,
            p2_table=p2,
            d1=d1,
            d2=d2,
            n=n,
            k1=k1,
            k2=k2,
            toeplitz_master=TEST_SEED_F,
        )
        assert np.array_equal(result.operational.high_hat, sample.high)
        assert np.array_equal(result.p2_hat_probs, result.p2_true_probs)
        assert result.operational.exact == result.oracle.exact
        assert (
            pg.classify_cell(result.operational.exact, result.oracle.exact) != "operational_only"
        )


def test_p5_exact_lower_bound_matches_independent_brute_force():
    for n, x in ((10, 3), (10, 7), (20, 13), (50, 40)):
        got = pg.exact_lower_bound(x, n)
        assert abs(got - literal_lower_bound(x, n)) < 1e-9, (n, x)
        assert abs(literal_tail(got, n, x) - 0.05) < 1e-9, (n, x)
    for x in (365, 370, 380):
        root = pg.exact_lower_bound(x, 384)
        assert abs(literal_tail(root, 384, x) - 0.05) < 1e-9
    assert pg.exact_lower_bound(0, 384) == 0.0
    assert abs(pg.exact_lower_bound(384, 384) - 0.05 ** (1.0 / 384)) < 1e-15
    assert (
        pg.exact_lower_bound(365, 384)
        < pg.exact_lower_bound(370, 384)
        < pg.exact_lower_bound(380, 384)
    )
    assert pg.exact_lower_bound(200, 384) > 0.30
    assert pg.exact_lower_bound(1, 384) < 0.30
    assert pg.binomial_tail_probability(0.5, 10, 11) == 0.0
    assert pg.binomial_tail_probability(0.0, 10, 0) == 1.0
    assert pg.binomial_tail_probability(0.0, 10, 1) == 0.0
    assert pg.binomial_tail_probability(1.0, 10, 10) == 1.0
    assert abs(pg.binomial_tail_probability(0.3, 384, 200) - literal_tail(0.3, 384, 200)) < 1e-9
    assert_raises_match(ValueError, "0..384", pg.exact_lower_bound, 385, 384)
    assert_raises_match(ValueError, ">= 1", pg.binomial_tail_probability, 0.5, 0, 1)


def test_p5_integrity_gates_recorded_and_failure_paths():
    root = Path(tempfile.mkdtemp()) / "clean"
    run = pg.run_penalty_gate(out_dir=str(root), **gate_kwargs(TEST_SEED_A))
    assert set(run.summary["integrity"]) == set(pg.INTEGRITY_GATE_ORDER)
    assert all(run.summary["integrity"].values())
    assert run.summary["integrity_all_pass"] is True
    assert run.summary["failing_integrity_gates"] == []
    # A 2-pair run is not the frozen 384 shape: integrity passes, no candidate.
    assert run.summary["shape_is_frozen_384"] is False
    assert run.summary["outcome_label"] == "HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED"
    assert run.summary["cells"]["operational_only"] == 0

    # Truth-leak sentinel failure is caught by the operational gate.
    root2 = Path(tempfile.mkdtemp()) / "leak"
    with patched(tl, "_truth_isolation_sentinel", lambda *args, **kwargs: False):
        run2 = pg.run_penalty_gate(out_dir=str(root2), **gate_kwargs(TEST_SEED_B, blocks=1))
    assert run2.summary["integrity"]["operational_truth_leak_zero"] is False
    assert run2.summary["integrity_all_pass"] is False
    assert run2.summary["outcome_label"] == "BLOCKED"
    assert "operational_truth_leak_zero" in run2.summary["failing_integrity_gates"]

    # Budget stop marks every remaining block resource_abort and blocks the label.
    root3 = Path(tempfile.mkdtemp()) / "abort"
    run3 = pg.run_penalty_gate(
        out_dir=str(root3), total_wall_s=1e-6, **gate_kwargs(TEST_SEED_C)
    )
    assert run3.summary["resource_stop_fired"] is True
    assert run3.summary["integrity"]["resource_abort_zero"] is False
    assert run3.summary["integrity"]["pairing_coverage_complete"] is True
    assert run3.summary["outcome_label"] == "BLOCKED"
    assert "resource_abort_zero" in run3.summary["failing_integrity_gates"]

    # p2_maxdiff below the floor refuses before any decoder call, and the root
    # is never created.
    def forbidden_decode(*args, **kwargs):
        raise AssertionError("decoder must not run below the p2_maxdiff floor")

    root4 = Path(tempfile.mkdtemp()) / "floor"
    with patched(tl, "sc_decode", forbidden_decode), patched(
        pg, "p2_cross_u1_maxdiff", lambda p2: 0.1
    ):
        assert_raises_match(
            ValueError, "p2_maxdiff", pg.run_penalty_gate, out_dir=str(root4),
            **gate_kwargs(TEST_SEED_D),
        )
    assert not root4.exists()


def test_p5_cli_refusals_without_decoder_calls():
    def forbidden_decode(*args, **kwargs):
        raise AssertionError("decoder must not run before refusals")

    sandbox = Path(tempfile.mkdtemp())
    existing = sandbox / "exists"
    existing.mkdir()
    never = sandbox / "never"
    base = gate_kwargs(TEST_SEED_A)
    with patched(tl, "sc_decode", forbidden_decode):
        assert_raises_match(
            FileExistsError, "refusing to overwrite", pg.run_penalty_gate,
            out_dir=str(existing), **base,
        )
        for banned, name in (
            (2026091351, "phase-1-6"),
            (2026091360, "P4"),
            (2026091361, "P4"),
        ):
            with_kwargs = dict(base)
            with_kwargs["seeds"] = [banned]
            assert_raises_match(
                ValueError, "banned", pg.run_penalty_gate, out_dir=str(never), **with_kwargs
            )
        for override in (
            {"profile": "weak"},
            {"profile": "bogus"},
            {"k1": 46},
            {"k2": 141},
            {"n": 128},
            {"epsilon1": 0.10},
            {"seeds": [TEST_SEED_A, TEST_SEED_A]},
        ):
            with_kwargs = dict(base)
            with_kwargs.update(override)
            assert_raises_match(
                ValueError, "", pg.run_penalty_gate, out_dir=str(never), **with_kwargs
            )
    assert not never.exists()

    # CLI: exactly the frozen flags, every one required, no production default.
    parser = pg.build_parser()
    frozen_argv = [
        "--n", "256", "--epsilon1", "0.05", "--profile", "strong",
        "--k1", "45", "--k2", "140",
        "--seeds", "2026091470", "2026091471", "2026091472",
        "--blocks-per-seed", "128", "--out-dir", "example_gate_root",
    ]
    args = parser.parse_args(frozen_argv)
    assert args.n == 256 and args.epsilon1 == 0.05 and args.profile == "strong"
    assert args.k1 == 45 and args.k2 == 140 and args.blocks_per_seed == 128
    assert args.seeds == [2026091470, 2026091471, 2026091472]
    option_pairs = [
        ("--n", "256"), ("--epsilon1", "0.05"), ("--profile", "strong"),
        ("--k1", "45"), ("--k2", "140"), ("--seeds", "2026091470"),
        ("--blocks-per-seed", "128"), ("--out-dir", "example_gate_root"),
    ]
    for drop in range(len(option_pairs)):
        reduced = []
        for index, (flag, value) in enumerate(option_pairs):
            if index != drop:
                reduced.extend([flag, value])
        assert_raises_match(SystemExit, "", parser.parse_args, reduced)
    assert pg.main(
        [
            "--n", "256", "--epsilon1", "0.05", "--profile", "strong",
            "--k1", "45", "--k2", "140", "--seeds", "2026091360",
            "--blocks-per-seed", "1", "--out-dir", str(never),
        ]
    ) == 2
    assert not never.exists()


def test_p5_tiny_smoke_five_files_schema_and_accounting():
    root = Path(tempfile.mkdtemp()) / "smoke"
    started = time.perf_counter()
    run = pg.run_penalty_gate(out_dir=str(root), **gate_kwargs(TEST_SEED_E, blocks=2))
    elapsed = time.perf_counter() - started
    assert sorted(path.name for path in root.iterdir()) == sorted(pg.OUTPUT_FILES)

    plan = json.loads((root / "frozen_plan.json").read_text(encoding="utf-8"))
    assert plan["seeds"] == [TEST_SEED_E]
    assert plan["toeplitz_masters"] == [TEST_SEED_E + pg.PUBLIC_TAG_MASTER_OFFSET]
    assert plan["blocks_per_seed"] == 2 and plan["planned_pairs"] == 2
    assert abs(plan["dependent_table"]["p2_maxdiff"] - 0.34875) < 1e-12
    assert plan["dependent_table"]["column_max_deviation"] <= 1e-12
    assert plan["dependent_table"]["p2_maxdiff_floor"] == 0.30
    assert len(plan["disclosure_coordinates"]["D1"]) == 45
    assert len(plan["disclosure_coordinates"]["D2"]) == 140
    assert plan["disclosure_coordinates"]["D1"] == sorted(set(plan["disclosure_coordinates"]["D1"]))
    assert plan["attempt_consumption_point"] == pg.ATTEMPT_CONSUMPTION_POINT
    assert plan["attempts_allowed"] == 1 and plan["attempts_consumed_before"] == 0
    assert plan["attempts_consumed_by_this_run"] == 1 and plan["retries"] == 0
    assert plan["budget"] == {
        "total_wall_s": 3600.0,
        "external_timeout_s": 3600,
        "ulimit_virtual_kib": 2097152,
        "rss_bytes_max": 2147483648,
    }
    assert plan["discriminator"]["oracle_exact_min"] == 365
    assert "0.05**(1/384)" in plan["discriminator"]["definition"]
    assert plan["frozen_command"] == pg.FROZEN_COMMAND
    assert plan["claim_scope"] == pg.CLAIM_SCOPE

    per_raw = (root / "per_block_paired_outcomes.json").read_text(encoding="utf-8")
    for banned in ("high_hat", "low_hat", "label_hat", "labels_true", "u1_disclosed",
                   "u2_disclosed", "b_high", "seed_bits", "seed_hex"):
        assert banned not in per_raw, banned
    per = json.loads(per_raw)
    assert per["n_blocks"] == 2 and len(per["blocks"]) == 2
    arm_keys = (
        "outcome", "exact", "label_match", "tag_pass", "l1_provenance", "l2_provenance",
        "l1_executed", "l1_decode_failed", "l2_invoked", "l2_skipped_by_l1_failure",
        "l2_decode_failed", "tag_invoked", "key_dependent_bits", "public_control_bits",
        "nonfinite", "truth_leak_violation", "l1_error_type", "l2_error_type", "wall_s",
    )
    for record in per["blocks"]:
        assert record["cell"] in pg.CELLS
        assert record["stream_seed"] == TEST_SEED_E
        for arm_name in ("operational", "oracle"):
            for key in arm_keys:
                assert key in record[arm_name]
            assert record[arm_name]["outcome"] in tl.OUTCOMES

    transcript = json.loads((root / "transcript_accounting.json").read_text(encoding="utf-8"))
    assert transcript["mismatch_count"] == 0 and transcript["mismatches"] == []
    assert transcript["public_control_bits_per_tag"] == 2623
    assert transcript["fully_invoked_arm_bits"] == 989
    assert transcript["per_pair_disclosure_bits_per_fully_invoked_arm"] == 989
    expected_kdb = sum(
        record[arm_name]["key_dependent_bits"]
        for record in per["blocks"]
        for arm_name in ("operational", "oracle")
    )
    expected_tags = sum(
        int(record[arm_name]["tag_invoked"])
        for record in per["blocks"]
        for arm_name in ("operational", "oracle")
    )
    assert transcript["incremental"]["key_dependent_bits"] == expected_kdb
    assert transcript["incremental"]["tag_invocations"] == expected_tags
    assert transcript["incremental"]["key_dependent_bits"] == transcript["recount"]["key_dependent_bits"]
    assert (
        transcript["incremental"]["public_control_bits"]
        == transcript["recount"]["public_control_bits"]
    )

    summary = json.loads((root / "aggregate_summary.json").read_text(encoding="utf-8"))
    assert summary == run.summary
    assert set(summary["integrity"]) == set(pg.INTEGRITY_GATE_ORDER)
    assert summary["integrity_all_pass"] is True
    assert summary["outcome_label"] == "HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED"
    assert summary["cells"] == run.summary["cells"]
    assert summary["lower_bound"] == run.summary["lower_bound"]
    assert summary["wall_s"] >= 0.0
    assert summary["rss_bytes_peak"] is None or summary["rss_bytes_peak"] > 0
    assert summary["claim_scope"] == pg.CLAIM_SCOPE

    report = (root / "report.md").read_text(encoding="utf-8")
    assert "synthetic single-point N=256 hard-conditioning penalty signal only" in report
    assert "not real-data FER, efficiency, qualification or promotion" in report
    assert "interface diagnostics" in report
    assert "HARD_L1_CONDITIONING_PENALTY_NOT_CONFIRMED" in report
    assert elapsed < 300.0


def test_p5_frozen_constants_seed_sets_and_fresh_test_seeds():
    assert pg.FROZEN_SEEDS == (2026091470, 2026091471, 2026091472)
    assert pg.FROZEN_BLOCKS_PER_SEED == 128 and pg.FROZEN_PAIRS == 384
    assert pg.PUBLIC_TAG_MASTER_OFFSET == 10000
    assert pg.FROZEN_N == 256 and pg.FROZEN_K1 == 45 and pg.FROZEN_K2 == 140
    assert pg.FROZEN_EPSILON1 == 0.05 and pg.FROZEN_PROFILE == "strong"
    assert pg.PROFILE_MEAN_EPSILON2 == 0.20
    assert pg.PROFILE_FORMULAS["strong"] == "0.02 + 0.36*u1/31"
    assert pg.P2_MAXDIFF_FLOOR == 0.30
    assert pg.ORACLE_EXACT_MIN == 365 and pg.LOWER_BOUND_MIN == 0.30
    assert pg.LOWER_BOUND_TARGET == 0.05
    assert pg.FULLY_INVOKED_ARM_BITS == 989
    assert pg.DISCLOSED_BITS_PER_COORDINATE * (45 + 140) + 64 == 989
    assert tl.seed_bits_for(256) == 2623
    assert pg.ATTEMPT_ACCOUNTING == {
        "attempts_allowed": 1,
        "attempts_consumed_before": 0,
        "attempts_consumed_by_this_run": 1,
        "retries": 0,
    }
    required_refusals = (
        set(range(2026091200, 2026091214))
        | set(range(2026091314, 2026091322))
        | {2026091330, 2026091340, 2026091341, 2026091350, 2026091351, 2026091360, 2026091361}
    )
    assert pg.BANNED_SEEDS == frozenset(required_refusals)
    for banned in sorted(required_refusals):
        assert banned in pg.BANNED_SEEDS
    for seed in pg.FROZEN_SEEDS:
        assert seed not in pg.BANNED_SEEDS
        assert seed + pg.PUBLIC_TAG_MASTER_OFFSET not in pg.BANNED_SEEDS
    for seed in TEST_SEEDS:
        assert seed >= 2026091480
        assert seed not in pg.BANNED_SEEDS and seed not in pg.FROZEN_SEEDS
    own = Path(__file__).read_text(encoding="utf-8")
    assert ("." + "workbuddy") not in own
    assert ("paired_penalty" + "_gate") not in own
    for seed in pg.FROZEN_SEEDS:
        assert f"default_rng({seed})" not in own


def test_p5_no_forbidden_markers_or_import_time_effects():
    import re

    source = Path(pg.__file__).read_text(encoding="utf-8")
    lowered = source.lower()
    for marker in FORBIDDEN_MARKERS:
        assert marker not in lowered, f"forbidden marker {marker!r} in penalty_gate.py"
    for match in re.finditer(r"np\.random\.([A-Za-z_]+)\s*\(", source):
        assert match.group(1) == "default_rng", f"global RNG use: {match.group(0)}"
    assert "open(" not in source

    empty = Path(tempfile.mkdtemp())
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import comparison_bench.src.comparison_bench.formal_ir.nbpolar.penalty_gate as p; "
            "assert p.FROZEN_PAIRS == 384 and p.OUTPUT_FILES[0] == 'frozen_plan.json'",
        ],
        cwd=str(empty),
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert list(empty.iterdir()) == []


if __name__ == "__main__":
    names = sorted(n for n, v in sorted(globals().items())
                   if n.startswith("test_") and callable(v))
    failed = 0
    for name in names:
        started = time.perf_counter()
        try:
            globals()[name]()
        except Exception as err:  # noqa: BLE001 -- minimal runner reports only
            failed += 1
            print(f"FAIL {name}: {type(err).__name__}: {err}")
        else:
            print(f"ok {name} ({time.perf_counter() - started:.3f}s)")
    print(f"{len(names) - failed}/{len(names)} passed")
    sys.exit(1 if failed else 0)
