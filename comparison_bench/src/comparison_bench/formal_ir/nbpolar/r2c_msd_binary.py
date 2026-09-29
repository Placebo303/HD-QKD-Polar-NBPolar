"""R2C strongest-binary arm: conditional hard-prefix MSD + SCL (no CRC), genie-SC Monte Carlo construction.

PI amendment 2026-09-29: E1 = genie-SC MC construction (replaces sampled DE, which is kept below but not
used on the run path); E2 = per-layer mu_i from the design set (replaces the global margin).

Library for ``workspace/r2c_strong_binary_msd_shg_64/`` (contract
``docs/nbpolar/R2C_STRONG_BINARY_MSD_CONTRACT_20260929.md``).  Operator-level
implementation only: every frozen parameter is a named constant below and is
copied from the contract; nothing here decides science.

Design constraints (contract sections in brackets)
--------------------------------------------------
* The lab (``qkd-reconciliation-lab``) is read-only [L-1]: ``load_lab`` sets
  ``PYTHONDONTWRITEBYTECODE`` / ``NUMBA_CACHE_DIR`` to a stage directory, copies
  ``msd_scl.cpp`` into the stage, and redirects ``scl_fast.CPP_DIR/CPP_SOURCE``.
* Construction (pmf choice, caps, DE orders, mu, f grid, k_i) uses ONLY the
  session CAL32 symbols + NB-side scalars.  ``freeze_construction`` takes no
  test-block argument by design (test T2-b).
* Frozen bits carry Alice's true ``u`` values (SW form); info positions are
  zeroed before being passed to the engine so they cannot leak.
* No real-data access happens in this module: callers pass arrays.
"""

from __future__ import annotations

import hashlib
import json
import math
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import numpy as np

# --------------------------------------------------------------------------- #
# Frozen constants (contract sections in comments)
# --------------------------------------------------------------------------- #
DEFAULT_LAB_SRC = "/mnt/d/Code/qkd-reconciliation-lab/src"
D_SYMBOL = 1024  # 10 bit planes, layer 0 = MSB
N_LOG = 15  # 4: N = 32768 per layer
LIST_SIZE = 16  # 6: main L
CLIP = 30.0  # 3.5: lab default LLR clip
MIN_K = 16  # 5: lab min_k
M_ROOT = 4096  # 4: DE root samples
DE_SAMPLES = 1024  # 4: DE population m
DE_SEED = 20260929  # 4: DE seed
M_DESIGN = 1024  # 5 (E2): design frames / layer / evaluation point (main-thread implementation choice: resolves 0.03/10)
GENIE_FRAMES = 4096  # E1: genie-SC frames per layer
GENIE_CHUNK = 256
F1_TARGET = 1.20  # 5: F1
F3_TARGET_FER = 0.03  # 5: F3 smoothed-sum threshold
F4_OFFSET = 0.10  # 5: F4 = F3 + 0.10
TAG_BITS = 64  # 6/7
CV_FOLDS = 8  # 3.4
CV_TIE_NAT = 0.005  # 3.4
NULL_GROUPS = 20  # 3.1
R_MAX = 1.25  # 3.1 / 3.2
PMF_ALPHA_HIST = 1.0  # 3.5
M2_FLOOR = 1e-15  # prior_m2 frozen floor
SLACK_MIN_CODEWORD_WALL_S = 2.0

# Operator-chosen (NOT specified by the contract; flagged in TASK_PACKET.md):
MU_HI_MAX = 0.30  # E2: per-layer bisection upper bracket min(cap_i, MU_HI_MAX) [bits/symbol]
MU_STEPS = 7  # E2: bisection steps per layer (resolution MU_HI_MAX/2^7 ~ 0.0023 bit)
DESIGN_SEED_BASE = 20260929  # design-set RNG base (per session/layer)
ROOT_SEED_BASE = 20260929  # DE root-sampling RNG base (per session/layer)
NULL_SEED_BASE = 20260929  # residual-null RNG base
GENIE_SEED_BASE = 20260929 + 7_000_000  # E1 genie-SC construction RNG base (per session/layer): distinct from design/null
POINT_LABELS = ("F1", "F2", "F3", "F4")

WALL_TOTAL_S = 6.0 * 3600.0  # 10 / D7
RSS_GIB = 6.0  # 10 / D7
USED_LAB_FILES = (
    "src/qkd_recon/msd_conditional.py",
    "src/qkd_recon/scl_fast.py",
    "src/qkd_recon/polar_core.py",
    "src/qkd_recon/de_frozen.py",
    "src/qkd_recon/scl_cpp/msd_scl.cpp",
)


# --------------------------------------------------------------------------- #
# Lab loading (L-1) and read-only snapshots
# --------------------------------------------------------------------------- #
def load_lab(stage_dir: str | Path, lab_src: str = DEFAULT_LAB_SRC, *, build: bool = True) -> SimpleNamespace:
    """Import the lab modules with all writes redirected to ``stage_dir``."""
    stage = Path(stage_dir).resolve()
    (stage / "numba_cache").mkdir(parents=True, exist_ok=True)
    (stage / "scl_cpp").mkdir(parents=True, exist_ok=True)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    want_cache = str(stage / "numba_cache")
    if "numba" in sys.modules:
        import numba  # already imported: NUMBA_CACHE_DIR must already match

        if str(getattr(numba.config, "CACHE_DIR", "")) != want_cache:
            raise RuntimeError(
                "numba was imported before NUMBA_CACHE_DIR was set to the stage dir; "
                "start a fresh interpreter (lab __pycache__/numba cache must not be written)"
            )
    os.environ["NUMBA_CACHE_DIR"] = want_cache
    if lab_src not in sys.path:
        sys.path.insert(0, lab_src)
    import importlib

    msd = importlib.import_module("qkd_recon.msd_conditional")
    polar = importlib.import_module("qkd_recon.polar_core")
    de = importlib.import_module("qkd_recon.de_frozen")
    scl = importlib.import_module("qkd_recon.scl_fast")
    import numba  # noqa: F811

    if str(numba.config.CACHE_DIR) != want_cache:
        raise RuntimeError(f"numba cache dir {numba.config.CACHE_DIR!r} != stage {want_cache!r}")
    cpp_src = Path(lab_src) / "qkd_recon" / "scl_cpp" / "msd_scl.cpp"
    cpp_dst = stage / "scl_cpp" / "msd_scl.cpp"
    if not cpp_dst.exists() or cpp_dst.read_bytes() != cpp_src.read_bytes():
        shutil.copyfile(cpp_src, cpp_dst)
    scl.CPP_DIR = stage / "scl_cpp"
    scl.CPP_SOURCE = cpp_dst
    lib = scl.build_library() if build else None
    if lib is not None and stage not in Path(lib).resolve().parents:
        raise RuntimeError(f"engine library {lib} is not under the stage dir {stage}")
    return SimpleNamespace(msd=msd, polar=polar, de=de, scl=scl, stage=stage, lib=lib, lab_src=lab_src)


def lab_snapshot(lab_root: str | Path) -> dict:
    """(git status --porcelain, src file (path,size,mtime_ns) list); read-only, no index refresh."""
    root = Path(lab_root)
    st = subprocess.run(
        ["git", "--no-optional-locks", "-c", f"safe.directory={root}", "-C", str(root), "status", "--porcelain"],
        capture_output=True, text=True,
    )
    files = []
    for p in sorted((root / "src").rglob("*")):
        if p.is_file():
            s = p.stat()
            files.append([str(p.relative_to(root)).replace("\\", "/"), int(s.st_size), int(s.st_mtime_ns)])
    return {"git_status_rc": st.returncode, "git_status_porcelain": st.stdout.splitlines(), "git_status_stderr": st.stderr.strip(), "src_files": files}


