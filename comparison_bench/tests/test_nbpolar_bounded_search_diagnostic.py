"""Focused Phase 4-P20B N=32768 bounded-search diagnostic tests.

Injected tables/arrays and temporary roots only. The V25 1M TRAIN NPZ and
the registered pairs parquet are NEVER content-opened (real-mode tests use
throwaway temporary stubs with patched loaders); the real P16
construction root, the real split manifest, every real evidence root and
the closed HOLD blocks 1600..1983 are never touched. Focused tests use
their own fresh seeds ``2026092081..2026092087`` and never the frozen P20B
tag master 2026092080 for real scoring, the P19 master 2026092060, the P18
master 2026092050, the P16/P17 streams, nor any prior/probe seed.

The frozen N=32768 makes real SC calls too slow for runner tests, so
runner tests patch the documented ``run_operational_block``,
``run_search_block`` and ``run_oracle_control_block`` seams with scripted
deterministic fakes; tables, formation, transform, NLL scoring, search
ranking, gates, accounting and checkpointing all run for real. The real
search path is exercised separately at tiny n with real SC and the real
P20B-domain tag (plus stubbed-metric selection tests). Every ``test_*``
takes no arguments, uses plain asserts and restores any monkeypatched
module attribute in a ``finally``.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    bounded_search_diagnostic as bd,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    holdout_microcheck as hm,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    operational_f13 as opf,
)
from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    holdout_backoff_diagnostic as hb,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# Fresh test-local seeds; never any frozen master/stream/probe seed.
TEST_SEEDS = (2026092081, 2026092082, 2026092083, 2026092084)
TEST_MASTER = 2026092085
TEST_SPARES = (2026092086, 2026092087)

FROZEN_LEAKAGE = 34119  # 5 * 6811 + 64 (operational arms, base)
FROZEN_CONTROL_LEAKAGE = 32524  # 5 * 6492 + 64 (oracle arm)
FROZEN_PUBLIC_BITS = 327743  # 10 * 32768 + 63
TOTAL_KEY_BITS = 2 * 3 * FROZEN_LEAKAGE + 3 * FROZEN_CONTROL_LEAKAGE  # 302286
TOTAL_PUBLIC_BITS = 9 * FROZEN_PUBLIC_BITS  # 2949687


@contextlib.contextmanager
def patched(obj, name, value):
    original = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, original)


@contextlib.contextmanager
def restored_open_guards():
    """Real-mode tests consume the one-open guards; restore them afterwards."""
    npz, dev = bd._NPZ_CONTENT_OPENED, bd._DEV_PARQUET_CONTENT_OPENED
    try:
        yield
    finally:
        bd._NPZ_CONTENT_OPENED = npz
        bd._DEV_PARQUET_CONTENT_OPENED = dev


def assert_raises_match(exc, substr, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc as err:
        assert substr in str(err), f"{substr!r} not in {err}"
        return
    raise AssertionError(f"expected {exc.__name__}({substr!r}) from {fn.__name__}{args}")


def injected_counts(seed: int = TEST_SEEDS[0]) -> np.ndarray:
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
    """Fabricate a canonical-shape predecessor copy (never the real P16 root)."""
    directory = Path(directory)
    n = 32768
    rng = np.random.default_rng(TEST_MASTER)
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
        "protocol": "nbpolar-p20b-tampered" if tamper == "protocol"
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
    if tamper == "val-frames":
        per[source]["frames"]["val"] = 399
    elif tamper == "val-pairs":
        per[source]["pairs"]["val"] = 102399
    elif tamper == "hold-frames":
        per[source]["frames"]["hold"] = 399
    elif tamper == "schema":
        schema = "nbldpc_v25_split_manifest_v2"
    elif tamper == "missing-source":
        per = {"type2_2M_20260121_183657": per[source]}
    path = Path(directory) / name
    path.write_text(json.dumps({"schema": schema, "per_source": per}), encoding="utf-8")
    return path


def injected_dev_table(*, frames=400, first_frame=1200, per_frame=256,
                       seed=TEST_SEEDS[1], extras=True):
    """Deterministic VAL-like pairs frame; shuffled rows, extra non-DEV rows."""
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
        # Frames outside the DEV pool, including a closed-HOLD frame: present
        # in the file but never selected.
        extra = pd.DataFrame({
            "frame_id": np.repeat([1199, 1600], per_frame),
            "pair_idx": np.tile(np.arange(per_frame), 2),
            "alice_symbol": rng.integers(0, 1024, size=2 * per_frame),
            "bob_symbol": rng.integers(0, 1024, size=2 * per_frame),
        })
        df = pd.concat([df, extra], ignore_index=True)
    return df.sample(frac=1.0, random_state=int(seed)).reset_index(drop=True)


def mutate_dev(df, how):
    out = df.copy()
    if how == "drop-frame":
        out = out[out["frame_id"] != 1300]
    elif how == "pair-gap":
        row = out[(out["frame_id"] == 1200) & (out["pair_idx"] == 255)].index[0]
        out.loc[row, "pair_idx"] = 254
    elif how == "symbol-range":
        row = out[out["frame_id"] == 1200].index[0]
        out.loc[row, "bob_symbol"] = 1024
    elif how == "no-dev":
        out = out[out["frame_id"].isin([1199, 1600])]
    else:
        raise AssertionError(f"unknown mutation {how}")
    return out


def tiny_tables(n, *, seed=TEST_SEEDS[2]):
    """Full-shape floored-positive P1/P2 tables plus a tiny DEV block view."""
    rng = np.random.default_rng(seed)
    p1 = rng.random((32, 1024)) + 0.5
    p1 = p1 / p1.sum(axis=0, keepdims=True)
    p2 = rng.random((32, 1024, 32)) + 0.5
    p2 = p2 / p2.sum(axis=2, keepdims=True)
    field = opf_provenance_field()
    bob = rng.integers(0, 1024, size=n).astype(np.int64)
    high = rng.integers(0, 32, size=n).astype(np.int64)
    low = rng.integers(0, 32, size=n).astype(np.int64)
    labels = (low + 32 * high).astype(np.int64)
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
        labels_to_bits,
    )
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
        polar_transform,
    )

    return {
        "p1": p1,
        "p2": p2,
        "field": field,
        "bob": bob,
        "high": high,
        "low": low,
        "labels": labels,
        "u1": polar_transform(high, field=field, alpha=2),
        "u2": polar_transform(low, field=field, alpha=2),
        "labels_bits": labels_to_bits(labels),
        "l1_order": rng.permutation(n).astype(np.int64),
        "l2_order": rng.permutation(n).astype(np.int64),
    }


def opf_provenance_field():
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.algebra import (
        make_gf32,
    )

    return make_gf32()


class FakeOperationalArm:
    """Scripted fake for the accepted ``run_operational_block`` (S0) seam."""

    def __init__(self, scripts=None):
        self.scripts = list(scripts or ["exact"] * 3)
        self.seen = []

    def __call__(self, **kwargs):
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
            seed_bits_for,
        )

        outcome = self.scripts[len(self.seen) % len(self.scripts)]
        l1_failed = outcome in ("decode_failed", "nonfinite")
        sc_delta = 1 if l1_failed else 2
        calls = kwargs.get("calls")
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + sc_delta
        n = int(kwargs["n"])
        k1, k2 = int(kwargs["k1"]), int(kwargs["k2"])
        tag = outcome in ("exact", "undetected", "verify_failed")
        self.seen.append({
            "arm": "S0_sc_base", "outcome": outcome,
            "block_index": int(kwargs["block_index"]), "tag_fn": kwargs.get("tag_fn"),
        })
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
            l2_invoked=bool(not l1_failed),
            l2_skipped_by_l1_failure=bool(l1_failed),
            l2_decode_failed=False,
            tag_invoked=bool(tag),
            key_dependent_bits=int(
                5 * k1 + (5 * k2 if not l1_failed else 0) + (64 if tag else 0)
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
            l1_exact=bool(outcome == "exact"),
            hard_l2_exact=bool(outcome == "exact"),
            oracle_l2_exact=None,
            pair_exact=bool(outcome == "exact"),
            high_hat=None if l1_failed else np.array(kwargs["high_true"], copy=True),
            low_hat=None if l1_failed else np.array(kwargs["low_true"], copy=True),
            label_hat=None,
        )


class FakeSearchArm:
    """Scripted fake for the ``run_search_block`` (S1) seam: (result, search)."""

    def __init__(self, scripts=None):
        self.scripts = list(scripts or ["greedy"] * 3)
        self.seen = []

    def __call__(self, **kwargs):
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
            seed_bits_for,
        )

        mode = self.scripts[len(self.seen) % len(self.scripts)]
        calls = kwargs.get("calls")
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + 2
        n = int(kwargs["n"])
        k1, k2 = int(kwargs["k1"]), int(kwargs["k2"])
        better = mode == "neighbor"
        self.seen.append({
            "arm": "S1_bounded_search", "mode": mode,
            "block_index": int(kwargs["block_index"]), "tag_fn": kwargs.get("tag_fn"),
        })
        result = opf.OperationalBlockResult(
            stream_seed=int(kwargs["frame_start"]),
            block_index=int(kwargs["block_index"]),
            outcome="exact",
            exact=True,
            label_match=True,
            tag_pass=True,
            l1_provenance=opf.Provenance.PRIOR_ONLY.value,
            l2_provenance=opf.Provenance.CANDIDATE_CONDITIONED.value,
            l1_executed=True,
            l1_decode_failed=False,
            l2_invoked=True,
            l2_skipped_by_l1_failure=False,
            l2_decode_failed=False,
            tag_invoked=True,
            key_dependent_bits=int(5 * (k1 + k2) + 64),
            public_control_bits=int(seed_bits_for(n)),
            nonfinite=False,
            truth_leak_violation=False,
            l1_error_type=None,
            l2_error_type=None,
            wall_s=0.001,
            k1=k1,
            k2=k2,
            l1_exact=True,
            hard_l2_exact=True,
            oracle_l2_exact=None,
            pair_exact=True,
            high_hat=np.array(kwargs["high_true"], copy=True),
            low_hat=np.array(kwargs["low_true"], copy=True),
            label_hat=None,
        )
        search = {
            "rescores_used": 8 if better else 1,
            "selected_index": 3 if better else 0,
            "selected_source": "neighbor" if better else "greedy",
            "search_found_better": bool(better),
            "greedy_total_nll_bits": 100.0,
            "selected_total_nll_bits": 90.0 if better else 100.0,
            "nll_improvement_bits": 10.0 if better else 0.0,
        }
        return result, search


class FakeControl:
    """Scripted fake for the ``run_oracle_control_block`` (S2) seam."""

    def __init__(self, scripts=None):
        self.scripts = list(scripts or ["exact"] * 3)
        self.seen = []

    def __call__(self, **kwargs):
        from comparison_bench.src.comparison_bench.formal_ir.nbpolar.two_layer import (
            seed_bits_for,
        )

        outcome = self.scripts[len(self.seen) % len(self.scripts)]
        calls = kwargs.get("calls")
        if calls is not None:
            calls["sc"] = int(calls.get("sc", 0)) + 1
        n = int(kwargs["n"])
        k2 = int(kwargs["k2"])
        tag = outcome in ("exact", "undetected", "verify_failed")
        l2_failed = outcome in ("decode_failed", "nonfinite")
        self.seen.append({
            "arm": "S2_true_l1_diagnostic", "outcome": outcome,
            "block_index": int(kwargs["block_index"]), "tag_fn": kwargs.get("tag_fn"),
        })
        return bd.OracleControlResult(
            frame_start=int(kwargs["frame_start"]),
            block_index=int(kwargs["block_index"]),
            outcome=outcome,
            exact=bool(outcome == "exact"),
            label_match=bool(outcome == "exact"),
            tag_pass=bool(outcome in ("exact", "undetected")),
            l2_invoked=True,
            l2_decode_failed=bool(l2_failed),
            tag_invoked=bool(tag),
            key_dependent_bits=int(5 * k2 + (64 if tag else 0)),
            public_control_bits=int(seed_bits_for(n) if tag else 0),
            nonfinite=bool(outcome == "nonfinite"),
            truth_leak_violation=False,
            l2_error_type=("NumericNonfiniteError" if outcome == "nonfinite"
                           else ("RuntimeError" if l2_failed else None)),
            wall_s=0.001,
            k2=k2,
            provenance=bd.ORACLE_PROVENANCE,
            oracle_truth_use=True,
            low_hat=None,
        )


def full_run(out, *, s0_scripts=None, s1_scripts=None, s2_scripts=None,
             counts=None, dev=None, **over):
    tmp = Path(out).parent
    fab_dir = tmp / "fab"
    fab_dir.mkdir(parents=True, exist_ok=True)
    fab_path, fab_hex = make_construction_file(fab_dir)
    man_path = make_manifest(tmp)
    if counts is None:
        counts = injected_counts()
    if dev is None:
        dev = injected_dev_table()
    s0 = FakeOperationalArm(s0_scripts)
    s1 = FakeSearchArm(s1_scripts)
    s2 = FakeControl(s2_scripts)
    kw = dict(
        counts=counts,
        dev_table=dev,
        expected_entropies=expected_seam(counts),
        construction=str(fab_path),
        construction_digest=fab_hex,
        manifest_path=str(man_path),
        out_dir=Path(out),
    )
    kw.update(over)
    with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
        with patched(bd, "verify_dev_block_identity", lambda: {"verified": True}):
            with patched(bd, "run_operational_block", s0):
                with patched(bd, "run_search_block", s1):
                    with patched(bd, "run_oracle_control_block", s2):
                        run = bd.run_bounded_search_diagnostic(**kw)
    return run, s0, s1, s2


# ---- frozen constants, arm table and fresh seeds ----

def test_frozen_constants_and_arm_table_pinned():
    assert bd.FROZEN_N == 32768
    assert (bd.FROZEN_K1, bd.FROZEN_K2, bd.FROZEN_K_TOTAL) == (319, 6492, 6811)
    assert bd.FROZEN_FLOOR == 1e-15
    assert bd.FROZEN_SEARCH_BOUND_M == 8
    assert bd.NEIGHBORHOOD_ID == "P20B-NBHD-1-hamming1-u-domain-margin-ranked"
    assert bd.FROZEN_BLOCK_RANGES == ((1200, 1327), (1328, 1455), (1456, 1583))
    assert bd.FROZEN_REMAINDER_FRAME_RANGE == (1584, 1599)
    assert bd.CLOSED_HOLD_FRAME_RANGE == (1600, 1983)
    assert bd.FROZEN_TAG_MASTER == 2026092080
    assert bd.PLANNED_SC_CALLS == 15
    assert bd.PLANNED_TAG_INVOCATIONS == 9
    assert bd.PLANNED_RECORDS == 9
    assert bd.FROZEN_LEAKAGE_BITS == FROZEN_LEAKAGE
    assert bd.FROZEN_CONTROL_LEAKAGE_BITS == FROZEN_CONTROL_LEAKAGE
    assert bd.FROZEN_TOTAL_KEY_DEPENDENT_BITS == TOTAL_KEY_BITS
    assert bd.FROZEN_TOTAL_PUBLIC_CONTROL_BITS == TOTAL_PUBLIC_BITS
    assert abs(bd.FROZEN_LEAKAGE_BITS / bd.FROZEN_RAW_INPUT_BITS - 0.1041229248046875) < 1e-12
    pin = bd.check_frozen_arm_table()
    assert pin["search_bound_m"] == 8
    assert pin["cap_vs_raw_ratio"] < 0.5
    assert "--dev-frames 1200 1599" in bd.FROZEN_COMMAND
    assert "--remainder-frames 1584 1599" in bd.FROZEN_COMMAND
    assert "--tag-master 2026092080" in bd.FROZEN_COMMAND
    assert "bounded_search_diagnostic" in bd.FROZEN_COMMAND
    assert "1600 1999" not in bd.FROZEN_COMMAND


def test_fresh_test_seeds_disjoint_from_all_frozen_seeds():
    frozen = (
        set(opf.FROZEN_DEV_SEEDS) | set(opf.FROZEN_TRAIN_SEEDS)
        | {hm.FROZEN_TAG_MASTER, hb.FROZEN_TAG_MASTER, bd.FROZEN_TAG_MASTER}
    )
    for seed in (2026092050, 2026092060,
                 2026092070, 2026092071, 2026092072, 2026092073,
                 2026092074, 2026092075, 2026092076):
        frozen.add(seed)
    for prior in (2026091650, 2026091680, 2026091710, 2026091820, 2026091860,
                  2026091930, 2026091940, 2026091960, 2026091970, 2026091980,
                  2026091990, 2026091800, 2026091811, 2026091753, 2026091760):
        frozen.add(prior)
    assert set(TEST_SEEDS).isdisjoint(frozen)
    assert set(TEST_SPARES).isdisjoint(frozen)
    assert TEST_MASTER not in TEST_SEEDS + TEST_SPARES
    assert bd.FROZEN_TAG_MASTER not in TEST_SEEDS + TEST_SPARES + (TEST_MASTER,)
    assert bd.FROZEN_TAG_MASTER != hm.FROZEN_TAG_MASTER
    assert bd.FROZEN_TAG_MASTER != hb.FROZEN_TAG_MASTER


def test_accepted_helpers_shared_not_reimplemented():
    assert bd.run_operational_block is opf.run_operational_block
    assert bd.run_oracle_control_block is hb.run_oracle_control_block
    assert bd.OracleControlResult is hb.OracleControlResult
    assert bd._decode_layer is opf._decode_layer
    assert bd.classify_operational_outcome is opf.classify_operational_outcome
    assert bd.verify_predecessor_construction.__module__.endswith(
        "operational_f13_replication")
    assert bd.verify_split_manifest is hm.verify_split_manifest
    assert bd.holdout_nll_bits is hm.holdout_nll_bits
    assert bd.raw_symbol_error_rate is hm.raw_symbol_error_rate
    assert bd.polar_transform_fn.__module__.endswith("transform")
    assert bd.make_gf32_fn.__module__.endswith("algebra")
    assert bd.toeplitz_tag_fn.__module__.endswith("shared")
    assert bd.build_p1_metrics_fn.__module__.endswith("prior")
    assert bd.gather_p2_metrics_fn.__module__.endswith("prior")
    assert bd.probs_to_symbol_metric_fn.__module__.endswith("prior")
    assert bd.target_preconditions.__module__.endswith("target_construction")
    assert bd.load_v25_channel_counts.__module__.endswith("v35_algorithm_development")
    assert bd.load_pairs_table.__module__.endswith("pairs_loader")
    for banned in ("sample_full_block", "block_genie_risks", "select_empirical_split",
                   "budget_k_total", "analytic_order", "wilson_lower_bound",
                   "recovery_gates", "select_label", "backoff_seed_bits",
                   "holdout_seed_bits", "operational_seed_bits", "list_decode",
                   "fwht", "belief_provenance", "smooth_joint_to_conditional"):
        assert not hasattr(bd, banned), banned
    # The accepted HOLD formation is range-pinned: DEV ranges are refused,
    # which justifies the local P20B formation with identical semantics.
    assert_raises_match(ValueError, "hold-frames",
                         hm.form_holdout_blocks, injected_dev_table(),
                         hold_frames=(1200, 1599), block_frames=128,
                         remainder_frames=(1584, 1599))


# ---- identities before any read ----

def test_predecessor_identity_tamper_refusals_zero_reads_zero_root():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    def forbidden_arm(**kwargs):
        raise AssertionError("no operational call may happen on a refusal")

    def forbidden_search(**kwargs):
        raise AssertionError("no search call may happen on a refusal")

    def forbidden_control(**kwargs):
        raise AssertionError("no control call may happen on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        man = make_manifest(tmp_path)
        for idx, tamper in enumerate(("k1", "k2", "order-dup", "n", "digest", "protocol")):
            sub = tmp_path / f"fab{idx}"
            sub.mkdir()
            fab_path, fab_hex = make_construction_file(sub, tamper=tamper)
            root = tmp_path / f"out{idx}"
            with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(bd, "load_v25_channel_counts", forbidden_loader):
                    with patched(bd, "load_pairs_table", forbidden_loader):
                        with patched(bd, "run_operational_block", forbidden_arm):
                            with patched(bd, "run_search_block", forbidden_search):
                                with patched(bd, "run_oracle_control_block", forbidden_control):
                                    assert_raises_match(
                                        ValueError, "predecessor construction identity",
                                        bd.run_bounded_search_diagnostic,
                                        counts=injected_counts(), dev_table=injected_dev_table(),
                                        construction=str(fab_path), construction_digest=fab_hex,
                                        manifest_path=str(man), out_dir=root,
                                    )
            assert not root.exists()
        fab_path, fab_hex = make_construction_file(tmp_path)
        bad_flag = ("0" if fab_hex[0] != "0" else "1") + fab_hex[1:]
        assert_raises_match(
            ValueError, "digest flag != frozen digest",
            bd.run_bounded_search_diagnostic,
            counts=injected_counts(), dev_table=injected_dev_table(),
            construction=str(fab_path), construction_digest=bad_flag,
            manifest_path=str(man), out_dir=tmp_path / "outflag",
        )
        assert not (tmp_path / "outflag").exists()


def test_manifest_and_dev_pin_refusals_zero_reads_zero_root():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        good = make_manifest(tmp_path, name="good.json")
        assert_raises_match(FileNotFoundError, "not found", bd.verify_dev_manifest,
                            str(tmp_path / "absent.json"))
        for idx, tamper in enumerate(("val-frames", "val-pairs", "hold-frames",
                                      "schema", "missing-source")):
            man = make_manifest(tmp_path, tamper=tamper, name=f"bad{idx}.json")
            assert_raises_match(ValueError, "manifest identity",
                                bd.verify_dev_manifest, man, source="1M")
            root = tmp_path / f"out{idx}"
            with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(bd, "load_v25_channel_counts", forbidden_loader):
                    with patched(bd, "load_pairs_table", forbidden_loader):
                        assert_raises_match(
                            ValueError, "manifest identity",
                            bd.run_bounded_search_diagnostic,
                            counts=injected_counts(), dev_table=injected_dev_table(),
                            construction=str(fab_path), construction_digest=fab_hex,
                            manifest_path=str(man), out_dir=root,
                        )
            assert not root.exists()
        # The DEV range pin refuses before the opens too, as does any
        # closed-HOLD overlap. Only CLI-uncovered constants reach the pin at
        # run level (CLI-covered drift trips the earlier frozen-flag refusal);
        # CLI-covered drift is pinned by direct pin calls below.
        root = tmp_path / "outpin"
        for field, value in (
            ("FROZEN_BLOCK_RANGES", ((1200, 1326), (1327, 1454), (1455, 1582))),
        ):
            with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(bd, field, value):
                    with patched(bd, "load_v25_channel_counts", forbidden_loader):
                        with patched(bd, "load_pairs_table", forbidden_loader):
                            assert_raises_match(
                                ValueError, "DEV block-range identity",
                                bd.run_bounded_search_diagnostic,
                                counts=injected_counts(), dev_table=injected_dev_table(),
                                construction=str(fab_path), construction_digest=fab_hex,
                                manifest_path=str(good), out_dir=root,
                            )
        assert not root.exists()
        for field, value, substr in (
            ("FROZEN_REMAINDER_FRAME_RANGE", (1585, 1599), "remainder_frame_range"),
            ("FROZEN_DEV_FRAME_RANGE", (1199, 1599), "dev_frame_range"),
        ):
            with patched(bd, field, value):
                assert_raises_match(ValueError, substr, bd.verify_dev_block_identity)
        with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(bd, "FROZEN_BLOCK_RANGES", ((1200, 1327), (1328, 1455), (1500, 1627))):
                with patched(bd, "load_v25_channel_counts", forbidden_loader):
                    with patched(bd, "load_pairs_table", forbidden_loader):
                        assert_raises_match(
                            ValueError, "overlaps closed HOLD",
                            bd.run_bounded_search_diagnostic,
                            counts=injected_counts(), dev_table=injected_dev_table(),
                            construction=str(fab_path), construction_digest=fab_hex,
                            manifest_path=str(good), out_dir=root,
                        )
        assert not root.exists()


# ---- deterministic slicing ----

def test_dev_slicing_blocks_and_remainder_exact():
    formation = bd.form_dev_blocks(injected_dev_table())
    assert formation["dev_frames"] == 400
    assert formation["dev_pairs"] == 102400
    assert formation["block_ranges"] == [[1200, 1327], [1328, 1455], [1456, 1583]]
    assert [b["frame_start"] for b in formation["blocks"]] == [1200, 1328, 1456]
    assert all(len(b["bob"]) == 32768 for b in formation["blocks"])
    assert formation["remainder"]["symbols"] == 4096
    assert formation["remainder"]["used"] is False
    closed_first, closed_last = bd.CLOSED_HOLD_FRAME_RANGE
    for start, end in formation["block_ranges"]:
        assert end < closed_first or start > closed_last


def test_malformed_dev_population_run_level_blocked_five_files():
    counts = injected_counts()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for idx, how in enumerate(("drop-frame", "pair-gap", "symbol-range", "no-dev")):
            root = tmp_path / f"bad{idx}"
            with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, "BLOCKED(dev_population_exact)",
                    bd.run_bounded_search_diagnostic,
                    counts=counts, dev_table=mutate_dev(injected_dev_table(), how),
                    expected_entropies=expected_seam(counts),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=root,
                )


def test_one_open_guards_refuse_reopen_with_zero_execution():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(bd, "_NPZ_CONTENT_OPENED", True):
                with patched(bd, "load_v25_channel_counts", forbidden_loader):
                    assert_raises_match(
                        ValueError, "reopen refused",
                        bd.run_bounded_search_diagnostic,
                        counts=None, dev_table=injected_dev_table(),
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=tmp_path / "o1",
                    )
            with patched(bd, "_DEV_PARQUET_CONTENT_OPENED", True):
                with patched(bd, "load_pairs_table", forbidden_loader):
                    assert_raises_match(
                        ValueError, "reopen refused",
                        bd.run_bounded_search_diagnostic,
                        counts=injected_counts(), dev_table=None,
                        construction=str(fab_path), construction_digest=fab_hex,
                        manifest_path=str(man), out_dir=tmp_path / "o2",
                    )
        assert not (tmp_path / "o1").exists()
        assert not (tmp_path / "o2").exists()
    assert bd._NPZ_CONTENT_OPENED is False
    assert bd._DEV_PARQUET_CONTENT_OPENED is False


def test_no_fitting_or_sampling_tokens_and_exact_call_counts():
    source = Path(bd.__file__).read_text(encoding="utf-8")
    for token in ("np.random.default_rng", "random_state", "sample_full_block",
                  "block_genie_risks", "list_decode", "fwht(", "posterior_APP",
                  "smooth_joint", "wilson_lower_bound", "results/",
                  "outputs_comparison", "git commit", "git push"):
        assert token not in source, token
    assert re.search(r"\bSCL\b", source) is None, "SCL"
    for token in ("bounded_search_seed_bits", "form_dev_blocks", "run_search_block",
                  "build_search_candidates", "candidate_nll_bits",
                  "raw_floor_diagnostics", "P20B-NBHD-1", "MemoryError",
                  "resource_abort", "oracle_isolation_ok"):
        assert token in source, token
    assert source.count("except MemoryError") >= 2
    assert source.count("raise  # resource stop owns MemoryError") >= 2
    assert bd.PLANNED_SC_CALLS == 15
    assert bd.PLANNED_TAG_INVOCATIONS == 9


# ---- arms, search, accounting ----

def test_three_arm_semantics_k_leakage_labels_and_call_counts():
    with tempfile.TemporaryDirectory() as tmp:
        run, s0, s1, s2 = full_run(Path(tmp) / "out")
        assert len(run.records) == 9
        assert run.summary["records_completed"] == 9
        assert run.summary["sc_calls"] == 15
        assert run.summary["tag_invocations"] == 9
        assert run.summary["aggregates"]["arms"]["S0_sc_base"]["key_dependent_bits"] == 3 * 34119
        assert run.summary["aggregates"]["arms"]["S1_bounded_search"]["key_dependent_bits"] == 3 * 34119
        assert run.summary["aggregates"]["arms"]["S2_true_l1_diagnostic"]["key_dependent_bits"] == 3 * 32524
        assert run.summary["aggregates"]["operational"]["key_dependent_bits"] == 6 * 34119
        assert run.summary["aggregates"]["operational"]["public_control_bits"] == 6 * 327743
        assert run.summary["outcome_label"] == bd.COMPLETE_LABEL
        assert run.summary["integrity_all_pass"] is True
        assert len(s0.seen) == 3 and len(s1.seen) == 3 and len(s2.seen) == 3
        # Slot order is block-major S0/S1/S2; every arm ran on every block.
        assert sorted(r["block_index"] for r in run.records
                      if r["arm"] == "S1_bounded_search") == [0, 1, 2]


def test_incremental_k_arithmetic_exact():
    assert 5 * (319 + 6492) + 64 == 34119
    assert 5 * 6492 + 64 == 32524
    assert 10 * 32768 + 63 == 327743
    assert 6 * 34119 + 3 * 32524 == TOTAL_KEY_BITS
    assert 9 * 327743 == TOTAL_PUBLIC_BITS


def test_p20b_seed_domain_arm_block_separation():
    seeds = {}
    for arm in bd.FROZEN_ARM_NAMES:
        for block in range(3):
            seed = bd.bounded_search_seed_bits(TEST_MASTER, 32768, arm, block)
            assert seed.shape == (327743,)
            seeds[(arm, block)] = seed.tobytes()
    assert len(set(seeds.values())) == 9
    for prefix in ("nbpolar-p16-operational-f13-seed",
                   "nbpolar-p17-operational-replication-seed",
                   "nbpolar-p18-holdout-microcheck-seed",
                   "nbpolar-p19-holdout-backoff-diagnostic-seed"):
        assert prefix != bd.SEED_PREFIX
    assert bd.FROZEN_TAG_MASTER not in (hm.FROZEN_TAG_MASTER, hb.FROZEN_TAG_MASTER)
    assert_raises_match(ValueError, "unknown frozen arm",
                         bd.bounded_search_seed_bits, TEST_MASTER, 32768, "base", 0)


def test_oracle_isolation_control_excluded_from_operational_aggregates():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _, _ = full_run(Path(tmp) / "out")
        operational = [r for r in run.records if r["arm_kind"] == "operational"]
        control = [r for r in run.records if r["arm_kind"] == "oracle_control"]
        assert len(operational) == 6 and len(control) == 3
        assert run.summary["aggregates"]["oracle_control"]["records"] == 3
        assert all(r["deployable"] is True for r in operational)
        assert all(r["deployable"] is False for r in control)
        assert all(r["oracle_l2_exact"] is None for r in operational)
        assert all(r["l1_exact"] is None and r["hard_l2_exact"] is None
                   and r["pair_exact"] is None for r in control)
        tampered = dict(control[0])
        tampered["arm_provenance"] = bd.OPERATIONAL_PROVENANCE
        assert bd.oracle_isolation_ok(run.records, final=True) is True
        assert bd.oracle_isolation_ok(
            [t if r is not control[0] else tampered for r, t in
             zip(run.records, run.records)], final=True) is False


def test_search_diagnostics_present_and_descriptive():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _, _ = full_run(Path(tmp) / "out", s1_scripts=["greedy", "neighbor", "greedy"])
        recovery = run.summary["aggregates"]["recovery"]
        assert recovery["search_better_count"] == 1
        assert [row["search_found_better"] for row in recovery["search_blocks"]] == [
            False, True, False]
        assert [row["selected_source"] for row in recovery["search_blocks"]] == [
            "greedy", "neighbor", "greedy"]
        # Found-count 1/3 is still descriptive COMPLETE, never a threshold.
        assert run.summary["outcome_label"] == bd.COMPLETE_LABEL
        s1_records = [r for r in run.records if r["arm"] == "S1_bounded_search"]
        assert all(r["rescores_used"] is not None and 1 <= r["rescores_used"] <= 8
                   for r in s1_records)
        assert all(r["deployable"] is True for r in s1_records)


def test_counts_buckets_and_recount_exact_and_tamper():
    with tempfile.TemporaryDirectory() as tmp:
        run, _, _, _ = full_run(Path(tmp) / "out")
        events = []
        for record in run.records:
            spec = bd.ARM_BY_NAME[record["arm"]]
            events.extend(bd.bounded_search_block_events(
                32768, spec, record["block_index"], record["frame_start"], record))
        recount = bd.bounded_search_recount_events(events)
        assert recount["key_dependent_bits"] == TOTAL_KEY_BITS
        assert recount["public_control_bits"] == TOTAL_PUBLIC_BITS
        assert recount["tag_invocations"] == 9
        tampered = dict(events[0])
        tampered["key_dependent_bits"] = int(tampered["key_dependent_bits"]) + 5
        assert_raises_match(ValueError, "transcript event id",
                             bd.bounded_search_recount_events,
                             [{"event_id": "bogus"}])
        tampered2 = dict(events[1])
        tampered2["event_type"] = "second_tag"
        assert_raises_match(ValueError, "not frozen",
                             bd.bounded_search_recount_events, [tampered2])
        assert recount["key_dependent_bits"] != (
            recount["key_dependent_bits"] + 5)


def test_outcome_classifier_every_bucket_and_precedence():
    assert bd.classify_operational_outcome is opf.classify_operational_outcome
    assert opf.classify_operational_outcome(
        l1_failed=True, l2_failed=False, nonfinite=True,
        tag_pass=False, label_match=False) == "nonfinite"
    assert opf.classify_operational_outcome(
        l1_failed=True, l2_failed=False, nonfinite=False,
        tag_pass=False, label_match=False) == "decode_failed"
    assert opf.classify_operational_outcome(
        l1_failed=False, l2_failed=False, nonfinite=False,
        tag_pass=False, label_match=False) == "verify_failed"
    assert opf.classify_operational_outcome(
        l1_failed=False, l2_failed=False, nonfinite=False,
        tag_pass=True, label_match=True) == "exact"
    assert opf.classify_operational_outcome(
        l1_failed=False, l2_failed=False, nonfinite=False,
        tag_pass=True, label_match=False) == "undetected"


def test_no_threshold_labels_all_recovery_patterns():
    assert bd.bounded_search_label(
        {name: True for name in bd.INTEGRITY_GATE_ORDER}) == bd.COMPLETE_LABEL
    gates = {name: True for name in bd.INTEGRITY_GATE_ORDER}
    gates["tags_exact"] = False
    assert bd.bounded_search_label(gates) == "BLOCKED(tags_exact)"


def test_budget_stop_abort_fill_and_precedence():
    with tempfile.TemporaryDirectory() as tmp:
        with patched(bd, "run_operational_block", FakeOperationalArm()):
            with patched(bd, "run_search_block", FakeSearchArm()):
                with patched(bd, "run_oracle_control_block", FakeControl()):
                    tmp_path = Path(tmp)
                    fab_path, fab_hex = make_construction_file(tmp_path)
                    man = make_manifest(tmp_path)
                    counts = injected_counts()
                    with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                        run = bd.run_bounded_search_diagnostic(
                            counts=counts, dev_table=injected_dev_table(),
                            expected_entropies=expected_seam(counts),
                            construction=str(fab_path), construction_digest=fab_hex,
                            manifest_path=str(man), out_dir=tmp_path / "out",
                            total_wall_s=1e-9,
                        )
        assert all(r["outcome"] == "resource_abort" for r in run.records)
        assert len(run.records) == 9
        assert run.summary["outcome_label"] == "BLOCKED(resource_limits_met_and_no_abort)"
        assert run.summary["resource_stop_fired"] is True


def test_search_memory_error_escapes_to_resource_path():
    def boom(*args, **kwargs):
        raise MemoryError("injected L1 OOM")

    tiny = tiny_tables(8)
    with patched(bd, "_decode_layer", boom):
        assert_raises_match(
            MemoryError, "injected L1 OOM", bd.run_search_block,
            n=8, block_index=0, frame_start=1200,
            bob=tiny["bob"], high_true=tiny["high"], low_true=tiny["low"],
            u1_true=tiny["u1"], u2_true=tiny["u2"], labels_true=tiny["labels"],
            labels_true_bits=tiny["labels_bits"], field=tiny["field"],
            p1_table=tiny["p1"], p2_table=tiny["p2"],
            l1_order=tiny["l1_order"], l2_order=tiny["l2_order"],
            k1=2, k2=3, master=TEST_MASTER, counts_arr=None,
        )
    # Runner level: a MemoryError seam becomes a resource BLOCKED, never success.
    with tempfile.TemporaryDirectory() as tmp:
        def seam_boom(**kwargs):
            raise MemoryError("injected runner OOM")

        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        counts = injected_counts()
        with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(bd, "run_operational_block", seam_boom):
                with patched(bd, "run_search_block", FakeSearchArm()):
                    with patched(bd, "run_oracle_control_block", FakeControl()):
                        try:
                            bd.run_bounded_search_diagnostic(
                                counts=counts, dev_table=injected_dev_table(),
                                expected_entropies=expected_seam(counts),
                                construction=str(fab_path), construction_digest=fab_hex,
                                manifest_path=str(man), out_dir=tmp_path / "out",
                            )
                        except bd.BoundedSearchDiagnosticResourceError as err:
                            assert "MemoryError" in str(err)
                        else:
                            raise AssertionError("expected resource BLOCKED on MemoryError")
        summary = json.loads((tmp_path / "out" / "aggregate_summary.json").read_text())
        assert summary["outcome_label"].startswith("BLOCKED(")


def test_search_ordinary_failure_keeps_decode_bucket():
    def boom(*args, **kwargs):
        raise RuntimeError("injected ordinary SC failure")

    tiny = tiny_tables(8)
    with patched(bd, "_decode_layer", boom):
        result, search = bd.run_search_block(
            n=8, block_index=0, frame_start=1200,
            bob=tiny["bob"], high_true=tiny["high"], low_true=tiny["low"],
            u1_true=tiny["u1"], u2_true=tiny["u2"], labels_true=tiny["labels"],
            labels_true_bits=tiny["labels_bits"], field=tiny["field"],
            p1_table=tiny["p1"], p2_table=tiny["p2"],
            l1_order=tiny["l1_order"], l2_order=tiny["l2_order"],
            k1=2, k2=3, master=TEST_MASTER, counts_arr=None,
        )
    assert result.outcome == "decode_failed"
    assert result.tag_invoked is False
    assert search["rescores_used"] == 0
    assert search["search_found_better"] is False


def test_precondition_failure_blocked_no_sc_call():
    def forbidden_sc(*args, **kwargs):
        raise AssertionError("no SC call may happen before preconditions pass")

    counts = np.zeros((1024, 1024), dtype=np.float64)
    counts[0, :] = 1.0
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
            with patched(bd, "_decode_layer", forbidden_sc):
                assert_raises_match(
                    ValueError, "BLOCKED(target_population_contract)",
                    bd.run_bounded_search_diagnostic,
                    counts=counts, dev_table=injected_dev_table(),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=tmp_path / "out",
                )


def test_five_file_scalar_only_inventory_and_resources():
    banned_keys = {"high_hat", "low_hat", "label_hat", "u_hat", "u1_hat", "u2_hat",
                   "logp", "seed_bits", "seed", "l1_order", "l2_order", "counts",
                   "counts_arr", "metrics", "metric", "bob", "alice_symbol",
                   "bob_symbol", "labels", "labels_bits", "p1_table", "p2_table",
                   "high", "low", "u1", "u2"}

    def walk_keys(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in banned_keys, key
                walk_keys(value)
        elif isinstance(obj, list):
            for value in obj:
                walk_keys(value)

    with tempfile.TemporaryDirectory() as tmp:
        run, _, _, _ = full_run(Path(tmp) / "out")
        out = Path(tmp) / "out"
        assert sorted(p.name for p in out.iterdir()) == sorted(bd.OUTPUT_FILES)
        for name in ("frozen_plan.json", "input_and_predecessor_identity.json",
                     "aggregate_summary.json"):
            walk_keys(json.loads((out / name).read_text(encoding="utf-8")))
        records = [json.loads(line) for line in
                   (out / "per_block_arm_outcomes.jsonl").read_text().splitlines()]
        assert len(records) == 9
        for record in records:
            walk_keys(record)
            assert bd.record_dict_consistent(record, n=32768)
            assert isinstance(record["resources"], dict)
        report = (out / "report.md").read_text(encoding="utf-8")
        for token in ("high_hat", "low_hat", "label_hat", "logp", "seed_bits",
                      "l1_order", "array("):
            assert token not in report, token
        summary = json.loads((out / "aggregate_summary.json").read_text(encoding="utf-8"))
        assert summary["records_completed"] == 9
        assert summary["attempt_read_accounting"]["attempts_consumed_by_this_run"] == 0
        assert summary["attempt_read_accounting"]["counts_content_opens"] == 0
        assert summary["attempt_read_accounting"]["dev_content_opens"] == 0


def test_real_mode_accounting_with_patched_loaders():
    with restored_open_guards():
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fab_path, fab_hex = make_construction_file(tmp_path)
            man = make_manifest(tmp_path)
            stub_npz = tmp_path / "counts.npz"
            stub_npz.write_bytes(b"stub")
            stub_parquet = tmp_path / "pairs.parquet"
            stub_parquet.write_bytes(b"stub")
            counts = injected_counts()
            dev = injected_dev_table()

            def fake_counts(path):
                assert str(path).endswith("counts.npz")
                return {"1M": counts}

            def fake_pairs(path):
                assert str(path).endswith("pairs.parquet")
                return dev

            with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(bd, "EXPECTED_NPZ_BYTES", 4):
                    with patched(bd, "load_v25_channel_counts", fake_counts):
                        with patched(bd, "load_pairs_table", fake_pairs):
                            with patched(bd, "run_operational_block", FakeOperationalArm()):
                                with patched(bd, "run_search_block", FakeSearchArm()):
                                    with patched(bd, "run_oracle_control_block", FakeControl()):
                                        run = bd.run_bounded_search_diagnostic(
                                            counts_path=str(stub_npz),
                                            dev_pairs=str(stub_parquet),
                                            expected_entropies=expected_seam(counts),
                                            construction=str(fab_path),
                                            construction_digest=fab_hex,
                                            manifest_path=str(man),
                                            out_dir=tmp_path / "out",
                                        )
            accounting = run.summary["attempt_read_accounting"]
            assert accounting["counts_content_opens"] == 1
            assert accounting["dev_content_opens"] == 1
            assert accounting["attempts_consumed_by_this_run"] == 1
            assert len(accounting["opened_content_paths"]) == 2


def test_real_mode_stat_change_blocks_with_earliest_gate():
    with restored_open_guards():
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fab_path, fab_hex = make_construction_file(tmp_path)
            man = make_manifest(tmp_path)
            stub_npz = tmp_path / "counts.npz"
            stub_npz.write_bytes(b"stub")
            stub_parquet = tmp_path / "pairs.parquet"
            stub_parquet.write_bytes(b"stub")
            counts = injected_counts()
            dev = injected_dev_table()

            def fake_counts(path):
                return {"1M": counts}

            def fake_pairs(path):
                return dev

            state = {"calls": 0}

            def drifting_stat(path):
                # Every stat call observes a new mtime: before != after.
                state["calls"] += 1
                if path is None:
                    return {"path": None, "size_bytes": None, "mtime_ns": None}
                return {"path": str(path), "size_bytes": 4,
                        "mtime_ns": 1000 + state["calls"]}

            with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                with patched(bd, "EXPECTED_NPZ_BYTES", 4):
                    with patched(bd, "_stat_record", drifting_stat):
                        with patched(bd, "load_v25_channel_counts", fake_counts):
                            with patched(bd, "load_pairs_table", fake_pairs):
                                with patched(bd, "run_operational_block", FakeOperationalArm()):
                                    with patched(bd, "run_search_block", FakeSearchArm()):
                                        with patched(bd, "run_oracle_control_block",
                                                      FakeControl()):
                                            run = bd.run_bounded_search_diagnostic(
                                                counts_path=str(stub_npz),
                                                dev_pairs=str(stub_parquet),
                                                expected_entropies=expected_seam(counts),
                                                construction=str(fab_path),
                                                construction_digest=fab_hex,
                                                manifest_path=str(man),
                                                out_dir=tmp_path / "out",
                                            )
            # Changed inputs between stat calls fail the earliest stat gate;
            # records still complete but the label is BLOCKED, never success.
            assert run.summary["records_completed"] == 9
            assert run.summary["outcome_label"] == "BLOCKED(input_stat_unchanged)"
            assert run.summary["integrity"]["input_stat_unchanged"] is False


def test_cli_parser_and_run_contract_refusals_before_open():
    parser = bd.build_parser()
    args = parser.parse_args([
        "--counts", "c", "--source", "1M", "--floor", "1e-15",
        "--n", "32768", "--k1", "319", "--k2", "6492",
        "--construction", "f", "--construction-digest", "d",
        "--dev-pairs", "p", "--dev-frames", "1200", "1599",
        "--block-frames", "128", "--remainder-frames", "1584", "1599",
        "--tag-master", "2026092080", "--chunk-rows", "512",
        "--tag-bits", "64", "--out-dir", "o",
    ])
    assert args.dev_frames == [1200, 1599]
    assert args.tag_master == 2026092080
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fab_path, fab_hex = make_construction_file(tmp_path)
        man = make_manifest(tmp_path)
        for over, substr in (
            ({"k1": 320}, "k1=319"),
            ({"floor": 1e-14}, "floor=1e-15"),
            ({"dev_frames": (1200, 1600)}, "dev-frames"),
            ({"tag_master": 2026092060}, "tag-master"),
            ({"bound": 16}, "M=8"),
        ):
            root = tmp_path / f"cli{abs(hash(substr)) % 100000}"
            with patched(bd, "FROZEN_CONSTRUCTION_DIGEST", fab_hex):
                assert_raises_match(
                    ValueError, substr, bd.run_bounded_search_diagnostic,
                    counts=injected_counts(), dev_table=injected_dev_table(),
                    construction=str(fab_path), construction_digest=fab_hex,
                    manifest_path=str(man), out_dir=root, **over,
                )
            assert not root.exists()


def test_existing_root_refusal_zero_execution():
    def forbidden_loader(*args, **kwargs):
        raise AssertionError("no loader may be called on a refusal")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "out"
        root.mkdir()
        with patched(bd, "load_v25_channel_counts", forbidden_loader):
            assert_raises_match(FileExistsError, "refusing to overwrite",
                                 bd.run_bounded_search_diagnostic,
                                 counts=injected_counts(), dev_table=injected_dev_table(),
                                 construction="f", construction_digest="d",
                                 manifest_path="m", out_dir=root)


def test_module_required_tokens_and_no_forbidden_paths():
    source = Path(bd.__file__).read_text(encoding="utf-8")
    for token in ("FROZEN_DEV_FRAME_RANGE = (1200, 1599)",
                  "CLOSED_HOLD_FRAME_RANGE = (1600, 1983)",
                  "S1_bounded_search", "S2_true_l1_diagnostic", "S0_sc_base",
                  "deployable", "search_found_better", "rescores_used",
                  "raw_zero_count_hits", "floor_hit_log_loss_bits",
                  "l2_nll_candidate_H_bits", "l2_nll_true_H_bits",
                  "first_error_layer", "nine_records_exact",
                  "dev_split_manifest_identity", "dev_block_range_identity",
                  "dev_population_exact"):
        assert token in source, token
    for token in ("hold-frames", "hold_frames", "FROZEN_HOLD_FRAME_RANGE",
                  "1600, 1999", "1984, 1999", "l1_plus", "l2_plus"):
        assert token not in source, token


# ---- tiny real-SC search behavior ----

def stub_metrics(n, *, choice, runner, gap, seed=TEST_SEEDS[3]):
    """Hand-built SC decision metrics: `choice` wins by `gap` (ln) over `runner`."""
    rng = np.random.default_rng(seed)
    metrics = np.full((n, 32), -8.0)
    metrics[np.arange(n), choice] = 0.0
    metrics[np.arange(n), runner] = -float(gap)
    metrics = metrics - np.logaddexp.reduce(metrics, axis=1, keepdims=True)
    return metrics


def test_candidate_building_ranking_and_bound():
    n = 8
    field = opf_provenance_field()
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
        polar_transform,
    )

    rng = np.random.default_rng(TEST_SEEDS[0])
    u1 = rng.integers(0, 32, size=n).astype(np.int64)
    u2 = rng.integers(0, 32, size=n).astype(np.int64)
    m1 = stub_metrics(n, choice=u1, runner=(u1 + 1) % 32, gap=0.05)
    m2 = stub_metrics(n, choice=u2, runner=(u2 + 1) % 32, gap=5.0)
    sc1 = SimpleNamespace(decision_metrics=m1, u_hat=u1,
                          x_hat=polar_transform(u1, field=field, alpha=2))
    sc2 = SimpleNamespace(decision_metrics=m2, u_hat=u2,
                          x_hat=polar_transform(u2, field=field, alpha=2))
    l1_pos = np.array([0, 1], dtype=np.int64)
    l2_pos = np.array([2, 3], dtype=np.int64)
    candidates = bd.build_search_candidates(
        n=n, u1_hat=u1, u2_hat=u2, sc1=sc1, sc2=sc2,
        l1_positions=l1_pos, l2_positions=l2_pos, field=field, bound=8)
    # Greedy + all 12 undisclosed coords ranked: 6 L1 alts (gap .05) first.
    assert len(candidates) == 8  # bound caps at M
    assert candidates[0]["kind"] == "greedy"
    assert all(c["kind"] == "neighbor" for c in candidates[1:])
    assert [c["layer"] for c in candidates[1:]] == ["L1"] * 6 + ["L2"]
    assert all(abs(c["gap_ln"] - 0.05) < 1e-9 for c in candidates[1:7])
    # Disclosed positions are never varied.
    varied = {(c["layer"], c["coord"]) for c in candidates[1:]}
    assert ("L1", 0) not in varied and ("L1", 1) not in varied
    assert ("L2", 2) not in varied and ("L2", 3) not in varied
    # Each alternate differs from greedy in exactly one U symbol.
    for cand in candidates[1:]:
        if cand["layer"] == "L1":
            assert np.array_equal(cand["low"], candidates[0]["low"])
            diff = np.flatnonzero(
                polar_transform(cand["high"], field=field, alpha=2) != u1)
            assert diff.tolist() == [cand["coord"]]
        else:
            assert np.array_equal(cand["high"], candidates[0]["high"])


def test_candidate_nll_selection_greedy_wins_ties():
    bob = np.array([0, 1, 2, 3], dtype=np.int64)
    high = np.array([5, 5, 5, 5], dtype=np.int64)
    low = np.array([7, 7, 7, 7], dtype=np.int64)
    p1 = np.full((32, 1024), 1.0 / 32)
    p2 = np.full((32, 1024, 32), 1.0 / 32)
    scored = bd.candidate_nll_bits(bob, high, low, p1, p2)
    assert scored["total_nll_bits"] == 8 * 5.0
    p1b = p1.copy()
    p1b[6, 0] = 0.5
    scored2 = bd.candidate_nll_bits(
        bob, np.array([6, 5, 5, 5]), low, p1b, p2)
    assert scored2["total_nll_bits"] < scored["total_nll_bits"]
    p1c = p1.copy()
    p1c[5, 0] = 0.0
    scored3 = bd.candidate_nll_bits(bob, high, low, p1c, p2)
    assert scored3["total_nll_bits"] == float("inf")


def test_search_selects_better_neighbor_with_stubbed_sc():
    n = 8
    tiny = tiny_tables(n)
    field = tiny["field"]
    rng = np.random.default_rng(TEST_SEEDS[0])
    u1 = rng.integers(0, 32, size=n).astype(np.int64)
    u2 = rng.integers(0, 32, size=n).astype(np.int64)
    from comparison_bench.src.comparison_bench.formal_ir.nbpolar.transform import (
        polar_transform,
    )

    x1 = polar_transform(u1, field=field, alpha=2)
    x2 = polar_transform(u2, field=field, alpha=2)
    m1 = stub_metrics(n, choice=u1, runner=(u1 + 1) % 32, gap=0.02)
    m2 = stub_metrics(n, choice=u2, runner=(u2 + 1) % 32, gap=9.0)
    sc1 = SimpleNamespace(decision_metrics=m1, u_hat=u1, x_hat=x1)
    sc2 = SimpleNamespace(decision_metrics=m2, u_hat=u2, x_hat=x2)
    l1_pos = np.array([0], dtype=np.int64)
    l2_pos = np.array([1], dtype=np.int64)
    # Plant the coherent-model preference: the L1 alternate at the
    # smallest-gap coord beats greedy; everything else is uniform.
    p1 = np.full((32, 1024), 1.0 / 32)
    p2 = np.full((32, 1024, 32), 1.0 / 32)
    alt_u1 = u1.copy()
    # Lowest-gap coord among undisclosed L1 coords (excluding disclosed 0).
    gaps = m1[np.arange(n), u1] - np.array(
        [max(v for s, v in enumerate(row) if s != int(u1[i]))
         for i, row in enumerate(m1)])
    order = sorted((g for i, g in enumerate(gaps) if i != 0))
    assert order[0] < 0.1
    coord = int(np.argmin([g if i != 0 else np.inf for i, g in enumerate(gaps)]))
    alt_u1[coord] = int(np.argmax([v if s != int(u1[coord]) else -np.inf
                                   for s, v in enumerate(m1[coord])]))
    alt_x1 = polar_transform(alt_u1, field=field, alpha=2)
    bob = tiny["bob"]
    p1[alt_x1, bob] = 0.9
    p1 = p1 / p1.sum(axis=0, keepdims=True)

    calls = {"sc": 0}

    def fake_decode(logp, *, field, positions, disclosed):
        if len(sc1_seen) == 0:
            sc1_seen.append(True)
            return sc1
        return sc2

    sc1_seen: list = []
    tags_a = []

    def tag_a(bits, seed, tag_bits):
        # Accepted pattern: one final verification = two tag_fn evaluations
        # (true bits, then selected-label bits) under one fixed seed.
        tags_a.append((np.array(bits, copy=True), bytes(seed), int(tag_bits)))
        return bd.toeplitz_tag_fn(bits, seed, tag_bits)

    tags_b = []

    def tag_b(bits, seed, tag_bits):
        tags_b.append((np.array(bits, copy=True), bytes(seed), int(tag_bits)))
        return bd.toeplitz_tag_fn(bits, seed, tag_bits)

    with patched(bd, "_decode_layer", fake_decode):
        result_a, search_a = bd.run_search_block(
            n=n, block_index=0, frame_start=1200,
            bob=bob, high_true=tiny["high"], low_true=tiny["low"],
            u1_true=tiny["u1"], u2_true=tiny["u2"], labels_true=tiny["labels"],
            labels_true_bits=tiny["labels_bits"], field=field,
            p1_table=p1, p2_table=p2,
            l1_order=tiny["l1_order"], l2_order=tiny["l2_order"],
            k1=1, k2=1, master=TEST_MASTER, counts_arr=None,
            tag_fn=tag_a, calls=calls,
        )
    assert calls["sc"] == 2  # rescore-only: no extra SC calls
    assert search_a["rescores_used"] == 8
    assert search_a["selected_source"] == "neighbor"
    assert search_a["search_found_better"] is True
    assert search_a["nll_improvement_bits"] > 0
    assert len(tags_a) == 2  # exactly one final verification (true + selected)
    assert np.array_equal(tags_a[0][0], tiny["labels_bits"])
    assert tags_a[0][1] == tags_a[1][1]  # one fixed seed, never tag-guided
    with patched(bd, "_decode_layer", fake_decode):
        calls2 = {"sc": 0}
        sc1_seen.clear()
        result_b, search_b = bd.run_search_block(
            n=n, block_index=0, frame_start=1200,
            bob=bob, high_true=tiny["high"], low_true=tiny["low"],
            u1_true=tiny["u1"], u2_true=tiny["u2"], labels_true=tiny["labels"],
            labels_true_bits=tiny["labels_bits"], field=field,
            p1_table=p1, p2_table=p2,
            l1_order=tiny["l1_order"], l2_order=tiny["l2_order"],
            k1=1, k2=1, master=TEST_MASTER, counts_arr=None,
            tag_fn=tag_b, calls=calls2,
        )
    # Selection never depends on the tag: identical search outcome.
    assert search_b["selected_index"] == search_a["selected_index"]
    assert search_b["selected_source"] == search_a["selected_source"]
    assert result_b.pair_exact == result_a.pair_exact
    assert result_b.oracle_l2_exact is None
    assert isinstance(result_a.l1_exact, bool)


def test_tiny_real_search_full_disclosure_anchor():
    n = 8
    tiny = tiny_tables(n)
    seed = bd.bounded_search_seed_bits(TEST_MASTER, n, "S1_bounded_search", 0)
    tag_calls = []

    def tag_fn(bits, _seed, tag_bits):
        tag_calls.append((np.array(bits, copy=True), bytes(_seed)))
        return bd.toeplitz_tag_fn(bits, seed, tag_bits)

    calls = {"sc": 0}
    result, search = bd.run_search_block(
        n=n, block_index=0, frame_start=1200,
        bob=tiny["bob"], high_true=tiny["high"], low_true=tiny["low"],
        u1_true=tiny["u1"], u2_true=tiny["u2"], labels_true=tiny["labels"],
        labels_true_bits=tiny["labels_bits"], field=tiny["field"],
        p1_table=tiny["p1"], p2_table=tiny["p2"],
        l1_order=np.arange(n, dtype=np.int64), l2_order=np.arange(n, dtype=np.int64),
        k1=n, k2=n, master=TEST_MASTER, counts_arr=None,
        tag_fn=tag_fn, calls=calls,
    )
    assert calls["sc"] == 2
    assert result.outcome == "exact"
    assert result.l1_exact is True and result.hard_l2_exact is True
    assert result.pair_exact is True
    assert search["selected_source"] == "greedy"
    assert search["search_found_better"] is False
    assert search["rescores_used"] == 1  # no undisclosed coords: greedy only
    assert len(tag_calls) == 2  # one verification: true bits + selected bits
    assert np.array_equal(tag_calls[0][0], tiny["labels_bits"])


def test_tiny_real_operational_and_oracle_via_p20b_closure():
    n = 8
    tiny = tiny_tables(n)
    seed0 = bd.bounded_search_seed_bits(TEST_MASTER, n, "S0_sc_base", 0)

    def tag_fn(bits, _seed, tag_bits):
        return bd.toeplitz_tag_fn(bits, seed0, tag_bits)

    calls = {"sc": 0}
    result = bd.run_operational_block(
        n=n, stream_seed=1200, block_index=0,
        bob=tiny["bob"], high_true=tiny["high"], low_true=tiny["low"],
        u1_true=tiny["u1"], u2_true=tiny["u2"], labels_true=tiny["labels"],
        labels_true_bits=tiny["labels_bits"], field=tiny["field"],
        p1_table=tiny["p1"], p2_table=tiny["p2"],
        l1_order=tiny["l1_order"], l2_order=tiny["l2_order"],
        k1=2, k2=3, master=TEST_MASTER, tag_fn=tag_fn, calls=calls,
    )
    assert calls["sc"] == 2
    assert result.tag_invoked is True
    assert result.oracle_l2_exact is None
    seed2 = bd.bounded_search_seed_bits(TEST_MASTER, n, "S2_true_l1_diagnostic", 0)

    def tag_fn2(bits, _seed, tag_bits):
        return bd.toeplitz_tag_fn(bits, seed2, tag_bits)

    calls2 = {"sc": 0}
    control = bd.run_oracle_control_block(
        n=n, block_index=0, frame_start=1200,
        bob=tiny["bob"], high_true=tiny["high"], low_true=tiny["low"],
        u1_true=tiny["u1"], u2_true=tiny["u2"], labels_true=tiny["labels"],
        labels_true_bits=tiny["labels_bits"], field=tiny["field"],
        p2_table=tiny["p2"], l2_order=tiny["l2_order"], k2=3,
        master=TEST_MASTER, tag_fn=tag_fn2, calls=calls2,
    )
    assert calls2["sc"] == 1
    assert control.provenance == bd.ORACLE_PROVENANCE
    assert control.l1_exact is None and control.pair_exact is None
    assert isinstance(control.oracle_l2_exact, bool)


def test_search_layer_endpoints_and_diagnostics_tiny_real():
    n = 8
    tiny = tiny_tables(n)
    seed = bd.bounded_search_seed_bits(TEST_MASTER, n, "S1_bounded_search", 1)

    def tag_fn(bits, _seed, tag_bits):
        return bd.toeplitz_tag_fn(bits, seed, tag_bits)

    result, search = bd.run_search_block(
        n=n, block_index=1, frame_start=1328,
        bob=tiny["bob"], high_true=tiny["high"], low_true=tiny["low"],
        u1_true=tiny["u1"], u2_true=tiny["u2"], labels_true=tiny["labels"],
        labels_true_bits=tiny["labels_bits"], field=tiny["field"],
        p1_table=tiny["p1"], p2_table=tiny["p2"],
        l1_order=tiny["l1_order"], l2_order=tiny["l2_order"],
        k1=2, k2=3, master=TEST_MASTER, counts_arr=None, tag_fn=tag_fn,
    )
    assert 1 <= search["rescores_used"] <= 8
    assert search["selected_source"] in ("greedy", "neighbor")
    assert result.truth_leak_violation is False
    first = bd.first_error_coordinate(
        result.high_hat, result.low_hat, tiny["high"], tiny["low"])
    assert first["first_error_layer"] in ("L1", "L2", None)


def test_zero_protected_opens_audit():
    assert bd._NPZ_CONTENT_OPENED is False
    assert bd._DEV_PARQUET_CONTENT_OPENED is False
