#!/usr/bin/env python3
"""R2 binary-Polar-baseline comparison driver: frozen bit-plane (d=1024, 10
layers) binary Polar reconciliation, decoded on the SAME frozen 64-block
SHG `_1`/`_2` pool as `workspace/r2_fer_shg_64/` (DATA_LEDGER.md §7), for a
descriptive comparison against the NB-Polar M2+SCL(L=16) result already
measured there (`workspace/r2_fer_shg_64/RESULT_SUMMARY.md`).

Authorization
-------------
**NOT YET GRANTED.** This file is a preparation-only artifact. See
``STATUS.yaml`` / ``AUTHORIZATION_PROMPT.md`` in this directory. ``main()``
refuses to run any real-data decode until PI authorization is on record and
an independent Pre-EXECUTE review PASSes (per the contract,
``docs/nbpolar/R2_BINARY_BASELINE_COMPARISON_CONTRACT_20260929.md``).

Scope and reuse discipline (AGENTS.md §5.1, §5.7, §10.1)
---------------------------------------------------------
This file is a NEW, additive driver. It imports and calls, UNCHANGED:

- ``scripts.m2_prior_validation`` (via the frozen NB-Polar packet
  ``workspace/r2_fer_shg_64/run.py``, imported read-only by file path -- NOT
  copied -- to guarantee the SAME session reconstruction / same 64-block
  frame ranges / byte-identical ``(x,y)`` symbol arrays as the NB-Polar R2
  measurement): ``build_session_blocks``, ``_reproduce_session_context``,
  ``SESSION_CFG``.
- ``src.reconciliation.real_polar_sc_rescue``: ``_polar_weight_order``
  (frozen construction -- polarization-weight / beta-expansion, beta=2**0.25,
  NOT density evolution, NOT genie/channel-adaptive -- this repo's
  `src/`/`experiments/` frozen baseline never implements DE; see
  TASK_PACKET.md §A for the full evidence trail), ``polar_encode_non_systematic``
  (confirmed self-inverse over GF(2) for this kernel/no-bit-reversal
  convention -- ``_selfcheck_involution.py`` in this directory, run against
  the frozen function, unmodified), ``polar_sc_decode_with_frozen``.
- ``src.reconciliation.cpp_scl_wrapper.PolarSCLDecoder`` (frozen CA-SCL,
  list size hardcoded to 4 in ``cpp_polar/main.cpp:14`` -- never edited;
  first use triggers ITS OWN designed self-build step, producing
  ``cpp_polar/ca_scl.so`` next to the already-shipped ``ca_scl.dll`` -- a
  compiled artifact of the unmodified ``main.cpp``, not a source edit).
- ``src.reconciliation.verification``: ``universal_hash_tag`` (frozen
  Toeplitz-style universal-hash tag, this repo's OWN baseline verification
  scheme -- reused for the block-level accept/tag check, at the SAME
  ``tag_bits`` length the NB-Polar side used, fetched at runtime from the
  NB-Polar ``chain.tag_bits``, never hardcoded independently).
- ``experiments.run_real_polar_max_pie``: ``calc_crc16``, ``_build_candidates``,
  ``_simulate_layer_sc_fer_early`` (frozen per-layer FER-calibration Monte
  Carlo, memoryless-BSC(p=layer_ber) model -- the SAME model the frozen
  baseline itself uses for its own rate search; see TASK_PACKET.md §A.2 for
  why no other model exists in `src/`/`experiments/`).

No line of ``sc.py``/``scl.py``/``scl_joint.py``/``two_layer.py``/
``transform.py``/``algebra.py``/``prior.py``/``prior_m2.py``/
``operational_f13*.py``/``m2_prior_validation.py``/``real_polar_sc_rescue.py``/
``run_real_polar_max_pie.py``/``cpp_scl_wrapper.py``/``verification.py``/
``cpp_polar/main.cpp``/``run_e2e_pipeline.py`` is edited by this file.

Mapping decisions (frozen here; see the contract for the full rationale)
-------------------------------------------------------------------------
- Native alphabet: d=1024 (10 bits/symbol) -- the SAME raw integer values
  already carried by ``frames_a``/``frames_b`` (``scripts.m2_prior_validation``
  symbol map ``b_A % 1024`` -- confirmed, not a re-derived choice; NB-Polar's
  own GF(32) two-layer framing is `A = 32*U1 + U2`, a *different
  decomposition of the identical native d=1024 integer*, not a coarser
  measurement).
- Binary layering: 10 INDEPENDENT bit-planes, MSB (layer_idx=0, shift=9)
  first, matching ``_extract_real_layer_bers``'s own convention verbatim
  -- no cross-layer conditioning (the frozen baseline's own MLC treatment;
  the *conditional* MSD scheme lives only in the sibling Release repo's
  `low_dim_opt/core/msd_conditional.py`, explicitly out of scope per
  AGENTS.md §0/§5.1).
- Per-layer code length: N=4096 (the largest of the frozen baseline's own
  choices, {1024,2048,4096} -- `run_real_polar_max_pie.py` argparse), 8
  codewords per layer per block (32768/4096=8), 80 codewords per block.
- Primary claim-bearing arm: SC (``polar_sc_decode_with_frozen``), because
  it needs no CRC-embedding side effect (see below) and reconciles 100% of
  Alice's real u-domain bits with a single deterministic path. Accept/tag
  is a SEPARATE, one-per-block Toeplitz check (frozen ``verification.py``),
  analogous to NB-Polar's own per-block tag.
- Secondary, descriptive-only arm: CA-SCL(L=4, CRC-16). The frozen C++
  decoder's CRC path-selection is baked in (``main.cpp`` checks CRC over the
  assembled info-bit vector internally) and requires the LAST 16 (ascending
  index) info positions of each codeword to genuinely hold CRC(message),
  which means those 16 real u-domain positions per codeword are
  overwritten/sacrificed as pure overhead (not reconciled content) -- unlike
  SC, which reconciles all k info bits with no overwrite. This is a genuine
  architectural cost of reusing the frozen CA-SCL decoder unmodified for
  source-coding-style reconciliation (it was designed/calibrated in
  `run_real_polar_max_pie.py` for a message-transmission FER estimate, not
  for real-data reconciliation) and is reported, not hidden: CA-SCL's
  disclosed-bit count includes this 16-bit/codeword CRC tax. No separate
  block-level tag arm is built for CA-SCL (out of scope for this
  comparison's effort budget); only per-codeword message-exact-match is
  recorded, descriptively.

Output
------
Additive-only, this directory. Nothing is written outside it.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import math
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

NB_PACKET_DIR = REPO_ROOT / "workspace" / "r2_fer_shg_64"

# ---------------------------------------------------------------------------
# Frozen binary-baseline construction constants (see module docstring).
# ---------------------------------------------------------------------------
D_ARY = 1024
N_LAYERS = 10  # log2(D_ARY)
LAYER_N = 4096
LAYER_N_LOG = 12
CODEWORDS_PER_LAYER = 32768 // LAYER_N  # 8
CRC_BITS = 16
FER_THRESH = 0.05
# CALIB_N_FRAMES: Monte-Carlo trials per rate-search candidate. Set to the
# FROZEN BASELINE'S OWN DEFAULT (`experiments/run_real_polar_max_pie.py`
# argparse `--frames` default=100), NOT an independently-chosen larger value.
# This was revised DOWN from an initial draft of 4000 after a timing probe
# (`_selfcheck_sc_timing.py`, this directory) found the frozen
# `polar_sc_decode_with_frozen` reference implementation costs ~80.8 ms/call
# at N=4096 post-JIT (O(N^2 log N), not O(N log N) -- it re-runs the FULL
# `_encoding_step` partial-sum propagation at every one of the N leaf
# positions; see the contract's addendum). At 4000 frames/candidate a fine
# 31-point margin sweep would have cost on the order of 100+ CPU-hours for
# construction alone per session -- infeasible and not what the baseline
# itself does (it defaults to 100 frames and a SHORT hand-picked margin
# list, not a fine sweep). 100 frames/candidate keeps the whole
# construction search under ~1 CPU-hour/session (see the contract addendum
# for the arithmetic) while still using the SAME Monte-Carlo FER-calibration
# model and frame count the baseline's own CLI defaults to.
CALIB_N_FRAMES = 100
LLR_CLIP = 20.0

# The f-grid search uses a SHORT, HAND-PICKED margin list -- matching the
# frozen baseline's own style (`--scl-margins` defaults to "0.02,0.05", a
# short explicit list, not a fine arange sweep) -- rather than a dense
# sweep, both for tractability (see CALIB_N_FRAMES's note above) and
# because it is the closer analogue of the baseline's own native practice.
SC_MARGIN_CANDIDATES = (0.02, 0.05, 0.08, 0.12, 0.18, 0.25, 0.30)
MAX_F_POINTS = 4

# --- Budget (SERIAL single-process execution; Pre-EXECUTE round-2 F4) ------
# One serial process: no fork/parallelism, no parent hard-terminate. Enforced
# in code:
#   - total wall (BUDGET_WALL_S_TOTAL, measured from the start of main()):
#     checked before each session's construction and before each block; once
#     exceeded nothing new is started (remaining blocks are recorded as
#     status=NOT_STARTED_STATUS); the block already running is allowed to
#     finish.
#   - per-block wall (BUDGET_WALL_S_PER_BLOCK, cumulative from block start),
#     checked before each grid point of that block.
#   - per-block RSS (BUDGET_RSS_GIB_PER_BLOCK, process VmHWM), checked after
#     each grid point.
BUDGET_WALL_S_PER_BLOCK = 1200.0
BUDGET_RSS_GIB_PER_BLOCK = 4.0
BUDGET_WALL_S_TOTAL = 4.0 * 3600.0
NOT_STARTED_STATUS = "not_started_total_wall_budget"
MIN_D_FOR_ESTIMATE = 56  # D-FER-03 n=56; pooled D below this is labeled INSUFFICIENT

RESULTS_PATH = THIS_DIR / "results.json"

# Monotonic clock hook (tests replace this with a fake clock).
_CLOCK = time.monotonic


def _now() -> float:
    return _CLOCK()

_CTX: dict = {}


def _fail(msg: str, code: int = 2):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


# ---------------------------------------------------------------------------
# Frozen-function imports (read-only reuse; see module docstring).
# ---------------------------------------------------------------------------

def _load_nb_packet_module():
    """Import workspace/r2_fer_shg_64/run.py BY FILE PATH (read-only; not
    modified, not executed as __main__) so this driver's 64-block session
    reconstruction is the SAME CODE as the NB-Polar R2 measurement -- the
    strongest possible guarantee that the (x,y) symbol arrays are
    byte-identical (not merely "same formula, re-typed")."""
    path = NB_PACKET_DIR / "run.py"
    if not path.exists():
        _fail(f"predecessor NB packet not found (read-only reference): {path}")
    spec = importlib.util.spec_from_file_location("_r2_fer_shg_64_run_readonly", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # module-level code only defines constants/functions; no I/O
    return mod


def _load_binary_baseline_functions():
    """Import the frozen binary-baseline symbols. Two are private-by-
    convention (leading underscore) but reused unchanged, never copied."""
    rescue = importlib.import_module("src.reconciliation.real_polar_sc_rescue")
    cpp_wrap = importlib.import_module("src.reconciliation.cpp_scl_wrapper")
    verif = importlib.import_module("src.reconciliation.verification")
    maxpie = importlib.import_module("experiments.run_real_polar_max_pie")
    return dict(
        polar_weight_order=rescue._polar_weight_order,
        polar_encode_non_systematic=rescue.polar_encode_non_systematic,
        polar_sc_decode_with_frozen=rescue.polar_sc_decode_with_frozen,
        PolarSCLDecoder=cpp_wrap.PolarSCLDecoder,
        universal_hash_tag=verif.universal_hash_tag,
        calc_crc16=maxpie.calc_crc16,
        build_candidates=maxpie._build_candidates,
        simulate_layer_sc_fer_early=maxpie._simulate_layer_sc_fer_early,
    )


# ---------------------------------------------------------------------------
# Pure helpers (exercised by the synthetic smoke test; no I/O).
# ---------------------------------------------------------------------------

def h2(p: float) -> float:
    p = float(min(1.0 - 1e-12, max(1e-12, p)))
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


def layer_bit(sym: np.ndarray, layer_idx: int, bits: int = N_LAYERS) -> np.ndarray:
    """Extract bit-plane `layer_idx` (0=MSB) from an int array of symbols in
    [0, 2**bits). Matches scripts.m2_prior_validation's / the frozen
    baseline's own `shift = bits - 1 - layer_idx` convention verbatim."""
    shift = bits - 1 - int(layer_idx)
    return ((np.asarray(sym, dtype=np.int64) >> shift) & 1).astype(np.int8)