def lab_used_files_provenance(lab_root: str | Path) -> list[dict]:
    root = Path(lab_root)
    out = []
    for rel in USED_LAB_FILES:
        p = root / rel
        dq = subprocess.run(
            ["git", "--no-optional-locks", "-c", f"safe.directory={root}", "-C", str(root), "diff", "--quiet", "--", rel],
            capture_output=True,
        ).returncode
        out.append({"file": rel, "git_diff_quiet": dq == 0, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    return out


def snapshots_equal(before: dict, after: dict) -> bool:
    return before["git_status_porcelain"] == after["git_status_porcelain"] and before["src_files"] == after["src_files"]


# --------------------------------------------------------------------------- #
# Bit planes / encoding helpers
# --------------------------------------------------------------------------- #
def layers_of(d: int) -> int:
    n = int(round(math.log2(d)))
    if 2**n != d:
        raise ValueError("d must be a power of two")
    return n


def plane_bits(sym: np.ndarray, layer: int, layers: int) -> np.ndarray:
    """Bit plane ``layer`` (0 = MSB) of natural-binary symbols; int8."""
    return ((np.asarray(sym, dtype=np.int64) >> (layers - 1 - int(layer))) & 1).astype(np.int8)


def symbols_to_bits(sym: np.ndarray, layers: int) -> np.ndarray:
    """MSB-first bit serialisation (n_symbols * layers) -- same convention as R2B."""
    return np.stack([plane_bits(sym, i, layers) for i in range(layers)], axis=1).reshape(-1)


def bits_to_symbols(bit_planes: list[np.ndarray]) -> np.ndarray:
    out = np.zeros(np.asarray(bit_planes[0]).shape[0], dtype=np.int64)
    for b in bit_planes:
        out = (out << 1) | (np.asarray(b, dtype=np.int64) & 1)
    return out


# --------------------------------------------------------------------------- #
# Difference-domain pmf sources and CAL-only selection (contract 3)
# --------------------------------------------------------------------------- #
def delta_counts(a: np.ndarray, b: np.ndarray, d: int) -> np.ndarray:
    """Counts of ``delta = (b - a) mod d`` (float64)."""
    dl = (np.asarray(b, dtype=np.int64) - np.asarray(a, dtype=np.int64)) % int(d)
    return np.bincount(dl, minlength=int(d)).astype(np.float64)[: int(d)]


def joint_from_symbols(a: np.ndarray, b: np.ndarray, d: int) -> np.ndarray:
    idx = np.asarray(a, dtype=np.int64) * int(d) + np.asarray(b, dtype=np.int64)
    return np.bincount(idx, minlength=int(d) * int(d)).reshape(int(d), int(d))


def m2_pmf(dcounts: np.ndarray, d: int, floor: float = M2_FLOOR) -> np.ndarray:
    """P-M2: CIRCULAR +/-1 triple (prior_m2.fit_m2_triple/build_m2_joint) projected to a 1-D pmf.

    ``prior_m2`` maps ``a = b+1 -> q_plus1`` i.e. delta = d-1, and ``a = b-1 -> q_minus1`` i.e.
    delta = 1.  Every column of the built joint is identical up to a circular shift, so the
    difference pmf is ``max(base, floor) / sum``.
    """
    dcounts = np.asarray(dcounts, dtype=np.float64)
    n = float(dcounts.sum())
    v = np.full(int(d), float(floor))
    v[0] = max(dcounts[0] / n, floor)
    v[d - 1] = max(dcounts[d - 1] / n, floor)
    v[1] = max(dcounts[1] / n, floor)
    return v / v.sum()


def hist_pmf(lab, dcounts: np.ndarray, d: int, alpha: float = PMF_ALPHA_HIST) -> np.ndarray:
    return lab.msd.smooth_difference_counts(dcounts, int(d), float(alpha))


def cv_select_pmf(lab, cal_a: np.ndarray, cal_b: np.ndarray, d: int, *, folds: int = CV_FOLDS) -> dict:
    """8-fold (contiguous) CV log-likelihood per symbol of P-M2 vs P-HIST; CAL32 only."""
    a = np.asarray(cal_a, dtype=np.int64)
    b = np.asarray(cal_b, dtype=np.int64)
    fold = a.size // folds
    if fold <= 0:
        raise ValueError("CAL too small for CV")
    dcs = [delta_counts(a[i * fold:(i + 1) * fold], b[i * fold:(i + 1) * fold], d) for i in range(folds)]
    tot = np.sum(dcs, axis=0)
    ll_m2 = ll_hist = 0.0
    for k in range(folds):
        train = tot - dcs[k]
        ll_m2 += float(np.sum(dcs[k] * np.log(m2_pmf(train, d))))
        ll_hist += float(np.sum(dcs[k] * np.log(hist_pmf(lab, train, d))))
    n_used = float(fold * folds)
    s_m2, s_h = ll_m2 / n_used, ll_hist / n_used
    diff = s_h - s_m2
    source = "P-HIST" if diff >= CV_TIE_NAT else "P-M2"  # tie (< 0.005 nat/sym) -> P-M2
    return {"cv_ll_per_symbol_pm2": s_m2, "cv_ll_per_symbol_phist": s_h, "hist_minus_m2": diff, "source": source,
            "n_used": int(n_used), "folds": int(folds), "tie_threshold_nat": CV_TIE_NAT}


def build_channel(lab, source: str, dcounts: np.ndarray, d: int, *, pmf_m2_override: np.ndarray | None = None) -> dict:
    """Effective pmf + LLR tables for the selected source (CAL32-derived only)."""
    n = float(np.sum(dcounts))
    if source == "P-M2":
        pmf = np.asarray(pmf_m2_override, dtype=np.float64) if pmf_m2_override is not None else m2_pmf(dcounts, d)
        like = lab.msd.shift_invariant_joint(pmf, d, scale=1.0)
        tables, _ = lab.msd.build_msd_llr_tables_shift(like, d, smoothing=0.0, clip=CLIP, smoothing_mode="diff_pmf")
    elif source == "P-HIST":
        pmf = hist_pmf(lab, dcounts, d)
        like = lab.msd.shift_invariant_joint(dcounts / n, d, scale=n)  # smoothing (alpha=1) acts on counts scale n
        tables, _ = lab.msd.build_msd_llr_tables_shift(like, d, smoothing=PMF_ALPHA_HIST, clip=CLIP, smoothing_mode="diff_pmf")
    else:
        raise ValueError(source)
    caps = lab.msd.conditional_capacities(lab.msd.shift_invariant_joint(pmf, d, scale=1.0), d)
    return {"pmf": pmf, "tables": tables, "caps": np.asarray(caps["conditional_mi_bits"], dtype=np.float64),
            "sum_caps": float(caps["sum_conditional"]), "joint_mi_bits": float(caps["joint_mi_bits"]),
            "pmf_entropy_bits": float(-np.sum(pmf * np.log2(pmf)))}


def invariance_check(lab, cal_a: np.ndarray, cal_b: np.ndarray, d: int, *, seed: int, groups: int = NULL_GROUPS) -> dict:
    """R = r_real / r_null for the circulant residual and for the marginal-uniformity L1 (3.1/3.2)."""
    a = np.asarray(cal_a, dtype=np.int64)
    b = np.asarray(cal_b, dtype=np.int64)
    n = a.size
    counts = joint_from_symbols(a, b, d)
    real = lab.msd.shift_model_residual(counts, d)
    pmf = lab.msd.difference_pmf(counts, d)
    cdf = np.cumsum(pmf)
    cdf[-1] = 1.0
    rng = np.random.default_rng(int(seed))
    res_null, marg_null = [], []
    for _ in range(groups):
        an = rng.integers(0, d, size=n)
        dl = np.minimum(np.searchsorted(cdf, rng.random(n)), d - 1)
        bn = (an + dl) % d
        r = lab.msd.shift_model_residual(joint_from_symbols(an, bn, d), d)
        res_null.append(r["resid_mean"])
        marg_null.append(r["marginal_uniformity_l1"])
    rn, mn = float(np.mean(res_null)), float(np.mean(marg_null))
    R_res = real["resid_mean"] / rn
    R_marg = real["marginal_uniformity_l1"] / mn
    return {"resid_mean_real": real["resid_mean"], "resid_mean_null": rn, "R_resid": R_res,
            "marginal_l1_real": real["marginal_uniformity_l1"], "marginal_l1_null": mn, "R_marginal": R_marg,
            "compatible": bool(R_res <= R_MAX and R_marg <= R_MAX), "R_max": R_MAX, "null_groups": int(groups), "null_seed": int(seed)}


# --------------------------------------------------------------------------- #
# DE construction (contract 4)
# --------------------------------------------------------------------------- #
def de_root_llr(tables, pmf: np.ndarray, layer: int, d: int, layers: int, *, m_root: int, seed: int) -> np.ndarray:
    """Symbol-aligned conditional LLR samples ``L * (1 - 2 a_i)`` (all-zero-codeword convention)."""
    rng = np.random.default_rng(int(seed))
    a = rng.integers(0, d, size=int(m_root))
    cdf = np.cumsum(pmf)
    cdf[-1] = 1.0
    dl = np.minimum(np.searchsorted(cdf, rng.random(int(m_root))), d - 1)
    b = (a + dl) % d
    pref = a >> (layers - int(layer))
    llr = tables.llr[int(layer)][pref, b]
    ai = (a >> (layers - 1 - int(layer))) & 1
    return llr * (1 - 2 * ai)


def de_order(lab, tables, pmf, layer: int, d: int, layers: int, n_log: int, *, root_seed: int, de_seed: int = DE_SEED,
             m_root: int = M_ROOT, n_samples: int = DE_SAMPLES) -> np.ndarray:
    root = de_root_llr(tables, pmf, layer, d, layers, m_root=m_root, seed=root_seed)
    pop = lab.de.de_llr_populations_from_root(root, int(n_log), n_samples=int(n_samples), seed=int(de_seed))
    order = lab.de.de_order_from_population(pop)  # reliable-first
    del pop
    return order


def info_set_overlap(order1: np.ndarray, order2: np.ndarray, k: int) -> float:
    if k <= 0:
        return 1.0
    return len(set(np.asarray(order1[:k]).tolist()) & set(np.asarray(order2[:k]).tolist())) / float(k)


# --------------------------------------------------------------------------- #
# E1: genie-SC Monte Carlo construction (replaces sampled DE on the run path)
# --------------------------------------------------------------------------- #
def f_minsum(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Check-node rule of the native engine (min-sum)."""
    return np.sign(a) * np.sign(b) * np.minimum(np.abs(a), np.abs(b))


def genie_sc_stats(llr: np.ndarray, u: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Genie SC (true u fed back) over frames.  ``llr, u``: (F, N).  Returns per-leaf sums over frames of
    (exp(-s/2), P[s<0]+0.5 P[s=0], s) with s = leaf LLR * (1 - 2 u_leaf) (sign-aligned to the true bit)."""
    F, N = llr.shape
    Z = np.zeros(N)
    E = np.zeros(N)
    S = np.zeros(N)

    def rec(al, us, off):
        n = al.shape[1]
        if n == 1:
            s = np.clip(al[:, 0] * (1 - 2.0 * us[:, 0]), -700, 700)
            Z[off] += np.exp(-s / 2).sum()
            E[off] += (s < 0).sum() + 0.5 * (s == 0).sum()
            S[off] += s.sum()
            return us.astype(np.int8)
        h = n // 2
        l, r = al[:, :h], al[:, h:]
        bl = rec(f_minsum(l, r), us[:, :h], off)
        br = rec(r + (1 - 2.0 * bl) * l, us[:, h:], off + h)
        return np.concatenate([bl ^ br, br], axis=1)

    rec(np.asarray(llr, dtype=np.float64), np.asarray(u, dtype=np.int8), 0)
    return Z, E, S


def synth_layer_frames(tables, pmf: np.ndarray, layer: int, d: int, layers: int, n: int, rng, nframes: int):
    """Synthetic layer-``layer`` frames from a circulant pmf: true prefix, ``x`` = bit plane, ``llr`` = conditional LLR
    (RNG stream: integers(a) then random(delta), (nframes, n))."""
    cdf = np.cumsum(pmf)
    cdf[-1] = 1.0
    a = rng.integers(0, d, size=(nframes, n))
    dl = np.minimum(np.searchsorted(cdf, rng.random((nframes, n))), d - 1)
    b = (a + dl) % d
    x = ((a >> (layers - 1 - int(layer))) & 1).astype(np.int8)
    llr = tables.llr[int(layer)][a >> (layers - int(layer)), b]
    return x, llr


def genie_mc_order(lab, tables, pmf: np.ndarray, layer: int, d: int, layers: int, n_log: int, *, seed: int,
                   frames: int = GENIE_FRAMES, chunk: int = GENIE_CHUNK) -> tuple[np.ndarray, dict]:
    """Reliable-first order from genie-SC Monte Carlo: Z_j = mean exp(-s_j/2), ascending; ties broken by mean s
    descending.  Uses only the (CAL32-fitted) ``pmf`` and its ``tables``."""
    n = 1 << int(n_log)
    rng = np.random.default_rng(int(seed))
    Zt = np.zeros(n)
    Et = np.zeros(n)
    St = np.zeros(n)
    for c0 in range(0, int(frames), int(chunk)):
        cm = min(int(chunk), int(frames) - c0)
        x, llr = synth_layer_frames(tables, pmf, layer, d, layers, n, rng, cm)
        u = np.stack([encode(lab, x[j], n_log) for j in range(cm)])
        Z, E, S = genie_sc_stats(llr, u)
        Zt += Z
        Et += E
        St += S
    Zm, Em, Sm = Zt / frames, Et / frames, St / frames
    order = np.lexsort((-Sm, Zm)).astype(np.int64)
    return order, {"Z": Zm, "Pe": Em, "S": Sm}


# --------------------------------------------------------------------------- #
# Rate allocation: k_i(mu), f(mu) (contract 5, 7)
# --------------------------------------------------------------------------- #
def layer_ks(caps: np.ndarray, mu: float, n: int, min_k: int = MIN_K) -> np.ndarray:
    k = np.floor(n * np.maximum(0.0, np.asarray(caps, dtype=np.float64) - np.asarray(mu, dtype=np.float64))).astype(np.int64)
    k[k < min_k] = 0  # whole-layer disclosure
    return k


def k_frozen(ks: np.ndarray, n: int) -> int:
    return int(np.sum(n - np.asarray(ks, dtype=np.int64)))


def f_of_ks(ks: np.ndarray, n: int, h_total_bits: float, tag_bits: int = TAG_BITS) -> float:
    return (k_frozen(ks, n) + int(tag_bits)) / (float(h_total_bits) * int(n))


def f_of_mu(caps, mu, n, h_total_bits, tag_bits=TAG_BITS) -> float:
    return f_of_ks(layer_ks(caps, mu, n), n, h_total_bits, tag_bits)


def solve_mu_for_f(caps, target_f: float, n: int, h_total_bits: float, tag_bits: int = TAG_BITS) -> float:
    """Smallest mu with f(mu) >= target_f (f(mu) is a non-decreasing step function); deterministic bisection."""
    lo, hi = 0.0, float(np.max(caps))
    if f_of_mu(caps, hi, n, h_total_bits, tag_bits) < target_f:
        raise ValueError("target f above the all-disclosed limit")
    if f_of_mu(caps, lo, n, h_total_bits, tag_bits) >= target_f:
        return lo
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f_of_mu(caps, mid, n, h_total_bits, tag_bits) >= target_f:
            hi = mid
        else:
            lo = mid
    return hi


def shifted_mu(mu_shape, delta: float) -> np.ndarray:
    """E2: per-layer margins ``mu_i + delta`` truncated to >= 0."""
    return np.maximum(0.0, np.asarray(mu_shape, dtype=np.float64) + float(delta))


def solve_delta_for_f(caps, mu_shape, target_f: float, n: int, h_total_bits: float, tag_bits: int = TAG_BITS) -> float:
    """Smallest uniform shift delta with f(mu_shape + delta) >= target_f (f is a non-decreasing step function of delta).
    Below the reachable minimum returns the lower end (all mu_i truncated to 0); above the maximum raises."""
    caps = np.asarray(caps, dtype=np.float64)
    lo, hi = -float(np.max(mu_shape)), float(np.max(caps))
    if f_of_mu(caps, shifted_mu(mu_shape, hi), n, h_total_bits, tag_bits) < target_f:
        raise ValueError("target f above the all-disclosed limit")
    if f_of_mu(caps, shifted_mu(mu_shape, lo), n, h_total_bits, tag_bits) >= target_f:
        return lo
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f_of_mu(caps, shifted_mu(mu_shape, mid), n, h_total_bits, tag_bits) >= target_f:
            hi = mid
        else:
            lo = mid
    return hi


def n_active_layers(caps, n: int, min_k: int = MIN_K) -> int:
    """Layers that are not whole-layer-disclosed at mu = 0 (E2: F3 budget split 0.03 / n_active)."""
    return int(np.sum(np.floor(n * np.asarray(caps, dtype=np.float64)) >= min_k))


# --------------------------------------------------------------------------- #
# Decoding primitives
# --------------------------------------------------------------------------- #
def encode(lab, u: np.ndarray, n_log: int) -> np.ndarray:
    return np.asarray(lab.polar.polar_encode(np.asarray(u, dtype=np.int8), int(n_log)), dtype=np.int8)


def decode_layer(lab, dec, llr: np.ndarray, order: np.ndarray, k: int, x_true: np.ndarray, n_log: int, list_size: int) -> tuple[np.ndarray, float]:
    """One SW codeword: frozen values = true u on frozen positions (info positions zeroed). Returns (x_hat, pm)."""
    n = 1 << int(n_log)
    mask = lab.polar.info_mask_from_order(order, int(k), n)
    u_true = encode(lab, x_true, n_log)  # F^{(x)n} is an involution: u = x F
    frozen = (u_true * (1 - mask.astype(np.int8))).astype(np.uint8)
    u_hat, pm, _ = dec.decode_batch(llr.reshape(1, -1), mask, frozen.reshape(1, -1), int(n_log), int(list_size))
    return encode(lab, u_hat[0], n_log), float(pm[0])


def decode_block(lab, dec, tables, orders, ks, a_sym, b_sym, *, layers: int, n_log: int, list_size: int) -> dict:
    """Hard-prefix MSD over layers 0..layers-1; wrong prefixes propagate (no early stop, no genie)."""
    hat_planes: list[np.ndarray] = []
    layer_recs = []
    first_err = None
    t_cw_max = 0.0
    for i in range(layers):
        x_true = plane_bits(a_sym, i, layers)
        k = int(ks[i])
        if k == 0:
            hat_planes.append(x_true.astype(np.int64))  # whole layer disclosed
            layer_recs.append({"layer": i, "k": 0, "n_frozen": 1 << n_log, "disclosed": True, "err": False, "n_bit_err": 0})
            continue
        pref = np.zeros(a_sym.shape[0], dtype=np.int64) if i == 0 else lab.msd.prefix_from_bits(hat_planes, i)
        llr = lab.msd.conditional_llr(tables, i, b_sym, pref)
        t0 = time.perf_counter()
        x_hat, pm = decode_layer(lab, dec, llr, orders[i], k, x_true, n_log, list_size)
        t_cw_max = max(t_cw_max, time.perf_counter() - t0)
        nerr = int(np.sum(x_hat != x_true))
        hat_planes.append(x_hat.astype(np.int64))
        if nerr and first_err is None:
            first_err = i
        layer_recs.append({"layer": i, "k": k, "n_frozen": (1 << n_log) - k, "disclosed": False, "err": bool(nerr), "n_bit_err": nerr, "pm": pm})
    a_hat = bits_to_symbols(hat_planes)
    exact = bool(np.array_equal(a_hat, np.asarray(a_sym, dtype=np.int64)))
    return {"a_hat": a_hat, "exact": exact, "first_error_layer": first_err, "layers": layer_recs, "wall_codeword_max_s": t_cw_max}


def block_tag_pass(a_sym, a_hat, exact: bool, tag_fn: Callable[[np.ndarray], np.ndarray], layers: int) -> bool:
    if exact:
        return True  # identical bits -> identical tag by construction
    ref = tag_fn(symbols_to_bits(a_sym, layers))
    cand = tag_fn(symbols_to_bits(a_hat, layers))
    return bool(np.array_equal(ref, cand))


def classify(exact: bool, tag_pass: bool) -> str:
    """``exact`` / ``verify_failed`` / ``undetected`` (never merged)."""
    if exact and tag_pass:
        return "exact"
    if (not exact) and tag_pass:
        return "undetected"
    return "verify_failed"


# --------------------------------------------------------------------------- #
# Statistics helpers
# --------------------------------------------------------------------------- #
def wilson(k: int, n: int, z: float = 1.96) -> dict:
    if n <= 0:
        return {"k": k, "n": n, "z": z, "p_hat": None, "lower": None, "upper": None}
    p = k / n
    den = 1.0 + z * z / n
    c = (p + z * z / (2.0 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4.0 * n * n)) / den
    return {"k": k, "n": n, "z": z, "p_hat": p, "lower": max(0.0, c - h), "upper": min(1.0, c + h)}


def taxonomy(entries: list[dict]) -> dict:
    """Per-group counts.  ``undetected`` is isolated (never in exact/fail/D)."""
    ok = [e for e in entries if e.get("status") == "ok"]
    exact = sum(1 for e in ok if e["outcome"] == "exact")
    vf = sum(1 for e in ok if e["outcome"] == "verify_failed")
    und = sum(1 for e in ok if e["outcome"] == "undetected")
    n_abort = sum(1 for e in entries if "resource_abort" in str(e.get("status")))
    n_err = sum(1 for e in entries if str(e.get("status")).startswith("error"))
    n_ns = sum(1 for e in entries if str(e.get("status")).startswith("not_started"))
    d = exact + vf
    return {"n_entries": len(entries), "exact": exact, "verify_failed": vf, "decode_failed": 0, "undetected": und,
            "resource_abort": n_abort, "error": n_err, "not_started": n_ns, "D_valid_denominator": d,
            "p_hat": (vf / d) if d else None, "wilson_95ci": wilson(vf, d) if d else None,
            "D_below_56": bool(d < 56)}


def contingency_2x2(pairs: list[tuple[bool, bool]]) -> dict:
    return {"n": len(pairs),
            "bin_exact_nb_exact": sum(1 for a, b in pairs if a and b),
            "bin_exact_nb_nonexact": sum(1 for a, b in pairs if a and not b),
            "bin_nonexact_nb_exact": sum(1 for a, b in pairs if (not a) and b),
            "bin_nonexact_nb_nonexact": sum(1 for a, b in pairs if (not a) and (not b))}


def load_nb_parts(nb_dir: str | Path) -> dict:
    out = {}
    for p in sorted(Path(nb_dir).glob("part_*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        scl = d.get("scl") or {}
        ok = d.get("status") == "ok"
        out[(d["session"], int(d["global_block_index"]))] = {
            "status": d.get("status"), "frame_start": d.get("frame_start"), "frame_end": d.get("frame_end"),
            "nb_scl_exact": bool(scl.get("exact")) if ok else None,
            "nb_scl_undetected": bool(scl.get("undetected")) if ok else None,
        }
    return out


# --------------------------------------------------------------------------- #
# Session inputs / configuration
# --------------------------------------------------------------------------- #
@dataclass
class RunConfig:
    n_log: int = N_LOG
    d: int = D_SYMBOL
    list_size: int = LIST_SIZE
    m_design: int = M_DESIGN
    genie_frames: int = GENIE_FRAMES
    genie_chunk: int = GENIE_CHUNK
    f1: float = F1_TARGET
    mu_hi_max: float = MU_HI_MAX
    mu_steps: int = MU_STEPS
    f3_target_fer: float = F3_TARGET_FER
    f4_offset: float = F4_OFFSET
    tag_bits: int = TAG_BITS
    n_workers: int = 8
    de_workers: int = 3  # construction (genie-MC) workers; name kept for the driver CLI (--de-workers)
    wall_total_s: float = WALL_TOTAL_S
    design_chunk: int = 8

    @property
    def n(self) -> int:
        return 1 << self.n_log

    @property
    def layers(self) -> int:
        return layers_of(self.d)


@dataclass
class SessionInput:
    name: str
    idx: int
    cal_a: np.ndarray
    cal_b: np.ndarray
    h_total_bits: float
    f_nb: float  # F2 target (NB f_book_with_crc)
    frames_a: np.ndarray | None = None
    frames_b: np.ndarray | None = None
    blocks: list = field(default_factory=list)
    fit_joint: np.ndarray | None = None  # NB-side fit['joint'] (real run only; cross-check + P-M2 source)


# --------------------------------------------------------------------------- #
# Process pool plumbing (fork; shared read-only globals)
# --------------------------------------------------------------------------- #
_G: dict[str, Any] = {}
_LOCAL: dict[str, Any] = {}


def _decoder():
    if "dec" not in _LOCAL or _LOCAL.get("pid") != os.getpid():
        _LOCAL["dec"] = _G["lab"].scl.MsdSclDecoder()
        _LOCAL["pid"] = os.getpid()
    return _LOCAL["dec"]


def _peak_rss_gib() -> float | None:
    try:
        with open("/proc/self/status", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    return float(line.split()[1]) / 1024.0**2
    except OSError:
        pass
    return None


def run_parallel(fn, args: list, n_workers: int) -> list:
    if n_workers <= 1 or len(args) <= 1:
        return [fn(a) for a in args]
    if "fork" not in mp.get_all_start_methods():
        raise RuntimeError("fork start method required (Linux/WSL)")
    with mp.get_context("fork").Pool(min(int(n_workers), len(args))) as pool:
        return pool.map(fn, args, chunksize=1)


def _genie_task(arg) -> dict:
    sess, layer = arg
    S = _G["sessions"][sess]
    cfg = _G["cfg"]
    t0 = time.perf_counter()
    order, st = genie_mc_order(_G["lab"], S["tables"], S["pmf"], layer, cfg.d, cfg.layers, cfg.n_log,
                               seed=GENIE_SEED_BASE + 1000 * S["idx"] + layer, frames=cfg.genie_frames, chunk=cfg.genie_chunk)
    return {"session": sess, "layer": layer, "order": order, "z": st["Z"], "pe": st["Pe"], "wall_s": time.perf_counter() - t0,
            "rss_gib_peak": _peak_rss_gib()}


def e_max_allowed(m_design: int, thr: float) -> int:
    """Largest error count e with p~ = (e+0.5)/(M+1) <= thr (-1 if even e=0 exceeds thr: M too small to resolve thr)."""
    e = -1
    while ptilde(e + 1, m_design) <= thr:
        e += 1
    return e


def _design_eval(sess: str, layer: int, k: int, e_max: int | None = None) -> dict:
    """Design-set MC for one (session, layer, k): errors over ``m_design`` synthetic codewords (true prefix,
    common random numbers across k).  With ``e_max`` the loop stops as soon as errors > e_max (``complete=False``)."""
    S = _G["sessions"][sess]
    cfg = _G["cfg"]
    lab = _G["lab"]
    dec = _decoder()
    n, d, layers = cfg.n, cfg.d, cfg.layers
    mask = lab.polar.info_mask_from_order(S["orders"][layer], int(k), n)
    inv = (1 - mask.astype(np.int8))
    rng = np.random.default_rng(DESIGN_SEED_BASE + 1000 * S["idx"] + layer)
    errs = 0
    done = 0
    t_start = time.perf_counter()
    for c0 in range(0, cfg.m_design, cfg.design_chunk):
        cm = min(cfg.design_chunk, cfg.m_design - c0)
        x, llr = synth_layer_frames(S["tables"], S["pmf"], layer, d, layers, n, rng, cm)
        u = np.stack([encode(lab, x[j], cfg.n_log) for j in range(cm)])
        frozen = (u * inv[None, :]).astype(np.uint8)
        u_hat, _, _ = dec.decode_batch(llr, mask, frozen, cfg.n_log, cfg.list_size)
        for j in range(cm):
            if not np.array_equal(encode(lab, u_hat[j], cfg.n_log), x[j]):
                errs += 1
        done += cm
        if e_max is not None and errs > e_max:
            break
    wall = time.perf_counter() - t_start
    return {"session": sess, "layer": layer, "k": int(k), "errors": int(errs), "frames": int(done), "complete": bool(done == cfg.m_design),
            "wall_s": wall, "wall_per_codeword_s": wall / max(done, 1), "rss_gib_peak": _peak_rss_gib()}


def _design_task(arg) -> dict:
    sess, layer, k = arg
    return _design_eval(sess, layer, k)


def _mu_task(arg) -> dict:
    """E2: smallest-mu bisection for one (session, layer): p~_i(mu_i) <= thr.  mu = 0 is tried first (early exit on failure),
    then ``mu_steps`` bisection steps on [0, min(cap_i, mu_hi_max)].  ``passed_eval`` is the complete evaluation at the result."""
    sess, layer, thr = arg
    S = _G["sessions"][sess]
    cfg = _G["cfg"]
    cap = float(S["caps"][layer])
    e_max = e_max_allowed(cfg.m_design, thr)
    if e_max < 0:
        raise ValueError(f"m_design={cfg.m_design} cannot resolve per-layer threshold {thr:.5f} (p~ floor {ptilde(0, cfg.m_design):.5f})")
    trace = []
    best = {"mu": None, "eval": None}

    def trial(mu):
        k = int(layer_ks(np.array([cap]), mu, cfg.n)[0])
        if k == 0:
            trace.append({"mu": mu, "k": 0, "errors": 0, "complete": True, "passed": True, "whole_layer_disclosed": True})
            return True, None
        r = _design_eval(sess, layer, k, e_max)
        ok = bool(r["complete"] and r["errors"] <= e_max)
        trace.append({"mu": mu, "k": k, "errors": r["errors"], "frames": r["frames"], "complete": r["complete"], "passed": ok})
        return ok, (r if ok else None)

    ok0, r0 = trial(0.0)
    if ok0:
        return {"session": sess, "layer": layer, "mu": 0.0, "e_max": e_max, "thr": thr, "trace": trace, "eval": r0, "flags": []}
    lo, hi0 = 0.0, min(cap, float(cfg.mu_hi_max))
    hi = hi0
    hi_verified = False
    hi_eval = None
    for _ in range(int(cfg.mu_steps)):
        mid = 0.5 * (lo + hi)
        ok, r = trial(mid)
        if ok:
            hi, hi_verified, hi_eval = mid, True, r
        else:
            lo = mid
    flags = []
    if not hi_verified:
        ok, r = trial(hi0)  # never passed inside the bracket: evaluate the upper edge once (complete result recorded)
        hi_eval = r if ok else _design_eval(sess, layer, int(layer_ks(np.array([cap]), hi0, cfg.n)[0]))
        flags.append("mu_upper_bracket_edge_" + ("passes_unrefined" if ok else "FAILS_layer_design_target_not_met"))
    return {"session": sess, "layer": layer, "mu": hi, "e_max": e_max, "thr": thr, "trace": trace, "eval": hi_eval, "flags": flags}


def _block_job(arg) -> dict:
    sess, block, point_idx = arg
    S = _G["sessions"][sess]
    cfg = _G["cfg"]
    lab = _G["lab"]
    pt = S["points"][point_idx]
    base = {"label": pt["label"], "f_target": pt["f_target"], "f_realized": pt["f_realized"], "mu": pt["mu"]}
    if time.time() > _G["deadline"]:
        return base | {"status": "not_started_total_wall_budget"}
    t0 = time.perf_counter()
    try:
        s, e = block["frame_start"], block["frame_end"]
        a_sym = S["input"].frames_a[s:e + 1].ravel()
        b_sym = S["input"].frames_b[s:e + 1].ravel()
        res = decode_block(lab, _decoder(), S["tables"], S["orders"], pt["ks"], a_sym, b_sym,
                           layers=cfg.layers, n_log=cfg.n_log, list_size=cfg.list_size)
        tag_ok = block_tag_pass(a_sym, res["a_hat"], res["exact"], lambda bits: _G["tag_fn"](bits, block["global_block_index"]), cfg.layers)
        outcome = classify(res["exact"], tag_ok)
        status = "ok"
        if res["wall_codeword_max_s"] > _G["codeword_wall_limit_s"]:
            status = "resource_abort_codeword_wall"  # recorded; excluded from taxonomy (never silent)
        return base | {"status": status, "outcome": outcome, "exact": res["exact"], "tag_pass": tag_ok,
                       "first_error_layer": res["first_error_layer"], "layers": res["layers"],
                       "n_symbol_err": int(np.sum(res["a_hat"] != np.asarray(a_sym, dtype=np.int64))),
                       "wall_s": time.perf_counter() - t0, "wall_codeword_max_s": res["wall_codeword_max_s"]}
    except Exception as exc:  # recorded, never propagated
        import traceback
        return base | {"status": f"error:{type(exc).__name__}", "error": traceback.format_exc()}


# --------------------------------------------------------------------------- #
# Construction (CAL32-only) -- deliberately has NO block/test argument
# --------------------------------------------------------------------------- #
def freeze_construction(lab, cfg: RunConfig, name: str, idx: int, cal_a: np.ndarray, cal_b: np.ndarray,
                        h_total_bits: float, fit_joint: np.ndarray | None = None) -> dict:
    """Stage 1 of a session: invariance gate, pmf choice, tables, caps.  DE orders are added later."""
    d = cfg.d
    inv = invariance_check(lab, cal_a, cal_b, d, seed=NULL_SEED_BASE + idx)
    out: dict[str, Any] = {"session": name, "idx": idx, "invariance": inv}
    if not inv["compatible"]:
        out["stop"] = "model_incompatible_R_gt_1.25 (D2: STOP to PI)"
        return out
    dcounts = delta_counts(cal_a, cal_b, d)
    cv = cv_select_pmf(lab, cal_a, cal_b, d)
    override = None
    m2_check = None
    if fit_joint is not None:
        override = lab.msd.difference_pmf(fit_joint, d)
        m2_check = float(np.max(np.abs(override - m2_pmf(dcounts, d))))
    ch = build_channel(lab, cv["source"], dcounts, d, pmf_m2_override=override if cv["source"] == "P-M2" else None)
    out |= {"cv": cv, "pm2_vs_fit_joint_maxabs": m2_check, "channel": ch, "n_cal": int(np.asarray(cal_a).size),
            "h_total_bits": float(h_total_bits),
            "caps_consistency": {"sum_caps": ch["sum_caps"], "layers_minus_sum_caps": cfg.layers - ch["sum_caps"],
                                 "h_total_bits": float(h_total_bits), "diff_bits": (cfg.layers - ch["sum_caps"]) - float(h_total_bits),
                                 "exceeds_0.03_bit": bool(abs((cfg.layers - ch["sum_caps"]) - float(h_total_bits)) > 0.03)}}
    return out


def _init_session_globals(cfg, lab, sessions: dict) -> None:
    _G["cfg"] = cfg
    _G["lab"] = lab
    _G["sessions"] = sessions


def compute_orders(cfg: RunConfig, lab, cons: dict[str, dict]) -> dict:
    """E1: genie-SC MC orders for every (session, layer) (parallel over ``cfg.de_workers``); CAL32-derived models only."""
    sessions = {s: {"idx": c["idx"], "tables": c["channel"]["tables"], "pmf": c["channel"]["pmf"]} for s, c in cons.items()}
    _init_session_globals(cfg, lab, sessions)
    args = [(s, i) for s in cons for i in range(cfg.layers)]
    res = run_parallel(_genie_task, args, cfg.de_workers)
    orders = {s: [None] * cfg.layers for s in cons}
    zs = {s: [None] * cfg.layers for s in cons}
    meta = {s: [None] * cfg.layers for s in cons}
    for r in res:
        orders[r["session"]][r["layer"]] = r["order"]
        zs[r["session"]][r["layer"]] = r["z"]
        o = r["order"]
        meta[r["session"]][r["layer"]] = {"wall_s": r["wall_s"], "rss_gib_peak": r["rss_gib_peak"], "genie_frames": cfg.genie_frames,
                                          "order_head8": o[:8].tolist(), "order_tail8": o[-8:].tolist(),
                                          "order_sha256": hashlib.sha256(np.asarray(o, dtype=np.int64).tobytes()).hexdigest()}
    return {"orders": orders, "z": zs, "meta": meta}


# --------------------------------------------------------------------------- #
# Design-set evaluation and the F grid (contract 5)
# --------------------------------------------------------------------------- #
def ptilde(errors: int, frames: int) -> float:
    return (errors + 0.5) / (frames + 1)


class DesignEvaluator:
    """Cached design-set MC.  ``solve_layer_mus`` (E2 per-layer bisection) and ``evaluate_many`` share the cache of
    COMPLETE evaluations keyed by (session, layer, k)."""

    def __init__(self, cfg: RunConfig, lab, cons: dict, orders: dict, zs: dict | None = None):
        self.cfg, self.lab, self.cons = cfg, lab, cons
        self.sessions = {s: {"idx": c["idx"], "tables": c["channel"]["tables"], "pmf": c["channel"]["pmf"], "orders": orders[s],
                             "caps": c["channel"]["caps"]} for s, c in cons.items()}
        self.zs = zs
        self.cache: dict[tuple, dict] = {}
        self.n_eval = 0
        self.max_cw_wall = 0.0

    def solve_layer_mus(self) -> dict:
        """E2 F3: per layer the smallest mu_i with p~_i <= 0.03 / n_active.  Returns {session: {...}}."""
        cfg = self.cfg
        _init_session_globals(cfg, self.lab, self.sessions)
        thr, args = {}, []
        for s, c in self.cons.items():
            thr[s] = cfg.f3_target_fer / n_active_layers(c["channel"]["caps"], cfg.n)
            args += [(s, i, thr[s]) for i in range(cfg.layers) if int(np.floor(cfg.n * c["channel"]["caps"][i])) >= MIN_K]
        out = {s: {"mu": np.zeros(cfg.layers), "n_active": n_active_layers(c["channel"]["caps"], cfg.n), "layer_threshold": thr[s],
                   "layers": {}} for s, c in self.cons.items()}
        for r in run_parallel(_mu_task, args, cfg.n_workers):
            o = out[r["session"]]
            o["mu"][r["layer"]] = r["mu"]
            o["layers"][r["layer"]] = {"mu": r["mu"], "e_max": r["e_max"], "trace": r["trace"], "flags": r["flags"]}
            e = r["eval"]
            if e is not None:
                self.cache[(r["session"], r["layer"], e["k"])] = e
                self.max_cw_wall = max(self.max_cw_wall, e["wall_per_codeword_s"])
        for s, c in self.cons.items():  # inactive (whole-layer-disclosed at mu=0) layers: mu = cap (k = 0)
            for i in range(cfg.layers):
                if i not in out[s]["layers"]:
                    out[s]["mu"][i] = float(c["channel"]["caps"][i])
                    out[s]["layers"][i] = {"mu": out[s]["mu"][i], "e_max": None, "trace": [], "flags": ["inactive_layer_whole_disclosure"]}
        return out

    def evaluate_many(self, reqs: list[tuple[str, np.ndarray]]) -> list[dict]:
        """reqs: (session, mu vector).  Missing (session, layer, k) design evaluations run in one pool (complete, no early exit)."""
        cfg = self.cfg
        plans = []
        need = []
        for s, mu in reqs:
            ks = layer_ks(self.cons[s]["channel"]["caps"], mu, cfg.n)
            plans.append((s, mu, ks))
            for i, k in enumerate(ks):
                if k > 0 and (s, i, int(k)) not in self.cache and (s, i, int(k)) not in need:
                    need.append((s, i, int(k)))
        if need:
            _init_session_globals(cfg, self.lab, self.sessions)
            for r in run_parallel(_design_task, need, cfg.n_workers):
                self.cache[(r["session"], r["layer"], r["k"])] = r
                self.max_cw_wall = max(self.max_cw_wall, r["wall_per_codeword_s"])
        out = []
        for s, mu, ks in plans:
            layers = []
            tot = 0.0
            for i, k in enumerate(ks):
                if k == 0:
                    layers.append({"layer": i, "k": 0, "disclosed": True, "errors": 0, "p_tilde": 0.0})
                else:
                    r = self.cache[(s, i, int(k))]
                    p = ptilde(r["errors"], r["frames"])
                    tot += p
                    rec = {"layer": i, "k": int(k), "disclosed": False, "errors": r["errors"], "frames": r["frames"], "p_tilde": p,
                           "wall_per_codeword_s": r["wall_per_codeword_s"]}
                    if self.zs is not None:  # union-bound style leading indicator on the genie-MC statistics
                        rec["sum_Z_info_set"] = float(self.zs[s][i][self.sessions[s]["orders"][i][:int(k)]].sum())
                    layers.append(rec)
            self.n_eval += 1
            out.append({"session": s, "mu": np.asarray(mu, dtype=np.float64), "f_realized": f_of_ks(ks, cfg.n, self.cons[s]["h_total_bits"], cfg.tag_bits),
                        "ks": ks, "sum_p_tilde": tot, "layers": layers})
        return out


def _f_flags(target: float, realized: float) -> list:
    if realized - target > 0.02:
        return [f"f_realized_exceeds_target_by_{realized - target:.3f}: f at the lowest reachable mu is above the target"]
    return []


def build_f_grid(cfg: RunConfig, cons: dict, ev: DesignEvaluator, f_nb: dict[str, float]) -> dict:
    """E2 grid per session.  F3 = per-layer design bisection (mu_i); F1/F2/F4 = F3 shape shifted by a uniform delta
    (mu_i + delta >= 0) to reach f = F1 / f_nb / f(F3) + 0.10.  Design-set only; no test block enters."""
    names = list(cons)
    caps = {s: cons[s]["channel"]["caps"] for s in names}
    hb = {s: cons[s]["h_total_bits"] for s in names}
    sol = ev.solve_layer_mus()
    plan = []  # (session, label, f_target, mu vector, delta)
    for s in names:
        mu3 = sol[s]["mu"]
        f3 = f_of_mu(caps[s], mu3, cfg.n, hb[s], cfg.tag_bits)
        targets = (("F1", cfg.f1), ("F2", f_nb[s]), ("F3", f3), ("F4", f3 + cfg.f4_offset))
        for lab_, f in targets:
            if lab_ == "F3":
                plan.append((s, lab_, f3, mu3, 0.0))
            else:
                dlt = solve_delta_for_f(caps[s], mu3, f, cfg.n, hb[s], cfg.tag_bits)
                plan.append((s, lab_, f, shifted_mu(mu3, dlt), dlt))
    res = ev.evaluate_many([(s, mu) for s, _, _, mu, _ in plan])
    grid = {s: {} for s in names}
    for (s, lab_, f, mu, dlt), r in zip(plan, res):
        g = {"label": lab_, "f_target": f, "mu": [float(x) for x in mu], "delta_vs_F3_shape": dlt, "f_realized": r["f_realized"],
             "ks": r["ks"], "design_sum_p_tilde": r["sum_p_tilde"], "design_layers": r["layers"],
             "flags": _f_flags(f, r["f_realized"])}
        if lab_ == "F3":
            g["layer_mu_bisection"] = {str(i): v for i, v in sol[s]["layers"].items()}
            g["n_active"] = sol[s]["n_active"]
            g["layer_threshold_p_tilde"] = sol[s]["layer_threshold"]
            for i, v in sol[s]["layers"].items():
                g["flags"] += [f"layer{i}:{fl}" for fl in v["flags"] if not fl.startswith("inactive")]
        grid[s][lab_] = g
    return grid


# --------------------------------------------------------------------------- #
# Full pipeline (synthetic or real SessionInputs)
# --------------------------------------------------------------------------- #
def _jsonable(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    return str(o)


def dump_json(path: Path, obj) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, default=_jsonable), encoding="utf-8")


def calibrate_codeword_wall(cfg: RunConfig, lab, S: dict, layer: int, k: int) -> float:
    """T0-style single-codeword timing (synthetic) used as the 5x resource-abort reference."""
    _init_session_globals(cfg, lab, {"cal": S})
    dec = lab.scl.MsdSclDecoder()
    rng = np.random.default_rng(DESIGN_SEED_BASE)
    n, d, layers = cfg.n, cfg.d, cfg.layers
    cdf = np.cumsum(S["pmf"])
    cdf[-1] = 1.0
    a = rng.integers(0, d, size=n)
    b = (a + np.minimum(np.searchsorted(cdf, rng.random(n)), d - 1)) % d
    llr = S["tables"].llr[layer][a >> (layers - layer), b]
    x = plane_bits(a, layer, layers)
    t0 = time.perf_counter()
    decode_layer(lab, dec, llr, S["orders"][layer], k, x, cfg.n_log, cfg.list_size)
    return time.perf_counter() - t0


def run_pipeline(lab, cfg: RunConfig, sessions: list[SessionInput], out_dir: str | Path, tag_fn: Callable, *,
                 nb_dir: str | Path | None = None, t_start: float | None = None) -> dict:
    """CAL32 construction (genie-MC orders) -> design MC (per-layer mu, F grid) -> block decoding -> aggregation.  Writes only under ``out_dir``."""
    t_start = time.time() if t_start is None else t_start
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if (out / "results.json").exists() or list(out.glob("part_*.json")):
        raise RuntimeError(f"refusing to run: results.json/part_*.json already exist in {out} (additive-only, one-shot)")
    by_name = {s.name: s for s in sessions}

    # 1. CAL32-only construction, per session
    cons = {}
    for s in sessions:
        c = freeze_construction(lab, cfg, s.name, s.idx, s.cal_a, s.cal_b, s.h_total_bits, s.fit_joint)
        c["f_nb"] = s.f_nb
        cons[s.name] = c
    stops = {s: c["stop"] for s, c in cons.items() if "stop" in c}
    if stops:
        for s, c in cons.items():
            dump_json(out / f"construction_frozen_{s}.json", {k: v for k, v in c.items() if k != "channel"})
        return {"status": "STOP_model_incompatible", "stops": stops}

    do = compute_orders(cfg, lab, cons)
    orders = do["orders"]
    # 2. design MC and grid
    S0 = cons[sessions[0].name]
    S0cal = {"tables": S0["channel"]["tables"], "pmf": S0["channel"]["pmf"], "orders": orders[sessions[0].name], "idx": S0["idx"]}
    k_cal = int(layer_ks(S0["channel"]["caps"], 0.02, cfg.n)[cfg.layers - 1]) or int(cfg.n // 2)
    t0_cw = calibrate_codeword_wall(cfg, lab, S0cal, cfg.layers - 1, k_cal)
    cw_limit = max(5.0 * t0_cw, SLACK_MIN_CODEWORD_WALL_S)
    ev = DesignEvaluator(cfg, lab, cons, orders, do["z"])
    grid = build_f_grid(cfg, cons, ev, {s.name: s.f_nb for s in sessions})

    # 3. per-session frozen record
    for s in sessions:
        c = cons[s.name]
        g = grid[s.name]
        rec = {k: v for k, v in c.items() if k != "channel"}
        rec["channel"] = {"source": c["cv"]["source"], "caps": c["channel"]["caps"], "sum_caps": c["channel"]["sum_caps"],
                          "joint_mi_bits": c["channel"]["joint_mi_bits"], "pmf_entropy_bits": c["channel"]["pmf_entropy_bits"], "pmf_head8": c["channel"]["pmf"][:8], "pmf_tail8": c["channel"]["pmf"][-8:]}
        rec["genie_orders"] = do["meta"][s.name]
        rec["points"] = {lab_: {k: v for k, v in p.items()} for lab_, p in g.items()}
        rec["timing"] = {"codeword_wall_ref_s": t0_cw, "codeword_wall_limit_s": cw_limit, "design_max_wall_per_codeword_s": ev.max_cw_wall}
        dump_json(out / f"construction_frozen_{s.name}.json", rec)

    # 4. block decoding
    sess_g = {}
    for s in sessions:
        c = cons[s.name]
        pts = [dict(grid[s.name][lab_], label=lab_) for lab_ in POINT_LABELS]
        sess_g[s.name] = {"idx": s.idx, "tables": c["channel"]["tables"], "pmf": c["channel"]["pmf"], "orders": orders[s.name],
                          "points": pts, "input": s}
    _init_session_globals(cfg, lab, sess_g)
    _G["tag_fn"] = tag_fn
    _G["deadline"] = t_start + cfg.wall_total_s
    _G["codeword_wall_limit_s"] = cw_limit
    jobs = [(s.name, b, pi) for s in sessions for b in s.blocks for pi in range(len(POINT_LABELS))]
    results = run_parallel(_block_job, jobs, cfg.n_workers)
    per_block: dict[tuple, dict] = {}
    for (sn, b, pi), r in zip(jobs, results):
        key = (sn, b["global_block_index"])
        rec = per_block.setdefault(key, {"session": sn, "global_block_index": b["global_block_index"], "local_index": b.get("local_index"),
                                         "frame_start": b["frame_start"], "frame_end": b["frame_end"],
                                         "stratum_official": b.get("stratum_official"), "stratum_task": b.get("stratum_task"), "points": []})
        rec["points"].append(r)
    for (sn, gi), rec in per_block.items():
        dump_json(out / f"part_{sn}_{gi:02d}.json", rec)

    results_obj = aggregate(cfg, sessions, cons, grid, per_block, nb_dir)
    de_rss = [x["rss_gib_peak"] for s in sessions for x in do["meta"][s.name] if x["rss_gib_peak"] is not None]
    dz_rss = [r["rss_gib_peak"] for r in ev.cache.values() if r["rss_gib_peak"] is not None]
    results_obj["resources"] = {"rss_gib_peak_construction_tasks_max": max(de_rss) if de_rss else None,
                                "rss_gib_peak_design_tasks_max": max(dz_rss) if dz_rss else None,
                                "rss_gib_budget_per_process": RSS_GIB,
                                "rss_over_budget": bool((de_rss and max(de_rss) > RSS_GIB) or (dz_rss and max(dz_rss) > RSS_GIB)),
                                "note": "VmHWM of the worker process at task end (a reused pool worker reports its own high-water mark)"}
    results_obj["timing"] = {"wall_s_total": time.time() - t_start, "budget_wall_s_total": cfg.wall_total_s,
                             "codeword_wall_ref_s": t0_cw, "codeword_wall_limit_s": cw_limit, "n_design_evaluations": ev.n_eval, "construction_wall_s_sum": sum(x["wall_s"] for s in sessions for x in do["meta"][s.name])}
    dump_json(out / "results.json", results_obj)
    return results_obj


# --------------------------------------------------------------------------- #
# Aggregation (contract 7, 8)
# --------------------------------------------------------------------------- #
STRATUM_OFFICIAL = ("A1_CAL_characterization", "HELDOUT_model_selection", "EVAL_already_decoded")
STRATUM_TASK = ("never_decoded", "heldout_model_selection", "previously_decoded_eval")


def aggregate(cfg: RunConfig, sessions: list[SessionInput], cons: dict, grid: dict, per_block: dict, nb_dir) -> dict:
    nb = load_nb_parts(nb_dir) if nb_dir else {}
    flat = []  # (session, point label, block rec, point rec)
    for (sn, gi), rec in per_block.items():
        for p in rec["points"]:
            flat.append((sn, p["label"], rec, p))

    def group(sel):
        return taxonomy([dict(p, session=sn) for sn, lab_, rec, p in flat if sel(sn, lab_, rec)])

    per_point = {}
    for lab_ in POINT_LABELS:
        entry = {"per_session": {}, "pooled": group(lambda sn, l, r, L=lab_: l == L),
                 "by_stratum_official": {}, "by_stratum_task": {}}
        for s in sessions:
            g = grid[s.name][lab_]
            entry["per_session"][s.name] = {
                "f_target": g["f_target"], "f_realized": g["f_realized"], "mu": g["mu"], "ks": g["ks"],
                "K_frozen": k_frozen(g["ks"], cfg.n), "tag_bits": cfg.tag_bits,
                "design_sum_p_tilde": g["design_sum_p_tilde"],
                "taxonomy": group(lambda sn, l, r, L=lab_, S=s.name: l == L and sn == S),
            }
        for st in STRATUM_OFFICIAL:
            entry["by_stratum_official"][st] = group(lambda sn, l, r, L=lab_, X=st: l == L and r["stratum_official"] == X)
        for st in STRATUM_TASK:
            entry["by_stratum_task"][st] = group(lambda sn, l, r, L=lab_, X=st: l == L and r["stratum_task"] == X)
        # layer decomposition + measured per-layer error counts
        meas = {}
        for s in sessions:
            counts = [0] * cfg.layers
            first = {}
            n_ok = 0
            for sn, l, rec, p in flat:
                if sn != s.name or l != lab_ or p.get("status") != "ok":
                    continue
                n_ok += 1
                for L_ in p["layers"]:
                    if L_["err"]:
                        counts[L_["layer"]] += 1
                fe = p["first_error_layer"]
                first[str(fe)] = first.get(str(fe), 0) + 1
            meas[s.name] = {"n_ok_blocks": n_ok, "blocks_with_layer_error": counts, "first_error_layer_hist": first}
        entry["measured_layer_errors"] = meas
        # NB pairing
        pairs, undet_bin, excl = [], [], []
        mism = []
        for sn, l, rec, p in flat:
            if l != lab_ or p.get("status") != "ok":
                continue
            nbp = nb.get((sn, rec["global_block_index"]))
            if nbp is None or nbp["status"] != "ok":
                excl.append([sn, rec["global_block_index"]])
                continue
            if nbp["frame_start"] != rec["frame_start"] or nbp["frame_end"] != rec["frame_end"]:
                mism.append([sn, rec["global_block_index"]])
                continue
            pairs.append((p["outcome"] == "exact", bool(nbp["nb_scl_exact"])))
            if p["outcome"] == "undetected":
                undet_bin.append([sn, rec["global_block_index"]])
        entry["nb_scl_L16_pairing"] = {"table": contingency_2x2(pairs), "excluded_blocks": excl, "frame_range_mismatch": mism,
                                       "binary_undetected_blocks_counted_as_nonexact": undet_bin,
                                       "note": "counts only; no win rate; binary L=16 no CRC vs NB-SCL L=16 CRC-16"}
        per_point[lab_] = entry
    undetected_ids = [[sn, l, rec["global_block_index"]] for sn, l, rec, p in flat if p.get("status") == "ok" and p.get("outcome") == "undetected"]
    n_expected = sum(len(s.blocks) for s in sessions) * len(POINT_LABELS)
    status_counts: dict[str, int] = {}
    for sn, l, rec, p in flat:
        status_counts[str(p.get("status"))] = status_counts.get(str(p.get("status")), 0) + 1
    return {
        "probe_id": "r2c-strong-binary-msd-shg-64",
        "point_labels": list(POINT_LABELS),
        "per_point": per_point,
        "per_session_construction": {
            s.name: {"source": cons[s.name]["cv"]["source"], "cv": cons[s.name]["cv"], "invariance": cons[s.name]["invariance"],
                     "caps": cons[s.name]["channel"]["caps"], "caps_consistency": cons[s.name]["caps_consistency"],
                     "h_total_bits": s.h_total_bits, "f_nb_target_F2": s.f_nb} for s in sessions},
        "stop_undetected": bool(undetected_ids),
        "undetected_block_ids": undetected_ids,
        "block_accounting": {"n_expected_block_points": n_expected, "n_recorded": len(flat), "status_counts": status_counts,
                             "consistent": bool(n_expected == len(flat))},
        "stratum_note": ("stratum_official / stratum_task tables are shown with every pooled number (P-1, R2 9.2); "
                         "A1_CAL_characterization and HELDOUT_model_selection blocks touched model selection in earlier work (R2 labels) "
                         "and are a separate stratum; the pooled denominator D is the cross-stratum total (n=56 rule)."),
        "claims": "No verdict; counts, Wilson CIs and pairing tables only (contract 8).",
    }
