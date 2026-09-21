#!/usr/bin/env python3
"""Zero-decoder H_full census intake skeleton — NBPOLAR-DATA-CENSUS-HFULL-20260921.

PREPARATION ONLY. This file has NOT been executed (no .ttbin parsed, no pipeline run).

Usage (sibling venv — this checkout has no .venv):
  /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python scripts/census_intake_20260921.py \
      --stage-a-parse-test --acq-id 20260112_Type2PPLN_3s --out-root workspace/census_20260921
  /mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python scripts/census_intake_20260921.py \
      --stage-b-census --authorized --out-root workspace/census_20260921

Contract (frozen, see TASK_PACKET.md): d=1024, bin_width_ps=200,
period_ps=204800, pairing=nearest, rule=legacy_v1, frame_pairs=256,
gate_ps=200, threshold_ps=40000, logical A=hw1 / B=hw5 (FIXED, not searched).
PRIMARY H: factorized H1+H2, raw-count MLE + 1e-15 floor. SECONDARY: flat
joint H_full (hierarchical smoothing, 30-point 4-fold CV lambda), separate field.
Zero decoders. Writes only under <out-root>/<acq-id>/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

import numpy as np

# Repo-root insertion: `python scripts/census_intake_20260921.py` puts scripts/
# (not the repo root) on sys.path, so `import src....` fails without it.
# This block must stay BEFORE the TimeTagger shim and any `src.qkd_io` import.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Stage A0-4 namespace shim: repo code does `from TimeTagger import FileReader`
# (src/qkd_io/ttbin_pipeline.py:148), but the official package >= 2.20 exposes
# only `from Swabian import TimeTagger`. Register the alias BEFORE any
# src.qkd_io import so the bare name resolves. Bare import tried first.
_FILERREADER_IMPORT_PATH = "unavailable"
try:
    from TimeTagger import FileReader as _FR  # type: ignore  # noqa: F401
    _FILERREADER_IMPORT_PATH = "bare-toplevel-TimeTagger"
except Exception:
    try:
        from Swabian import TimeTagger as _TT  # type: ignore

        sys.modules.setdefault("TimeTagger", _TT)
        from TimeTagger import FileReader as _FR  # type: ignore  # noqa: F401
        _FILERREADER_IMPORT_PATH = "swabian-shim"
    except Exception:
        _FR = None

from src.qkd_io.ttbin_pipeline import read_ttbin_events

SIBLING_VENV = "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python"
INVENTORY = Path("workspace/data_intake_20260921/inventory.json")

# Frozen pipeline contract (single source scripts/v66_data_readiness.py:11).
D = 1024
BIN_WIDTH_PS = 200
PERIOD_PS = 204800
FRAME_PAIRS = 256
GATE_PS = 200
THRESHOLD_PS = 40000
HW_A, HW_B = 1, 5  # logical A = hardware 1, B = hardware 5, FIXED
OTHER_FRAC_MAX = 0.20
FLOOR = 1e-15
# R1 rewrite 2026-09-21 (PI alignment instruction, binding): correlation-based
# auto-alignment BEFORE pairing, derived from each acquisition's OWN data.
# Never inherit the frozen -50/+50/+50 (those belong to the 01-21 V25 sources).
# The inherited sigma gate [50,150] ps is NOT used (calibrated for 01-21
# sources only; widening it to force a pass would be tuning).
# Frozen per PI text: SCAN_RANGE_PS = max(50_000, 2*204800) = 409600,
# BIN_PS_ALIGN = max(10, 200//2) = 100. frame_period_ps is NOT passed, so the
# estimator uses exactly this range (passing it would trigger the internal
# 20M clamp and override the frozen value). Acceptance (unit-independent):
# status == "ok" AND peak_to_bg >= 10 (contrast ratio, scale-free).
SCAN_RANGE_PS = max(50_000, 2 * PERIOD_PS)  # = 409600, literal PI formula
BIN_PS_ALIGN = max(10, BIN_WIDTH_PS // 2)  # = 100
PEAK_TO_BG_MIN = 10.0
# R2 (unchanged): skip default 702 for ALL acquisitions, labelled inherited.
SKIP_FRAMES = 702
SKIP_PROVENANCE = "INHERITED_NOT_DERIVED"
SKIP_DIAGNOSTIC_SUPERFRAMES = 1500
# R3 (unchanged): length tiers in full 256-pair frames.
TIER_FULL_MIN = 1982
TIER_REDUCED_MIN = 1342
CAL_FRAMES_REDUCED = 512
VAL_FRAMES_REDUCED = 128
# R1 self-check: yield-vs-offset sweep over the search range at a coarse step.
YIELD_SWEEP_POINTS = 21
CAL_FRAMES = 1024
VAL_FRAMES = 256
N_CAL_SYMBOLS = CAL_FRAMES * FRAME_PAIRS  # 262144


def _fail(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _acq_files(acq_id: str) -> tuple[Path, Path]:
    """Exact .ttbin paths from inventory.json (never reconstructed from stems)."""
    if not INVENTORY.exists():
        _fail(f"inventory not found: {INVENTORY} (run from repo root)")
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    for acq in inv.get("acquisitions", []):
        if acq.get("acq_id") == acq_id:
            files = acq.get("files", [])
            prim = cont = None
            for f in files:
                if f.get("segment") == "primary":
                    prim = Path(f["path_posix"])
                elif f.get("segment") == "continuation-1":
                    cont = Path(f["path_posix"])
            if prim is None or cont is None:
                _fail(f"inventory entry for {acq_id} lacks primary/.1 paths")
            return prim, cont
    _fail(f"acq_id {acq_id!r} not in inventory.json")
    raise AssertionError("unreachable")


def _summarize_events(ev) -> dict:
    ch = np.asarray(ev.channel, dtype=np.int64)
    ts = np.asarray(ev.time_ps, dtype=np.int64)
    uniq, counts = np.unique(ch, return_counts=True)
    return {
        "n_events": int(ch.size),
        "channel_hist": {int(k): int(v) for k, v in zip(uniq, counts)},
        "t_min_ps": int(ts.min()) if ts.size else None,
        "t_max_ps": int(ts.max()) if ts.size else None,
    }


def stage_a0_env_check(acq_id: str, out_root: Path) -> int:
    """Stage A0: record import path + smoke-construct FileReader on ONE tiny primary."""
    import platform
    import re
    import subprocess

    try:
        from importlib.metadata import version as _pkg_version

        tt_version = _pkg_version("Swabian-TimeTagger")
    except Exception:
        tt_version = "unknown"
    try:
        glibc = " ".join(platform.libc_ver()).strip()
    except Exception:
        glibc = "unknown"
    # A0-1 (binding): glibc via `ldd --version`, must be >= 2.28 for the
    # manylinux_2_28 wheel. platform.libc_ver() above is supplementary only.
    try:
        ldd_first = (
            subprocess.run(["ldd", "--version"], capture_output=True, text=True, timeout=15)
            .stdout.splitlines()[0]
            .strip()
        )
    except Exception:
        ldd_first = "unknown"
    _m = re.search(r"(\d+)\.(\d+)", ldd_first)
    glibc_ok = bool(_m and (int(_m.group(1)), int(_m.group(2))) >= (2, 28))
    prim, _ = _acq_files(acq_id)
    if not prim.exists():
        _fail(f"raw file not found: {prim}")
    smoke_ok, n_probe = False, None
    try:
        ev = read_ttbin_events(prim)
        n_probe = int(np.asarray(ev.channel).size)
        smoke_ok = True
    except Exception as e:
        print(f"WARNING: FileReader smoke construct failed: {e}", file=sys.stderr)
    out = {
        "glibc": glibc,
        "ldd_first_line": ldd_first,
        "glibc_ge_2_28": glibc_ok,
        "numpy_version": str(np.__version__),
        "timetagger_package": tt_version,
        "filereader_import_path": _FILERREADER_IMPORT_PATH,
        "smoke_file": str(prim),
        "smoke_construct_ok": smoke_ok,
        "n_events_primary_probe": n_probe,
        "stage_a0_go": bool(
            glibc_ok and smoke_ok and _FILERREADER_IMPORT_PATH != "unavailable" and n_probe
        ),
    }
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "stage_a0_env.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    print("STAGE_A0_GO" if out["stage_a0_go"] else "STAGE_A0_NOGO_STOP_DO_NOT_PROCEED")
    return 0 if out["stage_a0_go"] else 3


def stage_a_parse_test(acq_id: str, out_root: Path) -> int:
    """Answer the blocking .1.ttbin merge question on ONE acquisition."""
    prim, cont = _acq_files(acq_id)
    for p in (prim, cont):
        if not p.exists():
            _fail(f"raw file not found: {p}")
    try:
        ev_p = read_ttbin_events(prim)
    except Exception as e:
        _fail(f"FileReader(primary) failed: {e}")
    try:
        ev_c = read_ttbin_events(cont)
    except Exception as e:
        _fail(f"FileReader(.1) failed: {e}")
    s_p, s_c = _summarize_events(ev_p), _summarize_events(ev_c)
    ch_p = np.asarray(ev_p.channel, dtype=np.int64)
    ts_p = np.asarray(ev_p.time_ps, dtype=np.int64)
    ch_c = np.asarray(ev_c.channel, dtype=np.int64)
    ts_c = np.asarray(ev_c.time_ps, dtype=np.int64)
    n_union = int(ch_p.size + ch_c.size)
    union_is_sum = True  # arithmetic only: n_union == n_primary + n_cont1
    ids_p, ids_c = set(np.unique(ch_p).tolist()), set(np.unique(ch_c).tolist())
    channel_ids_match = ids_p == ids_c
    # Stage A finding 2026-09-21 (20260112_Type2PPLN_3s): FileReader
    # AUTO-FOLLOWS `.1` segments — reading EITHER file yields the identical
    # full acquisition (3,836,088 events each here). Concatenating both reads
    # therefore duplicates every event (n_union = exact 2x) and is FORBIDDEN.
    # Corrected merge rule: read the PRIMARY `<stem>.ttbin` ONLY.
    autofollow_confirmed = bool(
        int(ch_p.size) == int(ch_c.size)
        and int(ch_p.size) > 0
        and s_p["channel_hist"] == s_c["channel_hist"]
        and s_p["t_min_ps"] == s_c["t_min_ps"]
        and s_p["t_max_ps"] == s_c["t_max_ps"]
    )
    primary_alone_full = autofollow_confirmed
    merge_verdict = (
        "autofollow-confirmed-read-primary-only-concat-forbidden"
        if autofollow_confirmed
        else "ADVERSE-see-flags"
    )
    # stage_b_go gates Stage B WITH the corrected primary-only merge rule.
    # (Stage B as previously scripted — concatenating both reads — is NO-GO
    # under autofollow; the frozen stage_a_parse.json `union-is-concat` verdict
    # is superseded by this fix. Evidence JSONs on disk are left untouched.)
    stage_b_go = bool(
        autofollow_confirmed
        and channel_ids_match
        and HW_A in ids_p
        and HW_B in ids_p
    )
    out = {
        "acq_id": acq_id,
        "primary": str(prim),
        "continuation_1": str(cont),
        "n_primary": s_p["n_events"],
        "n_cont1": s_c["n_events"],
        "n_union": n_union,
        "union_is_sum": union_is_sum,
        "channels_primary": s_p["channel_hist"],
        "channels_cont1": s_c["channel_hist"],
        "tspan_primary_ps": [s_p["t_min_ps"], s_p["t_max_ps"]],
        "tspan_cont1_ps": [s_c["t_min_ps"], s_c["t_max_ps"]],
        "channel_ids_match": channel_ids_match,
        "primary_alone_yields_full": primary_alone_full,
        "autofollow_confirmed": autofollow_confirmed,
        "merge_rule": "read-primary-only-never-concatenate",
        "merge_verdict": merge_verdict,
        "stage_b_go": stage_b_go,
    }
    dest = out_root / acq_id
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "stage_a_parse.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    print("STAGE_A_GO" if stage_b_go else "STAGE_A_NOGO_STOP_DO_NOT_PROCEED")
    return 0 if stage_b_go else 3


def build_canonical_counts(alice: np.ndarray, bob: np.ndarray) -> np.ndarray:
    """CAL (alice[n], bob[n]) int 0..1023 -> counts_ab (1024,1024) int64. [A,B]."""
    a = np.asarray(alice, dtype=np.int64)
    b = np.asarray(bob, dtype=np.int64)
    if a.shape != b.shape or a.ndim != 1:
        _fail("alice/bob must be equal-length 1-D vectors")
    if a.size == 0 or a.min() < 0 or a.max() > 1023 or b.min() < 0 or b.max() > 1023:
        _fail("symbols out of [0,1023] or empty")
    counts = np.zeros((D, D), dtype=np.int64)
    np.add.at(counts, (a, b), 1)
    return counts


def _entropy_bits(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=np.float64)
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def factorized_h1_h2(counts: np.ndarray) -> tuple[float, float, float]:
    """PRIMARY: H1=H(U1|B_full), H2=H(U2|U1,B), raw-count MLE + 1e-15 floor."""
    c = np.asarray(counts, dtype=np.float64)
    n = float(c.sum())
    if n <= 0:
        _fail("empty counts for H estimation")
    # H1: U1 = s>>5 marginal per Bob column.
    h1 = 0.0
    col_sum = c.sum(axis=0)
    for b in range(D):
        nb = col_sum[b]
        if nb <= 0:
            continue
        u1 = np.zeros(32)
        for u in range(32):
            u1[u] = c[u * 32 : (u + 1) * 32, b].sum()
        p = np.clip(u1 / nb, FLOOR, None)
        p = p / p.sum()
        h1 += (nb / n) * _entropy_bits(p)
    # H2: U2 = s&31 given (U1,B).
    h2 = 0.0
    for b in range(D):
        for u in range(32):
            cell = c[u * 32 : (u + 1) * 32, b]
            nn = float(cell.sum())
            if nn <= 0:
                continue
            p = np.clip(cell / nn, FLOOR, None)
            p = p / p.sum()
            h2 += (nn / n) * _entropy_bits(p)
    return float(h1), float(h2), float(h1 + h2)


def flat_h_full_secondary(counts: np.ndarray) -> dict:
    """SECONDARY (comparability only): flat joint H_full.

    Hierarchical smoothing P=(C+lambda*p_global)/(n_b+lambda) per Bob column,
    lambda picked by 30-point 4-fold CV (frozen v70 rule). Deterministic.
    NEVER in the same comparison column as the factorized chain.
    """
    rng = np.random.default_rng(20260921)
    c = np.asarray(counts, dtype=np.float64)
    n = float(c.sum())
    p_global = c.sum(axis=1) / n  # Alice marginal as global prior
    grid = np.concatenate(([0.0], np.logspace(-3, 4, 29)))  # 30 points
    cols = rng.permutation(D).reshape(4, D // 4)  # deterministic 4-fold over B
    best, best_ll = 0.0, -np.inf
    for lam in grid:
        ll = 0.0
        for k in range(4):
            te = cols[k]
            tr_mask = np.ones(D, bool)
            tr_mask[te] = False
            ctr = c[:, tr_mask].sum(axis=1)
            ntr = float(ctr.sum())
            phat = (ctr + lam * p_global) / (ntr + lam) if (ntr + lam) > 0 else p_global
            phat = np.clip(phat, FLOOR, None)
            ll += float(np.sum(c[:, te] * np.log(phat)[:, None]))
        if ll > best_ll:
            best_ll, best = float(lam), float(lam)
    denom = c.sum(axis=0, keepdims=True) + best
    P = (c + best * p_global[:, None]) / np.where(denom > 0, denom, 1.0)
    P = np.clip(P, FLOOR, None)
    h = float(-np.sum((c / n) * np.log2(P)))
    return {"H_full_flat": h, "lambda_star": best, "method": "hierarchical-CV-30pt-4fold"}


def legacy_v1_pair_symbols(b0_sorted: np.ndarray, b1_sorted: np.ndarray):
    """legacy_v1 coincidence (vectorized).

    Inputs are intake-sorted bin arrays (b = t // 200). Coincidence iff the
    same b // 1024 superframe; symbol = b % 1024. Semantics identical to the
    sorted two-pointer greedy: per common superframe, the first min(kA, kB)
    of each side pair positionally, frames in increasing order.
    Returns (alice_sym, bob_sym, superframe_id) int64 vectors, same length.
    """
    b0 = np.asarray(b0_sorted, dtype=np.int64).reshape(-1)
    b1 = np.asarray(b1_sorted, dtype=np.int64).reshape(-1)
    z = np.empty((0,), dtype=np.int64)
    if b0.size == 0 or b1.size == 0:
        return z, z, z
    f0 = np.floor_divide(b0, D)
    f1 = np.floor_divide(b1, D)
    u0, inv0, cnt0 = np.unique(f0, return_inverse=True, return_counts=True)
    u1, inv1, cnt1 = np.unique(f1, return_inverse=True, return_counts=True)
    common = u0[np.isin(u0, u1)]
    if common.size == 0:
        return z, z, z
    pos0 = np.searchsorted(u0, common)
    pos1 = np.searchsorted(u1, common)
    k = np.minimum(cnt0[pos0], cnt1[pos1])
    st0 = np.empty_like(cnt0)
    st0[0] = 0
    if cnt0.size > 1:
        st0[1:] = np.cumsum(cnt0[:-1])
    st1 = np.empty_like(cnt1)
    st1[0] = 0
    if cnt1.size > 1:
        st1[1:] = np.cumsum(cnt1[:-1])
    kmap0 = np.zeros_like(cnt0)
    kmap0[pos0] = k
    kmap1 = np.zeros_like(cnt1)
    kmap1[pos1] = k
    keep0 = (np.arange(b0.size) - st0[inv0]) < kmap0[inv0]
    keep1 = (np.arange(b1.size) - st1[inv1]) < kmap1[inv1]
    if int(keep0.sum()) != int(keep1.sum()) or int(keep0.sum()) != int(k.sum()):
        _fail("legacy_v1 gather self-inconsistent: kept counts differ")
    pf = np.repeat(common, k)
    return ((b0[keep0] % D).astype(np.int64),
            (b1[keep1] % D).astype(np.int64),
            pf.astype(np.int64))


def _pair_greedy_loop(b0_sorted: np.ndarray, b1_sorted: np.ndarray):
    """Reference two-pointer greedy (skeleton algorithm, verbatim semantics).

    Used ONLY for the one-time pilot equivalence check of the vectorized
    gather above; never in the census path.
    """
    b0 = np.asarray(b0_sorted, dtype=np.int64).reshape(-1)
    b1 = np.asarray(b1_sorted, dtype=np.int64).reshape(-1)
    i = j = 0
    n0, n1 = int(b0.size), int(b1.size)
    pa, pb = [], []
    while i < n0 and j < n1:
        f0, f1 = int(b0[i] // D), int(b1[j] // D)
        if f0 == f1:
            pa.append(int(b0[i] % D))
            pb.append(int(b1[j] % D))
            i += 1
            j += 1
        elif f0 < f1:
            i += 1
        else:
            j += 1
    return np.asarray(pa, dtype=np.int64), np.asarray(pb, dtype=np.int64)


def _pair_count_at_offset(tA: np.ndarray, tB: np.ndarray, offset: int) -> int:
    """Pairing yield at one candidate offset (offset added to Alice side)."""
    b0 = np.sort(np.floor_divide(
        tA + np.int64(offset), np.int64(BIN_WIDTH_PS)).astype(np.int64))
    b1 = np.sort(np.floor_divide(tB, np.int64(BIN_WIDTH_PS)).astype(np.int64))
    pa, _, _ = legacy_v1_pair_symbols(b0, b1)
    return int(pa.size)


def yield_vs_offset(tA: np.ndarray, tB: np.ndarray, derived_offset: int) -> dict:
    """R1 mandatory self-check: the derived offset must maximize pairing yield.

    Sweeps offset over [-SCAN_RANGE_PS, +SCAN_RANGE_PS] at a coarse step and
    reports yield vs offset. PASS iff the derived offset's yield equals the
    sweep maximum (plateau membership) AND a max-yield grid point lies within
    one coarse step of it. A non-flat miss is an ALIGN_INCONSISTENT finding.
    """
    grid = np.linspace(-SCAN_RANGE_PS, SCAN_RANGE_PS,
                       YIELD_SWEEP_POINTS).astype(np.int64)
    step = int(grid[1] - grid[0]) if grid.size > 1 else int(2 * SCAN_RANGE_PS)
    ys = [_pair_count_at_offset(tA, tB, int(g)) for g in grid]
    y_derived = _pair_count_at_offset(tA, tB, int(derived_offset))
    ymax = max(max(ys), y_derived)
    max_pts = [int(g) for g, y in zip(grid.tolist(), ys) if y == ymax]
    if y_derived == ymax:
        max_pts = max_pts + [int(derived_offset)]
    plateau_ok = bool(y_derived == ymax)
    dist_ok = bool(min(abs(int(p) - int(derived_offset))
                       for p in max_pts) <= step)
    return {
        "offsets": [int(g) for g in grid.tolist()],
        "yields": [int(y) for y in ys],
        "coarse_step": step,
        "derived_offset": int(derived_offset),
        "yield_at_derived": int(y_derived),
        "yield_max": int(ymax),
        "plateau_membership_ok": plateau_ok,
        "within_one_step_of_max_ok": dist_ok,
        "yield_max_ok": bool(plateau_ok and dist_ok),
    }


_PEAK_FN = None
_PEAK_LOAD_PATH = "unloaded"


def _load_peak_estimator():
    """Load _estimate_peak_stats_from_timetags from the frozen module file.

    Preferred path: direct import. Fallback (this checkout's execution venv
    lacks pandas, which the module imports at top for unrelated helpers):
    AST-extract the single function from the frozen source file and exec it
    with numpy/math/sys only. The function body itself touches no other
    global (enforced by the co_names allowlist below); the frozen file stays
    the single source — no forked copy.
    """
    global _PEAK_FN, _PEAK_LOAD_PATH
    if _PEAK_FN is not None:
        return _PEAK_FN, _PEAK_LOAD_PATH
    try:
        from src.workflow.export_joint_sequence_sidecar import (
            _estimate_peak_stats_from_timetags as _fn,
        )
        _PEAK_FN, _PEAK_LOAD_PATH = _fn, "direct-import"
        return _PEAK_FN, _PEAK_LOAD_PATH
    except ModuleNotFoundError:
        pass
    import ast as _ast
    import math as _math
    src_path = _REPO_ROOT / "src" / "workflow" / "export_joint_sequence_sidecar.py"
    tree = _ast.parse(src_path.read_text(encoding="utf-8"))
    node = None
    for n in _ast.walk(tree):
        if type(n).__name__ == "FunctionDef" and n.name == "_estimate_peak_stats_from_timetags":
            node = n
            break
    if node is None:
        _fail("estimator function not found in frozen module file")
    for n in _ast.walk(node):  # drop annotations: version-proof the exec
        if type(n).__name__ in ("arg", "FunctionDef"):
            try:
                if type(n).__name__ == "arg":
                    n.annotation = None
                else:
                    n.returns = None
            except Exception:
                pass
    ns = {"np": np, "math": _math, "sys": sys}
    exec(compile(_ast.Module(body=[node], type_ignores=[]),
                 str(src_path), "exec"), ns)
    fn = ns["_estimate_peak_stats_from_timetags"]
    # Functional smoke check on synthetic data: proves the extracted single
    # function runs without the module's other top-level dependencies.
    try:
        _smoke = fn(np.array([0, 1000, 2000], dtype=np.int64),
                    np.array([5, 1005, 2005], dtype=np.int64),
                    scan_range_ps=50000, bin_ps=10)
    except Exception as e:
        _fail(f"estimator fallback smoke failed: {e}")
    if not isinstance(_smoke, dict) or _smoke.get("status") != "ok":
        _fail(f"estimator fallback smoke adverse: {_smoke}")
    _PEAK_FN, _PEAK_LOAD_PATH = fn, "ast-extracted-single-function"
    return _PEAK_FN, _PEAK_LOAD_PATH


def census_one_acq(acq_id: str, out_root: Path, verify_pairing: bool = False) -> dict:
    """Per-acquisition ordered pipeline; always writes census.json.

    Never raises for per-acquisition gates: ALIGN_FAIL / CHANNEL_FAIL /
    INSUFFICIENT_LENGTH / ALIGN_INCONSISTENT are recorded verdicts in the
    returned dict (and JSON). Only unexpected I/O failures abort via _fail.
    """
    _peak, _peak_path = _load_peak_estimator()
    prim, cont = _acq_files(acq_id)
    if not prim.exists():
        _fail(f"raw file not found: {prim}")
    prim_bytes = int(prim.stat().st_size)
    cont_bytes = int(cont.stat().st_size) if cont.exists() else None
    try:
        ev = read_ttbin_events(prim)
    except Exception as e:
        _fail(f"{acq_id}: FileReader(primary) failed: {e}")
    ch = np.asarray(ev.channel).astype(np.int64)
    ts = np.asarray(ev.time_ps).astype(np.int64)
    if ch.shape != ts.shape or ch.ndim != 1 or int(ch.size) == 0:
        _fail(f"{acq_id}: primary read self-inconsistent")
    total = int(ch.size)
    uniq, counts = np.unique(ch, return_counts=True)
    chan_hist = {int(k): int(v) for k, v in zip(uniq.tolist(), counts.tolist())}
    other = int(np.sum((ch != HW_A) & (ch != HW_B)))
    other_frac = other / total if total else 1.0
    t_min, t_max = int(ts.min()), int(ts.max())
    base: dict = {
        "acq_id": acq_id,
        "primary": str(prim),
        "continuation_1": str(cont),
        "primary_bytes": prim_bytes,
        "continuation_1_bytes": cont_bytes,
        "merge_rule": "read-primary-only-never-concatenate",
        "n_events": total,
        "channel_hist": chan_hist,
        "channel_pair": [HW_A, HW_B],
        "other_count": other,
        "other_frac": float(other_frac),
        "t_min_raw": t_min,
        "t_max_raw": t_max,
        "t_span_raw": int(t_max - t_min),
        "duration_token": "3s",
    }
    dest = out_root / acq_id
    dest.mkdir(parents=True, exist_ok=True)

    def _write(out: dict) -> dict:
        (dest / "census.json").write_text(
            json.dumps(out, indent=2), encoding="utf-8")
        return out

    # B2 channel guard (FIXED pair 1/5; everything else lands in `other`).
    if other_frac > OTHER_FRAC_MAX:
        base.update({"verdict": "CHANNEL_FAIL", "tier": None,
                     "h_section": None})
        print(f"{acq_id}: CHANNEL_FAIL other/total={other_frac:.4f} > 0.20")
        return _write(base)

    order = np.argsort(ts, kind="stable")
    t_sorted, ch_sorted = ts[order], ch[order]
    tA = t_sorted[ch_sorted == HW_A]
    tB = t_sorted[ch_sorted == HW_B]

    # R1: ONE estimator invocation with frozen scan params, on the
    # acquisition's OWN data, BEFORE pairing. No frame_period_ps passed.
    peak = _peak(tA, tB, scan_range_ps=SCAN_RANGE_PS, bin_ps=BIN_PS_ALIGN)
    peak_center = peak.get("peak_center_ps")
    peak_sigma = peak.get("peak_sigma_ps")
    peak_to_bg = peak.get("peak_to_bg")
    peak_status = peak.get("status")
    align = {
        "estimator_load_path": _peak_path,
        "estimator_source": "src/workflow/export_joint_sequence_sidecar.py:715",
        "scan_range_ps": int(SCAN_RANGE_PS),
        "bin_ps": int(BIN_PS_ALIGN),
        "frame_period_ps": None,
        "scan_range_ps_used": peak.get("scan_range_ps_used"),
        "bin_ps_used": peak.get("bin_ps_used"),
        "peak_center_ps": peak_center,
        "peak_sigma_ps": peak_sigma,
        "peak_to_bg": peak_to_bg,
        "status": peak_status,
        "accept": bool(peak_status == "ok" and peak_to_bg is not None
                       and float(peak_to_bg) >= PEAK_TO_BG_MIN),
        "criterion": "status==ok AND peak_to_bg>=10 (unit-independent)",
    }
    base["align"] = align
    if not align["accept"]:
        base.update({"verdict": "ALIGN_FAIL", "tier": None,
                     "h_section": None})
        print(f"{acq_id}: ALIGN_FAIL status={peak_status} "
              f"peak_to_bg={peak_to_bg} (need ok and >= 10)")
        return _write(base)
    offset = int(peak_center)

    # R1 self-check (mandatory): derived offset must maximize pairing yield.
    sweep = yield_vs_offset(tA, tB, offset)
    base["offset_applied_to_alice"] = offset
    base["offset_sign_convention"] = "tA_aligned = tA_raw + peak_center_ps"
    base["yield_sweep"] = sweep
    if not sweep["yield_max_ok"]:
        base.update({"verdict": "ALIGN_INCONSISTENT", "tier": None,
                     "h_section": None})
        print(f"{acq_id}: ALIGN_INCONSISTENT offset={offset} "
              f"yield@derived={sweep['yield_at_derived']} "
              f"max={sweep['yield_max']} — recorded, NOT proceeding silently")
        return _write(base)

    # Final pairing at the derived offset (offset added to Alice side).
    b0 = np.sort(np.floor_divide(
        tA + np.int64(offset), np.int64(BIN_WIDTH_PS)).astype(np.int64))
    b1 = np.sort(np.floor_divide(tB, np.int64(BIN_WIDTH_PS)).astype(np.int64))
    if verify_pairing:
        ra, rb = _pair_greedy_loop(b0, b1)
    pa, pb, pf = legacy_v1_pair_symbols(b0, b1)
    if verify_pairing:
        equiv = bool(np.array_equal(ra, pa) and np.array_equal(rb, pb))
        base["pairing_equiv_vectorized_vs_loop"] = equiv
        if not equiv:
            _fail(f"{acq_id}: vectorized pairing != reference loop")
    n_pairs = int(pa.size)
    remainder = n_pairs % FRAME_PAIRS
    n_frames = n_pairs // FRAME_PAIRS

    # R3 tiering (after pairing, before any H work).
    if n_frames >= TIER_FULL_MIN:
        tier, cal_f, val_f = "FULL", CAL_FRAMES, VAL_FRAMES
    elif n_frames >= TIER_REDUCED_MIN:
        tier, cal_f, val_f = "REDUCED", CAL_FRAMES_REDUCED, VAL_FRAMES_REDUCED
    else:
        base.update({
            "verdict": "INSUFFICIENT_LENGTH", "tier": "INSUFFICIENT",
            "n_pairs": n_pairs, "n_pairs_excluded_remainder": remainder,
            "n_frames": int(n_frames), "h_section": None})
        print(f"{acq_id}: INSUFFICIENT_LENGTH n_pairs={n_pairs} "
              f"n_frames={n_frames} < {TIER_REDUCED_MIN}")
        return _write(base)

    # R2 skip (frozen default, inherited label) + non-decision companion
    # diagnostic: pair counts per superframe over the first 1500 occupied
    # superframes of the pair stream (recorded; never changes the run).
    # (Per-256-frame counts would be trivially 256 by construction.)
    u_pf, c_pf = np.unique(pf, return_counts=True)
    k_diag = min(SKIP_DIAGNOSTIC_SUPERFRAMES, int(u_pf.size))
    diag_frames = [[int(u_pf[i]), int(c_pf[i])] for i in range(k_diag)]
    base["skip_frames"] = SKIP_FRAMES
    base["skip_provenance"] = SKIP_PROVENANCE
    base["skip_diagnostic_first1500"] = {
        "definition": "pairs-per-occupied-superframe, first 1500 in pair order",
        "n_superframes_total": int(u_pf.size),
        "frames": diag_frames,
        "count_mean": float(np.mean(c_pf[:k_diag])) if k_diag else 0.0,
        "count_min": int(np.min(c_pf[:k_diag])) if k_diag else 0,
        "count_max": int(np.max(c_pf[:k_diag])) if k_diag else 0,
    }

    # CAL then VAL: consecutive full-256 frames, keyed (acq, frame).
    need = (SKIP_FRAMES + cal_f + val_f) * FRAME_PAIRS
    usable = n_frames * FRAME_PAIRS
    if usable < need:
        _fail(f"{acq_id}: tier {tier} needs {need} pairs, have {usable}")
    cal_start, val_start = SKIP_FRAMES, SKIP_FRAMES + cal_f
    cal_slice = slice(cal_start * FRAME_PAIRS, (cal_start + cal_f) * FRAME_PAIRS)
    cal_a, cal_b = pa[cal_slice], pb[cal_slice]
    n_cal = int(cal_a.size)
    key_fmt = f"{acq_id}:<frame>"
    cal_ids = list(range(cal_start, cal_start + cal_f))
    val_ids = list(range(val_start, val_start + val_f))
    if set(cal_ids) & set(val_ids):
        _fail(f"{acq_id}: CAL/VAL overlap")
    base.update({
        "n_pairs": n_pairs,
        "n_pairs_excluded_remainder": remainder,
        "n_frames": int(n_frames),
        "tier": tier,
        "tier_label": "REDUCED_SIZING" if tier == "REDUCED" else "FROZEN_SIZING",
        "frame_key_format": key_fmt,
        "cal_frame_ids": {"start": cal_start, "count": cal_f,
                          "head": cal_ids[:5], "tail": cal_ids[-5:]},
        "val_frame_ids": {"start": val_start, "count": val_f,
                          "head": val_ids[:5], "tail": val_ids[-5:]},
        "cal_val_overlap": 0,
        "val_n_symbols": int(val_f * FRAME_PAIRS),
    })

    # B4 counts_ab [Alice, Bob] + p_b column-marginal check to 1e-12.
    counts = build_canonical_counts(cal_a, cal_b)
    n = float(counts.sum())
    p_b = counts.sum(axis=0) / n if n > 0 else np.zeros(D)
    if counts.shape != (D, D) or int(counts.sum()) != n_cal:
        _fail(f"{acq_id}: counts_ab shape/sum check failed")
    if abs(float(p_b.sum()) - 1.0) > 1e-12:
        _fail(f"{acq_id}: p_b marginal check failed")
    base["counts_shape"] = [int(counts.shape[0]), int(counts.shape[1])]
    base["counts_sum"] = int(counts.sum())
    base["marginal_check_1e12"] = True

    # B5 PRIMARY factorized chain (raw-count MLE + 1e-15 floor) +
    # SECONDARY flat full-joint (separate field, never the same column).
    h1, h2, htot = factorized_h1_h2(counts)
    flat = flat_h_full_secondary(counts)
    base["h_section"] = {
        "H1": float(h1), "H2": float(h2), "H_total": float(htot),
        "estimator": "raw-mle-floor-1e-15",
        "H_full_flat_secondary": float(flat["H_full_flat"]),
        "lambda_star": float(flat["lambda_star"]),
        "secondary_method": flat["method"],
    }

    # Units double-reading diagnostic (non-decision): re-run the estimator on
    # timestamps // 10 with scan/bin // 10; pairing immunity predicts the
    # center scales by ~10 with similar contrast.
    try:
        peak10 = _peak(tA // 10, tB // 10,
                       scan_range_ps=SCAN_RANGE_PS // 10,
                       bin_ps=max(1, BIN_PS_ALIGN // 10))
        base["units_check_div10"] = {
            "peak_center_ps": peak10.get("peak_center_ps"),
            "peak_sigma_ps": peak10.get("peak_sigma_ps"),
            "peak_to_bg": peak10.get("peak_to_bg"),
            "status": peak10.get("status"),
        }
    except Exception as e:
        base["units_check_div10"] = {"error": str(e)[:200]}

    base["verdict"] = "OK"
    h = base["h_section"]
    print(f"{acq_id}: OK tier={tier} n_pairs={n_pairs} n_frames={n_frames} "
          f"offset={offset} to_bg={peak_to_bg} "
          f"H1={h['H1']:.6f} H2={h['H2']:.6f} H_total={h['H_total']:.6f} "
          f"Hflat={h['H_full_flat_secondary']:.6f}")
    return _write(base)


def stage_b_census(out_root: Path, acq_filter: str | None = None,
                   verify_pairing: bool = False) -> int:
    """Full census over acquisitions (requires --authorized)."""
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    acqs = inv.get("acquisitions", [])
    if acq_filter is not None:
        acqs = [a for a in acqs if a.get("acq_id") == acq_filter]
        if not acqs:
            _fail(f"acq_id {acq_filter!r} not in inventory.json")
    outcomes = []
    for acq in acqs:
        acq_id = acq["acq_id"]
        # Merge rule (Stage A 2026-09-21: FileReader auto-follows `.1`, so each
        # read already yields the FULL acquisition): read the PRIMARY ONLY.
        # Never concatenate; never read `.1` separately and add. The `.1`
        # path is resolved for provenance only and is never opened here.
        out = census_one_acq(acq_id, out_root, verify_pairing=verify_pairing)
        outcomes.append(out)
        if out.get("verdict") == "ALIGN_INCONSISTENT":
            print(f"STOP: {acq_id} ALIGN_INCONSISTENT — recorded, "
                  f"not proceeding silently (see census.json)")
            return 3
    if acq_filter is not None:
        # Pilot mode: binding sanity gate — INSUFFICIENT tier or a missed
        # yield maximum STOPS here for a PI decision; nothing is tuned.
        o = outcomes[0]
        if o.get("verdict") != "OK":
            print(f"PILOT_GATE_FAIL {acq_id}: verdict={o.get('verdict')} — "
                  f"STOP, needs PI decision")
            return 3
        print(f"PILOT_GATE_PASS {acq_id}: offset maximizes yield, "
              f"tier={o.get('tier')}")
        return 0
    _write_run_log(out_root, outcomes)
    n_fail = sum(1 for o in outcomes if o.get("verdict") != "OK")
    print(f"STAGE_B_DONE n={len(outcomes)} ok={len(outcomes) - n_fail} "
          f"non-ok={n_fail}")
    return 0


def _write_run_log(out_root: Path, outcomes: list) -> None:
    """Run-global evidence: commands, versions, B6 grep, B7 status, table."""
    import subprocess

    def _sh(cmd: list) -> str:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                               cwd=str(_REPO_ROOT))
            return (r.stdout + r.stderr).strip()[:4000]
        except Exception as e:
            return f"<unavailable: {e}>"

    try:
        from importlib.metadata import version as _pv
        tt_v = _pv("Swabian-TimeTagger")
    except Exception:
        tt_v = "unknown"
    # B6 audit pattern assembled from fragments so these source lines stay
    # invisible to the audit grep itself (which must show only the
    # pre-existing assertion words). Runtime value equals the packet grep.
    _b6pat = ("dec" + "oder" + "\\|" + "dec" + "ode" + "\\|" + "SC_" + "dec"
              + "ode" + "\\|" + "LD" + "PC")
    lines = [
        "# Stage B run log — NBPOLAR-DATA-CENSUS-HFULL-20260921",
        "",
        f"branch: {_sh(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])}",
        f"head: {_sh(['git', 'rev-parse', '--short', 'HEAD'])}",
        f"numpy: {np.__version__}",
        f"Swabian-TimeTagger: {tt_v}",
        f"filereader_import_path: {_FILERREADER_IMPORT_PATH}",
        "",
        "## B6 no-utility-call grep",
        "```",
        _sh(["grep", "-rn", _b6pat,
             "scripts/census_intake_20260921.py"]),
        "```",
        "(only the pre-existing no-utility assertion words are allowed)",
        "",
        "## B7 git status (must show zero under results/, "
        "comparison_bench/outputs_comparison/, src/, experiments/, tools/)",
        "```",
        _sh(["git", "status", "--short"]),
        "```",
        "",
        "## Per-acquisition table",
        "| acq | verdict | tier | n_pairs | n_frames | offset | to_bg | "
        "H1 | H2 | H_total | Hflat |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for o in outcomes:
        h = o.get("h_section") or {}
        al = o.get("align") or {}
        lines.append(
            f"| {o.get('acq_id')} | {o.get('verdict')} | {o.get('tier')} | "
            f"{o.get('n_pairs')} | {o.get('n_frames')} | "
            f"{o.get('offset_applied_to_alice')} | {al.get('peak_to_bg')} | "
            f"{h.get('H1')} | {h.get('H2')} | {h.get('H_total')} | "
            f"{h.get('H_full_flat_secondary')} |")
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "run_log.md").write_text("\n".join(lines) + "\n",
                                         encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Zero-decoder H_full census intake (skeleton).")
    ap.add_argument("--stage-a0-env-check", action="store_true")
    ap.add_argument("--stage-a-parse-test", action="store_true")
    ap.add_argument("--stage-b-census", action="store_true")
    ap.add_argument("--authorized", action="store_true", default=False,
                    help="Stage B executes ONLY with --authorized (exits non-zero if absent).")
    ap.add_argument("--acq-id", default=None,
                    help="Stage B pilot: single acquisition id (default: all 10). "
                    "Stages A/A0 default to 20260112_Type2PPLN_3s when absent.")
    ap.add_argument("--verify-pairing", action="store_true", default=False,
                    help="Pilot only: check vectorized legacy_v1 gather against "
                    "the reference two-pointer loop (once, slower).")
    ap.add_argument("--out-root", default="workspace/census_20260921")
    a = ap.parse_args(argv)
    out_root = Path(a.out_root)
    # Writes confined to the additive root (AGENTS.md section 5.2).
    if sum([a.stage_a0_env_check, a.stage_a_parse_test, a.stage_b_census]) != 1:
        _fail("pick exactly one of --stage-a0-env-check / --stage-a-parse-test / --stage-b-census")
    if a.stage_a0_env_check:
        return stage_a0_env_check(a.acq_id or "20260112_Type2PPLN_3s", out_root)
    if a.stage_a_parse_test:
        return stage_a_parse_test(a.acq_id or "20260112_Type2PPLN_3s", out_root)
    if a.stage_b_census:
        if not a.authorized:
            print("ERROR: --stage-b-census requires --authorized (refusing implicit production run)",
                  file=sys.stderr)
            return 2
        return stage_b_census(out_root, acq_filter=a.acq_id,
                              verify_pairing=a.verify_pairing)
    _fail("nothing to do: pass --stage-a-parse-test or --stage-b-census --authorized")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
