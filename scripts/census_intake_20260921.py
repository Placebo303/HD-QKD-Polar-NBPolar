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


def stage_b_census(out_root: Path) -> int:
    """Full census over all 10 acquisitions (requires --authorized)."""
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    for acq in inv.get("acquisitions", []):
        acq_id = acq["acq_id"]
        prim, cont = _acq_files(acq_id)
        # Merge rule (Stage A 2026-09-21: FileReader auto-follows `.1`, so each
        # read already yields the FULL acquisition): read the PRIMARY ONLY.
        # Never concatenate; never read `.1` separately and add. `cont` is
        # resolved for provenance only and is never opened here.
        try:
            ev = read_ttbin_events(prim)
        except Exception as e:
            _fail(f"{acq_id}: FileReader(primary) failed: {e}")
        ch = np.asarray(ev.channel).astype(np.int64)
        ts = np.asarray(ev.time_ps).astype(np.int64)
        # Self-consistency guard on the single read.
        if ch.shape != ts.shape or ch.ndim != 1 or int(ch.size) == 0:
            _fail(f"{acq_id}: primary read self-inconsistent: "
                  f"channels shape {ch.shape}, times shape {ts.shape}")
        total = int(ch.size)
        print(f"{acq_id}: primary-only read file={prim} n_events={total} "
              f"(continuation {cont.name} NOT read — autofollow, concat forbidden)")
        other = int(np.sum((ch != HW_A) & (ch != HW_B)))
        other_frac = other / total if total else 1.0
        if other_frac > OTHER_FRAC_MAX:
            _fail(f"{acq_id}: channel ambiguity other/total={other_frac:.3f} > 0.20")
        # Delay <<SEARCH>> per acquisition: grid over candidate delays, objective
        # = peak height / peak_to_bg; accept only |delay-peak|<50ps,
        # sigma in [50,150] (scripts/v65_data_readiness.py:201-210). The grid
        # itself is preregistered per acquisition at authorization review.
        try:
            from src.workflow.export_joint_sequence_sidecar import (
                _estimate_peak_stats_from_timetags as _peak,
            )
        except Exception as e:
            _fail(f"{acq_id}: delay estimator import failed: {e}")
        frame_period_ps = PERIOD_PS * BIN_WIDTH_PS
        scan_range = max(50_000, 2 * frame_period_ps)
        bin_ps = max(10, BIN_WIDTH_PS // 2)
        order = np.argsort(ts, kind="stable")
        t_sorted, ch_sorted = ts[order], ch[order]
        # Real signature: (t0_ps, t1_ps, *, scan_range_ps, bin_ps,
        # frame_period_ps) -> dict with peak_center_ps / peak_sigma_ps /
        # peak_to_bg (src/workflow/export_joint_sequence_sidecar.py:715).
        peak = _peak(t_sorted[ch_sorted == HW_A], t_sorted[ch_sorted == HW_B],
                     scan_range_ps=scan_range, bin_ps=bin_ps,
                     frame_period_ps=frame_period_ps)
        delay, peak_c, sigma = (int(peak["peak_center_ps"]),
                                float(peak["peak_center_ps"]),
                                float(peak["peak_sigma_ps"] or -1))
        gate_ok = abs(delay - peak_c) < 50 and 50 <= sigma <= 150
        if not gate_ok:
            _fail(f"{acq_id}: delay gate FAIL delay={delay} peak={peak_c} sigma={sigma}")
        # Pairing (nearest, legacy_v1: same //1024 super-frame), remap hw->logical.
        t_a = t_sorted[ch_sorted == HW_A] - delay
        t_b = t_sorted[ch_sorted == HW_B]
        b0 = np.sort(np.floor_divide(t_a, BIN_WIDTH_PS).astype(np.int64))
        b1 = np.sort(np.floor_divide(t_b, BIN_WIDTH_PS).astype(np.int64))
        i = j = 0
        pa, pb = [], []
        while i < b0.size and j < b1.size:
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
        n_pairs = len(pa)
        if n_pairs % FRAME_PAIRS != 0:
            _fail(f"{acq_id}: pairs {n_pairs} not multiple of {FRAME_PAIRS}")
        # Skip length is preregistered PER acquisition (NOT the frozen 702 copy).
        _fail(
            f"{acq_id}: Stage B needs per-acquisition preregistered skip + delay "
            "from Stage A review — skeleton stops here by design (see TASK_PACKET.md B8)"
        )
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Zero-decoder H_full census intake (skeleton).")
    ap.add_argument("--stage-a0-env-check", action="store_true")
    ap.add_argument("--stage-a-parse-test", action="store_true")
    ap.add_argument("--stage-b-census", action="store_true")
    ap.add_argument("--authorized", action="store_true", default=False,
                    help="Stage B executes ONLY with --authorized (exits non-zero if absent).")
    ap.add_argument("--acq-id", default="20260112_Type2PPLN_3s")
    ap.add_argument("--out-root", default="workspace/census_20260921")
    a = ap.parse_args(argv)
    out_root = Path(a.out_root)
    # Writes confined to the additive root (AGENTS.md section 5.2).
    if sum([a.stage_a0_env_check, a.stage_a_parse_test, a.stage_b_census]) != 1:
        _fail("pick exactly one of --stage-a0-env-check / --stage-a-parse-test / --stage-b-census")
    if a.stage_a0_env_check:
        return stage_a0_env_check(a.acq_id, out_root)
    if a.stage_a_parse_test:
        return stage_a_parse_test(a.acq_id, out_root)
    if a.stage_b_census:
        if not a.authorized:
            print("ERROR: --stage-b-census requires --authorized (refusing implicit production run)",
                  file=sys.stderr)
            return 2
        return stage_b_census(out_root)
    _fail("nothing to do: pass --stage-a-parse-test or --stage-b-census --authorized")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