def layer_ber(sym_a: np.ndarray, sym_b: np.ndarray, layer_idx: int, bits: int = N_LAYERS) -> float:
    a = layer_bit(sym_a, layer_idx, bits)
    b = layer_bit(sym_b, layer_idx, bits)
    return float(np.mean(a != b))


def freeze_one_layer_rate(
    *, ber: float, margin: float, n: int, n_log: int, order: np.ndarray,
    fns: dict, fer_thresh: float, n_frames: int,
) -> dict:
    """Reuse the frozen baseline's own margin-based rate search
    (`_build_candidates` + `_simulate_layer_sc_fer_early`, SC/memoryless-BSC
    FER calibration) to find the largest k meeting `fer_thresh` at this
    layer's CAL32-estimated BER and this `margin`. Returns k=0 if none of
    the candidates qualify (layer effectively unusable at this margin)."""
    cap = 1.0 - h2(ber)
    k_base = int(math.floor(float(n) * max(0.0, cap - float(margin))))
    if k_base <= 16:
        return {"k": 0, "info_idx": np.zeros(0, dtype=np.int64), "cap": cap, "fer": None}
    max_err_allowed = int(math.floor(fer_thresh * n_frames - 1e-12))
    for k in fns["build_candidates"](k_base=k_base, n=n):
        info_idx = np.asarray(order[:k], dtype=np.int64)
        mask = np.zeros(n, dtype=np.int8)
        mask[info_idx] = 1
        fer = float(
            fns["simulate_layer_sc_fer_early"](
                float(ber), int(n), int(k), info_idx, mask, int(n_frames), LLR_CLIP, int(n_log), max_err_allowed
            )
        )
        if fer < fer_thresh:
            return {"k": int(k), "info_idx": info_idx, "cap": cap, "fer": fer}
    return {"k": 0, "info_idx": np.zeros(0, dtype=np.int64), "cap": cap, "fer": 1.0}


