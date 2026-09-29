#!/usr/bin/env python3
"""R2C strongest binary arm: conditional hard-prefix MSD + SCL(L=16, no CRC), genie-SC MC construction, per-layer mu_i,
on the 64-block SHG `_1`/`_2` pool.  Tier-Y one-shot decision gate (contract:
docs/nbpolar/R2C_STRONG_BINARY_MSD_CONTRACT_20260929.md).

**NOT AUTHORIZED.**  This file is a preparation-only artifact.  A real run needs (i) T0-T2 pass,
(ii) independent Pre-EXECUTE PASS, (iii) PI verbatim authorization (AUTHORIZATION_PROMPT.md) and
the ``--authorize`` flag.  ``--dry-run`` uses SYNTHETIC data only and writes under ``dry_run/``.

All algorithmic content lives in
``comparison_bench/src/comparison_bench/formal_ir/nbpolar/r2c_msd_binary.py`` (frozen constants
are named there).  This driver only: loads the lab read-only into ``_stage/`` (L-1), rebuilds the
two SHG sessions with the SAME frozen R2 code path (``workspace/r2_fer_shg_64/run.py``,
imported by file path, unmodified), takes H_total / F2 targets from ``r2_fer_shg_64/results.json``,
runs the pipeline, and checks the lab tree is unchanged.

Outputs (additive; refuses to run if any exist): ``results.json``, ``part_<S>_<idx>.json`` (64),
``construction_frozen_<S>.json`` (2), ``lab_readonly_check.json``.  ``_stage/`` holds the compiled
engine and the numba cache (not evidence; gitignored).
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

STAGE = THIS_DIR / "_stage"
LAB_ROOT = Path("/mnt/d/Code/qkd-reconciliation-lab")
LAB_SRC = str(LAB_ROOT / "src")
NB_DIR = REPO_ROOT / "workspace" / "r2_fer_shg_64"
MOD_PATH = REPO_ROOT / "comparison_bench" / "src" / "comparison_bench" / "formal_ir" / "nbpolar" / "r2c_msd_binary.py"
RESULTS_PATH = THIS_DIR / "results.json"
POINT_ID = "r2c-strong-binary-msd-shg64"
SESSIONS = ("G2", "G3")


def _fail(msg: str, code: int = 2):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_r2c():
    spec = importlib.util.spec_from_file_location("r2c_msd_binary", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["r2c_msd_binary"] = mod
    spec.loader.exec_module(mod)
    return mod


def load_nb_packet_module():
    """workspace/r2_fer_shg_64/run.py BY FILE PATH (read-only; module level defines only constants/functions)."""
    path = NB_DIR / "run.py"
    spec = importlib.util.spec_from_file_location("_r2_fer_shg_64_run_readonly", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_tag_fn():
    """Whole-block 64-bit Toeplitz tag, R2B convention (src.reconciliation.verification.universal_hash_tag,
    layer_id=0, block_index=global_block_index, message = MSB-first 10-bit serialisation of the 32768 symbols)."""
    verif = importlib.import_module("src.reconciliation.verification")

    def tag_fn(bits, block_index):
        return verif.universal_hash_tag(bits=bits, point_id=POINT_ID, layer_id=0, block_index=int(block_index), tag_bits=64)

    return tag_fn


def load_real_sessions(m, nb_mod, mod, chain, scl_joint_mod, r2_results: dict) -> list:
    """REAL DATA (only under --authorize): rebuild both sessions through the frozen R2 code path."""
    sessions = []
    for idx, name in enumerate(SESSIONS):
        blocks = nb_mod.build_session_blocks(mod, name)
        ctx = nb_mod._reproduce_session_context(mod, chain, scl_joint_mod, name)
        cal_ids = mod.g2_cal_ids(nb_mod.ARM)
        cal_a = ctx["frames_a"][cal_ids].ravel()
        cal_b = ctx["frames_b"][cal_ids].ravel()
        per = r2_results["per_session"][name]
        h_total = float(per["h_total_bits"])
        f_nb = float(per["f_book_with_crc_computed"])
        if abs(h_total - float(ctx["h_total_bits"])) > 1e-9 or abs(f_nb - float(ctx["f_book_with_crc"])) > 1e-9:
            raise RuntimeError(f"{name}: reproduced H_total/f_book differ from r2_fer_shg_64/results.json")
        n_tag = int(chain.tag_bits)
        if n_tag != m.TAG_BITS:
            raise RuntimeError(f"NB tag_bits={n_tag} != frozen {m.TAG_BITS}")
        for b in blocks:  # block metadata is exactly R2's (frame ranges, strata, global index)
            b["n_symbols"] = (b["frame_end"] - b["frame_start"] + 1) * ctx["frames_a"].shape[1]
            if b["n_symbols"] != 32768:
                raise RuntimeError(f"{name} block {b['global_block_index']}: {b['n_symbols']} symbols != 32768")
        sessions.append(m.SessionInput(name=name, idx=idx, cal_a=cal_a, cal_b=cal_b, h_total_bits=h_total, f_nb=f_nb,
                                       frames_a=ctx["frames_a"], frames_b=ctx["frames_b"], blocks=blocks, fit_joint=ctx["fit"]["joint"]))
    return sessions


def synthetic_sessions(m, d: int, n_log: int, n_blocks: int) -> list:
    """SYNTHETIC circulant sessions for --dry-run (no data access)."""
    import numpy as np

    n = 1 << n_log
    fp = n // 128
    out = []
    for idx, name in enumerate(SESSIONS):
        rng = np.random.default_rng(20260929 + idx)
        pmf = np.full(d, 1e-4)
        pmf[0] = 0.78
        for s, v in ((1, 0.08), (2, 0.02), (3, 0.005)):
            pmf[s % d] = v
            pmf[(-s) % d] = v
        pmf /= pmf.sum()
        cdf = np.cumsum(pmf)
        cdf[-1] = 1.0

        def draw(size):
            a = rng.integers(0, d, size=size)
            dl = np.minimum(np.searchsorted(cdf, rng.random(size)), d - 1)
            return a, (a + dl) % d

        cal_a, cal_b = draw(8192)
        fa, fb = draw((128 * n_blocks, fp))
        so = ("A1_CAL_characterization", "HELDOUT_model_selection", "EVAL_already_decoded")
        st = ("never_decoded", "heldout_model_selection", "previously_decoded_eval")
        blocks = [{"session": name, "local_index": i, "global_block_index": idx * 32 + i, "frame_start": i * 128, "frame_end": i * 128 + 127,
                   "stratum_official": so[i % 3], "stratum_task": st[i % 3]} for i in range(n_blocks)]
        h = float(-(pmf * np.log2(pmf)).sum())
        out.append(m.SessionInput(name=name, idx=idx, cal_a=cal_a, cal_b=cal_b, h_total_bits=h, f_nb=1.3, frames_a=fa, frames_b=fb, blocks=blocks))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="R2C strong binary MSD arm (see module docstring)")
    ap.add_argument("--authorize", action="store_true", help="REQUIRED for the real-data run")
    ap.add_argument("--dry-run", action="store_true", help="SYNTHETIC end-to-end (small d/N), writes under dry_run/")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--de-workers", type=int, default=3)
    args = ap.parse_args(argv)
    t_start = time.time()

    m = load_r2c()
    if args.dry_run:
        out_dir = THIS_DIR / "dry_run"
        lab = m.load_lab(STAGE, LAB_SRC)
        cfg = m.RunConfig(n_log=10, d=64, list_size=8, m_design=32, genie_frames=64, genie_chunk=32, f3_target_fer=0.3, mu_steps=4,
                          n_workers=args.workers, de_workers=min(args.de_workers, 2), wall_total_s=1800.0)
        res = m.run_pipeline(lab, cfg, synthetic_sessions(m, 64, 10, 3), out_dir, make_tag_fn(), t_start=t_start)
        print("[dry-run] done (synthetic)", json.dumps(res.get("block_accounting", res)), file=sys.stderr)
        return 0

    if not args.authorize:
        _fail("refusing to run without --authorize (preparation-only artifact; see STATUS.yaml / AUTHORIZATION_PROMPT.md)")
    if RESULTS_PATH.exists() or list(THIS_DIR.glob("part_*.json")) or list(THIS_DIR.glob("construction_frozen_*.json")):
        _fail("refusing to run: results.json / part_*.json / construction_frozen_*.json already exist (additive-only, one-shot)")

    snap_before = m.lab_snapshot(LAB_ROOT)
    lab = m.load_lab(STAGE, LAB_SRC)
    prov = m.lab_used_files_provenance(LAB_ROOT)
    r2_results = json.loads((NB_DIR / "results.json").read_text(encoding="utf-8"))

    nb_mod = load_nb_packet_module()
    mod = nb_mod._load_mod()
    chain, scl_joint_mod = nb_mod._load_scl_joint(mod)
    sessions = load_real_sessions(m, nb_mod, mod, chain, scl_joint_mod, r2_results)
    for s in sessions:
        print(f"[setup] {s.name}: H_total={s.h_total_bits:.6f} F2(NB f_book_with_crc)={s.f_nb:.6f} blocks={len(s.blocks)} "
              f"CAL symbols={s.cal_a.size}", file=sys.stderr)
    cfg = m.RunConfig(n_workers=args.workers, de_workers=args.de_workers)
    res = m.run_pipeline(lab, cfg, sessions, THIS_DIR, make_tag_fn(), nb_dir=NB_DIR, t_start=t_start)
    if res.get("status") == "STOP_model_incompatible":
        print("[STOP] invariance gate failed (D2): construction_frozen_*.json written; NO parts/results. Return to PI.", file=sys.stderr)
        return 3

    snap_after = m.lab_snapshot(LAB_ROOT)
    check = {"lab_unchanged": bool(m.snapshots_equal(snap_before, snap_after)), "git_status_before": snap_before["git_status_porcelain"],
             "git_status_after": snap_after["git_status_porcelain"], "n_src_files_before": len(snap_before["src_files"]),
             "n_src_files_after": len(snap_after["src_files"]), "used_files": prov, "engine_lib": str(lab.lib)}
    (THIS_DIR / "lab_readonly_check.json").write_text(json.dumps(check, indent=2, sort_keys=True), encoding="utf-8")
    res["lab_readonly_check"] = check
    res["authorization"] = {"source": "AUTHORIZATION_PROMPT.md (verbatim PI text recorded by the main thread)"}
    m.dump_json(RESULTS_PATH, res)
    print(f"DONE lab_unchanged={check['lab_unchanged']} stop_undetected={res['stop_undetected']} "
          f"accounting_consistent={res['block_accounting']['consistent']} wall_s={time.time() - t_start:.1f}", file=sys.stderr)
    return 0 if check["lab_unchanged"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
