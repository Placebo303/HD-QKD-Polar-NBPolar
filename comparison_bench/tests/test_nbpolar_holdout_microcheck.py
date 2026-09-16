"""Focused Phase 4-P18 N=32768 1M-HOLD operational-microcheck tests.

Injected tables/arrays and temporary roots only. The V25 1M TRAIN NPZ and the
registered HOLD pairs parquet are NEVER content-opened (the only files named
after them here are throwaway temporary stubs with patched loaders); the real
P16 construction root, the real split manifest and every real evidence root
are never touched. Focused tests use their own fresh seeds
``2026092060..2026092064`` and never the frozen P18 tag master 2026092050 for
real scoring, the P16 streams 2026092000..2003 / 2026092010..2017, the P17
streams 2026092030..2037, nor any prior/probe seed.

The frozen N=32768 makes real SC calls too slow for runner tests, so runner
tests patch the documented ``run_operational_block`` seam with a scripted
deterministic fake; tables, block formation, transform, NLL scoring, gates,
accounting and checkpointing all run for real. The real operational helper is
exercised separately at tiny n with real SC and the real P18-domain tag.
Every ``test_*`` takes no arguments, uses plain asserts and restores any
monkeypatched module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    holdout_microcheck as hm,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13 as opf,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13_replication as opr,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never the frozen tag master or any frozen stream.
TEST_SEEDS = (2026092060, 2026092061, 2026092062, 2026092063)
TEST_MASTER = 2026092064
TEST_SPARES = (2026092065, 2026092066)

FROZEN_LEAKAGE = 34119  # 5 * 6811 + 64
FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63
FROZEN_L1_ONLY_BITS = 5 * 319  # 1595


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


def injected_counts(seed: int = 2026092060) -> np.ndarray:
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


def fab_digest(cell: dict) -> str:
    payload = {
        "n": int(cell["n"]),
        "k_total": int(cell["k_total"]),
        "k1": int(cell["k1"]),
        "k2": int(cell["k2"]),
        "l1_order": [int(v) for v in cell["l1_order"]],
        "l2_order": [int(v) for v in cell["l2_order"]],
        "pooled_e1_mean": [float(v) for v in cell["pooled_e1_mean"]],
        "pooled_h1_mean": [float(v) for v in cell["pooled_h1_mean"]],
        "pooled_e2_mean": [float(v) for v in cell["pooled_e2_mean"]],
        "pooled_h2_mean": [float(v) for v in cell["pooled_h2_mean"]],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def make_construction_file(directory, *, tamper=None):
    """Fabricate a canonical-shape predecessor file (never the real P16 root)."""
    directory = Path(directory)
    n = 32768
    rng = np.random.default_rng(2026092064)
    l1 = rng.permutation(n).tolist()
    l2 = rng.permutation(n).tolist()
    zeros = [0.0] * n
    cell = {
        "n": n,
        "k_total": 6811,
        "k_total_raw": 6811.78,
        "k1": 319,
        "k2": 6492,
        "l1_order": l1,
        "l2_order": l2,
        "pooled_e1_mean": list(zeros),
        "pooled_h1_mean": list(zeros),
        "pooled_e2_mean": list(zeros),
        "pooled_h2_mean": list(zeros),
        "train_seeds": [2026092000, 2026092001, 2026092002, 2026092003],
        "dev_seeds": [2026092010 + i for i in range(8)],
    }
    clean_hex = fab_digest(cell)
    if tamper == "k1":
        cell["k1"] = 320
    elif tamper == "k2":
        cell["k2"] = 6491
    elif tamper == "order-dup":
        cell["l2_order"][0] = cell["l2_order"][1]
    elif tamper == "n":
        cell["n"] = 16384
    stored_hex = clean_hex
    if tamper == "digest":
        stored_hex = ("0" if clean_hex[0] != "0" else "1") + clean_hex[1:]
    cell["freeze_sha256"] = stored_hex
    doc = {
        "protocol": "nbpolar-p18-tampered" if tamper == "protocol"
        else "nbpolar-p16-operational-f13-gate",
        "frozen_before_first_dev": True,
        "cell": cell,
    }
    path = directory / "construction_and_allocation.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path, clean_hex


def make_manifest(directory, *, tamper=None, name="split_manifest.json"):
    frames = {"train": 1200, "val": 400, "hold": 400}
    pairs = {"train": 307200, "val": 102400, "hold": 102400}
    schema = hm.FROZEN_MANIFEST_SCHEMA
    source = "type2_1M_20260121_184040"
    per = {source: {"frames": dict(frames), "pairs": dict(pairs)}}
    if tamper == "hold-frames":
        per[source]["frames"]["hold"] = 399
    elif tamper == "hold-pairs":
        per[source]["pairs"]["hold"] = 102399
    elif tamper == "schema":
        schema = "nbldpc_v25_split_manifest_v2"
    elif tamper == "missing-source":
        per = {"type2_2M_20260121_183657": per[source]}
    path = Path(directory) / name
    path.write_text(
        json.dumps({"schema": schema, "per_source": per}), encoding="utf-8"
    )
    return path


def injected_hold_table(
    *, frames=400, first_frame=1600, per_frame=256, seed=2026092060, extras=True
):
    """Deterministic 1M-HOLD-like pairs frame; shuffled rows, extra non-HOLD rows."""
    rng = np.random.default_rng(seed)
    total = frames * per_frame
    frame_id = np.repeat(np.arange(first_frame, first_frame + frames), per_frame)
    pair_idx = np.tile(np.arange(per_frame), frames)
    alice = rng.integers(0, 1024, size=total)
    bob = rng.integers(0, 1024, size=total)
    df = pd.DataFrame({
        "frame_id": frame_id,
        "pair_idx": pair_idx,
        "alice_symbol": alice,
        "bob_symbol": bob,
    })
    if extras:
        extra = pd.DataFrame({
            "frame_id": np.repeat([1599, 2000], per_frame),
            "pair_idx": np.tile(np.arange(per_frame), 2),
            "alice_symbol": rng.integers(0, 1024, size=2 * per_frame),
            "bob_symbol": rng.integers(0, 1024, size=2 * per_frame),
        })
        df = pd.concat([df, extra], ignore_index=True)
    return df.sample(frac=1.0, random_state=int(seed)).reset_index(drop=True)


def mutate_hold(df, how):
    out = df.copy()
    if how == "drop-frame":
        out = out[out["frame_id"] != 1700]
    elif how == "pair-gap":
        row = out[(out["frame_id"] == 1600) & (out["pair_idx"] == 255)].index[0]
        out.loc[row, "pair_idx"] = 254
    elif how == "extra-frame-rows":
        row = out[out["frame_id"] == 1998].index[0]
        dup = out.loc[[row]].copy()
        dup["pair_idx"] = dup["pair_idx"] + 256
        out = pd.concat([out, dup], ignore_index=True)
    elif how == "symbol-range":
        row = out[out["frame_id"] == 1600].index[0]
        out.loc[row, "bob_symbol"] = 1024
    elif how == "shifted-range":
        out = out.copy()
        out["frame_id"] = out["frame_id"] + 100
    elif how == "no-hold":
        out = out[out["frame_id"].isin([1599, 2000])]
    else:
        raise AssertionError(f"unknown mutation {how}")
    return out


class FakeArm:
    """Scripted operational-block fake following the accepted result contract.

    ``high_hat`` mirrors the true high layer on tag outcomes so ``l1_correct``
    is exercised; L1 failures disclose only ``5*K1`` bits and make one SC call.
    """

    def __init__(self, script=None):
        self.script = list(script) if script else ["exact"] * 3
        self.n = 0
        self.seen = []

    def __call__(self, **kwargs):
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
            seed_bits_for,
        )

        self.seen.append(dict(kwargs))
        calls = kwargs.get("calls")
        outcome = self.script[self.n % len(self.script)]
        self.n += 1
        l1_failed = outcome in ("decode_failed", "nonfinite")
        invoked = not l1_failed
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + (1 if l1_failed else 2)
        n = int(kwargs["n"])
        k1, k2 = int(kwargs["k1"]), int(kwargs["k2"])
        tag = outcome in ("exact", "undetected", "verify_failed")
        return opf.OperationalBlockResult(
            stream_seed=int(kwargs["stream_seed"]),
            block_index=int(kwargs["block_index"]),
            outcome=outcome,
            exact=bool(outcome == "exact"),
            label_match=bool(outcome == "exact"),
            tag_pass=bool(outcome in ("exact", "undetected")),
            l1_provenance=None if l1_failed else opf.Provenance.PRIOR_ONLY.value,
            l2_provenance=None if l1_failed else opf.Provenance.CANDIDATE_CONDITIONED.value,
            l1_executed=bool(not l1_failed),
            l1_decode_failed=bool(l1_failed),
            l2_invoked=bool(invoked),
            l2_skipped_by_l1_failure=bool(l1_failed),
            l2_decode_failed=False,
            tag_invoked=bool(tag),
            key_dependent_bits=int(
                5 * k1 + (5 * k2 if invoked else 0) + (64 if tag else 0)
            ),
            public_control_bits=int(seed_bits_for(n) if tag else 0),
            nonfinite=bool(outcome == "nonfinite"),
            truth_leak_violation=False,
            l1_error_type=("NumericNonfiniteError" if outcome == "nonfinite"
                           else ("RuntimeError" if l1_failed else None)),
            l2_error_type=None,
            wall_s=0.001,
            k1=k1,
            k2=k2,
            high_hat=None if l1_failed else np.array(kwargs["high_true"], copy=True),
        )


def full_run(out, script=None, *, counts=None, hold=None, arm=None, **over):
    tmp = Path(out).parent
    fab_dir = tmp / "fab"
    fab_dir.mkdir(parents=True, exist_ok=True)
    fab_path, fab_hex = make_construction_file(fab_dir)
    man_path = make_manifest(tmp)
    if counts is None:
        counts = injected_counts()
    if hold is None:
        hold = injected_hold_table()
    if arm is None:
        arm = FakeArm(script)
    kw = dict(
        counts=counts,
        hold_table=hold,
        expected_entropies=expected_seam(counts),
        construction=str(fab_path),
        construction_digest=fab_hex,
        manifest_path=str(man_path),
        out_dir=Path(out),
    )
    kw.update(over)
    with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
        with patched(hm, "run_operational_block", arm):
            run = hm.run_holdout_microcheck(**kw)
    return run, arm


# ---- frozen constants and fresh seeds ----

def test_frozen_constants_pinned():
    assert hm.FROZEN_N == 32768 == opf.FROZEN_N
    assert hm.FROZEN_K1 == 319 and hm.FROZEN_K2 == 6492
    assert hm.FROZEN_K_TOTAL == 6811
    assert hm.FROZEN_LEAKAGE_BITS == FROZEN_LEAKAGE == 5 * 6811 + 64
    assert hm.FROZEN_PUBLIC_CONTROL_BITS == FROZEN_PUBLIC_BITS == 10 * 32768 + 63
    assert hm.FROZEN_BLOCK_COUNT == 3
    assert hm.FROZEN_BLOCK_FRAMES == 128 and hm.FROZEN_PAIRS_PER_FRAME == 256
    assert hm.FROZEN_SYMBOLS_PER_BLOCK == 32768
    assert hm.FROZEN_HOLD_FRAME_RANGE == (1600, 1999)
    assert hm.FROZEN_HOLD_FRAMES == 400 and hm.FROZEN_HOLD_PAIRS == 102400
    assert hm.FROZEN_BLOCK_RANGES == ((1600, 1727), (1728, 1855), (1856, 1983))
    assert hm.FROZEN_REMAINDER_FRAME_RANGE == (1984, 1999)
    assert hm.FROZEN_REMAINDER_FRAMES == 16
    assert hm.FROZEN_REMAINDER_SYMBOLS == 4096
    assert hm.FROZEN_TAG_MASTER == 2026092050
    assert hm.FROZEN_CHUNK_ROWS == 512 and hm.FROZEN_TAG_BITS == 64
    assert hm.PLANNED_SC_CALLS_MAX == 6 and hm.PLANNED_TAG_INVOCATIONS == 3
    assert hm.EXPECTED_NPZ_BYTES == 25166822 == opf.EXPECTED_NPZ_BYTES
    assert hm.EXPECTED_HOLD_PARQUET_BYTES == 1354289
    assert hm.FROZEN_MANIFEST_SCHEMA == "nbldpc_v25_split_manifest_v1"
    assert hm.OUTCOMES == opf.OUTCOMES == (
        "exact", "undetected", "verify_failed", "decode_failed", "nonfinite",
        "resource_abort",
    )
    assert hm.OUTPUT_FILES == (
        "frozen_plan.json", "input_and_construction_identity.json",
        "per_block_outcomes.jsonl", "aggregate_summary.json", "report.md",
    )
    assert hm.FROZEN_CONSTRUCTION_DIGEST == (
        "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
    )
    for h in (opf.EXPECTED_H1 + opf.EXPECTED_H2, opf.EXPECTED_TOTAL):
        raw = (1.3 * hm.FROZEN_N * h - 64.0) / 5.0
        assert math.floor(raw) == 6811, (repr(h), repr(raw))
    assert FROZEN_LEAKAGE <= 1.3 * hm.FROZEN_N * (opf.EXPECTED_H1 + opf.EXPECTED_H2)


def test_fresh_test_seeds_disjoint_from_all_frozen_seeds():
    frozen = set(opr.FROZEN_DEV_SEEDS) | set(opr.P16_PRIOR_STREAMS) | {
        hm.FROZEN_TAG_MASTER,
    }
    for name in ("2026092030", "2026092000", "2026092010", "2026091790"):
        frozen.add(int(name))
    assert set(TEST_SEEDS).isdisjoint(frozen)
    assert set(TEST_SPARES).isdisjoint(frozen)
    assert TEST_MASTER not in TEST_SEEDS + TEST_SPARES
    assert hm.FROZEN_TAG_MASTER not in TEST_SEEDS + TEST_SPARES + (TEST_MASTER,)
    for prior in (2026091650, 2026091680, 2026091710, 2026091820, 2026091860,
                  2026091930, 2026091940, 2026091960, 2026091970, 2026091980,
                  2026091990, 2026091800, 2026091811, 2026091753, 2026091760):
        assert prior not in TEST_SEEDS + TEST_SPARES + (TEST_MASTER,)
        assert prior != hm.FROZEN_TAG_MASTER


def test_accepted_helpers_shared_not_reimplemented():
    assert hm.run_operational_block is opf.run_operational_block
    assert hm.verify_predecessor_construction is opr.verify_predecessor_construction
    assert hm.target_preconditions.__module__.endswith("target_construction")
    assert hm.load_v25_channel_counts.__module__.endswith("v35_algorithm_development")
    assert hm.load_pairs_table.__module__.endswith("pairs_loader")
    for banned in ("sample_full_block", "block_genie_risks", "select_empirical_split",
                   "budget_k_total", "analytic_order"):
        assert not hasattr(hm, banned), banned


# ---- predecessor + manifest identity before any read ----

def test_predecessor_identity_tamper_refusals_zero_reads_zero_root():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        man = make_manifest(tmp_path)
        for idx, tamper in enumerate(("k1", "k2", "order-dup", "n", "digest", "protocol")):
            sub = tmp_path / f"fab{idx}"
            sub.mkdir()
            fab_path, fab_hex = make_construction_file(sub, tamper=tamper)
            root = tmp_path / f"out{idx}"
            with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hm, "load_v25_channel_counts", forbidden_loader):
                    with patched(hm, "load_pairs_table", forbidden_loader):
                        with patched(hm, "run_operational_block", forbidden_arm):
                            assert_raises_match(
                                ValueError, "predecessor construction identity",
                                hm.run_holdout_microcheck,
                                counts=injected_counts(), hold_table=injected_hold_table(),
                                construction=str(fab_path), construction_digest=fab_hex,
                                manifest_path=str(man), out_dir=root,
                            )
            assert not root.exists()
        # Wrong digest flag and an absent file also refuse before anything runs.
        fab_path, fab_hex = make_construction_file(tmp_path)
        bad_flag = ("0" if fab_hex[0] != "0" else "1") + fab_hex[1:]
        assert_raises_match(
            ValueError, "digest flag != frozen digest",
            hm.run_holdout_microcheck,
            counts=injected_counts(), hold_table=injected_hold_table(),
            construction=str(fab_path), construction_digest=bad_flag,
            manifest_path=str(man), out_dir=tmp_path / "outflag",
        )
        assert not (tmp_path / "outflag").exists()
        assert_raises_match(
            FileNotFoundError, "not found", hm.verify_split_manifest,
            str(tmp_path / "absent.json"),
        )
        with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            assert_raises_match(
                FileNotFoundError, "not found", hm.run_holdout_microcheck,
                counts=injected_counts(), hold_table=injected_hold_table(),
                construction=str(tmp_path / "absent.json"), construction_digest=fab_hex,
                manifest_path=str(man), out_dir=tmp_path / "outmissing",
            )
        assert not (tmp_path / "outmissing").exists()


def test_manifest_identity_tamper_refusals_zero_reads_zero_root():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        good = make_manifest(tmp_path, name="good.json")
        record = hm.verify_split_manifest(good, source="1M")
        assert record["hold_frames"] == 400 and record["hold_pairs"] == 102400
        assert record["source_tag"] == "type2_1M_20260121_184040"
        for idx, tamper in enumerate(("hold-frames", "hold-pairs", "schema", "missing-source")):
            man = make_manifest(tmp_path, tamper=tamper, name=f"bad{idx}.json")
            assert_raises_match(
                ValueError, "hold split manifest identity",
                hm.verify_split_manifest, man, source="1M",
            )
            root = tmp_path / f"out{idx}"
            with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hm, "load_v25_channel_counts", forbidden_loader):
                    with patched(hm, "load_pairs_table", forbidden_loader):
                        assert_raises_match(
                            ValueError, "hold split manifest identity",
                            hm.run_holdout_microcheck,
                            counts=injected_counts(), hold_table=injected_hold_table(),
                            construction=str(fab_path), construction_digest=fab_hex,
                            manifest_path=str(man), out_dir=root,
                        )
            assert not root.exists()


# ---- deterministic HOLD slicing ----

def test_hold_slicing_blocks_and_remainder_exact():
    df = injected_hold_table()
    formation = hm.form_holdout_blocks(df)
    assert formation["hold_frame_range"] == [1600, 1999]
    assert formation["hold_frames"] == 400
    assert formation["hold_pairs"] == 102400
    assert formation["block_ranges"] == [[1600, 1727], [1728, 1855], [1856, 1983]]
    assert formation["remainder"] == {
        "frame_start": 1984, "frame_end": 1999, "frames": 16,
        "symbols": 4096, "used": False,
    }
    assert len(formation["blocks"]) == 3
    covered = np.zeros(2000, dtype=bool)
    for block in formation["blocks"]:
        assert len(block["bob"]) == 32768
        assert len(block["labels"]) == 32768
        assert np.array_equal(block["labels"], block["low"] + 32 * block["high"])
        expected = (
            df[(df["frame_id"] >= block["frame_start"])
               & (df["frame_id"] <= block["frame_end"])]
            .sort_values(["frame_id", "pair_idx"])
        )
        assert np.array_equal(block["labels"], expected["alice_symbol"].to_numpy())
        assert np.array_equal(block["bob"], expected["bob_symbol"].to_numpy())
        covered[block["frame_start"]: block["frame_end"] + 1] = True
    assert covered[1600:1984].all()
    assert not covered[1984:].any()
    assert not covered[:1600].any()


def test_malformed_hold_population_rejections():
    df = injected_hold_table()
    for how in ("drop-frame", "pair-gap", "extra-frame-rows", "symbol-range",
                "shifted-range", "no-hold"):
        assert_raises_match(
            hm.HoldoutMicrocheckContractError, "BLOCKED(hold_population_exact)",
            hm.form_holdout_blocks, mutate_hold(df, how),
        )
    # Declared-range mismatches fail the block/remainder gate explicitly.
    assert_raises_match(
        hm.HoldoutMicrocheckContractError, "BLOCKED(blocks_exact_with_declared_remainder)",
        hm.form_holdout_blocks, df, block_frames=64,
    )
    assert_raises_match(
        ValueError, "remainder-frames",
        hm.form_holdout_blocks, df, remainder_frames=(1985, 1999),
    )


def test_malformed_hold_population_run_level_blocked_five_files():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(hm, "FROZEN_CONSTRUCTION_DIGEST",
                     make_construction_file(Path(tmp))[1]):
            fab_path, fab_hex = make_construction_file(Path(tmp))
            man = make_manifest(Path(tmp))
            assert_raises_match(
                hm.HoldoutMicrocheckContractError, "BLOCKED(hold_population_exact)",
                hm.run_holdout_microcheck,
                counts=injected_counts(), hold_table=mutate_hold(injected_hold_table(), "drop-frame"),
                expected_entropies=expected_seam(injected_counts()),
                construction=str(fab_path), construction_digest=fab_hex,
                manifest_path=str(man), out_dir=root,
            )
        assert sorted(p.name for p in root.iterdir()) == sorted(hm.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(hold_population_exact)"


# ---- one-open guards and no sampling/fitting ----

def test_one_open_guards_refuse_reopen_with_zero_execution():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        saved_npz = hm._NPZ_CONTENT_OPENED
        saved_hold = hm._HOLD_PARQUET_CONTENT_OPENED
        try:
            hm._NPZ_CONTENT_OPENED = True
            with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, "reopen refused",
                    hm.run_holdout_microcheck,
                    counts_path=str(tmp_path / "absent.npz"),
                    hold_table=injected_hold_table(),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=tmp_path / "outa",
                )
            assert not (tmp_path / "outa").exists()
            hm._NPZ_CONTENT_OPENED = False
            hm._HOLD_PARQUET_CONTENT_OPENED = True
            with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, "reopen refused",
                    hm.run_holdout_microcheck,
                    counts=injected_counts(),
                    hold_pairs=str(tmp_path / "absent.parquet"),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=tmp_path / "outb",
                )
            assert not (tmp_path / "outb").exists()
        finally:
            hm._NPZ_CONTENT_OPENED = saved_npz
            hm._HOLD_PARQUET_CONTENT_OPENED = saved_hold
        assert hm._NPZ_CONTENT_OPENED is False
        assert hm._HOLD_PARQUET_CONTENT_OPENED is False


def test_no_fitting_or_sampling_tokens_and_exact_call_counts():
    text = Path(hm.__file__).read_text(encoding="utf-8")
    # Call-style tokens only: the scope prose may say "no shuffle/resampling".
    for token in ("np.random", "default_rng", "random_state", ".shuffle",
                  "resample(", "bootstrap", "polyfit", "curve_fit",
                  "sample_full_block", "Genie", "GENIE", "genie",
                  "Adaptive", "ADAPTIVE", "adaptive", "FWHT", "fwht",
                  "Rescue", "rescue", "Oracle", "ORACLE", "oracle",
                  "load_v31", "load_v25_payload", "TTBin", "ttbin"):
        assert token not in text, token

    def forbidden(*args, **kwargs):
        raise AssertionError("protected loaders must never run in injected tests")

    with tempfile.TemporaryDirectory() as tmp:
        arm = FakeArm(["exact", "exact", "exact"])
        with patched(hm, "load_v25_channel_counts", forbidden):
            with patched(hm, "load_pairs_table", forbidden):
                run, _ = full_run(Path(tmp) / "out", arm=arm)
        assert arm.n == 3
        assert run.summary["block_count"] == 3
        assert run.summary["attempt_read_accounting"]["counts_content_opens"] == 0
        assert run.summary["attempt_read_accounting"]["hold_content_opens"] == 0
        assert hm._NPZ_CONTENT_OPENED is False
        assert hm._HOLD_PARQUET_CONTENT_OPENED is False


# ---- fixed construction path and tag domain ----

def test_fixed_orders_k_tag_domain_and_truth_boundary():
    from comparison_bench.src.comparison_bench.formal_ir.shared import (
        toeplitz_tag as real_tag,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        fab_doc = json.loads(fab_path.read_text(encoding="utf-8"))
        l1_expected = np.asarray(fab_doc["cell"]["l1_order"], dtype=np.int64)
        l2_expected = np.asarray(fab_doc["cell"]["l2_order"], dtype=np.int64)
        scope = {"tag": 0}

        class Spy(FakeArm):
            def __call__(self, **kwargs):
                scope["tag"] += 1
                return super().__call__(**kwargs)

        arm = Spy(["exact", "exact", "exact"])
        run, _ = full_run(tmp_path / "out", arm=arm)
        assert arm.n == 3
        for index, kw in enumerate(arm.seen):
            assert int(kw["n"]) == 32768
            assert int(kw["k1"]) == 319 and int(kw["k2"]) == 6492
            assert np.array_equal(np.asarray(kw["l1_order"]), l1_expected)
            assert np.array_equal(np.asarray(kw["l2_order"]), l2_expected)
            bits = np.zeros(10 * hm.FROZEN_N, dtype=np.uint8)
            p18_seed = hm.holdout_seed_bits(hm.FROZEN_TAG_MASTER, 32768, index)
            assert np.array_equal(kw["tag_fn"](bits, np.zeros(5, dtype=np.uint8), 64),
                                  real_tag(bits, p18_seed, 64))
            assert not np.array_equal(
                p18_seed, opf.operational_seed_bits(hm.FROZEN_TAG_MASTER, 32768, index)
            )
            assert not np.array_equal(
                p18_seed, opr.replication_seed_bits(hm.FROZEN_TAG_MASTER, 32768, index)
            )
        # Truth stays out of the operational metrics: provenance is exactly
        # PRIOR_ONLY / CANDIDATE_CONDITIONED on every executed block.
        for record in run.records:
            if record["l1_executed"]:
                assert record["l1_provenance"] == opf.Provenance.PRIOR_ONLY.value
            if record["l2_invoked"]:
                assert record["l2_provenance"] == opf.Provenance.CANDIDATE_CONDITIONED.value
            assert record["truth_leak_violation"] is False


def test_tiny_real_block_truth_isolation_and_p18_tag_domain():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
        derive_p1,
        derive_p2,
    )
    from comparison_bench.src.comparison_bench.formal_ir.shared import (
        toeplitz_tag as real_tag,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
        polar_transform,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        build_injected_joint_table,
        labels_to_bits,
        seed_bits_for,
    )

    n = 8
    gidx = 2
    table = build_injected_joint_table(epsilon1=0.05, epsilon2=0.2)
    rng = np.random.default_rng(TEST_SEEDS[0])
    bob, _, high, low = opf.sample_full_block(
        rng, np.full(1024, 1.0 / 1024), table, 32, 32, n
    )
    field = opf.make_gf32() if hasattr(opf, "make_gf32") else None
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
        make_gf32,
    )

    field = make_gf32()
    u1 = polar_transform(high, field=field, alpha=2)
    u2 = polar_transform(low, field=field, alpha=2)
    labels = (low + 32 * high).astype(np.int64)
    bits = labels_to_bits(labels)
    master = TEST_MASTER + 10000
    p18_seed = hm.holdout_seed_bits(master, n, gidx, bit_length=seed_bits_for(n))
    seen = []

    def spy_tag(bits_in, seed, tag_bits):
        seen.append(np.array(seed, copy=True))
        return real_tag(bits_in, seed, tag_bits)

    def p18_closure(bits_in, _seed, tag_bits, _fixed=p18_seed):
        return spy_tag(bits_in, _fixed, tag_bits)

    before = [np.array(v, copy=True) for v in (bob, high, low, u1, u2, labels)]
    with patched(hm, "toeplitz_tag", spy_tag):
        result = hm.run_operational_block(
            n=n, stream_seed=int(TEST_SEEDS[1]), block_index=gidx,
            bob=bob, high_true=high, low_true=low, u1_true=u1, u2_true=u2,
            labels_true=labels, labels_true_bits=bits, field=field,
            p1_table=derive_p1(table), p2_table=derive_p2(table),
            l1_order=np.arange(n), l2_order=np.arange(n), k1=n, k2=n,
            master=master, tag_fn=p18_closure,
        )
    assert len(seen) == 2
    assert np.array_equal(seen[0], p18_seed)
    assert np.array_equal(seen[1], p18_seed)
    assert not np.array_equal(seen[0], opf.operational_seed_bits(master, n, gidx))
    assert not np.array_equal(seen[0], opr.replication_seed_bits(master, n, gidx))
    assert result.outcome == "exact"
    assert result.key_dependent_bits == 5 * (n + n) + 64
    assert result.public_control_bits == seed_bits_for(n)
    assert result.truth_leak_violation is False
    # Input arrays are never mutated or aliased by the scoring path.
    for arr, snapshot in zip((bob, high, low, u1, u2, labels), before):
        assert np.array_equal(arr, snapshot)


def test_nll_raw_ser_and_ratio_arithmetic():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.prior import (
        derive_p1,
        derive_p2,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        build_injected_joint_table,
    )

    table = build_injected_joint_table(epsilon1=0.05, epsilon2=0.2)
    p1, p2 = derive_p1(table), derive_p2(table)
    n = 6
    rng = np.random.default_rng(TEST_SEEDS[2])
    bob, _, high, low = opf.sample_full_block(
        rng, np.full(1024, 1.0 / 1024), table, 32, 32, n
    )
    labels = (low + 32 * high).astype(np.int64)
    nll = hm.holdout_nll_bits(bob, high, low, p1, p2)
    expected_l1 = float(-np.sum(np.log2(p1[high, bob])))
    expected_l2 = float(-np.sum(np.log2(p2[high, bob, low])))
    assert abs(nll["l1_nll_bits"] - expected_l1) < 1e-12
    assert abs(nll["l2_nll_bits"] - expected_l2) < 1e-12
    assert abs(nll["total_nll_bits"] - (expected_l1 + expected_l2)) < 1e-12
    assert nll["pairs"] == n
    assert abs(nll["total_nll_bits_per_pair"] - nll["total_nll_bits"] / n) < 1e-12
    assert hm.raw_symbol_error_rate(labels, bob) == float(np.mean(labels != bob))
    assert_raises_match(
        ValueError, "non-positive", hm.holdout_nll_bits,
        bob, high, low, np.zeros((32, 1024)), p2,
    )
    # Runner records carry the literal per-block ratio 34119 / observed NLL.
    with tempfile.TemporaryDirectory() as tmp:
        run, _ = full_run(Path(tmp) / "out")
        total = 0.0
        for record in run.records:
            assert record["disclosure_ce_ratio"] == (
                hm.FROZEN_LEAKAGE_BITS / record["total_nll_bits"]
            )
            total += record["total_nll_bits"]
        aggregate = run.summary["disclosure"]["ce_normalized_disclosure_ratio"]
        assert abs(aggregate - (hm.FROZEN_LEAKAGE_BITS * 3 / total)) < 1e-15
        assert "NOT qualification efficiency" in run.summary["disclosure"]["ratio_note"]


# ---- outcome buckets, precedence and no-threshold labels ----

def test_outcome_classifier_every_bucket_and_precedence():
    c = opf.classify_operational_outcome
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=True, label_match=True) == "exact"
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=True, label_match=False) == "undetected"
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=False, label_match=False) == "verify_failed"
    assert c(l1_failed=False, l2_failed=False, nonfinite=False,
             tag_pass=False, label_match=True) == "verify_failed"
    assert c(l1_failed=True, l2_failed=False, nonfinite=False,
             tag_pass=False, label_match=False) == "decode_failed"
    assert c(l1_failed=False, l2_failed=True, nonfinite=False,
             tag_pass=False, label_match=False) == "decode_failed"
    assert c(l1_failed=True, l2_failed=False, nonfinite=True,
             tag_pass=False, label_match=False) == "nonfinite"
    assert c(l1_failed=False, l2_failed=True, nonfinite=True,
             tag_pass=False, label_match=False) == "nonfinite"


def test_scripted_buckets_undetected_and_nonfinite_block():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        run, _ = full_run(root, ["exact", "undetected", "verify_failed"])
        assert run.summary["outcome_counts"] == {
            "exact": 1, "undetected": 1, "verify_failed": 1,
            "decode_failed": 0, "nonfinite": 0, "resource_abort": 0,
        }
        assert run.summary["integrity"]["undetected_zero"] is False
        assert run.summary["integrity"]["nonfinite_zero"] is True
        # Undetected is never success even with a passing tag.
        undetected = [r for r in run.records if r["outcome"] == "undetected"][0]
        assert undetected["tag_pass"] is True and undetected["exact"] is False
        assert run.summary["outcome_label"] == "BLOCKED(undetected_zero)"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        run, _ = full_run(root, ["decode_failed", "nonfinite", "exact"])
        assert run.summary["outcome_counts"]["nonfinite"] == 1
        assert run.summary["outcome_counts"]["decode_failed"] == 1
        assert run.summary["integrity"]["nonfinite_zero"] is False
        assert run.summary["integrity"]["undetected_zero"] is True
        # Failure precedence: nonfinite_zero precedes resource/others here.
        assert run.summary["outcome_label"] == "BLOCKED(nonfinite_zero)"
        failed = [r for r in run.records if r["outcome"] == "decode_failed"][0]
        assert failed["key_dependent_bits"] == FROZEN_L1_ONLY_BITS
        assert failed["public_control_bits"] == 0
        assert failed["tag_invoked"] is False
        assert failed["l1_correct"] is False


def test_no_threshold_labels_zero_and_three_exact():
    # The label depends only on integrity gates: no count input exists.
    all_true = {name: True for name in hm.INTEGRITY_GATE_ORDER}
    assert hm.hold_microcheck_label(all_true) == hm.COMPLETE_LABEL
    assert "COMPLETE" in hm.COMPLETE_LABEL
    for name in hm.INTEGRITY_GATE_ORDER:
        gates = dict(all_true)
        gates[name] = False
        assert hm.hold_microcheck_label(gates) == f"BLOCKED({name})"
    assert not hasattr(hm, "recovery_gates")
    assert not hasattr(hm, "select_label")
    text = Path(hm.__file__).read_text(encoding="utf-8")
    for token in ("wilson", "Wilson", "WILSON", "recovery_gates", "EXACT_MIN",
                  "exact_fraction", "fer_rate", "FER boundary"):
        assert token not in text, token
    with tempfile.TemporaryDirectory() as tmp:
        run_zero, _ = full_run(Path(tmp) / "z", ["verify_failed"] * 3)
        assert run_zero.summary["exact_count"] == 0
        assert run_zero.summary["integrity_all_pass"] is True
        assert run_zero.summary["outcome_label"] == hm.COMPLETE_LABEL
    with tempfile.TemporaryDirectory() as tmp:
        run_full, _ = full_run(Path(tmp) / "f", ["exact"] * 3)
        assert run_full.summary["exact_count"] == 3
        assert run_full.summary["outcome_label"] == hm.COMPLETE_LABEL
        assert run_full.summary["decision"]["recovery_threshold"] is None


# ---- five-file evidence, scalar-only outputs and recount ----

def test_five_file_scalar_only_inventory_and_resources():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        run, _ = full_run(root)
        assert sorted(p.name for p in root.iterdir()) == sorted(hm.OUTPUT_FILES)
        lines = (root / "per_block_outcomes.jsonl").read_text().splitlines()
        assert len(lines) == 3
        records = [json.loads(line) for line in lines]
        required = {
            "block_index", "frame_start", "frame_end", "frame_count", "outcome",
            "raw_ser", "l1_nll_bits", "l2_nll_bits", "total_nll_bits",
            "total_nll_bits_per_pair", "l1_correct", "tag_pass", "tag_invoked",
            "key_dependent_bits", "public_control_bits",
            "full_block_key_dependent_bits", "public_control_bits_per_tag",
            "disclosure_ce_ratio", "l1_provenance", "l2_provenance", "k1", "k2",
            "error", "wall_s", "resources",
        }
        assert required <= set(records[0])
        for record in records:
            assert set(record["resources"]) == {
                "wall_s", "rss_bytes_hwm", "vm_peak_kb", "vm_size_kb"
            }
            assert record["full_block_key_dependent_bits"] == FROZEN_LEAKAGE
            assert record["public_control_bits_per_tag"] == FROZEN_PUBLIC_BITS
            assert record["key_dependent_bits"] == FROZEN_LEAKAGE
            assert record["public_control_bits"] == FROZEN_PUBLIC_BITS
        banned = {
            "bob", "high", "low", "high_true", "low_true", "u1_true", "u2_true",
            "a_full", "counts", "logp", "decision_metrics", "high_hat",
            "low_hat", "label_hat", "label_bits", "seed_bits", "rng_state",
            "p_b", "f_full", "labels_true", "l1_order", "l2_order",
            "pooled_e1_mean", "pooled_h1_mean", "pooled_e2_mean", "pooled_h2_mean",
            "labels", "alice", "frame_id", "pair_idx", "alice_symbol",
            "bob_symbol", "p1", "p2",
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
        walk(json.loads((root / "frozen_plan.json").read_text()), keys)
        walk(json.loads((root / "input_and_construction_identity.json").read_text()), keys)
        walk(json.loads((root / "aggregate_summary.json").read_text()), keys)
        for record in records:
            walk(record, keys)
        assert not (keys & banned), keys & banned
        assert run.summary["attempt_read_accounting"]["opened_content_paths"] == []


def test_recount_arithmetic_partial_and_tamper():
    with tempfile.TemporaryDirectory() as tmp:
        run, _ = full_run(Path(tmp) / "out", ["exact", "exact", "decode_failed"])
        disclosure = run.summary["disclosure"]
        assert disclosure["recount"] == {
            "key_dependent_bits": 2 * FROZEN_LEAKAGE + FROZEN_L1_ONLY_BITS,
            "public_control_bits": 2 * FROZEN_PUBLIC_BITS,
            "tag_invocations": 2,
            "event_types": {"l1_disclosure": 3, "l2_disclosure": 2,
                            "verification_tag": 2},
        }
        assert disclosure["mismatches"] == []
        assert disclosure["tag_invocations"] == 2
        assert disclosure["key_dependent_bits"] == (
            2 * FROZEN_LEAKAGE + FROZEN_L1_ONLY_BITS
        )
        tampered = [dict(e) for e in run.events]
        tampered[0] = dict(tampered[0], key_dependent_bits=tampered[0]["key_dependent_bits"] + 1)
        recount = hm.holdout_recount_events(tampered)
        incremental = {name: disclosure[name] for name in
                       ("key_dependent_bits", "public_control_bits", "tag_invocations")}
        assert opf._transcript_mismatches(incremental, recount) != []
        assert_raises_match(
            ValueError, "not N/arm-tagged", hm.holdout_recount_events,
            [{"event_id": "bogus", "event_type": "l1_disclosure",
              "key_dependent_bits": 0, "public_control_bits": 0}],
        )
        assert_raises_match(
            ValueError, "not frozen", hm.holdout_recount_events,
            [dict(run.events[0], event_type="bogus_type")],
        )
        assert run.events[0]["method"] == "nbpolar_holdout_microcheck"
        assert run.events[0]["frame_key"].startswith("nbpolar-p18-holdout-microcheck:")
        assert run.events[0]["event_id"].startswith("block-32768-0-microcheck-")


# ---- failure paths, checkpoints and precedence ----

def test_precondition_failure_blocked_no_sc_call():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        counts = injected_counts()
        counts[:, 0] = 0.0
        arm = FakeArm()
        root = tmp_path / "out"
        with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(hm, "run_operational_block", arm):
                assert_raises_match(
                    opr.TargetPopulationContractError,
                    "BLOCKED(target_population_contract)",
                    hm.run_holdout_microcheck,
                    counts=counts, hold_table=injected_hold_table(),
                    expected_entropies=(opf.EXPECTED_H1, opf.EXPECTED_H2,
                                        opf.EXPECTED_H1 + opf.EXPECTED_H2),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=root,
                )
        assert arm.n == 0
        assert sorted(p.name for p in root.iterdir()) == sorted(hm.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(target_population_contract)"


def test_budget_stop_abort_fill_and_precedence():
    real_guard = opf._budget_exceeded
    calls = {"n": 0}

    def flaky(start, cap):
        calls["n"] += 1
        if calls["n"] > 1:
            return "wall_s"
        return real_guard(start, cap)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(opf, "_budget_exceeded", flaky):
            run, arm = full_run(root, ["exact"])
        assert arm.n == 1
        lines = (root / "per_block_outcomes.jsonl").read_text().splitlines()
        assert len(lines) == 3
        records = [json.loads(line) for line in lines]
        aborts = [r for r in records if r["outcome"] == "resource_abort"]
        assert len(aborts) == 2
        assert [r["frame_start"] for r in aborts] == [1728, 1856]
        assert run.summary["resource_stop_fired"] is True
        assert run.summary["resource_stop_reason"] == "wall_s"
        assert run.summary["integrity"]["resource_limits_met_and_no_abort"] is False
        assert run.summary["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"
        # Checkpoints for the abort-filled records survived.
        assert sorted(p.name for p in root.iterdir()) == sorted(hm.OUTPUT_FILES)
    # Failure precedence: an earlier unordered bucket precedes the resource gate.
    calls["n"] = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(opf, "_budget_exceeded", flaky):
            run, _ = full_run(root, ["undetected"])
        assert run.summary["integrity"]["undetected_zero"] is False
        assert run.summary["outcome_label"] == "BLOCKED(undetected_zero)"


def test_memory_error_classification_path():
    def oom(**kwargs):
        raise MemoryError("injected exhaustion")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        with patched(hm, "run_operational_block", oom):
            # full_run patches the arm itself; run directly for the OOM seam.
            tmp_path = Path(tmp)
            fab_dir = tmp_path / "fab"
            fab_dir.mkdir()
            fab_path, fab_hex = make_construction_file(fab_dir)
            man = make_manifest(tmp_path)
            counts = injected_counts()
            with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    hm.HoldoutMicrocheckResourceError,
                    "BLOCKED(resource_limits_met_and_no_abort)",
                    hm.run_holdout_microcheck,
                    counts=counts, hold_table=injected_hold_table(),
                    expected_entropies=expected_seam(counts),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=root,
                )
        assert sorted(p.name for p in root.iterdir()) == sorted(hm.OUTPUT_FILES)
        blocked = json.loads((root / "aggregate_summary.json").read_text())
        assert blocked["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"


# ---- real-mode accounting without touching protected inputs ----

def _fake_protected_paths(tmp_path, *, npz_bytes=25166822):
    counts_path = tmp_path / "fake_counts.npz"
    with open(counts_path, "wb") as handle:
        handle.truncate(npz_bytes)
    pairs_path = tmp_path / "fake_pairs.parquet"
    pairs_path.write_bytes(b"fake parquet stand-in, never parsed")
    return counts_path, pairs_path


def test_real_mode_accounting_with_patched_loaders():
    counts = injected_counts()
    hold = injected_hold_table()
    calls = {"npz": 0, "pairs": 0}

    def fake_npz(path):
        calls["npz"] += 1
        return {"1M": counts}

    def fake_pairs(path):
        calls["pairs"] += 1
        return hold

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        counts_path, pairs_path = _fake_protected_paths(tmp_path)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        arm = FakeArm(["exact", "exact", "exact"])
        saved_npz = hm._NPZ_CONTENT_OPENED
        saved_hold = hm._HOLD_PARQUET_CONTENT_OPENED
        try:
            with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hm, "load_v25_channel_counts", fake_npz):
                    with patched(hm, "load_pairs_table", fake_pairs):
                        with patched(hm, "run_operational_block", arm):
                            run = hm.run_holdout_microcheck(
                                counts_path=str(counts_path),
                                hold_pairs=str(pairs_path),
                                expected_entropies=expected_seam(counts),
                                construction=str(fab_path), construction_digest=fab_hex,
                                manifest_path=str(man), out_dir=tmp_path / "out",
                            )
            assert calls == {"npz": 1, "pairs": 1}
            acc = run.summary["attempt_read_accounting"]
            assert acc["counts_content_opens"] == 1
            assert acc["hold_content_opens"] == 1
            assert acc["attempts_consumed_by_this_run"] == 1
            assert acc["opened_content_paths"] == [
                str(counts_path.resolve()), str(pairs_path.resolve())
            ]
            assert acc["registered_content_paths"] == acc["opened_content_paths"]
            integrity = run.summary["integrity"]
            assert integrity["one_open_per_protected_input"] is True
            assert integrity["input_stat_unchanged"] is True
            assert integrity["no_unregistered_access"] is True
            assert integrity["disclosure_recount_exact"] is True
            assert run.summary["outcome_label"] == hm.COMPLETE_LABEL
            assert hm._NPZ_CONTENT_OPENED is True
            assert hm._HOLD_PARQUET_CONTENT_OPENED is True
        finally:
            hm._NPZ_CONTENT_OPENED = saved_npz
            hm._HOLD_PARQUET_CONTENT_OPENED = saved_hold


def test_real_mode_stat_change_blocks_with_earliest_gate():
    counts = injected_counts()
    hold = injected_hold_table()
    real_stat = hm._stat_record
    calls = {"n": 0}

    def shifted_stat(path):
        calls["n"] += 1
        record = real_stat(path)
        if calls["n"] > 2 and record["path"] is not None:
            record["mtime_ns"] += 1
        return record

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        counts_path, pairs_path = _fake_protected_paths(tmp_path)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        saved_npz = hm._NPZ_CONTENT_OPENED
        saved_hold = hm._HOLD_PARQUET_CONTENT_OPENED
        try:
            with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(hm, "load_v25_channel_counts", lambda p: {"1M": counts}):
                    with patched(hm, "load_pairs_table", lambda p: hold):
                        with patched(hm, "run_operational_block", FakeArm()):
                            with patched(hm, "_stat_record", shifted_stat):
                                run = hm.run_holdout_microcheck(
                                    counts_path=str(counts_path),
                                    hold_pairs=str(pairs_path),
                                    expected_entropies=expected_seam(counts),
                                    construction=str(fab_path),
                                    construction_digest=fab_hex,
                                    manifest_path=str(man), out_dir=tmp_path / "out",
                                )
            assert run.summary["integrity"]["input_stat_unchanged"] is False
            assert run.summary["outcome_label"] == "BLOCKED(input_stat_unchanged)"
        finally:
            hm._NPZ_CONTENT_OPENED = saved_npz
            hm._HOLD_PARQUET_CONTENT_OPENED = saved_hold


# ---- CLI refusals and structural rules ----

def test_cli_parser_and_run_contract_refusals_before_open():
    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on a refusal")

    parser = hm.build_parser()
    required = {a.dest for a in parser._actions if a.required}
    assert required == {
        "counts", "source", "floor", "n", "k1", "k2", "construction",
        "construction_digest", "hold_pairs", "hold_frames", "block_frames",
        "remainder_frames", "tag_master", "chunk_rows", "tag_bits", "out_dir",
    }
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)

        def base(**over):
            kw = dict(
                counts=injected_counts(), hold_table=injected_hold_table(),
                construction=str(fab_path), construction_digest=fab_hex,
                manifest_path=str(man),
            )
            kw.update(over)
            return kw

        with patched(hm, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(hm, "run_operational_block", forbidden_arm):
                assert_raises_match(
                    ValueError, "hold-frames", hm.run_holdout_microcheck,
                    **base(hold_frames=(1600, 1998), out_dir=tmp_path / "a"),
                )
                assert_raises_match(
                    ValueError, "block-frames", hm.run_holdout_microcheck,
                    **base(block_frames=64, out_dir=tmp_path / "b"),
                )
                assert_raises_match(
                    ValueError, "remainder-frames", hm.run_holdout_microcheck,
                    **base(remainder_frames=(1985, 1999), out_dir=tmp_path / "c"),
                )
                assert_raises_match(
                    ValueError, "tag-master", hm.run_holdout_microcheck,
                    **base(tag_master=1, out_dir=tmp_path / "d"),
                )
                assert_raises_match(
                    ValueError, "n=32768", hm.run_holdout_microcheck,
                    **base(n=16384, out_dir=tmp_path / "e"),
                )
                assert_raises_match(
                    ValueError, "k1=319", hm.run_holdout_microcheck,
                    **base(k1=320, out_dir=tmp_path / "f"),
                )
                assert_raises_match(
                    ValueError, "k2=6492", hm.run_holdout_microcheck,
                    **base(k2=6491, out_dir=tmp_path / "g"),
                )
                assert_raises_match(
                    ValueError, "floor", hm.run_holdout_microcheck,
                    **base(floor=1e-12, out_dir=tmp_path / "h"),
                )
                assert_raises_match(
                    ValueError, "source", hm.run_holdout_microcheck,
                    **base(source="2M", out_dir=tmp_path / "i"),
                )
                assert_raises_match(
                    ValueError, "chunk-rows", hm.run_holdout_microcheck,
                    **base(chunk_rows=64, out_dir=tmp_path / "j"),
                )
                assert_raises_match(
                    ValueError, "tag-bits", hm.run_holdout_microcheck,
                    **base(tag_bits=32, out_dir=tmp_path / "k"),
                )
                assert_raises_match(
                    FileNotFoundError, "not found", hm.run_holdout_microcheck,
                    **base(construction=str(tmp_path / "absent.json"),
                           out_dir=tmp_path / "l"),
                )
        for name in "abcdefghijkl":
            assert not (tmp_path / name).exists()
    import subprocess
    proc = subprocess.run(
        [sys.executable, "-m",
         "comparison_bench.src.comparison_bench.formal_ir.nbpolar.holdout_microcheck",
         "--counts", "x"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 2


def test_existing_root_refusal_zero_execution():
    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        root = tmp_path / "out"
        root.mkdir()
        sentinel = root / "sentinel.txt"
        sentinel.write_text("untouched", encoding="utf-8")
        with patched(hm, "run_operational_block", forbidden_arm):
            assert_raises_match(
                FileExistsError, "refusing to overwrite",
                hm.run_holdout_microcheck,
                counts=injected_counts(), hold_table=injected_hold_table(),
                construction=str(tmp_path / "absent.json"),
                construction_digest="x", out_dir=root,
            )
        assert sentinel.read_text(encoding="utf-8") == "untouched"
        assert sorted(p.name for p in root.iterdir()) == ["sentinel.txt"]


def test_module_required_tokens_and_no_forbidden_paths():
    text = Path(hm.__file__).read_text(encoding="utf-8")
    for token in ("load_v25_channel_counts", "load_pairs_table",
                  "normalize_pair_columns", "verify_predecessor_construction",
                  "verify_split_manifest", "target_preconditions",
                  "run_operational_block", "polar_transform", "make_gf32",
                  "labels_to_bits", "seed_bits_for", "toeplitz_tag",
                  "canonical_event", "holdout_seed_bits", "form_holdout_blocks",
                  "holdout_nll_bits", "hold_microcheck_label",
                  "holdout_block_events", "holdout_recount_events",
                  "run_holdout_microcheck"):
        assert token in text, token
    # The runner is not a loader/decoder/benchmark project: no raw/real/EVAL
    # path, no transform/belief/list decoder, no second arm or retry.
    for token in ("heldout", "held_out", "EVAL_", "real_micro", "qualification(",
                  "rtol", "thresholds", "advance", "retry_arm", "second_arm"):
        assert token not in text, token
    assert hm.FROZEN_HOLD_PAIRS_PATH == (
        "comparison_bench/outputs_comparison/nonbinary_diagnostics/"
        "v13r3fresh_pairs_20260816/type2_1M_20260121_184040/pairs.parquet"
    )