def freeze_binary_construction(
    *, layer_bers: list[float], order: np.ndarray, fns: dict,
    target_f: float, h_total_bits: float, tag_bits: int,
    n_symbols: int = 32768, rng_seed: int = 0,
) -> dict:
    """Search sc_margin (a single global knob, matching the frozen
    baseline's own CLI `--sc-margin`, applied uniformly across all 10
    layers) to find: (1) the margin whose resulting f_book_sc is closest to
    `target_f`, and (2) up to MAX_F_POINTS-1 further margins bracketing the
    SC-arm FER<=0.05 crossover (coarse crossover: "does every layer's
    calibrated per-margin FER stay < FER_THRESH", which is what the k-search
    already enforces per layer -- so the "crossover" swept here is in
    ACHIEVED RATE / f, using the SAME frozen per-layer FER<0.05 acceptance
    criterion the baseline itself uses, per PI item 5(b)). CAL32-data-only:
    the caller must pass `layer_bers` computed ONLY from CAL32 symbols."""
    margins = list(SC_MARGIN_CANDIDATES)
    points: list[dict] = []
    for margin in margins:
        layers = []
        total_frozen_bits_sc = 0
        total_frozen_bits_scl = 0
        all_layers_ok = True
        for layer_idx, ber in enumerate(layer_bers):
            r = freeze_one_layer_rate(
                ber=ber, margin=float(margin), n=LAYER_N, n_log=LAYER_N_LOG, order=order,
                fns=fns, fer_thresh=FER_THRESH, n_frames=CALIB_N_FRAMES,
            )
            k = int(r["k"])
            if k <= 16:
                all_layers_ok = False
            frozen_sc = (LAYER_N - k) * CODEWORDS_PER_LAYER
            frozen_scl = frozen_sc + CRC_BITS * CODEWORDS_PER_LAYER if k > 16 else frozen_sc
            total_frozen_bits_sc += frozen_sc
            total_frozen_bits_scl += frozen_scl
            layers.append({"layer_idx": layer_idx, "ber": ber, "cap": r["cap"], "k": k, "fer_calibrated": r["fer"]})
        kdb_sc = total_frozen_bits_sc + int(tag_bits)
        kdb_scl = total_frozen_bits_scl + int(tag_bits)
        f_sc = kdb_sc / (h_total_bits * n_symbols)
        f_scl = kdb_scl / (h_total_bits * n_symbols)
        points.append({
            "sc_margin": float(margin), "all_layers_usable": bool(all_layers_ok),
            "kdb_sc": int(kdb_sc), "kdb_scl": int(kdb_scl),
            "f_book_sc": float(f_sc), "f_book_scl": float(f_scl),
            "layers": layers,
        })
    usable = [p for p in points if p["all_layers_usable"]]
    if not usable:
        return {"target_point": None, "grid_points": [], "all_points_considered": points, "status": "NO_USABLE_MARGIN"}
    # (a) closest to target_f (by the SC-arm f, the primary/claim-bearing arm)
    target_point = min(usable, key=lambda p: abs(p["f_book_sc"] - target_f))
    # (b) up to MAX_F_POINTS-1 more points spanning the usable margin range,
    # descriptively bracketing the FER<=0.05-achieving region (every usable
    # point already satisfies FER<0.05 per layer by construction of the
    # search above; "bracketing" here means spanning low-f/high-f usable
    # extremes plus one midpoint, giving the main thread a monotonic f-vs-
    # achievability curve rather than a single point).
    usable_sorted = sorted(usable, key=lambda p: p["f_book_sc"])
    extra: list[dict] = []
    if len(usable_sorted) > 1:
        candidates_idx = sorted(set([0, len(usable_sorted) // 2, len(usable_sorted) - 1]))
        for i in candidates_idx:
            p = usable_sorted[i]
            if p is not target_point and p not in extra:
                extra.append(p)
    grid = [target_point] + [p for p in extra if p is not target_point]
    grid = grid[:MAX_F_POINTS]
    return {
        "target_f": float(target_f), "target_point": target_point,
        "grid_points": grid, "n_grid_points": len(grid),
        "status": "OK",
    }


def sc_decode_codeword(
    *, a_bits: np.ndarray, b_bits: np.ndarray, ber: float, info_idx: np.ndarray,
    fns: dict, n_log: int = LAYER_N_LOG, n: int = LAYER_N,
) -> dict:
    """Real per-codeword SC reconciliation decode (primary arm). Returns the
    reconstructed bit vector, exactness, and disclosed-bit count. Pure
    function of its inputs; no randomness, no I/O."""
    u_a = fns["polar_encode_non_systematic"](np.asarray(a_bits, dtype=np.int8), int(n_log))
    mask = np.zeros(n, dtype=np.int8)
    mask[info_idx] = 1
    p = float(min(1.0 - 1e-6, max(1e-6, float(ber))))
    lam = float(math.log((1.0 - p) / p))
    b_bits = np.asarray(b_bits, dtype=np.int8)
    llr = np.where(b_bits == 0, lam, -lam).astype(np.float64)
    llr = np.clip(llr, -LLR_CLIP, LLR_CLIP)
    u_hat = fns["polar_sc_decode_with_frozen"](llr, mask, u_a.astype(np.int8), int(n_log))
    a_hat_bits = fns["polar_encode_non_systematic"](u_hat, int(n_log))
    exact = bool(np.array_equal(a_hat_bits, np.asarray(a_bits, dtype=np.int8)))
    disclosed_bits = int(n - int(np.sum(mask)))
    return {"a_hat_bits": a_hat_bits, "exact": exact, "disclosed_bits": disclosed_bits}


def scl_descriptive_codeword(
    *, a_bits: np.ndarray, b_bits: np.ndarray, ber: float, info_idx: np.ndarray,
    fns: dict, decoder, n_log: int = LAYER_N_LOG, n: int = LAYER_N,
) -> dict:
    """Real per-codeword CA-SCL descriptive decode (secondary arm). The last
    16 (ascending-index) info positions are OVERWRITTEN with CRC(message) --
    see module docstring for why. Returns message-exact-match only (not a
    block-level accept/tag arm)."""
    info_idx_sorted = np.sort(np.asarray(info_idx, dtype=np.int64))
    k = int(info_idx_sorted.size)
    if k <= CRC_BITS:
        return {"applicable": False}
    msg_len = k - CRC_BITS
    u_a = fns["polar_encode_non_systematic"](np.asarray(a_bits, dtype=np.int8), int(n_log))
    msg_true = u_a[info_idx_sorted[:msg_len]]
    crc_true = np.asarray(fns["calc_crc16"](msg_true), dtype=np.int8)
    mask = np.zeros(n, dtype=np.uint8)
    mask[info_idx_sorted] = 1
    p = float(min(1.0 - 1e-6, max(1e-6, float(ber))))
    lam = float(math.log((1.0 - p) / p))
    b_bits = np.asarray(b_bits, dtype=np.int8)
    llr = np.where(b_bits == 0, lam, -lam).astype(np.float32)
    llr = np.clip(llr, -LLR_CLIP, LLR_CLIP).reshape(1, n)
    out_bits = decoder.decode_batch(int(n), int(k), 1, mask, llr)[0]
    msg_hat = out_bits[:msg_len]
    msg_exact = bool(np.array_equal(msg_hat, msg_true))
    disclosed_bits = int(n - k) + CRC_BITS
    return {"applicable": True, "msg_exact": msg_exact, "disclosed_bits": disclosed_bits}


def block_tag_check(
    *, a_true_bits_full: np.ndarray, a_hat_bits_full: np.ndarray,
    point_id: str, block_index: int, tag_bits: int, fns: dict,
) -> dict:
    """One per-block Toeplitz-style universal-hash tag check (frozen
    ``src.reconciliation.verification.universal_hash_tag``, layer_id=0 by
    convention since this is a whole-block tag, not a per-layer one)."""
    ref_tag = fns["universal_hash_tag"](
        bits=np.asarray(a_true_bits_full, dtype=np.uint8), point_id=point_id, layer_id=0,
        block_index=int(block_index), tag_bits=int(tag_bits),
    )
    cand_tag = fns["universal_hash_tag"](
        bits=np.asarray(a_hat_bits_full, dtype=np.uint8), point_id=point_id, layer_id=0,
        block_index=int(block_index), tag_bits=int(tag_bits),
    )
    tag_pass = bool(np.array_equal(ref_tag, cand_tag))
    return {"tag_pass": tag_pass, "tag_bits": int(tag_bits)}


def block_hash(sym_a: np.ndarray, sym_b: np.ndarray) -> dict:
    """SHA-256 of the raw (x,y) symbol arrays for this block -- cross-check
    evidence that this driver's session reconstruction produced the SAME
    symbols as workspace/r2_fer_shg_64/'s (by code-path construction, since
    both call the identical imported `_reproduce_session_context`; this hash
    is recorded per PI's explicit request, not because equality is in doubt)."""
    a = np.asarray(sym_a, dtype=np.int64)
    b = np.asarray(sym_b, dtype=np.int64)
    return {
        "sha256_alice": hashlib.sha256(a.tobytes()).hexdigest(),
        "sha256_bob": hashlib.sha256(b.tobytes()).hexdigest(),
        "n_symbols": int(a.size),
    }


def decode_block_all_layers(
    *, sym_a: np.ndarray, sym_b: np.ndarray, grid_point: dict, fns: dict,
    scl_decoder=None, run_scl: bool = True, run_sc: bool = True,
) -> dict:
    """(D_BIN_TWO_PASS) pass 1 calls this with run_sc=True, run_scl=False; pass 2
    with run_sc=False, run_scl=True. Decode one full 32768-symbol block (all 10 layers x 8 codewords) at
    one frozen grid point (sc_margin/k/info_idx per layer). Returns the SC
    reconstruction (for the block-level tag check, done by the caller) plus
    per-layer/per-codeword descriptive stats for both arms."""
    n_bits = 10
    layer_records = []
    a_hat_layers = np.zeros((n_bits, sym_a.size), dtype=np.int8)
    sc_disclosed_total = 0
    scl_disclosed_total = 0
    for layer_idx, layer_cfg in enumerate(grid_point["layers"]):
        ber = float(layer_cfg["ber"])
        k = int(layer_cfg["k"])
        a_full = layer_bit(sym_a, layer_idx, n_bits)
        b_full = layer_bit(sym_b, layer_idx, n_bits)
        n_cw = CODEWORDS_PER_LAYER
        cw_records = []
        for cw in range(n_cw):
            s, e = cw * LAYER_N, (cw + 1) * LAYER_N
            a_bits = a_full[s:e]
            b_bits = b_full[s:e]
            if k <= 16:
                a_hat_layers[layer_idx, s:e] = a_bits  # unusable layer: not attempted, recorded as-is (0 disclosed via SC path skipped)
                cw_records.append({"cw": cw, "sc_exact": None, "sc_disclosed_bits": 0, "scl": {"applicable": False}})
                continue
            order = grid_point["_order"]
            info_idx = np.asarray(order[:k], dtype=np.int64)
            if run_sc:
                sc_res = sc_decode_codeword(
                    a_bits=a_bits, b_bits=b_bits, ber=ber, info_idx=info_idx, fns=fns,
                    n_log=LAYER_N_LOG, n=LAYER_N,
                )
                a_hat_layers[layer_idx, s:e] = sc_res["a_hat_bits"]
                sc_disclosed_total += sc_res["disclosed_bits"]
            else:
                sc_res = {"exact": None, "disclosed_bits": 0}
            scl_res = {"applicable": False}
            if run_scl and scl_decoder is not None:
                scl_res = scl_descriptive_codeword(
                    a_bits=a_bits, b_bits=b_bits, ber=ber, info_idx=info_idx, fns=fns, decoder=scl_decoder,
                    n_log=LAYER_N_LOG, n=LAYER_N,
                )
                if scl_res.get("applicable"):
                    scl_disclosed_total += scl_res["disclosed_bits"]
            cw_records.append({
                "cw": cw, "sc_exact": sc_res["exact"], "sc_disclosed_bits": sc_res["disclosed_bits"], "scl": scl_res,
            })
        layer_records.append({"layer_idx": layer_idx, "ber": ber, "k": k, "codewords": cw_records})
    a_hat_sym = np.zeros(sym_a.size, dtype=np.int64)
    for layer_idx in range(n_bits):
        a_hat_sym |= (a_hat_layers[layer_idx].astype(np.int64) << (n_bits - 1 - layer_idx))
    return {
        "a_hat_sym": a_hat_sym, "layers": layer_records,
        "sc_disclosed_total": sc_disclosed_total, "scl_disclosed_total": scl_disclosed_total,
    }


def _wilson(k: int, n: int, z: float = 1.96) -> dict:
    if n <= 0:
        return {"k": k, "n": n, "z": z, "p_hat": None, "lower": None, "upper": None}
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * ((p * (1.0 - p) / n + z * z / (4.0 * n * n)) ** 0.5) / denom
    return {"k": k, "n": n, "z": z, "p_hat": p, "lower": max(0.0, center - half), "upper": min(1.0, center + half)}


# ---------------------------------------------------------------------------
# Real-data entrypoints (guarded; do not run without authorization).
# ---------------------------------------------------------------------------

DRY_RUN_DIR = THIS_DIR / "dry_run"


def _part_path(global_block_index: int, session: str, *, dry_run: bool = False) -> Path:
    """F3 (Pre-EXECUTE round 1): dry-run output goes under `dry_run/`, NEVER
    at the top level, so it can never be mistaken for -- or collide with --
    a full run's own part files."""
    base = DRY_RUN_DIR if dry_run else THIS_DIR
    return base / f"part_{session}_{global_block_index:02d}.json"


def _construction_path(session: str, *, dry_run: bool = False) -> Path:
    base = DRY_RUN_DIR if dry_run else THIS_DIR
    return base / f"construction_frozen_{session}.json"


def _peak_rss_gib() -> float | None:
    """C1 (Pre-EXECUTE round 1): advisory RSS reading, same mechanism as
    `workspace/r2_fer_shg_64/run.py::_peak_rss_gib` (VmHWM from
    `/proc/self/status`, WSL/Linux only). Cheap (a few lines, no new
    dependency), so implemented rather than left purely as a documentation
    caveat -- but it is still ADVISORY: it reads the WHOLE WORKER
    PROCESS's peak RSS since process start, not a per-grid-point delta, so
    a budget breach is attributed to "this grid point's check point", not
    proven to have been CAUSED by that specific grid point alone."""
    try:
        with open("/proc/self/status", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    return float(line.split()[1]) / 1024.0**2
    except Exception:
        pass
    return None


def _run_one_block_entry(block: dict, grid_points: list[dict], *, dry_run: bool = False):
    session = block["session"]
    t0 = time.perf_counter()
    status = "ok"
    error = None
    per_grid_point = []
    try:
        ctx = _CTX[session]
        fns = _CTX["_fns"]
        s, e = block["frame_start"], block["frame_end"]
        sym_a = ctx["frames_a"][s : e + 1].ravel()
        sym_b = ctx["frames_b"][s : e + 1].ravel()
        bh = block_hash(sym_a, sym_b)
        for gp in grid_points:
            elapsed_so_far = time.perf_counter() - t0
            if elapsed_so_far > BUDGET_WALL_S_PER_BLOCK:
                per_grid_point.append({"sc_margin": gp["sc_margin"], "status": "resource_abort_wall_mid_grid"})
                continue
            # pass 1 = SC primary arm ONLY (D_BIN_TWO_PASS); CA-SCL runs later, in pass 2
            dec = decode_block_all_layers(sym_a=sym_a, sym_b=sym_b, grid_point=gp, fns=fns, scl_decoder=None, run_scl=False)
            tag = _block_bits_and_tag(
                sym_a=sym_a, a_hat_sym=dec["a_hat_sym"], gp=gp, block=block, ctx=ctx, fns=fns,
            )
            exact = bool(tag["tag_pass"] and np.array_equal(dec["a_hat_sym"], sym_a))
            accepted = bool(tag["tag_pass"])
            undetected = bool(accepted and not exact)
            verify_failed = bool(not accepted)
            rss_gib = _peak_rss_gib()
            # C1 (Pre-EXECUTE round 1): advisory RSS check after each grid
            # point. Over-budget => resource_abort (excluded from D by
            # `_binary_taxonomy_counts`'s ok-only rule), but the computed
            # fields are still recorded (audit trail), matching the
            # existing wall-budget precedent's own non-silent-drop style.
            gp_status = "ok"
            if rss_gib is not None and rss_gib > BUDGET_RSS_GIB_PER_BLOCK:
                gp_status = "resource_abort_rss_post_decode"
            per_grid_point.append({
                "sc_margin": gp["sc_margin"],
                "status": gp_status,
                "sc_disclosed_total": dec["sc_disclosed_total"],
                "tag_pass": tag["tag_pass"],
                "accepted": accepted,
                "exact": exact,
                "undetected": undetected,
                "verify_failed": verify_failed,
                "decode_failed": False,
                "rss_gib_peak_advisory": rss_gib,
                "budget_rss_gib_per_block": BUDGET_RSS_GIB_PER_BLOCK,
            })
    except Exception as exc:
        status = f"error:{type(exc).__name__}"
        error = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        bh = None
    wall_total_s = time.perf_counter() - t0
    record = {
        "session": block["session"], "global_block_index": block["global_block_index"],
        "frame_start": block["frame_start"], "frame_end": block["frame_end"],
        "stratum_official": block.get("stratum_official"), "stratum_task": block.get("stratum_task"),
        "status": status, "block_hash": bh, "grid": per_grid_point, "error": error,
        "resources": {"wall_total_s": wall_total_s, "budget_wall_s_per_block": BUDGET_WALL_S_PER_BLOCK},
        "dry_run": dry_run,
    }
    if dry_run:
        record["note"] = (
            "DRY-RUN TIMING PROBE ONLY. NOT counted in any results.json. A full authorized run "
            "independently re-decodes this exact block into the top-level part_*.json file; that "
            "re-decode is NOT skipped and NOT read from this dry_run/ file (this file is never "
            "read back by any code path)."
        )
    with open(_part_path(block["global_block_index"], session, dry_run=dry_run), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


def _scl_part_path(global_block_index: int, session: str, *, dry_run: bool = False) -> Path:
    """Pass-2 (CA-SCL secondary arm) records live in `scl_part_*.json`, a
    SEPARATE file per block, so pass-1 `part_*.json` files are never
    rewritten (additive-only)."""
    base = DRY_RUN_DIR if dry_run else THIS_DIR
    return base / f"scl_part_{session}_{global_block_index:02d}.json"


CA_SCL_NOT_STARTED = "ca_scl_not_started_total_wall_budget"


def _write_scl_part(block: dict, grid_entries: list, *, status: str, dry_run: bool, extra: dict | None = None) -> None:
    record = {
        "session": block["session"], "global_block_index": block["global_block_index"],
        "frame_start": block["frame_start"], "frame_end": block["frame_end"],
        "status": status, "grid": grid_entries, "dry_run": dry_run, "pass": 2, "arm": "ca_scl_descriptive",
    }
    if extra:
        record.update(extra)
    with open(_scl_part_path(block["global_block_index"], block["session"], dry_run=dry_run), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


def _run_scl_block_entry(block: dict, grid_points: list, *, dry_run: bool = False):
    """Pass 2 for one block: CA-SCL descriptive arm ONLY (no SC re-decode, no
    tag). Per-block wall (cumulative) and RSS checks as in pass 1."""
    session = block["session"]
    t0 = time.perf_counter()
    status = "ok"
    error = None
    entries = []
    try:
        ctx = _CTX[session]
        fns = _CTX["_fns"]
        scl_decoder = ctx.get("scl_decoder")
        s, e = block["frame_start"], block["frame_end"]
        sym_a = ctx["frames_a"][s : e + 1].ravel()
        sym_b = ctx["frames_b"][s : e + 1].ravel()
        for gp in grid_points:
            if time.perf_counter() - t0 > BUDGET_WALL_S_PER_BLOCK:
                entries.append({"sc_margin": gp["sc_margin"], "status": "resource_abort_wall_mid_grid"})
                continue
            if scl_decoder is None:
                entries.append({"sc_margin": gp["sc_margin"], "status": "ca_scl_unavailable"})
                continue
            dec = decode_block_all_layers(
                sym_a=sym_a, sym_b=sym_b, grid_point=gp, fns=fns, scl_decoder=scl_decoder, run_scl=True, run_sc=False,
            )
            rss_gib = _peak_rss_gib()
            gp_status = "ok"
            if rss_gib is not None and rss_gib > BUDGET_RSS_GIB_PER_BLOCK:
                gp_status = "resource_abort_rss_post_decode"
            entries.append({
                "sc_margin": gp["sc_margin"], "status": gp_status,
                "scl_disclosed_total": dec["scl_disclosed_total"],
                "ca_scl_descriptive": _scl_descriptive_summary(dec),
                "rss_gib_peak_advisory": rss_gib,
            })
    except Exception as exc:
        status = f"error:{type(exc).__name__}"
        error = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
    _write_scl_part(
        block, entries, status=status, dry_run=dry_run,
        extra={"error": error, "resources": {"wall_total_s": time.perf_counter() - t0}},
    )


def _total_wall_exceeded(t_start: float) -> bool:
    """F4 (Pre-EXECUTE round 2): in-code total-wall check, measured from the
    start of main() on the `_now()` monotonic clock."""
    return (_now() - t_start) > BUDGET_WALL_S_TOTAL


def _write_not_started_part(block: dict, *, elapsed_s: float, where: str, dry_run: bool = False) -> None:
    """Record a block that was NOT started because the total wall budget was
    exhausted. No grid results; never enters D; counted separately."""
    record = {
        "session": block["session"], "global_block_index": block["global_block_index"],
        "frame_start": block["frame_start"], "frame_end": block["frame_end"],
        "stratum_official": block.get("stratum_official"), "stratum_task": block.get("stratum_task"),
        "status": NOT_STARTED_STATUS, "block_hash": None, "grid": [], "error": None,
        "not_started_detail": {
            "checked_at": where, "elapsed_total_wall_s": elapsed_s, "budget_wall_s_total": BUDGET_WALL_S_TOTAL,
        },
        "resources": {"wall_total_s": 0.0, "budget_wall_s_per_block": BUDGET_WALL_S_PER_BLOCK},
        "dry_run": dry_run,
    }
    with open(_part_path(block["global_block_index"], block["session"], dry_run=dry_run), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)


def _run_sessions(sessions, blocks_fn, prepare_fn, t_start: float, *, dry_run: bool = False) -> dict:
    """Serial two-pass driver (D_BIN_TWO_PASS).

    PASS 1 (SC primary arm only): for each session, total-wall check BEFORE
    its construction (exceeded => none of its blocks start, all recorded
    not_started, no construction); construction via `prepare_fn(session)`
    (wall time recorded); then, over all constructed sessions' blocks, a
    total-wall check BEFORE each block (running block never interrupted;
    later blocks recorded not_started).

    PASS 2 (CA-SCL secondary arm, descriptive): only for blocks whose pass-1
    part is status=="ok". Total-wall check BEFORE each block; once exceeded
    the block's not-yet-run entries are recorded as
    status="ca_scl_not_started_total_wall_budget" in `scl_part_*.json`. This
    never touches pass-1 records, D or Table A/B1.

    Returns {"grid_by_session","construction_wall_s","not_started",
    "pass1_wall_s","pass2_wall_s","pass2_blocks_run","pass2_blocks_not_started"}."""
    grid_by_session: dict = {}
    construction_wall_s: dict = {}
    not_started: list = []
    targets_by_session: dict = {}
    t_p1 = _now()
    for session in sessions:
        blocks_meta = blocks_fn(session)
        targets = blocks_meta[:1] if dry_run else blocks_meta
        targets_by_session[session] = targets
        if _total_wall_exceeded(t_start):
            for block in targets:
                _write_not_started_part(block, elapsed_s=_now() - t_start, where="before_construction", dry_run=dry_run)
                not_started.append({"session": block["session"], "global_block_index": block["global_block_index"]})
            print(f"[budget] total wall exceeded before {session} construction; {len(targets)} blocks not started", file=sys.stderr)
            targets_by_session[session] = []
            if dry_run:
                break
            continue
        t_c = _now()
        grid_by_session[session] = prepare_fn(session)
        construction_wall_s[session] = _now() - t_c
        if dry_run:
            break
    ran_blocks: list = []  # pass-1 blocks that actually ran (candidates for pass 2)
    for session in sessions:
        for block in targets_by_session.get(session, []):
            if _total_wall_exceeded(t_start):
                _write_not_started_part(block, elapsed_s=_now() - t_start, where="before_block", dry_run=dry_run)
                not_started.append({"session": block["session"], "global_block_index": block["global_block_index"]})
                continue
            _run_one_block_entry(block, grid_by_session[session].get("grid_points", []), dry_run=dry_run)
            ran_blocks.append(block)
            print(f"[pass1 SC] {session} idx={block['global_block_index']} done", file=sys.stderr)
    pass1_wall_s = _now() - t_p1

    t_p2 = _now()
    p2_run = 0
    p2_not_started = 0
    for block in ran_blocks:
        gps = grid_by_session[block["session"]].get("grid_points", [])
        part_file = _part_path(block["global_block_index"], block["session"], dry_run=dry_run)
        try:
            with open(part_file, "r", encoding="utf-8") as fh:
                p1_status = json.load(fh).get("status")
        except Exception:
            p1_status = None
        if p1_status != "ok" or not gps:
            continue  # nothing to do in pass 2 for error / no-grid blocks
        if _total_wall_exceeded(t_start):
            _write_scl_part(
                block, [{"sc_margin": gp["sc_margin"], "status": CA_SCL_NOT_STARTED} for gp in gps],
                status=CA_SCL_NOT_STARTED, dry_run=dry_run,
                extra={"elapsed_total_wall_s": _now() - t_start, "budget_wall_s_total": BUDGET_WALL_S_TOTAL},
            )
            p2_not_started += 1
            continue
        _run_scl_block_entry(block, gps, dry_run=dry_run)
        p2_run += 1
        print(f"[pass2 CA-SCL] {block['session']} idx={block['global_block_index']} done", file=sys.stderr)
    pass2_wall_s = _now() - t_p2
    return {
        "grid_by_session": grid_by_session, "construction_wall_s": construction_wall_s, "not_started": not_started,
        "pass1_wall_s": pass1_wall_s, "pass2_wall_s": pass2_wall_s,
        "pass2_blocks_run": p2_run, "pass2_blocks_not_started": p2_not_started,
    }


def _symbols_to_bits(sym: np.ndarray, bits: int = N_LAYERS) -> np.ndarray:
    """MSB-first bit-serialization of a symbol array, one column per layer
    (matches `layer_bit`'s own convention exactly -- reused, not
    re-derived). Shape (n_symbols, bits) flattened to (n_symbols*bits,)."""
    cols = [layer_bit(sym, i, bits) for i in range(bits)]
    return np.stack(cols, axis=1).reshape(-1)


def _block_bits_and_tag(*, sym_a, a_hat_sym, gp, block, ctx, fns) -> dict:
    a_true_full = _symbols_to_bits(sym_a)
    a_hat_full = _symbols_to_bits(a_hat_sym)
    return block_tag_check(
        a_true_bits_full=a_true_full, a_hat_bits_full=a_hat_full,
        point_id=f"r2-binary-baseline-shg64-margin{gp['sc_margin']}",
        block_index=block["global_block_index"], tag_bits=ctx["tag_bits"], fns=fns,
    )


def _scl_descriptive_summary(dec: dict) -> dict:
    """CA-SCL secondary arm: descriptive codeword-level message-exact rate
    for one block at one grid point. NO block-level accept/tag/exact is
    computed for CA-SCL (see module docstring -- the 16 CRC-slot positions
    per codeword are genuine data positions that are OVERWRITTEN with
    CRC(message), never attempted to be reconciled, so a "full block
    exact" is not a well-defined quantity for this arm as scoped). We
    report only: how many codewords were applicable (k>16), how many had
    an exact message-bit match, and a DERIVED, EXPLICITLY-CAVEATED
    `all_applicable_msg_exact` flag (true iff every applicable codeword in
    this block had an exact message match) used ONLY as an approximate,
    labeled-as-such proxy in the cross-comparison Table B (see
    `build_cross_comparison`) -- never as a substitute for a true
    full-block reconciliation claim."""
    n_applicable = 0
    n_msg_exact = 0
    for layer in dec["layers"]:
        for cw in layer["codewords"]:
            scl = cw.get("scl") or {}
            if scl.get("applicable"):
                n_applicable += 1
                if scl.get("msg_exact"):
                    n_msg_exact += 1
    return {
        "n_codewords_applicable": n_applicable,
        "n_codewords_msg_exact": n_msg_exact,
        "msg_exact_rate": (n_msg_exact / n_applicable) if n_applicable > 0 else None,
        "all_applicable_msg_exact": bool(n_applicable > 0 and n_msg_exact == n_applicable),
    }


# ---------------------------------------------------------------------------
# Aggregation (results.json). Reads ONLY this packet's own part files
# (written by `_run_one_block_entry` above) and its own
# `construction_frozen_<SESSION>.json` files. Follows, verbatim, the
# already-reviewed `workspace/r2_fer_shg_64/run.py::_taxonomy_counts`
# convention (Pre-EXECUTE F1 fix, main thread 2026-09-28): only
# `status=="ok"` entries enter the taxonomy/`D`; `resource_abort`/`error`
# are scanned over ALL entries, never silently dropped, never merged into
# `D`. `undetected` is scanned over ALL entries regardless of status, same
# as the NB packet's own `stop_undetected` security-signal convention.
# ---------------------------------------------------------------------------

def _load_all_part_records(this_dir: Path = THIS_DIR) -> list[dict]:
    """Top-level part files ONLY (`Path.glob`, non-recursive, does not
    descend into `dry_run/`). Belt-and-suspenders: also explicitly drops
    any record that somehow carries `dry_run=True`, so a future refactor
    mistake cannot silently mix a timing-probe block into real results."""
    records = []
    for p in sorted(this_dir.glob("part_*.json")):
        with open(p, "r", encoding="utf-8") as fh:
            rec = json.load(fh)
        if rec.get("dry_run"):
            raise AssertionError(f"{p}: dry_run=True record found at top level; this must never happen")
        records.append(rec)
    return records


def _load_all_scl_records(this_dir: Path = THIS_DIR) -> list:
    """Pass-2 (CA-SCL) records: top-level `scl_part_*.json` only (non-recursive)."""
    records = []
    for p in sorted(this_dir.glob("scl_part_*.json")):
        with open(p, "r", encoding="utf-8") as fh:
            rec = json.load(fh)
        if rec.get("dry_run"):
            raise AssertionError(f"{p}: dry_run=True record found at top level; this must never happen")
        records.append(rec)
    return records


def _scl_index(scl_records: list) -> dict:
    """{(session, global_block_index, margin): entry} for every pass-2 grid entry."""
    idx = {}
    for rec in scl_records or []:
        for g in rec.get("grid", []):
            idx[(rec["session"], int(rec["global_block_index"]), float(g["sc_margin"]))] = g
    return idx


def _load_construction_frozen(session: str, this_dir: Path = THIS_DIR) -> dict | None:
    p = this_dir / f"construction_frozen_{session}.json"
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _all_margins_present(records: list[dict]) -> list[float]:
    seen = set()
    for rec in records:
        if rec.get("status") != "ok":
            continue
        for g in rec.get("grid", []):
            seen.add(float(g["sc_margin"]))
    return sorted(seen)


def _binary_taxonomy_counts(entries: list[dict]) -> dict:
    """`entries`: list of per-(block,margin) dicts carrying at least
    `status`/`exact`/`verify_failed`/`decode_failed`/`undetected`. Mirrors
    `workspace/r2_fer_shg_64/run.py::_taxonomy_counts` exactly (same field
    names, same ok-only-into-D rule, same resource_abort/error/undetected
    isolation), generalized from "per block" to "per (block, margin)
    entry"."""
    ok = [e for e in entries if e.get("status") == "ok"]
    exact = sum(1 for e in ok if e.get("exact"))
    verify_failed = sum(1 for e in ok if e.get("verify_failed"))
    decode_failed = sum(1 for e in ok if e.get("decode_failed"))
    # `undetected` is a security signal and must be scanned regardless of
    # `status` (an entry can carry `undetected=True` and still have its
    # status overridden to `resource_abort_rss_post_decode` by the RSS
    # check AFTER the tag decision was already made -- the security signal
    # must not be suppressed by that later, unrelated budget bookkeeping;
    # same class of fix as workspace/r2_fer_shg_64/run.py's own Pre-EXECUTE
    # round-1 F1 fix).
    undetected = sum(1 for e in entries if e.get("undetected"))
    resource_abort = sum(1 for e in entries if "resource_abort" in str(e.get("status")))
    errors = sum(1 for e in entries if str(e.get("status", "")).startswith("error"))
    d = exact + verify_failed + decode_failed
    p_hat = (verify_failed + decode_failed) / d if d > 0 else None
    return {
        "n_entries": len(entries),
        "exact": exact,
        "verify_failed": verify_failed,
        "decode_failed": decode_failed,
        "undetected": undetected,
        "resource_abort": resource_abort,
        "error": errors,
        "D_valid_denominator": d,
        "p_hat": p_hat,
        "wilson_95ci": _wilson(verify_failed + decode_failed, d) if d > 0 else None,
    }


def _entries_at_margin(records: list[dict], margin: float, *, session: str | None = None,
                        stratum_official: str | None = None, stratum_task: str | None = None) -> list[dict]:
    out = []
    for rec in records:
        # Same convention as workspace/r2_fer_shg_64/run.py::_taxonomy_counts:
        # only block-level status=="ok" blocks enter the per-margin tallies
        # (error:* and not_started blocks are listed in block_accounting;
        # their partial grids are NOT tallied here; the undetected security
        # scan in aggregate_results still covers ALL records).
        if rec.get("status") != "ok":
            continue
        if session is not None and rec.get("session") != session:
            continue
        if stratum_official is not None and rec.get("stratum_official") != stratum_official:
            continue
        if stratum_task is not None and rec.get("stratum_task") != stratum_task:
            continue
        for g in rec.get("grid", []):
            if float(g["sc_margin"]) == float(margin):
                out.append(dict(g, _key=(rec["session"], int(rec["global_block_index"]))))
    return out


def _ca_scl_pooled_descriptive(sc_entries: list, scl_index: dict) -> dict:
    """CA-SCL descriptive coverage + codeword message-exact counts for a set
    of SC entries (`_entries_at_margin` output, carrying `_key`). Only SC
    entries with status=="ok" are the expected population. CA-SCL entries
    that never ran because of the total-wall budget
    (`ca_scl_not_started_total_wall_budget`) are counted separately and do
    NOT affect SC counts / D / Table A."""
    n_app = n_exact = 0
    n_sc_ok = n_ok = n_not_started = n_no_record = n_other = 0
    for e in sc_entries:
        if e.get("status") != "ok":
            continue
        n_sc_ok += 1
        hit = scl_index.get((e["_key"][0], e["_key"][1], float(e["sc_margin"])))
        if hit is None:
            n_no_record += 1
        elif hit.get("status") == "ok":
            n_ok += 1
            d = hit.get("ca_scl_descriptive") or {}
            n_app += int(d.get("n_codewords_applicable") or 0)
            n_exact += int(d.get("n_codewords_msg_exact") or 0)
        elif hit.get("status") == CA_SCL_NOT_STARTED:
            n_not_started += 1
        else:
            n_other += 1
    return {
        "n_codewords_applicable": n_app, "n_codewords_msg_exact": n_exact,
        "msg_exact_rate": (n_exact / n_app) if n_app > 0 else None,
        "n_sc_ok_entries": n_sc_ok,
        "n_ca_scl_ok_entries": n_ok,
        "n_ca_scl_not_started_entries": n_not_started,
        "n_ca_scl_no_record_entries": n_no_record,
        "n_ca_scl_other_entries": n_other,
        "coverage": (n_ok / n_sc_ok) if n_sc_ok > 0 else None,
    }


STRATUM_OFFICIAL_VALUES = ("A1_CAL_characterization", "HELDOUT_model_selection", "EVAL_already_decoded")
STRATUM_TASK_VALUES = ("never_decoded", "heldout_model_selection", "previously_decoded_eval")


def _block_category(rec: dict) -> str:
    """Mutually exclusive block-level category (precedence order) used for the
    64-block accounting: not_started > error > contributing (>=1 status=="ok"
    grid entry) > resource_abort (only aborted entries) > no_grid_entries."""
    status = str(rec.get("status", ""))
    if status == NOT_STARTED_STATUS:
        return "not_started"
    if status.startswith("error"):
        return "error"
    grid = rec.get("grid", [])
    if any(g.get("status") == "ok" for g in grid):
        return "contributing"
    if any("resource_abort" in str(g.get("status")) for g in grid):
        return "resource_abort"
    return "no_grid_entries"


def _block_accounting(records: list[dict], expected_blocks: int) -> dict:
    ids: dict[str, list] = {k: [] for k in ("contributing", "error", "not_started", "resource_abort", "no_grid_entries")}
    for rec in records:
        ids[_block_category(rec)].append({"session": rec["session"], "global_block_index": rec["global_block_index"]})
    n = {k: len(v) for k, v in ids.items()}
    total = sum(n.values())
    return {
        "expected_blocks": expected_blocks,
        "n_records": len(records),
        "n_blocks_contributing": n["contributing"],
        "n_error": n["error"],
        "n_not_started": n["not_started"],
        "n_resource_abort": n["resource_abort"],
        "n_no_grid_entries": n["no_grid_entries"],
        "sum_of_categories": total,
        "consistent": bool(total == expected_blocks and len(records) == expected_blocks),
        "identity": "expected_blocks = contributing + error + not_started + resource_abort + no_grid_entries (last should be 0)",
        "error_block_ids": ids["error"],
        "not_started_block_ids": ids["not_started"],
        "resource_abort_block_ids": ids["resource_abort"],
        "no_grid_entries_block_ids": ids["no_grid_entries"],
        "note": (
            "A block with >=1 status=='ok' grid entry is 'contributing' even if some of its other grid "
            "entries were resource_abort (those entries are counted in the per-margin resource_abort). "
            "not_started blocks never enter D and are counted separately."
        ),
    }


def aggregate_results(records: list[dict], constructions: dict[str, dict], expected_blocks: int = 64,
                      scl_records: list | None = None) -> dict:
    """Build the full `results.json` content from this packet's own part
    files + construction_frozen files only. `constructions`:
    {"G2": <construction dict>, "G3": <construction dict>}; a session that
    was never constructed (total wall exhausted first) may be absent."""
    margins = _all_margins_present(records)
    accounting = _block_accounting(records, expected_blocks)
    scl_idx = _scl_index(scl_records or [])

    # undetected is a security signal: scanned over ALL grid entries
    # regardless of `status` (e.g. a later RSS-triggered
    # `resource_abort_rss_post_decode` override must never suppress it --
    # see `_binary_taxonomy_counts`'s own comment).
    n_undetected_total = sum(
        1 for rec in records for g in rec.get("grid", []) if g.get("undetected")
    )
    stop_undetected = bool(n_undetected_total >= 1)
    undetected_ids = [
        {"session": rec["session"], "global_block_index": rec["global_block_index"], "sc_margin": g["sc_margin"]}
        for rec in records for g in rec.get("grid", []) if g.get("undetected")
    ]

    per_margin = []
    for margin in margins:
        pooled_entries = _entries_at_margin(records, margin)
        by_stratum_official = {
            s: _binary_taxonomy_counts(_entries_at_margin(records, margin, stratum_official=s))
            for s in STRATUM_OFFICIAL_VALUES
        }
        by_stratum_task = {
            s: _binary_taxonomy_counts(_entries_at_margin(records, margin, stratum_task=s))
            for s in STRATUM_TASK_VALUES
        }
        by_session = {}
        f_breakdown = {}
        for session in ("G2", "G3"):
            session_entries = _entries_at_margin(records, margin, session=session)
            by_session[session] = _binary_taxonomy_counts(session_entries)
            by_session[session]["ca_scl_descriptive"] = _ca_scl_pooled_descriptive(session_entries, scl_idx)
            cons = constructions.get(session) or {}
            gp_match = next(
                (gp for gp in cons.get("grid_points", []) if float(gp["sc_margin"]) == float(margin)), None
            )
            if gp_match is not None:
                f_breakdown[session] = {
                    "sc_margin": gp_match["sc_margin"],
                    "kdb_sc": gp_match["kdb_sc"],
                    "kdb_scl": gp_match["kdb_scl"],
                    "f_book_sc": gp_match["f_book_sc"],
                    "f_book_scl": gp_match["f_book_scl"],
                    "layers": [
                        {
                            "layer_idx": ly["layer_idx"], "ber": ly["ber"], "k": ly["k"],
                            "frozen_bits_per_codeword": LAYER_N - ly["k"] if ly["k"] > 16 else None,
                            "frozen_bits_total_sc": (LAYER_N - ly["k"]) * CODEWORDS_PER_LAYER if ly["k"] > 16 else 0,
                            "crc_bits_total_scl": CRC_BITS * CODEWORDS_PER_LAYER if ly["k"] > 16 else 0,
                        }
                        for ly in gp_match["layers"]
                    ],
                    "tag_bits": (
                        gp_match["kdb_sc"] - sum(
                            (LAYER_N - ly["k"]) * CODEWORDS_PER_LAYER for ly in gp_match["layers"] if ly["k"] > 16
                        )
                    ),
                }
            else:
                f_breakdown[session] = {"status": "margin_not_in_this_session_construction"}
        pooled = _binary_taxonomy_counts(pooled_entries)
        pooled["ca_scl_descriptive"] = _ca_scl_pooled_descriptive(pooled_entries, scl_idx)
        per_margin.append({
            "sc_margin": margin,
            # blocks with a status=="ok" entry at this margin (i.e. entering the taxonomy here)
            "n_blocks_contributing": len({(r["session"], r["global_block_index"]) for r in records if r.get("status") == "ok" for g in r.get("grid", []) if float(g["sc_margin"]) == float(margin) and g.get("status") == "ok"}),
            "insufficient": bool(pooled["D_valid_denominator"] < MIN_D_FOR_ESTIMATE),
            "insufficient_note": (
                f"INSUFFICIENT: pooled D={pooled['D_valid_denominator']} < {MIN_D_FOR_ESTIMATE} (D-FER-03); "
                "not_started/error/resource_abort blocks are not in D. A margin selected by only one "
                "session can never reach D>=56 (max 32)."
            ) if pooled["D_valid_denominator"] < MIN_D_FOR_ESTIMATE else None,
            "taxonomy_pooled": pooled,
            "taxonomy_by_stratum_official": by_stratum_official,
            "taxonomy_by_stratum_task": by_stratum_task,
            "taxonomy_by_session": by_session,
            "f_breakdown_by_session": f_breakdown,
        })

    return {
        "packet": "r2-binary-baseline-shg-64",
        "classification": (
            "Descriptive real-data comparison measurement (no win/lose threshold computed by this "
            "script; contract §5). NOT a Tier-Y decision gate. Requires independent Pre-EXECUTE AND "
            "Pre-RESULT review plus explicit PI authorization before any publication."
        ),
        "margins_present": margins,
        "stop_undetected": stop_undetected,
        "undetected_ids": undetected_ids,
        "block_accounting": accounting,
        "n_blocks_contributing": accounting["n_blocks_contributing"],
        "error_block_ids": accounting["error_block_ids"],
        "not_started_block_ids": accounting["not_started_block_ids"],
        "construction_search_wall_s_by_session": {
            sess: (constructions.get(sess) or {}).get("search_wall_s") for sess in ("G2", "G3")
        },
        "per_margin": per_margin,
        "ca_scl_arm_note": (
            "CA-SCL has NO block-level accept/tag/exact taxonomy: its internal CRC path-selection "
            "requires overwriting 16 real u-domain bits/codeword with CRC(message), so those "
            "positions are never attempted to be reconciled and a 'full block exact' is not a "
            "well-defined quantity for this arm as scoped. Only descriptive per-codeword "
            "message-exact rates are reported (taxonomy_by_session[*].ca_scl_descriptive, "
            "taxonomy_pooled.ca_scl_descriptive). D_BIN_TWO_PASS: CA-SCL is pass 2 (after the SC "
            "primary arm over all blocks); entries not run because the total wall budget ran out are "
            "marked ca_scl_not_started_total_wall_budget and reported as coverage < 1; they never "
            "affect the SC taxonomy, D, Table A or Table B1."
        ),
    }


# ---------------------------------------------------------------------------
# Cross-comparison against workspace/r2_fer_shg_64/ (read-only; that
# packet's own decode is NEVER re-run). Field-name/coverage assumptions
# below were confirmed empirically against the real, already-committed
# part_*.json files before writing this code (36/64 blocks carry
# `sc_descriptive`, the other 28/64 -- the EVAL_already_decoded stratum --
# carry the equivalent SC fields inside `fidelity.actual` instead; ALL
# 64 carry `scl`). See TASK_PACKET.md for the confirmation record.
# ---------------------------------------------------------------------------

NB_PART_GLOB = "part_*.json"


def load_nb_parts(nb_dir: Path = NB_PACKET_DIR) -> dict[tuple[str, int], dict]:
    """Read-only load of workspace/r2_fer_shg_64/'s own committed part
    files. Returns {(session, global_block_index): summary}."""
    out: dict[tuple[str, int], dict] = {}
    paths = sorted(nb_dir.glob(NB_PART_GLOB))
    for p in paths:
        with open(p, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        if d.get("sc_descriptive") is not None:
            sc_outcome = d["sc_descriptive"].get("outcome")
        elif d.get("fidelity") is not None:
            sc_outcome = d["fidelity"]["actual"].get("outcome")
        else:
            sc_outcome = None  # should not happen for any status=="ok" block; recorded, not silently assumed
        scl = d.get("scl") or {}
        key = (d["session"], int(d["global_block_index"]))
        out[key] = {
            "status": d.get("status"),
            "frame_start": d.get("frame_start"),
            "frame_end": d.get("frame_end"),
            "stratum_official": d.get("stratum_official"),
            "stratum_task": d.get("stratum_task"),
            "nb_sc_exact": (sc_outcome == "exact") if sc_outcome is not None else None,
            "nb_sc_outcome": sc_outcome,
            "nb_scl_exact": bool(scl.get("exact")) if d.get("status") == "ok" else None,
            "nb_scl_undetected": bool(scl.get("undetected")) if d.get("status") == "ok" else None,
        }
    return out


def _contingency_2x2(pairs: list[tuple[bool, bool]], row_label: str, col_label: str) -> dict:
    pp = sum(1 for a, b in pairs if a and b)
    pn = sum(1 for a, b in pairs if a and not b)
    np_ = sum(1 for a, b in pairs if (not a) and b)
    nn = sum(1 for a, b in pairs if (not a) and (not b))
    return {
        "row": row_label, "col": col_label, "n": len(pairs),
        f"{row_label}_exact_AND_{col_label}_exact": pp,
        f"{row_label}_exact_AND_{col_label}_fail": pn,
        f"{row_label}_fail_AND_{col_label}_exact": np_,
        f"{row_label}_fail_AND_{col_label}_fail": nn,
    }


def build_cross_comparison(records: list[dict], margin: float, nb_parts: dict[tuple[str, int], dict],
                           scl_index: dict | None = None) -> dict:
    """Table A (NB-SC vs binary-SC, same decoder strength) and Table B
    (NB-SCL(L=16) vs binary-SC, AND NB-SCL vs binary-CA-SCL's
    `all_applicable_msg_exact` proxy -- explicitly caveated, see
    `_scl_descriptive_summary`), for ONE margin, matched block-by-block by
    the (session, global_block_index) identity key both packets share by
    construction (this packet imports the NB packet's own
    `build_session_blocks`, so frame ranges are byte-identical; verified
    per pair below via frame_start/frame_end equality, not merely assumed).
    """
    matched = []
    mismatches = []
    missing_nb = []
    for rec in records:
        if rec.get("status") != "ok":
            continue  # error/not_started blocks are listed in block_accounting, not tabulated
        key = (rec["session"], rec["global_block_index"])
        nb = nb_parts.get(key)
        if nb is None:
            missing_nb.append(key)
            continue
        if nb["frame_start"] != rec["frame_start"] or nb["frame_end"] != rec["frame_end"]:
            mismatches.append({
                "key": key, "nb_frames": [nb["frame_start"], nb["frame_end"]],
                "binary_frames": [rec["frame_start"], rec["frame_end"]],
            })
            continue
        g = next((g for g in rec.get("grid", []) if float(g["sc_margin"]) == float(margin) and g.get("status") == "ok"), None)
        if g is None or nb["status"] != "ok":
            continue
        matched.append({
            "key": key,
            "nb_sc_exact": nb["nb_sc_exact"], "nb_scl_exact": nb["nb_scl_exact"],
            "binary_sc_exact": g["exact"],
            # Table B2 input comes from PASS 2 only; None if CA-SCL did not run/finish for this (block, margin)
            "binary_ca_scl_all_msg_exact": (
                ((scl_index or {}).get((rec["session"], int(rec["global_block_index"]), float(margin))) or {})
                .get("ca_scl_descriptive") or {}
            ).get("all_applicable_msg_exact") if (
                ((scl_index or {}).get((rec["session"], int(rec["global_block_index"]), float(margin))) or {}).get("status") == "ok"
            ) else None,
        })

    table_a_pairs = [(m["nb_sc_exact"], m["binary_sc_exact"]) for m in matched if m["nb_sc_exact"] is not None]
    table_b1_pairs = [(m["nb_scl_exact"], m["binary_sc_exact"]) for m in matched if m["nb_scl_exact"] is not None]
    table_b2_pairs = [
        (m["nb_scl_exact"], m["binary_ca_scl_all_msg_exact"]) for m in matched
        if m["nb_scl_exact"] is not None and m["binary_ca_scl_all_msg_exact"] is not None
    ]
    return {
        "sc_margin": margin,
        "n_blocks_matched": len(matched),
        "n_blocks_missing_in_nb_parts": len(missing_nb),
        "missing_nb_keys": missing_nb,
        "frame_range_mismatches": mismatches,  # must be empty; both packets derive frame ranges from the same imported function
        "table_A_nb_sc_vs_binary_sc": _contingency_2x2(table_a_pairs, "nb_sc", "binary_sc"),
        "table_B1_nb_scl_vs_binary_sc": _contingency_2x2(table_b1_pairs, "nb_scl", "binary_sc"),
        "table_B2_nb_scl_vs_binary_ca_scl_msg_proxy": _contingency_2x2(table_b2_pairs, "nb_scl", "binary_ca_scl_msg_proxy"),
        "table_B2_coverage": {
            "n_blocks_in_table_B2": len(table_b2_pairs),
            "n_blocks_matched_for_A_and_B1": len(matched),
            "note": (
                "Table B2 only counts blocks whose CA-SCL pass-2 entry finished (status ok); blocks whose "
                "CA-SCL entry was ca_scl_not_started_total_wall_budget (or otherwise missing) are excluded "
                "from B2 ONLY -- Tables A and B1 use every matched SC-ok block regardless."
            ),
        },
        "decoder_strength_parity_note": (
            "Table A is the same-strength comparison (SC vs SC). Table B1 compares NB's SCL(L=16, "
            "top_m=4, CRC-16) joint two-layer decoder against binary SC -- DIFFERENT decoder "
            "strength, descriptive only, not a fair head-to-head. Table B2's 'binary_ca_scl_msg_proxy' "
            "is `all_applicable_msg_exact` (ALL codewords' MESSAGE bits matched; the 16 CRC-slot bits "
            "per codeword are never attempted), not a true full-block exact -- descriptive reference "
            "only, per the contract's decoder-strength-parity section."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="R2 binary-Polar-baseline comparison driver (see module docstring)")
    ap.add_argument("--dry-run-one", action="store_true", help="decode exactly 1 real block, for timing only; not counted in results.json")
    ap.add_argument("--authorize", action="store_true", help="required to run against real data; refused otherwise")
    args = ap.parse_args(argv)
    t_start = _now()  # F4: total-wall clock starts here

    if not args.authorize:
        _fail(
            "refusing to run without --authorize (this is a preparation-only artifact; "
            "see STATUS.yaml / AUTHORIZATION_PROMPT.md -- PI authorization + independent "
            "Pre-EXECUTE review PASS required before this flag may be used)"
        )

    if not args.dry_run_one:
        # F3 (Pre-EXECUTE round 1): a full run refuses to start if EITHER
        # results.json exists OR ANY top-level part_*.json exists (a single
        # one is enough) -- additive-only, one-shot. dry-run's own outputs
        # live under dry_run/ and are NEVER checked/reused/read back here
        # (see _part_path/_construction_path); a fresh construction is
        # ALWAYS (re)computed below, never loaded from dry_run/ or from a
        # pre-existing top-level file.
        if RESULTS_PATH.exists():
            _fail(f"refusing to run: {RESULTS_PATH} already exists (additive-only; one-shot)")
        existing_parts = sorted(THIS_DIR.glob("part_*.json")) + sorted(THIS_DIR.glob("scl_part_*.json"))
        if existing_parts:
            _fail(
                "refusing to run: top-level part_*.json / scl_part_*.json already present "
                f"({[p.name for p in existing_parts]}) -- additive-only, one-shot. "
                "(dry_run/'s own part files, if any, do not count and are not reused.)"
            )
    else:
        DRY_RUN_DIR.mkdir(parents=True, exist_ok=True)

    nb_mod = _load_nb_packet_module()
    fns = _load_binary_baseline_functions()
    _CTX["_fns"] = fns
    mod = nb_mod._load_mod()
    chain, scl_joint_mod = nb_mod._load_scl_joint(mod)

    order = fns["polar_weight_order"](LAYER_N)[::-1]

    def prepare_session(session: str) -> dict:
        """Heavy per-session setup: reproduce session context, CAL32-only
        construction freeze, write construction_frozen_<SESSION>.json
        (dry_run/ in dry-run mode). Always recomputed, never read back."""
        ctx_nb = nb_mod._reproduce_session_context(mod, chain, scl_joint_mod, session)
        cal_ids = mod.g2_cal_ids(nb_mod.ARM)
        cal_a = ctx_nb["frames_a"][cal_ids].ravel()
        cal_b = ctx_nb["frames_b"][cal_ids].ravel()
        layer_bers = [layer_ber(cal_a, cal_b, i) for i in range(N_LAYERS)]
        t_c0 = _now()
        construction = freeze_binary_construction(
            layer_bers=layer_bers, order=order, fns=fns,
            target_f=float(ctx_nb["f_book_with_crc"]), h_total_bits=float(ctx_nb["h_total_bits"]),
            tag_bits=int(chain.tag_bits),
        )
        construction["search_wall_s"] = _now() - t_c0
        for gp in construction.get("grid_points", []):
            gp["_order"] = order
        scl_decoder = None
        try:
            scl_decoder = fns["PolarSCLDecoder"](repo_root=REPO_ROOT, force_rebuild=False)
        except Exception as exc:  # pragma: no cover - CA-SCL is descriptive-only; SC arm proceeds regardless
            print(f"[setup] {session}: CA-SCL unavailable ({exc}); secondary arm will be skipped", file=sys.stderr)
        _CTX[session] = dict(
            frames_a=ctx_nb["frames_a"], frames_b=ctx_nb["frames_b"],
            tag_bits=int(chain.tag_bits), scl_decoder=scl_decoder,
            construction=construction, h_total_bits=float(ctx_nb["h_total_bits"]),
        )
        construction_payload = {k: v for k, v in construction.items() if k != "grid_points"} | {
            "grid_points": [{k2: v2 for k2, v2 in gp.items() if k2 != "_order"} for gp in construction.get("grid_points", [])]
        }
        if args.dry_run_one:
            construction_payload["note"] = (
                "DRY-RUN TIMING PROBE ONLY. NOT counted in any results.json. A full authorized run "
                "ALWAYS recomputes construction fresh from CAL32 and writes its OWN top-level "
                "construction_frozen_<SESSION>.json -- it never reads or reuses this dry_run/ file."
            )
        with open(_construction_path(session, dry_run=args.dry_run_one), "w", encoding="utf-8") as fh:
            json.dump(
                construction_payload,
                fh, indent=2, sort_keys=True, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o),
            )
        return construction

    run = _run_sessions(
        ("G2", "G3"), lambda s: nb_mod.build_session_blocks(mod, s), prepare_session, t_start,
        dry_run=args.dry_run_one,
    )

    if args.dry_run_one:
        print("[dry-run-one] done; not aggregated into results.json", file=sys.stderr)
        return 0

    records = _load_all_part_records()
    scl_records = _load_all_scl_records()
    scl_idx = _scl_index(scl_records)
    results = aggregate_results(records, run["grid_by_session"], expected_blocks=64, scl_records=scl_records)
    results["execution_order"] = "two-pass serial (D_BIN_TWO_PASS): pass 1 = construction + SC primary arm on all blocks x grid points; pass 2 = CA-SCL secondary arm (total-wall permitting)"
    results["pass2_ca_scl"] = {
        "blocks_run": run["pass2_blocks_run"], "blocks_not_started_total_wall": run["pass2_blocks_not_started"],
        "n_scl_part_records": len(scl_records),
    }
    results["timing"] = {
        "pass1_wall_s": run["pass1_wall_s"], "pass2_wall_s": run["pass2_wall_s"],
        "construction_wall_s_by_session": run["construction_wall_s"],
        "total_wall_s": _now() - t_start,
        "budget_wall_s_total": BUDGET_WALL_S_TOTAL,
        "total_wall_exceeded": bool(_total_wall_exceeded(t_start)),
        "execution_mode": "serial single process",
    }

    nb_parts = load_nb_parts()
    cross = {}
    for margin in results["margins_present"]:
        cross[str(margin)] = build_cross_comparison(records, margin, nb_parts, scl_idx)
    results["cross_comparison_vs_nb_polar"] = cross
    results["nb_parts_loaded"] = len(nb_parts)
    results["nb_parts_source"] = str(NB_PACKET_DIR / NB_PART_GLOB)

    with open(RESULTS_PATH, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    acct = results["block_accounting"]
    print(
        f"[done] results.json written; margins={results['margins_present']} stop_undetected={results['stop_undetected']} "
        f"block_accounting_consistent={acct['consistent']} not_started={acct['n_not_started']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
